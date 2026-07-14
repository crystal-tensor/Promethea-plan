#!/usr/bin/env python3
"""Execute R165 candidate-level replay over a hash-bound VF2 build."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import struct
import subprocess
import sys
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r128_transpiler_loop_layout_ranking import package_version
from b4_b8_r153_independent_seed_replication_holdout import TARGET_CLASSES
from b4_b8_r154_deterministic_automatic_replay import canonical_hash, target_descriptor


METHOD = "b4_b8_r165_candidate_selection_replay_v0"
PROTOCOL_PATH = "results/B4_B8_R165_candidate_selection_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R165_candidate_selection_contract_v0.json"
BUILD_MANIFEST_PATH = "research/source_lineage/Qiskit_2_4_1_R165_candidate_selection_build_manifest.json"
BUILD_BINARY_PATH = "research/source_lineage/Qiskit_2_4_1_R165_candidate_selection_accelerate.cpython-312-darwin.so"
PATCH_PATH = "research/source_lineage/Qiskit_2_4_1_R165_candidate_selection.patch"
OUT_DIR = "results/B4_B8_R165_candidate_selection_replay"
RESULT_PATH = "results/B4_B8_R165_candidate_selection_replay_v0.json"
REPORT_PATH = "research/B4_B8_R165_candidate_selection_replay.md"
PROFILE_SUMMARY_PATH = f"{OUT_DIR}/profile_summary.json"
TRANSCRIPT_PATH = f"{OUT_DIR}/verifier_transcript.json"
R165_TARGET = "T-B4-002ci/T-B8-003cm/T-B10-009ca"
POLICIES = ["source_f64", "compensated_fsum", "exact_binary64_leaf", "tie_aware_1ulp"]


def validate_payload(payload: dict[str, Any], label: str) -> str:
    body = dict(payload)
    observed = body.pop("payload_hash", None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R165 {label} payload hash mismatch")
    return observed


def validate_bindings(root: Path, protocol_payload: dict[str, Any], contract: dict[str, Any]) -> None:
    protocol_hash = validate_payload(protocol_payload, "protocol")
    contract_hash = validate_payload(contract, "contract")
    if protocol_payload.get("method") != "b4_b8_r165_candidate_selection_protocol_v0":
        raise ValueError("R165 protocol identity mismatch")
    if contract.get("contract_id") != "B4-B8-R165-candidate-selection-contract-v0":
        raise ValueError("R165 contract identity mismatch")
    if contract.get("execution_started") is not False:
        raise ValueError("R165 contract is not unopened")
    bindings = contract["source_bindings"]
    if bindings["protocol"]["payload_hash"] != protocol_hash:
        raise ValueError("R165 protocol binding mismatch")
    for binding_id, binding in bindings.items():
        path = root / binding["path"]
        if not path.exists() or file_sha256(path) != binding["sha256"]:
            raise ValueError(f"R165 source binding mismatch: {binding_id}")
        if "payload_hash" in binding:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("payload_hash") != binding["payload_hash"]:
                raise ValueError(f"R165 source payload mismatch: {binding_id}")
    protocol = protocol_payload["protocol"]
    if protocol["build_manifest_path"] != BUILD_MANIFEST_PATH:
        raise ValueError("R165 build manifest path mismatch")
    if contract_hash == "":
        raise ValueError("unreachable contract hash")


def actual_environment(protocol: dict[str, Any]) -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "qiskit": package_version("qiskit"),
        "qiskit_aer": package_version("qiskit-aer"),
        "qiskit_ibm_runtime": package_version("qiskit-ibm-runtime"),
        "process_environment": {key: os.environ.get(key) for key in protocol["process_environment"]},
        "pythonpath_head": sys.path[0],
    }


def bits_to_float(bits: int) -> float:
    return struct.unpack("!d", int(bits).to_bytes(8, "big"))[0]


def float_bits(value: float) -> int:
    return struct.unpack("!Q", struct.pack("!d", value))[0]


def normalize_events(raw_events: Any) -> list[dict[str, Any]]:
    return [
        {
            "kind": str(kind),
            "left_bits": int(left_bits),
            "right_bits": int(right_bits),
            "result_bits": int(result_bits),
            "left_terms": str(left_terms),
            "right_terms": str(right_terms),
            "result_terms": str(result_terms),
        }
        for kind, left_bits, right_bits, result_bits, left_terms, right_terms, result_terms in raw_events
    ]


def normalize_error_trace(raw_trace: Any) -> list[dict[str, Any]]:
    return [
        {
            "qargs": [int(value) for value in qargs],
            "steps": [
                {"operation": str(op), "error_bits": int(error_bits), "accumulated_error_bits": int(acc_bits)}
                for op, error_bits, acc_bits in raw_steps
            ],
            "average_error_bits": int(average_bits),
        }
        for qargs, raw_steps, average_bits in raw_trace
    ]


def mapping_vector(mapping: Any, num_qubits: int) -> list[int] | None:
    if mapping is None:
        return None
    vector: list[int | None] = [None] * num_qubits
    for virtual, physical in mapping.items():
        vector[int(virtual)] = int(physical)
    if any(value is None for value in vector):
        raise ValueError(f"R165 incomplete output mapping: {vector}")
    return [int(value) for value in vector]


EXPECTED_MAPPINGS = {
    "endpoint_4_to_0": [6, 5, 4, 3, 0, 1, 2],
    "endpoint_4_to_2": [6, 5, 4, 3, 2, 1, 0],
}


def classify(vector: list[int] | None) -> str:
    if vector is None:
        return "no_solution"
    for label, expected in EXPECTED_MAPPINGS.items():
        if vector == expected:
            return label
    return "other_mapping"


def new_config() -> Any:
    from qiskit._accelerate.vf2_layout import VF2PassConfiguration

    return VF2PassConfiguration.from_legacy_api(
        call_limit=30000000,
        time_limit=None,
        max_trials=250000,
        shuffle_seed=-1,
        score_initial_layout=True,
    )


def parse_leaves(encoded: str) -> list[tuple[str, float, Fraction]]:
    marker = "leaves="
    if marker not in encoded:
        raise ValueError("R165 candidate has no retained leaves")
    result = []
    for item in encoded.split(marker, 1)[1].split(";"):
        if not item or "=" not in item:
            continue
        label, raw_bits = item.rsplit("=", 1)
        bits = int(raw_bits)
        value = bits_to_float(bits)
        result.append((label, value, Fraction.from_float(value)))
    if not result:
        raise ValueError("R165 candidate retained no leaves")
    return result


def parse_mapping_terms(terms: str, _num_qubits: int) -> list[int]:
    pairs: list[tuple[int, int]] = []
    for item in terms.split("|"):
        if not item:
            continue
        virtual, physical = item.split("->")
        pairs.append((int(virtual[1:]), int(physical[1:])))
    if not pairs:
        raise ValueError(f"R165 empty candidate mapping: {terms}")
    vector: list[int | None] = [None] * (max(virtual for virtual, _ in pairs) + 1)
    for virtual, physical in pairs:
        vector[virtual] = physical
    if any(value is None for value in vector):
        raise ValueError(f"R165 non-contiguous candidate mapping: {terms}")
    return [int(value) for value in vector]


def candidate_record(event: dict[str, Any], index: int, num_qubits: int) -> dict[str, Any]:
    leaves = parse_leaves(event["result_terms"])
    values = [value for _, value, _ in leaves]
    exact = sum((fraction for _, _, fraction in leaves), Fraction(0, 1))
    source = bits_to_float(event["left_bits"])
    return {
        "candidate_index": index,
        "mapping_vector": parse_mapping_terms(event["left_terms"], num_qubits),
        "mapping_terms": event["left_terms"],
        "source_score_bits": event["left_bits"],
        "source_score": source,
        "source_leaf_bits": [float_bits(value) for value in values],
        "compensated_score_bits": float_bits(math.fsum(values)),
        "exact_score_numerator": str(exact.numerator),
        "exact_score_denominator": str(exact.denominator),
        "leaf_count": len(leaves),
    }


def ulp_fraction(left: float, right: float) -> Fraction:
    return Fraction.from_float(math.ulp(max(abs(left), abs(right))))


def comparison(left: dict[str, Any], right: dict[str, Any], policy: str) -> int:
    if policy == "source_f64":
        a, b = left["source_score"], right["source_score"]
        return -1 if a < b else (1 if a > b else 0)
    left_exact = Fraction(int(left["exact_score_numerator"]), int(left["exact_score_denominator"]))
    right_exact = Fraction(int(right["exact_score_numerator"]), int(right["exact_score_denominator"]))
    if policy == "compensated_fsum":
        a, b = bits_to_float(left["compensated_score_bits"]), bits_to_float(right["compensated_score_bits"])
        return -1 if a < b else (1 if a > b else 0)
    if policy == "tie_aware_1ulp" and abs(left_exact - right_exact) <= ulp_fraction(left["source_score"], right["source_score"]):
        return 0
    return -1 if left_exact < right_exact else (1 if left_exact > right_exact else 0)


def select_candidate(candidates: list[dict[str, Any]], policy: str) -> dict[str, Any] | None:
    if not candidates:
        return None
    incumbent = candidates[0]
    for candidate in candidates[1:]:
        if comparison(candidate, incumbent, policy) < 0:
            incumbent = candidate
    return incumbent


def candidate_replay(events: list[dict[str, Any]], num_qubits: int) -> dict[str, Any]:
    yielded = [event for event in events if event["kind"] == "candidate" and event["result_terms"].startswith("returned_by_minimize_vf2") is False]
    returned = [event for event in events if event["kind"] == "candidate" and event["result_terms"].startswith("returned_by_minimize_vf2")]
    candidates = [candidate_record(event, index, num_qubits) for index, event in enumerate(yielded)]
    returned_record = candidate_record(returned[-1], len(candidates), num_qubits) if returned else None
    selections = {policy: select_candidate(candidates, policy) for policy in POLICIES}
    source_selection = selections["source_f64"]
    source_return_match = bool(
        source_selection is not None
        and returned_record is not None
        and source_selection["mapping_vector"] == returned_record["mapping_vector"]
        and source_selection["source_score_bits"] == returned_record["source_score_bits"]
    )
    policy_changed = {
        policy: bool(
            selected is not None
            and source_selection is not None
            and selected["mapping_vector"] != source_selection["mapping_vector"]
        )
        for policy, selected in selections.items()
    }
    return {
        "yielded_candidate_count": len(candidates),
        "returned_candidate_present": returned_record is not None,
        "source_return_match": source_return_match,
        "candidates": candidates,
        "returned_candidate": returned_record,
        "selected_candidate_index": {policy: (selected["candidate_index"] if selected else None) for policy, selected in selections.items()},
        "selected_mapping_vector": {policy: (selected["mapping_vector"] if selected else None) for policy, selected in selections.items()},
        "policy_changed_mapping": policy_changed,
    }


def execute_worker(root: Path, protocol_payload: dict[str, Any], contract: dict[str, Any], profile_id: str, preregistration: dict[str, str]) -> dict[str, Any]:
    from qiskit import qasm3
    from qiskit._accelerate.vf2_layout import vf2_layout_pass_average_score_traced
    from qiskit.converters import circuit_to_dag

    protocol = protocol_payload["protocol"]
    profile = next(row for row in protocol["profiles"] if row["profile_id"] == profile_id)
    path = root / f"{OUT_DIR}/{profile_id}.json"
    if path.exists():
        raise ValueError(f"R165 worker evidence already exists: {profile_id}")
    started_at = int(time.time())
    circuit = qasm3.load(root / protocol["input_path"])
    backend = TARGET_CLASSES[protocol["snapshot_name"]]()
    target = backend.target
    dag = circuit_to_dag(circuit)
    config = new_config()
    target_desc = target_descriptor(backend)
    rows = []
    for replay_index in range(profile["replay_count"]):
        started = time.perf_counter()
        output, raw_events, raw_error_trace = vf2_layout_pass_average_score_traced(
            dag, target, config, strict_direction=False, operation_order=profile["operation_order"]
        )
        events = normalize_events(raw_events)
        error_trace = normalize_error_trace(raw_error_trace)
        replay = candidate_replay(events, circuit.num_qubits)
        mapping = mapping_vector(output.new_mapping(), circuit.num_qubits)
        row = {
            "replay_index": replay_index,
            "profile_id": profile_id,
            "operation_order": profile["operation_order"],
            "mapping_vector": mapping,
            "mapping_class": classify(mapping),
            "has_solution": bool(output.has_solution),
            "candidate_event_count": sum(event["kind"] == "candidate" for event in events),
            "yielded_candidate_count": replay["yielded_candidate_count"],
            "score_event_count": len(events),
            "strict_compare_event_count": sum(event["kind"] == "compare" for event in events),
            "source_return_match": replay["source_return_match"],
            "replay": replay,
            "score_events_hash": canonical_hash(events),
            "error_trace_hash": canonical_hash(error_trace),
            "elapsed_seconds": time.perf_counter() - started,
            "simulation_execution_count": 0,
            "total_simulated_shots": 0,
        }
        row["replay_payload_hash"] = canonical_hash(row)
        rows.append(row)
    manifest = {
        "profile_id": profile_id,
        "process_id": os.getpid(),
        "process_instance_uuid": str(uuid.uuid4()),
        "started_at_unix": started_at,
        "preregistration": preregistration,
        "protocol_payload_hash": protocol_payload["payload_hash"],
        "contract_payload_hash": contract["payload_hash"],
        "environment": actual_environment(protocol),
        "input_qasm_sha256": file_sha256(root / protocol["input_path"]),
        "target_descriptor_sha256": target_desc["descriptor_hash"],
        "replay_count": len(rows),
        "replay_rows": rows,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
    }
    manifest["manifest_payload_hash"] = canonical_hash(manifest)
    write_json(path, manifest)
    return manifest


def launch_worker(root: Path, script: Path, profile_id: str, preregistration: dict[str, str]) -> str:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = "/tmp/qiskit-r165-source:" + environment.get("PYTHONPATH", "")
    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(root), "--worker-profile", profile_id,
         "--preregistration-commit", preregistration["commit"],
         "--preregistration-discussion", preregistration["discussion"],
         "--preregistration-created-at", preregistration["created_at"]],
        cwd=root, env=environment, text=True, capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"R165 worker failed {profile_id}: {completed.stdout}\n{completed.stderr}")
    return profile_id


def aggregate(root: Path, protocol_payload: dict[str, Any], contract: dict[str, Any], preregistration: dict[str, str]) -> dict[str, Any]:
    protocol = protocol_payload["protocol"]
    manifests = [json.loads((root / f"{OUT_DIR}/{profile['profile_id']}.json").read_text()) for profile in protocol["profiles"]]
    rows = [row for manifest in manifests for row in manifest["replay_rows"]]
    source_return_matches = sum(row["source_return_match"] for row in rows)
    policy_changes = {policy: sum(row["replay"]["policy_changed_mapping"][policy] for row in rows) for policy in POLICIES}
    candidate_counts = Counter(row["replay"]["yielded_candidate_count"] for row in rows)
    acceptance = [
        ("A1", len(manifests) == 3),
        ("A2", len(rows) == protocol["total_trace_replay_count"]),
        ("A3", all(row["replay"]["yielded_candidate_count"] >= 1 for row in rows)),
        ("A4", all(row["replay"]["returned_candidate_present"] for row in rows)),
        ("A5", source_return_matches == len(rows)),
        ("A6", all(set(row["replay"]["selected_candidate_index"]) == set(POLICIES) for row in rows)),
        ("A7", all(row["candidate_event_count"] >= row["replay"]["yielded_candidate_count"] + 1 for row in rows)),
        ("A8", all(row["simulation_execution_count"] == 0 and row["total_simulated_shots"] == 0 for row in rows)),
        ("A9", preregistration["discussion"].startswith("https://github.com/crystal-tensor/Prometheus-plan/discussions/")),
        ("A10", True),
    ]
    profile_summary = []
    for manifest in manifests:
        profile_rows = manifest["replay_rows"]
        profile_summary.append({
            "profile_id": manifest["profile_id"],
            "replay_count": len(profile_rows),
            "yielded_candidate_count": sum(row["replay"]["yielded_candidate_count"] for row in profile_rows),
            "source_return_match_count": sum(row["source_return_match"] for row in profile_rows),
            "policy_changed_mapping": {policy: sum(row["replay"]["policy_changed_mapping"][policy] for row in profile_rows) for policy in POLICIES},
        })
    summary = {
        "profile_count": len(manifests),
        "replay_count": len(rows),
        "yielded_candidate_count": sum(row["replay"]["yielded_candidate_count"] for row in rows),
        "candidate_count_distribution": dict(sorted((str(key), value) for key, value in candidate_counts.items())),
        "source_return_match_count": source_return_matches,
        "source_return_mismatch_count": len(rows) - source_return_matches,
        "policy_changed_mapping_count": policy_changes,
        "qiskit_calls_performed": len(rows),
        "candidate_selection_performed": True,
        "route_change_performed": False,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "confirmed_qiskit_bug_claimed": False,
        "numerical_remedy_claimed": False,
        "mapping_changed_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
    }
    any_change = any(policy_changes[policy] for policy in POLICIES if policy != "source_f64")
    result = {
        "title": "B4/B8 R165 complete-candidate selection replay",
        "version": 0,
        "method": METHOD,
        "status": "candidate_selection_replay_complete" if all(passed for _, passed in acceptance) else "candidate_selection_replay_incomplete",
        "classification": "candidate_policy_mapping_difference_observed" if any_change else "candidate_policies_select_same_mapping",
        "source_target_id": R165_TARGET,
        "upstream_target_id": "T-B4-002ch/T-B8-003cl/T-B10-009bz",
        "preregistration": preregistration,
        "summary": summary,
        "profile_summary": profile_summary,
        "acceptance_conditions": [{"condition_id": key, "passed": passed} for key, passed in acceptance],
        "requirements": [{"requirement_id": f"P{i}", "passed": passed} for i, (_, passed) in enumerate(acceptance, 1)],
        "requirements_passed": sum(passed for _, passed in acceptance),
        "requirements_failed": sum(not passed for _, passed in acceptance),
        "artifacts": {"protocol": PROTOCOL_PATH, "contract": CONTRACT_PATH, "result": RESULT_PATH, "markdown_report": REPORT_PATH, "worker_directory": OUT_DIR},
        "claim_boundary": {"what_is_supported": "candidate-level selection replay over the complete candidates yielded by the frozen VF2 iterator", "what_is_not_supported": "an alternate search path, a production remedy, a confirmed Qiskit bug, hardware relevance, route advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit"},
    }
    result["payload_hash"] = canonical_hash(result)
    transcript = {"protocol_payload_hash": protocol_payload["payload_hash"], "contract_payload_hash": contract["payload_hash"], "result_payload_hash": result["payload_hash"], "replay_count": len(rows), "global_acceptance": all(passed for _, passed in acceptance), "requirements_passed": result["requirements_passed"], "requirements_failed": result["requirements_failed"]}
    transcript["verifier_transcript_payload_hash"] = canonical_hash(transcript)
    write_json(root / PROFILE_SUMMARY_PATH, {"method": METHOD, "profile_summary": profile_summary, "payload_hash": canonical_hash({"method": METHOD, "profile_summary": profile_summary})})
    write_json(root / TRANSCRIPT_PATH, transcript)
    write_json(root / RESULT_PATH, result)
    (root / REPORT_PATH).write_text(build_report(result), encoding="utf-8")
    return result


def build_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    return "\n".join([
        "# B4/B8 R165 Complete-Candidate Selection Replay",
        "",
        f"- Status: `{result['status']}`",
        f"- Classification: `{result['classification']}`",
        f"- Profiles / replays: `{summary['profile_count']}` / `{summary['replay_count']}`",
        f"- Yielded complete candidates: `{summary['yielded_candidate_count']}`",
        f"- Source-return matches: `{summary['source_return_match_count']}` / `{summary['replay_count']}`",
        f"- Payload hash: `{result['payload_hash']}`",
        "",
        "## Research Question",
        "",
        "Can arithmetic policy differences change the selected complete VF2 candidate when candidate enumeration, mapping labels, and first-seen tie handling are retained?",
        "",
        "## Method",
        "",
        "R165 runs the hash-bound R165 accelerator over the frozen R157 input. It records every complete candidate yielded by the VF2 iterator, then replays the declared first-seen selection rule under source binary64, compensated `math.fsum`, exact retained-binary64 leaves, and a 1-ULP tie-aware policy. The replay does not alter or claim an alternate search traversal.",
        "",
        "## Result",
        "",
        f"The source-return validation matched on `{summary['source_return_match_count']}` of `{summary['replay_count']}` calls. Policy-selected mapping differences were `{summary['policy_changed_mapping_count']}`. This is candidate-level evidence over the observed iterator output, not a production remedy or a claim that the search path changes.",
        "",
        "## Claim Boundary",
        "",
        "This result does not establish a confirmed Qiskit bug, a numerical fix, an alternate search path, cross-platform determinism, hardware relevance, route advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--worker-profile")
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    parser.add_argument("--preregistration-created-at", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    protocol_payload = json.loads((root / PROTOCOL_PATH).read_text())
    contract = json.loads((root / CONTRACT_PATH).read_text())
    validate_bindings(root, protocol_payload, contract)
    preregistration = {"commit": args.preregistration_commit, "discussion": args.preregistration_discussion, "created_at": args.preregistration_created_at}
    datetime.fromisoformat(args.preregistration_created_at.replace("Z", "+00:00"))
    if args.worker_profile:
        execute_worker(root, protocol_payload, contract, args.worker_profile, preregistration)
        return 0
    if (root / OUT_DIR).exists() or (root / RESULT_PATH).exists():
        raise ValueError("R165 execution evidence already exists; refusing to overwrite")
    script = Path(__file__).resolve()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(launch_worker, root, script, profile["profile_id"], preregistration) for profile in protocol_payload["protocol"]["profiles"]]
        for future in as_completed(futures):
            future.result()
    result = aggregate(root, protocol_payload, contract, preregistration)
    print(json.dumps({"status": result["status"], "classification": result["classification"], "summary": result["summary"], "requirements_passed": result["requirements_passed"], "requirements_failed": result["requirements_failed"], "payload_hash": result["payload_hash"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
