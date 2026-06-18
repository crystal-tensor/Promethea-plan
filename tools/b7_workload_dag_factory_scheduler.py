#!/usr/bin/env python3
"""Add workload-DAG and factory-throughput scheduling to the B7 B1/B2 bridge."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


FACTORY_VARIANTS = {
    "serial_factory": {"factory_count": 1, "factory_cycle_rounds": 12, "factory_tile_multiplier": 2.0},
    "balanced_factories": {"factory_count": 4, "factory_cycle_rounds": 10, "factory_tile_multiplier": 2.25},
    "throughput_heavy_factories": {"factory_count": 8, "factory_cycle_rounds": 8, "factory_tile_multiplier": 2.75},
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def magic_state_demand(metrics: dict, density: float) -> int:
    return int(math.ceil(float(metrics["two_qubit_gate_count"]) * density))


def factory_rounds(demand: int, variant: dict) -> int:
    if demand <= 0:
        return 0
    batches = math.ceil(demand / int(variant["factory_count"]))
    return batches * int(variant["factory_cycle_rounds"])


def build_dag(metrics: dict, variant_name: str, variant: dict, magic_density: float) -> list[dict]:
    logical_layers = int(metrics["logical_layer_count_with_init_readout"])
    b2_rounds = int(metrics["b2_rounds_per_logical_layer"])
    data_rounds = logical_layers * b2_rounds
    twoq_rounds = int(metrics["two_qubit_layers"]) * b2_rounds
    demand = magic_state_demand(metrics, magic_density)
    factory_work_rounds = factory_rounds(demand, variant)
    feed_forward_rounds = max(1, math.ceil(math.log2(max(2, int(metrics["logical_qubits"])))))
    return [
        {
            "id": "logical_memory_init",
            "kind": "data_path",
            "rounds": b2_rounds,
            "depends_on": [],
        },
        {
            "id": "two_qubit_data_path",
            "kind": "data_path",
            "rounds": twoq_rounds,
            "depends_on": ["logical_memory_init"],
        },
        {
            "id": f"{variant_name}_magic_state_queue",
            "kind": "factory_path",
            "magic_state_demand_proxy": demand,
            "rounds": factory_work_rounds,
            "depends_on": ["logical_memory_init"],
        },
        {
            "id": "feed_forward_placeholder",
            "kind": "classical_control_path",
            "rounds": feed_forward_rounds,
            "depends_on": ["two_qubit_data_path", f"{variant_name}_magic_state_queue"],
        },
        {
            "id": "measurement_and_readout",
            "kind": "readout",
            "rounds": b2_rounds,
            "depends_on": ["feed_forward_placeholder"],
        },
        {
            "id": "data_path_total",
            "kind": "summary",
            "rounds": data_rounds,
            "depends_on": ["logical_memory_init", "two_qubit_data_path", "measurement_and_readout"],
        },
    ]


def schedule(metrics: dict, variant_name: str, variant: dict, magic_density: float) -> dict:
    logical_qubits = int(metrics["logical_qubits"])
    b2_physical_qubits = int(metrics["b2_physical_qubits_per_logical_tile"])
    data_physical_qubits = logical_qubits * b2_physical_qubits
    factory_physical_qubits = int(
        math.ceil(int(variant["factory_count"]) * b2_physical_qubits * float(variant["factory_tile_multiplier"]))
    )
    total_physical_qubits = data_physical_qubits + factory_physical_qubits
    dag = build_dag(metrics, variant_name, variant, magic_density)
    data_rounds = next(node["rounds"] for node in dag if node["id"] == "data_path_total")
    factory_node = next(node for node in dag if node["kind"] == "factory_path")
    feed_forward = next(node["rounds"] for node in dag if node["id"] == "feed_forward_placeholder")
    readout_rounds = int(metrics["b2_rounds_per_logical_layer"])
    critical_rounds = max(data_rounds, factory_node["rounds"]) + feed_forward + readout_rounds
    bottleneck = "factory_path" if factory_node["rounds"] > data_rounds else "data_path"
    return {
        "variant": variant_name,
        "model_status": "workload_dag_factory_schedule_not_physical_layout",
        "logical_qubits": logical_qubits,
        "data_physical_qubits": data_physical_qubits,
        "factory_physical_qubits": factory_physical_qubits,
        "total_physical_qubits": total_physical_qubits,
        "factory_count": int(variant["factory_count"]),
        "factory_cycle_rounds": int(variant["factory_cycle_rounds"]),
        "magic_state_density_proxy": magic_density,
        "magic_state_demand_proxy": factory_node["magic_state_demand_proxy"],
        "data_rounds": data_rounds,
        "factory_rounds": factory_node["rounds"],
        "feed_forward_rounds": feed_forward,
        "critical_path_rounds": critical_rounds,
        "space_time_volume": total_physical_qubits * critical_rounds,
        "bottleneck": bottleneck,
        "dag_nodes": dag,
    }


def compare(workload: str, before: dict, after: dict, variant_name: str, variant: dict, magic_density: float) -> dict:
    before_schedule = schedule(before, variant_name, variant, magic_density)
    after_schedule = schedule(after, variant_name, variant, magic_density)
    return {
        "workload": workload,
        "factory_variant": variant_name,
        "before": before_schedule,
        "after": after_schedule,
        "critical_path_reduction": before_schedule["critical_path_rounds"] / after_schedule["critical_path_rounds"]
        if after_schedule["critical_path_rounds"]
        else None,
        "space_time_volume_reduction": before_schedule["space_time_volume"] / after_schedule["space_time_volume"]
        if after_schedule["space_time_volume"]
        else None,
        "magic_state_demand_reduction": before_schedule["magic_state_demand_proxy"] / after_schedule["magic_state_demand_proxy"]
        if after_schedule["magic_state_demand_proxy"]
        else None,
        "bottleneck_before": before_schedule["bottleneck"],
        "bottleneck_after": after_schedule["bottleneck"],
    }


def run(args: argparse.Namespace) -> dict:
    bridge = read_json(args.bridge)
    comparisons = []
    for row in bridge["comparisons"]:
        for variant_name, variant in FACTORY_VARIANTS.items():
            comparisons.append(
                compare(
                    row["workload"],
                    row["before"],
                    row["after"],
                    variant_name,
                    variant,
                    args.magic_state_density,
                )
            )
    reductions = [row["space_time_volume_reduction"] for row in comparisons if row["space_time_volume_reduction"]]
    factory_bottleneck_count = sum(
        1
        for row in comparisons
        if row["bottleneck_before"] == "factory_path" or row["bottleneck_after"] == "factory_path"
    )
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 workload-DAG factory-throughput schedule",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "workload_dag_factory_schedule_not_physical_layout",
        "method": "b7_workload_dag_factory_scheduler_v0",
        "source_bridge": str(args.bridge),
        "workload_count": len(bridge["comparisons"]),
        "factory_variants": sorted(FACTORY_VARIANTS),
        "comparison_count": len(comparisons),
        "magic_state_density_proxy": args.magic_state_density,
        "min_space_time_volume_reduction": min(reductions),
        "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
        "factory_bottleneck_comparisons": factory_bottleneck_count,
        "comparisons": comparisons,
        "limits": [
            "This is a workload-DAG and factory-throughput schedule, not a lattice-surgery or physical-layout compiler.",
            "Magic-state demand is a two-qubit-gate density proxy, not a T-count extracted from a fault-tolerant logical circuit.",
            "Factory footprints and cycle rounds are scenario parameters, not hardware-calibrated measurements.",
            "The purpose is to test whether B1/B2 gains survive explicit factory throughput bottlenecks before investing in a full layout model.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B7 Workload-DAG Factory-Throughput Schedule v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Workloads: {report['workload_count']}",
        f"- Factory variants: {report['factory_variants']}",
        f"- Comparisons: {report['comparison_count']}",
        f"- Magic-state density proxy: {report['magic_state_density_proxy']}",
        f"- Minimum STV reduction: {report['min_space_time_volume_reduction']:.3f}x",
        f"- Mean STV reduction: {report['mean_space_time_volume_reduction']:.3f}x",
        f"- Comparisons with a factory bottleneck: {report['factory_bottleneck_comparisons']}",
        "",
        "## Comparisons",
        "",
        "| workload | factory variant | bottleneck before | bottleneck after | critical path reduction | STV reduction | magic demand reduction |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in report["comparisons"]:
        lines.append(
            f"| {row['workload']} | {row['factory_variant']} | {row['bottleneck_before']} | "
            f"{row['bottleneck_after']} | {row['critical_path_reduction']:.3f}x | "
            f"{row['space_time_volume_reduction']:.3f}x | {row['magic_state_demand_reduction']:.3f}x |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", type=Path, default=Path("results/B7_b1_b2_dependency_schedule_bridge_v0.json"))
    parser.add_argument("--magic-state-density", type=float, default=0.5)
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_workload_dag_factory_schedule_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B7_workload_dag_factory_schedule.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "comparison_count": report["comparison_count"],
                    "min_space_time_volume_reduction": report["min_space_time_volume_reduction"],
                    "mean_space_time_volume_reduction": report["mean_space_time_volume_reduction"],
                    "factory_bottleneck_comparisons": report["factory_bottleneck_comparisons"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
