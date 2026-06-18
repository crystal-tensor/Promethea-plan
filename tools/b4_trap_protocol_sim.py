#!/usr/bin/env python3
"""Simulate a toy trap-check protocol for B4 verifiable advantage work."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def hoeffding_samples(completeness: float, soundness: float, delta: float) -> int | None:
    gap = completeness - soundness
    if gap <= 0:
        return None
    return math.ceil(2 * math.log(2 / delta) / (gap * gap))


def batch_pass_probability(per_task_pass: float, batch_size: int, acceptance_fraction: float) -> float:
    threshold = math.ceil(batch_size * acceptance_fraction)
    return sum(
        math.comb(batch_size, k) * per_task_pass**k * (1 - per_task_pass) ** (batch_size - k)
        for k in range(threshold, batch_size + 1)
    )


def simulate_per_task_pass(per_trap_correct: float, trap_count: int, trials: int, rng: np.random.Generator) -> float:
    correct = rng.random((trials, trap_count)) < per_trap_correct
    return float(np.mean(np.all(correct, axis=1)))


def run_protocol(
    qubits: list[int],
    trap_counts: list[int],
    honest_error: float,
    trials: int,
    batch_size: int,
    acceptance_fraction: float,
    delta: float,
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    adversaries = {
        "uniform_random_spoofer": 0.5,
        "marginal_matching_spoofer": 0.55,
        "low_depth_surrogate_spoofer": 0.65,
        "partial_trap_leak_spoofer": 0.75,
    }
    rows = []
    for qubit_count in qubits:
        for trap_count in trap_counts:
            if trap_count > qubit_count:
                continue
            honest_per_trap = 1 - honest_error
            honest_exact = honest_per_trap**trap_count
            honest_mc = simulate_per_task_pass(honest_per_trap, trap_count, trials, rng)
            batch_completeness = batch_pass_probability(honest_exact, batch_size, acceptance_fraction)
            for adversary, per_trap_correct in adversaries.items():
                soundness_exact = per_trap_correct**trap_count
                soundness_mc = simulate_per_task_pass(per_trap_correct, trap_count, trials, rng)
                batch_soundness = batch_pass_probability(soundness_exact, batch_size, acceptance_fraction)
                rows.append(
                    {
                        "task_family": "toy_random_circuit_sampling_with_hidden_traps",
                        "qubits": qubit_count,
                        "trap_count": trap_count,
                        "trap_fraction": trap_count / qubit_count,
                        "honest_error_per_trap": honest_error,
                        "honest_per_task_pass_exact": honest_exact,
                        "honest_per_task_pass_mc": honest_mc,
                        "adversary": adversary,
                        "adversary_per_trap_correct": per_trap_correct,
                        "adversary_per_task_pass_exact": soundness_exact,
                        "adversary_per_task_pass_mc": soundness_mc,
                        "batch_size": batch_size,
                        "acceptance_fraction": acceptance_fraction,
                        "batch_completeness_exact": batch_completeness,
                        "batch_soundness_exact": batch_soundness,
                        "hoeffding_sample_complexity_delta": delta,
                        "hoeffding_sample_complexity": hoeffding_samples(honest_exact, soundness_exact, delta),
                        "spoofing_gap": honest_exact - soundness_exact,
                    }
                )
    failing_adversaries = sorted(
        {
            row["adversary"]
            for row in rows
            if row["batch_soundness_exact"] <= 0.05 and row["batch_completeness_exact"] >= 0.8
        }
    )
    return {
        "benchmark_id": "B4",
        "method": "toy_hidden_trap_protocol_sim_v0",
        "model_status": "toy_statistical_protocol_not_quantum_advantage_claim",
        "seed": seed,
        "trials": trials,
        "batch_size": batch_size,
        "acceptance_fraction": acceptance_fraction,
        "honest_error_per_trap": honest_error,
        "delta": delta,
        "configuration_count": len(rows),
        "spoofing_families_tested": sorted(adversaries),
        "spoofing_families_failing_batch_rule": failing_adversaries,
        "spoofing_families_failing_count": len(failing_adversaries),
        "results": rows,
    }


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", default="16,24,32")
    parser.add_argument("--trap-counts", default="2,4,8")
    parser.add_argument("--honest-error", type=float, default=0.02)
    parser.add_argument("--trials", type=int, default=20000)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--acceptance-fraction", type=float, default=0.8)
    parser.add_argument("--delta", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=160626)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = run_protocol(
        qubits=parse_int_list(args.qubits),
        trap_counts=parse_int_list(args.trap_counts),
        honest_error=args.honest_error,
        trials=args.trials,
        batch_size=args.batch_size,
        acceptance_fraction=args.acceptance_fraction,
        delta=args.delta,
        seed=args.seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
