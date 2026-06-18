#!/usr/bin/env python3
"""Stress B10-T2 transcript verification under device-noise bridge profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from b4_b8_circuit_refresh_task import (
    REFRESH_KNOWN_FACTORS,
    build_tasks,
    parse_float_list,
    parse_int_list,
    parse_str_list,
    parity_signs,
    verify_samples,
)
from b10_t2_transcript_leakage_simulator import (
    ADVERSARIES,
    REFRESH_INDEPENDENT_MODES,
    adversary_transcript_samples,
    honest_samples,
    refreshed_masks,
    target_vector,
)


DEVICE_NOISE_PROFILES = {
    "ideal_transcript": {
        "bit_flip": 0.0,
        "readout_0_to_1": 0.0,
        "readout_1_to_0": 0.0,
        "correlated_flip": 0.0,
        "side_channel_known_fraction": 0.0,
        "bounded_bridge_profile": True,
    },
    "low_noise_bridge": {
        "bit_flip": 0.002,
        "readout_0_to_1": 0.002,
        "readout_1_to_0": 0.001,
        "correlated_flip": 0.001,
        "side_channel_known_fraction": 0.0,
        "bounded_bridge_profile": True,
    },
    "readout_biased_bridge": {
        "bit_flip": 0.003,
        "readout_0_to_1": 0.010,
        "readout_1_to_0": 0.002,
        "correlated_flip": 0.001,
        "side_channel_known_fraction": 0.04,
        "bounded_bridge_profile": True,
    },
    "drift_correlated_bridge": {
        "bit_flip": 0.006,
        "readout_0_to_1": 0.004,
        "readout_1_to_0": 0.004,
        "correlated_flip": 0.008,
        "side_channel_known_fraction": 0.08,
        "bounded_bridge_profile": True,
    },
    "calibration_side_channel": {
        "bit_flip": 0.003,
        "readout_0_to_1": 0.002,
        "readout_1_to_0": 0.002,
        "correlated_flip": 0.002,
        "side_channel_known_fraction": 0.70,
        "bounded_bridge_profile": False,
    },
}

BRIDGE_SAFE_REFRESH_MODES = {"challenge_refresh", "refresh_plus_rotation"}


def apply_device_noise(samples: np.ndarray, profile: dict, rng: np.random.Generator) -> np.ndarray:
    noisy = samples.copy()
    bit_flip = float(profile["bit_flip"])
    if bit_flip > 0:
        noisy[rng.random(noisy.shape) < bit_flip] ^= 1

    zero_to_one = float(profile["readout_0_to_1"])
    if zero_to_one > 0:
        mask = (noisy == 0) & (rng.random(noisy.shape) < zero_to_one)
        noisy[mask] = 1

    one_to_zero = float(profile["readout_1_to_0"])
    if one_to_zero > 0:
        mask = (noisy == 1) & (rng.random(noisy.shape) < one_to_zero)
        noisy[mask] = 0

    correlated_flip = float(profile["correlated_flip"])
    if correlated_flip > 0:
        shot_mask = rng.random(noisy.shape[0]) < correlated_flip
        width = max(1, noisy.shape[1] // 4)
        offset = int(rng.integers(0, noisy.shape[1]))
        columns = [(offset + idx) % noisy.shape[1] for idx in range(width)]
        noisy[np.ix_(shot_mask, columns)] ^= 1
    return noisy


def device_transcript_for_mode(
    task: dict,
    refresh_mode: str,
    leakage_fraction: float,
    invariant_count: int,
    profile: dict,
    rng: np.random.Generator,
) -> dict:
    masks = refreshed_masks(task, refresh_mode, invariant_count, rng)
    targets = target_vector(len(masks), task["qubits"])
    effective_known_fraction = min(
        1.0,
        leakage_fraction * REFRESH_KNOWN_FACTORS[refresh_mode]
        + float(profile["side_channel_known_fraction"]),
    )
    leaked_count = int(round(len(masks) * effective_known_fraction))
    if refresh_mode == "none":
        unknown_independent_count = 0
        stale_learnable_count = len(masks)
    else:
        unknown_independent_count = len(masks) - leaked_count
        stale_learnable_count = leaked_count
    refresh_independence_holds = (
        bool(profile["bounded_bridge_profile"])
        and refresh_mode in REFRESH_INDEPENDENT_MODES
        and unknown_independent_count >= 1
    )
    return {
        "masks": masks,
        "targets": targets,
        "leaked_count": leaked_count,
        "unknown_independent_count": unknown_independent_count,
        "stale_learnable_count": stale_learnable_count,
        "refresh_independence_holds": refresh_independence_holds,
        "effective_known_fraction": effective_known_fraction,
    }


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "device_noise_transcript_bridge_supports_bounded_noise_not_hardware_verifier":
        errors.append("status must identify bridge as bounded-noise transcript evidence")
    if report.get("source_target_id") != "B10-T2":
        errors.append("source target must be B10-T2")
    if report.get("device_noise_transcript_bridge_instantiated") is not True:
        errors.append("device-noise transcript bridge must be instantiated")
    if report.get("hardware_randomized_measurement_circuits_instantiated") is not False:
        errors.append("bridge must not claim hardware randomized-measurement circuits")
    if report.get("sampling_hardness_proved") is not False:
        errors.append("bridge must not claim sampling hardness")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("bridge must explicitly avoid BQP separation claims")
    if float(report.get("minimum_honest_completeness_bridge_safe_high_leakage", 0.0)) < 0.95:
        errors.append("bounded bridge profiles should preserve honest completeness")
    if float(report.get("max_soundness_bridge_safe_high_leakage", 1.0)) > 0.05:
        errors.append("bridge-safe refreshed modes should pass the 5% empirical soundness gate")
    if float(report.get("min_unknown_independent_count_bridge_safe_high_leakage", 0.0)) < 1:
        errors.append("bounded bridge profiles should retain unknown independent predicates")
    if "calibration_side_channel" not in report.get("unsafe_device_profiles", []):
        errors.append("calibration side-channel profile should be rejected")
    if "none" not in report.get("unsafe_refresh_modes_high_leakage", []):
        errors.append("no-refresh mode should remain unsafe")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def run(
    qubits: list[int],
    invariant_count: int,
    circuit_depth_factor: int,
    sample_count: int,
    reference_count: int,
    trials: int,
    tolerance: float,
    leakage_fractions: list[float],
    refresh_modes: list[str],
    device_profiles: list[str],
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    tasks = build_tasks(qubits, invariant_count, circuit_depth_factor, seed + 13000)
    rows = []

    for task in tasks:
        for profile_name in device_profiles:
            profile = DEVICE_NOISE_PROFILES[profile_name]
            for refresh_mode in refresh_modes:
                for leakage_fraction in leakage_fractions:
                    adversary_passes = {name: [] for name in ADVERSARIES}
                    adversary_errors = {name: [] for name in ADVERSARIES}
                    leaked_counts = []
                    guessed_counts = {name: [] for name in ADVERSARIES}
                    unknown_counts = []
                    independence_flags = []
                    effective_known_fractions = []
                    honest_passes = []
                    honest_errors = []

                    for _ in range(trials):
                        transcript = device_transcript_for_mode(
                            task,
                            refresh_mode,
                            leakage_fraction,
                            invariant_count,
                            profile,
                            rng,
                        )
                        calibration = honest_samples(
                            task["qubits"],
                            reference_count,
                            transcript["masks"],
                            transcript["targets"],
                            task["honest_bias"],
                            rng,
                        )
                        calibration = apply_device_noise(calibration, profile, rng)
                        reference_means = parity_signs(calibration, transcript["masks"]).mean(axis=0)

                        honest = honest_samples(
                            task["qubits"],
                            sample_count,
                            transcript["masks"],
                            transcript["targets"],
                            task["honest_bias"],
                            rng,
                        )
                        honest = apply_device_noise(honest, profile, rng)
                        honest_result = verify_samples(
                            honest,
                            transcript["masks"],
                            reference_means,
                            tolerance,
                        )
                        honest_passes.append(honest_result["passed"])
                        honest_errors.append(honest_result["max_abs_error"])
                        leaked_counts.append(transcript["leaked_count"])
                        unknown_counts.append(transcript["unknown_independent_count"])
                        independence_flags.append(transcript["refresh_independence_holds"])
                        effective_known_fractions.append(transcript["effective_known_fraction"])

                        for adversary in sorted(ADVERSARIES):
                            samples, _, guessed_count = adversary_transcript_samples(
                                task,
                                transcript,
                                refresh_mode,
                                adversary,
                                sample_count,
                                rng,
                            )
                            samples = apply_device_noise(samples, profile, rng)
                            result = verify_samples(
                                samples,
                                transcript["masks"],
                                reference_means,
                                tolerance,
                            )
                            adversary_passes[adversary].append(result["passed"])
                            adversary_errors[adversary].append(result["max_abs_error"])
                            guessed_counts[adversary].append(guessed_count)

                    for adversary in sorted(ADVERSARIES):
                        rows.append(
                            {
                                "task_id": task["task_id"],
                                "qubits": task["qubits"],
                                "device_profile": profile_name,
                                "bounded_bridge_profile": bool(profile["bounded_bridge_profile"]),
                                "refresh_mode": refresh_mode,
                                "leakage_fraction": leakage_fraction,
                                "adversary": adversary,
                                "mean_effective_known_fraction": float(np.mean(effective_known_fractions)),
                                "mean_leaked_predicate_count": float(np.mean(leaked_counts)),
                                "mean_guessed_hidden_predicate_count": float(np.mean(guessed_counts[adversary])),
                                "mean_unknown_independent_predicate_count": float(np.mean(unknown_counts)),
                                "refresh_independence_holds": bool(all(independence_flags)),
                                "honest_completeness": float(np.mean(honest_passes)),
                                "mean_honest_max_abs_error": float(np.mean(honest_errors)),
                                "empirical_soundness": float(np.mean(adversary_passes[adversary])),
                                "mean_adversary_max_abs_error": float(np.mean(adversary_errors[adversary])),
                            }
                        )

    summary_by_profile_mode = []
    for profile_name in device_profiles:
        for refresh_mode in refresh_modes:
            for leakage_fraction in leakage_fractions:
                subset = [
                    row
                    for row in rows
                    if row["device_profile"] == profile_name
                    and row["refresh_mode"] == refresh_mode
                    and row["leakage_fraction"] == leakage_fraction
                ]
                summary_by_profile_mode.append(
                    {
                        "device_profile": profile_name,
                        "bounded_bridge_profile": bool(DEVICE_NOISE_PROFILES[profile_name]["bounded_bridge_profile"]),
                        "refresh_mode": refresh_mode,
                        "leakage_fraction": leakage_fraction,
                        "honest_completeness": min(row["honest_completeness"] for row in subset),
                        "max_empirical_soundness": max(row["empirical_soundness"] for row in subset),
                        "mean_empirical_soundness": sum(row["empirical_soundness"] for row in subset) / len(subset),
                        "min_unknown_independent_predicate_count": min(
                            row["mean_unknown_independent_predicate_count"] for row in subset
                        ),
                        "refresh_independence_holds": all(row["refresh_independence_holds"] for row in subset),
                        "adversaries_over_5pct_soundness": sorted(
                            {
                                row["adversary"]
                                for row in subset
                                if row["empirical_soundness"] > 0.05
                            }
                        ),
                    }
                )

    high_leakage = [row for row in summary_by_profile_mode if row["leakage_fraction"] >= 0.75]
    bridge_safe_high = [
        row
        for row in high_leakage
        if row["bounded_bridge_profile"]
        and row["refresh_mode"] in BRIDGE_SAFE_REFRESH_MODES
        and row["refresh_independence_holds"]
    ]
    margin_sensitive_high = [
        row
        for row in high_leakage
        if row["bounded_bridge_profile"]
        and row["refresh_mode"] == "projection_rotation"
        and row["max_empirical_soundness"] > 0.05
    ]
    unsafe_device_profiles = sorted(
        {
            row["device_profile"]
            for row in high_leakage
            if row["max_empirical_soundness"] > 0.05
            or not row["refresh_independence_holds"]
        }
        - {
            row["device_profile"]
            for row in high_leakage
            if row["bounded_bridge_profile"]
            and row["refresh_mode"] in BRIDGE_SAFE_REFRESH_MODES
            and row["refresh_independence_holds"]
            and row["max_empirical_soundness"] <= 0.05
        }
    )
    unsafe_refresh_modes = sorted(
        {
            row["refresh_mode"]
            for row in high_leakage
            if row["max_empirical_soundness"] > 0.05
            or not row["refresh_independence_holds"]
        }
    )

    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T2 device-noise transcript bridge",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "device_noise_transcript_bridge_supports_bounded_noise_not_hardware_verifier",
        "method": "b10_t2_device_noise_transcript_bridge_v0",
        "source_target_id": "B10-T2",
        "source_simulator": "b10_t2_transcript_leakage_simulator_v0",
        "dependency_benchmark": "B8",
        "explicit_not_bqp_separation": True,
        "device_noise_transcript_bridge_instantiated": True,
        "hardware_randomized_measurement_circuits_instantiated": False,
        "sampling_hardness_proved": False,
        "task_count": len(tasks),
        "configuration_count": len(rows),
        "device_profile_count": len(device_profiles),
        "device_profiles": device_profiles,
        "qubits": qubits,
        "invariant_count": invariant_count,
        "sample_count": sample_count,
        "reference_count": reference_count,
        "trials": trials,
        "tolerance": tolerance,
        "refresh_modes": refresh_modes,
        "leakage_fractions": leakage_fractions,
        "adversaries_tested": sorted(ADVERSARIES),
        "minimum_honest_completeness": min(row["honest_completeness"] for row in rows),
        "maximum_empirical_soundness": max(row["empirical_soundness"] for row in rows),
        "minimum_honest_completeness_bridge_safe_high_leakage": min(
            row["honest_completeness"] for row in bridge_safe_high
        ),
        "max_soundness_bridge_safe_high_leakage": max(
            row["max_empirical_soundness"] for row in bridge_safe_high
        ),
        "min_unknown_independent_count_bridge_safe_high_leakage": min(
            row["min_unknown_independent_predicate_count"] for row in bridge_safe_high
        ),
        "bridge_safe_device_profiles": sorted({row["device_profile"] for row in bridge_safe_high}),
        "bridge_safe_refresh_modes": sorted(BRIDGE_SAFE_REFRESH_MODES),
        "margin_sensitive_refresh_modes": sorted({row["refresh_mode"] for row in margin_sensitive_high}),
        "margin_sensitive_profile_modes": [
            {
                "device_profile": row["device_profile"],
                "refresh_mode": row["refresh_mode"],
                "leakage_fraction": row["leakage_fraction"],
                "max_empirical_soundness": row["max_empirical_soundness"],
            }
            for row in margin_sensitive_high
        ],
        "unsafe_device_profiles": unsafe_device_profiles,
        "unsafe_refresh_modes_high_leakage": unsafe_refresh_modes,
        "summary_by_profile_mode": summary_by_profile_mode,
        "results": rows,
        "limits": [
            "This is a device-noise transcript bridge, not hardware execution.",
            "Noise is calibrated through transcript-level honest reference samples, not through real device calibration data.",
            "The calibration_side_channel profile is intentionally rejected because it violates refresh independence.",
            "The bridge does not prove sampling hardness, cryptographic soundness, or BQP/classical separation.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B10-T2 Device-Noise Transcript Bridge v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']}",
        f"- Source simulator: {report['source_simulator']}",
        f"- Method: {report['method']}",
        f"- Configurations: {report['configuration_count']}",
        f"- Device profiles: {report['device_profiles']}",
        f"- Minimum honest completeness: {report['minimum_honest_completeness']:.3f}",
        f"- Bridge-safe high-leakage honest completeness: {report['minimum_honest_completeness_bridge_safe_high_leakage']:.3f}",
        f"- Bridge-safe high-leakage max soundness: {report['max_soundness_bridge_safe_high_leakage']:.3f}",
        f"- Bridge-safe min unknown independent predicates: {report['min_unknown_independent_count_bridge_safe_high_leakage']:.1f}",
        f"- Bridge-safe refresh modes: {report['bridge_safe_refresh_modes']}",
        f"- Bridge-safe device profiles: {report['bridge_safe_device_profiles']}",
        f"- Margin-sensitive refresh modes: {report['margin_sensitive_refresh_modes']}",
        f"- Margin-sensitive profile/mode rows: {report['margin_sensitive_profile_modes']}",
        f"- Unsafe device profiles: {report['unsafe_device_profiles']}",
        f"- Unsafe high-leakage refresh modes: {report['unsafe_refresh_modes_high_leakage']}",
        f"- Device-noise transcript bridge instantiated: {report['device_noise_transcript_bridge_instantiated']}",
        f"- Hardware randomized-measurement circuits instantiated: {report['hardware_randomized_measurement_circuits_instantiated']}",
        f"- Sampling hardness proved: {report['sampling_hardness_proved']}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## High-Leakage Boundary By Profile",
        "",
        "| profile | mode | bounded | honest | independence | min unknown | max soundness | adversaries over 5% |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["summary_by_profile_mode"]:
        if row["leakage_fraction"] < 0.75:
            continue
        adversaries = ", ".join(row["adversaries_over_5pct_soundness"]) or "none"
        lines.append(
            f"| {row['device_profile']} | {row['refresh_mode']} | {row['bounded_bridge_profile']} | "
            f"{row['honest_completeness']:.3f} | {row['refresh_independence_holds']} | "
            f"{row['min_unknown_independent_predicate_count']:.1f} | "
            f"{row['max_empirical_soundness']:.3f} | {adversaries} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Supported: bounded device-noise transcript profiles preserve calibrated honest completeness and keep challenge_refresh / refresh_plus_rotation high-leakage empirical soundness below 5% in this proxy.",
            "- Margin-sensitive: projection_rotation can exceed the 5% empirical gate under low-noise transcript calibration and should not be counted as bridge-safe without extra margin.",
            "- Rejected: no-refresh and calibration-side-channel profiles do not satisfy the B10-T2 refresh-independence bridge.",
            "- Not claimed: real hardware execution, cryptographic soundness, sampling hardness, or BQP/classical separation.",
            "",
            "## Limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", default="12,16,20")
    parser.add_argument("--invariant-count", type=int, default=10)
    parser.add_argument("--circuit-depth-factor", type=int, default=4)
    parser.add_argument("--sample-count", type=int, default=4096)
    parser.add_argument("--reference-count", type=int, default=12000)
    parser.add_argument("--trials", type=int, default=48)
    parser.add_argument("--tolerance", type=float, default=0.10)
    parser.add_argument("--leakage-fractions", default="0.5,0.75")
    parser.add_argument("--refresh-modes", default="none,projection_rotation,challenge_refresh,refresh_plus_rotation")
    parser.add_argument(
        "--device-profiles",
        default="ideal_transcript,low_noise_bridge,readout_biased_bridge,drift_correlated_bridge,calibration_side_channel",
    )
    parser.add_argument("--seed", type=int, default=20260617)
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t2_device_noise_transcript_bridge_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t2_device_noise_transcript_bridge.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    device_profiles = parse_str_list(args.device_profiles)
    unknown_profiles = sorted(set(device_profiles) - set(DEVICE_NOISE_PROFILES))
    if unknown_profiles:
        raise SystemExit(f"unknown device profiles: {unknown_profiles}")

    report = run(
        qubits=parse_int_list(args.qubits),
        invariant_count=args.invariant_count,
        circuit_depth_factor=args.circuit_depth_factor,
        sample_count=args.sample_count,
        reference_count=args.reference_count,
        trials=args.trials,
        tolerance=args.tolerance,
        leakage_fractions=parse_float_list(args.leakage_fractions),
        refresh_modes=parse_str_list(args.refresh_modes),
        device_profiles=device_profiles,
        seed=args.seed,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "configuration_count": report["configuration_count"],
                    "bridge_safe_device_profiles": report["bridge_safe_device_profiles"],
                    "unsafe_device_profiles": report["unsafe_device_profiles"],
                    "max_soundness_bridge_safe_high_leakage": report["max_soundness_bridge_safe_high_leakage"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
