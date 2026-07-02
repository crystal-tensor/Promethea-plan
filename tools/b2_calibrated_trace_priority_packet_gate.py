#!/usr/bin/env python3
"""T-B2-010c: priority calibrated-trace row submission-packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b2_calibrated_trace_priority_packet_gate_v0"
STATUS = "calibrated_trace_priority_packet_open_missing_artifact"
MODEL_STATUS = "priority_calibrated_trace_contract_ready_no_row_submitted"
VERSION = "0.1"
EXPECTED_PACKET_ID = "B2-T5-calibrated-flag-observation-rows"
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
    intake = load_json(args.intake_template)
    packet = next(
        (row for row in intake["intake_packets"] if row["packet_id"] == EXPECTED_PACKET_ID),
        None,
    )
    submission_path = args.submission_dir / f"{EXPECTED_PACKET_ID}.json"
    required_row_keys = list(intake["required_row_keys"])
    production_required_keys = list(intake["production_required_keys"])
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None
    submitted_keys = sorted(submitted) if submitted else []
    missing_keys = [key for key in required_row_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    source_backed = (
        submitted is not None
        and submitted.get("source_evidence_files_present") is True
        and len(production_present) == len(production_required_keys)
    )

    priority_packet = {
        "packet_id": EXPECTED_PACKET_ID,
        "blocks_contract_gate": packet["blocks_contract_gate"] if packet else None,
        "blocks_scout_gate": packet["blocks_scout_gate"] if packet else None,
        "owner_role": packet["owner_role"] if packet else None,
        "template_hash": packet["template_hash"] if packet else None,
        "submission_artifact_path": str(submission_path),
        "required_row_keys": required_row_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": [
            "backend_or_calibration_source_manifest",
            "backend_properties_hash_source",
            "detector_bitstring_artifact",
            "calibrated_flag_events_artifact",
            "flag_confusion_matrix_artifact",
            "decoder_profile_manifest",
            "raw_trace_artifact",
            "postprocess_script",
        ],
        "accepted_only_if": [
            "all 21 required trace-row keys are present",
            "all 10 production-required keys are non-null and source-backed",
            "challenge_trace_hash is preserved from the existing B2 trace scout",
            "holdout_partition is declared before decoder comparison",
            "baseline_prediction and injected_prediction are replayable from source artifacts",
            "claim_boundary forbids production decoder, threshold, hardware, new-code, and advantage claims",
        ],
    }
    priority_packet["packet_hash"] = stable_hash(priority_packet)

    requirements = [
        requirement(
            "P1",
            "Intake template remains valid and open on calibrated rows",
            intake.get("method") == "b2_calibrated_trace_intake_template_gate_v0"
            and intake["summary"].get("validation_error_count") == 0
            and intake["summary"].get("failed_intake_requirement_ids") == ["T5", "T6", "T7"],
            {
                "source_status": intake.get("status"),
                "failed_intake_requirement_ids": intake["summary"].get("failed_intake_requirement_ids"),
                "validation_error_count": intake["summary"].get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Priority packet is fixed to calibrated flag observation rows",
            packet is not None
            and packet["packet_id"] == EXPECTED_PACKET_ID
            and packet["blocks_contract_gate"] == "K4"
            and packet["blocks_scout_gate"] == "S5",
            {
                "expected_packet_id": EXPECTED_PACKET_ID,
                "actual_packet_id": packet["packet_id"] if packet else None,
                "blocks_contract_gate": packet["blocks_contract_gate"] if packet else None,
                "blocks_scout_gate": packet["blocks_scout_gate"] if packet else None,
            },
        ),
        requirement(
            "P3",
            "Priority packet carries the 21-key trace schema and 10 production keys",
            len(required_row_keys) == 21 and len(production_required_keys) == 10,
            {
                "required_row_key_count": len(required_row_keys),
                "production_required_key_count": len(production_required_keys),
            },
        ),
        requirement(
            "P4",
            "Packet binds required source evidence classes",
            len(priority_packet["required_evidence_files"]) == 8,
            {"required_evidence_files": priority_packet["required_evidence_files"]},
        ),
        requirement(
            "P5",
            "Existing 3-challenge / 576-trace shape remains preserved",
            intake["summary"].get("challenge_count") == 3
            and intake["summary"].get("source_trace_count") == 576
            and intake["summary"].get("holdout_profile_shots") == 864,
            {
                "challenge_count": intake["summary"].get("challenge_count"),
                "source_trace_count": intake["summary"].get("source_trace_count"),
                "holdout_profile_shots": intake["summary"].get("holdout_profile_shots"),
            },
        ),
        requirement(
            "P6",
            "Priority calibrated trace artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted artifact satisfies the locked 21-key schema",
            submitted_exists and not missing_keys,
            {"submitted_key_count": len(submitted_keys), "missing_keys": missing_keys},
        ),
        requirement(
            "P8",
            "Submitted production keys are source-backed and non-null",
            source_backed,
            {
                "production_keys_present": production_present,
                "production_required_keys": production_required_keys,
                "source_evidence_files_present": submitted.get("source_evidence_files_present") if submitted else False,
            },
        ),
        requirement(
            "P9",
            "Forbidden decoder, threshold, hardware, new-code, and advantage claims remain false",
            all(
                intake["summary"].get(key) is False
                for key in [
                    "production_decoder_claimed",
                    "threshold_claimed",
                    "new_code_claimed",
                    "hardware_result_claimed",
                    "calibrated_device_claimed",
                    "quantum_advantage_claimed",
                ]
            ),
            {
                "production_decoder_claimed": intake["summary"].get("production_decoder_claimed"),
                "threshold_claimed": intake["summary"].get("threshold_claimed"),
                "hardware_result_claimed": intake["summary"].get("hardware_result_claimed"),
                "calibrated_device_claimed": intake["summary"].get("calibrated_device_claimed"),
                "quantum_advantage_claimed": intake["summary"].get("quantum_advantage_claimed"),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected priority packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted artifact until a hardware-data PR supplies one")

    summary = {
        "priority_packet_id": EXPECTED_PACKET_ID,
        "packet_hash": priority_packet["packet_hash"],
        "priority_requirement_count": len(requirements),
        "priority_requirements_passed": passed,
        "priority_requirements_failed": len(requirements) - passed,
        "failed_priority_requirement_ids": failed_ids,
        "required_row_key_count": len(required_row_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(priority_packet["required_evidence_files"]),
        "challenge_count": intake["summary"].get("challenge_count"),
        "source_trace_count": intake["summary"].get("source_trace_count"),
        "holdout_profile_shots": intake["summary"].get("holdout_profile_shots"),
        "submitted_artifact_exists": submitted_exists,
        "submitted_key_count": len(submitted_keys),
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "accepted_priority_trace_rows": 0,
        "production_decoder_claimed": False,
        "threshold_claimed": False,
        "new_code_claimed": False,
        "hardware_result_claimed": False,
        "calibrated_device_claimed": False,
        "quantum_advantage_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 Calibrated Trace Priority Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_intake_template_result": str(args.intake_template),
        "summary": summary,
        "priority_trace_packet": priority_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The first B2 calibrated-trace blocker now has a concrete source-backed row "
                "submission packet for calibrated flag observations."
            ),
            "what_is_not_supported": (
                "No calibrated trace row has been submitted or accepted; no production decoder, "
                "threshold, hardware result, calibrated-device result, new-code result, or "
                "quantum advantage is supported."
            ),
            "next_gate": (
                f"Submit {submission_path} with all 21 row keys, all 10 source-backed "
                "production keys, and replayable baseline/injected decoder predictions."
            ),
            "production_decoder_claimed": False,
            "threshold_claimed": False,
            "new_code_claimed": False,
            "hardware_result_claimed": False,
            "calibrated_device_claimed": False,
            "quantum_advantage_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["priority_trace_packet"]
    lines = [
        "# B2 Calibrated Trace Priority Packet Gate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Priority packet: `{summary['priority_packet_id']}`",
        f"- Packet hash: `{summary['packet_hash']}`",
        f"- Requirements passed/failed: {summary['priority_requirements_passed']} / {summary['priority_requirements_failed']}",
        f"- Failed requirement IDs: {summary['failed_priority_requirement_ids']}",
        f"- Required row keys / production keys: {summary['required_row_key_count']} / {summary['production_required_key_count']}",
        f"- Required evidence files: {summary['required_evidence_file_count']}",
        f"- Challenge count / source traces / holdout profile shots: {summary['challenge_count']} / {summary['source_trace_count']} / {summary['holdout_profile_shots']}",
        f"- Submitted artifact exists: {summary['submitted_artifact_exists']}",
        "",
        "## Priority Packet",
        "",
        f"- packet_id: `{packet['packet_id']}`",
        f"- submission_artifact_path: `{packet['submission_artifact_path']}`",
        f"- blocks_contract_gate: `{packet['blocks_contract_gate']}`",
        f"- blocks_scout_gate: `{packet['blocks_scout_gate']}`",
        "",
        "## Required Evidence Files",
        "",
    ]
    for item in packet["required_evidence_files"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Acceptance Conditions", ""])
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
            f"- production_decoder_claimed: {payload['claim_boundary']['production_decoder_claimed']}",
            f"- threshold_claimed: {payload['claim_boundary']['threshold_claimed']}",
            f"- hardware_result_claimed: {payload['claim_boundary']['hardware_result_claimed']}",
            f"- calibrated_device_claimed: {payload['claim_boundary']['calibrated_device_claimed']}",
            f"- quantum_advantage_claimed: {payload['claim_boundary']['quantum_advantage_claimed']}",
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
        "--intake-template",
        type=Path,
        default=Path("results/B2_calibrated_trace_intake_template_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B2_calibrated_trace_priority_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B2_calibrated_trace_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B2_calibrated_trace_priority_packet_gate.md"),
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
