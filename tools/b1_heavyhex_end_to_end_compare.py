#!/usr/bin/env python3
"""Compare heavy-hex routed source circuits against heavy-hex routed B1 outputs."""

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

from b1_qiskit_baseline import best_by, load_json


SOURCE_OPTIMIZED_PAIRS = [
    (
        "qasmbench_small",
        "results/qasmbench_small_fixed_point_pipeline_work/00_input",
        "results/qasmbench_small_fixed_point_pipeline_work/final",
    ),
    (
        "qasmbench_medium_exact",
        "results/qasmbench_medium_exact_fixed_point_pipeline_work/00_input",
        "results/qasmbench_medium_exact_fixed_point_pipeline_work/final",
    ),
    (
        "qasmbench_interaction_exact",
        "results/qasmbench_interaction_exact_fixed_point_pipeline_work/00_input",
        "results/qasmbench_interaction_exact_fixed_point_pipeline_work/final",
    ),
    (
        "b1_exact_extension",
        "results/b1_exact_extension_fixed_point_pipeline_work/00_input",
        "results/b1_exact_extension_fixed_point_pipeline_work/final",
    ),
]


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=check)


def qasm_files(path: Path) -> list[Path]:
    return sorted(path.rglob("*.qasm"))


def copy_bundle(root: Path, target_dir: Path, source_index: int) -> list[dict]:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for prefix, source_rel, optimized_rel in SOURCE_OPTIMIZED_PAIRS:
        source_path = root / (source_rel if source_index == 0 else optimized_rel)
        for file in qasm_files(source_path):
            target = target_dir / prefix / file.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
            rows.append({"subset": prefix, "source": str(file), "bundle_path": str(target)})
    return rows


def transpile_bundle(
    input_dir: Path,
    output_dir: Path,
    optimization_level: int,
    basis_gates: list[str],
    distance: int,
) -> dict:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    coupling_map = CouplingMap.from_heavy_hex(distance)
    rows = []
    total_runtime = 0.0
    for source in qasm_files(input_dir):
        relative = source.relative_to(input_dir)
        target = output_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        circuit = QuantumCircuit.from_qasm_file(str(source))
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
        "coupling": f"heavy_hex_distance_{distance}",
        "physical_qubits": coupling_map.size(),
        "coupling_edges": len(coupling_map.get_edges()),
        "circuit_count": len(rows),
        "runtime_seconds": total_runtime,
        "circuits": rows,
    }


def summarize_metrics(source_routed_metrics_path: Path, optimized_routed_metrics_path: Path, aer_path: Path, report: dict) -> dict:
    source = load_json(source_routed_metrics_path)
    optimized = load_json(optimized_routed_metrics_path)
    aer = load_json(aer_path)

    def total(payload: dict, key: str) -> float:
        return sum(float(row[key]) for row in payload["results"])

    summary = {
        "benchmark_id": "B1",
        "method": "heavyhex_routed_source_vs_b1_fixed_point_v0",
        "baseline_kind": "qiskit_heavy_hex_d3_level0_source_vs_b1_optimized",
        "optimization_level": report["optimization_level"],
        "physical_qubits": report["physical_qubits"],
        "coupling_edges": report["coupling_edges"],
        "circuit_count": source["circuit_count"],
        "aer_crosscheck_passed": aer["passed"],
        "aer_crosscheck_failed": aer["failed"],
        "aer_crosscheck_shots": aer["shots"],
        "aer_crosscheck_max_tvd": aer["max_total_variation_distance"],
        "aer_crosscheck_max_threshold": aer["max_threshold"],
    }
    for key in [
        "operation_count",
        "two_qubit_gate_count",
        "logical_depth",
        "hardware_weighted_error_exposure",
        "idle_layer_proxy",
    ]:
        short = "hardware_weighted_exposure" if key == "hardware_weighted_error_exposure" else key
        before_total = total(source, key)
        after_total = total(optimized, key)
        summary[f"{short}_source_routed"] = before_total
        summary[f"{short}_optimized_routed"] = after_total
        summary[f"{short}_delta"] = after_total - before_total
        summary[f"{short}_reduction_pct"] = (before_total - after_total) / before_total * 100 if before_total else 0.0
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--work-dir", type=Path, default=Path("results/b1_heavyhex_end_to_end_30_work"))
    parser.add_argument("--results-dir", type=Path, default=Path("results/b1_heavyhex_end_to_end_30"))
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--distance", type=int, default=3)
    parser.add_argument("--level", type=int, default=0)
    parser.add_argument("--aer-shots", type=int, default=2048)
    parser.add_argument("--aer-method", default="matrix_product_state")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    work_dir = root / args.work_dir
    results_dir = root / args.results_dir
    source_dir = work_dir / "00_source"
    optimized_dir = work_dir / "01_b1_optimized"
    source_routed_dir = work_dir / f"02_source_heavyhex_d{args.distance}_level{args.level}"
    optimized_routed_dir = work_dir / f"03_b1_heavyhex_d{args.distance}_level{args.level}"
    results_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    source_rows = copy_bundle(root, source_dir, source_index=0)
    optimized_rows = copy_bundle(root, optimized_dir, source_index=1)

    source_report = transpile_bundle(source_dir, source_routed_dir, args.level, ["u3", "cx", "measure"], args.distance)
    optimized_report = transpile_bundle(optimized_dir, optimized_routed_dir, args.level, ["u3", "cx", "measure"], args.distance)
    source_routed_metrics = results_dir / "source_routed_metrics.json"
    optimized_routed_metrics = results_dir / "b1_optimized_routed_metrics.json"
    aer_crosscheck = results_dir / "source_vs_b1_optimized_routed_aer_crosscheck.json"
    summary_path = results_dir / "heavyhex_end_to_end_summary.json"

    for input_dir, output_path in [
        (source_routed_dir, source_routed_metrics),
        (optimized_routed_dir, optimized_routed_metrics),
    ]:
        run(
            [
                sys.executable,
                "tools/b1_qasm_metrics.py",
                str(input_dir),
                "--profile",
                args.profile,
                "--pretty",
                "--output",
                str(output_path),
            ]
        )

    run(
        [
            sys.executable,
            "tools/b1_aer_measurement_crosscheck.py",
            str(source_dir),
            str(optimized_routed_dir),
            "--shots",
            str(args.aer_shots),
            "--method",
            args.aer_method,
            "--pretty",
            "--output",
            str(aer_crosscheck),
        ],
        check=False,
    )
    summary = summarize_metrics(source_routed_metrics, optimized_routed_metrics, aer_crosscheck, source_report)
    summary["source_input_count"] = len(source_rows)
    summary["optimized_input_count"] = len(optimized_rows)
    summary["source_routed_report"] = source_report
    summary["optimized_routed_report"] = optimized_report
    summary["source_routed_metrics"] = str(source_routed_metrics)
    summary["optimized_routed_metrics"] = str(optimized_routed_metrics)
    summary["aer_crosscheck_path"] = str(aer_crosscheck)
    summary["limits"] = [
        "This compares source circuits routed to heavy-hex against B1 fixed-point outputs routed to the same heavy-hex topology.",
        "The topology is Qiskit heavy-hex distance 3, not a calibrated backend noise model.",
        "Output equivalence is cross-checked by Qiskit Aer shots between source logical circuits and B1 optimized routed circuits.",
    ]
    summary_path.write_text(json.dumps(summary, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
