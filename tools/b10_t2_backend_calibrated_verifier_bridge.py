#!/usr/bin/env python3
"""Run B10-T2 verifier circuits with backend-property-derived Aer noise."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

import numpy as np
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

from b4_b8_circuit_refresh_task import build_tasks, gf2_inverse, parse_int_list, parse_str_list
from b10_t2_device_noise_transcript_bridge import BRIDGE_SAFE_REFRESH_MODES, DEVICE_NOISE_PROFILES, device_transcript_for_mode
from b10_t2_noisy_aer_verifier_bridge import evaluate_samples, output_samples_to_verifier_circuits
from b10_t2_transcript_leakage_simulator import ADVERSARIES, adversary_transcript_samples, honest_samples


@dataclass(frozen=True)
class CalibrationSnapshot:
    name: str
    seed: int
    gate_error_scale: float
    readout_error_scale: float


CALIBRATION_SNAPSHOTS = [
    CalibrationSnapshot("generic_v2_nominal_seed_1201", 1201, 1.0, 1.0),
    CalibrationSnapshot("generic_v2_cx_stress_seed_1202", 1202, 1.75, 1.0),
    CalibrationSnapshot("generic_v2_readout_stress_seed_1203", 1203, 1.0, 1.75),
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def bounded_probability(value: float, cap: float) -> float:
    return max(0.0, min(float(value), cap))


def backend_for_snapshot(snapshot: CalibrationSnapshot, qubit_count: int) -> GenericBackendV2:
    return GenericBackendV2(
        num_qubits=qubit_count,
        basis_gates=["id", "rz", "sx", "x", "cx", "measure"],
        seed=snapshot.seed,
        noise_info=True,
    )


def extract_calibration_summary(snapshot: CalibrationSnapshot, qubit_count: int) -> dict:
    backend = backend_for_snapshot(snapshot, qubit_count)
    target = backend.target
    x_errors = [
        bounded_probability(props.error or 0.0, 0.05) * snapshot.gate_error_scale
        for props in target["x"].values()
    ]
    cx_errors = [
        bounded_probability(props.error or 0.0, 0.10) * snapshot.gate_error_scale
        for props in target["cx"].values()
    ]
    readout_errors = [
        bounded_probability(props.error or 0.0, 0.20) * snapshot.readout_error_scale
        for props in target["measure"].values()
    ]
    cx_durations = [float(props.duration or 0.0) for props in target["cx"].values()]
    measure_durations = [float(props.duration or 0.0) for props in target["measure"].values()]
    return {
        "snapshot": snapshot.name,
        "seed": snapshot.seed,
        "backend_name": backend.name,
        "qubit_count": qubit_count,
        "gate_error_scale": snapshot.gate_error_scale,
        "readout_error_scale": snapshot.readout_error_scale,
        "mean_x_error": float(mean(x_errors)),
        "max_x_error": float(max(x_errors)),
        "mean_cx_error": float(mean(cx_errors)),
        "max_cx_error": float(max(cx_errors)),
        "mean_readout_error": float(mean(readout_errors)),
        "max_readout_error": float(max(readout_errors)),
        "mean_cx_duration_s": float(mean(cx_durations)),
        "mean_measure_duration_s": float(mean(measure_durations)),
    }


def build_backend_noise_model(snapshot: CalibrationSnapshot, qubit_count: int) -> NoiseModel:
    backend = backend_for_snapshot(snapshot, qubit_count)
    target = backend.target
    model = NoiseModel()

    for qargs, props in target["x"].items():
        error_rate = bounded_probability((props.error or 0.0) * snapshot.gate_error_scale, 0.05)
        if error_rate:
            model.add_quantum_error(depolarizing_error(error_rate, 1), ["x"], list(qargs))

    for qargs, props in target["cx"].items():
        error_rate = bounded_probability((props.error or 0.0) * snapshot.gate_error_scale, 0.10)
        if error_rate:
            model.add_quantum_error(depolarizing_error(error_rate, 2), ["cx"], list(qargs))

    for qargs, props in target["measure"].items():
        error_rate = bounded_probability((props.error or 0.0) * snapshot.readout_error_scale, 0.20)
        if error_rate:
            model.add_readout_error(
                ReadoutError([[1.0 - error_rate, error_rate], [error_rate, 1.0 - error_rate]]),
                list(qargs),
            )

    return model


def run_backend_calibrated_batch(
    circuits,
    predicate_count: int,
    challenge_flips: list[np.ndarray],
    snapshot: CalibrationSnapshot,
    qubit_count: int,
    seed: int,
) -> np.ndarray:
    simulator = AerSimulator(
        method="stabilizer",
        noise_model=build_backend_noise_model(snapshot, qubit_count),
        seed_simulator=seed,
    )
    result = simulator.run(circuits, shots=1, memory=True).result()
    measured = []
    from b10_t2_qiskit_aer_verifier_bridge import decode_memory

    for idx in range(len(circuits)):
        memory = result.get_memory(idx)[0]
        measured.append(decode_memory(memory, predicate_count, challenge_flips[idx]))
    return np.array(measured, dtype=np.int8)


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "backend_calibrated_aer_verifier_bridge_not_hardware_execution":
        errors.append("status must identify backend-calibrated Aer bridge as not hardware execution")
    if report.get("source_target_id") != "B10-T2":
        errors.append("source target must be B10-T2")
    if report.get("backend_calibrated_noise_parameters_instantiated") is not True:
        errors.append("backend-calibrated noise parameters must be instantiated")
    if report.get("qiskit_generic_backend_v2_used") is not True:
        errors.append("GenericBackendV2 calibration snapshots must be recorded")
    if report.get("hardware_execution_performed") is not False:
        errors.append("bridge must not claim hardware execution")
    if report.get("sampling_hardness_proved") is not False:
        errors.append("bridge must not claim sampling hardness")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("bridge must explicitly avoid BQP separation claims")
    if int(report.get("backend_calibrated_aer_circuit_count", 0)) < 5000:
        errors.append("backend-calibrated bridge should execute at least 5000 circuits")
    if float(report.get("minimum_safe_calibrated_honest_acceptance", 0.0)) < 0.75:
        errors.append("safe calibrated honest acceptance should remain at least 0.75")
    if float(report.get("maximum_safe_calibrated_adversary_acceptance", 1.0)) > 0.35:
        errors.append("safe calibrated adversary acceptance should stay below 0.35")
    if float(report.get("maximum_safe_calibrated_honest_predicate_bit_error_rate", 1.0)) > 0.20:
        errors.append("safe calibrated predicate-bit error should stay below 20%")
    if float(report.get("source_noisy_aer_max_safe_adversary_acceptance", 1.0)) > 0.05:
        errors.append("source noisy Aer bridge should have safe adversary acceptance <=5%")
    if "none" not in report.get("unsafe_calibrated_refresh_modes", []):
        errors.append("no-refresh mode should remain unsafe under calibrated bridge")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def run(
    qubits: list[int],
    invariant_count: int,
    circuit_depth_factor: int,
    refresh_modes: list[str],
    sample_count: int,
    trials: int,
    leakage_fraction: float,
    tolerance: float,
    seed: int,
    source_noisy_bridge_path: Path,
    source_device_noise_bridge_path: Path,
    transcript_profile: str,
) -> dict:
    rng = np.random.default_rng(seed)
    tasks = build_tasks(qubits, invariant_count, circuit_depth_factor, seed + 19000)
    source_noisy_bridge = load_json(source_noisy_bridge_path)
    source_device_bridge = load_json(source_device_noise_bridge_path)
    adversaries = sorted(ADVERSARIES)
    max_qubits_with_ancilla = max(task["qubits"] + invariant_count for task in tasks)
    calibration_summaries = [
        extract_calibration_summary(snapshot, max_qubits_with_ancilla) for snapshot in CALIBRATION_SNAPSHOTS
    ]

    rows = []
    circuit_count = 0
    profile = DEVICE_NOISE_PROFILES[transcript_profile]

    for task in tasks:
        inverse_matrix = gf2_inverse(task["matrix"])
        for snapshot in CALIBRATION_SNAPSHOTS:
            for refresh_mode in refresh_modes:
                honest_accepts = []
                honest_bit_errors = []
                adversary_accepts = {name: [] for name in adversaries}
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
                    measured = run_backend_calibrated_batch(
                        circuits,
                        len(masks),
                        flips,
                        snapshot,
                        max_qubits_with_ancilla,
                        seed + circuit_count + trial_idx + 1,
                    )
                    circuit_count += len(circuits)
                    honest_result = evaluate_samples(measured, targets, tolerance)
                    honest_accepts.append(honest_result["accepted"])
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
                        measured = run_backend_calibrated_batch(
                            circuits,
                            len(masks),
                            flips,
                            snapshot,
                            max_qubits_with_ancilla,
                            seed + circuit_count + trial_idx + 1009,
                        )
                        circuit_count += len(circuits)
                        adversary_result = evaluate_samples(measured, targets, tolerance)
                        adversary_accepts[adversary].append(adversary_result["accepted"])
                        adversary_bit_errors[adversary].append(adversary_result["predicate_bit_error_rate"])

                for adversary in adversaries:
                    rows.append(
                        {
                            "task_id": task["task_id"],
                            "qubits": task["qubits"],
                            "calibration_snapshot": snapshot.name,
                            "backend_seed": snapshot.seed,
                            "refresh_mode": refresh_mode,
                            "leakage_fraction": leakage_fraction,
                            "transcript_reference_profile": transcript_profile,
                            "adversary": adversary,
                            "sample_count_per_trial": sample_count,
                            "trials": trials,
                            "mean_unknown_independent_predicate_count": float(np.mean(unknown_counts)),
                            "refresh_independence_holds": bool(all(independence_flags)),
                            "honest_acceptance": float(np.mean(honest_accepts)),
                            "mean_honest_predicate_bit_error_rate": float(np.mean(honest_bit_errors)),
                            "adversary_acceptance": float(np.mean(adversary_accepts[adversary])),
                            "mean_adversary_predicate_bit_error_rate": float(
                                np.mean(adversary_bit_errors[adversary])
                            ),
                        }
                    )

    safe_rows = [
        row
        for row in rows
        if row["refresh_mode"] in BRIDGE_SAFE_REFRESH_MODES and row["refresh_independence_holds"]
    ]
    unsafe_refresh_modes = sorted(
        {
            row["refresh_mode"]
            for row in rows
            if row["adversary_acceptance"] > 0.35 or not row["refresh_independence_holds"]
        }
    )
    safe_snapshots = sorted({row["calibration_snapshot"] for row in safe_rows})

    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T2 backend-calibrated Aer verifier bridge",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "backend_calibrated_aer_verifier_bridge_not_hardware_execution",
        "method": "b10_t2_backend_calibrated_verifier_bridge_v0",
        "source_target_id": "B10-T2",
        "source_noisy_aer_bridge": "b10_t2_noisy_aer_verifier_bridge_v0",
        "source_device_noise_bridge": "b10_t2_device_noise_transcript_bridge_v0",
        "dependency_benchmark": "B8",
        "backend_calibrated_noise_parameters_instantiated": True,
        "qiskit_generic_backend_v2_used": True,
        "real_backend_properties_used": False,
        "hardware_execution_performed": False,
        "sampling_hardness_proved": False,
        "explicit_not_bqp_separation": True,
        "task_count": len(tasks),
        "refresh_modes": refresh_modes,
        "backend_calibration_snapshots": [snapshot.name for snapshot in CALIBRATION_SNAPSHOTS],
        "calibration_summaries": calibration_summaries,
        "adversaries_tested": adversaries,
        "sample_count_per_trial": sample_count,
        "trials_per_configuration": trials,
        "leakage_fraction": leakage_fraction,
        "tolerance": tolerance,
        "transcript_reference_profile": transcript_profile,
        "source_noisy_aer_circuit_count": source_noisy_bridge.get("noisy_aer_circuit_count"),
        "source_noisy_aer_max_safe_adversary_acceptance": source_noisy_bridge.get(
            "maximum_safe_noisy_adversary_acceptance"
        ),
        "source_device_noise_max_safe_high_leakage_soundness": source_device_bridge.get(
            "max_soundness_bridge_safe_high_leakage"
        ),
        "backend_calibrated_aer_circuit_count": circuit_count,
        "max_circuit_qubits_with_ancilla": max_qubits_with_ancilla,
        "bridge_safe_refresh_modes": sorted(BRIDGE_SAFE_REFRESH_MODES),
        "bridge_safe_backend_snapshots": safe_snapshots,
        "minimum_safe_calibrated_honest_acceptance": min(row["honest_acceptance"] for row in safe_rows),
        "maximum_safe_calibrated_adversary_acceptance": max(row["adversary_acceptance"] for row in safe_rows),
        "maximum_safe_calibrated_honest_predicate_bit_error_rate": max(
            row["mean_honest_predicate_bit_error_rate"] for row in safe_rows
        ),
        "minimum_safe_calibrated_unknown_independent_count": min(
            row["mean_unknown_independent_predicate_count"] for row in safe_rows
        ),
        "unsafe_calibrated_refresh_modes": unsafe_refresh_modes,
        "results": rows,
        "limits": [
            "This uses Qiskit GenericBackendV2 calibration-style target properties, not IBM Runtime backend properties.",
            "The bridge derives per-qubit readout errors and per-gate depolarizing errors from backend target InstructionProperties.",
            "No physical backend job was submitted and no real-device calibration history was accessed.",
            "The transcript bridge remains the source of the stricter empirical soundness boundary.",
            "No BQP/classical separation, sampling-hardness proof, cryptographic soundness theorem, or hardware-verifier claim is made.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B10-T2 Backend-Calibrated Aer Verifier Bridge v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']}",
        f"- Source noisy Aer bridge: {report['source_noisy_aer_bridge']}",
        f"- Source device-noise bridge: {report['source_device_noise_bridge']}",
        f"- Method: {report['method']}",
        f"- Backend-calibrated noise parameters instantiated: {report['backend_calibrated_noise_parameters_instantiated']}",
        f"- Qiskit GenericBackendV2 used: {report['qiskit_generic_backend_v2_used']}",
        f"- Real backend properties used: {report['real_backend_properties_used']}",
        f"- Hardware execution performed: {report['hardware_execution_performed']}",
        f"- Backend-calibrated Aer circuits executed: {report['backend_calibrated_aer_circuit_count']}",
        f"- Max circuit qubits including verifier ancillas: {report['max_circuit_qubits_with_ancilla']}",
        f"- Bridge-safe calibrated honest acceptance: {report['minimum_safe_calibrated_honest_acceptance']:.3f}",
        f"- Bridge-safe calibrated adversary acceptance: {report['maximum_safe_calibrated_adversary_acceptance']:.3f}",
        f"- Bridge-safe calibrated honest predicate-bit error: {report['maximum_safe_calibrated_honest_predicate_bit_error_rate']:.3f}",
        f"- Bridge-safe min unknown independent predicates: {report['minimum_safe_calibrated_unknown_independent_count']:.1f}",
        f"- Source noisy Aer safe adversary acceptance: {report['source_noisy_aer_max_safe_adversary_acceptance']}",
        f"- Source transcript safe high-leakage soundness: {report['source_device_noise_max_safe_high_leakage_soundness']}",
        f"- Unsafe calibrated refresh modes: {report['unsafe_calibrated_refresh_modes']}",
        f"- Sampling hardness proved: {report['sampling_hardness_proved']}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Calibration Snapshots",
        "",
        "| snapshot | seed | mean x err | max x err | mean cx err | max cx err | mean readout err | max readout err |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in report["calibration_summaries"]:
        lines.append(
            f"| {summary['snapshot']} | {summary['seed']} | {summary['mean_x_error']:.6f} | "
            f"{summary['max_x_error']:.6f} | {summary['mean_cx_error']:.6f} | "
            f"{summary['max_cx_error']:.6f} | {summary['mean_readout_error']:.6f} | "
            f"{summary['max_readout_error']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Backend-Calibrated Circuit Rows",
            "",
            "| task | snapshot | mode | adversary | honest accept | adversary accept | honest bit error | adversary bit error | unknown predicates | independence |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["results"]:
        lines.append(
            f"| {row['task_id']} | {row['calibration_snapshot']} | {row['refresh_mode']} | "
            f"{row['adversary']} | {row['honest_acceptance']:.3f} | "
            f"{row['adversary_acceptance']:.3f} | {row['mean_honest_predicate_bit_error_rate']:.3f} | "
            f"{row['mean_adversary_predicate_bit_error_rate']:.3f} | "
            f"{row['mean_unknown_independent_predicate_count']:.1f} | {row['refresh_independence_holds']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Supported: the B10-T2 randomized parity verifier can be driven by backend-property-derived Aer noise models.",
            "- Upgraded from the previous noisy bridge: noise parameters now come from backend target InstructionProperties instead of only hand-labeled transcript profiles.",
            "- Still open: replace GenericBackendV2 snapshots with real backend properties or execute randomized-measurement verifier jobs on hardware.",
            "- Not claimed: real hardware execution, hardware calibration validation, sampling hardness, cryptographic soundness, or BQP/classical separation.",
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
    parser.add_argument("--sample-count", type=int, default=32)
    parser.add_argument("--trials", type=int, default=4)
    parser.add_argument("--leakage-fraction", type=float, default=0.75)
    parser.add_argument("--tolerance", type=float, default=0.50)
    parser.add_argument("--seed", type=int, default=20260618)
    parser.add_argument("--transcript-profile", default="drift_correlated_bridge")
    parser.add_argument(
        "--source-noisy-bridge",
        type=Path,
        default=Path("results/B10_t2_noisy_aer_verifier_bridge_v0.json"),
    )
    parser.add_argument(
        "--source-device-noise-bridge",
        type=Path,
        default=Path("results/B10_t2_device_noise_transcript_bridge_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B10_t2_backend_calibrated_verifier_bridge_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B10_t2_backend_calibrated_verifier_bridge.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    if args.transcript_profile not in DEVICE_NOISE_PROFILES:
        raise SystemExit(f"unknown transcript profile: {args.transcript_profile}")

    report = run(
        qubits=parse_int_list(args.qubits),
        invariant_count=args.invariant_count,
        circuit_depth_factor=args.circuit_depth_factor,
        refresh_modes=parse_str_list(args.refresh_modes),
        sample_count=args.sample_count,
        trials=args.trials,
        leakage_fraction=args.leakage_fraction,
        tolerance=args.tolerance,
        seed=args.seed,
        source_noisy_bridge_path=args.source_noisy_bridge,
        source_device_noise_bridge_path=args.source_device_noise_bridge,
        transcript_profile=args.transcript_profile,
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
                    "backend_calibrated_aer_circuit_count": report["backend_calibrated_aer_circuit_count"],
                    "minimum_safe_calibrated_honest_acceptance": report[
                        "minimum_safe_calibrated_honest_acceptance"
                    ],
                    "maximum_safe_calibrated_adversary_acceptance": report[
                        "maximum_safe_calibrated_adversary_acceptance"
                    ],
                    "unsafe_calibrated_refresh_modes": report["unsafe_calibrated_refresh_modes"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
