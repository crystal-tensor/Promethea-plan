#!/usr/bin/env python3
"""Build the immutable R150 unseen-backend candidate-generation contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256


PROTOCOL_PATH = "results/B4_B8_R150_unseen_backend_candidate_generation_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R150_unseen_backend_candidate_generation_contract_v0.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    protocol = json.loads((root / PROTOCOL_PATH).read_text())
    contract = {
        "contract_id": "B4-B8-R150-unseen-backend-candidate-generation-contract-v0",
        "contract_status": "public_preregistration_challenge_unopened",
        "target_id": "T-B4-002bj/T-B8-003bn/T-B10-009bb",
        "upstream_target_id": protocol["source_target_id"],
        "research_question": "Can the frozen R149 generation recipe remain noninferior to strong seeded denominators on three previously unused seven-qubit fake backends?",
        "source_bindings": {
            "protocol_path": PROTOCOL_PATH,
            "protocol_sha256": file_sha256(root / PROTOCOL_PATH),
            "protocol_payload_hash": protocol["payload_hash"],
            **protocol["source_bindings"],
        },
        "challenge_protocol": protocol["protocol"],
        "acceptance_conditions": [
            {"condition_id": "A1", "condition": "contract, protocol, generated routes, denominators, and all source hashes remain exact"},
            {"condition_id": "A2", "condition": "three groups produce 24 rows and 72 executions with three same-seed arms"},
            {"condition_id": "A3", "condition": "all six frozen routes retain semantic fidelity at least 0.9999999999"},
            {"condition_id": "A4", "condition": "portfolio generated-automatic mean is at least -0.005 and bootstrap lower at least -0.01"},
            {"condition_id": "A5", "condition": "portfolio generated-denominator mean is at least -0.005 and bootstrap lower at least -0.015"},
            {"condition_id": "A6", "condition": "all three backend groups have mean generated-denominator delta at least -0.02"},
            {"condition_id": "A7", "condition": "zero rows have generated-denominator regression below -0.05"},
            {"condition_id": "A8", "condition": "each backend mean is at least -0.02"},
            {"condition_id": "A9", "condition": "challenge commitment, hidden seeds, row hashes, reveal, and transcript replay"},
            {"condition_id": "A10", "condition": "hardware, temporal, real-device transfer, general generation, advantage, BQP, solved-frontier, and credit claims remain false"},
        ],
        "phase_protocol": [
            "commit a fresh secret after public preregistration",
            "derive hidden transpiler, simulator, and bootstrap seeds",
            "replay generated, frozen strong-denominator, and fresh automatic arms",
            "write 24 rows before secret reveal",
            "reveal and verify the acceptance transcript",
        ],
        "claim_boundary": {
            "positive_result_requires_all_conditions": True,
            "what_is_not_supported_even_if_accepted": "temporal transfer, real-device transfer, hardware performance, general route-generation advantage, quantum advantage, BQP separation, or solved B4/B8/B10",
        },
    }
    output = root / CONTRACT_PATH
    write_json(output, contract)
    print(file_sha256(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
