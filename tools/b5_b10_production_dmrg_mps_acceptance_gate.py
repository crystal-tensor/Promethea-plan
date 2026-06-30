#!/usr/bin/env python3
"""T-B5-006g/T-B10-014e: W1 production DMRG/MPS acceptance gate."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b5_b10_production_dmrg_mps_acceptance_gate_v0"
STATUS = "production_dmrg_mps_acceptance_gate_failed_no_w1_denominator"
MODEL_STATUS = "w1_acceptance_gate_executed_production_denominator_not_constructed"
VERSION = "0.1"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pretty:
        text = json.dumps(payload, indent=2, sort_keys=True)
    else:
        text = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any], next_step: str) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
        "required_next_step": next_step,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    row_contract = load_json(args.row_contract)
    readiness = load_json(args.readiness_gate)
    smoke = load_json(args.smoke_gate)
    production_contract = load_json(args.production_contract)
    seeded_replacement = load_json(args.seeded_replacement)
    response_oracle = load_json(args.response_oracle)
    two_site = load_json(args.two_site_reference)

    row_summary = row_contract["summary"]
    readiness_summary = readiness["summary"]
    smoke_summary = smoke["summary"]
    production_summary = production_contract["summary"]
    seeded_summary = seeded_replacement["summary"]
    oracle_summary = response_oracle["summary"]
    two_site_summary = two_site["summary"]

    requirements = [
        requirement(
            "D1",
            "W4 row contract is preserved for all W1 comparisons",
            row_summary.get("row_contract_count") == 9 and row_summary.get("source_checks_failed") == 0,
            {
                "row_contract_count": row_summary.get("row_contract_count"),
                "source_checks_failed": row_summary.get("source_checks_failed"),
                "row_contract_hash": row_summary.get("row_contract_hash"),
            },
            "Keep the same nine B5/B10 D5 observable rows and row_contract_hash in every W1 denominator run.",
        ),
        requirement(
            "D2",
            "All nine rows expose environment-ledger diagnostics",
            smoke_summary.get("environment_ledger_rows") == row_summary.get("row_contract_count") == 9,
            {
                "environment_ledger_rows": smoke_summary.get("environment_ledger_rows"),
                "row_contract_count": row_summary.get("row_contract_count"),
            },
            "Retain row-level environment telemetry while replacing post-hoc diagnostics with a real canonical sweep engine.",
        ),
        requirement(
            "D3",
            "Non-exact-state-seeded production denominator is available",
            readiness_summary.get("production_dmrg") is True
            or production_summary.get("production_dmrg_available") is True,
            {
                "readiness_production_dmrg": readiness_summary.get("production_dmrg"),
                "contract_production_dmrg_available": production_summary.get("production_dmrg_available"),
                "seeded_exact_state_seeded": seeded_summary.get("seeded_exact_state_seeded"),
            },
            "Implement a production DMRG/MPS denominator that does not initialize from the exact target state.",
        ),
        requirement(
            "D4",
            "Stored canonical left/right environments and orthonormal residuals pass",
            readiness_summary.get("canonical_environment_production_dmrg") is True
            and smoke_summary.get("smoke_passed_row_count") == 9,
            {
                "canonical_environment_production_dmrg": readiness_summary.get(
                    "canonical_environment_production_dmrg"
                ),
                "smoke_passed_row_count": smoke_summary.get("smoke_passed_row_count"),
            },
            "Add canonical-center sweeps, stored left/right environments, and orthonormal residual checks for every row.",
        ),
        requirement(
            "D5",
            "Sweep convergence ledgers satisfy fixed-sector, variance, discarded-weight, and monotonicity gates",
            smoke_summary.get("fixed_sector_norm_passed_rows") == 9
            and smoke_summary.get("energy_variance_passed_rows") == 9
            and smoke_summary.get("discarded_weight_passed_rows") == 9
            and smoke_summary.get("energy_monotonicity_passed_rows") == 9,
            {
                "fixed_sector_norm_passed_rows": smoke_summary.get("fixed_sector_norm_passed_rows"),
                "energy_variance_passed_rows": smoke_summary.get("energy_variance_passed_rows"),
                "discarded_weight_passed_rows": smoke_summary.get("discarded_weight_passed_rows"),
                "energy_monotonicity_passed_rows": smoke_summary.get("energy_monotonicity_passed_rows"),
            },
            "Produce convergence ledgers that pass all four production diagnostics on the full nine-row contract.",
        ),
        requirement(
            "D6",
            "Production W1 denominator beats seeded-pressure ladder under same access",
            seeded_summary.get("seeded_pressure_replaced") is True
            and seeded_summary.get("deployable_replacement_count", 0) > 0,
            {
                "seeded_pressure_replaced": seeded_summary.get("seeded_pressure_replaced"),
                "deployable_replacement_count": seeded_summary.get("deployable_replacement_count"),
                "best_replacement_candidate_id": seeded_summary.get("best_replacement_candidate_id"),
                "best_replacement_rows_beating_seeded_pressure": seeded_summary.get(
                    "best_replacement_rows_beating_seeded_pressure"
                ),
            },
            "Beat the exact-state-seeded pressure reference globally with a deployable non-seeded production denominator.",
        ),
        requirement(
            "D7",
            "B10 same-access cost ledger is complete for DMRG/MPS comparison",
            production_summary.get("production_contract_ready") is True
            and oracle_summary.get("w3_response_oracle_constructed") is False,
            {
                "production_contract_ready": production_summary.get("production_contract_ready"),
                "blocking_sampling_requirement_count": production_summary.get(
                    "blocking_sampling_requirement_count"
                ),
                "oracle_remaining_failed_ids": oracle_summary.get("failed_oracle_requirement_ids"),
            },
            "Add wall-clock, matvec, sweep, memory, optimizer-loop, and denominator-ladder cost accounting.",
        ),
        requirement(
            "D8",
            "B10-T1 positive route is ready without a hidden access advantage",
            production_summary.get("same_access_positive_route_ready") is True
            and production_summary.get("b10_t1_positive_route_ready") is True,
            {
                "same_access_positive_route_ready": production_summary.get("same_access_positive_route_ready"),
                "b10_t1_positive_route_ready": production_summary.get("b10_t1_positive_route_ready"),
            },
            "Promote W1 to B10 only after the same-access production contract passes without oracle leakage.",
        ),
        requirement(
            "D9",
            "W1 improves over the strongest current non-production tensor prototype",
            two_site_summary.get("two_site_dmrg_rows_beating_seeded_mps_pressure_reference") == 9
            and readiness_summary.get("prototype_fixed_sector_norms_pass") is True,
            {
                "two_site_rows_beating_seeded_mps_pressure_reference": two_site_summary.get(
                    "two_site_dmrg_rows_beating_seeded_mps_pressure_reference"
                ),
                "two_site_rows_beating_variational_mps_als_reference": two_site_summary.get(
                    "two_site_dmrg_rows_beating_variational_mps_als_reference"
                ),
                "prototype_fixed_sector_norms_pass": readiness_summary.get("prototype_fixed_sector_norms_pass"),
            },
            "Use the current two-site/ALS evidence only as pressure input; do not accept it as production W1 evidence.",
        ),
        requirement(
            "D10",
            "Forbidden claims remain false while W1 is unresolved",
            all(
                item is False
                for item in [
                    row_summary.get("production_dmrg_claimed"),
                    seeded_summary.get("quantum_response_win_claimed"),
                    production_summary.get("same_access_positive_route_claimed"),
                    oracle_summary.get("quantum_advantage_claimed"),
                    oracle_summary.get("bqp_separation_claimed"),
                ]
            ),
            {
                "production_dmrg_claimed": row_summary.get("production_dmrg_claimed"),
                "quantum_response_win_claimed": seeded_summary.get("quantum_response_win_claimed"),
                "same_access_positive_route_claimed": production_summary.get(
                    "same_access_positive_route_claimed"
                ),
                "quantum_advantage_claimed": oracle_summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": oracle_summary.get("bqp_separation_claimed"),
            },
            "Continue blocking production-DMRG, same-access, quantum-advantage, and BQP claims until D1-D9 pass.",
        ),
    ]

    passed = sum(1 for item in requirements if item["passed"])
    failed = len(requirements) - passed
    failed_ids = [item["requirement_id"] for item in requirements if not item["passed"]]

    validation_errors: list[str] = []
    if row_summary.get("row_contract_count") != 9:
        validation_errors.append("row contract must contain nine rows")
    if smoke_summary.get("environment_ledger_rows") != 9:
        validation_errors.append("smoke gate should expose nine environment-ledger rows")
    if failed_ids != ["D3", "D4", "D5", "D6", "D7", "D8", "D9"]:
        validation_errors.append(f"unexpected W1 failed requirement IDs: {failed_ids}")
    if passed != 3 or failed != 7:
        validation_errors.append(f"unexpected W1 pass/fail split: {passed}/{failed}")
    for field, value in [
        ("production_dmrg_available", production_summary.get("production_dmrg_available")),
        ("seeded_pressure_replaced", seeded_summary.get("seeded_pressure_replaced")),
        ("same_access_positive_route_ready", production_summary.get("same_access_positive_route_ready")),
        ("b10_t1_positive_route_ready", production_summary.get("b10_t1_positive_route_ready")),
    ]:
        if value is not False:
            validation_errors.append(f"{field} must remain False in current W1 gate")

    summary = {
        "row_contract_hash": row_summary.get("row_contract_hash"),
        "row_contract_count": row_summary.get("row_contract_count"),
        "environment_ledger_rows": smoke_summary.get("environment_ledger_rows"),
        "production_dmrg_requirement_count": len(requirements),
        "production_dmrg_requirements_passed": passed,
        "production_dmrg_requirements_failed": failed,
        "failed_production_dmrg_requirement_ids": failed_ids,
        "w1_production_dmrg_acceptance_gate_executed": True,
        "w1_production_dmrg_denominator_available": False,
        "w1_remains_blocked_on_denominator_engine": True,
        "readiness_gate_count": readiness_summary.get("readiness_gate_count"),
        "readiness_passed_gate_count": readiness_summary.get("passed_gate_count"),
        "canonical_environment_smoke_passed_rows": smoke_summary.get("smoke_passed_row_count"),
        "fixed_sector_norm_passed_rows": smoke_summary.get("fixed_sector_norm_passed_rows"),
        "energy_variance_passed_rows": smoke_summary.get("energy_variance_passed_rows"),
        "discarded_weight_passed_rows": smoke_summary.get("discarded_weight_passed_rows"),
        "energy_monotonicity_passed_rows": smoke_summary.get("energy_monotonicity_passed_rows"),
        "seeded_pressure_replaced": seeded_summary.get("seeded_pressure_replaced"),
        "deployable_replacement_count": seeded_summary.get("deployable_replacement_count"),
        "best_replacement_candidate_id": seeded_summary.get("best_replacement_candidate_id"),
        "best_replacement_mean_relative_response_error": seeded_summary.get(
            "best_replacement_mean_relative_response_error"
        ),
        "seeded_mean_relative_response_error": seeded_summary.get("seeded_mean_relative_response_error"),
        "oracle_requirements_failed": oracle_summary.get("oracle_requirements_failed"),
        "oracle_failed_requirement_ids": oracle_summary.get("failed_oracle_requirement_ids"),
        "remaining_positive_route_packets": ["W1"],
        "catalog_change_required": False,
        "production_dmrg_available": False,
        "sampling_oracle_constructed": False,
        "same_access_response_oracle_constructed": False,
        "same_access_positive_route_ready": False,
        "b10_t1_positive_route_ready": False,
        "production_dmrg_claimed": False,
        "quantum_response_win_claimed": False,
        "accuracy_per_resource_win_claimed": False,
        "same_access_positive_route_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "dequantization_theorem_claimed": False,
        "sampling_access_theorem_claimed": False,
        "condition_count": len(requirements),
        "conditions_satisfied": passed,
        "conditions_failed": failed,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B5",
        "linked_benchmark_id": "B10",
        "source_target_id": "B10-T1",
        "dependency_benchmarks": ["B5", "B10"],
        "title": "B5/B10 W1 Production DMRG/MPS Acceptance Gate",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_row_contract_result": str(args.row_contract),
        "source_readiness_gate_result": str(args.readiness_gate),
        "source_smoke_gate_result": str(args.smoke_gate),
        "source_production_contract_result": str(args.production_contract),
        "source_seeded_replacement_result": str(args.seeded_replacement),
        "source_response_oracle_result": str(args.response_oracle),
        "summary": summary,
        "requirements": requirements,
        "claim_boundary": {
            "w1_acceptance_gate_executed": True,
            "production_dmrg_available": False,
            "w1_production_dmrg_denominator_available": False,
            "production_dmrg_claimed": False,
            "quantum_response_win_claimed": False,
            "accuracy_per_resource_win_claimed": False,
            "same_access_positive_route_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "dequantization_theorem_claimed": False,
            "sampling_access_theorem_claimed": False,
            "what_is_supported": (
                "A W1-specific acceptance gate that preserves the B5/B10 row contract and enumerates the "
                "production DMRG/MPS requirements still blocking a positive B5/B10 route."
            ),
            "what_is_not_supported": (
                "This is not a production DMRG implementation, not a deployable tensor solver, not a same-access "
                "positive route, not quantum advantage, and not a BQP separation."
            ),
            "next_gate": (
                "Implement tools/b5_production_dmrg_mps_denominator.py with non-exact-state-seeded canonical "
                "sweeps, stored environments, convergence ledgers, and same-access cost accounting."
            ),
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# B5/B10 W1 Production DMRG/MPS Acceptance Gate v0.1",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Row contract count/hash: {summary['row_contract_count']} / `{summary['row_contract_hash']}`",
        f"- Requirements passed/failed: {summary['production_dmrg_requirements_passed']} / {summary['production_dmrg_requirements_failed']}",
        f"- Failed requirement IDs: {summary['failed_production_dmrg_requirement_ids']}",
        f"- Readiness gates passed: {summary['readiness_passed_gate_count']} / {summary['readiness_gate_count']}",
        f"- Canonical-environment smoke-passed rows: {summary['canonical_environment_smoke_passed_rows']}",
        f"- W1 denominator available: {summary['w1_production_dmrg_denominator_available']}",
        f"- Remaining positive-route packets: {summary['remaining_positive_route_packets']}",
        "",
        "## Requirement Ledger",
        "",
        "| ID | Requirement | Passed | Evidence | Required next step |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in payload["requirements"]:
        evidence = "; ".join(f"{key}={value}" for key, value in item["evidence"].items())
        lines.append(
            f"| {item['requirement_id']} | {item['label']} | {item['passed']} | {evidence} | {item['required_next_step']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- what_is_supported: {payload['claim_boundary']['what_is_supported']}",
            f"- what_is_not_supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- next_gate: {payload['claim_boundary']['next_gate']}",
            f"- production_dmrg_claimed: {payload['claim_boundary']['production_dmrg_claimed']}",
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the B5/B10 W1 production DMRG/MPS acceptance gate.")
    parser.add_argument("--row-contract", type=Path, default=Path("results/B5_B10_row_contract_harness_v0.json"))
    parser.add_argument("--readiness-gate", type=Path, default=Path("results/B5_canonical_dmrg_readiness_gate_v0.json"))
    parser.add_argument("--smoke-gate", type=Path, default=Path("results/B5_canonical_environment_smoke_gate_v0.json"))
    parser.add_argument(
        "--production-contract",
        type=Path,
        default=Path("results/B5_B10_same_access_production_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--seeded-replacement",
        type=Path,
        default=Path("results/B5_seeded_pressure_replacement_audit_v0.json"),
    )
    parser.add_argument(
        "--response-oracle",
        type=Path,
        default=Path("results/B5_B10_response_oracle_cost_ledger_v0.json"),
    )
    parser.add_argument(
        "--two-site-reference",
        type=Path,
        default=Path("results/B5_two_site_dmrg_response_reference_v0.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("results/B5_B10_production_dmrg_mps_acceptance_gate_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B5_B10_production_dmrg_mps_acceptance_gate.md"))
    parser.add_argument("--last-updated", default=time.strftime("%Y-%m-%d"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, pretty=args.pretty)
    write_markdown(payload, args.markdown_output)
    if args.pretty:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
