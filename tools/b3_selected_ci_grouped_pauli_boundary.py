#!/usr/bin/env python3
"""Compare B3 sampled Pauli estimates against larger-basis selected-CI denominators."""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib-codex")
os.environ.setdefault("XDG_CACHE_HOME", "/private/tmp/codex-cache")

from pyscf import ao2mo, gto, scf
from pyscf.fci import selected_ci

from b3_hamiltonian_pauli_mapper_comparison import ATOM_BUILDERS, mapped_pauli_terms
from b3_sampled_pauli_estimator_confidence import (
    allocate_target_shots,
    hf_pauli_expectation,
    target_error_for_derivative,
)


STATUS = "selected_ci_larger_basis_grouped_pauli_boundary_not_advantage_claim"
METHOD = "b3_selected_ci_grouped_pauli_boundary_v0"
ANZATZ_LAYERS = 2

BASIS_PLAN = {
    "h2_bond_stretch": {
        "selected_ci_basis": "cc-pvdz",
        "select_cutoff": 0.01,
        "ci_coeff_cutoff": 0.01,
        "max_cycle": 20,
    },
    "lih_bond_stretch": {
        "selected_ci_basis": "cc-pvdz",
        "select_cutoff": 0.02,
        "ci_coeff_cutoff": 0.02,
        "max_cycle": 20,
    },
    "h2o_symmetric_oh_stretch": {
        "selected_ci_basis": "3-21g",
        "select_cutoff": 0.05,
        "ci_coeff_cutoff": 0.05,
        "max_cycle": 20,
    },
    "n2_bond_stretch": {
        "selected_ci_basis": "3-21g",
        "select_cutoff": 0.05,
        "ci_coeff_cutoff": 0.05,
        "max_cycle": 20,
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def qwc_compatible(left: str, right: str) -> bool:
    return all(a == "I" or b == "I" or a == b for a, b in zip(left, right))


def greedy_qwc_groups(terms: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    for term in sorted(terms, key=lambda item: (-abs(float(item["coefficient"])), item["pauli"])):
        for group in groups:
            if all(qwc_compatible(str(term["pauli"]), str(existing["pauli"])) for existing in group):
                group.append(term)
                break
        else:
            groups.append([term])
    return groups


def selected_ci_energy(molecule: str, coordinate: float, basis: str, settings: dict[str, Any]) -> dict[str, Any]:
    atom = ATOM_BUILDERS[molecule](float(coordinate))
    started = time.perf_counter()
    mol = gto.M(atom=atom, basis=basis, unit="Angstrom", verbose=0)
    mf = scf.RHF(mol).run()
    mo_coeff = mf.mo_coeff
    norb = int(mo_coeff.shape[1])
    h1e = mo_coeff.T @ mf.get_hcore() @ mo_coeff
    eri = ao2mo.kernel(mol, mo_coeff)
    solver = selected_ci.SelectedCI(mol)
    solver.max_cycle = int(settings["max_cycle"])
    solver.select_cutoff = float(settings["select_cutoff"])
    solver.ci_coeff_cutoff = float(settings["ci_coeff_cutoff"])
    solver.conv_tol = 1.0e-6
    solver.max_space = 8
    energy, ci_vector = solver.kernel(h1e, eri, norb, mol.nelec, ecore=mol.energy_nuc())
    alpha_strings = len(ci_vector._strs[0])
    beta_strings = len(ci_vector._strs[1])
    return {
        "basis": basis,
        "coordinate_value": coordinate,
        "spatial_orbitals": norb,
        "spin_orbital_qubits": 2 * norb,
        "electrons": int(sum(mol.nelec)),
        "num_alpha_particles": int(mol.nelec[0]),
        "num_beta_particles": int(mol.nelec[1]),
        "rhf_energy_hartree": float(mf.e_tot),
        "selected_ci_energy_hartree": float(energy),
        "correlation_energy_vs_rhf_hartree": float(energy - mf.e_tot),
        "selected_alpha_strings": alpha_strings,
        "selected_beta_strings": beta_strings,
        "selected_determinant_product": int(alpha_strings * beta_strings),
        "select_cutoff": float(settings["select_cutoff"]),
        "ci_coeff_cutoff": float(settings["ci_coeff_cutoff"]),
        "max_cycle": int(settings["max_cycle"]),
        "converged": bool(getattr(solver, "converged", False)),
        "wall_time_seconds": time.perf_counter() - started,
    }


def grouped_pauli_metrics(
    molecule: str,
    coordinate_center: float,
    basis: str,
    electrons: int,
    fci_derivative: float,
) -> dict[str, Any]:
    qubits, _particles, raw_terms = mapped_pauli_terms(
        molecule=molecule,
        coordinate_center=coordinate_center,
        basis=basis,
    )
    occupied = min(int(electrons), qubits)
    random_terms = []
    for term in raw_terms:
        expectation = hf_pauli_expectation(str(term["pauli"]), occupied)
        variance = 1.0 - expectation * expectation
        if variance > 0.0:
            random_terms.append({**term, "hf_expectation": expectation, "term_variance": variance})
    target_error = target_error_for_derivative(fci_derivative)
    target_shots, _allocations = allocate_target_shots(random_terms, target_error)
    groups = greedy_qwc_groups(random_terms)
    ansatz_two_qubit_gates_per_shot = max(0, 2 * (qubits - 1) * ANZATZ_LAYERS)
    ansatz_single_qubit_rotations_per_shot = 2 * qubits * ANZATZ_LAYERS
    return {
        "source_hamiltonian_basis": basis,
        "source_hamiltonian_qubits": qubits,
        "random_pauli_terms": len(random_terms),
        "qwc_group_count": len(groups),
        "max_group_size": max((len(group) for group in groups), default=0),
        "packet_reduction_vs_ungrouped": (len(random_terms) / len(groups)) if groups else math.inf,
        "target_total_shot_floor_neyman": target_shots,
        "ansatz_model": "two-layer nearest-neighbor hardware-efficient preparation surcharge",
        "ansatz_layers": ANZATZ_LAYERS,
        "ansatz_two_qubit_gates_per_shot": ansatz_two_qubit_gates_per_shot,
        "ansatz_single_qubit_rotations_per_shot": ansatz_single_qubit_rotations_per_shot,
        "ansatz_two_qubit_gate_executions_at_target": target_shots * ansatz_two_qubit_gates_per_shot,
        "measurement_setting_preview": [
            [term["pauli"] for term in group[:5]]
            for group in sorted(groups, key=len, reverse=True)[:5]
        ],
    }


def build_report(
    fci_path: Path,
    sampled_path: Path,
    mapper_path: Path,
) -> dict[str, Any]:
    fci = load_json(fci_path)
    sampled = load_json(sampled_path)
    mapper = load_json(mapper_path)
    sampled_by_name = {row["molecule"]: row for row in sampled.get("rows", [])}
    mapper_by_name = {row["molecule"]: row for row in mapper.get("rows", [])}
    rows = []
    for fci_row in fci.get("rows", []):
        molecule = fci_row["molecule"]
        settings = BASIS_PLAN[molecule]
        basis = settings["selected_ci_basis"]
        delta = float(fci_row["finite_difference_delta"])
        center = float(fci_row["coordinate_center"])
        minus = selected_ci_energy(molecule, center - delta, basis, settings)
        center_energy = selected_ci_energy(molecule, center, basis, settings)
        plus = selected_ci_energy(molecule, center + delta, basis, settings)
        derivative = (plus["selected_ci_energy_hartree"] - minus["selected_ci_energy_hartree"]) / (2.0 * delta)
        determinant_points = [
            minus["selected_determinant_product"],
            center_energy["selected_determinant_product"],
            plus["selected_determinant_product"],
        ]
        grouped = grouped_pauli_metrics(
            molecule=molecule,
            coordinate_center=center,
            basis=str(fci_row["basis"]),
            electrons=int(fci_row["electrons"]),
            fci_derivative=float(fci_row["methods"]["FCI"]["finite_difference_derivative_hartree_per_coordinate"]),
        )
        larger_orbital_basis = center_energy["spatial_orbitals"] > int(fci_row["spatial_orbitals"])
        basis_mismatch_blocks_advantage_claim = str(fci_row["basis"]).lower() != basis.lower()
        rows.append(
            {
                "source_benchmark": "B3",
                "molecule": molecule,
                "coordinate": fci_row["coordinate"],
                "coordinate_center": center,
                "finite_difference_delta": delta,
                "sto3g_spatial_orbitals": fci_row["spatial_orbitals"],
                "selected_ci_basis": basis,
                "selected_ci_larger_than_sto3g_orbitals": larger_orbital_basis,
                "selected_ci_center": center_energy,
                "selected_ci_minus": minus,
                "selected_ci_plus": plus,
                "selected_ci_finite_difference_derivative_hartree_per_coordinate": derivative,
                "fci_sto3g_derivative_hartree_per_coordinate": fci_row["methods"]["FCI"][
                    "finite_difference_derivative_hartree_per_coordinate"
                ],
                "selected_ci_derivative_shift_vs_sto3g_fci": derivative
                - float(fci_row["methods"]["FCI"]["finite_difference_derivative_hartree_per_coordinate"]),
                "selected_ci_total_wall_time_seconds": (
                    minus["wall_time_seconds"] + center_energy["wall_time_seconds"] + plus["wall_time_seconds"]
                ),
                "selected_ci_total_determinant_product_three_point": sum(determinant_points),
                "selected_ci_max_determinant_product": max(determinant_points),
                "all_selected_ci_points_converged": all(
                    point["converged"] for point in [minus, center_energy, plus]
                ),
                "grouped_pauli_estimator": grouped,
                "previous_sampled_target_shot_floor": sampled_by_name[molecule][
                    "target_total_shot_floor_neyman"
                ],
                "previous_mapper_total_measurement_shot_floor": mapper_by_name[molecule][
                    "total_measurement_shot_floor"
                ],
                "candidate_beats_selected_ci_larger_basis_denominator": False,
                "basis_mismatch_blocks_advantage_claim": basis_mismatch_blocks_advantage_claim,
                "comparison_interpretation": (
                    "The denominator is now a selected-CI finite-difference row in a larger orbital basis. "
                    "The Pauli estimator is still sourced from the STO-3G Hamiltonian and now carries "
                    "QWC grouping plus ansatz-preparation surcharge, so it is a stress comparison and "
                    "does not support an advantage claim."
                ),
            }
        )

    summary = {
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "selected_ci_or_larger_active_space_included": True,
        "selected_ci_larger_basis_rows": sum(
            1 for row in rows if row["selected_ci_larger_than_sto3g_orbitals"]
        ),
        "all_selected_ci_points_converged": all(row["all_selected_ci_points_converged"] for row in rows),
        "max_selected_ci_spatial_orbitals": max(
            row["selected_ci_center"]["spatial_orbitals"] for row in rows
        ),
        "max_selected_ci_spin_orbital_qubits": max(
            row["selected_ci_center"]["spin_orbital_qubits"] for row in rows
        ),
        "max_selected_ci_determinant_product": max(
            row["selected_ci_max_determinant_product"] for row in rows
        ),
        "max_selected_ci_total_determinant_product_three_point": max(
            row["selected_ci_total_determinant_product_three_point"] for row in rows
        ),
        "max_selected_ci_total_wall_time_seconds": max(
            row["selected_ci_total_wall_time_seconds"] for row in rows
        ),
        "pauli_grouping_included": True,
        "ansatz_state_preparation_surcharge_included": True,
        "large_basis_quantum_mapper_included": False,
        "min_packet_reduction_vs_ungrouped": min(
            row["grouped_pauli_estimator"]["packet_reduction_vs_ungrouped"] for row in rows
        ),
        "max_packet_reduction_vs_ungrouped": max(
            row["grouped_pauli_estimator"]["packet_reduction_vs_ungrouped"] for row in rows
        ),
        "max_qwc_group_count": max(row["grouped_pauli_estimator"]["qwc_group_count"] for row in rows),
        "max_ansatz_two_qubit_gate_executions_at_target": max(
            row["grouped_pauli_estimator"]["ansatz_two_qubit_gate_executions_at_target"]
            for row in rows
        ),
        "selected_ci_larger_basis_denominator_beaten_count": sum(
            1 for row in rows if row["candidate_beats_selected_ci_larger_basis_denominator"]
        ),
        "quantum_advantage_claimed": False,
        "reaction_dynamics_solution_claimed": False,
    }
    report = {
        "benchmark_id": "B3",
        "problem_id": 49,
        "title": "B3 selected-CI larger-basis denominator and grouped Pauli boundary",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": STATUS,
        "method": METHOD,
        "dependency_benchmark": "B3",
        "source_fci_reference": str(fci_path),
        "source_fci_method": fci.get("method"),
        "source_sampled_pauli": str(sampled_path),
        "source_sampled_pauli_method": sampled.get("method"),
        "source_mapper": str(mapper_path),
        "source_mapper_method": mapper.get("method"),
        "basis_plan": BASIS_PLAN,
        "summary": summary,
        "rows": rows,
        "claim_boundary": [
            "Supported: selected-CI finite-difference denominator rows in larger orbital bases for the same four B3 reaction coordinates.",
            "Supported: QWC grouped measurement-setting counts and an explicit two-layer ansatz state-preparation surcharge on the sampled Pauli side.",
            "Not supported: a large-basis quantum Hamiltonian mapper, selected-CI chemical benchmark quality, quantum advantage, or complete reaction dynamics.",
        ],
        "next_steps": [
            "Map the same larger-basis Hamiltonians to qubits instead of comparing STO-3G Pauli estimators to larger-basis selected-CI denominators.",
            "Replace the hardware-efficient ansatz surcharge with a chemically motivated UCC/ADAPT/adiabatic preparation cost.",
            "Use a stricter selected-CI schedule or DMRG denominator for H2O and N2 once determinant spaces become larger than this v0 stress table.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain a selected-CI/grouped-Pauli boundary")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("expected four B3 reaction-coordinate rows")
    if summary.get("selected_ci_or_larger_active_space_included") is not True:
        errors.append("selected-CI/larger-active-space denominator must be included")
    if summary.get("selected_ci_larger_basis_rows") != 4:
        errors.append("all rows must use a larger orbital basis than STO-3G")
    if summary.get("pauli_grouping_included") is not True:
        errors.append("Pauli grouping must be included")
    if summary.get("ansatz_state_preparation_surcharge_included") is not True:
        errors.append("ansatz state-preparation surcharge must be included")
    if summary.get("large_basis_quantum_mapper_included") is not False:
        errors.append("must not claim a large-basis quantum mapper in this artifact")
    if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
        errors.append("must not claim selected-CI/larger-basis denominator wins")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction dynamics solution")
    for row in report.get("rows", []):
        if row.get("selected_ci_larger_than_sto3g_orbitals") is not True:
            errors.append(f"{row.get('molecule')} is not larger than the STO-3G orbital row")
        if row.get("all_selected_ci_points_converged") is not True:
            errors.append(f"{row.get('molecule')} selected-CI points did not converge")
        if row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False:
            errors.append(f"{row.get('molecule')} must not claim a selected-CI denominator win")
        grouped = row.get("grouped_pauli_estimator", {})
        if grouped.get("qwc_group_count", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no QWC groups")
        if grouped.get("ansatz_two_qubit_gate_executions_at_target", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no ansatz preparation surcharge")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# B3 Selected-CI Larger-Basis Denominator and Grouped Pauli Boundary v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source sampled Pauli method: {report['source_sampled_pauli_method']}",
        f"- Source mapper method: {report['source_mapper_method']}",
        f"- Instances: {report['summary']['instance_count']}",
        f"- Selected-CI/larger-basis rows: {report['summary']['selected_ci_larger_basis_rows']}",
        f"- All selected-CI points converged: {report['summary']['all_selected_ci_points_converged']}",
        f"- Max selected-CI spatial orbitals: {report['summary']['max_selected_ci_spatial_orbitals']}",
        f"- Max selected-CI determinant product: {report['summary']['max_selected_ci_determinant_product']}",
        f"- Max selected-CI three-point determinant product: {report['summary']['max_selected_ci_total_determinant_product_three_point']}",
        f"- QWC packet reduction range: {report['summary']['min_packet_reduction_vs_ungrouped']:.3f}x-{report['summary']['max_packet_reduction_vs_ungrouped']:.3f}x",
        f"- Max QWC group count: {report['summary']['max_qwc_group_count']}",
        f"- Max ansatz two-qubit gate executions at target: {report['summary']['max_ansatz_two_qubit_gate_executions_at_target']}",
        f"- Selected-CI/larger-basis denominator beaten count: {report['summary']['selected_ci_larger_basis_denominator_beaten_count']}",
        f"- Quantum advantage claimed: {report['summary']['quantum_advantage_claimed']}",
        f"- Reaction-dynamics solution claimed: {report['summary']['reaction_dynamics_solution_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Rows",
        "",
        "| molecule | selected-CI basis | orbitals | selected det product | derivative shift vs STO-3G FCI | QWC groups | packet reduction | target shots | ansatz 2q executions | beats denominator? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        grouped = row["grouped_pauli_estimator"]
        lines.append(
            f"| {row['molecule']} | {row['selected_ci_basis']} | "
            f"{row['selected_ci_center']['spatial_orbitals']} | "
            f"{row['selected_ci_max_determinant_product']} | "
            f"{row['selected_ci_derivative_shift_vs_sto3g_fci']:.6e} | "
            f"{grouped['qwc_group_count']} | {grouped['packet_reduction_vs_ungrouped']:.3f}x | "
            f"{grouped['target_total_shot_floor_neyman']} | "
            f"{grouped['ansatz_two_qubit_gate_executions_at_target']} | "
            f"{row['candidate_beats_selected_ci_larger_basis_denominator']} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in report["claim_boundary"])
    lines.extend(["", "## Next Steps", ""])
    lines.extend(f"- {item}" for item in report["next_steps"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fci-reference",
        type=Path,
        default=Path("results/B10_t1_d5_b3_fci_reference_table_v0.json"),
    )
    parser.add_argument(
        "--sampled-pauli",
        type=Path,
        default=Path("results/B3_sampled_pauli_estimator_confidence_v0.json"),
    )
    parser.add_argument(
        "--mapper",
        type=Path,
        default=Path("results/B3_hamiltonian_pauli_mapper_comparison_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_selected_ci_grouped_pauli_boundary_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_selected_ci_grouped_pauli_boundary.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.fci_reference, args.sampled_pauli, args.mapper)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "instances": report["summary"]["instance_count"],
                    "selected_ci_larger_basis_rows": report["summary"][
                        "selected_ci_larger_basis_rows"
                    ],
                    "max_selected_ci_spatial_orbitals": report["summary"][
                        "max_selected_ci_spatial_orbitals"
                    ],
                    "max_qwc_group_count": report["summary"]["max_qwc_group_count"],
                    "denominator_beaten_count": report["summary"][
                        "selected_ci_larger_basis_denominator_beaten_count"
                    ],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
