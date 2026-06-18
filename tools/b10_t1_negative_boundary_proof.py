#!/usr/bin/env python3
"""Build the B10-T1 HHL/data-loading negative-boundary proof attempt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


THEOREMS = [
    {
        "id": "B10-T1-L1",
        "name": "explicit_io_lower_bound_for_linear_system_claims",
        "type": "accounting_lower_bound",
        "statement": (
            "For an n-dimensional linear-system task with explicit matrix/vector input or "
            "full-vector output, any end-to-end algorithm in the explicit-I/O model has "
            "runtime at least Omega(C_input + C_prep + C_block + B_out), where C_input "
            "is the cost of ingesting the explicit instance, C_prep is the cost of "
            "preparing |b>, C_block is the cost of constructing or invoking the block "
            "encoding, and B_out is the number of output bits written or certified."
        ),
        "assumptions": [
            "The input matrix/vector is not a free oracle unless its construction cost is charged separately.",
            "The algorithm must either ingest the explicit instance or cite a prebuilt oracle/data structure with declared cost.",
            "The output medium must contain enough bits to represent the requested answer to the requested precision.",
            "Runtime accounting includes classical preprocessing, state preparation, block-encoding construction, quantum queries, and output writing.",
        ],
        "proof_sketch": [
            "Any algorithm that receives an explicit instance through a finite-bandwidth classical interface must spend at least C_input steps to ingest or construct the data structure it later queries.",
            "If the quantum routine uses |b> or a block encoding of A, the construction or invocation costs C_prep and C_block are part of the end-to-end algorithm unless they are explicitly delegated to a trusted external oracle.",
            "If the claimed output contains B_out bits, at least B_out bit-write or equivalent certification operations are necessary simply to emit the answer.",
            "These lower bounds are independent bottlenecks in the end-to-end contract, so the total runtime is at least their sum up to constant-factor machine-model choices.",
        ],
        "consequence": (
            "A polylog(n) quantum subroutine does not imply a polylog(n) end-to-end algorithm "
            "when explicit input loading, oracle construction, state preparation, or full-output "
            "readout is required."
        ),
        "status": "proved_under_explicit_io_model",
    },
    {
        "id": "B10-T1-C1",
        "name": "no_hidden_exponential_speedup_for_full_output_hhl",
        "type": "negative_boundary_corollary",
        "statement": (
            "If a linear-system advantage claim requests the full n-dimensional solution vector "
            "to b bits of precision, or uses explicit input whose preparation/block-encoding cost "
            "is Omega(n), then no end-to-end exponential speedup over input/output size can be "
            "claimed from an HHL-style polylogarithmic quantum subroutine alone."
        ),
        "assumptions": [
            "Full-vector output requires B_out = Omega(n b) output bits.",
            "Explicit input or oracle construction costs are charged rather than hidden.",
            "The comparison denominator is end-to-end runtime, not only quantum query complexity.",
        ],
        "proof_sketch": [
            "Apply B10-T1-L1 with B_out = Omega(n b) for full-vector output.",
            "Alternatively, apply B10-T1-L1 with C_input + C_prep + C_block = Omega(n) for explicit loading or block-encoding construction.",
            "Either condition gives an Omega(n) end-to-end lower bound, excluding a polylog(n) end-to-end exponential-speedup claim in that model.",
        ],
        "consequence": (
            "HHL-like claims remain admissible only for succinct or already-charged input access "
            "and small observable-output tasks, with condition number, precision, and classical "
            "baselines declared."
        ),
        "status": "proved_under_explicit_io_model",
    },
]


OPEN_OBLIGATIONS = [
    {
        "id": "B10-T1-O1",
        "description": "Source-back the machine model and lower-bound statement with literature references.",
        "status": "open_literature_linking",
    },
    {
        "id": "B10-T1-O2",
        "description": "Instantiate the denominator comparison against concrete classical sparse linear-system or observable-estimation baselines.",
        "status": "open_baseline_instantiation",
    },
    {
        "id": "B10-T1-O3",
        "description": "Extend the lemma from full-output/readout and explicit-loading accounting to dequantization-style low-rank or sampling-access regimes.",
        "status": "open_dequantization_boundary",
    },
]


def validate_report(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "negative_boundary_accounting_lemma_proved_under_explicit_io_model_not_bqp_separation":
        errors.append("status must be a restricted accounting lemma, not a BQP separation")
    if not report.get("explicit_not_bqp_separation"):
        errors.append("report must explicitly avoid claiming a BQP/classical separation")
    if report.get("source_target_id") != "B10-T1":
        errors.append("source_target_id must be B10-T1")
    if len(report.get("theorems", [])) < 2:
        errors.append("report should include at least one lemma and one corollary")
    for theorem in report.get("theorems", []):
        for field in ["id", "statement", "assumptions", "proof_sketch", "consequence", "status"]:
            if theorem.get(field) in (None, "", [], {}):
                errors.append(f"{theorem.get('id', '<unknown>')} missing {field}")
        if theorem.get("status") != "proved_under_explicit_io_model":
            errors.append(f"{theorem.get('id', '<unknown>')} must be restricted to explicit-I/O proof status")
    if report.get("claim_boundary", {}).get("admissible_claim") in (None, ""):
        errors.append("claim boundary should identify remaining admissible claim type")
    return errors


def build_report() -> dict:
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T1 HHL/data-loading negative-boundary proof attempt",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "negative_boundary_accounting_lemma_proved_under_explicit_io_model_not_bqp_separation",
        "method": "b10_t1_linear_systems_io_accounting_negative_boundary_v0",
        "source_target_id": "B10-T1",
        "source_target_name": "linear_systems_data_loading_negative_boundary",
        "explicit_not_bqp_separation": True,
        "proof_result": "restricted_negative_boundary_accounting_lemma",
        "theorem_count": len(THEOREMS),
        "open_obligation_count": len(OPEN_OBLIGATIONS),
        "theorems": THEOREMS,
        "claim_boundary": {
            "rejected_claim": "End-to-end exponential HHL-style speedup for explicit full-output linear-system tasks while hiding loading, block-encoding, state-preparation, or readout costs.",
            "admissible_claim": "Conditional quantum speedup for small observable outputs under succinct, prebuilt, or fully charged access models with kappa, epsilon, and classical baselines declared.",
            "next_proof_pressure": "Instantiate denominator baselines and source-backed assumptions for specific B3/B5 observable tasks.",
        },
        "open_obligations": OPEN_OBLIGATIONS,
        "limits": [
            "This is an accounting lower-bound lemma under an explicit-I/O model, not an unconditional BQP versus classical separation.",
            "It does not rule out HHL-style speedups for succinctly specified, oracle-access, or small-observable tasks when all access costs are honestly charged.",
            "It still needs source-backed citations and concrete classical denominator baselines before it can become a publishable theory note.",
        ],
    }
    report["validation_errors"] = validate_report(report)
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B10-T1 HHL/Data-Loading Negative-Boundary Proof Attempt v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']} / {report['source_target_name']}",
        f"- Method: {report['method']}",
        f"- Proof result: {report['proof_result']}",
        f"- Theorem/corollary count: {report['theorem_count']}",
        f"- Open obligations: {report['open_obligation_count']}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## Claim Boundary",
        "",
        f"- Rejected claim: {report['claim_boundary']['rejected_claim']}",
        f"- Admissible claim: {report['claim_boundary']['admissible_claim']}",
        f"- Next proof pressure: {report['claim_boundary']['next_proof_pressure']}",
        "",
    ]
    for theorem in report["theorems"]:
        lines.extend(
            [
                f"## {theorem['id']}: {theorem['name']}",
                "",
                f"- Type: {theorem['type']}",
                f"- Status: {theorem['status']}",
                f"- Statement: {theorem['statement']}",
                "",
                "### Assumptions",
                "",
            ]
        )
        lines.extend(f"- {item}" for item in theorem["assumptions"])
        lines.extend(["", "### Proof Sketch", ""])
        lines.extend(f"- {item}" for item in theorem["proof_sketch"])
        lines.extend(["", "### Consequence", "", f"- {theorem['consequence']}", ""])
    lines.extend(["## Open Obligations", ""])
    for item in report["open_obligations"]:
        lines.append(f"- {item['id']} ({item['status']}): {item['description']}")
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t1_negative_boundary_proof_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t1_negative_boundary_proof.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "proof_result": report["proof_result"],
                    "theorem_count": report["theorem_count"],
                    "open_obligation_count": report["open_obligation_count"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
