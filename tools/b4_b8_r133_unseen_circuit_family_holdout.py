#!/usr/bin/env python3
"""T-B4-002ah/T-B8-003al: stress R132 on unseen circuit families."""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, qasm3, transpile

from b4_b8_r121_private_bundle_shot_sweep import basis_circuit, stable_hash, write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r128_transpiler_loop_layout_ranking import exposure_from_qasm, package_version
from b4_b8_r131_compiled_route_family_attribution import compiled_route_descriptor
from b4_b8_r132_topology_constrained_route_policy import (
    DETERMINISTIC_PROCESS_ENV,
    compile_policy,
)


METHOD = "b4_b8_r133_unseen_circuit_family_holdout_v0"
STATUS = "unseen_circuit_family_route_holdout_boundary"
MODEL_STATUS = "deterministic_route_generalizes_but_automatic_baseline_no_loss_gate_fails"
TARGET_ID = "T-B4-002ah/T-B8-003al/T-B10-009z"
UPSTREAM_TARGET_ID = "T-B4-002ag/T-B8-003ak/T-B10-009y"
R119_RESULT_PATH = "results/B4_B8_R119_private_observable_bundle_v0.json"
R125_RESULT_PATH = "results/B4_B8_R125_historical_snapshot_replay_v0.json"
R130_RESULT_PATH = "results/B4_B8_R130_route_signature_candidate_expansion_v0.json"
R132_RESULT_PATH = "results/B4_B8_R132_topology_constrained_route_policy_v0.json"
RESULT_PATH = "results/B4_B8_R133_unseen_circuit_family_holdout_v0.json"
REPORT_PATH = "research/B4_B8_R133_unseen_circuit_family_holdout.md"
OUT_DIR = "results/B4_B8_R133_unseen_circuit_family_holdout"
HOLDOUT_SEEDS = tuple(range(13351, 13361))
SELECTED_POLICY_ID = "selected_o3_lookahead"
TOLERANCE = 1e-15


def ensure_deterministic_process_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def build_holdout_tasks() -> list[dict[str, Any]]:
    ghz_echo = QuantumCircuit(6)
    ghz_echo.h(0)
    for target in [5, 4, 3, 2, 1]:
        ghz_echo.cx(0, target)
    for target in range(1, 6):
        ghz_echo.rz(math.pi * (target + 1) / 7, target)
    for target in [1, 2, 3, 4, 5]:
        ghz_echo.cx(0, target)
    ghz_echo.ry(math.pi / 5, 0)
    for target in [5, 4, 3, 2, 1]:
        ghz_echo.cx(0, target)

    star_phase = QuantumCircuit(6)
    star_phase.h(0)
    for target in range(1, 6):
        star_phase.cz(0, target)
    for target in range(6):
        star_phase.rx(math.pi * (target + 2) / 11, target)
    for target in [2, 4, 1, 5, 3]:
        star_phase.cz(0, target)

    ring_phase = QuantumCircuit(6)
    for target in range(6):
        ring_phase.h(target)
    ring_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
    for left, right in ring_edges:
        ring_phase.cz(left, right)
    for target in range(6):
        ring_phase.rx(math.pi * (target + 1) / 13, target)
    for left, right in reversed(ring_edges):
        ring_phase.cz(left, right)

    brickwork = QuantumCircuit(6)
    for target in range(6):
        brickwork.h(target)
    for left, right in [(0, 1), (2, 3), (4, 5)]:
        brickwork.cx(left, right)
    for target in range(6):
        brickwork.ry(math.pi * (target + 1) / 9, target)
    for left, right in [(1, 2), (3, 4)]:
        brickwork.cx(left, right)
    for target in range(6):
        brickwork.rz(math.pi * (target + 2) / 15, target)
    for left, right in [(0, 1), (2, 3), (4, 5)]:
        brickwork.cx(left, right)

    return [
        {
            "task_id": "holdout_ghz_echo_n6",
            "mapping_source_task_id": "private_bundle_ghz_n6",
            "family": "star_echo",
            "circuit": ghz_echo,
        },
        {
            "task_id": "holdout_star_phase_n6",
            "mapping_source_task_id": "private_bundle_ghz_n6",
            "family": "star_phase",
            "circuit": star_phase,
        },
        {
            "task_id": "holdout_ring_phase_n6",
            "mapping_source_task_id": "private_bundle_graph_n6",
            "family": "ring_phase",
            "circuit": ring_phase,
        },
        {
            "task_id": "holdout_brickwork_n6",
            "mapping_source_task_id": "private_bundle_graph_n6",
            "family": "brickwork",
            "circuit": brickwork,
        },
    ]


