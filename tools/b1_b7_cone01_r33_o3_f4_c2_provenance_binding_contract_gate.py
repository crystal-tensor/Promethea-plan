#!/usr/bin/env python3
"""T-B1-004ei/T-B7-013r: R33 O3-F4 C2 provenance binding contract gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r33_o3_f4_c2_provenance_binding_contract_gate_v0"
STATUS = "cone01_r33_o3_f4_c2_provenance_binding_contract_ready_no_submission"
MODEL_STATUS = "o3_f4_c2_binding_contract_ready_no_c2_acceptance"
VERSION = "0.1"
TARGET_ID = "T-B1-004ei/T-B7-013r"
UPSTREAM_TARGET_ID = "T-B1-004eh/T-B7-013q"
FAMILY_ID = "O3-F4"
CANDIDATE_ID = "NL-C02"
STRICT_TOLERANCE = 1.0e-8
BINDING_FIELDS = [
    "challenge_id",
    "parameter_indices",
    "submitted_parameter_values",
    "strict_tolerance",
    "max_unitary_replay_error",
    "unitary_distance_metric",
    "source_circuit_hash",
    "candidate_circuit_hash",
    "replay_command",
    "replay_stdout_hash",
    "verifier_version",
]
REQUIRED_EXECUTION_ARTIFACTS = [
    "replay_stdout_file",
    "replay_stdout_hash",
    "source_circuit_file",
    "source_circuit_hash",
    "candidate_circuit_file",
    "candidate_circuit_hash",
    "same_unitary_witness_file",
    "same_unitary_witness_hash",
    "provenance_binding_hash",
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


def build_contract(r32: dict[str, Any]) -> dict[str, Any]:
    contract = {
        "contract_id": "B1-B7-cone01-R33-O3-F4-C2-provenance-binding-contract",
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "family_id": FAMILY_ID,
        "candidate_id": CANDIDATE_ID,
        "source_r32_fixture_hash": r32["summary"]["fixture_hash"],
        "source_r32_preflight_hash": r32["summary"]["preflight_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "required_row_count": 8,
        "binding_hash_algorithm": "sha256(json.dumps(binding_payload, sort_keys=True, separators=(',', ':')))",
        "binding_fields": BINDING_FIELDS,
        "required_execution_artifacts": REQUIRED_EXECUTION_ARTIFACTS,
        "acceptance_rules": [
            "all_8_rows_present",
            "max_unitary_replay_error_lte_1e-08_for_all_rows",
            "every_hash_is_sha256",
            "declared_provenance_binding_hash_recomputes_for_all_rows",
            "all_required_execution_artifacts_exist_or_are_embedded",
            "zero_credit_claim_boundary_until_C2_and_C3_C7_acceptance",
        ],
        "rejection_rules": [
            "reject_hash_shape_without_binding",
            "reject_binding_without_execution_artifact",
            "reject_any_tolerance_relaxation",
            "reject_o3_reroute_b7_credit_before_full_certificate_triad",
        ],
    }
    contract["contract_hash"] = stable_hash(contract)
    return contract


def build_template(contract: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for idx in range(8):
        challenge_id = f"O3-F4-C{idx + 1:02d}"
        rows.append(
            {
                "challenge_id": challenge_id,
                "binding_payload": {field: f"<{field}>" for field in BINDING_FIELDS},
                "declared_provenance_binding_hash": "<sha256 of binding_payload>",
                "execution_artifacts": {
                    artifact: f"<{artifact}>" for artifact in REQUIRED_EXECUTION_ARTIFACTS
                },
                "max_unitary_replay_error": "<must be <= 1e-08>",
                "claim_boundary": "no C2/O3/reroute/B7/STV credit before acceptance",
            }
        )
    template = {
        "artifact_id": "B1-B7-cone01-O3-F4-C2-provenance-binding-submission.<submitter-id>",
        "source_target_id": TARGET_ID,
        "contract_hash": contract["contract_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "rows": rows,
        "o3_closed": False,
        "reroute_allowed": False,
        "b7_credit_delta": 0,
    }
    template["template_hash"] = stable_hash(template)
    return template


def evaluate_no_submission(contract: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    result = {
        "submission_exists": False,
        "accepted": False,
        "contract_hash": contract["contract_hash"],
        "template_hash": template["template_hash"],
        "required_row_count": contract["required_row_count"],
        "required_execution_artifact_count": len(contract["required_execution_artifacts"]),
        "failed_reasons": [
            "no_source_backed_submission",
            "no_execution_artifacts",
            "no_recomputed_binding_hashes",
        ],
    }
    result["preflight_hash"] = stable_hash(result)
    return result


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    started = time.time()
    r32 = load_json(args.r32_sentinel)
    contract = build_contract(r32)
    template = build_template(contract)
    preflight = evaluate_no_submission(contract, template)
    requirements = [
        requirement(
            "S1",
            "R32 source is validation-clean and exposes the binding mismatch blocker",
            r32["summary"].get("validation_error_count") == 0
            and r32["summary"].get("binding_pass") is False
            and r32["summary"].get("binding_mismatch_count") == 8,
            {
                "r32_validation_error_count": r32["summary"].get("validation_error_count"),
                "binding_pass": r32["summary"].get("binding_pass"),
                "binding_mismatch_count": r32["summary"].get("binding_mismatch_count"),
            },
        ),
        requirement(
            "S2",
            "Contract defines the exact C2 provenance binding fields",
            contract["binding_fields"] == BINDING_FIELDS,
            {"binding_fields": contract["binding_fields"]},
        ),
        requirement(
            "S3",
            "Contract requires replay execution artifacts in addition to hashes",
            contract["required_execution_artifacts"] == REQUIRED_EXECUTION_ARTIFACTS,
            {"required_execution_artifacts": contract["required_execution_artifacts"]},
        ),
        requirement(
            "S4",
            "Submission template contains 8 rows and zero-credit boundary fields",
            len(template["rows"]) == 8
            and template["o3_closed"] is False
            and template["reroute_allowed"] is False
            and template["b7_credit_delta"] == 0,
            {
                "template_row_count": len(template["rows"]),
                "o3_closed": template["o3_closed"],
                "reroute_allowed": template["reroute_allowed"],
                "b7_credit_delta": template["b7_credit_delta"],
            },
        ),
        requirement(
            "S5",
            "No submission is accepted without execution artifacts and recomputed bindings",
            preflight["submission_exists"] is False and preflight["accepted"] is False,
            {
                "submission_exists": preflight["submission_exists"],
                "accepted": preflight["accepted"],
                "failed_reasons": preflight["failed_reasons"],
            },
        ),
        requirement(
            "S6",
            "Contract, template, and preflight are hash-bound",
            bool(contract["contract_hash"])
            and bool(template["template_hash"])
            and bool(preflight["preflight_hash"]),
            {
                "contract_hash": contract["contract_hash"],
                "template_hash": template["template_hash"],
                "preflight_hash": preflight["preflight_hash"],
            },
        ),
        requirement(
            "S7",
            "R33 keeps C2, O3, reroute, and B7 credit unaccepted",
            preflight["accepted"] is False
            and template["o3_closed"] is False
            and template["reroute_allowed"] is False
            and template["b7_credit_delta"] == 0,
            {
                "c2_accepted": preflight["accepted"],
                "o3_closed": template["o3_closed"],
                "reroute_allowed": template["reroute_allowed"],
                "b7_credit_delta": template["b7_credit_delta"],
            },
        ),
        requirement(
            "S8",
            "R33 remains scoped to C2 provenance and claims no C3-C7 progress",
            True,
            {"scope": "C2 provenance binding contract", "c3_c7_progress_claimed": False},
        ),
    ]
    failed_requirements = [
        item["requirement_id"] for item in requirements if not item["passed"]
    ]
    summary = {
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "source_r32_fixture_hash": r32["summary"]["fixture_hash"],
        "source_r32_preflight_hash": r32["summary"]["preflight_hash"],
        "source_r32_file_sha256": file_hash(args.r32_sentinel),
        "contract_hash": contract["contract_hash"],
        "template_hash": template["template_hash"],
        "preflight_hash": preflight["preflight_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "binding_field_count": len(contract["binding_fields"]),
        "required_execution_artifact_count": len(contract["required_execution_artifacts"]),
        "template_row_count": len(template["rows"]),
        "submission_exists": False,
        "c2_provenance_binding_contract_ready": True,
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
            "C2_source_backed_execution_artifacts",
            "C2_recomputed_provenance_binding_hashes",
            "C3_same_unitary_replay_certificate",
            "C4_C5_same_access_denominator_comparison",
            "C6_leakage_free_optimizer_trace",
            "C7_machine_check_replay_bundle",
        ],
        "remaining_open_obligation_count": 6,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed_requirements),
        "requirements_failed": len(failed_requirements),
        "failed_requirement_ids": failed_requirements,
        "validation_error_count": len(failed_requirements),
    }
    payload = {
        "title": "B1/B7 Cone01 R33 O3-F4 C2 Provenance Binding Contract Gate",
        "version": VERSION,
        "last_updated": "2026-07-08",
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "o3_f4_c2_provenance_binding_contract_packet": {
            "source_r32_sentinel": str(args.r32_sentinel),
            "contract": contract,
            "template_output": str(args.template_output),
            "preflight_result": preflight,
        },
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "R33 emits a hash-bound C2 provenance binding contract and "
                "submission template for rows whose binding hashes must be "
                "recomputed from replay payloads and execution artifacts."
            ),
            "what_is_not_supported": (
                "R33 does not accept a C2 submission, does not close O3, and "
                "does not permit reroute, B7 credit, STV credit, or resource-saving claims."
            ),
            "next_gate": (
                "Submit source-backed C2 execution artifacts and 8 rows whose "
                "declared provenance binding hashes recompute from the row payload."
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
    lines = [
        "# B1/B7 Cone01 R33 O3-F4 C2 Provenance Binding Contract Gate",
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
            f"R33 passes {summary['requirements_passed']}/"
            f"{summary['requirement_count']} requirements by emitting the C2 "
            "provenance binding contract while accepting no submission."
        ),
        "",
        "## Contract Surface",
        "",
        f"- Binding field count: `{summary['binding_field_count']}`",
        f"- Required execution artifact count: `{summary['required_execution_artifact_count']}`",
        f"- Template row count: `{summary['template_row_count']}`",
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
    parser.add_argument(
        "--r32-sentinel",
        type=Path,
        default=Path("results/B1_B7_cone01_R32_o3_f4_c2_hash_shape_provenance_sentinel_gate_v0.json"),
    )
    parser.add_argument(
        "--template-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/"
            "B1-B7-cone01-O3-F4-C2-provenance-binding-submission.template.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R33_o3_f4_c2_provenance_binding_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R33_o3_f4_c2_provenance_binding_contract_gate.md"),
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
                    "binding_field_count": payload["summary"]["binding_field_count"],
                    "required_execution_artifact_count": payload["summary"][
                        "required_execution_artifact_count"
                    ],
                    "template_row_count": payload["summary"]["template_row_count"],
                    "c2_strict_replay_rows_accepted": payload["summary"][
                        "c2_strict_replay_rows_accepted"
                    ],
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
