#!/usr/bin/env python3
"""Build the immutable R145 counterbalanced runtime contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


PROTOCOL_PATH = "results/B4_B8_R145_counterbalanced_runtime_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R145_counterbalanced_runtime_contract_v0.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    protocol = json.loads((root / PROTOCOL_PATH).read_text())
    contract = {
        "contract_id": "B4-B8-R145-counterbalanced-runtime-contract-v0",
        "contract_status": "public_preregistration_measurement_unopened",
        "target_id": "T-B4-002az/T-B8-003bd/T-B10-009ar",
        "upstream_target_id": protocol["source_target_id"],
        "research_question": "Does R144 retain at least thirty percent pooled runtime savings after a secret-selected ABBA/BAAB repeated-order challenge?",
        "source_bindings": {
            "protocol_path": PROTOCOL_PATH,
            "protocol_sha256": file_sha256(root / PROTOCOL_PATH),
            "protocol_payload_hash": protocol["payload_hash"],
            **protocol["source_bindings"],
        },
        "timing_protocol": protocol["protocol"],
        "acceptance_conditions": [
            {"condition_id": "A1", "condition": "protocol and source bindings remain exact"},
            {"condition_id": "A2", "condition": "each full and halving repeat records 1,728 and 816 executions"},
            {"condition_id": "A3", "condition": "both full repeats reproduce all 12 R142 selections"},
            {"condition_id": "A4", "condition": "both halving repeats reproduce all 12 R143 selections"},
            {"condition_id": "A5", "condition": "pooled execution-loop runtime reduction is at least 30 percent"},
            {"condition_id": "A6", "condition": "each adjacent full/halving pair has at least 20 percent runtime reduction"},
            {"condition_id": "A7", "condition": "the two paired runtime-reduction fractions differ by at most 15 percentage points"},
            {"condition_id": "A8", "condition": "pooled halving/full per-execution runtime ratio lies between 0.5 and 2.0"},
            {"condition_id": "A9", "condition": "schedule follows the post-preregistration secret and transcript hashes verify"},
            {"condition_id": "A10", "condition": "cross-machine, calibration, hardware, advantage, BQP, solved-frontier, and credit claims remain false"},
        ],
        "phase_protocol": [
            "commit a fresh secret after public preregistration",
            "derive ABBA or BAAB from the secret",
            "perform shared untimed setup and warmup",
            "time four fresh strategy runs in the secret-selected order",
            "write all measurement records before secret reveal",
            "reveal the secret and verify counts, selections, pairing, and hashes",
        ],
        "claim_boundary": {
            "positive_result_requires_all_conditions": True,
            "what_is_not_supported_even_if_accepted": "cross-machine or calibration transfer, real hardware or cloud billing savings, protocol soundness, quantum advantage, BQP separation, or solved B4/B8/B10",
        },
    }
    output = root / CONTRACT_PATH
    write_json(output, contract)
    print(file_sha256(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
