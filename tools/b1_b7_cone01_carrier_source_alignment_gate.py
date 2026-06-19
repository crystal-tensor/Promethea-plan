#!/usr/bin/env python3
"""Source-line alignment gate for B1/B7 cone_01 carrier candidates.

T-B1-004y found one blocker-free same-target carrier candidate within a
16-line neighborhood. This gate asks the next syntactic replay question: does
that nearby candidate align with the actual nearest source line it is supposed
to absorb or replace?

The current answer is negative. The only blocker-free radius-16 candidate is
near a partner-qubit Clifford-like RZ line, not a source line on the candidate
qubit, so it remains a search hint rather than a replayable absorption
certificate.
"""

from __future__ import annotations

import argparse
import json
import re
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


ROOT = Path(__file__).resolve().parents[1]
NEIGHBORHOOD_GATE_PATH = (
    ROOT / "results" / "B1_B7_cone01_carrier_neighborhood_commutation_gate_v0.json"
)
JSON_OUT = ROOT / "results" / "B1_B7_cone01_carrier_source_alignment_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_carrier_source_alignment_gate.md"

METHOD = "b1_b7_cone01_carrier_source_alignment_gate_v0"
STATUS = "cone01_carrier_source_alignment_negative_gate"
MODEL_STATUS = "blocker_free_neighborhood_candidate_not_source_line_aligned"
SOURCE_RADIUS = 16
GATE_QUBIT_RE = re.compile(r"q\[(\d+)\]")


def parse_qasm_lines(path: Path) -> dict[int, str]:
    return {idx: line.strip() for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)}


def line_qubits(line: str) -> set[int]:
    return {int(match) for match in GATE_QUBIT_RE.findall(line)}


def source_alignment_row(row: dict[str, Any], qasm_lines: dict[int, str]) -> dict[str, Any]:
    candidates = [
        candidate
        for candidate in row.get("sample_neighborhood_candidates", [])
        if int(candidate.get("source_distance", 10**9)) <= SOURCE_RADIUS
    ]
    reviewed = []
    for candidate in candidates:
        source_line = int(candidate["nearest_source_line"])
        candidate_qubit = int(candidate["qubit"])
        source_text = qasm_lines.get(source_line, "")
        source_qubits = sorted(line_qubits(source_text))
        source_touches_candidate_qubit = candidate_qubit in source_qubits
        source_touches_pattern_target = bool(set(source_qubits).intersection(set(row["target_qubits"])))
        blocker_free = bool(candidate["target_blocker_free"])
        accepted = blocker_free and source_touches_candidate_qubit
        reviewed.append(
            {
                "candidate_line_number": int(candidate["line_number"]),
                "candidate_text": candidate["text"],
                "candidate_qubit": candidate_qubit,
                "nearest_source_line": source_line,
                "nearest_source_text": source_text,
                "nearest_source_qubits": source_qubits,
                "source_distance": int(candidate["source_distance"]),
                "target_blocker_free": blocker_free,
                "source_touches_candidate_qubit": source_touches_candidate_qubit,
                "source_touches_pattern_target": source_touches_pattern_target,
                "source_alignment_certificate_accepted": accepted,
                "rejection_reason": (
                    "accepted"
                    if accepted
                    else "candidate is blocked or nearest source line does not touch the candidate qubit"
                ),
            }
        )
    accepted_count = sum(1 for candidate in reviewed if candidate["source_alignment_certificate_accepted"])
    return {
        "pattern_id": row["pattern_id"],
        "occurrence_count": int(row["occurrence_count"]),
        "target_qubits": row["target_qubits"],
        "nearest_same_target_distance": row["nearest_same_target_distance"],
        "radius_16_candidate_count_reviewed": len(reviewed),
        "blocker_free_radius_16_candidate_count_reviewed": sum(
            1 for candidate in reviewed if candidate["target_blocker_free"]
        ),
        "source_qubit_aligned_radius_16_candidate_count": sum(
            1 for candidate in reviewed if candidate["source_touches_candidate_qubit"]
        ),
        "blocker_free_source_qubit_aligned_candidate_count": accepted_count,
        "accepted_source_alignment_certificate_count": accepted_count,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "reviewed_candidates": reviewed,
        "claim_boundary": (
            "Source-line alignment is a syntactic replay precondition only. Even a passing row "
            "would still require a semantic rewrite certificate before B7 could count savings."
        ),
    }


