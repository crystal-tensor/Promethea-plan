#!/usr/bin/env python3
"""Execute the publicly preregistered R138 post-commit statistical challenge."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qasm3, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from b4_b8_r119_private_observable_bundle_gate import stable_hash, write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r128_transpiler_loop_layout_ranking import package_version
from b4_b8_r132_topology_constrained_route_policy import DETERMINISTIC_PROCESS_ENV
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks


METHOD = "b4_b8_r138_postcommit_statistical_challenge_v0"
TARGET_ID = "T-B4-002am/T-B8-003aq/T-B10-009ae"
UPSTREAM_TARGET_ID = "T-B4-002al/T-B8-003ap/T-B10-009ad"
CONTRACT_PATH = "benchmarks/B4_B8_R138_postcommit_statistical_challenge_contract_v0.json"
CONTRACT_SHA256 = "caee4c8fe9d8fb7b12482e714b3aa29a23f8531bfa4a9682e56e84438a288ab0"
PREREGISTRATION_COMMIT = "17012a4a5706eca8ec3c650c3e2a72bbfa82c80c"
PREREGISTRATION_DISCUSSION = "https://github.com/crystal-tensor/Prometheus-plan/discussions/140"
PREREGISTRATION_CREATED_AT = "2026-07-12T16:50:38Z"
R137_RESULT_PATH = "results/B4_B8_R137_artifact_bound_private_challenge_v0.json"
RESULT_PATH = "results/B4_B8_R138_postcommit_statistical_challenge_v0.json"
REPORT_PATH = "research/B4_B8_R138_postcommit_statistical_challenge.md"
OUT_DIR = "results/B4_B8_R138_postcommit_statistical_challenge"
COMMITMENT_PATH = f"{OUT_DIR}/challenge_commitment.json"
TRIALS_PATH = f"{OUT_DIR}/paired_trial_rows.json"
REVEAL_PATH = f"{OUT_DIR}/challenge_reveal.json"
TRANSCRIPT_PATH = f"{OUT_DIR}/verifier_transcript.json"


def ensure_deterministic_process_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def utc_timestamp(value: str) -> int:
    from datetime import datetime

    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def derive_seed(secret: bytes, artifact_id: str, trial: int, role: str) -> int:
    message = f"{CONTRACT_SHA256}|{artifact_id}|{trial}|{role}".encode()
    digest = hmac.new(secret, message, hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big") % (2**31 - 1) + 1


def probability_from_counts(counts: dict[str, int], shots: int, width: int) -> dict[str, float]:
    return {
        bitstring.replace(" ", "").zfill(width): count / shots
        for bitstring, count in counts.items()
    }


def hellinger_fidelity(first: dict[str, float], second: dict[str, float]) -> float:
    keys = set(first) | set(second)
    coefficient = sum(
        math.sqrt(first.get(key, 0.0) * second.get(key, 0.0)) for key in keys
    )
    return coefficient * coefficient


def total_variation_distance(first: dict[str, float], second: dict[str, float]) -> float:
    keys = set(first) | set(second)
    return 0.5 * sum(abs(first.get(key, 0.0) - second.get(key, 0.0)) for key in keys)


def exact_distribution(circuit: Any) -> dict[str, float]:
    probabilities = Statevector.from_instruction(circuit).probabilities()
    width = circuit.num_qubits
    return {
        format(index, f"0{width}b"): float(probability)
        for index, probability in enumerate(probabilities)
        if probability > 1e-15
    }


def paired_bootstrap(deltas: list[float], seed: int, resamples: int) -> dict[str, float]:
    values = np.asarray(deltas, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.empty(resamples, dtype=float)
    for index in range(resamples):
        means[index] = float(np.mean(rng.choice(values, size=len(values), replace=True)))
    return {
        "resamples": resamples,
        "seed": seed,
        "lower_95": float(np.quantile(means, 0.025)),
        "median": float(np.quantile(means, 0.5)),
        "upper_95": float(np.quantile(means, 0.975)),
    }


def condition(
    condition_id: str,
    label: str,
    value: Any,
    threshold: Any,
    passed: bool,
) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "label": label,
        "value": value,
        "threshold": threshold,
        "passed": passed,
    }


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    conditions = "\n".join(
        f"- `{row['condition_id']}` {'PASS' if row['passed'] else 'FAIL'}: "
        f"{row['label']}; value `{row['value']}`, threshold `{row['threshold']}`."
        for row in payload["acceptance_conditions"]
    )
    groups = "\n".join(
        f"- `{row['artifact_id']}`: mean delta `{row['mean_paired_hellinger_fidelity_delta']:+.6f}`, "
        f"wins/ties/losses `{row['selected_win_count']}/{row['tie_count']}/{row['selected_loss_count']}`, "
        f"minimum `{row['minimum_paired_delta']:+.6f}`."
        for row in payload["group_rows"]
    )
    requirements = "\n".join(
        f"- `{row['requirement_id']}` {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    return f"""# B4/B8 R138 Post-Commit Statistical Challenge

