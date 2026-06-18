#!/usr/bin/env python3
"""Build a B5 MPS/Schmidt-truncation pressure reference for Hubbard response."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as spla

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from b10_t1_d5_observable_denominator_table import (  # noqa: E402
    ETA,
    RTOL,
    basis_states,
    hubbard_hamiltonian,
    local_density_diagonal,
)


METHOD = "b5_mps_schmidt_truncation_response_reference_v0"
STATUS = "mps_schmidt_truncation_response_reference_not_dmrg_or_advantage_claim"
DEFAULT_BOND_DIMS = (2, 4, 8, 16)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def lowest_eigenpair(matrix: sparse.csr_matrix) -> tuple[float, np.ndarray]:
    dim = matrix.shape[0]
    if dim <= 4:
        values, vectors = np.linalg.eigh(matrix.toarray())
        return float(values[0]), np.asarray(vectors[:, 0], dtype=np.float64)
    values, vectors = spla.eigsh(matrix, k=1, which="SA", tol=1e-10)
    return float(values[0]), np.asarray(vectors[:, 0], dtype=np.float64)


def local_state(up_bits: int, down_bits: int, site: int) -> int:
    up = (up_bits >> site) & 1
    down = (down_bits >> site) & 1
    return int(up + 2 * down)


def fixed_vector_to_full_tensor(psi: np.ndarray, sites: int, n_up: int, n_down: int) -> np.ndarray:
    tensor = np.zeros((4,) * sites, dtype=np.float64)
    for amplitude, (up_bits, down_bits) in zip(psi, basis_states(sites, n_up, n_down)):
        key = tuple(local_state(up_bits, down_bits, site) for site in range(sites))
        tensor[key] = float(amplitude)
    return tensor


def full_tensor_to_fixed_vector(tensor: np.ndarray, sites: int, n_up: int, n_down: int) -> np.ndarray:
    values = []
    for up_bits, down_bits in basis_states(sites, n_up, n_down):
        key = tuple(local_state(up_bits, down_bits, site) for site in range(sites))
        values.append(float(tensor[key]))
    return np.asarray(values, dtype=np.float64)


def mps_decompose(tensor: np.ndarray, max_bond_dimension: int) -> tuple[list[np.ndarray], list[dict[str, Any]]]:
    mps: list[np.ndarray] = []
    diagnostics: list[dict[str, Any]] = []
    current = tensor
    left_rank = 1
    site_count = tensor.ndim
    for site in range(site_count - 1):
        matrix = current.reshape(left_rank * 4, -1)
        u_matrix, singular_values, vh_matrix = np.linalg.svd(matrix, full_matrices=False)
        keep = min(max_bond_dimension, len(singular_values))
        discarded = singular_values[keep:]
        kept = singular_values[:keep]
        total_weight = float(np.sum(singular_values**2))
        discarded_weight = float(np.sum(discarded**2))
        diagnostics.append(
            {
                "cut_after_site": site,
                "full_rank": int(len(singular_values)),
                "kept_rank": int(keep),
                "discarded_weight": discarded_weight,
                "relative_discarded_weight": discarded_weight / total_weight if total_weight else 0.0,
                "largest_discarded_singular_value": float(discarded[0]) if len(discarded) else 0.0,
                "kept_singular_values": [float(value) for value in kept[: min(8, len(kept))]],
            }
        )
        mps.append(u_matrix[:, :keep].reshape(left_rank, 4, keep))
        current = kept[:, None] * vh_matrix[:keep, :]
        left_rank = keep
    mps.append(current.reshape(left_rank, 4, 1))
    return mps, diagnostics


def mps_reconstruct(mps: list[np.ndarray]) -> np.ndarray:
    state = mps[0][0, :, :]
    for tensor in mps[1:]:
        state = np.tensordot(state, tensor, axes=([-1], [0]))
    return np.squeeze(state, axis=-1)


def compressed_fixed_state(
    psi: np.ndarray,
    sites: int,
    n_up: int,
    n_down: int,
    max_bond_dimension: int,
) -> dict[str, Any]:
    full_tensor = fixed_vector_to_full_tensor(psi, sites, n_up, n_down)
    mps, cuts = mps_decompose(full_tensor, max_bond_dimension=max_bond_dimension)
    reconstructed_tensor = mps_reconstruct(mps)
    full_norm = float(np.linalg.norm(reconstructed_tensor.ravel()))
    fixed_vector = full_tensor_to_fixed_vector(reconstructed_tensor, sites, n_up, n_down)
    fixed_norm = float(np.linalg.norm(fixed_vector))
    if fixed_norm == 0.0:
        raise ValueError("MPS truncation projected to zero fixed-sector norm")
    fixed_vector = fixed_vector / fixed_norm
    overlap = abs(float(np.dot(psi, fixed_vector)))
    return {
        "state": fixed_vector,
        "mps_cut_diagnostics": cuts,
        "full_reconstructed_norm": full_norm,
        "fixed_sector_norm_before_normalization": fixed_norm,
        "fixed_sector_leakage": max(0.0, full_norm**2 - fixed_norm**2),
        "overlap_with_exact_ground_state": overlap,
        "max_kept_bond_dimension": max(cut["kept_rank"] for cut in cuts) if cuts else 1,
        "total_relative_discarded_weight": float(sum(cut["relative_discarded_weight"] for cut in cuts)),
        "max_relative_discarded_weight": float(max((cut["relative_discarded_weight"] for cut in cuts), default=0.0)),
    }


def solve_response_from_state(
    matrix: sparse.csr_matrix,
    psi: np.ndarray,
    exact_ground_energy: float,
    density: np.ndarray,
) -> dict[str, Any]:
    density_mean = float(np.dot(psi, density * psi))
    source = (density - density_mean) * psi
    source_norm = float(np.linalg.norm(source))
    if source_norm == 0.0:
        return {
            "density_mean": density_mean,
            "source_norm": 0.0,
            "susceptibility_proxy": 0.0,
            "relative_residual": 0.0,
            "solver_info": 0,
            "iterations": 0,
        }
    operator = matrix - exact_ground_energy * sparse.identity(matrix.shape[0], format="csr")
    operator = operator + ETA * sparse.identity(matrix.shape[0], format="csr")
    iterations = 0

    def count_iteration(_: np.ndarray) -> None:
        nonlocal iterations
        iterations += 1

    solution, info = spla.cg(
        operator,
        source,
        rtol=RTOL,
        atol=0.0,
        maxiter=5000,
        callback=count_iteration,
    )
    residual = float(np.linalg.norm(operator @ solution - source) / source_norm)
    susceptibility = float(np.dot(source, solution))
    return {
        "density_mean": density_mean,
        "source_norm": source_norm,
        "susceptibility_proxy": susceptibility,
        "relative_residual": residual,
        "solver_info": int(info),
        "iterations": iterations,
    }


def relative_error(candidate: float, target: float) -> float:
    return abs(candidate - target) / max(abs(target), 1e-12)


def build_rows(
    d5_source: dict[str, Any],
    non_oracle_source: dict[str, Any],
    bond_dimensions: tuple[int, ...],
) -> list[dict[str, Any]]:
    non_oracle_rows = {
        (int(row["sites"]), float(row["u_over_t"])): row
        for row in non_oracle_source.get("rows", [])
    }
    rows: list[dict[str, Any]] = []
    for d5_row in d5_source.get("rows", []):
        sites = int(d5_row["sites"])
        u_over_t = float(d5_row["u_over_t"])
        t_value = float(d5_row.get("t", 1.0))
        n_up = sites // 2
        n_down = sites // 2
        matrix = hubbard_hamiltonian(sites, n_up, n_down, u_over_t * t_value, t_value)
        ground_energy, exact_psi = lowest_eigenpair(matrix)
        density = local_density_diagonal(sites, n_up, n_down, sites // 2)
        exact_susceptibility = float(d5_row["susceptibility_proxy"])
        bond_rows = []
        for bond_dimension in bond_dimensions:
            compressed = compressed_fixed_state(
                exact_psi,
                sites,
                n_up,
                n_down,
                max_bond_dimension=bond_dimension,
            )
            psi_mps = compressed.pop("state")
            energy_expectation = float(np.dot(psi_mps, matrix @ psi_mps))
            energy_variance = float(np.dot(psi_mps, matrix @ (matrix @ psi_mps)) - energy_expectation**2)
            response = solve_response_from_state(matrix, psi_mps, ground_energy, density)
            susceptibility = float(response["susceptibility_proxy"])
            bond_rows.append(
                {
                    "bond_dimension": int(bond_dimension),
                    "energy_expectation": energy_expectation,
                    "energy_error_per_site": abs(energy_expectation - ground_energy) / sites,
                    "energy_variance": max(0.0, energy_variance),
                    "susceptibility_proxy": susceptibility,
                    "absolute_response_error": abs(susceptibility - exact_susceptibility),
                    "relative_response_error": relative_error(susceptibility, exact_susceptibility),
                    "response_relative_residual": float(response["relative_residual"]),
                    "response_iterations": int(response["iterations"]),
                    "response_solver_info": int(response["solver_info"]),
                    **compressed,
                }
            )

        selected = max(bond_rows, key=lambda row: int(row["bond_dimension"]))
        non_oracle_row = non_oracle_rows.get((sites, u_over_t), {})
        non_oracle_error = non_oracle_row.get("selected_relative_response_error")
        rows.append(
            {
                "model": "one_dimensional_fermi_hubbard_half_filled_density_response",
                "sites": sites,
                "u_over_t": u_over_t,
                "t": t_value,
                "eta": float(d5_row.get("eta", ETA)),
                "exact_d5_susceptibility_proxy": exact_susceptibility,
                "exact_d5_hilbert_dimension": int(d5_row["hilbert_dimension"]),
                "exact_ground_energy": ground_energy,
                "bond_dimensions_tested": list(bond_dimensions),
                "selected_bond_dimension": int(selected["bond_dimension"]),
                "selected_susceptibility_proxy": float(selected["susceptibility_proxy"]),
                "selected_relative_response_error": float(selected["relative_response_error"]),
                "selected_energy_error_per_site": float(selected["energy_error_per_site"]),
                "selected_overlap_with_exact_ground_state": float(selected["overlap_with_exact_ground_state"]),
                "selected_fixed_sector_norm_before_normalization": float(
                    selected["fixed_sector_norm_before_normalization"]
                ),
                "selected_response_relative_residual": float(selected["response_relative_residual"]),
                "non_oracle_embedding_relative_response_error": (
                    float(non_oracle_error) if non_oracle_error is not None else None
                ),
                "mps_reference_beats_non_oracle_embedding": (
                    bool(float(selected["relative_response_error"]) + 1e-9 < float(non_oracle_error))
                    if non_oracle_error is not None
                    else False
                ),
                "bond_dimension_rows": bond_rows,
                "exact_state_seeded": True,
                "variational_dmrg": False,
                "candidate_quantum_response_beats_mps_reference": False,
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]], bond_dimensions: tuple[int, ...]) -> dict[str, Any]:
    selected_errors = [float(row["selected_relative_response_error"]) for row in rows]
    selected_energy_errors = [float(row["selected_energy_error_per_site"]) for row in rows]
    overlaps = [float(row["selected_overlap_with_exact_ground_state"]) for row in rows]
    fixed_norms = [float(row["selected_fixed_sector_norm_before_normalization"]) for row in rows]
    return {
        "instance_count": len(rows),
        "site_values": sorted({row["sites"] for row in rows}),
        "u_over_t_values": sorted({row["u_over_t"] for row in rows}),
        "bond_dimensions_tested": list(bond_dimensions),
        "selected_bond_dimension": max(bond_dimensions),
        "selected_mean_relative_response_error": float(np.mean(selected_errors)),
        "selected_median_relative_response_error": float(np.median(selected_errors)),
        "selected_max_relative_response_error": float(np.max(selected_errors)),
        "selected_mean_energy_error_per_site": float(np.mean(selected_energy_errors)),
        "selected_max_energy_error_per_site": float(np.max(selected_energy_errors)),
        "selected_min_overlap_with_exact_ground_state": float(np.min(overlaps)),
        "selected_min_fixed_sector_norm_before_normalization": float(np.min(fixed_norms)),
        "mps_rows_beating_non_oracle_embedding": sum(
            bool(row["mps_reference_beats_non_oracle_embedding"]) for row in rows
        ),
        "max_exact_d5_hilbert_dimension": max(row["exact_d5_hilbert_dimension"] for row in rows),
        "max_full_local_basis_dimension": max(4 ** int(row["sites"]) for row in rows),
        "exact_state_seeded": True,
        "variational_dmrg": False,
        "quantum_response_win_claimed": False,
        "accuracy_per_resource_win_claimed": False,
    }


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain MPS truncation reference, not DMRG or advantage claim")
    if report.get("benchmark_id") != "B5":
        errors.append("benchmark_id must be B5")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    if report.get("explicit_not_quantum_advantage") is not True:
        errors.append("report must explicitly avoid quantum-advantage claims")
    if report.get("explicit_not_variational_dmrg") is not True:
        errors.append("report must disclose that this is not variational DMRG")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 9:
        errors.append("MPS truncation reference must cover the 9 D5 B5 rows")
    if summary.get("variational_dmrg") is not False:
        errors.append("summary must not imply variational DMRG")
    if summary.get("exact_state_seeded") is not True:
        errors.append("summary must disclose exact-state seeding")
    if summary.get("quantum_response_win_claimed") is not False:
        errors.append("quantum response win must not be claimed")
    if summary.get("accuracy_per_resource_win_claimed") is not False:
        errors.append("accuracy-per-resource win must not be claimed")
    if len(summary.get("bond_dimensions_tested", [])) < 3:
        errors.append("at least three MPS bond dimensions should be tested")
    for row in report.get("rows", []):
        label = f"sites={row.get('sites')} U/t={row.get('u_over_t')}"
        if row.get("exact_state_seeded") is not True:
            errors.append(f"{label} must disclose exact-state seeding")
        if row.get("variational_dmrg") is not False:
            errors.append(f"{label} must not claim DMRG")
        if row.get("candidate_quantum_response_beats_mps_reference") is not False:
            errors.append(f"{label} claims a quantum win")
        if not math.isfinite(float(row.get("selected_relative_response_error", math.inf))):
            errors.append(f"{label} has non-finite selected response error")
        if float(row.get("selected_response_relative_residual", 1.0)) > 1e-6:
            errors.append(f"{label} selected response residual too high")
        if len(row.get("bond_dimension_rows", [])) != len(summary.get("bond_dimensions_tested", [])):
            errors.append(f"{label} missing bond-dimension rows")
    return errors


def build_report(
    d5_source_path: Path,
    non_oracle_source_path: Path,
    bond_dimensions: tuple[int, ...],
) -> dict[str, Any]:
    started = time.perf_counter()
    d5_source = load_json(d5_source_path)
    non_oracle_source = load_json(non_oracle_source_path)
    rows = build_rows(d5_source, non_oracle_source, bond_dimensions)
    report = {
        "benchmark_id": "B5",
        "problem_id": 38,
        "title": "B5 MPS/Schmidt-truncation response reference for Hubbard D5 rows",
        "version": "0.1",
        "last_updated": "2026-06-18",
        "status": STATUS,
        "method": METHOD,
        "model_status": "exact_state_seeded_mps_truncation_tensor_pressure_reference",
        "dependency_b10_table": d5_source.get("method"),
        "dependency_b10_result": str(d5_source_path),
        "dependency_non_oracle_embedding_result": str(non_oracle_source_path),
        "explicit_not_quantum_advantage": True,
        "explicit_not_bqp_separation": True,
        "explicit_not_variational_dmrg": True,
        "exact_state_seeded": True,
        "summary": summarize(rows, bond_dimensions),
        "rows": rows,
        "runtime_seconds": time.perf_counter() - started,
        "claim_boundary": {
            "now_supported": (
                "A tensor-network pressure reference now measures how finite MPS bond dimension distorts "
                "the same B10 D5 Hubbard response rows after projecting back to the fixed particle-number sector."
            ),
            "still_not_supported": (
                "This is exact-state-seeded Schmidt truncation, not variational DMRG, not a deployable tensor solver, "
                "not a quantum response kernel, and not an accuracy-per-resource win."
            ),
            "next_gate": (
                "Replace the exact-state-seeded MPS pressure reference with a variational DMRG/MPS solver "
                "or compare a real quantum response kernel against this reference after full cost accounting."
            ),
        },
    }
    report["validation_errors"] = validate(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# B5 MPS/Schmidt-Truncation Response Reference v0.1",
        "",
        f"Last updated: {report['last_updated']}",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{report['method']}`",
        f"- Dependency B10 table: `{report['dependency_b10_table']}`",
        f"- Dependency non-oracle embedding denominator: `{report['dependency_non_oracle_embedding_result']}`",
        f"- Instances: {summary['instance_count']}",
        f"- Sites: {summary['site_values']}",
        f"- U/t values: {summary['u_over_t_values']}",
        f"- Bond dimensions tested: {summary['bond_dimensions_tested']}",
        f"- Selected bond dimension: {summary['selected_bond_dimension']}",
        f"- Selected mean / median / max relative response error: {summary['selected_mean_relative_response_error']:.6g} / {summary['selected_median_relative_response_error']:.6g} / {summary['selected_max_relative_response_error']:.6g}",
        f"- Selected mean / max energy error per site: {summary['selected_mean_energy_error_per_site']:.6g} / {summary['selected_max_energy_error_per_site']:.6g}",
        f"- Min selected overlap with exact ground state: {summary['selected_min_overlap_with_exact_ground_state']:.6g}",
        f"- Min selected fixed-sector norm before normalization: {summary['selected_min_fixed_sector_norm_before_normalization']:.6g}",
        f"- Rows beating non-oracle embedding denominator: {summary['mps_rows_beating_non_oracle_embedding']}",
        f"- Exact-state seeded: {summary['exact_state_seeded']}",
        f"- Variational DMRG: {summary['variational_dmrg']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Interpretation",
        "",
        "- This is a tensor-network pressure reference for B5/T-B5-003, not a completed DMRG baseline.",
        "- It compresses the exact Hubbard ground state into an MPS by sequential Schmidt truncation, reconstructs it, projects back to the fixed particle-number sector, and evaluates the same shifted D5 response.",
        "- Because the MPS is seeded by the exact state, it measures bond-dimension sensitivity rather than deployable variational optimization.",
        "- A future B5 denominator still needs a variational DMRG/MPS solver or a costed quantum response-kernel comparison.",
        "",
        "## Rows",
        "",
        "| Sites | U/t | Bond dim | Exact D5 chi | MPS chi | Rel. response error | Energy error/site | Overlap | Fixed-sector norm |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {sites} | {u:.1f} | {bond} | {exact:.8g} | {mps:.8g} | {rel:.6g} | {energy:.6g} | {overlap:.6g} | {norm:.6g} |".format(
                sites=row["sites"],
                u=row["u_over_t"],
                bond=row["selected_bond_dimension"],
                exact=row["exact_d5_susceptibility_proxy"],
                mps=row["selected_susceptibility_proxy"],
                rel=row["selected_relative_response_error"],
                energy=row["selected_energy_error_per_site"],
                overlap=row["selected_overlap_with_exact_ground_state"],
                norm=row["selected_fixed_sector_norm_before_normalization"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Now supported: {report['claim_boundary']['now_supported']}",
            f"- Still not supported: {report['claim_boundary']['still_not_supported']}",
            f"- Next gate: {report['claim_boundary']['next_gate']}",
        ]
    )
    if report["validation_errors"]:
        lines.extend(["", "## Validation Errors", ""])
        lines.extend(f"- {error}" for error in report["validation_errors"])
    return "\n".join(lines) + "\n"


def parse_int_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d5-source", type=Path, default=Path("results/B10_t1_d5_observable_denominator_table_v0.json"))
    parser.add_argument(
        "--non-oracle-source",
        type=Path,
        default=Path("results/B5_non_oracle_response_embedding_baseline_v0.json"),
    )
    parser.add_argument("--bond-dimensions", default=",".join(str(item) for item in DEFAULT_BOND_DIMS))
    parser.add_argument("--json-output", type=Path, default=Path("results/B5_mps_truncation_response_reference_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B5_mps_truncation_response_reference.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(
        d5_source_path=args.d5_source,
        non_oracle_source_path=args.non_oracle_source,
        bond_dimensions=parse_int_tuple(args.bond_dimensions),
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if not report["validation_errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
