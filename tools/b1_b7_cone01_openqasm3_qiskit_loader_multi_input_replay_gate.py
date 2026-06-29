#!/usr/bin/env python3
"""Qiskit-loader multi-input replay gate for B1/B7 cone_01 OpenQASM 3."""

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

METHOD = "b1_b7_cone01_openqasm3_qiskit_loader_multi_input_replay_gate_v0"
STATUS = "cone01_openqasm3_qiskit_loader_multi_input_replay_passed_sampled_inputs"
MODEL_STATUS = "qiskit_loader_openqasm3_matches_source_sampled_inputs_without_b7_credit"

SOURCE_QASM_PATH = RESULTS / "b1_native_t_resource_optimizer" / "qasmbench_medium_exact" / "gcm_h6.qasm"
QISKIT_LOADER_DEFAULT_PATH = RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_replay_gate_v0.json"
PROJECT_LOCAL_MULTI_INPUT_PATH = RESULTS / "B1_B7_cone01_openqasm3_multi_input_replay_gate_v0.json"
QASM3_PATH = (
    RESULTS
    / "B1_B7_cone01_openqasm3_candidate_export_gate"
    / "gcm_h6_line268_line1381_candidate_openqasm3.qasm"
)
OUT_JSON = RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_multi_input_replay_gate_v0.json"
OUT_MD = RESEARCH / "B1_B7_cone01_openqasm3_qiskit_loader_multi_input_replay_gate.md"

FIDELITY_TOLERANCE = 1e-10
AMPLITUDE_TOLERANCE = 1e-10
PROBABILITY_TOLERANCE = 1e-10
BASIS_INPUTS = [
    ("zero", []),
    ("x_q0", [0]),
    ("x_q4", [4]),
    ("x_q14", [14]),
    ("x_q4_q14", [4, 14]),
    ("x_q0_q4_q14", [0, 4, 14]),
]
PRODUCT_STATE_SEEDS = [17, 29]


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


def align_global_phase(reference: np.ndarray, candidate: np.ndarray) -> np.ndarray:
    inner = np.vdot(reference, candidate)
    if abs(inner) == 0:
        return candidate
    return candidate * np.conj(inner / abs(inner))


def basis_state(num_qubits: int, active_qubits: list[int]) -> Statevector:
    prep = QuantumCircuit(num_qubits)
    for qubit in active_qubits:
        prep.x(qubit)
    return Statevector.from_instruction(prep)


def product_state(num_qubits: int, seed: int) -> Statevector:
    rng = np.random.default_rng(seed)
    prep = QuantumCircuit(num_qubits)
    for qubit in range(num_qubits):
        prep.ry(float(rng.uniform(-np.pi, np.pi)), qubit)
        prep.rz(float(rng.uniform(-np.pi, np.pi)), qubit)
    return Statevector.from_instruction(prep)


def replay_case(
    label: str,
    input_kind: str,
    initial_state: Statevector,
    source_circuit: QuantumCircuit,
    qiskit_loader_circuit: QuantumCircuit,
) -> dict[str, Any]:
    source_state = initial_state.evolve(source_circuit)
    qiskit_state = initial_state.evolve(qiskit_loader_circuit)
    source_data = np.asarray(source_state.data)
    qiskit_data = np.asarray(qiskit_state.data)
    aligned_qiskit = align_global_phase(source_data, qiskit_data)
    amplitude_delta = np.abs(source_data - aligned_qiskit)
    probability_delta = np.abs(np.abs(source_data) ** 2 - np.abs(qiskit_data) ** 2)
    fidelity = float(state_fidelity(source_state, qiskit_state))
    infidelity = float(max(0.0, 1.0 - fidelity))
    max_amplitude_delta = float(np.max(amplitude_delta))
    max_probability_delta = float(np.max(probability_delta))
    return {
        "label": label,
        "input_kind": input_kind,
        "state_fidelity": fidelity,
        "infidelity": infidelity,
        "max_global_phase_aligned_amplitude_delta": max_amplitude_delta,
        "l2_global_phase_aligned_amplitude_delta": float(
            np.linalg.norm(source_data - aligned_qiskit)
        ),
        "max_probability_delta": max_probability_delta,
        "passed": bool(
            infidelity <= FIDELITY_TOLERANCE
            and max_amplitude_delta <= AMPLITUDE_TOLERANCE
            and max_probability_delta <= PROBABILITY_TOLERANCE
        ),
    }


