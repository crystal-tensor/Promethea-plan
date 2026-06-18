#!/usr/bin/env python3
"""Propagate QWC grouped-observable covariance for B3 larger-basis Hamiltonians."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

from b3_hamiltonian_pauli_mapper_comparison import mapped_pauli_terms
from b3_larger_basis_hamiltonian_mapper import ANZATZ_LAYERS, target_error


STATUS = "grouped_covariance_shot_floor_boundary_not_advantage_claim"
METHOD = "b3_grouped_covariance_shot_floor_v0"
QWC_ALGORITHM = "bitmask_first_fit_qwc_cover_weight_ascending"


Term = dict[str, Any]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def occupied_label_mask(qubits: int, occupied_qubits: int) -> int:
    mask = 0
    for qidx in range(min(qubits, occupied_qubits)):
        mask |= 1 << (qubits - 1 - qidx)
    return mask


def pauli_masks(pauli_label: str) -> tuple[int, int, int, int, str]:
    x_mask = 0
    y_mask = 0
    z_mask = 0
    weight = 0
    for idx, ch in enumerate(pauli_label):
        bit = 1 << idx
        if ch == "X":
            x_mask |= bit
            weight += 1
        elif ch == "Y":
            y_mask |= bit
            weight += 1
        elif ch == "Z":
            z_mask |= bit
            weight += 1
    return x_mask, y_mask, z_mask, weight, pauli_label


def hf_expectation_from_masks(
    x_mask: int,
    y_mask: int,
    z_mask: int,
    occupied_mask: int,
) -> float:
    if x_mask or y_mask:
        return 0.0
    return -1.0 if (z_mask & occupied_mask).bit_count() % 2 else 1.0


def masks_compatible(term: Term, group: Term) -> bool:
    return not (
        (term["x_mask"] & (group["y_mask"] | group["z_mask"]))
        or (term["y_mask"] & (group["x_mask"] | group["z_mask"]))
        or (term["z_mask"] & (group["x_mask"] | group["y_mask"]))
    )


def merge_group_masks(group: Term, term: Term) -> None:
    group["x_mask"] |= term["x_mask"]
    group["y_mask"] |= term["y_mask"]
    group["z_mask"] |= term["z_mask"]
    group["basis_weight"] = (group["x_mask"] | group["y_mask"] | group["z_mask"]).bit_count()


def grouped_qwc_cover(random_terms: list[Term]) -> dict[str, Any]:
    started = time.perf_counter()
    sorted_terms = sorted(random_terms, key=lambda item: (item["weight"], item["pauli"]))
    groups: list[Term] = []
    for term in sorted_terms:
        best_index = -1
        best_size = -1
        for idx, group in enumerate(groups):
            if len(group["terms"]) > best_size and masks_compatible(term, group):
                best_index = idx
                best_size = len(group["terms"])
        if best_index < 0:
            groups.append(
                {
                    "x_mask": term["x_mask"],
                    "y_mask": term["y_mask"],
                    "z_mask": term["z_mask"],
                    "basis_weight": term["weight"],
                    "representative_pauli": term["pauli"],
                    "terms": [term],
                }
            )
        else:
            group = groups[best_index]
            merge_group_masks(group, term)
            group["terms"].append(term)
    return {
        "groups": groups,
        "qwc_group_count": len(groups),
        "qwc_grouping_wall_time_seconds": time.perf_counter() - started,
    }


def group_variance(group: Term, occupied_mask: int) -> dict[str, Any]:
    terms = group["terms"]
    coefficient_l1 = sum(abs(float(term["coefficient"])) for term in terms)
    coefficient_l2_sq = sum(float(term["coefficient"]) ** 2 for term in terms)
    covariance_shift = 0.0
    nonzero_covariance_pairs = 0
    negative_covariance_pairs = 0
    positive_covariance_pairs = 0
    for left_idx, left in enumerate(terms):
        left_coeff = float(left["coefficient"])
        left_expectation = float(left["expectation"])
        for right in terms[left_idx + 1 :]:
            right_coeff = float(right["coefficient"])
            right_expectation = float(right["expectation"])
            product_x = left["x_mask"] ^ right["x_mask"]
            product_y = left["y_mask"] ^ right["y_mask"]
            product_z = left["z_mask"] ^ right["z_mask"]
            product_expectation = hf_expectation_from_masks(
                product_x,
                product_y,
                product_z,
                occupied_mask,
            )
            covariance = product_expectation - left_expectation * right_expectation
            if covariance:
                contribution = 2.0 * left_coeff * right_coeff * covariance
                covariance_shift += contribution
                nonzero_covariance_pairs += 1
                if contribution < 0.0:
                    negative_covariance_pairs += 1
                elif contribution > 0.0:
                    positive_covariance_pairs += 1
    raw_variance = coefficient_l2_sq + covariance_shift
    variance = max(0.0, raw_variance)
    return {
        "size": len(terms),
        "basis_weight": group["basis_weight"],
        "representative_pauli": group["representative_pauli"],
        "coefficient_l1": coefficient_l1,
        "coefficient_l2_sq": coefficient_l2_sq,
        "covariance_shift": covariance_shift,
        "raw_group_variance": raw_variance,
        "group_variance": variance,
        "sqrt_group_variance": math.sqrt(variance),
        "nonzero_covariance_pairs": nonzero_covariance_pairs,
        "negative_covariance_pairs": negative_covariance_pairs,
        "positive_covariance_pairs": positive_covariance_pairs,
    }


def size_histogram(sizes: list[int]) -> dict[str, int]:
    histogram: dict[str, int] = {}
    for size in sizes:
        key = str(size if size < 10 else f"{10 * (size // 10)}-{10 * (size // 10) + 9}")
        histogram[key] = histogram.get(key, 0) + 1
    return dict(sorted(histogram.items(), key=lambda item: item[0]))


def build_random_terms(terms: list[dict[str, Any]], occupied: int, qubits: int) -> tuple[list[Term], int]:
    occupied_mask = occupied_label_mask(qubits, occupied)
    random_terms: list[Term] = []
    deterministic_terms = 0
    for term in terms:
        x_mask, y_mask, z_mask, weight, label = pauli_masks(str(term["pauli"]))
        expectation = hf_expectation_from_masks(x_mask, y_mask, z_mask, occupied_mask)
        variance = 1.0 - expectation * expectation
        if variance > 0.0:
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
        else:
            deterministic_terms += 1
    return random_terms, deterministic_terms


def covariance_metrics(random_terms: list[Term], cover: dict[str, Any], epsilon: float, occupied_mask: int) -> dict[str, Any]:
    group_metrics = [group_variance(group, occupied_mask) for group in cover["groups"]]
    independent_l1 = sum(abs(float(term["coefficient"])) for term in random_terms)
    independent_l2_sq = sum(float(term["coefficient"]) ** 2 for term in random_terms)
    sqrt_variance_sum = sum(item["sqrt_group_variance"] for item in group_metrics)
    grouped_floor = int(math.ceil((sqrt_variance_sum / epsilon) ** 2)) if group_metrics else 0
    independent_floor = int(math.ceil((independent_l1 / epsilon) ** 2)) if random_terms else 0
    positive_groups = sum(1 for item in group_metrics if item["group_variance"] > 0.0)
    covariance_shift_total = sum(item["covariance_shift"] for item in group_metrics)
    nonzero_covariance_pairs = sum(item["nonzero_covariance_pairs"] for item in group_metrics)
    negative_covariance_pairs = sum(item["negative_covariance_pairs"] for item in group_metrics)
    positive_covariance_pairs = sum(item["positive_covariance_pairs"] for item in group_metrics)
    top_by_variance = sorted(
        group_metrics,
        key=lambda item: (-item["group_variance"], -item["size"], item["representative_pauli"]),
    )[:12]
    top_by_covariance_abs = sorted(
        group_metrics,
        key=lambda item: (-abs(item["covariance_shift"]), -item["size"], item["representative_pauli"]),
    )[:12]
    return {
        "covariance_model": "exact_HF_product_state_covariance_inside_each_QWC_group",
        "independent_term_neyman_shot_floor": independent_floor,
        "independent_term_l1_norm": independent_l1,
        "independent_term_l2_sq": independent_l2_sq,
        "grouped_covariance_sqrt_variance_sum": sqrt_variance_sum,
        "grouped_covariance_shot_floor": grouped_floor,
        "positive_variance_group_count": positive_groups,
        "zero_variance_group_count": len(group_metrics) - positive_groups,
        "grouped_covariance_reduction_vs_independent_terms": (
            independent_floor / grouped_floor if grouped_floor else math.inf
        ),
        "covariance_shift_total": covariance_shift_total,
        "nonzero_covariance_pair_count": nonzero_covariance_pairs,
        "negative_covariance_pair_count": negative_covariance_pairs,
        "positive_covariance_pair_count": positive_covariance_pairs,
        "group_size_histogram": size_histogram([item["size"] for item in group_metrics]),
        "top_groups_by_variance": top_by_variance,
        "top_groups_by_covariance_abs": top_by_covariance_abs,
    }


def build_report(mapper_path: Path, qwc_path: Path) -> dict[str, Any]:
    mapper = load_json(mapper_path)
    qwc = load_json(qwc_path)
    qwc_by_molecule = {row["molecule"]: row for row in qwc.get("rows", [])}
    rows = []
    for source_row in mapper.get("rows", []):
        molecule = source_row["molecule"]
        basis = source_row["selected_ci_basis"]
        coordinate_center = float(source_row["coordinate_center"])
        derivative = float(source_row["selected_ci_derivative_hartree_per_coordinate"])
        started = time.perf_counter()
        qubits, _particles, terms = mapped_pauli_terms(
            molecule=molecule,
            coordinate_center=coordinate_center,
            basis=basis,
        )
        mapping_wall_time = time.perf_counter() - started
        occupied = min(int(source_row["electrons"]), qubits)
        random_terms, deterministic_terms = build_random_terms(terms, occupied, qubits)
        cover = grouped_qwc_cover(random_terms)
        occupied_mask = occupied_label_mask(qubits, occupied)
        epsilon = target_error(derivative)
        cov = covariance_metrics(random_terms, cover, epsilon, occupied_mask)
        qwc_row = qwc_by_molecule[molecule]
        two_qubit_per_shot = max(0, 2 * (qubits - 1) * ANZATZ_LAYERS)
        grouped_ansatz_executions = cov["grouped_covariance_shot_floor"] * two_qubit_per_shot
        selected_ci_denominator_beaten = False
        rows.append(
            {
                "source_benchmark": "B3",
                "molecule": molecule,
                "coordinate": source_row["coordinate"],
                "coordinate_center": coordinate_center,
                "selected_ci_basis": basis,
                "mapper_method": mapper.get("method"),
                "source_qwc_method": qwc.get("method"),
                "larger_basis_quantum_mapper_included": True,
                "qwc_grouping_included": True,
                "grouped_covariance_included": True,
                "total_qubits": qubits,
                "pauli_terms_after_cutoff": len(terms),
                "deterministic_pauli_terms": deterministic_terms,
                "random_pauli_terms": len(random_terms),
                "qwc_group_count": cover["qwc_group_count"],
                "source_qwc_group_count": qwc_row["qwc_group_count"],
                "qwc_group_count_matches_source": cover["qwc_group_count"] == qwc_row["qwc_group_count"],
                "qwc_grouping_algorithm": QWC_ALGORITHM,
                "qwc_grouping_wall_time_seconds": cover["qwc_grouping_wall_time_seconds"],
                "mapping_wall_time_seconds": mapping_wall_time,
                "target_observable_error_hartree_per_coordinate": epsilon,
                "previous_independent_term_neyman_shot_floor": qwc_row["neyman_target_total_shot_floor"],
                "grouped_covariance_shot_floor": cov["grouped_covariance_shot_floor"],
                "grouped_covariance_reduction_vs_previous_independent_floor": (
                    qwc_row["neyman_target_total_shot_floor"] / cov["grouped_covariance_shot_floor"]
                    if cov["grouped_covariance_shot_floor"]
                    else math.inf
                ),
                "grouped_covariance_reduction_vs_recomputed_independent_floor": cov[
                    "grouped_covariance_reduction_vs_independent_terms"
                ],
                "grouped_covariance_sqrt_variance_sum": cov["grouped_covariance_sqrt_variance_sum"],
                "independent_term_l1_norm": cov["independent_term_l1_norm"],
                "independent_term_l2_sq": cov["independent_term_l2_sq"],
                "covariance_shift_total": cov["covariance_shift_total"],
                "nonzero_covariance_pair_count": cov["nonzero_covariance_pair_count"],
                "negative_covariance_pair_count": cov["negative_covariance_pair_count"],
                "positive_covariance_pair_count": cov["positive_covariance_pair_count"],
                "positive_variance_group_count": cov["positive_variance_group_count"],
                "zero_variance_group_count": cov["zero_variance_group_count"],
                "group_size_histogram": cov["group_size_histogram"],
                "top_groups_by_variance": cov["top_groups_by_variance"],
                "top_groups_by_covariance_abs": cov["top_groups_by_covariance_abs"],
                "ansatz_model": "two-layer nearest-neighbor hardware-efficient preparation surcharge",
                "ansatz_two_qubit_gates_per_shot": two_qubit_per_shot,
                "ansatz_two_qubit_gate_executions_at_grouped_covariance_target": grouped_ansatz_executions,
                "selected_ci_larger_basis_denominator_beaten": selected_ci_denominator_beaten,
                "comparison_interpretation": (
                    "QWC grouping is now propagated through an exact Hartree-Fock product-state covariance "
                    "model for grouped observables. This can reduce the measurement shot floor, but the "
                    "generic ansatz surcharge and lack of correlated-state covariance still block an "
                    "advantage claim."
                ),
            }
        )

    summary = {
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "larger_basis_quantum_mapper_included": True,
        "qwc_grouping_included": True,
        "qwc_grouping_algorithm": QWC_ALGORITHM,
        "grouped_covariance_included": True,
        "covariance_model": "exact_HF_product_state_covariance_inside_each_QWC_group",
        "max_total_qubits": max(row["total_qubits"] for row in rows),
        "max_pauli_terms_after_cutoff": max(row["pauli_terms_after_cutoff"] for row in rows),
        "max_qwc_group_count": max(row["qwc_group_count"] for row in rows),
        "max_previous_independent_term_neyman_shot_floor": max(
            row["previous_independent_term_neyman_shot_floor"] for row in rows
        ),
        "max_grouped_covariance_shot_floor": max(
            row["grouped_covariance_shot_floor"] for row in rows
        ),
        "min_grouped_covariance_reduction_vs_previous_independent_floor": min(
            row["grouped_covariance_reduction_vs_previous_independent_floor"] for row in rows
        ),
        "max_grouped_covariance_reduction_vs_previous_independent_floor": max(
            row["grouped_covariance_reduction_vs_previous_independent_floor"] for row in rows
        ),
        "max_covariance_shift_total": max(row["covariance_shift_total"] for row in rows),
        "min_covariance_shift_total": min(row["covariance_shift_total"] for row in rows),
        "max_nonzero_covariance_pair_count": max(row["nonzero_covariance_pair_count"] for row in rows),
        "max_ansatz_two_qubit_gate_executions_at_grouped_covariance_target": max(
            row["ansatz_two_qubit_gate_executions_at_grouped_covariance_target"] for row in rows
        ),
        "selected_ci_larger_basis_denominator_beaten_count": sum(
            1 for row in rows if row["selected_ci_larger_basis_denominator_beaten"]
        ),
        "quantum_advantage_claimed": False,
        "reaction_dynamics_solution_claimed": False,
    }
    report = {
        "benchmark_id": "B3",
        "problem_id": 49,
        "title": "B3 grouped covariance shot-floor boundary",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": STATUS,
        "method": METHOD,
        "dependency_benchmark": "B3",
        "source_larger_basis_mapper": str(mapper_path),
        "source_larger_basis_mapper_method": mapper.get("method"),
        "source_larger_basis_qwc_grouping": str(qwc_path),
        "source_larger_basis_qwc_grouping_method": qwc.get("method"),
        "summary": summary,
        "rows": rows,
        "claim_boundary": [
            "Supported: grouped-observable covariance propagation for the four larger-basis B3 QWC Hamiltonian covers under a Hartree-Fock product-state measurement model.",
            "Supported: group-level Neyman shot-floor estimates using N=(sum_g sqrt(Var_g)/epsilon)^2.",
            "Not supported: correlated chemical-state covariance, UCC/ADAPT/adiabatic preparation, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.",
        ],
        "next_steps": [
            "Replace the Hartree-Fock covariance model with sampled covariance from UCC, ADAPT-VQE, or adiabatic state-preparation states.",
            "Propagate grouped observable covariance through three-point reaction-coordinate derivatives rather than per-coordinate Hamiltonian energy only.",
            "Retest against stricter selected-CI, DMRG, or tensor-network denominators at fixed observable error.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain a grouped-covariance boundary")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("expected four B3 rows")
    if summary.get("larger_basis_quantum_mapper_included") is not True:
        errors.append("larger-basis mapper must be included")
    if summary.get("qwc_grouping_included") is not True:
        errors.append("QWC grouping must be included")
    if summary.get("grouped_covariance_included") is not True:
        errors.append("grouped covariance must be included")
    if summary.get("min_grouped_covariance_reduction_vs_previous_independent_floor", 0.0) <= 1.0:
        errors.append("grouped covariance must reduce every independent-term shot floor")
    if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
        errors.append("must not claim selected-CI denominator wins")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction dynamics solution")
    for row in report.get("rows", []):
        if row.get("qwc_group_count", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no QWC groups")
        if row.get("qwc_group_count_matches_source") is not True:
            errors.append(f"{row.get('molecule')} QWC regrouping differs from source")
        if row.get("grouped_covariance_shot_floor", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no grouped covariance shot floor")
        if row.get("grouped_covariance_reduction_vs_previous_independent_floor", 0.0) <= 1.0:
            errors.append(f"{row.get('molecule')} grouped covariance did not improve shot floor")
        if row.get("selected_ci_larger_basis_denominator_beaten") is not False:
            errors.append(f"{row.get('molecule')} must not claim denominator win")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# B3 Grouped Covariance Shot-Floor Boundary v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source mapper method: {report['source_larger_basis_mapper_method']}",
        f"- Source QWC method: {report['source_larger_basis_qwc_grouping_method']}",
        f"- Instances: {report['summary']['instance_count']}",
        f"- Covariance model: {report['summary']['covariance_model']}",
        f"- QWC grouping included: {report['summary']['qwc_grouping_included']}",
        f"- Grouped covariance included: {report['summary']['grouped_covariance_included']}",
        f"- Max total qubits: {report['summary']['max_total_qubits']}",
        f"- Max Pauli terms after cutoff: {report['summary']['max_pauli_terms_after_cutoff']}",
        f"- Max QWC group count: {report['summary']['max_qwc_group_count']}",
        f"- Max previous independent-term shot floor: {report['summary']['max_previous_independent_term_neyman_shot_floor']}",
        f"- Max grouped-covariance shot floor: {report['summary']['max_grouped_covariance_shot_floor']}",
        f"- Grouped-covariance reduction range: {report['summary']['min_grouped_covariance_reduction_vs_previous_independent_floor']:.3f}x-{report['summary']['max_grouped_covariance_reduction_vs_previous_independent_floor']:.3f}x",
        f"- Max nonzero covariance pairs: {report['summary']['max_nonzero_covariance_pair_count']}",
        f"- Max ansatz two-qubit executions at grouped-covariance target: {report['summary']['max_ansatz_two_qubit_gate_executions_at_grouped_covariance_target']}",
        f"- Selected-CI larger-basis denominator beaten count: {report['summary']['selected_ci_larger_basis_denominator_beaten_count']}",
        f"- Quantum advantage claimed: {report['summary']['quantum_advantage_claimed']}",
        f"- Reaction-dynamics solution claimed: {report['summary']['reaction_dynamics_solution_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Rows",
        "",
        "| molecule | basis | QWC groups | previous shots | grouped-cov shots | reduction | covariance pairs | ansatz 2q executions | beats denominator? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['molecule']} | {row['selected_ci_basis']} | {row['qwc_group_count']} | "
            f"{row['previous_independent_term_neyman_shot_floor']} | "
            f"{row['grouped_covariance_shot_floor']} | "
            f"{row['grouped_covariance_reduction_vs_previous_independent_floor']:.3f}x | "
            f"{row['nonzero_covariance_pair_count']} | "
            f"{row['ansatz_two_qubit_gate_executions_at_grouped_covariance_target']} | "
            f"{row['selected_ci_larger_basis_denominator_beaten']} |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.append(
        "This report turns the previous QWC measurement-setting reduction into an explicit grouped-observable "
        "variance calculation. The covariance model is still the Hartree-Fock product-state model used by "
        "the existing B3 Pauli estimators; it is useful for bounding measurement economics, but it is not "
        "a correlated chemical state-preparation result."
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
        default=Path("results/B3_larger_basis_hamiltonian_mapper_v0.json"),
    )
    parser.add_argument(
        "--qwc",
        type=Path,
        default=Path("results/B3_larger_basis_qwc_grouping_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_grouped_covariance_shot_floor_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_grouped_covariance_shot_floor.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.mapper, args.qwc)
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
                    "max_grouped_covariance_shot_floor": report["summary"][
                        "max_grouped_covariance_shot_floor"
                    ],
                    "grouped_covariance_reduction_range": [
                        report["summary"][
                            "min_grouped_covariance_reduction_vs_previous_independent_floor"
                        ],
                        report["summary"][
                            "max_grouped_covariance_reduction_vs_previous_independent_floor"
                        ],
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
