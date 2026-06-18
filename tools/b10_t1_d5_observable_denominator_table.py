#!/usr/bin/env python3
"""Build a B10-T1 D5 observable-denominator table on B5 Hubbard response tasks."""

from __future__ import annotations

import argparse
import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as spla


RTOL = 1e-8
ETA = 0.25
BITS_PER_OBSERVABLE = 53


def bitstrings_with_weight(width: int, weight: int) -> list[int]:
    return [bits for bits in range(1 << width) if bits.bit_count() == weight]


def hop(bits: int, src: int, dst: int) -> tuple[int, int] | None:
    if not (bits >> src) & 1 or (bits >> dst) & 1:
        return None
    lo, hi = sorted((src, dst))
    parity = ((bits >> (lo + 1)) & ((1 << (hi - lo - 1)) - 1)).bit_count()
    sign = -1 if parity % 2 else 1
    new_bits = bits ^ (1 << src) ^ (1 << dst)
    return new_bits, sign


@lru_cache(maxsize=None)
def basis_states(sites: int, n_up: int, n_down: int) -> tuple[tuple[int, int], ...]:
    up_states = bitstrings_with_weight(sites, n_up)
    down_states = bitstrings_with_weight(sites, n_down)
    return tuple((up, down) for up in up_states for down in down_states)


def hubbard_hamiltonian(sites: int, n_up: int, n_down: int, u_value: float, t_value: float) -> sparse.csr_matrix:
    basis = basis_states(sites, n_up, n_down)
    index = {state: idx for idx, state in enumerate(basis)}
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    neighbors = [(site, site + 1) for site in range(sites - 1)]

    for col, (up_bits, down_bits) in enumerate(basis):
        rows.append(col)
        cols.append(col)
        data.append(u_value * (up_bits & down_bits).bit_count())
        for src, dst in neighbors:
            for a, b in [(src, dst), (dst, src)]:
                up_hop = hop(up_bits, a, b)
                if up_hop is not None:
                    new_up, sign = up_hop
                    rows.append(index[(new_up, down_bits)])
                    cols.append(col)
                    data.append(-t_value * sign)
                down_hop = hop(down_bits, a, b)
                if down_hop is not None:
                    new_down, sign = down_hop
                    rows.append(index[(up_bits, new_down)])
                    cols.append(col)
                    data.append(-t_value * sign)
    return sparse.coo_matrix((data, (rows, cols)), shape=(len(basis), len(basis))).tocsr()


def local_density_diagonal(sites: int, n_up: int, n_down: int, site: int) -> np.ndarray:
    values = []
    for up_bits, down_bits in basis_states(sites, n_up, n_down):
        values.append(float(((up_bits >> site) & 1) + ((down_bits >> site) & 1)))
    return np.asarray(values, dtype=np.float64)


