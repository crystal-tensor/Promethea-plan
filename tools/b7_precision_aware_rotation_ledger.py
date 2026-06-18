#!/usr/bin/env python3
"""Precision-aware rotation synthesis ledger for the B7 gcm_h6 boundary.

This is a planning-level proxy, not a physical layout or certified synthesis
result.  It asks whether the current fixed-cost arbitrary-rotation assumption
is strong enough after an explicit synthesis error budget is attached.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path


FAMILY_COSTS = {
    "clifford_rotation": 0,
    "exact_pi_over_4_rotation": 1,
    "exact_pi_over_8_rotation": 4,
    "direct_t_gate": 1,
    "ccx_decomposition": 7,
    "unknown_or_symbolic_rotation": 20,
}

ANGLE_RE = re.compile(r"^\s*([a-z][a-z0-9]*)\(([^)]*)\)", re.IGNORECASE)
NUMERIC_RE = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def t_count_from_families(families: dict[str, int], arbitrary_rotation_t_cost: int) -> int:
    total = 0
    for family, count in families.items():
        if family == "arbitrary_numeric_rotation":
            total += int(count) * arbitrary_rotation_t_cost
        else:
            total += int(count) * FAMILY_COSTS.get(family, 20)
    return total


def factory_rounds(t_count: int, schedule: dict) -> int:
    if t_count <= 0:
        return 0
    batches = math.ceil(t_count / int(schedule["factory_count"]))
    return batches * int(schedule["factory_cycle_rounds"])


def reschedule(schedule: dict, t_count: int) -> dict:
    rounds = factory_rounds(t_count, schedule)
    tail_rounds = int(schedule["critical_path_rounds"]) - max(
        int(schedule["data_rounds"]),
        int(schedule["factory_rounds"]),
    )
    critical = max(int(schedule["data_rounds"]), rounds) + tail_rounds
    return {
        "logical_t_count_ledger": t_count,
        "factory_rounds": rounds,
        "data_rounds": int(schedule["data_rounds"]),
        "tail_rounds": tail_rounds,
        "critical_path_rounds": critical,
        "space_time_volume": int(schedule["total_physical_qubits"]) * critical,
        "bottleneck": "factory_path" if rounds > int(schedule["data_rounds"]) else "data_path",
    }


def recompute_comparison(row: dict, arbitrary_rotation_t_cost: int) -> dict:
    before_t = t_count_from_families(row["before"]["rotation_family_counts"], arbitrary_rotation_t_cost)
    after_t = t_count_from_families(row["after"]["rotation_family_counts"], arbitrary_rotation_t_cost)
    before = {**row["before"], **reschedule(row["before"], before_t)}
    after = {**row["after"], **reschedule(row["after"], after_t)}
    return {
        "workload": row["workload"],
        "factory_variant": row["factory_variant"],
        "arbitrary_rotation_t_cost": arbitrary_rotation_t_cost,
        "before": before,
        "after": after,
        "space_time_volume_reduction": before["space_time_volume"] / after["space_time_volume"]
        if after["space_time_volume"]
        else None,
        "logical_t_count_reduction": before_t / after_t if after_t else None,
        "bottleneck_before": before["bottleneck"],
        "bottleneck_after": after["bottleneck"],
    }


def portfolio_at_cost(ledger: dict, arbitrary_rotation_t_cost: int) -> dict:
    comparisons = [recompute_comparison(row, arbitrary_rotation_t_cost) for row in ledger["comparisons"]]
    reductions = [row["space_time_volume_reduction"] for row in comparisons if row["space_time_volume_reduction"]]
    min_row = min(comparisons, key=lambda row: row["space_time_volume_reduction"])
    gcm_rows = [
        row for row in comparisons if row["workload"] == "qasmbench_medium_exact/gcm_h6.qasm"
    ]
    gcm_min = min(gcm_rows, key=lambda row: row["space_time_volume_reduction"])
    return {
        "arbitrary_rotation_t_cost": arbitrary_rotation_t_cost,
        "min_space_time_volume_reduction": min(reductions),
        "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
        "min_workload": min_row["workload"],
        "min_factory_variant": min_row["factory_variant"],
        "min_bottleneck_after": min_row["bottleneck_after"],
        "gcm_h6_min_space_time_volume_reduction": gcm_min["space_time_volume_reduction"],
        "gcm_h6_min_factory_variant": gcm_min["factory_variant"],
        "factory_bottleneck_after_count": sum(1 for row in comparisons if row["bottleneck_after"] == "factory_path"),
        "data_bottleneck_after_count": sum(1 for row in comparisons if row["bottleneck_after"] == "data_path"),
    }


def ross_selinger_style_cost(total_error_budget: float, arbitrary_count: int, alpha: float, beta: float) -> dict:
    if arbitrary_count <= 0:
        return {
            "total_error_budget": total_error_budget,
            "per_rotation_error_budget": None,
            "arbitrary_rotation_t_cost": 0,
        }
    per_rotation = total_error_budget / arbitrary_count
    cost = max(0, math.ceil(alpha * math.log2(1.0 / per_rotation) + beta))
    return {
        "total_error_budget": total_error_budget,
        "per_rotation_error_budget": per_rotation,
        "arbitrary_rotation_t_cost": cost,
    }


def target_cost_for_gcm(row: dict, target_reduction: float) -> dict:
    before = row["before"]
    after = row["after"]
    before_stv = float(before["space_time_volume"])
    after_total_physical = int(after["total_physical_qubits"])
    tail_rounds = int(after["critical_path_rounds"]) - max(
        int(after["data_rounds"]),
        int(after["factory_rounds"]),
    )
    max_critical_rounds = math.floor((before_stv / target_reduction) / after_total_physical)
    max_factory_rounds = max_critical_rounds - tail_rounds
    if max_factory_rounds < int(after["data_rounds"]):
        max_t_count = -1
    else:
        max_t_count = (max_factory_rounds // int(after["factory_cycle_rounds"])) * int(after["factory_count"])
    exact_after_t = t_count_from_families({k: v for k, v in after["rotation_family_counts"].items() if k != "arbitrary_numeric_rotation"}, 0)
    arbitrary_count = int(after["rotation_family_counts"].get("arbitrary_numeric_rotation", 0))
    if max_t_count < exact_after_t or arbitrary_count <= 0:
        max_avg_cost = None
    else:
        max_avg_cost = math.floor((max_t_count - exact_after_t) / arbitrary_count)
    return {
        "target_stv_reduction": target_reduction,
        "max_after_t_ledger": max_t_count,
        "fixed_exact_after_t_ledger": exact_after_t,
        "arbitrary_numeric_rotation_count": arbitrary_count,
        "max_average_arbitrary_rotation_t_cost": max_avg_cost,
        "fixed_cost_20_meets_target": max_avg_cost is not None and 20 <= max_avg_cost,
    }


def total_error_needed_for_cost(cost: int, arbitrary_count: int, alpha: float, beta: float) -> float | None:
    if arbitrary_count <= 0:
        return None
    per_rotation = 2 ** (-max(cost - beta, 0.0) / alpha)
    return arbitrary_count * per_rotation


def parse_numeric_rotation_reuse(qasm_path: Path) -> dict:
    if not qasm_path.exists():
        return {"qasm_path": str(qasm_path), "exists": False}
    counter: Counter[str] = Counter()
    instruction_counter: Counter[str] = Counter()
    for line in qasm_path.read_text(encoding="utf-8").splitlines():
        match = ANGLE_RE.match(line)
        if not match:
            continue
        gate, params = match.groups()
        numeric_params = NUMERIC_RE.findall(params)
        if not numeric_params:
            continue
        instruction_counter[f"{gate}({params})"] += 1
        for value in numeric_params:
            counter[value] += 1
    return {
        "qasm_path": str(qasm_path),
        "exists": True,
        "numeric_parameter_occurrences": sum(counter.values()),
        "unique_numeric_parameters": len(counter),
        "numeric_instruction_occurrences": sum(instruction_counter.values()),
        "unique_numeric_instructions": len(instruction_counter),
        "top_numeric_parameters": [{"value": value, "count": count} for value, count in counter.most_common(12)],
        "top_numeric_instructions": [
            {"instruction": value, "count": count} for value, count in instruction_counter.most_common(12)
        ],
    }


def run(args: argparse.Namespace) -> dict:
    ledger = read_json(args.ledger)
    boundary = read_json(args.boundary)
    current_min = min(ledger["comparisons"], key=lambda row: row["space_time_volume_reduction"])
    gcm_throughput = next(
        row
        for row in ledger["comparisons"]
        if row["workload"] == "qasmbench_medium_exact/gcm_h6.qasm"
        and row["factory_variant"] == "throughput_heavy_factories"
    )
    arbitrary_count = int(gcm_throughput["after"]["rotation_family_counts"].get("arbitrary_numeric_rotation", 0))
    target_costs = [target_cost_for_gcm(gcm_throughput, target) for target in args.target_reductions]
    budgets = [
        ross_selinger_style_cost(error_budget, arbitrary_count, args.alpha, args.beta)
        for error_budget in args.total_error_budgets
    ]
    budget_rows = [
        {
            **budget,
            **portfolio_at_cost(ledger, int(budget["arbitrary_rotation_t_cost"])),
        }
        for budget in budgets
    ]
    relaxed_costs = sorted(
        {
            int(row["max_average_arbitrary_rotation_t_cost"])
            for row in target_costs
            if row["max_average_arbitrary_rotation_t_cost"] is not None
        }
        | {20, 18, 17, 16}
    )
    relaxed_rows = [portfolio_at_cost(ledger, cost) for cost in relaxed_costs]
    cost_requirements = []
    for row in target_costs:
        max_cost = row["max_average_arbitrary_rotation_t_cost"]
        cost_requirements.append(
            {
                **row,
                "total_error_budget_needed_at_max_cost_proxy": total_error_needed_for_cost(
                    int(max_cost), arbitrary_count, args.alpha, args.beta
                )
                if max_cost is not None
                else None,
            }
        )
    best_budget = max(budget_rows, key=lambda row: row["min_space_time_volume_reduction"])
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 precision-aware arbitrary-rotation ledger for gcm_h6",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": "precision_aware_rotation_ledger_negative_boundary_not_physical_layout",
        "method": "b7_precision_aware_rotation_ledger_v0",
        "source_ledger": str(args.ledger),
        "source_boundary": str(args.boundary),
        "synthesis_cost_model": {
            "name": "ross_selinger_style_proxy",
            "formula": "ceil(alpha * log2(1 / per_rotation_error_budget) + beta)",
            "alpha": args.alpha,
            "beta": args.beta,
            "allocation": "uniform_total_synthesis_error_budget_over_after_arbitrary_numeric_rotations",
            "caveat": "planning proxy only; not a certified Clifford+T synthesis run",
        },
        "current_min_workload": current_min["workload"],
        "current_min_factory_variant": current_min["factory_variant"],
        "current_min_space_time_volume_reduction": current_min["space_time_volume_reduction"],
        "gcm_h6_throughput_after_arbitrary_numeric_rotation_count": arbitrary_count,
        "gcm_h6_throughput_after_fixed_exact_t_ledger": t_count_from_families(
            {
                k: v
                for k, v in gcm_throughput["after"]["rotation_family_counts"].items()
                if k != "arbitrary_numeric_rotation"
            },
            0,
        ),
        "gcm_h6_throughput_after_current_total_t_ledger": gcm_throughput["after"]["logical_t_count_ledger"],
        "gcm_h6_one_sided_after_target_cost_requirements": cost_requirements,
        "precision_budget_rows": budget_rows,
        "relaxed_cost_rows": relaxed_rows,
        "numeric_rotation_reuse_probe": parse_numeric_rotation_reuse(args.gcm_qasm),
        "best_precision_budget_row": best_budget,
        "portfolio_precision_budgets_clear_1_20": any(
            row["min_space_time_volume_reduction"] >= 1.20 for row in budget_rows
        ),
        "gcm_h6_precision_budgets_clear_1_20": any(
            row["gcm_h6_min_space_time_volume_reduction"] >= 1.20 for row in budget_rows
        ),
        "interpretation": (
            "Under the explicit uniform synthesis-error budgets tested here, the implied arbitrary-rotation T cost "
            "is above the previous fixed cost 20 assumption, so precision-aware synthesis does not close the gcm_h6 "
            "1.20x boundary.  The one-sided 1.20x gcm_h6 throughput row would need after-row average arbitrary-rotation "
            "cost at or below the reported target-cost requirement; when a synthesis-cost change is applied to both "
            "before and after rows, the portfolio still does not clear 1.20x.  A real solution therefore needs a "
            "structural reduction in arbitrary rotations, data rounds, factory timing, or layout."
        ),
        "next_actions": [
            "Attempt a gcm_h6 numeric-rotation structure pass that merges or cancels repeated arbitrary angles.",
            "Test shared-synthesis/cache assumptions for repeated numeric angles as a separate non-physical proxy.",
            "Add layout/factory/feed-forward timing assumptions only after the synthesis/error-budget claim is explicit.",
            "If no structural pass reduces arbitrary rotations, move B7 attention to layout/factory or B1 semantic rewrites.",
        ],
        "limits": [
            "This is not a physical layout, lattice-surgery, or certified synthesis result.",
            "The Ross-Selinger-style proxy is used only to expose the error-budget direction of pressure.",
            "The uniform error allocation is deliberately simple; better allocation can be tested as a future PR.",
            "The QASM reuse probe counts textual numeric parameters/instructions and is not an equivalence proof.",
        ],
        "boundary_input_snapshot": {
            "current_min_workload": boundary.get("current_min_workload"),
            "current_min_factory_variant": boundary.get("current_min_factory_variant"),
            "current_min_space_time_volume_reduction": boundary.get("current_min_space_time_volume_reduction"),
            "gcm_h6_after_arbitrary_numeric_rotation_count": boundary.get(
                "gcm_h6_after_arbitrary_numeric_rotation_count"
            ),
            "gcm_h6_after_arbitrary_numeric_t_cost": boundary.get("gcm_h6_after_arbitrary_numeric_t_cost"),
        },
    }


def fmt(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    if abs(value) < 0.001:
        return f"{value:.3e}"
    return f"{value:.6g}"


def markdown(report: dict) -> str:
    model = report["synthesis_cost_model"]
    reuse = report["numeric_rotation_reuse_probe"]
    lines = [
        "# B7 Precision-Aware Rotation Ledger v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source ledger: `{report['source_ledger']}`",
        f"- Source boundary: `{report['source_boundary']}`",
        f"- Method: `{report['method']}`",
        f"- Current portfolio min row: `{report['current_min_workload']}` / `{report['current_min_factory_variant']}`",
        f"- Current portfolio min STV reduction: {report['current_min_space_time_volume_reduction']:.6f}x",
        f"- gcm_h6 arbitrary numeric rotations after B1/B7 passes: {report['gcm_h6_throughput_after_arbitrary_numeric_rotation_count']}",
        f"- gcm_h6 non-arbitrary exact T ledger after passes: {report['gcm_h6_throughput_after_fixed_exact_t_ledger']}",
        f"- gcm_h6 current total T ledger after passes: {report['gcm_h6_throughput_after_current_total_t_ledger']}",
        f"- Precision budgets clear 1.20x all-variant min: {report['portfolio_precision_budgets_clear_1_20']}",
        f"- Precision budgets clear 1.20x gcm_h6 min: {report['gcm_h6_precision_budgets_clear_1_20']}",
        f"- Interpretation: {report['interpretation']}",
        "",
        "## Cost Model",
        "",
        f"- Name: `{model['name']}`",
        f"- Formula: `{model['formula']}`",
        f"- alpha / beta: {model['alpha']} / {model['beta']}",
        f"- Allocation: {model['allocation']}",
        f"- Caveat: {model['caveat']}",
        "",
        "## Target Cost Requirements For gcm_h6 Throughput Row",
        "",
        "| target STV | max after T ledger | exact after T ledger | arbitrary rotations | max avg arbitrary T cost | total error budget needed at max cost proxy | fixed cost 20 meets target |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["gcm_h6_one_sided_after_target_cost_requirements"]:
        lines.append(
            f"| {row['target_stv_reduction']:.3f}x | {row['max_after_t_ledger']} | "
            f"{row['fixed_exact_after_t_ledger']} | {row['arbitrary_numeric_rotation_count']} | "
            f"{fmt(row['max_average_arbitrary_rotation_t_cost'])} | "
            f"{fmt(row['total_error_budget_needed_at_max_cost_proxy'])} | "
            f"{row['fixed_cost_20_meets_target']} |"
        )
    lines.extend(
        [
            "",
            "## Precision Budget Sweep",
            "",
            "| total error budget | per-rotation budget | implied arbitrary T cost | portfolio min STV | gcm_h6 min STV | min row |",
            "|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report["precision_budget_rows"]:
        lines.append(
            f"| {fmt(row['total_error_budget'])} | {fmt(row['per_rotation_error_budget'])} | "
            f"{row['arbitrary_rotation_t_cost']} | {row['min_space_time_volume_reduction']:.6f}x | "
            f"{row['gcm_h6_min_space_time_volume_reduction']:.6f}x | "
            f"{row['min_workload']} / {row['min_factory_variant']} |"
        )
    lines.extend(
        [
            "",
            "## Relaxed Fixed-Cost Rows",
            "",
            "| arbitrary T cost | portfolio min STV | gcm_h6 min STV | min row | after factory/data rows |",
            "|---:|---:|---:|---|---:|",
        ]
    )
    for row in report["relaxed_cost_rows"]:
        lines.append(
            f"| {row['arbitrary_rotation_t_cost']} | {row['min_space_time_volume_reduction']:.6f}x | "
            f"{row['gcm_h6_min_space_time_volume_reduction']:.6f}x | "
            f"{row['min_workload']} / {row['min_factory_variant']} | "
            f"{row['factory_bottleneck_after_count']} / {row['data_bottleneck_after_count']} |"
        )
    lines.extend(["", "## Numeric Rotation Reuse Probe", ""])
    if reuse.get("exists"):
        lines.extend(
            [
                f"- QASM path: `{reuse['qasm_path']}`",
                f"- Numeric parameter occurrences: {reuse['numeric_parameter_occurrences']}",
                f"- Unique numeric parameters: {reuse['unique_numeric_parameters']}",
                f"- Numeric instruction occurrences: {reuse['numeric_instruction_occurrences']}",
                f"- Unique numeric instructions: {reuse['unique_numeric_instructions']}",
                "",
                "| numeric parameter | count |",
                "|---|---:|",
            ]
        )
        for row in reuse["top_numeric_parameters"]:
            lines.append(f"| `{row['value']}` | {row['count']} |")
    else:
        lines.append(f"- QASM path missing: `{reuse['qasm_path']}`")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=Path("results/B7_ft_synthesis_ledger_v0.json"))
    parser.add_argument("--boundary", type=Path, default=Path("results/B7_gcm_h6_ft_boundary_v0.json"))
    parser.add_argument(
        "--gcm-qasm",
        type=Path,
        default=Path("results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_precision_aware_rotation_ledger_v0.json"))
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B7_precision_aware_rotation_ledger.md"),
    )
    parser.add_argument("--alpha", type=float, default=3.0)
    parser.add_argument("--beta", type=float, default=0.0)
    parser.add_argument("--target-reductions", type=float, nargs="+", default=[1.20, 1.25])
    parser.add_argument("--total-error-budgets", type=float, nargs="+", default=[1e-1, 1e-2, 1e-3, 1e-4, 1e-6])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run(args)
    write_json(args.json_output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    print(
        "status="
        f"{report['status']} portfolio_1_20={report['portfolio_precision_budgets_clear_1_20']} "
        f"gcm_h6_1_20={report['gcm_h6_precision_budgets_clear_1_20']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
