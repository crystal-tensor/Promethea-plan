#!/usr/bin/env python3
"""Classify the remaining B7 minimum-STV regime after B1 T-resource passes."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


DEFAULT_STAGE_PATHS = [
    ("virtual_swap", Path("results/B7_logical_t_factory_schedule_v0.json")),
    ("post_1q", Path("results/B7_logical_t_factory_schedule_post_1q_v0.json")),
    ("native_z", Path("results/B7_logical_t_factory_schedule_native_v0.json")),
    ("control_rz", Path("results/B7_logical_t_factory_schedule_control_rz_v0.json")),
    ("u3_phase_factored", Path("results/B7_logical_t_factory_schedule_u3_phase_factored_v0.json")),
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_div(a: float, b: float) -> float | None:
    return a / b if b else None


def required_t_for_target(row: dict, target_reduction: float) -> dict:
    before = row["before"]
    after = row["after"]
    factory_count = int(after["factory_count"])
    factory_cycle_rounds = int(after["factory_cycle_rounds"])
    after_t = int(after["logical_t_count_proxy"])
    before_stv = float(before["space_time_volume"])
    after_total_physical = int(after["total_physical_qubits"])
    data_rounds = int(after["data_rounds"])
    factory_rounds = int(after["factory_rounds"])
    fixed_tail_rounds = int(after["critical_path_rounds"]) - max(data_rounds, factory_rounds)
    target_after_stv = before_stv / target_reduction
    max_critical_rounds = math.floor(target_after_stv / after_total_physical)
    max_factory_rounds = max_critical_rounds - fixed_tail_rounds
    max_factory_rounds = max(0, max_factory_rounds)
    if max_factory_rounds < data_rounds:
        # The requested target would also require shrinking the data path.
        max_t_count = -1
    else:
        max_batches = max_factory_rounds // factory_cycle_rounds
        max_t_count = max_batches * factory_count
    additional_t_to_remove = after_t - max_t_count if max_t_count >= 0 else None
    return {
        "target_stv_reduction": target_reduction,
        "max_critical_rounds": max_critical_rounds,
        "fixed_tail_rounds": fixed_tail_rounds,
        "max_factory_rounds": max_factory_rounds,
        "max_logical_t_count_proxy": max_t_count,
        "additional_t_count_proxy_to_remove": additional_t_to_remove,
        "requires_data_path_reduction": max_t_count < 0,
    }


def classify_row(row: dict, target_reductions: list[float]) -> dict:
    before = row["before"]
    after = row["after"]
    before_factory = int(before["factory_rounds"])
    after_factory = int(after["factory_rounds"])
    before_data = int(before["data_rounds"])
    after_data = int(after["data_rounds"])
    before_t = int(before["logical_t_count_proxy"])
    after_t = int(after["logical_t_count_proxy"])
    factory_count = int(after["factory_count"])
    after_tail_rounds = int(after["critical_path_rounds"]) - max(after_data, after_factory)
    after_batches = math.ceil(after_t / factory_count) if factory_count else 0
    previous_batch_threshold = (after_batches - 1) * factory_count if after_batches else 0
    t_to_drop_one_batch = max(0, after_t - previous_batch_threshold + (1 if after_t == previous_batch_threshold else 0))
    factory_to_data_ratio_after = safe_div(after_factory, after_data)
    if row["bottleneck_after"] == "factory_path" and (factory_to_data_ratio_after or 0) > 10:
        regime = "factory_locked_deep"
    elif row["bottleneck_after"] == "factory_path":
        regime = "factory_locked_near_data_path"
    elif row["bottleneck_after"] == "data_path":
        regime = "data_path_limited"
    else:
        regime = "mixed_or_unknown"
    return {
        "workload": row["workload"],
        "factory_variant": row["factory_variant"],
        "regime": regime,
        "bottleneck_before": row["bottleneck_before"],
        "bottleneck_after": row["bottleneck_after"],
        "space_time_volume_reduction": row["space_time_volume_reduction"],
        "logical_t_count_reduction": row["logical_t_count_reduction"],
        "logical_t_depth_reduction": row["logical_t_depth_reduction"],
        "before_logical_t_count_proxy": before_t,
        "after_logical_t_count_proxy": after_t,
        "before_factory_rounds": before_factory,
        "after_factory_rounds": after_factory,
        "before_data_rounds": before_data,
        "after_data_rounds": after_data,
        "after_factory_to_data_round_ratio": factory_to_data_ratio_after,
        "after_factory_count": factory_count,
        "after_factory_cycle_rounds": int(after["factory_cycle_rounds"]),
        "after_tail_rounds": after_tail_rounds,
        "after_factory_batches": after_batches,
        "t_count_proxy_to_drop_one_factory_batch": t_to_drop_one_batch,
        "target_requirements": [required_t_for_target(row, target) for target in target_reductions],
    }


def workload_summaries(classified_rows: list[dict]) -> list[dict]:
    by_workload: dict[str, list[dict]] = defaultdict(list)
    for row in classified_rows:
        by_workload[row["workload"]].append(row)
    summaries = []
    for workload, rows in sorted(by_workload.items()):
        reductions = [row["space_time_volume_reduction"] for row in rows]
        summaries.append(
            {
                "workload": workload,
                "variant_count": len(rows),
                "min_space_time_volume_reduction": min(reductions),
                "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
                "dominant_regimes": sorted(set(row["regime"] for row in rows)),
                "all_factory_bottleneck": all(row["bottleneck_after"] == "factory_path" for row in rows),
                "min_variant": min(rows, key=lambda row: row["space_time_volume_reduction"])["factory_variant"],
                "min_after_logical_t_count_proxy": min(rows, key=lambda row: row["space_time_volume_reduction"])[
                    "after_logical_t_count_proxy"
                ],
            }
        )
    summaries.sort(key=lambda row: row["min_space_time_volume_reduction"])
    return summaries


def stage_progression(stage_paths: list[tuple[str, Path]], min_workload: str) -> list[dict]:
    progression = []
    for stage, path in stage_paths:
        if not path.exists():
            continue
        payload = read_json(path)
        rows = [row for row in payload.get("comparisons", []) if row["workload"] == min_workload]
        if not rows:
            continue
        reductions = [row["space_time_volume_reduction"] for row in rows if row["space_time_volume_reduction"]]
        t_reductions = [row["logical_t_count_reduction"] for row in rows if row["logical_t_count_reduction"]]
        progression.append(
            {
                "stage": stage,
                "path": str(path),
                "min_space_time_volume_reduction": min(reductions),
                "mean_space_time_volume_reduction": sum(reductions) / len(reductions),
                "min_logical_t_count_reduction": min(t_reductions),
                "mean_logical_t_count_reduction": sum(t_reductions) / len(t_reductions),
            }
        )
    return progression


def run(args: argparse.Namespace) -> dict:
    schedule = read_json(args.schedule)
    target_reductions = [float(value) for value in args.target_reductions.split(",")]
    classified = [classify_row(row, target_reductions) for row in schedule["comparisons"]]
    classified.sort(key=lambda row: (row["space_time_volume_reduction"], row["workload"], row["factory_variant"]))
    min_rows = [
        row
        for row in classified
        if abs(row["space_time_volume_reduction"] - classified[0]["space_time_volume_reduction"]) <= 1e-12
    ]
    workload_rows = workload_summaries(classified)
    min_workload = workload_rows[0]["workload"]
    stage_paths = DEFAULT_STAGE_PATHS
    stage_rows = stage_progression(stage_paths, min_workload)
    all_factory = sum(1 for row in classified if row["bottleneck_after"] == "factory_path")
    deep_factory = sum(1 for row in classified if row["regime"] == "factory_locked_deep")
    return {
        "benchmark_id": "B7",
        "problem_id": 21,
        "title": "B7 minimum-STV regime classifier",
        "version": "0.1",
        "last_updated": "2026-06-15",
        "status": "min_stv_regime_classified_not_physical_layout_claim",
        "method": "b7_min_stv_regime_classifier_v0",
        "source_schedule": str(args.schedule),
        "comparison_count": len(classified),
        "workload_count": len(workload_rows),
        "target_reductions": target_reductions,
        "min_space_time_volume_reduction": classified[0]["space_time_volume_reduction"],
        "min_workload": min_workload,
        "min_rows": min_rows,
        "workload_summaries": workload_rows,
        "stage_progression_for_min_workload": stage_rows,
        "factory_bottleneck_after_count": all_factory,
        "deep_factory_locked_count": deep_factory,
        "interpretation": (
            "The remaining minimum-STV row is factory-path dominated; U3 phase factoring improved portfolio mean STV "
            "but did not move the sat_n11 minimum row beyond the control-RZ boundary."
        ),
        "next_actions": [
            "Attack sat_n11 logical T-count directly or prove it is a negative boundary for the current local phase passes.",
            "Replace fixed-cost rotation proxy with a fault-tolerant synthesis ledger to test whether pi/4, arbitrary, and unknown rotations have different factory pressure.",
            "Add physical layout and feed-forward assumptions before promoting any B7 result beyond proxy status.",
        ],
        "limits": [
            "This classifier consumes B7 logical T-factory schedule rows; it is not a physical layout or lattice-surgery result.",
            "The target-removal calculation assumes the same factory variant and total physical qubit footprint.",
            "Logical T-count proxy uses the scheduler fixed rotation cost and should not be treated as a calibrated synthesis cost.",
        ],
    }


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6g}"


def markdown(report: dict) -> str:
    lines = [
        "# B7 Minimum-STV Regime Classifier v0.1",
        "",
        "Last updated: 2026-06-15",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source schedule: `{report['source_schedule']}`",
        f"- Comparisons: {report['comparison_count']}",
        f"- Workloads: {report['workload_count']}",
        f"- Minimum STV reduction: {report['min_space_time_volume_reduction']:.6f}x",
        f"- Minimum workload: `{report['min_workload']}`",
        f"- Factory-bottleneck after rows: {report['factory_bottleneck_after_count']}",
        f"- Deep factory-locked rows: {report['deep_factory_locked_count']}",
        f"- Interpretation: {report['interpretation']}",
        "",
        "## Minimum Rows",
        "",
        "| workload | variant | regime | STV reduction | T reduction | after T | after factory/data rounds | T to drop one batch |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["min_rows"]:
        lines.append(
            f"| {row['workload']} | {row['factory_variant']} | {row['regime']} | "
            f"{row['space_time_volume_reduction']:.6f}x | {row['logical_t_count_reduction']:.6f}x | "
            f"{row['after_logical_t_count_proxy']} | "
            f"{row['after_factory_rounds']} / {row['after_data_rounds']} | "
            f"{row['t_count_proxy_to_drop_one_factory_batch']} |"
        )
    lines.extend(
        [
            "",
            "## Target Removal Requirements",
            "",
            "| workload | variant | target STV | max after T proxy | additional T proxy to remove | needs data path reduction |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in report["min_rows"]:
        for target in row["target_requirements"]:
            lines.append(
                f"| {row['workload']} | {row['factory_variant']} | {target['target_stv_reduction']:.3f}x | "
                f"{target['max_logical_t_count_proxy']} | {fmt(target['additional_t_count_proxy_to_remove'])} | "
                f"{target['requires_data_path_reduction']} |"
            )
    lines.extend(
        [
            "",
            "## Workload Ranking",
            "",
            "| workload | min STV | mean STV | min variant | regimes | all factory bottleneck |",
            "|---|---:|---:|---|---|---|",
        ]
    )
    for row in report["workload_summaries"]:
        lines.append(
            f"| {row['workload']} | {row['min_space_time_volume_reduction']:.6f}x | "
            f"{row['mean_space_time_volume_reduction']:.6f}x | {row['min_variant']} | "
            f"{', '.join(row['dominant_regimes'])} | {row['all_factory_bottleneck']} |"
        )
    lines.extend(
        [
            "",
            "## Stage Progression For Minimum Workload",
            "",
            "| stage | min STV | mean STV | min T-count reduction | mean T-count reduction |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["stage_progression_for_min_workload"]:
        lines.append(
            f"| {row['stage']} | {row['min_space_time_volume_reduction']:.6f}x | "
            f"{row['mean_space_time_volume_reduction']:.6f}x | "
            f"{row['min_logical_t_count_reduction']:.6f}x | {row['mean_logical_t_count_reduction']:.6f}x |"
        )
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, default=Path("results/B7_logical_t_factory_schedule_u3_phase_factored_v0.json"))
    parser.add_argument("--target-reductions", default="1.20,1.25")
    parser.add_argument("--json-output", type=Path, default=Path("results/B7_min_stv_regime_classifier_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B7_min_stv_regime_classifier.md"))
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
                    "min_workload": report["min_workload"],
                    "min_space_time_volume_reduction": report["min_space_time_volume_reduction"],
                    "factory_bottleneck_after_count": report["factory_bottleneck_after_count"],
                    "deep_factory_locked_count": report["deep_factory_locked_count"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