def main() -> None:
    default_loader_payload = load_json(QISKIT_LOADER_DEFAULT_PATH)
    local_multi_payload = load_json(PROJECT_LOCAL_MULTI_INPUT_PATH)
    source_circuit = QuantumCircuit.from_qasm_file(str(SOURCE_QASM_PATH))
    qiskit_circuit = qasm3.loads(QASM3_PATH.read_text(encoding="utf-8"))

    errors: list[str] = []
    if default_loader_payload.get("status") != "cone01_openqasm3_qiskit_loader_replay_passed_default_input_only":
        errors.append("source Qiskit-loader default-input gate status changed")
    if (
        local_multi_payload.get("status")
        != "cone01_openqasm3_multi_input_replay_pressure_passed_not_symbolic_certificate"
    ):
        errors.append("source project-local multi-input gate status changed")

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
    cases: list[dict[str, Any]] = []
    for label, active_qubits in BASIS_INPUTS:
        cases.append(
            replay_case(
                label,
                "computational_basis",
                basis_state(num_qubits, active_qubits),
                source_unitary,
                qiskit_unitary,
            )
        )
    for seed in PRODUCT_STATE_SEEDS:
        cases.append(
            replay_case(
                f"product_seed_{seed}",
                "deterministic_product_state",
                product_state(num_qubits, seed),
                source_unitary,
                qiskit_unitary,
            )
        )

    failed_cases = [case["label"] for case in cases if not case["passed"]]
    replay_passed = not failed_cases
    if failed_cases:
        errors.append("Qiskit-loader multi-input replay failed cases: " + ", ".join(failed_cases))

    summary = {
        "source_qiskit_loader_default_input_gate": rel(QISKIT_LOADER_DEFAULT_PATH),
        "source_project_local_multi_input_gate": rel(PROJECT_LOCAL_MULTI_INPUT_PATH),
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
        "final_measurement_removed_for_statevector": True,
        "input_case_count": len(cases),
        "computational_basis_input_count": len(BASIS_INPUTS),
        "deterministic_product_state_input_count": len(PRODUCT_STATE_SEEDS),
        "product_state_seeds": PRODUCT_STATE_SEEDS,
        "input_cases": cases,
        "qiskit_loader_multi_input_replay_passed": replay_passed,
        "failed_input_case_count": len(failed_cases),
        "failed_input_cases": failed_cases,
        "min_state_fidelity": min(case["state_fidelity"] for case in cases),
        "max_infidelity": max(case["infidelity"] for case in cases),
        "max_global_phase_aligned_amplitude_delta": max(
            case["max_global_phase_aligned_amplitude_delta"] for case in cases
        ),
        "max_probability_delta": max(case["max_probability_delta"] for case in cases),
        "accepted_qiskit_loader_parse_artifact_count": 1,
        "accepted_qiskit_loader_replay_artifact_count": 1 if replay_passed else 0,
        "accepted_qiskit_loader_multi_input_replay_artifact_count": 1 if replay_passed else 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_symbolic_unitary_equivalence_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
        "qiskit_loader_parse_claimed": True,
        "qiskit_loader_replay_claimed": replay_passed,
        "qiskit_loader_multi_input_replay_claimed": replay_passed,
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
        "status": STATUS if not errors else "cone01_openqasm3_qiskit_loader_multi_input_replay_failed",
        "model_status": MODEL_STATUS if not errors else "qiskit_loader_openqasm3_multi_input_replay_rejected",
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "claim_boundary": {
            "supported_claim": (
                "The Qiskit-loaded OpenQASM 3 candidate matches the optimized source "
                "on the same deterministic 8-input suite used by the project-local "
                "multi-input replay gate after final measurements are removed."
            ),
            "qiskit_loader_parse_claimed": True,
            "qiskit_loader_replay_claimed": replay_passed,
            "qiskit_loader_multi_input_replay_claimed": replay_passed,
            "symbolic_unitary_equivalence_claimed": False,
            "arbitrary_input_equivalence_claimed": False,
            "full_hilbert_space_certificate_claimed": False,
            "local_u3_pricing_accepted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "unsupported_claims": [
                "This is sampled multi-input statevector evidence, not arbitrary-input equivalence.",
                "This is not a symbolic exact full-circuit unitary proof.",
                "This does not price or eliminate the remaining line-1381 off-grid local-U3 parameters.",
                "This does not recover the dropped line-1378 overlap delta.",
                "This does not improve the B7 resource ledger.",
            ],
        },
        "summary": summary,
        "validation_errors": errors,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    if errors:
        raise SystemExit("OpenQASM3 Qiskit-loader multi-input replay failed: " + "; ".join(errors))


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    claims = payload["claim_boundary"]
    return "\n".join(
        [
            "# B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Multi-Input Replay Gate",
            "",
            f"- Method: `{payload['method']}`",
            f"- Status: `{payload['status']}`",
            f"- Model status: `{payload['model_status']}`",
            f"- Workload: `{payload['workload']}`",
            f"- Supported claim: {claims['supported_claim']}",
            "",
            "## Inputs",
            "",
            f"- Qiskit-loader default-input gate: `{summary['source_qiskit_loader_default_input_gate']}`",
            f"- Project-local multi-input gate: `{summary['source_project_local_multi_input_gate']}`",
            f"- OpenQASM 3 candidate: `{summary['openqasm3_candidate_path']}`",
            "",
            "## Loader Evidence",
            "",
            f"- Qiskit / qiskit-qasm3-import / openqasm3 versions: {summary['qiskit_version']} / {summary['qiskit_qasm3_import_version']} / {summary['openqasm3_package_version']}",
            f"- Qubits / clbits / depth: {summary['qiskit_num_qubits']} / {summary['qiskit_num_clbits']} / {summary['qiskit_depth']}",
            f"- Operation counts: {summary['qiskit_count_ops']}",
            "",
            "## Multi-Input Replay Evidence",
            "",
            f"- Input cases: {summary['input_case_count']} ({summary['computational_basis_input_count']} computational-basis, {summary['deterministic_product_state_input_count']} product-state)",
            f"- Product-state seeds: {summary['product_state_seeds']}",
            f"- Min fidelity / max infidelity: {summary['min_state_fidelity']} / {summary['max_infidelity']}",
            f"- Max amplitude / probability delta: {summary['max_global_phase_aligned_amplitude_delta']} / {summary['max_probability_delta']}",
            f"- Failed cases: {summary['failed_input_cases']}",
            f"- Accepted Qiskit-loader parse / replay / multi-input replay artifacts: {summary['accepted_qiskit_loader_parse_artifact_count']} / {summary['accepted_qiskit_loader_replay_artifact_count']} / {summary['accepted_qiskit_loader_multi_input_replay_artifact_count']}",
            f"- Accepted occurrence / proxy-T reduction / B7 claim: {summary['accepted_occurrence_removal']} / {summary['accepted_proxy_t_reduction']} / {summary['b7_ledger_improvement_claimed']}",
            "",
            "## Claim Boundary",
            "",
            *[f"- {claim}" for claim in claims["unsupported_claims"]],
            "",
            "## Validation",
            "",
            f"- Qiskit-loader multi-input replay passed: {summary['qiskit_loader_multi_input_replay_passed']}",
            f"- Validation errors: {summary['validation_error_count']}",
            "",
        ]
    )


if __name__ == "__main__":
    main()
