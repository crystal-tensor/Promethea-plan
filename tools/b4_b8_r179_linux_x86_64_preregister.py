#!/usr/bin/env python3
"""Freeze R179 Linux x86-64 build and replay before workflow dispatch."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


METHOD = "b4_b8_r179_linux_x86_64_protocol_v0"
PROTOCOL_PATH = "results/B4_B8_R179_linux_x86_64_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R179_linux_x86_64_contract_v0.json"
REPORT_PATH = "research/B4_B8_R179_linux_x86_64_protocol.md"
R176_PROTOCOL_PATH = "results/B4_B8_R176_fixed_superaccumulator_protocol_v0.json"
R176_CONTRACT_PATH = "benchmarks/B4_B8_R176_fixed_superaccumulator_contract_v0.json"
RESULT_PATHS = [
    "research/source_lineage/Qiskit_2_4_1_R179_fixed_superaccumulator_pyext.x86_64-linux-gnu.so",
    "research/source_lineage/Qiskit_2_4_1_R179_linux_x86_64_build_manifest.json",
    "research/source_lineage/R179_linux_x86_64_build_logs",
    "research/B4_B8_R179_linux_x86_64_replay.md",
    "research/B4_B8_R179_independent_linux_x86_64_oracle.md",
    "results/B4_B8_R179_linux_x86_64_replay",
    "results/B4_B8_R179_linux_x86_64_replay_v0.json",
    "results/B4_B8_R179_independent_linux_x86_64_oracle_v0.json",
    "results/B4_B8_R179_linux_x86_64_bundle_manifest_v0.json",
]
TOOLS = [
    "tools/b4_b8_r179_linux_x86_64_preregister.py",
    "tools/b4_b8_r179_linux_x86_64_build.py",
    "tools/b4_b8_r179_linux_x86_64_replay.py",
    "tools/b4_b8_r179_independent_linux_x86_64_oracle.py",
    "tools/b4_b8_r179_linux_x86_64_bundle.py",
    "tools/b4_b8_r176_fixed_superaccumulator_replay.py",
    "tools/b4_b8_r176_independent_fixed_accumulator_oracle.py",
    ".github/workflows/r179-linux-x86-64.yml",
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
        raise ValueError(f"R179 source binding is missing: {relative}")
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
            "# B4/B8/B10 R179 Linux x86-64 Protocol",
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
            f"The workflow fixes `{protocol['worker_count']}` isolated Linux x86-64 workers, `{protocol['total_recorded_calls']}` recorded calls, and `{protocol['total_qiskit_calls_including_warmup'] - protocol['total_recorded_calls']}` warmups across source f64, R175 BigUint, and R176 fixed exact scoring.",
            "",
            "## Performance Gates",
            "",
            f"Fixed/source must remain at most `{thresholds['maximum_cell_median_time_ratio']}` per cell and `{thresholds['maximum_aggregate_median_time_ratio']}` aggregate; fixed/BigUint must remain at most `{thresholds['maximum_aggregate_fixed_to_biguint_median_time_ratio']}` aggregate; peak RSS must remain at most `{thresholds['maximum_worker_peak_rss_ratio']}` relative to source.",
            "",
            "## Claim Boundary",
            "",
            "This is a preregistered Ubuntu x86-64 build and replay contract. It does not claim an upstream patch, production remedy, confirmed Qiskit bug, successful cross-platform result, hardware evidence, quantum advantage, BQP separation, solved B4/B8/B10, or new credit before execution.",
            "",
        ]
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for relative in [PROTOCOL_PATH, CONTRACT_PATH, REPORT_PATH, *RESULT_PATHS]:
        if (root / relative).exists():
            raise ValueError(f"R179 output already exists: {relative}")
    r176_protocol = json.loads((root / R176_PROTOCOL_PATH).read_text(encoding="utf-8"))
    r176_contract = json.loads((root / R176_CONTRACT_PATH).read_text(encoding="utf-8"))
    protocol = copy.deepcopy(r176_protocol)
    protocol.update(
        {
            "title": "B4/B8/B10 R179 Linux x86-64 independent replay protocol",
            "version": 0,
            "method": METHOD,
            "status": "preregistered_unopened",
            "source_target_id": "T-B4-002di/T-B8-003dm/T-B10-009cy-r179-protocol",
            "upstream_target_id": "T-B4-002dh/T-B8-003dl/T-B10-009cx-r178-import-failure",
            "research_question": "After R178 built and identified the correct Linux binary but let the source checkout shadow its isolated import overlay, can a cwd-isolated Ubuntu x86-64 import pass and reproduce the full R176 exact-selection result inside the same frozen local performance gates?",
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
                "the official Qiskit source commit and R176 patch reproduce the frozen patched-source hashes",
                "cargo fmt, check, three fixed-accumulator tests, diff check, and release build return zero",
                "the release artifact name is derived from crates/pyext/Cargo.toml and the copied binary passes a hash-bound Python import smoke test whose current directory is outside the source checkout",
                "all 39 isolated workers identify Linux x86-64 and bind one recorded accelerator hash",
                "all 2400 recorded calls and 624 warmups complete without simulation or shots",
                "source f64, BigUint, and fixed exact each match all 800 frozen outcomes",
                "fixed exact preserves R169 and repairs every R170, R172, and R160 frozen case",
                "every row, worker, build, result, source, and workflow binding hash validates",
                "the unchanged R176 fixed/source timing and peak-RSS thresholds pass",
                "fixed remains at least 10 percent faster than BigUint on the aggregate median",
                "a standard-library oracle imports neither Qiskit nor the R179 executor and reproduces every outcome",
                "all forbidden claims and credit remain false or zero",
            ],
            "planned_artifacts": {
                "build_manifest": RESULT_PATHS[1],
                "accelerator": RESULT_PATHS[0],
                "worker_directory": RESULT_PATHS[5],
                "result": RESULT_PATHS[6],
                "result_report": RESULT_PATHS[3],
                "independent_oracle": RESULT_PATHS[7],
                "independent_oracle_report": RESULT_PATHS[4],
                "bundle_manifest": RESULT_PATHS[8],
            },
        }
    )
    protocol.pop("payload_hash", None)
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
            "results/B4_B8_R178_linux_x86_64_import_failure_v0.json",
            "research/B4_B8_R178_linux_x86_64_import_failure.md",
            "research/source_lineage/Qiskit_2_4_1_R178_fixed_superaccumulator_pyext.x86_64-linux-gnu.so",
            "research/source_lineage/Qiskit_2_4_1_R176_fixed_superaccumulator.patch",
        }
    )
    contract = {
        "contract_id": "B4-B8-R179-linux-x86-64-contract-v0",
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
        "result_paths_must_be_absent": RESULT_PATHS,
        "expected_counts": {
            "worker_count": 39,
            "total_recorded_calls": 2400,
            "warmup_call_count": 624,
            "total_qiskit_calls": 3024,
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
