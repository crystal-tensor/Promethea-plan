#!/usr/bin/env python3
"""Analyze the B7 FT-ledger minimum-STV boundary after T-B7-002."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


FAMILY_COSTS = {
    "clifford_rotation": 0,
    "exact_pi_over_4_rotation": 1,
    "exact_pi_over_8_rotation": 4,
    "direct_t_gate": 1,
    "ccx_decomposition": 7,
    "unknown_or_symbolic_rotation": 20,
}


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


def sweep_costs(ledger: dict, min_cost: int, max_cost: int) -> list[dict]:
    rows = []
    for cost in range(min_cost, max_cost + 1):
        comparisons = [recompute_comparison(row, cost) for row in ledger["comparisons"]]
        reductions = [row["space_time_volume_reduction"] for row in comparisons if row["space_time_volume_reduction"]]
        min_row = min(comparisons, key=lambda row: row["space_time_volume_reduction"])
        rows.append(
            {
                "arbitrary_rotation_t_cost": cost,
                "min_space_time_volume_reduction": min(reductions),
                "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
                "min_workload": min_row["workload"],
                "min_factory_variant": min_row["factory_variant"],
                "min_bottleneck_before": min_row["bottleneck_before"],
                "min_bottleneck_after": min_row["bottleneck_after"],
                "factory_bottleneck_after_count": sum(
                    1 for row in comparisons if row["bottleneck_after"] == "factory_path"
                ),
                "data_bottleneck_after_count": sum(1 for row in comparisons if row["bottleneck_after"] == "data_path"),
            }
        )
    return rows


def target_requirement(row: dict, target_reduction: float) -> dict:
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
    current_t = int(after["logical_t_count_ledger"])
    additional_t_to_remove = current_t - max_t_count if max_t_count >= 0 else None
    arbitrary_count = int(after["rotation_family_counts"].get("arbitrary_numeric_rotation", 0))
    arbitrary_cost = 20
    return {
        "target_stv_reduction": target_reduction,
        "max_critical_rounds": max_critical_rounds,
        "max_factory_rounds": max_factory_rounds,
        "max_after_t_ledger": max_t_count,
        "current_after_t_ledger": current_t,
        "additional_t_ledger_to_remove": additional_t_to_remove,
        "equivalent_arbitrary_rotations_to_remove_at_cost_20": math.ceil(additional_t_to_remove / arbitrary_cost)
        if additional_t_to_remove is not None
        else None,
        "current_after_arbitrary_numeric_rotation_count": arbitrary_count,
        "requires_data_path_reduction": max_t_count < 0,
    }


def threshold_for_target(sweep_rows: list[dict], target: float) -> dict:
    passing = [row for row in sweep_rows if row["min_space_time_volume_reduction"] >= target]
    if not passing:
        return {
            "target_stv_reduction": target,
            "max_arbitrary_rotation_t_cost_meeting_target": None,
            "passing_cost_count": 0,
        }
    best = max(passing, key=lambda row: row["arbitrary_rotation_t_cost"])
    return {
        "target_stv_reduction": target,
        "max_arbitrary_rotation_t_cost_meeting_target": best["arbitrary_rotation_t_cost"],
        "min_space_time_volume_reduction_at_threshold": best["min_space_time_volume_reduction"],
        "min_workload_at_threshold": best["min_workload"],
        "min_factory_variant_at_threshold": best["min_factory_variant"],
        "passing_cost_count": len(passing),
    }


def run(args: argparse.Namespace) -> dict:
    ledger = read_json(args.ledger)
    current_min = min(ledger["comparisons"], key=lambda row: row["space_time_volume_reduction"])
    current_requirements = [target_requirement(current_min, target) for target in args.target_reductions]
    sweep_rows = sweep_costs(ledger, args.min_arbitrary_cost, args.max_arbitrary_cost)
    thresholds = [threshold_for_target(sweep_rows, target) for target in args.target_reductions]
    gcm_resource = next(
        row for row in ledger["resource_rows"] if row["workload"] == "qasmbench_medium_exact/gcm_h6.qasm"
    )
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 gcm_h6 FT-ledger boundary analysis",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": "gcm_h6_ft_boundary_quantified_not_physical_layout",
        "method": "b7_gcm_h6_ft_boundary_v0",
        "source_ledger": str(args.ledger),
        "current_min_workload": current_min["workload"],
        "current_min_factory_variant": current_min["factory_variant"],
        "current_min_space_time_volume_reduction": current_min["space_time_volume_reduction"],
        "current_min_bottleneck_after": current_min["bottleneck_after"],
        "gcm_h6_after_arbitrary_numeric_rotation_count": gcm_resource["after_rotation_family_counts"].get(
            "arbitrary_numeric_rotation", 0
        ),
        "gcm_h6_after_arbitrary_numeric_t_cost": gcm_resource["after_t_cost_by_family"].get(
            "arbitrary_numeric_rotation", 0
        ),
        "gcm_h6_after_total_t_ledger": gcm_resource["after_logical_t_count_ledger"],
        "target_requirements_for_current_min": current_requirements,
        "arbitrary_rotation_cost_sweep": sweep_rows,
        "portfolio_thresholds": thresholds,
        "interpretation": (
            "The FT ledger moved sat_n11 out of the parallel-factory minimum row; gcm_h6 is now limited by "
            "arbitrary numeric rotations. Under the current footprint, the gcm_h6 throughput row needs a "
            "large reduction in after-ledger T pressure or a lower arbitrary-rotation synthesis cost to push "
            "portfolio min STV beyond 1.20x."
        ),
        "next_actions": [
            "Implement a gcm_h6-targeted arbitrary-rotation synthesis ledger with precision/error budgeting.",
            "Try a semantic-preserving numeric rotation merge/cancellation pass for adjacent or commute-safe rotations.",
            "If no local pass can reduce the 270 arbitrary numeric rotations, record a negative boundary for local phase passes.",
        ],
        "limits": [
            "This analysis sweeps synthesis costs inside the existing B7 ledger; it is not a physical layout result.",
            "Lower arbitrary-rotation costs must later be justified by a precision-aware FT synthesis method.",
            "Removing arbitrary rotations here means equivalent T-ledger reduction, not necessarily deleting QASM gates.",
        ],
    }


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6g}"


def markdown(report: dict) -> str:
    lines = [
        "# B7 gcm_h6 FT-Ledger Boundary v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source ledger: `{report['source_ledger']}`",
        f"- Current min workload: `{report['current_min_workload']}`",
        f"- Current min factory variant: `{report['current_min_factory_variant']}`",
        f"- Current min STV reduction: {report['current_min_space_time_volume_reduction']:.6f}x",
        f"- Current min bottleneck after: {report['current_min_bottleneck_after']}",
        f"- gcm_h6 after arbitrary numeric rotations: {report['gcm_h6_after_arbitrary_numeric_rotation_count']}",
        f"- gcm_h6 arbitrary numeric T cost: {report['gcm_h6_after_arbitrary_numeric_t_cost']}",
        f"- gcm_h6 after total T ledger: {report['gcm_h6_after_total_t_ledger']}",
        f"- Interpretation: {report['interpretation']}",
        "",
        "## Target Requirements For Current Min Row",
        "",
        "| target STV | max after T ledger | additional T ledger to remove | equivalent arbitrary rotations at cost 20 | needs data path reduction |",
        "|---:|---:|---:|---:|---|",
    ]
    for row in report["target_requirements_for_current_min"]:
        lines.append(
            f"| {row['target_stv_reduction']:.3f}x | {row['max_after_t_ledger']} | "
            f"{fmt(row['additional_t_ledger_to_remove'])} | "
            f"{fmt(row['equivalent_arbitrary_rotations_to_remove_at_cost_20'])} | "
            f"{row['requires_data_path_reduction']} |"
        )
    lines.extend(
        [
            "",
            "## Portfolio Arbitrary-Rotation Cost Sweep",
            "",
            "| arbitrary T cost | min STV | mean STV | min workload | min variant | after factory/data rows |",
            "|---:|---:|---:|---|---|---:|",
        ]
    )
    for row in report["arbitrary_rotation_cost_sweep"]:
        lines.append(
            f"| {row['arbitrary_rotation_t_cost']} | {row['min_space_time_volume_reduction']:.6f}x | "
            f"{row['mean_space_time_volume_reduction']:.6f}x | {row['min_workload']} | "
            f"{row['min_factory_variant']} | {row['factory_bottleneck_after_count']} / {row['data_bottleneck_after_count']} |"
        )
    lines.extend(["", "## Portfolio Thresholds", ""])
    for row in report["portfolio_thresholds"]:
        lines.append(
            f"- Target {row['target_stv_reduction']:.3f}x: max arbitrary-rotation T cost "
            f"{row['max_arbitrary_rotation_t_cost_meeting_target']} "
            f"(min row `{row.get('min_workload_at_threshold', 'n/a')}` / `{row.get('min_factory_variant_at_threshold', 'n/a')}`)"
        )
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path("results/B7_ft_synthesis_ledger_v0.json"))
    parser.add_argument("--target-reductions", type=float, nargs="+", default=[1.20, 1.25])
    parser.add_argument("--min-arbitrary-cost", type=int, default=0)
    parser.add_argument("--max-arbitrary-cost", type=int, default=20)
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_gcm_h6_ft_boundary_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B7_gcm_h6_ft_boundary.md"))
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
                    "current_min_workload": report["current_min_workload"],
                    "current_min_space_time_volume_reduction": report[
                        "current_min_space_time_volume_reduction"
                    ],
                    "portfolio_thresholds": report["portfolio_thresholds"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
