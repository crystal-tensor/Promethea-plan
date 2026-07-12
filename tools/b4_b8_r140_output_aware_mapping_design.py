#!/usr/bin/env python3
"""Design a parameter-free output-aware mapping score over the R136 portfolio."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from qiskit import qasm3
from qiskit_aer.noise import NoiseModel

from b4_b8_r119_private_observable_bundle_gate import stable_hash, write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r128_transpiler_loop_layout_ranking import exposure_from_qasm, package_version
from b4_b8_r132_topology_constrained_route_policy import (
    DETERMINISTIC_PROCESS_ENV,
    compile_policy,
)
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import exact_distribution, hellinger_fidelity
from b4_b8_r139_lagos_ising_channel_attribution import (
    apply_symmetric_readout_channel,
    exact_compiled_classical_distribution,
    measurement_map,
    readout_errors,
)


METHOD = "b4_b8_r140_output_aware_mapping_design_v0"
STATUS = "output_aware_parameter_free_mapping_design_frozen_before_holdout"
MODEL_STATUS = "r136_portfolio_reranked_without_r138_or_r139_validation_outcomes"
TARGET_ID = "T-B4-002ao/T-B8-003as/T-B10-009ag"
UPSTREAM_TARGET_ID = "T-B4-002an/T-B8-003ar/T-B10-009af"
R125_RESULT_PATH = "results/B4_B8_R125_historical_snapshot_replay_v0.json"
R136_RESULT_PATH = "results/B4_B8_R136_route_realization_margin_v0.json"
RESULT_PATH = "results/B4_B8_R140_output_aware_mapping_design_v0.json"
REPORT_PATH = "research/B4_B8_R140_output_aware_mapping_design.md"
OUT_DIR = "results/B4_B8_R140_output_aware_mapping_design"


def ensure_deterministic_process_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    groups = "\n".join(
        f"- `{row['snapshot']}` / `{row['task_id']}`: old/new exact-readout "
        f"`{row['old_selected_exact_readout_fidelity']:.8f}` / "
        f"`{row['new_selected_exact_readout_fidelity']:.8f}`, old/new CX-any-error "
        f"`{row['old_selected_cx_any_error_proxy']:.8f}` / "
        f"`{row['new_selected_cx_any_error_proxy']:.8f}`, score improvement "
        f"`{row['score_improvement']:+.8f}`, changed `{row['selection_changed']}`."
        for row in payload["group_rows"]
    )
    requirements = "\n".join(
        f"- `{row['requirement_id']}` {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    return f"""# B4/B8 R140 Output-Aware Mapping Design

## Design Result

- R136 candidates replayed: `{summary['candidate_count']}`
- Candidate QASM hashes matched: `{summary['candidate_qasm_hash_match_count']}`
- Backend/task groups: `{summary['group_count']}`
- Changed selections: `{summary['changed_selection_count']}`
- Groups with improved output-aware score: `{summary['groups_with_score_improvement']}`
- Groups with improved exact readout fidelity: `{summary['groups_with_exact_readout_improvement']}`
- Minimum selected exact semantic fidelity: `{summary['minimum_selected_exact_semantic_fidelity']:.16f}`
- Frozen selected QASM replay: `{summary['selected_qasm_replay_match_count']}` / `12`
- R138/R139 validation rows read during selection: `0`
- New credit delta: `0`

The parameter-free score is

`(1 - cx_any_error_proxy) * exact_output_aware_readout_fidelity`.

The first factor uses the historical compiled CX route. The second factor
applies the physical readout channel induced by the candidate measurement map
to the exact logical output distribution. There is no fitted weight. R138 and
R139 are used only to motivate the score and define the later falsification
target; their validation rows are not loaded by this design program.

## Group Selection Evidence

{groups}

## Requirements

{requirements}

## Claim Boundary

