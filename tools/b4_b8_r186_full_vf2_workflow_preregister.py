#!/usr/bin/env python3
"""Freeze the R186 full VF2 workflow translation experiment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r186_full_vf2_workflow_protocol_v0"
PROTOCOL_PATH = "results/B4_B8_R186_full_vf2_workflow_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R186_full_vf2_workflow_contract_v0.json"
REPORT_PATH = "research/B4_B8_R186_full_vf2_workflow_protocol.md"
SOURCE_PATHS = [
    "results/B4_B8_R184_window_exact_score_v0.json",
    "results/B4_B8_R184_independent_oracle_v0.json",
    "results/B4_B8_R184_window_exact_score_bundle_v0.json",
    "results/B4_B8_R185_macos_arm64_replication_v0.json",
    "results/B4_B8_R185_independent_oracle_v0.json",
    "results/B4_B8_R185_macos_arm64_replication_bundle_v0.json",
    "research/source_lineage/Qiskit_2_4_1_R184_window_exact_score.patch",
    "research/source_lineage/Qiskit_2_4_1_R184_window_exact_pyext.x86_64-linux-gnu.so",
    "research/source_lineage/Qiskit_2_4_1_R185_window_exact_pyext.arm64-darwin.so",
    "research/source_lineage/Qiskit_2_4_1_vf2_source_manifest.json",
]
EXPECTED_PAYLOADS = {
    SOURCE_PATHS[0]: "5b9d5e7f21ffaefb681a2115268242fcecb2d488411817083d278c8fa1f53022",
    SOURCE_PATHS[1]: "88996be1d3c5889088bfc0528c0fde06f3e6571b3875f9bf1e1a8e60b8874bb2",
    SOURCE_PATHS[2]: "378f1e1b4b2ea96d2dae5b667a7b311fafa36fc67dfb69c180a6c084047cadf0",
    SOURCE_PATHS[3]: "09e3f16f0920b7e854d18274cd7f5f8a569859172132627d69584c5100ddd0a3",
    SOURCE_PATHS[4]: "b0e818eb3986a3b0e0fe1c9146537a12794f7d77c6c89c808a22a607b8cdb278",
    SOURCE_PATHS[5]: "0c164aa051ca1eb5c0302f08f8c445d7a2800a74fb9dbd08199a3974e5fa6a18",
    SOURCE_PATHS[9]: "aa50b224ae244f25fbf0fcfa61ee844d7fca298efd7420bc6b70a838f08e2ed2",
}
REQUIRED_EXECUTION_ARTIFACTS = [
    "tools/b4_b8_r186_full_vf2_workflow_replay.py",
    "tools/b4_b8_r186_independent_oracle.py",
    "tools/b4_b8_r186_execution_contract.py",
    "tools/b4_b8_r186_evidence_bundle.py",
    ".github/workflows/r186-full-vf2-workflow-linux-x86-64.yml",
]


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
        raise ValueError(f"R186 {label} payload hash mismatch")
    return str(observed)


def source_binding(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"R186 source binding is missing: {relative}")
    output: dict[str, Any] = {
        "path": relative,
        "sha256": file_sha256(path),
        "size_bytes": path.stat().st_size,
    }
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        for field in ("payload_hash", "manifest_hash"):
            if field in payload:
                output[field] = payload[field]
    return output


def render_report(protocol: dict[str, Any], contract: dict[str, Any]) -> str:
    counts = protocol["frozen_workload"]
    return "\n".join(
        [
            "# B4/B8/B10 R186 Full VF2 Workflow Protocol",
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
            "## Why This Gate Exists",
            "",
            "R184 and R185 timed the complete Rust VF2 search-and-score entry point. They did not time Qiskit's Python `VF2Layout.run`, target resolution, pass configuration, `Layout` construction, property-set writes, or `PassManager` scheduling. R186 measures both surfaces and refuses to call a Rust-core gain a compiler-workflow gain unless the latter survives independently.",
            "",
            "## Frozen Matrix",
            "",
            f"Each architecture runs `{counts['measured_row_count']}` rows across `{counts['workload_cell_count']}` cells. Every row contains BigUint, prefix, and window exact arms on both the direct accelerator surface and the Python PassManager surface. The 12 arm/surface schedules each occur three times per cell, yielding `{counts['measured_timing_call_count_per_platform']}` measured and `{counts['warmup_call_count_per_platform']}` warmup calls per platform.",
            "",
            "## Decision Boundary",
            "",
            "All six outputs must equal the frozen expected mapping in every row. On Linux x86-64 and macOS arm64 separately, window/BigUint must be at most 1.00 on both surfaces. At least 10% of the direct-surface fractional saving must remain after the PassManager boundary. No threshold may be relaxed after timing data open.",
            "",
            "## Claim Boundary",
            "",
            "This is a source-faithful external monkeypatch harness around Qiskit 2.4.1, not an upstream integration or full transpilation benchmark. It uses zero circuit simulations, zero quantum shots, and zero real-backend rows. It cannot establish a production remedy, hardware result, quantum advantage, BQP separation, solved B4/B8/B10 frontier, or new credit.",
            "",
        ]
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for relative in (PROTOCOL_PATH, CONTRACT_PATH, REPORT_PATH):
        if (root / relative).exists():
            raise ValueError(f"R186 output already exists: {relative}")

    for relative, expected in EXPECTED_PAYLOADS.items():
        payload = json.loads((root / relative).read_text(encoding="utf-8"))
        if validate_payload(payload, relative) != expected:
            raise ValueError(f"R186 accepted source changed: {relative}")

    protocol: dict[str, Any] = {
        "title": "B4/B8/B10 R186 full VF2 workflow translation protocol",
        "version": 0,
        "method": METHOD,
        "status": "preregistered_design_unopened",
        "source_target_id": "T-B4-002ef/T-B8-003ej/T-B10-009dv-r186-full-vf2-workflow-protocol",
        "upstream_target_id": "T-B4-002ee/T-B8-003ei/T-B10-009du-r185-result",
        "research_question": "R184/R185 made exact VF2 scoring faster inside the Rust search entry point. Does that advantage survive the actual Python VF2Layout plus PassManager boundary on both Linux x86-64 and macOS arm64, or does orchestration overhead erase it?",
        "source_result_payload_hashes": EXPECTED_PAYLOADS,
        "qiskit_boundary": {
            "version": "2.4.1",
            "source_commit": "0fd015a22b84c9082173597a5d2304dc0aaec08c",
            "python_vf2_layout_relative_path": "qiskit/transpiler/passes/layout/vf2_layout.py",
            "python_vf2_layout_sha256": "0a8fdcaf18c9356e8f701f6438f95608684d13626c1dc2d3e86189d31049f6aa",
            "entrypoint_patch": SOURCE_PATHS[6],
            "strict_direction": False,
            "shuffle_seed": -1,
            "call_limit": 30000000,
            "time_limit": None,
            "max_trials": 250000,
            "score_initial_layout": False,
            "external_error_map_injection": True,
        },
        "platforms": [
            {
                "platform_id": "linux_x86_64",
                "runner": "github_hosted_ubuntu_24_04",
                "python": "3.12",
                "binary_path": SOURCE_PATHS[7],
            },
            {
                "platform_id": "macos_arm64",
                "runner": "clean_public_main_local_runner",
                "python": "3.12",
                "binary_path": SOURCE_PATHS[8],
            },
        ],
        "frozen_arms": {
            "baseline": {
                "policy": "rust_biguint_exact_retained_binary64",
                "entrypoint": "vf2_layout_pass_average_exact_score",
            },
            "reference": {
                "policy": "rust_prefix_initialized_34_limb_exact",
                "entrypoint": "vf2_layout_pass_average_prefix_initialized_exact_score",
            },
            "candidate": {
                "policy": "rust_windowed_4_limb_exact_with_biguint_fallback",
                "entrypoint": "vf2_layout_pass_average_window_exact_score",
            },
        },
        "frozen_surfaces": {
            "accelerator_entrypoint": "Direct patched Rust entry point with the same VF2PassConfiguration values used by VF2Layout.run.",
            "python_passmanager": "Fresh ErrorMap injection pass, VF2Layout pass, and PassManager per call, including target/configuration handling, pass execution, Layout construction, property-set writes, and mapping extraction.",
        },
        "design_preflight_non_evidence": {
            "purpose": "Validate harness feasibility and choose a falsifiable retention threshold before public freezing.",
            "integrity_calls": 111,
            "integrity_failures": 0,
            "integrity_scope": "All 13 cells, 37 subcells, and three exact arms through PassManager once per subcell.",
            "timing_scope": "One standard cell only, 120 exploratory rows, BigUint and window arms, both surfaces.",
            "exploratory_direct_window_to_biguint_ratio": 0.472527015107329,
            "exploratory_passmanager_window_to_biguint_ratio": 0.8898142614205968,
            "exploratory_retained_fraction": 0.20889361490583921,
            "accepted_as_scientific_evidence": False,
        },
        "frozen_workload": {
            "standard_dataset_profile_cells": 9,
            "small_gap_policy_cells": 4,
            "workload_cell_count": 13,
            "subcell_count": 37,
            "arm_count": 3,
            "surface_count": 2,
            "schedule_count": 12,
            "repetitions_per_schedule_per_cell": 3,
            "measured_rows_per_cell": 36,
            "measured_row_count": 468,
            "timing_calls_per_row": 6,
            "measured_timing_call_count_per_platform": 2808,
            "warmup_schedules_per_cell": 12,
            "warmup_calls_per_cell": 72,
            "warmup_call_count_per_platform": 936,
            "total_qiskit_call_count_per_platform": 3744,
            "total_qiskit_call_count_both_platforms": 7488,
        },
        "frozen_hypotheses": [
            {
                "hypothesis_id": "H1-full-boundary-integrity",
                "statement": "Every arm on both timing surfaces equals the frozen expected mapping in every measured row on both architectures.",
            },
            {
                "hypothesis_id": "H2-direct-window-competitiveness",
                "statement": "Window/BigUint aggregate paired median is at most 1.00 on the direct accelerator surface on each architecture.",
                "maximum_ratio": 1.0,
            },
            {
                "hypothesis_id": "H3-passmanager-window-competitiveness",
                "statement": "Window/BigUint aggregate paired median is at most 1.00 through Python VF2Layout plus PassManager on each architecture.",
                "maximum_ratio": 1.0,
            },
            {
                "hypothesis_id": "H4-relative-saving-retention",
                "statement": "At least 10% of the positive direct-surface fractional window saving survives through the PassManager surface on each architecture.",
                "minimum_retained_fraction": 0.1,
                "formula": "(1 - passmanager_window_biguint_ratio) / (1 - direct_window_biguint_ratio)",
            },
            {
                "hypothesis_id": "H5-cross-architecture-workflow-transfer",
                "statement": "H1 through H4 pass independently on both Linux x86-64 and macOS arm64 under the same source patch, workload, schedules, and thresholds.",
            },
        ],
        "acceptance_requirements": [
            "P1 all R184/R185 sources, payloads, binaries, and Qiskit lineage bindings validate",
            "P2 public design commit and Discussion predate both platform executions",
            "P3 a second-stage execution contract binds runner, replay, oracle, bundle, workflow, and landing update",
            "P4 the imported extension and Python VF2Layout source match their platform and frozen hashes",
            "P5 all six mappings equal the expected mapping in every measured row",
            "P6 all 13 cells contain 36 rows and each of 12 schedules occurs three times",
            "P7 each platform records 2,808 measured calls and 936 warmup calls",
            "P8 H1 through H5 follow the frozen thresholds without relaxation",
            "P9 a standard-library oracle validates all row/worker hashes, counts, ratios, and classifications",
            "P10 Linux and macOS results remain separately auditable before cross-platform aggregation",
            "P11 simulation execution count, quantum shot count, and real-backend row count remain zero",
            "P12 upstream-integration, full-transpilation, production-remedy, hardware, advantage, BQP, solved-frontier, and new-credit fields remain false or zero",
        ],
        "claim_boundary": {
            "full_workflow_gain_claimed_before_execution": False,
            "external_monkeypatch_harness": True,
            "upstream_patch_accepted": False,
            "full_transpilation_pipeline_benchmarked": False,
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
        "contract_id": "B4-B8-R186-full-vf2-workflow-design-contract-v0",
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
        "result_paths_must_be_absent": [
            "results/B4_B8_R186_full_vf2_workflow_linux_x86_64_v0.json",
            "results/B4_B8_R186_full_vf2_workflow_macos_arm64_v0.json",
            "results/B4_B8_R186_independent_oracle_v0.json",
            "results/B4_B8_R186_full_vf2_workflow_bundle_v0.json",
        ],
        "claim_boundary": protocol["claim_boundary"],
    }
    contract["payload_hash"] = canonical_hash(contract)
    write_json(root / CONTRACT_PATH, contract)
    (root / REPORT_PATH).write_text(
        render_report(protocol, contract), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "protocol": PROTOCOL_PATH,
                "protocol_payload_hash": protocol["payload_hash"],
                "design_contract": CONTRACT_PATH,
                "design_contract_payload_hash": contract["payload_hash"],
                "status": protocol["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
