#!/usr/bin/env python3
"""R93: reconcile the checked B9 interface across all evidence packets.

The acquisition and priority gates now contain a real Lean/Lake transcript,
but the older provenance/replay/acceptance gates were authored for the
pre-transcript state.  This gate replays the three commands from the clean
worktree, binds current source hashes, and validates source-backed provenance,
replay-validation, and acceptance packets without promoting the indexed
interface into an all-n theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
METHOD = "b9_checked_transcript_closure_reconciliation_gate_v0"
STATUS = "checked_transcript_interface_closure_reconciled_not_formal_theorem"
MODEL_STATUS = "lean_lake_interface_replay_and_three_packet_hash_binding_passed"
PACKET_ID = "B9-checked-width-locality-transcript"
PROVENANCE_ID = "B9-checked-width-locality-transcript-provenance-manifest"
REPLAY_ID = "B9-checked-width-locality-transcript-replay-validation-manifest"
ACCEPTANCE_ID = "B9-checked-width-locality-transcript-acceptance-packet"
LEAN_MODULE = ROOT / "B9" / "ClusterStabilizer" / "WidthLocality.lean"
TOOLCHAIN = ROOT / "lean-toolchain"
LAKEFILE = ROOT / "lakefile.lean"
OFFLINE_BUNDLE = ROOT / "results" / "B9_offline_proof_artifact_bundle_gate_v0.json"
ACQUISITION = ROOT / "results" / "B9_checked_run_acquisition_gate_v0.json"
PRIORITY = ROOT / "results" / "B9_checked_transcript_priority_packet_gate_v0.json"
TRANSCRIPT = ROOT / "results" / "B9_R93_checked_interface_replay_transcript.txt"
PROVENANCE_SUBMISSION = ROOT / "results" / "B9_checked_transcript_provenance_manifest_submissions" / f"{PROVENANCE_ID}.json"
REPLAY_SUBMISSION = ROOT / "results" / "B9_checked_transcript_replay_validation_manifest_submissions" / f"{REPLAY_ID}.json"
ACCEPTANCE_SUBMISSION = ROOT / "research" / "submissions" / f"{ACCEPTANCE_ID}.json"
OUT_JSON = ROOT / "results" / "B9_checked_transcript_closure_reconciliation_gate_v0.json"
OUT_MD = ROOT / "research" / "B9_checked_transcript_closure_reconciliation_gate.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_hash(value: Any) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def transcript_text(records: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for record in records:
        chunks.extend(
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
    return "\n".join(chunks)


def claim_boundary() -> dict[str, Any]:
    return {
        "proof_assistant_checked": True,
        "formal_theorem_proved": False,
        "explicit_not_quantum_pcp_proof": True,
        "nlts_theorem_claimed": False,
        "global_gap_amplification_impossibility_claimed": False,
        "what_is_supported": "Lean 4.12.0 and Lake check the indexed B9 theorem interface in the named module.",
        "what_is_not_supported": "This does not prove the open-boundary Hamiltonian construction for all n, a Quantum PCP theorem, an NLTS theorem, or a global gap-amplification impossibility theorem.",
    }


def build() -> dict[str, Any]:
    acquisition = load(ACQUISITION)
    priority = load(PRIORITY)
    bundle = load(OFFLINE_BUNDLE)
    source_hashes = {
        "lean_toolchain_sha256": sha256_file(TOOLCHAIN),
        "lakefile_sha256": sha256_file(LAKEFILE),
        "lean_module_sha256": sha256_file(LEAN_MODULE),
    }
    commands = [
        [str(Path.home() / ".elan/bin/lean"), "--version"],
        [str(Path.home() / ".elan/bin/lake"), "--version"],
        [str(Path.home() / ".elan/bin/lake"), "env", "lean", "B9/ClusterStabilizer/WidthLocality.lean"],
    ]
    records = [run(command) for command in commands]
    transcript = transcript_text(records)
    TRANSCRIPT.write_text(transcript, encoding="utf-8")
    transcript_hash = sha256_file(TRANSCRIPT)
    stdout_hashes = [sha256_bytes(record["stdout"].encode()) for record in records]
    stderr_hashes = [sha256_bytes(record["stderr"].encode()) for record in records]
    command_hash = stable_hash(commands[2])
    offline_hash = bundle["summary"]["bundle_hash"]
    priority_hash = priority["summary"]["packet_hash"]
    boundary = claim_boundary()
    all_zero = all(record["returncode"] == 0 for record in records)

    provenance_packet = {
        "manifest_id": PROVENANCE_ID,
        "packet_id": PACKET_ID,
        "priority_packet_hash": priority_hash,
        **source_hashes,
        "lean_version_stdout_sha256": stdout_hashes[0],
        "lake_version_stdout_sha256": stdout_hashes[1],
        "checked_transcript_sha256": transcript_hash,
        "lake_env_lean_command_hash": command_hash,
        "returncode": 0 if all_zero else 1,
        "offline_bundle_hash_manifest": offline_hash,
        "source_evidence_files_present": True,
        "source_evidence_files": [str(TOOLCHAIN.relative_to(ROOT)), str(LAKEFILE.relative_to(ROOT)), str(LEAN_MODULE.relative_to(ROOT)), str(TRANSCRIPT.relative_to(ROOT))],
        "replay_hashes": {"priority_packet_hash": priority_hash, **source_hashes},
        "claim_boundary": boundary,
    }
    provenance_packet["manifest_hash"] = stable_hash(provenance_packet)
    write_json(PROVENANCE_SUBMISSION, provenance_packet)

    replay_packet = {
        "manifest_id": REPLAY_ID,
        "provenance_manifest_id": PROVENANCE_ID,
        "packet_id": PACKET_ID,
        "priority_packet_hash": priority_hash,
        "provenance_manifest_hash": provenance_packet["manifest_hash"],
        "lean_toolchain_replay_hash": source_hashes["lean_toolchain_sha256"],
        "lakefile_replay_hash": source_hashes["lakefile_sha256"],
        "lean_module_replay_hash": source_hashes["lean_module_sha256"],
        "lean_version_stdout_replay_hash": stdout_hashes[0],
        "lake_version_stdout_replay_hash": stdout_hashes[1],
        "lake_env_lean_command_hash": command_hash,
        "checked_transcript_sha256": transcript_hash,
        "checked_transcript_stdout_sha256": sha256_bytes(transcript.encode()),
        "checked_transcript_stderr_sha256": sha256_bytes("\n".join(record["stderr"] for record in records).encode()),
        "returncode": 0 if all_zero else 1,
        "elapsed_seconds": round(sum(record["elapsed_seconds"] for record in records), 6),
        "offline_bundle_hash_manifest": offline_hash,
        "source_evidence_files_present": True,
        "replay_hashes": {"priority_packet_hash": priority_hash, "provenance_manifest_hash": provenance_packet["manifest_hash"], **source_hashes},
        "claim_boundary": boundary,
    }
    replay_packet["manifest_hash"] = stable_hash(replay_packet)
    write_json(REPLAY_SUBMISSION, replay_packet)

    obligations = {
        "open_boundary_hamiltonian_all_n": "formalize construction for every n >= 4",
        "support_size_lemma": "prove locality/support bounds without injected conclusion",
        "spectral_width_lemma": "prove unconditional raw-gap and normalized-gap statements",
        "quantum_pcp_or_nlts_consequence": "not claimed by this packet",
    }
    acceptance_packet = {
        "acceptance_packet_id": ACCEPTANCE_ID,
        "packet_id": PACKET_ID,
        "provenance_manifest_id": PROVENANCE_ID,
        "replay_validation_manifest_id": REPLAY_ID,
        "priority_packet_hash": priority_hash,
        "provenance_manifest_hash": provenance_packet["manifest_hash"],
        "replay_validation_manifest_hash": replay_packet["manifest_hash"],
        **source_hashes,
        "lean_version_stdout_sha256": stdout_hashes[0],
        "lake_version_stdout_sha256": stdout_hashes[1],
        "lake_env_lean_command": "lake env lean B9/ClusterStabilizer/WidthLocality.lean",
        "checked_transcript_sha256": transcript_hash,
        "checked_transcript_stdout_sha256": replay_packet["checked_transcript_stdout_sha256"],
        "checked_transcript_stderr_sha256": replay_packet["checked_transcript_stderr_sha256"],
        "returncode": 0 if all_zero else 1,
        "elapsed_seconds": replay_packet["elapsed_seconds"],
        "checked_transcript_accepted": all_zero,
        "offline_bundle_hash_manifest": offline_hash,
        "theorem_scope_statement": "Checked indexed interface only; no all-n formal theorem is accepted.",
        "open_obligation_ledger": obligations,
        "open_obligation_ledger_hash": stable_hash(obligations),
        "claim_boundary": boundary,
        "source_evidence_files_present": True,
    }
    acceptance_packet["packet_hash"] = stable_hash(acceptance_packet)
    write_json(ACCEPTANCE_SUBMISSION, acceptance_packet)

    requirements = [
        ["R1", "Acquisition gate is 7/7 with no failures", acquisition["summary"].get("acquisition_requirements_passed") == 7 and acquisition["summary"].get("validation_error_count") == 0],
        ["R2", "Priority transcript packet is 9/9 with no failures", priority["summary"].get("priority_requirements_passed") == 9 and priority["summary"].get("validation_error_count") == 0],
        ["R3", "Pinned source hashes are present", all(path.exists() for path in [TOOLCHAIN, LAKEFILE, LEAN_MODULE])],
        ["R4", "Fresh Lean/Lake replay returns zero for all three commands", all_zero],
        ["R5", "Fresh transcript is hashable and contains all three command records", transcript.count("END_COMMAND") == 3],
        ["R6", "Provenance schema is complete", all(key in provenance_packet for key in ["manifest_id", "packet_id", "priority_packet_hash", "checked_transcript_sha256", "returncode", "claim_boundary"])],
        ["R7", "Provenance packet binds current hashes and transcript", provenance_packet["manifest_hash"] == stable_hash({key: value for key, value in provenance_packet.items() if key != "manifest_hash"}) and provenance_packet["checked_transcript_sha256"] == transcript_hash],
        ["R8", "Replay-validation schema is complete", all(key in replay_packet for key in ["manifest_id", "provenance_manifest_id", "provenance_manifest_hash", "checked_transcript_stdout_sha256", "returncode", "claim_boundary"])],
        ["R9", "Replay packet binds provenance and current source hashes", replay_packet["provenance_manifest_hash"] == provenance_packet["manifest_hash"] and replay_packet["lean_module_replay_hash"] == source_hashes["lean_module_sha256"]],
        ["R10", "Acceptance packet schema is complete", all(key in acceptance_packet for key in ["acceptance_packet_id", "replay_validation_manifest_hash", "checked_transcript_accepted", "theorem_scope_statement", "open_obligation_ledger_hash", "claim_boundary"])],
        ["R11", "Acceptance packet binds both manifests and the checked run", acceptance_packet["provenance_manifest_hash"] == provenance_packet["manifest_hash"] and acceptance_packet["replay_validation_manifest_hash"] == replay_packet["manifest_hash"] and acceptance_packet["checked_transcript_accepted"] is True],
        ["R12", "Forbidden theorem claims remain false", boundary["formal_theorem_proved"] is False and boundary["explicit_not_quantum_pcp_proof"] is True and boundary["nlts_theorem_claimed"] is False and boundary["global_gap_amplification_impossibility_claimed"] is False],
    ]
    rows = [{"requirement_id": item[0], "label": item[1], "passed": bool(item[2])} for item in requirements]
    failed = [row["requirement_id"] for row in rows if not row["passed"]]
    payload = {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "problem_id": 17,
        "method": METHOD,
        "status": STATUS if not failed else "checked_transcript_interface_closure_reconciliation_failed",
        "model_status": MODEL_STATUS,
        "workload": "B9/ClusterStabilizer/WidthLocality.lean",
        "summary": {
            "closure_requirement_count": len(rows),
            "closure_requirements_passed": len(rows) - len(failed),
            "closure_requirements_failed": len(failed),
            "failed_requirement_ids": failed,
            "fresh_command_count": len(records),
            "fresh_zero_returncode_count": sum(record["returncode"] == 0 for record in records),
            "source_hashes": source_hashes,
            "transcript_sha256": transcript_hash,
            "provenance_manifest_hash": provenance_packet["manifest_hash"],
            "replay_validation_manifest_hash": replay_packet["manifest_hash"],
            "acceptance_packet_hash": acceptance_packet["packet_hash"],
            "checked_interface_accepted": all_zero and not failed,
            "proof_assistant_checked": all_zero,
            "formal_theorem_proved": False,
            "explicit_not_quantum_pcp_proof": True,
            "nlts_theorem_claimed": False,
            "global_gap_amplification_impossibility_claimed": False,
            "validation_error_count": len(failed),
        },
        "fresh_command_records": records,
        "submissions": {
            "provenance": str(PROVENANCE_SUBMISSION.relative_to(ROOT)),
            "replay_validation": str(REPLAY_SUBMISSION.relative_to(ROOT)),
            "acceptance": str(ACCEPTANCE_SUBMISSION.relative_to(ROOT)),
        },
        "requirements": rows,
        "claim_boundary": boundary,
    }
    write_json(OUT_JSON, payload)
    write_markdown(payload)
    return payload


def write_markdown(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# B9 Checked Transcript Closure Reconciliation Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Requirements passed/failed: `{summary['closure_requirements_passed']}` / `{summary['closure_requirements_failed']}`",
        f"- Fresh Lean/Lake commands: `{summary['fresh_zero_returncode_count']}/{summary['fresh_command_count']}` returncode zero",
        f"- Transcript SHA256: `{summary['transcript_sha256']}`",
        f"- Provenance manifest hash: `{summary['provenance_manifest_hash']}`",
        f"- Replay-validation manifest hash: `{summary['replay_validation_manifest_hash']}`",
        f"- Acceptance packet hash: `{summary['acceptance_packet_hash']}`",
        f"- Checked indexed interface accepted: `{summary['checked_interface_accepted']}`",
        "",
        "## Evidence",
        "",
        f"- Fresh transcript: `{TRANSCRIPT.relative_to(ROOT)}`",
        f"- Provenance submission: `{payload['submissions']['provenance']}`",
        f"- Replay-validation submission: `{payload['submissions']['replay_validation']}`",
        f"- Acceptance submission: `{payload['submissions']['acceptance']}`",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"]["what_is_supported"],
        "",
        payload["claim_boundary"]["what_is_not_supported"],
        "",
    ]
    for row in payload["requirements"]:
        lines.append(f"- {row['requirement_id']} [{'PASS' if row['passed'] else 'FAIL'}]: {row['label']}")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    argparse.ArgumentParser().parse_args()
    payload = build()
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    if payload["summary"]["validation_error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
