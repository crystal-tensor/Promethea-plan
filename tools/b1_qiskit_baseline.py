#!/usr/bin/env python3
"""Run Qiskit transpiler baselines on the B1 30-circuit exact suite."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit import qasm2


DEFAULT_SOURCES = [
    ("qasmbench_small", "results/qasmbench_small_fixed_point_pipeline_work/00_input"),
    ("qasmbench_medium_exact", "results/qasmbench_medium_exact_fixed_point_pipeline_work/00_input"),
    ("qasmbench_interaction_exact", "results/qasmbench_interaction_exact_fixed_point_pipeline_work/00_input"),
    ("b1_exact_extension", "results/b1_exact_extension_fixed_point_pipeline_work/00_input"),
]


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=check)


def qasm_files(path: Path) -> list[Path]:
    return sorted(path.rglob("*.qasm"))


def copy_source_bundle(root: Path, source_dir: Path, sources: list[tuple[str, str]]) -> list[dict]:
    if source_dir.exists():
        shutil.rmtree(source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for prefix, rel_path in sources:
        path = root / rel_path
        for file in qasm_files(path):
            target = source_dir / prefix / file.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
            rows.append({"subset": prefix, "source": str(file), "bundle_path": str(target)})
    return rows


def transpile_bundle(source_dir: Path, output_dir: Path, optimization_level: int, basis_gates: list[str]) -> dict:
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
        started = time.perf_counter()
        transpiled = transpile(circuit, basis_gates=basis_gates, optimization_level=optimization_level)
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
                "output_ops": int(transpiled.size()),
                "runtime_seconds": runtime,
            }
        )
    return {
        "optimization_level": optimization_level,
        "output_dir": str(output_dir),
        "basis_gates": basis_gates,
        "circuit_count": len(rows),
        "runtime_seconds": total_runtime,
        "circuits": rows,
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_metrics(before_path: Path, after_path: Path, equivalence_path: Path, transpile_report: dict) -> dict:
    before = load_json(before_path)
    after = load_json(after_path)
    equivalence = load_json(equivalence_path)

    def total(payload: dict, key: str) -> float:
        return sum(float(row[key]) for row in payload["results"])

    summary = {
        "benchmark_id": "B1",
        "method": "qiskit_transpiler_baseline_v0",
        "baseline_kind": "qiskit_all_to_all_u3_cx_basis_no_routing",
        "optimization_level": transpile_report["optimization_level"],
        "basis_gates": transpile_report["basis_gates"],
        "circuit_count": before["circuit_count"],
        "equivalence_passed": equivalence["passed"],
        "equivalence_failed": equivalence["failed"],
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


def best_by(summaries: list[dict], key: str) -> dict:
    return max(summaries, key=lambda row: row[key])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--work-dir", type=Path, default=Path("results/b1_qiskit_baseline_30_work"))
    parser.add_argument("--results-dir", type=Path, default=Path("results/b1_qiskit_baseline_30"))
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

    source_metrics = results_dir / "qiskit_baseline_source_metrics.json"
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
        label = f"qiskit_level{level}"
        output_dir = work_dir / label
        transpile_report = transpile_bundle(
            source_dir,
            output_dir,
            optimization_level=level,
            basis_gates=["u3", "cx", "measure"],
        )
        transpile_reports.append(transpile_report)
        after_metrics = results_dir / f"{label}_metrics.json"
        equivalence_path = results_dir / f"{label}_equivalence.json"
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
        summary = summarize_metrics(source_metrics, after_metrics, equivalence_path, transpile_report)
        summary["summary_path"] = str(summary_path)
        summary["metrics_path"] = str(after_metrics)
        summary["equivalence_path"] = str(equivalence_path)
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summaries.append(summary)

    valid_summaries = [summary for summary in summaries if summary["equivalence_failed"] == 0]
    invalid_summaries = [summary for summary in summaries if summary["equivalence_failed"] != 0]
    if not valid_summaries:
        raise SystemExit("No Qiskit baseline level passed exact equivalence")

    payload = {
        "benchmark_id": "B1",
        "method": "qiskit_transpiler_baseline_suite_v0",
        "baseline_kind": "qiskit_all_to_all_u3_cx_basis_no_routing",
        "last_updated": "2026-06-13",
        "profile": args.profile,
        "source_dir": str(source_dir),
        "source_circuit_count": len(source_rows),
        "source_metrics": str(source_metrics),
        "transpile_reports": transpile_reports,
        "summaries": summaries,
        "valid_optimization_levels": [summary["optimization_level"] for summary in valid_summaries],
        "invalid_optimization_levels": [summary["optimization_level"] for summary in invalid_summaries],
        "best_by_operation_count": best_by(valid_summaries, "operation_count_reduction_pct")["optimization_level"],
        "best_by_logical_depth": best_by(valid_summaries, "logical_depth_reduction_pct")["optimization_level"],
        "best_by_hardware_weighted_exposure": best_by(valid_summaries, "hardware_weighted_exposure_reduction_pct")["optimization_level"],
        "limits": [
            "Qiskit baseline uses all-to-all connectivity and u3/cx basis without routing.",
            "This is an independent compiler baseline, not a calibrated heavy-hex hardware transpilation.",
            "Output equivalence is checked by the local exact statevector checker for the 30-circuit suite.",
        ],
    }
    suite_path = results_dir / "qiskit_baseline_suite_summary.json"
    suite_path.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
