#!/usr/bin/env python3
"""Freeze the R172 replay and independent-oracle contract before execution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from b4_b8_r154_deterministic_automatic_replay import canonical_hash, target_descriptor
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2


PROTOCOL_PATH = "results/B4_B8_R172_second_near_tie_candidate_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R172_second_near_tie_candidate_contract_v0.json"
INPUT_PATH = "benchmarks/B4_B8_R172_second_near_tie_candidate_v0.qasm"
DESIGN_RESULT_PATH = "results/B4_B8_R172_second_near_tie_design_v0.json"
REPLAY_EXECUTOR_PATH = "tools/b4_b8_r172_second_near_tie_candidate_replay.py"
ORACLE_EXECUTOR_PATH = "tools/b4_b8_r172_independent_second_near_tie_oracle.py"
INSTRUMENTED_BINARY_PATH = "research/source_lineage/Qiskit_2_4_1_R165_candidate_selection_accelerate.cpython-312-darwin.so"
INSTRUMENTED_BINARY_SHA256 = "56101c7bedbaa157c341542d18b95e60b9d37acb9f29d6305fa2f7337cb8fd69"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def payload_binding(root: Path, relative: str) -> dict[str, str]:
    payload = read_json(root, relative)
    body = dict(payload)
    observed = body.pop("payload_hash", None)
    if observed != canonical_hash(body):
        raise ValueError(f"payload mismatch: {relative}")
    return {"path": relative, "sha256": file_sha256(root / relative), "payload_hash": observed}


def file_binding(root: Path, relative: str) -> dict[str, str]:
    return {"path": relative, "sha256": file_sha256(root / relative)}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_protocol(root: Path) -> dict[str, Any]:
    design = read_json(root, DESIGN_RESULT_PATH)
    if design["status"] != "second_near_tie_design_complete":
        raise ValueError("R172 design is not complete")
    summary = design["summary"]
    protocol = {
        "method": "b4_b8_r172_second_near_tie_candidate_protocol_v0",
        "status": "second_near_tie_protocol_frozen_before_execution",
        "title": "B4/B8 R172 nonisomorphic second near-tie replay protocol",
        "version": 0,
        "input_path": INPUT_PATH,
        "input_sha256": file_sha256(root / INPUT_PATH),
        "input_description": "five-active-qubit weighted T-tree with degree sequence (3,2,1,1,1), nonisomorphic to the R170 path, selected by a bounded 625-variant scan",
        "snapshot_name": "FakeNairobiV2",
        "target_descriptor_sha256": target_descriptor(FakeNairobiV2())["descriptor_hash"],
        "qiskit_source_commit": "0fd015a22b84c9082173597a5d2304dc0aaec08c",
        "instrumented_binary_sha256": INSTRUMENTED_BINARY_SHA256,
        "process_environment": ["MKL_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "PYTHONHASHSEED", "QISKIT_PARALLEL", "RAYON_NUM_THREADS"],
        "frozen_software": {"python": "3.12.6", "qiskit": "2.4.1"},
        "vf2_configuration": {"call_limit": 30000000, "max_trials": 250000, "score_initial_layout": True, "shuffle_seed": -1, "strict_direction": False, "time_limit": None},
        "profiles": [
            {"profile_id": "native_hashset_order", "operation_order": "native", "replay_count": 64},
            {"profile_id": "ascending_sorted_order", "operation_order": "ascending", "replay_count": 64},
            {"profile_id": "descending_sorted_order", "operation_order": "descending", "replay_count": 64},
        ],
        "profile_count": 3,
        "total_process_count": 3,
        "total_replay_count": 192,
        "candidate_event_schema": {
            "yielded_candidate": "every complete mapping yielded by the frozen VF2 iterator, retaining index, mapping, source-score bits, leaves, and order",
            "returned_candidate": "the final source mapping and score retained separately for source replay validation",
            "candidate_set_boundary": "only frozen-source iterator candidates are replayed; no alternate traversal is claimed",
        },
        "selection_rule": {
            "enumeration": "preserve observed candidate_index order",
            "incumbent": "first yielded complete candidate",
            "replace": "replace incumbent only when the policy comparison is Less",
            "tie": "retain first-seen incumbent",
            "policies": ["source_f64", "compensated_fsum", "exact_binary64_leaf", "tie_aware_1ulp"],
        },
        "design_preflight": {
            "method": design["method"],
            "result_path": DESIGN_RESULT_PATH,
            "payload_hash": design["payload_hash"],
            "weighted_variants_scanned": summary["weighted_variants_scanned"],
            "one_ulp_variant_count": summary["one_ulp_variant_count"],
            "selected_multiplicities": summary["selected_multiplicities"],
            "candidate_count": summary["selected_candidate_count"],
            "best_two_source_score_gap_ulp_ratio": summary["best_two_source_score_gap_ulp_ratio"],
            "degree_sequence_proves_nonisomorphism": summary["degree_sequence_proves_nonisomorphism"],
        },
        "independent_oracle": {
            "executor_path": ORACLE_EXECUTOR_PATH,
            "imports_qiskit": False,
            "inputs": "committed R172 worker manifests and aggregate result only",
            "checks": "row hashes, retained leaf scores, exact rational sums, four policies, source-return mapping, aggregate split",
        },
        "execution_boundary": {"qiskit_calls_performed": 192, "candidate_selection_performed": True, "route_change_performed": False, "simulation_execution_count": 0, "total_simulated_shots": 0, "sampling_performed": False, "new_hidden_seed_count": 0},
        "claim_boundary": {
            "what_is_supported": "a preregistered candidate replay and independent arithmetic oracle on a graph nonisomorphic to R170",
            "what_is_not_supported": "broad cross-input generality, a numerical remedy, a production mapping change, an alternate search path, a confirmed Qiskit bug, cross-platform determinism, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    protocol["payload_hash"] = canonical_hash(protocol)
    return protocol


def build_contract(root: Path, protocol: dict[str, Any]) -> dict[str, Any]:
    protocol_path = root / PROTOCOL_PATH
    contract = {
        "contract_id": "B4-B8-R172-second-near-tie-candidate-contract-v0",
        "contract_status": "public_preregistration_execution_unopened",
        "execution_started": False,
        "protocol_path": PROTOCOL_PATH,
        "protocol_payload_hash": protocol["payload_hash"],
        "acceptance_conditions": [
            {"condition_id": "A1", "label": "input, design, protocol, replay executor, independent oracle, source manifest, and instrumented binary are hash-bound"},
            {"condition_id": "A2", "label": "R172 graph degree sequence differs from R170 and the bounded scan selects a one-ULP control"},
            {"condition_id": "A3", "label": "three operation-order profiles and 192 post-registration traced calls are present"},
            {"condition_id": "A4", "label": "every complete candidate retains mapping, source score, leaves, and enumeration index"},
            {"condition_id": "A5", "label": "source selection reproduces the returned mapping and score on every call"},
            {"condition_id": "A6", "label": "all four arithmetic policies use first-seen tie handling"},
            {"condition_id": "A7", "label": "the independent standard-library oracle reproduces every row and aggregate selection"},
            {"condition_id": "A8", "label": "zero simulation, shots, sampling, route changes, and hidden seeds are recorded"},
            {"condition_id": "A9", "label": "candidate replay does not claim an alternate search traversal or production policy"},
            {"condition_id": "A10", "label": "forbidden bug, hardware, advantage, BQP, solved-frontier, and credit claims remain false"},
        ],
        "source_bindings": {
            "replay_executor": file_binding(root, REPLAY_EXECUTOR_PATH),
            "independent_oracle": file_binding(root, ORACLE_EXECUTOR_PATH),
            "protocol": {"path": PROTOCOL_PATH, "sha256": file_sha256(protocol_path), "payload_hash": protocol["payload_hash"]},
            "input": file_binding(root, INPUT_PATH),
            "design_executor": file_binding(root, "tools/b4_b8_r172_second_near_tie_design.py"),
            "design_result": payload_binding(root, DESIGN_RESULT_PATH),
            "r171_result": payload_binding(root, "results/B4_B8_R171_independent_near_tie_oracle_v0.json"),
            "r170_result": payload_binding(root, "results/B4_B8_R170_near_tie_candidate_replay_v0.json"),
            "r165_executor": file_binding(root, "tools/b4_b8_r165_candidate_selection_replay.py"),
            "source_manifest": file_binding(root, "research/source_lineage/Qiskit_2_4_1_vf2_source_manifest.json"),
            "instrumented_binary": file_binding(root, INSTRUMENTED_BINARY_PATH),
        },
        "claim_boundary": protocol["claim_boundary"],
    }
    contract["payload_hash"] = canonical_hash(contract)
    return contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    if (root / PROTOCOL_PATH).exists() or (root / CONTRACT_PATH).exists():
        raise ValueError("R172 preregistration already exists; refusing to overwrite")
    if file_sha256(root / INSTRUMENTED_BINARY_PATH) != INSTRUMENTED_BINARY_SHA256:
        raise ValueError("R172 instrumented binary hash mismatch")
    protocol = build_protocol(root)
    write_json(root / PROTOCOL_PATH, protocol)
    contract = build_contract(root, protocol)
    write_json(root / CONTRACT_PATH, contract)
    print(json.dumps({"status": protocol["status"], "protocol_payload_hash": protocol["payload_hash"], "contract_payload_hash": contract["payload_hash"], "execution_started": contract["execution_started"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
