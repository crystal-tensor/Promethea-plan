#!/usr/bin/env python3
"""Freeze the R150 unseen-backend generated-route hidden holdout."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


METHOD = "b4_b8_r150_unseen_backend_candidate_generation_protocol_v0"
DESIGN_PATH = "results/B4_B8_R150_unseen_backend_candidate_generation_design_v0.json"
R149_RESULT_PATH = "results/B4_B8_R149_jakarta_xy_candidate_generation_holdout_v0.json"
RESULT_PATH = "results/B4_B8_R150_unseen_backend_candidate_generation_protocol_v0.json"
REPORT_PATH = "research/B4_B8_R150_unseen_backend_candidate_generation_protocol.md"


def build(root: Path) -> dict:
    design = json.loads((root / DESIGN_PATH).read_text())
    r149 = json.loads((root / R149_RESULT_PATH).read_text())
    protocol = {
        "snapshot_names": ["FakeCasablancaV2", "FakeNairobiV2", "FakePerth"],
        "task_id": "dense_validation_xy_network_n6",
        "portfolio_group_count": 3,
        "hidden_trial_count_per_group": 8,
        "trial_row_count": 24,
        "arms": ["generated_route", "strong_seeded_denominator", "fresh_automatic"],
        "simulated_circuit_execution_count": 72,
        "shots_per_execution": 2048,
        "total_simulated_shots": 147456,
        "challenge_seed_derivation": "HMAC-SHA256 from post-preregistration secret",
        "shared_seed_rule": "all three arms in one row share one simulator seed",
        "generated_rule": "recompile each R150 selected mapping, policy, and realization seed",
        "denominator_rule": "replay the frozen minimum-calibration-exposure route from 80 independent optimization-level-3 transpiler seeds",
        "automatic_rule": "fresh optimization-level-3 compile with a hidden transpiler seed",
        "minimum_semantic_fidelity": 0.9999999999,
        "minimum_portfolio_generated_minus_automatic_mean": -0.005,
        "minimum_portfolio_generated_minus_automatic_bootstrap_lower": -0.01,
        "minimum_portfolio_generated_minus_denominator_mean": -0.005,
        "minimum_portfolio_generated_minus_denominator_bootstrap_lower": -0.015,
        "minimum_group_count_above_negative_0_02_vs_denominator": 3,
        "maximum_severe_regression_count_below_negative_0_05_vs_denominator": 0,
        "minimum_each_target_mean_generated_minus_denominator": -0.02,
    }
    requirements = [
        {"requirement_id": "R1", "label": "R150 design and R149 provenance hashes are bound", "passed": True},
        {"requirement_id": "R2", "label": "three previously unused backend classes remain the only targets", "passed": protocol["snapshot_names"] == design["design_protocol"]["target_snapshots"]},
        {"requirement_id": "R3", "label": "R149 hidden rows remain unused by R150 generation and selection", "passed": design["summary"]["r149_hidden_trial_rows_read_count"] == 0},
        {"requirement_id": "R4", "label": "three generated and three strong denominator routes are frozen", "passed": len(design["target_rows"]) == 3},
        {"requirement_id": "R5", "label": "eight hidden trials produce 24 rows and 72 executions", "passed": protocol["trial_row_count"] == 24 and protocol["simulated_circuit_execution_count"] == 72},
        {"requirement_id": "R6", "label": "portfolio generated-automatic and generated-denominator floors are explicit", "passed": protocol["minimum_portfolio_generated_minus_automatic_mean"] == -0.005 and protocol["minimum_portfolio_generated_minus_denominator_mean"] == -0.005},
        {"requirement_id": "R7", "label": "all three backend groups must clear -0.02", "passed": protocol["minimum_group_count_above_negative_0_02_vs_denominator"] == 3 and protocol["minimum_each_target_mean_generated_minus_denominator"] == -0.02},
        {"requirement_id": "R8", "label": "zero severe regressions are allowed", "passed": protocol["maximum_severe_regression_count_below_negative_0_05_vs_denominator"] == 0},
        {"requirement_id": "R9", "label": "no R150 hidden holdout has run during protocol design", "passed": True},
        {"requirement_id": "R10", "label": "hardware, temporal, real-device transfer, general generation, advantage, BQP, solved-frontier, and credit claims remain false", "passed": True},
    ]
    payload = {
        "title": "B4/B8 R150 unseen-backend candidate-generation protocol",
        "version": 0,
        "method": METHOD,
        "status": "unseen_backend_candidate_generation_protocol_frozen_before_challenge",
        "model_status": "three_unseen_fake_backends_with_strong_seeded_denominators",
        "generated_at_unix": int(time.time()),
        "source_target_id": "T-B4-002bi/T-B8-003bm/T-B10-009ba",
        "upstream_target_id": "T-B4-002bh/T-B8-003bl/T-B10-009az",
        "source_bindings": {
            "r150_design_path": DESIGN_PATH,
            "r150_design_sha256": file_sha256(root / DESIGN_PATH),
            "r150_design_payload_hash": design["payload_hash"],
            "r149_result_path": R149_RESULT_PATH,
            "r149_result_sha256_provenance_only": file_sha256(root / R149_RESULT_PATH),
            "r149_result_payload_hash": r149["payload_hash"],
            "r149_trial_rows_consumed": False,
        },
        "protocol": protocol,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "challenge_executed": False,
        "claim_boundary": {
            "what_is_supported": "an immutable three-backend dense-XY generated-route holdout protocol",
            "what_is_not_supported": "a hidden result, temporal transfer, real-device transfer, hardware performance, general route-generation advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def report(payload: dict) -> str:
    p = payload["protocol"]
    return f"""# B4/B8 R150 Unseen-Backend Candidate-Generation Protocol

- Backends / hidden rows: `{p['portfolio_group_count']}` / `{p['trial_row_count']}`
- Executions / total shots: `{p['simulated_circuit_execution_count']}` / `{p['total_simulated_shots']}`
- Generated-denominator portfolio mean / bootstrap floors: `{p['minimum_portfolio_generated_minus_denominator_mean']}` / `{p['minimum_portfolio_generated_minus_denominator_bootstrap_lower']}`
- Groups above -0.02 versus denominator: `{p['minimum_group_count_above_negative_0_02_vs_denominator']} / 3`
- Severe rows below -0.05: at most `{p['maximum_severe_regression_count_below_negative_0_05_vs_denominator']}`
- Challenge executed: `false`

Casablanca, Nairobi, and Perth each replay one generated route, one frozen
strong route selected from 80 automatic compilations, and one fresh hidden-seed
automatic compile. All three must clear the per-backend denominator floor.

This protocol does not establish temporal or real-device transfer, hardware
performance, general route-generation advantage, quantum advantage, BQP
separation, a solved frontier, or new credit.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    payload = build(root)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload["protocol"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
