#!/usr/bin/env python3
"""Simulate B10-T2 transcript leakage under refresh-independence assumptions."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from b4_b8_circuit_refresh_task import (
    REFRESH_KNOWN_FACTORS,
    build_tasks,
    enforce_invariants,
    parse_float_list,
    parse_int_list,
    parse_str_list,
    parity_signs,
    random_cnot_gates,
    verify_samples,
)


ADVERSARIES = {
    "leaked_predicate_replayer": {
        "uses_stale_transcript": False,
        "hidden_guess_fraction": 0.0,
        "hidden_guess_accuracy": 0.50,
        "leaked_strength": 1.02,
        "hidden_strength": 0.0,
    },
    "stale_transcript_learner": {
        "uses_stale_transcript": True,
        "hidden_guess_fraction": 0.25,
        "hidden_guess_accuracy": 0.54,
        "leaked_strength": 1.04,
        "hidden_strength": 0.35,
    },
    "generative_mask_searcher": {
        "uses_stale_transcript": False,
        "hidden_guess_fraction": 0.55,
        "hidden_guess_accuracy": 0.55,
        "leaked_strength": 1.04,
        "hidden_strength": 0.55,
    },
    "oracle_cover_spoofer": {
        "uses_stale_transcript": True,
        "hidden_guess_fraction": 1.0,
        "hidden_guess_accuracy": 0.50,
        "leaked_strength": 1.05,
        "hidden_strength": 1.05,
    },
}


REFRESH_INDEPENDENT_MODES = {"projection_rotation", "challenge_refresh", "refresh_plus_rotation"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def random_masks(qubits: int, count: int, rng: np.random.Generator) -> list[list[int]]:
    if count > qubits:
        raise ValueError("transcript predicate count cannot exceed qubits in independent-coordinate mode")
    return [[int(idx)] for idx in rng.choice(qubits, size=count, replace=False).tolist()]


def rotated_masks(masks: list[list[int]], qubits: int, rng: np.random.Generator) -> list[list[int]]:
    permutation = rng.permutation(qubits)
    return [sorted(int(permutation[idx]) for idx in mask) for mask in masks]


def refreshed_masks(task: dict, refresh_mode: str, invariant_count: int, rng: np.random.Generator) -> list[list[int]]:
    base_masks = [[idx] for idx in range(invariant_count)]
    if refresh_mode == "none":
        return base_masks
    if refresh_mode == "projection_rotation":
        return rotated_masks(base_masks, task["qubits"], rng)
    if refresh_mode == "challenge_refresh":
        return random_masks(task["qubits"], invariant_count, rng)
    if refresh_mode == "refresh_plus_rotation":
        base = random_masks(task["qubits"], invariant_count, rng)
        return rotated_masks(base, task["qubits"], rng)
    raise ValueError(f"unknown refresh mode {refresh_mode!r}")


def target_vector(count: int, qubits: int) -> np.ndarray:
    return np.array([1 if (idx + qubits) % 3 != 1 else -1 for idx in range(count)])


def honest_samples(
    qubits: int,
    sample_count: int,
    masks: list[list[int]],
    targets: np.ndarray,
    honest_bias: float,
    rng: np.random.Generator,
) -> np.ndarray:
    samples = rng.integers(0, 2, size=(sample_count, qubits), dtype=np.int8)
    return enforce_invariants(samples, masks, targets, honest_bias, rng)


def guessed_targets(true_targets: np.ndarray, accuracy: float, rng: np.random.Generator) -> np.ndarray:
    guesses = true_targets.copy()
    correct = rng.random(len(true_targets)) < accuracy
    guesses[~correct] *= -1
    return guesses


def transcript_for_mode(
    task: dict,
    refresh_mode: str,
    leakage_fraction: float,
    invariant_count: int,
    rng: np.random.Generator,
) -> dict:
    masks = refreshed_masks(task, refresh_mode, invariant_count, rng)
    targets = target_vector(len(masks), task["qubits"])
    effective_known_fraction = min(1.0, leakage_fraction * REFRESH_KNOWN_FACTORS[refresh_mode])
    leaked_count = int(round(len(masks) * effective_known_fraction))
    if refresh_mode == "none":
        # Without refresh, repeated transcript access invalidates the independence
        # assumption; a stale learner can recover all predicates over time.
        unknown_independent_count = 0
        stale_learnable_count = len(masks)
    else:
        unknown_independent_count = len(masks) - leaked_count
        stale_learnable_count = leaked_count
    return {
        "masks": masks,
        "targets": targets,
        "leaked_count": leaked_count,
        "unknown_independent_count": unknown_independent_count,
        "stale_learnable_count": stale_learnable_count,
        "refresh_independence_holds": refresh_mode in REFRESH_INDEPENDENT_MODES and unknown_independent_count >= 1,
    }


def adversary_transcript_samples(
    task: dict,
    transcript: dict,
    refresh_mode: str,
    adversary: str,
    sample_count: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, int, int]:
    spec = ADVERSARIES[adversary]
    masks = transcript["masks"]
    targets = transcript["targets"]
    leaked_count = transcript["leaked_count"]
    leaked_masks = masks[:leaked_count]
    leaked_targets = targets[:leaked_count]
    hidden_masks = masks[leaked_count:]
    hidden_targets = targets[leaked_count:]

    samples = rng.integers(0, 2, size=(sample_count, task["qubits"]), dtype=np.int8)
    samples = enforce_invariants(
        samples,
        leaked_masks,
        leaked_targets,
        task["honest_bias"] * spec["leaked_strength"],
        rng,
    )

    if refresh_mode == "none" and spec["uses_stale_transcript"]:
        chosen_hidden_masks = hidden_masks
        chosen_hidden_targets = hidden_targets
    else:
        guess_count = int(round(len(hidden_masks) * spec["hidden_guess_fraction"]))
        chosen_hidden_masks = hidden_masks[:guess_count]
        chosen_hidden_targets = guessed_targets(hidden_targets[:guess_count], spec["hidden_guess_accuracy"], rng)

    samples = enforce_invariants(
        samples,
        chosen_hidden_masks,
        chosen_hidden_targets,
        task["honest_bias"] * spec["hidden_strength"],
        rng,
    )
    return samples, leaked_count, len(chosen_hidden_masks)


def hoeffding_bound(sample_count: int, honest_signal: float, tolerance: float, unknown_count: int) -> float:
    if unknown_count <= 0:
        return 1.0
    gap = honest_signal - tolerance
    if gap <= 0:
        return 1.0
    return math.exp(-sample_count * gap * gap / 2.0) ** unknown_count


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "transcript_leakage_simulator_supports_restricted_lemma_not_hardware_verifier":
        errors.append("status must identify simulator as not a hardware verifier")
    if report.get("source_target_id") != "B10-T2":
        errors.append("source target must be B10-T2")
    if report.get("hardware_randomized_measurement_circuits_instantiated") is not False:
        errors.append("simulator must not claim hardware randomized-measurement circuits")
    if report.get("sampling_hardness_proved") is not False:
        errors.append("simulator must not claim sampling hardness")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("simulator must explicitly avoid BQP separation claims")
    if "none" not in report.get("unsafe_high_leakage_modes", []):
        errors.append("no-refresh high leakage should remain unsafe")
    required_safe = {"projection_rotation", "challenge_refresh", "refresh_plus_rotation"}
    if not required_safe <= set(report.get("refresh_independent_high_leakage_modes", [])):
        errors.append("all refreshed modes should satisfy high-leakage refresh independence in this simulator")
    if report.get("max_soundness_refresh_independent_high_leakage", 1.0) > 0.05:
        errors.append("refresh-independent high-leakage modes should pass the 5% empirical gate")
    if report.get("min_unknown_independent_count_refresh_high_leakage", 0) < 1:
        errors.append("refreshed high-leakage modes should retain at least one unknown independent predicate")
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
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    tasks = build_tasks(qubits, invariant_count, circuit_depth_factor, seed + 11000)
    rows = []
    honest_completeness_by_task = {}

    for task in tasks:
        for refresh_mode in refresh_modes:
            for leakage_fraction in leakage_fractions:
                for adversary in sorted(ADVERSARIES):
                    pass_flags = []
                    max_errors = []
                    leaked_counts = []
                    guessed_counts = []
                    unknown_counts = []
                    independence_flags = []
                    theory_bounds = []
                    honest_passes = []
                    for _ in range(trials):
                        transcript = transcript_for_mode(task, refresh_mode, leakage_fraction, invariant_count, rng)
                        reference_means = transcript["targets"] * ((1.0 + task["honest_bias"]) / 2.0)
                        honest = honest_samples(
                            task["qubits"],
                            sample_count,
                            transcript["masks"],
                            transcript["targets"],
                            task["honest_bias"],
                            rng,
                        )
                        honest_passes.append(
                            verify_samples(honest, transcript["masks"], reference_means, tolerance)["passed"]
                        )
                        samples, leaked_count, guessed_count = adversary_transcript_samples(
                            task,
                            transcript,
                            refresh_mode,
                            adversary,
                            sample_count,
                            rng,
                        )
                        result = verify_samples(samples, transcript["masks"], reference_means, tolerance)
                        pass_flags.append(result["passed"])
                        max_errors.append(result["max_abs_error"])
                        leaked_counts.append(leaked_count)
                        guessed_counts.append(guessed_count)
                        unknown_counts.append(transcript["unknown_independent_count"])
                        independence_flags.append(transcript["refresh_independence_holds"])
                        theory_bounds.append(
                            hoeffding_bound(
                                sample_count,
                                task["honest_bias"],
                                tolerance,
                                transcript["unknown_independent_count"],
                            )
                        )
                    honest_completeness_by_task.setdefault(task["task_id"], []).extend(honest_passes)
                    rows.append(
                        {
                            "task_id": task["task_id"],
                            "qubits": task["qubits"],
                            "refresh_mode": refresh_mode,
                            "leakage_fraction": leakage_fraction,
                            "adversary": adversary,
                            "mean_leaked_predicate_count": float(np.mean(leaked_counts)),
                            "mean_guessed_hidden_predicate_count": float(np.mean(guessed_counts)),
                            "mean_unknown_independent_predicate_count": float(np.mean(unknown_counts)),
                            "refresh_independence_holds": bool(all(independence_flags)),
                            "mean_theoretical_bound": float(np.mean(theory_bounds)),
                            "honest_completeness": float(np.mean(honest_passes)),
                            "empirical_soundness": float(np.mean(pass_flags)),
                            "mean_max_abs_error": float(np.mean(max_errors)),
                        }
                    )

    summary_by_mode = []
    for refresh_mode in refresh_modes:
        for leakage_fraction in leakage_fractions:
            subset = [
                row
                for row in rows
                if row["refresh_mode"] == refresh_mode and row["leakage_fraction"] == leakage_fraction
            ]
            summary_by_mode.append(
                {
                    "refresh_mode": refresh_mode,
                    "leakage_fraction": leakage_fraction,
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

    high_leakage = [row for row in summary_by_mode if row["leakage_fraction"] >= 0.75]
    refresh_independent_high = [
        row for row in high_leakage if row["refresh_mode"] != "none" and row["refresh_independence_holds"]
    ]
    unsafe_high = [
        row["refresh_mode"]
        for row in high_leakage
        if row["max_empirical_soundness"] > 0.05 or not row["refresh_independence_holds"]
    ]
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T2 transcript leakage simulator",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "transcript_leakage_simulator_supports_restricted_lemma_not_hardware_verifier",
        "method": "b10_t2_transcript_leakage_simulator_v0",
        "source_target_id": "B10-T2",
        "source_lemma": "b10_t2_restricted_soundness_lemma_v0",
        "dependency_benchmark": "B8",
        "explicit_not_bqp_separation": True,
        "hardware_randomized_measurement_circuits_instantiated": False,
        "sampling_hardness_proved": False,
        "task_count": len(tasks),
        "configuration_count": len(rows),
        "qubits": qubits,
        "invariant_count": invariant_count,
        "sample_count": sample_count,
        "reference_count": reference_count,
        "trials": trials,
        "tolerance": tolerance,
        "refresh_modes": refresh_modes,
        "leakage_fractions": leakage_fractions,
        "adversaries_tested": sorted(ADVERSARIES),
        "minimum_honest_completeness": min(float(np.mean(values)) for values in honest_completeness_by_task.values()),
        "maximum_empirical_soundness": max(row["empirical_soundness"] for row in rows),
        "max_soundness_refresh_independent_high_leakage": max(
            row["max_empirical_soundness"] for row in refresh_independent_high
        ),
        "min_unknown_independent_count_refresh_high_leakage": min(
            row["min_unknown_independent_predicate_count"] for row in refresh_independent_high
        ),
        "refresh_independent_high_leakage_modes": sorted({row["refresh_mode"] for row in refresh_independent_high}),
        "unsafe_high_leakage_modes": sorted(set(unsafe_high)),
        "summary_by_mode": summary_by_mode,
        "results": rows,
        "limits": [
            "This is a transcript-level simulator, not a hardware randomized-measurement verifier.",
            "It tests whether declared refresh schedules satisfy the independence assumption used by the B10-T2 restricted lemma.",
            "It does not prove sampling hardness or BQP/classical separation.",
            "Unrestricted hardware noise, calibration leakage, and device-specific side channels are not modeled.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B10-T2 Transcript Leakage Simulator v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']}",
        f"- Source lemma: {report['source_lemma']}",
        f"- Method: {report['method']}",
        f"- Configurations: {report['configuration_count']}",
        f"- Minimum honest completeness: {report['minimum_honest_completeness']:.3f}",
        f"- Maximum empirical soundness: {report['maximum_empirical_soundness']:.3f}",
        f"- Max refreshed high-leakage soundness: {report['max_soundness_refresh_independent_high_leakage']:.3f}",
        f"- Min refreshed high-leakage unknown independent predicates: {report['min_unknown_independent_count_refresh_high_leakage']:.1f}",
        f"- Refresh-independent high-leakage modes: {report['refresh_independent_high_leakage_modes']}",
        f"- Unsafe high-leakage modes: {report['unsafe_high_leakage_modes']}",
        f"- Hardware randomized-measurement circuits instantiated: {report['hardware_randomized_measurement_circuits_instantiated']}",
        f"- Sampling hardness proved: {report['sampling_hardness_proved']}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Transcript Boundary By Mode",
        "",
        "| mode | leakage | refresh independence | min unknown independent | max soundness | mean soundness | adversaries over 5% |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["summary_by_mode"]:
        adversaries = ", ".join(row["adversaries_over_5pct_soundness"]) or "none"
        lines.append(
            f"| {row['refresh_mode']} | {row['leakage_fraction']:.2f} | "
            f"{row['refresh_independence_holds']} | {row['min_unknown_independent_predicate_count']:.1f} | "
            f"{row['max_empirical_soundness']:.3f} | {row['mean_empirical_soundness']:.3f} | {adversaries} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Supported: in this transcript model, refreshed modes retain at least one unknown independent predicate at high leakage and pass the empirical 5% soundness gate.",
            "- Rejected: no-refresh high leakage still fails because stale transcript learning violates refresh independence.",
            "- Not claimed: hardware execution, cryptographic soundness, sampling hardness, or BQP/classical separation.",
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
    parser.add_argument("--reference-count", type=int, default=50000)
    parser.add_argument("--trials", type=int, default=80)
    parser.add_argument("--tolerance", type=float, default=0.08)
    parser.add_argument("--leakage-fractions", default="0.0,0.25,0.5,0.75")
    parser.add_argument("--refresh-modes", default="none,projection_rotation,challenge_refresh,refresh_plus_rotation")
    parser.add_argument("--seed", type=int, default=20260617)
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t2_transcript_leakage_simulator_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t2_transcript_leakage_simulator.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

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
                    "maximum_empirical_soundness": report["maximum_empirical_soundness"],
                    "max_soundness_refresh_independent_high_leakage": report[
                        "max_soundness_refresh_independent_high_leakage"
                    ],
                    "unsafe_high_leakage_modes": report["unsafe_high_leakage_modes"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
