#!/usr/bin/env python3
"""T-B10-017: B10-T1 zero-credit boundary over B3/B5 positive-route gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b10_t1_positive_route_acceptance_boundary_v0"
STATUS = "b10_t1_positive_route_acceptance_boundary_synced"
MODEL_STATUS = "b10_t1_zero_credit_boundary_after_b3_b5_acceptance_packet_gates"
VERSION = "0.1"
B3_METHOD = "b3_b10_full_covariance_row_acceptance_packet_gate_v0"
B3_ACCEPTANCE_PACKET_ID = "B3-R1-full-covariance-row-acceptance-packet"
B5_METHOD = "b5_b10_w1_priority_row_acceptance_packet_gate_v0"
B5_ACCEPTANCE_PACKET_ID = "B5B10-W1-priority-row-acceptance-packet"
EXPECTED_FAILED_IDS = ["P6", "P7", "P8"]
EXPECTED_B3_SUBMITTED_FAILED_IDS = ["P8"]


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
    b3 = load_json(args.b3_acceptance_packet_gate)
    b5 = load_json(args.b5_acceptance_packet_gate)
    b3s = b3["summary"]
    b5s = b5["summary"]

    boundary_packet = {
        "boundary_id": "B10-T1-positive-route-acceptance-boundary",
        "source_b3_acceptance_packet_gate": str(args.b3_acceptance_packet_gate),
        "source_b5_acceptance_packet_gate": str(args.b5_acceptance_packet_gate),
        "b3_source_method": b3.get("method"),
        "b5_source_method": b5.get("method"),
        "b3_acceptance_packet_id": b3s.get("acceptance_packet_id"),
        "b3_acceptance_packet_hash": b3s.get("acceptance_packet_hash"),
        "b5_acceptance_packet_id": b5s.get("acceptance_packet_id"),
        "b5_acceptance_packet_hash": b5s.get("acceptance_packet_hash"),
        "b3_row_aligned_instance_count": b3s.get("row_aligned_instance_count"),
        "b3_compiled_pilot_instance_count": b3s.get("compiled_pilot_instance_count"),
        "b3_denominator_win_count": b3s.get("denominator_win_count"),
        "b3_optimizer_loop_shot_lower_bound": b3s.get("max_optimizer_loop_total_shots_lower_bound"),
        "b3_accepted_full_covariance_rows": b3s.get("accepted_full_covariance_row_count"),
        "b5_row_contract_count": b5s.get("row_contract_count"),
        "b5_priority_row_id": b5s.get("priority_row_id"),
        "b5_accepted_priority_rows": b5s.get("accepted_priority_row_count"),
        "b5_production_contract_rows_accepted": b5s.get("production_contract_rows_accepted"),
        "b10_t1_credit_allowed": False,
        "b10_positive_route_ready": False,
        "b10_bqp_separation_credit_allowed": False,
        "b10_quantum_advantage_credit_allowed": False,
        "required_downstream_before_b10_t1_credit": [
            "accepted B3-R1-full-covariance-row-acceptance-packet or accepted B5B10-W1-priority-row-acceptance-packet",
            "nonzero accepted B3 full-covariance row count or nonzero accepted B5 production row count",
            "B3 full-covariance denominator win or B5 production DMRG denominator win under the locked same-access row contract",
            "optimizer-loop and same-access cost ledger showing a positive route after denominator costs",
            "B10 access-boundary note replacing zero-credit status with a positive-route ledger",
            "claim boundary that still forbids reaction-dynamics, production-DMRG, same-access, quantum-advantage, and BQP-separation claims until evidence is source-backed",
        ],
    }
    boundary_packet["boundary_hash"] = stable_hash(boundary_packet)

    requirements = [
        requirement(
            "S1",
            "B3 full-covariance row acceptance packet gate is present and current",
            b3.get("method") == B3_METHOD
            and b3s.get("acceptance_packet_id") == B3_ACCEPTANCE_PACKET_ID
            and b3s.get("validation_error_count") == 0,
            {
                "source_method": b3.get("method"),
                "acceptance_packet_id": b3s.get("acceptance_packet_id"),
                "validation_error_count": b3s.get("validation_error_count"),
            },
        ),
        requirement(
            "S2",
            "B5 W1 priority-row acceptance packet gate is present and current",
            b5.get("method") == B5_METHOD
            and b5s.get("acceptance_packet_id") == B5_ACCEPTANCE_PACKET_ID
            and b5s.get("validation_error_count") == 0,
            {
                "source_method": b5.get("method"),
                "acceptance_packet_id": b5s.get("acceptance_packet_id"),
                "validation_error_count": b5s.get("validation_error_count"),
            },
        ),
        requirement(
            "S3",
            "Both source gates remain blocked before positive-route credit",
            b3s.get("failed_acceptance_requirement_ids") == EXPECTED_B3_SUBMITTED_FAILED_IDS
            and b5s.get("failed_acceptance_requirement_ids") == EXPECTED_FAILED_IDS
            and b3s.get("submitted_acceptance_packet_exists") is True
            and b5s.get("submitted_acceptance_packet_exists") is False,
            {
                "b3_failed_acceptance_requirement_ids": b3s.get("failed_acceptance_requirement_ids"),
                "b5_failed_acceptance_requirement_ids": b5s.get("failed_acceptance_requirement_ids"),
                "b3_submitted_acceptance_packet_exists": b3s.get("submitted_acceptance_packet_exists"),
                "b5_submitted_acceptance_packet_exists": b5s.get("submitted_acceptance_packet_exists"),
                "b3_denominator_win_count": b3s.get("denominator_win_count"),
                "b3_accepted_full_covariance_row_count": b3s.get(
                    "accepted_full_covariance_row_count"
                ),
            },
        ),
        requirement(
            "S4",
            "B3 full-covariance route remains demoted with no denominator win",
            b3s.get("row_aligned_instance_count") == 4
            and b3s.get("compiled_pilot_instance_count") == 1
            and b3s.get("denominator_win_count") == 0
            and b3s.get("accepted_full_covariance_row_count") == 0
            and b3s.get("b3_reopen_ready") is False
            and b3s.get("b10_t1_credit_allowed") is False,
            {
                "row_aligned_instance_count": b3s.get("row_aligned_instance_count"),
                "compiled_pilot_instance_count": b3s.get("compiled_pilot_instance_count"),
                "denominator_win_count": b3s.get("denominator_win_count"),
                "accepted_full_covariance_row_count": b3s.get("accepted_full_covariance_row_count"),
                "b3_reopen_ready": b3s.get("b3_reopen_ready"),
                "b10_t1_credit_allowed": b3s.get("b10_t1_credit_allowed"),
            },
        ),
        requirement(
            "S5",
            "B5 W1 route remains zero-row with no production-DMRG positive route",
            b5s.get("row_contract_count") == 9
            and b5s.get("accepted_priority_row_count") == 0
            and b5s.get("production_contract_rows_accepted") == 0
            and b5s.get("b10_t1_positive_route_ready") is False
            and b5s.get("production_dmrg_claimed") is False,
            {
                "row_contract_count": b5s.get("row_contract_count"),
                "accepted_priority_row_count": b5s.get("accepted_priority_row_count"),
                "production_contract_rows_accepted": b5s.get("production_contract_rows_accepted"),
                "b10_t1_positive_route_ready": b5s.get("b10_t1_positive_route_ready"),
                "production_dmrg_claimed": b5s.get("production_dmrg_claimed"),
            },
        ),
        requirement(
            "S6",
            "Forbidden B10-T1 quantum advantage and BQP claims remain absent across both routes",
            b3s.get("quantum_advantage_claimed") is False
            and b3s.get("bqp_separation_claimed") is False
            and b5s.get("quantum_advantage_claimed") is False
            and b5s.get("bqp_separation_claimed") is False
            and b3s.get("positive_same_access_route_available") is False
            and b5s.get("same_access_positive_route_claimed") is False,
            {
                "b3_quantum_advantage_claimed": b3s.get("quantum_advantage_claimed"),
                "b3_bqp_separation_claimed": b3s.get("bqp_separation_claimed"),
                "b3_positive_same_access_route_available": b3s.get("positive_same_access_route_available"),
                "b5_quantum_advantage_claimed": b5s.get("quantum_advantage_claimed"),
                "b5_bqp_separation_claimed": b5s.get("bqp_separation_claimed"),
                "b5_same_access_positive_route_claimed": b5s.get("same_access_positive_route_claimed"),
            },
        ),
        requirement(
            "S7",
            "B10-T1 unified positive-route credit remains explicitly disabled",
            boundary_packet["b10_t1_credit_allowed"] is False
            and boundary_packet["b10_positive_route_ready"] is False
            and boundary_packet["b10_bqp_separation_credit_allowed"] is False
            and boundary_packet["b10_quantum_advantage_credit_allowed"] is False,
            {
                "b10_t1_credit_allowed": boundary_packet["b10_t1_credit_allowed"],
                "b10_positive_route_ready": boundary_packet["b10_positive_route_ready"],
                "b10_bqp_separation_credit_allowed": boundary_packet["b10_bqp_separation_credit_allowed"],
                "b10_quantum_advantage_credit_allowed": boundary_packet[
                    "b10_quantum_advantage_credit_allowed"
                ],
            },
        ),
        requirement(
            "S8",
            "Boundary packet records downstream evidence required before B10-T1 credit",
            len(boundary_packet["required_downstream_before_b10_t1_credit"]) == 6,
            {
                "required_downstream_before_b10_t1_credit": boundary_packet[
                    "required_downstream_before_b10_t1_credit"
                ]
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors = []
    if failed_ids:
        validation_errors.append(f"B10-T1 positive-route acceptance boundary failed: {failed_ids}")

    payload_summary = {
        "boundary_id": boundary_packet["boundary_id"],
        "boundary_hash": boundary_packet["boundary_hash"],
        "b3_acceptance_packet_id": b3s.get("acceptance_packet_id"),
        "b3_acceptance_packet_hash": b3s.get("acceptance_packet_hash"),
        "b5_acceptance_packet_id": b5s.get("acceptance_packet_id"),
        "b5_acceptance_packet_hash": b5s.get("acceptance_packet_hash"),
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "b3_failed_acceptance_requirement_ids": b3s.get("failed_acceptance_requirement_ids"),
        "b5_failed_acceptance_requirement_ids": b5s.get("failed_acceptance_requirement_ids"),
        "b3_submitted_acceptance_packet_exists": b3s.get("submitted_acceptance_packet_exists"),
        "b5_submitted_acceptance_packet_exists": b5s.get("submitted_acceptance_packet_exists"),
        "b3_accepted_full_covariance_row_count": b3s.get("accepted_full_covariance_row_count"),
        "b3_denominator_win_count": b3s.get("denominator_win_count"),
        "b3_optimizer_loop_shot_lower_bound": b3s.get("max_optimizer_loop_total_shots_lower_bound"),
        "b5_accepted_priority_row_count": b5s.get("accepted_priority_row_count"),
        "b5_production_contract_rows_accepted": b5s.get("production_contract_rows_accepted"),
        "b10_t1_credit_allowed": False,
        "b10_positive_route_ready": False,
        "b10_bqp_separation_credit_allowed": False,
        "b10_quantum_advantage_credit_allowed": False,
        "production_dmrg_claimed": False,
        "same_access_positive_route_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B10",
        "linked_benchmark_id": "B3_B5",
        "source_target_id": "B10-T1",
        "title": "B10-T1 Positive-Route Acceptance Boundary",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_b3_acceptance_packet_gate": str(args.b3_acceptance_packet_gate),
        "source_b5_acceptance_packet_gate": str(args.b5_acceptance_packet_gate),
        "summary": payload_summary,
        "boundary_packet": boundary_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "B10-T1 is now explicitly synchronized to the B3 full-covariance "
                "and B5 W1 priority-row acceptance packet gates as a unified positive-route "
                "zero-credit boundary."
            ),
            "what_is_not_supported": (
                "No accepted B3 full-covariance row, B5 production row, production DMRG "
                "denominator, same-access positive route, quantum advantage, or BQP "
                "separation is supported."
            ),
            "next_gate": (
                "Submit and accept either the B3 full-covariance row acceptance packet "
                "or the B5 W1 priority-row acceptance packet, then produce a source-backed "
                "denominator win and same-access cost ledger before B10-T1 can leave zero-credit status."
            ),
            "b10_t1_credit_allowed": False,
            "b10_positive_route_ready": False,
            "b10_bqp_separation_credit_allowed": False,
            "b10_quantum_advantage_credit_allowed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["boundary_packet"]
    lines = [
        "# B10-T1 Positive-Route Acceptance Boundary",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Boundary: `{summary['boundary_id']}`",
        f"- Boundary hash: `{summary['boundary_hash']}`",
        f"- B3 acceptance packet: `{summary['b3_acceptance_packet_id']}`",
        f"- B3 acceptance packet hash: `{summary['b3_acceptance_packet_hash']}`",
        f"- B5 acceptance packet: `{summary['b5_acceptance_packet_id']}`",
        f"- B5 acceptance packet hash: `{summary['b5_acceptance_packet_hash']}`",
        f"- Requirements passed/failed: `{summary['requirements_passed']}` / `{summary['requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_requirement_ids']}`",
        f"- B3 failed acceptance IDs: `{summary['b3_failed_acceptance_requirement_ids']}`",
        f"- B5 failed acceptance IDs: `{summary['b5_failed_acceptance_requirement_ids']}`",
        f"- B3 accepted rows / denominator wins: `{summary['b3_accepted_full_covariance_row_count']}` / `{summary['b3_denominator_win_count']}`",
        f"- B3 optimizer-loop lower-bound shots: `{summary['b3_optimizer_loop_shot_lower_bound']}`",
        f"- B5 accepted priority rows / production rows: `{summary['b5_accepted_priority_row_count']}` / `{summary['b5_production_contract_rows_accepted']}`",
        f"- B10-T1 credit / positive-route / BQP credit allowed: `{summary['b10_t1_credit_allowed']}` / `{summary['b10_positive_route_ready']}` / `{summary['b10_bqp_separation_credit_allowed']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Required Downstream Evidence Before B10-T1 Credit",
        "",
    ]
    for item in packet["required_downstream_before_b10_t1_credit"]:
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
            f"- b10_t1_credit_allowed: {payload['claim_boundary']['b10_t1_credit_allowed']}",
            f"- b10_positive_route_ready: {payload['claim_boundary']['b10_positive_route_ready']}",
            f"- b10_bqp_separation_credit_allowed: {payload['claim_boundary']['b10_bqp_separation_credit_allowed']}",
            f"- b10_quantum_advantage_credit_allowed: {payload['claim_boundary']['b10_quantum_advantage_credit_allowed']}",
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
        "--b3-acceptance-packet-gate",
        type=Path,
        default=Path("results/B3_B10_full_covariance_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--b5-acceptance-packet-gate",
        type=Path,
        default=Path("results/B5_B10_w1_priority_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B10_T1_positive_route_acceptance_boundary_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B10_T1_positive_route_acceptance_boundary.md"),
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
