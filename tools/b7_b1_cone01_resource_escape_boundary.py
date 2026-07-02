#!/usr/bin/env python3
"""T-B7-012i/T-B1-004da: B7 view of the B1 cone_01 resource-escape gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b7_b1_cone01_resource_escape_boundary_v0"
STATUS = "b7_b1_cone01_resource_escape_boundary_synced"
MODEL_STATUS = "b7_zero_credit_boundary_after_b1_cone01_resource_escape_acceptance_packet_gate"
VERSION = "0.1"
EXPECTED_METHOD = "b1_b7_cone01_resource_escape_acceptance_packet_gate_v0"
EXPECTED_ACCEPTANCE_PACKET_ID = "B1-B7-cone01-resource-escape-acceptance-packet"
EXPECTED_PRIORITY_PACKET_ID = "B1-B7-cone01-resource-escape"
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
        "boundary_id": "B7-B1-cone01-resource-escape-boundary",
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "source_method": source.get("method"),
        "acceptance_packet_id": summary.get("acceptance_packet_id"),
        "acceptance_packet_hash": summary.get("acceptance_packet_hash"),
        "priority_packet_id": summary.get("priority_packet_id"),
        "priority_packet_hash": summary.get("priority_packet_hash"),
        "replay_validation_manifest_id": summary.get("replay_validation_manifest_id"),
        "replay_validation_manifest_hash": summary.get("replay_validation_manifest_hash"),
        "selected_line_numbers": summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "line1381_off_grid_parameter_count": summary.get("line1381_off_grid_parameter_count"),
        "line1381_unpriced_proxy_t_pressure": summary.get("line1381_unpriced_proxy_t_pressure"),
        "line1378_delta_recovered": summary.get("line1378_delta_recovered"),
        "accepted_exit_route_count": summary.get("accepted_exit_route_count"),
        "accepted_occurrence_removal": summary.get("accepted_occurrence_removal"),
        "accepted_proxy_t_reduction": summary.get("accepted_proxy_t_reduction"),
        "source_b7_credit_delta": summary.get("b7_credit_delta"),
        "b7_resource_credit_allowed": False,
        "b7_ft_ledger_credit_allowed": False,
        "b7_occurrence_removal_credit_allowed": False,
        "b7_proxy_t_reduction_credit": 0,
        "b7_space_time_volume_credit": 0,
        "required_downstream_before_b7_credit": [
            "submitted B1-B7-cone01-resource-escape-acceptance-packet",
            "one accepted source-backed exit route",
            "full-circuit replay or symbolic equivalence certificate",
            "no-double-counting ledger for selected lines [268, 1381] and dropped overlap line [1378]",
            "line-1381 off-grid local-U3 elimination, absorption, or honest physical pricing",
            "line-1378 recovery proof or explicit unrecovered-delta accounting",
            "refreshed B7 ledger replay with nonzero accepted occurrence removal and proxy-T reduction",
            "claim boundary forbidding B7 resource, FT ledger, quantum-advantage, and solution claims until the ledger accepts the route",
        ],
    }
    boundary_packet["boundary_hash"] = stable_hash(boundary_packet)

    no_forbidden_claims = all(
        summary.get(key) is False
        for key in [
            "resource_saving_claimed",
            "b7_ledger_improvement_claimed",
        ]
    )

    requirements = [
        requirement(
            "S1",
            "Source B1/B7 cone_01 resource-escape acceptance packet gate is present and current",
            source.get("method") == EXPECTED_METHOD
            and summary.get("acceptance_packet_id") == EXPECTED_ACCEPTANCE_PACKET_ID
            and summary.get("priority_packet_id") == EXPECTED_PRIORITY_PACKET_ID
            and summary.get("validation_error_count") == 0,
            {
                "source_method": source.get("method"),
                "acceptance_packet_id": summary.get("acceptance_packet_id"),
                "priority_packet_id": summary.get("priority_packet_id"),
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
            "The B1/B7 resource-escape scope is preserved for the B7 view",
            summary.get("selected_line_numbers") == [268, 1381]
            and summary.get("dropped_overlap_candidate_line_numbers") == [1378]
            and summary.get("line1381_off_grid_parameter_count") == 5
            and summary.get("line1381_unpriced_proxy_t_pressure") == 100,
            {
                "selected_line_numbers": summary.get("selected_line_numbers"),
                "dropped_overlap_candidate_line_numbers": summary.get(
                    "dropped_overlap_candidate_line_numbers"
                ),
                "line1381_off_grid_parameter_count": summary.get(
                    "line1381_off_grid_parameter_count"
                ),
                "line1381_unpriced_proxy_t_pressure": summary.get(
                    "line1381_unpriced_proxy_t_pressure"
                ),
            },
        ),
        requirement(
            "S4",
            "No resource-escape exit route has been accepted",
            summary.get("accepted_exit_route_count") == 0
            and summary.get("accepted_occurrence_removal") == 0
            and summary.get("accepted_proxy_t_reduction") == 0
            and summary.get("line1378_delta_recovered") is False,
            {
                "accepted_exit_route_count": summary.get("accepted_exit_route_count"),
                "accepted_occurrence_removal": summary.get("accepted_occurrence_removal"),
                "accepted_proxy_t_reduction": summary.get("accepted_proxy_t_reduction"),
                "line1378_delta_recovered": summary.get("line1378_delta_recovered"),
            },
        ),
        requirement(
            "S5",
            "B7 resource, FT ledger, occurrence-removal, proxy-T, and STV credit remain disabled",
            boundary_packet["b7_resource_credit_allowed"] is False
            and boundary_packet["b7_ft_ledger_credit_allowed"] is False
            and boundary_packet["b7_occurrence_removal_credit_allowed"] is False
            and boundary_packet["b7_proxy_t_reduction_credit"] == 0
            and boundary_packet["b7_space_time_volume_credit"] == 0
            and summary.get("b7_credit_delta") == 0,
            {
                "b7_resource_credit_allowed": boundary_packet["b7_resource_credit_allowed"],
                "b7_ft_ledger_credit_allowed": boundary_packet["b7_ft_ledger_credit_allowed"],
                "b7_occurrence_removal_credit_allowed": boundary_packet[
                    "b7_occurrence_removal_credit_allowed"
                ],
                "b7_proxy_t_reduction_credit": boundary_packet["b7_proxy_t_reduction_credit"],
                "b7_space_time_volume_credit": boundary_packet["b7_space_time_volume_credit"],
                "source_b7_credit_delta": summary.get("b7_credit_delta"),
            },
        ),
        requirement(
            "S6",
            "Forbidden resource-saving and B7 ledger-improvement claims remain absent",
            no_forbidden_claims,
            {
                "resource_saving_claimed": summary.get("resource_saving_claimed"),
                "b7_ledger_improvement_claimed": summary.get("b7_ledger_improvement_claimed"),
                "b7_resource_credit_allowed": boundary_packet["b7_resource_credit_allowed"],
            },
        ),
        requirement(
            "S7",
            "Boundary records downstream evidence required before B7 can count credit",
            len(boundary_packet["required_downstream_before_b7_credit"]) == 8,
            {
                "required_downstream_before_b7_credit": boundary_packet[
                    "required_downstream_before_b7_credit"
                ]
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors = []
    if failed_ids:
        validation_errors.append(f"B7/B1 cone_01 resource-escape boundary failed: {failed_ids}")

    payload_summary = {
        "boundary_id": boundary_packet["boundary_id"],
        "boundary_hash": boundary_packet["boundary_hash"],
        "source_acceptance_packet_hash": summary.get("acceptance_packet_hash"),
        "acceptance_packet_id": summary.get("acceptance_packet_id"),
        "priority_packet_id": summary.get("priority_packet_id"),
        "replay_validation_manifest_id": summary.get("replay_validation_manifest_id"),
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "source_failed_acceptance_requirement_ids": summary.get(
            "failed_acceptance_requirement_ids"
        ),
        "submitted_acceptance_packet_exists": summary.get("submitted_acceptance_packet_exists"),
        "selected_line_numbers": summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "line1381_off_grid_parameter_count": summary.get("line1381_off_grid_parameter_count"),
        "line1381_unpriced_proxy_t_pressure": summary.get("line1381_unpriced_proxy_t_pressure"),
        "line1378_delta_recovered": summary.get("line1378_delta_recovered"),
        "accepted_exit_route_count": summary.get("accepted_exit_route_count"),
        "accepted_occurrence_removal": summary.get("accepted_occurrence_removal"),
        "accepted_proxy_t_reduction": summary.get("accepted_proxy_t_reduction"),
        "b7_credit_delta": 0,
        "b7_resource_credit_allowed": False,
        "b7_ft_ledger_credit_allowed": False,
        "b7_occurrence_removal_credit_allowed": False,
        "b7_proxy_t_reduction_credit": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B7",
        "linked_benchmark_id": "B1",
        "source_target_id": "T-B7-012i/T-B1-004da",
        "title": "B7/B1 Cone01 Resource-Escape Boundary",
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
                "B7 is now explicitly synchronized to the B1 cone_01 resource-escape "
                "acceptance packet as a zero-credit resource boundary."
            ),
            "what_is_not_supported": (
                "No accepted exit route, occurrence removal, proxy-T reduction, "
                "space-time-volume reduction, FT ledger improvement, B7 resource credit, "
                "quantum advantage, or solution claim is supported."
            ),
            "next_gate": (
                "Submit and accept the B1-B7 cone_01 resource-escape acceptance packet "
                "with one source-backed exit route, full replay or symbolic equivalence, "
                "no-double-counting ledger, honest line-1381 pricing, line-1378 accounting, "
                "and refreshed B7 ledger before B7 can count resource credit."
            ),
            "b7_resource_credit_allowed": False,
            "b7_ft_ledger_credit_allowed": False,
            "b7_occurrence_removal_credit_allowed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["boundary_packet"]
    lines = [
        "# B7/B1 Cone01 Resource-Escape Boundary",
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
        f"- Priority packet: `{summary['priority_packet_id']}`",
        f"- Replay-validation manifest: `{summary['replay_validation_manifest_id']}`",
        f"- Requirements passed/failed: `{summary['requirements_passed']}` / `{summary['requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_requirement_ids']}`",
        f"- Source failed acceptance IDs: `{summary['source_failed_acceptance_requirement_ids']}`",
        f"- Selected lines / dropped overlap line: `{summary['selected_line_numbers']}` / `{summary['dropped_overlap_candidate_line_numbers']}`",
        f"- Line 1381 off-grid parameters / unpriced proxy-T pressure: `{summary['line1381_off_grid_parameter_count']}` / `{summary['line1381_unpriced_proxy_t_pressure']}`",
        f"- Line 1378 delta recovered: `{summary['line1378_delta_recovered']}`",
        f"- Accepted exit routes / occurrence removal / proxy-T reduction: `{summary['accepted_exit_route_count']}` / `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- B7 resource / FT ledger / occurrence-removal credit allowed: `{summary['b7_resource_credit_allowed']}` / `{summary['b7_ft_ledger_credit_allowed']}` / `{summary['b7_occurrence_removal_credit_allowed']}`",
        f"- B7 proxy-T / STV credit: `{summary['b7_proxy_t_reduction_credit']}` / `{summary['b7_space_time_volume_credit']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Required Downstream Evidence Before B7 Credit",
        "",
    ]
    for item in packet["required_downstream_before_b7_credit"]:
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
            f"- b7_resource_credit_allowed: {payload['claim_boundary']['b7_resource_credit_allowed']}",
            f"- b7_ft_ledger_credit_allowed: {payload['claim_boundary']['b7_ft_ledger_credit_allowed']}",
            f"- b7_occurrence_removal_credit_allowed: {payload['claim_boundary']['b7_occurrence_removal_credit_allowed']}",
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
        default=Path("results/B1_B7_cone01_resource_escape_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B7_B1_cone01_resource_escape_boundary_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B7_B1_cone01_resource_escape_boundary.md"),
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
