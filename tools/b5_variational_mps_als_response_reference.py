#!/usr/bin/env python3
"""Build a non-exact-seeded variational MPS/ALS pressure reference for B5."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import linalg
from scipy import sparse

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from b10_t1_d5_observable_denominator_table import (  # noqa: E402
    ETA,
    basis_states,
    hubbard_hamiltonian,
    local_density_diagonal,
)
from b5_mps_truncation_response_reference import (  # noqa: E402
    full_tensor_to_fixed_vector,
    lowest_eigenpair,
    mps_reconstruct,
    relative_error,
    solve_response_from_state,
)


METHOD = "b5_variational_mps_als_response_reference_v0"
STATUS = "variational_mps_als_pressure_reference_not_production_dmrg_or_advantage_claim"
MODEL_STATUS = "non_exact_state_seeded_variational_mps_als_pressure_reference"
DEFAULT_BOND_DIMS = (2, 4)
DEFAULT_SWEEPS = 8
DEFAULT_RESTARTS = 3
RNG_SEED = 20260618


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def local_state(up_bits: int, down_bits: int, site: int) -> int:
    up = (up_bits >> site) & 1
    down = (down_bits >> site) & 1
    return int(up + 2 * down)


def product_pattern(sites: int) -> list[int]:
    """Return a half-filled product pattern with alternating up/down sites."""
    pattern: list[int] = []
    for site in range(sites):
        pattern.append(1 if site % 2 == 0 else 2)
    return pattern


def random_mps(
    sites: int,
    max_bond_dimension: int,
    rng: np.random.Generator,
    noise_scale: float = 0.02,
) -> list[np.ndarray]:
    ranks = [1] + [min(max_bond_dimension, 4 ** min(cut, sites - cut)) for cut in range(1, sites)] + [1]
    tensors = [
        rng.normal(0.0, noise_scale, size=(ranks[site], 4, ranks[site + 1]))
        for site in range(sites)
    ]
    pattern = product_pattern(sites)
    for site, physical in enumerate(pattern):
        tensors[site][0, physical, 0] += 1.0
    return tensors


def fixed_state_from_mps(mps: list[np.ndarray], sites: int, n_up: int, n_down: int) -> dict[str, Any]:
    tensor = mps_reconstruct(mps)
    full_norm = float(np.linalg.norm(tensor.ravel()))
    fixed_vector = full_tensor_to_fixed_vector(tensor, sites, n_up, n_down)
    fixed_norm = float(np.linalg.norm(fixed_vector))
    if fixed_norm <= 1e-14:
        return {
            "state": None,
            "full_norm": full_norm,
            "fixed_sector_norm_before_normalization": fixed_norm,
            "fixed_sector_leakage": max(0.0, full_norm**2 - fixed_norm**2),
        }
    return {
        "state": fixed_vector / fixed_norm,
        "full_norm": full_norm,
        "fixed_sector_norm_before_normalization": fixed_norm,
        "fixed_sector_leakage": max(0.0, full_norm**2 - fixed_norm**2),
    }


def energy_of_mps(
    mps: list[np.ndarray],
    matrix: sparse.csr_matrix,
    sites: int,
    n_up: int,
    n_down: int,
) -> dict[str, Any]:
    state_payload = fixed_state_from_mps(mps, sites, n_up, n_down)
    state = state_payload["state"]
    if state is None:
        return {**state_payload, "energy": math.inf, "energy_variance": math.inf}
    energy = float(np.dot(state, matrix @ state))
    variance = float(np.dot(state, matrix @ (matrix @ state)) - energy**2)
    return {**state_payload, "energy": energy, "energy_variance": max(0.0, variance)}


def local_basis_matrix(
    mps: list[np.ndarray],
    site: int,
    sites: int,
    n_up: int,
    n_down: int,
) -> np.ndarray:
    original = mps[site]
    parameter_count = int(original.size)
    basis_columns: list[np.ndarray] = []
    for flat_index in range(parameter_count):
        trial_tensor = np.zeros_like(original)
        trial_tensor.reshape(-1)[flat_index] = 1.0
        mps[site] = trial_tensor
        tensor = mps_reconstruct(mps)
        basis_columns.append(full_tensor_to_fixed_vector(tensor, sites, n_up, n_down))
    mps[site] = original
    return np.column_stack(basis_columns)


def optimize_site(
    mps: list[np.ndarray],
    site: int,
    matrix: sparse.csr_matrix,
    sites: int,
    n_up: int,
    n_down: int,
) -> dict[str, Any]:
    basis = local_basis_matrix(mps, site, sites, n_up, n_down)
    norm_matrix = basis.T @ basis
    h_matrix = basis.T @ (matrix @ basis)
    reg = 1e-10 * max(1.0, float(np.trace(norm_matrix)) / max(1, norm_matrix.shape[0]))
    norm_matrix = norm_matrix + reg * np.eye(norm_matrix.shape[0])
    values, vectors = linalg.eigh(h_matrix, norm_matrix, check_finite=False)
    best = np.asarray(vectors[:, int(np.argmin(values))], dtype=np.float64)
    tensor = best.reshape(mps[site].shape)
    scale = float(np.linalg.norm(tensor.ravel()))
    if scale > 0.0:
        tensor = tensor / scale
    mps[site] = tensor
    return {
        "site": site,
        "local_parameter_count": int(basis.shape[1]),
        "local_rank": int(np.linalg.matrix_rank(norm_matrix, tol=1e-9)),
        "local_lowest_energy": float(np.min(values)),
        "regularization": reg,
    }


def run_als(
    matrix: sparse.csr_matrix,
    sites: int,
    n_up: int,
    n_down: int,
    bond_dimension: int,
    restarts: int,
    sweeps: int,
    seed: int,
) -> dict[str, Any]:
    best_payload: dict[str, Any] | None = None
    restart_summaries = []
    for restart in range(restarts):
        rng = np.random.default_rng(seed + 1009 * restart + 97 * bond_dimension + 13 * sites)
        mps = random_mps(sites, bond_dimension, rng)
        initial = energy_of_mps(mps, matrix, sites, n_up, n_down)
        sweep_history = []
        for sweep in range(sweeps):
            local_updates = []
            direction = range(sites) if sweep % 2 == 0 else range(sites - 1, -1, -1)
            for site in direction:
                local_updates.append(optimize_site(mps, site, matrix, sites, n_up, n_down))
            energy_payload = energy_of_mps(mps, matrix, sites, n_up, n_down)
            sweep_history.append(
                {
                    "sweep": sweep + 1,
                    "direction": "left_to_right" if sweep % 2 == 0 else "right_to_left",
                    "energy": float(energy_payload["energy"]),
                    "energy_variance": float(energy_payload["energy_variance"]),
                    "fixed_sector_norm_before_normalization": float(
                        energy_payload["fixed_sector_norm_before_normalization"]
                    ),
                    "max_local_parameter_count": max(update["local_parameter_count"] for update in local_updates),
                    "min_local_rank": min(update["local_rank"] for update in local_updates),
                }
            )
        final_payload = energy_of_mps(mps, matrix, sites, n_up, n_down)
        restart_summary = {
            "restart": restart,
            "initial_energy": float(initial["energy"]),
            "final_energy": float(final_payload["energy"]),
            "final_energy_variance": float(final_payload["energy_variance"]),
            "final_fixed_sector_norm_before_normalization": float(
                final_payload["fixed_sector_norm_before_normalization"]
            ),
            "sweep_history": sweep_history,
        }
        restart_summaries.append(restart_summary)
        candidate = {
            "mps": mps,
            "state": final_payload["state"],
            "full_norm": final_payload["full_norm"],
            "fixed_sector_norm_before_normalization": final_payload["fixed_sector_norm_before_normalization"],
            "fixed_sector_leakage": final_payload["fixed_sector_leakage"],
            "energy": final_payload["energy"],
            "energy_variance": final_payload["energy_variance"],
            "restart": restart,
            "restart_summaries": restart_summaries,
        }
        if best_payload is None or float(candidate["energy"]) < float(best_payload["energy"]):
            best_payload = candidate
    if best_payload is None or best_payload.get("state") is None:
        raise RuntimeError("variational MPS ALS did not produce a nonzero fixed-sector state")
    return {
        "state": best_payload["state"],
        "energy": float(best_payload["energy"]),
        "energy_variance": float(best_payload["energy_variance"]),
        "full_norm": float(best_payload["full_norm"]),
        "fixed_sector_norm_before_normalization": float(
            best_payload["fixed_sector_norm_before_normalization"]
        ),
        "fixed_sector_leakage": float(best_payload["fixed_sector_leakage"]),
        "selected_restart": int(best_payload["restart"]),
        "restart_summaries": restart_summaries,
    }


def build_rows(
    d5_source: dict[str, Any],
    mps_pressure_source: dict[str, Any],
    bond_dimensions: tuple[int, ...],
    restarts: int,
    sweeps: int,
    seed: int,
) -> list[dict[str, Any]]:
    pressure_rows = {
        (int(row["sites"]), float(row["u_over_t"])): row
        for row in mps_pressure_source.get("rows", [])
    }
    rows: list[dict[str, Any]] = []
    for d5_row in d5_source.get("rows", []):
        sites = int(d5_row["sites"])
        u_over_t = float(d5_row["u_over_t"])
        t_value = float(d5_row.get("t", 1.0))
        n_up = sites // 2
        n_down = sites // 2
        matrix = hubbard_hamiltonian(sites, n_up, n_down, u_over_t * t_value, t_value)
        exact_ground_energy, exact_psi = lowest_eigenpair(matrix)
        density = local_density_diagonal(sites, n_up, n_down, sites // 2)
        exact_susceptibility = float(d5_row["susceptibility_proxy"])
        bond_rows = []
        for bond_dimension in bond_dimensions:
            optimized = run_als(
                matrix,
                sites,
                n_up,
                n_down,
                bond_dimension=bond_dimension,
                restarts=restarts,
                sweeps=sweeps,
                seed=seed,
            )
            psi_mps = np.asarray(optimized.pop("state"), dtype=np.float64)
            response = solve_response_from_state(matrix, psi_mps, exact_ground_energy, density)
            susceptibility = float(response["susceptibility_proxy"])
            bond_rows.append(
                {
                    "bond_dimension": int(bond_dimension),
                    "energy_expectation": float(optimized["energy"]),
                    "energy_error_per_site": abs(float(optimized["energy"]) - exact_ground_energy) / sites,
                    "energy_variance": float(optimized["energy_variance"]),
                    "overlap_with_exact_ground_state": abs(float(np.dot(exact_psi, psi_mps))),
                    "susceptibility_proxy": susceptibility,
                    "absolute_response_error": abs(susceptibility - exact_susceptibility),
                    "relative_response_error": relative_error(susceptibility, exact_susceptibility),
                    "response_relative_residual": float(response["relative_residual"]),
                    "response_iterations": int(response["iterations"]),
                    "response_solver_info": int(response["solver_info"]),
                    "optimizer": "one_site_variational_mps_als_generalized_eigen_sweeps",
                    "selected_by": "lowest_variational_energy_across_restarts_not_response_target",
                    "exact_state_seeded": False,
                    "exact_energy_used_for_response_shift": True,
                    **optimized,
                }
            )
        selected = min(bond_rows, key=lambda row: float(row["energy_expectation"]))
        pressure_row = pressure_rows.get((sites, u_over_t), {})
        seeded_error = pressure_row.get("selected_relative_response_error")
        rows.append(
            {
                "model": "one_dimensional_fermi_hubbard_half_filled_density_response",
                "sites": sites,
                "u_over_t": u_over_t,
                "t": t_value,
                "eta": float(d5_row.get("eta", ETA)),
                "exact_d5_susceptibility_proxy": exact_susceptibility,
                "exact_d5_hilbert_dimension": int(d5_row["hilbert_dimension"]),
                "exact_ground_energy": exact_ground_energy,
                "bond_dimensions_tested": list(bond_dimensions),
                "selected_bond_dimension": int(selected["bond_dimension"]),
                "selected_susceptibility_proxy": float(selected["susceptibility_proxy"]),
                "selected_relative_response_error": float(selected["relative_response_error"]),
                "selected_energy_error_per_site": float(selected["energy_error_per_site"]),
                "selected_energy_variance": float(selected["energy_variance"]),
                "selected_overlap_with_exact_ground_state": float(selected["overlap_with_exact_ground_state"]),
                "selected_fixed_sector_norm_before_normalization": float(
                    selected["fixed_sector_norm_before_normalization"]
                ),
                "selected_response_relative_residual": float(selected["response_relative_residual"]),
                "seeded_mps_pressure_relative_response_error": (
                    float(seeded_error) if seeded_error is not None else None
                ),
                "variational_mps_beats_seeded_mps_pressure_reference": (
                    bool(float(selected["relative_response_error"]) + 1e-9 < float(seeded_error))
                    if seeded_error is not None
                    else False
                ),
                "bond_dimension_rows": bond_rows,
                "exact_state_seeded": False,
                "variational_mps_als": True,
                "production_dmrg": False,
                "candidate_quantum_response_beats_variational_mps_reference": False,
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]], bond_dimensions: tuple[int, ...], restarts: int, sweeps: int) -> dict[str, Any]:
    selected_errors = [float(row["selected_relative_response_error"]) for row in rows]
    selected_energy_errors = [float(row["selected_energy_error_per_site"]) for row in rows]
    selected_overlaps = [float(row["selected_overlap_with_exact_ground_state"]) for row in rows]
    selected_norms = [float(row["selected_fixed_sector_norm_before_normalization"]) for row in rows]
    return {
        "instance_count": len(rows),
        "site_values": sorted({int(row["sites"]) for row in rows}),
        "u_over_t_values": sorted({float(row["u_over_t"]) for row in rows}),
        "bond_dimensions_tested": list(bond_dimensions),
        "selected_bond_dimensions": sorted({int(row["selected_bond_dimension"]) for row in rows}),
        "restarts_per_instance_bond_dimension": restarts,
        "sweeps_per_restart": sweeps,
        "selected_mean_relative_response_error": float(np.mean(selected_errors)),
        "selected_median_relative_response_error": float(np.median(selected_errors)),
        "selected_max_relative_response_error": float(np.max(selected_errors)),
        "selected_mean_energy_error_per_site": float(np.mean(selected_energy_errors)),
        "selected_max_energy_error_per_site": float(np.max(selected_energy_errors)),
        "selected_min_overlap_with_exact_ground_state": float(np.min(selected_overlaps)),
        "selected_min_fixed_sector_norm_before_normalization": float(np.min(selected_norms)),
        "variational_mps_rows_beating_seeded_mps_pressure_reference": sum(
            1 for row in rows if row["variational_mps_beats_seeded_mps_pressure_reference"]
        ),
        "max_exact_d5_hilbert_dimension": max(int(row["exact_d5_hilbert_dimension"]) for row in rows),
        "exact_state_seeded": False,
        "variational_mps_als": True,
        "production_dmrg": False,
        "quantum_response_win_claimed": False,
        "accuracy_per_resource_win_claimed": False,
        "uses_exact_target_for_selection": False,
        "exact_energy_used_for_response_shift": True,
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload.get("summary", {})
    if payload.get("benchmark_id") != "B5":
        errors.append("benchmark_id must be B5")
    if payload.get("method") != METHOD:
        errors.append("method mismatch")
    if payload.get("status") != STATUS:
        errors.append("status mismatch")
    if payload.get("exact_state_seeded") is not False:
        errors.append("payload must disclose exact_state_seeded=false")
    if payload.get("production_dmrg") is not False:
        errors.append("payload must not claim production DMRG")
    if payload.get("explicit_not_quantum_advantage") is not True:
        errors.append("must explicitly avoid quantum advantage claims")
    if payload.get("explicit_not_bqp_separation") is not True:
        errors.append("must explicitly avoid BQP separation claims")
    if summary.get("instance_count") != 9:
        errors.append("expected 9 B5 D5 instances")
    if summary.get("exact_state_seeded") is not False:
        errors.append("summary must disclose exact_state_seeded=false")
    if summary.get("production_dmrg") is not False:
        errors.append("summary must not claim production DMRG")
    if summary.get("quantum_response_win_claimed") is not False:
        errors.append("must not claim quantum response win")
    if summary.get("accuracy_per_resource_win_claimed") is not False:
        errors.append("must not claim accuracy-per-resource win")
    if summary.get("uses_exact_target_for_selection") is not False:
        errors.append("must not use exact response target for selection")
    for row in payload.get("rows", []):
        label = f"sites={row.get('sites')} U/t={row.get('u_over_t')}"
        if row.get("exact_state_seeded") is not False:
            errors.append(f"row must disclose exact_state_seeded=false: {label}")
        if row.get("production_dmrg") is not False:
            errors.append(f"row must not claim production DMRG: {label}")
        if row.get("candidate_quantum_response_beats_variational_mps_reference") is not False:
            errors.append(f"row must not claim quantum win: {label}")
        if float(row.get("selected_response_relative_residual", 1.0)) > 1e-6:
            errors.append(f"response residual above tolerance: {label}")
    return errors


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# B5 Variational MPS/ALS Response Reference v0.1",
        "",
        f"Last updated: {payload['last_updated']}",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Dependency B10 table: `{payload['dependency_b10_table']}`",
        f"- Dependency seeded MPS pressure reference: `{payload['dependency_seeded_mps_pressure_result']}`",
        f"- Instances: {summary['instance_count']}",
        f"- Sites: {summary['site_values']}",
        f"- U/t values: {summary['u_over_t_values']}",
        f"- Bond dimensions tested: {summary['bond_dimensions_tested']}",
        f"- Selected bond dimensions: {summary['selected_bond_dimensions']}",
        f"- Restarts per instance/bond dimension: {summary['restarts_per_instance_bond_dimension']}",
        f"- Sweeps per restart: {summary['sweeps_per_restart']}",
        "- Selected mean / median / max relative response error: "
        f"{summary['selected_mean_relative_response_error']:.6g} / "
        f"{summary['selected_median_relative_response_error']:.6g} / "
        f"{summary['selected_max_relative_response_error']:.6g}",
        "- Selected mean / max energy error per site: "
        f"{summary['selected_mean_energy_error_per_site']:.6g} / "
        f"{summary['selected_max_energy_error_per_site']:.6g}",
        f"- Min selected overlap with exact ground state: {summary['selected_min_overlap_with_exact_ground_state']:.6g}",
        "- Rows beating exact-state-seeded MPS pressure reference: "
        f"{summary['variational_mps_rows_beating_seeded_mps_pressure_reference']}",
        f"- Exact-state seeded: {summary['exact_state_seeded']}",
        f"- Variational MPS/ALS: {summary['variational_mps_als']}",
        f"- Production DMRG: {summary['production_dmrg']}",
        f"- Validation errors: {len(payload['validation_errors'])}",
        "",
        "## Interpretation",
        "",
        "- This is a non-exact-state-seeded variational MPS/ALS pressure reference for B5/T-B5-003.",
        "- It initializes from a product state plus random perturbations, then performs one-site generalized-eigenproblem sweeps over MPS tensors.",
        "- Selection is by lowest variational energy across restarts, not by response-target error.",
        "- The D5 exact response target is used only for evaluation; the exact ground energy is still used as the response-operator shift to match the existing D5 denominator definition.",
        "- This is not a mature canonical-environment DMRG implementation, not a quantum response kernel, and not an accuracy-per-resource win.",
        "",
        "## Rows",
        "",
        "| Sites | U/t | Bond dim | Exact D5 chi | Var-MPS chi | Rel. response error | Energy error/site | Overlap | Beats seeded pressure? |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {sites} | {u_over_t:.1f} | {selected_bond_dimension} | "
            "{exact_d5_susceptibility_proxy:.8g} | {selected_susceptibility_proxy:.8g} | "
            "{selected_relative_response_error:.6g} | {selected_energy_error_per_site:.6g} | "
            "{selected_overlap_with_exact_ground_state:.6g} | {beats} |".format(
                beats=row["variational_mps_beats_seeded_mps_pressure_reference"],
                **row,
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Now supported: {payload['claim_boundary']['now_supported']}",
            f"- Still not supported: {payload['claim_boundary']['still_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--d5-result", type=Path, default=Path("results/B10_t1_d5_observable_denominator_table_v0.json"))
    parser.add_argument(
        "--seeded-mps-result",
        type=Path,
        default=Path("results/B5_mps_truncation_response_reference_v0.json"),
    )
    parser.add_argument("--result-output", type=Path, default=Path("results/B5_variational_mps_als_response_reference_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B5_variational_mps_als_response_reference.md"))
    parser.add_argument("--bond-dimensions", type=int, nargs="+", default=list(DEFAULT_BOND_DIMS))
    parser.add_argument("--restarts", type=int, default=DEFAULT_RESTARTS)
    parser.add_argument("--sweeps", type=int, default=DEFAULT_SWEEPS)
    parser.add_argument("--seed", type=int, default=RNG_SEED)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    started = time.time()
    d5_source = load_json(args.d5_result)
    seeded_mps_source = load_json(args.seeded_mps_result)
    bond_dimensions = tuple(sorted({int(value) for value in args.bond_dimensions}))
    rows = build_rows(
        d5_source,
        seeded_mps_source,
        bond_dimensions=bond_dimensions,
        restarts=int(args.restarts),
        sweeps=int(args.sweeps),
        seed=int(args.seed),
    )
    payload: dict[str, Any] = {
        "benchmark_id": "B5",
        "problem_id": 38,
        "title": "Strongly Correlated Matter via Variational MPS/ALS Reference",
        "version": "0.1",
        "last_updated": "2026-06-18",
        "status": STATUS,
        "method": METHOD,
        "model_status": MODEL_STATUS,
        "dependency_b10_table": d5_source.get("method"),
        "dependency_b10_result": str(args.d5_result),
        "dependency_seeded_mps_pressure_result": str(args.seeded_mps_result),
        "exact_state_seeded": False,
        "variational_mps_als": True,
        "production_dmrg": False,
        "uses_exact_target_for_selection": False,
        "exact_energy_used_for_response_shift": True,
        "explicit_not_quantum_advantage": True,
        "explicit_not_bqp_separation": True,
        "explicit_not_production_dmrg": True,
        "claim_boundary": {
            "now_supported": (
                "A non-exact-state-seeded variational MPS/ALS optimizer now provides a small-scale "
                "tensor reference attempt on the same B10 D5 Hubbard response rows."
            ),
            "still_not_supported": (
                "This is not canonical-environment production DMRG, not a 2D/doped correlated-matter "
                "solver, not a quantum response kernel, and not an accuracy-per-resource win."
            ),
            "next_gate": (
                "Replace this prototype with a mature variational DMRG/MPS implementation or compare "
                "a real quantum response kernel against the D5 and tensor references after full cost accounting."
            ),
        },
        "summary": summarize(rows, bond_dimensions, int(args.restarts), int(args.sweeps)),
        "rows": rows,
        "runtime_seconds": time.time() - started,
    }
    payload["validation_errors"] = validate(payload)
    args.result_output.write_text(
        json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(payload, args.markdown_output)
    if args.pretty:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
        print(f"validation_errors={len(payload['validation_errors'])}")
    else:
        print(
            f"wrote {args.result_output} and {args.markdown_output}; "
            f"validation_errors={len(payload['validation_errors'])}"
        )


if __name__ == "__main__":
    main()
