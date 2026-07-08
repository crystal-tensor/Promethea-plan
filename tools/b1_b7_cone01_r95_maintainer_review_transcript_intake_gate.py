#!/usr/bin/env python3
"""T-B1-004gs/T-B7-016b: R95 maintainer review transcript intake."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r95_maintainer_review_transcript_intake_gate_v0"
STATUS = "cone01_r95_review_transcript_intake_open_no_transcript_yet"
MODEL_STATUS = "r94_verdict_contract_ready_but_review_transcript_missing"
VERSION = "0.1"
TARGET_ID = "T-B1-004gs/T-B7-016b"
UPSTREAM_TARGET_ID = "T-B1-004gr/T-B7-016a"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"

R94_RESULT = "results/B1_B7_cone01_R94_maintainer_verdict_counter_contract_gate_v0.json"
R94_VERDICT_CONTRACT = f"{SUBMISSION_DIR}/R94-G1-maintainer-verdict-contract.json"
R94_VERDICT_TEMPLATE = f"{SUBMISSION_DIR}/R94-G1-maintainer-verdict.template.json"
R94_PREFLIGHT = f"{SUBMISSION_DIR}/R94-G1-maintainer-verdict-preflight.verdict.json"
R94_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R94-G1-post-verdict-blocker-queue.json"

R95_TRANSCRIPT_CONTRACT = f"{SUBMISSION_DIR}/R95-G1-maintainer-review-transcript-contract.json"
R95_TRANSCRIPT_TEMPLATE = f"{SUBMISSION_DIR}/R95-G1-maintainer-review-transcript.template.json"
R95_EMPTY_TRANSCRIPT = f"{SUBMISSION_DIR}/R95-G1-empty-maintainer-review-transcript.json"
R95_PREFLIGHT = f"{SUBMISSION_DIR}/R95-G1-maintainer-review-transcript-preflight.verdict.json"
R95_STDOUT = f"{SUBMISSION_DIR}/R95-G1-maintainer-review-transcript.stdout.txt"
R95_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R95-G1-post-review-transcript-blocker-queue.json"

RESULT_PATH = "results/B1_B7_cone01_R95_maintainer_review_transcript_intake_gate_v0.json"
REPORT_PATH = "research/B1_B7_cone01_R95_maintainer_review_transcript_intake_gate.md"

TRANSCRIPT_REQUIRED_FIELDS = [
    "transcript_id",
    "reviewer_agent_id",
    "reviewed_r93_packet_path",
    "reviewed_r93_packet_sha256",
    "reviewed_r93_packet_hash",
    "source_r94_verdict_contract_hash",
    "source_r94_verdict_template_hash",
    "command_transcript_path",
    "command_transcript_sha256",
    "environment_manifest_path",
    "environment_manifest_sha256",
    "recomputed_target_rows_path",
    "recomputed_target_rows_sha256",
    "double_count_test_path",
    "double_count_test_sha256",
    "review_notes_path",
    "review_notes_sha256",
    "evidence_sufficiency_label",
    "counter_target",
    "proposed_credit_decision",
    "proposed_counter_delta",
    "one_unit_credit_preserved",
    "one_unit_credit_revoked",
    "new_credit_delta",
    "claim_boundary",
    "o3_closed",
    "resource_saving_claimed",
    "physical_layout_claimed",
    "transcript_timestamp_unix",
    "reviewer_signature_hash",
]

PRODUCTION_REQUIRED_FIELDS = [
    "transcript_id",
    "reviewer_agent_id",
    "reviewed_r93_packet_path",
    "reviewed_r93_packet_sha256",
    "reviewed_r93_packet_hash",
    "command_transcript_path",
    "command_transcript_sha256",
    "environment_manifest_path",
    "environment_manifest_sha256",
    "recomputed_target_rows_path",
    "recomputed_target_rows_sha256",
    "double_count_test_path",
    "double_count_test_sha256",
    "evidence_sufficiency_label",
    "counter_target",
    "proposed_credit_decision",
    "claim_boundary",
    "reviewer_signature_hash",
]


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def stable_self_hash(payload: dict[str, Any], hash_key: str) -> str:
    copy = dict(payload)
    copy.pop(hash_key, None)
    return stable_hash(copy)


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


def build_transcript_contract(
    root: Path,
    r94_result: dict[str, Any],
    r94_contract: dict[str, Any],
    r94_template: dict[str, Any],
    r94_preflight: dict[str, Any],
    r94_blocker_queue: dict[str, Any],
) -> dict[str, Any]:
    contract = {
        "artifact": "R95 G1 maintainer review transcript intake contract",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r94_result_path": R94_RESULT,
        "source_r94_result_sha256": file_hash(root / R94_RESULT),
        "source_r94_payload_hash": r94_result["payload_hash"],
        "source_r94_verdict_contract_path": R94_VERDICT_CONTRACT,
        "source_r94_verdict_contract_sha256": file_hash(root / R94_VERDICT_CONTRACT),
        "source_r94_verdict_contract_hash": r94_contract["verdict_contract_hash"],
        "source_r94_verdict_template_path": R94_VERDICT_TEMPLATE,
        "source_r94_verdict_template_sha256": file_hash(root / R94_VERDICT_TEMPLATE),
        "source_r94_verdict_template_hash": r94_template["verdict_template_hash"],
        "source_r94_preflight_path": R94_PREFLIGHT,
        "source_r94_preflight_sha256": file_hash(root / R94_PREFLIGHT),
        "source_r94_preflight_hash": r94_preflight["preflight_hash"],
        "source_r94_blocker_queue_path": R94_BLOCKER_QUEUE,
        "source_r94_blocker_queue_sha256": file_hash(root / R94_BLOCKER_QUEUE),
        "source_r94_blocker_queue_hash": r94_blocker_queue["blocker_queue_hash"],
        "contract_id": "R95-G1-maintainer-review-transcript-intake",
        "route_id": r94_contract["route_id"],
        "required_fields": TRANSCRIPT_REQUIRED_FIELDS,
        "required_field_count": len(TRANSCRIPT_REQUIRED_FIELDS),
        "production_required_fields": PRODUCTION_REQUIRED_FIELDS,
        "production_required_field_count": len(PRODUCTION_REQUIRED_FIELDS),
        "allowed_evidence_sufficiency": r94_contract["allowed_evidence_sufficiency"],
        "allowed_counter_targets": r94_contract["allowed_counter_targets"],
        "allowed_credit_decisions": r94_contract["allowed_credit_decisions"],
        "required_evidence_files": [
            "reviewed_r93_packet",
            "command_transcript",
            "environment_manifest",
            "recomputed_target_rows",
            "double_count_test",
            "review_notes",
        ],
        "transcript_acceptance_rules": [
            "reviewed packet hash must be present",
            "command transcript and environment manifest must be hash-bound",
            "recomputed target rows and double-count test must be hash-bound",
            "counter target and proposed credit decision must be allowed by R94",
            "R95 cannot directly increment new credit or close stronger B7 claims",
        ],
        "maintainer_review_transcript_accepted": False,
        "maintainer_verdict_accepted": False,
        "counter_delta": 0,
        "accepted_external_reproduction_count": 0,
        "accepted_external_falsification_count": 0,
        "new_credit_delta": 0,
        "o3_closed": False,
        "resource_saving_claimed": False,
        "physical_layout_claimed": False,
        "claim_boundary": (
            "R95 defines the source-backed review transcript that must exist before "
            "an R94 maintainer verdict can count. The empty transcript is rejected, "
            "no verdict is accepted, and no counter or B7 credit moves."
        ),
    }
    contract["transcript_contract_hash"] = stable_self_hash(
        contract, "transcript_contract_hash"
    )
    return contract


def build_transcript_template(contract: dict[str, Any]) -> dict[str, Any]:
    template = {
        "artifact": "R95 G1 maintainer review transcript template",
        "contract_id": contract["contract_id"],
        "transcript_contract_hash": contract["transcript_contract_hash"],
        "fields": {field: None for field in contract["required_fields"]},
        "allowed_evidence_sufficiency": contract["allowed_evidence_sufficiency"],
        "allowed_counter_targets": contract["allowed_counter_targets"],
        "allowed_credit_decisions": contract["allowed_credit_decisions"],
        "required_evidence_files": contract["required_evidence_files"],
        "instructions": [
            "Bind a filled non-fixture R93 packet and its packet hash.",
            "Attach command transcript, environment manifest, recomputed rows, double-count test, and review notes.",
            "Use an R94-allowed evidence sufficiency label, counter target, and credit decision.",
            "Do not claim O3, physical layout, resource savings, or new credit from R95 alone.",
        ],
    }
    template["transcript_template_hash"] = stable_self_hash(
        template, "transcript_template_hash"
    )
    return template


def build_empty_transcript(contract: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    fields = dict(template["fields"])
    fields.update(
        {
            "transcript_id": "R95-G1-empty-maintainer-review-transcript",
            "source_r94_verdict_contract_hash": contract["source_r94_verdict_contract_hash"],
            "source_r94_verdict_template_hash": contract["source_r94_verdict_template_hash"],
            "proposed_counter_delta": 0,
            "one_unit_credit_preserved": False,
            "one_unit_credit_revoked": False,
            "new_credit_delta": 0,
            "o3_closed": False,
            "resource_saving_claimed": False,
            "physical_layout_claimed": False,
            "claim_boundary": "empty_review_transcript_no_source_backed_review_evidence",
        }
    )
    transcript = {
        "artifact": "R95 current empty maintainer review transcript",
        "contract_id": contract["contract_id"],
        "transcript_contract_hash": contract["transcript_contract_hash"],
        "transcript_template_hash": template["transcript_template_hash"],
        "fields": fields,
    }
    transcript["transcript_hash"] = stable_self_hash(transcript, "transcript_hash")
    return transcript


def build_preflight(contract: dict[str, Any], transcript: dict[str, Any]) -> dict[str, Any]:
    fields = transcript["fields"]
    missing_required = [field for field in contract["required_fields"] if field not in fields]
    missing_production = [
        field for field in contract["production_required_fields"] if fields.get(field) in (None, "")
    ]
    gates = {
        "all_required_fields_present": not missing_required,
        "production_required_fields_present": not missing_production,
        "reviewer_identity_present": bool(fields.get("reviewer_agent_id")),
        "reviewed_r93_packet_bound": bool(fields.get("reviewed_r93_packet_path"))
        and bool(fields.get("reviewed_r93_packet_sha256"))
        and bool(fields.get("reviewed_r93_packet_hash")),
        "r94_contract_hash_bound": fields.get("source_r94_verdict_contract_hash")
        == contract["source_r94_verdict_contract_hash"],
        "r94_template_hash_bound": fields.get("source_r94_verdict_template_hash")
        == contract["source_r94_verdict_template_hash"],
        "command_transcript_bound": bool(fields.get("command_transcript_path"))
        and bool(fields.get("command_transcript_sha256")),
        "environment_manifest_bound": bool(fields.get("environment_manifest_path"))
        and bool(fields.get("environment_manifest_sha256")),
        "recomputed_rows_bound": bool(fields.get("recomputed_target_rows_path"))
        and bool(fields.get("recomputed_target_rows_sha256")),
        "double_count_test_bound": bool(fields.get("double_count_test_path"))
        and bool(fields.get("double_count_test_sha256")),
        "review_notes_bound": bool(fields.get("review_notes_path"))
        and bool(fields.get("review_notes_sha256")),
        "allowed_evidence_sufficiency": fields.get("evidence_sufficiency_label")
        in contract["allowed_evidence_sufficiency"],
        "allowed_counter_target": fields.get("counter_target")
        in contract["allowed_counter_targets"],
        "allowed_credit_decision": fields.get("proposed_credit_decision")
        in contract["allowed_credit_decisions"],
        "zero_direct_new_credit": fields.get("new_credit_delta") == 0,
        "counter_delta_zero_until_verdict": fields.get("proposed_counter_delta") == 0,
        "claim_boundary_safe": fields.get("o3_closed") is False
        and fields.get("resource_saving_claimed") is False
        and fields.get("physical_layout_claimed") is False,
        "signature_present": bool(fields.get("reviewer_signature_hash")),
        "maintainer_review_transcript_accepted": False,
    }
    failed = [gate for gate, passed in gates.items() if not passed]
    preflight = {
        "artifact": "R95 maintainer review transcript preflight verdict",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "transcript_contract_hash": contract["transcript_contract_hash"],
        "transcript_hash": transcript["transcript_hash"],
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "missing_required_fields": missing_required,
        "missing_production_fields": missing_production,
        "empty_transcript_rejected": True,
        "maintainer_review_transcript_accepted": False,
        "maintainer_verdict_accepted": False,
        "counter_delta": 0,
        "accepted_external_reproduction_count": 0,
        "accepted_external_falsification_count": 0,
        "new_credit_delta": 0,
        "claim_boundary": contract["claim_boundary"],
    }
    preflight["preflight_hash"] = stable_self_hash(preflight, "preflight_hash")
    return preflight


def build_blocker_queue(contract: dict[str, Any], preflight: dict[str, Any]) -> dict[str, Any]:
    queue = {
        "artifact": "R95 post maintainer review transcript blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "transcript_contract_hash": contract["transcript_contract_hash"],
        "preflight_hash": preflight["preflight_hash"],
        "queue": [
            {
                "blocker_id": "R95-G1-1",
                "priority": 1,
                "target_gate": "filled_r93_packet_hash_binding",
                "needed_artifact": "filled non-fixture R93 packet path, SHA-256, and packet hash",
            },
            {
                "blocker_id": "R95-G1-2",
                "priority": 2,
                "target_gate": "review_evidence_file_bundle",
                "needed_artifact": "command transcript, environment manifest, recomputed target rows, double-count test, and review notes",
            },
            {
                "blocker_id": "R95-G1-3",
                "priority": 3,
                "target_gate": "r94_allowed_verdict_fields",
                "needed_artifact": "R94-allowed evidence sufficiency label, counter target, credit decision, and zero direct new-credit increment",
            },
            {
                "blocker_id": "R95-G1-4",
                "priority": 4,
                "target_gate": "accepted_r94_maintainer_verdict",
                "needed_artifact": "source-backed maintainer verdict that references the accepted R95 transcript",
            },
        ],
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    return queue


def write_stdout(root: Path, contract: dict[str, Any], preflight: dict[str, Any], queue: dict[str, Any]) -> str:
    text = "\n".join(
        [
            "R95 maintainer review transcript intake stdout",
            f"method={METHOD}",
            f"source_target_id={TARGET_ID}",
            f"upstream_target_id={UPSTREAM_TARGET_ID}",
            f"transcript_contract_hash={contract['transcript_contract_hash']}",
            f"preflight_hash={preflight['preflight_hash']}",
            f"blocker_queue_hash={queue['blocker_queue_hash']}",
            f"required_field_count={contract['required_field_count']}",
            f"production_required_field_count={contract['production_required_field_count']}",
            f"failed_gate_count={preflight['failed_gate_count']}",
            "maintainer_review_transcript_accepted=false",
            "maintainer_verdict_accepted=false",
            "accepted_external_reproduction_count=0",
            "accepted_external_falsification_count=0",
            "new_credit_delta=0",
        ]
    ) + "\n"
    path = root / R95_STDOUT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    r94_result = load_json(root / R94_RESULT)
    r94_contract = load_json(root / R94_VERDICT_CONTRACT)
    r94_template = load_json(root / R94_VERDICT_TEMPLATE)
    r94_preflight = load_json(root / R94_PREFLIGHT)
    r94_blocker_queue = load_json(root / R94_BLOCKER_QUEUE)

    contract = build_transcript_contract(
        root, r94_result, r94_contract, r94_template, r94_preflight, r94_blocker_queue
    )
    write_json(root / R95_TRANSCRIPT_CONTRACT, contract)
    template = build_transcript_template(contract)
    write_json(root / R95_TRANSCRIPT_TEMPLATE, template)
    empty_transcript = build_empty_transcript(contract, template)
    write_json(root / R95_EMPTY_TRANSCRIPT, empty_transcript)
    preflight = build_preflight(contract, empty_transcript)
    write_json(root / R95_PREFLIGHT, preflight)
    blocker_queue = build_blocker_queue(contract, preflight)
    write_json(root / R95_BLOCKER_QUEUE, blocker_queue)
    stdout_sha256 = write_stdout(root, contract, preflight, blocker_queue)

    requirements = [
        req(
            "A1",
            "R95 binds the R94 result, verdict contract, verdict template, preflight, and blocker queue",
            r94_result["summary"]["source_target_id"] == UPSTREAM_TARGET_ID
            and r94_result["verdict_contract_hash"] == r94_contract["verdict_contract_hash"]
            and r94_result["verdict_template_hash"] == r94_template["verdict_template_hash"]
            and r94_result["preflight_hash"] == r94_preflight["preflight_hash"],
            {
                "r94_payload_hash": r94_result["payload_hash"],
                "r94_verdict_contract_hash": r94_contract["verdict_contract_hash"],
                "r94_preflight_hash": r94_preflight["preflight_hash"],
                "r94_blocker_queue_hash": r94_blocker_queue["blocker_queue_hash"],
            },
        ),
        req(
            "A2",
            "R95 emits a review transcript intake contract with explicit evidence-file classes",
            contract["required_field_count"] == 30
            and contract["production_required_field_count"] == 18
            and len(contract["required_evidence_files"]) == 6,
            {
                "transcript_contract_hash": contract["transcript_contract_hash"],
                "required_field_count": contract["required_field_count"],
                "production_required_field_count": contract["production_required_field_count"],
                "required_evidence_files": contract["required_evidence_files"],
            },
        ),
        req(
            "A3",
            "R95 emits a fillable review transcript template",
            template["transcript_contract_hash"] == contract["transcript_contract_hash"]
            and all(field in template["fields"] for field in TRANSCRIPT_REQUIRED_FIELDS),
            {
                "transcript_template_hash": template["transcript_template_hash"],
                "template_field_count": len(template["fields"]),
            },
        ),
        req(
            "A4",
            "R95 rejects the empty review transcript before source-backed review evidence exists",
            preflight["empty_transcript_rejected"] is True
            and preflight["maintainer_review_transcript_accepted"] is False
            and preflight["failed_gate_count"] == 13,
            {
                "preflight_hash": preflight["preflight_hash"],
                "failed_gates": preflight["failed_gates"],
                "missing_production_field_count": len(preflight["missing_production_fields"]),
            },
        ),
        req(
            "A5",
            "R95 keeps maintainer verdict, external counters, and new credit at zero",
            preflight["maintainer_verdict_accepted"] is False
            and preflight["accepted_external_reproduction_count"] == 0
            and preflight["accepted_external_falsification_count"] == 0
            and preflight["counter_delta"] == 0
            and preflight["new_credit_delta"] == 0,
            {
                "maintainer_verdict_accepted": preflight["maintainer_verdict_accepted"],
                "counter_delta": preflight["counter_delta"],
                "accepted_external_reproduction_count": preflight[
                    "accepted_external_reproduction_count"
                ],
                "accepted_external_falsification_count": preflight[
                    "accepted_external_falsification_count"
                ],
                "new_credit_delta": preflight["new_credit_delta"],
            },
        ),
        req(
            "A6",
            "R95 keeps O3, resource-saving, and physical-layout claims closed",
            contract["o3_closed"] is False
            and contract["resource_saving_claimed"] is False
            and contract["physical_layout_claimed"] is False,
            {
                "o3_closed": contract["o3_closed"],
                "resource_saving_claimed": contract["resource_saving_claimed"],
                "physical_layout_claimed": contract["physical_layout_claimed"],
            },
        ),
        req(
            "A7",
            "R95 emits blockers for R93 packet binding, review evidence bundle, R94 fields, and accepted verdict",
            [item["target_gate"] for item in blocker_queue["queue"]]
            == [
                "filled_r93_packet_hash_binding",
                "review_evidence_file_bundle",
                "r94_allowed_verdict_fields",
                "accepted_r94_maintainer_verdict",
            ],
            {
                "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
                "blocker_ids": [item["blocker_id"] for item in blocker_queue["queue"]],
            },
        ),
    ]

    failed_requirements = [
        requirement["requirement_id"] for requirement in requirements if not requirement["passed"]
    ]
    validation_errors = []
    if failed_requirements:
        validation_errors.append("one or more R95 requirements failed")
    if preflight["maintainer_review_transcript_accepted"]:
        validation_errors.append("R95 must not accept the empty review transcript")
    if preflight["new_credit_delta"] != 0:
        validation_errors.append("R95 must not grant new credit")

    payload = {
        "artifact": "B1/B7 cone01 R95 maintainer review transcript intake gate",
        "method": METHOD,
        "version": VERSION,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "generated_at_unix": int(time.time()),
        "transcript_contract_path": R95_TRANSCRIPT_CONTRACT,
        "transcript_contract_hash": contract["transcript_contract_hash"],
        "transcript_template_path": R95_TRANSCRIPT_TEMPLATE,
        "transcript_template_hash": template["transcript_template_hash"],
        "empty_transcript_path": R95_EMPTY_TRANSCRIPT,
        "empty_transcript_hash": empty_transcript["transcript_hash"],
        "preflight_path": R95_PREFLIGHT,
        "preflight_hash": preflight["preflight_hash"],
        "stdout_path": R95_STDOUT,
        "stdout_sha256": stdout_sha256,
        "blocker_queue_path": R95_BLOCKER_QUEUE,
        "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
        "requirement_count": len(requirements),
        "requirements_passed": sum(1 for requirement in requirements if requirement["passed"]),
        "requirements_failed": len(failed_requirements),
        "failed_requirement_ids": failed_requirements,
        "requirements": requirements,
        "validation_error_count": len(validation_errors),
        "validation_errors": validation_errors,
        "summary": {
            "method": METHOD,
            "status": STATUS,
            "model_status": MODEL_STATUS,
            "source_target_id": TARGET_ID,
            "upstream_target_id": UPSTREAM_TARGET_ID,
            "route_id": contract["route_id"],
            "contract_id": contract["contract_id"],
            "required_field_count": contract["required_field_count"],
            "production_required_field_count": contract["production_required_field_count"],
            "required_evidence_file_count": len(contract["required_evidence_files"]),
            "empty_transcript_rejected": preflight["empty_transcript_rejected"],
            "maintainer_review_transcript_accepted": preflight[
                "maintainer_review_transcript_accepted"
            ],
            "maintainer_verdict_accepted": preflight["maintainer_verdict_accepted"],
            "preflight_failed_gate_count": preflight["failed_gate_count"],
            "missing_production_field_count": len(preflight["missing_production_fields"]),
            "counter_delta": preflight["counter_delta"],
            "accepted_external_reproduction_count": preflight[
                "accepted_external_reproduction_count"
            ],
            "accepted_external_falsification_count": preflight[
                "accepted_external_falsification_count"
            ],
            "new_credit_delta": preflight["new_credit_delta"],
            "o3_closed": contract["o3_closed"],
            "resource_saving_claimed": contract["resource_saving_claimed"],
            "physical_layout_claimed": contract["physical_layout_claimed"],
            "transcript_contract_hash": contract["transcript_contract_hash"],
            "transcript_template_hash": template["transcript_template_hash"],
            "empty_transcript_hash": empty_transcript["transcript_hash"],
            "preflight_hash": preflight["preflight_hash"],
            "stdout_sha256": stdout_sha256,
            "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
            "payload_hash": None,
            "requirements_passed": sum(1 for requirement in requirements if requirement["passed"]),
            "requirements_failed": len(failed_requirements),
            "failed_requirement_ids": failed_requirements,
            "validation_error_count": len(validation_errors),
        },
    }
    payload["payload_hash"] = stable_self_hash(payload, "payload_hash")
    payload["summary"]["payload_hash"] = payload["payload_hash"]
    return payload


def write_report(root: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone01 R95 Maintainer Review Transcript Intake Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R95 turns the R94 verdict blocker into a source-backed maintainer review",
        "transcript intake contract. The template requires a filled R93 packet hash,",
        "command transcript, environment manifest, recomputed target rows, double-count",
        "test, review notes, evidence-sufficiency label, counter target, proposed credit",
        "decision, and claim boundary before any R94 verdict can count.",
        "",
        "The current empty review transcript is rejected. No maintainer verdict is",
        "accepted, no external reproduction or falsification counter is incremented,",
        "and no new B7 credit is granted.",
        "",
        "## Key Counters",
        "",
        f"- Required fields: `{summary['required_field_count']}`",
        f"- Production-required fields: `{summary['production_required_field_count']}`",
        f"- Required evidence-file classes: `{summary['required_evidence_file_count']}`",
        f"- Empty transcript rejected: `{summary['empty_transcript_rejected']}`",
        f"- Review transcript accepted: `{summary['maintainer_review_transcript_accepted']}`",
        f"- Maintainer verdict accepted: `{summary['maintainer_verdict_accepted']}`",
        f"- Preflight failed gates: `{summary['preflight_failed_gate_count']}`",
        f"- Missing production fields: `{summary['missing_production_field_count']}`",
        f"- Counter delta: `{summary['counter_delta']}`",
        f"- Accepted external reproductions: `{summary['accepted_external_reproduction_count']}`",
        f"- Accepted external falsifications: `{summary['accepted_external_falsification_count']}`",
        f"- New credit delta: `{summary['new_credit_delta']}`",
        "",
        "## Requirements",
        "",
    ]
    for requirement in payload["requirements"]:
        status = "PASS" if requirement["passed"] else "FAIL"
        lines.append(f"- `{requirement['requirement_id']}` {status}: {requirement['label']}")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Result JSON: `{RESULT_PATH}`",
            f"- Transcript contract: `{R95_TRANSCRIPT_CONTRACT}`",
            f"- Transcript template: `{R95_TRANSCRIPT_TEMPLATE}`",
            f"- Empty transcript: `{R95_EMPTY_TRANSCRIPT}`",
            f"- Preflight verdict: `{R95_PREFLIGHT}`",
            f"- Stdout: `{R95_STDOUT}`",
            f"- Blocker queue: `{R95_BLOCKER_QUEUE}`",
            "",
            "## Claim Boundary",
            "",
            "R95 is a review-transcript intake gate. It does not accept a transcript",
            "yet, does not accept a maintainer verdict, does not increment reproduction",
            "or falsification counters, does not grant new B7 credit, and does not close",
            "1.25x, O3, physical layout, resource-saving, paper, patent, funding, or",
            "product-readiness claims.",
            "",
        ]
    )
    (root / REPORT_PATH).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    payload = build_payload(args)
    write_json(root / RESULT_PATH, payload)
    write_report(root, payload)
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
