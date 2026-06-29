#!/usr/bin/env python3
"""Qiskit-loader global-phase subspace replay gate for B1/B7 cone_01 OpenQASM 3."""

from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qasm3
from qiskit.quantum_info import Statevector, state_fidelity


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESEARCH = ROOT / "research"

METHOD = "b1_b7_cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_gate_v0"
STATUS = "cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_passed"
MODEL_STATUS = (
    "qiskit_loader_openqasm3_has_global_phase_anchored_subspace_replay_without_b7_credit"
)

SOURCE_QASM_PATH = RESULTS / "b1_native_t_resource_optimizer" / "qasmbench_medium_exact" / "gcm_h6.qasm"
QISKIT_LOADER_PHASE_PATH = (
    RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_phase_consistent_replay_gate_v0.json"
)
PROJECT_LOCAL_GLOBAL_PHASE_PATH = (
    RESULTS / "B1_B7_cone01_openqasm3_global_phase_subspace_replay_gate_v0.json"
)
QASM3_PATH = (
    RESULTS
    / "B1_B7_cone01_openqasm3_candidate_export_gate"
    / "gcm_h6_line268_line1381_candidate_openqasm3.qasm"
)
OUT_JSON = RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_gate_v0.json"
OUT_MD = RESEARCH / "B1_B7_cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_gate.md"

PHASE_TOLERANCE = 1e-10
FIDELITY_TOLERANCE = 1e-10
AMPLITUDE_TOLERANCE = 1e-10
PROBABILITY_TOLERANCE = 1e-10


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def without_final_measurements(circuit: QuantumCircuit) -> QuantumCircuit:
    return circuit.remove_final_measurements(inplace=False)


def basis_state(num_qubits: int, active_qubits: tuple[int, ...]) -> Statevector:
    prep = QuantumCircuit(num_qubits)
    for qubit in active_qubits:
        prep.x(qubit)
    return Statevector.from_instruction(prep)


def normalized_superposition(left: Statevector, right: Statevector, phase: complex) -> Statevector:
    vector = np.asarray(left.data) + phase * np.asarray(right.data)
    return Statevector(vector / np.linalg.norm(vector))


def anchor_suite(num_qubits: int) -> list[tuple[str, Statevector]]:
    return [
        ("zero", basis_state(num_qubits, ())),
        ("x_q0", basis_state(num_qubits, (0,))),
        ("x_q4", basis_state(num_qubits, (4,))),
        ("x_q14", basis_state(num_qubits, (14,))),
        ("x_q0_q4", basis_state(num_qubits, (0, 4))),
        ("x_q4_q14", basis_state(num_qubits, (4, 14))),
    ]


def superposition_suite(anchors: list[tuple[str, Statevector]]) -> list[tuple[str, Statevector]]:
    by_label = dict(anchors)
    pairs = [
        ("zero", "x_q0"),
        ("zero", "x_q4"),
        ("x_q0", "x_q14"),
        ("x_q4", "x_q0_q4"),
        ("x_q0_q4", "x_q4_q14"),
    ]
    phases = [("plus", 1.0), ("minus", -1.0), ("iplus", 1j)]
    cases: list[tuple[str, Statevector]] = []
    for left, right in pairs:
        for phase_label, phase in phases:
            cases.append(
                (
                    f"sup_{left}_{phase_label}_{right}",
                    normalized_superposition(by_label[left], by_label[right], phase),
                )
            )
    return cases


def phase_from_overlap(overlap: complex) -> complex:
    if abs(overlap) == 0:
        return 1.0 + 0.0j
    return overlap / abs(overlap)


