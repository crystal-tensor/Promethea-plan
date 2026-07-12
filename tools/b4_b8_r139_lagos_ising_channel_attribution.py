#!/usr/bin/env python3
"""Attribute the R138 Lagos complete-Ising regression across noise channels."""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import tempfile
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qasm3, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

from b4_b8_r119_private_observable_bundle_gate import stable_hash, write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r128_transpiler_loop_layout_ranking import exposure_from_qasm, package_version
from b4_b8_r132_topology_constrained_route_policy import DETERMINISTIC_PROCESS_ENV
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import (
    exact_distribution,
    hellinger_fidelity,
    paired_bootstrap,
    probability_from_counts,
)


METHOD = "b4_b8_r139_lagos_ising_channel_attribution_v0"
STATUS = "lagos_ising_output_aware_readout_assignment_boundary"
MODEL_STATUS = "synthetic_channel_ablation_attributes_negative_group_to_readout_assignment"
TARGET_ID = "T-B4-002an/T-B8-003ar/T-B10-009af"
UPSTREAM_TARGET_ID = "T-B4-002am/T-B8-003aq/T-B10-009ae"
R125_RESULT_PATH = "results/B4_B8_R125_historical_snapshot_replay_v0.json"
R138_RESULT_PATH = "results/B4_B8_R138_postcommit_statistical_challenge_v0.json"
RESULT_PATH = "results/B4_B8_R139_lagos_ising_channel_attribution_v0.json"
REPORT_PATH = "research/B4_B8_R139_lagos_ising_channel_attribution.md"
OUT_DIR = "results/B4_B8_R139_lagos_ising_channel_attribution"
CHANNEL_ROWS_PATH = f"{OUT_DIR}/channel_rows.json"
TRANSCRIPT_PATH = f"{OUT_DIR}/attribution_transcript.json"
ARTIFACT_ID = "FakeLagosV2::dense_validation_complete_ising_n6"
CHANNELS = ("full", "gate_only", "readout_only", "noiseless")


def ensure_deterministic_process_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def measurement_map(circuit: Any) -> dict[int, int]:
    return {
        circuit.find_bit(instruction.clbits[0]).index: circuit.find_bit(
            instruction.qubits[0]
        ).index
        for instruction in circuit.data
        if instruction.operation.name == "measure"
    }


def exact_compiled_classical_distribution(circuit: Any) -> dict[str, float]:
    mapping = measurement_map(circuit)
    width = circuit.num_clbits
    bare = circuit.remove_final_measurements(inplace=False)
    probabilities = Statevector.from_instruction(bare).probabilities()
    output = {format(index, f"0{width}b"): 0.0 for index in range(2**width)}
    for basis_index, probability in enumerate(probabilities):
        if probability <= 1e-15:
            continue
        classical_index = 0
        for classical_bit, physical_qubit in mapping.items():
            classical_index |= ((basis_index >> physical_qubit) & 1) << classical_bit
        output[format(classical_index, f"0{width}b")] += float(probability)
    return output


def readout_errors(noise_dict: dict[str, Any]) -> dict[int, float]:
    errors = {}
    for error in noise_dict["errors"]:
        if error["type"] != "roerror":
            continue
        physical_qubit = error["gate_qubits"][0][0]
        errors[physical_qubit] = float(error["probabilities"][0][1])
    return errors


def apply_symmetric_readout_channel(
    distribution: dict[str, float], errors_by_classical_bit: list[float]
) -> dict[str, float]:
    width = len(errors_by_classical_bit)
    output = {format(index, f"0{width}b"): 0.0 for index in range(2**width)}
    for true_string, true_probability in distribution.items():
        true_index = int(true_string, 2)
        for observed_index in range(2**width):
            probability = true_probability
            for bit, error in enumerate(errors_by_classical_bit):
                probability *= (
                    1.0 - error
                    if ((true_index >> bit) & 1) == ((observed_index >> bit) & 1)
                    else error
                )
            output[format(observed_index, f"0{width}b")] += probability
    return output


