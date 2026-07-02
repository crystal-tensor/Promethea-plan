#!/usr/bin/env python3
"""T-B9-004i/T-B10-016a: priority checked transcript packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b9_checked_transcript_priority_packet_gate_v0"
STATUS = "checked_transcript_priority_packet_open_missing_artifact"
MODEL_STATUS = "priority_checked_transcript_packet_ready_no_checked_run_submitted"
VERSION = "0.1"
EXPECTED_FAILED_IDS = ["P6", "P7", "P8"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    acquisition = load_json(args.acquisition_gate)
    summary = acquisition["summary"]
    submission_path = args.submission_dir / "B9-checked-width-locality-transcript.json"
    transcript_path = Path("results/B9_checked_run_width_locality_transcript_v0.txt")
    lean_module_path = Path("B9/ClusterStabilizer/WidthLocality.lean")
    toolchain_path = Path("lean-toolchain")
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None
    required_keys = [
        "packet_id",
        "lean_toolchain_sha256",
        "lean_version_stdout",
        "lake_version_stdout",
        "checked_transcript_sha256",
        "checked_transcript_path",
        "lean_module_sha256",
        "lake_env_lean_command",
        "returncode",
        "claim_boundary",
    ]
    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    transcript_present = transcript_path.exists()
    source_backed = (
        submitted is not None
        and submitted.get("source_evidence_files_present") is True
        and not missing_keys
        and submitted.get("returncode") == 0
    )

    priority_packet = {
        "packet_id": "B9-checked-width-locality-transcript",
        "blocks_acquisition_requirements": ["A3", "A4", "A6"],
        "submission_artifact_path": str(submission_path),
        "required_keys": required_keys,
        "required_evidence_files": [
            "lean_toolchain_file",
            "lean_version_transcript",
            "lake_version_transcript",
            "lake_env_lean_width_locality_transcript",
            "checked_transcript_file",
            "lean_module_source_hash",
            "offline_bundle_hash_manifest",
            "claim_boundary_note",
        ],
        "accepted_only_if": [
            "lean --version reports Lean 4.12.0 or the declared pinned toolchain equivalent",
            "lake --version exits successfully under the same toolchain",
            "lake env lean B9/ClusterStabilizer/WidthLocality.lean exits with returncode 0",
            "checked transcript hash matches the submitted transcript file",
            "lean module hash matches the current scaffold source",
            "claim_boundary forbids Quantum PCP, NLTS, formal theorem, and global impossibility claims",
        ],
        "expected_local_paths": {
            "lean_toolchain": str(toolchain_path),
            "lean_module": str(lean_module_path),
            "checked_transcript": str(transcript_path),
        },
    }
    priority_packet["packet_hash"] = stable_hash(priority_packet)

    requirements = [
        requirement(
            "P1",
            "Checked-run acquisition gate remains valid and blocked only on A3/A4/A6",
            acquisition.get("method") == "b9_checked_run_acquisition_gate_v0"
            and summary.get("validation_error_count") == 0
            and summary.get("failed_acquisition_requirement_ids") == ["A3", "A4", "A6"],
            {
                "source_status": acquisition.get("status"),
                "failed_acquisition_requirement_ids": summary.get(
                    "failed_acquisition_requirement_ids"
                ),
                "validation_error_count": summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Pinned Lean toolchain and module source are present",
            toolchain_path.exists()
            and lean_module_path.exists()
            and toolchain_path.read_text(encoding="utf-8").strip() == "leanprover/lean4:v4.12.0",
            {
                "lean_toolchain_exists": toolchain_path.exists(),
                "lean_toolchain_sha256": sha256_file(toolchain_path) if toolchain_path.exists() else None,
                "lean_module_exists": lean_module_path.exists(),
                "lean_module_sha256": sha256_file(lean_module_path) if lean_module_path.exists() else None,
            },
        ),
        requirement(
            "P3",
            "Priority packet binds the three acquisition blockers",
            priority_packet["blocks_acquisition_requirements"] == ["A3", "A4", "A6"],
            {"blocks_acquisition_requirements": priority_packet["blocks_acquisition_requirements"]},
        ),
        requirement(
            "P4",
            "Packet carries checked transcript schema and evidence file classes",
            len(required_keys) == 10 and len(priority_packet["required_evidence_files"]) == 8,
            {
                "required_key_count": len(required_keys),
                "required_evidence_file_count": len(priority_packet["required_evidence_files"]),
            },
        ),
        requirement(
            "P5",
            "Current state has no proof-assistant checked theorem",
            summary.get("proof_assistant_checked") is False
            and summary.get("formal_theorem_proved") is False
            and summary.get("explicit_not_quantum_pcp_proof") is True,
            {
                "proof_assistant_checked": summary.get("proof_assistant_checked"),
                "formal_theorem_proved": summary.get("formal_theorem_proved"),
                "explicit_not_quantum_pcp_proof": summary.get("explicit_not_quantum_pcp_proof"),
            },
        ),
        requirement(
            "P6",
            "Priority checked transcript artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted artifact satisfies the locked checked-run schema",
            submitted_exists and not missing_keys,
            {"missing_keys": missing_keys, "submitted_key_count": len(submitted) if submitted else 0},
        ),
        requirement(
            "P8",
            "Submitted transcript is source-backed and returncode-zero",
            source_backed and transcript_present,
            {
                "source_evidence_files_present": submitted.get("source_evidence_files_present")
                if submitted
                else False,
                "returncode": submitted.get("returncode") if submitted else None,
                "checked_transcript_present": transcript_present,
            },
        ),
        requirement(
            "P9",
            "Forbidden Quantum PCP, NLTS, formal theorem, and global impossibility claims remain false",
            acquisition["claim_boundary"].get("proof_assistant_checked") is False
            and acquisition["claim_boundary"].get("formal_theorem_proved") is False
            and acquisition["claim_boundary"].get("explicit_not_quantum_pcp_proof") is True
            and acquisition["claim_boundary"].get("nlts_theorem_claimed") is False,
            {
                "proof_assistant_checked": acquisition["claim_boundary"].get(
                    "proof_assistant_checked"
                ),
                "formal_theorem_proved": acquisition["claim_boundary"].get("formal_theorem_proved"),
                "explicit_not_quantum_pcp_proof": acquisition["claim_boundary"].get(
                    "explicit_not_quantum_pcp_proof"
                ),
                "nlts_theorem_claimed": acquisition["claim_boundary"].get("nlts_theorem_claimed"),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected checked transcript packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted artifact until a proof-agent PR supplies one")

    payload_summary = {
        "priority_packet_id": priority_packet["packet_id"],
        "packet_hash": priority_packet["packet_hash"],
        "priority_requirement_count": len(requirements),
        "priority_requirements_passed": passed,
        "priority_requirements_failed": len(requirements) - passed,
        "failed_priority_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "required_evidence_file_count": len(priority_packet["required_evidence_files"]),
        "blocks_acquisition_requirements": priority_packet["blocks_acquisition_requirements"],
        "lean4_available": summary.get("lean4_available"),
        "lake_available": summary.get("lake_available"),
        "checked_transcript_present": transcript_present,
        "submitted_artifact_exists": submitted_exists,
        "missing_key_count": len(missing_keys),
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
        "title": "B9 Checked Transcript Priority Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_acquisition_gate_result": str(args.acquisition_gate),
        "summary": payload_summary,
        "priority_checked_transcript_packet": priority_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The first B9 proof-assistant blocker now has a concrete source-backed "
                "submission packet for a Lean/Lake checked transcript."
            ),
            "what_is_not_supported": (
                "No checked transcript artifact has been submitted or accepted; no proof-assistant "
                "checked theorem, Quantum PCP proof, NLTS theorem, or global impossibility theorem is supported."
            ),
            "next_gate": (
                f"Submit {submission_path} plus the checked transcript for lean --version, "
                "lake --version, and lake env lean B9/ClusterStabilizer/WidthLocality.lean."
            ),
            "proof_assistant_checked": False,
            "formal_theorem_proved": False,
            "explicit_not_quantum_pcp_proof": True,
            "nlts_theorem_claimed": False,
            "global_gap_amplification_impossibility_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["priority_checked_transcript_packet"]
    lines = [
        "# B9 Checked Transcript Priority Packet Gate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Priority packet: `{summary['priority_packet_id']}`",
        f"- Packet hash: `{summary['packet_hash']}`",
        f"- Requirements passed/failed: {summary['priority_requirements_passed']} / {summary['priority_requirements_failed']}",
        f"- Failed requirement IDs: {summary['failed_priority_requirement_ids']}",
        f"- Required keys: {summary['required_key_count']}",
        f"- Required evidence file classes: {summary['required_evidence_file_count']}",
        f"- Blocks acquisition requirements: {summary['blocks_acquisition_requirements']}",
        f"- Lean 4 / Lake available: {summary['lean4_available']} / {summary['lake_available']}",
        f"- Checked transcript present: {summary['checked_transcript_present']}",
        f"- Submitted artifact exists: {summary['submitted_artifact_exists']}",
        "",
        "## Submission Packet",
        "",
        f"- Submission path: `{packet['submission_artifact_path']}`",
        f"- Expected checked transcript: `{packet['expected_local_paths']['checked_transcript']}`",
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
    for row in payload["requirements"]:
        status = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- {row['requirement_id']} [{status}]: {row['label']}")
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
            "",
            "## Validation",
            "",
            f"- validation_error_count: {summary['validation_error_count']}",
        ]
    )
    if payload["validation_errors"]:
        for error in payload["validation_errors"]:
            lines.append(f"- {error}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--acquisition-gate",
        type=Path,
        default=Path("results/B9_checked_run_acquisition_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B9_checked_transcript_priority_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B9_checked_transcript_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B9_checked_transcript_priority_packet_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-02")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, pretty=args.pretty)
    write_markdown(payload, args.markdown_output)

    print(json.dumps(payload["summary"], indent=2 if args.pretty else None, sort_keys=True))
    if payload["validation_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
