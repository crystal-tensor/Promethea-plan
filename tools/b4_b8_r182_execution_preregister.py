#!/usr/bin/env python3
"""Bind the R182 execution toolchain after the public protocol amendment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PROTOCOL_PATH = "results/B4_B8_R182_score_cost_attribution_protocol_v0.json"
AMENDMENT_PATH = (
    "results/B4_B8_R182_score_cost_attribution_protocol_amendment_v1.json"
)
DESIGN_CONTRACT_PATH = (
    "benchmarks/B4_B8_R182_score_cost_attribution_contract_v0.json"
)
R181_CONTRACT_PATH = "benchmarks/B4_B8_R181_active_limb_contract_v0.json"
OUTPUT_PATH = (
    "benchmarks/B4_B8_R182_score_cost_attribution_execution_contract_v0.json"
)
REPORT_PATH = "research/B4_B8_R182_score_cost_attribution_execution_contract.md"
TOOL_PATHS = [
    "research/source_lineage/Qiskit_2_4_1_R182_score_cost_attribution.patch",
    "tools/b4_b8_r182_score_cost_attribution_replay.py",
    "tools/b4_b8_r182_independent_cost_oracle.py",
    "tools/b4_b8_r182_linux_x86_64_build.py",
    "tools/b4_b8_r182_linux_x86_64_bundle.py",
    ".github/workflows/r182-score-cost-attribution-linux-x86-64.yml",
]
DIRECT_SOURCE_PATHS = [
    PROTOCOL_PATH,
    AMENDMENT_PATH,
    DESIGN_CONTRACT_PATH,
    R181_CONTRACT_PATH,
    "results/B4_B8_R181_active_limb_protocol_v0.json",
    "results/B4_B8_R181_active_limb_replay_v0.json",
    "results/B4_B8_R181_independent_active_limb_oracle_v0.json",
    "results/B4_B8_R181_active_limb_bundle_manifest_v0.json",
    "tools/b4_b8_r181_active_limb_replay.py",
    "tools/b4_b8_r119_private_observable_bundle_gate.py",
    "tools/b4_b8_r126_calibration_attribution_ledger.py",
    "tools/b4_b8_r153_independent_seed_replication_holdout.py",
    "tools/b4_b8_r154_deterministic_automatic_replay.py",
    "tools/b4_b8_r160_deterministic_error_map_remediation.py",
]
EXPECTED_HASHES = {
    PROTOCOL_PATH: "c4108dd5cab9d33cfe6a69f7822892f8ae4a151d6d3c4b5f8f41c2bd297dbe03",
    AMENDMENT_PATH: "747065513098d25f90e977b5d548219ca0d6944dd8b40840f97c17e55c348dfb",
    DESIGN_CONTRACT_PATH: "065799ba197dc8cd81a7138b1e821848540fe7f1d559da3f26fa1f1e604b700a",
}
COUNTER_DEFINITIONS = {
    "leaf_construction_count": "Number of retained-binary64 score leaves constructed by the instrumented score type.",
    "destination_zeroed_limb_count": "Number of u64 destination limbs explicitly zero-initialized by fixed-34 or active-limb constructors, identities, and combines; BigUint records zero for this fixed-array channel.",
    "arithmetic_limb_visit_count": "Algorithmic u64 limbs visited by score addition: 34 for every fixed combine and max(left_used,right_used) for active-limb and BigUint probes.",
    "comparison_limb_visit_count": "Algorithmic u64 value limbs inspected before comparison resolves; differing used lengths require zero value-limb visits.",
    "carry_extension_count": "Number of additions whose result uses more u64 limbs than both operands.",
    "maximum_used_limb_count": "Maximum numerical u64 limb length observed in a score value during the probe.",
    "biguint_heap_allocation_count": "Successful System allocator alloc, alloc_zeroed, or realloc events while the thread-local BigUint construction/addition guard is enabled.",
    "biguint_heap_allocated_bytes": "Cumulative requested bytes for those guarded successful BigUint allocator events; deallocation is not subtracted.",
    "elapsed_nanoseconds": "Wall-clock nanoseconds for the paired uninstrumented timing call only; the counter probe is excluded.",
}


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_payload(payload: dict[str, Any], label: str) -> str:
    body = dict(payload)
    observed = body.pop("payload_hash", None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R182 {label} payload hash mismatch")
    return str(observed)


def binding(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"R182 execution binding is missing: {relative}")
    output: dict[str, Any] = {"path": relative, "sha256": file_sha256(path)}
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        for field in ("payload_hash", "manifest_hash"):
            if field in payload:
                output[field] = payload[field]
    return output


def cells(r181: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    for dataset in r181["datasets"]:
        for profile in r181["standard_profiles"]:
            output.append(
                {
                    "cell_id": f"standard__{dataset['dataset_id']}__{profile}",
                    "kind": "standard",
                    "dataset_id": dataset["dataset_id"],
                    "profile_id": profile,
                }
            )
    for mode in r181["small_gap_modes"]:
        output.append(
            {"cell_id": f"small-gap__{mode}", "kind": "small-gap", "mode": mode}
        )
    return output


def report(contract: dict[str, Any]) -> str:
    counts = contract["measurement_pair_contract"]
    return "\n".join(
        [
            "# B4/B8/B10 R182 Execution Contract",
            "",
            "- Status: `execution_tooling_bound_measurement_unopened`",
            f"- Contract payload hash: `{contract['payload_hash']}`",
            f"- Tool bindings: `{len(contract['tool_bindings'])}`",
            f"- Source bindings: `{len(contract['source_bindings'])}`",
            "- Scientific execution: unopened",
            "",
            "## Paired Measurement",
            "",
            f"Each of the `{counts['measured_pairs_all_policies']}` frozen measurements contains an uninstrumented timing call followed by a separate counter probe. Their mappings must agree exactly. Probe time is excluded from `elapsed_nanoseconds`. The matrix contains `{counts['expected_worker_count']}` isolated workers and `{counts['total_qiskit_function_calls']}` total Qiskit function calls including warmups.",
            "",
            "## Allocation Boundary",
            "",
            "BigUint allocation counts are actual successful System allocator events observed only while a thread-local guard surrounds BigUint score construction and addition. The allocator wrapper remains compiled into the timing binary with tracking disabled; its residual branch overhead is not separately estimated, so H2 can support or reject only a source-bound pressure classification, never a production causal claim.",
            "",
            "## Claim Boundary",
            "",
            "The instrumentation patch, runner, independent oracle, Linux build, bundle tool, and public workflow are hash-bound. No build or measurement has started. This contract is not a cost result, Qiskit remedy, hardware result, quantum advantage, BQP separation, solved frontier, or new credit.",
            "",
        ]
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for relative in (OUTPUT_PATH, REPORT_PATH):
        if (root / relative).exists():
            raise ValueError(f"R182 execution output already exists: {relative}")
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    amendment = json.loads((root / AMENDMENT_PATH).read_text(encoding="utf-8"))
    design = json.loads((root / DESIGN_CONTRACT_PATH).read_text(encoding="utf-8"))
    r181_contract = json.loads((root / R181_CONTRACT_PATH).read_text(encoding="utf-8"))
    r181 = json.loads(
        (root / "results/B4_B8_R181_active_limb_protocol_v0.json").read_text(
            encoding="utf-8"
        )
    )
    observed = {
        PROTOCOL_PATH: validate_payload(protocol, "protocol"),
        AMENDMENT_PATH: validate_payload(amendment, "amendment"),
        DESIGN_CONTRACT_PATH: validate_payload(design, "design contract"),
    }
    if observed != EXPECTED_HASHES:
        raise ValueError("R182 execution sources do not match the frozen design")
    if amendment.get("execution_started") is not False:
        raise ValueError("R182 amendment no longer records an unopened experiment")
    required = set(design["required_before_execution"])
    if required != set(TOOL_PATHS):
        raise ValueError("R182 design and execution tool lists differ")
    inherited_paths = [
        row["path"] for row in r181_contract.get("source_bindings", {}).values()
    ]
    source_paths = list(dict.fromkeys([*DIRECT_SOURCE_PATHS, *inherited_paths]))
    workload_cells = cells(r181)
    corrected = amendment["corrected_workload_counts"]
    measurement_contract = {
        "pair_order": ["uninstrumented_timing", "counter_probe"],
        "probe_elapsed_excluded_from_timing": True,
        "mapping_equality_required_within_pair": True,
        "cells_per_policy": corrected["cells_per_policy"],
        "exact_policy_count": corrected["exact_policy_count"],
        "warmups_per_cell_policy": corrected["warmups_per_cell"],
        "measured_pairs_per_cell_policy": corrected["measured_replays_per_cell"],
        "measured_pairs_per_policy": corrected["measured_calls_per_policy"],
        "warmups_per_policy": corrected["warmup_calls_per_policy"],
        "measured_pairs_all_policies": corrected["measured_calls_all_policies"],
        "warmups_all_policies": corrected["warmup_calls_all_policies"],
        "timing_calls_all_policies": corrected["measured_calls_all_policies"],
        "counter_probe_calls_all_policies": corrected[
            "measured_calls_all_policies"
        ],
        "expected_worker_count": len(workload_cells)
        * corrected["exact_policy_count"],
        "total_qiskit_function_calls": corrected["warmup_calls_all_policies"]
        + 2 * corrected["measured_calls_all_policies"],
        "small_gap_case_schedule": "replay_index_modulo_seven_in_frozen_R181_case_order",
        "counter_determinism_group": "cell_id_policy_subcell_id",
    }
    contract: dict[str, Any] = {
        "title": "B4/B8/B10 R182 score-cost attribution execution contract",
        "version": 0,
        "contract_id": "B4-B8-R182-score-cost-attribution-execution-contract-v0",
        "status": "execution_tooling_bound_measurement_unopened",
        "execution_tooling_bound": True,
        "execution_started": False,
        "protocol_path": PROTOCOL_PATH,
        "protocol_payload_hash": protocol["payload_hash"],
        "amendment_path": AMENDMENT_PATH,
        "amendment_payload_hash": amendment["payload_hash"],
        "design_contract_path": DESIGN_CONTRACT_PATH,
        "design_contract_payload_hash": design["payload_hash"],
        "public_preregistration": {
            "discussion": "https://github.com/crystal-tensor/Prometheus-plan/discussions/272",
            "created_at": "2026-07-20T18:00:03Z",
            "correction_comment_created_at": "2026-07-20T18:17:13Z",
            "amendment_public_commit": "8ec24b221e2e2690ffb8c80fe73ce0e31a019a7a",
        },
        "platform_contract": protocol["platform_contract"],
        "process_environment": r181["process_environment"],
        "policies": protocol["frozen_policies"],
        "workload_matrix": {
            "cells": workload_cells,
            "cell_count": len(workload_cells),
            "small_gap_cases": r181["small_gap_cases"],
        },
        "measurement_pair_contract": measurement_contract,
        "counter_definitions": COUNTER_DEFINITIONS,
        "allocator_instrumentation_boundary": {
            "allocator": "std::alloc::System",
            "tracking_scope": "thread_local_guard_around_instrumented_BigUint_construction_and_addition",
            "counted_events": ["alloc", "alloc_zeroed", "realloc"],
            "deallocation_subtracted": False,
            "successful_allocations_only": True,
            "timing_call_tracking_enabled": False,
            "allocator_wrapper_compiled_into_timing_binary": True,
            "wrapper_branch_overhead_separately_estimated": False,
            "causal_production_claim_allowed": False,
        },
        "aggregation_rules": {
            "H1_arithmetic_visit_reduction": "1_minus_active_total_over_fixed_total",
            "H1_full_width_initialization": "active_total_destination_zeroed_limbs_equals_fixed_total",
            "H1_speed_failure": "aggregate_active_median_over_fixed_median_greater_than_0.90",
            "H2_allocation_pressure": "per_cell_median_biguint_heap_allocated_bytes",
            "H2_timing_gap": "per_cell_biguint_median_nanoseconds_minus_active_median_nanoseconds",
            "H2_correlation": "average_rank_spearman_across_13_cells",
            "H2_support": "positive_allocation_pressure_all_cells_and_spearman_at_least_0.60",
            "H3_coverage": "all_13_cells_reported",
        },
        "source_bindings": {
            f"source_{index:03d}": binding(root, relative)
            for index, relative in enumerate(source_paths, start=1)
        },
        "tool_bindings": {
            f"tool_{index:02d}": binding(root, relative)
            for index, relative in enumerate(TOOL_PATHS, start=1)
        },
        "contract_generator_binding": binding(
            root, "tools/b4_b8_r182_execution_preregister.py"
        ),
        "result_paths_must_be_absent": [
            "research/B4_B8_R182_score_cost_attribution.md",
            "research/B4_B8_R182_independent_cost_oracle.md",
            "results/B4_B8_R182_score_cost_attribution_replay",
            "results/B4_B8_R182_score_cost_attribution_v0.json",
            "results/B4_B8_R182_independent_cost_oracle_v0.json",
            "results/B4_B8_R182_score_cost_attribution_bundle_v0.json",
        ],
        "build_output_paths_created_before_replay": [
            "research/source_lineage/Qiskit_2_4_1_R182_score_cost_pyext.x86_64-linux-gnu.so",
            "research/source_lineage/Qiskit_2_4_1_R182_score_cost_linux_x86_64_build_manifest.json",
            "research/source_lineage/R182_score_cost_linux_x86_64_build_logs",
        ],
        "claim_boundary": {
            "cost_attribution_claimed_before_execution": False,
            "causal_bottleneck_claimed": False,
            "production_qiskit_remedy_claimed": False,
            "hardware_result_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "solved_frontier_claimed": False,
            "new_credit_delta": 0,
        },
    }
    contract["payload_hash"] = canonical_hash(contract)
    path = root / OUTPUT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (root / REPORT_PATH).write_text(report(contract), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": contract["status"],
                "payload_hash": contract["payload_hash"],
                "source_binding_count": len(contract["source_bindings"]),
                "tool_binding_count": len(contract["tool_bindings"]),
                **measurement_contract,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
