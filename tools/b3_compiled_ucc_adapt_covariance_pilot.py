#!/usr/bin/env python3
"""Pilot sampled covariance for a small compiled UCC/ADAPT-style B3 state."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np

from b3_grouped_covariance_shot_floor import grouped_qwc_cover, pauli_masks
from b3_hamiltonian_pauli_mapper_comparison import mapped_pauli_terms


STATUS = "compiled_ucc_adapt_covariance_pilot_not_advantage_claim"
METHOD = "b3_compiled_ucc_adapt_covariance_pilot_v0"
SOURCE_DERIVATIVE_METHOD = "b3_chemical_state_prep_derivative_boundary_v0"
MOLECULE = "h2_bond_stretch"
ANSATZ_THETA = 0.18
PILOT_GROUP_COUNT = 48
PILOT_SHOTS_PER_GROUP = 512
PILOT_MAX_BASIS_WEIGHT = 12
OPTIMIZER_ITERATIONS = 12
PARAMETER_SHIFT_EVALS_PER_ITERATION = 2
OBJECTIVE_EVALS_PER_ITERATION = 1
FINAL_EVALS = 1
SEED = 733215


Term = dict[str, Any]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def label_bit_for_qubit(qubits: int, qidx: int) -> int:
    return 1 << (qubits - 1 - qidx)


def hf_mask(qubits: int, occupied_qubits: int) -> int:
    mask = 0
    for qidx in range(min(qubits, occupied_qubits)):
        mask |= label_bit_for_qubit(qubits, qidx)
    return mask


def selected_double_excitation_mask(qubits: int, occupied_qubits: int) -> int:
    base = hf_mask(qubits, occupied_qubits)
    if occupied_qubits < 2 or qubits < 4:
        return base
    for qidx in [0, 1]:
        base &= ~label_bit_for_qubit(qubits, qidx)
    for qidx in [2, 3]:
        base |= label_bit_for_qubit(qubits, qidx)
    return base


def apply_pauli_masks(
    x_mask: int,
    y_mask: int,
    z_mask: int,
    state_mask: int,
    qubits: int,
) -> tuple[int, complex]:
    phase: complex = 1.0 + 0.0j
    output = state_mask
    for idx in range(qubits):
        bit = 1 << idx
        occupied = bool(output & bit)
        if z_mask & bit:
            if occupied:
                phase *= -1.0
        if y_mask & bit:
            phase *= -1.0j if occupied else 1.0j
            output ^= bit
        elif x_mask & bit:
            output ^= bit
    return output, phase


def two_determinant_expectation(
    x_mask: int,
    y_mask: int,
    z_mask: int,
    determinants: dict[int, float],
    qubits: int,
) -> float:
    value = 0.0 + 0.0j
    for ket, ket_amp in determinants.items():
        bra, phase = apply_pauli_masks(x_mask, y_mask, z_mask, ket, qubits)
        bra_amp = determinants.get(bra)
        if bra_amp is not None:
            value += bra_amp * ket_amp * phase
    if abs(value.imag) > 1.0e-9:
        raise ValueError(f"non-real Pauli expectation {value}")
    return float(value.real)


def build_ucc_terms(terms: list[dict[str, Any]], determinants: dict[int, float], qubits: int) -> list[Term]:
    random_terms: list[Term] = []
    for term in terms:
        x_mask, y_mask, z_mask, weight, label = pauli_masks(str(term["pauli"]))
        expectation = two_determinant_expectation(x_mask, y_mask, z_mask, determinants, qubits)
        variance = max(0.0, 1.0 - expectation * expectation)
        if variance > 1.0e-12:
            random_terms.append(
                {
                    "pauli": label,
                    "coefficient": float(term["coefficient"]),
                    "abs_coefficient": abs(float(term["coefficient"])),
                    "weight": weight,
                    "x_mask": x_mask,
                    "y_mask": y_mask,
                    "z_mask": z_mask,
                    "expectation": expectation,
                    "term_variance": variance,
                }
            )
    return random_terms


def ucc_group_variance(group: Term, determinants: dict[int, float], qubits: int) -> dict[str, Any]:
    terms = group["terms"]
    expectations = [
        two_determinant_expectation(term["x_mask"], term["y_mask"], term["z_mask"], determinants, qubits)
        for term in terms
    ]
    mean = sum(float(term["coefficient"]) * expectations[idx] for idx, term in enumerate(terms))
    second_moment = 0.0
    covariance_shift = 0.0
    nonzero_covariance_pairs = 0
    for left_idx, left in enumerate(terms):
        left_coeff = float(left["coefficient"])
        left_expectation = expectations[left_idx]
        second_moment += left_coeff * left_coeff
        for right_idx in range(left_idx + 1, len(terms)):
            right = terms[right_idx]
            right_coeff = float(right["coefficient"])
            product_x = left["x_mask"] ^ right["x_mask"]
            product_y = left["y_mask"] ^ right["y_mask"]
            product_z = left["z_mask"] ^ right["z_mask"]
            product_expectation = two_determinant_expectation(
                product_x,
                product_y,
                product_z,
                determinants,
                qubits,
            )
            pair_second = 2.0 * left_coeff * right_coeff * product_expectation
            second_moment += pair_second
            covariance = product_expectation - left_expectation * expectations[right_idx]
            if abs(covariance) > 1.0e-12:
                nonzero_covariance_pairs += 1
                covariance_shift += 2.0 * left_coeff * right_coeff * covariance
    variance = max(0.0, second_moment - mean * mean)
    return {
        "size": len(terms),
        "basis_weight": group["basis_weight"],
        "representative_pauli": group["representative_pauli"],
        "mean": mean,
        "group_variance": variance,
        "sqrt_group_variance": math.sqrt(variance),
        "covariance_shift": covariance_shift,
        "nonzero_covariance_pairs": nonzero_covariance_pairs,
    }


def measurement_basis(group: Term) -> list[tuple[int, str]]:
    basis = []
    occupied = group["x_mask"] | group["y_mask"] | group["z_mask"]
    idx = 0
    while occupied:
        if occupied & 1:
            bit = 1 << idx
            if group["x_mask"] & bit:
                basis.append((idx, "X"))
            elif group["y_mask"] & bit:
                basis.append((idx, "Y"))
            elif group["z_mask"] & bit:
                basis.append((idx, "Z"))
        occupied >>= 1
        idx += 1
    return basis


def single_basis_amplitude(basis: str, outcome_bit: int, state_bit: int) -> complex:
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    if basis == "Z":
        return 1.0 + 0.0j if outcome_bit == state_bit else 0.0 + 0.0j
    if basis == "X":
        return inv_sqrt2 if (outcome_bit == 0 or state_bit == 0) else -inv_sqrt2
    if basis == "Y":
        if outcome_bit == 0:
            return inv_sqrt2 if state_bit == 0 else -1.0j * inv_sqrt2
        return inv_sqrt2 if state_bit == 0 else 1.0j * inv_sqrt2
    raise ValueError(f"unknown basis {basis}")


def group_outcome_probabilities(
    group: Term,
    determinants: dict[int, float],
    qubits: int,
) -> tuple[list[tuple[int, str]], np.ndarray]:
    basis = measurement_basis(group)
    measured_mask = 0
    for idx, _kind in basis:
        measured_mask |= 1 << idx
    full_mask = (1 << qubits) - 1
    outside_mask = full_mask ^ measured_mask
    probabilities = np.zeros(1 << len(basis), dtype=float)
    det_items = list(determinants.items())
    for outcome in range(len(probabilities)):
        value = 0.0 + 0.0j
        for left_mask, left_amp in det_items:
            for right_mask, right_amp in det_items:
                if (left_mask & outside_mask) != (right_mask & outside_mask):
                    continue
                left_product = 1.0 + 0.0j
                right_product = 1.0 + 0.0j
                for pos, (idx, kind) in enumerate(basis):
                    outcome_bit = (outcome >> pos) & 1
                    left_bit = 1 if (left_mask & (1 << idx)) else 0
                    right_bit = 1 if (right_mask & (1 << idx)) else 0
                    left_product *= single_basis_amplitude(kind, outcome_bit, left_bit)
                    right_product *= single_basis_amplitude(kind, outcome_bit, right_bit)
                value += left_amp * right_amp * left_product * right_product.conjugate()
        probabilities[outcome] = max(0.0, float(value.real))
    total = float(probabilities.sum())
    if total <= 0.0:
        raise ValueError("measurement probabilities vanished")
    probabilities /= total
    return basis, probabilities


def term_outcome_mask(term: Term, basis: list[tuple[int, str]]) -> int:
    term_mask = term["x_mask"] | term["y_mask"] | term["z_mask"]
    mask = 0
    for pos, (idx, _kind) in enumerate(basis):
        if term_mask & (1 << idx):
            mask |= 1 << pos
    return mask


def sample_group_observable(
    rng: np.random.Generator,
    group: Term,
    determinants: dict[int, float],
    qubits: int,
    shots: int,
) -> dict[str, Any]:
    basis, probabilities = group_outcome_probabilities(group, determinants, qubits)
    outcomes = rng.choice(len(probabilities), size=shots, p=probabilities)
    term_masks = [term_outcome_mask(term, basis) for term in group["terms"]]
    coefficients = [float(term["coefficient"]) for term in group["terms"]]
    values = np.zeros(shots, dtype=float)
    for idx, outcome in enumerate(outcomes):
        total = 0.0
        for term_mask, coefficient in zip(term_masks, coefficients):
            parity = (outcome & term_mask).bit_count() % 2
            total += coefficient * (-1.0 if parity else 1.0)
        values[idx] = total
    return {
        "sample_mean": float(values.mean()),
        "sample_variance": float(values.var(ddof=1)) if shots > 1 else 0.0,
        "basis_weight": len(basis),
        "probability_support": int(np.count_nonzero(probabilities > 1.0e-12)),
    }


def derivative_shot_floor(center_floor: int, delta: float) -> int:
    return int(math.ceil(center_floor / (delta * delta)))


def optimizer_multiplier() -> int:
    return OPTIMIZER_ITERATIONS * (
        PARAMETER_SHIFT_EVALS_PER_ITERATION + OBJECTIVE_EVALS_PER_ITERATION
    ) + FINAL_EVALS


def build_report(
    derivative_path: Path,
    mapper_path: Path,
    json_seed: int,
) -> dict[str, Any]:
    derivative = load_json(derivative_path)
    mapper = load_json(mapper_path)
    source_row = next(row for row in derivative["rows"] if row["molecule"] == MOLECULE)
    mapper_row = next(row for row in mapper["rows"] if row["molecule"] == MOLECULE)
    qubits, _particles, terms = mapped_pauli_terms(
        molecule=MOLECULE,
        coordinate_center=float(source_row["coordinate_center"]),
        basis=source_row["selected_ci_basis"],
    )
    occupied = int(mapper_row["electrons"])
    hf = hf_mask(qubits, occupied)
    excited = selected_double_excitation_mask(qubits, occupied)
    determinants = {
        hf: math.cos(ANSATZ_THETA),
        excited: math.sin(ANSATZ_THETA),
    }
    started = time.perf_counter()
    random_terms = build_ucc_terms(terms, determinants, qubits)
    cover = grouped_qwc_cover(random_terms)
    group_metrics = [ucc_group_variance(group, determinants, qubits) for group in cover["groups"]]
    sqrt_variance_sum = sum(item["sqrt_group_variance"] for item in group_metrics)
    target_error = float(source_row["derivative_shot_floor"]["derivative_target_error_hartree_per_coordinate"])
    center_floor = int(math.ceil((sqrt_variance_sum / target_error) ** 2))
    delta = float(source_row["derivative_shot_floor"]["finite_difference_delta"])
    derivative_floor = derivative_shot_floor(center_floor, delta)
    optimizer_evaluation_multiplier = optimizer_multiplier()
    compiled_two_qubit_gates_per_preparation = 8 * max(1, 2 * (qubits - 1))
    derivative_prep_executions = derivative_floor * compiled_two_qubit_gates_per_preparation
    optimizer_loop_shots = derivative_floor * optimizer_evaluation_multiplier
    optimizer_loop_two_qubit_executions = optimizer_loop_shots * compiled_two_qubit_gates_per_preparation

    sampleable_indices = [
        idx for idx, group in enumerate(cover["groups"]) if int(group["basis_weight"]) <= PILOT_MAX_BASIS_WEIGHT
    ]
    top_indices = sorted(
        sampleable_indices,
        key=lambda idx: (-group_metrics[idx]["group_variance"], -group_metrics[idx]["size"]),
    )[:PILOT_GROUP_COUNT]
    rng = np.random.default_rng(json_seed)
    sampled_groups = []
    for idx in top_indices:
        sample = sample_group_observable(
            rng,
            cover["groups"][idx],
            determinants,
            qubits,
            PILOT_SHOTS_PER_GROUP,
        )
        exact_variance = group_metrics[idx]["group_variance"]
        sampled_groups.append(
            {
                "group_index": idx,
                "size": group_metrics[idx]["size"],
                "basis_weight": sample["basis_weight"],
                "probability_support": sample["probability_support"],
                "exact_mean": group_metrics[idx]["mean"],
                "sample_mean": sample["sample_mean"],
                "exact_variance": exact_variance,
                "sample_variance": sample["sample_variance"],
                "relative_variance_error": (
                    abs(sample["sample_variance"] - exact_variance) / exact_variance
                    if exact_variance > 0.0
                    else 0.0
                ),
                "nonzero_covariance_pairs": group_metrics[idx]["nonzero_covariance_pairs"],
                "representative_pauli": group_metrics[idx]["representative_pauli"],
            }
        )

    max_relative_error = max(item["relative_variance_error"] for item in sampled_groups)
    mean_relative_error = sum(item["relative_variance_error"] for item in sampled_groups) / len(sampled_groups)
    row = {
        "source_benchmark": "B3",
        "molecule": MOLECULE,
        "coordinate": source_row["coordinate"],
        "coordinate_center": source_row["coordinate_center"],
        "selected_ci_basis": source_row["selected_ci_basis"],
        "total_qubits": qubits,
        "electrons": occupied,
        "ansatz_model": "compiled_one_parameter_ucc_double_adapt_seed",
        "ansatz_theta": ANSATZ_THETA,
        "hf_determinant_mask": hf,
        "excited_determinant_mask": excited,
        "compiled_two_qubit_gates_per_preparation": compiled_two_qubit_gates_per_preparation,
        "random_pauli_terms_under_compiled_state": len(random_terms),
        "qwc_group_count_under_compiled_state": cover["qwc_group_count"],
        "target_error_hartree_per_coordinate": target_error,
        "compiled_state_center_grouped_covariance_shot_floor": center_floor,
        "source_hf_center_grouped_covariance_shot_floor": source_row[
            "source_grouped_covariance_shot_floor"
        ],
        "center_shot_floor_ratio_vs_hf_grouped_covariance": (
            center_floor / source_row["source_grouped_covariance_shot_floor"]
        ),
        "finite_difference_delta": delta,
        "compiled_state_three_point_derivative_shot_floor": derivative_floor,
        "source_hf_three_point_derivative_shot_floor": source_row["derivative_shot_floor"][
            "three_point_derivative_total_shot_floor"
        ],
        "derivative_shot_floor_ratio_vs_hf_boundary": (
            derivative_floor
            / source_row["derivative_shot_floor"]["three_point_derivative_total_shot_floor"]
        ),
        "optimizer_loop_model": "one_parameter_parameter_shift",
        "optimizer_iterations": OPTIMIZER_ITERATIONS,
        "optimizer_evaluation_multiplier": optimizer_evaluation_multiplier,
        "optimizer_loop_total_shots": optimizer_loop_shots,
        "derivative_target_two_qubit_executions": derivative_prep_executions,
        "optimizer_loop_two_qubit_executions": optimizer_loop_two_qubit_executions,
        "pilot_sampled_covariance_included": True,
        "pilot_group_count": len(sampled_groups),
        "pilot_max_basis_weight": PILOT_MAX_BASIS_WEIGHT,
        "pilot_shots_per_group": PILOT_SHOTS_PER_GROUP,
        "pilot_total_group_measurement_shots": len(sampled_groups) * PILOT_SHOTS_PER_GROUP,
        "pilot_mean_relative_variance_error": mean_relative_error,
        "pilot_max_relative_variance_error": max_relative_error,
        "sampled_groups": sampled_groups[:12],
        "full_sampled_group_count": len(sampled_groups),
        "candidate_beats_selected_ci_larger_basis_denominator": False,
        "comparison_interpretation": (
            "A real sampled covariance pilot is now attached to a small compiled one-parameter UCC/ADAPT "
            "seed state for H2/cc-pVDZ. The exact compiled-state covariance and optimizer-loop accounting "
            "remain far from a denominator win, and this is not a converged VQE or reaction-dynamics result."
        ),
    }
    summary = {
        "instance_count": 1,
        "source_derivative_method": derivative.get("method"),
        "molecule": MOLECULE,
        "compiled_ucc_adapt_covariance_included": True,
        "pilot_sampled_covariance_included": True,
        "optimizer_loop_shot_accounting_included": True,
        "converged_vqe_or_adapt_energy": False,
        "ansatz_model": row["ansatz_model"],
        "ansatz_parameter_count": 1,
        "pilot_group_count": row["pilot_group_count"],
        "pilot_max_basis_weight": PILOT_MAX_BASIS_WEIGHT,
        "pilot_shots_per_group": PILOT_SHOTS_PER_GROUP,
        "pilot_total_group_measurement_shots": row["pilot_total_group_measurement_shots"],
        "pilot_mean_relative_variance_error": mean_relative_error,
        "pilot_max_relative_variance_error": max_relative_error,
        "compiled_two_qubit_gates_per_preparation": compiled_two_qubit_gates_per_preparation,
        "compiled_state_center_grouped_covariance_shot_floor": center_floor,
        "source_hf_center_grouped_covariance_shot_floor": source_row[
            "source_grouped_covariance_shot_floor"
        ],
        "compiled_state_three_point_derivative_shot_floor": derivative_floor,
        "source_hf_three_point_derivative_shot_floor": source_row["derivative_shot_floor"][
            "three_point_derivative_total_shot_floor"
        ],
        "optimizer_evaluation_multiplier": optimizer_evaluation_multiplier,
        "optimizer_loop_total_shots": optimizer_loop_shots,
        "optimizer_loop_two_qubit_executions": optimizer_loop_two_qubit_executions,
        "selected_ci_larger_basis_denominator_beaten_count": 0,
        "quantum_advantage_claimed": False,
        "reaction_dynamics_solution_claimed": False,
        "wall_time_seconds": time.perf_counter() - started,
    }
    report = {
        "benchmark_id": "B3",
        "problem_id": 49,
        "title": "B3 compiled UCC/ADAPT covariance pilot",
        "version": "0.1",
        "last_updated": "2026-06-18",
        "status": STATUS,
        "method": METHOD,
        "dependency_benchmark": "B3",
        "source_derivative_boundary": str(derivative_path),
        "source_derivative_boundary_method": derivative.get("method"),
        "summary": summary,
        "rows": [row],
        "claim_boundary": [
            "Supported: one H2/cc-pVDZ compiled one-parameter UCC-double/ADAPT-seed covariance pilot.",
            "Supported: sampled covariance estimates for the top sampleable groups with basis weight <= 12, plus exact full-cover covariance and optimizer-loop shot accounting for that pilot state.",
            "Not supported: sampled covariance for every QWC group, converged UCC/ADAPT/VQE chemistry, sampled covariance for all B3 molecules, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.",
        ],
        "next_steps": [
            "Compile a real multi-parameter UCCSD or ADAPT circuit and repeat covariance sampling beyond the one-parameter seed.",
            "Extend the sampled covariance pilot from H2 to LiH/H2O/N2 or demote B3 if optimizer-loop costs remain prohibitive.",
            "Compare against stricter selected-CI, DMRG, or tensor-network denominators at derivative-level observable error.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain a compiled UCC/ADAPT covariance pilot")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    if report.get("source_derivative_boundary_method") != SOURCE_DERIVATIVE_METHOD:
        errors.append("source derivative boundary method changed")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 1:
        errors.append("T-B3-010 pilot should cover one small instance")
    if summary.get("compiled_ucc_adapt_covariance_included") is not True:
        errors.append("compiled UCC/ADAPT covariance must be included")
    if summary.get("pilot_sampled_covariance_included") is not True:
        errors.append("sampled covariance pilot must be included")
    if summary.get("optimizer_loop_shot_accounting_included") is not True:
        errors.append("optimizer-loop shot accounting must be included")
    if summary.get("converged_vqe_or_adapt_energy") is not False:
        errors.append("must not claim converged VQE/ADAPT energy")
    if summary.get("pilot_group_count", 0) <= 0:
        errors.append("pilot group count must be positive")
    if summary.get("pilot_max_basis_weight") != PILOT_MAX_BASIS_WEIGHT:
        errors.append("pilot max basis weight changed")
    if summary.get("pilot_max_relative_variance_error", 0.0) < 0.0:
        errors.append("pilot variance error must be nonnegative")
    if summary.get("optimizer_loop_total_shots", 0) <= summary.get(
        "compiled_state_three_point_derivative_shot_floor", 0
    ):
        errors.append("optimizer loop shots must exceed one final derivative estimate")
    if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
        errors.append("must not claim denominator wins")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction dynamics solution")
    for row in report.get("rows", []):
        if row.get("pilot_sampled_covariance_included") is not True:
            errors.append(f"{row.get('molecule')} lacks sampled covariance")
        if row.get("optimizer_loop_total_shots", 0) <= row.get(
            "compiled_state_three_point_derivative_shot_floor", 0
        ):
            errors.append(f"{row.get('molecule')} lacks optimizer-loop overhead")
        if row.get("candidate_beats_selected_ci_larger_basis_denominator") is not False:
            errors.append(f"{row.get('molecule')} must not claim denominator win")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    row = report["rows"][0]
    lines = [
        "# B3 Compiled UCC/ADAPT Covariance Pilot v0.1",
        "",
        "Last updated: 2026-06-18",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source derivative method: {report['source_derivative_boundary_method']}",
        f"- Molecule: {summary['molecule']}",
        f"- Ansatz model: {summary['ansatz_model']}",
        f"- Compiled UCC/ADAPT covariance included: {summary['compiled_ucc_adapt_covariance_included']}",
        f"- Pilot sampled covariance included: {summary['pilot_sampled_covariance_included']}",
        f"- Optimizer-loop shot accounting included: {summary['optimizer_loop_shot_accounting_included']}",
        f"- Converged VQE/ADAPT energy: {summary['converged_vqe_or_adapt_energy']}",
        f"- Pilot groups / max basis weight / shots per group: {summary['pilot_group_count']} / {summary['pilot_max_basis_weight']} / {summary['pilot_shots_per_group']}",
        f"- Pilot mean/max relative variance error: {summary['pilot_mean_relative_variance_error']:.3f} / {summary['pilot_max_relative_variance_error']:.3f}",
        f"- Compiled 2Q gates per preparation: {summary['compiled_two_qubit_gates_per_preparation']}",
        f"- Center grouped-covariance shot floor: {summary['compiled_state_center_grouped_covariance_shot_floor']}",
        f"- Three-point derivative shot floor: {summary['compiled_state_three_point_derivative_shot_floor']}",
        f"- Optimizer evaluation multiplier: {summary['optimizer_evaluation_multiplier']}",
        f"- Optimizer-loop total shots: {summary['optimizer_loop_total_shots']}",
        f"- Optimizer-loop 2Q executions: {summary['optimizer_loop_two_qubit_executions']}",
        f"- Selected-CI larger-basis denominator beaten count: {summary['selected_ci_larger_basis_denominator_beaten_count']}",
        f"- Quantum advantage claimed: {summary['quantum_advantage_claimed']}",
        f"- Reaction-dynamics solution claimed: {summary['reaction_dynamics_solution_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Pilot Row",
        "",
        "| molecule | basis | random terms | QWC groups | center shots | derivative shots | optimizer shots | prep 2Q | optimizer 2Q execs | beats denominator? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        (
            f"| {row['molecule']} | {row['selected_ci_basis']} | "
            f"{row['random_pauli_terms_under_compiled_state']} | "
            f"{row['qwc_group_count_under_compiled_state']} | "
            f"{row['compiled_state_center_grouped_covariance_shot_floor']} | "
            f"{row['compiled_state_three_point_derivative_shot_floor']} | "
            f"{row['optimizer_loop_total_shots']} | "
            f"{row['compiled_two_qubit_gates_per_preparation']} | "
            f"{row['optimizer_loop_two_qubit_executions']} | "
            f"{row['candidate_beats_selected_ci_larger_basis_denominator']} |"
        ),
        "",
        "## Sampled Group Preview",
        "",
        "| group | size | basis weight | exact variance | sample variance | rel error |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for item in row["sampled_groups"][:8]:
        lines.append(
            f"| {item['group_index']} | {item['size']} | {item['basis_weight']} | "
            f"{item['exact_variance']:.6e} | {item['sample_variance']:.6e} | "
            f"{item['relative_variance_error']:.3f} |"
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
        "--derivative-boundary",
        type=Path,
        default=Path("results/B3_chemical_state_prep_derivative_boundary_v0.json"),
    )
    parser.add_argument(
        "--mapper",
        type=Path,
        default=Path("results/B3_larger_basis_hamiltonian_mapper_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_compiled_ucc_adapt_covariance_pilot_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_compiled_ucc_adapt_covariance_pilot.md"),
    )
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.derivative_boundary, args.mapper, args.seed)
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
                    "molecule": report["summary"]["molecule"],
                    "pilot_group_count": report["summary"]["pilot_group_count"],
                    "pilot_max_basis_weight": report["summary"]["pilot_max_basis_weight"],
                    "pilot_max_relative_variance_error": report["summary"][
                        "pilot_max_relative_variance_error"
                    ],
                    "compiled_state_three_point_derivative_shot_floor": report["summary"][
                        "compiled_state_three_point_derivative_shot_floor"
                    ],
                    "optimizer_loop_total_shots": report["summary"]["optimizer_loop_total_shots"],
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
