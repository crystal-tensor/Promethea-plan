#!/usr/bin/env python3
"""Stress-test B8 hidden-invariant verification against adaptive leakage spoofers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


ADVERSARIES = {
    "metadata_only_adaptive_spoofer": {
        "known_strength": 0.0,
        "unknown_guess_fraction": 0.15,
        "unknown_guess_accuracy": 0.52,
        "unknown_strength": 0.18,
    },
    "known_projection_replay_spoofer": {
        "known_strength": 0.95,
        "unknown_guess_fraction": 0.05,
        "unknown_guess_accuracy": 0.50,
        "unknown_strength": 0.10,
    },
    "surrogate_projection_learner": {
        "known_strength": 0.80,
        "unknown_guess_fraction": 0.45,
        "unknown_guess_accuracy": 0.58,
        "unknown_strength": 0.28,
    },
    "trap_aware_leakage_spoofer": {
        "known_strength": 1.05,
        "unknown_guess_fraction": 0.70,
        "unknown_guess_accuracy": 0.62,
        "unknown_strength": 0.95,
    },
}


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def make_masks(qubits: int, invariant_count: int, rng: np.random.Generator) -> list[list[int]]:
    masks = []
    seen = set()
    while len(masks) < invariant_count:
        width = int(rng.integers(3, min(7, qubits) + 1))
        mask = tuple(sorted(rng.choice(qubits, size=width, replace=False).tolist()))
        if mask not in seen:
            seen.add(mask)
            masks.append(list(mask))
    return masks


def parity_signs(samples: np.ndarray, masks: list[list[int]]) -> np.ndarray:
    columns = []
    for mask in masks:
        parity = np.sum(samples[:, mask], axis=1) % 2
        columns.append(1 - 2 * parity)
    return np.column_stack(columns)


def enforce_invariants(
    samples: np.ndarray,
    masks: list[list[int]],
    targets: np.ndarray,
    bias: float,
    rng: np.random.Generator,
) -> np.ndarray:
    if not masks:
        return samples
    p_enforce = min(1.0, max(0.0, (1 + bias) / 2))
    for idx, mask in enumerate(masks):
        should_enforce = rng.random(samples.shape[0]) < p_enforce
        parity = np.sum(samples[:, mask], axis=1) % 2
        current = 1 - 2 * parity
        mismatch = should_enforce & (current != targets[idx])
        samples[mismatch, mask[0]] ^= 1
    return samples


def sample_task(
    qubits: int,
    sample_count: int,
    masks: list[list[int]],
    targets: np.ndarray,
    bias: float,
    rng: np.random.Generator,
) -> np.ndarray:
    samples = rng.integers(0, 2, size=(sample_count, qubits), dtype=np.int8)
    return enforce_invariants(samples, masks, targets, bias, rng)


def verify_samples(
    samples: np.ndarray,
    masks: list[list[int]],
    reference_means: np.ndarray,
    tolerance: float,
) -> dict:
    observed = parity_signs(samples, masks).mean(axis=0)
    errors = np.abs(observed - reference_means)
    return {
        "max_abs_error": float(np.max(errors)),
        "mean_abs_error": float(np.mean(errors)),
        "passed": bool(np.max(errors) <= tolerance),
    }


def build_tasks(qubits_list: list[int], invariant_count: int, seed: int) -> list[dict]:
    rng = np.random.default_rng(seed)
    tasks = []
    for qubits in qubits_list:
        masks = make_masks(qubits, invariant_count, rng)
        targets = np.array([1 if (idx * 3 + qubits) % 5 in {0, 1, 3} else -1 for idx in range(invariant_count)])
        tasks.append(
            {
                "task_id": f"adaptive_hidden_projection_n{qubits}",
                "qubits": qubits,
                "masks": masks,
                "targets": targets,
                "honest_bias": 0.34 if qubits <= 16 else 0.30,
            }
        )
    return tasks


def guessed_unknown_targets(
    true_targets: np.ndarray,
    accuracy: float,
    rng: np.random.Generator,
) -> np.ndarray:
    correct = rng.random(len(true_targets)) < accuracy
    guesses = true_targets.copy()
    guesses[~correct] *= -1
    return guesses


def adversary_samples(
    task: dict,
    sample_count: int,
    leakage_fraction: float,
    adversary: str,
    rng: np.random.Generator,
) -> tuple[np.ndarray, int, int]:
    spec = ADVERSARIES[adversary]
    masks = task["masks"]
    targets = task["targets"]
    invariant_count = len(masks)
    known_count = int(round(invariant_count * leakage_fraction))
    known_masks = masks[:known_count]
    known_targets = targets[:known_count]
    hidden_masks = masks[known_count:]
    hidden_targets = targets[known_count:]
    adaptive_guess_fraction = min(
        1.0,
        spec["unknown_guess_fraction"] + leakage_fraction * (1.0 - spec["unknown_guess_fraction"]),
    )
    adaptive_guess_accuracy = min(
        0.98,
        spec["unknown_guess_accuracy"] + leakage_fraction * (1.0 - spec["unknown_guess_accuracy"]) * 0.8,
    )
    guess_count = int(round(len(hidden_masks) * adaptive_guess_fraction))
    guess_masks = hidden_masks[:guess_count]
    guess_targets = guessed_unknown_targets(
        hidden_targets[:guess_count],
        adaptive_guess_accuracy,
        rng,
    )

    samples = rng.integers(0, 2, size=(sample_count, task["qubits"]), dtype=np.int8)
    samples = enforce_invariants(
        samples,
        known_masks,
        known_targets,
        task["honest_bias"] * spec["known_strength"],
        rng,
    )
    samples = enforce_invariants(
        samples,
        guess_masks,
        guess_targets,
        task["honest_bias"] * spec["unknown_strength"],
        rng,
    )
    return samples, known_count, guess_count


def run(
    qubits: list[int],
    invariant_count: int,
    sample_count: int,
    reference_count: int,
    trials: int,
    tolerance: float,
    leakage_fractions: list[float],
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    tasks = build_tasks(qubits, invariant_count, seed + 1000)
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

        for leakage_fraction in leakage_fractions:
            for adversary in sorted(ADVERSARIES):
                pass_flags = []
                max_errors = []
                known_counts = []
                guessed_counts = []
                for _ in range(trials):
                    samples, known_count, guessed_count = adversary_samples(
                        task,
                        sample_count,
                        leakage_fraction,
                        adversary,
                        rng,
                    )
                    result = verify_samples(samples, task["masks"], reference_means, tolerance)
                    pass_flags.append(result["passed"])
                    max_errors.append(result["max_abs_error"])
                    known_counts.append(known_count)
                    guessed_counts.append(guessed_count)
                rows.append(
                    {
                        "task_id": task["task_id"],
                        "qubits": task["qubits"],
                        "invariant_count": invariant_count,
                        "sample_count": sample_count,
                        "reference_count": reference_count,
                        "trials": trials,
                        "tolerance": tolerance,
                        "leakage_fraction": leakage_fraction,
                        "adversary": adversary,
                        "known_invariant_count": int(round(float(np.mean(known_counts)))),
                        "guessed_hidden_invariant_count": int(round(float(np.mean(guessed_counts)))),
                        "honest_completeness": honest_completeness,
                        "adaptive_soundness": sum(pass_flags) / trials,
                        "mean_max_abs_error": float(np.mean(max_errors)),
                        "max_max_abs_error": float(np.max(max_errors)),
                    }
                )

    by_leakage = []
    for leakage_fraction in leakage_fractions:
        subset = [row for row in rows if row["leakage_fraction"] == leakage_fraction]
        by_leakage.append(
            {
                "leakage_fraction": leakage_fraction,
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

    dangerous = [
        entry["leakage_fraction"]
        for entry in by_leakage
        if entry["max_adaptive_soundness"] > 0.05
    ]
    return {
        "benchmark_id": "B8",
        "problem_id": 30,
        "title": "B8 adaptive hidden-invariant leakage stress test",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "adaptive_leakage_stress_test_not_full_distribution_verification",
        "method": "adaptive_hidden_invariant_leakage_spoofer_v0",
        "task_count": len(tasks),
        "configuration_count": len(rows),
        "sample_count": sample_count,
        "reference_count": reference_count,
        "trials": trials,
        "tolerance": tolerance,
        "invariant_count": invariant_count,
        "leakage_fractions": leakage_fractions,
        "adversaries_tested": sorted(ADVERSARIES),
        "minimum_honest_completeness": min(honest_completeness_by_task.values()),
        "maximum_adaptive_soundness": max(row["adaptive_soundness"] for row in rows),
        "dangerous_leakage_threshold": min(dangerous) if dangerous else None,
        "leakage_summary": by_leakage,
        "results": rows,
        "limits": [
            "This is an adaptive synthetic stress test, not real quantum-output verification.",
            "Spoofers observe controlled leakage fractions and use simple projection-enforcement heuristics, not trained generative models.",
            "The verifier still uses hidden parity projections, not classical shadows or randomized measurement data.",
            "A high-leakage failure should be read as a design warning: hidden challenges must remain hidden or be refreshed.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B8 Adaptive Leakage Spoofer Stress Test v0.1",
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
        f"- Adversaries tested: {report['adversaries_tested']}",
        f"- Minimum honest completeness: {report['minimum_honest_completeness']:.3f}",
        f"- Maximum adaptive soundness: {report['maximum_adaptive_soundness']:.3f}",
        f"- Dangerous leakage threshold: {report['dangerous_leakage_threshold']}",
        "",
        "## Leakage Summary",
        "",
        "| leakage | max soundness | mean soundness | adversaries over 5% |",
        "|---:|---:|---:|---|",
    ]
    for row in report["leakage_summary"]:
        lines.append(
            f"| {row['leakage_fraction']:.2f} | {row['max_adaptive_soundness']:.3f} | "
            f"{row['mean_adaptive_soundness']:.3f} | {', '.join(row['adversaries_over_5pct_soundness']) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Worst Rows",
            "",
            "| task | leakage | adversary | soundness | mean max error | known | guessed hidden |",
            "|---|---:|---|---:|---:|---:|---:|",
        ]
    )
    worst = sorted(report["results"], key=lambda row: row["adaptive_soundness"], reverse=True)[:12]
    for row in worst:
        lines.append(
            f"| {row['task_id']} | {row['leakage_fraction']:.2f} | {row['adversary']} | "
            f"{row['adaptive_soundness']:.3f} | {row['mean_max_abs_error']:.3f} | "
            f"{row['known_invariant_count']} | {row['guessed_hidden_invariant_count']} |"
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
    parser.add_argument("--seed", type=int, default=300627)
    parser.add_argument("--json-output", type=Path, default=Path("results/B8_adaptive_leakage_spoofer_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B8_adaptive_leakage_spoofer.md"))
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
                    "dangerous_leakage_threshold": report["dangerous_leakage_threshold"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
