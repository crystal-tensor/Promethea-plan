#!/usr/bin/env python3
"""T-B3-021/T-B10-015h: post-boundary submission triage for full covariance."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b3_b10_full_covariance_post_boundary_submission_triage_v0"
STATUS = "b3_b10_full_covariance_post_boundary_triage_ready_no_credit"
MODEL_STATUS = "b3_zero_credit_reopen_boundary_split_into_pr_sized_covariance_packets"
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
            "F1",
            "Four source-backed full compiled-state covariance rows",
            "chemistry-measurement-agent",
            "ready_for_external_pr_not_credit",
            "accepted full-covariance row count is still zero",
            [
                "submissions/B3-R1-full-compiled-covariance/full_covariance_rows.json",
                "submissions/B3-R1-full-compiled-covariance/compiled_state_replay/",
                "submissions/B3-R1-full-compiled-covariance/covariance_replay_manifest.json",
            ],
            [
                "four row-aligned instances are source-backed",
                "compiled-state covariance replay is hash-bound",
                "accepted_full_covariance_row_count > 0 only after row replay validation",
            ],
        ),
        packet(
            "F2",
            "Multi-parameter converged chemistry state-preparation evidence",
            "chemistry-stateprep-agent",
            "ready_for_external_pr_not_credit",
            "only one compiled pilot exists and it is not a converged multi-parameter state-prep result",
            [
                "submissions/B3-R1-full-compiled-covariance/stateprep_convergence_ledger.json",
                "submissions/B3-R1-full-compiled-covariance/multi_parameter_ansatz_manifest.json",
                "submissions/B3-R1-full-compiled-covariance/stateprep_cost_ledger.json",
            ],
            [
                "multi-parameter state-prep convergence is shown for the same rows",
                "state-prep cost is charged in two-qubit gates and optimizer calls",
                "one-parameter pilot evidence is not promoted beyond provenance",
            ],
        ),
        packet(
            "F3",
            "Same-access selected-CI/larger-basis denominator wins",
            "baseline-adversary",
            "ready_for_external_pr_not_credit",
            "denominator win count remains zero",
            [
                "submissions/B3-R1-full-compiled-covariance/same_access_denominator_ledger.json",
                "submissions/B3-R1-full-compiled-covariance/selected_ci_replay_manifest.json",
                "submissions/B3-R1-full-compiled-covariance/denominator_comparison_table.json",
            ],
            [
                "denominator_win_count > 0 under the same row and access contract",
                "selected-CI/larger-basis replay is hash-bound",
                "no hidden access advantage is used",
            ],
        ),
        packet(
            "F4",
            "Optimizer-loop cost collapse evidence",
            "measurement-optimization-agent",
            "ready_for_external_pr_not_credit",
            "optimizer-loop lower-bound shots remain 475,043,013,690,000",
            [
                "submissions/B3-R1-full-compiled-covariance/optimizer_loop_cost_replay.json",
                "submissions/B3-R1-full-compiled-covariance/derivative_estimator_replay.json",
                "submissions/B3-R1-full-compiled-covariance/measurement_strategy_delta.json",
            ],
            [
                "optimizer-loop lower-bound shots materially decrease",
                "derivative estimator and measurement strategy are replayable",
                "state-prep and measurement costs remain charged",
            ],
        ),
        packet(
            "F5",
            "B10-T1 access-contract acceptance after F1-F4",
            "bqp-boundary-agent",
            "blocked_until_F1_F2_F3_F4_evidence",
            "B10-T1 cannot count credit without accepted rows, denominator wins, and same-access replay",
            [
                "submissions/B3-R1-full-compiled-covariance/b10_access_contract_acceptance.json",
                "submissions/B3-R1-full-compiled-covariance/b10_t1_claim_boundary.md",
            ],
            [
                "F1-F4 evidence is accepted by the B3 row acceptance packet",
                "positive same-access route is explicit",
                "B10-T1 credit remains false until access-contract acceptance",
            ],
        ),
    ]
    ready_packets = [p for p in work_packets if p["status"] == "ready_for_external_pr_not_credit"]
    blocked_packets = [p for p in work_packets if p["status"].startswith("blocked_")]
    triage_packet = {
        "triage_id": "B3-B10-full-covariance-post-boundary-submission-triage",
        "source_boundary": str(args.boundary),
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "boundary_hash": boundary_summary.get("boundary_hash"),
        "acceptance_packet_hash": boundary_summary.get("source_acceptance_packet_hash"),
        "priority_packet_hash": acceptance_summary.get("priority_packet_hash"),
        "downstream_packet_id": boundary_summary.get("downstream_packet_id"),
        "row_aligned_instance_count": boundary_summary.get("row_aligned_instance_count"),
        "compiled_pilot_instance_count": boundary_summary.get("compiled_pilot_instance_count"),
        "accepted_full_covariance_row_count": boundary_summary.get(
            "accepted_full_covariance_row_count"
        ),
        "denominator_win_count": boundary_summary.get("denominator_win_count"),
        "max_optimizer_loop_total_shots_lower_bound": boundary_summary.get(
            "max_optimizer_loop_total_shots_lower_bound"
        ),
        "b3_reopen_ready": False,
        "b3_full_covariance_credit_allowed": False,
        "b10_t1_credit_allowed": False,
        "work_packet_ids": [p["packet_id"] for p in work_packets],
    }
    triage_packet["triage_hash"] = stable_hash(triage_packet)

    forbidden_claims_false = all(
        boundary_summary.get(key) is False
        for key in [
            "reaction_dynamics_solution_claimed",
            "quantum_advantage_claimed",
            "bqp_separation_claimed",
        ]
    )

    conditions = [
        condition(
            "C1",
            "Source B3/B10 full-covariance zero-credit boundary is current and valid",
            boundary.get("method") == "b3_b10_full_covariance_reopen_boundary_v0"
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
            "The source acceptance packet remains blocked before row credit",
            acceptance.get("method") == "b3_b10_full_covariance_row_acceptance_packet_gate_v0"
            and (
                (
                    acceptance_summary.get("failed_acceptance_requirement_ids") == ["P6", "P7", "P8"]
                    and acceptance_summary.get("submitted_acceptance_packet_exists") is False
                )
                or (
                    acceptance_summary.get("failed_acceptance_requirement_ids") == ["P8"]
                    and acceptance_summary.get("submitted_acceptance_packet_exists") is True
                    and acceptance_summary.get("denominator_win_count") == 0
                    and acceptance_summary.get("accepted_full_covariance_row_count") == 0
                )
            ),
            {
                "failed_acceptance_requirement_ids": acceptance_summary.get(
                    "failed_acceptance_requirement_ids"
                ),
                "submitted_acceptance_packet_exists": acceptance_summary.get(
                    "submitted_acceptance_packet_exists"
                ),
                "denominator_win_count": acceptance_summary.get("denominator_win_count"),
                "accepted_full_covariance_row_count": acceptance_summary.get(
                    "accepted_full_covariance_row_count"
                ),
            },
        ),
        condition(
            "C3",
            "The B3 full-covariance scope is preserved",
            boundary_summary.get("row_aligned_instance_count") == 4
            and boundary_summary.get("compiled_pilot_instance_count") == 1
            and boundary_summary.get("max_optimizer_loop_total_shots_lower_bound")
            == 475043013690000,
            {
                "row_aligned_instance_count": boundary_summary.get("row_aligned_instance_count"),
                "compiled_pilot_instance_count": boundary_summary.get("compiled_pilot_instance_count"),
                "max_optimizer_loop_total_shots_lower_bound": boundary_summary.get(
                    "max_optimizer_loop_total_shots_lower_bound"
                ),
            },
        ),
        condition(
            "C4",
            "Four B3 evidence PR packets are ready for external agents",
            [p["packet_id"] for p in ready_packets] == ["F1", "F2", "F3", "F4"],
            {"ready_packet_ids": [p["packet_id"] for p in ready_packets]},
        ),
        condition(
            "C5",
            "B10-T1 access-contract acceptance is correctly blocked until F1-F4 evidence exists",
            [p["packet_id"] for p in blocked_packets] == ["F5"]
            and boundary_summary.get("accepted_full_covariance_row_count") == 0
            and boundary_summary.get("denominator_win_count") == 0,
            {
                "blocked_packet_ids": [p["packet_id"] for p in blocked_packets],
                "accepted_full_covariance_row_count": boundary_summary.get(
                    "accepted_full_covariance_row_count"
                ),
                "denominator_win_count": boundary_summary.get("denominator_win_count"),
            },
        ),
        condition(
            "C6",
            "Forbidden B3/B10 credit and advantage claims remain false",
            forbidden_claims_false
            and boundary_summary.get("b3_reopen_ready") is False
            and boundary_summary.get("b3_full_covariance_credit_allowed") is False
            and boundary_summary.get("b10_t1_credit_allowed") is False
            and priority_summary.get("quantum_advantage_claimed") is False,
            {
                "b3_reopen_ready": boundary_summary.get("b3_reopen_ready"),
                "b3_full_covariance_credit_allowed": boundary_summary.get(
                    "b3_full_covariance_credit_allowed"
                ),
                "b10_t1_credit_allowed": boundary_summary.get("b10_t1_credit_allowed"),
                "reaction_dynamics_solution_claimed": boundary_summary.get(
                    "reaction_dynamics_solution_claimed"
                ),
                "quantum_advantage_claimed": boundary_summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": boundary_summary.get("bqp_separation_claimed"),
            },
        ),
    ]
    satisfied = sum(row["satisfied"] for row in conditions)
    failed_ids = [row["condition_id"] for row in conditions if not row["satisfied"]]
    validation_errors = []
    if failed_ids:
        validation_errors.append(f"B3/B10 full-covariance post-boundary triage failed: {failed_ids}")
    if len(work_packets) != 5 or len(ready_packets) != 4 or len(blocked_packets) != 1:
        validation_errors.append("unexpected B3/B10 work-packet shape")

    summary = {
        "triage_id": triage_packet["triage_id"],
        "triage_hash": triage_packet["triage_hash"],
        "source_boundary_hash": boundary_summary.get("boundary_hash"),
        "source_acceptance_packet_hash": boundary_summary.get("source_acceptance_packet_hash"),
        "priority_packet_hash": acceptance_summary.get("priority_packet_hash"),
        "downstream_packet_id": boundary_summary.get("downstream_packet_id"),
        "work_packet_count": len(work_packets),
        "ready_external_pr_packet_count": len(ready_packets),
        "blocked_packet_count": len(blocked_packets),
        "ready_packet_ids": [p["packet_id"] for p in ready_packets],
        "blocked_packet_ids": [p["packet_id"] for p in blocked_packets],
        "condition_count": len(conditions),
        "conditions_satisfied": satisfied,
        "conditions_failed": len(conditions) - satisfied,
        "failed_condition_ids": failed_ids,
        "row_aligned_instance_count": boundary_summary.get("row_aligned_instance_count"),
        "compiled_pilot_instance_count": boundary_summary.get("compiled_pilot_instance_count"),
        "accepted_full_covariance_row_count": boundary_summary.get(
            "accepted_full_covariance_row_count"
        ),
        "accepted_priority_reopen_rows": boundary_summary.get("accepted_priority_reopen_rows"),
        "denominator_win_count": boundary_summary.get("denominator_win_count"),
        "selected_ci_larger_basis_denominator_beaten_count": boundary_summary.get(
            "selected_ci_larger_basis_denominator_beaten_count"
        ),
        "max_optimizer_loop_total_shots_lower_bound": boundary_summary.get(
            "max_optimizer_loop_total_shots_lower_bound"
        ),
        "b3_reopen_ready": False,
        "b3_full_covariance_credit_allowed": False,
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
        "source_target_id": "T-B3-021/T-B10-015h",
        "title": "B3/B10 Full-Covariance Post-Boundary Submission Triage",
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
            "b3_reopen_ready": False,
            "b3_full_covariance_credit_allowed": False,
            "b10_t1_credit_allowed": False,
            "positive_same_access_route_allowed": False,
            "reaction_dynamics_solution_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
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
            f"The B3/B10 full-covariance post-boundary triage satisfies "
            f"{s['conditions_satisfied']}/{s['condition_count']} conditions and emits "
            f"{s['work_packet_count']} PR-sized work packets."
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
            f"- Downstream packet: `{s['downstream_packet_id']}`",
            f"- Row-aligned instances: `{s['row_aligned_instance_count']}`",
            f"- Compiled pilot instances: `{s['compiled_pilot_instance_count']}`",
            f"- Accepted full-covariance rows: `{s['accepted_full_covariance_row_count']}`",
            f"- Denominator wins: `{s['denominator_win_count']}`",
            f"- Optimizer-loop lower-bound shots: `{s['max_optimizer_loop_total_shots_lower_bound']}`",
            f"- B3 reopen ready: `{s['b3_reopen_ready']}`",
            f"- B10-T1 credit allowed: `{s['b10_t1_credit_allowed']}`",
            "",
            "## Claim Boundary",
            "",
            "This is a triage result, not a reaction-dynamics result. It does not claim B3 reopen, full-covariance credit, same-access positive route, quantum advantage, BQP separation, or B10-T1 credit.",
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
        default=Path("results/B3_B10_full_covariance_reopen_boundary_v0.json"),
    )
    parser.add_argument(
        "--acceptance-packet-gate",
        type=Path,
        default=Path("results/B3_B10_full_covariance_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B3_B10_reopen_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_B10_full_covariance_post_boundary_submission_triage_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_B10_full_covariance_post_boundary_submission_triage.md"),
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
        raise SystemExit("B3/B10 full-covariance post-boundary triage validation failed")


if __name__ == "__main__":
    main()
