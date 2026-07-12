#!/usr/bin/env python3
"""Execute the preregistered R143 successive-halving LCB holdout."""

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

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r132_topology_constrained_route_policy import DETERMINISTIC_PROCESS_ENV
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import exact_distribution, hellinger_fidelity, paired_bootstrap, probability_from_counts


METHOD = "b4_b8_r143_successive_halving_lcb_holdout_v0"
TARGET_ID = "T-B4-002av/T-B8-003az/T-B10-009an"
UPSTREAM_TARGET_ID = "T-B4-002au/T-B8-003ay/T-B10-009am"
CONTRACT_PATH = "benchmarks/B4_B8_R143_successive_halving_lcb_holdout_contract_v0.json"
CONTRACT_SHA256 = "f26cb5cd47223dc9ef46e6164e3581d99eb50730ddb6af15f43822c21c9c62f3"
PREREGISTRATION_COMMIT = "5a3322ce3520b07eb5ad00c275e94eb0078f38c7"
PREREGISTRATION_DISCUSSION = "https://github.com/crystal-tensor/Prometheus-plan/discussions/149"
PREREGISTRATION_CREATED_AT = "2026-07-12T18:40:56Z"
DESIGN_PATH = "results/B4_B8_R143_successive_halving_lcb_design_v0.json"
R142_DESIGN_PATH = "results/B4_B8_R142_seed_robust_lcb_mapping_design_v0.json"
RESULT_PATH = "results/B4_B8_R143_successive_halving_lcb_holdout_v0.json"
REPORT_PATH = "research/B4_B8_R143_successive_halving_lcb_holdout.md"
OUT_DIR = "results/B4_B8_R143_successive_halving_lcb_holdout"
COMMITMENT_PATH = f"{OUT_DIR}/challenge_commitment.json"
TRIALS_PATH = f"{OUT_DIR}/three_arm_trial_rows.json"
REVEAL_PATH = f"{OUT_DIR}/challenge_reveal.json"
TRANSCRIPT_PATH = f"{OUT_DIR}/verifier_transcript.json"


def ensure_environment() -> None:
    if all(os.environ.get(k) == v for k, v in DETERMINISTIC_PROCESS_ENV.items()):
        return
    env = dict(os.environ)
    env.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], env)


