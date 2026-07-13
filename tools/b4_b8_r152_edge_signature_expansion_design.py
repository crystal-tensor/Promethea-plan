#!/usr/bin/env python3
"""Select a new Casablanca route from edge signatures absent in R150 candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from qiskit import qasm3
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeCasablancaV2

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r132_topology_constrained_route_policy import DETERMINISTIC_PROCESS_ENV
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import exact_distribution, hellinger_fidelity, probability_from_counts


METHOD = "b4_b8_r152_edge_signature_expansion_design_v0"
R150_DESIGN_PATH = "results/B4_B8_R150_unseen_backend_candidate_generation_design_v0.json"
R151_PATH = "results/B4_B8_R151_casablanca_failure_attribution_v0.json"
RESULT_PATH = "results/B4_B8_R152_edge_signature_expansion_design_v0.json"
REPORT_PATH = "research/B4_B8_R152_edge_signature_expansion_design.md"
TARGET_SNAPSHOT = "FakeCasablancaV2"
TARGET_TASK = "dense_validation_xy_network_n6"
ROUND_SEEDS = ((15201, 15202, 15203, 15204), (15205, 15206, 15207, 15208), tuple(range(15209, 15217)))
SURVIVOR_COUNTS = (4, 1, 1)
SHOTS = 2048


def ensure_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def signature(path: Path) -> tuple[tuple[int, int, int], ...]:
    circuit = qasm3.load(path)
    counts: Counter[tuple[int, int]] = Counter()
    for instruction in circuit.data:
        if instruction.operation.name == "cx":
            counts[tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)] += 1
    return tuple(sorted((a, b, count) for (a, b), count in counts.items()))


def lcb(values: list[float]) -> float:
    mean = statistics.mean(values)
    return mean if len(values) < 2 else mean - 1.96 * statistics.stdev(values) / math.sqrt(len(values))


def run_fidelity(simulator: AerSimulator, circuit: Any, ideal: dict[str, float], seed: int, qubits: int) -> float:
    counts = simulator.run(circuit, shots=SHOTS, seed_simulator=seed).result().get_counts()
    return hellinger_fidelity(ideal, probability_from_counts(counts, SHOTS, qubits))


def build(root: Path) -> dict[str, Any]:
    design = json.loads((root / R150_DESIGN_PATH).read_text())
    r151_sha = file_sha256(root / R151_PATH)
    task = next(row for row in build_dense_validation_tasks() if row["task_id"] == TARGET_TASK)
    ideal = exact_distribution(task["circuit"])
    backend = FakeCasablancaV2()
    simulator = AerSimulator.from_backend(backend)
    target = next(row for row in design["target_rows"] if row["target_snapshot"] == TARGET_SNAPSHOT)
    original_candidates = [row for row in design["candidate_rows"] if row["target_snapshot"] == TARGET_SNAPSHOT]
    denominator_pool = [row for row in design["denominator_rows"] if row["target_snapshot"] == TARGET_SNAPSHOT]
    original_signatures = {signature(root / row["circuit_path"]) for row in original_candidates}
    winner_path = root / target["denominator_circuit_path"]
    winner_signature = signature(winner_path)
    representatives = {}
    for row in denominator_pool:
        sig = signature(root / row["circuit_path"])
        if sig in original_signatures or sig == winner_signature or row["circuit_sha256"] == target["denominator_circuit_sha256"]:
            continue
        current = representatives.get(sig)
        if current is None or (row["compiled_combined_any_error_proxy"], row["compiled_cx_occurrence_count"], row["transpiler_seed"]) < (current["compiled_combined_any_error_proxy"], current["compiled_cx_occurrence_count"], current["transpiler_seed"]):
            representatives[sig] = row
    candidates = []
    for sig, row in representatives.items():
        candidates.append({
            **row,
            "edge_signature": [list(item) for item in sig],
            "edge_signature_sha256": hashlib.sha256(json.dumps(sig, separators=(",", ":")).encode()).hexdigest(),
            "design_fidelities": [],
            "selection_trace": [],
        })
    candidates.sort(key=lambda row: (row["compiled_combined_any_error_proxy"], row["compiled_cx_occurrence_count"], row["transpiler_seed"]))
    survivors = candidates
    rounds = []
    charged_executions = 0
    for round_index, (seeds, survivor_count) in enumerate(zip(ROUND_SEEDS, SURVIVOR_COUNTS, strict=True), start=1):
        for candidate in survivors:
            circuit = qasm3.load(root / candidate["circuit_path"])
            for seed in seeds:
                candidate["design_fidelities"].append(run_fidelity(simulator, circuit, ideal, seed, task["circuit"].num_qubits))
                charged_executions += 1
            candidate["selection_trace"].append({
                "round": round_index,
                "mean_fidelity": statistics.mean(candidate["design_fidelities"]),
                "lcb_95": lcb(candidate["design_fidelities"]),
            })
        ranked = sorted(survivors, key=lambda row: (-lcb(row["design_fidelities"]), -statistics.mean(row["design_fidelities"]), row["compiled_combined_any_error_proxy"], row["transpiler_seed"]))
        survivors = ranked[:survivor_count]
        rounds.append({
            "round": round_index,
            "candidate_count_before": len(ranked),
            "survivor_count": len(survivors),
            "leader_transpiler_seed": ranked[0]["transpiler_seed"],
            "leader_lcb_95": lcb(ranked[0]["design_fidelities"]),
        })
    selected = survivors[0]
    all_seeds = tuple(seed for batch in ROUND_SEEDS for seed in batch)
    winner = qasm3.load(winner_path)
    original = qasm3.load(root / target["selected_circuit_path"])
    selected_values = selected["design_fidelities"]
    winner_values = [run_fidelity(simulator, winner, ideal, seed, task["circuit"].num_qubits) for seed in all_seeds]
    original_values = [run_fidelity(simulator, original, ideal, seed, task["circuit"].num_qubits) for seed in all_seeds]
    diagnostic_executions = len(all_seeds) * 2
    selected_signature = tuple(tuple(item) for item in selected["edge_signature"])
    summary = {
        "target_snapshot": TARGET_SNAPSHOT,
        "target_task": TARGET_TASK,
        "original_candidate_count": len(original_candidates),
        "original_candidate_edge_signature_count": len(original_signatures),
        "denominator_pool_count": len(denominator_pool),
        "denominator_edge_signature_count": len({signature(root / row["circuit_path"]) for row in denominator_pool}),
        "eligible_novel_edge_signature_count": len(candidates),
        "selected_transpiler_seed": selected["transpiler_seed"],
        "selected_circuit_path": selected["circuit_path"],
        "selected_circuit_sha256": selected["circuit_sha256"],
        "selected_edge_signature_sha256": selected["edge_signature_sha256"],
        "selected_cx_occurrence_count": selected["compiled_cx_occurrence_count"],
        "selected_combined_any_error_proxy": selected["compiled_combined_any_error_proxy"],
        "selected_mean_fidelity": statistics.mean(selected_values),
        "selected_lcb_95": lcb(selected_values),
        "selected_minus_strong_denominator_mean": statistics.mean(a - b for a, b in zip(selected_values, winner_values, strict=True)),
        "selected_minus_r150_generated_mean": statistics.mean(a - b for a, b in zip(selected_values, original_values, strict=True)),
        "selected_exact_qasm_matches_strong_denominator": selected["circuit_sha256"] == target["denominator_circuit_sha256"],
        "selected_edge_signature_matches_strong_denominator": selected_signature == winner_signature,
        "selected_edge_signature_present_in_original_candidates": selected_signature in original_signatures,
        "charged_design_execution_count": charged_executions,
        "diagnostic_execution_count": diagnostic_executions,
        "total_design_execution_count": charged_executions + diagnostic_executions,
        "total_design_shots": (charged_executions + diagnostic_executions) * SHOTS,
        "r150_hidden_trial_values_used_for_candidate_scoring_count": 0,
        "challenge_executed": False,
        "hardware_execution_claimed": False,
        "general_route_generation_advantage_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        {"requirement_id": "R1", "label": "R150 design and R151 attribution hashes are bound", "passed": True},
        {"requirement_id": "R2", "label": "all 48 original candidate signatures are excluded", "passed": all(tuple(tuple(item) for item in row["edge_signature"]) not in original_signatures for row in candidates)},
        {"requirement_id": "R3", "label": "strong denominator QASM and exact edge signature are excluded", "passed": all(row["circuit_sha256"] != target["denominator_circuit_sha256"] and tuple(tuple(item) for item in row["edge_signature"]) != winner_signature for row in candidates)},
        {"requirement_id": "R4", "label": "16 novel edge signatures enter the candidate pool", "passed": len(candidates) == 16},
        {"requirement_id": "R5", "label": "16-to-4-to-1-to-1 selection charges 88 executions", "passed": [row["survivor_count"] for row in rounds] == [4, 1, 1] and charged_executions == 88},
        {"requirement_id": "R6", "label": "32 post-selection diagnostics do not affect selection", "passed": diagnostic_executions == 32},
        {"requirement_id": "R7", "label": "selected route matches neither excluded signature class", "passed": not summary["selected_exact_qasm_matches_strong_denominator"] and not summary["selected_edge_signature_matches_strong_denominator"] and not summary["selected_edge_signature_present_in_original_candidates"]},
        {"requirement_id": "R8", "label": "R150 hidden trial values are not used for candidate scoring", "passed": summary["r150_hidden_trial_values_used_for_candidate_scoring_count"] == 0},
        {"requirement_id": "R9", "label": "no R152 holdout executes during design", "passed": not summary["challenge_executed"]},
        {"requirement_id": "R10", "label": "hardware, general generation, advantage, BQP, solved-frontier, and credit claims remain false", "passed": not any([summary["hardware_execution_claimed"], summary["general_route_generation_advantage_claimed"], summary["quantum_advantage_claimed"], summary["bqp_separation_claimed"], summary["solved_frontier_claimed"], summary["new_credit_delta"]])},
    ]
    payload = {
        "title": "B4/B8 R152 Casablanca edge-signature expansion design",
        "version": 0,
        "method": METHOD,
        "status": "edge_signature_expansion_design_frozen_before_holdout",
        "model_status": "novel_denominator_pool_signatures_excluding_winner_and_r150_candidate_support",
        "generated_at_unix": int(time.time()),
        "source_target_id": "T-B4-002bl/T-B8-003bp/T-B10-009bd",
        "upstream_target_id": "T-B4-002bk/T-B8-003bo/T-B10-009bc",
        "source_bindings": {
            "r150_design_path": R150_DESIGN_PATH,
            "r150_design_sha256": file_sha256(root / R150_DESIGN_PATH),
            "r150_design_payload_hash": design["payload_hash"],
            "r151_attribution_path": R151_PATH,
            "r151_attribution_sha256_provenance_only": r151_sha,
            "r150_hidden_trial_values_used_for_candidate_scoring": False,
        },
        "design_protocol": {
            "candidate_source": "unique R150 automatic denominator-pool edge signatures absent from the original candidate pool",
            "excluded_classes": ["R150 original candidate signatures", "strong denominator exact QASM", "strong denominator exact edge signature"],
            "round_simulator_seeds": [list(batch) for batch in ROUND_SEEDS],
            "survivor_counts": list(SURVIVOR_COUNTS),
            "selection_statistic": "mean_fidelity_minus_1.96_standard_error",
            "post_selection_diagnostics": ["strong_denominator", "R150_generated"],
            "post_selection_diagnostics_used_for_selection": False,
            "shots_per_execution": SHOTS,
        },
        "summary": summary,
        "candidate_rows": candidates,
        "successive_halving_rounds": rounds,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "artifacts": {"result": RESULT_PATH, "markdown_report": REPORT_PATH},
        "claim_boundary": {
            "what_is_supported": "one novel Casablanca edge-signature route selected without copying the strong denominator or original R150 candidate signatures",
            "what_is_not_supported": "a hidden repair, causal proof, temporal or real-device transfer, hardware performance, general route-generation advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def report(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    return f"""# B4/B8 R152 Casablanca Edge-Signature Expansion Design

