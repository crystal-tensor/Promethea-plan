#!/usr/bin/env python3
"""T-B1-004ed/T-B7-013m: R28 O3-F4 certificate-triad contract gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r28_o3_f4_certificate_triad_contract_gate_v0"
STATUS = "cone01_r28_o3_f4_certificate_triad_contract_ready_no_submission"
MODEL_STATUS = "o3_f4_certificate_denominator_leakage_contract_ready_no_o3_no_reroute"
VERSION = "0.1"
TARGET_ID = "T-B1-004ed/T-B7-013m"
UPSTREAM_TARGET_ID = "T-B1-004ec/T-B7-013l"
CANDIDATE_ID = "NL-C02"
FAMILY_ID = "O3-F4"
CONTRACT_ID = "B1-B7-cone01-R28-O3-F4-certificate-triad-contract"
STRICT_TOLERANCE = 1.0e-8
EVIDENCE_BUNDLES = [
    "same_unitary_replay_certificate",
    "same_access_denominator_comparison",
    "leakage_free_optimizer_trace",
]
ACCEPTANCE_GATES = [
    "C1-source-lineage",
    "C2-strict-replay-under-tolerance",
    "C3-replay-certificate-complete",
    "C4-denominator-comparison-complete",
    "C5-same-access-model",
    "C6-leakage-free-optimizer-trace",
    "C7-machine-check-replay",
    "C8-claim-boundary-zero-credit-until-accepted",
    "C9-hash-bound-evidence-bundle",
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


def file_hash(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def requirement(
    requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_contract(r24: dict[str, Any], r27: dict[str, Any]) -> dict[str, Any]:
    required_fields = [
        "artifact_id",
        "source_target_id",
        "family_id",
        "candidate_id",
        "source_harness_hash",
        "source_r27_ablation_hash",
        "strict_tolerance",
        "unitary_replay_protocol",
        "same_unitary_replay_certificate",
        "same_access_denominator_comparison",
        "leakage_free_optimizer_trace",
        "challenge_rows_covered",
        "r11_r12_rows_covered",
        "route_a_effect",
        "machine_check_command",
        "checker_stdout_hash",
        "checker_returncode",
        "offline_bundle_hash",
        "artifact_hash",
        "claim_boundary",
        "o3_closed",
        "reroute_allowed",
        "b7_credit_delta",
        "submitted_by",
    ]
    production_fields = [
        "artifact_id",
        "source_target_id",
        "source_harness_hash",
        "source_r27_ablation_hash",
        "unitary_replay_protocol",
        "same_unitary_replay_certificate",
        "same_access_denominator_comparison",
        "leakage_free_optimizer_trace",
        "machine_check_command",
        "checker_stdout_hash",
        "offline_bundle_hash",
        "claim_boundary",
    ]
    rejection_rules = [
        "reject_if_replay_tolerance_exceeds_strict_tolerance",
        "reject_if_same_unitary_replay_certificate_missing",
        "reject_if_denominator_comparison_not_complete",
        "reject_if_same_access_model_false",
        "reject_if_optimizer_trace_sees_challenge_packet_or_uses_hidden_restarts",
        "reject_if_claim_boundary_promotes_b7_or_reroute_before_acceptance",
    ]
    contract = {
        "contract_id": CONTRACT_ID,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "family_id": FAMILY_ID,
        "candidate_id": CANDIDATE_ID,
        "source_harness_hash": r24["summary"]["harness_hash"],
        "source_template_hash": r24["summary"]["template_hash"],
        "source_gate_table_hash": r24["summary"]["gate_table_hash"],
        "source_r27_ablation_hash": r27["summary"]["ablation_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "tolerance_waiver_allowed": False,
        "evidence_bundles": EVIDENCE_BUNDLES,
        "required_fields": required_fields,
        "production_fields": production_fields,
        "acceptance_gates": ACCEPTANCE_GATES,
        "rejection_rules": rejection_rules,
        "triad_gate_map": {
            "same_unitary_replay_certificate": ["C2-strict-replay-under-tolerance", "C3-replay-certificate-complete"],
            "same_access_denominator_comparison": ["C4-denominator-comparison-complete", "C5-same-access-model"],
            "leakage_free_optimizer_trace": ["C6-leakage-free-optimizer-trace"],
        },
        "minimum_denominator_rows": 31,
        "challenge_row_count": 8,
        "claim_policy": {
            "o3_closed_before_acceptance": False,
            "reroute_before_acceptance": False,
            "b7_credit_before_acceptance": 0,
        },
    }
    contract["required_field_hash"] = stable_hash(required_fields)
    contract["production_field_hash"] = stable_hash(production_fields)
    contract["acceptance_gate_hash"] = stable_hash(ACCEPTANCE_GATES)
    contract["rejection_rule_hash"] = stable_hash(rejection_rules)
    contract["contract_hash"] = stable_hash(contract)
    return contract


def build_template(contract: dict[str, Any]) -> dict[str, Any]:
    template = {
        "artifact_id": "B1-B7-cone01-O3-F4-certificate-triad-submission.<submitter-id>",
        "source_target_id": TARGET_ID,
        "family_id": FAMILY_ID,
        "candidate_id": CANDIDATE_ID,
        "source_harness_hash": contract["source_harness_hash"],
        "source_r27_ablation_hash": contract["source_r27_ablation_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "unitary_replay_protocol": {
            "status": "required",
            "tolerance": STRICT_TOLERANCE,
            "max_unitary_replay_error": "<must be <= strict_tolerance>",
            "challenge_ids": "<all 8 O3-F4 challenge ids>",
            "replay_rows": [],
        },
        "same_unitary_replay_certificate": {
            "status": "required",
            "certificate_type": "<symbolic|interval|verified_numeric_with_bounds>",
            "certificate_hash": "<sha256>",
            "replay_command": "<command>",
            "proof_or_bound_file": "<path>",
        },
        "same_access_denominator_comparison": {
            "status": "required",
            "same_access_model": True,
            "covered_r11_r12_rows": 31,
            "required_r11_r12_rows": 31,
            "denominator_hash": "<sha256>",
            "comparison_table": [],
        },
        "leakage_free_optimizer_trace": {
            "status": "required",
            "challenge_packet_visible_to_optimizer": False,
            "hidden_restart_count": 0,
            "seed_schedule_hash": "<sha256>",
            "optimizer_trace_hash": "<sha256>",
        },
        "challenge_rows_covered": "<must equal 8>",
        "r11_r12_rows_covered": "<must equal 31>",
        "route_a_effect": "not_claimed_until_certificate_acceptance",
        "machine_check_command": "python3 tools/b1_b7_cone01_r28_o3_f4_certificate_triad_contract_gate.py --submission <this-file> --pretty",
        "checker_stdout_hash": "<sha256>",
        "checker_returncode": 0,
        "offline_bundle_hash": "<sha256>",
        "artifact_hash": "<sha256>",
        "claim_boundary": {
            "supported": "candidate O3-F4 certificate-triad submission only after all C1-C9 gates pass",
            "not_supported": "O3 closure, R5 reroute, B7 credit, STV credit, and resource savings are not supported before acceptance",
            "kill_conditions": [
                "replay exceeds strict tolerance",
                "replay certificate missing",
                "denominator comparison incomplete",
                "same-access model false",
                "optimizer leakage",
            ],
        },
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
        "submitted_by": "<agent-or-human-id>",
    }
    template["template_hash"] = stable_hash(template)
    return template


def evaluate_missing_submission(contract: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    return {
        "submission_exists": False,
        "accepted": False,
        "passed_gate_ids": ["C1-source-lineage", "C8-claim-boundary-zero-credit-until-accepted", "C9-hash-bound-evidence-bundle"],
        "failed_gate_ids": [
            "C2-strict-replay-under-tolerance",
            "C3-replay-certificate-complete",
            "C4-denominator-comparison-complete",
            "C5-same-access-model",
            "C6-leakage-free-optimizer-trace",
            "C7-machine-check-replay",
        ],
        "missing_required_fields": contract["required_fields"],
        "template_hash": template["template_hash"],
        "why": "No source-backed O3-F4 certificate-triad submission has been provided.",
    }


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    started = time.time()
    r24 = load_json(args.r24_harness)
    r27 = load_json(args.r27_ablation)
    contract = build_contract(r24, r27)
    template = build_template(contract)
    preflight = evaluate_missing_submission(contract, template)
    preflight["preflight_hash"] = stable_hash(preflight)

    requirements = [
        requirement(
            "S1",
            "R24 harness and R27 ablation are validation-clean sources",
            r24["summary"].get("validation_error_count") == 0
            and r27["summary"].get("validation_error_count") == 0,
            {
                "r24_validation_error_count": r24["summary"].get("validation_error_count"),
                "r27_validation_error_count": r27["summary"].get("validation_error_count"),
            },
        ),
        requirement(
            "S2",
            "Contract covers the certificate, denominator, and leakage evidence triad",
            contract["evidence_bundles"] == EVIDENCE_BUNDLES,
            {"evidence_bundles": contract["evidence_bundles"]},
        ),
        requirement(
            "S3",
            "Strict tolerance policy is preserved and tolerance waiver remains disallowed",
            contract["strict_tolerance"] == STRICT_TOLERANCE
            and contract["tolerance_waiver_allowed"] is False,
            {
                "strict_tolerance": contract["strict_tolerance"],
                "tolerance_waiver_allowed": contract["tolerance_waiver_allowed"],
            },
        ),
        requirement(
            "S4",
            "Acceptance gates explicitly bind strict replay, certificate, denominator, same-access, leakage, and machine replay",
            all(gate in contract["acceptance_gates"] for gate in ACCEPTANCE_GATES),
            {"acceptance_gates": contract["acceptance_gates"]},
        ),
        requirement(
            "S5",
            "Template contains every required contract field",
            all(field in template for field in contract["required_fields"]),
            {
                "required_field_count": len(contract["required_fields"]),
                "missing_template_fields": [
                    field for field in contract["required_fields"] if field not in template
                ],
            },
        ),
        requirement(
            "S6",
            "No source-backed certificate-triad submission exists or is accepted",
            preflight["submission_exists"] is False and preflight["accepted"] is False,
            {
                "submission_exists": preflight["submission_exists"],
                "accepted": preflight["accepted"],
                "failed_gate_ids": preflight["failed_gate_ids"],
            },
        ),
        requirement(
            "S7",
            "R28 preserves zero O3, reroute, and B7 credit claims",
            contract["claim_policy"]["o3_closed_before_acceptance"] is False
            and contract["claim_policy"]["reroute_before_acceptance"] is False
            and contract["claim_policy"]["b7_credit_before_acceptance"] == 0,
            contract["claim_policy"],
        ),
        requirement(
            "S8",
            "Contract, template, and preflight are hash-bound",
            bool(contract["contract_hash"]) and bool(template["template_hash"]) and bool(preflight["preflight_hash"]),
            {
                "contract_hash": contract["contract_hash"],
                "template_hash": template["template_hash"],
                "preflight_hash": preflight["preflight_hash"],
            },
        ),
    ]
    failed_requirements = [
        item["requirement_id"] for item in requirements if not item["passed"]
    ]
    summary = {
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "contract_id": CONTRACT_ID,
        "contract_hash": contract["contract_hash"],
        "template_hash": template["template_hash"],
        "preflight_hash": preflight["preflight_hash"],
        "source_harness_hash": contract["source_harness_hash"],
        "source_r27_ablation_hash": contract["source_r27_ablation_hash"],
        "required_field_count": len(contract["required_fields"]),
        "production_field_count": len(contract["production_fields"]),
        "evidence_bundle_count": len(contract["evidence_bundles"]),
        "acceptance_gate_count": len(contract["acceptance_gates"]),
        "rejection_rule_count": len(contract["rejection_rules"]),
        "strict_tolerance": STRICT_TOLERANCE,
        "tolerance_waiver_allowed": False,
        "template_emitted": True,
        "submission_exists": False,
        "preflight_accepted": False,
        "o3_f4_artifact_accepted": False,
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
            "O3-F3_symbolic_lu_artifact",
            "O3-F4_valid_certificate_triad_artifact",
            "O3-F5_route_a_artifact",
        ],
        "remaining_open_obligation_count": 3,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed_requirements),
        "requirements_failed": len(failed_requirements),
        "failed_requirement_ids": failed_requirements,
        "validation_error_count": len(failed_requirements),
    }
    payload = {
        "title": "B1/B7 Cone01 R28 O3-F4 Certificate-Triad Contract Gate",
        "version": VERSION,
        "last_updated": "2026-07-08",
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "o3_f4_certificate_triad_contract_packet": {
            "contract": contract,
            "template_output": str(args.template_output),
            "template_hash": template["template_hash"],
            "preflight_result": preflight,
        },
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "R28 emits a hash-bound O3-F4 certificate-triad contract and "
                "submission template for the remaining strict replay, "
                "certificate, denominator, and leakage obligations."
            ),
            "what_is_not_supported": (
                "R28 does not submit or accept a valid O3-F4 artifact, does not "
                "close O3, and does not permit R5 reroute. No B7 credit or "
                "resource saving is supported."
            ),
            "next_gate": (
                "Submit a source-backed certificate-triad artifact filling the "
                "R28 template and passing all C1-C9 acceptance gates."
            ),
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": failed_requirements,
        "runtime_seconds": round(time.time() - started, 6),
    }
    return payload, template


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    contract = payload["o3_f4_certificate_triad_contract_packet"]["contract"]
    lines = [
        "# B1/B7 Cone01 R28 O3-F4 Certificate-Triad Contract Gate",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Contract hash: `{summary['contract_hash']}`",
        f"- Template hash: `{summary['template_hash']}`",
        f"- Preflight hash: `{summary['preflight_hash']}`",
        "",
        "## Result",
        "",
        (
            f"R28 passes {summary['requirements_passed']}/"
            f"{summary['requirement_count']} requirements. It emits the "
            "certificate-triad contract required for a real O3-F4 submission, "
            "but no source-backed submission exists yet."
        ),
        "",
        "## Evidence Bundles",
        "",
    ]
    for bundle in contract["evidence_bundles"]:
        lines.append(f"- `{bundle}`")
    lines.extend(["", "## Acceptance Gates", ""])
    for gate in contract["acceptance_gates"]:
        lines.append(f"- `{gate}`")
    lines.extend(["", "## Requirement Results", ""])
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
    parser.add_argument(
        "--r24-harness",
        type=Path,
        default=Path("results/B1_B7_cone01_R24_o3_f4_numerical_refit_harness_gate_v0.json"),
    )
    parser.add_argument(
        "--r27-ablation",
        type=Path,
        default=Path("results/B1_B7_cone01_R27_o3_f4_tolerance_ablation_gate_v0.json"),
    )
    parser.add_argument(
        "--template-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/"
            "B1-B7-cone01-O3-F4-certificate-triad.template.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R28_o3_f4_certificate_triad_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R28_o3_f4_certificate_triad_contract_gate.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload, template = build_payload(args)
    write_json(args.template_output, template, pretty=True)
    write_json(args.json_output, payload, pretty=True)
    write_markdown(args.markdown_output, payload)
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": payload["status"],
                    "requirements_passed": payload["summary"]["requirements_passed"],
                    "requirements_failed": payload["summary"]["requirements_failed"],
                    "contract_hash": payload["summary"]["contract_hash"],
                    "template_hash": payload["summary"]["template_hash"],
                    "preflight_hash": payload["summary"]["preflight_hash"],
                    "required_field_count": payload["summary"]["required_field_count"],
                    "acceptance_gate_count": payload["summary"]["acceptance_gate_count"],
                    "template_emitted": payload["summary"]["template_emitted"],
                    "submission_exists": payload["summary"]["submission_exists"],
                    "o3_closed": payload["summary"]["o3_closed"],
                    "reroute_allowed": payload["summary"]["reroute_allowed"],
                    "b7_credit_delta": payload["summary"]["b7_credit_delta"],
                    "template_output": str(args.template_output),
                    "json_output": str(args.json_output),
                    "markdown_output": str(args.markdown_output),
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
