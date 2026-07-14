#!/usr/bin/env python3
"""Execute the preregistered R162 source score-combination trace matrix."""

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


METHOD = "b4_b8_r162_score_trace_v0"
PROTOCOL_PATH = "results/B4_B8_R162_score_trace_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R162_score_trace_contract_v0.json"
BUILD_MANIFEST_PATH = "research/source_lineage/Qiskit_2_4_1_R162_score_trace_build_manifest.json"
OUT_DIR = "results/B4_B8_R162_score_trace"
RESULT_PATH = "results/B4_B8_R162_score_trace_v0.json"
REPORT_PATH = "research/B4_B8_R162_score_trace.md"
PROFILE_SUMMARY_PATH = f"{OUT_DIR}/profile_summary.json"
TRANSCRIPT_PATH = f"{OUT_DIR}/verifier_transcript.json"
EXPECTED_MAPPINGS = {
    "endpoint_4_to_0": [6, 5, 4, 3, 0, 1, 2],
    "endpoint_4_to_2": [6, 5, 4, 3, 2, 1, 0],
}
MAPPING_CLASSES = ["endpoint_4_to_0", "endpoint_4_to_2", "other_mapping", "no_solution"]
SHADOW_CLASSES = [
    "no_candidate",
    "source_equals_fsum_equals_exact_binary64",
    "source_equals_fsum_but_exact_binary64_differs",
    "source_differs_from_fsum",
]


def ensure_environment(protocol: dict[str, Any]) -> None:
    expected = protocol["process_environment"]
    actual = {key: os.environ.get(key) for key in expected}
    if actual == expected:
        return
    environment = dict(os.environ)
    environment.update(expected)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def utc_timestamp(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def validate_payload(payload: dict[str, Any], label: str) -> str:
    body = dict(payload)
    payload_hash = body.pop("payload_hash", None)
    if not payload_hash or payload_hash != canonical_hash(body):
        raise ValueError(f"R162 {label} payload hash mismatch")
    return payload_hash


def validate_bindings(root: Path, protocol_payload: dict[str, Any], contract: dict[str, Any]) -> None:
    protocol_hash = validate_payload(protocol_payload, "protocol")
    contract_hash = validate_payload(contract, "contract")
    if protocol_payload.get("method") != "b4_b8_r162_score_trace_protocol_v0":
        raise ValueError("R162 protocol identity mismatch")
    if contract.get("contract_id") != "B4-B8-R162-score-trace-contract-v0":
        raise ValueError("R162 contract identity mismatch")
    if contract.get("execution_started") is not False:
        raise ValueError("R162 contract is not unopened")
    bindings = contract["source_bindings"]
    if bindings["protocol"]["payload_hash"] != protocol_hash:
        raise ValueError("R162 protocol binding mismatch")
    for binding_id, binding in bindings.items():
        path = root / binding["path"]
        if not path.exists() or file_sha256(path) != binding["sha256"]:
            raise ValueError(f"R162 source binding mismatch: {binding_id}")
        if "payload_hash" in binding:
            payload = json.loads(path.read_text())
            if payload.get("payload_hash") != binding["payload_hash"]:
                raise ValueError(f"R162 source payload mismatch: {binding_id}")
    protocol = protocol_payload["protocol"]
    if protocol["build_manifest_payload_hash"] != bindings["build_manifest"]["payload_hash"]:
        raise ValueError("R162 build manifest payload binding mismatch")
    manifest = json.loads((root / BUILD_MANIFEST_PATH).read_text())
    validate_payload(manifest, "build manifest")
    import qiskit._accelerate as accelerate
    from qiskit._accelerate import vf2_layout

    binary_path = Path(accelerate.__file__).resolve()
    if file_sha256(binary_path) != protocol["instrumented_binary_sha256"]:
        raise ValueError("R162 imported accelerator binary hash mismatch")
    if binary_path.stat().st_size != protocol["instrumented_binary_size_bytes"]:
        raise ValueError("R162 imported accelerator binary size mismatch")
    if not hasattr(vf2_layout, "vf2_layout_pass_average_score_traced"):
        raise ValueError("R162 score-trace entry point missing")
    if not hasattr(vf2_layout, "vf2_layout_pass_average_traced"):
        raise ValueError("R162 ErrorMap-trace entry point missing")
    _ = contract_hash


def actual_environment(protocol: dict[str, Any]) -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "qiskit": package_version("qiskit"),
        "qiskit_aer": package_version("qiskit-aer"),
        "qiskit_ibm_runtime": package_version("qiskit-ibm-runtime"),
        "process_environment": {
            key: os.environ.get(key) for key in protocol["process_environment"]
        },
    }


