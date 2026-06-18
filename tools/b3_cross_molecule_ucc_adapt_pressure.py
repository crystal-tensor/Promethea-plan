#!/usr/bin/env python3
"""Cross-molecule pressure test for the B3 compiled UCC/ADAPT pilot."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np

from b3_compiled_ucc_adapt_covariance_pilot import (
    ANSATZ_THETA,
    build_ucc_terms,
    hf_mask,
    sample_group_observable,
    selected_double_excitation_mask,
    ucc_group_variance,
)
from b3_grouped_covariance_shot_floor import grouped_qwc_cover
from b3_hamiltonian_pauli_mapper_comparison import mapped_pauli_terms


STATUS = "cross_molecule_ucc_adapt_pressure_demote_boundary_not_advantage_claim"
METHOD = "b3_cross_molecule_ucc_adapt_pressure_v0"
SOURCE_DERIVATIVE_METHOD = "b3_chemical_state_prep_derivative_boundary_v0"
SOURCE_PILOT_METHOD = "b3_compiled_ucc_adapt_covariance_pilot_v0"
PILOT_GROUPS_PER_MOLECULE = 24
PILOT_SHOTS_PER_GROUP = 384
PILOT_MAX_BASIS_WEIGHT = 12
PILOT_MAX_TERMS_PER_MOLECULE = 96
OPTIMIZER_EVALUATION_MULTIPLIER = 37
SEED = 913057


Term = dict[str, Any]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def derivative_shot_floor(center_floor: int, delta: float) -> int:
    return int(math.ceil(center_floor / (delta * delta)))


def compiled_two_qubit_gates_per_preparation(qubits: int) -> int:
    return 8 * max(1, 2 * (qubits - 1))


def group_l2_proxy(group: Term) -> float:
    return sum(float(term["coefficient"]) ** 2 for term in group["terms"])


def sampled_pressure_for_row(
    source_row: dict[str, Any],
    grouped_row: dict[str, Any],
    rng: np.random.Generator,
) -> dict[str, Any]:
    molecule = source_row["molecule"]
    qubits, _particles, terms = mapped_pauli_terms(
        molecule=molecule,
        coordinate_center=float(source_row["coordinate_center"]),
        basis=source_row["selected_ci_basis"],
    )
    occupied = int(source_row["electrons"])
    hf = hf_mask(qubits, occupied)
    excited = selected_double_excitation_mask(qubits, occupied)
    determinants = {
        hf: math.cos(ANSATZ_THETA),
        excited: math.sin(ANSATZ_THETA),
    }
    started = time.perf_counter()
    random_terms = build_ucc_terms(terms, determinants, qubits)
    sample_terms = sorted(
        [term for term in random_terms if int(term["weight"]) <= PILOT_MAX_BASIS_WEIGHT],
        key=lambda term: (-float(term["coefficient"]) ** 2, -int(term["weight"]), term["pauli"]),
    )[:PILOT_MAX_TERMS_PER_MOLECULE]
    cover = grouped_qwc_cover(sample_terms)

    sampleable_indices = [
        idx
        for idx, group in enumerate(cover["groups"])
        if int(group["basis_weight"]) <= PILOT_MAX_BASIS_WEIGHT
    ]
    fallback_singleton_groups_used = False
    groups_for_sampling = cover["groups"]
    if not sampleable_indices:
        fallback_singleton_groups_used = True
        groups_for_sampling = [
            {
                "x_mask": term["x_mask"],
                "y_mask": term["y_mask"],
                "z_mask": term["z_mask"],
                "basis_weight": term["weight"],
                "representative_pauli": term["pauli"],
                "terms": [term],
            }
            for term in sample_terms
            if int(term["weight"]) <= PILOT_MAX_BASIS_WEIGHT
        ]
        sampleable_indices = list(range(len(groups_for_sampling)))
    chosen_indices = sorted(
        sampleable_indices,
        key=lambda idx: (
            -group_l2_proxy(groups_for_sampling[idx]),
            -len(groups_for_sampling[idx]["terms"]),
            groups_for_sampling[idx]["representative_pauli"],
        ),
    )[:PILOT_GROUPS_PER_MOLECULE]

    sampled_groups = []
    for idx in chosen_indices:
        group = groups_for_sampling[idx]
        exact = ucc_group_variance(group, determinants, qubits)
        sample = sample_group_observable(rng, group, determinants, qubits, PILOT_SHOTS_PER_GROUP)
        exact_variance = exact["group_variance"]
        sampled_groups.append(
            {
                "group_index": idx,
                "size": exact["size"],
                "basis_weight": sample["basis_weight"],
                "probability_support": sample["probability_support"],
                "exact_mean": exact["mean"],
                "sample_mean": sample["sample_mean"],
                "exact_variance": exact_variance,
                "sample_variance": sample["sample_variance"],
                "relative_variance_error": (
                    abs(sample["sample_variance"] - exact_variance) / exact_variance
                    if exact_variance > 0.0
                    else 0.0
                ),
                "nonzero_covariance_pairs": exact["nonzero_covariance_pairs"],
                "representative_pauli": exact["representative_pauli"],
            }
        )

    source_hf_center_floor = int(source_row["source_grouped_covariance_shot_floor"])
    delta = float(source_row["derivative_shot_floor"]["finite_difference_delta"])
    optimistic_derivative_floor = derivative_shot_floor(source_hf_center_floor, delta)
    prep_2q = compiled_two_qubit_gates_per_preparation(qubits)
    optimizer_loop_total_shots = optimistic_derivative_floor * OPTIMIZER_EVALUATION_MULTIPLIER
    optimizer_loop_two_qubit_executions = optimizer_loop_total_shots * prep_2q

    mean_relative_error = (
        sum(item["relative_variance_error"] for item in sampled_groups) / len(sampled_groups)
        if sampled_groups
        else math.inf
    )
    max_relative_error = (
        max(item["relative_variance_error"] for item in sampled_groups) if sampled_groups else math.inf
    )
    return {
        "source_benchmark": "B3",
        "molecule": molecule,
        "coordinate": source_row["coordinate"],
        "coordinate_center": source_row["coordinate_center"],
        "selected_ci_basis": source_row["selected_ci_basis"],
        "total_qubits": qubits,
        "electrons": occupied,
        "ansatz_model": "cross_molecule_one_parameter_ucc_double_adapt_seed_pressure",
        "ansatz_theta": ANSATZ_THETA,
        "converged_vqe_or_adapt_energy": False,
        "hf_determinant_mask": hf,
        "excited_determinant_mask": excited,
        "compiled_two_qubit_gates_per_preparation": prep_2q,
        "random_pauli_terms_under_compiled_state": len(random_terms),
        "source_hf_qwc_group_count": grouped_row["qwc_group_count"],
        "sample_subset_term_count": len(sample_terms),
        "sample_subset_qwc_group_count": cover["qwc_group_count"],
        "fallback_singleton_groups_used": fallback_singleton_groups_used,
        "sampleable_qwc_group_count": len(sampleable_indices),
        "pilot_sampled_covariance_included": True,
        "pilot_group_count": len(sampled_groups),
        "pilot_max_basis_weight": PILOT_MAX_BASIS_WEIGHT,
        "pilot_shots_per_group": PILOT_SHOTS_PER_GROUP,
        "pilot_total_group_measurement_shots": len(sampled_groups) * PILOT_SHOTS_PER_GROUP,
        "pilot_mean_relative_variance_error": mean_relative_error,
        "pilot_max_relative_variance_error": max_relative_error,
        "sampled_groups_preview": sampled_groups[:8],
        "full_compiled_state_covariance_computed": False,
        "full_compiled_state_covariance_reason": (
            "T-B3-011 pressure run samples a bounded high-coefficient QWC subset for every molecule; "
            "full cross-molecule QWC cover construction and compiled covariance are left for a future "
            "multi-parameter ansatz run."
        ),
        "source_hf_center_grouped_covariance_shot_floor": source_hf_center_floor,
        "source_hf_three_point_derivative_shot_floor": source_row["derivative_shot_floor"][
            "three_point_derivative_total_shot_floor"
        ],
        "optimistic_cross_molecule_derivative_shot_floor_lower_bound": optimistic_derivative_floor,
        "optimizer_evaluation_multiplier": OPTIMIZER_EVALUATION_MULTIPLIER,
        "optimizer_loop_total_shots_lower_bound": optimizer_loop_total_shots,
        "optimizer_loop_two_qubit_executions_lower_bound": optimizer_loop_two_qubit_executions,
        "candidate_beats_selected_ci_larger_basis_denominator": False,
        "pressure_wall_time_seconds": time.perf_counter() - started,
        "comparison_interpretation": (
            "This cross-molecule pressure test extends the sampled compiled-state covariance pilot "
            "to a bounded QWC subset. Even using the optimistic HF grouped-covariance derivative floor "
            "as the lower-bound shot budget, optimizer-loop costs remain prohibitive and no denominator "
            "win is claimed."
        ),
    }


def build_report(
    derivative_path: Path,
    grouped_path: Path,
    source_pilot_path: Path,
    json_seed: int,
) -> dict[str, Any]:
    derivative = load_json(derivative_path)
    grouped = load_json(grouped_path)
    source_pilot = load_json(source_pilot_path)
    grouped_by_molecule = {row["molecule"]: row for row in grouped.get("rows", [])}
    rng = np.random.default_rng(json_seed)
    rows = [
        sampled_pressure_for_row(row, grouped_by_molecule[row["molecule"]], rng)
        for row in derivative.get("rows", [])
    ]
    total_sampled_groups = sum(row["pilot_group_count"] for row in rows)
    total_pilot_shots = sum(row["pilot_total_group_measurement_shots"] for row in rows)
    max_optimizer_shots = max(row["optimizer_loop_total_shots_lower_bound"] for row in rows)
    max_optimizer_2q = max(row["optimizer_loop_two_qubit_executions_lower_bound"] for row in rows)
    max_relative_error = max(row["pilot_max_relative_variance_error"] for row in rows)
    mean_relative_error = sum(row["pilot_mean_relative_variance_error"] for row in rows) / len(rows)
    demotion_recommended = all(
        not row["candidate_beats_selected_ci_larger_basis_denominator"] for row in rows
    ) and max_optimizer_shots > 10**13

    summary = {
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "source_derivative_method": derivative.get("method"),
        "source_grouped_covariance_method": grouped.get("method"),
        "source_pilot_method": source_pilot.get("method"),
        "cross_molecule_pressure_included": True,
        "compiled_ucc_adapt_sampled_covariance_extended": True,
        "full_compiled_state_covariance_computed": False,
        "converged_vqe_or_adapt_energy": False,
        "ansatz_model": "cross_molecule_one_parameter_ucc_double_adapt_seed_pressure",
        "ansatz_parameter_count": 1,
        "pilot_groups_per_molecule": PILOT_GROUPS_PER_MOLECULE,
        "pilot_max_terms_per_molecule": PILOT_MAX_TERMS_PER_MOLECULE,
        "pilot_group_count_total": total_sampled_groups,
        "pilot_max_basis_weight": PILOT_MAX_BASIS_WEIGHT,
        "pilot_shots_per_group": PILOT_SHOTS_PER_GROUP,
        "pilot_total_group_measurement_shots": total_pilot_shots,
        "pilot_mean_relative_variance_error_across_molecules": mean_relative_error,
        "pilot_max_relative_variance_error_across_molecules": max_relative_error,
        "optimizer_loop_shot_accounting_included": True,
        "optimizer_evaluation_multiplier": OPTIMIZER_EVALUATION_MULTIPLIER,
        "max_optimizer_loop_total_shots_lower_bound": max_optimizer_shots,
        "max_optimizer_loop_two_qubit_executions_lower_bound": max_optimizer_2q,
        "selected_ci_larger_basis_denominator_beaten_count": 0,
        "demotion_recommended": demotion_recommended,
        "b3_status_recommendation": (
            "demote_to_negative_boundary_until_multi_parameter_state_prep_or_new_measurement_strategy"
            if demotion_recommended
            else "continue_with_stronger_multi_parameter_state_prep"
        ),
        "quantum_advantage_claimed": False,
        "reaction_dynamics_solution_claimed": False,
    }
    report = {
        "benchmark_id": "B3",
        "problem_id": 49,
        "title": "B3 cross-molecule UCC/ADAPT pressure and demotion boundary",
        "version": "0.1",
        "last_updated": "2026-06-18",
        "status": STATUS,
        "method": METHOD,
        "dependency_benchmark": "B3",
        "source_derivative_boundary": str(derivative_path),
        "source_derivative_boundary_method": derivative.get("method"),
        "source_grouped_covariance": str(grouped_path),
        "source_grouped_covariance_method": grouped.get("method"),
        "source_compiled_ucc_adapt_pilot": str(source_pilot_path),
        "source_compiled_ucc_adapt_pilot_method": source_pilot.get("method"),
        "summary": summary,
        "rows": rows,
        "claim_boundary": [
            "Supported: bounded high-coefficient sampled covariance pressure test on H2, LiH, H2O, and N2 using one-parameter compiled UCC-double / ADAPT-seed states.",
            "Supported: optimizer-loop lower-bound accounting using the source HF grouped-covariance derivative floors.",
            "Supported: a B3 demotion recommendation under the current one-parameter ansatz and QWC-only measurement strategy.",
            "Not supported: full cross-molecule QWC cover construction under the compiled state, full compiled covariance, converged UCCSD/ADAPT/VQE chemistry, all-group sampled covariance, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.",
        ],
        "next_steps": [
            "Demote B3 to a negative-boundary track unless a real multi-parameter UCCSD/ADAPT ansatz or stronger measurement strategy changes the denominator comparison.",
            "If continuing B3, require full covariance for at least one multi-parameter UCCSD/ADAPT state and a selected-CI/DMRG/tensor denominator comparison.",
            "Prioritize B5/B10 or B4/B8 if B3 remains optimizer-loop dominated after the next multi-parameter attempt.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain a demotion-boundary pressure test")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    if report.get("source_derivative_boundary_method") != SOURCE_DERIVATIVE_METHOD:
        errors.append("source derivative boundary method mismatch")
    if report.get("source_compiled_ucc_adapt_pilot_method") != SOURCE_PILOT_METHOD:
        errors.append("source compiled pilot method mismatch")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("cross-molecule pressure test must cover four B3 rows")
    if summary.get("compiled_ucc_adapt_sampled_covariance_extended") is not True:
        errors.append("sampled covariance extension must be present")
    if summary.get("full_compiled_state_covariance_computed") is not False:
        errors.append("must not claim full cross-molecule compiled covariance")
    if summary.get("converged_vqe_or_adapt_energy") is not False:
        errors.append("must not claim converged VQE/ADAPT")
    if summary.get("pilot_group_count_total", 0) <= 0:
        errors.append("must sample at least one group")
    if summary.get("pilot_max_basis_weight") != PILOT_MAX_BASIS_WEIGHT:
        errors.append("pilot basis cap mismatch")
    if summary.get("pilot_max_terms_per_molecule") != PILOT_MAX_TERMS_PER_MOLECULE:
        errors.append("pilot term cap mismatch")
    if summary.get("optimizer_loop_shot_accounting_included") is not True:
        errors.append("optimizer-loop accounting must be included")
    if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
        errors.append("must not claim denominator wins")
    if summary.get("demotion_recommended") is not True:
        errors.append("current cross-molecule pressure should recommend demotion")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction dynamics solution")
    for row in report.get("rows", []):
        if row.get("pilot_sampled_covariance_included") is not True:
            errors.append(f"{row.get('molecule')} lacks sampled covariance")
        if row.get("pilot_group_count", 0) <= 0:
            errors.append(f"{row.get('molecule')} sampled no groups")
        if row.get("full_compiled_state_covariance_computed") is not False:
            errors.append(f"{row.get('molecule')} must not claim full covariance")
        if row.get("optimizer_loop_total_shots_lower_bound", 0) <= row.get(
            "optimistic_cross_molecule_derivative_shot_floor_lower_bound", 0
        ):
            errors.append(f"{row.get('molecule')} lacks optimizer-loop overhead")
        if row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False:
            errors.append(f"{row.get('molecule')} must not claim denominator win")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("report should be validated before validation_errors are attached")
    return errors


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# B3 Cross-Molecule UCC/ADAPT Pressure and Demotion Boundary",
        "",
        f"- Status: `{report['status']}`",
        f"- Method: `{report['method']}`",
        f"- Source derivative boundary: `{report['source_derivative_boundary_method']}`",
        f"- Source grouped covariance: `{report['source_grouped_covariance_method']}`",
        f"- Source compiled pilot: `{report['source_compiled_ucc_adapt_pilot_method']}`",
        f"- Molecules: {summary['molecule_count']}",
        f"- Total sampled groups: {summary['pilot_group_count_total']}",
        f"- Pilot shots per group: {summary['pilot_shots_per_group']}",
        f"- Pilot basis cap: {summary['pilot_max_basis_weight']}",
        f"- Pilot max terms per molecule: {summary['pilot_max_terms_per_molecule']}",
        f"- Mean/max relative variance error across molecules: {summary['pilot_mean_relative_variance_error_across_molecules']:.6f} / {summary['pilot_max_relative_variance_error_across_molecules']:.6f}",
        f"- Max optimizer-loop shots lower bound: {summary['max_optimizer_loop_total_shots_lower_bound']}",
        f"- Max optimizer-loop 2Q executions lower bound: {summary['max_optimizer_loop_two_qubit_executions_lower_bound']}",
        f"- Demotion recommended: {summary['demotion_recommended']}",
        f"- Recommendation: `{summary['b3_status_recommendation']}`",
        "",
        "## Rows",
        "",
        "| Molecule | qubits | source QWC groups | subset terms | subset groups | sampled | mean err | max err | HF derivative floor | optimizer shots lower bound | optimizer 2Q lower bound | demote? |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| "
            f"{row['molecule']} | {row['total_qubits']} | {row['source_hf_qwc_group_count']} | "
            f"{row['sample_subset_term_count']} | {row['sample_subset_qwc_group_count']} | "
            f"{row['pilot_group_count']} | {row['pilot_mean_relative_variance_error']:.6f} | "
            f"{row['pilot_max_relative_variance_error']:.6f} | "
            f"{row['source_hf_three_point_derivative_shot_floor']} | "
            f"{row['optimizer_loop_total_shots_lower_bound']} | "
            f"{row['optimizer_loop_two_qubit_executions_lower_bound']} | yes |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            *[f"- {item}" for item in report["claim_boundary"]],
            "",
            "## Next Steps",
            "",
            *[f"- {item}" for item in report["next_steps"]],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--derivative",
        type=Path,
        default=Path("results/B3_chemical_state_prep_derivative_boundary_v0.json"),
    )
    parser.add_argument(
        "--source-pilot",
        type=Path,
        default=Path("results/B3_compiled_ucc_adapt_covariance_pilot_v0.json"),
    )
    parser.add_argument(
        "--grouped",
        type=Path,
        default=Path("results/B3_grouped_covariance_shot_floor_v0.json"),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("results/B3_cross_molecule_ucc_adapt_pressure_v0.json"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("research/B3_cross_molecule_ucc_adapt_pressure.md"),
    )
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.derivative, args.grouped, args.source_pilot, args.seed)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(report), encoding="utf-8")
    payload = {
        "status": report["status"],
        "instance_count": report["summary"]["instance_count"],
        "pilot_group_count_total": report["summary"]["pilot_group_count_total"],
        "pilot_max_relative_variance_error": report["summary"][
            "pilot_max_relative_variance_error_across_molecules"
        ],
        "max_optimizer_loop_total_shots_lower_bound": report["summary"][
            "max_optimizer_loop_total_shots_lower_bound"
        ],
        "demotion_recommended": report["summary"]["demotion_recommended"],
        "validation_error_count": len(report["validation_errors"]),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
