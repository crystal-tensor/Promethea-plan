#!/usr/bin/env python3
"""Extract the B2 reduced-round small-distance/aggressive artifact boundary."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def improved_rows(payload: dict) -> list[dict]:
    return [row for row in payload.get("comparisons", []) if row.get("improved_volume")]


def counter_to_plain(counter: Counter) -> dict[str, int]:
    return {str(key): value for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def summarize_improvements(rows: list[dict]) -> dict:
    variants = Counter(row.get("candidate_variant") for row in rows)
    distance_pairs = Counter((row.get("baseline_distance"), row.get("candidate_distance")) for row in rows)
    candidate_distances = Counter(row.get("candidate_distance") for row in rows)
    candidate_rounds = Counter((row.get("candidate_row") or {}).get("rounds") for row in rows)
    targets = Counter(row.get("target_logical_error") for row in rows)
    physical_errors = Counter(row.get("physical_error") for row in rows)
    memory_bases = Counter(row.get("memory_basis") for row in rows)
    aggressive_count = sum(count for variant, count in variants.items() if variant and "aggressive_round" in variant)
    non_aggressive_count = len(rows) - aggressive_count
    return {
        "improved_volume_count": len(rows),
        "aggressive_improved_volume_count": aggressive_count,
        "non_aggressive_improved_volume_count": non_aggressive_count,
        "variant_counts": counter_to_plain(variants),
        "distance_pair_counts": counter_to_plain(distance_pairs),
        "candidate_distance_counts": counter_to_plain(candidate_distances),
        "candidate_round_counts": counter_to_plain(candidate_rounds),
        "target_counts": counter_to_plain(targets),
        "physical_error_counts": counter_to_plain(physical_errors),
        "memory_basis_counts": counter_to_plain(memory_bases),
        "all_improvements_are_aggressive": bool(rows and non_aggressive_count == 0),
        "all_improvements_at_min_distance_3": bool(rows and set(candidate_distances) == {3}),
        "all_improvements_at_one_round": bool(rows and set(candidate_rounds) == {1}),
    }


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "reduced_round_small_distance_aggressive_artifact_boundary":
        errors.append("status must identify the reduced-round result as an artifact boundary")
    if report.get("method") != "b2_reduced_round_artifact_boundary_v0":
        errors.append("method mismatch")
    if report.get("non_aggressive_mechanism_survives") is not False:
        errors.append("non-aggressive mechanism should not be marked as surviving")
    if report.get("small_distance_artifact_flag") is not True:
        errors.append("small-distance artifact flag should be true")
    if report.get("aggressive_schedule_dependency_flag") is not True:
        errors.append("aggressive schedule dependency should be true")
    if report.get("candidate_positive_rows", {}).get("improved_volume_count") != 22:
        errors.append("candidate positive row count should remain 22")
    if report.get("robustness_positive_rows", {}).get("improved_volume_count") != 88:
        errors.append("robustness positive row count should remain 88")
    if report.get("robustness_positive_rows", {}).get("non_aggressive_improved_volume_count") != 0:
        errors.append("robustness should have zero non-aggressive improved rows")
    if report.get("robustness_positive_rows", {}).get("all_improvements_at_min_distance_3") is not True:
        errors.append("robustness improvements should be confined to distance 3")
    if report.get("robustness_positive_rows", {}).get("all_improvements_at_one_round") is not True:
        errors.append("robustness improvements should be confined to one-round candidates")
    if report.get("new_code_claimed") is not False:
        errors.append("must not claim a new code")
    if report.get("threshold_claimed") is not False:
        errors.append("must not claim a threshold result")
    if report.get("calibrated_device_claimed") is not False:
        errors.append("must not claim calibrated device evidence")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def run(candidate_path: Path, robustness_path: Path) -> dict:
    candidate = load_json(candidate_path)
    robustness = load_json(robustness_path)
    candidate_summary = summarize_improvements(improved_rows(candidate))
    robustness_summary = summarize_improvements(improved_rows(robustness))
    report = {
        "benchmark_id": "B2",
        "problem_id": 22,
        "title": "B2 reduced-round small-distance/aggressive artifact boundary",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "reduced_round_small_distance_aggressive_artifact_boundary",
        "method": "b2_reduced_round_artifact_boundary_v0",
        "source_candidate": str(candidate_path),
        "source_candidate_method": candidate.get("method"),
        "source_robustness": str(robustness_path),
        "source_robustness_method": robustness.get("method"),
        "criterion": robustness.get("criterion") or candidate.get("criterion"),
        "candidate_positive_rows": candidate_summary,
        "robustness_positive_rows": robustness_summary,
        "non_aggressive_mechanism_survives": False,
        "small_distance_artifact_flag": robustness_summary["all_improvements_at_min_distance_3"],
        "aggressive_schedule_dependency_flag": robustness_summary["all_improvements_are_aggressive"],
        "one_round_candidate_dependency_flag": robustness_summary["all_improvements_at_one_round"],
        "artifact_boundary_statement": (
            "The current reduced-round B2 signal is a useful diagnostic but should be treated as a "
            "small-distance aggressive-schedule artifact: all 22 original volume-positive rows and all "
            "88 stress-preserved rows are aggressive, distance-3, one-round candidates, while the "
            "non-aggressive reduced-round mechanism has zero volume-improved rows under robustness stress."
        ),
        "decision": "close_T_B2_002_as_artifact_boundary_until_new_non_aggressive_mechanism_exists",
        "next_steps": [
            "Do not use the aggressive d-4 one-round signal as a low-overhead QEC claim.",
            "Open a new task only for a different mechanism: non-aggressive schedule, different code family, leakage-aware circuit model, or larger-distance validated decoder improvement.",
            "If the reduced-round idea is revisited, require distance 5/7 positive rows and non-aggressive volume improvement under noise mismatch before promoting it.",
        ],
        "new_code_claimed": False,
        "threshold_claimed": False,
        "calibrated_device_claimed": False,
        "claim_boundary": [
            "Supported: finite-shot evidence that the current reduced-round lever does not survive as a non-aggressive volume-reducing mechanism.",
            "Supported: an explicit boundary that all preserved volume-positive rows are distance-3 one-round aggressive schedules.",
            "Not supported: a new quantum code, threshold theorem, calibrated-device schedule, or scalable low-overhead QEC solution.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def markdown(report: dict) -> str:
    candidate = report["candidate_positive_rows"]
    robustness = report["robustness_positive_rows"]
    lines = [
        "# B2 Reduced-Round Artifact Boundary v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Criterion: {report['criterion']}",
        f"- Candidate positive rows: {candidate['improved_volume_count']}",
        f"- Robustness positive rows: {robustness['improved_volume_count']}",
        f"- Robust non-aggressive improved rows: {robustness['non_aggressive_improved_volume_count']}",
        f"- All robustness improvements aggressive: {robustness['all_improvements_are_aggressive']}",
        f"- All robustness improvements at distance 3: {robustness['all_improvements_at_min_distance_3']}",
        f"- All robustness improvements at one candidate round: {robustness['all_improvements_at_one_round']}",
        f"- Non-aggressive mechanism survives: {report['non_aggressive_mechanism_survives']}",
        f"- New code / threshold / calibrated device claimed: {report['new_code_claimed']} / {report['threshold_claimed']} / {report['calibrated_device_claimed']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Boundary Statement",
        "",
        report["artifact_boundary_statement"],
        "",
        "## Candidate Positive Rows",
        "",
        f"- Variant counts: {candidate['variant_counts']}",
        f"- Candidate distance counts: {candidate['candidate_distance_counts']}",
        f"- Candidate round counts: {candidate['candidate_round_counts']}",
        f"- Target counts: {candidate['target_counts']}",
        "",
        "## Robustness Positive Rows",
        "",
        f"- Variant counts: {robustness['variant_counts']}",
        f"- Candidate distance counts: {robustness['candidate_distance_counts']}",
        f"- Candidate round counts: {robustness['candidate_round_counts']}",
        f"- Target counts: {robustness['target_counts']}",
        "",
        "## Decision",
        "",
        report["decision"],
        "",
        "## Claim Boundary",
        "",
    ]
    lines.extend(f"- {item}" for item in report["claim_boundary"])
    lines.extend(["", "## Next Steps", ""])
    lines.extend(f"- {item}" for item in report["next_steps"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=Path("results/B2_same_hardware_schedule_candidate_v0.json"))
    parser.add_argument("--robustness", type=Path, default=Path("results/B2_same_hardware_schedule_robustness_v0.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B2_reduced_round_artifact_boundary_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B2_reduced_round_artifact_boundary.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(args.candidate, args.robustness)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "candidate_improved": report["candidate_positive_rows"]["improved_volume_count"],
                    "robustness_improved": report["robustness_positive_rows"]["improved_volume_count"],
                    "robustness_non_aggressive": report["robustness_positive_rows"][
                        "non_aggressive_improved_volume_count"
                    ],
                    "small_distance_artifact_flag": report["small_distance_artifact_flag"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
