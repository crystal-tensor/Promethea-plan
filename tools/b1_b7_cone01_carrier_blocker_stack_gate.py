#!/usr/bin/env python3
"""Blocker-stack gate for B1/B7 cone_01 carrier candidates.

T-B1-004z found that no radius-16 candidate is both blocker-free and
source-line aligned. This gate inspects the source-aligned candidates that fail
only because of intervening target-touching CNOTs.

The current answer is negative for simple commutation clearing: all
source-aligned candidates are blocked, with 15 target-touching CNOT blockers in
total and 14 touching the candidate qubit directly.
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
SOURCE_ALIGNMENT_GATE_PATH = (
    ROOT / "results" / "B1_B7_cone01_carrier_source_alignment_gate_v0.json"
)
JSON_OUT = ROOT / "results" / "B1_B7_cone01_carrier_blocker_stack_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_carrier_blocker_stack_gate.md"

METHOD = "b1_b7_cone01_carrier_blocker_stack_gate_v0"
STATUS = "cone01_carrier_blocker_stack_negative_gate"
MODEL_STATUS = "source_aligned_candidates_have_target_touching_cx_blocker_stacks"
CX_RE = re.compile(r"^cx q\[(\d+)\],q\[(\d+)\];$")


def parse_qasm_lines(path: Path) -> dict[int, str]:
    return {idx: line.strip() for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)}


def cx_qubits(line: str) -> set[int]:
    match = CX_RE.match(line.strip())
    if not match:
        return set()
    return {int(match.group(1)), int(match.group(2))}


def target_cx_blockers(
    qasm_lines: dict[int, str],
    candidate_line: int,
    source_line: int,
    target_qubits: set[int],
    candidate_qubit: int,
) -> list[dict[str, Any]]:
    lower = min(candidate_line, source_line) + 1
    upper = max(candidate_line, source_line)
    blockers = []
    for line_number in range(lower, upper):
        qubits = cx_qubits(qasm_lines.get(line_number, ""))
        if not qubits or not qubits.intersection(target_qubits):
            continue
        blockers.append(
            {
                "line_number": line_number,
                "text": qasm_lines[line_number],
                "qubits": sorted(qubits),
                "touches_candidate_qubit": candidate_qubit in qubits,
                "touches_target_qubit": True,
                "edge_signature": "-".join(str(q) for q in sorted(qubits)),
            }
        )
    return blockers


def analyze_row(row: dict[str, Any], qasm_lines: dict[int, str]) -> dict[str, Any]:
    target_qubits = set(int(q) for q in row["target_qubits"])
    source_aligned = [
        candidate for candidate in row.get("reviewed_candidates", []) if candidate["source_touches_candidate_qubit"]
    ]
    candidate_rows = []
    for candidate in source_aligned:
        blockers = target_cx_blockers(
            qasm_lines=qasm_lines,
            candidate_line=int(candidate["candidate_line_number"]),
            source_line=int(candidate["nearest_source_line"]),
            target_qubits=target_qubits,
            candidate_qubit=int(candidate["candidate_qubit"]),
        )
        candidate_qubit_blockers = [blocker for blocker in blockers if blocker["touches_candidate_qubit"]]
        non_candidate_target_blockers = [
            blocker for blocker in blockers if not blocker["touches_candidate_qubit"]
        ]
        accepted = len(blockers) == 0
        candidate_rows.append(
            {
                "candidate_line_number": int(candidate["candidate_line_number"]),
                "candidate_text": candidate["candidate_text"],
                "candidate_qubit": int(candidate["candidate_qubit"]),
                "nearest_source_line": int(candidate["nearest_source_line"]),
                "nearest_source_text": candidate["nearest_source_text"],
                "source_distance": int(candidate["source_distance"]),
                "target_blocker_count": len(blockers),
                "candidate_qubit_blocker_count": len(candidate_qubit_blockers),
                "non_candidate_target_blocker_count": len(non_candidate_target_blockers),
                "unique_blocker_edge_signatures": sorted(
                    {blocker["edge_signature"] for blocker in blockers}
                ),
                "target_cx_blockers": blockers,
                "simple_commutation_clearance_accepted": accepted,
                "rejection_reason": (
                    "accepted"
                    if accepted
                    else "source-aligned candidate has intervening target-touching CNOT blockers"
                ),
            }
        )
    accepted_count = sum(1 for candidate in candidate_rows if candidate["simple_commutation_clearance_accepted"])
    total_blockers = sum(candidate["target_blocker_count"] for candidate in candidate_rows)
    return {
        "pattern_id": row["pattern_id"],
        "occurrence_count": int(row["occurrence_count"]),
        "target_qubits": row["target_qubits"],
        "source_aligned_candidate_count": len(source_aligned),
        "source_aligned_blocked_candidate_count": len(source_aligned) - accepted_count,
        "total_source_aligned_target_blocker_count": total_blockers,
        "candidate_qubit_blocker_count": sum(
            candidate["candidate_qubit_blocker_count"] for candidate in candidate_rows
        ),
        "non_candidate_target_blocker_count": sum(
            candidate["non_candidate_target_blocker_count"] for candidate in candidate_rows
        ),
        "unique_target_blocker_line_count": len(
            {
                blocker["line_number"]
                for candidate in candidate_rows
                for blocker in candidate["target_cx_blockers"]
            }
        ),
        "unique_blocker_edge_signatures": sorted(
            {
                blocker["edge_signature"]
                for candidate in candidate_rows
                for blocker in candidate["target_cx_blockers"]
            }
        ),
        "accepted_simple_commutation_clearance_count": accepted_count,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "source_aligned_candidates": candidate_rows,
        "claim_boundary": (
            "A source-aligned but blocked carrier candidate is a blocker-stack diagnostic only. "
            "It is not a commutation, rewrite, semantic, or B7 resource certificate."
        ),
    }


def build_payload() -> dict[str, Any]:
    source = load_json(SOURCE_ALIGNMENT_GATE_PATH)
    qasm_lines = parse_qasm_lines(INVENTORY_QASM_PATH)
    rows = [analyze_row(row, qasm_lines) for row in source.get("carrier_source_alignment_rows", [])]
    accepted_removed = sum(row["accepted_occurrence_removal"] for row in rows)
    summary = {
        "source_method": source.get("method"),
        "source_status": source.get("status"),
        "inventory_qasm": display_path(INVENTORY_QASM_PATH),
        "pattern_group_count": len(rows),
        "covered_invariant_flat_occurrence_count": sum(row["occurrence_count"] for row in rows),
        "source_aligned_candidate_count": sum(row["source_aligned_candidate_count"] for row in rows),
        "source_aligned_blocked_candidate_count": sum(
            row["source_aligned_blocked_candidate_count"] for row in rows
        ),
        "total_source_aligned_target_blocker_count": sum(
            row["total_source_aligned_target_blocker_count"] for row in rows
        ),
        "candidate_qubit_blocker_count": sum(row["candidate_qubit_blocker_count"] for row in rows),
        "non_candidate_target_blocker_count": sum(
            row["non_candidate_target_blocker_count"] for row in rows
        ),
        "unique_target_blocker_line_count": len(
            {
                blocker["line_number"]
                for row in rows
                for candidate in row["source_aligned_candidates"]
                for blocker in candidate["target_cx_blockers"]
            }
        ),
        "unique_blocker_edge_signatures": sorted(
            {
                blocker["edge_signature"]
                for row in rows
                for candidate in row["source_aligned_candidates"]
                for blocker in candidate["target_cx_blockers"]
            }
        ),
        "patterns_with_source_aligned_candidates": [
            row["pattern_id"] for row in rows if row["source_aligned_candidate_count"] > 0
        ],
        "patterns_with_source_aligned_blocked_candidates": [
            row["pattern_id"] for row in rows if row["source_aligned_blocked_candidate_count"] > 0
        ],
        "accepted_simple_commutation_clearance_count": sum(
            row["accepted_simple_commutation_clearance_count"] for row in rows
        ),
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": accepted_removed * PROXY_T_PER_OCCURRENCE,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed)
        * PROXY_T_PER_OCCURRENCE,
        "blocker_clearance_certificate_claimed": False,
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
        "title": "B1/B7 cone_01 carrier blocker stack gate",
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_result": display_path(SOURCE_ALIGNMENT_GATE_PATH),
        "source_method": source.get("method"),
        "workload": source.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "summary": summary,
        "carrier_blocker_stack_rows": rows,
        "claim_boundary": {
            "blocker_clearance_certificate_claimed": False,
            "commutation_certificate_claimed": False,
            "semantic_certificate_claimed": False,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "Every source-aligned candidate is blocked by target-touching CNOTs; "
                "simple commutation clearance is not accepted."
            ),
            "unsupported_claims": [
                "No blocker-clearance certificate is produced.",
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
    expected = {
        "pattern_group_count": 3,
        "covered_invariant_flat_occurrence_count": 11,
        "source_aligned_candidate_count": 3,
        "source_aligned_blocked_candidate_count": 3,
        "total_source_aligned_target_blocker_count": 15,
        "candidate_qubit_blocker_count": 14,
        "non_candidate_target_blocker_count": 1,
        "unique_target_blocker_line_count": 11,
        "accepted_simple_commutation_clearance_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
    }
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if payload.get("source_method") != "b1_b7_cone01_carrier_source_alignment_gate_v0":
        errors.append("source_method_mismatch")
    for field, value in expected.items():
        if summary.get(field) != value:
            errors.append(f"{field}_mismatch")
    if summary.get("unique_blocker_edge_signatures") != ["10-14", "2-14", "4-8"]:
        errors.append("unique_blocker_edge_signatures_mismatch")
    if summary.get("patterns_with_source_aligned_candidates") != ["flat_pattern_01"]:
        errors.append("patterns_with_source_aligned_candidates_mismatch")
    if summary.get("patterns_with_source_aligned_blocked_candidates") != ["flat_pattern_01"]:
        errors.append("patterns_with_source_aligned_blocked_candidates_mismatch")
    for row in payload.get("carrier_blocker_stack_rows", []):
        if row.get("accepted_occurrence_removal") != 0:
            errors.append(f"{row.get('pattern_id')}_accepted_removal_must_be_zero")
        for candidate in row.get("source_aligned_candidates", []):
            if candidate.get("simple_commutation_clearance_accepted"):
                errors.append(f"{row.get('pattern_id')}_{candidate.get('candidate_line_number')}_must_not_clear")
    for field in [
        "blocker_clearance_certificate_claimed",
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
        "# B1/B7 Cone_01 Carrier Blocker Stack Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004z and checks whether source-aligned carrier candidates can be cleared by a simple blocker-stack condition.",
        "",
        "## Summary",
        "",
        f"- Source-aligned candidates: `{summary['source_aligned_candidate_count']}`",
        f"- Source-aligned blocked candidates: `{summary['source_aligned_blocked_candidate_count']}`",
        f"- Target-touching CNOT blockers across source-aligned candidates: `{summary['total_source_aligned_target_blocker_count']}`",
        f"- Candidate-qubit blockers / other target blockers: `{summary['candidate_qubit_blocker_count']}` / `{summary['non_candidate_target_blocker_count']}`",
        f"- Unique blocker lines: `{summary['unique_target_blocker_line_count']}`",
        f"- Unique blocker edge signatures: `{', '.join(summary['unique_blocker_edge_signatures'])}`",
        f"- Accepted simple commutation-clearance certificates: `{summary['accepted_simple_commutation_clearance_count']}`",
        f"- Accepted occurrence/proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Rows",
        "",
        "| Pattern | Source-aligned | Blocked | Target CNOT blockers | Candidate-qubit blockers | Other target blockers | Accepted |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["carrier_blocker_stack_rows"]:
        lines.append(
            f"| {row['pattern_id']} | {row['source_aligned_candidate_count']} | "
            f"{row['source_aligned_blocked_candidate_count']} | "
            f"{row['total_source_aligned_target_blocker_count']} | "
            f"{row['candidate_qubit_blocker_count']} | "
            f"{row['non_candidate_target_blocker_count']} | "
            f"{row['accepted_simple_commutation_clearance_count']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Every source-aligned candidate is blocked by target-touching CNOTs.",
            "- Fourteen of fifteen blockers touch the candidate qubit directly, so this is not a single-qubit commute-through issue.",
            "- No blocker-clearance, commutation, semantic rewrite, occurrence removal, or B7 ledger improvement is claimed.",
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
