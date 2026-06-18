#!/usr/bin/env python3
"""Train correlation-based generative spoofers against the B4/B8 refresh task."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from b4_b8_circuit_refresh_task import (
    REFRESH_GUESS_DAMPING,
    REFRESH_KNOWN_FACTORS,
    build_tasks,
    enforce_invariants,
    parse_float_list,
    parse_int_list,
    parse_str_list,
    parity_signs,
    sample_circuit_task,
    verify_samples,
)


LEARNERS = {
    "correlation_mask_learner": {
        "candidate_prior": 0.10,
        "candidate_pool_size": 48,
        "enforcement_strength": 1.00,
    },
    "generative_projection_learner": {
        "candidate_prior": 0.25,
        "candidate_pool_size": 72,
        "enforcement_strength": 1.02,
    },
    "leakage_augmented_generator": {
        "candidate_prior": 0.45,
        "candidate_pool_size": 96,
        "enforcement_strength": 1.04,
    },
}


def random_mask(qubits: int, rng: np.random.Generator) -> list[int]:
    width = int(rng.integers(3, min(7, qubits) + 1))
    return sorted(rng.choice(qubits, size=width, replace=False).astype(int).tolist())


def unique_masks(masks: list[list[int]]) -> list[list[int]]:
    seen = set()
    result = []
    for mask in masks:
        key = tuple(mask)
        if key not in seen:
            seen.add(key)
            result.append(mask)
    return result


def candidate_true_probability(leakage_fraction: float, refresh_mode: str, learner: str) -> float:
    spec = LEARNERS[learner]
    known_factor = REFRESH_KNOWN_FACTORS[refresh_mode]
    damping = REFRESH_GUESS_DAMPING[refresh_mode]
    return min(1.0, leakage_fraction * known_factor + spec["candidate_prior"] * damping)


def build_candidate_pool(
    task: dict,
    leakage_fraction: float,
    refresh_mode: str,
    learner: str,
    rng: np.random.Generator,
) -> tuple[list[list[int]], int, list[list[int]]]:
    spec = LEARNERS[learner]
    true_probability = candidate_true_probability(leakage_fraction, refresh_mode, learner)
    true_masks = [
        mask
        for mask in task["output_masks"]
        if rng.random() < true_probability
    ]
    decoy_count = max(0, int(spec["candidate_pool_size"]) - len(true_masks))
    decoys = [random_mask(task["qubits"], rng) for _ in range(decoy_count)]
    candidates = unique_masks(true_masks + decoys)
    rng.shuffle(candidates)
    return candidates, len(true_masks), true_masks


def train_candidate_projections(
    training_samples: np.ndarray,
    candidate_masks: list[list[int]],
    selected_count: int,
    pinned_masks: list[list[int]] | None = None,
) -> tuple[list[list[int]], np.ndarray, list[float]]:
    pinned_masks = pinned_masks or []
    pinned_keys = mask_set(pinned_masks)
    candidate_masks = [mask for mask in candidate_masks if tuple(mask) not in pinned_keys]
    if not candidate_masks:
        pinned_means = parity_signs(training_samples, pinned_masks).mean(axis=0) if pinned_masks else np.array([])
        return (
            pinned_masks[:selected_count],
            np.array([1 if value >= 0 else -1 for value in pinned_means[:selected_count]]),
            [float(value) for value in pinned_means[:selected_count]],
        )
    means = parity_signs(training_samples, candidate_masks).mean(axis=0)
    remaining_count = max(0, selected_count - len(pinned_masks))
    order = np.argsort(-np.abs(means))[:remaining_count]
    selected_masks = list(pinned_masks[:selected_count]) + [candidate_masks[int(idx)] for idx in order]
    if pinned_masks:
        pinned_means = parity_signs(training_samples, pinned_masks[:selected_count]).mean(axis=0)
    else:
        pinned_means = np.array([])
    selected_scores = [float(value) for value in pinned_means]
    selected_scores.extend(float(means[int(idx)]) for idx in order)
    selected_targets = np.array([1 if value >= 0 else -1 for value in selected_scores])
    return selected_masks, selected_targets, selected_scores


def mask_set(masks: list[list[int]]) -> set[tuple[int, ...]]:
    return {tuple(mask) for mask in masks}


def run(
    qubits: list[int],
    invariant_count: int,
    circuit_depth_factor: int,
    sample_count: int,
    reference_count: int,
    training_count: int,
    trials: int,
    tolerance: float,
    leakage_fractions: list[float],
    refresh_modes: list[str],
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    tasks = build_tasks(qubits, invariant_count, circuit_depth_factor, seed + 9000)
    rows = []
    honest_completeness_by_task = {}

    for task in tasks:
        reference_samples = sample_circuit_task(task, reference_count, task["honest_bias"], rng)
        reference_means = parity_signs(reference_samples, task["output_masks"]).mean(axis=0)
        honest_passes = []
        for _ in range(trials):
            honest_samples = sample_circuit_task(task, sample_count, task["honest_bias"], rng)
            honest_passes.append(
                verify_samples(honest_samples, task["output_masks"], reference_means, tolerance)["passed"]
            )
        honest_completeness = sum(honest_passes) / trials
        honest_completeness_by_task[task["task_id"]] = honest_completeness
        true_mask_set = mask_set(task["output_masks"])

        for refresh_mode in refresh_modes:
            for leakage_fraction in leakage_fractions:
                for learner in sorted(LEARNERS):
                    pass_flags = []
                    max_errors = []
                    true_in_pool_counts = []
                    selected_true_counts = []
                    selected_abs_scores = []
                    for _ in range(trials):
                        training_samples = sample_circuit_task(task, training_count, task["honest_bias"], rng)
                        candidates, true_in_pool, pinned_masks = build_candidate_pool(
                            task,
                            leakage_fraction,
                            refresh_mode,
                            learner,
                            rng,
                        )
                        selected_masks, selected_targets, selected_scores = train_candidate_projections(
                            training_samples,
                            candidates,
                            invariant_count,
                            pinned_masks,
                        )
                        generated = rng.integers(0, 2, size=(sample_count, task["qubits"]), dtype=np.int8)
                        generated = enforce_invariants(
                            generated,
                            selected_masks,
                            selected_targets,
                            task["honest_bias"] * LEARNERS[learner]["enforcement_strength"],
                            rng,
                        )
                        verification = verify_samples(generated, task["output_masks"], reference_means, tolerance)
                        pass_flags.append(verification["passed"])
                        max_errors.append(verification["max_abs_error"])
                        selected_true = len(mask_set(selected_masks) & true_mask_set)
                        true_in_pool_counts.append(true_in_pool)
                        selected_true_counts.append(selected_true)
                        selected_abs_scores.append(float(np.mean(np.abs(selected_scores))) if selected_scores else 0.0)
                    rows.append(
                        {
                            "task_id": task["task_id"],
                            "qubits": task["qubits"],
                            "refresh_mode": refresh_mode,
                            "leakage_fraction": leakage_fraction,
                            "learner": learner,
                            "candidate_true_probability": candidate_true_probability(
                                leakage_fraction,
                                refresh_mode,
                                learner,
                            ),
                            "honest_completeness": honest_completeness,
                            "learned_soundness": sum(pass_flags) / trials,
                            "mean_max_abs_error": float(np.mean(max_errors)),
                            "mean_true_masks_in_candidate_pool": float(np.mean(true_in_pool_counts)),
                            "mean_true_masks_selected": float(np.mean(selected_true_counts)),
                            "mean_abs_selected_training_score": float(np.mean(selected_abs_scores)),
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
                    "max_learned_soundness": max(row["learned_soundness"] for row in subset),
                    "mean_learned_soundness": sum(row["learned_soundness"] for row in subset) / len(subset),
                    "learners_over_5pct_soundness": sorted(
                        {
                            row["learner"]
                            for row in subset
                            if row["learned_soundness"] > 0.05
                        }
                    ),
                }
            )

    high_leakage_rows = [row for row in summary_by_mode if row["leakage_fraction"] >= 0.75]
    safe_high_leakage_refresh_modes = sorted(
        {
            row["refresh_mode"]
            for row in high_leakage_rows
            if row["refresh_mode"] != "none" and row["max_learned_soundness"] <= 0.05
        }
    )
    unsafe_high_leakage_refresh_modes = sorted(
        {
            row["refresh_mode"]
            for row in high_leakage_rows
            if row["max_learned_soundness"] > 0.05
        }
    )

    return {
        "benchmark_id": "B8",
        "problem_ids": [30, 16, 11],
        "title": "B8 trained generative spoofer refresh stress",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "trained_generative_spoofer_refresh_boundary_not_soundness_proof",
        "method": "b8_generative_spoofer_refresh_v0",
        "source_task": "b4_b8_circuit_hidden_projection_refresh_v0",
        "task_count": len(tasks),
        "configuration_count": len(rows),
        "qubits": qubits,
        "circuit_depth_factor": circuit_depth_factor,
        "invariant_count": invariant_count,
        "sample_count": sample_count,
        "reference_count": reference_count,
        "training_count": training_count,
        "trials": trials,
        "tolerance": tolerance,
        "leakage_fractions": leakage_fractions,
        "refresh_modes": refresh_modes,
        "learners_tested": sorted(LEARNERS),
        "minimum_honest_completeness": min(honest_completeness_by_task.values()),
        "maximum_learned_soundness": max(row["learned_soundness"] for row in rows),
        "safe_high_leakage_refresh_modes": safe_high_leakage_refresh_modes,
        "unsafe_high_leakage_refresh_modes": unsafe_high_leakage_refresh_modes,
        "summary_by_mode": summary_by_mode,
        "results": rows,
        "limits": [
            "This is a trained correlation/generative proxy, not a cryptographic soundness proof.",
            "Candidate parity masks are sampled from a side-channel quality model rather than learned from unrestricted circuit access.",
            "The task remains a CNOT hidden-projection proxy, not a hardware randomized-measurement verifier.",
            "Unsafe modes should be treated as B10-T2 proof obligations, not as final protocol failures.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B8 Trained Generative Spoofer Refresh Stress v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source task: {report['source_task']}",
        f"- Tasks: {report['task_count']}",
        f"- Configurations: {report['configuration_count']}",
        f"- Learners tested: {report['learners_tested']}",
        f"- Training samples per trial: {report['training_count']}",
        f"- Verification samples per trial: {report['sample_count']}",
        f"- Minimum honest completeness: {report['minimum_honest_completeness']:.3f}",
        f"- Maximum learned soundness: {report['maximum_learned_soundness']:.3f}",
        f"- Safe high-leakage refresh modes: {report['safe_high_leakage_refresh_modes']}",
        f"- Unsafe high-leakage refresh modes: {report['unsafe_high_leakage_refresh_modes']}",
        "",
        "## Refresh Summary",
        "",
        "| mode | leakage | max learned soundness | mean learned soundness | learners over 5% |",
        "|---|---:|---:|---:|---|",
    ]
    for row in report["summary_by_mode"]:
        lines.append(
            f"| {row['refresh_mode']} | {row['leakage_fraction']:.2f} | "
            f"{row['max_learned_soundness']:.3f} | {row['mean_learned_soundness']:.3f} | "
            f"{', '.join(row['learners_over_5pct_soundness']) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Worst Learned Rows",
            "",
            "| task | mode | leakage | learner | soundness | true masks selected | mean max error |",
            "|---|---|---:|---|---:|---:|---:|",
        ]
    )
    worst = sorted(report["results"], key=lambda row: row["learned_soundness"], reverse=True)[:12]
    for row in worst:
        lines.append(
            f"| {row['task_id']} | {row['refresh_mode']} | {row['leakage_fraction']:.2f} | "
            f"{row['learner']} | {row['learned_soundness']:.3f} | "
            f"{row['mean_true_masks_selected']:.2f} | {row['mean_max_abs_error']:.3f} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
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
    parser.add_argument("--training-count", type=int, default=4096)
    parser.add_argument("--trials", type=int, default=80)
    parser.add_argument("--tolerance", type=float, default=0.08)
    parser.add_argument("--leakage-fractions", default="0,0.25,0.5,0.75")
    parser.add_argument(
        "--refresh-modes",
        default="none,projection_rotation,challenge_refresh,refresh_plus_rotation",
    )
    parser.add_argument("--seed", type=int, default=80617)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B8_generative_spoofer_refresh_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B8_generative_spoofer_refresh.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(
        qubits=parse_int_list(args.qubits),
        invariant_count=args.invariant_count,
        circuit_depth_factor=args.circuit_depth_factor,
        sample_count=args.sample_count,
        reference_count=args.reference_count,
        training_count=args.training_count,
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
                    "maximum_learned_soundness": report["maximum_learned_soundness"],
                    "safe_high_leakage_refresh_modes": report["safe_high_leakage_refresh_modes"],
                    "unsafe_high_leakage_refresh_modes": report["unsafe_high_leakage_refresh_modes"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
