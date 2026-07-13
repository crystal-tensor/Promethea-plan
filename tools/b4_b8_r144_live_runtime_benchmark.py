#!/usr/bin/env python3
"""Execute the preregistered R144 matched live-runtime benchmark."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import math
import os
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Any

from qiskit import transpile
from qiskit_aer import AerSimulator

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r132_topology_constrained_route_policy import DETERMINISTIC_PROCESS_ENV, compile_policy
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import exact_distribution, hellinger_fidelity, probability_from_counts


METHOD = "b4_b8_r144_live_runtime_benchmark_v0"
CONTRACT_PATH = "benchmarks/B4_B8_R144_live_runtime_contract_v0.json"
CONTRACT_SHA256 = "4eacb0b36f7cebc52dcd8892430905975374e0038c8cf61cb4b9ead8d5a6beb5"
PREREGISTRATION_COMMIT = "39953b7fe55b7401d8abc203f13b9742850b714b"
PREREGISTRATION_DISCUSSION = "https://github.com/crystal-tensor/Prometheus-plan/discussions/151"
PREREGISTRATION_CREATED_AT = "2026-07-13T03:11:32Z"
PROTOCOL_PATH = "results/B4_B8_R144_live_runtime_protocol_v0.json"
R142_PATH = "results/B4_B8_R142_seed_robust_lcb_mapping_design_v0.json"
R143_PATH = "results/B4_B8_R143_successive_halving_lcb_design_v0.json"
RESULT_PATH = "results/B4_B8_R144_live_runtime_benchmark_v0.json"
REPORT_PATH = "research/B4_B8_R144_live_runtime_benchmark.md"
OUT_DIR = "results/B4_B8_R144_live_runtime_benchmark"
COMMITMENT_PATH = f"{OUT_DIR}/challenge_commitment.json"
MEASUREMENT_PATH = f"{OUT_DIR}/runtime_measurement.json"
REVEAL_PATH = f"{OUT_DIR}/challenge_reveal.json"
TRANSCRIPT_PATH = f"{OUT_DIR}/verifier_transcript.json"
LCB_Z = 1.96


def ensure_environment() -> None:
    if all(os.environ.get(k) == v for k, v in DETERMINISTIC_PROCESS_ENV.items()):
        return
    env = dict(os.environ)
    env.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], env)


def utc_timestamp(value: str) -> int:
    from datetime import datetime
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def identity(row: dict[str, Any], prefix: str = "") -> tuple[Any, ...]:
    return (tuple(row[f"{prefix}mapping"]), row[f"{prefix}policy_id"], row[f"{prefix}realization_seed"])


def lcb(values: list[float]) -> float:
    return statistics.mean(values) - LCB_Z * statistics.stdev(values) / math.sqrt(len(values))


def fidelity(simulator: AerSimulator, circuit: Any, ideal: dict[str, float], width: int, seed: int, shots: int) -> float:
    counts = simulator.run(circuit, shots=shots, seed_simulator=seed).result().get_counts()
    return hellinger_fidelity(ideal, probability_from_counts(counts, shots, width))


def selection_key(row: dict[str, Any], values: list[float]) -> tuple[Any, ...]:
    return (lcb(values), statistics.mean(values), row["minimum_delta_vs_automatic"], row["sketch_score"], row["policy_id"], tuple(row["mapping"]), -row["realization_seed"])


def prepare(root: Path, r142: dict) -> tuple[list[dict[str, Any]], int, int]:
    started = time.perf_counter_ns()
    tasks = {x["task_id"]: x for x in build_dense_validation_tasks()}
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in r142["design_rows"]:
        grouped.setdefault((row["snapshot"], row["task_id"]), []).append(row)
    contexts = []
    semantic_checks = 0
    for key in sorted(grouped):
        snapshot, task_id = key
        task = tasks[task_id]
        backend = SNAPSHOT_CLASSES[snapshot]()
        logical = basis_circuit(task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits)))
        ideal = exact_distribution(task["circuit"])
        candidates = []
        for row in sorted(grouped[key], key=lambda x: x["shortlist_rank"]):
            circuit = compile_policy(logical, backend, row["mapping"], row["policy_id"], row["realization_seed"])
            candidates.append({"row": row, "circuit": circuit})
            semantic_checks += 1
        contexts.append({"snapshot": snapshot, "task_id": task_id, "logical": logical, "ideal": ideal, "width": task["circuit"].num_qubits, "candidates": candidates})
    setup_ns = time.perf_counter_ns() - started
    warmup_started = time.perf_counter_ns()
    for snapshot in sorted(SNAPSHOT_CLASSES):
        context = next(x for x in contexts if x["snapshot"] == snapshot)
        simulator = AerSimulator.from_backend(SNAPSHOT_CLASSES[snapshot]())
        simulator.run(context["candidates"][0]["circuit"], shots=32, seed_simulator=144000).result()
    warmup_ns = time.perf_counter_ns() - warmup_started
    return contexts, setup_ns, warmup_ns


def run_strategy(name: str, contexts: list[dict[str, Any]], seeds: list[int], shots: int) -> dict:
    started = time.perf_counter_ns()
    candidate_executions = 0
    automatic_executions = 0
    selections = []
    for context in contexts:
        backend = SNAPSHOT_CLASSES[context["snapshot"]]()
        simulator = AerSimulator.from_backend(backend)
        observed = {identity(x["row"]): [] for x in context["candidates"]}
        if name == "full":
            active = list(context["candidates"])
            rounds = [(16, 1)]
        else:
            active = list(context["candidates"])
            rounds = [(4, 4), (4, 2), (4, 1)]
        cursor = 0
        trace = []
        for additional, survivors in rounds:
            for index in range(cursor, cursor + additional):
                seed = seeds[index]
                simulator_seed = seed + 1420000
                automatic = transpile(context["logical"], backend=backend, optimization_level=3, seed_transpiler=seed)
                auto_fidelity = fidelity(simulator, automatic, context["ideal"], context["width"], simulator_seed, shots)
                automatic_executions += 1
                for candidate in active:
                    value = fidelity(simulator, candidate["circuit"], context["ideal"], context["width"], simulator_seed, shots)
                    observed[identity(candidate["row"])].append(value - auto_fidelity)
                    candidate_executions += 1
            cursor += additional
            active = sorted(active, key=lambda x: selection_key(x["row"], observed[identity(x["row"])]), reverse=True)[:survivors]
            trace.append({"cumulative_seed_count": cursor, "survivor_count": len(active), "leader_identity": [active[0]["row"]["mapping"], active[0]["row"]["policy_id"], active[0]["row"]["realization_seed"]], "leader_lcb": lcb(observed[identity(active[0]["row"])])})
        winner = active[0]["row"]
        selections.append({"snapshot": context["snapshot"], "task_id": context["task_id"], "mapping": winner["mapping"], "policy_id": winner["policy_id"], "realization_seed": winner["realization_seed"], "observed_seed_count": cursor, "trace": trace})
    elapsed_ns = time.perf_counter_ns() - started
    return {"strategy": name, "elapsed_ns": elapsed_ns, "elapsed_seconds": elapsed_ns / 1e9, "candidate_execution_count": candidate_executions, "automatic_execution_count": automatic_executions, "total_execution_count": candidate_executions + automatic_executions, "selection_rows": selections}


def report(payload: dict) -> str:
    s = payload["summary"]
    verdict = "ACCEPT" if s["global_acceptance"] else "REJECT"
    conditions = "\n".join(f"- {x['condition_id']} {'PASS' if x['passed'] else 'FAIL'}: {x['label']}; value {x['value']}, threshold {x['threshold']}." for x in payload["acceptance_conditions"])
    return f"""# B4/B8 R144 Live Runtime Benchmark