def anchored_replay_case(
    label: str,
    input_kind: str,
    initial_state: Statevector,
    source_circuit: QuantumCircuit,
    qiskit_loader_circuit: QuantumCircuit,
    global_phase_anchor: complex,
) -> dict[str, Any]:
    source_state = initial_state.evolve(source_circuit)
    qiskit_state = initial_state.evolve(qiskit_loader_circuit)
    source_data = np.asarray(source_state.data)
    qiskit_data = np.asarray(qiskit_state.data)
    overlap = complex(np.vdot(source_data, qiskit_data))
    overlap_phase = phase_from_overlap(overlap)
    anchored_qiskit = qiskit_data * np.conj(global_phase_anchor)
    amplitude_delta = np.abs(source_data - anchored_qiskit)
    probability_delta = np.abs(np.abs(source_data) ** 2 - np.abs(qiskit_data) ** 2)
    fidelity = float(state_fidelity(source_state, qiskit_state))
    infidelity = float(max(0.0, 1.0 - fidelity))
    phase_delta = float(np.angle(overlap_phase / global_phase_anchor))
    max_amplitude_delta = float(np.max(amplitude_delta))
    max_probability_delta = float(np.max(probability_delta))
    return {
        "label": label,
        "input_kind": input_kind,
        "overlap_magnitude": float(abs(overlap)),
        "overlap_phase_radians": float(np.angle(overlap)),
        "global_anchor_phase_delta_radians": phase_delta,
        "state_fidelity": fidelity,
        "infidelity": infidelity,
        "max_global_anchor_aligned_amplitude_delta": max_amplitude_delta,
        "l2_global_anchor_aligned_amplitude_delta": float(np.linalg.norm(source_data - anchored_qiskit)),
        "max_probability_delta": max_probability_delta,
        "passed": bool(
            abs(phase_delta) <= PHASE_TOLERANCE
            and infidelity <= FIDELITY_TOLERANCE
            and max_amplitude_delta <= AMPLITUDE_TOLERANCE
            and max_probability_delta <= PROBABILITY_TOLERANCE
        ),
    }


