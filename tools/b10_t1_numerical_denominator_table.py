#!/usr/bin/env python3
"""Build a numerical denominator table for the B10-T1 explicit-I/O boundary."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as spla


BITS_PER_FLOAT_OUTPUT = 53
RTOL = 1e-8


def tridiagonal_spd(n: int, shift: float) -> sparse.csr_matrix:
    diagonal = np.full(n, 2.0 + shift)
    off = np.full(n - 1, -1.0)
    return sparse.diags([off, diagonal, off], offsets=[-1, 0, 1], format="csr")


def spd_condition_estimate(n: int, shift: float) -> float:
    lam_min = shift + 2.0 - 2.0 * math.cos(math.pi / (n + 1))
    lam_max = shift + 2.0 - 2.0 * math.cos(n * math.pi / (n + 1))
    return lam_max / lam_min


def run_cg_instance(n: int, shift: float) -> dict[str, Any]:
    matrix = tridiagonal_spd(n, shift)
    x_true = np.sin(np.linspace(0.2, 1.8, n)) + 0.1 * np.cos(np.linspace(0.0, 4.0, n))
    rhs = matrix @ x_true
    iterations = 0

    def count_iteration(_: np.ndarray) -> None:
        nonlocal iterations
        iterations += 1

    start = time.perf_counter()
    solution, info = spla.cg(matrix, rhs, rtol=RTOL, atol=0.0, maxiter=5000, callback=count_iteration)
    elapsed = time.perf_counter() - start
    residual_norm = float(np.linalg.norm(matrix @ solution - rhs) / np.linalg.norm(rhs))
    full_output_bits = n * BITS_PER_FLOAT_OUTPUT
    input_entries = int(matrix.nnz + n)
    explicit_io_floor = int(input_entries + full_output_bits)
    return {
        "family": "D1_explicit_spd_full_solution_cg",
        "solver": "cg",
        "n": n,
        "shape": [n, n],
        "nnz": int(matrix.nnz),
        "shift": shift,
        "condition_estimate": spd_condition_estimate(n, shift),
        "rtol": RTOL,
        "iterations": iterations,
        "solver_info": int(info),
        "relative_residual": residual_norm,
        "wall_time_seconds": elapsed,
        "matvec_equivalent_ops": int(iterations * matrix.nnz),
        "explicit_input_entries": input_entries,
        "full_output_bits": full_output_bits,
        "explicit_io_floor_units": explicit_io_floor,
        "boundary_interpretation": (
            "Full-vector output and explicit sparse input already impose an Omega(nnz(A)+n*bits) "
            "floor before any HHL-style subroutine claim can be counted end to end."
        ),
    }


def sparse_rectangular_system(n: int, seed: int) -> tuple[sparse.csr_matrix, np.ndarray]:
    rng = np.random.default_rng(seed)
    m = n + max(8, n // 8)
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    for col in range(n):
        rows.append(col)
        cols.append(col)
        data.append(2.0 + 0.1 * math.sin(col))
        if col + 1 < m:
            rows.append(col + 1)
            cols.append(col)
            data.append(-0.45 + 0.02 * math.cos(col))
        if col + 2 < m:
            rows.append(col + 2)
            cols.append(col)
            data.append(0.18)
    extra_count = max(n // 3, 12)
    extra_rows = rng.integers(0, m, size=extra_count)
    extra_cols = rng.integers(0, n, size=extra_count)
    extra_values = rng.normal(0.0, 0.025, size=extra_count)
    rows.extend(int(v) for v in extra_rows)
    cols.extend(int(v) for v in extra_cols)
    data.extend(float(v) for v in extra_values)
    matrix = sparse.coo_matrix((data, (rows, cols)), shape=(m, n)).tocsr()
    x_true = np.cos(np.linspace(0.1, 2.2, n))
    rhs = matrix @ x_true
    rhs += 1e-5 * rng.normal(0.0, 1.0, size=m)
    return matrix, rhs


def run_lsqr_instance(n: int, seed: int) -> dict[str, Any]:
    matrix, rhs = sparse_rectangular_system(n, seed)
    start = time.perf_counter()
    result = spla.lsqr(matrix, rhs, atol=RTOL, btol=RTOL, iter_lim=5000)
    elapsed = time.perf_counter() - start
    solution = result[0]
    iterations = int(result[2])
    residual_norm = float(np.linalg.norm(matrix @ solution - rhs) / np.linalg.norm(rhs))
    full_output_bits = n * BITS_PER_FLOAT_OUTPUT
    input_entries = int(matrix.nnz + matrix.shape[0])
    explicit_io_floor = int(input_entries + full_output_bits)
    return {
        "family": "D2_explicit_general_sparse_least_squares",
        "solver": "lsqr",
        "n": n,
        "shape": [int(matrix.shape[0]), int(matrix.shape[1])],
        "nnz": int(matrix.nnz),
        "seed": seed,
        "rtol": RTOL,
        "iterations": iterations,
        "solver_info": int(result[1]),
        "condition_estimate": float(result[6]),
        "relative_residual": residual_norm,
        "wall_time_seconds": elapsed,
        "matvec_equivalent_ops": int(iterations * matrix.nnz),
        "explicit_input_entries": input_entries,
        "full_output_bits": full_output_bits,
        "explicit_io_floor_units": explicit_io_floor,
        "boundary_interpretation": (
            "General sparse linear-system claims need a denominator such as LSQR; comparing "
            "a quantum oracle subroutine to an unstated classical baseline is not accepted."
        ),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_family: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_family.setdefault(row["family"], []).append(row)
    family_summary = {}
    for family, family_rows in by_family.items():
        family_summary[family] = {
            "instance_count": len(family_rows),
            "n_values": sorted({row["n"] for row in family_rows}),
            "max_relative_residual": max(row["relative_residual"] for row in family_rows),
            "median_iterations": float(np.median([row["iterations"] for row in family_rows])),
            "max_explicit_io_floor_units": max(row["explicit_io_floor_units"] for row in family_rows),
            "max_matvec_equivalent_ops": max(row["matvec_equivalent_ops"] for row in family_rows),
        }
    return {
        "family_count": len(by_family),
        "instance_count": len(rows),
        "cg_instance_count": sum(1 for row in rows if row["solver"] == "cg"),
        "lsqr_instance_count": sum(1 for row in rows if row["solver"] == "lsqr"),
        "max_relative_residual": max(row["relative_residual"] for row in rows),
        "families": family_summary,
    }


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "numerical_denominator_table_instantiated_not_quantum_speedup_claim":
        errors.append("status must remain a denominator table, not a quantum-speedup claim")
    if report.get("source_target_id") != "B10-T1":
        errors.append("source_target_id must be B10-T1")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("must explicitly avoid BQP/classical separation claims")
    summary = report.get("summary", {})
    if summary.get("family_count", 0) < 2:
        errors.append("at least two denominator families are required")
    if summary.get("cg_instance_count", 0) < 8:
        errors.append("at least eight CG instances are required")
    if summary.get("lsqr_instance_count", 0) < 4:
        errors.append("at least four LSQR instances are required")
    if summary.get("max_relative_residual", 1.0) > 1e-5:
        errors.append("maximum relative residual is too high for a denominator table")
    for row in report.get("rows", []):
        if row.get("iterations", 0) <= 0:
            errors.append(f"{row.get('family')} n={row.get('n')} has no recorded iterations")
        if row.get("explicit_io_floor_units", 0) <= row.get("nnz", 0):
            errors.append(f"{row.get('family')} n={row.get('n')} has invalid explicit I/O floor")
        if row.get("solver_info", 0) not in (0, 1, 2):
            errors.append(f"{row.get('family')} n={row.get('n')} solver_info={row.get('solver_info')} needs review")
    return errors


def build_report() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for n in [64, 128, 256, 512]:
        for shift in [1e-1, 1e-2, 1e-3]:
            rows.append(run_cg_instance(n, shift))
    for n in [64, 128, 256, 512]:
        rows.append(run_lsqr_instance(n, seed=17 + n))
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T1 numerical denominator table for explicit sparse linear systems",
        "version": "0.3",
        "last_updated": "2026-06-13",
        "status": "numerical_denominator_table_instantiated_not_quantum_speedup_claim",
        "method": "b10_t1_numerical_denominator_table_v0",
        "source_target_id": "B10-T1",
        "source_target_name": "linear_systems_data_loading_negative_boundary",
        "builds_on": "b10_t1_source_backed_boundaries_v0",
        "explicit_not_bqp_separation": True,
        "rtol": RTOL,
        "bits_per_float_output": BITS_PER_FLOAT_OUTPUT,
        "summary": summarize(rows),
        "rows": rows,
        "claim_boundary": {
            "now_supported": (
                "D1 and D2 denominator regimes have runnable sparse-CG/LSQR measurements "
                "with explicit input and full-output accounting."
            ),
            "still_not_supported": (
                "This table does not benchmark a quantum implementation, does not prove BQP/classical "
                "separation, and does not settle dequantized sampling-access regimes."
            ),
            "next_proof_pressure": (
                "Map one B3/B5 observable to a D5 linear-response denominator, or write the D4 "
                "sampling-access theorem note."
            ),
        },
    }
    report["validation_errors"] = validate(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# B10-T1 Numerical Denominator Table v0.3",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']} / {report['source_target_name']}",
        f"- Builds on: {report['builds_on']}",
        f"- Denominator families: {report['summary']['family_count']}",
        f"- Total instances: {report['summary']['instance_count']}",
        f"- CG instances: {report['summary']['cg_instance_count']}",
        f"- LSQR instances: {report['summary']['lsqr_instance_count']}",
        f"- Max relative residual: {report['summary']['max_relative_residual']:.3e}",
        f"- Validation errors: {len(report['validation_errors'])}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        "",
        "## Interpretation",
        "",
        "- This is the first runnable denominator table for B10-T1, not a quantum-speedup benchmark.",
        "- D1 covers explicit sparse SPD full-vector output with conjugate gradient.",
        "- D2 covers explicit general sparse least-squares style instances with LSQR.",
        "- The explicit-I/O floor records sparse input entries plus full-vector output bits; any HHL-style end-to-end claim must charge those terms before comparing subroutine complexity.",
        "",
        "## Family Summary",
        "",
        "| Family | Instances | n values | Median iterations | Max residual | Max explicit-I/O floor | Max matvec-equivalent ops |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for family, item in report["summary"]["families"].items():
        lines.append(
            "| {family} | {count} | {n_values} | {median:.1f} | {residual:.3e} | {floor} | {ops} |".format(
                family=family,
                count=item["instance_count"],
                n_values=",".join(str(v) for v in item["n_values"]),
                median=item["median_iterations"],
                residual=item["max_relative_residual"],
                floor=item["max_explicit_io_floor_units"],
                ops=item["max_matvec_equivalent_ops"],
            )
        )
    lines.extend(
        [
            "",
            "## Instance Table",
            "",
            "| Solver | n | shape | nnz | condition estimate | iterations | residual | explicit-I/O floor | matvec-equivalent ops |",
            "|---|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["rows"]:
        lines.append(
            "| {solver} | {n} | {shape} | {nnz} | {cond:.3e} | {it} | {res:.3e} | {floor} | {ops} |".format(
                solver=row["solver"],
                n=row["n"],
                shape="x".join(str(v) for v in row["shape"]),
                nnz=row["nnz"],
                cond=row["condition_estimate"],
                it=row["iterations"],
                res=row["relative_residual"],
                floor=row["explicit_io_floor_units"],
                ops=row["matvec_equivalent_ops"],
            )
        )
    lines.extend(["", "## Claim Boundary", ""])
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t1_numerical_denominator_table_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t1_numerical_denominator_table.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "family_count": report["summary"]["family_count"],
                    "instance_count": report["summary"]["instance_count"],
                    "cg_instance_count": report["summary"]["cg_instance_count"],
                    "lsqr_instance_count": report["summary"]["lsqr_instance_count"],
                    "max_relative_residual": report["summary"]["max_relative_residual"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
