#!/usr/bin/env python3
"""Build the B1 line-routing Qiskit diagnostic report."""

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


def relpath(path: str, root: Path) -> str:
    raw = Path(path)
    if raw.is_absolute():
        try:
            return str(raw.relative_to(root))
        except ValueError:
            return str(raw)
    return str(raw)


def normalized_circuit_name(path: str) -> str:
    text = relpath(path, Path.cwd())
    marker = "00_source/"
    if marker in text:
        return text.split(marker, 1)[1]
    return Path(text).name


def load_aer_crosschecks(root: Path, summaries: list[dict]) -> dict:
    rows = []
    for summary in summaries:
        level = summary["optimization_level"]
        path = root / "results" / "b1_qiskit_line_routing_30" / f"qiskit_line_level{level}_aer_measurement_crosscheck.json"
        if not path.exists():
            rows.append(
                {
                    "optimization_level": level,
                    "exists": False,
                    "path": str(path.relative_to(root)),
                }
            )
            continue
        payload = read_json(path)
        rows.append(
            {
                "optimization_level": level,
                "exists": True,
                "path": str(path.relative_to(root)),
                "check": payload.get("check"),
                "simulator": payload.get("simulator"),
                "method": payload.get("method"),
                "shots": payload.get("shots"),
                "passed": payload.get("passed"),
                "failed": payload.get("failed"),
                "pair_count": payload.get("pair_count"),
                "max_total_variation_distance": payload.get("max_total_variation_distance"),
                "max_threshold": payload.get("max_threshold"),
            }
        )
    return {
        "available": all(row.get("exists") for row in rows),
        "all_passed": bool(rows) and all(row.get("exists") and row.get("failed") == 0 for row in rows),
        "levels": rows,
        "total_pairs": sum(int(row.get("pair_count") or 0) for row in rows),
        "total_failed": sum(int(row.get("failed") or 0) for row in rows),
        "max_total_variation_distance": max(
            (float(row.get("max_total_variation_distance") or 0.0) for row in rows),
            default=0.0,
        ),
        "max_threshold": max((float(row.get("max_threshold") or 0.0) for row in rows), default=0.0),
    }


