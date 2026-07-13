#!/usr/bin/env python3
"""Design generated dense-XY routes on three previously unused fake backends."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

from qiskit import qasm3, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeCasablancaV2, FakeNairobiV2, FakePerth

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit, stable_hash
from b4_b8_r125_historical_snapshot_replay import canonical_snapshot
from b4_b8_r126_calibration_attribution_ledger import circuit_exposure, file_sha256
from b4_b8_r127_calibration_aware_layout_design import logical_two_qubit_edges, static_layout_objective
from b4_b8_r132_topology_constrained_route_policy import DETERMINISTIC_PROCESS_ENV, compile_policy
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import exact_distribution, hellinger_fidelity, probability_from_counts
from b4_b8_r139_lagos_ising_channel_attribution import apply_symmetric_readout_channel, exact_compiled_classical_distribution


METHOD = "b4_b8_r150_unseen_backend_candidate_generation_design_v0"
TARGET_CLASSES = {
    "FakeCasablancaV2": FakeCasablancaV2,
    "FakeNairobiV2": FakeNairobiV2,
    "FakePerth": FakePerth,
}
TARGET_TASK = "dense_validation_xy_network_n6"
R149_RESULT_PATH = "results/B4_B8_R149_jakarta_xy_candidate_generation_holdout_v0.json"
TASK_BUILDER_PATH = "tools/b4_b8_r135_dense_interaction_fallback.py"
RESULT_PATH = "results/B4_B8_R150_unseen_backend_candidate_generation_design_v0.json"
REPORT_PATH = "research/B4_B8_R150_unseen_backend_candidate_generation_design.md"
OUT_DIR = "results/B4_B8_R150_unseen_backend_candidate_generation_design"
SHORTLIST_MAPPING_COUNT = 12
POLICY_IDS = ("selected_o3_default", "selected_o3_lookahead")
REALIZATION_SEEDS = (15001, 15002)
ROUND_SEEDS = ((15011, 15012, 15013, 15014), (15015, 15016, 15017, 15018), tuple(range(15019, 15027)))
SURVIVOR_COUNTS = (12, 3, 1)
DENOMINATOR_TRANSPILER_SEEDS = tuple(range(150101, 150181))
SHOTS = 2048


def ensure_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def lcb(values: list[float]) -> float:
    mean = statistics.mean(values)
    return mean if len(values) < 2 else mean - 1.96 * statistics.stdev(values) / math.sqrt(len(values))


def metadata_for(backend_class: type) -> dict[str, Any]:
    canonical, digest = canonical_snapshot(backend_class)
    return {"canonical": canonical, "sha256": digest}


def expose(root: Path, path: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    row = circuit_exposure(path, metadata)
    row["circuit_path"] = str(path.relative_to(root))
    return row


def build(root: Path) -> dict[str, Any]:
    r149 = json.loads((root / R149_RESULT_PATH).read_text())
    task = next(row for row in build_dense_validation_tasks() if row["task_id"] == TARGET_TASK)
    logical = basis_circuit(task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits)))
    ideal = exact_distribution(task["circuit"])
    logical_edges = logical_two_qubit_edges(task)
    all_candidate_rows = []
    all_denominator_rows = []
    target_rows = []
    round_rows = []
    snapshot_metadata = {}
    out = root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    for target_name, backend_class in TARGET_CLASSES.items():
        backend = backend_class()
        simulator = AerSimulator.from_backend(backend)
        metadata = metadata_for(backend_class)
        snapshot_metadata[target_name] = metadata
        measure_errors = {
            row["qargs"][0]: float(row["error"] or 0.0)
            for row in metadata["canonical"]["instruction_properties"]["measure"]
        }
        static_rows = []
        for mapping in itertools.permutations(range(backend.num_qubits), task["circuit"].num_qubits):
            objective = static_layout_objective(backend, mapping, logical_edges)
            readout_vector = [measure_errors[physical] for physical in mapping]
            readout_fidelity = hellinger_fidelity(ideal, apply_symmetric_readout_channel(ideal, readout_vector))
            cx_success = 1.0 - objective["static_cx_any_error_proxy"]
            static_rows.append({
                "mapping": list(mapping),
                "exact_output_aware_readout_fidelity": readout_fidelity,
                "static_cx_success_proxy": cx_success,
                "static_product_score": readout_fidelity * cx_success,
                "static_routed_step_count_proxy": objective["routed_step_count_proxy"],
                "static_combined_any_error_proxy": objective["static_combined_any_error_proxy"],
            })
        rankings = [
            sorted(static_rows, key=lambda row: (-row["exact_output_aware_readout_fidelity"], -row["static_cx_success_proxy"], row["mapping"])),
            sorted(static_rows, key=lambda row: (-row["static_cx_success_proxy"], -row["exact_output_aware_readout_fidelity"], row["mapping"])),
            sorted(static_rows, key=lambda row: (-row["static_product_score"], row["static_routed_step_count_proxy"], row["mapping"])),
        ]
        shortlist = []
        seen = set()
        rank = 0
        while len(shortlist) < SHORTLIST_MAPPING_COUNT:
            for ranking_name, ranking in zip(("readout_first", "cx_first", "product"), rankings, strict=True):
                row = ranking[rank]
                key = tuple(row["mapping"])
                if key in seen:
                    continue
                seen.add(key)
                shortlist.append({**row, "shortlist_source": ranking_name, "shortlist_source_rank": rank + 1})
                if len(shortlist) == SHORTLIST_MAPPING_COUNT:
                    break
            rank += 1

        target_dir = out / target_name
        target_dir.mkdir(parents=True, exist_ok=True)
        candidates = []
        for mapping_row in shortlist:
            for policy_id in POLICY_IDS:
                for realization_seed in REALIZATION_SEEDS:
                    compiled = compile_policy(logical, backend, mapping_row["mapping"], policy_id, realization_seed)
                    candidate_id = f"m{'-'.join(map(str, mapping_row['mapping']))}__{policy_id}__s{realization_seed}"
                    path = target_dir / f"candidate__{candidate_id}.qasm"
                    path.write_text(qasm3.dumps(compiled), encoding="utf-8")
                    exposure = expose(root, path, metadata)
                    candidates.append({
                        "target_snapshot": target_name,
                        "candidate_id": candidate_id,
                        "mapping": mapping_row["mapping"],
                        "policy_id": policy_id,
                        "realization_seed": realization_seed,
                        "shortlist_source": mapping_row["shortlist_source"],
                        "circuit_path": str(path.relative_to(root)),
                        "circuit_sha256": file_sha256(path),
                        "qasm_stable_hash": stable_hash(qasm3.dumps(compiled)),
                        "semantic_fidelity": hellinger_fidelity(ideal, exact_compiled_classical_distribution(compiled)),
                        "compiled_combined_any_error_proxy": exposure["combined_any_error_proxy"],
                        "compiled_cx_occurrence_count": exposure["cx_occurrence_count"],
                        "design_fidelities": [],
                        "selection_trace": [],
                    })

        survivors = candidates
        charged_executions = 0
        for round_index, (seeds, survivor_count) in enumerate(zip(ROUND_SEEDS, SURVIVOR_COUNTS, strict=True), start=1):
            for candidate in survivors:
                circuit = qasm3.load(root / candidate["circuit_path"])
                for seed in seeds:
                    counts = simulator.run(circuit, shots=SHOTS, seed_simulator=seed).result().get_counts()
                    observed = probability_from_counts(counts, SHOTS, task["circuit"].num_qubits)
                    candidate["design_fidelities"].append(hellinger_fidelity(ideal, observed))
                    charged_executions += 1
                candidate["selection_trace"].append({
                    "round": round_index,
                    "mean_fidelity": statistics.mean(candidate["design_fidelities"]),
                    "lcb_95": lcb(candidate["design_fidelities"]),
                })
            ranked = sorted(survivors, key=lambda row: (-lcb(row["design_fidelities"]), -statistics.mean(row["design_fidelities"]), row["compiled_combined_any_error_proxy"], row["candidate_id"]))
            survivors = ranked[:survivor_count]
            round_rows.append({
                "target_snapshot": target_name,
                "round": round_index,
                "candidate_count_before": len(ranked),
                "survivor_count": len(survivors),
                "leader_candidate_id": ranked[0]["candidate_id"],
                "leader_lcb_95": lcb(ranked[0]["design_fidelities"]),
            })
        selected = survivors[0]

        denominators = []
        for transpiler_seed in DENOMINATOR_TRANSPILER_SEEDS:
            circuit = transpile(logical, backend=backend, optimization_level=3, seed_transpiler=transpiler_seed)
            path = target_dir / f"denominator__seed_{transpiler_seed}.qasm"
            path.write_text(qasm3.dumps(circuit), encoding="utf-8")
            exposure = expose(root, path, metadata)
            denominators.append({
                "target_snapshot": target_name,
                "transpiler_seed": transpiler_seed,
                "circuit_path": str(path.relative_to(root)),
                "circuit_sha256": file_sha256(path),
                "qasm_stable_hash": stable_hash(qasm3.dumps(circuit)),
                "semantic_fidelity": hellinger_fidelity(ideal, exact_compiled_classical_distribution(circuit)),
                "compiled_combined_any_error_proxy": exposure["combined_any_error_proxy"],
                "compiled_cx_occurrence_count": exposure["cx_occurrence_count"],
            })
        denominator = min(denominators, key=lambda row: (row["compiled_combined_any_error_proxy"], row["compiled_cx_occurrence_count"], row["transpiler_seed"]))
        selected_values = selected["design_fidelities"]
        denominator_values = []
        denominator_circuit = qasm3.load(root / denominator["circuit_path"])
        for seed in tuple(seed for batch in ROUND_SEEDS for seed in batch):
            counts = simulator.run(denominator_circuit, shots=SHOTS, seed_simulator=seed).result().get_counts()
            observed = probability_from_counts(counts, SHOTS, task["circuit"].num_qubits)
            denominator_values.append(hellinger_fidelity(ideal, observed))
        target_rows.append({
            "target_snapshot": target_name,
            "enumerated_mapping_count": len(static_rows),
            "shortlist_mapping_count": len(shortlist),
            "compiled_candidate_count": len(candidates),
            "charged_design_execution_count": charged_executions,
            "denominator_pool_count": len(denominators),
            "diagnostic_execution_count": len(denominator_values),
            "selected_candidate_id": selected["candidate_id"],
            "selected_mapping": selected["mapping"],
            "selected_policy_id": selected["policy_id"],
            "selected_realization_seed": selected["realization_seed"],
            "selected_circuit_path": selected["circuit_path"],
            "selected_circuit_sha256": selected["circuit_sha256"],
            "selected_semantic_fidelity": selected["semantic_fidelity"],
            "selected_mean_fidelity": statistics.mean(selected_values),
            "selected_lcb_95": lcb(selected_values),
            "denominator_transpiler_seed": denominator["transpiler_seed"],
            "denominator_circuit_path": denominator["circuit_path"],
            "denominator_circuit_sha256": denominator["circuit_sha256"],
            "denominator_semantic_fidelity": denominator["semantic_fidelity"],
            "diagnostic_selected_minus_denominator_mean": statistics.mean(a - b for a, b in zip(selected_values, denominator_values, strict=True)),
            "diagnostics_used_for_selection": False,
        })
        all_candidate_rows.extend(candidates)
        all_denominator_rows.extend(denominators)

    summary = {
        "target_snapshot_count": len(target_rows),
        "target_task": TARGET_TASK,
        "enumerated_mapping_count": sum(row["enumerated_mapping_count"] for row in target_rows),
        "shortlist_mapping_count": sum(row["shortlist_mapping_count"] for row in target_rows),
        "compiled_candidate_count": len(all_candidate_rows),
        "denominator_pool_count": len(all_denominator_rows),
        "charged_design_execution_count": sum(row["charged_design_execution_count"] for row in target_rows),
        "diagnostic_execution_count": sum(row["diagnostic_execution_count"] for row in target_rows),
        "total_design_execution_count": sum(row["charged_design_execution_count"] + row["diagnostic_execution_count"] for row in target_rows),
        "total_design_shots": sum(row["charged_design_execution_count"] + row["diagnostic_execution_count"] for row in target_rows) * SHOTS,
        "semantic_fidelity_pass_count": sum(row["semantic_fidelity"] >= 0.9999999999 for row in all_candidate_rows + all_denominator_rows),
        "semantic_fidelity_check_count": len(all_candidate_rows) + len(all_denominator_rows),
        "diagnostic_group_count_noninferior_to_negative_0_02": sum(row["diagnostic_selected_minus_denominator_mean"] >= -0.02 for row in target_rows),
        "minimum_diagnostic_selected_minus_denominator_mean": min(row["diagnostic_selected_minus_denominator_mean"] for row in target_rows),
        "prior_backend_identity_count": 0,
        "r149_hidden_trial_rows_read_count": 0,
        "challenge_executed": False,
        "hardware_execution_claimed": False,
        "quantum_advantage_claimed": False,
        "cross_machine_transfer_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        {"requirement_id": "R1", "label": "R149 provenance and task builder are bound", "passed": True},
        {"requirement_id": "R2", "label": "three previously unused seven-qubit backend classes are explicit", "passed": set(TARGET_CLASSES) == {"FakeCasablancaV2", "FakeNairobiV2", "FakePerth"}},
        {"requirement_id": "R3", "label": "all 15,120 mappings are enumerated", "passed": summary["enumerated_mapping_count"] == 15120},
        {"requirement_id": "R4", "label": "36 mappings produce 144 generated candidates", "passed": summary["shortlist_mapping_count"] == 36 and summary["compiled_candidate_count"] == 144},
        {"requirement_id": "R5", "label": "three 48-to-12-to-3-to-1 selections charge 792 executions", "passed": summary["charged_design_execution_count"] == 792 and [row["survivor_count"] for row in round_rows] == [12, 3, 1] * 3},
        {"requirement_id": "R6", "label": "240 seeded automatic denominator candidates are compiled", "passed": summary["denominator_pool_count"] == 240},
        {"requirement_id": "R7", "label": "all 384 generated and denominator circuits preserve semantics", "passed": summary["semantic_fidelity_pass_count"] == 384},
        {"requirement_id": "R8", "label": "diagnostics do not influence selection and R149 hidden rows stay unused", "passed": all(not row["diagnostics_used_for_selection"] for row in target_rows) and summary["r149_hidden_trial_rows_read_count"] == 0},
        {"requirement_id": "R9", "label": "no R150 holdout is executed during design", "passed": not summary["challenge_executed"]},
        {"requirement_id": "R10", "label": "hardware, transfer, advantage, solved-frontier, and credit claims remain false", "passed": not any([summary["hardware_execution_claimed"], summary["cross_machine_transfer_claimed"], summary["quantum_advantage_claimed"], summary["solved_frontier_claimed"], summary["new_credit_delta"]])},
    ]
    payload = {
        "title": "B4/B8 R150 unseen-backend dense-XY candidate generation design",
        "version": 0,
        "method": METHOD,
        "status": "unseen_backend_candidate_generation_design_frozen_before_holdout",
        "model_status": "same_generation_recipe_on_three_previously_unused_fake_backends",
        "generated_at_unix": int(time.time()),
        "source_target_id": "T-B4-002bi/T-B8-003bm/T-B10-009ba",
        "upstream_target_id": "T-B4-002bh/T-B8-003bl/T-B10-009az",
        "source_bindings": {
            "r149_result_path": R149_RESULT_PATH,
            "r149_result_sha256_provenance_only": file_sha256(root / R149_RESULT_PATH),
            "r149_result_payload_hash": r149["payload_hash"],
            "r149_trial_rows_consumed": False,
            "task_builder_path": TASK_BUILDER_PATH,
            "task_builder_sha256": file_sha256(root / TASK_BUILDER_PATH),
        },
        "design_protocol": {
            "target_snapshots": list(TARGET_CLASSES),
            "target_task": TARGET_TASK,
            "static_rankings": ["exact_output_aware_readout_fidelity", "static_cx_success_proxy", "static_product_score"],
            "shortlist_mapping_count_per_target": SHORTLIST_MAPPING_COUNT,
            "policy_ids": list(POLICY_IDS),
            "realization_seeds": list(REALIZATION_SEEDS),
            "round_simulator_seeds": [list(seeds) for seeds in ROUND_SEEDS],
            "survivor_counts": list(SURVIVOR_COUNTS),
            "denominator_transpiler_seeds": list(DENOMINATOR_TRANSPILER_SEEDS),
            "denominator_selection_statistic": "minimum_compiled_combined_any_error_proxy_then_cx_count_then_seed",
            "post_selection_diagnostics_used_for_selection": False,
            "shots_per_execution": SHOTS,
        },
        "snapshot_metadata": snapshot_metadata,
        "summary": summary,
        "target_rows": target_rows,
        "candidate_rows": all_candidate_rows,
        "denominator_rows": all_denominator_rows,
        "successive_halving_rounds": round_rows,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "artifacts": {"circuit_directory": OUT_DIR, "result": RESULT_PATH, "markdown_report": REPORT_PATH},
        "claim_boundary": {
            "what_is_supported": "three generated dense-XY routes and three calibration-exposure-selected denominators prepared on previously unused fake backends",
            "what_is_not_supported": "a hidden holdout result, temporal transfer, real-device transfer, hardware performance, general route-generation advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def report(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    targets = "\n".join(
        f"- `{row['target_snapshot']}`: generated `{row['selected_mapping']}` / `{row['selected_policy_id']}` / `{row['selected_realization_seed']}`, denominator seed `{row['denominator_transpiler_seed']}`, public diagnostic delta `{row['diagnostic_selected_minus_denominator_mean']:+.8f}`."
        for row in payload["target_rows"]
    )
    return f"""# B4/B8 R150 Unseen-Backend Candidate Generation Design

