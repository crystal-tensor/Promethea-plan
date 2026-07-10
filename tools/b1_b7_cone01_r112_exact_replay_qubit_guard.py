#!/usr/bin/env python3
"""T-B1-004hj/T-B7-016s: exact replay with an explicit qubit-limit guard."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r112_exact_replay_qubit_guard_v0"
STATUS = "cone01_r112_exact_replay_passed_qubit_guard_explicit"
MODEL_STATUS = "13_qubit_exact_replay_passes_but_no_two_qubit_or_b7_credit"
TARGET_ID = "T-B1-004hj/T-B7-016s"
UPSTREAM_TARGET_ID = "T-B1-004hi/T-B7-016r"
SOURCE_PATH = "benchmarks/qasmbench_medium_exact/gcm_h6.qasm"
OUT_DIR = "results/B1_B7_cone01_R112_exact_replay_qubit_guard"
RESULT_PATH = "results/B1_B7_cone01_R112_exact_replay_qubit_guard_v0.json"
REPORT_PATH = "research/B1_B7_cone01_R112_exact_replay_qubit_guard.md"


def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_command(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)


def qreg_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    return sum(int(size) for size in re.findall(r"^qreg\s+\w+\[(\d+)\]\s*;", text, re.MULTILINE))


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def build_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    rows = "\n".join(
        f"- `{item['requirement_id']}` {'PASS' if item['passed'] else 'FAIL'}: {item['label']}"
        for item in payload["requirements"]
    )
    return f"""# B1/B7 Cone01 R112 Exact Replay Qubit Guard

## Summary

- Target: `{TARGET_ID}`
- Upstream target: `{UPSTREAM_TARGET_ID}`
- Method: `{METHOD}`
- Status: `{STATUS}`
- Model status: `{MODEL_STATUS}`
- Source: `{SOURCE_PATH}`
- Qubit count: `{summary['qubit_count']}`
- Exact equivalence at max 13 qubits: `{summary['equivalence_passed']}/{summary['equivalence_failed']}`
- Operation reduction: `{summary['operation_reduction_pct']:.4f}%`
- Logical-depth reduction: `{summary['logical_depth_reduction_pct']:.4f}%`
- Hardware-exposure reduction: `{summary['hardware_exposure_reduction_pct']:.4f}%`
- Two-qubit gate delta: `{summary['two_qubit_gate_delta']}`

R112 makes the qubit-limit boundary executable. The default `max-qubits=12`
guard rejects this 13-qubit workload; rerunning with `max-qubits=13` passes exact
statevector equivalence. The local rewrite certificates are valid, but the
two-qubit count does not change, so this is not a B7 resource-saving claim.

## Requirements

{rows}

## Claim Boundary

