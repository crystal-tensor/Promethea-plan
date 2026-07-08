#!/usr/bin/env python3
"""T-B1-004hc/T-B7-016l: R105 external-origin attestation verifier gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r105_external_origin_attestation_verifier_gate_v0"
STATUS = "cone01_r105_origin_attestation_verifier_ready_no_counter_move"
MODEL_STATUS = "r104_contract_ready_but_no_verified_external_origin_packet"
VERSION = "0.1"
TARGET_ID = "T-B1-004hc/T-B7-016l"
UPSTREAM_TARGET_ID = "T-B1-004hb/T-B7-016k"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"

R104_RESULT = "results/B1_B7_cone01_R104_external_origin_attestation_contract_gate_v0.json"
R104_CONTRACT = f"{SUBMISSION_DIR}/R104-G1-external-origin-attestation-contract.json"
R104_TEMPLATE = f"{SUBMISSION_DIR}/R104-G1-external-origin-attestation.template.json"
R104_PLACEHOLDER = f"{SUBMISSION_DIR}/R104-G1-local-placeholder-origin-attestation.json"
R104_PREFLIGHT = f"{SUBMISSION_DIR}/R104-G1-external-origin-attestation-preflight.verdict.json"
R104_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R104-G1-post-origin-attestation-contract-blocker-queue.json"

R105_RULES = f"{SUBMISSION_DIR}/R105-G1-external-origin-attestation-verifier-rules.json"
R105_TEMPLATE_VALIDATION = f"{SUBMISSION_DIR}/R105-G1-empty-template-validation.verdict.json"
R105_PLACEHOLDER_VALIDATION = f"{SUBMISSION_DIR}/R105-G1-local-placeholder-validation.verdict.json"
R105_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R105-G1-post-origin-verifier-blocker-queue.json"
R105_STDOUT = f"{SUBMISSION_DIR}/R105-G1-external-origin-attestation-verifier.stdout.txt"

RESULT_PATH = "results/B1_B7_cone01_R105_external_origin_attestation_verifier_gate_v0.json"
REPORT_PATH = "research/B1_B7_cone01_R105_external_origin_attestation_verifier_gate.md"


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


def contains_forbidden_marker(value: str, markers: list[str]) -> bool:
    return any(marker in value for marker in markers)


def build_verifier_rules(contract: dict[str, Any], r104_result: dict[str, Any]) -> dict[str, Any]:
    rules = {
        "artifact": "R105 external-origin attestation verifier rules",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r104_payload_hash": r104_result["payload_hash"],
        "origin_contract_hash": contract["origin_contract_hash"],
        "required_fields": contract["required_fields"],
        "required_field_count": contract["required_field_count"],
        "forbidden_local_origin_markers": contract["forbidden_local_origin_markers"],
        "accepted_counter_transition_modes": contract["accepted_counter_transition_modes"],
        "gate_order": [
            "contract_hash_matches",
            "required_keys_present",
            "production_fields_nonempty",
            "signed_external_origin_statement",
            "source_url_https_remote",
            "commit_sha_pinned",
            "clone_command_network_remote",
            "transcript_file_hash_matches",
            "transcript_content_nonlocal",
            "environment_manifest_file_hash_matches",
            "environment_manifest_nonlocal",
            "replay_bundle_file_hash_matches",
            "replay_bundle_nonlocal",
            "counter_transition_mode_allowed",
            "claim_boundary_present",
            "origin_attestation_accepted",
        ],
        "acceptance_rule": (
            "All gates except origin_attestation_accepted must pass before the final "
            "origin_attestation_accepted gate may become true."
        ),
        "counter_policy": (
            "R105 validates origin evidence only. It never moves reproduction, "
            "falsification, B7, O3, resource, or layout counters."
        ),
    }
    rules["verifier_rules_hash"] = stable_self_hash(rules, "verifier_rules_hash")
    return rules


def extract_fields(packet: dict[str, Any]) -> dict[str, Any]:
    return packet.get("fields", {})


def validate_packet(
    root: Path,
    packet: dict[str, Any],
    contract: dict[str, Any],
    rules: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    fields = extract_fields(packet)
    required = rules["required_fields"]
    missing_keys = [field for field in required if field not in fields]
    empty_fields = [field for field in required if fields.get(field) in (None, "")]
    markers = rules["forbidden_local_origin_markers"]

    transcript_path = root / fields.get("clone_network_transcript_path", "")
    env_path = root / fields.get("environment_manifest_path", "")
    replay_path = root / fields.get("replay_artifact_bundle_path", "")
    transcript_text = transcript_path.read_text(encoding="utf-8") if transcript_path.is_file() else ""
    env_manifest = load_json(env_path) if env_path.is_file() else {}

    transcript_hash_matches = (
        transcript_path.is_file()
        and fields.get("clone_network_transcript_sha256") == file_hash(transcript_path)
    )
    env_hash_matches = (
        env_path.is_file()
        and fields.get("environment_manifest_sha256") == file_hash(env_path)
    )
    replay_hash_matches = (
        replay_path.is_file()
        and fields.get("replay_artifact_bundle_sha256") == file_hash(replay_path)
    )
    signed_origin = (
        "external_origin_attested" in fields.get("external_origin_attestation_statement", "")
        and "not_external_origin" not in fields.get("external_origin_attestation_statement", "")
        and fields.get("signature_hash", "") != ""
    )
    source_url = fields.get("repository_source_url", "")
    clone_command = fields.get("clone_command", "")
    source_remote = (
        source_url.startswith("https://")
        and "github.com/" in source_url
        and not contains_forbidden_marker(source_url, markers)
    )
    commit_pinned = bool(re.fullmatch(r"[0-9a-f]{40}", fields.get("repository_source_commit_sha", "")))
    clone_remote = (
        clone_command.startswith("git clone https://")
        and "--local" not in clone_command
        and not contains_forbidden_marker(clone_command, markers)
    )
    transcript_nonlocal = (
        transcript_hash_matches
        and not contains_forbidden_marker(fields.get("clone_network_transcript_path", ""), markers)
        and not contains_forbidden_marker(transcript_text, markers)
    )
    environment_nonlocal = (
        env_hash_matches
        and env_manifest.get("clone_was_local") is not True
        and not contains_forbidden_marker(fields.get("environment_manifest_path", ""), markers)
    )
    replay_nonlocal = (
        replay_hash_matches
        and "repo-local" not in fields.get("artifact_origin_statement", "")
        and not contains_forbidden_marker(fields.get("replay_artifact_bundle_path", ""), markers)
    )
    counter_mode_allowed = (
        fields.get("requested_counter_transition")
        in rules["accepted_counter_transition_modes"]
    )
    claim_boundary_present = fields.get("claim_boundary", "") != ""

    preacceptance_gates = {
        "contract_hash_matches": packet.get("origin_contract_hash")
        == contract["origin_contract_hash"],
        "required_keys_present": not missing_keys,
        "production_fields_nonempty": not empty_fields,
        "signed_external_origin_statement": signed_origin,
        "source_url_https_remote": source_remote,
        "commit_sha_pinned": commit_pinned,
        "clone_command_network_remote": clone_remote,
        "transcript_file_hash_matches": transcript_hash_matches,
        "transcript_content_nonlocal": transcript_nonlocal,
        "environment_manifest_file_hash_matches": env_hash_matches,
        "environment_manifest_nonlocal": environment_nonlocal,
        "replay_bundle_file_hash_matches": replay_hash_matches,
        "replay_bundle_nonlocal": replay_nonlocal,
        "counter_transition_mode_allowed": counter_mode_allowed,
        "claim_boundary_present": claim_boundary_present,
    }
    origin_accepted = all(preacceptance_gates.values())
    gates = dict(preacceptance_gates)
    gates["origin_attestation_accepted"] = origin_accepted
    failed = [gate for gate, passed in gates.items() if not passed]
    verdict = {
        "artifact": f"R105 {label} origin-attestation validation verdict",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "origin_contract_hash": contract["origin_contract_hash"],
        "verifier_rules_hash": rules["verifier_rules_hash"],
        "packet_hash": packet.get("attestation_template_hash")
        or packet.get("local_placeholder_hash")
        or stable_hash(packet),
        "packet_label": label,
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "missing_keys": missing_keys,
        "empty_fields": empty_fields,
        "origin_attestation_accepted": origin_accepted,
        "counter_transition_accepted": False,
        "counter_delta": 0,
        "accepted_external_reproduction_count": 0,
        "accepted_external_falsification_count": 0,
        "new_credit_delta": 0,
        "claim_boundary": (
            "R105 validates packet origin only. A passed origin verifier still needs "
            "a separate single-counter transition audit before any counter can move."
        ),
    }
    verdict["validation_hash"] = stable_self_hash(verdict, "validation_hash")
    return verdict


def build_blocker_queue(template_verdict: dict[str, Any], placeholder_verdict: dict[str, Any]) -> dict[str, Any]:
    queue = {
        "artifact": "R105 post external-origin verifier blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "template_validation_hash": template_verdict["validation_hash"],
        "placeholder_validation_hash": placeholder_verdict["validation_hash"],
        "queue": [
            {
                "blocker_id": "R105-G1-1",
                "priority": 1,
                "target_gate": "filled_r104_template",
                "needed_artifact": "all 20 R104 attestation fields filled with production values",
            },
            {
                "blocker_id": "R105-G1-2",
                "priority": 2,
                "target_gate": "remote_commit_and_network_clone",
                "needed_artifact": "https source URL, 40-hex commit SHA, and nonlocal clone command/transcript",
            },
            {
                "blocker_id": "R105-G1-3",
                "priority": 3,
                "target_gate": "nonlocal_environment_and_replay_bundle",
                "needed_artifact": "environment manifest and replay bundle whose hashes and content do not reuse R101/R103 local files",
            },
            {
                "blocker_id": "R105-G1-4",
                "priority": 4,
                "target_gate": "single_counter_transition_audit",
                "needed_artifact": "separate audit accepting exactly one reproduction or falsification counter transition",
            },
        ],
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    return queue


def write_stdout(root: Path, template_verdict: dict[str, Any], placeholder_verdict: dict[str, Any], queue: dict[str, Any]) -> str:
    text = "\n".join(
        [
            "R105 external-origin attestation verifier stdout",
            f"method={METHOD}",
            f"source_target_id={TARGET_ID}",
            f"upstream_target_id={UPSTREAM_TARGET_ID}",
            f"template_validation_hash={template_verdict['validation_hash']}",
            f"placeholder_validation_hash={placeholder_verdict['validation_hash']}",
            f"blocker_queue_hash={queue['blocker_queue_hash']}",
            "empty_template_origin_accepted=false",
            "local_placeholder_origin_accepted=false",
            "counter_transition_accepted=false",
            "new_credit_delta=0",
        ]
    ) + "\n"
    path = root / R105_STDOUT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    r104_result = load_json(root / R104_RESULT)
    contract = load_json(root / R104_CONTRACT)
    template = load_json(root / R104_TEMPLATE)
    placeholder = load_json(root / R104_PLACEHOLDER)
    preflight = load_json(root / R104_PREFLIGHT)
    r104_queue = load_json(root / R104_BLOCKER_QUEUE)

    rules = build_verifier_rules(contract, r104_result)
    write_json(root / R105_RULES, rules)
    template_verdict = validate_packet(root, template, contract, rules, "empty-template")
    write_json(root / R105_TEMPLATE_VALIDATION, template_verdict)
    placeholder_verdict = validate_packet(root, placeholder, contract, rules, "local-placeholder")
    write_json(root / R105_PLACEHOLDER_VALIDATION, placeholder_verdict)
    blocker_queue = build_blocker_queue(template_verdict, placeholder_verdict)
    write_json(root / R105_BLOCKER_QUEUE, blocker_queue)
    stdout_sha256 = write_stdout(root, template_verdict, placeholder_verdict, blocker_queue)

    requirements = [
        req(
            "A1",
            "R105 binds the R104 contract, preflight, and blocker queue",
            r104_result["summary"]["source_target_id"] == UPSTREAM_TARGET_ID
            and r104_result["origin_contract_hash"] == contract["origin_contract_hash"]
            and r104_result["preflight_hash"] == preflight["preflight_hash"]
            and r104_result["blocker_queue_hash"] == r104_queue["blocker_queue_hash"],
            {
                "r104_payload_hash": r104_result["payload_hash"],
                "origin_contract_hash": contract["origin_contract_hash"],
                "r104_preflight_hash": preflight["preflight_hash"],
            },
        ),
        req(
            "A2",
            "R105 emits executable verifier rules for all R104 fields",
            rules["required_field_count"] == 20
            and len(rules["gate_order"]) == 16
            and rules["origin_contract_hash"] == contract["origin_contract_hash"],
            {
                "verifier_rules_hash": rules["verifier_rules_hash"],
                "required_field_count": rules["required_field_count"],
                "gate_count": len(rules["gate_order"]),
            },
        ),
        req(
            "A3",
            "R105 rejects the empty R104 template",
            template_verdict["origin_attestation_accepted"] is False
            and "production_fields_nonempty" in template_verdict["failed_gates"]
            and len(template_verdict["empty_fields"]) == 20,
            {
                "template_validation_hash": template_verdict["validation_hash"],
                "empty_field_count": len(template_verdict["empty_fields"]),
            },
        ),
        req(
            "A4",
            "R105 rejects the local placeholder on nonlocal-origin gates",
            placeholder_verdict["origin_attestation_accepted"] is False
            and "source_url_https_remote" in placeholder_verdict["failed_gates"]
            and "clone_command_network_remote" in placeholder_verdict["failed_gates"]
            and "environment_manifest_nonlocal" in placeholder_verdict["failed_gates"]
            and "replay_bundle_nonlocal" in placeholder_verdict["failed_gates"],
            {
                "placeholder_validation_hash": placeholder_verdict["validation_hash"],
                "failed_gates": placeholder_verdict["failed_gates"],
            },
        ),
        req(
            "A5",
            "R105 keeps counters at zero and emits the next verifier blocker queue",
            template_verdict["new_credit_delta"] == 0
            and placeholder_verdict["new_credit_delta"] == 0
            and [item["target_gate"] for item in blocker_queue["queue"]]
            == [
                "filled_r104_template",
                "remote_commit_and_network_clone",
                "nonlocal_environment_and_replay_bundle",
                "single_counter_transition_audit",
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
        validation_errors.append("one or more R105 requirements failed")
    if template_verdict["origin_attestation_accepted"] or placeholder_verdict[
        "origin_attestation_accepted"
    ]:
        validation_errors.append("R105 must reject the empty template and local placeholder")

    payload = {
        "artifact": "B1/B7 cone01 R105 external-origin attestation verifier gate",
        "method": METHOD,
        "version": VERSION,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "generated_at_unix": int(time.time()),
        "verifier_rules_path": R105_RULES,
        "verifier_rules_hash": rules["verifier_rules_hash"],
        "template_validation_path": R105_TEMPLATE_VALIDATION,
        "template_validation_hash": template_verdict["validation_hash"],
        "placeholder_validation_path": R105_PLACEHOLDER_VALIDATION,
        "placeholder_validation_hash": placeholder_verdict["validation_hash"],
        "stdout_path": R105_STDOUT,
        "stdout_sha256": stdout_sha256,
        "blocker_queue_path": R105_BLOCKER_QUEUE,
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
            "required_field_count": rules["required_field_count"],
            "verifier_gate_count": len(rules["gate_order"]),
            "empty_template_origin_accepted": template_verdict[
                "origin_attestation_accepted"
            ],
            "empty_template_failed_gate_count": template_verdict["failed_gate_count"],
            "local_placeholder_origin_accepted": placeholder_verdict[
                "origin_attestation_accepted"
            ],
            "local_placeholder_failed_gate_count": placeholder_verdict[
                "failed_gate_count"
            ],
            "counter_transition_accepted": False,
            "counter_delta": 0,
            "accepted_external_reproduction_count": 0,
            "accepted_external_falsification_count": 0,
            "new_credit_delta": 0,
            "verifier_rules_hash": rules["verifier_rules_hash"],
            "template_validation_hash": template_verdict["validation_hash"],
            "placeholder_validation_hash": placeholder_verdict["validation_hash"],
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
        "# B1/B7 Cone01 R105 External-Origin Attestation Verifier Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R105 converts the R104 external-origin attestation contract into executable",
        "verifier rules. It rejects both the empty R104 template and the local",
        "placeholder packet, while keeping every counter at zero.",
        "",
        "## Key Counters",
        "",
        f"- Required fields: `{summary['required_field_count']}`",
        f"- Verifier gates: `{summary['verifier_gate_count']}`",
        f"- Empty template accepted: `{summary['empty_template_origin_accepted']}`",
        f"- Empty template failed gates: `{summary['empty_template_failed_gate_count']}`",
        f"- Local placeholder accepted: `{summary['local_placeholder_origin_accepted']}`",
        f"- Local placeholder failed gates: `{summary['local_placeholder_failed_gate_count']}`",
        f"- Counter transition accepted: `{summary['counter_transition_accepted']}`",
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
            f"- Verifier rules: `{R105_RULES}`",
            f"- Empty-template validation: `{R105_TEMPLATE_VALIDATION}`",
            f"- Local-placeholder validation: `{R105_PLACEHOLDER_VALIDATION}`",
            f"- Blocker queue: `{R105_BLOCKER_QUEUE}`",
            "",
            "## Claim Boundary",
            "",
            "R105 is a verifier-rules gate. It does not accept external origin, does",
            "not move reproduction or falsification counters, does not grant new",
            "credit, and does not close B7/O3/resource/layout claims.",
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
