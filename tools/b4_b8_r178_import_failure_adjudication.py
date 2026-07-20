#!/usr/bin/env python3
"""Seal the public R178 isolated-import failure without scientific credit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ID = 29755312637
JOB_ID = 88396030273
ARTIFACT_ID = 8466710742
RUN_URL = "https://github.com/crystal-tensor/Prometheus-plan/actions/runs/29755312637"
DISCUSSION_URL = "https://github.com/crystal-tensor/Prometheus-plan/discussions/267"
PREREGISTRATION_COMMIT = "478f9277a8c8d524c709249e34afd1a8952fbbe3"
PROTOCOL_PATH = "results/B4_B8_R178_linux_x86_64_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R178_linux_x86_64_contract_v0.json"
LOG_DIR = "research/source_lineage/R178_linux_x86_64_build_logs"
BINARY_PATH = (
    "research/source_lineage/"
    "Qiskit_2_4_1_R178_fixed_superaccumulator_pyext.x86_64-linux-gnu.so"
)
RESULT_PATH = "results/B4_B8_R178_linux_x86_64_import_failure_v0.json"
REPORT_PATH = "research/B4_B8_R178_linux_x86_64_import_failure.md"


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_hash(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    observed = payload.pop("payload_hash", None)
    expected = canonical_hash(payload)
    if observed != expected:
        raise ValueError(f"payload hash mismatch: {path}")
    return str(observed)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output = root / RESULT_PATH
    report = root / REPORT_PATH
    if output.exists() or report.exists():
        raise ValueError("R178 failure adjudication already exists")
    protocol_hash = payload_hash(root / PROTOCOL_PATH)
    contract_hash = payload_hash(root / CONTRACT_PATH)
    log_root = root / LOG_DIR
    logs = [
        {
            "path": str(path.relative_to(root)),
            "sha256": file_sha256(path),
            "size_bytes": path.stat().st_size,
        }
        for path in sorted(log_root.glob("*.txt"))
    ]
    if len(logs) != 24:
        raise ValueError(f"R178 expected 24 downloaded log files, found {len(logs)}")
    release_stderr = (log_root / "11_cargo_release.stderr.txt").read_text(
        encoding="utf-8"
    )
    if (
        "Finished `release` profile [optimized]" not in release_stderr
        or "Compiling qiskit-pyext v2.4.1" not in release_stderr
    ):
        raise ValueError("R178 release-success evidence missing")
    import_stderr = (log_root / "12_python_import_smoke.stderr.txt").read_text(
        encoding="utf-8"
    )
    if (
        "cannot import name '_accelerate' from partially initialized module 'qiskit'"
        not in import_stderr
        or "/tmp/prometheus-r178-qiskit-source/qiskit/__init__.py" not in import_stderr
    ):
        raise ValueError("R178 isolated-import failure evidence missing")
    binary = root / BINARY_PATH
    if not binary.is_file():
        raise ValueError("R178 built Linux binary is missing")
    result = {
        "title": "B4/B8/B10 R178 Linux x86-64 import failure adjudication",
        "version": 0,
        "method": "b4_b8_r178_import_failure_adjudication_v0",
        "status": "isolated_import_failed_before_scientific_replay",
        "source_target_id": ("T-B4-002dh/T-B8-003dl/T-B10-009cx-r178-import-failure"),
        "upstream_target_id": "T-B4-002de/T-B8-003di/T-B10-009cu-r178-protocol",
        "public_preregistration": {
            "commit": PREREGISTRATION_COMMIT,
            "discussion": DISCUSSION_URL,
            "created_at": "2026-07-20T15:27:43Z",
            "protocol_payload_hash": protocol_hash,
            "contract_payload_hash": contract_hash,
        },
        "github_actions": {
            "run_id": RUN_ID,
            "job_id": JOB_ID,
            "artifact_id": ARTIFACT_ID,
            "run_url": RUN_URL,
            "conclusion": "failure",
            "artifact_sha256": (
                "cb7c5c8cc7339bb6d69db1528787f546b2ed2882be0b7bf66382b1b71f8023de"
            ),
        },
        "completed_build_gates": [
            "official Qiskit source checkout",
            "R176 patch applicability and application",
            "patched-source hash verification",
            "cargo fmt --check",
            "cargo check for qiskit-transpiler",
            "three R176 fixed-accumulator unit tests",
            "git diff --check",
            "release build of qiskit-pyext",
            "source-metadata resolution of target/release/libqiskit_pyext.so",
            "x86-64 ELF shared-object validation",
        ],
        "built_accelerator": {
            "path": BINARY_PATH,
            "sha256": file_sha256(binary),
            "size_bytes": binary.stat().st_size,
        },
        "failure": {
            "stage": "post_build_isolated_python_import_smoke",
            "observed_exception": (
                "ImportError: cannot import name '_accelerate' from partially "
                "initialized module 'qiskit'"
            ),
            "root_cause": (
                "the smoke subprocess ran with the Qiskit source checkout as its "
                "current directory, so Python sys.path[0] shadowed the isolated "
                "overlay and imported the unbuilt source package"
            ),
            "scientific_matrix_started": False,
            "worker_count_started": 0,
            "recorded_call_count": 0,
            "warmup_call_count": 0,
            "oracle_started": False,
        },
        "downloaded_log_count": len(logs),
        "downloaded_logs": logs,
        "next_gate": (
            "freeze a new protocol that runs the same hash-bound import smoke from "
            "the isolated overlay rather than the Qiskit source checkout"
        ),
        "hardware_result_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "new_credit_delta": 0,
    }
    result["payload_hash"] = canonical_hash(result)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report.write_text(
        "\n".join(
            [
                "# B4/B8/B10 R178 Linux x86-64 Import Failure",
                "",
                f"- Public run: `{RUN_URL}`",
                f"- Result hash: `{result['payload_hash']}`",
                "- Status: `isolated_import_failed_before_scientific_replay`",
                "",
                "## What Passed",
                "",
                "The official source checkout, patch binding, patched-source hashes, cargo format/check/test gates, git diff check, optimized `qiskit-pyext` release build, source-metadata artifact resolution, and x86-64 ELF check completed successfully on Ubuntu x86-64.",
                "",
                "## What Failed",
                "",
                "The isolated import subprocess inherited the Qiskit source checkout as its current directory. Python therefore resolved `qiskit` from the unbuilt source tree before the intended overlay and failed while importing `qiskit._accelerate`. The built Linux binary itself is preserved and hash-bound; its import was not validated.",
                "",
                "## Claim Boundary",
                "",
                "No worker, warmup, recorded call, independent oracle, simulation, or hardware execution started. R178 therefore says nothing positive or negative about the cross-platform scientific result. It records a reproducible import-environment defect and grants no B4, B8, B10, hardware, advantage, or solved-frontier credit.",
                "",
                "## Next Gate",
                "",
                result["next_gate"].capitalize() + ".",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"status": result["status"], "payload_hash": result["payload_hash"]},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