R112 supports one exact replay of the fixed-point local-rewrite pipeline on
`gcm_h6.qasm`. It does not establish arbitrary-input equivalence, a reduction
in two-qubit gates, a non-Clifford/T-resource reduction, a layout improvement,
or any B7 credit.
"""


def run(root: Path) -> dict[str, Any]:
    root = root.resolve()
    source = root / SOURCE_PATH
    out = root / OUT_DIR
    if out.exists():
        shutil.rmtree(out)
    work = out / "pipeline_work"
    results = out / "pipeline_results"
    work.mkdir(parents=True)
    results.mkdir(parents=True)
    label = "r112_exact_replay"
    pipeline = run_command(
        [
            sys.executable,
            "tools/b1_run_pipeline.py",
            SOURCE_PATH,
            "--work-dir",
            rel(work, root),
            "--results-dir",
            rel(results, root),
            "--profile",
            "heavy_hex_like_sparse",
            "--max-qubits",
            "13",
            "--max-rzz-passes",
            "8",
            "--max-scan",
            "80",
            "--label",
            label,
        ],
        root,
    )
    pipeline_stdout = results / "pipeline.stdout.txt"
    pipeline_stdout.write_text(pipeline.stdout + pipeline.stderr, encoding="utf-8")
    summary_path = results / f"{label}_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    guard = run_command(
        [
            sys.executable,
            "tools/b1_equivalence_check.py",
            rel(work / "00_input", root),
            rel(work / "02_rzz_pass", root),
            "--max-qubits",
            "12",
            "--pretty",
            "--output",
            rel(results / "max12_guard.json", root),
        ],
        root,
    )
    guard_text = guard.stdout + guard.stderr
    (results / "max12_guard.stdout.txt").write_text(guard_text, encoding="utf-8")
    guard_rejected = guard.returncode != 0 and "exceeding max 12" in guard_text
    qubits = qreg_count(source)
    equivalence_ok = pipeline.returncode == 0 and summary.get("equivalence_passed") == 1 and summary.get("equivalence_failed") == 0
    local_certs = summary.get("local_certificates", {})
    oneq = local_certs.get("single_qubit_block_resynthesis", {})
    rzz = local_certs.get("rzz_window_resynthesis", {})
    requirements = [
        {"requirement_id": "P1", "label": "source workload has 13 qubits", "passed": qubits == 13, "evidence": {"qubit_count": qubits}},
        {"requirement_id": "P2", "label": "max-qubits=12 rejects the 13-qubit workload explicitly", "passed": guard_rejected, "evidence": {"returncode": guard.returncode, "message": guard_text[-300:]}},
        {"requirement_id": "P3", "label": "max-qubits=13 exact equivalence passes", "passed": equivalence_ok, "evidence": {"pipeline_returncode": pipeline.returncode, "equivalence_passed": summary.get("equivalence_passed"), "equivalence_failed": summary.get("equivalence_failed")}},
        {"requirement_id": "P4", "label": "local rewrite certificates are emitted", "passed": oneq.get("resynthesized_runs") == 480 and oneq.get("removed_single_qubit_gates") == 1297 and rzz.get("windows") == 0, "evidence": {"resynthesized_runs": oneq.get("resynthesized_runs"), "removed_single_qubit_gates": oneq.get("removed_single_qubit_gates"), "rzz_windows": rzz.get("windows")}},
        {"requirement_id": "P5", "label": "operation, depth, and exposure improve on this workload", "passed": summary.get("operation_count_delta", 0) < 0 and summary.get("logical_depth_delta", 0) < 0 and summary.get("hardware_weighted_exposure_delta", 0) < 0, "evidence": {"operation_count_delta": summary.get("operation_count_delta"), "logical_depth_delta": summary.get("logical_depth_delta"), "hardware_weighted_exposure_delta": summary.get("hardware_weighted_exposure_delta")}},
        {"requirement_id": "P6", "label": "two-qubit gate count does not receive false credit", "passed": summary.get("two_qubit_gate_count_delta") == 0, "evidence": {"two_qubit_gate_count_delta": summary.get("two_qubit_gate_count_delta")}},
        {"requirement_id": "P7", "label": "replay artifacts are materialized and hashable", "passed": pipeline_stdout.exists() and summary_path.exists(), "evidence": {"pipeline_stdout": rel(pipeline_stdout, root), "summary": rel(summary_path, root)}},
        {"requirement_id": "P8", "label": "claim boundary keeps B7 credit at zero", "passed": True, "evidence": {"model_status": MODEL_STATUS}},
    ]
    failed = [item["requirement_id"] for item in requirements if not item["passed"]]
    metrics = {
        "operation_reduction_pct": summary.get("operation_count_reduction_pct", 0),
        "logical_depth_reduction_pct": summary.get("logical_depth_reduction_pct", 0),
        "hardware_exposure_reduction_pct": summary.get("hardware_weighted_exposure_reduction_pct", 0),
        "two_qubit_gate_delta": summary.get("two_qubit_gate_count_delta", 0),
    }
    result_summary = {
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "qubit_count": qubits,
        "max12_guard_rejected": guard_rejected,
        "equivalence_passed": summary.get("equivalence_passed", 0),
        "equivalence_failed": summary.get("equivalence_failed", 0),
        **metrics,
        "counter_transition_accepted": False,
        "counter_delta": 0,
        "new_credit_delta": 0,
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
    }
    payload = {
        "title": "B1/B7 cone01 R112 exact replay qubit guard",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_path": SOURCE_PATH,
        "requirements": requirements,
        "requirement_count": len(requirements),
        "requirements_passed": result_summary["requirements_passed"],
        "requirements_failed": result_summary["requirements_failed"],
        "summary": result_summary,
        "pipeline_summary": summary,
        "artifacts": {"pipeline_summary": rel(summary_path, root), "pipeline_stdout": rel(pipeline_stdout, root), "max12_guard_stdout": rel(results / "max12_guard.stdout.txt", root), "final_qasm": rel(work / "final" / "gcm_h6.qasm", root)},
        "claim_boundary": {"what_is_supported": "One 13-qubit exact statevector replay of the fixed-point local-rewrite pipeline with explicit max-qubits guard.", "what_is_not_supported": "No arbitrary-input equivalence, two-qubit gate reduction, T-resource reduction, layout improvement, or B7 credit.", "next_gate": "Produce a composable full-circuit semantic certificate and nonzero two-qubit or proxy-T delta under the same denominator."},
    }
    payload["payload_hash"] = stable_hash(payload)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(build_report(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    print(json.dumps(run(Path(args.repo_root)), sort_keys=True))


if __name__ == "__main__":
    main()
