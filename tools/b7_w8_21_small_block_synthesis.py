#!/usr/bin/env python3
"""Exact small-block synthesis probe for B7 template w8_21.

T-B7-008 focuses on the best repeated block from the nonlocal template scan.
The gate family is intentionally narrow and auditable: keep the same two-CNOT
role skeleton and test whether any one of the five arbitrary rotations can be
made exact/Clifford while re-optimizing the remaining four arbitrary angles.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares


ARBITRARY_T_COST = 20
EXACT_T_COSTS = {
    "0": 0,
    "pi": 0,
    "-pi": 0,
    "pi/2": 0,
    "-pi/2": 0,
    "pi/4": 1,
    "-pi/4": 1,
    "3*pi/4": 1,
    "-3*pi/4": 1,
    "pi/8": 4,
    "-pi/8": 4,
}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def phase_align(candidate: np.ndarray, target: np.ndarray) -> np.ndarray:
    overlap = np.trace(np.conjugate(target.T) @ candidate)
    if abs(overlap) <= 1e-15:
        return candidate
    return candidate * np.exp(-1j * np.angle(overlap))


def residual_vector(candidate: np.ndarray, target: np.ndarray) -> np.ndarray:
    diff = phase_align(candidate, target) - target
    return np.concatenate([diff.real.ravel(), diff.imag.ravel()])


def frobenius_residual(candidate: np.ndarray, target: np.ndarray) -> float:
    return float(np.linalg.norm(residual_vector(candidate, target)))


def rz(theta: float) -> np.ndarray:
    return np.array(
        [[np.exp(-0.5j * theta), 0.0], [0.0, np.exp(0.5j * theta)]],
        dtype=complex,
    )


def ry(theta: float) -> np.ndarray:
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)
    return np.array([[c, -s], [s, c]], dtype=complex)


def kron(control_op: np.ndarray, target_op: np.ndarray) -> np.ndarray:
    return np.kron(control_op, target_op)


I2 = np.eye(2, dtype=complex)
P0 = np.array([[1, 0], [0, 0]], dtype=complex)
P1 = np.array([[0, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
CX_CONTROL_TARGET = kron(P0, I2) + kron(P1, X)


def role_block_unitary(params: dict[str, float]) -> np.ndarray:
    # Qubit order in the matrix is |control, target>.  The original template
    # uses q[14] as control and q[13] as target.
    ops = [
        kron(I2, rz(params["a"])),
        CX_CONTROL_TARGET,
        kron(I2, rz(params["b"])),
        kron(I2, ry(params["c"])),
        kron(I2, rz(math.pi)),
        CX_CONTROL_TARGET,
        kron(I2, rz(params["d"])),
        kron(I2, ry(params["e"])),
    ]
    total = np.eye(4, dtype=complex)
    for op in ops:
        total = op @ total
    return total


def vectorize_family(params: dict[str, float], target: np.ndarray) -> np.ndarray:
    return residual_vector(role_block_unitary(params), target)


def finite_difference_rank(base_params: dict[str, float], target: np.ndarray, step: float) -> dict:
    names = ["a", "b", "c", "d", "e"]
    columns = []
    base = vectorize_family(base_params, target)
    for name in names:
        plus = dict(base_params)
        minus = dict(base_params)
        plus[name] += step
        minus[name] -= step
        columns.append((vectorize_family(plus, target) - vectorize_family(minus, target)) / (2.0 * step))
    jac = np.stack(columns, axis=1)
    singular_values = np.linalg.svd(jac, compute_uv=False)
    rank = int(np.sum(singular_values > 1e-7))
    return {
        "parameter_names": names,
        "finite_difference_step": step,
        "singular_values": [float(value) for value in singular_values],
        "numerical_rank_threshold": 1e-7,
        "numerical_rank": rank,
        "base_residual_norm": float(np.linalg.norm(base)),
    }


def exact_angle_table() -> dict[str, float]:
    return {
        "0": 0.0,
        "pi": math.pi,
        "-pi": -math.pi,
        "pi/2": math.pi / 2.0,
        "-pi/2": -math.pi / 2.0,
        "pi/4": math.pi / 4.0,
        "-pi/4": -math.pi / 4.0,
        "3*pi/4": 3.0 * math.pi / 4.0,
        "-3*pi/4": -3.0 * math.pi / 4.0,
        "pi/8": math.pi / 8.0,
        "-pi/8": -math.pi / 8.0,
    }


def candidate_params(base_params: dict[str, float], fixed_name: str, fixed_value: float, free_values: np.ndarray) -> dict:
    params = {}
    cursor = 0
    for name in ["a", "b", "c", "d", "e"]:
        if name == fixed_name:
            params[name] = fixed_value
        else:
            params[name] = float(free_values[cursor])
            cursor += 1
    return params


def initial_points(base_params: dict[str, float], fixed_name: str, seed_count: int) -> list[np.ndarray]:
    names = [name for name in ["a", "b", "c", "d", "e"] if name != fixed_name]
    base = np.array([base_params[name] for name in names], dtype=float)
    points = [base, np.zeros_like(base)]
    rng = np.random.default_rng(8721)
    for scale in [0.1, 0.5, 1.0, math.pi]:
        points.append(base + rng.normal(0.0, scale, size=base.shape))
        points.append(rng.uniform(-math.pi, math.pi, size=base.shape))
    while len(points) < seed_count:
        points.append(rng.uniform(-2 * math.pi, 2 * math.pi, size=base.shape))
    return points[:seed_count]


def optimize_fixed_candidate(
    target: np.ndarray,
    base_params: dict[str, float],
    fixed_name: str,
    fixed_label: str,
    fixed_value: float,
    seed_count: int,
) -> dict:
    def objective(values: np.ndarray) -> np.ndarray:
        params = candidate_params(base_params, fixed_name, fixed_value, values)
        return residual_vector(role_block_unitary(params), target)

    best = None
    for seed in initial_points(base_params, fixed_name, seed_count):
        result = least_squares(
            objective,
            seed,
            method="trf",
            ftol=1e-12,
            xtol=1e-12,
            gtol=1e-12,
            max_nfev=4000,
        )
        residual = float(np.linalg.norm(result.fun))
        if best is None or residual < best["residual_norm"]:
            best = {
                "fixed_parameter": fixed_name,
                "fixed_label": fixed_label,
                "fixed_value": fixed_value,
                "fixed_t_cost": EXACT_T_COSTS[fixed_label],
                "free_parameter_count": 4,
                "arbitrary_rotation_count": 4,
                "candidate_t_cost": (4 * ARBITRARY_T_COST) + EXACT_T_COSTS[fixed_label],
                "baseline_t_cost": 5 * ARBITRARY_T_COST,
                "t_saving_if_exact": (5 * ARBITRARY_T_COST) - ((4 * ARBITRARY_T_COST) + EXACT_T_COSTS[fixed_label]),
                "residual_norm": residual,
                "max_abs_entry_error": float(
                    np.max(np.abs(phase_align(role_block_unitary(candidate_params(base_params, fixed_name, fixed_value, result.x)), target) - target))
                ),
                "optimized_free_values": [float(value) for value in result.x],
                "optimizer_success": bool(result.success),
                "optimizer_cost": float(result.cost),
                "optimizer_nfev": int(result.nfev),
            }
    assert best is not None
    return best


def run(args: argparse.Namespace) -> dict:
    base_params = {
        "a": 1.4922506383856682,
        "b": 2.1870074319274799,
        "c": 0.52538524712872736,
        "d": 2.538142068316358,
        "e": 1.1254377896453873,
    }
    target = role_block_unitary(base_params)
    baseline_residual = frobenius_residual(role_block_unitary(base_params), target)
    rank = finite_difference_rank(base_params, target, args.finite_difference_step)

    exact_angles = exact_angle_table()
    attempts = []
    for fixed_name in ["a", "b", "c", "d", "e"]:
        for fixed_label, fixed_value in exact_angles.items():
            attempts.append(
                optimize_fixed_candidate(
                    target,
                    base_params,
                    fixed_name,
                    fixed_label,
                    fixed_value,
                    args.seed_count,
                )
            )
    attempts.sort(key=lambda row: row["residual_norm"])
    passing = [row for row in attempts if row["residual_norm"] <= args.exact_tolerance]
    best = attempts[0]
    status = (
        "w8_21_small_block_synthesis_positive_proxy_not_physical_layout"
        if passing
        else "w8_21_small_block_synthesis_negative_boundary_not_physical_layout"
    )
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 w8_21 exact small-block synthesis probe",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": status,
        "method": "b7_w8_21_small_block_synthesis_v0",
        "source_template_report": str(args.source_template_report),
        "template_id": "w8_21",
        "template_width": 8,
        "template_nonoverlap_occurrences": 20,
        "template_unique_binding_count": 14,
        "baseline_arbitrary_rotations_per_occurrence": 5,
        "baseline_t_cost_per_occurrence": 100,
        "template_physical_arbitrary_occurrences_covered": 100,
        "template_baseline_t_cost_covered": 2000,
        "target_parameters": base_params,
        "target_operations": [
            "rz(a) target",
            "cx control,target",
            "rz(b) target",
            "ry(c) target",
            "rz(pi) target",
            "cx control,target",
            "rz(d) target",
            "ry(e) target",
        ],
        "baseline_exact_residual_norm": baseline_residual,
        "exact_tolerance": args.exact_tolerance,
        "finite_difference_rank": rank,
        "candidate_family": {
            "description": "same two-CNOT w8_21 skeleton with one arbitrary rotation fixed to an exact/Clifford angle and the other four angles re-optimized",
            "fixed_parameter_count_per_attempt": 1,
            "free_parameter_count_per_attempt": 4,
            "fixed_angle_labels": list(exact_angles),
            "attempt_count": len(attempts),
            "seed_count_per_attempt": args.seed_count,
        },
        "passing_candidate_count": len(passing),
        "best_candidate": best,
        "top_candidates": attempts[:16],
        "claim_boundary": {
            "same_skeleton_one_rotation_exact_replacement_found": bool(passing),
            "same_skeleton_best_residual_below_tolerance": best["residual_norm"] <= args.exact_tolerance,
            "five_parameter_family_local_rank": rank["numerical_rank"],
            "rank_supports_five_independent_continuous_degrees": rank["numerical_rank"] == 5,
            "would_reduce_arbitrary_occurrences_if_passing": 20 if passing else 0,
            "would_reduce_t_ledger_if_passing_best": 20 * int(best["t_saving_if_exact"]) if passing else 0,
        },
        "interpretation": (
            "No same-skeleton replacement was found that fixes one of the five arbitrary angles to an exact/Clifford value "
            "while preserving the 2-qubit unitary within tolerance.  The finite-difference Jacobian has rank 5 at w8_21, "
            "supporting that this template carries five independent continuous degrees inside this skeleton.  This is not a "
            "global lower bound over all possible two-qubit circuits, but it closes the most direct T-B7-008 compression path."
            if not passing
            else "A same-skeleton exact-angle replacement was found; this must be lifted into the full gcm_h6 QASM and retested."
        ),
        "next_actions": [
            "If negative, broaden synthesis beyond the same two-CNOT skeleton: KAK/COSINE-style two-qubit synthesis or numerical search over different CNOT placements.",
            "If a broader candidate beats 5 arbitrary rotations, emit a QASM rewrite for all 20 w8_21 occurrences and run Aer/proof checks.",
            "If broader synthesis also fails, write a template-family minimality note as a B7 negative-result lemma.",
        ],
        "limits": [
            "This is a scoped same-skeleton numerical synthesis probe, not a proof over all two-qubit circuits.",
            "Exact/Clifford fixed-angle replacements are tested numerically with global phase alignment.",
            "No full gcm_h6 QASM rewrite is emitted unless a candidate passes the exact tolerance.",
            "The FT ledger remains a proxy until physical layout and synthesis assumptions are made explicit.",
        ],
    }


def certificates_jsonl(path: Path, report: dict) -> None:
    rows = []
    for row in report["top_candidates"]:
        rows.append(
            {
                "rule": "same_skeleton_one_arbitrary_to_exact_probe",
                "certificate_type": "small_block_synthesis_attempt",
                **row,
                "passes_exact_tolerance": row["residual_norm"] <= report["exact_tolerance"],
            }
        )
    rows.append(
        {
            "rule": "finite_difference_family_rank",
            "certificate_type": "local_dimension_check",
            **report["finite_difference_rank"],
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def markdown(report: dict) -> str:
    best = report["best_candidate"]
    rank = report["finite_difference_rank"]
    lines = [
        "# B7 w8_21 Exact Small-Block Synthesis v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source template report: `{report['source_template_report']}`",
        f"- Template: `{report['template_id']}` / width {report['template_width']}",
        f"- Non-overlap occurrences in gcm_h6: {report['template_nonoverlap_occurrences']}",
        f"- Baseline arbitrary rotations per occurrence: {report['baseline_arbitrary_rotations_per_occurrence']}",
        f"- Candidate family: {report['candidate_family']['description']}",
        f"- Candidate attempts: {report['candidate_family']['attempt_count']} with {report['candidate_family']['seed_count_per_attempt']} seeds each",
        f"- Passing candidates at tolerance {report['exact_tolerance']}: {report['passing_candidate_count']}",
        f"- Best residual norm: {best['residual_norm']:.6e}",
        f"- Best max entry error: {best['max_abs_entry_error']:.6e}",
        f"- Best fixed parameter/angle: `{best['fixed_parameter']}` = `{best['fixed_label']}`",
        f"- Local finite-difference rank: {rank['numerical_rank']} over {rank['parameter_names']}",
        f"- Interpretation: {report['interpretation']}",
        "",
        "## Target Operations",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report["target_operations"])
    lines.extend(
        [
            "",
            "## Local Rank Check",
            "",
            f"- Singular values: `{rank['singular_values']}`",
            f"- Rank threshold: {rank['numerical_rank_threshold']}",
            f"- Rank supports five independent continuous degrees: {report['claim_boundary']['rank_supports_five_independent_continuous_degrees']}",
            "",
            "## Top Candidate Attempts",
            "",
            "| fixed parameter | exact value | residual | max entry error | candidate T cost | T saving if exact |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["top_candidates"]:
        lines.append(
            f"| `{row['fixed_parameter']}` | `{row['fixed_label']}` | {row['residual_norm']:.6e} | "
            f"{row['max_abs_entry_error']:.6e} | {row['candidate_t_cost']} | {row['t_saving_if_exact']} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-template-report",
        type=Path,
        default=Path("results/B7_nonlocal_template_block_scan_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B7_w8_21_small_block_synthesis_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B7_w8_21_small_block_synthesis.md"),
    )
    parser.add_argument(
        "--proof-log",
        type=Path,
        default=Path("results/b7_w8_21_small_block_synthesis/proofs.jsonl"),
    )
    parser.add_argument("--seed-count", type=int, default=16)
    parser.add_argument("--exact-tolerance", type=float, default=1e-8)
    parser.add_argument("--finite-difference-step", type=float, default=1e-6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run(args)
    write_json(args.json_output, report)
    certificates_jsonl(args.proof_log, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    print(f"wrote {args.proof_log}")
    print(
        f"status={report['status']} passing={report['passing_candidate_count']} "
        f"best_residual={report['best_candidate']['residual_norm']:.6e} rank={report['finite_difference_rank']['numerical_rank']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
