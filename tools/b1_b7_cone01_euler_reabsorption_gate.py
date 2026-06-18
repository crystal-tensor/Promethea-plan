#!/usr/bin/env python3
"""Restricted Euler-reabsorption gate for the B1/B7 gcm_h6 cone_01 target.

T-B1-004c showed that deleting cone_01's arbitrary RY, or replacing it with a
Z phase, cannot clear the local exact gate.  This tool tests a slightly broader
same-envelope hypothesis: lock that arbitrary RY to an exact/Clifford-like RY
angle while allowing neighboring target-qubit RZ phases in the same two-CNOT
window to reabsorb the difference.

This still does not produce a resource-saving rewrite: even if a window passed,
the optimized neighboring RZ phases would need their own exactness/resource
accounting and replayable certificates before B7 could count anything.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from b1_b7_cone01_phase_removal_gate import (
    EXACT_TOLERANCE,
    angle_from_params,
    phase_align,
    residual_vector,
    target_rows,
    unitary_for_ops,
)


METHOD = "b1_b7_cone01_euler_reabsorption_gate_v0"
STATUS = "cone01_euler_reabsorption_restricted_negative_gate"
MODEL_STATUS = "same_envelope_euler_reabsorption_search_not_semantic_certificate"
VERSION = "0.1"
EXACT_RY_ANGLES = {
    "0": 0.0,
    "pi/4": math.pi / 4.0,
    "-pi/4": -math.pi / 4.0,
    "pi/2": math.pi / 2.0,
    "-pi/2": -math.pi / 2.0,
    "3*pi/4": 3.0 * math.pi / 4.0,
    "-3*pi/4": -3.0 * math.pi / 4.0,
    "pi": math.pi,
    "-pi": -math.pi,
}


def write_json(path: Path, payload: dict, pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def editable_rz_ops(window: list[dict], target_qubit: int, ry_op_index: int) -> list[int]:
    indices = []
    for idx, op in enumerate(window):
        if op["op_index"] == ry_op_index:
            continue
        if op["gate"] == "rz" and op["qubits"] == [target_qubit]:
            indices.append(idx)
    return indices


def candidate_window(window: list[dict], row: dict, fixed_ry_angle: float, rz_values: np.ndarray) -> list[dict]:
    output = []
    rz_indices = editable_rz_ops(window, row["qubit"], row["op_index"])
    rz_cursor = 0
    for idx, op in enumerate(window):
        clone = dict(op)
        if op["op_index"] == row["op_index"]:
            clone["gate"] = "ry"
            clone["params"] = f"{fixed_ry_angle:.17g}"
            clone["text"] = f"ry({fixed_ry_angle:.17g}) q[{row['qubit']}];"
        elif idx in rz_indices:
            angle = float(rz_values[rz_cursor])
            rz_cursor += 1
            clone["gate"] = "rz"
            clone["params"] = f"{angle:.17g}"
            clone["text"] = f"rz({angle:.17g}) q[{row['qubit']}];"
        output.append(clone)
    return output


def seed_points(window: list[dict], row: dict, seed_count: int) -> list[np.ndarray]:
    rz_indices = editable_rz_ops(window, row["qubit"], row["op_index"])
    base = np.array([angle_from_params(window[idx]["params"]) for idx in rz_indices], dtype=float)
    if base.size == 0:
        return [base]
    points = [base, np.zeros_like(base)]
    rng = np.random.default_rng(1004 + row["line_number"])
    for scale in [0.05, 0.25, 1.0, math.pi]:
        points.append(base + rng.normal(0.0, scale, size=base.shape))
        points.append(rng.uniform(-math.pi, math.pi, size=base.shape))
    while len(points) < seed_count:
        points.append(rng.uniform(-2.0 * math.pi, 2.0 * math.pi, size=base.shape))
    return points[:seed_count]


def optimize_fixed_ry(window: list[dict], row: dict, local_qubits: list[int], target: np.ndarray, label: str, angle: float, seed_count: int) -> dict:
    rz_indices = editable_rz_ops(window, row["qubit"], row["op_index"])

    def objective(values: np.ndarray) -> np.ndarray:
        candidate = unitary_for_ops(candidate_window(window, row, angle, values), local_qubits)
        return residual_vector(candidate, target)

    best = None
    for seed in seed_points(window, row, seed_count):
        result = least_squares(
            objective,
            seed,
            method="trf",
            ftol=1e-13,
            xtol=1e-13,
            gtol=1e-13,
            max_nfev=4000,
        )
        residual = float(np.linalg.norm(result.fun))
        if best is None or residual < best["residual_norm"]:
            candidate = unitary_for_ops(candidate_window(window, row, angle, result.x), local_qubits)
            best = {
                "fixed_ry_label": label,
                "fixed_ry_angle": angle,
                "optimized_rz_values": [float(value) for value in result.x],
                "optimized_rz_parameter_count": len(rz_indices),
                "residual_norm": residual,
                "max_abs_entry_error": float(np.max(np.abs(phase_align(candidate, target) - target))),
                "optimizer_success": bool(result.success),
                "optimizer_nfev": int(result.nfev),
                "passes_exact_gate": residual <= EXACT_TOLERANCE,
            }
    assert best is not None
    return best


def analyze_window(ops: list[dict], row: dict, seed_count: int) -> dict:
    local_qubits = [row["previous_cx_partner"], row["qubit"]]
    window = ops[row["previous_cx_index"] : row["next_cx_index"] + 1]
    target = unitary_for_ops(window, local_qubits)
    attempts = [
        optimize_fixed_ry(window, row, local_qubits, target, label, angle, seed_count)
        for label, angle in EXACT_RY_ANGLES.items()
    ]
    best = min(attempts, key=lambda item: item["residual_norm"])
    return {
        "line_number": row["line_number"],
        "op_index": row["op_index"],
        "qubit": row["qubit"],
        "partner": row["previous_cx_partner"],
        "original_ry_params": row["params"],
        "previous_cx_line": row["previous_cx_line"],
        "next_cx_line": row["next_cx_line"],
        "window_operation_count": len(window),
        "editable_rz_parameter_count": len(editable_rz_ops(window, row["qubit"], row["op_index"])),
        "window_text": [op["text"] for op in window],
        "best_fixed_ry_label": best["fixed_ry_label"],
        "best_fixed_ry_angle": best["fixed_ry_angle"],
        "best_residual_norm": best["residual_norm"],
        "best_max_abs_entry_error": best["max_abs_entry_error"],
        "best_optimized_rz_values": best["optimized_rz_values"],
        "best_optimizer_success": best["optimizer_success"],
        "best_optimizer_nfev": best["optimizer_nfev"],
        "passes_exact_gate": best["passes_exact_gate"],
        "attempts": attempts,
    }


def build_payload(args: argparse.Namespace) -> dict:
    ops, rows = target_rows(args)
    analyses = [analyze_window(ops, row, args.seed_count) for row in rows]
    best_rows = sorted(analyses, key=lambda item: item["best_residual_norm"])
    editable_counts = [row["editable_rz_parameter_count"] for row in analyses]
    summary = {
        "target_cone_id": args.cone_id,
        "candidate_window_count": len(analyses),
        "required_exact_windows_for_b7_target": args.required_windows,
        "exact_ry_candidate_angle_count": len(EXACT_RY_ANGLES),
        "optimizer_seed_count": args.seed_count,
        "fixed_ry_with_rz_reabsorption_exact_pass_count": sum(1 for row in analyses if row["passes_exact_gate"]),
        "best_residual_norm": best_rows[0]["best_residual_norm"] if analyses else None,
        "median_residual_norm": float(np.median([row["best_residual_norm"] for row in analyses])) if analyses else None,
        "editable_rz_parameter_count_min": min(editable_counts) if editable_counts else None,
        "editable_rz_parameter_count_max": max(editable_counts) if editable_counts else None,
        "exact_tolerance": EXACT_TOLERANCE,
        "restricted_gate_clears_b7_target": False,
        "rewrite_claimed": False,
        "resource_saving_claimed": False,
        "semantic_certificate_claimed": False,
        "obstruction_theorem_claimed": False,
    }
    summary["restricted_gate_clears_b7_target"] = (
        summary["fixed_ry_with_rz_reabsorption_exact_pass_count"] >= args.required_windows
    )
    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 restricted Euler reabsorption gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_qasm": str(args.qasm),
        "source_selector": str(args.selector),
        "source_feasibility_gate": str(args.feasibility),
        "source_phase_removal_gate": str(args.phase_removal),
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "summary": summary,
        "top_windows_by_residual": best_rows[: args.report_limit],
        "claim_boundary": {
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "semantic_certificate_claimed": False,
            "obstruction_theorem_claimed": False,
            "physical_layout_claimed": False,
            "supported_claim": (
                "The restricted same-envelope Euler reabsorption route does not clear "
                "the cone_01 target under the exact numerical tolerance."
            ),
            "unsupported_claims": [
                "No local rewrite certificate is produced.",
                "No global obstruction theorem is proved.",
                "No B7 FT ledger improvement is counted.",
                "Optimized neighboring RZ phases are not charged as resource savings.",
            ],
            "next_gate": (
                "Move beyond same-envelope Euler reabsorption to a broader two-qubit synthesis "
                "or KAK/Clifford scaffold that can emit replayable certificates."
            ),
        },
    }
    errors = validate(payload)
    payload["summary"]["validation_error_count"] = len(errors)
    payload["validation_errors"] = errors
    return payload


def validate(payload: dict) -> list[str]:
    errors = []
    summary = payload["summary"]
    if payload.get("method") != METHOD:
        errors.append("method mismatch")
    if payload.get("status") != STATUS:
        errors.append("status mismatch")
    if summary["candidate_window_count"] < summary["required_exact_windows_for_b7_target"]:
        errors.append("candidate windows should cover the B7 occurrence target")
    if summary["restricted_gate_clears_b7_target"]:
        errors.append("restricted Euler reabsorption unexpectedly clears B7 target; review claim boundary")
    if summary["fixed_ry_with_rz_reabsorption_exact_pass_count"] != 0:
        errors.append("fixed-RY plus RZ reabsorption should not pass exact gate for current cone_01 windows")
    for field in [
        "rewrite_claimed",
        "resource_saving_claimed",
        "semantic_certificate_claimed",
        "obstruction_theorem_claimed",
    ]:
        if summary.get(field) is not False:
            errors.append(f"{field} must be false")
    return errors


def markdown_report(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 Restricted Euler Reabsorption Gate",
        "",
        f"- Status: `{payload['status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- Target cone: `{summary['target_cone_id']}`",
        f"- Candidate windows: {summary['candidate_window_count']}",
        f"- Required exact windows for B7 one-sided target: {summary['required_exact_windows_for_b7_target']}",
        f"- Exact RY candidate angle count: {summary['exact_ry_candidate_angle_count']}",
        f"- Optimizer seed count per angle: {summary['optimizer_seed_count']}",
        f"- Fixed RY + RZ reabsorption exact pass count: {summary['fixed_ry_with_rz_reabsorption_exact_pass_count']}",
        f"- Best residual: {summary['best_residual_norm']}",
        f"- Median residual: {summary['median_residual_norm']}",
        f"- Editable RZ parameter count range: {summary['editable_rz_parameter_count_min']} - {summary['editable_rz_parameter_count_max']}",
        f"- Restricted gate clears B7 target: {summary['restricted_gate_clears_b7_target']}",
        f"- Validation errors: {summary['validation_error_count']}",
        "",
        "## Interpretation",
        "",
        "This closes another narrow route.  Even when the arbitrary RY is locked to",
        "an exact candidate angle and neighboring target-qubit RZ phases are allowed",
        "to reoptimize inside the same two-CNOT envelope, no cone_01 window passes",
        "the exact gate.  This is not a global obstruction theorem; it is a",
        "restricted numerical gate that points T-B1-004 toward broader two-qubit",
        "synthesis or KAK/Clifford scaffolding.",
        "",
        "## Claim Boundary",
        "",
        f"- Rewrite claimed: {payload['claim_boundary']['rewrite_claimed']}",
        f"- Resource saving claimed: {payload['claim_boundary']['resource_saving_claimed']}",
        f"- Semantic certificate claimed: {payload['claim_boundary']['semantic_certificate_claimed']}",
        f"- Obstruction theorem claimed: {payload['claim_boundary']['obstruction_theorem_claimed']}",
        "",
        "## Best Attempts",
        "",
        "| line | qubit | partner | original theta | best fixed RY | residual | editable RZs |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["top_windows_by_residual"]:
        lines.append(
            f"| {row['line_number']} | {row['qubit']} | {row['partner']} | "
            f"{row['original_ry_params']} | {row['best_fixed_ry_label']} | "
            f"{row['best_residual_norm']} | {row['editable_rz_parameter_count']} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qasm", type=Path, default=Path("results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm"))
    parser.add_argument("--selector", type=Path, default=Path("results/B1_B7_gcm_h6_target_selector_v0.json"))
    parser.add_argument("--feasibility", type=Path, default=Path("results/B1_B7_gcm_h6_cone_feasibility_gate_v0.json"))
    parser.add_argument("--phase-removal", type=Path, default=Path("results/B1_B7_cone01_phase_removal_gate_v0.json"))
    parser.add_argument("--result", type=Path, default=Path("results/B1_B7_cone01_euler_reabsorption_gate_v0.json"))
    parser.add_argument("--markdown", type=Path, default=Path("research/B1_B7_cone01_euler_reabsorption_gate.md"))
    parser.add_argument("--cone-id", default="cone_01")
    parser.add_argument("--required-windows", type=int, default=30)
    parser.add_argument("--seed-count", type=int, default=8)
    parser.add_argument("--report-limit", type=int, default=12)
    parser.add_argument("--last-updated", default="2026-06-18")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = build_payload(args)
    write_json(args.result, payload, args.pretty)
    write_text(args.markdown, markdown_report(payload))
    print(f"wrote {args.result}")
    print(f"wrote {args.markdown}")
    if payload["validation_errors"]:
        print(json.dumps(payload["validation_errors"], indent=2), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