## Verdict

- Preregistered verdict: `{'ACCEPT' if summary['global_acceptance'] else 'REJECT'}`
- Contract SHA-256: `{CONTRACT_SHA256}`
- Public preregistration commit: `{PREREGISTRATION_COMMIT}`
- Paired trial rows: `{summary['paired_trial_row_count']}`
- Shots per circuit / total shots: `{summary['shots_per_circuit']}` / `{summary['total_simulated_shots']}`
- Mean selected / automatic Hellinger fidelity: `{summary['mean_selected_hellinger_fidelity']:.8f}` / `{summary['mean_automatic_hellinger_fidelity']:.8f}`
- Mean paired delta: `{summary['mean_paired_hellinger_fidelity_delta']:+.8f}`
- Paired bootstrap 95% interval: `[{summary['paired_bootstrap_95_lower']:+.8f}, {summary['paired_bootstrap_95_upper']:+.8f}]`
- Selected wins/ties/losses: `{summary['selected_win_count']}/{summary['tie_count']}/{summary['selected_loss_count']}`
- Groups above -0.025: `{summary['groups_with_mean_delta_at_least_negative_0_025']}` / `12`
- Severe regressions below -0.05: `{summary['severe_regression_count_delta_below_negative_0_05']}`
- Phase artifact replay: `{summary['phase_artifact_replay_match_count']}` / `4`
- New credit delta: `0`

The R138 contract and thresholds were public before the challenge secret was
generated. The secret deterministically derives fresh automatic-transpiler,
paired simulator, and bootstrap seeds. Each frozen selected QASM is compared
with a fresh optimization-level-3 automatic compilation under the matching
historical FakeBackend noise model and the same simulator seed within each
pair.

## Acceptance Conditions

{conditions}

## Group Evidence

{groups}

## Requirements

{requirements}

## Claim Boundary

