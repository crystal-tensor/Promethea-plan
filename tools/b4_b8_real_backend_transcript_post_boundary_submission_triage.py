#!/usr/bin/env python3
"""T-B4-002p/T-B8-003t/T-B10-009h: post-boundary triage for real-backend transcripts."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b4_b8_real_backend_transcript_post_boundary_submission_triage_v0"
STATUS = "real_backend_transcript_post_boundary_triage_ready_no_credit"
MODEL_STATUS = "b8_zero_credit_soundness_boundary_split_into_pr_sized_transcript_packets"
VERSION = "0.1"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def stable_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def packet(
    packet_id: str,
    title: str,
    owner_role: str,
    status: str,
    blocker: str,
    expected_artifacts: list[str],
    acceptance_evidence: list[str],
) -> dict[str, Any]:
    return {
        "packet_id": packet_id,
        "title": title,
        "owner_role": owner_role,
        "status": status,
        "blocker": blocker,
        "expected_artifacts": expected_artifacts,
        "acceptance_evidence": acceptance_evidence,
    }


def condition(condition_id: str, label: str, satisfied: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "label": label,
        "satisfied": bool(satisfied),
        "evidence": evidence,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    boundary = load_json(args.boundary)
    acceptance = load_json(args.acceptance_packet_gate)
    b10_boundary = load_json(args.b10_boundary)
    boundary_summary = boundary["summary"]
    acceptance_summary = acceptance["summary"]
    b10_summary = b10_boundary["summary"]

    work_packets = [
        packet(
            "H1",
            "Backend provider/session and device-property replay",
            "hardware-intake-agent",
            "ready_for_external_pr_not_credit",
            "no source-backed provider/session/device-property evidence has been accepted",
            [
                "submissions/B4B8-M6-real-backend-transcript-rows/provider_session_manifest.json",
                "submissions/B4B8-M6-real-backend-transcript-rows/backend_properties_bundle/",
                "submissions/B4B8-M6-real-backend-transcript-rows/hardware_claim_boundary.md",
            ],
            [
                "provider/session identifiers and backend properties are source-backed",
                "device snapshot hashes match the transcript provenance chain",
                "claim boundary forbids hardware-result, soundness, advantage, and BQP claims",
            ],
        ),
        packet(
            "H2",
            "Hardware randomized-measurement job/count transcript rows",
            "hardware-execution-agent",
            "ready_for_external_pr_not_credit",
            "real backend transcript rows remain zero",
            [
                "submissions/B4B8-M6-real-backend-transcript-rows/job_metadata_manifest.json",
                "submissions/B4B8-M6-real-backend-transcript-rows/raw_counts_bundle/",
                "submissions/B4B8-M6-real-backend-transcript-rows/shot_allocation_ledger.json",
            ],
            [
                "real_backend_transcript_rows > 0",
                "raw counts and job metadata are hash-bound",
                "shot allocation matches the replay-validation manifest",
            ],
        ),
        packet(
            "H3",
            "Postprocess, private-predicate commitment, and redaction replay",
            "verification-agent",
            "ready_for_external_pr_not_credit",
            "no source-backed postprocess/private-predicate/redaction replay has been accepted",
            [
                "submissions/B4B8-M6-real-backend-transcript-rows/postprocess_replay.json",
                "submissions/B4B8-M6-real-backend-transcript-rows/private_predicate_commitment.json",
                "submissions/B4B8-M6-real-backend-transcript-rows/redaction_hash_replay.json",
            ],
            [
                "accepted transcript rows include replayed postprocess outputs",
                "private predicate commitment remains non-public before reveal",
                "redaction hashes reproduce the submitted transcript packet",
            ],
        ),
        packet(
            "H4",
            "Leakage-separated fit and no-leak/full-leak margin retest",
            "baseline-adversary",
            "ready_for_external_pr_not_credit",
            "real-row leakage-separated margins have not met <=16/160 no-leak and <=40/160 full-leak budgets",
            [
                "submissions/B4B8-M6-real-backend-transcript-rows/leakage_separated_fit.json",
                "submissions/B4B8-M6-real-backend-transcript-rows/no_leak_margin_retest.json",
                "submissions/B4B8-M6-real-backend-transcript-rows/full_leak_margin_retest.json",
            ],
            [
                "leakage-blind no-leak accepted rows stay <=16/160",
                "full-leak accepted rows stay <=40/160 or are explicitly excluded",
                "learned/generative spoofers are replayed against accepted rows",
            ],
        ),
        packet(
            "H5",
            "B8/B4/B10 soundness and advantage credit replay",
            "bqp-boundary-agent",
            "blocked_until_H1_H2_H3_H4_accept",
            "soundness and advantage credit cannot count before real transcript rows and leakage margins are accepted",
            [
                "submissions/B4B8-M6-real-backend-transcript-rows/b8_soundness_replay.json",
                "submissions/B4B8-M6-real-backend-transcript-rows/b4_advantage_boundary.json",
                "submissions/B4B8-M6-real-backend-transcript-rows/b10_t2_credit_boundary.json",
            ],
            [
                "H1-H4 evidence is accepted by the transcript row acceptance packet",
                "B8 protocol/cryptographic/sampling soundness is replayed against real rows",
                "B4 advantage and B10-T2 credit remain false until boundary acceptance",
            ],
        ),
    ]
    ready_packets = [p for p in work_packets if p["status"] == "ready_for_external_pr_not_credit"]
    blocked_packets = [p for p in work_packets if p["status"].startswith("blocked_")]
    triage_packet = {
        "triage_id": "B4-B8-real-backend-transcript-post-boundary-submission-triage",
        "source_boundary": str(args.boundary),
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "source_b10_boundary": str(args.b10_boundary),
        "boundary_hash": boundary_summary.get("boundary_hash"),
        "b10_boundary_hash": b10_summary.get("boundary_hash"),
        "acceptance_packet_hash": boundary_summary.get("source_acceptance_packet_hash"),
        "transcript_packet_id": boundary_summary.get("transcript_packet_id"),
        "holdout_row_count": boundary_summary.get("holdout_row_count"),
        "no_leak_allowed_accepts_per_160": boundary_summary.get("no_leak_allowed_accepts_per_160"),
        "full_leak_allowed_accepts_per_160": boundary_summary.get(
            "full_leak_allowed_accepts_per_160"
        ),
        "real_backend_transcript_rows": boundary_summary.get("real_backend_transcript_rows"),
        "accepted_priority_transcript_rows": boundary_summary.get(
            "accepted_priority_transcript_rows"
        ),
        "b8_protocol_soundness_credit_allowed": False,
        "b4_verifiable_advantage_credit_allowed": False,
        "b10_t2_credit_allowed": False,
        "work_packet_ids": [p["packet_id"] for p in work_packets],
    }
    triage_packet["triage_hash"] = stable_hash(triage_packet)

    forbidden_claims_false = all(
        boundary_summary.get(key) is False
        for key in [
            "protocol_soundness_proved",
            "cryptographic_soundness_proved",
            "sampling_hardness_proved",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
        ]
    )

    conditions = [
        condition(
            "C1",
            "Source B8/B4 real-backend zero-credit boundary is current and valid",
            boundary.get("method") == "b8_b4_real_backend_soundness_boundary_v0"
            and boundary_summary.get("requirements_failed") == 0
            and boundary_summary.get("validation_error_count") == 0,
            {
                "source_method": boundary.get("method"),
                "requirements_failed": boundary_summary.get("requirements_failed"),
                "validation_error_count": boundary_summary.get("validation_error_count"),
            },
        ),
        condition(
            "C2",
            "The transcript row acceptance packet remains blocked on missing submitted evidence",
            acceptance.get("method") == "b4_b8_real_backend_transcript_row_acceptance_packet_gate_v0"
            and acceptance_summary.get("failed_acceptance_requirement_ids") == ["P6", "P7", "P8"]
            and acceptance_summary.get("submitted_acceptance_packet_exists") is False,
            {
                "failed_acceptance_requirement_ids": acceptance_summary.get(
                    "failed_acceptance_requirement_ids"
                ),
                "submitted_acceptance_packet_exists": acceptance_summary.get(
                    "submitted_acceptance_packet_exists"
                ),
            },
        ),
        condition(
            "C3",
            "The holdout and leakage-margin scope is preserved",
            boundary_summary.get("holdout_row_count") == 160
            and boundary_summary.get("no_leak_allowed_accepts_per_160") == 16
            and boundary_summary.get("full_leak_allowed_accepts_per_160") == 40,
            {
                "holdout_row_count": boundary_summary.get("holdout_row_count"),
                "no_leak_allowed_accepts_per_160": boundary_summary.get(
                    "no_leak_allowed_accepts_per_160"
                ),
                "full_leak_allowed_accepts_per_160": boundary_summary.get(
                    "full_leak_allowed_accepts_per_160"
                ),
            },
        ),
        condition(
            "C4",
            "Four real-backend transcript PR packets are ready for external agents",
            [p["packet_id"] for p in ready_packets] == ["H1", "H2", "H3", "H4"],
            {"ready_packet_ids": [p["packet_id"] for p in ready_packets]},
        ),
        condition(
            "C5",
            "Soundness and advantage replay is correctly blocked until H1-H4 evidence exists",
            [p["packet_id"] for p in blocked_packets] == ["H5"]
            and boundary_summary.get("real_backend_transcript_rows") == 0
            and boundary_summary.get("accepted_priority_transcript_rows") == 0,
            {
                "blocked_packet_ids": [p["packet_id"] for p in blocked_packets],
                "real_backend_transcript_rows": boundary_summary.get(
                    "real_backend_transcript_rows"
                ),
                "accepted_priority_transcript_rows": boundary_summary.get(
                    "accepted_priority_transcript_rows"
                ),
            },
        ),
        condition(
            "C6",
            "Forbidden B8/B4/B10 soundness, advantage, and BQP claims remain false",
            forbidden_claims_false
            and boundary_summary.get("b8_protocol_soundness_credit_allowed") is False
            and boundary_summary.get("b4_verifiable_advantage_credit_allowed") is False
            and boundary_summary.get("b10_t2_credit_allowed") is False
            and b10_summary.get("b10_soundness_credit_allowed") is False
            and b10_summary.get("b10_bqp_separation_credit_allowed") is False,
            {
                "protocol_soundness_proved": boundary_summary.get("protocol_soundness_proved"),
                "cryptographic_soundness_proved": boundary_summary.get(
                    "cryptographic_soundness_proved"
                ),
                "sampling_hardness_proved": boundary_summary.get("sampling_hardness_proved"),
                "quantum_advantage_claimed": boundary_summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": boundary_summary.get("bqp_separation_claimed"),
                "b8_protocol_soundness_credit_allowed": boundary_summary.get(
                    "b8_protocol_soundness_credit_allowed"
                ),
                "b4_verifiable_advantage_credit_allowed": boundary_summary.get(
                    "b4_verifiable_advantage_credit_allowed"
                ),
                "b10_t2_credit_allowed": boundary_summary.get("b10_t2_credit_allowed"),
            },
        ),
    ]
    satisfied = sum(row["satisfied"] for row in conditions)
    failed_ids = [row["condition_id"] for row in conditions if not row["satisfied"]]
    validation_errors = []
    if failed_ids:
        validation_errors.append(f"B4/B8 transcript post-boundary triage failed: {failed_ids}")
    if len(work_packets) != 5 or len(ready_packets) != 4 or len(blocked_packets) != 1:
        validation_errors.append("unexpected B4/B8 transcript work-packet shape")

    summary = {
        "triage_id": triage_packet["triage_id"],
        "triage_hash": triage_packet["triage_hash"],
        "source_boundary_hash": boundary_summary.get("boundary_hash"),
        "source_b10_boundary_hash": b10_summary.get("boundary_hash"),
        "source_acceptance_packet_hash": boundary_summary.get("source_acceptance_packet_hash"),
        "transcript_packet_id": boundary_summary.get("transcript_packet_id"),
        "work_packet_count": len(work_packets),
        "ready_external_pr_packet_count": len(ready_packets),
        "blocked_packet_count": len(blocked_packets),
        "ready_packet_ids": [p["packet_id"] for p in ready_packets],
        "blocked_packet_ids": [p["packet_id"] for p in blocked_packets],
        "condition_count": len(conditions),
        "conditions_satisfied": satisfied,
        "conditions_failed": len(conditions) - satisfied,
        "failed_condition_ids": failed_ids,
        "holdout_row_count": boundary_summary.get("holdout_row_count"),
        "no_leak_allowed_accepts_per_160": boundary_summary.get(
            "no_leak_allowed_accepts_per_160"
        ),
        "full_leak_allowed_accepts_per_160": boundary_summary.get(
            "full_leak_allowed_accepts_per_160"
        ),
        "real_backend_transcript_rows": boundary_summary.get("real_backend_transcript_rows"),
        "accepted_priority_transcript_rows": boundary_summary.get(
            "accepted_priority_transcript_rows"
        ),
        "b8_protocol_soundness_credit_allowed": False,
        "b8_cryptographic_soundness_credit_allowed": False,
        "b8_sampling_hardness_credit_allowed": False,
        "b4_verifiable_advantage_credit_allowed": False,
        "b10_t2_credit_allowed": False,
        "b10_soundness_credit_allowed": False,
        "b10_bqp_separation_credit_allowed": False,
        "protocol_soundness_proved": False,
        "cryptographic_soundness_proved": False,
        "sampling_hardness_proved": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B4",
        "linked_benchmark_ids": ["B8", "B10"],
        "source_target_id": "T-B4-002p/T-B8-003t/T-B10-009h",
        "title": "B4/B8 Real-Backend Transcript Post-Boundary Submission Triage",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_boundary": str(args.boundary),
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "source_b10_boundary": str(args.b10_boundary),
        "summary": summary,
        "triage_packet": triage_packet,
        "work_packets": work_packets,
        "conditions": conditions,
        "claim_boundary": {
            "protocol_soundness_proved": False,
            "cryptographic_soundness_proved": False,
            "sampling_hardness_proved": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "b8_protocol_soundness_credit_allowed": False,
            "b4_verifiable_advantage_credit_allowed": False,
            "b10_t2_credit_allowed": False,
            "problem_solved_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Triage hash: `{s['triage_hash']}`",
        f"- Source boundary hash: `{s['source_boundary_hash']}`",
        f"- Source acceptance packet hash: `{s['source_acceptance_packet_hash']}`",
        "",
        "## Result",
        "",
        (
            f"The real-backend transcript post-boundary triage satisfies "
            f"{s['conditions_satisfied']}/{s['condition_count']} conditions and emits "
            f"{s['work_packet_count']} PR-sized work packets."
        ),
        (
            f"Ready external PR packets: {', '.join(s['ready_packet_ids'])}. "
            f"Blocked packet: {', '.join(s['blocked_packet_ids'])}."
        ),
        "",
        "## Work Packets",
        "",
        "| Packet | Status | Blocker |",
        "| --- | --- | --- |",
    ]
    for row in payload["work_packets"]:
        lines.append(f"| {row['packet_id']} | {row['status']} | {row['blocker']} |")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            f"- Transcript packet: `{s['transcript_packet_id']}`",
            f"- Holdout rows: `{s['holdout_row_count']}`",
            f"- No-leak budget: `{s['no_leak_allowed_accepts_per_160']}/160`",
            f"- Full-leak budget: `{s['full_leak_allowed_accepts_per_160']}/160`",
            f"- Real backend transcript rows: `{s['real_backend_transcript_rows']}`",
            f"- Accepted transcript rows: `{s['accepted_priority_transcript_rows']}`",
            f"- B8 protocol soundness credit: `{s['b8_protocol_soundness_credit_allowed']}`",
            f"- B4 advantage credit: `{s['b4_verifiable_advantage_credit_allowed']}`",
            f"- B10-T2 credit: `{s['b10_t2_credit_allowed']}`",
            "",
            "## Claim Boundary",
            "",
            "This is a triage result, not a hardware or soundness result. It does not claim protocol soundness, cryptographic soundness, sampling hardness, quantum advantage, B4 advantage, B10-T2 credit, or BQP separation.",
            "",
            "## Validation",
            "",
            f"- Validation errors: `{s['validation_error_count']}`",
        ]
    )
    for row in payload["conditions"]:
        marker = "PASS" if row["satisfied"] else "FAIL"
        lines.append(f"- `{row['condition_id']}` {marker}: {row['label']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--boundary",
        type=Path,
        default=Path("results/B8_B4_real_backend_soundness_boundary_v0.json"),
    )
    parser.add_argument(
        "--acceptance-packet-gate",
        type=Path,
        default=Path("results/B4_B8_real_backend_transcript_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--b10-boundary",
        type=Path,
        default=Path("results/B10_T2_real_backend_transcript_row_acceptance_boundary_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B4_B8_real_backend_transcript_post_boundary_submission_triage_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B4_B8_real_backend_transcript_post_boundary_submission_triage.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-03")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "triage_hash": payload["summary"]["triage_hash"],
                "conditions_satisfied": payload["summary"]["conditions_satisfied"],
                "conditions_failed": payload["summary"]["conditions_failed"],
                "ready_packet_ids": payload["summary"]["ready_packet_ids"],
                "blocked_packet_ids": payload["summary"]["blocked_packet_ids"],
                "validation_error_count": payload["summary"]["validation_error_count"],
                "json_output": str(args.json_output),
                "markdown_output": str(args.markdown_output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B4/B8 real-backend transcript post-boundary triage validation failed")


if __name__ == "__main__":
    main()
