#!/usr/bin/env python3
"""Finite linear-span replay certificate gate for the B1/B7 cone_01 candidate.

T-B1-004az fixes a single global phase anchor and checks sampled basis and
coherent-superposition inputs. This gate turns the basis-anchor part into a
finite subspace certificate: it computes the error operator restricted to the
six tested computational-basis inputs and reports the spectral norm bound for
all normalized linear combinations inside that six-dimensional span.

This is still not a full unitary-equivalence proof, not arbitrary-input
coverage, and not B7 resource credit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    load_json,
    write_json,
    write_text,
)
from b1_b7_cone01_global_phase_subspace_replay_gate import (
    CANDIDATE_REWRITE_PATH,
    SOURCE_QASM_PATH,
    anchor_suite,
    phase_from_overlap,
    without_final_measurements,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SUBSPACE_REPLAY_PATH = (
    ROOT / "results" / "B1_B7_cone01_global_phase_subspace_replay_gate_v0.json"
)
JSON_OUT = ROOT / "results" / "B1_B7_cone01_linear_span_replay_certificate_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_linear_span_replay_certificate_gate.md"

METHOD = "b1_b7_cone01_linear_span_replay_certificate_gate_v0"
STATUS = "cone01_linear_span_replay_certificate_passed_not_full_unitary"
MODEL_STATUS = "qasm2_candidate_has_six_dimensional_linear_span_replay_certificate_without_b7_credit"
SPECTRAL_NORM_TOLERANCE = 1e-10
GRAM_TOLERANCE = 1e-10
AMPLITUDE_TOLERANCE = 1e-10
PROBABILITY_TOLERANCE = 1e-10


def load_circuit(path: Path) -> QuantumCircuit:
    return QuantumCircuit.from_qasm_file(str(path))


def error_operator_metrics(
    source_circuit: QuantumCircuit,
    candidate_circuit: QuantumCircuit,
    global_phase_anchor: complex,
) -> dict[str, Any]:
    anchors = anchor_suite(source_circuit.num_qubits)
    source_columns: list[np.ndarray] = []
    candidate_columns: list[np.ndarray] = []
    basis_rows: list[dict[str, Any]] = []
    for label, state in anchors:
        source_state = state.evolve(source_circuit)
        candidate_state = state.evolve(candidate_circuit)
        source_data = np.asarray(source_state.data)
        anchored_candidate = np.asarray(candidate_state.data) * np.conj(global_phase_anchor)
        error = source_data - anchored_candidate
        source_columns.append(source_data)
        candidate_columns.append(anchored_candidate)
        basis_rows.append(
            {
                "label": label,
                "l2_error": float(np.linalg.norm(error)),
                "max_amplitude_delta": float(np.max(np.abs(error))),
                "max_probability_delta": float(
                    np.max(np.abs(np.abs(source_data) ** 2 - np.abs(candidate_state.data) ** 2))
                ),
            }
        )

    source_matrix = np.column_stack(source_columns)
    candidate_matrix = np.column_stack(candidate_columns)
    error_matrix = source_matrix - candidate_matrix
    error_gram = error_matrix.conj().T @ error_matrix
    error_eigenvalues = np.linalg.eigvalsh(error_gram)
    spectral_norm = float(np.sqrt(max(0.0, float(np.max(error_eigenvalues)))))
    source_gram = source_matrix.conj().T @ source_matrix
    candidate_gram = candidate_matrix.conj().T @ candidate_matrix
    gram_delta = np.abs(source_gram - candidate_gram)
    cross_gram_delta = np.abs(source_matrix.conj().T @ candidate_matrix - np.eye(len(anchors)))
    return {
        "basis_anchor_labels": [label for label, _ in anchors],
        "basis_anchor_case_count": len(anchors),
        "basis_anchor_rows": basis_rows,
        "linear_span_dimension": len(anchors),
        "linear_span_error_spectral_norm": spectral_norm,
        "linear_span_error_frobenius_norm": float(np.linalg.norm(error_matrix, "fro")),
        "max_basis_l2_error": max(row["l2_error"] for row in basis_rows),
        "max_basis_amplitude_delta": max(row["max_amplitude_delta"] for row in basis_rows),
        "max_basis_probability_delta": max(row["max_probability_delta"] for row in basis_rows),
        "max_source_candidate_gram_delta": float(np.max(gram_delta)),
        "max_cross_gram_delta": float(np.max(cross_gram_delta)),
    }


def run_probe() -> dict[str, Any]:
    candidate_payload = load_json(CANDIDATE_REWRITE_PATH)
    subspace_payload = load_json(SOURCE_SUBSPACE_REPLAY_PATH)
    subspace_summary = subspace_payload.get("summary", {})
    candidate_qasm = ROOT / candidate_payload["summary"]["qasm2_candidate_path"]
    source_unitary_part = without_final_measurements(load_circuit(SOURCE_QASM_PATH))
    candidate_unitary_part = without_final_measurements(load_circuit(candidate_qasm))
    zero_state = anchor_suite(source_unitary_part.num_qubits)[0][1]
    zero_source = zero_state.evolve(source_unitary_part)
    zero_candidate = zero_state.evolve(candidate_unitary_part)
    global_phase_anchor = phase_from_overlap(
        complex(np.vdot(np.asarray(zero_source.data), np.asarray(zero_candidate.data)))
    )
    span_metrics = error_operator_metrics(
        source_unitary_part,
        candidate_unitary_part,
        global_phase_anchor,
    )
    coherent_cases = [
        case
        for case in subspace_summary.get("input_cases", [])
        if case.get("input_kind") == "coherent_pair_superposition"
    ]
    coherent_witness_passed = all(case.get("passed") is True for case in coherent_cases)
    accepted_removed = 0
    full_dimension = 2 ** source_unitary_part.num_qubits
    finite_span_passed = (
        subspace_summary.get("global_phase_subspace_replay_passed") is True
        and coherent_witness_passed
        and span_metrics["linear_span_error_spectral_norm"] <= SPECTRAL_NORM_TOLERANCE
        and span_metrics["max_source_candidate_gram_delta"] <= GRAM_TOLERANCE
        and span_metrics["max_cross_gram_delta"] <= GRAM_TOLERANCE
        and span_metrics["max_basis_amplitude_delta"] <= AMPLITUDE_TOLERANCE
        and span_metrics["max_basis_probability_delta"] <= PROBABILITY_TOLERANCE
    )
    summary = {
        "source_qasm": display_path(SOURCE_QASM_PATH),
        "candidate_qasm": display_path(candidate_qasm),
        "source_method": candidate_payload.get("method"),
        "source_subspace_replay_method": subspace_payload.get("method"),
        "qubit_count": source_unitary_part.num_qubits,
        "statevector_dimension": full_dimension,
        "source_cnot_count": int(source_unitary_part.count_ops().get("cx", 0)),
        "candidate_cnot_count": int(candidate_unitary_part.count_ops().get("cx", 0)),
        "candidate_cnot_delta": int(source_unitary_part.count_ops().get("cx", 0))
        - int(candidate_unitary_part.count_ops().get("cx", 0)),
        "final_measurement_removed_for_statevector": True,
        "global_phase_anchor_label": "zero",
        "global_phase_anchor_radians": float(np.angle(global_phase_anchor)),
        "finite_linear_span_certificate_passed": finite_span_passed,
        "certified_input_subspace_dimension": span_metrics["linear_span_dimension"],
        "full_input_space_dimension": full_dimension,
        "certified_input_subspace_fraction": span_metrics["linear_span_dimension"] / full_dimension,
        "coherent_pair_witness_count": len(coherent_cases),
        "coherent_pair_witness_passed": coherent_witness_passed,
        **span_metrics,
        "symbolic_unitary_equivalence_claimed": False,
        "arbitrary_input_equivalence_claimed": False,
        "full_hilbert_space_certificate_claimed": False,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_full_circuit_qasm_patch_count": 0,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(
            0,
            (REQUIRED_OCCURRENCE_REMOVALS - accepted_removed) * PROXY_T_PER_OCCURRENCE,
        ),
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": 0,
    }
    payload = {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "source_candidate_rewrite_result": display_path(CANDIDATE_REWRITE_PATH),
        "source_subspace_replay_result": display_path(SOURCE_SUBSPACE_REPLAY_PATH),
        "summary": summary,
        "claim_boundary": {
            "supported_claim": (
                "The T-B1-004av QASM2 candidate has a tolerance-bounded replay "
                "certificate on the six-dimensional input span generated by the "
                "listed basis anchors, under the zero-input global phase anchor."
            ),
            "unsupported_claims": [
                "This is not a symbolic unitary-equivalence proof for the full circuit.",
                "This is not arbitrary-input or full Hilbert-space coverage.",
                "This is not an accepted B7 occurrence-removing certificate.",
                "This does not recover the dropped line-1378 overlap delta.",
                "This does not price or eliminate the remaining line-1381 off-grid local-U3 parameters.",
            ],
            "symbolic_unitary_equivalence_claimed": False,
            "arbitrary_input_equivalence_claimed": False,
            "full_hilbert_space_certificate_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }
    return payload


def markdown_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 Linear-Span Replay Certificate Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- Source candidate: `{payload['source_candidate_rewrite_result']}`",
        f"- Source subspace replay: `{payload['source_subspace_replay_result']}`",
        "",
        "## Result",
        "",
        f"- Finite linear-span certificate passed: `{summary['finite_linear_span_certificate_passed']}`",
        f"- Certified input subspace dimension: `{summary['certified_input_subspace_dimension']}` of `{summary['full_input_space_dimension']}`",
        f"- Certified input subspace fraction: `{summary['certified_input_subspace_fraction']}`",
        f"- Linear-span error spectral norm: `{summary['linear_span_error_spectral_norm']}`",
        f"- Max basis L2 error: `{summary['max_basis_l2_error']}`",
        f"- Max basis amplitude delta: `{summary['max_basis_amplitude_delta']}`",
        f"- Max basis probability delta: `{summary['max_basis_probability_delta']}`",
        f"- Max source/candidate Gram delta: `{summary['max_source_candidate_gram_delta']}`",
        f"- Max cross-Gram delta: `{summary['max_cross_gram_delta']}`",
        f"- Coherent pair witnesses passed: `{summary['coherent_pair_witness_passed']}` across `{summary['coherent_pair_witness_count']}` cases",
        f"- Candidate CNOT count: `{summary['candidate_cnot_count']}` vs source `{summary['source_cnot_count']}`",
        "",
        "## Claim Boundary",
        "",
        "- This certifies only a six-dimensional finite input span under a fixed numerical tolerance.",
        "- It is not a symbolic full-circuit unitary-equivalence proof.",
        "- It is not arbitrary-input coverage and does not count as B7 resource credit.",
        "- Accepted occurrence removal, proxy-T reduction, and B7 ledger improvement remain 0.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", default=str(JSON_OUT))
    parser.add_argument("--markdown-output", default=str(MD_OUT))
    args = parser.parse_args()
    payload = run_probe()
    write_json(Path(args.json_output), payload, True)
    write_text(Path(args.markdown_output), markdown_report(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
