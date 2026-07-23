#!/usr/bin/env python3
"""R97: check the all-n canonical cluster-term family locality bridge."""

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
TRANSCRIPT = ROOT / "results" / "B9_R97_term_family_locality_transcript.txt"
OUT_JSON = ROOT / "results" / "B9_term_family_locality_gate_v0.json"
OUT_MD = ROOT / "research" / "B9_term_family_locality_gate.md"
METHOD = "b9_term_family_locality_gate_v0"


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

    start = source.index("def ClusterTerm.at")
    end = source.index("theorem locality_in_support_set", start)
    family_api = source[start:end]
    no_warnings = all("warning:" not in record["stdout"] + record["stderr"] for record in records)
    requirements = [
        ["R1", "Lean/Lake version probes return zero", all(record["returncode"] == 0 for record in records[:2])],
        ["R2", "The B9 module returns zero", records[2]["returncode"] == 0],
        ["R3", "ClusterTerm.at is an indexed construction", "def ClusterTerm.at" in family_api and "Fin n" in family_api],
        ["R4", "The left boundary branch is explicit", ".leftBoundary hN" in family_api and "i.val = 0" in family_api],
        ["R5", "The right boundary branch is explicit", ".rightBoundary hN" in family_api and "i.val + 1 = n" in family_api],
        ["R6", "The interior branch carries both arithmetic bounds", ".interior i.val" in family_api and "by omega" in family_api],
        ["R7", "ClusterTermFamily is total over Fin n", "def ClusterTermFamily (n : Nat) := Fin n → ClusterTerm n" in family_api],
        ["R8", "The canonical family is defined for every n >= 2", "canonicalClusterTermFamily" in family_api and "fun i => ClusterTerm.at hN i" in family_api],
        ["R9", "The canonical family has checked support and max-locality theorems", "canonical_cluster_term_family_locality_in_support_set" in family_api and "canonical_cluster_term_family_max_locality" in family_api],
        ["R10", "The family is total and the transcript is fresh", "canonical_cluster_term_family_is_total" in family_api and transcript.count("END_COMMAND") == 3 and no_warnings and f"SOURCE_SHA256: {source_hash}" in transcript],
    ]
    rows = [{"requirement_id": item[0], "label": item[1], "passed": bool(item[2])} for item in requirements]
    failed = [row["requirement_id"] for row in rows if not row["passed"]]
    zero_returns = all(record["returncode"] == 0 for record in records)
    payload = {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "method": METHOD,
        "status": "term_family_locality_checked_not_hamiltonian_spectral_proof" if not failed else "term_family_locality_failed",
        "model_status": "all_n_fin_indexed_cluster_term_family_checked_under_pinned_lean_lake",
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
            "checked_all_n_term_family_bridge": not failed and zero_returns,
            "index_domain": "Fin n",
            "minimum_n": 2,
            "support_sizes": [2, 3],
            "max_locality": 3,
            "proof_assistant_checked": zero_returns,
            "formal_theorem_proved": False,
            "explicit_not_hamiltonian_spectral_proof": True,
            "quantum_pcp_theorem_claimed": False,
            "nlts_theorem_claimed": False,
            "bqp_separation_claimed": False,
            "validation_error_count": len(failed),
        },
        "claim_boundary": {
            "what_is_supported": "For every n >= 2, Lean checks a canonical Fin n-indexed family whose terms are explicitly boundary or interior constructors, every term has locality in {2,3}, every term has locality at most 3, and the family is total over its index domain.",
            "what_is_not_supported": "This does not define Pauli operators or prove a Hamiltonian term sum, its spectrum, a Quantum PCP theorem, an NLTS theorem, a global gap-amplification impossibility result, or a BQP separation.",
        },
        "requirements": rows,
        "fresh_command_records": records,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# B9 All-n Term-Family Locality Gate",
        "",
        f"- Method: `{METHOD}`",
        f"- Status: `{payload['status']}`",
        f"- Requirements passed/failed: `{len(rows) - len(failed)}` / `{len(failed)}`",
        f"- Fresh Lean/Lake commands returning zero: `{payload['summary']['fresh_zero_returncode_count']}/{len(records)}`",
        f"- Index domain: `{payload['summary']['index_domain']}`",
        f"- Minimum n: `{payload['summary']['minimum_n']}`",
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
