#!/usr/bin/env python3
"""Freeze the R185 macOS arm64 replication before execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r185_macos_arm64_replication_protocol_v0"
PROTOCOL_PATH = "results/B4_B8_R185_macos_arm64_replication_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R185_macos_arm64_replication_contract_v0.json"
REPORT_PATH = "research/B4_B8_R185_macos_arm64_replication_protocol.md"
SOURCE_PATHS = [
    "results/B4_B8_R184_window_exact_score_protocol_v0.json",
    "benchmarks/B4_B8_R184_window_exact_score_contract_v0.json",
    "benchmarks/B4_B8_R184_window_exact_score_execution_contract_v0.json",
    "results/B4_B8_R184_window_exact_score_v0.json",
    "results/B4_B8_R184_independent_oracle_v0.json",
    "results/B4_B8_R184_window_exact_score_bundle_v0.json",
    "research/source_lineage/Qiskit_2_4_1_R184_window_exact_score.patch",
    "research/source_lineage/Qiskit_2_4_1_R184_window_exact_linux_x86_64_build_manifest.json",
]
REQUIRED_EXECUTION_ARTIFACTS = [
    "research/source_lineage/Qiskit_2_4_1_R184_window_exact_score.patch",
    "tools/b4_b8_r185_macos_arm64_replay.py",
    "tools/b4_b8_r185_independent_oracle.py",
    "tools/b4_b8_r185_macos_arm64_build.py",
    "tools/b4_b8_r185_macos_arm64_bundle.py",
]
EXPECTED_R184_PAYLOADS = {
    SOURCE_PATHS[0]: "6282eebdfa41ff94dfbe4eed4b61fc2030f02bec5eea6bb360b9fa27c890a999",
    SOURCE_PATHS[1]: "e0c226bf419da94dc9e5afa3a249eabd085505c6b5328b7a2b3af1a8f6a4d108",
    SOURCE_PATHS[2]: "afd219391029c7e39eacffd185d3bf1402147ad713564aaba053e38ee3bc4280",
    SOURCE_PATHS[3]: "5b9d5e7f21ffaefb681a2115268242fcecb2d488411817083d278c8fa1f53022",
    SOURCE_PATHS[4]: "88996be1d3c5889088bfc0528c0fde06f3e6571b3875f9bf1e1a8e60b8874bb2",
    SOURCE_PATHS[5]: "378f1e1b4b2ea96d2dae5b667a7b311fafa36fc67dfb69c180a6c084047cadf0",
    SOURCE_PATHS[7]: "3f1ed26ad15be26ee07777c46e2335fdc4d8338696f3cb58dd8c6f8bc06c524d",
}


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def validate_payload(payload: dict[str, Any], label: str) -> str:
    body = dict(payload)
    observed = body.pop("payload_hash", None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R185 {label} payload hash mismatch")
    return str(observed)


def source_binding(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"R185 source binding is missing: {relative}")
    output: dict[str, Any] = {"path": relative, "sha256": file_sha256(path)}
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        for field in ("payload_hash", "manifest_hash"):
            if field in payload:
                output[field] = payload[field]
    return output


def report(protocol: dict[str, Any], contract: dict[str, Any]) -> str:
    counts = protocol["frozen_workload"]
    return "\n".join(
        [
            "# B4/B8/B10 R185 macOS arm64 Replication Protocol",
            "",
            "- Status: `preregistered_design_unopened`",
            f"- Protocol payload hash: `{protocol['payload_hash']}`",
            f"- Design contract payload hash: `{contract['payload_hash']}`",
            "- Scientific execution: unopened",
            "",
            "## Heuristic Question",
            "",
            protocol["research_question"],
            "",
            "## Frozen Cross-Architecture Pairing",
            "",
            f"The macOS arm64 matrix repeats the exact R184 Linux workload: `{counts['measured_triplet_count']}` same-process BigUint/prefix/window triplets across `{counts['workload_cell_count']}` cells. All six arm orders appear `{counts['repetitions_per_order_per_cell']}` times per cell, so platform is changed without changing workload or scheduler position balance.",
            "",
            "## Decision Boundary",
            "",
            "The macOS build must preserve every expected mapping, stay at four compact limbs or fewer, remain at 64 bytes or fewer, and avoid fallback on the frozen workload. The same 0.90 window/prefix and 1.00 window/BigUint ceilings are retained. Cross-architecture transfer is accepted only if the committed Linux result and the new macOS result both pass H1-H4 without changing the patch, inputs, or thresholds.",
            "",
            "## Claim Boundary",
            "",
            "This is a preregistered classical compiler cross-architecture replication. It is not a universal architecture theorem, upstream Qiskit patch, full-domain performance theorem, production remedy, hardware result, quantum advantage, BQP separation, solved B4/B8/B10 frontier, or new credit.",
            "",
        ]
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for relative in (PROTOCOL_PATH, CONTRACT_PATH, REPORT_PATH):
        if (root / relative).exists():
            raise ValueError(f"R185 output already exists: {relative}")

    for relative, expected in EXPECTED_R184_PAYLOADS.items():
        payload = json.loads((root / relative).read_text(encoding="utf-8"))
        if validate_payload(payload, relative) != expected:
            raise ValueError(f"R185 accepted R184 boundary changed: {relative}")

    protocol: dict[str, Any] = {
        "title": "B4/B8/B10 R185 macOS arm64 exact-score replication protocol",
        "version": 0,
        "method": METHOD,
        "status": "preregistered_design_unopened",
        "source_target_id": "T-B4-002ec/T-B8-003eg/T-B10-009ds-r185-macos-arm64-replication-protocol",
        "upstream_target_id": "T-B4-002ea/T-B8-003ee/T-B10-009dq-r184-result",
        "research_question": "R184 preserved all 468 mappings and reached 0.771535x versus prefix plus 0.814726x versus BigUint on Linux x86-64. Does the same exact representation clear the unchanged integrity, compactness, and performance gates on macOS arm64, or was the apparent win architecture-specific?",
        "source_result_payload_hashes": EXPECTED_R184_PAYLOADS,
        "platform_contract": {
            "runner": "clean_public_main_local_runner",
            "system": "Darwin",
            "machine": "arm64",
            "python": "3.12",
            "qiskit": "2.4.1",
            "source_commit": "0fd015a22b84c9082173597a5d2304dc0aaec08c",
            "requires_remote_main_equal_runner_commit": True,
            "requires_public_discussion_before_execution": True,
        },
        "frozen_arms": {
            "baseline": "rust_biguint_exact_retained_binary64",
            "reference": "rust_prefix_initialized_34_limb_exact",
            "candidate": "rust_windowed_4_limb_exact_with_biguint_fallback",
        },
        "frozen_workload": {
            "standard_dataset_profile_cells": 9,
            "small_gap_policy_cells": 4,
            "workload_cell_count": 13,
            "worker_count": 13,
            "candidate_compact_limb_capacity": 4,
            "candidate_maximum_object_size_bytes": 64,
            "arm_order_permutation_count": 6,
            "repetitions_per_order_per_cell": 6,
            "warmups_per_arm_per_cell": 9,
            "measured_triplets_per_cell": 36,
            "measured_triplet_count": 468,
            "timing_call_count": 1404,
            "counter_probe_call_count": 468,
            "warmup_call_count": 351,
            "total_qiskit_function_call_count": 2223,
        },
        "required_counter_keys": [
            "leaf_construction_count",
            "window_combine_count",
            "window_compare_count",
            "compact_result_count",
            "fallback_transition_count",
            "wide_combine_count",
            "maximum_window_limb_count",
            "score_object_size_bytes",
        ],
        "frozen_hypotheses": [
            {
                "hypothesis_id": "H1-exact-integrity",
                "statement": "BigUint, prefix, window timing, and window probe mappings equal the frozen expected mapping in every triplet.",
            },
            {
                "hypothesis_id": "H2-compact-common-path",
                "statement": "The window representation stays within four limbs and 64 bytes, with zero fallback transitions and zero wide combines on the frozen workload.",
                "maximum_window_limb_count": 4,
                "maximum_score_object_size_bytes": 64,
            },
            {
                "hypothesis_id": "H3-representation-speedup",
                "statement": "The window candidate has an aggregate paired median elapsed ratio at most 0.90 against the prefix-initialized exact reference after H1 and H2 pass.",
                "maximum_candidate_to_reference_paired_median_ratio": 0.90,
            },
            {
                "hypothesis_id": "H4-biguint-competitiveness",
                "statement": "The window candidate has an aggregate paired median elapsed ratio at most 1.00 against the BigUint exact denominator after H1 and H2 pass.",
                "maximum_candidate_to_baseline_paired_median_ratio": 1.00,
                "required_cell_count": 13,
                "required_count_per_order_per_cell": 6,
            },
            {
                "hypothesis_id": "H5-cross-architecture-transfer",
                "statement": "The committed Linux x86-64 result and the new macOS arm64 result both support H1 through H4 under the identical source patch, workload, and thresholds.",
                "required_linux_result_payload_hash": EXPECTED_R184_PAYLOADS[SOURCE_PATHS[3]],
                "required_linux_oracle_payload_hash": EXPECTED_R184_PAYLOADS[SOURCE_PATHS[4]],
                "required_supported_hypothesis_ids": [
                    "H1-exact-integrity",
                    "H2-compact-common-path",
                    "H3-representation-speedup",
                    "H4-biguint-competitiveness",
                ],
            },
        ],
        "acceptance_requirements": [
            "P1 all accepted R184 payloads and source bindings validate",
            "P2 the public Discussion and design commit predate every R185 build and worker",
            "P3 a second-stage execution contract hash-binds the unchanged R184 patch plus the R185 runner, oracle, build, and bundle",
            "P4 cargo format, check, R180/R182/R183/R184 tests, release build, Mach-O arm64 validation, and isolated import smoke pass",
            "P5 all three timing mappings and the candidate probe mapping equal the expected mapping for every triplet",
            "P6 all eight candidate counters are present, nonnegative, and deterministic by subcell",
            "P7 candidate compactness, fallback, and object-size fields follow H2 without relaxation",
            "P8 all 13 cells contain 36 triplets, six of every arm order, plus 9 warmups per arm",
            "P9 H1 through H5 follow the frozen thresholds without relaxation",
            "P10 a stdlib-only oracle recomputes hashes, counts, paired ratios, and cross-platform classifications",
            "P11 the build starts from a clean commit already published as remote main",
            "P12 simulation execution count and quantum shot count remain zero",
            "P13 universal-platform, production-remedy, hardware, advantage, BQP, solved-frontier, and new-credit fields remain false or zero",
        ],
        "claim_boundary": {
            "representation_speedup_claimed_before_execution": False,
            "cross_architecture_transfer_claimed_before_execution": False,
            "universal_architecture_performance_claimed": False,
            "full_domain_compactness_claimed": False,
            "causal_bottleneck_claimed": False,
            "upstream_patch_accepted": False,
            "production_qiskit_remedy_claimed": False,
            "hardware_result_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "solved_frontier_claimed": False,
            "new_credit_delta": 0,
        },
    }
    protocol["payload_hash"] = canonical_hash(protocol)
    write_json(root / PROTOCOL_PATH, protocol)

    tool_path = Path(__file__).resolve()
    contract: dict[str, Any] = {
        "contract_id": "B4-B8-R185-macos-arm64-replication-design-contract-v0",
        "status": "design_frozen_execution_tooling_unbound",
        "execution_started": False,
        "execution_tooling_bound": False,
        "protocol_path": PROTOCOL_PATH,
        "protocol_payload_hash": protocol["payload_hash"],
        "source_bindings": {
            f"source_{index:02d}": source_binding(root, relative)
            for index, relative in enumerate(SOURCE_PATHS, start=1)
        },
        "design_tool_binding": {
            "path": str(tool_path.relative_to(root)),
            "sha256": file_sha256(tool_path),
        },
        "required_before_execution": REQUIRED_EXECUTION_ARTIFACTS,
        "required_before_execution_count": len(REQUIRED_EXECUTION_ARTIFACTS),
        "planned_result_paths": [
            "results/B4_B8_R185_macos_arm64_replication_v0.json",
            "results/B4_B8_R185_independent_oracle_v0.json",
            "results/B4_B8_R185_macos_arm64_replication_bundle_v0.json",
            "research/B4_B8_R185_macos_arm64_replication.md",
            "research/B4_B8_R185_independent_oracle.md",
        ],
    }
    contract["payload_hash"] = canonical_hash(contract)
    write_json(root / CONTRACT_PATH, contract)
    (root / REPORT_PATH).write_text(report(protocol, contract), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": protocol["status"],
                "protocol_payload_hash": protocol["payload_hash"],
                "contract_payload_hash": contract["payload_hash"],
                "measured_triplet_count": protocol["frozen_workload"][
                    "measured_triplet_count"
                ],
                "total_qiskit_function_call_count": protocol["frozen_workload"][
                    "total_qiskit_function_call_count"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
