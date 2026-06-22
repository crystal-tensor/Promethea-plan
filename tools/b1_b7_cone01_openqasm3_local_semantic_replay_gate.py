#!/usr/bin/env python3
"""Local semantic replay gate for the B1/B7 cone_01 OpenQASM 3 artifact.

T-B1-004bw proved that the OpenQASM 3 artifact structurally roundtrips against
the legacy OpenQASM 2 candidate. This gate takes the next local step: parse the
OpenQASM 3 artifact with the project's strict subset parser, construct a
QuantumCircuit directly, and compare the resulting default-input statevector
against the optimized source circuit.

This is still not a Qiskit OpenQASM 3 loader pass, arbitrary-input symbolic
equivalence, local-U3 pricing, occurrence removal, or B7 resource credit.
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
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


ROOT = Path(__file__).resolve().parents[1]
SOURCE_QASM_PATH = (
    ROOT / "results" / "b1_native_t_resource_optimizer" / "qasmbench_medium_exact" / "gcm_h6.qasm"
)
SOURCE_ROUNDTRIP = ROOT / "results" / "B1_B7_cone01_openqasm3_structural_roundtrip_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_openqasm3_local_semantic_replay_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_openqasm3_local_semantic_replay_gate.md"

METHOD = "b1_b7_cone01_openqasm3_local_semantic_replay_gate_v0"
STATUS = "cone01_openqasm3_local_semantic_replay_passed_default_input_only"
MODEL_STATUS = "project_local_openqasm3_replay_matches_source_default_input_without_b7_credit"
FIDELITY_TOLERANCE = 1e-10
AMPLITUDE_TOLERANCE = 1e-10
PROBABILITY_TOLERANCE = 1e-10
MEASURED_QUBIT = 4

HEADER_RE = re.compile(r"^OPENQASM 3\.0;$")
INCLUDE_RE = re.compile(r'^include "stdgates\.inc";$')
QUBIT_RE = re.compile(r"^qubit\[(\d+)\]\s+q;$")
BIT_RE = re.compile(r"^bit\[(\d+)\]\s+c;$")
U_RE = re.compile(r"^U\(([^()]*)\)\s+q\[(\d+)\];$")
RZ_RE = re.compile(r"^rz\(([^()]*)\)\s+q\[(\d+)\];$", re.IGNORECASE)
CX_RE = re.compile(r"^cx\s+q\[(\d+)\]\s*,\s*q\[(\d+)\];$", re.IGNORECASE)
MEASURE_RE = re.compile(r"^c\[(\d+)\]\s*=\s*measure\s+q\[(\d+)\];$")


class AngleEvaluator(ast.NodeVisitor):
    allowed_binops = (ast.Add, ast.Sub, ast.Mult, ast.Div)
    allowed_unary = (ast.UAdd, ast.USub)

    def visit_Expression(self, node: ast.Expression) -> float:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> float:
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"unsupported_constant_{node.value!r}")

    def visit_Name(self, node: ast.Name) -> float:
        if node.id == "pi":
            return math.pi
        raise ValueError(f"unsupported_name_{node.id}")

    def visit_BinOp(self, node: ast.BinOp) -> float:
        if not isinstance(node.op, self.allowed_binops):
            raise ValueError(f"unsupported_binop_{type(node.op).__name__}")
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        raise ValueError("unreachable_binop")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> float:
        if not isinstance(node.op, self.allowed_unary):
            raise ValueError(f"unsupported_unary_{type(node.op).__name__}")
        value = self.visit(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value

    def generic_visit(self, node: ast.AST) -> float:
        raise ValueError(f"unsupported_ast_{type(node).__name__}")


def parse_angle(expr: str) -> float:
    tree = ast.parse(expr.strip(), mode="eval")
    return float(AngleEvaluator().visit(tree))


def parse_angles(args: str, expected_count: int) -> list[float]:
    parts = [part.strip() for part in args.split(",")]
    if len(parts) != expected_count:
        raise ValueError(f"expected_{expected_count}_args_got_{len(parts)}")
    return [parse_angle(part) for part in parts]


def load_source_circuit() -> QuantumCircuit:
    return QuantumCircuit.from_qasm_file(str(SOURCE_QASM_PATH))


def load_openqasm3_local_circuit(path: Path) -> tuple[QuantumCircuit, dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    operation_counts = {"U": 0, "rz": 0, "cx": 0, "measure": 0}
    if len(lines) < 4:
        errors.append("too_few_lines")
    if not lines or not HEADER_RE.match(lines[0].strip()):
        errors.append("missing_openqasm3_header")
    if len(lines) < 2 or not INCLUDE_RE.match(lines[1].strip()):
        errors.append("missing_stdgates_include")

    qubits = None
    bits = None
    circuit: QuantumCircuit | None = None
    first_operation_line = None
    last_operation_kind = None

    for line_number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if line_number <= 2:
            continue
        qdecl = QUBIT_RE.match(line)
        if qdecl:
            qubits = int(qdecl.group(1))
            continue
        bdecl = BIT_RE.match(line)
        if bdecl:
            bits = int(bdecl.group(1))
            if qubits is None:
                errors.append(f"line_{line_number}_bit_decl_before_qubit_decl")
            else:
                circuit = QuantumCircuit(qubits, bits)
            continue
        if circuit is None:
            errors.append(f"line_{line_number}_operation_before_declarations")
            continue

        u_match = U_RE.match(line)
        if u_match:
            theta, phi, lam = parse_angles(u_match.group(1), 3)
            qubit = int(u_match.group(2))
            circuit.u(theta, phi, lam, qubit)
            operation_counts["U"] += 1
            first_operation_line = first_operation_line or line_number
            last_operation_kind = "U"
            continue
        rz_match = RZ_RE.match(line)
        if rz_match:
            (angle,) = parse_angles(rz_match.group(1), 1)
            qubit = int(rz_match.group(2))
            circuit.rz(angle, qubit)
            operation_counts["rz"] += 1
            first_operation_line = first_operation_line or line_number
            last_operation_kind = "rz"
            continue
        cx_match = CX_RE.match(line)
        if cx_match:
            control = int(cx_match.group(1))
            target = int(cx_match.group(2))
            circuit.cx(control, target)
            operation_counts["cx"] += 1
            first_operation_line = first_operation_line or line_number
            last_operation_kind = "cx"
            continue
        measure_match = MEASURE_RE.match(line)
        if measure_match:
            bit = int(measure_match.group(1))
            qubit = int(measure_match.group(2))
            circuit.measure(qubit, bit)
            operation_counts["measure"] += 1
            first_operation_line = first_operation_line or line_number
            last_operation_kind = "measure"
            continue
        errors.append(f"line_{line_number}_unparsed_statement")

    if circuit is None:
        circuit = QuantumCircuit(0, 0)
        errors.append("missing_circuit_declarations")
    return circuit, {
        "errors": errors,
        "qubit_count": qubits,
        "bit_count": bits,
        "statement_count": len([line for line in lines if line.strip()]),
        "operation_counts": operation_counts,
        "operation_row_count": sum(operation_counts.values()),
        "first_operation_line": first_operation_line,
        "last_operation_kind": last_operation_kind,
    }


def align_global_phase(reference: np.ndarray, candidate: np.ndarray) -> np.ndarray:
    inner = np.vdot(reference, candidate)
    if abs(inner) == 0:
        return candidate
    return candidate * np.conj(inner / abs(inner))


def measured_marginal(statevector: Statevector, qubit: int) -> dict[str, float]:
    probabilities = statevector.probabilities([qubit])
    return {"0": float(probabilities[0]), "1": float(probabilities[1])}


def max_distribution_delta(left: dict[str, float], right: dict[str, float]) -> float:
    return max(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in set(left) | set(right))


def without_final_measurements(circuit: QuantumCircuit) -> QuantumCircuit:
    return circuit.remove_final_measurements(inplace=False)


def build_payload() -> dict[str, Any]:
    roundtrip_payload = load_json(SOURCE_ROUNDTRIP)
    openqasm3_path = ROOT / roundtrip_payload["summary"]["openqasm3_candidate_path"]
    source_circuit = load_source_circuit()
    local_circuit, local_parse = load_openqasm3_local_circuit(openqasm3_path)
    source_unitary = without_final_measurements(source_circuit)
    local_unitary = without_final_measurements(local_circuit)

    source_state = Statevector.from_instruction(source_unitary)
    local_state = Statevector.from_instruction(local_unitary)
    source_data = np.asarray(source_state.data)
    local_data = np.asarray(local_state.data)
    aligned_local = align_global_phase(source_data, local_data)
    amplitude_delta = np.abs(source_data - aligned_local)
    probability_delta = np.abs(np.abs(source_data) ** 2 - np.abs(local_data) ** 2)
    fidelity = float(state_fidelity(source_state, local_state))
    source_marginal = measured_marginal(source_state, MEASURED_QUBIT)
    local_marginal = measured_marginal(local_state, MEASURED_QUBIT)
    measured_delta = max_distribution_delta(source_marginal, local_marginal)
    replay_passed = (
        not local_parse["errors"]
        and 1.0 - fidelity <= FIDELITY_TOLERANCE
        and float(np.max(amplitude_delta)) <= AMPLITUDE_TOLERANCE
        and float(np.max(probability_delta)) <= PROBABILITY_TOLERANCE
        and measured_delta <= PROBABILITY_TOLERANCE
    )
    accepted_removed = 0
    summary = {
        "source_method": roundtrip_payload.get("method"),
        "source_openqasm3_structural_roundtrip_gate": display_path(SOURCE_ROUNDTRIP),
        "source_qasm": display_path(SOURCE_QASM_PATH),
        "openqasm3_candidate_path": display_path(openqasm3_path),
        "project_local_openqasm3_parser_passed": not local_parse["errors"],
        "project_local_openqasm3_parser_error_count": len(local_parse["errors"]),
        "project_local_operation_counts": local_parse["operation_counts"],
        "qubit_count": local_parse["qubit_count"],
        "bit_count": local_parse["bit_count"],
        "statement_count": local_parse["statement_count"],
        "operation_row_count": local_parse["operation_row_count"],
        "first_operation_line": local_parse["first_operation_line"],
        "last_operation_kind": local_parse["last_operation_kind"],
        "statevector_dimension": len(source_state.data),
        "source_operation_count_without_measurements": int(source_unitary.size()),
        "openqasm3_operation_count_without_measurements": int(local_unitary.size()),
        "source_cnot_count": int(source_unitary.count_ops().get("cx", 0)),
        "openqasm3_cnot_count": int(local_unitary.count_ops().get("cx", 0)),
        "openqasm3_cnot_delta": int(source_unitary.count_ops().get("cx", 0))
        - int(local_unitary.count_ops().get("cx", 0)),
        "final_measurement_removed_for_statevector": True,
        "measured_qubit": MEASURED_QUBIT,
        "source_measured_marginal": source_marginal,
        "openqasm3_measured_marginal": local_marginal,
        "measured_marginal_max_delta": measured_delta,
        "state_fidelity": fidelity,
        "infidelity": float(max(0.0, 1.0 - fidelity)),
        "max_global_phase_aligned_amplitude_delta": float(np.max(amplitude_delta)),
        "l2_global_phase_aligned_amplitude_delta": float(np.linalg.norm(source_data - aligned_local)),
        "max_probability_delta": float(np.max(probability_delta)),
        "openqasm3_local_semantic_replay_passed": replay_passed,
        "accepted_project_local_openqasm3_replay_artifact_count": 1 if replay_passed else 0,
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
        "source_openqasm3_structural_roundtrip_gate": display_path(SOURCE_ROUNDTRIP),
        "source_qasm": display_path(SOURCE_QASM_PATH),
        "openqasm3_candidate_qasm": display_path(openqasm3_path),
        "summary": summary,
        "project_local_parser_errors": local_parse["errors"],
        "validation_errors": validation_errors,
        "claim_boundary": {
            "supported_claim": (
                "The project-local OpenQASM 3 parser can construct and replay the candidate "
                "against the optimized source on the benchmark default-input statevector."
            ),
            "unsupported_claims": [
                "This is not a Qiskit OpenQASM 3 loader parse.",
                "This is not symbolic unitary equivalence or arbitrary-input equivalence.",
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
        "first_operation_line": 5,
        "last_operation_kind": "measure",
        "statevector_dimension": 524288,
        "source_cnot_count": 795,
        "openqasm3_cnot_count": 789,
        "openqasm3_cnot_delta": 6,
        "final_measurement_removed_for_statevector": True,
        "measured_qubit": 4,
        "openqasm3_local_semantic_replay_passed": True,
        "accepted_project_local_openqasm3_replay_artifact_count": 1,
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
    if 1.0 - float(summary.get("state_fidelity", 0.0)) > FIDELITY_TOLERANCE:
        errors.append("state_fidelity_below_tolerance")
    if float(summary.get("max_global_phase_aligned_amplitude_delta", 1.0)) > AMPLITUDE_TOLERANCE:
        errors.append("max_amplitude_delta_above_tolerance")
    if float(summary.get("max_probability_delta", 1.0)) > PROBABILITY_TOLERANCE:
        errors.append("max_probability_delta_above_tolerance")
    if float(summary.get("measured_marginal_max_delta", 1.0)) > PROBABILITY_TOLERANCE:
        errors.append("measured_marginal_delta_above_tolerance")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 OpenQASM 3 Local Semantic Replay Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004bw and checks whether the project-local OpenQASM 3 parser can construct a replayable circuit for the forward-facing artifact.",
        "",
        "## Summary",
        "",
        f"- Source QASM: `{payload['source_qasm']}`",
        f"- OpenQASM 3 candidate: `{payload['openqasm3_candidate_qasm']}`",
        f"- Project-local parser passed / errors: `{summary['project_local_openqasm3_parser_passed']}` / `{summary['project_local_openqasm3_parser_error_count']}`",
        f"- Operation counts: `{summary['project_local_operation_counts']}`",
        f"- Qubits / bits / statements / operation rows: `{summary['qubit_count']}` / `{summary['bit_count']}` / `{summary['statement_count']}` / `{summary['operation_row_count']}`",
        f"- Statevector dimension: `{summary['statevector_dimension']}`",
        f"- Source / OpenQASM 3 CNOT count / delta: `{summary['source_cnot_count']}` / `{summary['openqasm3_cnot_count']}` / `{summary['openqasm3_cnot_delta']}`",
        f"- State fidelity / infidelity: `{summary['state_fidelity']}` / `{summary['infidelity']}`",
        f"- Max global-phase-aligned amplitude delta: `{summary['max_global_phase_aligned_amplitude_delta']}`",
        f"- Max probability / measured marginal delta: `{summary['max_probability_delta']}` / `{summary['measured_marginal_max_delta']}`",
        f"- Local semantic replay passed: `{summary['openqasm3_local_semantic_replay_passed']}`",
        f"- Accepted local replay / Qiskit loader / symbolic equivalence artifacts: `{summary['accepted_project_local_openqasm3_replay_artifact_count']}` / `{summary['accepted_qiskit_loader_parse_artifact_count']}` / `{summary['accepted_symbolic_unitary_equivalence_count']}`",
        f"- Accepted replay certificate / local-U3 pricing / occurrence / proxy-T reduction: `{summary['accepted_full_circuit_replay_certificate_count']}` / `{summary['accepted_local_u3_pricing_certificate_count']}` / `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"]["supported_claim"],
        "",
        "Unsupported claims:",
        "",
    ]
    for claim in payload["claim_boundary"]["unsupported_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Next Required Gate",
            "",
            "Move from default-input local replay to reproducible loader replay, symbolic or broader-input semantic evidence, and separate local-U3 pricing before any B7 resource credit is accepted.",
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
