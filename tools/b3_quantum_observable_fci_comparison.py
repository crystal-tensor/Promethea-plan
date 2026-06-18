#!/usr/bin/env python3
"""Build B3 observable-estimation circuit proxies compared with FCI denominators."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


TARGET_ERROR_FRACTION = 0.05
MIN_TARGET_ERROR = 1.0e-3


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def qasm_identifier(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name.lower()).strip("_")


def target_error_for_derivative(value: float) -> float:
    return max(MIN_TARGET_ERROR, TARGET_ERROR_FRACTION * abs(value))


def shot_floor(error: float) -> int:
    return int(math.ceil(1.0 / (error * error)))


def build_qasm(row: dict, fci_row: dict, controlled_terms: int) -> str:
    system_qubits = 2 * int(fci_row["spatial_orbitals"])
    total_qubits = system_qubits + 1
    ancilla = 0
    lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{total_qubits}];",
        "creg c[1];",
        f"// B3 observable-estimation proxy for {row['molecule']}",
        f"// Coordinate: {row['coordinate']}",
        "// q[0] is the Hadamard-test ancilla; q[1:] are Jordan-Wigner spin-orbital proxy qubits.",
    ]
    for idx in range(min(int(fci_row["electrons"]), system_qubits)):
        lines.append(f"x q[{idx + 1}];")
    lines.append(f"h q[{ancilla}];")
    # Deterministic phase-kickback proxy: distribute response-matrix terms over system qubits.
    # Angles are scaled by the finite-difference source magnitude so the circuit stays bounded.
    base_angle = min(0.25, abs(float(row["finite_difference_energy_derivative"])) + 0.01)
    for term_idx in range(controlled_terms):
        target = 1 + (term_idx % system_qubits)
        angle = base_angle / (1 + (term_idx % 7))
        lines.append(f"crz({angle:.12g}) q[{ancilla}],q[{target}];")
    lines.append(f"h q[{ancilla}];")
    lines.append(f"measure q[{ancilla}] -> c[0];")
    lines.append("")
    return "\n".join(lines)


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "quantum_observable_circuit_vs_fci_denominator_proxy_not_advantage_claim":
        errors.append("status must remain a circuit proxy, not an advantage claim")
    if report.get("method") != "b3_quantum_observable_fci_comparison_v0":
        errors.append("method mismatch")
    if report.get("dependency_benchmark") != "B3":
        errors.append("dependency_benchmark must be B3")
    if report.get("source_denominator_method") != "b10_t1_d5_b3_reaction_observable_table_v0":
        errors.append("source denominator method mismatch")
    if report.get("source_fci_method") != "b10_t1_d5_b3_fci_reference_table_v0":
        errors.append("source FCI method mismatch")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("expected four reaction-coordinate instances")
    if summary.get("qasm_file_count") != 4:
        errors.append("expected four QASM circuit files")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction-dynamics solution")
    if summary.get("max_controlled_phase_gates", 0) < 100:
        errors.append("expected at least one nontrivial controlled-phase proxy circuit")
    if summary.get("max_measurement_shot_floor", 0) <= 0:
        errors.append("measurement shot floor must be positive")
    for row in report.get("rows", []):
        if not Path(row.get("qasm_path", "")).exists():
            errors.append(f"missing qasm file: {row.get('qasm_path')}")
        if row.get("quantum_beats_fci_denominator") is not False:
            errors.append(f"{row.get('molecule')} must not claim to beat FCI")
        if row.get("measurement_shot_floor", 0) <= 0:
            errors.append(f"{row.get('molecule')} has invalid shot floor")
        if row.get("controlled_phase_gates", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no controlled phase gates")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def build_report(denominator_path: Path, fci_path: Path, qasm_dir: Path) -> dict:
    denominator = load_json(denominator_path)
    fci = load_json(fci_path)
    denom_by_name = {row["molecule"]: row for row in denominator.get("rows", [])}
    rows = []
    qasm_dir.mkdir(parents=True, exist_ok=True)
    for fci_row in fci.get("rows", []):
        molecule = fci_row["molecule"]
        denom_row = denom_by_name[molecule]
        fci_derivative = float(fci_row["methods"]["FCI"]["finite_difference_derivative_hartree_per_coordinate"])
        target_error = target_error_for_derivative(fci_derivative)
        shots = shot_floor(target_error)
        controlled_terms = int(denom_row["response_nnz"])
        qasm_path = qasm_dir / f"{qasm_identifier(molecule)}_observable_estimation.qasm"
        qasm_path.write_text(build_qasm(denom_row, fci_row, controlled_terms), encoding="utf-8")
        rows.append(
            {
                "source_benchmark": "B3",
                "molecule": molecule,
                "basis": fci_row["basis"],
                "coordinate": fci_row["coordinate"],
                "coordinate_center": fci_row["coordinate_center"],
                "spatial_orbitals": fci_row["spatial_orbitals"],
                "spin_orbital_qubits": 2 * int(fci_row["spatial_orbitals"]),
                "ancilla_qubits": 1,
                "total_qubits": 2 * int(fci_row["spatial_orbitals"]) + 1,
                "electrons": fci_row["electrons"],
                "response_dimension": denom_row["response_dimension"],
                "response_nnz": denom_row["response_nnz"],
                "controlled_phase_gates": controlled_terms,
                "state_preparation_x_gates": min(int(fci_row["electrons"]), 2 * int(fci_row["spatial_orbitals"])),
                "hadamard_gates": 2,
                "measurement_count": 1,
                "single_circuit_gate_count_proxy": controlled_terms
                + min(int(fci_row["electrons"]), 2 * int(fci_row["spatial_orbitals"]))
                + 3,
                "single_circuit_depth_proxy": controlled_terms + 4,
                "qasm_path": str(qasm_path),
                "fci_derivative_hartree_per_coordinate": fci_derivative,
                "fci_center_energy_hartree": fci_row["methods"]["FCI"]["center_energy_hartree"],
                "fci_wall_time_seconds": fci_row["wall_time_seconds"],
                "target_observable_error_hartree_per_coordinate": target_error,
                "target_error_fraction": TARGET_ERROR_FRACTION,
                "measurement_shot_floor": shots,
                "sampled_controlled_phase_budget": shots * controlled_terms,
                "classical_denominator": "STO-3G finite-difference FCI derivative",
                "quantum_beats_fci_denominator": False,
                "comparison_interpretation": (
                    "The circuit proxy is mapped to the same reaction-coordinate derivative target as the FCI "
                    "denominator, but no accuracy, runtime, or advantage win is claimed."
                ),
            }
        )

    summary = {
        "instance_count": len(rows),
        "qasm_file_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "max_total_qubits": max(row["total_qubits"] for row in rows),
        "max_controlled_phase_gates": max(row["controlled_phase_gates"] for row in rows),
        "max_measurement_shot_floor": max(row["measurement_shot_floor"] for row in rows),
        "max_sampled_controlled_phase_budget": max(row["sampled_controlled_phase_budget"] for row in rows),
        "quantum_advantage_claimed": False,
        "reaction_dynamics_solution_claimed": False,
        "fci_denominator_beaten_count": sum(1 for row in rows if row["quantum_beats_fci_denominator"]),
    }
    report = {
        "benchmark_id": "B3",
        "problem_id": 49,
        "title": "B3 quantum observable-estimation circuit proxies vs FCI denominators",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "quantum_observable_circuit_vs_fci_denominator_proxy_not_advantage_claim",
        "method": "b3_quantum_observable_fci_comparison_v0",
        "dependency_benchmark": "B3",
        "source_denominator": str(denominator_path),
        "source_denominator_method": denominator.get("method"),
        "source_fci_reference": str(fci_path),
        "source_fci_method": fci.get("method"),
        "summary": summary,
        "rows": rows,
        "claim_boundary": [
            "Supported: four OpenQASM observable-estimation proxy circuits aligned to B3 reaction-coordinate FCI derivative denominators.",
            "Supported: explicit measurement-shot and controlled-phase budget floors for the proxy circuits.",
            "Not supported: quantum advantage, chemistry accuracy, complete reaction dynamics, basis-set completeness, or beating the FCI denominator.",
        ],
        "next_steps": [
            "Replace phase-kickback proxies with Hamiltonian Pauli-term circuits from a chemistry mapper.",
            "Add state-preparation cost and observable variance estimates from sampled simulation.",
            "Scale the denominator beyond STO-3G FCI to selected-CI or larger active spaces.",
            "Only promote if a concrete circuit beats the declared denominator at fixed observable error after all preparation/readout costs.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B3 Quantum Observable Circuit vs FCI Denominator v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source denominator method: {report['source_denominator_method']}",
        f"- Source FCI method: {report['source_fci_method']}",
        f"- Instances: {report['summary']['instance_count']}",
        f"- QASM files: {report['summary']['qasm_file_count']}",
        f"- Max qubits: {report['summary']['max_total_qubits']}",
        f"- Max controlled-phase gates: {report['summary']['max_controlled_phase_gates']}",
        f"- Max measurement shot floor: {report['summary']['max_measurement_shot_floor']}",
        f"- FCI denominator beaten count: {report['summary']['fci_denominator_beaten_count']}",
        f"- Quantum advantage claimed: {report['summary']['quantum_advantage_claimed']}",
        f"- Reaction-dynamics solution claimed: {report['summary']['reaction_dynamics_solution_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Circuit Rows",
        "",
        "| molecule | qubits | controlled phases | shot floor | FCI derivative | target error | QASM | beats FCI? |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['molecule']} | {row['total_qubits']} | {row['controlled_phase_gates']} | "
            f"{row['measurement_shot_floor']} | {row['fci_derivative_hartree_per_coordinate']:.6e} | "
            f"{row['target_observable_error_hartree_per_coordinate']:.6e} | `{row['qasm_path']}` | "
            f"{row['quantum_beats_fci_denominator']} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in report["claim_boundary"])
    lines.extend(["", "## Next Steps", ""])
    lines.extend(f"- {item}" for item in report["next_steps"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--denominator",
        type=Path,
        default=Path("results/B10_t1_d5_b3_reaction_observable_table_v0.json"),
    )
    parser.add_argument(
        "--fci-reference",
        type=Path,
        default=Path("results/B10_t1_d5_b3_fci_reference_table_v0.json"),
    )
    parser.add_argument(
        "--qasm-dir",
        type=Path,
        default=Path("results/b3_quantum_observable_fci_comparison/circuits"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_quantum_observable_fci_comparison_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_quantum_observable_fci_comparison.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.denominator, args.fci_reference, args.qasm_dir)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "instances": report["summary"]["instance_count"],
                    "qasm_files": report["summary"]["qasm_file_count"],
                    "max_qubits": report["summary"]["max_total_qubits"],
                    "max_controlled_phase_gates": report["summary"]["max_controlled_phase_gates"],
                    "fci_denominator_beaten_count": report["summary"]["fci_denominator_beaten_count"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
