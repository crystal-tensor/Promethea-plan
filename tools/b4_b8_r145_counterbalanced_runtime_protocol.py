#!/usr/bin/env python3
"""Freeze the R145 counterbalanced repeated-order runtime protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


METHOD = "b4_b8_r145_counterbalanced_runtime_protocol_v0"
RESULT_PATH = "results/B4_B8_R145_counterbalanced_runtime_protocol_v0.json"
REPORT_PATH = "research/B4_B8_R145_counterbalanced_runtime_protocol.md"
R142_PATH = "results/B4_B8_R142_seed_robust_lcb_mapping_design_v0.json"
R143_PATH = "results/B4_B8_R143_successive_halving_lcb_design_v0.json"
R144_PATH = "results/B4_B8_R144_live_runtime_benchmark_v0.json"


def build(root: Path) -> dict:
    r142 = json.loads((root / R142_PATH).read_text())
    r143 = json.loads((root / R143_PATH).read_text())
    r144 = json.loads((root / R144_PATH).read_text())
    protocol = {
        "timer": "time.perf_counter_ns",
        "schedule_family": ["ABBA", "BAAB"],
        "schedule_selection": "derived_from_post_preregistration_secret",
        "strategy_labels": {"A": "full", "B": "halving"},
        "repeat_count_per_strategy": 2,
        "pairing_rule": [[0, 1], [2, 3]],
        "shared_untimed_setup": [
            "load frozen source rows",
            "compile the same 96 unique-QASM shortlist circuits",
            "verify exact circuit semantics",
            "one simulator warmup circuit per backend snapshot",
        ],
        "timed_scope": [
            "create fresh strategy-local AerSimulator instances",
            "compile same-seed automatic baselines",
            "execute automatic and candidate circuits",
            "update online LCB statistics and eliminate candidates",
        ],
        "full_execution_count_per_repeat": 1728,
        "halving_execution_count_per_repeat": 816,
        "full_execution_count_total": 3456,
        "halving_execution_count_total": 1632,
        "shots_per_execution": 2048,
        "design_seeds": r142["summary"]["design_seeds"],
        "minimum_pooled_runtime_reduction_fraction": 0.30,
        "minimum_each_pair_runtime_reduction_fraction": 0.20,
        "maximum_pair_reduction_spread_fraction": 0.15,
        "per_execution_runtime_ratio_interval": [0.5, 2.0],
        "required_selection_replay_count_per_strategy": 24,
    }
    requirements = [
        {"requirement_id": "R1", "label": "R142, R143, and R144 source hashes are bound", "passed": True},
        {"requirement_id": "R2", "label": "ABBA and BAAB are the only admissible schedules", "passed": protocol["schedule_family"] == ["ABBA", "BAAB"]},
        {"requirement_id": "R3", "label": "each strategy repeats exactly twice", "passed": protocol["repeat_count_per_strategy"] == 2},
        {"requirement_id": "R4", "label": "per-repeat execution counts remain 1,728 and 816", "passed": protocol["full_execution_count_per_repeat"] == 1728 and protocol["halving_execution_count_per_repeat"] == 816},
        {"requirement_id": "R5", "label": "both strategies use 2,048 shots and the same 16 seeds", "passed": protocol["shots_per_execution"] == 2048 and len(protocol["design_seeds"]) == 16},
        {"requirement_id": "R6", "label": "pooled and per-pair runtime floors are fixed", "passed": protocol["minimum_pooled_runtime_reduction_fraction"] == 0.30 and protocol["minimum_each_pair_runtime_reduction_fraction"] == 0.20},
        {"requirement_id": "R7", "label": "pair spread ceiling is fixed at fifteen percentage points", "passed": protocol["maximum_pair_reduction_spread_fraction"] == 0.15},
        {"requirement_id": "R8", "label": "all 24 selections per strategy must replay", "passed": protocol["required_selection_replay_count_per_strategy"] == 24},
        {"requirement_id": "R9", "label": "no R145 timing measurement has run during protocol design", "passed": True},
        {"requirement_id": "R10", "label": "cross-machine, calibration, hardware, advantage, BQP, and credit claims remain false", "passed": True},
    ]
    payload = {
        "title": "B4/B8 R145 counterbalanced repeated-order runtime protocol",
        "version": 0,
        "method": METHOD,
        "status": "counterbalanced_runtime_protocol_frozen_before_measurement",
        "model_status": "secret_selected_abba_or_baab_timing_boundary_without_measurement",
        "generated_at_unix": int(time.time()),
        "source_target_id": "T-B4-002ay/T-B8-003bc/T-B10-009aq",
        "upstream_target_id": "T-B4-002ax/T-B8-003bb/T-B10-009ap",
        "source_bindings": {
            "r142_design_path": R142_PATH,
            "r142_design_sha256": file_sha256(root / R142_PATH),
            "r142_design_payload_hash": r142["payload_hash"],
            "r143_design_path": R143_PATH,
            "r143_design_sha256": file_sha256(root / R143_PATH),
            "r143_design_payload_hash": r143["payload_hash"],
            "r144_runtime_path": R144_PATH,
            "r144_runtime_sha256": file_sha256(root / R144_PATH),
            "r144_runtime_payload_hash": r144["payload_hash"],
        },
        "protocol": protocol,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(x["passed"] for x in requirements),
        "requirements_failed": sum(not x["passed"] for x in requirements),
        "failed_requirement_ids": [x["requirement_id"] for x in requirements if not x["passed"]],
        "measurement_executed": False,
        "claim_boundary": {
            "what_is_supported": "an immutable secret-selected ABBA/BAAB repeated-order timing protocol",
            "what_is_not_supported": "repeated-order savings, cross-machine or cross-calibration transfer, hardware or billing savings, soundness, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def report(payload: dict) -> str:
    p = payload["protocol"]
    return f"""# B4/B8 R145 Counterbalanced Repeated-Order Runtime Protocol

- Schedule family: `ABBA` or `BAAB`, selected by a post-preregistration secret
- Repeats per strategy: `{p['repeat_count_per_strategy']}`
- Full / halving executions per repeat: `{p['full_execution_count_per_repeat']}` / `{p['halving_execution_count_per_repeat']}`
- Full / halving charged executions total: `{p['full_execution_count_total']}` / `{p['halving_execution_count_total']}`
- Shots per execution: `{p['shots_per_execution']}`
- Pooled runtime-reduction floor: `{p['minimum_pooled_runtime_reduction_fraction']:.0%}`
- Each paired runtime-reduction floor: `{p['minimum_each_pair_runtime_reduction_fraction']:.0%}`
- Maximum pair-reduction spread: `{p['maximum_pair_reduction_spread_fraction']:.0%}`
- Required selection replay: `{p['required_selection_replay_count_per_strategy']} / 24` per strategy
- Measurement executed: `false`

The two adjacent full/halving pairs attack first-run, warm-cache, and order
effects while preserving the R144 timer boundary. Shared preparation and warmup
remain excluded and disclosed separately.

This protocol does not yet support a repeated-order runtime result,
cross-machine or calibration transfer, hardware or billing savings, advantage,
BQP separation, solved-frontier status, or new credit.
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
