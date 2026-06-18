#!/usr/bin/env python3
"""Build a suite report for B1 heavy-hex end-to-end routed comparisons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_SUMMARIES = [
    Path("results/b1_heavyhex_end_to_end_30/heavyhex_end_to_end_summary.json"),
    Path("results/b1_heavyhex_end_to_end_30_level1/heavyhex_end_to_end_summary.json"),
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def percent(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}%"


def row_from_summary(root: Path, path: Path) -> dict:
    payload = read_json(path)
    return {
        "summary_path": str(path.relative_to(root)),
        "optimization_level": payload["optimization_level"],
        "circuit_count": payload["circuit_count"],
        "aer_crosscheck_passed": payload["aer_crosscheck_passed"],
        "aer_crosscheck_failed": payload["aer_crosscheck_failed"],
        "aer_crosscheck_shots": payload["aer_crosscheck_shots"],
        "aer_crosscheck_max_tvd": payload["aer_crosscheck_max_tvd"],
        "operation_count_reduction_pct": payload["operation_count_reduction_pct"],
        "two_qubit_gate_count_reduction_pct": payload["two_qubit_gate_count_reduction_pct"],
        "logical_depth_reduction_pct": payload["logical_depth_reduction_pct"],
        "hardware_weighted_exposure_reduction_pct": payload["hardware_weighted_exposure_reduction_pct"],
        "idle_layer_proxy_reduction_pct": payload["idle_layer_proxy_reduction_pct"],
    }


def build_report(root: Path, summaries: list[Path]) -> dict:
    rows = [row_from_summary(root, path.resolve()) for path in summaries]
    best_exposure = max(rows, key=lambda row: row["hardware_weighted_exposure_reduction_pct"])
    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 heavy-hex end-to-end routed benefit suite",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "topology_routed_benefit_suite_not_calibrated_noise_claim",
        "levels": rows,
        "levels_tested": [row["optimization_level"] for row in rows],
        "all_aer_crosschecks_passed": all(row["aer_crosscheck_failed"] == 0 for row in rows),
        "best_level_by_exposure": best_exposure["optimization_level"],
        "best_exposure_reduction_pct": best_exposure["hardware_weighted_exposure_reduction_pct"],
        "interpretation": [
            "B1 retains measurable routed benefits under Qiskit heavy-hex level 0.",
            "Qiskit heavy-hex level 1 nearly erases the current B1 pre-routing benefits after routing.",
            "Post-routing two-qubit count does not improve at either tested level.",
            "The next B1 algorithmic step should be routing-aware 2-4 qubit optimization rather than more isolated 1Q compression.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B1 Heavy-Hex End-to-End Routed Benefit Suite v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Level Results",
        "",
        "| Qiskit level | Aer pass/fail | Operation | 2Q gates | Depth | Exposure | Idle proxy |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["levels"]:
        lines.append(
            f"| {row['optimization_level']} | {row['aer_crosscheck_passed']} / {row['aer_crosscheck_failed']} | "
            f"{percent(row['operation_count_reduction_pct'])} | "
            f"{percent(row['two_qubit_gate_count_reduction_pct'])} | "
            f"{percent(row['logical_depth_reduction_pct'])} | "
            f"{percent(row['hardware_weighted_exposure_reduction_pct'])} | "
            f"{percent(row['idle_layer_proxy_reduction_pct'])} |"
        )
    lines.extend(
        [
            "",
            f"Best level by exposure reduction: `{report['best_level_by_exposure']}` ({percent(report['best_exposure_reduction_pct'])}).",
            "",
            "## Interpretation",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["interpretation"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--summaries", nargs="*", type=Path, default=DEFAULT_SUMMARIES)
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_heavyhex_end_to_end_suite.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_heavyhex_end_to_end_suite.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    report = build_report(root, [root / path for path in args.summaries])
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