def solve_density_response(sites: int, u_over_t: float, t_value: float) -> dict[str, Any]:
    if sites % 2:
        raise ValueError("half-filled D5 table requires an even site count")
    n_up = sites // 2
    n_down = sites // 2
    matrix = hubbard_hamiltonian(sites, n_up, n_down, u_over_t * t_value, t_value)
    dim = matrix.shape[0]
    started = time.perf_counter()
    energy, vecs = spla.eigsh(matrix, k=1, which="SA", tol=1e-10)
    ground_energy = float(energy[0])
    psi0 = vecs[:, 0]
    density = local_density_diagonal(sites, n_up, n_down, site=sites // 2)
    density_mean = float(np.dot(psi0, density * psi0))
    source = (density - density_mean) * psi0
    source_norm = float(np.linalg.norm(source))
    if source_norm == 0.0:
        raise ValueError("centered density source has zero norm")
    operator = matrix - ground_energy * sparse.identity(dim, format="csr")
    operator = operator + ETA * sparse.identity(dim, format="csr")
    iterations = 0

    def count_iteration(_: np.ndarray) -> None:
        nonlocal iterations
        iterations += 1

    solution, info = spla.cg(operator, source, rtol=RTOL, atol=0.0, maxiter=5000, callback=count_iteration)
    elapsed = time.perf_counter() - started
    residual = float(np.linalg.norm(operator @ solution - source) / source_norm)
    susceptibility = float(np.dot(source, solution))
    observable_bits = BITS_PER_OBSERVABLE
    explicit_input_entries = int(matrix.nnz + dim + sites)
    explicit_io_floor = int(explicit_input_entries + observable_bits)
    return {
        "family": "D5_b3_b5_observable_linear_response",
        "source_benchmark": "B5",
        "model": "one_dimensional_fermi_hubbard_half_filled_density_response",
        "solver": "cg_shifted_hubbard_response",
        "sites": sites,
        "n_up": n_up,
        "n_down": n_down,
        "u_over_t": u_over_t,
        "t": t_value,
        "eta": ETA,
        "hilbert_dimension": int(dim),
        "hamiltonian_nnz": int(matrix.nnz),
        "ground_energy": ground_energy,
        "density_site": sites // 2,
        "density_mean": density_mean,
        "source_norm": source_norm,
        "susceptibility_proxy": susceptibility,
        "rtol": RTOL,
        "iterations": iterations,
        "solver_info": int(info),
        "relative_residual": residual,
        "wall_time_seconds": elapsed,
        "matvec_equivalent_ops": int(iterations * matrix.nnz),
        "explicit_input_entries": explicit_input_entries,
        "observable_output_bits": observable_bits,
        "explicit_io_floor_units": explicit_io_floor,
        "boundary_interpretation": (
            "This D5 row maps a B5 Hubbard observable to a shifted linear-response system; "
            "any quantum observable-estimation claim must compare against this domain "
            "denominator at the same eta, observable, and residual target."
        ),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "family_count": len({row["family"] for row in rows}),
        "source_benchmark_count": len({row["source_benchmark"] for row in rows}),
        "instance_count": len(rows),
        "site_values": sorted({row["sites"] for row in rows}),
        "u_over_t_values": sorted({row["u_over_t"] for row in rows}),
        "max_hilbert_dimension": max(row["hilbert_dimension"] for row in rows),
        "max_hamiltonian_nnz": max(row["hamiltonian_nnz"] for row in rows),
        "max_relative_residual": max(row["relative_residual"] for row in rows),
        "median_iterations": float(np.median([row["iterations"] for row in rows])),
        "max_explicit_io_floor_units": max(row["explicit_io_floor_units"] for row in rows),
        "max_matvec_equivalent_ops": max(row["matvec_equivalent_ops"] for row in rows),
    }


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "d5_observable_denominator_table_instantiated_not_quantum_speedup_claim":
        errors.append("status must remain a D5 denominator table, not a quantum-speedup claim")
    if report.get("source_target_id") != "B10-T1":
        errors.append("source_target_id must be B10-T1")
    if report.get("dependency_benchmark") != "B5":
        errors.append("D5 table must be tied to B5 for this version")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("must explicitly avoid BQP/classical separation claims")
    summary = report.get("summary", {})
    if summary.get("instance_count", 0) < 9:
        errors.append("at least nine B5 response instances are required")
    if summary.get("max_hilbert_dimension", 0) < 1000:
        errors.append("D5 table should include a nontrivial Hilbert dimension")
    if summary.get("max_relative_residual", 1.0) > 1e-6:
        errors.append("maximum relative residual is too high for the D5 denominator table")
    for row in report.get("rows", []):
        if row.get("solver_info") != 0:
            errors.append(f"sites={row.get('sites')} U/t={row.get('u_over_t')} solver_info={row.get('solver_info')}")
        if row.get("iterations", 0) <= 0:
            errors.append(f"sites={row.get('sites')} U/t={row.get('u_over_t')} has no CG iterations")
        if row.get("observable_output_bits") != BITS_PER_OBSERVABLE:
            errors.append(f"sites={row.get('sites')} U/t={row.get('u_over_t')} has wrong observable bit accounting")
    return errors


def build_report() -> dict[str, Any]:
    rows = []
    for sites in [4, 6, 8]:
        for u_over_t in [2.0, 4.0, 8.0]:
            rows.append(solve_density_response(sites, u_over_t, t_value=1.0))
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T1 D5 observable denominator table for B5 Hubbard response",
        "version": "0.4",
        "last_updated": "2026-06-13",
        "status": "d5_observable_denominator_table_instantiated_not_quantum_speedup_claim",
        "method": "b10_t1_d5_observable_denominator_table_v0",
        "source_target_id": "B10-T1",
        "source_target_name": "linear_systems_data_loading_negative_boundary",
        "dependency_benchmark": "B5",
        "builds_on": "b10_t1_numerical_denominator_table_v0",
        "explicit_not_bqp_separation": True,
        "summary": summarize(rows),
        "rows": rows,
        "claim_boundary": {
            "now_supported": (
                "D5 has a concrete B5 Hubbard density-response denominator with explicit "
                "Hamiltonian input, observable output, residual target, and CG iteration accounting."
            ),
            "still_not_supported": (
                "This is not a quantum implementation, not a BQP/classical separation, and not "
                "evidence of a B5 accuracy-per-resource improvement."
            ),
            "next_proof_pressure": (
                "Compare a candidate quantum impurity/response subroutine against this D5 table, "
                "or extend D5 from 1D Hubbard response to B3 molecular reaction observables."
            ),
        },
    }
    report["validation_errors"] = validate(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# B10-T1 D5 Observable Denominator Table v0.4",
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
        f"- Instances: {summary['instance_count']}",
        f"- Sites: {summary['site_values']}",
        f"- U/t values: {summary['u_over_t_values']}",
        f"- Max Hilbert dimension: {summary['max_hilbert_dimension']}",
        f"- Max Hamiltonian nnz: {summary['max_hamiltonian_nnz']}",
        f"- Max relative residual: {summary['max_relative_residual']:.3e}",
        f"- Median CG iterations: {summary['median_iterations']:.1f}",
        f"- Validation errors: {len(report['validation_errors'])}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        "",
        "## Interpretation",
        "",
        "- This table maps B10-T1 D5 to a concrete B5 observable task.",
        "- The observable is a local density-response proxy in a half-filled 1D Hubbard model.",
        "- The denominator solves `(H - E0 + eta I) x = (n_i - <n_i>) |psi0>` with classical CG.",
        "- Only one scalar observable is read out, so the table separates observable-output accounting from full-vector readout.",
        "- It is a classical denominator and claim-boundary artifact, not a quantum-speedup result.",
        "",
        "## Instance Table",
        "",
        "| sites | U/t | dim | nnz | density mean | susceptibility proxy | iterations | residual | explicit-I/O floor | matvec-equivalent ops |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {sites} | {u:.1f} | {dim} | {nnz} | {mean:.6f} | {sus:.6f} | {it} | {res:.3e} | {floor} | {ops} |".format(
                sites=row["sites"],
                u=row["u_over_t"],
                dim=row["hilbert_dimension"],
                nnz=row["hamiltonian_nnz"],
                mean=row["density_mean"],
                sus=row["susceptibility_proxy"],
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
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t1_d5_observable_denominator_table_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t1_d5_observable_denominator_table.md"))
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
                    "instance_count": report["summary"]["instance_count"],
                    "max_hilbert_dimension": report["summary"]["max_hilbert_dimension"],
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
