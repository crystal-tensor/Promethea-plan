#!/usr/bin/env python3
"""Build a real QWC grouping cover for B3 larger-basis Pauli Hamiltonians."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

from b3_hamiltonian_pauli_mapper_comparison import mapped_pauli_terms
from b3_larger_basis_hamiltonian_mapper import ANZATZ_LAYERS, target_error
from b3_sampled_pauli_estimator_confidence import hf_pauli_expectation


STATUS = "larger_basis_qwc_grouping_boundary_not_advantage_claim"
METHOD = "b3_larger_basis_qwc_grouping_v0"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def masks_compatible(
    term: tuple[int, int, int, int, str],
    group: tuple[int, int, int, int, str],
) -> bool:
    term_x, term_y, term_z, _term_weight, _term_label = term
    group_x, group_y, group_z, _group_weight, _group_label = group
    return not (
        (term_x & (group_y | group_z))
        or (term_y & (group_x | group_z))
        or (term_z & (group_x | group_y))
    )


def merge_masks(
    term: tuple[int, int, int, int, str],
    group: tuple[int, int, int, int, str],
) -> tuple[int, int, int, int, str]:
    term_x, term_y, term_z, _term_weight, _term_label = term
    group_x, group_y, group_z, _group_weight, group_label = group
    merged_x = group_x | term_x
    merged_y = group_y | term_y
    merged_z = group_z | term_z
    return (
        merged_x,
        merged_y,
        merged_z,
        (merged_x | merged_y | merged_z).bit_count(),
        group_label,
    )


def greedy_qwc_cover(random_terms: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.perf_counter()
    terms = sorted(
        [pauli_masks(str(term["pauli"])) + (float(term["coefficient"]),) for term in random_terms],
        key=lambda item: (item[3], item[4]),
    )
    groups: list[tuple[int, int, int, int, str]] = []
    group_sizes: list[int] = []
    group_l1: list[float] = []
    for term_x, term_y, term_z, term_weight, term_label, coefficient in terms:
        term_masks = (term_x, term_y, term_z, term_weight, term_label)
        best_index = -1
        best_size = -1
        for idx, group in enumerate(groups):
            if group_sizes[idx] > best_size and masks_compatible(term_masks, group):
                best_index = idx
                best_size = group_sizes[idx]
        if best_index < 0:
            groups.append(term_masks)
            group_sizes.append(1)
            group_l1.append(abs(coefficient))
        else:
            groups[best_index] = merge_masks(term_masks, groups[best_index])
            group_sizes[best_index] += 1
            group_l1[best_index] += abs(coefficient)

    group_count = len(groups)
    size_histogram: dict[str, int] = {}
    for size in group_sizes:
        key = str(size if size < 10 else f"{10 * (size // 10)}-{10 * (size // 10) + 9}")
        size_histogram[key] = size_histogram.get(key, 0) + 1
    top_groups = sorted(
        [
            {
                "size": group_sizes[idx],
                "basis_weight": groups[idx][3],
                "coefficient_l1": group_l1[idx],
                "representative_pauli": groups[idx][4],
            }
            for idx in range(group_count)
        ],
        key=lambda item: (-item["size"], -item["coefficient_l1"], item["representative_pauli"]),
    )[:12]
    return {
        "grouping_algorithm": "bitmask_first_fit_qwc_cover_weight_ascending",
        "qwc_group_count": group_count,
        "qwc_grouping_wall_time_seconds": time.perf_counter() - started,
        "qwc_reduction_vs_ungrouped_random_terms": len(random_terms) / group_count if group_count else math.inf,
        "max_group_size": max(group_sizes) if group_sizes else 0,
        "mean_group_size": (sum(group_sizes) / group_count) if group_count else 0.0,
        "max_group_coefficient_l1": max(group_l1) if group_l1 else 0.0,
        "group_size_histogram": dict(sorted(size_histogram.items(), key=lambda item: item[0])),
        "top_groups": top_groups,
    }


def build_report(mapper_path: Path) -> dict[str, Any]:
    mapper = load_json(mapper_path)
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
        random_terms = []
        deterministic_terms = 0
        random_coeff_l1 = 0.0
        for term in terms:
            expectation = hf_pauli_expectation(str(term["pauli"]), occupied)
            variance = 1.0 - expectation * expectation
            if variance > 0.0:
                random_terms.append(term)
                random_coeff_l1 += abs(float(term["coefficient"]))
            else:
                deterministic_terms += 1

        cover = greedy_qwc_cover(random_terms)
        epsilon = target_error(derivative)
        neyman_shot_floor = int(math.ceil((random_coeff_l1 / epsilon) ** 2)) if random_terms else 0
        two_qubit_per_shot = max(0, 2 * (qubits - 1) * ANZATZ_LAYERS)
        ansatz_executions = neyman_shot_floor * two_qubit_per_shot
        previous_bucket_count = int(source_row["measurement_model"]["conservative_same_basis_bucket_count"])
        rows.append(
            {
                "source_benchmark": "B3",
                "molecule": molecule,
                "coordinate": source_row["coordinate"],
                "coordinate_center": coordinate_center,
                "selected_ci_basis": basis,
                "mapper_method": mapper.get("method"),
                "larger_basis_quantum_mapper_included": True,
                "total_qubits": qubits,
                "pauli_terms_after_cutoff": len(terms),
                "deterministic_pauli_terms": deterministic_terms,
                "random_pauli_terms": len(random_terms),
                "previous_conservative_same_basis_bucket_count": previous_bucket_count,
                "qwc_group_count": cover["qwc_group_count"],
                "qwc_reduction_vs_previous_bucket_count": previous_bucket_count / cover["qwc_group_count"],
                "qwc_reduction_vs_ungrouped_random_terms": cover[
                    "qwc_reduction_vs_ungrouped_random_terms"
                ],
                "qwc_grouping_wall_time_seconds": cover["qwc_grouping_wall_time_seconds"],
                "mapping_wall_time_seconds": mapping_wall_time,
                "max_group_size": cover["max_group_size"],
                "mean_group_size": cover["mean_group_size"],
                "grouping_algorithm": cover["grouping_algorithm"],
                "group_size_histogram": cover["group_size_histogram"],
                "top_groups": cover["top_groups"],
                "target_observable_error_hartree_per_coordinate": epsilon,
                "neyman_target_total_shot_floor": neyman_shot_floor,
                "neyman_shot_floor_reduced_by_grouping": False,
                "shot_floor_note": (
                    "QWC grouping reduces the number of measurement settings. This v0 keeps the same "
                    "coefficient-L1 Neyman shot-floor upper bound because grouped observable covariance "
                    "is not yet propagated."
                ),
                "ansatz_model": "two-layer nearest-neighbor hardware-efficient preparation surcharge",
                "ansatz_two_qubit_gates_per_shot": two_qubit_per_shot,
                "ansatz_two_qubit_gate_executions_at_neyman_target": ansatz_executions,
                "selected_ci_larger_basis_denominator_beaten": False,
            }
        )

    summary = {
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "larger_basis_quantum_mapper_included": True,
        "qwc_grouping_included": True,
        "qwc_grouping_algorithm": "bitmask_first_fit_qwc_cover_weight_ascending",
        "max_total_qubits": max(row["total_qubits"] for row in rows),
        "max_pauli_terms_after_cutoff": max(row["pauli_terms_after_cutoff"] for row in rows),
        "max_previous_conservative_same_basis_bucket_count": max(
            row["previous_conservative_same_basis_bucket_count"] for row in rows
        ),
        "max_qwc_group_count": max(row["qwc_group_count"] for row in rows),
        "min_qwc_reduction_vs_previous_bucket_count": min(
            row["qwc_reduction_vs_previous_bucket_count"] for row in rows
        ),
        "max_qwc_reduction_vs_previous_bucket_count": max(
            row["qwc_reduction_vs_previous_bucket_count"] for row in rows
        ),
        "max_group_size": max(row["max_group_size"] for row in rows),
        "max_neyman_target_total_shot_floor": max(row["neyman_target_total_shot_floor"] for row in rows),
        "neyman_shot_floor_reduced_by_grouping": False,
        "max_ansatz_two_qubit_gate_executions_at_neyman_target": max(
            row["ansatz_two_qubit_gate_executions_at_neyman_target"] for row in rows
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
        "title": "B3 larger-basis QWC grouping boundary",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": STATUS,
        "method": METHOD,
        "dependency_benchmark": "B3",
        "source_larger_basis_mapper": str(mapper_path),
        "source_larger_basis_mapper_method": mapper.get("method"),
        "summary": summary,
        "rows": rows,
        "claim_boundary": [
            "Supported: actual qubit-wise commuting grouping covers for four larger-basis B3 Hamiltonians.",
            "Supported: measurement-setting reductions versus the previous same-basis bucket upper bound.",
            "Not supported: reduced shot floor from covariance propagation, chemical state preparation, selected-CI denominator wins, quantum advantage, or complete reaction dynamics.",
        ],
        "next_steps": [
            "Propagate grouped-observable covariance to decide whether shot floors actually decrease.",
            "Replace the generic two-layer ansatz surcharge with UCC, ADAPT-VQE, or adiabatic preparation costs.",
            "Retest against stricter selected-CI, DMRG, or tensor-network denominators at fixed observable error.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain a QWC grouping boundary")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("expected four B3 rows")
    if summary.get("larger_basis_quantum_mapper_included") is not True:
        errors.append("larger-basis mapper must be included")
    if summary.get("qwc_grouping_included") is not True:
        errors.append("QWC grouping must be included")
    if summary.get("min_qwc_reduction_vs_previous_bucket_count", 0.0) <= 1.0:
        errors.append("QWC grouping must reduce every previous bucket count")
    if summary.get("neyman_shot_floor_reduced_by_grouping") is not False:
        errors.append("must not claim shot-floor reduction from grouping without covariance propagation")
    if summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
        errors.append("must not claim selected-CI denominator wins")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction dynamics solution")
    for row in report.get("rows", []):
        if row.get("qwc_group_count", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no QWC groups")
        if row.get("qwc_group_count", 0) >= row.get("previous_conservative_same_basis_bucket_count", 0):
            errors.append(f"{row.get('molecule')} QWC group count did not improve")
        if row.get("neyman_shot_floor_reduced_by_grouping") is not False:
            errors.append(f"{row.get('molecule')} must not claim shot-floor reduction")
        if row.get("selected_ci_larger_basis_denominator_beaten") is not False:
            errors.append(f"{row.get('molecule')} must not claim denominator win")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# B3 Larger-Basis QWC Grouping Boundary v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source mapper method: {report['source_larger_basis_mapper_method']}",
        f"- Instances: {report['summary']['instance_count']}",
        f"- QWC grouping included: {report['summary']['qwc_grouping_included']}",
        f"- Algorithm: {report['summary']['qwc_grouping_algorithm']}",
        f"- Max total qubits: {report['summary']['max_total_qubits']}",
        f"- Max Pauli terms after cutoff: {report['summary']['max_pauli_terms_after_cutoff']}",
        f"- Max previous bucket count: {report['summary']['max_previous_conservative_same_basis_bucket_count']}",
        f"- Max QWC group count: {report['summary']['max_qwc_group_count']}",
        f"- QWC reduction range: {report['summary']['min_qwc_reduction_vs_previous_bucket_count']:.3f}x-{report['summary']['max_qwc_reduction_vs_previous_bucket_count']:.3f}x",
        f"- Max group size: {report['summary']['max_group_size']}",
        f"- Max Neyman target shot floor: {report['summary']['max_neyman_target_total_shot_floor']}",
        f"- Shot floor reduced by grouping: {report['summary']['neyman_shot_floor_reduced_by_grouping']}",
        f"- Max ansatz two-qubit executions at target: {report['summary']['max_ansatz_two_qubit_gate_executions_at_neyman_target']}",
        f"- Selected-CI larger-basis denominator beaten count: {report['summary']['selected_ci_larger_basis_denominator_beaten_count']}",
        f"- Quantum advantage claimed: {report['summary']['quantum_advantage_claimed']}",
        f"- Reaction-dynamics solution claimed: {report['summary']['reaction_dynamics_solution_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Rows",
        "",
        "| molecule | basis | random terms | previous buckets | QWC groups | reduction | max group | Neyman shots | ansatz 2q executions | beats denominator? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['molecule']} | {row['selected_ci_basis']} | {row['random_pauli_terms']} | "
            f"{row['previous_conservative_same_basis_bucket_count']} | {row['qwc_group_count']} | "
            f"{row['qwc_reduction_vs_previous_bucket_count']:.3f}x | {row['max_group_size']} | "
            f"{row['neyman_target_total_shot_floor']} | "
            f"{row['ansatz_two_qubit_gate_executions_at_neyman_target']} | "
            f"{row['selected_ci_larger_basis_denominator_beaten']} |"
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
        "--json-output",
        type=Path,
        default=Path("results/B3_larger_basis_qwc_grouping_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_larger_basis_qwc_grouping.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.mapper)
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
                    "max_qwc_group_count": report["summary"]["max_qwc_group_count"],
                    "qwc_reduction_range": [
                        report["summary"]["min_qwc_reduction_vs_previous_bucket_count"],
                        report["summary"]["max_qwc_reduction_vs_previous_bucket_count"],
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