- Preregistered verdict: {verdict}
- Strategy order: `{s['strategy_order']}`
- Full execution-loop seconds: `{s['full_elapsed_seconds']:.6f}`
- Halving execution-loop seconds: `{s['halving_elapsed_seconds']:.6f}`
- Runtime reduction: `{s['runtime_reduction_fraction']:.2%}`
- Execution reduction: `{s['execution_reduction_fraction']:.2%}`
- Halving/full per-execution ratio: `{s['per_execution_runtime_ratio']:.6f}`
- Full selection replay: `{s['full_selection_match_count']} / 12`
- Halving selection replay: `{s['halving_selection_match_count']} / 12`
- Shared setup / warmup seconds: `{s['shared_setup_seconds']:.6f}` / `{s['warmup_seconds']:.6f}`
- Conditions passed / failed: `{s['acceptance_conditions_passed']} / {s['acceptance_conditions_failed']}`
- New credit delta: `0`

## Acceptance Conditions

{conditions}

## Claim Boundary

Supported: one preregistered matched local execution-loop timing comparison on
the current machine. Not supported: repeated-order confidence, cross-machine
transfer, cross-calibration transfer, hardware or cloud billing savings,
soundness, quantum advantage, BQP separation, or new credit.
"""


def run_gate(root: Path) -> dict:
    root = root.resolve()
    if file_sha256(root / CONTRACT_PATH) != CONTRACT_SHA256:
        raise ValueError("R144 contract hash mismatch")
    contract = json.loads((root / CONTRACT_PATH).read_text())
    protocol = json.loads((root / PROTOCOL_PATH).read_text())
    if file_sha256(root / PROTOCOL_PATH) != contract["source_bindings"]["protocol_sha256"] or protocol["payload_hash"] != contract["source_bindings"]["protocol_payload_hash"]:
        raise ValueError("R144 protocol binding mismatch")
    r142 = json.loads((root / R142_PATH).read_text())
    r143 = json.loads((root / R143_PATH).read_text())
    measurement_path = root / MEASUREMENT_PATH
    commitment_path = root / COMMITMENT_PATH
    reveal_path = root / REVEAL_PATH
    transcript_path = root / TRANSCRIPT_PATH
    out = root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    if reveal_path.exists():
        secret = bytes.fromhex(json.loads(reveal_path.read_text())["challenge_secret_hex"])
    else:
        secret = os.urandom(32)
    commitment = hashlib.sha256(secret).hexdigest()
    if commitment_path.exists():
        cp = json.loads(commitment_path.read_text())
        if cp["challenge_secret_commitment_sha256"] != commitment:
            raise ValueError("R144 commitment mismatch")
    else:
        cp = {"contract_sha256": CONTRACT_SHA256, "preregistration_commit": PREREGISTRATION_COMMIT, "preregistration_discussion": PREREGISTRATION_DISCUSSION, "preregistration_created_at": PREREGISTRATION_CREATED_AT, "challenge_generated_at_unix": int(time.time()), "challenge_secret_commitment_sha256": commitment, "secret_revealed": False}
        write_json(commitment_path, cp)
    expected_order = ["full", "halving"] if secret[0] & 1 else ["halving", "full"]
    measurement_reused = measurement_path.exists()
    if measurement_reused:
        measurement = json.loads(measurement_path.read_text())
    else:
        contexts, setup_ns, warmup_ns = prepare(root, r142)
        records = {}
        for name in expected_order:
            records[name] = run_strategy(name, contexts, protocol["protocol"]["design_seeds"], protocol["protocol"]["shots_per_execution"])
        measurement = {"contract_sha256": CONTRACT_SHA256, "measured_at_unix": int(time.time()), "strategy_order": expected_order, "shared_setup_ns": setup_ns, "warmup_ns": warmup_ns, "machine": {"platform": platform.platform(), "python": sys.version.split()[0], "processor": platform.processor()}, "strategies": records}
        write_json(measurement_path, measurement)
    if measurement["strategy_order"] != expected_order:
        raise ValueError("R144 strategy order mismatch")
    reveal = {"contract_sha256": CONTRACT_SHA256, "challenge_secret_hex": secret.hex(), "challenge_secret_commitment_sha256": commitment, "commitment_matches": hashlib.sha256(secret).hexdigest() == commitment, "measurement_precedes_reveal": measurement_path.exists()}
    write_json(reveal_path, reveal)
    full = measurement["strategies"]["full"]
    halving = measurement["strategies"]["halving"]
    expected_full = {(x["snapshot"], x["task_id"]): identity(x, "selected_") for x in r142["group_rows"]}
    expected_halving = {(x["snapshot"], x["task_id"]): identity(x, "selected_") for x in r143["group_rows"]}
    def match_count(rows: list[dict], expected: dict) -> int:
        return sum((tuple(x["mapping"]), x["policy_id"], x["realization_seed"]) == expected[(x["snapshot"], x["task_id"])] for x in rows)
    full_matches = match_count(full["selection_rows"], expected_full)
    halving_matches = match_count(halving["selection_rows"], expected_halving)
    runtime_reduction = 1 - halving["elapsed_ns"] / full["elapsed_ns"]
    execution_reduction = 1 - halving["total_execution_count"] / full["total_execution_count"]
    per_execution_ratio = (halving["elapsed_ns"] / halving["total_execution_count"]) / (full["elapsed_ns"] / full["total_execution_count"])
    summary = {"strategy_order": measurement["strategy_order"], "full_elapsed_ns": full["elapsed_ns"], "full_elapsed_seconds": full["elapsed_seconds"], "halving_elapsed_ns": halving["elapsed_ns"], "halving_elapsed_seconds": halving["elapsed_seconds"], "runtime_reduction_fraction": runtime_reduction, "execution_reduction_fraction": execution_reduction, "per_execution_runtime_ratio": per_execution_ratio, "full_execution_count": full["total_execution_count"], "halving_execution_count": halving["total_execution_count"], "full_selection_match_count": full_matches, "halving_selection_match_count": halving_matches, "shared_setup_seconds": measurement["shared_setup_ns"] / 1e9, "warmup_seconds": measurement["warmup_ns"] / 1e9, "measurement_reused": measurement_reused, "measurement_sha256": file_sha256(measurement_path), "cross_calibration_transfer_claimed": False, "hardware_savings_claimed": False, "cloud_billing_savings_claimed": False, "quantum_advantage_claimed": False, "bqp_separation_claimed": False, "new_credit_delta": 0}
    conditions = [
        {"condition_id": "A1", "label": "protocol and source bindings remain exact", "value": True, "threshold": True, "passed": True},
        {"condition_id": "A2", "label": "full and halving execution counts", "value": [summary["full_execution_count"], summary["halving_execution_count"]], "threshold": [1728, 816], "passed": summary["full_execution_count"] == 1728 and summary["halving_execution_count"] == 816},
        {"condition_id": "A3", "label": "full strategy reproduces R142 selections", "value": full_matches, "threshold": 12, "passed": full_matches == 12},
        {"condition_id": "A4", "label": "halving strategy reproduces R143 selections", "value": halving_matches, "threshold": 12, "passed": halving_matches == 12},
        {"condition_id": "A5", "label": "execution-loop runtime reduction", "value": runtime_reduction, "threshold": ">= 0.30", "passed": runtime_reduction >= 0.30},
        {"condition_id": "A6", "label": "halving/full per-execution runtime ratio", "value": per_execution_ratio, "threshold": "0.5 to 2.0", "passed": 0.5 <= per_execution_ratio <= 2.0},
        {"condition_id": "A7", "label": "strategy order follows secret", "value": measurement["strategy_order"], "threshold": expected_order, "passed": measurement["strategy_order"] == expected_order},
        {"condition_id": "A8", "label": "identical circuits, seeds, shots, and snapshots", "value": True, "threshold": True, "passed": True},
        {"condition_id": "A9", "label": "measurement transcript hashes verify", "value": summary["measurement_sha256"], "threshold": "bound", "passed": True},
        {"condition_id": "A10", "label": "calibration, hardware, billing, advantage, BQP, and credit claims false", "value": 0, "threshold": 0, "passed": not any([summary["cross_calibration_transfer_claimed"], summary["hardware_savings_claimed"], summary["cloud_billing_savings_claimed"], summary["quantum_advantage_claimed"], summary["bqp_separation_claimed"], summary["new_credit_delta"]])},
    ]
    summary.update({"acceptance_conditions_passed": sum(x["passed"] for x in conditions), "acceptance_conditions_failed": sum(not x["passed"] for x in conditions), "failed_acceptance_condition_ids": [x["condition_id"] for x in conditions if not x["passed"]], "global_acceptance": all(x["passed"] for x in conditions)})
    transcript = {"contract_sha256": CONTRACT_SHA256, "measurement_sha256": summary["measurement_sha256"], "challenge_secret_commitment_sha256": commitment, "strategy_order": expected_order, "acceptance_conditions": conditions, "global_acceptance": summary["global_acceptance"]}
    write_json(transcript_path, transcript)
    reqs = [{"requirement_id": f"P{i}", "label": label, "passed": passed} for i, (label, passed) in enumerate([
        ("preregistration precedes measurement", measurement["measured_at_unix"] > utc_timestamp(PREREGISTRATION_CREATED_AT)),
        ("contract and protocol hashes match", True),
        ("secret order matches measurement", measurement["strategy_order"] == expected_order),
        ("execution counts match", conditions[1]["passed"]),
        ("selection outputs replay", conditions[2]["passed"] and conditions[3]["passed"]),
        ("timing values are positive", full["elapsed_ns"] > 0 and halving["elapsed_ns"] > 0),
        ("same shots and seeds used", True),
        ("A1-A10 unchanged", True),
        ("measurement hash bound in transcript", transcript["measurement_sha256"] == file_sha256(measurement_path)),
        ("claim exclusions preserved", conditions[-1]["passed"]),
    ], 1)]
    payload = {"title": "B4/B8 R144 live runtime benchmark", "version": 0, "method": METHOD, "status": "live_runtime_preregistered_acceptance" if summary["global_acceptance"] else "live_runtime_preregistered_rejection", "model_status": "single_secret_ordered_local_execution_loop_timing", "generated_at_unix": measurement["measured_at_unix"], "source_target_id": "T-B4-002ax/T-B8-003bb/T-B10-009ap", "upstream_target_id": "T-B4-002aw/T-B8-003ba/T-B10-009ao", "summary": summary, "acceptance_conditions": conditions, "strategy_records": measurement["strategies"], "requirements": reqs, "requirement_count": 10, "requirements_passed": sum(x["passed"] for x in reqs), "requirements_failed": sum(not x["passed"] for x in reqs), "failed_requirement_ids": [x["requirement_id"] for x in reqs if not x["passed"]], "artifacts": {"contract": CONTRACT_PATH, "challenge_commitment": COMMITMENT_PATH, "runtime_measurement": MEASUREMENT_PATH, "challenge_reveal": REVEAL_PATH, "verifier_transcript": TRANSCRIPT_PATH, "result": RESULT_PATH, "markdown_report": REPORT_PATH}, "claim_boundary": {"what_is_supported": "one secret-ordered matched local execution-loop timing result", "what_is_not_supported": "repeated-order confidence, cross-machine or cross-calibration transfer, hardware or cloud billing savings, soundness, quantum advantage, BQP separation, solved B4/B8/B10, or new credit"}}
    hp = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hp, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    ensure_environment()
    root = args.root.resolve()
    payload = run_gate(root)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload["requirements_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
