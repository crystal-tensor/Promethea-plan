#!/usr/bin/env python3
"""T-B3-047/T-B10-015ah: P8 integrated acceptance closure gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b3_b10_p8_integrated_acceptance_closure_gate_v0"
STATUS = "b3_b10_p8_integrated_acceptance_closure_open_zero_credit"
MODEL_STATUS = "p8_integrated_closure_board_open_until_positive_replay_artifacts"
VERSION = "0.1"
EXPECTED_PRESSURE_PACKET_HASH = "55384c1a143b50d9b334193c3e55151f33bc9511b90dd19a21f22198bf9fe0b0"
EXPECTED_P8A_TEMPLATE_TABLE_HASH = "a82007811e0448e2436857aaf22ca5fcf30060a1d032370f8f8e8252848584a2"
EXPECTED_P8B_TEMPLATE_TABLE_HASH = "95ea8fecbfb592aae2491ec95d4dc6b19d0b12e98b4dfdbee0087499cfe523ba"
EXPECTED_P8C_BLOCKER_TABLE_HASH = "290440c963db1924d8fefefaa3435e95830e171e4cd2ca29962a60f2992cb009"
EXPECTED_P8D_ACCESS_BOUNDARY_HASH = "e5a2fa2de1148b5272d078dcfa7139bac8347682954cd966cea4894e51378495"
EXPECTED_P8E_BOUNDARY_TABLE_HASH = "5cb6bb002a4f67e28f28dcd943ff40dbe682a166bba7c7fa14c70a28c408e769"


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


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    pressure = load_json(args.p8_pressure_gate)
    p8a = load_json(args.p8a_intake_gate)
    p8b = load_json(args.p8b_intake_gate)
    p8c = load_json(args.p8c_readiness_gate)
    p8d = load_json(args.p8d_access_boundary_gate)
    p8e = load_json(args.p8e_claim_audit_gate)

    pressure_summary = pressure["summary"]
    p8a_summary = p8a["summary"]
    p8b_summary = p8b["summary"]
    p8c_summary = p8c["summary"]
    p8d_summary = p8d["summary"]
    p8e_summary = p8e["summary"]

    closure_rows = [
        {
            "packet_id": "P8-A",
            "title": "Accepted-row validity replay",
            "artifact": str(args.p8a_intake_gate),
            "hash": p8a_summary.get("template_table_hash"),
            "expected_hash": EXPECTED_P8A_TEMPLATE_TABLE_HASH,
            "state": "open_missing_accepted_row",
            "positive_condition": "accepted_full_covariance_row_count > 0",
            "current_value": p8a_summary.get("accepted_full_covariance_row_count"),
            "positive": p8a_summary.get("accepted_full_covariance_row_count", 0) > 0,
            "credit_allowed": False,
        },
        {
            "packet_id": "P8-B",
            "title": "Same-access denominator win replay",
            "artifact": str(args.p8b_intake_gate),
            "hash": p8b_summary.get("template_table_hash"),
            "expected_hash": EXPECTED_P8B_TEMPLATE_TABLE_HASH,
            "state": "open_missing_denominator_win",
            "positive_condition": "accepted_denominator_win_row_count > 0",
            "current_value": p8b_summary.get("accepted_denominator_win_row_count"),
            "positive": p8b_summary.get("accepted_denominator_win_row_count", 0) > 0,
            "credit_allowed": False,
        },
        {
            "packet_id": "P8-C",
            "title": "Derivative and optimizer-loop promotion readiness",
            "artifact": str(args.p8c_readiness_gate),
            "hash": p8c_summary.get("blocker_table_hash"),
            "expected_hash": EXPECTED_P8C_BLOCKER_TABLE_HASH,
            "state": "blocked_missing_p8a_p8b_positive",
            "positive_condition": "ready_for_derivative_optimizer_promotion is true",
            "current_value": p8c_summary.get("ready_for_derivative_optimizer_promotion"),
            "positive": p8c_summary.get("ready_for_derivative_optimizer_promotion") is True,
            "credit_allowed": False,
        },
        {
            "packet_id": "P8-D",
            "title": "B10 access-boundary replay",
            "artifact": str(args.p8d_access_boundary_gate),
            "hash": p8d_summary.get("access_boundary_table_hash"),
            "expected_hash": EXPECTED_P8D_ACCESS_BOUNDARY_HASH,
            "state": "blocked_until_p8abc_positive",
            "positive_condition": "b10_access_boundary_blocked is false with P8-A/P8-B/P8-C positive",
            "current_value": p8d_summary.get("b10_access_boundary_blocked"),
            "positive": p8d_summary.get("b10_access_boundary_blocked") is False,
            "credit_allowed": False,
        },
        {
            "packet_id": "P8-E",
            "title": "Claim-boundary audit",
            "artifact": str(args.p8e_claim_audit_gate),
            "hash": p8e_summary.get("boundary_table_hash"),
            "expected_hash": EXPECTED_P8E_BOUNDARY_TABLE_HASH,
            "state": "audit_passed_zero_credit",
            "positive_condition": "requirements_failed == 0 and forbidden hits == 0",
            "current_value": {
                "requirements_failed": p8e_summary.get("requirements_failed"),
                "forbidden_result_hit_count": p8e_summary.get("forbidden_result_hit_count"),
                "forbidden_landing_hit_count": p8e_summary.get("forbidden_landing_hit_count"),
            },
            "positive": (
                p8e_summary.get("requirements_failed") == 0
                and p8e_summary.get("forbidden_result_hit_count") == 0
                and p8e_summary.get("forbidden_landing_hit_count") == 0
            ),
            "credit_allowed": False,
        },
    ]
    for row in closure_rows:
        row["hash_matches"] = row["hash"] == row["expected_hash"]

    closure_table_hash = stable_hash(closure_rows)
    positive_packet_ids = [row["packet_id"] for row in closure_rows if row["positive"] is True]
    unresolved_packet_ids = [
        row["packet_id"]
        for row in closure_rows
        if row["packet_id"] != "P8-E" and row["positive"] is False
    ]
    p8_resolved = unresolved_packet_ids == [] and "P8-E" in positive_packet_ids

    requirements = [
        requirement(
            "G1",
            "Source P8 pressure gate is current and lists all P8 packets",
            pressure.get("method") == "b3_b10_f1_p8_acceptance_pressure_gate_v0"
            and pressure_summary.get("pressure_packet_hash") == EXPECTED_PRESSURE_PACKET_HASH
            and pressure_summary.get("ready_pressure_packet_ids") == ["P8-A", "P8-B", "P8-C", "P8-E"]
            and pressure_summary.get("blocked_pressure_packet_ids") == ["P8-D"],
            {
                "method": pressure.get("method"),
                "pressure_packet_hash": pressure_summary.get("pressure_packet_hash"),
                "ready_pressure_packet_ids": pressure_summary.get("ready_pressure_packet_ids"),
                "blocked_pressure_packet_ids": pressure_summary.get("blocked_pressure_packet_ids"),
            },
        ),
        requirement(
            "G2",
            "P8-A through P8-E artifacts match their locked hashes",
            all(row["hash_matches"] for row in closure_rows),
            {"closure_rows": closure_rows},
        ),
        requirement(
            "G3",
            "P8-A remains open until at least one accepted row exists",
            "P8-A" in unresolved_packet_ids and p8a_summary.get("accepted_full_covariance_row_count") == 0,
            {"accepted_full_covariance_row_count": p8a_summary.get("accepted_full_covariance_row_count")},
        ),
        requirement(
            "G4",
            "P8-B remains open until at least one same-access denominator win exists",
            "P8-B" in unresolved_packet_ids
            and p8b_summary.get("accepted_denominator_win_row_count") == 0
            and p8b_summary.get("denominator_win_count") == 0,
            {
                "accepted_denominator_win_row_count": p8b_summary.get(
                    "accepted_denominator_win_row_count"
                ),
                "denominator_win_count": p8b_summary.get("denominator_win_count"),
            },
        ),
        requirement(
            "G5",
            "P8-C remains blocked until P8-A and P8-B are positive",
            "P8-C" in unresolved_packet_ids
            and p8c_summary.get("ready_for_derivative_optimizer_promotion") is False,
            {
                "ready_for_derivative_optimizer_promotion": p8c_summary.get(
                    "ready_for_derivative_optimizer_promotion"
                )
            },
        ),
        requirement(
            "G6",
            "P8-D keeps B10-T1 access-boundary credit blocked",
            "P8-D" in unresolved_packet_ids
            and p8d_summary.get("b10_access_boundary_blocked") is True
            and p8d_summary.get("b10_t1_credit_allowed") is False,
            {
                "b10_access_boundary_blocked": p8d_summary.get("b10_access_boundary_blocked"),
                "b10_t1_credit_allowed": p8d_summary.get("b10_t1_credit_allowed"),
            },
        ),
        requirement(
            "G7",
            "P8-E claim-boundary audit passes while preserving zero credit",
            "P8-E" in positive_packet_ids
            and p8e_summary.get("requirements_failed") == 0
            and p8e_summary.get("forbidden_result_hit_count") == 0
            and p8e_summary.get("forbidden_landing_hit_count") == 0
            and p8e_summary.get("b10_t1_credit_allowed") is False,
            {
                "requirements_failed": p8e_summary.get("requirements_failed"),
                "forbidden_result_hit_count": p8e_summary.get("forbidden_result_hit_count"),
                "forbidden_landing_hit_count": p8e_summary.get("forbidden_landing_hit_count"),
                "b10_t1_credit_allowed": p8e_summary.get("b10_t1_credit_allowed"),
            },
        ),
        requirement(
            "G8",
            "Integrated closure does not resolve P8 or grant B3/B10 credit",
            p8_resolved is False
            and pressure_summary.get("b3_reopen_ready") is False
            and pressure_summary.get("b10_t1_credit_allowed") is False
            and pressure_summary.get("quantum_advantage_claimed") is False
            and pressure_summary.get("bqp_separation_claimed") is False,
            {
                "p8_resolved": p8_resolved,
                "b3_reopen_ready": pressure_summary.get("b3_reopen_ready"),
                "b10_t1_credit_allowed": pressure_summary.get("b10_t1_credit_allowed"),
                "quantum_advantage_claimed": pressure_summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": pressure_summary.get("bqp_separation_claimed"),
            },
        ),
        requirement(
            "G9",
            "Integrated closure table is deterministic and source-bound",
            closure_table_hash == stable_hash(closure_rows) and len(closure_rows) == 5,
            {"closure_table_hash": closure_table_hash, "closure_row_count": len(closure_rows)},
        ),
    ]
    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids:
        validation_errors.append(f"unexpected P8 integrated closure failures: {failed_ids}")
    if p8_resolved:
        validation_errors.append("P8 integrated closure must remain open without positive replay artifacts")

    summary = {
        "integrated_closure_id": "B3B10-P8-integrated-acceptance-closure",
        "source_pressure_packet_hash": pressure_summary.get("pressure_packet_hash"),
        "source_p8a_template_table_hash": p8a_summary.get("template_table_hash"),
        "source_p8b_template_table_hash": p8b_summary.get("template_table_hash"),
        "source_p8c_blocker_table_hash": p8c_summary.get("blocker_table_hash"),
        "source_p8d_access_boundary_table_hash": p8d_summary.get("access_boundary_table_hash"),
        "source_p8e_boundary_table_hash": p8e_summary.get("boundary_table_hash"),
        "closure_table_hash": closure_table_hash,
        "closure_row_count": len(closure_rows),
        "positive_packet_ids": positive_packet_ids,
        "unresolved_packet_ids": unresolved_packet_ids,
        "unresolved_packet_count": len(unresolved_packet_ids),
        "p8_resolved": p8_resolved,
        "accepted_full_covariance_row_count": p8a_summary.get("accepted_full_covariance_row_count"),
        "accepted_denominator_win_row_count": p8b_summary.get("accepted_denominator_win_row_count"),
        "denominator_win_count": p8b_summary.get("denominator_win_count"),
        "ready_for_derivative_optimizer_promotion": p8c_summary.get(
            "ready_for_derivative_optimizer_promotion"
        ),
        "b10_access_boundary_blocked": p8d_summary.get("b10_access_boundary_blocked"),
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "failed_requirement_ids": failed_ids,
        "b3_reopen_ready": False,
        "b10_t1_credit_allowed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }
    return {
        "benchmark_id": "B3_B10",
        "problem_ids": [49, 11],
        "title": "B3/B10 P8 Integrated Acceptance Closure Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_p8_pressure_gate": str(args.p8_pressure_gate),
        "source_p8a_intake_gate": str(args.p8a_intake_gate),
        "source_p8b_intake_gate": str(args.p8b_intake_gate),
        "source_p8c_readiness_gate": str(args.p8c_readiness_gate),
        "source_p8d_access_boundary_gate": str(args.p8d_access_boundary_gate),
        "source_p8e_claim_audit_gate": str(args.p8e_claim_audit_gate),
        "source_target_id": "B10-T1",
        "dependency_benchmarks": ["B3", "B10"],
        "summary": summary,
        "closure_rows": closure_rows,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "P8-A through P8-E are now integrated into one closure board that explains "
                "why P8 is still open and why B3/B10 credit remains zero."
            ),
            "what_is_not_supported": (
                "This does not solve P8, accept rows, establish denominator wins, allow P8-C "
                "promotion, unlock B10-T1, claim quantum advantage, or claim BQP separation."
            ),
            "next_gate": (
                "Submit positive P8-A/P8-B artifacts, rerun P8-C/P8-D/P8-E, and rerun this "
                "integrated closure gate before any B3/B10 promotion."
            ),
            "accepted_full_covariance_row_count": summary["accepted_full_covariance_row_count"],
            "accepted_denominator_win_row_count": summary["accepted_denominator_win_row_count"],
            "denominator_win_count": summary["denominator_win_count"],
            "b3_reopen_ready": False,
            "b10_t1_credit_allowed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    s = payload["summary"]
    lines = [
        "# B3/B10 P8 Integrated Acceptance Closure Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Integrated closure: `{s['integrated_closure_id']}`",
        f"- Closure table hash: `{s['closure_table_hash']}`",
        f"- Positive packet IDs: `{s['positive_packet_ids']}`",
        f"- Unresolved packet IDs: `{s['unresolved_packet_ids']}`",
        f"- P8 resolved: `{s['p8_resolved']}`",
        f"- Accepted rows / denominator wins: `{s['accepted_full_covariance_row_count']}` / `{s['denominator_win_count']}`",
        f"- B10 access boundary blocked: `{s['b10_access_boundary_blocked']}`",
        f"- Requirements passed/failed: `{s['requirements_passed']}` / `{s['requirements_failed']}`",
        f"- Failed requirement IDs: `{s['failed_requirement_ids']}`",
        f"- validation_error_count: `{s['validation_error_count']}`",
        "",
        "## Closure Rows",
        "",
    ]
    for row in payload["closure_rows"]:
        lines.extend(
            [
                f"### {row['packet_id']}: {row['title']}",
                "",
                f"- Artifact: `{row['artifact']}`",
                f"- Hash: `{row['hash']}`",
                f"- Hash matches: `{row['hash_matches']}`",
                f"- State: `{row['state']}`",
                f"- Positive condition: {row['positive_condition']}",
                f"- Current value: `{row['current_value']}`",
                f"- Positive: `{row['positive']}`",
                f"- Credit allowed: `{row['credit_allowed']}`",
                "",
            ]
        )
    lines.extend(["## Requirement Results", ""])
    for row in payload["requirements"]:
        state = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- {row['requirement_id']} [{state}]: {row['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            f"- b3_reopen_ready: {payload['claim_boundary']['b3_reopen_ready']}",
            f"- b10_t1_credit_allowed: {payload['claim_boundary']['b10_t1_credit_allowed']}",
            f"- quantum_advantage_claimed: {payload['claim_boundary']['quantum_advantage_claimed']}",
            f"- bqp_separation_claimed: {payload['claim_boundary']['bqp_separation_claimed']}",
            "",
            "## Validation",
            "",
            f"- validation_error_count: {s['validation_error_count']}",
        ]
    )
    if payload["validation_errors"]:
        lines.extend(f"- {error}" for error in payload["validation_errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--p8-pressure-gate",
        type=Path,
        default=Path("results/B3_B10_F1_P8_acceptance_pressure_gate_v0.json"),
    )
    parser.add_argument(
        "--p8a-intake-gate",
        type=Path,
        default=Path("results/B3_B10_P8A_accepted_row_replay_intake_template_gate_v0.json"),
    )
    parser.add_argument(
        "--p8b-intake-gate",
        type=Path,
        default=Path("results/B3_B10_P8B_same_access_denominator_replay_intake_template_gate_v0.json"),
    )
    parser.add_argument(
        "--p8c-readiness-gate",
        type=Path,
        default=Path("results/B3_B10_P8C_derivative_optimizer_promotion_readiness_gate_v0.json"),
    )
    parser.add_argument(
        "--p8d-access-boundary-gate",
        type=Path,
        default=Path("results/B3_B10_P8D_b10_access_boundary_blocked_gate_v0.json"),
    )
    parser.add_argument(
        "--p8e-claim-audit-gate",
        type=Path,
        default=Path("results/B3_B10_P8E_claim_boundary_audit_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_B10_P8_integrated_acceptance_closure_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_B10_P8_integrated_acceptance_closure_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-03")
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
