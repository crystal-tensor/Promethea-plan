#!/usr/bin/env python3
"""Interleaving-commutation gate for B1/B7 cone_01 carrier blockers.

T-B1-004ac showed that the blocked source-aligned carrier candidates cannot be
cleared by cheap CNOT parity or adjacent duplicate-CNOT cancellation. This gate
checks the next cheap route: whether the single-qubit gates interleaved between
repeated blocker CNOTs are benign enough to commute away without a real
two-qubit semantic synthesis/replay certificate.

The current answer is negative. Some interleavings are control-side diagonal
phases, but every candidate is still blocked by target-side phase or
non-diagonal single-qubit gates. No occurrence-removing rewrite or B7 resource
saving is accepted.
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
    eval_angle_expr,
    load_json,
    split_args,
    write_json,
    write_text,
)


ROOT = Path(__file__).resolve().parents[1]
PARITY_GATE_PATH = ROOT / "results" / "B1_B7_cone01_carrier_blocker_parity_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_carrier_interleaving_commutation_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_carrier_interleaving_commutation_gate.md"

METHOD = "b1_b7_cone01_carrier_interleaving_commutation_gate_v0"
STATUS = "cone01_carrier_interleaving_commutation_negative_gate"
MODEL_STATUS = "interleaved_single_qubit_gates_block_cheap_cnot_commutation_clearance"
SINGLE_QUBIT_RE = re.compile(r"^(u3|rz|rx|ry|u1|u2|u)\((.*)\) q\[(\d+)\];$")
CX_RE = re.compile(r"^cx q\[(\d+)\],q\[(\d+)\];$")
ANGLE_TOLERANCE = 1e-9


def parse_qasm_lines(path: Path) -> dict[int, str]:
    return {idx: line.strip() for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)}


def is_zero_angle(raw: str) -> bool:
    return abs(eval_angle_expr(raw)) <= ANGLE_TOLERANCE


def single_qubit_gate(line: str) -> dict[str, Any] | None:
    match = SINGLE_QUBIT_RE.match(line.strip())
    if not match:
        return None
    gate, raw_args, qubit = match.groups()
    args = split_args(raw_args)
    diagonal = False
    non_diagonal = True
    if gate in {"rz", "u1"}:
        diagonal = True
        non_diagonal = False
    elif gate in {"u3", "u"} and args and is_zero_angle(args[0]):
        diagonal = True
        non_diagonal = False
    return {
        "gate": gate,
        "raw_args": args,
        "qubit": int(qubit),
        "diagonal_z_phase_family": diagonal,
        "non_diagonal_family": non_diagonal,
    }


def cx_orientation(line: str) -> dict[str, int] | None:
    match = CX_RE.match(line.strip())
    if not match:
        return None
    return {"control": int(match.group(1)), "target": int(match.group(2))}


def classify_interleaving(
    qasm_lines: dict[int, str],
    pair: dict[str, Any],
) -> list[dict[str, Any]]:
    orientation = cx_orientation(qasm_lines[int(pair["left_blocker_line"])])
    if orientation is None:
        return []
    rows = []
    for line_number in pair.get("target_single_qubit_lines", []):
        text = qasm_lines[int(line_number)]
        gate = single_qubit_gate(text)
        if gate is None:
            continue
        if gate["qubit"] == orientation["control"]:
            role = "control"
        elif gate["qubit"] == orientation["target"]:
            role = "target"
        else:
            role = "edge_other"

        cheap_commuting = role == "control" and gate["diagonal_z_phase_family"]
        if cheap_commuting:
            obstruction = "control-side diagonal phase commutes with the blocker CNOT"
        elif gate["non_diagonal_family"]:
            obstruction = "non-diagonal single-qubit gate blocks cheap CNOT commutation clearance"
        elif role == "target":
            obstruction = "target-side diagonal phase conjugates through CNOT into an extra control phase"
        else:
            obstruction = "single-qubit interleaving is not accepted as cheap-clearance evidence"

        rows.append(
            {
                "line_number": int(line_number),
                "text": text,
                "gate": gate["gate"],
                "qubit": gate["qubit"],
                "cnot_control": orientation["control"],
                "cnot_target": orientation["target"],
                "role_against_blocker_cnot": role,
                "diagonal_z_phase_family": gate["diagonal_z_phase_family"],
                "non_diagonal_family": gate["non_diagonal_family"],
                "cheap_commuting_control_phase": cheap_commuting,
                "commutation_obstruction": obstruction,
            }
        )
    return rows


def analyze_candidate(candidate: dict[str, Any], qasm_lines: dict[int, str]) -> dict[str, Any]:
    interleavings = [
        row
        for pair in candidate.get("repeated_same_edge_pairs", [])
        for row in classify_interleaving(qasm_lines, pair)
    ]
    control_phase_count = sum(1 for row in interleavings if row["cheap_commuting_control_phase"])
    target_phase_count = sum(
        1
        for row in interleavings
        if row["role_against_blocker_cnot"] == "target" and row["diagonal_z_phase_family"]
    )
    non_diagonal_count = sum(1 for row in interleavings if row["non_diagonal_family"])
    accepted = bool(interleavings) and target_phase_count == 0 and non_diagonal_count == 0
    if accepted:
        reason = "accepted"
    elif non_diagonal_count:
        reason = "non-diagonal interleavings remain inside repeated blocker-CNOT pairs"
    elif target_phase_count:
        reason = "target-side phase interleavings are not a cheap standalone CNOT-cancellation certificate"
    else:
        reason = "no accepted interleaving commutation certificate"
    return {
        "candidate_line_number": int(candidate["candidate_line_number"]),
        "candidate_qubit": int(candidate["candidate_qubit"]),
        "source_distance": int(candidate["source_distance"]),
        "repeated_same_edge_pair_count": int(candidate["repeated_same_edge_pair_count"]),
        "interleaving_op_count": len(interleavings),
        "cheap_commuting_control_phase_count": control_phase_count,
        "target_side_phase_obstruction_count": target_phase_count,
        "non_diagonal_interleaving_count": non_diagonal_count,
        "unique_interleaving_line_count": len({row["line_number"] for row in interleavings}),
        "interleaving_commutation_clearance_accepted": accepted,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "rejection_reason": reason,
        "interleavings": interleavings,
    }


def analyze_row(row: dict[str, Any], qasm_lines: dict[int, str]) -> dict[str, Any]:
    candidates = [
        analyze_candidate(candidate, qasm_lines)
        for candidate in row.get("parity_candidates", [])
    ]
    return {
        "pattern_id": row["pattern_id"],
        "occurrence_count": int(row["occurrence_count"]),
        "target_qubits": row["target_qubits"],
        "commutation_candidate_count": len(candidates),
        "interleaving_op_count": sum(candidate["interleaving_op_count"] for candidate in candidates),
        "cheap_commuting_control_phase_count": sum(
            candidate["cheap_commuting_control_phase_count"] for candidate in candidates
        ),
        "target_side_phase_obstruction_count": sum(
            candidate["target_side_phase_obstruction_count"] for candidate in candidates
        ),
        "non_diagonal_interleaving_count": sum(
            candidate["non_diagonal_interleaving_count"] for candidate in candidates
        ),
        "accepted_interleaving_commutation_clearance_count": sum(
            1 for candidate in candidates if candidate["interleaving_commutation_clearance_accepted"]
        ),
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "commutation_candidates": candidates,
        "claim_boundary": (
            "Single-qubit interleaving classification is a cheap-commutation diagnostic only. "
            "It is not a semantic CNOT-stack rewrite, replay certificate, or B7 resource certificate."
        ),
    }


def build_payload() -> dict[str, Any]:
    source = load_json(PARITY_GATE_PATH)
    qasm_lines = parse_qasm_lines(INVENTORY_QASM_PATH)
    rows = [analyze_row(row, qasm_lines) for row in source.get("carrier_blocker_parity_rows", [])]
    candidates = [candidate for row in rows for candidate in row["commutation_candidates"]]
    interleavings = [
        interleaving
        for candidate in candidates
        for interleaving in candidate["interleavings"]
    ]
    accepted_removed = sum(row["accepted_occurrence_removal"] for row in rows)
    summary = {
        "source_method": source.get("method"),
        "source_status": source.get("status"),
        "inventory_qasm": display_path(INVENTORY_QASM_PATH),
        "pattern_group_count": len(rows),
        "covered_invariant_flat_occurrence_count": sum(row["occurrence_count"] for row in rows),
        "commutation_candidate_count": len(candidates),
        "candidate_with_interleaving_count": sum(
            1 for candidate in candidates if candidate["interleaving_op_count"] > 0
        ),
        "interleaving_op_count": len(interleavings),
        "unique_interleaving_line_count": len({row["line_number"] for row in interleavings}),
        "cheap_commuting_control_phase_count": sum(
            1 for row in interleavings if row["cheap_commuting_control_phase"]
        ),
        "target_side_phase_obstruction_count": sum(
            1
            for row in interleavings
            if row["role_against_blocker_cnot"] == "target" and row["diagonal_z_phase_family"]
        ),
        "non_diagonal_interleaving_count": sum(
            1 for row in interleavings if row["non_diagonal_family"]
        ),
        "candidate_with_non_diagonal_interleaving_count": sum(
            1 for candidate in candidates if candidate["non_diagonal_interleaving_count"] > 0
        ),
        "accepted_interleaving_commutation_clearance_count": sum(
            1 for candidate in candidates if candidate["interleaving_commutation_clearance_accepted"]
        ),
        "interleaving_commutation_gate_passed": False,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": accepted_removed * PROXY_T_PER_OCCURRENCE,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed)
        * PROXY_T_PER_OCCURRENCE,
        "commutation_clearance_claimed": False,
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
        "title": "B1/B7 cone_01 carrier interleaving commutation gate",
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_result": display_path(PARITY_GATE_PATH),
        "source_method": source.get("method"),
        "workload": source.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "summary": summary,
        "carrier_interleaving_commutation_rows": rows,
        "claim_boundary": {
            "commutation_clearance_claimed": False,
            "semantic_certificate_claimed": False,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "Target-side phase and non-diagonal interleavings prevent cheap "
                "standalone CNOT commutation clearance for the current source-aligned candidates."
            ),
            "unsupported_claims": [
                "No semantic CNOT-stack synthesis certificate is produced.",
                "No replay certificate is produced.",
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
        "commutation_candidate_count": 3,
        "candidate_with_interleaving_count": 3,
        "interleaving_op_count": 18,
        "unique_interleaving_line_count": 13,
        "cheap_commuting_control_phase_count": 7,
        "target_side_phase_obstruction_count": 4,
        "non_diagonal_interleaving_count": 7,
        "candidate_with_non_diagonal_interleaving_count": 3,
        "accepted_interleaving_commutation_clearance_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
    }
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if payload.get("source_method") != "b1_b7_cone01_carrier_blocker_parity_gate_v0":
        errors.append("source_method_mismatch")
    for field, value in expected.items():
        if summary.get(field) != value:
            errors.append(f"{field}_mismatch")
    for field in [
        "interleaving_commutation_gate_passed",
        "commutation_clearance_claimed",
        "semantic_certificate_claimed",
        "rewrite_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field}_must_remain_false")
    for field in [
        "commutation_clearance_claimed",
        "semantic_certificate_claimed",
        "rewrite_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if payload["claim_boundary"].get(field) is not False:
            errors.append(f"claim_boundary_{field}_must_remain_false")
    for row in payload.get("carrier_interleaving_commutation_rows", []):
        if row.get("accepted_occurrence_removal") != 0:
            errors.append(f"{row.get('pattern_id')}_accepted_removal_must_be_zero")
        for candidate in row.get("commutation_candidates", []):
            if candidate.get("interleaving_commutation_clearance_accepted"):
                errors.append(f"{row.get('pattern_id')}_{candidate.get('candidate_line_number')}_accepted")
    return errors


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Carrier Interleaving Commutation Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004ac and checks whether the single-qubit gates interleaved between repeated blocker CNOTs are benign enough to commute away without a real two-qubit semantic replay certificate.",
        "",
        "## Summary",
        "",
        f"- Commutation candidates: `{summary['commutation_candidate_count']}`",
        f"- Interleaving single-qubit ops: `{summary['interleaving_op_count']}`",
        f"- Unique interleaving lines: `{summary['unique_interleaving_line_count']}`",
        f"- Cheap control-side phase commutations: `{summary['cheap_commuting_control_phase_count']}`",
        f"- Target-side phase obstructions: `{summary['target_side_phase_obstruction_count']}`",
        f"- Non-diagonal interleaving obstructions: `{summary['non_diagonal_interleaving_count']}`",
        f"- Candidates with non-diagonal interleavings: `{summary['candidate_with_non_diagonal_interleaving_count']}`",
        f"- Accepted interleaving commutation clearances: `{summary['accepted_interleaving_commutation_clearance_count']}`",
        f"- Accepted occurrence/proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Candidate Rows",
        "",
        "| Pattern | Candidate line | Interleavings | Control-side phases | Target-side phases | Non-diagonal gates | Rejection |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["carrier_interleaving_commutation_rows"]:
        for candidate in row["commutation_candidates"]:
            lines.append(
                "| "
                f"{row['pattern_id']} | "
                f"{candidate['candidate_line_number']} | "
                f"{candidate['interleaving_op_count']} | "
                f"{candidate['cheap_commuting_control_phase_count']} | "
                f"{candidate['target_side_phase_obstruction_count']} | "
                f"{candidate['non_diagonal_interleaving_count']} | "
                f"{candidate['rejection_reason']} |"
            )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This is a negative cheap-commutation gate. It does not prove that no semantic CNOT-stack rewrite exists. It only rejects the shortcut where the repeated blocker CNOTs can be cleared by commuting away all intervening single-qubit gates under simple CNOT rules.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.json_out, payload, args.pretty)
    write_text(args.md_out, markdown(payload))
    if args.pretty:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    if payload["validation_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
