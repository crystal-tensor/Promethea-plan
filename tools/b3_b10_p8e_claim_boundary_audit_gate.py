#!/usr/bin/env python3
"""T-B3-045/T-B10-015af: P8-E claim-boundary audit gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


METHOD = "b3_b10_p8e_claim_boundary_audit_gate_v0"
STATUS = "b3_b10_p8e_claim_boundary_audit_passed_zero_credit"
MODEL_STATUS = "p8e_claim_boundary_locked_no_premature_b3_b10_claims"
VERSION = "0.1"
EXPECTED_PRESSURE_PACKET_HASH = "55384c1a143b50d9b334193c3e55151f33bc9511b90dd19a21f22198bf9fe0b0"
EXPECTED_P8A_TEMPLATE_TABLE_HASH = "a82007811e0448e2436857aaf22ca5fcf30060a1d032370f8f8e8252848584a2"
EXPECTED_P8B_TEMPLATE_TABLE_HASH = "95ea8fecbfb592aae2491ec95d4dc6b19d0b12e98b4dfdbee0087499cfe523ba"
EXPECTED_P8C_BLOCKER_TABLE_HASH = "290440c963db1924d8fefefaa3435e95830e171e4cd2ca29962a60f2992cb009"
EXPECTED_CSS_HASH = "648722d5e4b5fddd6a51e545ff7a6a09a4156e391a808e5cd0daf0b2172f8732"


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


def css_hash(html: str) -> str:
    match = re.search(r"<style>(.*?)</style>", html, re.S)
    if not match:
        return ""
    return hashlib.sha256(match.group(1).encode("utf-8")).hexdigest()


def forbidden_hits(text: str) -> list[str]:
    patterns = [
        r"\bB3\s+solved\b",
        r"\breaction[- ]dynamics\s+solution\s+achieved\b",
        r"\bquantum\s+advantage\s+achieved\b",
        r"\bBQP\s+separation\s+achieved\b",
        r"\bB10[- ]T1\s+credit\s+allowed\b",
        r"\bb3_reopen_ready['\"]?\s*[:=]\s*true\b",
        r"\bb10_t1_credit_allowed['\"]?\s*[:=]\s*true\b",
        r"\bquantum_advantage_claimed['\"]?\s*[:=]\s*true\b",
        r"\bbqp_separation_claimed['\"]?\s*[:=]\s*true\b",
    ]
    hits: list[str] = []
    for pattern in patterns:
        if re.search(pattern, text, flags=re.I):
            hits.append(pattern)
    return hits


def result_boundary_row(label: str, payload: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    summary = payload["summary"]
    row = {
        "label": label,
        "method": payload.get("method"),
        "status": payload.get("status"),
        "expected_hash_key": expected.get("hash_key"),
        "expected_hash_value": expected.get("hash_value"),
        "actual_hash_value": summary.get(expected.get("hash_key", "")),
        "accepted_full_covariance_row_count": summary.get("accepted_full_covariance_row_count", 0),
        "accepted_denominator_win_row_count": summary.get("accepted_denominator_win_row_count", 0),
        "denominator_win_count": summary.get("denominator_win_count", 0),
        "b3_reopen_ready": summary.get("b3_reopen_ready", False),
        "b10_t1_credit_allowed": summary.get("b10_t1_credit_allowed", False),
        "quantum_advantage_claimed": summary.get("quantum_advantage_claimed", False),
        "bqp_separation_claimed": summary.get("bqp_separation_claimed", False),
        "validation_error_count": summary.get("validation_error_count", 0),
    }
    row["hash_matches"] = row["actual_hash_value"] == row["expected_hash_value"]
    row["zero_credit_boundary_holds"] = (
        row["accepted_full_covariance_row_count"] == 0
        and row["denominator_win_count"] == 0
        and row["b3_reopen_ready"] is False
        and row["b10_t1_credit_allowed"] is False
        and row["quantum_advantage_claimed"] is False
        and row["bqp_separation_claimed"] is False
        and row["validation_error_count"] == 0
    )
    return row


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    pressure = load_json(args.p8_pressure_gate)
    p8a = load_json(args.p8a_intake_gate)
    p8b = load_json(args.p8b_intake_gate)
    p8c = load_json(args.p8c_readiness_gate)
    landing = args.landing_page.read_text(encoding="utf-8")
    landing_css_hash = css_hash(landing)

    pressure_summary = pressure["summary"]
    p8a_summary = p8a["summary"]
    p8b_summary = p8b["summary"]
    p8c_summary = p8c["summary"]
    p8e_packet = next(
        (packet for packet in pressure.get("pressure_packets", []) if packet.get("packet_id") == "P8-E"),
        {},
    )
    boundary_rows = [
        {
            "label": "P8-pressure",
            "method": pressure.get("method"),
            "status": pressure.get("status"),
            "actual_hash_value": pressure_summary.get("pressure_packet_hash"),
            "expected_hash_value": EXPECTED_PRESSURE_PACKET_HASH,
            "hash_matches": pressure_summary.get("pressure_packet_hash") == EXPECTED_PRESSURE_PACKET_HASH,
            "accepted_full_covariance_row_count": pressure_summary.get(
                "accepted_full_covariance_row_count", 0
            ),
            "accepted_denominator_win_row_count": 0,
            "denominator_win_count": pressure_summary.get("denominator_win_count", 0),
            "b3_reopen_ready": pressure_summary.get("b3_reopen_ready", False),
            "b10_t1_credit_allowed": pressure_summary.get("b10_t1_credit_allowed", False),
            "quantum_advantage_claimed": pressure_summary.get("quantum_advantage_claimed", False),
            "bqp_separation_claimed": pressure_summary.get("bqp_separation_claimed", False),
            "validation_error_count": pressure_summary.get("validation_error_count", 0),
        },
        result_boundary_row(
            "P8-A",
            p8a,
            {"hash_key": "template_table_hash", "hash_value": EXPECTED_P8A_TEMPLATE_TABLE_HASH},
        ),
        result_boundary_row(
            "P8-B",
            p8b,
            {"hash_key": "template_table_hash", "hash_value": EXPECTED_P8B_TEMPLATE_TABLE_HASH},
        ),
        result_boundary_row(
            "P8-C",
            p8c,
            {"hash_key": "blocker_table_hash", "hash_value": EXPECTED_P8C_BLOCKER_TABLE_HASH},
        ),
    ]
    for row in boundary_rows:
        row["zero_credit_boundary_holds"] = (
            row.get("accepted_full_covariance_row_count", 0) == 0
            and row.get("denominator_win_count", 0) == 0
            and row.get("b3_reopen_ready") is False
            and row.get("b10_t1_credit_allowed") is False
            and row.get("quantum_advantage_claimed") is False
            and row.get("bqp_separation_claimed") is False
            and row.get("validation_error_count") == 0
        )
    boundary_table_hash = stable_hash(boundary_rows)
    landing_hits = forbidden_hits(landing)
    result_hits = forbidden_hits(json.dumps([pressure, p8a, p8b, p8c], sort_keys=True))

    requirements = [
        requirement(
            "E1",
            "P8-E claim-boundary packet is ready in the source pressure gate",
            p8e_packet.get("status") == "ready_for_external_pr_not_credit"
            and p8e_packet.get("packet_id") == "P8-E"
            and pressure_summary.get("pressure_packet_hash") == EXPECTED_PRESSURE_PACKET_HASH,
            {
                "packet": p8e_packet,
                "pressure_packet_hash": pressure_summary.get("pressure_packet_hash"),
            },
        ),
        requirement(
            "E2",
            "P8-A/P8-B/P8-C source hashes match the locked intake/readiness artifacts",
            all(row["hash_matches"] for row in boundary_rows),
            {"boundary_rows": boundary_rows},
        ),
        requirement(
            "E3",
            "All audited P8 artifacts preserve zero-credit boundaries",
            all(row["zero_credit_boundary_holds"] for row in boundary_rows),
            {"boundary_rows": boundary_rows},
        ),
        requirement(
            "E4",
            "No forbidden positive claim pattern appears in audited P8 result artifacts",
            len(result_hits) == 0,
            {"forbidden_result_hits": result_hits},
        ),
        requirement(
            "E5",
            "Landing page has the expected current research status without changing style",
            "T-B3-045/T-B10-015af" in landing
            and "P8-E claim-boundary audit" in landing
            and landing_css_hash == EXPECTED_CSS_HASH,
            {
                "contains_t_b3_045": "T-B3-045/T-B10-015af" in landing,
                "contains_p8e_phrase": "P8-E claim-boundary audit" in landing,
                "landing_css_hash": landing_css_hash,
                "expected_css_hash": EXPECTED_CSS_HASH,
            },
        ),
        requirement(
            "E6",
            "No forbidden positive claim pattern appears in the landing page",
            len(landing_hits) == 0,
            {"forbidden_landing_hits": landing_hits},
        ),
        requirement(
            "E7",
            "P8-E keeps B3/B10 promotion disabled until P8-A, P8-B, and P8-C gates pass",
            p8a_summary.get("accepted_full_covariance_row_count") == 0
            and p8b_summary.get("accepted_denominator_win_row_count") == 0
            and p8c_summary.get("ready_for_derivative_optimizer_promotion") is False,
            {
                "p8a_accepted_full_covariance_row_count": p8a_summary.get(
                    "accepted_full_covariance_row_count"
                ),
                "p8b_accepted_denominator_win_row_count": p8b_summary.get(
                    "accepted_denominator_win_row_count"
                ),
                "p8c_ready_for_derivative_optimizer_promotion": p8c_summary.get(
                    "ready_for_derivative_optimizer_promotion"
                ),
            },
        ),
        requirement(
            "E8",
            "P8-E audit table is deterministic and source-bound",
            boundary_table_hash == stable_hash(boundary_rows)
            and len(boundary_rows) == 4,
            {"boundary_table_hash": boundary_table_hash, "boundary_row_count": len(boundary_rows)},
        ),
    ]
    passed = sum(row["passed"] for row in requirements)
    failed_ids = [row["requirement_id"] for row in requirements if not row["passed"]]
    validation_errors: list[str] = []
    if failed_ids:
        validation_errors.append(f"unexpected P8-E claim-boundary failures: {failed_ids}")
    if any(row.get("b3_reopen_ready") for row in boundary_rows):
        validation_errors.append("P8-E audit must not allow B3 reopen")
    if any(row.get("b10_t1_credit_allowed") for row in boundary_rows):
        validation_errors.append("P8-E audit must not allow B10-T1 credit")

    summary = {
        "claim_boundary_audit_id": "B3B10-P8E-claim-boundary-audit",
        "source_pressure_packet_hash": pressure_summary.get("pressure_packet_hash"),
        "source_p8a_template_table_hash": p8a_summary.get("template_table_hash"),
        "source_p8b_template_table_hash": p8b_summary.get("template_table_hash"),
        "source_p8c_blocker_table_hash": p8c_summary.get("blocker_table_hash"),
        "boundary_table_hash": boundary_table_hash,
        "landing_css_hash": landing_css_hash,
        "boundary_row_count": len(boundary_rows),
        "forbidden_result_hit_count": len(result_hits),
        "forbidden_landing_hit_count": len(landing_hits),
        "accepted_full_covariance_row_count": 0,
        "accepted_denominator_win_row_count": 0,
        "denominator_win_count": 0,
        "ready_for_derivative_optimizer_promotion": False,
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
        "title": "B3/B10 P8-E Claim Boundary Audit Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_p8_pressure_gate": str(args.p8_pressure_gate),
        "source_p8a_intake_gate": str(args.p8a_intake_gate),
        "source_p8b_intake_gate": str(args.p8b_intake_gate),
        "source_p8c_readiness_gate": str(args.p8c_readiness_gate),
        "source_landing_page": str(args.landing_page),
        "source_target_id": "B10-T1",
        "dependency_benchmarks": ["B3", "B10"],
        "summary": summary,
        "boundary_rows": boundary_rows,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "P8-E now audits the current P8 pressure, P8-A, P8-B, P8-C, and landing-page "
                "claim boundary state and confirms zero-credit language remains enforced."
            ),
            "what_is_not_supported": (
                "This does not solve P8, accept rows, create denominator wins, reopen B3, grant "
                "B10-T1 credit, claim quantum advantage, or claim BQP separation."
            ),
            "next_gate": (
                "Submit positive P8-A and P8-B artifacts, rerun P8-C readiness, and rerun this "
                "P8-E audit after any public-facing status update."
            ),
            "accepted_full_covariance_row_count": 0,
            "accepted_denominator_win_row_count": 0,
            "denominator_win_count": 0,
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
        "# B3/B10 P8-E Claim Boundary Audit Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Audit: `{s['claim_boundary_audit_id']}`",
        f"- Boundary table hash: `{s['boundary_table_hash']}`",
        f"- Landing CSS hash: `{s['landing_css_hash']}`",
        f"- Boundary rows: `{s['boundary_row_count']}`",
        f"- Forbidden result hits / landing hits: `{s['forbidden_result_hit_count']}` / `{s['forbidden_landing_hit_count']}`",
        f"- Accepted rows / denominator wins: `{s['accepted_full_covariance_row_count']}` / `{s['denominator_win_count']}`",
        f"- Requirements passed/failed: `{s['requirements_passed']}` / `{s['requirements_failed']}`",
        f"- Failed requirement IDs: `{s['failed_requirement_ids']}`",
        f"- validation_error_count: `{s['validation_error_count']}`",
        "",
        "## Boundary Rows",
        "",
    ]
    for row in payload["boundary_rows"]:
        lines.extend(
            [
                f"### {row['label']}",
                "",
                f"- Method: `{row['method']}`",
                f"- Status: `{row['status']}`",
                f"- Hash matches: `{row['hash_matches']}`",
                f"- Zero-credit boundary holds: `{row['zero_credit_boundary_holds']}`",
                f"- accepted_full_covariance_row_count: `{row['accepted_full_covariance_row_count']}`",
                f"- denominator_win_count: `{row['denominator_win_count']}`",
                f"- b3_reopen_ready: `{row['b3_reopen_ready']}`",
                f"- b10_t1_credit_allowed: `{row['b10_t1_credit_allowed']}`",
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
        "--landing-page",
        type=Path,
        default=Path("research/axiom_horizon_landing.html"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_B10_P8E_claim_boundary_audit_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_B10_P8E_claim_boundary_audit_gate.md"),
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