def outcome(delta: float) -> str:
    return "win" if delta > TOLERANCE else "loss" if delta < -TOLERANCE else "tie"


def loss_attribution(
    constrained_gain_vs_automatic: float,
    fixed_mapping_gain_vs_automatic: float,
    lookahead_gain_vs_fixed_default: float,
) -> str:
    if constrained_gain_vs_automatic >= -TOLERANCE:
        return "no_constrained_loss"
    if fixed_mapping_gain_vs_automatic < -TOLERANCE:
        if lookahead_gain_vs_fixed_default >= -TOLERANCE:
            return "fixed_mapping_gap_not_recovered"
        return "fixed_mapping_and_policy_regression"
    return "lookahead_policy_induced_loss"


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    group_lines = []
    for row in payload["holdout_group_rows"]:
        group_lines.append(
            "- `{snapshot}` / `{task}`: route/QASM classes `{routes}/{qasm}`; "
            "mean gain vs automatic `{gain:+.6f}`; wins/ties/losses "
            "`{wins}/{ties}/{losses}`; mapping-gap/policy-induced losses "
            "`{mapping}/{policy}`.".format(
                snapshot=row["snapshot"],
                task=row["task_id"],
                routes=row["constrained_unique_route_family_count"],
                qasm=row["constrained_unique_qasm_hash_count"],
                gain=row["mean_constrained_gain_vs_automatic_default"],
                wins=row["win_count_vs_automatic_default"],
                ties=row["tie_count_vs_automatic_default"],
                losses=row["loss_count_vs_automatic_default"],
                mapping=row["fixed_mapping_gap_not_recovered_count"],
                policy=row["lookahead_policy_induced_loss_count"],
            )
        )
    requirements = "\n".join(
        f"- `{row['requirement_id']}` {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    return f"""# B4/B8 R133 Unseen Circuit-Family Holdout

## Result

- Unseen source circuits: `{summary['holdout_task_count']}`
- Backend/circuit groups: `{summary['holdout_group_count']}`
- Holdout compilations: `{summary['holdout_compilation_count']}`
- Groups with one route-exposure class: `{summary['route_family_invariant_group_count']}` / `12`
- Groups with one exact QASM hash: `{summary['exact_qasm_seed_invariant_group_count']}` / `12`
- Frozen constrained-QASM replay: `{summary['frozen_qasm_replay_match_count']}` / `120`
- Wins/ties/losses vs automatic layout: `{summary['win_count_vs_automatic_default']}/{summary['tie_count_vs_automatic_default']}/{summary['loss_count_vs_automatic_default']}`
- Groups with no automatic-baseline loss: `{summary['no_loss_group_count_vs_automatic_default']}` / `12`
- Fixed-mapping-gap losses: `{summary['fixed_mapping_gap_not_recovered_count']}`
- Lookahead-policy-induced losses: `{summary['lookahead_policy_induced_loss_count']}`
- Deterministic generalization gate passed: `{summary['deterministic_generalization_gate_passed']}`
- Automatic-baseline no-loss gate passed: `{summary['automatic_baseline_no_loss_gate_passed']}`
- New credit delta: `0`

## Holdout Evidence

{chr(10).join(group_lines)}

R133 freezes four circuit families that were absent from R119-R132: star echo,
star phase, ring phase, and brickwork. It reuses only the already-selected R130
mapping associated with the parent star or path family and the already-selected
R132 `lookahead` policy. No policy or mapping is selected from these holdout rows.

Determinism generalizes, but baseline quality does not. The attribution ledger
compares the constrained route with both the same fixed mapping under Qiskit's
default router and the fully automatic layout, separating inherited mapping gaps
from losses introduced by the `lookahead` policy.

## Requirements

{requirements}

## Claim Boundary

Supported: unseen circuit-family evidence that the R132 route policy remains
byte-reproducible while failing the automatic-layout no-loss criterion, with a
per-seed mapping-versus-policy loss attribution. Not supported: verifier
acceptance, causal hardware performance, current calibration, mitigation,
protocol soundness, quantum advantage, BQP separation, or new B10 credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    r119_path = root / R119_RESULT_PATH
    r125_path = root / R125_RESULT_PATH
    r130_path = root / R130_RESULT_PATH
    r132_path = root / R132_RESULT_PATH
    r119 = json.loads(r119_path.read_text(encoding="utf-8"))
    r125 = json.loads(r125_path.read_text(encoding="utf-8"))
    r130 = json.loads(r130_path.read_text(encoding="utf-8"))
    r132 = json.loads(r132_path.read_text(encoding="utf-8"))
    if r132.get("status") != "topology_constrained_route_policy_boundary":
        raise ValueError("R133 requires the R132 topology-constrained boundary")
    if r132["summary"].get("selected_policy_id") != SELECTED_POLICY_ID:
        raise ValueError("R133 requires the exact R132 selected policy")
    prior_seeds = set(
        r130["summary"]["training_seeds"]
        + r130["summary"]["validation_seeds"]
        + r132["summary"]["training_seeds"]
        + r132["summary"]["validation_seeds"]
    )
    if prior_seeds & set(HOLDOUT_SEEDS):
        raise ValueError("R133 seeds must be disjoint from R130 and R132")

    mapping_by_group = {
        (row["snapshot"], row["task_id"]): row["selected_mapping"]
        for row in r130["selected_layout_rows"]
    }
    output = root / OUT_DIR
    source_dir = output / "source_circuits"
    constrained_dir = output / "constrained_circuits"
    source_dir.mkdir(parents=True, exist_ok=True)
    constrained_dir.mkdir(parents=True, exist_ok=True)
    prior_source_hashes = {
        file_sha256(root / path) for path in r119.get("artifacts", {}).get("circuits", [])
    }
    tasks = build_holdout_tasks()
    source_rows = []
    holdout_rows = []
    frozen_paths = []
    frozen_preexisting_count = 0
    frozen_match_count = 0

    with tempfile.TemporaryDirectory(prefix="r133-") as temporary:
        scratch = Path(temporary) / "compiled.qasm"
        for task in tasks:
            source_path = source_dir / f"{task['task_id']}.qasm"
            source_qasm = qasm3.dumps(task["circuit"])
            source_path.write_text(source_qasm, encoding="utf-8")
            source_hash = file_sha256(source_path)
            source_rows.append(
                {
                    "task_id": task["task_id"],
                    "family": task["family"],
                    "mapping_source_task_id": task["mapping_source_task_id"],
                    "source_circuit_path": str(source_path.relative_to(root)),
                    "source_circuit_sha256": source_hash,
                    "unseen_vs_r119_source_circuits": source_hash not in prior_source_hashes,
                }
            )
            representative = basis_circuit(
                task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits))
            )
            for snapshot_name in sorted(SNAPSHOT_CLASSES):
                backend = SNAPSHOT_CLASSES[snapshot_name]()
                metadata = r125["snapshot_metadata"][snapshot_name]
                mapping = mapping_by_group[
                    (snapshot_name, task["mapping_source_task_id"])
                ]
                for seed in HOLDOUT_SEEDS:
                    constrained = compile_policy(
                        representative,
                        backend,
                        mapping,
                        SELECTED_POLICY_ID,
                        seed,
                    )
                    fixed_default = compile_policy(
                        representative,
                        backend,
                        mapping,
                        "selected_o3_default",
                        seed,
                    )
                    automatic_default = transpile(
                        representative,
                        backend=backend,
                        optimization_level=3,
                        seed_transpiler=seed,
                    )
                    constrained_qasm = qasm3.dumps(constrained)
                    fixed_qasm = qasm3.dumps(fixed_default)
                    automatic_qasm = qasm3.dumps(automatic_default)
                    constrained_exposure = exposure_from_qasm(
                        constrained_qasm, metadata, scratch
                    )
                    fixed_exposure = exposure_from_qasm(fixed_qasm, metadata, scratch)
                    automatic_exposure = exposure_from_qasm(
                        automatic_qasm, metadata, scratch
                    )
                    constrained_descriptor = compiled_route_descriptor(
                        constrained, constrained_exposure
                    )
                    fixed_descriptor = compiled_route_descriptor(
                        fixed_default, fixed_exposure
                    )
                    automatic_descriptor = compiled_route_descriptor(
                        automatic_default, automatic_exposure
                    )
                    constrained_path = constrained_dir / (
                        f"{snapshot_name}_{task['task_id']}_seed_{seed}.qasm"
                    )
                    relative_path = str(constrained_path.relative_to(root))
                    frozen_paths.append(relative_path)
                    if constrained_path.exists():
                        frozen_preexisting_count += 1
                        frozen_match = (
                            constrained_path.read_text(encoding="utf-8")
                            == constrained_qasm
                        )
                    else:
                        constrained_path.write_text(constrained_qasm, encoding="utf-8")
                        frozen_match = True
                    frozen_match_count += frozen_match
                    constrained_gain = (
                        automatic_exposure["combined_any_error_proxy"]
                        - constrained_exposure["combined_any_error_proxy"]
                    )
                    fixed_gain = (
                        automatic_exposure["combined_any_error_proxy"]
                        - fixed_exposure["combined_any_error_proxy"]
                    )
                    lookahead_gain = (
                        fixed_exposure["combined_any_error_proxy"]
                        - constrained_exposure["combined_any_error_proxy"]
                    )
                    attribution = loss_attribution(
                        constrained_gain, fixed_gain, lookahead_gain
                    )
                    holdout_rows.append(
                        {
                            "snapshot": snapshot_name,
                            "task_id": task["task_id"],
                            "family": task["family"],
                            "mapping_source_task_id": task["mapping_source_task_id"],
                            "seed": seed,
                            "selected_mapping": mapping,
                            "selected_policy_id": SELECTED_POLICY_ID,
                            "constrained_circuit_path": relative_path,
                            "constrained_circuit_sha256": file_sha256(constrained_path),
                            "frozen_qasm_replay_matches": frozen_match,
                            "constrained_qasm_hash": stable_hash(constrained_qasm),
                            "constrained_route_family": constrained_descriptor,
                            "fixed_mapping_default_route_family": fixed_descriptor,
                            "automatic_default_route_family": automatic_descriptor,
                            "constrained_combined_any_error_proxy": constrained_exposure[
                                "combined_any_error_proxy"
                            ],
                            "fixed_mapping_default_combined_any_error_proxy": fixed_exposure[
                                "combined_any_error_proxy"
                            ],
                            "automatic_default_combined_any_error_proxy": automatic_exposure[
                                "combined_any_error_proxy"
                            ],
                            "constrained_gain_vs_automatic_default": constrained_gain,
                            "fixed_mapping_gain_vs_automatic_default": fixed_gain,
                            "lookahead_gain_vs_fixed_mapping_default": lookahead_gain,
                            "outcome_vs_automatic_default": outcome(constrained_gain),
                            "loss_attribution": attribution,
                        }
                    )

    group_rows = []
    group_keys = sorted({(row["snapshot"], row["task_id"]) for row in holdout_rows})
    for key in group_keys:
        rows = [
            row
            for row in holdout_rows
            if (row["snapshot"], row["task_id"]) == key
        ]
        family_count = len(
            {row["constrained_route_family"]["route_family_id"] for row in rows}
        )
        qasm_count = len({row["constrained_qasm_hash"] for row in rows})
        group_rows.append(
            {
                "snapshot": key[0],
                "task_id": key[1],
                "family": rows[0]["family"],
                "mapping_source_task_id": rows[0]["mapping_source_task_id"],
                "constrained_unique_route_family_count": family_count,
                "constrained_unique_qasm_hash_count": qasm_count,
                "route_family_seed_invariant": family_count == 1,
                "exact_qasm_seed_invariant": qasm_count == 1,
                "mean_constrained_gain_vs_automatic_default": statistics.fmean(
                    row["constrained_gain_vs_automatic_default"] for row in rows
                ),
                "minimum_constrained_gain_vs_automatic_default": min(
                    row["constrained_gain_vs_automatic_default"] for row in rows
                ),
                "mean_lookahead_gain_vs_fixed_mapping_default": statistics.fmean(
                    row["lookahead_gain_vs_fixed_mapping_default"] for row in rows
                ),
                "win_count_vs_automatic_default": sum(
                    row["outcome_vs_automatic_default"] == "win" for row in rows
                ),
                "tie_count_vs_automatic_default": sum(
                    row["outcome_vs_automatic_default"] == "tie" for row in rows
                ),
                "loss_count_vs_automatic_default": sum(
                    row["outcome_vs_automatic_default"] == "loss" for row in rows
                ),
                "fixed_mapping_gap_not_recovered_count": sum(
                    row["loss_attribution"] == "fixed_mapping_gap_not_recovered"
                    for row in rows
                ),
                "fixed_mapping_and_policy_regression_count": sum(
                    row["loss_attribution"] == "fixed_mapping_and_policy_regression"
                    for row in rows
                ),
                "lookahead_policy_induced_loss_count": sum(
                    row["loss_attribution"] == "lookahead_policy_induced_loss"
                    for row in rows
                ),
            }
        )

    route_invariant_count = sum(row["route_family_seed_invariant"] for row in group_rows)
    qasm_invariant_count = sum(row["exact_qasm_seed_invariant"] for row in group_rows)
    win_count = sum(row["outcome_vs_automatic_default"] == "win" for row in holdout_rows)
    tie_count = sum(row["outcome_vs_automatic_default"] == "tie" for row in holdout_rows)
    loss_count = sum(row["outcome_vs_automatic_default"] == "loss" for row in holdout_rows)
    no_loss_group_count = sum(row["loss_count_vs_automatic_default"] == 0 for row in group_rows)
    mapping_gap_count = sum(
        row["loss_attribution"] == "fixed_mapping_gap_not_recovered"
        for row in holdout_rows
    )
    mapping_policy_count = sum(
        row["loss_attribution"] == "fixed_mapping_and_policy_regression"
        for row in holdout_rows
    )
    policy_loss_count = sum(
        row["loss_attribution"] == "lookahead_policy_induced_loss"
        for row in holdout_rows
    )
    deterministic_gate = (
        route_invariant_count == 12
        and qasm_invariant_count == 12
        and frozen_preexisting_count == 120
        and frozen_match_count == 120
    )
    no_loss_gate = loss_count == 0
    summary = {
        "holdout_task_count": len(tasks),
        "holdout_group_count": len(group_rows),
        "holdout_seed_count": len(HOLDOUT_SEEDS),
        "holdout_seeds": list(HOLDOUT_SEEDS),
        "holdout_compilation_count": len(holdout_rows) * 3,
        "holdout_row_count": len(holdout_rows),
        "source_circuit_count": len(source_rows),
        "source_circuits_unseen_vs_r119_count": sum(
            row["unseen_vs_r119_source_circuits"] for row in source_rows
        ),
        "selected_policy_id": SELECTED_POLICY_ID,
        "mapping_or_policy_selected_on_holdout": False,
        "route_family_invariant_group_count": route_invariant_count,
        "exact_qasm_seed_invariant_group_count": qasm_invariant_count,
        "frozen_qasm_preexisting_count": frozen_preexisting_count,
        "frozen_qasm_replay_match_count": frozen_match_count,
        "win_count_vs_automatic_default": win_count,
        "tie_count_vs_automatic_default": tie_count,
        "loss_count_vs_automatic_default": loss_count,
        "no_loss_group_count_vs_automatic_default": no_loss_group_count,
        "fixed_mapping_gap_not_recovered_count": mapping_gap_count,
        "fixed_mapping_and_policy_regression_count": mapping_policy_count,
        "lookahead_policy_induced_loss_count": policy_loss_count,
        "attributed_loss_count": mapping_gap_count
        + mapping_policy_count
        + policy_loss_count,
        "deterministic_generalization_gate_passed": deterministic_gate,
        "automatic_baseline_no_loss_gate_passed": no_loss_gate,
        "exact_qasm_cross_process_replay_claimed": frozen_preexisting_count == 120
        and frozen_match_count == 120,
        "fresh_holdout_seed_block_used": True,
        "r130_or_r132_seeds_reused": False,
        "acceptance_holdout_executed": False,
        "r125_acceptance_rows_read": False,
        "readout_mitigation_tested": False,
        "current_backend_calibration_used": False,
        "hardware_execution_performed": False,
        "protocol_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        {
            "requirement_id": "P1",
            "label": "R132 source and selected policy are hash-bound",
            "passed": r132.get("source_target_id") == UPSTREAM_TARGET_ID
            and summary["selected_policy_id"] == r132["summary"]["selected_policy_id"],
            "evidence": {"r132_sha256": file_sha256(r132_path)},
        },
        {
            "requirement_id": "P2",
            "label": "four unseen source circuit families are materialized",
            "passed": len(source_rows) == 4
            and len({row["source_circuit_sha256"] for row in source_rows}) == 4
            and summary["source_circuits_unseen_vs_r119_count"] == 4,
            "evidence": {"source_rows": source_rows},
        },
        {
            "requirement_id": "P3",
            "label": "fresh holdout seeds are disjoint and no holdout selection occurs",
            "passed": summary["fresh_holdout_seed_block_used"]
            and not summary["r130_or_r132_seeds_reused"]
            and not summary["mapping_or_policy_selected_on_holdout"],
            "evidence": {"holdout_seeds": list(HOLDOUT_SEEDS)},
        },
        {
            "requirement_id": "P4",
            "label": "all 12 groups retain one route-exposure class",
            "passed": route_invariant_count == 12,
            "evidence": {"route_family_invariant_group_count": route_invariant_count},
        },
        {
            "requirement_id": "P5",
            "label": "all 12 groups retain one exact QASM hash across seeds",
            "passed": qasm_invariant_count == 12,
            "evidence": {"exact_qasm_seed_invariant_group_count": qasm_invariant_count},
        },
        {
            "requirement_id": "P6",
            "label": "all 120 constrained circuits replay in a fresh process",
            "passed": frozen_preexisting_count == 120 and frozen_match_count == 120,
            "evidence": {
                "frozen_qasm_preexisting_count": frozen_preexisting_count,
                "frozen_qasm_replay_match_count": frozen_match_count,
            },
        },
        {
            "requirement_id": "P7",
            "label": "all holdout rows compare constrained, fixed-map, and automatic routes",
            "passed": len(holdout_rows) == 120
            and summary["holdout_compilation_count"] == 360,
            "evidence": {"holdout_row_count": len(holdout_rows)},
        },
        {
            "requirement_id": "P8",
            "label": "every automatic-baseline loss has a mapping-or-policy attribution",
            "passed": summary["attributed_loss_count"] == loss_count,
            "evidence": {
                "loss_count": loss_count,
                "attributed_loss_count": summary["attributed_loss_count"],
                "automatic_baseline_no_loss_gate_passed": no_loss_gate,
            },
        },
        {
            "requirement_id": "P9",
            "label": "verifier acceptance, mitigation, calibration, and hardware remain excluded",
            "passed": not summary["acceptance_holdout_executed"]
            and not summary["r125_acceptance_rows_read"]
            and not summary["readout_mitigation_tested"]
            and not summary["current_backend_calibration_used"]
            and not summary["hardware_execution_performed"],
            "evidence": {"compiler_holdout_only": True},
        },
        {
            "requirement_id": "P10",
            "label": "no soundness, advantage, BQP, or new credit is claimed",
            "passed": not summary["protocol_soundness_claimed"]
            and not summary["quantum_advantage_claimed"]
            and not summary["bqp_separation_claimed"]
            and summary["new_credit_delta"] == 0,
            "evidence": {"new_credit_delta": 0},
        },
    ]
    failed = [row["requirement_id"] for row in requirements if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R133 unseen circuit-family holdout",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "requirements": requirements,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "summary": summary,
        "source_circuit_rows": source_rows,
        "holdout_group_rows": group_rows,
        "holdout_rows": holdout_rows,
        "environment": {
            "deterministic_process_environment": DETERMINISTIC_PROCESS_ENV,
            "qiskit": package_version("qiskit"),
            "qiskit_ibm_runtime": package_version("qiskit-ibm-runtime"),
        },
        "artifacts": {
            "r119_result": R119_RESULT_PATH,
            "r132_result": R132_RESULT_PATH,
            "source_circuits": [row["source_circuit_path"] for row in source_rows],
            "constrained_circuits": sorted(frozen_paths),
        },
        "claim_boundary": {
            "what_is_supported": (
                "Unseen circuit-family compiler evidence that the R132 route remains "
                "deterministic but fails the automatic-layout no-loss criterion, with "
                "mapping-versus-policy attribution."
            ),
            "what_is_not_supported": (
                "Verifier acceptance, causal hardware performance, readout mitigation, "
                "current calibration, provider access, hardware execution, protocol soundness, "
                "quantum advantage, BQP separation, or new B10 credit."
            ),
            "next_gate": (
                "Replace transferred mappings with a circuit-family-agnostic deterministic "
                "mapping rule and require zero automatic-baseline losses on a new holdout."
            ),
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
