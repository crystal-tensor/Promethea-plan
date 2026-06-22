#!/usr/bin/env python3
"""Phase-consistent replay gate for the B1/B7 cone_01 OpenQASM 3 artifact.

T-B1-004by checks a deterministic multi-input suite, but each case aligns a
global phase independently. This gate adds superposition and overlap-phase
pressure to the project-local OpenQASM 3 path, reducing the risk that sampled
replay is hiding an input-dependent phase mismatch.

This remains local numerical evidence. It is not a Qiskit OpenQASM 3 loader
pass, symbolic arbitrary-input equivalence, local-U3 pricing, occurrence
removal, or B7 resource credit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    load_json,
    write_json,
    write_text,
)
from b1_b7_cone01_openqasm3_local_semantic_replay_gate import (
    load_openqasm3_local_circuit,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_QASM_PATH = (
    ROOT / "results" / "b1_native_t_resource_optimizer" / "qasmbench_medium_exact" / "gcm_h6.qasm"
)
SOURCE_MULTI_INPUT_REPLAY = (
    ROOT / "results" / "B1_B7_cone01_openqasm3_multi_input_replay_gate_v0.json"
)
JSON_OUT = ROOT / "results" / "B1_B7_cone01_openqasm3_phase_consistent_replay_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_openqasm3_phase_consistent_replay_gate.md"

METHOD = "b1_b7_cone01_openqasm3_phase_consistent_replay_gate_v0"
STATUS = "cone01_openqasm3_phase_consistent_replay_passed_not_symbolic_certificate"
MODEL_STATUS = "project_local_openqasm3_candidate_has_phase_consistent_sampled_replay_without_b7_credit"
PHASE_TOLERANCE = 1e-10
FIDELITY_TOLERANCE = 1e-10
AMPLITUDE_TOLERANCE = 1e-10
PROBABILITY_TOLERANCE = 1e-10
PRODUCT_STATE_SEEDS = [17, 29]


def load_source_circuit() -> QuantumCircuit:
    return QuantumCircuit.from_qasm_file(str(SOURCE_QASM_PATH))


def without_final_measurements(circuit: QuantumCircuit) -> QuantumCircuit:
    return circuit.remove_final_measurements(inplace=False)


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


def normalized_superposition(left: Statevector, right: Statevector, phase: complex = 1.0) -> Statevector:
    vector = np.asarray(left.data) + phase * np.asarray(right.data)
    return Statevector(vector / np.linalg.norm(vector))


def input_suite(num_qubits: int) -> list[tuple[str, str, Statevector]]:
    zero = basis_state(num_qubits, [])
    x_q0 = basis_state(num_qubits, [0])
    x_q4 = basis_state(num_qubits, [4])
    x_q14 = basis_state(num_qubits, [14])
    product_17 = product_state(num_qubits, 17)
    product_29 = product_state(num_qubits, 29)
    return [
        ("zero", "basis_phase_anchor", zero),
        ("x_q0", "basis_phase_anchor", x_q0),
        ("x_q4", "basis_phase_anchor", x_q4),
        ("x_q14", "basis_phase_anchor", x_q14),
        ("sup_zero_xq4", "basis_superposition", normalized_superposition(zero, x_q4)),
        ("sup_xq0_xq14", "basis_superposition", normalized_superposition(x_q0, x_q14)),
        ("sup_zero_product17", "basis_product_superposition", normalized_superposition(zero, product_17)),
        (
            "sup_product17_i_product29",
            "product_superposition",
            normalized_superposition(product_17, product_29, 1j),
        ),
    ]


def align_global_phase(reference: np.ndarray, candidate: np.ndarray, overlap: complex) -> np.ndarray:
    if abs(overlap) == 0:
        return candidate
    return candidate * np.conj(overlap / abs(overlap))


def replay_case(
    label: str,
    input_kind: str,
    initial_state: Statevector,
    source_circuit: QuantumCircuit,
    openqasm3_circuit: QuantumCircuit,
) -> dict[str, Any]:
    source_state = initial_state.evolve(source_circuit)
    openqasm3_state = initial_state.evolve(openqasm3_circuit)
    source_data = np.asarray(source_state.data)
    openqasm3_data = np.asarray(openqasm3_state.data)
    overlap = complex(np.vdot(source_data, openqasm3_data))
    aligned_openqasm3 = align_global_phase(source_data, openqasm3_data, overlap)
    amplitude_delta = np.abs(source_data - aligned_openqasm3)
    probability_delta = np.abs(np.abs(source_data) ** 2 - np.abs(openqasm3_data) ** 2)
    fidelity = float(state_fidelity(source_state, openqasm3_state))
    return {
        "label": label,
        "input_kind": input_kind,
        "overlap_magnitude": float(abs(overlap)),
        "overlap_phase_radians": float(np.angle(overlap)),
        "state_fidelity": fidelity,
        "infidelity": float(max(0.0, 1.0 - fidelity)),
        "max_global_phase_aligned_amplitude_delta": float(np.max(amplitude_delta)),
        "l2_global_phase_aligned_amplitude_delta": float(
            np.linalg.norm(source_data - aligned_openqasm3)
        ),
        "max_probability_delta": float(np.max(probability_delta)),
        "passed": bool(
            1.0 - fidelity <= FIDELITY_TOLERANCE
            and float(np.max(amplitude_delta)) <= AMPLITUDE_TOLERANCE
            and float(np.max(probability_delta)) <= PROBABILITY_TOLERANCE
        ),
    }


def phase_spread(phases: list[float]) -> float:
    unwrapped = np.unwrap(np.asarray(phases, dtype=float))
    return float(np.max(unwrapped) - np.min(unwrapped))


def build_payload() -> dict[str, Any]:
    multi_input_payload = load_json(SOURCE_MULTI_INPUT_REPLAY)
    openqasm3_path = ROOT / multi_input_payload["summary"]["openqasm3_candidate_path"]
    source_circuit = load_source_circuit()
    openqasm3_circuit, local_parse = load_openqasm3_local_circuit(openqasm3_path)
    source_unitary = without_final_measurements(source_circuit)
    openqasm3_unitary = without_final_measurements(openqasm3_circuit)
    num_qubits = source_circuit.num_qubits

    cases = [
        replay_case(label, kind, state, source_unitary, openqasm3_unitary)
        for label, kind, state in input_suite(num_qubits)
    ]
    failed_cases = [case["label"] for case in cases if not case["passed"]]
    spread = phase_spread([case["overlap_phase_radians"] for case in cases])
    accepted_removed = 0
    replay_passed = not local_parse["errors"] and not failed_cases and spread <= PHASE_TOLERANCE
    summary = {
        "source_method": multi_input_payload.get("method"),
        "source_openqasm3_multi_input_replay_gate": display_path(SOURCE_MULTI_INPUT_REPLAY),
        "source_qasm": display_path(SOURCE_QASM_PATH),
        "openqasm3_candidate_path": display_path(openqasm3_path),
        "project_local_openqasm3_parser_passed": not local_parse["errors"],
        "project_local_openqasm3_parser_error_count": len(local_parse["errors"]),
        "project_local_operation_counts": local_parse["operation_counts"],
        "qubit_count": num_qubits,
        "bit_count": local_parse["bit_count"],
        "statement_count": local_parse["statement_count"],
        "operation_row_count": local_parse["operation_row_count"],
        "statevector_dimension": 2**num_qubits,
        "source_operation_count_without_measurements": int(source_unitary.size()),
        "openqasm3_operation_count_without_measurements": int(openqasm3_unitary.size()),
        "source_cnot_count": int(source_unitary.count_ops().get("cx", 0)),
        "openqasm3_cnot_count": int(openqasm3_unitary.count_ops().get("cx", 0)),
        "openqasm3_cnot_delta": int(source_unitary.count_ops().get("cx", 0))
        - int(openqasm3_unitary.count_ops().get("cx", 0)),
        "final_measurement_removed_for_statevector": True,
        "input_case_count": len(cases),
        "phase_anchor_input_count": 4,
        "superposition_input_count": 4,
        "product_state_seeds": PRODUCT_STATE_SEEDS,
        "input_cases": cases,
        "phase_consistent_replay_passed": replay_passed,
        "failed_input_case_count": len(failed_cases),
        "failed_input_cases": failed_cases,
        "overlap_phase_spread_radians": spread,
        "min_overlap_magnitude": min(case["overlap_magnitude"] for case in cases),
        "min_state_fidelity": min(case["state_fidelity"] for case in cases),
        "max_infidelity": max(case["infidelity"] for case in cases),
        "max_global_phase_aligned_amplitude_delta": max(
            case["max_global_phase_aligned_amplitude_delta"] for case in cases
        ),
        "max_probability_delta": max(case["max_probability_delta"] for case in cases),
        "accepted_project_local_openqasm3_phase_consistent_replay_artifact_count": (
            1 if replay_passed else 0
        ),
        "accepted_qiskit_loader_parse_artifact_count": 0,
        "accepted_symbolic_unitary_equivalence_count": 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(
            0,
            (REQUIRED_OCCURRENCE_REMOVALS - accepted_removed) * PROXY_T_PER_OCCURRENCE,
        ),
        "project_local_openqasm3_replay_claimed": replay_passed,
        "qiskit_loader_parse_claimed": False,
        "symbolic_unitary_equivalence_claimed": False,
        "arbitrary_input_equivalence_claimed": False,
        "local_u3_pricing_accepted": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": 0,
    }
    validation_errors = validate_summary(summary, local_parse["errors"])
    summary["validation_error_count"] = len(validation_errors)
    return {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "source_openqasm3_multi_input_replay_gate": display_path(SOURCE_MULTI_INPUT_REPLAY),
        "source_qasm": display_path(SOURCE_QASM_PATH),
        "openqasm3_candidate_qasm": display_path(openqasm3_path),
        "summary": summary,
        "project_local_parser_errors": local_parse["errors"],
        "validation_errors": validation_errors,
        "claim_boundary": {
            "supported_claim": (
                "The project-local OpenQASM 3 parser can construct the candidate and "
                "match the optimized source across phase-anchor and superposition "
                "statevector replay pressure while maintaining tiny overlap-phase spread."
            ),
            "unsupported_claims": [
                "This is not a Qiskit OpenQASM 3 loader parse.",
                "This is not symbolic unitary equivalence or arbitrary-input equivalence.",
                "This is not an exhaustive input-space replay certificate.",
                "This does not price or eliminate local-U3 burden.",
                "This does not create B7 occurrence, proxy-T, or space-time-volume credit.",
            ],
            "project_local_openqasm3_replay_claimed": replay_passed,
            "qiskit_loader_parse_claimed": False,
            "symbolic_unitary_equivalence_claimed": False,
            "arbitrary_input_equivalence_claimed": False,
            "local_u3_pricing_accepted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }


def validate_summary(summary: dict[str, Any], parser_errors: list[str]) -> list[str]:
    errors: list[str] = []
    expected = {
        "project_local_openqasm3_parser_passed": True,
        "project_local_openqasm3_parser_error_count": 0,
        "project_local_operation_counts": {"U": 487, "rz": 601, "cx": 789, "measure": 1},
        "qubit_count": 19,
        "bit_count": 1,
        "statement_count": 1884,
        "operation_row_count": 1878,
        "statevector_dimension": 524288,
        "source_cnot_count": 795,
        "openqasm3_cnot_count": 789,
        "openqasm3_cnot_delta": 6,
        "final_measurement_removed_for_statevector": True,
        "input_case_count": 8,
        "phase_anchor_input_count": 4,
        "superposition_input_count": 4,
        "phase_consistent_replay_passed": True,
        "failed_input_case_count": 0,
        "accepted_project_local_openqasm3_phase_consistent_replay_artifact_count": 1,
        "accepted_qiskit_loader_parse_artifact_count": 0,
        "accepted_symbolic_unitary_equivalence_count": 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
        "project_local_openqasm3_replay_claimed": True,
        "qiskit_loader_parse_claimed": False,
        "symbolic_unitary_equivalence_claimed": False,
        "arbitrary_input_equivalence_claimed": False,
        "local_u3_pricing_accepted": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
    }
    for field, value in expected.items():
        if summary.get(field) != value:
            errors.append(f"{field}_expected_{value}_got_{summary.get(field)}")
    if parser_errors:
        errors.append("project_local_parser_errors_not_empty")
    if summary.get("product_state_seeds") != PRODUCT_STATE_SEEDS:
        errors.append("product_state_seeds_mismatch")
    if float(summary.get("overlap_phase_spread_radians", 1.0)) > PHASE_TOLERANCE:
        errors.append("phase_spread_above_tolerance")
    if float(summary.get("max_infidelity", 1.0)) > FIDELITY_TOLERANCE:
        errors.append("max_infidelity_above_tolerance")
    if float(summary.get("max_global_phase_aligned_amplitude_delta", 1.0)) > AMPLITUDE_TOLERANCE:
        errors.append("max_amplitude_delta_above_tolerance")
    if float(summary.get("max_probability_delta", 1.0)) > PROBABILITY_TOLERANCE:
        errors.append("max_probability_delta_above_tolerance")
    if summary.get("failed_input_cases") != []:
        errors.append("failed_input_cases_not_empty")
    for case in summary.get("input_cases", []):
        if case.get("passed") is not True:
            errors.append(f"case_{case.get('label')}_failed")
        if 1.0 - float(case.get("state_fidelity", 0.0)) > FIDELITY_TOLERANCE:
            errors.append(f"case_{case.get('label')}_fidelity_below_tolerance")
        if float(case.get("max_probability_delta", 1.0)) > PROBABILITY_TOLERANCE:
            errors.append(f"case_{case.get('label')}_probability_delta_above_tolerance")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 OpenQASM 3 Phase-Consistent Replay Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004by and adds overlap-phase and superposition pressure to the project-local OpenQASM 3 replay path.",
        "",
        "## Summary",
        "",
        f"- Source QASM: `{payload['source_qasm']}`",
        f"- OpenQASM 3 candidate: `{payload['openqasm3_candidate_qasm']}`",
        f"- Project-local parser passed / errors: `{summary['project_local_openqasm3_parser_passed']}` / `{summary['project_local_openqasm3_parser_error_count']}`",
        f"- Input cases: `{summary['input_case_count']}` total; `{summary['phase_anchor_input_count']}` phase anchors and `{summary['superposition_input_count']}` superposition inputs",
        f"- Source / OpenQASM 3 CNOT count / delta: `{summary['source_cnot_count']}` / `{summary['openqasm3_cnot_count']}` / `{summary['openqasm3_cnot_delta']}`",
        f"- Phase-consistent replay passed: `{summary['phase_consistent_replay_passed']}`",
        f"- Overlap phase spread radians: `{summary['overlap_phase_spread_radians']}`",
        f"- Min overlap magnitude: `{summary['min_overlap_magnitude']}`",
        f"- Min state fidelity / max infidelity: `{summary['min_state_fidelity']}` / `{summary['max_infidelity']}`",
        f"- Max global-phase-aligned amplitude delta: `{summary['max_global_phase_aligned_amplitude_delta']}`",
        f"- Max probability delta: `{summary['max_probability_delta']}`",
        f"- Accepted OpenQASM 3 phase replay / Qiskit loader / symbolic equivalence artifacts: `{summary['accepted_project_local_openqasm3_phase_consistent_replay_artifact_count']}` / `{summary['accepted_qiskit_loader_parse_artifact_count']}` / `{summary['accepted_symbolic_unitary_equivalence_count']}`",
        f"- Accepted replay certificate / local-U3 pricing / occurrence / proxy-T reduction: `{summary['accepted_full_circuit_replay_certificate_count']}` / `{summary['accepted_local_u3_pricing_certificate_count']}` / `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Input Cases",
        "",
        "| Case | Kind | Overlap phase | Fidelity | Max probability delta | Passed |",
        "|---|---|---:|---:|---:|---|",
    ]
    for case in summary["input_cases"]:
        lines.append(
            f"| `{case['label']}` | `{case['input_kind']}` | `{case['overlap_phase_radians']}` | `{case['state_fidelity']}` | `{case['max_probability_delta']}` | `{case['passed']}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"]["supported_claim"],
            "",
            "Unsupported claims:",
            "",
        ]
    )
    for claim in payload["claim_boundary"]["unsupported_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Next Required Gate",
            "",
            "Move from project-local OpenQASM 3 phase replay to Qiskit-loader replay, symbolic/local-unitary evidence, or a global-phase anchored certificate; then separately price or eliminate the remaining local-U3 burden before any B7 resource credit is accepted.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=JSON_OUT)
    parser.add_argument("--markdown-output", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.json_output, payload, args.pretty)
    write_text(args.markdown_output, render_markdown(payload))
    print(json.dumps(payload["summary"], indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
