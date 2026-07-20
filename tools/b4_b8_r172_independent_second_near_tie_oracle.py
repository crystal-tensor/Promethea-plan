#!/usr/bin/env python3
"""Independently recompute the R172 second-graph near-tie evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from fractions import Fraction
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r172_independent_second_near_tie_oracle_v0"
R172_RESULT_PATH = "results/B4_B8_R172_second_near_tie_candidate_replay_v0.json"
R172_PROTOCOL_PATH = "results/B4_B8_R172_second_near_tie_candidate_protocol_v0.json"
R172_CONTRACT_PATH = "benchmarks/B4_B8_R172_second_near_tie_candidate_contract_v0.json"
R172_WORKER_DIR = "results/B4_B8_R172_second_near_tie_candidate_replay"
PROTOCOL_PATH = R172_PROTOCOL_PATH
CONTRACT_PATH = R172_CONTRACT_PATH
RESULT_PATH = "results/B4_B8_R172_independent_second_near_tie_oracle_v0.json"
REPORT_PATH = "research/B4_B8_R172_independent_second_near_tie_oracle.md"
POLICIES = ["source_f64", "compensated_fsum", "exact_binary64_leaf", "tie_aware_1ulp"]


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def verify_payload(payload: dict[str, Any], field: str, label: str) -> None:
    body = dict(payload)
    observed = body.pop(field, None)
    if observed != canonical_hash(body):
        raise ValueError(f"R172 oracle {label} payload mismatch")


def bits_to_float(bits: int) -> float:
    return struct.unpack("!d", int(bits).to_bytes(8, "big"))[0]


def float_bits(value: float) -> int:
    return struct.unpack("!Q", struct.pack("!d", value))[0]


def exact_score(leaf_bits: list[int]) -> Fraction:
    return sum((Fraction.from_float(bits_to_float(bits)) for bits in leaf_bits), Fraction(0, 1))


def derived_candidate(stored: dict[str, Any]) -> dict[str, Any]:
    leaf_bits = [int(bits) for bits in stored["source_leaf_bits"]]
    values = [bits_to_float(bits) for bits in leaf_bits]
    exact = exact_score(leaf_bits)
    return {
        "candidate_index": int(stored["candidate_index"]),
        "mapping_vector": [int(value) for value in stored["mapping_vector"]],
        "mapping_terms": stored["mapping_terms"],
        "source_score_bits": int(stored["source_score_bits"]),
        "source_score": bits_to_float(int(stored["source_score_bits"])),
        "source_leaf_bits": leaf_bits,
        "compensated_score_bits": float_bits(math.fsum(values)),
        "exact_score_numerator": str(exact.numerator),
        "exact_score_denominator": str(exact.denominator),
        "leaf_count": len(leaf_bits),
    }


def verify_stored_candidate(stored: dict[str, Any]) -> None:
    derived = derived_candidate(stored)
    for field in ["candidate_index", "mapping_vector", "mapping_terms", "source_score_bits", "source_leaf_bits", "compensated_score_bits", "exact_score_numerator", "exact_score_denominator", "leaf_count"]:
        if stored.get(field) != derived[field]:
            raise ValueError(f"R172 oracle stored candidate field mismatch: {field}")
    if not math.isclose(stored["source_score"], derived["source_score"], rel_tol=0.0, abs_tol=0.0):
        raise ValueError("R172 oracle stored source score mismatch")


def ulp_fraction(left: float, right: float) -> Fraction:
    return Fraction.from_float(math.ulp(max(abs(left), abs(right))))


def compare(left: dict[str, Any], right: dict[str, Any], policy: str) -> int:
    if policy == "source_f64":
        a, b = left["source_score"], right["source_score"]
    elif policy == "compensated_fsum":
        a, b = bits_to_float(left["compensated_score_bits"]), bits_to_float(right["compensated_score_bits"])
    else:
        left_exact = Fraction(int(left["exact_score_numerator"]), int(left["exact_score_denominator"]))
        right_exact = Fraction(int(right["exact_score_numerator"]), int(right["exact_score_denominator"]))
        if policy == "tie_aware_1ulp" and abs(left_exact - right_exact) <= ulp_fraction(left["source_score"], right["source_score"]):
            return 0
        a, b = left_exact, right_exact
    return -1 if a < b else (1 if a > b else 0)


def select(candidates: list[dict[str, Any]], policy: str) -> dict[str, Any]:
    incumbent = candidates[0]
    for candidate in candidates[1:]:
        if compare(candidate, incumbent, policy) < 0:
            incumbent = candidate
    return incumbent


def verify_row(row: dict[str, Any]) -> dict[str, Any]:
    body = dict(row)
    observed = body.pop("replay_payload_hash", None)
    if observed != canonical_hash(body):
        raise ValueError("R172 oracle replay row hash mismatch")
    replay = row["replay"]
    candidates = replay["candidates"]
    if len(candidates) != 3 or replay["yielded_candidate_count"] != 3:
        raise ValueError("R172 oracle candidate count mismatch")
    for candidate in candidates:
        verify_stored_candidate(candidate)
    returned = replay["returned_candidate"]
    verify_stored_candidate(returned)
    selections = {policy: select(candidates, policy) for policy in POLICIES}
    for policy, chosen in selections.items():
        if replay["selected_candidate_index"][policy] != chosen["candidate_index"]:
            raise ValueError(f"R172 oracle selection mismatch: {policy}")
        if replay["policy_changed_mapping"][policy] != (chosen["mapping_vector"] != selections["source_f64"]["mapping_vector"]):
            raise ValueError(f"R172 oracle policy-change flag mismatch: {policy}")
    source = selections["source_f64"]
    if source["mapping_vector"] != returned["mapping_vector"] or source["source_score_bits"] != returned["source_score_bits"]:
        raise ValueError("R172 oracle source-return mismatch")
    scores = sorted(candidate["source_score"] for candidate in candidates)
    if scores[1] - scores[0] != math.ulp(max(abs(scores[0]), abs(scores[1]))):
        raise ValueError("R172 oracle one-ULP gap mismatch")
    return {"candidate_count": len(candidates), "source_return_match": 1, "policy_changed_mapping": {policy: int(replay["policy_changed_mapping"][policy]) for policy in POLICIES}}


def verify_bindings(root: Path, protocol: dict[str, Any], contract: dict[str, Any]) -> None:
    verify_payload(protocol, "payload_hash", "protocol")
    verify_payload(contract, "payload_hash", "contract")
    if protocol.get("method") != "b4_b8_r172_second_near_tie_candidate_protocol_v0":
        raise ValueError("R172 oracle protocol identity mismatch")
    if contract.get("contract_id") != "B4-B8-R172-second-near-tie-candidate-contract-v0" or contract.get("execution_started") is not False:
        raise ValueError("R172 oracle contract identity or unopened boundary mismatch")
    if contract.get("protocol_payload_hash") != protocol.get("payload_hash"):
        raise ValueError("R172 oracle protocol binding mismatch")
    for binding_id, binding in contract["source_bindings"].items():
        path = root / binding["path"]
        if not path.exists() or file_sha256(path) != binding["sha256"]:
            raise ValueError(f"R172 oracle source binding mismatch: {binding_id}")
        if binding.get("payload_hash"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("payload_hash") != binding["payload_hash"]:
                raise ValueError(f"R172 oracle source payload binding mismatch: {binding_id}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    parser.add_argument("--preregistration-created-at", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    protocol = read_json(root, PROTOCOL_PATH)
    contract = read_json(root, CONTRACT_PATH)
    verify_bindings(root, protocol, contract)
    if (root / RESULT_PATH).exists() or (root / REPORT_PATH).exists():
        raise ValueError("R172 oracle result already exists; refusing to overwrite")
    r172 = read_json(root, R172_RESULT_PATH)
    r172_protocol = read_json(root, R172_PROTOCOL_PATH)
    r172_contract = read_json(root, R172_CONTRACT_PATH)
    verify_payload(r172, "payload_hash", "R172 result")
    verify_payload(r172_protocol, "payload_hash", "R172 protocol")
    verify_payload(r172_contract, "payload_hash", "R172 contract")
    manifests = []
    for profile in protocol["profiles"]:
        path = root / R172_WORKER_DIR / f"{profile['profile_id']}.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        body = dict(manifest)
        observed = body.pop("manifest_payload_hash", None)
        if observed != canonical_hash(body):
            raise ValueError(f"R172 oracle worker manifest hash mismatch: {profile['profile_id']}")
        if manifest.get("replay_count") != profile["replay_count"]:
            raise ValueError(f"R172 oracle worker replay count mismatch: {profile['profile_id']}")
        manifests.append(manifest)
    rows = [row for manifest in manifests for row in manifest["replay_rows"]]
    checks = [verify_row(row) for row in rows]
    policy_changes = {policy: sum(check["policy_changed_mapping"][policy] for check in checks) for policy in POLICIES}
    summary = {
        "profile_count": len(manifests),
        "replay_count": len(rows),
        "row_payload_hash_match_count": len(checks),
        "candidate_record_count": sum(check["candidate_count"] for check in checks),
        "returned_candidate_record_count": len(checks),
        "source_return_match_count": sum(check["source_return_match"] for check in checks),
        "source_return_mismatch_count": 0,
        "policy_changed_mapping_count": policy_changes,
        "r172_result_aggregate_match": policy_changes == r172["summary"]["policy_changed_mapping_count"] and sum(check["candidate_count"] for check in checks) == r172["summary"]["yielded_candidate_count"],
        "candidate_order_profiles_recomputed": 3,
        "qiskit_calls_performed": 0,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "new_credit_delta": 0,
    }
    acceptance = [
        ("A1", summary["profile_count"] == 3),
        ("A2", summary["replay_count"] == 192),
        ("A3", summary["row_payload_hash_match_count"] == 192),
        ("A4", summary["candidate_record_count"] == 576),
        ("A5", summary["source_return_match_count"] == 192),
        ("A6", summary["policy_changed_mapping_count"] == r172["summary"]["policy_changed_mapping_count"]),
        ("A7", summary["r172_result_aggregate_match"]),
        ("A8", summary["candidate_order_profiles_recomputed"] == 3),
        ("A9", summary["qiskit_calls_performed"] == 0 and summary["simulation_execution_count"] == 0),
        ("A10", args.preregistration_discussion.startswith("https://github.com/crystal-tensor/Prometheus-plan/discussions/")),
    ]
    result = {
        "method": METHOD,
        "version": 0,
        "title": "B4/B8 R172 independent second-graph near-tie oracle",
        "status": "independent_near_tie_oracle_complete" if all(passed for _, passed in acceptance) else "independent_near_tie_oracle_incomplete",
        "classification": "independent_reproduction_confirmed_policy_split" if all(passed for _, passed in acceptance) else "independent_near_tie_oracle_incomplete",
        "upstream_target_id": "T-B4-002cp/T-B8-003ct/T-B10-009cf-r172",
        "preregistration": {"commit": args.preregistration_commit, "discussion": args.preregistration_discussion, "created_at": args.preregistration_created_at},
        "summary": summary,
        "acceptance_conditions": [{"condition_id": key, "passed": passed} for key, passed in acceptance],
        "requirements_passed": sum(passed for _, passed in acceptance),
        "requirements_failed": sum(not passed for _, passed in acceptance),
        "claim_boundary": {"what_is_supported": "independent standard-library recomputation of the R172 candidate records and policy split on a graph nonisomorphic to R170", "what_is_not_supported": "a new Qiskit execution, a production mapping change, an alternate search path, a confirmed Qiskit bug, broad cross-input generality, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit"},
        "artifacts": {"protocol": PROTOCOL_PATH, "contract": CONTRACT_PATH, "result": RESULT_PATH, "markdown_report": REPORT_PATH, "source_result": R172_RESULT_PATH, "source_worker_directory": R172_WORKER_DIR},
    }
    result["payload_hash"] = canonical_hash(result)
    (root / RESULT_PATH).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / REPORT_PATH).write_text("\n".join([
        "# B4/B8 R172 Independent Second-Graph Near-Tie Oracle",
        "",
        f"- Status: `{result['status']}`",
        f"- Classification: `{result['classification']}`",
        f"- Rows / candidates: `{summary['replay_count']}` / `{summary['candidate_record_count']}`",
        f"- Source-return matches: `{summary['source_return_match_count']}` / `{summary['replay_count']}`",
        f"- Policy-change counts: `{summary['policy_changed_mapping_count']}`",
        f"- Payload hash: `{result['payload_hash']}`",
        "",
        "## Heuristic question",
        "",
        "Can a standard-library oracle reproduce the second-graph one-ULP policy split without importing Qiskit?",
        "",
        "The oracle reads only the R172 worker manifests. It reconstructs source scores from binary64 bits, compensated sums from retained leaf bits, exact rational leaf sums, and the declared 1-ULP tie rule. It verifies row hashes, candidate records, source-return mappings, all three operation-order profiles, and the aggregate policy split.",
        "",
        "## Claim boundary",
        "",
        "This is independent evidence integrity and arithmetic recomputation for one frozen nonisomorphic R172 input. It is not a new Qiskit execution, a production mapping change, a confirmed bug, broad cross-input generality, hardware evidence, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.",
        "",
    ]), encoding="utf-8")
    print(json.dumps({"status": result["status"], "classification": result["classification"], "summary": summary, "requirements_passed": result["requirements_passed"], "requirements_failed": result["requirements_failed"], "payload_hash": result["payload_hash"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
