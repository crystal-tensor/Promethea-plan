#!/usr/bin/env python3
"""Build B3 Hamiltonian Pauli-term measurement circuits vs FCI denominators."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib-codex")
os.environ.setdefault("XDG_CACHE_HOME", "/private/tmp/codex-cache")

from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.units import DistanceUnit


COEFF_CUTOFF = 1.0e-10
MAX_QASM_TERMS = 16
MIN_TARGET_ERROR = 1.0e-3
TARGET_ERROR_FRACTION = 0.05


def atoms_h2(r: float) -> str:
    return f"H 0 0 0; H 0 0 {r}"


def atoms_lih(r: float) -> str:
    return f"Li 0 0 0; H 0 0 {r}"


def atoms_n2(r: float) -> str:
    return f"N 0 0 0; N 0 0 {r}"


def atoms_h2o(scale: float) -> str:
    return (
        "O 0 0 0; "
        f"H 0 {0.757 * scale} {0.587 * scale}; "
        f"H 0 {-0.757 * scale} {0.587 * scale}"
    )


ATOM_BUILDERS = {
    "h2_bond_stretch": atoms_h2,
    "lih_bond_stretch": atoms_lih,
    "h2o_symmetric_oh_stretch": atoms_h2o,
    "n2_bond_stretch": atoms_n2,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def qasm_identifier(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name.lower()).strip("_")


def target_error_for_derivative(value: float) -> float:
    return max(MIN_TARGET_ERROR, TARGET_ERROR_FRACTION * abs(value))


def build_problem(atom: str, basis: str):
    driver = PySCFDriver(
        atom=atom,
        basis=basis.replace("-", ""),
        charge=0,
        spin=0,
        unit=DistanceUnit.ANGSTROM,
    )
    return driver.run()


def mapped_pauli_terms(molecule: str, coordinate_center: float, basis: str) -> tuple[int, tuple[int, int], list[dict]]:
    atom = ATOM_BUILDERS[molecule](float(coordinate_center))
    problem = build_problem(atom, basis)
    qubit_op = JordanWignerMapper().map(problem.hamiltonian.second_q_op())
    terms = []
    for pauli, coeff in zip(qubit_op.paulis, qubit_op.coeffs):
        real_coeff = float(complex(coeff).real)
        imag_coeff = float(complex(coeff).imag)
        if abs(imag_coeff) > 1.0e-8:
            raise ValueError(f"{molecule} has non-real mapped coefficient {coeff}")
        if abs(real_coeff) <= COEFF_CUTOFF:
            continue
        terms.append(
            {
                "pauli": str(pauli),
                "coefficient": real_coeff,
                "abs_coefficient": abs(real_coeff),
                "weight": sum(1 for ch in str(pauli) if ch != "I"),
            }
        )
    terms.sort(key=lambda row: (-row["abs_coefficient"], row["pauli"]))
    return int(qubit_op.num_qubits), tuple(int(x) for x in problem.num_particles), terms


def add_basis_rotation(lines: list[str], pauli_label: str) -> None:
    # Qiskit labels are big-endian; OpenQASM q[0] is the least-significant qubit.
    for qidx, ch in enumerate(reversed(pauli_label)):
        if ch == "X":
            lines.append(f"h q[{qidx}];")
        elif ch == "Y":
            lines.append(f"sdg q[{qidx}];")
            lines.append(f"h q[{qidx}];")


def build_measurement_packet_qasm(molecule: str, qubits: int, electrons: int, terms: list[dict]) -> str:
    classical_bits = max(1, qubits * len(terms))
    lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{qubits}];",
        f"creg c[{classical_bits}];",
        f"// B3 Hamiltonian Pauli-term measurement packet for {molecule}",
        "// Mapper: Qiskit Nature JordanWignerMapper",
        "// Each block resets qubits, prepares a Hartree-Fock occupation bitstring, rotates into the Pauli basis, then measures.",
    ]
    for term_idx, term in enumerate(terms):
        offset = term_idx * qubits
        lines.append(f"// term {term_idx}: {term['coefficient']:.12g} * {term['pauli']}")
        for qidx in range(qubits):
            lines.append(f"reset q[{qidx}];")
        for qidx in range(min(electrons, qubits)):
            lines.append(f"x q[{qidx}];")
        add_basis_rotation(lines, str(term["pauli"]))
        for qidx in range(qubits):
            lines.append(f"measure q[{qidx}] -> c[{offset + qidx}];")
    lines.append("")
    return "\n".join(lines)


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "hamiltonian_pauli_mapper_circuits_vs_fci_denominator_not_advantage_claim":
        errors.append("status must remain a non-advantage Hamiltonian mapper artifact")
    if report.get("method") != "b3_hamiltonian_pauli_mapper_comparison_v0":
        errors.append("method mismatch")
    if report.get("dependency_benchmark") != "B3":
        errors.append("dependency_benchmark must be B3")
    summary = report.get("summary", {})
    if summary.get("instance_count") != 4:
        errors.append("expected four reaction-coordinate instances")
    if summary.get("qasm_file_count") != 4:
        errors.append("expected four QASM packet files")
    if summary.get("state_preparation_cost_included") is not True:
        errors.append("state-preparation cost must be included")
    if summary.get("observable_variance_estimate_included") is not True:
        errors.append("observable variance estimate must be included")
    if summary.get("quantum_advantage_claimed") is not False:
        errors.append("must not claim quantum advantage")
    if summary.get("reaction_dynamics_solution_claimed") is not False:
        errors.append("must not claim reaction-dynamics solution")
    if summary.get("fci_denominator_beaten_count") != 0:
        errors.append("must not claim to beat FCI denominators")
    for row in report.get("rows", []):
        if not Path(row.get("qasm_path", "")).exists():
            errors.append(f"missing qasm file: {row.get('qasm_path')}")
        if row.get("pauli_terms_after_cutoff", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no mapped Pauli terms")
        if row.get("measurement_packet_terms", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no measurement packet terms")
        if row.get("state_preparation_x_gates", 0) <= 0:
            errors.append(f"{row.get('molecule')} has no state-preparation cost")
        if row.get("variance_upper_bound", 0.0) <= 0.0:
            errors.append(f"{row.get('molecule')} has no variance estimate")
        if row.get("quantum_beats_fci_denominator") is not False:
            errors.append(f"{row.get('molecule')} must not claim an FCI win")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def build_report(fci_path: Path, qasm_dir: Path) -> dict[str, Any]:
    fci = load_json(fci_path)
    qasm_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for fci_row in fci.get("rows", []):
        molecule = fci_row["molecule"]
        fci_derivative = float(fci_row["methods"]["FCI"]["finite_difference_derivative_hartree_per_coordinate"])
        qubits, particles, terms = mapped_pauli_terms(
            molecule=molecule,
            coordinate_center=float(fci_row["coordinate_center"]),
            basis=str(fci_row["basis"]),
        )
        packet_terms = terms[:MAX_QASM_TERMS]
        coeff_l1 = sum(term["abs_coefficient"] for term in terms)
        variance_upper_bound = sum(term["coefficient"] ** 2 for term in terms)
        target_error = target_error_for_derivative(fci_derivative)
        per_term_shots = int(math.ceil(variance_upper_bound / (target_error * target_error)))
        total_measurement_shots = per_term_shots * len(terms)
        qasm_path = qasm_dir / f"{qasm_identifier(molecule)}_hamiltonian_pauli_measurements.qasm"
        qasm_path.write_text(
            build_measurement_packet_qasm(
                molecule=molecule,
                qubits=qubits,
                electrons=int(fci_row["electrons"]),
                terms=packet_terms,
            ),
            encoding="utf-8",
        )
        rows.append(
            {
                "source_benchmark": "B3",
                "molecule": molecule,
                "basis": fci_row["basis"],
                "coordinate": fci_row["coordinate"],
                "coordinate_center": fci_row["coordinate_center"],
                "mapper": "qiskit_nature.second_q.mappers.JordanWignerMapper",
                "spatial_orbitals": fci_row["spatial_orbitals"],
                "spin_orbital_qubits": qubits,
                "total_qubits": qubits,
                "electrons": fci_row["electrons"],
                "num_alpha_particles": particles[0],
                "num_beta_particles": particles[1],
                "pauli_terms_after_cutoff": len(terms),
                "coefficient_cutoff": COEFF_CUTOFF,
                "measurement_packet_terms": len(packet_terms),
                "qasm_path": str(qasm_path),
                "state_preparation_model": "Hartree-Fock occupation bitstring via X gates before each Pauli measurement block",
                "state_preparation_x_gates": min(int(fci_row["electrons"]), qubits),
                "state_preparation_x_gates_per_packet": min(int(fci_row["electrons"]), qubits)
                * len(packet_terms),
                "max_pauli_weight": max(term["weight"] for term in terms),
                "mean_pauli_weight": sum(term["weight"] for term in terms) / len(terms),
                "largest_abs_coefficient": max(term["abs_coefficient"] for term in terms),
                "coefficient_l1_norm": coeff_l1,
                "variance_upper_bound": variance_upper_bound,
                "target_observable_error_hartree_per_coordinate": target_error,
                "target_error_fraction": TARGET_ERROR_FRACTION,
                "per_term_shot_floor_from_variance": per_term_shots,
                "total_measurement_shot_floor": total_measurement_shots,
                "fci_derivative_hartree_per_coordinate": fci_derivative,
                "fci_center_energy_hartree": fci_row["methods"]["FCI"]["center_energy_hartree"],
                "fci_wall_time_seconds": fci_row["wall_time_seconds"],
                "classical_denominator": "STO-3G finite-difference FCI derivative",
                "quantum_beats_fci_denominator": False,
                "top_pauli_terms": packet_terms,
                "comparison_interpretation": (
                    "Hamiltonian Pauli terms are now produced by a chemistry mapper and paired with "
                    "state-preparation plus variance shot floors, but this still does not beat the FCI "
                    "denominator or solve reaction dynamics."
                ),
            }
        )

    summary = {
        "instance_count": len(rows),
        "qasm_file_count": len(rows),
        "molecule_count": len({row["molecule"] for row in rows}),
        "max_total_qubits": max(row["total_qubits"] for row in rows),
        "max_pauli_terms_after_cutoff": max(row["pauli_terms_after_cutoff"] for row in rows),
        "max_measurement_packet_terms": max(row["measurement_packet_terms"] for row in rows),
        "max_total_measurement_shot_floor": max(row["total_measurement_shot_floor"] for row in rows),
        "max_variance_upper_bound": max(row["variance_upper_bound"] for row in rows),
        "state_preparation_cost_included": True,
        "observable_variance_estimate_included": True,
        "quantum_advantage_claimed": False,
        "reaction_dynamics_solution_claimed": False,
        "fci_denominator_beaten_count": sum(1 for row in rows if row["quantum_beats_fci_denominator"]),
    }
    report = {
        "benchmark_id": "B3",
        "problem_id": 49,
        "title": "B3 Hamiltonian Pauli-term mapper circuits vs FCI denominators",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "hamiltonian_pauli_mapper_circuits_vs_fci_denominator_not_advantage_claim",
        "method": "b3_hamiltonian_pauli_mapper_comparison_v0",
        "dependency_benchmark": "B3",
        "source_fci_reference": str(fci_path),
        "source_fci_method": fci.get("method"),
        "summary": summary,
        "rows": rows,
        "claim_boundary": [
            "Supported: four chemistry-mapper Jordan-Wigner Hamiltonian Pauli-term measurement packets.",
            "Supported: Hartree-Fock state-preparation X-gate counts and conservative Pauli-estimator variance shot floors.",
            "Not supported: quantum advantage, FCI denominator win, basis-set completeness, chemistry accuracy, or complete reaction dynamics.",
        ],
        "next_steps": [
            "Replace Hartree-Fock bitstring preparation with an ansatz or adiabatic/state-preparation cost model.",
            "Run sampled Pauli-estimator simulation to replace the variance upper bound with observed confidence intervals.",
            "Scale the denominator to selected-CI or larger active spaces.",
            "Only promote if a mapped circuit beats the declared denominator at fixed observable error after preparation and measurement costs.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# B3 Hamiltonian Pauli Mapper Comparison v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source FCI method: {report['source_fci_method']}",
        f"- Instances: {report['summary']['instance_count']}",
        f"- QASM files: {report['summary']['qasm_file_count']}",
        f"- Max qubits: {report['summary']['max_total_qubits']}",
        f"- Max mapped Pauli terms: {report['summary']['max_pauli_terms_after_cutoff']}",
        f"- Max measurement packet terms: {report['summary']['max_measurement_packet_terms']}",
        f"- Max variance upper bound: {report['summary']['max_variance_upper_bound']:.6e}",
        f"- Max total measurement shot floor: {report['summary']['max_total_measurement_shot_floor']}",
        f"- FCI denominator beaten count: {report['summary']['fci_denominator_beaten_count']}",
        f"- State-preparation cost included: {report['summary']['state_preparation_cost_included']}",
        f"- Observable-variance estimate included: {report['summary']['observable_variance_estimate_included']}",
        f"- Quantum advantage claimed: {report['summary']['quantum_advantage_claimed']}",
        f"- Reaction-dynamics solution claimed: {report['summary']['reaction_dynamics_solution_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Rows",
        "",
        "| molecule | qubits | Pauli terms | packet terms | HF X gates | variance upper | total shot floor | FCI derivative | QASM | beats FCI? |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['molecule']} | {row['total_qubits']} | {row['pauli_terms_after_cutoff']} | "
            f"{row['measurement_packet_terms']} | {row['state_preparation_x_gates']} | "
            f"{row['variance_upper_bound']:.6e} | {row['total_measurement_shot_floor']} | "
            f"{row['fci_derivative_hartree_per_coordinate']:.6e} | `{row['qasm_path']}` | "
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
        "--fci-reference",
        type=Path,
        default=Path("results/B10_t1_d5_b3_fci_reference_table_v0.json"),
    )
    parser.add_argument(
        "--qasm-dir",
        type=Path,
        default=Path("results/b3_hamiltonian_pauli_mapper_comparison/circuits"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_hamiltonian_pauli_mapper_comparison_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_hamiltonian_pauli_mapper_comparison.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.fci_reference, args.qasm_dir)
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
                    "max_pauli_terms": report["summary"]["max_pauli_terms_after_cutoff"],
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
