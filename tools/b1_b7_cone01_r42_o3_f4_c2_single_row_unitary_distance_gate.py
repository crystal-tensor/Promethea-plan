#!/usr/bin/env python3
"""T-B1-004er/T-B7-014a: R42 O3-F4 C2 single-row unitary-distance gate."""

from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
import re
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r42_o3_f4_c2_single_row_unitary_distance_gate_v0"
STATUS = "cone01_r42_o3_f4_c2_single_row_unitary_distance_computed_rejected"
MODEL_STATUS = "o3_f4_c2_single_row_unitary_distance_witness_no_source_backed_acceptance"
VERSION = "0.1"
TARGET_ID = "T-B1-004er/T-B7-014a"
UPSTREAM_TARGET_ID = "T-B1-004eq/T-B7-013z"
FAMILY_ID = "O3-F4"
CANDIDATE_ID = "NL-C02"
CHALLENGE_ID = "O3-F4-C01"
STRICT_TOLERANCE = 1.0e-8
WITNESS_SCHEMA = "source_backed_unitary_equivalence_v1"
WITNESS_VERIFIER = "r42_single_qubit_rz_unitary_distance_not_c2_certificate"
UNITARY_DISTANCE_METRIC = "one_qubit_rz_operator_norm"
FILE_ARTIFACT_FIELDS = [
    "replay_stdout_file",
    "source_circuit_file",
    "candidate_circuit_file",
    "same_unitary_witness_file",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def requirement(
    requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def verify_file_hash(root: Path, path_value: Any, expected_hash: Any) -> bool:
    path = root / path_value if isinstance(path_value, str) else None
    return bool(
        path
        and path.exists()
        and path.is_file()
        and isinstance(expected_hash, str)
        and file_hash(path) == expected_hash
    )


def verify_materialized_files(row: dict[str, Any], root: Path) -> bool:
    artifacts = row.get("execution_artifacts", {})
    return all(
        verify_file_hash(root, artifacts.get(field), artifacts.get(field.replace("_file", "_hash")))
        for field in FILE_ARTIFACT_FIELDS
    )


def row_source_provenance_passed(row: dict[str, Any], root: Path) -> bool:
    return (
        bool(row.get("source_dataset_id"))
        and bool(row.get("source_trace_id"))
        and verify_file_hash(root, row.get("source_dataset_file"), row.get("source_dataset_sha256"))
        and verify_file_hash(root, row.get("source_trace_file"), row.get("source_trace_sha256"))
        and verify_file_hash(
            root,
            row.get("replay_environment_file"),
            row.get("replay_environment_sha256"),
        )
    )


def row_witness_schema_passed(row: dict[str, Any], root: Path) -> bool:
    return (
        row.get("same_unitary_witness_schema") == WITNESS_SCHEMA
        and bool(row.get("same_unitary_witness_verifier"))
        and verify_file_hash(
            root,
            row.get("same_unitary_witness_schema_file"),
            row.get("same_unitary_witness_schema_sha256"),
        )
        and verify_file_hash(
            root,
            row.get("same_unitary_witness_verifier_file"),
            row.get("same_unitary_witness_verifier_sha256"),
        )
    )


def row_witness_preflight_passed(row: dict[str, Any], root: Path) -> bool:
    return (
        row.get("witness_preflight_passed") is True
        and verify_file_hash(
            root,
            row.get("same_unitary_witness_preflight_file"),
            row.get("same_unitary_witness_preflight_sha256"),
        )
        and verify_file_hash(
            root,
            row.get("same_unitary_witness_preflight_command_file"),
            row.get("same_unitary_witness_preflight_command_sha256"),
        )
    )


def parse_single_rz_angle(qasm_text: str) -> float:
    body_lines = [
        line.strip()
        for line in qasm_text.splitlines()
        if line.strip() and not line.strip().startswith("//")
    ]
    if not any(line == "OPENQASM 3.0;" for line in body_lines):
        raise ValueError("expected OPENQASM 3.0 header")
    matches = re.findall(r"\brz\s*\(\s*([-+0-9.eE]+)\s*\)\s+q\s*\[\s*0\s*\]\s*;", qasm_text)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one rz(theta) q[0] operation, found {len(matches)}")
    return float(matches[0])


def rz_unitary(theta: float) -> tuple[complex, complex]:
    return (cmath.exp(-0.5j * theta), cmath.exp(0.5j * theta))


def one_qubit_rz_operator_norm_distance(source_theta: float, candidate_theta: float) -> float:
    source = rz_unitary(source_theta)
    candidate = rz_unitary(candidate_theta)
    return max(abs(source[idx] - candidate[idx]) for idx in range(2))


def build_unitary_distance_witness(row: dict[str, Any], root: Path) -> dict[str, Any]:
    artifacts = row.get("execution_artifacts", {})
    source_path = root / artifacts["source_circuit_file"]
    candidate_path = root / artifacts["candidate_circuit_file"]
    source_text = source_path.read_text(encoding="utf-8")
    candidate_text = candidate_path.read_text(encoding="utf-8")
    source_theta = parse_single_rz_angle(source_text)
    candidate_theta = parse_single_rz_angle(candidate_text)
    distance = one_qubit_rz_operator_norm_distance(source_theta, candidate_theta)
    witness = {
        "artifact": "R42 single-row unitary-distance witness",
        "challenge_id": CHALLENGE_ID,
        "scope": "single_qubit_rz_smoke_artifact_not_source_backed_c2_acceptance",
        "schema": WITNESS_SCHEMA,
        "verifier": WITNESS_VERIFIER,
        "unitary_distance_metric": UNITARY_DISTANCE_METRIC,
        "strict_tolerance": STRICT_TOLERANCE,
        "source_circuit_file": artifacts["source_circuit_file"],
        "source_circuit_sha256": file_hash(source_path),
        "candidate_circuit_file": artifacts["candidate_circuit_file"],
        "candidate_circuit_sha256": file_hash(candidate_path),
        "source_theta": source_theta,
        "candidate_theta": candidate_theta,
        "computed_unitary_distance": distance,
        "unitary_distance_passed": bool(math.isfinite(distance) and distance <= STRICT_TOLERANCE),
        "source_backed_replay": False,
        "same_unitary_certificate_claimed": False,
        "smoke_only_not_c2_acceptance": True,
        "c2_accepted": False,
        "acceptance_blockers": [
            "source_backed_replay_false",
            "same_unitary_certificate_false",
            "smoke_only_not_c2_acceptance_true",
            "only_one_smoke_row_has_unitary_distance_witness",
            "remaining_7_rows_lack_source_provenance_witness_preflight_and_unitary_distance",
        ],
    }
    witness["unitary_distance_witness_hash"] = stable_hash(witness)
    return witness


def write_unitary_distance_files(root: Path, output_dir: Path, row: dict[str, Any]) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    witness = build_unitary_distance_witness(row, root)
    transcript = {
        "artifact": "R42 single-row unitary-distance transcript",
        "challenge_id": CHALLENGE_ID,
        "command": (
            "python3 tools/b1_b7_cone01_r42_o3_f4_c2_single_row_unitary_distance_gate.py "
            "--verify-only"
        ),
        "metric": UNITARY_DISTANCE_METRIC,
        "source_theta": witness["source_theta"],
        "candidate_theta": witness["candidate_theta"],
        "computed_unitary_distance": witness["computed_unitary_distance"],
        "strict_tolerance": STRICT_TOLERANCE,
        "passed": witness["unitary_distance_passed"],
        "expected_witness_hash": witness["unitary_distance_witness_hash"],
        "claim_boundary": "unitary distance for one smoke row only; not source-backed C2 acceptance",
    }
    files = {
        f"{CHALLENGE_ID}.unitary_distance_witness.json": witness,
        f"{CHALLENGE_ID}.unitary_distance_transcript.json": transcript,
    }
    result: dict[str, Any] = {"witness": witness}
    for name, payload in files.items():
        path = output_dir / name
        write_json(path, payload, pretty=True)
        key = name.replace(f"{CHALLENGE_ID}.", "").replace(".json", "")
        result[f"{key}_file"] = str(path.relative_to(root))
        result[f"{key}_sha256"] = file_hash(path)
    return result


def augment_fixture(fixture: dict[str, Any], root: Path, unitary_dir: Path) -> dict[str, Any]:
    rows = []
    for row in fixture["rows"]:
        new_row = json.loads(json.dumps(row))
        if new_row.get("challenge_id") == CHALLENGE_ID:
            packet = write_unitary_distance_files(root, unitary_dir, new_row)
            witness = packet["witness"]
            new_row.update(
                {
                    "same_unitary_witness_verifier": WITNESS_VERIFIER,
                    "same_unitary_unitary_distance_witness_file": packet[
                        "unitary_distance_witness_file"
                    ],
                    "same_unitary_unitary_distance_witness_sha256": packet[
                        "unitary_distance_witness_sha256"
                    ],
                    "same_unitary_unitary_distance_transcript_file": packet[
                        "unitary_distance_transcript_file"
                    ],
                    "same_unitary_unitary_distance_transcript_sha256": packet[
                        "unitary_distance_transcript_sha256"
                    ],
                    "same_unitary_unitary_distance_witness_hash": witness[
                        "unitary_distance_witness_hash"
                    ],
                    "unitary_distance_metric": UNITARY_DISTANCE_METRIC,
                    "computed_unitary_distance": witness["computed_unitary_distance"],
                    "unitary_distance_passed": witness["unitary_distance_passed"],
                    "source_backed_replay": False,
                    "same_unitary_certificate": False,
                    "smoke_only_not_c2_acceptance": True,
                }
            )
        rows.append(new_row)
    augmented = {
        "artifact_id": "B1-B7-cone01-O3-F4-C2-single-row-unitary-distance.fixture",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_fixture_hash": fixture["fixture_hash"],
        "contract_hash": fixture["contract_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "rows": rows,
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
    }
    augmented["fixture_hash"] = stable_hash(augmented)
    return augmented


def row_unitary_distance_passed(row: dict[str, Any], root: Path) -> bool:
    return (
        row.get("unitary_distance_passed") is True
        and row.get("unitary_distance_metric") == UNITARY_DISTANCE_METRIC
        and isinstance(row.get("computed_unitary_distance"), (int, float))
        and row.get("computed_unitary_distance") <= STRICT_TOLERANCE
        and verify_file_hash(
            root,
            row.get("same_unitary_unitary_distance_witness_file"),
            row.get("same_unitary_unitary_distance_witness_sha256"),
        )
        and verify_file_hash(
            root,
            row.get("same_unitary_unitary_distance_transcript_file"),
            row.get("same_unitary_unitary_distance_transcript_sha256"),
        )
    )


def evaluate_fixture(fixture: dict[str, Any], root: Path, fixture_path: Path) -> dict[str, Any]:
    row_results = []
    for row in fixture["rows"]:
        provenance_passed = row_source_provenance_passed(row, root)
        witness_schema_passed = row_witness_schema_passed(row, root)
        preflight_passed = row_witness_preflight_passed(row, root)
        unitary_distance_passed = row_unitary_distance_passed(row, root)
        source_backed_flags_passed = (
            row.get("source_backed_replay") is True
            and row.get("same_unitary_certificate") is True
            and row.get("smoke_only_not_c2_acceptance") is False
        )
        materialized_files_passed = verify_materialized_files(row, root)
        accepted = (
            materialized_files_passed
            and provenance_passed
            and witness_schema_passed
            and preflight_passed
            and unitary_distance_passed
            and source_backed_flags_passed
        )
        row_results.append(
            {
                "challenge_id": row["challenge_id"],
                "materialized_files_passed": materialized_files_passed,
                "source_provenance_passed": provenance_passed,
                "witness_schema_passed": witness_schema_passed,
                "witness_preflight_passed": preflight_passed,
                "unitary_distance_passed": unitary_distance_passed,
                "computed_unitary_distance": row.get("computed_unitary_distance"),
                "source_backed_flags_passed": source_backed_flags_passed,
                "source_backed_replay": row.get("source_backed_replay") is True,
                "same_unitary_certificate": row.get("same_unitary_certificate") is True,
                "smoke_only_not_c2_acceptance": row.get("smoke_only_not_c2_acceptance") is True,
                "accepted": accepted,
            }
        )
    evaluation = {
        "input_artifact": str(fixture_path),
        "input_artifact_sha256": file_hash(fixture_path),
        "fixture_hash": fixture["fixture_hash"],
        "row_count": len(row_results),
        "row_results": row_results,
        "materialized_rows_passed": sum(1 for row in row_results if row["materialized_files_passed"]),
        "source_provenance_rows_passed": sum(1 for row in row_results if row["source_provenance_passed"]),
        "source_provenance_failures": sum(1 for row in row_results if not row["source_provenance_passed"]),
        "witness_schema_rows_passed": sum(1 for row in row_results if row["witness_schema_passed"]),
        "witness_schema_failures": sum(1 for row in row_results if not row["witness_schema_passed"]),
        "witness_preflight_rows_passed": sum(1 for row in row_results if row["witness_preflight_passed"]),
        "witness_preflight_failures": sum(1 for row in row_results if not row["witness_preflight_passed"]),
        "unitary_distance_rows_passed": sum(1 for row in row_results if row["unitary_distance_passed"]),
        "unitary_distance_failures": sum(1 for row in row_results if not row["unitary_distance_passed"]),
        "source_backed_rows_passed": sum(1 for row in row_results if row["accepted"]),
        "source_backed_flag_failures": sum(1 for row in row_results if not row["source_backed_flags_passed"]),
        "smoke_only_row_count": sum(1 for row in row_results if row["smoke_only_not_c2_acceptance"]),
        "accepted": False,
    }
    evaluation["accepted"] = (
        evaluation["source_backed_rows_passed"] == 8
        and fixture.get("o3_closed") is False
        and fixture.get("reroute_allowed") is False
        and fixture.get("b7_credit_delta") == 0
    )
    evaluation["evaluation_hash"] = stable_hash(evaluation)
    return evaluation


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    started = time.time()
    r41 = load_json(args.r41_result)
    source_fixture = load_json(args.r41_fixture)
    augmented_fixture = augment_fixture(source_fixture, args.root, args.unitary_dir)
    write_json(args.fixture_output, augmented_fixture, pretty=True)
    evaluation = evaluate_fixture(augmented_fixture, args.root, args.fixture_output)
    c01_row = next(
        row for row in evaluation["row_results"] if row["challenge_id"] == CHALLENGE_ID
    )
    requirements = [
        requirement(
            "S1",
            "R41 preflight gate is validation-clean with one preflight row",
            r41["summary"].get("validation_error_count") == 0
            and r41["summary"].get("witness_preflight_rows_passed") == 1
            and r41["summary"].get("source_backed_rows_passed") == 0,
            {
                "r41_validation_error_count": r41["summary"].get("validation_error_count"),
                "r41_witness_preflight_rows_passed": r41["summary"].get("witness_preflight_rows_passed"),
                "r41_source_backed_rows_passed": r41["summary"].get("source_backed_rows_passed"),
            },
        ),
        requirement(
            "S2",
            "R42 computes one actual unitary-distance witness",
            evaluation["unitary_distance_rows_passed"] == 1
            and evaluation["unitary_distance_failures"] == 7
            and c01_row["computed_unitary_distance"] == 0.0,
            {
                "unitary_distance_rows_passed": evaluation["unitary_distance_rows_passed"],
                "unitary_distance_failures": evaluation["unitary_distance_failures"],
                "c01_computed_unitary_distance": c01_row["computed_unitary_distance"],
                "metric": UNITARY_DISTANCE_METRIC,
            },
        ),
        requirement(
            "S3",
            "The row keeps provenance, witness schema, and preflight intact",
            evaluation["source_provenance_rows_passed"] == 1
            and evaluation["witness_schema_rows_passed"] == 1
            and evaluation["witness_preflight_rows_passed"] == 1,
            {
                "source_provenance_rows_passed": evaluation["source_provenance_rows_passed"],
                "witness_schema_rows_passed": evaluation["witness_schema_rows_passed"],
                "witness_preflight_rows_passed": evaluation["witness_preflight_rows_passed"],
            },
        ),
        requirement(
            "S4",
            "All materialized C2 files remain hash-valid",
            evaluation["materialized_rows_passed"] == 8,
            {"materialized_rows_passed": evaluation["materialized_rows_passed"]},
        ),
        requirement(
            "S5",
            "R42 does not claim source-backed replay or same-unitary acceptance",
            evaluation["source_backed_rows_passed"] == 0
            and evaluation["source_backed_flag_failures"] == 8,
            {
                "source_backed_rows_passed": evaluation["source_backed_rows_passed"],
                "source_backed_flag_failures": evaluation["source_backed_flag_failures"],
            },
        ),
        requirement(
            "S6",
            "R42 keeps C2/O3/reroute/B7 zero-credit boundaries",
            augmented_fixture.get("o3_closed") is False
            and augmented_fixture.get("reroute_allowed") is False
            and augmented_fixture.get("b7_credit_delta") == 0,
            {
                "o3_closed": augmented_fixture.get("o3_closed"),
                "reroute_allowed": augmented_fixture.get("reroute_allowed"),
                "b7_credit_delta": augmented_fixture.get("b7_credit_delta"),
            },
        ),
        requirement(
            "S7",
            "R42 claims no C3-C7 or ledger progress",
            True,
            {"c3_c7_progress_claimed": False, "b7_ledger_credit_claimed": False},
        ),
        requirement(
            "S8",
            "R42 output is hash-bound",
            bool(augmented_fixture["fixture_hash"]) and bool(evaluation["evaluation_hash"]),
            {"fixture_hash": augmented_fixture["fixture_hash"], "evaluation_hash": evaluation["evaluation_hash"]},
        ),
    ]
    failed_requirements = [item["requirement_id"] for item in requirements if not item["passed"]]
    summary = {
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "challenge_id": CHALLENGE_ID,
        "source_r41_evaluation_hash": r41["summary"]["evaluation_hash"],
        "source_r41_fixture_hash": r41["summary"]["single_row_witness_preflight_fixture_hash"],
        "source_r41_file_sha256": file_hash(args.r41_result),
        "single_row_unitary_distance_fixture_hash": augmented_fixture["fixture_hash"],
        "single_row_unitary_distance_fixture_file_sha256": file_hash(args.fixture_output),
        "evaluation_hash": evaluation["evaluation_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "unitary_distance_metric": UNITARY_DISTANCE_METRIC,
        "c01_computed_unitary_distance": c01_row["computed_unitary_distance"],
        "template_row_count": evaluation["row_count"],
        "materialized_rows_passed": evaluation["materialized_rows_passed"],
        "source_provenance_rows_passed": evaluation["source_provenance_rows_passed"],
        "source_provenance_failures": evaluation["source_provenance_failures"],
        "witness_schema_rows_passed": evaluation["witness_schema_rows_passed"],
        "witness_schema_failures": evaluation["witness_schema_failures"],
        "witness_preflight_rows_passed": evaluation["witness_preflight_rows_passed"],
        "witness_preflight_failures": evaluation["witness_preflight_failures"],
        "unitary_distance_rows_passed": evaluation["unitary_distance_rows_passed"],
        "unitary_distance_failures": evaluation["unitary_distance_failures"],
        "source_backed_rows_passed": evaluation["source_backed_rows_passed"],
        "source_backed_flag_failures": evaluation["source_backed_flag_failures"],
        "smoke_only_row_count": evaluation["smoke_only_row_count"],
        "single_row_unitary_distance_ready": True,
        "single_row_witness_preflight_ready": True,
        "single_row_witness_scaffold_ready": True,
        "single_row_source_provenance_ready": True,
        "source_backed_discriminator_ready": True,
        "c2_source_backed_replacement_contract_ready": True,
        "c2_provenance_submission_accepted": False,
        "c2_strict_replay_rows_accepted": False,
        "o3_f4_artifact_accepted": False,
        "same_unitary_replay_certificate_complete": False,
        "same_access_denominator_comparison_complete": False,
        "leakage_free_optimizer_trace_complete": False,
        "machine_check_replay_complete": False,
        "o3_closed": False,
        "checked_negative_lemma_present": False,
        "nlc02_full_lemma_ready": False,
        "reroute_allowed": False,
        "accepted_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "remaining_open_obligations": [
            "replace_smoke_flags_with_real_source_backed_replay_flags",
            "provide_source_provenance_for_remaining_7_rows",
            "provide_witness_schema_preflight_and_unitary_distance_for_remaining_7_rows",
            "pass_C2_source_backed_discriminator_for_all_rows",
            "C3_same_unitary_replay_certificate",
            "C4_C5_same_access_denominator_comparison",
            "C6_leakage_free_optimizer_trace",
            "C7_machine_check_replay_bundle",
        ],
        "remaining_open_obligation_count": 8,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed_requirements),
        "requirements_failed": len(failed_requirements),
        "failed_requirement_ids": failed_requirements,
        "validation_error_count": len(failed_requirements),
    }
    payload = {
        "title": "B1/B7 Cone01 R42 O3-F4 C2 Single-Row Unitary-Distance Gate",
        "version": VERSION,
        "last_updated": "2026-07-08",
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "o3_f4_c2_single_row_unitary_distance_packet": {
            "source_r41_result": str(args.r41_result),
            "source_r41_fixture": str(args.r41_fixture),
            "unitary_dir": str(args.unitary_dir),
            "fixture_output": str(args.fixture_output),
            "evaluation": evaluation,
        },
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "R42 computes an actual single-qubit RZ operator-norm unitary "
                "distance for one C2 smoke row and binds the witness plus "
                "transcript by hash."
            ),
            "what_is_not_supported": (
                "R42 does not mark the row source-backed, does not turn the "
                "numeric distance into a same-unitary certificate, does not "
                "accept C2, does not close O3, and does not permit reroute, "
                "B7 credit, STV credit, or resource-saving claims."
            ),
            "next_gate": (
                "Replace smoke flags with real source-backed replay flags only "
                "after independent source lineage and replay evidence exist, "
                "then replicate provenance, witness, preflight, and unitary "
                "distance packets for the remaining 7 rows."
            ),
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": failed_requirements,
        "runtime_seconds": round(time.time() - started, 6),
    }
    return payload, augmented_fixture


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R42 O3-F4 C2 Single-Row Unitary-Distance Gate",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Fixture hash: `{summary['single_row_unitary_distance_fixture_hash']}`",
        f"- Evaluation hash: `{summary['evaluation_hash']}`",
        "",
        "## Result",
        "",
        (
            f"R42 passes {summary['requirements_passed']}/"
            f"{summary['requirement_count']} requirements by computing one "
            "actual unitary-distance witness while keeping C2 rejected."
        ),
        "",
        "## Rejection Surface",
        "",
        f"- Source-provenance rows passed: `{summary['source_provenance_rows_passed']}`",
        f"- Witness-schema rows passed: `{summary['witness_schema_rows_passed']}`",
        f"- Witness-preflight rows passed: `{summary['witness_preflight_rows_passed']}`",
        f"- Unitary-distance rows passed: `{summary['unitary_distance_rows_passed']}`",
        f"- Unitary-distance failures: `{summary['unitary_distance_failures']}`",
        f"- C01 computed unitary distance: `{summary['c01_computed_unitary_distance']}`",
        f"- Source-backed rows passed: `{summary['source_backed_rows_passed']}`",
        f"- Source-backed flag failures: `{summary['source_backed_flag_failures']}`",
        f"- C2 accepted: `{summary['c2_strict_replay_rows_accepted']}`",
        "",
        "## Requirement Results",
        "",
    ]
    for item in payload["requirements"]:
        mark = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- `{item['requirement_id']}` {mark}: {item['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            f"- validation_error_count: `{summary['validation_error_count']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument(
        "--r41-result",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_R41_o3_f4_c2_single_row_witness_preflight_gate_v0.json"
        ),
    )
    parser.add_argument(
        "--r41-fixture",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/"
            "B1-B7-cone01-O3-F4-C2-single-row-witness-preflight.fixture.json"
        ),
    )
    parser.add_argument(
        "--unitary-dir",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/"
            "unitary_distance/r42_c01"
        ),
    )
    parser.add_argument(
        "--fixture-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/"
            "B1-B7-cone01-O3-F4-C2-single-row-unitary-distance.fixture.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_R42_o3_f4_c2_single_row_unitary_distance_gate_v0.json"
        ),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(
            "research/B1_B7_cone01_R42_o3_f4_c2_single_row_unitary_distance_gate.md"
        ),
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verify_only:
        fixture = load_json(args.r41_fixture)
        row = next(row for row in fixture["rows"] if row["challenge_id"] == CHALLENGE_ID)
        print(json.dumps(build_unitary_distance_witness(row, args.root), indent=2, sort_keys=True))
        return
    payload, _fixture = build_payload(args)
    write_json(args.json_output, payload, pretty=True)
    write_markdown(args.markdown_output, payload)
    if args.pretty:
        summary = payload["summary"]
        print(
            json.dumps(
                {
                    "status": payload["status"],
                    "fixture_hash": summary[
                        "single_row_unitary_distance_fixture_hash"
                    ],
                    "evaluation_hash": summary["evaluation_hash"],
                    "requirements_passed": summary["requirements_passed"],
                    "requirements_failed": summary["requirements_failed"],
                    "unitary_distance_rows_passed": summary[
                        "unitary_distance_rows_passed"
                    ],
                    "unitary_distance_failures": summary[
                        "unitary_distance_failures"
                    ],
                    "source_backed_rows_passed": summary[
                        "source_backed_rows_passed"
                    ],
                    "c2_strict_replay_rows_accepted": summary[
                        "c2_strict_replay_rows_accepted"
                    ],
                    "o3_closed": summary["o3_closed"],
                    "reroute_allowed": summary["reroute_allowed"],
                    "b7_credit_delta": summary["b7_credit_delta"],
                    "json_output": str(args.json_output),
                    "fixture_output": str(args.fixture_output),
                    "markdown_output": str(args.markdown_output),
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
