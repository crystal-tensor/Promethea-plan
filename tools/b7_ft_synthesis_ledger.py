#!/usr/bin/env python3
"""Schedule B7 workloads with a rotation-family fault-tolerant synthesis ledger.

This is still a proxy, not a physical layout or lattice-surgery result. Its
purpose is to replace the earlier single fixed T-cost for every non-Clifford
rotation with a transparent ledger:

- Clifford Pauli rotations cost 0.
- Exact odd pi/4 Pauli rotations cost 1 T gate.
- Exact odd pi/8 Pauli rotations use a separate conservative cost.
- Unknown or arbitrary rotations keep the fixed fallback synthesis cost.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from b7_dependency_schedule_bridge import load_metric_pairs
from b7_workload_dag_factory_scheduler import FACTORY_VARIANTS


PARAM_RE = re.compile(r"^([a-z][a-z0-9_]*)\((.*?)\)\s+(.*);$", re.IGNORECASE)
GATE_RE = re.compile(r"^([a-z][a-z0-9_]*)\b\s*(.*);$", re.IGNORECASE)
QUBIT_RE = re.compile(r"q\[(\d+)\]")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def split_params(params: str) -> list[str]:
    return [part.strip() for part in params.split(",") if part.strip()]


def angle_to_pi_units(expr: str) -> float | None:
    expr = expr.strip().lower().replace(" ", "")
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Constant,
        ast.Name,
        ast.Load,
    )
    try:
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                return None
            if isinstance(node, ast.Name) and node.id != "pi":
                return None
        value = float(eval(compile(tree, "<angle>", "eval"), {"__builtins__": {}}, {"pi": math.pi}))
        return value / math.pi
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError):
        return None


def near_integer(value: float, tolerance: float = 1e-9) -> bool:
    return abs(value - round(value)) <= tolerance


def classify_rotation(expr: str) -> str:
    units = angle_to_pi_units(expr)
    if units is None:
        return "unknown_or_symbolic_rotation"
    units = units % 2.0
    if near_integer(2.0 * units):
        return "clifford_rotation"
    if near_integer(4.0 * units):
        return "exact_pi_over_4_rotation"
    if near_integer(8.0 * units):
        return "exact_pi_over_8_rotation"
    return "arbitrary_numeric_rotation"


def rotation_cost(expr: str, args: argparse.Namespace) -> tuple[int, str]:
    family = classify_rotation(expr)
    if family == "clifford_rotation":
        return 0, family
    if family == "exact_pi_over_4_rotation":
        return args.pi_over_4_t_cost, family
    if family == "exact_pi_over_8_rotation":
        return args.pi_over_8_t_cost, family
    if family == "arbitrary_numeric_rotation":
        return args.arbitrary_rotation_t_cost, family
    return args.unknown_rotation_t_cost, family


def gate_rotation_params(gate: str, params: list[str]) -> list[tuple[str, str]]:
    if gate in {"rz", "rx", "ry", "u1"} and params:
        return [(gate, params[0])]
    if gate == "u2" and len(params) == 2:
        return [("ry", "pi/2"), ("rz", params[1]), ("rz", params[0])]
    if gate in {"u3", "u"} and len(params) == 3:
        theta, phi, lam = params
        return [("rz", lam), ("ry", theta), ("rz", phi)]
    return []


def qasm_ft_resources(path: Path, args: argparse.Namespace) -> dict:
    qubit_layers: dict[int, int] = {}
    t_count = 0
    direct_t_count = 0
    ccx_count = 0
    operation_count = 0
    rotation_count = 0
    class_counts: Counter[str] = Counter()
    cost_by_class: Counter[str] = Counter()
    gate_counts: Counter[str] = Counter()

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        lower = line.lower()
        if (
            not lower
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

        gate_counts[gate] += 1
        qubits = [int(value) for value in QUBIT_RE.findall(operand_text)]
        cost = 0
        if gate in {"t", "tdg"}:
            cost = 1
            direct_t_count += 1
            class_counts["direct_t_gate"] += 1
            cost_by_class["direct_t_gate"] += 1
        elif gate == "ccx":
            cost = 7
            ccx_count += 1
            class_counts["ccx_decomposition"] += 1
            cost_by_class["ccx_decomposition"] += 7
        else:
            for _axis, expr in gate_rotation_params(gate, params):
                component_cost, family = rotation_cost(expr, args)
                cost += component_cost
                rotation_count += 1
                class_counts[family] += 1
                cost_by_class[family] += component_cost

        if cost <= 0:
            continue
        active_qubits = qubits or [-1]
        start_layer = max(qubit_layers.get(q, 0) for q in active_qubits) + 1
        end_layer = start_layer + cost - 1
        for q in active_qubits:
            qubit_layers[q] = end_layer
        t_count += cost

    return {
        "path": str(path),
        "operation_count_scanned": operation_count,
        "logical_t_count_ledger": t_count,
        "logical_t_depth_ledger": max(qubit_layers.values()) if qubit_layers else 0,
        "direct_t_count": direct_t_count,
        "ccx_count": ccx_count,
        "rotation_component_count": rotation_count,
        "rotation_family_counts": dict(sorted(class_counts.items())),
        "t_cost_by_family": dict(sorted(cost_by_class.items())),
        "gate_counts": dict(sorted(gate_counts.items())),
    }


def load_ft_resource_pairs(before_metrics: Path, after_metrics: Path, args: argparse.Namespace) -> list[tuple[str, dict, dict, dict, dict]]:
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
                qasm_ft_resources(before_path, args),
                qasm_ft_resources(after_path, args),
            )
        )
    return out


def aggregate_ft_resources(rows: list[dict]) -> dict:
    family_counts: Counter[str] = Counter()
    costs: Counter[str] = Counter()
    gate_counts: Counter[str] = Counter()
    for row in rows:
        family_counts.update(row["rotation_family_counts"])
        costs.update(row["t_cost_by_family"])
        gate_counts.update(row["gate_counts"])
    return {
        "path": "aggregate_30_circuits",
        "operation_count_scanned": sum(row["operation_count_scanned"] for row in rows),
        "logical_t_count_ledger": sum(row["logical_t_count_ledger"] for row in rows),
        "logical_t_depth_ledger": sum(row["logical_t_depth_ledger"] for row in rows),
        "direct_t_count": sum(row["direct_t_count"] for row in rows),
        "ccx_count": sum(row["ccx_count"] for row in rows),
        "rotation_component_count": sum(row["rotation_component_count"] for row in rows),
        "rotation_family_counts": dict(sorted(family_counts.items())),
        "t_cost_by_family": dict(sorted(costs.items())),
        "gate_counts": dict(sorted(gate_counts.items())),
    }


def factory_rounds_from_t_count(t_count: int, variant: dict) -> int:
    if t_count <= 0:
        return 0
    batches = math.ceil(t_count / int(variant["factory_count"]))
    return batches * int(variant["factory_cycle_rounds"])


def schedule(metrics: dict, ft_resources: dict, variant_name: str, variant: dict) -> dict:
    logical_qubits = int(metrics["logical_qubits"])
    b2_physical_qubits = int(metrics["b2_physical_qubits_per_logical_tile"])
    data_physical_qubits = logical_qubits * b2_physical_qubits
    factory_physical_qubits = int(
        math.ceil(int(variant["factory_count"]) * b2_physical_qubits * float(variant["factory_tile_multiplier"]))
    )
    total_physical_qubits = data_physical_qubits + factory_physical_qubits
    b2_rounds = int(metrics["b2_rounds_per_logical_layer"])
    data_rounds = int(metrics["logical_layer_count_with_init_readout"]) * b2_rounds
    factory_rounds = factory_rounds_from_t_count(ft_resources["logical_t_count_ledger"], variant)
    feed_forward_rounds = max(1, math.ceil(math.log2(max(2, logical_qubits))))
    critical_rounds = max(data_rounds, factory_rounds) + feed_forward_rounds + b2_rounds
    bottleneck = "factory_path" if factory_rounds > data_rounds else "data_path"
    return {
        "variant": variant_name,
        "model_status": "ft_synthesis_ledger_schedule_not_physical_layout",
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
        "logical_t_count_ledger": ft_resources["logical_t_count_ledger"],
        "logical_t_depth_ledger": ft_resources["logical_t_depth_ledger"],
        "rotation_family_counts": ft_resources["rotation_family_counts"],
        "t_cost_by_family": ft_resources["t_cost_by_family"],
        "direct_t_count": ft_resources["direct_t_count"],
        "ccx_count": ft_resources["ccx_count"],
    }


def compare(workload: str, before_metrics: dict, after_metrics: dict, before_ft: dict, after_ft: dict, variant_name: str, variant: dict) -> dict:
    before_schedule = schedule(before_metrics, before_ft, variant_name, variant)
    after_schedule = schedule(after_metrics, after_ft, variant_name, variant)
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
        "logical_t_count_reduction": before_schedule["logical_t_count_ledger"] / after_schedule["logical_t_count_ledger"]
        if after_schedule["logical_t_count_ledger"]
        else None,
        "logical_t_depth_reduction": before_schedule["logical_t_depth_ledger"] / after_schedule["logical_t_depth_ledger"]
        if after_schedule["logical_t_depth_ledger"]
        else None,
        "bottleneck_before": before_schedule["bottleneck"],
        "bottleneck_after": after_schedule["bottleneck"],
    }


def run(args: argparse.Namespace) -> dict:
    bridge = read_json(args.bridge)
    pairs = load_ft_resource_pairs(args.before_metrics, args.after_metrics, args)
    ft_by_key = {key: (before_ft, after_ft) for key, _before_metrics, _after_metrics, before_ft, after_ft in pairs}
    before_aggregate_ft = aggregate_ft_resources([row[3] for row in pairs])
    after_aggregate_ft = aggregate_ft_resources([row[4] for row in pairs])
    workloads = []
    resource_rows = []
    for bridge_row in bridge["comparisons"]:
        workload = bridge_row["workload"]
        if workload == "aggregate_30_circuits":
            before_ft, after_ft = before_aggregate_ft, after_aggregate_ft
        else:
            before_ft, after_ft = ft_by_key[workload]
        workloads.append((workload, bridge_row["before"], bridge_row["after"], before_ft, after_ft))
        resource_rows.append(
            {
                "workload": workload,
                "before_logical_t_count_ledger": before_ft["logical_t_count_ledger"],
                "after_logical_t_count_ledger": after_ft["logical_t_count_ledger"],
                "logical_t_count_reduction": before_ft["logical_t_count_ledger"] / after_ft["logical_t_count_ledger"]
                if after_ft["logical_t_count_ledger"]
                else None,
                "before_rotation_family_counts": before_ft["rotation_family_counts"],
                "after_rotation_family_counts": after_ft["rotation_family_counts"],
                "before_t_cost_by_family": before_ft["t_cost_by_family"],
                "after_t_cost_by_family": after_ft["t_cost_by_family"],
            }
        )

    comparisons = []
    for workload, before_metrics, after_metrics, before_ft, after_ft in workloads:
        for variant_name, variant in FACTORY_VARIANTS.items():
            comparisons.append(compare(workload, before_metrics, after_metrics, before_ft, after_ft, variant_name, variant))

    reductions = [row["space_time_volume_reduction"] for row in comparisons if row["space_time_volume_reduction"]]
    t_reductions = [row["logical_t_count_reduction"] for row in comparisons if row["logical_t_count_reduction"] is not None]
    factory_after = sum(1 for row in comparisons if row["bottleneck_after"] == "factory_path")
    data_after = sum(1 for row in comparisons if row["bottleneck_after"] == "data_path")
    min_row = min(comparisons, key=lambda row: row["space_time_volume_reduction"])
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 FT synthesis ledger schedule",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": "ft_synthesis_ledger_proxy_not_physical_layout",
        "method": "b7_ft_synthesis_ledger_v0",
        "source_bridge": str(args.bridge),
        "b1_before_metrics": str(args.before_metrics),
        "b1_after_metrics": str(args.after_metrics),
        "cost_model": {
            "clifford_rotation_t_cost": 0,
            "pi_over_4_rotation_t_cost": args.pi_over_4_t_cost,
            "pi_over_8_rotation_t_cost": args.pi_over_8_t_cost,
            "arbitrary_rotation_t_cost": args.arbitrary_rotation_t_cost,
            "unknown_rotation_t_cost": args.unknown_rotation_t_cost,
            "ccx_t_cost": 7,
        },
        "workload_count": len(workloads),
        "factory_variants": sorted(FACTORY_VARIANTS),
        "comparison_count": len(comparisons),
        "min_space_time_volume_reduction": min(reductions),
        "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
        "factory_bottleneck_after_count": factory_after,
        "data_bottleneck_after_count": data_after,
        "min_logical_t_count_reduction": min(t_reductions) if t_reductions else None,
        "mean_logical_t_count_reduction": sum(t_reductions) / len(t_reductions) if t_reductions else None,
        "min_row": {
            "workload": min_row["workload"],
            "factory_variant": min_row["factory_variant"],
            "space_time_volume_reduction": min_row["space_time_volume_reduction"],
            "bottleneck_before": min_row["bottleneck_before"],
            "bottleneck_after": min_row["bottleneck_after"],
        },
        "resource_rows": resource_rows,
        "comparisons": comparisons,
        "limits": [
            "This ledger classifies exact Pauli rotations by angle family; it is not a lattice-surgery or physical layout result.",
            "Exact odd pi/4 rotations are counted as one T gate using Clifford conjugation for X/Y axes.",
            "Unknown, symbolic, and arbitrary numeric rotations retain conservative fixed fallback costs.",
            "Data-path dominance after re-costing does not prove solved architecture; it identifies the next bottleneck after factory pressure is reduced.",
        ],
    }


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6g}"


def markdown(report: dict) -> str:
    min_row = report["min_row"]
    lines = [
        "# B7 FT Synthesis Ledger v0.1",
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
        f"- Minimum STV reduction: {report['min_space_time_volume_reduction']:.6f}x",
        f"- Mean STV reduction: {report['mean_space_time_volume_reduction']:.6f}x",
        f"- Minimum row: `{min_row['workload']}` / `{min_row['factory_variant']}`",
        f"- Minimum row bottleneck before/after: {min_row['bottleneck_before']} -> {min_row['bottleneck_after']}",
        f"- After rows bottlenecked by factory/data: {report['factory_bottleneck_after_count']} / {report['data_bottleneck_after_count']}",
        f"- Minimum logical T-count ledger reduction: {report['min_logical_t_count_reduction']:.6f}x",
        f"- Mean logical T-count ledger reduction: {report['mean_logical_t_count_reduction']:.6f}x",
        "",
        "## Cost Model",
        "",
    ]
    for key, value in report["cost_model"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Resource Ledger By Workload",
            "",
            "| workload | before T ledger | after T ledger | T reduction | after families | after T cost by family |",
            "|---|---:|---:|---:|---|---|",
        ]
    )
    for row in report["resource_rows"]:
        lines.append(
            f"| {row['workload']} | {row['before_logical_t_count_ledger']} | "
            f"{row['after_logical_t_count_ledger']} | {fmt(row['logical_t_count_reduction'])}x | "
            f"`{row['after_rotation_family_counts']}` | `{row['after_t_cost_by_family']}` |"
        )
    lines.extend(
        [
            "",
            "## Schedule Comparisons",
            "",
            "| workload | factory variant | bottleneck before | bottleneck after | STV reduction | T-count reduction | before/after T ledger |",
            "|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in report["comparisons"]:
        lines.append(
            f"| {row['workload']} | {row['factory_variant']} | {row['bottleneck_before']} | "
            f"{row['bottleneck_after']} | {row['space_time_volume_reduction']:.6f}x | "
            f"{fmt(row['logical_t_count_reduction'])}x | "
            f"{row['before']['logical_t_count_ledger']} / {row['after']['logical_t_count_ledger']} |"
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
        default=Path("results/b1_u3_phase_factored_optimizer/after_metrics.json"),
    )
    parser.add_argument("--pi-over-4-t-cost", type=int, default=1)
    parser.add_argument("--pi-over-8-t-cost", type=int, default=4)
    parser.add_argument("--arbitrary-rotation-t-cost", type=int, default=20)
    parser.add_argument("--unknown-rotation-t-cost", type=int, default=20)
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_ft_synthesis_ledger_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B7_ft_synthesis_ledger.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = run(args)
    write_json(args.json_output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "comparison_count": report["comparison_count"],
                    "min_space_time_volume_reduction": report["min_space_time_volume_reduction"],
                    "mean_space_time_volume_reduction": report["mean_space_time_volume_reduction"],
                    "factory_bottleneck_after_count": report["factory_bottleneck_after_count"],
                    "data_bottleneck_after_count": report["data_bottleneck_after_count"],
                    "min_row": report["min_row"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
