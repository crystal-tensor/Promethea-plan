#!/usr/bin/env python3
"""T-B1-004cy/T-B7-012g: cone_01 resource-escape acceptance packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_resource_escape_acceptance_packet_gate_v0"
STATUS = "cone01_resource_escape_acceptance_packet_open_missing_artifact"
MODEL_STATUS = "resource_escape_acceptance_packet_required_before_b7_credit"
VERSION = "0.1"
EXPECTED_PACKET_ID = "B1-B7-cone01-resource-escape"
EXPECTED_PROVENANCE_MANIFEST_ID = "B1-B7-cone01-resource-escape-provenance-manifest"
EXPECTED_REPLAY_MANIFEST_ID = "B1-B7-cone01-resource-escape-replay-validation-manifest"
EXPECTED_ACCEPTANCE_PACKET_ID = "B1-B7-cone01-resource-escape-acceptance-packet"
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
        "priority_packet_id",
        "provenance_manifest_id",
        "replay_validation_manifest_id",
        "priority_packet_hash",
        "provenance_manifest_hash",
        "replay_validation_manifest_hash",
        "selected_line_numbers",
        "dropped_overlap_candidate_line_numbers",
        "line1381_resolution_artifact_hash",
        "line1378_recovery_artifact_hash",
        "occurrence_certificate_batch_hash",
        "full_replay_or_symbolic_equivalence_hash",
        "no_double_counting_ledger_hash",
        "resource_delta_ledger_hash",
        "b7_refreshed_ledger_hash",
        "accepted_exit_route_count",
        "accepted_occurrence_removal",
        "accepted_proxy_t_reduction",
        "b7_credit_delta",
        "line1381_off_grid_parameter_count_after",
        "source_qasm_hash",
        "candidate_qasm_or_patch_hash",
        "b7_credit_boundary",
        "claim_boundary",
        "source_evidence_files_present",
    ]
    production_required_keys = [
        "replay_validation_manifest_hash",
        "selected_line_numbers",
        "line1381_resolution_artifact_hash",
        "line1378_recovery_artifact_hash",
        "occurrence_certificate_batch_hash",
        "full_replay_or_symbolic_equivalence_hash",
        "no_double_counting_ledger_hash",
        "resource_delta_ledger_hash",
        "b7_refreshed_ledger_hash",
        "accepted_exit_route_count",
        "accepted_occurrence_removal",
        "accepted_proxy_t_reduction",
        "b7_credit_delta",
        "line1381_off_grid_parameter_count_after",
        "source_qasm_hash",
        "candidate_qasm_or_patch_hash",
        "b7_credit_boundary",
        "claim_boundary",
    ]
    required_evidence_files = [
        "accepted_replay_validation_manifest",
        "priority_resource_escape_packet",
        "provenance_manifest",
        "line1381_resolution_artifact",
        "line1378_recovery_artifact",
        "occurrence_certificate_batch",
        "full_replay_or_symbolic_equivalence_certificate",
        "no_double_counting_ledger",
        "resource_delta_ledger",
        "b7_refreshed_ledger",
        "source_qasm_hash_manifest",
        "candidate_qasm_or_patch_hash_manifest",
        "qiskit_loader_claim_boundary_seal",
        "physical_synthesis_pricing_replay",
        "b7_credit_boundary_note",
        "claim_boundary_note",
    ]

    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    manifest_bound = (
        submitted is not None
        and submitted.get("acceptance_packet_id") == EXPECTED_ACCEPTANCE_PACKET_ID
        and submitted.get("priority_packet_id") == EXPECTED_PACKET_ID
        and submitted.get("provenance_manifest_id") == EXPECTED_PROVENANCE_MANIFEST_ID
        and submitted.get("replay_validation_manifest_id") == EXPECTED_REPLAY_MANIFEST_ID
        and submitted.get("priority_packet_hash") == replay_summary.get("priority_packet_hash")
        and submitted.get("provenance_manifest_hash") == replay_summary.get("provenance_manifest_hash")
        and submitted.get("replay_validation_manifest_hash") == replay_summary.get("manifest_hash")
    )
    line1381_closed = (
        submitted is not None
        and submitted.get("line1381_off_grid_parameter_count_after") == 0
        and bool(submitted.get("line1381_resolution_artifact_hash"))
        and bool(submitted.get("full_replay_or_symbolic_equivalence_hash"))
    )
    line1378_closed = (
        submitted is not None
        and bool(submitted.get("line1378_recovery_artifact_hash"))
        and bool(submitted.get("no_double_counting_ledger_hash"))
    )
    occurrence_closed = (
        submitted is not None
        and bool(submitted.get("occurrence_certificate_batch_hash"))
        and submitted.get("accepted_occurrence_removal", 0) >= 30
        and submitted.get("accepted_proxy_t_reduction", 0) >= 600
    )
    row_acceptance_valid = (
        submitted is not None
        and submitted.get("accepted_exit_route_count", 0) > 0
        and submitted.get("b7_credit_delta", 0) >= 0
        and (line1381_closed or line1378_closed or occurrence_closed)
    )
    b7_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("b7_credit_boundary"), dict)
        and submitted["b7_credit_boundary"].get("credit_allowed_before_acceptance") is False
        and submitted["b7_credit_boundary"].get("double_counting_excluded") is True
    )
    claim_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("claim_boundary"), dict)
        and submitted["claim_boundary"].get("resource_saving_claimed") is False
        and submitted["claim_boundary"].get("b7_ledger_improvement_claimed") is False
        and submitted["claim_boundary"].get("occurrence_removal_claimed") is False
        and submitted["claim_boundary"].get("proxy_t_reduction_claimed") is False
    )
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True

    acceptance_packet = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "priority_packet_id": EXPECTED_PACKET_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "replay_validation_manifest_id": EXPECTED_REPLAY_MANIFEST_ID,
        "source_replay_validation_manifest_gate": str(args.replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "submission_artifact_path": str(submission_path),
        "priority_packet_hash": replay_summary.get("priority_packet_hash"),
        "provenance_manifest_hash": replay_summary.get("provenance_manifest_hash"),
        "replay_validation_manifest_hash": replay_summary.get("manifest_hash"),
        "selected_line_numbers": replay_summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": replay_summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "line1381_off_grid_parameter_count": replay_summary.get("line1381_off_grid_parameter_count"),
        "line1381_unpriced_proxy_t_pressure": replay_summary.get("line1381_unpriced_proxy_t_pressure"),
        "line1378_delta_recovered": replay_summary.get("line1378_delta_recovered"),
        "accepted_occurrence_removal": replay_summary.get("accepted_occurrence_removal"),
        "accepted_proxy_t_reduction": replay_summary.get("accepted_proxy_t_reduction"),
        "accepted_exit_route_count": replay_summary.get("accepted_exit_route_count"),
        "required_keys": required_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": required_evidence_files,
        "accepted_only_if": [
            "acceptance_packet_id equals B1-B7-cone01-resource-escape-acceptance-packet",
            "priority packet, provenance manifest, replay-validation manifest, and all source hashes match the source gates",
            "at least one source-backed exit route closes line1381, recovers line1378 without double counting, or supplies 30 occurrence-removing certificates",
            "full replay or symbolic equivalence evidence is hash-bound before any occurrence removal can count",
            "resource_delta_ledger and b7_refreshed_ledger_hash are present before any B7 credit delta is counted",
            "line1381_off_grid_parameter_count_after is zero for a line1381 acceptance route",
            "B7 credit boundary forbids pre-acceptance credit and excludes double counting",
            "claim_boundary forbids resource-saving, B7-ledger improvement, occurrence-removal, and proxy-T reduction claims until accepted",
        ],
    }
    acceptance_packet["packet_hash"] = stable_hash(acceptance_packet)

    requirements = [
        requirement(
            "P1",
            "Replay-validation manifest gate remains valid and blocked only on P6/P7/P8",
            replay.get("method") == "b1_b7_cone01_resource_escape_replay_validation_manifest_gate_v0"
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
            "Priority resource-escape packet remains fixed and source-shaped",
            priority.get("method") == "b1_b7_cone01_resource_escape_priority_packet_gate_v0"
            and priority_summary.get("priority_packet_id") == EXPECTED_PACKET_ID
            and priority_summary.get("validation_error_count") == 0
            and priority_summary.get("failed_priority_requirement_ids") == EXPECTED_FAILED_IDS,
            {
                "priority_packet_id": priority_summary.get("priority_packet_id"),
                "packet_hash": priority_summary.get("packet_hash"),
                "failed_priority_requirement_ids": priority_summary.get(
                    "failed_priority_requirement_ids"
                ),
            },
        ),
        requirement(
            "P3",
            "Acceptance packet carries locked B1/B7 resource-credit schema and evidence classes",
            len(required_keys) == 26
            and len(production_required_keys) == 18
            and len(required_evidence_files) == 16,
            {
                "required_key_count": len(required_keys),
                "production_required_key_count": len(production_required_keys),
                "required_evidence_file_count": len(required_evidence_files),
            },
        ),
        requirement(
            "P4",
            "Current line and resource blockers remain preserved",
            replay_summary.get("selected_line_numbers") == [268, 1381]
            and replay_summary.get("dropped_overlap_candidate_line_numbers") == [1378]
            and replay_summary.get("line1381_off_grid_parameter_count") == 5
            and replay_summary.get("line1378_delta_recovered") is False,
            {
                "selected_line_numbers": replay_summary.get("selected_line_numbers"),
                "dropped_overlap_candidate_line_numbers": replay_summary.get(
                    "dropped_overlap_candidate_line_numbers"
                ),
                "line1381_off_grid_parameter_count": replay_summary.get(
                    "line1381_off_grid_parameter_count"
                ),
                "line1378_delta_recovered": replay_summary.get("line1378_delta_recovered"),
            },
        ),
        requirement(
            "P5",
            "Current state has zero accepted escape route and zero B7 credit",
            replay_summary.get("accepted_exit_route_count") == 0
            and replay_summary.get("accepted_occurrence_removal") == 0
            and replay_summary.get("accepted_proxy_t_reduction") == 0
            and replay_summary.get("resource_saving_claimed") is False
            and replay_summary.get("b7_ledger_improvement_claimed") is False,
            {
                "accepted_exit_route_count": replay_summary.get("accepted_exit_route_count"),
                "accepted_occurrence_removal": replay_summary.get("accepted_occurrence_removal"),
                "accepted_proxy_t_reduction": replay_summary.get("accepted_proxy_t_reduction"),
                "resource_saving_claimed": replay_summary.get("resource_saving_claimed"),
                "b7_ledger_improvement_claimed": replay_summary.get(
                    "b7_ledger_improvement_claimed"
                ),
            },
        ),
        requirement(
            "P6",
            "Resource-escape acceptance packet has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted acceptance packet satisfies the locked resource-credit schema",
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
            "Submitted acceptance packet is source-backed, manifest-bound, route-valid, B7-boundary-bound, and claim-boundary-bound",
            source_backed
            and manifest_bound
            and row_acceptance_valid
            and b7_boundary_bound
            and claim_boundary_bound,
            {
                "source_backed": source_backed,
                "manifest_bound": manifest_bound,
                "route_valid": row_acceptance_valid,
                "b7_boundary_bound": b7_boundary_bound,
                "claim_boundary_bound": claim_boundary_bound,
            },
        ),
        requirement(
            "P9",
            "Forbidden resource-saving and B7-ledger claims remain false",
            replay_summary.get("resource_saving_claimed") is False
            and replay_summary.get("b7_ledger_improvement_claimed") is False,
            {
                "resource_saving_claimed": replay_summary.get("resource_saving_claimed"),
                "b7_ledger_improvement_claimed": replay_summary.get(
                    "b7_ledger_improvement_claimed"
                ),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected resource-escape acceptance packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted acceptance packet until a compiler PR supplies one")

    summary = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "priority_packet_id": EXPECTED_PACKET_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "replay_validation_manifest_id": EXPECTED_REPLAY_MANIFEST_ID,
        "priority_packet_hash": replay_summary.get("priority_packet_hash"),
        "provenance_manifest_hash": replay_summary.get("provenance_manifest_hash"),
        "replay_validation_manifest_hash": replay_summary.get("manifest_hash"),
        "acceptance_packet_hash": acceptance_packet["packet_hash"],
        "acceptance_requirement_count": len(requirements),
        "acceptance_requirements_passed": passed,
        "acceptance_requirements_failed": len(requirements) - passed,
        "failed_acceptance_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(required_evidence_files),
        "selected_line_numbers": replay_summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": replay_summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "line1381_off_grid_parameter_count": replay_summary.get("line1381_off_grid_parameter_count"),
        "line1381_unpriced_proxy_t_pressure": replay_summary.get(
            "line1381_unpriced_proxy_t_pressure"
        ),
        "line1378_delta_recovered": replay_summary.get("line1378_delta_recovered"),
        "accepted_exit_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
        "submitted_acceptance_packet_exists": submitted_exists,
        "submitted_key_count": len(submitted) if submitted else 0,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "problem_ids": [25, 21],
        "title": "B1/B7 Cone_01 Resource-Escape Acceptance Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_replay_validation_manifest_gate": str(args.replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "workload": replay.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "summary": summary,
        "resource_escape_acceptance_packet": acceptance_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The B1/B7 cone_01 resource-escape route now has an acceptance packet defining "
                "what evidence must exist before occurrence removal, proxy-T reduction, or B7 ledger "
                "credit can count."
            ),
            "what_is_not_supported": (
                "No resource-escape acceptance packet or exit route has been submitted or accepted; "
                "line 1381 still has five off-grid parameters, line 1378 remains unrecovered, and "
                "B7 credit remains zero."
            ),
            "next_gate": (
                "Submit B1-B7-cone01-resource-escape-acceptance-packet with replay manifest hash, "
                "one accepted exit route, full replay or symbolic equivalence, no-double-counting "
                "ledger, resource delta ledger, B7 refreshed ledger, B7 credit boundary, and claim boundary."
            ),
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "occurrence_removal_claimed": False,
            "proxy_t_reduction_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["resource_escape_acceptance_packet"]
    lines = [
        "# B1/B7 Cone_01 Resource-Escape Acceptance Packet Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Acceptance packet: `{summary['acceptance_packet_id']}`",
        f"- Priority packet: `{summary['priority_packet_id']}`",
        f"- Replay-validation manifest: `{summary['replay_validation_manifest_id']}`",
        f"- Replay-validation manifest hash: `{summary['replay_validation_manifest_hash']}`",
        f"- Priority packet hash: `{summary['priority_packet_hash']}`",
        f"- Acceptance packet hash: `{summary['acceptance_packet_hash']}`",
        f"- Requirements passed/failed: `{summary['acceptance_requirements_passed']}` / `{summary['acceptance_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_acceptance_requirement_ids']}`",
        f"- Required key / production key / evidence file count: `{summary['required_key_count']}` / `{summary['production_required_key_count']}` / `{summary['required_evidence_file_count']}`",
        f"- Selected lines: `{summary['selected_line_numbers']}`",
        f"- Dropped overlap line(s): `{summary['dropped_overlap_candidate_line_numbers']}`",
        f"- line1381 off-grid parameters / unpriced proxy-T pressure: `{summary['line1381_off_grid_parameter_count']}` / `{summary['line1381_unpriced_proxy_t_pressure']}`",
        f"- line1378 delta recovered: `{summary['line1378_delta_recovered']}`",
        f"- accepted exit routes / occurrence removal / proxy-T reduction: `{summary['accepted_exit_route_count']}` / `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- B7 credit delta: `{summary['b7_credit_delta']}`",
        f"- Submitted acceptance packet exists: `{summary['submitted_acceptance_packet_exists']}`",
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
            f"- resource_saving_claimed: {payload['claim_boundary']['resource_saving_claimed']}",
            f"- b7_ledger_improvement_claimed: {payload['claim_boundary']['b7_ledger_improvement_claimed']}",
            f"- occurrence_removal_claimed: {payload['claim_boundary']['occurrence_removal_claimed']}",
            f"- proxy_t_reduction_claimed: {payload['claim_boundary']['proxy_t_reduction_claimed']}",
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
        default=Path("results/B1_B7_cone01_resource_escape_replay_validation_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B1_B7_cone01_resource_escape_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B1_B7_cone01_resource_escape_acceptance_packet_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_resource_escape_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_resource_escape_acceptance_packet_gate.md"),
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
