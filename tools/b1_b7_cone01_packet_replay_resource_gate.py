#!/usr/bin/env python3
"""Full-circuit replay/resource accounting gate for B1/B7 cone_01 packets.

T-B1-004af found numerical reduced-CNOT packet candidates. This gate asks the
next, stricter question: can those candidates be accepted as B7-relevant
replays after pricing the arbitrary local U3 layers they introduce?

The answer is deliberately conservative. The packet matrices replay
numerically inside their bounded two-qubit windows, but the replacement
scaffolds introduce many off-pi/4 local-U3 parameters. That resource burden is
not an accepted fault-tolerant saving, so B7 ledger reduction remains zero.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    eval_angle_expr,
    load_json,
    write_json,
    write_text,
)


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_PACKET_PATH = ROOT / "results" / "B1_B7_cone01_semantic_replay_packet_gate_v0.json"
SYNTHESIS_PATH = ROOT / "results" / "B1_B7_cone01_packet_synthesis_search_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_packet_replay_resource_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_packet_replay_resource_gate.md"

METHOD = "b1_b7_cone01_packet_replay_resource_gate_v0"
STATUS = "cone01_packet_replay_resource_accounting_rejects_ledger_acceptance"
MODEL_STATUS = "reduced_cnot_packet_candidates_fail_local_u3_resource_accounting"
ANGLE_TOLERANCE = 1e-6


def is_pi_over_four_grid(raw_angle: str) -> bool:
    value = eval_angle_expr(raw_angle)
    return abs(value - round(value / (math.pi / 4.0)) * (math.pi / 4.0)) <= ANGLE_TOLERANCE


def source_parameter_stats(packet: dict[str, Any]) -> dict[str, int]:
    parameter_count = 0
    off_grid_count = 0
    single_qubit_gate_count = 0
    for op in packet.get("normalized_ops", []):
        raw_args = op.get("raw_args")
        if not raw_args:
            continue
        single_qubit_gate_count += 1
        parameter_count += len(raw_args)
        off_grid_count += sum(0 if is_pi_over_four_grid(raw_arg) else 1 for raw_arg in raw_args)
    return {
        "source_single_qubit_gate_count": single_qubit_gate_count,
        "source_parameter_count": parameter_count,
        "source_off_pi_over_four_parameter_count": off_grid_count,
        "source_off_grid_proxy_t_pressure": off_grid_count * PROXY_T_PER_OCCURRENCE,
    }


def best_exact_scaffold(row: dict[str, Any]) -> dict[str, Any] | None:
    exact_rows = [item for item in row.get("scaffold_results", []) if item.get("exact_pass") is True]
    if not exact_rows:
        return None
    return min(exact_rows, key=lambda item: int(item["cnot_count"]))


def analyze_row(packet: dict[str, Any], synthesis_row: dict[str, Any]) -> dict[str, Any]:
    exact = best_exact_scaffold(synthesis_row)
    source_stats = source_parameter_stats(packet)
    source_cnot = int(packet["cx_count"])
    source_window_gate_count = len(packet.get("normalized_ops", []))

    if exact is None:
        replacement_cnot = None
        replacement_local_u3_gates = 0
        replacement_parameter_count = 0
        replacement_off_grid_parameters = 0
        cnot_reduction = 0
        bounded_packet_replay_numerically_consistent = False
        max_abs_entry_error = None
        residual_norm = None
    else:
        replacement_cnot = int(exact["cnot_count"])
        replacement_local_u3_gates = int(exact["local_u3_layer_count"]) * 2
        replacement_parameter_count = int(exact["parameter_count"])
        replacement_off_grid_parameters = int(
            exact["best"]["parameter_stats"]["off_pi_over_four_grid_parameter_count"]
        )
        cnot_reduction = source_cnot - replacement_cnot
        bounded_packet_replay_numerically_consistent = bool(exact.get("exact_pass"))
        max_abs_entry_error = float(exact["best"]["max_abs_entry_error"])
        residual_norm = float(exact["best"]["residual_norm"])

    replacement_off_grid_proxy_t = replacement_off_grid_parameters * PROXY_T_PER_OCCURRENCE
    incremental_off_grid_parameters = (
        replacement_off_grid_parameters - source_stats["source_off_pi_over_four_parameter_count"]
    )
    incremental_proxy_t_pressure = (
        replacement_off_grid_proxy_t - source_stats["source_off_grid_proxy_t_pressure"]
    )
    local_u3_resource_burden_detected = incremental_proxy_t_pressure > 0
    accepted = False

    return {
        "pattern_id": packet["pattern_id"],
        "candidate_line_number": int(packet["candidate_line_number"]),
        "window_start_line": int(packet["window_start_line"]),
        "window_end_line": int(packet["window_end_line"]),
        "support_qubits": packet["support_qubits"],
        "source_window_gate_count": source_window_gate_count,
        "source_cnot_count": source_cnot,
        **source_stats,
        "replacement_cnot_count": replacement_cnot,
        "replacement_local_u3_gate_count": replacement_local_u3_gates,
        "replacement_parameter_count": replacement_parameter_count,
        "replacement_off_pi_over_four_parameter_count": replacement_off_grid_parameters,
        "replacement_off_grid_proxy_t_pressure": replacement_off_grid_proxy_t,
        "candidate_cnot_reduction": cnot_reduction,
        "local_u3_gate_delta": replacement_local_u3_gates
        - source_stats["source_single_qubit_gate_count"],
        "parameter_count_delta": replacement_parameter_count - source_stats["source_parameter_count"],
        "off_grid_parameter_delta": incremental_off_grid_parameters,
        "incremental_proxy_t_pressure": incremental_proxy_t_pressure,
        "local_u3_resource_burden_detected": local_u3_resource_burden_detected,
        "bounded_packet_replay_numerically_consistent": bounded_packet_replay_numerically_consistent,
        "max_abs_entry_error": max_abs_entry_error,
        "residual_norm": residual_norm,
        "accepted_full_circuit_replay_certificate": accepted,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "resource_accounting_rejection_reason": (
            "The reduced-CNOT packet candidate is numerically consistent, but its arbitrary local "
            "U3 layers add off-grid synthesis pressure that is not accepted by the current B7 ledger."
        ),
    }


def build_payload() -> dict[str, Any]:
    semantic = load_json(SEMANTIC_PACKET_PATH)
    synthesis = load_json(SYNTHESIS_PATH)
    synthesis_by_line = {
        int(row["candidate_line_number"]): row
        for row in synthesis.get("packet_synthesis_rows", [])
    }
    rows = [
        analyze_row(packet, synthesis_by_line[int(packet["candidate_line_number"])])
        for packet in semantic.get("semantic_replay_packets", [])
    ]

    accepted_removed = sum(row["accepted_occurrence_removal"] for row in rows)
    total_replacement_off_grid = sum(
        row["replacement_off_pi_over_four_parameter_count"] for row in rows
    )
    total_source_off_grid = sum(row["source_off_pi_over_four_parameter_count"] for row in rows)
    total_incremental_proxy_t = sum(row["incremental_proxy_t_pressure"] for row in rows)
    total_candidate_cnot_reduction = sum(row["candidate_cnot_reduction"] for row in rows)
    replay_consistent_count = sum(
        1 for row in rows if row["bounded_packet_replay_numerically_consistent"]
    )
    burden_count = sum(1 for row in rows if row["local_u3_resource_burden_detected"])
    accepted_replay_count = sum(
        1 for row in rows if row["accepted_full_circuit_replay_certificate"]
    )

    summary = {
        "source_semantic_method": semantic.get("method"),
        "source_synthesis_method": synthesis.get("method"),
        "packet_count": len(rows),
        "bounded_packet_replay_numerically_consistent_count": replay_consistent_count,
        "candidate_cnot_reduction_if_accepted": total_candidate_cnot_reduction,
        "source_off_pi_over_four_parameter_count": total_source_off_grid,
        "replacement_local_u3_gate_count": sum(row["replacement_local_u3_gate_count"] for row in rows),
        "replacement_parameter_count": sum(row["replacement_parameter_count"] for row in rows),
        "replacement_off_pi_over_four_parameter_count": total_replacement_off_grid,
        "incremental_off_pi_over_four_parameter_count": total_replacement_off_grid
        - total_source_off_grid,
        "source_off_grid_proxy_t_pressure": total_source_off_grid * PROXY_T_PER_OCCURRENCE,
        "replacement_off_grid_proxy_t_pressure": total_replacement_off_grid
        * PROXY_T_PER_OCCURRENCE,
        "incremental_proxy_t_pressure": total_incremental_proxy_t,
        "local_u3_resource_burden_packet_count": burden_count,
        "accepted_full_circuit_replay_certificate_count": accepted_replay_count,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": sum(row["accepted_proxy_t_reduction"] for row in rows),
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(
            0,
            (REQUIRED_OCCURRENCE_REMOVALS - accepted_removed) * PROXY_T_PER_OCCURRENCE,
        ),
        "candidate_accepted_after_resource_accounting": accepted_replay_count == len(rows) and len(rows) > 0,
        "bounded_packet_replay_claimed_as_full_circuit_certificate": False,
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
        "summary": summary,
        "packet_replay_resource_rows": rows,
        "claim_boundary": {
            "supported_claim": (
                "The T-B1-004af reduced-CNOT packet candidates replay the bounded two-qubit packet "
                "matrices numerically, but resource accounting rejects them as B7 ledger savings."
            ),
            "unsupported_claims": [
                "No full-circuit QASM replacement certificate is accepted.",
                "No symbolic exact decomposition is produced.",
                "No B7 proxy-T or occurrence reduction is accepted.",
            ],
            "bounded_packet_replay_claimed_as_full_circuit_certificate": False,
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
    rows = payload.get("packet_replay_resource_rows", [])
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if len(rows) != 3:
        errors.append("packet_row_count_must_be_3")
    expected = {
        "packet_count": 3,
        "bounded_packet_replay_numerically_consistent_count": 3,
        "candidate_cnot_reduction_if_accepted": 9,
        "source_off_pi_over_four_parameter_count": 1,
        "replacement_local_u3_gate_count": 16,
        "replacement_parameter_count": 48,
        "replacement_off_pi_over_four_parameter_count": 40,
        "incremental_off_pi_over_four_parameter_count": 39,
        "source_off_grid_proxy_t_pressure": 20,
        "replacement_off_grid_proxy_t_pressure": 800,
        "incremental_proxy_t_pressure": 780,
        "local_u3_resource_burden_packet_count": 3,
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
        "candidate_accepted_after_resource_accounting",
        "bounded_packet_replay_claimed_as_full_circuit_certificate",
        "symbolic_exact_decomposition_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field}_must_be_false")
        if payload.get("claim_boundary", {}).get(field) is not False and field != "candidate_accepted_after_resource_accounting":
            errors.append(f"claim_boundary_{field}_must_be_false")
    for row in rows:
        if row.get("bounded_packet_replay_numerically_consistent") is not True:
            errors.append(f"{row.get('candidate_line_number')}_bounded_replay_must_be_true")
        if row.get("local_u3_resource_burden_detected") is not True:
            errors.append(f"{row.get('candidate_line_number')}_resource_burden_must_be_true")
        if row.get("accepted_full_circuit_replay_certificate") is not False:
            errors.append(f"{row.get('candidate_line_number')}_accepted_replay_must_be_false")
        if row.get("accepted_occurrence_removal") != 0:
            errors.append(f"{row.get('candidate_line_number')}_accepted_removal_must_be_zero")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Packet Replay Resource Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004ae/T-B1-004af and asks whether the reduced-CNOT packet candidates can be accepted after local-U3 resource accounting.",
        "",
        "## Summary",
        "",
        f"- Packets checked: `{summary['packet_count']}`",
        f"- Bounded packet replay numerically consistent: `{summary['bounded_packet_replay_numerically_consistent_count']}`",
        f"- Candidate CNOT reduction if accepted: `{summary['candidate_cnot_reduction_if_accepted']}`",
        f"- Source off-grid parameter count: `{summary['source_off_pi_over_four_parameter_count']}`",
        f"- Replacement local U3 gates / parameters / off-grid parameters: `{summary['replacement_local_u3_gate_count']}` / `{summary['replacement_parameter_count']}` / `{summary['replacement_off_pi_over_four_parameter_count']}`",
        f"- Incremental off-grid parameters / proxy-T pressure: `{summary['incremental_off_pi_over_four_parameter_count']}` / `{summary['incremental_proxy_t_pressure']}`",
        f"- Accepted full-circuit replay certificates: `{summary['accepted_full_circuit_replay_certificate_count']}`",
        f"- Accepted occurrence/proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Packet Rows",
        "",
        "| Candidate line | Source CX | Replacement CX | CNOT delta | Source off-grid params | Replacement off-grid params | Incremental proxy-T pressure | Accepted replay |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["packet_replay_resource_rows"]:
        lines.append(
            f"| {row['candidate_line_number']} | {row['source_cnot_count']} | "
            f"{row['replacement_cnot_count']} | {row['candidate_cnot_reduction']} | "
            f"{row['source_off_pi_over_four_parameter_count']} | "
            f"{row['replacement_off_pi_over_four_parameter_count']} | "
            f"{row['incremental_proxy_t_pressure']} | "
            f"{row['accepted_full_circuit_replay_certificate']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The reduced-CNOT packet candidates are useful synthesis evidence, but they are not accepted B7 savings. The local U3 replacements introduce off-grid synthesis pressure that is larger than the off-grid burden in the source windows, and no symbolic exact decomposition or full-circuit QASM replay certificate has been emitted.",
            "",
            "## Next Required Gate",
            "",
            "The next route must either exactify the local U3 layers into a cheaper Clifford+T/native basis, absorb them into surrounding circuit context with replay certificates, or abandon this reduced-CNOT scaffold in favor of a route that lowers the actual B7 ledger.",
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
