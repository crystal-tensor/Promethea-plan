#!/usr/bin/env python3
"""Build symbolic-obligation intake packets for the open B7 w8_21 route."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b7_w8_21_symbolic_obligation_intake_gate_v0"
STATUS = "w8_21_symbolic_obligation_intake_open_no_rewrite_certificate"
MODEL_STATUS = "w8_21_numeric_failures_mapped_to_symbolic_or_rewrite_pr_packets"
VERSION = "0.1"
EXPECTED_FAILED_IDS = ["S5", "S6", "S7"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def stable_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def obligation(
    packet_id: str,
    owner_role: str,
    acceptance_rule: str,
    required_artifacts: list[str],
    current_evidence: dict[str, Any],
) -> dict[str, Any]:
    row = {
        "packet_id": packet_id,
        "owner_role": owner_role,
        "acceptance_rule": acceptance_rule,
        "required_artifacts": required_artifacts,
        "current_evidence": current_evidence,
        "submitted_artifact_present": False,
        "accepted_certificate": False,
        "ready_for_b7_ledger_retest": False,
    }
    row["packet_hash"] = stable_hash(
        {
            "packet_id": packet_id,
            "acceptance_rule": acceptance_rule,
            "required_artifacts": required_artifacts,
        }
    )
    return row


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    priority = load_json(args.template_priority)
    three_cnot = load_json(args.three_cnot_search)
    priority_summary = priority["summary"]

    best_template = next(
        row for row in priority["template_priority_rows"] if row["template_id"] == "w8_21"
    )
    obligations = [
        obligation(
            "B7-S1-w8-21-symbolic-kak-obstruction",
            "theory_agent",
            "Provide a symbolic KAK/local-invariant obstruction or exact constructive certificate for the w8_21 two-qubit target family.",
            [
                "normalized two-qubit target matrix for w8_21",
                "symbolic local-invariant or KAK coordinates",
                "statement separating tested local/Euler scaffolds from untested global routes",
                "machine-readable theorem or reproducible algebra notebook",
            ],
            {
                "template_id": "w8_21",
                "prior_exact_rewrite_found": priority_summary["w8_21_prior_exact_rewrite_found"],
                "prior_optimizer_runs": priority_summary["w8_21_prior_optimizer_runs"],
            },
        ),
        obligation(
            "B7-S2-occurrence-removing-rewrite-certificate",
            "compiler_agent",
            "Submit at least 30 occurrence-removing certificates or 20 w8_21 occurrence certificates removing at least 2 arbitrary rotations per occurrence.",
            [
                "source occurrence ids and line spans",
                "replacement OpenQASM 3 snippets",
                "statevector or unitary replay certificates",
                "resource delta showing removed arbitrary rotations under the current B7 ledger",
            ],
            {
                "target_removed_arbitrary_occurrences": priority_summary[
                    "target_removed_arbitrary_occurrences_for_gcm_h6_1_20"
                ],
                "w8_21_nonoverlap_occurrences": best_template["nonoverlap_occurrences"],
                "required_arbitrary_removed_per_occurrence": best_template[
                    "required_arbitrary_removed_per_occurrence_for_gcm_h6_1_20"
                ],
                "accepted_occurrence_reduction": 0,
            },
        ),
        obligation(
            "B7-S3-ledger-retest-after-certificate",
            "ft_ledger_agent",
            "Rerun the B7 ledger after accepted certificates and prove the gcm_h6 one-sided 1.20x target without cache-only or unpriced-local-rotation credit.",
            [
                "updated arbitrary-rotation ledger",
                "proxy-T or physical synthesis pricing table",
                "min-STV retest for gcm_h6",
                "claim-boundary note forbidding cache-only credit",
            ],
            {
                "target_removed_t_ledger": priority_summary[
                    "target_removed_t_ledger_for_gcm_h6_1_20"
                ],
                "one_angle_clear_count": priority_summary["single_template_one_angle_clear_count"],
                "physical_resource_reduction_claimed": priority["claim_boundary"][
                    "physical_resource_reduction_claimed"
                ],
            },
        ),
    ]

    submitted = sum(row["submitted_artifact_present"] for row in obligations)
    accepted = sum(row["accepted_certificate"] for row in obligations)
    ready = sum(row["ready_for_b7_ledger_retest"] for row in obligations)

    requirements = [
        requirement(
            "S1",
            "Template priority gate selects w8_21 and keeps resource claims false",
            priority.get("method") == "b7_template_priority_gate_v0"
            and priority_summary["best_template_id"] == "w8_21"
            and priority["claim_boundary"]["physical_resource_reduction_claimed"] is False,
            {
                "source_method": priority.get("method"),
                "best_template_id": priority_summary["best_template_id"],
                "physical_resource_reduction_claimed": priority["claim_boundary"][
                    "physical_resource_reduction_claimed"
                ],
            },
        ),
        requirement(
            "S2",
            "w8_21 still needs two arbitrary removals per occurrence",
            best_template["required_arbitrary_removed_per_occurrence_for_gcm_h6_1_20"] == 2
            and best_template["nonoverlap_occurrences"] == 20,
            {
                "nonoverlap_occurrences": best_template["nonoverlap_occurrences"],
                "required_arbitrary_removed_per_occurrence": best_template[
                    "required_arbitrary_removed_per_occurrence_for_gcm_h6_1_20"
                ],
                "one_arbitrary_removed_t_ledger": best_template["one_arbitrary_removed_t_ledger"],
            },
        ),
        requirement(
            "S3",
            "Three-CNOT numerical search remains negative and non-promotional",
            three_cnot.get("method") == "b7_w8_21_three_cnot_search_v0"
            and three_cnot.get("passing_candidate_count") == 0
            and three_cnot["claim_boundary"][
                "three_cnot_four_rotation_search_found_exact_candidate"
            ]
            is False,
            {
                "source_method": three_cnot.get("method"),
                "attempted_optimizer_runs": three_cnot.get("attempted_optimizer_runs"),
                "passing_candidate_count": three_cnot.get("passing_candidate_count"),
                "best_residual_norm": three_cnot["best_candidate"]["residual_norm"],
            },
        ),
        requirement(
            "S4",
            "Symbolic/rewrite obligation packets are explicit",
            len(obligations) == 3 and bool(stable_hash(obligations)),
            {
                "packet_count": len(obligations),
                "packet_ids": [row["packet_id"] for row in obligations],
                "packet_table_hash": stable_hash(obligations),
            },
        ),
        requirement(
            "S5",
            "Submitted symbolic or rewrite artifacts exist",
            submitted > 0,
            {"submitted_artifact_count": submitted},
        ),
        requirement(
            "S6",
            "Accepted occurrence-removing or obstruction certificates exist",
            accepted > 0,
            {"accepted_certificate_count": accepted},
        ),
        requirement(
            "S7",
            "B7 ledger retest is ready",
            ready == len(obligations),
            {"ready_packet_count": ready, "required_packet_count": len(obligations)},
        ),
        requirement(
            "S8",
            "Forbidden rewrite, lower-bound, and resource claims remain false",
            all(
                priority["claim_boundary"].get(key) is False
                for key in [
                    "new_rewrite_claimed",
                    "global_lower_bound_claimed",
                    "physical_resource_reduction_claimed",
                ]
            )
            and three_cnot["claim_boundary"]["global_two_qubit_lower_bound_claimed"] is False,
            {
                "new_rewrite_claimed": priority["claim_boundary"].get("new_rewrite_claimed"),
                "global_lower_bound_claimed": priority["claim_boundary"].get(
                    "global_lower_bound_claimed"
                ),
                "physical_resource_reduction_claimed": priority["claim_boundary"].get(
                    "physical_resource_reduction_claimed"
                ),
                "global_two_qubit_lower_bound_claimed": three_cnot["claim_boundary"][
                    "global_two_qubit_lower_bound_claimed"
                ],
            },
        ),
    ]

    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected symbolic obligation failures: {failed_ids}")
    if submitted != 0 or accepted != 0 or ready != 0:
        validation_errors.append("intake gate must not fabricate proof or rewrite certificates")

    summary = {
        "source_template_priority_status": priority.get("status"),
        "source_three_cnot_status": three_cnot.get("status"),
        "intake_requirement_count": len(requirements),
        "intake_requirements_passed": passed,
        "intake_requirements_failed": len(requirements) - passed,
        "failed_intake_requirement_ids": failed_ids,
        "packet_count": len(obligations),
        "packet_ids": [row["packet_id"] for row in obligations],
        "packet_table_hash": stable_hash(obligations),
        "best_template_id": priority_summary["best_template_id"],
        "w8_21_nonoverlap_occurrences": best_template["nonoverlap_occurrences"],
        "required_arbitrary_removed_per_occurrence": best_template[
            "required_arbitrary_removed_per_occurrence_for_gcm_h6_1_20"
        ],
        "target_removed_arbitrary_occurrences": priority_summary[
            "target_removed_arbitrary_occurrences_for_gcm_h6_1_20"
        ],
        "target_removed_t_ledger": priority_summary["target_removed_t_ledger_for_gcm_h6_1_20"],
        "prior_optimizer_runs": priority_summary["w8_21_prior_optimizer_runs"],
        "three_cnot_attempted_optimizer_runs": three_cnot["attempted_optimizer_runs"],
        "three_cnot_passing_candidate_count": three_cnot["passing_candidate_count"],
        "submitted_artifact_count": submitted,
        "accepted_certificate_count": accepted,
        "ready_for_b7_ledger_retest_count": ready,
        "new_rewrite_claimed": False,
        "global_lower_bound_claimed": False,
        "physical_resource_reduction_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B7",
        "linked_benchmark_id": "B1",
        "problem_id": 21,
        "title": "B7 w8_21 Symbolic Obligation Intake Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_template_priority_result": str(args.template_priority),
        "source_three_cnot_search_result": str(args.three_cnot_search),
        "summary": summary,
        "requirements": requirements,
        "obligation_packets": obligations,
        "claim_boundary": {
            "what_is_supported": (
                "The open w8_21 route is converted into symbolic KAK, occurrence-removing "
                "rewrite, and B7 ledger-retest obligation packets."
            ),
            "what_is_not_supported": (
                "No symbolic obstruction, exact rewrite, resource reduction, global lower "
                "bound, or B7 ledger improvement is established."
            ),
            "next_gate": (
                "Submit an accepted symbolic certificate or occurrence-removing rewrite, then "
                "rerun the B7 ledger before counting any gcm_h6 1.20x resource credit."
            ),
            "new_rewrite_claimed": False,
            "global_lower_bound_claimed": False,
            "physical_resource_reduction_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# B7 w8_21 Symbolic Obligation Intake Gate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Intake requirements passed/failed: {summary['intake_requirements_passed']} / {summary['intake_requirements_failed']}",
        f"- Failed intake requirement IDs: {summary['failed_intake_requirement_ids']}",
        f"- Best template: {summary['best_template_id']}",
        f"- Nonoverlap occurrences: {summary['w8_21_nonoverlap_occurrences']}",
        f"- Required arbitrary removals per occurrence: {summary['required_arbitrary_removed_per_occurrence']}",
        f"- Target removed arbitrary occurrences / proxy-T: {summary['target_removed_arbitrary_occurrences']} / {summary['target_removed_t_ledger']}",
        f"- Prior optimizer runs: {summary['prior_optimizer_runs']}",
        f"- Three-CNOT passing candidates: {summary['three_cnot_passing_candidate_count']}",
        "",
        "## Obligation Packets",
        "",
        "| Packet | Owner | Submitted | Accepted | Ledger retest ready |",
        "|---|---|---|---|---|",
    ]
    for row in payload["obligation_packets"]:
        lines.append(
            f"| {row['packet_id']} | {row['owner_role']} | {row['submitted_artifact_present']} | "
            f"{row['accepted_certificate']} | {row['ready_for_b7_ledger_retest']} |"
        )
    lines.extend(["", "## Requirement Results", ""])
    for row in payload["requirements"]:
        status = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- {row['requirement_id']} [{status}]: {row['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            f"- new_rewrite_claimed: {payload['claim_boundary']['new_rewrite_claimed']}",
            f"- global_lower_bound_claimed: {payload['claim_boundary']['global_lower_bound_claimed']}",
            f"- physical_resource_reduction_claimed: {payload['claim_boundary']['physical_resource_reduction_claimed']}",
            "",
            "## Validation",
            "",
            f"- validation_error_count: {summary['validation_error_count']}",
        ]
    )
    if payload["validation_errors"]:
        for error in payload["validation_errors"]:
            lines.append(f"- {error}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--template-priority",
        type=Path,
        default=Path("results/B7_template_priority_gate_v0.json"),
    )
    parser.add_argument(
        "--three-cnot-search",
        type=Path,
        default=Path("results/B7_w8_21_three_cnot_search_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B7_w8_21_symbolic_obligation_intake_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B7_w8_21_symbolic_obligation_intake_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-01")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, pretty=args.pretty)
    write_markdown(payload, args.markdown_output)
    print(json.dumps(payload["summary"], indent=2 if args.pretty else None, sort_keys=True))
    if payload["validation_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
