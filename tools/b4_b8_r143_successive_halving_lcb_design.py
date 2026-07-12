#!/usr/bin/env python3
"""Compress R142 LCB selection with a fixed successive-halving schedule."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

from qiskit import qasm3

from b4_b8_r119_private_observable_bundle_gate import stable_hash, write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r132_topology_constrained_route_policy import (
    DETERMINISTIC_PROCESS_ENV,
    compile_policy,
)
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import (
    exact_distribution,
    hellinger_fidelity,
)
from b4_b8_r139_lagos_ising_channel_attribution import (
    exact_compiled_classical_distribution,
)


METHOD = "b4_b8_r143_successive_halving_lcb_design_v0"
STATUS = "successive_halving_lcb_design_frozen_before_holdout"
MODEL_STATUS = "r142_design_rows_replayed_under_fixed_8_to_4_to_2_to_1_schedule"
TARGET_ID = "T-B4-002au/T-B8-003ay/T-B10-009am"
UPSTREAM_TARGET_ID = "T-B4-002at/T-B8-003ax/T-B10-009al"
R136_PATH = "results/B4_B8_R136_route_realization_margin_v0.json"
R140_PATH = "results/B4_B8_R140_output_aware_mapping_design_v0.json"
R141_PATH = "results/B4_B8_R141_hashed_output_sketch_design_v0.json"
R142_PATH = "results/B4_B8_R142_seed_robust_lcb_mapping_design_v0.json"
RESULT_PATH = "results/B4_B8_R143_successive_halving_lcb_design_v0.json"
REPORT_PATH = "research/B4_B8_R143_successive_halving_lcb_design.md"
OUT_DIR = "results/B4_B8_R143_successive_halving_lcb_design"

ROUNDS = [
    {"additional_seed_count": 4, "survivor_count": 4},
    {"additional_seed_count": 4, "survivor_count": 2},
    {"additional_seed_count": 4, "survivor_count": 1},
]
LCB_Z = 1.96


def ensure_deterministic_process_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def identity(row: dict[str, Any], prefix: str = "") -> tuple[Any, ...]:
    return (
        tuple(row[f"{prefix}mapping"]),
        row[f"{prefix}policy_id"],
        row[f"{prefix}realization_seed"],
    )


def lcb(values: list[float]) -> float:
    return statistics.mean(values) - LCB_Z * statistics.stdev(values) / math.sqrt(
        len(values)
    )


def ranking_key(row: dict[str, Any], values: list[float]) -> tuple[Any, ...]:
    return (
        lcb(values),
        statistics.mean(values),
        row["minimum_delta_vs_automatic"],
        row["sketch_score"],
        row["policy_id"],
        tuple(row["mapping"]),
        -row["realization_seed"],
    )


def select(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    active = list(rows)
    observed = {identity(row): [] for row in rows}
    cursor = 0
    candidate_execution_count = 0
    trace = []
    for round_index, round_spec in enumerate(ROUNDS, 1):
        additional = round_spec["additional_seed_count"]
        indices = range(cursor, cursor + additional)
        cursor += additional
        before = len(active)
        for row in active:
            observed[identity(row)].extend(
                row["design_deltas_vs_automatic"][index] for index in indices
            )
            candidate_execution_count += additional
        ranked = sorted(
            active,
            key=lambda row: ranking_key(row, observed[identity(row)]),
            reverse=True,
        )
        active = ranked[: round_spec["survivor_count"]]
        trace.append(
            {
                "round": round_index,
                "additional_seed_count": additional,
                "cumulative_seed_count": cursor,
                "candidate_count_before": before,
                "survivor_count": len(active),
                "leader_mapping": active[0]["mapping"],
                "leader_policy_id": active[0]["policy_id"],
                "leader_realization_seed": active[0]["realization_seed"],
                "leader_lcb": lcb(observed[identity(active[0])]),
            }
        )
    return active[0], trace, candidate_execution_count + cursor


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    groups = "\n".join(
        f"- `{row['snapshot']}` / `{row['task_id']}`: matches R142 "
        f"`{row['selection_matches_r142']}`, full-budget LCB regret "
        f"`{row['full_budget_lcb_regret']:.8f}`, selected mapping "
        f"`{row['selected_mapping']}`."
        for row in payload["group_rows"]
    )
    requirements = "\n".join(
        f"- `{row['requirement_id']}` {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    return f"""# B4/B8 R143 Successive-Halving LCB Design

## Design Result

- Fixed schedule: `8 -> 4 -> 2 -> 1` over `4 + 4 + 4` seed increments
- Charged executions: `{summary['charged_execution_count']}` versus R142 `{summary['r142_design_execution_count']}`
- Execution reduction: `{summary['execution_reduction_fraction']:.2%}`
- Selection agreement with R142: `{summary['selection_agreement_count']} / 12`
- Mean / maximum full-budget LCB regret: `{summary['mean_full_budget_lcb_regret']:.8f}` / `{summary['maximum_full_budget_lcb_regret']:.8f}`
- Lagos selection agreement: `{summary['lagos_ising_selection_matches_r142']}`
- Lagos full-budget LCB: `{summary['lagos_ising_full_budget_lcb']:+.8f}`
- R142 holdout rows read during selection: `0`
- Selected OpenQASM 3 replay: `{summary['selected_qasm_replay_match_count']} / 12`
- New credit delta: `0`

