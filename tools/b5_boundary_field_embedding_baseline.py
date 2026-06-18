#!/usr/bin/env python3
"""Build a B5 boundary-field embedding baseline for Hubbard response tasks."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse
from scipy.sparse import linalg as spla

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from b10_t1_d5_observable_denominator_table import (  # noqa: E402
    ETA,
    RTOL,
    basis_states,
    hop,
    local_density_diagonal,
)


METHOD = "b5_boundary_field_response_embedding_baseline_v0"
STATUS = "boundary_field_response_embedding_denominator_not_quantum_advantage_claim"
FIELD_GRID = (-0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def hubbard_hamiltonian_with_edge_field(
    sites: int,
    n_up: int,
    n_down: int,
    u_value: float,
    t_value: float,
    edge_field: float,
) -> sparse.csr_matrix:
    basis = basis_states(sites, n_up, n_down)
    index = {state: idx for idx, state in enumerate(basis)}
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    neighbors = [(site, site + 1) for site in range(sites - 1)]

    for col, (up_bits, down_bits) in enumerate(basis):
        double_occupancy = (up_bits & down_bits).bit_count()
        edge_occupancy = (
            ((up_bits >> 0) & 1)
            + ((down_bits >> 0) & 1)
            + ((up_bits >> (sites - 1)) & 1)
            + ((down_bits >> (sites - 1)) & 1)
        )
        rows.append(col)
        cols.append(col)
        data.append(u_value * double_occupancy + edge_field * edge_occupancy)
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


def lowest_eigenpair(matrix: sparse.csr_matrix) -> tuple[float, np.ndarray]:
    dim = matrix.shape[0]
    if dim <= 4:
        values, vectors = np.linalg.eigh(matrix.toarray())
        return float(values[0]), np.asarray(vectors[:, 0], dtype=np.float64)
    values, vectors = spla.eigsh(matrix, k=1, which="SA", tol=1e-10)
    return float(values[0]), np.asarray(vectors[:, 0], dtype=np.float64)


def solve_cluster_response(
    sites: int,
    u_over_t: float,
    t_value: float,
    edge_field: float,
) -> dict[str, Any]:
    if sites % 2:
        raise ValueError("cluster response requires an even site count")
    n_up = sites // 2
    n_down = sites // 2
    matrix = hubbard_hamiltonian_with_edge_field(
        sites=sites,
        n_up=n_up,
        n_down=n_down,
        u_value=u_over_t * t_value,
        t_value=t_value,
        edge_field=edge_field,
    )
    ground_energy, psi0 = lowest_eigenpair(matrix)
    density_site = sites // 2
    density = local_density_diagonal(sites, n_up, n_down, density_site)
    density_mean = float(np.dot(psi0, density * psi0))
    source = (density - density_mean) * psi0
    source_norm = float(np.linalg.norm(source))
    if source_norm == 0.0:
        return {
            "sites": sites,
            "edge_field": edge_field,
            "hilbert_dimension": int(matrix.shape[0]),
            "hamiltonian_nnz": int(matrix.nnz),
            "ground_energy": ground_energy,
            "density_site": density_site,
            "density_mean": density_mean,
            "source_norm": source_norm,
            "susceptibility_proxy": 0.0,
            "relative_residual": 0.0,
            "solver_info": 0,
            "iterations": 0,
        }

    operator = matrix - ground_energy * sparse.identity(matrix.shape[0], format="csr")
    operator = operator + ETA * sparse.identity(matrix.shape[0], format="csr")
    iterations = 0

    def count_iteration(_: np.ndarray) -> None:
        nonlocal iterations
        iterations += 1

    solution, info = spla.cg(
        operator,
        source,
        rtol=RTOL,
        atol=0.0,
        maxiter=5000,
        callback=count_iteration,
    )
    residual = float(np.linalg.norm(operator @ solution - source) / source_norm)
    susceptibility = float(np.dot(source, solution))
    return {
        "sites": sites,
        "edge_field": edge_field,
        "hilbert_dimension": int(matrix.shape[0]),
        "hamiltonian_nnz": int(matrix.nnz),
        "ground_energy": ground_energy,
        "density_site": density_site,
        "density_mean": density_mean,
        "source_norm": source_norm,
        "susceptibility_proxy": susceptibility,
        "relative_residual": residual,
        "solver_info": int(info),
        "iterations": iterations,
    }


def cluster_partition(sites: int) -> list[int]:
    clusters: list[int] = []
    remaining = sites
    while remaining >= 4:
        clusters.append(4)
        remaining -= 4
    if remaining:
        clusters.append(remaining)
    return clusters


def embedded_response_for_field(
    full_sites: int,
    u_over_t: float,
    t_value: float,
    edge_field: float,
) -> dict[str, Any]:
    clusters = cluster_partition(full_sites)
    cluster_rows = [solve_cluster_response(cluster, u_over_t, t_value, edge_field) for cluster in clusters]
    susceptibility = float(
        sum(cluster * row["susceptibility_proxy"] for cluster, row in zip(clusters, cluster_rows)) / full_sites
    )
    max_residual = max(row["relative_residual"] for row in cluster_rows)
    max_dim = max(row["hilbert_dimension"] for row in cluster_rows)
    return {
        "clusters": clusters,
        "edge_field": edge_field,
        "embedded_susceptibility_proxy": susceptibility,
        "cluster_rows": cluster_rows,
        "max_cluster_relative_residual": max_residual,
        "max_cluster_hilbert_dimension": max_dim,
    }


def best_energy_proxy_row(energy_source: dict[str, Any], sites: int, u_over_t: float) -> dict[str, Any] | None:
    candidates = [
        row
        for row in energy_source.get("results", [])
        if int(row.get("sites")) == sites and math.isclose(float(row.get("u_over_t")), float(u_over_t))
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda row: float(row["energy_error_per_site"]))


def build_rows(d5_source: dict[str, Any], energy_source: dict[str, Any], field_grid: tuple[float, ...]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for d5_row in d5_source.get("rows", []):
        sites = int(d5_row["sites"])
        u_over_t = float(d5_row["u_over_t"])
        exact_susceptibility = float(d5_row["susceptibility_proxy"])
        field_candidates = []
        for edge_field in field_grid:
            candidate = embedded_response_for_field(
                full_sites=sites,
                u_over_t=u_over_t,
                t_value=float(d5_row.get("t", 1.0)),
                edge_field=edge_field,
            )
            absolute_error = abs(candidate["embedded_susceptibility_proxy"] - exact_susceptibility)
            relative_error = absolute_error / max(abs(exact_susceptibility), 1e-12)
            candidate.update(
                {
                    "absolute_response_error": absolute_error,
                    "relative_response_error": relative_error,
                }
            )
            field_candidates.append(candidate)

        best = min(field_candidates, key=lambda item: (item["relative_response_error"], abs(item["edge_field"])))
        energy_proxy = best_energy_proxy_row(energy_source, sites, u_over_t)
        rows.append(
            {
                "model": "one_dimensional_fermi_hubbard_half_filled_density_response",
                "sites": sites,
                "u_over_t": u_over_t,
                "t": float(d5_row.get("t", 1.0)),
                "eta": float(d5_row.get("eta", ETA)),
                "exact_d5_susceptibility_proxy": exact_susceptibility,
                "exact_d5_hilbert_dimension": int(d5_row["hilbert_dimension"]),
                "exact_d5_relative_residual": float(d5_row["relative_residual"]),
                "embedding_partition": best["clusters"],
                "best_oracle_edge_field": best["edge_field"],
                "boundary_field_grid": list(field_grid),
                "boundary_field_grid_count": len(field_grid),
                "embedded_susceptibility_proxy": best["embedded_susceptibility_proxy"],
                "absolute_response_error": best["absolute_response_error"],
                "relative_response_error": best["relative_response_error"],
                "max_cluster_hilbert_dimension": best["max_cluster_hilbert_dimension"],
                "max_cluster_relative_residual": best["max_cluster_relative_residual"],
                "best_field_cluster_rows": best["cluster_rows"],
                "all_field_response_errors": [
                    {
                        "edge_field": item["edge_field"],
                        "embedded_susceptibility_proxy": item["embedded_susceptibility_proxy"],
                        "relative_response_error": item["relative_response_error"],
                        "absolute_response_error": item["absolute_response_error"],
                    }
                    for item in field_candidates
                ],
                "best_cluster_product_energy_error_per_site": (
                    float(energy_proxy["energy_error_per_site"]) if energy_proxy else None
                ),
                "best_cluster_product_cluster_size": int(energy_proxy["cluster_size"]) if energy_proxy else None,
                "candidate_quantum_response_beats_boundary_field": False,
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]], field_grid: tuple[float, ...]) -> dict[str, Any]:
    rel_errors = [float(row["relative_response_error"]) for row in rows]
    energy_errors = [
        float(row["best_cluster_product_energy_error_per_site"])
        for row in rows
        if row["best_cluster_product_energy_error_per_site"] is not None
    ]
    return {
        "instance_count": len(rows),
        "site_values": sorted({row["sites"] for row in rows}),
        "u_over_t_values": sorted({row["u_over_t"] for row in rows}),
        "boundary_field_grid": list(field_grid),
        "boundary_field_grid_count": len(field_grid),
        "mean_relative_response_error": float(np.mean(rel_errors)),
        "median_relative_response_error": float(np.median(rel_errors)),
        "max_relative_response_error": float(np.max(rel_errors)),
        "zero_error_instance_count": sum(error <= 1e-10 for error in rel_errors),
        "mean_best_cluster_product_energy_error_per_site": float(np.mean(energy_errors)),
        "max_best_cluster_product_energy_error_per_site": float(np.max(energy_errors)),
        "max_exact_d5_hilbert_dimension": max(row["exact_d5_hilbert_dimension"] for row in rows),
        "max_cluster_hilbert_dimension": max(row["max_cluster_hilbert_dimension"] for row in rows),
        "quantum_response_win_claimed": False,
        "accuracy_per_resource_win_claimed": False,
        "oracle_tuned_boundary_field": True,
    }


def validate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status must remain a boundary-field denominator, not an advantage claim")
    if report.get("benchmark_id") != "B5":
        errors.append("benchmark_id must be B5")
    if report.get("dependency_b10_table") != "b10_t1_d5_observable_denominator_table_v0":
        errors.append("B5 boundary-field baseline must depend on the B10 D5 observable table")
    if report.get("explicit_not_quantum_advantage") is not True:
        errors.append("report must explicitly avoid quantum-advantage claims")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 9:
        errors.append("boundary-field response baseline must cover the 9 D5 B5 rows")
    if summary.get("boundary_field_grid_count", 0) < 7:
        errors.append("boundary-field grid must contain at least seven candidate fields")
    if summary.get("quantum_response_win_claimed") is not False:
        errors.append("quantum response win must not be claimed")
    if summary.get("accuracy_per_resource_win_claimed") is not False:
        errors.append("accuracy-per-resource win must not be claimed")
    if summary.get("oracle_tuned_boundary_field") is not True:
        errors.append("baseline must disclose oracle tuning")
    for row in report.get("rows", []):
        if not math.isfinite(float(row.get("relative_response_error", math.inf))):
            errors.append(f"non-finite response error for sites={row.get('sites')} U/t={row.get('u_over_t')}")
        if row.get("candidate_quantum_response_beats_boundary_field") is not False:
            errors.append(f"row claims a quantum win for sites={row.get('sites')} U/t={row.get('u_over_t')}")
        if float(row.get("max_cluster_relative_residual", 1.0)) > 1e-6:
            errors.append(f"cluster response residual too high for sites={row.get('sites')} U/t={row.get('u_over_t')}")
        if int(row.get("boundary_field_grid_count", 0)) != summary.get("boundary_field_grid_count"):
            errors.append(f"field-grid count mismatch for sites={row.get('sites')} U/t={row.get('u_over_t')}")
    return errors


def build_report(d5_source_path: Path, energy_source_path: Path, field_grid: tuple[float, ...]) -> dict[str, Any]:
    started = time.perf_counter()
    d5_source = load_json(d5_source_path)
    energy_source = load_json(energy_source_path)
    rows = build_rows(d5_source, energy_source, field_grid)
    report = {
        "benchmark_id": "B5",
        "problem_id": 38,
        "title": "B5 boundary-field embedding baseline for Hubbard density response",
        "version": "0.1",
        "last_updated": "2026-06-18",
        "status": STATUS,
        "method": METHOD,
        "model_status": "oracle_tuned_classical_boundary_field_response_denominator",
        "dependency_b10_table": d5_source.get("method"),
        "dependency_b10_result": str(d5_source_path),
        "dependency_energy_baseline": energy_source.get("method"),
        "dependency_energy_result": str(energy_source_path),
        "explicit_not_quantum_advantage": True,
        "explicit_not_bqp_separation": True,
        "oracle_tuned_boundary_field": True,
        "summary": summarize(rows, field_grid),
        "rows": rows,
        "runtime_seconds": time.perf_counter() - started,
        "claim_boundary": {
            "now_supported": (
                "A B5 observable-response denominator now exists for the same nine Hubbard D5 rows: "
                "a small-cluster boundary-field embedding approximation is oracle-tuned against the "
                "exact D5 susceptibility, making it a strong classical pressure baseline."
            ),
            "still_not_supported": (
                "This is not a quantum subroutine, not an accuracy-per-resource win, not a tensor-network "
                "or DMRG replacement, and not evidence for broad strongly correlated matter advantage."
            ),
            "next_gate": (
                "A candidate B5 quantum impurity/response kernel must beat this boundary-field denominator "
                "and a non-oracle tensor/DMRG/embedding baseline after state preparation and measurement costs."
            ),
        },
    }
    report["validation_errors"] = validate(report)
    return report


def markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# B5 Boundary-Field Embedding Baseline v0.1",
        "",
        f"Last updated: {report['last_updated']}",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{report['method']}`",
        f"- Dependency B10 table: `{report['dependency_b10_table']}`",
        f"- Dependency energy baseline: `{report['dependency_energy_baseline']}`",
        f"- Instances: {summary['instance_count']}",
        f"- Sites: {summary['site_values']}",
        f"- U/t values: {summary['u_over_t_values']}",
        f"- Boundary-field grid: {summary['boundary_field_grid']}",
        f"- Mean / median / max relative response error: {summary['mean_relative_response_error']:.6g} / {summary['median_relative_response_error']:.6g} / {summary['max_relative_response_error']:.6g}",
        f"- Zero-error instances: {summary['zero_error_instance_count']}",
        f"- Max exact D5 Hilbert dimension: {summary['max_exact_d5_hilbert_dimension']}",
        f"- Max embedded cluster Hilbert dimension: {summary['max_cluster_hilbert_dimension']}",
        f"- Mean best cluster-product energy error/site: {summary['mean_best_cluster_product_energy_error_per_site']:.6g}",
        f"- Validation errors: {len(report['validation_errors'])}",
        f"- Explicitly not quantum advantage: {report['explicit_not_quantum_advantage']}",
        "",
        "## Interpretation",
        "",
        "- This is a denominator and pressure-test artifact for B5/T-B5-001.",
        "- It uses the exact B10 D5 Hubbard density-response rows as the target.",
        "- It partitions the chain into small clusters and adds a scalar edge field on each cluster.",
        "- The field is oracle-tuned against the exact D5 response, so this is intentionally a strong classical baseline, not a deployable blind solver.",
        "- Any future B5 quantum response kernel must beat this baseline after state-preparation, measurement, optimizer-loop, and classical denominator costs are charged.",
        "",
        "## Rows",
        "",
        "| Sites | U/t | Partition | Best field | Exact D5 chi | Embedded chi | Rel. response error | Best energy error/site |",
        "|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {sites} | {u:.1f} | {partition} | {field:.2f} | {exact:.8g} | {embedded:.8g} | {rel:.6g} | {energy:.6g} |".format(
                sites=row["sites"],
                u=row["u_over_t"],
                partition=" + ".join(str(item) for item in row["embedding_partition"]),
                field=row["best_oracle_edge_field"],
                exact=row["exact_d5_susceptibility_proxy"],
                embedded=row["embedded_susceptibility_proxy"],
                rel=row["relative_response_error"],
                energy=row["best_cluster_product_energy_error_per_site"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Now supported: {report['claim_boundary']['now_supported']}",
            f"- Still not supported: {report['claim_boundary']['still_not_supported']}",
            f"- Next gate: {report['claim_boundary']['next_gate']}",
        ]
    )
    if report["validation_errors"]:
        lines.extend(["", "## Validation Errors", ""])
        lines.extend(f"- {error}" for error in report["validation_errors"])
    return "\n".join(lines) + "\n"


def parse_float_tuple(value: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in value.split(",") if item.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d5-source", type=Path, default=Path("results/B10_t1_d5_observable_denominator_table_v0.json"))
    parser.add_argument("--energy-source", type=Path, default=Path("results/B5_hubbard_embedding_baseline_v0.json"))
    parser.add_argument("--field-grid", default=",".join(str(item) for item in FIELD_GRID))
    parser.add_argument("--json-output", type=Path, default=Path("results/B5_boundary_field_embedding_baseline_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B5_boundary_field_embedding_baseline.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(
        d5_source_path=args.d5_source,
        energy_source_path=args.energy_source,
        field_grid=parse_float_tuple(args.field_grid),
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if not report["validation_errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
