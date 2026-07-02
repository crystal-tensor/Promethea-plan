#!/usr/bin/env python3
"""T-B6-005g: priority DFT/B5 observable row packet gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b6_b5_observable_priority_packet_gate_v0"
STATUS = "observable_priority_packet_open_missing_artifact"
MODEL_STATUS = "priority_dft_b5_observable_packet_ready_no_rows_submitted"
VERSION = "0.1"
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
    intake = load_json(args.intake_template)
    summary = intake["summary"]
    row_template = next(
        (row for row in intake["row_templates"] if row["material_id"] == EXPECTED_MATERIAL_ID),
        None,
    )
    dft_keys = list(intake["dft_required_keys"])
    b5_keys = list(intake["b5_required_keys"])
    combined_required_keys = [f"dft.{key}" for key in dft_keys] + [f"b5.{key}" for key in b5_keys]
    submission_path = args.submission_dir / f"{EXPECTED_MATERIAL_ID}.json"
    submitted_exists = submission_path.exists()
    submitted = load_json(submission_path) if submitted_exists else None
    dft_row = submitted.get("dft_row") if submitted else None
    b5_row = submitted.get("b5_row") if submitted else None
    missing_dft_keys = [key for key in dft_keys if not isinstance(dft_row, dict) or key not in dft_row]
    missing_b5_keys = [key for key in b5_keys if not isinstance(b5_row, dict) or key not in b5_row]
    source_backed = (
        submitted is not None
        and submitted.get("source_evidence_files_present") is True
        and not missing_dft_keys
        and not missing_b5_keys
    )
    hashes_preserved = (
        submitted is not None
        and submitted.get("source_table_hash") == summary["source_table_hash"]
        and submitted.get("replay_formula_hash") == summary["replay_formula_hash"]
        and submitted.get("replay_table_hash") == summary["replay_table_hash"]
    )

    priority_packet = {
        "material_id": EXPECTED_MATERIAL_ID,
        "rank": row_template["rank"] if row_template else None,
        "family": row_template["family"] if row_template else None,
        "template_hash": row_template["template_hash"] if row_template else None,
        "submission_artifact_path": str(submission_path),
        "dft_required_keys": dft_keys,
        "b5_required_keys": b5_keys,
        "combined_required_keys": combined_required_keys,
        "required_evidence_files": [
            "structure_reference_or_cif",
            "dft_input_manifest",
            "dft_output_or_parser_log",
            "dft_calculation_hash_source",
            "effective_model_derivation_note",
            "b5_solver_trace_artifact",
            "same_access_cost_ledger",
            "observable_join_key_audit",
            "source_replay_hash_manifest",
            "claim_boundary_note",
        ],
        "accepted_only_if": [
            "dft_row contains all 11 DFT keys",
            "b5_row contains all 11 B5-computed observable keys",
            "material_id matches the rank-1 intake template",
            "source_table_hash, replay_formula_hash, and replay_table_hash are preserved",
            "DFT calculation_hash and B5 solver_trace_hash bind source artifacts",
            "same_access_cost_units is present for the B5 row",
            "claim_boundary forbids material discovery, mechanism-solved, and solution claims",
        ],
    }
    priority_packet["packet_hash"] = stable_hash(priority_packet)

    requirements = [
        requirement(
            "P1",
            "Observable intake template remains valid and open on DFT/B5 rows",
            intake.get("method") == "b6_observable_row_intake_template_gate_v0"
            and summary.get("validation_error_count") == 0
            and summary.get("failed_intake_requirement_ids") == ["T6", "T7"],
            {
                "source_status": intake.get("status"),
                "failed_intake_requirement_ids": summary.get("failed_intake_requirement_ids"),
                "validation_error_count": summary.get("validation_error_count"),
            },
        ),
        requirement(
            "P2",
            "Priority material is fixed to the rank-1 top-post replay template",
            row_template is not None
            and row_template["rank"] == 1
            and row_template["material_id"] == EXPECTED_MATERIAL_ID,
            {
                "expected_material_id": EXPECTED_MATERIAL_ID,
                "actual_material_id": row_template["material_id"] if row_template else None,
                "rank": row_template["rank"] if row_template else None,
            },
        ),
        requirement(
            "P3",
            "Priority packet carries both 11-key observable schemas",
            len(dft_keys) == 11 and len(b5_keys) == 11 and len(combined_required_keys) == 22,
            {
                "required_dft_key_count": len(dft_keys),
                "required_b5_key_count": len(b5_keys),
                "combined_required_key_count": len(combined_required_keys),
            },
        ),
        requirement(
            "P4",
            "Packet binds required source evidence classes",
            len(priority_packet["required_evidence_files"]) == 10,
            {"required_evidence_files": priority_packet["required_evidence_files"]},
        ),
        requirement(
            "P5",
            "Source, formula, replay, and schema hashes are preserved from intake",
            summary.get("source_table_hash") == "ce134d0a5d295af982b77be0a8a43e90ea19e828af20cc80ac3f20b7664d2fdc"
            and summary.get("replay_formula_hash") == "e23239648dd11aa8e0db8ecdeb5824506a5a379c9ba2777965c3aafa5d5d8230"
            and summary.get("replay_table_hash") == "c44099194d0bc04d74cd3c4c4e068bf51a9e114d11c6e0b5e3890786cda5b8de"
            and summary.get("dft_schema_hash") == stable_hash(dft_keys)
            and summary.get("b5_schema_hash") == stable_hash(b5_keys),
            {
                "source_table_hash": summary.get("source_table_hash"),
                "replay_formula_hash": summary.get("replay_formula_hash"),
                "replay_table_hash": summary.get("replay_table_hash"),
                "dft_schema_hash": summary.get("dft_schema_hash"),
                "b5_schema_hash": summary.get("b5_schema_hash"),
            },
        ),
        requirement(
            "P6",
            "Priority observable artifact has been submitted",
            submitted_exists,
            {"submission_artifact_path": str(submission_path), "exists": submitted_exists},
        ),
        requirement(
            "P7",
            "Submitted artifact satisfies both locked observable schemas",
            submitted_exists and not missing_dft_keys and not missing_b5_keys,
            {
                "missing_dft_keys": missing_dft_keys,
                "missing_b5_keys": missing_b5_keys,
                "submitted_top_level_keys": sorted(submitted) if submitted else [],
            },
        ),
        requirement(
            "P8",
            "Submitted rows are source-backed and preserve replay hashes",
            source_backed and hashes_preserved,
            {
                "source_evidence_files_present": submitted.get("source_evidence_files_present")
                if submitted
                else False,
                "hashes_preserved": hashes_preserved,
            },
        ),
        requirement(
            "P9",
            "Forbidden observable, discovery, mechanism, and solution claims remain false",
            all(
                summary.get(key) is False
                for key in [
                    "dft_observable_claimed",
                    "b5_computed_observable_claimed",
                    "material_discovery_claimed",
                    "mechanism_solved",
                    "solution_claimed",
                ]
            ),
            {
                "dft_observable_claimed": summary.get("dft_observable_claimed"),
                "b5_computed_observable_claimed": summary.get("b5_computed_observable_claimed"),
                "material_discovery_claimed": summary.get("material_discovery_claimed"),
                "mechanism_solved": summary.get("mechanism_solved"),
                "solution_claimed": summary.get("solution_claimed"),
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected priority observable packet failures: {failed_ids}")
    if submitted_exists:
        validation_errors.append("gate expected no submitted artifact until an observable PR supplies one")

    payload_summary = {
        "priority_material_id": EXPECTED_MATERIAL_ID,
        "priority_material_rank": row_template["rank"] if row_template else None,
        "priority_material_family": row_template["family"] if row_template else None,
        "packet_hash": priority_packet["packet_hash"],
        "priority_requirement_count": len(requirements),
        "priority_requirements_passed": passed,
        "priority_requirements_failed": len(requirements) - passed,
        "failed_priority_requirement_ids": failed_ids,
        "required_dft_key_count": len(dft_keys),
        "required_b5_key_count": len(b5_keys),
        "combined_required_key_count": len(combined_required_keys),
        "required_evidence_file_count": len(priority_packet["required_evidence_files"]),
        "template_row_count": summary.get("template_row_count"),
        "submitted_artifact_exists": submitted_exists,
        "missing_dft_key_count": len(missing_dft_keys),
        "missing_b5_key_count": len(missing_b5_keys),
        "accepted_priority_dft_rows": 0,
        "accepted_priority_b5_rows": 0,
        "source_table_hash": summary.get("source_table_hash"),
        "replay_formula_hash": summary.get("replay_formula_hash"),
        "replay_table_hash": summary.get("replay_table_hash"),
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
        "title": "B6/B5 Observable Priority Packet Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_intake_template_result": str(args.intake_template),
        "summary": payload_summary,
        "priority_observable_packet": priority_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The first B6/B5 observable blocker now has a concrete source-backed "
                "submission packet for a paired DFT and B5-computed observable row."
            ),
            "what_is_not_supported": (
                "No DFT row or B5-computed observable row has been submitted or accepted; "
                "no material discovery, high-Tc mechanism solution, or B6 solution claim is supported."
            ),
            "next_gate": (
                f"Submit {submission_path} with dft_row and b5_row blocks satisfying all 22 "
                "combined schema keys while preserving source/replay hashes."
            ),
            "dft_observable_claimed": False,
            "b5_computed_observable_claimed": False,
            "material_discovery_claimed": False,
            "mechanism_solved": False,
            "solution_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    packet = payload["priority_observable_packet"]
    lines = [
        "# B6/B5 Observable Priority Packet Gate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Priority material: `{summary['priority_material_id']}`",
        f"- Packet hash: `{summary['packet_hash']}`",
        f"- Requirements passed/failed: {summary['priority_requirements_passed']} / {summary['priority_requirements_failed']}",
        f"- Failed requirement IDs: {summary['failed_priority_requirement_ids']}",
        f"- DFT/B5 required key counts: {summary['required_dft_key_count']} / {summary['required_b5_key_count']}",
        f"- Combined schema keys: {summary['combined_required_key_count']}",
        f"- Required evidence file classes: {summary['required_evidence_file_count']}",
        f"- Submitted artifact exists: {summary['submitted_artifact_exists']}",
        f"- Accepted priority DFT/B5 rows: {summary['accepted_priority_dft_rows']} / {summary['accepted_priority_b5_rows']}",
        "",
        "## Submission Packet",
        "",
        f"- Submission path: `{packet['submission_artifact_path']}`",
        f"- Rank / family: {packet['rank']} / {packet['family']}",
        f"- Template hash: `{packet['template_hash']}`",
        "",
        "Required evidence files:",
        "",
    ]
    for item in packet["required_evidence_files"]:
        lines.append(f"- {item}")
    lines.extend(["", "Acceptance predicates:", ""])
    for item in packet["accepted_only_if"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## DFT Row Schema",
            "",
            ", ".join(packet["dft_required_keys"]),
            "",
            "## B5 Row Schema",
            "",
            ", ".join(packet["b5_required_keys"]),
            "",
            "## Requirement Results",
            "",
        ]
    )
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
        for error in payload["validation_errors"]:
            lines.append(f"- {error}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--intake-template",
        type=Path,
        default=Path("results/B6_B5_observable_row_intake_template_gate_v0.json"),
    )
    parser.add_argument(
        "--submission-dir",
        type=Path,
        default=Path("results/B6_B5_observable_priority_submissions"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B6_B5_observable_priority_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B6_B5_observable_priority_packet_gate.md"),
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
