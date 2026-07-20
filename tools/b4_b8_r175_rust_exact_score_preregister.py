#!/usr/bin/env python3
"""Freeze the R175 integrated Rust exact-score experiment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r154_deterministic_automatic_replay import canonical_hash


METHOD = "b4_b8_r175_rust_exact_score_protocol_v0"
BUILD_MANIFEST_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R175_rust_exact_score_build_manifest.json"
)
PROTOCOL_PATH = "results/B4_B8_R175_rust_exact_score_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R175_rust_exact_score_contract_v0.json"
REPORT_PATH = "research/B4_B8_R175_rust_exact_score_protocol.md"
RESULT_PATH = "results/B4_B8_R175_rust_exact_score_v0.json"
RESULT_REPORT_PATH = "research/B4_B8_R175_rust_exact_score.md"
ORACLE_PATH = "results/B4_B8_R175_independent_rust_exact_oracle_v0.json"
ORACLE_REPORT_PATH = "research/B4_B8_R175_independent_rust_exact_oracle.md"
WORKER_DIR = "results/B4_B8_R175_rust_exact_score"
PATCH_PATH = "research/source_lineage/Qiskit_2_4_1_R175_rust_exact_score.patch"
BINARY_PATH = (
    "research/source_lineage/"
    "Qiskit_2_4_1_R175_rust_exact_score_accelerate.cpython-312-darwin.so"
)

DATASETS = [
    {
        "dataset_id": "r169_non_tie",
        "input_path": "benchmarks/B4_B8_R169_target_compatible_candidate_v0.qasm",
        "protocol_path": "results/B4_B8_R169_target_compatible_candidate_protocol_v0.json",
        "result_path": "results/B4_B8_R169_target_compatible_candidate_replay_v0.json",
        "worker_directory": "results/B4_B8_R169_target_compatible_candidate_replay",
        "expected_relation": "exact_preserves_source_non_tie",
    },
    {
        "dataset_id": "r170_path_true_tie",
        "input_path": "benchmarks/B4_B8_R170_near_tie_candidate_v0.qasm",
        "protocol_path": "results/B4_B8_R170_near_tie_candidate_protocol_v0.json",
        "result_path": "results/B4_B8_R170_near_tie_candidate_replay_v0.json",
        "worker_directory": "results/B4_B8_R170_near_tie_candidate_replay",
        "expected_relation": "exact_repairs_source_one_ulp_false_winner",
    },
    {
        "dataset_id": "r172_t_tree_true_tie",
        "input_path": "benchmarks/B4_B8_R172_second_near_tie_candidate_v0.qasm",
        "protocol_path": "results/B4_B8_R172_second_near_tie_candidate_protocol_v0.json",
        "result_path": "results/B4_B8_R172_second_near_tie_candidate_replay_v0.json",
        "worker_directory": "results/B4_B8_R172_second_near_tie_candidate_replay",
        "expected_relation": "exact_repairs_source_one_ulp_false_winner",
    },
]
PROFILES = [
    "native_hashset_order",
    "ascending_sorted_order",
    "descending_sorted_order",
]
SMALL_GAP_MODES = [
    "ascending_f64",
    "descending_f64",
    "math_fsum",
    "exact_binary_fraction",
]
SMALL_GAP_CASES = [
    "edge_0_1_m008ulp",
    "edge_0_1_m001ulp",
    "edge_1_0_p001ulp",
    "edge_1_0_p008ulp",
    "edge_1_2_m001ulp",
    "edge_2_1_p001ulp",
    "edge_2_1_p008ulp",
]
TOOL_PATHS = [
    "tools/b4_b8_r175_rust_exact_score_preregister.py",
    "tools/b4_b8_r175_rust_exact_score_replay.py",
    "tools/b4_b8_r175_independent_rust_exact_oracle.py",
]


def source_binding(root: Path, path: str) -> dict[str, Any]:
    payload: dict[str, Any] = {"path": path, "sha256": file_sha256(root / path)}
    if path.endswith(".json"):
        parsed = json.loads((root / path).read_text(encoding="utf-8"))
        for key in (
            "payload_hash",
            "manifest_payload_hash",
            "case_analysis_payload_hash",
        ):
            if key in parsed:
                payload[key] = parsed[key]
    return payload


def build_report(protocol: dict[str, Any], contract: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# B4/B8/B10 R175 Integrated Rust Exact-Score Protocol",
            "",
            "- Status: `preregistered_unopened`",
            f"- Protocol payload hash: `{protocol['payload_hash']}`",
            f"- Contract payload hash: `{contract['payload_hash']}`",
            "",
            "## Research Question",
            "",
            "Can an exact retained-binary64 accumulator inside Qiskit's compiled Rust VF2 path repair true ties and sub-ULP non-ties while preserving ordinary mappings at bounded runtime and memory cost?",
            "",
            "## Frozen Matrix",
            "",
            "- R169 ordinary non-tie: 3 profiles x 64 calls x 2 policies.",
            "- R170 first true-tie graph: 3 profiles x 64 calls x 2 policies.",
            "- R172 second true-tie graph: 3 profiles x 64 calls x 2 policies.",
            "- R157/R160 sub-ULP controls: 4 ErrorMap modes x 7 cases x 8 calls x 2 policies.",
            "- Total recorded calls: 1,600; each policy contributes 800.",
            "- Each of 26 isolated workers performs 16 unrecorded warmups before measurement.",
            "",
            "## Frozen Performance Gates",
            "",
            "- Every exact/source median-time ratio must be at most 3.0.",
            "- The aggregate exact/source median-time ratio must be at most 2.5.",
            "- The maximum exact/source worker peak-RSS ratio must be at most 1.25.",
            "",
            "## Claim Boundary",
            "",
            "This is a source-bound experimental Rust entry point built from Qiskit 2.4.1 commit `0fd015a22b84c9082173597a5d2304dc0aaec08c`. It is not an upstream-accepted or production Qiskit patch, a confirmed Qiskit bug, a route-quality result, a hardware result, quantum advantage, BQP separation, a solved frontier, or new credit.",
            "",
        ]
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output_paths = [
        BUILD_MANIFEST_PATH,
        PROTOCOL_PATH,
        CONTRACT_PATH,
        REPORT_PATH,
    ]
    for path in output_paths:
        if (root / path).exists():
            raise ValueError(f"R175 preregistration output already exists: {path}")
    forbidden = [
        RESULT_PATH,
        RESULT_REPORT_PATH,
        ORACLE_PATH,
        ORACLE_REPORT_PATH,
        WORKER_DIR,
    ]
    for path in forbidden:
        if (root / path).exists():
            raise ValueError(f"R175 experimental evidence already exists: {path}")

    build_manifest = {
        "title": "Qiskit 2.4.1 R175 Rust exact-score build manifest",
        "version": 0,
        "status": "compiled_pre_registration_build",
        "official_source": {
            "repository": "https://github.com/Qiskit/qiskit",
            "release": "2.4.1",
            "commit": "0fd015a22b84c9082173597a5d2304dc0aaec08c",
        },
        "patch": source_binding(root, PATCH_PATH),
        "accelerator": {
            **source_binding(root, BINARY_PATH),
            "size_bytes": (root / BINARY_PATH).stat().st_size,
            "platform": "macOS arm64 / CPython 3.12 extension-module build",
        },
        "patched_source_hashes": {
            "crates/transpiler/Cargo.toml": "0e04369fa263fc8f12495bb091c16858c077b216bf3dad7324a59a95b7a7fa26",
            "crates/transpiler/src/passes/vf2/vf2_layout.rs": "9aaeab2673a602ac1a74643a4bb6f8743131d16499bfc8a7729516bf73f191cd",
        },
        "build_checks": [
            {"command": "cargo fmt --all -- --check", "returncode": 0},
            {"command": "cargo check -p qiskit-transpiler --lib", "returncode": 0},
            {"command": "git diff --check", "returncode": 0},
            {
                "command": "cargo rustc --lib --manifest-path crates/pyext/Cargo.toml --release --features cache_pygates,pyo3/extension-module --crate-type cdylib",
                "returncode": 0,
            },
        ],
        "packaging_note": "setup.py build_rust produced the release artifact but its setuptools-rust install adapter raised a post-build signature TypeError; the recorded binary comes from the successful direct cargo rustc link.",
        "pre_registration_smoke": {
            "new_entry_point_imported": True,
            "r169_source_equals_exact": True,
            "r170_source_differs_from_exact": True,
            "r172_source_differs_from_exact": True,
            "r160_single_small_gap_source_differs_from_exact": True,
            "formal_matrix_executed": False,
            "formal_performance_evidence_collected": False,
        },
    }
    build_manifest["payload_hash"] = canonical_hash(build_manifest)
    write_json(root / BUILD_MANIFEST_PATH, build_manifest)

    protocol = {
        "title": "B4/B8/B10 R175 integrated Rust exact-score protocol",
        "version": 0,
        "method": METHOD,
        "status": "preregistered_unopened",
        "source_target_id": "T-B4-002cw/T-B8-003da/T-B10-009cm-r175-protocol",
        "upstream_target_id": "T-B4-002cv/T-B8-003cz/T-B10-009cl-r174",
        "research_question": "Can an exact retained-binary64 accumulator inside Qiskit's compiled Rust VF2 path repair true ties and sub-ULP non-ties while preserving ordinary mappings at bounded runtime and memory cost?",
        "datasets": DATASETS,
        "standard_profiles": PROFILES,
        "small_gap_modes": SMALL_GAP_MODES,
        "small_gap_cases": SMALL_GAP_CASES,
        "policies": ["source_f64", "rust_exact_retained_binary64"],
        "standard_replays_per_worker": 64,
        "small_gap_replays_per_case": 8,
        "warmup_calls_per_worker": 16,
        "worker_count": 26,
        "recorded_calls_per_policy": 800,
        "total_recorded_calls": 1600,
        "total_qiskit_calls_including_warmup": 2016,
        "process_environment": {
            "MKL_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "PYTHONHASHSEED": "0",
            "QISKIT_PARALLEL": "FALSE",
            "RAYON_NUM_THREADS": "1",
        },
        "vf2_configuration": {
            "call_limit": 30000000,
            "time_limit": None,
            "max_trials": 250000,
            "shuffle_seed": -1,
            "score_initial_layout": True,
            "strict_direction": False,
        },
        "exact_leaf_semantics": "decode each rounded binary64 value of neg_log_fidelity(error) * integer interaction count onto the exact 2^-1074 grid, then add arbitrary-precision integers",
        "tie_policy": "strict decreasing comparison preserves the first exact minimizer seen",
        "performance_thresholds": {
            "maximum_cell_median_time_ratio": 3.0,
            "maximum_aggregate_median_time_ratio": 2.5,
            "maximum_worker_peak_rss_ratio": 1.25,
        },
        "acceptance_requirements": [
            "all 26 isolated workers start after public preregistration and import the bound R175 accelerator",
            "all 1600 recorded calls and 416 warmups complete without simulation, shots, or route mutation",
            "source f64 reproduces all 800 committed source outcomes",
            "exact preserves all 192 R169 ordinary non-ties",
            "exact repairs all 192 R170 and all 192 R172 true-tie false winners",
            "exact repairs all 224 R160 sub-ULP unique-minimum rows while source reproduces all 224 prior wrong winners",
            "every row, worker, result, and source binding hash validates",
            "all frozen timing and peak-RSS thresholds pass",
            "an independent standard-library oracle imports neither Qiskit nor the R175 comparator and reproduces every expected outcome",
            "all forbidden claims and credit remain false or zero",
        ],
        "forbidden_claims": [
            "upstream_accepted_patch",
            "production_qiskit_remedy",
            "confirmed_qiskit_bug",
            "route_quality_improvement",
            "hardware_result",
            "quantum_advantage",
            "bqp_separation",
            "solved_frontier",
            "new_credit",
        ],
        "planned_artifacts": {
            "build_manifest": BUILD_MANIFEST_PATH,
            "contract": CONTRACT_PATH,
            "worker_directory": WORKER_DIR,
            "result": RESULT_PATH,
            "result_report": RESULT_REPORT_PATH,
            "independent_oracle": ORACLE_PATH,
            "independent_oracle_report": ORACLE_REPORT_PATH,
        },
    }
    protocol["payload_hash"] = canonical_hash(protocol)
    write_json(root / PROTOCOL_PATH, protocol)

    source_paths = [
        BUILD_MANIFEST_PATH,
        "results/B4_B8_R174_exact_score_comparator_v0.json",
        "results/B4_B8_R159_error_map_accumulation_trace/native_hashset_order.json",
        "results/B4_B8_R159_error_map_accumulation_trace/ascending_sorted_order.json",
        "results/B4_B8_R159_error_map_accumulation_trace/descending_sorted_order.json",
        "results/B4_B8_R160_deterministic_error_map_remediation_protocol_v0.json",
        "results/B4_B8_R160_deterministic_error_map_remediation_v0.json",
        "results/B4_B8_R160_deterministic_error_map_remediation/case_analysis.json",
        "results/B4_B8_R161_source_faithful_score_audit_v0.json",
        "benchmarks/B4_B8_R157_vf2_post_layout_input_v0.qasm",
    ]
    for dataset in DATASETS:
        source_paths.extend(
            [dataset["input_path"], dataset["protocol_path"], dataset["result_path"]]
        )
        source_paths.extend(
            str(path.relative_to(root))
            for path in sorted((root / dataset["worker_directory"]).glob("*.json"))
        )
    bindings = {
        f"source_{index:02d}": source_binding(root, path)
        for index, path in enumerate(source_paths, start=1)
    }
    contract = {
        "contract_id": "B4-B8-R175-rust-exact-score-contract-v0",
        "execution_started": False,
        "protocol_path": PROTOCOL_PATH,
        "protocol_payload_hash": protocol["payload_hash"],
        "source_bindings": bindings,
        "tool_bindings": {
            Path(path).stem: source_binding(root, path) for path in TOOL_PATHS
        },
        "expected_counts": {
            "worker_count": 26,
            "standard_worker_count": 18,
            "small_gap_worker_count": 8,
            "recorded_calls_per_policy": 800,
            "total_recorded_calls": 1600,
            "warmup_call_count": 416,
            "total_qiskit_calls": 2016,
            "standard_rows_per_policy": 576,
            "small_gap_rows_per_policy": 224,
        },
        "result_paths_must_be_absent": forbidden,
    }
    contract["payload_hash"] = canonical_hash(contract)
    write_json(root / CONTRACT_PATH, contract)
    (root / REPORT_PATH).write_text(build_report(protocol, contract), encoding="utf-8")
    print(
        json.dumps(
            {
                "build_manifest": build_manifest,
                "protocol": protocol,
                "contract": contract,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
