#!/usr/bin/env python3
"""Build the B1 heavy-hex end-to-end routed benefit report."""

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


def build_report(root: Path, summary_path: Path) -> dict:
    summary = read_json(summary_path)
    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 heavy-hex end-to-end routed benefit",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "topology_routed_benefit_diagnostic_not_calibrated_noise_claim",
        "summary_path": str(summary_path.relative_to(root)),
        "baseline_kind": summary["baseline_kind"],
        "optimization_level": summary["optimization_level"],
        "physical_qubits": summary["physical_qubits"],
        "coupling_edges": summary["coupling_edges"],
        "circuit_count": summary["circuit_count"],
        "aer_crosscheck_passed": summary["aer_crosscheck_passed"],
        "aer_crosscheck_failed": summary["aer_crosscheck_failed"],
        "aer_crosscheck_shots": summary["aer_crosscheck_shots"],
        "aer_crosscheck_max_tvd": summary["aer_crosscheck_max_tvd"],
        "operation_count_reduction_pct": summary["operation_count_reduction_pct"],
        "two_qubit_gate_count_reduction_pct": summary["two_qubit_gate_count_reduction_pct"],
        "logical_depth_reduction_pct": summary["logical_depth_reduction_pct"],
        "hardware_weighted_exposure_reduction_pct": summary["hardware_weighted_exposure_reduction_pct"],
        "idle_layer_proxy_reduction_pct": summary["idle_layer_proxy_reduction_pct"],
        "source_routed_metrics": summary["source_routed_metrics"],
        "optimized_routed_metrics": summary["optimized_routed_metrics"],
        "aer_crosscheck_path": summary["aer_crosscheck_path"],
        "interpretation": [
            "B1 fixed-point compression retains measurable routed benefits after both source and optimized circuits are routed to the same heavy-hex distance-3 topology.",
            "The strongest routed benefits in this first diagnostic are operation count, logical depth, and idle-layer proxy reductions.",
            "Two-qubit gate count is unchanged after routing at Qiskit level 0, so the current B1 two-qubit logical reduction is mostly absorbed by routing overhead.",
            "Hardware-weighted exposure improves only modestly after routing, far below the 20% portfolio target.",
            "This is a topology-routed diagnostic, not a calibrated backend noise or duration claim.",
        ],
        "open_gates": [
            "Run optimization levels 1 and 3 as a longer regression to see whether routing optimization preserves or erases B1 benefits.",
            "Route both source and B1 optimized circuits through a calibrated or synthetic-noise heavy-hex backend model.",
            "Add routing-aware optimization passes so B1 reduces post-routing two-qubit count and exposure, not only pre-routing logical depth.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B1 Heavy-Hex End-to-End Routed Benefit v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Summary",
        "",
        f"- Circuits: {report['circuit_count']}",
        f"- Heavy-hex physical qubits: {report['physical_qubits']}",
        f"- Coupling edges: {report['coupling_edges']}",
        f"- Aer cross-check pass/fail: {report['aer_crosscheck_passed']} / {report['aer_crosscheck_failed']}",
        f"- Aer shots per pair: {report['aer_crosscheck_shots']}",
        f"- Aer max TVD: {report['aer_crosscheck_max_tvd']:.5f}",
        "",
        "## Routed Benefit",
        "",
        "| Metric | Reduction after routing |",
        "|---|---:|",
        f"| Operation count | {percent(report['operation_count_reduction_pct'])} |",
        f"| Two-qubit gates | {percent(report['two_qubit_gate_count_reduction_pct'])} |",
        f"| Logical depth | {percent(report['logical_depth_reduction_pct'])} |",
        f"| Hardware-weighted exposure | {percent(report['hardware_weighted_exposure_reduction_pct'])} |",
        f"| Idle-layer proxy | {percent(report['idle_layer_proxy_reduction_pct'])} |",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report["interpretation"])
    lines.extend(["", "## Open Gates", ""])
    lines.extend(f"- {item}" for item in report["open_gates"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/b1_heavyhex_end_to_end_30/heavyhex_end_to_end_summary.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_heavyhex_end_to_end_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_heavyhex_end_to_end_report.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    report = build_report(root, (root / args.summary).resolve())
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