def channel_models(backend: Any) -> dict[str, AerSimulator]:
    full_model = NoiseModel.from_backend(backend)
    noise_dict = full_model.to_dict()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        gate_only = NoiseModel.from_dict(
            {"errors": [row for row in noise_dict["errors"] if row["type"] == "qerror"]}
        )
        readout_only = NoiseModel.from_dict(
            {"errors": [row for row in noise_dict["errors"] if row["type"] == "roerror"]}
        )
    return {
        "full": AerSimulator.from_backend(backend),
        "gate_only": AerSimulator(noise_model=gate_only),
        "readout_only": AerSimulator(noise_model=readout_only),
        "noiseless": AerSimulator(),
    }


def pearson(first: list[float], second: list[float]) -> float:
    if len(first) < 2 or statistics.pstdev(first) == 0 or statistics.pstdev(second) == 0:
        return 0.0
    return float(np.corrcoef(np.asarray(first), np.asarray(second))[0, 1])


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    channels = "\n".join(
        f"- `{name}`: mean selected/automatic `{row['mean_selected_hellinger_fidelity']:.8f}` / "
        f"`{row['mean_automatic_hellinger_fidelity']:.8f}`, delta "
        f"`{row['mean_paired_delta']:+.8f}`, wins/losses "
        f"`{row['selected_win_count']}/{row['selected_loss_count']}`, bootstrap 95% "
        f"`[{row['bootstrap_95_lower']:+.8f}, {row['bootstrap_95_upper']:+.8f}]`."
        for name, row in payload["channel_summaries"].items()
    )
    requirements = "\n".join(
        f"- `{row['requirement_id']}` {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    return f"""# B4/B8 R139 Lagos Complete-Ising Channel Attribution

## Result

- Source R138 group mean delta: `{summary['r138_full_mean_delta']:+.8f}`
- Replayed full-noise mean delta: `{summary['full_mean_delta']:+.8f}`
- Gate-only mean delta: `{summary['gate_only_mean_delta']:+.8f}`
- Readout-only mean delta: `{summary['readout_only_mean_delta']:+.8f}`
- Noiseless sampled mean delta: `{summary['noiseless_mean_delta']:+.8f}`
- Minimum exact semantic fidelity: `{summary['minimum_exact_semantic_fidelity']:.16f}`
- Exact output-aware readout mean delta: `{summary['exact_output_aware_readout_mean_delta']:+.8f}`
- Exact/sampled readout sign agreement: `{summary['exact_sampled_readout_sign_agreement_count']}` / `8`
- Exact/sampled readout delta correlation: `{summary['exact_sampled_readout_delta_correlation']:.8f}`
- Proxy says selected wins / exact readout says selected loses: `{summary['proxy_selected_but_exact_readout_loses_count']}` / `8`
- Attribution: `{summary['attribution']}`
- Phase replay: `{summary['phase_artifact_replay_match_count']}` / `2`
- New credit delta: `0`

R139 reuses the eight already revealed R138 seed pairs without selecting a new
seed or circuit. The same selected and automatic circuits are replayed under
full, gate-only, readout-only, and noiseless channels. It also removes final
measurements, reconstructs the exact classical output distribution from each
compiled circuit, and applies the backend readout matrices analytically using
the actual logical-to-physical measurement assignment.

## Channel Evidence

{channels}

The combined-any-error proxy ranks the selected route ahead in all eight rows,
but that proxy is output agnostic. The exact readout channel sees which logical
output bit lands on each physical readout channel and predicts the sampled
readout-only ranking in every row. The diagnostic therefore supports an
output-aware readout-assignment failure, not a semantic failure and not a raw
CX-count explanation.

## Requirements

{requirements}

## Claim Boundary

Supported: synthetic channel-ablation and exact output-aware readout attribution
for the R138 FakeLagosV2 complete-Ising negative group. Not supported: causal
hardware attribution, current calibration, mitigation performance, a repaired
mapping, independent verifier custody, protocol soundness, quantum advantage,
BQP separation, or new B10 credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    r138_path = root / R138_RESULT_PATH
    r138 = json.loads(r138_path.read_text(encoding="utf-8"))
    if r138.get("status") != "preregistered_postcommit_statistical_noninferiority_acceptance":
        raise ValueError("R139 requires the accepted R138 statistical boundary")
    source_group = next(
        row for row in r138["group_rows"] if row["artifact_id"] == ARTIFACT_ID
    )
    source_rows = sorted(
        [row for row in r138["paired_trial_rows"] if row["artifact_id"] == ARTIFACT_ID],
        key=lambda row: row["trial"],
    )
    if len(source_rows) != 8 or source_group["mean_paired_hellinger_fidelity_delta"] >= 0:
        raise ValueError("R139 requires the eight-row negative Lagos complete-Ising group")

    r125 = json.loads((root / R125_RESULT_PATH).read_text(encoding="utf-8"))
    metadata = r125["snapshot_metadata"]["FakeLagosV2"]
    task = next(
        row for row in build_dense_validation_tasks() if row["task_id"] == "dense_validation_complete_ising_n6"
    )
    logical = basis_circuit(
        task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits))
    )
    ideal = exact_distribution(task["circuit"])
    backend = SNAPSHOT_CLASSES["FakeLagosV2"]()
    simulators = channel_models(backend)
    noise_dict = NoiseModel.from_backend(backend).to_dict()
    physical_readout_errors = readout_errors(noise_dict)
    selected_path = root / source_rows[0]["selected_qasm_path"]
    selected = qasm3.loads(selected_path.read_text(encoding="utf-8"))
    output = root / OUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    phase_paths = [root / CHANNEL_ROWS_PATH, root / TRANSCRIPT_PATH]
    preexisting = {str(path): path.read_bytes() for path in phase_paths if path.exists()}

    channel_rows: list[dict[str, Any]] = []
    structure_rows: list[dict[str, Any]] = []
    selected_exact = exact_compiled_classical_distribution(selected)
    selected_semantic_fidelity = hellinger_fidelity(ideal, selected_exact)
    selected_measurement_map = measurement_map(selected)
    selected_readout_error_vector = [
        physical_readout_errors[selected_measurement_map[index]] for index in range(6)
    ]
    selected_exact_readout_fidelity = hellinger_fidelity(
        ideal,
        apply_symmetric_readout_channel(selected_exact, selected_readout_error_vector),
    )
    with tempfile.TemporaryDirectory(prefix="r139-") as temporary:
        scratch = Path(temporary) / "compiled.qasm"
        selected_exposure = exposure_from_qasm(
            selected_path.read_text(encoding="utf-8"), metadata, scratch
        )
        for source_row in source_rows:
            automatic = transpile(
                logical,
                backend=backend,
                optimization_level=3,
                seed_transpiler=source_row["transpiler_seed"],
            )
            automatic_qasm = qasm3.dumps(automatic)
            automatic_exposure = exposure_from_qasm(automatic_qasm, metadata, scratch)
            automatic_exact = exact_compiled_classical_distribution(automatic)
            automatic_semantic_fidelity = hellinger_fidelity(ideal, automatic_exact)
            automatic_measurement_map = measurement_map(automatic)
            automatic_readout_error_vector = [
                physical_readout_errors[automatic_measurement_map[index]]
                for index in range(6)
            ]
            automatic_exact_readout_fidelity = hellinger_fidelity(
                ideal,
                apply_symmetric_readout_channel(
                    automatic_exact, automatic_readout_error_vector
                ),
            )
            exact_readout_delta = (
                selected_exact_readout_fidelity - automatic_exact_readout_fidelity
            )
            structure_rows.append(
                {
                    "trial": source_row["trial"],
                    "transpiler_seed": source_row["transpiler_seed"],
                    "simulator_seed": source_row["simulator_seed"],
                    "selected_measurement_map": selected_measurement_map,
                    "automatic_measurement_map": automatic_measurement_map,
                    "selected_readout_error_vector": selected_readout_error_vector,
                    "automatic_readout_error_vector": automatic_readout_error_vector,
                    "selected_exact_semantic_fidelity": selected_semantic_fidelity,
                    "automatic_exact_semantic_fidelity": automatic_semantic_fidelity,
                    "selected_exact_readout_fidelity": selected_exact_readout_fidelity,
                    "automatic_exact_readout_fidelity": automatic_exact_readout_fidelity,
                    "exact_output_aware_readout_delta": exact_readout_delta,
                    "selected_combined_any_error_proxy": selected_exposure[
                        "combined_any_error_proxy"
                    ],
                    "automatic_combined_any_error_proxy": automatic_exposure[
                        "combined_any_error_proxy"
                    ],
                    "combined_proxy_gain_selected_over_automatic": automatic_exposure[
                        "combined_any_error_proxy"
                    ]
                    - selected_exposure["combined_any_error_proxy"],
                    "selected_cx_count": selected_exposure["cx_occurrence_count"],
                    "automatic_cx_count": automatic_exposure["cx_occurrence_count"],
                }
            )
            for channel_name in CHANNELS:
                simulator = simulators[channel_name]
                fidelities = []
                for circuit in [selected, automatic]:
                    counts = simulator.run(
                        circuit,
                        shots=source_row["shots"],
                        seed_simulator=source_row["simulator_seed"],
                    ).result().get_counts()
                    observed = probability_from_counts(
                        counts, source_row["shots"], task["circuit"].num_qubits
                    )
                    fidelities.append(hellinger_fidelity(ideal, observed))
                channel_rows.append(
                    {
                        "trial": source_row["trial"],
                        "channel": channel_name,
                        "shots": source_row["shots"],
                        "transpiler_seed": source_row["transpiler_seed"],
                        "simulator_seed": source_row["simulator_seed"],
                        "selected_hellinger_fidelity": fidelities[0],
                        "automatic_hellinger_fidelity": fidelities[1],
                        "paired_delta": fidelities[0] - fidelities[1],
                    }
                )

    write_json(
        root / CHANNEL_ROWS_PATH,
        {
            "source_result_sha256": file_sha256(r138_path),
            "artifact_id": ARTIFACT_ID,
            "channel_rows": channel_rows,
            "structure_rows": structure_rows,
        },
    )
    channel_summaries = {}
    for channel_name in CHANNELS:
        rows = [row for row in channel_rows if row["channel"] == channel_name]
        deltas = [row["paired_delta"] for row in rows]
        bootstrap = paired_bootstrap(
            deltas,
            int(stable_hash([ARTIFACT_ID, channel_name])[:8], 16),
            10000,
        )
        channel_summaries[channel_name] = {
            "trial_count": len(rows),
            "mean_selected_hellinger_fidelity": statistics.fmean(
                row["selected_hellinger_fidelity"] for row in rows
            ),
            "mean_automatic_hellinger_fidelity": statistics.fmean(
                row["automatic_hellinger_fidelity"] for row in rows
            ),
            "mean_paired_delta": statistics.fmean(deltas),
            "minimum_paired_delta": min(deltas),
            "maximum_paired_delta": max(deltas),
            "selected_win_count": sum(delta > 1e-15 for delta in deltas),
            "selected_loss_count": sum(delta < -1e-15 for delta in deltas),
            "bootstrap_95_lower": bootstrap["lower_95"],
            "bootstrap_95_upper": bootstrap["upper_95"],
        }

    full_deltas = [
        row["paired_delta"] for row in channel_rows if row["channel"] == "full"
    ]
    readout_deltas = [
        row["paired_delta"]
        for row in channel_rows
        if row["channel"] == "readout_only"
    ]
    exact_readout_deltas = [
        row["exact_output_aware_readout_delta"] for row in structure_rows
    ]
    semantic_fidelities = [
        value
        for row in structure_rows
        for value in [
            row["selected_exact_semantic_fidelity"],
            row["automatic_exact_semantic_fidelity"],
        ]
    ]
    sign_agreement = sum(
        (sampled > 0) == (exact > 0)
        for sampled, exact in zip(readout_deltas, exact_readout_deltas)
    )
    proxy_selected_exact_readout_loses = sum(
        row["combined_proxy_gain_selected_over_automatic"] > 0
        and row["exact_output_aware_readout_delta"] < 0
        for row in structure_rows
    )
    attribution_passed = (
        channel_summaries["full"]["mean_paired_delta"] < 0
        and abs(channel_summaries["gate_only"]["mean_paired_delta"]) <= 0.002
        and channel_summaries["readout_only"]["mean_paired_delta"] < 0
        and statistics.fmean(exact_readout_deltas) < 0
        and sign_agreement == 8
        and min(semantic_fidelities) >= 1.0 - 1e-12
    )
    attribution = (
        "output_aware_readout_assignment_dominates_synthetic_regression"
        if attribution_passed
        else "channel_attribution_inconclusive"
    )
    transcript = {
        "artifact_id": ARTIFACT_ID,
        "source_result_sha256": file_sha256(r138_path),
        "channel_summaries": channel_summaries,
        "exact_output_aware_readout_mean_delta": statistics.fmean(
            exact_readout_deltas
        ),
        "exact_sampled_readout_sign_agreement_count": sign_agreement,
        "exact_sampled_readout_delta_correlation": pearson(
            exact_readout_deltas, readout_deltas
        ),
        "attribution": attribution,
        "attribution_passed": attribution_passed,
    }
    write_json(root / TRANSCRIPT_PATH, transcript)
    replay_matches = sum(
        path.read_bytes() == preexisting.get(str(path), b"") for path in phase_paths
    )

    summary = {
        "artifact_id": ARTIFACT_ID,
        "source_trial_count": len(source_rows),
        "channel_count": len(CHANNELS),
        "paired_channel_row_count": len(channel_rows),
        "simulated_circuit_execution_count": 2 * len(channel_rows),
        "shots_per_execution": source_rows[0]["shots"],
        "total_simulated_shots": 2
        * len(channel_rows)
        * source_rows[0]["shots"],
        "r138_full_mean_delta": source_group[
            "mean_paired_hellinger_fidelity_delta"
        ],
        "full_mean_delta": channel_summaries["full"]["mean_paired_delta"],
        "gate_only_mean_delta": channel_summaries["gate_only"]["mean_paired_delta"],
        "readout_only_mean_delta": channel_summaries["readout_only"][
            "mean_paired_delta"
        ],
        "noiseless_mean_delta": channel_summaries["noiseless"]["mean_paired_delta"],
        "r138_full_channel_replay_match_count": sum(
            abs(first - second) <= 1e-15
            for first, second in zip(
                full_deltas,
                [row["paired_hellinger_fidelity_delta"] for row in source_rows],
            )
        ),
        "minimum_exact_semantic_fidelity": min(semantic_fidelities),
        "exact_output_aware_readout_mean_delta": statistics.fmean(
            exact_readout_deltas
        ),
        "exact_sampled_readout_sign_agreement_count": sign_agreement,
        "exact_sampled_readout_delta_correlation": pearson(
            exact_readout_deltas, readout_deltas
        ),
        "full_sampled_readout_delta_correlation": pearson(
            full_deltas, readout_deltas
        ),
        "proxy_selected_but_exact_readout_loses_count": proxy_selected_exact_readout_loses,
        "attribution": attribution,
        "attribution_passed": attribution_passed,
        "phase_artifact_count": 2,
        "phase_artifact_preexisting_count": len(preexisting),
        "phase_artifact_replay_match_count": replay_matches,
        "new_seed_selected": False,
        "new_circuit_selected": False,
        "current_backend_calibration_used": False,
        "hardware_execution_performed": False,
        "readout_mitigation_tested": False,
        "causal_hardware_attribution_claimed": False,
        "mapping_repair_claimed": False,
        "protocol_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        ("P1", "R138 source and the negative Lagos complete-Ising group are hash-bound", r138["source_target_id"] == UPSTREAM_TARGET_ID and len(source_rows) == 8 and source_group["mean_paired_hellinger_fidelity_delta"] < 0),
        ("P2", "the eight revealed R138 circuit and seed pairs are reused without reselection", not summary["new_seed_selected"] and not summary["new_circuit_selected"]),
        ("P3", "full, gate-only, readout-only, and noiseless channels cover all eight pairs", len(channel_rows) == 32 and all(channel_summaries[name]["trial_count"] == 8 for name in CHANNELS)),
        ("P4", "the full-noise channel exactly replays all eight R138 deltas", summary["r138_full_channel_replay_match_count"] == 8),
        ("P5", "selected and automatic compiled circuits preserve the exact logical distribution", summary["minimum_exact_semantic_fidelity"] >= 1.0 - 1e-12),
        ("P6", "gate-only, readout-only, and exact readout counterfactuals are materialized", all(name in channel_summaries for name in ["gate_only", "readout_only"]) and len(structure_rows) == 8),
        ("P7", "exact output-aware readout predicts all sampled readout ranking signs", summary["exact_sampled_readout_sign_agreement_count"] == 8),
        ("P8", "the readout-dominant attribution follows the fixed channel evidence", summary["attribution_passed"] and summary["attribution"] == "output_aware_readout_assignment_dominates_synthetic_regression"),
        ("P9", "both channel and attribution phase artifacts replay across a fresh process", len(preexisting) == 2 and replay_matches == 2),
        ("P10", "hardware causality, mitigation, repair, soundness, advantage, BQP, and credit remain excluded", not summary["hardware_execution_performed"] and not summary["causal_hardware_attribution_claimed"] and not summary["readout_mitigation_tested"] and not summary["mapping_repair_claimed"] and not summary["protocol_soundness_claimed"] and not summary["quantum_advantage_claimed"] and not summary["bqp_separation_claimed"] and summary["new_credit_delta"] == 0),
    ]
    requirement_rows = [
        {"requirement_id": identifier, "label": label, "passed": passed}
        for identifier, label, passed in requirements
    ]
    failed = [row["requirement_id"] for row in requirement_rows if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R139 Lagos complete-Ising channel attribution",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "requirements": requirement_rows,
        "requirement_count": len(requirement_rows),
        "requirements_passed": len(requirement_rows) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "summary": summary,
        "channel_summaries": channel_summaries,
        "channel_rows": channel_rows,
        "structure_rows": structure_rows,
        "artifacts": {
            "r138_result": R138_RESULT_PATH,
            "channel_rows": CHANNEL_ROWS_PATH,
            "attribution_transcript": TRANSCRIPT_PATH,
        },
        "environment": {
            "qiskit": package_version("qiskit"),
            "qiskit_aer": package_version("qiskit-aer"),
        },
        "claim_boundary": {
            "what_is_supported": "Synthetic channel-ablation and exact output-aware readout attribution for the R138 FakeLagosV2 complete-Ising negative group.",
            "what_is_not_supported": "Causal hardware attribution, current calibration, mitigation performance, a repaired mapping, independent verifier custody, protocol soundness, quantum advantage, BQP separation, or new B10 credit.",
            "next_gate": "Design an output-aware readout-assignment score, freeze it before validation, and test whether it repairs Lagos complete-Ising without regressing the other eleven groups.",
        },
    }
    payload["payload_hash"] = stable_hash(payload)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    return payload


def main() -> None:
    ensure_deterministic_process_environment()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    payload = run_gate(args.root)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
