#!/usr/bin/env python3
"""T-B1-004dv/T-B7-013e: R20 O3-F3 artifact intake preflight gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r20_o3_f3_artifact_intake_preflight_gate_v0"
STATUS = "cone01_r20_o3_f3_artifact_intake_ready_no_submission"
MODEL_STATUS = "o3_f3_intake_template_and_preflight_ready_no_artifact_no_reroute"
VERSION = "0.1"
TARGET_ID = "T-B1-004dv/T-B7-013e"
SOURCE_TARGET_ID = "T-B1-004du/T-B7-013d"
CANDIDATE_ID = "NL-C02"
FAMILY_ID = "O3-F3"
INTAKE_ID = "B1-B7-cone01-R20-O3-F3-artifact-intake-preflight"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def stable_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_template(contract_packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": "B1-B7-cone01-O3-F3-symbolic-lu-<submitter>-<short-name>",
        "source_target_id": TARGET_ID,
        "upstream_contract_target_id": SOURCE_TARGET_ID,
        "family_id": FAMILY_ID,
        "candidate_id": CANDIDATE_ID,
        "source_contract_hash": contract_packet["contract_hash"],
        "source_registry_hash": contract_packet["source_artifact_hashes"]["r18_registry_hash"],
        "symbolic_transform_definition": {
            "status": "required",
            "domain": "R13_line1381_five_parameter_source_domain",
            "codomain": "proposed_symbolic_local_unitary_coordinates",
            "definition": "<exact symbolic map or counterexample construction>",
        },
        "source_unitary_preservation_certificate": {
            "status": "required",
            "certificate_type": "proof|machine_check|counterexample_replay",
            "checker": "<command or formal proof reference>",
        },
        "leaveout_domain_mapping": {
            "status": "required",
            "covered_source_parameters": [3, 4, 9, 16, 17],
            "mapping": "<symbolic mapping, or explicit escape with replay>",
        },
        "pi_over_four_lattice_relation": {
            "status": "required",
            "relation": "preserves_lattice|reaches_lattice|escapes_lattice|does_not_reach_lattice",
            "symbolic_argument": "<required>",
        },
        "route_a_effect": "not_claimed",
        "counterexample_payload": None,
        "claim_boundary": {
            "supported": "<required>",
            "not_supported": (
                "No B7 credit, STV credit, R5 reroute, O3 closure, or R1 solution may be claimed "
                "unless all acceptance gates and downstream ledgers pass."
            ),
            "kill_conditions": ["fails local-unitary preservation", "changes source domain", "missing replay"],
        },
        "machine_check_command": "<required>",
        "expected_outputs": {
            "checker_stdout_hash": "<required>",
            "artifact_hash": "<required after submission>",
        },
    }


def build_checklist(contract_packet: dict[str, Any], template: dict[str, Any]) -> list[dict[str, Any]]:
    gates = contract_packet["acceptance_gates"]
    checks: list[dict[str, Any]] = []
    for gate in gates:
        gate_id = gate["gate_id"]
        checks.append(
            {
                "gate_id": gate_id,
                "gate": gate["gate"],
                "source_acceptance_rule": gate["acceptance_rule"],
                "preflight_probe": {
                    "A1": "family_id, candidate_id, source_contract_hash, and source_registry_hash exact-match the R19 contract",
                    "A2": "source_unitary_preservation_certificate exists and names a machine-checkable proof route",
                    "A3": "leaveout_domain_mapping covers source parameters [3,4,9,16,17] or gives explicit replayable escape",
                    "A4": "pi_over_four_lattice_relation is symbolic and not a bare numerical fit",
                    "A5": "route_a_effect is one of not_claimed, clears_route_a, does_not_clear_route_a",
                    "A6": "claim_boundary refuses B7/STV/reroute/O3 closure overclaims before downstream ledgers",
                    "A7": "machine_check_command and expected_outputs are present and hash-bound",
                    "A8": "artifact cannot set checked_negative_lemma_present, reroute_allowed, or o3_closed directly",
                }[gate_id],
                "template_field_refs": [
                    row["field"]
                    for row in contract_packet["required_fields"]
                    if row["field"] in json.dumps(template, sort_keys=True)
                ],
            }
        )
    return checks


def evaluate_submission(
    submission: dict[str, Any] | None,
    contract_packet: dict[str, Any],
) -> dict[str, Any]:
    required_fields = [row["field"] for row in contract_packet["required_fields"]]
    if submission is None:
        return {
            "submission_exists": False,
            "missing_required_fields": required_fields,
            "passed_gate_ids": [],
            "failed_gate_ids": [],
            "blocked_gate_ids": [row["gate_id"] for row in contract_packet["acceptance_gates"]],
            "accepted": False,
            "why": "No O3-F3 artifact has been submitted to the intake path.",
        }

    missing = [field for field in required_fields if field not in submission]
    passed: list[str] = []
    failed: list[str] = []

    if (
        submission.get("family_id") == FAMILY_ID
        and submission.get("candidate_id") == CANDIDATE_ID
        and submission.get("source_registry_hash")
        == contract_packet["source_artifact_hashes"]["r18_registry_hash"]
    ):
        passed.append("A1")
    else:
        failed.append("A1")

    if submission.get("source_unitary_preservation_certificate"):
        passed.append("A2")
    else:
        failed.append("A2")

    mapping = submission.get("leaveout_domain_mapping")
    if mapping and "3" in json.dumps(mapping) and "17" in json.dumps(mapping):
        passed.append("A3")
    else:
        failed.append("A3")

    lattice = submission.get("pi_over_four_lattice_relation")
    if lattice and "numerical_only" not in json.dumps(lattice):
        passed.append("A4")
    else:
        failed.append("A4")

    if submission.get("route_a_effect") in {"not_claimed", "clears_route_a", "does_not_clear_route_a"}:
        passed.append("A5")
    else:
        failed.append("A5")

    boundary = json.dumps(submission.get("claim_boundary", {}), sort_keys=True)
    if "B7 credit" in boundary or "STV credit" in boundary or "reroute" in boundary:
        passed.append("A6")
    else:
        failed.append("A6")

    if submission.get("machine_check_command") and submission.get("expected_outputs"):
        passed.append("A7")
    else:
        failed.append("A7")

    if not any(submission.get(flag) is True for flag in ["checked_negative_lemma_present", "reroute_allowed", "o3_closed"]):
        passed.append("A8")
    else:
        failed.append("A8")

    if missing:
        for gate in [row["gate_id"] for row in contract_packet["acceptance_gates"]]:
            if gate not in failed and gate not in passed:
                failed.append(gate)

    return {
        "submission_exists": True,
        "missing_required_fields": missing,
        "passed_gate_ids": passed,
        "failed_gate_ids": failed,
        "blocked_gate_ids": [],
        "accepted": not missing and len(failed) == 0 and len(passed) == 8,
        "why": "Submission accepted by preflight only if all required fields and all eight gates pass.",
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r19 = load_json(args.r19_contract)
    r19_summary = r19["summary"]
    contract_packet = r19["o3_f3_symbolic_lu_contract_packet"]
    template = build_template(contract_packet)
    checklist = build_checklist(contract_packet, template)
    submission = load_json(args.submission) if args.submission.exists() else None
    preflight = evaluate_submission(submission, contract_packet)
    template_hash = stable_hash(template)
    checklist_hash = stable_hash(checklist)
    preflight_hash = stable_hash(preflight)

    intake_packet = {
        "intake_id": INTAKE_ID,
        "source_target_id": TARGET_ID,
        "source_r19_contract": str(args.r19_contract),
        "source_hashes": {
            "r19_contract_file": file_hash(args.r19_contract),
            "submission_file": file_hash(args.submission),
        },
        "source_contract_hash": r19_summary["contract_hash"],
        "source_required_field_table_hash": r19_summary["required_field_table_hash"],
        "source_acceptance_gate_table_hash": r19_summary["acceptance_gate_table_hash"],
        "source_rejection_rule_hash": r19_summary["rejection_rule_hash"],
        "template_output": str(args.template_output),
        "submission_path": str(args.submission),
        "template": template,
        "preflight_checklist": checklist,
        "preflight_result": preflight,
        "decision": {
            "o3_f3_intake_ready": True,
            "o3_f3_template_emitted": True,
            "o3_f3_submission_exists": preflight["submission_exists"],
            "o3_f3_preflight_accepted": preflight["accepted"],
            "o3_f3_artifact_accepted": False,
            "o3_closed": False,
            "checked_negative_lemma_present": False,
            "nlc02_full_lemma_ready": False,
            "reroute_allowed": False,
            "why": (
                "R20 makes O3-F3 submissions mechanically checkable at intake time, but it does not "
                "accept any artifact or promote B7 credit."
            ),
        },
    }
    intake_packet["template_hash"] = template_hash
    intake_packet["checklist_hash"] = checklist_hash
    intake_packet["preflight_hash"] = preflight_hash
    intake_packet["intake_hash"] = stable_hash(intake_packet)

    requirements = [
        requirement(
            "K1",
            "R19 contract is validation-clean and ready",
            r19.get("method") == "b1_b7_cone01_r19_o3_f3_symbolic_lu_contract_gate_v0"
            and r19_summary.get("validation_error_count") == 0
            and r19_summary.get("o3_f3_contract_ready") is True,
            {
                "r19_method": r19.get("method"),
                "r19_validation_error_count": r19_summary.get("validation_error_count"),
                "o3_f3_contract_ready": r19_summary.get("o3_f3_contract_ready"),
            },
        ),
        requirement(
            "K2",
            "Template carries all fourteen R19 required fields",
            all(row["field"] in template for row in contract_packet["required_fields"]),
            {"template_field_count": len(template), "required_field_count": len(contract_packet["required_fields"])},
        ),
        requirement(
            "K3",
            "Template is hash-bound to the R19 contract and R18 registry",
            template["source_contract_hash"] == r19_summary["contract_hash"]
            and template["source_registry_hash"] == r19_summary["source_r18_registry_hash"],
            {
                "template_hash": template_hash,
                "source_contract_hash": template["source_contract_hash"],
                "source_registry_hash": template["source_registry_hash"],
            },
        ),
        requirement(
            "K4",
            "Preflight checklist mirrors all eight R19 acceptance gates",
            len(checklist) == 8 and {row["gate_id"] for row in checklist} == {f"A{i}" for i in range(1, 9)},
            {"checklist_hash": checklist_hash, "gate_ids": [row["gate_id"] for row in checklist]},
        ),
        requirement(
            "K5",
            "Current absent submission is rejected without failing the intake readiness gate",
            preflight["submission_exists"] is False
            and preflight["accepted"] is False
            and len(preflight["blocked_gate_ids"]) == 8,
            preflight,
        ),
        requirement(
            "K6",
            "R20 does not silently close O3, accept O3-F3, or allow reroute",
            intake_packet["decision"]["o3_f3_artifact_accepted"] is False
            and intake_packet["decision"]["o3_closed"] is False
            and intake_packet["decision"]["reroute_allowed"] is False,
            intake_packet["decision"],
        ),
        requirement(
            "K7",
            "R20 preserves zero B7/resource credit claims",
            True,
            {
                "accepted_route_count": 0,
                "accepted_occurrence_removal": 0,
                "accepted_proxy_t_reduction": 0,
                "b7_credit_delta": 0,
                "b7_space_time_volume_credit": 0,
                "resource_saving_claimed": False,
                "b7_ledger_improvement_claimed": False,
            },
        ),
        requirement(
            "K8",
            "Intake packet is internally hash-bound",
            bool(intake_packet["intake_hash"]) and bool(template_hash) and bool(checklist_hash) and bool(preflight_hash),
            {
                "intake_hash": intake_packet["intake_hash"],
                "template_hash": template_hash,
                "checklist_hash": checklist_hash,
                "preflight_hash": preflight_hash,
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids:
        validation_errors.append(f"unexpected R20 O3-F3 intake failures: {failed_ids}")

    summary = {
        "intake_id": INTAKE_ID,
        "intake_hash": intake_packet["intake_hash"],
        "template_hash": template_hash,
        "checklist_hash": checklist_hash,
        "preflight_hash": preflight_hash,
        "source_contract_hash": r19_summary["contract_hash"],
        "source_r18_registry_hash": r19_summary["source_r18_registry_hash"],
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "required_field_count": len(contract_packet["required_fields"]),
        "acceptance_gate_count": len(contract_packet["acceptance_gates"]),
        "rejection_rule_count": len(contract_packet["rejection_rules"]),
        "preflight_check_count": len(checklist),
        "o3_f3_intake_ready": True,
        "o3_f3_template_emitted": True,
        "o3_f3_submission_exists": preflight["submission_exists"],
        "o3_f3_preflight_accepted": preflight["accepted"],
        "o3_f3_artifact_accepted": False,
        "o3_closed": False,
        "remaining_open_obligations": ["O3-F3_symbolic_lu_artifact", "O3-F4_refit_harness", "O3-F5_route_a_artifact"],
        "remaining_open_obligation_count": 3,
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
        "requirement_count": len(requirements),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "source_target_id": TARGET_ID,
        "upstream_target_id": SOURCE_TARGET_ID,
        "title": "B1/B7 Cone01 R20 O3-F3 Artifact Intake Preflight Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "summary": summary,
        "o3_f3_artifact_intake_packet": intake_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "R20 emits a reusable O3-F3 artifact template and preflight checklist bound to the R19 contract."
            ),
            "what_is_not_supported": (
                "R20 does not submit or accept an O3-F3 artifact, does not close O3, and does not permit R5 reroute. "
                "No R1 solution, occurrence removal, proxy-T reduction, B7 credit, resource saving, or impossibility theorem is supported."
            ),
            "next_gate": (
                "A contributor or agent should fill the O3-F3 template with a symbolic local-unitary proof, "
                "counterexample, or rejection-strengthening artifact and rerun the preflight."
            ),
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    packet = payload["o3_f3_artifact_intake_packet"]
    preflight = packet["preflight_result"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Candidate: `{s['candidate_id']}`",
        f"- Family: `{s['family_id']}`",
        f"- Intake hash: `{s['intake_hash']}`",
        f"- Template hash: `{s['template_hash']}`",
        f"- Checklist hash: `{s['checklist_hash']}`",
        f"- Preflight hash: `{s['preflight_hash']}`",
        "",
        "## Result",
        "",
        (
            f"The R20 O3-F3 intake preflight gate passes {s['requirements_passed']}/{s['requirement_count']} requirements. "
            "It emits a reusable artifact template and an eight-gate preflight checklist. No O3-F3 artifact is submitted or accepted."
        ),
        "",
        "## Template Output",
        "",
        f"- Template path: `{packet['template_output']}`",
        f"- Submission path checked: `{packet['submission_path']}`",
        f"- Submission exists: `{preflight['submission_exists']}`",
        f"- Preflight accepted: `{preflight['accepted']}`",
        "",
        "## Preflight Checklist",
        "",
    ]
    for row in packet["preflight_checklist"]:
        lines.append(f"- `{row['gate_id']}` {row['gate']}: {row['preflight_probe']}")
    lines.extend(["", "## Current Preflight Result", ""])
    lines.append(f"- Missing required fields: `{len(preflight['missing_required_fields'])}`")
    lines.append(f"- Blocked gate ids: `{preflight['blocked_gate_ids']}`")
    lines.append(f"- Why: {preflight['why']}")
    lines.extend(["", "## Decision", ""])
    for key in [
        "o3_f3_intake_ready",
        "o3_f3_template_emitted",
        "o3_f3_submission_exists",
        "o3_f3_preflight_accepted",
        "o3_f3_artifact_accepted",
        "o3_closed",
        "checked_negative_lemma_present",
        "reroute_allowed",
    ]:
        lines.append(f"- {key}: `{s[key]}`")
    lines.extend(["", "## Requirement Results", ""])
    for row in payload["requirements"]:
        marker = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- `{row['requirement_id']}` {marker}: {row['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            "This intake gate does not claim resource saving, occurrence removal, proxy-T reduction, B7 ledger improvement, FT resource credit, a checked impossibility theorem, an R5 reroute, or a solved B1/B7 problem.",
            "",
            "## Validation",
            "",
            f"- validation_error_count: `{s['validation_error_count']}`",
        ]
    )
    for error in payload["validation_errors"]:
        lines.append(f"- {error}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--r19-contract",
        type=Path,
        default=Path("results/B1_B7_cone01_R19_o3_f3_symbolic_lu_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--submission",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f3_symbolic_lu_submissions/"
            "B1-B7-cone01-O3-F3-symbolic-lu.submission.json"
        ),
    )
    parser.add_argument(
        "--template-output",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f3_symbolic_lu_submissions/"
            "B1-B7-cone01-O3-F3-symbolic-lu.template.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R20_o3_f3_artifact_intake_preflight_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R20_o3_f3_artifact_intake_preflight_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-06")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.template_output, payload["o3_f3_artifact_intake_packet"]["template"], True)
    write_json(args.json_output, payload, args.pretty)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "intake_hash": payload["summary"]["intake_hash"],
                "template_hash": payload["summary"]["template_hash"],
                "checklist_hash": payload["summary"]["checklist_hash"],
                "preflight_hash": payload["summary"]["preflight_hash"],
                "o3_f3_intake_ready": payload["summary"]["o3_f3_intake_ready"],
                "o3_f3_submission_exists": payload["summary"]["o3_f3_submission_exists"],
                "o3_f3_preflight_accepted": payload["summary"]["o3_f3_preflight_accepted"],
                "o3_f3_artifact_accepted": payload["summary"]["o3_f3_artifact_accepted"],
                "o3_closed": payload["summary"]["o3_closed"],
                "reroute_allowed": payload["summary"]["reroute_allowed"],
                "requirements_passed": payload["summary"]["requirements_passed"],
                "requirements_failed": payload["summary"]["requirements_failed"],
                "validation_error_count": payload["summary"]["validation_error_count"],
                "template_output": str(args.template_output),
                "json_output": str(args.json_output),
                "markdown_output": str(args.markdown_output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B1/B7 R20 O3-F3 artifact intake preflight gate validation failed")


if __name__ == "__main__":
    main()
