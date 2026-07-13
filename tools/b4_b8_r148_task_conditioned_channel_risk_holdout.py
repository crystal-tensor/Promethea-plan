#!/usr/bin/env python3
"""Execute the preregistered R148 task-conditioned channel-risk holdout."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from qiskit import qasm3, transpile
from qiskit_aer import AerSimulator

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit, stable_hash
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r132_topology_constrained_route_policy import DETERMINISTIC_PROCESS_ENV, compile_policy
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import exact_distribution, hellinger_fidelity, paired_bootstrap, probability_from_counts
from b4_b8_r139_lagos_ising_channel_attribution import exact_compiled_classical_distribution


METHOD = "b4_b8_r148_task_conditioned_channel_risk_holdout_v0"
CONTRACT_PATH = "benchmarks/B4_B8_R148_task_conditioned_channel_risk_contract_v0.json"
CONTRACT_SHA256 = "fa2c21ca88e6f08ec65c689c44d065e00ca00a5182846ec74ca70177b7103132"
PREREGISTRATION_COMMIT = "fe12c65679f8b34ca9ba58dfa736ad792cf4602d"
PREREGISTRATION_DISCUSSION = "https://github.com/crystal-tensor/Prometheus-plan/discussions/159"
PREREGISTRATION_CREATED_AT = "2026-07-13T10:06:14Z"
PROTOCOL_PATH = "results/B4_B8_R148_task_conditioned_channel_risk_protocol_v0.json"
DESIGN_PATH = "results/B4_B8_R148_task_conditioned_channel_risk_design_v0.json"
R143_PATH = "results/B4_B8_R143_successive_halving_lcb_design_v0.json"
RESULT_PATH = "results/B4_B8_R148_task_conditioned_channel_risk_holdout_v0.json"
REPORT_PATH = "research/B4_B8_R148_task_conditioned_channel_risk_holdout.md"
OUT_DIR = "results/B4_B8_R148_task_conditioned_channel_risk_holdout"
COMMITMENT_PATH = f"{OUT_DIR}/challenge_commitment.json"
TRIALS_PATH = f"{OUT_DIR}/three_arm_trial_rows.json"
REVEAL_PATH = f"{OUT_DIR}/challenge_reveal.json"
TRANSCRIPT_PATH = f"{OUT_DIR}/verifier_transcript.json"


def ensure_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def utc_timestamp(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def derive_seed(secret: bytes, group_id: str, trial: int, role: str) -> int:
    message = f"{CONTRACT_SHA256}|{group_id}|{trial}|{role}".encode()
    digest = hmac.new(secret, message, hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big") % (2**31 - 1) + 1


def condition(condition_id: str, label: str, value: Any, threshold: Any, passed: bool) -> dict[str, Any]:
    return {"condition_id": condition_id, "label": label, "value": value, "threshold": threshold, "passed": passed}


def report(payload: dict) -> str:
    s = payload["summary"]
    verdict = "ACCEPT" if s["global_acceptance"] else "REJECT"
    conditions = "\n".join(
        f"- {row['condition_id']} {'PASS' if row['passed'] else 'FAIL'}: {row['label']}; value {row['value']}, threshold {row['threshold']}."
        for row in payload["acceptance_conditions"]
    )
    targets = "\n".join(
        f"- `{row['target_snapshot']}`: conditioned-target `{row['mean_conditioned_minus_target']:+.8f}`, conditioned-auto `{row['mean_conditioned_minus_automatic']:+.8f}` over `{row['row_count']}` rows."
        for row in payload["target_snapshot_rows"]
    )
    failures = "\n".join(
        f"- `{row['adaptation_group_id']}`: mean `{row['mean_conditioned_minus_target']:+.8f}`, minimum `{row['minimum_conditioned_minus_target']:+.8f}`, severe rows `{row['severe_regression_count']}`."
        for row in payload["r147_failure_group_rows"]
    )
    return f"""# B4/B8 R148 Task-Conditioned Channel-Risk Holdout

