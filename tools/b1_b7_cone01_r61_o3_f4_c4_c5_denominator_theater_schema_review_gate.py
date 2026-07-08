#!/usr/bin/env python3
"""T-B1-004fk/T-B7-014t: R61 C4/C5 denominator-theater schema review gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r61_o3_f4_c4_c5_denominator_theater_schema_review_gate_v0"
STATUS = "cone01_r61_denominator_theater_schema_review_passed_zero_b7_credit"
MODEL_STATUS = "r60_schema_hardened_against_field_presence_denominator_theater"
VERSION = "0.1"
TARGET_ID = "T-B1-004fk/T-B7-014t"
UPSTREAM_TARGET_ID = "T-B1-004fj/T-B7-014s"
HARDENED_SCHEMA_VERSION = "r61_c4_c5_same_access_denominator_row_hardened_v1"


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


def out_dir(root: Path) -> Path:
    return root / "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows"


def repo_path_exists(root: Path, value: str) -> bool:
    return bool(value) and (root / value).exists()


def is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def build_theater_row(root: Path, template: dict[str, Any]) -> dict[str, Any]:
    challenge_id = template["challenge_id"]
    missing_impl = (
        "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows/"
        f"{challenge_id}.r61_missing_denominator_impl.py"
    )
    missing_transcript = (
        "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows/"
        f"{challenge_id}.r61_missing_denominator_transcript.json"
    )
    row = {
        "challenge_id": challenge_id,
        "acceptance_schema_version": template["acceptance_schema_version"],
        "denominator_method_id": "adversarial_metadata_only_denominator_theater_v0",
        "denominator_implementation_path": missing_impl,
        "reproducible_command": f"python3 {missing_impl} --claim-zero-distance",
        "access_model_hash": template["access_model_hash"],
        "same_access_statement": "I used the same inputs, trust this statement.",
        "source_circuit_file": template["source_circuit_file"],
        "source_circuit_sha256": template["source_circuit_sha256"],
        "candidate_circuit_file": template["candidate_circuit_file"],
        "candidate_circuit_sha256": template["candidate_circuit_sha256"],
        "r59_certificate_file": template["r59_certificate_file"],
        "r59_certificate_hash": template["r59_certificate_hash"],
        "unitary_distance_metric": template["unitary_distance_metric"],
        "strict_tolerance": template["strict_tolerance"],
        "denominator_distance": 0.0,
        "denominator_cost_units": "self_asserted_zero_cost",
        "denominator_cost_value": 0,
        "denominator_beats_r59_positive_distance": True,
        "denominator_rejects_r59_negative_control_pressure": True,
        "leakage_audit_statement": "No leakage observed.",
        "verifier_transcript_path": missing_transcript,
        "verifier_transcript_sha256": "f" * 64,
        "claim_boundary": "Claims C4/C5 denominator win and permits B7 credit.",
        "attack_model": "field_presence_only_denominator_theater",
        "self_asserted_denominator_win": True,
        "denominator_distance_source": "self_asserted_not_transcript_bound",
        "reproducible_command_replayed": False,
        "structured_leakage_audit": False,
    }
    row["required_fields_present"] = all(
        field in row and row[field] not in (None, "") for field in template["required_fields"]
    )
    row["naive_field_presence_accepts"] = row["required_fields_present"]
    violations = []
    if row["acceptance_schema_version"] != template["acceptance_schema_version"]:
        violations.append("schema_version_mismatch")
    if row["access_model_hash"] != template["access_model_hash"]:
        violations.append("access_model_hash_mismatch")
    if row["source_circuit_sha256"] != template["source_circuit_sha256"]:
        violations.append("source_hash_mismatch")
    if row["candidate_circuit_sha256"] != template["candidate_circuit_sha256"]:
        violations.append("candidate_hash_mismatch")
    if row["r59_certificate_hash"] != template["r59_certificate_hash"]:
        violations.append("r59_certificate_hash_mismatch")
    if not repo_path_exists(root, row["denominator_implementation_path"]):
        violations.append("missing_denominator_implementation_path")
    if not repo_path_exists(root, row["verifier_transcript_path"]):
        violations.append("missing_verifier_transcript_path")
    if row["verifier_transcript_sha256"] == "f" * 64:
        violations.append("unbound_verifier_transcript_sha256")
    if row["reproducible_command_replayed"] is not True:
        violations.append("reproducible_command_not_replayed")
    if row["structured_leakage_audit"] is not True:
        violations.append("leakage_audit_not_structured")
    if row["denominator_distance_source"] != "verifier_transcript_bound":
        violations.append("denominator_distance_self_asserted")
    if not is_finite_number(row["denominator_distance"]):
        violations.append("denominator_distance_not_finite")
    if "B7 credit" in row["claim_boundary"] or "denominator win" in row["claim_boundary"]:
        violations.append("claim_boundary_overclaims_credit")
    row["hardened_rejection_reasons"] = violations
    row["hardened_acceptance_passed"] = len(violations) == 0
    row["row_hash"] = stable_hash(row)
    row_file = out_dir(root) / f"{challenge_id}.r61_denominator_theater_attack_row.json"
    write_json(row_file, row)
    row["row_file"] = str(row_file.relative_to(root))
    row["row_file_sha256"] = file_hash(row_file)
    return row


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r60 = load_json(args.r60_result)
    r60_summary = r60["summary"]
    templates = sorted(
        r60["r60_c4_c5_denominator_contract_packet"]["templates"],
        key=lambda item: item["challenge_id"],
    )
    attack_rows = [build_theater_row(args.root, item) for item in templates]
    hardening_rules = [
        "denominator_implementation_path must exist in the repository and hash-match a reviewed file",
        "reproducible_command must be replayed by the verifier, not merely provided as text",
        "verifier_transcript_path must exist and its SHA-256 must match verifier_transcript_sha256",
        "denominator_distance must be parsed from the verifier transcript, not self-asserted",
        "same_access_statement must be structured against the template access_model_hash",
        "leakage_audit_statement must be structured and enumerate every forbidden input class",
        "denominator_beats_r59_positive_distance must be computed from transcript-bound distance",
        "denominator_rejects_r59_negative_control_pressure must be checked against row-specific negative-control pressure",
        "claim_boundary must explicitly keep O3/reroute/B7/STV credit false until all C4-C7 gates pass",
        "acceptance requires all eight rows to pass before C4/C5 comparison can close",
    ]
    bundle = {
        "artifact": "R61 C4/C5 denominator-theater adversarial schema review bundle",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "method": METHOD,
        "hardened_schema_version": HARDENED_SCHEMA_VERSION,
        "source_r60_result": str(args.r60_result),
        "source_r60_file_sha256": file_hash(args.r60_result),
        "source_r60_contract_hash": r60_summary["r60_contract_hash"],
        "row_count": len(attack_rows),
        "attack_row_count": len(attack_rows),
        "naive_field_presence_accept_count": sum(
            1 for item in attack_rows if item["naive_field_presence_accepts"]
        ),
        "hardened_reject_count": sum(
            1 for item in attack_rows if not item["hardened_acceptance_passed"]
        ),
        "hardened_accept_count": sum(
            1 for item in attack_rows if item["hardened_acceptance_passed"]
        ),
        "unique_hardened_rejection_reasons": sorted(
            {
                reason
                for item in attack_rows
                for reason in item["hardened_rejection_reasons"]
            }
        ),
        "hardening_rule_count": len(hardening_rules),
        "hardening_rules": hardening_rules,
        "attack_row_hashes": {item["challenge_id"]: item["row_hash"] for item in attack_rows},
        "attack_row_files": {item["challenge_id"]: item["row_file"] for item in attack_rows},
        "c4_c5_same_access_denominator_schema_hardened": len(attack_rows) == 8
        and all(item["naive_field_presence_accepts"] for item in attack_rows)
        and all(not item["hardened_acceptance_passed"] for item in attack_rows),
        "c4_c5_same_access_denominator_comparison_complete": False,
        "accepted_denominator_row_count": 0,
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "claim_boundary": (
            "R61 adversarially reviews the R60 schema and rejects metadata-only "
            "field-presence denominator theater. It hardens the next acceptance "
            "verifier but does not accept denominator rows, close C4/C5, close O3, "
            "reroute, or grant B7/STV/resource credit."
        ),
    }
    bundle["bundle_hash"] = stable_hash(bundle)
    write_json(args.bundle_output, bundle)
    zero_credit_ok = (
        r60_summary["o3_closed"] is False
        and r60_summary["reroute_allowed"] is False
        and r60_summary["b7_credit_delta"] == 0
        and r60_summary["b7_space_time_volume_credit"] == 0
        and r60_summary["resource_saving_claimed"] is False
        and r60_summary["b7_ledger_improvement_claimed"] is False
    )
    requirements = [
        req(
            "A1",
            "R60 upstream emitted all 8 C4/C5 denominator templates with zero credit",
            r60_summary["c4_c5_same_access_denominator_contract_emitted"] is True
            and r60_summary["template_count"] == 8
            and zero_credit_ok,
            {
                "r60_template_count": r60_summary["template_count"],
                "r60_contract_hash": r60_summary["r60_contract_hash"],
                "zero_credit_ok": zero_credit_ok,
            },
        ),
        req(
            "A2",
            "R61 emits one field-presence theater row for each R60 template",
            len(attack_rows) == 8
            and len({item["challenge_id"] for item in attack_rows}) == 8,
            {
                "attack_row_count": len(attack_rows),
                "challenge_ids": [item["challenge_id"] for item in attack_rows],
            },
        ),
        req(
            "A3",
            "Naive required-field checking would accept every adversarial row",
            bundle["naive_field_presence_accept_count"] == 8,
            {"naive_field_presence_accept_count": bundle["naive_field_presence_accept_count"]},
        ),
        req(
            "A4",
            "The hardened verifier rejects every adversarial row",
            bundle["hardened_reject_count"] == 8 and bundle["hardened_accept_count"] == 0,
            {
                "hardened_reject_count": bundle["hardened_reject_count"],
                "hardened_accept_count": bundle["hardened_accept_count"],
                "unique_rejection_reasons": bundle["unique_hardened_rejection_reasons"],
            },
        ),
        req(
            "A5",
            "R61 emits hardened acceptance rules that close the field-presence loophole",
            bundle["hardening_rule_count"] == 10
            and bundle["c4_c5_same_access_denominator_schema_hardened"] is True,
            {
                "hardening_rule_count": bundle["hardening_rule_count"],
                "hardened_schema_version": bundle["hardened_schema_version"],
            },
        ),
        req(
            "A6",
            "R61 accepts no denominator rows and keeps C4/C5 incomplete",
            bundle["accepted_denominator_row_count"] == 0
            and bundle["c4_c5_same_access_denominator_comparison_complete"] is False,
            {
                "accepted_denominator_row_count": bundle["accepted_denominator_row_count"],
                "c4_c5_same_access_denominator_comparison_complete": bundle[
                    "c4_c5_same_access_denominator_comparison_complete"
                ],
            },
        ),
        req(
            "A7",
            "R61 preserves O3/reroute/B7 zero-credit boundaries",
            zero_credit_ok
            and bundle["o3_closed"] is False
            and bundle["reroute_allowed"] is False
            and bundle["b7_credit_delta"] == 0,
            {
                "o3_closed": bundle["o3_closed"],
                "reroute_allowed": bundle["reroute_allowed"],
                "b7_credit_delta": bundle["b7_credit_delta"],
                "b7_space_time_volume_credit": bundle["b7_space_time_volume_credit"],
            },
        ),
        req(
            "A8",
            "R61 bundle and per-row attack artifacts are hash-bound",
            bool(bundle["bundle_hash"]) and all(item["row_file_sha256"] for item in attack_rows),
            {
                "bundle_hash": bundle["bundle_hash"],
                "bundle_file_sha256": file_hash(args.bundle_output),
                "attack_row_hashes": bundle["attack_row_hashes"],
            },
        ),
    ]
    failed = [item["requirement_id"] for item in requirements if not item["passed"]]
    summary = {
        "source_r60_contract_hash": r60_summary["r60_contract_hash"],
        "source_r60_file_sha256": file_hash(args.r60_result),
        "r61_bundle_hash": bundle["bundle_hash"],
        "r61_bundle_file_sha256": file_hash(args.bundle_output),
        "row_count": bundle["row_count"],
        "attack_row_count": bundle["attack_row_count"],
        "naive_field_presence_accept_count": bundle["naive_field_presence_accept_count"],
        "hardened_reject_count": bundle["hardened_reject_count"],
        "hardened_accept_count": bundle["hardened_accept_count"],
        "hardening_rule_count": bundle["hardening_rule_count"],
        "hardened_schema_version": HARDENED_SCHEMA_VERSION,
        "c4_c5_same_access_denominator_schema_hardened": bundle[
            "c4_c5_same_access_denominator_schema_hardened"
        ],
        "c4_c5_same_access_denominator_comparison_complete": False,
        "accepted_denominator_row_count": 0,
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "remaining_open_obligations": [
            "implement_R61_hardened_acceptance_verifier",
            "submit_C4_C5_same_access_denominator_rows_with_existing_transcripts",
            "accept_8_denominator_rows_under_R61_hardened_schema",
            "C6_leakage_free_optimizer_trace",
            "C7_machine_check_replay_bundle",
            "B7_ledger_retest_after_C4_C7",
        ],
        "remaining_open_obligation_count": 6,
        "unique_hardened_rejection_reasons": bundle["unique_hardened_rejection_reasons"],
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "validation_error_count": len(failed),
    }
    return {
        "title": "B1/B7 Cone01 R61 O3-F4 C4/C5 Denominator-Theater Schema Review Gate",
        "version": VERSION,
        "last_updated": "2026-07-08",
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "r61_denominator_theater_schema_review_packet": {
            "source_r60_result": str(args.r60_result),
            "bundle_output": str(args.bundle_output),
            "bundle": bundle,
            "attack_rows": attack_rows,
        },
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "R61 proves that a naive R60 required-field checker is insufficient, "
                "because metadata-only adversarial rows can satisfy every field while "
                "lacking implementation, transcript, replay, structured leakage audit, "
                "and transcript-bound distance evidence. It emits hardened acceptance "
                "rules and rejects all eight adversarial rows."
            ),
            "what_is_not_supported": (
                "R61 does not accept any denominator row, does not complete C4/C5, "
                "does not audit C6 leakage, does not produce a C7 machine-check bundle, "
                "and does not grant O3/reroute/B7/STV credit."
            ),
            "next_gate": (
                "Implement the R61 hardened acceptance verifier and submit real "
                "source-backed denominator rows with existing implementation and "
                "verifier transcript artifacts."
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
        "# B1/B7 Cone01 R61 O3-F4 C4/C5 Denominator-Theater Schema Review Gate",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- R61 bundle hash: `{s['r61_bundle_hash']}`",
        "",
        "## Result",
        "",
        (
            f"R61 passes {s['requirements_passed']}/{s['requirement_count']} adversarial "
            "schema-review requirements. It creates 8 metadata-only theater rows that "
            "would pass naive required-field checking, then rejects all 8 under the "
            "R61 hardened schema. C4/C5, C6, C7, O3 closure, reroute, and B7 ledger "
            "credit remain blocked."
        ),
        "",
        "## Adversarial Evidence",
        "",
        f"- Attack rows: `{s['attack_row_count']}`",
        f"- Naive field-presence accepts: `{s['naive_field_presence_accept_count']}`",
        f"- Hardened rejects: `{s['hardened_reject_count']}`",
        f"- Hardened accepts: `{s['hardened_accept_count']}`",
        f"- Hardening rules: `{s['hardening_rule_count']}`",
        f"- Hardened schema version: `{s['hardened_schema_version']}`",
        f"- C4/C5 comparison complete: `{s['c4_c5_same_access_denominator_comparison_complete']}`",
        f"- B7 credit delta: `{s['b7_credit_delta']}`",
        "",
        "## Rejection Reasons",
        "",
    ]
    for item in s["unique_hardened_rejection_reasons"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Requirement Results", ""])
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
        "--bundle-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/source_backed_rows/"
            "O3-F4-all8.r61_denominator_theater_schema_review_bundle.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_R61_o3_f4_c4_c5_denominator_theater_schema_review_gate_v0.json"
        ),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(
            "research/B1_B7_cone01_R61_o3_f4_c4_c5_denominator_theater_schema_review_gate.md"
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
                    "attack_row_count": s["attack_row_count"],
                    "naive_field_presence_accept_count": s[
                        "naive_field_presence_accept_count"
                    ],
                    "hardened_reject_count": s["hardened_reject_count"],
                    "hardened_accept_count": s["hardened_accept_count"],
                    "hardening_rule_count": s["hardening_rule_count"],
                    "c4_c5_same_access_denominator_schema_hardened": s[
                        "c4_c5_same_access_denominator_schema_hardened"
                    ],
                    "c4_c5_same_access_denominator_comparison_complete": s[
                        "c4_c5_same_access_denominator_comparison_complete"
                    ],
                    "o3_closed": s["o3_closed"],
                    "reroute_allowed": s["reroute_allowed"],
                    "b7_credit_delta": s["b7_credit_delta"],
                    "r61_bundle_hash": s["r61_bundle_hash"],
                    "json_output": str(args.json_output),
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
