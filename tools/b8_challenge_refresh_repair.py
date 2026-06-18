#!/usr/bin/env python3
"""Toy challenge-refresh repair experiment for B8 adaptive leakage failures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from b8_adaptive_spoofer_leakage import (
    ADVERSARIES,
    adversary_samples,
    build_tasks,
    parse_float_list,
    parse_int_list,
    parity_signs,
    sample_task,
    verify_samples,
)


def parse_str_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def effective_leakage(leakage_fraction: float, refresh_mode: str) -> float:
    if refresh_mode == "none":
        return leakage_fraction
    if refresh_mode == "projection_rotation":
        return 0.5 * leakage_fraction
    if refresh_mode == "challenge_refresh":
        return 0.25 * leakage_fraction
    if refresh_mode == "refresh_plus_rotation":
        return 0.1 * leakage_fraction
    raise ValueError(f"unsupported refresh mode: {refresh_mode}")


def run(
    qubits: list[int],
    invariant_count: int,
    sample_count: int,
    reference_count: int,
    trials: int,
    tolerance: float,
    leakage_fractions: list[float],
    refresh_modes: list[str],
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    tasks = build_tasks(qubits, invariant_count, seed + 5000)
    rows = []
    honest_completeness_by_task = {}

    for task in tasks:
        reference_samples = sample_task(
            task["qubits"],
            reference_count,
            task["masks"],
            task["targets"],
            task["honest_bias"],
            rng,
        )
        reference_means = parity_signs(reference_samples, task["masks"]).mean(axis=0)
        honest_passes = []
        for _ in range(trials):
            honest_samples = sample_task(
                task["qubits"],
                sample_count,
                task["masks"],
                task["targets"],
                task["honest_bias"],
                rng,
            )
            honest_passes.append(verify_samples(honest_samples, task["masks"], reference_means, tolerance)["passed"])
        honest_completeness = sum(honest_passes) / trials
        honest_completeness_by_task[task["task_id"]] = honest_completeness

        for refresh_mode in refresh_modes:
            for leakage_fraction in leakage_fractions:
                eff_leakage = effective_leakage(leakage_fraction, refresh_mode)
                for adversary in sorted(ADVERSARIES):
                    pass_flags = []
                    max_errors = []
                    for _ in range(trials):
                        samples, _known_count, _guessed_count = adversary_samples(
                            task,
                            sample_count,
                            eff_leakage,
                            adversary,
                            rng,
                        )
                        result = verify_samples(samples, task["masks"], reference_means, tolerance)
                        pass_flags.append(result["passed"])
                        max_errors.append(result["max_abs_error"])
                    rows.append(
                        {
                            "task_id": task["task_id"],
                            "qubits": task["qubits"],
                            "refresh_mode": refresh_mode,
                            "leakage_fraction": leakage_fraction,
                            "effective_leakage_fraction": eff_leakage,
                            "adversary": adversary,
                            "honest_completeness": honest_completeness,
                            "adaptive_soundness": sum(pass_flags) / trials,
                            "mean_max_abs_error": float(np.mean(max_errors)),
                            "max_max_abs_error": float(np.max(max_errors)),
                        }
                    )

    by_mode = []
    for refresh_mode in refresh_modes:
        for leakage_fraction in leakage_fractions:
            subset = [
                row
                for row in rows
                if row["refresh_mode"] == refresh_mode and row["leakage_fraction"] == leakage_fraction
            ]
            by_mode.append(
                {
                    "refresh_mode": refresh_mode,
                    "leakage_fraction": leakage_fraction,
                    "effective_leakage_fraction": effective_leakage(leakage_fraction, refresh_mode),
                    "max_adaptive_soundness": max(row["adaptive_soundness"] for row in subset),
                    "mean_adaptive_soundness": sum(row["adaptive_soundness"] for row in subset) / len(subset),
                    "adversaries_over_5pct_soundness": sorted(
                        {
                            row["adversary"]
                            for row in subset
                            if row["adaptive_soundness"] > 0.05
                        }
                    ),
                }
            )

    repaired_high_leakage = [
        row
        for row in by_mode
        if row["leakage_fraction"] >= 0.75
        and row["refresh_mode"] != "none"
        and row["max_adaptive_soundness"] <= 0.05
    ]
    high_leakage_non_none = [
        row
        for row in by_mode
        if row["leakage_fraction"] >= 0.75 and row["refresh_mode"] != "none"
    ]

    return {
        "benchmark_id": "B8",
        "problem_id": 30,
        "title": "B8 challenge-refresh projection-rotation repair baseline",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "challenge_refresh_projection_rotation_toy_repair_not_full_distribution_verification",
        "method": "challenge_refresh_projection_rotation_repair_v0",
        "task_count": len(tasks),
        "configuration_count": len(rows),
        "sample_count": sample_count,
        "reference_count": reference_count,
        "trials": trials,
        "tolerance": tolerance,
        "invariant_count": invariant_count,
        "leakage_fractions": leakage_fractions,
        "refresh_modes": refresh_modes,
        "adversaries_tested": sorted(ADVERSARIES),
        "minimum_honest_completeness": min(honest_completeness_by_task.values()),
        "maximum_adaptive_soundness": max(row["adaptive_soundness"] for row in rows),
        "high_leakage_repair_modes_passing": sorted({row["refresh_mode"] for row in repaired_high_leakage}),
        "high_leakage_repair_modes_tested": sorted({row["refresh_mode"] for row in high_leakage_non_none}),
        "summary_by_mode": by_mode,
        "results": rows,
        "limits": [
            "This is a toy repair baseline, not a proof of classical verification.",
            "Refresh and rotation are modeled as reducing effective leakage; a real protocol must instantiate fresh circuits or randomized measurement settings.",
            "Spoofers are heuristic projection-enforcement adversaries, not trained generative models.",
            "The result is useful only as a design gate for the next circuit-level B4/B8 task.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B8 Challenge-Refresh Repair Baseline v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Tasks: {report['task_count']}",
        f"- Configurations: {report['configuration_count']}",
        f"- Samples per trial: {report['sample_count']}",
        f"- Trials: {report['trials']}",
        f"- Leakage fractions: {report['leakage_fractions']}",
        f"- Refresh modes: {report['refresh_modes']}",
        f"- Minimum honest completeness: {report['minimum_honest_completeness']:.3f}",
        f"- Maximum adaptive soundness: {report['maximum_adaptive_soundness']:.3f}",
        f"- High-leakage repair modes passing <=5% soundness: {report['high_leakage_repair_modes_passing']}",
        "",
        "## Summary By Refresh Mode",
        "",
        "| mode | leakage | effective leakage | max soundness | mean soundness | adversaries over 5% |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in report["summary_by_mode"]:
        lines.append(
            f"| {row['refresh_mode']} | {row['leakage_fraction']:.2f} | "
            f"{row['effective_leakage_fraction']:.3f} | {row['max_adaptive_soundness']:.3f} | "
            f"{row['mean_adaptive_soundness']:.3f} | "
            f"{', '.join(row['adversaries_over_5pct_soundness']) or 'none'} |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", default="12,16,20")
    parser.add_argument("--invariant-count", type=int, default=10)
    parser.add_argument("--sample-count", type=int, default=4096)
    parser.add_argument("--reference-count", type=int, default=50000)
    parser.add_argument("--trials", type=int, default=120)
    parser.add_argument("--tolerance", type=float, default=0.08)
    parser.add_argument("--leakage-fractions", default="0,0.25,0.5,0.75")
    parser.add_argument(
        "--refresh-modes",
        default="none,projection_rotation,challenge_refresh,refresh_plus_rotation",
    )
    parser.add_argument("--seed", type=int, default=300631)
    parser.add_argument("--json-output", type=Path, default=Path("results/B8_challenge_refresh_repair_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B8_challenge_refresh_repair.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(
        qubits=parse_int_list(args.qubits),
        invariant_count=args.invariant_count,
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
                    "minimum_honest_completeness": report["minimum_honest_completeness"],
                    "maximum_adaptive_soundness": report["maximum_adaptive_soundness"],
                    "high_leakage_repair_modes_passing": report["high_leakage_repair_modes_passing"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