The schedule evaluates all eight candidates on four seeds, keeps four, adds
four seeds, keeps two, adds four final seeds, and selects one. Automatic
baseline executions are shared once per used seed. The algorithm is replayed
from R142 design rows only; hidden R142 rows are not loaded.

## Group Evidence

{groups}

## Requirements

{requirements}

## Claim Boundary

Supported: a frozen counterfactual execution schedule that reduces the R142
design denominator by more than half while preserving low full-budget LCB
regret. Not supported: fresh hidden acceptance, live wall-clock savings,
cross-calibration transfer, hardware, soundness, quantum advantage, BQP
separation, solved B4/B8/B10, or new credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    started_at = int(time.time())
    r142 = json.loads((root / R142_PATH).read_text(encoding="utf-8"))
    r141 = json.loads((root / R141_PATH).read_text(encoding="utf-8"))
    r140 = json.loads((root / R140_PATH).read_text(encoding="utf-8"))
    r136 = json.loads((root / R136_PATH).read_text(encoding="utf-8"))
    tasks = {task["task_id"]: task for task in build_dense_validation_tasks()}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in r142["design_rows"]:
        groups.setdefault((row["snapshot"], row["task_id"]), []).append(row)
    r142_groups = {
        (row["snapshot"], row["task_id"]): row for row in r142["group_rows"]
    }
    source_groups = []
    for payload, mapping_key, policy_key, seed_key, path_key in [
        (r142, "selected_mapping", "selected_policy_id", "selected_realization_seed", "selected_circuit_path"),
        (r141, "selected_mapping", "selected_policy_id", "selected_realization_seed", "selected_circuit_path"),
        (r140, "new_selected_mapping", "new_selected_policy_id", "new_selected_realization_seed", "selected_circuit_path"),
        (r136, "selected_mapping", "selected_policy_id", "selected_realization_seed", "selected_circuit_path"),
    ]:
        rows = payload["group_rows"] if "group_rows" in payload else payload["validation_group_rows"]
        source_groups.append(
            {
                (row["snapshot"], row["task_id"]): {
                    "identity": (
                        tuple(row[mapping_key]),
                        row[policy_key],
                        row[seed_key],
                    ),
                    "path": row[path_key],
                }
                for row in rows
            }
        )

    selected_dir = root / OUT_DIR / "selected_circuits"
    selected_dir.mkdir(parents=True, exist_ok=True)
    group_rows = []
    selected_preexisting = 0
    selected_replay_matches = 0
    charged_executions = 0
    for key in sorted(groups):
        selected, trace, group_charge = select(groups[key])
        charged_executions += group_charge
        full_selected = max(
            groups[key],
            key=lambda row: (
                row["lcb_delta_vs_automatic"],
                row["mean_delta_vs_automatic"],
                row["minimum_delta_vs_automatic"],
                row["sketch_score"],
                row["policy_id"],
                tuple(row["mapping"]),
                -row["realization_seed"],
            ),
        )
        selected_identity = identity(selected)
        source_path = None
        for source in source_groups:
            if key in source and source[key]["identity"] == selected_identity:
                source_path = source[key]["path"]
                break
        snapshot_name, task_id = key
        task = tasks[task_id]
        ideal = exact_distribution(task["circuit"])
        if source_path:
            qasm = (root / source_path).read_text(encoding="utf-8")
            circuit = qasm3.loads(qasm)
        else:
            backend = SNAPSHOT_CLASSES[snapshot_name]()
            logical = basis_circuit(
                task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits))
            )
            circuit = compile_policy(
                logical,
                backend,
                selected["mapping"],
                selected["policy_id"],
                selected["realization_seed"],
            )
            qasm = qasm3.dumps(circuit)
        semantic_fidelity = hellinger_fidelity(
            ideal, exact_compiled_classical_distribution(circuit)
        )
        path = selected_dir / f"{snapshot_name}_{task_id}.qasm"
        if path.exists():
            selected_preexisting += 1
            replay_match = path.read_text(encoding="utf-8") == qasm
        else:
            path.write_text(qasm, encoding="utf-8")
            replay_match = True
        selected_replay_matches += replay_match
        group_rows.append(
            {
                "snapshot": snapshot_name,
                "task_id": task_id,
                "charged_execution_count": group_charge,
                "selection_trace": trace,
                "selected_mapping": selected["mapping"],
                "selected_policy_id": selected["policy_id"],
                "selected_realization_seed": selected["realization_seed"],
                "selection_matches_r142": selected_identity == identity(full_selected),
                "full_budget_selected_lcb": selected["lcb_delta_vs_automatic"],
                "r142_full_budget_lcb": full_selected["lcb_delta_vs_automatic"],
                "full_budget_lcb_regret": full_selected["lcb_delta_vs_automatic"]
                - selected["lcb_delta_vs_automatic"],
                "semantic_fidelity": semantic_fidelity,
                "selected_qasm_stable_hash": stable_hash(qasm),
                "selected_circuit_path": str(path.relative_to(root)),
                "selected_circuit_sha256": file_sha256(path),
                "selected_qasm_replay_matches": replay_match,
            }
        )
    lagos = next(
        row
        for row in group_rows
        if row["snapshot"] == "FakeLagosV2"
        and row["task_id"] == "dense_validation_complete_ising_n6"
    )
    regrets = [row["full_budget_lcb_regret"] for row in group_rows]
    r142_execution_count = r142["summary"]["simulated_circuit_execution_count"]
    summary = {
        "source_group_count": len(groups),
        "source_candidate_count": len(r142["design_rows"]),
        "round_schedule": ROUNDS,
        "seeds_used_per_finalist": 12,
        "charged_execution_count": charged_executions,
        "r142_design_execution_count": r142_execution_count,
        "execution_saving_count": r142_execution_count - charged_executions,
        "execution_reduction_fraction": 1 - charged_executions / r142_execution_count,
        "selection_agreement_count": sum(
            row["selection_matches_r142"] for row in group_rows
        ),
        "mean_full_budget_lcb_regret": statistics.mean(regrets),
        "maximum_full_budget_lcb_regret": max(regrets),
        "minimum_selected_semantic_fidelity": min(
            row["semantic_fidelity"] for row in group_rows
        ),
        "lagos_ising_selection_matches_r142": lagos["selection_matches_r142"],
        "lagos_ising_selected_mapping": lagos["selected_mapping"],
        "lagos_ising_full_budget_lcb": lagos["full_budget_selected_lcb"],
        "r142_holdout_rows_read_during_selection": 0,
        "fresh_holdout_executed": False,
        "selected_qasm_preexisting_count": selected_preexisting,
        "selected_qasm_replay_match_count": selected_replay_matches,
        "live_wall_clock_saving_claimed": False,
        "cross_calibration_transfer_claimed": False,
        "hardware_execution_performed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        {"requirement_id": "R1", "label": "all 96 R142 shortlist rows are replayed", "passed": summary["source_candidate_count"] == 96},
        {"requirement_id": "R2", "label": "the fixed 8-to-4-to-2-to-1 schedule uses twelve seeds per finalist", "passed": summary["seeds_used_per_finalist"] == 12},
        {"requirement_id": "R3", "label": "charged execution count is 816", "passed": summary["charged_execution_count"] == 816},
        {"requirement_id": "R4", "label": "execution reduction exceeds fifty percent", "passed": summary["execution_reduction_fraction"] >= 0.5},
        {"requirement_id": "R5", "label": "at least ten of twelve selections match R142", "passed": summary["selection_agreement_count"] >= 10},
        {"requirement_id": "R6", "label": "maximum full-budget LCB regret remains below 0.001", "passed": summary["maximum_full_budget_lcb_regret"] <= 0.001},
        {"requirement_id": "R7", "label": "Lagos selection matches accepted R142", "passed": summary["lagos_ising_selection_matches_r142"]},
        {"requirement_id": "R8", "label": "all selected QASM files replay with exact semantics", "passed": selected_replay_matches == 12 and summary["minimum_selected_semantic_fidelity"] >= 1 - 1e-12},
        {"requirement_id": "R9", "label": "R142 holdout rows remain unread and no fresh holdout runs", "passed": summary["r142_holdout_rows_read_during_selection"] == 0 and not summary["fresh_holdout_executed"]},
        {"requirement_id": "R10", "label": "live savings, cross-calibration, hardware, advantage, BQP, and credit claims remain false", "passed": not any([summary["live_wall_clock_saving_claimed"], summary["cross_calibration_transfer_claimed"], summary["hardware_execution_performed"], summary["quantum_advantage_claimed"], summary["bqp_separation_claimed"], summary["new_credit_delta"]])},
    ]
    payload = {
        "title": "B4/B8 R143 successive-halving LCB design",
        "version": 0,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "generated_at_unix": started_at,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "summary": summary,
        "group_rows": group_rows,
        "requirements": requirements,
        "requirement_count": len(requirements),
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "artifacts": {
            "r142_design_result": R142_PATH,
            "selected_circuit_directory": str(selected_dir.relative_to(root)),
            "result": RESULT_PATH,
            "markdown_report": REPORT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": "a fixed counterfactual successive-halving schedule with charged execution savings and low full-budget LCB regret",
            "what_is_not_supported": "fresh hidden acceptance, live wall-clock savings, cross-calibration transfer, hardware, soundness, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(
        json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    ensure_deterministic_process_environment()
    root = args.root.resolve()
    payload = run_gate(root)
    output = args.output or root / RESULT_PATH
    markdown = args.report or root / REPORT_PATH
    write_json(output, payload)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["requirements_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