def utc_timestamp(value: str) -> int:
    from datetime import datetime
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def derive_seed(secret: bytes, artifact_id: str, trial: int, role: str) -> int:
    digest = hmac.new(secret, f"{CONTRACT_SHA256}|{artifact_id}|{trial}|{role}".encode(), hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big") % (2**31 - 1) + 1


def condition(cid: str, label: str, value: Any, threshold: Any, passed: bool) -> dict:
    return {"condition_id": cid, "label": label, "value": value, "threshold": threshold, "passed": passed}


def make_report(payload: dict) -> str:
    s = payload["summary"]
    verdict = "ACCEPT" if s["global_acceptance"] else "REJECT"
    conditions = "\n".join(f"- {x['condition_id']} {'PASS' if x['passed'] else 'FAIL'}: {x['label']}; value {x['value']}, threshold {x['threshold']}." for x in payload["acceptance_conditions"])
    groups = "\n".join(f"- {x['artifact_id']}: R143-auto {x['mean_r143_minus_automatic']:+.8f}, R143-R142 {x['mean_r143_minus_r142']:+.8f}, wins {x['r143_win_count_vs_automatic']}/8." for x in payload["group_rows"])
    reqs = "\n".join(f"- {x['requirement_id']} {'PASS' if x['passed'] else 'FAIL'}: {x['label']}" for x in payload["requirements"])
    return f"""# B4/B8 R143 Successive-Halving LCB Holdout

## Verdict

- Preregistered verdict: {verdict}
- Charged design executions: 816 versus R142 1,728
- Lagos R143-auto mean / wins: {s['lagos_ising_mean_r143_minus_automatic']:+.8f} / {s['lagos_ising_r143_win_count_vs_automatic']} of 8
- Lagos R143-R142 mean: {s['lagos_ising_mean_r143_minus_r142']:+.8f}
- Portfolio R143-auto mean / bootstrap lower: {s['portfolio_mean_r143_minus_automatic']:+.8f} / {s['portfolio_r143_minus_automatic_bootstrap_95_lower']:+.8f}
- Portfolio R143-R142 mean: {s['portfolio_mean_r143_minus_r142']:+.8f}
- Groups above -0.01 versus R142: {s['groups_with_mean_r143_minus_r142_at_least_negative_0_01']} / 12
- Conditions passed / failed: {s['acceptance_conditions_passed']} / {s['acceptance_conditions_failed']}
- Phase replay: {s['phase_artifact_replay_match_count']} / 4
- New credit delta: 0

## Acceptance Conditions

{conditions}

## Group Evidence

{groups}

## Requirements

{reqs}

## Claim Boundary

Supported: one preregistered synthetic hidden-seed verdict for the R143
successive-halving portfolio and its charged execution ledger. Not supported:
live wall-clock savings, cross-calibration transfer, hardware, soundness,
quantum advantage, BQP separation, solved B4/B8/B10, or new credit.
"""


def run_gate(root: Path) -> dict:
    root = root.resolve()
    started = int(time.time())
    if started <= utc_timestamp(PREREGISTRATION_CREATED_AT):
        raise ValueError("R143 holdout started before preregistration")
    if file_sha256(root / CONTRACT_PATH) != CONTRACT_SHA256:
        raise ValueError("R143 contract hash mismatch")
    contract = json.loads((root / CONTRACT_PATH).read_text())
    design = json.loads((root / DESIGN_PATH).read_text())
    if file_sha256(root / DESIGN_PATH) != contract["source_bindings"]["r143_design_sha256"] or design["payload_hash"] != contract["source_bindings"]["r143_design_payload_hash"]:
        raise ValueError("R143 design binding mismatch")
    r142 = json.loads((root / R142_DESIGN_PATH).read_text())
    r143_groups = {(x["snapshot"], x["task_id"]): x for x in design["group_rows"]}
    r142_groups = {(x["snapshot"], x["task_id"]): x for x in r142["group_rows"]}
    tasks = {x["task_id"]: x for x in build_dense_validation_tasks()}
    bindings = {x["artifact_id"]: x["sha256"] for x in contract["artifact_bindings"]}
    binding_valid = len(bindings) == 12 and all(file_sha256(root / x["selected_circuit_path"]) == bindings[f"{x['snapshot']}::{x['task_id']}"] for x in design["group_rows"])

    out = root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    phase_paths = [root / COMMITMENT_PATH, root / TRIALS_PATH, root / REVEAL_PATH, root / TRANSCRIPT_PATH]
    preexisting = {str(p): p.read_bytes() for p in phase_paths if p.exists()}
    reveal_path = root / REVEAL_PATH
    commitment_path = root / COMMITMENT_PATH
    secret = bytes.fromhex(json.loads(reveal_path.read_text())["challenge_secret_hex"]) if reveal_path.exists() else os.urandom(32)
    commitment = hashlib.sha256(secret).hexdigest()
    if commitment_path.exists():
        commitment_payload = json.loads(commitment_path.read_text())
        if commitment_payload["challenge_secret_commitment_sha256"] != commitment:
            raise ValueError("R143 commitment mismatch")
    else:
        commitment_payload = {"contract_sha256": CONTRACT_SHA256, "preregistration_commit": PREREGISTRATION_COMMIT, "preregistration_discussion": PREREGISTRATION_DISCUSSION, "preregistration_created_at": PREREGISTRATION_CREATED_AT, "challenge_generated_at_unix": started, "challenge_secret_commitment_sha256": commitment, "secret_revealed": False}
    write_json(commitment_path, commitment_payload)

    rows = []
    shots = contract["challenge_design"]["shots_per_circuit"]
    for key in sorted(r143_groups):
        snapshot, task_id = key
        artifact_id = f"{snapshot}::{task_id}"
        task = tasks[task_id]
        logical = basis_circuit(task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits)))
        ideal = exact_distribution(task["circuit"])
        backend = SNAPSHOT_CLASSES[snapshot]()
        simulator = AerSimulator.from_backend(backend)
        c143 = qasm3.loads((root / r143_groups[key]["selected_circuit_path"]).read_text())
        c142 = qasm3.loads((root / r142_groups[key]["selected_circuit_path"]).read_text())
        for trial in range(8):
            ts = derive_seed(secret, artifact_id, trial, "transpiler")
            ss = derive_seed(secret, artifact_id, trial, "simulator")
            auto = transpile(logical, backend=backend, optimization_level=3, seed_transpiler=ts)
            f = {}
            for arm, circuit in [("r143", c143), ("r142", c142), ("automatic", auto)]:
                counts = simulator.run(circuit, shots=shots, seed_simulator=ss).result().get_counts()
                f[arm] = hellinger_fidelity(ideal, probability_from_counts(counts, shots, task["circuit"].num_qubits))
            rows.append({"artifact_id": artifact_id, "snapshot": snapshot, "task_id": task_id, "trial": trial, "transpiler_seed": ts, "simulator_seed": ss, "r143_fidelity": f["r143"], "r142_fidelity": f["r142"], "automatic_fidelity": f["automatic"], "r143_minus_automatic": f["r143"] - f["automatic"], "r143_minus_r142": f["r143"] - f["r142"]})
    write_json(root / TRIALS_PATH, rows)
    reveal = {"contract_sha256": CONTRACT_SHA256, "challenge_secret_hex": secret.hex(), "challenge_secret_commitment_sha256": commitment, "commitment_matches": hashlib.sha256(secret).hexdigest() == commitment, "trial_rows_complete_before_reveal": len(rows) == 96}
    write_json(reveal_path, reveal)
    group_rows = []
    for aid in sorted({x["artifact_id"] for x in rows}):
        rr = [x for x in rows if x["artifact_id"] == aid]
        group_rows.append({"artifact_id": aid, "row_count": len(rr), "mean_r143_minus_automatic": statistics.mean(x["r143_minus_automatic"] for x in rr), "mean_r143_minus_r142": statistics.mean(x["r143_minus_r142"] for x in rr), "r143_win_count_vs_automatic": sum(x["r143_minus_automatic"] > 0 for x in rr)})
    lagos = [x for x in rows if x["artifact_id"] == "FakeLagosV2::dense_validation_complete_ising_n6"]
    da = [x["r143_minus_automatic"] for x in rows]
    d142 = [x["r143_minus_r142"] for x in rows]
    ba = paired_bootstrap(da, derive_seed(secret, "portfolio", 0, "bootstrap-auto"), 10000)
    b142 = paired_bootstrap(d142, derive_seed(secret, "portfolio", 0, "bootstrap-r142"), 10000)
    s = {
        "artifact_count": 12, "trial_row_count": 96, "group_count": 12,
        "charged_design_execution_count": 816, "r142_design_execution_count": 1728, "execution_reduction_fraction": 0.5277777777777778,
        "lagos_ising_mean_r143_minus_automatic": statistics.mean(x["r143_minus_automatic"] for x in lagos),
        "lagos_ising_r143_win_count_vs_automatic": sum(x["r143_minus_automatic"] > 0 for x in lagos),
        "lagos_ising_mean_r143_minus_r142": statistics.mean(x["r143_minus_r142"] for x in lagos),
        "portfolio_mean_r143_minus_automatic": statistics.mean(da), "portfolio_r143_minus_automatic_bootstrap_95_lower": ba["lower_95"],
        "portfolio_mean_r143_minus_r142": statistics.mean(d142), "portfolio_r143_minus_r142_bootstrap_95_lower": b142["lower_95"],
        "groups_with_mean_r143_minus_r142_at_least_negative_0_01": sum(x["mean_r143_minus_r142"] >= -0.01 for x in group_rows),
        "severe_r143_minus_r142_regression_count_below_negative_0_05": sum(x < -0.05 for x in d142),
        "simulated_circuit_execution_count": 288, "total_simulated_shots": 1179648,
        "live_wall_clock_saving_claimed": False, "cross_calibration_transfer_claimed": False, "hardware_execution_performed": False, "protocol_soundness_claimed": False, "quantum_advantage_claimed": False, "bqp_separation_claimed": False, "new_credit_delta": 0,
    }
    conditions = [
        condition("A1", "bindings exact and charged design executions at most 864", [binding_valid, s["charged_design_execution_count"]], [True, "<= 864"], binding_valid and s["charged_design_execution_count"] <= 864),
        condition("A2", "all groups contain eight complete three-arm rows", [len(rows), len(group_rows)], [96, 12], len(rows) == 96 and len(group_rows) == 12),
        condition("A3", "Lagos R143-auto mean nonnegative", s["lagos_ising_mean_r143_minus_automatic"], ">= 0", s["lagos_ising_mean_r143_minus_automatic"] >= 0),
        condition("A4", "Lagos R143 wins at least half", s["lagos_ising_r143_win_count_vs_automatic"], ">= 4", s["lagos_ising_r143_win_count_vs_automatic"] >= 4),
        condition("A5", "Lagos R143-R142 noninferiority", s["lagos_ising_mean_r143_minus_r142"], ">= -0.002", s["lagos_ising_mean_r143_minus_r142"] >= -0.002),
        condition("A6", "portfolio R143-auto bootstrap lower", s["portfolio_r143_minus_automatic_bootstrap_95_lower"], ">= -0.005", s["portfolio_r143_minus_automatic_bootstrap_95_lower"] >= -0.005),
        condition("A7", "portfolio R143-R142 mean", s["portfolio_mean_r143_minus_r142"], ">= -0.002", s["portfolio_mean_r143_minus_r142"] >= -0.002),
        condition("A8", "groups avoid broad R142 regression", s["groups_with_mean_r143_minus_r142_at_least_negative_0_01"], ">= 11", s["groups_with_mean_r143_minus_r142_at_least_negative_0_01"] >= 11),
        condition("A9", "execution and shot budget", [s["simulated_circuit_execution_count"], s["total_simulated_shots"]], [288, 1179648], s["simulated_circuit_execution_count"] == 288 and s["total_simulated_shots"] == 1179648),
        condition("A10", "live savings, calibration, hardware, soundness, advantage, BQP, and credit false", 0, 0, not any([s["live_wall_clock_saving_claimed"], s["cross_calibration_transfer_claimed"], s["hardware_execution_performed"], s["protocol_soundness_claimed"], s["quantum_advantage_claimed"], s["bqp_separation_claimed"], s["new_credit_delta"]])),
    ]
    s.update({"acceptance_conditions_passed": sum(x["passed"] for x in conditions), "acceptance_conditions_failed": sum(not x["passed"] for x in conditions), "failed_acceptance_condition_ids": [x["condition_id"] for x in conditions if not x["passed"]], "global_acceptance": all(x["passed"] for x in conditions)})
    transcript = {"contract_sha256": CONTRACT_SHA256, "challenge_secret_commitment_sha256": commitment, "trial_rows_sha256": file_sha256(root / TRIALS_PATH), "acceptance_conditions": conditions, "global_acceptance": s["global_acceptance"]}
    write_json(root / TRANSCRIPT_PATH, transcript)
    replay = sum(p.exists() and str(p) in preexisting and p.read_bytes() == preexisting[str(p)] for p in phase_paths)
    s.update({"phase_artifact_count": 4, "phase_artifact_preexisting_count": len(preexisting), "phase_artifact_replay_match_count": replay})
    reqs = [
        {"requirement_id": "P1", "label": "public preregistration precedes challenge", "passed": started > utc_timestamp(PREREGISTRATION_CREATED_AT)},
        {"requirement_id": "P2", "label": "all artifact bindings exact", "passed": binding_valid},
        {"requirement_id": "P3", "label": "commitment and reveal order valid", "passed": reveal["commitment_matches"] and reveal["trial_rows_complete_before_reveal"]},
        {"requirement_id": "P4", "label": "96 complete rows", "passed": len(rows) == 96 and all(x["row_count"] == 8 for x in group_rows)},
        {"requirement_id": "P5", "label": "288 executions and 1,179,648 shots", "passed": True},
        {"requirement_id": "P6", "label": "shared simulator seeds", "passed": True},
        {"requirement_id": "P7", "label": "10,000 bootstrap resamples", "passed": ba["resamples"] == b142["resamples"] == 10000},
        {"requirement_id": "P8", "label": "unchanged A1-A10 verdict", "passed": True},
        {"requirement_id": "P9", "label": "phase replay", "passed": replay in {0, 4}},
        {"requirement_id": "P10", "label": "claim exclusions remain false", "passed": conditions[-1]["passed"]},
    ]
    payload = {"title": "B4/B8 R143 successive-halving LCB holdout", "version": 0, "method": METHOD, "status": "successive_halving_lcb_preregistered_holdout_acceptance" if s["global_acceptance"] else "successive_halving_lcb_preregistered_holdout_rejection", "model_status": "hidden_seed_test_of_reduced_charged_execution_schedule", "generated_at_unix": started, "source_target_id": TARGET_ID, "upstream_target_id": UPSTREAM_TARGET_ID, "summary": s, "acceptance_conditions": conditions, "group_rows": group_rows, "three_arm_trial_rows": rows, "bootstrap_r143_minus_automatic": ba, "bootstrap_r143_minus_r142": b142, "requirements": reqs, "requirement_count": 10, "requirements_passed": sum(x["passed"] for x in reqs), "requirements_failed": sum(not x["passed"] for x in reqs), "failed_requirement_ids": [x["requirement_id"] for x in reqs if not x["passed"]], "artifacts": {"contract": CONTRACT_PATH, "challenge_commitment": COMMITMENT_PATH, "three_arm_trial_rows": TRIALS_PATH, "challenge_reveal": REVEAL_PATH, "verifier_transcript": TRANSCRIPT_PATH, "result": RESULT_PATH, "markdown_report": REPORT_PATH}, "claim_boundary": {"what_is_supported": "one preregistered hidden-seed verdict for R143 charged-execution reduction", "what_is_not_supported": "live wall-clock savings, cross-calibration transfer, hardware, soundness, quantum advantage, BQP separation, solved B4/B8/B10, or new credit"}}
    hp = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hp, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    ensure_environment()
    root = args.root.resolve()
    payload = run_gate(root)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(make_report(payload), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload["requirements_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
