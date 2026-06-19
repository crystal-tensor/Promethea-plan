#!/usr/bin/env python3
"""Local-Clifford dressing gate for B1/B7 cone_01 flat packets.

T-B1-004r showed that arbitrary SU(2)xSU(2) local dressing can numerically
match the three flat-pattern packets. T-B1-004s showed that direct pi/4 Euler
projection does not exactify those dressings. This gate checks a stricter
resource-accounting route: does any exact local Clifford dressing on both sides
of the nearest-grid representative reproduce the original packet?

The search is finite: 24 one-qubit Clifford representatives produce 576 pair-
local Clifford representatives, and each packet checks all 576 x 576 left/right
local dressings. A pass would be a strong candidate for a replayable exact
certificate. A fail closes the "plain local Clifford dressing" route only; it
does not prove that no non-Clifford exact rewrite exists.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np

from b1_b7_cone01_flat_pattern_kak_packet import parse_normalized_op, replace_target_ry_with_grid
from b1_b7_cone01_phase_removal_gate import EXACT_TOLERANCE, residual_norm, unitary_for_ops


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKET_PATH = ROOT / "results" / "B1_B7_cone01_flat_pattern_kak_packet_v0.json"
SOURCE_ABSORPTION_PATH = ROOT / "results" / "B1_B7_cone01_dressing_absorption_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_local_clifford_dressing_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_local_clifford_dressing_gate.md"

METHOD = "b1_b7_cone01_local_clifford_dressing_gate_v0"
STATUS = "cone01_local_clifford_dressing_negative_gate"
MODEL_STATUS = "no_plain_local_clifford_dressing_certificate_found"
PROXY_T_PER_OCCURRENCE = 20
REQUIRED_OCCURRENCE_REMOVALS = 30


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def canonical_key(matrix: np.ndarray, digits: int = 10) -> tuple[tuple[float, float], ...]:
    flat = matrix.ravel()
    anchor = next((value for value in flat if abs(value) > 1e-10), 1.0 + 0.0j)
    normalized = matrix * np.exp(-1j * np.angle(anchor))
    return tuple((round(float(value.real), digits), round(float(value.imag), digits)) for value in normalized.ravel())


def one_qubit_cliffords() -> list[dict[str, Any]]:
    h = (1.0 / math.sqrt(2.0)) * np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex)
    s = np.array([[1.0, 0.0], [0.0, 1.0j]], dtype=complex)
    generators = [("H", h), ("S", s)]
    start = np.eye(2, dtype=complex)
    seen = {canonical_key(start)}
    queue: deque[tuple[str, np.ndarray]] = deque([("I", start)])
    rows: list[dict[str, Any]] = []
    while queue:
        label, matrix = queue.popleft()
        rows.append({"label": label, "matrix": matrix})
        for gen_label, gen_matrix in generators:
            candidate = gen_matrix @ matrix
            key = canonical_key(candidate)
            if key not in seen:
                seen.add(key)
                queue.append((f"{gen_label}{label}" if label != "I" else gen_label, candidate))
    rows.sort(key=lambda row: row["label"])
    return rows


def pair_local_cliffords(single_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for partner in single_rows:
        for target in single_rows:
            rows.append(
                {
                    "label": f"{partner['label']}|{target['label']}",
                    "matrix": np.kron(partner["matrix"], target["matrix"]),
                }
            )
    return rows


def reconstruct_pattern(packet: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    ops = [parse_normalized_op(text) for text in packet["normalized_window_text"]]
    target = unitary_for_ops(ops, [0, 1])
    grid_ops = replace_target_ry_with_grid(ops, float(packet["nearest_grid_angle"]))
    return target, unitary_for_ops(grid_ops, [0, 1])


def analyze_packet(packet: dict[str, Any], pair_rows: list[dict[str, Any]]) -> dict[str, Any]:
    target, grid_unitary = reconstruct_pattern(packet)
    best: dict[str, Any] | None = None
    exact_pass_count = 0
    trial_count = 0
    for left in pair_rows:
        left_grid = left["matrix"] @ grid_unitary
        for right in pair_rows:
            trial_count += 1
            residual = residual_norm(left_grid @ right["matrix"], target)
            if residual <= EXACT_TOLERANCE:
                exact_pass_count += 1
            if best is None or residual < best["residual_norm"]:
                best = {
                    "left_pair_label": left["label"],
                    "right_pair_label": right["label"],
                    "residual_norm": residual,
                }
    assert best is not None
    return {
        "pattern_id": packet["pattern_id"],
        "occurrence_count": packet["occurrence_count"],
        "nearest_grid_label": packet["nearest_grid_label"],
        "same_envelope_grid_residual_norm": packet["same_envelope_grid_residual_norm"],
        "local_clifford_left_right_trial_count": trial_count,
        "local_clifford_exact_pass_count": exact_pass_count,
        "local_clifford_exact_pass": exact_pass_count > 0,
        "best_local_clifford_residual_norm": best["residual_norm"],
        "best_local_clifford_labels": {
            "left_pair_label": best["left_pair_label"],
            "right_pair_label": best["right_pair_label"],
        },
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
    }


def build_payload() -> dict[str, Any]:
    packet_payload = load_json(SOURCE_PACKET_PATH)
    absorption_payload = load_json(SOURCE_ABSORPTION_PATH)
    single_rows = one_qubit_cliffords()
    pair_rows = pair_local_cliffords(single_rows)
    pattern_rows = [analyze_packet(packet, pair_rows) for packet in packet_payload["pattern_packets"]]
    exact_packet_count = sum(1 for row in pattern_rows if row["local_clifford_exact_pass"])
    accepted_occurrence_removal = sum(row["accepted_occurrence_removal"] for row in pattern_rows)
    missing_occurrences = REQUIRED_OCCURRENCE_REMOVALS - accepted_occurrence_removal
    summary = {
        "source_method": packet_payload.get("method"),
        "source_status": packet_payload.get("status"),
        "source_absorption_method": absorption_payload.get("method"),
        "source_absorption_status": absorption_payload.get("status"),
        "single_qubit_clifford_count": len(single_rows),
        "pair_local_clifford_count": len(pair_rows),
        "left_right_pair_trial_count_per_pattern": len(pair_rows) * len(pair_rows),
        "pattern_group_count": len(pattern_rows),
        "covered_invariant_flat_occurrence_count": sum(int(row["occurrence_count"]) for row in pattern_rows),
        "local_clifford_exact_packet_count": exact_packet_count,
        "all_packets_have_local_clifford_dressing": exact_packet_count == len(pattern_rows),
        "best_local_clifford_residual_norm": min(
            (row["best_local_clifford_residual_norm"] for row in pattern_rows), default=None
        ),
        "max_best_local_clifford_residual_norm": max(
            (row["best_local_clifford_residual_norm"] for row in pattern_rows), default=None
        ),
        "accepted_occurrence_removal": accepted_occurrence_removal,
        "accepted_proxy_t_reduction": 0,
        "required_occurrence_removals_for_b7_target": REQUIRED_OCCURRENCE_REMOVALS,
        "missing_occurrences_after_gate": missing_occurrences,
        "missing_proxy_t_after_gate": missing_occurrences * PROXY_T_PER_OCCURRENCE,
        "local_clifford_certificate_claimed": False,
        "rewrite_claimed": False,
        "semantic_certificate_claimed": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": None,
    }
    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 local Clifford dressing gate",
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_result": display_path(SOURCE_PACKET_PATH),
        "source_method": packet_payload.get("method"),
        "source_absorption_result": display_path(SOURCE_ABSORPTION_PATH),
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "summary": summary,
        "pattern_local_clifford_results": pattern_rows,
        "claim_boundary": {
            "local_clifford_certificate_claimed": False,
            "rewrite_claimed": False,
            "semantic_certificate_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "A complete finite search over left/right pair-local Clifford dressings "
                "does not find an exact certificate for the three flat-pattern packets."
            ),
            "unsupported_claims": [
                "This does not rule out non-Clifford exact local dressing.",
                "This does not rule out a broader two-qubit rewrite with changed envelope.",
                "This is not a resource saving or B7 ledger improvement.",
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
    claims = payload["claim_boundary"]
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if payload.get("source_method") != "b1_b7_cone01_flat_pattern_kak_packet_v0":
        errors.append("source_method_mismatch")
    if summary.get("source_absorption_method") != "b1_b7_cone01_dressing_absorption_gate_v0":
        errors.append("source_absorption_method_mismatch")
    if summary.get("single_qubit_clifford_count") != 24:
        errors.append("single_qubit_clifford_count_mismatch")
    if summary.get("pair_local_clifford_count") != 576:
        errors.append("pair_local_clifford_count_mismatch")
    if summary.get("left_right_pair_trial_count_per_pattern") != 331776:
        errors.append("left_right_trial_count_mismatch")
    if summary.get("pattern_group_count") != 3:
        errors.append("pattern_group_count_mismatch")
    if summary.get("covered_invariant_flat_occurrence_count") != 11:
        errors.append("covered_occurrence_count_mismatch")
    if summary.get("local_clifford_exact_packet_count") != 0:
        errors.append("local_clifford_exact_packet_count_should_be_zero")
    if summary.get("all_packets_have_local_clifford_dressing") is not False:
        errors.append("all_packets_have_local_clifford_dressing_should_be_false")
    if summary.get("accepted_occurrence_removal") != 0:
        errors.append("accepted_occurrence_removal_must_remain_zero")
    if summary.get("accepted_proxy_t_reduction") != 0:
        errors.append("accepted_proxy_t_reduction_must_remain_zero")
    if summary.get("missing_occurrences_after_gate") != 30:
        errors.append("missing_occurrences_after_gate_mismatch")
    if summary.get("missing_proxy_t_after_gate") != 600:
        errors.append("missing_proxy_t_after_gate_mismatch")
    for row in payload.get("pattern_local_clifford_results", []):
        if row.get("local_clifford_exact_pass_count") != 0:
            errors.append(f"pattern_{row.get('pattern_id')}_local_clifford_should_not_exact_pass")
        if row.get("accepted_occurrence_removal") != 0:
            errors.append(f"pattern_{row.get('pattern_id')}_accepted_removal_nonzero")
    for field in [
        "local_clifford_certificate_claimed",
        "rewrite_claimed",
        "semantic_certificate_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False or claims.get(field) is not False:
            errors.append(f"forbidden_claim_{field}")
    return errors


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone 01 Local Clifford Dressing Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact performs a complete finite search over local Clifford dressings on both sides of each nearest-grid representative. It is a negative certificate route check, not a rewrite or resource-saving claim.",
        "",
        "## Summary",
        "",
        f"- Single-qubit Clifford representatives: `{summary['single_qubit_clifford_count']}`",
        f"- Pair-local Clifford representatives: `{summary['pair_local_clifford_count']}`",
        f"- Left/right pair trials per pattern: `{summary['left_right_pair_trial_count_per_pattern']}`",
        f"- Pattern groups: `{summary['pattern_group_count']}`",
        f"- Covered invariant-flat occurrences: `{summary['covered_invariant_flat_occurrence_count']}`",
        f"- Local Clifford exact packets: `{summary['local_clifford_exact_packet_count']}`",
        f"- Best/max best local-Clifford residual: `{summary['best_local_clifford_residual_norm']}` / `{summary['max_best_local_clifford_residual_norm']}`",
        f"- Accepted occurrence removal: `{summary['accepted_occurrence_removal']}`",
        f"- Missing occurrences after this gate: `{summary['missing_occurrences_after_gate']}`",
        "",
        "## Pattern Results",
        "",
        "| Pattern | Occurrences | Grid | Same-envelope residual | Best Clifford residual | Exact Clifford passes | Best left | Best right |",
        "|---|---:|---|---:|---:|---:|---|---|",
    ]
    for row in payload["pattern_local_clifford_results"]:
        labels = row["best_local_clifford_labels"]
        lines.append(
            "| {pattern_id} | {occurrence_count} | `{grid}` | `{same:.12g}` | `{best:.12g}` | `{exact}` | `{left}` | `{right}` |".format(
                pattern_id=row["pattern_id"],
                occurrence_count=row["occurrence_count"],
                grid=row["nearest_grid_label"],
                same=row["same_envelope_grid_residual_norm"],
                best=row["best_local_clifford_residual_norm"],
                exact=row["local_clifford_exact_pass_count"],
                left=labels["left_pair_label"],
                right=labels["right_pair_label"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- No exact local Clifford dressing was found for the three packets.",
            "- Accepted occurrence removal and accepted proxy-T reduction remain 0.",
            "- This does not rule out non-Clifford exact dressing or a broader two-qubit rewrite.",
            "- No local Clifford certificate, semantic rewrite, resource saving, or B7 ledger improvement is claimed.",
            "",
            f"Validation error count: `{summary['validation_error_count']}`",
            "",
        ]
    )
    write_text(path, "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=JSON_OUT)
    parser.add_argument("--markdown-output", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.json_output, payload, pretty=args.pretty)
    write_markdown(payload, args.markdown_output)
    print(json.dumps(payload["summary"], indent=2 if args.pretty else None, sort_keys=True))
    return 0 if not payload["validation_errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
