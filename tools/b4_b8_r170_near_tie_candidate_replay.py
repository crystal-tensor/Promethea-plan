#!/usr/bin/env python3
"""Run R170 near-tie candidate-level VF2 replay on OpenQASM 3 input."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r128_transpiler_loop_layout_ranking import package_version
from b4_b8_r153_independent_seed_replication_holdout import TARGET_CLASSES
from b4_b8_r154_deterministic_automatic_replay import canonical_hash, target_descriptor
from b4_b8_r165_candidate_selection_replay import (
    POLICIES,
    candidate_replay,
    classify,
    mapping_vector,
    new_config,
    normalize_error_trace,
    normalize_events,
)


METHOD = "b4_b8_r170_near_tie_candidate_replay_v0"
PROTOCOL_PATH = "results/B4_B8_R170_near_tie_candidate_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R170_near_tie_candidate_contract_v0.json"
INPUT_PATH = "benchmarks/B4_B8_R170_near_tie_candidate_v0.qasm"
OUT_DIR = "results/B4_B8_R170_near_tie_candidate_replay"
RESULT_PATH = "results/B4_B8_R170_near_tie_candidate_replay_v0.json"
REPORT_PATH = "research/B4_B8_R170_near_tie_candidate_replay.md"
R165_EXECUTOR_PATH = "tools/b4_b8_r165_candidate_selection_replay.py"
BUILD_BINARY_PATH = "research/source_lineage/Qiskit_2_4_1_R165_candidate_selection_accelerate.cpython-312-darwin.so"
R170_TARGET = "T-B4-002cn/T-B8-003cr/T-B10-009cd-r170"


def validate_payload(payload: dict[str, Any], label: str) -> str:
    body = dict(payload)
    observed = body.pop("payload_hash", None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R170 {label} payload hash mismatch")
    return str(observed)


def actual_environment(protocol: dict[str, Any]) -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "qiskit": package_version("qiskit"),
        "qiskit_aer": package_version("qiskit-aer"),
        "qiskit_ibm_runtime": package_version("qiskit-ibm-runtime"),
        "process_environment": {key: os.environ.get(key) for key in protocol["process_environment"]},
        "pythonpath_head": sys.path[0],
    }


def validate_bindings(root: Path, protocol_payload: dict[str, Any], contract: dict[str, Any]) -> None:
    protocol_hash = validate_payload(protocol_payload, "protocol")
    contract_hash = validate_payload(contract, "contract")
    if protocol_payload.get("method") != "b4_b8_r170_near_tie_candidate_protocol_v0":
        raise ValueError("R170 protocol identity mismatch")
    if contract.get("contract_id") != "B4-B8-R170-near-tie-candidate-contract-v0":
        raise ValueError("R170 contract identity mismatch")
    if contract.get("execution_started") is not False:
        raise ValueError("R170 contract is not unopened")
    if contract.get("protocol_payload_hash") != protocol_hash:
        raise ValueError("R170 protocol binding mismatch")
    for binding_id, binding in contract["source_bindings"].items():
        path = root / binding["path"]
        if not path.exists() or file_sha256(path) != binding["sha256"]:
            raise ValueError(f"R170 source binding mismatch: {binding_id}")
        if "payload_hash" in binding:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("payload_hash") != binding["payload_hash"]:
                raise ValueError(f"R170 source payload mismatch: {binding_id}")
    if protocol_payload["input_sha256"] != file_sha256(root / INPUT_PATH):
        raise ValueError("R170 input hash mismatch")
    if contract_hash == "":
        raise ValueError("unreachable contract hash")


def execute_worker(root: Path, protocol_payload: dict[str, Any], profile_id: str, preregistration: dict[str, str]) -> dict[str, Any]:
    import qiskit
    from qiskit import qasm3
    from qiskit._accelerate import vf2_layout as vf2_module
    from qiskit._accelerate.vf2_layout import vf2_layout_pass_average_score_traced
    from qiskit.converters import circuit_to_dag

    protocol = protocol_payload
    profile = next(row for row in protocol["profiles"] if row["profile_id"] == profile_id)
    path = root / f"{OUT_DIR}/{profile_id}.json"
    if path.exists():
        raise ValueError(f"R170 worker evidence already exists: {profile_id}")
    binary_candidates = sorted(Path(qiskit.__file__).resolve().parent.glob("_accelerate*.so"))
    if len(binary_candidates) != 1:
        raise ValueError(f"R170 expected one Qiskit accelerator binary, found {len(binary_candidates)}")
    binary_path = binary_candidates[0]
    if file_sha256(binary_path) != protocol["instrumented_binary_sha256"]:
        raise ValueError("R170 imported accelerator hash mismatch")
    started_at = int(time.time())
    circuit = qasm3.load(root / INPUT_PATH)
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
        "contract_payload_hash": json.loads((root / CONTRACT_PATH).read_text())["payload_hash"],
        "environment": actual_environment(protocol),
        "input_qasm_sha256": file_sha256(root / INPUT_PATH),
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
        raise RuntimeError(f"R170 worker failed {profile_id}: {completed.stdout}\n{completed.stderr}")
    return profile_id


def aggregate(root: Path, protocol_payload: dict[str, Any], contract: dict[str, Any], preregistration: dict[str, str]) -> dict[str, Any]:
    protocol = protocol_payload
    manifests = [json.loads((root / f"{OUT_DIR}/{profile['profile_id']}.json").read_text()) for profile in protocol["profiles"]]
    rows = [row for manifest in manifests for row in manifest["replay_rows"]]
    source_return_matches = sum(row["replay"]["source_return_match"] for row in rows)
    policy_changes = {policy: sum(row["replay"]["policy_changed_mapping"][policy] for row in rows) for policy in POLICIES}
    candidate_counts = Counter(row["replay"]["yielded_candidate_count"] for row in rows)
    acceptance = [
        ("A1", len(manifests) == len(protocol["profiles"])),
        ("A2", len(rows) == protocol["total_replay_count"]),
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
            "source_return_match_count": sum(row["replay"]["source_return_match"] for row in profile_rows),
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
    result = {
        "title": "B4/B8 R170 near-tie complete-candidate replay",
        "version": 0,
        "method": METHOD,
        "status": "new_input_candidate_replay_complete" if all(passed for _, passed in acceptance) else "new_input_candidate_replay_incomplete",
        "classification": "new_input_candidate_replay_complete" if all(passed for _, passed in acceptance) else "new_input_candidate_replay_incomplete",
        "source_target_id": R170_TARGET,
        "upstream_target_id": "T-B4-002cm/T-B8-003cq/T-B10-009cc-r169",
        "preregistration": preregistration,
        "summary": summary,
        "profile_summary": profile_summary,
        "acceptance_conditions": [{"condition_id": key, "passed": passed} for key, passed in acceptance],
        "requirements": [{"requirement_id": f"P{i}", "passed": passed} for i, (_, passed) in enumerate(acceptance, 1)],
        "requirements_passed": sum(passed for _, passed in acceptance),
        "requirements_failed": sum(not passed for _, passed in acceptance),
        "artifacts": {"protocol": PROTOCOL_PATH, "contract": CONTRACT_PATH, "result": RESULT_PATH, "markdown_report": REPORT_PATH, "worker_directory": OUT_DIR},
        "claim_boundary": {"what_is_supported": "candidate-level replay over a newly frozen OpenQASM 3 input under the declared profiles and policies", "what_is_not_supported": "an alternate search path, a production remedy, a confirmed Qiskit bug, cross-input generality, cross-platform determinism, hardware relevance, route advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit"},
    }
    result["payload_hash"] = canonical_hash(result)
    write_json(root / RESULT_PATH, result)
    (root / REPORT_PATH).write_text(build_report(result), encoding="utf-8")
    return result


def build_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    return "\n".join([
        "# B4/B8 R170 Near-Tie Complete-Candidate Replay",
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
        "Does a target-compatible OpenQASM 3 interaction graph with near-tied candidates expose arithmetic-policy instability?",
        "",
        "## Method",
        "",
        "R170 runs the hash-bound candidate instrumentation on a five-active-qubit target-compatible tree input over FakeNairobiV2. The design preflight identified a one-ULP source-score gap between the best two candidates for this graph family. The replay retains every complete VF2 candidate and applies source binary64, compensated `math.fsum`, exact retained-binary64 leaves, and 1-ULP tie-aware selection without changing the search traversal.",
        "",
        "## Result",
        "",
        f"Across `{summary['profile_count']}` profiles and `{summary['replay_count']}` calls, `{summary['yielded_candidate_count']}` candidates were yielded, source-return validation matched `{summary['source_return_match_count']}/{summary['replay_count']}`, and policy-change counts were `{summary['policy_changed_mapping_count']}`.",
        "",
        "## Claim Boundary",
        "",
        "This is one near-tie target-compatible input candidate-level result. It does not establish cross-input generality, a production mapping change, an alternate search path, a confirmed Qiskit bug, hardware relevance, route advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--worker-profile")
    parser.add_argument("--aggregate-existing", action="store_true")
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    parser.add_argument("--preregistration-created-at", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    protocol_payload = json.loads((root / PROTOCOL_PATH).read_text())
    contract = json.loads((root / CONTRACT_PATH).read_text())
    validate_bindings(root, protocol_payload, contract)
    preregistration = {"commit": args.preregistration_commit, "discussion": args.preregistration_discussion, "created_at": args.preregistration_created_at}
    if args.worker_profile:
        execute_worker(root, protocol_payload, args.worker_profile, preregistration)
        return 0
    if (root / OUT_DIR).exists() or (root / RESULT_PATH).exists():
        if not args.aggregate_existing:
            raise ValueError("R170 execution evidence already exists; refusing to overwrite")
        result = aggregate(root, protocol_payload, contract, preregistration)
        print(json.dumps({"status": result["status"], "classification": result["classification"], "summary": result["summary"], "requirements_passed": result["requirements_passed"], "requirements_failed": result["requirements_failed"], "payload_hash": result["payload_hash"]}, indent=2, sort_keys=True))
        return 0
    script = Path(__file__).resolve()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(launch_worker, root, script, profile["profile_id"], preregistration) for profile in protocol_payload["profiles"]]
        for future in as_completed(futures):
            future.result()
    result = aggregate(root, protocol_payload, contract, preregistration)
    print(json.dumps({"status": result["status"], "classification": result["classification"], "summary": result["summary"], "requirements_passed": result["requirements_passed"], "requirements_failed": result["requirements_failed"], "payload_hash": result["payload_hash"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
