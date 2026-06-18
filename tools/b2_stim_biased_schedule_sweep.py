#!/usr/bin/env python3
"""Run circuit-level biased schedule/noise sweeps for the B2 surface-code baseline."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pymatching
import stim


TARGETS = [0.1, 0.05, 0.01, 0.001]

VARIANTS = {
    "measurement_reset_hardened_schedule": {
        "description": "Halves measurement and reset flip probabilities while leaving data and Clifford depolarization unchanged.",
        "after_clifford_depolarization_multiplier": 1.0,
        "before_round_data_depolarization_multiplier": 1.0,
        "before_measure_flip_probability_multiplier": 0.5,
        "after_reset_flip_probability_multiplier": 0.5,
        "round_multiplier": 1.0,
        "extra_qubit_multiplier": 1.0,
    },
    "data_memory_hardened_schedule": {
        "description": "Halves before-round data depolarization while leaving reset, measurement, and Clifford depolarization unchanged.",
        "after_clifford_depolarization_multiplier": 1.0,
        "before_round_data_depolarization_multiplier": 0.5,
        "before_measure_flip_probability_multiplier": 1.0,
        "after_reset_flip_probability_multiplier": 1.0,
        "round_multiplier": 1.0,
        "extra_qubit_multiplier": 1.0,
    },
    "clifford_gate_hardened_schedule": {
        "description": "Halves Clifford-gate depolarization while leaving data, reset, and measurement noise unchanged.",
        "after_clifford_depolarization_multiplier": 0.5,
        "before_round_data_depolarization_multiplier": 1.0,
        "before_measure_flip_probability_multiplier": 1.0,
        "after_reset_flip_probability_multiplier": 1.0,
        "round_multiplier": 1.0,
        "extra_qubit_multiplier": 1.0,
    },
}


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def parse_str_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def wilson_interval(failures: int, shots: int, z: float = 1.96) -> tuple[float, float]:
    if shots == 0:
        return 0.0, 0.0
    phat = failures / shots
    denom = 1 + z**2 / shots
    center = (phat + z**2 / (2 * shots)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z**2 / (4 * shots)) / shots) / denom
    return max(0.0, center - half), min(1.0, center + half)


def generated_task_name(basis: str) -> str:
    if basis not in {"x", "z"}:
        raise ValueError(f"unsupported memory basis: {basis}")
    return f"surface_code:rotated_memory_{basis}"


def metric_value(row: dict, criterion: str) -> float:
    if criterion == "wilson_95_high":
        return float(row["wilson_95_high"])
    if criterion == "observed_logical_error_rate":
        return float(row["logical_error_rate"])
    raise ValueError(f"unsupported target criterion: {criterion}")


def variant_noise_params(physical_error: float, variant: dict) -> dict:
    return {
        "after_clifford_depolarization": physical_error
        * float(variant["after_clifford_depolarization_multiplier"]),
        "before_round_data_depolarization": physical_error
        * float(variant["before_round_data_depolarization_multiplier"]),
        "before_measure_flip_probability": physical_error
        * float(variant["before_measure_flip_probability_multiplier"]),
        "after_reset_flip_probability": physical_error
        * float(variant["after_reset_flip_probability_multiplier"]),
    }


def build_circuit(distance: int, rounds: int, physical_error: float, basis: str, variant: dict) -> stim.Circuit:
    params = variant_noise_params(physical_error, variant)
    return stim.Circuit.generated(
        generated_task_name(basis),
        distance=distance,
        rounds=rounds,
        after_clifford_depolarization=params["after_clifford_depolarization"],
        before_round_data_depolarization=params["before_round_data_depolarization"],
        before_measure_flip_probability=params["before_measure_flip_probability"],
        after_reset_flip_probability=params["after_reset_flip_probability"],
    )


def run_config(
    variant_name: str,
    variant: dict,
    distance: int,
    rounds: int,
    physical_error: float,
    basis: str,
    shots: int,
    seed: int,
) -> dict:
    started_build = time.perf_counter()
    circuit = build_circuit(distance, rounds, physical_error, basis, variant)
    dem = circuit.detector_error_model(decompose_errors=True)
    matching = pymatching.Matching.from_detector_error_model(dem)
    build_seconds = time.perf_counter() - started_build

    started_sample = time.perf_counter()
    sampler = circuit.compile_detector_sampler(seed=seed)
    detection_events, observables = sampler.sample(shots, separate_observables=True)
    sample_seconds = time.perf_counter() - started_sample

    started_decode = time.perf_counter()
    predictions = matching.decode_batch(detection_events)
    decode_seconds = time.perf_counter() - started_decode

    failures_by_shot = np.any(predictions != observables, axis=1)
    failures = int(np.count_nonzero(failures_by_shot))
    logical_error_rate = failures / shots
    low, high = wilson_interval(failures, shots)
    noise_params = variant_noise_params(physical_error, variant)
    return {
        "variant": variant_name,
        "variant_description": variant["description"],
        "code_family": "rotated_surface_code_memory_biased_schedule_noise_sweep",
        "source_code_family": "rotated_surface_code_memory",
        "toolchain": "stim_1.16.0_pymatching_2.4.0",
        "stim_task": generated_task_name(basis),
        "memory_basis": basis,
        "distance": distance,
        "rounds": rounds,
        "physical_error": physical_error,
        "noise_parameters": noise_params,
        "noise_multipliers": {
            "after_clifford_depolarization": variant["after_clifford_depolarization_multiplier"],
            "before_round_data_depolarization": variant["before_round_data_depolarization_multiplier"],
            "before_measure_flip_probability": variant["before_measure_flip_probability_multiplier"],
            "after_reset_flip_probability": variant["after_reset_flip_probability_multiplier"],
        },
        "shots": shots,
        "physical_qubits_in_stim_circuit": circuit.num_qubits,
        "detectors": circuit.num_detectors,
        "observables": circuit.num_observables,
        "dem_terms": len(str(dem).splitlines()),
        "matching_nodes": matching.num_nodes,
        "matching_edges": matching.num_edges,
        "logical_failures": failures,
        "logical_error_rate": logical_error_rate,
        "wilson_95_low": low,
        "wilson_95_high": high,
        "space_time_volume": int(circuit.num_qubits) * int(rounds),
        "build_seconds": build_seconds,
        "sample_seconds": sample_seconds,
        "decode_seconds": decode_seconds,
        "decoder_runtime_seconds_per_shot": decode_seconds / shots if shots else 0.0,
        "total_runtime_seconds_per_shot": (sample_seconds + decode_seconds) / shots if shots else 0.0,
        "seed": seed,
    }


def baseline_volume_rows(target_report: dict) -> dict[tuple[str, float, float], dict]:
    return {
        (row["memory_basis"], float(row["physical_error"]), float(row["target_logical_error"])): row
        for row in target_report["results"]
    }


def best_candidate_for(rows: list[dict], basis: str, physical_error: float, target: float, criterion: str) -> dict | None:
    candidates = [
        row
        for row in rows
        if row["memory_basis"] == basis
        and float(row["physical_error"]) == physical_error
        and metric_value(row, criterion) <= target
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda row: (row["space_time_volume"], row["distance"], row["variant"]))


def compare_to_baseline(candidate_rows: list[dict], target_report: dict, targets: list[float], criterion: str) -> list[dict]:
    baseline_by_key = baseline_volume_rows(target_report)
    bases = sorted({row["memory_basis"] for row in candidate_rows})
    physical_errors = sorted({float(row["physical_error"]) for row in candidate_rows})
    comparisons = []
    for basis in bases:
        for physical_error in physical_errors:
            for target in targets:
                baseline_row = baseline_by_key[(basis, physical_error, target)]
                candidate = best_candidate_for(candidate_rows, basis, physical_error, target, criterion)
                baseline_met = bool(baseline_row["met"])
                candidate_met = candidate is not None
                baseline_volume = baseline_row["space_time_volume"] if baseline_met else None
                candidate_volume = candidate["space_time_volume"] if candidate_met else None
                volume_reduction = (
                    baseline_volume / candidate_volume
                    if baseline_volume and candidate_volume
                    else None
                )
                improved = bool(volume_reduction is not None and volume_reduction > 1.0)
                candidate_only = candidate_met and not baseline_met
                comparisons.append(
                    {
                        "memory_basis": basis,
                        "physical_error": physical_error,
                        "target_logical_error": target,
                        "criterion": criterion,
                        "baseline_met": baseline_met,
                        "baseline_distance": baseline_row.get("distance"),
                        "baseline_space_time_volume": baseline_volume,
                        "baseline_metric_value": baseline_row.get("wilson_95_high")
                        if baseline_met
                        else baseline_row.get("best_available_wilson_95_high"),
                        "candidate_met": candidate_met,
                        "candidate_variant": candidate["variant"] if candidate else None,
                        "candidate_distance": candidate["distance"] if candidate else None,
                        "candidate_space_time_volume": candidate_volume,
                        "candidate_metric_value": metric_value(candidate, criterion) if candidate else None,
                        "volume_reduction_vs_baseline": volume_reduction,
                        "improved_volume": improved,
                        "candidate_only_meets_target": candidate_only,
                        "interpretation": (
                            "candidate_beats_baseline_volume"
                            if improved
                            else "candidate_meets_target_unmet_by_baseline"
                            if candidate_only
                            else "candidate_matches_baseline_target_without_volume_gain"
                            if candidate_met and baseline_met
                            else "no_candidate_advantage"
                        ),
                    }
                )
    return comparisons


def summarize(rows: list[dict], comparisons: list[dict]) -> dict:
    improved_rows = [row for row in comparisons if row["improved_volume"]]
    candidate_only_rows = [row for row in comparisons if row["candidate_only_meets_target"]]
    met_rows = [row for row in comparisons if row["candidate_met"]]
    reductions = [float(row["volume_reduction_vs_baseline"]) for row in improved_rows]
    best_rows_by_variant = {}
    for variant_name in sorted({row["variant"] for row in rows}):
        variant_rows = [row for row in rows if row["variant"] == variant_name]
        best = min(variant_rows, key=lambda row: row["wilson_95_high"])
        worst = max(variant_rows, key=lambda row: row["wilson_95_high"])
        best_rows_by_variant[variant_name] = {
            "min_wilson_95_high": best["wilson_95_high"],
            "min_configuration": {
                "memory_basis": best["memory_basis"],
                "distance": best["distance"],
                "physical_error": best["physical_error"],
                "logical_failures": best["logical_failures"],
                "shots": best["shots"],
            },
            "max_wilson_95_high": worst["wilson_95_high"],
        }
    return {
        "configuration_count": len(rows),
        "variant_count": len({row["variant"] for row in rows}),
        "total_shots": sum(row["shots"] for row in rows),
        "distance_values": sorted({row["distance"] for row in rows}),
        "memory_bases": sorted({row["memory_basis"] for row in rows}),
        "physical_error_rates": sorted({float(row["physical_error"]) for row in rows}),
        "max_decoder_runtime_seconds_per_shot": max(row["decoder_runtime_seconds_per_shot"] for row in rows),
        "target_combinations": len(comparisons),
        "baseline_met_count": sum(1 for row in comparisons if row["baseline_met"]),
        "candidate_met_count": len(met_rows),
        "candidate_only_meets_target_count": len(candidate_only_rows),
        "improved_volume_count": len(improved_rows),
        "mean_volume_reduction_on_improved": sum(reductions) / len(reductions) if reductions else None,
        "max_volume_reduction": max(reductions) if reductions else None,
        "best_rows_by_variant": best_rows_by_variant,
    }


def fmt_ratio(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}x"


def markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# B2 Stim Biased-Schedule Circuit-Level Sweep v0.1",
        "",
        "Last updated: 2026-06-13",
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
        f"- Mean volume reduction on improved rows: {fmt_ratio(summary['mean_volume_reduction_on_improved'])}",
        f"- Max volume reduction: {fmt_ratio(summary['max_volume_reduction'])}",
        f"- Max decoder runtime / shot: {summary['max_decoder_runtime_seconds_per_shot']:.6g} s",
        "",
        "## Candidate Variants",
        "",
        "| variant | Clifford mult | data mult | measure mult | reset mult | description |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name, variant in report["variant_definitions"].items():
        lines.append(
            f"| {name} | {variant['after_clifford_depolarization_multiplier']} | "
            f"{variant['before_round_data_depolarization_multiplier']} | "
            f"{variant['before_measure_flip_probability_multiplier']} | "
            f"{variant['after_reset_flip_probability_multiplier']} | {variant['description']} |"
        )
    lines.extend(
        [
            "",
            "## Target Comparisons",
            "",
            "| basis | p | target | baseline met | baseline volume | candidate met | variant | candidate d | candidate volume | volume reduction | interpretation |",
            "|---|---:|---:|---|---:|---|---|---:|---:|---:|---|",
        ]
    )
    for row in report["target_comparisons"]:
        lines.append(
            f"| {row['memory_basis']} | {row['physical_error']:.4g} | {row['target_logical_error']:.4g} | "
            f"{row['baseline_met']} | {row['baseline_space_time_volume'] or 'n/a'} | "
            f"{row['candidate_met']} | {row['candidate_variant'] or 'n/a'} | "
            f"{row['candidate_distance'] or 'n/a'} | {row['candidate_space_time_volume'] or 'n/a'} | "
            f"{fmt_ratio(row['volume_reduction_vs_baseline'])} | {row['interpretation']} |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def run_experiment(args: argparse.Namespace) -> dict:
    rows = []
    selected_variants = parse_str_list(args.variants)
    for variant_name in selected_variants:
        if variant_name not in VARIANTS:
            raise ValueError(f"unknown variant: {variant_name}")
    for variant_index, variant_name in enumerate(selected_variants):
        variant = VARIANTS[variant_name]
        for basis_index, basis in enumerate(parse_str_list(args.bases)):
            for distance_index, distance in enumerate(parse_int_list(args.distances)):
                if distance <= 0 or distance % 2 == 0:
                    raise ValueError(f"distance must be positive and odd: {distance}")
                rounds = distance if args.rounds == "distance" else int(args.rounds)
                for error_index, physical_error in enumerate(parse_float_list(args.physical_errors)):
                    seed = args.seed + 100000 * variant_index + 10000 * basis_index + 100 * distance_index + error_index
                    rows.append(
                        run_config(
                            variant_name=variant_name,
                            variant=variant,
                            distance=distance,
                            rounds=rounds,
                            physical_error=physical_error,
                            basis=basis,
                            shots=args.shots,
                            seed=seed,
                        )
                    )
    target_report = json.loads(args.target_volume.read_text(encoding="utf-8"))
    targets = parse_float_list(args.targets)
    comparisons = compare_to_baseline(rows, target_report, targets, args.criterion)
    summary = summarize(rows, comparisons)
    return {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 Stim/PyMatching biased-schedule circuit-level sweep",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "stim_biased_schedule_circuit_sweep_not_new_code_claim",
        "method": "stim_biased_schedule_circuit_level_noise_sweep_v0",
        "source_baseline": "B2_stim_surface_code_memory_baseline_v0",
        "source_target_volume": "B2_stim_surface_code_target_volume_v0",
        "criterion": args.criterion,
        "seed": args.seed,
        "shots_per_configuration": args.shots,
        "candidate_variants": selected_variants,
        "variant_definitions": {name: VARIANTS[name] for name in selected_variants},
        "summary": summary,
        "results": rows,
        "target_comparisons": comparisons,
        "target_combinations": summary["target_combinations"],
        "baseline_met_count": summary["baseline_met_count"],
        "candidate_met_count": summary["candidate_met_count"],
        "candidate_only_meets_target_count": summary["candidate_only_meets_target_count"],
        "improved_volume_count": summary["improved_volume_count"],
        "mean_volume_reduction_on_improved": summary["mean_volume_reduction_on_improved"],
        "max_volume_reduction": summary["max_volume_reduction"],
        "limits": [
            "This is a real Stim circuit-level noise-parameter sweep, but it is not a new code-family claim.",
            "The candidate changes operation-class noise assumptions, so any advantage requires a physical mechanism for measurement/reset or data-memory hardening.",
            "The comparison uses the same Wilson target-volume contract as the surface-code baseline, but the baseline has not yet been retuned under identical biased hardware assumptions.",
            "The sweep is small: distances d=3/5/7, generated rotated-memory circuits, and finite shots.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-volume", type=Path, default=Path("results/B2_stim_surface_code_target_volume_v0.json"))
    parser.add_argument("--distances", default="3,5,7")
    parser.add_argument("--rounds", default="distance")
    parser.add_argument("--physical-errors", default="0.001,0.003,0.005,0.007,0.01")
    parser.add_argument("--bases", default="x,z")
    parser.add_argument("--targets", default="1e-1,5e-2,1e-2,1e-3")
    parser.add_argument("--criterion", choices=["wilson_95_high", "observed_logical_error_rate"], default="wilson_95_high")
    parser.add_argument("--variants", default="measurement_reset_hardened_schedule,data_memory_hardened_schedule,clifford_gate_hardened_schedule")
    parser.add_argument("--shots", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=220713)
    parser.add_argument("--json-output", type=Path, default=Path("results/B2_stim_biased_schedule_sweep_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B2_stim_biased_schedule_sweep.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run_experiment(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        keys = [
            "status",
            "target_combinations",
            "baseline_met_count",
            "candidate_met_count",
            "candidate_only_meets_target_count",
            "improved_volume_count",
            "mean_volume_reduction_on_improved",
            "max_volume_reduction",
        ]
        print(json.dumps({key: report[key] for key in keys}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
