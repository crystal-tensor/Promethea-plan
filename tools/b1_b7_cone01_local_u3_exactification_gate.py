#!/usr/bin/env python3
"""Local-U3 exactification gate for B1/B7 cone_01 reduced-CNOT packets.

T-B1-004ag showed that the reduced-CNOT packet candidates are numerically
consistent only by introducing arbitrary local U3 layers. This gate tests the
cheapest exactification route: project those local U3 parameters to the pi/4
grid and replay the packet targets again.

The result is intentionally conservative. Direct pi/4 snapping is a useful
negative test, but it is not a symbolic exact decomposition, not an absorption
certificate, and not a B7 ledger reduction.
"""

from __future__ import annotations

import argparse
import json
import math
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
from b1_b7_cone01_packet_synthesis_search_gate import (
    EXACT_TOLERANCE,
    first_cnot_orientation,
    residual_norm,
    scaffold_unitary,
    target_matrix,
)


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_PACKET_PATH = ROOT / "results" / "B1_B7_cone01_semantic_replay_packet_gate_v0.json"
SYNTHESIS_PATH = ROOT / "results" / "B1_B7_cone01_packet_synthesis_search_gate_v0.json"
RESOURCE_PATH = ROOT / "results" / "B1_B7_cone01_packet_replay_resource_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_local_u3_exactification_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_local_u3_exactification_gate.md"

METHOD = "b1_b7_cone01_local_u3_exactification_gate_v0"
STATUS = "cone01_local_u3_exactification_negative_gate"
MODEL_STATUS = "pi_over_four_snapping_fails_to_absorb_reduced_cnot_local_u3_burden"
ANGLE_TOLERANCE = 1e-6


def is_pi_over_four_grid(value: float) -> bool:
    return abs(value - round(value / (math.pi / 4.0)) * (math.pi / 4.0)) <= ANGLE_TOLERANCE


def snap_to_pi_over_four(value: float) -> float:
    return float(round(value / (math.pi / 4.0)) * (math.pi / 4.0))


def wrap_angle(value: float) -> float:
    return float((value + math.pi) % (2.0 * math.pi) - math.pi)


def best_exact_scaffold(row: dict[str, Any]) -> dict[str, Any] | None:
    exact_rows = [item for item in row.get("scaffold_results", []) if item.get("exact_pass") is True]
    if not exact_rows:
        return None
    return min(exact_rows, key=lambda item: int(item["cnot_count"]))


def parameter_stats(values: list[float]) -> dict[str, int]:
    off_grid = sum(0 if is_pi_over_four_grid(value) else 1 for value in values)
    nonzero = sum(1 if abs(value) > 1e-7 else 0 for value in values)
    return {
        "parameter_count": len(values),
        "nonzero_parameter_count": nonzero,
        "off_pi_over_four_parameter_count": off_grid,
    }


def analyze_row(
    packet: dict[str, Any],
    synthesis_row: dict[str, Any],
    resource_row: dict[str, Any],
) -> dict[str, Any]:
    exact = best_exact_scaffold(synthesis_row)
    if exact is None:
        raise ValueError(f"missing exact reduced scaffold for line {packet['candidate_line_number']}")

    original_parameters = [float(value) for value in exact["best"]["wrapped_parameters"]]
    snapped_parameters = [wrap_angle(snap_to_pi_over_four(value)) for value in original_parameters]
    matrix = target_matrix(packet)
    control, target_qubit = first_cnot_orientation(packet)
    snapped_unitary = scaffold_unitary(
        np.array(snapped_parameters, dtype=float),
        int(exact["cnot_count"]),
        control,
        target_qubit,
    )
    snapped_residual = residual_norm(snapped_unitary, matrix)
    original_residual = float(exact["best"]["residual_norm"])
    exactification_pass = snapped_residual <= EXACT_TOLERANCE
    original_stats = parameter_stats(original_parameters)
    snapped_stats = parameter_stats(snapped_parameters)
    projected_count = original_stats["off_pi_over_four_parameter_count"]

    return {
        "pattern_id": packet["pattern_id"],
        "candidate_line_number": int(packet["candidate_line_number"]),
        "window_start_line": int(packet["window_start_line"]),
        "window_end_line": int(packet["window_end_line"]),
        "support_qubits": packet["support_qubits"],
        "source_cnot_count": int(packet["cx_count"]),
        "replacement_cnot_count": int(exact["cnot_count"]),
        "candidate_cnot_reduction": int(packet["cx_count"]) - int(exact["cnot_count"]),
        "original_residual_norm": original_residual,
        "snapped_residual_norm": snapped_residual,
        "residual_increase": snapped_residual - original_residual,
        "exactification_pass": exactification_pass,
        "original_parameter_stats": original_stats,
        "snapped_parameter_stats": snapped_stats,
        "projected_off_pi_over_four_parameter_count": projected_count,
        "source_off_pi_over_four_parameter_count": int(
            resource_row["source_off_pi_over_four_parameter_count"]
        ),
        "replacement_off_pi_over_four_parameter_count": int(
            resource_row["replacement_off_pi_over_four_parameter_count"]
        ),
        "replacement_off_grid_proxy_t_pressure": int(
            resource_row["replacement_off_grid_proxy_t_pressure"]
        ),
        "direct_pi_over_four_snap_replay_accepted": False,
        "local_u3_absorption_certificate_accepted": False,
        "accepted_full_circuit_replay_certificate": False,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "rejection_reason": (
            "Direct pi/4 snapping removes off-grid local-U3 parameters only by breaking the "
            "bounded packet replay beyond the exactness tolerance."
        ),
    }