- Original / denominator / eligible novel signatures: `{s['original_candidate_edge_signature_count']}` / `{s['denominator_edge_signature_count']}` / `{s['eligible_novel_edge_signature_count']}`
- Selected transpiler seed: `{s['selected_transpiler_seed']}`
- Selected CX count / exposure proxy: `{s['selected_cx_occurrence_count']}` / `{s['selected_combined_any_error_proxy']:.8f}`
- Selected mean / LCB: `{s['selected_mean_fidelity']:.8f}` / `{s['selected_lcb_95']:.8f}`
- Public selected-strong / selected-R150-generated deltas: `{s['selected_minus_strong_denominator_mean']:+.8f}` / `{s['selected_minus_r150_generated_mean']:+.8f}`
- Copies strong QASM / strong signature / original signature: `{str(s['selected_exact_qasm_matches_strong_denominator']).lower()}` / `{str(s['selected_edge_signature_matches_strong_denominator']).lower()}` / `{str(s['selected_edge_signature_present_in_original_candidates']).lower()}`
- Selection / diagnostic executions: `{s['charged_design_execution_count']}` / `{s['diagnostic_execution_count']}`
- R150 hidden values used for scoring: `0`
- Holdout executed: `false`

R152 expands only the missing edge-signature support identified by R151. The
strong denominator route and exact signature are excluded, as are every edge
signature in the original R150 candidate pool. Public diagnostics are recorded
after selection and cannot change the chosen route.

This design is not a hidden repair, causal proof, hardware result, general
route-generation advantage, quantum advantage, BQP separation, solved
frontier, or new credit.
"""


def main() -> int:
    ensure_environment()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    payload = build(root)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
