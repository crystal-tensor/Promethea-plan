#!/usr/bin/env python3
"""Stress-test the B2 same-hardware reduced-round schedule candidate.

The first same-hardware B2 diagnostic found Wilson target-volume improvements,
but all improved rows came from the aggressive d-4 all-operation hardening
variant.  This runner keeps the same baseline comparison and asks whether that
signal survives higher-shot reseeding and simple noise-mismatch stress profiles.
"""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter, defaultdict
from pathlib import Path

from b2_same_hardware_schedule_candidate import (
    SAME_HARDWARE_VARIANTS,
    enrich_comparisons,
    run_same_hardware_config,
)
from b2_stim_biased_schedule_sweep import TARGETS, compare_to_baseline, parse_float_list, parse_int_list, parse_str_list, summarize


DEFAULT_VARIANTS = "round_reduced_all_ops_hardened,aggressive_round_reduced_all_ops_hardened"


STRESS_PROFILES = {
    "higher_shot_reseed": {
        "description": "Same candidate noise model as v0, but with a fresh seed and larger shots per configuration.",
        "hardened_multiplier_floor": None,
        "clifford_only": False,
    },
    "mild_noise_mismatch_0p60": {
        "description": "Any candidate operation-class multiplier below 1.0 is relaxed to 0.60 to test mild hardening mismatch.",
        "hardened_multiplier_floor": 0.60,
        "clifford_only": False,
    },
    "moderate_noise_mismatch_0p75": {
        "description": "Any candidate operation-class multiplier below 1.0 is relaxed to 0.75 to test moderate hardening mismatch.",
        "hardened_multiplier_floor": 0.75,
        "clifford_only": False,
    },
    "clifford_only_mechanism": {
        "description": "Reduced-round variants keep Clifford hardening but lose data/measurement/reset hardening.",
        "hardened_multiplier_floor": None,
        "clifford_only": True,
    },
}


NOISE_KEYS = [
    "after_clifford_depolarization_multiplier",
    "before_round_data_depolarization_multiplier",
    "before_measure_flip_probability_multiplier",
    "after_reset_flip_probability_multiplier",
]


def stressed_variant(base_variant: dict, profile: dict) -> dict:
    variant = copy.deepcopy(base_variant)
    if profile["hardened_multiplier_floor"] is not None:
        floor = float(profile["hardened_multiplier_floor"])
        for key in NOISE_KEYS:
            if float(variant[key]) < 1.0:
                variant[key] = floor
    if profile["clifford_only"]:
        variant["after_clifford_depolarization_multiplier"] = min(
            float(variant["after_clifford_depolarization_multiplier"]), 0.5
        )
        variant["before_round_data_depolarization_multiplier"] = 1.0
        variant["before_measure_flip_probability_multiplier"] = 1.0
        variant["after_reset_flip_probability_multiplier"] = 1.0
    return variant


def profile_variant_name(profile_name: str, variant_name: str) -> str:
    return f"{profile_name}::{variant_name}"


def summarize_profile(profile_name: str, profile_rows: list[dict], comparisons: list[dict]) -> dict:
    summary = summarize(profile_rows, comparisons)
    improved_by_variant = Counter(row["candidate_variant"] for row in comparisons if row["improved_volume"])
    candidate_only_by_variant = Counter(row["candidate_variant"] for row in comparisons if row["candidate_only_meets_target"])
    non_aggressive_improvements = sum(
        count for variant, count in improved_by_variant.items() if variant and "aggressive_round" not in variant
    )
    aggressive_improvements = sum(
        count for variant, count in improved_by_variant.items() if variant and "aggressive_round" in variant
    )
    summary.update(
        {
            "profile": profile_name,
            "improved_by_variant": dict(improved_by_variant),
            "candidate_only_by_variant": dict(candidate_only_by_variant),
            "non_aggressive_improved_volume_count": non_aggressive_improvements,
            "aggressive_improved_volume_count": aggressive_improvements,
            "positive_signal_depends_on_aggressive_schedule": bool(
                aggressive_improvements > 0 and non_aggressive_improvements == 0
            ),
        }
    )
    return summary


