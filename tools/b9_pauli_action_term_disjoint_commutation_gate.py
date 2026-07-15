#!/usr/bin/env python3
"""R102-B9: check term-level disjoint Pauli replay commutation."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAKEFILE = ROOT / "lakefile.lean"
WIDTH_SOURCE = ROOT / "B9" / "ClusterStabilizer" / "WidthLocality.lean"
BASIS_SOURCE = ROOT / "B9" / "ClusterStabilizer" / "PauliBasisAction.lean"
COMPOSITION_SOURCE = ROOT / "B9" / "ClusterStabilizer" / "PauliActionComposition.lean"
COMMUTATION_SOURCE = ROOT / "B9" / "ClusterStabilizer" / "PauliActionCommutation.lean"
SOURCE = ROOT / "B9" / "ClusterStabilizer" / "PauliActionTermCommutation.lean"
TRANSCRIPT = ROOT / "results" / "B9_R102_term_disjoint_commutation_transcript.txt"
OUT_JSON = ROOT / "results" / "B9_pauli_action_term_disjoint_commutation_gate_v0.json"
OUT_MD = ROOT / "research" / "B9_pauli_action_term_disjoint_commutation_gate.md"
METHOD = "b9_pauli_action_term_disjoint_commutation_gate_v0"
STATUS = "pauli_action_term_disjoint_commutation_checked_not_linear_or_spectral_proof"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> dict[str, Any]:
    started = time.time()
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if command[0].endswith("/lean"):
        executable = "~/.elan/bin/lean"
    elif command[0].endswith("/lake"):
        executable = "~/.elan/bin/lake"
    else:
        executable = command[0]
    return {
        "command": [executable, *command[1:]],
        "returncode": completed.returncode,
        "elapsed_seconds": round(time.time() - started, 6),
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def build() -> dict[str, Any]:
    source = SOURCE.read_text(encoding="utf-8")
    source_hashes = {
        "lakefile_sha256": sha256_file(LAKEFILE),
        "width_source_sha256": sha256_file(WIDTH_SOURCE),
        "basis_source_sha256": sha256_file(BASIS_SOURCE),
        "composition_source_sha256": sha256_file(COMPOSITION_SOURCE),
        "commutation_source_sha256": sha256_file(COMMUTATION_SOURCE),
        "source_sha256": sha256_file(SOURCE),
    }
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
            f"lake env lean -o {build_dir}/PauliBasisAction.olean "
            "B9/ClusterStabilizer/PauliBasisAction.lean && "
            f"lake env lean -o {build_dir}/PauliActionComposition.olean "
            "B9/ClusterStabilizer/PauliActionComposition.lean && "
            f"lake env lean -o {build_dir}/PauliActionCommutation.olean "
            "B9/ClusterStabilizer/PauliActionCommutation.lean && "
            "lake env lean B9/ClusterStabilizer/PauliActionTermCommutation.lean",
        ],
    ]
    records = [run(command) for command in commands]
    transcript_parts = [*(f"{key.upper()}: {value}" for key, value in source_hashes.items()), ""]
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
        ["R2", "All five B9 modules compile together", records[2]["returncode"] == 0],
        ["R3", "The source defines a factor-to-term disjointness predicate", "def PauliFactor.disjointTerm" in source],
        ["R4", "A factor commutes with an entire disjoint term", "theorem pauli_factor_term_disjoint_commute" in source],
        ["R5", "The theorem reuses the prior factor-level commutation proof", "pauli_factor_act_disjoint_commute" in source],
        ["R6", "The theorem reuses compositional replay associativity", "basis_action_compose_assoc" in source],
        ["R7", "The source proves whole-term disjoint replay commutation", "theorem pauli_term_basis_action_disjoint_commute" in source],
        ["R8", "The term theorem quantifies over both site supports", "leftSite ∈ left.siteSupport" in source and "rightSite ∈ right.siteSupport" in source],
        ["R9", "The checked module contains no matrix or complex-amplitude machinery", "Matrix" not in source and "Complex" not in source],
        ["R10", "Fresh transcript binds every source and project hash", transcript.count("END_COMMAND") == 3 and all(f"{key.upper()}: {value}" in transcript for key, value in source_hashes.items())],
        ["R11", "The proof is finite replay semantics rather than a spectral theorem", "BasisAction" in source and "Hamiltonian" not in source],
        ["R12", "The source does not claim BQP or Quantum PCP resolution", "BQP" not in source and "Quantum PCP" not in source],
    ]
    rows = [{"requirement_id": item[0], "label": item[1], "passed": bool(item[2])} for item in requirements]
    failed = [row["requirement_id"] for row in rows if not row["passed"]]
    zero_returns = all(record["returncode"] == 0 for record in records)
    payload = {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "method": METHOD,
        "status": STATUS if not failed else "pauli_action_term_disjoint_commutation_failed",
        "model_status": "computational_basis_term_disjoint_pauli_replay_commutation_checked_under_pinned_lean_lake",
        "workload": str(SOURCE.relative_to(ROOT)),
        "summary": {
            "requirement_count": len(rows),
            "requirements_passed": len(rows) - len(failed),
            "requirements_failed": len(failed),
            "failed_requirement_ids": failed,
            "fresh_command_count": len(records),
            "fresh_zero_returncode_count": sum(record["returncode"] == 0 for record in records),
            "fresh_no_warning": no_warnings,
            **source_hashes,
            "transcript_sha256": sha256_file(TRANSCRIPT),
            "checked_term_disjoint_commutation": not failed and zero_returns,
            "proof_assistant_checked": zero_returns,
            "formal_theorem_proved": False,
            "explicit_not_linear_or_spectral_proof": True,
            "quantum_pcp_theorem_claimed": False,
            "nlts_theorem_claimed": False,
            "bqp_separation_claimed": False,
            "validation_error_count": len(failed),
        },
        "claim_boundary": {
            "what_is_supported": "Lean checks that two Pauli terms with disjoint site supports commute under the restricted computational-basis replay, including final basis state and accumulated phase.",
            "what_is_not_supported": "This is still a finite computational-basis action model, not a complex linear operator, Hamiltonian sum, Hermiticity proof, spectral theorem, Quantum PCP/NLTS theorem, global impossibility result, BQP separation, or quantum-advantage claim.",
        },
        "requirements": rows,
        "fresh_command_records": records,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# B9 Term-Level Disjoint Pauli Action Commutation Gate",
        "",
        f"- Method: `{METHOD}`",
        f"- Status: `{payload['status']}`",
        f"- Requirements passed/failed: `{len(rows) - len(failed)}` / `{len(failed)}`",
        f"- Fresh Lean/Lake commands returning zero: `{payload['summary']['fresh_zero_returncode_count']}/{len(records)}`",
        f"- Source SHA256: `{source_hashes['source_sha256']}`",
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
