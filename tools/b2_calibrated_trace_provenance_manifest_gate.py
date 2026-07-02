#!/usr/bin/env python3
"""T-B2-010e/T-B7-012b: calibrated-trace row provenance manifest gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b2_calibrated_trace_provenance_manifest_gate_v0"
STATUS = "calibrated_trace_provenance_manifest_open_missing_artifact"
MODEL_STATUS = "trace_row_provenance_manifest_required_before_b2_b7_credit"
VERSION = "0.1"
EXPECTED_SOURCE_MANIFEST_ID = "B2-T5-calibration-source-manifest"
EXPECTED_TRACE_PACKET_ID = "B2-T5-calibrated-flag-observation-rows"
EXPECTED_PROVENANCE_MANIFEST_ID = "B2-T5-calibrated-trace-row-provenance-manifest"
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
    source_gate = load_json(args.calibration_source_manifest_gate)
    b7_credit = load_json(args.b7_dependency_credit_gate)
    source_summary = source_gate["summary"]
    b7_summary = b7_credit["summary"]
    submission_path = args.submission_dir / f"{EXPECTED_PROVENANCE_MANIFEST_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None

    required_keys = [
        "manifest_id",
        "calibration_source_manifest_id",
        "trace_packet_id",
        "calibration_source_manifest_hash",
        "row_batch_manifest_hash",
        "detector_trace_hash_manifest",
        "flag_event_schema_hash",
        "confusion_matrix_artifact_hash",
        "decoder_profile_manifest_hash",
        "holdout_partition_hash",
        "posterior_likelihood_profile_hash",
        "baseline_prediction_manifest_hash",
        "injected_prediction_manifest_hash",
        "replay_command_hash",
        "b7_credit_boundary",
        "claim_boundary",
    ]
    production_required_keys = [
        "calibration_source_manifest_hash",
        "row_batch_manifest_hash",
        "detector_trace_hash_manifest",
        "flag_event_schema_hash",
        "confusion_matrix_artifact_hash",
        "decoder_profile_manifest_hash",
        "holdout_partition_hash",
        "posterior_likelihood_profile_hash",
        "baseline_prediction_manifest_hash",
        "injected_prediction_manifest_hash",
        "replay_command_hash",
    ]
    evidence_files = [
        "accepted_calibration_source_manifest",
        "row_batch_manifest",
        "detector_trace_hash_manifest",
        "flag_event_schema_note",
        "confusion_matrix_artifact",
        "decoder_profile_manifest",
        "holdout_partition_manifest",
        "posterior_likelihood_profile",
        "baseline_prediction_manifest",
        "injected_prediction_manifest",
        "replay_command_transcript",
        "b7_credit_boundary_note",
        "claim_boundary_note",
    ]

    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    replay_hashes = submitted.get("replay_hashes") if submitted else None
    replay_bound = (
        isinstance(replay_hashes, dict)
        and replay_hashes.get("calibration_source_manifest_hash") == source_summary.get("manifest_hash")
        and replay_hashes.get("trace_packet_id") == EXPECTED_TRACE_PACKET_ID
    )
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True
    manifest_bound = (
        submitted is not None
        and submitted.get("manifest_id") == EXPECTED_PROVENANCE_MANIFEST_ID
        and submitted.get("calibration_source_manifest_id") == EXPECTED_SOURCE_MANIFEST_ID
        and submitted.get("trace_packet_id") == EXPECTED_TRACE_PACKET_ID
        and submitted.get("calibration_source_manifest_hash") == source_summary.get("manifest_hash")
    )
    b7_boundary_declared = (
        submitted is not None
        and isinstance(submitted.get("b7_credit_boundary"), dict)
        and submitted["b7_credit_boundary"].get("dependency_credit_allowed") is False
    )

    manifest_packet = {
        "manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "calibration_source_manifest_id": EXPECTED_SOURCE_MANIFEST_ID,
        "trace_packet_id": EXPECTED_TRACE_PACKET_ID,
        "source_calibration_manifest_gate": str(args.calibration_source_manifest_gate),
        "source_b7_dependency_credit_gate": str(args.b7_dependency_credit_gate),
        "submission_artifact_path": str(submission_path),
        "calibration_source_manifest_hash": source_summary.get("manifest_hash"),
        "challenge_count": source_summary.get("challenge_count"),
        "source_trace_count": source_summary.get("source_trace_count"),
        "holdout_profile_shots": source_summary.get("holdout_profile_shots"),
        "required_keys": required_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": evidence_files,
        "accepted_only_if": [
            "manifest_id equals B2-T5-calibrated-trace-row-provenance-manifest",
            "calibration_source_manifest_id equals B2-T5-calibration-source-manifest",
            "trace_packet_id equals B2-T5-calibrated-flag-observation-rows",
            "calibration_source_manifest_hash matches the accepted source-manifest gate hash",
            "row batch, detector trace hashes, flag schema, confusion matrix, decoder profile, holdout partition, posterior likelihood profile, baseline predictions, and injected predictions are hash-bound",
            "replay_hashes bind calibration_source_manifest_hash and trace_packet_id",
            "source evidence files are present and hash-bound",
            "b7_credit_boundary keeps dependency_credit_allowed false until accepted calibrated trace rows and all-challenge holdout non-regression exist",
            "claim_boundary forbids production decoder, threshold, calibrated-device, hardware-result, new-code, quantum-advantage, and B7 resource-credit claims",
        ],
    }
    manifest_packet["manifest_hash"] = stable_hash(manifest_packet)

    forbidden_claims = [
        "production_decoder_claimed",
        "threshold_claimed",
        "new_code_claimed",
        "hardware_result_claimed",
        "calibrated_device_claimed",
        "quantum_advantage_claimed",
    ]
    requirements = [
        requirement(
            "P1",
            "Calibration source manifest gate remains valid and blocked only on P6/P7/P8",
            source_gate.get("method") == "b2_calibration_source_manifest_gate_v0"
            and source_summary.get("validation_error_count") == 0
            and source_summary.get("failed_manifest_requirement_ids") == ["P6", "P7", "P8"],
            {
                "source_status": source_gate.get("status"),
                "failed_manifest_requirement_ids": source_summary.get("failed_manifest_requirement_ids"),
                "validation_error_count": source_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Trace provenance manifest is bound to the source manifest and calibrated trace row packet",
            source_summary.get("manifest_id") == EXPECTED_SOURCE_MANIFEST_ID
            and source_summary.get("downstream_packet_id") == EXPECTED_TRACE_PACKET_ID
            and source_summary.get("accepted_priority_trace_rows") == 0,
            {
                "source_manifest_id": source_summary.get("manifest_id"),
                "downstream_packet_id": source_summary.get("downstream_packet_id"),
                "accepted_priority_trace_rows": source_summary.get("accepted_priority_trace_rows"),
            },
        ),
        requirement(
            "P3",
            "Manifest packet carries locked trace-row provenance schema and evidence classes",
            len(required_keys) == 16
            and len(production_required_keys) == 11
            and len(evidence_files) == 13,
            {
                "required_key_count": len(required_keys),
                "production_required_key_count": len(production_required_keys),
                "required_evidence_file_count": len(evidence_files),
            },
        ),
        requirement(
            "P4",
            "Existing B2 trace denominator shape is preserved",
            source_summary.get("challenge_count") == 3
            and source_summary.get("source_trace_count") == 576
            and source_summary.get("holdout_profile_shots") == 864,
            {
                "challenge_count": source_summary.get("challenge_count"),
                "source_trace_count": source_summary.get("source_trace_count"),
                "holdout_profile_shots": source_summary.get("holdout_profile_shots"),
            },
        ),
        requirement(
            "P5",
            "B7 dependency credit remains blocked before accepted calibrated trace rows",
            b7_summary.get("dependency_credit_allowed") is False
            and source_summary.get("b7_dependency_credit_allowed") is False
            and source_summary.get("accepted_priority_trace_rows") == 0,
            {
                "b7_dependency_credit_allowed": b7_summary.get("dependency_credit_allowed"),
                "source_manifest_b7_dependency_credit_allowed": source_summary.get("b7_dependency_credit_allowed"),
                "accepted_priority_trace_rows": source_summary.get("accepted_priority_trace_rows"),
            },
        ),
        requirement(
            "P6",
            "Calibrated trace row provenance manifest artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted manifest satisfies the locked trace-row provenance schema",
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
            "Submitted manifest is source-backed, source-manifest-bound, replay-bound, and B7-boundary-bound",
            source_backed and manifest_bound and replay_bound and b7_boundary_declared,
            {
                "source_evidence_files_present": source_backed,
                "manifest_bound": manifest_bound,
                "replay_bound": replay_bound,
                "b7_boundary_declared": b7_boundary_declared,
            },
        ),
        requirement(
            "P9",
            "Forbidden decoder, threshold, hardware, advantage, and B7-credit claims remain false",
            all(source_summary.get(key) is False for key in forbidden_claims)
            and b7_summary.get("dependency_credit_allowed") is False,
            {
                **{key: source_summary.get(key) for key in forbidden_claims},
                "b7_dependency_credit_allowed": b7_summary.get("dependency_credit_allowed"),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected trace provenance manifest failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted provenance manifest until a hardware-data PR supplies one")

    summary = {
        "manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "calibration_source_manifest_id": EXPECTED_SOURCE_MANIFEST_ID,
        "trace_packet_id": EXPECTED_TRACE_PACKET_ID,
        "calibration_source_manifest_hash": source_summary.get("manifest_hash"),
        "manifest_hash": manifest_packet["manifest_hash"],
        "manifest_requirement_count": len(requirements),
        "manifest_requirements_passed": passed,
        "manifest_requirements_failed": len(requirements) - passed,
        "failed_manifest_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(evidence_files),
        "challenge_count": source_summary.get("challenge_count"),
        "source_trace_count": source_summary.get("source_trace_count"),
        "holdout_profile_shots": source_summary.get("holdout_profile_shots"),
        "submitted_manifest_exists": submitted_exists,
        "submitted_key_count": len(submitted) if submitted else 0,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "accepted_priority_trace_rows": source_summary.get("accepted_priority_trace_rows"),
        "b7_dependency_credit_allowed": False,
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
        "linked_benchmark_id": "B7",
        "problem_id": 22,
        "title": "B2 Calibrated Trace Row Provenance Manifest Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_calibration_manifest_gate": str(args.calibration_source_manifest_gate),
        "source_b7_dependency_credit_gate": str(args.b7_dependency_credit_gate),
        "summary": summary,
        "calibrated_trace_provenance_manifest_packet": manifest_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The B2/B7 calibrated-trace path now has a row-level provenance manifest packet "
                "that must bind calibration-source hashes, row-batch hashes, decoder inputs, "
                "holdout partitions, replay commands, and a zero-credit B7 boundary."
            ),
            "what_is_not_supported": (
                "No calibrated trace provenance manifest or calibrated trace row has been submitted "
                "or accepted; no production decoder, threshold, hardware result, calibrated-device "
                "result, new-code result, quantum advantage, or B7 resource credit is supported."
            ),
            "next_gate": (
                "Submit B2-T5-calibrated-trace-row-provenance-manifest with the accepted "
                "calibration source manifest hash, row-batch and detector trace hashes, decoder "
                "profile hashes, holdout partition hash, baseline/injected prediction hashes, "
                "replay command hash, and explicit B7 zero-credit boundary."
            ),
            "production_decoder_claimed": False,
            "threshold_claimed": False,
            "new_code_claimed": False,
            "hardware_result_claimed": False,
            "calibrated_device_claimed": False,
            "quantum_advantage_claimed": False,
            "b7_dependency_credit_allowed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["calibrated_trace_provenance_manifest_packet"]
    lines = [
        "# B2 Calibrated Trace Row Provenance Manifest Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Manifest: `{summary['manifest_id']}`",
        f"- Calibration source manifest: `{summary['calibration_source_manifest_id']}`",
        f"- Trace packet: `{summary['trace_packet_id']}`",
        f"- Calibration source manifest hash: `{summary['calibration_source_manifest_hash']}`",
        f"- Manifest hash: `{summary['manifest_hash']}`",
        f"- Requirements passed/failed: `{summary['manifest_requirements_passed']}` / `{summary['manifest_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_manifest_requirement_ids']}`",
        f"- Required key / production key / evidence file count: `{summary['required_key_count']}` / `{summary['production_required_key_count']}` / `{summary['required_evidence_file_count']}`",
        f"- Challenge count / source traces / holdout profile shots: `{summary['challenge_count']}` / `{summary['source_trace_count']}` / `{summary['holdout_profile_shots']}`",
        f"- Submitted manifest exists: `{summary['submitted_manifest_exists']}`",
        f"- Accepted priority trace rows: `{summary['accepted_priority_trace_rows']}`",
        f"- B7 dependency credit allowed: `{summary['b7_dependency_credit_allowed']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Manifest Packet",
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
            f"- b7_dependency_credit_allowed: {payload['claim_boundary']['b7_dependency_credit_allowed']}",
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
        "--calibration-source-manifest-gate",
        type=Path,
        default=Path("results/B2_calibration_source_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--b7-dependency-credit-gate",
        type=Path,
        default=Path("results/B7_B2_calibrated_dependency_credit_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B2_calibrated_trace_provenance_manifest_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B2_calibrated_trace_provenance_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B2_calibrated_trace_provenance_manifest_gate.md"),
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
