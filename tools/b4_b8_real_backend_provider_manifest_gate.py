#!/usr/bin/env python3
"""T-B4-002k/T-B8-003o/T-B10-009c: real-backend provider manifest gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b4_b8_real_backend_provider_manifest_gate_v0"
STATUS = "real_backend_provider_manifest_open_missing_artifact"
MODEL_STATUS = "provider_session_manifest_ready_before_real_backend_transcript"
VERSION = "0.1"
EXPECTED_PACKET_ID = "B4B8-M6-provider-session-manifest"
EXPECTED_TRANSCRIPT_PACKET_ID = "B4B8-M6-real-backend-transcript-rows"
EXPECTED_FAILED_IDS = ["P6", "P7", "P8"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


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
    transcript_gate = load_json(args.transcript_priority_gate)
    summary = transcript_gate["summary"]
    submission_path = args.submission_dir / f"{EXPECTED_PACKET_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None
    required_keys = [
        "packet_id",
        "provider_name",
        "backend_name",
        "access_mode",
        "session_or_queue_id_hash",
        "calibration_window_utc",
        "backend_properties_hash",
        "runnable_circuit_manifest_hash",
        "shot_budget",
        "claim_boundary",
    ]
    production_required_keys = [
        "provider_name",
        "backend_name",
        "access_mode",
        "calibration_window_utc",
        "backend_properties_hash",
        "runnable_circuit_manifest_hash",
        "shot_budget",
    ]
    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True
    transcript_bound = (
        submitted is not None
        and submitted.get("downstream_transcript_packet_id") == EXPECTED_TRANSCRIPT_PACKET_ID
    )
    budget_sufficient = (
        submitted is not None
        and isinstance(submitted.get("shot_budget"), int)
        and submitted.get("shot_budget", 0) >= summary.get("holdout_row_count", 160)
    )

    provider_packet = {
        "packet_id": EXPECTED_PACKET_ID,
        "blocks_transcript_packet": EXPECTED_TRANSCRIPT_PACKET_ID,
        "submission_artifact_path": str(submission_path),
        "source_transcript_priority_gate": str(args.transcript_priority_gate),
        "required_keys": required_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": [
            "provider_access_manifest",
            "backend_properties_snapshot",
            "calibration_window_source",
            "runnable_circuit_manifest",
            "shot_budget_or_job_plan",
            "private_predicate_handling_plan",
            "hashing_and_redaction_manifest",
            "claim_boundary_note",
        ],
        "accepted_only_if": [
            "packet_id equals B4B8-M6-provider-session-manifest",
            "downstream_transcript_packet_id equals B4B8-M6-real-backend-transcript-rows",
            "provider, backend, access mode, calibration window, backend properties hash, runnable circuit manifest, and shot budget are present",
            "shot_budget covers at least the locked 160-row denominator or declares a reviewed replacement denominator",
            "source evidence files are present and hash-bound",
            "claim_boundary forbids protocol soundness, quantum advantage, sampling hardness, cryptographic soundness, and BQP separation claims",
        ],
        "margin_retest_budgets": {
            "holdout_row_count": summary.get("holdout_row_count"),
            "leakage_blind_no_leak_allowed_accepts_per_160": summary.get(
                "no_leak_allowed_accepts_per_160"
            ),
            "full_private_material_leak_allowed_accepts_per_160": summary.get(
                "full_leak_allowed_accepts_per_160"
            ),
        },
    }
    provider_packet["packet_hash"] = stable_hash(provider_packet)

    forbidden_claims = [
        "protocol_soundness_proved",
        "cryptographic_soundness_proved",
        "sampling_hardness_proved",
        "quantum_advantage_claimed",
        "bqp_separation_claimed",
    ]
    requirements = [
        requirement(
            "P1",
            "Transcript priority gate remains valid and blocked only on P6/P7/P8",
            transcript_gate.get("method") == "b4_b8_real_backend_transcript_priority_packet_gate_v0"
            and summary.get("validation_error_count") == 0
            and summary.get("failed_priority_requirement_ids") == ["P6", "P7", "P8"],
            {
                "source_status": transcript_gate.get("status"),
                "failed_priority_requirement_ids": summary.get("failed_priority_requirement_ids"),
                "validation_error_count": summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Provider manifest is bound to the M6 real-backend transcript packet",
            transcript_gate["priority_transcript_packet"].get("packet_id")
            == EXPECTED_TRANSCRIPT_PACKET_ID
            and summary.get("real_backend_transcript_rows") == 0,
            {
                "downstream_transcript_packet_id": transcript_gate["priority_transcript_packet"].get(
                    "packet_id"
                ),
                "real_backend_transcript_rows": summary.get("real_backend_transcript_rows"),
            },
        ),
        requirement(
            "P3",
            "Provider packet carries locked schema and evidence file classes",
            len(required_keys) == 10
            and len(production_required_keys) == 7
            and len(provider_packet["required_evidence_files"]) == 8,
            {
                "required_key_count": len(required_keys),
                "production_required_key_count": len(production_required_keys),
                "required_evidence_file_count": len(provider_packet["required_evidence_files"]),
            },
        ),
        requirement(
            "P4",
            "Locked margin budgets are preserved before hardware execution",
            summary.get("holdout_row_count") == 160
            and summary.get("no_leak_allowed_accepts_per_160") == 16
            and summary.get("full_leak_allowed_accepts_per_160") == 40,
            {
                "holdout_row_count": summary.get("holdout_row_count"),
                "no_leak_allowed_accepts_per_160": summary.get(
                    "no_leak_allowed_accepts_per_160"
                ),
                "full_leak_allowed_accepts_per_160": summary.get(
                    "full_leak_allowed_accepts_per_160"
                ),
            },
        ),
        requirement(
            "P5",
            "Current state has no accepted hardware transcript or soundness claim",
            summary.get("accepted_priority_transcript_rows") == 0
            and summary.get("protocol_soundness_proved") is False
            and summary.get("quantum_advantage_claimed") is False
            and summary.get("bqp_separation_claimed") is False,
            {
                "accepted_priority_transcript_rows": summary.get(
                    "accepted_priority_transcript_rows"
                ),
                "protocol_soundness_proved": summary.get("protocol_soundness_proved"),
                "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": summary.get("bqp_separation_claimed"),
            },
        ),
        requirement(
            "P6",
            "Provider/session manifest artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted manifest satisfies the locked provider schema",
            submitted_exists and not missing_keys and len(production_present) == len(production_required_keys),
            {
                "missing_keys": missing_keys,
                "production_keys_present": production_present,
                "production_required_keys": production_required_keys,
                "submitted_key_count": len(submitted) if submitted else 0,
            },
        ),
        requirement(
            "P8",
            "Submitted manifest is source-backed, transcript-bound, and budget-sufficient",
            source_backed and transcript_bound and budget_sufficient,
            {
                "source_evidence_files_present": source_backed,
                "transcript_bound": transcript_bound,
                "budget_sufficient": budget_sufficient,
                "shot_budget": submitted.get("shot_budget") if submitted else None,
            },
        ),
        requirement(
            "P9",
            "Forbidden soundness, advantage, and BQP claims remain false",
            all(summary.get(key) is False for key in forbidden_claims),
            {key: summary.get(key) for key in forbidden_claims},
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected provider manifest failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted manifest until a hardware intake PR supplies one")

    payload_summary = {
        "priority_packet_id": EXPECTED_PACKET_ID,
        "downstream_transcript_packet_id": EXPECTED_TRANSCRIPT_PACKET_ID,
        "packet_hash": provider_packet["packet_hash"],
        "priority_requirement_count": len(requirements),
        "priority_requirements_passed": passed,
        "priority_requirements_failed": len(requirements) - passed,
        "failed_priority_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(provider_packet["required_evidence_files"]),
        "holdout_row_count": summary.get("holdout_row_count"),
        "no_leak_allowed_accepts_per_160": summary.get("no_leak_allowed_accepts_per_160"),
        "full_leak_allowed_accepts_per_160": summary.get("full_leak_allowed_accepts_per_160"),
        "real_backend_transcript_rows": summary.get("real_backend_transcript_rows"),
        "accepted_priority_transcript_rows": summary.get("accepted_priority_transcript_rows"),
        "submitted_manifest_exists": submitted_exists,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "provider_manifest_accepted": False,
        "protocol_soundness_proved": False,
        "cryptographic_soundness_proved": False,
        "sampling_hardness_proved": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark": "B4/B8",
        "benchmark_id": "B4_B8",
        "linked_benchmark_id": "B10",
        "source_target_id": "B10-T2",
        "dependency_benchmarks": ["B4", "B8", "B10"],
        "title": "B4/B8 Real-Backend Provider Manifest Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_transcript_priority_gate": str(args.transcript_priority_gate),
        "summary": payload_summary,
        "provider_manifest_packet": provider_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The first B4/B8 hardware execution step now has a concrete provider/session "
                "manifest packet before any real-backend transcript can be accepted."
            ),
            "what_is_not_supported": (
                "No provider/session manifest or real-backend transcript row has been "
                "submitted or accepted; no protocol soundness, quantum advantage, sampling "
                "hardness, cryptographic soundness, or BQP separation claim is supported."
            ),
            "next_gate": (
                "Submit B4B8-M6-provider-session-manifest with provider/backend, access mode, "
                "calibration window, backend properties hash, runnable circuit manifest, shot "
                "budget, and claim boundary."
            ),
            "protocol_soundness_proved": False,
            "cryptographic_soundness_proved": False,
            "sampling_hardness_proved": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["provider_manifest_packet"]
    lines = [
        "# B4/B8 Real-Backend Provider Manifest Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Priority packet: `{summary['priority_packet_id']}`",
        f"- Downstream transcript packet: `{summary['downstream_transcript_packet_id']}`",
        f"- Packet hash: `{summary['packet_hash']}`",
        f"- Requirements passed/failed: `{summary['priority_requirements_passed']}` / `{summary['priority_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_priority_requirement_ids']}`",
        f"- Required key / production key / evidence file count: `{summary['required_key_count']}` / `{summary['production_required_key_count']}` / `{summary['required_evidence_file_count']}`",
        f"- Holdout row count: `{summary['holdout_row_count']}`",
        f"- No-leak / full-leak accepts per 160: `{summary['no_leak_allowed_accepts_per_160']}` / `{summary['full_leak_allowed_accepts_per_160']}`",
        f"- Real-backend transcript rows: `{summary['real_backend_transcript_rows']}`",
        f"- Provider manifest accepted: `{summary['provider_manifest_accepted']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Submission Packet",
        "",
        f"- Submission path: `{packet['submission_artifact_path']}`",
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
            f"- protocol_soundness_proved: {payload['claim_boundary']['protocol_soundness_proved']}",
            f"- cryptographic_soundness_proved: {payload['claim_boundary']['cryptographic_soundness_proved']}",
            f"- sampling_hardness_proved: {payload['claim_boundary']['sampling_hardness_proved']}",
            f"- quantum_advantage_claimed: {payload['claim_boundary']['quantum_advantage_claimed']}",
            f"- bqp_separation_claimed: {payload['claim_boundary']['bqp_separation_claimed']}",
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
        "--transcript-priority-gate",
        type=Path,
        default=Path("results/B4_B8_real_backend_transcript_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B4_B8_real_backend_provider_manifest_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B4_B8_real_backend_provider_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B4_B8_real_backend_provider_manifest_gate.md"),
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
