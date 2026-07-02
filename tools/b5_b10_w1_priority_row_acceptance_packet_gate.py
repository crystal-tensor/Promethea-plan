#!/usr/bin/env python3
"""T-B5-006s/T-B10-014o: W1 priority-row acceptance packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b5_b10_w1_priority_row_acceptance_packet_gate_v0"
STATUS = "w1_priority_row_acceptance_packet_open_missing_artifact"
MODEL_STATUS = "w1_priority_row_acceptance_packet_required_before_production_dmrg_or_b10_credit"
VERSION = "0.1"
EXPECTED_ROW_CONTRACT_HASH = "7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc"
EXPECTED_PRIORITY_ROW_ID = "D5H_s8_u2_eta0.25_n4x4_obs_density_site_4"
EXPECTED_PROVENANCE_MANIFEST_ID = "B5B10-W1-priority-row-provenance-manifest"
EXPECTED_REPLAY_MANIFEST_ID = "B5B10-W1-priority-row-replay-validation-manifest"
EXPECTED_ACCEPTANCE_PACKET_ID = "B5B10-W1-priority-row-acceptance-packet"
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
        "priority_row_id",
        "provenance_manifest_id",
        "replay_validation_manifest_id",
        "priority_packet_hash",
        "provenance_manifest_hash",
        "replay_validation_manifest_hash",
        "row_contract_hash",
        "canonical_state_replay_hash",
        "canonical_center_site",
        "left_environment_hash",
        "right_environment_hash",
        "orthonormal_residual_norm",
        "production_discarded_weight",
        "convergence_ledger_hash",
        "sweep_matvec_ledger_hash",
        "wall_clock_memory_ledger_hash",
        "seeded_pressure_comparison_hash",
        "same_access_cost_ledger_hash",
        "b10_access_boundary",
        "b10_access_boundary_hash",
        "accepted_priority_row_count",
        "production_contract_rows_accepted",
        "claim_boundary",
        "source_evidence_files_present",
    ]
    production_required_keys = [
        "replay_validation_manifest_hash",
        "row_contract_hash",
        "canonical_state_replay_hash",
        "canonical_center_site",
        "left_environment_hash",
        "right_environment_hash",
        "orthonormal_residual_norm",
        "production_discarded_weight",
        "convergence_ledger_hash",
        "sweep_matvec_ledger_hash",
        "wall_clock_memory_ledger_hash",
        "seeded_pressure_comparison_hash",
        "same_access_cost_ledger_hash",
        "b10_access_boundary",
        "b10_access_boundary_hash",
        "accepted_priority_row_count",
        "production_contract_rows_accepted",
        "claim_boundary",
    ]
    required_evidence_files = [
        "accepted_replay_validation_manifest",
        "priority_row_packet_contract",
        "accepted_provenance_manifest",
        "canonical_state_replay_manifest",
        "canonical_center_site_table",
        "left_environment_tensor_hash_manifest",
        "right_environment_tensor_hash_manifest",
        "orthonormal_residual_table",
        "discarded_weight_table",
        "convergence_ledger",
        "sweep_matvec_ledger",
        "wall_clock_memory_ledger",
        "seeded_pressure_comparison_manifest",
        "same_access_cost_ledger",
        "b10_access_boundary_note",
        "claim_boundary_note",
    ]

    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    manifest_bound = (
        submitted is not None
        and submitted.get("acceptance_packet_id") == EXPECTED_ACCEPTANCE_PACKET_ID
        and submitted.get("priority_row_id") == EXPECTED_PRIORITY_ROW_ID
        and submitted.get("provenance_manifest_id") == EXPECTED_PROVENANCE_MANIFEST_ID
        and submitted.get("replay_validation_manifest_id") == EXPECTED_REPLAY_MANIFEST_ID
        and submitted.get("priority_packet_hash") == priority_summary.get("packet_hash")
        and submitted.get("provenance_manifest_hash") == replay_summary.get("provenance_manifest_hash")
        and submitted.get("replay_validation_manifest_hash") == replay_summary.get("manifest_hash")
        and submitted.get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH
    )
    row_acceptance_valid = (
        submitted is not None
        and submitted.get("accepted_priority_row_count", 0) > 0
        and submitted.get("production_contract_rows_accepted", 0) > 0
        and isinstance(submitted.get("canonical_center_site"), int)
        and bool(submitted.get("left_environment_hash"))
        and bool(submitted.get("right_environment_hash"))
        and isinstance(submitted.get("orthonormal_residual_norm"), (int, float))
        and submitted.get("orthonormal_residual_norm") <= 1e-8
        and isinstance(submitted.get("production_discarded_weight"), (int, float))
    )
    b10_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("b10_access_boundary"), dict)
        and submitted["b10_access_boundary"].get("b10_t1_credit_allowed") is False
        and submitted["b10_access_boundary"].get("same_access_positive_route_claimed") is False
        and submitted["b10_access_boundary"].get("bqp_separation_claimed") is False
        and bool(submitted.get("b10_access_boundary_hash"))
    )
    claim_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("claim_boundary"), dict)
        and submitted["claim_boundary"].get("production_dmrg_claimed") is False
        and submitted["claim_boundary"].get("same_access_positive_route_claimed") is False
        and submitted["claim_boundary"].get("quantum_advantage_claimed") is False
        and submitted["claim_boundary"].get("bqp_separation_claimed") is False
    )
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True

    acceptance_packet = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "priority_row_id": EXPECTED_PRIORITY_ROW_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "replay_validation_manifest_id": EXPECTED_REPLAY_MANIFEST_ID,
        "source_replay_validation_manifest_gate": str(args.replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "submission_artifact_path": str(submission_path),
        "priority_packet_hash": priority_summary.get("packet_hash"),
        "provenance_manifest_hash": replay_summary.get("provenance_manifest_hash"),
        "replay_validation_manifest_hash": replay_summary.get("manifest_hash"),
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "row_contract_count": replay_summary.get("row_contract_count"),
        "prototype_trace_hash_rows": replay_summary.get("prototype_trace_hash_rows"),
        "prototype_discarded_weight_metric_rows": replay_summary.get(
            "prototype_discarded_weight_metric_rows"
        ),
        "production_contract_rows_accepted": replay_summary.get("production_contract_rows_accepted"),
        "required_keys": required_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": required_evidence_files,
        "accepted_only_if": [
            "acceptance_packet_id equals B5B10-W1-priority-row-acceptance-packet",
            "priority row, provenance manifest, replay-validation manifest, priority packet hash, and row-contract hash match the source gates",
            "canonical state replay, center site, left/right environment hashes, residual norm, discarded weight, convergence, sweep/matvec, wall-clock/memory, seeded-pressure, and same-access cost ledgers are hash-bound",
            "accepted_priority_row_count and production_contract_rows_accepted are positive only after source evidence exists",
            "orthonormal_residual_norm is at or below 1e-8 for the accepted priority row",
            "B10 access boundary remains zero-credit and explicitly denies same-access positive-route or BQP-separation credit",
            "claim_boundary forbids production DMRG, same-access positive route, quantum advantage, and BQP separation claims until a larger audited denominator route closes",
        ],
    }
    acceptance_packet["packet_hash"] = stable_hash(acceptance_packet)

    forbidden_claims = [
        "production_dmrg_claimed",
        "same_access_positive_route_claimed",
        "quantum_advantage_claimed",
        "bqp_separation_claimed",
    ]
    requirements = [
        requirement(
            "P1",
            "Replay-validation manifest gate remains valid and blocked only on P6/P7/P8",
            replay.get("method") == "b5_b10_w1_replay_validation_manifest_gate_v0"
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
            "Priority row packet remains fixed and source-shaped",
            priority.get("method") == "b5_b10_w1_priority_row_submission_packet_gate_v0"
            and priority_summary.get("priority_row_id") == EXPECTED_PRIORITY_ROW_ID
            and priority_summary.get("validation_error_count") == 0
            and priority_summary.get("failed_packet_requirement_ids") == EXPECTED_FAILED_IDS,
            {
                "priority_row_id": priority_summary.get("priority_row_id"),
                "packet_hash": priority_summary.get("packet_hash"),
                "failed_packet_requirement_ids": priority_summary.get("failed_packet_requirement_ids"),
            },
        ),
        requirement(
            "P3",
            "Acceptance packet carries locked W1 production-row schema and evidence classes",
            len(required_keys) == 25
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
            "Replay scope and prototype blockers remain preserved",
            replay_summary.get("row_contract_count") == 9
            and replay_summary.get("prototype_trace_hash_rows") == 9
            and replay_summary.get("prototype_discarded_weight_metric_rows") == 9
            and replay_summary.get("production_contract_rows_accepted") == 0,
            {
                "row_contract_count": replay_summary.get("row_contract_count"),
                "prototype_trace_hash_rows": replay_summary.get("prototype_trace_hash_rows"),
                "prototype_discarded_weight_metric_rows": replay_summary.get(
                    "prototype_discarded_weight_metric_rows"
                ),
                "production_contract_rows_accepted": replay_summary.get("production_contract_rows_accepted"),
            },
        ),
        requirement(
            "P5",
            "Current state has no accepted priority row or forbidden claims",
            replay_summary.get("accepted_priority_row_count") == 0
            and replay_summary.get("b10_t1_positive_route_ready") is False
            and all(replay_summary.get(key) is False for key in forbidden_claims),
            {
                "accepted_priority_row_count": replay_summary.get("accepted_priority_row_count"),
                "b10_t1_positive_route_ready": replay_summary.get("b10_t1_positive_route_ready"),
                **{key: replay_summary.get(key) for key in forbidden_claims},
            },
        ),
        requirement(
            "P6",
            "Priority-row acceptance packet has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted acceptance packet satisfies the locked W1 production-row schema",
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
            "Submitted acceptance packet is source-backed, manifest-bound, row-valid, B10-boundary-bound, and claim-boundary-bound",
            source_backed
            and manifest_bound
            and row_acceptance_valid
            and b10_boundary_bound
            and claim_boundary_bound,
            {
                "source_backed": source_backed,
                "manifest_bound": manifest_bound,
                "row_acceptance_valid": row_acceptance_valid,
                "b10_boundary_bound": b10_boundary_bound,
                "claim_boundary_bound": claim_boundary_bound,
            },
        ),
        requirement(
            "P9",
            "Forbidden production, positive-route, advantage, and BQP claims remain false",
            replay_summary.get("b10_t1_positive_route_ready") is False
            and all(replay_summary.get(key) is False for key in forbidden_claims),
            {
                "b10_t1_positive_route_ready": replay_summary.get("b10_t1_positive_route_ready"),
                **{key: replay_summary.get(key) for key in forbidden_claims},
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected W1 priority-row acceptance failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted acceptance packet until a solver PR supplies one")

    summary = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "priority_row_id": EXPECTED_PRIORITY_ROW_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "replay_validation_manifest_id": EXPECTED_REPLAY_MANIFEST_ID,
        "priority_packet_hash": priority_summary.get("packet_hash"),
        "provenance_manifest_hash": replay_summary.get("provenance_manifest_hash"),
        "replay_validation_manifest_hash": replay_summary.get("manifest_hash"),
        "acceptance_packet_hash": acceptance_packet["packet_hash"],
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "acceptance_requirement_count": len(requirements),
        "acceptance_requirements_passed": passed,
        "acceptance_requirements_failed": len(requirements) - passed,
        "failed_acceptance_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(required_evidence_files),
        "row_contract_count": replay_summary.get("row_contract_count"),
        "prototype_trace_hash_rows": replay_summary.get("prototype_trace_hash_rows"),
        "prototype_discarded_weight_metric_rows": replay_summary.get(
            "prototype_discarded_weight_metric_rows"
        ),
        "production_contract_rows_accepted": replay_summary.get("production_contract_rows_accepted"),
        "submitted_acceptance_packet_exists": submitted_exists,
        "submitted_key_count": len(submitted) if submitted else 0,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "accepted_priority_row_count": 0,
        "b10_t1_positive_route_ready": False,
        "production_dmrg_claimed": False,
        "same_access_positive_route_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B5",
        "linked_benchmark_id": "B10",
        "source_target_id": "B10-T1",
        "dependency_benchmarks": ["B5", "B10"],
        "title": "B5/B10 W1 Priority-Row Acceptance Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_replay_validation_manifest_gate": str(args.replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "summary": summary,
        "priority_row_acceptance_packet": acceptance_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The B5/B10 W1 route now has a priority-row acceptance packet defining what the first "
                "source-backed production-row artifact must contain before it can count."
            ),
            "what_is_not_supported": (
                "No priority-row acceptance packet or production row has been submitted or accepted; no "
                "production DMRG denominator, same-access positive route, quantum advantage, or BQP "
                "separation is supported."
            ),
            "next_gate": (
                "Submit B5B10-W1-priority-row-acceptance-packet with the accepted replay-validation "
                "manifest hash, canonical center and environment hashes, residual and discarded-weight "
                "evidence, convergence and resource ledgers, seeded-pressure comparison, same-access cost "
                "ledger, B10 access boundary, and claim boundary."
            ),
            "production_dmrg_claimed": False,
            "same_access_positive_route_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["priority_row_acceptance_packet"]
    lines = [
        "# B5/B10 W1 Priority-Row Acceptance Packet Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Acceptance packet: `{summary['acceptance_packet_id']}`",
        f"- Priority row: `{summary['priority_row_id']}`",
        f"- Replay-validation manifest: `{summary['replay_validation_manifest_id']}`",
        f"- Replay-validation manifest hash: `{summary['replay_validation_manifest_hash']}`",
        f"- Priority packet hash: `{summary['priority_packet_hash']}`",
        f"- Acceptance packet hash: `{summary['acceptance_packet_hash']}`",
        f"- Row contract hash: `{summary['row_contract_hash']}`",
        f"- Requirements passed/failed: `{summary['acceptance_requirements_passed']}` / `{summary['acceptance_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_acceptance_requirement_ids']}`",
        f"- Required key / production key / evidence file count: `{summary['required_key_count']}` / `{summary['production_required_key_count']}` / `{summary['required_evidence_file_count']}`",
        f"- Row contracts / prototype trace hashes / discarded-weight metric rows: `{summary['row_contract_count']}` / `{summary['prototype_trace_hash_rows']}` / `{summary['prototype_discarded_weight_metric_rows']}`",
        f"- Production contract rows accepted: `{summary['production_contract_rows_accepted']}`",
        f"- Submitted acceptance packet exists: `{summary['submitted_acceptance_packet_exists']}`",
        f"- Accepted priority rows: `{summary['accepted_priority_row_count']}`",
        f"- B10-T1 positive route ready: `{summary['b10_t1_positive_route_ready']}`",
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
            f"- production_dmrg_claimed: {payload['claim_boundary']['production_dmrg_claimed']}",
            f"- same_access_positive_route_claimed: {payload['claim_boundary']['same_access_positive_route_claimed']}",
            f"- quantum_advantage_claimed: {payload['claim_boundary']['quantum_advantage_claimed']}",
            f"- bqp_separation_claimed: {payload['claim_boundary']['bqp_separation_claimed']}",
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
        default=Path("results/B5_B10_w1_replay_validation_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B5_B10_w1_priority_row_submission_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B5_B10_w1_priority_row_acceptance_packet_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B5_B10_w1_priority_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B5_B10_w1_priority_row_acceptance_packet_gate.md"),
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
