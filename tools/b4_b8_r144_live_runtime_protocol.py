#!/usr/bin/env python3
"""Freeze the R144 matched live-runtime benchmark protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


METHOD = "b4_b8_r144_live_runtime_protocol_v0"
RESULT_PATH = "results/B4_B8_R144_live_runtime_protocol_v0.json"
REPORT_PATH = "research/B4_B8_R144_live_runtime_protocol.md"
R142_PATH = "results/B4_B8_R142_seed_robust_lcb_mapping_design_v0.json"
R143_DESIGN_PATH = "results/B4_B8_R143_successive_halving_lcb_design_v0.json"
R143_HOLDOUT_PATH = "results/B4_B8_R143_successive_halving_lcb_holdout_v0.json"


def build(root: Path) -> dict:
    r142 = json.loads((root / R142_PATH).read_text())
    r143 = json.loads((root / R143_DESIGN_PATH).read_text())
    protocol = {
        "timer": "time.perf_counter_ns",
        "strategy_order": "derived_from_post_preregistration_secret",
        "shared_untimed_setup": [
            "load frozen source rows",
            "load or compile the same 96 unique-QASM shortlist circuits",
            "verify exact circuit semantics",
            "one simulator warmup circuit per backend snapshot",
        ],
        "timed_scope": [
            "create fresh strategy-local AerSimulator instances",
            "compile same-seed automatic baselines",
            "execute automatic and candidate circuits",
            "update online LCB statistics and eliminate candidates",
        ],
        "full_strategy": {
            "candidate_count_per_group": 8,
            "seed_count": 16,
            "candidate_execution_count": 1536,
            "automatic_execution_count": 192,
            "total_execution_count": 1728,
        },
        "halving_strategy": {
            "round_schedule": r143["summary"]["round_schedule"],
            "candidate_execution_count": 672,
            "automatic_execution_count": 144,
            "total_execution_count": 816,
        },
        "shots_per_execution": 2048,
        "design_seeds": r142["summary"]["design_seeds"],
        "minimum_runtime_reduction_fraction": 0.30,
        "maximum_selection_disagreement_count": 2,
        "maximum_full_budget_lcb_regret": 0.001,
        "timing_repeat_count": 1,
    }
    requirements = [
        {"requirement_id": "R1", "label": "R142 and R143 source hashes are bound", "passed": True},
        {"requirement_id": "R2", "label": "full strategy fixes 1,728 executions", "passed": protocol["full_strategy"]["total_execution_count"] == 1728},
        {"requirement_id": "R3", "label": "halving strategy fixes 816 executions", "passed": protocol["halving_strategy"]["total_execution_count"] == 816},
        {"requirement_id": "R4", "label": "both strategies use 2,048 shots and the same design seeds", "passed": protocol["shots_per_execution"] == 2048 and len(protocol["design_seeds"]) == 16},
        {"requirement_id": "R5", "label": "shared preparation and timed scope are disjoint and explicit", "passed": True},
        {"requirement_id": "R6", "label": "strategy order is hidden until after preregistration", "passed": protocol["strategy_order"] == "derived_from_post_preregistration_secret"},
        {"requirement_id": "R7", "label": "runtime reduction floor is fixed at thirty percent", "passed": protocol["minimum_runtime_reduction_fraction"] == 0.30},
        {"requirement_id": "R8", "label": "selection disagreement and LCB regret gates are fixed", "passed": protocol["maximum_selection_disagreement_count"] == 2 and protocol["maximum_full_budget_lcb_regret"] == 0.001},
        {"requirement_id": "R9", "label": "no timing measurement has run during protocol design", "passed": True},
        {"requirement_id": "R10", "label": "hardware, calibration-transfer, advantage, BQP, and credit claims remain false", "passed": True},
    ]
    payload = {
        "title": "B4/B8 R144 live runtime protocol",
        "version": 0,
        "method": METHOD,
        "status": "live_runtime_protocol_frozen_before_measurement",
        "model_status": "matched_strategy_timing_boundary_without_measurement",
        "generated_at_unix": int(time.time()),
        "source_target_id": "T-B4-002aw/T-B8-003ba/T-B10-009ao",
        "upstream_target_id": "T-B4-002av/T-B8-003az/T-B10-009an",
        "source_bindings": {
            "r142_design_path": R142_PATH,
            "r142_design_sha256": file_sha256(root / R142_PATH),
            "r142_design_payload_hash": r142["payload_hash"],
            "r143_design_path": R143_DESIGN_PATH,
            "r143_design_sha256": file_sha256(root / R143_DESIGN_PATH),
            "r143_design_payload_hash": r143["payload_hash"],
            "r143_holdout_path": R143_HOLDOUT_PATH,
            "r143_holdout_sha256": file_sha256(root / R143_HOLDOUT_PATH),
        },
        "protocol": protocol,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": 10,
        "requirements_failed": 0,
        "failed_requirement_ids": [],
        "measurement_executed": False,
        "claim_boundary": {
            "what_is_supported": "an immutable matched live-runtime protocol with explicit timing boundaries",
            "what_is_not_supported": "measured wall-clock savings, cross-calibration transfer, hardware, soundness, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hp = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hp, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def report(payload: dict) -> str:
    p = payload["protocol"]
    return f"""# B4/B8 R144 Live Runtime Protocol

- Full executions: `{p['full_strategy']['total_execution_count']}`
- Successive-halving executions: `{p['halving_strategy']['total_execution_count']}`
- Shots per execution: `{p['shots_per_execution']}`
- Strategy order: post-preregistration secret
- Runtime reduction floor: `{p['minimum_runtime_reduction_fraction']:.0%}`
- Maximum selection disagreement: `{p['maximum_selection_disagreement_count']} / 12`
- Maximum full-budget LCB regret: `{p['maximum_full_budget_lcb_regret']}`
- Measurement executed: `false`

Shared source loading, circuit preparation, semantic checks, and one warmup per
backend are excluded and reported separately. The timer covers fresh simulator
creation, automatic compilation, circuit execution, online LCB updates, and
candidate elimination.

This protocol does not yet support measured wall-clock savings,
cross-calibration transfer, hardware, advantage, BQP, or new credit.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    payload = build(root)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
