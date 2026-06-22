#!/usr/bin/env python3
"""Multi-rotation context gate for the priced 3-CNOT union candidate.

T-B1-004br rejected exact inventory matches, same-support context matches, and
one-step same-support context cancellation for the 18 off-pi/4 local-U3
parameters in the best-priced exact 3-CNOT union candidate.  This gate asks the
next bounded question: can any signed sum of two or three same-support context
rotations absorb one of those 18 parameters back to the pi/4 grid?

The result is still only a bounded search boundary. A positive hit would need a
commutation-aware symbolic replay certificate before touching the B7 ledger.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    INVENTORY_QASM_PATH,
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    load_json,
    write_json,
    write_text,
)
from b1_b7_cone01_line1381_multi_rotation_context_gate import (
    SEARCH_WIDTHS,
    best_width_absorption,
    signed_combination_count,
)
from b1_b7_cone01_three_cnot_context_absorption_gate import (
    JSON_OUT as THREE_CNOT_CONTEXT_PATH,
)


ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "results" / "B1_B7_cone01_three_cnot_multi_rotation_context_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_three_cnot_multi_rotation_context_gate.md"

METHOD = "b1_b7_cone01_three_cnot_multi_rotation_context_gate_v0"
STATUS = "cone01_three_cnot_multi_rotation_context_not_accepted"
MODEL_STATUS = "best_three_cnot_candidate_has_no_two_or_three_rotation_context_absorption"


def build_context_rows(source_row: dict[str, Any]) -> list[dict[str, Any]]:
    from b1_b7_cone01_carrier_absorption_inventory_gate import parse_rotation_inventory

    support_qubits = {int(qubit) for qubit in source_row["support_qubits"]}
    context_start = int(source_row["context_start_line"])
    context_end = int(source_row["context_end_line"])
    return [
        row
        for row in parse_rotation_inventory(INVENTORY_QASM_PATH)
        if int(row["qubit"]) in support_qubits
        and context_start <= int(row["line_number"]) <= context_end
    ]


def analyze_source_row(
    source_row: dict[str, Any],
    context_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    value = float(source_row["parameter_value"])
    width_results = [
        best_width_absorption(value, context_rows, width) for width in SEARCH_WIDTHS
    ]
    best_overall = min(
        (result["best_absorption_candidate"] for result in width_results),
        key=lambda candidate: (
            candidate["distance_to_pi_over_four_grid"],
            candidate["width"],
            tuple(candidate["context_lines"]),
        ),
    )
    accepted_occurrence_removal = 0
    return {
        "parameter_index": int(source_row["parameter_index"]),
        "parameter_value": value,
        "value_over_pi": float(source_row["value_over_pi"]),
        "distance_to_pi_over_four_grid": float(source_row["distance_to_pi_over_four_grid"]),
        "support_qubits": source_row["support_qubits"],
        "context_start_line": int(source_row["context_start_line"]),
        "context_end_line": int(source_row["context_end_line"]),
        "context_rotation_argument_count": len(context_rows),
        "source_single_step_best_grid_error": source_row[
            "best_context_grid_cancellation"
        ]["distance_to_pi_over_four_grid"],
        "search_widths": list(SEARCH_WIDTHS),
        "width_results": width_results,
        "best_multi_rotation_context_candidate": best_overall,
        "exact_two_or_three_rotation_absorption": False,
        "accepted_multi_rotation_context_absorption": False,
        "accepted_occurrence_removal": accepted_occurrence_removal,
        "accepted_proxy_t_reduction": accepted_occurrence_removal
        * PROXY_T_PER_OCCURRENCE,
        "claim_boundary": (
            "Two- and three-rotation signed context sums are bounded search hints only. "
            "They are not commutation, symbolic replay, full-circuit replay, local-U3 "
            "pricing acceptance, or B7 resource certificates."
        ),
    }


def build_payload() -> dict[str, Any]:
    context_source = load_json(THREE_CNOT_CONTEXT_PATH)
    source_summary = context_source["summary"]
    source_rows = context_source["three_cnot_context_absorption_rows"]
    context_rows = build_context_rows(source_rows[0]) if source_rows else []
    rows = [analyze_source_row(row, context_rows) for row in source_rows]
    accepted_removed = sum(row["accepted_occurrence_removal"] for row in rows)
    all_width_results = [result for row in rows for result in row["width_results"]]
    best_width2 = [
        result["best_absorption_candidate"]["distance_to_pi_over_four_grid"]
        for result in all_width_results
        if result["width"] == 2
    ]
    best_width3 = [
        result["best_absorption_candidate"]["distance_to_pi_over_four_grid"]
        for result in all_width_results
        if result["width"] == 3
    ]
    summary = {
        "source_three_cnot_context_absorption_method": context_source.get("method"),
        "source_three_cnot_context_absorption_status": context_source.get("status"),
        "source_three_cnot_context_absorption_model_status": context_source.get(
            "model_status"
        ),
        "inventory_qasm": display_path(INVENTORY_QASM_PATH),
        "target_line_number": source_summary["target_line_number"],
        "union_window": source_summary["union_window"],
        "support_qubits": source_summary["support_qubits"],
        "selected_sequence_id": source_summary["selected_sequence_id"],
        "selected_off_pi_over_four_parameter_count": source_summary[
            "selected_off_pi_over_four_parameter_count"
        ],
        "selected_proxy_t_pressure": source_summary["selected_proxy_t_pressure"],
        "source_single_step_exact_absorption_count": source_summary[
            "context_grid_cancellation_exact_parameter_count"
        ],
        "source_context_rotation_argument_count": source_summary[
            "context_rotation_argument_count"
        ],
        "rotation_argument_inventory_count": source_summary[
            "rotation_argument_inventory_count"
        ],
        "context_radius": source_summary["context_radius"],
        "context_start_line": source_summary["context_start_line"],
        "context_end_line": source_summary["context_end_line"],
        "context_rotation_argument_count": len(context_rows),
        "tested_off_grid_parameter_count": len(rows),
        "search_widths": list(SEARCH_WIDTHS),
        "width2_signed_combination_count_per_parameter": signed_combination_count(
            len(context_rows), 2
        ),
        "width3_signed_combination_count_per_parameter": signed_combination_count(
            len(context_rows), 3
        ),
        "total_signed_combination_tests": sum(
            result["signed_combination_count"] for result in all_width_results
        ),
        "width2_exact_absorption_parameter_count": sum(
            1
            for row in rows
            for result in row["width_results"]
            if result["width"] == 2 and result["exact_absorption_candidate_count"] > 0
        ),
        "width3_exact_absorption_parameter_count": sum(
            1
            for row in rows
            for result in row["width_results"]
            if result["width"] == 3 and result["exact_absorption_candidate_count"] > 0
        ),
        "two_or_three_rotation_exact_absorption_parameter_count": sum(
            1 for row in rows if row["exact_two_or_three_rotation_absorption"]
        ),
        "min_best_width2_context_grid_error": min(best_width2) if best_width2 else None,
        "max_best_width2_context_grid_error": max(best_width2) if best_width2 else None,
        "min_best_width3_context_grid_error": min(best_width3) if best_width3 else None,
        "max_best_width3_context_grid_error": max(best_width3) if best_width3 else None,
        "accepted_multi_rotation_context_absorption_count": 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": accepted_removed * PROXY_T_PER_OCCURRENCE,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed)
        * PROXY_T_PER_OCCURRENCE,
        "multi_rotation_context_absorption_claimed": False,
        "full_circuit_rewrite_claimed": False,
        "local_u3_pricing_accepted": False,
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
        "inventory_qasm": display_path(INVENTORY_QASM_PATH),
        "source_three_cnot_context_absorption_result": display_path(
            THREE_CNOT_CONTEXT_PATH
        ),
        "summary": summary,
        "three_cnot_multi_rotation_context_rows": rows,
        "claim_boundary": {
            "supported_claim": (
                "The 18 off-pi/4 parameters of the best-priced exact 3-CNOT "
                "union candidate have no exact two- or three-rotation signed "
                "same-support context absorption back to the pi/4 grid inside "
                "the configured window."
            ),
            "unsupported_claims": [
                "This is not a global obstruction theorem for the 3-CNOT candidate.",
                "This does not reject four-or-more-rotation symbolic absorption.",
                "This does not reject commutation-aware or full-circuit replay routes.",
                "No B7 occurrence or proxy-T ledger reduction is accepted.",
            ],
            "multi_rotation_context_absorption_claimed": False,
            "full_circuit_rewrite_claimed": False,
            "local_u3_pricing_accepted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }
    payload["summary"]["validation_error_count"] = len(validate_payload(payload))
    return payload


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload.get("summary", {})
    rows = payload.get("three_cnot_multi_rotation_context_rows", [])
    expected = {
        "source_three_cnot_context_absorption_method": "b1_b7_cone01_three_cnot_context_absorption_gate_v0",
        "source_three_cnot_context_absorption_status": "cone01_three_cnot_context_absorption_not_accepted",
        "source_three_cnot_context_absorption_model_status": "best_three_cnot_candidate_has_no_single_step_context_absorption",
        "target_line_number": 1381,
        "union_window": [1369, 1379],
        "support_qubits": [4, 8],
        "selected_sequence_id": "10-10-01",
        "selected_off_pi_over_four_parameter_count": 18,
        "selected_proxy_t_pressure": 360,
        "source_single_step_exact_absorption_count": 0,
        "rotation_argument_inventory_count": 2049,
        "context_radius": 64,
        "context_start_line": 1305,
        "context_end_line": 1443,
        "context_rotation_argument_count": 44,
        "tested_off_grid_parameter_count": 18,
        "search_widths": [2, 3],
        "width2_signed_combination_count_per_parameter": 3784,
        "width3_signed_combination_count_per_parameter": 105952,
        "total_signed_combination_tests": 1975248,
        "width2_exact_absorption_parameter_count": 0,
        "width3_exact_absorption_parameter_count": 0,
        "two_or_three_rotation_exact_absorption_parameter_count": 0,
        "accepted_multi_rotation_context_absorption_count": 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
        "multi_rotation_context_absorption_claimed": False,
        "full_circuit_rewrite_claimed": False,
        "local_u3_pricing_accepted": False,
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
    for field, expected_value in expected.items():
        if summary.get(field) != expected_value:
            errors.append(f"{field}_expected_{expected_value}_got_{summary.get(field)}")
    if len(rows) != 18:
        errors.append(f"row_count_expected_18_got_{len(rows)}")
    else:
        expected_indices = [2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 15, 16, 17, 19, 20, 21, 22, 23]
        if [row.get("parameter_index") for row in rows] != expected_indices:
            errors.append("parameter_indices_mismatch")
        for row in rows:
            if row.get("accepted_multi_rotation_context_absorption") is not False:
                errors.append(f"parameter_{row.get('parameter_index')}_must_not_accept_absorption")
            if row.get("exact_two_or_three_rotation_absorption") is not False:
                errors.append(f"parameter_{row.get('parameter_index')}_must_not_exact_absorb")
            if len(row.get("width_results", [])) != 2:
                errors.append(f"parameter_{row.get('parameter_index')}_width_result_count_mismatch")
            for result in row.get("width_results", []):
                if result.get("exact_absorption_candidate_count") != 0:
                    errors.append(
                        f"parameter_{row.get('parameter_index')}_width_{result.get('width')}_must_have_zero_hits"
                    )
                if result.get("accepted_multi_rotation_context_absorption") is not False:
                    errors.append(
                        f"parameter_{row.get('parameter_index')}_width_{result.get('width')}_must_not_accept"
                    )
    for field in [
        "multi_rotation_context_absorption_claimed",
        "full_circuit_rewrite_claimed",
        "local_u3_pricing_accepted",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field}_must_be_false")
        if payload.get("claim_boundary", {}).get(field) is not False:
            errors.append(f"claim_boundary_{field}_must_be_false")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = payload["three_cnot_multi_rotation_context_rows"]
    lines = [
        "# B1/B7 Cone_01 Three-CNOT Multi-Rotation Context Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004br and tests whether the 18 off-pi/4 local-U3 parameters in the best exact 3-CNOT priced candidate can be absorbed by signed sums of two or three nearby same-support context rotations in the native optimized `gcm_h6` QASM.",
        "",
        "## Summary",
        "",
        f"- Selected sequence: `{summary['selected_sequence_id']}`",
        f"- Selected off-grid parameters / proxy-T pressure: `{summary['selected_off_pi_over_four_parameter_count']}` / `{summary['selected_proxy_t_pressure']}`",
        f"- Source window: `{summary['union_window']}`",
        f"- Context radius: `+/-{summary['context_radius']}` lines",
        f"- Context rotation arguments reviewed: `{summary['context_rotation_argument_count']}`",
        f"- Parameters tested: `{summary['tested_off_grid_parameter_count']}`",
        f"- Signed combinations per parameter, width 2 / width 3: `{summary['width2_signed_combination_count_per_parameter']}` / `{summary['width3_signed_combination_count_per_parameter']}`",
        f"- Total signed combination tests: `{summary['total_signed_combination_tests']}`",
        f"- Width-2 / width-3 exact absorption parameters: `{summary['width2_exact_absorption_parameter_count']}` / `{summary['width3_exact_absorption_parameter_count']}`",
        f"- Min best width-2 / width-3 grid error: `{summary['min_best_width2_context_grid_error']:.12e}` / `{summary['min_best_width3_context_grid_error']:.12e}`",
        f"- Accepted replay / occurrence / proxy-T reduction: `{summary['accepted_full_circuit_replay_certificate_count']}` / `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Parameter Rows",
        "",
        "| Param index | Value/pi | Best width-2 error | Best width-3 error | Best overall width | Accepted |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        by_width = {
            result["width"]: result["best_absorption_candidate"]["distance_to_pi_over_four_grid"]
            for result in row["width_results"]
        }
        best = row["best_multi_rotation_context_candidate"]
        lines.append(
            f"| {row['parameter_index']} | {row['value_over_pi']:.12f} | "
            f"{by_width[2]:.6e} | {by_width[3]:.6e} | "
            f"{best['width']} | {row['accepted_multi_rotation_context_absorption']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This closes only a bounded two-/three-rotation context-combination route for the direct 3-CNOT candidate. It does not rule out four-or-more-rotation symbolic absorption, commutation-aware rewriting, broader symbolic synthesis, or full-circuit replay. The B7 ledger remains unchanged at zero accepted occurrence removals and zero accepted proxy-T reduction.",
            "",
            "## Next Required Gate",
            "",
            "The next route must either build a different scaffold that beats the current 5-parameter / 100-proxy-T line-1381 boundary, attempt a justified four-or-more-rotation symbolic absorption route, or abandon this direct 3-CNOT route for another occurrence-removing scaffold with honest B7 resource accounting.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=JSON_OUT)
    parser.add_argument("--markdown-output", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload()
    errors = validate_payload(payload)
    payload["summary"]["validation_error_count"] = len(errors)
    if errors:
        payload["validation_errors"] = errors
    write_json(args.json_output, payload, pretty=args.pretty)
    write_text(args.markdown_output, render_markdown(payload))
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
