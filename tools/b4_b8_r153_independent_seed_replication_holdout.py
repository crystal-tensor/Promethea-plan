#!/usr/bin/env python3
"""Execute the preregistered R153 independent hidden-seed replication."""

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
from qiskit_ibm_runtime.fake_provider import FakeCasablancaV2, FakeNairobiV2, FakePerth

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit, stable_hash
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r132_topology_constrained_route_policy import DETERMINISTIC_PROCESS_ENV, compile_policy
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import exact_distribution, hellinger_fidelity, paired_bootstrap, probability_from_counts
from b4_b8_r139_lagos_ising_channel_attribution import exact_compiled_classical_distribution


METHOD = "b4_b8_r153_independent_seed_replication_holdout_v0"
CONTRACT_PATH = "benchmarks/B4_B8_R153_independent_seed_replication_contract_v0.json"
CONTRACT_SHA256 = "99aae34034c9193cdc58a4aa62b68208c664098a2b44773ccf86c075850e46f7"
PREREGISTRATION_COMMIT = "61ae44dd625ac050338097277cbcb450f9831c7e"
PREREGISTRATION_DISCUSSION = "https://github.com/crystal-tensor/Prometheus-plan/discussions/168"
PREREGISTRATION_CREATED_AT = "2026-07-13T12:52:52Z"
PROTOCOL_PATH = "results/B4_B8_R153_independent_seed_replication_protocol_v0.json"
DESIGN_PATH = "results/B4_B8_R152_edge_signature_expansion_design_v0.json"
R150_DESIGN_PATH = "results/B4_B8_R150_unseen_backend_candidate_generation_design_v0.json"
R152_RESULT_PATH = "results/B4_B8_R152_edge_signature_expansion_holdout_v0.json"
RESULT_PATH = "results/B4_B8_R153_independent_seed_replication_holdout_v0.json"
REPORT_PATH = "research/B4_B8_R153_independent_seed_replication_holdout.md"
OUT_DIR = "results/B4_B8_R153_independent_seed_replication_holdout"
COMMITMENT_PATH = f"{OUT_DIR}/challenge_commitment.json"
TRIALS_PATH = f"{OUT_DIR}/three_arm_trial_rows.json"
REVEAL_PATH = f"{OUT_DIR}/challenge_reveal.json"
TRANSCRIPT_PATH = f"{OUT_DIR}/verifier_transcript.json"
TARGET_CLASSES = {
    "FakeCasablancaV2": FakeCasablancaV2,
    "FakeNairobiV2": FakeNairobiV2,
    "FakePerth": FakePerth,
}


