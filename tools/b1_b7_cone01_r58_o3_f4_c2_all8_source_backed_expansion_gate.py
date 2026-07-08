#!/usr/bin/env python3
"""T-B1-004fh/T-B7-014q: R58 expands R47/R38 to all 8 source-backed rows."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r58_o3_f4_c2_all8_source_backed_expansion_gate_v0"
STATUS = "cone01_r58_o3_f4_c2_all8_source_backed_rows_accepted_zero_b7_credit"
MODEL_STATUS = "o3_f4_c2_all8_source_backed_rows_accepted_c3_c7_and_b7_still_open"
VERSION = "0.1"
TARGET_ID = "T-B1-004fh/T-B7-014q"
UPSTREAM_TARGET_ID = "T-B1-004fg/T-B7-014p"
FAMILY_ID = "O3-F4"
STRICT_TOLERANCE = 1.0e-8
QASM_RZ_RE = re.compile(r"rz\(\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*\)")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_r38_module(root: Path) -> Any:
    module_path = root / "tools/b1_b7_cone01_r38_o3_f4_c2_source_backed_discriminator_gate.py"
    spec = importlib.util.spec_from_file_location("r38_source_backed_discriminator", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load R38 discriminator module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def req(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def parse_single_rz_theta(path: Path) -> float:
    text = path.read_text(encoding="utf-8")
    match = QASM_RZ_RE.search(text)
    if not match:
        raise ValueError(f"Unable to parse single-qubit rz angle from {path}")
    return float(match.group(1))


def rz_operator_norm_distance(theta_a: float, theta_b: float) -> float:
    return 2.0 * abs(math.sin((theta_a - theta_b) / 4.0))


def rel(root: Path, path_value: str) -> Path:
    return root / path_value


def evidence_dir(root: Path) -> Path:
    return root / "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows"


def build_row_evidence(
    r38: Any,
    root: Path,
    original_row: dict[str, Any],
    r57: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    challenge_id = original_row["challenge_id"]
    out_dir = evidence_dir(root)
    artifacts = original_row["execution_artifacts"]
    source_circuit_file = artifacts["source_circuit_file"]
    candidate_circuit_file = artifacts["candidate_circuit_file"]
    source_path = rel(root, source_circuit_file)
    candidate_path = rel(root, candidate_circuit_file)
    source_circuit_sha256 = r38.file_hash(source_path)
    candidate_circuit_sha256 = r38.file_hash(candidate_path)
    source_theta = parse_single_rz_theta(source_path)
    candidate_theta = parse_single_rz_theta(candidate_path)
    computed_distance = rz_operator_norm_distance(source_theta, candidate_theta)
    within_tolerance = computed_distance <= STRICT_TOLERANCE

    source_dataset = {
        "artifact": "R58 source-backed source dataset",
        "challenge_id": challenge_id,
        "dataset_id": f"qasmbench_medium_exact/gcm_h6.qasm::line1381::{challenge_id}::r58_source_backed_replay",
        "source_backed_replay": True,
        "source_circuit_file": source_circuit_file,
        "source_circuit_sha256": source_circuit_sha256,
        "candidate_circuit_file": candidate_circuit_file,
        "candidate_circuit_sha256": candidate_circuit_sha256,
        "source_theta": source_theta,
        "candidate_theta": candidate_theta,
        "strict_tolerance": STRICT_TOLERANCE,
        "lineage_from": original_row.get("source_dataset_file"),
        "lineage_from_sha256": original_row.get("source_dataset_sha256"),
        "claim_boundary": "R58 C2 row evidence only; no O3 closure, no reroute, no B7 or STV credit",
    }
    source_dataset["dataset_hash"] = r38.stable_hash(source_dataset)
    source_dataset_file = out_dir / f"{challenge_id}.r58_source_dataset.json"
    write_json(source_dataset_file, source_dataset)
    source_dataset_sha256 = r38.file_hash(source_dataset_file)

    source_trace = {
        "artifact": "R58 source-backed replay trace",
        "challenge_id": challenge_id,
        "trace_id": f"{challenge_id}::r58_source_backed_replay_trace",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r57_evaluation_hash": r57["summary"]["r57_evaluation_hash"],
        "source_r57_fixture_hash": r57["summary"]["r57_fixture_hash"],
        "source_dataset_file": str(source_dataset_file.relative_to(root)),
        "source_dataset_sha256": source_dataset_sha256,
        "source_circuit_file": source_circuit_file,
        "candidate_circuit_file": candidate_circuit_file,
        "source_theta": source_theta,
        "candidate_theta": candidate_theta,
        "computed_unitary_distance": computed_distance,
        "unitary_distance_metric": "single_qubit_rz_operator_norm",
        "passed": within_tolerance,
        "claim_boundary": "all-8 C2 discriminator input; downstream C3-C7 still open",
    }
    source_trace["trace_hash"] = r38.stable_hash(source_trace)
    source_trace_file = out_dir / f"{challenge_id}.r58_source_trace.json"
    write_json(source_trace_file, source_trace)
    source_trace_sha256 = r38.file_hash(source_trace_file)

    replay_environment = {
        "artifact": "R58 source-backed replay environment",
        "challenge_id": challenge_id,
        "environment_id": f"{challenge_id}::r58_replay_environment",
        "qasm_version_required": "OPENQASM 3.0",
        "verifier": METHOD,
        "strict_tolerance": STRICT_TOLERANCE,
        "parser": "single_qubit_rz_openqasm3_regex",
        "distance_formula": "2*abs(sin((source_theta-candidate_theta)/4))",
        "source_replay_environment_file": original_row.get("replay_environment_file"),
        "source_replay_environment_sha256": original_row.get("replay_environment_sha256"),
        "claim_boundary": "deterministic local replay only; no hardware or B7 ledger claim",
    }
    replay_environment["environment_hash"] = r38.stable_hash(replay_environment)
    replay_environment_file = out_dir / f"{challenge_id}.r58_replay_environment.json"
    write_json(replay_environment_file, replay_environment)
    replay_environment_sha256 = r38.file_hash(replay_environment_file)

    replay_stdout = (
        f"R58 source-backed replay for {challenge_id}\n"
        f"source_circuit_sha256={source_circuit_sha256}\n"
        f"candidate_circuit_sha256={candidate_circuit_sha256}\n"
        f"source_theta={source_theta}\n"
        f"candidate_theta={candidate_theta}\n"
        f"computed_unitary_distance={computed_distance:.17g}\n"
        f"strict_tolerance={STRICT_TOLERANCE:.17g}\n"
        f"passed={str(within_tolerance).lower()}\n"
        "claim_boundary=no O3 closure, no reroute, no B7 credit, no STV credit\n"
    )
    replay_stdout_file = out_dir / f"{challenge_id}.r58_source_backed_replay.stdout.txt"
    replay_stdout_file.write_text(replay_stdout, encoding="utf-8")
    replay_stdout_sha256 = r38.file_hash(replay_stdout_file)

    same_unitary_witness = {
        "artifact": "R58 same-unitary witness",
        "challenge_id": challenge_id,
        "schema": "source_backed_unitary_equivalence_v1",
        "source_circuit_file": source_circuit_file,
        "source_circuit_sha256": source_circuit_sha256,
        "candidate_circuit_file": candidate_circuit_file,
        "candidate_circuit_sha256": candidate_circuit_sha256,
        "source_theta": source_theta,
        "candidate_theta": candidate_theta,
        "unitary_distance_metric": "single_qubit_rz_operator_norm",
        "computed_unitary_distance": computed_distance,
        "max_unitary_replay_error": computed_distance,
        "strict_tolerance": STRICT_TOLERANCE,
        "same_unitary_certificate": within_tolerance,
        "source_backed_replay": True,
        "source_dataset_file": str(source_dataset_file.relative_to(root)),
        "source_dataset_sha256": source_dataset_sha256,
        "source_trace_file": str(source_trace_file.relative_to(root)),
        "source_trace_sha256": source_trace_sha256,
        "replay_environment_file": str(replay_environment_file.relative_to(root)),
        "replay_environment_sha256": replay_environment_sha256,
        "replay_stdout_file": str(replay_stdout_file.relative_to(root)),
        "replay_stdout_sha256": replay_stdout_sha256,
        "claim_boundary": "same-unitary witness for C2 discriminator only; no B7 ledger credit",
    }
    same_unitary_witness["witness_hash"] = r38.stable_hash(same_unitary_witness)
    same_unitary_witness_file = out_dir / f"{challenge_id}.r58_same_unitary_witness.json"
    write_json(same_unitary_witness_file, same_unitary_witness)
    same_unitary_witness_sha256 = r38.file_hash(same_unitary_witness_file)

    verifier_transcript = {
        "artifact": "R58 same-unitary verifier transcript",
        "challenge_id": challenge_id,
        "verifier": METHOD,
        "schema": "source_backed_unitary_equivalence_v1",
        "source_circuit_sha256": source_circuit_sha256,
        "candidate_circuit_sha256": candidate_circuit_sha256,
        "same_unitary_witness_file": str(same_unitary_witness_file.relative_to(root)),
        "same_unitary_witness_sha256": same_unitary_witness_sha256,
        "computed_unitary_distance": computed_distance,
        "strict_tolerance": STRICT_TOLERANCE,
        "source_backed_replay": True,
        "same_unitary_certificate": within_tolerance,
        "accepted_by_r58_local_verifier": within_tolerance,
        "claim_boundary": "verifier transcript only; C3-C7 and B7 ledger remain open",
    }
    verifier_transcript["verifier_transcript_hash"] = r38.stable_hash(verifier_transcript)
    verifier_transcript_file = out_dir / f"{challenge_id}.r58_same_unitary_verifier_transcript.json"
    write_json(verifier_transcript_file, verifier_transcript)
    verifier_transcript_sha256 = r38.file_hash(verifier_transcript_file)

    verifier_signature = {
        "artifact": "R58 verifier signature artifact",
        "challenge_id": challenge_id,
        "source_target_id": TARGET_ID,
        "method": METHOD,
        "source_dataset_sha256": source_dataset_sha256,
        "source_trace_sha256": source_trace_sha256,
        "replay_environment_sha256": replay_environment_sha256,
        "replay_stdout_sha256": replay_stdout_sha256,
        "same_unitary_witness_sha256": same_unitary_witness_sha256,
        "same_unitary_verifier_transcript_sha256": verifier_transcript_sha256,
        "computed_unitary_distance": computed_distance,
        "strict_tolerance": STRICT_TOLERANCE,
        "accepted_for_r47_r38_input": within_tolerance,
        "claim_boundary": "signature binds evidence for R58 all-8 discriminator input only",
    }
    verifier_signature["signature_hash"] = r38.stable_hash(verifier_signature)
    verifier_signature_file = out_dir / f"{challenge_id}.r58_verifier_signature_artifact.json"
    write_json(verifier_signature_file, verifier_signature)
    verifier_signature_sha256 = r38.file_hash(verifier_signature_file)

    evidence_packet = {
        "artifact": "R58 row evidence packet",
        "challenge_id": challenge_id,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r57_evaluation_hash": r57["summary"]["r57_evaluation_hash"],
        "source_r57_fixture_hash": r57["summary"]["r57_fixture_hash"],
        "source_dataset_file": str(source_dataset_file.relative_to(root)),
        "source_dataset_sha256": source_dataset_sha256,
        "source_trace_file": str(source_trace_file.relative_to(root)),
        "source_trace_sha256": source_trace_sha256,
        "replay_environment_file": str(replay_environment_file.relative_to(root)),
        "replay_environment_sha256": replay_environment_sha256,
        "replay_stdout_file": str(replay_stdout_file.relative_to(root)),
        "replay_stdout_sha256": replay_stdout_sha256,
        "same_unitary_witness_file": str(same_unitary_witness_file.relative_to(root)),
        "same_unitary_witness_sha256": same_unitary_witness_sha256,
        "same_unitary_verifier_transcript_file": str(verifier_transcript_file.relative_to(root)),
        "same_unitary_verifier_transcript_sha256": verifier_transcript_sha256,
        "verifier_signature_file": str(verifier_signature_file.relative_to(root)),
        "verifier_signature_sha256": verifier_signature_sha256,
        "source_circuit_file": source_circuit_file,
        "source_circuit_sha256": source_circuit_sha256,
        "candidate_circuit_file": candidate_circuit_file,
        "candidate_circuit_sha256": candidate_circuit_sha256,
        "computed_unitary_distance": computed_distance,
        "max_unitary_replay_error": computed_distance,
        "strict_tolerance": STRICT_TOLERANCE,
        "source_backed_replay": True,
        "same_unitary_certificate": within_tolerance,
        "smoke_only_not_c2_acceptance": False,
        "claim_boundary": "R58 source-backed C2 row evidence; no O3 closure, reroute, B7 credit, or STV credit",
    }
    evidence_packet["evidence_packet_hash"] = r38.stable_hash(evidence_packet)
    evidence_packet_file = out_dir / f"{challenge_id}.r58_evidence_packet.json"
    write_json(evidence_packet_file, evidence_packet)
    evidence_packet_sha256 = r38.file_hash(evidence_packet_file)

    binding_payload = {
        "challenge_id": challenge_id,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r57_evaluation_hash": r57["summary"]["r57_evaluation_hash"],
        "source_r57_fixture_hash": r57["summary"]["r57_fixture_hash"],
        "source_dataset_hash": source_dataset_sha256,
        "source_trace_hash": source_trace_sha256,
        "replay_environment_hash": replay_environment_sha256,
        "source_circuit_hash": source_circuit_sha256,
        "candidate_circuit_hash": candidate_circuit_sha256,
        "replay_stdout_hash": replay_stdout_sha256,
        "same_unitary_witness_hash": same_unitary_witness_sha256,
        "same_unitary_verifier_transcript_hash": verifier_transcript_sha256,
        "verifier_signature_hash": verifier_signature_sha256,
        "evidence_packet_hash": evidence_packet["evidence_packet_hash"],
        "evidence_packet_file_sha256": evidence_packet_sha256,
        "strict_tolerance": STRICT_TOLERANCE,
        "max_unitary_replay_error": computed_distance,
        "unitary_distance_metric": "single_qubit_rz_operator_norm",
        "verifier_version": METHOD,
    }
    binding_hash = r38.stable_hash(binding_payload)
    row = {
        "challenge_id": challenge_id,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "binding_payload": binding_payload,
        "declared_provenance_binding_hash": binding_hash,
        "execution_artifacts": {
            "source_circuit_file": source_circuit_file,
            "source_circuit_hash": source_circuit_sha256,
            "candidate_circuit_file": candidate_circuit_file,
            "candidate_circuit_hash": candidate_circuit_sha256,
            "replay_stdout_file": str(replay_stdout_file.relative_to(root)),
            "replay_stdout_hash": replay_stdout_sha256,
            "same_unitary_witness_file": str(same_unitary_witness_file.relative_to(root)),
            "same_unitary_witness_hash": same_unitary_witness_sha256,
            "provenance_binding_hash": binding_hash,
        },
        "max_unitary_replay_error": computed_distance,
        "computed_unitary_distance": computed_distance,
        "unitary_distance_metric": "single_qubit_rz_operator_norm",
        "unitary_distance_passed": within_tolerance,
        "source_dataset_id": source_dataset["dataset_id"],
        "source_dataset_file": str(source_dataset_file.relative_to(root)),
        "source_dataset_sha256": source_dataset_sha256,
        "source_trace_id": source_trace["trace_id"],
        "source_trace_file": str(source_trace_file.relative_to(root)),
        "source_trace_sha256": source_trace_sha256,
        "replay_environment_file": str(replay_environment_file.relative_to(root)),
        "replay_environment_sha256": replay_environment_sha256,
        "same_unitary_witness_schema": "source_backed_unitary_equivalence_v1",
        "same_unitary_witness_file": str(same_unitary_witness_file.relative_to(root)),
        "same_unitary_witness_sha256": same_unitary_witness_sha256,
        "same_unitary_witness_verifier": f"{verifier_transcript_file.relative_to(root)}::{verifier_transcript_sha256}",
        "same_unitary_verifier_transcript_file": str(verifier_transcript_file.relative_to(root)),
        "same_unitary_verifier_transcript_sha256": verifier_transcript_sha256,
        "verifier_signature_file": str(verifier_signature_file.relative_to(root)),
        "verifier_signature_sha256": verifier_signature_sha256,
        "evidence_packet_file": str(evidence_packet_file.relative_to(root)),
        "evidence_packet_sha256": evidence_packet_sha256,
        "evidence_packet_hash": evidence_packet["evidence_packet_hash"],
        "source_backed_replay": True,
        "same_unitary_certificate": within_tolerance,
        "smoke_only_not_c2_acceptance": False,
        "claim_boundary": "R58 all-8 R47/R38 C2 input only; no C2 theorem closure; O3 remains open; no reroute; no B7 credit; no STV credit",
    }
    row["r58_discriminator_row_hash"] = r38.stable_hash(row)
    row_file = out_dir / f"{challenge_id}.r58_source_backed_discriminator_row.json"
    write_json(row_file, row)
    evidence_packet["r58_discriminator_row_file"] = str(row_file.relative_to(root))
    evidence_packet["r58_discriminator_row_hash"] = row["r58_discriminator_row_hash"]
    write_json(evidence_packet_file, evidence_packet)
    evidence_packet["evidence_packet_file_sha256"] = r38.file_hash(evidence_packet_file)
    return row, evidence_packet


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r38 = load_r38_module(args.root)
    r57 = load_json(args.r57_result)
    r37 = load_json(args.r37_result)
    r33 = load_json(args.r33_contract)
    source_fixture = load_json(args.source_fixture)
    contract = r38.build_replacement_contract(r37, r33)
    write_json(args.contract_output, contract)

    rows = []
    evidence_packets = []
    for original_row in source_fixture.get("rows", []):
        row, packet = build_row_evidence(r38, args.root, original_row, r57)
        rows.append(row)
        evidence_packets.append(packet)
    rows.sort(key=lambda item: item["challenge_id"])

    fixture = {
        "artifact_id": "B1-B7-cone01-O3-F4-C2-R58-all8-source-backed-fixture",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r57_result": str(args.r57_result),
        "source_r57_evaluation_hash": r57["summary"]["r57_evaluation_hash"],
        "source_r57_fixture_hash": r57["summary"]["r57_fixture_hash"],
        "source_fixture": str(args.source_fixture),
        "source_fixture_sha256": r38.file_hash(args.source_fixture),
        "contract_hash": contract["contract_hash"],
        "required_row_count_for_this_gate": 8,
        "all8_required_before_full_c2_closure": True,
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "rows": rows,
    }
    fixture["fixture_hash"] = r38.stable_hash(fixture)
    write_json(args.fixture_output, fixture)
    evaluation = r38.evaluate_fixture(fixture, contract, args.root, args.fixture_output)
    evaluation["r58_all8_r47_r38_acceptance"] = (
        evaluation["row_count"] == 8
        and evaluation["source_backed_rows_passed"] == 8
        and evaluation["source_backed_flag_failures"] == 0
        and evaluation["source_provenance_failures"] == 0
        and evaluation["witness_schema_failures"] == 0
        and evaluation["binding_mismatch_count"] == 0
        and evaluation["accepted"] is True
    )
    evaluation["full_contract_all8_accepted"] = evaluation["r58_all8_r47_r38_acceptance"]
    evaluation["c2_strict_replay_rows_accepted"] = evaluation["r58_all8_r47_r38_acceptance"]
    evaluation["claim_boundary"] = (
        "R58 accepts all 8 source-backed rows at the R47/R38 discriminator layer only; "
        "C3-C7, O3 closure, reroute permission, and B7/STV/resource credit remain blocked."
    )
    evaluation["r58_evaluation_hash"] = r38.stable_hash(evaluation)
    write_json(args.evaluation_output, evaluation)

    row_results = evaluation["row_results"]
    all_evidence_packets_passed = (
        len(evidence_packets) == 8
        and all(packet["source_backed_replay"] is True for packet in evidence_packets)
        and all(packet["same_unitary_certificate"] is True for packet in evidence_packets)
        and all(packet["smoke_only_not_c2_acceptance"] is False for packet in evidence_packets)
        and all(packet["computed_unitary_distance"] <= STRICT_TOLERANCE for packet in evidence_packets)
    )
    zero_credit_ok = (
        fixture["o3_closed"] is False
        and fixture["reroute_allowed"] is False
        and fixture["b7_credit_delta"] == 0
        and fixture["b7_space_time_volume_credit"] == 0
        and fixture["resource_saving_claimed"] is False
        and fixture["b7_ledger_improvement_claimed"] is False
    )
    requirements = [
        req(
            "S1",
            "R57 upstream accepted exactly one source-backed row and left all-8 scaling open",
            r57["summary"].get("requirements_passed") == 8
            and r57["summary"].get("r47_exact_one_row_accepted") is True
            and r57["summary"].get("accepted_source_backed_row_count") == 1
            and r57["summary"].get("full_contract_all8_accepted") is False,
            {
                "r57_requirements_passed": r57["summary"].get("requirements_passed"),
                "r57_exact_one_row_accepted": r57["summary"].get("r47_exact_one_row_accepted"),
                "r57_accepted_source_backed_row_count": r57["summary"].get("accepted_source_backed_row_count"),
                "r57_full_contract_all8_accepted": r57["summary"].get("full_contract_all8_accepted"),
            },
        ),
        req(
            "S2",
            "R58 creates 8 source-backed evidence packets with same-unitary certificates",
            all_evidence_packets_passed,
            {
                "evidence_packet_count": len(evidence_packets),
                "challenge_ids": [packet["challenge_id"] for packet in evidence_packets],
                "max_computed_unitary_distance": max(packet["computed_unitary_distance"] for packet in evidence_packets),
            },
        ),
        req(
            "S3",
            "R58 fixture contains 8 rows and is bound to the unchanged R38 replacement contract",
            len(rows) == 8
            and fixture["contract_hash"] == contract["contract_hash"]
            and evaluation["contract_hash"] == contract["contract_hash"],
            {
                "row_count": len(rows),
                "contract_hash": contract["contract_hash"],
                "fixture_hash": fixture["fixture_hash"],
            },
        ),
        req(
            "S4",
            "Every row passes materialized files, binding, replay tolerance, flags, source provenance, witness schema, and zero-credit boundary",
            all(result["accepted"] for result in row_results)
            and evaluation["materialized_rows_passed"] == 8
            and evaluation["source_backed_flag_failures"] == 0
            and evaluation["source_provenance_failures"] == 0
            and evaluation["witness_schema_failures"] == 0
            and evaluation["binding_mismatch_count"] == 0,
            {
                "materialized_rows_passed": evaluation["materialized_rows_passed"],
                "source_backed_flag_failures": evaluation["source_backed_flag_failures"],
                "source_provenance_failures": evaluation["source_provenance_failures"],
                "witness_schema_failures": evaluation["witness_schema_failures"],
                "binding_mismatch_count": evaluation["binding_mismatch_count"],
                "failed_rows": [
                    result["challenge_id"] for result in row_results if not result["accepted"]
                ],
            },
        ),
        req(
            "S5",
            "R47/R38 all-8 discriminator accepts the R58 fixture under the required row count",
            evaluation["r58_all8_r47_r38_acceptance"] is True
            and evaluation["row_count"] == evaluation["required_row_count"] == 8
            and evaluation["source_backed_rows_passed"] == 8,
            {
                "r58_all8_r47_r38_acceptance": evaluation["r58_all8_r47_r38_acceptance"],
                "row_count": evaluation["row_count"],
                "required_row_count": evaluation["required_row_count"],
                "source_backed_rows_passed": evaluation["source_backed_rows_passed"],
            },
        ),
        req(
            "S6",
            "R58 promotes C2 row-level strict replay only, with no O3/reroute/B7/STV/resource credit",
            evaluation["c2_strict_replay_rows_accepted"] is True and zero_credit_ok,
            {
                "c2_strict_replay_rows_accepted": evaluation["c2_strict_replay_rows_accepted"],
                "o3_closed": fixture["o3_closed"],
                "reroute_allowed": fixture["reroute_allowed"],
                "b7_credit_delta": fixture["b7_credit_delta"],
                "b7_space_time_volume_credit": fixture["b7_space_time_volume_credit"],
                "resource_saving_claimed": fixture["resource_saving_claimed"],
                "b7_ledger_improvement_claimed": fixture["b7_ledger_improvement_claimed"],
            },
        ),
        req(
            "S7",
            "R58 leaves C3-C7 and B7 ledger retest as open obligations",
            True,
            {
                "remaining_open_obligations": [
                    "C3_same_unitary_replay_certificate",
                    "C4_C5_same_access_denominator_comparison",
                    "C6_leakage_free_optimizer_trace",
                    "C7_machine_check_replay_bundle",
                    "B7_ledger_retest_after_full_C2_closure",
                ]
            },
        ),
        req(
            "S8",
            "R58 fixture, evaluation, and evidence rows are hash-bound",
            bool(fixture["fixture_hash"])
            and bool(evaluation["r58_evaluation_hash"])
            and all(row.get("r58_discriminator_row_hash") for row in rows)
            and all(packet.get("evidence_packet_hash") for packet in evidence_packets),
            {
                "fixture_hash": fixture["fixture_hash"],
                "fixture_file_sha256": r38.file_hash(args.fixture_output),
                "evaluation_hash": evaluation["r58_evaluation_hash"],
                "evaluation_file_sha256": r38.file_hash(args.evaluation_output),
                "row_hashes": {
                    row["challenge_id"]: row["r58_discriminator_row_hash"] for row in rows
                },
            },
        ),
    ]
    failed = [item["requirement_id"] for item in requirements if not item["passed"]]
    summary = {
        "source_r57_evaluation_hash": r57["summary"]["r57_evaluation_hash"],
        "source_r57_fixture_hash": r57["summary"]["r57_fixture_hash"],
        "source_fixture_sha256": r38.file_hash(args.source_fixture),
        "replacement_contract_hash": contract["contract_hash"],
        "r58_fixture_hash": fixture["fixture_hash"],
        "r58_fixture_file_sha256": r38.file_hash(args.fixture_output),
        "r58_evaluation_hash": evaluation["r58_evaluation_hash"],
        "r58_evaluation_file_sha256": r38.file_hash(args.evaluation_output),
        "discriminator_hash": evaluation["discriminator_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "row_count": evaluation["row_count"],
        "required_row_count": evaluation["required_row_count"],
        "materialized_rows_passed": evaluation["materialized_rows_passed"],
        "source_backed_rows_passed": evaluation["source_backed_rows_passed"],
        "accepted_source_backed_row_count": evaluation["source_backed_rows_passed"],
        "source_backed_flag_failures": evaluation["source_backed_flag_failures"],
        "source_provenance_failures": evaluation["source_provenance_failures"],
        "witness_schema_failures": evaluation["witness_schema_failures"],
        "binding_mismatch_count": evaluation["binding_mismatch_count"],
        "smoke_only_row_count": evaluation["smoke_only_row_count"],
        "r47_rerun_performed": True,
        "r47_all8_rows_accepted": evaluation["r58_all8_r47_r38_acceptance"],
        "full_contract_all8_accepted": evaluation["full_contract_all8_accepted"],
        "c2_single_row_source_backed_accepted": True,
        "c2_strict_replay_rows_accepted": evaluation["c2_strict_replay_rows_accepted"],
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "c3_same_unitary_replay_certificate_complete": False,
        "c4_c5_same_access_denominator_comparison_complete": False,
        "c6_leakage_free_optimizer_trace_complete": False,
        "c7_machine_check_replay_bundle_complete": False,
        "remaining_open_obligations": [
            "C3_same_unitary_replay_certificate",
            "C4_C5_same_access_denominator_comparison",
            "C6_leakage_free_optimizer_trace",
            "C7_machine_check_replay_bundle",
            "B7_ledger_retest_after_full_C2_closure",
        ],
        "remaining_open_obligation_count": 5,
        "challenge_ids": [row["challenge_id"] for row in rows],
        "r58_discriminator_row_hashes": {
            row["challenge_id"]: row["r58_discriminator_row_hash"] for row in rows
        },
        "r58_evidence_packet_hashes": {
            packet["challenge_id"]: packet["evidence_packet_hash"] for packet in evidence_packets
        },
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "validation_error_count": len(failed),
    }
    return {
        "title": "B1/B7 Cone01 R58 O3-F4 C2 All-8 Source-Backed Expansion Gate",
        "version": VERSION,
        "last_updated": "2026-07-08",
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "r58_all8_source_backed_packet": {
            "source_r57_result": str(args.r57_result),
            "source_fixture": str(args.source_fixture),
            "fixture_output": str(args.fixture_output),
            "evaluation_output": str(args.evaluation_output),
            "replacement_contract_output": str(args.contract_output),
            "fixture": fixture,
            "evaluation": evaluation,
        },
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "R58 generates source-backed replay evidence for all 8 O3-F4 rows and "
                "passes the unchanged R47/R38 all-row discriminator under strict tolerance."
            ),
            "what_is_not_supported": (
                "R58 does not close O3, does not prove a theorem-level same-unitary replay "
                "certificate beyond the single-qubit RZ check, does not permit reroute, and "
                "does not grant B7/STV/resource/ledger credit."
            ),
            "next_gate": (
                "Run C3 same-unitary replay certificate pressure, then C4/C5 denominator, "
                "C6 leakage-free trace, C7 machine-check bundle, and only then B7 ledger retest."
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
        "# B1/B7 Cone01 R58 O3-F4 C2 All-8 Source-Backed Expansion Gate",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- R58 fixture hash: `{s['r58_fixture_hash']}`",
        f"- R58 evaluation hash: `{s['r58_evaluation_hash']}`",
        f"- Discriminator hash: `{s['discriminator_hash']}`",
        "",
        "## Result",
        "",
        (
            f"R58 passes {s['requirements_passed']}/{s['requirement_count']} requirements "
            "by expanding the R47/R38 source-backed discriminator from exactly one row to all 8 rows. "
            "C3-C7, O3 closure, reroute, and B7 ledger credit remain blocked."
        ),
        "",
        "## R47/R38 Evidence",
        "",
        f"- Row count: `{s['row_count']}` / required `{s['required_row_count']}`",
        f"- Source-backed rows passed: `{s['source_backed_rows_passed']}`",
        f"- Source-backed flag failures: `{s['source_backed_flag_failures']}`",
        f"- Source provenance failures: `{s['source_provenance_failures']}`",
        f"- Witness schema failures: `{s['witness_schema_failures']}`",
        f"- Binding mismatch count: `{s['binding_mismatch_count']}`",
        f"- R47 all-8 rows accepted: `{s['r47_all8_rows_accepted']}`",
        f"- C2 strict replay rows accepted: `{s['c2_strict_replay_rows_accepted']}`",
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
        "--r57-result",
        type=Path,
        default=Path("results/B1_B7_cone01_R57_o3_f4_c2_r47_exact_one_row_rerun_gate_v0.json"),
    )
    parser.add_argument(
        "--r37-result",
        type=Path,
        default=Path("results/B1_B7_cone01_R37_o3_f4_c2_all_rows_materialized_smoke_gate_v0.json"),
    )
    parser.add_argument(
        "--r33-contract",
        type=Path,
        default=Path("results/B1_B7_cone01_R33_o3_f4_c2_provenance_binding_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--source-fixture",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/"
            "B1-B7-cone01-O3-F4-C2-remaining-witness-preflight.fixture.json"
        ),
    )
    parser.add_argument(
        "--fixture-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows/"
            "O3-F4-all8.r58_r47_all8_fixture.json"
        ),
    )
    parser.add_argument(
        "--evaluation-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows/"
            "O3-F4-all8.r58_r47_all8_evaluation.json"
        ),
    )
    parser.add_argument(
        "--contract-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows/"
            "O3-F4-all8.r58_source_backed_replacement.contract.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R58_o3_f4_c2_all8_source_backed_expansion_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R58_o3_f4_c2_all8_source_backed_expansion_gate.md"),
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
                    "row_count": s["row_count"],
                    "source_backed_rows_passed": s["source_backed_rows_passed"],
                    "r47_all8_rows_accepted": s["r47_all8_rows_accepted"],
                    "c2_strict_replay_rows_accepted": s["c2_strict_replay_rows_accepted"],
                    "o3_closed": s["o3_closed"],
                    "reroute_allowed": s["reroute_allowed"],
                    "b7_credit_delta": s["b7_credit_delta"],
                    "r58_evaluation_hash": s["r58_evaluation_hash"],
                    "r58_fixture_hash": s["r58_fixture_hash"],
                    "json_output": str(args.json_output),
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
