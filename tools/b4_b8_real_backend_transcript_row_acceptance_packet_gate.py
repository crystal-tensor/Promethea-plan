#!/usr/bin/env python3
"""T-B4-002n/T-B8-003r/T-B10-009f: real-backend transcript row acceptance packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b4_b8_real_backend_transcript_row_acceptance_packet_gate_v0"
STATUS = "real_backend_transcript_row_acceptance_packet_open_missing_artifact"
MODEL_STATUS = "transcript_row_acceptance_packet_required_before_soundness_or_b10_credit"
VERSION = "0.1"
EXPECTED_ACCEPTANCE_PACKET_ID = "B4B8-M6-real-backend-transcript-row-acceptance-packet"
EXPECTED_REPLAY_MANIFEST_ID = "B4B8-M6-real-backend-transcript-replay-validation-manifest"
EXPECTED_PROVENANCE_MANIFEST_ID = "B4B8-M6-real-backend-transcript-provenance-manifest"
EXPECTED_PROVIDER_PACKET_ID = "B4B8-M6-provider-session-manifest"
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
    replay = load_json(args.replay_validation_manifest_gate)
    priority = load_json(args.priority_packet_gate)
    replay_summary = replay["summary"]
    priority_summary = priority["summary"]
    submission_path = args.submission_dir / f"{EXPECTED_ACCEPTANCE_PACKET_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None

    required_keys = [
        "acceptance_packet_id",
        "provider_packet_id",
        "provenance_manifest_id",
        "replay_validation_manifest_id",
        "transcript_packet_id",
        "provider_packet_hash",
        "provenance_manifest_hash",
        "replay_validation_manifest_hash",
        "priority_packet_hash",
        "backend_properties_hash",
        "runnable_circuit_manifest_hash",
        "job_metadata_hash",
        "raw_counts_hash",
        "postprocess_script_hash",
        "shot_allocation_ledger_hash",
        "private_predicate_commitment_hash",
        "redaction_manifest_hash",
        "leakage_blind_margin_table_hash",
        "full_leak_margin_table_hash",
        "spoofer_attack_table_hash",
        "accepted_transcript_row_count",
        "leakage_blind_accepts_per_160",
        "full_leak_accepts_per_160",
        "margin_retest_passed",
        "b10_credit_boundary",
        "claim_boundary",
        "source_evidence_files_present",
    ]
    production_required_keys = [
        "replay_validation_manifest_hash",
        "priority_packet_hash",
        "backend_properties_hash",
        "runnable_circuit_manifest_hash",
        "job_metadata_hash",
        "raw_counts_hash",
        "postprocess_script_hash",
        "shot_allocation_ledger_hash",
        "private_predicate_commitment_hash",
        "redaction_manifest_hash",
        "leakage_blind_margin_table_hash",
        "full_leak_margin_table_hash",
        "spoofer_attack_table_hash",
        "accepted_transcript_row_count",
        "leakage_blind_accepts_per_160",
        "full_leak_accepts_per_160",
        "margin_retest_passed",
        "b10_credit_boundary",
        "claim_boundary",
    ]
    evidence_files = [
        "accepted_replay_validation_manifest",
        "priority_transcript_packet",
        "backend_properties_manifest",
        "runnable_circuit_manifest",
        "job_metadata_manifest",
        "raw_counts_artifact",
        "postprocess_replay_script",
        "shot_allocation_ledger",
        "private_predicate_commitment_note",
        "hashing_and_redaction_manifest",
        "leakage_blind_margin_retest_table",
        "full_leak_margin_retest_table",
        "spoofer_attack_replay_table",
        "transcript_row_acceptance_ledger",
        "b10_zero_credit_boundary_note",
        "claim_boundary_note",
    ]

    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    manifest_bound = (
        submitted is not None
        and submitted.get("acceptance_packet_id") == EXPECTED_ACCEPTANCE_PACKET_ID
        and submitted.get("provider_packet_id") == EXPECTED_PROVIDER_PACKET_ID
        and submitted.get("provenance_manifest_id") == EXPECTED_PROVENANCE_MANIFEST_ID
        and submitted.get("replay_validation_manifest_id") == EXPECTED_REPLAY_MANIFEST_ID
        and submitted.get("transcript_packet_id") == EXPECTED_TRANSCRIPT_PACKET_ID
        and submitted.get("provider_packet_hash") == replay_summary.get("provider_packet_hash")
        and submitted.get("provenance_manifest_hash") == replay_summary.get("provenance_manifest_hash")
        and submitted.get("replay_validation_manifest_hash") == replay_summary.get("manifest_hash")
        and submitted.get("priority_packet_hash") == priority_summary.get("packet_hash")
    )
    row_acceptance_valid = (
        submitted is not None
        and submitted.get("accepted_transcript_row_count", -1) > 0
        and submitted.get("leakage_blind_accepts_per_160", 161)
        <= replay_summary.get("no_leak_allowed_accepts_per_160")
        and submitted.get("full_leak_accepts_per_160", 161)
        <= replay_summary.get("full_leak_allowed_accepts_per_160")
        and submitted.get("margin_retest_passed") is True
    )
    b10_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("b10_credit_boundary"), dict)
        and submitted["b10_credit_boundary"].get("soundness_credit_allowed") is False
        and submitted["b10_credit_boundary"].get("bqp_separation_credit_allowed") is False
    )
    claim_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("claim_boundary"), dict)
        and submitted["claim_boundary"].get("protocol_soundness_proved") is False
        and submitted["claim_boundary"].get("cryptographic_soundness_proved") is False
        and submitted["claim_boundary"].get("sampling_hardness_proved") is False
        and submitted["claim_boundary"].get("quantum_advantage_claimed") is False
        and submitted["claim_boundary"].get("bqp_separation_claimed") is False
    )
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True

    acceptance_packet = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "provider_packet_id": EXPECTED_PROVIDER_PACKET_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "replay_validation_manifest_id": EXPECTED_REPLAY_MANIFEST_ID,
        "transcript_packet_id": EXPECTED_TRANSCRIPT_PACKET_ID,
        "source_replay_validation_manifest_gate": str(args.replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "submission_artifact_path": str(submission_path),
        "provider_packet_hash": replay_summary.get("provider_packet_hash"),
        "provenance_manifest_hash": replay_summary.get("provenance_manifest_hash"),
        "replay_validation_manifest_hash": replay_summary.get("manifest_hash"),
        "priority_packet_hash": priority_summary.get("packet_hash"),
        "holdout_row_count": replay_summary.get("holdout_row_count"),
        "no_leak_allowed_accepts_per_160": replay_summary.get("no_leak_allowed_accepts_per_160"),
        "full_leak_allowed_accepts_per_160": replay_summary.get("full_leak_allowed_accepts_per_160"),
        "required_keys": required_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": evidence_files,
        "accepted_only_if": [
            "acceptance_packet_id equals B4B8-M6-real-backend-transcript-row-acceptance-packet",
            "provider, provenance, replay-validation, and transcript packet IDs match source gates",
            "provider, provenance, replay-validation, and priority packet hashes match source gates",
            "backend properties, runnable circuit manifest, job metadata, raw counts, postprocess, shot allocation, predicate commitment, redaction, margins, and spoofer tables are hash-bound",
            "accepted_transcript_row_count is positive only after leakage-blind <=16/160 and full-leak <=40/160 margin retest passes",
            "B10 credit boundary keeps soundness and BQP-separation credit false until an independently accepted transcript route exists",
            "claim_boundary forbids protocol soundness, cryptographic soundness, sampling hardness, quantum advantage, and BQP separation claims",
        ],
    }
    acceptance_packet["packet_hash"] = stable_hash(acceptance_packet)

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
            "Replay-validation manifest gate remains valid and blocked only on P6/P7/P8",
            replay.get("method") == "b4_b8_real_backend_transcript_replay_validation_manifest_gate_v0"
            and replay_summary.get("validation_error_count") == 0
            and replay_summary.get("failed_manifest_requirement_ids") == EXPECTED_FAILED_IDS,
            {
                "source_status": replay.get("status"),
                "failed_manifest_requirement_ids": replay_summary.get("failed_manifest_requirement_ids"),
                "validation_error_count": replay_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Priority transcript packet remains fixed and source-shaped",
            priority.get("method") == "b4_b8_real_backend_transcript_priority_packet_gate_v0"
            and priority_summary.get("priority_packet_id") == EXPECTED_TRANSCRIPT_PACKET_ID
            and priority_summary.get("validation_error_count") == 0
            and priority_summary.get("failed_priority_requirement_ids") == EXPECTED_FAILED_IDS,
            {
                "priority_packet_id": priority_summary.get("priority_packet_id"),
                "packet_hash": priority_summary.get("packet_hash"),
                "failed_priority_requirement_ids": priority_summary.get("failed_priority_requirement_ids"),
            },
        ),
        requirement(
            "P3",
            "Acceptance packet carries locked transcript acceptance schema and evidence classes",
            len(required_keys) == 27
            and len(production_required_keys) == 19
            and len(evidence_files) == 16,
            {
                "required_key_count": len(required_keys),
                "production_required_key_count": len(production_required_keys),
                "required_evidence_file_count": len(evidence_files),
            },
        ),
        requirement(
            "P4",
            "Locked margin budgets and denominator scope are preserved",
            replay_summary.get("holdout_row_count") == 160
            and replay_summary.get("no_leak_allowed_accepts_per_160") == 16
            and replay_summary.get("full_leak_allowed_accepts_per_160") == 40
            and replay_summary.get("real_backend_transcript_rows") == 0,
            {
                "holdout_row_count": replay_summary.get("holdout_row_count"),
                "no_leak_allowed_accepts_per_160": replay_summary.get("no_leak_allowed_accepts_per_160"),
                "full_leak_allowed_accepts_per_160": replay_summary.get("full_leak_allowed_accepts_per_160"),
                "real_backend_transcript_rows": replay_summary.get("real_backend_transcript_rows"),
            },
        ),
        requirement(
            "P5",
            "Current state has no accepted transcript row or B10 credit",
            replay_summary.get("accepted_priority_transcript_rows") == 0
            and all(replay_summary.get(key) is False for key in forbidden_claims),
            {
                "accepted_priority_transcript_rows": replay_summary.get("accepted_priority_transcript_rows"),
                **{key: replay_summary.get(key) for key in forbidden_claims},
            },
        ),
        requirement(
            "P6",
            "Real-backend transcript row acceptance packet has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted acceptance packet satisfies the locked transcript schema",
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
            "Submitted acceptance packet is source-backed, manifest-bound, margin-valid, B10-boundary-bound, and claim-boundary-bound",
            source_backed
            and manifest_bound
            and row_acceptance_valid
            and b10_boundary_bound
            and claim_boundary_bound,
            {
                "source_backed": source_backed,
                "manifest_bound": manifest_bound,
                "row_acceptance_valid": row_acceptance_valid,
                "b10_boundary_bound": b10_boundary_bound,
                "claim_boundary_bound": claim_boundary_bound,
            },
        ),
        requirement(
            "P9",
            "Forbidden soundness, advantage, and BQP claims remain false",
            all(replay_summary.get(key) is False for key in forbidden_claims),
            {key: replay_summary.get(key) for key in forbidden_claims},
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected transcript row acceptance packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted acceptance packet until a hardware PR supplies one")

    summary = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "provider_packet_id": EXPECTED_PROVIDER_PACKET_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "replay_validation_manifest_id": EXPECTED_REPLAY_MANIFEST_ID,
        "transcript_packet_id": EXPECTED_TRANSCRIPT_PACKET_ID,
        "provider_packet_hash": replay_summary.get("provider_packet_hash"),
        "provenance_manifest_hash": replay_summary.get("provenance_manifest_hash"),
        "replay_validation_manifest_hash": replay_summary.get("manifest_hash"),
        "priority_packet_hash": priority_summary.get("packet_hash"),
        "acceptance_packet_hash": acceptance_packet["packet_hash"],
        "acceptance_requirement_count": len(requirements),
        "acceptance_requirements_passed": passed,
        "acceptance_requirements_failed": len(requirements) - passed,
        "failed_acceptance_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(evidence_files),
        "holdout_row_count": replay_summary.get("holdout_row_count"),
        "no_leak_allowed_accepts_per_160": replay_summary.get("no_leak_allowed_accepts_per_160"),
        "full_leak_allowed_accepts_per_160": replay_summary.get("full_leak_allowed_accepts_per_160"),
        "real_backend_transcript_rows": 0,
        "accepted_priority_transcript_rows": 0,
        "submitted_acceptance_packet_exists": submitted_exists,
        "submitted_key_count": len(submitted) if submitted else 0,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "protocol_soundness_proved": False,
        "cryptographic_soundness_proved": False,
        "sampling_hardness_proved": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "b10_soundness_credit_allowed": False,
        "b10_bqp_separation_credit_allowed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark": "B4/B8",
        "benchmark_id": "B4_B8",
        "linked_benchmark_id": "B10",
        "source_target_id": "B10-T2",
        "dependency_benchmarks": ["B4", "B8", "B10"],
        "title": "B4/B8 Real-Backend Transcript Row Acceptance Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_replay_validation_manifest_gate": str(args.replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "summary": summary,
        "real_backend_transcript_row_acceptance_packet": acceptance_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The B4/B8/B10 real-backend transcript route now has a row acceptance packet "
                "that binds replay-validation, priority-packet, backend, job, counts, postprocess, "
                "margin-retest, spoofer-replay, and B10 zero-credit evidence before transcript rows can count."
            ),
            "what_is_not_supported": (
                "No real-backend transcript row acceptance packet or transcript row has been submitted or "
                "accepted; no protocol soundness, cryptographic soundness, sampling hardness, quantum "
                "advantage, or BQP separation claim is supported."
            ),
            "next_gate": (
                "Submit B4B8-M6-real-backend-transcript-row-acceptance-packet with accepted replay "
                "manifest hash, source-backed raw counts and postprocess replay, leakage-blind and "
                "full-leak margin retest tables, spoofer replay, B10 zero-credit boundary, and claim boundary."
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
    packet = payload["real_backend_transcript_row_acceptance_packet"]
    lines = [
        "# B4/B8 Real-Backend Transcript Row Acceptance Packet Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Acceptance packet: `{summary['acceptance_packet_id']}`",
        f"- Transcript packet: `{summary['transcript_packet_id']}`",
        f"- Replay-validation manifest: `{summary['replay_validation_manifest_id']}`",
        f"- Replay-validation manifest hash: `{summary['replay_validation_manifest_hash']}`",
        f"- Priority packet hash: `{summary['priority_packet_hash']}`",
        f"- Acceptance packet hash: `{summary['acceptance_packet_hash']}`",
        f"- Requirements passed/failed: `{summary['acceptance_requirements_passed']}` / `{summary['acceptance_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_acceptance_requirement_ids']}`",
        f"- Required key / production key / evidence file count: `{summary['required_key_count']}` / `{summary['production_required_key_count']}` / `{summary['required_evidence_file_count']}`",
        f"- Holdout row count: `{summary['holdout_row_count']}`",
        f"- No-leak / full-leak accepts per 160: `{summary['no_leak_allowed_accepts_per_160']}` / `{summary['full_leak_allowed_accepts_per_160']}`",
        f"- Real-backend transcript rows: `{summary['real_backend_transcript_rows']}`",
        f"- Accepted priority transcript rows: `{summary['accepted_priority_transcript_rows']}`",
        f"- B10 soundness / BQP credit allowed: `{summary['b10_soundness_credit_allowed']}` / `{summary['b10_bqp_separation_credit_allowed']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Acceptance Packet",
        "",
        f"- Submission path: `{packet['submission_artifact_path']}`",
        f"- Packet hash: `{packet['packet_hash']}`",
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
        state = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- {row['requirement_id']} [{state}]: {row['label']}")
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
        "--replay-validation-manifest-gate",
        type=Path,
        default=Path("results/B4_B8_real_backend_transcript_replay_validation_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B4_B8_real_backend_transcript_priority_packet_gate_v0.json"),
    )
    parser.add_argument("--submission-dir", type=Path, default=Path("research/submissions"))
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B4_B8_real_backend_transcript_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B4_B8_real_backend_transcript_row_acceptance_packet_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-03")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    write_markdown(payload, args.markdown_output)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    if payload["validation_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