def new_config() -> Any:
    from qiskit._accelerate.vf2_layout import VF2PassConfiguration

    return VF2PassConfiguration.from_legacy_api(
        call_limit=30000000,
        time_limit=None,
        max_trials=250000,
        shuffle_seed=-1,
        score_initial_layout=True,
    )


def mapping_vector(mapping: Any, num_qubits: int) -> list[int] | None:
    if mapping is None:
        return None
    vector: list[int | None] = [None] * num_qubits
    for virtual, physical in mapping.items():
        vector[int(virtual)] = int(physical)
    if any(value is None for value in vector):
        raise ValueError(f"R162 incomplete mapping: {vector}")
    return [int(value) for value in vector]


def classify(vector: list[int] | None) -> str:
    if vector is None:
        return "no_solution"
    for class_id, expected in EXPECTED_MAPPINGS.items():
        if vector == expected:
            return class_id
    return "other_mapping"


def bits_to_float(bits: int) -> float:
    return struct.unpack("!d", int(bits).to_bytes(8, "big"))[0]


def normalize_events(raw_events: Any) -> list[dict[str, Any]]:
    rows = []
    for kind, left_bits, right_bits, result_bits, left_terms, right_terms, result_terms in raw_events:
        rows.append({
            "kind": str(kind),
            "left_bits": int(left_bits),
            "right_bits": int(right_bits),
            "result_bits": int(result_bits),
            "left_terms": str(left_terms),
            "right_terms": str(right_terms),
            "result_terms": str(result_terms),
        })
    return rows


def normalize_error_trace(raw_trace: Any) -> list[dict[str, Any]]:
    rows = []
    for qargs, raw_steps, average_error_bits in raw_trace:
        rows.append({
            "qargs": [int(value) for value in qargs],
            "steps": [
                {
                    "operation": str(operation),
                    "error_bits": int(error_bits),
                    "accumulated_error_bits": int(accumulated_error_bits),
                }
                for operation, error_bits, accumulated_error_bits in raw_steps
            ],
            "average_error_bits": int(average_error_bits),
        })
    return rows


