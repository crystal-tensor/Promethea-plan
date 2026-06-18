#!/usr/bin/env python3
"""Physical cost-model feasibility gate for B1/B7 cone_01 theta sharing.

T-B1-004f showed that repeated theta values create a tempting cache signal, but
the current occurrence-based FT ledger does not count cache reuse as a physical
resource reduction. This gate states the acceptance requirements for any future
physical theta-sharing cost model and checks the current evidence against them.

The expected current result is negative: no new physical cost model is accepted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_theta_sharing_cost_model_gate_v0"
STATUS = "cone01_theta_sharing_cost_model_not_accepted"
MODEL_STATUS = "physical_theta_sharing_cost_model_requirements_error_budget_scaffolded"
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


def build_requirement_rows(
    theta_summary: dict[str, Any],
    shared_summary: dict[str, Any] | None,
    replay_summary: dict[str, Any] | None,
    layout_summary: dict[str, Any] | None,
    factory_summary: dict[str, Any] | None,
    error_budget_summary: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Return current acceptance gates for a physical theta-sharing model."""
    shared_object_count = 0
    shared_object_gate_passed = False
    replayed_object_count = 0
    replay_gate_passed = False
    layout_routed_object_count = 0
    layout_gate_passed = False
    factory_gross_proxy_t_delta = 0
    factory_gate_passed = False
    error_budget_current_evidence = False
    error_budget_gate_passed = False
    if shared_summary:
        shared_object_count = int(shared_summary["shared_synthesis_object_count"])
        shared_object_gate_passed = (
            shared_summary["shared_object_existence_gate_passed"] is True
            and shared_summary["all_candidate_windows_covered"] is True
            and int(shared_summary["semantic_replay_verified_object_count"]) == 0
            and int(shared_summary["physical_layout_assigned_object_count"]) == 0
            and int(shared_summary["b7_ledger_accepted_object_count"]) == 0
        )
    if replay_summary:
        replayed_object_count = int(replay_summary["replay_verified_object_count"])
        replay_gate_passed = (
            replay_summary["shared_theta_replay_gate_passed"] is True
            and int(replay_summary["replayed_occurrence_count"]) == int(theta_summary["candidate_window_count"])
            and replay_summary["semantic_rewrite_verified"] is False
            and int(replay_summary["occurrence_ledger_removed_occurrences"]) == 0
        )
    if layout_summary:
        layout_routed_object_count = int(layout_summary["layout_routed_object_count"])
        layout_gate_passed = (
            layout_summary["layout_routing_gate_passed"] is True
            and int(layout_summary["layout_routed_occurrence_count"]) == int(theta_summary["candidate_window_count"])
            and layout_summary["physical_layout_claimed"] is False
            and layout_summary["factory_amortization_model_present"] is False
            and int(layout_summary["occurrence_ledger_removed_occurrences"]) == 0
        )
    if factory_summary:
        factory_gross_proxy_t_delta = int(factory_summary["gross_proxy_t_pressure_delta"])
        factory_gate_passed = (
            factory_summary["factory_amortization_gate_passed"] is True
            and int(factory_summary["baseline_factory_compilation_count"]) == int(theta_summary["candidate_window_count"])
            and int(factory_summary["shared_object_factory_compilation_count"]) == int(theta_summary["distinct_theta_group_count"])
            and int(factory_summary["gross_proxy_t_pressure_delta"])
            == int(theta_summary["optimistic_cache_proxy_t_reuse"])
            and factory_summary["physical_factory_schedule_present"] is False
            and factory_summary["shared_error_budget_present"] is False
            and int(factory_summary["occurrence_ledger_removed_occurrences"]) == 0
        )
    if error_budget_summary:
        error_budget_current_evidence = bool(error_budget_summary["shared_error_budget_gate_passed"])
        error_budget_gate_passed = (
            error_budget_summary["shared_error_budget_gate_passed"] is True
            and int(error_budget_summary["shared_synthesis_object_count"]) == int(theta_summary["distinct_theta_group_count"])
            and int(error_budget_summary["correlation_group_count"]) == int(theta_summary["distinct_theta_group_count"])
            and int(error_budget_summary["max_correlated_occurrence_count"]) == 16
            and float(error_budget_summary["total_shared_theta_error_budget"]) == 1.0e-6
            and float(error_budget_summary["aggregate_per_occurrence_error_budget"])
            <= float(error_budget_summary["aggregate_object_error_budget"])
            and error_budget_summary["independent_calibration_present"] is False
            and error_budget_summary["hardware_noise_model_present"] is False
            and int(error_budget_summary["occurrence_ledger_removed_occurrences"]) == 0
        )
    return [
        {
            "gate_id": "CM-01",
            "requirement": "At least 30 replayable occurrence-removing semantic certificates.",
            "current_evidence": int(theta_summary["occurrence_ledger_removed_occurrences"]),
            "required_evidence": int(theta_summary["target_removed_arbitrary_occurrences_for_gcm_h6_1_20"]),
            "passed": False,
            "failure_reason": "Current evidence has 0 accepted occurrence removals.",
        },
        {
            "gate_id": "CM-02",
            "requirement": "A shared synthesis object that replaces repeated theta occurrences, not only a classical template label.",
            "current_evidence": shared_object_count,
            "required_evidence": 4,
            "passed": shared_object_gate_passed,
            "failure_reason": (
                "Shared-theta object proposals now exist, but this gate alone does not replay-verify "
                "or physically accept the cost model."
                if shared_object_gate_passed
                else "No complete shared-theta synthesis object proposal covers the cone_01 windows."
            ),
        },
        {
            "gate_id": "CM-03",
            "requirement": "A replay verifier for the shared-theta object across all affected windows.",
            "current_evidence": replayed_object_count,
            "required_evidence": 4,
            "passed": replay_gate_passed,
            "failure_reason": (
                "A line-level shared-theta replay verifier now covers all objects, but it is not a "
                "semantic rewrite certificate or physical acceptance by itself."
                if replay_gate_passed
                else "No complete shared-theta replay verifier covers all objects."
            ),
        },
        {
            "gate_id": "CM-04",
            "requirement": "An explicit layout/routing model showing where the shared object lives and how windows consume it.",
            "current_evidence": layout_routed_object_count,
            "required_evidence": True,
            "passed": layout_gate_passed,
            "failure_reason": (
                "A logical layout/routing scaffold now assigns anchors and route packets for all "
                "shared objects, but it is not a physical device layout or cost acceptance by itself."
                if layout_gate_passed
                else "No complete layout/routing scaffold is supplied."
            ),
        },
        {
            "gate_id": "CM-05",
            "requirement": "A factory-amortization model proving lower T-factory pressure under the shared object.",
            "current_evidence": factory_gross_proxy_t_delta,
            "required_evidence": True,
            "passed": factory_gate_passed,
            "failure_reason": (
                "A factory-amortization scaffold now shows 35 per-occurrence synthesis requests "
                "collapsing to 4 shared-object synthesis requests with 620 gross proxy-T pressure "
                "delta, but it is not a physical factory schedule or B7 acceptance by itself."
                if factory_gate_passed
                else "No factory-throughput or amortization ledger is supplied."
            ),
        },
        {
            "gate_id": "CM-06",
            "requirement": "A synthesis-error and correlation budget for shared theta reuse.",
            "current_evidence": error_budget_current_evidence,
            "required_evidence": True,
            "passed": error_budget_gate_passed,
            "failure_reason": (
                "A scaffold-level shared-error budget now allocates 1e-6 aggregate error "
                "across the four shared-theta objects, but it is not device-calibrated "
                "or independently validated."
                if error_budget_gate_passed
                else "No shared-error or correlation budget is supplied."
            ),
        },
        {
            "gate_id": "CM-07",
            "requirement": "An independent baseline showing cache-only accounting is not double-counting occurrence cost.",
            "current_evidence": False,
            "required_evidence": True,
            "passed": False,
            "failure_reason": "No independent physical baseline separates cache labels from occurrence cost.",
        },
        {
            "gate_id": "CM-08",
            "requirement": "A refreshed B7 FT ledger that accepts the model and improves the gcm_h6 min row.",
            "current_evidence": False,
            "required_evidence": True,
            "passed": False,
            "failure_reason": "No refreshed B7 ledger accepts theta sharing as a physical saving.",
        },
    ]


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    theta_gate = read_json(args.theta_sharing_gate)
    shared_object_gate = read_json(args.shared_object_gate) if args.shared_object_gate.exists() else None
    replay_gate = read_json(args.replay_verifier_gate) if args.replay_verifier_gate.exists() else None
    layout_gate = read_json(args.layout_routing_gate) if args.layout_routing_gate.exists() else None
    factory_gate = read_json(args.factory_amortization_gate) if args.factory_amortization_gate.exists() else None
    error_budget_gate = read_json(args.error_budget_gate) if args.error_budget_gate.exists() else None
    theta_summary = theta_gate["summary"]
    shared_summary = shared_object_gate["summary"] if shared_object_gate else None
    replay_summary = replay_gate["summary"] if replay_gate else None
    layout_summary = layout_gate["summary"] if layout_gate else None
    factory_summary = factory_gate["summary"] if factory_gate else None
    error_budget_summary = error_budget_gate["summary"] if error_budget_gate else None
    rows = build_requirement_rows(
        theta_summary,
        shared_summary,
        replay_summary,
        layout_summary,
        factory_summary,
        error_budget_summary,
    )
    passed_count = sum(1 for row in rows if row["passed"])
    failed_count = len(rows) - passed_count
    optimistic_cache_signal_present = (
        theta_summary["optimistic_cache_model_clears_target"] is True
        and int(theta_summary["optimistic_cache_proxy_t_reuse"])
        >= int(theta_summary["target_proxy_t_ledger_reduction_for_gcm_h6_1_20"])
    )

    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 theta-sharing physical cost-model gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_theta_sharing_ledger_gate": display_path(args.theta_sharing_gate),
        "source_shared_theta_synthesis_object_gate": (
            display_path(args.shared_object_gate) if shared_object_gate else None
        ),
        "source_shared_theta_replay_verifier_gate": (
            display_path(args.replay_verifier_gate) if replay_gate else None
        ),
        "source_shared_theta_layout_routing_gate": (
            display_path(args.layout_routing_gate) if layout_gate else None
        ),
        "source_shared_theta_factory_amortization_gate": (
            display_path(args.factory_amortization_gate) if factory_gate else None
        ),
        "source_shared_theta_error_budget_gate": (
            display_path(args.error_budget_gate) if error_budget_gate else None
        ),
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "summary": {
            "candidate_window_count": int(theta_summary["candidate_window_count"]),
            "distinct_theta_group_count": int(theta_summary["distinct_theta_group_count"]),
            "duplicate_theta_occurrence_count": int(theta_summary["duplicate_theta_occurrence_count"]),
            "optimistic_cache_proxy_t_reuse": int(theta_summary["optimistic_cache_proxy_t_reuse"]),
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": int(
                theta_summary["target_proxy_t_ledger_reduction_for_gcm_h6_1_20"]
            ),
            "optimistic_cache_signal_present": optimistic_cache_signal_present,
            "shared_synthesis_object_count": int(shared_summary["shared_synthesis_object_count"]) if shared_summary else 0,
            "shared_object_existence_gate_passed": (
                bool(shared_summary["shared_object_existence_gate_passed"]) if shared_summary else False
            ),
            "shared_object_all_windows_covered": (
                bool(shared_summary["all_candidate_windows_covered"]) if shared_summary else False
            ),
            "shared_theta_replay_gate_passed": (
                bool(replay_summary["shared_theta_replay_gate_passed"]) if replay_summary else False
            ),
            "shared_theta_replay_verified_object_count": (
                int(replay_summary["replay_verified_object_count"]) if replay_summary else 0
            ),
            "shared_theta_replayed_occurrence_count": (
                int(replay_summary["replayed_occurrence_count"]) if replay_summary else 0
            ),
            "shared_theta_layout_routing_gate_passed": (
                bool(layout_summary["layout_routing_gate_passed"]) if layout_summary else False
            ),
            "shared_theta_layout_routed_object_count": (
                int(layout_summary["layout_routed_object_count"]) if layout_summary else 0
            ),
            "shared_theta_layout_routed_occurrence_count": (
                int(layout_summary["layout_routed_occurrence_count"]) if layout_summary else 0
            ),
            "shared_theta_layout_total_logical_hop_count": (
                int(layout_summary["total_logical_hop_count"]) if layout_summary else 0
            ),
            "shared_theta_layout_max_logical_hop_count": (
                int(layout_summary["max_logical_hop_count"]) if layout_summary else 0
            ),
            "shared_theta_factory_amortization_gate_passed": (
                bool(factory_summary["factory_amortization_gate_passed"]) if factory_summary else False
            ),
            "shared_theta_factory_baseline_compilation_count": (
                int(factory_summary["baseline_factory_compilation_count"]) if factory_summary else 0
            ),
            "shared_theta_factory_shared_object_compilation_count": (
                int(factory_summary["shared_object_factory_compilation_count"]) if factory_summary else 0
            ),
            "shared_theta_factory_gross_proxy_t_delta": (
                int(factory_summary["gross_proxy_t_pressure_delta"]) if factory_summary else 0
            ),
            "shared_theta_error_budget_gate_passed": (
                bool(error_budget_summary["shared_error_budget_gate_passed"]) if error_budget_summary else False
            ),
            "shared_theta_total_error_budget": (
                float(error_budget_summary["total_shared_theta_error_budget"]) if error_budget_summary else 0.0
            ),
            "shared_theta_aggregate_per_occurrence_error_budget": (
                float(error_budget_summary["aggregate_per_occurrence_error_budget"])
                if error_budget_summary
                else 0.0
            ),
            "shared_theta_correlation_group_count": (
                int(error_budget_summary["correlation_group_count"]) if error_budget_summary else 0
            ),
            "shared_theta_max_correlated_occurrence_count": (
                int(error_budget_summary["max_correlated_occurrence_count"]) if error_budget_summary else 0
            ),
            "cost_model_acceptance_gate_count": len(rows),
            "cost_model_acceptance_pass_count": passed_count,
            "cost_model_acceptance_fail_count": failed_count,
            "cost_model_accepted": False,
            "occurrence_ledger_removed_occurrences": int(theta_summary["occurrence_ledger_removed_occurrences"]),
            "occurrence_ledger_proxy_t_reduction": int(theta_summary["occurrence_ledger_proxy_t_reduction"]),
            "b7_ledger_proxy_t_reduction_after_cost_model": 0,
            "additional_occurrence_certificates_required": int(
                theta_summary["additional_occurrence_certificates_required"]
            ),
            "additional_cost_model_gates_required": failed_count,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "physical_resource_reduction_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "validation_error_count": None,
        },
        "cost_model_acceptance_gates": rows,
        "claim_boundary": {
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "physical_resource_reduction_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "A shared-theta synthesis object proposal now exists for all cone_01 windows, "
                "a line-level replay verifier covers the shared objects, and a logical "
                "layout/routing scaffold assigns anchors and route packets for the shared "
                "objects. A factory-amortization scaffold accounts for the 35-to-4 "
                "compilation-pressure change. A shared-error budget scaffold now allocates "
                "error across the four shared-theta objects, but the physical theta-sharing "
                "cost model is still not acceptable under the current evidence; the optimistic "
                "620 proxy-T cache signal remains unaccepted."
            ),
            "unsupported_claims": [
                "No occurrence-removing semantic certificates are produced.",
                "The replay verifier is not a semantic rewrite certificate.",
                "The logical layout scaffold is not a physical device layout.",
                "The shared-error budget scaffold is not device-calibrated or independently validated.",
                "No independent physical baseline validates theta sharing.",
                "No B7 min-row resource improvement is counted.",
            ],
            "next_gate": (
                "A future PR must produce 30 occurrence-removing certificates, or satisfy "
                "CM-07 through CM-08 after the existing CM-02/CM-03/CM-04/CM-05/CM-06 scaffold, before "
                "any B7 resource delta can be counted."
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
    if payload.get("method") != METHOD:
        errors.append("method mismatch")
    if payload.get("status") != STATUS:
        errors.append("status mismatch")
    if payload.get("model_status") != MODEL_STATUS:
        errors.append("model_status mismatch")
    if summary["candidate_window_count"] != 35:
        errors.append("expected 35 candidate windows")
    if summary["distinct_theta_group_count"] != 4:
        errors.append("expected 4 theta groups")
    if summary["duplicate_theta_occurrence_count"] != 31:
        errors.append("expected 31 duplicate theta occurrences")
    if summary["optimistic_cache_proxy_t_reuse"] != 620:
        errors.append("expected optimistic cache signal of 620 proxy-T")
    if summary["optimistic_cache_signal_present"] is not True:
        errors.append("optimistic cache signal should be present")
    if summary["cost_model_acceptance_gate_count"] != 8:
        errors.append("expected 8 cost-model acceptance gates")
    if summary["shared_synthesis_object_count"] != 4:
        errors.append("expected 4 shared synthesis object proposals")
    if summary["shared_object_existence_gate_passed"] is not True:
        errors.append("shared object existence gate should now pass")
    if summary["shared_object_all_windows_covered"] is not True:
        errors.append("shared objects should cover all cone_01 windows")
    if summary["shared_theta_replay_gate_passed"] is not True:
        errors.append("shared theta replay gate should now pass")
    if summary["shared_theta_replay_verified_object_count"] != 4:
        errors.append("expected 4 replay-verified shared theta objects")
    if summary["shared_theta_replayed_occurrence_count"] != 35:
        errors.append("expected 35 replayed shared theta occurrences")
    if summary["shared_theta_layout_routing_gate_passed"] is not True:
        errors.append("shared theta layout/routing gate should now pass")
    if summary["shared_theta_layout_routed_object_count"] != 4:
        errors.append("expected 4 layout-routed shared theta objects")
    if summary["shared_theta_layout_routed_occurrence_count"] != 35:
        errors.append("expected 35 layout-routed shared theta occurrences")
    if summary["shared_theta_factory_amortization_gate_passed"] is not True:
        errors.append("shared theta factory amortization gate should now pass")
    if summary["shared_theta_factory_baseline_compilation_count"] != 35:
        errors.append("expected 35 baseline factory compilation requests")
    if summary["shared_theta_factory_shared_object_compilation_count"] != 4:
        errors.append("expected 4 shared-object factory compilation requests")
    if summary["shared_theta_factory_gross_proxy_t_delta"] != 620:
        errors.append("expected 620 gross proxy-T factory pressure delta")
    if summary["shared_theta_error_budget_gate_passed"] is not True:
        errors.append("shared theta error-budget gate should now pass")
    if summary["shared_theta_total_error_budget"] != 1.0e-6:
        errors.append("expected shared theta total error budget of 1e-6")
    if summary["shared_theta_correlation_group_count"] != 4:
        errors.append("expected 4 shared theta correlation groups")
    if summary["shared_theta_max_correlated_occurrence_count"] != 16:
        errors.append("expected max correlated occurrence count of 16")
    if summary["cost_model_acceptance_pass_count"] != 5:
        errors.append("current cost-model acceptance passes must be 5")
    if summary["cost_model_acceptance_fail_count"] != 3:
        errors.append("current cost-model acceptance failures must be 3")
    if summary["cost_model_accepted"] is not False:
        errors.append("cost model must not be accepted")
    if summary["b7_ledger_proxy_t_reduction_after_cost_model"] != 0:
        errors.append("B7 ledger reduction after unaccepted cost model must be 0")
    for row in payload["cost_model_acceptance_gates"]:
        if row.get("gate_id") in {"CM-02", "CM-03", "CM-04", "CM-05", "CM-06"}:
            if row.get("passed") is not True:
                errors.append(f"{row.get('gate_id')} should pass after shared object/replay/layout/factory/error-budget gates")
        elif row.get("passed") is not False:
            errors.append(f"{row.get('gate_id')} must not pass under current evidence")
    for field in [
        "rewrite_claimed",
        "resource_saving_claimed",
        "semantic_certificate_claimed",
        "physical_resource_reduction_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field} must remain false in summary")
        if claims.get(field) is not False:
            errors.append(f"{field} must remain false in claim boundary")
    return errors


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Theta-Sharing Physical Cost-Model Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact asks whether the repeated-theta cache signal from T-B1-004f "
        "can already be promoted into a physical B7 cost model. The answer is no. "
        "A shared synthesis object proposal now exists for the four theta groups, "
        "a line-level replay verifier covers the shared objects, and a logical "
        "layout/routing scaffold assigns anchors and route packets. A factory-amortization "
        "scaffold now accounts for the 35-to-4 compilation-pressure change. The current "
        "evidence still lacks occurrence-removing certificates, physical device "
        "layout, device-calibrated error validation, independent baseline, and refreshed B7 ledger.",
        "",
        "It is not a rewrite certificate, not a resource-saving claim, and not a "
        "physical cost-model acceptance.",
        "",
        "## Summary",
        "",
        f"- Candidate windows: `{summary['candidate_window_count']}`",
        f"- Distinct theta groups: `{summary['distinct_theta_group_count']}`",
        f"- Duplicate theta occurrences: `{summary['duplicate_theta_occurrence_count']}`",
        f"- Optimistic cache proxy-T signal: `{summary['optimistic_cache_proxy_t_reuse']}`",
        f"- Target proxy-T reduction: `{summary['target_proxy_t_ledger_reduction_for_gcm_h6_1_20']}`",
        f"- Optimistic cache signal present: `{summary['optimistic_cache_signal_present']}`",
        f"- Shared synthesis object proposals: `{summary['shared_synthesis_object_count']}`",
        f"- Shared object existence gate passed: `{summary['shared_object_existence_gate_passed']}`",
        f"- Shared-theta replay gate passed: `{summary['shared_theta_replay_gate_passed']}`",
        f"- Replay-verified shared objects: `{summary['shared_theta_replay_verified_object_count']}`",
        f"- Logical layout/routing gate passed: `{summary['shared_theta_layout_routing_gate_passed']}`",
        f"- Layout-routed shared objects: `{summary['shared_theta_layout_routed_object_count']}`",
        f"- Layout-routed occurrences: `{summary['shared_theta_layout_routed_occurrence_count']}`",
        f"- Layout total / max logical hops: `{summary['shared_theta_layout_total_logical_hop_count']}` / `{summary['shared_theta_layout_max_logical_hop_count']}`",
        f"- Factory-amortization gate passed: `{summary['shared_theta_factory_amortization_gate_passed']}`",
        f"- Factory baseline/shared-object compilation counts: `{summary['shared_theta_factory_baseline_compilation_count']}` / `{summary['shared_theta_factory_shared_object_compilation_count']}`",
        f"- Factory gross proxy-T delta: `{summary['shared_theta_factory_gross_proxy_t_delta']}`",
        f"- Shared-error budget gate passed: `{summary['shared_theta_error_budget_gate_passed']}`",
        f"- Shared-theta total error budget: `{summary['shared_theta_total_error_budget']}`",
        f"- Shared-theta aggregate per-occurrence error budget: `{summary['shared_theta_aggregate_per_occurrence_error_budget']}`",
        f"- Shared-theta correlation groups: `{summary['shared_theta_correlation_group_count']}`",
        f"- Acceptance gates passed / total: `{summary['cost_model_acceptance_pass_count']}` / `{summary['cost_model_acceptance_gate_count']}`",
        f"- Cost model accepted: `{summary['cost_model_accepted']}`",
        f"- B7 ledger proxy-T reduction after cost model: `{summary['b7_ledger_proxy_t_reduction_after_cost_model']}`",
        f"- Additional occurrence certificates required: `{summary['additional_occurrence_certificates_required']}`",
        f"- Additional cost-model gates required: `{summary['additional_cost_model_gates_required']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Acceptance Gates",
        "",
        "| gate | requirement | current evidence | required evidence | passed |",
        "|---|---|---:|---:|---|",
    ]
    for row in payload["cost_model_acceptance_gates"]:
        lines.append(
            f"| {row['gate_id']} | {row['requirement']} | `{row['current_evidence']}` | "
            f"`{row['required_evidence']}` | `{row['passed']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The repeated-theta structure is valuable because it identifies where a "
            "future physical-sharing proposal would have leverage. The shared object "
            "proposal, replay verifier, logical layout/routing scaffold, and factory "
            "amortization plus error-budget scaffolds close five bookkeeping gaps, but they are not enough "
            "by themselves. A future PR must satisfy the remaining gates, or "
            "bypass the cost-model route by producing 30 occurrence-removing certificates.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--theta-sharing-gate",
        type=Path,
        default=root / "results" / "B1_B7_cone01_theta_sharing_ledger_gate_v0.json",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=root / "results" / "B1_B7_cone01_theta_sharing_cost_model_gate_v0.json",
    )
    parser.add_argument(
        "--shared-object-gate",
        type=Path,
        default=root / "results" / "B1_B7_cone01_shared_theta_synthesis_object_gate_v0.json",
    )
    parser.add_argument(
        "--replay-verifier-gate",
        type=Path,
        default=root / "results" / "B1_B7_cone01_shared_theta_replay_verifier_gate_v0.json",
    )
    parser.add_argument(
        "--layout-routing-gate",
        type=Path,
        default=root / "results" / "B1_B7_cone01_shared_theta_layout_routing_gate_v0.json",
    )
    parser.add_argument(
        "--factory-amortization-gate",
        type=Path,
        default=root / "results" / "B1_B7_cone01_shared_theta_factory_amortization_gate_v0.json",
    )
    parser.add_argument(
        "--error-budget-gate",
        type=Path,
        default=root / "results" / "B1_B7_cone01_shared_theta_error_budget_gate_v0.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=root / "research" / "B1_B7_cone01_theta_sharing_cost_model_gate.md",
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
