#!/usr/bin/env python3
"""Build a late-bound private-challenge contract gate for the B4/B8 packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


METHOD = "b4_b8_late_bound_private_challenge_contract_gate_v0"
STATUS = "late_bound_private_challenge_contract_partial_not_protocol_soundness"
MODEL_STATUS = "private_challenge_boundary_contract_not_hardware_execution"
VERSION = "0.1"
SOURCE_METHOD = "b4_b8_openqasm3_randomized_measurement_packet_v0"

QUBIT_RE = re.compile(r"^qubit\[(\d+)\]\s+q;$")
CBIT_RE = re.compile(r"^bit\[(\d+)\]\s+c;$")
X_RE = re.compile(r"^x\s+q\[(\d+)\];$")
CX_RE = re.compile(r"^cx\s+q\[(\d+)\],\s*q\[(\d+)\];$")
MEASURE_RE = re.compile(r"^c\[(\d+)\]\s*=\s*measure\s+q\[(\d+)\];$")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_qasm_counts(qasm_text: str) -> dict[str, Any]:
    qubit_count = None
    classical_bit_count = None
    x_count = 0
    cx_count = 0
    measure_count = 0
    unsupported: list[str] = []
    for raw_line in qasm_text.splitlines():
        line = raw_line.strip()
        if not line or line == "OPENQASM 3.0;" or line == 'include "stdgates.inc";':
            continue
        if match := QUBIT_RE.match(line):
            qubit_count = int(match.group(1))
            continue
        if match := CBIT_RE.match(line):
            classical_bit_count = int(match.group(1))
            continue
        if X_RE.match(line):
            x_count += 1
            continue
        if CX_RE.match(line):
            cx_count += 1
            continue
        if MEASURE_RE.match(line):
            measure_count += 1
            continue
        unsupported.append(line)
    return {
        "qubit_count": qubit_count,
        "classical_bit_count": classical_bit_count,
        "x_count": x_count,
        "cx_count": cx_count,
        "measure_count": measure_count,
        "unsupported_line_count": len(unsupported),
        "unsupported_lines": unsupported[:5],
    }


def emulate_deterministic_qasm(qasm_text: str) -> dict[str, Any]:
    counts = parse_qasm_counts(qasm_text)
    qubits = [0] * int(counts["qubit_count"] or 0)
    cbits = [None] * int(counts["classical_bit_count"] or 0)
    unsupported: list[str] = []
    for raw_line in qasm_text.splitlines():
        line = raw_line.strip()
        if not line or line == "OPENQASM 3.0;" or line == 'include "stdgates.inc";':
            continue
        if QUBIT_RE.match(line) or CBIT_RE.match(line):
            continue
        if match := X_RE.match(line):
            qubits[int(match.group(1))] ^= 1
            continue
        if match := CX_RE.match(line):
            control = int(match.group(1))
            target = int(match.group(2))
            qubits[target] ^= qubits[control]
            continue
        if match := MEASURE_RE.match(line):
            classical = int(match.group(1))
            qubit = int(match.group(2))
            cbits[classical] = qubits[qubit]
            continue
        unsupported.append(line)
    predicted = [int(bit) if bit is not None else -1 for bit in cbits]
    return {
        "deterministic_subset_supported": not unsupported and all(bit is not None for bit in cbits),
        "predicted_bits": predicted,
        "predicted_memory": "".join(str(bit) for bit in reversed(predicted)) if predicted else "",
        "predicted_bit_weight": int(sum(predicted)) if predicted else 0,
        "unsupported_line_count": len(unsupported),
    }


def extract_private_material_from_public_packet(qasm_text: str, data_qubits: int) -> dict[str, Any]:
    ancilla_masks: dict[int, list[int]] = {}
    challenge_flips: dict[int, int] = {}
    measured_ancillas: set[int] = set()
    for raw_line in qasm_text.splitlines():
        line = raw_line.strip()
        if match := CX_RE.match(line):
            control = int(match.group(1))
            target = int(match.group(2))
            if control < data_qubits <= target:
                ancilla_masks.setdefault(target, []).append(control)
        elif match := X_RE.match(line):
            qubit = int(match.group(1))
            if qubit >= data_qubits:
                challenge_flips[qubit] = 1
        elif match := MEASURE_RE.match(line):
            qubit = int(match.group(2))
            if qubit >= data_qubits:
                measured_ancillas.add(qubit)
    mask_widths = [len(ancilla_masks.get(ancilla, [])) for ancilla in sorted(measured_ancillas)]
    return {
        "private_ancilla_count": len(measured_ancillas),
        "private_mask_count": len(mask_widths),
        "private_mask_widths": mask_widths,
        "private_challenge_flip_count": sum(challenge_flips.get(ancilla, 0) for ancilla in measured_ancillas),
        "private_material_was_embedded_in_source_public_qasm": bool(measured_ancillas),
    }


def make_public_skeleton(qasm_text: str, data_qubits: int) -> str:
    lines = ["OPENQASM 3.0;", 'include "stdgates.inc";', f"bit[{data_qubits}] c;", f"qubit[{data_qubits}] q;"]
    for raw_line in qasm_text.splitlines():
        line = raw_line.strip()
        if match := X_RE.match(line):
            qubit = int(match.group(1))
            if qubit < data_qubits:
                lines.append(f"x q[{qubit}];")
        elif match := CX_RE.match(line):
            control = int(match.group(1))
            target = int(match.group(2))
            if control < data_qubits and target < data_qubits:
                lines.append(f"cx q[{control}], q[{target}];")
    for qubit in range(data_qubits):
        lines.append(f"c[{qubit}] = measure q[{qubit}];")
    return "\n".join(lines) + "\n"


def build_gate(source_packet: Path, skeleton_dir: Path) -> dict[str, Any]:
    started = time.time()
    packet = json.loads(source_packet.read_text(encoding="utf-8"))
    skeleton_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    deterministic_skeleton_count = 0
    source_private_material_count = 0
    skeleton_private_leak_count = 0

    for circuit in packet.get("circuits", []):
        qasm_path = Path(circuit["path"])
        qasm_text = qasm_path.read_text(encoding="utf-8")
        data_qubits = int(circuit["data_qubits"])
        private_material = extract_private_material_from_public_packet(qasm_text, data_qubits)
        if private_material["private_material_was_embedded_in_source_public_qasm"]:
            source_private_material_count += 1
        skeleton_text = make_public_skeleton(qasm_text, data_qubits)
        skeleton_private_material = extract_private_material_from_public_packet(skeleton_text, data_qubits)
        if skeleton_private_material["private_material_was_embedded_in_source_public_qasm"]:
            skeleton_private_leak_count += 1
        skeleton_name = Path(circuit["path"]).name.replace(".qasm", "_public_skeleton.qasm")
        skeleton_path = skeleton_dir / skeleton_name
        skeleton_path.write_text(skeleton_text, encoding="utf-8")
        skeleton_counts = parse_qasm_counts(skeleton_text)
        skeleton_emulation = emulate_deterministic_qasm(skeleton_text)
        if skeleton_emulation["deterministic_subset_supported"]:
            deterministic_skeleton_count += 1
        rows.append(
            {
                "task_id": circuit["task_id"],
                "refresh_mode": circuit["refresh_mode"],
                "packet_index": circuit["packet_index"],
                "source_qasm_path": circuit["path"],
                "public_skeleton_path": str(skeleton_path),
                "public_skeleton_sha256": sha256_text(skeleton_text),
                "data_qubits": data_qubits,
                "source_private_mask_count": private_material["private_mask_count"],
                "source_private_challenge_flip_count": private_material["private_challenge_flip_count"],
                "source_private_material_was_embedded_in_public_qasm": private_material[
                    "private_material_was_embedded_in_source_public_qasm"
                ],
                "public_skeleton_private_material_embedded": skeleton_private_material[
                    "private_material_was_embedded_in_source_public_qasm"
                ],
                "public_skeleton_qubit_count": skeleton_counts["qubit_count"],
                "public_skeleton_classical_bit_count": skeleton_counts["classical_bit_count"],
                "public_skeleton_cx_count": skeleton_counts["cx_count"],
                "public_skeleton_x_count": skeleton_counts["x_count"],
                "public_skeleton_measure_count": skeleton_counts["measure_count"],
                "public_skeleton_deterministic_emulator_supported": skeleton_emulation[
                    "deterministic_subset_supported"
                ],
                "public_skeleton_predicted_memory": skeleton_emulation["predicted_memory"],
                "late_bound_parity_answer_computable_from_public_data_transcript": skeleton_emulation[
                    "deterministic_subset_supported"
                ],
            }
        )

    packet_circuit_count = len(packet.get("circuits", []))
    public_skeletons_hide_private_material = skeleton_private_leak_count == 0 and packet_circuit_count > 0
    public_data_deterministic = deterministic_skeleton_count == packet_circuit_count and packet_circuit_count > 0
    acceptance_gates = [
        {
            "gate": "source_public_packet_private_material_detected",
            "passed": source_private_material_count == packet_circuit_count,
            "interpretation": "The prior public packet did embed verifier masks/flips and is unsuitable as a public protocol.",
        },
        {
            "gate": "public_skeletons_hide_private_material",
            "passed": public_skeletons_hide_private_material,
            "interpretation": "The generated public skeletons remove ancilla masks and challenge flips.",
        },
        {
            "gate": "raw_private_masks_not_persisted_in_contract",
            "passed": True,
            "interpretation": "The contract records mask/flip counts only and does not persist raw private masks.",
        },
        {
            "gate": "public_data_transcript_not_classically_predictable",
            "passed": not public_data_deterministic,
            "interpretation": "Fails for the current deterministic CNOT skeletons.",
        },
        {
            "gate": "non_stabilizer_or_hardware_entropy_source_present",
            "passed": False,
            "interpretation": "No non-stabilizer randomness or hardware entropy is present in this contract gate.",
        },
        {
            "gate": "real_backend_or_hardware_execution_present",
            "passed": False,
            "interpretation": "No real backend properties or hardware execution are used.",
        },
        {
            "gate": "late_bound_challenge_alone_sufficient_for_soundness",
            "passed": False,
            "interpretation": "Late-bound masks alone are insufficient when the full public data transcript is predictable.",
        },
        {
            "gate": "no_forbidden_claims",
            "passed": True,
            "interpretation": "The result keeps hardware, hardness, soundness, advantage, and BQP claims false.",
        },
    ]
    passed_gate_count = sum(1 for gate in acceptance_gates if gate["passed"])
    failed_gate_count = len(acceptance_gates) - passed_gate_count
    report = {
        "benchmark_id": "B4_B8",
        "problem_ids": [16, 30, 11],
        "title": "B4/B8 late-bound private challenge contract gate",
        "version": VERSION,
        "last_updated": time.strftime("%Y-%m-%d"),
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_method": SOURCE_METHOD,
        "source_packet_result": str(source_packet),
        "public_skeleton_directory": str(skeleton_dir),
        "packet_circuit_count": packet_circuit_count,
        "public_skeleton_file_count": len(rows),
        "source_private_material_embedded_file_count": source_private_material_count,
        "public_skeleton_private_material_embedded_file_count": skeleton_private_leak_count,
        "public_skeletons_hide_private_material": public_skeletons_hide_private_material,
        "public_skeleton_deterministic_emulator_file_count": deterministic_skeleton_count,
        "public_data_transcript_classically_predictable": public_data_deterministic,
        "late_bound_parity_answer_computable_from_public_data_transcript": public_data_deterministic,
        "late_bound_private_challenge_contract_defined": True,
        "late_bound_private_challenge_alone_sufficient_for_soundness": False,
        "non_stabilizer_or_hardware_entropy_source_present": False,
        "real_backend_or_hardware_execution_present": False,
        "acceptance_gate_count": len(acceptance_gates),
        "passed_gate_count": passed_gate_count,
        "failed_gate_count": failed_gate_count,
        "acceptance_gates": acceptance_gates,
        "hardware_execution_performed": False,
        "real_backend_properties_used": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "sampling_hardness_proved": False,
        "cryptographic_soundness_proved": False,
        "protocol_soundness_proved": False,
        "rows": rows,
        "claim_boundary": {
            "what_is_supported": (
                "A public/private separation contract can remove verifier masks and challenge flips from "
                "public QASM skeletons."
            ),
            "what_is_not_supported": (
                "For the current deterministic CNOT data skeletons, late-bound private parity challenges "
                "alone do not create protocol soundness because a public emulator can predict the data transcript."
            ),
            "next_gate": (
                "Combine late-bound private challenges with non-stabilizer task structure, real backend "
                "properties, hardware execution, or transcripts not classically predictable from public QASM."
            ),
        },
        "runtime_seconds": round(time.time() - started, 6),
    }
    report["validation_errors"] = validate_report(report)
    return report


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("status") != STATUS:
        errors.append("status mismatch")
    if report.get("method") != METHOD:
        errors.append("method mismatch")
    if report.get("packet_circuit_count") != 36:
        errors.append("source packet must contain 36 circuits")
    if report.get("public_skeleton_file_count") != report.get("packet_circuit_count"):
        errors.append("public skeleton count must equal packet circuit count")
    if report.get("source_private_material_embedded_file_count") != report.get("packet_circuit_count"):
        errors.append("source packet should expose private verifier material in every verifier circuit")
    if report.get("public_skeleton_private_material_embedded_file_count") != 0:
        errors.append("public skeletons must not embed verifier-private masks/flips")
    if report.get("public_skeletons_hide_private_material") is not True:
        errors.append("public skeleton private-material separation should pass")
    if report.get("public_data_transcript_classically_predictable") is not True:
        errors.append("current public data skeletons should remain classically predictable")
    if report.get("late_bound_private_challenge_alone_sufficient_for_soundness") is not False:
        errors.append("late-bound challenge alone must not be marked sufficient")
    if report.get("failed_gate_count", 0) < 3:
        errors.append("contract should keep the unsolved gates visible")
    for field in [
        "hardware_execution_performed",
        "real_backend_properties_used",
        "quantum_advantage_claimed",
        "bqp_separation_claimed",
        "sampling_hardness_proved",
        "cryptographic_soundness_proved",
        "protocol_soundness_proved",
    ]:
        if report.get(field) is not False:
            errors.append(f"must keep {field}=False")
    return errors


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# B4/B8 Late-Bound Private Challenge Contract Gate v0.1",
        "",
        f"Last updated: {report['last_updated']}",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source packet: `{report['source_packet_result']}`",
        f"- Public skeleton directory: `{report['public_skeleton_directory']}`",
        f"- Packet circuits: {report['packet_circuit_count']}",
        f"- Public skeleton files: {report['public_skeleton_file_count']}",
        f"- Source files with embedded private verifier material: {report['source_private_material_embedded_file_count']}",
        f"- Public skeletons with embedded private verifier material: {report['public_skeleton_private_material_embedded_file_count']}",
        f"- Public skeletons hide private material: {report['public_skeletons_hide_private_material']}",
        f"- Public data transcript classically predictable: {report['public_data_transcript_classically_predictable']}",
        f"- Late-bound private challenge alone sufficient: {report['late_bound_private_challenge_alone_sufficient_for_soundness']}",
        f"- Acceptance gates passed / failed: {report['passed_gate_count']} / {report['failed_gate_count']}",
        "",
        "## Interpretation",
        "",
        (
            "This gate is a contract boundary, not a soundness result. It shows that we can remove "
            "verifier masks and challenge flips from public QASM skeletons, but the current public data "
            "skeletons are deterministic X/CX/measure circuits. A public emulator can predict their data "
            "transcripts, so late-bound private parity challenges alone are not enough."
        ),
        "",
        "## Acceptance Gates",
        "",
    ]
    for gate in report["acceptance_gates"]:
        mark = "PASS" if gate["passed"] else "FAIL"
        lines.append(f"- {mark}: `{gate['gate']}` - {gate['interpretation']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Not hardware execution.",
            "- Not real backend properties.",
            "- Not cryptographic soundness.",
            "- Not sampling hardness.",
            "- Not quantum advantage.",
            "- Not BQP separation.",
            "",
            "## Next Gate",
            "",
            (
                "Combine late-bound private challenges with non-stabilizer task structure, real backend "
                "properties, hardware execution, or transcripts not classically predictable from public QASM."
            ),
            "",
            "## Validation",
            "",
            f"- Validation errors: {len(report['validation_errors'])}",
        ]
    )
    if report["validation_errors"]:
        lines.extend([f"  - {error}" for error in report["validation_errors"]])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-packet",
        type=Path,
        default=Path("results/B4_B8_openqasm3_randomized_measurement_packet_v0.json"),
    )
    parser.add_argument(
        "--skeleton-dir",
        type=Path,
        default=Path("results/B4_B8_late_bound_private_challenge_contract/public_skeletons"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B4_B8_late_bound_private_challenge_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B4_B8_late_bound_private_challenge_contract_gate.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_gate(args.source_packet, args.skeleton_dir)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "public_skeleton_file_count": report["public_skeleton_file_count"],
                    "public_skeletons_hide_private_material": report["public_skeletons_hide_private_material"],
                    "public_data_transcript_classically_predictable": report[
                        "public_data_transcript_classically_predictable"
                    ],
                    "passed_gate_count": report["passed_gate_count"],
                    "failed_gate_count": report["failed_gate_count"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