def candidate_shadow(events: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [row for row in events if row["kind"] == "candidate"]
    if not candidates:
        return {
            "candidate_count": 0,
            "shadow_class": "no_candidate",
            "source_score_bits": None,
            "compensated_score_bits": None,
            "exact_binary64_leaf_sum_numerator": None,
            "exact_binary64_leaf_sum_denominator": None,
            "first_divergence": "no_candidate",
            "candidate_mapping_terms": None,
        }
    candidate = candidates[-1]
    marker = "leaves="
    encoded = candidate["result_terms"].split(marker, 1)[1] if marker in candidate["result_terms"] else ""
    leaves: list[tuple[str, float, Fraction]] = []
    for item in encoded.split(";"):
        if not item or "=" not in item:
            continue
        label, bits = item.rsplit("=", 1)
        raw_bits = int(bits)
        value = bits_to_float(raw_bits)
        leaves.append((label, value, Fraction.from_float(value)))
    values = [value for _, value, _ in leaves]
    source_score = bits_to_float(candidate["left_bits"])
    compensated = math.fsum(values)
    exact = sum((fraction for _, _, fraction in leaves), Fraction(0, 1))
    source_bits = candidate["left_bits"]
    compensated_bits = struct.unpack("!Q", struct.pack("!d", compensated))[0]
    exact_float = float(exact)
    exact_float_bits = struct.unpack("!Q", struct.pack("!d", exact_float))[0]
    source_vs_fsum = source_bits != compensated_bits
    exact_differs = Fraction.from_float(source_score) != exact
    if source_vs_fsum:
        shadow_class = "source_differs_from_fsum"
        first_divergence = "candidate_total_vs_compensated_fsum"
    elif exact_differs:
        shadow_class = "source_equals_fsum_but_exact_binary64_differs"
        first_divergence = "candidate_total_vs_exact_binary64_leaf_sum"
    else:
        shadow_class = "source_equals_fsum_equals_exact_binary64"
        first_divergence = "none"
    return {
        "candidate_count": len(candidates),
        "shadow_class": shadow_class,
        "source_score_bits": source_bits,
        "compensated_score_bits": compensated_bits,
        "exact_binary64_float_bits": exact_float_bits,
        "exact_binary64_leaf_sum_numerator": str(exact.numerator),
        "exact_binary64_leaf_sum_denominator": str(exact.denominator),
        "leaf_count": len(leaves),
        "first_divergence": first_divergence,
        "candidate_mapping_terms": candidate["left_terms"],
    }


def execute_worker(root: Path, protocol_payload: dict[str, Any], contract: dict[str, Any], profile_id: str, preregistration: dict[str, str]) -> dict[str, Any]:
    from qiskit import qasm3
    from qiskit._accelerate.vf2_layout import vf2_layout_pass_average_score_traced
    from qiskit.converters import circuit_to_dag

    protocol = protocol_payload["protocol"]
    profile = next(row for row in protocol["profiles"] if row["profile_id"] == profile_id)
    path = root / f"{OUT_DIR}/{profile_id}.json"
    if path.exists():
        raise ValueError(f"R162 worker evidence already exists: {profile_id}")
    started_at = int(time.time())
    circuit = qasm3.load(root / protocol["input_path"])
    backend = TARGET_CLASSES[protocol["snapshot_name"]]()
    target = backend.target
    target_desc = target_descriptor(backend)
    dag = circuit_to_dag(circuit)
    config = new_config()
    identity_guards = [circuit, backend, target, dag, config]
    rows = []
    for replay_index in range(profile["replay_count"]):
        started = time.perf_counter()
        output, raw_events, raw_error_trace = vf2_layout_pass_average_score_traced(
            dag,
            target,
            config,
            strict_direction=False,
            operation_order=profile["operation_order"],
        )
        score_events = normalize_events(raw_events)
        error_trace = normalize_error_trace(raw_error_trace)
        shadow = candidate_shadow(score_events)
        mapping = mapping_vector(output.new_mapping(), circuit.num_qubits)
        row = {
            "replay_index": replay_index,
            "profile_id": profile_id,
            "operation_order": profile["operation_order"],
            "mapping_vector": mapping,
            "mapping_class": classify(mapping),
            "has_solution": bool(output.has_solution),
            "stop_reason": "solution found" if mapping is not None else ("no improvement" if output.has_solution else "no solution"),
            "score_event_count": len(score_events),
            "score_event_kind_counts": dict(Counter(row["kind"] for row in score_events)),
            "strict_compare_event_count": sum(row["kind"] == "compare" for row in score_events),
            "candidate_event_count": sum(row["kind"] == "candidate" for row in score_events),
            "score_events": score_events,
            "score_events_hash": canonical_hash(score_events),
            "error_trace_row_count": len(error_trace),
            "error_trace_hash": canonical_hash(error_trace),
            "shadow": shadow,
            "elapsed_seconds": time.perf_counter() - started,
            "simulation_execution_count": 0,
            "total_simulated_shots": 0,
        }
        row["replay_payload_hash"] = canonical_hash(row)
        rows.append(row)
    del identity_guards
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
        "shared_object_ids": {"circuit": id(circuit), "target": id(target), "dag": id(dag), "config": id(config)},
        "replay_count": len(rows),
        "replay_rows": rows,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
    }
    manifest["manifest_payload_hash"] = canonical_hash(manifest)
    write_json(path, manifest)
    return manifest


