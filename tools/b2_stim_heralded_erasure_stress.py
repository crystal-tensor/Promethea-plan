#!/usr/bin/env python3
"""Stress B2 leakage-erasure pressure with Stim HERALDED_ERASE circuits."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pymatching
import stim


METHOD = "b2_stim_heralded_erasure_stress_v0"
STATUS = "stim_heralded_erasure_stress_boundary_not_full_leakage_decoder"
TARGETS = [0.1, 0.05, 0.02, 0.01]


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


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


def base_circuit(distance: int, physical_error: float, basis: str) -> stim.Circuit:
    return stim.Circuit.generated(
        generated_task_name(basis),
        distance=distance,
        rounds=distance,
        after_clifford_depolarization=physical_error,
        before_round_data_depolarization=physical_error,
        before_measure_flip_probability=physical_error,
        after_reset_flip_probability=physical_error,
    )


def inject_tick_noise(circuit: stim.Circuit, mode: str, leakage_rate: float) -> stim.Circuit:
    if leakage_rate <= 0:
        return circuit
    output = stim.Circuit()
    qubits = list(range(circuit.num_qubits))
    for instruction in circuit:
        output.append(instruction)
        if getattr(instruction, "name", None) == "TICK":
            if mode == "unheralded_depolarizing_leakage_proxy":
                output.append("DEPOLARIZE1", qubits, leakage_rate)
            elif mode == "heralded_erasure_proxy":
                output.append("HERALDED_ERASE", qubits, leakage_rate)
            else:
                raise ValueError(f"unsupported leakage stress mode: {mode}")
    return output


def run_config(
    mode: str,
    distance: int,
    physical_error: float,
    leakage_rate: float,
    basis: str,
    shots: int,
    seed: int,
) -> dict:
    started_build = time.perf_counter()
    circuit = inject_tick_noise(base_circuit(distance, physical_error, basis), mode, leakage_rate)
    dem = circuit.detector_error_model(decompose_errors=True, approximate_disjoint_errors=True)
    matching = pymatching.Matching.from_detector_error_model(dem)
    build_seconds = time.perf_counter() - started_build

    started_sample = time.perf_counter()
    detection_events, observables = circuit.compile_detector_sampler(seed=seed).sample(
        shots,
        separate_observables=True,
    )
    sample_seconds = time.perf_counter() - started_sample

    started_decode = time.perf_counter()
    predictions = matching.decode_batch(detection_events)
    decode_seconds = time.perf_counter() - started_decode

    failures = int(np.count_nonzero(np.any(predictions != observables, axis=1)))
    logical_error_rate = failures / shots
    low, high = wilson_interval(failures, shots)
    return {
        "mode": mode,
        "code_family": "stim_generated_rotated_surface_code_memory",
        "stim_task": generated_task_name(basis),
        "memory_basis": basis,
        "distance": distance,
        "rounds": distance,
        "physical_error": physical_error,
        "leakage_rate_per_tick": leakage_rate,
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
        "space_time_volume": int(circuit.num_qubits) * int(distance),
        "build_seconds": build_seconds,
        "sample_seconds": sample_seconds,
        "decode_seconds": decode_seconds,
        "decoder_runtime_seconds_per_shot": decode_seconds / shots if shots else 0.0,
        "seed": seed,
    }


def metric_value(row: dict, criterion: str) -> float:
    if criterion == "wilson_95_high":
        return float(row["wilson_95_high"])
    if criterion == "observed_logical_error_rate":
        return float(row["logical_error_rate"])
    raise ValueError(f"unsupported criterion: {criterion}")


def best_for_target(
    rows: list[dict],
    mode: str,
    basis: str,
    physical_error: float,
    leakage_rate: float,
    target: float,
    criterion: str,
    volume_overhead: float,
) -> dict | None:
    candidates = [
        {
            **row,
            "overhead_adjusted_space_time_volume": row["space_time_volume"] * volume_overhead,
        }
        for row in rows
        if row["mode"] == mode
        and row["memory_basis"] == basis
        and float(row["physical_error"]) == physical_error
        and float(row["leakage_rate_per_tick"]) == leakage_rate
        and metric_value(row, criterion) <= target
    ]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda row: (
            row["overhead_adjusted_space_time_volume"],
            row["distance"],
            metric_value(row, criterion),
        ),
    )


def compare_targets(rows: list[dict], targets: list[float], criterion: str, flag_overhead: float) -> list[dict]:
    bases = sorted({row["memory_basis"] for row in rows})
    physical_errors = sorted({float(row["physical_error"]) for row in rows})
    leakage_rates = sorted({float(row["leakage_rate_per_tick"]) for row in rows})
    comparisons = []
    for basis in bases:
        for physical_error in physical_errors:
            for leakage_rate in leakage_rates:
                for target in targets:
                    baseline = best_for_target(
                        rows,
                        mode="unheralded_depolarizing_leakage_proxy",
                        basis=basis,
                        physical_error=physical_error,
                        leakage_rate=leakage_rate,
                        target=target,
                        criterion=criterion,
                        volume_overhead=1.0,
                    )
                    candidate = best_for_target(
                        rows,
                        mode="heralded_erasure_proxy",
                        basis=basis,
                        physical_error=physical_error,
                        leakage_rate=leakage_rate,
                        target=target,
                        criterion=criterion,
                        volume_overhead=flag_overhead,
                    )
                    baseline_volume = baseline["overhead_adjusted_space_time_volume"] if baseline else None
                    candidate_volume = candidate["overhead_adjusted_space_time_volume"] if candidate else None
                    reduction = (
                        baseline_volume / candidate_volume
                        if baseline_volume is not None and candidate_volume is not None
                        else None
                    )
                    comparisons.append(
                        {
                            "memory_basis": basis,
                            "physical_error": physical_error,
                            "leakage_rate_per_tick": leakage_rate,
                            "target_logical_error": target,
                            "criterion": criterion,
                            "baseline_met": baseline is not None,
                            "baseline_distance": baseline["distance"] if baseline else None,
                            "baseline_metric_value": metric_value(baseline, criterion) if baseline else None,
                            "baseline_space_time_volume": baseline_volume,
                            "candidate_met": candidate is not None,
                            "candidate_distance": candidate["distance"] if candidate else None,
                            "candidate_metric_value": metric_value(candidate, criterion) if candidate else None,
                            "candidate_space_time_volume": candidate_volume,
                            "candidate_raw_space_time_volume": candidate["space_time_volume"] if candidate else None,
                            "flag_overhead": flag_overhead,
                            "volume_reduction_vs_baseline": reduction,
                            "improved_volume": bool(reduction is not None and reduction > 1.0),
                            "candidate_only_meets_target": candidate is not None and baseline is None,
                            "candidate_distance_5_or_7": candidate["distance"] in {5, 7} if candidate else False,
                        }
                    )
    return comparisons


def summarize(rows: list[dict], comparisons: list[dict]) -> dict:
    improved = [row for row in comparisons if row["improved_volume"]]
    candidate_only = [row for row in comparisons if row["candidate_only_meets_target"]]
    d5_d7 = [row for row in improved if row["candidate_distance_5_or_7"]]
    reductions = [row["volume_reduction_vs_baseline"] for row in improved]
    by_mode = {}
    for mode in sorted({row["mode"] for row in rows}):
        subset = [row for row in rows if row["mode"] == mode]
        by_mode[mode] = {
            "configuration_count": len(subset),
            "total_shots": sum(row["shots"] for row in subset),
            "mean_wilson_95_high": sum(row["wilson_95_high"] for row in subset) / len(subset),
            "max_wilson_95_high": max(row["wilson_95_high"] for row in subset),
            "min_wilson_95_high": min(row["wilson_95_high"] for row in subset),
            "max_decoder_runtime_seconds_per_shot": max(
                row["decoder_runtime_seconds_per_shot"] for row in subset
            ),
        }
    return {
        "configuration_count": len(rows),
        "total_shots": sum(row["shots"] for row in rows),
        "target_comparisons": len(comparisons),
        "baseline_met_count": sum(1 for row in comparisons if row["baseline_met"]),
        "candidate_met_count": sum(1 for row in comparisons if row["candidate_met"]),
        "candidate_only_meets_target_count": len(candidate_only),
        "improved_volume_count": len(improved),
        "distance_5_7_improved_count": len(d5_d7),
        "max_volume_reduction": max(reductions) if reductions else None,
        "mean_volume_reduction_on_improved": (
            sum(reductions) / len(reductions) if reductions else None
        ),
        "modes": by_mode,
        "distances": sorted({row["distance"] for row in rows}),
        "physical_errors": sorted({float(row["physical_error"]) for row in rows}),
        "leakage_rates_per_tick": sorted({float(row["leakage_rate_per_tick"]) for row in rows}),
        "memory_bases": sorted({row["memory_basis"] for row in rows}),
    }


def validate(report: dict) -> list[str]:
    summary = report["summary"]
    claims = report["claim_boundary"]
    errors = []
    if summary["configuration_count"] <= 0:
        errors.append("configuration_count must be positive")
    if summary["target_comparisons"] <= 0:
        errors.append("target_comparisons must be positive")
    if summary["improved_volume_count"] <= 0:
        errors.append("expected at least one heralded-erasure target-volume improvement row")
    if summary["distance_5_7_improved_count"] <= 0:
        errors.append("expected at least one distance-5/7 target-volume improvement row")
    if claims.get("new_code_claimed") is not False:
        errors.append("must not claim a new code")
    if claims.get("threshold_claimed") is not False:
        errors.append("must not claim a threshold")
    if claims.get("calibrated_device_claimed") is not False:
        errors.append("must not claim calibrated device evidence")
    if claims.get("full_physical_leakage_decoder_claimed") is not False:
        errors.append("must not claim a full physical leakage decoder")
    return errors


def build_report(args: argparse.Namespace) -> dict:
    rows = []
    config_index = 0
    modes = [
        "unheralded_depolarizing_leakage_proxy",
        "heralded_erasure_proxy",
    ]
    for basis in parse_str_list(args.bases):
        for physical_error in parse_float_list(args.physical_errors):
            for leakage_rate in parse_float_list(args.leakage_rates):
                for distance in parse_int_list(args.distances):
                    for mode in modes:
                        config_index += 1
                        rows.append(
                            run_config(
                                mode=mode,
                                distance=distance,
                                physical_error=physical_error,
                                leakage_rate=leakage_rate,
                                basis=basis,
                                shots=args.shots,
                                seed=args.seed + config_index,
                            )
                        )
    comparisons = compare_targets(
        rows=rows,
        targets=parse_float_list(args.targets),
        criterion=args.criterion,
        flag_overhead=args.flag_overhead,
    )
    report = {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 Stim heralded-erasure leakage stress",
        "version": "0.1",
        "last_updated": args.last_updated,
        "status": STATUS,
        "method": METHOD,
        "model_status": "stim_generated_surface_code_with_tick_level_unheralded_vs_heralded_erasure_noise",
        "toolchain": "Stim HERALDED_ERASE / DEPOLARIZE1 plus PyMatching detector-error-model decoder",
        "criterion": args.criterion,
        "flag_overhead": args.flag_overhead,
        "shots_per_configuration": args.shots,
        "parameters": {
            "distances": parse_int_list(args.distances),
            "physical_errors": parse_float_list(args.physical_errors),
            "leakage_rates_per_tick": parse_float_list(args.leakage_rates),
            "memory_bases": parse_str_list(args.bases),
            "targets": parse_float_list(args.targets),
            "seed": args.seed,
        },
        "summary": summarize(rows, comparisons),
        "claim_boundary": {
            "new_code_claimed": False,
            "threshold_claimed": False,
            "calibrated_device_claimed": False,
            "full_physical_leakage_decoder_claimed": False,
            "shot_conditioned_erasure_decoder_claimed": False,
            "circuit_derived_stim_evidence": True,
            "reduced_rounds_used": False,
            "distance_3_candidate_used": False,
            "what_is_supported": (
                "Under a Stim generated rotated-surface-code memory circuit with tick-level "
                "DEPOLARIZE1 versus HERALDED_ERASE leakage proxies, the heralded-erasure "
                "proxy can lower Wilson target-volume pressure on some d=5/d=7 rows after "
                "a declared flag-overhead penalty."
            ),
            "what_is_not_supported": (
                "This is not a calibrated leakage model, threshold estimate, new code, "
                "hardware result, or full shot-conditioned erasure decoder."
            ),
        },
        "results": rows,
        "comparisons": comparisons,
    }
    report["validation_errors"] = validate(report)
    return report


def write_markdown(report: dict, path: Path) -> None:
    summary = report["summary"]
    improved = [row for row in report["comparisons"] if row["improved_volume"]]
    improved.sort(
        key=lambda row: (
            -(row["volume_reduction_vs_baseline"] or 0.0),
            row["physical_error"],
            row["leakage_rate_per_tick"],
            row["target_logical_error"],
            row["memory_basis"],
        )
    )
    lines = [
        "# B2 Stim Heralded-Erasure Leakage Stress v0.1",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: {report['method']}",
        f"- Model status: {report['model_status']}",
        f"- Toolchain: {report['toolchain']}",
        f"- Configurations: {summary['configuration_count']}",
        f"- Total shots: {summary['total_shots']}",
        f"- Target comparisons: {summary['target_comparisons']}",
        f"- Baseline met count: {summary['baseline_met_count']}",
        f"- Candidate met count: {summary['candidate_met_count']}",
        f"- Candidate-only target hits: {summary['candidate_only_meets_target_count']}",
        f"- Improved target-volume rows: {summary['improved_volume_count']}",
        f"- Improved rows with candidate distance 5 or 7: {summary['distance_5_7_improved_count']}",
        f"- Max volume reduction after flag overhead: {summary['max_volume_reduction']}",
        f"- Mean volume reduction after flag overhead: {summary['mean_volume_reduction_on_improved']}",
        f"- Validation errors: {report['validation_errors']}",
        "",
        "## Mode Summary",
        "",
        "| mode | configs | shots | mean Wilson high | min Wilson high | max Wilson high | max decode s/shot |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for mode, row in summary["modes"].items():
        lines.append(
            f"| {mode} | {row['configuration_count']} | {row['total_shots']} | "
            f"{row['mean_wilson_95_high']:.6g} | {row['min_wilson_95_high']:.6g} | "
            f"{row['max_wilson_95_high']:.6g} | {row['max_decoder_runtime_seconds_per_shot']:.6g} |"
        )
    lines.extend(
        [
            "",
            "## Improved Target-Volume Rows",
            "",
            "| basis | p | leakage/tick | target | baseline d | candidate d | baseline volume | candidate volume | reduction |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in improved[:20]:
        lines.append(
            f"| {row['memory_basis']} | {row['physical_error']:.4g} | "
            f"{row['leakage_rate_per_tick']:.4g} | {row['target_logical_error']:.4g} | "
            f"{row['baseline_distance']} | {row['candidate_distance']} | "
            f"{row['baseline_space_time_volume']:.2f} | {row['candidate_space_time_volume']:.2f} | "
            f"{row['volume_reduction_vs_baseline']:.3f}x |"
        )
    if not improved:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
        ]
    )
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            "Replace this detector-error-model stress with either a shot-conditioned erasure",
            "decoder, a more realistic leakage circuit model, or calibrated backend leakage",
            "data. The result should be demoted if the d=5/d=7 volume rows disappear under",
            "that stronger model.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distances", default="5,7,9")
    parser.add_argument("--physical-errors", default="0.001,0.003,0.005")
    parser.add_argument("--leakage-rates", default="0.003,0.005,0.01")
    parser.add_argument("--bases", default="x,z")
    parser.add_argument("--targets", default="0.1,0.05,0.02,0.01")
    parser.add_argument("--criterion", choices=["wilson_95_high", "observed_logical_error_rate"], default="wilson_95_high")
    parser.add_argument("--flag-overhead", type=float, default=1.15)
    parser.add_argument("--shots", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=220628)
    parser.add_argument("--last-updated", default="2026-06-18")
    parser.add_argument("--json-output", type=Path, default=Path("results/B2_stim_heralded_erasure_stress_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B2_stim_heralded_erasure_stress.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(report, args.markdown_output)
    print(
        json.dumps(
            {
                "status": report["status"],
                "method": report["method"],
                **report["summary"],
                "validation_errors": report["validation_errors"],
            },
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
