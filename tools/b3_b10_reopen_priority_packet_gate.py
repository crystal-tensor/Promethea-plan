#!/usr/bin/env python3
"""T-B3-012a/T-B10-015a: priority B3/B10 reopen packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b3_b10_reopen_priority_packet_gate_v0"
STATUS = "b3_b10_reopen_priority_packet_open_missing_artifact"
MODEL_STATUS = "priority_full_covariance_reopen_packet_ready_no_artifact_submitted"
VERSION = "0.1"
EXPECTED_PACKET_ID = "B3-R1-full-compiled-covariance"
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
    queue = load_json(args.reopen_queue)
    summary = queue["summary"]
    packet = next(
        (row for row in queue["reopen_packets"] if row["packet_id"] == EXPECTED_PACKET_ID),
        None,
    )
    submission_path = args.submission_dir / f"{EXPECTED_PACKET_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None
    required_row_keys = [
        "packet_id",
        "row_aligned_instance_count",
        "compiled_covariance_table_hashes",
        "state_preparation_provenance_hashes",
        "grouped_observable_covariance_ledger_hash",
        "derivative_shot_floor_table_hash",
        "reference_validation_table_hash",
        "source_rescue_gate_hash",
        "source_negative_boundary_hash",
        "claim_boundary",
    ]
    missing_keys = [key for key in required_row_keys if submitted is None or key not in submitted]
    source_backed = (
        submitted is not None
        and submitted.get("source_evidence_files_present") is True
        and not missing_keys
        and submitted.get("row_aligned_instance_count") == summary["row_aligned_instance_count"]
    )

    priority_packet = {
        "packet_id": EXPECTED_PACKET_ID,
        "blocks_gate": packet["blocks_gate"] if packet else None,
        "owner_role": packet["owner_role"] if packet else None,
        "downstream_gate": packet["downstream_gate"] if packet else None,
        "acceptance_rule": packet["acceptance_rule"] if packet else None,
        "submission_artifact_path": str(submission_path),
        "required_row_keys": required_row_keys,
        "required_evidence_files": [
            "compiled_state_covariance_tables",
            "state_preparation_circuit_provenance",
            "grouped_observable_variance_covariance_ledger",
            "derivative_level_shot_floor_table",
            "sampled_vs_reference_covariance_validation",
            "source_rescue_gate_manifest",
            "source_negative_boundary_manifest",
            "claim_boundary_note",
        ],
        "accepted_only_if": [
            "all four row-aligned B3 reaction-coordinate rows have compiled-state covariance tables",
            "state-preparation circuit provenance exists for every row",
            "grouped observable covariance and derivative shot-floor ledgers are replayable",
            "sampled covariance validation rows compare against exact or high-confidence references",
            "source rescue and negative-boundary artifacts are hash-bound",
            "claim_boundary forbids B3 reopen, reaction solution, quantum advantage, and BQP separation claims",
        ],
    }
    priority_packet["packet_hash"] = stable_hash(priority_packet)

    requirements = [
        requirement(
            "P1",
            "Reopen queue remains valid and aligned to M5-M9 blockers",
            queue.get("method") == "b3_b10_reopen_blocker_queue_gate_v0"
            and summary.get("failed_source_gate_ids") == ["M5", "M6", "M7", "M8", "M9"]
            and summary.get("failed_requirement_count") == 0,
            {
                "source_status": queue.get("status"),
                "failed_source_gate_ids": summary.get("failed_source_gate_ids"),
                "failed_requirement_count": summary.get("failed_requirement_count"),
            },
        ),
        requirement(
            "P2",
            "Priority packet is fixed to full compiled-state covariance",
            packet is not None
            and packet["packet_id"] == EXPECTED_PACKET_ID
            and packet["blocks_gate"] == "M5",
            {
                "expected_packet_id": EXPECTED_PACKET_ID,
                "actual_packet_id": packet["packet_id"] if packet else None,
                "blocks_gate": packet["blocks_gate"] if packet else None,
            },
        ),
        requirement(
            "P3",
            "Packet preserves the four-row B3 reaction-coordinate scope",
            summary.get("row_aligned_instance_count") == 4
            and summary.get("compiled_pilot_instance_count") == 1
            and summary.get("full_compiled_state_covariance_computed") is False,
            {
                "row_aligned_instance_count": summary.get("row_aligned_instance_count"),
                "compiled_pilot_instance_count": summary.get("compiled_pilot_instance_count"),
                "full_compiled_state_covariance_computed": summary.get(
                    "full_compiled_state_covariance_computed"
                ),
            },
        ),
        requirement(
            "P4",
            "Packet binds required evidence file classes",
            len(priority_packet["required_evidence_files"]) == 8,
            {"required_evidence_files": priority_packet["required_evidence_files"]},
        ),
        requirement(
            "P5",
            "Current B3/B10 route stays demoted before submission",
            summary.get("b3_reopen_ready") is False
            and summary.get("positive_same_access_route_available") is False
            and summary.get("b10_sampling_access_bridge_refuted_for_current_evidence") is True,
            {
                "b3_reopen_ready": summary.get("b3_reopen_ready"),
                "positive_same_access_route_available": summary.get(
                    "positive_same_access_route_available"
                ),
                "b10_sampling_access_bridge_refuted_for_current_evidence": summary.get(
                    "b10_sampling_access_bridge_refuted_for_current_evidence"
                ),
            },
        ),
        requirement(
            "P6",
            "Priority reopen artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted artifact satisfies the locked full-covariance schema",
            submitted_exists and not missing_keys,
            {"missing_keys": missing_keys, "submitted_key_count": len(submitted) if submitted else 0},
        ),
        requirement(
            "P8",
            "Submitted artifact is source-backed and covers all four rows",
            source_backed,
            {
                "source_evidence_files_present": submitted.get("source_evidence_files_present")
                if submitted
                else False,
                "row_aligned_instance_count": submitted.get("row_aligned_instance_count")
                if submitted
                else None,
            },
        ),
        requirement(
            "P9",
            "Forbidden reopen, solution, advantage, and BQP claims remain false",
            all(
                queue["claim_boundary"].get(key) is False
                for key in [
                    "b3_reopen_ready",
                    "positive_same_access_route_claimed",
                    "reaction_dynamics_solution_claimed",
                    "quantum_advantage_claimed",
                    "bqp_separation_claimed",
                ]
            ),
            {
                "b3_reopen_ready": queue["claim_boundary"].get("b3_reopen_ready"),
                "positive_same_access_route_claimed": queue["claim_boundary"].get(
                    "positive_same_access_route_claimed"
                ),
                "reaction_dynamics_solution_claimed": queue["claim_boundary"].get(
                    "reaction_dynamics_solution_claimed"
                ),
                "quantum_advantage_claimed": queue["claim_boundary"].get("quantum_advantage_claimed"),
                "bqp_separation_claimed": queue["claim_boundary"].get("bqp_separation_claimed"),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected priority reopen packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted artifact until a chemistry PR supplies one")

    payload_summary = {
        "priority_packet_id": EXPECTED_PACKET_ID,
        "packet_hash": priority_packet["packet_hash"],
        "priority_requirement_count": len(requirements),
        "priority_requirements_passed": passed,
        "priority_requirements_failed": len(requirements) - passed,
        "failed_priority_requirement_ids": failed_ids,
        "required_row_key_count": len(required_row_keys),
        "required_evidence_file_count": len(priority_packet["required_evidence_files"]),
        "row_aligned_instance_count": summary.get("row_aligned_instance_count"),
        "compiled_pilot_instance_count": summary.get("compiled_pilot_instance_count"),
        "full_compiled_state_covariance_computed": summary.get(
            "full_compiled_state_covariance_computed"
        ),
        "submitted_artifact_exists": submitted_exists,
        "missing_key_count": len(missing_keys),
        "accepted_priority_reopen_rows": 0,
        "b3_reopen_ready": False,
        "positive_same_access_route_available": False,
        "reaction_dynamics_solution_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B3_B10",
        "problem_ids": [49, 11],
        "title": "B3/B10 Reopen Priority Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_reopen_queue_result": str(args.reopen_queue),
        "source_target_id": "B10-T1",
        "dependency_benchmarks": ["B3", "B10"],
        "summary": payload_summary,
        "priority_reopen_packet": priority_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The first B3/B10 reopen blocker now has a concrete source-backed "
                "submission packet for full compiled-state covariance evidence."
            ),
            "what_is_not_supported": (
                "No full-covariance artifact has been submitted or accepted; B3 remains demoted "
                "and no reaction-dynamics solution, quantum advantage, or BQP separation is supported."
            ),
            "next_gate": (
                f"Submit {submission_path} with all required full-covariance rows, state-prep "
                "provenance, covariance ledgers, derivative shot floors, and validation hashes."
            ),
            "b3_reopen_ready": False,
            "positive_same_access_route_claimed": False,
            "reaction_dynamics_solution_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["priority_reopen_packet"]
    lines = [
        "# B3/B10 Reopen Priority Packet Gate",
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
        f"- Required row keys: {summary['required_row_key_count']}",
        f"- Required evidence file classes: {summary['required_evidence_file_count']}",
        f"- Row-aligned / compiled-pilot instances: {summary['row_aligned_instance_count']} / {summary['compiled_pilot_instance_count']}",
        f"- Full compiled-state covariance computed: {summary['full_compiled_state_covariance_computed']}",
        f"- Submitted artifact exists: {summary['submitted_artifact_exists']}",
        f"- Accepted priority reopen rows: {summary['accepted_priority_reopen_rows']}",
        "",
        "## Submission Packet",
        "",
        f"- Submission path: `{packet['submission_artifact_path']}`",
        f"- Blocks gate: `{packet['blocks_gate']}`",
        f"- Owner role: `{packet['owner_role']}`",
        f"- Downstream gate: `{packet['downstream_gate']}`",
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
            f"- b3_reopen_ready: {payload['claim_boundary']['b3_reopen_ready']}",
            f"- reaction_dynamics_solution_claimed: {payload['claim_boundary']['reaction_dynamics_solution_claimed']}",
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
        "--reopen-queue",
        type=Path,
        default=Path("results/B3_B10_reopen_blocker_queue_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B3_B10_reopen_priority_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_B10_reopen_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_B10_reopen_priority_packet_gate.md"),
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
