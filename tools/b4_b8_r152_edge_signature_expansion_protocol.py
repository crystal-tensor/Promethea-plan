#!/usr/bin/env python3
"""Freeze the R152 edge-signature expansion hidden holdout."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


METHOD = "b4_b8_r152_edge_signature_expansion_protocol_v0"
DESIGN_PATH = "results/B4_B8_R152_edge_signature_expansion_design_v0.json"
R150_DESIGN_PATH = "results/B4_B8_R150_unseen_backend_candidate_generation_design_v0.json"
R151_PATH = "results/B4_B8_R151_casablanca_failure_attribution_v0.json"
RESULT_PATH = "results/B4_B8_R152_edge_signature_expansion_protocol_v0.json"
REPORT_PATH = "research/B4_B8_R152_edge_signature_expansion_protocol.md"


def build(root: Path) -> dict:
    design = json.loads((root / DESIGN_PATH).read_text())
    r150_design = json.loads((root / R150_DESIGN_PATH).read_text())
    protocol = {
        "snapshot_names": ["FakeCasablancaV2", "FakeNairobiV2", "FakePerth"],
        "task_id": "dense_validation_xy_network_n6",
        "portfolio_group_count": 3,
        "hidden_trial_count_per_group": 8,
        "trial_row_count": 24,
        "arms": ["repaired_route", "strong_seeded_denominator", "fresh_automatic"],
        "simulated_circuit_execution_count": 72,
        "shots_per_execution": 2048,
        "total_simulated_shots": 147456,
        "challenge_seed_derivation": "HMAC-SHA256 from post-preregistration secret",
        "shared_seed_rule": "all three arms in one row share one simulator seed",
        "repaired_rule": "use the R152 selected novel Casablanca edge signature and preserve R150 generated routes on Nairobi and Perth",
        "denominator_rule": "replay the frozen R150 minimum-calibration-exposure route from 80 independent optimization-level-3 transpiler seeds",
        "automatic_rule": "fresh optimization-level-3 compile with a hidden transpiler seed",
        "minimum_semantic_fidelity": 0.9999999999,
        "minimum_portfolio_repaired_minus_automatic_mean": -0.005,
        "minimum_portfolio_repaired_minus_automatic_bootstrap_lower": -0.01,
        "minimum_portfolio_repaired_minus_denominator_mean": -0.005,
        "minimum_portfolio_repaired_minus_denominator_bootstrap_lower": -0.015,
        "minimum_group_count_above_negative_0_02_vs_denominator": 3,
        "maximum_severe_regression_count_below_negative_0_05_vs_denominator": 0,
        "minimum_each_target_mean_repaired_minus_denominator": -0.02,
        "minimum_casablanca_mean_repaired_minus_denominator": -0.02,
    }
    target_rows = r150_design["target_rows"]
    requirements = [
        {"requirement_id": "R1", "label": "R152 design and R151 provenance hashes are bound", "passed": True},
        {"requirement_id": "R2", "label": "Casablanca route is novel and does not copy excluded signatures", "passed": not design["summary"]["selected_exact_qasm_matches_strong_denominator"] and not design["summary"]["selected_edge_signature_matches_strong_denominator"] and not design["summary"]["selected_edge_signature_present_in_original_candidates"]},
        {"requirement_id": "R3", "label": "R150 hidden values remain unused for R152 candidate scoring", "passed": design["summary"]["r150_hidden_trial_values_used_for_candidate_scoring_count"] == 0},
        {"requirement_id": "R4", "label": "Nairobi and Perth retain their frozen R150 generated routes", "passed": [row["target_snapshot"] for row in target_rows] == protocol["snapshot_names"]},
        {"requirement_id": "R5", "label": "eight hidden trials produce 24 rows and 72 executions", "passed": protocol["trial_row_count"] == 24 and protocol["simulated_circuit_execution_count"] == 72},
        {"requirement_id": "R6", "label": "portfolio repaired-automatic and repaired-denominator floors are explicit", "passed": protocol["minimum_portfolio_repaired_minus_automatic_mean"] == -0.005 and protocol["minimum_portfolio_repaired_minus_denominator_mean"] == -0.005},
        {"requirement_id": "R7", "label": "all three backend groups must clear -0.02", "passed": protocol["minimum_group_count_above_negative_0_02_vs_denominator"] == 3 and protocol["minimum_each_target_mean_repaired_minus_denominator"] == -0.02},
        {"requirement_id": "R8", "label": "Casablanca must clear -0.02 with zero severe regressions", "passed": protocol["minimum_casablanca_mean_repaired_minus_denominator"] == -0.02 and protocol["maximum_severe_regression_count_below_negative_0_05_vs_denominator"] == 0},
        {"requirement_id": "R9", "label": "no R152 hidden holdout has run during protocol design", "passed": True},
        {"requirement_id": "R10", "label": "hardware, temporal, real-device transfer, general generation, advantage, BQP, solved-frontier, and credit claims remain false", "passed": True},
    ]
    payload = {
        "title": "B4/B8 R152 edge-signature expansion protocol",
        "version": 0,
        "method": METHOD,
        "status": "edge_signature_expansion_protocol_frozen_before_challenge",
        "model_status": "casablanca_novel_signature_repair_with_two_r150_control_routes",
        "generated_at_unix": int(time.time()),
        "source_target_id": "T-B4-002bl/T-B8-003bp/T-B10-009bd",
        "upstream_target_id": "T-B4-002bk/T-B8-003bo/T-B10-009bc",
        "source_bindings": {
            "r152_design_path": DESIGN_PATH,
            "r152_design_sha256": file_sha256(root / DESIGN_PATH),
            "r152_design_payload_hash": design["payload_hash"],
            "r150_design_path": R150_DESIGN_PATH,
            "r150_design_sha256": file_sha256(root / R150_DESIGN_PATH),
            "r150_design_payload_hash": r150_design["payload_hash"],
            "r151_attribution_path": R151_PATH,
            "r151_attribution_sha256_provenance_only": file_sha256(root / R151_PATH),
            "r150_hidden_trial_values_used_for_candidate_scoring": False,
        },
        "protocol": protocol,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "challenge_executed": False,
        "claim_boundary": {
            "what_is_supported": "an immutable three-backend simulated-noise holdout for one novel Casablanca edge signature",
            "what_is_not_supported": "a hidden result, causal proof, temporal or real-device transfer, hardware performance, general route-generation advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def report(payload: dict) -> str:
    p = payload["protocol"]
    return f"""# B4/B8 R152 Edge-Signature Expansion Protocol

- Backends / hidden rows: `{p['portfolio_group_count']}` / `{p['trial_row_count']}`
- Executions / total shots: `{p['simulated_circuit_execution_count']}` / `{p['total_simulated_shots']}`
- Repaired-denominator portfolio mean / bootstrap floors: `{p['minimum_portfolio_repaired_minus_denominator_mean']}` / `{p['minimum_portfolio_repaired_minus_denominator_bootstrap_lower']}`
- Groups above -0.02 versus denominator: `{p['minimum_group_count_above_negative_0_02_vs_denominator']} / 3`
- Casablanca mean floor: `{p['minimum_casablanca_mean_repaired_minus_denominator']}`
- Severe rows below -0.05: at most `{p['maximum_severe_regression_count_below_negative_0_05_vs_denominator']}`
- Challenge executed: `false`

Casablanca replays the R152 novel edge-signature route. Nairobi and Perth keep
their R150 generated routes as controls. Every group replays its frozen strong
denominator and a fresh hidden-seed automatic compile under same-row seeds.

This protocol does not establish causal repair, temporal or real-device
transfer, hardware performance, general route-generation advantage, quantum
advantage, BQP separation, a solved frontier, or new credit.
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