def build_payload() -> dict[str, Any]:
    qiskit_phase_payload = load_json(QISKIT_LOADER_PHASE_PATH)
    local_global_payload = load_json(PROJECT_LOCAL_GLOBAL_PHASE_PATH)
    source_circuit = QuantumCircuit.from_qasm_file(str(SOURCE_QASM_PATH))
    qiskit_circuit = qasm3.loads(QASM3_PATH.read_text(encoding="utf-8"))

    errors: list[str] = []
    if qiskit_phase_payload.get("status") != "cone01_openqasm3_qiskit_loader_phase_consistent_replay_passed":
        errors.append("source Qiskit-loader phase-consistent gate status changed")
    if (
        local_global_payload.get("status")
        != "cone01_openqasm3_global_phase_subspace_replay_passed_not_symbolic_certificate"
    ):
        errors.append("source project-local global-phase subspace gate status changed")

    qiskit_counts = {key: int(value) for key, value in qiskit_circuit.count_ops().items()}
    expected_counts = {"cx": 789, "rz": 601, "u": 487, "measure": 1}
    if qiskit_counts != expected_counts:
        errors.append("Qiskit-loader operation counts changed")
    if qiskit_circuit.num_qubits != 19:
        errors.append("Qiskit-loader qubit count changed")
    if qiskit_circuit.num_clbits != 1:
        errors.append("Qiskit-loader clbit count changed")
    if qiskit_circuit.depth() != 1483:
        errors.append("Qiskit-loader depth changed")

    source_unitary = without_final_measurements(source_circuit)
    qiskit_unitary = without_final_measurements(qiskit_circuit)
    num_qubits = source_circuit.num_qubits
    anchors = anchor_suite(num_qubits)

    zero_source = anchors[0][1].evolve(source_unitary)
    zero_qiskit = anchors[0][1].evolve(qiskit_unitary)
    global_phase_anchor = phase_from_overlap(
        complex(np.vdot(np.asarray(zero_source.data), np.asarray(zero_qiskit.data)))
    )

    anchor_cases = [
        anchored_replay_case(
            label,
            "basis_subspace_anchor",
            state,
            source_unitary,
            qiskit_unitary,
            global_phase_anchor,
        )
        for label, state in anchors
    ]
    superposition_cases = [
        anchored_replay_case(
            label,
            "coherent_pair_superposition",
            state,
            source_unitary,
            qiskit_unitary,
            global_phase_anchor,
        )
        for label, state in superposition_suite(anchors)
    ]
    cases = anchor_cases + superposition_cases
    failed_cases = [case["label"] for case in cases if not case["passed"]]
    replay_passed = not failed_cases
    if failed_cases:
        errors.append("Qiskit-loader global-phase subspace replay failed cases: " + ", ".join(failed_cases))

    max_anchor_delta = max(abs(case["global_anchor_phase_delta_radians"]) for case in cases)
    min_overlap = min(case["overlap_magnitude"] for case in cases)
    min_fidelity = min(case["state_fidelity"] for case in cases)
    max_infidelity = max(case["infidelity"] for case in cases)
    max_amplitude_delta = max(case["max_global_anchor_aligned_amplitude_delta"] for case in cases)
    max_probability_delta = max(case["max_probability_delta"] for case in cases)
    if max_anchor_delta > PHASE_TOLERANCE:
        errors.append(f"Qiskit-loader global anchor phase delta exceeds tolerance: {max_anchor_delta}")
    if max_infidelity > FIDELITY_TOLERANCE:
        errors.append(f"Qiskit-loader global-phase infidelity exceeds tolerance: {max_infidelity}")
    if max_amplitude_delta > AMPLITUDE_TOLERANCE:
        errors.append(f"Qiskit-loader global-anchor amplitude delta exceeds tolerance: {max_amplitude_delta}")
    if max_probability_delta > PROBABILITY_TOLERANCE:
        errors.append(f"Qiskit-loader global-phase probability delta exceeds tolerance: {max_probability_delta}")

    summary = {
        "source_qiskit_loader_phase_consistent_gate": rel(QISKIT_LOADER_PHASE_PATH),
        "source_project_local_global_phase_subspace_gate": rel(PROJECT_LOCAL_GLOBAL_PHASE_PATH),
        "source_qasm_path": rel(SOURCE_QASM_PATH),
        "openqasm3_candidate_path": rel(QASM3_PATH),
        "qiskit_version": package_version("qiskit"),
        "qiskit_qasm3_import_version": package_version("qiskit-qasm3-import"),
        "openqasm3_package_version": package_version("openqasm3"),
        "qiskit_loader_passed": True,
        "qiskit_num_qubits": int(qiskit_circuit.num_qubits),
        "qiskit_num_clbits": int(qiskit_circuit.num_clbits),
        "qiskit_depth": int(qiskit_circuit.depth()),
        "qiskit_count_ops": qiskit_counts,
        "expected_qiskit_count_ops": expected_counts,
        "statevector_dimension": 2**num_qubits,
        "source_operation_count_without_measurements": int(source_unitary.size()),
        "qiskit_operation_count_without_measurements": int(qiskit_unitary.size()),
        "source_cnot_count": int(source_unitary.count_ops().get("cx", 0)),
        "qiskit_cnot_count": int(qiskit_unitary.count_ops().get("cx", 0)),
        "qiskit_cnot_delta": int(source_unitary.count_ops().get("cx", 0))
        - int(qiskit_unitary.count_ops().get("cx", 0)),
        "final_measurement_removed_for_statevector": True,
        "global_phase_anchor_label": "zero",
        "global_phase_anchor_radians": float(np.angle(global_phase_anchor)),
        "basis_anchor_case_count": len(anchor_cases),
        "coherent_superposition_case_count": len(superposition_cases),
        "input_case_count": len(cases),
        "input_cases": cases,
        "qiskit_loader_global_phase_subspace_replay_passed": replay_passed,
        "failed_input_case_count": len(failed_cases),
        "failed_input_cases": failed_cases,
        "max_global_anchor_phase_delta_radians": max_anchor_delta,
        "min_overlap_magnitude": min_overlap,
        "min_state_fidelity": min_fidelity,
        "max_infidelity": max_infidelity,
        "max_global_anchor_aligned_amplitude_delta": max_amplitude_delta,
        "max_probability_delta": max_probability_delta,
        "accepted_qiskit_loader_parse_artifact_count": 1,
        "accepted_qiskit_loader_replay_artifact_count": 1 if replay_passed else 0,
        "accepted_qiskit_loader_phase_consistent_replay_artifact_count": 1,
        "accepted_qiskit_loader_global_phase_subspace_replay_artifact_count": (
            1 if replay_passed else 0
        ),
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_symbolic_unitary_equivalence_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
        "qiskit_loader_parse_claimed": True,
        "qiskit_loader_replay_claimed": replay_passed,
        "qiskit_loader_phase_consistent_replay_claimed": True,
        "qiskit_loader_global_phase_subspace_replay_claimed": replay_passed,
        "symbolic_unitary_equivalence_claimed": False,
        "arbitrary_input_equivalence_claimed": False,
        "full_hilbert_space_certificate_claimed": False,
        "local_u3_pricing_accepted": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": len(errors),
    }
    payload = {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS if not errors else "cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_failed",
        "model_status": MODEL_STATUS if not errors else "qiskit_loader_openqasm3_global_phase_subspace_replay_rejected",
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "claim_boundary": {
            "supported_claim": (
                "The Qiskit-loaded OpenQASM 3 candidate matches the optimized source "
                "under one zero-input global phase anchor across 6 basis anchors and "
                "15 coherent pair superpositions after final measurements are removed."
            ),
            "qiskit_loader_parse_claimed": True,
            "qiskit_loader_replay_claimed": replay_passed,
            "qiskit_loader_phase_consistent_replay_claimed": True,
            "qiskit_loader_global_phase_subspace_replay_claimed": replay_passed,
            "symbolic_unitary_equivalence_claimed": False,
            "arbitrary_input_equivalence_claimed": False,
            "full_hilbert_space_certificate_claimed": False,
            "local_u3_pricing_accepted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "unsupported_claims": [
                "This is sampled fixed-anchor subspace replay, not arbitrary-input equivalence.",
                "This is not a symbolic exact full-circuit unitary proof.",
                "This does not price or eliminate the remaining line-1381 off-grid local-U3 parameters.",
                "This does not recover the dropped line-1378 overlap delta.",
                "This does not improve the B7 resource ledger.",
            ],
        },
        "summary": summary,
        "validation_errors": errors,
    }
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    claims = payload["claim_boundary"]
    lines = [
        "# B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Global-Phase Subspace Replay Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- Supported claim: {claims['supported_claim']}",
        "",
        "## Inputs",
        "",
        f"- Qiskit-loader phase-consistent gate: `{summary['source_qiskit_loader_phase_consistent_gate']}`",
        f"- Project-local global-phase subspace gate: `{summary['source_project_local_global_phase_subspace_gate']}`",
        f"- OpenQASM 3 candidate: `{summary['openqasm3_candidate_path']}`",
        "",
        "## Loader Evidence",
        "",
        f"- Qiskit / qiskit-qasm3-import / openqasm3 versions: {summary['qiskit_version']} / {summary['qiskit_qasm3_import_version']} / {summary['openqasm3_package_version']}",
        f"- Qubits / clbits / depth: {summary['qiskit_num_qubits']} / {summary['qiskit_num_clbits']} / {summary['qiskit_depth']}",
        f"- Operation counts: {summary['qiskit_count_ops']}",
        "",
        "## Global-Phase Subspace Replay Evidence",
        "",
        f"- Global phase anchor: `{summary['global_phase_anchor_label']}` / `{summary['global_phase_anchor_radians']}` radians",
        f"- Input cases: {summary['input_case_count']} ({summary['basis_anchor_case_count']} basis anchors, {summary['coherent_superposition_case_count']} coherent superpositions)",
        f"- Max global-anchor phase delta: {summary['max_global_anchor_phase_delta_radians']}",
        f"- Min overlap magnitude: {summary['min_overlap_magnitude']}",
        f"- Min fidelity / max infidelity: {summary['min_state_fidelity']} / {summary['max_infidelity']}",
        f"- Max amplitude / probability delta: {summary['max_global_anchor_aligned_amplitude_delta']} / {summary['max_probability_delta']}",
        f"- Failed cases: {summary['failed_input_cases']}",
        f"- Accepted Qiskit-loader parse / replay / phase / global-anchor artifacts: {summary['accepted_qiskit_loader_parse_artifact_count']} / {summary['accepted_qiskit_loader_replay_artifact_count']} / {summary['accepted_qiskit_loader_phase_consistent_replay_artifact_count']} / {summary['accepted_qiskit_loader_global_phase_subspace_replay_artifact_count']}",
        f"- Accepted occurrence / proxy-T reduction / B7 claim: {summary['accepted_occurrence_removal']} / {summary['accepted_proxy_t_reduction']} / {summary['b7_ledger_improvement_claimed']}",
        "",
        "## Input Cases",
        "",
        "| Case | Kind | Anchor phase delta | Fidelity | Max probability delta | Passed |",
        "|---|---|---:|---:|---:|---|",
    ]
    for case in summary["input_cases"]:
        lines.append(
            f"| `{case['label']}` | `{case['input_kind']}` | `{case['global_anchor_phase_delta_radians']}` | `{case['state_fidelity']}` | `{case['max_probability_delta']}` | `{case['passed']}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            *[f"- {claim}" for claim in claims["unsupported_claims"]],
            "",
            "## Validation",
            "",
            f"- Qiskit-loader global-phase subspace replay passed: {summary['qiskit_loader_global_phase_subspace_replay_passed']}",
            f"- Validation errors: {summary['validation_error_count']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    if payload["validation_errors"]:
        raise SystemExit(
            "OpenQASM3 Qiskit-loader global-phase subspace replay failed: "
            + "; ".join(payload["validation_errors"])
        )


if __name__ == "__main__":
    main()
