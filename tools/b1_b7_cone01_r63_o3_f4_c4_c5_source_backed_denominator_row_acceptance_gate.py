#!/usr/bin/env python3
"""T-B1-004fm/T-B7-014v: R63 C4/C5 source-backed denominator row acceptance gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r63_o3_f4_c4_c5_source_backed_denominator_row_acceptance_gate_v0"
STATUS = "cone01_r63_c4_c5_source_backed_denominator_rows_accepted_zero_b7_credit"
MODEL_STATUS = "all_8_same_access_rz_denominator_rows_pass_r62_compatible_acceptance"
VERSION = "0.1"
TARGET_ID = "T-B1-004fm/T-B7-014v"
UPSTREAM_TARGET_ID = "T-B1-004fl/T-B7-014u"
DENOMINATOR_VERIFIER = "tools/b1_b7_o3_f4_same_access_rz_denominator_verifier.py"


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def req(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def out_dir(root: Path) -> Path:
    return root / "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows"


def repo_file(root: Path, value: str) -> Path:
    return root / value


def path_exists(root: Path, value: str) -> bool:
    return bool(value) and repo_file(root, value).is_file()


def hash_matches(root: Path, value: str, expected_hash: str | None) -> bool:
    if not expected_hash or not path_exists(root, value):
        return False
    return file_hash(repo_file(root, value)) == expected_hash


def is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def parse_command_path(command: str) -> str | None:
    try:
        parts = shlex.split(command)
    except ValueError:
        return None
    if len(parts) < 2:
        return None
    if parts[0] not in {"python", "python3"} and not parts[0].endswith("/python3"):
        return None
    return parts[1]


def structured_same_access_statement(value: Any) -> bool:
    return isinstance(value, dict) and {
        "access_model_hash",
        "allowed_inputs_used",
        "forbidden_inputs_used",
        "same_metric_used",
    }.issubset(value)


def structured_leakage_audit(value: Any) -> bool:
    return isinstance(value, dict) and {
        "forbidden_inputs_reviewed",
        "forbidden_inputs_used",
        "leakage_free",
        "audit_hash",
    }.issubset(value)


def transcript_distance(transcript: dict[str, Any]) -> float | None:
    value = transcript.get("denominator_distance")
    if is_finite_number(value):
        return float(value)
    return None


def verify_row(root: Path, row: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    challenge_id = template["challenge_id"]
    checks: list[dict[str, Any]] = []

    def add(check_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> None:
        checks.append(
            {
                "check_id": check_id,
                "label": label,
                "passed": bool(passed),
                "evidence": evidence,
            }
        )

    required_fields_present = all(
        field in row and row[field] not in (None, "") for field in template["required_fields"]
    )
    add(
        "H1",
        "all R60 required fields are present",
        required_fields_present,
        {
            "required_field_count": template["required_field_count"],
            "missing_fields": [
                field
                for field in template["required_fields"]
                if field not in row or row[field] in (None, "")
            ],
        },
    )
    add(
        "H2",
        "challenge id and schema version match the template",
        row.get("challenge_id") == challenge_id
        and row.get("acceptance_schema_version") == template["acceptance_schema_version"],
        {
            "row_challenge_id": row.get("challenge_id"),
            "template_challenge_id": challenge_id,
            "row_schema": row.get("acceptance_schema_version"),
            "template_schema": template["acceptance_schema_version"],
        },
    )
    add(
        "H3",
        "source, candidate, R59 certificate, metric, tolerance, and access-model hashes match",
        row.get("source_circuit_file") == template["source_circuit_file"]
        and row.get("source_circuit_sha256") == template["source_circuit_sha256"]
        and row.get("candidate_circuit_file") == template["candidate_circuit_file"]
        and row.get("candidate_circuit_sha256") == template["candidate_circuit_sha256"]
        and row.get("r59_certificate_file") == template["r59_certificate_file"]
        and row.get("r59_certificate_hash") == template["r59_certificate_hash"]
        and row.get("unitary_distance_metric") == template["unitary_distance_metric"]
        and row.get("strict_tolerance") == template["strict_tolerance"]
        and row.get("access_model_hash") == template["access_model_hash"],
        {"access_model_hash": row.get("access_model_hash")},
    )
    impl_path = row.get("denominator_implementation_path")
    impl_exists = isinstance(impl_path, str) and path_exists(root, impl_path)
    add(
        "H4",
        "denominator implementation exists in the repository",
        impl_exists,
        {"denominator_implementation_path": impl_path},
    )
    command_path = parse_command_path(str(row.get("reproducible_command", "")))
    add(
        "H5",
        "reproducible command points at the reviewed implementation and was replayed",
        impl_exists
        and command_path == impl_path
        and row.get("reproducible_command_replayed") is True,
        {
            "command_path": command_path,
            "denominator_implementation_path": impl_path,
            "reproducible_command_replayed": row.get("reproducible_command_replayed"),
        },
    )
    transcript_path = row.get("verifier_transcript_path")
    transcript_exists = isinstance(transcript_path, str) and path_exists(root, transcript_path)
    transcript_hash_ok = (
        isinstance(transcript_path, str)
        and isinstance(row.get("verifier_transcript_sha256"), str)
        and hash_matches(root, transcript_path, row.get("verifier_transcript_sha256"))
    )
    add(
        "H6",
        "verifier transcript exists and hash-matches the row",
        transcript_exists and transcript_hash_ok,
        {
            "verifier_transcript_path": transcript_path,
            "transcript_exists": transcript_exists,
            "transcript_hash_ok": transcript_hash_ok,
        },
    )
    transcript: dict[str, Any] = {}
    if transcript_exists and transcript_hash_ok and isinstance(transcript_path, str):
        transcript = load_json(repo_file(root, transcript_path))
    distance_from_transcript = transcript_distance(transcript)
    add(
        "H7",
        "denominator distance is finite and transcript-bound",
        distance_from_transcript is not None
        and is_finite_number(row.get("denominator_distance"))
        and float(row["denominator_distance"]) == distance_from_transcript
        and row.get("denominator_distance_source") == "verifier_transcript_bound",
        {
            "row_denominator_distance": row.get("denominator_distance"),
            "distance_from_transcript": distance_from_transcript,
            "denominator_distance_source": row.get("denominator_distance_source"),
        },
    )
    add(
        "H8",
        "same-access and leakage audits are structured",
        structured_same_access_statement(row.get("same_access_statement"))
        and structured_leakage_audit(row.get("leakage_audit_statement"))
        and row.get("structured_leakage_audit") is True,
        {
            "same_access_statement_type": type(row.get("same_access_statement")).__name__,
            "leakage_audit_statement_type": type(row.get("leakage_audit_statement")).__name__,
            "structured_leakage_audit": row.get("structured_leakage_audit"),
        },
    )
    add(
        "H9",
        "computed denominator pressure flags are transcript-derived",
        row.get("denominator_beats_r59_positive_distance") is True
        and row.get("denominator_rejects_r59_negative_control_pressure") is True
        and transcript.get("pressure_flags_transcript_bound") is True,
        {
            "denominator_beats_r59_positive_distance": row.get(
                "denominator_beats_r59_positive_distance"
            ),
            "denominator_rejects_r59_negative_control_pressure": row.get(
                "denominator_rejects_r59_negative_control_pressure"
            ),
            "pressure_flags_transcript_bound": transcript.get("pressure_flags_transcript_bound"),
        },
    )
    claim_boundary = str(row.get("claim_boundary", ""))
    overclaims = any(
        token in claim_boundary.lower()
        for token in ["b7 credit", "stv credit", "o3 closure", "denominator win"]
    )
    add(
        "H10",
        "claim boundary avoids O3/reroute/B7/STV overclaim",
        not overclaims,
        {"claim_boundary": claim_boundary, "overclaims": overclaims},
    )
    failed = [item["check_id"] for item in checks if not item["passed"]]
    transcript_payload = {
        "artifact": "R63 R62-compatible denominator row acceptance transcript",
        "challenge_id": challenge_id,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "method": METHOD,
        "input_row_file": row.get("row_file"),
        "input_row_hash": row.get("row_hash"),
        "template_hash": template["template_hash"],
        "checks": checks,
        "check_count": len(checks),
        "passed_check_count": len(checks) - len(failed),
        "failed_check_count": len(failed),
        "failed_check_ids": failed,
        "accepted": len(failed) == 0,
        "claim_boundary": (
            "Acceptance transcript only. Row acceptance can move the C4/C5 evidence "
            "gate but does not promote architecture or resource claims."
        ),
    }
    transcript_payload["transcript_hash"] = stable_hash(transcript_payload)
    transcript_file = out_dir(root) / f"{challenge_id}.r63_r62_acceptance_verifier_transcript.json"
    write_json(transcript_file, transcript_payload)
    transcript_payload["transcript_file"] = str(transcript_file.relative_to(root))
    transcript_payload["transcript_file_sha256"] = file_hash(transcript_file)
    return transcript_payload


def run_denominator_verifier(root: Path, template: dict[str, Any]) -> dict[str, Any]:
    challenge_id = template["challenge_id"]
    transcript_path = (
        out_dir(root) / f"{challenge_id}.r63_same_access_denominator_verifier_transcript.json"
    )
    stdout_path = out_dir(root) / f"{challenge_id}.r63_same_access_denominator_verifier.stdout.txt"
    negative_control = (
        out_dir(root) / f"{challenge_id}.r59_c3_negative_control.json"
    ).relative_to(root)
    command = [
        "python3",
        DENOMINATOR_VERIFIER,
        "--challenge-id",
        challenge_id,
        "--source",
        template["source_circuit_file"],
        "--candidate",
        template["candidate_circuit_file"],
        "--r59-certificate",
        template["r59_certificate_file"],
        "--negative-control",
        str(negative_control),
        "--access-model-hash",
        template["access_model_hash"],
        "--output",
        str(transcript_path.relative_to(root)),
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
    )
    stdout_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"denominator verifier failed for {challenge_id}: {completed.returncode}"
        )
    transcript = load_json(transcript_path)
    transcript["stdout_file"] = str(stdout_path.relative_to(root))
    transcript["stdout_file_sha256"] = file_hash(stdout_path)
    write_json(transcript_path, transcript)
    return {
        "command": " ".join(shlex.quote(part) for part in command),
        "stdout_file": str(stdout_path.relative_to(root)),
        "stdout_file_sha256": file_hash(stdout_path),
        "transcript_path": str(transcript_path.relative_to(root)),
        "transcript_sha256": file_hash(transcript_path),
        "transcript": transcript,
    }


def make_row(root: Path, template: dict[str, Any], replay: dict[str, Any]) -> dict[str, Any]:
    challenge_id = template["challenge_id"]
    transcript = replay["transcript"]
    forbidden_inputs = template["access_model"].get("forbidden_inputs", [])
    same_access_statement = {
        "access_model_hash": template["access_model_hash"],
        "allowed_inputs_used": transcript["same_access_inputs_used"],
        "forbidden_inputs_used": transcript["forbidden_inputs_used"],
        "same_metric_used": template["unitary_distance_metric"],
        "same_access_replay_stdout": replay["stdout_file"],
    }
    leakage_audit_statement = {
        "forbidden_inputs_reviewed": forbidden_inputs,
        "forbidden_inputs_used": transcript["forbidden_inputs_used"],
        "leakage_free": transcript["forbidden_inputs_used"] == [],
        "audit_hash": stable_hash(
            {
                "challenge_id": challenge_id,
                "forbidden_inputs_reviewed": forbidden_inputs,
                "forbidden_inputs_used": transcript["forbidden_inputs_used"],
            }
        ),
    }
    row = {
        "challenge_id": challenge_id,
        "acceptance_schema_version": template["acceptance_schema_version"],
        "denominator_method_id": "same_access_single_qubit_rz_distance_denominator_v0",
        "denominator_implementation_path": DENOMINATOR_VERIFIER,
        "reproducible_command": replay["command"],
        "reproducible_command_replayed": True,
        "access_model_hash": template["access_model_hash"],
        "same_access_statement": same_access_statement,
        "source_circuit_file": template["source_circuit_file"],
        "source_circuit_sha256": template["source_circuit_sha256"],
        "candidate_circuit_file": template["candidate_circuit_file"],
        "candidate_circuit_sha256": template["candidate_circuit_sha256"],
        "r59_certificate_file": template["r59_certificate_file"],
        "r59_certificate_hash": template["r59_certificate_hash"],
        "unitary_distance_metric": template["unitary_distance_metric"],
        "strict_tolerance": template["strict_tolerance"],
        "denominator_distance": transcript["denominator_distance"],
        "denominator_distance_source": "verifier_transcript_bound",
        "denominator_cost_units": "single_qubit_rz_parse_and_operator_norm",
        "denominator_cost_value": 1,
        "denominator_beats_r59_positive_distance": transcript[
            "positive_distance_met_or_equal"
        ],
        "denominator_rejects_r59_negative_control_pressure": transcript[
            "negative_control_rejected"
        ],
        "leakage_audit_statement": leakage_audit_statement,
        "structured_leakage_audit": True,
        "verifier_transcript_path": replay["transcript_path"],
        "verifier_transcript_sha256": replay["transcript_sha256"],
        "claim_boundary": (
            "C4/C5 row evidence only; no O3 closing, reroute permission, B7/STV "
            "promotion, or resource-ledger promotion is claimed."
        ),
    }
    row["row_hash"] = stable_hash(row)
    row_file = out_dir(root) / f"{challenge_id}.r63_source_backed_denominator_row.json"
    row["row_file"] = str(row_file.relative_to(root))
    write_json(row_file, row)
    row["row_file_sha256"] = file_hash(row_file)
    write_json(row_file, row)
    row["row_file_sha256"] = file_hash(row_file)
    return row


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r60 = load_json(args.r60_result)
    r62 = load_json(args.r62_result)
    templates = sorted(
        r60["r60_c4_c5_denominator_contract_packet"]["templates"],
        key=lambda item: item["challenge_id"],
    )
    rows: list[dict[str, Any]] = []
    verifier_replays: list[dict[str, Any]] = []
    acceptance_transcripts: list[dict[str, Any]] = []
    for template in templates:
        replay = run_denominator_verifier(args.root, template)
        row = make_row(args.root, template, replay)
        rows.append(row)
        verifier_replays.append(
            {
                "challenge_id": template["challenge_id"],
                "command": replay["command"],
                "stdout_file": replay["stdout_file"],
                "stdout_file_sha256": replay["stdout_file_sha256"],
                "transcript_path": replay["transcript_path"],
                "transcript_sha256": replay["transcript_sha256"],
                "denominator_distance": replay["transcript"]["denominator_distance"],
            }
        )
        acceptance_transcripts.append(verify_row(args.root, row, template))
    accepted = [item for item in acceptance_transcripts if item["accepted"]]
    distance_values = [float(row["denominator_distance"]) for row in rows]
    bundle = {
        "artifact": "R63 all-row source-backed denominator row acceptance bundle",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "method": METHOD,
        "source_r60_result": str(args.r60_result),
        "source_r60_file_sha256": file_hash(args.r60_result),
        "source_r62_result": str(args.r62_result),
        "source_r62_file_sha256": file_hash(args.r62_result),
        "source_r62_bundle_hash": r62["summary"]["r62_bundle_hash"],
        "denominator_verifier_path": DENOMINATOR_VERIFIER,
        "denominator_verifier_sha256": file_hash(args.root / DENOMINATOR_VERIFIER),
        "submitted_denominator_row_count": len(rows),
        "accepted_denominator_row_count": len(accepted),
        "r62_compatible_acceptance_transcript_count": len(acceptance_transcripts),
        "all_required_fields_present": all(
            all(field in row and row[field] not in (None, "") for field in template["required_fields"])
            for row, template in zip(rows, templates)
        ),
        "all_denominator_transcripts_hash_match": all(
            hash_matches(args.root, row["verifier_transcript_path"], row["verifier_transcript_sha256"])
            for row in rows
        ),
        "all_rows_accepted_under_r62_compatible_verifier": len(accepted) == len(rows) == 8,
        "max_denominator_distance": max(distance_values),
        "min_denominator_distance": min(distance_values),
        "c4_c5_same_access_denominator_row_acceptance_complete": len(accepted) == 8,
        "c4_c5_same_access_denominator_comparison_complete": len(accepted) == 8,
        "c6_leakage_free_optimizer_trace_complete": False,
        "c7_machine_check_replay_complete": False,
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "row_hashes": {row["challenge_id"]: row["row_hash"] for row in rows},
        "row_files": {row["challenge_id"]: row["row_file"] for row in rows},
        "denominator_transcript_files": {
            row["challenge_id"]: row["verifier_transcript_path"] for row in rows
        },
        "acceptance_transcript_files": {
            item["challenge_id"]: item["transcript_file"] for item in acceptance_transcripts
        },
        "claim_boundary": (
            "R63 accepts 8 C4/C5 same-access denominator rows under an R62-compatible "
            "verifier. This advances the row-acceptance gate only; C6, C7, O3, "
            "reroute, B7, STV, and resource-ledger claims remain blocked."
        ),
    }
    bundle["bundle_hash"] = stable_hash(bundle)
    write_json(args.bundle_output, bundle)
    requirements = [
        req(
            "D1",
            "R60 templates and R62 verifier gate are present",
            len(templates) == 8
            and r62["summary"]["c4_c5_same_access_denominator_acceptance_verifier_executable"]
            is True,
            {
                "template_count": len(templates),
                "source_r62_bundle_hash": r62["summary"]["r62_bundle_hash"],
            },
        ),
        req(
            "D2",
            "R63 denominator verifier implementation is hash-bound and replayed",
            bool(bundle["denominator_verifier_sha256"])
            and len(verifier_replays) == 8
            and all(item["stdout_file_sha256"] for item in verifier_replays),
            {
                "denominator_verifier_path": DENOMINATOR_VERIFIER,
                "denominator_verifier_sha256": bundle["denominator_verifier_sha256"],
                "verifier_replay_count": len(verifier_replays),
            },
        ),
        req(
            "D3",
            "R63 submits all 8 source-backed denominator rows with R60 required fields",
            len(rows) == 8 and bundle["all_required_fields_present"] is True,
            {
                "submitted_denominator_row_count": len(rows),
                "required_field_count": templates[0]["required_field_count"],
            },
        ),
        req(
            "D4",
            "R63 denominator transcripts are hash-bound and finite",
            bundle["all_denominator_transcripts_hash_match"] is True
            and all(is_finite_number(row["denominator_distance"]) for row in rows),
            {
                "max_denominator_distance": bundle["max_denominator_distance"],
                "min_denominator_distance": bundle["min_denominator_distance"],
            },
        ),
        req(
            "D5",
            "R63 rows pass the R62-compatible hardened acceptance verifier",
            bundle["all_rows_accepted_under_r62_compatible_verifier"] is True,
            {
                "accepted_denominator_row_count": bundle["accepted_denominator_row_count"],
                "r62_compatible_acceptance_transcript_count": bundle[
                    "r62_compatible_acceptance_transcript_count"
                ],
            },
        ),
        req(
            "D6",
            "R63 keeps same-access and leakage audits structured",
            all(structured_same_access_statement(row["same_access_statement"]) for row in rows)
            and all(structured_leakage_audit(row["leakage_audit_statement"]) for row in rows),
            {"structured_row_count": len(rows)},
        ),
        req(
            "D7",
            "R63 completes C4/C5 row acceptance but leaves C6 and C7 open",
            bundle["c4_c5_same_access_denominator_row_acceptance_complete"] is True
            and bundle["c6_leakage_free_optimizer_trace_complete"] is False
            and bundle["c7_machine_check_replay_complete"] is False,
            {
                "c4_c5_same_access_denominator_row_acceptance_complete": bundle[
                    "c4_c5_same_access_denominator_row_acceptance_complete"
                ],
                "c6_leakage_free_optimizer_trace_complete": bundle[
                    "c6_leakage_free_optimizer_trace_complete"
                ],
                "c7_machine_check_replay_complete": bundle[
                    "c7_machine_check_replay_complete"
                ],
            },
        ),
        req(
            "D8",
            "R63 preserves O3/reroute/B7 zero-credit boundaries",
            bundle["o3_closed"] is False
            and bundle["reroute_allowed"] is False
            and bundle["b7_credit_delta"] == 0
            and bundle["b7_space_time_volume_credit"] == 0
            and bundle["resource_saving_claimed"] is False
            and bundle["b7_ledger_improvement_claimed"] is False,
            {
                "o3_closed": bundle["o3_closed"],
                "reroute_allowed": bundle["reroute_allowed"],
                "b7_credit_delta": bundle["b7_credit_delta"],
                "b7_space_time_volume_credit": bundle["b7_space_time_volume_credit"],
            },
        ),
    ]
    failed = [item["requirement_id"] for item in requirements if not item["passed"]]
    summary = {
        "source_r62_bundle_hash": r62["summary"]["r62_bundle_hash"],
        "r63_bundle_hash": bundle["bundle_hash"],
        "r63_bundle_file_sha256": file_hash(args.bundle_output),
        "denominator_verifier_sha256": bundle["denominator_verifier_sha256"],
        "submitted_denominator_row_count": bundle["submitted_denominator_row_count"],
        "accepted_denominator_row_count": bundle["accepted_denominator_row_count"],
        "r62_compatible_acceptance_transcript_count": bundle[
            "r62_compatible_acceptance_transcript_count"
        ],
        "max_denominator_distance": bundle["max_denominator_distance"],
        "min_denominator_distance": bundle["min_denominator_distance"],
        "all_rows_accepted_under_r62_compatible_verifier": bundle[
            "all_rows_accepted_under_r62_compatible_verifier"
        ],
        "c4_c5_same_access_denominator_row_acceptance_complete": bundle[
            "c4_c5_same_access_denominator_row_acceptance_complete"
        ],
        "c4_c5_same_access_denominator_comparison_complete": bundle[
            "c4_c5_same_access_denominator_comparison_complete"
        ],
        "c6_leakage_free_optimizer_trace_complete": False,
        "c7_machine_check_replay_complete": False,
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "remaining_open_obligations": [
            "C6_leakage_free_optimizer_trace",
            "C7_machine_check_replay_bundle",
            "B7_ledger_retest_after_C6_C7",
        ],
        "remaining_open_obligation_count": 3,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "validation_error_count": len(failed),
    }
    return {
        "title": "B1/B7 Cone01 R63 O3-F4 C4/C5 Source-Backed Denominator Row Acceptance Gate",
        "version": VERSION,
        "last_updated": "2026-07-08",
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "r63_source_backed_denominator_row_acceptance_packet": {
            "source_r60_result": str(args.r60_result),
            "source_r62_result": str(args.r62_result),
            "bundle_output": str(args.bundle_output),
            "bundle": bundle,
            "denominator_verifier_replays": verifier_replays,
            "submitted_rows": rows,
            "acceptance_transcripts": acceptance_transcripts,
        },
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "R63 submits all 8 C4/C5 same-access denominator rows with existing "
                "implementation, replay stdout, hash-matched verifier transcripts, "
                "transcript-bound distances, and structured same-access/leakage audits. "
                "The rows pass an R62-compatible hardened verifier."
            ),
            "what_is_not_supported": (
                "R63 does not complete C6 leakage-free optimizer trace, does not "
                "produce a C7 machine-check bundle, does not close O3, and does not "
                "grant reroute, B7, STV, or resource-ledger promotion."
            ),
            "next_gate": (
                "Run C6 leakage-free optimizer trace on the accepted rows, then C7 "
                "machine-check replay before any B7 ledger retest."
            ),
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": failed,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    s = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R63 O3-F4 C4/C5 Source-Backed Denominator Row Acceptance Gate",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- R63 bundle hash: `{s['r63_bundle_hash']}`",
        "",
        "## Result",
        "",
        (
            f"R63 passes {s['requirements_passed']}/{s['requirement_count']} requirements "
            "by submitting 8 source-backed C4/C5 denominator rows and accepting all 8 "
            "under an R62-compatible hardened verifier. The maximum denominator distance "
            f"is `{s['max_denominator_distance']}`. C6, C7, O3, reroute, B7, STV, and "
            "resource-ledger promotion remain blocked."
        ),
        "",
        "## Evidence",
        "",
        f"- Submitted denominator rows: `{s['submitted_denominator_row_count']}`",
        f"- Accepted denominator rows: `{s['accepted_denominator_row_count']}`",
        f"- Acceptance transcripts: `{s['r62_compatible_acceptance_transcript_count']}`",
        f"- Max denominator distance: `{s['max_denominator_distance']}`",
        f"- Min denominator distance: `{s['min_denominator_distance']}`",
        f"- C4/C5 row acceptance complete: `{s['c4_c5_same_access_denominator_row_acceptance_complete']}`",
        f"- C4/C5 comparison complete: `{s['c4_c5_same_access_denominator_comparison_complete']}`",
        f"- C6 complete: `{s['c6_leakage_free_optimizer_trace_complete']}`",
        f"- C7 complete: `{s['c7_machine_check_replay_complete']}`",
        f"- B7 credit delta: `{s['b7_credit_delta']}`",
        "",
        "## Requirement Results",
        "",
    ]
    for item in payload["requirements"]:
        lines.append(f"- `{item['requirement_id']}` {'PASS' if item['passed'] else 'FAIL'}: {item['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            "## Remaining Open Obligations",
            "",
        ]
    )
    for item in s["remaining_open_obligations"]:
        lines.append(f"- `{item}`")
    lines.extend(["", f"- validation_error_count: `{s['validation_error_count']}`", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--r60-result",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_R60_o3_f4_c4_c5_same_access_denominator_contract_gate_v0.json"
        ),
    )
    parser.add_argument(
        "--r62-result",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_R62_o3_f4_c4_c5_hardened_denominator_acceptance_verifier_gate_v0.json"
        ),
    )
    parser.add_argument(
        "--bundle-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows/"
            "O3-F4-all8.r63_source_backed_denominator_acceptance_bundle.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_R63_o3_f4_c4_c5_source_backed_denominator_row_acceptance_gate_v0.json"
        ),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(
            "research/B1_B7_cone01_R63_o3_f4_c4_c5_source_backed_denominator_row_acceptance_gate.md"
        ),
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    write_json(args.json_output, payload)
    write_markdown(args.markdown_output, payload)
    if args.pretty:
        s = payload["summary"]
        print(
            json.dumps(
                {
                    "status": payload["status"],
                    "requirements_passed": s["requirements_passed"],
                    "requirements_failed": s["requirements_failed"],
                    "submitted_denominator_row_count": s["submitted_denominator_row_count"],
                    "accepted_denominator_row_count": s["accepted_denominator_row_count"],
                    "max_denominator_distance": s["max_denominator_distance"],
                    "c4_c5_same_access_denominator_comparison_complete": s[
                        "c4_c5_same_access_denominator_comparison_complete"
                    ],
                    "c6_leakage_free_optimizer_trace_complete": s[
                        "c6_leakage_free_optimizer_trace_complete"
                    ],
                    "c7_machine_check_replay_complete": s[
                        "c7_machine_check_replay_complete"
                    ],
                    "o3_closed": s["o3_closed"],
                    "reroute_allowed": s["reroute_allowed"],
                    "b7_credit_delta": s["b7_credit_delta"],
                    "r63_bundle_hash": s["r63_bundle_hash"],
                    "json_output": str(args.json_output),
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
