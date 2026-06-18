#!/usr/bin/env python3
"""Build a B10-T1 D5 denominator table for B3 molecular observable proxies."""

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


RTOL = 1e-8
BITS_PER_OBSERVABLE = 53


def molecular_response_matrix(row: dict[str, Any], precision: float) -> sparse.csr_matrix:
    spin_orbitals = int(row["spin_orbitals"])
    one_terms = int(row["one_body_spin_terms"])
    two_terms = int(row["two_body_spin_terms"])
    lambda_proxy = float(row["lambda_one_body_proxy"] + row["lambda_two_body_proxy"])
    dimension = max(64, 8 * spin_orbitals)
    grid = np.arange(dimension, dtype=np.float64)
    diagonal = 1.0 + precision + lambda_proxy / max(dimension, 1)
    diagonal += 0.01 * (1.0 + np.sin((grid + 1.0) / max(spin_orbitals, 1)))
    off1 = -0.25 * np.ones(dimension - 1)
    off2 = -0.05 * np.ones(dimension - 2)
    matrix = sparse.diags([off2, off1, diagonal, off1, off2], [-2, -1, 0, 1, 2], format="lil")
    stride = max(3, dimension // max(4, min(dimension, spin_orbitals)))
    coupling_scale = 0.001 * math.log1p(one_terms + two_terms)
    for col in range(0, dimension, stride):
        row_idx = (col + spin_orbitals + 1) % dimension
        if row_idx != col:
            matrix[row_idx, col] = matrix[row_idx, col] - coupling_scale
            matrix[col, row_idx] = matrix[col, row_idx] - coupling_scale
    return matrix.tocsr()


def observable_source(row: dict[str, Any], dimension: int) -> np.ndarray:
    electrons = int(row["electrons"])
    spin_orbitals = int(row["spin_orbitals"])
    observable_fraction = float(row["resource_estimates"]["observable_first"]["observable_fraction"])
    width = max(1, math.ceil(dimension * observable_fraction))
    center = min(dimension - 1, max(0, electrons * dimension // max(2 * spin_orbitals, 1)))
    grid = np.arange(dimension)
    envelope = np.exp(-((grid - center) ** 2) / max(1.0, 2.0 * width**2))
    alternating = np.where(grid % 2 == 0, 1.0, -1.0)
    source = envelope * alternating
    source -= np.mean(source)
    norm = np.linalg.norm(source)
    if norm == 0:
        raise ValueError("observable source has zero norm")
    return source / norm


def run_molecule(row: dict[str, Any], precision: float) -> dict[str, Any]:
    matrix = molecular_response_matrix(row, precision)
    source = observable_source(row, matrix.shape[0])
    iterations = 0

    def count_iteration(_: np.ndarray) -> None:
        nonlocal iterations
        iterations += 1

    started = time.perf_counter()
    solution, info = spla.cg(matrix, source, rtol=RTOL, atol=0.0, maxiter=5000, callback=count_iteration)
    elapsed = time.perf_counter() - started
    residual = float(np.linalg.norm(matrix @ solution - source) / np.linalg.norm(source))
    observable_estimate = float(np.dot(source, solution))
    observable = row["resource_estimates"]["observable_first"]
    full = row["resource_estimates"]["full_phase_estimation"]
    explicit_input_entries = int(matrix.nnz + row["one_body_integral_nonzero"] + row["two_body_integral_nonzero"])
    explicit_io_floor = explicit_input_entries + BITS_PER_OBSERVABLE
    return {
        "family": "D5_b3_b5_observable_linear_response",
        "source_benchmark": "B3",
        "model": "small_molecule_observable_response_proxy",
        "molecule": row["molecule"],
        "basis": row["basis"],
        "solver": "cg_molecular_response_proxy",
        "spin_orbitals": int(row["spin_orbitals"]),
        "electrons": int(row["electrons"]),
        "matrix_dimension": int(matrix.shape[0]),
        "matrix_nnz": int(matrix.nnz),
        "precision_hartree": precision,
        "observable_fraction": float(observable["observable_fraction"]),
        "lambda_proxy": float(row["lambda_one_body_proxy"] + row["lambda_two_body_proxy"]),
        "full_t_count_proxy": int(full["t_count_proxy"]),
        "observable_t_count_proxy": int(observable["t_count_proxy"]),
        "proxy_t_count_reduction_factor": float(row["resource_estimates"]["proxy_t_count_reduction_factor"]),
        "rtol": RTOL,
        "iterations": iterations,
        "solver_info": int(info),
        "relative_residual": residual,
        "observable_response_proxy": observable_estimate,
        "wall_time_seconds": elapsed,
        "matvec_equivalent_ops": int(iterations * matrix.nnz),
        "explicit_input_entries": explicit_input_entries,
        "observable_output_bits": BITS_PER_OBSERVABLE,
        "explicit_io_floor_units": int(explicit_io_floor),
        "boundary_interpretation": (
            "This B3 D5 row turns an observable-first molecular resource proxy into a "
            "classical linear-response denominator; future quantum chemistry claims must "
            "state whether they beat this denominator after charging molecular integrals, "
            "state preparation, and observable readout."
        ),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "family_count": len({row["family"] for row in rows}),
        "source_benchmark_count": len({row["source_benchmark"] for row in rows}),
        "instance_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "molecules": [row["molecule"] for row in rows],
        "max_matrix_dimension": max(row["matrix_dimension"] for row in rows),
        "max_matrix_nnz": max(row["matrix_nnz"] for row in rows),
        "max_relative_residual": max(row["relative_residual"] for row in rows),
        "median_iterations": float(np.median([row["iterations"] for row in rows])),
        "max_explicit_io_floor_units": max(row["explicit_io_floor_units"] for row in rows),
        "max_matvec_equivalent_ops": max(row["matvec_equivalent_ops"] for row in rows),
        "proxy_t_count_reduction_range": [
            min(row["proxy_t_count_reduction_factor"] for row in rows),
            max(row["proxy_t_count_reduction_factor"] for row in rows),
        ],
    }


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "b3_d5_molecular_observable_denominator_proxy_not_reaction_solution":
        errors.append("status must remain a B3 D5 denominator proxy, not a reaction solution")
    if report.get("source_target_id") != "B10-T1":
        errors.append("source_target_id must be B10-T1")
    if report.get("dependency_benchmark") != "B3":
        errors.append("B3 molecular table must declare dependency_benchmark=B3")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("must explicitly avoid BQP/classical separation claims")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("B3 D5 proxy should cover the four existing B3 calibration molecules")
    if summary.get("max_matrix_dimension", 0) < 128:
        errors.append("B3 D5 proxy should include a nontrivial molecular response matrix")
    if summary.get("max_relative_residual", 1.0) > 1e-6:
        errors.append("maximum relative residual is too high for the B3 D5 proxy")
    for row in report.get("rows", []):
        if row.get("solver_info") != 0:
            errors.append(f"{row.get('molecule')} solver_info={row.get('solver_info')}")
        if row.get("iterations", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no CG iterations")
        if row.get("observable_output_bits") != BITS_PER_OBSERVABLE:
            errors.append(f"{row.get('molecule')} has wrong observable output bit accounting")
    return errors


def build_report(b3_result_path: Path) -> dict[str, Any]:
    b3_payload = json.loads(b3_result_path.read_text(encoding="utf-8"))
    rows = [run_molecule(row, precision=float(b3_payload["precision_hartree"])) for row in b3_payload["results"]]
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T1 D5 molecular observable denominator proxy for B3",
        "version": "0.5",
        "last_updated": "2026-06-13",
        "status": "b3_d5_molecular_observable_denominator_proxy_not_reaction_solution",
        "method": "b10_t1_d5_b3_molecular_observable_table_v0",
        "source_target_id": "B10-T1",
        "source_target_name": "linear_systems_data_loading_negative_boundary",
        "dependency_benchmark": "B3",
        "builds_on": "b10_t1_d5_observable_denominator_table_v0",
        "source_result": str(b3_result_path),
        "explicit_not_bqp_separation": True,
        "summary": summarize(rows),
        "rows": rows,
        "claim_boundary": {
            "now_supported": (
                "B10-T1 D5 now has a B3 molecular observable denominator proxy tied to the "
                "existing PySCF calibration resource estimates."
            ),
            "still_not_supported": (
                "This is not a reaction-coordinate simulation, not a quantum implementation, "
                "not a chemistry accuracy claim, and not a BQP/classical separation."
            ),
            "next_proof_pressure": (
                "Replace the proxy response matrix with an OpenFermion/PySCF Hamiltonian-derived "
                "observable along a reaction coordinate, then compare against coupled-cluster or selected-CI references."
            ),
        },
    }
    report["validation_errors"] = validate(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# B10-T1 D5 B3 Molecular Observable Denominator Proxy v0.5",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']} / {report['source_target_name']}",
        f"- Dependency benchmark: {report['dependency_benchmark']}",
        f"- Builds on: {report['builds_on']}",
        f"- Source result: {report['source_result']}",
        f"- Instances: {summary['instance_count']}",
        f"- Molecules: {summary['molecules']}",
        f"- Max matrix dimension: {summary['max_matrix_dimension']}",
        f"- Max matrix nnz: {summary['max_matrix_nnz']}",
        f"- Max relative residual: {summary['max_relative_residual']:.3e}",
        f"- Median CG iterations: {summary['median_iterations']:.1f}",
        f"- Validation errors: {len(report['validation_errors'])}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        "",
        "## Interpretation",
        "",
        "- This table extends B10-T1 D5 from B5 Hubbard response to the B3 molecular calibration set.",
        "- It uses the existing PySCF resource-proxy output and builds a deterministic molecular response denominator proxy.",
        "- The table is a claim-boundary artifact for observable-first chemistry claims, not a reaction-dynamics solution.",
        "- The next serious step is replacing this proxy matrix with a Hamiltonian-derived observable along a reaction coordinate.",
        "",
        "## Instance Table",
        "",
        "| molecule | spin orbitals | matrix dim | nnz | observable fraction | iterations | residual | observable response | explicit-I/O floor | observable/full T proxy |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {mol} | {so} | {dim} | {nnz} | {frac:.2f} | {it} | {res:.3e} | {obs:.6e} | {floor} | {ratio:.3f} |".format(
                mol=row["molecule"],
                so=row["spin_orbitals"],
                dim=row["matrix_dimension"],
                nnz=row["matrix_nnz"],
                frac=row["observable_fraction"],
                it=row["iterations"],
                res=row["relative_residual"],
                obs=row["observable_response_proxy"],
                floor=row["explicit_io_floor_units"],
                ratio=row["observable_t_count_proxy"] / row["full_t_count_proxy"],
            )
        )
    lines.extend(["", "## Claim Boundary", ""])
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--b3-result", type=Path, default=Path("results/B3_pyscf_resource_estimate_v0.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t1_d5_b3_molecular_observable_table_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t1_d5_b3_molecular_observable_table.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.b3_result)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "instance_count": report["summary"]["instance_count"],
                    "max_matrix_dimension": report["summary"]["max_matrix_dimension"],
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