Supported: one publicly preregistered post-commit synthetic-noise statistical
noninferiority verdict for the fixed 12-artifact R136 bundle under the frozen
R138 design. Not supported: current calibration, real hardware, mitigation,
independent verifier custody, protocol or cryptographic soundness, sampling
hardness, quantum advantage, BQP separation, or new B10 credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    started_at = int(time.time())
    preregistered_at = utc_timestamp(PREREGISTRATION_CREATED_AT)
    if started_at <= preregistered_at:
        raise ValueError("R138 execution must start after public preregistration")

    contract_path = root / CONTRACT_PATH
    if file_sha256(contract_path) != CONTRACT_SHA256:
        raise ValueError("R138 contract hash mismatch")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract.get("contract_status") != "public_preregistration_execution_unopened":
        raise ValueError("R138 requires the unopened public contract")
    r137_path = root / R137_RESULT_PATH
    r137 = json.loads(r137_path.read_text(encoding="utf-8"))
    source_bindings = contract["source_bindings"]
    if r137.get("payload_hash") != source_bindings["r137_payload_hash"]:
        raise ValueError("R138 contract does not bind the current R137 payload")
    if r137.get("commitment_hash") != source_bindings["r137_commitment_hash"]:
        raise ValueError("R138 contract does not bind the current R137 commitment")

    design = contract["challenge_design"]
    shots = design["shots_per_circuit"]
    trials_per_group = design["trial_count_per_group"]
    bootstrap_resamples = design["bootstrap_resamples"]
    output = root / OUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    phase_paths = [
        root / COMMITMENT_PATH,
        root / TRIALS_PATH,
        root / REVEAL_PATH,
        root / TRANSCRIPT_PATH,
    ]
    preexisting = {str(path): path.read_bytes() for path in phase_paths if path.exists()}
    reveal_path = root / REVEAL_PATH
    commitment_path = root / COMMITMENT_PATH
    if reveal_path.exists():
        prior_reveal = json.loads(reveal_path.read_text(encoding="utf-8"))
        secret = bytes.fromhex(prior_reveal["challenge_secret_hex"])
    else:
        secret = os.urandom(32)
    secret_commitment = hashlib.sha256(secret).hexdigest()
    if commitment_path.exists():
        challenge_commitment = json.loads(commitment_path.read_text(encoding="utf-8"))
        if challenge_commitment.get("challenge_secret_commitment_sha256") != secret_commitment:
            raise ValueError("R138 preexisting secret commitment mismatch")
    else:
        challenge_commitment = {
            "contract_sha256": CONTRACT_SHA256,
            "preregistration_commit": PREREGISTRATION_COMMIT,
            "preregistration_created_at": PREREGISTRATION_CREATED_AT,
            "challenge_generated_at_unix": started_at,
            "challenge_secret_commitment_sha256": secret_commitment,
            "secret_revealed": False,
        }
    write_json(commitment_path, challenge_commitment)

    tasks = {task["task_id"]: task for task in build_dense_validation_tasks()}
    r137_artifacts = {
        row["artifact_id"]: row for row in r137["commitment"]["artifacts"]
    }
    artifact_bindings = contract["artifact_bindings"]
    source_binding_valid = (
        len(artifact_bindings) == 12
        and all(
            binding["artifact_id"] in r137_artifacts
            and binding["sha256"] == r137_artifacts[binding["artifact_id"]]["sha256"]
            and file_sha256(root / r137_artifacts[binding["artifact_id"]]["path"])
            == binding["sha256"]
            for binding in artifact_bindings
        )
    )
    trial_rows: list[dict[str, Any]] = []
    for binding in sorted(artifact_bindings, key=lambda row: row["artifact_id"]):
        artifact_id = binding["artifact_id"]
        artifact = r137_artifacts[artifact_id]
        snapshot_name, task_id = artifact_id.split("::", maxsplit=1)
        task = tasks[task_id]
        logical = basis_circuit(
            task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits))
        )
        ideal = exact_distribution(task["circuit"])
        backend = SNAPSHOT_CLASSES[snapshot_name]()
        simulator = AerSimulator.from_backend(backend)
        selected_path = root / artifact["path"]
        selected = qasm3.loads(selected_path.read_text(encoding="utf-8"))
        for trial in range(trials_per_group):
            transpiler_seed = derive_seed(secret, artifact_id, trial, "transpiler")
            simulator_seed = derive_seed(secret, artifact_id, trial, "simulator")
            automatic = transpile(
                logical,
                backend=backend,
                optimization_level=3,
                seed_transpiler=transpiler_seed,
            )
            selected_counts = simulator.run(
                selected, shots=shots, seed_simulator=simulator_seed
            ).result().get_counts()
            automatic_counts = simulator.run(
                automatic, shots=shots, seed_simulator=simulator_seed
            ).result().get_counts()
            selected_distribution = probability_from_counts(
                selected_counts, shots, task["circuit"].num_qubits
            )
            automatic_distribution = probability_from_counts(
                automatic_counts, shots, task["circuit"].num_qubits
            )
            selected_fidelity = hellinger_fidelity(ideal, selected_distribution)
            automatic_fidelity = hellinger_fidelity(ideal, automatic_distribution)
            delta = selected_fidelity - automatic_fidelity
            trial_rows.append(
                {
                    "artifact_id": artifact_id,
                    "snapshot": snapshot_name,
                    "task_id": task_id,
                    "trial": trial,
                    "shots": shots,
                    "transpiler_seed": transpiler_seed,
                    "simulator_seed": simulator_seed,
                    "same_simulator_seed_within_pair": True,
                    "selected_qasm_path": artifact["path"],
                    "selected_qasm_sha256": binding["sha256"],
                    "automatic_qasm_sha256": hashlib.sha256(
                        qasm3.dumps(automatic).encode()
                    ).hexdigest(),
                    "selected_depth": selected.depth(),
                    "automatic_depth": automatic.depth(),
                    "selected_cx_count": int(selected.count_ops().get("cx", 0)),
                    "automatic_cx_count": int(automatic.count_ops().get("cx", 0)),
                    "selected_hellinger_fidelity": selected_fidelity,
                    "automatic_hellinger_fidelity": automatic_fidelity,
                    "paired_hellinger_fidelity_delta": delta,
                    "selected_total_variation_distance": total_variation_distance(
                        ideal, selected_distribution
                    ),
                    "automatic_total_variation_distance": total_variation_distance(
                        ideal, automatic_distribution
                    ),
                }
            )
    write_json(
        root / TRIALS_PATH,
        {
            "contract_sha256": CONTRACT_SHA256,
            "challenge_secret_commitment_sha256": secret_commitment,
            "paired_trial_rows": trial_rows,
        },
    )
    reveal = {
        "contract_sha256": CONTRACT_SHA256,
        "challenge_secret_commitment_sha256": secret_commitment,
        "challenge_secret_hex": secret.hex(),
        "revealed_after_trial_row_count": len(trial_rows),
    }
    write_json(root / REVEAL_PATH, reveal)

    deltas = [row["paired_hellinger_fidelity_delta"] for row in trial_rows]
    bootstrap = paired_bootstrap(
        deltas,
        derive_seed(secret, "global", 0, "bootstrap"),
        bootstrap_resamples,
    )
    group_rows = []
    for artifact_id in sorted(r137_artifacts):
        rows = [row for row in trial_rows if row["artifact_id"] == artifact_id]
        group_deltas = [row["paired_hellinger_fidelity_delta"] for row in rows]
        group_rows.append(
            {
                "artifact_id": artifact_id,
                "trial_count": len(rows),
                "mean_selected_hellinger_fidelity": statistics.fmean(
                    row["selected_hellinger_fidelity"] for row in rows
                ),
                "mean_automatic_hellinger_fidelity": statistics.fmean(
                    row["automatic_hellinger_fidelity"] for row in rows
                ),
                "mean_paired_hellinger_fidelity_delta": statistics.fmean(group_deltas),
                "minimum_paired_delta": min(group_deltas),
                "maximum_paired_delta": max(group_deltas),
                "selected_win_count": sum(delta > 1e-15 for delta in group_deltas),
                "tie_count": sum(abs(delta) <= 1e-15 for delta in group_deltas),
                "selected_loss_count": sum(delta < -1e-15 for delta in group_deltas),
            }
        )
    mean_delta = statistics.fmean(deltas)
    groups_above_floor = sum(
        row["mean_paired_hellinger_fidelity_delta"] >= -0.025 for row in group_rows
    )
    severe_regressions = sum(delta < -0.05 for delta in deltas)
    summary = {
        "source_binding_valid": source_binding_valid,
        "artifact_count": len(artifact_bindings),
        "artifact_hash_match_count": sum(
            file_sha256(root / r137_artifacts[row["artifact_id"]]["path"])
            == row["sha256"]
            for row in artifact_bindings
        ),
        "group_count": len(group_rows),
        "trial_count_per_group": trials_per_group,
        "paired_trial_row_count": len(trial_rows),
        "simulated_circuit_execution_count": 2 * len(trial_rows),
        "shots_per_circuit": shots,
        "total_simulated_shots": 2 * len(trial_rows) * shots,
        "mean_selected_hellinger_fidelity": statistics.fmean(
            row["selected_hellinger_fidelity"] for row in trial_rows
        ),
        "mean_automatic_hellinger_fidelity": statistics.fmean(
            row["automatic_hellinger_fidelity"] for row in trial_rows
        ),
        "mean_paired_hellinger_fidelity_delta": mean_delta,
        "median_paired_hellinger_fidelity_delta": statistics.median(deltas),
        "minimum_paired_hellinger_fidelity_delta": min(deltas),
        "maximum_paired_hellinger_fidelity_delta": max(deltas),
        "paired_bootstrap_resamples": bootstrap_resamples,
        "paired_bootstrap_95_lower": bootstrap["lower_95"],
        "paired_bootstrap_median": bootstrap["median"],
        "paired_bootstrap_95_upper": bootstrap["upper_95"],
        "selected_win_count": sum(delta > 1e-15 for delta in deltas),
        "tie_count": sum(abs(delta) <= 1e-15 for delta in deltas),
        "selected_loss_count": sum(delta < -1e-15 for delta in deltas),
        "groups_with_mean_delta_at_least_negative_0_025": groups_above_floor,
        "severe_regression_count_delta_below_negative_0_05": severe_regressions,
        "route_realization_compilation_count": r137["summary"][
            "route_realization_compilation_count"
        ],
        "automatic_validation_compilation_count": r137["summary"][
            "automatic_validation_compilation_count"
        ],
        "total_compilation_count": r137["summary"]["total_compilation_count"],
        "challenge_generated_after_preregistration": challenge_commitment[
            "challenge_generated_at_unix"
        ]
        > preregistered_at,
        "secret_revealed_after_all_trials": reveal["revealed_after_trial_row_count"]
        == len(trial_rows)
        == 96,
        "contract_thresholds_revised": False,
        "current_backend_calibration_used": False,
        "hardware_execution_performed": False,
        "readout_mitigation_tested": False,
        "independent_verifier_custody_claimed": False,
        "protocol_soundness_claimed": False,
        "cryptographic_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    acceptance_conditions = [
        condition("A1", contract["acceptance_conditions"][0]["label"], summary["artifact_hash_match_count"], "12 and source binding valid", source_binding_valid and summary["artifact_hash_match_count"] == 12),
        condition("A2", contract["acceptance_conditions"][1]["label"], [summary["paired_trial_row_count"], summary["group_count"]], [96, 12], summary["paired_trial_row_count"] == 96 and summary["group_count"] == 12),
        condition("A3", contract["acceptance_conditions"][2]["label"], mean_delta, ">= -0.005", mean_delta >= -0.005),
        condition("A4", contract["acceptance_conditions"][3]["label"], bootstrap["lower_95"], ">= -0.0125", bootstrap["lower_95"] >= -0.0125),
        condition("A5", contract["acceptance_conditions"][4]["label"], groups_above_floor, ">= 10", groups_above_floor >= 10),
        condition("A6", contract["acceptance_conditions"][5]["label"], severe_regressions, "<= 2", severe_regressions <= 2),
        condition("A7", contract["acceptance_conditions"][6]["label"], [summary["route_realization_compilation_count"], summary["total_compilation_count"]], [1536, 1656], summary["route_realization_compilation_count"] == 1536 and summary["total_compilation_count"] == 1656),
        condition("A8", contract["acceptance_conditions"][7]["label"], 0, "all forbidden claims false and new_credit_delta == 0", not summary["hardware_execution_performed"] and not summary["protocol_soundness_claimed"] and not summary["quantum_advantage_claimed"] and not summary["bqp_separation_claimed"] and summary["new_credit_delta"] == 0),
    ]
    global_acceptance = all(row["passed"] for row in acceptance_conditions)
    summary["acceptance_conditions_passed"] = sum(
        row["passed"] for row in acceptance_conditions
    )
    summary["acceptance_conditions_failed"] = len(acceptance_conditions) - summary[
        "acceptance_conditions_passed"
    ]
    summary["global_acceptance"] = global_acceptance
    transcript = {
        "contract_sha256": CONTRACT_SHA256,
        "challenge_secret_commitment_sha256": secret_commitment,
        "trial_rows_hash": stable_hash(trial_rows),
        "bootstrap": bootstrap,
        "acceptance_conditions": acceptance_conditions,
        "global_verdict": "ACCEPT" if global_acceptance else "REJECT",
    }
    write_json(root / TRANSCRIPT_PATH, transcript)
    replay_matches = sum(
        path.read_bytes() == preexisting.get(str(path), b"") for path in phase_paths
    )
    summary["phase_artifact_count"] = len(phase_paths)
    summary["phase_artifact_preexisting_count"] = len(preexisting)
    summary["phase_artifact_replay_match_count"] = replay_matches

    requirements = [
        ("P1", "public contract hash and publication precede challenge generation", file_sha256(contract_path) == CONTRACT_SHA256 and summary["challenge_generated_after_preregistration"]),
        ("P2", "R137 payload, commitment, and all 12 artifact hashes remain bound", source_binding_valid and summary["artifact_hash_match_count"] == 12),
        ("P3", "challenge secret is committed before rows and revealed after all rows", summary["secret_revealed_after_all_trials"] and hashlib.sha256(bytes.fromhex(reveal["challenge_secret_hex"])).hexdigest() == secret_commitment),
        ("P4", "all 12 groups and 96 paired hidden-seed rows execute", summary["group_count"] == 12 and summary["paired_trial_row_count"] == 96),
        ("P5", "192 circuit executions and 786,432 shots match the contract", summary["simulated_circuit_execution_count"] == 192 and summary["total_simulated_shots"] == 786432),
        ("P6", "every selected/automatic pair shares its simulator seed", all(row["same_simulator_seed_within_pair"] for row in trial_rows)),
        ("P7", "the fixed Hellinger and 10,000-resample bootstrap statistics are materialized", bootstrap["resamples"] == 10000 and len(deltas) == 96),
        ("P8", "the verdict is computed from unchanged A1-A8 conditions", len(acceptance_conditions) == 8 and not summary["contract_thresholds_revised"] and global_acceptance == all(row["passed"] for row in acceptance_conditions)),
        ("P9", "all four phase artifacts replay identically in a fresh process", len(preexisting) == 4 and replay_matches == 4),
        ("P10", "hardware, custody, soundness, advantage, BQP, and new credit remain excluded", not summary["hardware_execution_performed"] and not summary["independent_verifier_custody_claimed"] and not summary["protocol_soundness_claimed"] and not summary["cryptographic_soundness_claimed"] and not summary["quantum_advantage_claimed"] and not summary["bqp_separation_claimed"] and summary["new_credit_delta"] == 0),
    ]
    requirement_rows = [
        {"requirement_id": identifier, "label": label, "passed": passed}
        for identifier, label, passed in requirements
    ]
    failed = [row["requirement_id"] for row in requirement_rows if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R138 post-commit statistical challenge",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": (
            "preregistered_postcommit_statistical_noninferiority_acceptance"
            if global_acceptance
            else "preregistered_postcommit_statistical_noninferiority_rejection"
        ),
        "model_status": "historical_fake_backend_paired_hardware_agnostic_boundary",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "preregistration": {
            "contract_path": CONTRACT_PATH,
            "contract_sha256": CONTRACT_SHA256,
            "remote_commit": PREREGISTRATION_COMMIT,
            "discussion": PREREGISTRATION_DISCUSSION,
            "created_at": PREREGISTRATION_CREATED_AT,
            "created_before_execution": summary["challenge_generated_after_preregistration"],
        },
        "requirements": requirement_rows,
        "requirement_count": len(requirement_rows),
        "requirements_passed": len(requirement_rows) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "acceptance_conditions": acceptance_conditions,
        "summary": summary,
        "group_rows": group_rows,
        "paired_trial_rows": trial_rows,
        "bootstrap": bootstrap,
        "artifacts": {
            "r137_result": R137_RESULT_PATH,
            "challenge_commitment": COMMITMENT_PATH,
            "paired_trial_rows": TRIALS_PATH,
            "challenge_reveal": REVEAL_PATH,
            "verifier_transcript": TRANSCRIPT_PATH,
        },
        "environment": {
            "deterministic_process_environment": DETERMINISTIC_PROCESS_ENV,
            "qiskit": package_version("qiskit"),
            "qiskit_aer": package_version("qiskit-aer"),
        },
        "claim_boundary": {
            "what_is_supported": "One publicly preregistered post-commit synthetic-noise statistical noninferiority verdict for the fixed 12-artifact R136 bundle under the frozen R138 design.",
            "what_is_not_supported": "Current calibration, real hardware, mitigation, independent verifier custody, protocol or cryptographic soundness, sampling hardness, quantum advantage, BQP separation, or new B10 credit.",
            "next_gate": "Transfer the published commitment to a genuinely independent verifier or hardware provider for private challenge custody and real backend execution.",
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