Supported: a frozen, replayable, parameter-free output-aware reranking of the
1,536 R136 route realizations. Not supported: noisy validation acceptance,
Lagos repair, scalable exact-output estimation, current calibration, hardware,
mitigation, protocol soundness, quantum advantage, BQP separation, or new B10
credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    r136_path = root / R136_RESULT_PATH
    r136 = json.loads(r136_path.read_text(encoding="utf-8"))
    if r136.get("status") != "route_realization_lower_tail_margin_boundary":
        raise ValueError("R140 design requires the R136 route-realization portfolio")
    r125 = json.loads((root / R125_RESULT_PATH).read_text(encoding="utf-8"))
    tasks = {task["task_id"]: task for task in build_dense_validation_tasks()}
    old_groups = {
        (row["snapshot"], row["task_id"]): row
        for row in r136["validation_group_rows"]
    }
    source_rows_by_group: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in r136["route_realization_rows"]:
        key = (row["snapshot"], row["task_id"])
        source_rows_by_group.setdefault(key, []).append(row)
    if len(source_rows_by_group) != 12 or any(
        len(rows) != 128 for rows in source_rows_by_group.values()
    ):
        raise ValueError("R140 design requires 12 complete 128-candidate groups")

    output = root / OUT_DIR
    selected_dir = output / "selected_circuits"
    selected_dir.mkdir(parents=True, exist_ok=True)
    candidate_rows: list[dict[str, Any]] = []
    group_rows: list[dict[str, Any]] = []
    selected_paths: list[str] = []
    qasm_hash_matches = 0
    selected_preexisting = 0
    selected_replay_matches = 0

    with tempfile.TemporaryDirectory(prefix="r140-design-") as temporary:
        scratch = Path(temporary) / "compiled.qasm"
        for key in sorted(source_rows_by_group):
            snapshot_name, task_id = key
            backend = SNAPSHOT_CLASSES[snapshot_name]()
            metadata = r125["snapshot_metadata"][snapshot_name]
            task = tasks[task_id]
            representative = basis_circuit(
                task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits))
            )
            ideal = exact_distribution(task["circuit"])
            physical_readout_errors = readout_errors(
                NoiseModel.from_backend(backend).to_dict()
            )
            compiled_candidates = []
            for source_row in source_rows_by_group[key]:
                compiled = compile_policy(
                    representative,
                    backend,
                    source_row["mapping"],
                    source_row["policy_id"],
                    source_row["realization_seed"],
                )
                qasm = qasm3.dumps(compiled)
                qasm_hash_match = stable_hash(qasm) == source_row["qasm_hash"]
                qasm_hash_matches += qasm_hash_match
                exposure = exposure_from_qasm(qasm, metadata, scratch)
                mapping = measurement_map(compiled)
                readout_error_vector = [
                    physical_readout_errors[mapping[index]]
                    for index in range(task["circuit"].num_qubits)
                ]
                distorted = apply_symmetric_readout_channel(
                    ideal, readout_error_vector
                )
                exact_readout_fidelity = hellinger_fidelity(ideal, distorted)
                cx_success_proxy = 1.0 - exposure["cx_any_error_proxy"]
                score = cx_success_proxy * exact_readout_fidelity
                row = {
                    "snapshot": snapshot_name,
                    "task_id": task_id,
                    "mapping": source_row["mapping"],
                    "policy_id": source_row["policy_id"],
                    "realization_seed": source_row["realization_seed"],
                    "r135_candidate_rank": source_row["r135_candidate_rank"],
                    "qasm_hash": source_row["qasm_hash"],
                    "qasm_hash_matches_r136": qasm_hash_match,
                    "measurement_map": mapping,
                    "readout_error_vector": readout_error_vector,
                    "cx_occurrence_count": exposure["cx_occurrence_count"],
                    "cx_any_error_proxy": exposure["cx_any_error_proxy"],
                    "combined_any_error_proxy": exposure[
                        "combined_any_error_proxy"
                    ],
                    "exact_output_aware_readout_fidelity": exact_readout_fidelity,
                    "cx_success_proxy": cx_success_proxy,
                    "output_aware_product_score": score,
                }
                candidate_rows.append(row)
                compiled_candidates.append((row, qasm, compiled))
            selected_row, selected_qasm, selected_circuit = max(
                compiled_candidates,
                key=lambda item: (
                    item[0]["output_aware_product_score"],
                    item[0]["exact_output_aware_readout_fidelity"],
                    -item[0]["cx_any_error_proxy"],
                    -item[0]["cx_occurrence_count"],
                    item[0]["policy_id"],
                    tuple(item[0]["mapping"]),
                    -item[0]["realization_seed"],
                ),
            )
            selected_path = selected_dir / f"{snapshot_name}_{task_id}.qasm"
            relative_path = str(selected_path.relative_to(root))
            selected_paths.append(relative_path)
            if selected_path.exists():
                selected_preexisting += 1
                replay_match = selected_path.read_text(encoding="utf-8") == selected_qasm
            else:
                selected_path.write_text(selected_qasm, encoding="utf-8")
                replay_match = True
            selected_replay_matches += replay_match

            old = old_groups[key]
            old_candidate = next(
                row
                for row in candidate_rows
                if row["snapshot"] == snapshot_name
                and row["task_id"] == task_id
                and row["mapping"] == old["selected_mapping"]
                and row["policy_id"] == old["selected_policy_id"]
                and row["realization_seed"] == old["selected_realization_seed"]
            )
            selected_exact = exact_compiled_classical_distribution(selected_circuit)
            semantic_fidelity = hellinger_fidelity(ideal, selected_exact)
            group_rows.append(
                {
                    "snapshot": snapshot_name,
                    "task_id": task_id,
                    "candidate_count": len(compiled_candidates),
                    "old_selected_mapping": old["selected_mapping"],
                    "old_selected_policy_id": old["selected_policy_id"],
                    "old_selected_realization_seed": old[
                        "selected_realization_seed"
                    ],
                    "old_selected_output_aware_score": old_candidate[
                        "output_aware_product_score"
                    ],
                    "old_selected_exact_readout_fidelity": old_candidate[
                        "exact_output_aware_readout_fidelity"
                    ],
                    "old_selected_cx_any_error_proxy": old_candidate[
                        "cx_any_error_proxy"
                    ],
                    "new_selected_mapping": selected_row["mapping"],
                    "new_selected_policy_id": selected_row["policy_id"],
                    "new_selected_realization_seed": selected_row[
                        "realization_seed"
                    ],
                    "new_selected_output_aware_score": selected_row[
                        "output_aware_product_score"
                    ],
                    "new_selected_exact_readout_fidelity": selected_row[
                        "exact_output_aware_readout_fidelity"
                    ],
                    "new_selected_cx_any_error_proxy": selected_row[
                        "cx_any_error_proxy"
                    ],
                    "score_improvement": selected_row[
                        "output_aware_product_score"
                    ]
                    - old_candidate["output_aware_product_score"],
                    "exact_readout_improvement": selected_row[
                        "exact_output_aware_readout_fidelity"
                    ]
                    - old_candidate["exact_output_aware_readout_fidelity"],
                    "cx_any_error_change": selected_row["cx_any_error_proxy"]
                    - old_candidate["cx_any_error_proxy"],
                    "selection_changed": (
                        selected_row["mapping"] != old["selected_mapping"]
                        or selected_row["policy_id"] != old["selected_policy_id"]
                        or selected_row["realization_seed"]
                        != old["selected_realization_seed"]
                    ),
                    "selected_exact_semantic_fidelity": semantic_fidelity,
                    "selected_circuit_path": relative_path,
                    "selected_circuit_sha256": file_sha256(selected_path),
                    "selected_qasm_replay_matches": replay_match,
                }
            )

    lagos_ising = next(
        row
        for row in group_rows
        if row["snapshot"] == "FakeLagosV2"
        and row["task_id"] == "dense_validation_complete_ising_n6"
    )
    summary = {
        "candidate_count": len(candidate_rows),
        "candidate_qasm_hash_match_count": qasm_hash_matches,
        "group_count": len(group_rows),
        "candidates_per_group": 128,
        "score_formula": "(1-cx_any_error_proxy)*exact_output_aware_readout_fidelity",
        "fitted_weight_count": 0,
        "changed_selection_count": sum(row["selection_changed"] for row in group_rows),
        "groups_with_score_improvement": sum(
            row["score_improvement"] > 1e-15 for row in group_rows
        ),
        "groups_with_exact_readout_improvement": sum(
            row["exact_readout_improvement"] > 1e-15 for row in group_rows
        ),
        "minimum_selected_exact_semantic_fidelity": min(
            row["selected_exact_semantic_fidelity"] for row in group_rows
        ),
        "selected_qasm_preexisting_count": selected_preexisting,
        "selected_qasm_replay_match_count": selected_replay_matches,
        "lagos_ising_selection_changed": lagos_ising["selection_changed"],
        "lagos_ising_exact_readout_improvement": lagos_ising[
            "exact_readout_improvement"
        ],
        "lagos_ising_score_improvement": lagos_ising["score_improvement"],
        "r138_validation_rows_read_during_selection": 0,
        "r139_channel_rows_read_during_selection": 0,
        "noisy_holdout_executed": False,
        "current_backend_calibration_used": False,
        "hardware_execution_performed": False,
        "mapping_repair_claimed": False,
        "protocol_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        ("P1", "R136 result and all 1,536 route realizations are hash-bound", r136["source_target_id"] == "T-B4-002ak/T-B8-003ao/T-B10-009ac" and len(candidate_rows) == 1536),
        ("P2", "all 1,536 candidate QASM programs replay their R136 hashes", qasm_hash_matches == 1536),
        ("P3", "the score has no fitted weight and uses only CX and exact readout terms", summary["fitted_weight_count"] == 0 and summary["score_formula"] == "(1-cx_any_error_proxy)*exact_output_aware_readout_fidelity"),
        ("P4", "R138 and R139 validation outcomes are not loaded during selection", summary["r138_validation_rows_read_during_selection"] == 0 and summary["r139_channel_rows_read_during_selection"] == 0),
        ("P5", "all 12 groups expose 128 candidates and one frozen selection", len(group_rows) == 12 and all(row["candidate_count"] == 128 for row in group_rows)),
        ("P6", "all frozen selections preserve the exact logical output distribution", summary["minimum_selected_exact_semantic_fidelity"] >= 1.0 - 1e-12),
        ("P7", "the output-aware objective changes the Lagos complete-Ising selection", summary["lagos_ising_selection_changed"] and summary["lagos_ising_exact_readout_improvement"] > 0),
        ("P8", "all 12 selected QASM files replay in a fresh process", selected_preexisting == 12 and selected_replay_matches == 12),
        ("P9", "no noisy holdout or current calibration is consumed during design", not summary["noisy_holdout_executed"] and not summary["current_backend_calibration_used"]),
        ("P10", "repair, hardware, soundness, advantage, BQP, and credit remain unclaimed", not summary["mapping_repair_claimed"] and not summary["hardware_execution_performed"] and not summary["protocol_soundness_claimed"] and not summary["quantum_advantage_claimed"] and not summary["bqp_separation_claimed"] and summary["new_credit_delta"] == 0),
    ]
    requirement_rows = [
        {"requirement_id": identifier, "label": label, "passed": passed}
        for identifier, label, passed in requirements
    ]
    failed = [row["requirement_id"] for row in requirement_rows if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R140 output-aware mapping design",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "requirements": requirement_rows,
        "requirement_count": len(requirement_rows),
        "requirements_passed": len(requirement_rows) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "summary": summary,
        "group_rows": group_rows,
        "candidate_rows": candidate_rows,
        "artifacts": {
            "r136_result": R136_RESULT_PATH,
            "selected_circuits": sorted(selected_paths),
        },
        "environment": {
            "deterministic_process_environment": DETERMINISTIC_PROCESS_ENV,
            "qiskit": package_version("qiskit"),
            "qiskit_aer": package_version("qiskit-aer"),
        },
        "claim_boundary": {
            "what_is_supported": "A frozen, replayable, parameter-free output-aware reranking of the 1,536 R136 route realizations.",
            "what_is_not_supported": "Noisy validation acceptance, Lagos repair, scalable exact-output estimation, current calibration, hardware, mitigation, protocol soundness, quantum advantage, BQP separation, or new B10 credit.",
            "next_gate": "Publish the 12 selected QASM hashes and immutable cross-group holdout contract before generating fresh hidden validation seeds.",
        },
    }
    payload["payload_hash"] = stable_hash(payload)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    return payload


def main() -> None:
    ensure_deterministic_process_environment()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    payload = run_gate(args.root)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
