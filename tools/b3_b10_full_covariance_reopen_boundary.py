#!/usr/bin/env python3
"""T-B3-020/T-B10-015g: B3 reopen view of the full-covariance row gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b3_b10_full_covariance_reopen_boundary_v0"
STATUS = "b3_b10_full_covariance_reopen_boundary_synced"
MODEL_STATUS = "b3_zero_credit_reopen_boundary_after_full_covariance_row_acceptance_gate"
VERSION = "0.1"
EXPECTED_METHOD = "b3_b10_full_covariance_row_acceptance_packet_gate_v0"
EXPECTED_ACCEPTANCE_PACKET_ID = "B3-R1-full-covariance-row-acceptance-packet"
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
    source = load_json(args.acceptance_packet_gate)
    summary = source["summary"]

    boundary_packet = {
        "boundary_id": "B3-B10-full-covariance-reopen-boundary",
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "source_method": source.get("method"),
        "acceptance_packet_id": summary.get("acceptance_packet_id"),
        "acceptance_packet_hash": summary.get("acceptance_packet_hash"),
        "downstream_packet_id": summary.get("downstream_packet_id"),
        "row_replay_validation_manifest_id": summary.get("row_replay_validation_manifest_id"),
        "row_replay_validation_manifest_hash": summary.get(
            "row_replay_validation_manifest_hash"
        ),
        "row_aligned_instance_count": summary.get("row_aligned_instance_count"),
        "compiled_pilot_instance_count": summary.get("compiled_pilot_instance_count"),
        "accepted_full_covariance_row_count": summary.get("accepted_full_covariance_row_count"),
        "accepted_priority_reopen_rows": summary.get("accepted_priority_reopen_rows"),
        "selected_ci_larger_basis_denominator_beaten_count": summary.get(
            "selected_ci_larger_basis_denominator_beaten_count"
        ),
        "denominator_win_count": summary.get("denominator_win_count"),
        "max_optimizer_loop_total_shots_lower_bound": summary.get(
            "max_optimizer_loop_total_shots_lower_bound"
        ),
        "source_b3_reopen_ready": summary.get("b3_reopen_ready"),
        "source_positive_same_access_route_available": summary.get(
            "positive_same_access_route_available"
        ),
        "source_b10_t1_credit_allowed": summary.get("b10_t1_credit_allowed"),
        "b3_reopen_ready": False,
        "b3_full_covariance_credit_allowed": False,
        "b3_reaction_dynamics_solution_credit_allowed": False,
        "b10_t1_credit_allowed": False,
        "positive_same_access_route_allowed": False,
        "required_downstream_before_b3_reopen": [
            "submitted B3-R1-full-covariance-row-acceptance-packet",
            "accepted full compiled-state covariance row table for all 4 row-aligned instances",
            "compiled-state replay and covariance replay for multi-parameter/converged chemistry states",
            "derivative estimator replay and optimizer-loop cost ledger beating the current lower-bound pressure",
            "same-access denominator win ledger with denominator_win_count > 0",
            "B10 access-boundary replay accepting the positive route without oracle or data-loading leakage",
            "B3 reopen boundary that preserves claim discipline until rows are accepted",
            "claim boundary forbidding reaction-dynamics solution, quantum advantage, and BQP separation before acceptance",
        ],
    }
    boundary_packet["boundary_hash"] = stable_hash(boundary_packet)

    no_forbidden_claims = all(
        summary.get(key) is False
        for key in [
            "reaction_dynamics_solution_claimed",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
            "positive_same_access_route_available",
            "b10_t1_credit_allowed",
            "b3_reopen_ready",
        ]
    )

    requirements = [
        requirement(
            "S1",
            "Source B3/B10 full-covariance row acceptance packet gate is present and current",
            source.get("method") == EXPECTED_METHOD
            and summary.get("acceptance_packet_id") == EXPECTED_ACCEPTANCE_PACKET_ID
            and summary.get("downstream_packet_id") == EXPECTED_DOWNSTREAM_PACKET_ID
            and summary.get("validation_error_count") == 0,
            {
                "source_method": source.get("method"),
                "acceptance_packet_id": summary.get("acceptance_packet_id"),
                "downstream_packet_id": summary.get("downstream_packet_id"),
                "validation_error_count": summary.get("validation_error_count"),
            },
        ),
        requirement(
            "S2",
            "Source acceptance gate remains blocked on missing submitted packet evidence",
            summary.get("failed_acceptance_requirement_ids") == EXPECTED_FAILED_IDS
            and summary.get("submitted_acceptance_packet_exists") is False,
            {
                "failed_acceptance_requirement_ids": summary.get(
                    "failed_acceptance_requirement_ids"
                ),
                "submitted_acceptance_packet_exists": summary.get(
                    "submitted_acceptance_packet_exists"
                ),
            },
        ),
        requirement(
            "S3",
            "B3 full-covariance row scope and current denominator pressure are preserved",
            summary.get("row_aligned_instance_count") == 4
            and summary.get("compiled_pilot_instance_count") == 1
            and summary.get("max_optimizer_loop_total_shots_lower_bound") == 475043013690000,
            {
                "row_aligned_instance_count": summary.get("row_aligned_instance_count"),
                "compiled_pilot_instance_count": summary.get("compiled_pilot_instance_count"),
                "max_optimizer_loop_total_shots_lower_bound": summary.get(
                    "max_optimizer_loop_total_shots_lower_bound"
                ),
            },
        ),
        requirement(
            "S4",
            "No full-covariance row, reopen row, or denominator win has been accepted",
            summary.get("accepted_full_covariance_row_count") == 0
            and summary.get("accepted_priority_reopen_rows") == 0
            and summary.get("denominator_win_count") == 0
            and summary.get("selected_ci_larger_basis_denominator_beaten_count") == 0,
            {
                "accepted_full_covariance_row_count": summary.get(
                    "accepted_full_covariance_row_count"
                ),
                "accepted_priority_reopen_rows": summary.get("accepted_priority_reopen_rows"),
                "denominator_win_count": summary.get("denominator_win_count"),
                "selected_ci_larger_basis_denominator_beaten_count": summary.get(
                    "selected_ci_larger_basis_denominator_beaten_count"
                ),
            },
        ),
        requirement(
            "S5",
            "B3 reopen, B3 credit, B10-T1 credit, and positive same-access route remain disabled",
            boundary_packet["b3_reopen_ready"] is False
            and boundary_packet["b3_full_covariance_credit_allowed"] is False
            and boundary_packet["b3_reaction_dynamics_solution_credit_allowed"] is False
            and boundary_packet["b10_t1_credit_allowed"] is False
            and boundary_packet["positive_same_access_route_allowed"] is False,
            {
                "b3_reopen_ready": boundary_packet["b3_reopen_ready"],
                "b3_full_covariance_credit_allowed": boundary_packet[
                    "b3_full_covariance_credit_allowed"
                ],
                "b3_reaction_dynamics_solution_credit_allowed": boundary_packet[
                    "b3_reaction_dynamics_solution_credit_allowed"
                ],
                "b10_t1_credit_allowed": boundary_packet["b10_t1_credit_allowed"],
                "positive_same_access_route_allowed": boundary_packet[
                    "positive_same_access_route_allowed"
                ],
            },
        ),
        requirement(
            "S6",
            "Forbidden solution, advantage, BQP, and positive-route claims remain absent",
            no_forbidden_claims,
            {
                "reaction_dynamics_solution_claimed": summary.get(
                    "reaction_dynamics_solution_claimed"
                ),
                "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": summary.get("bqp_separation_claimed"),
                "positive_same_access_route_available": summary.get(
                    "positive_same_access_route_available"
                ),
                "b10_t1_credit_allowed": summary.get("b10_t1_credit_allowed"),
                "b3_reopen_ready": summary.get("b3_reopen_ready"),
            },
        ),
        requirement(
            "S7",
            "Boundary records downstream evidence required before B3 can reopen",
            len(boundary_packet["required_downstream_before_b3_reopen"]) == 8,
            {
                "required_downstream_before_b3_reopen": boundary_packet[
                    "required_downstream_before_b3_reopen"
                ]
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors = []
    if failed_ids:
        validation_errors.append(f"B3/B10 full-covariance reopen boundary failed: {failed_ids}")

    payload_summary = {
        "boundary_id": boundary_packet["boundary_id"],
        "boundary_hash": boundary_packet["boundary_hash"],
        "source_acceptance_packet_hash": summary.get("acceptance_packet_hash"),
        "acceptance_packet_id": summary.get("acceptance_packet_id"),
        "downstream_packet_id": summary.get("downstream_packet_id"),
        "row_replay_validation_manifest_id": summary.get("row_replay_validation_manifest_id"),
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "source_failed_acceptance_requirement_ids": summary.get(
            "failed_acceptance_requirement_ids"
        ),
        "submitted_acceptance_packet_exists": summary.get("submitted_acceptance_packet_exists"),
        "row_aligned_instance_count": summary.get("row_aligned_instance_count"),
        "compiled_pilot_instance_count": summary.get("compiled_pilot_instance_count"),
        "accepted_full_covariance_row_count": summary.get("accepted_full_covariance_row_count"),
        "accepted_priority_reopen_rows": summary.get("accepted_priority_reopen_rows"),
        "denominator_win_count": summary.get("denominator_win_count"),
        "selected_ci_larger_basis_denominator_beaten_count": summary.get(
            "selected_ci_larger_basis_denominator_beaten_count"
        ),
        "max_optimizer_loop_total_shots_lower_bound": summary.get(
            "max_optimizer_loop_total_shots_lower_bound"
        ),
        "b3_reopen_ready": False,
        "b3_full_covariance_credit_allowed": False,
        "b3_reaction_dynamics_solution_credit_allowed": False,
        "b10_t1_credit_allowed": False,
        "positive_same_access_route_allowed": False,
        "reaction_dynamics_solution_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B3",
        "linked_benchmark_id": "B10",
        "source_target_id": "T-B3-020/T-B10-015g",
        "title": "B3/B10 Full-Covariance Reopen Boundary",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "summary": payload_summary,
        "boundary_packet": boundary_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "B3 is explicitly synchronized to the B3/B10 full-covariance row acceptance "
                "packet as a zero-credit reopen boundary."
            ),
            "what_is_not_supported": (
                "No accepted full-covariance row, B3 reopen, reaction-dynamics solution, "
                "positive same-access route, quantum advantage, BQP separation, or B10-T1 "
                "credit is supported."
            ),
            "next_gate": (
                "Submit and accept the full-covariance row acceptance packet with four "
                "source-backed full-covariance rows, compiled-state and covariance replay, "
                "optimizer-loop cost replay, same-access denominator wins, B10 access-boundary "
                "acceptance, and claim boundary before B3 can reopen."
            ),
            "b3_reopen_ready": False,
            "b3_full_covariance_credit_allowed": False,
            "positive_same_access_route_allowed": False,
            "b10_t1_credit_allowed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["boundary_packet"]
    lines = [
        "# B3/B10 Full-Covariance Reopen Boundary",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Boundary: `{summary['boundary_id']}`",
        f"- Boundary hash: `{summary['boundary_hash']}`",
        f"- Source acceptance packet: `{summary['acceptance_packet_id']}`",
        f"- Source acceptance packet hash: `{summary['source_acceptance_packet_hash']}`",
        f"- Downstream packet: `{summary['downstream_packet_id']}`",
        f"- Row replay-validation manifest: `{summary['row_replay_validation_manifest_id']}`",
        f"- Requirements passed/failed: `{summary['requirements_passed']}` / `{summary['requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_requirement_ids']}`",
        f"- Source failed acceptance IDs: `{summary['source_failed_acceptance_requirement_ids']}`",
        f"- Row-aligned / compiled-pilot instances: `{summary['row_aligned_instance_count']}` / `{summary['compiled_pilot_instance_count']}`",
        f"- Accepted full-covariance rows / priority reopen rows: `{summary['accepted_full_covariance_row_count']}` / `{summary['accepted_priority_reopen_rows']}`",
        f"- Denominator wins / selected-CI larger-basis wins: `{summary['denominator_win_count']}` / `{summary['selected_ci_larger_basis_denominator_beaten_count']}`",
        f"- Optimizer-loop lower-bound shots: `{summary['max_optimizer_loop_total_shots_lower_bound']}`",
        f"- B3 reopen / B3 credit / B10-T1 credit / positive route allowed: `{summary['b3_reopen_ready']}` / `{summary['b3_full_covariance_credit_allowed']}` / `{summary['b10_t1_credit_allowed']}` / `{summary['positive_same_access_route_allowed']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Required Downstream Evidence Before B3 Reopen",
        "",
    ]
    for item in packet["required_downstream_before_b3_reopen"]:
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
            f"- b3_reopen_ready: {payload['claim_boundary']['b3_reopen_ready']}",
            f"- b3_full_covariance_credit_allowed: {payload['claim_boundary']['b3_full_covariance_credit_allowed']}",
            f"- positive_same_access_route_allowed: {payload['claim_boundary']['positive_same_access_route_allowed']}",
            f"- b10_t1_credit_allowed: {payload['claim_boundary']['b10_t1_credit_allowed']}",
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
        "--acceptance-packet-gate",
        type=Path,
        default=Path("results/B3_B10_full_covariance_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_B10_full_covariance_reopen_boundary_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_B10_full_covariance_reopen_boundary.md"),
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
