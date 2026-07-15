#!/usr/bin/env python3
"""R99: check executable computational-basis action for Pauli term descriptors."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WIDTH_SOURCE = ROOT / "B9" / "ClusterStabilizer" / "WidthLocality.lean"
SOURCE = ROOT / "B9" / "ClusterStabilizer" / "PauliBasisAction.lean"
TRANSCRIPT = ROOT / "results" / "B9_R99_pauli_basis_action_transcript.txt"
OUT_JSON = ROOT / "results" / "B9_pauli_basis_action_gate_v0.json"
OUT_MD = ROOT / "research" / "B9_pauli_basis_action_gate.md"
METHOD = "b9_pauli_basis_action_gate_v0"


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
    width_source = WIDTH_SOURCE.read_text(encoding="utf-8")
    source_hash = sha256_file(SOURCE)
    width_source_hash = sha256_file(WIDTH_SOURCE)
    build_dir = ".lake/build/lib/B9/ClusterStabilizer"
    commands = [
        [str(Path.home() / ".elan/bin/lean"), "--version"],
        [str(Path.home() / ".elan/bin/lake"), "--version"],
        [
            "sh",
            "-c",
            f"mkdir -p {build_dir} && "
            f"lake env lean -o {build_dir}/WidthLocality.olean "
            "B9/ClusterStabilizer/WidthLocality.lean && "
            "lake env lean B9/ClusterStabilizer/PauliBasisAction.lean",
        ],
    ]
    records = [run(command) for command in commands]
    transcript_parts = [
        f"WIDTH_SOURCE_SHA256: {width_source_hash}",
        f"SOURCE_SHA256: {source_hash}",
        "",
    ]
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

    no_warnings = all("warning:" not in record["stdout"] + record["stderr"] for record in records)
    requirements = [
        ["R1", "Lean and Lake version probes return zero", all(record["returncode"] == 0 for record in records[:2])],
        ["R2", "WidthLocality and PauliBasisAction compile together", records[2]["returncode"] == 0],
        ["R3", "BasisState is a Fin n computational basis", "def BasisState (n : Nat) := Fin n -> Bool" in source],
        ["R4", "Phase has plus/minus and bit interpretation", "inductive Phase" in source and "def Phase.ofBit" in source],
        ["R5", "X flips one site", "def flipAt" in source and "| .x => { phase := .plus" in source],
        ["R6", "Z records a basis-bit phase and preserves the state", "| .z => { phase := Phase.ofBit" in source],
        ["R7", "Pauli terms have recursive basis action", "def PauliTerm.basisAction" in source and "theorem pauli_term_basis_action_cons" in source],
        ["R8", "Single-factor action is local", "pauli_factor_act_agrees_outside" in source],
        ["R9", "Term action preserves basis bits outside its site support", "pauli_term_basis_action_agrees_outside" in source and "def PauliTerm.siteSupport" in source],
        ["R10", "Action is total and transcript is fresh", "pauli_term_basis_action_is_total" in source and transcript.count("END_COMMAND") == 3 and no_warnings and f"SOURCE_SHA256: {source_hash}" in transcript],
    ]
    rows = [{"requirement_id": item[0], "label": item[1], "passed": bool(item[2])} for item in requirements]
    failed = [row["requirement_id"] for row in rows if not row["passed"]]
    zero_returns = all(record["returncode"] == 0 for record in records)
    payload = {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "method": METHOD,
        "status": "pauli_basis_action_checked_not_matrix_or_spectral_proof" if not failed else "pauli_basis_action_failed",
        "model_status": "computational_basis_pauli_action_checked_under_pinned_lean_lake",
        "workload": str(SOURCE.relative_to(ROOT)),
        "summary": {
            "requirement_count": len(rows),
            "requirements_passed": len(rows) - len(failed),
            "requirements_failed": len(failed),
            "failed_requirement_ids": failed,
            "fresh_command_count": len(records),
            "fresh_zero_returncode_count": sum(record["returncode"] == 0 for record in records),
            "fresh_no_warning": no_warnings,
            "source_sha256": source_hash,
            "width_source_sha256": width_source_hash,
            "transcript_sha256": sha256_file(TRANSCRIPT),
            "checked_pauli_basis_action": not failed and zero_returns,
            "basis_domain": "Fin n -> Bool",
            "phase_alphabet": ["plus", "minus"],
            "factor_alphabet": ["X", "Z"],
            "proof_assistant_checked": zero_returns,
            "formal_theorem_proved": False,
            "explicit_not_matrix_or_spectral_proof": True,
            "quantum_pcp_theorem_claimed": False,
            "nlts_theorem_claimed": False,
            "bqp_separation_claimed": False,
            "validation_error_count": len(failed),
        },
        "claim_boundary": {
            "what_is_supported": "Lean checks a total recursive action of Pauli-labelled terms on computational-basis bitstrings: X flips its site, Z preserves the bitstring while recording a sign phase, and the final state agrees with the input outside the finite factor site support.",
            "what_is_not_supported": "This is a computational-basis action model, not a complex matrix, linear operator, Hamiltonian sum, Hermiticity proof, spectral theorem, Quantum PCP/NLTS theorem, global impossibility result, or BQP separation.",
        },
        "requirements": rows,
        "fresh_command_records": records,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# B9 Pauli Basis Action Gate",
        "",
        f"- Method: `{METHOD}`",
        f"- Status: `{payload['status']}`",
        f"- Requirements passed/failed: `{len(rows) - len(failed)}` / `{len(failed)}`",
        f"- Fresh Lean/Lake commands returning zero: `{payload['summary']['fresh_zero_returncode_count']}/{len(records)}`",
        f"- Basis domain: `{payload['summary']['basis_domain']}`",
        f"- Phase alphabet: `{payload['summary']['phase_alphabet']}`",
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
