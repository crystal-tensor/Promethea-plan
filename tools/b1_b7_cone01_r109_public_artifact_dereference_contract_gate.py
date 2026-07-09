#!/usr/bin/env python3
"""T-B1-004hg/T-B7-016p: R109 public artifact dereference contract gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r109_public_artifact_dereference_contract_gate_v0"
STATUS = "cone01_r109_public_dereference_contract_ready_url_only_rejected"
MODEL_STATUS = "r108_preflight_requires_public_artifact_dereference_challenge"
VERSION = "0.1"
TARGET_ID = "T-B1-004hg/T-B7-016p"
UPSTREAM_TARGET_ID = "T-B1-004hf/T-B7-016o"
SUBMISSION_DIR = "results/B1_B7_cone01_o3_f4_exit_route_submissions"
R109_DIR = f"{SUBMISSION_DIR}/R109-G1-public-artifact-dereference-contract"

R108_RESULT = "results/B1_B7_cone01_R108_material_evidence_preflight_verifier_gate_v0.json"
R108_RULES = (
    f"{SUBMISSION_DIR}/R108-G1-material-evidence-preflight-verifier/"
    "material-evidence-preflight-verifier-rules.json"
)
R108_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R108-G1-post-preflight-verifier-blocker-queue.json"

R109_CONTRACT = f"{R109_DIR}/public-artifact-dereference-contract.json"
R109_TEMPLATE = f"{R109_DIR}/public-artifact-dereference-packet.template.json"
R109_URL_ONLY_PACKET = f"{R109_DIR}/url-only-public-artifact-negative-control.json"
R109_URL_ONLY_VERDICT = f"{R109_DIR}/url-only-public-artifact-preflight.verdict.json"
R109_CACHED_PACKET = f"{R109_DIR}/cached-transcript-negative-control.json"
R109_CACHED_VERDICT = f"{R109_DIR}/cached-transcript-preflight.verdict.json"
R109_CACHED_CI_TRANSCRIPT = f"{R109_DIR}/cached-ci-run-http-transcript.json"
R109_CACHED_ARTIFACT_TRANSCRIPT = f"{R109_DIR}/cached-artifact-http-transcript.json"
R109_CACHED_KEY_TRANSCRIPT = f"{R109_DIR}/cached-key-http-transcript.json"
R109_BLOCKER_QUEUE = f"{SUBMISSION_DIR}/R109-G1-post-public-dereference-contract-blocker-queue.json"
R109_STDOUT = f"{SUBMISSION_DIR}/R109-G1-public-artifact-dereference-contract.stdout.txt"

RESULT_PATH = "results/B1_B7_cone01_R109_public_artifact_dereference_contract_gate_v0.json"
REPORT_PATH = "research/B1_B7_cone01_R109_public_artifact_dereference_contract_gate.md"

REQUIRED_FIELDS = [
    "challenge_nonce",
    "challenge_issued_at_unix",
    "challenge_scope",
    "reviewer_id",
    "reviewer_key_url",
    "reviewer_key_http_transcript_path",
    "reviewer_key_http_transcript_sha256",
    "ci_run_url",
    "ci_run_http_transcript_path",
    "ci_run_http_transcript_sha256",
    "artifact_url",
    "artifact_http_transcript_path",
    "artifact_http_transcript_sha256",
    "immutable_commit_sha",
    "requested_counter_transition",
    "claim_boundary",
]

HASH_BINDINGS = {
    "reviewer_key_http_transcript_path": "reviewer_key_http_transcript_sha256",
    "ci_run_http_transcript_path": "ci_run_http_transcript_sha256",
    "artifact_http_transcript_path": "artifact_http_transcript_sha256",
}

ACCEPTANCE_GATES = [
    "contract_hash_matches",
    "required_fields_present",
    "required_fields_nonempty",
    "challenge_nonce_format",
    "challenge_scope_matches_target",
    "immutable_commit_sha_format",
    "urls_are_https",
    "http_transcript_hashes_match",
    "http_transcripts_are_live_public_fetches",
    "http_transcripts_bind_challenge_nonce",
    "http_transcripts_bind_requested_urls",
    "counter_transition_mode_allowed",
    "claim_boundary_present",
]

ACCEPTED_COUNTER_TRANSITIONS = [
    "external_reproduction_counter_increment",
    "external_falsification_counter_increment",
]

SYNTHETIC_MARKERS = [
    "url-only-negative-control",
    "cached-transcript-negative-control",
    "local-cache-no-live-fetch",
    "not-live-public-fetch",
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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_contract(root: Path, r108_result: dict[str, Any], r108_rules: dict[str, Any]) -> dict[str, Any]:
    contract = {
        "artifact": "R109 public artifact dereference contract",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_r108_result": R108_RESULT,
        "source_r108_rules": R108_RULES,
        "source_r108_blocker_queue": R108_BLOCKER_QUEUE,
        "source_r108_payload_hash": r108_result["payload_hash"],
        "source_r108_verifier_rules_hash": r108_rules["verifier_rules_hash"],
        "required_fields": REQUIRED_FIELDS,
        "required_hash_bindings": HASH_BINDINGS,
        "acceptance_gates": ACCEPTANCE_GATES,
        "accepted_counter_transition_modes": ACCEPTED_COUNTER_TRANSITIONS,
        "synthetic_markers": SYNTHETIC_MARKERS,
        "claim_boundary": (
            "R109 requires public HTTP dereference transcripts bound to a challenge "
            "nonce before R108 passing material may enter a single-counter audit."
        ),
    }
    contract["contract_hash"] = stable_self_hash(contract, "contract_hash")
    write_json(root / R109_CONTRACT, contract)
    return contract


def base_fields(contract: dict[str, Any]) -> dict[str, Any]:
    fields = {field: "" for field in REQUIRED_FIELDS}
    fields.update(
        {
            "challenge_nonce": "R109-CHALLENGE-0001-abcdef1234567890",
            "challenge_issued_at_unix": 1783557600,
            "challenge_scope": TARGET_ID,
            "reviewer_id": "r109-public-artifact-reviewer",
            "reviewer_key_url": "https://github.com/r109-reviewer.keys",
            "ci_run_url": "https://github.com/crystal-tensor/Prometheus-plan/actions/runs/1090000001",
            "artifact_url": "https://github.com/crystal-tensor/Prometheus-plan/actions/runs/1090000001/artifacts/r109-material-evidence",
            "immutable_commit_sha": "c9d6885fe9dd97b2bbeff03aa57c9c7e1cd78c23",
            "requested_counter_transition": "external_reproduction_counter_increment",
            "claim_boundary": (
                "One external reproduction counter request only; no B7/O3/resource/layout claim."
            ),
        }
    )
    return fields


def build_template(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    template = {
        "artifact": "R109 public artifact dereference packet template",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "contract_hash": contract["contract_hash"],
        "fields": {field: "" for field in REQUIRED_FIELDS},
        "template_status": "fillable_not_accepted",
    }
    template["template_hash"] = stable_self_hash(template, "template_hash")
    write_json(root / R109_TEMPLATE, template)
    return template


def build_url_only_packet(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    fields = base_fields(contract)
    fields.update(
        {
            "reviewer_key_http_transcript_path": "",
            "reviewer_key_http_transcript_sha256": "",
            "ci_run_http_transcript_path": "",
            "ci_run_http_transcript_sha256": "",
            "artifact_http_transcript_path": "",
            "artifact_http_transcript_sha256": "",
            "claim_boundary": "url-only-negative-control; should be rejected before counter audit",
        }
    )
    packet = {
        "artifact": "R109 URL-only public artifact negative control",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "contract_hash": contract["contract_hash"],
        "fields": fields,
        "negative_control_reason": "URLs are present, but no dereference transcripts are attached.",
    }
    packet["url_only_packet_hash"] = stable_self_hash(packet, "url_only_packet_hash")
    write_json(root / R109_URL_ONLY_PACKET, packet)
    return packet


def transcript(url: str, nonce: str, *, live: bool, marker: str) -> dict[str, Any]:
    return {
        "url": url,
        "http_status": 200,
        "fetched_at_unix": 1783557601,
        "challenge_nonce": nonce,
        "live_public_fetch": live,
        "response_body_sha256": stable_hash({"url": url, "nonce": nonce, "marker": marker}),
        "marker": marker,
    }


def build_cached_packet(root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    fields = base_fields(contract)
    nonce = fields["challenge_nonce"]
    transcripts = {
        R109_CACHED_KEY_TRANSCRIPT: transcript(
            fields["reviewer_key_url"], nonce, live=False, marker="cached-transcript-negative-control"
        ),
        R109_CACHED_CI_TRANSCRIPT: transcript(
            fields["ci_run_url"], nonce, live=False, marker="local-cache-no-live-fetch"
        ),
        R109_CACHED_ARTIFACT_TRANSCRIPT: transcript(
            fields["artifact_url"], nonce, live=False, marker="not-live-public-fetch"
        ),
    }
    for path, payload in transcripts.items():
        write_json(root / path, payload)
    fields.update(
        {
            "reviewer_key_http_transcript_path": R109_CACHED_KEY_TRANSCRIPT,
            "reviewer_key_http_transcript_sha256": file_hash(root / R109_CACHED_KEY_TRANSCRIPT),
            "ci_run_http_transcript_path": R109_CACHED_CI_TRANSCRIPT,
            "ci_run_http_transcript_sha256": file_hash(root / R109_CACHED_CI_TRANSCRIPT),
            "artifact_http_transcript_path": R109_CACHED_ARTIFACT_TRANSCRIPT,
            "artifact_http_transcript_sha256": file_hash(root / R109_CACHED_ARTIFACT_TRANSCRIPT),
            "claim_boundary": "cached-transcript-negative-control; no live public fetch",
        }
    )
    packet = {
        "artifact": "R109 cached transcript negative control",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "contract_hash": contract["contract_hash"],
        "fields": fields,
        "negative_control_reason": (
            "Transcript files exist and hashes match, but they explicitly say "
            "live_public_fetch=false."
        ),
    }
    packet["cached_packet_hash"] = stable_self_hash(packet, "cached_packet_hash")
    write_json(root / R109_CACHED_PACKET, packet)
    return packet


def transcript_hashes_match(root: Path, fields: dict[str, Any]) -> bool:
    for path_field, hash_field in HASH_BINDINGS.items():
        rel_path = fields.get(path_field)
        expected = fields.get(hash_field)
        if not rel_path or not expected:
            return False
        path = root / rel_path
        if not path.is_file() or file_hash(path) != expected:
            return False
    return True


def load_transcripts(root: Path, fields: dict[str, Any]) -> list[dict[str, Any]]:
    transcripts: list[dict[str, Any]] = []
    for path_field in HASH_BINDINGS:
        rel_path = fields.get(path_field)
        if rel_path and (root / rel_path).is_file():
            transcripts.append(load_json(root / rel_path))
    return transcripts


def validate_packet(root: Path, packet: dict[str, Any], contract: dict[str, Any], label: str) -> dict[str, Any]:
    fields = packet["fields"]
    transcripts = load_transcripts(root, fields)
    expected_urls = {
        fields.get("reviewer_key_url"),
        fields.get("ci_run_url"),
        fields.get("artifact_url"),
    }
    transcript_urls = {item.get("url") for item in transcripts}
    nonce = fields.get("challenge_nonce")
    serialized = json.dumps(packet, sort_keys=True) + json.dumps(transcripts, sort_keys=True)
    gates = {
        "contract_hash_matches": packet.get("contract_hash") == contract["contract_hash"],
        "required_fields_present": all(field in fields for field in contract["required_fields"]),
        "required_fields_nonempty": all(fields.get(field) not in (None, "") for field in contract["required_fields"]),
        "challenge_nonce_format": bool(re.fullmatch(r"R109-CHALLENGE-[0-9A-Za-z-]{12,64}", str(nonce))),
        "challenge_scope_matches_target": fields.get("challenge_scope") == TARGET_ID,
        "immutable_commit_sha_format": bool(re.fullmatch(r"[0-9a-f]{40}", str(fields.get("immutable_commit_sha", "")))),
        "urls_are_https": all(str(url).startswith("https://") for url in expected_urls),
        "http_transcript_hashes_match": transcript_hashes_match(root, fields),
        "http_transcripts_are_live_public_fetches": len(transcripts) == 3
        and all(item.get("live_public_fetch") is True and item.get("http_status") == 200 for item in transcripts),
        "http_transcripts_bind_challenge_nonce": len(transcripts) == 3
        and all(item.get("challenge_nonce") == nonce for item in transcripts),
        "http_transcripts_bind_requested_urls": len(transcripts) == 3 and expected_urls == transcript_urls,
        "counter_transition_mode_allowed": fields.get("requested_counter_transition")
        in contract["accepted_counter_transition_modes"],
        "claim_boundary_present": fields.get("claim_boundary") not in (None, ""),
        "synthetic_markers_absent": not any(marker in serialized for marker in contract["synthetic_markers"]),
    }
    gates["dereference_packet_accepted"] = all(gates.values())
    failed = [gate for gate, passed in gates.items() if not passed]
    verdict = {
        "artifact": f"R109 public dereference preflight verdict: {label}",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "contract_hash": contract["contract_hash"],
        "packet_label": label,
        "gates": gates,
        "passed_gate_count": sum(1 for passed in gates.values() if passed),
        "failed_gate_count": len(failed),
        "failed_gates": failed,
        "dereference_packet_accepted": gates["dereference_packet_accepted"],
        "claim_boundary": (
            "R109 acceptance would only allow R108 rerun and a separate single-counter audit."
        ),
    }
    verdict["preflight_hash"] = stable_self_hash(verdict, "preflight_hash")
    return verdict


def build_blocker_queue(root: Path, contract: dict[str, Any], url_verdict: dict[str, Any], cached_verdict: dict[str, Any]) -> dict[str, Any]:
    queue = {
        "artifact": "R109 post-public-dereference-contract blocker queue",
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "contract_hash": contract["contract_hash"],
        "url_only_preflight_hash": url_verdict["preflight_hash"],
        "cached_transcript_preflight_hash": cached_verdict["preflight_hash"],
        "counter_transition_accepted": False,
        "counter_delta": 0,
        "accepted_external_reproduction_count": 0,
        "accepted_external_falsification_count": 0,
        "new_credit_delta": 0,
        "blockers": [
            {
                "blocker_id": "R109-G1-1",
                "label": "Attach live public HTTP transcripts for reviewer key, CI run, and artifact URL.",
            },
            {
                "blocker_id": "R109-G1-2",
                "label": "Bind every transcript to the R109 challenge nonce and requested URL.",
            },
            {
                "blocker_id": "R109-G1-3",
                "label": "Remove local-cache/synthetic markers and rerun R109 plus R108.",
            },
            {
                "blocker_id": "R109-G1-4",
                "label": "Only after R109/R108 pass, run a separate single-counter audit.",
            },
        ],
    }
    queue["blocker_queue_hash"] = stable_self_hash(queue, "blocker_queue_hash")
    write_json(root / R109_BLOCKER_QUEUE, queue)
    return queue


def build_report(result: dict[str, Any]) -> str:
    s = result["summary"]
    lines = [
        "# B1/B7 Cone01 R109 Public Artifact Dereference Contract Gate",
        "",
        f"- Target: `{TARGET_ID}`",
        f"- Upstream target: `{UPSTREAM_TARGET_ID}`",
        f"- Method: `{METHOD}`",
        f"- Status: `{STATUS}`",
        f"- Model status: `{MODEL_STATUS}`",
        "",
        "## Result",
        "",
        "R109 adds the public dereference layer after R108. It rejects URL-only",
        "evidence and cached transcript evidence, requiring live public HTTP",
        "transcripts bound to the challenge nonce before any R108 rerun or",
        "single-counter audit can proceed.",
        "",
        "## Key Counters",
        "",
        f"- Required fields: `{s['required_field_count']}`",
        f"- Acceptance gates: `{s['acceptance_gate_count']}`",
        f"- URL-only packet accepted: `{s['url_only_packet_accepted']}`",
        f"- URL-only gates passed / failed: `{s['url_only_passed_gate_count']}` / `{s['url_only_failed_gate_count']}`",
        f"- Cached transcript packet accepted: `{s['cached_packet_accepted']}`",
        f"- Cached transcript gates passed / failed: `{s['cached_passed_gate_count']}` / `{s['cached_failed_gate_count']}`",
        f"- Counter transition accepted: `{s['counter_transition_accepted']}`",
        f"- Counter delta: `{s['counter_delta']}`",
        f"- Accepted external reproductions: `{s['accepted_external_reproduction_count']}`",
        f"- Accepted external falsifications: `{s['accepted_external_falsification_count']}`",
        f"- New credit delta: `{s['new_credit_delta']}`",
        "",
        "## Requirements",
        "",
    ]
    for requirement in result["requirements"]:
        mark = "PASS" if requirement["passed"] else "FAIL"
        lines.append(f"- `{requirement['requirement_id']}` {mark}: {requirement['label']}")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Result JSON: `{RESULT_PATH}`",
            f"- Contract: `{R109_CONTRACT}`",
            f"- Template: `{R109_TEMPLATE}`",
            f"- URL-only packet: `{R109_URL_ONLY_PACKET}`",
            f"- URL-only verdict: `{R109_URL_ONLY_VERDICT}`",
            f"- Cached transcript packet: `{R109_CACHED_PACKET}`",
            f"- Cached transcript verdict: `{R109_CACHED_VERDICT}`",
            f"- Blocker queue: `{R109_BLOCKER_QUEUE}`",
            "",
            "## Claim Boundary",
            "",
            "R109 is a dereference-contract and negative-control gate. It does not",
            "accept an external reproduction, does not move a counter, and does not",
            "grant B7/O3/resource/layout credit.",
            "",
        ]
    )
    return "\n".join(lines)


def run(root: Path) -> dict[str, Any]:
    r108_result = load_json(root / R108_RESULT)
    r108_rules = load_json(root / R108_RULES)
    contract = build_contract(root, r108_result, r108_rules)
    template = build_template(root, contract)
    url_packet = build_url_only_packet(root, contract)
    cached_packet = build_cached_packet(root, contract)
    url_verdict = validate_packet(root, url_packet, contract, "url-only")
    cached_verdict = validate_packet(root, cached_packet, contract, "cached-transcript")
    write_json(root / R109_URL_ONLY_VERDICT, url_verdict)
    write_json(root / R109_CACHED_VERDICT, cached_verdict)
    blocker_queue = build_blocker_queue(root, contract, url_verdict, cached_verdict)

    requirements = [
        req(
            "A1",
            "R109 binds the R108 result and verifier rules",
            contract["source_r108_payload_hash"] == r108_result["payload_hash"]
            and contract["source_r108_verifier_rules_hash"] == r108_rules["verifier_rules_hash"],
            {
                "r108_payload_hash": contract["source_r108_payload_hash"],
                "r108_verifier_rules_hash": contract["source_r108_verifier_rules_hash"],
            },
        ),
        req(
            "A2",
            "R109 emits a challenge-nonce public dereference contract and template",
            len(contract["required_fields"]) == 16 and len(contract["acceptance_gates"]) == 13,
            {
                "contract_hash": contract["contract_hash"],
                "template_hash": template["template_hash"],
                "required_field_count": len(contract["required_fields"]),
                "acceptance_gate_count": len(contract["acceptance_gates"]),
            },
        ),
        req(
            "A3",
            "R109 rejects URL-only public artifact claims",
            url_verdict["dereference_packet_accepted"] is False
            and "http_transcript_hashes_match" in url_verdict["failed_gates"],
            {
                "url_only_preflight_hash": url_verdict["preflight_hash"],
                "url_only_failed_gates": url_verdict["failed_gates"],
            },
        ),
        req(
            "A4",
            "R109 rejects cached transcripts that are not live public fetches",
            cached_verdict["dereference_packet_accepted"] is False
            and "http_transcripts_are_live_public_fetches" in cached_verdict["failed_gates"],
            {
                "cached_transcript_preflight_hash": cached_verdict["preflight_hash"],
                "cached_failed_gates": cached_verdict["failed_gates"],
            },
        ),
        req(
            "A5",
            "R109 keeps counters and new credit at zero",
            blocker_queue["counter_delta"] == 0
            and blocker_queue["accepted_external_reproduction_count"] == 0
            and blocker_queue["accepted_external_falsification_count"] == 0
            and blocker_queue["new_credit_delta"] == 0,
            {
                "counter_delta": blocker_queue["counter_delta"],
                "accepted_external_reproduction_count": blocker_queue["accepted_external_reproduction_count"],
                "accepted_external_falsification_count": blocker_queue["accepted_external_falsification_count"],
                "new_credit_delta": blocker_queue["new_credit_delta"],
            },
        ),
        req(
            "A6",
            "R109 emits blockers for live transcript, nonce binding, and separate counter audit",
            len(blocker_queue["blockers"]) == 4,
            {
                "blocker_ids": [blocker["blocker_id"] for blocker in blocker_queue["blockers"]],
                "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
            },
        ),
    ]
    failed_requirement_ids = [
        requirement["requirement_id"] for requirement in requirements if not requirement["passed"]
    ]
    validation_errors: list[str] = []
    if failed_requirement_ids:
        validation_errors.append(f"failed_requirements={failed_requirement_ids}")

    summary = {
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "required_field_count": len(contract["required_fields"]),
        "acceptance_gate_count": len(contract["acceptance_gates"]),
        "url_only_packet_accepted": url_verdict["dereference_packet_accepted"],
        "url_only_passed_gate_count": url_verdict["passed_gate_count"],
        "url_only_failed_gate_count": url_verdict["failed_gate_count"],
        "cached_packet_accepted": cached_verdict["dereference_packet_accepted"],
        "cached_passed_gate_count": cached_verdict["passed_gate_count"],
        "cached_failed_gate_count": cached_verdict["failed_gate_count"],
        "counter_transition_accepted": blocker_queue["counter_transition_accepted"],
        "counter_delta": blocker_queue["counter_delta"],
        "accepted_external_reproduction_count": blocker_queue["accepted_external_reproduction_count"],
        "accepted_external_falsification_count": blocker_queue["accepted_external_falsification_count"],
        "new_credit_delta": blocker_queue["new_credit_delta"],
        "contract_hash": contract["contract_hash"],
        "template_hash": template["template_hash"],
        "url_only_packet_hash": url_packet["url_only_packet_hash"],
        "url_only_preflight_hash": url_verdict["preflight_hash"],
        "cached_packet_hash": cached_packet["cached_packet_hash"],
        "cached_transcript_preflight_hash": cached_verdict["preflight_hash"],
        "blocker_queue_hash": blocker_queue["blocker_queue_hash"],
        "requirements_passed": sum(1 for requirement in requirements if requirement["passed"]),
        "requirements_failed": len(failed_requirement_ids),
        "failed_requirement_ids": failed_requirement_ids,
        "validation_error_count": len(validation_errors),
    }
    payload = {
        "artifact": "B1/B7 cone01 R109 public artifact dereference contract gate",
        "version": VERSION,
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "requirement_count": len(requirements),
        "requirements_passed": summary["requirements_passed"],
        "requirements_failed": summary["requirements_failed"],
        "requirements": requirements,
        "validation_error_count": len(validation_errors),
        "validation_errors": validation_errors,
        "contract_path": R109_CONTRACT,
        "template_path": R109_TEMPLATE,
        "url_only_packet_path": R109_URL_ONLY_PACKET,
        "url_only_preflight_path": R109_URL_ONLY_VERDICT,
        "cached_packet_path": R109_CACHED_PACKET,
        "cached_transcript_preflight_path": R109_CACHED_VERDICT,
        "blocker_queue_path": R109_BLOCKER_QUEUE,
        "stdout_path": R109_STDOUT,
        "summary": summary,
    }
    payload["payload_hash"] = stable_self_hash(payload, "payload_hash")
    payload["summary"]["payload_hash"] = payload["payload_hash"]
    write_json(root / RESULT_PATH, payload)
    report_path = root / REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(payload), encoding="utf-8")
    stdout = {
        "artifact": payload["artifact"],
        "method": METHOD,
        "source_target_id": TARGET_ID,
        "requirements_passed": payload["requirements_passed"],
        "requirements_failed": payload["requirements_failed"],
        "url_only_packet_accepted": url_verdict["dereference_packet_accepted"],
        "cached_packet_accepted": cached_verdict["dereference_packet_accepted"],
        "counter_delta": blocker_queue["counter_delta"],
        "new_credit_delta": blocker_queue["new_credit_delta"],
        "payload_hash": payload["payload_hash"],
    }
    stdout_path = root / R109_STDOUT
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(json.dumps(stdout, sort_keys=True) + "\n", encoding="utf-8")
    payload["stdout_sha256"] = file_hash(stdout_path)
    payload["summary"]["stdout_sha256"] = payload["stdout_sha256"]
    write_json(root / RESULT_PATH, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()
    payload = run(Path(args.repo_root).resolve())
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