def build_payload() -> dict[str, Any]:
    source = load_json(NEIGHBORHOOD_GATE_PATH)
    qasm_lines = parse_qasm_lines(INVENTORY_QASM_PATH)
    rows = [source_alignment_row(row, qasm_lines) for row in source.get("carrier_neighborhood_rows", [])]
    reviewed_count = sum(row["radius_16_candidate_count_reviewed"] for row in rows)
    blocker_free_count = sum(row["blocker_free_radius_16_candidate_count_reviewed"] for row in rows)
    source_aligned_count = sum(row["source_qubit_aligned_radius_16_candidate_count"] for row in rows)
    blocker_free_source_aligned_count = sum(
        row["blocker_free_source_qubit_aligned_candidate_count"] for row in rows
    )
    accepted_count = sum(row["accepted_source_alignment_certificate_count"] for row in rows)
    accepted_removed = sum(row["accepted_occurrence_removal"] for row in rows)
    summary = {
        "source_method": source.get("method"),
        "source_status": source.get("status"),
        "inventory_qasm": display_path(INVENTORY_QASM_PATH),
        "pattern_group_count": len(rows),
        "covered_invariant_flat_occurrence_count": sum(row["occurrence_count"] for row in rows),
        "radius_16_candidate_count_reviewed": reviewed_count,
        "blocker_free_radius_16_candidate_count_reviewed": blocker_free_count,
        "source_qubit_aligned_radius_16_candidate_count": source_aligned_count,
        "blocker_free_source_qubit_aligned_candidate_count": blocker_free_source_aligned_count,
        "accepted_source_alignment_certificate_count": accepted_count,
        "patterns_with_reviewed_radius_16_candidate": [
            row["pattern_id"] for row in rows if row["radius_16_candidate_count_reviewed"] > 0
        ],
        "patterns_with_blocker_free_radius_16_candidate": [
            row["pattern_id"] for row in rows if row["blocker_free_radius_16_candidate_count_reviewed"] > 0
        ],
        "patterns_with_source_qubit_aligned_candidate": [
            row["pattern_id"] for row in rows if row["source_qubit_aligned_radius_16_candidate_count"] > 0
        ],
        "patterns_with_blocker_free_source_qubit_aligned_candidate": [
            row["pattern_id"] for row in rows if row["blocker_free_source_qubit_aligned_candidate_count"] > 0
        ],
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": accepted_removed * PROXY_T_PER_OCCURRENCE,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed)
        * PROXY_T_PER_OCCURRENCE,
        "source_alignment_certificate_claimed": False,
        "commutation_certificate_claimed": False,
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
        "title": "B1/B7 cone_01 carrier source alignment gate",
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_result": display_path(NEIGHBORHOOD_GATE_PATH),
        "source_method": source.get("method"),
        "workload": source.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "summary": summary,
        "carrier_source_alignment_rows": rows,
        "claim_boundary": {
            "source_alignment_certificate_claimed": False,
            "commutation_certificate_claimed": False,
            "semantic_certificate_claimed": False,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "The only blocker-free radius-16 carrier candidate does not touch the nearest "
                "source line qubit and is not accepted as an absorption certificate."
            ),
            "unsupported_claims": [
                "No carrier absorption certificate is produced.",
                "No commutation or semantic replay certificate is produced.",
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
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if payload.get("source_method") != "b1_b7_cone01_carrier_neighborhood_commutation_gate_v0":
        errors.append("source_method_mismatch")
    expected = {
        "pattern_group_count": 3,
        "covered_invariant_flat_occurrence_count": 11,
        "radius_16_candidate_count_reviewed": 5,
        "blocker_free_radius_16_candidate_count_reviewed": 1,
        "source_qubit_aligned_radius_16_candidate_count": 3,
        "blocker_free_source_qubit_aligned_candidate_count": 0,
        "accepted_source_alignment_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
    }
    for field, value in expected.items():
        if summary.get(field) != value:
            errors.append(f"{field}_mismatch")
    if summary.get("patterns_with_reviewed_radius_16_candidate") != ["flat_pattern_01"]:
        errors.append("patterns_with_reviewed_radius_16_candidate_mismatch")
    if summary.get("patterns_with_blocker_free_radius_16_candidate") != ["flat_pattern_01"]:
        errors.append("patterns_with_blocker_free_radius_16_candidate_mismatch")
    if summary.get("patterns_with_source_qubit_aligned_candidate") != ["flat_pattern_01"]:
        errors.append("patterns_with_source_qubit_aligned_candidate_mismatch")
    if summary.get("patterns_with_blocker_free_source_qubit_aligned_candidate") != []:
        errors.append("patterns_with_blocker_free_source_qubit_aligned_candidate_mismatch")
    for row in payload.get("carrier_source_alignment_rows", []):
        if row.get("accepted_source_alignment_certificate_count") != 0:
            errors.append(f"{row.get('pattern_id')}_accepted_alignment_count_must_be_zero")
        if row.get("accepted_occurrence_removal") != 0:
            errors.append(f"{row.get('pattern_id')}_accepted_removal_must_be_zero")
    for field in [
        "source_alignment_certificate_claimed",
        "commutation_certificate_claimed",
        "semantic_certificate_claimed",
        "rewrite_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field}_must_remain_false")
        if payload["claim_boundary"].get(field) is not False:
            errors.append(f"claim_boundary_{field}_must_remain_false")
    return errors


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Carrier Source Alignment Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004y and checks whether nearby carrier candidates align with their nearest source lines.",
        "",
        "## Summary",
        "",
        f"- Reviewed radius-16 candidates: `{summary['radius_16_candidate_count_reviewed']}`",
        f"- Blocker-free radius-16 candidates: `{summary['blocker_free_radius_16_candidate_count_reviewed']}`",
        f"- Source-qubit-aligned candidates: `{summary['source_qubit_aligned_radius_16_candidate_count']}`",
        f"- Blocker-free and source-qubit-aligned candidates: `{summary['blocker_free_source_qubit_aligned_candidate_count']}`",
        f"- Accepted source-alignment certificates: `{summary['accepted_source_alignment_certificate_count']}`",
        f"- Accepted occurrence/proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Rows",
        "",
        "| Pattern | Reviewed | Blocker-free | Source-aligned | Blocker-free source-aligned | Accepted |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["carrier_source_alignment_rows"]:
        lines.append(
            f"| {row['pattern_id']} | {row['radius_16_candidate_count_reviewed']} | "
            f"{row['blocker_free_radius_16_candidate_count_reviewed']} | "
            f"{row['source_qubit_aligned_radius_16_candidate_count']} | "
            f"{row['blocker_free_source_qubit_aligned_candidate_count']} | "
            f"{row['accepted_source_alignment_certificate_count']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- The only blocker-free radius-16 candidate is not aligned with the nearest source-line qubit.",
            "- A source-line alignment pass would still be only a replay precondition.",
            "- No commutation, semantic rewrite, occurrence removal, or B7 ledger improvement is claimed.",
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
