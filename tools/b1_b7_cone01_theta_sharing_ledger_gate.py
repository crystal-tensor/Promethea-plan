#!/usr/bin/env python3
"""Theta-sharing ledger gate for B1/B7 cone_01.

T-B1-004e showed that the 35 cone_01 windows collapse into four theta groups,
but every occurrence remains locally parameter-sensitive.  This gate separates
two accounting models:

1. an optimistic template-cache model, where repeated theta values look like
   reusable synthesis templates;
2. the current B7 occurrence ledger, where every physical occurrence still
   pays unless a rewrite certificate removes or shares the occurrence itself.

The artifact is an accounting guardrail. It does not produce a rewrite.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_theta_sharing_ledger_gate_v0"
STATUS = "cone01_theta_sharing_ledger_guardrail"
MODEL_STATUS = "theta_group_cache_accounting_not_occurrence_saving"
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
    transfer = read_json(args.parameter_transfer)
    template_gate = read_json(args.template_gate)
    transfer_summary = transfer["summary"]
    template_summary = template_gate["summary"]

    groups = transfer["angle_groups"]
    candidate_count = int(transfer_summary["candidate_window_count"])
    group_count = int(transfer_summary["distinct_canonical_theta_count"])
    duplicate_occurrences = sum(max(0, int(group["occurrence_count"]) - 1) for group in groups)
    proxy_cost = int(template_gate["proxy_t_cost_per_arbitrary_rotation"])
    target_occurrences = int(template_summary["target_removed_arbitrary_occurrences_for_gcm_h6_1_20"])
    target_proxy_t = int(template_summary["target_removed_t_ledger_for_gcm_h6_1_20"])
    optimistic_cache_proxy_t_reuse = duplicate_occurrences * proxy_cost
    optimistic_cache_clears_target = (
        duplicate_occurrences >= target_occurrences and optimistic_cache_proxy_t_reuse >= target_proxy_t
    )
    occurrence_ledger_removed_occurrences = 0
    occurrence_ledger_proxy_t_reduction = 0
    occurrence_ledger_clears_target = False
    additional_occurrence_certificates_required = target_occurrences

    rows = []
    for group in groups:
        occurrences = int(group["occurrence_count"])
        duplicates = max(0, occurrences - 1)
        rows.append(
            {
                "canonical_theta": group["canonical_theta"],
                "occurrence_count": occurrences,
                "template_cache_duplicate_occurrences": duplicates,
                "optimistic_cache_proxy_t_reuse": duplicates * proxy_cost,
                "occurrence_ledger_removed_occurrences": 0,
                "occurrence_ledger_proxy_t_reduction": 0,
                "line_numbers": group["line_numbers"],
            }
        )

    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 theta-sharing ledger gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_parameter_transfer_gate": display_path(args.parameter_transfer),
        "source_b7_template_gate": display_path(args.template_gate),
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "summary": {
            "candidate_window_count": candidate_count,
            "distinct_theta_group_count": group_count,
            "duplicate_theta_occurrence_count": duplicate_occurrences,
            "proxy_t_cost_per_arbitrary_rotation": proxy_cost,
            "optimistic_cache_proxy_t_reuse": optimistic_cache_proxy_t_reuse,
            "target_removed_arbitrary_occurrences_for_gcm_h6_1_20": target_occurrences,
            "target_proxy_t_ledger_reduction_for_gcm_h6_1_20": target_proxy_t,
            "optimistic_cache_model_clears_target": optimistic_cache_clears_target,
            "occurrence_ledger_removed_occurrences": occurrence_ledger_removed_occurrences,
            "occurrence_ledger_proxy_t_reduction": occurrence_ledger_proxy_t_reduction,
            "occurrence_ledger_clears_target": occurrence_ledger_clears_target,
            "additional_occurrence_certificates_required": additional_occurrence_certificates_required,
            "cache_model_not_accepted_as_ft_ledger": True,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "physical_resource_reduction_claimed": False,
            "validation_error_count": None,
        },
        "theta_group_accounting_rows": rows,
        "claim_boundary": {
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "physical_resource_reduction_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "The four theta groups create an optimistic cache-reuse signal, but under the current "
                "occurrence-based B7 ledger they remove zero physical arbitrary-rotation occurrences."
            ),
            "unsupported_claims": [
                "No cone_01 rewrite certificate is produced.",
                "No B7 FT ledger improvement is counted.",
                "No shared-synthesis cache is accepted as a physical T-ledger reduction.",
                "No hardware layout or factory throughput improvement is claimed.",
            ],
            "next_gate": (
                "Either produce occurrence-removing certificates for at least 30 cone_01 windows, "
                "or define and justify a new B7 cost model where theta sharing is physically countable."
            ),
        },
    }
    errors = validate(payload)
    payload["summary"]["validation_error_count"] = len(errors)
    payload["validation_errors"] = errors
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors = []
    summary = payload["summary"]
    if payload.get("method") != METHOD:
        errors.append("method mismatch")
    if payload.get("status") != STATUS:
        errors.append("status mismatch")
    if summary["candidate_window_count"] != 35:
        errors.append("expected 35 cone_01 candidate windows")
    if summary["distinct_theta_group_count"] != 4:
        errors.append("expected 4 theta groups")
    if summary["duplicate_theta_occurrence_count"] != 31:
        errors.append("expected 31 duplicate theta occurrences under cache model")
    if summary["optimistic_cache_model_clears_target"] is not True:
        errors.append("optimistic cache model should clear the numerical target")
    if summary["occurrence_ledger_clears_target"] is not False:
        errors.append("occurrence ledger must not clear target without occurrence certificates")
    if summary["occurrence_ledger_removed_occurrences"] != 0:
        errors.append("occurrence ledger removed occurrences must remain zero")
    if summary["cache_model_not_accepted_as_ft_ledger"] is not True:
        errors.append("cache model must be marked as not accepted FT ledger")
    for field in [
        "rewrite_claimed",
        "resource_saving_claimed",
        "semantic_certificate_claimed",
        "physical_resource_reduction_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field} must remain false")
        if payload["claim_boundary"].get(field) is not False:
            errors.append(f"claim boundary {field} must remain false")
    if payload["claim_boundary"].get("b7_ledger_improvement_claimed") is not False:
        errors.append("B7 ledger improvement must not be claimed")
    return errors


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Theta-Sharing Ledger Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact separates a tempting cache interpretation from the current B7 "
        "occurrence ledger. The cone_01 windows use only four theta groups, so a "
        "template-cache model sees many repeated theta occurrences. The current B7 "
        "ledger, however, charges physical occurrences unless a replayable rewrite "
        "certificate removes or shares those occurrences in a countable way.",
        "",
        "It is not a rewrite certificate, not a resource-saving claim, and not a "
        "physical-layout claim.",
        "",
        "## Summary",
        "",
        f"- Candidate windows: `{summary['candidate_window_count']}`",
        f"- Distinct theta groups: `{summary['distinct_theta_group_count']}`",
        f"- Duplicate theta occurrences under cache model: `{summary['duplicate_theta_occurrence_count']}`",
        f"- Optimistic cache proxy-T reuse: `{summary['optimistic_cache_proxy_t_reuse']}`",
        f"- Target proxy-T reduction: `{summary['target_proxy_t_ledger_reduction_for_gcm_h6_1_20']}`",
        f"- Optimistic cache model clears target: `{summary['optimistic_cache_model_clears_target']}`",
        f"- Occurrence-ledger removed occurrences: `{summary['occurrence_ledger_removed_occurrences']}`",
        f"- Occurrence-ledger proxy-T reduction: `{summary['occurrence_ledger_proxy_t_reduction']}`",
        f"- Occurrence-ledger clears target: `{summary['occurrence_ledger_clears_target']}`",
        f"- Additional occurrence certificates required: `{summary['additional_occurrence_certificates_required']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Theta Groups",
        "",
        "| canonical theta | occurrences | cache duplicates | optimistic proxy-T reuse | occurrence-ledger reduction |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in payload["theta_group_accounting_rows"]:
        lines.append(
            "| {canonical_theta} | {occurrence_count} | {template_cache_duplicate_occurrences} | "
            "{optimistic_cache_proxy_t_reuse} | {occurrence_ledger_proxy_t_reduction} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The optimistic cache model would appear to clear the numerical B7 target, "
            "because 31 duplicate theta occurrences times a proxy cost of 20 gives "
            "620 proxy-T units. This is deliberately not accepted as a B7 ledger "
            "improvement: the current ledger is occurrence-based, and these repeated "
            "theta values still appear in separate physical windows.",
            "",
            "The next admissible route must either produce at least 30 occurrence-removing "
            "certificates, or define and justify a new physical cost model where theta "
            "sharing reduces the FT ledger.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--parameter-transfer",
        type=Path,
        default=root / "results" / "B1_B7_cone01_parameter_transfer_gate_v0.json",
    )
    parser.add_argument(
        "--template-gate",
        type=Path,
        default=root / "results" / "B7_template_priority_gate_v0.json",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=root / "results" / "B1_B7_cone01_theta_sharing_ledger_gate_v0.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=root / "research" / "B1_B7_cone01_theta_sharing_ledger_gate.md",
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
