#!/usr/bin/env python3
"""Select foreign R143 routes using only public target calibration descriptors."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from qiskit import qasm3

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit, stable_hash
from b4_b8_r126_calibration_attribution_ledger import circuit_exposure, file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r132_topology_constrained_route_policy import compile_policy
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import exact_distribution, hellinger_fidelity
from b4_b8_r139_lagos_ising_channel_attribution import exact_compiled_classical_distribution


METHOD = "b4_b8_r147_target_descriptor_adaptation_design_v0"
R143_PATH = "results/B4_B8_R143_successive_halving_lcb_design_v0.json"
R146_PATH = "results/B4_B8_R146_cross_snapshot_transfer_holdout_v0.json"
R125_PATH = "results/B4_B8_R125_historical_snapshot_replay_v0.json"
TASK_BUILDER_PATH = "tools/b4_b8_r135_dense_interaction_fallback.py"
RESULT_PATH = "results/B4_B8_R147_target_descriptor_adaptation_design_v0.json"
REPORT_PATH = "research/B4_B8_R147_target_descriptor_adaptation_design.md"
OUT_DIR = "results/B4_B8_R147_target_descriptor_adaptation_design/candidates"


def candidate_key(row: dict[str, Any]) -> tuple[Any, ...]:
    """Parameter-free ordering fixed before any R147 challenge is run."""
    return (
        row["combined_any_error_proxy"],
        row["cx_any_error_proxy"],
        row["readout_any_error_proxy"],
        row["cx_occurrence_count"],
        row["source_snapshot"],
    )


def build(root: Path) -> dict[str, Any]:
    r143 = json.loads((root / R143_PATH).read_text())
    r125 = json.loads((root / R125_PATH).read_text())
    tasks = {task["task_id"]: task for task in build_dense_validation_tasks()}
    route_rows = {(row["snapshot"], row["task_id"]): row for row in r143["group_rows"]}
    snapshots = sorted({snapshot for snapshot, _ in route_rows})
    task_ids = sorted(tasks)
    output_dir = root / OUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    candidate_rows = []
    selection_rows = []
    for target_snapshot in snapshots:
        backend = SNAPSHOT_CLASSES[target_snapshot]()
        target_metadata = r125["snapshot_metadata"][target_snapshot]
        for task_id in task_ids:
            task = tasks[task_id]
            logical = basis_circuit(
                task["circuit"],
                tuple("Z" for _ in range(task["circuit"].num_qubits)),
            )
            ideal = exact_distribution(task["circuit"])
            group_candidates = []
            for source_snapshot in snapshots:
                if source_snapshot == target_snapshot:
                    continue
                route = route_rows[(source_snapshot, task_id)]
                compiled = compile_policy(
                    logical,
                    backend,
                    route["selected_mapping"],
                    route["selected_policy_id"],
                    route["selected_realization_seed"],
                )
                filename = f"{target_snapshot}__{task_id}__from_{source_snapshot}.qasm"
                path = output_dir / filename
                path.write_text(qasm3.dumps(compiled), encoding="utf-8")
                exposure = circuit_exposure(path, target_metadata)
                semantic = hellinger_fidelity(
                    ideal, exact_compiled_classical_distribution(compiled)
                )
                row = {
                    "adaptation_group_id": f"{target_snapshot}::{task_id}",
                    "target_snapshot": target_snapshot,
                    "task_id": task_id,
                    "source_snapshot": source_snapshot,
                    "source_mapping": route["selected_mapping"],
                    "source_policy_id": route["selected_policy_id"],
                    "source_realization_seed": route["selected_realization_seed"],
                    "candidate_circuit_path": str(path.relative_to(root)),
                    "candidate_circuit_sha256": file_sha256(path),
                    "candidate_qasm_stable_hash": stable_hash(qasm3.dumps(compiled)),
                    "semantic_fidelity": semantic,
                    "readout_any_error_proxy": exposure["readout_any_error_proxy"],
                    "cx_any_error_proxy": exposure["cx_any_error_proxy"],
                    "combined_any_error_proxy": exposure["combined_any_error_proxy"],
                    "cx_occurrence_count": exposure["cx_occurrence_count"],
                    "measurement_map": exposure["measurement_map"],
                    "unique_cx_edges": exposure["unique_cx_edges"],
                }
                candidate_rows.append(row)
                group_candidates.append(row)
            selected = min(group_candidates, key=candidate_key)
            selection_rows.append({
                "adaptation_group_id": selected["adaptation_group_id"],
                "target_snapshot": target_snapshot,
                "task_id": task_id,
                "candidate_count": len(group_candidates),
                "candidate_source_snapshots": sorted(row["source_snapshot"] for row in group_candidates),
                "target_specific_route_excluded_from_selector": True,
                "selected_source_snapshot": selected["source_snapshot"],
                "selected_mapping": selected["source_mapping"],
                "selected_policy_id": selected["source_policy_id"],
                "selected_realization_seed": selected["source_realization_seed"],
                "selected_circuit_path": selected["candidate_circuit_path"],
                "selected_circuit_sha256": selected["candidate_circuit_sha256"],
                "selected_qasm_stable_hash": selected["candidate_qasm_stable_hash"],
                "selected_semantic_fidelity": selected["semantic_fidelity"],
                "selected_readout_any_error_proxy": selected["readout_any_error_proxy"],
                "selected_cx_any_error_proxy": selected["cx_any_error_proxy"],
                "selected_combined_any_error_proxy": selected["combined_any_error_proxy"],
                "selection_key": list(candidate_key(selected)),
            })

    minimum_semantic = min(row["semantic_fidelity"] for row in candidate_rows)
    summary = {
        "snapshot_count": len(snapshots),
        "task_count": len(task_ids),
        "adaptation_group_count": len(selection_rows),
        "foreign_candidate_count": len(candidate_rows),
        "foreign_candidates_per_group": 2,
        "target_specific_routes_in_selector_count": 0,
        "r146_hidden_trial_rows_read_count": 0,
        "minimum_candidate_semantic_fidelity": minimum_semantic,
        "semantic_fidelity_pass_count": sum(row["semantic_fidelity"] >= 0.9999999999 for row in candidate_rows),
        "lagos_selected_source_counts": {
            source: sum(
                row["target_snapshot"] == "FakeLagosV2" and row["selected_source_snapshot"] == source
                for row in selection_rows
            )
            for source in snapshots
            if source != "FakeLagosV2"
        },
        "challenge_executed": False,
        "hardware_execution_claimed": False,
        "quantum_advantage_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        {"requirement_id": "R1", "label": "R143, R125, R146 provenance, and task-builder hashes are bound", "passed": True},
        {"requirement_id": "R2", "label": "three targets and four tasks produce 12 adaptation groups", "passed": len(selection_rows) == 12},
        {"requirement_id": "R3", "label": "exactly two foreign candidates are evaluated per group", "passed": len(candidate_rows) == 24 and all(row["candidate_count"] == 2 for row in selection_rows)},
        {"requirement_id": "R4", "label": "target-specific routes are excluded from every selector pool", "passed": all(row["target_specific_route_excluded_from_selector"] for row in selection_rows)},
        {"requirement_id": "R5", "label": "selection uses target-descriptor exposure with deterministic tie breaks", "passed": True},
        {"requirement_id": "R6", "label": "all 24 foreign candidates preserve semantic fidelity", "passed": summary["semantic_fidelity_pass_count"] == 24},
        {"requirement_id": "R7", "label": "R146 hidden trial rows are never read for selection or tuning", "passed": summary["r146_hidden_trial_rows_read_count"] == 0},
        {"requirement_id": "R8", "label": "no R147 holdout is executed during design", "passed": not summary["challenge_executed"]},
        {"requirement_id": "R9", "label": "all candidate QASM files and hashes are replayable", "passed": all(file_sha256(root / row["candidate_circuit_path"]) == row["candidate_circuit_sha256"] for row in candidate_rows)},
        {"requirement_id": "R10", "label": "hardware, advantage, solved-frontier, and credit claims remain false", "passed": not any([summary["hardware_execution_claimed"], summary["quantum_advantage_claimed"], summary["solved_frontier_claimed"], summary["new_credit_delta"]])},
    ]
    payload = {
        "title": "B4/B8 R147 target-descriptor foreign-route adaptation design",
        "version": 0,
        "method": METHOD,
        "status": "target_descriptor_adaptation_design_frozen_before_holdout",
        "model_status": "public_target_calibration_descriptor_selector_without_r146_row_reuse",
        "generated_at_unix": int(time.time()),
        "source_target_id": "T-B4-002bc/T-B8-003bg/T-B10-009au",
        "upstream_target_id": "T-B4-002bb/T-B8-003bf/T-B10-009at",
        "source_bindings": {
            "r143_design_path": R143_PATH,
            "r143_design_sha256": file_sha256(root / R143_PATH),
            "r143_design_payload_hash": r143["payload_hash"],
            "r125_snapshot_path": R125_PATH,
            "r125_snapshot_sha256": file_sha256(root / R125_PATH),
            "r125_snapshot_payload_hash": r125["payload_hash"],
            "r146_result_path": R146_PATH,
            "r146_result_sha256_provenance_only": file_sha256(root / R146_PATH),
            "r146_trial_rows_consumed": False,
            "task_builder_path": TASK_BUILDER_PATH,
            "task_builder_sha256": file_sha256(root / TASK_BUILDER_PATH),
        },
        "selector": {
            "candidate_pool": "the two foreign R143 routes for each target/task group",
            "target_descriptor_source": "R125 canonical target snapshot readout and CX calibration metadata",
            "primary_score": "compiled combined_any_error_proxy on the target snapshot",
            "tie_breaks": ["cx_any_error_proxy", "readout_any_error_proxy", "cx_occurrence_count", "source_snapshot"],
            "target_specific_route_used_for_selection": False,
            "r146_trial_rows_used_for_selection_or_tuning": False,
        },
        "summary": summary,
        "candidate_rows": candidate_rows,
        "selection_rows": selection_rows,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "artifacts": {"candidate_directory": OUT_DIR, "result": RESULT_PATH, "markdown_report": REPORT_PATH},
        "claim_boundary": {
            "what_is_supported": "a deterministic foreign-route selector based only on public target calibration descriptors",
            "what_is_not_supported": "holdout improvement, temporal transfer, cross-machine transfer, hardware execution, mitigation, soundness, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    selections = "\n".join(
        f"- `{row['target_snapshot']}` / `{row['task_id']}`: selected `{row['selected_source_snapshot']}`; combined/CX/readout proxies `{row['selected_combined_any_error_proxy']:.6f}` / `{row['selected_cx_any_error_proxy']:.6f}` / `{row['selected_readout_any_error_proxy']:.6f}`."
        for row in payload["selection_rows"]
    )
    return f"""# B4/B8 R147 Target-Descriptor Foreign-Route Adaptation Design

- Targets / tasks / adaptation groups: `{summary['snapshot_count']}` / `{summary['task_count']}` / `{summary['adaptation_group_count']}`
- Foreign candidates: `{summary['foreign_candidate_count']}` (`2` per group)
- Target-specific routes in selector: `{summary['target_specific_routes_in_selector_count']}`
- R146 hidden trial rows read: `{summary['r146_hidden_trial_rows_read_count']}`
- Candidate semantic passes: `{summary['semantic_fidelity_pass_count']} / 24`
- Holdout executed: `false`

## Frozen Selections

{selections}

## Method Boundary

For each target snapshot and dense task, the selector recompiles only the two
foreign R143 route identities on the target. It selects the lowest combined
readout-and-CX exposure proxy from public target calibration metadata, with
fixed deterministic tie breaks. The target-specific R143 route is excluded
from selection and reserved as a holdout denominator. No R146 trial row is
read or used for tuning.

This design does not support a holdout improvement, temporal or cross-machine
transfer, real hardware, mitigation, soundness, quantum advantage, BQP
separation, a solved frontier, or new credit.
"""


def main() -> int:
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
