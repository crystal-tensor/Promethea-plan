#!/usr/bin/env python3
"""Extract a finite-instance B9 failed gap-amplification negative lemma."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def row_id(row: dict) -> str:
    return f"{row['model']}:{row['qubits']}q:{row['transformation']}"


def select_rows(source: dict, raw_gap_threshold: float, normalized_gap_threshold: float) -> dict:
    rows = source["results"]
    local_rows = [row for row in rows if int(row["locality_max"]) <= 3]
    local_pass_rows = [row for row in local_rows if bool(row["candidate_passes_screen"])]
    strict_width_traps = [
        row
        for row in local_rows
        if row["gap_ratio"] is not None
        and float(row["gap_ratio"]) > raw_gap_threshold
        and float(row["normalized_gap_ratio"]) < 1.0
    ]
    tolerance_width_traps = [
        row
        for row in local_rows
        if row["gap_ratio"] is not None
        and float(row["gap_ratio"]) > raw_gap_threshold
        and float(row["normalized_gap_ratio"]) < normalized_gap_threshold
    ]
    dense_locality_traps = [
        row
        for row in rows
        if row["transformation"] == "shifted_square_spectral_filter_v0"
        and row["gap_ratio"] is not None
        and float(row["gap_ratio"]) > raw_gap_threshold
        and int(row["locality_max"]) > 3
    ]
    return {
        "local_rows": local_rows,
        "local_pass_rows": local_pass_rows,
        "strict_width_traps": strict_width_traps,
        "tolerance_width_traps": tolerance_width_traps,
        "dense_locality_traps": dense_locality_traps,
    }


def summarize_counterexample(row: dict) -> dict:
    return {
        "case_id": row_id(row),
        "model": row["model"],
        "qubits": row["qubits"],
        "transformation": row["transformation"],
        "locality_max": row["locality_max"],
        "baseline_gap": row["baseline_gap"],
        "baseline_normalized_gap": row["baseline_normalized_gap"],
        "gap_ratio": row["gap_ratio"],
        "normalized_gap_ratio": row["normalized_gap_ratio"],
        "ground_state_overlap": row["ground_state_overlap"],
        "candidate_passes_screen": row["candidate_passes_screen"],
    }


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "finite_instance_negative_gap_amplification_lemma_not_quantum_pcp_proof":
        errors.append("status must identify finite-instance negative lemma and not Quantum PCP proof")
    if report.get("source_benchmark_id") != "B9":
        errors.append("source benchmark must be B9")
    if report.get("source_method") != "small_local_hamiltonian_gap_lab_v0":
        errors.append("source method mismatch")
    if report.get("theorem_count") != 1:
        errors.append("report should contain one finite-instance negative lemma")
    if int(report.get("strict_counterexample_count", 0)) < 4:
        errors.append("strict counterexample count should preserve the four source candidates")
    if int(report.get("local_candidate_pass_count", 1)) != 0:
        errors.append("local candidate pass count should remain zero")
    if int(report.get("dense_locality_trap_count", 0)) < 3:
        errors.append("dense locality traps should be recorded")
    if report.get("explicit_not_quantum_pcp_proof") is not True:
        errors.append("report must explicitly avoid Quantum PCP proof claims")
    if report.get("global_gap_amplification_impossibility_claimed") is not False:
        errors.append("report must not claim global impossibility")
    if report.get("proof_assistant_formalized") is not False:
        errors.append("proof assistant formalization should remain open")
    if len(report.get("validation_errors", [])) != 0:
        errors.append("nested validation errors should be empty before finalization")
    return errors


def run(source_path: Path, raw_gap_threshold: float, normalized_gap_threshold: float) -> dict:
    source = load_json(source_path)
    selected = select_rows(source, raw_gap_threshold, normalized_gap_threshold)
    strict_counterexamples = [summarize_counterexample(row) for row in selected["strict_width_traps"]]
    tolerance_counterexamples = [summarize_counterexample(row) for row in selected["tolerance_width_traps"]]
    dense_locality_traps = [summarize_counterexample(row) for row in selected["dense_locality_traps"]]

    report = {
        "benchmark_id": "B9",
        "problem_id": 17,
        "title": "B9 failed gap-amplification negative lemma",
        "version": "0.1",
        "last_updated": "2026-06-17",
        "status": "finite_instance_negative_gap_amplification_lemma_not_quantum_pcp_proof",
        "method": "b9_failed_gap_amplification_negative_lemma_v0",
        "source_benchmark_id": source.get("benchmark_id"),
        "source_method": source.get("method"),
        "source_model_status": source.get("model_status"),
        "source_result": str(source_path),
        "theorem_count": 1,
        "lemma_name": "raw_gap_amplification_is_not_a_local_normalized_gap_amplification_certificate",
        "lemma_scope": "finite_exact_diagonalization_screen_for_b9_v0_models_and_transformations",
        "lemma_statement": (
            "In the B9 v0 exact small-instance screen, a transformation is not accepted as a "
            "gap-amplification proof step merely because the raw spectral gap increases. It must "
            "also preserve locality, maintain the tracked ground-space overlap, and improve the "
            "normalized gap. The tested locality-preserving reweighting family has zero accepted "
            "rows; several rows increase raw gap while failing normalized-gap improvement."
        ),
        "screen_conditions": {
            "locality_max_at_most": 3,
            "ground_state_overlap_at_least": 0.95,
            "normalized_gap_ratio_required": normalized_gap_threshold,
            "raw_gap_counterexample_threshold": raw_gap_threshold,
        },
        "configuration_count": source.get("configuration_count"),
        "locality_preserving_candidate_count": len(selected["local_rows"]),
        "local_candidate_pass_count": len(selected["local_pass_rows"]),
        "strict_counterexample_count": len(strict_counterexamples),
        "tolerance_counterexample_count": len(tolerance_counterexamples),
        "dense_locality_trap_count": len(dense_locality_traps),
        "max_local_candidate_normalized_gap_ratio": source.get("max_local_candidate_normalized_gap_ratio"),
        "max_dense_filter_gap_ratio": source.get("max_dense_filter_gap_ratio"),
        "strict_counterexamples": strict_counterexamples,
        "tolerance_counterexamples": tolerance_counterexamples,
        "dense_locality_traps": dense_locality_traps,
        "proof_obligations": [
            "Replace finite exact-diagonalization evidence with a symbolic statement over a named Hamiltonian family.",
            "Track spectral-width growth analytically, not only raw spectral gap.",
            "Prove locality preservation term-by-term after any transformation.",
            "Bound ground-space perturbation or specify the acceptable promise gap model.",
            "Separate dense spectral filters from local Hamiltonian transformations before invoking PCP-style intuition.",
        ],
        "explicit_not_quantum_pcp_proof": True,
        "global_gap_amplification_impossibility_claimed": False,
        "proof_assistant_formalized": False,
        "limits": [
            "Finite-instance negative lemma only; it covers the v0 model/transform screen and not all gap-amplification strategies.",
            "The local reweighting family is a toy probe, not a complete family of locality-preserving transformations.",
            "Dense shifted-square filters are recorded as locality traps, not as valid local-Hamiltonian proof steps.",
            "No Quantum PCP theorem, NLTS theorem, or global no-go theorem is claimed.",
        ],
    }
    report["validation_errors"] = validate_report({**report, "validation_errors": []})
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B9 Failed Gap-Amplification Negative Lemma v0.1",
        "",
        "Last updated: 2026-06-17",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Finite-Instance Lemma",
        "",
        f"**Name:** `{report['lemma_name']}`",
        "",
        report["lemma_statement"],
        "",
        "This is a finite exact-diagonalization negative lemma for the current B9 v0 screen. It is useful because it prevents a common overclaim: raw spectral-gap growth alone is not a local-Hamiltonian gap-amplification certificate.",
        "",
        "## Summary",
        "",
        f"- Source method: {report['source_method']}",
        f"- Configurations: {report['configuration_count']}",
        f"- Locality-preserving candidates: {report['locality_preserving_candidate_count']}",
        f"- Local candidate passes: {report['local_candidate_pass_count']}",
        f"- Strict counterexamples: {report['strict_counterexample_count']}",
        f"- Tolerance counterexamples: {report['tolerance_counterexample_count']}",
        f"- Dense locality traps: {report['dense_locality_trap_count']}",
        f"- Max local normalized-gap ratio: {report['max_local_candidate_normalized_gap_ratio']}",
        f"- Max dense-filter raw gap ratio: {report['max_dense_filter_gap_ratio']}",
        f"- Explicitly not Quantum PCP proof: {report['explicit_not_quantum_pcp_proof']}",
        f"- Global impossibility claimed: {report['global_gap_amplification_impossibility_claimed']}",
        f"- Proof assistant formalized: {report['proof_assistant_formalized']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Strict Counterexamples",
        "",
        "| case | locality | gap ratio | normalized-gap ratio | overlap | accepted |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["strict_counterexamples"]:
        lines.append(
            f"| {row['case_id']} | {row['locality_max']} | {row['gap_ratio']:.6f} | "
            f"{row['normalized_gap_ratio']:.6f} | {row['ground_state_overlap']:.6f} | "
            f"{row['candidate_passes_screen']} |"
        )
    lines.extend(
        [
            "",
            "## Dense Locality Traps",
            "",
            "| case | locality | gap ratio | normalized-gap ratio | overlap |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["dense_locality_traps"]:
        lines.append(
            f"| {row['case_id']} | {row['locality_max']} | {row['gap_ratio']:.6f} | "
            f"{row['normalized_gap_ratio']:.6f} | {row['ground_state_overlap']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Proof Obligations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["proof_obligations"])
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Supported: a reusable finite-instance failed-proof record for naive gap amplification in the B9 v0 screen.",
            "- Not supported: a Quantum PCP proof, an NLTS theorem, a local-Hamiltonian hardness theorem, or a global impossibility theorem for gap amplification.",
            "",
            "## Limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("results/B9_local_hamiltonian_gap_lab_v0.json"))
    parser.add_argument("--raw-gap-threshold", type=float, default=1.05)
    parser.add_argument("--normalized-gap-threshold", type=float, default=1.05)
    parser.add_argument("--json-output", type=Path, default=Path("results/B9_failed_gap_amplification_lemma_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B9_failed_gap_amplification_lemma.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = run(
        source_path=args.source,
        raw_gap_threshold=args.raw_gap_threshold,
        normalized_gap_threshold=args.normalized_gap_threshold,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "local_candidate_pass_count": report["local_candidate_pass_count"],
                    "strict_counterexample_count": report["strict_counterexample_count"],
                    "dense_locality_trap_count": report["dense_locality_trap_count"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 1 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
