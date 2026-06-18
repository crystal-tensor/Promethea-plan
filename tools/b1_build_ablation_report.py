#!/usr/bin/env python3
"""Build an ablation report from B1 fixed-point pipeline work directories."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from b1_qasm_metrics import compute_metrics, find_qasm_files, load_profiles


SUBSETS = [
    {
        "name": "qasmbench_small",
        "work_dir": "results/qasmbench_small_fixed_point_pipeline_work",
        "summary": "results/qasmbench_small_fixed_point_pipeline/qasmbench_small_fixed_point_summary.json",
    },
    {
        "name": "qasmbench_medium_exact",
        "work_dir": "results/qasmbench_medium_exact_fixed_point_pipeline_work",
        "summary": "results/qasmbench_medium_exact_fixed_point_pipeline/qasmbench_medium_exact_fixed_point_summary.json",
    },
    {
        "name": "qasmbench_interaction_exact",
        "work_dir": "results/qasmbench_interaction_exact_fixed_point_pipeline_work",
        "summary": "results/qasmbench_interaction_exact_fixed_point_pipeline/qasmbench_interaction_exact_fixed_point_summary.json",
    },
    {
        "name": "b1_exact_extension",
        "work_dir": "results/b1_exact_extension_fixed_point_pipeline_work",
        "summary": "results/b1_exact_extension_fixed_point_pipeline/b1_exact_extension_fixed_point_summary.json",
    },
]

METRIC_KEYS = [
    "operation_count",
    "two_qubit_gate_count",
    "logical_depth",
    "hardware_weighted_error_exposure",
]

STAGE_LABELS = {
    "00_input": "baseline",
    "01_1q_commute": "after_1q_resynthesis",
    "02_rzz_pass": "after_adjacent_rzz",
    "final": "final",
}

RZZ_STAGE_RE = re.compile(r"^\d+_rzz_pass$")


def qasm_stage_dirs(work_dir: Path) -> dict[str, Path]:
    stages = {}
    for child in sorted(work_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name in {"00_input", "01_1q_commute", "02_rzz_pass", "final"}:
            stages[child.name] = child
        elif RZZ_STAGE_RE.match(child.name):
            stages[child.name] = child
    return stages


def totals_for_dir(path: Path, profile: dict) -> dict[str, float]:
    rows = [compute_metrics(file, profile) for file in find_qasm_files([path])]
    return {
        "circuit_count": len(rows),
        "max_qubits": max(int(row["qubits"]) for row in rows) if rows else 0,
        **{key: sum(float(row[key]) for row in rows) for key in METRIC_KEYS},
    }


def reduction_pct(before: float, after: float) -> float:
    return (before - after) / before * 100 if before else 0.0


def format_float(value: float) -> float:
    return round(float(value), 12)


def stage_sequence(stages: dict[str, Path]) -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    for key in ["00_input", "01_1q_commute", "02_rzz_pass"]:
        if key in stages:
            rows.append((STAGE_LABELS[key], stages[key]))
    extra_rzz = sorted(
        key for key in stages if RZZ_STAGE_RE.match(key) and key not in {"02_rzz_pass"}
    )
    for key in extra_rzz:
        rows.append((f"after_{key}", stages[key]))
    if "final" in stages:
        rows.append(("final", stages["final"]))
    return rows


def build_subset(root: Path, subset: dict, profile: dict) -> dict:
    work_dir = root / subset["work_dir"]
    stages = qasm_stage_dirs(work_dir)
    ordered = stage_sequence(stages)
    if not ordered or ordered[0][0] != "baseline":
        raise ValueError(f"{work_dir} has no baseline stage")

    stage_totals = []
    previous = None
    baseline = None
    for label, path in ordered:
        totals = totals_for_dir(path, profile)
        if baseline is None:
            baseline = totals
        row = {
            "stage": label,
            "path": str(path.relative_to(root)),
            **{key: format_float(value) for key, value in totals.items()},
        }
        if previous is None:
            row["incremental"] = {key: 0.0 for key in METRIC_KEYS}
        else:
            row["incremental"] = {
                key: format_float(previous[key] - totals[key])
                for key in METRIC_KEYS
            }
        row["reduction_from_baseline_pct"] = {
            key: format_float(reduction_pct(baseline[key], totals[key]))
            for key in METRIC_KEYS
        }
        stage_totals.append(row)
        previous = totals

    final = stage_totals[-1]
    return {
        "name": subset["name"],
        "work_dir": subset["work_dir"],
        "summary": subset["summary"],
        "circuit_count": int(final["circuit_count"]),
        "max_qubits": int(final["max_qubits"]),
        "stages": stage_totals,
        "final_reduction_pct": final["reduction_from_baseline_pct"],
    }


def aggregate_stage(subsets: list[dict], stage_name: str) -> dict:
    selected = []
    for subset in subsets:
        matches = [row for row in subset["stages"] if row["stage"] == stage_name]
        if matches:
            selected.append(matches[-1])
        else:
            selected.append(subset["stages"][-1])
    return {
        "stage": stage_name,
        "circuit_count": sum(int(row["circuit_count"]) for row in selected),
        "max_qubits": max(int(row["max_qubits"]) for row in selected),
        **{
            key: format_float(sum(float(row[key]) for row in selected))
            for key in METRIC_KEYS
        },
    }


def build_report(root: Path, profile_name: str) -> dict:
    profiles = load_profiles(root / "benchmarks" / "hardware_profiles.json")
    profile = profiles[profile_name]
    subsets = [build_subset(root, subset, profile) for subset in SUBSETS]
    stage_names = ["baseline", "after_1q_resynthesis", "after_adjacent_rzz", "final"]
    aggregate = []
    previous = None
    baseline = None
    for stage_name in stage_names:
        row = aggregate_stage(subsets, stage_name)
        if baseline is None:
            baseline = row
        if previous is None:
            row["incremental"] = {key: 0.0 for key in METRIC_KEYS}
        else:
            row["incremental"] = {
                key: format_float(float(previous[key]) - float(row[key]))
                for key in METRIC_KEYS
            }
        row["reduction_from_baseline_pct"] = {
            key: format_float(reduction_pct(float(baseline[key]), float(row[key])))
            for key in METRIC_KEYS
        }
        aggregate.append(row)
        previous = row

    final = aggregate[-1]
    total_reductions = {
        key: float(aggregate[0][key]) - float(final[key])
        for key in METRIC_KEYS
    }
    contribution_share = []
    for row in aggregate[1:]:
        contribution_share.append(
            {
                "stage": row["stage"],
                "share_of_total_reduction": {
                    key: format_float(float(row["incremental"][key]) / total_reductions[key] * 100)
                    if total_reductions[key]
                    else 0.0
                    for key in METRIC_KEYS
                },
            }
        )

    return {
        "benchmark_id": "B1",
        "report": "30_circuit_ablation_v0",
        "last_updated": "2026-06-13",
        "profile": profile_name,
        "circuit_count": int(final["circuit_count"]),
        "subsets": subsets,
        "aggregate": aggregate,
        "contribution_share": contribution_share,
        "interpretation": {
            "largest_hardware_exposure_contributor": max(
                contribution_share,
                key=lambda row: row["share_of_total_reduction"]["hardware_weighted_error_exposure"],
            )["stage"],
            "largest_depth_contributor": max(
                contribution_share,
                key=lambda row: row["share_of_total_reduction"]["logical_depth"],
            )["stage"],
            "limits": [
                "This is an ablation over the current fixed pass order, not a causal proof that passes are independent.",
                "The final stage includes all remaining RZZ passes after the adjacent pass.",
                "The suite includes generated exact-extension circuits and still needs more external benchmarks.",
            ],
        },
    }


def pct(value: float) -> str:
    return f"{float(value):.2f}%"


def markdown(report: dict) -> str:
    exposure = "hardware_weighted_error_exposure"
    lines = [
        "# B1 30-Circuit Ablation Report v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Profile: `{report['profile']}`",
        f"Circuits: {report['circuit_count']}",
        "",
        "## Aggregate Stage Table",
        "",
        "| Stage | Operation reduction | 2Q reduction | Depth reduction | Exposure reduction |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report["aggregate"]:
        reductions = row["reduction_from_baseline_pct"]
        lines.append(
            f"| {row['stage']} | {pct(reductions['operation_count'])} | "
            f"{pct(reductions['two_qubit_gate_count'])} | "
            f"{pct(reductions['logical_depth'])} | {pct(reductions[exposure])} |"
        )

    lines.extend(
        [
            "",
            "## Incremental Contribution Share",
            "",
            "| Stage | Operation share | 2Q share | Depth share | Exposure share |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["contribution_share"]:
        shares = row["share_of_total_reduction"]
        lines.append(
            f"| {row['stage']} | {pct(shares['operation_count'])} | "
            f"{pct(shares['two_qubit_gate_count'])} | "
            f"{pct(shares['logical_depth'])} | {pct(shares[exposure])} |"
        )

    lines.extend(
        [
            "",
            "## Subset Final Reductions",
            "",
            "| Subset | Circuits | Operation | 2Q | Depth | Exposure |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for subset in report["subsets"]:
        reductions = subset["final_reduction_pct"]
        lines.append(
            f"| {subset['name']} | {subset['circuit_count']} | "
            f"{pct(reductions['operation_count'])} | "
            f"{pct(reductions['two_qubit_gate_count'])} | "
            f"{pct(reductions['logical_depth'])} | {pct(reductions[exposure])} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Largest hardware-exposure contributor: `{report['interpretation']['largest_hardware_exposure_contributor']}`.",
            f"- Largest depth contributor: `{report['interpretation']['largest_depth_contributor']}`.",
        ]
    )
    lines.extend(f"- Limit: {item}" for item in report["interpretation"]["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_ablation_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_ablation_report.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    report = build_report(root, args.profile)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
