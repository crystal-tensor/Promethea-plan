#!/usr/bin/env python3
"""Same-hardware B2 schedule candidates with Wilson target-volume comparison.

This extends the B2 biased-schedule sweep by testing candidates that keep the
same rotated-surface-code distance, basis, physical qubit footprint, shot budget,
and PyMatching decoder, but reduce syndrome rounds.  A candidate is counted as a
volume improvement only when it meets the same Wilson-bound target with lower
qubit-round volume than the surface-code baseline target-volume row.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from b2_stim_biased_schedule_sweep import (
    TARGETS,
    build_circuit,
    compare_to_baseline,
    parse_float_list,
    parse_int_list,
    parse_str_list,
    run_config,
    summarize,
)


SAME_HARDWARE_VARIANTS = {
    "round_reduced_baseline_noise": {
        "description": "Same distance and physical qubits as baseline, but uses d-2 syndrome rounds without changing operation-class noise.",
        "after_clifford_depolarization_multiplier": 1.0,
        "before_round_data_depolarization_multiplier": 1.0,
        "before_measure_flip_probability_multiplier": 1.0,
        "after_reset_flip_probability_multiplier": 1.0,
        "round_delta": -2,
        "extra_qubit_multiplier": 1.0,
    },
    "round_reduced_clifford_hardened": {
        "description": "Same hardware footprint with d-2 syndrome rounds and half Clifford depolarization, testing whether schedule-level hardening can buy lower target volume.",
        "after_clifford_depolarization_multiplier": 0.5,
        "before_round_data_depolarization_multiplier": 1.0,
        "before_measure_flip_probability_multiplier": 1.0,
        "after_reset_flip_probability_multiplier": 1.0,
        "round_delta": -2,
        "extra_qubit_multiplier": 1.0,
    },
    "round_reduced_all_ops_hardened": {
        "description": "Same hardware footprint with d-2 syndrome rounds and half noise multipliers for Clifford, data, measurement, and reset operations.",
        "after_clifford_depolarization_multiplier": 0.5,
        "before_round_data_depolarization_multiplier": 0.5,
        "before_measure_flip_probability_multiplier": 0.5,
        "after_reset_flip_probability_multiplier": 0.5,
        "round_delta": -2,
        "extra_qubit_multiplier": 1.0,
    },
    "aggressive_round_reduced_all_ops_hardened": {
        "description": "Same hardware footprint with d-4 syndrome rounds and half operation-class noise; included as an aggressive schedule boundary test.",
        "after_clifford_depolarization_multiplier": 0.5,
        "before_round_data_depolarization_multiplier": 0.5,
        "before_measure_flip_probability_multiplier": 0.5,
        "after_reset_flip_probability_multiplier": 0.5,
        "round_delta": -4,
        "extra_qubit_multiplier": 1.0,
    },
}


def candidate_rounds(distance: int, variant: dict) -> int:
    return max(1, int(distance) + int(variant["round_delta"]))


def run_same_hardware_config(
    variant_name: str,
    variant: dict,
    distance: int,
    physical_error: float,
    basis: str,
    shots: int,
    seed: int,
) -> dict:
    rounds = candidate_rounds(distance, variant)
    row = run_config(variant_name, variant, distance, rounds, physical_error, basis, shots, seed)
    baseline_rounds = distance
    baseline_circuit = build_circuit(
        distance=distance,
        rounds=baseline_rounds,
        physical_error=physical_error,
        basis=basis,
        variant={
            "after_clifford_depolarization_multiplier": 1.0,
            "before_round_data_depolarization_multiplier": 1.0,
            "before_measure_flip_probability_multiplier": 1.0,
            "after_reset_flip_probability_multiplier": 1.0,
        },
    )
    row["same_hardware_contract"] = {
        "same_distance_as_baseline": True,
        "same_memory_basis_as_baseline": True,
        "same_physical_error_as_baseline": True,
        "same_decoder_family": "PyMatching detector_error_model decoder",
        "same_physical_qubit_count_as_baseline_distance_rounds": int(row["physical_qubits_in_stim_circuit"])
        == int(baseline_circuit.num_qubits),
        "baseline_rounds_at_same_distance": baseline_rounds,
        "candidate_rounds": rounds,
        "round_delta": int(variant["round_delta"]),
    }
    return row


def markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# B2 Same-Hardware Schedule Candidate v0.1",
        "",
        f"Last updated: {report['last_updated']}",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Criterion: {report['criterion']}",
        f"- Candidate variants: {report['candidate_variants']}",
        f"- Configurations: {summary['configuration_count']}",
        f"- Total shots: {summary['total_shots']}",
        f"- Target combinations: {summary['target_combinations']}",
        f"- Baseline met count: {summary['baseline_met_count']}",
        f"- Candidate met count: {summary['candidate_met_count']}",
        f"- Candidate-only target hits: {summary['candidate_only_meets_target_count']}",
        f"- Candidate volume improvements: {summary['improved_volume_count']}",
        f"- Mean volume reduction on improved rows: {summary['mean_volume_reduction_on_improved']}",
        f"- Max volume reduction: {summary['max_volume_reduction']}",
        "",
        "## Candidate Variants",
        "",
        "| variant | round delta | Clifford mult | data mult | measure mult | reset mult | description |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for name in report["candidate_variants"]:
        variant = report["variant_definitions"][name]
        lines.append(
            f"| {name} | {variant['round_delta']} | {variant['after_clifford_depolarization_multiplier']} | "
            f"{variant['before_round_data_depolarization_multiplier']} | {variant['before_measure_flip_probability_multiplier']} | "
            f"{variant['after_reset_flip_probability_multiplier']} | {variant['description']} |"
        )
    lines.extend(
        [
            "",
            "## Improved Target-Volume Rows",
            "",
            "| basis | p | target | baseline d | baseline volume | candidate variant | candidate d | candidate rounds | candidate volume | reduction |",
            "|---|---:|---:|---:|---:|---|---:|---:|---:|---:|",
        ]
    )
    improved = [row for row in report["comparisons"] if row["improved_volume"]]
    if improved:
        for row in improved:
            candidate = row["candidate_row"]
            lines.append(
                f"| {row['memory_basis']} | {row['physical_error']:.4g} | {row['target_logical_error']:.4g} | "
                f"{row['baseline_distance']} | {row['baseline_space_time_volume']} | {row['candidate_variant']} | "
                f"{row['candidate_distance']} | {candidate['rounds']} | {row['candidate_space_time_volume']} | "
                f"{row['volume_reduction_vs_baseline']:.3f}x |"
            )
    else:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
        ]
    )
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Limits", ""])
    for item in report["limits"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def enrich_comparisons(comparisons: list[dict], rows: list[dict]) -> list[dict]:
    by_key = {
        (
            row["variant"],
            row["memory_basis"],
            float(row["physical_error"]),
            int(row["distance"]),
            int(row["rounds"]),
        ): row
        for row in rows
    }
    enriched = []
    for comparison in comparisons:
        row = dict(comparison)
        candidate_row = None
        if row.get("candidate_met"):
            key_candidates = [
                item
                for key, item in by_key.items()
                if key[0] == row["candidate_variant"]
                and key[1] == row["memory_basis"]
                and key[2] == float(row["physical_error"])
                and key[3] == int(row["candidate_distance"])
                and int(item["space_time_volume"]) == int(row["candidate_space_time_volume"])
            ]
            if key_candidates:
                candidate_row = key_candidates[0]
        row["candidate_row"] = candidate_row
        enriched.append(row)
    return enriched


def run(args: argparse.Namespace) -> dict:
    target_report = json.loads(args.target_volume.read_text(encoding="utf-8"))
    distances = parse_int_list(args.distances)
    physical_errors = parse_float_list(args.physical_errors)
    memory_bases = parse_str_list(args.memory_bases)
    variant_names = parse_str_list(args.variants)
    variants = {name: SAME_HARDWARE_VARIANTS[name] for name in variant_names}

    rows = []
    config_index = 0
    for variant_name, variant in variants.items():
        for basis in memory_bases:
            for physical_error in physical_errors:
                for distance in distances:
                    config_index += 1
                    rows.append(
                        run_same_hardware_config(
                            variant_name=variant_name,
                            variant=variant,
                            distance=distance,
                            physical_error=physical_error,
                            basis=basis,
                            shots=args.shots,
                            seed=args.seed + config_index,
                        )
                    )

    comparisons = compare_to_baseline(rows, target_report, TARGETS, args.criterion)
    comparisons = enrich_comparisons(comparisons, rows)
    summary = summarize(rows, comparisons)
    improved_rows = [row for row in comparisons if row["improved_volume"]]
    status = (
        "same_hardware_schedule_candidate_volume_positive_diagnostic_not_new_code_claim"
        if improved_rows
        else "same_hardware_schedule_candidate_no_volume_gain_boundary"
    )
    report = {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 same-hardware schedule candidate",
        "version": "0.1",
        "last_updated": args.last_updated,
        "status": status,
        "method": "b2_same_hardware_schedule_candidate_v0",
        "source_target_volume": str(args.target_volume),
        "criterion": args.criterion,
        "candidate_variants": variant_names,
        "variant_definitions": variants,
        "same_hardware_contract": {
            "same_code_family": "rotated_surface_code_memory",
            "same_distance_grid": distances,
            "same_memory_bases": memory_bases,
            "same_physical_error_grid": physical_errors,
            "same_shots_per_configuration": args.shots,
            "same_decoder": "PyMatching detector_error_model decoder",
            "same_physical_qubits_per_distance": True,
            "volume_lever": "reduced_syndrome_rounds_only",
        },
        "summary": summary,
        "rows": rows,
        "comparisons": comparisons,
        "claim_boundary": {
            "same_hardware_volume_improvement_found": bool(improved_rows),
            "improved_volume_count": summary["improved_volume_count"],
            "max_volume_reduction": summary["max_volume_reduction"],
            "candidate_only_meets_target_count": summary["candidate_only_meets_target_count"],
            "new_code_claimed": False,
            "threshold_claimed": False,
            "calibrated_device_claimed": False,
        },
        "limits": [
            "This is a same-code-family schedule/noise candidate, not a new quantum code.",
            "The candidate uses reduced syndrome rounds, so positive rows must be interpreted as schedule-level target-volume diagnostics.",
            "The noise hardening variants require a physical mechanism before any hardware claim.",
            "The sweep is finite-shot and small-distance; Wilson upper bounds are conservative but not a threshold proof.",
        ],
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-volume", type=Path, default=Path("results/B2_stim_surface_code_target_volume_v0.json"))
    parser.add_argument("--distances", default="3,5,7")
    parser.add_argument("--physical-errors", default="0.001,0.003,0.005,0.007,0.01")
    parser.add_argument("--memory-bases", default="x,z")
    parser.add_argument(
        "--variants",
        default="round_reduced_baseline_noise,round_reduced_clifford_hardened,round_reduced_all_ops_hardened,aggressive_round_reduced_all_ops_hardened",
    )
    parser.add_argument("--criterion", choices=["wilson_95_high", "observed_logical_error_rate"], default="wilson_95_high")
    parser.add_argument("--shots", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=220628)
    parser.add_argument("--last-updated", default="2026-06-16")
    parser.add_argument("--json-output", type=Path, default=Path("results/B2_same_hardware_schedule_candidate_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B2_same_hardware_schedule_candidate.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        keys = ["status", "method", "criterion"]
        summary = {key: report[key] for key in keys}
        summary.update(report["summary"])
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
