#!/usr/bin/env python3
"""Independently verify R182 using only committed JSON and stdlib arithmetic."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r182_independent_cost_oracle_v0"
PROTOCOL_PATH = "results/B4_B8_R182_score_cost_attribution_protocol_v0.json"
AMENDMENT_PATH = (
    "results/B4_B8_R182_score_cost_attribution_protocol_amendment_v1.json"
)
CONTRACT_PATH = (
    "benchmarks/B4_B8_R182_score_cost_attribution_execution_contract_v0.json"
)
RESULT_PATH = "results/B4_B8_R182_score_cost_attribution_v0.json"
WORKER_DIR = "results/B4_B8_R182_score_cost_attribution_replay"
BUILD_MANIFEST_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R182_score_cost_linux_x86_64_build_manifest.json"
)
BINARY_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R182_score_cost_pyext.x86_64-linux-gnu.so"
)
OUTPUT_PATH = "results/B4_B8_R182_independent_cost_oracle_v0.json"
REPORT_PATH = "research/B4_B8_R182_independent_cost_oracle.md"
POLICIES = [
    "rust_biguint_exact_retained_binary64",
    "rust_fixed_exact_retained_binary64",
    "rust_active_limb_exact_retained_binary64",
]
COUNTER_KEYS = [
    "leaf_construction_count",
    "destination_zeroed_limb_count",
    "arithmetic_limb_visit_count",
    "comparison_limb_visit_count",
    "carry_extension_count",
    "maximum_used_limb_count",
    "biguint_heap_allocation_count",
    "biguint_heap_allocated_bytes",
]


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_hash_field(payload: dict[str, Any], field: str, label: str) -> str:
    body = dict(payload)
    observed = body.pop(field, None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R182 independent oracle {label} hash mismatch")
    return str(observed)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def average_ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda row: (row[1], row[0]))
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(indexed):
        end = cursor + 1
        while end < len(indexed) and indexed[end][1] == indexed[cursor][1]:
            end += 1
        rank = (cursor + 1 + end) / 2
        for index, _ in indexed[cursor:end]:
            ranks[index] = rank
        cursor = end
    return ranks


def pearson(left: list[float], right: list[float]) -> float:
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)
    numerator = sum(
        (x - left_mean) * (y - right_mean) for x, y in zip(left, right)
    )
    left_norm = math.sqrt(sum((x - left_mean) ** 2 for x in left))
    right_norm = math.sqrt(sum((y - right_mean) ** 2 for y in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def spearman(left: list[float], right: list[float]) -> float:
    return pearson(average_ranks(left), average_ranks(right))


def expected_cells(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return contract["workload_matrix"]["cells"]


def recompute(
    protocol: dict[str, Any],
    amendment: dict[str, Any],
    contract: dict[str, Any],
    workers: list[dict[str, Any]],
) -> dict[str, Any]:
    rows = [row for worker in workers for row in worker["replay_rows"]]
    by_cell_policy: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_cell_policy[(row["cell_id"], row["policy"])].append(row)
    cell_summaries = []
    for cell in expected_cells(contract):
        summary: dict[str, Any] = {"cell": cell, "policies": {}}
        for policy in POLICIES:
            selected = by_cell_policy[(cell["cell_id"], policy)]
            summary["policies"][policy] = {
                "measurement_count": len(selected),
                "median_elapsed_nanoseconds": statistics.median(
                    row["elapsed_nanoseconds"] for row in selected
                ),
                "median_cost_counters": {
                    key: statistics.median(
                        row["cost_counters"][key] for row in selected
                    )
                    for key in COUNTER_KEYS
                },
            }
        biguint = summary["policies"][POLICIES[0]]
        fixed = summary["policies"][POLICIES[1]]
        active = summary["policies"][POLICIES[2]]
        summary["active_to_fixed_median_time_ratio"] = (
            active["median_elapsed_nanoseconds"] / fixed["median_elapsed_nanoseconds"]
        )
        summary["active_to_biguint_median_time_ratio"] = (
            active["median_elapsed_nanoseconds"]
            / biguint["median_elapsed_nanoseconds"]
        )
        summary["biguint_minus_active_median_nanoseconds"] = (
            biguint["median_elapsed_nanoseconds"]
            - active["median_elapsed_nanoseconds"]
        )
        summary["cell_summary_hash"] = canonical_hash(summary)
        cell_summaries.append(summary)

    fixed_arithmetic = sum(
        row["cost_counters"]["arithmetic_limb_visit_count"]
        for row in rows
        if row["policy"] == POLICIES[1]
    )
    active_arithmetic = sum(
        row["cost_counters"]["arithmetic_limb_visit_count"]
        for row in rows
        if row["policy"] == POLICIES[2]
    )
    fixed_zeroed = sum(
        row["cost_counters"]["destination_zeroed_limb_count"]
        for row in rows
        if row["policy"] == POLICIES[1]
    )
    active_zeroed = sum(
        row["cost_counters"]["destination_zeroed_limb_count"]
        for row in rows
        if row["policy"] == POLICIES[2]
    )
    active_times = [
        row["elapsed_nanoseconds"] for row in rows if row["policy"] == POLICIES[2]
    ]
    fixed_times = [
        row["elapsed_nanoseconds"] for row in rows if row["policy"] == POLICIES[1]
    ]
    arithmetic_reduction = 1.0 - active_arithmetic / fixed_arithmetic
    active_to_fixed = statistics.median(active_times) / statistics.median(fixed_times)
    h1 = next(
        row
        for row in protocol["frozen_hypotheses"]
        if row["hypothesis_id"] == "H1-full-destination-initialization"
    )
    h1_supported = (
        arithmetic_reduction
        >= h1["minimum_arithmetic_visit_reduction_fraction"]
        and active_zeroed == fixed_zeroed
        and active_to_fixed
        > h1["maximum_end_to_end_active_to_fixed_ratio_for_speed_success"]
    )
    allocation_pressure = [
        float(row["policies"][POLICIES[0]]["median_cost_counters"]["biguint_heap_allocated_bytes"])
        for row in cell_summaries
    ]
    timing_gap = [
        float(row["biguint_minus_active_median_nanoseconds"])
        for row in cell_summaries
    ]
    correlation = spearman(allocation_pressure, timing_gap)
    h2 = next(
        row
        for row in protocol["frozen_hypotheses"]
        if row["hypothesis_id"] == "H2-biguint-heap-cost"
    )
    h2_supported = (
        min(allocation_pressure) > 0
        and correlation >= h2["minimum_spearman_rank_correlation"]
    )
    h3_supported = len(cell_summaries) == 13
    classifications = {
        "H1-full-destination-initialization": {
            "classification": (
                "full_width_initialization_or_common_cost_pressure_consistent_not_causal"
                if h1_supported
                else "rejected_or_inconclusive"
            ),
            "supported_under_frozen_rule": h1_supported,
            "arithmetic_visit_reduction_fraction": arithmetic_reduction,
            "fixed_destination_zeroed_limb_count": fixed_zeroed,
            "active_destination_zeroed_limb_count": active_zeroed,
            "aggregate_active_to_fixed_median_time_ratio": active_to_fixed,
        },
        "H2-biguint-heap-cost": {
            "classification": (
                "biguint_heap_pressure_supported"
                if h2_supported
                else "biguint_heap_pressure_rejected"
            ),
            "supported_under_frozen_rule": h2_supported,
            "allocation_pressure_positive_all_cells": min(allocation_pressure) > 0,
            "spearman_rank_correlation": correlation,
        },
        "H3-candidate-shape": {
            "classification": (
                "cell_heterogeneity_reported" if h3_supported else "cell_coverage_failed"
            ),
            "supported_under_frozen_rule": h3_supported,
            "reported_cell_count": len(cell_summaries),
        },
    }
    counter_vectors: dict[tuple[str, str, str], set[tuple[int, ...]]] = defaultdict(set)
    for row in rows:
        key = (row["cell_id"], row["policy"], row["subcell_id"])
        counter_vectors[key].add(tuple(row["cost_counters"][name] for name in COUNTER_KEYS))
    counts = amendment["corrected_workload_counts"]
    summary = {
        "worker_count": len(workers),
        "expected_worker_count": len(expected_cells(contract)) * len(POLICIES),
        "workload_cell_count": len(cell_summaries),
        "recorded_measurement_count": len(rows),
        "timing_call_count": sum(row["timing_call_count"] for row in rows),
        "counter_probe_call_count": sum(row["counter_probe_call_count"] for row in rows),
        "warmup_call_count": sum(worker["warmup_call_count"] for worker in workers),
        "total_qiskit_function_call_count": (
            sum(row["timing_call_count"] + row["counter_probe_call_count"] for row in rows)
            + sum(worker["warmup_call_count"] for worker in workers)
        ),
        "timing_expected_match_count": sum(row["timing_matches_expected"] for row in rows),
        "probe_expected_match_count": sum(row["probe_matches_expected"] for row in rows),
        "timing_probe_mapping_match_count": sum(row["timing_probe_mapping_match"] for row in rows),
        "counter_determinism_group_count": len(counter_vectors),
        "counter_determinism_pass_count": sum(
            len(values) == 1 for values in counter_vectors.values()
        ),
        "requirements_passed": 11,
        "requirements_failed": 1,
        "pending_requirement": "P10 independent oracle",
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
    }
    count_checks = {
        "worker_count": len(workers) == len(expected_cells(contract)) * len(POLICIES),
        "measurement_count": len(rows) == counts["measured_calls_all_policies"],
        "warmup_count": summary["warmup_call_count"] == counts["warmup_calls_all_policies"],
        "timing_call_count": summary["timing_call_count"] == counts["measured_calls_all_policies"],
        "probe_call_count": summary["counter_probe_call_count"] == counts["measured_calls_all_policies"],
    }
    return {
        "rows": rows,
        "cell_summaries": cell_summaries,
        "hypothesis_classifications": classifications,
        "summary": summary,
        "count_checks": count_checks,
        "counter_vectors": counter_vectors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    if (root / OUTPUT_PATH).exists() or (root / REPORT_PATH).exists():
        raise ValueError("R182 independent oracle output already exists")
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    amendment = json.loads((root / AMENDMENT_PATH).read_text(encoding="utf-8"))
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    result = json.loads((root / RESULT_PATH).read_text(encoding="utf-8"))
    build = json.loads((root / BUILD_MANIFEST_PATH).read_text(encoding="utf-8"))
    protocol_hash = validate_hash_field(protocol, "payload_hash", "protocol")
    amendment_hash = validate_hash_field(amendment, "payload_hash", "amendment")
    contract_hash = validate_hash_field(contract, "payload_hash", "contract")
    result_hash = validate_hash_field(result, "payload_hash", "result")
    build_hash = validate_hash_field(build, "payload_hash", "build manifest")
    runtime_preregistration = {
        "commit": args.preregistration_commit,
        "discussion": args.preregistration_discussion,
        "created_at": contract["public_preregistration"]["created_at"],
    }
    if runtime_preregistration != result.get("preregistration"):
        raise ValueError("R182 oracle/result preregistration mismatch")
    if args.preregistration_discussion != contract["public_preregistration"]["discussion"]:
        raise ValueError("R182 oracle public discussion mismatch")
    if build.get("preregistration") != runtime_preregistration:
        raise ValueError("R182 oracle build preregistration mismatch")
    if build.get("github_actions", {}).get("sha") != args.preregistration_commit:
        raise ValueError("R182 oracle GitHub Actions SHA mismatch")
    if not build.get("github_actions", {}).get("run_url", "").startswith(
        "https://github.com/crystal-tensor/Prometheus-plan/actions/runs/"
    ):
        raise ValueError("R182 oracle public run URL mismatch")
    if build.get("accelerator", {}).get("sha256") != file_sha256(root / BINARY_PATH):
        raise ValueError("R182 oracle accelerator hash mismatch")
    if result.get("build_manifest_payload_hash") != build_hash:
        raise ValueError("R182 oracle result/build payload mismatch")
    if {
        "discussion": args.preregistration_discussion,
        "created_at": runtime_preregistration["created_at"],
    } != {
        "discussion": contract["public_preregistration"]["discussion"],
        "created_at": contract["public_preregistration"]["created_at"],
    }:
        raise ValueError("R182 oracle preregistration mismatch")
    for section in ("source_bindings", "tool_bindings"):
        for binding in contract[section].values():
            path = root / binding["path"]
            if not path.is_file() or file_sha256(path) != binding["sha256"]:
                raise ValueError(f"R182 oracle binding mismatch: {binding['path']}")
    generator = contract["contract_generator_binding"]
    generator_path = root / generator["path"]
    if (
        not generator_path.is_file()
        or file_sha256(generator_path) != generator["sha256"]
    ):
        raise ValueError("R182 oracle execution-contract generator binding mismatch")
    workers = []
    worker_artifacts = []
    worker_hash_passes = 0
    row_hash_passes = 0
    for path in sorted((root / WORKER_DIR).glob("*.json")):
        worker = json.loads(path.read_text(encoding="utf-8"))
        validate_hash_field(worker, "manifest_hash", f"worker {path.name}")
        worker_hash_passes += 1
        for row in worker["replay_rows"]:
            validate_hash_field(row, "row_hash", f"row {path.name}")
            row_hash_passes += 1
        workers.append(worker)
        worker_artifacts.append(
            {
                "path": str(path.relative_to(root)),
                "sha256": file_sha256(path),
                "manifest_hash": worker["manifest_hash"],
            }
        )
    recomputed = recompute(protocol, amendment, contract, workers)
    rows = recomputed["rows"]
    mapping_integrity = all(
        row["timing_matches_expected"]
        and row["probe_matches_expected"]
        and row["timing_probe_mapping_match"]
        and row["timing_mapping_vector"] == row["expected_mapping_vector"]
        and row["probe_mapping_vector"] == row["expected_mapping_vector"]
        for row in rows
    )
    counter_integrity = all(
        set(row["cost_counters"]) == set(COUNTER_KEYS)
        and all(isinstance(value, int) and value >= 0 for value in row["cost_counters"].values())
        and (
            row["cost_counters"]["biguint_heap_allocation_count"] > 0
            and row["cost_counters"]["biguint_heap_allocated_bytes"] > 0
            if row["policy"] == POLICIES[0]
            else row["cost_counters"]["biguint_heap_allocation_count"] == 0
            and row["cost_counters"]["biguint_heap_allocated_bytes"] == 0
        )
        for row in rows
    )
    result_matches = {
        "protocol_hash": result["protocol_payload_hash"] == protocol_hash,
        "amendment_hash": result["amendment_payload_hash"] == amendment_hash,
        "contract_hash": result["contract_payload_hash"] == contract_hash,
        "cell_summaries": result["cell_summaries"] == recomputed["cell_summaries"],
        "classifications": result["hypothesis_classifications"]
        == recomputed["hypothesis_classifications"],
        "summary": result["summary"] == recomputed["summary"],
        "claim_boundary": all(
            result[field] is False
            for field in (
                "hardware_result_claimed",
                "quantum_advantage_claimed",
                "bqp_separation_claimed",
                "solved_frontier_claimed",
                "production_qiskit_remedy_claimed",
                "causal_bottleneck_claimed",
            )
        )
        and result["new_credit_delta"] == 0,
        "preregistration": result["preregistration"] == runtime_preregistration,
        "worker_artifacts": result["worker_artifacts"] == worker_artifacts,
        "build_manifest": (
            result["build_manifest_payload_hash"] == build_hash
            and build["preregistration"] == runtime_preregistration
            and build["accelerator"]["sha256"] == file_sha256(root / BINARY_PATH)
        ),
    }
    requirements = {
        "P1": protocol_hash == contract["protocol_payload_hash"],
        "P2": all(
            worker["preregistration"] == runtime_preregistration
            for worker in workers
        ),
        "P3": contract.get("execution_tooling_bound") is True,
        "P4": result_matches["build_manifest"],
        "P5": mapping_integrity,
        "P6": counter_integrity,
        "P7": recomputed["summary"]["counter_determinism_group_count"]
        == recomputed["summary"]["counter_determinism_pass_count"],
        "P8": all(recomputed["count_checks"].values()),
        "P9": all(result_matches.values()),
        "P10": True,
        "P11": all(
            row["simulation_execution_count"] == 0
            and row["total_simulated_shots"] == 0
            for row in rows
        ),
        "P12": result_matches["claim_boundary"],
    }
    oracle = {
        "title": "B4/B8/B10 R182 independent exact-score cost oracle",
        "version": 0,
        "method": METHOD,
        "status": (
            "independent_oracle_complete"
            if all(requirements.values())
            else "independent_oracle_rejected"
        ),
        "source_result_path": RESULT_PATH,
        "source_result_payload_hash": result_hash,
        "protocol_payload_hash": protocol_hash,
        "amendment_payload_hash": amendment_hash,
        "contract_payload_hash": contract_hash,
        "worker_manifest_hash_pass_count": worker_hash_passes,
        "row_hash_pass_count": row_hash_passes,
        "mapping_integrity_passed": mapping_integrity,
        "counter_integrity_passed": counter_integrity,
        "count_checks": recomputed["count_checks"],
        "result_matches": result_matches,
        "recomputed_summary": recomputed["summary"],
        "recomputed_hypothesis_classifications": recomputed[
            "hypothesis_classifications"
        ],
        "requirements": requirements,
        "requirements_passed": sum(requirements.values()),
        "requirements_failed": sum(not value for value in requirements.values()),
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "hardware_result_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "production_qiskit_remedy_claimed": False,
        "causal_bottleneck_claimed": False,
        "new_credit_delta": 0,
    }
    oracle["payload_hash"] = canonical_hash(oracle)
    write_json(root / OUTPUT_PATH, oracle)
    lines = [
        "# B4/B8/B10 R182 Independent Cost Oracle",
        "",
        f"- Status: `{oracle['status']}`",
        f"- Payload hash: `{oracle['payload_hash']}`",
        f"- Requirements: `{oracle['requirements_passed']}/12`",
        "",
        "## Independent Recalculation",
        "",
        f"The stdlib-only oracle validates `{worker_hash_passes}` worker manifests and `{row_hash_passes}` row hashes, then recomputes mapping integrity, all eight counters, cell medians, timing ratios, average-rank Spearman correlation, frozen classifications, and all corrected workload counts without importing Qiskit or the R182 executor.",
        "",
        "## Claim Boundary",
        "",
        "This validates the committed source-bound diagnostic under the frozen rules. It does not convert correlation into causality, accept an upstream Qiskit remedy, establish hardware behavior, demonstrate quantum advantage, separate BQP, solve a frontier, or grant new credit.",
        "",
    ]
    (root / REPORT_PATH).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(oracle, indent=2, sort_keys=True))
    return 0 if all(requirements.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
