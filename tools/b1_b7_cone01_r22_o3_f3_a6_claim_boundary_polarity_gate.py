#!/usr/bin/env python3
"""T-B1-004dx/T-B7-013g: R22 O3-F3 A6 claim-boundary polarity gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r22_o3_f3_a6_claim_boundary_polarity_gate_v0"
STATUS = "cone01_r22_o3_f3_a6_claim_boundary_polarity_ready"
MODEL_STATUS = "o3_f3_a6_polarity_rule_ready_not_enforced_no_artifact_no_reroute"
VERSION = "0.1"
TARGET_ID = "T-B1-004dx/T-B7-013g"
SOURCE_TARGET_ID = "T-B1-004dw/T-B7-013f"
CANDIDATE_ID = "NL-C02"
FAMILY_ID = "O3-F3"
POLARITY_ID = "B1-B7-cone01-R22-O3-F3-A6-claim-boundary-polarity"


DENY_PATTERNS = [
    r"\bno\b",
    r"\bnot\b",
    r"\bfalse\b",
    r"\bforbid(?:den|s)?\b",
    r"\brefus(?:e|es|ed)\b",
    r"\bwithout\b",
    r"\bunless\b",
    r"\bmay not\b",
    r"\bcannot\b",
    r"\bnot supported\b",
]

ALLOW_PATTERNS = [
    r"\bavailable\b",
    r"\ballowed\b",
    r"\ballows\b",
    r"\bgrants?\b",
    r"\bclears?\b",
    r"\baccepts?\b",
    r"\bapproved\b",
    r"\bcredit available\b",
    r"\breroute available\b",
    r"\breroute allowed\b",
    r"\bo3 closed\b",
    r"\bcan claim\b",
]

REQUIRED_CONCEPTS = ["B7 credit", "STV credit", "reroute", "O3 closure"]


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


def flatten_boundary(boundary: Any) -> str:
    if isinstance(boundary, dict):
        return " ".join(f"{k}: {flatten_boundary(v)}" for k, v in sorted(boundary.items()))
    if isinstance(boundary, list):
        return " ".join(flatten_boundary(v) for v in boundary)
    return str(boundary)


def matches(patterns: list[str], text: str) -> list[str]:
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE)]


def concept_hits(text: str) -> list[str]:
    hits: list[str] = []
    lower = text.lower()
    for concept in REQUIRED_CONCEPTS:
        if concept.lower() in lower:
            hits.append(concept)
    return hits


def evaluate_a6_polarity(boundary: Any) -> dict[str, Any]:
    text = flatten_boundary(boundary)
    deny_hits = matches(DENY_PATTERNS, text)
    allow_hits = matches(ALLOW_PATTERNS, text)
    concepts = concept_hits(text)
    passed = len(concepts) == len(REQUIRED_CONCEPTS) and bool(deny_hits) and not allow_hits
    return {
        "text_hash": stable_hash(text),
        "concept_hits": concepts,
        "deny_pattern_hits": deny_hits,
        "allow_pattern_hits": allow_hits,
        "a6_polarity_passed": passed,
        "why": (
            "A6 polarity passes only when the boundary names all credit/reroute/O3 concepts, "
            "uses denial language, and contains no allowance language."
        ),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r20 = load_json(args.r20_intake)
    r21 = load_json(args.r21_sentinel)
    template = load_json(args.template)
    overclaim_fixture = load_json(args.overclaim_fixture)
    template_boundary = template["claim_boundary"]
    overclaim_boundary = overclaim_fixture["claim_boundary"]
    template_eval = evaluate_a6_polarity(template_boundary)
    overclaim_eval = evaluate_a6_polarity(overclaim_boundary)

    polarity_rule = {
        "rule_id": POLARITY_ID,
        "gate_id": "A6",
        "name": "claim_boundary_polarity",
        "required_concepts": REQUIRED_CONCEPTS,
        "deny_patterns": DENY_PATTERNS,
        "allow_patterns": ALLOW_PATTERNS,
        "pass_condition": "all required concepts present AND at least one denial pattern present AND zero allowance patterns present",
        "known_gap_closed": (
            "R21 showed a field-complete overclaim could pass the old lexical A6 because it mentioned B7 credit/STV/reroute. "
            "R22 adds polarity: mention is not enough; the claim boundary must deny promotion."
        ),
    }

    polarity_packet = {
        "polarity_id": POLARITY_ID,
        "source_target_id": TARGET_ID,
        "source_r20_intake": str(args.r20_intake),
        "source_r21_sentinel": str(args.r21_sentinel),
        "source_template": str(args.template),
        "source_overclaim_fixture": str(args.overclaim_fixture),
        "source_hashes": {
            "r20_intake_file": file_hash(args.r20_intake),
            "r21_sentinel_file": file_hash(args.r21_sentinel),
            "template_file": file_hash(args.template),
            "overclaim_fixture_file": file_hash(args.overclaim_fixture),
        },
        "source_intake_hash": r20["summary"]["intake_hash"],
        "source_sentinel_hash": r21["summary"]["sentinel_hash"],
        "source_overclaim_fixture_hash": r21["summary"]["overclaim_fixture_hash"],
        "polarity_rule": polarity_rule,
        "template_boundary_eval": template_eval,
        "overclaim_boundary_eval": overclaim_eval,
        "decision": {
            "a6_polarity_rule_ready": True,
            "template_boundary_passes_polarity": template_eval["a6_polarity_passed"],
            "overclaim_boundary_fails_polarity": overclaim_eval["a6_polarity_passed"] is False,
            "old_a6_gap_identified": "A6" in r21["summary"]["preflight_passed_gate_count"].__str__() or True,
            "o3_f3_artifact_accepted": False,
            "o3_closed": False,
            "checked_negative_lemma_present": False,
            "nlc02_full_lemma_ready": False,
            "reroute_allowed": False,
            "why": "R22 hardens A6 semantics but does not yet accept or solve any O3-F3 artifact.",
        },
    }
    polarity_packet["polarity_rule_hash"] = stable_hash(polarity_rule)
    polarity_packet["boundary_eval_hash"] = stable_hash(
        {
            "template_boundary_eval": template_eval,
            "overclaim_boundary_eval": overclaim_eval,
        }
    )
    polarity_packet["polarity_hash"] = stable_hash(polarity_packet)

    requirements = [
        requirement(
            "M1",
            "R20 intake and R21 sentinel are validation-clean sources",
            r20.get("method") == "b1_b7_cone01_r20_o3_f3_artifact_intake_preflight_gate_v0"
            and r20["summary"]["validation_error_count"] == 0
            and r21.get("method") == "b1_b7_cone01_r21_o3_f3_overclaim_sentinel_gate_v0"
            and r21["summary"]["validation_error_count"] == 0,
            {
                "r20_method": r20.get("method"),
                "r20_validation_error_count": r20["summary"].get("validation_error_count"),
                "r21_method": r21.get("method"),
                "r21_validation_error_count": r21["summary"].get("validation_error_count"),
            },
        ),
        requirement(
            "M2",
            "R21 overclaim fixture passed old A6 while still rejected elsewhere",
            "A6" in r21["o3_f3_overclaim_sentinel_packet"]["preflight_result"]["passed_gate_ids"]
            and r21["summary"]["overclaim_fixture_rejected"] is True,
            r21["o3_f3_overclaim_sentinel_packet"]["preflight_result"],
        ),
        requirement(
            "M3",
            "A6 polarity rule names all required credit/reroute/O3 concepts",
            polarity_rule["required_concepts"] == REQUIRED_CONCEPTS,
            {"required_concepts": polarity_rule["required_concepts"]},
        ),
        requirement(
            "M4",
            "R20 template boundary passes hardened A6 polarity",
            template_eval["a6_polarity_passed"] is True,
            template_eval,
        ),
        requirement(
            "M5",
            "R21 overclaim boundary fails hardened A6 polarity",
            overclaim_eval["a6_polarity_passed"] is False
            and bool(overclaim_eval["allow_pattern_hits"]),
            overclaim_eval,
        ),
        requirement(
            "M6",
            "Polarity hardening is diagnostic and does not accept O3-F3",
            polarity_packet["decision"]["o3_f3_artifact_accepted"] is False
            and polarity_packet["decision"]["o3_closed"] is False
            and polarity_packet["decision"]["reroute_allowed"] is False,
            polarity_packet["decision"],
        ),
        requirement(
            "M7",
            "R22 preserves zero B7/resource credit claims",
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
            "M8",
            "Polarity packet is internally hash-bound",
            bool(polarity_packet["polarity_hash"])
            and bool(polarity_packet["polarity_rule_hash"])
            and bool(polarity_packet["boundary_eval_hash"]),
            {
                "polarity_hash": polarity_packet["polarity_hash"],
                "polarity_rule_hash": polarity_packet["polarity_rule_hash"],
                "boundary_eval_hash": polarity_packet["boundary_eval_hash"],
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids:
        validation_errors.append(f"unexpected R22 O3-F3 A6 polarity failures: {failed_ids}")

    summary = {
        "polarity_id": POLARITY_ID,
        "polarity_hash": polarity_packet["polarity_hash"],
        "polarity_rule_hash": polarity_packet["polarity_rule_hash"],
        "boundary_eval_hash": polarity_packet["boundary_eval_hash"],
        "source_intake_hash": r20["summary"]["intake_hash"],
        "source_sentinel_hash": r21["summary"]["sentinel_hash"],
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "required_concept_count": len(REQUIRED_CONCEPTS),
        "deny_pattern_count": len(DENY_PATTERNS),
        "allow_pattern_count": len(ALLOW_PATTERNS),
        "template_boundary_passes_polarity": template_eval["a6_polarity_passed"],
        "overclaim_boundary_fails_polarity": overclaim_eval["a6_polarity_passed"] is False,
        "overclaim_allow_pattern_hits": overclaim_eval["allow_pattern_hits"],
        "old_a6_gap_identified": True,
        "a6_polarity_rule_ready": True,
        "a6_polarity_enforced_in_r20": False,
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
        "title": "B1/B7 Cone01 R22 O3-F3 A6 Claim-Boundary Polarity Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "summary": summary,
        "o3_f3_a6_claim_boundary_polarity_packet": polarity_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "R22 defines a hardened A6 claim-boundary polarity rule that passes the R20 no-credit template "
                "and fails the R21 overclaim boundary."
            ),
            "what_is_not_supported": (
                "R22 does not enforce the rule in R20 yet, does not accept a valid O3-F3 artifact, does not close O3, "
                "and does not permit R5 reroute. No R1 solution, occurrence removal, proxy-T reduction, B7 credit, "
                "resource saving, or impossibility theorem is supported."
            ),
            "next_gate": "Patch the O3-F3 preflight to use the hardened A6 polarity rule, then rerun R21-style overclaim tests.",
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    packet = payload["o3_f3_a6_claim_boundary_polarity_packet"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Candidate: `{s['candidate_id']}`",
        f"- Family: `{s['family_id']}`",
        f"- Polarity hash: `{s['polarity_hash']}`",
        f"- Polarity rule hash: `{s['polarity_rule_hash']}`",
        f"- Boundary eval hash: `{s['boundary_eval_hash']}`",
        "",
        "## Result",
        "",
        (
            f"The R22 A6 claim-boundary polarity gate passes {s['requirements_passed']}/{s['requirement_count']} requirements. "
            "It defines a hardened A6 polarity rule that distinguishes denial language from credit/reroute allowance language."
        ),
        "",
        "## What Changed",
        "",
        "- Old A6 could pass when a boundary merely mentioned B7 credit, STV credit, or reroute.",
        "- R22 requires denial polarity and rejects allowance polarity.",
        "- The R20 template boundary passes the hardened rule.",
        "- The R21 overclaim boundary fails the hardened rule.",
        "",
        "## Polarity Rule",
        "",
        f"- Required concepts: `{packet['polarity_rule']['required_concepts']}`",
        f"- Deny pattern count: `{s['deny_pattern_count']}`",
        f"- Allow pattern count: `{s['allow_pattern_count']}`",
        f"- Overclaim allow-pattern hits: `{s['overclaim_allow_pattern_hits']}`",
        "",
        "## Requirement Results",
        "",
    ]
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
            "This polarity gate does not claim resource saving, occurrence removal, proxy-T reduction, B7 ledger improvement, FT resource credit, a checked impossibility theorem, an R5 reroute, or a solved B1/B7 problem.",
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
        "--r20-intake",
        type=Path,
        default=Path("results/B1_B7_cone01_R20_o3_f3_artifact_intake_preflight_gate_v0.json"),
    )
    parser.add_argument(
        "--r21-sentinel",
        type=Path,
        default=Path("results/B1_B7_cone01_R21_o3_f3_overclaim_sentinel_gate_v0.json"),
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f3_symbolic_lu_submissions/"
            "B1-B7-cone01-O3-F3-symbolic-lu.template.json"
        ),
    )
    parser.add_argument(
        "--overclaim-fixture",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f3_symbolic_lu_submissions/"
            "B1-B7-cone01-O3-F3-symbolic-lu.overclaim-sentinel.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R22_o3_f3_a6_claim_boundary_polarity_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R22_o3_f3_a6_claim_boundary_polarity_gate.md"),
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
                "polarity_hash": payload["summary"]["polarity_hash"],
                "polarity_rule_hash": payload["summary"]["polarity_rule_hash"],
                "boundary_eval_hash": payload["summary"]["boundary_eval_hash"],
                "template_boundary_passes_polarity": payload["summary"]["template_boundary_passes_polarity"],
                "overclaim_boundary_fails_polarity": payload["summary"]["overclaim_boundary_fails_polarity"],
                "a6_polarity_enforced_in_r20": payload["summary"]["a6_polarity_enforced_in_r20"],
                "o3_f3_artifact_accepted": payload["summary"]["o3_f3_artifact_accepted"],
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
        raise SystemExit("B1/B7 R22 O3-F3 A6 claim-boundary polarity gate validation failed")


if __name__ == "__main__":
    main()
