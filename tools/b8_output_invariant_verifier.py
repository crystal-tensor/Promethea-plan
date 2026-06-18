#!/usr/bin/env python3
"""Simulate toy invariant checks for classical verification of quantum outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


ADVERSARIES = {
    "uniform_random_spoofer": {"known_fraction": 0.0, "bias_scale": 0.0},
    "marginal_matching_spoofer": {"known_fraction": 0.0, "bias_scale": 0.0},
    "public_invariant_spoofer": {"known_fraction": 0.4, "bias_scale": 1.0},
    "leaked_half_invariant_spoofer": {"known_fraction": 0.5, "bias_scale": 0.9},
    "weak_surrogate_spoofer": {"known_fraction": 1.0, "bias_scale": 0.35},
}


def make_masks(qubits: int, invariant_count: int, rng: np.random.Generator) -> list[list[int]]:
    masks = []
    seen = set()
    while len(masks) < invariant_count:
        width = int(rng.integers(3, min(6, qubits) + 1))
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
    p_enforce = (1 + bias) / 2
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
    absolute_errors = np.abs(observed - reference_means)
    return {
        "observed_means": observed.tolist(),
        "max_abs_error": float(np.max(absolute_errors)),
        "mean_abs_error": float(np.mean(absolute_errors)),
        "passed": bool(np.max(absolute_errors) <= tolerance),
    }


def build_tasks(qubits_list: list[int], invariant_count: int, seed: int) -> list[dict]:
    tasks = []
    rng = np.random.default_rng(seed)
    for qubits in qubits_list:
        masks = make_masks(qubits, invariant_count, rng)
        targets = np.array([1 if idx % 2 == 0 else -1 for idx in range(invariant_count)])
        tasks.append(
            {
                "task_id": f"hidden_parity_projection_n{qubits}",
                "qubits": qubits,
                "masks": masks,
                "targets": targets,
                "honest_bias": 0.34 if qubits <= 16 else 0.30,
            }
        )
    return tasks


def run(
    qubits: list[int],
    invariant_count: int,
    sample_count: int,
    reference_count: int,
    trials: int,
    tolerance: float,
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    tasks = build_tasks(qubits, invariant_count, seed + 1000)
    rows = []
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
            samples = sample_task(
                task["qubits"],
                sample_count,
                task["masks"],
                task["targets"],
                task["honest_bias"],
                rng,
            )
            honest_passes.append(verify_samples(samples, task["masks"], reference_means, tolerance)["passed"])
        honest_completeness = sum(honest_passes) / trials

        for adversary, spec in ADVERSARIES.items():
            known_count = int(round(len(task["masks"]) * spec["known_fraction"]))
            known_masks = task["masks"][:known_count]
            known_targets = task["targets"][:known_count]
            pass_flags = []
            max_errors = []
            for _ in range(trials):
                samples = rng.integers(0, 2, size=(sample_count, task["qubits"]), dtype=np.int8)
                if known_masks:
                    samples = enforce_invariants(
                        samples,
                        known_masks,
                        known_targets,
                        task["honest_bias"] * spec["bias_scale"],
                        rng,
                    )
                result = verify_samples(samples, task["masks"], reference_means, tolerance)
                pass_flags.append(result["passed"])
                max_errors.append(result["max_abs_error"])
            soundness = sum(pass_flags) / trials
            rows.append(
                {
                    "task_id": task["task_id"],
                    "qubits": task["qubits"],
                    "invariant_count": len(task["masks"]),
                    "sample_count": sample_count,
                    "reference_count": reference_count,
                    "trials": trials,
                    "tolerance": tolerance,
                    "honest_bias": task["honest_bias"],
                    "honest_completeness": honest_completeness,
                    "adversary": adversary,
                    "known_invariant_count": known_count,
                    "adversary_soundness": soundness,
                    "mean_max_abs_error": float(np.mean(max_errors)),
                    "reference_means": reference_means.tolist(),
                    "masks": task["masks"],
                }
            )

    failing_adversaries = sorted(
        {
            row["adversary"]
            for row in rows
            if row["honest_completeness"] >= 0.8 and row["adversary_soundness"] <= 0.05
        }
    )
    return {
        "benchmark_id": "B8",
        "method": "toy_hidden_invariant_output_verifier_v0",
        "model_status": "toy_invariant_property_test_not_full_distribution_verification",
        "task_count": len(tasks),
        "configuration_count": len(rows),
        "sample_count": sample_count,
        "reference_count": reference_count,
        "trials": trials,
        "tolerance": tolerance,
        "adversaries_tested": sorted(ADVERSARIES),
        "adversaries_failing_count": len(failing_adversaries),
        "adversaries_failing_invariant_rule": failing_adversaries,
        "minimum_honest_completeness": min(row["honest_completeness"] for row in rows),
        "maximum_adversary_soundness": max(row["adversary_soundness"] for row in rows),
        "results": rows,
    }


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", default="12,16,20")
    parser.add_argument("--invariant-count", type=int, default=8)
    parser.add_argument("--sample-count", type=int, default=4096)
    parser.add_argument("--reference-count", type=int, default=50000)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--tolerance", type=float, default=0.08)
    parser.add_argument("--seed", type=int, default=300626)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = run(
        qubits=parse_int_list(args.qubits),
        invariant_count=args.invariant_count,
        sample_count=args.sample_count,
        reference_count=args.reference_count,
        trials=args.trials,
        tolerance=args.tolerance,
        seed=args.seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
