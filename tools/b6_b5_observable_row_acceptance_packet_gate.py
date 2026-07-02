#!/usr/bin/env python3
"""T-B6-005k/T-B5-006t: DFT/B5 observable row acceptance packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b6_b5_observable_row_acceptance_packet_gate_v0"
STATUS = "observable_row_acceptance_packet_open_missing_artifact"
MODEL_STATUS = "observable_row_acceptance_packet_required_before_dft_b5_row_credit"
VERSION = "0.1"
EXPECTED_ACCEPTANCE_PACKET_ID = "B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet"
EXPECTED_ROW_REPLAY_MANIFEST_ID = "B6B5-O1-monolayer-FeSe-STO-row-replay-validation-manifest"
EXPECTED_REPLAY_MANIFEST_ID = "B6B5-O1-monolayer-FeSe-STO-replay-validation-manifest"
EXPECTED_PROVENANCE_MANIFEST_ID = "B6B5-O1-monolayer-FeSe-STO-provenance-manifest"
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
    row_replay = load_json(args.row_replay_validation_manifest_gate)
    priority = load_json(args.priority_packet_gate)
    row_summary = row_replay["summary"]
    priority_summary = priority["summary"]
    submission_path = args.submission_dir / f"{EXPECTED_ACCEPTANCE_PACKET_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None

    required_keys = [
        "acceptance_packet_id",
        "material_id",
        "provenance_manifest_id",
        "replay_validation_manifest_id",
        "row_replay_validation_manifest_id",
        "priority_packet_hash",
        "provenance_manifest_hash",
        "replay_validation_manifest_hash",
        "row_replay_validation_manifest_hash",
        "source_formula_hash",
        "structure_input_hash",
        "dft_input_deck_hash",
        "dft_output_bundle_hash",
        "observable_table_hash",
        "b5_correlation_observable_hash",
        "negative_control_replay_hash",
        "leakage_guardrail_hash",
        "family_prior_denominator_hash",
        "same_access_cost_ledger_hash",
        "row_acceptance_ledger_hash",
        "accepted_dft_b5_row_count",
        "top_post_rank",
        "negative_control_topk_count",
        "material_family_count",
        "source_record_count",
        "b5_mechanism_boundary",
        "claim_boundary",
        "source_evidence_files_present",
    ]
    production_required_keys = [
        "row_replay_validation_manifest_hash",
        "source_formula_hash",
        "structure_input_hash",
        "dft_input_deck_hash",
        "dft_output_bundle_hash",
        "observable_table_hash",
        "b5_correlation_observable_hash",
        "negative_control_replay_hash",
        "leakage_guardrail_hash",
        "family_prior_denominator_hash",
        "same_access_cost_ledger_hash",
        "row_acceptance_ledger_hash",
        "accepted_dft_b5_row_count",
        "top_post_rank",
        "negative_control_topk_count",
        "material_family_count",
        "source_record_count",
        "b5_mechanism_boundary",
        "claim_boundary",
    ]
    evidence_files = [
        "accepted_row_replay_validation_manifest",
        "priority_observable_packet",
        "accepted_provenance_manifest",
        "accepted_replay_validation_manifest",
        "source_formula_manifest",
        "structure_input_artifact",
        "dft_input_deck_manifest",
        "dft_output_bundle",
        "observable_table",
        "b5_correlation_observable_table",
        "negative_control_replay_table",
        "leakage_guardrail_report",
        "family_prior_denominator_table",
        "same_access_cost_ledger",
        "row_acceptance_ledger",
        "b5_mechanism_boundary_note",
        "claim_boundary_note",
    ]

    missing_keys = [key for key in required_keys if submitted is None or key not in submitted]
    production_present = [
        key for key in production_required_keys if submitted is not None and submitted.get(key) is not None
    ]
    manifest_bound = (
        submitted is not None
        and submitted.get("acceptance_packet_id") == EXPECTED_ACCEPTANCE_PACKET_ID
        and submitted.get("material_id") == EXPECTED_MATERIAL_ID
        and submitted.get("provenance_manifest_id") == EXPECTED_PROVENANCE_MANIFEST_ID
        and submitted.get("replay_validation_manifest_id") == EXPECTED_REPLAY_MANIFEST_ID
        and submitted.get("row_replay_validation_manifest_id") == EXPECTED_ROW_REPLAY_MANIFEST_ID
        and submitted.get("priority_packet_hash") == priority_summary.get("packet_hash")
        and submitted.get("provenance_manifest_hash") == row_summary.get("provenance_manifest_hash")
        and submitted.get("replay_validation_manifest_hash") == row_summary.get(
            "replay_validation_manifest_hash"
        )
        and submitted.get("row_replay_validation_manifest_hash") == row_summary.get("manifest_hash")
    )
    row_acceptance_valid = (
        submitted is not None
        and submitted.get("accepted_dft_b5_row_count", 0) > 0
        and submitted.get("top_post_rank") == 1
        and submitted.get("negative_control_topk_count") == row_summary.get(
            "selected_negative_controls_in_top_k"
        )
        and submitted.get("material_family_count") == row_summary.get("family_count")
        and submitted.get("source_record_count") == row_summary.get("record_count")
        and bool(submitted.get("structure_input_hash"))
        and bool(submitted.get("dft_input_deck_hash"))
        and bool(submitted.get("dft_output_bundle_hash"))
        and bool(submitted.get("observable_table_hash"))
        and bool(submitted.get("b5_correlation_observable_hash"))
    )
    b5_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("b5_mechanism_boundary"), dict)
        and submitted["b5_mechanism_boundary"].get("b5_mechanism_solved") is False
        and submitted["b5_mechanism_boundary"].get("high_tc_mechanism_solved") is False
        and submitted["b5_mechanism_boundary"].get("quantum_advantage_claimed") is False
    )
    claim_boundary_bound = (
        submitted is not None
        and isinstance(submitted.get("claim_boundary"), dict)
        and submitted["claim_boundary"].get("dft_observable_claimed") is False
        and submitted["claim_boundary"].get("b5_computed_observable_claimed") is False
        and submitted["claim_boundary"].get("material_discovery_claimed") is False
        and submitted["claim_boundary"].get("mechanism_solved") is False
        and submitted["claim_boundary"].get("solution_claimed") is False
    )
    source_backed = submitted is not None and submitted.get("source_evidence_files_present") is True

    acceptance_packet = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "material_id": EXPECTED_MATERIAL_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "replay_validation_manifest_id": EXPECTED_REPLAY_MANIFEST_ID,
        "row_replay_validation_manifest_id": EXPECTED_ROW_REPLAY_MANIFEST_ID,
        "source_row_replay_validation_manifest_gate": str(args.row_replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "submission_artifact_path": str(submission_path),
        "priority_packet_hash": priority_summary.get("packet_hash"),
        "provenance_manifest_hash": row_summary.get("provenance_manifest_hash"),
        "replay_validation_manifest_hash": row_summary.get("replay_validation_manifest_hash"),
        "row_replay_validation_manifest_hash": row_summary.get("manifest_hash"),
        "source_table_hash": row_summary.get("source_table_hash"),
        "replay_formula_hash": row_summary.get("replay_formula_hash"),
        "replay_table_hash": row_summary.get("replay_table_hash"),
        "record_count": row_summary.get("record_count"),
        "family_count": row_summary.get("family_count"),
        "negative_control_count": row_summary.get("negative_control_count"),
        "selected_negative_controls_in_top_k": row_summary.get("selected_negative_controls_in_top_k"),
        "template_row_count": row_summary.get("template_row_count"),
        "accepted_priority_dft_rows": row_summary.get("accepted_priority_dft_rows"),
        "accepted_priority_b5_rows": row_summary.get("accepted_priority_b5_rows"),
        "required_keys": required_keys,
        "production_required_keys": production_required_keys,
        "required_evidence_files": evidence_files,
        "accepted_only_if": [
            "acceptance_packet_id equals B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet",
            "material, provenance, replay-validation, row-replay-validation, and priority packet hashes match the source gates",
            "source formula, structure input, DFT input/output, observable table, B5 correlation observable, negative-control replay, leakage guardrail, family-prior denominator, same-access ledger, and row acceptance ledger are hash-bound",
            "accepted_dft_b5_row_count is positive only after the paired DFT/B5 row is source-backed and row-valid",
            "top_post_rank, negative-control top-k count, family count, and source-record count preserve the 56-record / 28-family / 18-negative-control denominator",
            "B5 mechanism boundary explicitly denies B5 mechanism, high-Tc mechanism, and quantum-advantage claims",
            "claim_boundary forbids DFT-observable, B5-observable, material-discovery, mechanism-solved, and solution claims until audited rows are accepted",
        ],
    }
    acceptance_packet["packet_hash"] = stable_hash(acceptance_packet)

    forbidden_claims = [
        "dft_observable_claimed",
        "b5_computed_observable_claimed",
        "material_discovery_claimed",
        "mechanism_solved",
        "solution_claimed",
    ]
    requirements = [
        requirement(
            "P1",
            "Row replay-validation manifest gate remains valid and blocked only on P6/P7/P8",
            row_replay.get("method") == "b6_b5_observable_row_replay_validation_manifest_gate_v0"
            and row_summary.get("validation_error_count") == 0
            and row_summary.get("failed_manifest_requirement_ids") == EXPECTED_FAILED_IDS,
            {
                "source_status": row_replay.get("status"),
                "failed_manifest_requirement_ids": row_summary.get("failed_manifest_requirement_ids"),
                "validation_error_count": row_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Priority observable packet remains fixed and source-shaped",
            priority.get("method") == "b6_b5_observable_priority_packet_gate_v0"
            and priority_summary.get("priority_material_id") == EXPECTED_MATERIAL_ID
            and priority_summary.get("validation_error_count") == 0
            and priority_summary.get("failed_priority_requirement_ids") == EXPECTED_FAILED_IDS,
            {
                "priority_material_id": priority_summary.get("priority_material_id"),
                "packet_hash": priority_summary.get("packet_hash"),
                "failed_priority_requirement_ids": priority_summary.get("failed_priority_requirement_ids"),
            },
        ),
        requirement(
            "P3",
            "Acceptance packet carries locked DFT/B5 observable row schema and evidence classes",
            len(required_keys) == 28
            and len(production_required_keys) == 19
            and len(evidence_files) == 17,
            {
                "required_key_count": len(required_keys),
                "production_required_key_count": len(production_required_keys),
                "required_evidence_file_count": len(evidence_files),
            },
        ),
        requirement(
            "P4",
            "Replay scope, template table, and negative-control denominator remain preserved",
            row_summary.get("record_count") == 56
            and row_summary.get("family_count") == 28
            and row_summary.get("negative_control_count") == 18
            and row_summary.get("selected_negative_controls_in_top_k") == 2
            and row_summary.get("template_row_count") == 12
            and row_summary.get("accepted_priority_dft_rows") == 0
            and row_summary.get("accepted_priority_b5_rows") == 0,
            {
                "record_count": row_summary.get("record_count"),
                "family_count": row_summary.get("family_count"),
                "negative_control_count": row_summary.get("negative_control_count"),
                "selected_negative_controls_in_top_k": row_summary.get(
                    "selected_negative_controls_in_top_k"
                ),
                "template_row_count": row_summary.get("template_row_count"),
                "accepted_priority_dft_rows": row_summary.get("accepted_priority_dft_rows"),
                "accepted_priority_b5_rows": row_summary.get("accepted_priority_b5_rows"),
            },
        ),
        requirement(
            "P5",
            "Current state has no accepted DFT/B5 observable rows and no discovery claim",
            row_summary.get("accepted_priority_dft_rows") == 0
            and row_summary.get("accepted_priority_b5_rows") == 0
            and all(row_summary.get(key) is False for key in forbidden_claims),
            {
                "accepted_priority_dft_rows": row_summary.get("accepted_priority_dft_rows"),
                "accepted_priority_b5_rows": row_summary.get("accepted_priority_b5_rows"),
                **{key: row_summary.get(key) for key in forbidden_claims},
            },
        ),
        requirement(
            "P6",
            "Observable row acceptance packet has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted acceptance packet satisfies the locked DFT/B5 observable row schema",
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
            "Submitted acceptance packet is source-backed, manifest-bound, row-valid, B5-boundary-bound, and claim-boundary-bound",
            source_backed
            and manifest_bound
            and row_acceptance_valid
            and b5_boundary_bound
            and claim_boundary_bound,
            {
                "source_backed": source_backed,
                "manifest_bound": manifest_bound,
                "row_acceptance_valid": row_acceptance_valid,
                "b5_boundary_bound": b5_boundary_bound,
                "claim_boundary_bound": claim_boundary_bound,
            },
        ),
        requirement(
            "P9",
            "Forbidden observable, discovery, mechanism, and solution claims remain false",
            all(row_summary.get(key) is False for key in forbidden_claims),
            {key: row_summary.get(key) for key in forbidden_claims},
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected observable row acceptance packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted acceptance packet until an observable PR supplies one")

    summary = {
        "acceptance_packet_id": EXPECTED_ACCEPTANCE_PACKET_ID,
        "material_id": EXPECTED_MATERIAL_ID,
        "provenance_manifest_id": EXPECTED_PROVENANCE_MANIFEST_ID,
        "replay_validation_manifest_id": EXPECTED_REPLAY_MANIFEST_ID,
        "row_replay_validation_manifest_id": EXPECTED_ROW_REPLAY_MANIFEST_ID,
        "priority_packet_hash": priority_summary.get("packet_hash"),
        "provenance_manifest_hash": row_summary.get("provenance_manifest_hash"),
        "replay_validation_manifest_hash": row_summary.get("replay_validation_manifest_hash"),
        "row_replay_validation_manifest_hash": row_summary.get("manifest_hash"),
        "acceptance_packet_hash": acceptance_packet["packet_hash"],
        "acceptance_requirement_count": len(requirements),
        "acceptance_requirements_passed": passed,
        "acceptance_requirements_failed": len(requirements) - passed,
        "failed_acceptance_requirement_ids": failed_ids,
        "required_key_count": len(required_keys),
        "production_required_key_count": len(production_required_keys),
        "required_evidence_file_count": len(evidence_files),
        "record_count": row_summary.get("record_count"),
        "family_count": row_summary.get("family_count"),
        "negative_control_count": row_summary.get("negative_control_count"),
        "selected_negative_controls_in_top_k": row_summary.get("selected_negative_controls_in_top_k"),
        "template_row_count": row_summary.get("template_row_count"),
        "submitted_acceptance_packet_exists": submitted_exists,
        "submitted_key_count": len(submitted) if submitted else 0,
        "missing_key_count": len(missing_keys),
        "production_keys_present_count": len(production_present),
        "accepted_dft_b5_row_count": 0,
        "accepted_priority_dft_rows": 0,
        "accepted_priority_b5_rows": 0,
        "dft_observable_claimed": False,
        "b5_computed_observable_claimed": False,
        "material_discovery_claimed": False,
        "mechanism_solved": False,
        "solution_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B6",
        "linked_benchmark_id": "B5",
        "problem_id": 37,
        "title": "B6/B5 Observable Row Acceptance Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_row_replay_validation_manifest_gate": str(args.row_replay_validation_manifest_gate),
        "source_priority_packet_gate": str(args.priority_packet_gate),
        "summary": summary,
        "observable_row_acceptance_packet": acceptance_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The rank-1 B6/B5 observable route now has an acceptance packet gate after "
                "row replay-validation and before any paired DFT/B5 observable row can count."
            ),
            "what_is_not_supported": (
                "No acceptance packet, DFT row, or B5-computed observable row has been "
                "submitted or accepted; no material discovery, mechanism-solved, "
                "observable, quantum advantage, or solution claim is supported."
            ),
            "next_gate": (
                "Submit B6B5-O1-monolayer-FeSe-STO-row-acceptance-packet with source "
                "formula, structure input, DFT input/output, observable table, B5 "
                "correlation observable, negative-control replay, leakage guardrail, "
                "family-prior denominator, same-access ledger, row acceptance ledger, "
                "B5 mechanism boundary, and claim boundary."
            ),
            "accepted_dft_b5_row_count": 0,
            "accepted_priority_dft_rows": 0,
            "accepted_priority_b5_rows": 0,
            "dft_observable_claimed": False,
            "b5_computed_observable_claimed": False,
            "material_discovery_claimed": False,
            "mechanism_solved": False,
            "solution_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["observable_row_acceptance_packet"]
    lines = [
        "# B6/B5 Observable Row Acceptance Packet Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Acceptance packet: `{summary['acceptance_packet_id']}`",
        f"- Priority material: `{summary['material_id']}`",
        f"- Row replay-validation manifest: `{summary['row_replay_validation_manifest_id']}`",
        f"- Row replay-validation hash: `{summary['row_replay_validation_manifest_hash']}`",
        f"- Acceptance packet hash: `{summary['acceptance_packet_hash']}`",
        f"- Requirements passed/failed: `{summary['acceptance_requirements_passed']}` / `{summary['acceptance_requirements_failed']}`",
        f"- Failed requirement IDs: `{summary['failed_acceptance_requirement_ids']}`",
        f"- Required key / production key / evidence file count: `{summary['required_key_count']}` / `{summary['production_required_key_count']}` / `{summary['required_evidence_file_count']}`",
        f"- Replay scope records/families/negative controls: `{summary['record_count']}` / `{summary['family_count']}` / `{summary['negative_control_count']}`",
        f"- Template rows / negative controls in top-k: `{summary['template_row_count']}` / `{summary['selected_negative_controls_in_top_k']}`",
        f"- Submitted acceptance packet exists: `{summary['submitted_acceptance_packet_exists']}`",
        f"- Accepted DFT/B5 row count: `{summary['accepted_dft_b5_row_count']}`",
        f"- validation_error_count: `{summary['validation_error_count']}`",
        "",
        "## Acceptance Packet",
        "",
        f"- Submission path: `{packet['submission_artifact_path']}`",
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
            f"- accepted_dft_b5_row_count: {payload['claim_boundary']['accepted_dft_b5_row_count']}",
            f"- accepted_priority_dft_rows: {payload['claim_boundary']['accepted_priority_dft_rows']}",
            f"- accepted_priority_b5_rows: {payload['claim_boundary']['accepted_priority_b5_rows']}",
            f"- dft_observable_claimed: {payload['claim_boundary']['dft_observable_claimed']}",
            f"- b5_computed_observable_claimed: {payload['claim_boundary']['b5_computed_observable_claimed']}",
            f"- material_discovery_claimed: {payload['claim_boundary']['material_discovery_claimed']}",
            f"- mechanism_solved: {payload['claim_boundary']['mechanism_solved']}",
            f"- solution_claimed: {payload['claim_boundary']['solution_claimed']}",
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
        "--row-replay-validation-manifest-gate",
        type=Path,
        default=Path("results/B6_B5_observable_row_replay_validation_manifest_gate_v0.json"),
    )
    parser.add_argument(
        "--priority-packet-gate",
        type=Path,
        default=Path("results/B6_B5_observable_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B6_B5_observable_row_acceptance_packet_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B6_B5_observable_row_acceptance_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B6_B5_observable_row_acceptance_packet_gate.md"),
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
