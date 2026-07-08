#!/usr/bin/env python3
"""T-B1-004gq/T-B7-015z: R93 non-fixture external intake for R91/R92."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r93_nonfixture_external_intake_gate_v0"
STATUS = "cone01_r93_nonfixture_external_intake_open_no_submission_yet"
MODEL_STATUS = "r92_validator_ready_but_nonfixture_external_submission_missing"
VERSION = "0.1"
TARGET_ID = "T-B1-004gq/T-B7-015z"
UPSTREAM_TARGET_ID = "T-B1-004gp/T-B7-015y"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"

R92_RESULT = "results/B1_B7_cone01_R92_external_submission_validator_gate_v0.json"
R92_VALIDATOR_RULES = f"{SUBMISSION_DIR}/R92-G1-external-submission-validator-rules.json"
R92_FIXTURE_SUBMISSION = f"{SUBMISSION_DIR}/R92-G1-local-validator-filled-submission.json"
R92_FIXTURE_PREFLIGHT = f"{SUBMISSION_DIR}/R92-G1-local-validator-preflight.verdict.json"
R92_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R92-G1-post-validator-blocker-queue.json"

R93_INTAKE_CONTRACT = f"{SUBMISSION_DIR}/R93-G1-nonfixture-external-intake-contract.json"
R93_PACKET_TEMPLATE = f"{SUBMISSION_DIR}/R93-G1-nonfixture-external-submission-packet.template.json"
R93_EMPTY_PACKET = f"{SUBMISSION_DIR}/R93-G1-nonfixture-external-empty-packet.json"
R93_PREFLIGHT = f"{SUBMISSION_DIR}/R93-G1-nonfixture-external-intake-preflight.verdict.json"
R93_STDOUT = f"{SUBMISSION_DIR}/R93-G1-nonfixture-external-intake.stdout.txt"
R93_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R93-G1-post-nonfixture-intake-blocker-queue.json"


EXTRA_NONFIXTURE_FIELDS = [
    "external_submitter_attested",
    "submitter_independence_statement",
    "fixture_agent_id_used",
    "maintainer_review_required",
    "review_counter_target",
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


def build_intake_contract(
    root: Path,
    r92_result: dict[str, Any],
    validator_rules: dict[str, Any],
    fixture_submission: dict[str, Any],
    fixture_preflight: dict[str, Any],
    blocker_queue: dict[str, Any],
) -> dict[str, Any]:
    banned_agent_id = fixture_submission["fields"]["agent_id"]
    contract = {
        "artifact": "R93 G1 non-fixture external intake contract",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r92_result_path": R92_RESULT,
        "source_r92_result_sha256": file_hash(root / R92_RESULT),
        "source_r92_payload_hash": r92_result["payload_hash"],
        "source_r92_validator_rules_path": R92_VALIDATOR_RULES,
        "source_r92_validator_rules_sha256": file_hash(root / R92_VALIDATOR_RULES),
        "source_r92_validator_rules_hash": validator_rules["validator_rules_hash"],
        "source_r92_fixture_submission_path": R92_FIXTURE_SUBMISSION,
        "source_r92_fixture_submission_sha256": file_hash(root / R92_FIXTURE_SUBMISSION),
        "source_r92_fixture_submission_hash": fixture_submission["submission_hash"],
        "source_r92_fixture_preflight_path": R92_FIXTURE_PREFLIGHT,
        "source_r92_fixture_preflight_sha256": file_hash(root / R92_FIXTURE_PREFLIGHT),
        "source_r92_fixture_preflight_hash": fixture_preflight["preflight_hash"],
        "source_r92_blocker_queue_path": R92_BLOCKER_QUEUE,
        "source_r92_blocker_queue_sha256": file_hash(root / R92_BLOCKER_QUEUE),
        "source_r92_blocker_queue_hash": blocker_queue["blocker_queue_hash"],
        "contract_id": "R93-G1-nonfixture-external-intake",
        "route_id": validator_rules["route_id"],
        "base_required_fields": validator_rules["required_fields"],
        "extra_nonfixture_fields": EXTRA_NONFIXTURE_FIELDS,
        "required_field_count": len(validator_rules["required_fields"])
        + len(EXTRA_NONFIXTURE_FIELDS),
        "production_required_fields": validator_rules["production_required_fields"]
        + EXTRA_NONFIXTURE_FIELDS,
        "production_required_field_count": len(validator_rules["production_required_fields"])
        + len(EXTRA_NONFIXTURE_FIELDS),
        "validator_gate_count": len(validator_rules["validator_gates"]),
        "nonfixture_gate_names": [
            "agent_is_not_fixture",
            "external_submitter_attested",
            "independence_statement_present",
            "validator_hash_bound",
            "maintainer_review_required",
            "review_counter_target_present",
        ],
        "banned_fixture_agent_ids": [banned_agent_id],
        "accepted_review_modes": validator_rules["accepted_review_modes"],
        "accepted_credit_decisions": validator_rules["accepted_credit_decisions"],
        "allowed_review_counter_targets": [
            "accepted_external_reproduction_count",
            "accepted_external_falsification_count",
            "new_credit_candidate_pending_review",
        ],
        "external_submission_accepted": False,
        "accepted_external_reproduction_count": 0,
        "accepted_external_falsification_count": 0,
        "new_credit_delta": 0,
        "o3_closed": False,
        "resource_saving_claimed": False,
        "physical_layout_claimed": False,
        "claim_boundary": (
            "R93 defines the non-fixture external intake path after R92. It bans "
            "the R92 local fixture agent id, requires external attestation and "
            "maintainer review, accepts no external packet yet, and grants no "
            "new B7 credit."
        ),
    }
    contract["intake_contract_hash"] = stable_self_hash(contract, "intake_contract_hash")
    return contract


def build_packet_template(contract: dict[str, Any]) -> dict[str, Any]:
    fields = {field: None for field in contract["base_required_fields"]}
    fields.update({field: None for field in EXTRA_NONFIXTURE_FIELDS})
    template = {
        "artifact": "R93 G1 non-fixture external submission packet template",
        "contract_id": contract["contract_id"],
        "intake_contract_hash": contract["intake_contract_hash"],
        "fields": fields,
        "banned_fixture_agent_ids": contract["banned_fixture_agent_ids"],
        "allowed_review_counter_targets": contract["allowed_review_counter_targets"],
        "instructions": [
            "Use a non-fixture agent id.",
            "Attach independently generated environment and command transcript artifacts.",
            "Run the R92 validator rules before asking for maintainer review.",
            "Do not claim O3, physical layout, or resource savings without separate evidence.",
        ],
    }
    template["packet_template_hash"] = stable_self_hash(template, "packet_template_hash")
    return template


def build_empty_packet(contract: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    fields = dict(template["fields"])
    fields.update(
        {
            "submission_id": "R93-G1-empty-nonfixture-packet",
            "agent_id": None,
            "review_mode": None,
            "external_submitter_attested": False,
            "submitter_independence_statement": None,
            "fixture_agent_id_used": None,
            "maintainer_review_required": True,
            "review_counter_target": None,
            "new_credit_delta": 0,
            "falsification_claimed": False,
            "reproduction_claimed": False,
            "o3_closed": False,
            "resource_saving_claimed": False,
            "physical_layout_claimed": False,
            "claim_boundary": "empty_nonfixture_packet_no_external_evidence",
        }
    )
    packet = {
        "artifact": "R93 current empty non-fixture external packet",
        "contract_id": contract["contract_id"],
        "intake_contract_hash": contract["intake_contract_hash"],
        "packet_template_hash": template["packet_template_hash"],
        "fields": fields,
    }
    packet["packet_hash"] = stable_self_hash(packet, "packet_hash")
    return packet


def build_preflight(contract: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    fields = packet["fields"]
    required = contract["base_required_fields"] + EXTRA_NONFIXTURE_FIELDS
    production_required = contract["production_required_fields"]
    missing_required = [field for field in required if field not in fields]
    missing_production = [
        field for field in production_required if fields.get(field) in (None, "")
    ]
    gates = {
        "all_required_fields_present": not missing_required,
        "production_required_fields_present": not missing_production,
        "agent_is_not_fixture": fields.get("agent_id") not in contract["banned_fixture_agent_ids"]
        and bool(fields.get("agent_id")),
        "external_submitter_attested": fields.get("external_submitter_attested") is True,
        "independence_statement_present": bool(
            fields.get("submitter_independence_statement")
        ),
        "validator_hash_bound": fields.get("source_r90_review_ledger_hash") is not None
        and fields.get("source_r90_verdict_hash") is not None,
        "maintainer_review_required": fields.get("maintainer_review_required") is True,
        "review_counter_target_present": fields.get("review_counter_target")
        in contract["allowed_review_counter_targets"],
        "claim_boundary_safe": fields.get("o3_closed") is False
        and fields.get("resource_saving_claimed") is False
        and fields.get("physical_layout_claimed") is False,
        "external_submission_accepted": False,
    }
    failed = [gate for gate, passed in gates.items() if not passed]
    preflight = {
        "artifact": "R93 non-fixture external intake preflight verdict",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "intake_contract_hash": contract["intake_contract_hash"],
        "packet_hash": packet["packet_hash"],
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "missing_required_fields": missing_required,
        "missing_production_fields": missing_production,
        "empty_packet_rejected": True,
        "external_submission_accepted": False,
        "accepted_external_reproduction_count": 0,
        "accepted_external_falsification_count": 0,
        "new_credit_delta": 0,
        "claim_boundary": contract["claim_boundary"],
    }
    preflight["preflight_hash"] = stable_self_hash(preflight, "preflight_hash")
    return preflight


def build_blocker_queue(contract: dict[str, Any], preflight: dict[str, Any]) -> dict[str, Any]:
    queue = {
        "artifact": "R93 post non-fixture intake blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "intake_contract_hash": contract["intake_contract_hash"],
        "preflight_hash": preflight["preflight_hash"],
        "queue": [
            {
                "blocker_id": "R93-G1-1",
                "priority": 1,
                "target_gate": "nonfixture_agent_packet",
                "needed_artifact": "filled R93 packet with a non-fixture agent id and external attestation",
                "missing_fields": preflight["missing_production_fields"],
            },
            {
                "blocker_id": "R93-G1-2",
                "priority": 2,
                "target_gate": "maintainer_review_verdict",
                "needed_artifact": "maintainer verdict deciding whether to increment reproduction or falsification counters",
            },
            {
                "blocker_id": "R93-G1-3",
                "priority": 3,
                "target_gate": "credit_counter_update",
                "needed_artifact": "post-review counter update that preserves, revokes, or marks insufficient evidence",
            },
        ],
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    return queue


def write_stdout(root: Path, contract: dict[str, Any], preflight: dict[str, Any], queue: dict[str, Any]) -> str:
    text = "\n".join(
        [
            "R93 non-fixture external intake stdout",
            f"method={METHOD}",
            f"source_target_id={TARGET_ID}",
            f"upstream_target_id={UPSTREAM_TARGET_ID}",
            f"intake_contract_hash={contract['intake_contract_hash']}",
            f"preflight_hash={preflight['preflight_hash']}",
            f"blocker_queue_hash={queue['blocker_queue_hash']}",
            f"required_field_count={contract['required_field_count']}",
            f"production_required_field_count={contract['production_required_field_count']}",
            f"failed_gate_count={preflight['failed_gate_count']}",
            "external_submission_accepted=false",
            "accepted_external_reproduction_count=0",
            "accepted_external_falsification_count=0",
            "new_credit_delta=0",
        ]
    ) + "\n"
    path = root / R93_STDOUT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    r92_result = load_json(root / R92_RESULT)
    validator_rules = load_json(root / R92_VALIDATOR_RULES)
    fixture_submission = load_json(root / R92_FIXTURE_SUBMISSION)
    fixture_preflight = load_json(root / R92_FIXTURE_PREFLIGHT)
    r92_blocker_queue = load_json(root / R92_BLOCKER_QUEUE)

    contract = build_intake_contract(
        root, r92_result, validator_rules, fixture_submission, fixture_preflight, r92_blocker_queue
    )
    write_json(root / R93_INTAKE_CONTRACT, contract)
    template = build_packet_template(contract)
    write_json(root / R93_PACKET_TEMPLATE, template)
    empty_packet = build_empty_packet(contract, template)
    write_json(root / R93_EMPTY_PACKET, empty_packet)
    preflight = build_preflight(contract, empty_packet)
    write_json(root / R93_PREFLIGHT, preflight)
    blocker_queue = build_blocker_queue(contract, preflight)
    write_json(root / R93_BLOCKER_QUEUE, blocker_queue)
    stdout_sha256 = write_stdout(root, contract, preflight, blocker_queue)

    requirements = [
        req(
            "A1",
            "R93 binds the R92 result, validator rules, fixture submission, preflight, and blocker queue",
            r92_result["summary"]["source_target_id"] == UPSTREAM_TARGET_ID
            and r92_result["validator_rules_hash"] == validator_rules["validator_rules_hash"]
            and r92_result["fixture_submission_hash"] == fixture_submission["submission_hash"]
            and r92_result["fixture_preflight_hash"] == fixture_preflight["preflight_hash"],
            {
                "r92_payload_hash": r92_result["payload_hash"],
                "validator_rules_hash": validator_rules["validator_rules_hash"],
                "fixture_preflight_hash": fixture_preflight["preflight_hash"],
            },
        ),
        req(
            "A2",
            "R93 emits a non-fixture intake contract that bans the R92 fixture agent",
            fixture_submission["fields"]["agent_id"] in contract["banned_fixture_agent_ids"]
            and contract["required_field_count"] == 33
            and contract["production_required_field_count"] == 19,
            {
                "intake_contract_hash": contract["intake_contract_hash"],
                "banned_fixture_agent_ids": contract["banned_fixture_agent_ids"],
                "required_field_count": contract["required_field_count"],
            },
        ),
        req(
            "A3",
            "R93 emits a fillable packet template with non-fixture fields",
            template["intake_contract_hash"] == contract["intake_contract_hash"]
            and all(field in template["fields"] for field in EXTRA_NONFIXTURE_FIELDS),
            {
                "packet_template_hash": template["packet_template_hash"],
                "extra_nonfixture_fields": EXTRA_NONFIXTURE_FIELDS,
            },
        ),
        req(
            "A4",
            "R93 rejects the empty non-fixture packet before external evidence exists",
            preflight["empty_packet_rejected"] is True
            and preflight["external_submission_accepted"] is False
            and preflight["failed_gate_count"] == 7,
            {
                "preflight_hash": preflight["preflight_hash"],
                "failed_gates": preflight["failed_gates"],
                "missing_production_field_count": len(preflight["missing_production_fields"]),
            },
        ),
        req(
            "A5",
            "R93 keeps external counters and new credit at zero",
            preflight["accepted_external_reproduction_count"] == 0
            and preflight["accepted_external_falsification_count"] == 0
            and preflight["new_credit_delta"] == 0,
            {
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
            "R93 keeps O3, resource-saving, and physical-layout claims closed",
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
            "R93 emits blockers for non-fixture packet, maintainer verdict, and counter update",
            len(blocker_queue["queue"]) == 3
            and [item["target_gate"] for item in blocker_queue["queue"]]
            == [
                "nonfixture_agent_packet",
                "maintainer_review_verdict",
                "credit_counter_update",
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
        validation_errors.append("one or more R93 requirements failed")
    if preflight["external_submission_accepted"]:
        validation_errors.append("R93 must not accept the empty packet")
    if preflight["new_credit_delta"] != 0:
        validation_errors.append("R93 must not grant new credit")

    payload = {
        "artifact": "B1/B7 cone01 R93 non-fixture external intake gate",
        "method": METHOD,
        "version": VERSION,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "generated_at_unix": int(time.time()),
        "intake_contract_path": R93_INTAKE_CONTRACT,
        "intake_contract_hash": contract["intake_contract_hash"],
        "packet_template_path": R93_PACKET_TEMPLATE,
        "packet_template_hash": template["packet_template_hash"],
        "empty_packet_path": R93_EMPTY_PACKET,
        "empty_packet_hash": empty_packet["packet_hash"],
        "preflight_path": R93_PREFLIGHT,
        "preflight_hash": preflight["preflight_hash"],
        "stdout_path": R93_STDOUT,
        "stdout_sha256": stdout_sha256,
        "blocker_queue_path": R93_BLOCKER_QUEUE,
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
            "production_required_field_count": contract[
                "production_required_field_count"
            ],
            "banned_fixture_agent_ids": contract["banned_fixture_agent_ids"],
            "nonfixture_gate_count": len(contract["nonfixture_gate_names"]),
            "empty_packet_rejected": preflight["empty_packet_rejected"],
            "preflight_failed_gate_count": preflight["failed_gate_count"],
            "missing_production_field_count": len(preflight["missing_production_fields"]),
            "external_submission_accepted": preflight["external_submission_accepted"],
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
            "intake_contract_hash": contract["intake_contract_hash"],
            "packet_template_hash": template["packet_template_hash"],
            "empty_packet_hash": empty_packet["packet_hash"],
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
        "# B1/B7 Cone01 R93 Non-Fixture External Intake Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R93 converts the R92 validator into a non-fixture external intake path. It",
        "emits an intake contract, a packet template, an empty packet, a preflight",
        "verdict, and a blocker queue. The contract explicitly bans the R92 local",
        "fixture agent id and requires external submitter attestation plus maintainer",
        "review before any reproduction or falsification counter can move.",
        "",
        "The current empty packet is rejected. No external submission is accepted, no",
        "external reproduction or falsification counter is incremented, and no new",
        "B7 credit is granted.",
        "",
        "## Key Counters",
        "",
        f"- Required fields: `{summary['required_field_count']}`",
        f"- Production-required fields: `{summary['production_required_field_count']}`",
        f"- Banned fixture agent ids: `{', '.join(summary['banned_fixture_agent_ids'])}`",
        f"- Empty packet rejected: `{summary['empty_packet_rejected']}`",
        f"- Preflight failed gates: `{summary['preflight_failed_gate_count']}`",
        f"- Missing production fields: `{summary['missing_production_field_count']}`",
        f"- External submission accepted: `{summary['external_submission_accepted']}`",
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
            "- Result JSON: `results/B1_B7_cone01_R93_nonfixture_external_intake_gate_v0.json`",
            f"- Intake contract: `{R93_INTAKE_CONTRACT}`",
            f"- Packet template: `{R93_PACKET_TEMPLATE}`",
            f"- Empty packet: `{R93_EMPTY_PACKET}`",
            f"- Preflight verdict: `{R93_PREFLIGHT}`",
            f"- Stdout: `{R93_STDOUT}`",
            f"- Blocker queue: `{R93_BLOCKER_QUEUE}`",
            "",
            "## Claim Boundary",
            "",
            "R93 is an intake and review-control gate. It does not accept an external",
            "submission yet, does not increment reproduction or falsification counters,",
            "does not grant new B7 credit, and does not close 1.25x, O3, physical",
            "layout, resource-saving, or product-readiness claims.",
            "",
        ]
    )
    report_path = root / "research/B1_B7_cone01_R93_nonfixture_external_intake_gate.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    payload = build_payload(args)
    result_path = root / "results/B1_B7_cone01_R93_nonfixture_external_intake_gate_v0.json"
    write_json(result_path, payload)
    write_report(root, payload)
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
