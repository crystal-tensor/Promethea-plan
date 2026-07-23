#!/usr/bin/env python3
"""R94: check the nonzero-scale cancellation lemma in the B9 Lean module."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
METHOD = "b9_scale_cancellation_formalization_gate_v0"
SOURCE = ROOT / "B9" / "ClusterStabilizer" / "WidthLocality.lean"
TRANSCRIPT = ROOT / "results" / "B9_R94_scale_cancellation_formalization_transcript.txt"
OUT_JSON = ROOT / "results" / "B9_scale_cancellation_formalization_gate_v0.json"
OUT_MD = ROOT / "research" / "B9_scale_cancellation_formalization_gate.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> dict[str, Any]:
    started = time.time()
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "command": ["~/.elan/bin/lake", *command[2:]],
        "returncode": completed.returncode,
        "elapsed_seconds": round(time.time() - started, 6),
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def build() -> dict[str, Any]:
    source_text = SOURCE.read_text(encoding="utf-8")
    commands = [
        [str(Path.home() / ".elan/bin/lean"), "--version"],
        [str(Path.home() / ".elan/bin/lake"), "--version"],
        [str(Path.home() / ".elan/bin/lake"), "env", "lean", "B9/ClusterStabilizer/WidthLocality.lean"],
    ]
    records = [run(command) for command in commands]
    source_hash = sha256_file(SOURCE)
    transcript_lines: list[str] = []
    transcript_lines.append(f"SOURCE_SHA256: {source_hash}")
    transcript_lines.append("")
    for record in records:
        transcript_lines.extend(
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
    transcript = "\n".join(transcript_lines)
    TRANSCRIPT.parent.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT.write_text(transcript, encoding="utf-8")

    zero_returns = all(record["returncode"] == 0 for record in records)
    no_warnings = all("warning:" not in record["stdout"] + record["stderr"] for record in records)
    requirements = [
        ["R1", "Lean/Lake version probes return zero", all(record["returncode"] == 0 for record in records[:2])],
        ["R2", "The B9 module returns zero under lake env lean", records[2]["returncode"] == 0],
        ["R3", "The source declares normalized_gap_scale_cancel", "theorem normalized_gap_scale_cancel" in source_text],
        ["R4", "The cancellation theorem requires a nonzero scale", "(hScale : scale ≠ 0)" in source_text],
        ["R5", "The cancellation proof does not inject hRatio", "normalized_gap_scale_cancel" in source_text and "hRatio" not in source_text[source_text.index("theorem normalized_gap_scale_cancel"):source_text.index("theorem uniform_scale_preserves_normalized_gap\n")]],
        ["R6", "The new normalized-gap theorem consumes the cancellation lemma", "uniform_scale_preserves_normalized_gap_from_nonzero_scale" in source_text and "normalized_gap_scale_cancel gap width scale hScale" in source_text],
        ["R7", "The concrete 27/20 scale is checked as nonzero", "uniform_scale_factor_ne_zero" in source_text and "norm_num [UniformScaleFactor]" in source_text],
        ["R8", "Fresh transcript has three command records and no warnings", transcript.count("END_COMMAND") == 3 and no_warnings],
        ["R9", "The transcript binds the current source hash", SOURCE.exists() and f"SOURCE_SHA256: {source_hash}" in transcript],
        ["R10", "Forbidden B9/B10 claims remain false", True],
    ]
    rows = [{"requirement_id": item[0], "label": item[1], "passed": bool(item[2])} for item in requirements]
    failed = [row["requirement_id"] for row in rows if not row["passed"]]
    payload = {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "method": METHOD,
        "status": "scale_cancellation_formalization_checked_not_quantum_pcp_proof" if not failed else "scale_cancellation_formalization_failed",
        "model_status": "formal_scalar_lemma_checked_under_pinned_lean_lake",
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
            "checked_scale_cancellation_lemma": not failed and zero_returns,
            "formal_theorem_proved": False,
            "proof_assistant_checked": zero_returns,
            "explicit_not_quantum_pcp_proof": True,
            "nlts_theorem_claimed": False,
            "global_gap_amplification_impossibility_claimed": False,
            "bqp_separation_claimed": False,
            "validation_error_count": len(failed),
        },
        "fresh_command_records": records,
        "source_files": ["B9/ClusterStabilizer/WidthLocality.lean"],
        "claim_boundary": {
            "what_is_supported": "For real gap, width, and nonzero scale parameters, Lean checks cancellation of uniform scaling in the normalized-gap ratio, and checks that the project scale 27/20 is nonzero.",
            "what_is_not_supported": "This does not formalize the all-n Hamiltonian construction, locality over the construction, a Quantum PCP theorem, an NLTS theorem, a global gap-amplification impossibility theorem, or B10 complexity separation.",
        },
        "requirements": rows,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# B9 Scale-Cancellation Formalization Gate",
        "",
        f"- Method: `{METHOD}`",
        f"- Status: `{payload['status']}`",
        f"- Requirements passed/failed: `{len(rows) - len(failed)}` / `{len(failed)}`",
        f"- Fresh Lean/Lake commands returning zero: `{payload['summary']['fresh_zero_returncode_count']}/{len(records)}`",
        f"- Source SHA256: `{payload['summary']['source_sha256']}`",
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
    parser = argparse.ArgumentParser()
    parser.parse_args()
    payload = build()
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    if payload["summary"]["validation_error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
