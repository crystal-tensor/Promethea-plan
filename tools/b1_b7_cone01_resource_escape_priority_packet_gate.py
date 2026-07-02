#!/usr/bin/env python3
"""T-B1-004cu/T-B7-012: B1/B7 cone_01 resource-escape priority packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_resource_escape_priority_packet_gate_v0"
STATUS = "cone01_resource_escape_priority_packet_open_missing_artifact"
MODEL_STATUS = "line1381_line1378_or_30_occurrence_escape_packet_ready_no_artifact_submitted"
VERSION = "0.1"
EXPECTED_PACKET_ID = "B1-B7-cone01-resource-escape"
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
    claim_seal = load_json(args.claim_boundary_seal)
    claim_summary = claim_seal["summary"]
    physical = load_json(args.physical_pricing_gate)
    physical_summary = physical["summary"]
    submission_path = args.submission_dir / f"{EXPECTED_PACKET_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None

    required_keys = [
        "packet_id",
        "selected_line_numbers",
        "line1381_resolution_mode",
        "line1381_parameter_certificate_hashes",
        "line1378_recovery_certificate_hash",
        "occurrence_certificate_count",
        "occurrence_certificate_hashes",
        "b7_ledger_replay_hash",
        "qiskit_loader_evidence_seal_hash",
        "claim_boundary",
    ]
    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]

    line1381_closed = (
        submitted is not None
        and submitted.get("line1381_off_grid_parameter_count_after") == 0
        and submitted.get("line1381_resolution_mode")
        in {"eliminated", "absorbed", "symbolically_decomposed", "honestly_priced_with_credit"}
        and submitted.get("full_replay_certificate_present") is True
    )
    line1378_closed = (
        submitted is not None
        and submitted.get("line1378_delta_recovered") is True
        and submitted.get("overlap_double_counting_excluded") is True
    )
    occurrence_closed = (
        submitted is not None
        and submitted.get("occurrence_certificate_count", 0) >= 30
        and submitted.get("b7_ledger_accepted_occurrence_removal", 0) >= 30
        and submitted.get("b7_ledger_accepted_proxy_t_reduction", 0) >= 600
    )
    source_backed = (
        submitted is not None
        and submitted.get("source_evidence_files_present") is True
        and not missing_keys
        and (line1381_closed or line1378_closed or occurrence_closed)
    )

    priority_packet = {
        "packet_id": EXPECTED_PACKET_ID,
        "submission_artifact_path": str(submission_path),
        "source_claim_boundary_seal": str(args.claim_boundary_seal),
        "source_physical_pricing_gate": str(args.physical_pricing_gate),
        "selected_line_numbers": claim_summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": claim_summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "required_keys": required_keys,
        "required_evidence_files": [
            "line1381_parameter_resolution_certificates",
            "line1381_full_replay_or_symbolic_equivalence_certificate",
            "line1378_overlap_recovery_certificate",
            "line1378_no_double_counting_ledger",
            "occurrence_removal_certificate_batch",
            "b7_refreshed_ledger_replay",
            "qiskit_loader_evidence_seal_manifest",
            "openqasm3_candidate_and_source_map",
            "claim_boundary_note",
        ],
        "accepted_exit_modes": [
            {
                "mode": "line1381_resource_escape",
                "acceptance_rule": (
                    "All five line-1381 off-grid local-U3 parameters are eliminated, "
                    "absorbed, symbolically decomposed, or honestly priced with enough "
                    "B7 credit, and the result has replay or symbolic-equivalence evidence."
                ),
            },
            {
                "mode": "line1378_overlap_recovery",
                "acceptance_rule": (
                    "The dropped line-1378 3-CNOT delta is recovered with an explicit "
                    "no-double-counting ledger against the selected line-1381 window."
                ),
            },
            {
                "mode": "thirty_occurrence_removing_certificates",
                "acceptance_rule": (
                    "At least 30 occurrence-removing certificates are accepted by the "
                    "refreshed B7 ledger with at least 600 proxy-T reduction."
                ),
            },
        ],
    }
    priority_packet["packet_hash"] = stable_hash(priority_packet)

    requirements = [
        requirement(
            "P1",
            "OpenQASM 3/Qiskit-loader claim-boundary seal remains citable",
            claim_seal.get("method") == "b1_b7_cone01_openqasm3_claim_boundary_seal_gate_v0"
            and claim_summary.get("validation_error_count") == 0
            and claim_summary.get("claim_boundary_sealed") is True,
            {
                "source_status": claim_seal.get("status"),
                "claim_boundary_sealed": claim_summary.get("claim_boundary_sealed"),
                "validation_error_count": claim_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Physical synthesis pricing rejects current line-1381 B7 credit",
            physical.get("method") == "b1_b7_cone01_physical_synthesis_pricing_gate_v0"
            and physical_summary.get("line1381_off_grid_parameter_count") == 5
            and physical_summary.get("physical_synthesis_pricing_accepted") is False
            and physical_summary.get("physical_synthesis_cost_minus_selected_cnot_credit") == 365,
            {
                "line1381_off_grid_parameter_count": physical_summary.get(
                    "line1381_off_grid_parameter_count"
                ),
                "total_physical_synthesis_t_count_bound": physical_summary.get(
                    "total_physical_synthesis_t_count_bound"
                ),
                "physical_synthesis_cost_minus_selected_cnot_credit": physical_summary.get(
                    "physical_synthesis_cost_minus_selected_cnot_credit"
                ),
                "physical_synthesis_pricing_accepted": physical_summary.get(
                    "physical_synthesis_pricing_accepted"
                ),
            },
        ),
        requirement(
            "P3",
            "Packet binds the current three accepted escape routes",
            priority_packet["selected_line_numbers"] == [268, 1381]
            and priority_packet["dropped_overlap_candidate_line_numbers"] == [1378]
            and len(priority_packet["accepted_exit_modes"]) == 3,
            {
                "selected_line_numbers": priority_packet["selected_line_numbers"],
                "dropped_overlap_candidate_line_numbers": priority_packet[
                    "dropped_overlap_candidate_line_numbers"
                ],
                "accepted_exit_mode_count": len(priority_packet["accepted_exit_modes"]),
            },
        ),
        requirement(
            "P4",
            "Packet carries locked schema and evidence file classes",
            len(required_keys) == 10 and len(priority_packet["required_evidence_files"]) == 9,
            {
                "required_key_count": len(required_keys),
                "required_evidence_file_count": len(priority_packet["required_evidence_files"]),
            },
        ),
        requirement(
            "P5",
            "Current B1/B7 state still has zero accepted B7 resource credit",
            claim_summary.get("accepted_occurrence_removal") == 0
            and claim_summary.get("accepted_proxy_t_reduction") == 0
            and claim_summary.get("b7_ledger_improvement_claimed") is False
            and claim_summary.get("resource_saving_claimed") is False,
            {
                "accepted_occurrence_removal": claim_summary.get("accepted_occurrence_removal"),
                "accepted_proxy_t_reduction": claim_summary.get("accepted_proxy_t_reduction"),
                "b7_ledger_improvement_claimed": claim_summary.get(
                    "b7_ledger_improvement_claimed"
                ),
                "resource_saving_claimed": claim_summary.get("resource_saving_claimed"),
            },
        ),
        requirement(
            "P6",
            "Priority resource-escape artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted artifact satisfies the locked resource-escape schema",
            submitted_exists and not missing_keys,
            {"missing_keys": missing_keys, "submitted_key_count": len(submitted) if submitted else 0},
        ),
        requirement(
            "P8",
            "Submitted artifact source-backs at least one accepted escape route",
            source_backed,
            {
                "source_evidence_files_present": submitted.get("source_evidence_files_present")
                if submitted
                else False,
                "line1381_closed": line1381_closed,
                "line1378_closed": line1378_closed,
                "occurrence_closed": occurrence_closed,
            },
        ),
        requirement(
            "P9",
            "Forbidden resource-saving and B7-ledger claims remain false",
            claim_seal["claim_boundary"].get("resource_saving_claimed") is False
            and claim_seal["claim_boundary"].get("b7_ledger_improvement_claimed") is False
            and physical["claim_boundary"].get("resource_saving_claimed") is False
            and physical["claim_boundary"].get("b7_ledger_improvement_claimed") is False,
            {
                "claim_seal_resource_saving_claimed": claim_seal["claim_boundary"].get(
                    "resource_saving_claimed"
                ),
                "claim_seal_b7_ledger_improvement_claimed": claim_seal["claim_boundary"].get(
                    "b7_ledger_improvement_claimed"
                ),
                "physical_resource_saving_claimed": physical["claim_boundary"].get(
                    "resource_saving_claimed"
                ),
                "physical_b7_ledger_improvement_claimed": physical["claim_boundary"].get(
                    "b7_ledger_improvement_claimed"
                ),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected resource-escape packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted artifact until a compiler PR supplies one")

    payload_summary = {
        "priority_packet_id": EXPECTED_PACKET_ID,
        "packet_hash": priority_packet["packet_hash"],
        "priority_requirement_count": len(requirements),
        "priority_requirements_passed": passed,
        "priority_requirements_failed": len(requirements) - passed,
        "failed_priority_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "required_evidence_file_count": len(priority_packet["required_evidence_files"]),
        "selected_line_numbers": claim_summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": claim_summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "line1381_off_grid_parameter_count": claim_summary.get(
            "line1381_replacement_off_pi_over_four_parameter_count"
        ),
        "line1381_unpriced_proxy_t_pressure": claim_summary.get(
            "line1381_unpriced_proxy_t_pressure"
        ),
        "line1378_delta_recovered": claim_summary.get("line1378_delta_recovered"),
        "accepted_occurrence_removal": claim_summary.get("accepted_occurrence_removal"),
        "accepted_proxy_t_reduction": claim_summary.get("accepted_proxy_t_reduction"),
        "b7_ledger_improvement_claimed": False,
        "resource_saving_claimed": False,
        "submitted_artifact_exists": submitted_exists,
        "missing_key_count": len(missing_keys),
        "accepted_exit_route_count": 0,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "problem_ids": [25, 21],
        "title": "B1/B7 Cone_01 Resource-Escape Priority Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_claim_boundary_seal": str(args.claim_boundary_seal),
        "source_physical_pricing_gate": str(args.physical_pricing_gate),
        "workload": claim_seal.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "summary": payload_summary,
        "priority_resource_escape_packet": priority_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The current B1/B7 cone_01 blocker has a concrete source-backed "
                "submission packet with three accepted escape routes."
            ),
            "what_is_not_supported": (
                "No submitted artifact closes line 1381, recovers line 1378, or provides "
                "30 B7-accepted occurrence-removing certificates. No B7 resource saving "
                "or ledger improvement is claimed."
            ),
            "next_gate": (
                "Submit B1-B7-cone01-resource-escape with one source-backed exit route: "
                "line-1381 resolution, line-1378 recovery, or 30 accepted certificates."
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
    packet = payload["priority_resource_escape_packet"]
    lines = [
        "# B1/B7 Cone_01 Resource-Escape Priority Packet Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Priority packet: `{summary['priority_packet_id']}`",
        f"- Packet hash: `{summary['packet_hash']}`",
        f"- Requirements passed/failed: `{summary['priority_requirements_passed']}` / `{summary['priority_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_priority_requirement_ids']}`",
        f"- Selected lines: `{summary['selected_line_numbers']}`",
        f"- Dropped overlap line(s): `{summary['dropped_overlap_candidate_line_numbers']}`",
        f"- Line-1381 off-grid parameters / proxy-T pressure: `{summary['line1381_off_grid_parameter_count']}` / `{summary['line1381_unpriced_proxy_t_pressure']}`",
        f"- Line-1378 recovered: `{summary['line1378_delta_recovered']}`",
        f"- Accepted occurrence/proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- B7 ledger improvement claimed: `{summary['b7_ledger_improvement_claimed']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Submission Packet",
        "",
        f"- Submission path: `{packet['submission_artifact_path']}`",
        f"- Required key count: `{summary['required_key_count']}`",
        f"- Required evidence file count: `{summary['required_evidence_file_count']}`",
        "",
        "Required evidence files:",
        "",
    ]
    for item in packet["required_evidence_files"]:
        lines.append(f"- {item}")
    lines.extend(["", "Accepted exit modes:", ""])
    for mode in packet["accepted_exit_modes"]:
        lines.append(f"- `{mode['mode']}`: {mode['acceptance_rule']}")
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
        "--claim-boundary-seal",
        type=Path,
        default=Path("results/B1_B7_cone01_openqasm3_claim_boundary_seal_gate_v0.json"),
    )
    parser.add_argument(
        "--physical-pricing-gate",
        type=Path,
        default=Path("results/B1_B7_cone01_physical_synthesis_pricing_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B1_B7_cone01_resource_escape_priority_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_resource_escape_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_resource_escape_priority_packet_gate.md"),
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
