#!/usr/bin/env python3
"""R98: check the operator-labelled Pauli term family bridge."""

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
TRANSCRIPT = ROOT / "results" / "B9_R98_pauli_term_family_transcript.txt"
OUT_JSON = ROOT / "results" / "B9_pauli_term_family_gate_v0.json"
OUT_MD = ROOT / "research" / "B9_pauli_term_family_gate.md"
METHOD = "b9_pauli_term_family_gate_v0"


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

    start = source.index("inductive PauliAxis")
    end = source.index("theorem locality_in_support_set", start)
    operator_api = source[start:end]
    no_warnings = all("warning:" not in record["stdout"] + record["stderr"] for record in records)
    requirements = [
        ["R1", "Lean/Lake version probes return zero", all(record["returncode"] == 0 for record in records[:2])],
        ["R2", "The B9 module returns zero", records[2]["returncode"] == 0],
        ["R3", "PauliAxis exposes X and Z labels", "| x" in operator_api and "| z" in operator_api],
        ["R4", "PauliFactor carries a Fin n site", "structure PauliFactor (n : Nat)" in operator_api and "site : Fin n" in operator_api],
        ["R5", "PauliTerm carries an explicit factor list", "structure PauliTerm (n : Nat)" in operator_api and "factors : List" in operator_api],
        ["R6", "ClusterTerm maps to explicit Z-X-Z or boundary factors", "def ClusterTerm.toPauliTerm" in operator_api and "axis := .z" in operator_api and "axis := .x" in operator_api],
        ["R7", "The operator term locality equals source term locality", "cluster_term_to_pauli_term_locality" in operator_api and "term.toPauliTerm.locality = term.locality" in operator_api],
        ["R8", "HamiltonianTermFamily is Fin n-indexed", "def HamiltonianTermFamily (n : Nat) := Fin n → PauliTerm n" in operator_api and "canonicalHamiltonianTermFamily" in operator_api],
        ["R9", "The canonical operator family has support and max-locality theorems", "canonical_hamiltonian_term_family_locality_in_support_set" in operator_api and "canonical_hamiltonian_term_family_max_locality" in operator_api],
        ["R10", "The operator family is total and the transcript is fresh", "canonical_hamiltonian_term_family_is_total" in operator_api and transcript.count("END_COMMAND") == 3 and no_warnings and f"SOURCE_SHA256: {source_hash}" in transcript],
    ]
    rows = [{"requirement_id": item[0], "label": item[1], "passed": bool(item[2])} for item in requirements]
    failed = [row["requirement_id"] for row in rows if not row["passed"]]
    zero_returns = all(record["returncode"] == 0 for record in records)
    payload = {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "method": METHOD,
        "status": "pauli_term_family_checked_not_hamiltonian_spectral_proof" if not failed else "pauli_term_family_failed",
        "model_status": "fin_indexed_pauli_labelled_term_family_checked_under_pinned_lean_lake",
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
            "checked_pauli_term_family_bridge": not failed and zero_returns,
            "index_domain": "Fin n",
            "factor_alphabet": ["X", "Z"],
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
            "what_is_supported": "Lean checks an all-n Fin n-indexed family of Pauli-labelled term descriptors: interior terms carry explicit Z-X-Z factors, boundaries carry two factors, factor-list locality matches the source ClusterTerm locality, and the family is total with support at most 3.",
            "what_is_not_supported": "The descriptors are not yet matrices or an operator algebra. This does not define a Hamiltonian sum, prove Hermiticity or spectrum, prove Quantum PCP or NLTS, prove a global impossibility result, or establish BQP separation.",
        },
        "requirements": rows,
        "fresh_command_records": records,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# B9 Pauli-Term Family Gate",
        "",
        f"- Method: `{METHOD}`",
        f"- Status: `{payload['status']}`",
        f"- Requirements passed/failed: `{len(rows) - len(failed)}` / `{len(failed)}`",
        f"- Fresh Lean/Lake commands returning zero: `{payload['summary']['fresh_zero_returncode_count']}/{len(records)}`",
        f"- Index domain: `{payload['summary']['index_domain']}`",
        f"- Factor alphabet: `{payload['summary']['factor_alphabet']}`",
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
    raise SystemExit(main())
