#!/usr/bin/env python3
"""T-B3-022/T-B10-015i: F1 full-covariance row packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b3_b10_f1_full_covariance_row_packet_gate_v0"
STATUS = "f1_full_covariance_row_packet_open_missing_artifact"
MODEL_STATUS = "f1_full_compiled_state_covariance_row_contract_ready_no_credit"
VERSION = "0.1"
EXPECTED_PACKET_ID = "B3B10-F1-full-compiled-state-covariance-rows"
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
    triage = load_json(args.post_boundary_triage)
    acceptance = load_json(args.row_acceptance_gate)
    priority = load_json(args.priority_packet_gate)
    provenance = load_json(args.provenance_manifest_gate)
    triage_summary = triage["summary"]
    acceptance_summary = acceptance["summary"]
    priority_summary = priority["summary"]
    provenance_summary = provenance["summary"]
    submission_path = args.submission_dir / f"{EXPECTED_PACKET_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None

    required_keys = [
        "packet_id",
        "source_triage_id",
        "source_priority_packet_id",
        "source_provenance_manifest_id",
        "downstream_packet_id",
        "row_aligned_instance_ids",
        "compiled_state_replay_hashes",
        "full_covariance_matrix_hashes",
        "qwc_group_manifest_hashes",
        "shot_allocation_or_exact_covariance_mode",
        "stateprep_circuit_hashes",
        "measurement_replay_command_hash",
        "derivative_propagation_manifest_hash",
        "same_access_denominator_contract_hash",
        "optimizer_loop_cost_ledger_hash",
        "claim_boundary",
    ]
    production_required_keys = [
        "row_aligned_instance_ids",
        "compiled_state_replay_hashes",
        "full_covariance_matrix_hashes",
        "qwc_group_manifest_hashes",
        "shot_allocation_or_exact_covariance_mode",
        "stateprep_circuit_hashes",
        "measurement_replay_command_hash",
        "derivative_propagation_manifest_hash",
        "claim_boundary",
    ]
    required_evidence_files = [
        "row_manifest",
        "compiled_state_replay_bundle",
        "full_covariance_matrix_bundle",
        "qwc_group_manifest",
        "shot_allocation_or_exact_covariance_note",
        "stateprep_circuit_manifest",
        "measurement_replay_transcript",
        "derivative_propagation_manifest",
        "same_access_denominator_contract",
        "optimizer_loop_cost_ledger",
        "claim_boundary_note",
    ]

    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True
    downstream_bound = submitted is not None and submitted.get("downstream_packet_id") == EXPECTED_DOWNSTREAM_PACKET_ID
    row_scope_valid = (
        submitted is not None
        and isinstance(submitted.get("row_aligned_instance_ids"), list)
        and len(submitted["row_aligned_instance_ids"]) == triage_summary.get("row_aligned_instance_count")
    )
    provenance_bound = (
        submitted is not None
        and submitted.get("source_provenance_manifest_hash") == provenance_summary.get("manifest_hash")
    )

    f1_packet = {
        "packet_id": EXPECTED_PACKET_ID,
        "work_packet_id": "F1",
        "source_post_boundary_triage": str(args.post_boundary_triage),
        "source_row_acceptance_gate": str(args.row_acceptance_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "source_provenance_manifest_gate": str(args.provenance_manifest_gate),
        "source_triage_hash": triage_summary.get("triage_hash"),
        "source_acceptance_packet_hash": acceptance_summary.get("acceptance_packet_hash"),
        "source_priority_packet_hash": priority_summary.get("packet_hash"),
        "source_provenance_manifest_hash": provenance_summary.get("manifest_hash"),
        "downstream_packet_id": EXPECTED_DOWNSTREAM_PACKET_ID,
        "submission_artifact_path": str(submission_path),
        "required_keys": required_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": required_evidence_files,
        "accepted_only_if": [
            "packet_id equals B3B10-F1-full-compiled-state-covariance-rows",
            "downstream_packet_id equals B3-R1-full-compiled-covariance",
            "four row_aligned_instance_ids are supplied for the current B3/B10 reopen scope",
            "compiled state replay hashes and full covariance matrix hashes are source-backed",
            "QWC group manifests, state-prep circuit hashes, measurement replay commands, derivative propagation, denominator contract, and optimizer-loop cost ledger are present",
            "source_provenance_manifest_hash matches the accepted provenance-manifest gate hash",
            "claim_boundary forbids reaction-dynamics solution, quantum advantage, B3 reopen credit, B10-T1 credit, and BQP separation claims",
        ],
        "locked_scope": {
            "row_aligned_instance_count": triage_summary.get("row_aligned_instance_count"),
            "compiled_pilot_instance_count": triage_summary.get("compiled_pilot_instance_count"),
            "max_optimizer_loop_total_shots_lower_bound": triage_summary.get(
                "max_optimizer_loop_total_shots_lower_bound"
            ),
        },
    }
    f1_packet["packet_hash"] = stable_hash(f1_packet)

    requirements = [
        requirement(
            "P1",
            "Post-boundary triage is valid and exposes F1 as a ready PR packet",
            triage.get("method") == "b3_b10_full_covariance_post_boundary_submission_triage_v0"
            and triage_summary.get("validation_error_count") == 0
            and "F1" in triage_summary.get("ready_packet_ids", []),
            {
                "source_method": triage.get("method"),
                "ready_packet_ids": triage_summary.get("ready_packet_ids"),
                "validation_error_count": triage_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "F5 B10 access replay remains blocked while accepted rows and denominator wins are zero",
            triage_summary.get("blocked_packet_ids") == ["F5"]
            and triage_summary.get("accepted_full_covariance_row_count") == 0
            and triage_summary.get("denominator_win_count") == 0
            and triage_summary.get("b10_t1_credit_allowed") is False,
            {
                "blocked_packet_ids": triage_summary.get("blocked_packet_ids"),
                "accepted_full_covariance_row_count": triage_summary.get(
                    "accepted_full_covariance_row_count"
                ),
                "denominator_win_count": triage_summary.get("denominator_win_count"),
                "b10_t1_credit_allowed": triage_summary.get("b10_t1_credit_allowed"),
            },
        ),
        requirement(
            "P3",
            "Existing row acceptance gate remains the F1 source and is open on P6/P7/P8",
            acceptance.get("method") == "b3_b10_full_covariance_row_acceptance_packet_gate_v0"
            and acceptance_summary.get("failed_acceptance_requirement_ids") == EXPECTED_FAILED_IDS
            and acceptance_summary.get("submitted_acceptance_packet_exists") is False,
            {
                "source_method": acceptance.get("method"),
                "failed_acceptance_requirement_ids": acceptance_summary.get(
                    "failed_acceptance_requirement_ids"
                ),
                "acceptance_packet_hash": acceptance_summary.get("acceptance_packet_hash"),
            },
        ),
        requirement(
            "P4",
            "Locked B3/B10 full-covariance scope is preserved",
            triage_summary.get("row_aligned_instance_count") == 4
            and triage_summary.get("compiled_pilot_instance_count") == 1
            and triage_summary.get("max_optimizer_loop_total_shots_lower_bound") == 475043013690000,
            {
                "row_aligned_instance_count": triage_summary.get("row_aligned_instance_count"),
                "compiled_pilot_instance_count": triage_summary.get("compiled_pilot_instance_count"),
                "max_optimizer_loop_total_shots_lower_bound": triage_summary.get(
                    "max_optimizer_loop_total_shots_lower_bound"
                ),
            },
        ),
        requirement(
            "P5",
            "F1 packet schema and evidence classes are locked",
            len(required_keys) == 16
            and len(production_required_keys) == 9
            and len(required_evidence_files) == 11,
            {
                "required_key_count": len(required_keys),
                "production_required_key_count": len(production_required_keys),
                "required_evidence_file_count": len(required_evidence_files),
            },
        ),
        requirement(
            "P6",
            "F1 full-covariance row artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted F1 row artifact satisfies the locked schema",
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
            "Submitted F1 row artifact is source-backed, downstream-bound, provenance-bound, and row-scope valid",
            source_backed and downstream_bound and provenance_bound and row_scope_valid,
            {
                "source_evidence_files_present": source_backed,
                "downstream_bound": downstream_bound,
                "provenance_bound": provenance_bound,
                "row_scope_valid": row_scope_valid,
            },
        ),
        requirement(
            "P9",
            "Forbidden B3/B10 reaction, advantage, reopen, credit, and BQP claims remain false",
            triage_summary.get("reaction_dynamics_solution_claimed") is False
            and triage_summary.get("quantum_advantage_claimed") is False
            and triage_summary.get("bqp_separation_claimed") is False
            and triage_summary.get("b3_reopen_ready") is False
            and triage_summary.get("b10_t1_credit_allowed") is False,
            {
                "reaction_dynamics_solution_claimed": triage_summary.get(
                    "reaction_dynamics_solution_claimed"
                ),
                "quantum_advantage_claimed": triage_summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": triage_summary.get("bqp_separation_claimed"),
                "b3_reopen_ready": triage_summary.get("b3_reopen_ready"),
                "b10_t1_credit_allowed": triage_summary.get("b10_t1_credit_allowed"),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected F1 row packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted F1 full-covariance artifact until a chemistry PR supplies one")

    summary = {
        "f1_packet_id": EXPECTED_PACKET_ID,
        "f1_packet_hash": f1_packet["packet_hash"],
        "source_triage_hash": triage_summary.get("triage_hash"),
        "source_acceptance_packet_hash": acceptance_summary.get("acceptance_packet_hash"),
        "source_priority_packet_hash": priority_summary.get("packet_hash"),
        "source_provenance_manifest_hash": provenance_summary.get("manifest_hash"),
        "downstream_packet_id": EXPECTED_DOWNSTREAM_PACKET_ID,
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(required_evidence_files),
        "row_aligned_instance_count": triage_summary.get("row_aligned_instance_count"),
        "compiled_pilot_instance_count": triage_summary.get("compiled_pilot_instance_count"),
        "accepted_full_covariance_row_count": triage_summary.get(
            "accepted_full_covariance_row_count"
        ),
        "denominator_win_count": triage_summary.get("denominator_win_count"),
        "max_optimizer_loop_total_shots_lower_bound": triage_summary.get(
            "max_optimizer_loop_total_shots_lower_bound"
        ),
        "submitted_f1_artifact_exists": submitted_exists,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "f1_full_covariance_rows_accepted": False,
        "b3_reopen_ready": False,
        "b3_full_covariance_credit_allowed": False,
        "b10_t1_credit_allowed": False,
        "reaction_dynamics_solution_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B3",
        "linked_benchmark_id": "B10",
        "source_target_id": "T-B3-022/T-B10-015i",
        "title": "B3/B10 F1 Full-Covariance Row Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_post_boundary_triage": str(args.post_boundary_triage),
        "source_row_acceptance_gate": str(args.row_acceptance_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "source_provenance_manifest_gate": str(args.provenance_manifest_gate),
        "summary": summary,
        "f1_row_packet": f1_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": "F1 now has a locked full compiled-state covariance row packet schema and acceptance boundary.",
            "what_is_not_supported": "No F1 row artifact, accepted full-covariance row, denominator win, B3 reopen credit, B10-T1 credit, reaction-dynamics solution, quantum advantage, or BQP separation is supported.",
            "next_gate": "Submit the F1 row artifact with four source-backed full compiled-state covariance rows, compiled-state replay, covariance matrices, QWC group manifests, state-prep circuit hashes, measurement replay, derivative propagation, denominator contract, optimizer-loop ledger, and claim boundary.",
            "reaction_dynamics_solution_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "b3_reopen_ready": False,
            "b10_t1_credit_allowed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    p = payload["f1_row_packet"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- F1 packet: `{s['f1_packet_id']}`",
        f"- F1 packet hash: `{s['f1_packet_hash']}`",
        f"- Source triage hash: `{s['source_triage_hash']}`",
        f"- Source acceptance packet hash: `{s['source_acceptance_packet_hash']}`",
        "",
        "## Result",
        "",
        (
            f"The F1 gate passes {s['requirements_passed']}/{s['requirement_count']} "
            f"requirements and intentionally fails {s['failed_requirement_ids']} because no "
            "source-backed full compiled-state covariance row artifact has been submitted."
        ),
        "",
        "## Locked F1 Packet",
        "",
        f"- Submission path: `{p['submission_artifact_path']}`",
        f"- Required keys: `{s['required_key_count']}`",
        f"- Production required keys: `{s['production_required_key_count']}`",
        f"- Evidence file classes: `{s['required_evidence_file_count']}`",
        "",
        "Required evidence files:",
        "",
    ]
    for item in p["required_evidence_files"]:
        lines.append(f"- {item}")
    lines.extend(["", "Acceptance predicates:", ""])
    for item in p["accepted_only_if"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            f"- Downstream packet: `{s['downstream_packet_id']}`",
            f"- Row-aligned instances / compiled pilot: `{s['row_aligned_instance_count']}` / `{s['compiled_pilot_instance_count']}`",
            f"- Accepted full-covariance rows: `{s['accepted_full_covariance_row_count']}`",
            f"- Denominator wins: `{s['denominator_win_count']}`",
            f"- Optimizer-loop lower-bound shots: `{s['max_optimizer_loop_total_shots_lower_bound']}`",
            f"- F1 accepted: `{s['f1_full_covariance_rows_accepted']}`",
            f"- B3 reopen / B10-T1 credit: `{s['b3_reopen_ready']}` / `{s['b10_t1_credit_allowed']}`",
            "",
            "## Requirement Results",
            "",
        ]
    )
    for row in payload["requirements"]:
        marker = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- `{row['requirement_id']}` {marker}: {row['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            "This packet gate does not claim a reaction-dynamics solution, quantum advantage, B3 reopen credit, B10-T1 credit, or BQP separation.",
            "",
            "## Validation",
            "",
            f"- validation_error_count: `{s['validation_error_count']}`",
        ]
    )
    for error in payload["validation_errors"]:
        lines.append(f"- {error}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--post-boundary-triage",
        type=Path,
        default=Path("results/B3_B10_full_covariance_post_boundary_submission_triage_v0.json"),
    )
    parser.add_argument(
        "--row-acceptance-gate",
        type=Path,
        default=Path("results/B3_B10_full_covariance_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B3_B10_reopen_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--provenance-manifest-gate",
        type=Path,
        default=Path("results/B3_B10_full_covariance_provenance_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B3_B10_F1_full_covariance_row_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_B10_F1_full_covariance_row_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_B10_F1_full_covariance_row_packet_gate.md"),
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
                "f1_packet_hash": payload["summary"]["f1_packet_hash"],
                "requirements_passed": payload["summary"]["requirements_passed"],
                "requirements_failed": payload["summary"]["requirements_failed"],
                "failed_requirement_ids": payload["summary"]["failed_requirement_ids"],
                "validation_error_count": payload["summary"]["validation_error_count"],
                "json_output": str(args.json_output),
                "markdown_output": str(args.markdown_output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B3/B10 F1 full-covariance row packet gate validation failed")


if __name__ == "__main__":
    main()
