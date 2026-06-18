#!/usr/bin/env python3
"""Build a source-backed B10-T1 boundary note with denominator baselines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SOURCES = [
    {
        "id": "hhl_2009",
        "title": "Quantum algorithm for solving linear systems of equations",
        "authors": "Harrow, Hassidim, Lloyd",
        "year": 2009,
        "url": "https://arxiv.org/abs/0811.3171",
        "role": "canonical_quantum_linear_systems_claim",
        "supports": [
            "The HHL task is naturally a state or observable-estimation task, not a free full-vector-output task.",
            "The headline speedup depends on sparsity, conditioning, precision, and access assumptions.",
        ],
    },
    {
        "id": "childs_kothari_somma_2017",
        "title": "Quantum algorithm for systems of linear equations with exponentially improved dependence on precision",
        "authors": "Childs, Kothari, Somma",
        "year": 2017,
        "url": "https://arxiv.org/abs/1511.02306",
        "role": "improved_qlsa_precision_boundary",
        "supports": [
            "Modern QLSA improvements refine precision dependence while still outputting a solution state.",
            "Precision improvements do not remove state-preparation, oracle, block-encoding, or readout accounting.",
        ],
    },
    {
        "id": "tang_2019",
        "title": "A quantum-inspired classical algorithm for recommendation systems",
        "authors": "Tang",
        "year": 2019,
        "url": "https://arxiv.org/abs/1807.04271",
        "role": "dequantization_warning_for_sampling_access",
        "supports": [
            "Under strong sample/query input access, some claimed quantum machine-learning speedups can be classically matched up to polynomial factors.",
            "Sampling access is not a harmless implementation detail; it changes the fair classical denominator.",
        ],
    },
    {
        "id": "chia_lin_wang_2018",
        "title": "Quantum-inspired sublinear classical algorithms for solving low-rank linear systems",
        "authors": "Chia, Lin, Wang",
        "year": 2018,
        "url": "https://arxiv.org/abs/1811.04852",
        "role": "linear_systems_dequantization_boundary",
        "supports": [
            "Low-rank linear systems with sample/query access admit sublinear classical algorithms for samples or entries of the solution.",
            "A B10-T1 claim must separate explicit-I/O, succinct-oracle, and sampling-access regimes.",
        ],
    },
    {
        "id": "shewchuk_1994",
        "title": "An Introduction to the Conjugate Gradient Method Without the Agonizing Pain",
        "authors": "Shewchuk",
        "year": 1994,
        "url": "https://www.cs.cmu.edu/~quake-papers/painless-conjugate-gradient.pdf",
        "role": "classical_sparse_spd_baseline",
        "supports": [
            "Conjugate gradient is a standard denominator for sparse symmetric positive-definite systems.",
            "Iteration cost scales through sparse matrix-vector products and condition-dependent convergence.",
        ],
    },
    {
        "id": "paige_saunders_1982",
        "title": "LSQR: An algorithm for sparse linear equations and sparse least squares",
        "authors": "Paige, Saunders",
        "year": 1982,
        "url": "https://doi.org/10.1145/355984.355989",
        "role": "classical_general_sparse_least_squares_baseline",
        "supports": [
            "LSQR is a standard baseline for general sparse linear equations and least-squares instances.",
            "General sparse linear-system claims need a denominator beyond SPD-only conjugate gradient.",
        ],
    },
]


BASELINES = [
    {
        "id": "D1_explicit_spd_full_solution_cg",
        "task_regime": "Explicit sparse SPD A, explicit b, full solution vector requested.",
        "classical_denominator": "Conjugate gradient or preconditioned conjugate gradient.",
        "cost_shape": "O(nnz(A) * sqrt(kappa) * log(1/epsilon)) style matvec iteration accounting, plus Omega(n * bits) output writing for full x.",
        "quantum_claim_allowed": "No end-to-end exponential speedup claim unless input loading, block encoding, state preparation, and full readout are charged and still dominated.",
        "sources": ["shewchuk_1994", "hhl_2009"],
    },
    {
        "id": "D2_explicit_general_sparse_least_squares",
        "task_regime": "Explicit rectangular or nonsymmetric sparse linear equation / least-squares instance.",
        "classical_denominator": "LSQR or Krylov-family sparse iterative solvers.",
        "cost_shape": "O(iterations * nnz(A)) sparse multiply accounting, plus explicit output or certificate cost.",
        "quantum_claim_allowed": "Only compare observable or state-output QLSA claims after charging all access construction and readout costs.",
        "sources": ["paige_saunders_1982", "childs_kothari_somma_2017"],
    },
    {
        "id": "D3_succinct_oracle_small_observable",
        "task_regime": "Succinctly generated or prebuilt oracle/block-encoding with only a small observable required.",
        "classical_denominator": "Best known classical algorithm under the same succinct description or oracle contract.",
        "cost_shape": "Query complexity plus oracle-construction cost and observable-estimation samples; no full-vector readout.",
        "quantum_claim_allowed": "Admissible candidate advantage regime, but not a full explicit-I/O speedup claim.",
        "sources": ["hhl_2009", "childs_kothari_somma_2017"],
    },
    {
        "id": "D4_low_rank_sampling_access",
        "task_regime": "Low-rank or recommendation-style matrix with sample/query access to rows, columns, norms, or entries.",
        "classical_denominator": "Quantum-inspired sample/query classical algorithms.",
        "cost_shape": "poly(rank, kappa, norm, 1/epsilon) * polylog(dimensions) style accounting under the same access model.",
        "quantum_claim_allowed": "No exponential claim until compared against dequantized sampling-access baselines.",
        "sources": ["tang_2019", "chia_lin_wang_2018"],
    },
    {
        "id": "D5_b3_b5_observable_linear_response",
        "task_regime": "B3/B5 physics observable that reduces to a linear-system or Green-function estimate.",
        "classical_denominator": "Domain baseline: sparse Krylov/DMRG/embedding/Monte Carlo as applicable, plus observable estimator.",
        "cost_shape": "End-to-end wall-clock or operation-count baseline at fixed physical observable error, not only abstract QLSA query count.",
        "quantum_claim_allowed": "A future B3/B5 claim must state whether the advantage is from Hamiltonian simulation, state preparation, or observable estimation.",
        "sources": ["hhl_2009", "childs_kothari_somma_2017", "shewchuk_1994"],
    },
]


BOUNDARY_CHECKS = [
    {
        "id": "C1_output_contract",
        "question": "Does the task request the full vector x, a sample from x, one entry of x, or an expectation value?",
        "reject_if": "The claim advertises polylog(n) end-to-end runtime while requesting full explicit x.",
    },
    {
        "id": "C2_access_contract",
        "question": "Is A/b explicit input, succinctly generated, oracle-provided, block-encoded, or sample/query accessible?",
        "reject_if": "The claim treats oracle or sample/query access as free while comparing to an explicit-input classical baseline.",
    },
    {
        "id": "C3_condition_precision_contract",
        "question": "Are kappa, epsilon, sparsity/rank, norm parameters, and success probability fixed in both algorithms?",
        "reject_if": "The claim hides poor condition number, precision, or norm dependence in constants.",
    },
    {
        "id": "C4_denominator_contract",
        "question": "Is the classical denominator CG/LSQR/domain-specific/dequantized under the same access model?",
        "reject_if": "The claim compares a quantum oracle query bound to a weaker classical explicit-I/O baseline.",
    },
]


def validate(report: dict) -> list[str]:
    errors: list[str] = []
    if report.get("status") != "source_backed_denominator_baselines_instantiated_not_publishable_theorem":
        errors.append("status must remain a source-backed boundary note, not a publishable theorem claim")
    if report.get("source_target_id") != "B10-T1":
        errors.append("source_target_id must be B10-T1")
    if len(report.get("sources", [])) < 6:
        errors.append("at least six source anchors are required")
    if len(report.get("denominator_baselines", [])) < 5:
        errors.append("at least five denominator baselines are required")
    source_ids = {source["id"] for source in report.get("sources", [])}
    for baseline in report.get("denominator_baselines", []):
        if not baseline.get("sources"):
            errors.append(f"{baseline.get('id', '<unknown>')} has no sources")
        missing = [sid for sid in baseline.get("sources", []) if sid not in source_ids]
        if missing:
            errors.append(f"{baseline.get('id', '<unknown>')} references missing sources: {missing}")
    if len(report.get("boundary_checks", [])) < 4:
        errors.append("boundary checklist should have at least four checks")
    if report.get("explicit_not_bqp_separation") is not True:
        errors.append("must explicitly avoid BQP/classical separation claims")
    return errors


def build_report() -> dict:
    report = {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T1 source-backed HHL/data-loading boundary baselines",
        "version": "0.2",
        "last_updated": "2026-06-13",
        "status": "source_backed_denominator_baselines_instantiated_not_publishable_theorem",
        "method": "b10_t1_source_backed_boundaries_v0",
        "source_target_id": "B10-T1",
        "source_target_name": "linear_systems_data_loading_negative_boundary",
        "builds_on": "b10_t1_negative_boundary_proof_v0",
        "explicit_not_bqp_separation": True,
        "obligation_status": {
            "B10-T1-O1": "source_links_added_for_hhl_qlsa_dequantization_and_classical_denominators",
            "B10-T1-O2": "five_denominator_baselines_instantiated_for_future_claim_checks",
            "B10-T1-O3": "partially_scoped_dequantization_boundary_still_open",
        },
        "sources": SOURCES,
        "source_count": len(SOURCES),
        "denominator_baselines": BASELINES,
        "baseline_count": len(BASELINES),
        "boundary_checks": BOUNDARY_CHECKS,
        "remaining_open_items": [
            "Replace cost-shape placeholders with theorem-specific asymptotic constants after choosing one B3/B5 observable.",
            "Add a source-backed sampling-access theorem note for the Chia-Lin-Wang regime.",
            "Map the D5 observable-denominator regime to one concrete B3/B5 physics task.",
        ],
        "claim_boundary": {
            "now_supported": "B10-T1 is source-backed enough to reject hidden full-output/loading/readout HHL-style end-to-end exponential claims.",
            "still_not_supported": "It is not yet a literature-ready theorem paper, not a BQP/classical separation, and not a blanket rejection of QLSA advantages.",
            "next_proof_pressure": "Extend the D1/D2 numerical table to one D5 B3/B5 observable task, or write the D4 sampling-access theorem note.",
        },
    }
    report["validation_errors"] = validate(report)
    return report


def markdown(report: dict) -> str:
    lines = [
        "# B10-T1 Source-Backed Boundary Baselines v0.2",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source target: {report['source_target_id']} / {report['source_target_name']}",
        f"- Builds on: {report['builds_on']}",
        f"- Source anchors: {report['source_count']}",
        f"- Denominator baselines: {report['baseline_count']}",
        f"- Boundary checks: {len(report['boundary_checks'])}",
        f"- Explicitly not a BQP separation: {report['explicit_not_bqp_separation']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
        "## What Changed",
        "",
        "- B10-T1-O1 is now source-linked across HHL/QLSA, dequantization, and classical sparse-solver baselines.",
        "- B10-T1-O2 now has five concrete denominator regimes that future B3/B5/B10 claims must choose from.",
        "- B10-T1-O3 is partly scoped: sampling-access and low-rank regimes are no longer treated as ordinary explicit-I/O tasks, but a separate theorem note is still needed.",
        "",
        "## Sources",
        "",
    ]
    for source in report["sources"]:
        lines.extend(
            [
                f"### {source['id']}",
                "",
                f"- Citation: {source['authors']} ({source['year']}), [{source['title']}]({source['url']})",
                f"- Role: {source['role']}",
                "- Supports:",
            ]
        )
        lines.extend(f"  - {item}" for item in source["supports"])
        lines.append("")
    lines.extend(["## Denominator Baselines", ""])
    for baseline in report["denominator_baselines"]:
        lines.extend(
            [
                f"### {baseline['id']}",
                "",
                f"- Task regime: {baseline['task_regime']}",
                f"- Classical denominator: {baseline['classical_denominator']}",
                f"- Cost shape: {baseline['cost_shape']}",
                f"- Quantum claim allowed: {baseline['quantum_claim_allowed']}",
                f"- Sources: {', '.join(baseline['sources'])}",
                "",
            ]
        )
    lines.extend(["## Boundary Checklist", ""])
    for check in report["boundary_checks"]:
        lines.extend(
            [
                f"- {check['id']}: {check['question']}",
                f"  Reject if: {check['reject_if']}",
            ]
        )
    lines.extend(["", "## Claim Boundary", ""])
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Remaining Open Items", ""])
    lines.extend(f"- {item}" for item in report["remaining_open_items"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_t1_source_backed_boundaries_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_t1_source_backed_boundaries.md"))
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
                    "source_count": report["source_count"],
                    "baseline_count": report["baseline_count"],
                    "boundary_check_count": len(report["boundary_checks"]),
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