def launch_worker(root: Path, script: Path, profile_id: str, preregistration: dict[str, str]) -> str:
    completed = subprocess.run([
        sys.executable, str(script), "--root", str(root), "--worker-profile", profile_id,
        "--preregistration-commit", preregistration["commit"],
        "--preregistration-discussion", preregistration["discussion"],
        "--preregistration-created-at", preregistration["created_at"],
    ], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"R162 worker failed {profile_id}: {completed.stdout}\n{completed.stderr}")
    return profile_id


def profile_summary(protocol: dict[str, Any], manifests: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for profile in protocol["profiles"]:
        manifest = next(row for row in manifests if row["profile_id"] == profile["profile_id"])
        replay_rows = manifest["replay_rows"]
        mapping_counts = Counter(row["mapping_class"] for row in replay_rows)
        shadow_counts = Counter(row["shadow"]["shadow_class"] for row in replay_rows)
        rows.append({
            "profile_id": profile["profile_id"],
            "operation_order": profile["operation_order"],
            "process_count": 1,
            "replay_count": len(replay_rows),
            "mapping_class_counts": {key: mapping_counts.get(key, 0) for key in MAPPING_CLASSES},
            "shadow_class_counts": {key: shadow_counts.get(key, 0) for key in SHADOW_CLASSES},
            "unique_score_event_hash_count": len({row["score_events_hash"] for row in replay_rows}),
            "unique_error_trace_hash_count": len({row["error_trace_hash"] for row in replay_rows}),
            "mean_score_event_count": sum(row["score_event_count"] for row in replay_rows) / len(replay_rows),
            "mean_strict_compare_event_count": sum(row["strict_compare_event_count"] for row in replay_rows) / len(replay_rows),
        })
    payload = {"profile_count": len(rows), "total_process_count": len(manifests), "total_trace_replay_count": sum(row["replay_count"] for row in rows), "profile_rows": rows}
    payload["profile_summary_payload_hash"] = canonical_hash(payload)
    return payload


def build_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# B4/B8 R162 VF2 Score-Combination Trace",
        "",
        f"- Status: `{result['status']}`",
        f"- Classification: `{summary['classification']}`",
        f"- Profiles / processes / replays: `{summary['profile_count']}` / `{summary['process_count']}` / `{summary['replay_count']}`",
        f"- Score events / strict comparisons / returned candidates: `{summary['score_event_count']}` / `{summary['strict_compare_event_count']}` / `{summary['candidate_event_count']}`",
        f"- Shadow classes: `{json.dumps(summary['shadow_class_counts'], sort_keys=True)}`",
        f"- Requirements passed/failed: `{result['requirements_passed']}` / `{result['requirements_failed']}`",
        f"- Payload hash: `{result['payload_hash']}`",
        "",
        "## Research Question",
        "",
        "At which retained event does the source-order binary64 score first diverge from compensated or exact-binary64-leaf arithmetic?",
        "",
        "## Result",
        "",
        summary["diagnostic_interpretation"],
        "",
        "## Profile Summary",
        "",
        "| Profile | Replays | Mapping counts | Shadow counts | Mean score events | Mean strict compares |",
        "|---|---:|---|---|---:|---:|",
    ]
    for row in result["profile_summary"]["profile_rows"]:
        lines.append(
            f"| `{row['profile_id']}` | {row['replay_count']} | `{json.dumps(row['mapping_class_counts'], sort_keys=True)}` | "
            f"`{json.dumps(row['shadow_class_counts'], sort_keys=True)}` | {row['mean_score_event_count']:.2f} | {row['mean_strict_compare_event_count']:.2f} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The trace retains source operands and labels; the compensated and exact-binary64-leaf values are arithmetic shadows over those retained leaves. They do not replace Qiskit's source score, establish a bug, or prove a remedy.",
        "",
        "## Claim Boundary",
        "",
        "This diagnostic does not establish a confirmed Qiskit bug, a numerical fix, cross-platform determinism, hardware relevance, route advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new research credit.",
        "",
    ])
    return "\n".join(lines)


