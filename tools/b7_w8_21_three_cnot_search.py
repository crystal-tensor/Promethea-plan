#!/usr/bin/env python3
"""Bounded three-CNOT/four-arbitrary-angle search for B7 template w8_21.

This continues T-B7-009 after the two-CNOT broad-skeleton and Euler-local
negative searches.  It asks a bounded question: if one extra CNOT is allowed,
can a target-informed local Euler template represent w8_21 exactly while using
only four arbitrary local angles and the original exact pi scaffold?

The output is a search certificate, not a global synthesis lower bound.
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
TARGET_PARAMS = {
    "a": 1.4922506383856682,
    "b": 2.1870074319274799,
    "c": 0.52538524712872736,
    "d": 2.538142068316358,
    "e": 1.1254377896453873,
}

LAYERS = ("pre", "mid1", "mid2", "post")
EULER_AXES = ("rz0", "ry", "rz1")
CNOT_DIRS = ("01", "10")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rz(theta: float) -> np.ndarray:
    return np.array([[np.exp(-0.5j * theta), 0.0], [0.0, np.exp(0.5j * theta)]], dtype=complex)


def ry(theta: float) -> np.ndarray:
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)
    return np.array([[c, -s], [s, c]], dtype=complex)


I2 = np.eye(2, dtype=complex)
P0 = np.array([[1, 0], [0, 0]], dtype=complex)
P1 = np.array([[0, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
CX_01 = np.kron(P0, I2) + np.kron(P1, X)
CX_10 = np.kron(I2, P0) + np.kron(X, P1)


def one_qubit_rotation(qubit: int, axis: str, theta: float) -> np.ndarray:
    single = rz(theta) if axis.startswith("rz") else ry(theta)
    return np.kron(single, I2) if qubit == 0 else np.kron(I2, single)


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
        one_qubit_rotation(1, "rz0", params["a"]),
        CX_01,
        one_qubit_rotation(1, "rz0", params["b"]),
        one_qubit_rotation(1, "ry", params["c"]),
        one_qubit_rotation(1, "rz1", math.pi),
        CX_01,
        one_qubit_rotation(1, "rz0", params["d"]),
        one_qubit_rotation(1, "ry", params["e"]),
    ]
    total = np.eye(4, dtype=complex)
    for op in ops:
        total = op @ total
    return total


def euler_slots() -> list[dict]:
    slots = []
    for layer in LAYERS:
        for qubit in (0, 1):
            for axis in EULER_AXES:
                slots.append(
                    {
                        "index": len(slots),
                        "layer": layer,
                        "qubit": qubit,
                        "axis": axis,
                        "label": f"{layer}:q{qubit}:{axis}",
                    }
                )
    return slots


SLOTS = euler_slots()
SLOT_BY_LABEL = {slot["label"]: slot["index"] for slot in SLOTS}
SOURCE_TARGET_ANGLES = {
    SLOT_BY_LABEL["pre:q1:rz0"]: TARGET_PARAMS["a"],
    SLOT_BY_LABEL["mid1:q1:rz0"]: TARGET_PARAMS["b"],
    SLOT_BY_LABEL["mid1:q1:ry"]: TARGET_PARAMS["c"],
    SLOT_BY_LABEL["mid1:q1:rz1"]: math.pi,
    SLOT_BY_LABEL["post:q1:rz0"]: TARGET_PARAMS["d"],
    SLOT_BY_LABEL["post:q1:ry"]: TARGET_PARAMS["e"],
}
SOURCE_ARBITRARY_SLOTS = tuple(slot for slot, value in SOURCE_TARGET_ANGLES.items() if abs(value - math.pi) > 1e-12)
SOURCE_PI_SLOT = SLOT_BY_LABEL["mid1:q1:rz1"]


def candidate_unitary(cnot_dirs: tuple[str, str, str], fixed_angles: dict[int, float], free_slots: tuple[int, ...], values: np.ndarray) -> np.ndarray:
    angles = np.zeros(len(SLOTS), dtype=float)
    for slot, value in fixed_angles.items():
        angles[slot] = value
    for slot, value in zip(free_slots, values):
        angles[slot] = float(value)

    total = np.eye(4, dtype=complex)
    cnot_index = 0
    for layer in LAYERS:
        for slot in [slot for slot in SLOTS if slot["layer"] == layer]:
            total = one_qubit_rotation(slot["qubit"], slot["axis"], float(angles[slot["index"]])) @ total
        if layer != "post":
            total = (CX_01 if cnot_dirs[cnot_index] == "01" else CX_10) @ total
            cnot_index += 1
    return total


def family_label(cnot_dirs: tuple[str, str, str], fixed_angles: dict[int, float], free_slots: tuple[int, ...]) -> str:
    fixed = ",".join(f"{SLOTS[slot]['label']}=pi" for slot in sorted(fixed_angles)) or "zero-scaffold"
    free = ",".join(SLOTS[slot]["label"] for slot in free_slots)
    return f"cx{cnot_dirs[0]}-cx{cnot_dirs[1]}-cx{cnot_dirs[2]}|fixed[{fixed}]|free[{free}]"


def initial_points(free_slots: tuple[int, ...], seed_count: int, rng: np.random.Generator) -> list[np.ndarray]:
    source = np.array([SOURCE_TARGET_ANGLES.get(slot, 0.0) for slot in free_slots], dtype=float)
    points = [source, np.zeros(len(free_slots), dtype=float)]
    while len(points) < seed_count:
        points.append(rng.uniform(-math.pi, math.pi, size=len(free_slots)))
    return points[:seed_count]


def optimize_family(
    target: np.ndarray,
    cnot_dirs: tuple[str, str, str],
    fixed_angles: dict[int, float],
    free_slots: tuple[int, ...],
    seeds: list[np.ndarray],
    max_nfev: int,
) -> dict:
    def objective(values: np.ndarray) -> np.ndarray:
        return residual_vector(candidate_unitary(cnot_dirs, fixed_angles, free_slots, values), target)

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
        matrix = candidate_unitary(cnot_dirs, fixed_angles, free_slots, result.x)
        residual = float(np.linalg.norm(result.fun))
        candidate = {
            "family_label": family_label(cnot_dirs, fixed_angles, free_slots),
            "cnot_directions": list(cnot_dirs),
            "fixed_angles": [
                {"slot": SLOTS[slot]["label"], "value": float(value)}
                for slot, value in sorted(fixed_angles.items())
            ],
            "free_slots": [SLOTS[slot]["label"] for slot in free_slots],
            "seed_index": seed_index,
            "parameter_values": [float(value) for value in result.x],
            "residual_norm": residual,
            "max_abs_entry_error": float(np.max(np.abs(phase_align(matrix, target) - target))),
            "optimizer_success": bool(result.success),
            "optimizer_cost": float(result.cost),
            "optimizer_nfev": int(result.nfev),
            "cnot_count": 3,
            "arbitrary_rotation_count": len(free_slots),
            "exact_nonzero_scaffold_count": len([value for value in fixed_angles.values() if abs(value) > 1e-12]),
            "candidate_t_cost": len(free_slots) * ARBITRARY_T_COST,
            "baseline_t_cost": 5 * ARBITRARY_T_COST,
            "t_saving_if_exact": (5 - len(free_slots)) * ARBITRARY_T_COST,
        }
        if best is None or residual < best["residual_norm"]:
            best = candidate
    assert best is not None
    return best


def iter_target_informed_families(min_source_free_slots: int) -> list[tuple[tuple[str, str, str], dict[int, float], tuple[int, ...]]]:
    families = []
    free_slot_universe = [slot for slot in range(len(SLOTS)) if slot != SOURCE_PI_SLOT]
    for cnot_dirs in itertools.product(CNOT_DIRS, repeat=3):
        for free_slots in itertools.combinations(free_slot_universe, 4):
            source_overlap = len(set(free_slots) & set(SOURCE_ARBITRARY_SLOTS))
            if source_overlap < min_source_free_slots:
                continue
            fixed_angles = {SOURCE_PI_SLOT: math.pi}
            families.append((cnot_dirs, fixed_angles, free_slots))
    return families


def run(args: argparse.Namespace) -> dict:
    rng = np.random.default_rng(args.random_seed)
    target = target_unitary()
    all_families = iter_target_informed_families(args.min_source_free_slots)
    families = all_families
    family_selection = "exhaustive"
    if args.family_limit:
        limit = min(args.family_limit, len(all_families))
        selected_indices = np.linspace(0, len(all_families) - 1, num=limit, dtype=int)
        families = [all_families[int(index)] for index in selected_indices]
        family_selection = "evenly_spaced_subset"

    top_candidates: list[dict] = []
    passing = []
    attempted_optimizer_runs = 0
    for index, (cnot_dirs, fixed_angles, free_slots) in enumerate(families, start=1):
        seeds = initial_points(free_slots, args.seed_count, rng)
        result = optimize_family(target, cnot_dirs, fixed_angles, free_slots, seeds, args.max_nfev)
        result["family_index"] = index
        attempted_optimizer_runs += len(seeds)
        top_candidates.append(result)
        top_candidates.sort(key=lambda item: item["residual_norm"])
        top_candidates = top_candidates[: args.keep_top]
        if result["residual_norm"] <= args.exact_tolerance:
            passing.append(result)

    best = top_candidates[0]
    status = (
        "w8_21_three_cnot_search_positive_proxy_not_physical_layout"
        if passing
        else "w8_21_three_cnot_search_negative_boundary_not_global_lower_bound"
    )
    payload = {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 w8_21 bounded three-CNOT synthesis search",
        "status": status,
        "method": "b7_w8_21_three_cnot_search_v0",
        "last_updated": args.last_updated,
        "source_template_report": str(args.source_template_report),
        "source_euler_local_report": str(args.source_euler_local_report),
        "template_id": "w8_21",
        "question": "Can one extra CNOT let a target-informed local Euler template represent w8_21 exactly with only four arbitrary local angles?",
        "candidate_family": {
            "description": "three CNOTs with pre/mid1/mid2/post local Rz-Ry-Rz Euler layers on both qubits",
            "basis": "local Rz/Ry Euler layers plus three CNOTs; four free arbitrary angles; original source pi scaffold fixed",
            "family_mode": "target-informed",
            "local_euler_slot_count": len(SLOTS),
            "free_slot_count": 4,
            "min_source_free_slots": args.min_source_free_slots,
            "total_family_count": len(all_families),
            "family_count": len(families),
            "family_selection": family_selection,
            "seed_count_per_family": args.seed_count,
            "max_nfev_per_seed": args.max_nfev,
            "slot_labels": [slot["label"] for slot in SLOTS],
            "source_arbitrary_slot_labels": [SLOTS[slot]["label"] for slot in SOURCE_ARBITRARY_SLOTS],
            "source_pi_slot_label": SLOTS[SOURCE_PI_SLOT]["label"],
        },
        "exact_tolerance": args.exact_tolerance,
        "baseline_cnot_count": 2,
        "candidate_cnot_count": 3,
        "baseline_arbitrary_rotations_per_occurrence": 5,
        "candidate_arbitrary_rotations_per_occurrence": 4,
        "baseline_t_cost_per_occurrence": 5 * ARBITRARY_T_COST,
        "candidate_t_cost_per_occurrence": 4 * ARBITRARY_T_COST,
        "attempted_optimizer_runs": attempted_optimizer_runs,
        "passing_candidate_count": len(passing),
        "best_candidate": best,
        "top_candidates": top_candidates,
        "claim_boundary": {
            "three_cnot_four_rotation_search_found_exact_candidate": bool(passing),
            "allows_one_extra_cnot": True,
            "allows_local_euler_layers": True,
            "keeps_source_pi_scaffold": True,
            "would_reduce_arbitrary_occurrences_if_passing": 20 if passing else 0,
            "would_reduce_t_ledger_if_passing_best": 400 if passing else 0,
            "global_two_qubit_lower_bound_claimed": False,
            "all_three_cnot_clifford_scaffolds_claimed": False,
            "ancilla_or_measurement_claimed": False,
        },
        "interpretation": (
            "No exact four-arbitrary-angle candidate was found in this bounded target-informed three-CNOT search. "
            "This means that adding one extra CNOT did not rescue the specific four-arbitrary-angle compression "
            "families tested here. It is still not a global lower bound over all three-CNOT circuits, Clifford "
            "scaffolds, ancillas, measurements, or symbolic KAK decompositions."
            if not passing
            else "A bounded three-CNOT candidate was found and must be converted into a concrete QASM rewrite before any FT ledger claim."
        ),
        "next_actions": [
            "If positive, emit QASM rewrites for all 20 w8_21 occurrences and rerun proof/Aer/resource checks.",
            "If negative, write a scoped minimality note covering T-B7-008/T-B7-009 searched families.",
            "Do not count any w8_21 ledger reduction until an exact rewrite is emitted and verified.",
        ],
        "limits": [
            "Bounded numerical search only; not a formal proof.",
            "Only target-informed free-slot choices with the source pi scaffold are included.",
            "No physical layout, feed-forward, or factory timing claim is made.",
        ],
    }
    return payload


def write_markdown(path: Path, payload: dict) -> None:
    best = payload["best_candidate"]
    lines = [
        "# B7 w8_21 Bounded Three-CNOT Search",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Scope",
        "",
        f"- Method: `{payload['method']}`",
        f"- Template: `{payload['template_id']}`",
        f"- Family count: {payload['candidate_family']['family_count']}",
        f"- Total family count: {payload['candidate_family']['total_family_count']}",
        f"- Family mode: `{payload['candidate_family']['family_mode']}`",
        f"- Min source free slots: {payload['candidate_family']['min_source_free_slots']}",
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
        f"- Candidate CNOT count: {payload['candidate_cnot_count']}",
        f"- Candidate arbitrary rotations per occurrence: {payload['candidate_arbitrary_rotations_per_occurrence']}",
        f"- Baseline arbitrary rotations per occurrence: {payload['baseline_arbitrary_rotations_per_occurrence']}",
        "",
        "## Claim Boundary",
        "",
    ]
    for key, value in payload["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Interpretation", "", payload["interpretation"], "", "## Next Actions", ""])
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
                    "certificate_type": "three_cnot_search_summary",
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
                        "certificate_type": "three_cnot_top_candidate",
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
    parser.add_argument("--source-euler-local-report", type=Path, default=Path("results/B7_w8_21_euler_local_search_v0.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_w8_21_three_cnot_search_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B7_w8_21_three_cnot_search.md"))
    parser.add_argument("--proof-log", type=Path, default=Path("results/b7_w8_21_three_cnot_search/proofs.jsonl"))
    parser.add_argument("--last-updated", default="2026-06-16")
    parser.add_argument("--exact-tolerance", type=float, default=1e-8)
    parser.add_argument("--seed-count", type=int, default=4)
    parser.add_argument("--max-nfev", type=int, default=700)
    parser.add_argument("--family-limit", type=int, default=0, help="Optional evenly spaced subset for faster partial scans.")
    parser.add_argument("--keep-top", type=int, default=20)
    parser.add_argument("--random-seed", type=int, default=79333)
    parser.add_argument("--min-source-free-slots", type=int, default=3)
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
