#!/usr/bin/env python3
"""T-B5-006u/T-B6-005l: B5 view of the B6/B5 observable row acceptance gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b5_b6_observable_mechanism_boundary_v0"
STATUS = "b5_b6_observable_mechanism_boundary_synced"
MODEL_STATUS = "b5_mechanism_zero_credit_after_b6_b5_observable_row_acceptance_packet_gate"
VERSION = "0.1"
EXPECTED_METHOD = "b6_b5_observable_row_acceptance_packet_gate_v0"
EXPECTED_ACCEPTANCE_PACKET_ID = "B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet"
EXPECTED_MATERIAL_ID = "monolayer_FeSe_STO_2012"
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
        "boundary_id": "B5-B6-observable-mechanism-boundary",
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "source_method": source.get("method"),
        "acceptance_packet_id": summary.get("acceptance_packet_id"),
        "acceptance_packet_hash": summary.get("acceptance_packet_hash"),
        "material_id": summary.get("material_id"),
        "row_replay_validation_manifest_id": summary.get("row_replay_validation_manifest_id"),
        "row_replay_validation_manifest_hash": summary.get("row_replay_validation_manifest_hash"),
        "record_count": summary.get("record_count"),
        "family_count": summary.get("family_count"),
        "negative_control_count": summary.get("negative_control_count"),
        "selected_negative_controls_in_top_k": summary.get("selected_negative_controls_in_top_k"),
        "accepted_dft_b5_row_count": summary.get("accepted_dft_b5_row_count"),
        "accepted_priority_dft_rows": summary.get("accepted_priority_dft_rows"),
        "accepted_priority_b5_rows": summary.get("accepted_priority_b5_rows"),
        "b5_mechanism_credit_allowed": False,
        "b5_computed_observable_credit_allowed": False,
        "high_tc_mechanism_credit_allowed": False,
        "material_discovery_credit_allowed": False,
        "required_downstream_before_b5_mechanism_credit": [
            "accepted B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet",
            "source-backed DFT input and output bundle",
            "source-backed B5 correlation observable table",
            "same-access cost ledger linking B6 descriptor evidence to B5 observable computation",
            "negative-control replay preserving the 56-record / 28-family / 18-negative-control denominator",
            "family-prior denominator result showing the observable route beats the family prior",
            "claim boundary that still forbids discovery, mechanism-solved, solution, and quantum-advantage claims until rows are accepted",
        ],
    }
    boundary_packet["boundary_hash"] = stable_hash(boundary_packet)

    no_forbidden_claims = all(
        summary.get(key) is False
        for key in [
            "dft_observable_claimed",
            "b5_computed_observable_claimed",
            "material_discovery_claimed",
            "mechanism_solved",
            "solution_claimed",
        ]
    )

    requirements = [
        requirement(
            "S1",
            "Source B6/B5 observable row acceptance packet gate is present and current",
            source.get("method") == EXPECTED_METHOD
            and summary.get("acceptance_packet_id") == EXPECTED_ACCEPTANCE_PACKET_ID
            and summary.get("material_id") == EXPECTED_MATERIAL_ID
            and summary.get("validation_error_count") == 0,
            {
                "source_method": source.get("method"),
                "acceptance_packet_id": summary.get("acceptance_packet_id"),
                "material_id": summary.get("material_id"),
                "validation_error_count": summary.get("validation_error_count"),
            },
        ),
        requirement(
            "S2",
            "Source acceptance gate remains blocked on missing submitted packet evidence",
            summary.get("failed_acceptance_requirement_ids") == EXPECTED_FAILED_IDS
            and summary.get("submitted_acceptance_packet_exists") is False,
            {
                "failed_acceptance_requirement_ids": summary.get("failed_acceptance_requirement_ids"),
                "submitted_acceptance_packet_exists": summary.get("submitted_acceptance_packet_exists"),
            },
        ),
        requirement(
            "S3",
            "B6/B5 denominator scope remains preserved",
            summary.get("record_count") == 56
            and summary.get("family_count") == 28
            and summary.get("negative_control_count") == 18
            and summary.get("selected_negative_controls_in_top_k") == 2
            and summary.get("template_row_count") == 12,
            {
                "record_count": summary.get("record_count"),
                "family_count": summary.get("family_count"),
                "negative_control_count": summary.get("negative_control_count"),
                "selected_negative_controls_in_top_k": summary.get("selected_negative_controls_in_top_k"),
                "template_row_count": summary.get("template_row_count"),
            },
        ),
        requirement(
            "S4",
            "No DFT/B5 observable row has been accepted",
            summary.get("accepted_dft_b5_row_count") == 0
            and summary.get("accepted_priority_dft_rows") == 0
            and summary.get("accepted_priority_b5_rows") == 0,
            {
                "accepted_dft_b5_row_count": summary.get("accepted_dft_b5_row_count"),
                "accepted_priority_dft_rows": summary.get("accepted_priority_dft_rows"),
                "accepted_priority_b5_rows": summary.get("accepted_priority_b5_rows"),
            },
        ),
        requirement(
            "S5",
            "B5 mechanism, observable, material-discovery, and solution credit remain disabled",
            boundary_packet["b5_mechanism_credit_allowed"] is False
            and boundary_packet["b5_computed_observable_credit_allowed"] is False
            and boundary_packet["high_tc_mechanism_credit_allowed"] is False
            and boundary_packet["material_discovery_credit_allowed"] is False,
            {
                "b5_mechanism_credit_allowed": boundary_packet["b5_mechanism_credit_allowed"],
                "b5_computed_observable_credit_allowed": boundary_packet[
                    "b5_computed_observable_credit_allowed"
                ],
                "high_tc_mechanism_credit_allowed": boundary_packet["high_tc_mechanism_credit_allowed"],
                "material_discovery_credit_allowed": boundary_packet["material_discovery_credit_allowed"],
            },
        ),
        requirement(
            "S6",
            "Forbidden observable, discovery, mechanism, and solution claims remain absent",
            no_forbidden_claims,
            {
                "dft_observable_claimed": summary.get("dft_observable_claimed"),
                "b5_computed_observable_claimed": summary.get("b5_computed_observable_claimed"),
                "material_discovery_claimed": summary.get("material_discovery_claimed"),
                "mechanism_solved": summary.get("mechanism_solved"),
                "solution_claimed": summary.get("solution_claimed"),
            },
        ),
        requirement(
            "S7",
            "Boundary records downstream evidence required before B5 mechanism credit",
            len(boundary_packet["required_downstream_before_b5_mechanism_credit"]) == 7,
            {
                "required_downstream_before_b5_mechanism_credit": boundary_packet[
                    "required_downstream_before_b5_mechanism_credit"
                ]
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors = []
    if failed_ids:
        validation_errors.append(f"B5/B6 observable mechanism boundary failed: {failed_ids}")

    payload_summary = {
        "boundary_id": boundary_packet["boundary_id"],
        "boundary_hash": boundary_packet["boundary_hash"],
        "source_acceptance_packet_hash": summary.get("acceptance_packet_hash"),
        "acceptance_packet_id": summary.get("acceptance_packet_id"),
        "material_id": summary.get("material_id"),
        "row_replay_validation_manifest_id": summary.get("row_replay_validation_manifest_id"),
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "source_failed_acceptance_requirement_ids": summary.get("failed_acceptance_requirement_ids"),
        "submitted_acceptance_packet_exists": summary.get("submitted_acceptance_packet_exists"),
        "record_count": summary.get("record_count"),
        "family_count": summary.get("family_count"),
        "negative_control_count": summary.get("negative_control_count"),
        "selected_negative_controls_in_top_k": summary.get("selected_negative_controls_in_top_k"),
        "accepted_dft_b5_row_count": summary.get("accepted_dft_b5_row_count"),
        "accepted_priority_dft_rows": summary.get("accepted_priority_dft_rows"),
        "accepted_priority_b5_rows": summary.get("accepted_priority_b5_rows"),
        "b5_mechanism_credit_allowed": False,
        "b5_computed_observable_credit_allowed": False,
        "high_tc_mechanism_credit_allowed": False,
        "material_discovery_credit_allowed": False,
        "dft_observable_claimed": False,
        "b5_computed_observable_claimed": False,
        "material_discovery_claimed": False,
        "mechanism_solved": False,
        "solution_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B5",
        "linked_benchmark_id": "B6",
        "source_target_id": "T-B5-006u/T-B6-005l",
        "title": "B5/B6 Observable Mechanism Boundary",
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
                "B5 is now explicitly synchronized to the B6/B5 observable row acceptance "
                "packet as a zero-credit mechanism boundary."
            ),
            "what_is_not_supported": (
                "No accepted DFT row, B5 computed observable row, high-Tc mechanism, "
                "material discovery, mechanism solution, or B5 mechanism credit is supported."
            ),
            "next_gate": (
                "Submit and accept the B6/B5 observable row acceptance packet with source-backed "
                "DFT, B5 correlation observable, negative-control replay, family-prior denominator, "
                "same-access ledger, and claim boundary before B5 mechanism credit can count."
            ),
            "b5_mechanism_credit_allowed": False,
            "b5_computed_observable_credit_allowed": False,
            "high_tc_mechanism_credit_allowed": False,
            "material_discovery_credit_allowed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["boundary_packet"]
    lines = [
        "# B5/B6 Observable Mechanism Boundary",
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
        f"- Material: `{summary['material_id']}`",
        f"- Row replay-validation manifest: `{summary['row_replay_validation_manifest_id']}`",
        f"- Requirements passed/failed: `{summary['requirements_passed']}` / `{summary['requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_requirement_ids']}`",
        f"- Source failed acceptance IDs: `{summary['source_failed_acceptance_requirement_ids']}`",
        f"- Denominator records / families / negative controls: `{summary['record_count']}` / `{summary['family_count']}` / `{summary['negative_control_count']}`",
        f"- Selected negative controls in top-k: `{summary['selected_negative_controls_in_top_k']}`",
        f"- Accepted DFT/B5 row count: `{summary['accepted_dft_b5_row_count']}`",
        f"- Accepted priority DFT/B5 rows: `{summary['accepted_priority_dft_rows']}` / `{summary['accepted_priority_b5_rows']}`",
        f"- B5 mechanism / observable / high-Tc / discovery credit allowed: `{summary['b5_mechanism_credit_allowed']}` / `{summary['b5_computed_observable_credit_allowed']}` / `{summary['high_tc_mechanism_credit_allowed']}` / `{summary['material_discovery_credit_allowed']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Required Downstream Evidence Before B5 Mechanism Credit",
        "",
    ]
    for item in packet["required_downstream_before_b5_mechanism_credit"]:
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
            f"- b5_mechanism_credit_allowed: {payload['claim_boundary']['b5_mechanism_credit_allowed']}",
            f"- b5_computed_observable_credit_allowed: {payload['claim_boundary']['b5_computed_observable_credit_allowed']}",
            f"- high_tc_mechanism_credit_allowed: {payload['claim_boundary']['high_tc_mechanism_credit_allowed']}",
            f"- material_discovery_credit_allowed: {payload['claim_boundary']['material_discovery_credit_allowed']}",
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
        default=Path("results/B6_B5_observable_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B5_B6_observable_mechanism_boundary_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B5_B6_observable_mechanism_boundary.md"),
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