def ensure_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def utc_timestamp(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def derive_seed(secret: bytes, group_id: str, trial: int, role: str) -> int:
    digest = hmac.new(secret, f"{CONTRACT_SHA256}|{group_id}|{trial}|{role}".encode(), hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big") % (2**31 - 1) + 1


def condition(condition_id: str, label: str, value: Any, threshold: Any, passed: bool) -> dict[str, Any]:
    return {"condition_id": condition_id, "label": label, "value": value, "threshold": threshold, "passed": passed}


def report(payload: dict) -> str:
    s = payload["summary"]
    verdict = "ACCEPT" if s["global_acceptance"] else "REJECT"
    groups = "\n".join(
        f"- `{row['target_snapshot']}`: repaired-denominator `{row['mean_repaired_minus_denominator']:+.8f}`, repaired-auto `{row['mean_repaired_minus_automatic']:+.8f}`, minimum `{row['minimum_repaired_minus_denominator']:+.8f}`, severe rows `{row['severe_regression_count']}`."
        for row in payload["group_rows"]
    )
    conditions = "\n".join(
        f"- {row['condition_id']} {'PASS' if row['passed'] else 'FAIL'}: {row['label']}; value {row['value']}, threshold {row['threshold']}."
        for row in payload["acceptance_conditions"]
    )
    blocks = "\n".join(
        f"- `{row['target_snapshot']}` block `{row['block_index']}`: repaired-denominator `{row['mean_repaired_minus_denominator']:+.8f}`, minimum `{row['minimum_repaired_minus_denominator']:+.8f}`, wins `{row['repaired_win_count_vs_denominator']} / {row['row_count']}`."
        for row in payload["block_rows"]
    )
    return f"""# B4/B8 R153 Independent Seed Replication Holdout

- Preregistered verdict: {verdict}
- Groups / trial rows / executions: `{s['portfolio_group_count']}` / `{s['trial_row_count']}` / `{s['simulated_circuit_execution_count']}`
- Portfolio repaired-automatic mean / bootstrap lower: `{s['portfolio_mean_repaired_minus_automatic']:+.8f}` / `{s['portfolio_repaired_minus_automatic_bootstrap_95_lower']:+.8f}`
- Portfolio repaired-denominator mean / bootstrap lower: `{s['portfolio_mean_repaired_minus_denominator']:+.8f}` / `{s['portfolio_repaired_minus_denominator_bootstrap_95_lower']:+.8f}`
- Groups above -0.02 versus denominator: `{s['groups_with_mean_repaired_minus_denominator_at_least_negative_0_02']} / 3`
- Blocks above -0.03 versus denominator: `{s['blocks_with_mean_repaired_minus_denominator_at_least_negative_0_03']} / {s['independent_block_count']}`
- Maximum within-backend block spread: `{s['maximum_within_backend_block_mean_spread']:.8f}`
- Severe rows below -0.05: `{s['severe_repaired_minus_denominator_regression_count_below_negative_0_05']}`
- Semantic passes: `{s['semantic_fidelity_pass_count']} / 6`
- Conditions passed / failed: `{s['acceptance_conditions_passed']}` / `{s['acceptance_conditions_failed']}`
- New credit delta: `0`

## Backend Evidence

{groups}

## Independent Block Evidence

{blocks}

## Acceptance Conditions

{conditions}

## Claim Boundary

Supported only if accepted: one preregistered independent hidden-seed
replication of the accepted R152 routes across four blocks per backend. Not
supported: causal repair, temporal transfer, real-device transfer, hardware
performance, general route-generation advantage, quantum advantage, BQP
separation, solved B4/B8/B10, or new credit.
"""


def run_gate(root: Path) -> dict:
    root = root.resolve()
    started_at = int(time.time())
    if started_at <= utc_timestamp(PREREGISTRATION_CREATED_AT):
        raise ValueError("R153 holdout must start after public preregistration")
    if file_sha256(root / CONTRACT_PATH) != CONTRACT_SHA256:
        raise ValueError("R153 contract hash mismatch")
    contract = json.loads((root / CONTRACT_PATH).read_text())
    protocol_payload = json.loads((root / PROTOCOL_PATH).read_text())
    design = json.loads((root / DESIGN_PATH).read_text())
    r150_design = json.loads((root / R150_DESIGN_PATH).read_text())
    r152_result = json.loads((root / R152_RESULT_PATH).read_text())
    bindings = contract["source_bindings"]
    if file_sha256(root / PROTOCOL_PATH) != bindings["protocol_sha256"] or protocol_payload["payload_hash"] != bindings["protocol_payload_hash"]:
        raise ValueError("R153 protocol binding mismatch")
    if file_sha256(root / R152_RESULT_PATH) != bindings["r152_result_sha256"] or r152_result["payload_hash"] != bindings["r152_result_payload_hash"]:
        raise ValueError("R153 accepted R152-result binding mismatch")
    if r152_result["summary"]["global_acceptance"] is not True:
        raise ValueError("R153 requires an accepted R152 source result")
    if file_sha256(root / DESIGN_PATH) != bindings["r152_design_sha256"] or design["payload_hash"] != bindings["r152_design_payload_hash"]:
        raise ValueError("R153 R152-design binding mismatch")
    if file_sha256(root / R150_DESIGN_PATH) != bindings["r150_design_sha256"] or r150_design["payload_hash"] != bindings["r150_design_payload_hash"]:
        raise ValueError("R153 R150-control design binding mismatch")
    if bindings.get("r153_candidate_selection_performed") is not False:
        raise ValueError("R153 candidate-selection boundary mismatch")
    if protocol_payload["source_bindings"].get("r153_candidate_selection_performed") is not False:
        raise ValueError("R153 protocol candidate-selection boundary mismatch")
    selected_path = root / design["summary"]["selected_circuit_path"]
    if file_sha256(selected_path) != design["summary"]["selected_circuit_sha256"]:
        raise ValueError("R153 frozen Casablanca circuit hash mismatch")
    protocol = protocol_payload["protocol"]
    task = next(row for row in build_dense_validation_tasks() if row["task_id"] == protocol["task_id"])
    logical = basis_circuit(task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits)))
    ideal = exact_distribution(task["circuit"])
    target_rows = {row["target_snapshot"]: row for row in r150_design["target_rows"]}

    out = root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    phase_paths = [root / COMMITMENT_PATH, root / TRIALS_PATH, root / REVEAL_PATH, root / TRANSCRIPT_PATH]
    commitment_path, trials_path, reveal_path, transcript_path = phase_paths
    preexisting = {str(path): path.read_bytes() for path in phase_paths if path.exists()}
    secret = bytes.fromhex(json.loads(reveal_path.read_text())["challenge_secret_hex"]) if reveal_path.exists() else os.urandom(32)
    commitment = hashlib.sha256(secret).hexdigest()
    if commitment_path.exists():
        commitment_payload = json.loads(commitment_path.read_text())
        if commitment_payload["challenge_secret_commitment_sha256"] != commitment:
            raise ValueError("R153 challenge commitment mismatch")
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
    for target_name in protocol["snapshot_names"]:
        backend = TARGET_CLASSES[target_name]()
        simulator = AerSimulator.from_backend(backend)
        selected = target_rows[target_name]
        if target_name == "FakeCasablancaV2":
            repaired = qasm3.load(selected_path)
            repaired_source = "R152_novel_edge_signature"
            repaired_seed = design["summary"]["selected_transpiler_seed"]
        else:
            repaired = compile_policy(logical, backend, selected["selected_mapping"], selected["selected_policy_id"], selected["selected_realization_seed"])
            repaired_source = "R150_preserved_generated_control"
            repaired_seed = selected["selected_realization_seed"]
        denominator = qasm3.load(root / selected["denominator_circuit_path"])
        repaired_semantic = hellinger_fidelity(ideal, exact_compiled_classical_distribution(repaired))
        denominator_semantic = hellinger_fidelity(ideal, exact_compiled_classical_distribution(denominator))
        compiled_rows.append({
            "target_snapshot": target_name,
            "repaired_route_source": repaired_source,
            "repaired_route_seed": repaired_seed,
            "repaired_mapping": None if target_name == "FakeCasablancaV2" else selected["selected_mapping"],
            "repaired_policy_id": None if target_name == "FakeCasablancaV2" else selected["selected_policy_id"],
            "repaired_qasm_stable_hash": stable_hash(qasm3.dumps(repaired)),
            "denominator_transpiler_seed": selected["denominator_transpiler_seed"],
            "denominator_qasm_stable_hash": stable_hash(qasm3.dumps(denominator)),
            "repaired_semantic_fidelity": repaired_semantic,
            "denominator_semantic_fidelity": denominator_semantic,
        })
        for trial in range(protocol["hidden_trial_count_per_group"]):
            transpiler_seed = derive_seed(secret, target_name, trial, "transpiler")
            simulator_seed = derive_seed(secret, target_name, trial, "simulator")
            automatic = transpile(logical, backend=backend, optimization_level=3, seed_transpiler=transpiler_seed)
            fidelities = {}
            for arm, circuit in [("repaired", repaired), ("denominator", denominator), ("automatic", automatic)]:
                counts = simulator.run(circuit, shots=protocol["shots_per_execution"], seed_simulator=simulator_seed).result().get_counts()
                observed = probability_from_counts(counts, protocol["shots_per_execution"], task["circuit"].num_qubits)
                fidelities[arm] = hellinger_fidelity(ideal, observed)
            trial_rows.append({
                "target_snapshot": target_name,
                "task_id": protocol["task_id"],
                "trial": trial,
                "block_index": trial // protocol["trial_count_per_block"],
                "trial_in_block": trial % protocol["trial_count_per_block"],
                "transpiler_seed": transpiler_seed,
                "simulator_seed": simulator_seed,
                "repaired_fidelity": fidelities["repaired"],
                "denominator_fidelity": fidelities["denominator"],
                "automatic_fidelity": fidelities["automatic"],
                "repaired_minus_automatic": fidelities["repaired"] - fidelities["automatic"],
                "repaired_minus_denominator": fidelities["repaired"] - fidelities["denominator"],
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
    for target_name in protocol["snapshot_names"]:
        rows = [row for row in trial_rows if row["target_snapshot"] == target_name]
        group_rows.append({
            "target_snapshot": target_name,
            "row_count": len(rows),
            "mean_repaired_minus_automatic": statistics.mean(row["repaired_minus_automatic"] for row in rows),
            "mean_repaired_minus_denominator": statistics.mean(row["repaired_minus_denominator"] for row in rows),
            "minimum_repaired_minus_denominator": min(row["repaired_minus_denominator"] for row in rows),
            "repaired_win_count_vs_denominator": sum(row["repaired_minus_denominator"] > 0 for row in rows),
            "severe_regression_count": sum(row["repaired_minus_denominator"] < -0.05 for row in rows),
        })
    block_rows = []
    backend_block_spreads = []
    for target_name in protocol["snapshot_names"]:
        target_blocks = []
        for block_index in range(protocol["independent_block_count_per_group"]):
            rows = [
                row
                for row in trial_rows
                if row["target_snapshot"] == target_name and row["block_index"] == block_index
            ]
            block_row = {
                "target_snapshot": target_name,
                "block_index": block_index,
                "row_count": len(rows),
                "mean_repaired_minus_automatic": statistics.mean(row["repaired_minus_automatic"] for row in rows),
                "mean_repaired_minus_denominator": statistics.mean(row["repaired_minus_denominator"] for row in rows),
                "minimum_repaired_minus_denominator": min(row["repaired_minus_denominator"] for row in rows),
                "repaired_win_count_vs_denominator": sum(row["repaired_minus_denominator"] > 0 for row in rows),
                "severe_regression_count": sum(row["repaired_minus_denominator"] < -0.05 for row in rows),
            }
            block_rows.append(block_row)
            target_blocks.append(block_row)
        block_means = [row["mean_repaired_minus_denominator"] for row in target_blocks]
        backend_block_spreads.append(max(block_means) - min(block_means))
    auto_deltas = [row["repaired_minus_automatic"] for row in trial_rows]
    denominator_deltas = [row["repaired_minus_denominator"] for row in trial_rows]
    bootstrap_auto = paired_bootstrap(auto_deltas, derive_seed(secret, "portfolio", 0, "bootstrap-auto"), 10000)
    bootstrap_denominator = paired_bootstrap(denominator_deltas, derive_seed(secret, "portfolio", 0, "bootstrap-denominator"), 10000)
    semantic_values = [value for row in compiled_rows for value in [row["repaired_semantic_fidelity"], row["denominator_semantic_fidelity"]]]
    summary = {
        "portfolio_group_count": len(group_rows),
        "trial_row_count": len(trial_rows),
        "simulated_circuit_execution_count": len(trial_rows) * 3,
        "total_simulated_shots": len(trial_rows) * 3 * protocol["shots_per_execution"],
        "portfolio_mean_repaired_minus_automatic": statistics.mean(auto_deltas),
        "portfolio_repaired_minus_automatic_bootstrap_95_lower": bootstrap_auto["lower_95"],
        "portfolio_repaired_minus_automatic_bootstrap_95_upper": bootstrap_auto["upper_95"],
        "portfolio_mean_repaired_minus_denominator": statistics.mean(denominator_deltas),
        "portfolio_repaired_minus_denominator_bootstrap_95_lower": bootstrap_denominator["lower_95"],
        "portfolio_repaired_minus_denominator_bootstrap_95_upper": bootstrap_denominator["upper_95"],
        "groups_with_mean_repaired_minus_denominator_at_least_negative_0_02": sum(row["mean_repaired_minus_denominator"] >= -0.02 for row in group_rows),
        "independent_block_count": len(block_rows),
        "blocks_with_mean_repaired_minus_denominator_at_least_negative_0_03": sum(row["mean_repaired_minus_denominator"] >= -0.03 for row in block_rows),
        "maximum_within_backend_block_mean_spread": max(backend_block_spreads),
        "severe_repaired_minus_denominator_regression_count_below_negative_0_05": sum(value < -0.05 for value in denominator_deltas),
        "minimum_target_mean_repaired_minus_denominator": min(row["mean_repaired_minus_denominator"] for row in group_rows),
        "minimum_semantic_fidelity": min(semantic_values),
        "semantic_fidelity_pass_count": sum(value >= protocol["minimum_semantic_fidelity"] for value in semantic_values),
        "phase_artifact_count": 4,
        "phase_artifact_preexisting_count": len(preexisting),
        "r153_candidate_selection_performed": False,
        "causal_repair_claimed": False,
        "temporal_transfer_claimed": False,
        "real_device_transfer_claimed": False,
        "hardware_execution_claimed": False,
        "general_route_generation_advantage_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
    }
    conditions = [
        condition("A1", "contract, protocol, accepted R152 result, routes, denominators, and bindings remain exact", True, True, True),
        condition("A2", "groups, rows, executions, blocks, and same-seed arms", [summary["portfolio_group_count"], summary["trial_row_count"], summary["simulated_circuit_execution_count"], summary["independent_block_count"]], [3, 96, 288, 12], summary["portfolio_group_count"] == 3 and summary["trial_row_count"] == 96 and summary["simulated_circuit_execution_count"] == 288 and summary["independent_block_count"] == 12),
        condition("A3", "all repaired and denominator routes retain semantics", [summary["semantic_fidelity_pass_count"], summary["minimum_semantic_fidelity"]], [6, protocol["minimum_semantic_fidelity"]], summary["semantic_fidelity_pass_count"] == 6),
        condition("A4", "portfolio repaired versus automatic noninferiority", [summary["portfolio_mean_repaired_minus_automatic"], summary["portfolio_repaired_minus_automatic_bootstrap_95_lower"]], [protocol["minimum_portfolio_repaired_minus_automatic_mean"], protocol["minimum_portfolio_repaired_minus_automatic_bootstrap_lower"]], summary["portfolio_mean_repaired_minus_automatic"] >= protocol["minimum_portfolio_repaired_minus_automatic_mean"] and summary["portfolio_repaired_minus_automatic_bootstrap_95_lower"] >= protocol["minimum_portfolio_repaired_minus_automatic_bootstrap_lower"]),
        condition("A5", "portfolio repaired versus strong denominator noninferiority", [summary["portfolio_mean_repaired_minus_denominator"], summary["portfolio_repaired_minus_denominator_bootstrap_95_lower"]], [protocol["minimum_portfolio_repaired_minus_denominator_mean"], protocol["minimum_portfolio_repaired_minus_denominator_bootstrap_lower"]], summary["portfolio_mean_repaired_minus_denominator"] >= protocol["minimum_portfolio_repaired_minus_denominator_mean"] and summary["portfolio_repaired_minus_denominator_bootstrap_95_lower"] >= protocol["minimum_portfolio_repaired_minus_denominator_bootstrap_lower"]),
        condition("A6", "all groups above negative 0.02 versus denominator", summary["groups_with_mean_repaired_minus_denominator_at_least_negative_0_02"], protocol["minimum_group_count_above_negative_0_02_vs_denominator"], summary["groups_with_mean_repaired_minus_denominator_at_least_negative_0_02"] >= protocol["minimum_group_count_above_negative_0_02_vs_denominator"]),
        condition("A7", "severe row regressions below negative 0.05", summary["severe_repaired_minus_denominator_regression_count_below_negative_0_05"], protocol["maximum_severe_regression_count_below_negative_0_05_vs_denominator"], summary["severe_repaired_minus_denominator_regression_count_below_negative_0_05"] <= protocol["maximum_severe_regression_count_below_negative_0_05_vs_denominator"]),
        condition("A8", "Casablanca mean, independent block count, and within-backend block spread clear frozen floors", [next(row["mean_repaired_minus_denominator"] for row in group_rows if row["target_snapshot"] == "FakeCasablancaV2"), summary["blocks_with_mean_repaired_minus_denominator_at_least_negative_0_03"], summary["maximum_within_backend_block_mean_spread"]], [protocol["minimum_casablanca_mean_repaired_minus_denominator"], protocol["minimum_block_count_above_negative_0_03_vs_denominator"], protocol["maximum_block_mean_spread"]], next(row["mean_repaired_minus_denominator"] for row in group_rows if row["target_snapshot"] == "FakeCasablancaV2") >= protocol["minimum_casablanca_mean_repaired_minus_denominator"] and summary["blocks_with_mean_repaired_minus_denominator_at_least_negative_0_03"] >= protocol["minimum_block_count_above_negative_0_03_vs_denominator"] and summary["maximum_within_backend_block_mean_spread"] <= protocol["maximum_block_mean_spread"]),
        condition("A9", "commitment, hidden rows, reveal, and transcript", reveal["commitment_matches"] and reveal["trial_rows_complete_before_reveal"], True, reveal["commitment_matches"] and reveal["trial_rows_complete_before_reveal"]),
        condition("A10", "forbidden claims and credit remain false", 0, 0, not any([summary["causal_repair_claimed"], summary["temporal_transfer_claimed"], summary["real_device_transfer_claimed"], summary["hardware_execution_claimed"], summary["general_route_generation_advantage_claimed"], summary["quantum_advantage_claimed"], summary["bqp_separation_claimed"], summary["solved_frontier_claimed"], summary["new_credit_delta"]])),
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
        {"requirement_id": "P2", "label": "contract, protocol, accepted R152 result, and design hashes verify", "passed": True},
        {"requirement_id": "P3", "label": "three frozen backend groups execute", "passed": len(group_rows) == 3},
        {"requirement_id": "P4", "label": "96 rows partition into twelve independent eight-row blocks with shared arm seeds", "passed": len(trial_rows) == 96 and len(block_rows) == 12 and all(row["row_count"] == 8 for row in block_rows)},
        {"requirement_id": "P5", "label": "commitment matches revealed secret", "passed": reveal["commitment_matches"]},
        {"requirement_id": "P6", "label": "trial rows are complete before reveal", "passed": reveal["trial_rows_complete_before_reveal"]},
        {"requirement_id": "P7", "label": "six compiled route semantic checks pass", "passed": summary["semantic_fidelity_pass_count"] == 6},
        {"requirement_id": "P8", "label": "four phase artifacts replay", "passed": phase_replay == 4},
        {"requirement_id": "P9", "label": "acceptance transcript contains A1-A10", "passed": len(conditions) == 10},
        {"requirement_id": "P10", "label": "R153 performs no candidate selection and claim boundary remains explicit", "passed": summary["r153_candidate_selection_performed"] is False and conditions[-1]["passed"]},
    ]
    payload = {
        "title": "B4/B8 R153 independent seed replication holdout",
        "version": 0,
        "method": METHOD,
        "status": "independent_seed_replication_preregistered_acceptance" if summary["global_acceptance"] else "independent_seed_replication_preregistered_rejection",
        "model_status": "accepted_r152_routes_under_four_independent_hidden_seed_blocks",
        "generated_at_unix": started_at,
        "source_target_id": "T-B4-002bo/T-B8-003bs/T-B10-009bg",
        "upstream_target_id": "T-B4-002bn/T-B8-003br/T-B10-009bf",
        "summary": summary,
        "acceptance_conditions": conditions,
        "compiled_route_rows": compiled_rows,
        "group_rows": group_rows,
        "block_rows": block_rows,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "artifacts": {"contract": CONTRACT_PATH, "challenge_commitment": COMMITMENT_PATH, "three_arm_trial_rows": TRIALS_PATH, "challenge_reveal": REVEAL_PATH, "verifier_transcript": TRANSCRIPT_PATH, "result": RESULT_PATH, "markdown_report": REPORT_PATH},
        "claim_boundary": {"what_is_supported": "one preregistered independent hidden-seed replication verdict for the accepted R152 routes across four blocks per backend", "what_is_not_supported": "causal repair, temporal transfer, real-device transfer, hardware performance, general route-generation advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit"},
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
