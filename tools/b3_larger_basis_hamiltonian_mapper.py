#!/usr/bin/env python3
"""Map B3 selected-CI larger-basis Hamiltonians to qubits and retest measurement costs."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

from b3_hamiltonian_pauli_mapper_comparison import COEFF_CUTOFF, mapped_pauli_terms
from b3_sampled_pauli_estimator_confidence import hf_pauli_expectation


STATUS = "larger_basis_hamiltonian_mapper_boundary_not_advantage_claim"
METHOD = "b3_larger_basis_hamiltonian_mapper_v0"
ANZATZ_LAYERS = 2
MIN_TARGET_ERROR = 1.0e-3
TARGET_ERROR_FRACTION = 0.05


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def target_error(value: float) -> float:
    return max(MIN_TARGET_ERROR, TARGET_ERROR_FRACTION * abs(value))


def measurement_bucket_label(pauli_label: str) -> str:
    # Conservative setting bucket: exact Pauli basis label. Compatible terms can
    # be further merged later; this bucket count is a valid upper bound.
    return pauli_label


def pauli_measurement_metrics(
    terms: list[dict[str, Any]],
    electrons: int,
    qubits: int,
    derivative: float,
) -> dict[str, Any]:
    occupied = min(electrons, qubits)
    deterministic_terms = 0
    random_terms = 0
    random_coeff_l1 = 0.0
    random_coeff_l2_sq = 0.0
    conservative_bucket_set: set[str] = set()
    top_random_terms = []
    hf_energy = 0.0
    for term in terms:
        expectation = hf_pauli_expectation(str(term["pauli"]), occupied)
        coefficient = float(term["coefficient"])
        variance = 1.0 - expectation * expectation
        hf_energy += coefficient * expectation
        if variance > 0.0:
            random_terms += 1
            random_coeff_l1 += abs(coefficient)
            random_coeff_l2_sq += coefficient * coefficient
            conservative_bucket_set.add(measurement_bucket_label(str(term["pauli"])))
            if len(top_random_terms) < 12:
                top_random_terms.append(
                    {
                        "pauli": term["pauli"],
                        "coefficient": coefficient,
                        "weight": term["weight"],
                    }
                )
        else:
            deterministic_terms += 1
    epsilon = target_error(derivative)
    neyman_shot_floor = int(math.ceil((random_coeff_l1 / epsilon) ** 2)) if random_terms else 0
    variance_upper_bound_floor = int(math.ceil(random_coeff_l2_sq / (epsilon * epsilon))) * max(1, random_terms)
    two_qubit_per_shot = max(0, 2 * (qubits - 1) * ANZATZ_LAYERS)
    single_qubit_per_shot = 2 * qubits * ANZATZ_LAYERS
    return {
        "hf_reference_energy_from_pauli_terms_hartree": hf_energy,
        "deterministic_pauli_terms": deterministic_terms,
        "random_pauli_terms": random_terms,
        "conservative_same_basis_bucket_count": len(conservative_bucket_set),
        "conservative_bucket_reduction_vs_ungrouped": (
            random_terms / len(conservative_bucket_set) if conservative_bucket_set else math.inf
        ),
        "target_observable_error_hartree_per_coordinate": epsilon,
        "target_error_fraction": TARGET_ERROR_FRACTION,
        "random_coefficient_l1_norm": random_coeff_l1,
        "random_coefficient_l2_sq": random_coeff_l2_sq,
        "neyman_target_total_shot_floor": neyman_shot_floor,
        "variance_upper_bound_total_shot_floor": variance_upper_bound_floor,
        "ansatz_model": "two-layer nearest-neighbor hardware-efficient preparation surcharge",
        "ansatz_layers": ANZATZ_LAYERS,
        "ansatz_two_qubit_gates_per_shot": two_qubit_per_shot,
        "ansatz_single_qubit_rotations_per_shot": single_qubit_per_shot,
        "ansatz_two_qubit_gate_executions_at_neyman_target": neyman_shot_floor * two_qubit_per_shot,
        "top_random_terms_preview": top_random_terms,
    }


def build_report(selected_ci_path: Path) -> dict[str, Any]:
    selected_ci = load_json(selected_ci_path)
    rows = []
    for source_row in selected_ci.get("rows", []):
        molecule = source_row["molecule"]
        basis = source_row["selected_ci_basis"]
        coordinate_center = float(source_row["coordinate_center"])
        derivative = float(source_row["selected_ci_finite_difference_derivative_hartree_per_coordinate"])
        started = time.perf_counter()
        qubits, particles, terms = mapped_pauli_terms(
            molecule=molecule,
            coordinate_center=coordinate_center,
            basis=basis,
        )
        mapping_wall_time = time.perf_counter() - started
        coeff_l1 = sum(float(term["abs_coefficient"]) for term in terms)
        coeff_l2_sq = sum(float(term["coefficient"]) ** 2 for term in terms)
        measurement = pauli_measurement_metrics(
            terms=terms,
            electrons=int(source_row["selected_ci_center"]["electrons"]),
            qubits=qubits,
            derivative=derivative,
        )
        selected_det = int(source_row["selected_ci_max_determinant_product"])
        rows.append(
            {
                "source_benchmark": "B3",
                "molecule": molecule,
                "coordinate": source_row["coordinate"],
                "coordinate_center": coordinate_center,
                "selected_ci_basis": basis,
                "mapper": "qiskit_nature.second_q.mappers.JordanWignerMapper",
                "larger_basis_quantum_mapper_included": True,
                "spatial_orbitals": int(source_row["selected_ci_center"]["spatial_orbitals"]),
                "spin_orbital_qubits": qubits,
                "total_qubits": qubits,
                "selected_ci_spin_orbital_qubits": int(
                    source_row["selected_ci_center"]["spin_orbital_qubits"]
                ),
                "electrons": int(source_row["selected_ci_center"]["electrons"]),
                "num_alpha_particles": int(source_row["selected_ci_center"]["num_alpha_particles"]),
                "num_beta_particles": int(source_row["selected_ci_center"]["num_beta_particles"]),
                "mapper_particles": [int(particles[0]), int(particles[1])],
                "pauli_terms_after_cutoff": len(terms),
                "coefficient_cutoff": COEFF_CUTOFF,
                "max_pauli_weight": max(term["weight"] for term in terms),
                "mean_pauli_weight": sum(term["weight"] for term in terms) / len(terms),
                "coefficient_l1_norm": coeff_l1,
                "coefficient_l2_sq": coeff_l2_sq,
                "largest_abs_coefficient": max(term["abs_coefficient"] for term in terms),
                "selected_ci_derivative_hartree_per_coordinate": derivative,
                "selected_ci_center_energy_hartree": source_row["selected_ci_center"][
                    "selected_ci_energy_hartree"
                ],
                "selected_ci_max_determinant_product": selected_det,
                "selected_ci_total_determinant_product_three_point": int(
                    source_row["selected_ci_total_determinant_product_three_point"]
                ),
                "selected_ci_total_wall_time_seconds": float(
                    source_row["selected_ci_total_wall_time_seconds"]
                ),
                "mapping_wall_time_seconds": mapping_wall_time,
                "measurement_model": measurement,
                "candidate_beats_selected_ci_larger_basis_denominator": False,
                "comparison_interpretation": (
                    "This row maps the same larger-basis Hamiltonian used by the selected-CI denominator. "
                    "The mapped Hamiltonian and conservative measurement buckets are now explicit, but the "
                    "Neyman shot floor plus generic ansatz preparation surcharge still does not justify an "
                    "advantage claim."
                ),
            }
        )

    summary = {
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "larger_basis_quantum_mapper_included": True,
        "same_basis_as_selected_ci_denominator": True,
        "pauli_measurement_cost_included": True,
        "conservative_measurement_bucket_model": "same_basis_bucket_upper_bound_not_optimal_qwc_cover",
        "ansatz_state_preparation_surcharge_included": True,
        "max_total_qubits": max(row["total_qubits"] for row in rows),
        "max_pauli_terms_after_cutoff": max(row["pauli_terms_after_cutoff"] for row in rows),
        "max_pauli_weight": max(row["max_pauli_weight"] for row in rows),
        "max_conservative_same_basis_bucket_count": max(
            row["measurement_model"]["conservative_same_basis_bucket_count"] for row in rows
        ),
        "min_conservative_bucket_reduction_vs_ungrouped": min(
            row["measurement_model"]["conservative_bucket_reduction_vs_ungrouped"] for row in rows
        ),
        "max_conservative_bucket_reduction_vs_ungrouped": max(
            row["measurement_model"]["conservative_bucket_reduction_vs_ungrouped"] for row in rows
        ),
        "max_neyman_target_total_shot_floor": max(
            row["measurement_model"]["neyman_target_total_shot_floor"] for row in rows
        ),
        "max_ansatz_two_qubit_gate_executions_at_neyman_target": max(
            row["measurement_model"]["ansatz_two_qubit_gate_executions_at_neyman_target"]
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
        "title": "B3 larger-basis Hamiltonian mapper boundary",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": STATUS,
        "method": METHOD,
        "dependency_benchmark": "B3",
        "source_selected_ci_grouped_pauli": str(selected_ci_path),
        "source_selected_ci_grouped_pauli_method": selected_ci.get("method"),
        "summary": summary,
        "rows": rows,
        "claim_boundary": [
            "Supported: Jordan-Wigner qubit Hamiltonians for the same larger bases used by the selected-CI denominator rows.",
            "Supported: conservative same-basis measurement bucket counts, Neyman shot floors, and a two-layer ansatz state-preparation surcharge.",
            "Not supported: optimal Pauli grouping, chemical ansatz preparation, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.",
        ],
        "next_steps": [
            "Replace conservative same-basis buckets with an actual QWC or commuting-cover optimizer on the larger-basis Pauli sets.",
            "Replace the generic two-layer ansatz surcharge with UCC, ADAPT-VQE, or adiabatic preparation costs.",
            "Retest against stricter selected-CI, DMRG, or tensor-network denominators at fixed observable error.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain a larger-basis mapper boundary")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    if report.get("dependency_benchmark") != "B3":
        errors.append("dependency_benchmark must be B3")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("expected four B3 reaction-coordinate rows")
    if summary.get("larger_basis_quantum_mapper_included") is not True:
        errors.append("larger-basis quantum mapper must be included")
    if summary.get("same_basis_as_selected_ci_denominator") is not True:
        errors.append("mapped basis must match selected-CI denominator basis")
    if summary.get("pauli_measurement_cost_included") is not True:
        errors.append("Pauli measurement cost must be included")
    if summary.get("ansatz_state_preparation_surcharge_included") is not True:
        errors.append("ansatz state-preparation surcharge must be included")
    if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
        errors.append("must not claim selected-CI larger-basis denominator wins")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction dynamics solution")
    for row in report.get("rows", []):
        if row.get("larger_basis_quantum_mapper_included") is not True:
            errors.append(f"{row.get('molecule')} must include larger-basis mapper")
        if row.get("spin_orbital_qubits") != row.get("selected_ci_spin_orbital_qubits"):
            errors.append(f"{row.get('molecule')} mapper qubits differ from selected-CI qubits")
        if row.get("pauli_terms_after_cutoff", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no mapped Pauli terms")
        measurement = row.get("measurement_model", {})
        if measurement.get("random_pauli_terms", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no random Pauli terms")
        if measurement.get("conservative_same_basis_bucket_count", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no measurement buckets")
        if measurement.get("neyman_target_total_shot_floor", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no Neyman shot floor")
        if measurement.get("ansatz_two_qubit_gate_executions_at_neyman_target", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no ansatz execution surcharge")
        if row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False:
            errors.append(f"{row.get('molecule')} must not claim a selected-CI denominator win")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# B3 Larger-Basis Hamiltonian Mapper Boundary v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source selected-CI boundary method: {report['source_selected_ci_grouped_pauli_method']}",
        f"- Instances: {report['summary']['instance_count']}",
        f"- Larger-basis quantum mapper included: {report['summary']['larger_basis_quantum_mapper_included']}",
        f"- Same basis as selected-CI denominator: {report['summary']['same_basis_as_selected_ci_denominator']}",
        f"- Max total qubits: {report['summary']['max_total_qubits']}",
        f"- Max Pauli terms after cutoff: {report['summary']['max_pauli_terms_after_cutoff']}",
        f"- Max conservative same-basis bucket count: {report['summary']['max_conservative_same_basis_bucket_count']}",
        f"- Conservative bucket reduction range: {report['summary']['min_conservative_bucket_reduction_vs_ungrouped']:.3f}x-{report['summary']['max_conservative_bucket_reduction_vs_ungrouped']:.3f}x",
        f"- Max Neyman target shot floor: {report['summary']['max_neyman_target_total_shot_floor']}",
        f"- Max ansatz two-qubit executions at Neyman target: {report['summary']['max_ansatz_two_qubit_gate_executions_at_neyman_target']}",
        f"- Selected-CI larger-basis denominator beaten count: {report['summary']['selected_ci_larger_basis_denominator_beaten_count']}",
        f"- Quantum advantage claimed: {report['summary']['quantum_advantage_claimed']}",
        f"- Reaction-dynamics solution claimed: {report['summary']['reaction_dynamics_solution_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Rows",
        "",
        "| molecule | basis | qubits | Pauli terms | random terms | buckets | bucket reduction | Neyman shots | ansatz 2q executions | beats denominator? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        measurement = row["measurement_model"]
        lines.append(
            f"| {row['molecule']} | {row['selected_ci_basis']} | {row['total_qubits']} | "
            f"{row['pauli_terms_after_cutoff']} | {measurement['random_pauli_terms']} | "
            f"{measurement['conservative_same_basis_bucket_count']} | "
            f"{measurement['conservative_bucket_reduction_vs_ungrouped']:.3f}x | "
            f"{measurement['neyman_target_total_shot_floor']} | "
            f"{measurement['ansatz_two_qubit_gate_executions_at_neyman_target']} | "
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
        "--selected-ci-boundary",
        type=Path,
        default=Path("results/B3_selected_ci_grouped_pauli_boundary_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_larger_basis_hamiltonian_mapper_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_larger_basis_hamiltonian_mapper.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.selected_ci_boundary)
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
                    "max_total_qubits": report["summary"]["max_total_qubits"],
                    "max_pauli_terms_after_cutoff": report["summary"]["max_pauli_terms_after_cutoff"],
                    "max_neyman_target_shot_floor": report["summary"][
                        "max_neyman_target_total_shot_floor"
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
