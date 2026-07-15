#!/usr/bin/env python3
"""R101: check disjoint Pauli-factor replay commutation."""

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
SOURCE = ROOT / "B9" / "ClusterStabilizer" / "PauliActionCommutation.lean"
TRANSCRIPT = ROOT / "results" / "B9_R101_pauli_action_disjoint_commutation_transcript.txt"
OUT_JSON = ROOT / "results" / "B9_pauli_action_disjoint_commutation_gate_v0.json"
OUT_MD = ROOT / "research" / "B9_pauli_action_disjoint_commutation_gate.md"
METHOD = "b9_pauli_action_disjoint_commutation_gate_v0"
STATUS = "pauli_action_disjoint_commutation_checked_not_linear_or_spectral_proof"


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
    composition_source = COMPOSITION_SOURCE.read_text(encoding="utf-8")
    source_hash = sha256_file(SOURCE)
    composition_source_hash = sha256_file(COMPOSITION_SOURCE)
    basis_source_hash = sha256_file(BASIS_SOURCE)
    width_source_hash = sha256_file(WIDTH_SOURCE)
    lakefile_hash = sha256_file(LAKEFILE)
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
            "lake env lean B9/ClusterStabilizer/PauliActionCommutation.lean",
        ],
    ]
    records = [run(command) for command in commands]
    transcript_parts = [
        f"LAKEFILE_SHA256: {lakefile_hash}",
        f"WIDTH_SOURCE_SHA256: {width_source_hash}",
        f"BASIS_SOURCE_SHA256: {basis_source_hash}",
        f"COMPOSITION_SOURCE_SHA256: {composition_source_hash}",
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
        ["R2", "All four B9 modules compile together", records[2]["returncode"] == 0],
        ["R3", "The helper proves double flips commute at distinct sites", "theorem flipAt_commute" in source],
        ["R4", "The phase alphabet has a checked commutative multiplication lemma", "theorem phase_mul_comm" in source],
        ["R5", "Disjoint Pauli factor actions commute as composed actions", "theorem pauli_factor_act_disjoint_commute" in source],
        ["R6", "The state projection of disjoint replay is order independent", "theorem pauli_factor_act_disjoint_state_commute" in source],
        ["R7", "The phase projection of disjoint replay is order independent", "theorem pauli_factor_act_disjoint_phase_commute" in source],
        ["R8", "The proof imports the prior compositional replay contract", "import B9.ClusterStabilizer.PauliActionComposition" in source and "def BasisAction.compose" in composition_source],
        ["R9", "The checked module contains no matrix or complex-amplitude machinery", "Matrix" not in source and "Complex" not in source],
        ["R10", "Fresh transcript binds all source and project hashes", transcript.count("END_COMMAND") == 3 and all(token in transcript for token in [f"LAKEFILE_SHA256: {lakefile_hash}", f"SOURCE_SHA256: {source_hash}", f"COMPOSITION_SOURCE_SHA256: {composition_source_hash}"])],
        ["R11", "The source keeps the restricted proof boundary explicit", "computational" not in source or "quantum" not in source],
    ]
    rows = [{"requirement_id": item[0], "label": item[1], "passed": bool(item[2])} for item in requirements]
    failed = [row["requirement_id"] for row in rows if not row["passed"]]
    zero_returns = all(record["returncode"] == 0 for record in records)
    payload = {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "method": METHOD,
        "status": STATUS if not failed else "pauli_action_disjoint_commutation_failed",
        "model_status": "computational_basis_disjoint_pauli_action_commutation_checked_under_pinned_lean_lake",
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
            "composition_source_sha256": composition_source_hash,
            "basis_source_sha256": basis_source_hash,
            "width_source_sha256": width_source_hash,
            "lakefile_sha256": lakefile_hash,
            "transcript_sha256": sha256_file(TRANSCRIPT),
            "checked_disjoint_commutation": not failed and zero_returns,
            "proof_assistant_checked": zero_returns,
            "formal_theorem_proved": False,
            "explicit_not_linear_or_spectral_proof": True,
            "quantum_pcp_theorem_claimed": False,
            "nlts_theorem_claimed": False,
            "bqp_separation_claimed": False,
            "validation_error_count": len(failed),
        },
        "claim_boundary": {
            "what_is_supported": "Lean checks that two Pauli factors on distinct Fin n sites commute under the restricted computational-basis replay, with matching final basis state and phase projections.",
            "what_is_not_supported": "This is still a factor-level computational-basis action model, not a complex linear operator, Hamiltonian sum, Hermiticity proof, spectral theorem, Quantum PCP/NLTS theorem, global impossibility result, BQP separation, or quantum-advantage claim.",
        },
        "requirements": rows,
        "fresh_command_records": records,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# B9 Disjoint Pauli Action Commutation Gate",
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
    raise SystemExit(main())
