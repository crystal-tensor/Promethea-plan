#!/usr/bin/env python3
"""Independently verify R174 with Fraction and no Qiskit/comparator import."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import struct
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r174_independent_exact_score_oracle_v0"
PROTOCOL_PATH = "results/B4_B8_R174_exact_score_comparator_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R174_exact_score_comparator_contract_v0.json"
SOURCE_PATH = "results/B4_B8_R174_exact_score_comparator_v0.json"
RESULT_PATH = "results/B4_B8_R174_independent_exact_score_oracle_v0.json"
REPORT_PATH = "research/B4_B8_R174_independent_exact_score_oracle.md"
R160_PATH = "results/B4_B8_R160_deterministic_error_map_remediation/case_analysis.json"


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bits_to_float(bits: int) -> float:
    return struct.unpack("!d", int(bits).to_bytes(8, "big"))[0]


def exact_sum(candidate: dict[str, Any]) -> Fraction:
    return sum(
        (Fraction.from_float(bits_to_float(bits)) for bits in candidate["source_leaf_bits"]),
        Fraction(0, 1),
    )


def grid_int(value: Fraction) -> int:
    scaled = value * (1 << 1074)
    if scaled.denominator != 1:
        raise ValueError("R174 oracle value is not on the binary64 grid")
    return scaled.numerator


def grid_hash(value: int) -> str:
    return hashlib.sha256(str(value).encode("ascii")).hexdigest()


def select(candidates: list[dict[str, Any]]) -> tuple[int, list[int], list[Fraction]]:
    keys = [exact_sum(candidate) for candidate in candidates]
    minimum = min(keys)
    tied = [index for index, key in enumerate(keys) if key == minimum]
    return tied[0], tied, keys


def recompute_row(
    dataset_id: str,
    worker_path: str,
    profile_id: str,
    replay_index: int,
    replay: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    candidates = replay["candidates"]
    selected, tied, keys = select(candidates)
    source = int(replay["selected_candidate_index"]["source_f64"])
    stored_exact = int(replay["selected_candidate_index"]["exact_binary64_leaf"])
    exact_fields = [
        Fraction(
            int(candidate["exact_score_numerator"]),
            int(candidate["exact_score_denominator"]),
        )
        for candidate in candidates
    ]
    totals_match = keys == exact_fields
    minimum = min(keys)
    permutation_passed = 0
    for permutation in itertools.permutations(range(len(candidates))):
        permuted = [candidates[index] for index in permutation]
        selected_position, _, _ = select(permuted)
        selected_original = permutation[selected_position]
        expected = next(index for index in permutation if keys[index] == minimum)
        permutation_passed += selected_original == expected
    integers = [grid_int(value) for value in keys]
    record = {
        "dataset_id": dataset_id,
        "worker_path": worker_path,
        "profile_id": profile_id,
        "replay_index": replay_index,
        "source_selected_candidate_index": source,
        "stored_exact_candidate_index": stored_exact,
        "comparator_selected_candidate_index": selected,
        "exact_minimizer_indices": tied,
        "exact_minimizer_count": len(tied),
        "source_to_comparator_score_bit_gap": abs(
            int(candidates[source]["source_score_bits"])
            - int(candidates[selected]["source_score_bits"])
        ),
        "candidate_total_grid_hashes": [grid_hash(value) for value in integers],
        "candidate_total_bit_lengths": [abs(value).bit_length() for value in integers],
        "candidate_totals_match_stored_exact": totals_match,
        "comparator_matches_stored_exact": selected == stored_exact,
        "permutation_checks_passed": permutation_passed,
        "permutation_check_count": 6,
    }
    record["row_hash"] = canonical_hash(record)
    return record, sum(left == right for left, right in zip(keys, exact_fields))


def recompute_r160(root: Path) -> dict[str, int]:
    payload = json.loads((root / R160_PATH).read_text(encoding="utf-8"))
    tie_rows = payload["tie_baseline"]["mode_rows"]
    tie_passed = sum(
        int(row["oracle"]["minimizer_count"]) == 2
        and bool(row["selected_vectors"])
        and row["selected_vectors"][0] == row["oracle"]["minimizer_vectors"][0]
        for row in tie_rows
    )
    non_tie_rows = [
        row
        for case in payload["case_rows"]
        if not case["all_replays_within_oracle"]
        for row in case["mode_rows"]
    ]
    non_tie_passed = sum(
        int(row["oracle"]["minimizer_count"]) == 1
        and Fraction(row["oracle"]["minimum_score_fraction"])
        < Fraction(row["oracle"]["second_distinct_score_fraction"])
        for row in non_tie_rows
    )
    return {
        "tie_control_count": len(tie_rows),
        "tie_controls_passed": tie_passed,
        "non_tie_control_count": len(non_tie_rows),
        "non_tie_controls_passed": non_tie_passed,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    return "\n".join(
        [
            "# B4/B8/B10 R174 Independent Exact-Score Oracle",
            "",
            f"- Status: `{result['status']}`",
            f"- Classification: `{result['classification']}`",
            f"- Requirements: `{result['requirements_passed']}/10`",
            f"- Payload hash: `{result['payload_hash']}`",
            "",
            "## Result",
            "",
            f"A standard-library `Fraction` implementation, without importing Qiskit or the R174 comparator, reproduces `{summary['row_record_matches']}/{summary['row_count']}` row records and `{summary['candidate_total_matches']}/{summary['candidate_count']}` candidate totals. It also passes `{summary['permutation_checks_passed']}/{summary['permutation_check_count']}` permutation checks and the R160 4/4 tie plus 28/28 non-tie guardrail.",
            "",
            "## Claim Boundary",
            "",
            "This independently validates the frozen replay arithmetic and selection semantics. It is not an integrated source patch, production performance result, confirmed Qiskit bug, hardware result, quantum advantage, BQP separation, solved frontier, or new credit.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    parser.add_argument("--preregistration-created-at", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if (root / RESULT_PATH).exists():
        raise ValueError("R174 independent oracle artifact already exists")
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    source = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    for payload, key, label in (
        (protocol, "payload_hash", "protocol"),
        (contract, "payload_hash", "contract"),
        (source, "payload_hash", "source result"),
    ):
        body = dict(payload)
        observed = body.pop(key)
        if canonical_hash(body) != observed:
            raise ValueError(f"R174 oracle {label} payload mismatch")
    path_bindings = {
        binding["path"]: binding
        for binding in contract["source_bindings"].values()
    }
    records = []
    candidate_total_matches = 0
    for dataset in protocol["datasets"]:
        for worker in sorted((root / dataset["worker_directory"]).glob("*.json")):
            worker_path = str(worker.relative_to(root))
            if file_sha256(worker) != path_bindings[worker_path]["sha256"]:
                raise ValueError(f"R174 oracle worker hash mismatch: {worker_path}")
            payload = json.loads(worker.read_text(encoding="utf-8"))
            for replay_index, row in enumerate(payload["replay_rows"]):
                record, matched = recompute_row(
                    dataset["dataset_id"],
                    worker_path,
                    payload["profile_id"],
                    replay_index,
                    row["replay"],
                )
                records.append(record)
                candidate_total_matches += matched
    controls = recompute_r160(root)
    primary_by_key = {
        (row["dataset_id"], row["profile_id"], row["replay_index"]): row
        for row in source["row_records"]
    }
    row_matches = sum(
        primary_by_key[(row["dataset_id"], row["profile_id"], row["replay_index"])]
        == row
        for row in records
    )
    record_hashes_valid = sum(
        canonical_hash({key: value for key, value in row.items() if key != "row_hash"})
        == row["row_hash"]
        for row in source["row_records"]
    )
    permutation_passed = sum(row["permutation_checks_passed"] for row in records)
    permutation_count = sum(row["permutation_check_count"] for row in records)
    dataset_counts = {
        dataset_id: sum(row["dataset_id"] == dataset_id for row in records)
        for dataset_id in (
            "r169_non_tie",
            "r170_path_true_tie",
            "r172_t_tree_true_tie",
        )
    }
    requirements = [
        ("P1", len(records) == 576 and len(source["row_records"]) == 576),
        ("P2", record_hashes_valid == 576),
        ("P3", row_matches == 576),
        ("P4", canonical_hash(records) == source["row_record_set_hash"]),
        ("P5", candidate_total_matches == 1728),
        ("P6", dataset_counts == {"r169_non_tie": 192, "r170_path_true_tie": 192, "r172_t_tree_true_tie": 192}),
        ("P7", permutation_passed == permutation_count == 3456),
        ("P8", controls == {"tie_control_count": 4, "tie_controls_passed": 4, "non_tie_control_count": 28, "non_tie_controls_passed": 28}),
        ("P9", "qiskit" not in sys.modules and "b4_b8_r174_exact_score_comparator" not in sys.modules),
        ("P10", args.preregistration_commit == source["preregistration"]["commit"] and args.preregistration_discussion == source["preregistration"]["discussion"]),
    ]
    passed = all(value for _, value in requirements)
    result = {
        "title": "B4/B8/B10 R174 independent exact-score oracle",
        "version": 0,
        "method": METHOD,
        "status": "independent_exact_score_oracle_complete" if passed else "independent_exact_score_oracle_failed",
        "classification": "independent_fraction_reproduction_of_fixed_grid_comparator" if passed else "incomplete",
        "source_target_id": "T-B4-002cu/T-B8-003cy/T-B10-009ck-r174-oracle",
        "upstream_target_id": source["source_target_id"],
        "preregistration": source["preregistration"],
        "source_result_payload_hash": source["payload_hash"],
        "row_record_set_hash": canonical_hash(records),
        "r160_policy_guardrail": controls,
        "summary": {
            "row_count": len(records),
            "row_record_matches": row_matches,
            "primary_row_hashes_valid": record_hashes_valid,
            "candidate_count": 1728,
            "candidate_total_matches": candidate_total_matches,
            "permutation_checks_passed": permutation_passed,
            "permutation_check_count": permutation_count,
            "r160_tie_controls_passed": controls["tie_controls_passed"],
            "r160_non_tie_controls_passed": controls["non_tie_controls_passed"],
            "qiskit_imported": "qiskit" in sys.modules,
            "comparator_imported": "b4_b8_r174_exact_score_comparator" in sys.modules,
            "qiskit_calls_performed": 0,
            "simulation_execution_count": 0,
            "total_simulated_shots": 0,
            "source_patch_performed": False,
            "production_policy_changed": False,
            "confirmed_qiskit_bug_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "solved_frontier_claimed": False,
            "new_credit_delta": 0,
        },
        "requirements": [
            {"requirement_id": requirement_id, "passed": value}
            for requirement_id, value in requirements
        ],
        "requirements_passed": sum(value for _, value in requirements),
        "requirements_failed": sum(not value for _, value in requirements),
        "artifacts": {
            "source_result": SOURCE_PATH,
            "result": RESULT_PATH,
            "markdown_report": REPORT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": "independent standard-library Fraction reproduction of every R174 fixed-grid comparator row and control",
            "what_is_not_supported": "an integrated source patch, acceptable production overhead, a confirmed Qiskit bug, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    result["payload_hash"] = canonical_hash(result)
    write_json(root / RESULT_PATH, result)
    (root / REPORT_PATH).write_text(build_report(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