- Preregistered verdict: {verdict}
- Groups / trial rows: `{s['adaptation_group_count']}` / `{s['trial_row_count']}`
- Three-arm executions / shots: `{s['simulated_circuit_execution_count']}` / `{s['total_simulated_shots']}`
- Portfolio conditioned-automatic mean / bootstrap lower: `{s['portfolio_mean_conditioned_minus_automatic']:+.8f}` / `{s['portfolio_conditioned_minus_automatic_bootstrap_95_lower']:+.8f}`
- Portfolio conditioned-target mean / bootstrap lower: `{s['portfolio_mean_conditioned_minus_target']:+.8f}` / `{s['portfolio_conditioned_minus_target_bootstrap_95_lower']:+.8f}`
- Groups above -0.02 versus target: `{s['groups_with_mean_conditioned_minus_target_at_least_negative_0_02']} / 12`
- Severe rows below -0.05 versus target: `{s['severe_conditioned_minus_target_regression_count_below_negative_0_05']}`
- Minimum target-snapshot mean: `{s['minimum_target_snapshot_mean_conditioned_minus_target']:+.8f}`
- Minimum R147 failure-group mean / combined severe rows: `{s['minimum_r147_failure_group_mean_conditioned_minus_target']:+.8f}` / `{s['r147_failure_group_severe_regression_count']}`
- Semantic passes: `{s['semantic_fidelity_pass_count']} / 24`
- Conditions passed / failed: `{s['acceptance_conditions_passed']}` / `{s['acceptance_conditions_failed']}`
- New credit delta: `0`

## Target Snapshot Evidence

{targets}

## R147 Failure-Group Repairs

{failures}

## Acceptance Conditions

{conditions}

## Claim Boundary

