#!/usr/bin/env python3
"""Execute the preregistered R140 three-arm output-aware mapping holdout."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

from qiskit import qasm3, transpile
from qiskit_aer import AerSimulator

from b4_b8_r119_private_observable_bundle_gate import stable_hash, write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r128_transpiler_loop_layout_ranking import package_version
from b4_b8_r132_topology_constrained_route_policy import DETERMINISTIC_PROCESS_ENV
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import (
    exact_distribution,
    hellinger_fidelity,
    paired_bootstrap,
    probability_from_counts,
)


METHOD = "b4_b8_r140_output_aware_mapping_holdout_v0"
TARGET_ID = "T-B4-002ap/T-B8-003at/T-B10-009ah"
UPSTREAM_TARGET_ID = "T-B4-002ao/T-B8-003as/T-B10-009ag"
CONTRACT_PATH = "benchmarks/B4_B8_R140_output_aware_mapping_holdout_contract_v0.json"
CONTRACT_SHA256 = "d11f07b5d5a25c81a3f89a1b03297deb1a80486ce3613d1c17d3071e651a7cb5"
PREREGISTRATION_COMMIT = "9b39d062a613209366f74aea9d9e8804641401dd"
PREREGISTRATION_DISCUSSION = "https://github.com/crystal-tensor/Prometheus-plan/discussions/143"
PREREGISTRATION_CREATED_AT = "2026-07-12T17:31:14Z"
R136_RESULT_PATH = "results/B4_B8_R136_route_realization_margin_v0.json"
DESIGN_RESULT_PATH = "results/B4_B8_R140_output_aware_mapping_design_v0.json"
RESULT_PATH = "results/B4_B8_R140_output_aware_mapping_holdout_v0.json"
REPORT_PATH = "research/B4_B8_R140_output_aware_mapping_holdout.md"
OUT_DIR = "results/B4_B8_R140_output_aware_mapping_holdout"
COMMITMENT_PATH = f"{OUT_DIR}/challenge_commitment.json"
TRIALS_PATH = f"{OUT_DIR}/three_arm_trial_rows.json"
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


def condition(
    condition_id: str, label: str, value: Any, threshold: Any, passed: bool
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
        f"- {row['condition_id']} {'PASS' if row['passed'] else 'FAIL'}: "
        f"{row['label']}; value {row['value']}, threshold {row['threshold']}."
        for row in payload["acceptance_conditions"]
    )
    groups = "\n".join(
        f"- {row['artifact_id']}: new-auto {row['mean_new_minus_automatic']:+.8f}, "
        f"new-old {row['mean_new_minus_old']:+.8f}, wins vs auto "
        f"{row['new_win_count_vs_automatic']}/8, wins vs old "
        f"{row['new_win_count_vs_old']}/8."
        for row in payload["group_rows"]
    )
    requirements = "\n".join(
        f"- {row['requirement_id']} {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    verdict = "ACCEPT" if summary["global_acceptance"] else "REJECT"
    return f"""# B4/B8 R140 Output-Aware Mapping Holdout

## Verdict

- Preregistered verdict: {verdict}
- Contract SHA-256: {CONTRACT_SHA256}
- Three-arm trial rows: {summary['paired_trial_row_count']}
- Simulated executions / shots: {summary['simulated_circuit_execution_count']} / {summary['total_simulated_shots']}
- Lagos new / old / automatic mean fidelity: {summary['lagos_ising_mean_new_fidelity']:.8f} / {summary['lagos_ising_mean_old_fidelity']:.8f} / {summary['lagos_ising_mean_automatic_fidelity']:.8f}
- Lagos new-auto / new-old: {summary['lagos_ising_mean_new_minus_automatic']:+.8f} / {summary['lagos_ising_mean_new_minus_old']:+.8f}
- Lagos new wins vs automatic: {summary['lagos_ising_new_win_count_vs_automatic']} / 8
- Portfolio new-auto mean / bootstrap lower: {summary['portfolio_mean_new_minus_automatic']:+.8f} / {summary['portfolio_new_minus_automatic_bootstrap_95_lower']:+.8f}
- Portfolio new-old mean: {summary['portfolio_mean_new_minus_old']:+.8f}
- Groups above -0.01 vs old: {summary['groups_with_mean_new_minus_old_at_least_negative_0_01']} / 12
- Severe new-old regressions below -0.05: {summary['severe_new_minus_old_regression_count_below_negative_0_05']}
- Conditions passed / failed: {summary['acceptance_conditions_passed']} / {summary['acceptance_conditions_failed']}
- Phase replay: {summary['phase_artifact_replay_match_count']} / 4
- New credit delta: 0

