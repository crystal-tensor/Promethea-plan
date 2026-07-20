#!/usr/bin/env python3
"""Independently audit R175 without importing Qiskit or its comparator."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import struct
import sys
from collections import Counter
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r175_independent_rust_exact_oracle_v0"
PROTOCOL_PATH = "results/B4_B8_R175_rust_exact_score_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R175_rust_exact_score_contract_v0.json"
SOURCE_PATH = "results/B4_B8_R175_rust_exact_score_v0.json"
WORKER_DIR = "results/B4_B8_R175_rust_exact_score"
R160_ANALYSIS_PATH = "results/B4_B8_R160_deterministic_error_map_remediation/case_analysis.json"
R161_PATH = "results/B4_B8_R161_source_faithful_score_audit_v0.json"
RESULT_PATH = "results/B4_B8_R175_independent_rust_exact_oracle_v0.json"
REPORT_PATH = "research/B4_B8_R175_independent_rust_exact_oracle.md"


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_hash_field(payload: dict[str, Any], field: str, label: str) -> str:
    body = dict(payload)
    observed = body.pop(field, None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R175 independent {label} hash mismatch")
    return str(observed)


def bits_to_float(bits: int) -> float:
    return struct.unpack(">d", int(bits).to_bytes(8, "big"))[0]


def neg_log_fidelity(error: float) -> float:
    if math.isnan(error) or error < 0.0 or error > 1.0:
        return math.inf
    return -math.log1p(-error)


def exact_leaf_oracle(
    descriptor: dict[str, Any], inventory: dict[str, Any]
) -> dict[str, Any]:
    values = {
        tuple(int(value) for value in row["key"]): bits_to_float(row["value_bits"])
        for row in descriptor["rows"]
    }
    one_counts = Counter(
        {int(key): int(value) for key, value in inventory["one_qubit_counts"].items()}
    )
    two_counts = Counter(
        {
            tuple(int(part) for part in key.split(",")): int(value)
            for key, value in inventory["two_qubit_counts"].items()
        }
    )
    scored: list[tuple[Fraction, tuple[int, ...]]] = []
    for vector in permutations(range(7)):
        score = Fraction()
        feasible = True
        for virtual, count in one_counts.items():
            value = values.get((vector[virtual], vector[virtual]))
            if value is None:
                feasible = False
                break
            score += Fraction.from_float(neg_log_fidelity(value) * count)
        if not feasible:
            continue
        for (left, right), count in two_counts.items():
            value = values.get((vector[left], vector[right]))
            if value is None:
                value = values.get((vector[right], vector[left]))
            if value is None:
                feasible = False
                break
            score += Fraction.from_float(neg_log_fidelity(value) * count)
        if feasible:
            scored.append((score, vector))
    if not scored:
        raise ValueError("R175 independent oracle found no feasible mapping")
    scored.sort(key=lambda row: (row[0], row[1]))
    best = scored[0][0]
    minimizers = [list(vector) for score, vector in scored if score == best]
    second = next(score for score, _ in scored if score > best)
    gap = second - best
    return {
        "feasible_mapping_count": len(scored),
        "minimum_score_fraction": f"{best.numerator}/{best.denominator}",
        "second_distinct_score_fraction": f"{second.numerator}/{second.denominator}",
        "minimizer_count": len(minimizers),
        "minimizer_vectors": minimizers,
        "minimum_gap_fraction": f"{gap.numerator}/{gap.denominator}",
        "minimum_gap_float": float(gap),
        "minimum_gap_ulp_ratio": float(gap) / math.ulp(float(best)),
    }


def expected_standard_vectors(worker: dict[str, Any]) -> tuple[list[int], list[int]]:
    first = worker["replay_rows"][0]
    replay = first["replay"]
    source_full = [int(value) for value in first["mapping_vector"]]
    source_internal = [
        int(value) for value in replay["selected_mapping_vector"]["source_f64"]
    ]
    exact_internal = [
        int(value)
        for value in replay["selected_mapping_vector"]["exact_binary64_leaf"]
    ]
    physical_to_virtual = {
        physical: virtual for virtual, physical in enumerate(source_full)
    }
    exact_full = list(source_full)
    for source_physical, exact_physical in zip(source_internal, exact_internal):
        exact_full[physical_to_virtual[source_physical]] = exact_physical
    return source_full, exact_full


def median_ratio(source: list[int], exact: list[int]) -> float:
    return float(statistics.median(exact) / statistics.median(source))


def build_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    return "\n".join(
        [
            "# B4/B8/B10 R175 Independent Rust Exact-Score Oracle",
            "",
            f"- Status: `{result['status']}`",
            f"- Requirements: `{result['requirements_passed']}/12`",
            f"- Payload hash: `{result['payload_hash']}`",
            "",
            "## Independent Check",
            "",
            f"A standard-library-only audit validates `{summary['worker_hashes_valid']}/26` worker hashes and `{summary['row_hashes_valid']}/1600` row hashes. It reproduces `{summary['standard_outcomes_reproduced']}/1152` standard outcomes and independently enumerates all `{summary['small_gap_oracle_count']}/28` sub-ULP exact-oracle cells.",
            "",
            "It imports neither Qiskit nor the R175 execution module, performs zero Qiskit calls, simulations, routes, or shots, and recomputes the timing and peak-RSS ratios from immutable worker rows.",
            "",
            "## Claim Boundary",
            "",
            "This strengthens evidence integrity for the frozen R175 matrix. It does not make the experimental patch upstream accepted or production ready, establish a confirmed Qiskit bug, prove broad route-quality improvement or cross-platform overhead, provide hardware evidence, quantum advantage, BQP separation, solve B4/B8/B10, or add credit.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if (root / RESULT_PATH).exists() or (root / REPORT_PATH).exists():
        raise ValueError("R175 independent oracle evidence already exists")
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    source = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    validate_hash_field(protocol, "payload_hash", "protocol")
    validate_hash_field(contract, "payload_hash", "contract")
    validate_hash_field(source, "payload_hash", "source result")
    for section in ("source_bindings", "tool_bindings"):
        for binding in contract[section].values():
            path = root / binding["path"]
            if not path.exists() or file_sha256(path) != binding["sha256"]:
                raise ValueError(f"R175 independent binding mismatch: {binding['path']}")
    manifests = []
    worker_hashes_valid = 0
    row_hashes_valid = 0
    case_hashes_valid = 0
    artifacts_match = 0
    artifacts = {row["path"]: row for row in source["worker_artifacts"]}
    for path in sorted((root / WORKER_DIR).glob("*.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        validate_hash_field(manifest, "manifest_hash", f"worker {path.name}")
        worker_hashes_valid += 1
        relative = str(path.relative_to(root))
        artifact = artifacts.get(relative, {})
        artifacts_match += (
            artifact.get("sha256") == file_sha256(path)
            and artifact.get("manifest_hash") == manifest["manifest_hash"]
        )
        for row in manifest["replay_rows"]:
            validate_hash_field(row, "row_hash", f"row {path.name}")
            row_hashes_valid += 1
        for row in manifest.get("case_summaries", []):
            validate_hash_field(row, "case_summary_hash", f"case {path.name}")
            case_hashes_valid += 1
        manifests.append(manifest)
    rows = [row for manifest in manifests for row in manifest["replay_rows"]]

    standard_outcomes_reproduced = 0
    for manifest in [row for row in manifests if row["kind"] == "standard"]:
        dataset = next(
            row
            for row in protocol["datasets"]
            if row["dataset_id"] == manifest["dataset_id"]
        )
        committed = json.loads(
            (
                root
                / dataset["worker_directory"]
                / f"{manifest['profile_id']}.json"
            ).read_text(encoding="utf-8")
        )
        source_expected, exact_expected = expected_standard_vectors(committed)
        expected = (
            source_expected
            if manifest["policy"] == "source_f64"
            else exact_expected
        )
        standard_outcomes_reproduced += sum(
            row["mapping_vector"] == expected
            and row["expected_mapping_vector"] == expected
            for row in manifest["replay_rows"]
        )

    r160 = json.loads((root / R160_ANALYSIS_PATH).read_text(encoding="utf-8"))
    r161 = json.loads((root / R161_PATH).read_text(encoding="utf-8"))
    r160_rows = {row["case_id"]: row for row in r160["case_rows"]}
    oracle_by_cell: dict[tuple[str, str], dict[str, Any]] = {}
    oracle_payload_matches = 0
    small_gap_outcomes_reproduced = 0
    for manifest in [row for row in manifests if row["kind"] == "small-gap"]:
        for case in manifest["case_summaries"]:
            cell = (manifest["mode"], case["case_id"])
            oracle = exact_leaf_oracle(
                case["error_map_descriptor"], r161["interaction_inventory"]
            )
            if cell in oracle_by_cell and oracle_by_cell[cell] != oracle:
                raise ValueError(f"R175 independent descriptor disagreement: {cell}")
            oracle_by_cell[cell] = oracle
            oracle_payload_matches += oracle == case["exact_leaf_oracle"]
        for row in manifest["replay_rows"]:
            source_expected = next(
                mode["selected_vectors"][0]
                for mode in r160_rows[row["case_id"]]["mode_rows"]
                if mode["mode"] == manifest["mode"]
            )
            exact_expected = oracle_by_cell[(manifest["mode"], row["case_id"])][
                "minimizer_vectors"
            ][0]
            expected = (
                source_expected
                if manifest["policy"] == "source_f64"
                else exact_expected
            )
            small_gap_outcomes_reproduced += (
                row["mapping_vector"] == expected
                and row["expected_mapping_vector"] == expected
            )

    performance_cells = []
    for dataset in protocol["datasets"]:
        for profile in protocol["standard_profiles"]:
            selected = [
                row
                for row in rows
                if row["kind"] == "standard"
                and row["dataset_id"] == dataset["dataset_id"]
                and row["profile_id"] == profile
            ]
            source_values = [
                row["elapsed_ns"] for row in selected if row["policy"] == "source_f64"
            ]
            exact_values = [
                row["elapsed_ns"]
                for row in selected
                if row["policy"] == "rust_exact_retained_binary64"
            ]
            performance_cells.append(
                {
                    "cell_id": f"{dataset['dataset_id']}__{profile}",
                    "kind": "standard",
                    "source_median_ns": statistics.median(source_values),
                    "exact_median_ns": statistics.median(exact_values),
                    "exact_to_source_median_ratio": median_ratio(
                        source_values, exact_values
                    ),
                }
            )
    for mode in protocol["small_gap_modes"]:
        for case_id in protocol["small_gap_cases"]:
            selected = [
                row
                for row in rows
                if row["kind"] == "small-gap"
                and row["mode"] == mode
                and row["case_id"] == case_id
            ]
            source_values = [
                row["elapsed_ns"] for row in selected if row["policy"] == "source_f64"
            ]
            exact_values = [
                row["elapsed_ns"]
                for row in selected
                if row["policy"] == "rust_exact_retained_binary64"
            ]
            performance_cells.append(
                {
                    "cell_id": f"{mode}__{case_id}",
                    "kind": "small-gap",
                    "source_median_ns": statistics.median(source_values),
                    "exact_median_ns": statistics.median(exact_values),
                    "exact_to_source_median_ratio": median_ratio(
                        source_values, exact_values
                    ),
                }
            )
    worker_pairs = []
    for kind, identity in sorted(
        {(row["kind"], row["identity"]) for row in manifests}
    ):
        source_worker = next(
            row
            for row in manifests
            if row["kind"] == kind
            and row["identity"] == identity
            and row["policy"] == "source_f64"
        )
        exact_worker = next(
            row
            for row in manifests
            if row["kind"] == kind
            and row["identity"] == identity
            and row["policy"] == "rust_exact_retained_binary64"
        )
        worker_pairs.append(
            {
                "cell_id": f"{kind}__{identity}",
                "source_peak_rss": source_worker["peak_rss"],
                "exact_peak_rss": exact_worker["peak_rss"],
                "rss_unit": source_worker["peak_rss_unit"],
                "exact_to_source_peak_rss_ratio": exact_worker["peak_rss"]
                / source_worker["peak_rss"],
            }
        )
    source_rows = [row for row in rows if row["policy"] == "source_f64"]
    exact_rows = [
        row for row in rows if row["policy"] == "rust_exact_retained_binary64"
    ]
    aggregate_ratio = median_ratio(
        [row["elapsed_ns"] for row in source_rows],
        [row["elapsed_ns"] for row in exact_rows],
    )
    summary_matches = (
        source["summary"]["aggregate_exact_to_source_median_time_ratio"]
        == aggregate_ratio
        and source["summary"]["maximum_cell_exact_to_source_median_time_ratio"]
        == max(row["exact_to_source_median_ratio"] for row in performance_cells)
        and source["summary"]["maximum_worker_exact_to_source_peak_rss_ratio"]
        == max(row["exact_to_source_peak_rss_ratio"] for row in worker_pairs)
    )
    preregistration_matches = (
        args.preregistration_commit == source["preregistration"]["commit"]
        and args.preregistration_discussion
        == source["preregistration"]["discussion"]
    )
    requirements = [
        ("P1", len(manifests) == worker_hashes_valid == artifacts_match == 26),
        ("P2", len(rows) == row_hashes_valid == 1600 and case_hashes_valid == 56),
        ("P3", canonical_hash(rows) == source["row_set_hash"]),
        ("P4", standard_outcomes_reproduced == 1152),
        ("P5", len(oracle_by_cell) == 28 and oracle_payload_matches == 56),
        ("P6", all(row["minimizer_count"] == 1 for row in oracle_by_cell.values())),
        ("P7", small_gap_outcomes_reproduced == 448),
        ("P8", performance_cells == source["performance_cells"]),
        ("P9", worker_pairs == source["memory_pairs"] and summary_matches),
        ("P10", source["requirements_failed"] == 0 and source["requirements_passed"] == 14),
        ("P11", "qiskit" not in sys.modules and "b4_b8_r175_rust_exact_score_replay" not in sys.modules),
        ("P12", preregistration_matches),
    ]
    passed = all(value for _, value in requirements)
    result = {
        "title": "B4/B8/B10 R175 independent Rust exact-score oracle",
        "version": 0,
        "method": METHOD,
        "status": "independent_rust_exact_score_oracle_complete" if passed else "independent_rust_exact_score_oracle_failed",
        "classification": "standard_library_reproduction_of_integrated_rust_matrix" if passed else "incomplete",
        "source_target_id": "T-B4-002cy/T-B8-003dc/T-B10-009co-r175-oracle",
        "upstream_target_id": source["source_target_id"],
        "preregistration": source["preregistration"],
        "source_result_payload_hash": source["payload_hash"],
        "summary": {
            "worker_hashes_valid": worker_hashes_valid,
            "row_hashes_valid": row_hashes_valid,
            "case_hashes_valid": case_hashes_valid,
            "worker_artifacts_match": artifacts_match,
            "standard_outcomes_reproduced": standard_outcomes_reproduced,
            "small_gap_oracle_count": len(oracle_by_cell),
            "small_gap_oracle_payload_matches": oracle_payload_matches,
            "small_gap_outcomes_reproduced": small_gap_outcomes_reproduced,
            "performance_cell_count": len(performance_cells),
            "memory_pair_count": len(worker_pairs),
            "summary_matches": summary_matches,
            "qiskit_imported": "qiskit" in sys.modules,
            "r175_executor_imported": "b4_b8_r175_rust_exact_score_replay" in sys.modules,
            "qiskit_calls_performed": 0,
            "simulation_execution_count": 0,
            "total_simulated_shots": 0,
            "upstream_patch_accepted": False,
            "production_qiskit_remedy_claimed": False,
            "confirmed_qiskit_bug_claimed": False,
            "hardware_result_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "solved_frontier_claimed": False,
            "new_credit_delta": 0,
        },
        "oracle_cells": [
            {"mode": key[0], "case_id": key[1], "oracle": value}
            for key, value in sorted(oracle_by_cell.items())
        ],
        "requirements": [
            {"requirement_id": key, "passed": value} for key, value in requirements
        ],
        "requirements_passed": sum(value for _, value in requirements),
        "requirements_failed": sum(not value for _, value in requirements),
        "artifacts": {
            "source_result": SOURCE_PATH,
            "result": RESULT_PATH,
            "markdown_report": REPORT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": "a Qiskit-free standard-library reproduction of every frozen R175 mapping expectation, sub-ULP exact oracle, hash, timing ratio, and peak-RSS ratio",
            "what_is_not_supported": "an upstream-accepted or production Qiskit remedy, confirmed Qiskit bug, broad route-quality improvement, cross-platform overhead, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    result["payload_hash"] = canonical_hash(result)
    write_json(root / RESULT_PATH, result)
    (root / REPORT_PATH).write_text(build_report(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
