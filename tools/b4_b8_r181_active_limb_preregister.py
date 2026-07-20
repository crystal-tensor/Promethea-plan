#!/usr/bin/env python3
"""Freeze R181 Linux x86-64 build and replay before workflow dispatch."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r181_active_limb_protocol_v0"
PROTOCOL_PATH = "results/B4_B8_R181_active_limb_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R181_active_limb_contract_v0.json"
REPORT_PATH = "research/B4_B8_R181_active_limb_protocol.md"
R176_PROTOCOL_PATH = "results/B4_B8_R176_fixed_superaccumulator_protocol_v0.json"
R176_CONTRACT_PATH = "benchmarks/B4_B8_R176_fixed_superaccumulator_contract_v0.json"
BUILD_OUTPUT_PATHS = [
    "research/source_lineage/Qiskit_2_4_1_R181_active_limb_pyext.x86_64-linux-gnu.so",
    "research/source_lineage/Qiskit_2_4_1_R181_active_limb_linux_x86_64_build_manifest.json",
    "research/source_lineage/R181_active_limb_linux_x86_64_build_logs",
]
SCIENTIFIC_RESULT_PATHS = [
    "research/B4_B8_R181_active_limb_replay.md",
    "research/B4_B8_R181_independent_active_limb_oracle.md",
    "results/B4_B8_R181_active_limb_replay",
    "results/B4_B8_R181_active_limb_replay_v0.json",
    "results/B4_B8_R181_independent_active_limb_oracle_v0.json",
    "results/B4_B8_R181_active_limb_bundle_manifest_v0.json",
]
GENERATED_PATHS = [*BUILD_OUTPUT_PATHS, *SCIENTIFIC_RESULT_PATHS]
TOOLS = [
    "tools/b4_b8_r181_active_limb_preregister.py",
    "tools/b4_b8_r181_linux_x86_64_build.py",
    "tools/b4_b8_r181_active_limb_replay.py",
    "tools/b4_b8_r181_independent_active_limb_oracle.py",
    "tools/b4_b8_r181_linux_x86_64_bundle.py",
    ".github/workflows/r181-active-limb-linux-x86-64.yml",
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


def source_binding(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"R181 source binding is missing: {relative}")
    binding: dict[str, Any] = {"path": relative, "sha256": file_sha256(path)}
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if "payload_hash" in payload:
            binding["payload_hash"] = payload["payload_hash"]
        if "manifest_hash" in payload:
            binding["manifest_hash"] = payload["manifest_hash"]
    return binding


def report(protocol: dict[str, Any], contract: dict[str, Any]) -> str:
    thresholds = protocol["performance_thresholds"]
    return "\n".join(
        [
            "# B4/B8/B10 R181 Active-Limb Linux x86-64 Protocol",
            "",
            "- Status: `preregistered_unopened`",
            f"- Protocol payload hash: `{protocol['payload_hash']}`",
            f"- Contract payload hash: `{contract['payload_hash']}`",
            "- Execution: unopened until a public Discussion is created",
            "",
            "## Research Question",
            "",
            protocol["research_question"],
            "",
            "## Frozen Matrix",
            "",
            f"The workflow fixes `{protocol['worker_count']}` isolated Linux x86-64 workers, `{protocol['total_recorded_calls']}` recorded calls, and `{protocol['total_qiskit_calls_including_warmup'] - protocol['total_recorded_calls']}` warmups across source f64, BigUint exact, fixed-34 exact, and active-limb fixed exact scoring.",
            "",
            "## Performance Gates",
            "",
            f"Active/source must remain at most `{thresholds['maximum_active_to_source_cell_median_time_ratio']}` per cell and `{thresholds['maximum_active_to_source_aggregate_median_time_ratio']}` aggregate. Active/fixed-34 must be at most `{thresholds['maximum_active_to_fixed_aggregate_median_time_ratio']}` and active/BigUint at most `{thresholds['maximum_active_to_biguint_aggregate_median_time_ratio']}`. Active/source peak RSS must remain at most `{thresholds['maximum_active_to_source_worker_peak_rss_ratio']}`.",
            "",
            "## Claim Boundary",
            "",
            "This is a preregistered Ubuntu x86-64 cost-attribution experiment. It does not claim an upstream patch, production remedy, confirmed Qiskit bug, hardware evidence, quantum advantage, BQP separation, solved B4/B8/B10, or new credit before execution.",
            "",
        ]
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for relative in [PROTOCOL_PATH, CONTRACT_PATH, REPORT_PATH, *GENERATED_PATHS]:
        if (root / relative).exists():
            raise ValueError(f"R181 output already exists: {relative}")
    r176_protocol = json.loads((root / R176_PROTOCOL_PATH).read_text(encoding="utf-8"))
    r176_contract = json.loads((root / R176_CONTRACT_PATH).read_text(encoding="utf-8"))
    protocol = copy.deepcopy(r176_protocol)
    protocol.update(
        {
            "title": "B4/B8/B10 R181 active-limb Linux x86-64 protocol",
            "version": 0,
            "method": METHOD,
            "status": "preregistered_unopened",
            "source_target_id": "T-B4-002dn/T-B8-003dr/T-B10-009dd-r181-protocol",
            "upstream_target_id": "T-B4-002dm/T-B8-003dq/T-B10-009dc-r180-execution-boundary-failure",
            "research_question": "After separating build outputs from unopened scientific results, can the unchanged active-limb scorer preserve exact retained-binary64 selection while reversing R179's Linux performance loss caused by scanning all 34 fixed limbs?",
            "platform_contract": {
                "runner": "github_hosted_ubuntu_24_04",
                "system": "Linux",
                "machine": "x86_64",
                "python": "3.12",
                "qiskit": "2.4.1",
                "source_commit": "0fd015a22b84c9082173597a5d2304dc0aaec08c",
                "workflow_dispatch_only": True,
                "requires_public_discussion_before_dispatch": True,
            },
            "acceptance_requirements": [
                "the Linux build and every worker start after a public preregistration Discussion",
                "the official Qiskit source commit and R181 patch reproduce the frozen patched-source hashes",
                "cargo fmt, check, four active-limb tests, diff check, and release build return zero",
                "the release artifact name is derived from crates/pyext/Cargo.toml and the copied binary passes a hash-bound Python import smoke test whose current directory is outside the source checkout",
                "the replay guard requires all scientific result paths to be absent while accepting only the hash-bound build outputs created by the preceding build step",
                "all 52 isolated workers identify Linux x86-64 and bind one recorded accelerator hash",
                "all 3200 recorded calls and 832 warmups complete without simulation or shots",
                "source f64, BigUint, fixed-34, and active-limb exact each match all 800 frozen outcomes",
                "active-limb exact preserves R169 and repairs every R170, R172, and R160 frozen case",
                "every row, worker, build, result, source, and workflow binding hash validates",
                "active-limb/source timing and peak-RSS thresholds pass",
                "active-limb is at least 10 percent faster than fixed-34 and no slower than BigUint on the aggregate median",
                "a standard-library oracle imports neither Qiskit nor the R181 executor and reproduces every outcome",
                "all forbidden claims and credit remain false or zero",
            ],
            "planned_artifacts": {
                "build_manifest": BUILD_OUTPUT_PATHS[1],
                "accelerator": BUILD_OUTPUT_PATHS[0],
                "worker_directory": SCIENTIFIC_RESULT_PATHS[2],
                "result": SCIENTIFIC_RESULT_PATHS[3],
                "result_report": SCIENTIFIC_RESULT_PATHS[0],
                "independent_oracle": SCIENTIFIC_RESULT_PATHS[4],
                "independent_oracle_report": SCIENTIFIC_RESULT_PATHS[1],
                "bundle_manifest": SCIENTIFIC_RESULT_PATHS[5],
            },
        }
    )
    protocol.pop("payload_hash", None)
    protocol.update(
        {
            "policies": [
                "source_f64",
                "rust_biguint_exact_retained_binary64",
                "rust_fixed_exact_retained_binary64",
                "rust_active_limb_exact_retained_binary64",
            ],
            "worker_count": 52,
            "recorded_calls_per_policy": 800,
            "total_recorded_calls": 3200,
            "total_qiskit_calls_including_warmup": 4032,
            "active_limb_semantics": "retain the 34-limb stack-resident coefficient array but store the highest nonzero limb count; addition scans max(left.used,right.used) plus carry and comparison first compares used length before scanning only active limbs",
            "performance_thresholds": {
                "maximum_active_to_source_cell_median_time_ratio": 3.0,
                "maximum_active_to_source_aggregate_median_time_ratio": 2.5,
                "maximum_active_to_fixed_aggregate_median_time_ratio": 0.90,
                "maximum_active_to_biguint_aggregate_median_time_ratio": 1.0,
                "maximum_active_to_source_worker_peak_rss_ratio": 1.25,
            },
        }
    )
    protocol["payload_hash"] = canonical_hash(protocol)
    write_json(root / PROTOCOL_PATH, protocol)

    source_paths = {
        binding["path"] for binding in r176_contract.get("source_bindings", {}).values()
    }
    source_paths.update(
        {
            R176_PROTOCOL_PATH,
            R176_CONTRACT_PATH,
            "results/B4_B8_R176_fixed_superaccumulator_v0.json",
            "results/B4_B8_R176_independent_fixed_accumulator_oracle_v0.json",
            "results/B4_B8_R179_linux_x86_64_replay_v0.json",
            "results/B4_B8_R179_independent_linux_x86_64_oracle_v0.json",
            "results/B4_B8_R179_independent_linux_x86_64_oracle_adjudication_v0.json",
            "results/B4_B8_R180_execution_boundary_failure_v0.json",
            "research/source_lineage/Qiskit_2_4_1_R180_active_limb_linux_x86_64_build_manifest.json",
            "research/source_lineage/Qiskit_2_4_1_R180_active_limb_superaccumulator.patch",
        }
    )
    contract = {
        "contract_id": "B4-B8-R181-active-limb-contract-v0",
        "execution_started": False,
        "protocol_path": PROTOCOL_PATH,
        "protocol_payload_hash": protocol["payload_hash"],
        "source_bindings": {
            f"source_{index:02d}": source_binding(root, path)
            for index, path in enumerate(sorted(source_paths), start=1)
        },
        "tool_bindings": {
            Path(path).stem: source_binding(root, path) for path in TOOLS
        },
        "build_output_paths_created_before_replay": BUILD_OUTPUT_PATHS,
        "result_paths_must_be_absent": SCIENTIFIC_RESULT_PATHS,
        "expected_counts": {
            "worker_count": 52,
            "total_recorded_calls": 3200,
            "warmup_call_count": 832,
            "total_qiskit_calls": 4032,
            "recorded_calls_per_policy": 800,
            "standard_rows_per_policy": 576,
            "small_gap_rows_per_policy": 224,
        },
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
                "worker_count": protocol["worker_count"],
                "recorded_calls": protocol["total_recorded_calls"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