The R140 design and thresholds were public before the hidden secret was
generated. Each fresh trial uses one transpiler seed and one shared simulator
seed for the frozen R140 circuit, frozen R136 circuit, and fresh automatic
compilation. The output-aware candidate is never recompiled during validation.

## Acceptance Conditions

{conditions}

## Group Evidence

{groups}

## Requirements

{requirements}

## Claim Boundary

Supported: one preregistered historical synthetic-noise holdout verdict for the
parameter-free output-aware mapper across twelve fixed groups. Not supported:
scalable exact-output estimation, current calibration, real hardware,
mitigation, independent verifier custody, protocol soundness, quantum
advantage, BQP separation, or new B10 credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    started_at = int(time.time())
    preregistered_at = utc_timestamp(PREREGISTRATION_CREATED_AT)
    if started_at <= preregistered_at:
        raise ValueError("R140 holdout must start after public preregistration")
    contract_path = root / CONTRACT_PATH
    if file_sha256(contract_path) != CONTRACT_SHA256:
        raise ValueError("R140 holdout contract hash mismatch")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    design_path = root / DESIGN_RESULT_PATH
    design = json.loads(design_path.read_text(encoding="utf-8"))
    source_bindings = contract["source_bindings"]
    if file_sha256(design_path) != source_bindings["r140_design_result_sha256"]:
        raise ValueError("R140 holdout design file hash mismatch")
    if design.get("payload_hash") != source_bindings["r140_design_payload_hash"]:
        raise ValueError("R140 holdout design payload mismatch")

    r136 = json.loads((root / R136_RESULT_PATH).read_text(encoding="utf-8"))
    old_groups = {
        (row["snapshot"], row["task_id"]): row for row in r136["validation_group_rows"]
    }
    design_groups = {
        (row["snapshot"], row["task_id"]): row for row in design["group_rows"]
    }
    tasks = {task["task_id"]: task for task in build_dense_validation_tasks()}
    artifact_bindings = {
        row["artifact_id"]: row["sha256"] for row in contract["artifact_bindings"]
    }
    source_binding_valid = len(artifact_bindings) == 12 and all(
        file_sha256(root / row["selected_circuit_path"])
        == artifact_bindings[f"{row['snapshot']}::{row['task_id']}"]
        for row in design["group_rows"]
    )

    challenge_design = contract["challenge_design"]
    shots = challenge_design["shots_per_circuit"]
    trials_per_group = challenge_design["trial_count_per_group"]
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
        secret = bytes.fromhex(
            json.loads(reveal_path.read_text(encoding="utf-8"))["challenge_secret_hex"]
        )
    else:
        secret = os.urandom(32)
    secret_commitment = hashlib.sha256(secret).hexdigest()
    if commitment_path.exists():
        challenge_commitment = json.loads(commitment_path.read_text(encoding="utf-8"))
        if challenge_commitment["challenge_secret_commitment_sha256"] != secret_commitment:
            raise ValueError("R140 preexisting challenge commitment mismatch")
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

    trial_rows: list[dict[str, Any]] = []
    for key in sorted(design_groups):
        snapshot_name, task_id = key
        artifact_id = f"{snapshot_name}::{task_id}"
        design_group = design_groups[key]
        old_group = old_groups[key]
        task = tasks[task_id]
        logical = basis_circuit(
            task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits))
        )
        ideal = exact_distribution(task["circuit"])
        backend = SNAPSHOT_CLASSES[snapshot_name]()
        simulator = AerSimulator.from_backend(backend)
        new_circuit = qasm3.loads(
            (root / design_group["selected_circuit_path"]).read_text(encoding="utf-8")
        )
        old_circuit = qasm3.loads(
            (root / old_group["selected_circuit_path"]).read_text(encoding="utf-8")
        )
        for trial in range(trials_per_group):
            transpiler_seed = derive_seed(secret, artifact_id, trial, "transpiler")
            simulator_seed = derive_seed(secret, artifact_id, trial, "simulator")
            automatic = transpile(
                logical,
                backend=backend,
                optimization_level=3,
                seed_transpiler=transpiler_seed,
            )
            fidelities = {}
            for arm, circuit in [
                ("new", new_circuit),
                ("old", old_circuit),
                ("automatic", automatic),
            ]:
                counts = simulator.run(
                    circuit, shots=shots, seed_simulator=simulator_seed
                ).result().get_counts()
                observed = probability_from_counts(
                    counts, shots, task["circuit"].num_qubits
                )
                fidelities[arm] = hellinger_fidelity(ideal, observed)
            trial_rows.append(
                {
                    "artifact_id": artifact_id,
                    "snapshot": snapshot_name,
                    "task_id": task_id,
                    "trial": trial,
                    "shots_per_arm": shots,
                    "transpiler_seed": transpiler_seed,
                    "simulator_seed": simulator_seed,
                    "same_simulator_seed_within_three_arm_trial": True,
                    "new_qasm_path": design_group["selected_circuit_path"],
                    "new_qasm_sha256": design_group["selected_circuit_sha256"],
                    "old_qasm_path": old_group["selected_circuit_path"],
                    "old_qasm_sha256": file_sha256(
                        root / old_group["selected_circuit_path"]
                    ),
                    "automatic_qasm_sha256": hashlib.sha256(
                        qasm3.dumps(automatic).encode()
                    ).hexdigest(),
                    "new_hellinger_fidelity": fidelities["new"],
                    "old_hellinger_fidelity": fidelities["old"],
                    "automatic_hellinger_fidelity": fidelities["automatic"],
                    "new_minus_automatic": fidelities["new"] - fidelities["automatic"],
                    "new_minus_old": fidelities["new"] - fidelities["old"],
                    "old_minus_automatic": fidelities["old"]
                    - fidelities["automatic"],
                }
            )
    write_json(
        root / TRIALS_PATH,
        {
            "contract_sha256": CONTRACT_SHA256,
            "challenge_secret_commitment_sha256": secret_commitment,
            "three_arm_trial_rows": trial_rows,
        },
    )
    reveal = {
        "contract_sha256": CONTRACT_SHA256,
        "challenge_secret_commitment_sha256": secret_commitment,
        "challenge_secret_hex": secret.hex(),
        "revealed_after_trial_row_count": len(trial_rows),
    }
    write_json(root / REVEAL_PATH, reveal)

    group_rows = []
    for artifact_id in sorted(artifact_bindings):
        rows = [row for row in trial_rows if row["artifact_id"] == artifact_id]
        new_auto = [row["new_minus_automatic"] for row in rows]
        new_old = [row["new_minus_old"] for row in rows]
        group_rows.append(
            {
                "artifact_id": artifact_id,
                "trial_count": len(rows),
                "mean_new_fidelity": statistics.fmean(
                    row["new_hellinger_fidelity"] for row in rows
                ),
                "mean_old_fidelity": statistics.fmean(
                    row["old_hellinger_fidelity"] for row in rows
                ),
                "mean_automatic_fidelity": statistics.fmean(
                    row["automatic_hellinger_fidelity"] for row in rows
                ),
                "mean_new_minus_automatic": statistics.fmean(new_auto),
                "mean_new_minus_old": statistics.fmean(new_old),
                "minimum_new_minus_old": min(new_old),
                "new_win_count_vs_automatic": sum(value > 1e-15 for value in new_auto),
                "new_loss_count_vs_automatic": sum(value < -1e-15 for value in new_auto),
                "new_win_count_vs_old": sum(value > 1e-15 for value in new_old),
                "new_loss_count_vs_old": sum(value < -1e-15 for value in new_old),
            }
        )
    lagos = next(
        row
        for row in group_rows
        if row["artifact_id"] == "FakeLagosV2::dense_validation_complete_ising_n6"
    )
    all_new_auto = [row["new_minus_automatic"] for row in trial_rows]
    all_new_old = [row["new_minus_old"] for row in trial_rows]
    bootstrap_new_auto = paired_bootstrap(
        all_new_auto,
        derive_seed(secret, "portfolio", 0, "bootstrap_new_auto"),
        challenge_design["bootstrap_resamples"],
    )
    bootstrap_new_old = paired_bootstrap(
        all_new_old,
        derive_seed(secret, "portfolio", 0, "bootstrap_new_old"),
        challenge_design["bootstrap_resamples"],
    )
    groups_nonregressed = sum(
        row["mean_new_minus_old"] >= -0.01 for row in group_rows
    )
    severe_regressions = sum(value < -0.05 for value in all_new_old)
    summary = {
        "source_binding_valid": source_binding_valid,
        "artifact_count": len(artifact_bindings),
        "artifact_hash_match_count": sum(
            file_sha256(root / row["selected_circuit_path"])
            == artifact_bindings[f"{row['snapshot']}::{row['task_id']}"]
            for row in design["group_rows"]
        ),
        "group_count": len(group_rows),
        "trial_count_per_group": trials_per_group,
        "paired_trial_row_count": len(trial_rows),
        "simulated_circuit_execution_count": 3 * len(trial_rows),
        "shots_per_circuit": shots,
        "total_simulated_shots": 3 * len(trial_rows) * shots,
        "lagos_ising_mean_new_fidelity": lagos["mean_new_fidelity"],
        "lagos_ising_mean_old_fidelity": lagos["mean_old_fidelity"],
        "lagos_ising_mean_automatic_fidelity": lagos["mean_automatic_fidelity"],
        "lagos_ising_mean_new_minus_automatic": lagos["mean_new_minus_automatic"],
        "lagos_ising_mean_new_minus_old": lagos["mean_new_minus_old"],
        "lagos_ising_new_win_count_vs_automatic": lagos[
            "new_win_count_vs_automatic"
        ],
        "lagos_ising_new_win_count_vs_old": lagos["new_win_count_vs_old"],
        "portfolio_mean_new_minus_automatic": statistics.fmean(all_new_auto),
        "portfolio_new_minus_automatic_bootstrap_95_lower": bootstrap_new_auto[
            "lower_95"
        ],
        "portfolio_new_minus_automatic_bootstrap_95_upper": bootstrap_new_auto[
            "upper_95"
        ],
        "portfolio_mean_new_minus_old": statistics.fmean(all_new_old),
        "portfolio_new_minus_old_bootstrap_95_lower": bootstrap_new_old["lower_95"],
        "portfolio_new_minus_old_bootstrap_95_upper": bootstrap_new_old["upper_95"],
        "groups_with_mean_new_minus_old_at_least_negative_0_01": groups_nonregressed,
        "severe_new_minus_old_regression_count_below_negative_0_05": severe_regressions,
        "design_candidate_compilation_count": contract["design_cost_ledger"][
            "candidate_compilation_count"
        ],
        "design_process_replay_count": contract["design_cost_ledger"][
            "design_process_replay_count"
        ],
        "challenge_generated_after_preregistration": challenge_commitment[
            "challenge_generated_at_unix"
        ]
        > preregistered_at,
        "contract_thresholds_revised": False,
        "scalable_output_estimation_claimed": False,
        "current_backend_calibration_used": False,
        "hardware_execution_performed": False,
        "mitigation_tested": False,
        "independent_verifier_custody_claimed": False,
        "protocol_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    labels = [row["label"] for row in contract["acceptance_conditions"]]
    acceptance_conditions = [
        condition("A1", labels[0], summary["artifact_hash_match_count"], "12 and bound", source_binding_valid and summary["artifact_hash_match_count"] == 12),
        condition("A2", labels[1], [len(trial_rows), len(group_rows)], [96, 12], len(trial_rows) == 96 and len(group_rows) == 12),
        condition("A3", labels[2], summary["lagos_ising_mean_new_minus_automatic"], ">= 0.0", summary["lagos_ising_mean_new_minus_automatic"] >= 0.0),
        condition("A4", labels[3], summary["lagos_ising_mean_new_minus_old"], ">= 0.01", summary["lagos_ising_mean_new_minus_old"] >= 0.01),
        condition("A5", labels[4], summary["lagos_ising_new_win_count_vs_automatic"], ">= 4", summary["lagos_ising_new_win_count_vs_automatic"] >= 4),
        condition("A6", labels[5], summary["portfolio_new_minus_automatic_bootstrap_95_lower"], ">= -0.005", summary["portfolio_new_minus_automatic_bootstrap_95_lower"] >= -0.005),
        condition("A7", labels[6], summary["portfolio_mean_new_minus_old"], ">= -0.002", summary["portfolio_mean_new_minus_old"] >= -0.002),
        condition("A8", labels[7], groups_nonregressed, ">= 11", groups_nonregressed >= 11),
        condition("A9", labels[8], [severe_regressions, summary["design_candidate_compilation_count"]], ["<= 2", 1536], severe_regressions <= 2 and summary["design_candidate_compilation_count"] == 1536),
        condition("A10", labels[9], 0, "forbidden claims false", not summary["hardware_execution_performed"] and not summary["scalable_output_estimation_claimed"] and not summary["protocol_soundness_claimed"] and not summary["quantum_advantage_claimed"] and not summary["bqp_separation_claimed"] and summary["new_credit_delta"] == 0),
    ]
    global_acceptance = all(row["passed"] for row in acceptance_conditions)
    summary["acceptance_conditions_passed"] = sum(
        row["passed"] for row in acceptance_conditions
    )
    summary["acceptance_conditions_failed"] = len(acceptance_conditions) - summary[
        "acceptance_conditions_passed"
    ]
    summary["failed_acceptance_condition_ids"] = [
        row["condition_id"] for row in acceptance_conditions if not row["passed"]
    ]
    summary["global_acceptance"] = global_acceptance
    transcript = {
        "contract_sha256": CONTRACT_SHA256,
        "challenge_secret_commitment_sha256": secret_commitment,
        "trial_rows_hash": stable_hash(trial_rows),
        "bootstrap_new_minus_automatic": bootstrap_new_auto,
        "bootstrap_new_minus_old": bootstrap_new_old,
        "acceptance_conditions": acceptance_conditions,
        "global_verdict": "ACCEPT" if global_acceptance else "REJECT",
    }
    write_json(root / TRANSCRIPT_PATH, transcript)
    replay_matches = sum(
        path.read_bytes() == preexisting.get(str(path), b"") for path in phase_paths
    )
    summary["phase_artifact_count"] = 4
    summary["phase_artifact_preexisting_count"] = len(preexisting)
    summary["phase_artifact_replay_match_count"] = replay_matches

    requirements = [
        ("P1", "public design and contract hashes precede challenge generation", file_sha256(contract_path) == CONTRACT_SHA256 and summary["challenge_generated_after_preregistration"]),
        ("P2", "all 12 new QASM bindings remain exact", source_binding_valid and summary["artifact_hash_match_count"] == 12),
        ("P3", "secret commitment precedes rows and reveal follows all rows", hashlib.sha256(bytes.fromhex(reveal["challenge_secret_hex"])).hexdigest() == secret_commitment and reveal["revealed_after_trial_row_count"] == 96),
        ("P4", "all 12 groups contain eight complete three-arm trials", summary["group_count"] == 12 and summary["paired_trial_row_count"] == 96),
        ("P5", "288 executions and 1,179,648 shots match the contract", summary["simulated_circuit_execution_count"] == 288 and summary["total_simulated_shots"] == 1179648),
        ("P6", "each three-arm trial shares one simulator seed", all(row["same_simulator_seed_within_three_arm_trial"] for row in trial_rows)),
        ("P7", "both portfolio bootstraps use 10,000 resamples", bootstrap_new_auto["resamples"] == 10000 and bootstrap_new_old["resamples"] == 10000),
        ("P8", "the verdict follows unchanged A1-A10 gates", len(acceptance_conditions) == 10 and not summary["contract_thresholds_revised"] and global_acceptance == all(row["passed"] for row in acceptance_conditions)),
        ("P9", "all four phase artifacts replay in a fresh process", len(preexisting) == 4 and replay_matches == 4),
        ("P10", "scalability, hardware, mitigation, custody, soundness, advantage, BQP, and credit remain excluded", not summary["scalable_output_estimation_claimed"] and not summary["hardware_execution_performed"] and not summary["mitigation_tested"] and not summary["independent_verifier_custody_claimed"] and not summary["protocol_soundness_claimed"] and not summary["quantum_advantage_claimed"] and not summary["bqp_separation_claimed"] and summary["new_credit_delta"] == 0),
    ]
    requirement_rows = [
        {"requirement_id": identifier, "label": label, "passed": passed}
        for identifier, label, passed in requirements
    ]
    failed = [row["requirement_id"] for row in requirement_rows if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R140 output-aware mapping holdout",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": (
            "output_aware_mapping_preregistered_holdout_acceptance"
            if global_acceptance
            else "output_aware_mapping_preregistered_holdout_rejection"
        ),
        "model_status": "historical_fake_backend_three_arm_output_aware_boundary",
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
        "three_arm_trial_rows": trial_rows,
        "artifacts": {
            "design_result": DESIGN_RESULT_PATH,
            "r136_result": R136_RESULT_PATH,
            "challenge_commitment": COMMITMENT_PATH,
            "three_arm_trial_rows": TRIALS_PATH,
            "challenge_reveal": REVEAL_PATH,
            "verifier_transcript": TRANSCRIPT_PATH,
        },
        "environment": {
            "deterministic_process_environment": DETERMINISTIC_PROCESS_ENV,
            "qiskit": package_version("qiskit"),
            "qiskit_aer": package_version("qiskit-aer"),
        },
        "claim_boundary": {
            "what_is_supported": "One preregistered historical synthetic-noise holdout verdict for the parameter-free output-aware mapper across twelve fixed groups.",
            "what_is_not_supported": "Scalable exact-output estimation, current calibration, real hardware, mitigation, independent verifier custody, protocol soundness, quantum advantage, BQP separation, or new B10 credit.",
            "next_gate": "Replace exact six-qubit output probabilities with a preregistered scalable sensitivity surrogate and repeat under independent custody or hardware.",
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
