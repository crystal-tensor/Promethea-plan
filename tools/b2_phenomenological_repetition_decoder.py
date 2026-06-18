#!/usr/bin/env python3
"""Run a small phenomenological repetition-code decoder fallback for B2."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def wilson_interval(failures: int, shots: int, z: float = 1.96) -> tuple[float, float]:
    if shots == 0:
        return 0.0, 0.0
    phat = failures / shots
    denom = 1 + z**2 / shots
    center = (phat + z**2 / (2 * shots)) / denom
    half = z * math.sqrt((phat * (1 - phat) + z**2 / (4 * shots)) / shots) / denom
    return max(0.0, center - half), min(1.0, center + half)


def state_bits(state_count: int, distance: int) -> np.ndarray:
    states = np.arange(state_count, dtype=np.uint32)[:, None]
    shifts = np.arange(distance, dtype=np.uint32)[None, :]
    return ((states >> shifts) & 1).astype(np.uint8)


def syndrome_ints(bits: np.ndarray) -> np.ndarray:
    syndrome_bits = bits[:, :-1] ^ bits[:, 1:]
    powers = (1 << np.arange(syndrome_bits.shape[1], dtype=np.uint32))
    return syndrome_bits.astype(np.uint32) @ powers


def hamming_weight_ints(values: np.ndarray) -> np.ndarray:
    # Small arrays only; unpacking keeps this portable across Python/Numpy versions.
    return np.array([int(value).bit_count() for value in values], dtype=np.float64)


def transition_cost_matrix(distance: int, data_error: float) -> np.ndarray:
    state_count = 1 << distance
    states = np.arange(state_count, dtype=np.uint32)
    flips = states[:, None] ^ states[None, :]
    weights = hamming_weight_ints(flips.reshape(-1)).reshape(state_count, state_count)
    p = min(max(data_error, 1e-15), 1 - 1e-15)
    return -weights * math.log(p) - (distance - weights) * math.log1p(-p)


def emission_cost_table(distance: int, measurement_error: float, syndromes: np.ndarray) -> np.ndarray:
    syndrome_count = 1 << (distance - 1)
    observations = np.arange(syndrome_count, dtype=np.uint32)
    diff = syndromes[:, None] ^ observations[None, :]
    weights = hamming_weight_ints(diff.reshape(-1)).reshape(len(syndromes), syndrome_count)
    p = min(max(measurement_error, 1e-15), 1 - 1e-15)
    check_count = distance - 1
    return -weights * math.log(p) - (check_count - weights) * math.log1p(-p)


def viterbi_decode(observations: np.ndarray, transition_cost: np.ndarray, emission_cost: np.ndarray) -> int:
    state_count = transition_cost.shape[0]
    costs = np.full(state_count, np.inf)
    costs[0] = 0.0
    for observation in observations:
        costs = np.min(costs[:, None] + transition_cost, axis=0) + emission_cost[:, int(observation)]
    return int(np.argmin(costs))


def simulate_config(
    distance: int,
    rounds: int,
    data_error: float,
    measurement_error: float,
    shots: int,
    rng: np.random.Generator,
) -> dict:
    state_count = 1 << distance
    bits_by_state = state_bits(state_count, distance)
    syndrome_by_state = syndrome_ints(bits_by_state)
    transition_cost = transition_cost_matrix(distance, data_error)
    emission_cost = emission_cost_table(distance, measurement_error, syndrome_by_state)
    syndrome_powers = (1 << np.arange(distance - 1, dtype=np.uint32))

    viterbi_failures = 0
    majority_failures = 0
    started = time.perf_counter()
    for _ in range(shots):
        error_bits = np.zeros(distance, dtype=np.uint8)
        observations: list[int] = []
        for _round in range(rounds):
            error_bits ^= (rng.random(distance) < data_error).astype(np.uint8)
            syndrome_bits = error_bits[:-1] ^ error_bits[1:]
            syndrome_bits ^= (rng.random(distance - 1) < measurement_error).astype(np.uint8)
            observations.append(int(syndrome_bits.astype(np.uint32) @ syndrome_powers))

        decoded_state = viterbi_decode(np.array(observations, dtype=np.uint32), transition_cost, emission_cost)
        decoded_bits = bits_by_state[decoded_state]
        residual = error_bits ^ decoded_bits
        if int(residual.sum()) > distance // 2:
            viterbi_failures += 1
        if int(error_bits.sum()) > distance // 2:
            majority_failures += 1

    elapsed = time.perf_counter() - started
    v_low, v_high = wilson_interval(viterbi_failures, shots)
    m_low, m_high = wilson_interval(majority_failures, shots)
    v_rate = viterbi_failures / shots
    m_rate = majority_failures / shots
    return {
        "code_family": "phenomenological_repetition_memory",
        "decoder": "minimum_weight_syndrome_viterbi",
        "comparison_decoder": "final_majority_without_syndrome_history",
        "distance": distance,
        "rounds": rounds,
        "physical_qubits": distance,
        "syndrome_checks": distance - 1,
        "space_time_volume": distance * rounds,
        "data_error": data_error,
        "measurement_error": measurement_error,
        "shots": shots,
        "viterbi_logical_failures": viterbi_failures,
        "viterbi_logical_error_rate": v_rate,
        "viterbi_wilson_95_low": v_low,
        "viterbi_wilson_95_high": v_high,
        "majority_logical_failures": majority_failures,
        "majority_logical_error_rate": m_rate,
        "majority_wilson_95_low": m_low,
        "majority_wilson_95_high": m_high,
        "relative_logical_error_reduction_vs_majority": (m_rate - v_rate) / m_rate if m_rate else None,
        "decoder_runtime_seconds_per_shot": elapsed / shots if shots else 0.0,
    }


def summarize(rows: list[dict]) -> dict:
    improved = [
        row
        for row in rows
        if row["relative_logical_error_reduction_vs_majority"] is not None
        and row["relative_logical_error_reduction_vs_majority"] > 0
    ]
    best = max(
        rows,
        key=lambda row: (
            row["relative_logical_error_reduction_vs_majority"]
            if row["relative_logical_error_reduction_vs_majority"] is not None
            else -1
        ),
    )
    return {
        "configuration_count": len(rows),
        "improved_configurations": len(improved),
        "best_relative_reduction": best["relative_logical_error_reduction_vs_majority"],
        "best_configuration": {
            "distance": best["distance"],
            "rounds": best["rounds"],
            "data_error": best["data_error"],
            "measurement_error": best["measurement_error"],
            "viterbi_logical_error_rate": best["viterbi_logical_error_rate"],
            "majority_logical_error_rate": best["majority_logical_error_rate"],
        },
        "max_decoder_runtime_seconds_per_shot": max(row["decoder_runtime_seconds_per_shot"] for row in rows),
    }


def markdown(report: dict) -> str:
    lines = [
        "# B2 Phenomenological Repetition Decoder v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Configurations: {report['summary']['configuration_count']}",
        f"- Improved configurations: {report['summary']['improved_configurations']}",
        f"- Best relative reduction vs majority: {report['summary']['best_relative_reduction']:.2%}",
        f"- Max decoder runtime / shot: {report['summary']['max_decoder_runtime_seconds_per_shot']:.6g} s",
        "",
        "## Results",
        "",
        "| d | rounds | p_data | p_meas | Viterbi pL | Majority pL | Reduction | runtime/shot |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["results"]:
        reduction = row["relative_logical_error_reduction_vs_majority"]
        reduction_text = "n/a" if reduction is None else f"{reduction:.2%}"
        lines.append(
            f"| {row['distance']} | {row['rounds']} | {row['data_error']:.4g} | "
            f"{row['measurement_error']:.4g} | {row['viterbi_logical_error_rate']:.4g} | "
            f"{row['majority_logical_error_rate']:.4g} | {reduction_text} | "
            f"{row['decoder_runtime_seconds_per_shot']:.4g} |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def run_experiment(args: argparse.Namespace) -> dict:
    rng = np.random.default_rng(args.seed)
    rows = []
    for distance in parse_int_list(args.distances):
        if distance <= 0 or distance % 2 == 0:
            raise ValueError(f"distance must be positive and odd: {distance}")
        if distance > 8:
            raise ValueError("fallback Viterbi decoder is intended for distances <= 8")
        rounds = distance if args.rounds == "distance" else int(args.rounds)
        for data_error in parse_float_list(args.data_errors):
            for ratio in parse_float_list(args.measurement_error_ratios):
                rows.append(
                    simulate_config(
                        distance=distance,
                        rounds=rounds,
                        data_error=data_error,
                        measurement_error=data_error * ratio,
                        shots=args.shots,
                        rng=rng,
                    )
                )
    return {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 phenomenological repetition-code decoder fallback",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "phenomenological_decoder_fallback_not_surface_code_claim",
        "method": "small_repetition_memory_viterbi_syndrome_decoder_v0",
        "seed": args.seed,
        "shots_per_configuration": args.shots,
        "summary": summarize(rows),
        "results": rows,
        "limits": [
            "This is a phenomenological repetition-code memory model, not a surface-code or LDPC result.",
            "The decoder is a transparent Viterbi/minimum-weight fallback for small distances, not PyMatching.",
            "Data and measurement errors are independent bit-flip events; no leakage or correlated two-qubit circuit noise is modeled.",
            "The purpose is to establish B2's decoder interface and syndrome-history reporting before adding Stim/PyMatching or code search.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distances", default="3,5,7")
    parser.add_argument("--rounds", default="distance")
    parser.add_argument("--data-errors", default="0.003,0.005,0.01,0.02")
    parser.add_argument("--measurement-error-ratios", default="1.0")
    parser.add_argument("--shots", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=220626)
    parser.add_argument("--json-output", type=Path, default=Path("results/B2_phenomenological_repetition_decoder_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B2_phenomenological_repetition_decoder.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run_experiment(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