def aggregate(root: Path, protocol_payload: dict[str, Any], contract: dict[str, Any], preregistration: dict[str, str]) -> dict[str, Any]:
    protocol = protocol_payload["protocol"]
    manifests = []
    for profile in protocol["profiles"]:
        path = root / f"{OUT_DIR}/{profile['profile_id']}.json"
        manifest = json.loads(path.read_text())
        body = dict(manifest)
        payload_hash = body.pop("manifest_payload_hash", None)
        if payload_hash != canonical_hash(body):
            raise ValueError(f"R162 worker payload mismatch: {profile['profile_id']}")
        manifests.append(manifest)
    replay_rows = [row for manifest in manifests for row in manifest["replay_rows"]]
    counts = Counter(row["mapping_class"] for row in replay_rows)
    shadow_counts = Counter(row["shadow"]["shadow_class"] for row in replay_rows)
    profile_payload = profile_summary(protocol, manifests)
    expected_counts = [profile["replay_count"] for profile in protocol["profiles"]]
    trace_complete = all(
        row["score_event_count"] > 0
        and row["strict_compare_event_count"] > 0
        and row["candidate_event_count"] == 1
        and row["score_events_hash"] == canonical_hash(row["score_events"])
        and row["replay_payload_hash"] == canonical_hash({key: value for key, value in row.items() if key != "replay_payload_hash"})
        for row in replay_rows
    )
    env_match = all(manifest["environment"]["process_environment"] == protocol["process_environment"] for manifest in manifests)
    source_match = all(manifest["input_qasm_sha256"] == protocol["input_qasm_sha256"] and manifest["target_descriptor_sha256"] == protocol["target_descriptor_sha256"] for manifest in manifests)
    prereg_time = utc_timestamp(preregistration["created_at"])
    after_preregistration = all(manifest["started_at_unix"] >= prereg_time for manifest in manifests)
    classification = "source_f64_equals_compensated_and_exact_binary64_shadow" if shadow_counts["source_equals_fsum_equals_exact_binary64"] == len(replay_rows) else "source_score_shadow_divergence_localized"
    if shadow_counts["source_differs_from_fsum"]:
        interpretation = f"The returned source f64 score differs from the compensated fsum shadow on {shadow_counts['source_differs_from_fsum']}/{len(replay_rows)} calls; this is the earliest retained candidate-total divergence. Exact-binary64-leaf comparisons remain arithmetic shadows, not a source fix."
    elif shadow_counts["source_equals_fsum_but_exact_binary64_differs"]:
        interpretation = f"The source f64 score agrees with math.fsum on all calls, while {shadow_counts['source_equals_fsum_but_exact_binary64_differs']}/{len(replay_rows)} returned candidates differ from the exact rational sum of their retained binary64 leaves. The first localized boundary is final binary64 accumulation."
    else:
        interpretation = "The source f64 score agrees with both arithmetic shadows on every returned candidate in this matrix; no divergence was localized by the frozen trace."
    acceptance = [
        ("A1", True),
        ("A2", len(manifests) == 3 and len(replay_rows) == 256),
        ("A3", env_match and source_match and after_preregistration),
        ("A4", expected_counts == [128, 64, 64]),
        ("A5", trace_complete),
        ("A6", sum(shadow_counts.values()) == len(replay_rows) and all(row["shadow"]["first_divergence"] for row in replay_rows)),
        ("A7", sum(counts.values()) == 256),
        ("A8", all(row["strict_compare_event_count"] > 0 for row in replay_rows)),
        ("A9", protocol["input_qasm_sha256"] == "ce216610e995b4c8b4bd9de6547ac6069961e1eb8881997aa05e0068ea16ab98"),
        ("A10", True),
    ]
    requirements = [{"requirement_id": f"P{i}", "passed": passed} for i, (_, passed) in enumerate(acceptance, 1)]
    summary = {
        "profile_count": len(manifests),
        "process_count": len(manifests),
        "replay_count": len(replay_rows),
        "score_event_count": sum(row["score_event_count"] for row in replay_rows),
        "strict_compare_event_count": sum(row["strict_compare_event_count"] for row in replay_rows),
        "candidate_event_count": sum(row["candidate_event_count"] for row in replay_rows),
        "mapping_class_counts": {key: counts.get(key, 0) for key in MAPPING_CLASSES},
        "shadow_class_counts": {key: shadow_counts.get(key, 0) for key in SHADOW_CLASSES},
        "classification": classification,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "source_patch_performed": True,
        "confirmed_qiskit_bug_claimed": False,
        "hardware_execution_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
        "diagnostic_interpretation": interpretation,
    }
    result = {
        "title": "B4/B8 R162 VF2 score-combination trace",
        "version": 0,
        "method": METHOD,
        "status": "score_trace_diagnostic_complete" if all(passed for _, passed in acceptance) else "score_trace_diagnostic_incomplete",
        "classification": classification,
        "source_target_id": "T-B4-002cf/T-B8-003cj/T-B10-009bx",
        "upstream_target_id": "T-B4-002ce/T-B8-003ci/T-B10-009bw",
        "preregistration": preregistration,
        "summary": summary,
        "profile_summary": profile_payload,
        "acceptance_conditions": [{"condition_id": key, "passed": passed} for key, passed in acceptance],
        "requirements": requirements,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "artifacts": {"protocol": PROTOCOL_PATH, "contract": CONTRACT_PATH, "build_manifest": BUILD_MANIFEST_PATH, "result": RESULT_PATH, "markdown_report": REPORT_PATH, "worker_directory": OUT_DIR},
        "claim_boundary": {"what_is_supported": "one source- and binary-bound score trace with compensated and exact-binary64-leaf arithmetic shadows", "what_is_not_supported": "a confirmed Qiskit bug, numerical remedy, cross-platform theorem, hardware performance, route advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit"},
    }
    result["payload_hash"] = canonical_hash(result)
    transcript = {"protocol_payload_hash": protocol_payload["payload_hash"], "contract_payload_hash": contract["payload_hash"], "result_payload_hash": result["payload_hash"], "replay_count": len(replay_rows), "global_acceptance": all(passed for _, passed in acceptance), "requirements_passed": result["requirements_passed"], "requirements_failed": result["requirements_failed"]}
    transcript["verifier_transcript_payload_hash"] = canonical_hash(transcript)
    write_json(root / PROFILE_SUMMARY_PATH, profile_payload)
    write_json(root / TRANSCRIPT_PATH, transcript)
    write_json(root / RESULT_PATH, result)
    (root / REPORT_PATH).write_text(build_report(result), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--worker-profile")
    parser.add_argument("--preregistration-commit")
    parser.add_argument("--preregistration-discussion")
    parser.add_argument("--preregistration-created-at")
    args = parser.parse_args()
    root = args.root.resolve()
    protocol_payload = json.loads((root / PROTOCOL_PATH).read_text())
    contract = json.loads((root / CONTRACT_PATH).read_text())
    protocol = protocol_payload["protocol"]
    ensure_environment(protocol)
    validate_bindings(root, protocol_payload, contract)
    preregistration = {"commit": args.preregistration_commit, "discussion": args.preregistration_discussion, "created_at": args.preregistration_created_at}
    if not all(preregistration.values()) or not preregistration["discussion"].startswith("https://github.com/crystal-tensor/Prometheus-plan/discussions/"):
        raise ValueError("R162 preregistration fields are required")
    utc_timestamp(preregistration["created_at"])
    if args.worker_profile:
        execute_worker(root, protocol_payload, contract, args.worker_profile, preregistration)
        return 0
    if (root / OUT_DIR).exists() or (root / RESULT_PATH).exists():
        raise ValueError("R162 execution evidence already exists; refusing to overwrite")
    script = Path(__file__).resolve()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(launch_worker, root, script, profile["profile_id"], preregistration): profile["profile_id"] for profile in protocol["profiles"]}
        for future in as_completed(futures):
            print(f"R162 worker complete: {future.result()}")
    result = aggregate(root, protocol_payload, contract, preregistration)
    print(json.dumps({"status": result["status"], "classification": result["classification"], "summary": result["summary"], "requirements_passed": result["requirements_passed"], "requirements_failed": result["requirements_failed"], "payload_hash": result["payload_hash"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