Supported only if accepted: one preregistered finite six-qubit synthetic
task-conditioned foreign-route verdict. Not supported: scalable exact-output
evaluation, temporal same-device transfer, cross-machine transfer, provider
access, real hardware, mitigation, soundness, quantum advantage, BQP
separation, solved B4/B8/B10, or new credit.
"""


def run_gate(root: Path) -> dict:
    root = root.resolve()
    started_at = int(time.time())
    if started_at <= utc_timestamp(PREREGISTRATION_CREATED_AT):
        raise ValueError("R148 holdout must start after public preregistration")
    if file_sha256(root / CONTRACT_PATH) != CONTRACT_SHA256:
        raise ValueError("R148 contract hash mismatch")
    contract = json.loads((root / CONTRACT_PATH).read_text())
    protocol_payload = json.loads((root / PROTOCOL_PATH).read_text())
    design = json.loads((root / DESIGN_PATH).read_text())
    r143 = json.loads((root / R143_PATH).read_text())
    bindings = contract["source_bindings"]
    if file_sha256(root / PROTOCOL_PATH) != bindings["protocol_sha256"] or protocol_payload["payload_hash"] != bindings["protocol_payload_hash"]:
        raise ValueError("R148 protocol binding mismatch")
    if file_sha256(root / DESIGN_PATH) != bindings["r148_design_sha256"] or design["payload_hash"] != bindings["r148_design_payload_hash"]:
        raise ValueError("R148 design binding mismatch")
    if file_sha256(root / R143_PATH) != bindings["r143_design_sha256"] or r143["payload_hash"] != bindings["r143_design_payload_hash"]:
        raise ValueError("R148 R143 binding mismatch")
    if bindings.get("r147_trial_rows_consumed") is not False or design["summary"]["r147_hidden_trial_rows_read_count"] != 0:
        raise ValueError("R148 forbidden R147 row consumption boundary mismatch")
    protocol = protocol_payload["protocol"]
    tasks = {task["task_id"]: task for task in build_dense_validation_tasks()}
    selections = {(row["target_snapshot"], row["task_id"]): row for row in design["selection_rows"]}
    target_routes = {(row["snapshot"], row["task_id"]): row for row in r143["group_rows"]}

    out = root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    commitment_path = root / COMMITMENT_PATH
    trials_path = root / TRIALS_PATH
    reveal_path = root / REVEAL_PATH
    transcript_path = root / TRANSCRIPT_PATH
    phase_paths = [commitment_path, trials_path, reveal_path, transcript_path]
    preexisting = {str(path): path.read_bytes() for path in phase_paths if path.exists()}
    secret = bytes.fromhex(json.loads(reveal_path.read_text())["challenge_secret_hex"]) if reveal_path.exists() else os.urandom(32)
    commitment = hashlib.sha256(secret).hexdigest()
    if commitment_path.exists():
        commitment_payload = json.loads(commitment_path.read_text())
        if commitment_payload["challenge_secret_commitment_sha256"] != commitment:
            raise ValueError("R148 challenge commitment mismatch")
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

    trial_rows = []
    compiled_rows = []
    for target_snapshot in protocol["snapshot_names"]:
        backend = SNAPSHOT_CLASSES[target_snapshot]()
        simulator = AerSimulator.from_backend(backend)
        for task_id in protocol["task_ids"]:
            group_id = f"{target_snapshot}::{task_id}"
            task = tasks[task_id]
            logical = basis_circuit(task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits)))
            ideal = exact_distribution(task["circuit"])
            selected = selections[(target_snapshot, task_id)]
            target_route = target_routes[(target_snapshot, task_id)]
            conditioned = compile_policy(logical, backend, selected["selected_mapping"], selected["selected_policy_id"], selected["selected_realization_seed"])
            target = compile_policy(logical, backend, target_route["selected_mapping"], target_route["selected_policy_id"], target_route["selected_realization_seed"])
            conditioned_semantic = hellinger_fidelity(ideal, exact_compiled_classical_distribution(conditioned))
            target_semantic = hellinger_fidelity(ideal, exact_compiled_classical_distribution(target))
            compiled_rows.append({
                "adaptation_group_id": group_id,
                "target_snapshot": target_snapshot,
                "task_id": task_id,
                "channel_priority_mode": selected["channel_priority_mode"],
                "conditioned_source_snapshot": selected["selected_source_snapshot"],
                "selection_changed_from_r147": selected["selection_changed_from_r147"],
                "conditioned_mapping": selected["selected_mapping"],
                "conditioned_policy_id": selected["selected_policy_id"],
                "conditioned_realization_seed": selected["selected_realization_seed"],
                "conditioned_qasm_stable_hash": stable_hash(qasm3.dumps(conditioned)),
                "target_specific_qasm_stable_hash": stable_hash(qasm3.dumps(target)),
                "conditioned_semantic_fidelity": conditioned_semantic,
                "target_specific_semantic_fidelity": target_semantic,
            })
            for trial in range(protocol["hidden_trial_count_per_group"]):
                transpiler_seed = derive_seed(secret, group_id, trial, "transpiler")
                simulator_seed = derive_seed(secret, group_id, trial, "simulator")
                automatic = transpile(logical, backend=backend, optimization_level=3, seed_transpiler=transpiler_seed)
                fidelities = {}
                for arm, circuit in [("task_conditioned_foreign", conditioned), ("target_specific", target), ("automatic", automatic)]:
                    counts = simulator.run(circuit, shots=protocol["shots_per_execution"], seed_simulator=simulator_seed).result().get_counts()
                    observed = probability_from_counts(counts, protocol["shots_per_execution"], task["circuit"].num_qubits)
                    fidelities[arm] = hellinger_fidelity(ideal, observed)
                trial_rows.append({
                    "adaptation_group_id": group_id,
                    "target_snapshot": target_snapshot,
                    "task_id": task_id,
                    "trial": trial,
                    "transpiler_seed": transpiler_seed,
                    "simulator_seed": simulator_seed,
                    "task_conditioned_fidelity": fidelities["task_conditioned_foreign"],
                    "target_specific_fidelity": fidelities["target_specific"],
                    "automatic_fidelity": fidelities["automatic"],
                    "conditioned_minus_automatic": fidelities["task_conditioned_foreign"] - fidelities["automatic"],
                    "conditioned_minus_target": fidelities["task_conditioned_foreign"] - fidelities["target_specific"],
                })
    write_json(trials_path, trial_rows)
    reveal = {
        "contract_sha256": CONTRACT_SHA256,
        "challenge_secret_hex": secret.hex(),
        "challenge_secret_commitment_sha256": commitment,
        "commitment_matches": hashlib.sha256(secret).hexdigest() == commitment,
        "trial_rows_complete_before_reveal": len(trial_rows) == protocol["trial_row_count"],
    }
    write_json(reveal_path, reveal)

    group_rows = []
    for group_id in sorted({row["adaptation_group_id"] for row in trial_rows}):
        rows = [row for row in trial_rows if row["adaptation_group_id"] == group_id]
        group_rows.append({
            "adaptation_group_id": group_id,
            "target_snapshot": rows[0]["target_snapshot"],
            "task_id": rows[0]["task_id"],
            "row_count": len(rows),
            "mean_conditioned_minus_automatic": statistics.mean(row["conditioned_minus_automatic"] for row in rows),
            "mean_conditioned_minus_target": statistics.mean(row["conditioned_minus_target"] for row in rows),
            "conditioned_win_count_vs_automatic": sum(row["conditioned_minus_automatic"] > 0 for row in rows),
            "conditioned_win_count_vs_target": sum(row["conditioned_minus_target"] > 0 for row in rows),
            "minimum_conditioned_minus_target": min(row["conditioned_minus_target"] for row in rows),
            "severe_regression_count": sum(row["conditioned_minus_target"] < -0.05 for row in rows),
        })
    target_rows = []
    for target_snapshot in protocol["snapshot_names"]:
        rows = [row for row in trial_rows if row["target_snapshot"] == target_snapshot]
        target_rows.append({
            "target_snapshot": target_snapshot,
            "row_count": len(rows),
            "mean_conditioned_minus_automatic": statistics.mean(row["conditioned_minus_automatic"] for row in rows),
            "mean_conditioned_minus_target": statistics.mean(row["conditioned_minus_target"] for row in rows),
        })
    failure_group_rows = [row for row in group_rows if row["adaptation_group_id"] in protocol["r147_failure_group_ids"]]
    auto_deltas = [row["conditioned_minus_automatic"] for row in trial_rows]
    target_deltas = [row["conditioned_minus_target"] for row in trial_rows]
    bootstrap_auto = paired_bootstrap(auto_deltas, derive_seed(secret, "portfolio", 0, "bootstrap-auto"), 10000)
    bootstrap_target = paired_bootstrap(target_deltas, derive_seed(secret, "portfolio", 0, "bootstrap-target"), 10000)
    semantic_values = [value for row in compiled_rows for value in [row["conditioned_semantic_fidelity"], row["target_specific_semantic_fidelity"]]]
    summary = {
        "adaptation_group_count": len(group_rows),
        "trial_row_count": len(trial_rows),
        "simulated_circuit_execution_count": len(trial_rows) * 3,
        "total_simulated_shots": len(trial_rows) * 3 * protocol["shots_per_execution"],
        "portfolio_mean_conditioned_minus_automatic": statistics.mean(auto_deltas),
        "portfolio_conditioned_minus_automatic_bootstrap_95_lower": bootstrap_auto["lower_95"],
        "portfolio_conditioned_minus_automatic_bootstrap_95_upper": bootstrap_auto["upper_95"],
        "portfolio_mean_conditioned_minus_target": statistics.mean(target_deltas),
        "portfolio_conditioned_minus_target_bootstrap_95_lower": bootstrap_target["lower_95"],
        "portfolio_conditioned_minus_target_bootstrap_95_upper": bootstrap_target["upper_95"],
        "groups_with_mean_conditioned_minus_target_at_least_negative_0_02": sum(row["mean_conditioned_minus_target"] >= -0.02 for row in group_rows),
        "severe_conditioned_minus_target_regression_count_below_negative_0_05": sum(value < -0.05 for value in target_deltas),
        "minimum_target_snapshot_mean_conditioned_minus_target": min(row["mean_conditioned_minus_target"] for row in target_rows),
        "r147_failure_group_count": len(failure_group_rows),
        "minimum_r147_failure_group_mean_conditioned_minus_target": min(row["mean_conditioned_minus_target"] for row in failure_group_rows),
        "r147_failure_group_severe_regression_count": sum(row["severe_regression_count"] for row in failure_group_rows),
        "minimum_semantic_fidelity": min(semantic_values),
        "semantic_fidelity_pass_count": sum(value >= protocol["minimum_semantic_fidelity"] for value in semantic_values),
        "selection_change_count_from_r147": sum(row["selection_changed_from_r147"] for row in compiled_rows),
        "phase_artifact_count": 4,
        "phase_artifact_preexisting_count": len(preexisting),
        "r147_hidden_trial_rows_read_count": 0,
        "target_specific_routes_in_selector_count": 0,
        "scalable_exact_output_method_claimed": False,
        "temporal_same_device_transfer_claimed": False,
        "cross_machine_transfer_claimed": False,
        "hardware_execution_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
    }
    a8_pass = summary["minimum_target_snapshot_mean_conditioned_minus_target"] >= protocol["minimum_each_target_mean_conditioned_minus_target"] and summary["minimum_r147_failure_group_mean_conditioned_minus_target"] >= protocol["minimum_each_r147_failure_group_mean_conditioned_minus_target"] and summary["r147_failure_group_severe_regression_count"] <= protocol["maximum_r147_failure_group_severe_regression_count"]
    conditions = [
        condition("A1", "protocol, selector, route identities, and source bindings remain exact", True, True, True),
        condition("A2", "groups, rows, and executions", [summary["adaptation_group_count"], summary["trial_row_count"], summary["simulated_circuit_execution_count"]], [12, 96, 288], summary["adaptation_group_count"] == 12 and summary["trial_row_count"] == 96 and summary["simulated_circuit_execution_count"] == 288),
        condition("A3", "all conditioned and target routes retain semantic fidelity", [summary["semantic_fidelity_pass_count"], summary["minimum_semantic_fidelity"]], [24, protocol["minimum_semantic_fidelity"]], summary["semantic_fidelity_pass_count"] == 24),
        condition("A4", "portfolio conditioned versus automatic noninferiority", [summary["portfolio_mean_conditioned_minus_automatic"], summary["portfolio_conditioned_minus_automatic_bootstrap_95_lower"]], [protocol["minimum_portfolio_conditioned_minus_automatic_mean"], protocol["minimum_portfolio_conditioned_minus_automatic_bootstrap_lower"]], summary["portfolio_mean_conditioned_minus_automatic"] >= protocol["minimum_portfolio_conditioned_minus_automatic_mean"] and summary["portfolio_conditioned_minus_automatic_bootstrap_95_lower"] >= protocol["minimum_portfolio_conditioned_minus_automatic_bootstrap_lower"]),
        condition("A5", "portfolio conditioned versus target-specific noninferiority", [summary["portfolio_mean_conditioned_minus_target"], summary["portfolio_conditioned_minus_target_bootstrap_95_lower"]], [protocol["minimum_portfolio_conditioned_minus_target_mean"], protocol["minimum_portfolio_conditioned_minus_target_bootstrap_lower"]], summary["portfolio_mean_conditioned_minus_target"] >= protocol["minimum_portfolio_conditioned_minus_target_mean"] and summary["portfolio_conditioned_minus_target_bootstrap_95_lower"] >= protocol["minimum_portfolio_conditioned_minus_target_bootstrap_lower"]),
        condition("A6", "groups above negative 0.02 versus target", summary["groups_with_mean_conditioned_minus_target_at_least_negative_0_02"], protocol["minimum_group_count_above_negative_0_02_vs_target"], summary["groups_with_mean_conditioned_minus_target_at_least_negative_0_02"] >= protocol["minimum_group_count_above_negative_0_02_vs_target"]),
        condition("A7", "severe row regressions below negative 0.05", summary["severe_conditioned_minus_target_regression_count_below_negative_0_05"], protocol["maximum_severe_regression_count_below_negative_0_05_vs_target"], summary["severe_conditioned_minus_target_regression_count_below_negative_0_05"] <= protocol["maximum_severe_regression_count_below_negative_0_05_vs_target"]),
        condition("A8", "each-target and all R147 failure-group guards", [summary["minimum_target_snapshot_mean_conditioned_minus_target"], summary["minimum_r147_failure_group_mean_conditioned_minus_target"], summary["r147_failure_group_severe_regression_count"]], [protocol["minimum_each_target_mean_conditioned_minus_target"], protocol["minimum_each_r147_failure_group_mean_conditioned_minus_target"], protocol["maximum_r147_failure_group_severe_regression_count"]], a8_pass),
        condition("A9", "commitment, hidden rows, reveal, and transcript", reveal["commitment_matches"] and reveal["trial_rows_complete_before_reveal"], True, reveal["commitment_matches"] and reveal["trial_rows_complete_before_reveal"]),
        condition("A10", "forbidden claims and credit remain false", 0, 0, not any([summary["scalable_exact_output_method_claimed"], summary["temporal_same_device_transfer_claimed"], summary["cross_machine_transfer_claimed"], summary["hardware_execution_claimed"], summary["quantum_advantage_claimed"], summary["bqp_separation_claimed"], summary["solved_frontier_claimed"], summary["new_credit_delta"]])),
    ]
    summary.update({
        "acceptance_conditions_passed": sum(row["passed"] for row in conditions),
        "acceptance_conditions_failed": sum(not row["passed"] for row in conditions),
        "failed_acceptance_condition_ids": [row["condition_id"] for row in conditions if not row["passed"]],
        "global_acceptance": all(row["passed"] for row in conditions),
    })
    transcript = {"contract_sha256": CONTRACT_SHA256, "trial_rows_sha256": file_sha256(trials_path), "challenge_secret_commitment_sha256": commitment, "acceptance_conditions": conditions, "global_acceptance": summary["global_acceptance"]}
    write_json(transcript_path, transcript)
    phase_replay = sum(path.exists() and (str(path) not in preexisting or path.read_bytes() == preexisting[str(path)]) for path in phase_paths)
    summary["phase_artifact_replay_match_count"] = phase_replay
    requirements = [
        {"requirement_id": "P1", "label": "public preregistration precedes challenge", "passed": started_at >= utc_timestamp(PREREGISTRATION_CREATED_AT)},
        {"requirement_id": "P2", "label": "contract, protocol, design, and R143 hashes verify", "passed": True},
        {"requirement_id": "P3", "label": "12 frozen groups execute", "passed": len(group_rows) == 12},
        {"requirement_id": "P4", "label": "all three arms share one row seed", "passed": len(trial_rows) == 96},
        {"requirement_id": "P5", "label": "commitment matches revealed secret", "passed": reveal["commitment_matches"]},
        {"requirement_id": "P6", "label": "trial rows are complete before reveal", "passed": reveal["trial_rows_complete_before_reveal"]},
        {"requirement_id": "P7", "label": "24 compiled route semantic checks pass", "passed": summary["semantic_fidelity_pass_count"] == 24},
        {"requirement_id": "P8", "label": "four phase artifacts replay", "passed": phase_replay == 4},
        {"requirement_id": "P9", "label": "acceptance transcript contains A1-A10", "passed": len(conditions) == 10},
        {"requirement_id": "P10", "label": "R147 rows stay unused and claim boundary remains explicit", "passed": summary["r147_hidden_trial_rows_read_count"] == 0 and conditions[-1]["passed"]},
    ]
    payload = {
        "title": "B4/B8 R148 task-conditioned channel-risk holdout",
        "version": 0,
        "method": METHOD,
        "status": "task_conditioned_channel_risk_preregistered_acceptance" if summary["global_acceptance"] else "task_conditioned_channel_risk_preregistered_rejection",
        "model_status": "finite_six_qubit_zero_fit_channel_priority_foreign_route_holdout",
        "generated_at_unix": started_at,
        "source_target_id": "T-B4-002bf/T-B8-003bj/T-B10-009ax",
        "upstream_target_id": "T-B4-002be/T-B8-003bi/T-B10-009aw",
        "summary": summary,
        "acceptance_conditions": conditions,
        "compiled_route_rows": compiled_rows,
        "group_rows": group_rows,
        "target_snapshot_rows": target_rows,
        "r147_failure_group_rows": failure_group_rows,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "artifacts": {"contract": CONTRACT_PATH, "challenge_commitment": COMMITMENT_PATH, "three_arm_trial_rows": TRIALS_PATH, "challenge_reveal": REVEAL_PATH, "verifier_transcript": TRANSCRIPT_PATH, "result": RESULT_PATH, "markdown_report": REPORT_PATH},
        "claim_boundary": {"what_is_supported": "one preregistered finite six-qubit synthetic task-conditioned foreign-route verdict", "what_is_not_supported": "scalable exact-output evaluation, temporal same-device transfer, cross-machine transfer, provider access, real hardware, mitigation, soundness, quantum advantage, BQP separation, solved B4/B8/B10, or new credit"},
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    return payload


def main() -> int:
    ensure_environment()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    payload = run_gate(args.root)
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "requirements_passed": payload["requirements_passed"], "requirements_failed": payload["requirements_failed"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