def build_payload() -> dict[str, Any]:
    semantic = load_json(SEMANTIC_PACKET_PATH)
    synthesis = load_json(SYNTHESIS_PATH)
    resource = load_json(RESOURCE_PATH)
    synthesis_by_line = {
        int(row["candidate_line_number"]): row
        for row in synthesis.get("packet_synthesis_rows", [])
    }
    resource_by_line = {
        int(row["candidate_line_number"]): row
        for row in resource.get("packet_replay_resource_rows", [])
    }
    rows = [
        analyze_row(
            packet,
            synthesis_by_line[int(packet["candidate_line_number"])],
            resource_by_line[int(packet["candidate_line_number"])],
        )
        for packet in semantic.get("semantic_replay_packets", [])
    ]

    snap_pass_count = sum(1 for row in rows if row["exactification_pass"])
    accepted_removed = sum(row["accepted_occurrence_removal"] for row in rows)
    replacement_off_grid = sum(row["replacement_off_pi_over_four_parameter_count"] for row in rows)
    source_off_grid = sum(row["source_off_pi_over_four_parameter_count"] for row in rows)
    summary = {
        "source_semantic_method": semantic.get("method"),
        "source_synthesis_method": synthesis.get("method"),
        "source_resource_method": resource.get("method"),
        "packet_count": len(rows),
        "pi_over_four_snap_packet_count": len(rows),
        "exact_snap_pass_count": snap_pass_count,
        "exact_snap_fail_count": len(rows) - snap_pass_count,
        "min_snapped_residual_norm": min(row["snapped_residual_norm"] for row in rows),
        "max_snapped_residual_norm": max(row["snapped_residual_norm"] for row in rows),
        "candidate_cnot_reduction_if_accepted": sum(
            row["candidate_cnot_reduction"] for row in rows
        ),
        "source_off_pi_over_four_parameter_count": source_off_grid,
        "replacement_off_pi_over_four_parameter_count": replacement_off_grid,
        "projected_off_pi_over_four_parameter_count": sum(
            row["projected_off_pi_over_four_parameter_count"] for row in rows
        ),
        "snapped_remaining_off_pi_over_four_parameter_count": sum(
            row["snapped_parameter_stats"]["off_pi_over_four_parameter_count"] for row in rows
        ),
        "exactified_off_pi_over_four_parameter_count": 0,
        "residual_resource_burden_parameter_count": replacement_off_grid,
        "replacement_off_grid_proxy_t_pressure": replacement_off_grid * PROXY_T_PER_OCCURRENCE,
        "accepted_local_u3_exactification_count": 0,
        "accepted_absorption_certificate_count": 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(
            0,
            (REQUIRED_OCCURRENCE_REMOVALS - accepted_removed) * PROXY_T_PER_OCCURRENCE,
        ),
        "direct_pi_over_four_snap_claimed_exact": False,
        "local_u3_absorption_claimed": False,
        "symbolic_exact_decomposition_claimed": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
    }
    payload = {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "workload": semantic.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "source_semantic_packet_result": display_path(SEMANTIC_PACKET_PATH),
        "source_packet_synthesis_result": display_path(SYNTHESIS_PATH),
        "source_packet_replay_resource_result": display_path(RESOURCE_PATH),
        "summary": summary,
        "local_u3_exactification_rows": rows,
        "claim_boundary": {
            "supported_claim": (
                "Direct pi/4 snapping of the reduced-CNOT local-U3 replacement parameters was "
                "tested against the three bounded packet targets and failed the exactness gate."
            ),
            "unsupported_claims": [
                "No snapped local-U3 replacement is accepted as exact.",
                "No local-U3 absorption certificate is produced.",
                "No full-circuit replay certificate or B7 ledger reduction is accepted.",
            ],
            "direct_pi_over_four_snap_claimed_exact": False,
            "local_u3_absorption_claimed": False,
            "symbolic_exact_decomposition_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }
    payload["summary"]["validation_error_count"] = len(validate_payload(payload))
    return payload


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload.get("summary", {})
    rows = payload.get("local_u3_exactification_rows", [])
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if len(rows) != 3:
        errors.append("row_count_must_be_3")
    expected = {
        "packet_count": 3,
        "pi_over_four_snap_packet_count": 3,
        "exact_snap_pass_count": 0,
        "exact_snap_fail_count": 3,
        "candidate_cnot_reduction_if_accepted": 9,
        "source_off_pi_over_four_parameter_count": 1,
        "replacement_off_pi_over_four_parameter_count": 40,
        "projected_off_pi_over_four_parameter_count": 40,
        "snapped_remaining_off_pi_over_four_parameter_count": 0,
        "exactified_off_pi_over_four_parameter_count": 0,
        "residual_resource_burden_parameter_count": 40,
        "replacement_off_grid_proxy_t_pressure": 800,
        "accepted_local_u3_exactification_count": 0,
        "accepted_absorption_certificate_count": 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
    }
    for field, expected_value in expected.items():
        if summary.get(field) != expected_value:
            errors.append(f"{field}_expected_{expected_value}_got_{summary.get(field)}")
    for field in [
        "direct_pi_over_four_snap_claimed_exact",
        "local_u3_absorption_claimed",
        "symbolic_exact_decomposition_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field}_must_be_false")
        if payload.get("claim_boundary", {}).get(field) is not False:
            errors.append(f"claim_boundary_{field}_must_be_false")
    if summary.get("min_snapped_residual_norm", 0.0) <= EXACT_TOLERANCE:
        errors.append("min_snapped_residual_must_fail_exact_tolerance")
    for row in rows:
        line = row.get("candidate_line_number")
        if row.get("exactification_pass") is not False:
            errors.append(f"{line}_exactification_must_fail")
        if row.get("snapped_parameter_stats", {}).get("off_pi_over_four_parameter_count") != 0:
            errors.append(f"{line}_snapped_parameters_must_be_on_grid")
        if row.get("direct_pi_over_four_snap_replay_accepted") is not False:
            errors.append(f"{line}_direct_snap_replay_must_not_be_accepted")
        if row.get("local_u3_absorption_certificate_accepted") is not False:
            errors.append(f"{line}_absorption_certificate_must_not_be_accepted")
        if row.get("accepted_occurrence_removal") != 0:
            errors.append(f"{line}_accepted_occurrence_removal_must_be_zero")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Local-U3 Exactification Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004af/T-B1-004ag and tests whether the arbitrary local-U3 replacement layers can be cheaply exactified by direct pi/4-grid snapping.",
        "",
        "## Summary",
        "",
        f"- Packets checked: `{summary['packet_count']}`",
        f"- Exact pi/4-snap passes/fails: `{summary['exact_snap_pass_count']}` / `{summary['exact_snap_fail_count']}`",
        f"- Snapped residual range: `{summary['min_snapped_residual_norm']:.6e}` - `{summary['max_snapped_residual_norm']:.6e}`",
        f"- Candidate CNOT reduction if accepted: `{summary['candidate_cnot_reduction_if_accepted']}`",
        f"- Replacement off-grid local-U3 parameters before snapping: `{summary['replacement_off_pi_over_four_parameter_count']}`",
        f"- Accepted exactified off-grid parameters: `{summary['exactified_off_pi_over_four_parameter_count']}`",
        f"- Residual resource-burden parameters: `{summary['residual_resource_burden_parameter_count']}`",
        f"- Accepted occurrence/proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Packet Rows",
        "",
        "| Candidate line | Replacement CX | Projected off-grid params | Snapped residual | Exact pass | Accepted absorption |",
        "|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["local_u3_exactification_rows"]:
        lines.append(
            f"| {row['candidate_line_number']} | {row['replacement_cnot_count']} | "
            f"{row['projected_off_pi_over_four_parameter_count']} | "
            f"{row['snapped_residual_norm']:.6e} | "
            f"{row['exactification_pass']} | "
            f"{row['local_u3_absorption_certificate_accepted']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Direct pi/4 snapping does put the replacement local-U3 parameters on the cheap grid, but it breaks the bounded packet replay for all three packets. Therefore this artifact does not accept the reduced-CNOT route as a symbolic exact decomposition, an absorption certificate, a full-circuit rewrite, or a B7 ledger improvement.",
            "",
            "## Next Required Gate",
            "",
            "The next route must use a stronger exact synthesis/absorption mechanism than direct snapping, or abandon this reduced-CNOT scaffold and search for an occurrence-removing route that lowers the actual gcm_h6 B7 ledger.",
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
