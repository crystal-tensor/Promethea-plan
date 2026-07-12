#!/usr/bin/env python3
"""Build the immutable R141 hashed-output-sketch holdout contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


TARGET_ID = "T-B4-002ar/T-B8-003av/T-B10-009aj"
DESIGN_PATH = "results/B4_B8_R141_hashed_output_sketch_design_v0.json"
R140_DESIGN_PATH = "results/B4_B8_R140_output_aware_mapping_design_v0.json"
R140_HOLDOUT_PATH = "results/B4_B8_R140_output_aware_mapping_holdout_v0.json"
R136_PATH = "results/B4_B8_R136_route_realization_margin_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R141_hashed_output_sketch_holdout_contract_v0.json"


def load(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def build_contract(root: Path) -> dict[str, Any]:
    design = load(root, DESIGN_PATH)
    r140_design = load(root, R140_DESIGN_PATH)
    r140_holdout = load(root, R140_HOLDOUT_PATH)
    selected = [
        {
            "artifact_id": f"{row['snapshot']}::{row['task_id']}",
            "path": row["selected_circuit_path"],
            "sha256": row["selected_circuit_sha256"],
        }
        for row in design["group_rows"]
    ]
    candidate_identity_payload = [
        {
            "snapshot": row["snapshot"],
            "task_id": row["task_id"],
            "mapping": row["mapping"],
            "policy_id": row["policy_id"],
            "realization_seed": row["realization_seed"],
            "qasm_hash": row["qasm_hash"],
        }
        for row in design["candidate_rows"]
    ]
    return {
        "contract_id": "B4-B8-R141-hashed-output-sketch-holdout-v0",
        "contract_status": "public_preregistration_execution_unopened",
        "target_id": TARGET_ID,
        "upstream_target_id": design["source_target_id"],
        "research_question": "Can a fixed-width sample sketch preserve the useful mapping decisions of exact output-aware scoring under hidden pilot and noisy seeds?",
        "source_bindings": {
            "r141_design_path": DESIGN_PATH,
            "r141_design_sha256": file_sha256(root / DESIGN_PATH),
            "r141_design_payload_hash": design["payload_hash"],
            "r140_design_path": R140_DESIGN_PATH,
            "r140_design_sha256": file_sha256(root / R140_DESIGN_PATH),
            "r140_design_payload_hash": r140_design["payload_hash"],
            "r140_holdout_path": R140_HOLDOUT_PATH,
            "r140_holdout_sha256": file_sha256(root / R140_HOLDOUT_PATH),
            "r140_holdout_payload_hash": r140_holdout["payload_hash"],
            "r136_result_path": R136_PATH,
            "r136_result_sha256": file_sha256(root / R136_PATH),
            "candidate_identity_sha256": hashlib.sha256(
                json.dumps(
                    candidate_identity_payload,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest(),
        },
        "algorithm_lock": {
            "sketch_bucket_count": 256,
            "hash_multiplier": 173,
            "hash_offset": 97,
            "pilot_sample_count": 4096,
            "readout_replica_count": 8,
            "score_formula": "(1-cx_any_error_proxy)*hashed_hellinger_fidelity",
            "tie_break_order": [
                "hashed_output_sketch_score_desc",
                "hashed_output_sketch_readout_fidelity_desc",
                "cx_any_error_proxy_asc",
                "cx_occurrence_count_asc",
                "policy_id_desc",
                "mapping_lexicographic_desc",
                "realization_seed_asc",
            ],
            "full_distribution_values_visible_to_selector": 0,
        },
        "artifact_bindings": selected,
        "challenge_design": {
            "backend_task_group_count": 12,
            "hidden_pilot_trial_count_per_group": 8,
            "selection_trial_row_count": 96,
            "candidate_count_per_selection": 128,
            "arms": ["sketch", "r140_exact", "r136_old", "automatic"],
            "simulated_circuit_execution_count": 384,
            "shots_per_circuit": 4096,
            "total_simulated_shots": 1572864,
            "shared_simulator_seed_within_four_arm_row": True,
            "hidden_pilot_seed_derived_after_preregistration": True,
            "pilot_source": "statevector_backed_samples_hidden_from_selector",
            "bootstrap_resample_count": 10000,
        },
        "acceptance_conditions": [
            {"condition_id": "A1", "condition": "all design, candidate-pool, and selected-QASM bindings remain exact"},
            {"condition_id": "A2", "condition": "all 96 rows contain a complete sample-only sketch selection and four-arm noisy replay"},
            {"condition_id": "A3", "condition": "Lagos complete-Ising sketch selection matches R140 exact in at least 7 of 8 hidden pilot blocks"},
            {"condition_id": "A4", "condition": "at least 80 of 96 sketch selections match R140 exact selection"},
            {"condition_id": "A5", "condition": "maximum exact R140 score regret is at most 0.005"},
            {"condition_id": "A6", "condition": "portfolio sketch-minus-automatic noisy fidelity bootstrap 95% lower bound is at least -0.005"},
            {"condition_id": "A7", "condition": "Lagos sketch-minus-automatic mean noisy fidelity is nonnegative and wins at least 4 of 8 rows"},
            {"condition_id": "A8", "condition": "portfolio sketch-minus-R140-exact mean noisy fidelity is at least -0.002"},
            {"condition_id": "A9", "condition": "all phase artifacts replay and disclosed work equals 384 executions and 1,572,864 shots"},
            {"condition_id": "A10", "condition": "scalable pilot acquisition, hardware, soundness, advantage, BQP, and new-credit claims remain false"},
        ],
        "phase_protocol": [
            "commit a fresh secret after this contract is public",
            "derive hidden pilot, transpiler, simulator, and bootstrap seeds",
            "write all 96 four-arm rows before revealing the secret",
            "reveal the secret and replay every selection, row, and verdict",
        ],
        "claim_boundary": {
            "positive_result_requires_all_conditions": True,
            "what_is_not_supported_even_if_accepted": "scalable pilot acquisition, current calibration, real hardware, mitigation, independent custody, protocol soundness, quantum advantage, BQP separation, or solved B4/B8/B10",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / CONTRACT_PATH
    write_json(output, build_contract(root))
    print(file_sha256(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
