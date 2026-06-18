#!/usr/bin/env python3
"""Run B10-T2 randomized parity verifier circuits under noisy Qiskit Aer models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error, pauli_error

from b4_b8_circuit_refresh_task import build_tasks, gf2_inverse, parse_int_list, parse_str_list, verify_samples
from b10_t2_device_noise_transcript_bridge import (
    BRIDGE_SAFE_REFRESH_MODES,
    DEVICE_NOISE_PROFILES,
    device_transcript_for_mode,
)
from b10_t2_qiskit_aer_verifier_bridge import build_verifier_circuit, decode_memory, output_to_input_bits
from b10_t2_transcript_leakage_simulator import ADVERSARIES, adversary_transcript_samples, honest_samples


PROFILE_TO_AER_NOISE = {
    "ideal_transcript": {
        "one_qubit_x": 0.0,
        "cx_depolarizing": 0.0,
    },
    "low_noise_bridge": {
        "one_qubit_x": 0.001,
        "cx_depolarizing": 0.002,
    },
    "readout_biased_bridge": {
        "one_qubit_x": 0.0015,
        "cx_depolarizing": 0.003,
    },
    "drift_correlated_bridge": {
        "one_qubit_x": 0.003,
        "cx_depolarizing": 0.006,
    },
    "calibration_side_channel": {
        "one_qubit_x": 0.0015,
        "cx_depolarizing": 0.003,
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_noise_model(profile_name: str) -> NoiseModel:
    profile = DEVICE_NOISE_PROFILES[profile_name]
    aer_noise = PROFILE_TO_AER_NOISE[profile_name]
    model = NoiseModel()

    one_qubit_x = float(aer_noise["one_qubit_x"])
    if one_qubit_x > 0:
        model.add_all_qubit_quantum_error(
            pauli_error([("X", one_qubit_x), ("I", 1.0 - one_qubit_x)]),
            ["x"],
        )

    cx_depolarizing = float(aer_noise["cx_depolarizing"])
    if cx_depolarizing > 0:
        model.add_all_qubit_quantum_error(depolarizing_error(cx_depolarizing, 2), ["cx"])

    readout_0_to_1 = float(profile["readout_0_to_1"])
    readout_1_to_0 = float(profile["readout_1_to_0"])
    if readout_0_to_1 > 0 or readout_1_to_0 > 0:
        model.add_all_qubit_readout_error(
            ReadoutError(
                [
                    [1.0 - readout_0_to_1, readout_0_to_1],
                    [readout_1_to_0, 1.0 - readout_1_to_0],
                ]
            )
        )
    return model


def run_noisy_aer_batch(
    circuits: list[QuantumCircuit],
    predicate_count: int,
    challenge_flips: list[np.ndarray],
    profile_name: str,
    seed: int,
) -> np.ndarray:
    simulator = AerSimulator(
        method="stabilizer",
        noise_model=build_noise_model(profile_name),
        seed_simulator=seed,
    )
    result = simulator.run(circuits, shots=1, memory=True).result()
    measured = []
    for idx in range(len(circuits)):
        memory = result.get_memory(idx)[0]
        measured.append(decode_memory(memory, predicate_count, challenge_flips[idx]))
    return np.array(measured, dtype=np.int8)


def output_samples_to_verifier_circuits(
    task: dict,
    output_samples: np.ndarray,
    inverse_matrix: np.ndarray,
    masks: list[list[int]],
    rng: np.random.Generator,
) -> tuple[list[QuantumCircuit], list[np.ndarray]]:
    circuits = []
    challenge_flips = []
    for output_bits in output_samples:
        input_bits = output_to_input_bits(output_bits, inverse_matrix)
        flips = rng.integers(0, 2, size=len(masks), dtype=np.int8)
        circuits.append(build_verifier_circuit(task, input_bits, masks, flips))
        challenge_flips.append(flips)
    return circuits, challenge_flips


def evaluate_samples(
    measured_bits: np.ndarray,
    targets: np.ndarray,
    tolerance: float,
) -> dict:
    expected_bits = ((1 - targets) // 2).astype(np.int8)
    verify_result = verify_samples(
        measured_bits,
        [[idx] for idx in range(len(targets))],
        targets.astype(float),
        tolerance,
    )
    return {
        "accepted": bool(verify_result["passed"]),
        "max_abs_error": float(verify_result["max_abs_error"]),
        "predicate_bit_error_rate": float(np.mean(measured_bits != expected_bits)),
    }


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "noisy_aer_circuit_verifier_bridge_not_hardware_execution":
        errors.append("status must identify noisy Aer bridge as not hardware execution")
    if report.get("source_target_id") != "B10-T2":
        errors.append("source target must be B10-T2")
    if report.get("noisy_qiskit_aer_bridge_instantiated") is not True:
        errors.append("noisy Qiskit/Aer bridge must be instantiated")
    if report.get("circuit_level_adversary_inputs_instantiated") is not True:
        errors.append("circuit-level adversary inputs should be instantiated")
    if report.get("hardware_execution_performed") is not False:
        errors.append("bridge must not claim hardware execution")
    if report.get("sampling_hardness_proved") is not False:
        errors.append("bridge must not claim sampling hardness")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("bridge must explicitly avoid BQP separation claims")
    if int(report.get("noisy_aer_circuit_count", 0)) <= int(report.get("source_aer_circuit_count", 0)):
        errors.append("noisy bridge should execute more circuits than the ideal semantic bridge")
    if float(report.get("minimum_safe_noisy_honest_acceptance", 0.0)) < 0.75:
        errors.append("bridge-safe noisy honest acceptance should remain at least 0.75")
    if float(report.get("maximum_safe_noisy_adversary_acceptance", 1.0)) > 0.35:
        errors.append("bridge-safe noisy adversary acceptance should stay below 0.35")
    if float(report.get("source_device_noise_max_safe_high_leakage_soundness", 1.0)) > 0.05:
        errors.append("source transcript bridge should keep safe high-leakage soundness below 5%")
    if "calibration_side_channel" not in report.get("unsafe_noisy_device_profiles", []):
        errors.append("calibration side-channel noisy profile should be rejected")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def run(
    qubits: list[int],
    invariant_count: int,
    circuit_depth_factor: int,
    refresh_modes: list[str],
    device_profiles: list[str],
    sample_count: int,
    trials: int,
    leakage_fraction: float,
    tolerance: float,
    seed: int,
    source_ideal_bridge_path: Path,
    source_device_noise_bridge_path: Path,
) -> dict:
    rng = np.random.default_rng(seed)
    tasks = build_tasks(qubits, invariant_count, circuit_depth_factor, seed + 17000)
    source_ideal_bridge = load_json(source_ideal_bridge_path)
    source_device_bridge = load_json(source_device_noise_bridge_path)
    adversaries = sorted(ADVERSARIES)

    rows = []
    circuit_count = 0
    max_qubits_with_ancilla = 0

    for task in tasks:
        inverse_matrix = gf2_inverse(task["matrix"])
        for profile_name in device_profiles:
            profile = DEVICE_NOISE_PROFILES[profile_name]
            for refresh_mode in refresh_modes:
                honest_accepts = []
                honest_errors = []
                honest_bit_errors = []
                adversary_accepts = {name: [] for name in adversaries}
                adversary_errors = {name: [] for name in adversaries}
                adversary_bit_errors = {name: [] for name in adversaries}
                unknown_counts = []
                independence_flags = []

                for trial_idx in range(trials):
                    transcript = device_transcript_for_mode(
                        task,
                        refresh_mode,
                        leakage_fraction,
                        invariant_count,
                        profile,
                        rng,
                    )
                    masks = transcript["masks"]
                    targets = transcript["targets"]
                    unknown_counts.append(transcript["unknown_independent_count"])
                    independence_flags.append(transcript["refresh_independence_holds"])
                    max_qubits_with_ancilla = max(max_qubits_with_ancilla, task["qubits"] + len(masks))

                    honest_outputs = honest_samples(
                        task["qubits"],
                        sample_count,
                        masks,
                        targets,
                        honest_bias=1.0,
                        rng=rng,
                    )
                    circuits, flips = output_samples_to_verifier_circuits(
                        task,
                        honest_outputs,
                        inverse_matrix,
                        masks,
                        rng,
                    )
                    measured = run_noisy_aer_batch(
                        circuits,
                        len(masks),
                        flips,
                        profile_name,
                        seed + circuit_count + trial_idx + 1,
                    )
                    circuit_count += len(circuits)
                    honest_result = evaluate_samples(measured, targets, tolerance)
                    honest_accepts.append(honest_result["accepted"])
                    honest_errors.append(honest_result["max_abs_error"])
                    honest_bit_errors.append(honest_result["predicate_bit_error_rate"])

                    for adversary in adversaries:
                        adversary_outputs, _, _ = adversary_transcript_samples(
                            task,
                            transcript,
                            refresh_mode,
                            adversary,
                            sample_count,
                            rng,
                        )
                        circuits, flips = output_samples_to_verifier_circuits(
                            task,
                            adversary_outputs,
                            inverse_matrix,
                            masks,
                            rng,
                        )
                        measured = run_noisy_aer_batch(
                            circuits,
                            len(masks),
                            flips,
                            profile_name,
                            seed + circuit_count + trial_idx + 1009,
                        )
                        circuit_count += len(circuits)
                        adversary_result = evaluate_samples(measured, targets, tolerance)
                        adversary_accepts[adversary].append(adversary_result["accepted"])
                        adversary_errors[adversary].append(adversary_result["max_abs_error"])
                        adversary_bit_errors[adversary].append(adversary_result["predicate_bit_error_rate"])

                for adversary in adversaries:
                    rows.append(
                        {
                            "task_id": task["task_id"],
                            "qubits": task["qubits"],
                            "device_profile": profile_name,
                            "bounded_bridge_profile": bool(profile["bounded_bridge_profile"]),
                            "refresh_mode": refresh_mode,
                            "leakage_fraction": leakage_fraction,
                            "adversary": adversary,
                            "aer_noise_profile": PROFILE_TO_AER_NOISE[profile_name],
                            "sample_count_per_trial": sample_count,
                            "trials": trials,
                            "mean_unknown_independent_predicate_count": float(np.mean(unknown_counts)),
                            "refresh_independence_holds": bool(all(independence_flags)),
                            "honest_acceptance": float(np.mean(honest_accepts)),
                            "mean_honest_max_abs_error": float(np.mean(honest_errors)),
                            "mean_honest_predicate_bit_error_rate": float(np.mean(honest_bit_errors)),
                            "adversary_acceptance": float(np.mean(adversary_accepts[adversary])),
                            "mean_adversary_max_abs_error": float(np.mean(adversary_errors[adversary])),
                            "mean_adversary_predicate_bit_error_rate": float(np.mean(adversary_bit_errors[adversary])),
                        }
                    )

    high_leakage_safe = [
        row
        for row in rows
        if row["bounded_bridge_profile"]
        and row["refresh_mode"] in BRIDGE_SAFE_REFRESH_MODES
        and row["refresh_independence_holds"]
    ]
    unsafe_profiles = sorted(
        {
            row["device_profile"]
            for row in rows
            if (
                not row["bounded_bridge_profile"]
                or (
                    row["refresh_mode"] in BRIDGE_SAFE_REFRESH_MODES
                    and row["bounded_bridge_profile"]
                    and row["refresh_independence_holds"]
                    and (row["adversary_acceptance"] > 0.35 or row["honest_acceptance"] < 0.75)
                )
            )
        }
    )
    unsafe_refresh_modes = sorted(
        {
            row["refresh_mode"]
            for row in rows
            if row["bounded_bridge_profile"]
            and (row["adversary_acceptance"] > 0.35 or not row["refresh_independence_holds"])
        }
    )
    bridge_safe_profiles = sorted({row["device_profile"] for row in high_leakage_safe})

    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T2 noisy Qiskit/Aer verifier bridge",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "noisy_aer_circuit_verifier_bridge_not_hardware_execution",
        "method": "b10_t2_noisy_aer_verifier_bridge_v0",
        "source_target_id": "B10-T2",
        "source_ideal_aer_bridge": "b10_t2_qiskit_aer_verifier_bridge_v0",
        "source_device_noise_bridge": "b10_t2_device_noise_transcript_bridge_v0",
        "dependency_benchmark": "B8",
        "noisy_qiskit_aer_bridge_instantiated": True,
        "circuit_level_adversary_inputs_instantiated": True,
        "hardware_execution_performed": False,
        "sampling_hardness_proved": False,
        "explicit_not_bqp_separation": True,
        "task_count": len(tasks),
        "refresh_modes": refresh_modes,
        "device_profiles": device_profiles,
        "adversaries_tested": adversaries,
        "sample_count_per_trial": sample_count,
        "trials_per_configuration": trials,
        "leakage_fraction": leakage_fraction,
        "tolerance": tolerance,
        "source_aer_circuit_count": source_ideal_bridge.get("aer_circuit_count"),
        "noisy_aer_circuit_count": circuit_count,
        "max_circuit_qubits_with_ancilla": max_qubits_with_ancilla,
        "source_device_noise_max_safe_high_leakage_soundness": source_device_bridge.get(
            "max_soundness_bridge_safe_high_leakage"
        ),
        "source_device_noise_bridge_safe_refresh_modes": source_device_bridge.get("bridge_safe_refresh_modes", []),
        "bridge_safe_refresh_modes": sorted(BRIDGE_SAFE_REFRESH_MODES),
        "bridge_safe_noisy_device_profiles": bridge_safe_profiles,
        "minimum_safe_noisy_honest_acceptance": min(row["honest_acceptance"] for row in high_leakage_safe),
        "maximum_safe_noisy_adversary_acceptance": max(row["adversary_acceptance"] for row in high_leakage_safe),
        "maximum_safe_noisy_honest_predicate_bit_error_rate": max(
            row["mean_honest_predicate_bit_error_rate"] for row in high_leakage_safe
        ),
        "minimum_safe_noisy_unknown_independent_count": min(
            row["mean_unknown_independent_predicate_count"] for row in high_leakage_safe
        ),
        "unsafe_noisy_device_profiles": unsafe_profiles,
        "unsafe_noisy_refresh_modes": unsafe_refresh_modes,
        "results": rows,
        "limits": [
            "This executes noisy Qiskit/Aer stabilizer circuits, not a calibrated physical backend.",
            "Circuit-level adversary inputs are generated by choosing adversarial verifier-output bit strings and inverting the CNOT task map.",
            "The Aer noise model uses Pauli and readout errors derived from transcript bridge profiles; it does not model coherent drift, leakage outside the computational subspace, or backend calibration history.",
            "The transcript bridge remains the source of the stricter <=5% empirical soundness claim.",
            "No BQP/classical separation, sampling-hardness proof, cryptographic soundness theorem, or hardware-verifier claim is made.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B10-T2 Noisy Qiskit/Aer Verifier Bridge v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']}",
        f"- Source ideal Aer bridge: {report['source_ideal_aer_bridge']}",
        f"- Source device-noise bridge: {report['source_device_noise_bridge']}",
        f"- Method: {report['method']}",
        f"- Noisy Qiskit/Aer bridge instantiated: {report['noisy_qiskit_aer_bridge_instantiated']}",
        f"- Circuit-level adversary inputs instantiated: {report['circuit_level_adversary_inputs_instantiated']}",
        f"- Hardware execution performed: {report['hardware_execution_performed']}",
        f"- Noisy Aer circuits executed: {report['noisy_aer_circuit_count']}",
        f"- Max circuit qubits including verifier ancillas: {report['max_circuit_qubits_with_ancilla']}",
        f"- Bridge-safe noisy honest acceptance: {report['minimum_safe_noisy_honest_acceptance']:.3f}",
        f"- Bridge-safe noisy adversary acceptance: {report['maximum_safe_noisy_adversary_acceptance']:.3f}",
        f"- Bridge-safe noisy honest predicate-bit error: {report['maximum_safe_noisy_honest_predicate_bit_error_rate']:.3f}",
        f"- Bridge-safe min unknown independent predicates: {report['minimum_safe_noisy_unknown_independent_count']:.1f}",
        f"- Source transcript safe high-leakage soundness: {report['source_device_noise_max_safe_high_leakage_soundness']}",
        f"- Unsafe noisy device profiles: {report['unsafe_noisy_device_profiles']}",
        f"- Unsafe noisy refresh modes: {report['unsafe_noisy_refresh_modes']}",
        f"- Sampling hardness proved: {report['sampling_hardness_proved']}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## High-Leakage Noisy Circuit Rows",
        "",
        "| task | profile | mode | adversary | honest accept | adversary accept | honest bit error | unknown predicates | independence |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["results"]:
        lines.append(
            f"| {row['task_id']} | {row['device_profile']} | {row['refresh_mode']} | {row['adversary']} | "
            f"{row['honest_acceptance']:.3f} | {row['adversary_acceptance']:.3f} | "
            f"{row['mean_honest_predicate_bit_error_rate']:.3f} | "
            f"{row['mean_unknown_independent_predicate_count']:.1f} | {row['refresh_independence_holds']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Supported: the randomized parity verifier can be executed as noisy Aer circuits with explicit circuit-level adversary input generation.",
            "- Compared: the noisy Aer bridge inherits the stricter transcript bridge result for the <=5% high-leakage soundness claim.",
            "- Rejected: calibration-side-channel and no-refresh rows violate the refresh-independence boundary or produce unsafe adversary acceptance.",
            "- Not claimed: real hardware execution, calibrated-backend validation, sampling hardness, cryptographic soundness, or BQP/classical separation.",
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
    parser.add_argument("--qubits", default="12")
    parser.add_argument("--invariant-count", type=int, default=10)
    parser.add_argument("--circuit-depth-factor", type=int, default=4)
    parser.add_argument("--refresh-modes", default="none,challenge_refresh,refresh_plus_rotation")
    parser.add_argument(
        "--device-profiles",
        default="ideal_transcript,low_noise_bridge,readout_biased_bridge,drift_correlated_bridge,calibration_side_channel",
    )
    parser.add_argument("--sample-count", type=int, default=32)
    parser.add_argument("--trials", type=int, default=4)
    parser.add_argument("--leakage-fraction", type=float, default=0.75)
    parser.add_argument("--tolerance", type=float, default=0.50)
    parser.add_argument("--seed", type=int, default=20260617)
    parser.add_argument(
        "--source-ideal-bridge",
        type=Path,
        default=Path("results/B10_t2_qiskit_aer_verifier_bridge_v0.json"),
    )
    parser.add_argument(
        "--source-device-noise-bridge",
        type=Path,
        default=Path("results/B10_t2_device_noise_transcript_bridge_v0.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t2_noisy_aer_verifier_bridge_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t2_noisy_aer_verifier_bridge.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    device_profiles = parse_str_list(args.device_profiles)
    unknown_profiles = sorted(set(device_profiles) - set(DEVICE_NOISE_PROFILES))
    if unknown_profiles:
        raise SystemExit(f"unknown device profiles: {unknown_profiles}")

    report = run(
        qubits=parse_int_list(args.qubits),
        invariant_count=args.invariant_count,
        circuit_depth_factor=args.circuit_depth_factor,
        refresh_modes=parse_str_list(args.refresh_modes),
        device_profiles=device_profiles,
        sample_count=args.sample_count,
        trials=args.trials,
        leakage_fraction=args.leakage_fraction,
        tolerance=args.tolerance,
        seed=args.seed,
        source_ideal_bridge_path=args.source_ideal_bridge,
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
                    "noisy_aer_circuit_count": report["noisy_aer_circuit_count"],
                    "minimum_safe_noisy_honest_acceptance": report["minimum_safe_noisy_honest_acceptance"],
                    "maximum_safe_noisy_adversary_acceptance": report["maximum_safe_noisy_adversary_acceptance"],
                    "unsafe_noisy_device_profiles": report["unsafe_noisy_device_profiles"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
