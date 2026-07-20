#!/usr/bin/env python3
"""Run the preregistered R174 fixed-grid exact-score shadow comparator."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r154_deterministic_automatic_replay import canonical_hash
from b4_b8_r174_exact_score_comparator import select_first_exact_minimum


METHOD = "b4_b8_r174_exact_score_comparator_v0"
PROTOCOL_PATH = "results/B4_B8_R174_exact_score_comparator_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R174_exact_score_comparator_contract_v0.json"
RESULT_PATH = "results/B4_B8_R174_exact_score_comparator_v0.json"
REPORT_PATH = "research/B4_B8_R174_exact_score_comparator.md"
R160_PATH = "results/B4_B8_R160_deterministic_error_map_remediation/case_analysis.json"


def validate_payload(payload: dict[str, Any], key: str, label: str) -> str:
    body = dict(payload)
    observed = body.pop(key, None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R174 {label} payload hash mismatch")
    return str(observed)


def binding_by_path(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        binding["path"]: binding
        for binding in contract["source_bindings"].values()
    }


def validate_contract(root: Path, protocol: dict[str, Any], contract: dict[str, Any]) -> None:
    protocol_hash = validate_payload(protocol, "payload_hash", "protocol")
    validate_payload(contract, "payload_hash", "contract")
    if contract.get("contract_id") != "B4-B8-R174-exact-score-comparator-contract-v0":
        raise ValueError("R174 contract identity mismatch")
    if contract.get("execution_started") is not False:
        raise ValueError("R174 contract is not unopened")
    if contract.get("protocol_payload_hash") != protocol_hash:
        raise ValueError("R174 protocol binding mismatch")
    for section in ("source_bindings", "tool_bindings"):
        for binding in contract[section].values():
            path = root / binding["path"]
            if not path.exists() or file_sha256(path) != binding["sha256"]:
                raise ValueError(f"R174 binding mismatch: {binding['path']}")
    for path in contract["result_paths_must_be_absent"]:
        if (root / path).exists():
            raise ValueError(f"R174 result existed before execution: {path}")


def fraction_fields_to_grid(candidate: dict[str, Any]) -> int:
    numerator = int(candidate["exact_score_numerator"])
    denominator = int(candidate["exact_score_denominator"])
    if denominator <= 0 or denominator & (denominator - 1):
        raise ValueError("R174 expected a power-of-two exact-score denominator")
    denominator_exponent = denominator.bit_length() - 1
    if denominator_exponent > 1074:
        raise ValueError("R174 exact-score denominator is finer than binary64 grid")
    return numerator << (1074 - denominator_exponent)


def grid_hash(value: int) -> str:
    return hashlib.sha256(str(value).encode("ascii")).hexdigest()


def first_exact_minimum_for_permutation(
    candidates: list[dict[str, Any]], permutation: tuple[int, ...]
) -> int:
    permuted = [candidates[index] for index in permutation]
    selected_position, _, _ = select_first_exact_minimum(permuted)
    return permutation[selected_position]


def analyze_replay_row(
    dataset_id: str,
    worker_path: str,
    profile_id: str,
    replay_index: int,
    replay: dict[str, Any],
) -> dict[str, Any]:
    candidates = replay["candidates"]
    if len(candidates) != 3:
        raise ValueError("R174 frozen matrix expects exactly three candidates per row")
    selected, tied, keys = select_first_exact_minimum(candidates)
    stored_exact = int(replay["selected_candidate_index"]["exact_binary64_leaf"])
    source = int(replay["selected_candidate_index"]["source_f64"])
    stored_keys = [fraction_fields_to_grid(candidate) for candidate in candidates]
    candidate_totals_match = keys == stored_keys
    minimum = min(keys)
    permutations_passed = 0
    for permutation in itertools.permutations(range(len(candidates))):
        expected = next(index for index in permutation if keys[index] == minimum)
        permutations_passed += (
            first_exact_minimum_for_permutation(candidates, permutation) == expected
        )
    source_gap_bits = abs(
        int(candidates[source]["source_score_bits"])
        - int(candidates[selected]["source_score_bits"])
    )
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
        "source_to_comparator_score_bit_gap": source_gap_bits,
        "candidate_total_grid_hashes": [grid_hash(key) for key in keys],
        "candidate_total_bit_lengths": [abs(key).bit_length() for key in keys],
        "candidate_totals_match_stored_exact": candidate_totals_match,
        "comparator_matches_stored_exact": selected == stored_exact,
        "permutation_checks_passed": permutations_passed,
        "permutation_check_count": 6,
    }
    record["row_hash"] = canonical_hash(record)
    return record


def r160_controls(root: Path) -> dict[str, Any]:
    payload = json.loads((root / R160_PATH).read_text(encoding="utf-8"))
    tie_rows = []
    for row in payload["tie_baseline"]["mode_rows"]:
        minimizers = row["oracle"]["minimizer_vectors"]
        selected = row["selected_vectors"]
        tie_rows.append(
            {
                "mode": row["mode"],
                "exact_tie": int(row["oracle"]["minimizer_count"]) == 2,
                "first_exact_minimizer_preserved": bool(selected)
                and selected[0] == minimizers[0],
            }
        )
    non_tie_rows = []
    for case in payload["case_rows"]:
        if case["all_replays_within_oracle"]:
            continue
        for row in case["mode_rows"]:
            minimum = row["oracle"]["minimum_score_fraction"]
            second = row["oracle"]["second_distinct_score_fraction"]
            minimum_num, minimum_den = (int(value) for value in minimum.split("/"))
            second_num, second_den = (int(value) for value in second.split("/"))
            non_tie_rows.append(
                {
                    "case_id": case["case_id"],
                    "mode": row["mode"],
                    "unique_exact_minimum": int(row["oracle"]["minimizer_count"]) == 1,
                    "strict_exact_gap": minimum_num * second_den
                    < second_num * minimum_den,
                }
            )
    return {
        "source_path": R160_PATH,
        "source_sha256": file_sha256(root / R160_PATH),
        "tie_control_count": len(tie_rows),
        "tie_controls_passed": sum(
            row["exact_tie"] and row["first_exact_minimizer_preserved"]
            for row in tie_rows
        ),
        "non_tie_control_count": len(non_tie_rows),
        "non_tie_controls_passed": sum(
            row["unique_exact_minimum"] and row["strict_exact_gap"]
            for row in non_tie_rows
        ),
        "tie_rows": tie_rows,
        "non_tie_rows": non_tie_rows,
    }


def build_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    matrix = result["dataset_summary"]
    rows = [
        f"| {row['dataset_id']} | {row['replay_count']} | {row['source_preserved_count']} | {row['source_changed_to_exact_count']} | {row['exact_tie_count']} |"
        for row in matrix
    ]
    return "\n".join(
        [
            "# B4/B8/B10 R174 Exact-Score Comparator",
            "",
            f"- Status: `{result['status']}`",
            f"- Classification: `{result['classification']}`",
            f"- Requirements: `{result['requirements_passed']}/10`",
            f"- Payload hash: `{result['payload_hash']}`",
            "",
            "## Research Question",
            "",
            "Can an exact fixed-grid score comparator remove two cross-graph one-ULP false winners without disturbing declared non-ties?",
            "",
            "## Result",
            "",
            f"The shadow comparator validates `{summary['replay_rows_validated']}/576` replay rows and `{summary['candidate_totals_validated']}/1728` candidate totals. It passes `{summary['permutation_checks_passed']}/{summary['permutation_check_count']}` order tests, each of which requires the first exact minimizer in the presented candidate order.",
            "",
            "| Dataset | Rows | Source preserved | Changed to exact | Exact ties |",
            "|---|---:|---:|---:|---:|",
            *rows,
            "",
            "R169 preserves all 192 non-tie selections. R170 and R172 each replace all 192 source one-ULP false winners with the first member of the exact tie. The R160 guardrail passes 4/4 exact ties and 28/28 exact non-ties.",
            "",
            "## Mechanism",
            "",
            "Every finite binary64 leaf is decoded exactly into an integer multiple of `2^-1074`. Integer addition is associative and order independent, so candidate comparison no longer depends on the reduction tree. Equality uses strict-less-than semantics and therefore preserves the first candidate seen.",
            "",
            "## Claim Boundary",
            "",
            "This is a replay-backed shadow comparator, not an integrated Qiskit source patch. It does not establish acceptable runtime overhead, route quality beyond the frozen matrix, a confirmed Qiskit bug, hardware relevance, quantum advantage, BQP separation, a solved frontier, or new credit.",
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
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    validate_contract(root, protocol, contract)
    path_bindings = binding_by_path(contract)
    records = []
    dataset_summary = []
    for dataset in protocol["datasets"]:
        result_path = dataset["result_path"]
        result_payload = json.loads((root / result_path).read_text(encoding="utf-8"))
        validate_payload(result_payload, "payload_hash", dataset["dataset_id"])
        if file_sha256(root / result_path) != path_bindings[result_path]["sha256"]:
            raise ValueError(f"R174 result source changed: {result_path}")
        dataset_records = []
        for worker in sorted((root / dataset["worker_directory"]).glob("*.json")):
            worker_path = str(worker.relative_to(root))
            if file_sha256(worker) != path_bindings[worker_path]["sha256"]:
                raise ValueError(f"R174 worker source changed: {worker_path}")
            payload = json.loads(worker.read_text(encoding="utf-8"))
            for replay_index, row in enumerate(payload["replay_rows"]):
                dataset_records.append(
                    analyze_replay_row(
                        dataset["dataset_id"],
                        worker_path,
                        payload["profile_id"],
                        replay_index,
                        row["replay"],
                    )
                )
        records.extend(dataset_records)
        dataset_summary.append(
            {
                "dataset_id": dataset["dataset_id"],
                "replay_count": len(dataset_records),
                "candidate_count": len(dataset_records) * 3,
                "candidate_totals_validated": sum(
                    row["candidate_totals_match_stored_exact"] for row in dataset_records
                )
                * 3,
                "comparator_matches_stored_exact_count": sum(
                    row["comparator_matches_stored_exact"] for row in dataset_records
                ),
                "source_preserved_count": sum(
                    row["source_selected_candidate_index"]
                    == row["comparator_selected_candidate_index"]
                    for row in dataset_records
                ),
                "source_changed_to_exact_count": sum(
                    row["source_selected_candidate_index"]
                    != row["comparator_selected_candidate_index"]
                    and row["comparator_matches_stored_exact"]
                    for row in dataset_records
                ),
                "exact_tie_count": sum(
                    row["exact_minimizer_count"] > 1 for row in dataset_records
                ),
                "one_ulp_source_split_count": sum(
                    row["source_to_comparator_score_bit_gap"] == 1
                    and row["source_selected_candidate_index"]
                    != row["comparator_selected_candidate_index"]
                    for row in dataset_records
                ),
                "permutation_checks_passed": sum(
                    row["permutation_checks_passed"] for row in dataset_records
                ),
                "permutation_check_count": len(dataset_records) * 6,
            }
        )
    by_id = {row["dataset_id"]: row for row in dataset_summary}
    controls = r160_controls(root)
    replay_validated = sum(row["comparator_matches_stored_exact"] for row in records)
    candidate_totals_validated = sum(
        3 for row in records if row["candidate_totals_match_stored_exact"]
    )
    permutation_passed = sum(row["permutation_checks_passed"] for row in records)
    permutation_count = sum(row["permutation_check_count"] for row in records)
    requirements = [
        ("P1", len(records) == 576 and candidate_totals_validated == 1728),
        ("P2", replay_validated == 576),
        ("P3", by_id["r169_non_tie"]["source_preserved_count"] == 192),
        ("P4", by_id["r169_non_tie"]["exact_tie_count"] == 0),
        ("P5", by_id["r170_path_true_tie"]["source_changed_to_exact_count"] == 192 and by_id["r170_path_true_tie"]["one_ulp_source_split_count"] == 192),
        ("P6", by_id["r172_t_tree_true_tie"]["source_changed_to_exact_count"] == 192 and by_id["r172_t_tree_true_tie"]["one_ulp_source_split_count"] == 192),
        ("P7", by_id["r170_path_true_tie"]["exact_tie_count"] == 192 and by_id["r172_t_tree_true_tie"]["exact_tie_count"] == 192),
        ("P8", permutation_passed == permutation_count == 3456),
        ("P9", controls["tie_controls_passed"] == controls["tie_control_count"] == 4 and controls["non_tie_controls_passed"] == controls["non_tie_control_count"] == 28),
        ("P10", args.preregistration_discussion.startswith("https://github.com/crystal-tensor/Prometheus-plan/discussions/") and len(args.preregistration_commit) >= 7),
    ]
    passed = all(value for _, value in requirements)
    result = {
        "title": "B4/B8/B10 R174 fixed-grid exact-score comparator",
        "version": 0,
        "method": METHOD,
        "status": "shadow_comparator_matrix_passed" if passed else "shadow_comparator_matrix_failed",
        "classification": "cross_graph_exact_tie_repair_with_non_tie_preservation" if passed else "incomplete",
        "source_target_id": "T-B4-002ct/T-B8-003cx/T-B10-009cj-r174",
        "upstream_target_id": protocol["source_target_id"],
        "preregistration": {
            "commit": args.preregistration_commit,
            "discussion": args.preregistration_discussion,
            "created_at": args.preregistration_created_at,
        },
        "protocol_payload_hash": protocol["payload_hash"],
        "contract_payload_hash": contract["payload_hash"],
        "algorithm": protocol["algorithm"],
        "dataset_summary": dataset_summary,
        "row_records": records,
        "row_record_set_hash": canonical_hash(records),
        "r160_policy_guardrail": controls,
        "summary": {
            "dataset_count": len(dataset_summary),
            "worker_file_count": 9,
            "replay_rows_validated": replay_validated,
            "candidate_totals_validated": candidate_totals_validated,
            "permutation_checks_passed": permutation_passed,
            "permutation_check_count": permutation_count,
            "r169_non_tie_source_preserved": by_id["r169_non_tie"]["source_preserved_count"],
            "r170_true_tie_repaired": by_id["r170_path_true_tie"]["source_changed_to_exact_count"],
            "r172_true_tie_repaired": by_id["r172_t_tree_true_tie"]["source_changed_to_exact_count"],
            "r160_tie_controls_passed": controls["tie_controls_passed"],
            "r160_non_tie_controls_passed": controls["non_tie_controls_passed"],
            "qiskit_calls_performed": 0,
            "simulation_execution_count": 0,
            "total_simulated_shots": 0,
            "qiskit_source_changed": False,
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
            "protocol": PROTOCOL_PATH,
            "contract": CONTRACT_PATH,
            "result": RESULT_PATH,
            "markdown_report": REPORT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": "a replay-backed fixed-grid exact-score shadow comparator that preserves the R169 non-ties and repairs the R170/R172 exact ties under first-seen semantics",
            "what_is_not_supported": "an integrated Qiskit source patch, acceptable production overhead, changed route quality beyond the frozen matrix, a confirmed Qiskit bug, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    result["payload_hash"] = canonical_hash(result)
    write_json(root / RESULT_PATH, result)
    (root / REPORT_PATH).write_text(build_report(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

