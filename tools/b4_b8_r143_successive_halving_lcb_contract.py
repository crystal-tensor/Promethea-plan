#!/usr/bin/env python3
"""Build the immutable R143 successive-halving LCB holdout contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


DESIGN_PATH = "results/B4_B8_R143_successive_halving_lcb_design_v0.json"
R142_HOLDOUT_PATH = "results/B4_B8_R142_seed_robust_lcb_mapping_holdout_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R143_successive_halving_lcb_holdout_contract_v0.json"


def load(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def build(root: Path) -> dict:
    design = load(root, DESIGN_PATH)
    r142_holdout = load(root, R142_HOLDOUT_PATH)
    return {
        "contract_id": "B4-B8-R143-successive-halving-lcb-holdout-v0",
        "contract_status": "public_preregistration_execution_unopened",
        "target_id": "T-B4-002av/T-B8-003az/T-B10-009an",
        "upstream_target_id": design["source_target_id"],
        "research_question": "Can an 816-execution successive-halving schedule preserve the accepted R142 hidden-seed performance?",
        "source_bindings": {
            "r143_design_path": DESIGN_PATH,
            "r143_design_sha256": file_sha256(root / DESIGN_PATH),
            "r143_design_payload_hash": design["payload_hash"],
            "r142_holdout_path": R142_HOLDOUT_PATH,
            "r142_holdout_sha256": file_sha256(root / R142_HOLDOUT_PATH),
            "r142_holdout_payload_hash": r142_holdout["payload_hash"],
        },
        "algorithm_lock": {
            "initial_candidate_count": 8,
            "round_schedule": design["summary"]["round_schedule"],
            "charged_execution_count": 816,
            "r142_execution_count": 1728,
            "execution_reduction_fraction": design["summary"]["execution_reduction_fraction"],
            "lcb_z": 1.96,
            "r142_holdout_rows_visible_to_selector": 0,
        },
        "artifact_bindings": [
            {
                "artifact_id": f"{row['snapshot']}::{row['task_id']}",
                "path": row["selected_circuit_path"],
                "sha256": row["selected_circuit_sha256"],
            }
            for row in design["group_rows"]
        ],
        "challenge_design": {
            "backend_task_group_count": 12,
            "hidden_trial_count_per_group": 8,
            "paired_trial_row_count": 96,
            "arms": ["r143_halving", "r142_full", "automatic"],
            "simulated_circuit_execution_count": 288,
            "shots_per_circuit": 4096,
            "total_simulated_shots": 1179648,
            "shared_simulator_seed_within_three_arm_row": True,
            "bootstrap_resample_count": 10000,
        },
        "acceptance_conditions": [
            {"condition_id": "A1", "condition": "all bindings remain exact and charged design executions stay at most 864"},
            {"condition_id": "A2", "condition": "all 96 hidden rows contain complete R143, R142, and automatic arms"},
            {"condition_id": "A3", "condition": "Lagos R143-minus-automatic mean is nonnegative"},
            {"condition_id": "A4", "condition": "Lagos R143 wins at least 4 of 8 rows against automatic"},
            {"condition_id": "A5", "condition": "Lagos R143-minus-R142 mean is at least -0.002"},
            {"condition_id": "A6", "condition": "portfolio R143-minus-automatic bootstrap lower is at least -0.005"},
            {"condition_id": "A7", "condition": "portfolio R143-minus-R142 mean is at least -0.002"},
            {"condition_id": "A8", "condition": "at least 11 of 12 groups have mean R143-minus-R142 at least -0.01"},
            {"condition_id": "A9", "condition": "phase replay and 288 executions / 1,179,648 shots match"},
            {"condition_id": "A10", "condition": "live savings, calibration transfer, hardware, soundness, advantage, BQP, and credit claims remain false"},
        ],
        "phase_protocol": [
            "commit fresh secret after public preregistration",
            "derive hidden transpiler, simulator, and bootstrap seeds",
            "write all three-arm rows before reveal",
            "reveal secret and replay every row and verdict",
        ],
        "claim_boundary": {
            "positive_result_requires_all_conditions": True,
            "what_is_not_supported_even_if_accepted": "live wall-clock savings, cross-calibration transfer, real hardware, mitigation, soundness, quantum advantage, BQP separation, or solved B4/B8/B10",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / CONTRACT_PATH
    write_json(output, build(root))
    print(file_sha256(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
