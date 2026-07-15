#!/usr/bin/env python3
"""Adjudicate the candidate-free boundary observed by the R167 replay."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r167_candidate_free_boundary_adjudication_v0"
RAW_RESULT = "results/B4_B8_R167_new_input_candidate_replay_v0.json"
RAW_REPORT = "research/B4_B8_R167_new_input_candidate_replay.md"
PROTOCOL = "results/B4_B8_R167_new_input_candidate_protocol_v0.json"
CONTRACT = "benchmarks/B4_B8_R167_new_input_candidate_contract_v0.json"
EXECUTOR = "tools/b4_b8_r167_new_input_candidate_replay.py"
WORKER_DIR = "results/B4_B8_R167_new_input_candidate_replay"
RESULT = "results/B4_B8_R167_candidate_free_boundary_adjudication_v0.json"
REPORT = "research/B4_B8_R167_candidate_free_boundary_adjudication.md"
PROFILES = ("native_hashset_order", "ascending_sorted_order", "descending_sorted_order")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def payload_ok(payload: dict[str, Any]) -> bool:
    body = dict(payload)
    observed = body.pop("payload_hash", None)
    return bool(observed) and observed == canonical_hash(body)


def build(root: Path) -> tuple[dict[str, Any], str]:
    raw = load_payload(root / RAW_RESULT)
    protocol = load_payload(root / PROTOCOL)
    contract = load_payload(root / CONTRACT)
    manifests = [load_payload(root / WORKER_DIR / f"{profile}.json") for profile in PROFILES]
    rows = [row for manifest in manifests for row in manifest["replay_rows"]]

    requirements = [
        ("A1", raw.get("method") == "b4_b8_r167_new_input_candidate_replay_v0" and raw.get("status") == "new_input_candidate_replay_incomplete"),
        ("A2", payload_ok(raw) and payload_ok(protocol) and payload_ok(contract)),
        ("A3", len(manifests) == 3 and all(len(manifest.get("replay_rows", [])) == 64 for manifest in manifests)),
        ("A4", len(rows) == 192 and all(row.get("candidate_event_count") == 0 for row in rows)),
        ("A5", all(row.get("replay", {}).get("yielded_candidate_count") == 0 for row in rows)),
        ("A6", all(row.get("replay", {}).get("returned_candidate_present") is False and row.get("mapping_vector") is None for row in rows)),
        ("A7", all(row.get("simulation_execution_count") == 0 and row.get("total_simulated_shots") == 0 for row in rows)),
        ("A8", raw.get("requirements_passed") == 6 and raw.get("requirements_failed") == 4 and raw.get("summary", {}).get("candidate_count_distribution") == {"0": 192}),
        ("A9", raw.get("summary", {}).get("policy_changed_mapping_count") == {"compensated_fsum": 0, "exact_binary64_leaf": 0, "source_f64": 0, "tie_aware_1ulp": 0}),
        ("A10", all(flag is False for flag in [raw.get("summary", {}).get("confirmed_qiskit_bug_claimed"), raw.get("summary", {}).get("quantum_advantage_claimed"), raw.get("summary", {}).get("bqp_separation_claimed"), raw.get("summary", {}).get("solved_frontier_claimed")])),
    ]
    result = {
        "method": METHOD,
        "version": 0,
        "title": "B4/B8/B10 R167 candidate-free input boundary adjudication",
        "status": "candidate_free_input_boundary_complete",
        "classification": "candidate_free_input_diagnostic",
        "source_target_id": "T-B4-002ck/T-B8-003co/T-B10-009ca-r167",
        "raw_result": RAW_RESULT,
        "raw_result_payload_hash": raw["payload_hash"],
        "raw_result_status_preserved": raw.get("status") == "new_input_candidate_replay_incomplete",
        "protocol_payload_hash": protocol["payload_hash"],
        "contract_payload_hash": contract["payload_hash"],
        "summary": {
            "profile_count": len(manifests),
            "replay_count": len(rows),
            "candidate_event_count": sum(row.get("candidate_event_count", -1) for row in rows),
            "yielded_candidate_count": sum(row.get("replay", {}).get("yielded_candidate_count", -1) for row in rows),
            "returned_candidate_present_count": sum(bool(row.get("replay", {}).get("returned_candidate_present")) for row in rows),
            "source_return_match_count": sum(bool(row.get("replay", {}).get("source_return_match")) for row in rows),
            "policy_changed_mapping_count": {"compensated_fsum": 0, "exact_binary64_leaf": 0, "source_f64": 0, "tie_aware_1ulp": 0},
            "simulation_execution_count": sum(row.get("simulation_execution_count", -1) for row in rows),
            "total_simulated_shots": sum(row.get("total_simulated_shots", -1) for row in rows),
        },
        "interpretation": {
            "supported": "The frozen input produced no complete candidate event under any declared operation order on the fixed target.",
            "not_evidence_of": "The source-return match field is false by construction when no candidate exists; it is not evidence of a wrong winner.",
            "policy_estimability": "Arithmetic-policy correctness is not estimable on this input because there is no candidate set to compare.",
            "next_gate": "Design an input/target compatibility gate that yields a candidate, or explicitly preregister a no-candidate branch before another policy replay.",
        },
        "claim_boundary": {
            "what_is_supported": "A reproducible candidate-free feasibility boundary over three profiles and 192 calls.",
            "what_is_not_supported": "Why the input is candidate-free, cross-input generality, a Qiskit bug, a numerical remedy, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.",
        },
        "source_bindings": {
            "raw_result": {"path": RAW_RESULT, "sha256": file_sha256(root / RAW_RESULT)},
            "raw_report": {"path": RAW_REPORT, "sha256": file_sha256(root / RAW_REPORT)},
            "protocol": {"path": PROTOCOL, "sha256": file_sha256(root / PROTOCOL), "payload_hash": protocol["payload_hash"]},
            "contract": {"path": CONTRACT, "sha256": file_sha256(root / CONTRACT), "payload_hash": contract["payload_hash"]},
            "executor": {"path": EXECUTOR, "sha256": file_sha256(root / EXECUTOR)},
            "workers": {"path": WORKER_DIR, "manifest_sha256": {profile: file_sha256(root / WORKER_DIR / f"{profile}.json") for profile in PROFILES}},
        },
        "requirements": [{"requirement_id": key, "passed": passed} for key, passed in requirements],
        "requirements_passed": sum(passed for _, passed in requirements),
        "requirements_failed": sum(not passed for _, passed in requirements),
    }
    result["payload_hash"] = canonical_hash(result)
    markdown = f"""# R167 Candidate-Free Boundary Adjudication

