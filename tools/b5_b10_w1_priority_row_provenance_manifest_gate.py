#!/usr/bin/env python3
"""T-B5-006o/T-B10-014m: W1 priority-row provenance manifest gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b5_b10_w1_priority_row_provenance_manifest_gate_v0"
STATUS = "w1_priority_row_provenance_manifest_open_missing_artifact"
MODEL_STATUS = "priority_row_provenance_manifest_required_before_production_row_acceptance"
VERSION = "0.1"
EXPECTED_ROW_CONTRACT_HASH = "7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc"
EXPECTED_PRIORITY_ROW_ID = "D5H_s8_u2_eta0.25_n4x4_obs_density_site_4"
EXPECTED_MANIFEST_ID = "B5B10-W1-priority-row-provenance-manifest"
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
    priority = load_json(args.priority_packet_gate)
    summary = priority["summary"]
    packet = priority["priority_row_submission_packet"]
    submission_path = args.submission_dir / f"{EXPECTED_MANIFEST_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None

    required_manifest_keys = [
        "manifest_id",
        "row_id",
        "row_contract_hash",
        "priority_packet_hash",
        "template_hash",
        "prototype_trace_hash",
        "canonical_state_manifest_hash",
        "environment_hash_source_manifest",
        "residual_protocol_hash",
        "discarded_weight_protocol_hash",
        "cost_ledger_protocol_hash",
        "same_access_replay_hashes",
        "claim_boundary",
    ]
    production_manifest_keys = [
        "canonical_state_manifest_hash",
        "environment_hash_source_manifest",
        "residual_protocol_hash",
        "discarded_weight_protocol_hash",
        "cost_ledger_protocol_hash",
        "same_access_replay_hashes",
    ]
    required_evidence_files = [
        "canonical_state_manifest_source",
        "left_environment_hash_source",
        "right_environment_hash_source",
        "orthonormal_residual_protocol_note",
        "discarded_weight_protocol_note",
        "wall_clock_memory_measurement_note",
        "sweep_or_matvec_count_note",
        "same_access_replay_command_manifest",
        "row_contract_hash_replay_note",
        "claim_boundary_note",
    ]

    missing_keys = [key for key in required_manifest_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_manifest_keys if submitted is not None and submitted.get(key) is not None
    ]
    replay_hashes = submitted.get("same_access_replay_hashes") if submitted else None
    replay_bound = (
        isinstance(replay_hashes, dict)
        and replay_hashes.get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH
        and replay_hashes.get("priority_packet_hash") == summary.get("packet_hash")
        and replay_hashes.get("template_hash") == packet.get("template_hash")
    )
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True
    row_bound = (
        submitted is not None
        and submitted.get("manifest_id") == EXPECTED_MANIFEST_ID
        and submitted.get("row_id") == EXPECTED_PRIORITY_ROW_ID
        and submitted.get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH
        and submitted.get("priority_packet_hash") == summary.get("packet_hash")
        and submitted.get("template_hash") == packet.get("template_hash")
        and submitted.get("prototype_trace_hash") == packet.get("prototype_trace_hash")
    )

    manifest_packet = {
        "manifest_id": EXPECTED_MANIFEST_ID,
        "row_id": EXPECTED_PRIORITY_ROW_ID,
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "submission_artifact_path": str(submission_path),
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "priority_packet_hash": summary.get("packet_hash"),
        "template_hash": packet.get("template_hash"),
        "prototype_trace_hash": packet.get("prototype_trace_hash"),
        "prototype_values_are_provenance_only": True,
        "required_manifest_keys": required_manifest_keys,
        "production_manifest_keys": production_manifest_keys,
        "required_evidence_files": required_evidence_files,
        "accepted_only_if": [
            "manifest_id equals B5B10-W1-priority-row-provenance-manifest",
            "row_id equals D5H_s8_u2_eta0.25_n4x4_obs_density_site_4",
            "row_contract_hash, priority_packet_hash, template_hash, and prototype_trace_hash match the source priority packet",
            "canonical-state, environment-source, residual, discarded-weight, cost-ledger, and replay protocol hashes are present",
            "same_access_replay_hashes bind row_contract_hash, priority_packet_hash, and template_hash",
            "source evidence files are present and hash-bound",
            "claim_boundary forbids production-DMRG, positive-route, quantum-advantage, and BQP-separation claims",
        ],
    }
    manifest_packet["manifest_hash"] = stable_hash(manifest_packet)

    forbidden_claims = [
        "production_dmrg_claimed",
        "same_access_positive_route_claimed",
        "quantum_advantage_claimed",
        "bqp_separation_claimed",
    ]
    requirements = [
        requirement(
            "P1",
            "Priority-row submission packet remains valid and blocked only on P6/P7/P8",
            priority.get("method") == "b5_b10_w1_priority_row_submission_packet_gate_v0"
            and summary.get("validation_error_count") == 0
            and summary.get("failed_packet_requirement_ids") == ["P6", "P7", "P8"],
            {
                "source_status": priority.get("status"),
                "failed_packet_requirement_ids": summary.get("failed_packet_requirement_ids"),
                "validation_error_count": summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Priority row and locked W1 row contract are preserved",
            summary.get("priority_row_id") == EXPECTED_PRIORITY_ROW_ID
            and summary.get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH,
            {
                "priority_row_id": summary.get("priority_row_id"),
                "row_contract_hash": summary.get("row_contract_hash"),
            },
        ),
        requirement(
            "P3",
            "Manifest packet carries locked provenance schema and evidence file classes",
            len(required_manifest_keys) == 13
            and len(production_manifest_keys) == 6
            and len(required_evidence_files) == 10,
            {
                "required_manifest_key_count": len(required_manifest_keys),
                "production_manifest_key_count": len(production_manifest_keys),
                "required_evidence_file_count": len(required_evidence_files),
            },
        ),
        requirement(
            "P4",
            "Priority-row schema, production keys, and evidence classes remain preserved",
            summary.get("required_row_key_count") == 17
            and summary.get("production_required_key_count") == 8
            and summary.get("required_evidence_file_count") == 8,
            {
                "required_row_key_count": summary.get("required_row_key_count"),
                "production_required_key_count": summary.get("production_required_key_count"),
                "required_evidence_file_count": summary.get("required_evidence_file_count"),
            },
        ),
        requirement(
            "P5",
            "Current state has no accepted priority row or production route credit",
            summary.get("accepted_priority_row_count") == 0
            and summary.get("submitted_artifact_exists") is False
            and all(summary.get(key) is False for key in forbidden_claims),
            {
                "accepted_priority_row_count": summary.get("accepted_priority_row_count"),
                "submitted_artifact_exists": summary.get("submitted_artifact_exists"),
                **{key: summary.get(key) for key in forbidden_claims},
            },
        ),
        requirement(
            "P6",
            "Provenance manifest artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted manifest satisfies the locked provenance schema",
            submitted_exists and not missing_keys and len(production_present) == len(production_manifest_keys),
            {
                "missing_keys": missing_keys,
                "production_keys_present": production_present,
                "production_manifest_keys": production_manifest_keys,
                "submitted_key_count": len(submitted) if submitted else 0,
            },
        ),
        requirement(
            "P8",
            "Submitted manifest is source-backed, row-bound, and replay-hash-bound",
            source_backed and row_bound and replay_bound,
            {
                "source_evidence_files_present": source_backed,
                "row_bound": row_bound,
                "replay_bound": replay_bound,
            },
        ),
        requirement(
            "P9",
            "Forbidden production, positive-route, advantage, and BQP claims remain false",
            all(summary.get(key) is False for key in forbidden_claims),
            {key: summary.get(key) for key in forbidden_claims},
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected provenance manifest failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted provenance manifest until a solver PR supplies one")

    payload_summary = {
        "manifest_id": EXPECTED_MANIFEST_ID,
        "priority_row_id": EXPECTED_PRIORITY_ROW_ID,
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "priority_packet_hash": summary.get("packet_hash"),
        "manifest_hash": manifest_packet["manifest_hash"],
        "manifest_requirement_count": len(requirements),
        "manifest_requirements_passed": passed,
        "manifest_requirements_failed": len(requirements) - passed,
        "failed_manifest_requirement_ids": failed_ids,
        "required_manifest_key_count": len(required_manifest_keys),
        "production_manifest_key_count": len(production_manifest_keys),
        "required_evidence_file_count": len(required_evidence_files),
        "priority_required_row_key_count": summary.get("required_row_key_count"),
        "priority_production_required_key_count": summary.get("production_required_key_count"),
        "submitted_manifest_exists": submitted_exists,
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
        "title": "B5/B10 W1 Priority Row Provenance Manifest Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "summary": payload_summary,
        "provenance_manifest_packet": manifest_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The first B5/B10 W1 production-row obligation now has a pre-row provenance "
                "manifest packet that must bind state, environment, residual, discarded-weight, "
                "cost-ledger, and replay evidence before any priority row can be accepted."
            ),
            "what_is_not_supported": (
                "No provenance manifest or priority production row has been submitted or accepted; "
                "no production DMRG denominator, same-access positive route, quantum advantage, "
                "or BQP separation is supported."
            ),
            "next_gate": (
                f"Submit {submission_path} before the priority-row JSON artifact, then rerun this "
                "gate and the priority-row submission gate."
            ),
            "production_dmrg_claimed": False,
            "same_access_positive_route_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["provenance_manifest_packet"]
    lines = [
        "# B5/B10 W1 Priority Row Provenance Manifest Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Manifest: `{summary['manifest_id']}`",
        f"- Priority row: `{summary['priority_row_id']}`",
        f"- Manifest hash: `{summary['manifest_hash']}`",
        f"- Requirements passed/failed: `{summary['manifest_requirements_passed']}` / `{summary['manifest_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_manifest_requirement_ids']}`",
        f"- Required manifest keys / production manifest keys / evidence files: `{summary['required_manifest_key_count']}` / `{summary['production_manifest_key_count']}` / `{summary['required_evidence_file_count']}`",
        f"- Priority row schema keys / production keys: `{summary['priority_required_row_key_count']}` / `{summary['priority_production_required_key_count']}`",
        f"- Submitted manifest exists: `{summary['submitted_manifest_exists']}`",
        f"- Accepted priority rows: `{summary['accepted_priority_row_count']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Provenance Manifest Packet",
        "",
        f"- Submission path: `{packet['submission_artifact_path']}`",
        f"- Row contract hash: `{packet['row_contract_hash']}`",
        f"- Priority packet hash: `{packet['priority_packet_hash']}`",
        f"- Template hash: `{packet['template_hash']}`",
        f"- Prototype trace hash: `{packet['prototype_trace_hash']}`",
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
    for item in payload["requirements"]:
        state = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {item['requirement_id']} [{state}]: {item['label']}")
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
        lines.extend(f"- {error}" for error in payload["validation_errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B5_B10_w1_priority_row_submission_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B5_B10_w1_priority_row_provenance_manifest_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B5_B10_w1_priority_row_provenance_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B5_B10_w1_priority_row_provenance_manifest_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-02")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    write_markdown(payload, args.markdown_output)
    print(json.dumps(payload["summary"], indent=2 if args.pretty else None, sort_keys=True))
    if payload["validation_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
