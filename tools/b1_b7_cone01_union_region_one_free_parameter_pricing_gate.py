#!/usr/bin/env python3
"""One-free-parameter pricing gate for B1/B7 cone_01 union-region candidates.

T-B1-004bm showed that fully snapping the exact 2-CNOT union-region census
candidates to the pi/4 grid fails. This gate tests the next-cheapest pricing
escape hatch: for each exact 2-CNOT union candidate, snap every local-U3
parameter to the pi/4 grid, then free exactly one parameter and re-optimize it.

If any trial reached exact replay, the union route would have a plausible
one-off-grid-parameter pricing path. If all fail, the project must not count a
20-proxy-T union replacement route without a different scaffold or symbolic
absorption proof.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import least_squares

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    load_json,
    write_json,
    write_text,
)
from b1_b7_cone01_local_u3_exactification_gate import snap_to_pi_over_four, wrap_angle
from b1_b7_cone01_packet_synthesis_search_gate import (
    EXACT_TOLERANCE,
    parameter_stats,
    residual_norm,
    residual_vector,
    target_matrix,
)
from b1_b7_cone01_union_region_two_cnot_orientation_census_gate import (
    mixed_scaffold_unitary,
)


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_PACKET_PATH = ROOT / "results" / "B1_B7_cone01_semantic_replay_packet_gate_v0.json"
ORIENTATION_CENSUS_PATH = (
    ROOT / "results" / "B1_B7_cone01_union_region_two_cnot_orientation_census_gate_v0.json"
)
GRID_SNAP_PATH = (
    ROOT / "results" / "B1_B7_cone01_union_region_grid_snap_pricing_gate_v0.json"
)
JSON_OUT = (
    ROOT / "results" / "B1_B7_cone01_union_region_one_free_parameter_pricing_gate_v0.json"
)
MD_OUT = (
    ROOT / "research" / "B1_B7_cone01_union_region_one_free_parameter_pricing_gate.md"
)

METHOD = "b1_b7_cone01_union_region_one_free_parameter_pricing_gate_v0"
STATUS = "cone01_union_region_one_free_parameter_pricing_rejected"
MODEL_STATUS = "one_free_parameter_union_census_candidates_do_not_recover_exactness"
TARGET_LINE = 1381
DEFAULT_MAX_NFEV = 900


def line_packet(payload: dict[str, Any], line_number: int) -> dict[str, Any]:
    for packet in payload.get("semantic_replay_packets", []):
        if int(packet["candidate_line_number"]) == line_number:
            return packet
    raise ValueError(f"missing semantic packet line {line_number}")


def snapped_parameters(values: list[float]) -> np.ndarray:
    return np.array(
        [float(wrap_angle(snap_to_pi_over_four(float(value)))) for value in values],
        dtype=float,
    )


def one_free_seeds(grid_value: float, original_value: float) -> list[np.ndarray]:
    return [
        np.array([grid_value], dtype=float),
        np.array([original_value], dtype=float),
        np.array([0.0], dtype=float),
        np.array([math.pi / 4], dtype=float),
        np.array([-math.pi / 4], dtype=float),
        np.array([math.pi / 2], dtype=float),
        np.array([-math.pi / 2], dtype=float),
    ]


def optimize_one_parameter(
    base: np.ndarray,
    original: np.ndarray,
    parameter_index: int,
    sequence: list[tuple[int, int]],
    target: np.ndarray,
    max_nfev: int,
) -> dict[str, Any]:
    def objective(value: np.ndarray) -> np.ndarray:
        trial = base.copy()
        trial[parameter_index] = value[0]
        return residual_vector(mixed_scaffold_unitary(trial, sequence), target)

    best: dict[str, Any] | None = None
    for seed_index, seed in enumerate(one_free_seeds(base[parameter_index], original[parameter_index])):
        result = least_squares(
            objective,
            seed,
            method="trf",
            max_nfev=max_nfev,
            ftol=1e-12,
            xtol=1e-12,
            gtol=1e-12,
        )
        residual = float(np.linalg.norm(result.fun))
        if best is None or residual < best["residual_norm"]:
            repaired = base.copy()
            repaired[parameter_index] = result.x[0]
            wrapped = [float(wrap_angle(value)) for value in repaired]
            best = {
                "free_parameter_index": parameter_index,
                "free_parameter_value": float(wrap_angle(result.x[0])),
                "source_parameter_value": float(original[parameter_index]),
                "grid_parameter_value": float(base[parameter_index]),
                "absolute_delta_from_grid": abs(
                    float(wrap_angle(result.x[0])) - float(base[parameter_index])
                ),
                "residual_norm": residual,
                "residual_ratio_to_exact_tolerance": residual / EXACT_TOLERANCE,
                "exact_pass": residual <= EXACT_TOLERANCE,
                "optimizer_success": bool(result.success),
                "optimizer_nfev": int(result.nfev),
                "best_seed_index": seed_index,
                "repaired_parameter_stats": parameter_stats(wrapped),
            }
    assert best is not None
    return best


def run_probe(max_nfev: int) -> dict[str, Any]:
    semantic = load_json(SEMANTIC_PACKET_PATH)
    census = load_json(ORIENTATION_CENSUS_PATH)
    grid_snap = load_json(GRID_SNAP_PATH)
    packet = line_packet(semantic, TARGET_LINE)
    target = target_matrix(packet)

    trial_rows: list[dict[str, Any]] = []
    sequence_rows: list[dict[str, Any]] = []
    for row in census["union_region_two_cnot_orientation_rows"]:
        sequence = [(int(control), int(target_qubit)) for control, target_qubit in row["cnot_sequence"]]
        original = np.array([float(value) for value in row["best"]["wrapped_parameters"]], dtype=float)
        snapped = snapped_parameters(original.tolist())
        snapped_residual = residual_norm(mixed_scaffold_unitary(snapped, sequence), target)
        sequence_trials = []
        for parameter_index in range(len(original)):
            trial = optimize_one_parameter(
                snapped,
                original,
                parameter_index,
                sequence,
                target,
                max_nfev,
            )
            trial.update(
                {
                    "sequence_id": row["sequence_id"],
                    "cnot_sequence": row["cnot_sequence"],
                }
            )
            sequence_trials.append(trial)
            trial_rows.append(trial)
        best_trial = min(sequence_trials, key=lambda trial: trial["residual_norm"])
        sequence_rows.append(
            {
                "sequence_id": row["sequence_id"],
                "cnot_sequence": row["cnot_sequence"],
                "source_residual_norm": row["best"]["residual_norm"],
                "source_off_pi_over_four_parameter_count": row["best"]["parameter_stats"][
                    "off_pi_over_four_grid_parameter_count"
                ],
                "grid_snap_residual_norm": snapped_residual,
                "one_free_trial_count": len(sequence_trials),
                "one_free_exact_pass_count": sum(
                    1 for trial in sequence_trials if trial["exact_pass"]
                ),
                "best_one_free_parameter_index": best_trial["free_parameter_index"],
                "best_one_free_residual_norm": best_trial["residual_norm"],
                "best_one_free_residual_ratio_to_exact_tolerance": best_trial[
                    "residual_ratio_to_exact_tolerance"
                ],
                "best_one_free_off_pi_over_four_parameter_count": best_trial[
                    "repaired_parameter_stats"
                ]["off_pi_over_four_grid_parameter_count"],
                "best_one_free_nonzero_parameter_count": best_trial[
                    "repaired_parameter_stats"
                ]["nonzero_parameter_count"],
            }
        )

    exact_pass_count = sum(1 for trial in trial_rows if trial["exact_pass"])
    best_trial = min(trial_rows, key=lambda trial: trial["residual_norm"])
    best_sequence = min(sequence_rows, key=lambda row: row["best_one_free_residual_norm"])
    worst_sequence = max(sequence_rows, key=lambda row: row["best_one_free_residual_norm"])
    accepted_removed = 0
    one_free_proxy_t_pressure = 20
    summary = {
        "source_semantic_packet_method": semantic.get("method"),
        "source_orientation_census_method": census.get("method"),
        "source_grid_snap_pricing_method": grid_snap.get("method"),
        "target_line_number": TARGET_LINE,
        "union_window": [
            int(packet["window_start_line"]),
            int(packet["window_end_line"]),
        ],
        "support_qubits": packet["support_qubits"],
        "source_cnot_count": int(packet["cx_count"]),
        "searched_cnot_count": 2,
        "orientation_sequence_count": len(sequence_rows),
        "orientation_sequence_ids": [row["sequence_id"] for row in sequence_rows],
        "one_free_trial_count": len(trial_rows),
        "one_free_exact_pass_count": exact_pass_count,
        "one_free_exact_fail_count": len(trial_rows) - exact_pass_count,
        "all_one_free_trials_fail": exact_pass_count == 0,
        "best_one_free_sequence_id": best_sequence["sequence_id"],
        "best_one_free_parameter_index": best_trial["free_parameter_index"],
        "best_one_free_residual_norm": best_trial["residual_norm"],
        "best_one_free_residual_ratio_to_exact_tolerance": best_trial[
            "residual_ratio_to_exact_tolerance"
        ],
        "worst_best_sequence_id": worst_sequence["sequence_id"],
        "worst_best_sequence_residual_norm": worst_sequence["best_one_free_residual_norm"],
        "one_free_proxy_t_pressure_if_accepted": one_free_proxy_t_pressure,
        "current_line1381_proxy_t_pressure": grid_snap["summary"][
            "current_line1381_proxy_t_pressure"
        ],
        "best_source_proxy_t_pressure": grid_snap["summary"]["best_source_proxy_t_pressure"],
        "one_free_pricing_accepted": False,
        "local_u3_pricing_completed": False,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_full_circuit_qasm_patch_count": 0,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(
            0,
            (REQUIRED_OCCURRENCE_REMOVALS - accepted_removed) * PROXY_T_PER_OCCURRENCE,
        ),
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
    }
    payload = {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "source_semantic_packet_result": display_path(SEMANTIC_PACKET_PATH),
        "source_orientation_census_result": display_path(ORIENTATION_CENSUS_PATH),
        "source_grid_snap_pricing_result": display_path(GRID_SNAP_PATH),
        "summary": summary,
        "union_region_one_free_sequence_rows": sequence_rows,
        "union_region_one_free_trial_rows": trial_rows,
        "claim_boundary": {
            "supported_claim": (
                "Within the T-B1-004bf union-region two-CNOT census candidates, "
                "no one-free-parameter pi/4-grid repair reaches exact replay."
            ),
            "unsupported_claims": [
                "This is not a global lower bound for the union target.",
                "This does not rule out two or more free parameters, a different scaffold, or symbolic absorption.",
                "This does not accept local-U3 pricing, occurrence removal, or a B7 ledger improvement.",
            ],
            "one_free_pricing_accepted": False,
            "local_u3_pricing_completed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }
    payload["summary"]["validation_error_count"] = len(validate_payload(payload))
    return payload


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload.get("summary", {})
    sequence_rows = payload.get("union_region_one_free_sequence_rows", [])
    trial_rows = payload.get("union_region_one_free_trial_rows", [])
    expected = {
        "target_line_number": 1381,
        "union_window": [1369, 1379],
        "support_qubits": [4, 8],
        "source_cnot_count": 5,
        "searched_cnot_count": 2,
        "orientation_sequence_count": 4,
        "orientation_sequence_ids": ["01-01", "01-10", "10-01", "10-10"],
        "one_free_trial_count": 72,
        "one_free_exact_pass_count": 0,
        "one_free_exact_fail_count": 72,
        "all_one_free_trials_fail": True,
        "one_free_pricing_accepted": False,
        "local_u3_pricing_completed": False,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_full_circuit_qasm_patch_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
    }
    if payload.get("benchmark_id") != "B1":
        errors.append("benchmark_id_mismatch")
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if payload.get("model_status") != MODEL_STATUS:
        errors.append("model_status_mismatch")
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(f"summary_{key}_expected_{value!r}_got_{summary.get(key)!r}")
    if len(sequence_rows) != 4:
        errors.append(f"sequence_row_count_expected_4_got_{len(sequence_rows)}")
    if len(trial_rows) != 72:
        errors.append(f"trial_row_count_expected_72_got_{len(trial_rows)}")
    if any(trial.get("exact_pass") for trial in trial_rows):
        errors.append("unexpected_one_free_exact_pass")
    claims = payload.get("claim_boundary", {})
    for field in [
        "one_free_pricing_accepted",
        "local_u3_pricing_completed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if claims.get(field) is not False:
            errors.append(f"claim_boundary_{field}_not_false")
    return errors


def markdown_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 Union-Region One-Free-Parameter Pricing Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- Union window: `{summary['union_window']}`",
        f"- Support qubits: `{summary['support_qubits']}`",
        f"- Orientation sequences: `{summary['orientation_sequence_ids']}`",
        f"- One-free trials: `{summary['one_free_trial_count']}`",
        f"- Exact pass / fail: `{summary['one_free_exact_pass_count']}` / `{summary['one_free_exact_fail_count']}`",
        f"- Best one-free residual: `{summary['best_one_free_residual_norm']}`",
        f"- Best one-free sequence / parameter: `{summary['best_one_free_sequence_id']}` / `{summary['best_one_free_parameter_index']}`",
        f"- Worst best-sequence residual: `{summary['worst_best_sequence_residual_norm']}`",
        f"- One-free proxy-T pressure if accepted: `{summary['one_free_proxy_t_pressure_if_accepted']}`",
        f"- Current line-1381 proxy-T pressure: `{summary['current_line1381_proxy_t_pressure']}`",
        f"- B7 ledger improvement claimed: `{summary['b7_ledger_improvement_claimed']}`",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"]["supported_claim"],
        "",
        "Unsupported claims:",
    ]
    for claim in payload["claim_boundary"]["unsupported_claims"]:
        lines.append(f"- {claim}")
    lines.extend(["", "## Sequence Best Rows", ""])
    for row in payload["union_region_one_free_sequence_rows"]:
        lines.append(
            "- "
            f"`{row['sequence_id']}`: best parameter `{row['best_one_free_parameter_index']}`, "
            f"residual `{row['best_one_free_residual_norm']}`, "
            f"exact passes `{row['one_free_exact_pass_count']}` / `{row['one_free_trial_count']}`"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=JSON_OUT)
    parser.add_argument("--markdown-output", type=Path, default=MD_OUT)
    parser.add_argument("--max-nfev", type=int, default=DEFAULT_MAX_NFEV)
    args = parser.parse_args()

    payload = run_probe(args.max_nfev)
    errors = validate_payload(payload)
    if errors:
        raise SystemExit("validation failed: " + "; ".join(errors))
    write_json(args.json_output, payload, True)
    write_text(args.markdown_output, markdown_report(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
