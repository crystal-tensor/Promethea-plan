#!/usr/bin/env python3
"""Run a reproducible repetition-code memory baseline for B2 QEC work."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np


def logical_error_exact(distance: int, physical_error: float) -> float:
    threshold = distance // 2 + 1
    return sum(
        math.comb(distance, k) * physical_error**k * (1 - physical_error) ** (distance - k)
        for k in range(threshold, distance + 1)
    )


def wilson_interval(failures: int, shots: int, z: float = 1.96) -> tuple[float, float]:
    if shots == 0:
        return 0.0, 0.0
    phat = failures / shots
    denom = 1 + z**2 / shots
    center = (phat + z**2 / (2 * shots)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z**2 / (4 * shots)) / shots) / denom
    return max(0.0, center - half), min(1.0, center + half)


def simulate_majority_decoder(distance: int, physical_error: float, shots: int, rng: np.random.Generator) -> tuple[int, float]:
    started = time.perf_counter()
    errors = rng.random((shots, distance)) < physical_error
    logical_failures = np.count_nonzero(errors.sum(axis=1) > distance // 2)
    elapsed = time.perf_counter() - started
    return int(logical_failures), elapsed / shots if shots else 0.0


def run_sweep(distances: list[int], physical_errors: list[float], shots: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    rows = []
    for distance in distances:
        for physical_error in physical_errors:
            failures, runtime_per_shot = simulate_majority_decoder(distance, physical_error, shots, rng)
            estimate = failures / shots
            low, high = wilson_interval(failures, shots)
            exact = logical_error_exact(distance, physical_error)
            rows.append(
                {
                    "code_family": "repetition_code_memory_control",
                    "decoder": "majority_vote",
                    "distance": distance,
                    "physical_qubits": distance,
                    "rounds": distance,
                    "space_time_volume": distance * distance,
                    "physical_error": physical_error,
                    "shots": shots,
                    "logical_failures": failures,
                    "logical_error_rate_mc": estimate,
                    "logical_error_rate_exact": exact,
                    "wilson_95_low": low,
                    "wilson_95_high": high,
                    "unencoded_error_rate": physical_error,
                    "suppression_factor_exact": physical_error / exact if exact else float("inf"),
                    "decoder_runtime_seconds_per_shot": runtime_per_shot,
                }
            )
    return {
        "benchmark_id": "B2",
        "method": "repetition_code_memory_majority_baseline_v0",
        "seed": seed,
        "shots": shots,
        "distance_count": len(distances),
        "physical_error_count": len(physical_errors),
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distances", default="3,5,7,9,11")
    parser.add_argument("--physical-errors", default="0.001,0.003,0.005,0.01,0.02,0.05,0.1,0.15")
    parser.add_argument("--shots", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=220626)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    distances = [int(item.strip()) for item in args.distances.split(",") if item.strip()]
    physical_errors = [float(item.strip()) for item in args.physical_errors.split(",") if item.strip()]
    for distance in distances:
        if distance <= 0 or distance % 2 == 0:
            raise SystemExit(f"distance must be a positive odd integer: {distance}")
    payload = run_sweep(distances, physical_errors, args.shots, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
