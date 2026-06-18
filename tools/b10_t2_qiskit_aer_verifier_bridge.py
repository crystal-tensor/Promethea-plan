#!/usr/bin/env python3
"""Instantiate B10-T2 randomized parity verifier circuits and cross-check with Qiskit Aer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from b4_b8_circuit_refresh_task import (
    build_tasks,
    gf2_inverse,
    parse_int_list,
    parse_str_list,
    verify_samples,
)
from b10_t2_device_noise_transcript_bridge import BRIDGE_SAFE_REFRESH_MODES
from b10_t2_transcript_leakage_simulator import honest_samples, refreshed_masks, target_vector


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def output_to_input_bits(output_bits: np.ndarray, inverse_matrix: np.ndarray) -> np.ndarray:
    return (output_bits.astype(np.uint8) @ inverse_matrix.T) % 2


def build_verifier_circuit(
    task: dict,
    input_bits: np.ndarray,
    masks: list[list[int]],
    challenge_flips: np.ndarray,
) -> QuantumCircuit:
    data_qubits = int(task["qubits"])
    predicate_count = len(masks)
    circuit = QuantumCircuit(data_qubits + predicate_count, predicate_count)
    for qubit, bit in enumerate(input_bits.tolist()):
        if int(bit):
            circuit.x(qubit)
    for control, target in task["gates"]:
        circuit.cx(int(control), int(target))
    for predicate_idx, mask in enumerate(masks):
        ancilla = data_qubits + predicate_idx
        for qubit in mask:
            circuit.cx(int(qubit), ancilla)
        if int(challenge_flips[predicate_idx]):
            circuit.x(ancilla)
        circuit.measure(ancilla, predicate_idx)
    return circuit


def decode_memory(memory: str, predicate_count: int, challenge_flips: np.ndarray) -> np.ndarray:
    bits = np.array([int(bit) for bit in memory[::-1][:predicate_count]], dtype=np.int8)
    return bits ^ challenge_flips.astype(np.int8)


def run_aer_batch(
    circuits: list[QuantumCircuit],
    predicate_count: int,
    challenge_flips: list[np.ndarray],
    seed: int,
) -> np.ndarray:
    simulator = AerSimulator(method="stabilizer", seed_simulator=seed)
    result = simulator.run(circuits, shots=1, memory=True).result()
    measured = []
    for idx in range(len(circuits)):
        memory = result.get_memory(idx)[0]
        measured.append(decode_memory(memory, predicate_count, challenge_flips[idx]))
    return np.array(measured, dtype=np.int8)


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "qiskit_aer_circuit_level_verifier_bridge_not_hardware_execution":
        errors.append("status must identify Qiskit/Aer bridge as not hardware execution")
    if report.get("source_target_id") != "B10-T2":
        errors.append("source target must be B10-T2")
    if report.get("qiskit_aer_bridge_instantiated") is not True:
        errors.append("Qiskit/Aer bridge must be instantiated")
    if report.get("hardware_executable_randomized_measurement_circuits_instantiated") is not True:
        errors.append("hardware-executable randomized measurement circuits should be instantiated")
    if report.get("hardware_execution_performed") is not False:
        errors.append("bridge must not claim hardware execution")
    if report.get("sampling_hardness_proved") is not False:
        errors.append("bridge must not claim sampling hardness")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("bridge must explicitly avoid BQP separation claims")
    if report.get("aer_semantic_mismatch_count") != 0:
        errors.append("ideal Aer verifier circuits should have zero semantic mismatches")
    if float(report.get("minimum_aer_honest_completeness", 0.0)) < 0.99:
        errors.append("ideal Aer honest completeness should be near 1.0")
    if float(report.get("source_device_noise_max_safe_high_leakage_soundness", 1.0)) > 0.05:
        errors.append("source device-noise bridge should keep safe high-leakage soundness below 5%")
    if "projection_rotation" not in report.get("source_margin_sensitive_refresh_modes", []):
        errors.append("source bridge should preserve projection_rotation as margin-sensitive")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def run(
    qubits: list[int],
    invariant_count: int,
    circuit_depth_factor: int,
    refresh_modes: list[str],
    aer_trials: int,
    tolerance: float,
    seed: int,
    source_device_noise_bridge_path: Path,
) -> dict:
    rng = np.random.default_rng(seed)
    tasks = build_tasks(qubits, invariant_count, circuit_depth_factor, seed + 15000)
    source_bridge = load_json(source_device_noise_bridge_path)

    rows = []
    circuit_count = 0
    semantic_mismatch_count = 0
    max_qubits_with_ancilla = 0

    for task in tasks:
        inverse_matrix = gf2_inverse(task["matrix"])
        for refresh_mode in refresh_modes:
            masks = refreshed_masks(task, refresh_mode, invariant_count, rng)
            targets = target_vector(len(masks), task["qubits"])
            desired_outputs = honest_samples(
                task["qubits"],
                aer_trials,
                masks,
                targets,
                honest_bias=1.0,
                rng=rng,
            )
            circuits = []
            challenge_flips = []
            expected_bits = []
            for output_bits in desired_outputs:
                input_bits = output_to_input_bits(output_bits, inverse_matrix)
                flips = rng.integers(0, 2, size=len(masks), dtype=np.int8)
                circuits.append(build_verifier_circuit(task, input_bits, masks, flips))
                challenge_flips.append(flips)
                expected_bits.append(((1 - targets) // 2).astype(np.int8))
            measured_bits = run_aer_batch(
                circuits,
                predicate_count=len(masks),
                challenge_flips=challenge_flips,
                seed=seed + circuit_count + 1,
            )
            expected = np.array(expected_bits, dtype=np.int8)
            mismatches = int(np.sum(measured_bits != expected))
            semantic_mismatch_count += mismatches
            circuit_count += len(circuits)
            max_qubits_with_ancilla = max(max_qubits_with_ancilla, task["qubits"] + len(masks))

            measured_signs = 1 - 2 * measured_bits
            reference_means = targets.astype(float)
            verify_result = verify_samples(measured_bits, [[idx] for idx in range(len(masks))], reference_means, tolerance)
            # verify_samples expects sample bit parities; single-coordinate masks on decoded predicate bits match signs.
            rows.append(
                {
                    "task_id": task["task_id"],
                    "qubits": task["qubits"],
                    "ancilla_qubits": len(masks),
                    "total_circuit_qubits": task["qubits"] + len(masks),
                    "refresh_mode": refresh_mode,
                    "aer_circuits": len(circuits),
                    "semantic_mismatch_count": mismatches,
                    "predicate_bit_error_rate": float(np.mean(measured_bits != expected)),
                    "honest_completeness": 1.0 if verify_result["passed"] else 0.0,
                    "max_abs_error": verify_result["max_abs_error"],
                    "mean_observed_sign": [float(x) for x in measured_signs.mean(axis=0)],
                    "targets": [int(x) for x in targets.tolist()],
                }
            )

    bridge_safe_modes = sorted(set(source_bridge.get("bridge_safe_refresh_modes", [])))
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T2 Qiskit/Aer circuit-level verifier bridge",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "qiskit_aer_circuit_level_verifier_bridge_not_hardware_execution",
        "method": "b10_t2_qiskit_aer_verifier_bridge_v0",
        "source_target_id": "B10-T2",
        "source_device_noise_bridge": "b10_t2_device_noise_transcript_bridge_v0",
        "dependency_benchmark": "B8",
        "qiskit_aer_bridge_instantiated": True,
        "hardware_executable_randomized_measurement_circuits_instantiated": True,
        "hardware_execution_performed": False,
        "sampling_hardness_proved": False,
        "explicit_not_bqp_separation": True,
        "task_count": len(tasks),
        "refresh_modes": refresh_modes,
        "bridge_safe_refresh_modes": bridge_safe_modes,
        "aer_trial_circuits_per_task_mode": aer_trials,
        "aer_circuit_count": circuit_count,
        "max_circuit_qubits_with_ancilla": max_qubits_with_ancilla,
        "aer_semantic_mismatch_count": semantic_mismatch_count,
        "minimum_aer_honest_completeness": min(row["honest_completeness"] for row in rows),
        "maximum_aer_predicate_bit_error_rate": max(row["predicate_bit_error_rate"] for row in rows),
        "source_device_noise_max_safe_high_leakage_soundness": source_bridge.get(
            "max_soundness_bridge_safe_high_leakage"
        ),
        "source_device_noise_min_unknown_independent_count": source_bridge.get(
            "min_unknown_independent_count_bridge_safe_high_leakage"
        ),
        "source_margin_sensitive_refresh_modes": source_bridge.get("margin_sensitive_refresh_modes", []),
        "source_unsafe_device_profiles": source_bridge.get("unsafe_device_profiles", []),
        "results": rows,
        "limits": [
            "Qiskit/Aer executes ideal randomized parity verifier circuits, not real hardware.",
            "The adversary and device-noise stress metrics are inherited from the transcript-level device-noise bridge.",
            "The circuit bridge proves semantic consistency of the verifier circuit construction, not sampling hardness.",
            "No BQP/classical separation, cryptographic soundness theorem, or calibrated-device claim is made.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B10-T2 Qiskit/Aer Circuit-Level Verifier Bridge v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']}",
        f"- Source device-noise bridge: {report['source_device_noise_bridge']}",
        f"- Method: {report['method']}",
        f"- Qiskit/Aer bridge instantiated: {report['qiskit_aer_bridge_instantiated']}",
        f"- Hardware-executable randomized measurement circuits instantiated: {report['hardware_executable_randomized_measurement_circuits_instantiated']}",
        f"- Hardware execution performed: {report['hardware_execution_performed']}",
        f"- Aer circuit count: {report['aer_circuit_count']}",
        f"- Max circuit qubits including verifier ancillas: {report['max_circuit_qubits_with_ancilla']}",
        f"- Aer semantic mismatch count: {report['aer_semantic_mismatch_count']}",
        f"- Minimum Aer honest completeness: {report['minimum_aer_honest_completeness']:.3f}",
        f"- Source device-noise safe high-leakage max soundness: {report['source_device_noise_max_safe_high_leakage_soundness']}",
        f"- Source margin-sensitive refresh modes: {report['source_margin_sensitive_refresh_modes']}",
        f"- Source unsafe device profiles: {report['source_unsafe_device_profiles']}",
        f"- Sampling hardness proved: {report['sampling_hardness_proved']}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Aer Circuit Semantic Checks",
        "",
        "| task | mode | data qubits | ancillas | circuits | mismatches | bit error | honest completeness |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["results"]:
        lines.append(
            f"| {row['task_id']} | {row['refresh_mode']} | {row['qubits']} | {row['ancilla_qubits']} | "
            f"{row['aer_circuits']} | {row['semantic_mismatch_count']} | "
            f"{row['predicate_bit_error_rate']:.3f} | {row['honest_completeness']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Supported: the hidden-predicate verifier has explicit Qiskit circuits with randomized ancilla challenge flips and ideal Aer semantic checks.",
            "- Inherited: device-noise/adversary soundness comes from the transcript-level device-noise bridge, where challenge_refresh and refresh_plus_rotation remain bridge-safe.",
            "- Not claimed: real hardware execution, sampling hardness, cryptographic soundness, or BQP/classical separation.",
            "",
            "## Limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", default="12,16,20")
    parser.add_argument("--invariant-count", type=int, default=10)
    parser.add_argument("--circuit-depth-factor", type=int, default=4)
    parser.add_argument("--refresh-modes", default="projection_rotation,challenge_refresh,refresh_plus_rotation")
    parser.add_argument("--aer-trials", type=int, default=24)
    parser.add_argument("--tolerance", type=float, default=0.02)
    parser.add_argument("--seed", type=int, default=20260617)
    parser.add_argument(
        "--source-device-noise-bridge",
        type=Path,
        default=Path("results/B10_t2_device_noise_transcript_bridge_v0.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t2_qiskit_aer_verifier_bridge_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t2_qiskit_aer_verifier_bridge.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(
        qubits=parse_int_list(args.qubits),
        invariant_count=args.invariant_count,
        circuit_depth_factor=args.circuit_depth_factor,
        refresh_modes=parse_str_list(args.refresh_modes),
        aer_trials=args.aer_trials,
        tolerance=args.tolerance,
        seed=args.seed,
        source_device_noise_bridge_path=args.source_device_noise_bridge,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "aer_circuit_count": report["aer_circuit_count"],
                    "aer_semantic_mismatch_count": report["aer_semantic_mismatch_count"],
                    "minimum_aer_honest_completeness": report["minimum_aer_honest_completeness"],
                    "source_device_noise_max_safe_high_leakage_soundness": report[
                        "source_device_noise_max_safe_high_leakage_soundness"
                    ],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
