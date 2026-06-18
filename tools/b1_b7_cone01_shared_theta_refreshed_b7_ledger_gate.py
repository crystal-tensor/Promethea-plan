#!/usr/bin/env python3
"""Refreshed-B7-ledger rejection gate for B1/B7 cone_01 shared theta.

The prior cost-model gate has six of eight scaffold requirements in place, but
the model is still not accepted. This gate records the CM-08 ledger refresh
attempt explicitly: the B7 FT ledger is inspected against the unaccepted
shared-theta cost model, and the refresh is rejected until occurrence-removing
certificates or a physically accepted model exist.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_shared_theta_refreshed_b7_ledger_gate_v0"
STATUS = "cone01_shared_theta_refreshed_b7_ledger_rejected"
MODEL_STATUS = "refreshed_b7_ledger_rejects_unaccepted_theta_sharing_model"
VERSION = "0.1"


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
    cost_gate = read_json(args.cost_model_gate)
    b7_boundary = read_json(args.b7_ft_boundary)
    cost_summary = cost_gate["summary"]
    target = b7_boundary["target_requirements_for_current_min"][0]

    cost_model_accepted = bool(cost_summary["cost_model_accepted"])
    occurrence_reduction = int(cost_summary["occurrence_ledger_proxy_t_reduction"])
    prior_b7_reduction = int(cost_summary["b7_ledger_proxy_t_reduction_after_cost_model"])
    required_proxy_t_reduction = int(cost_summary["target_proxy_t_ledger_reduction_for_gcm_h6_1_20"])
    missing_proxy_t_reduction = max(required_proxy_t_reduction - prior_b7_reduction, 0)
    refresh_accepts_model = (
        cost_model_accepted
        and occurrence_reduction >= required_proxy_t_reduction
        and int(cost_summary["cost_model_acceptance_fail_count"]) == 0
    )

    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 shared-theta refreshed-B7-ledger rejection gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_theta_sharing_cost_model_gate": display_path(args.cost_model_gate),
        "source_b7_ft_boundary": display_path(args.b7_ft_boundary),
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "summary": {
            "b7_ledger_refresh_attempted": True,
            "b7_ledger_accepts_theta_sharing": refresh_accepts_model,
            "cost_model_accepted": cost_model_accepted,
            "cost_model_acceptance_pass_count": int(cost_summary["cost_model_acceptance_pass_count"]),
            "cost_model_acceptance_fail_count": int(cost_summary["cost_model_acceptance_fail_count"]),
            "cm08_refreshed_b7_ledger_gate_passed": refresh_accepts_model,
            "candidate_window_count": int(cost_summary["candidate_window_count"]),
            "distinct_theta_group_count": int(cost_summary["distinct_theta_group_count"]),
            "optimistic_cache_proxy_t_reuse": int(cost_summary["optimistic_cache_proxy_t_reuse"]),
            "occurrence_ledger_removed_occurrences": int(cost_summary["occurrence_ledger_removed_occurrences"]),
            "occurrence_ledger_proxy_t_reduction": occurrence_reduction,
            "b7_ledger_proxy_t_reduction_before_refresh": prior_b7_reduction,
            "b7_ledger_proxy_t_reduction_after_refresh": 0,
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": required_proxy_t_reduction,
            "missing_proxy_t_ledger_reduction_for_gcm_h6_1_20": missing_proxy_t_reduction,
            "gcm_h6_current_total_t_ledger": int(b7_boundary["gcm_h6_after_total_t_ledger"]),
            "gcm_h6_target_max_after_t_ledger_1_20": int(target["max_after_t_ledger"]),
            "gcm_h6_additional_t_ledger_to_remove_for_1_20": int(target["additional_t_ledger_to_remove"]),
            "gcm_h6_min_row_improved": False,
            "current_min_space_time_volume_reduction": float(
                b7_boundary["current_min_space_time_volume_reduction"]
            ),
            "refreshed_min_space_time_volume_reduction": float(
                b7_boundary["current_min_space_time_volume_reduction"]
            ),
            "physical_device_layout_present": False,
            "physical_factory_schedule_present": False,
            "device_calibrated_validation_present": False,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "physical_resource_reduction_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "validation_error_count": None,
        },
        "refresh_decision": {
            "decision": "reject_theta_sharing_as_b7_resource_saving",
            "reason": (
                "The shared-theta cost model is not accepted, CM-01 and CM-08 remain failed, "
                "and the accepted occurrence-ledger proxy-T reduction is still 0."
            ),
            "conditions_required_to_accept": [
                "Produce at least 30 occurrence-removing semantic certificates, or accepted equivalent proxy-T ledger reduction.",
                "Remove all remaining physical cost-model failures.",
                "Refresh the B7 FT ledger with an accepted physical device/layout/factory interpretation.",
                "Show an actual gcm_h6 min-row improvement under the same B7 ledger denominator.",
            ],
        },
        "claim_boundary": {
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "physical_resource_reduction_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "The CM-08 refresh attempt has been made explicit and rejects the current "
                "shared-theta cost model for B7 ledger accounting."
            ),
            "unsupported_claims": [
                "No occurrence-removing semantic certificate is produced.",
                "No physical device layout or factory schedule accepts shared-theta reuse.",
                "No B7 proxy-T reduction or gcm_h6 min-row improvement is counted.",
                "The cost model remains unaccepted.",
            ],
            "next_gate": (
                "CM-08 can only pass after the model is physically accepted and a refreshed "
                "B7 ledger records nonzero accepted proxy-T reduction or a real min-row improvement."
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
        "distinct_theta_group_count": 4,
        "optimistic_cache_proxy_t_reuse": 620,
        "occurrence_ledger_removed_occurrences": 0,
        "occurrence_ledger_proxy_t_reduction": 0,
        "b7_ledger_proxy_t_reduction_before_refresh": 0,
        "b7_ledger_proxy_t_reduction_after_refresh": 0,
        "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": 600,
        "missing_proxy_t_ledger_reduction_for_gcm_h6_1_20": 600,
        "gcm_h6_current_total_t_ledger": 6224,
        "gcm_h6_target_max_after_t_ledger_1_20": 5632,
        "gcm_h6_additional_t_ledger_to_remove_for_1_20": 592,
    }
    if payload.get("method") != METHOD:
        errors.append("method mismatch")
    if payload.get("status") != STATUS:
        errors.append("status mismatch")
    if payload.get("model_status") != MODEL_STATUS:
        errors.append("model_status mismatch")
    for field, value in expected.items():
        if summary.get(field) != value:
            errors.append(f"{field} expected {value}, got {summary.get(field)}")
    if summary.get("b7_ledger_refresh_attempted") is not True:
        errors.append("B7 ledger refresh attempt should be explicit")
    if summary.get("b7_ledger_accepts_theta_sharing") is not False:
        errors.append("B7 ledger must reject theta sharing under current evidence")
    if summary.get("cost_model_accepted") is not False:
        errors.append("cost model must remain unaccepted")
    if summary.get("cost_model_acceptance_pass_count") != 6:
        errors.append("cost-model pass count must remain 6")
    if summary.get("cost_model_acceptance_fail_count") != 2:
        errors.append("cost-model fail count must remain 2")
    if summary.get("cm08_refreshed_b7_ledger_gate_passed") is not False:
        errors.append("CM-08 must remain failed")
    if summary.get("gcm_h6_min_row_improved") is not False:
        errors.append("gcm_h6 min row must not improve under rejected refresh")
    if summary.get("current_min_space_time_volume_reduction") != summary.get(
        "refreshed_min_space_time_volume_reduction"
    ):
        errors.append("rejected refresh must preserve current min-STV value")
    for field in [
        "physical_device_layout_present",
        "physical_factory_schedule_present",
        "device_calibrated_validation_present",
        "rewrite_claimed",
        "resource_saving_claimed",
        "semantic_certificate_claimed",
        "physical_resource_reduction_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field} must remain false in summary")
    for field in [
        "rewrite_claimed",
        "resource_saving_claimed",
        "semantic_certificate_claimed",
        "physical_resource_reduction_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if claims.get(field) is not False:
            errors.append(f"{field} must remain false in claim boundary")
    return errors


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 Shared-Theta Refreshed-B7-Ledger Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact makes the CM-08 ledger-refresh decision explicit. It reads "
        "the current shared-theta cost-model gate and the B7 `gcm_h6` FT boundary, "
        "then asks whether the B7 ledger can accept theta sharing as a physical "
        "resource saving. The answer is no under current evidence.",
        "",
        "It is a rejection gate, not a rewrite certificate, not a physical layout, "
        "and not a B7 resource-saving claim.",
        "",
        "## Summary",
        "",
        f"- B7 ledger refresh attempted: `{summary['b7_ledger_refresh_attempted']}`",
        f"- B7 ledger accepts theta sharing: `{summary['b7_ledger_accepts_theta_sharing']}`",
        f"- Cost model accepted: `{summary['cost_model_accepted']}`",
        f"- Cost-model gates passed / failed: `{summary['cost_model_acceptance_pass_count']}` / `{summary['cost_model_acceptance_fail_count']}`",
        f"- CM-08 refreshed-B7-ledger gate passed: `{summary['cm08_refreshed_b7_ledger_gate_passed']}`",
        f"- Candidate windows / theta groups: `{summary['candidate_window_count']}` / `{summary['distinct_theta_group_count']}`",
        f"- Optimistic cache proxy-T signal: `{summary['optimistic_cache_proxy_t_reuse']}`",
        f"- Occurrence-ledger removed occurrences / proxy-T reduction: `{summary['occurrence_ledger_removed_occurrences']}` / `{summary['occurrence_ledger_proxy_t_reduction']}`",
        f"- B7 proxy-T reduction before / after refresh: `{summary['b7_ledger_proxy_t_reduction_before_refresh']}` / `{summary['b7_ledger_proxy_t_reduction_after_refresh']}`",
        f"- Target / missing proxy-T reduction for 1.20x: `{summary['target_proxy_t_ledger_reduction_for_gcm_h6_1_20']}` / `{summary['missing_proxy_t_ledger_reduction_for_gcm_h6_1_20']}`",
        f"- gcm_h6 current total T ledger: `{summary['gcm_h6_current_total_t_ledger']}`",
        f"- gcm_h6 target max after T ledger for 1.20x: `{summary['gcm_h6_target_max_after_t_ledger_1_20']}`",
        f"- gcm_h6 additional T ledger to remove for 1.20x: `{summary['gcm_h6_additional_t_ledger_to_remove_for_1_20']}`",
        f"- gcm_h6 min row improved: `{summary['gcm_h6_min_row_improved']}`",
        f"- Current / refreshed min-STV reduction: `{summary['current_min_space_time_volume_reduction']}` / `{summary['refreshed_min_space_time_volume_reduction']}`",
        f"- Physical layout / factory schedule / device-calibrated validation present: `{summary['physical_device_layout_present']}` / `{summary['physical_factory_schedule_present']}` / `{summary['device_calibrated_validation_present']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Decision",
        "",
        f"- Decision: `{payload['refresh_decision']['decision']}`",
        f"- Reason: {payload['refresh_decision']['reason']}",
        "",
        "## Conditions Required To Accept",
        "",
    ]
    for condition in payload["refresh_decision"]["conditions_required_to_accept"]:
        lines.append(f"- {condition}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The shared-theta route remains useful as a research target, but the B7 "
            "ledger cannot count it yet. The accepted ledger reduction is still 0, "
            "so the active route remains either occurrence-removing certificates or "
            "a stronger physical model that survives this refresh gate.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--cost-model-gate",
        type=Path,
        default=root / "results" / "B1_B7_cone01_theta_sharing_cost_model_gate_v0.json",
    )
    parser.add_argument(
        "--b7-ft-boundary",
        type=Path,
        default=root / "results" / "B7_gcm_h6_ft_boundary_v0.json",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=root / "results" / "B1_B7_cone01_shared_theta_refreshed_b7_ledger_gate_v0.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=root / "research" / "B1_B7_cone01_shared_theta_refreshed_b7_ledger_gate.md",
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
