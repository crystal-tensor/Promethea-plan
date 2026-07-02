#!/usr/bin/env python3
"""T-B9-004j/T-B10-016b: provenance manifest gate for checked Lean/Lake transcript."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b9_checked_transcript_provenance_manifest_gate_v0"
STATUS = "checked_transcript_provenance_manifest_open_missing_artifact"
MODEL_STATUS = "checked_transcript_manifest_required_before_checked_run_acceptance"
VERSION = "0.1"
EXPECTED_PACKET_ID = "B9-checked-width-locality-transcript"
EXPECTED_MANIFEST_ID = "B9-checked-width-locality-transcript-provenance-manifest"
EXPECTED_FAILED_IDS = ["P6", "P7", "P8"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def stable_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    priority = load_json(args.priority_packet_gate)
    summary = priority["summary"]
    packet = priority["priority_checked_transcript_packet"]
    submission_path = args.submission_dir / f"{EXPECTED_MANIFEST_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None

    lean_toolchain = Path("lean-toolchain")
    lakefile = Path("lakefile.lean")
    lean_module = Path("B9/ClusterStabilizer/WidthLocality.lean")
    expected_transcript = Path("results/B9_checked_run_width_locality_transcript_v0.txt")
    required_manifest_keys = [
        "manifest_id",
        "packet_id",
        "priority_packet_hash",
        "lean_toolchain_sha256",
        "lakefile_sha256",
        "lean_module_sha256",
        "lean_version_stdout_sha256",
        "lake_version_stdout_sha256",
        "checked_transcript_sha256",
        "lake_env_lean_command_hash",
        "returncode",
        "offline_bundle_hash_manifest",
        "claim_boundary",
    ]
    production_manifest_keys = [
        "lean_toolchain_sha256",
        "lakefile_sha256",
        "lean_module_sha256",
        "lean_version_stdout_sha256",
        "lake_version_stdout_sha256",
        "checked_transcript_sha256",
        "lake_env_lean_command_hash",
        "returncode",
    ]
    required_evidence_files = [
        "lean_toolchain_file",
        "lakefile_source",
        "lean_module_source",
        "lean_version_stdout_transcript",
        "lake_version_stdout_transcript",
        "lake_env_lean_width_locality_transcript",
        "checked_transcript_file",
        "offline_bundle_hash_manifest",
        "reproduction_environment_note",
        "claim_boundary_note",
    ]

    missing_keys = [key for key in required_manifest_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_manifest_keys if submitted is not None and submitted.get(key) is not None
    ]
    replay_hashes = submitted.get("replay_hashes") if submitted else None
    replay_bound = (
        isinstance(replay_hashes, dict)
        and replay_hashes.get("priority_packet_hash") == summary.get("packet_hash")
        and replay_hashes.get("lean_toolchain_sha256") == sha256_file(lean_toolchain)
        and replay_hashes.get("lean_module_sha256") == sha256_file(lean_module)
    )
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True
    manifest_bound = (
        submitted is not None
        and submitted.get("manifest_id") == EXPECTED_MANIFEST_ID
        and submitted.get("packet_id") == EXPECTED_PACKET_ID
        and submitted.get("priority_packet_hash") == summary.get("packet_hash")
    )

    manifest_packet = {
        "manifest_id": EXPECTED_MANIFEST_ID,
        "packet_id": EXPECTED_PACKET_ID,
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "submission_artifact_path": str(submission_path),
        "priority_packet_hash": summary.get("packet_hash"),
        "blocks_acquisition_requirements": summary.get("blocks_acquisition_requirements"),
        "expected_local_paths": {
            "lean_toolchain": str(lean_toolchain),
            "lakefile": str(lakefile),
            "lean_module": str(lean_module),
            "checked_transcript": str(expected_transcript),
        },
        "source_hashes_at_gate_time": {
            "lean_toolchain_sha256": sha256_file(lean_toolchain),
            "lakefile_sha256": sha256_file(lakefile),
            "lean_module_sha256": sha256_file(lean_module),
        },
        "required_manifest_keys": required_manifest_keys,
        "production_manifest_keys": production_manifest_keys,
        "required_evidence_files": required_evidence_files,
        "accepted_only_if": [
            "manifest_id equals B9-checked-width-locality-transcript-provenance-manifest",
            "packet_id equals B9-checked-width-locality-transcript",
            "priority_packet_hash matches the source priority packet",
            "lean-toolchain, lakefile, and Lean module hashes match the submitted checked run",
            "Lean version, Lake version, and lake env lean transcripts are present and hash-bound",
            "returncode is 0 and checked_transcript_sha256 matches the checked transcript file",
            "source evidence files are present and replay hashes bind priority packet plus local source hashes",
            "claim_boundary forbids Quantum PCP, NLTS, formal theorem, and global impossibility claims",
        ],
    }
    manifest_packet["manifest_hash"] = stable_hash(manifest_packet)

    requirements = [
        requirement(
            "P1",
            "Priority checked transcript packet remains valid and blocked only on P6/P7/P8",
            priority.get("method") == "b9_checked_transcript_priority_packet_gate_v0"
            and summary.get("validation_error_count") == 0
            and summary.get("failed_priority_requirement_ids") == ["P6", "P7", "P8"],
            {
                "source_status": priority.get("status"),
                "failed_priority_requirement_ids": summary.get("failed_priority_requirement_ids"),
                "validation_error_count": summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Pinned Lean project sources remain present",
            lean_toolchain.exists() and lakefile.exists() and lean_module.exists(),
            {
                "lean_toolchain_sha256": sha256_file(lean_toolchain),
                "lakefile_sha256": sha256_file(lakefile),
                "lean_module_sha256": sha256_file(lean_module),
            },
        ),
        requirement(
            "P3",
            "Manifest packet carries locked provenance schema and evidence file classes",
            len(required_manifest_keys) == 13
            and len(production_manifest_keys) == 8
            and len(required_evidence_files) == 10,
            {
                "required_manifest_key_count": len(required_manifest_keys),
                "production_manifest_key_count": len(production_manifest_keys),
                "required_evidence_file_count": len(required_evidence_files),
            },
        ),
        requirement(
            "P4",
            "Manifest remains bound to acquisition blockers A3/A4/A6 and the priority packet hash",
            summary.get("blocks_acquisition_requirements") == ["A3", "A4", "A6"]
            and packet.get("packet_hash") == summary.get("packet_hash"),
            {
                "blocks_acquisition_requirements": summary.get("blocks_acquisition_requirements"),
                "priority_packet_hash": summary.get("packet_hash"),
            },
        ),
        requirement(
            "P5",
            "Current state has no checked transcript or theorem claim",
            summary.get("checked_transcript_present") is False
            and summary.get("proof_assistant_checked") is False
            and summary.get("formal_theorem_proved") is False
            and summary.get("explicit_not_quantum_pcp_proof") is True,
            {
                "checked_transcript_present": summary.get("checked_transcript_present"),
                "proof_assistant_checked": summary.get("proof_assistant_checked"),
                "formal_theorem_proved": summary.get("formal_theorem_proved"),
                "explicit_not_quantum_pcp_proof": summary.get("explicit_not_quantum_pcp_proof"),
            },
        ),
        requirement(
            "P6",
            "Provenance manifest artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted manifest satisfies the locked checked-run provenance schema",
            submitted_exists and not missing_keys and len(production_present) == len(production_manifest_keys),
            {
                "missing_keys": missing_keys,
                "production_keys_present": production_present,
                "production_manifest_keys": production_manifest_keys,
                "submitted_key_count": len(submitted) if submitted else 0,
            },
        ),
        requirement(
            "P8",
            "Submitted manifest is source-backed, packet-bound, replay-hash-bound, and returncode-zero",
            source_backed and manifest_bound and replay_bound and submitted is not None and submitted.get("returncode") == 0,
            {
                "source_evidence_files_present": source_backed,
                "manifest_bound": manifest_bound,
                "replay_bound": replay_bound,
                "returncode": submitted.get("returncode") if submitted else None,
            },
        ),
        requirement(
            "P9",
            "Forbidden Quantum PCP, NLTS, formal theorem, and global impossibility claims remain false",
            summary.get("proof_assistant_checked") is False
            and summary.get("formal_theorem_proved") is False
            and summary.get("explicit_not_quantum_pcp_proof") is True
            and summary.get("nlts_theorem_claimed") is False
            and summary.get("global_gap_amplification_impossibility_claimed") is False,
            {
                "proof_assistant_checked": summary.get("proof_assistant_checked"),
                "formal_theorem_proved": summary.get("formal_theorem_proved"),
                "explicit_not_quantum_pcp_proof": summary.get("explicit_not_quantum_pcp_proof"),
                "nlts_theorem_claimed": summary.get("nlts_theorem_claimed"),
                "global_gap_amplification_impossibility_claimed": summary.get(
                    "global_gap_amplification_impossibility_claimed"
                ),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected checked transcript provenance manifest failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted provenance manifest until a proof-agent PR supplies one")

    payload_summary = {
        "manifest_id": EXPECTED_MANIFEST_ID,
        "priority_packet_id": EXPECTED_PACKET_ID,
        "priority_packet_hash": summary.get("packet_hash"),
        "manifest_hash": manifest_packet["manifest_hash"],
        "manifest_requirement_count": len(requirements),
        "manifest_requirements_passed": passed,
        "manifest_requirements_failed": len(requirements) - passed,
        "failed_manifest_requirement_ids": failed_ids,
        "required_manifest_key_count": len(required_manifest_keys),
        "production_manifest_key_count": len(production_manifest_keys),
        "required_evidence_file_count": len(required_evidence_files),
        "blocks_acquisition_requirements": summary.get("blocks_acquisition_requirements"),
        "lean_toolchain_sha256": sha256_file(lean_toolchain),
        "lakefile_sha256": sha256_file(lakefile),
        "lean_module_sha256": sha256_file(lean_module),
        "submitted_manifest_exists": submitted_exists,
        "submitted_key_count": len(submitted) if submitted else 0,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "checked_transcript_present": False,
        "proof_assistant_checked": False,
        "formal_theorem_proved": False,
        "explicit_not_quantum_pcp_proof": True,
        "nlts_theorem_claimed": False,
        "global_gap_amplification_impossibility_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B9",
        "linked_benchmark_id": "B10",
        "problem_id": 17,
        "title": "B9 Checked Transcript Provenance Manifest Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "summary": payload_summary,
        "provenance_manifest_packet": manifest_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The first B9 checked-transcript route now has a provenance manifest "
                "packet that must bind Lean/Lake source hashes, version transcripts, "
                "checked-run transcript hash, returncode, replay hashes, and claim boundary."
            ),
            "what_is_not_supported": (
                "No provenance manifest or checked transcript has been submitted or accepted; "
                "no proof-assistant checked theorem, Quantum PCP proof, NLTS theorem, or "
                "global impossibility theorem is supported."
            ),
            "next_gate": (
                f"Submit {submission_path} before the checked transcript priority artifact, "
                "then rerun this gate and the priority packet gate."
            ),
            "proof_assistant_checked": False,
            "formal_theorem_proved": False,
            "explicit_not_quantum_pcp_proof": True,
            "nlts_theorem_claimed": False,
            "global_gap_amplification_impossibility_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["provenance_manifest_packet"]
    lines = [
        "# B9 Checked Transcript Provenance Manifest Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Manifest: `{summary['manifest_id']}`",
        f"- Priority packet: `{summary['priority_packet_id']}`",
        f"- Manifest hash: `{summary['manifest_hash']}`",
        f"- Requirements passed/failed: `{summary['manifest_requirements_passed']}` / `{summary['manifest_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_manifest_requirement_ids']}`",
        f"- Required manifest keys / production manifest keys / evidence files: `{summary['required_manifest_key_count']}` / `{summary['production_manifest_key_count']}` / `{summary['required_evidence_file_count']}`",
        f"- Blocks acquisition requirements: `{summary['blocks_acquisition_requirements']}`",
        f"- Submitted manifest exists: `{summary['submitted_manifest_exists']}`",
        f"- Checked transcript present: `{summary['checked_transcript_present']}`",
        f"- Proof assistant checked: `{summary['proof_assistant_checked']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Provenance Manifest Packet",
        "",
        f"- Submission path: `{packet['submission_artifact_path']}`",
        f"- Priority packet hash: `{packet['priority_packet_hash']}`",
        f"- Lean module hash at gate time: `{summary['lean_module_sha256']}`",
        "",
        "Required evidence files:",
        "",
    ]
    for item in packet["required_evidence_files"]:
        lines.append(f"- {item}")
    lines.extend(["", "Acceptance predicates:", ""])
    for item in packet["accepted_only_if"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Requirement Results", ""])
    for item in payload["requirements"]:
        state = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {item['requirement_id']} [{state}]: {item['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            f"- proof_assistant_checked: {payload['claim_boundary']['proof_assistant_checked']}",
            f"- formal_theorem_proved: {payload['claim_boundary']['formal_theorem_proved']}",
            f"- explicit_not_quantum_pcp_proof: {payload['claim_boundary']['explicit_not_quantum_pcp_proof']}",
            f"- nlts_theorem_claimed: {payload['claim_boundary']['nlts_theorem_claimed']}",
            f"- global_gap_amplification_impossibility_claimed: {payload['claim_boundary']['global_gap_amplification_impossibility_claimed']}",
            "",
            "## Validation",
            "",
            f"- validation_error_count: {summary['validation_error_count']}",
        ]
    )
    if payload["validation_errors"]:
        lines.extend(f"- {error}" for error in payload["validation_errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B9_checked_transcript_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B9_checked_transcript_provenance_manifest_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B9_checked_transcript_provenance_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B9_checked_transcript_provenance_manifest_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-02")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    write_markdown(payload, args.markdown_output)
    print(json.dumps(payload["summary"], indent=2 if args.pretty else None, sort_keys=True))
    if payload["validation_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
