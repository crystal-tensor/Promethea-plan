#!/usr/bin/env python3
"""T-B2-010i/T-B7-012j: post-boundary submission triage for calibrated traces."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b2_b7_calibrated_trace_post_boundary_submission_triage_v0"
STATUS = "calibrated_trace_post_boundary_submission_triage_ready_no_credit"
MODEL_STATUS = "b7_zero_credit_calibrated_trace_boundary_split_into_pr_sized_trace_packets"
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
    priority = load_json(args.priority_packet_gate)
    boundary_summary = boundary["summary"]
    acceptance_summary = acceptance["summary"]
    priority_summary = priority["summary"]

    work_packets = [
        packet(
            "C1",
            "Real or independently calibrated trace source replay",
            "hardware-data-agent",
            "ready_for_external_pr_not_credit",
            "no real or independently calibrated trace replay has been submitted",
            [
                "submissions/B2-T5-calibrated-flag-observation-rows/calibration_source_manifest.json",
                "submissions/B2-T5-calibrated-flag-observation-rows/independent_calibration_bundle/",
                "submissions/B2-T5-calibrated-flag-observation-rows/calibration_claim_boundary.md",
            ],
            [
                "calibration source is real or independently calibrated",
                "backend/noise/source hashes are reproducible",
                "claim boundary forbids hardware, threshold, and calibrated-device claims",
            ],
        ),
        packet(
            "C2",
            "Accepted calibrated trace row batch",
            "qec-agent",
            "ready_for_external_pr_not_credit",
            "accepted calibrated trace rows remain zero",
            [
                "submissions/B2-T5-calibrated-flag-observation-rows/row_batch_manifest.json",
                "submissions/B2-T5-calibrated-flag-observation-rows/detector_trace_manifest.json",
                "submissions/B2-T5-calibrated-flag-observation-rows/decoder_profile_manifest.json",
            ],
            [
                "accepted_trace_row_count > 0",
                "3 challenges remain covered",
                "576 source traces are hash-bound to row and decoder artifacts",
            ],
        ),
        packet(
            "C3",
            "Strict holdout improvement with all-challenge non-regression",
            "baseline-adversary",
            "ready_for_external_pr_not_credit",
            "strict holdout improvement and all-challenge non-regression have not been accepted",
            [
                "submissions/B2-T5-calibrated-flag-observation-rows/holdout_partition_manifest.json",
                "submissions/B2-T5-calibrated-flag-observation-rows/holdout_nonregression_table.json",
                "submissions/B2-T5-calibrated-flag-observation-rows/all_challenge_coverage_table.json",
            ],
            [
                "864 holdout profile-shots remain covered",
                "all_challenge_nonregression_passed is true",
                "strict holdout improvement is measured against the same decoder path",
            ],
        ),
        packet(
            "C4",
            "B7 dependency ledger replay after accepted calibrated rows",
            "fault-tolerance-agent",
            "blocked_until_C1_C2_C3_accept",
            "B7 dependency ledger cannot count credit before calibrated rows and holdout evidence are accepted",
            [
                "submissions/B2-T5-calibrated-flag-observation-rows/b7_dependency_ledger_replay.json",
                "submissions/B2-T5-calibrated-flag-observation-rows/b7_credit_boundary.json",
            ],
            [
                "C1/C2/C3 are accepted by the trace row acceptance packet",
                "b7_credit_delta is computed under the same challenge and holdout scope",
                "B7 dependency/FT/resource credit remains false until the ledger accepts the route",
            ],
        ),
    ]
    ready_packets = [p for p in work_packets if p["status"] == "ready_for_external_pr_not_credit"]
    blocked_packets = [p for p in work_packets if p["status"].startswith("blocked_")]
    triage_packet = {
        "triage_id": "B2-B7-calibrated-trace-post-boundary-submission-triage",
        "source_boundary": str(args.boundary),
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "boundary_hash": boundary_summary.get("boundary_hash"),
        "acceptance_packet_hash": boundary_summary.get("source_acceptance_packet_hash"),
        "priority_packet_hash": acceptance_summary.get("priority_packet_hash"),
        "trace_packet_id": boundary_summary.get("trace_packet_id"),
        "challenge_count": boundary_summary.get("challenge_count"),
        "source_trace_count": boundary_summary.get("source_trace_count"),
        "holdout_profile_shots": boundary_summary.get("holdout_profile_shots"),
        "accepted_priority_trace_rows": boundary_summary.get("accepted_priority_trace_rows"),
        "b7_dependency_credit_allowed": False,
        "b7_ft_ledger_credit_allowed": False,
        "b7_resource_credit_allowed": False,
        "b7_space_time_volume_reduction_credit": 0,
        "b7_logical_error_improvement_credit": 0,
        "work_packet_ids": [p["packet_id"] for p in work_packets],
    }
    triage_packet["triage_hash"] = stable_hash(triage_packet)

    forbidden_claims_false = all(
        boundary_summary.get(key) is False
        for key in [
            "production_decoder_claimed",
            "threshold_claimed",
            "new_code_claimed",
            "hardware_result_claimed",
            "calibrated_device_claimed",
            "quantum_advantage_claimed",
        ]
    )

    conditions = [
        condition(
            "C1",
            "Source B7/B2 zero-credit boundary is current and valid",
            boundary.get("method") == "b7_b2_calibrated_trace_acceptance_boundary_v0"
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
            "The source trace acceptance packet remains blocked on missing submitted evidence",
            acceptance.get("method") == "b2_calibrated_trace_row_acceptance_packet_gate_v0"
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
            "The calibrated trace scope is preserved",
            boundary_summary.get("challenge_count") == 3
            and boundary_summary.get("source_trace_count") == 576
            and boundary_summary.get("holdout_profile_shots") == 864,
            {
                "challenge_count": boundary_summary.get("challenge_count"),
                "source_trace_count": boundary_summary.get("source_trace_count"),
                "holdout_profile_shots": boundary_summary.get("holdout_profile_shots"),
            },
        ),
        condition(
            "C4",
            "Three calibrated trace PR packets are ready for external agents",
            [p["packet_id"] for p in ready_packets] == ["C1", "C2", "C3"],
            {"ready_packet_ids": [p["packet_id"] for p in ready_packets]},
        ),
        condition(
            "C5",
            "B7 dependency ledger replay is correctly blocked until calibrated rows are accepted",
            [p["packet_id"] for p in blocked_packets] == ["C4"]
            and boundary_summary.get("accepted_priority_trace_rows") == 0,
            {
                "blocked_packet_ids": [p["packet_id"] for p in blocked_packets],
                "accepted_priority_trace_rows": boundary_summary.get(
                    "accepted_priority_trace_rows"
                ),
            },
        ),
        condition(
            "C6",
            "Forbidden decoder, hardware, threshold, advantage, and B7 credit claims remain false",
            forbidden_claims_false
            and boundary_summary.get("b7_dependency_credit_allowed") is False
            and boundary_summary.get("b7_ft_ledger_credit_allowed") is False
            and boundary_summary.get("b7_resource_credit_allowed") is False
            and priority_summary.get("production_decoder_claimed") is False,
            {
                "production_decoder_claimed": boundary_summary.get("production_decoder_claimed"),
                "threshold_claimed": boundary_summary.get("threshold_claimed"),
                "hardware_result_claimed": boundary_summary.get("hardware_result_claimed"),
                "calibrated_device_claimed": boundary_summary.get("calibrated_device_claimed"),
                "quantum_advantage_claimed": boundary_summary.get("quantum_advantage_claimed"),
                "b7_dependency_credit_allowed": boundary_summary.get("b7_dependency_credit_allowed"),
                "b7_ft_ledger_credit_allowed": boundary_summary.get("b7_ft_ledger_credit_allowed"),
                "b7_resource_credit_allowed": boundary_summary.get("b7_resource_credit_allowed"),
            },
        ),
    ]
    satisfied = sum(row["satisfied"] for row in conditions)
    failed_ids = [row["condition_id"] for row in conditions if not row["satisfied"]]
    validation_errors = []
    if failed_ids:
        validation_errors.append(f"calibrated trace post-boundary triage failed: {failed_ids}")
    if len(work_packets) != 4 or len(ready_packets) != 3 or len(blocked_packets) != 1:
        validation_errors.append("unexpected calibrated trace work-packet shape")

    summary = {
        "triage_id": triage_packet["triage_id"],
        "triage_hash": triage_packet["triage_hash"],
        "source_boundary_hash": boundary_summary.get("boundary_hash"),
        "source_acceptance_packet_hash": boundary_summary.get("source_acceptance_packet_hash"),
        "priority_packet_hash": acceptance_summary.get("priority_packet_hash"),
        "trace_packet_id": boundary_summary.get("trace_packet_id"),
        "work_packet_count": len(work_packets),
        "ready_external_pr_packet_count": len(ready_packets),
        "blocked_packet_count": len(blocked_packets),
        "ready_packet_ids": [p["packet_id"] for p in ready_packets],
        "blocked_packet_ids": [p["packet_id"] for p in blocked_packets],
        "condition_count": len(conditions),
        "conditions_satisfied": satisfied,
        "conditions_failed": len(conditions) - satisfied,
        "failed_condition_ids": failed_ids,
        "challenge_count": boundary_summary.get("challenge_count"),
        "source_trace_count": boundary_summary.get("source_trace_count"),
        "holdout_profile_shots": boundary_summary.get("holdout_profile_shots"),
        "accepted_priority_trace_rows": boundary_summary.get("accepted_priority_trace_rows"),
        "b7_dependency_credit_allowed": False,
        "b7_ft_ledger_credit_allowed": False,
        "b7_resource_credit_allowed": False,
        "b7_space_time_volume_reduction_credit": 0,
        "b7_logical_error_improvement_credit": 0,
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
        "source_target_id": "T-B2-010i/T-B7-012j",
        "title": "B2/B7 Calibrated Trace Post-Boundary Submission Triage",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_boundary": str(args.boundary),
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "summary": summary,
        "triage_packet": triage_packet,
        "work_packets": work_packets,
        "conditions": conditions,
        "claim_boundary": {
            "production_decoder_claimed": False,
            "threshold_claimed": False,
            "new_code_claimed": False,
            "hardware_result_claimed": False,
            "calibrated_device_claimed": False,
            "quantum_advantage_claimed": False,
            "b7_dependency_credit_allowed": False,
            "b7_ft_ledger_credit_allowed": False,
            "b7_resource_credit_allowed": False,
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
            f"The calibrated-trace post-boundary triage satisfies {s['conditions_satisfied']}/"
            f"{s['condition_count']} conditions and emits {s['work_packet_count']} PR-sized work packets."
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
            f"- Trace packet: `{s['trace_packet_id']}`",
            f"- Challenges: `{s['challenge_count']}`",
            f"- Source traces: `{s['source_trace_count']}`",
            f"- Holdout profile shots: `{s['holdout_profile_shots']}`",
            f"- Accepted priority trace rows: `{s['accepted_priority_trace_rows']}`",
            f"- B7 dependency credit allowed: `{s['b7_dependency_credit_allowed']}`",
            f"- B7 FT ledger credit allowed: `{s['b7_ft_ledger_credit_allowed']}`",
            f"- B7 resource credit allowed: `{s['b7_resource_credit_allowed']}`",
            "",
            "## Claim Boundary",
            "",
            "This is a triage result, not a QEC result. It does not claim a production decoder, threshold, hardware result, calibrated-device result, quantum advantage, B7 dependency credit, or B7 FT/resource credit.",
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
        default=Path("results/B7_B2_calibrated_trace_acceptance_boundary_v0.json"),
    )
    parser.add_argument(
        "--acceptance-packet-gate",
        type=Path,
        default=Path("results/B2_calibrated_trace_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B2_calibrated_trace_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B2_B7_calibrated_trace_post_boundary_submission_triage_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B2_B7_calibrated_trace_post_boundary_submission_triage.md"),
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
        raise SystemExit("B2/B7 calibrated trace post-boundary triage validation failed")


if __name__ == "__main__":
    main()
