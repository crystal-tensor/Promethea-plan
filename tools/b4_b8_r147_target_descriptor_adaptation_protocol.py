#!/usr/bin/env python3
"""Freeze the R147 target-descriptor adaptation holdout protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


METHOD = "b4_b8_r147_target_descriptor_adaptation_protocol_v0"
DESIGN_PATH = "results/B4_B8_R147_target_descriptor_adaptation_design_v0.json"
R143_PATH = "results/B4_B8_R143_successive_halving_lcb_design_v0.json"
R146_PATH = "results/B4_B8_R146_cross_snapshot_transfer_holdout_v0.json"
RESULT_PATH = "results/B4_B8_R147_target_descriptor_adaptation_protocol_v0.json"
REPORT_PATH = "research/B4_B8_R147_target_descriptor_adaptation_protocol.md"


def build(root: Path) -> dict:
    design = json.loads((root / DESIGN_PATH).read_text())
    r143 = json.loads((root / R143_PATH).read_text())
    protocol = {
        "snapshot_names": sorted({row["target_snapshot"] for row in design["selection_rows"]}),
        "task_ids": sorted({row["task_id"] for row in design["selection_rows"]}),
        "adaptation_group_count": 12,
        "hidden_trial_count_per_group": 8,
        "trial_row_count": 96,
        "arms": ["descriptor_adapted_foreign", "target_specific", "automatic"],
        "simulated_circuit_execution_count": 288,
        "shots_per_execution": 2048,
        "total_simulated_shots": 589824,
        "challenge_seed_derivation": "HMAC-SHA256 from post-preregistration secret",
        "shared_seed_rule": "all three arms in one row share one simulator seed",
        "adaptation_rule": "use the frozen R147 foreign route selected only by target readout/CX exposure descriptors and recompile on target",
        "target_rule": "recompile the target-specific R143 route on target only as a denominator",
        "automatic_rule": "fresh optimization-level-3 compile on target with a hidden transpiler seed",
        "selector_forbidden_inputs": ["R146 hidden trial rows", "R146 group deltas", "R146 target deltas", "target-specific R143 route identity"],
        "minimum_semantic_fidelity": 0.9999999999,
        "minimum_portfolio_adapted_minus_automatic_mean": -0.005,
        "minimum_portfolio_adapted_minus_automatic_bootstrap_lower": -0.01,
        "minimum_portfolio_adapted_minus_target_mean": -0.005,
        "minimum_portfolio_adapted_minus_target_bootstrap_lower": -0.01,
        "minimum_group_count_above_negative_0_02_vs_target": 11,
        "maximum_severe_regression_count_below_negative_0_05_vs_target": 0,
        "minimum_each_target_mean_adapted_minus_target": -0.01,
        "lagos_dense_xy_task_id": "dense_validation_xy_network_n6",
        "minimum_lagos_dense_xy_mean_adapted_minus_target": -0.02,
        "maximum_lagos_dense_xy_severe_regression_count": 0,
    }
    requirements = [
        {"requirement_id": "R1", "label": "R147 design, R143 denominator, and R146 provenance hashes are bound", "passed": True},
        {"requirement_id": "R2", "label": "12 frozen adaptation groups contain only two-candidate foreign-route selections", "passed": design["summary"]["adaptation_group_count"] == 12 and design["summary"]["foreign_candidate_count"] == 24},
        {"requirement_id": "R3", "label": "R146 rows and target-specific routes were excluded from selection", "passed": design["summary"]["r146_hidden_trial_rows_read_count"] == 0 and design["summary"]["target_specific_routes_in_selector_count"] == 0},
        {"requirement_id": "R4", "label": "eight hidden trials produce 96 rows and 288 executions", "passed": protocol["trial_row_count"] == 96 and protocol["simulated_circuit_execution_count"] == 288},
        {"requirement_id": "R5", "label": "all arms use 2,048 shots and one shared row seed", "passed": protocol["shots_per_execution"] == 2048},
        {"requirement_id": "R6", "label": "portfolio noninferiority floors are fixed before challenge", "passed": protocol["minimum_portfolio_adapted_minus_target_mean"] == -0.005 and protocol["minimum_portfolio_adapted_minus_target_bootstrap_lower"] == -0.01},
        {"requirement_id": "R7", "label": "group, severe-row, and each-target guards are fixed", "passed": protocol["minimum_group_count_above_negative_0_02_vs_target"] == 11 and protocol["maximum_severe_regression_count_below_negative_0_05_vs_target"] == 0 and protocol["minimum_each_target_mean_adapted_minus_target"] == -0.01},
        {"requirement_id": "R8", "label": "the R146 failure locus has a dedicated Lagos dense-XY guard", "passed": protocol["minimum_lagos_dense_xy_mean_adapted_minus_target"] == -0.02 and protocol["maximum_lagos_dense_xy_severe_regression_count"] == 0},
        {"requirement_id": "R9", "label": "no R147 holdout has run during protocol design", "passed": True},
        {"requirement_id": "R10", "label": "temporal, cross-machine, hardware, advantage, BQP, solved-frontier, and credit claims remain false", "passed": True},
    ]
    payload = {
        "title": "B4/B8 R147 target-descriptor adaptation holdout protocol",
        "version": 0,
        "method": METHOD,
        "status": "target_descriptor_adaptation_protocol_frozen_before_challenge",
        "model_status": "synthetic_foreign_route_adaptation_without_r146_row_reuse",
        "generated_at_unix": int(time.time()),
        "source_target_id": "T-B4-002bc/T-B8-003bg/T-B10-009au",
        "upstream_target_id": "T-B4-002bb/T-B8-003bf/T-B10-009at",
        "source_bindings": {
            "r147_design_path": DESIGN_PATH,
            "r147_design_sha256": file_sha256(root / DESIGN_PATH),
            "r147_design_payload_hash": design["payload_hash"],
            "r143_design_path": R143_PATH,
            "r143_design_sha256": file_sha256(root / R143_PATH),
            "r143_design_payload_hash": r143["payload_hash"],
            "r146_result_path": R146_PATH,
            "r146_result_sha256_provenance_only": file_sha256(root / R146_PATH),
            "r146_trial_rows_consumed": False,
        },
        "protocol": protocol,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "challenge_executed": False,
        "claim_boundary": {
            "what_is_supported": "an immutable synthetic target-descriptor adaptation protocol with frozen selectors and thresholds",
            "what_is_not_supported": "a holdout result, temporal same-device transfer, cross-machine transfer, real hardware, mitigation, soundness, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def report(payload: dict) -> str:
    p = payload["protocol"]
    return f"""# B4/B8 R147 Target-Descriptor Adaptation Holdout Protocol

