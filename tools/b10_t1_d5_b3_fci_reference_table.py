#!/usr/bin/env python3
"""Build FCI-strength B3 references for the B10-T1 D5 reaction-coordinate table."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
from pyscf import cc, fci, gto, mp, scf


DELTA_ANGSTROM = 0.01
METHODS = ["RHF", "MP2", "CCSD", "FCI"]


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


def run_methods(atom: str, basis: str, charge: int, spin: int) -> dict[str, Any]:
    mol = build_mol(atom, basis, charge, spin)
    mf = scf.RHF(mol)
    mf.conv_tol = 1e-11
    mf.kernel()
    if not mf.converged:
        raise RuntimeError("RHF did not converge")

    mp2 = mp.MP2(mf)
    mp2.verbose = 0
    mp2.kernel()

    ccsd = cc.CCSD(mf)
    ccsd.verbose = 0
    ccsd.conv_tol = 1e-9
    ccsd.kernel()
    if not ccsd.converged:
        raise RuntimeError("CCSD did not converge")

    cisolver = fci.FCI(mf)
    cisolver.max_cycle = 100
    fci_energy, _ = cisolver.kernel()

    return {
        "RHF": float(mf.e_tot),
        "MP2": float(mp2.e_tot),
        "CCSD": float(ccsd.e_tot),
        "FCI": float(fci_energy),
        "electrons": int(mol.nelectron),
        "spatial_orbitals": int(mf.mo_coeff.shape[1]),
    }


def run_coordinate(config: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    builder: Callable[[float], str] = config["atom_builder"]
    center = float(config["center"])
    basis = config["basis"]
    charge = int(config["charge"])
    spin = int(config["spin"])

    center_result = run_methods(builder(center), basis, charge, spin)
    plus_result = run_methods(builder(center + DELTA_ANGSTROM), basis, charge, spin)
    minus_result = run_methods(builder(center - DELTA_ANGSTROM), basis, charge, spin)

    methods = {}
    for method in METHODS:
        center_energy = center_result[method]
        plus_energy = plus_result[method]
        minus_energy = minus_result[method]
        derivative = (plus_energy - minus_energy) / (2.0 * DELTA_ANGSTROM)
        methods[method] = {
            "center_energy_hartree": center_energy,
            "plus_energy_hartree": plus_energy,
            "minus_energy_hartree": minus_energy,
            "finite_difference_derivative_hartree_per_coordinate": derivative,
            "correlation_energy_vs_rhf_hartree": center_energy - center_result["RHF"],
            "energy_gap_vs_fci_hartree": center_energy - center_result["FCI"],
        }

    return {
        "source_benchmark": "B3",
        "molecule": config["molecule"],
        "basis": basis,
        "coordinate": config["coordinate"],
        "coordinate_center": center,
        "finite_difference_delta": DELTA_ANGSTROM,
        "electrons": center_result["electrons"],
        "spatial_orbitals": center_result["spatial_orbitals"],
        "methods": methods,
        "mp2_derivative_shift_vs_rhf": methods["MP2"]["finite_difference_derivative_hartree_per_coordinate"]
        - methods["RHF"]["finite_difference_derivative_hartree_per_coordinate"],
        "ccsd_derivative_shift_vs_rhf": methods["CCSD"]["finite_difference_derivative_hartree_per_coordinate"]
        - methods["RHF"]["finite_difference_derivative_hartree_per_coordinate"],
        "fci_derivative_shift_vs_rhf": methods["FCI"]["finite_difference_derivative_hartree_per_coordinate"]
        - methods["RHF"]["finite_difference_derivative_hartree_per_coordinate"],
        "fci_derivative_shift_vs_ccsd": methods["FCI"]["finite_difference_derivative_hartree_per_coordinate"]
        - methods["CCSD"]["finite_difference_derivative_hartree_per_coordinate"],
        "wall_time_seconds": time.perf_counter() - started,
        "boundary_interpretation": (
            "This row upgrades the B3 reaction-coordinate denominator to an FCI-strength "
            "small-basis classical reference. Future quantum observable-estimation claims "
            "must state whether they beat HF-only, MP2, CCSD, or FCI references at the "
            "same coordinate and basis."
        ),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "methods": METHODS,
        "max_abs_fci_derivative_shift_vs_rhf": max(abs(row["fci_derivative_shift_vs_rhf"]) for row in rows),
        "max_abs_fci_derivative_shift_vs_ccsd": max(abs(row["fci_derivative_shift_vs_ccsd"]) for row in rows),
        "max_abs_ccsd_derivative_shift_vs_rhf": max(abs(row["ccsd_derivative_shift_vs_rhf"]) for row in rows),
        "total_wall_time_seconds": float(sum(row["wall_time_seconds"] for row in rows)),
    }


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "fci_b3_reaction_references_instantiated_not_quantum_advantage_claim":
        errors.append("status must remain FCI references, not quantum advantage")
    if report.get("source_target_id") != "B10-T1":
        errors.append("source_target_id must be B10-T1")
    if report.get("dependency_benchmark") != "B3":
        errors.append("FCI reference table must declare dependency_benchmark=B3")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("must explicitly avoid BQP/classical separation claims")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("FCI reference table should cover four reaction-coordinate rows")
    if summary.get("methods") != METHODS:
        errors.append("FCI reference table must include RHF, MP2, CCSD, and FCI")
    if summary.get("max_abs_fci_derivative_shift_vs_rhf", 0.0) <= 0.0:
        errors.append("FCI derivative shifts should be nonzero against RHF")
    for row in report.get("rows", []):
        for method in METHODS:
            if method not in row.get("methods", {}):
                errors.append(f"{row.get('molecule')} missing {method}")
            elif not np.isfinite(row["methods"][method]["center_energy_hartree"]):
                errors.append(f"{row.get('molecule')} {method} center energy is not finite")
    return errors


def build_report() -> dict[str, Any]:
    rows = [run_coordinate(config) for config in REACTION_COORDINATES]
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T1 FCI-strength B3 reaction-coordinate references",
        "version": "0.8",
        "last_updated": "2026-06-15",
        "status": "fci_b3_reaction_references_instantiated_not_quantum_advantage_claim",
        "method": "b10_t1_d5_b3_fci_reference_table_v0",
        "source_target_id": "B10-T1",
        "source_target_name": "linear_systems_data_loading_negative_boundary",
        "dependency_benchmark": "B3",
        "builds_on": "b10_t1_d5_b3_correlated_reference_table_v0",
        "explicit_not_bqp_separation": True,
        "summary": summarize(rows),
        "rows": rows,
        "claim_boundary": {
            "now_supported": (
                "B3 D5 reaction-coordinate denominator rows now have RHF, MP2, CCSD, "
                "and FCI finite-difference reference derivatives in STO-3G."
            ),
            "still_not_supported": (
                "This is not a quantum implementation, not a full reaction-dynamics solution, "
                "not a basis-set-complete chemistry claim, and not a BQP/classical separation."
            ),
            "next_proof_pressure": (
                "Compare a concrete quantum observable-estimation circuit against the FCI "
                "reference denominator, then scale to an active-space or selected-CI setting."
            ),
        },
    }
    report["validation_errors"] = validate(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# B10-T1 FCI-Strength B3 Reaction-Coordinate References v0.8",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']} / {report['source_target_name']}",
        f"- Dependency benchmark: {report['dependency_benchmark']}",
        f"- Builds on: {report['builds_on']}",
        f"- Instances: {summary['instance_count']}",
        f"- Methods: {summary['methods']}",
        f"- Max |FCI derivative shift vs RHF|: {summary['max_abs_fci_derivative_shift_vs_rhf']:.3e}",
        f"- Max |FCI derivative shift vs CCSD|: {summary['max_abs_fci_derivative_shift_vs_ccsd']:.3e}",
        f"- Max |CCSD derivative shift vs RHF|: {summary['max_abs_ccsd_derivative_shift_vs_rhf']:.3e}",
        f"- Validation errors: {len(report['validation_errors'])}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        "",
        "## Interpretation",
        "",
        "- This table upgrades the B3 reaction-coordinate denominator to include FCI in the same small-basis settings.",
        "- It records RHF, MP2, CCSD, and FCI finite-difference energy derivatives on the same coordinates used by the Hamiltonian-derived D5 table.",
        "- It remains a classical reference and claim-boundary artifact, not a quantum advantage result.",
        "",
        "## Instance Table",
        "",
        "| molecule | coordinate | RHF dE/dq | MP2 dE/dq | CCSD dE/dq | FCI dE/dq | FCI-RHF shift | FCI-CCSD shift |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        m = row["methods"]
        lines.append(
            "| {molecule} | {coordinate} | {rhf:.6e} | {mp2:.6e} | {ccsd:.6e} | {fci:.6e} | {fci_rhf:.6e} | {fci_ccsd:.6e} |".format(
                molecule=row["molecule"],
                coordinate=row["coordinate"],
                rhf=m["RHF"]["finite_difference_derivative_hartree_per_coordinate"],
                mp2=m["MP2"]["finite_difference_derivative_hartree_per_coordinate"],
                ccsd=m["CCSD"]["finite_difference_derivative_hartree_per_coordinate"],
                fci=m["FCI"]["finite_difference_derivative_hartree_per_coordinate"],
                fci_rhf=row["fci_derivative_shift_vs_rhf"],
                fci_ccsd=row["fci_derivative_shift_vs_ccsd"],
            )
        )
    boundary = report["claim_boundary"]
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- now_supported: {boundary['now_supported']}",
            f"- still_not_supported: {boundary['still_not_supported']}",
            f"- next_proof_pressure: {boundary['next_proof_pressure']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", default="results/B10_t1_d5_b3_fci_reference_table_v0.json")
    parser.add_argument("--markdown-output", default="research/B10_t1_d5_b3_fci_reference_table.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report()
    Path(args.json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.markdown_output).write_text(markdown(report) + "\n", encoding="utf-8")

    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "instance_count": report["summary"]["instance_count"],
                    "methods": report["summary"]["methods"],
                    "max_abs_fci_derivative_shift_vs_rhf": report["summary"][
                        "max_abs_fci_derivative_shift_vs_rhf"
                    ],
                    "max_abs_fci_derivative_shift_vs_ccsd": report["summary"][
                        "max_abs_fci_derivative_shift_vs_ccsd"
                    ],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0 if not report["validation_errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
