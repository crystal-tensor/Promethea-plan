#!/usr/bin/env python3
"""Schedule B7 workloads with logical T-count/T-depth proxy factory demand."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from b7_dependency_schedule_bridge import aggregate_metrics, circuit_key, load_metric_pairs
from b7_workload_dag_factory_scheduler import FACTORY_VARIANTS


PARAM_RE = re.compile(r"^([a-z][a-z0-9_]*)\((.*?)\)\s+(.*);$", re.IGNORECASE)
GATE_RE = re.compile(r"^([a-z][a-z0-9_]*)\b\s*(.*);$", re.IGNORECASE)
QUBIT_RE = re.compile(r"q\[(\d+)\]")


def angle_to_pi_units(expr: str) -> float | None:
    expr = expr.strip().lower().replace(" ", "")
    if expr in {"0", "0.0"}:
        return 0.0
    sign = -1.0 if expr.startswith("-") else 1.0
    if expr.startswith("-"):
        expr = expr[1:]
    if expr == "pi":
        return sign
    if expr.startswith("pi/"):
        try:
            return sign / float(expr.split("/", 1)[1])
        except ValueError:
            return None
    if expr.startswith("pi*"):
        try:
            return sign * float(expr.split("*", 1)[1])
        except ValueError:
            return None
    try:
        return sign * float(expr) / math.pi
    except ValueError:
        return None


def is_clifford_angle(expr: str, tolerance: float = 1e-9) -> bool:
    units = angle_to_pi_units(expr)
    if units is None:
        return False
    doubled = 2.0 * units
    return abs(doubled - round(doubled)) <= tolerance


def split_params(params: str) -> list[str]:
    return [part.strip() for part in params.split(",") if part.strip()]


def qasm_t_resources(path: Path, rotation_t_cost: int) -> dict:
    qubit_layers: dict[int, int] = {}
    t_count = 0
    direct_t_count = 0
    ccx_count = 0
    non_clifford_rotation_count = 0
    unknown_rotation_count = 0
    operation_count = 0

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        lower = line.lower()
        if (
            not line
            or lower.startswith("//")
            or lower.startswith("openqasm")
            or lower.startswith("include")
            or lower.startswith("qreg")
            or lower.startswith("creg")
            or lower.startswith("barrier")
            or lower.startswith("measure")
        ):
            continue
        operation_count += 1
        param_match = PARAM_RE.match(lower)
        gate_match = GATE_RE.match(lower)
        if param_match:
            gate = param_match.group(1)
            params = split_params(param_match.group(2))
            operand_text = param_match.group(3)
        elif gate_match:
            gate = gate_match.group(1)
            params = []
            operand_text = gate_match.group(2)
        else:
            continue

        qubits = [int(value) for value in QUBIT_RE.findall(operand_text)]
        cost = 0
        if gate in {"t", "tdg"}:
            cost = 1
            direct_t_count += 1
        elif gate == "ccx":
            cost = 7
            ccx_count += 1
        elif gate in {"rz", "rx", "ry", "u1"}:
            if params and not is_clifford_angle(params[0]):
                cost = rotation_t_cost
                non_clifford_rotation_count += 1
                if angle_to_pi_units(params[0]) is None:
                    unknown_rotation_count += 1
        elif gate in {"u2", "u3"}:
            for param in params:
                if not is_clifford_angle(param):
                    cost += rotation_t_cost
                    non_clifford_rotation_count += 1
                    if angle_to_pi_units(param) is None:
                        unknown_rotation_count += 1

        if cost <= 0:
            continue
        t_count += cost
        active_qubits = qubits or [-1]
        start_layer = max(qubit_layers.get(q, 0) for q in active_qubits) + 1
        end_layer = start_layer + cost - 1
        for q in active_qubits:
            qubit_layers[q] = end_layer

    return {
        "path": str(path),
        "operation_count_scanned": operation_count,
        "logical_t_count_proxy": t_count,
        "logical_t_depth_proxy": max(qubit_layers.values()) if qubit_layers else 0,
        "direct_t_count": direct_t_count,
        "ccx_count": ccx_count,
        "non_clifford_rotation_count": non_clifford_rotation_count,
        "unknown_rotation_count": unknown_rotation_count,
        "rotation_t_cost": rotation_t_cost,
    }


def load_t_resource_pairs(before_metrics: Path, after_metrics: Path, rotation_t_cost: int) -> list[tuple[str, dict, dict, dict, dict]]:
    pairs = load_metric_pairs(before_metrics, after_metrics)
    out = []
    for key, before_metrics_row, after_metrics_row in pairs:
        before_path = Path(before_metrics_row["path"])
        after_path = Path(after_metrics_row["path"])
        out.append(
            (
                key,
                before_metrics_row,
                after_metrics_row,
                qasm_t_resources(before_path, rotation_t_cost),
                qasm_t_resources(after_path, rotation_t_cost),
            )
        )
    return out


def aggregate_t_resources(rows: list[dict]) -> dict:
    return {
        "path": "aggregate_30_circuits",
        "operation_count_scanned": sum(row["operation_count_scanned"] for row in rows),
        "logical_t_count_proxy": sum(row["logical_t_count_proxy"] for row in rows),
        "logical_t_depth_proxy": sum(row["logical_t_depth_proxy"] for row in rows),
        "direct_t_count": sum(row["direct_t_count"] for row in rows),
        "ccx_count": sum(row["ccx_count"] for row in rows),
        "non_clifford_rotation_count": sum(row["non_clifford_rotation_count"] for row in rows),
        "unknown_rotation_count": sum(row["unknown_rotation_count"] for row in rows),
        "rotation_t_cost": rows[0]["rotation_t_cost"] if rows else 0,
    }


def factory_rounds_from_t_count(t_count: int, variant: dict) -> int:
    if t_count <= 0:
        return 0
    batches = math.ceil(t_count / int(variant["factory_count"]))
    return batches * int(variant["factory_cycle_rounds"])


def schedule(metrics: dict, t_resources: dict, variant_name: str, variant: dict) -> dict:
    logical_qubits = int(metrics["logical_qubits"])
    b2_physical_qubits = int(metrics["b2_physical_qubits_per_logical_tile"])
    data_physical_qubits = logical_qubits * b2_physical_qubits
    factory_physical_qubits = int(
        math.ceil(int(variant["factory_count"]) * b2_physical_qubits * float(variant["factory_tile_multiplier"]))
    )
    total_physical_qubits = data_physical_qubits + factory_physical_qubits
    b2_rounds = int(metrics["b2_rounds_per_logical_layer"])
    data_rounds = int(metrics["logical_layer_count_with_init_readout"]) * b2_rounds
    factory_rounds = factory_rounds_from_t_count(t_resources["logical_t_count_proxy"], variant)
    feed_forward_rounds = max(1, math.ceil(math.log2(max(2, logical_qubits))))
    critical_rounds = max(data_rounds, factory_rounds) + feed_forward_rounds + b2_rounds
    bottleneck = "factory_path" if factory_rounds > data_rounds else "data_path"
    return {
        "variant": variant_name,
        "model_status": "logical_t_factory_schedule_not_physical_layout",
        "logical_qubits": logical_qubits,
        "data_physical_qubits": data_physical_qubits,
        "factory_physical_qubits": factory_physical_qubits,
        "total_physical_qubits": total_physical_qubits,
        "factory_count": int(variant["factory_count"]),
        "factory_cycle_rounds": int(variant["factory_cycle_rounds"]),
        "data_rounds": data_rounds,
        "factory_rounds": factory_rounds,
        "feed_forward_rounds": feed_forward_rounds,
        "critical_path_rounds": critical_rounds,
        "space_time_volume": total_physical_qubits * critical_rounds,
        "bottleneck": bottleneck,
        "logical_t_count_proxy": t_resources["logical_t_count_proxy"],
        "logical_t_depth_proxy": t_resources["logical_t_depth_proxy"],
        "non_clifford_rotation_count": t_resources["non_clifford_rotation_count"],
        "direct_t_count": t_resources["direct_t_count"],
        "ccx_count": t_resources["ccx_count"],
    }


def compare(workload: str, before_metrics: dict, after_metrics: dict, before_t: dict, after_t: dict, variant_name: str, variant: dict) -> dict:
    before_schedule = schedule(before_metrics, before_t, variant_name, variant)
    after_schedule = schedule(after_metrics, after_t, variant_name, variant)
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
        "logical_t_count_reduction": before_schedule["logical_t_count_proxy"] / after_schedule["logical_t_count_proxy"]
        if after_schedule["logical_t_count_proxy"]
        else None,
        "logical_t_depth_reduction": before_schedule["logical_t_depth_proxy"] / after_schedule["logical_t_depth_proxy"]
        if after_schedule["logical_t_depth_proxy"]
        else None,
        "bottleneck_before": before_schedule["bottleneck"],
        "bottleneck_after": after_schedule["bottleneck"],
    }


def run(args: argparse.Namespace) -> dict:
    bridge = json.loads(args.bridge.read_text(encoding="utf-8"))
    pairs = load_t_resource_pairs(args.before_metrics, args.after_metrics, args.rotation_t_cost)
    t_by_key = {key: (before_t, after_t) for key, _before_metrics, _after_metrics, before_t, after_t in pairs}
    before_aggregate_t = aggregate_t_resources([row[3] for row in pairs])
    after_aggregate_t = aggregate_t_resources([row[4] for row in pairs])
    workloads = []
    for bridge_row in bridge["comparisons"]:
        workload = bridge_row["workload"]
        if workload == "aggregate_30_circuits":
            before_t, after_t = before_aggregate_t, after_aggregate_t
        else:
            before_t, after_t = t_by_key[workload]
        workloads.append((workload, bridge_row["before"], bridge_row["after"], before_t, after_t))

    comparisons = []
    for workload, before_metrics, after_metrics, before_t, after_t in workloads:
        for variant_name, variant in FACTORY_VARIANTS.items():
            comparisons.append(compare(workload, before_metrics, after_metrics, before_t, after_t, variant_name, variant))

    reductions = [row["space_time_volume_reduction"] for row in comparisons if row["space_time_volume_reduction"]]
    factory_bottleneck_count = sum(
        1
        for row in comparisons
        if row["bottleneck_before"] == "factory_path" or row["bottleneck_after"] == "factory_path"
    )
    t_reductions = [row["logical_t_count_reduction"] for row in comparisons if row["logical_t_count_reduction"] is not None]
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 logical T-resource factory schedule",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": "logical_t_factory_schedule_proxy_not_physical_layout",
        "method": "b7_logical_t_factory_scheduler_v0",
        "source_bridge": str(args.bridge),
        "b1_before_metrics": str(args.before_metrics),
        "b1_after_metrics": str(args.after_metrics),
        "rotation_synthesis_t_cost": args.rotation_t_cost,
        "workload_count": len(workloads),
        "factory_variants": sorted(FACTORY_VARIANTS),
        "comparison_count": len(comparisons),
        "min_space_time_volume_reduction": min(reductions),
        "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
        "factory_bottleneck_comparisons": factory_bottleneck_count,
        "min_logical_t_count_reduction": min(t_reductions) if t_reductions else None,
        "mean_logical_t_count_reduction": sum(t_reductions) / len(t_reductions) if t_reductions else None,
        "comparisons": comparisons,
        "limits": [
            "This is a logical T-resource proxy schedule, not a fault-tolerant synthesis result.",
            "Arbitrary u3/rz/rx/ry non-Clifford rotations are assigned a fixed T synthesis cost.",
            "The current B1 virtual-SWAP pass mostly removes CX/SWAP work, so T-resource reductions may be absent even when routing depth improves.",
            "The purpose is to expose when factory-dominated workloads erase routing/compression gains.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B7 Logical T-Resource Factory Schedule v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Workloads: {report['workload_count']}",
        f"- Factory variants: {report['factory_variants']}",
        f"- Comparisons: {report['comparison_count']}",
        f"- Rotation synthesis T-cost proxy: {report['rotation_synthesis_t_cost']}",
        f"- Minimum STV reduction: {report['min_space_time_volume_reduction']:.3f}x",
        f"- Mean STV reduction: {report['mean_space_time_volume_reduction']:.3f}x",
        f"- Comparisons with factory bottleneck: {report['factory_bottleneck_comparisons']}",
        f"- Minimum logical T-count reduction: {report['min_logical_t_count_reduction']:.3f}x",
        f"- Mean logical T-count reduction: {report['mean_logical_t_count_reduction']:.3f}x",
        "",
        "## Comparisons",
        "",
        "| workload | factory variant | bottleneck before | bottleneck after | STV reduction | T-count reduction | T-depth reduction |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in report["comparisons"]:
        t_depth = row["logical_t_depth_reduction"]
        t_count = row["logical_t_count_reduction"]
        lines.append(
            f"| {row['workload']} | {row['factory_variant']} | {row['bottleneck_before']} | "
            f"{row['bottleneck_after']} | {row['space_time_volume_reduction']:.3f}x | "
            f"{t_count:.3f}x | {t_depth:.3f}x |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", type=Path, default=Path("results/B7_b1_b2_dependency_schedule_bridge_v0.json"))
    parser.add_argument(
        "--before-metrics",
        type=Path,
        default=Path("results/b1_virtual_swap_elimination_level1/before_virtual_swap_metrics.json"),
    )
    parser.add_argument(
        "--after-metrics",
        type=Path,
        default=Path("results/b1_virtual_swap_elimination_level1/after_virtual_swap_metrics.json"),
    )
    parser.add_argument("--rotation-t-cost", type=int, default=20)
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_logical_t_factory_schedule_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B7_logical_t_factory_schedule.md"))
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
                    "mean_logical_t_count_reduction": report["mean_logical_t_count_reduction"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
