#!/usr/bin/env python3
"""T-B3-019/T-B10-015f: full-covariance row acceptance packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b3_b10_full_covariance_row_acceptance_packet_gate_v0"
STATUS = "b3_b10_full_covariance_row_acceptance_packet_open_missing_artifact"
MODEL_STATUS = "row_acceptance_packet_required_before_full_covariance_row_credit"
VERSION = "0.1"
EXPECTED_ACCEPTANCE_PACKET_ID = "B3-R1-full-covariance-row-acceptance-packet"
EXPECTED_ROW_REPLAY_MANIFEST_ID = "B3-R1-full-covariance-row-replay-validation-manifest"
EXPECTED_DENOMINATOR_MANIFEST_ID = "B3-R1-full-covariance-denominator-replay-manifest"
EXPECTED_PROVENANCE_MANIFEST_ID = "B3-R1-full-covariance-provenance-manifest"
EXPECTED_DOWNSTREAM_PACKET_ID = "B3-R1-full-compiled-covariance"
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
    row_replay = load_json(args.row_replay_validation_manifest_gate)
    priority = load_json(args.priority_packet_gate)
    row_summary = row_replay["summary"]
    priority_summary = priority["summary"]
    submission_path = args.submission_dir / f"{EXPECTED_ACCEPTANCE_PACKET_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None

    required_keys = [
        "acceptance_packet_id",
        "provenance_manifest_id",
        "denominator_replay_manifest_id",
        "row_replay_validation_manifest_id",
        "downstream_packet_id",
        "priority_packet_hash",
        "provenance_manifest_hash",
        "denominator_manifest_hash",
        "row_replay_validation_manifest_hash",
        "row_scope_hash",
        "full_covariance_row_table_hash",
        "compiled_state_replay_hash",
        "pauli_grouping_covariance_replay_hash",
        "derivative_estimator_replay_hash",
        "selected_ci_fci_denominator_replay_hash",
        "optimizer_loop_cost_ledger_hash",
        "same_access_decision_hash",
        "b10_access_boundary_hash",
        "row_acceptance_ledger_hash",
        "negative_boundary_nonpromotion_hash",
        "accepted_full_covariance_row_count",
        "denominator_win_count",
        "optimizer_loop_total_shots_lower_bound",
        "b3_reopen_boundary",
        "b10_access_boundary",
        "claim_boundary",
        "source_evidence_files_present",
    ]
    production_required_keys = [
        "row_replay_validation_manifest_hash",
        "row_scope_hash",
        "full_covariance_row_table_hash",
        "compiled_state_replay_hash",
        "pauli_grouping_covariance_replay_hash",
        "derivative_estimator_replay_hash",
        "selected_ci_fci_denominator_replay_hash",
        "optimizer_loop_cost_ledger_hash",
        "same_access_decision_hash",
        "b10_access_boundary_hash",
        "row_acceptance_ledger_hash",
        "negative_boundary_nonpromotion_hash",
        "accepted_full_covariance_row_count",
        "denominator_win_count",
        "optimizer_loop_total_shots_lower_bound",
        "b3_reopen_boundary",
        "b10_access_boundary",
        "claim_boundary",
    ]
    evidence_files = [
        "accepted_row_replay_validation_manifest",
        "priority_reopen_packet",
        "accepted_provenance_manifest",
        "accepted_denominator_replay_manifest",
        "row_scope_manifest",
        "full_covariance_row_table",
        "compiled_state_replay_or_sampler_trace",
        "pauli_grouping_covariance_replay",
        "derivative_estimator_replay",
        "selected_ci_fci_denominator_replay",
        "optimizer_loop_cost_ledger",
        "same_access_decision_report",
        "b10_access_boundary_note",
        "row_acceptance_ledger",
        "negative_boundary_nonpromotion_note",
        "b3_reopen_boundary_note",
        "claim_boundary_note",
    ]

    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    manifest_bound = (
        submitted is not None
        and submitted.get("acceptance_packet_id") == EXPECTED_ACCEPTANCE_PACKET_ID
        and submitted.get("provenance_manifest_id") == EXPECTED_PROVENANCE_MANIFEST_ID
        and submitted.get("denominator_replay_manifest_id") == EXPECTED_DENOMINATOR_MANIFEST_ID
        and submitted.get("row_replay_validation_manifest_id") == EXPECTED_ROW_REPLAY_MANIFEST_ID
        and submitted.get("downstream_packet_id") == EXPECTED_DOWNSTREAM_PACKET_ID
        and submitted.get("priority_packet_hash") == priority_summary.get("packet_hash")
        and submitted.get("provenance_manifest_hash") == row_summary.get("provenance_manifest_hash")
        and submitted.get("denominator_manifest_hash") == row_summary.get("denominator_manifest_hash")
        and submitted.get("row_replay_validation_manifest_hash") == row_summary.get("manifest_hash")
    )
    row_acceptance_valid = (
        submitted is not None
        and submitted.get("accepted_full_covariance_row_count", 0) > 0
        and submitted.get("denominator_win_count") > 0
        and submitted.get("optimizer_loop_total_shots_lower_bound")
        == row_summary.get("max_optimizer_loop_total_shots_lower_bound")
        and bool(submitted.get("row_scope_hash"))
        and bool(submitted.get("full_covariance_row_table_hash"))
        and bool(submitted.get("compiled_state_replay_hash"))
        and bool(submitted.get("pauli_grouping_covariance_replay_hash"))
        and bool(submitted.get("derivative_estimator_replay_hash"))
        and bool(submitted.get("same_access_decision_hash"))
    )
    b3_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("b3_reopen_boundary"), dict)
        and submitted["b3_reopen_boundary"].get("b3_reopen_ready") is False
        and submitted["b3_reopen_boundary"].get("multi_parameter_converged_chemistry") is False
        and submitted["b3_reopen_boundary"].get("reaction_dynamics_solution_claimed") is False
    )
    b10_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("b10_access_boundary"), dict)
        and submitted["b10_access_boundary"].get("b10_t1_credit_allowed") is False
        and submitted["b10_access_boundary"].get("positive_same_access_route_claimed") is False
        and submitted["b10_access_boundary"].get("bqp_separation_claimed") is False
    )
    claim_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("claim_boundary"), dict)
        and submitted["claim_boundary"].get("b3_reopen_ready") is False
        and submitted["claim_boundary"].get("reaction_dynamics_solution_claimed") is False
        and submitted["claim_boundary"].get("positive_same_access_route_claimed") is False
        and submitted["claim_boundary"].get("quantum_advantage_claimed") is False
        and submitted["claim_boundary"].get("bqp_separation_claimed") is False
    )
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True

    acceptance_packet = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "denominator_replay_manifest_id": EXPECTED_DENOMINATOR_MANIFEST_ID,
        "row_replay_validation_manifest_id": EXPECTED_ROW_REPLAY_MANIFEST_ID,
        "downstream_packet_id": EXPECTED_DOWNSTREAM_PACKET_ID,
        "source_row_replay_validation_manifest_gate": str(args.row_replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "submission_artifact_path": str(submission_path),
        "priority_packet_hash": priority_summary.get("packet_hash"),
        "provenance_manifest_hash": row_summary.get("provenance_manifest_hash"),
        "denominator_manifest_hash": row_summary.get("denominator_manifest_hash"),
        "row_replay_validation_manifest_hash": row_summary.get("manifest_hash"),
        "row_aligned_instance_count": row_summary.get("row_aligned_instance_count"),
        "compiled_pilot_instance_count": row_summary.get("compiled_pilot_instance_count"),
        "selected_ci_larger_basis_denominator_beaten_count": row_summary.get(
            "selected_ci_larger_basis_denominator_beaten_count"
        ),
        "max_optimizer_loop_total_shots_lower_bound": row_summary.get(
            "max_optimizer_loop_total_shots_lower_bound"
        ),
        "accepted_priority_reopen_rows": row_summary.get("accepted_priority_reopen_rows"),
        "required_keys": required_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": evidence_files,
        "accepted_only_if": [
            "acceptance_packet_id equals B3-R1-full-covariance-row-acceptance-packet",
            "provenance, denominator replay, row replay-validation, priority packet, and downstream packet IDs and hashes match the source gates",
            "row scope, full covariance row table, compiled-state replay, Pauli grouping covariance replay, derivative estimator replay, selected-CI/FCI denominator replay, optimizer-loop cost ledger, same-access decision, and B10 access boundary are hash-bound",
            "accepted_full_covariance_row_count and denominator_win_count are positive only after source evidence exists",
            "optimizer_loop_total_shots_lower_bound preserves the locked 475,043,013,690,000-shot lower-bound pressure",
            "B3 reopen boundary keeps multi-parameter converged chemistry and reaction-dynamics solution claims false",
            "B10 access boundary keeps positive same-access route and BQP separation credit false",
            "claim_boundary forbids B3 reopen, reaction-dynamics solution, quantum advantage, and BQP separation claims until a larger audited route closes",
        ],
    }
    acceptance_packet["packet_hash"] = stable_hash(acceptance_packet)

    forbidden_claims = [
        "b3_reopen_ready",
        "positive_same_access_route_available",
        "reaction_dynamics_solution_claimed",
        "quantum_advantage_claimed",
        "bqp_separation_claimed",
    ]
    requirements = [
        requirement(
            "P1",
            "Row replay-validation manifest gate remains valid and blocked only on P6/P7/P8",
            row_replay.get("method") == "b3_b10_full_covariance_row_replay_validation_manifest_gate_v0"
            and row_summary.get("validation_error_count") == 0
            and row_summary.get("failed_manifest_requirement_ids") == EXPECTED_FAILED_IDS,
            {
                "source_status": row_replay.get("status"),
                "failed_manifest_requirement_ids": row_summary.get("failed_manifest_requirement_ids"),
                "validation_error_count": row_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Priority full-covariance packet remains fixed and source-shaped",
            priority.get("method") == "b3_b10_reopen_priority_packet_gate_v0"
            and priority_summary.get("priority_packet_id") == EXPECTED_DOWNSTREAM_PACKET_ID
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
            "Acceptance packet carries locked full-covariance row schema and evidence classes",
            len(required_keys) == 27
            and len(production_required_keys) == 18
            and len(evidence_files) == 17,
            {
                "required_key_count": len(required_keys),
                "production_required_key_count": len(production_required_keys),
                "required_evidence_file_count": len(evidence_files),
            },
        ),
        requirement(
            "P4",
            "Four-row scope and denominator negative boundary remain preserved",
            row_summary.get("row_aligned_instance_count") == 4
            and row_summary.get("compiled_pilot_instance_count") == 1
            and row_summary.get("selected_ci_larger_basis_denominator_beaten_count") == 0
            and row_summary.get("max_optimizer_loop_total_shots_lower_bound") == 475043013690000,
            {
                "row_aligned_instance_count": row_summary.get("row_aligned_instance_count"),
                "compiled_pilot_instance_count": row_summary.get("compiled_pilot_instance_count"),
                "selected_ci_larger_basis_denominator_beaten_count": row_summary.get(
                    "selected_ci_larger_basis_denominator_beaten_count"
                ),
                "max_optimizer_loop_total_shots_lower_bound": row_summary.get(
                    "max_optimizer_loop_total_shots_lower_bound"
                ),
            },
        ),
        requirement(
            "P5",
            "Current state has no accepted full-covariance rows or B10 credit",
            row_summary.get("accepted_priority_reopen_rows") == 0
            and all(row_summary.get(key) is False for key in forbidden_claims),
            {
                "accepted_priority_reopen_rows": row_summary.get("accepted_priority_reopen_rows"),
                **{key: row_summary.get(key) for key in forbidden_claims},
            },
        ),
        requirement(
            "P6",
            "Full-covariance row acceptance packet has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted acceptance packet satisfies the locked full-covariance row schema",
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
            "Submitted acceptance packet is source-backed, manifest-bound, row-valid, B3-boundary-bound, B10-boundary-bound, and claim-boundary-bound",
            source_backed
            and manifest_bound
            and row_acceptance_valid
            and b3_boundary_bound
            and b10_boundary_bound
            and claim_boundary_bound,
            {
                "source_backed": source_backed,
                "manifest_bound": manifest_bound,
                "row_acceptance_valid": row_acceptance_valid,
                "b3_boundary_bound": b3_boundary_bound,
                "b10_boundary_bound": b10_boundary_bound,
                "claim_boundary_bound": claim_boundary_bound,
            },
        ),
        requirement(
            "P9",
            "Forbidden reopen, solution, advantage, and BQP claims remain false",
            all(row_summary.get(key) is False for key in forbidden_claims),
            {key: row_summary.get(key) for key in forbidden_claims},
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    expected_failed_ids = ["P8"] if submitted_exists else EXPECTED_FAILED_IDS
    if failed_ids != expected_failed_ids:
        validation_errors.append(f"unexpected full-covariance row acceptance packet failures: {failed_ids}")

    summary = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "denominator_replay_manifest_id": EXPECTED_DENOMINATOR_MANIFEST_ID,
        "row_replay_validation_manifest_id": EXPECTED_ROW_REPLAY_MANIFEST_ID,
        "downstream_packet_id": EXPECTED_DOWNSTREAM_PACKET_ID,
        "priority_packet_hash": priority_summary.get("packet_hash"),
        "provenance_manifest_hash": row_summary.get("provenance_manifest_hash"),
        "denominator_manifest_hash": row_summary.get("denominator_manifest_hash"),
        "row_replay_validation_manifest_hash": row_summary.get("manifest_hash"),
        "acceptance_submission_hash": submitted.get("acceptance_submission_hash") if submitted else None,
        "acceptance_packet_hash": acceptance_packet["packet_hash"],
        "acceptance_requirement_count": len(requirements),
        "acceptance_requirements_passed": passed,
        "acceptance_requirements_failed": len(requirements) - passed,
        "failed_acceptance_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(evidence_files),
        "row_aligned_instance_count": row_summary.get("row_aligned_instance_count"),
        "compiled_pilot_instance_count": row_summary.get("compiled_pilot_instance_count"),
        "selected_ci_larger_basis_denominator_beaten_count": row_summary.get(
            "selected_ci_larger_basis_denominator_beaten_count"
        ),
        "max_optimizer_loop_total_shots_lower_bound": row_summary.get(
            "max_optimizer_loop_total_shots_lower_bound"
        ),
        "submitted_acceptance_packet_exists": submitted_exists,
        "submitted_key_count": len(submitted) if submitted else 0,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "accepted_full_covariance_row_count": 0,
        "accepted_priority_reopen_rows": 0,
        "denominator_win_count": 0,
        "b3_reopen_ready": False,
        "positive_same_access_route_available": False,
        "reaction_dynamics_solution_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "b10_t1_credit_allowed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B3_B10",
        "problem_ids": [49, 11],
        "title": "B3/B10 Full-Covariance Row Acceptance Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": "b3_b10_full_covariance_row_acceptance_packet_submitted_blocked_zero_credit"
        if submitted_exists
        else STATUS,
        "model_status": MODEL_STATUS,
        "source_row_replay_validation_manifest_gate": str(args.row_replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "source_target_id": "B10-T1",
        "dependency_benchmarks": ["B3", "B10"],
        "summary": summary,
        "full_covariance_row_acceptance_packet": acceptance_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The B3/B10 full-covariance reopen route now has a submitted acceptance packet "
                "bound to row replay-validation and the four-row F1 candidate bundle."
                if submitted_exists
                else "The B3/B10 full-covariance reopen route now has an acceptance packet "
                "gate after row replay-validation and before any full compiled-state "
                "covariance row, B3 reopen, or B10 credit can count."
            ),
            "what_is_not_supported": (
                "The submitted acceptance packet is still blocked on row-validity and same-access "
                "denominator conditions; no full-covariance row has been accepted, B3 remains "
                "demoted, and no reaction-dynamics solution, positive same-access route, "
                "quantum advantage, or BQP separation is supported."
                if submitted_exists
                else "No acceptance packet or full-covariance row has been submitted or "
                "accepted; B3 remains demoted and no reaction-dynamics solution, "
                "positive same-access route, quantum advantage, or BQP separation is supported."
            ),
            "next_gate": (
                "Submit B3-R1-full-covariance-row-acceptance-packet with row scope, "
                "full covariance row table, compiled-state replay, covariance replay, "
                "derivative estimator replay, denominator replay, optimizer-loop cost "
                "ledger, same-access decision, B10 access boundary, row acceptance ledger, "
                "B3 reopen boundary, and claim boundary."
            ),
            "accepted_full_covariance_row_count": 0,
            "accepted_priority_reopen_rows": 0,
            "denominator_win_count": 0,
            "b3_reopen_ready": False,
            "positive_same_access_route_claimed": False,
            "reaction_dynamics_solution_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["full_covariance_row_acceptance_packet"]
    lines = [
        "# B3/B10 Full-Covariance Row Acceptance Packet Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Acceptance packet: `{summary['acceptance_packet_id']}`",
        f"- Downstream packet: `{summary['downstream_packet_id']}`",
        f"- Row replay-validation manifest: `{summary['row_replay_validation_manifest_id']}`",
        f"- Row replay-validation hash: `{summary['row_replay_validation_manifest_hash']}`",
        f"- Acceptance packet hash: `{summary['acceptance_packet_hash']}`",
        f"- Requirements passed/failed: `{summary['acceptance_requirements_passed']}` / `{summary['acceptance_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_acceptance_requirement_ids']}`",
        f"- Required key / production key / evidence file count: `{summary['required_key_count']}` / `{summary['production_required_key_count']}` / `{summary['required_evidence_file_count']}`",
        f"- Row-aligned / compiled-pilot instances: `{summary['row_aligned_instance_count']}` / `{summary['compiled_pilot_instance_count']}`",
        f"- Denominator wins / accepted rows: `{summary['denominator_win_count']}` / `{summary['accepted_full_covariance_row_count']}`",
        f"- Max optimizer-loop lower-bound shots: `{summary['max_optimizer_loop_total_shots_lower_bound']}`",
        f"- Submitted acceptance packet exists: `{summary['submitted_acceptance_packet_exists']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Acceptance Packet",
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
            f"- accepted_full_covariance_row_count: {payload['claim_boundary']['accepted_full_covariance_row_count']}",
            f"- accepted_priority_reopen_rows: {payload['claim_boundary']['accepted_priority_reopen_rows']}",
            f"- denominator_win_count: {payload['claim_boundary']['denominator_win_count']}",
            f"- b3_reopen_ready: {payload['claim_boundary']['b3_reopen_ready']}",
            f"- positive_same_access_route_claimed: {payload['claim_boundary']['positive_same_access_route_claimed']}",
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
        lines.extend(f"- {error}" for error in payload["validation_errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--row-replay-validation-manifest-gate",
        type=Path,
        default=Path("results/B3_B10_full_covariance_row_replay_validation_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B3_B10_reopen_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B3_B10_full_covariance_row_acceptance_packet_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_B10_full_covariance_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_B10_full_covariance_row_acceptance_packet_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-03")
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
