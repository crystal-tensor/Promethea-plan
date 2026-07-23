#!/usr/bin/env python3
"""R96: check the constructive B9 cluster-term locality bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "B9" / "ClusterStabilizer" / "WidthLocality.lean"
TRANSCRIPT = ROOT / "results" / "B9_R96_support_locality_formalization_transcript.txt"
OUT_JSON = ROOT / "results" / "B9_support_locality_formalization_gate_v0.json"
OUT_MD = ROOT / "research" / "B9_support_locality_formalization_gate.md"
METHOD = "b9_support_locality_formalization_gate_v0"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> dict[str, Any]:
    started = time.time()
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    executable = "~/.elan/bin/lean" if command[0].endswith("/lean") else "~/.elan/bin/lake"
    return {
        "command": [executable, *command[1:]],
        "returncode": completed.returncode,
        "elapsed_seconds": round(time.time() - started, 6),
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def build() -> dict[str, Any]:
    source = SOURCE.read_text(encoding="utf-8")
    source_hash = sha256_file(SOURCE)
    commands = [
        [str(Path.home() / ".elan/bin/lean"), "--version"],
        [str(Path.home() / ".elan/bin/lake"), "--version"],
        [str(Path.home() / ".elan/bin/lake"), "env", "lean", "B9/ClusterStabilizer/WidthLocality.lean"],
    ]
    records = [run(command) for command in commands]
    transcript_parts = [f"SOURCE_SHA256: {source_hash}", ""]
    for record in records:
        transcript_parts.extend(
            [
                f"COMMAND: {' '.join(record['command'])}",
                f"RETURNCODE: {record['returncode']}",
                f"ELAPSED_SECONDS: {record['elapsed_seconds']}",
                "STDOUT:",
                record["stdout"],
                "STDERR:",
                record["stderr"],
                "END_COMMAND",
                "",
            ]
        )
    transcript = "\n".join(transcript_parts)
    TRANSCRIPT.parent.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT.write_text(transcript, encoding="utf-8")
    start = source.index("inductive ClusterTerm")
    end = source.index("theorem locality_in_support_set", start)
    support_api = source[start:end]
    zero_returns = all(record["returncode"] == 0 for record in records)
    no_warnings = all("warning:" not in record["stdout"] + record["stderr"] for record in records)
    requirements = [
        ["R1", "Lean/Lake probes return zero", all(record["returncode"] == 0 for record in records[:2])],
        ["R2", "The B9 module returns zero", records[2]["returncode"] == 0],
        ["R3", "ClusterTerm is an inductive support-bearing construction", "inductive ClusterTerm (n : Nat)" in support_api],
        ["R4", "Interior terms are fixed at support size three", "| .interior _ _ _ => 3" in support_api],
        ["R5", "Boundary terms are fixed at support size two", "| .leftBoundary _ => 2" in support_api and "| .rightBoundary _ => 2" in support_api],
        ["R6", "Every constructed term is in the support set", "cluster_term_locality_in_support_set" in support_api and "cases term <;> simp" in support_api],
        ["R7", "Every constructed term has maximum locality three", "cluster_term_max_locality" in support_api and "term.locality ≤ 3" in support_api],
        ["R8", "The support construction connects to SpectralSummary", "cluster_term_summary_has_support_size" in support_api and "HasSupportSize" in support_api],
        ["R9", "Uniform reweighting preserves constructed locality", "uniform_reweight_preserves_cluster_term_locality" in support_api and "rfl" in support_api],
        ["R10", "Transcript binds source hash, has three records, and has no warnings", transcript.count("END_COMMAND") == 3 and no_warnings and f"SOURCE_SHA256: {source_hash}" in transcript],
    ]
    rows = [{"requirement_id": item[0], "label": item[1], "passed": bool(item[2])} for item in requirements]
    failed = [row["requirement_id"] for row in rows if not row["passed"]]
    payload = {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "method": METHOD,
        "status": "support_locality_formalization_checked_not_quantum_pcp_proof" if not failed else "support_locality_formalization_failed",
        "model_status": "constructive_cluster_term_support_bridge_checked_under_pinned_lean_lake",
        "workload": "B9/ClusterStabilizer/WidthLocality.lean",
        "summary": {
            "requirement_count": len(rows),
            "requirements_passed": len(rows) - len(failed),
            "requirements_failed": len(failed),
            "failed_requirement_ids": failed,
            "fresh_command_count": len(records),
            "fresh_zero_returncode_count": sum(record["returncode"] == 0 for record in records),
            "fresh_no_warning": no_warnings,
            "source_sha256": source_hash,
            "transcript_sha256": sha256_file(TRANSCRIPT),
            "checked_constructive_support_bridge": not failed and zero_returns,
            "support_sizes": [2, 3],
            "max_locality": 3,
            "proof_assistant_checked": zero_returns,
            "formal_theorem_proved": False,
            "explicit_not_quantum_pcp_proof": True,
            "nlts_theorem_claimed": False,
            "global_gap_amplification_impossibility_claimed": False,
            "bqp_separation_claimed": False,
            "validation_error_count": len(failed),
        },
        "claim_boundary": {
            "what_is_supported": "Lean checks a constructive ClusterTerm support interface: interior terms have locality 3, boundary terms have locality 2, every term has locality at most 3, and uniform reweighting preserves that locality.",
            "what_is_not_supported": "This does not prove that a full all-n Hamiltonian has the desired spectrum, does not prove a Quantum PCP or NLTS theorem, and does not prove a global gap-amplification impossibility or BQP separation.",
        },
        "requirements": rows,
        "fresh_command_records": records,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# B9 Support/Locality Formalization Gate",
        "",
        f"- Method: `{METHOD}`",
        f"- Status: `{payload['status']}`",
        f"- Requirements passed/failed: `{len(rows) - len(failed)}` / `{len(failed)}`",
        f"- Fresh Lean/Lake commands returning zero: `{payload['summary']['fresh_zero_returncode_count']}/{len(records)}`",
        f"- Source SHA256: `{source_hash}`",
        f"- Transcript SHA256: `{payload['summary']['transcript_sha256']}`",
        "",
        "## Supported Result",
        "",
        payload["claim_boundary"]["what_is_supported"],
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"]["what_is_not_supported"],
        "",
    ]
    lines.extend(f"- {row['requirement_id']} [{'PASS' if row['passed'] else 'FAIL'}]: {row['label']}" for row in rows)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    argparse.ArgumentParser().parse_args()
    payload = build()
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    if payload["summary"]["validation_error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
