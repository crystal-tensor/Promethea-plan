#!/usr/bin/env python3
"""Run Qiskit line-coupling routing baselines on the B1 30-circuit suite."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from qiskit import QuantumCircuit, qasm2, transpile
from qiskit.transpiler import CouplingMap

from b1_qiskit_baseline import DEFAULT_SOURCES, best_by, copy_source_bundle, load_json


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=check)


def qasm_files(path: Path) -> list[Path]:
    return sorted(path.rglob("*.qasm"))


def transpile_line_bundle(source_dir: Path, output_dir: Path, optimization_level: int, basis_gates: list[str]) -> dict:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    total_runtime = 0.0
    for source in qasm_files(source_dir):
        relative = source.relative_to(source_dir)
        target = output_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        circuit = QuantumCircuit.from_qasm_file(str(source))
        coupling_map = CouplingMap.from_line(circuit.num_qubits)
        started = time.perf_counter()
        transpiled = transpile(
            circuit,
            basis_gates=basis_gates,
            coupling_map=coupling_map,
            optimization_level=optimization_level,
            seed_transpiler=220626,
        )
        runtime = time.perf_counter() - started
        total_runtime += runtime
        target.write_text(qasm2.dumps(transpiled), encoding="utf-8")
        rows.append(
            {
                "source": str(source),
                "output": str(target),
                "optimization_level": optimization_level,
                "input_qubits": circuit.num_qubits,
                "input_ops": int(circuit.size()),
                "output_qubits": transpiled.num_qubits,
                "output_ops": int(transpiled.size()),
                "runtime_seconds": runtime,
            }
        )
    return {
        "optimization_level": optimization_level,
        "output_dir": str(output_dir),
        "basis_gates": basis_gates,
        "coupling": "line_same_qubit_count",
        "circuit_count": len(rows),
        "runtime_seconds": total_runtime,
        "circuits": rows,
    }


def summarize_metrics(
    before_path: Path,
    after_path: Path,
    equivalence_path: Path,
    measurement_equivalence_path: Path,
    transpile_report: dict,
) -> dict:
    before = load_json(before_path)
    after = load_json(after_path)
    equivalence = load_json(equivalence_path)
    measurement_equivalence = load_json(measurement_equivalence_path)

    def total(payload: dict, key: str) -> float:
        return sum(float(row[key]) for row in payload["results"])

    summary = {
        "benchmark_id": "B1",
        "method": "qiskit_line_routing_baseline_v0",
        "baseline_kind": "qiskit_line_coupling_u3_cx_basis",
        "optimization_level": transpile_report["optimization_level"],
        "basis_gates": transpile_report["basis_gates"],
        "coupling": transpile_report["coupling"],
        "circuit_count": before["circuit_count"],
        "equivalence_passed": equivalence["passed"],
        "equivalence_failed": equivalence["failed"],
        "measurement_distribution_passed": measurement_equivalence["passed"],
        "measurement_distribution_failed": measurement_equivalence["failed"],
        "measurement_distribution_failed_circuits": [
            row["left"] for row in measurement_equivalence["results"] if not row["equivalent"]
        ],
        "runtime_seconds": transpile_report["runtime_seconds"],
        "output_dir": transpile_report["output_dir"],
    }
    for key in [
        "operation_count",
        "two_qubit_gate_count",
        "logical_depth",
        "hardware_weighted_error_exposure",
    ]:
        short = "hardware_weighted_exposure" if key == "hardware_weighted_error_exposure" else key
        before_total = total(before, key)
        after_total = total(after, key)
        summary[f"{short}_before"] = before_total
        summary[f"{short}_after"] = after_total
        summary[f"{short}_delta"] = after_total - before_total
        summary[f"{short}_reduction_pct"] = (before_total - after_total) / before_total * 100 if before_total else 0.0
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--work-dir", type=Path, default=Path("results/b1_qiskit_line_routing_30_work"))
    parser.add_argument("--results-dir", type=Path, default=Path("results/b1_qiskit_line_routing_30"))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--max-qubits", type=int, default=15)
    parser.add_argument("--levels", nargs="+", type=int, default=[0, 1, 3])
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    work_dir = root / args.work_dir
    results_dir = root / args.results_dir
    source_dir = work_dir / "00_source"
    results_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    source_rows = copy_source_bundle(root, source_dir, DEFAULT_SOURCES)

    source_metrics = results_dir / "qiskit_line_source_metrics.json"
    run(
        [
            sys.executable,
            "tools/b1_qasm_metrics.py",
            str(source_dir),
            "--profile",
            args.profile,
            "--pretty",
            "--output",
            str(source_metrics),
        ]
    )

    summaries = []
    transpile_reports = []
    for level in args.levels:
        label = f"qiskit_line_level{level}"
        output_dir = work_dir / label
        transpile_report = transpile_line_bundle(
            source_dir,
            output_dir,
            optimization_level=level,
            basis_gates=["u3", "cx", "measure"],
        )
        transpile_reports.append(transpile_report)
        after_metrics = results_dir / f"{label}_metrics.json"
        equivalence_path = results_dir / f"{label}_equivalence.json"
        measurement_equivalence_path = results_dir / f"{label}_measurement_equivalence.json"
        summary_path = results_dir / f"{label}_summary.json"
        run(
            [
                sys.executable,
                "tools/b1_qasm_metrics.py",
                str(output_dir),
                "--profile",
                args.profile,
                "--pretty",
                "--output",
                str(after_metrics),
            ]
        )
        run(
            [
                sys.executable,
                "tools/b1_equivalence_check.py",
                str(source_dir),
                str(output_dir),
                "--max-qubits",
                str(args.max_qubits),
                "--pretty",
                "--output",
                str(equivalence_path),
            ],
            check=False,
        )
        run(
            [
                sys.executable,
                "tools/b1_measurement_distribution_check.py",
                str(source_dir),
                str(output_dir),
                "--max-qubits",
                str(args.max_qubits),
                "--pretty",
                "--output",
                str(measurement_equivalence_path),
            ],
            check=False,
        )
        summary = summarize_metrics(
            source_metrics,
            after_metrics,
            equivalence_path,
            measurement_equivalence_path,
            transpile_report,
        )
        summary["summary_path"] = str(summary_path)
        summary["metrics_path"] = str(after_metrics)
        summary["equivalence_path"] = str(equivalence_path)
        summary["measurement_equivalence_path"] = str(measurement_equivalence_path)
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summaries.append(summary)

    valid_summaries = [summary for summary in summaries if summary["equivalence_failed"] == 0]
    invalid_summaries = [summary for summary in summaries if summary["equivalence_failed"] != 0]
    measurement_valid_summaries = [summary for summary in summaries if summary["measurement_distribution_failed"] == 0]
    diagnostic_best = best_by(summaries, "hardware_weighted_exposure_reduction_pct")

    payload = {
        "benchmark_id": "B1",
        "method": "qiskit_line_routing_baseline_suite_v0",
        "baseline_kind": "qiskit_line_coupling_u3_cx_basis",
        "diagnostic_status": (
            "full_exact_valid_baseline"
            if valid_summaries
            else "diagnostic_only_no_level_passed_bare_statevector_equivalence"
        ),
        "last_updated": "2026-06-13",
        "profile": args.profile,
        "source_dir": str(source_dir),
        "source_circuit_count": len(source_rows),
        "source_metrics": str(source_metrics),
        "transpile_reports": transpile_reports,
        "summaries": summaries,
        "valid_optimization_levels": [summary["optimization_level"] for summary in valid_summaries],
        "invalid_optimization_levels": [summary["optimization_level"] for summary in invalid_summaries],
        "measurement_distribution_valid_optimization_levels": [
            summary["optimization_level"] for summary in measurement_valid_summaries
        ],
        "measurement_distribution_invalid_optimization_levels": [
            summary["optimization_level"]
            for summary in summaries
            if summary["measurement_distribution_failed"] != 0
        ],
        "best_by_operation_count": (
            best_by(valid_summaries, "operation_count_reduction_pct")["optimization_level"] if valid_summaries else None
        ),
        "best_by_logical_depth": (
            best_by(valid_summaries, "logical_depth_reduction_pct")["optimization_level"] if valid_summaries else None
        ),
        "best_by_hardware_weighted_exposure": (
            best_by(valid_summaries, "hardware_weighted_exposure_reduction_pct")["optimization_level"] if valid_summaries else None
        ),
        "diagnostic_best_by_hardware_weighted_exposure": diagnostic_best["optimization_level"],
        "limits": [
            "Qiskit line-routing baseline constrains CX interactions to a line coupling map with the same qubit count as each circuit.",
            "This is routing-aware, but it is not a calibrated heavy-hex device target.",
            "Bare statevector equivalence can fail when the router changes final measurement-to-classical-bit mappings.",
            "Measurement-distribution equivalence is diagnostic because the current checker assumes final measurements and does not support all mid-circuit measurement semantics.",
        ],
    }
    suite_path = results_dir / "qiskit_line_routing_suite_summary.json"
    suite_path.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
