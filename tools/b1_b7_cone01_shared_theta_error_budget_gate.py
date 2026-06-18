#!/usr/bin/env python3
"""Shared-error budget scaffold for B1/B7 cone_01 shared-theta reuse.

This gate asks whether the replayed, logically routed, and factory-amortized
shared-theta objects have an explicit synthesis-error and correlation budget.
It allocates a conservative per-object error budget and records the correlation
groups that would need to be validated before theta sharing could be accepted
as a physical cost model.

The gate deliberately does not accept the physical cost model.  It has no
independent baseline, no device-calibrated factory schedule, and no refreshed
B7 ledger.  It is CM-06 scaffold evidence only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_shared_theta_error_budget_gate_v0"
STATUS = "cone01_shared_theta_error_budget_scaffold"
MODEL_STATUS = "shared_error_budget_scaffold_not_physical_cost_model"
VERSION = "0.1"
TOTAL_SHARED_THETA_ERROR_BUDGET = 1.0e-6
PER_OBJECT_ERROR_BUDGET = 2.5e-7
PER_OCCURRENCE_ERROR_BUDGET = 1.0e-8


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def display_path(path: Path) -> str:
    root = Path(__file__).resolve().parents[1]
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(root))
    except ValueError:
        return str(path)


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    factory_gate = read_json(args.factory_amortization_gate)
    layout_gate = read_json(args.layout_routing_gate)
    factory_summary = factory_gate["summary"]
    layout_rows = layout_gate["layout_route_rows"]
    amortization_rows = {
        row["object_id"]: row
        for row in factory_gate["object_amortization_rows"]
    }

    error_rows = []
    for row in layout_rows:
        object_id = row["object_id"]
        occurrence_count = int(row["route_packet_count"])
        amortization = amortization_rows[object_id]
        per_occurrence_total = round(occurrence_count * PER_OCCURRENCE_ERROR_BUDGET, 12)
        object_budget_margin = round(PER_OBJECT_ERROR_BUDGET - per_occurrence_total, 12)
        error_rows.append(
            {
                "object_id": object_id,
                "canonical_theta": row["canonical_theta"],
                "occurrence_count": occurrence_count,
                "logical_anchor_qubit": row["logical_anchor_qubit"],
                "max_logical_hop_count": row["max_logical_hop_count"],
                "amortized_saved_compile_count": amortization["amortized_saved_compile_count"],
                "per_occurrence_error_budget": PER_OCCURRENCE_ERROR_BUDGET,
                "per_object_error_budget": PER_OBJECT_ERROR_BUDGET,
                "per_occurrence_error_budget_total": per_occurrence_total,
                "object_budget_margin": object_budget_margin,
                "within_object_budget": object_budget_margin >= 0.0,
                "correlation_group_id": object_id,
                "correlated_occurrence_count": occurrence_count,
                "correlation_model_present": True,
                "independent_calibration_present": False,
                "hardware_noise_model_present": False,
            }
        )

    aggregate_per_occurrence_budget = round(sum(
        row["per_occurrence_error_budget_total"] for row in error_rows
    ), 12)
    aggregate_object_budget = round(len(error_rows) * PER_OBJECT_ERROR_BUDGET, 12)
    unused_total_budget = round(TOTAL_SHARED_THETA_ERROR_BUDGET - aggregate_object_budget, 12)
    shared_error_budget_gate_passed = (
        factory_summary["factory_amortization_gate_passed"] is True
        and len(error_rows) == int(factory_summary["shared_synthesis_object_count"])
        and all(row["within_object_budget"] for row in error_rows)
        and aggregate_object_budget <= TOTAL_SHARED_THETA_ERROR_BUDGET
    )

    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 shared-theta error-budget scaffold",
        "version": VERSION,
        "last_updated": args.last_updated,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_shared_theta_factory_amortization_gate": display_path(args.factory_amortization_gate),
        "source_shared_theta_layout_routing_gate": display_path(args.layout_routing_gate),
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "summary": {
            "candidate_window_count": int(factory_summary["candidate_window_count"]),
            "shared_synthesis_object_count": int(factory_summary["shared_synthesis_object_count"]),
            "layout_routed_occurrence_count": int(factory_summary["layout_routed_occurrence_count"]),
            "distinct_theta_group_count": int(factory_summary["distinct_theta_group_count"]),
            "duplicate_theta_occurrence_count": int(factory_summary["duplicate_theta_occurrence_count"]),
            "total_shared_theta_error_budget": TOTAL_SHARED_THETA_ERROR_BUDGET,
            "per_object_error_budget": PER_OBJECT_ERROR_BUDGET,
            "per_occurrence_error_budget": PER_OCCURRENCE_ERROR_BUDGET,
            "aggregate_per_occurrence_error_budget": aggregate_per_occurrence_budget,
            "aggregate_object_error_budget": aggregate_object_budget,
            "unused_total_error_budget": unused_total_budget,
            "correlation_group_count": len(error_rows),
            "max_correlated_occurrence_count": max(row["correlated_occurrence_count"] for row in error_rows),
            "shared_error_budget_gate_passed": shared_error_budget_gate_passed,
            "factory_amortization_gate_passed": bool(factory_summary["factory_amortization_gate_passed"]),
            "independent_calibration_present": False,
            "hardware_noise_model_present": False,
            "independent_baseline_present": False,
            "refreshed_b7_ledger_present": False,
            "occurrence_ledger_removed_occurrences": 0,
            "occurrence_ledger_proxy_t_reduction": 0,
            "cost_model_accepted": False,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "physical_resource_reduction_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "validation_error_count": None,
        },
        "object_error_budget_rows": error_rows,
        "claim_boundary": {
            "cost_model_accepted": False,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "physical_resource_reduction_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "The shared-theta objects now have an explicit scaffold-level synthesis-error "
                "budget and correlation grouping: four shared objects receive 2.5e-7 error "
                "budget each under a 1e-6 aggregate budget."
            ),
            "unsupported_claims": [
                "No device-calibrated hardware noise model is supplied.",
                "No independent calibration validates the correlation budget.",
                "No independent physical baseline validates theta sharing.",
                "No refreshed B7 ledger accepts this as a resource saving.",
            ],
            "next_gate": (
                "Use this as CM-06 shared-error budget scaffold evidence, then build "
                "CM-07 independent-baseline evidence and CM-08 refreshed-B7-ledger evidence "
                "before any physical theta-sharing cost model can be accepted."
            ),
        },
    }
    errors = validate(payload)
    payload["summary"]["validation_error_count"] = len(errors)
    payload["validation_errors"] = errors
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload["summary"]
    claims = payload["claim_boundary"]
    expected = {
        "candidate_window_count": 35,
        "shared_synthesis_object_count": 4,
        "layout_routed_occurrence_count": 35,
        "distinct_theta_group_count": 4,
        "duplicate_theta_occurrence_count": 31,
        "correlation_group_count": 4,
        "max_correlated_occurrence_count": 16,
        "occurrence_ledger_removed_occurrences": 0,
        "occurrence_ledger_proxy_t_reduction": 0,
    }
    if payload.get("method") != METHOD:
        errors.append("method mismatch")
    if payload.get("status") != STATUS:
        errors.append("status mismatch")
    if payload.get("model_status") != MODEL_STATUS:
        errors.append("model_status mismatch")
    for field, value in expected.items():
        if summary.get(field) != value:
            errors.append(f"{field} expected {value}")
    if summary.get("total_shared_theta_error_budget") != TOTAL_SHARED_THETA_ERROR_BUDGET:
        errors.append("total shared-theta error budget mismatch")
    if summary.get("per_object_error_budget") != PER_OBJECT_ERROR_BUDGET:
        errors.append("per-object error budget mismatch")
    if summary.get("per_occurrence_error_budget") != PER_OCCURRENCE_ERROR_BUDGET:
        errors.append("per-occurrence error budget mismatch")
    if summary.get("aggregate_object_error_budget") != TOTAL_SHARED_THETA_ERROR_BUDGET:
        errors.append("aggregate object budget should consume the total scaffold budget")
    if summary.get("aggregate_per_occurrence_error_budget") > summary.get("aggregate_object_error_budget"):
        errors.append("per-occurrence budget total must stay within object budget")
    if summary.get("shared_error_budget_gate_passed") is not True:
        errors.append("shared-error budget scaffold should pass")
    if summary.get("factory_amortization_gate_passed") is not True:
        errors.append("factory-amortization dependency should pass")
    for field in [
        "independent_calibration_present",
        "hardware_noise_model_present",
        "independent_baseline_present",
        "refreshed_b7_ledger_present",
        "cost_model_accepted",
        "rewrite_claimed",
        "resource_saving_claimed",
        "semantic_certificate_claimed",
        "physical_resource_reduction_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field} must remain false in summary")
        if field in claims and claims.get(field) is not False:
            errors.append(f"{field} must remain false in claim boundary")
    for row in payload["object_error_budget_rows"]:
        if row.get("within_object_budget") is not True:
            errors.append(f"{row.get('object_id')} exceeds object budget")
        if row.get("correlation_model_present") is not True:
            errors.append(f"{row.get('object_id')} missing correlation model")
        if row.get("independent_calibration_present") is not False:
            errors.append(f"{row.get('object_id')} must not claim independent calibration")
        if row.get("hardware_noise_model_present") is not False:
            errors.append(f"{row.get('object_id')} must not claim hardware noise model")
    return errors


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Shared-Theta Error-Budget Scaffold",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact adds CM-06 bookkeeping for the replayed, logically routed, "
        "and factory-amortized shared-theta objects. It gives each shared object a "
        "scaffold-level synthesis-error allocation and records the correlation group "
        "that would need independent validation before theta sharing could be accepted "
        "as a physical cost model.",
        "",
        "It is not a hardware noise model, not an independent calibration, not a "
        "semantic rewrite certificate, and not a B7 resource-saving claim.",
        "",
        "## Summary",
        "",
        f"- Candidate windows: `{summary['candidate_window_count']}`",
        f"- Shared objects: `{summary['shared_synthesis_object_count']}`",
        f"- Layout-routed occurrences: `{summary['layout_routed_occurrence_count']}`",
        f"- Total shared-theta error budget: `{summary['total_shared_theta_error_budget']}`",
        f"- Per-object error budget: `{summary['per_object_error_budget']}`",
        f"- Per-occurrence error budget: `{summary['per_occurrence_error_budget']}`",
        f"- Aggregate per-occurrence error budget: `{summary['aggregate_per_occurrence_error_budget']}`",
        f"- Aggregate object error budget: `{summary['aggregate_object_error_budget']}`",
        f"- Correlation groups: `{summary['correlation_group_count']}`",
        f"- Max correlated occurrences: `{summary['max_correlated_occurrence_count']}`",
        f"- Shared-error budget gate passed: `{summary['shared_error_budget_gate_passed']}`",
        f"- Independent calibration present: `{summary['independent_calibration_present']}`",
        f"- Hardware noise model present: `{summary['hardware_noise_model_present']}`",
        f"- Cost model accepted: `{summary['cost_model_accepted']}`",
        f"- B7 ledger improvement claimed: `{summary['b7_ledger_improvement_claimed']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Object Budgets",
        "",
        "| object | occurrences | per-object budget | per-occurrence total | margin | correlated occurrences |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["object_error_budget_rows"]:
        lines.append(
            f"| {row['object_id']} | {row['occurrence_count']} | "
            f"`{row['per_object_error_budget']}` | `{row['per_occurrence_error_budget_total']}` | "
            f"`{row['object_budget_margin']}` | `{row['correlated_occurrence_count']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This closes the CM-06 bookkeeping gap, but only as a scaffold. A future "
            "PR must still supply an independent baseline and a refreshed B7 ledger, "
            "or bypass the cost-model route by producing 30 occurrence-removing "
            "semantic certificates.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--factory-amortization-gate",
        type=Path,
        default=root / "results" / "B1_B7_cone01_shared_theta_factory_amortization_gate_v0.json",
    )
    parser.add_argument(
        "--layout-routing-gate",
        type=Path,
        default=root / "results" / "B1_B7_cone01_shared_theta_layout_routing_gate_v0.json",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=root / "results" / "B1_B7_cone01_shared_theta_error_budget_gate_v0.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=root / "research" / "B1_B7_cone01_shared_theta_error_budget_gate.md",
    )
    parser.add_argument("--last-updated", default="2026-06-18")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    write_text(args.markdown_output, markdown(payload))
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Wrote {args.json_output}")
        print(f"Wrote {args.markdown_output}")


if __name__ == "__main__":
    main()