def build_report(root: Path, suite_path: Path) -> dict:
    suite = read_json(suite_path)
    summaries = suite["summaries"]
    aer_crosscheck = load_aer_crosschecks(root, summaries)
    exact_valid = [row for row in summaries if row["equivalence_failed"] == 0]
    measurement_full_valid = [row for row in summaries if row["measurement_distribution_failed"] == 0]
    measurement_partial_valid = [row for row in summaries if row["measurement_distribution_failed"] <= 1]
    common_measurement_failures = sorted(
        set.intersection(
            *[
                {normalized_circuit_name(path) for path in row.get("measurement_distribution_failed_circuits", [])}
                for row in summaries
            ]
        )
        if summaries
        else set()
    )
    best_diagnostic = max(summaries, key=lambda row: row["hardware_weighted_exposure_reduction_pct"])
    measurement_pass_counts = sorted(
        {f"{row['measurement_distribution_passed']}/{row['measurement_distribution_passed'] + row['measurement_distribution_failed']}" for row in summaries}
    )
    interpretation = [
        "No line-routing optimization level currently passes the bare statevector checker on all 30 circuits.",
        "The sequential measurement-distribution checker models mid-circuit measurement by branching and collapse, so it is the relevant diagnostic for circuits that keep using measured qubits.",
    ]
    if measurement_full_valid:
        interpretation.append(
            "All tested line-routing levels pass measurement-distribution equivalence on the 30-circuit suite under the sequential measurement model."
        )
    else:
        interpretation.append(
            "The measurement-distribution checker is still partial; at least one tested level has an unmatched output distribution."
        )
    interpretation.extend(
        [
            f"Observed measurement-distribution pass counts across levels: {', '.join(measurement_pass_counts)}.",
            (
                "Independent Qiskit Aer shot-based cross-check passes all routed pairs."
                if aer_crosscheck["all_passed"]
                else "Independent Qiskit Aer shot-based cross-check is missing or has failures."
            ),
            "All tested line-routing levels worsen hardware-weighted exposure on this sparse line coupling map, so this diagnostic does not weaken the current B1 advantage versus all-to-all exact-valid Qiskit baselines.",
            "This is not a calibrated heavy-hex routing baseline; that gate remains open.",
        ]
    )
    report = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "Qiskit line-routing baseline diagnostic",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "diagnostic_only_not_validated_baseline",
        "suite_summary": str(suite_path.relative_to(root)),
        "baseline_kind": suite["baseline_kind"],
        "profile": suite["profile"],
        "source_circuit_count": suite["source_circuit_count"],
        "diagnostic_status": suite.get("diagnostic_status"),
        "line_routing_is_calibrated_heavy_hex": False,
        "full_exact_valid_baseline": bool(exact_valid),
        "full_measurement_distribution_valid_baseline": bool(measurement_full_valid),
        "measurement_distribution_partial_valid_levels": [
            row["optimization_level"] for row in measurement_partial_valid
        ],
        "common_measurement_distribution_failures": common_measurement_failures,
        "aer_crosscheck": aer_crosscheck,
        "best_diagnostic_level_by_exposure": best_diagnostic["optimization_level"],
        "best_diagnostic_exposure_reduction_pct": best_diagnostic["hardware_weighted_exposure_reduction_pct"],
        "interpretation": interpretation,
        "levels": [
            {
                "optimization_level": row["optimization_level"],
                "statevector_passed": row["equivalence_passed"],
                "statevector_failed": row["equivalence_failed"],
                "measurement_distribution_passed": row["measurement_distribution_passed"],
                "measurement_distribution_failed": row["measurement_distribution_failed"],
                "operation_count_reduction_pct": row["operation_count_reduction_pct"],
                "two_qubit_gate_count_reduction_pct": row["two_qubit_gate_count_reduction_pct"],
                "logical_depth_reduction_pct": row["logical_depth_reduction_pct"],
                "hardware_weighted_exposure_reduction_pct": row[
                    "hardware_weighted_exposure_reduction_pct"
                ],
                "summary_path": relpath(row["summary_path"], root),
                "equivalence_path": relpath(row["equivalence_path"], root),
                "measurement_equivalence_path": relpath(row["measurement_equivalence_path"], root),
                "aer_crosscheck": next(
                    aer_row
                    for aer_row in aer_crosscheck["levels"]
                    if aer_row["optimization_level"] == row["optimization_level"]
                ),
                "failed_measurement_circuits": [
                    normalized_circuit_name(path)
                    for path in row.get("measurement_distribution_failed_circuits", [])
                ],
            }
            for row in summaries
        ],
        "open_gates": [
            "Add calibrated heavy-hex routing baseline with a device-like coupling map and noise/error model.",
            "Turn the Aer shot-based cross-check into either an exact independent probability check or a larger-shot statistical regression before promoting it beyond diagnostic evidence.",
            "Decide whether routing baseline comparison should use output-distribution equivalence, unitary equivalence with layout recovery, or both.",
        ],
    }
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B1 Routing Baseline Diagnostic v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Summary",
        "",
        (
            "This report records a Qiskit line-coupling routing diagnostic for the "
            "30-circuit B1 exact suite. It is useful evidence, but it is not a "
            "validated calibrated heavy-hex baseline."
        ),
        "",
        f"- Source circuits: {report['source_circuit_count']}",
        f"- Full exact-valid baseline: {report['full_exact_valid_baseline']}",
        f"- Full measurement-distribution-valid baseline: {report['full_measurement_distribution_valid_baseline']}",
        f"- Partial measurement-distribution-valid levels: {report['measurement_distribution_partial_valid_levels']}",
        f"- Common unsupported/failing circuit: {report['common_measurement_distribution_failures']}",
        f"- Aer cross-check all passed: {report['aer_crosscheck']['all_passed']}",
        f"- Aer cross-check pairs: {report['aer_crosscheck']['total_pairs']}",
        f"- Aer cross-check max TVD: {report['aer_crosscheck']['max_total_variation_distance']:.5f}",
        f"- Best diagnostic level by exposure: {report['best_diagnostic_level_by_exposure']}",
        f"- Best diagnostic exposure reduction: {percent(report['best_diagnostic_exposure_reduction_pct'])}",
        "",
        "## Level Results",
        "",
        "| Level | Statevector pass/fail | Measurement distribution pass/fail | Operation | 2Q gates | Depth | Exposure |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["levels"]:
        lines.append(
            f"| {row['optimization_level']} | "
            f"{row['statevector_passed']} / {row['statevector_failed']} | "
            f"{row['measurement_distribution_passed']} / {row['measurement_distribution_failed']} | "
            f"{percent(row['operation_count_reduction_pct'])} | "
            f"{percent(row['two_qubit_gate_count_reduction_pct'])} | "
            f"{percent(row['logical_depth_reduction_pct'])} | "
            f"{percent(row['hardware_weighted_exposure_reduction_pct'])} |"
        )
    lines.extend(
        [
            "",
            "Negative reduction means the routed baseline worsened that metric.",
            "",
            "## Aer Cross-Check",
            "",
            "| Level | Pairs pass/fail | Shots | Max TVD | Max threshold |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["aer_crosscheck"]["levels"]:
        if not row.get("exists"):
            lines.append(f"| {row['optimization_level']} | missing | n/a | n/a | n/a |")
        else:
            lines.append(
                f"| {row['optimization_level']} | {row['passed']} / {row['failed']} | "
                f"{row['shots']} | {row['max_total_variation_distance']:.5f} | {row['max_threshold']:.5f} |"
            )
    lines.extend(
        [
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
        default=Path("results/b1_qiskit_line_routing_30/qiskit_line_routing_suite_summary.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_routing_baseline_diagnostic.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_routing_baseline_diagnostic.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    suite_path = (root / args.suite_summary).resolve()
    report = build_report(root, suite_path)
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