def markdown(report: dict) -> str:
    lines = [
        "# B2 Same-Hardware Schedule Robustness Stress v0.1",
        "",
        f"Last updated: {report['last_updated']}",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Criterion: {report['criterion']}",
        f"- Shots per configuration: {report['shots_per_configuration']}",
        f"- Profiles: {', '.join(report['stress_profiles'])}",
        f"- Base variants: {', '.join(report['base_variants'])}",
        f"- Configurations: {report['overall_summary']['configuration_count']}",
        f"- Total shots: {report['overall_summary']['total_shots']}",
        f"- Robust non-aggressive volume improvements: {report['claim_boundary']['robust_non_aggressive_volume_improvement_found']}",
        f"- Any aggressive volume improvement under stress: {report['claim_boundary']['any_aggressive_volume_improvement_under_stress']}",
        f"- Positive signal depends on aggressive schedule: {report['claim_boundary']['positive_signal_depends_on_aggressive_schedule']}",
        "",
        "## Profile Results",
        "",
        "| profile | candidate met | candidate-only | improved volume | non-aggressive improved | aggressive improved | max reduction | interpretation |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["profile_summaries"]:
        max_reduction = row["max_volume_reduction"]
        max_reduction_text = f"{max_reduction:.3f}x" if max_reduction is not None else "n/a"
        lines.append(
            f"| {row['profile']} | {row['candidate_met_count']} | {row['candidate_only_meets_target_count']} | "
            f"{row['improved_volume_count']} | {row['non_aggressive_improved_volume_count']} | "
            f"{row['aggressive_improved_volume_count']} | {max_reduction_text} | {row['interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Improved Rows By Profile",
            "",
            "| profile | basis | p | target | baseline volume | candidate variant | candidate d | candidate rounds | candidate volume | reduction |",
            "|---|---|---:|---:|---:|---|---:|---:|---:|---:|",
        ]
    )
    improved_rows = [row for row in report["comparisons"] if row["improved_volume"]]
    if not improved_rows:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    else:
        if len(improved_rows) > 80:
            lines.append(
                f"| note | showing first 80 of {len(improved_rows)} improved rows | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |"
            )
        for row in improved_rows[:80]:
            candidate = row.get("candidate_row") or {}
            lines.append(
                f"| {row['stress_profile']} | {row['memory_basis']} | {row['physical_error']:.4g} | "
                f"{row['target_logical_error']:.4g} | {row['baseline_space_time_volume']} | "
                f"{row['candidate_variant']} | {row['candidate_distance']} | {candidate.get('rounds', 'n/a')} | "
                f"{row['candidate_space_time_volume']} | {row['volume_reduction_vs_baseline']:.3f}x |"
            )
    lines.extend(["", "## Claim Boundary", ""])
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Limits", ""])
    for item in report["limits"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict:
    target_report = json.loads(args.target_volume.read_text(encoding="utf-8"))
    distances = parse_int_list(args.distances)
    physical_errors = parse_float_list(args.physical_errors)
    memory_bases = parse_str_list(args.memory_bases)
    base_variant_names = parse_str_list(args.variants)
    profile_names = parse_str_list(args.profiles)

    all_rows = []
    all_comparisons = []
    profile_summaries = []
    config_index = 0
    for profile_name in profile_names:
        profile = STRESS_PROFILES[profile_name]
        profile_rows = []
        for base_variant_name in base_variant_names:
            base_variant = SAME_HARDWARE_VARIANTS[base_variant_name]
            variant = stressed_variant(base_variant, profile)
            variant_name = profile_variant_name(profile_name, base_variant_name)
            variant["description"] = f"{profile['description']} Base variant: {base_variant['description']}"
            for basis in memory_bases:
                for physical_error in physical_errors:
                    for distance in distances:
                        config_index += 1
                        row = run_same_hardware_config(
                            variant_name=variant_name,
                            variant=variant,
                            distance=distance,
                            physical_error=physical_error,
                            basis=basis,
                            shots=args.shots,
                            seed=args.seed + config_index,
                        )
                        row["stress_profile"] = profile_name
                        row["base_variant"] = base_variant_name
                        profile_rows.append(row)
                        all_rows.append(row)

        comparisons = compare_to_baseline(profile_rows, target_report, TARGETS, args.criterion)
        comparisons = enrich_comparisons(comparisons, profile_rows)
        for comparison in comparisons:
            comparison["stress_profile"] = profile_name
        profile_summary = summarize_profile(profile_name, profile_rows, comparisons)
        if profile_summary["non_aggressive_improved_volume_count"] > 0:
            profile_summary["interpretation"] = "non_aggressive_candidate_survives_profile"
        elif profile_summary["aggressive_improved_volume_count"] > 0:
            profile_summary["interpretation"] = "positive_signal_only_aggressive_under_profile"
        elif profile_summary["candidate_only_meets_target_count"] > 0:
            profile_summary["interpretation"] = "target_feasibility_gain_without_volume_improvement"
        else:
            profile_summary["interpretation"] = "no_target_volume_or_feasibility_gain"
        profile_summaries.append(profile_summary)
        all_comparisons.extend(comparisons)

    overall_summary = {
        "configuration_count": len(all_rows),
        "total_shots": sum(row["shots"] for row in all_rows),
        "profile_count": len(profile_names),
        "variant_count_per_profile": len(base_variant_names),
        "target_comparisons": len(all_comparisons),
        "total_improved_volume_rows": sum(row["improved_volume_count"] for row in profile_summaries),
        "total_non_aggressive_improved_volume_rows": sum(
            row["non_aggressive_improved_volume_count"] for row in profile_summaries
        ),
        "total_aggressive_improved_volume_rows": sum(row["aggressive_improved_volume_count"] for row in profile_summaries),
        "max_decoder_runtime_seconds_per_shot": max(row["decoder_runtime_seconds_per_shot"] for row in all_rows),
    }
    robust_non_aggressive = overall_summary["total_non_aggressive_improved_volume_rows"] > 0
    any_aggressive = overall_summary["total_aggressive_improved_volume_rows"] > 0
    status = (
        "same_hardware_schedule_robust_non_aggressive_positive_diagnostic"
        if robust_non_aggressive
        else "same_hardware_schedule_robustness_boundary_aggressive_only_or_negative"
    )

    return {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 same-hardware schedule robustness stress",
        "version": "0.1",
        "last_updated": args.last_updated,
        "status": status,
        "method": "b2_same_hardware_schedule_robustness_v0",
        "source_candidate": str(args.source_candidate),
        "source_target_volume": str(args.target_volume),
        "criterion": args.criterion,
        "shots_per_configuration": args.shots,
        "stress_profiles": profile_names,
        "stress_profile_definitions": {name: STRESS_PROFILES[name] for name in profile_names},
        "base_variants": base_variant_names,
        "same_hardware_contract": {
            "same_code_family": "rotated_surface_code_memory",
            "same_distance_grid": distances,
            "same_memory_bases": memory_bases,
            "same_physical_error_grid": physical_errors,
            "same_decoder": "PyMatching detector_error_model decoder",
            "same_physical_qubits_per_distance": True,
            "volume_lever": "reduced_syndrome_rounds_only",
            "stress_levers": ["larger_shots_reseed", "candidate_noise_mismatch", "clifford_only_physical_mechanism"],
        },
        "overall_summary": overall_summary,
        "profile_summaries": profile_summaries,
        "rows": all_rows,
        "comparisons": all_comparisons,
        "claim_boundary": {
            "robust_non_aggressive_volume_improvement_found": robust_non_aggressive,
            "any_aggressive_volume_improvement_under_stress": any_aggressive,
            "positive_signal_depends_on_aggressive_schedule": bool(any_aggressive and not robust_non_aggressive),
            "new_code_claimed": False,
            "threshold_claimed": False,
            "calibrated_device_claimed": False,
        },
        "limits": [
            "This is a finite-shot robustness stress test, not a threshold proof.",
            "Noise-mismatch profiles are synthetic parameter stressors, not calibrated hardware drift models.",
            "A positive aggressive reduced-round row does not by itself justify a hardware schedule claim.",
            "B2 should not strengthen beyond diagnostic status until a non-aggressive or physically motivated schedule survives larger distances and calibrated/noise-mismatch checks.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-volume", type=Path, default=Path("results/B2_stim_surface_code_target_volume_v0.json"))
    parser.add_argument("--source-candidate", type=Path, default=Path("results/B2_same_hardware_schedule_candidate_v0.json"))
    parser.add_argument("--distances", default="3,5,7")
    parser.add_argument("--physical-errors", default="0.001,0.003,0.005,0.007,0.01")
    parser.add_argument("--memory-bases", default="x,z")
    parser.add_argument("--variants", default=DEFAULT_VARIANTS)
    parser.add_argument(
        "--profiles",
        default="higher_shot_reseed,mild_noise_mismatch_0p60,moderate_noise_mismatch_0p75,clifford_only_mechanism",
    )
    parser.add_argument("--criterion", choices=["wilson_95_high", "observed_logical_error_rate"], default="wilson_95_high")
    parser.add_argument("--shots", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=220629)
    parser.add_argument("--last-updated", default="2026-06-17")
    parser.add_argument("--json-output", type=Path, default=Path("results/B2_same_hardware_schedule_robustness_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B2_same_hardware_schedule_robustness.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    for name in parse_str_list(args.profiles):
        if name not in STRESS_PROFILES:
            raise ValueError(f"unknown stress profile: {name}")
    for name in parse_str_list(args.variants):
        if name not in SAME_HARDWARE_VARIANTS:
            raise ValueError(f"unknown base variant: {name}")

    report = run(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "method": report["method"],
                    "criterion": report["criterion"],
                    "overall_summary": report["overall_summary"],
                    "claim_boundary": report["claim_boundary"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
