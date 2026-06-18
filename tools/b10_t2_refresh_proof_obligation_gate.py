#!/usr/bin/env python3
"""Build the B10-T2 refresh proof-obligation gate from the B8 spoofer stress."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SOUNDNESS_GATE = 0.05
COMPLETENESS_GATE = 0.95
HIGH_LEAKAGE_FRACTION = 0.75


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def target_by_id(formal_targets: dict, target_id: str) -> dict:
    for target in formal_targets.get("targets", []):
        if target.get("id") == target_id:
            return target
    raise ValueError(f"{formal_targets.get('title', 'formal targets')} has no {target_id}")


def mode_summary(b8_report: dict, leakage_fraction: float) -> list[dict]:
    rows = [
        row
        for row in b8_report.get("summary_by_mode", [])
        if float(row.get("leakage_fraction", -1.0)) == leakage_fraction
    ]
    return sorted(rows, key=lambda row: str(row["refresh_mode"]))


def worst_rows(b8_report: dict, limit: int = 8) -> list[dict]:
    rows = sorted(
        b8_report.get("results", []),
        key=lambda row: (
            float(row.get("learned_soundness", 0.0)),
            float(row.get("mean_true_masks_selected", 0.0)),
        ),
        reverse=True,
    )
    return rows[:limit]


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "proof_obligation_gate_proxy_supports_rejection_rule_not_soundness_lemma":
        errors.append("status must remain a proof-obligation gate, not a proved soundness lemma")
    if report.get("source_target_id") != "B10-T2":
        errors.append("source_target_id must be B10-T2")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("report must explicitly avoid BQP separation claims")
    if report.get("lemma_status") != "not_proved_proxy_insufficient_for_general_soundness":
        errors.append("lemma_status must state that the proxy is insufficient for a general soundness proof")
    if report.get("validation_claim", {}).get("rejected_claim") in (None, ""):
        errors.append("report must include a rejected claim")
    if report.get("validation_claim", {}).get("admissible_next_claim") in (None, ""):
        errors.append("report must include an admissible next claim")
    if not report.get("proof_obligations") or len(report["proof_obligations"]) < 6:
        errors.append("report must include at least six proof obligations")
    if "none" not in report.get("unsafe_high_leakage_refresh_modes", []):
        errors.append("no-refresh mode should remain unsafe at high leakage")
    safe_modes = set(report.get("safe_high_leakage_refresh_modes", []))
    required_safe = {"projection_rotation", "challenge_refresh", "refresh_plus_rotation"}
    if not required_safe <= safe_modes:
        errors.append("safe high-leakage modes must include projection rotation and challenge refresh variants")
    if float(report.get("maximum_learned_soundness", 0.0)) <= SOUNDNESS_GATE:
        errors.append("maximum learned soundness should expose at least one unsafe adversarial mode")
    if float(report.get("minimum_honest_completeness", 0.0)) < COMPLETENESS_GATE:
        errors.append("honest completeness is below the gate")
    if report.get("hardware_randomized_measurement_circuits_instantiated") is not False:
        errors.append("report must not imply hardware randomized-measurement circuits are instantiated")
    return errors


def build_report(b8_report: dict, formal_targets: dict) -> dict:
    target = target_by_id(formal_targets, "B10-T2")
    high_leakage_rows = mode_summary(b8_report, HIGH_LEAKAGE_FRACTION)
    safe_modes = [
        row["refresh_mode"]
        for row in high_leakage_rows
        if float(row.get("max_learned_soundness", 1.0)) <= SOUNDNESS_GATE
    ]
    unsafe_modes = [
        row["refresh_mode"]
        for row in high_leakage_rows
        if float(row.get("max_learned_soundness", 0.0)) > SOUNDNESS_GATE
    ]
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T2 refresh proof-obligation gate",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "proof_obligation_gate_proxy_supports_rejection_rule_not_soundness_lemma",
        "method": "b10_t2_refresh_proof_obligation_gate_v0",
        "source_target_id": "B10-T2",
        "source_target_name": target.get("name"),
        "source_formal_target": "B10_formal_theorem_targets_v0",
        "source_b8_stress": b8_report.get("method"),
        "dependency_benchmark": "B8",
        "explicit_not_bqp_separation": True,
        "lemma_status": "not_proved_proxy_insufficient_for_general_soundness",
        "soundness_gate": SOUNDNESS_GATE,
        "completeness_gate": COMPLETENESS_GATE,
        "high_leakage_fraction": HIGH_LEAKAGE_FRACTION,
        "configuration_count": b8_report.get("configuration_count"),
        "task_count": b8_report.get("task_count"),
        "learners_tested": b8_report.get("learners_tested"),
        "minimum_honest_completeness": b8_report.get("minimum_honest_completeness"),
        "maximum_learned_soundness": b8_report.get("maximum_learned_soundness"),
        "safe_high_leakage_refresh_modes": safe_modes,
        "unsafe_high_leakage_refresh_modes": unsafe_modes,
        "high_leakage_summary": high_leakage_rows,
        "worst_learned_rows": worst_rows(b8_report),
        "validation_claim": {
            "rejected_claim": (
                "A B10-T2 sampling-advantage verification layer with fixed hidden projections, "
                "no challenge refresh, and lambda=0.75 leakage can claim soundness <= 0.05."
            ),
            "supported_rejection_rule": (
                "Reject no-refresh verifier claims at lambda=0.75 in this CNOT hidden-projection "
                "proxy, because trained/generative spoofers reach learned soundness 1.0."
            ),
            "admissible_next_claim": (
                "A restricted soundness lemma may be attempted only after projection rotation or "
                "challenge refresh is formalized as an unpredictable post-sampling challenge with "
                "a declared leakage channel and asymptotic adversary model."
            ),
        },
        "candidate_lemma_schema": {
            "name": "minimum_refresh_soundness_gate_for_hidden_projection_verifiers",
            "not_yet_proved_statement": (
                "For a sampling verifier with independent projection rotation or challenge refresh, "
                "bounded leakage lambda, and adversaries limited to the declared transcript model, "
                "adaptive-spoofer pass probability is at most s(lambda, m, N) below the declared "
                "soundness gate while honest completeness stays above c."
            ),
            "why_current_proxy_is_insufficient": [
                "The B8 task uses finite CNOT hidden-projection proxies rather than a hardware randomized-measurement circuit family.",
                "Candidate true masks are exposed through a side-channel quality model, not derived from unrestricted transcript access.",
                "The adversary class is empirical and finite, not an asymptotic or cryptographic adaptive adversary model.",
                "The refresh operations are modeled as projection rotation/challenge reset effects, not yet as a fully specified verifier protocol with seed timing and transcript distribution.",
                "The stress result has strong negative evidence for no-refresh high leakage, but finite positive rows do not prove universal soundness for every learner.",
            ],
        },
        "proof_obligations": [
            {
                "id": "B10-T2-O1",
                "status": "open",
                "description": "Define the verifier transcript distribution, seed timing, and challenge-refresh schedule as a formal protocol.",
            },
            {
                "id": "B10-T2-O2",
                "status": "open",
                "description": "Replace the side-channel candidate-mask model with a leakage channel L that maps transcripts to adversary information.",
            },
            {
                "id": "B10-T2-O3",
                "status": "open",
                "description": "State an adversary class with allowed computation, samples, adaptivity, and access to refreshed challenges.",
            },
            {
                "id": "B10-T2-O4",
                "status": "open",
                "description": "Prove or bound soundness as a function of leakage lambda, invariant count, verifier samples, and refresh entropy.",
            },
            {
                "id": "B10-T2-O5",
                "status": "open",
                "description": "Instantiate hardware-executable randomized-measurement circuits or clearly declare that the result remains a proxy.",
            },
            {
                "id": "B10-T2-O6",
                "status": "open",
                "description": "Separate the verifier soundness statement from the external sampling-hardness assumption used for advantage.",
            },
            {
                "id": "B10-T2-O7",
                "status": "open",
                "description": "Audit verifier overhead so refresh does not erase the claimed sampling-advantage denominator.",
            },
        ],
        "hardware_randomized_measurement_circuits_instantiated": False,
        "result_dependency": {
            "b8_result_path": "results/B8_generative_spoofer_refresh_v0.json",
            "formal_target_path": "results/B10_formal_theorem_targets_v0.json",
        },
        "limits": [
            "This gate is a proof-pressure artifact, not a cryptographic soundness proof.",
            "It supports a rejection rule for no-refresh high-leakage claims in the current proxy.",
            "It does not establish a BQP/classical separation or a universal verification theorem.",
            "It should be used to drive B4/B8 protocol formalization, not to advertise a solved B10 result.",
        ],
    }
    report["validation_errors"] = validate_report(report)
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B10-T2 Refresh Proof-Obligation Gate v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']} / {report['source_target_name']}",
        f"- Method: {report['method']}",
        f"- Source B8 stress: {report['source_b8_stress']}",
        f"- Lemma status: {report['lemma_status']}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        f"- Configurations: {report['configuration_count']}",
        f"- Minimum honest completeness: {report['minimum_honest_completeness']:.3f}",
        f"- Maximum learned soundness: {report['maximum_learned_soundness']:.3f}",
        f"- Soundness gate: {report['soundness_gate']:.2f}",
        f"- High leakage fraction: {report['high_leakage_fraction']:.2f}",
        f"- Safe high-leakage refresh modes: {report['safe_high_leakage_refresh_modes']}",
        f"- Unsafe high-leakage refresh modes: {report['unsafe_high_leakage_refresh_modes']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Validation Claim",
        "",
        f"- Rejected claim: {report['validation_claim']['rejected_claim']}",
        f"- Supported rejection rule: {report['validation_claim']['supported_rejection_rule']}",
        f"- Admissible next claim: {report['validation_claim']['admissible_next_claim']}",
        "",
        "## High-Leakage Refresh Boundary",
        "",
        "| refresh mode | max learned soundness | mean learned soundness | learners over 5% |",
        "|---|---:|---:|---|",
    ]
    for row in report["high_leakage_summary"]:
        learners = ", ".join(row.get("learners_over_5pct_soundness", [])) or "none"
        lines.append(
            f"| {row['refresh_mode']} | {row['max_learned_soundness']:.3f} | "
            f"{row['mean_learned_soundness']:.3f} | {learners} |"
        )
    schema = report["candidate_lemma_schema"]
    lines.extend(
        [
            "",
            "## Candidate Lemma Schema",
            "",
            f"- Name: {schema['name']}",
            f"- Not-yet-proved statement: {schema['not_yet_proved_statement']}",
            "",
            "### Why The Current Proxy Is Insufficient",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in schema["why_current_proxy_is_insufficient"])
    lines.extend(["", "## Proof Obligations", ""])
    for item in report["proof_obligations"]:
        lines.append(f"- {item['id']} ({item['status']}): {item['description']}")
    lines.extend(
        [
            "",
            "## Worst Learned Rows",
            "",
            "| task | mode | leakage | learner | soundness | true masks selected | mean max error |",
            "|---|---|---:|---|---:|---:|---:|",
        ]
    )
    for row in report["worst_learned_rows"]:
        lines.append(
            f"| {row['task_id']} | {row['refresh_mode']} | {row['leakage_fraction']:.2f} | "
            f"{row['learner']} | {row['learned_soundness']:.3f} | "
            f"{row['mean_true_masks_selected']:.2f} | {row['mean_max_abs_error']:.3f} |"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--b8-result", type=Path, default=Path("results/B8_generative_spoofer_refresh_v0.json"))
    parser.add_argument("--formal-targets", type=Path, default=Path("results/B10_formal_theorem_targets_v0.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t2_refresh_proof_obligation_gate_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t2_refresh_proof_obligation_gate.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(load_json(args.b8_result), load_json(args.formal_targets))
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "lemma_status": report["lemma_status"],
                    "validation_error_count": len(report["validation_errors"]),
                    "unsafe_high_leakage_refresh_modes": report["unsafe_high_leakage_refresh_modes"],
                    "safe_high_leakage_refresh_modes": report["safe_high_leakage_refresh_modes"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
