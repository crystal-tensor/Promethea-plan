#!/usr/bin/env python3
"""T-B10-016e: B10-T3 view of the B9 checked-transcript acceptance packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b10_t3_checked_transcript_acceptance_boundary_v0"
STATUS = "b10_t3_checked_transcript_acceptance_boundary_synced"
MODEL_STATUS = "b10_t3_zero_credit_boundary_after_b9_checked_transcript_acceptance_packet_gate"
VERSION = "0.1"
EXPECTED_METHOD = "b9_checked_transcript_acceptance_packet_gate_v0"
EXPECTED_ACCEPTANCE_PACKET_ID = "B9-checked-width-locality-transcript-acceptance-packet"


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
        "boundary_id": "B10-T3-checked-transcript-acceptance-boundary",
        "source_acceptance_packet_gate": str(args.acceptance_packet_gate),
        "source_method": source.get("method"),
        "acceptance_packet_id": summary.get("acceptance_packet_id"),
        "acceptance_packet_hash": summary.get("acceptance_packet_hash"),
        "packet_id": summary.get("packet_id"),
        "replay_validation_manifest_id": summary.get("replay_validation_manifest_id"),
        "blocks_acquisition_requirements": summary.get("blocks_acquisition_requirements"),
        "checked_transcript_present": summary.get("checked_transcript_present"),
        "checked_transcript_accepted": summary.get("checked_transcript_accepted"),
        "proof_assistant_checked": summary.get("proof_assistant_checked"),
        "formal_theorem_proved": summary.get("formal_theorem_proved"),
        "explicit_not_quantum_pcp_proof": summary.get("explicit_not_quantum_pcp_proof"),
        "nlts_theorem_claimed": summary.get("nlts_theorem_claimed"),
        "global_gap_amplification_impossibility_claimed": summary.get(
            "global_gap_amplification_impossibility_claimed"
        ),
        "b10_formal_credit_allowed": False,
        "b10_quantum_pcp_credit_allowed": False,
        "b10_nlts_credit_allowed": False,
        "b10_bqp_separation_credit_allowed": False,
        "required_downstream_before_credit": [
            "accepted B9-checked-width-locality-transcript-provenance-manifest",
            "accepted B9-checked-width-locality-transcript-replay-validation-manifest",
            "accepted B9-checked-width-locality-transcript-acceptance-packet",
            "Lean4/Lake command replay with returncode 0",
            "checked transcript hash and stdout/stderr hashes",
            "theorem scope statement",
            "open obligation ledger",
            "claim boundary that still forbids Quantum PCP, NLTS, global impossibility, and BQP separation claims",
        ],
    }
    boundary_packet["boundary_hash"] = stable_hash(boundary_packet)

    requirements = [
        requirement(
            "S1",
            "Source B9 checked transcript acceptance packet gate is present and current",
            source.get("method") == EXPECTED_METHOD
            and summary.get("acceptance_packet_id") == EXPECTED_ACCEPTANCE_PACKET_ID
            and summary.get("validation_error_count") == 0,
            {
                "source_method": source.get("method"),
                "acceptance_packet_id": summary.get("acceptance_packet_id"),
                "validation_error_count": summary.get("validation_error_count"),
            },
        ),
        requirement(
            "S2",
            "Source gate remains blocked on missing submitted acceptance packet only",
            summary.get("failed_acceptance_requirement_ids") == ["P6", "P7", "P8"]
            and summary.get("submitted_acceptance_packet_exists") is False,
            {
                "failed_acceptance_requirement_ids": summary.get("failed_acceptance_requirement_ids"),
                "submitted_acceptance_packet_exists": summary.get("submitted_acceptance_packet_exists"),
            },
        ),
        requirement(
            "S3",
            "Checked transcript and proof-assistant credit remain absent",
            summary.get("checked_transcript_present") is False
            and summary.get("checked_transcript_accepted") is False
            and summary.get("proof_assistant_checked") is False,
            {
                "checked_transcript_present": summary.get("checked_transcript_present"),
                "checked_transcript_accepted": summary.get("checked_transcript_accepted"),
                "proof_assistant_checked": summary.get("proof_assistant_checked"),
            },
        ),
        requirement(
            "S4",
            "Formal theorem, Quantum PCP, NLTS, and global impossibility claims remain forbidden",
            summary.get("formal_theorem_proved") is False
            and summary.get("explicit_not_quantum_pcp_proof") is True
            and summary.get("nlts_theorem_claimed") is False
            and summary.get("global_gap_amplification_impossibility_claimed") is False,
            {
                "formal_theorem_proved": summary.get("formal_theorem_proved"),
                "explicit_not_quantum_pcp_proof": summary.get("explicit_not_quantum_pcp_proof"),
                "nlts_theorem_claimed": summary.get("nlts_theorem_claimed"),
                "global_gap_amplification_impossibility_claimed": summary.get(
                    "global_gap_amplification_impossibility_claimed"
                ),
            },
        ),
        requirement(
            "S5",
            "B10 formal, Quantum PCP, NLTS, and BQP credit remain explicitly disabled",
            boundary_packet["b10_formal_credit_allowed"] is False
            and boundary_packet["b10_quantum_pcp_credit_allowed"] is False
            and boundary_packet["b10_nlts_credit_allowed"] is False
            and boundary_packet["b10_bqp_separation_credit_allowed"] is False,
            {
                "b10_formal_credit_allowed": boundary_packet["b10_formal_credit_allowed"],
                "b10_quantum_pcp_credit_allowed": boundary_packet["b10_quantum_pcp_credit_allowed"],
                "b10_nlts_credit_allowed": boundary_packet["b10_nlts_credit_allowed"],
                "b10_bqp_separation_credit_allowed": boundary_packet["b10_bqp_separation_credit_allowed"],
            },
        ),
        requirement(
            "S6",
            "B10 boundary packet records downstream evidence required before credit",
            len(boundary_packet["required_downstream_before_credit"]) == 8,
            {"required_downstream_before_credit": boundary_packet["required_downstream_before_credit"]},
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors = []
    if failed_ids:
        validation_errors.append(f"B10-T3 checked transcript boundary failed: {failed_ids}")

    payload_summary = {
        "boundary_id": boundary_packet["boundary_id"],
        "boundary_hash": boundary_packet["boundary_hash"],
        "source_acceptance_packet_hash": summary.get("acceptance_packet_hash"),
        "acceptance_packet_id": summary.get("acceptance_packet_id"),
        "packet_id": summary.get("packet_id"),
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "submitted_acceptance_packet_exists": summary.get("submitted_acceptance_packet_exists"),
        "checked_transcript_present": summary.get("checked_transcript_present"),
        "checked_transcript_accepted": summary.get("checked_transcript_accepted"),
        "proof_assistant_checked": summary.get("proof_assistant_checked"),
        "formal_theorem_proved": False,
        "explicit_not_quantum_pcp_proof": True,
        "nlts_theorem_claimed": False,
        "global_gap_amplification_impossibility_claimed": False,
        "b10_formal_credit_allowed": False,
        "b10_quantum_pcp_credit_allowed": False,
        "b10_nlts_credit_allowed": False,
        "b10_bqp_separation_credit_allowed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B10",
        "linked_benchmark_id": "B9",
        "source_target_id": "B10-T3",
        "title": "B10-T3 Checked Transcript Acceptance Boundary",
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
                "B10-T3 is now explicitly synchronized to the B9 checked transcript "
                "acceptance packet gate as the current formal zero-credit boundary."
            ),
            "what_is_not_supported": (
                "No checked transcript, proof-assistant checked theorem, Quantum PCP "
                "proof, NLTS theorem, global impossibility theorem, or BQP separation is supported."
            ),
            "next_gate": (
                "Submit the provenance manifest, replay-validation manifest, acceptance "
                "packet, Lean4/Lake checked transcript, theorem scope statement, open "
                "obligation ledger, and claim boundary before B10-T3 can leave zero-credit status."
            ),
            "b10_formal_credit_allowed": False,
            "b10_quantum_pcp_credit_allowed": False,
            "b10_nlts_credit_allowed": False,
            "b10_bqp_separation_credit_allowed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["boundary_packet"]
    lines = [
        "# B10-T3 Checked Transcript Acceptance Boundary",
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
        f"- Requirements passed/failed: `{summary['requirements_passed']}` / `{summary['requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_requirement_ids']}`",
        f"- Submitted acceptance packet exists: `{summary['submitted_acceptance_packet_exists']}`",
        f"- Checked transcript present/accepted: `{summary['checked_transcript_present']}` / `{summary['checked_transcript_accepted']}`",
        f"- Proof assistant checked: `{summary['proof_assistant_checked']}`",
        f"- B10 formal / Quantum PCP / NLTS / BQP credit allowed: `{summary['b10_formal_credit_allowed']}` / `{summary['b10_quantum_pcp_credit_allowed']}` / `{summary['b10_nlts_credit_allowed']}` / `{summary['b10_bqp_separation_credit_allowed']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Required Downstream Evidence Before Credit",
        "",
    ]
    for item in packet["required_downstream_before_credit"]:
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
            f"- b10_formal_credit_allowed: {payload['claim_boundary']['b10_formal_credit_allowed']}",
            f"- b10_quantum_pcp_credit_allowed: {payload['claim_boundary']['b10_quantum_pcp_credit_allowed']}",
            f"- b10_nlts_credit_allowed: {payload['claim_boundary']['b10_nlts_credit_allowed']}",
            f"- b10_bqp_separation_credit_allowed: {payload['claim_boundary']['b10_bqp_separation_credit_allowed']}",
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
        default=Path("results/B9_checked_transcript_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B10_T3_checked_transcript_acceptance_boundary_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B10_T3_checked_transcript_acceptance_boundary.md"),
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
