#!/usr/bin/env python3
"""Circuit-level hidden-projection refresh task for B4/B8.

The task is still a classical binary/CNOT-level proxy.  It upgrades the earlier
B8 toy invariant checks by deriving verifier masks from explicit random CNOT
circuits, then measuring how challenge refresh and projection rotation change
adaptive-spoofer soundness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


ADVERSARIES = {
    "metadata_only_adaptive_spoofer": {
        "known_strength": 0.0,
        "unknown_guess_fraction": 0.12,
        "unknown_guess_accuracy": 0.52,
        "unknown_strength": 0.15,
    },
    "known_projection_replay_spoofer": {
        "known_strength": 0.98,
        "unknown_guess_fraction": 0.05,
        "unknown_guess_accuracy": 0.50,
        "unknown_strength": 0.08,
    },
    "surrogate_projection_learner": {
        "known_strength": 0.82,
        "unknown_guess_fraction": 0.42,
        "unknown_guess_accuracy": 0.58,
        "unknown_strength": 0.26,
    },
    "trap_aware_leakage_spoofer": {
        "known_strength": 1.05,
        "unknown_guess_fraction": 0.68,
        "unknown_guess_accuracy": 0.63,
        "unknown_strength": 0.95,
    },
}

REFRESH_KNOWN_FACTORS = {
    "none": 1.0,
    "projection_rotation": 0.50,
    "challenge_refresh": 0.25,
    "refresh_plus_rotation": 0.10,
}

REFRESH_GUESS_DAMPING = {
    "none": 1.0,
    "projection_rotation": 0.55,
    "challenge_refresh": 0.35,
    "refresh_plus_rotation": 0.18,
}


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def parse_str_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def cnot_matrix(qubits: int, gates: list[tuple[int, int]]) -> np.ndarray:
    matrix = np.eye(qubits, dtype=np.uint8)
    for control, target in gates:
        matrix[target] ^= matrix[control]
    return matrix


def gf2_inverse(matrix: np.ndarray) -> np.ndarray:
    size = matrix.shape[0]
    aug = np.concatenate([matrix.copy() % 2, np.eye(size, dtype=np.uint8)], axis=1)
    for col in range(size):
        pivot = None
        for row in range(col, size):
            if aug[row, col]:
                pivot = row
                break
        if pivot is None:
            raise ValueError("matrix is singular over GF(2)")
        if pivot != col:
            aug[[col, pivot]] = aug[[pivot, col]]
        for row in range(size):
            if row != col and aug[row, col]:
                aug[row] ^= aug[col]
    return aug[:, size:]


def random_cnot_gates(qubits: int, depth: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    gates = []
    for _ in range(depth):
        control, target = rng.choice(qubits, size=2, replace=False).tolist()
        gates.append((int(control), int(target)))
    return gates


def make_input_masks(qubits: int, invariant_count: int, rng: np.random.Generator) -> list[list[int]]:
    masks = []
    seen = set()
    while len(masks) < invariant_count:
        width = int(rng.integers(3, min(7, qubits) + 1))
        mask = tuple(sorted(rng.choice(qubits, size=width, replace=False).tolist()))
        if mask not in seen:
            seen.add(mask)
            masks.append(list(mask))
    return masks


def propagate_masks_to_output(
    input_masks: list[list[int]],
    inverse_matrix: np.ndarray,
) -> list[list[int]]:
    output_masks = []
    for mask in input_masks:
        coeff = np.zeros(inverse_matrix.shape[0], dtype=np.uint8)
        coeff[mask] = 1
        output_coeff = (coeff @ inverse_matrix) % 2
        output_masks.append(np.flatnonzero(output_coeff).astype(int).tolist())
    return output_masks


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
    p_enforce = min(1.0, max(0.0, (1.0 + bias) / 2.0))
    for idx, mask in enumerate(masks):
        if not mask:
            continue
        should_enforce = rng.random(samples.shape[0]) < p_enforce
        parity = np.sum(samples[:, mask], axis=1) % 2
        current = 1 - 2 * parity
        mismatch = should_enforce & (current != targets[idx])
        samples[mismatch, mask[0]] ^= 1
    return samples


def sample_circuit_task(
    task: dict,
    sample_count: int,
    bias: float,
    rng: np.random.Generator,
) -> np.ndarray:
    inputs = rng.integers(0, 2, size=(sample_count, task["qubits"]), dtype=np.uint8)
    outputs = (inputs @ task["matrix"].T) % 2
    return enforce_invariants(
        outputs.astype(np.int8),
        task["output_masks"],
        task["targets"],
        bias,
        rng,
    )


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


def build_tasks(
    qubits_list: list[int],
    invariant_count: int,
    circuit_depth_factor: int,
    seed: int,
) -> list[dict]:
    rng = np.random.default_rng(seed)
    tasks = []
    for qubits in qubits_list:
        depth = circuit_depth_factor * qubits
        gates = random_cnot_gates(qubits, depth, rng)
        matrix = cnot_matrix(qubits, gates)
        inverse_matrix = gf2_inverse(matrix)
        input_masks = make_input_masks(qubits, invariant_count, rng)
        output_masks = propagate_masks_to_output(input_masks, inverse_matrix)
        targets = np.array([1 if (idx + qubits) % 3 != 1 else -1 for idx in range(invariant_count)])
        tasks.append(
            {
                "task_id": f"cnot_hidden_projection_n{qubits}_d{depth}",
                "qubits": qubits,
                "depth": depth,
                "gate_count": len(gates),
                "gates": gates,
                "matrix": matrix,
                "input_masks": input_masks,
                "output_masks": output_masks,
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
    refresh_mode: str,
    adversary: str,
    rng: np.random.Generator,
) -> tuple[np.ndarray, int, int]:
    spec = ADVERSARIES[adversary]
    masks = task["output_masks"]
    targets = task["targets"]
    known_factor = REFRESH_KNOWN_FACTORS[refresh_mode]
    guess_damping = REFRESH_GUESS_DAMPING[refresh_mode]
    effective_known_fraction = min(1.0, leakage_fraction * known_factor)
    known_count = int(round(len(masks) * effective_known_fraction))
    known_masks = masks[:known_count]
    known_targets = targets[:known_count]

    hidden_masks = masks[known_count:]
    hidden_targets = targets[known_count:]
    adaptive_guess_fraction = min(
        1.0,
        spec["unknown_guess_fraction"] * guess_damping
        + leakage_fraction * known_factor * (1.0 - spec["unknown_guess_fraction"]) * 0.7,
    )
    adaptive_guess_accuracy = min(
        0.96,
        0.5 + (spec["unknown_guess_accuracy"] - 0.5) * guess_damping
        + leakage_fraction * known_factor * 0.22,
    )
    guess_count = int(round(len(hidden_masks) * adaptive_guess_fraction))
    guess_masks = hidden_masks[:guess_count]
    guess_targets = guessed_unknown_targets(hidden_targets[:guess_count], adaptive_guess_accuracy, rng)

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
        task["honest_bias"] * spec["unknown_strength"] * guess_damping,
        rng,
    )
    return samples, known_count, guess_count


def public_task(task: dict) -> dict:
    return {
        "task_id": task["task_id"],
        "qubits": task["qubits"],
        "depth": task["depth"],
        "gate_count": task["gate_count"],
        "input_masks": task["input_masks"],
        "output_masks": task["output_masks"],
        "targets": task["targets"].astype(int).tolist(),
        "honest_bias": task["honest_bias"],
    }


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
    tasks = build_tasks(qubits, invariant_count, circuit_depth_factor, seed + 7000)
    rows = []
    honest_completeness_by_task = {}

    for task in tasks:
        reference_samples = sample_circuit_task(
            task,
            reference_count,
            task["honest_bias"],
            rng,
        )
        reference_means = parity_signs(reference_samples, task["output_masks"]).mean(axis=0)
        honest_passes = []
        for _ in range(trials):
            honest_samples = sample_circuit_task(
                task,
                sample_count,
                task["honest_bias"],
                rng,
            )
            honest_passes.append(
                verify_samples(honest_samples, task["output_masks"], reference_means, tolerance)["passed"]
            )
        honest_completeness = sum(honest_passes) / trials
        honest_completeness_by_task[task["task_id"]] = honest_completeness

        for refresh_mode in refresh_modes:
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
                            refresh_mode,
                            adversary,
                            rng,
                        )
                        result = verify_samples(samples, task["output_masks"], reference_means, tolerance)
                        pass_flags.append(result["passed"])
                        max_errors.append(result["max_abs_error"])
                        known_counts.append(known_count)
                        guessed_counts.append(guessed_count)
                    rows.append(
                        {
                            "task_id": task["task_id"],
                            "qubits": task["qubits"],
                            "depth": task["depth"],
                            "refresh_mode": refresh_mode,
                            "leakage_fraction": leakage_fraction,
                            "effective_known_fraction": leakage_fraction * REFRESH_KNOWN_FACTORS[refresh_mode],
                            "adversary": adversary,
                            "known_invariant_count": int(round(float(np.mean(known_counts)))),
                            "guessed_hidden_invariant_count": int(round(float(np.mean(guessed_counts)))),
                            "honest_completeness": honest_completeness,
                            "adaptive_soundness": sum(pass_flags) / trials,
                            "mean_max_abs_error": float(np.mean(max_errors)),
                            "max_max_abs_error": float(np.max(max_errors)),
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

    high_leakage_rows = [row for row in summary_by_mode if row["leakage_fraction"] >= 0.75]
    high_leakage_repair_modes_passing = sorted(
        {
            row["refresh_mode"]
            for row in high_leakage_rows
            if row["refresh_mode"] != "none" and row["max_adaptive_soundness"] <= 0.05
        }
    )
    none_high_leakage_max = max(
        row["max_adaptive_soundness"]
        for row in high_leakage_rows
        if row["refresh_mode"] == "none"
    )
    best_repair_high_leakage_max = min(
        row["max_adaptive_soundness"]
        for row in high_leakage_rows
        if row["refresh_mode"] != "none"
    )

    return {
        "benchmark_id": "B4_B8",
        "problem_ids": [16, 30],
        "title": "B4/B8 circuit-level hidden-projection refresh task",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "circuit_level_hidden_projection_refresh_boundary_not_quantum_advantage_claim",
        "method": "b4_b8_circuit_hidden_projection_refresh_v0",
        "task_family": "random_cnot_hidden_projection_sampling",
        "task_count": len(tasks),
        "configuration_count": len(rows),
        "qubits": qubits,
        "circuit_depth_factor": circuit_depth_factor,
        "invariant_count": invariant_count,
        "sample_count": sample_count,
        "reference_count": reference_count,
        "trials": trials,
        "tolerance": tolerance,
        "leakage_fractions": leakage_fractions,
        "refresh_modes": refresh_modes,
        "adversaries_tested": sorted(ADVERSARIES),
        "minimum_honest_completeness": min(honest_completeness_by_task.values()),
        "maximum_adaptive_soundness": max(row["adaptive_soundness"] for row in rows),
        "none_high_leakage_max_soundness": none_high_leakage_max,
        "best_repair_high_leakage_max_soundness": best_repair_high_leakage_max,
        "high_leakage_repair_modes_passing": high_leakage_repair_modes_passing,
        "summary_by_mode": summary_by_mode,
        "tasks": [public_task(task) for task in tasks],
        "results": rows,
        "limits": [
            "This is a circuit-level CNOT/hidden-projection proxy, not a quantum advantage protocol.",
            "The verifier checks task-relevant hidden projections rather than the full output distribution.",
            "Challenge refresh and projection rotation are instantiated as fresh hidden masks derived from explicit CNOT circuits, but not yet as hardware-executable randomized measurement circuits.",
            "Adaptive spoofers are heuristic projection-enforcement models, not trained generative attackers.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B4/B8 Circuit-Level Hidden-Projection Refresh Task v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Task family: {report['task_family']}",
        f"- Tasks: {report['task_count']}",
        f"- Configurations: {report['configuration_count']}",
        f"- Qubits: {report['qubits']}",
        f"- Circuit depth factor: {report['circuit_depth_factor']}",
        f"- Invariants per task: {report['invariant_count']}",
        f"- Samples per trial: {report['sample_count']}",
        f"- Trials: {report['trials']}",
        f"- Minimum honest completeness: {report['minimum_honest_completeness']:.3f}",
        f"- Maximum adaptive soundness: {report['maximum_adaptive_soundness']:.3f}",
        f"- No-refresh high-leakage max soundness: {report['none_high_leakage_max_soundness']:.3f}",
        f"- Best repair high-leakage max soundness: {report['best_repair_high_leakage_max_soundness']:.3f}",
        f"- High-leakage repair modes passing <=5% soundness: {report['high_leakage_repair_modes_passing']}",
        "",
        "## Refresh Summary",
        "",
        "| mode | leakage | max soundness | mean soundness | adversaries over 5% |",
        "|---|---:|---:|---:|---|",
    ]
    for row in report["summary_by_mode"]:
        lines.append(
            f"| {row['refresh_mode']} | {row['leakage_fraction']:.2f} | "
            f"{row['max_adaptive_soundness']:.3f} | {row['mean_adaptive_soundness']:.3f} | "
            f"{', '.join(row['adversaries_over_5pct_soundness']) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Worst Rows",
            "",
            "| task | mode | leakage | adversary | soundness | known | guessed | mean max error |",
            "|---|---|---:|---|---:|---:|---:|---:|",
        ]
    )
    worst = sorted(report["results"], key=lambda row: row["adaptive_soundness"], reverse=True)[:12]
    for row in worst:
        lines.append(
            f"| {row['task_id']} | {row['refresh_mode']} | {row['leakage_fraction']:.2f} | "
            f"{row['adversary']} | {row['adaptive_soundness']:.3f} | "
            f"{row['known_invariant_count']} | {row['guessed_hidden_invariant_count']} | "
            f"{row['mean_max_abs_error']:.3f} |"
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
    parser.add_argument("--trials", type=int, default=120)
    parser.add_argument("--tolerance", type=float, default=0.08)
    parser.add_argument("--leakage-fractions", default="0,0.25,0.5,0.75")
    parser.add_argument(
        "--refresh-modes",
        default="none,projection_rotation,challenge_refresh,refresh_plus_rotation",
    )
    parser.add_argument("--seed", type=int, default=40617)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B4_B8_circuit_refresh_task_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B4_B8_circuit_refresh_task.md"),
    )
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
                    "minimum_honest_completeness": report["minimum_honest_completeness"],
                    "maximum_adaptive_soundness": report["maximum_adaptive_soundness"],
                    "none_high_leakage_max_soundness": report["none_high_leakage_max_soundness"],
                    "best_repair_high_leakage_max_soundness": report["best_repair_high_leakage_max_soundness"],
                    "high_leakage_repair_modes_passing": report["high_leakage_repair_modes_passing"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
