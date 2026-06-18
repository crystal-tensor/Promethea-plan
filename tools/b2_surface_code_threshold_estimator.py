#!/usr/bin/env python3
"""Estimate surface-code target volumes with a documented threshold-law model."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def logical_error_threshold_law(physical_error: float, distance: int, threshold: float, prefactor: float) -> float:
    if physical_error >= threshold:
        return float("inf")
    exponent = (distance + 1) / 2
    return prefactor * (physical_error / threshold) ** exponent


def physical_qubits_rotated_surface_code(distance: int) -> int:
    return 2 * distance * distance - 1


def estimate(
    physical_errors: list[float],
    targets: list[float],
    distances: list[int],
    threshold: float,
    prefactor: float,
) -> dict:
    rows = []
    for physical_error in physical_errors:
        candidates = []
        for distance in distances:
            logical_error = logical_error_threshold_law(physical_error, distance, threshold, prefactor)
            physical_qubits = physical_qubits_rotated_surface_code(distance)
            rounds = distance
            candidates.append(
                {
                    "distance": distance,
                    "physical_qubits": physical_qubits,
                    "rounds": rounds,
                    "space_time_volume": physical_qubits * rounds,
                    "logical_error_rate_estimate": logical_error,
                }
            )
        for target in targets:
            feasible = [row for row in candidates if row["logical_error_rate_estimate"] <= target]
            if feasible:
                best = min(feasible, key=lambda row: (row["space_time_volume"], row["distance"]))
                rows.append(
                    {
                        "physical_error": physical_error,
                        "target_logical_error": target,
                        "met": True,
                        **best,
                    }
                )
            else:
                best_available = min(candidates, key=lambda row: row["logical_error_rate_estimate"])
                rows.append(
                    {
                        "physical_error": physical_error,
                        "target_logical_error": target,
                        "met": False,
                        "distance": None,
                        "physical_qubits": None,
                        "rounds": None,
                        "space_time_volume": None,
                        "best_available_distance": best_available["distance"],
                        "best_available_logical_error_estimate": best_available["logical_error_rate_estimate"],
                    }
                )
    met_count = sum(1 for row in rows if row["met"])
    return {
        "benchmark_id": "B2",
        "method": "surface_code_threshold_law_target_volume_estimate_v0",
        "model_status": "rough_analytic_estimate_not_circuit_level_simulation",
        "threshold": threshold,
        "prefactor": prefactor,
        "distance_count": len(distances),
        "physical_error_count": len(physical_errors),
        "target_count": len(targets),
        "met_count": met_count,
        "unmet_count": len(rows) - met_count,
        "physical_qubit_model": "rotated_surface_code_data_plus_ancilla_proxy_2d2_minus_1",
        "round_model": "rounds_equal_distance",
        "results": rows,
    }


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--physical-errors", default="0.001,0.003,0.005,0.007,0.009")
    parser.add_argument("--targets", default="1e-2,1e-3,1e-4,1e-5")
    parser.add_argument("--distances", default="3,5,7,9,11,13,15,17,19,21,23,25")
    parser.add_argument("--threshold", type=float, default=0.01)
    parser.add_argument("--prefactor", type=float, default=0.1)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    distances = parse_int_list(args.distances)
    for distance in distances:
        if distance <= 0 or distance % 2 == 0:
            raise SystemExit(f"distance must be a positive odd integer: {distance}")
    payload = estimate(
        physical_errors=parse_float_list(args.physical_errors),
        targets=parse_float_list(args.targets),
        distances=distances,
        threshold=args.threshold,
        prefactor=args.prefactor,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
