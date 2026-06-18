#!/usr/bin/env python3
"""Propagate B3 grouped covariance to derivative error and chemical prep envelopes."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


STATUS = "chemical_state_prep_derivative_boundary_not_advantage_claim"
METHOD = "b3_chemical_state_prep_derivative_boundary_v0"
SOURCE_COVARIANCE_METHOD = "b3_grouped_covariance_shot_floor_v0"
SOURCE_SELECTED_CI_METHOD = "b3_selected_ci_grouped_pauli_boundary_v0"
SOURCE_MAPPER_METHOD = "b3_larger_basis_hamiltonian_mapper_v0"
UCC_TROTTER_REPS = 1
ADAPT_SELECTED_EXCITATION_FACTOR = 4
ADIABATIC_STEP_FACTOR = 10


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def n_choose_2(value: int) -> int:
    return value * (value - 1) // 2 if value >= 2 else 0


def chemical_prep_envelope(qubits: int, electrons: int) -> dict[str, Any]:
    occupied = min(electrons, qubits)
    virtual = max(0, qubits - occupied)
    ucc_singles = occupied * virtual
    ucc_doubles = n_choose_2(occupied) * n_choose_2(virtual)
    ucc_excitations = ucc_singles + ucc_doubles
    ladder_two_qubit_gates = max(1, 2 * (qubits - 1))
    adapt_selected = min(ucc_excitations, ADAPT_SELECTED_EXCITATION_FACTOR * qubits)
    adapt_pool = ucc_excitations
    adiabatic_steps = max(1, ADIABATIC_STEP_FACTOR * qubits)
    return {
        "occupied_spin_orbitals": occupied,
        "virtual_spin_orbitals": virtual,
        "jw_ladder_two_qubit_gates_per_excitation": ladder_two_qubit_gates,
        "uccsd_singles": ucc_singles,
        "uccsd_doubles": ucc_doubles,
        "uccsd_excitation_count": ucc_excitations,
        "uccsd_trotter_reps": UCC_TROTTER_REPS,
        "uccsd_two_qubit_gates_per_preparation": ucc_excitations
        * ladder_two_qubit_gates
        * UCC_TROTTER_REPS,
        "adapt_pool_size": adapt_pool,
        "adapt_selected_excitation_cap": adapt_selected,
        "adapt_two_qubit_gates_per_preparation": adapt_selected * ladder_two_qubit_gates,
        "adapt_gradient_pool_evaluations_per_layer": adapt_pool,
        "adiabatic_trotter_steps": adiabatic_steps,
        "adiabatic_two_qubit_gates_per_step": ladder_two_qubit_gates,
        "adiabatic_two_qubit_gates_per_preparation": adiabatic_steps * ladder_two_qubit_gates,
    }


def derivative_shot_floor(
    grouped_energy_shot_floor: int,
    derivative_target_error: float,
    finite_difference_delta: float,
) -> dict[str, Any]:
    endpoint_energy_error = derivative_target_error * finite_difference_delta * math.sqrt(2.0)
    scale = (derivative_target_error / endpoint_energy_error) ** 2
    endpoint_floor = int(math.ceil(grouped_energy_shot_floor * scale))
    total_floor = 2 * endpoint_floor
    return {
        "derivative_target_error_hartree_per_coordinate": derivative_target_error,
        "finite_difference_delta": finite_difference_delta,
        "endpoint_energy_error_target_hartree": endpoint_energy_error,
        "endpoint_shot_floor_scale_vs_center_energy_floor": scale,
        "endpoint_grouped_covariance_shot_floor": endpoint_floor,
        "three_point_derivative_total_shot_floor": total_floor,
        "derivative_shot_floor_inflation_vs_center_energy_floor": (
            total_floor / grouped_energy_shot_floor if grouped_energy_shot_floor else math.inf
        ),
    }


def build_report(
    grouped_covariance_path: Path,
    selected_ci_path: Path,
    mapper_path: Path,
) -> dict[str, Any]:
    grouped = load_json(grouped_covariance_path)
    selected_ci = load_json(selected_ci_path)
    mapper = load_json(mapper_path)
    selected_by_molecule = {row["molecule"]: row for row in selected_ci.get("rows", [])}
    mapper_by_molecule = {row["molecule"]: row for row in mapper.get("rows", [])}
    rows = []
    for cov_row in grouped.get("rows", []):
        molecule = cov_row["molecule"]
        selected_row = selected_by_molecule[molecule]
        mapper_row = mapper_by_molecule[molecule]
        qubits = int(cov_row["total_qubits"])
        electrons = int(mapper_row["electrons"])
        derivative = derivative_shot_floor(
            int(cov_row["grouped_covariance_shot_floor"]),
            float(cov_row["target_observable_error_hartree_per_coordinate"]),
            float(selected_row["finite_difference_delta"]),
        )
        prep = chemical_prep_envelope(qubits, electrons)
        prep_executions = {
            "hf_reference_two_qubit_gate_executions_at_derivative_target": (
                derivative["three_point_derivative_total_shot_floor"]
                * int(cov_row["ansatz_two_qubit_gates_per_shot"])
            ),
            "uccsd_two_qubit_gate_executions_at_derivative_target": (
                derivative["three_point_derivative_total_shot_floor"]
                * prep["uccsd_two_qubit_gates_per_preparation"]
            ),
            "adapt_two_qubit_gate_executions_at_derivative_target": (
                derivative["three_point_derivative_total_shot_floor"]
                * prep["adapt_two_qubit_gates_per_preparation"]
            ),
            "adiabatic_two_qubit_gate_executions_at_derivative_target": (
                derivative["three_point_derivative_total_shot_floor"]
                * prep["adiabatic_two_qubit_gates_per_preparation"]
            ),
        }
        rows.append(
            {
                "source_benchmark": "B3",
                "molecule": molecule,
                "coordinate": cov_row["coordinate"],
                "coordinate_center": cov_row["coordinate_center"],
                "selected_ci_basis": cov_row["selected_ci_basis"],
                "total_qubits": qubits,
                "electrons": electrons,
                "spatial_orbitals": int(mapper_row["spatial_orbitals"]),
                "selected_ci_max_determinant_product": int(
                    mapper_row["selected_ci_max_determinant_product"]
                ),
                "selected_ci_total_determinant_product_three_point": int(
                    mapper_row["selected_ci_total_determinant_product_three_point"]
                ),
                "source_grouped_covariance_shot_floor": int(
                    cov_row["grouped_covariance_shot_floor"]
                ),
                "source_grouped_covariance_reduction_vs_independent": float(
                    cov_row["grouped_covariance_reduction_vs_previous_independent_floor"]
                ),
                "derivative_error_propagation_included": True,
                "derivative_shot_floor": derivative,
                "sampled_chemical_state_covariance_included": False,
                "chemical_state_prep_cost_envelope_included": True,
                "chemical_state_prep_envelope": prep,
                "chemical_state_prep_executions": prep_executions,
                "candidate_beats_selected_ci_larger_basis_denominator": False,
                "comparison_interpretation": (
                    "Derivative-level propagation inflates the grouped-covariance shot budget because "
                    "two endpoint energy estimates are needed for the finite difference. UCCSD, ADAPT, "
                    "and adiabatic preparation envelopes are now explicitly charged, but no sampled "
                    "correlated-state covariance is available yet, so this remains a boundary result."
                ),
            }
        )

    summary = {
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "source_grouped_covariance_method": grouped.get("method"),
        "source_selected_ci_method": selected_ci.get("method"),
        "source_mapper_method": mapper.get("method"),
        "derivative_error_propagation_included": True,
        "sampled_chemical_state_covariance_included": False,
        "chemical_state_prep_cost_envelope_included": True,
        "chemical_state_prep_models": ["UCCSD", "ADAPT-VQE-envelope", "adiabatic-envelope"],
        "max_total_qubits": max(row["total_qubits"] for row in rows),
        "max_source_grouped_covariance_shot_floor": max(
            row["source_grouped_covariance_shot_floor"] for row in rows
        ),
        "max_three_point_derivative_total_shot_floor": max(
            row["derivative_shot_floor"]["three_point_derivative_total_shot_floor"]
            for row in rows
        ),
        "min_derivative_shot_floor_inflation_vs_center_energy_floor": min(
            row["derivative_shot_floor"]["derivative_shot_floor_inflation_vs_center_energy_floor"]
            for row in rows
        ),
        "max_derivative_shot_floor_inflation_vs_center_energy_floor": max(
            row["derivative_shot_floor"]["derivative_shot_floor_inflation_vs_center_energy_floor"]
            for row in rows
        ),
        "max_uccsd_two_qubit_gates_per_preparation": max(
            row["chemical_state_prep_envelope"]["uccsd_two_qubit_gates_per_preparation"]
            for row in rows
        ),
        "max_adapt_two_qubit_gates_per_preparation": max(
            row["chemical_state_prep_envelope"]["adapt_two_qubit_gates_per_preparation"]
            for row in rows
        ),
        "max_adiabatic_two_qubit_gates_per_preparation": max(
            row["chemical_state_prep_envelope"]["adiabatic_two_qubit_gates_per_preparation"]
            for row in rows
        ),
        "max_uccsd_two_qubit_gate_executions_at_derivative_target": max(
            row["chemical_state_prep_executions"][
                "uccsd_two_qubit_gate_executions_at_derivative_target"
            ]
            for row in rows
        ),
        "max_adapt_two_qubit_gate_executions_at_derivative_target": max(
            row["chemical_state_prep_executions"][
                "adapt_two_qubit_gate_executions_at_derivative_target"
            ]
            for row in rows
        ),
        "max_adiabatic_two_qubit_gate_executions_at_derivative_target": max(
            row["chemical_state_prep_executions"][
                "adiabatic_two_qubit_gate_executions_at_derivative_target"
            ]
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
        "title": "B3 chemical state-preparation derivative boundary",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": STATUS,
        "method": METHOD,
        "dependency_benchmark": "B3",
        "source_grouped_covariance": str(grouped_covariance_path),
        "source_grouped_covariance_method": grouped.get("method"),
        "source_selected_ci": str(selected_ci_path),
        "source_selected_ci_method": selected_ci.get("method"),
        "source_larger_basis_mapper": str(mapper_path),
        "source_larger_basis_mapper_method": mapper.get("method"),
        "summary": summary,
        "rows": rows,
        "claim_boundary": [
            "Supported: propagation of grouped-covariance energy shot floors through three-point finite-difference derivative error.",
            "Supported: explicit UCCSD, ADAPT-VQE-envelope, and adiabatic-envelope two-qubit state-preparation cost models.",
            "Not supported: sampled correlated chemical-state covariance, converged UCC/ADAPT energies, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.",
        ],
        "next_steps": [
            "Generate actual sampled covariance from a small UCC or ADAPT state instead of using the HF covariance source.",
            "Replace the envelope gate counts with compiled ansatz circuits and optimizer-loop shot accounting.",
            "Retest against stricter selected-CI, DMRG, or tensor-network denominators at derivative-level observable error.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain a chemical state-prep derivative boundary")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    if report.get("source_grouped_covariance_method") != SOURCE_COVARIANCE_METHOD:
        errors.append("source grouped covariance method changed")
    if report.get("source_selected_ci_method") != SOURCE_SELECTED_CI_METHOD:
        errors.append("source selected-CI method changed")
    if report.get("source_larger_basis_mapper_method") != SOURCE_MAPPER_METHOD:
        errors.append("source mapper method changed")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("expected four B3 rows")
    if summary.get("derivative_error_propagation_included") is not True:
        errors.append("derivative error propagation must be included")
    if summary.get("sampled_chemical_state_covariance_included") is not False:
        errors.append("must not claim sampled chemical-state covariance")
    if summary.get("chemical_state_prep_cost_envelope_included") is not True:
        errors.append("chemical state-preparation cost envelope must be included")
    if summary.get("min_derivative_shot_floor_inflation_vs_center_energy_floor", 0.0) <= 1.0:
        errors.append("derivative-level floor should inflate versus center energy floor")
    if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
        errors.append("must not claim selected-CI denominator wins")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction dynamics solution")
    for row in report.get("rows", []):
        if row.get("derivative_error_propagation_included") is not True:
            errors.append(f"{row.get('molecule')} lacks derivative propagation")
        if row.get("sampled_chemical_state_covariance_included") is not False:
            errors.append(f"{row.get('molecule')} must not claim sampled chemical covariance")
        if row.get("chemical_state_prep_cost_envelope_included") is not True:
            errors.append(f"{row.get('molecule')} lacks chemical prep envelope")
        derivative = row.get("derivative_shot_floor", {})
        if derivative.get("three_point_derivative_total_shot_floor", 0) <= row.get(
            "source_grouped_covariance_shot_floor", 0
        ):
            errors.append(f"{row.get('molecule')} derivative floor did not inflate")
        prep = row.get("chemical_state_prep_envelope", {})
        if prep.get("uccsd_two_qubit_gates_per_preparation", 0) <= 0:
            errors.append(f"{row.get('molecule')} lacks UCCSD prep cost")
        if prep.get("adapt_two_qubit_gates_per_preparation", 0) <= 0:
            errors.append(f"{row.get('molecule')} lacks ADAPT prep cost")
        if prep.get("adiabatic_two_qubit_gates_per_preparation", 0) <= 0:
            errors.append(f"{row.get('molecule')} lacks adiabatic prep cost")
        if row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False:
            errors.append(f"{row.get('molecule')} must not claim denominator win")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# B3 Chemical State-Preparation Derivative Boundary v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source grouped covariance method: {report['source_grouped_covariance_method']}",
        f"- Source selected-CI method: {report['source_selected_ci_method']}",
        f"- Source mapper method: {report['source_larger_basis_mapper_method']}",
        f"- Instances: {summary['instance_count']}",
        f"- Derivative error propagation included: {summary['derivative_error_propagation_included']}",
        f"- Sampled chemical-state covariance included: {summary['sampled_chemical_state_covariance_included']}",
        f"- Chemical state-prep envelope included: {summary['chemical_state_prep_cost_envelope_included']}",
        f"- Chemical state-prep models: {', '.join(summary['chemical_state_prep_models'])}",
        f"- Max source grouped-covariance shot floor: {summary['max_source_grouped_covariance_shot_floor']}",
        f"- Max three-point derivative total shot floor: {summary['max_three_point_derivative_total_shot_floor']}",
        f"- Derivative shot-floor inflation range: {summary['min_derivative_shot_floor_inflation_vs_center_energy_floor']:.3f}x-{summary['max_derivative_shot_floor_inflation_vs_center_energy_floor']:.3f}x",
        f"- Max UCCSD 2Q gates per preparation: {summary['max_uccsd_two_qubit_gates_per_preparation']}",
        f"- Max ADAPT 2Q gates per preparation: {summary['max_adapt_two_qubit_gates_per_preparation']}",
        f"- Max adiabatic 2Q gates per preparation: {summary['max_adiabatic_two_qubit_gates_per_preparation']}",
        f"- Max UCCSD 2Q executions at derivative target: {summary['max_uccsd_two_qubit_gate_executions_at_derivative_target']}",
        f"- Selected-CI larger-basis denominator beaten count: {summary['selected_ci_larger_basis_denominator_beaten_count']}",
        f"- Quantum advantage claimed: {summary['quantum_advantage_claimed']}",
        f"- Reaction-dynamics solution claimed: {summary['reaction_dynamics_solution_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Rows",
        "",
        "| molecule | basis | center shots | derivative shots | inflation | UCCSD prep 2Q | ADAPT prep 2Q | adiabatic prep 2Q | UCCSD execs | beats denominator? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        derivative = row["derivative_shot_floor"]
        prep = row["chemical_state_prep_envelope"]
        execs = row["chemical_state_prep_executions"]
        lines.append(
            f"| {row['molecule']} | {row['selected_ci_basis']} | "
            f"{row['source_grouped_covariance_shot_floor']} | "
            f"{derivative['three_point_derivative_total_shot_floor']} | "
            f"{derivative['derivative_shot_floor_inflation_vs_center_energy_floor']:.3f}x | "
            f"{prep['uccsd_two_qubit_gates_per_preparation']} | "
            f"{prep['adapt_two_qubit_gates_per_preparation']} | "
            f"{prep['adiabatic_two_qubit_gates_per_preparation']} | "
            f"{execs['uccsd_two_qubit_gate_executions_at_derivative_target']} | "
            f"{row['candidate_beats_selected_ci_larger_basis_denominator']} |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.append(
        "This artifact moves B3 from per-coordinate energy measurement economics to derivative-level "
        "finite-difference accounting. Because the derivative uses two endpoint energy estimates, the "
        "shot budget inflates by roughly 1/delta^2. Chemical state-preparation costs are now explicit "
        "for UCCSD, ADAPT, and adiabatic envelopes, but sampled correlated-state covariance is still an "
        "open task."
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
        "--grouped-covariance",
        type=Path,
        default=Path("results/B3_grouped_covariance_shot_floor_v0.json"),
    )
    parser.add_argument(
        "--selected-ci",
        type=Path,
        default=Path("results/B3_selected_ci_grouped_pauli_boundary_v0.json"),
    )
    parser.add_argument(
        "--mapper",
        type=Path,
        default=Path("results/B3_larger_basis_hamiltonian_mapper_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_chemical_state_prep_derivative_boundary_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_chemical_state_prep_derivative_boundary.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.grouped_covariance, args.selected_ci, args.mapper)
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
                    "max_three_point_derivative_total_shot_floor": report["summary"][
                        "max_three_point_derivative_total_shot_floor"
                    ],
                    "derivative_inflation_range": [
                        report["summary"][
                            "min_derivative_shot_floor_inflation_vs_center_energy_floor"
                        ],
                        report["summary"][
                            "max_derivative_shot_floor_inflation_vs_center_energy_floor"
                        ],
                    ],
                    "sampled_chemical_state_covariance_included": report["summary"][
                        "sampled_chemical_state_covariance_included"
                    ],
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
