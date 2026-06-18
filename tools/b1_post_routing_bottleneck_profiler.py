#!/usr/bin/env python3
"""Profile per-circuit bottlenecks after heavy-hex routing for B1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_LEVELS = {
    "0": {
        "source": Path("results/b1_heavyhex_end_to_end_30/source_routed_metrics.json"),
        "optimized": Path("results/b1_heavyhex_end_to_end_30/b1_optimized_routed_metrics.json"),
        "summary": Path("results/b1_heavyhex_end_to_end_30/heavyhex_end_to_end_summary.json"),
    },
    "1": {
        "source": Path("results/b1_heavyhex_end_to_end_30_level1/source_routed_metrics.json"),
        "optimized": Path("results/b1_heavyhex_end_to_end_30_level1/b1_optimized_routed_metrics.json"),
        "summary": Path("results/b1_heavyhex_end_to_end_30_level1/heavyhex_end_to_end_summary.json"),
    },
}

METRICS = [
    "operation_count",
    "two_qubit_gate_count",
    "logical_depth",
    "hardware_weighted_error_exposure",
    "idle_layer_proxy",
]

METRIC_LABELS = {
    "operation_count": "Operations",
    "two_qubit_gate_count": "2Q gates",
    "logical_depth": "Depth",
    "hardware_weighted_error_exposure": "Exposure",
    "idle_layer_proxy": "Idle proxy",
}

LEVEL_ERASURE_EPSILON = 0.01


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def percent(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return 100.0 * numerator / denominator


def fmt_pct(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}%"


def fmt_num(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:.6g}"
    return str(int(value))


def circuit_key(path_text: str) -> str:
    parts = Path(path_text).parts
    for marker in [
        "02_source_heavyhex_d3_level0",
        "03_b1_heavyhex_d3_level0",
        "02_source_heavyhex_d3_level1",
        "03_b1_heavyhex_d3_level1",
    ]:
        if marker in parts:
            index = parts.index(marker)
            return str(Path(*parts[index + 1 :]))
    for subset in [
        "b1_exact_extension",
        "qasmbench_interaction_exact",
        "qasmbench_medium_exact",
        "qasmbench_small",
    ]:
        if subset in parts:
            index = parts.index(subset)
            return str(Path(*parts[index:]))
    return Path(path_text).name


def indexed_results(metrics_path: Path) -> dict[str, dict]:
    payload = read_json(metrics_path)
    rows = payload.get("results", [])
    indexed: dict[str, dict] = {}
    for row in rows:
        key = circuit_key(row["path"])
        if key in indexed:
            raise ValueError(f"duplicate circuit key {key!r} in {metrics_path}")
        indexed[key] = row
    return indexed


def compare_level(level: str, source_path: Path, optimized_path: Path, summary_path: Path) -> dict:
    source = indexed_results(source_path)
    optimized = indexed_results(optimized_path)
    source_keys = set(source)
    optimized_keys = set(optimized)
    if source_keys != optimized_keys:
        raise ValueError(
            f"level {level} source/optimized key mismatch: "
            f"source_only={sorted(source_keys - optimized_keys)}, "
            f"optimized_only={sorted(optimized_keys - source_keys)}"
        )

    rows = []
    totals = {
        metric: {"source": 0.0, "optimized": 0.0, "delta": 0.0, "reduction_pct": 0.0}
        for metric in METRICS
    }
    for key in sorted(source):
        src = source[key]
        opt = optimized[key]
        deltas = {}
        for metric in METRICS:
            source_value = float(src.get(metric, 0.0))
            optimized_value = float(opt.get(metric, 0.0))
            improvement = source_value - optimized_value
            deltas[metric] = {
                "source": source_value,
                "optimized": optimized_value,
                "delta": optimized_value - source_value,
                "improvement": improvement,
                "reduction_pct": percent(improvement, source_value),
            }
            totals[metric]["source"] += source_value
            totals[metric]["optimized"] += optimized_value
        rows.append(
            {
                "circuit": key,
                "source_path": src["path"],
                "optimized_path": opt["path"],
                "qubits": max(int(src.get("qubits", 0)), int(opt.get("qubits", 0))),
                "classical_bits": max(int(src.get("classical_bits", 0)), int(opt.get("classical_bits", 0))),
                "metrics": deltas,
            }
        )

    for metric in METRICS:
        totals[metric]["delta"] = totals[metric]["optimized"] - totals[metric]["source"]
        totals[metric]["improvement"] = totals[metric]["source"] - totals[metric]["optimized"]
        totals[metric]["reduction_pct"] = percent(totals[metric]["improvement"], totals[metric]["source"])

    summary = read_json(summary_path)
    return {
        "optimization_level": int(level),
        "source_metrics_path": str(source_path),
        "optimized_metrics_path": str(optimized_path),
        "summary_path": str(summary_path),
        "circuit_count": len(rows),
        "aer_crosscheck_passed": summary.get("aer_crosscheck_passed"),
        "aer_crosscheck_failed": summary.get("aer_crosscheck_failed"),
        "aer_crosscheck_max_tvd": summary.get("aer_crosscheck_max_tvd"),
        "totals": totals,
        "circuits": rows,
    }


def row_metric(row: dict, metric: str, field: str) -> float:
    return float(row["metrics"][metric][field])


def top_positive(rows: list[dict], metric: str, limit: int) -> list[dict]:
    ranked = [row for row in rows if row_metric(row, metric, "improvement") > 0]
    ranked.sort(key=lambda row: row_metric(row, metric, "improvement"), reverse=True)
    return summarize_rows(ranked[:limit], metric)


def top_regressions(rows: list[dict], metric: str, limit: int) -> list[dict]:
    ranked = [row for row in rows if row_metric(row, metric, "delta") > 0]
    ranked.sort(key=lambda row: row_metric(row, metric, "delta"), reverse=True)
    return summarize_rows(ranked[:limit], metric)


def summarize_rows(rows: list[dict], metric: str) -> list[dict]:
    return [
        {
            "circuit": row["circuit"],
            "source": row_metric(row, metric, "source"),
            "optimized": row_metric(row, metric, "optimized"),
            "improvement": row_metric(row, metric, "improvement"),
            "delta": row_metric(row, metric, "delta"),
            "reduction_pct": row_metric(row, metric, "reduction_pct"),
            "qubits": row["qubits"],
        }
        for row in rows
    ]


def build_bottlenecks(levels: dict[str, dict], limit: int) -> dict:
    level0 = levels["0"]["circuits"]
    level1 = levels["1"]["circuits"]
    by0 = {row["circuit"]: row for row in level0}
    by1 = {row["circuit"]: row for row in level1}
    common = sorted(set(by0) & set(by1))

    erased = []
    for key in common:
        row0 = by0[key]
        row1 = by1[key]
        exposure0 = row_metric(row0, "hardware_weighted_error_exposure", "reduction_pct")
        exposure1 = row_metric(row1, "hardware_weighted_error_exposure", "reduction_pct")
        depth0 = row_metric(row0, "logical_depth", "reduction_pct")
        depth1 = row_metric(row1, "logical_depth", "reduction_pct")
        if (exposure0 > LEVEL_ERASURE_EPSILON and exposure1 <= LEVEL_ERASURE_EPSILON) or (
            depth0 > LEVEL_ERASURE_EPSILON and depth1 <= LEVEL_ERASURE_EPSILON
        ):
            erased.append(
                {
                    "circuit": key,
                    "level0_exposure_reduction_pct": exposure0,
                    "level1_exposure_reduction_pct": exposure1,
                    "level0_depth_reduction_pct": depth0,
                    "level1_depth_reduction_pct": depth1,
                    "level1_2q_delta": row_metric(row1, "two_qubit_gate_count", "delta"),
                    "level1_operation_delta": row_metric(row1, "operation_count", "delta"),
                }
            )
    erased.sort(
        key=lambda row: (
            row["level0_exposure_reduction_pct"] - row["level1_exposure_reduction_pct"],
            row["level0_depth_reduction_pct"] - row["level1_depth_reduction_pct"],
        ),
        reverse=True,
    )

    level1_2q = []
    for row in level1:
        level1_2q.append(
            {
                "circuit": row["circuit"],
                "optimized_2q_count": row_metric(row, "two_qubit_gate_count", "optimized"),
                "source_2q_count": row_metric(row, "two_qubit_gate_count", "source"),
                "delta": row_metric(row, "two_qubit_gate_count", "delta"),
                "reduction_pct": row_metric(row, "two_qubit_gate_count", "reduction_pct"),
                "optimized_exposure": row_metric(row, "hardware_weighted_error_exposure", "optimized"),
            }
        )
    level1_2q.sort(key=lambda row: (row["optimized_2q_count"], row["optimized_exposure"]), reverse=True)

    return {
        "level0_top_exposure_contributors": top_positive(
            level0, "hardware_weighted_error_exposure", limit
        ),
        "level0_top_depth_contributors": top_positive(level0, "logical_depth", limit),
        "level0_top_operation_contributors": top_positive(level0, "operation_count", limit),
        "level1_top_exposure_contributors": top_positive(
            level1, "hardware_weighted_error_exposure", limit
        ),
        "level1_exposure_regressions": top_regressions(
            level1, "hardware_weighted_error_exposure", limit
        ),
        "level1_depth_regressions": top_regressions(level1, "logical_depth", limit),
        "benefit_erased_by_level1": erased[:limit],
        "level1_two_qubit_bottlenecks": level1_2q[:limit],
        "erased_circuit_count": len(erased),
    }


def build_report(root: Path, limit: int) -> dict:
    levels = {}
    for level, paths in DEFAULT_LEVELS.items():
        levels[level] = compare_level(
            level,
            (root / paths["source"]).resolve(),
            (root / paths["optimized"]).resolve(),
            (root / paths["summary"]).resolve(),
        )
    bottlenecks = build_bottlenecks(levels, limit)
    totals0 = levels["0"]["totals"]
    totals1 = levels["1"]["totals"]
    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 post-routing bottleneck profile",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "post_routing_bottleneck_profile_diagnostic_not_calibrated_noise_claim",
        "levels_tested": [0, 1],
        "circuit_count": levels["0"]["circuit_count"],
        "all_aer_crosschecks_passed": all(
            level["aer_crosscheck_failed"] == 0 for level in levels.values()
        ),
        "level_summary": {
            "0": {
                "operation_count_reduction_pct": totals0["operation_count"]["reduction_pct"],
                "two_qubit_gate_count_reduction_pct": totals0["two_qubit_gate_count"][
                    "reduction_pct"
                ],
                "logical_depth_reduction_pct": totals0["logical_depth"]["reduction_pct"],
                "hardware_weighted_exposure_reduction_pct": totals0[
                    "hardware_weighted_error_exposure"
                ]["reduction_pct"],
                "idle_layer_proxy_reduction_pct": totals0["idle_layer_proxy"]["reduction_pct"],
            },
            "1": {
                "operation_count_reduction_pct": totals1["operation_count"]["reduction_pct"],
                "two_qubit_gate_count_reduction_pct": totals1["two_qubit_gate_count"][
                    "reduction_pct"
                ],
                "logical_depth_reduction_pct": totals1["logical_depth"]["reduction_pct"],
                "hardware_weighted_exposure_reduction_pct": totals1[
                    "hardware_weighted_error_exposure"
                ]["reduction_pct"],
                "idle_layer_proxy_reduction_pct": totals1["idle_layer_proxy"]["reduction_pct"],
            },
        },
        "levels": levels,
        "bottlenecks": bottlenecks,
        "interpretation": [
            "Level 0 preserves B1 operation, depth, idle-layer, and small exposure benefits after heavy-hex routing.",
            "Level 1 nearly erases the current routed benefit, so the present B1 rewrites are not robust to stronger routing optimization.",
            "Post-routing two-qubit count remains the dominant unsolved bottleneck; the next optimizer should operate on routing-aware 2-4 qubit windows rather than isolated 1Q cleanup.",
        ],
    }


def table(rows: list[dict], metric: str) -> list[str]:
    lines = ["| Circuit | Source | Optimized | Improvement | Reduction |", "|---|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| `{row['circuit']}` | {fmt_num(row['source'])} | {fmt_num(row['optimized'])} | "
            f"{fmt_num(row['improvement'])} | {fmt_pct(row['reduction_pct'])} |"
        )
    if len(lines) == 2:
        lines.append("| n/a | n/a | n/a | n/a | n/a |")
    return lines


def markdown(report: dict) -> str:
    lines = [
        "# B1 Post-Routing Bottleneck Profile v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Level Summary",
        "",
        "| Qiskit level | Aer all pass | Operation | 2Q gates | Depth | Exposure | Idle proxy |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for level in ["0", "1"]:
        summary = report["level_summary"][level]
        level_payload = report["levels"][level]
        lines.append(
            f"| {level} | {level_payload['aer_crosscheck_failed'] == 0} | "
            f"{fmt_pct(summary['operation_count_reduction_pct'])} | "
            f"{fmt_pct(summary['two_qubit_gate_count_reduction_pct'])} | "
            f"{fmt_pct(summary['logical_depth_reduction_pct'])} | "
            f"{fmt_pct(summary['hardware_weighted_exposure_reduction_pct'])} | "
            f"{fmt_pct(summary['idle_layer_proxy_reduction_pct'])} |"
        )

    bottlenecks = report["bottlenecks"]
    sections = [
        ("## Level 0 Exposure Contributors", "level0_top_exposure_contributors", "hardware_weighted_error_exposure"),
        ("## Level 0 Depth Contributors", "level0_top_depth_contributors", "logical_depth"),
        ("## Level 1 Exposure Contributors", "level1_top_exposure_contributors", "hardware_weighted_error_exposure"),
        ("## Level 1 Exposure Regressions", "level1_exposure_regressions", "hardware_weighted_error_exposure"),
    ]
    for heading, key, metric in sections:
        lines.extend(["", heading, ""])
        lines.extend(table(bottlenecks[key], metric))

    lines.extend(
        [
            "",
            "## Level 1 Benefit Erasure",
            "",
            "| Circuit | L0 exposure | L1 exposure | L0 depth | L1 depth | L1 2Q delta |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in bottlenecks["benefit_erased_by_level1"]:
        lines.append(
            f"| `{row['circuit']}` | {fmt_pct(row['level0_exposure_reduction_pct'])} | "
            f"{fmt_pct(row['level1_exposure_reduction_pct'])} | "
            f"{fmt_pct(row['level0_depth_reduction_pct'])} | "
            f"{fmt_pct(row['level1_depth_reduction_pct'])} | "
            f"{fmt_num(row['level1_2q_delta'])} |"
        )

    lines.extend(
        [
            "",
            "## Level 1 Two-Qubit Bottlenecks",
            "",
            "| Circuit | Source 2Q | Optimized 2Q | Delta | Reduction | Optimized exposure |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in bottlenecks["level1_two_qubit_bottlenecks"]:
        lines.append(
            f"| `{row['circuit']}` | {fmt_num(row['source_2q_count'])} | "
            f"{fmt_num(row['optimized_2q_count'])} | {fmt_num(row['delta'])} | "
            f"{fmt_pct(row['reduction_pct'])} | {fmt_num(row['optimized_exposure'])} |"
        )

    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {item}" for item in report["interpretation"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_post_routing_bottleneck_profile.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_post_routing_bottleneck_profile.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    report = build_report(root, args.limit)
    json_output = (root / args.json_output).resolve()
    markdown_output = (root / args.markdown_output).resolve()
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
