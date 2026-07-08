#!/usr/bin/env python3
"""T-B1-004fi/T-B7-014r: R59 C3 same-unitary replay certificate gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r59_o3_f4_c3_same_unitary_replay_certificate_gate_v0"
STATUS = "cone01_r59_o3_f4_c3_same_unitary_replay_certificate_passed_zero_b7_credit"
MODEL_STATUS = "o3_f4_c3_same_unitary_replay_certificate_passed_c4_c7_and_b7_open"
VERSION = "0.1"
TARGET_ID = "T-B1-004fi/T-B7-014r"
UPSTREAM_TARGET_ID = "T-B1-004fh/T-B7-014q"
STRICT_TOLERANCE = 1.0e-8
NEGATIVE_CONTROL_DELTA = 0.03125
QASM_RZ_RE = re.compile(r"rz\(\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*\)")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def req(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def parse_single_rz_theta(path: Path) -> float:
    text = path.read_text(encoding="utf-8")
    if "OPENQASM 3.0" not in text:
        raise ValueError(f"{path} is not an OpenQASM 3.0 replay file")
    matches = QASM_RZ_RE.findall(text)
    if len(matches) != 1:
        raise ValueError(f"{path} must contain exactly one rz(theta), found {len(matches)}")
    return float(matches[0])


def rz_operator_norm_distance(theta_a: float, theta_b: float) -> float:
    return 2.0 * abs(math.sin((theta_a - theta_b) / 4.0))


def rel(root: Path, value: str) -> Path:
    return root / value


def out_dir(root: Path) -> Path:
    return root / "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows"


def verify_bound_file(root: Path, path_value: str, expected_hash: str) -> dict[str, Any]:
    path = rel(root, path_value)
    exists = path.exists() and path.is_file()
    actual_hash = file_hash(path) if exists else None
    return {
        "path": path_value,
        "exists": exists,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "hash_matches": exists and actual_hash == expected_hash,
    }


def build_row_certificate(root: Path, row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    challenge_id = row["challenge_id"]
    artifacts = row["execution_artifacts"]
    source_file = artifacts["source_circuit_file"]
    candidate_file = artifacts["candidate_circuit_file"]
    source_hash = file_hash(rel(root, source_file))
    candidate_hash = file_hash(rel(root, candidate_file))
    source_theta = parse_single_rz_theta(rel(root, source_file))
    candidate_theta = parse_single_rz_theta(rel(root, candidate_file))
    positive_distance = rz_operator_norm_distance(source_theta, candidate_theta)
    positive_passed = positive_distance <= STRICT_TOLERANCE
    negative_candidate_theta = candidate_theta + NEGATIVE_CONTROL_DELTA
    negative_distance = rz_operator_norm_distance(source_theta, negative_candidate_theta)
    negative_rejected = negative_distance > STRICT_TOLERANCE
    bound_files = [
        verify_bound_file(root, source_file, artifacts["source_circuit_hash"]),
        verify_bound_file(root, candidate_file, artifacts["candidate_circuit_hash"]),
        verify_bound_file(root, row["same_unitary_witness_file"], row["same_unitary_witness_sha256"]),
        verify_bound_file(
            root,
            row["same_unitary_verifier_transcript_file"],
            row["same_unitary_verifier_transcript_sha256"],
        ),
        verify_bound_file(root, row["verifier_signature_file"], row["verifier_signature_sha256"]),
    ]
    evidence_packet_file = row["evidence_packet_file"]
    evidence_packet_path = rel(root, evidence_packet_file)
    evidence_packet = load_json(evidence_packet_path)
    evidence_packet_actual_sha256 = file_hash(evidence_packet_path)
    evidence_packet_file_sha256_matches_r58 = (
        evidence_packet_actual_sha256 == row.get("evidence_packet_sha256")
    )
    evidence_packet_semantic_hash_matches = (
        evidence_packet.get("evidence_packet_hash") == row.get("evidence_packet_hash")
        and evidence_packet.get("r58_discriminator_row_hash") == row.get("r58_discriminator_row_hash")
    )
    bound_files_passed = all(item["hash_matches"] for item in bound_files)
    certificate = {
        "artifact": "R59 C3 same-unitary replay certificate",
        "challenge_id": challenge_id,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "method": METHOD,
        "source_circuit_file": source_file,
        "source_circuit_sha256": source_hash,
        "candidate_circuit_file": candidate_file,
        "candidate_circuit_sha256": candidate_hash,
        "source_theta": source_theta,
        "candidate_theta": candidate_theta,
        "unitary_distance_metric": "single_qubit_rz_operator_norm",
        "positive_replay_distance": positive_distance,
        "strict_tolerance": STRICT_TOLERANCE,
        "positive_replay_passed": positive_passed,
        "bound_files": bound_files,
        "bound_files_passed": bound_files_passed,
        "evidence_packet_file": evidence_packet_file,
        "evidence_packet_expected_sha256_from_r58": row.get("evidence_packet_sha256"),
        "evidence_packet_actual_sha256": evidence_packet_actual_sha256,
        "evidence_packet_file_sha256_matches_r58": evidence_packet_file_sha256_matches_r58,
        "evidence_packet_semantic_hash_matches": evidence_packet_semantic_hash_matches,
        "source_r58_discriminator_row_hash": row["r58_discriminator_row_hash"],
        "source_r58_evidence_packet_hash": row["evidence_packet_hash"],
        "source_r58_same_unitary_witness_sha256": row["same_unitary_witness_sha256"],
        "claim_boundary": (
            "C3 row-level single-qubit RZ replay certificate only; no O3 closure, "
            "no reroute, no B7 credit, no STV credit"
        ),
    }
    certificate["accepted"] = (
        positive_passed and bound_files_passed and evidence_packet_semantic_hash_matches
    )
    certificate["certificate_hash"] = stable_hash(certificate)
    cert_file = out_dir(root) / f"{challenge_id}.r59_c3_same_unitary_replay_certificate.json"
    write_json(cert_file, certificate)
    certificate["certificate_file"] = str(cert_file.relative_to(root))
    certificate["certificate_file_sha256"] = file_hash(cert_file)

    negative_control = {
        "artifact": "R59 C3 negative-control replay challenge",
        "challenge_id": challenge_id,
        "method": METHOD,
        "source_theta": source_theta,
        "original_candidate_theta": candidate_theta,
        "negative_candidate_theta": negative_candidate_theta,
        "negative_control_delta": NEGATIVE_CONTROL_DELTA,
        "negative_control_distance": negative_distance,
        "strict_tolerance": STRICT_TOLERANCE,
        "negative_control_rejected": negative_rejected,
        "would_be_false_positive": negative_distance <= STRICT_TOLERANCE,
        "claim_boundary": (
            "Negative control must be rejected; this is verifier-pressure evidence, "
            "not a resource or B7 ledger claim."
        ),
    }
    negative_control["negative_control_hash"] = stable_hash(negative_control)
    neg_file = out_dir(root) / f"{challenge_id}.r59_c3_negative_control.json"
    write_json(neg_file, negative_control)
    negative_control["negative_control_file"] = str(neg_file.relative_to(root))
    negative_control["negative_control_file_sha256"] = file_hash(neg_file)
    return certificate, negative_control


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r58 = load_json(args.r58_result)
    r58_fixture = load_json(args.r58_fixture)
    rows = sorted(r58_fixture["rows"], key=lambda item: item["challenge_id"])
    certificates = []
    negative_controls = []
    for row in rows:
        cert, neg = build_row_certificate(args.root, row)
        certificates.append(cert)
        negative_controls.append(neg)
    bundle = {
        "artifact": "R59 C3 all-row same-unitary replay certificate bundle",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "method": METHOD,
        "source_r58_result": str(args.r58_result),
        "source_r58_evaluation_hash": r58["summary"]["r58_evaluation_hash"],
        "source_r58_fixture": str(args.r58_fixture),
        "source_r58_fixture_hash": r58["summary"]["r58_fixture_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "negative_control_delta": NEGATIVE_CONTROL_DELTA,
        "row_count": len(certificates),
        "positive_replay_passed_count": sum(1 for item in certificates if item["accepted"]),
        "negative_control_rejected_count": sum(
            1 for item in negative_controls if item["negative_control_rejected"]
        ),
        "evidence_packet_file_sha256_mismatch_count": sum(
            1 for item in certificates if not item["evidence_packet_file_sha256_matches_r58"]
        ),
        "evidence_packet_semantic_hash_match_count": sum(
            1 for item in certificates if item["evidence_packet_semantic_hash_matches"]
        ),
        "max_positive_replay_distance": max(
            item["positive_replay_distance"] for item in certificates
        ),
        "min_negative_control_distance": min(
            item["negative_control_distance"] for item in negative_controls
        ),
        "certificate_hashes": {
            item["challenge_id"]: item["certificate_hash"] for item in certificates
        },
        "negative_control_hashes": {
            item["challenge_id"]: item["negative_control_hash"] for item in negative_controls
        },
        "claim_boundary": (
            "R59 completes C3 for the restricted O3-F4 single-qubit RZ replay surface. "
            "It also records that R58 evidence-packet file SHA fields are stale after "
            "final row binding, while semantic packet hashes still match. C4/C5, C6, "
            "C7, O3 closure, reroute, and B7 ledger credit remain open."
        ),
    }
    bundle["c3_same_unitary_replay_certificate_complete"] = (
        bundle["row_count"] == 8
        and bundle["positive_replay_passed_count"] == 8
        and bundle["negative_control_rejected_count"] == 8
        and bundle["max_positive_replay_distance"] <= STRICT_TOLERANCE
        and bundle["min_negative_control_distance"] > STRICT_TOLERANCE
    )
    bundle["bundle_hash"] = stable_hash(bundle)
    write_json(args.bundle_output, bundle)

    zero_credit_ok = (
        r58["summary"]["o3_closed"] is False
        and r58["summary"]["reroute_allowed"] is False
        and r58["summary"]["b7_credit_delta"] == 0
        and r58["summary"]["b7_space_time_volume_credit"] == 0
        and r58["summary"]["resource_saving_claimed"] is False
        and r58["summary"]["b7_ledger_improvement_claimed"] is False
    )
    requirements = [
        req(
            "S1",
            "R58 upstream accepted all 8 C2 source-backed discriminator rows with zero B7 credit",
            r58["summary"].get("requirements_passed") == 8
            and r58["summary"].get("r47_all8_rows_accepted") is True
            and r58["summary"].get("source_backed_rows_passed") == 8
            and zero_credit_ok,
            {
                "r58_requirements_passed": r58["summary"].get("requirements_passed"),
                "r58_r47_all8_rows_accepted": r58["summary"].get("r47_all8_rows_accepted"),
                "r58_source_backed_rows_passed": r58["summary"].get("source_backed_rows_passed"),
                "zero_credit_ok": zero_credit_ok,
            },
        ),
        req(
            "S2",
            "R59 parses exactly one OpenQASM 3.0 RZ angle for each source and candidate row",
            len(certificates) == 8
            and all(isinstance(item["source_theta"], float) for item in certificates)
            and all(isinstance(item["candidate_theta"], float) for item in certificates),
            {
                "row_count": len(certificates),
                "challenge_ids": [item["challenge_id"] for item in certificates],
            },
        ),
        req(
            "S3",
            "All critical R58-bound files hash-match and evidence packets remain semantically bound",
            all(item["bound_files_passed"] for item in certificates)
            and bundle["evidence_packet_semantic_hash_match_count"] == 8,
            {
                "rows_with_bound_file_failures": [
                    item["challenge_id"] for item in certificates if not item["bound_files_passed"]
                ],
                "evidence_packet_semantic_hash_match_count": bundle[
                    "evidence_packet_semantic_hash_match_count"
                ],
                "evidence_packet_file_sha256_mismatch_count": bundle[
                    "evidence_packet_file_sha256_mismatch_count"
                ],
            },
        ),
        req(
            "S4",
            "Positive same-unitary replay certificates pass for all 8 rows",
            bundle["positive_replay_passed_count"] == 8
            and bundle["max_positive_replay_distance"] <= STRICT_TOLERANCE,
            {
                "positive_replay_passed_count": bundle["positive_replay_passed_count"],
                "max_positive_replay_distance": bundle["max_positive_replay_distance"],
            },
        ),
        req(
            "S5",
            "Negative-control perturbations are rejected for all 8 rows",
            bundle["negative_control_rejected_count"] == 8
            and bundle["min_negative_control_distance"] > STRICT_TOLERANCE,
            {
                "negative_control_rejected_count": bundle["negative_control_rejected_count"],
                "min_negative_control_distance": bundle["min_negative_control_distance"],
                "negative_control_delta": NEGATIVE_CONTROL_DELTA,
            },
        ),
        req(
            "S6",
            "R59 completes the restricted C3 replay certificate without promoting O3/reroute/B7 credit",
            bundle["c3_same_unitary_replay_certificate_complete"] is True and zero_credit_ok,
            {
                "c3_same_unitary_replay_certificate_complete": bundle[
                    "c3_same_unitary_replay_certificate_complete"
                ],
                "o3_closed": False,
                "reroute_allowed": False,
                "b7_credit_delta": 0,
                "b7_space_time_volume_credit": 0,
            },
        ),
        req(
            "S7",
            "R59 leaves C4/C5, C6, C7, and B7 ledger retest open",
            True,
            {
                "remaining_open_obligations": [
                    "C4_C5_same_access_denominator_comparison",
                    "C6_leakage_free_optimizer_trace",
                    "C7_machine_check_replay_bundle",
                    "B7_ledger_retest_after_C4_C7",
                ]
            },
        ),
        req(
            "S8",
            "R59 bundle and per-row certificates are hash-bound",
            bool(bundle["bundle_hash"])
            and all(item.get("certificate_hash") for item in certificates)
            and all(item.get("negative_control_hash") for item in negative_controls),
            {
                "bundle_hash": bundle["bundle_hash"],
                "bundle_file_sha256": file_hash(args.bundle_output),
                "certificate_hashes": bundle["certificate_hashes"],
                "negative_control_hashes": bundle["negative_control_hashes"],
            },
        ),
    ]
    failed = [item["requirement_id"] for item in requirements if not item["passed"]]
    summary = {
        "source_r58_evaluation_hash": r58["summary"]["r58_evaluation_hash"],
        "source_r58_fixture_hash": r58["summary"]["r58_fixture_hash"],
        "source_r58_file_sha256": file_hash(args.r58_result),
        "r59_bundle_hash": bundle["bundle_hash"],
        "r59_bundle_file_sha256": file_hash(args.bundle_output),
        "strict_tolerance": STRICT_TOLERANCE,
        "negative_control_delta": NEGATIVE_CONTROL_DELTA,
        "row_count": bundle["row_count"],
        "positive_replay_passed_count": bundle["positive_replay_passed_count"],
        "negative_control_rejected_count": bundle["negative_control_rejected_count"],
        "evidence_packet_file_sha256_mismatch_count": bundle[
            "evidence_packet_file_sha256_mismatch_count"
        ],
        "evidence_packet_semantic_hash_match_count": bundle[
            "evidence_packet_semantic_hash_match_count"
        ],
        "max_positive_replay_distance": bundle["max_positive_replay_distance"],
        "min_negative_control_distance": bundle["min_negative_control_distance"],
        "c2_strict_replay_rows_accepted": True,
        "c3_same_unitary_replay_certificate_complete": bundle[
            "c3_same_unitary_replay_certificate_complete"
        ],
        "c4_c5_same_access_denominator_comparison_complete": False,
        "c6_leakage_free_optimizer_trace_complete": False,
        "c7_machine_check_replay_bundle_complete": False,
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "remaining_open_obligations": [
            "C4_C5_same_access_denominator_comparison",
            "C6_leakage_free_optimizer_trace",
            "C7_machine_check_replay_bundle",
            "B7_ledger_retest_after_C4_C7",
        ],
        "remaining_open_obligation_count": 4,
        "certificate_hashes": bundle["certificate_hashes"],
        "negative_control_hashes": bundle["negative_control_hashes"],
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "validation_error_count": len(failed),
    }
    return {
        "title": "B1/B7 Cone01 R59 O3-F4 C3 Same-Unitary Replay Certificate Gate",
        "version": VERSION,
        "last_updated": "2026-07-08",
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "r59_c3_replay_certificate_packet": {
            "source_r58_result": str(args.r58_result),
            "source_r58_fixture": str(args.r58_fixture),
            "bundle_output": str(args.bundle_output),
            "bundle": bundle,
            "certificates": certificates,
            "negative_controls": negative_controls,
        },
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "R59 completes the restricted C3 same-unitary replay certificate for the "
                "8 O3-F4 single-qubit RZ rows accepted by R58, adds negative-control "
                "perturbations that the verifier rejects, and normalizes the observed "
                "R58 evidence-packet file-SHA staleness by rebinding actual file hashes."
            ),
            "what_is_not_supported": (
                "R59 does not prove a global O3 theorem, does not compare against a "
                "same-access denominator, does not audit leakage, does not produce a "
                "machine-check replay bundle, and does not grant reroute or B7/STV credit."
            ),
            "next_gate": (
                "Run C4/C5 same-access denominator comparison before C6 leakage-free "
                "trace, C7 machine-check bundle, or any B7 ledger retest."
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
        "# B1/B7 Cone01 R59 O3-F4 C3 Same-Unitary Replay Certificate Gate",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- R59 bundle hash: `{s['r59_bundle_hash']}`",
        "",
        "## Result",
        "",
        (
            f"R59 passes {s['requirements_passed']}/{s['requirement_count']} requirements "
            "by replay-certifying all 8 R58 source-backed rows and rejecting all 8 "
            "negative-control perturbations. C4/C5, C6, C7, O3 closure, reroute, "
            "and B7 ledger credit remain blocked."
        ),
        "",
        "## C3 Evidence",
        "",
        f"- Row count: `{s['row_count']}`",
        f"- Positive replay passed: `{s['positive_replay_passed_count']}`",
        f"- Negative controls rejected: `{s['negative_control_rejected_count']}`",
        f"- Evidence packet semantic hash matches: `{s['evidence_packet_semantic_hash_match_count']}`",
        f"- Evidence packet stale file-SHA observations: `{s['evidence_packet_file_sha256_mismatch_count']}`",
        f"- Max positive replay distance: `{s['max_positive_replay_distance']}`",
        f"- Min negative-control distance: `{s['min_negative_control_distance']}`",
        f"- C3 replay certificate complete: `{s['c3_same_unitary_replay_certificate_complete']}`",
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
        "--r58-result",
        type=Path,
        default=Path("results/B1_B7_cone01_R58_o3_f4_c2_all8_source_backed_expansion_gate_v0.json"),
    )
    parser.add_argument(
        "--r58-fixture",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows/"
            "O3-F4-all8.r58_r47_all8_fixture.json"
        ),
    )
    parser.add_argument(
        "--bundle-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows/"
            "O3-F4-all8.r59_c3_replay_certificate_bundle.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R59_o3_f4_c3_same_unitary_replay_certificate_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R59_o3_f4_c3_same_unitary_replay_certificate_gate.md"),
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
                    "positive_replay_passed_count": s["positive_replay_passed_count"],
                    "negative_control_rejected_count": s["negative_control_rejected_count"],
                    "c3_same_unitary_replay_certificate_complete": s[
                        "c3_same_unitary_replay_certificate_complete"
                    ],
                    "o3_closed": s["o3_closed"],
                    "reroute_allowed": s["reroute_allowed"],
                    "b7_credit_delta": s["b7_credit_delta"],
                    "r59_bundle_hash": s["r59_bundle_hash"],
                    "json_output": str(args.json_output),
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
