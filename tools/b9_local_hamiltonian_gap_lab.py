#!/usr/bin/env python3
"""Run a small exact-diagonalization lab for B9 local-Hamiltonian gap behavior."""

from __future__ import annotations

import argparse
import json
from functools import reduce
from pathlib import Path

import numpy as np


PAULI = {
    "I": np.array([[1, 0], [0, 1]], dtype=np.complex128),
    "X": np.array([[0, 1], [1, 0]], dtype=np.complex128),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
    "Z": np.array([[1, 0], [0, -1]], dtype=np.complex128),
}


def kron_all(ops: list[np.ndarray]) -> np.ndarray:
    return reduce(np.kron, ops)


def pauli_term(qubits: int, labels: dict[int, str]) -> np.ndarray:
    return kron_all([PAULI[labels.get(idx, "I")] for idx in range(qubits)])


def build_terms(model: str, qubits: int) -> list[dict]:
    terms: list[dict] = []
    if model == "transverse_ising_frustrated":
        for idx in range(qubits - 1):
            coeff = 1.0 if idx % 2 == 0 else -0.65
            terms.append({"coeff": coeff, "labels": {idx: "Z", idx + 1: "Z"}, "kind": "interaction"})
        for idx in range(qubits):
            terms.append({"coeff": -0.55, "labels": {idx: "X"}, "kind": "field"})
    elif model == "xxz_chain":
        for idx in range(qubits - 1):
            terms.append({"coeff": 0.7, "labels": {idx: "X", idx + 1: "X"}, "kind": "interaction"})
            terms.append({"coeff": 0.7, "labels": {idx: "Y", idx + 1: "Y"}, "kind": "interaction"})
            terms.append({"coeff": 1.0, "labels": {idx: "Z", idx + 1: "Z"}, "kind": "interaction"})
        for idx in range(qubits):
            terms.append({"coeff": 0.17 * ((-1) ** idx), "labels": {idx: "Z"}, "kind": "field"})
    elif model == "cluster_stabilizer_open":
        for idx in range(1, qubits - 1):
            terms.append({"coeff": -1.0, "labels": {idx - 1: "Z", idx: "X", idx + 1: "Z"}, "kind": "stabilizer"})
        terms.append({"coeff": -0.65, "labels": {0: "X", 1: "Z"}, "kind": "boundary"})
        terms.append({"coeff": -0.65, "labels": {qubits - 2: "Z", qubits - 1: "X"}, "kind": "boundary"})
    else:
        raise ValueError(f"unknown model: {model}")
    return terms


def term_matrix(qubits: int, term: dict) -> np.ndarray:
    return term["coeff"] * pauli_term(qubits, term["labels"])


def hamiltonian(qubits: int, terms: list[dict]) -> np.ndarray:
    size = 2**qubits
    matrix = np.zeros((size, size), dtype=np.complex128)
    for term in terms:
        matrix += term_matrix(qubits, term)
    return matrix


def spectrum_stats(matrix: np.ndarray) -> dict:
    values, vectors = np.linalg.eigh(matrix)
    values = np.real_if_close(values).real
    width = float(values[-1] - values[0])
    gap = float(values[1] - values[0])
    return {
        "ground_energy": float(values[0]),
        "first_excited_energy": float(values[1]),
        "spectral_gap": gap,
        "spectral_width": width,
        "normalized_gap": gap / width if width > 0 else 0.0,
        "ground_vector": vectors[:, 0],
    }


def local_reweight_terms(terms: list[dict], interaction_scale: float, field_scale: float) -> list[dict]:
    out = []
    for term in terms:
        support = len(term["labels"])
        scale = interaction_scale if support >= 2 else field_scale
        out.append({**term, "coeff": term["coeff"] * scale})
    return out


def shifted_square_transform(matrix: np.ndarray, ground_energy: float, gamma: float) -> np.ndarray:
    shifted = matrix - ground_energy * np.eye(matrix.shape[0], dtype=np.complex128)
    return shifted + gamma * (shifted @ shifted)


