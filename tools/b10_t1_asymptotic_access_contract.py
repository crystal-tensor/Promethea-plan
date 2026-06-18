#!/usr/bin/env python3
"""Build B10-T1 asymptotic family and access-contract notes for B3/B5."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METHOD = "b10_t1_asymptotic_access_contract_v0"
STATUS = "access_contract_skeleton_sampling_bridge_refuted_for_current_evidence"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(results_dir: Path) -> dict[str, Any]:
    missing_note = read_json(results_dir / "B10_t1_missing_assumption_note_v0.json")
    comparison = read_json(results_dir / "B10_t1_b3_b5_denominator_boundary_comparison_v0.json")
    b3_pressure = read_json(results_dir / "B3_cross_molecule_ucc_adapt_pressure_v0.json")
    b5_mps = read_json(results_dir / "B5_variational_mps_als_response_reference_v0.json")

    comparison_summary = comparison["summary"]
    b3_summary = b3_pressure["summary"]
    b5_summary = b5_mps["summary"]

    family_contracts = [
        {
            "id": "F_B3_reaction_derivative_family",
            "track": "B3",
            "family_parameter": "n = spin-orbital count plus basis/active-space growth",
            "observable": "finite-difference derivative of molecular energy along a reaction coordinate",
            "explicit_input_contract": (
                "A Hamiltonian term list, geometry grid, basis/active-space rule, target derivative error, "
                "and classical denominator must be explicitly available."
            ),
            "oracle_contract": (
                "Sparse-Hamiltonian or Pauli-term query access is allowed only if construction and indexing costs are charged."
            ),
            "sampling_access_contract": (
                "Sampling access would require a sampler for correlated-state Pauli groups with variance certificates "
                "under the same state-preparation and optimizer-loop budget."
            ),
            "current_portfolio_status": "finite_instances_only_not_asymptotic_theorem",
            "current_blocker": "B3 one-parameter UCC/ADAPT pressure is demoted and has no multi-parameter covariance rescue.",
        },
        {
            "id": "F_B5_hubbard_response_family",
            "track": "B5",
            "family_parameter": "n = lattice sites with U/t, filling, boundary field, and response observable scaling",
            "observable": "density or boundary-field response in strongly correlated Hubbard-like instances",
            "explicit_input_contract": (
                "The lattice, interaction profile, field protocol, response target, tolerance, and denominator solver "
                "must be explicit."
            ),
            "oracle_contract": (
                "Local-term oracle access is allowed only when the oracle build, response observable, and precision costs are charged."
            ),
            "sampling_access_contract": (
                "Sampling access would require a classical or quantum sampler whose response-estimator variance, "
                "mixing/preparation cost, and error propagation are all certified."
            ),
            "current_portfolio_status": "finite_d5_pressure_plus_nonproduction_mps",
            "current_blocker": "B5 has strong classical pressure, but the current variational MPS/ALS prototype is not production DMRG.",
        },
    ]

    access_contract_rows = []
    access_modes = [
        {
            "mode": "explicit",
            "equivalence_requirement": "Both sides receive the same explicit Hamiltonian/observable description and tolerance.",
            "bridge_status": "specified_for_next_theorem_target",
        },
        {
            "mode": "sparse_or_local_oracle",
            "equivalence_requirement": "Both sides receive equivalent term-query access with oracle construction and precision charged.",
            "bridge_status": "specified_but_not_instantiated",
        },
        {
            "mode": "sampling_or_query_access",
            "equivalence_requirement": "Both sides receive comparable sampling/query access, including preparation, variance, and failure probability.",
            "bridge_status": "refuted_for_current_portfolio_evidence",
        },
        {
            "mode": "quantum_state_preparation_or_block_encoding",
            "equivalence_requirement": "Quantum state preparation, block encoding, measurement, and optimizer-loop costs are charged end to end.",
            "bridge_status": "not_positive_ready",
        },
    ]
    for family in family_contracts:
        for mode in access_modes:
            access_contract_rows.append(
                {
                    "family_id": family["id"],
                    "track": family["track"],
                    "access_mode": mode["mode"],
                    "equivalence_requirement": mode["equivalence_requirement"],
                    "bridge_status": mode["bridge_status"],
                }
            )

    bridge_conditions = [
        {
            "id": "C1_asymptotic_scaling_law",
            "status": "defined_as_contract_not_proved",
            "current_evidence": "Two family contracts are now stated, but no all-n scaling theorem is proved.",
            "blocks_general_theorem": True,
        },
        {
            "id": "C2_equivalent_access_models",
            "status": "specified_as_contract_not_instantiated",
            "current_evidence": "Explicit, oracle, sampling, and quantum-preparation modes are separated in the matrix.",
            "blocks_general_theorem": True,
        },
        {
            "id": "C3_sampling_oracle_constructor",
            "status": "refuted_for_current_portfolio_evidence",
            "current_evidence": (
                "No current B3/B5 artifact constructs comparable sampling/query access; B3 max optimizer-loop shots lower bound is "
                f"{comparison_summary['b3_max_optimizer_loop_total_shots_lower_bound']}."
            ),
            "blocks_general_theorem": True,
        },
        {
            "id": "C4_classical_denominator_under_same_contract",
            "status": "partially_satisfied_for_finite_instances",
            "current_evidence": (
                "B3 selected-CI wins remain "
                f"{comparison_summary['b3_selected_ci_larger_basis_denominator_beaten_count']}; "
                "B5 variational-over-seeded MPS wins remain "
                f"{comparison_summary['b5_variational_mps_rows_beating_seeded_mps_pressure_reference']}."
            ),
            "blocks_general_theorem": True,
        },
        {
            "id": "C5_positive_quantum_kernel_after_full_costs",
            "status": "refuted_for_current_portfolio_evidence",
            "current_evidence": (
                "B3 demoted = "
                f"{comparison_summary['b3_demoted']}; B5 positive ready = {comparison_summary['b5_positive_claim_ready']}; "
                f"B5 production DMRG = {b5_summary['production_dmrg']}."
            ),
            "blocks_general_theorem": True,
        },
    ]

    theorem_targets = [
        {
            "id": "T1_explicit_input_negative_boundary_contract",
            "statement": (
                "For explicit B3/B5 inputs, a positive quantum claim must beat the best same-input selected-CI, FCI, "
                "tensor/MPS, embedding, or response denominator after state-preparation, measurement, and optimizer costs."
            ),
            "status": "theorem_target_contract_ready_not_proved",
        },
        {
            "id": "T2_sampling_access_bridge_failure_current_portfolio",
            "statement": (
                "The current B3/B5 portfolio does not instantiate the sampling/query access bridge required to turn "
                "the finite denominator pressure into a dequantization or sampling-access theorem."
            ),
            "status": "supported_as_current_evidence_refutation_not_general_impossibility",
        },
    ]

    validation_errors = []
    if missing_note["summary"].get("missing_assumption_count", 0) < 5:
        validation_errors.append("source missing-assumption note is weaker than expected")
    if comparison_summary.get("b3_demoted") is not True:
        validation_errors.append("B3 must remain demoted for this bridge-refutation artifact")
    if comparison_summary.get("b5_positive_claim_ready") is not False:
        validation_errors.append("B5 must not be positive-ready for this bridge-refutation artifact")
    if comparison_summary.get("quantum_advantage_claimed") is not False:
        validation_errors.append("source comparison must not claim quantum advantage")
    if b3_summary.get("selected_ci_larger_basis_denominator_beaten_count") != 0:
        validation_errors.append("B3 selected-CI denominator wins must remain zero")
    if b5_summary.get("production_dmrg") is not False:
        validation_errors.append("B5 variational MPS source should not be production DMRG")
    if not any(row["bridge_status"] == "refuted_for_current_portfolio_evidence" for row in access_contract_rows):
        validation_errors.append("access contract must record current sampling-bridge refutation")

    bridge_refuted_for_current_evidence = all(
        condition["blocks_general_theorem"] for condition in bridge_conditions
    ) and any(
        condition["status"] == "refuted_for_current_portfolio_evidence" for condition in bridge_conditions
    )

    return {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10-T1 Asymptotic Access Contract",
        "version": "0.1",
        "status": STATUS,
        "method": METHOD,
        "source_target_id": "B10-T1",
        "dependency_benchmarks": ["B3", "B5", "B10"],
        "source_missing_assumption_method": missing_note["method"],
        "source_comparison_method": comparison["method"],
        "summary": {
            "family_contract_count": len(family_contracts),
            "access_contract_count": len(access_contract_rows),
            "bridge_condition_count": len(bridge_conditions),
            "theorem_target_count": len(theorem_targets),
            "sampling_access_bridge_proved": False,
            "sampling_access_bridge_refuted_for_current_evidence": bridge_refuted_for_current_evidence,
            "general_dequantization_theorem_proved": False,
            "general_sampling_access_theorem_proved": False,
            "bqp_separation_claimed": False,
            "quantum_advantage_claimed": False,
            "b3_demoted": comparison_summary["b3_demoted"],
            "b5_positive_claim_ready": comparison_summary["b5_positive_claim_ready"],
            "b3_selected_ci_denominator_wins": comparison_summary["b3_selected_ci_larger_basis_denominator_beaten_count"],
            "b5_variational_mps_over_seeded_wins": comparison_summary[
                "b5_variational_mps_rows_beating_seeded_mps_pressure_reference"
            ],
            "validation_error_count": len(validation_errors),
        },
        "family_contracts": family_contracts,
        "access_contract_rows": access_contract_rows,
        "bridge_conditions": bridge_conditions,
        "theorem_targets": theorem_targets,
        "claim_boundary": {
            "sampling_access_bridge_proved": False,
            "sampling_access_bridge_refuted_for_current_evidence": bridge_refuted_for_current_evidence,
            "general_dequantization_theorem_proved": False,
            "general_sampling_access_theorem_proved": False,
            "bqp_separation_claimed": False,
            "quantum_advantage_claimed": False,
            "what_is_supported": (
                "Two asymptotic-family contracts and eight access-contract rows are now explicit. "
                "For the current portfolio evidence, the sampling/query access bridge is refuted because no comparable "
                "sampling oracle or positive quantum response kernel is instantiated."
            ),
            "what_is_not_supported": (
                "This is not a general dequantization theorem, not a sampling-access theorem, not a BQP separation, "
                "and not a quantum advantage result."
            ),
        },
        "next_required_artifacts": [
            "Choose one B3 or B5 family and formalize its all-n scaling law.",
            "Construct or refute a comparable sampling/query oracle for that family.",
            "Replace B5 variational MPS/ALS with production canonical DMRG/MPS pressure.",
            "Only reopen a positive quantum route after full state-preparation, measurement, and optimizer-loop accounting.",
        ],
        "validation_errors": validation_errors,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# B10-T1 Asymptotic Access Contract v0.1",
        "",
        f"- Status: {report['status']}",
        f"- Method: {report['method']}",
        f"- Source missing-assumption method: {report['source_missing_assumption_method']}",
        f"- Family contracts: {report['summary']['family_contract_count']}",
        f"- Access contract rows: {report['summary']['access_contract_count']}",
        f"- Bridge conditions: {report['summary']['bridge_condition_count']}",
        f"- Sampling-access bridge proved: {report['summary']['sampling_access_bridge_proved']}",
        f"- Sampling-access bridge refuted for current evidence: {report['summary']['sampling_access_bridge_refuted_for_current_evidence']}",
        f"- General dequantization theorem proved: {report['summary']['general_dequantization_theorem_proved']}",
        f"- BQP separation claimed: {report['summary']['bqp_separation_claimed']}",
        f"- Validation errors: {report['validation_errors']}",
        "",
        "## Family Contracts",
        "",
    ]
    for row in report["family_contracts"]:
        lines.extend(
            [
                f"### {row['id']}",
                "",
                f"- Track: {row['track']}",
                f"- Family parameter: {row['family_parameter']}",
                f"- Observable: {row['observable']}",
                f"- Explicit input contract: {row['explicit_input_contract']}",
                f"- Oracle contract: {row['oracle_contract']}",
                f"- Sampling access contract: {row['sampling_access_contract']}",
                f"- Current portfolio status: {row['current_portfolio_status']}",
                f"- Current blocker: {row['current_blocker']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Access Contract Matrix",
            "",
            "| family | mode | bridge status | equivalence requirement |",
            "|---|---|---|---|",
        ]
    )
    for row in report["access_contract_rows"]:
        lines.append(
            f"| {row['family_id']} | {row['access_mode']} | {row['bridge_status']} | {row['equivalence_requirement']} |"
        )

    lines.extend(["", "## Bridge Conditions", ""])
    for row in report["bridge_conditions"]:
        lines.extend(
            [
                f"### {row['id']}",
                "",
                f"- Status: {row['status']}",
                f"- Current evidence: {row['current_evidence']}",
                f"- Blocks general theorem: {row['blocks_general_theorem']}",
                "",
            ]
        )

    lines.extend(["## Theorem Targets", ""])
    for row in report["theorem_targets"]:
        lines.extend(
            [
                f"### {row['id']}",
                "",
                f"- Status: {row['status']}",
                f"- Statement: {row['statement']}",
                "",
            ]
        )

    lines.extend(["## Claim Boundary", ""])
    for key, value in report["claim_boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B10_t1_asymptotic_access_contract_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B10_t1_asymptotic_access_contract.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.results_dir)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "method": report["method"],
                **report["summary"],
                "validation_errors": report["validation_errors"],
            },
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0 if not report["validation_errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
