#!/usr/bin/env python3
"""Leave-three-out pressure gate for the B1/B7 cone_01 line-1381 parameters.

T-B1-004bh showed that no single current line-1381 off-grid local-U3 parameter
can be snapped back to the pi/4 grid for free. This gate tightens that boundary:
for every triple of the five current off-grid parameters, snap that triple back to the
pi/4 grid and re-optimize the remaining two parameters on the same 2-CNOT
scaffold.

All ten triple-removal trials fail the exact replay threshold. This is still
scaffold-local pressure, not a global minimality theorem.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    load_json,
    write_json,
    write_text,
)
from b1_b7_cone01_local_u3_exactification_gate import (
    best_exact_scaffold,
    snap_to_pi_over_four,
    wrap_angle,
)
from b1_b7_cone01_packet_synthesis_search_gate import (
    EXACT_TOLERANCE,
    first_cnot_orientation,
    residual_norm,
    scaffold_unitary,
    target_matrix,
)
from b1_b7_cone01_sparse_local_u3_repair_gate import optimize_free_indices


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_PACKET_PATH = ROOT / "results" / "B1_B7_cone01_semantic_replay_packet_gate_v0.json"
SYNTHESIS_PATH = ROOT / "results" / "B1_B7_cone01_packet_synthesis_search_gate_v0.json"
FIVE_PARAMETER_PATH = (
    ROOT / "results" / "B1_B7_cone01_five_parameter_line1381_exact_repair_gate_v0.json"
)
LEAVE_TWO_OUT_PATH = (
    ROOT / "results" / "B1_B7_cone01_line1381_leave_two_out_parameter_gate_v0.json"
)
JSON_OUT = ROOT / "results" / "B1_B7_cone01_line1381_leave_three_out_parameter_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_line1381_leave_three_out_parameter_gate.md"

METHOD = "b1_b7_cone01_line1381_leave_three_out_parameter_gate_v0"
STATUS = "cone01_line1381_no_three_parameter_free_removal"
MODEL_STATUS = "line1381_off_grid_parameter_triples_are_leave_three_out_required"
TARGET_LINE = 1381
DEFAULT_MAX_NFEV = 1800


def by_line(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(row["candidate_line_number"]): row for row in rows}


def build_repaired_parameters(
    original_parameters: np.ndarray, five_row: dict[str, Any]
) -> tuple[np.ndarray, list[int], list[float]]:
    snapped = np.array(
        [wrap_angle(snap_to_pi_over_four(value)) for value in original_parameters],
        dtype=float,
    )
    indices = [int(index) for index in five_row["first_exact_five_parameter_free_indices"]]
    values = [float(value) for value in five_row["first_exact_five_parameter_free_values"]]
    repaired = snapped.copy()
    for index, value in zip(indices, values):
        repaired[index] = value
    return repaired, indices, values


def run_probe(max_nfev: int) -> dict[str, Any]:
    semantic = load_json(SEMANTIC_PACKET_PATH)
    synthesis = load_json(SYNTHESIS_PATH)
    five_parameter = load_json(FIVE_PARAMETER_PATH)
    leave_two_out = load_json(LEAVE_TWO_OUT_PATH)
    packet = by_line(semantic["semantic_replay_packets"])[TARGET_LINE]
    synthesis_row = by_line(synthesis["packet_synthesis_rows"])[TARGET_LINE]
    five_row = by_line(five_parameter["five_parameter_line1381_exact_repair_rows"])[TARGET_LINE]
    exact = best_exact_scaffold(synthesis_row)
    if exact is None:
        raise ValueError(f"missing exact scaffold for line {TARGET_LINE}")

    original_parameters = np.array([float(value) for value in exact["best"]["wrapped_parameters"]])
    repaired_parameters, off_grid_indices, off_grid_values = build_repaired_parameters(
        original_parameters, five_row
    )
    matrix = target_matrix(packet)
    control, target_qubit = first_cnot_orientation(packet)
    cnot_count = int(exact["cnot_count"])
    base_residual = residual_norm(
        scaffold_unitary(repaired_parameters, cnot_count, control, target_qubit),
        matrix,
    )

    rows = []
    for fixed_triple in itertools.combinations(off_grid_indices, 3):
        base = repaired_parameters.copy()
        fixed_values = []
        fixed_grid_values = []
        fixed_snap_errors = []
        for fixed_index in fixed_triple:
            original_value = float(base[fixed_index])
            grid_value = float(wrap_angle(snap_to_pi_over_four(original_value)))
            base[fixed_index] = grid_value
            fixed_values.append(original_value)
            fixed_grid_values.append(grid_value)
            fixed_snap_errors.append(abs(original_value - grid_value))
        reoptimized_indices = tuple(index for index in off_grid_indices if index not in fixed_triple)
        row = optimize_free_indices(
            base,
            repaired_parameters,
            reoptimized_indices,
            matrix,
            cnot_count,
            control,
            target_qubit,
            max_nfev,
        )
        rows.append(
            {
                "fixed_parameter_indices": list(fixed_triple),
                "fixed_original_values": fixed_values,
                "fixed_pi_over_four_values": fixed_grid_values,
                "fixed_absolute_snap_errors": fixed_snap_errors,
                "reoptimized_free_indices": list(reoptimized_indices),
                "reoptimized_free_parameter_count": len(reoptimized_indices),
                "residual_norm": row["residual_norm"],
                "exact_pass": row["exact_pass"],
                "optimizer_success": row["optimizer_success"],
                "optimizer_nfev": row["optimizer_nfev"],
                "off_pi_over_four_parameter_count_after_reoptimization": int(
                    row["repaired_parameter_stats"]["off_pi_over_four_parameter_count"]
                ),
            }
        )

    accepted_removed = 0
    exact_pass_count = sum(1 for row in rows if row["exact_pass"])
    best_row = min(rows, key=lambda row: row["residual_norm"])
    worst_row = max(rows, key=lambda row: row["residual_norm"])
    summary = {
        "source_semantic_packet_method": semantic.get("method"),
        "source_packet_synthesis_method": synthesis.get("method"),
        "source_five_parameter_line1381_exact_repair_method": five_parameter.get("method"),
        "source_leave_two_out_parameter_method": leave_two_out.get("method"),
        "target_candidate_line_number": TARGET_LINE,
        "support_qubits": packet["support_qubits"],
        "window_start_line": int(packet["window_start_line"]),
        "window_end_line": int(packet["window_end_line"]),
        "source_cnot_count": int(packet["cx_count"]),
        "replacement_cnot_count": cnot_count,
        "candidate_cnot_reduction": int(packet["cx_count"]) - cnot_count,
        "base_five_parameter_residual_norm": base_residual,
        "exact_tolerance": EXACT_TOLERANCE,
        "current_off_grid_parameter_indices": off_grid_indices,
        "current_off_grid_parameter_values": off_grid_values,
        "current_off_grid_parameter_count": len(off_grid_indices),
        "leave_three_out_row_count": len(rows),
        "leave_three_out_exact_pass_count": exact_pass_count,
        "leave_three_out_exact_fail_count": len(rows) - exact_pass_count,
        "all_three_parameter_removals_fail": exact_pass_count == 0,
        "best_leave_three_out_residual_norm": best_row["residual_norm"],
        "best_leave_three_out_fixed_parameter_indices": best_row["fixed_parameter_indices"],
        "worst_leave_three_out_residual_norm": worst_row["residual_norm"],
        "worst_leave_three_out_fixed_parameter_indices": worst_row["fixed_parameter_indices"],
        "min_residual_ratio_to_exact_tolerance": best_row["residual_norm"] / EXACT_TOLERANCE,
        "max_residual_ratio_to_exact_tolerance": worst_row["residual_norm"] / EXACT_TOLERANCE,
        "three_parameter_free_removal_accepted": False,
        "line1381_off_grid_parameters_eliminated": False,
        "line1381_off_grid_parameters_absorbed": False,
        "line1381_off_grid_parameters_symbolically_decomposed": False,
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
        "source_packet_synthesis_result": display_path(SYNTHESIS_PATH),
        "source_five_parameter_line1381_exact_repair_result": display_path(
            FIVE_PARAMETER_PATH
        ),
        "source_leave_two_out_parameter_result": display_path(LEAVE_TWO_OUT_PATH),
        "summary": summary,
        "line1381_leave_three_out_parameter_rows": rows,
        "claim_boundary": {
            "supported_claim": (
                "Within the current line-1381 two-CNOT scaffold and local replay target, "
                "snapping any triple of the five off-grid parameters back to the pi/4 grid "
                "and re-optimizing the other two does not recover exactness."
            ),
            "unsupported_claims": [
                "This is not a global five-parameter minimality theorem.",
                "This does not rule out a different scaffold, a symbolic identity, or context absorption.",
                "This does not eliminate, absorb, or price the five line-1381 parameters.",
                "This does not improve the B7 ledger.",
            ],
            "three_parameter_free_removal_accepted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }
    payload["summary"]["validation_error_count"] = len(validate_payload(payload))
    return payload


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload.get("summary", {})
    rows = payload.get("line1381_leave_three_out_parameter_rows", [])
    expected = {
        "target_candidate_line_number": 1381,
        "support_qubits": [4, 8],
        "window_start_line": 1369,
        "window_end_line": 1379,
        "source_cnot_count": 5,
        "replacement_cnot_count": 2,
        "candidate_cnot_reduction": 3,
        "current_off_grid_parameter_indices": [3, 4, 9, 16, 17],
        "current_off_grid_parameter_count": 5,
        "leave_three_out_row_count": 10,
        "leave_three_out_exact_pass_count": 0,
        "leave_three_out_exact_fail_count": 10,
        "all_three_parameter_removals_fail": True,
        "best_leave_three_out_residual_norm": 0.29673862906454757,
        "best_leave_three_out_fixed_parameter_indices": [4, 9, 16],
        "worst_leave_three_out_residual_norm": 0.7449029676343185,
        "worst_leave_three_out_fixed_parameter_indices": [4, 16, 17],
        "min_residual_ratio_to_exact_tolerance": 29673862.906454757,
        "max_residual_ratio_to_exact_tolerance": 74490296.76343185,
        "three_parameter_free_removal_accepted": False,
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
    if len(rows) != 10:
        errors.append(f"row_count_expected_10_got_{len(rows)}")
    if any(row.get("exact_pass") for row in rows):
        errors.append("unexpected_leave_three_out_exact_pass")
    if any(row.get("reoptimized_free_parameter_count") != 2 for row in rows):
        errors.append("leave_three_out_rows_must_reoptimize_two_parameters")
    if summary.get("best_leave_three_out_residual_norm", 0.0) <= EXACT_TOLERANCE:
        errors.append("best_leave_three_out_residual_not_above_exact_tolerance")
    if payload.get("claim_boundary", {}).get("b7_ledger_improvement_claimed") is not False:
        errors.append("claim_boundary_b7_ledger_improvement_claimed_not_false")
    return errors


def markdown_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 Line-1381 Leave-Three-Out Parameter Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- Source five-parameter repair: `{payload['source_five_parameter_line1381_exact_repair_result']}`",
        f"- Source leave-two-out gate: `{payload['source_leave_two_out_parameter_result']}`",
        "",
        "## Result",
        "",
        f"- Current line-1381 off-grid parameter indices: `{summary['current_off_grid_parameter_indices']}`",
        f"- Base five-parameter residual: `{summary['base_five_parameter_residual_norm']}`",
        f"- Leave-three-out rows: `{summary['leave_three_out_row_count']}`",
        f"- Exact pass / fail: `{summary['leave_three_out_exact_pass_count']}` / `{summary['leave_three_out_exact_fail_count']}`",
        f"- Best leave-three-out residual: `{summary['best_leave_three_out_residual_norm']}` at parameters `{summary['best_leave_three_out_fixed_parameter_indices']}`",
        f"- Worst leave-three-out residual: `{summary['worst_leave_three_out_residual_norm']}` at parameters `{summary['worst_leave_three_out_fixed_parameter_indices']}`",
        f"- Minimum residual ratio to exact tolerance: `{summary['min_residual_ratio_to_exact_tolerance']}`",
        f"- Three-parameter free removal accepted: `{summary['three_parameter_free_removal_accepted']}`",
        f"- Accepted occurrence / proxy-T reduction / B7 claim: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}` / `{summary['b7_ledger_improvement_claimed']}`",
        "",
        "## Leave-Three-Out Rows",
        "",
        "| Fixed parameters | Snap errors | Reoptimized indices | Residual | Exact |",
        "| --- | ---: | --- | ---: | --- |",
    ]
    for row in payload["line1381_leave_three_out_parameter_rows"]:
        lines.append(
            "| "
            f"{row['fixed_parameter_indices']} | "
            f"{[round(value, 12) for value in row['fixed_absolute_snap_errors']]} | "
            f"`{row['reoptimized_free_indices']}` | "
            f"{row['residual_norm']:.12g} | "
            f"{row['exact_pass']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- This is a scaffold-local leave-three-out pressure gate, not a global minimality theorem.",
            "- The result blocks a cheap three-parameter removal claim for line 1381, but it does not remove, absorb, or symbolically decompose the five-parameter burden.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-nfev", type=int, default=DEFAULT_MAX_NFEV)
    parser.add_argument("--json-output", default=str(JSON_OUT))
    parser.add_argument("--markdown-output", default=str(MD_OUT))
    args = parser.parse_args()
    payload = run_probe(args.max_nfev)
    write_json(Path(args.json_output), payload, True)
    write_text(Path(args.markdown_output), markdown_report(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