def analyze_case(model: str, qubits: int, gamma: float) -> list[dict]:
    terms = build_terms(model, qubits)
    base = hamiltonian(qubits, terms)
    base_stats = spectrum_stats(base)

    transforms = {
        "local_interaction_reweight_v0": {
            "matrix": hamiltonian(qubits, local_reweight_terms(terms, interaction_scale=1.35, field_scale=0.90)),
            "locality_max": max(len(term["labels"]) for term in terms),
            "locality_note": "same_term_support_reweighted",
        },
        "shifted_square_spectral_filter_v0": {
            "matrix": shifted_square_transform(base, base_stats["ground_energy"], gamma),
            "locality_max": qubits,
            "locality_note": "nonlocal_dense_filter_for_counterexample_screening",
        },
    }

    rows = []
    for name, payload in transforms.items():
        stats = spectrum_stats(payload["matrix"])
        overlap = abs(np.vdot(base_stats["ground_vector"], stats["ground_vector"])) ** 2
        rows.append(
            {
                "model": model,
                "qubits": qubits,
                "hilbert_dimension": 2**qubits,
                "term_count": len(terms),
                "baseline_ground_energy": base_stats["ground_energy"],
                "baseline_gap": base_stats["spectral_gap"],
                "baseline_normalized_gap": base_stats["normalized_gap"],
                "transformation": name,
                "transformed_ground_energy": stats["ground_energy"],
                "transformed_gap": stats["spectral_gap"],
                "transformed_normalized_gap": stats["normalized_gap"],
                "gap_ratio": stats["spectral_gap"] / base_stats["spectral_gap"] if base_stats["spectral_gap"] else None,
                "normalized_gap_ratio": stats["normalized_gap"] / base_stats["normalized_gap"] if base_stats["normalized_gap"] else None,
                "ground_state_overlap": float(overlap),
                "locality_max": payload["locality_max"],
                "locality_note": payload["locality_note"],
                "candidate_passes_screen": bool(
                    payload["locality_max"] <= 3
                    and overlap >= 0.95
                    and stats["normalized_gap"] >= 1.05 * base_stats["normalized_gap"]
                ),
            }
        )
    return rows


def run(qubits: list[int], gamma: float) -> dict:
    models = ["transverse_ising_frustrated", "xxz_chain", "cluster_stabilizer_open"]
    rows = []
    for model in models:
        for n_qubits in qubits:
            if model == "cluster_stabilizer_open" and n_qubits < 4:
                continue
            rows.extend(analyze_case(model, n_qubits, gamma))

    local_rows = [row for row in rows if row["locality_max"] <= 3]
    pass_rows = [row for row in rows if row["candidate_passes_screen"]]
    counterexample_rows = [
        row
        for row in local_rows
        if row["gap_ratio"] is not None
        and row["gap_ratio"] > 1.05
        and row["normalized_gap_ratio"] < 1.0
    ]
    return {
        "benchmark_id": "B9",
        "method": "small_local_hamiltonian_gap_lab_v0",
        "model_status": "exact_small_instance_lab_not_quantum_pcp_proof",
        "models": models,
        "qubits": qubits,
        "configuration_count": len(rows),
        "locality_preserving_candidate_count": len(local_rows),
        "candidate_pass_count": len(pass_rows),
        "counterexample_candidate_count": len(counterexample_rows),
        "max_local_candidate_normalized_gap_ratio": max(row["normalized_gap_ratio"] for row in local_rows),
        "max_dense_filter_gap_ratio": max(
            row["gap_ratio"] for row in rows if row["transformation"] == "shifted_square_spectral_filter_v0"
        ),
        "results": rows,
    }


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", default="4,5,6")
    parser.add_argument("--gamma", type=float, default=0.7)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = run(qubits=parse_int_list(args.qubits), gamma=args.gamma)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
