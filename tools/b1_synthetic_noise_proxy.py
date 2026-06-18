#!/usr/bin/env python3
"""Build a synthetic heavy-hex noise proxy report for B1 routed circuits."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


METRIC_KEYS = [
    "operation_count",
    "two_qubit_gate_count",
    "logical_depth",
    "hardware_weighted_error_exposure",
    "idle_layer_proxy",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rel_key(path_text: str) -> str:
    path = Path(path_text)
    parts = path.parts
    for marker in [
        "qasmbench_small",
        "qasmbench_medium_exact",
        "qasmbench_interaction_exact",
        "b1_exact_extension",
    ]:
        if marker in parts:
            index = parts.index(marker)
            return str(Path(*parts[index:]))
    return path.name


def load_metrics(path: Path) -> dict[str, dict]:
    payload = read_json(path)
    return {rel_key(row["path"]): row for row in payload["results"]}


def total(rows: dict[str, dict], key: str) -> float:
    return sum(float(row.get(key, 0.0)) for row in rows.values())


def success_proxy(exposure: float) -> float:
    return math.exp(-exposure)


def comparison(name: str, before: dict[str, dict], after: dict[str, dict]) -> dict:
    before_keys = set(before)
    after_keys = set(after)
    common = sorted(before_keys & after_keys)
    missing_before = sorted(after_keys - before_keys)
    missing_after = sorted(before_keys - after_keys)
    metric_rows = {}
    for key in METRIC_KEYS:
        before_total = sum(float(before[item].get(key, 0.0)) for item in common)
        after_total = sum(float(after[item].get(key, 0.0)) for item in common)
        metric_rows[key] = {
            "before": before_total,
            "after": after_total,
            "delta": after_total - before_total,
            "reduction_pct": (before_total - after_total) / before_total * 100 if before_total else 0.0,
        }
    before_exposure = metric_rows["hardware_weighted_error_exposure"]["before"]
    after_exposure = metric_rows["hardware_weighted_error_exposure"]["after"]
    exposure_delta = after_exposure - before_exposure
    success_ratio = math.exp(before_exposure - after_exposure)
    top_exposure_improvements = []
    for item in common:
        before_value = float(before[item].get("hardware_weighted_error_exposure", 0.0))
        after_value = float(after[item].get("hardware_weighted_error_exposure", 0.0))
        top_exposure_improvements.append(
            {
                "circuit": item,
                "before_exposure": before_value,
                "after_exposure": after_value,
                "delta": after_value - before_value,
                "reduction_pct": (before_value - after_value) / before_value * 100 if before_value else 0.0,
            }
        )
    top_exposure_improvements.sort(key=lambda row: row["delta"])
    return {
        "name": name,
        "circuit_count": len(common),
        "missing_before": missing_before,
        "missing_after": missing_after,
        "metrics": metric_rows,
        "aggregate_log_success_proxy_before": -before_exposure,
        "aggregate_log_success_proxy_after": -after_exposure,
        "aggregate_success_proxy_before": success_proxy(before_exposure),
        "aggregate_success_proxy_after": success_proxy(after_exposure),
        "aggregate_success_proxy_ratio": success_ratio,
        "aggregate_failure_exposure_delta": exposure_delta,
        "top_exposure_improvements": top_exposure_improvements[:10],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B1 Synthetic Heavy-Hex Noise Proxy v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Noise Profile",
        "",
        f"- Profile: `{report['profile_name']}`",
        f"- Description: {report['profile']['description']}",
        f"- Single-qubit error: {report['profile']['gate_errors']['single_qubit']}",
        f"- Two-qubit error: {report['profile']['gate_errors']['two_qubit']}",
        f"- Measurement error: {report['profile']['gate_errors']['measurement']}",
        f"- Idle error per layer: {report['profile']['idle_error_per_layer']}",
        "",
        "## Aggregate Comparisons",
        "",
        "| Comparison | Exposure before | Exposure after | Reduction | Success proxy ratio | 2Q reduction |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["comparisons"]:
        exposure = row["metrics"]["hardware_weighted_error_exposure"]
        twoq = row["metrics"]["two_qubit_gate_count"]
        lines.append(
            f"| {row['name']} | {exposure['before']:.6g} | {exposure['after']:.6g} | "
            f"{exposure['reduction_pct']:.2f}% | {row['aggregate_success_proxy_ratio']:.6g}x | "
            f"{twoq['reduction_pct']:.2f}% |"
        )
    lines.extend(["", "## Top Exposure Improvements", ""])
    for row in report["comparisons"]:
        lines.extend(
            [
                f"### {row['name']}",
                "",
                "| Circuit | Before | After | Delta | Reduction |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for item in row["top_exposure_improvements"][:5]:
            lines.append(
                f"| `{item['circuit']}` | {item['before_exposure']:.6g} | "
                f"{item['after_exposure']:.6g} | {item['delta']:.6g} | {item['reduction_pct']:.2f}% |"
            )
        lines.append("")
    lines.extend(["## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def build_report(args: argparse.Namespace) -> dict:
    profiles = read_json(args.profiles)
    profile = profiles[args.profile]
    source = load_metrics(args.source_routed_metrics)
    b1_routed = load_metrics(args.b1_routed_metrics)
    virtual_swap = load_metrics(args.virtual_swap_metrics)
    comparisons = [
        comparison("source_level1_routed_vs_b1_level1_routed", source, b1_routed),
        comparison("b1_level1_routed_vs_virtual_swap", b1_routed, virtual_swap),
        comparison("source_level1_routed_vs_virtual_swap", source, virtual_swap),
    ]
    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 synthetic heavy-hex noise proxy",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "synthetic_noise_proxy_not_calibrated_device_claim",
        "profile_name": args.profile,
        "profile": profile,
        "source_routed_metrics": str(args.source_routed_metrics),
        "b1_routed_metrics": str(args.b1_routed_metrics),
        "virtual_swap_metrics": str(args.virtual_swap_metrics),
        "comparisons": comparisons,
        "best_comparison_by_exposure_reduction": max(
            comparisons,
            key=lambda row: row["metrics"]["hardware_weighted_error_exposure"]["reduction_pct"],
        )["name"],
        "limits": [
            "This is a documented synthetic heavy-hex-like noise proxy using fixed gate, readout, and idle error rates.",
            "It is not calibrated from a live backend and does not close the true calibrated-device baseline gate.",
            "The success proxy is exp(-hardware_weighted_error_exposure), useful for relative comparison rather than absolute device prediction.",
            "Metric inputs are routed QASM metrics; no stochastic noisy simulation is performed here.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", type=Path, default=Path("benchmarks/hardware_profiles.json"))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument(
        "--source-routed-metrics",
        type=Path,
        default=Path("results/b1_heavyhex_end_to_end_30_level1/source_routed_metrics.json"),
    )
    parser.add_argument(
        "--b1-routed-metrics",
        type=Path,
        default=Path("results/b1_heavyhex_end_to_end_30_level1/b1_optimized_routed_metrics.json"),
    )
    parser.add_argument(
        "--virtual-swap-metrics",
        type=Path,
        default=Path("results/b1_virtual_swap_elimination_level1/after_virtual_swap_metrics.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_synthetic_noise_proxy_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_synthetic_noise_proxy_report.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
