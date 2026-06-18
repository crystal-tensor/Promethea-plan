#!/usr/bin/env python3
"""Build a small exact-diagonalization baseline for B5 Hubbard embedding work."""

from __future__ import annotations

import argparse
import json
import math
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.sparse import dok_matrix
from scipy.sparse.linalg import eigsh


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
def hubbard_ground_energy(
    sites: int,
    n_up: int,
    n_down: int,
    u_value: float,
    t_value: float,
    boundary: str,
) -> tuple[float, int]:
    up_states = bitstrings_with_weight(sites, n_up)
    down_states = bitstrings_with_weight(sites, n_down)
    basis = [(up, down) for up in up_states for down in down_states]
    index = {state: idx for idx, state in enumerate(basis)}
    dim = len(basis)
    matrix = dok_matrix((dim, dim), dtype=np.float64)

    neighbors = [(site, site + 1) for site in range(sites - 1)]
    if boundary == "periodic" and sites > 2:
        neighbors.append((sites - 1, 0))

    for col, (up_bits, down_bits) in enumerate(basis):
        matrix[col, col] = u_value * (up_bits & down_bits).bit_count()
        for src, dst in neighbors:
            for a, b in [(src, dst), (dst, src)]:
                up_hop = hop(up_bits, a, b)
                if up_hop is not None:
                    new_up, sign = up_hop
                    row = index[(new_up, down_bits)]
                    matrix[row, col] = matrix.get((row, col), 0.0) - t_value * sign
                down_hop = hop(down_bits, a, b)
                if down_hop is not None:
                    new_down, sign = down_hop
                    row = index[(up_bits, new_down)]
                    matrix[row, col] = matrix.get((row, col), 0.0) - t_value * sign

    csr = matrix.tocsr()
    if dim <= 4:
        energy = float(np.linalg.eigvalsh(csr.toarray())[0])
    else:
        energy = float(eigsh(csr, k=1, which="SA", return_eigenvectors=False, tol=1e-10)[0])
    return energy, dim


def cluster_product_energy(
    sites: int,
    cluster_size: int,
    u_value: float,
    t_value: float,
) -> tuple[float, int] | None:
    if sites % cluster_size != 0 or cluster_size % 2 != 0:
        return None
    clusters = sites // cluster_size
    cluster_energy, cluster_dim = hubbard_ground_energy(
        cluster_size,
        cluster_size // 2,
        cluster_size // 2,
        u_value,
        t_value,
        "open",
    )
    return clusters * cluster_energy, cluster_dim**clusters


def run(sites: list[int], u_values: list[float], cluster_sizes: list[int], t_value: float, boundary: str) -> dict:
    rows = []
    started = time.time()
    for site_count in sites:
        if site_count % 2 != 0:
            continue
        n_up = site_count // 2
        n_down = site_count // 2
        for u_value in u_values:
            exact_energy, exact_dim = hubbard_ground_energy(site_count, n_up, n_down, u_value, t_value, boundary)
            for cluster_size in cluster_sizes:
                proxy = cluster_product_energy(site_count, cluster_size, u_value, t_value)
                if proxy is None:
                    continue
                proxy_energy, proxy_dim = proxy
                absolute_error = abs(proxy_energy - exact_energy)
                rows.append(
                    {
                        "model": "one_dimensional_fermi_hubbard_half_filled",
                        "sites": site_count,
                        "n_up": n_up,
                        "n_down": n_down,
                        "u_over_t": u_value / t_value,
                        "t": t_value,
                        "boundary": boundary,
                        "exact_ground_energy": exact_energy,
                        "exact_energy_per_site": exact_energy / site_count,
                        "exact_hilbert_dimension": exact_dim,
                        "cluster_size": cluster_size,
                        "cluster_product_energy": proxy_energy,
                        "cluster_product_energy_per_site": proxy_energy / site_count,
                        "cluster_product_dimension_proxy": proxy_dim,
                        "absolute_energy_error": absolute_error,
                        "energy_error_per_site": absolute_error / site_count,
                        "relative_energy_error": absolute_error / abs(exact_energy) if exact_energy else None,
                    }
                )

    by_cluster = {}
    for cluster_size in sorted({row["cluster_size"] for row in rows}):
        subset = [row for row in rows if row["cluster_size"] == cluster_size]
        by_cluster[str(cluster_size)] = {
            "mean_error_per_site": float(np.mean([row["energy_error_per_site"] for row in subset])),
            "max_error_per_site": float(np.max([row["energy_error_per_site"] for row in subset])),
            "configuration_count": len(subset),
        }

    return {
        "benchmark_id": "B5",
        "method": "small_hubbard_exact_diagonalization_cluster_proxy_v0",
        "model_status": "exact_small_system_reference_plus_cluster_product_proxy",
        "sites": sites,
        "u_over_t_values": [u / t_value for u in u_values],
        "cluster_sizes": cluster_sizes,
        "boundary": boundary,
        "configuration_count": len(rows),
        "summary_by_cluster_size": by_cluster,
        "runtime_seconds": time.time() - started,
        "results": rows,
    }


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sites", default="4,6,8")
    parser.add_argument("--u-values", default="2,4,8")
    parser.add_argument("--cluster-sizes", default="2,4")
    parser.add_argument("--t", type=float, default=1.0)
    parser.add_argument("--boundary", choices=["open", "periodic"], default="open")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = run(
        sites=parse_int_list(args.sites),
        u_values=parse_float_list(args.u_values),
        cluster_sizes=parse_int_list(args.cluster_sizes),
        t_value=args.t,
        boundary=args.boundary,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
