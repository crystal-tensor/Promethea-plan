#!/usr/bin/env python3
"""T-B4-002i/T-B8-003m: quantify real-backend soundness margins."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any


METHOD = "b4_b8_real_backend_soundness_margin_gate_v0"
STATUS = "real_backend_soundness_margin_failed_missing_real_backend_rows"
MODEL_STATUS = "synthetic_holdout_acceptance_margins_quantified_not_soundness"
VERSION = "0.1"
NO_LEAK_THRESHOLD = 0.10
FULL_LEAK_THRESHOLD = 0.25
EXPECTED_FAILED_IDS = ["M4", "M5", "M6"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def acceptance_budget(rate: float, denominator: int, threshold: float) -> dict[str, Any]:
    observed_accepts = int(round(rate * denominator))
    allowed_accepts = int(math.floor(threshold * denominator))
    excess_accepts = max(0, observed_accepts - allowed_accepts)
    absolute_margin = threshold - rate
    reduction_factor_needed = (rate / threshold) if threshold > 0 else None
    return {
        "rate": rate,
        "denominator": denominator,
        "observed_accepts": observed_accepts,
        "threshold": threshold,
        "allowed_accepts": allowed_accepts,
        "excess_accepts": excess_accepts,
        "absolute_margin": absolute_margin,
        "passes_threshold": rate <= threshold,
        "reduction_factor_needed": reduction_factor_needed,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    packet_scout = load_json(args.packet_scout)
    summary = packet_scout["summary"]
    holdout_rows = int(summary["holdout_row_count"])
    real_backend_rows = int(summary["real_backend_transcript_rows"])
    private_safe_rate = float(summary["private_safe_max_no_leak_fitted_acceptance"])
    leakage_blind_rate = float(summary["leakage_blind_max_no_leak_fitted_acceptance"])
    full_leak_rate = float(summary["leakage_aware_max_full_private_material_leak_fitted_acceptance"])

    private_safe_budget = acceptance_budget(private_safe_rate, holdout_rows, NO_LEAK_THRESHOLD)
    leakage_blind_budget = acceptance_budget(leakage_blind_rate, holdout_rows, NO_LEAK_THRESHOLD)
    full_leak_budget = acceptance_budget(full_leak_rate, holdout_rows, FULL_LEAK_THRESHOLD)

    requirements = [
        requirement(
            "M1",
            "Real-backend packet scout is present and still blocks promotion",
            packet_scout.get("status") == "real_backend_packet_scout_failed_missing_real_backend_evidence",
            {
                "source_status": packet_scout.get("status"),
                "failed_packet_scout_requirement_ids": summary.get(
                    "failed_packet_scout_requirement_ids"
                ),
            },
        ),
        requirement(
            "M2",
            "Holdout denominator and fitted-evaluation rows are explicit",
            holdout_rows == 160 and int(summary["fitted_evaluation_row_count"]) == 640,
            {
                "holdout_row_count": holdout_rows,
                "fitted_evaluation_row_count": summary["fitted_evaluation_row_count"],
            },
        ),
        requirement(
            "M3",
            "Private-safe no-leak fitted acceptance is within the no-leak threshold",
            private_safe_budget["passes_threshold"],
            private_safe_budget,
        ),
        requirement(
            "M4",
            "Leakage-blind no-leak fitted acceptance is within the no-leak threshold",
            leakage_blind_budget["passes_threshold"],
            leakage_blind_budget,
        ),
        requirement(
            "M5",
            "Full-private-material leakage is contained within the leakage threshold",
            full_leak_budget["passes_threshold"],
            full_leak_budget,
        ),
        requirement(
            "M6",
            "Real backend transcript rows exist before claiming soundness margins",
            real_backend_rows > 0,
            {"real_backend_transcript_rows": real_backend_rows},
        ),
        requirement(
            "M7",
            "Next PR acceptance budgets are computable from the current holdout denominator",
            leakage_blind_budget["allowed_accepts"] == 16 and full_leak_budget["allowed_accepts"] == 40,
            {
                "no_leak_allowed_accepts_per_160": leakage_blind_budget["allowed_accepts"],
                "full_leak_allowed_accepts_per_160": full_leak_budget["allowed_accepts"],
            },
        ),
        requirement(
            "M8",
            "Forbidden soundness, advantage, and BQP claims remain false",
            all(
                summary.get(key) is False
                for key in [
                    "protocol_soundness_proved",
                    "cryptographic_soundness_proved",
                    "sampling_hardness_proved",
                    "quantum_advantage_claimed",
                    "bqp_separation_claimed",
                ]
            ),
            {
                "protocol_soundness_proved": summary.get("protocol_soundness_proved"),
                "cryptographic_soundness_proved": summary.get("cryptographic_soundness_proved"),
                "sampling_hardness_proved": summary.get("sampling_hardness_proved"),
                "quantum_advantage_claimed": summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": summary.get("bqp_separation_claimed"),
            },
        ),
    ]
    passed = sum(item["passed"] for item in requirements)
    failed_ids = [item["requirement_id"] for item in requirements if not item["passed"]]
    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected failed margin requirements: {failed_ids}")
    if real_backend_rows != 0:
        validation_errors.append("margin gate should not fabricate real backend transcript rows")

    payload_summary = {
        "source_packet_scout_status": packet_scout.get("status"),
        "margin_requirement_count": len(requirements),
        "margin_requirements_passed": passed,
        "margin_requirements_failed": len(requirements) - passed,
        "failed_margin_requirement_ids": failed_ids,
        "holdout_row_count": holdout_rows,
        "fitted_evaluation_row_count": summary["fitted_evaluation_row_count"],
        "real_backend_transcript_rows": real_backend_rows,
        "no_leak_threshold": NO_LEAK_THRESHOLD,
        "full_leak_threshold": FULL_LEAK_THRESHOLD,
        "private_safe_no_leak_budget": private_safe_budget,
        "leakage_blind_no_leak_budget": leakage_blind_budget,
        "full_private_material_leak_budget": full_leak_budget,
        "leakage_blind_excess_accepts_per_160": leakage_blind_budget["excess_accepts"],
        "full_leak_excess_accepts_per_160": full_leak_budget["excess_accepts"],
        "real_backend_soundness_margin_ready": False,
        "protocol_soundness_proved": False,
        "cryptographic_soundness_proved": False,
        "sampling_hardness_proved": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark": "B4/B8",
        "benchmark_id": "B4_B8",
        "dependency_benchmarks": ["B4", "B8", "B10"],
        "title": "B4/B8 Real-Backend Soundness Margin Gate v0",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_packet_scout_result": str(args.packet_scout),
        "summary": payload_summary,
        "requirements": requirements,
        "claim_boundary": {
            "what_is_supported": (
                "The synthetic fitted-spoofer holdout margins are quantified as acceptance "
                "budgets for the next real-backend PR."
            ),
            "what_is_not_supported": (
                "No real backend transcript rows exist, leakage-blind no-leak acceptance "
                "still exceeds the 0.10 threshold, full leakage is not contained, and no "
                "protocol soundness, quantum advantage, or BQP separation is established."
            ),
            "next_gate": (
                "Collect real backend transcript rows and make leakage-blind no-leak "
                "acceptance <= 16/160 while full-private-material leakage is either "
                "excluded or <= 40/160."
            ),
            "protocol_soundness_proved": False,
            "cryptographic_soundness_proved": False,
            "sampling_hardness_proved": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# B4/B8 Real-Backend Soundness Margin Gate v0.1",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Requirements passed/failed: {summary['margin_requirements_passed']} / {summary['margin_requirements_failed']}",
        f"- Failed requirement IDs: {summary['failed_margin_requirement_ids']}",
        f"- Holdout rows / real backend rows: {summary['holdout_row_count']} / {summary['real_backend_transcript_rows']}",
        f"- Private-safe no-leak accepts: {summary['private_safe_no_leak_budget']['observed_accepts']} / {summary['holdout_row_count']}",
        f"- Leakage-blind no-leak accepts: {summary['leakage_blind_no_leak_budget']['observed_accepts']} / {summary['holdout_row_count']} (excess {summary['leakage_blind_excess_accepts_per_160']})",
        f"- Full-leakage accepts: {summary['full_private_material_leak_budget']['observed_accepts']} / {summary['holdout_row_count']} (excess {summary['full_leak_excess_accepts_per_160']})",
        "",
        "## Acceptance Budgets",
        "",
        "| channel | threshold | observed accepts | allowed accepts | excess accepts | passes |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for label, budget_key in [
        ("private-safe no-leak", "private_safe_no_leak_budget"),
        ("leakage-blind no-leak", "leakage_blind_no_leak_budget"),
        ("full private-material leakage", "full_private_material_leak_budget"),
    ]:
        budget = summary[budget_key]
        lines.append(
            f"| {label} | {budget['threshold']} | {budget['observed_accepts']} | "
            f"{budget['allowed_accepts']} | {budget['excess_accepts']} | {budget['passes_threshold']} |"
        )
    lines.extend(
        [
            "",
            "## Requirement Results",
            "",
        ]
    )
    for item in payload["requirements"]:
        state = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {item['requirement_id']} [{state}]: {item['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            f"- protocol_soundness_proved: {payload['claim_boundary']['protocol_soundness_proved']}",
            f"- quantum_advantage_claimed: {payload['claim_boundary']['quantum_advantage_claimed']}",
            f"- bqp_separation_claimed: {payload['claim_boundary']['bqp_separation_claimed']}",
            "",
            "## Validation",
            "",
            f"- validation_error_count: {len(payload['validation_errors'])}",
        ]
    )
    if payload["validation_errors"]:
        lines.extend(f"- {error}" for error in payload["validation_errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--packet-scout",
        type=Path,
        default=Path("results/B4_B8_real_backend_packet_scout_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B4_B8_real_backend_soundness_margin_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B4_B8_real_backend_soundness_margin_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-01")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    write_markdown(payload, args.markdown_output)
    print(payload["status"])
    print(
        payload["summary"]["margin_requirements_passed"],
        payload["summary"]["margin_requirements_failed"],
        payload["summary"]["failed_margin_requirement_ids"],
    )


if __name__ == "__main__":
    main()
