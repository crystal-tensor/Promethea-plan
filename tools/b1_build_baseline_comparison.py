#!/usr/bin/env python3
"""Build B1 comparison report against independent transpiler baselines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


METRICS = [
    ("operation_count_reduction_pct", "Operation"),
    ("two_qubit_gate_count_reduction_pct", "2Q"),
    ("logical_depth_reduction_pct", "Depth"),
    ("hardware_weighted_exposure_reduction_pct", "Exposure"),
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: float) -> str:
    return f"{float(value):.2f}%"


def build_report(root: Path) -> dict:
    certificate_path = root / "research" / "B1_certificate_report.json"
    qiskit_path = root / "results" / "b1_qiskit_baseline_30" / "qiskit_baseline_suite_summary.json"
    certificate = load_json(certificate_path)
    qiskit = load_json(qiskit_path)
    exact = certificate["exact_aggregate"]
    valid = [row for row in qiskit["summaries"] if row["equivalence_failed"] == 0]
    invalid = [row for row in qiskit["summaries"] if row["equivalence_failed"] != 0]
    best_valid = max(valid, key=lambda row: row["hardware_weighted_exposure_reduction_pct"])
    b1_row = {
        "method": "b1_fixed_point_commuting_1q_plus_iterative_rzz_v0",
        "equivalence_failed": exact["equivalence_failed"],
        "circuit_count": exact["circuit_count"],
        "operation_count_reduction_pct": exact["operation_count_reduction_pct"],
        "two_qubit_gate_count_reduction_pct": exact["two_qubit_gate_count_reduction_pct"],
        "logical_depth_reduction_pct": exact["logical_depth_reduction_pct"],
        "hardware_weighted_exposure_reduction_pct": exact["hardware_weighted_exposure_reduction_pct"],
    }
    deltas = {
        key: b1_row[key] - best_valid[key]
        for key, _label in METRICS
    }
    return {
        "benchmark_id": "B1",
        "report": "baseline_comparison_v0",
        "last_updated": "2026-06-13",
        "profile": certificate["prooflog_results"][0]["profile"],
        "b1": b1_row,
        "baseline_suite": {
            "path": str(qiskit_path.relative_to(root)),
            "kind": qiskit["baseline_kind"],
            "valid_optimization_levels": qiskit["valid_optimization_levels"],
            "invalid_optimization_levels": qiskit["invalid_optimization_levels"],
            "limits": qiskit["limits"],
        },
        "valid_qiskit_baselines": valid,
        "invalid_qiskit_baselines": invalid,
        "best_valid_qiskit_by_exposure": best_valid,
        "b1_minus_best_valid_qiskit": deltas,
        "claim": (
            "On the 30-circuit exact suite, B1 outperforms the best exact-valid "
            "Qiskit all-to-all u3/cx baseline on operation count, two-qubit count, "
            "logical depth, and hardware-weighted exposure. Qiskit level 3 is not "
            "used as a valid baseline because exact equivalence fails on 7 circuits."
        ),
        "remaining_gap": (
            "This is still not a routing-aware calibrated heavy-hex comparison; "
            "the next baseline should include coupling maps, target basis, and "
            "layout/routing constraints without changing circuit semantics."
        ),
    }


def markdown(report: dict) -> str:
    lines = [
        "# B1 Baseline Comparison Report v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        report["claim"],
        "",
        f"Remaining gap: {report['remaining_gap']}",
        "",
        "## Best Valid Comparison",
        "",
        "| Method | Equiv failures | Operation | 2Q | Depth | Exposure |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    b1 = report["b1"]
    q = report["best_valid_qiskit_by_exposure"]
    lines.append(
        f"| B1 fixed-point | {b1['equivalence_failed']} | {fmt(b1['operation_count_reduction_pct'])} | "
        f"{fmt(b1['two_qubit_gate_count_reduction_pct'])} | {fmt(b1['logical_depth_reduction_pct'])} | "
        f"{fmt(b1['hardware_weighted_exposure_reduction_pct'])} |"
    )
    lines.append(
        f"| Qiskit level {q['optimization_level']} | {q['equivalence_failed']} | {fmt(q['operation_count_reduction_pct'])} | "
        f"{fmt(q['two_qubit_gate_count_reduction_pct'])} | {fmt(q['logical_depth_reduction_pct'])} | "
        f"{fmt(q['hardware_weighted_exposure_reduction_pct'])} |"
    )

    lines.extend(["", "## B1 Minus Best Valid Qiskit", "", "| Metric | Delta |", "|---|---:|"])
    for key, label in METRICS:
        lines.append(f"| {label} | {fmt(report['b1_minus_best_valid_qiskit'][key])} |")

    lines.extend(
        [
            "",
            "## Qiskit Baseline Levels",
            "",
            "| Level | Exact pass/fail | Operation | 2Q | Depth | Exposure |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["valid_qiskit_baselines"] + report["invalid_qiskit_baselines"]:
        lines.append(
            f"| {row['optimization_level']} | {row['equivalence_passed']}/{row['equivalence_failed']} | "
            f"{fmt(row['operation_count_reduction_pct'])} | {fmt(row['two_qubit_gate_count_reduction_pct'])} | "
            f"{fmt(row['logical_depth_reduction_pct'])} | {fmt(row['hardware_weighted_exposure_reduction_pct'])} |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["baseline_suite"]["limits"])
    lines.append("- Level 3 is reported for diagnostics only because exact equivalence failed.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_baseline_comparison.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_baseline_comparison.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    report = build_report(root)
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
