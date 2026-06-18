#!/usr/bin/env python3
"""Build a Hamiltonian-derived B3 reaction-observable denominator table for B10-T1 D5."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
from pyscf import ao2mo, gto, scf
from scipy import sparse
from scipy.sparse import linalg as spla


RTOL = 1e-10
DELTA_ANGSTROM = 0.01
ETA = 0.05
BITS_PER_OBSERVABLE = 53


def atoms_h2(r: float) -> str:
    return f"H 0 0 0; H 0 0 {r}"


def atoms_lih(r: float) -> str:
    return f"Li 0 0 0; H 0 0 {r}"


def atoms_n2(r: float) -> str:
    return f"N 0 0 0; N 0 0 {r}"


def atoms_h2o(scale: float) -> str:
    return f"O 0 0 0; H 0 {0.757 * scale} {0.587 * scale}; H 0 {-0.757 * scale} {0.587 * scale}"


REACTION_COORDINATES: list[dict[str, Any]] = [
    {
        "molecule": "h2_bond_stretch",
        "basis": "sto-3g",
        "charge": 0,
        "spin": 0,
        "coordinate": "H-H bond length",
        "center": 0.7414,
        "atom_builder": atoms_h2,
    },
    {
        "molecule": "lih_bond_stretch",
        "basis": "sto-3g",
        "charge": 0,
        "spin": 0,
        "coordinate": "Li-H bond length",
        "center": 1.6,
        "atom_builder": atoms_lih,
    },
    {
        "molecule": "h2o_symmetric_oh_stretch",
        "basis": "sto-3g",
        "charge": 0,
        "spin": 0,
        "coordinate": "symmetric O-H stretch scale",
        "center": 1.0,
        "atom_builder": atoms_h2o,
    },
    {
        "molecule": "n2_bond_stretch",
        "basis": "sto-3g",
        "charge": 0,
        "spin": 0,
        "coordinate": "N-N bond length",
        "center": 1.0977,
        "atom_builder": atoms_n2,
    },
]


def build_mol(atom: str, basis: str, charge: int, spin: int) -> gto.Mole:
    mol = gto.Mole()
    mol.atom = atom
    mol.unit = "Angstrom"
    mol.basis = basis
    mol.charge = charge
    mol.spin = spin
    mol.verbose = 0
    mol.build()
    return mol


def run_rhf(mol: gto.Mole) -> scf.hf.RHF:
    mf = scf.RHF(mol)
    mf.conv_tol = 1e-11
    mf.kernel()
    if not mf.converged:
        raise RuntimeError("RHF did not converge")
    return mf


def finite_difference_hcore(
    builder: Callable[[float], str],
    center: float,
    delta: float,
    basis: str,
    charge: int,
    spin: int,
) -> tuple[np.ndarray, float, float]:
    plus = build_mol(builder(center + delta), basis, charge, spin)
    minus = build_mol(builder(center - delta), basis, charge, spin)
    mf_plus = run_rhf(plus)
    mf_minus = run_rhf(minus)
    derivative = (mf_plus.get_hcore() - mf_minus.get_hcore()) / (2.0 * delta)
    energy_derivative = (float(mf_plus.e_tot) - float(mf_minus.e_tot)) / (2.0 * delta)
    return derivative, energy_derivative, float(mf_plus.e_tot - mf_minus.e_tot)


def singles_response_matrix(mol: gto.Mole, mf: scf.hf.RHF) -> tuple[sparse.csr_matrix, list[tuple[int, int]], dict[str, float]]:
    mo_coeff = mf.mo_coeff
    mo_energy = mf.mo_energy
    nmo = mo_coeff.shape[1]
    nocc = mol.nelectron // 2
    singles = [(i, a) for i in range(nocc) for a in range(nocc, nmo)]
    dim = len(singles)
    if dim == 0:
        raise ValueError("no occupied-virtual singles available")
    eri_packed = ao2mo.kernel(mol, mo_coeff)
    eri = ao2mo.restore(1, eri_packed, nmo)
    dense = np.zeros((dim, dim), dtype=np.float64)
    for p, (i, a) in enumerate(singles):
        dense[p, p] = max(ETA, float(mo_energy[a] - mo_energy[i] + ETA))
        for q, (j, b) in enumerate(singles):
            coupling = 0.5 * (eri[a, i, j, b] + eri[b, j, i, a])
            dense[p, q] += 0.05 * coupling
    dense = 0.5 * (dense + dense.T)
    min_eval = float(np.linalg.eigvalsh(dense)[0])
    stabilizer = 0.0
    if min_eval <= 1e-8:
        stabilizer = abs(min_eval) + 1e-6
        dense += stabilizer * np.eye(dim)
    stats = {
        "min_eigenvalue_after_shift": float(np.linalg.eigvalsh(dense)[0]),
        "stabilizer_shift": stabilizer,
        "nocc": float(nocc),
        "nvir": float(nmo - nocc),
    }
    return sparse.csr_matrix(dense), singles, stats


def source_from_hcore_derivative(mf: scf.hf.RHF, hcore_derivative: np.ndarray, singles: list[tuple[int, int]]) -> np.ndarray:
    h_mo = mf.mo_coeff.T @ hcore_derivative @ mf.mo_coeff
    source = np.asarray([h_mo[a, i] for i, a in singles], dtype=np.float64)
    norm = np.linalg.norm(source)
    if norm == 0.0:
        raise ValueError("Hamiltonian-derived response source has zero norm")
    return source


def run_coordinate(config: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    builder = config["atom_builder"]
    center = float(config["center"])
    basis = config["basis"]
    charge = int(config["charge"])
    spin = int(config["spin"])
    mol = build_mol(builder(center), basis, charge, spin)
    mf = run_rhf(mol)
    h_derivative, energy_derivative, energy_difference = finite_difference_hcore(
        builder, center, DELTA_ANGSTROM, basis, charge, spin
    )
    response_matrix, singles, matrix_stats = singles_response_matrix(mol, mf)
    source = source_from_hcore_derivative(mf, h_derivative, singles)
    source_norm = float(np.linalg.norm(source))
    iterations = 0

    def count_iteration(_: np.ndarray) -> None:
        nonlocal iterations
        iterations += 1

    solution, info = spla.cg(response_matrix, source, rtol=RTOL, atol=0.0, maxiter=1000, callback=count_iteration)
    residual = float(np.linalg.norm(response_matrix @ solution - source) / source_norm)
    observable_response = float(np.dot(source, solution))
    hcore_nnz = int(np.count_nonzero(np.abs(mf.get_hcore()) > 1e-12))
    eri_nnz_proxy = int(np.count_nonzero(np.abs(mol.intor("int2e")) > 1e-12))
    explicit_input_entries = int(hcore_nnz + eri_nnz_proxy + response_matrix.nnz + len(source))
    return {
        "family": "D5_b3_b5_observable_linear_response",
        "source_benchmark": "B3",
        "model": "hamiltonian_derived_reaction_coordinate_observable_response",
        "molecule": config["molecule"],
        "basis": basis,
        "coordinate": config["coordinate"],
        "coordinate_center": center,
        "finite_difference_delta": DELTA_ANGSTROM,
        "hf_energy_hartree": float(mf.e_tot),
        "finite_difference_energy_derivative": energy_derivative,
        "finite_difference_energy_delta": energy_difference,
        "electrons": int(mol.nelectron),
        "spatial_orbitals": int(mf.mo_coeff.shape[1]),
        "occupied_orbitals": int(matrix_stats["nocc"]),
        "virtual_orbitals": int(matrix_stats["nvir"]),
        "response_dimension": int(response_matrix.shape[0]),
        "response_nnz": int(response_matrix.nnz),
        "response_min_eigenvalue": matrix_stats["min_eigenvalue_after_shift"],
        "response_stabilizer_shift": matrix_stats["stabilizer_shift"],
        "source_norm": source_norm,
        "observable_response_proxy": observable_response,
        "rtol": RTOL,
        "solver": "cg_singles_response",
        "iterations": iterations,
        "solver_info": int(info),
        "relative_residual": residual,
        "wall_time_seconds": time.perf_counter() - started,
        "matvec_equivalent_ops": int(iterations * response_matrix.nnz),
        "explicit_input_entries": explicit_input_entries,
        "observable_output_bits": BITS_PER_OBSERVABLE,
        "explicit_io_floor_units": int(explicit_input_entries + BITS_PER_OBSERVABLE),
        "boundary_interpretation": (
            "This row replaces the B3 proxy matrix with a Hamiltonian-derived finite-difference "
            "reaction-coordinate source and a singles response denominator. It is a denominator "
            "for observable claims, not a quantum chemistry accuracy result."
        ),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "family_count": len({row["family"] for row in rows}),
        "source_benchmark_count": len({row["source_benchmark"] for row in rows}),
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "molecules": [row["molecule"] for row in rows],
        "max_response_dimension": max(row["response_dimension"] for row in rows),
        "max_response_nnz": max(row["response_nnz"] for row in rows),
        "max_relative_residual": max(row["relative_residual"] for row in rows),
        "median_iterations": float(np.median([row["iterations"] for row in rows])),
        "max_explicit_io_floor_units": max(row["explicit_io_floor_units"] for row in rows),
        "max_matvec_equivalent_ops": max(row["matvec_equivalent_ops"] for row in rows),
    }


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "hamiltonian_derived_b3_reaction_observable_denominator_not_reaction_solution":
        errors.append("status must remain a Hamiltonian-derived denominator, not a reaction solution")
    if report.get("source_target_id") != "B10-T1":
        errors.append("source_target_id must be B10-T1")
    if report.get("dependency_benchmark") != "B3":
        errors.append("reaction observable table must declare dependency_benchmark=B3")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("must explicitly avoid BQP/classical separation claims")
    summary = report.get("summary", {})
    if summary.get("instance_count", 0) < 4:
        errors.append("Hamiltonian-derived table should cover at least four reaction-coordinate instances")
    if summary.get("max_response_dimension", 0) < 10:
        errors.append("Hamiltonian-derived table should include a nontrivial response dimension")
    if summary.get("max_relative_residual", 1.0) > 1e-8:
        errors.append("maximum relative residual is too high for the Hamiltonian-derived table")
    for row in report.get("rows", []):
        if row.get("solver_info") != 0:
            errors.append(f"{row.get('molecule')} solver_info={row.get('solver_info')}")
        if row.get("iterations", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no CG iterations")
        if row.get("source_norm", 0.0) <= 0.0:
            errors.append(f"{row.get('molecule')} has zero source norm")
        if row.get("observable_output_bits") != BITS_PER_OBSERVABLE:
            errors.append(f"{row.get('molecule')} has wrong observable bit accounting")
    return errors


def build_report() -> dict[str, Any]:
    rows = [run_coordinate(config) for config in REACTION_COORDINATES]
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T1 Hamiltonian-derived B3 reaction-observable denominator table",
        "version": "0.6",
        "last_updated": "2026-06-13",
        "status": "hamiltonian_derived_b3_reaction_observable_denominator_not_reaction_solution",
        "method": "b10_t1_d5_b3_reaction_observable_table_v0",
        "source_target_id": "B10-T1",
        "source_target_name": "linear_systems_data_loading_negative_boundary",
        "dependency_benchmark": "B3",
        "builds_on": "b10_t1_d5_b3_molecular_observable_table_v0",
        "explicit_not_bqp_separation": True,
        "summary": summarize(rows),
        "rows": rows,
        "claim_boundary": {
            "now_supported": (
                "B10-T1 D5 now has Hamiltonian-derived B3 reaction-coordinate denominator rows "
                "using PySCF finite-difference one-electron Hamiltonians and singles response equations."
            ),
            "still_not_supported": (
                "This is not a full reaction-dynamics simulation, not a quantum implementation, "
                "not a chemistry accuracy claim, and not a BQP/classical separation."
            ),
            "next_proof_pressure": (
                "Add correlated classical references such as MP2/CCSD or selected-CI along the coordinate, "
                "then compare a concrete quantum observable-estimation circuit against this denominator."
            ),
        },
    }
    report["validation_errors"] = validate(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# B10-T1 Hamiltonian-Derived B3 Reaction Observable Denominator Table v0.6",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']} / {report['source_target_name']}",
        f"- Dependency benchmark: {report['dependency_benchmark']}",
        f"- Builds on: {report['builds_on']}",
        f"- Instances: {summary['instance_count']}",
        f"- Molecules: {summary['molecules']}",
        f"- Max response dimension: {summary['max_response_dimension']}",
        f"- Max response nnz: {summary['max_response_nnz']}",
        f"- Max relative residual: {summary['max_relative_residual']:.3e}",
        f"- Median CG iterations: {summary['median_iterations']:.1f}",
        f"- Validation errors: {len(report['validation_errors'])}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        "",
        "## Interpretation",
        "",
        "- This table replaces the previous B3 proxy response matrix with Hamiltonian-derived finite-difference sources.",
        "- Each row uses a reaction-coordinate perturbation, central RHF molecular orbitals, and a singles response denominator.",
        "- It remains a denominator and claim-boundary artifact, not a reaction-dynamics solution or quantum-speedup result.",
        "",
        "## Instance Table",
        "",
        "| molecule | coordinate | response dim | nnz | source norm | response proxy | iterations | residual | explicit-I/O floor |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {mol} | {coord} | {dim} | {nnz} | {src:.3e} | {obs:.6e} | {it} | {res:.3e} | {floor} |".format(
                mol=row["molecule"],
                coord=row["coordinate"],
                dim=row["response_dimension"],
                nnz=row["response_nnz"],
                src=row["source_norm"],
                obs=row["observable_response_proxy"],
                it=row["iterations"],
                res=row["relative_residual"],
                floor=row["explicit_io_floor_units"],
            )
        )
    lines.extend(["", "## Claim Boundary", ""])
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t1_d5_b3_reaction_observable_table_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t1_d5_b3_reaction_observable_table.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "instance_count": report["summary"]["instance_count"],
                    "max_response_dimension": report["summary"]["max_response_dimension"],
                    "max_relative_residual": report["summary"]["max_relative_residual"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
