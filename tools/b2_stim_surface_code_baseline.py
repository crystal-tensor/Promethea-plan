#!/usr/bin/env python3
"""Run a small Stim/PyMatching rotated surface-code memory baseline for B2."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pymatching
import stim


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


def build_circuit(distance: int, rounds: int, physical_error: float, basis: str) -> stim.Circuit:
    return stim.Circuit.generated(
        generated_task_name(basis),
        distance=distance,
        rounds=rounds,
        after_clifford_depolarization=physical_error,
        before_round_data_depolarization=physical_error,
        before_measure_flip_probability=physical_error,
        after_reset_flip_probability=physical_error,
    )


def run_config(
    distance: int,
    rounds: int,
    physical_error: float,
    basis: str,
    shots: int,
    seed: int,
) -> dict:
    started_build = time.perf_counter()
    circuit = build_circuit(distance, rounds, physical_error, basis)
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
    return {
        "code_family": "rotated_surface_code_memory",
        "toolchain": "stim_1.16.0_pymatching_2.4.0",
        "stim_task": generated_task_name(basis),
        "memory_basis": basis,
        "distance": distance,
        "rounds": rounds,
        "physical_error": physical_error,
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
        "build_seconds": build_seconds,
        "sample_seconds": sample_seconds,
        "decode_seconds": decode_seconds,
        "decoder_runtime_seconds_per_shot": decode_seconds / shots if shots else 0.0,
        "total_runtime_seconds_per_shot": (sample_seconds + decode_seconds) / shots if shots else 0.0,
        "seed": seed,
    }


def summarize(rows: list[dict]) -> dict:
    best = min(rows, key=lambda row: row["logical_error_rate"])
    worst = max(rows, key=lambda row: row["logical_error_rate"])
    trend_checks = []
    bases = sorted({row["memory_basis"] for row in rows})
    error_rates = sorted({row["physical_error"] for row in rows})
    for basis in bases:
        for physical_error in error_rates:
            matching_rows = sorted(
                [
                    row
                    for row in rows
                    if row["memory_basis"] == basis and row["physical_error"] == physical_error
                ],
                key=lambda row: row["distance"],
            )
            if len(matching_rows) < 2:
                continue
            logical_rates = [row["logical_error_rate"] for row in matching_rows]
            trend_checks.append(
                {
                    "memory_basis": basis,
                    "physical_error": physical_error,
                    "distances": [row["distance"] for row in matching_rows],
                    "logical_error_rates": logical_rates,
                    "nonincreasing_with_distance": all(
                        logical_rates[index + 1] <= logical_rates[index]
                        for index in range(len(logical_rates) - 1)
                    ),
                }
            )
    return {
        "configuration_count": len(rows),
        "total_shots": sum(row["shots"] for row in rows),
        "distance_values": sorted({row["distance"] for row in rows}),
        "memory_bases": bases,
        "physical_error_rates": error_rates,
        "min_logical_error_rate": best["logical_error_rate"],
        "min_logical_error_configuration": {
            "memory_basis": best["memory_basis"],
            "distance": best["distance"],
            "rounds": best["rounds"],
            "physical_error": best["physical_error"],
            "logical_failures": best["logical_failures"],
            "shots": best["shots"],
        },
        "max_logical_error_rate": worst["logical_error_rate"],
        "max_decoder_runtime_seconds_per_shot": max(
            row["decoder_runtime_seconds_per_shot"] for row in rows
        ),
        "max_total_runtime_seconds_per_shot": max(row["total_runtime_seconds_per_shot"] for row in rows),
        "distance_trend_checks": trend_checks,
        "nonincreasing_trend_count": sum(1 for check in trend_checks if check["nonincreasing_with_distance"]),
    }


def markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# B2 Stim Surface-Code Memory Baseline v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Toolchain: {report['toolchain']}",
        f"- Configurations: {summary['configuration_count']}",
        f"- Total shots: {summary['total_shots']}",
        f"- Distances: {summary['distance_values']}",
        f"- Memory bases: {summary['memory_bases']}",
        f"- Physical error rates: {summary['physical_error_rates']}",
        f"- Minimum observed logical error rate: {summary['min_logical_error_rate']:.6g}",
        f"- Maximum decoder runtime / shot: {summary['max_decoder_runtime_seconds_per_shot']:.6g} s",
        f"- Nonincreasing distance trend checks: {summary['nonincreasing_trend_count']} / {len(summary['distance_trend_checks'])}",
        "",
        "## Results",
        "",
        "| basis | d | rounds | p | shots | failures | logical pL | 95% CI | decode s/shot |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["results"]:
        lines.append(
            f"| {row['memory_basis']} | {row['distance']} | {row['rounds']} | "
            f"{row['physical_error']:.4g} | {row['shots']} | {row['logical_failures']} | "
            f"{row['logical_error_rate']:.6g} | "
            f"[{row['wilson_95_low']:.6g}, {row['wilson_95_high']:.6g}] | "
            f"{row['decoder_runtime_seconds_per_shot']:.4g} |"
        )
    lines.extend(
        [
            "",
            "## Distance Trend Checks",
            "",
            "| basis | p | distances | logical pL by distance | nonincreasing |",
            "|---|---:|---|---|---|",
        ]
    )
    for check in summary["distance_trend_checks"]:
        rates = ", ".join(f"{value:.6g}" for value in check["logical_error_rates"])
        lines.append(
            f"| {check['memory_basis']} | {check['physical_error']:.4g} | "
            f"{check['distances']} | {rates} | {check['nonincreasing_with_distance']} |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def run_experiment(args: argparse.Namespace) -> dict:
    rows = []
    base_seed = args.seed
    for basis_index, basis in enumerate(parse_str_list(args.bases)):
        for distance_index, distance in enumerate(parse_int_list(args.distances)):
            if distance <= 0 or distance % 2 == 0:
                raise ValueError(f"distance must be positive and odd: {distance}")
            rounds = distance if args.rounds == "distance" else int(args.rounds)
            for error_index, physical_error in enumerate(parse_float_list(args.physical_errors)):
                seed = base_seed + 10000 * basis_index + 100 * distance_index + error_index
                rows.append(
                    run_config(
                        distance=distance,
                        rounds=rounds,
                        physical_error=physical_error,
                        basis=basis,
                        shots=args.shots,
                        seed=seed,
                    )
                )
    return {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 Stim/PyMatching rotated surface-code memory baseline",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "stim_pymatching_surface_code_memory_baseline",
        "method": "stim_generated_rotated_surface_code_memory_with_pymatching_decoder_v0",
        "toolchain": "Stim generated rotated_memory_x/z plus PyMatching detector-error-model decoder",
        "seed": args.seed,
        "shots_per_configuration": args.shots,
        "summary": summarize(rows),
        "results": rows,
        "limits": [
            "This is a baseline, not a new code-family improvement claim.",
            "The sweep is intentionally small and should be expanded before threshold or overhead claims.",
            "Noise is Stim's generated circuit-level phenomenological/depolarizing parameterization, not a calibrated device model.",
            "The current report does not yet compare a searched low-overhead code family against this baseline.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distances", default="3,5,7")
    parser.add_argument("--rounds", default="distance")
    parser.add_argument("--physical-errors", default="0.001,0.003,0.005,0.007,0.01")
    parser.add_argument("--bases", default="x,z")
    parser.add_argument("--shots", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=220627)
    parser.add_argument("--json-output", default="results/B2_stim_surface_code_memory_baseline_v0.json")
    parser.add_argument("--markdown-output", default="research/B2_stim_surface_code_memory_baseline.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run_experiment(args)
    json_path = Path(args.json_output)
    md_path = Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
