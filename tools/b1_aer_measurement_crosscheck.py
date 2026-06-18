#!/usr/bin/env python3
"""Shot-based Qiskit Aer cross-check for B1 measurement distributions."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def discover_pairs(left: Path, right: Path) -> list[tuple[Path, Path]]:
    if left.is_file() and right.is_file():
        return [(left, right)]
    if not left.is_dir() or not right.is_dir():
        raise ValueError("Inputs must be either two files or two directories")
    pairs = []
    for left_file in sorted(left.rglob("*.qasm")):
        right_file = right / left_file.relative_to(left)
        if right_file.exists():
            pairs.append((left_file, right_file))
    return pairs


def normalized_counts(counts: dict[str, int], shots: int) -> dict[str, float]:
    return {key.replace(" ", ""): value / shots for key, value in counts.items()}


def total_variation(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys)


def threshold_for_support(support_size: int, shots: int, base: float, multiplier: float, cap: float) -> float:
    sampling_scale = math.sqrt(max(support_size, 1) / (math.pi * shots))
    return min(cap, base + multiplier * sampling_scale)


def aer_counts(path: Path, simulator: AerSimulator, shots: int, seed: int) -> dict[str, int]:
    circuit = QuantumCircuit.from_qasm_file(str(path))
    result = simulator.run(circuit, shots=shots, seed_simulator=seed).result()
    return dict(result.get_counts())


def compare_pair(
    left: Path,
    right: Path,
    simulator: AerSimulator,
    counts_cache: dict[str, dict[str, int]],
    shots: int,
    seed: int,
    base_tvd: float,
    threshold_multiplier: float,
    max_tvd: float,
) -> dict:
    left_key = str(left.resolve())
    right_key = str(right.resolve())
    if left_key not in counts_cache:
        counts_cache[left_key] = aer_counts(left, simulator, shots, seed)
    if right_key not in counts_cache:
        counts_cache[right_key] = aer_counts(right, simulator, shots, seed)

    left_dist = normalized_counts(counts_cache[left_key], shots)
    right_dist = normalized_counts(counts_cache[right_key], shots)
    support_size = len(set(left_dist) | set(right_dist))
    tvd = total_variation(left_dist, right_dist)
    threshold = threshold_for_support(support_size, shots, base_tvd, threshold_multiplier, max_tvd)
    return {
        "left": str(left),
        "right": str(right),
        "left_support": len(left_dist),
        "right_support": len(right_dist),
        "combined_support": support_size,
        "total_variation_distance": tvd,
        "threshold": threshold,
        "passed": tvd <= threshold,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--shots", type=int, default=32768)
    parser.add_argument("--seed", type=int, default=220626)
    parser.add_argument("--base-tvd", type=float, default=0.02)
    parser.add_argument("--threshold-multiplier", type=float, default=2.0)
    parser.add_argument("--max-tvd", type=float, default=0.35)
    parser.add_argument("--method", default="statevector")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    pairs = discover_pairs(args.left, args.right)
    if not pairs:
        raise SystemExit("No matching .qasm file pairs found")

    simulator = AerSimulator(method=args.method, seed_simulator=args.seed)
    counts_cache: dict[str, dict[str, int]] = {}
    results = [
        compare_pair(
            left,
            right,
            simulator,
            counts_cache,
            args.shots,
            args.seed,
            args.base_tvd,
            args.threshold_multiplier,
            args.max_tvd,
        )
        for left, right in pairs
    ]
    payload = {
        "benchmark_id": "B1",
        "check": "qiskit_aer_shot_measurement_equivalence_crosscheck",
        "simulator": "qiskit_aer.AerSimulator",
        "method": args.method,
        "shots": args.shots,
        "seed": args.seed,
        "threshold_model": {
            "base_tvd": args.base_tvd,
            "threshold_multiplier": args.threshold_multiplier,
            "max_tvd": args.max_tvd,
            "formula": "min(max_tvd, base_tvd + threshold_multiplier * sqrt(combined_support / (pi * shots)))",
        },
        "pair_count": len(results),
        "passed": sum(1 for row in results if row["passed"]),
        "failed": sum(1 for row in results if not row["passed"]),
        "max_total_variation_distance": max(row["total_variation_distance"] for row in results),
        "max_threshold": max(row["threshold"] for row in results),
        "results": results,
    }
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if payload["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
