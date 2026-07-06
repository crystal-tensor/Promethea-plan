#!/usr/bin/env python3
"""T-B1-004dk/T-B7-012t: R9 R1 reroute-pressure gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r9_r1_reroute_pressure_gate_v0"
STATUS = "cone01_r9_r1_reroute_pressure_not_checked_negative_lemma"
MODEL_STATUS = "r1_line1381_evidence_pressures_reroute_but_no_checked_negative_lemma"
VERSION = "0.1"
TARGET_ID = "T-B1-004dk/T-B7-012t"
PACKET_ID = "B1-B7-cone01-R9-R1-reroute-pressure"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def stable_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def source_row(path: Path, data: dict[str, Any], summary_keys: list[str]) -> dict[str, Any]:
    summary = data.get("summary", {})
    return {
        "path": str(path),
        "sha256": file_hash(path),
        "method": data.get("method"),
        "status": data.get("status"),
        "validation_error_count": summary.get("validation_error_count"),
        "summary": {key: summary.get(key) for key in summary_keys},
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r8 = load_json(args.r8_preflight)
    exact = load_json(args.exact_decomposition)
    context1 = load_json(args.context_absorption)
    context23 = load_json(args.multi_rotation_context)
    context4 = load_json(args.four_rotation_context)
    context5 = load_json(args.five_rotation_context)
    corridor = load_json(args.commutation_corridor)
    physical = load_json(args.physical_pricing)
    leave_paths = [
        args.leave_one,
        args.leave_two,
        args.leave_three,
        args.leave_four,
        args.leave_five,
    ]
    leave_data = [load_json(path) for path in leave_paths]

    r8s = r8["summary"]
    exacts = exact["summary"]
    c1s = context1["summary"]
    c23s = context23["summary"]
    c4s = context4["summary"]
    c5s = context5["summary"]
    cors = corridor["summary"]
    phys = physical["summary"]

    leave_attempt_rows = []
    total_leave_rows = 0
    total_leave_passes = 0
    total_leave_failures = 0
    for path, data in zip(leave_paths, leave_data):
        summary = data["summary"]
        row_count = (
            summary.get("leave_one_out_row_count")
            or summary.get("leave_two_out_row_count")
            or summary.get("leave_three_out_row_count")
            or summary.get("leave_four_out_row_count")
            or summary.get("leave_five_out_row_count")
            or 0
        )
        pass_count = (
            summary.get("leave_one_out_exact_pass_count")
            or summary.get("leave_two_out_exact_pass_count")
            or summary.get("leave_three_out_exact_pass_count")
            or summary.get("leave_four_out_exact_pass_count")
            or summary.get("leave_five_out_exact_pass_count")
            or 0
        )
        fail_count = (
            summary.get("leave_one_out_exact_fail_count")
            or summary.get("leave_two_out_exact_fail_count")
            or summary.get("leave_three_out_exact_fail_count")
            or summary.get("leave_four_out_exact_fail_count")
            or summary.get("leave_five_out_exact_fail_count")
            or 0
        )
        total_leave_rows += row_count
        total_leave_passes += pass_count
        total_leave_failures += fail_count
        leave_attempt_rows.append(
            source_row(
                path,
                data,
                [
                    "current_off_grid_parameter_count",
                    "current_off_grid_parameter_indices",
                    "exact_tolerance",
                    "accepted_occurrence_removal",
                    "accepted_proxy_t_reduction",
                    "line1381_off_grid_parameters_eliminated",
                    "line1381_off_grid_parameters_absorbed",
                    "line1381_off_grid_parameters_symbolically_decomposed",
                ],
            )
            | {
                "row_count": row_count,
                "exact_pass_count": pass_count,
                "exact_fail_count": fail_count,
            }
        )

    context_attempts = [
        source_row(
            args.context_absorption,
            context1,
            [
                "context_grid_cancellation_exact_parameter_count",
                "context_rotation_argument_count",
                "min_best_context_grid_cancellation_error",
                "max_best_context_grid_cancellation_error",
                "accepted_context_absorption_certificate_count",
            ],
        )
        | {"widths": [1], "exact_absorption_parameter_count": c1s.get("context_grid_cancellation_exact_parameter_count")},
        source_row(
            args.multi_rotation_context,
            context23,
            [
                "width2_exact_absorption_parameter_count",
                "width3_exact_absorption_parameter_count",
                "width2_signed_combination_count_per_parameter",
                "width3_signed_combination_count_per_parameter",
                "min_best_width3_context_grid_error",
                "accepted_multi_rotation_context_absorption_count",
            ],
        )
        | {
            "widths": [2, 3],
            "exact_absorption_parameter_count": c23s.get(
                "two_or_three_rotation_exact_absorption_parameter_count"
            ),
        },
        source_row(
            args.four_rotation_context,
            context4,
            [
                "width4_exact_absorption_parameter_count",
                "width4_signed_combination_count_per_parameter",
                "min_best_width4_context_grid_error",
                "accepted_four_rotation_context_absorption_count",
            ],
        )
        | {"widths": [4], "exact_absorption_parameter_count": c4s.get("width4_exact_absorption_parameter_count")},
        source_row(
            args.five_rotation_context,
            context5,
            [
                "width5_exact_absorption_parameter_count",
                "width5_signed_combination_count_per_parameter",
                "min_best_width5_context_grid_error",
                "accepted_five_rotation_context_absorption_count",
            ],
        )
        | {"widths": [5], "exact_absorption_parameter_count": c5s.get("width5_exact_absorption_parameter_count")},
    ]
    context_widths_tested = [1, 2, 3, 4, 5]
    total_context_exact_absorptions = sum(
        int(row.get("exact_absorption_parameter_count") or 0) for row in context_attempts
    )
    min_context_grid_error = min(
        value
        for value in [
            c1s.get("min_best_context_grid_cancellation_error"),
            c23s.get("min_best_width3_context_grid_error"),
            c4s.get("min_best_width4_context_grid_error"),
            c5s.get("min_best_width5_context_grid_error"),
        ]
        if value is not None
    )
    total_width5_virtual_tests = (
        int(c5s.get("tested_remaining_parameter_count") or 0)
        * int(c5s.get("width5_signed_combination_count_per_parameter") or 0)
    )

    pressure_packet = {
        "packet_id": PACKET_ID,
        "source_target_id": TARGET_ID,
        "source_r8_preflight": str(args.r8_preflight),
        "r8_preflight_hash": r8s.get("preflight_hash"),
        "route_a_passed": r8s.get("route_a_passed"),
        "route_b_passed": r8s.get("route_b_passed"),
        "parameter_removal_pressure": {
            "leave_attempt_family_count": len(leave_attempt_rows),
            "leave_attempt_row_count": total_leave_rows,
            "leave_attempt_exact_pass_count": total_leave_passes,
            "leave_attempt_exact_fail_count": total_leave_failures,
            "rows": leave_attempt_rows,
        },
        "exact_decomposition_pressure": source_row(
            args.exact_decomposition,
            exact,
            [
                "tested_remaining_parameter_count",
                "remaining_off_grid_parameter_count",
                "accepted_exact_decomposition_parameter_count",
                "accepted_symbolic_decomposition_count",
                "accepted_source_absorption_count",
            ],
        ),
        "context_absorption_pressure": {
            "context_widths_tested": context_widths_tested,
            "total_context_exact_absorption_parameter_count": total_context_exact_absorptions,
            "min_context_grid_error": min_context_grid_error,
            "width5_virtual_test_count": total_width5_virtual_tests,
            "rows": context_attempts,
        },
        "commutation_corridor_pressure": source_row(
            args.commutation_corridor,
            corridor,
            [
                "best_context_candidate_count",
                "accepted_commutation_corridor_replay_candidate_count",
                "candidate_all_references_corridor_accepted_count",
                "blocked_corridor_reference_count",
            ],
        ),
        "physical_pricing_pressure": source_row(
            args.physical_pricing,
            physical,
            [
                "physical_synthesis_cost_minus_selected_cnot_credit",
                "total_physical_synthesis_t_count_bound",
                "selected_cnot_delta_proxy_credit",
                "placeholder_proxy_t_pressure",
                "physical_synthesis_pricing_accepted",
            ],
        ),
        "reroute_decision": {
            "reroute_allowed": False,
            "checked_negative_lemma_present": False,
            "current_evidence_supports_pressure_note": True,
            "why_not_reroute_yet": (
                "The current evidence rejects many concrete R1 subroutes, but it is not a checked "
                "negative lemma covering all R1 parameter-elimination, absorption, symbolic, and "
                "physical-pricing possibilities."
            ),
        },
        "next_gate": (
            "Submit a checked negative lemma artifact that binds these source hashes and states the "
            "covered R1 search domain, or submit a new R1 artifact that clears R8 Route A or Route B."
        ),
    }
    pressure_packet["pressure_hash"] = stable_hash(pressure_packet)

    requirements = [
        requirement(
            "N1",
            "R8 preflight rejects both R1 contract routes",
            r8.get("method") == "b1_b7_cone01_r8_r1_contract_preflight_gate_v0"
            and r8s.get("route_a_passed") is False
            and r8s.get("route_b_passed") is False,
            {
                "r8_method": r8.get("method"),
                "route_a_passed": r8s.get("route_a_passed"),
                "route_b_passed": r8s.get("route_b_passed"),
            },
        ),
        requirement(
            "N2",
            "Leave-out parameter removal pressure covers all nonempty removal sizes",
            len(leave_attempt_rows) == 5
            and total_leave_rows == 31
            and total_leave_passes == 0
            and total_leave_failures == 31,
            {
                "leave_attempt_family_count": len(leave_attempt_rows),
                "leave_attempt_row_count": total_leave_rows,
                "leave_attempt_exact_pass_count": total_leave_passes,
                "leave_attempt_exact_fail_count": total_leave_failures,
            },
        ),
        requirement(
            "N3",
            "Simple exact decomposition/source absorption accepts none of the five parameters",
            exacts.get("remaining_off_grid_parameter_count") == 5
            and exacts.get("accepted_exact_decomposition_parameter_count") == 0
            and exacts.get("accepted_source_absorption_count") == 0,
            {
                "remaining_off_grid_parameter_count": exacts.get("remaining_off_grid_parameter_count"),
                "accepted_exact_decomposition_parameter_count": exacts.get(
                    "accepted_exact_decomposition_parameter_count"
                ),
                "accepted_source_absorption_count": exacts.get("accepted_source_absorption_count"),
            },
        ),
        requirement(
            "N4",
            "Context absorption pressure covers widths one through five with zero exact absorptions",
            context_widths_tested == [1, 2, 3, 4, 5]
            and total_context_exact_absorptions == 0
            and total_width5_virtual_tests == 173761280,
            {
                "context_widths_tested": context_widths_tested,
                "total_context_exact_absorption_parameter_count": total_context_exact_absorptions,
                "width5_virtual_test_count": total_width5_virtual_tests,
                "min_context_grid_error": min_context_grid_error,
            },
        ),
        requirement(
            "N5",
            "Commutation-corridor pressure accepts no replay-safe candidate",
            cors.get("accepted_commutation_corridor_replay_candidate_count") == 0
            and cors.get("candidate_all_references_corridor_accepted_count") == 0,
            {
                "accepted_commutation_corridor_replay_candidate_count": cors.get(
                    "accepted_commutation_corridor_replay_candidate_count"
                ),
                "candidate_all_references_corridor_accepted_count": cors.get(
                    "candidate_all_references_corridor_accepted_count"
                ),
            },
        ),
        requirement(
            "N6",
            "Physical pricing still misses Route B by 365",
            phys.get("physical_synthesis_cost_minus_selected_cnot_credit") == 365
            and phys.get("physical_synthesis_pricing_accepted") is False,
            {
                "physical_synthesis_cost_minus_selected_cnot_credit": phys.get(
                    "physical_synthesis_cost_minus_selected_cnot_credit"
                ),
                "physical_synthesis_pricing_accepted": phys.get(
                    "physical_synthesis_pricing_accepted"
                ),
            },
        ),
        requirement(
            "N7",
            "All pressure sources are hash-bound and validation-clean",
            all(row["sha256"] for row in leave_attempt_rows)
            and all(row["validation_error_count"] == 0 for row in leave_attempt_rows)
            and all(row["validation_error_count"] == 0 for row in context_attempts)
            and pressure_packet["exact_decomposition_pressure"]["validation_error_count"] == 0
            and pressure_packet["commutation_corridor_pressure"]["validation_error_count"] == 0
            and pressure_packet["physical_pricing_pressure"]["validation_error_count"] == 0,
            {
                "leave_source_count": len(leave_attempt_rows),
                "context_source_count": len(context_attempts),
                "hash_bound": True,
            },
        ),
        requirement(
            "N8",
            "Pressure is not upgraded into a checked negative lemma or reroute decision",
            pressure_packet["reroute_decision"]["reroute_allowed"] is False
            and pressure_packet["reroute_decision"]["checked_negative_lemma_present"] is False,
            pressure_packet["reroute_decision"],
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids:
        validation_errors.append(f"unexpected R9 pressure failures: {failed_ids}")

    summary = {
        "pressure_id": PACKET_ID,
        "pressure_hash": pressure_packet["pressure_hash"],
        "r8_preflight_hash": r8s.get("preflight_hash"),
        "route_a_passed": r8s.get("route_a_passed"),
        "route_b_passed": r8s.get("route_b_passed"),
        "leave_attempt_family_count": len(leave_attempt_rows),
        "leave_attempt_row_count": total_leave_rows,
        "leave_attempt_exact_pass_count": total_leave_passes,
        "context_widths_tested": context_widths_tested,
        "total_context_exact_absorption_parameter_count": total_context_exact_absorptions,
        "width5_virtual_test_count": total_width5_virtual_tests,
        "min_context_grid_error": min_context_grid_error,
        "commutation_corridor_accepted_count": cors.get(
            "accepted_commutation_corridor_replay_candidate_count"
        ),
        "physical_cost_minus_credit": phys.get(
            "physical_synthesis_cost_minus_selected_cnot_credit"
        ),
        "reroute_allowed": False,
        "checked_negative_lemma_present": False,
        "accepted_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "source_target_id": TARGET_ID,
        "title": "B1/B7 Cone01 R9 R1 Reroute-Pressure Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "summary": summary,
        "r1_reroute_pressure_packet": pressure_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "R9 aggregates hash-bound R1 negative-pressure evidence and shows why a checked "
                "negative lemma would be valuable."
            ),
            "what_is_not_supported": (
                "No checked negative lemma, R5 reroute, submitted R1 solution, occurrence removal, "
                "proxy-T reduction, B7 credit, resource saving, or impossibility theorem is supported."
            ),
            "next_gate": pressure_packet["next_gate"],
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    packet = payload["r1_reroute_pressure_packet"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Pressure packet: `{s['pressure_id']}`",
        f"- Pressure hash: `{s['pressure_hash']}`",
        f"- R8 preflight hash: `{s['r8_preflight_hash']}`",
        "",
        "## Result",
        "",
        (
            f"The R9 reroute-pressure gate passes {s['requirements_passed']}/{s['requirement_count']} "
            "requirements. It aggregates negative pressure against the current R1 route, but does not "
            "upgrade that pressure into a checked negative lemma or an R5 reroute."
        ),
        "",
        "## Pressure Evidence",
        "",
        f"- Leave-out parameter removal families / rows / exact passes: `{s['leave_attempt_family_count']}` / `{s['leave_attempt_row_count']}` / `{s['leave_attempt_exact_pass_count']}`",
        f"- Context widths tested: `{s['context_widths_tested']}`",
        f"- Width-5 virtual tests: `{s['width5_virtual_test_count']}`",
        f"- Total context exact absorption parameter count: `{s['total_context_exact_absorption_parameter_count']}`",
        f"- Best context grid error: `{s['min_context_grid_error']}`",
        f"- Commutation-corridor accepted candidates: `{s['commutation_corridor_accepted_count']}`",
        f"- Physical cost-minus-credit: `{s['physical_cost_minus_credit']}`",
        "",
        "## Reroute Decision",
        "",
        f"- Reroute allowed: `{s['reroute_allowed']}`",
        f"- Checked negative lemma present: `{s['checked_negative_lemma_present']}`",
        f"- Why not reroute yet: {packet['reroute_decision']['why_not_reroute_yet']}",
        "",
        "## Next Gate",
        "",
        packet["next_gate"],
        "",
        "## Requirement Results",
        "",
    ]
    for row in payload["requirements"]:
        marker = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- `{row['requirement_id']}` {marker}: {row['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            "This reroute-pressure gate does not claim resource saving, occurrence removal, proxy-T reduction, B7 ledger improvement, FT resource credit, a checked impossibility theorem, an R5 reroute, or a solved B1/B7 problem.",
            "",
            "## Validation",
            "",
            f"- validation_error_count: `{s['validation_error_count']}`",
        ]
    )
    for error in payload["validation_errors"]:
        lines.append(f"- {error}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--r8-preflight",
        type=Path,
        default=Path("results/B1_B7_cone01_R8_r1_contract_preflight_gate_v0.json"),
    )
    parser.add_argument(
        "--exact-decomposition",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_exact_decomposition_pressure_gate_v0.json"),
    )
    parser.add_argument(
        "--context-absorption",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_context_absorption_gate_v0.json"),
    )
    parser.add_argument(
        "--multi-rotation-context",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_multi_rotation_context_gate_v0.json"),
    )
    parser.add_argument(
        "--four-rotation-context",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_four_rotation_context_gate_v0.json"),
    )
    parser.add_argument(
        "--five-rotation-context",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_five_rotation_context_gate_v0.json"),
    )
    parser.add_argument(
        "--commutation-corridor",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_commutation_corridor_gate_v0.json"),
    )
    parser.add_argument(
        "--physical-pricing",
        type=Path,
        default=Path("results/B1_B7_cone01_physical_synthesis_pricing_gate_v0.json"),
    )
    parser.add_argument(
        "--leave-one",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_leave_one_out_parameter_gate_v0.json"),
    )
    parser.add_argument(
        "--leave-two",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_leave_two_out_parameter_gate_v0.json"),
    )
    parser.add_argument(
        "--leave-three",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_leave_three_out_parameter_gate_v0.json"),
    )
    parser.add_argument(
        "--leave-four",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_leave_four_out_parameter_gate_v0.json"),
    )
    parser.add_argument(
        "--leave-five",
        type=Path,
        default=Path("results/B1_B7_cone01_line1381_leave_five_out_parameter_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R9_r1_reroute_pressure_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R9_r1_reroute_pressure_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-06")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "pressure_hash": payload["summary"]["pressure_hash"],
                "leave_attempt_row_count": payload["summary"]["leave_attempt_row_count"],
                "width5_virtual_test_count": payload["summary"]["width5_virtual_test_count"],
                "physical_cost_minus_credit": payload["summary"]["physical_cost_minus_credit"],
                "reroute_allowed": payload["summary"]["reroute_allowed"],
                "requirements_passed": payload["summary"]["requirements_passed"],
                "requirements_failed": payload["summary"]["requirements_failed"],
                "validation_error_count": payload["summary"]["validation_error_count"],
                "json_output": str(args.json_output),
                "markdown_output": str(args.markdown_output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B1/B7 R9 R1 reroute-pressure gate validation failed")


if __name__ == "__main__":
    main()
