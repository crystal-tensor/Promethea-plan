#!/usr/bin/env python3
"""T-B4-002r/T-B8-003v/T-B10-009j: H1 provider/session access closure gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b4_b8_b10_h1_provider_session_access_closure_gate_v0"
STATUS = "h1_provider_session_access_closure_open_zero_credit"
MODEL_STATUS = "h1_access_blocker_closed_as_auditable_zero_credit_gate"
VERSION = "0.1"
EXPECTED_H1_METHOD = "b4_b8_h1_provider_session_replay_packet_gate_v0"
EXPECTED_B10_BOUNDARY_METHOD = "b10_t2_real_backend_transcript_row_acceptance_boundary_v0"
EXPECTED_H1_PACKET_ID = "B4B8-H1-provider-session-device-property-replay"
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
    h1_gate = load_json(args.h1_packet_gate)
    b10_boundary = load_json(args.b10_boundary)
    h1_summary = h1_gate["summary"]
    b10_summary = b10_boundary["summary"]
    h1_packet = h1_gate["h1_replay_packet"]

    blocker_chain = [
        {
            "blocker_id": "H1",
            "status": "open_missing_source_backed_provider_session_access",
            "required_before_unlock": [
                "provider_access_manifest",
                "session_or_queue_receipt_hash",
                "backend_properties_snapshot",
                "device_properties_snapshot",
                "calibration_window_source",
                "runnable_circuit_manifest",
                "shot_budget_or_job_plan",
                "private_predicate_handling_plan",
                "hashing_and_redaction_manifest",
                "hardware_execution_exclusion_note",
                "claim_boundary_note",
            ],
        },
        {
            "blocker_id": "H2",
            "status": "blocked_until_H1_accepted",
            "required_before_unlock": [
                "hardware_randomized_measurement_job_metadata",
                "raw_counts_bundle",
                "shot_allocation_ledger",
            ],
        },
        {
            "blocker_id": "H3",
            "status": "blocked_until_H1_H2_accepted",
            "required_before_unlock": [
                "postprocess_replay",
                "private_predicate_commitment",
                "redaction_hash_replay",
            ],
        },
        {
            "blocker_id": "H4",
            "status": "blocked_until_H1_H2_H3_accepted",
            "required_before_unlock": [
                "leakage_separated_fit",
                "no_leak_margin_retest",
                "full_leak_margin_retest_or_exclusion",
                "learned_or_generative_spoofer_replay",
            ],
        },
        {
            "blocker_id": "H5",
            "status": "blocked_until_H1_H2_H3_H4_accepted",
            "required_before_unlock": [
                "B8 soundness replay",
                "B4 advantage boundary",
                "B10-T2 credit boundary",
            ],
        },
    ]

    closure_packet = {
        "closure_id": "B4B8B10-H1-provider-session-access-closure",
        "source_h1_packet_gate": str(args.h1_packet_gate),
        "source_b10_boundary": str(args.b10_boundary),
        "h1_packet_id": h1_summary.get("h1_packet_id"),
        "h1_packet_hash": h1_summary.get("h1_packet_hash"),
        "b10_boundary_hash": b10_summary.get("boundary_hash"),
        "downstream_transcript_packet_id": h1_summary.get("downstream_transcript_packet_id"),
        "h1_submission_path": h1_packet.get("submission_artifact_path"),
        "holdout_row_count": h1_summary.get("holdout_row_count"),
        "no_leak_allowed_accepts_per_160": h1_summary.get("no_leak_allowed_accepts_per_160"),
        "full_leak_allowed_accepts_per_160": h1_summary.get("full_leak_allowed_accepts_per_160"),
        "real_backend_transcript_rows": h1_summary.get("real_backend_transcript_rows"),
        "accepted_priority_transcript_rows": h1_summary.get("accepted_priority_transcript_rows"),
        "blocker_chain": blocker_chain,
        "credit_policy": {
            "h2_hardware_rows_may_start": False,
            "b8_protocol_soundness_credit_allowed": False,
            "b4_verifiable_advantage_credit_allowed": False,
            "b10_t2_credit_allowed": False,
            "b10_bqp_separation_credit_allowed": False,
        },
    }
    closure_packet["closure_hash"] = stable_hash(closure_packet)

    requirements = [
        requirement(
            "A1",
            "Source H1 replay packet gate is current and validation-clean",
            h1_gate.get("method") == EXPECTED_H1_METHOD
            and h1_summary.get("h1_packet_id") == EXPECTED_H1_PACKET_ID
            and h1_summary.get("validation_error_count") == 0,
            {
                "source_method": h1_gate.get("method"),
                "h1_packet_id": h1_summary.get("h1_packet_id"),
                "validation_error_count": h1_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "A2",
            "H1 is still open only on missing submitted source-backed artifact requirements",
            h1_summary.get("failed_requirement_ids") == EXPECTED_FAILED_IDS
            and h1_summary.get("submitted_h1_artifact_exists") is False
            and h1_summary.get("missing_key_count", 0) > 0,
            {
                "failed_requirement_ids": h1_summary.get("failed_requirement_ids"),
                "submitted_h1_artifact_exists": h1_summary.get("submitted_h1_artifact_exists"),
                "missing_key_count": h1_summary.get("missing_key_count"),
            },
        ),
        requirement(
            "A3",
            "H1 access artifact cannot unlock H2 because provider/session evidence is absent",
            h1_summary.get("production_keys_present_count") == 0
            and h1_summary.get("required_evidence_file_count") == 11
            and h1_summary.get("h1_provider_session_replay_accepted") is False,
            {
                "production_keys_present_count": h1_summary.get("production_keys_present_count"),
                "required_evidence_file_count": h1_summary.get("required_evidence_file_count"),
                "h1_provider_session_replay_accepted": h1_summary.get(
                    "h1_provider_session_replay_accepted"
                ),
            },
        ),
        requirement(
            "A4",
            "B10-T2 zero-credit boundary is synchronized to the same downstream transcript route",
            b10_boundary.get("method") == EXPECTED_B10_BOUNDARY_METHOD
            and b10_summary.get("transcript_packet_id") == EXPECTED_TRANSCRIPT_PACKET_ID
            and b10_summary.get("requirements_failed") == 0
            and b10_summary.get("validation_error_count") == 0,
            {
                "source_method": b10_boundary.get("method"),
                "transcript_packet_id": b10_summary.get("transcript_packet_id"),
                "requirements_failed": b10_summary.get("requirements_failed"),
                "validation_error_count": b10_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "A5",
            "No real-backend transcript rows or accepted rows exist in either source",
            h1_summary.get("real_backend_transcript_rows") == 0
            and h1_summary.get("accepted_priority_transcript_rows") == 0
            and b10_summary.get("real_backend_transcript_rows") == 0
            and b10_summary.get("accepted_priority_transcript_rows") == 0,
            {
                "h1_real_backend_transcript_rows": h1_summary.get("real_backend_transcript_rows"),
                "h1_accepted_priority_transcript_rows": h1_summary.get(
                    "accepted_priority_transcript_rows"
                ),
                "b10_real_backend_transcript_rows": b10_summary.get(
                    "real_backend_transcript_rows"
                ),
                "b10_accepted_priority_transcript_rows": b10_summary.get(
                    "accepted_priority_transcript_rows"
                ),
            },
        ),
        requirement(
            "A6",
            "Locked H1/B10 denominator and leakage budgets match",
            h1_summary.get("holdout_row_count") == b10_summary.get("holdout_row_count") == 160
            and h1_summary.get("no_leak_allowed_accepts_per_160")
            == b10_summary.get("no_leak_allowed_accepts_per_160")
            == 16
            and h1_summary.get("full_leak_allowed_accepts_per_160")
            == b10_summary.get("full_leak_allowed_accepts_per_160")
            == 40,
            {
                "h1_holdout_row_count": h1_summary.get("holdout_row_count"),
                "b10_holdout_row_count": b10_summary.get("holdout_row_count"),
                "h1_no_leak_allowed_accepts_per_160": h1_summary.get(
                    "no_leak_allowed_accepts_per_160"
                ),
                "b10_no_leak_allowed_accepts_per_160": b10_summary.get(
                    "no_leak_allowed_accepts_per_160"
                ),
                "h1_full_leak_allowed_accepts_per_160": h1_summary.get(
                    "full_leak_allowed_accepts_per_160"
                ),
                "b10_full_leak_allowed_accepts_per_160": b10_summary.get(
                    "full_leak_allowed_accepts_per_160"
                ),
            },
        ),
        requirement(
            "A7",
            "All B4/B8/B10 soundness, advantage, and BQP credits remain disabled",
            h1_summary.get("b8_protocol_soundness_credit_allowed") is False
            and h1_summary.get("b4_verifiable_advantage_credit_allowed") is False
            and h1_summary.get("b10_t2_credit_allowed") is False
            and h1_summary.get("b10_bqp_separation_credit_allowed") is False
            and b10_summary.get("b10_soundness_credit_allowed") is False
            and b10_summary.get("b10_bqp_separation_credit_allowed") is False,
            {
                "b8_protocol_soundness_credit_allowed": h1_summary.get(
                    "b8_protocol_soundness_credit_allowed"
                ),
                "b4_verifiable_advantage_credit_allowed": h1_summary.get(
                    "b4_verifiable_advantage_credit_allowed"
                ),
                "b10_t2_credit_allowed": h1_summary.get("b10_t2_credit_allowed"),
                "b10_bqp_separation_credit_allowed": h1_summary.get(
                    "b10_bqp_separation_credit_allowed"
                ),
                "b10_soundness_credit_allowed": b10_summary.get("b10_soundness_credit_allowed"),
            },
        ),
        requirement(
            "A8",
            "Closure packet keeps H1 before H2/H3/H4/H5 in the execution order",
            [row["blocker_id"] for row in blocker_chain] == ["H1", "H2", "H3", "H4", "H5"]
            and closure_packet["credit_policy"]["h2_hardware_rows_may_start"] is False,
            {
                "blocker_order": [row["blocker_id"] for row in blocker_chain],
                "h2_hardware_rows_may_start": closure_packet["credit_policy"][
                    "h2_hardware_rows_may_start"
                ],
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids:
        validation_errors.append(f"H1 provider/session access closure failed: {failed_ids}")

    summary = {
        "closure_id": closure_packet["closure_id"],
        "closure_hash": closure_packet["closure_hash"],
        "h1_packet_id": h1_summary.get("h1_packet_id"),
        "h1_packet_hash": h1_summary.get("h1_packet_hash"),
        "b10_boundary_hash": b10_summary.get("boundary_hash"),
        "downstream_transcript_packet_id": h1_summary.get("downstream_transcript_packet_id"),
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "h1_source_failed_requirement_ids": h1_summary.get("failed_requirement_ids"),
        "h1_submitted_artifact_exists": h1_summary.get("submitted_h1_artifact_exists"),
        "h1_missing_key_count": h1_summary.get("missing_key_count"),
        "h1_required_evidence_file_count": h1_summary.get("required_evidence_file_count"),
        "holdout_row_count": h1_summary.get("holdout_row_count"),
        "no_leak_allowed_accepts_per_160": h1_summary.get("no_leak_allowed_accepts_per_160"),
        "full_leak_allowed_accepts_per_160": h1_summary.get(
            "full_leak_allowed_accepts_per_160"
        ),
        "real_backend_transcript_rows": h1_summary.get("real_backend_transcript_rows"),
        "accepted_priority_transcript_rows": h1_summary.get(
            "accepted_priority_transcript_rows"
        ),
        "h2_hardware_rows_may_start": False,
        "b8_protocol_soundness_credit_allowed": False,
        "b4_verifiable_advantage_credit_allowed": False,
        "b10_t2_credit_allowed": False,
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
        "source_target_id": "T-B4-002r/T-B8-003v/T-B10-009j",
        "title": "B4/B8/B10 H1 Provider Session Access Closure Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_h1_packet_gate": str(args.h1_packet_gate),
        "source_b10_boundary": str(args.b10_boundary),
        "summary": summary,
        "closure_packet": closure_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The B4/B8/B10 route now has a single auditable H1 access-closure "
                "gate proving that provider/session evidence is the immediate blocker."
            ),
            "what_is_not_supported": (
                "No H1 artifact, hardware execution, accepted real-backend transcript row, "
                "protocol soundness, quantum advantage, or BQP separation is supported."
            ),
            "next_gate": (
                "Submit B4B8-H1-provider-session-device-property-replay with source-backed "
                "provider access, session or queue receipt hash, backend/device snapshots, "
                "calibration-window source, runnable circuit manifest, shot budget, "
                "private-predicate handling, redaction policy, hardware-execution exclusion "
                "note, and claim boundary before H2 hardware transcript rows start."
            ),
            "h2_hardware_rows_may_start": False,
            "protocol_soundness_proved": False,
            "cryptographic_soundness_proved": False,
            "sampling_hardness_proved": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    packet = payload["closure_packet"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Closure hash: `{s['closure_hash']}`",
        f"- H1 packet: `{s['h1_packet_id']}`",
        f"- H1 packet hash: `{s['h1_packet_hash']}`",
        f"- B10 boundary hash: `{s['b10_boundary_hash']}`",
        "",
        "## Result",
        "",
        (
            f"The H1 access closure passes {s['requirements_passed']}/{s['requirement_count']} "
            "requirements. It does not accept H1; it proves H1 is still the immediate "
            "provider/session access blocker and keeps H2-H5 plus all B4/B8/B10 credit closed."
        ),
        "",
        "## Immediate Blocker",
        "",
        f"- H1 submitted artifact exists: `{s['h1_submitted_artifact_exists']}`",
        f"- H1 source failed requirements: `{s['h1_source_failed_requirement_ids']}`",
        f"- Missing H1 keys: `{s['h1_missing_key_count']}`",
        f"- Required H1 evidence file classes: `{s['h1_required_evidence_file_count']}`",
        f"- H2 hardware rows may start: `{s['h2_hardware_rows_may_start']}`",
        "",
        "## Locked Evidence Boundary",
        "",
        f"- Downstream transcript packet: `{s['downstream_transcript_packet_id']}`",
        f"- Holdout rows: `{s['holdout_row_count']}`",
        f"- No-leak / full-leak budgets per 160: `{s['no_leak_allowed_accepts_per_160']}` / `{s['full_leak_allowed_accepts_per_160']}`",
        f"- Real backend transcript rows: `{s['real_backend_transcript_rows']}`",
        f"- Accepted transcript rows: `{s['accepted_priority_transcript_rows']}`",
        f"- B8 soundness / B4 advantage / B10-T2 / BQP credit: `{s['b8_protocol_soundness_credit_allowed']}` / `{s['b4_verifiable_advantage_credit_allowed']}` / `{s['b10_t2_credit_allowed']}` / `{s['b10_bqp_separation_credit_allowed']}`",
        "",
        "## Blocker Chain",
        "",
    ]
    for row in packet["blocker_chain"]:
        lines.append(f"### {row['blocker_id']}: {row['status']}")
        for item in row["required_before_unlock"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend(["## Requirement Results", ""])
    for row in payload["requirements"]:
        marker = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- `{row['requirement_id']}` {marker}: {row['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            "This closure gate does not claim hardware execution, protocol soundness, cryptographic soundness, sampling hardness, quantum advantage, B4 advantage, B10-T2 credit, or BQP separation.",
            "",
            "## Validation",
            "",
            f"- validation_error_count: `{s['validation_error_count']}`",
        ]
    )
    for error in payload["validation_errors"]:
        lines.append(f"- {error}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--h1-packet-gate",
        type=Path,
        default=Path("results/B4_B8_H1_provider_session_replay_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--b10-boundary",
        type=Path,
        default=Path("results/B10_t2_real_backend_transcript_row_acceptance_boundary_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B4_B8_B10_H1_provider_session_access_closure_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B4_B8_B10_H1_provider_session_access_closure_gate.md"),
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
                "closure_hash": payload["summary"]["closure_hash"],
                "requirements_passed": payload["summary"]["requirements_passed"],
                "requirements_failed": payload["summary"]["requirements_failed"],
                "validation_error_count": payload["summary"]["validation_error_count"],
                "json_output": str(args.json_output),
                "markdown_output": str(args.markdown_output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B4/B8/B10 H1 provider/session access closure gate validation failed")


if __name__ == "__main__":
    main()
