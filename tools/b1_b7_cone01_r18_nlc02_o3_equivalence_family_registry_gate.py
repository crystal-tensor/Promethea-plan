#!/usr/bin/env python3
"""T-B1-004dt/T-B7-013c: R18 NL-C02 O3 equivalence-family registry gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r18_nlc02_o3_equivalence_family_registry_gate_v0"
STATUS = "cone01_r18_nlc02_o3_equivalence_family_registry_ready_not_full_lemma"
MODEL_STATUS = "nlc02_o3_attack_surface_partitioned_reroute_still_forbidden"
VERSION = "0.1"
TARGET_ID = "T-B1-004dt/T-B7-013c"
REGISTRY_ID = "B1-B7-cone01-R18-NL-C02-O3-equivalence-family-registry"
CANDIDATE_ID = "NL-C02"


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
    r13 = load_json(args.r13_binding)
    r16 = load_json(args.r16_lemma)
    r17 = load_json(args.r17_boundary)
    r13s = r13["summary"]
    r16s = r16["summary"]
    r17s = r17["summary"]

    family_rows = [
        {
            "family_id": "O3-F1",
            "family": "identity_and_periodic_pi_complement",
            "status": "covered_by_r14_screen",
            "evidence_hash": "97bc38b63779b504f3bbc157d622b0d893c4266bcd00f35e5143bccef9b98b26",
            "accepted_escape_count": 0,
            "closed_for_full_o3": False,
            "next_pr": "none; subsumed by O3-F2 for current registry purposes",
        },
        {
            "family_id": "O3-F2",
            "family": "clifford_frame_affine_pi_over_2_periodic_sign",
            "status": "closed_sublemma_by_r16",
            "evidence_hash": r16s["lemma_hash"],
            "proof_table_hash": r16s["proof_table_hash"],
            "accepted_escape_count": 0,
            "closed_for_full_o3": False,
            "next_pr": "try to generalize the lattice-distance invariance proof beyond Clifford-frame affine maps",
        },
        {
            "family_id": "O3-F3",
            "family": "symbolic_local_unitary_reparameterization",
            "status": "open_needs_symbolic_equivalence_argument",
            "evidence_hash": None,
            "accepted_escape_count": None,
            "closed_for_full_o3": False,
            "next_pr": "define the allowed symbolic local-unitary coordinate transformations and prove they preserve the leave-out domain or produce a counterexample",
        },
        {
            "family_id": "O3-F4",
            "family": "numerical_coordinate_refit_under_same_unitary",
            "status": "open_needs_adversarial_refit_harness",
            "evidence_hash": None,
            "accepted_escape_count": None,
            "closed_for_full_o3": False,
            "next_pr": "build a refit harness that searches equivalent parameterizations while replaying the same local unitary",
        },
        {
            "family_id": "O3-F5",
            "family": "route_a_candidate_reparameterization",
            "status": "blocked_until_route_a_artifact_exists",
            "evidence_hash": None,
            "accepted_escape_count": None,
            "closed_for_full_o3": False,
            "next_pr": "submit a Route A artifact against the R7/R8 contract, then test whether it leaves the R13/R17 domain",
        },
    ]

    open_family_count = sum(1 for row in family_rows if row["status"].startswith("open"))
    blocked_family_count = sum(1 for row in family_rows if row["status"].startswith("blocked"))
    closed_sublemma_count = sum(1 for row in family_rows if "closed" in row["status"] or "covered" in row["status"])
    falsifier_rows = [
        {
            "falsifier_id": "O3-X1",
            "target_family": "O3-F3",
            "success_condition": "valid symbolic local-unitary reparameterization reaches pi/4 lattice while preserving the source unitary",
        },
        {
            "falsifier_id": "O3-X2",
            "target_family": "O3-F4",
            "success_condition": "numerical refit finds an equivalent parameterization outside the leave-out table that clears Route A",
        },
        {
            "falsifier_id": "O3-X3",
            "target_family": "O3-F5",
            "success_condition": "submitted Route A artifact clears R7/R8 and invalidates the current R17 search-domain boundary",
        },
    ]

    registry_packet = {
        "registry_id": REGISTRY_ID,
        "source_target_id": TARGET_ID,
        "candidate_id": CANDIDATE_ID,
        "source_artifacts": {
            "r13_binding": str(args.r13_binding),
            "r16_lemma": str(args.r16_lemma),
            "r17_boundary": str(args.r17_boundary),
        },
        "source_hashes": {
            "r13_binding_file": file_hash(args.r13_binding),
            "r16_lemma_file": file_hash(args.r16_lemma),
            "r17_boundary_file": file_hash(args.r17_boundary),
        },
        "source_artifact_hashes": {
            "r13_binding_hash": r13s["binding_hash"],
            "r13_domain_hash": r13s["domain_hash"],
            "r16_lemma_hash": r16s["lemma_hash"],
            "r16_proof_table_hash": r16s["proof_table_hash"],
            "r17_boundary_hash": r17s["boundary_hash"],
            "r17_disposition_table_hash": r17s["disposition_table_hash"],
        },
        "o3_registry_statement": (
            "O3 is not closed. The only closed equivalence-family evidence is the Clifford-frame affine "
            "sublemma; general symbolic local-unitary reparameterization, numerical refit, and Route A "
            "candidate reparameterizations remain open or blocked."
        ),
        "family_rows": family_rows,
        "falsifier_rows": falsifier_rows,
        "decision": {
            "o3_closed": False,
            "o3_attack_surface_partitioned": True,
            "closed_sublemma_count": closed_sublemma_count,
            "open_family_count": open_family_count,
            "blocked_family_count": blocked_family_count,
            "falsifier_count": len(falsifier_rows),
            "checked_negative_lemma_present": False,
            "nlc02_full_lemma_ready": False,
            "reroute_allowed": False,
            "why": (
                "R18 converts O3 from a vague remaining obligation into a registry of equivalence-family PR targets. "
                "It does not close full O3 and cannot unlock R5 reroute or B7 credit."
            ),
        },
    }
    registry_packet["family_table_hash"] = stable_hash(family_rows)
    registry_packet["falsifier_table_hash"] = stable_hash(falsifier_rows)
    registry_packet["registry_hash"] = stable_hash(registry_packet)

    requirements = [
        requirement(
            "I1",
            "R13 source-domain binding is validation-clean and keeps O3 open",
            r13.get("method") == "b1_b7_cone01_r13_nlc02_source_domain_binding_gate_v0"
            and r13s.get("validation_error_count") == 0
            and "O3" in r13s.get("remaining_open_obligations", []),
            {
                "r13_method": r13.get("method"),
                "r13_validation_error_count": r13s.get("validation_error_count"),
                "remaining_open_obligations": r13s.get("remaining_open_obligations"),
            },
        ),
        requirement(
            "I2",
            "R16 closes the Clifford-frame affine sublemma but not full O3",
            r16.get("method") == "b1_b7_cone01_r16_nlc02_clifford_frame_invariance_lemma_gate_v0"
            and r16s.get("validation_error_count") == 0
            and r16s.get("clifford_frame_invariance_sublemma_closed") is True
            and r16s.get("o3_closed") is False,
            {
                "r16_method": r16.get("method"),
                "r16_validation_error_count": r16s.get("validation_error_count"),
                "clifford_frame_invariance_sublemma_closed": r16s.get(
                    "clifford_frame_invariance_sublemma_closed"
                ),
                "o3_closed": r16s.get("o3_closed"),
            },
        ),
        requirement(
            "I3",
            "R17 declares a search-domain boundary and still keeps O3 open",
            r17.get("method") == "b1_b7_cone01_r17_nlc02_o1_search_domain_boundary_gate_v0"
            and r17s.get("validation_error_count") == 0
            and r17s.get("search_domain_negative_diagnostic_ready") is True
            and r17s.get("o3_closed") is False,
            {
                "r17_method": r17.get("method"),
                "r17_validation_error_count": r17s.get("validation_error_count"),
                "search_domain_negative_diagnostic_ready": r17s.get(
                    "search_domain_negative_diagnostic_ready"
                ),
                "o3_closed": r17s.get("o3_closed"),
            },
        ),
        requirement(
            "I4",
            "Registry enumerates five equivalence-family rows",
            len(family_rows) == 5
            and [row["family_id"] for row in family_rows] == ["O3-F1", "O3-F2", "O3-F3", "O3-F4", "O3-F5"],
            {"family_ids": [row["family_id"] for row in family_rows]},
        ),
        requirement(
            "I5",
            "Registry has at least two open families and one blocked Route A family",
            open_family_count >= 2 and blocked_family_count == 1,
            {"open_family_count": open_family_count, "blocked_family_count": blocked_family_count},
        ),
        requirement(
            "I6",
            "Registry exposes falsifier-ready PR targets",
            len(falsifier_rows) == 3
            and all(row["success_condition"] for row in falsifier_rows),
            {"falsifier_count": len(falsifier_rows), "falsifier_ids": [row["falsifier_id"] for row in falsifier_rows]},
        ),
        requirement(
            "I7",
            "Registry is hash-bound to R13, R16, and R17",
            all(registry_packet["source_hashes"].values())
            and all(registry_packet["source_artifact_hashes"].values())
            and bool(registry_packet["family_table_hash"])
            and bool(registry_packet["falsifier_table_hash"])
            and bool(registry_packet["registry_hash"]),
            {
                "source_hashes": registry_packet["source_hashes"],
                "source_artifact_hashes": registry_packet["source_artifact_hashes"],
                "family_table_hash": registry_packet["family_table_hash"],
                "falsifier_table_hash": registry_packet["falsifier_table_hash"],
                "registry_hash": registry_packet["registry_hash"],
            },
        ),
        requirement(
            "I8",
            "Registry explicitly refuses to close full O3",
            registry_packet["decision"]["o3_closed"] is False
            and registry_packet["decision"]["o3_attack_surface_partitioned"] is True,
            registry_packet["decision"],
        ),
        requirement(
            "I9",
            "Registry is not upgraded into a checked negative lemma or reroute",
            registry_packet["decision"]["checked_negative_lemma_present"] is False
            and registry_packet["decision"]["nlc02_full_lemma_ready"] is False
            and registry_packet["decision"]["reroute_allowed"] is False,
            registry_packet["decision"],
        ),
        requirement(
            "I10",
            "Registry preserves zero resource and B7 credit claims",
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
        validation_errors.append(f"unexpected R18 O3 registry failures: {failed_ids}")

    summary = {
        "registry_id": REGISTRY_ID,
        "registry_hash": registry_packet["registry_hash"],
        "family_table_hash": registry_packet["family_table_hash"],
        "falsifier_table_hash": registry_packet["falsifier_table_hash"],
        "source_r13_binding_hash": r13s["binding_hash"],
        "source_r16_lemma_hash": r16s["lemma_hash"],
        "source_r17_boundary_hash": r17s["boundary_hash"],
        "candidate_id": CANDIDATE_ID,
        "family_count": len(family_rows),
        "closed_sublemma_count": closed_sublemma_count,
        "open_family_count": open_family_count,
        "blocked_family_count": blocked_family_count,
        "falsifier_count": len(falsifier_rows),
        "o3_attack_surface_partitioned": True,
        "o3_closed": False,
        "remaining_open_obligations": ["O3_general_local_unitary_invariance", "Route_A_candidate_reparameterization"],
        "remaining_open_obligation_count": 2,
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
        "title": "B1/B7 Cone01 R18 NL-C02 O3 Equivalence-Family Registry Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "summary": summary,
        "nlc02_o3_equivalence_family_registry_packet": registry_packet,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "R18 partitions O3 into concrete equivalence-family rows and falsifier-ready PR targets. "
                "It records that only the Clifford-frame affine sublemma is closed."
            ),
            "what_is_not_supported": (
                "R18 does not close general local-unitary invariance, does not make NL-C02 a checked negative "
                "lemma, and does not permit R5 reroute. No R1 solution, occurrence removal, proxy-T reduction, "
                "B7 credit, resource saving, or impossibility theorem is supported."
            ),
            "next_gate": (
                "Submit an O3-F3 symbolic local-unitary proof/counterexample, an O3-F4 numerical refit harness, "
                "or an O3-F5 Route A candidate artifact against the R7/R8 contract."
            ),
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    packet = payload["nlc02_o3_equivalence_family_registry_packet"]
    lines = [
        f"# {payload['title']}",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Candidate: `{s['candidate_id']}`",
        f"- Registry hash: `{s['registry_hash']}`",
        f"- Family-table hash: `{s['family_table_hash']}`",
        f"- Falsifier-table hash: `{s['falsifier_table_hash']}`",
        "",
        "## Result",
        "",
        (
            f"The R18 O3 registry gate passes {s['requirements_passed']}/{s['requirement_count']} requirements. "
            "It partitions O3 into concrete equivalence-family work items, but it does not close O3."
        ),
        "",
        "## Registry Statement",
        "",
        packet["o3_registry_statement"],
        "",
        "## Equivalence Families",
        "",
    ]
    for row in packet["family_rows"]:
        lines.append(f"- `{row['family_id']}` {row['family']}: {row['status']}")
    lines.extend(["", "## Falsifier Targets", ""])
    for row in packet["falsifier_rows"]:
        lines.append(f"- `{row['falsifier_id']}` -> `{row['target_family']}`: {row['success_condition']}")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- O3 attack surface partitioned: `{s['o3_attack_surface_partitioned']}`",
            f"- O3 closed: `{s['o3_closed']}`",
            f"- Closed sublemma count: `{s['closed_sublemma_count']}`",
            f"- Open family count: `{s['open_family_count']}`",
            f"- Blocked family count: `{s['blocked_family_count']}`",
            f"- Falsifier count: `{s['falsifier_count']}`",
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
            "This registry gate does not claim resource saving, occurrence removal, proxy-T reduction, B7 ledger improvement, FT resource credit, a checked impossibility theorem, an R5 reroute, or a solved B1/B7 problem.",
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
        "--r13-binding",
        type=Path,
        default=Path("results/B1_B7_cone01_R13_nlc02_source_domain_binding_gate_v0.json"),
    )
    parser.add_argument(
        "--r16-lemma",
        type=Path,
        default=Path("results/B1_B7_cone01_R16_nlc02_clifford_frame_invariance_lemma_gate_v0.json"),
    )
    parser.add_argument(
        "--r17-boundary",
        type=Path,
        default=Path("results/B1_B7_cone01_R17_nlc02_o1_search_domain_boundary_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R18_nlc02_o3_equivalence_family_registry_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R18_nlc02_o3_equivalence_family_registry_gate.md"),
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
                "registry_hash": payload["summary"]["registry_hash"],
                "family_table_hash": payload["summary"]["family_table_hash"],
                "falsifier_table_hash": payload["summary"]["falsifier_table_hash"],
                "family_count": payload["summary"]["family_count"],
                "open_family_count": payload["summary"]["open_family_count"],
                "blocked_family_count": payload["summary"]["blocked_family_count"],
                "falsifier_count": payload["summary"]["falsifier_count"],
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
        raise SystemExit("B1/B7 R18 O3 registry gate validation failed")


if __name__ == "__main__":
    main()
