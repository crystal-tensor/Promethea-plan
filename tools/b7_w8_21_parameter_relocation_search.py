#!/usr/bin/env python3
"""Search relocated five-angle Euler families for the w8_21 contexts.

The carrier-pricing gate shows that an external target-local rotation is exact
with a sixth local parameter, but that this does not save a resource.  This
gate asks a narrower alternative: can five arbitrary angles be relocated to
different local Euler slots, while retaining two CX gates and one fixed pi
scaffold, and still absorb each of the seven source-bound external-Rz
contexts?

This is a bounded numerical search.  It is not a lower-bound theorem and it
does not claim that all Clifford frames, ancillas, measurements, or layouts
have been exhausted.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import b7_w8_21_neighborhood_transfer as neighborhood


METHOD = "b7_w8_21_parameter_relocation_search_v0"
TEMPLATE_ID = "w8_21"
ARBITRARY_T_COST = 20
EXACT_TOLERANCE = 1e-10
BASE_PARAMS = neighborhood.BASE_PARAMS
LAYERS = ("pre", "mid", "post")
EULER_AXES = ("rz0", "ry", "rz1")
CNOT_DIRS = ("01", "10")

I2 = np.eye(2, dtype=complex)
P0 = np.array([[1, 0], [0, 0]], dtype=complex)
P1 = np.array([[0, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
CX_01 = np.kron(P0, I2) + np.kron(P1, X)
CX_10 = np.kron(I2, P0) + np.kron(X, P1)


def stable_hash(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rz(theta: float) -> np.ndarray:
    return np.array(
        [[np.exp(-0.5j * theta), 0.0], [0.0, np.exp(0.5j * theta)]],
        dtype=complex,
    )


def ry(theta: float) -> np.ndarray:
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)
    return np.array([[c, -s], [s, c]], dtype=complex)


def one_qubit_rotation(qubit: int, axis: str, theta: float) -> np.ndarray:
    single = rz(theta) if axis.startswith("rz") else ry(theta)
    return np.kron(single, I2) if qubit == 0 else np.kron(I2, single)


def euler_slots() -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
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
SOURCE_ARBITRARY = {
    SLOT_BY_LABEL["pre:q1:rz0"]: BASE_PARAMS[0],
    SLOT_BY_LABEL["mid:q1:rz0"]: BASE_PARAMS[1],
    SLOT_BY_LABEL["mid:q1:ry"]: BASE_PARAMS[2],
    SLOT_BY_LABEL["post:q1:rz0"]: BASE_PARAMS[3],
    SLOT_BY_LABEL["post:q1:ry"]: BASE_PARAMS[4],
}
SOURCE_PI_SLOT = SLOT_BY_LABEL["mid:q1:rz1"]


def candidate_unitary(
    cnot_dirs: tuple[str, str], fixed_angles: dict[int, float], free_slots: tuple[int, ...], values: np.ndarray
) -> np.ndarray:
    angles = np.zeros(len(SLOTS), dtype=float)
    for slot, value in fixed_angles.items():
        angles[slot] = value
    for slot, value in zip(free_slots, values):
        angles[slot] = float(value)

    total = np.eye(4, dtype=complex)
    cnot_index = 0
    for layer in LAYERS:
        for slot in SLOTS:
            if slot["layer"] == layer:
                total = one_qubit_rotation(slot["qubit"], slot["axis"], angles[slot["index"]]) @ total
        if layer != "post":
            total = (CX_01 if cnot_dirs[cnot_index] == "01" else CX_10) @ total
            cnot_index += 1
    return total


def phase_align(candidate: np.ndarray, target: np.ndarray) -> np.ndarray:
    overlap = np.trace(np.conjugate(target.T) @ candidate)
    return candidate * np.exp(-1j * np.angle(overlap)) if abs(overlap) > 1e-15 else candidate


def residual_vector(candidate: np.ndarray, target: np.ndarray) -> np.ndarray:
    diff = phase_align(candidate, target) - target
    return np.concatenate([diff.real.ravel(), diff.imag.ravel()])


def family_label(cnot_dirs: tuple[str, str], free_slots: tuple[int, ...]) -> str:
    free = ",".join(SLOTS[slot]["label"] for slot in free_slots)
    return f"cx{cnot_dirs[0]}-cx{cnot_dirs[1]}|fixed[mid:q1:rz1=pi]|free[{free}]"


def families() -> list[tuple[tuple[str, str], tuple[int, ...]]]:
    source_slots = set(SOURCE_ARBITRARY)
    universe = [slot["index"] for slot in SLOTS if slot["index"] != SOURCE_PI_SLOT]
    result = []
    for cnot_dirs in itertools.product(CNOT_DIRS, repeat=2):
        for free_slots in itertools.combinations(universe, 5):
            overlap = len(set(free_slots) & source_slots)
            if overlap < 4:
                continue
            # Remove the exact source placement; every retained family relocates
            # at least one arbitrary angle or changes the CX orientation.
            if cnot_dirs == ("01", "01") and set(free_slots) == source_slots:
                continue
            result.append((cnot_dirs, free_slots))
    return result


def initial_points(free_slots: tuple[int, ...], seed_count: int) -> list[np.ndarray]:
    source = np.array([SOURCE_ARBITRARY.get(slot, 0.0) for slot in free_slots], dtype=float)
    points = [source, np.zeros(len(free_slots), dtype=float)]
    for index in range(2, seed_count):
        offsets = np.array([((13 * index + 7 * slot) % 29 - 14) * math.pi / 29.0 for slot in free_slots])
        points.append(source + offsets)
    return points[:seed_count]


def context_targets(root: Path) -> list[dict[str, Any]]:
    rows = neighborhood.context_rows(root)
    source = neighborhood.source_unitary(BASE_PARAMS)
    targets = []
    for row in rows:
        operation = row["context_operation"]
        local = neighborhood.target_local_matrix(operation, row["target"])
        if local is None:
            raise ValueError(f"unsupported context operation: {operation}")
        matrix = local @ source if row["direction"] == "after" else source @ local
        targets.append({"row": row, "matrix": matrix})
    return targets


def optimize_family(
    target: np.ndarray,
    cnot_dirs: tuple[str, str],
    free_slots: tuple[int, ...],
    seed_count: int,
    max_nfev: int,
) -> dict[str, Any]:
    fixed_angles = {SOURCE_PI_SLOT: math.pi}

    def objective(values: np.ndarray) -> np.ndarray:
        return residual_vector(candidate_unitary(cnot_dirs, fixed_angles, free_slots, values), target)

    best: dict[str, Any] | None = None
    for seed_index, seed in enumerate(initial_points(free_slots, seed_count)):
        fit = least_squares(objective, seed, max_nfev=max_nfev, xtol=1e-12, ftol=1e-12, gtol=1e-12)
        matrix = candidate_unitary(cnot_dirs, fixed_angles, free_slots, fit.x)
        residual = float(np.linalg.norm(residual_vector(matrix, target)))
        candidate = {
            "seed_index": seed_index,
            "fitted_parameters": [float(value) for value in fit.x],
            "residual_norm": residual,
            "max_abs_entry_error": float(np.max(np.abs(phase_align(matrix, target) - target))),
            "optimizer_nfev": int(fit.nfev),
            "optimizer_status": int(fit.status),
            "optimizer_success": bool(fit.success),
        }
        if best is None or candidate["residual_norm"] < best["residual_norm"]:
            best = candidate
    assert best is not None
    return best


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    all_families = families()
    selected = all_families
    selection = "exhaustive"
    if args.family_limit:
        selected = all_families[: min(args.family_limit, len(all_families))]
        selection = "prefix_subset"
    targets = context_targets(root)
    fixed_angles = {SOURCE_PI_SLOT: math.pi}
    results = []
    optimizer_runs = 0
    for context_index, context in enumerate(targets, start=1):
        best = None
        passing = []
        for family_index, (cnot_dirs, free_slots) in enumerate(selected, start=1):
            fit = optimize_family(context["matrix"], cnot_dirs, free_slots, args.seed_count, args.max_nfev)
            optimizer_runs += args.seed_count
            row = {
                "family_index": family_index,
                "family_label": family_label(cnot_dirs, free_slots),
                "cnot_directions": list(cnot_dirs),
                "free_slots": [SLOTS[slot]["label"] for slot in free_slots],
                "arbitrary_rotation_count": 5,
                "candidate_cnot_count": 2,
                "fit": fit,
            }
            if best is None or fit["residual_norm"] < best["fit"]["residual_norm"]:
                best = row
            if fit["residual_norm"] <= args.exact_tolerance:
                passing.append(row)
        assert best is not None
        results.append(
            {
                "context_index": context_index,
                "direction": context["row"]["direction"],
                "target": context["row"]["target"],
                "context_operation": context["row"]["context_operation"],
                "line_span": context["row"]["line_span"],
                "tested_family_count": len(selected),
                "passing_family_count": len(passing),
                "best_candidate": best,
                "accepted_occurrence_removal": 0,
                "accepted_proxy_t_reduction": 0,
                "b7_credit": 0,
            }
        )

    best_residual = min(row["best_candidate"]["fit"]["residual_norm"] for row in results)
    exact_context_count = sum(row["passing_family_count"] > 0 for row in results)
    payload = {
        "title": "B7 w8_21 parameter relocation search",
        "status": "parameter_relocation_search_complete_no_five_angle_context_replay" if exact_context_count == 0 else "parameter_relocation_search_found_bounded_context_candidate",
        "method": METHOD,
        "template_id": TEMPLATE_ID,
        "classification": "bounded_relocated_euler_family_context_boundary",
        "last_updated": args.last_updated,
        "question": "Can five arbitrary Euler angles be relocated while retaining two CX gates and one pi scaffold, absorbing the seven external target-local Rz contexts without a sixth carrier?",
        "candidate_family": {
            "description": "two CX gates, one fixed mid:q1:rz1=pi scaffold, five arbitrary Euler slots, with at least four of the five source arbitrary slots retained",
            "slot_count": len(SLOTS),
            "free_slot_count": 5,
            "source_arbitrary_slot_labels": [SLOTS[slot]["label"] for slot in SOURCE_ARBITRARY],
            "fixed_scaffold": "mid:q1:rz1=pi",
            "total_family_count": len(all_families),
            "family_count": len(selected),
            "family_selection": selection,
            "seed_count_per_family": args.seed_count,
            "max_nfev_per_seed": args.max_nfev,
        },
        "fit_configuration": {
            "seed_count": args.seed_count,
            "max_nfev": args.max_nfev,
            "exact_tolerance": args.exact_tolerance,
            "objective": "global-phase-aligned 4x4 unitary residual",
        },
        "summary": {
            "tested_context_count": len(results),
            "exact_context_count": exact_context_count,
            "best_residual_norm": best_residual,
            "attempted_optimizer_runs": optimizer_runs,
            "baseline_arbitrary_parameter_count": 6,
            "candidate_arbitrary_parameter_count": 5,
            "baseline_cnot_count": 2,
            "candidate_cnot_count": 2,
            "accepted_occurrence_removal": 0,
            "accepted_proxy_t_reduction": 0,
            "b7_credit": 0,
            "validation_error_count": 0,
            "rewrite_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "source_bindings": {
            "source_qasm": neighborhood.SOURCE_QASM,
            "source_qasm_sha256": file_sha256(root / neighborhood.SOURCE_QASM),
            "scan_report": neighborhood.SCAN_PATH,
            "scan_report_sha256": file_sha256(root / neighborhood.SCAN_PATH),
            "neighborhood_result": "results/B7_w8_21_neighborhood_transfer_v0.json",
            "neighborhood_result_sha256": file_sha256(root / "results/B7_w8_21_neighborhood_transfer_v0.json"),
        },
        "claim_boundary": {
            "five_angle_relocated_family_found_exact_context": exact_context_count > 0,
            "global_two_qubit_lower_bound_claimed": False,
            "all_clifford_scaffolds_claimed": False,
            "ancilla_or_measurement_claimed": False,
            "full_circuit_rewrite_claimed": False,
            "resource_saving_claimed": False,
        },
        "results": results,
        "validation_errors": [],
        "payload_hash": "",
    }
    payload["payload_hash"] = stable_hash({key: value for key, value in payload.items() if key != "payload_hash"})
    return payload


def write_report(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# B7 w8_21 Parameter Relocation Search",
        "",
        f"- Status: `{payload['status']}`",
        f"- Method: `{payload['method']}`",
        f"- Contexts tested: `{summary['tested_context_count']}`",
        f"- Relocated families tested per context: `{payload['candidate_family']['family_count']}`",
        f"- Optimizer runs: `{summary['attempted_optimizer_runs']}`",
        f"- Exact context replays: `{summary['exact_context_count']}/{summary['tested_context_count']}`",
        f"- Best residual norm: `{summary['best_residual_norm']:.16g}`",
        "",
        "## Question",
        "",
        payload["question"],
        "",
        "## Scope",
        "",
        "The search keeps two CX gates and the exact `mid:q1:rz1=pi` scaffold, then relocates five arbitrary Euler angles. It retains at least four of the five source arbitrary slots and excludes the exact source placement. Each family is tested against the seven source-bound external target-local Rz contexts selected by the neighborhood gate.",
        "",
        "## Result",
        "",
        "No exact five-angle relocated-family replay was found in the declared bounded search." if summary["exact_context_count"] == 0 else "At least one bounded relocated-family replay was found; it requires source-circuit replay before any credit.",
        "",
        "| Context | Direction | Best residual | Best family |",
        "|---:|---|---:|---|",
    ]
    for row in payload["results"]:
        best = row["best_candidate"]
        lines.append(f"| {row['context_index']} | {row['direction']} | {best['fit']['residual_norm']:.16g} | `{best['family_label']}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The result closes only the declared five-angle relocated Euler family over the seven selected contexts. It is not a global minimality theorem, not a proof that six parameters are necessary in every circuit, and not a full-circuit rewrite or B7 resource credit.",
            "",
            "- Accepted occurrence removal: `0`",
            "- Accepted proxy-T reduction: `0`",
            "- B7 credit: `0`",
            "",
            "## Next Route",
            "",
            "The remaining high-value route is symbolic: characterize whether the external Rz changes a local invariant that cannot be represented by the retained five-angle two-CX family, then test a genuinely different Clifford scaffold or an occurrence-removing rewrite.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_w8_21_parameter_relocation_search_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B7_w8_21_parameter_relocation_search.md"))
    parser.add_argument("--last-updated", default="2026-07-15")
    parser.add_argument("--family-limit", type=int, default=0)
    parser.add_argument("--seed-count", type=int, default=2)
    parser.add_argument("--max-nfev", type=int, default=300)
    parser.add_argument("--exact-tolerance", type=float, default=EXACT_TOLERANCE)
    args = parser.parse_args()
    payload = run(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(args.markdown_output, payload)
    print(json.dumps({"status": payload["status"], "payload_hash": payload["payload_hash"], **payload["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