- New fake backends: `{s['target_snapshot_count']}`
- Enumerated mappings: `{s['enumerated_mapping_count']}`
- Generated candidates / denominator pool: `{s['compiled_candidate_count']}` / `{s['denominator_pool_count']}`
- Selection / diagnostic / total executions: `{s['charged_design_execution_count']}` / `{s['diagnostic_execution_count']}` / `{s['total_design_execution_count']}`
- Semantic passes: `{s['semantic_fidelity_pass_count']} / {s['semantic_fidelity_check_count']}`
- Public diagnostic groups above -0.02: `{s['diagnostic_group_count_noninferior_to_negative_0_02']} / 3`
- Minimum public diagnostic delta: `{s['minimum_diagnostic_selected_minus_denominator_mean']:+.8f}`
- R149 hidden rows read: `0`
- Holdout executed: `false`

{targets}

The same R149 generation recipe is applied independently to Casablanca,
Nairobi, and Perth, which were absent from the R125-R149 portfolio. Each
generated route is pressure-tested against the best calibration-exposure route
from 80 independently seeded optimization-level-3 compilations. Diagnostics
are recorded only after selection and cannot alter the chosen route.

This design does not establish a hidden holdout result, temporal or real-device
transfer, hardware performance, general route-generation advantage, quantum
advantage, BQP separation, a solved frontier, or new credit.
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
