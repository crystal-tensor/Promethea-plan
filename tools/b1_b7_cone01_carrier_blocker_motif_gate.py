#!/usr/bin/env python3
"""Blocker-motif gate for B1/B7 cone_01 carrier candidates.

T-B1-004aa showed that every source-aligned carrier candidate is blocked by
target-touching CNOT stacks. This gate asks whether those blocker stacks form a
single reusable motif that could justify a narrow template-synthesis branch.

The current answer is negative: the exact blocker stacks are three distinct
motifs, the largest edge-family group covers only two candidates, and no
cross-pattern blocker motif exists.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    load_json,
    write_json,
    write_text,
)


ROOT = Path(__file__).resolve().parents[1]
BLOCKER_STACK_GATE_PATH = ROOT / "results" / "B1_B7_cone01_carrier_blocker_stack_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_carrier_blocker_motif_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_carrier_blocker_motif_gate.md"

METHOD = "b1_b7_cone01_carrier_blocker_motif_gate_v0"
STATUS = "cone01_carrier_blocker_motif_negative_gate"
MODEL_STATUS = "blocker_stacks_do_not_form_single_reusable_template_motif"


def exact_stack_signature(blockers: list[dict[str, Any]]) -> str:
    return "|".join(blocker["edge_signature"] for blocker in blockers)


def edge_family_signature(blockers: list[dict[str, Any]]) -> str:
    return "+".join(sorted({blocker["edge_signature"] for blocker in blockers}))


def analyze_row(row: dict[str, Any]) -> dict[str, Any]:
    motif_candidates = []
    for candidate in row.get("source_aligned_candidates", []):
        blockers = candidate.get("target_cx_blockers", [])
        exact_signature = exact_stack_signature(blockers)
        family_signature = edge_family_signature(blockers)
        edge_counts = Counter(blocker["edge_signature"] for blocker in blockers)
        motif_candidates.append(
            {
                "candidate_line_number": candidate["candidate_line_number"],
                "candidate_qubit": candidate["candidate_qubit"],
                "nearest_source_line": candidate["nearest_source_line"],
                "source_distance": candidate["source_distance"],
                "stack_length": len(blockers),
                "exact_stack_signature": exact_signature,
                "edge_family_signature": family_signature,
                "edge_counts": dict(sorted(edge_counts.items())),
                "single_edge_stack": len(edge_counts) == 1,
                "dominant_edge_signature": edge_counts.most_common(1)[0][0] if edge_counts else None,
                "dominant_edge_count": edge_counts.most_common(1)[0][1] if edge_counts else 0,
                "template_generalization_accepted": False,
                "rejection_reason": "no exact repeated motif or cross-pattern motif certificate",
            }
        )
    exact_counts = Counter(candidate["exact_stack_signature"] for candidate in motif_candidates)
    family_counts = Counter(candidate["edge_family_signature"] for candidate in motif_candidates)
    return {
        "pattern_id": row["pattern_id"],
        "occurrence_count": int(row["occurrence_count"]),
        "motif_candidate_count": len(motif_candidates),
        "unique_exact_stack_motif_count": len(exact_counts),
        "unique_edge_family_motif_count": len(family_counts),
        "largest_exact_stack_motif_candidate_count": max(exact_counts.values(), default=0),
        "largest_edge_family_motif_candidate_count": max(family_counts.values(), default=0),
        "single_edge_stack_candidate_count": sum(1 for candidate in motif_candidates if candidate["single_edge_stack"]),
        "mixed_edge_stack_candidate_count": sum(1 for candidate in motif_candidates if not candidate["single_edge_stack"]),
        "all_candidates_share_exact_stack_motif": len(exact_counts) == 1 and bool(motif_candidates),
        "all_candidates_share_edge_family_motif": len(family_counts) == 1 and bool(motif_candidates),
        "accepted_template_motif_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "motif_candidates": motif_candidates,
        "claim_boundary": (
            "Blocker motif grouping is a template-prioritization diagnostic only; it is not "
            "a CNOT-stack rewrite, semantic replay certificate, or B7 resource certificate."
        ),
    }


def build_payload() -> dict[str, Any]:
    source = load_json(BLOCKER_STACK_GATE_PATH)
    rows = [analyze_row(row) for row in source.get("carrier_blocker_stack_rows", [])]
    all_candidates = [candidate for row in rows for candidate in row["motif_candidates"]]
    exact_counts = Counter(candidate["exact_stack_signature"] for candidate in all_candidates)
    family_counts = Counter(candidate["edge_family_signature"] for candidate in all_candidates)
    accepted_removed = sum(row["accepted_occurrence_removal"] for row in rows)
    summary = {
        "source_method": source.get("method"),
        "source_status": source.get("status"),
        "pattern_group_count": len(rows),
        "covered_invariant_flat_occurrence_count": sum(row["occurrence_count"] for row in rows),
        "source_aligned_candidate_count": source.get("summary", {}).get("source_aligned_candidate_count"),
        "blocker_motif_candidate_count": len(all_candidates),
        "unique_exact_stack_motif_count": len(exact_counts),
        "unique_edge_family_motif_count": len(family_counts),
        "largest_exact_stack_motif_candidate_count": max(exact_counts.values(), default=0),
        "largest_edge_family_motif_candidate_count": max(family_counts.values(), default=0),
        "single_edge_stack_candidate_count": sum(1 for candidate in all_candidates if candidate["single_edge_stack"]),
        "mixed_edge_stack_candidate_count": sum(1 for candidate in all_candidates if not candidate["single_edge_stack"]),
        "patterns_with_blocker_motif_candidates": [
            row["pattern_id"] for row in rows if row["motif_candidate_count"] > 0
        ],
        "patterns_without_blocker_motif_candidates": [
            row["pattern_id"] for row in rows if row["motif_candidate_count"] == 0
        ],
        "all_candidates_share_exact_stack_motif": len(exact_counts) == 1 and bool(all_candidates),
        "all_candidates_share_edge_family_motif": len(family_counts) == 1 and bool(all_candidates),
        "cross_pattern_motif_present": False,
        "template_generalization_gate_passed": False,
        "accepted_template_motif_count": 0,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": accepted_removed * PROXY_T_PER_OCCURRENCE,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed)
        * PROXY_T_PER_OCCURRENCE,
        "template_rewrite_claimed": False,
        "semantic_certificate_claimed": False,
        "rewrite_claimed": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": None,
    }
    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 carrier blocker motif gate",
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_result": display_path(BLOCKER_STACK_GATE_PATH),
        "source_method": source.get("method"),
        "workload": source.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "summary": summary,
        "carrier_blocker_motif_rows": rows,
        "claim_boundary": {
            "template_rewrite_claimed": False,
            "semantic_certificate_claimed": False,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "The blocked source-aligned candidates do not share a single exact or "
                "cross-pattern blocker motif."
            ),
            "unsupported_claims": [
                "No CNOT-stack template rewrite is produced.",
                "No semantic replay certificate is produced.",
                "No occurrence is removed from the B7 ledger.",
            ],
        },
    }
    errors = validate(payload)
    payload["summary"]["validation_error_count"] = len(errors)
    payload["validation_errors"] = errors
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload["summary"]
    expected = {
        "pattern_group_count": 3,
        "covered_invariant_flat_occurrence_count": 11,
        "source_aligned_candidate_count": 3,
        "blocker_motif_candidate_count": 3,
        "unique_exact_stack_motif_count": 3,
        "unique_edge_family_motif_count": 2,
        "largest_exact_stack_motif_candidate_count": 1,
        "largest_edge_family_motif_candidate_count": 2,
        "single_edge_stack_candidate_count": 2,
        "mixed_edge_stack_candidate_count": 1,
        "accepted_template_motif_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
    }
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if payload.get("source_method") != "b1_b7_cone01_carrier_blocker_stack_gate_v0":
        errors.append("source_method_mismatch")
    for field, value in expected.items():
        if summary.get(field) != value:
            errors.append(f"{field}_mismatch")
    if summary.get("patterns_with_blocker_motif_candidates") != ["flat_pattern_01"]:
        errors.append("patterns_with_blocker_motif_candidates_mismatch")
    if summary.get("patterns_without_blocker_motif_candidates") != ["flat_pattern_02", "flat_pattern_03"]:
        errors.append("patterns_without_blocker_motif_candidates_mismatch")
    for field in [
        "all_candidates_share_exact_stack_motif",
        "all_candidates_share_edge_family_motif",
        "cross_pattern_motif_present",
        "template_generalization_gate_passed",
        "template_rewrite_claimed",
        "semantic_certificate_claimed",
        "rewrite_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field}_must_remain_false")
    for field in [
        "template_rewrite_claimed",
        "semantic_certificate_claimed",
        "rewrite_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if payload["claim_boundary"].get(field) is not False:
            errors.append(f"claim_boundary_{field}_must_remain_false")
    for row in payload.get("carrier_blocker_motif_rows", []):
        if row.get("accepted_occurrence_removal") != 0:
            errors.append(f"{row.get('pattern_id')}_accepted_removal_must_be_zero")
        for candidate in row.get("motif_candidates", []):
            if candidate.get("template_generalization_accepted"):
                errors.append(f"{row.get('pattern_id')}_{candidate.get('candidate_line_number')}_accepted")
    return errors


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Carrier Blocker Motif Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004aa and checks whether blocked source-aligned carrier candidates share a reusable CNOT-stack motif.",
        "",
        "## Summary",
        "",
        f"- Blocker motif candidates: `{summary['blocker_motif_candidate_count']}`",
        f"- Unique exact stack motifs: `{summary['unique_exact_stack_motif_count']}`",
        f"- Unique edge-family motifs: `{summary['unique_edge_family_motif_count']}`",
        f"- Largest exact stack / edge-family candidate group: `{summary['largest_exact_stack_motif_candidate_count']}` / `{summary['largest_edge_family_motif_candidate_count']}`",
        f"- Single-edge / mixed-edge stack candidates: `{summary['single_edge_stack_candidate_count']}` / `{summary['mixed_edge_stack_candidate_count']}`",
        f"- Cross-pattern motif present: `{summary['cross_pattern_motif_present']}`",
        f"- Template generalization gate passed: `{summary['template_generalization_gate_passed']}`",
        f"- Accepted occurrence/proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Rows",
        "",
        "| Pattern | Candidates | Exact motifs | Edge-family motifs | Largest exact | Largest family | Accepted motifs |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["carrier_blocker_motif_rows"]:
        lines.append(
            f"| {row['pattern_id']} | {row['motif_candidate_count']} | "
            f"{row['unique_exact_stack_motif_count']} | {row['unique_edge_family_motif_count']} | "
            f"{row['largest_exact_stack_motif_candidate_count']} | "
            f"{row['largest_edge_family_motif_candidate_count']} | "
            f"{row['accepted_template_motif_count']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- The exact blocker stacks are three distinct motifs.",
            "- The largest edge-family group covers only two candidates and no cross-pattern motif exists.",
            "- No CNOT-stack template rewrite, semantic replay, occurrence removal, or B7 ledger improvement is claimed.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.json_out, payload, args.pretty)
    write_text(args.md_out, markdown(payload))
    print(json.dumps(payload["summary"], indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
