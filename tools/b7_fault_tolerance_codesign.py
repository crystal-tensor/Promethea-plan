#!/usr/bin/env python3
"""Estimate planning-level resource gains from fault-tolerance co-design."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


WORKLOADS = {
    "chemistry_phase_estimation": {
        "logical_qubits": 420,
        "t_count": 1.2e10,
        "t_depth": 3.0e9,
        "clifford_depth": 8.0e9,
        "target_logical_failure": 0.01,
        "algorithmic_block_reuse": 1.0,
    },
    "factoring_2048_modular_arithmetic": {
        "logical_qubits": 6200,
        "t_count": 1.1e12,
        "t_depth": 2.2e11,
        "clifford_depth": 1.8e12,
        "target_logical_failure": 0.01,
        "algorithmic_block_reuse": 0.92,
    },
    "hubbard_time_evolution": {
        "logical_qubits": 960,
        "t_count": 8.0e9,
        "t_depth": 1.6e9,
        "clifford_depth": 6.5e9,
        "target_logical_failure": 0.02,
        "algorithmic_block_reuse": 1.15,
    },
}


CONFIGS = {
    "surface_code_serial_factory_baseline": {
        "code_family": "rotated_surface_code",
        "physical_error_rate": 1.0e-3,
        "threshold": 1.0e-2,
        "prefactor": 0.10,
        "factory_count": 4,
        "factory_qubits_per_distance_sq": 18.0,
        "data_qubits_per_distance_sq": 2.0,
        "cycle_time_us": 1.0,
        "routing_overhead": 1.35,
        "lattice_surgery_overhead": 1.25,
        "factory_throughput_t_per_cycle": 0.010,
        "distillation_acceptance": 0.82,
        "schedule_parallelism": 0.42,
    },
    "codesigned_parallel_factory_layout_v0": {
        "code_family": "rotated_surface_code_codesigned_layout",
        "physical_error_rate": 1.0e-3,
        "threshold": 1.0e-2,
        "prefactor": 0.10,
        "factory_count": 12,
        "factory_qubits_per_distance_sq": 14.0,
        "data_qubits_per_distance_sq": 1.75,
        "cycle_time_us": 0.9,
        "routing_overhead": 1.08,
        "lattice_surgery_overhead": 1.05,
        "factory_throughput_t_per_cycle": 0.014,
        "distillation_acceptance": 0.88,
        "schedule_parallelism": 0.66,
    },
}


def logical_error_per_cycle(distance: int, physical_error_rate: float, threshold: float, prefactor: float) -> float:
    exponent = (distance + 1) / 2
    return prefactor * (physical_error_rate / threshold) ** exponent


def choose_distance(workload: dict, config: dict) -> int:
    total_locations = workload["logical_qubits"] * (workload["t_depth"] + workload["clifford_depth"])
    for distance in range(3, 51, 2):
        per_cycle = logical_error_per_cycle(
            distance,
            config["physical_error_rate"],
            config["threshold"],
            config["prefactor"],
        )
        if per_cycle * total_locations <= workload["target_logical_failure"]:
            return distance
    return 51


def estimate(workload_name: str, workload: dict, config_name: str, config: dict) -> dict:
    distance = choose_distance(workload, config)
    distance_sq = distance * distance
    data_physical_qubits = math.ceil(workload["logical_qubits"] * config["data_qubits_per_distance_sq"] * distance_sq)
    factory_physical_qubits = math.ceil(config["factory_count"] * config["factory_qubits_per_distance_sq"] * distance_sq)
    physical_qubits = data_physical_qubits + factory_physical_qubits

    factory_rate = config["factory_count"] * config["factory_throughput_t_per_cycle"] * config["distillation_acceptance"]
    factory_limited_cycles = workload["t_count"] / max(factory_rate, 1.0e-12)
    depth_limited_cycles = (
        workload["t_depth"] / max(config["schedule_parallelism"], 1.0e-12)
        + workload["clifford_depth"] * 0.08
    )
    runtime_cycles = max(factory_limited_cycles, depth_limited_cycles)
    runtime_cycles *= config["routing_overhead"] * config["lattice_surgery_overhead"] / workload["algorithmic_block_reuse"]

    runtime_seconds = runtime_cycles * distance * config["cycle_time_us"] * 1.0e-6
    space_time_volume = physical_qubits * runtime_cycles * distance
    factory_fraction = factory_physical_qubits / physical_qubits

    return {
        "workload": workload_name,
        "config": config_name,
        "model_status": "planning_level_resource_model_not_physical_layout",
        "code_family": config["code_family"],
        "chosen_distance": distance,
        "logical_qubits": workload["logical_qubits"],
        "t_count": workload["t_count"],
        "physical_qubits": physical_qubits,
        "data_physical_qubits": data_physical_qubits,
        "factory_physical_qubits": factory_physical_qubits,
        "factory_fraction": factory_fraction,
        "factory_count": config["factory_count"],
        "runtime_cycles": runtime_cycles,
        "runtime_seconds": runtime_seconds,
        "space_time_volume": space_time_volume,
        "bottleneck": "factory" if factory_limited_cycles >= depth_limited_cycles else "depth",
    }


def run() -> dict:
    rows = []
    comparisons = []
    for workload_name, workload in WORKLOADS.items():
        estimates = {
            config_name: estimate(workload_name, workload, config_name, config)
            for config_name, config in CONFIGS.items()
        }
        rows.extend(estimates.values())
        baseline = estimates["surface_code_serial_factory_baseline"]
        candidate = estimates["codesigned_parallel_factory_layout_v0"]
        comparisons.append(
            {
                "workload": workload_name,
                "baseline_config": baseline["config"],
                "candidate_config": candidate["config"],
                "physical_qubit_reduction": baseline["physical_qubits"] / candidate["physical_qubits"],
                "runtime_reduction": baseline["runtime_seconds"] / candidate["runtime_seconds"],
                "space_time_volume_reduction": baseline["space_time_volume"] / candidate["space_time_volume"],
                "baseline_bottleneck": baseline["bottleneck"],
                "candidate_bottleneck": candidate["bottleneck"],
            }
        )

    reductions = [row["space_time_volume_reduction"] for row in comparisons]
    return {
        "benchmark_id": "B7",
        "method": "fault_tolerance_codesign_resource_model_v0",
        "model_status": "planning_level_resource_model_not_physical_layout",
        "workload_count": len(WORKLOADS),
        "configuration_count": len(rows),
        "baseline_config": "surface_code_serial_factory_baseline",
        "candidate_config": "codesigned_parallel_factory_layout_v0",
        "min_space_time_volume_reduction": min(reductions),
        "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
        "workloads_meeting_25_percent_reduction": sum(1 for value in reductions if value >= 1.25),
        "comparisons": comparisons,
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
