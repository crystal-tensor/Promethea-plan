#!/usr/bin/env python3
"""T-B2-010j/T-B7-012k: C1 calibration source replay packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b2_b7_c1_calibration_source_replay_packet_gate_v0"
STATUS = "c1_calibration_source_replay_packet_open_missing_artifact"
MODEL_STATUS = "c1_real_or_independent_calibration_source_replay_contract_ready_no_credit"
VERSION = "0.1"
EXPECTED_PACKET_ID = "B2B7-C1-calibration-source-replay"
EXPECTED_SOURCE_MANIFEST_ID = "B2-T5-calibration-source-manifest"
EXPECTED_TRACE_PACKET_ID = "B2-T5-calibrated-flag-observation-rows"
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
    triage = load_json(args.post_boundary_triage)
    source_gate = load_json(args.calibration_source_manifest_gate)
    triage_summary = triage["summary"]
    source_summary = source_gate["summary"]
    submission_path = args.submission_dir / f"{EXPECTED_PACKET_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None

    required_keys = [
        "packet_id",
        "source_triage_id",
        "source_calibration_manifest_id",
        "trace_packet_id",
        "calibration_source_type",
        "backend_or_dataset_name",
        "acquisition_window_utc",
        "provider_or_dataset_access_hash",
        "backend_properties_or_noise_model_hash",
        "detector_trace_hash_manifest",
        "flag_event_schema_hash",
        "confusion_matrix_plan_hash",
        "holdout_partition_hash",
        "replay_command_hash",
        "independent_replay_bundle_hash",
        "claim_boundary",
    ]
    production_required_keys = [
        "calibration_source_type",
        "backend_or_dataset_name",
        "acquisition_window_utc",
        "provider_or_dataset_access_hash",
        "backend_properties_or_noise_model_hash",
        "detector_trace_hash_manifest",
        "flag_event_schema_hash",
        "holdout_partition_hash",
        "replay_command_hash",
        "claim_boundary",
    ]
    required_evidence_files = [
        "calibration_source_manifest",
        "provider_or_dataset_access_note",
        "acquisition_window_source",
        "backend_properties_or_noise_model_snapshot",
        "detector_trace_hash_manifest",
        "flag_event_schema_note",
        "confusion_matrix_or_labeling_plan",
        "holdout_partition_manifest",
        "independent_replay_bundle",
        "replay_command_transcript",
        "calibration_claim_boundary_note",
    ]

    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True
    source_bound = (
        submitted is not None
        and submitted.get("source_calibration_manifest_id") == EXPECTED_SOURCE_MANIFEST_ID
        and submitted.get("source_calibration_manifest_hash") == source_summary.get("manifest_hash")
    )
    trace_bound = submitted is not None and submitted.get("trace_packet_id") == EXPECTED_TRACE_PACKET_ID
    replay_bound = (
        submitted is not None
        and isinstance(submitted.get("replay_hashes"), dict)
        and submitted["replay_hashes"].get("trace_packet_id") == EXPECTED_TRACE_PACKET_ID
        and submitted["replay_hashes"].get("source_calibration_manifest_hash")
        == source_summary.get("manifest_hash")
    )
    source_type_allowed = (
        submitted is not None
        and submitted.get("calibration_source_type") in {"real_backend", "independent_calibration"}
    )

    c1_packet = {
        "packet_id": EXPECTED_PACKET_ID,
        "work_packet_id": "C1",
        "source_post_boundary_triage": str(args.post_boundary_triage),
        "source_calibration_source_manifest_gate": str(args.calibration_source_manifest_gate),
        "source_triage_hash": triage_summary.get("triage_hash"),
        "source_calibration_manifest_hash": source_summary.get("manifest_hash"),
        "source_calibration_manifest_id": EXPECTED_SOURCE_MANIFEST_ID,
        "blocks_trace_packet": EXPECTED_TRACE_PACKET_ID,
        "submission_artifact_path": str(submission_path),
        "required_keys": required_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": required_evidence_files,
        "accepted_only_if": [
            "packet_id equals B2B7-C1-calibration-source-replay",
            "source_calibration_manifest_id equals B2-T5-calibration-source-manifest",
            "trace_packet_id equals B2-T5-calibrated-flag-observation-rows",
            "calibration_source_type is real_backend or independent_calibration",
            "backend or dataset access, acquisition window, backend/noise snapshot, detector trace hash manifest, flag schema, holdout partition, replay command, and independent replay bundle are present",
            "replay_hashes bind source_calibration_manifest_hash and trace_packet_id",
            "source evidence files are present and hash-bound",
            "claim_boundary forbids production decoder, threshold, calibrated-device, hardware-result, new-code, quantum-advantage, and B7 resource-credit claims",
        ],
        "locked_scope": {
            "challenge_count": triage_summary.get("challenge_count"),
            "source_trace_count": triage_summary.get("source_trace_count"),
            "holdout_profile_shots": triage_summary.get("holdout_profile_shots"),
        },
    }
    c1_packet["packet_hash"] = stable_hash(c1_packet)

    requirements = [
        requirement(
            "P1",
            "Post-boundary triage is valid and exposes C1 as a ready PR packet",
            triage.get("method") == "b2_b7_calibrated_trace_post_boundary_submission_triage_v0"
            and triage_summary.get("validation_error_count") == 0
            and "C1" in triage_summary.get("ready_packet_ids", []),
            {
                "source_method": triage.get("method"),
                "ready_packet_ids": triage_summary.get("ready_packet_ids"),
                "validation_error_count": triage_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "C4 B7 dependency replay remains blocked while accepted calibrated rows are zero",
            triage_summary.get("blocked_packet_ids") == ["C4"]
            and triage_summary.get("accepted_priority_trace_rows") == 0
            and triage_summary.get("b7_dependency_credit_allowed") is False,
            {
                "blocked_packet_ids": triage_summary.get("blocked_packet_ids"),
                "accepted_priority_trace_rows": triage_summary.get(
                    "accepted_priority_trace_rows"
                ),
                "b7_dependency_credit_allowed": triage_summary.get(
                    "b7_dependency_credit_allowed"
                ),
            },
        ),
        requirement(
            "P3",
            "Existing calibration source manifest gate remains the C1 source and is open on P6/P7/P8",
            source_gate.get("method") == "b2_calibration_source_manifest_gate_v0"
            and source_summary.get("manifest_id") == EXPECTED_SOURCE_MANIFEST_ID
            and source_summary.get("failed_manifest_requirement_ids") == EXPECTED_FAILED_IDS,
            {
                "source_method": source_gate.get("method"),
                "manifest_id": source_summary.get("manifest_id"),
                "failed_manifest_requirement_ids": source_summary.get(
                    "failed_manifest_requirement_ids"
                ),
                "manifest_hash": source_summary.get("manifest_hash"),
            },
        ),
        requirement(
            "P4",
            "Locked calibrated trace scope is preserved",
            triage_summary.get("challenge_count") == 3
            and triage_summary.get("source_trace_count") == 576
            and triage_summary.get("holdout_profile_shots") == 864,
            {
                "challenge_count": triage_summary.get("challenge_count"),
                "source_trace_count": triage_summary.get("source_trace_count"),
                "holdout_profile_shots": triage_summary.get("holdout_profile_shots"),
            },
        ),
        requirement(
            "P5",
            "C1 packet schema and evidence classes are locked",
            len(required_keys) == 16
            and len(production_required_keys) == 10
            and len(required_evidence_files) == 11,
            {
                "required_key_count": len(required_keys),
                "production_required_key_count": len(production_required_keys),
                "required_evidence_file_count": len(required_evidence_files),
            },
        ),
        requirement(
            "P6",
            "C1 calibration source replay artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted C1 replay artifact satisfies the locked schema",
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
            "Submitted C1 replay artifact is source-backed, trace-bound, replay-bound, and source-type valid",
            source_backed and source_bound and trace_bound and replay_bound and source_type_allowed,
            {
                "source_evidence_files_present": source_backed,
                "source_bound": source_bound,
                "trace_bound": trace_bound,
                "replay_bound": replay_bound,
                "source_type_allowed": source_type_allowed,
                "calibration_source_type": submitted.get("calibration_source_type") if submitted else None,
            },
        ),
        requirement(
            "P9",
            "Forbidden B2/B7 decoder, hardware, threshold, advantage, and credit claims remain false",
            triage_summary.get("production_decoder_claimed") is False
            and triage_summary.get("threshold_claimed") is False
            and triage_summary.get("hardware_result_claimed") is False
            and triage_summary.get("calibrated_device_claimed") is False
            and triage_summary.get("quantum_advantage_claimed") is False
            and triage_summary.get("b7_dependency_credit_allowed") is False,
            {
                "production_decoder_claimed": triage_summary.get("production_decoder_claimed"),
                "threshold_claimed": triage_summary.get("threshold_claimed"),
                "hardware_result_claimed": triage_summary.get("hardware_result_claimed"),
                "calibrated_device_claimed": triage_summary.get("calibrated_device_claimed"),
                "quantum_advantage_claimed": triage_summary.get("quantum_advantage_claimed"),
                "b7_dependency_credit_allowed": triage_summary.get("b7_dependency_credit_allowed"),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected C1 replay packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted C1 replay artifact until a hardware data PR supplies one")

    summary = {
        "c1_packet_id": EXPECTED_PACKET_ID,
        "c1_packet_hash": c1_packet["packet_hash"],
        "source_triage_hash": triage_summary.get("triage_hash"),
        "source_calibration_manifest_hash": source_summary.get("manifest_hash"),
        "source_calibration_manifest_id": EXPECTED_SOURCE_MANIFEST_ID,
        "trace_packet_id": EXPECTED_TRACE_PACKET_ID,
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(required_evidence_files),
        "challenge_count": triage_summary.get("challenge_count"),
        "source_trace_count": triage_summary.get("source_trace_count"),
        "holdout_profile_shots": triage_summary.get("holdout_profile_shots"),
        "accepted_priority_trace_rows": triage_summary.get("accepted_priority_trace_rows"),
        "submitted_c1_artifact_exists": submitted_exists,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "c1_calibration_source_replay_accepted": False,
        "b7_dependency_credit_allowed": False,
        "b7_ft_ledger_credit_allowed": False,
        "b7_resource_credit_allowed": False,
        "production_decoder_claimed": False,
        "threshold_claimed": False,
        "hardware_result_claimed": False,
        "calibrated_device_claimed": False,
        "new_code_claimed": False,
        "quantum_advantage_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B2",
        "linked_benchmark_id": "B7",
        "source_target_id": "T-B2-010j/T-B7-012k",
        "title": "B2/B7 C1 Calibration Source Replay Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_post_boundary_triage": str(args.post_boundary_triage),
        "source_calibration_source_manifest_gate": str(args.calibration_source_manifest_gate),
        "summary": summary,
        "c1_replay_packet": c1_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": "C1 now has a locked real-or-independent calibration source replay packet schema and acceptance boundary.",
            "what_is_not_supported": "No C1 replay artifact, accepted calibrated trace row, production decoder, threshold, hardware result, calibrated-device result, quantum advantage, or B7 credit is supported.",
            "next_gate": "Submit the C1 replay artifact with source-backed calibration source, backend or dataset access, acquisition window, backend/noise snapshot, detector trace hashes, flag schema, holdout partition, independent replay bundle, replay command, and claim boundary.",
            "production_decoder_claimed": False,
            "threshold_claimed": False,
            "hardware_result_claimed": False,
            "calibrated_device_claimed": False,
            "quantum_advantage_claimed": False,
            "b7_dependency_credit_allowed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    p = payload["c1_replay_packet"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- C1 packet: `{s['c1_packet_id']}`",
        f"- C1 packet hash: `{s['c1_packet_hash']}`",
        f"- Source triage hash: `{s['source_triage_hash']}`",
        f"- Source calibration manifest hash: `{s['source_calibration_manifest_hash']}`",
        "",
        "## Result",
        "",
        (
            f"The C1 gate passes {s['requirements_passed']}/{s['requirement_count']} "
            f"requirements and intentionally fails {s['failed_requirement_ids']} because no "
            "source-backed real-or-independent calibration replay artifact has been submitted."
        ),
        "",
        "## Locked C1 Packet",
        "",
        f"- Submission path: `{p['submission_artifact_path']}`",
        f"- Required keys: `{s['required_key_count']}`",
        f"- Production required keys: `{s['production_required_key_count']}`",
        f"- Evidence file classes: `{s['required_evidence_file_count']}`",
        "",
        "Required evidence files:",
        "",
    ]
    for item in p["required_evidence_files"]:
        lines.append(f"- {item}")
    lines.extend(["", "Acceptance predicates:", ""])
    for item in p["accepted_only_if"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            f"- Trace packet: `{s['trace_packet_id']}`",
            f"- Challenges / source traces / holdout profile-shots: `{s['challenge_count']}` / `{s['source_trace_count']}` / `{s['holdout_profile_shots']}`",
            f"- Accepted calibrated trace rows: `{s['accepted_priority_trace_rows']}`",
            f"- C1 accepted: `{s['c1_calibration_source_replay_accepted']}`",
            f"- B7 dependency / FT ledger / resource credit: `{s['b7_dependency_credit_allowed']}` / `{s['b7_ft_ledger_credit_allowed']}` / `{s['b7_resource_credit_allowed']}`",
            "",
            "## Requirement Results",
            "",
        ]
    )
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
            "This packet gate does not claim a production decoder, threshold, hardware result, calibrated-device result, new code, quantum advantage, B7 dependency credit, FT ledger credit, or resource credit.",
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
        "--post-boundary-triage",
        type=Path,
        default=Path("results/B2_B7_calibrated_trace_post_boundary_submission_triage_v0.json"),
    )
    parser.add_argument(
        "--calibration-source-manifest-gate",
        type=Path,
        default=Path("results/B2_calibration_source_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B2_B7_C1_calibration_source_replay_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B2_B7_C1_calibration_source_replay_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B2_B7_C1_calibration_source_replay_packet_gate.md"),
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
                "c1_packet_hash": payload["summary"]["c1_packet_hash"],
                "requirements_passed": payload["summary"]["requirements_passed"],
                "requirements_failed": payload["summary"]["requirements_failed"],
                "failed_requirement_ids": payload["summary"]["failed_requirement_ids"],
                "validation_error_count": payload["summary"]["validation_error_count"],
                "json_output": str(args.json_output),
                "markdown_output": str(args.markdown_output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B2/B7 C1 calibration source replay packet gate validation failed")


if __name__ == "__main__":
    main()
