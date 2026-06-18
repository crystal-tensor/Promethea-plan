#!/usr/bin/env python3
"""Build sampled Pauli-estimator confidence intervals for B3 Hamiltonian mapper rows."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from b3_hamiltonian_pauli_mapper_comparison import (
    COEFF_CUTOFF,
    mapped_pauli_terms,
    qasm_identifier,
    target_error_for_derivative,
)


PILOT_SHOTS_PER_RANDOM_TERM = 2048
CONFIDENCE_Z = 2.576
SEED = 733104
MIN_RANDOM_TERM_SHOTS_FOR_TARGET = 1


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def hf_pauli_expectation(pauli_label: str, occupied_qubits: int) -> float:
    value = 1.0
    for qidx, ch in enumerate(reversed(pauli_label)):
        if ch in {"X", "Y"}:
            return 0.0
        if ch == "Z" and qidx < occupied_qubits:
            value *= -1.0
    return value


def allocate_target_shots(terms: list[dict[str, Any]], target_error: float) -> tuple[int, list[dict[str, Any]]]:
    random_terms = [term for term in terms if term["term_variance"] > 0.0]
    if not random_terms:
        return 0, []
    coeff_abs_sum = sum(abs(float(term["coefficient"])) for term in random_terms)
    # Neyman allocation for independent Pauli measurements with Bernoulli variance 1.
    total_shots = int(math.ceil((coeff_abs_sum / target_error) ** 2))
    allocations = []
    allocated = 0
    for term in random_terms:
        raw = total_shots * abs(float(term["coefficient"])) / coeff_abs_sum
        shots = max(MIN_RANDOM_TERM_SHOTS_FOR_TARGET, int(math.floor(raw)))
        allocations.append({"pauli": term["pauli"], "target_shots": shots})
        allocated += shots
    remaining = max(0, total_shots - allocated)
    order = sorted(
        range(len(random_terms)),
        key=lambda idx: abs(float(random_terms[idx]["coefficient"])),
        reverse=True,
    )
    for idx in order[:remaining]:
        allocations[idx]["target_shots"] += 1
    return sum(item["target_shots"] for item in allocations), allocations


def sample_term_mean(rng: np.random.Generator, expectation: float, shots: int) -> float:
    p_plus = (1.0 + expectation) / 2.0
    plus_count = int(rng.binomial(shots, p_plus))
    return (2.0 * plus_count - shots) / shots


def build_report(mapper_path: Path, fci_path: Path) -> dict[str, Any]:
    mapper = load_json(mapper_path)
    fci = load_json(fci_path)
    fci_by_name = {row["molecule"]: row for row in fci.get("rows", [])}
    rng = np.random.default_rng(SEED)
    rows = []
    for mapper_row in mapper.get("rows", []):
        molecule = mapper_row["molecule"]
        fci_row = fci_by_name[molecule]
        fci_derivative = float(fci_row["methods"]["FCI"]["finite_difference_derivative_hartree_per_coordinate"])
        _qubits, _particles, raw_terms = mapped_pauli_terms(
            molecule=molecule,
            coordinate_center=float(fci_row["coordinate_center"]),
            basis=str(fci_row["basis"]),
        )
        occupied = min(int(fci_row["electrons"]), int(mapper_row["total_qubits"]))
        terms = []
        true_energy = 0.0
        deterministic_energy = 0.0
        random_variance_coeff_sum = 0.0
        for term in raw_terms:
            expectation = hf_pauli_expectation(str(term["pauli"]), occupied)
            coefficient = float(term["coefficient"])
            term_variance = 1.0 - expectation * expectation
            contribution = coefficient * expectation
            true_energy += contribution
            if term_variance == 0.0:
                deterministic_energy += contribution
            else:
                random_variance_coeff_sum += coefficient * coefficient * term_variance
            terms.append(
                {
                    **term,
                    "hf_expectation": expectation,
                    "term_variance": term_variance,
                    "hf_energy_contribution": contribution,
                }
            )

        random_terms = [term for term in terms if term["term_variance"] > 0.0]
        pilot_estimate = deterministic_energy
        pilot_variance = 0.0
        for term in random_terms:
            mean_hat = sample_term_mean(rng, float(term["hf_expectation"]), PILOT_SHOTS_PER_RANDOM_TERM)
            coefficient = float(term["coefficient"])
            pilot_estimate += coefficient * mean_hat
            pilot_variance += coefficient * coefficient * (1.0 - mean_hat * mean_hat) / PILOT_SHOTS_PER_RANDOM_TERM

        pilot_standard_error = math.sqrt(max(0.0, pilot_variance))
        pilot_ci_half_width = CONFIDENCE_Z * pilot_standard_error
        target_error = target_error_for_derivative(fci_derivative)
        target_shots, target_allocations = allocate_target_shots(terms, target_error)
        old_shot_floor = int(mapper_row["total_measurement_shot_floor"])
        shot_reduction_vs_upper_bound = old_shot_floor / target_shots if target_shots else math.inf
        rows.append(
            {
                "source_benchmark": "B3",
                "molecule": molecule,
                "basis": fci_row["basis"],
                "coordinate": fci_row["coordinate"],
                "coordinate_center": fci_row["coordinate_center"],
                "mapper_method": mapper.get("method"),
                "pauli_terms_after_cutoff": len(terms),
                "coefficient_cutoff": COEFF_CUTOFF,
                "deterministic_pauli_terms": len(terms) - len(random_terms),
                "random_pauli_terms": len(random_terms),
                "pilot_shots_per_random_term": PILOT_SHOTS_PER_RANDOM_TERM,
                "pilot_total_shots": len(random_terms) * PILOT_SHOTS_PER_RANDOM_TERM,
                "pilot_energy_estimate_hartree": pilot_estimate,
                "hf_exact_energy_from_pauli_terms_hartree": true_energy,
                "pilot_abs_error_hartree": abs(pilot_estimate - true_energy),
                "pilot_standard_error_hartree": pilot_standard_error,
                "pilot_confidence_z": CONFIDENCE_Z,
                "pilot_ci_half_width_hartree": pilot_ci_half_width,
                "pilot_ci_contains_exact_energy": abs(pilot_estimate - true_energy) <= pilot_ci_half_width,
                "random_term_variance_coeff_sum": random_variance_coeff_sum,
                "target_observable_error_hartree_per_coordinate": target_error,
                "target_error_fraction": 0.05,
                "target_total_shot_floor_neyman": target_shots,
                "previous_total_shot_floor_upper_bound": old_shot_floor,
                "shot_reduction_vs_upper_bound": shot_reduction_vs_upper_bound,
                "fci_derivative_hartree_per_coordinate": fci_derivative,
                "fci_wall_time_seconds": fci_row["wall_time_seconds"],
                "quantum_beats_fci_denominator": False,
                "sampled_confidence_interval_claim": (
                    "Pilot Pauli sampling on the Hartree-Fock bitstring gives a reproducible estimator "
                    "confidence interval; it is not a quantum advantage or reaction-dynamics solution."
                ),
                "top_target_allocations": sorted(
                    target_allocations,
                    key=lambda item: item["target_shots"],
                    reverse=True,
                )[:8],
                "random_terms_preview": [
                    {
                        "pauli": term["pauli"],
                        "coefficient": term["coefficient"],
                        "target_shots": next(
                            (
                                item["target_shots"]
                                for item in target_allocations
                                if item["pauli"] == term["pauli"]
                            ),
                            0,
                        ),
                    }
                    for term in random_terms[:8]
                ],
            }
        )

    finite_reductions = [
        row["shot_reduction_vs_upper_bound"]
        for row in rows
        if math.isfinite(row["shot_reduction_vs_upper_bound"])
    ]
    summary = {
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "pilot_shots_per_random_term": PILOT_SHOTS_PER_RANDOM_TERM,
        "confidence_z": CONFIDENCE_Z,
        "max_random_pauli_terms": max(row["random_pauli_terms"] for row in rows),
        "max_pilot_total_shots": max(row["pilot_total_shots"] for row in rows),
        "max_target_total_shot_floor_neyman": max(row["target_total_shot_floor_neyman"] for row in rows),
        "max_previous_total_shot_floor_upper_bound": max(row["previous_total_shot_floor_upper_bound"] for row in rows),
        "min_shot_reduction_vs_upper_bound": min(finite_reductions),
        "max_shot_reduction_vs_upper_bound": max(finite_reductions),
        "all_pilot_cis_contain_exact_energy": all(row["pilot_ci_contains_exact_energy"] for row in rows),
        "fci_denominator_beaten_count": sum(1 for row in rows if row["quantum_beats_fci_denominator"]),
        "sampled_confidence_intervals_included": True,
        "selected_ci_or_larger_active_space_included": False,
        "quantum_advantage_claimed": False,
        "reaction_dynamics_solution_claimed": False,
    }
    report = {
        "benchmark_id": "B3",
        "problem_id": 49,
        "title": "B3 sampled Pauli-estimator confidence intervals",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "sampled_pauli_estimator_confidence_intervals_not_advantage_claim",
        "method": "b3_sampled_pauli_estimator_confidence_v0",
        "dependency_benchmark": "B3",
        "source_mapper": str(mapper_path),
        "source_mapper_method": mapper.get("method"),
        "source_fci_reference": str(fci_path),
        "source_fci_method": fci.get("method"),
        "random_seed": SEED,
        "summary": summary,
        "rows": rows,
        "claim_boundary": [
            "Supported: reproducible pilot Pauli-estimator confidence intervals for four B3 Hamiltonian-mapped rows.",
            "Supported: Neyman-style target shot floors replacing the previous coefficient-squared upper-bound floor for Hartree-Fock bitstring measurements.",
            "Not supported: selected-CI scaling, larger active-space denominators, quantum advantage, chemistry accuracy, or complete reaction dynamics.",
        ],
        "next_steps": [
            "Replace Hartree-Fock bitstring expectations with ansatz or adiabatic state-preparation samples.",
            "Attach selected-CI or larger-active-space denominators to the same coordinates.",
            "Group commuting Pauli terms instead of measuring each random Pauli independently.",
            "Only promote if preparation, grouped measurement, and strong denominator costs are all beaten at fixed observable error.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "sampled_pauli_estimator_confidence_intervals_not_advantage_claim":
        errors.append("status must remain a sampled-confidence artifact, not an advantage claim")
    if report.get("method") != "b3_sampled_pauli_estimator_confidence_v0":
        errors.append("method mismatch")
    if report.get("dependency_benchmark") != "B3":
        errors.append("dependency_benchmark must be B3")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("expected four reaction-coordinate instances")
    if summary.get("sampled_confidence_intervals_included") is not True:
        errors.append("sampled confidence intervals must be included")
    if summary.get("selected_ci_or_larger_active_space_included") is not False:
        errors.append("selected-CI/larger-active-space denominator should remain false in this artifact")
    if summary.get("fci_denominator_beaten_count") != 0:
        errors.append("must not claim FCI denominator wins")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction dynamics solution")
    if summary.get("max_target_total_shot_floor_neyman", 0) <= 0:
        errors.append("target shot floor must be positive")
    for row in report.get("rows", []):
        if row.get("random_pauli_terms", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no random Pauli terms")
        if row.get("pilot_total_shots", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no pilot samples")
        if row.get("target_total_shot_floor_neyman", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no target shot floor")
        if row.get("quantum_beats_fci_denominator") is not False:
            errors.append(f"{row.get('molecule')} must not claim FCI win")
        if row.get("pilot_ci_half_width_hartree", 0.0) <= 0.0:
            errors.append(f"{row.get('molecule')} has no pilot confidence interval")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# B3 Sampled Pauli Estimator Confidence Intervals v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source mapper method: {report['source_mapper_method']}",
        f"- Source FCI method: {report['source_fci_method']}",
        f"- Instances: {report['summary']['instance_count']}",
        f"- Pilot shots per random Pauli term: {report['summary']['pilot_shots_per_random_term']}",
        f"- Max random Pauli terms: {report['summary']['max_random_pauli_terms']}",
        f"- Max pilot total shots: {report['summary']['max_pilot_total_shots']}",
        f"- Max target shot floor (Neyman): {report['summary']['max_target_total_shot_floor_neyman']}",
        f"- Max previous upper-bound shot floor: {report['summary']['max_previous_total_shot_floor_upper_bound']}",
        f"- Shot reduction range vs upper bound: {report['summary']['min_shot_reduction_vs_upper_bound']:.3f}x-{report['summary']['max_shot_reduction_vs_upper_bound']:.3f}x",
        f"- All pilot CIs contain exact HF energy: {report['summary']['all_pilot_cis_contain_exact_energy']}",
        f"- FCI denominator beaten count: {report['summary']['fci_denominator_beaten_count']}",
        f"- Quantum advantage claimed: {report['summary']['quantum_advantage_claimed']}",
        f"- Reaction-dynamics solution claimed: {report['summary']['reaction_dynamics_solution_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Rows",
        "",
        "| molecule | random terms | pilot shots | pilot abs error | CI half-width | target shots | previous floor | reduction | beats FCI? |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['molecule']} | {row['random_pauli_terms']} | {row['pilot_total_shots']} | "
            f"{row['pilot_abs_error_hartree']:.6e} | {row['pilot_ci_half_width_hartree']:.6e} | "
            f"{row['target_total_shot_floor_neyman']} | {row['previous_total_shot_floor_upper_bound']} | "
            f"{row['shot_reduction_vs_upper_bound']:.3f}x | {row['quantum_beats_fci_denominator']} |"
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
        "--mapper",
        type=Path,
        default=Path("results/B3_hamiltonian_pauli_mapper_comparison_v0.json"),
    )
    parser.add_argument(
        "--fci-reference",
        type=Path,
        default=Path("results/B10_t1_d5_b3_fci_reference_table_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_sampled_pauli_estimator_confidence_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_sampled_pauli_estimator_confidence.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.mapper, args.fci_reference)
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
                    "max_random_pauli_terms": report["summary"]["max_random_pauli_terms"],
                    "max_target_shot_floor_neyman": report["summary"][
                        "max_target_total_shot_floor_neyman"
                    ],
                    "shot_reduction_range": [
                        report["summary"]["min_shot_reduction_vs_upper_bound"],
                        report["summary"]["max_shot_reduction_vs_upper_bound"],
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
