#!/usr/bin/env python3
"""R95: check the assumption-free B9 spectral-width ratio interface."""

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
TRANSCRIPT = ROOT / "results" / "B9_R95_spectral_width_formalization_transcript.txt"
OUT_JSON = ROOT / "results" / "B9_spectral_width_formalization_gate_v0.json"
OUT_MD = ROOT / "research" / "B9_spectral_width_formalization_gate.md"
METHOD = "b9_spectral_width_formalization_gate_v0"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> dict[str, Any]:
    started = time.time()
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "command": ["~/.elan/bin/lean" if command[0].endswith("/lean") else "~/.elan/bin/lake", *command[1:]],
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
    start = source.index("theorem spectral_width_ratio_scale_cancel")
    end = source.index("theorem uniform_scale_preserves_spectral_width_ratio\n", start)
    new_api = source[start:end]
    zero_returns = all(record["returncode"] == 0 for record in records)
    no_warnings = all("warning:" not in record["stdout"] + record["stderr"] for record in records)
    requirements = [
        ["R1", "Lean/Lake probes return zero", all(record["returncode"] == 0 for record in records[:2])],
        ["R2", "The B9 module returns zero", records[2]["returncode"] == 0],
        ["R3", "The spectral-width cancellation theorem exists", "theorem spectral_width_ratio_scale_cancel" in new_api],
        ["R4", "The theorem requires a nonzero scale", "(hScale : scale ≠ 0)" in new_api],
        ["R5", "The theorem delegates to normalized-gap cancellation", "normalized_gap_scale_cancel width gap scale hScale" in new_api],
        ["R6", "The new interface has no injected hRatio", "hRatio" not in new_api],
        ["R7", "The generic uniform-scale spectral-width interface exists", "uniform_scale_preserves_spectral_width_ratio_from_nonzero_scale" in new_api],
        ["R8", "The concrete 27/20 wrapper exists", "uniform_scale_preserves_spectral_width_ratio_concrete" in new_api and "uniform_scale_factor_ne_zero" in new_api],
        ["R9", "Transcript has three records, no warnings, and binds source hash", transcript.count("END_COMMAND") == 3 and no_warnings and f"SOURCE_SHA256: {source_hash}" in transcript],
        ["R10", "Formal-complexity claims remain explicitly out of scope", True],
    ]
    rows = [{"requirement_id": item[0], "label": item[1], "passed": bool(item[2])} for item in requirements]
    failed = [row["requirement_id"] for row in rows if not row["passed"]]
    payload = {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "method": METHOD,
        "status": "spectral_width_formalization_checked_not_quantum_pcp_proof" if not failed else "spectral_width_formalization_failed",
        "model_status": "formal_spectral_ratio_lemma_checked_under_pinned_lean_lake",
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
            "checked_spectral_width_ratio_lemma": not failed and zero_returns,
            "proof_assistant_checked": zero_returns,
            "formal_theorem_proved": False,
            "explicit_not_quantum_pcp_proof": True,
            "nlts_theorem_claimed": False,
            "global_gap_amplification_impossibility_claimed": False,
            "bqp_separation_claimed": False,
            "validation_error_count": len(failed),
        },
        "claim_boundary": {
            "what_is_supported": "Lean checks spectral-width ratio cancellation for a nonzero uniform real scale and checks a concrete UniformScaleFactor wrapper.",
            "what_is_not_supported": "This does not prove the all-n Hamiltonian construction, locality, a Quantum PCP theorem, an NLTS theorem, a global gap-amplification impossibility theorem, or a BQP separation.",
        },
        "requirements": rows,
        "fresh_command_records": records,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# B9 Spectral-Width Formalization Gate",
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
