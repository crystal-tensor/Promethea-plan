#!/usr/bin/env python3
"""Build the immutable R144 matched live-runtime contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


PROTOCOL_PATH = "results/B4_B8_R144_live_runtime_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R144_live_runtime_contract_v0.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    protocol = json.loads((root / PROTOCOL_PATH).read_text())
    contract = {
        "contract_id": "B4-B8-R144-live-runtime-contract-v0",
        "contract_status": "public_preregistration_measurement_unopened",
        "target_id": "T-B4-002ax/T-B8-003bb/T-B10-009ap",
        "upstream_target_id": protocol["source_target_id"],
        "research_question": "Does the accepted R143 charged-execution reduction produce at least thirty percent measured execution-loop wall-clock savings?",
        "source_bindings": {
            "protocol_path": PROTOCOL_PATH,
            "protocol_sha256": file_sha256(root / PROTOCOL_PATH),
            "protocol_payload_hash": protocol["payload_hash"],
            **protocol["source_bindings"],
        },
        "timing_protocol": protocol["protocol"],
        "acceptance_conditions": [
            {"condition_id": "A1", "condition": "protocol and source bindings remain exact"},
            {"condition_id": "A2", "condition": "full and halving execution counts equal 1,728 and 816"},
            {"condition_id": "A3", "condition": "full strategy reproduces all 12 R142 selections"},
            {"condition_id": "A4", "condition": "halving strategy reproduces all 12 R143 selections"},
            {"condition_id": "A5", "condition": "measured execution-loop runtime reduction is at least 30 percent"},
            {"condition_id": "A6", "condition": "halving/full per-execution runtime ratio lies between 0.5 and 2.0"},
            {"condition_id": "A7", "condition": "strategy order follows the post-preregistration secret"},
            {"condition_id": "A8", "condition": "both strategies use identical circuits, seeds, shots, and backend snapshots"},
            {"condition_id": "A9", "condition": "measurement transcript hashes and deterministic outputs verify"},
            {"condition_id": "A10", "condition": "cross-calibration, hardware, advantage, BQP, solved-frontier, and credit claims remain false"},
        ],
        "phase_protocol": [
            "commit a fresh secret after public preregistration",
            "derive full-first or halving-first strategy order",
            "perform shared untimed setup and warmup",
            "time each strategy once with perf_counter_ns",
            "write measurement rows before secret reveal",
            "reveal secret and verify transcript hashes and deterministic selections",
        ],
        "claim_boundary": {
            "positive_result_requires_all_conditions": True,
            "what_is_not_supported_even_if_accepted": "cross-calibration transfer, real hardware savings, cloud billing savings, protocol soundness, quantum advantage, BQP separation, or solved B4/B8/B10",
        },
    }
    output = root / CONTRACT_PATH
    write_json(output, contract)
    print(file_sha256(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
