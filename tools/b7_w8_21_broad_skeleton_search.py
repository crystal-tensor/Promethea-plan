#!/usr/bin/env python3
"""Bounded broad-skeleton synthesis search for B7 template w8_21.

T-B7-009 moves beyond the exact same two-CNOT skeleton tested in T-B7-008.
This first pass asks a deliberately bounded question: can the w8_21 2-qubit
unitary be represented by any circuit with two CNOTs and only four arbitrary
Rz/Ry rotations, allowing the CNOT directions and operation positions to vary?

The result is a search certificate, not a global lower bound.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares


ARBITRARY_T_COST = 20
PARAMETER_NAMES = ["a", "b", "c", "d", "e"]
TARGET_PARAMS = {
    "a": 1.4922506383856682,
    "b": 2.1870074319274799,
    "c": 0.52538524712872736,
    "d": 2.538142068316358,
    "e": 1.1254377896453873,
}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rz(theta: float) -> np.ndarray:
    return np.array([[np.exp(-0.5j * theta), 0.0], [0.0, np.exp(0.5j * theta)]], dtype=complex)


def ry(theta: float) -> np.ndarray:
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)
    return np.array([[c, -s], [s, c]], dtype=complex)


def kron(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.kron(left, right)


I2 = np.eye(2, dtype=complex)
P0 = np.array([[1, 0], [0, 0]], dtype=complex)
P1 = np.array([[0, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
CX_01 = kron(P0, I2) + kron(P1, X)
CX_10 = kron(I2, P0) + kron(X, P1)


def one_qubit_rotation(qubit: int, axis: str, theta: float) -> np.ndarray:
    single = rz(theta) if axis == "rz" else ry(theta)
    return kron(single, I2) if qubit == 0 else kron(I2, single)


def phase_align(candidate: np.ndarray, target: np.ndarray) -> np.ndarray:
    overlap = np.trace(np.conjugate(target.T) @ candidate)
    if abs(overlap) <= 1e-15:
        return candidate
    return candidate * np.exp(-1j * np.angle(overlap))


def residual_vector(candidate: np.ndarray, target: np.ndarray) -> np.ndarray:
    diff = phase_align(candidate, target) - target
    return np.concatenate([diff.real.ravel(), diff.imag.ravel()])


def target_unitary(params: dict[str, float] = TARGET_PARAMS) -> np.ndarray:
    ops = [
        one_qubit_rotation(1, "rz", params["a"]),
        CX_01,
        one_qubit_rotation(1, "rz", params["b"]),
        one_qubit_rotation(1, "ry", params["c"]),
        one_qubit_rotation(1, "rz", math.pi),
        CX_01,
        one_qubit_rotation(1, "rz", params["d"]),
        one_qubit_rotation(1, "ry", params["e"]),
    ]
    total = np.eye(4, dtype=complex)
    for op in ops:
        total = op @ total
    return total


def candidate_unitary(cnot_positions: tuple[int, int], cnot_dirs: tuple[str, str], rotations: tuple[tuple[int, str], ...], values: np.ndarray) -> np.ndarray:
    total = np.eye(4, dtype=complex)
    rotation_cursor = 0
    cnot_cursor = 0
    cnot_by_position = dict(zip(cnot_positions, cnot_dirs))
    for position in range(6):
        cnot_dir = cnot_by_position.get(position)
        if cnot_dir:
            op = CX_01 if cnot_dir == "01" else CX_10
            cnot_cursor += 1
        else:
            qubit, axis = rotations[rotation_cursor]
            op = one_qubit_rotation(qubit, axis, float(values[rotation_cursor]))
            rotation_cursor += 1
        total = op @ total
    assert cnot_cursor == 2
    assert rotation_cursor == 4
    return total


def family_label(cnot_positions: tuple[int, int], cnot_dirs: tuple[str, str], rotations: tuple[tuple[int, str], ...]) -> str:
    parts = []
    rotation_cursor = 0
    cnot_by_position = dict(zip(cnot_positions, cnot_dirs))
    for position in range(6):
        cnot_dir = cnot_by_position.get(position)
        if cnot_dir:
            parts.append(f"cx{cnot_dir}")
        else:
            qubit, axis = rotations[rotation_cursor]
            parts.append(f"{axis}_q{qubit}")
            rotation_cursor += 1
    return "-".join(parts)


def initial_points(seed_count: int, rng: np.random.Generator) -> list[np.ndarray]:
    points = [
        np.zeros(4, dtype=float),
        np.array([TARGET_PARAMS[name] for name in PARAMETER_NAMES[:4]], dtype=float),
        np.array([TARGET_PARAMS[name] for name in PARAMETER_NAMES[1:]], dtype=float),
    ]
    while len(points) < seed_count:
        points.append(rng.uniform(-math.pi, math.pi, size=4))
    return points[:seed_count]


def optimize_family(
    target: np.ndarray,
    cnot_positions: tuple[int, int],
    cnot_dirs: tuple[str, str],
    rotations: tuple[tuple[int, str], ...],
    seeds: list[np.ndarray],
    max_nfev: int,
) -> dict:
    def objective(values: np.ndarray) -> np.ndarray:
        return residual_vector(candidate_unitary(cnot_positions, cnot_dirs, rotations, values), target)

    best = None
    for seed_index, seed in enumerate(seeds):
        result = least_squares(
            objective,
            seed,
            method="trf",
            ftol=1e-11,
            xtol=1e-11,
            gtol=1e-11,
            max_nfev=max_nfev,
        )
        residual = float(np.linalg.norm(result.fun))
        if best is None or residual < best["residual_norm"]:
            matrix = candidate_unitary(cnot_positions, cnot_dirs, rotations, result.x)
            best = {
                "family_label": family_label(cnot_positions, cnot_dirs, rotations),
                "cnot_positions": list(cnot_positions),
                "cnot_directions": list(cnot_dirs),
                "rotation_slots": [{"qubit": qubit, "axis": axis} for qubit, axis in rotations],
                "seed_index": seed_index,
                "parameter_values": [float(value) for value in result.x],
                "residual_norm": residual,
                "max_abs_entry_error": float(np.max(np.abs(phase_align(matrix, target) - target))),
                "optimizer_success": bool(result.success),
                "optimizer_cost": float(result.cost),
                "optimizer_nfev": int(result.nfev),
                "arbitrary_rotation_count": 4,
                "candidate_t_cost": 4 * ARBITRARY_T_COST,
                "baseline_t_cost": 5 * ARBITRARY_T_COST,
                "t_saving_if_exact": ARBITRARY_T_COST,
            }
    assert best is not None
    return best


def iter_families() -> list[tuple[tuple[int, int], tuple[str, str], tuple[tuple[int, str], ...]]]:
    cnot_position_sets = list(itertools.combinations(range(6), 2))
    cnot_direction_sets = list(itertools.product(["01", "10"], repeat=2))
    rotation_choices = list(itertools.product([(0, "rz"), (0, "ry"), (1, "rz"), (1, "ry")], repeat=4))
    families = []
    for cnot_positions in cnot_position_sets:
        for cnot_dirs in cnot_direction_sets:
            for rotations in rotation_choices:
                families.append((cnot_positions, cnot_dirs, rotations))
    return families


def run(args: argparse.Namespace) -> dict:
    rng = np.random.default_rng(args.random_seed)
    target = target_unitary()
    seeds = initial_points(args.seed_count, rng)
    all_families = iter_families()
    families = all_families
    family_selection = "exhaustive"
    if args.family_limit:
        limit = min(args.family_limit, len(all_families))
        selected_indices = np.linspace(0, len(all_families) - 1, num=limit, dtype=int)
        families = [all_families[int(index)] for index in selected_indices]
        family_selection = "evenly_spaced_subset"

    top_candidates: list[dict] = []
    passing = []
    for index, (cnot_positions, cnot_dirs, rotations) in enumerate(families, start=1):
        result = optimize_family(target, cnot_positions, cnot_dirs, rotations, seeds, args.max_nfev)
        result["family_index"] = index
        top_candidates.append(result)
        top_candidates.sort(key=lambda item: item["residual_norm"])
        top_candidates = top_candidates[: args.keep_top]
        if result["residual_norm"] <= args.exact_tolerance:
            passing.append(result)

    best = top_candidates[0]
    status = (
        "w8_21_broad_skeleton_search_positive_proxy_not_physical_layout"
        if passing
        else "w8_21_broad_skeleton_search_negative_boundary_not_global_lower_bound"
    )
    payload = {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 w8_21 bounded broad-skeleton synthesis search",
        "status": status,
        "method": "b7_w8_21_broad_skeleton_search_v0",
        "last_updated": args.last_updated,
        "source_template_report": str(args.source_template_report),
        "source_small_block_report": str(args.source_small_block_report),
        "template_id": "w8_21",
        "question": "Can a bounded search over two-CNOT circuits with four arbitrary Rz/Ry rotations represent w8_21 exactly?",
        "candidate_family": {
            "description": "all length-6 circuits with two CNOTs placed anywhere, either CNOT direction, and four arbitrary Rz/Ry rotations on either qubit",
            "basis": "Rz/Ry arbitrary rotations plus CNOT",
            "cnot_position_pattern_count": len(list(itertools.combinations(range(6), 2))),
            "cnot_direction_pattern_count": 4,
            "rotation_slot_choice_count": 4**4,
            "total_family_count": len(all_families),
            "family_count": len(families),
            "family_selection": family_selection,
            "seed_count_per_family": args.seed_count,
            "max_nfev_per_seed": args.max_nfev,
        },
        "exact_tolerance": args.exact_tolerance,
        "baseline_arbitrary_rotations_per_occurrence": 5,
        "candidate_arbitrary_rotations_per_occurrence": 4,
        "baseline_t_cost_per_occurrence": 5 * ARBITRARY_T_COST,
        "candidate_t_cost_per_occurrence": 4 * ARBITRARY_T_COST,
        "attempted_optimizer_runs": len(families) * args.seed_count,
        "passing_candidate_count": len(passing),
        "best_candidate": best,
        "top_candidates": top_candidates,
        "claim_boundary": {
            "bounded_four_rotation_two_cnot_search_found_exact_candidate": bool(passing),
            "would_reduce_arbitrary_occurrences_if_passing": 20 if passing else 0,
            "would_reduce_t_ledger_if_passing_best": 400 if passing else 0,
            "global_two_qubit_lower_bound_claimed": False,
            "basis_complete_claimed": False,
        },
        "interpretation": (
            "No exact four-arbitrary-rotation candidate was found in the bounded two-CNOT Rz/Ry skeleton search. "
            "This broadens T-B7-008 beyond the same two-CNOT skeleton, but it is not a global lower bound because "
            "it does not search arbitrary one-qubit Euler blocks, more CNOTs, measurements, ancillas, or all KAK-equivalent decompositions."
            if not passing
            else "A bounded four-arbitrary-rotation candidate was found and must be converted into a QASM rewrite before any physical ledger claim."
        ),
        "next_actions": [
            "If positive, emit QASM rewrites for all 20 w8_21 occurrences and run proof/Aer/resource checks.",
            "If negative, broaden the basis to Euler-local/KAK templates or allow three CNOTs while tracking arbitrary-rotation count.",
            "Convert repeated negative searches into a scoped minimality note rather than a global no-go theorem.",
        ],
        "limits": [
            "Bounded numerical search only; not a formal proof.",
            "Only Rz/Ry single-axis arbitrary rotations are searched.",
            "No physical layout, feed-forward, or factory timing claim is made.",
        ],
    }
    return payload


def write_markdown(path: Path, payload: dict) -> None:
    best = payload["best_candidate"]
    lines = [
        "# B7 w8_21 Bounded Broad-Skeleton Search",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Scope",
        "",
        f"- Method: `{payload['method']}`",
        f"- Template: `{payload['template_id']}`",
        f"- Family count: {payload['candidate_family']['family_count']}",
        f"- Seeds per family: {payload['candidate_family']['seed_count_per_family']}",
        f"- Optimizer runs: {payload['attempted_optimizer_runs']}",
        f"- Exact tolerance: {payload['exact_tolerance']}",
        "",
        "## Result",
        "",
        f"- Passing candidates: {payload['passing_candidate_count']}",
        f"- Best family: `{best['family_label']}`",
        f"- Best residual norm: {best['residual_norm']}",
        f"- Best max entry error: {best['max_abs_entry_error']}",
        f"- Candidate arbitrary rotations per occurrence: {payload['candidate_arbitrary_rotations_per_occurrence']}",
        f"- Baseline arbitrary rotations per occurrence: {payload['baseline_arbitrary_rotations_per_occurrence']}",
        "",
        "## Claim Boundary",
        "",
    ]
    for key, value in payload["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            payload["interpretation"],
            "",
            "## Next Actions",
            "",
        ]
    )
    for action in payload["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_proofs(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "certificate_type": "bounded_broad_skeleton_search_summary",
                    "method": payload["method"],
                    "status": payload["status"],
                    "family_count": payload["candidate_family"]["family_count"],
                    "attempted_optimizer_runs": payload["attempted_optimizer_runs"],
                    "passing_candidate_count": payload["passing_candidate_count"],
                    "best_candidate": payload["best_candidate"],
                    "claim_boundary": payload["claim_boundary"],
                },
                sort_keys=True,
            )
            + "\n"
        )
        for candidate in payload["top_candidates"]:
            handle.write(
                json.dumps(
                    {
                        "certificate_type": "bounded_broad_skeleton_top_candidate",
                        "method": payload["method"],
                        "candidate": candidate,
                    },
                    sort_keys=True,
                )
                + "\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-template-report", type=Path, default=Path("results/B7_nonlocal_template_block_scan_v0.json"))
    parser.add_argument("--source-small-block-report", type=Path, default=Path("results/B7_w8_21_small_block_synthesis_v0.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_w8_21_broad_skeleton_search_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B7_w8_21_broad_skeleton_search.md"))
    parser.add_argument("--proof-log", type=Path, default=Path("results/b7_w8_21_broad_skeleton_search/proofs.jsonl"))
    parser.add_argument("--last-updated", default="2026-06-16")
    parser.add_argument("--exact-tolerance", type=float, default=1e-8)
    parser.add_argument("--seed-count", type=int, default=3)
    parser.add_argument("--max-nfev", type=int, default=700)
    parser.add_argument("--family-limit", type=int, default=0, help="Optional prefix limit for faster partial scans.")
    parser.add_argument("--keep-top", type=int, default=20)
    parser.add_argument("--random-seed", type=int, default=79009)
    parser.add_argument("--summary-only", action="store_true", help="Print a compact run summary instead of the full JSON payload.")
    args = parser.parse_args()

    payload = run(args)
    write_json(args.json_output, payload)
    write_markdown(args.markdown_output, payload)
    write_proofs(args.proof_log, payload)
    if args.summary_only:
        summary = {
            "status": payload["status"],
            "method": payload["method"],
            "family_count": payload["candidate_family"]["family_count"],
            "total_family_count": payload["candidate_family"]["total_family_count"],
            "family_selection": payload["candidate_family"]["family_selection"],
            "attempted_optimizer_runs": payload["attempted_optimizer_runs"],
            "passing_candidate_count": payload["passing_candidate_count"],
            "best_family_label": payload["best_candidate"]["family_label"],
            "best_residual_norm": payload["best_candidate"]["residual_norm"],
            "best_max_abs_entry_error": payload["best_candidate"]["max_abs_entry_error"],
            "result": str(args.json_output),
            "markdown": str(args.markdown_output),
            "proof_log": str(args.proof_log),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
