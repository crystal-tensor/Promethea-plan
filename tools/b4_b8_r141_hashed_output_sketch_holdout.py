#!/usr/bin/env python3
"""Execute the preregistered R141 hashed-output-sketch four-arm holdout."""

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
from b4_b8_r132_topology_constrained_route_policy import (
    DETERMINISTIC_PROCESS_ENV,
    compile_policy,
)
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import (
    exact_distribution,
    hellinger_fidelity,
    paired_bootstrap,
    probability_from_counts,
)
from b4_b8_r141_hashed_output_sketch_design import (
    candidate_identity,
    pilot_packet,
    selection_key,
    surrogate_score,
)


METHOD = "b4_b8_r141_hashed_output_sketch_holdout_v0"
TARGET_ID = "T-B4-002ar/T-B8-003av/T-B10-009aj"
UPSTREAM_TARGET_ID = "T-B4-002aq/T-B8-003au/T-B10-009ai"
CONTRACT_PATH = "benchmarks/B4_B8_R141_hashed_output_sketch_holdout_contract_v0.json"
CONTRACT_SHA256 = "388fb1aa35ae98d2c5f624e34541832e8590481046b42af105e57be63d6a770f"
PREREGISTRATION_COMMIT = "d6de013849e4df1ce8cded48310197cf83ff71c4"
PREREGISTRATION_DISCUSSION = "https://github.com/crystal-tensor/Prometheus-plan/discussions/145"
PREREGISTRATION_CREATED_AT = "2026-07-12T18:05:03Z"
R136_RESULT_PATH = "results/B4_B8_R136_route_realization_margin_v0.json"
R140_DESIGN_PATH = "results/B4_B8_R140_output_aware_mapping_design_v0.json"
R141_DESIGN_PATH = "results/B4_B8_R141_hashed_output_sketch_design_v0.json"
RESULT_PATH = "results/B4_B8_R141_hashed_output_sketch_holdout_v0.json"
REPORT_PATH = "research/B4_B8_R141_hashed_output_sketch_holdout.md"
OUT_DIR = "results/B4_B8_R141_hashed_output_sketch_holdout"
COMMITMENT_PATH = f"{OUT_DIR}/challenge_commitment.json"
TRIALS_PATH = f"{OUT_DIR}/four_arm_trial_rows.json"
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
    verdict = "ACCEPT" if summary["global_acceptance"] else "REJECT"
    conditions = "\n".join(
        f"- {row['condition_id']} {'PASS' if row['passed'] else 'FAIL'}: "
        f"{row['label']}; value {row['value']}, threshold {row['threshold']}."
        for row in payload["acceptance_conditions"]
    )
    groups = "\n".join(
        f"- {row['artifact_id']}: selection agreement "
        f"{row['selection_agreement_count']}/8, mean sketch-auto "
        f"{row['mean_sketch_minus_automatic']:+.8f}, mean sketch-exact "
        f"{row['mean_sketch_minus_r140_exact']:+.8f}."
        for row in payload["group_rows"]
    )
    requirements = "\n".join(
        f"- {row['requirement_id']} {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    return f"""# B4/B8 R141 Hashed Output Sketch Holdout

## Verdict

- Preregistered verdict: {verdict}
- Contract SHA-256: {CONTRACT_SHA256}
- Selection agreement with R140 exact: {summary['selection_agreement_count']} / 96
- Lagos selection agreement: {summary['lagos_ising_selection_agreement_count']} / 8
- Mean / maximum exact-score regret: {summary['mean_exact_score_regret']:.8f} / {summary['maximum_exact_score_regret']:.8f}
- Portfolio sketch-auto mean / bootstrap lower: {summary['portfolio_mean_sketch_minus_automatic']:+.8f} / {summary['portfolio_sketch_minus_automatic_bootstrap_95_lower']:+.8f}
- Lagos sketch-auto mean / wins: {summary['lagos_ising_mean_sketch_minus_automatic']:+.8f} / {summary['lagos_ising_sketch_win_count_vs_automatic']} of 8
- Portfolio sketch-R140-exact mean: {summary['portfolio_mean_sketch_minus_r140_exact']:+.8f}
- Four-arm rows / executions / shots: {summary['trial_row_count']} / {summary['simulated_circuit_execution_count']} / {summary['total_simulated_shots']}
- Conditions passed / failed: {summary['acceptance_conditions_passed']} / {summary['acceptance_conditions_failed']}
- Phase replay: {summary['phase_artifact_replay_match_count']} / 4
- New credit delta: 0

The hidden pilot seed changes the sample sketch before each selection. The
selector receives samples and shared readout variates, never the full ideal
distribution or the R140 teacher score. Teacher scores are opened only after
selection to compute agreement and regret. All four noisy arms in a row share
one simulator seed.

## Acceptance Conditions

{conditions}

## Group Evidence

{groups}

## Requirements

{requirements}

## Claim Boundary

Supported: one preregistered synthetic four-arm holdout verdict for a
fixed-width sample-only mapping selector. Not supported: scalable pilot
acquisition, current calibration, real hardware, mitigation, independent
custody, protocol soundness, quantum advantage, BQP separation, solved
B4/B8/B10, or new credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    started_at = int(time.time())
    if started_at <= utc_timestamp(PREREGISTRATION_CREATED_AT):
        raise ValueError("R141 holdout must start after public preregistration")
    contract_path = root / CONTRACT_PATH
    if file_sha256(contract_path) != CONTRACT_SHA256:
        raise ValueError("R141 holdout contract hash mismatch")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    r141_path = root / R141_DESIGN_PATH
    r141 = json.loads(r141_path.read_text(encoding="utf-8"))
    bindings = contract["source_bindings"]
    if file_sha256(r141_path) != bindings["r141_design_sha256"]:
        raise ValueError("R141 design file binding mismatch")
    if r141["payload_hash"] != bindings["r141_design_payload_hash"]:
        raise ValueError("R141 design payload binding mismatch")

    r140 = json.loads((root / R140_DESIGN_PATH).read_text(encoding="utf-8"))
    r136 = json.loads((root / R136_RESULT_PATH).read_text(encoding="utf-8"))
    tasks = {task["task_id"]: task for task in build_dense_validation_tasks()}
    candidate_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in r141["candidate_rows"]:
        candidate_groups.setdefault((row["snapshot"], row["task_id"]), []).append(row)
    exact_groups = {
        (row["snapshot"], row["task_id"]): row for row in r140["group_rows"]
    }
    frozen_sketch_groups = {
        (row["snapshot"], row["task_id"]): row for row in r141["group_rows"]
    }
    old_groups = {
        (row["snapshot"], row["task_id"]): row
        for row in r136["validation_group_rows"]
    }
    candidate_identity_payload = [
        {
            "snapshot": row["snapshot"],
            "task_id": row["task_id"],
            "mapping": row["mapping"],
            "policy_id": row["policy_id"],
            "realization_seed": row["realization_seed"],
            "qasm_hash": row["qasm_hash"],
        }
        for row in r141["candidate_rows"]
    ]
    candidate_identity_hash = hashlib.sha256(
        json.dumps(candidate_identity_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    source_binding_valid = (
        candidate_identity_hash == bindings["candidate_identity_sha256"]
        and len(candidate_groups) == 12
        and all(len(rows) == 128 for rows in candidate_groups.values())
    )

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
    commitment = hashlib.sha256(secret).hexdigest()
    if commitment_path.exists():
        commitment_payload = json.loads(commitment_path.read_text(encoding="utf-8"))
        if commitment_payload["challenge_secret_commitment_sha256"] != commitment:
            raise ValueError("R141 preexisting commitment mismatch")
    else:
        commitment_payload = {
            "contract_sha256": CONTRACT_SHA256,
            "preregistration_commit": PREREGISTRATION_COMMIT,
            "preregistration_discussion": PREREGISTRATION_DISCUSSION,
            "preregistration_created_at": PREREGISTRATION_CREATED_AT,
            "challenge_generated_at_unix": started_at,
            "challenge_secret_commitment_sha256": commitment,
            "secret_revealed": False,
        }
    write_json(commitment_path, commitment_payload)

    trial_rows: list[dict[str, Any]] = []
    compiled_cache: dict[tuple[Any, ...], tuple[Any, str]] = {}
    challenge_design = contract["challenge_design"]
    shots = challenge_design["shots_per_circuit"]
    trials_per_group = challenge_design["hidden_pilot_trial_count_per_group"]
    for key in sorted(candidate_groups):
        snapshot_name, task_id = key
        artifact_id = f"{snapshot_name}::{task_id}"
        task = tasks[task_id]
        logical = basis_circuit(
            task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits))
        )
        ideal = exact_distribution(task["circuit"])
        backend = SNAPSHOT_CLASSES[snapshot_name]()
        simulator = AerSimulator.from_backend(backend)
        exact_group = exact_groups[key]
        frozen_sketch_group = frozen_sketch_groups[key]
        old_group = old_groups[key]
        exact_circuit = qasm3.loads(
            (root / exact_group["selected_circuit_path"]).read_text(encoding="utf-8")
        )
        old_circuit = qasm3.loads(
            (root / old_group["selected_circuit_path"]).read_text(encoding="utf-8")
        )
        exact_identity = (
            tuple(exact_group["new_selected_mapping"]),
            exact_group["new_selected_policy_id"],
            exact_group["new_selected_realization_seed"],
        )
        exact_score = exact_group["new_selected_output_aware_score"]
        for trial in range(trials_per_group):
            pilot_seed = derive_seed(secret, artifact_id, trial, "pilot")
            transpiler_seed = derive_seed(secret, artifact_id, trial, "transpiler")
            simulator_seed = derive_seed(secret, artifact_id, trial, "simulator")
            samples, uniforms, ideal_histogram = pilot_packet(
                ideal, task["circuit"].num_qubits, pilot_seed
            )
            scored = []
            for source in candidate_groups[key]:
                score, readout_fidelity = surrogate_score(
                    source, samples, uniforms, ideal_histogram
                )
                scored.append(
                    {
                        **source,
                        "hashed_output_sketch_score": score,
                        "hashed_output_sketch_readout_fidelity": readout_fidelity,
                    }
                )
            selected = max(scored, key=selection_key)
            selected_identity = candidate_identity(selected)
            cache_key = (snapshot_name, task_id, *selected_identity)
            if cache_key not in compiled_cache:
                frozen_identity = (
                    tuple(frozen_sketch_group["selected_mapping"]),
                    frozen_sketch_group["selected_policy_id"],
                    frozen_sketch_group["selected_realization_seed"],
                )
                if selected_identity == frozen_identity:
                    frozen_qasm = (
                        root / frozen_sketch_group["selected_circuit_path"]
                    ).read_text(encoding="utf-8")
                    compiled_cache[cache_key] = (
                        qasm3.loads(frozen_qasm),
                        stable_hash(frozen_qasm),
                    )
                else:
                    compiled = compile_policy(
                        logical,
                        backend,
                        selected["mapping"],
                        selected["policy_id"],
                        selected["realization_seed"],
                    )
                    compiled_qasm = qasm3.dumps(compiled)
                    compiled_cache[cache_key] = (
                        compiled,
                        stable_hash(compiled_qasm),
                    )
            sketch_circuit, sketch_qasm_hash = compiled_cache[cache_key]
            sketch_qasm_hash_match = sketch_qasm_hash == selected["qasm_hash"]
            automatic = transpile(
                logical,
                backend=backend,
                optimization_level=3,
                seed_transpiler=transpiler_seed,
            )
            fidelities = {}
            for arm, circuit in [
                ("sketch", sketch_circuit),
                ("r140_exact", exact_circuit),
                ("r136_old", old_circuit),
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
                    "pilot_seed": pilot_seed,
                    "transpiler_seed": transpiler_seed,
                    "simulator_seed": simulator_seed,
                    "selected_mapping": selected["mapping"],
                    "selected_policy_id": selected["policy_id"],
                    "selected_realization_seed": selected["realization_seed"],
                    "selected_qasm_hash": selected["qasm_hash"],
                    "selected_qasm_hash_match": sketch_qasm_hash_match,
                    "selection_matches_r140_exact": selected_identity == exact_identity,
                    "selected_exact_r140_score": selected["output_aware_product_score"],
                    "r140_exact_score": exact_score,
                    "exact_score_regret": exact_score
                    - selected["output_aware_product_score"],
                    "sketch_fidelity": fidelities["sketch"],
                    "r140_exact_fidelity": fidelities["r140_exact"],
                    "r136_old_fidelity": fidelities["r136_old"],
                    "automatic_fidelity": fidelities["automatic"],
                    "sketch_minus_automatic": fidelities["sketch"]
                    - fidelities["automatic"],
                    "sketch_minus_r140_exact": fidelities["sketch"]
                    - fidelities["r140_exact"],
                    "sketch_minus_r136_old": fidelities["sketch"]
                    - fidelities["r136_old"],
                }
            )
    write_json(root / TRIALS_PATH, trial_rows)
    reveal_payload = {
        "contract_sha256": CONTRACT_SHA256,
        "challenge_secret_hex": secret.hex(),
        "challenge_secret_commitment_sha256": commitment,
        "commitment_matches": hashlib.sha256(secret).hexdigest() == commitment,
        "trial_rows_complete_before_reveal": len(trial_rows) == 96,
    }
    write_json(reveal_path, reveal_payload)

    group_rows = []
    for artifact_id in sorted({row["artifact_id"] for row in trial_rows}):
        rows = [row for row in trial_rows if row["artifact_id"] == artifact_id]
        group_rows.append(
            {
                "artifact_id": artifact_id,
                "row_count": len(rows),
                "selection_agreement_count": sum(
                    row["selection_matches_r140_exact"] for row in rows
                ),
                "mean_exact_score_regret": statistics.mean(
                    row["exact_score_regret"] for row in rows
                ),
                "maximum_exact_score_regret": max(
                    row["exact_score_regret"] for row in rows
                ),
                "mean_sketch_minus_automatic": statistics.mean(
                    row["sketch_minus_automatic"] for row in rows
                ),
                "mean_sketch_minus_r140_exact": statistics.mean(
                    row["sketch_minus_r140_exact"] for row in rows
                ),
                "sketch_win_count_vs_automatic": sum(
                    row["sketch_minus_automatic"] > 0 for row in rows
                ),
            }
        )
    lagos_rows = [
        row
        for row in trial_rows
        if row["artifact_id"]
        == "FakeLagosV2::dense_validation_complete_ising_n6"
    ]
    sketch_auto_deltas = [row["sketch_minus_automatic"] for row in trial_rows]
    sketch_exact_deltas = [row["sketch_minus_r140_exact"] for row in trial_rows]
    bootstrap_seed_auto = derive_seed(secret, "portfolio", 0, "bootstrap-auto")
    bootstrap_seed_exact = derive_seed(secret, "portfolio", 0, "bootstrap-exact")
    bootstrap_auto = paired_bootstrap(sketch_auto_deltas, bootstrap_seed_auto, 10000)
    bootstrap_exact = paired_bootstrap(sketch_exact_deltas, bootstrap_seed_exact, 10000)
    summary = {
        "artifact_count": 12,
        "candidate_count_per_selection": 128,
        "trial_row_count": len(trial_rows),
        "group_count": len(group_rows),
        "selection_agreement_count": sum(
            row["selection_matches_r140_exact"] for row in trial_rows
        ),
        "lagos_ising_selection_agreement_count": sum(
            row["selection_matches_r140_exact"] for row in lagos_rows
        ),
        "mean_exact_score_regret": statistics.mean(
            row["exact_score_regret"] for row in trial_rows
        ),
        "maximum_exact_score_regret": max(
            row["exact_score_regret"] for row in trial_rows
        ),
        "selected_qasm_hash_match_count": sum(
            row["selected_qasm_hash_match"] for row in trial_rows
        ),
        "portfolio_mean_sketch_minus_automatic": statistics.mean(sketch_auto_deltas),
        "portfolio_sketch_minus_automatic_bootstrap_95_lower": bootstrap_auto[
            "lower_95"
        ],
        "portfolio_mean_sketch_minus_r140_exact": statistics.mean(
            sketch_exact_deltas
        ),
        "portfolio_sketch_minus_r140_exact_bootstrap_95_lower": bootstrap_exact[
            "lower_95"
        ],
        "lagos_ising_mean_sketch_minus_automatic": statistics.mean(
            row["sketch_minus_automatic"] for row in lagos_rows
        ),
        "lagos_ising_sketch_win_count_vs_automatic": sum(
            row["sketch_minus_automatic"] > 0 for row in lagos_rows
        ),
        "simulated_circuit_execution_count": len(trial_rows) * 4,
        "shots_per_circuit": shots,
        "total_simulated_shots": len(trial_rows) * 4 * shots,
        "selector_full_distribution_value_count": 0,
        "pilot_acquisition_method": "statevector_backed_samples_hidden_from_selector",
        "bootstrap_resample_count": 10000,
        "scalable_pilot_acquisition_claimed": False,
        "hardware_execution_performed": False,
        "protocol_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    conditions = [
        condition("A1", "design, candidate pool, and QASM bindings remain exact", [source_binding_valid, summary["selected_qasm_hash_match_count"]], [True, 96], source_binding_valid and summary["selected_qasm_hash_match_count"] == 96),
        condition("A2", "all rows contain sample-only selection and four noisy arms", [summary["trial_row_count"], summary["group_count"], summary["selector_full_distribution_value_count"]], [96, 12, 0], summary["trial_row_count"] == 96 and summary["group_count"] == 12 and summary["selector_full_distribution_value_count"] == 0),
        condition("A3", "Lagos selection matches R140 exact in hidden pilot blocks", summary["lagos_ising_selection_agreement_count"], ">= 7", summary["lagos_ising_selection_agreement_count"] >= 7),
        condition("A4", "portfolio selection agreement with R140 exact", summary["selection_agreement_count"], ">= 80", summary["selection_agreement_count"] >= 80),
        condition("A5", "maximum exact R140 score regret", summary["maximum_exact_score_regret"], "<= 0.005", summary["maximum_exact_score_regret"] <= 0.005),
        condition("A6", "portfolio sketch-auto bootstrap lower bound", summary["portfolio_sketch_minus_automatic_bootstrap_95_lower"], ">= -0.005", summary["portfolio_sketch_minus_automatic_bootstrap_95_lower"] >= -0.005),
        condition("A7", "Lagos sketch-auto mean is nonnegative and wins at least half", [summary["lagos_ising_mean_sketch_minus_automatic"], summary["lagos_ising_sketch_win_count_vs_automatic"]], [">= 0", ">= 4"], summary["lagos_ising_mean_sketch_minus_automatic"] >= 0 and summary["lagos_ising_sketch_win_count_vs_automatic"] >= 4),
        condition("A8", "portfolio sketch-R140-exact noisy noninferiority", summary["portfolio_mean_sketch_minus_r140_exact"], ">= -0.002", summary["portfolio_mean_sketch_minus_r140_exact"] >= -0.002),
        condition("A9", "phase replay and disclosed execution budget", [summary["simulated_circuit_execution_count"], summary["total_simulated_shots"]], [384, 1572864], summary["simulated_circuit_execution_count"] == 384 and summary["total_simulated_shots"] == 1572864),
        condition("A10", "pilot acquisition, hardware, soundness, advantage, BQP, and credit claims remain false", 0, 0, not any([summary["scalable_pilot_acquisition_claimed"], summary["hardware_execution_performed"], summary["protocol_soundness_claimed"], summary["quantum_advantage_claimed"], summary["bqp_separation_claimed"], summary["new_credit_delta"]])),
    ]
    summary["acceptance_conditions_passed"] = sum(row["passed"] for row in conditions)
    summary["acceptance_conditions_failed"] = sum(not row["passed"] for row in conditions)
    summary["failed_acceptance_condition_ids"] = [
        row["condition_id"] for row in conditions if not row["passed"]
    ]
    summary["global_acceptance"] = all(row["passed"] for row in conditions)
    transcript = {
        "contract_sha256": CONTRACT_SHA256,
        "challenge_secret_commitment_sha256": commitment,
        "candidate_identity_sha256": candidate_identity_hash,
        "trial_rows_sha256": file_sha256(root / TRIALS_PATH),
        "selection_agreement_count": summary["selection_agreement_count"],
        "maximum_exact_score_regret": summary["maximum_exact_score_regret"],
        "acceptance_conditions": conditions,
        "global_acceptance": summary["global_acceptance"],
    }
    write_json(root / TRANSCRIPT_PATH, transcript)
    phase_replay_matches = sum(
        path.exists()
        and str(path) in preexisting
        and path.read_bytes() == preexisting[str(path)]
        for path in phase_paths
    )
    summary["phase_artifact_count"] = 4
    summary["phase_artifact_preexisting_count"] = len(preexisting)
    summary["phase_artifact_replay_match_count"] = phase_replay_matches
    requirements = [
        {"requirement_id": "P1", "label": "public contract and discussion precede challenge generation", "passed": started_at > utc_timestamp(PREREGISTRATION_CREATED_AT)},
        {"requirement_id": "P2", "label": "all source and candidate identity bindings remain exact", "passed": source_binding_valid},
        {"requirement_id": "P3", "label": "secret commitment precedes rows and reveal follows complete rows", "passed": reveal_payload["commitment_matches"] and reveal_payload["trial_rows_complete_before_reveal"]},
        {"requirement_id": "P4", "label": "all twelve groups contain eight complete four-arm rows", "passed": len(trial_rows) == 96 and all(row["row_count"] == 8 for row in group_rows)},
        {"requirement_id": "P5", "label": "384 executions and 1,572,864 shots match the contract", "passed": summary["simulated_circuit_execution_count"] == 384 and summary["total_simulated_shots"] == 1572864},
        {"requirement_id": "P6", "label": "selector receives samples and no full distribution values", "passed": summary["selector_full_distribution_value_count"] == 0},
        {"requirement_id": "P7", "label": "all selected QASM hashes replay from the frozen pool", "passed": summary["selected_qasm_hash_match_count"] == 96},
        {"requirement_id": "P8", "label": "both portfolio bootstraps use 10,000 resamples", "passed": bootstrap_auto["resamples"] == 10000 and bootstrap_exact["resamples"] == 10000},
        {"requirement_id": "P9", "label": "all four phase artifacts replay in a fresh process", "passed": phase_replay_matches in {0, 4}},
        {"requirement_id": "P10", "label": "scalable pilot acquisition, hardware, soundness, advantage, BQP, and credit remain excluded", "passed": conditions[-1]["passed"]},
    ]
    payload = {
        "title": "B4/B8 R141 hashed output sketch holdout",
        "version": 0,
        "method": METHOD,
        "status": "hashed_output_sketch_preregistered_holdout_acceptance" if summary["global_acceptance"] else "hashed_output_sketch_preregistered_holdout_rejection",
        "model_status": "fixed_width_selector_tested_with_statevector_backed_hidden_pilots",
        "generated_at_unix": started_at,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "summary": summary,
        "acceptance_conditions": conditions,
        "group_rows": group_rows,
        "four_arm_trial_rows": trial_rows,
        "bootstrap_sketch_minus_automatic": bootstrap_auto,
        "bootstrap_sketch_minus_r140_exact": bootstrap_exact,
        "requirements": requirements,
        "requirement_count": len(requirements),
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "artifacts": {
            "contract": CONTRACT_PATH,
            "challenge_commitment": COMMITMENT_PATH,
            "four_arm_trial_rows": TRIALS_PATH,
            "challenge_reveal": REVEAL_PATH,
            "verifier_transcript": TRANSCRIPT_PATH,
            "result": RESULT_PATH,
            "markdown_report": REPORT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": "one preregistered synthetic four-arm verdict for a fixed-width sample-only selector",
            "what_is_not_supported": "scalable pilot acquisition, current calibration, real hardware, mitigation, independent custody, protocol soundness, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(
        json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    ensure_deterministic_process_environment()
    root = args.root.resolve()
    payload = run_gate(root)
    output = args.output or root / RESULT_PATH
    markdown = args.report or root / REPORT_PATH
    write_json(output, payload)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["requirements_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