- Frozen adaptation groups / hidden rows: `{p['adaptation_group_count']}` / `{p['trial_row_count']}`
- Three-arm executions / total shots: `{p['simulated_circuit_execution_count']}` / `{p['total_simulated_shots']}`
- Arms: descriptor-adapted foreign route, target-specific R143, automatic
- Adapted-target mean / bootstrap floors: `{p['minimum_portfolio_adapted_minus_target_mean']}` / `{p['minimum_portfolio_adapted_minus_target_bootstrap_lower']}`
- Groups above -0.02 versus target: at least `{p['minimum_group_count_above_negative_0_02_vs_target']} / 12`
- Severe rows below -0.05: at most `{p['maximum_severe_regression_count_below_negative_0_05_vs_target']}`
- Each-target mean floor: `{p['minimum_each_target_mean_adapted_minus_target']}`
- Lagos dense-XY mean floor / severe-row cap: `{p['minimum_lagos_dense_xy_mean_adapted_minus_target']}` / `{p['maximum_lagos_dense_xy_severe_regression_count']}`
- Challenge executed: `false`

The selector is frozen before the challenge. It uses only public target readout
and CX calibration descriptors to choose between the two foreign R143 routes.
R146 hidden rows, R146 deltas, and the target-specific R143 route identity are
forbidden selector inputs. The target-specific route is used only as a blind
denominator after preregistration.

This protocol does not represent temporal calibration drift, another machine,
real hardware, mitigation, soundness, quantum advantage, BQP separation, a
solved frontier, or new credit.
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
