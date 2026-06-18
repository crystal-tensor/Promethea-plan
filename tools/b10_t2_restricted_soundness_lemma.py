#!/usr/bin/env python3
"""Build a restricted B10-T2 soundness lemma from the refresh gate."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def hoeffding_single_mask_bound(samples: int, signal_gap: float) -> float:
    if signal_gap <= 0:
        return 1.0
    return math.exp(-samples * signal_gap * signal_gap / 2.0)


def hoeffding_independent_masks_bound(samples: int, signal_gap: float, unknown_masks: int) -> float:
    if unknown_masks <= 0:
        return 1.0
    return hoeffding_single_mask_bound(samples, signal_gap) ** unknown_masks


def high_leakage_summary(b8_report: dict, leakage_fraction: float) -> list[dict]:
    return sorted(
        [
            row
            for row in b8_report.get("summary_by_mode", [])
            if float(row.get("leakage_fraction", -1.0)) == leakage_fraction
        ],
        key=lambda row: str(row["refresh_mode"]),
    )


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "restricted_soundness_lemma_proved_under_refresh_independence_model":
        errors.append("status must be the restricted refresh-independence lemma")
    if report.get("source_target_id") != "B10-T2":
        errors.append("source_target_id must be B10-T2")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("report must explicitly avoid BQP separation claims")
    if report.get("hardware_randomized_measurement_circuits_instantiated") is not False:
        errors.append("report must not imply hardware randomized-measurement circuits are instantiated")
    if report.get("sampling_hardness_proved") is not False:
        errors.append("report must not imply sampling hardness is proved")
    if report.get("theorem_count") != 1:
        errors.append("report should contain exactly one restricted lemma")
    if report.get("corollary_count") != 1:
        errors.append("report should contain exactly one operational corollary")
    if report.get("validation_claim", {}).get("admissible_claim") in (None, ""):
        errors.append("report must include an admissible claim")
    if report.get("validation_claim", {}).get("rejected_claim") in (None, ""):
        errors.append("report must include a rejected claim")
    assumptions = report.get("theorem", {}).get("assumptions", [])
    required_phrases = ["refresh independence", "bounded leakage", "unknown predicate"]
    assumption_text = " ".join(assumptions).lower()
    for phrase in required_phrases:
        if phrase not in assumption_text:
            errors.append(f"theorem assumptions should mention {phrase}")
    if float(report.get("single_unknown_mask_soundness_bound", 1.0)) >= 0.05:
        errors.append("single-unknown-mask bound should clear the 5% gate for current parameters")
    if report.get("empirical_stress_still_required") is not True:
        errors.append("report must keep empirical stress testing as required")
    return errors


def build_report(b8_report: dict, gate_report: dict) -> dict:
    samples = int(b8_report["sample_count"])
    tolerance = float(b8_report["tolerance"])
    # B4/B8 tasks use honest_bias 0.34 for 12/16 qubits and 0.30 for 20 qubits.
    # The lemma uses the minimum signal to avoid cherry-picking the strongest task.
    minimum_honest_signal = 0.30
    signal_gap = minimum_honest_signal - tolerance
    single_bound = hoeffding_single_mask_bound(samples, signal_gap)
    high_rows = high_leakage_summary(b8_report, float(gate_report["high_leakage_fraction"]))
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T2 restricted refresh-independence soundness lemma",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "restricted_soundness_lemma_proved_under_refresh_independence_model",
        "method": "b10_t2_restricted_soundness_lemma_v0",
        "source_target_id": "B10-T2",
        "source_target_name": "sampling_advantage_verification_layer_target",
        "source_gate": gate_report.get("method"),
        "source_b8_stress": b8_report.get("method"),
        "dependency_benchmark": "B8",
        "explicit_not_bqp_separation": True,
        "hardware_randomized_measurement_circuits_instantiated": False,
        "sampling_hardness_proved": False,
        "empirical_stress_still_required": True,
        "theorem_count": 1,
        "corollary_count": 1,
        "sample_count": samples,
        "invariant_count": b8_report.get("invariant_count"),
        "tolerance": tolerance,
        "minimum_honest_signal": minimum_honest_signal,
        "signal_gap": signal_gap,
        "single_unknown_mask_soundness_bound": single_bound,
        "three_independent_unknown_masks_soundness_bound": hoeffding_independent_masks_bound(samples, signal_gap, 3),
        "ten_independent_unknown_masks_soundness_bound": hoeffding_independent_masks_bound(samples, signal_gap, 10),
        "high_leakage_summary_from_b8": high_rows,
        "theorem": {
            "id": "B10-T2-L1",
            "name": "refresh_independence_hidden_predicate_soundness_bound",
            "type": "restricted_soundness_lemma",
            "statement": (
                "In the declared transcript model, suppose challenge refresh or projection rotation "
                "leaves at least one verifier predicate unknown and statistically independent of the "
                "adversary's generated transcript after bounded leakage. If the honest verifier "
                "expects parity mean at least mu and accepts within tolerance tau < mu using N "
                "independent samples, then any adversary whose transcript is unbiased on that unknown "
                "predicate passes that predicate with probability at most exp(-N(mu-tau)^2/2)."
            ),
            "assumptions": [
                "The leakage channel is bounded leakage: it may reveal public parameters and a declared subset of predicates, but at least one tested predicate remains hidden.",
                "The challenge-refresh schedule provides refresh independence: the remaining unknown predicate is sampled after, or independently of, the adversary's transcript-generation strategy.",
                "For every unknown predicate, the adversary's generated samples have parity mean 0 conditional on the leaked transcript.",
                "Verifier samples are independent enough for a Hoeffding tail bound at the tested predicate.",
                "The honest signal gap mu - tau is positive and all verifier runtime/sample costs are included separately.",
            ],
            "proof_sketch": [
                "Condition on the complete leaked transcript and all public verifier parameters.",
                "For one refreshed unknown predicate, the adversary's parity variables are bounded in [-1, 1] with conditional mean 0.",
                "Acceptance on that predicate requires the empirical parity mean to deviate upward by at least mu - tau.",
                "Hoeffding's inequality gives probability at most exp(-N(mu-tau)^2/2) for that deviation.",
                "If several unknown predicates are independently refreshed, multiply the one-predicate bound under the declared independence assumption; otherwise keep the single-predicate bound only.",
            ],
            "status": "proved_under_refresh_independence_model_not_cryptographic_soundness",
        },
        "corollary": {
            "id": "B10-T2-C1",
            "name": "current_proxy_parameters_clear_five_percent_if_one_predicate_remains_unknown",
            "statement": (
                "With N=4096 verifier samples, minimum honest signal mu=0.30, and tolerance tau=0.08, "
                "the single-refreshed-predicate bound is below the 5% soundness gate."
            ),
            "computed_bound": single_bound,
            "status": "parameterized_corollary_for_current_proxy_only",
        },
        "validation_claim": {
            "admissible_claim": (
                "B10-T2 has a restricted, conditional verifier-soundness lemma when refresh independence "
                "guarantees at least one hidden predicate unknown to the adversary."
            ),
            "rejected_claim": (
                "This proves a hardware-verifier protocol, cryptographic soundness, sampling hardness, "
                "or a BQP/classical separation."
            ),
            "operational_rule": (
                "A verifier claim may cite this lemma only if it declares the leakage channel, proves at "
                "least one refreshed predicate remains unknown, and reports verifier sample overhead."
            ),
        },
        "remaining_obligations": [
            {
                "id": "B10-T2-R1",
                "status": "open",
                "description": "Instantiate a hardware-executable randomized-measurement verifier whose transcript actually satisfies refresh independence.",
            },
            {
                "id": "B10-T2-R2",
                "status": "open",
                "description": "Replace the empirical CNOT hidden-projection proxy with a distribution family tied to a sampling-hardness assumption.",
            },
            {
                "id": "B10-T2-R3",
                "status": "open",
                "description": "Stress unrestricted learned/generative adversaries against the formal leakage channel, not only side-channel candidate masks.",
            },
            {
                "id": "B10-T2-R4",
                "status": "open",
                "description": "Account for verifier overhead so the refresh schedule does not erase the claimed advantage denominator.",
            },
        ],
        "limits": [
            "This is a restricted conditional lemma, not a cryptographic verification theorem.",
            "The proof covers only the case where at least one tested predicate remains hidden and independent after leakage.",
            "The empirical B8 rows are still required to catch full-cover leakage cases such as no-refresh high leakage.",
            "The result does not prove sampling hardness, hardware feasibility, or BQP versus classical separation.",
        ],
        "result_dependency": {
            "b8_result_path": "results/B8_generative_spoofer_refresh_v0.json",
            "gate_result_path": "results/B10_t2_refresh_proof_obligation_gate_v0.json",
        },
    }
    report["validation_errors"] = validate_report(report)
    return report


def markdown(report: dict) -> str:
    theorem = report["theorem"]
    corollary = report["corollary"]
    lines = [
        "# B10-T2 Restricted Refresh-Independence Soundness Lemma v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']} / {report['source_target_name']}",
        f"- Method: {report['method']}",
        f"- Source gate: {report['source_gate']}",
        f"- Source B8 stress: {report['source_b8_stress']}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        f"- Hardware randomized-measurement circuits instantiated: {report['hardware_randomized_measurement_circuits_instantiated']}",
        f"- Sampling hardness proved: {report['sampling_hardness_proved']}",
        f"- Verifier samples: {report['sample_count']}",
        f"- Minimum honest signal: {report['minimum_honest_signal']:.3f}",
        f"- Tolerance: {report['tolerance']:.3f}",
        f"- Signal gap: {report['signal_gap']:.3f}",
        f"- Single-unknown-mask bound: {report['single_unknown_mask_soundness_bound']:.3e}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Validation Claim",
        "",
        f"- Admissible claim: {report['validation_claim']['admissible_claim']}",
        f"- Rejected claim: {report['validation_claim']['rejected_claim']}",
        f"- Operational rule: {report['validation_claim']['operational_rule']}",
        "",
        f"## {theorem['id']}: {theorem['name']}",
        "",
        f"- Type: {theorem['type']}",
        f"- Status: {theorem['status']}",
        f"- Statement: {theorem['statement']}",
        "",
        "### Assumptions",
        "",
    ]
    lines.extend(f"- {item}" for item in theorem["assumptions"])
    lines.extend(["", "### Proof Sketch", ""])
    lines.extend(f"- {item}" for item in theorem["proof_sketch"])
    lines.extend(
        [
            "",
            f"## {corollary['id']}: {corollary['name']}",
            "",
            f"- Statement: {corollary['statement']}",
            f"- Computed bound: {corollary['computed_bound']:.3e}",
            f"- Status: {corollary['status']}",
            "",
            "## High-Leakage Empirical Boundary From B8",
            "",
            "| refresh mode | max learned soundness | mean learned soundness | learners over 5% |",
            "|---|---:|---:|---|",
        ]
    )
    for row in report["high_leakage_summary_from_b8"]:
        learners = ", ".join(row.get("learners_over_5pct_soundness", [])) or "none"
        lines.append(
            f"| {row['refresh_mode']} | {row['max_learned_soundness']:.3f} | "
            f"{row['mean_learned_soundness']:.3f} | {learners} |"
        )
    lines.extend(["", "## Remaining Obligations", ""])
    for item in report["remaining_obligations"]:
        lines.append(f"- {item['id']} ({item['status']}): {item['description']}")
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--b8-result", type=Path, default=Path("results/B8_generative_spoofer_refresh_v0.json"))
    parser.add_argument("--gate-result", type=Path, default=Path("results/B10_t2_refresh_proof_obligation_gate_v0.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t2_restricted_soundness_lemma_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t2_restricted_soundness_lemma.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(load_json(args.b8_result), load_json(args.gate_result))
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "single_unknown_mask_soundness_bound": report["single_unknown_mask_soundness_bound"],
                    "theorem_count": report["theorem_count"],
                    "corollary_count": report["corollary_count"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
