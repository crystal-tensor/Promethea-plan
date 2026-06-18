#!/usr/bin/env python3
"""Build the B1 Qiskit heavy-hex routing diagnostic report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def percent(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}%"


def build_report(root: Path, suite_path: Path) -> dict:
    suite = read_json(suite_path)
    summaries = suite["summaries"]
    aer_valid = [row for row in summaries if row["aer_crosscheck_failed"] == 0]
    best = max(summaries, key=lambda row: row["hardware_weighted_exposure_reduction_pct"])
    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "Qiskit heavy-hex routing diagnostic",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "device_like_topology_diagnostic_not_calibrated_noise_baseline",
        "suite_summary": str(suite_path.relative_to(root)),
        "baseline_kind": suite["baseline_kind"],
        "profile": suite["profile"],
        "distance": suite["distance"],
        "physical_qubits": suite["physical_qubits"],
        "coupling_edges": suite["coupling_edges"],
        "source_circuit_count": suite["source_circuit_count"],
        "aer_crosscheck_all_passed": len(aer_valid) == len(summaries),
        "aer_crosscheck_valid_levels": [row["optimization_level"] for row in aer_valid],
        "best_diagnostic_level_by_exposure": best["optimization_level"],
        "best_diagnostic_exposure_reduction_pct": best["hardware_weighted_exposure_reduction_pct"],
        "line_routing_is_calibrated_heavy_hex": False,
        "calibrated_noise_model": False,
        "levels": [
            {
                "optimization_level": row["optimization_level"],
                "measurement_distribution_check": row["measurement_distribution_check"],
                "aer_crosscheck_passed": row["aer_crosscheck_passed"],
                "aer_crosscheck_failed": row["aer_crosscheck_failed"],
                "aer_crosscheck_shots": row["aer_crosscheck_shots"],
                "aer_crosscheck_max_tvd": row["aer_crosscheck_max_tvd"],
                "aer_crosscheck_max_threshold": row["aer_crosscheck_max_threshold"],
                "operation_count_reduction_pct": row["operation_count_reduction_pct"],
                "two_qubit_gate_count_reduction_pct": row["two_qubit_gate_count_reduction_pct"],
                "logical_depth_reduction_pct": row["logical_depth_reduction_pct"],
                "hardware_weighted_exposure_reduction_pct": row["hardware_weighted_exposure_reduction_pct"],
                "summary_path": row["summary_path"],
                "metrics_path": row["metrics_path"],
                "aer_crosscheck_path": row["aer_crosscheck_path"],
            }
            for row in summaries
        ],
        "interpretation": [
            "This is the first B1 topology-aware Qiskit heavy-hex routing diagnostic.",
            "The Qiskit heavy-hex distance-3 coupling map has 19 physical qubits and 40 directed edges.",
            "Level 0 passes independent Aer output-distribution cross-checks for all 30 circuit pairs under the current shot-based threshold model.",
            "Routing to this sparse physical topology substantially worsens operation count, two-qubit count, logical depth, and hardware-weighted exposure.",
            "This is not a calibrated device baseline because no backend-specific durations, error rates, readout errors, or noise model are used.",
        ],
        "open_gates": [
            "Run optimization levels 1 and 3 as a longer regression or optimize the runner to avoid long interactive waits.",
            "Add calibrated backend properties or a documented synthetic heavy-hex noise model.",
            "Compare B1 compressed circuits after routing, not only source circuits after routing, to quantify end-to-end routed benefit.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B1 Heavy-Hex Routing Diagnostic v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Summary",
        "",
        f"- Physical topology: heavy-hex distance {report['distance']}",
        f"- Physical qubits: {report['physical_qubits']}",
        f"- Coupling edges: {report['coupling_edges']}",
        f"- Source circuits: {report['source_circuit_count']}",
        f"- Aer cross-check all passed: {report['aer_crosscheck_all_passed']}",
        f"- Aer-valid levels: {report['aer_crosscheck_valid_levels']}",
        f"- Best diagnostic level by exposure: {report['best_diagnostic_level_by_exposure']}",
        f"- Best diagnostic exposure reduction: {percent(report['best_diagnostic_exposure_reduction_pct'])}",
        "",
        "## Level Results",
        "",
        "| Level | Aer pass/fail | Shots | Max TVD | Operation | 2Q gates | Depth | Exposure |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["levels"]:
        lines.append(
            f"| {row['optimization_level']} | "
            f"{row['aer_crosscheck_passed']} / {row['aer_crosscheck_failed']} | "
            f"{row['aer_crosscheck_shots']} | {row['aer_crosscheck_max_tvd']:.5f} | "
            f"{percent(row['operation_count_reduction_pct'])} | "
            f"{percent(row['two_qubit_gate_count_reduction_pct'])} | "
            f"{percent(row['logical_depth_reduction_pct'])} | "
            f"{percent(row['hardware_weighted_exposure_reduction_pct'])} |"
        )
    lines.extend(
        [
            "",
            "Negative reduction means routing worsened that metric.",
            "",
            "## Interpretation",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["interpretation"])
    lines.extend(["", "## Open Gates", ""])
    lines.extend(f"- {item}" for item in report["open_gates"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--suite-summary",
        type=Path,
        default=Path("results/b1_qiskit_heavyhex_routing_30/qiskit_heavyhex_routing_suite_summary.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_heavyhex_routing_diagnostic.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_heavyhex_routing_diagnostic.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    report = build_report(root, (root / args.suite_summary).resolve())
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