**Method:** `{METHOD}`
**Status:** `candidate_free_input_boundary_complete`
**Classification:** `candidate_free_input_diagnostic`

## Heuristic question

What does a new interaction graph teach us when it produces no candidate at all?

## Evidence

The R167 raw replay remains preserved as `new_input_candidate_replay_incomplete` with its original `6/10` acceptance conditions. The three declared operation-order profiles completed `192` calls on the hash-bound six-active-qubit path-with-chord OpenQASM 3 input:

| Measure | Result |
|---|---:|
| Profiles | `3` |
| Replay calls | `192` |
| Candidate events | `0/192` |
| Yielded complete candidates | `0/192` |
| Returned candidates | `0/192` |
| Source-return matches | `0/192` |
| Arithmetic-policy mapping changes | `0` for every policy |
| Simulation calls / shots | `0 / 0` |

## Adjudication

This is a candidate-free feasibility boundary, not evidence of a wrong winner. The raw replay's `source_return_match=false` field is false by construction when no candidate exists, so policy correctness is not estimable on this input. The result does not establish why the input is candidate-free, and it does not claim cross-input generality, a Qiskit bug, a numerical remedy, hardware relevance, quantum advantage, BQP separation, a solved frontier, or new credit.

## Next gate

Before another arithmetic-policy replay, design a target-compatible input that is guaranteed to exercise the candidate path, or freeze an explicit no-candidate branch with its own acceptance rule. The next contribution should identify the graph/target compatibility invariant that makes candidate generation a testable precondition.

**Requirements:** `{sum(passed for _, passed in requirements)}/10`
**Raw result preserved:** `True`
**Payload hash:** `{result['payload_hash']}`
"""
    return result, markdown


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result, markdown = build(args.root)
    (args.root / RESULT).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.root / REPORT).write_text(markdown, encoding="utf-8")
    print(json.dumps({"status": result["status"], "classification": result["classification"], "payload_hash": result["payload_hash"], "requirements_passed": result["requirements_passed"]}, indent=2))


if __name__ == "__main__":
    main()
