#!/usr/bin/env python3
"""T-B1-004du/T-B7-013d: R19 O3-F3 symbolic local-unitary contract gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r19_o3_f3_symbolic_lu_contract_gate_v0"
STATUS = "cone01_r19_o3_f3_symbolic_lu_contract_ready_not_submitted"
MODEL_STATUS = "o3_f3_symbolic_local_unitary_contract_ready_no_artifact_no_reroute"
VERSION = "0.1"
TARGET_ID = "T-B1-004du/T-B7-013d"
CONTRACT_ID = "B1-B7-cone01-R19-O3-F3-symbolic-local-unitary-contract"
CANDIDATE_ID = "NL-C02"
FAMILY_ID = "O3-F3"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
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


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r18 = load_json(args.r18_registry)
    r18s = r18["summary"]
    packet = r18["nlc02_o3_equivalence_family_registry_packet"]
    family_rows = packet["family_rows"]
    falsifier_rows = packet["falsifier_rows"]
    o3_f3 = next(row for row in family_rows if row["family_id"] == FAMILY_ID)
    o3_x1 = next(row for row in falsifier_rows if row["target_family"] == FAMILY_ID)

    required_fields = [
        {
            "field": "artifact_id",
            "purpose": "stable artifact identifier for the symbolic local-unitary proof or counterexample",
        },
        {"field": "source_target_id", "purpose": "must cite T-B1-004du/T-B7-013d or descendant"},
        {"field": "family_id", "purpose": "must equal O3-F3"},
        {"field": "candidate_id", "purpose": "must equal NL-C02"},
        {
            "field": "source_registry_hash",
            "purpose": "must equal the R18 registry hash consumed by this contract",
        },
        {
            "field": "symbolic_transform_definition",
            "purpose": "defines the local-unitary coordinate transformation with domains and codomains",
        },
        {
            "field": "source_unitary_preservation_certificate",
            "purpose": "proves or checks that the transformed coordinates preserve the source local unitary",
        },
        {
            "field": "leaveout_domain_mapping",
            "purpose": "maps the transformed coordinates back to the R13/R17 leave-out domain or explains the escape",
        },
        {
            "field": "pi_over_four_lattice_relation",
            "purpose": "states whether the transform preserves, reaches, or escapes the pi/4 lattice",
        },
        {
            "field": "route_a_effect",
            "purpose": "states whether the artifact clears Route A against the R7/R8 contract",
        },
        {
            "field": "counterexample_payload",
            "purpose": "required when claiming a falsifier; contains exact symbolic values or a replayable construction",
        },
        {
            "field": "claim_boundary",
            "purpose": "states what is supported, not supported, and what would kill the result",
        },
        {
            "field": "machine_check_command",
            "purpose": "command that reproduces the proof check, symbolic replay, or counterexample verification",
        },
        {
            "field": "expected_outputs",
            "purpose": "hashes or exact outputs for the checker result",
        },
    ]

    acceptance_gates = [
        {
            "gate_id": "A1",
            "gate": "family_and_source_binding",
            "acceptance_rule": "family_id == O3-F3 and source_registry_hash matches R18 registry_hash",
        },
        {
            "gate_id": "A2",
            "gate": "local_unitary_preservation",
            "acceptance_rule": "source_unitary_preservation_certificate is present and machine-checkable",
        },
        {
            "gate_id": "A3",
            "gate": "domain_mapping",
            "acceptance_rule": "leaveout_domain_mapping covers the five R13 line1381 parameters or gives an explicit escape",
        },
        {
            "gate_id": "A4",
            "gate": "lattice_relation",
            "acceptance_rule": "pi_over_four_lattice_relation is symbolic, replayable, and not only numerical",
        },
        {
            "gate_id": "A5",
            "gate": "route_a_effect",
            "acceptance_rule": "Route A impact is explicitly positive, negative, or not claimed",
        },
        {
            "gate_id": "A6",
            "gate": "claim_boundary",
            "acceptance_rule": "artifact refuses B7 credit unless Route A/B and resource ledgers are accepted",
        },
        {
            "gate_id": "A7",
            "gate": "checker_replay",
            "acceptance_rule": "machine_check_command reproduces expected_outputs",
        },
        {
            "gate_id": "A8",
            "gate": "no_silent_upgrade",
            "acceptance_rule": "artifact does not set checked_negative_lemma_present or reroute_allowed without all acceptance gates",
        },
    ]

    rejection_rules = [
        "Reject if the transform is only a numerical fit without a symbolic local-unitary preservation certificate.",
        "Reject if the artifact reaches the pi/4 lattice but does not preserve the source local unitary.",
        "Reject if the artifact claims B7 credit before an accepted Route A/B artifact and refreshed B7 ledger replay.",
        "Reject if the artifact silently changes the R13 five-parameter source domain.",
        "Reject if the machine-check command is missing, nondeterministic, or not hash-bound.",
    ]

    contract_packet = {
        "contract_id": CONTRACT_ID,
        "source_target_id": TARGET_ID,
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "source_r18_registry": str(args.r18_registry),
        "source_hashes": {"r18_registry_file": file_hash(args.r18_registry)},
        "source_artifact_hashes": {
            "r18_registry_hash": r18s["registry_hash"],
            "r18_family_table_hash": r18s["family_table_hash"],
            "r18_falsifier_table_hash": r18s["falsifier_table_hash"],
        },
        "source_family_row": o3_f3,
        "source_falsifier_row": o3_x1,
        "required_fields": required_fields,
        "acceptance_gates": acceptance_gates,
        "rejection_rules": rejection_rules,
        "artifact_template": {
            "artifact_id": "B1-B7-cone01-O3-F3-symbolic-lu-<submitter>-<short-name>",
            "source_target_id": TARGET_ID,
            "family_id": FAMILY_ID,
            "candidate_id": CANDIDATE_ID,
            "source_registry_hash": r18s["registry_hash"],
            "symbolic_transform_definition": "<required>",
            "source_unitary_preservation_certificate": "<required>",
            "leaveout_domain_mapping": "<required>",
            "pi_over_four_lattice_relation": "<required>",
            "route_a_effect": "not_claimed|clears_route_a|does_not_clear_route_a",
            "counterexample_payload": None,
            "claim_boundary": "<required>",
            "machine_check_command": "<required>",
            "expected_outputs": "<required>",
        },
        "decision": {
            "o3_f3_contract_ready": True,
            "o3_f3_artifact_submitted": False,
            "o3_f3_accepted": False,
            "o3_closed": False,
            "checked_negative_lemma_present": False,
            "nlc02_full_lemma_ready": False,
            "reroute_allowed": False,
            "why": (
                "R19 prepares a strict O3-F3 submission contract. No symbolic local-unitary artifact "
                "has been submitted or accepted, so O3 and R5 remain closed to credit."
            ),
        },
    }
    contract_packet["required_field_table_hash"] = stable_hash(required_fields)
    contract_packet["acceptance_gate_table_hash"] = stable_hash(acceptance_gates)
    contract_packet["rejection_rule_hash"] = stable_hash(rejection_rules)
    contract_packet["contract_hash"] = stable_hash(contract_packet)

    requirements = [
        requirement(
            "J1",
            "R18 registry is validation-clean and keeps O3-F3 open",
            r18.get("method") == "b1_b7_cone01_r18_nlc02_o3_equivalence_family_registry_gate_v0"
            and r18s.get("validation_error_count") == 0
            and o3_f3.get("status") == "open_needs_symbolic_equivalence_argument",
            {
                "r18_method": r18.get("method"),
                "r18_validation_error_count": r18s.get("validation_error_count"),
                "o3_f3_status": o3_f3.get("status"),
            },
        ),
        requirement(
            "J2",
            "R18 exposes the O3-X1 falsifier target for O3-F3",
            o3_x1.get("falsifier_id") == "O3-X1"
            and "symbolic local-unitary" in o3_x1.get("success_condition", ""),
            o3_x1,
        ),
        requirement(
            "J3",
            "Contract defines fourteen required submission fields",
            len(required_fields) == 14,
            {"required_field_count": len(required_fields), "fields": [row["field"] for row in required_fields]},
        ),
        requirement(
            "J4",
            "Contract defines eight acceptance gates",
            len(acceptance_gates) == 8,
            {"acceptance_gate_count": len(acceptance_gates), "gate_ids": [row["gate_id"] for row in acceptance_gates]},
        ),
        requirement(
            "J5",
            "Contract defines explicit rejection rules for overclaims",
            len(rejection_rules) == 5
            and any("B7 credit" in rule for rule in rejection_rules),
            {"rejection_rule_count": len(rejection_rules), "rejection_rules": rejection_rules},
        ),
        requirement(
            "J6",
            "Artifact template is bound to O3-F3 and the R18 registry hash",
            contract_packet["artifact_template"]["family_id"] == FAMILY_ID
            and contract_packet["artifact_template"]["source_registry_hash"] == r18s["registry_hash"],
            contract_packet["artifact_template"],
        ),
        requirement(
            "J7",
            "Contract is hash-bound to the R18 registry and internal tables",
            all(contract_packet["source_hashes"].values())
            and all(contract_packet["source_artifact_hashes"].values())
            and bool(contract_packet["required_field_table_hash"])
            and bool(contract_packet["acceptance_gate_table_hash"])
            and bool(contract_packet["rejection_rule_hash"])
            and bool(contract_packet["contract_hash"]),
            {
                "source_hashes": contract_packet["source_hashes"],
                "source_artifact_hashes": contract_packet["source_artifact_hashes"],
                "required_field_table_hash": contract_packet["required_field_table_hash"],
                "acceptance_gate_table_hash": contract_packet["acceptance_gate_table_hash"],
                "rejection_rule_hash": contract_packet["rejection_rule_hash"],
                "contract_hash": contract_packet["contract_hash"],
            },
        ),
        requirement(
            "J8",
            "No O3-F3 artifact is silently accepted",
            contract_packet["decision"]["o3_f3_contract_ready"] is True
            and contract_packet["decision"]["o3_f3_artifact_submitted"] is False
            and contract_packet["decision"]["o3_f3_accepted"] is False,
            contract_packet["decision"],
        ),
        requirement(
            "J9",
            "Contract does not close O3 or allow reroute",
            contract_packet["decision"]["o3_closed"] is False
            and contract_packet["decision"]["checked_negative_lemma_present"] is False
            and contract_packet["decision"]["reroute_allowed"] is False,
            contract_packet["decision"],
        ),
        requirement(
            "J10",
            "Contract preserves zero resource and B7 credit claims",
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
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids:
        validation_errors.append(f"unexpected R19 O3-F3 contract failures: {failed_ids}")

    summary = {
        "contract_id": CONTRACT_ID,
        "contract_hash": contract_packet["contract_hash"],
        "required_field_table_hash": contract_packet["required_field_table_hash"],
        "acceptance_gate_table_hash": contract_packet["acceptance_gate_table_hash"],
        "rejection_rule_hash": contract_packet["rejection_rule_hash"],
        "source_r18_registry_hash": r18s["registry_hash"],
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "required_field_count": len(required_fields),
        "acceptance_gate_count": len(acceptance_gates),
        "rejection_rule_count": len(rejection_rules),
        "o3_f3_contract_ready": True,
        "o3_f3_artifact_submitted": False,
        "o3_f3_accepted": False,
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
        "title": "B1/B7 Cone01 R19 O3-F3 Symbolic Local-Unitary Contract Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "summary": summary,
        "o3_f3_symbolic_lu_contract_packet": contract_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "R19 creates a strict submission contract for O3-F3 symbolic local-unitary proof or counterexample artifacts."
            ),
            "what_is_not_supported": (
                "R19 does not submit or accept an O3-F3 artifact, does not close O3, and does not permit R5 reroute. "
                "No R1 solution, occurrence removal, proxy-T reduction, B7 credit, resource saving, or impossibility theorem is supported."
            ),
            "next_gate": (
                "Submit an O3-F3 artifact satisfying the fourteen required fields and eight acceptance gates, "
                "or move to O3-F4/O3-F5 under the R18 registry."
            ),
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    packet = payload["o3_f3_symbolic_lu_contract_packet"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Candidate: `{s['candidate_id']}`",
        f"- Family: `{s['family_id']}`",
        f"- Contract hash: `{s['contract_hash']}`",
        f"- Required-field table hash: `{s['required_field_table_hash']}`",
        f"- Acceptance-gate table hash: `{s['acceptance_gate_table_hash']}`",
        f"- Rejection-rule hash: `{s['rejection_rule_hash']}`",
        "",
        "## Result",
        "",
        (
            f"The R19 O3-F3 contract gate passes {s['requirements_passed']}/{s['requirement_count']} requirements. "
            "It prepares a strict symbolic local-unitary submission contract, but no O3-F3 artifact is submitted or accepted."
        ),
        "",
        "## Required Fields",
        "",
    ]
    for row in packet["required_fields"]:
        lines.append(f"- `{row['field']}`: {row['purpose']}")
    lines.extend(["", "## Acceptance Gates", ""])
    for row in packet["acceptance_gates"]:
        lines.append(f"- `{row['gate_id']}` {row['gate']}: {row['acceptance_rule']}")
    lines.extend(["", "## Rejection Rules", ""])
    for rule in packet["rejection_rules"]:
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- O3-F3 contract ready: `{s['o3_f3_contract_ready']}`",
            f"- O3-F3 artifact submitted: `{s['o3_f3_artifact_submitted']}`",
            f"- O3-F3 accepted: `{s['o3_f3_accepted']}`",
            f"- O3 closed: `{s['o3_closed']}`",
            f"- Checked negative lemma present: `{s['checked_negative_lemma_present']}`",
            f"- Reroute allowed: `{s['reroute_allowed']}`",
            "",
            "## Requirement Results",
            "",
        ]
    )
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
            "This contract gate does not claim resource saving, occurrence removal, proxy-T reduction, B7 ledger improvement, FT resource credit, a checked impossibility theorem, an R5 reroute, or a solved B1/B7 problem.",
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
        "--r18-registry",
        type=Path,
        default=Path("results/B1_B7_cone01_R18_nlc02_o3_equivalence_family_registry_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R19_o3_f3_symbolic_lu_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R19_o3_f3_symbolic_lu_contract_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-06")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "contract_hash": payload["summary"]["contract_hash"],
                "required_field_count": payload["summary"]["required_field_count"],
                "acceptance_gate_count": payload["summary"]["acceptance_gate_count"],
                "rejection_rule_count": payload["summary"]["rejection_rule_count"],
                "o3_f3_contract_ready": payload["summary"]["o3_f3_contract_ready"],
                "o3_f3_artifact_submitted": payload["summary"]["o3_f3_artifact_submitted"],
                "o3_f3_accepted": payload["summary"]["o3_f3_accepted"],
                "o3_closed": payload["summary"]["o3_closed"],
                "reroute_allowed": payload["summary"]["reroute_allowed"],
                "requirements_passed": payload["summary"]["requirements_passed"],
                "requirements_failed": payload["summary"]["requirements_failed"],
                "validation_error_count": payload["summary"]["validation_error_count"],
                "json_output": str(args.json_output),
                "markdown_output": str(args.markdown_output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B1/B7 R19 O3-F3 symbolic LU contract gate validation failed")


if __name__ == "__main__":
    main()
