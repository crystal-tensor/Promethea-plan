#!/usr/bin/env python3
"""T-B5-006j/T-B10-014h: W1 implementation contract gate."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b5_b10_w1_implementation_contract_gate_v0"
STATUS = "w1_implementation_contract_open_not_production_dmrg"
MODEL_STATUS = "w1_blockers_converted_to_solver_implementation_contract"
VERSION = "0.1"
EXPECTED_ROW_CONTRACT_HASH = "7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc"
EXPECTED_SOURCE_FAILED_IDS = ["C3", "C4", "C5", "C7"]
EXPECTED_PACKET_IDS = [
    "W1-E4-env-residuals",
    "W1-E5-convergence",
    "W1-E6-seeded-pressure",
    "W1-E7-cost-ledger",
]


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


def packet(packet_id: str, role: str, required_files: list[str], acceptance: list[str]) -> dict[str, Any]:
    return {
        "packet_id": packet_id,
        "owner_role": role,
        "required_files": required_files,
        "acceptance": acceptance,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    blocker = load_json(args.canonical_residual_blocker)
    row_contract = load_json(args.row_contract_harness)
    denominator = load_json(args.denominator_engine)

    blocker_summary = blocker["summary"]
    row_contract_summary = row_contract["summary"]
    denominator_summary = denominator["summary"]
    source_packet_ids = [item["packet_id"] for item in blocker.get("pr_packets", [])]

    row_schema = {
        "required_row_keys": [
            "row_id",
            "sites",
            "u_over_t",
            "row_contract_hash",
            "canonical_center_site",
            "left_environment_hash",
            "right_environment_hash",
            "orthonormal_residual_norm",
            "discarded_weight",
            "sweep_count",
            "energy_variance",
            "fixed_sector_norm",
            "relative_response_error",
            "seeded_pressure_relative_response_error",
            "wall_clock_seconds",
            "peak_memory_mb",
            "matvec_or_sweep_count",
        ],
        "required_row_count": 9,
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "required_pass_conditions": [
            "environment_rows == 9",
            "orthonormal_residual_rows == 9",
            "discarded_weight_rows == 9",
            "convergence_passed_rows == 9",
            "rows_beating_seeded_pressure == 9",
            "same_access_production_cost_ledger_complete == true",
        ],
    }

    implementation_packets = [
        packet(
            "W1-E4-env-residuals",
            "DMRG Solver Agent",
            [
                "results/B5_w1_environment_rows_v*.json",
                "research/B5_w1_environment_rows.md",
            ],
            [
                "contains nine rows under the locked row-contract hash",
                "stores left/right environment hashes for every row",
                "stores orthonormal residual norms for every row",
            ],
        ),
        packet(
            "W1-E5-convergence",
            "Baseline Adversary",
            [
                "results/B5_w1_convergence_ledger_v*.json",
                "research/B5_w1_convergence_ledger.md",
            ],
            [
                "fixed-sector, energy-variance, discarded-weight, and monotonicity checks pass for all nine rows",
                "all convergence thresholds are declared before comparing against seeded pressure",
            ],
        ),
        packet(
            "W1-E6-seeded-pressure",
            "Tensor Denominator Agent",
            [
                "results/B5_w1_seeded_pressure_comparison_v*.json",
                "research/B5_w1_seeded_pressure_comparison.md",
            ],
            [
                "compares against the exact-state-seeded MPS pressure row by row",
                "records rows_beating_seeded_pressure == 9 before any positive B5/B10 route claim",
            ],
        ),
        packet(
            "W1-E7-cost-ledger",
            "Cost Ledger Agent",
            [
                "results/B5_w1_same_access_cost_ledger_v*.json",
                "research/B5_w1_same_access_cost_ledger.md",
            ],
            [
                "includes wall-clock, memory, sweep/matvec, and optimizer-loop costs",
                "uses the same nine-row access contract without hidden exact-state access",
            ],
        ),
    ]

    implementation_packet_ids = [item["packet_id"] for item in implementation_packets]
    environment_rows = int(blocker_summary.get("environment_rows", 0))
    residual_rows = int(blocker_summary.get("orthonormal_residual_rows", 0))
    discarded_rows = int(blocker_summary.get("discarded_weight_rows", 0))
    convergence_rows = int(blocker_summary.get("convergence_passed_rows", 0))
    seeded_win_rows = int(blocker_summary.get("rows_beating_seeded_pressure", 0))
    same_access_cost = bool(blocker_summary.get("same_access_production_cost_ledger_complete"))

    requirements = [
        requirement(
            "K1",
            "Canonical residual blocker source is valid and negative",
            blocker.get("status") == "w1_canonical_residual_blocker_gate_failed_missing_production_evidence"
            and blocker_summary.get("validation_error_count") == 0,
            {
                "source_status": blocker.get("status"),
                "source_validation_error_count": blocker_summary.get("validation_error_count"),
            },
        ),
        requirement(
            "K2",
            "Locked B5/B10 row contract hash is preserved",
            row_contract_summary.get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH
            and blocker_summary.get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH
            and denominator_summary.get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH,
            {
                "row_contract_hash": row_contract_summary.get("row_contract_hash"),
                "blocker_hash": blocker_summary.get("row_contract_hash"),
                "denominator_hash": denominator_summary.get("row_contract_hash"),
            },
        ),
        requirement(
            "K3",
            "Source blocker packets are complete",
            source_packet_ids == EXPECTED_PACKET_IDS,
            {"source_packet_ids": source_packet_ids},
        ),
        requirement(
            "K4",
            "Implementation contract schema is declared",
            len(row_schema["required_row_keys"]) == 17 and len(implementation_packets) == 4,
            {
                "required_row_key_count": len(row_schema["required_row_keys"]),
                "implementation_packet_count": len(implementation_packets),
            },
        ),
        requirement(
            "K5",
            "Canonical environment rows are supplied",
            environment_rows == 9,
            {"environment_rows": environment_rows, "required_rows": 9},
        ),
        requirement(
            "K6",
            "Orthonormal residual and discarded-weight rows are supplied",
            residual_rows == 9 and discarded_rows == 9,
            {
                "orthonormal_residual_rows": residual_rows,
                "discarded_weight_rows": discarded_rows,
                "required_rows": 9,
            },
        ),
        requirement(
            "K7",
            "All nine rows pass convergence",
            convergence_rows == 9,
            {"convergence_passed_rows": convergence_rows, "required_rows": 9},
        ),
        requirement(
            "K8",
            "Candidate beats seeded pressure on all rows",
            seeded_win_rows == 9,
            {"rows_beating_seeded_pressure": seeded_win_rows, "required_rows": 9},
        ),
        requirement(
            "K9",
            "Same-access production cost ledger is complete",
            same_access_cost is True,
            {"same_access_production_cost_ledger_complete": same_access_cost},
        ),
        requirement(
            "K10",
            "Forbidden claims remain false",
            all(
                blocker_summary.get(key) is False
                for key in [
                    "production_dmrg_claimed",
                    "same_access_positive_route_claimed",
                    "quantum_advantage_claimed",
                    "bqp_separation_claimed",
                ]
            ),
            {
                "production_dmrg_claimed": blocker_summary.get("production_dmrg_claimed"),
                "same_access_positive_route_claimed": blocker_summary.get(
                    "same_access_positive_route_claimed"
                ),
                "quantum_advantage_claimed": blocker_summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": blocker_summary.get("bqp_separation_claimed"),
            },
        ),
    ]
    passed = sum(1 for item in requirements if item["passed"])
    failed_ids = [item["requirement_id"] for item in requirements if not item["passed"]]

    validation_errors: list[str] = []
    if failed_ids != ["K5", "K6", "K7", "K8", "K9"]:
        validation_errors.append(f"unexpected failed implementation requirements: {failed_ids}")
    if blocker_summary.get("failed_canonical_residual_requirement_ids") != EXPECTED_SOURCE_FAILED_IDS:
        validation_errors.append("source canonical residual failed IDs changed")
    if source_packet_ids != EXPECTED_PACKET_IDS:
        validation_errors.append("source packet IDs changed")
    if row_contract_summary.get("row_contract_count") != 9:
        validation_errors.append("row contract count changed")

    summary = {
        "row_contract_count": int(row_contract_summary.get("row_contract_count", 0)),
        "row_contract_hash": row_contract_summary.get("row_contract_hash"),
        "source_blocker_method": blocker.get("method"),
        "source_blocker_status": blocker.get("status"),
        "source_failed_canonical_residual_ids": blocker_summary.get(
            "failed_canonical_residual_requirement_ids"
        ),
        "source_packet_ids": source_packet_ids,
        "implementation_contract_requirement_count": len(requirements),
        "implementation_contract_requirements_passed": passed,
        "implementation_contract_requirements_failed": len(requirements) - passed,
        "failed_implementation_contract_requirement_ids": failed_ids,
        "required_row_key_count": len(row_schema["required_row_keys"]),
        "implementation_packet_count": len(implementation_packets),
        "implementation_packet_ids": implementation_packet_ids,
        "environment_rows": environment_rows,
        "orthonormal_residual_rows": residual_rows,
        "discarded_weight_rows": discarded_rows,
        "convergence_passed_rows": convergence_rows,
        "rows_beating_seeded_pressure": seeded_win_rows,
        "same_access_production_cost_ledger_complete": same_access_cost,
        "w1_implementation_contract_ready": False,
        "production_dmrg_available": False,
        "same_access_positive_route_ready": False,
        "production_dmrg_claimed": False,
        "same_access_positive_route_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B5",
        "linked_benchmark_id": "B10",
        "source_target_id": "B10-T1",
        "dependency_benchmarks": ["B5", "B10"],
        "title": "B5/B10 W1 Implementation Contract Gate v0",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_canonical_residual_blocker_result": str(args.canonical_residual_blocker),
        "source_row_contract_harness_result": str(args.row_contract_harness),
        "source_denominator_engine_result": str(args.denominator_engine),
        "summary": summary,
        "requirements": requirements,
        "row_artifact_schema": row_schema,
        "implementation_packets": implementation_packets,
        "claim_boundary": {
            "what_is_supported": (
                "The W1 production-DMRG blocker has been converted into an implementation contract "
                "with row-level schema, four packetized deliverables, and acceptance predicates tied "
                "to the locked B5/B10 row-contract hash."
            ),
            "what_is_not_supported": (
                "This does not supply production DMRG, canonical environments, residual ledgers, "
                "converged rows, seeded-pressure wins, same-access cost evidence, a positive B5/B10 route, "
                "quantum advantage, or BQP separation."
            ),
            "next_gate": (
                "A future W1 solver PR must submit all four implementation packets and pass K5-K9 "
                "before the B5/B10 route can be reconsidered."
            ),
            "production_dmrg_claimed": False,
            "same_access_positive_route_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# B5/B10 W1 Implementation Contract Gate v0.1",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Row contract count/hash: {summary['row_contract_count']} / `{summary['row_contract_hash']}`",
        f"- Requirements passed/failed: {summary['implementation_contract_requirements_passed']} / {summary['implementation_contract_requirements_failed']}",
        f"- Failed requirement IDs: {summary['failed_implementation_contract_requirement_ids']}",
        f"- Source blocker failed IDs: {summary['source_failed_canonical_residual_ids']}",
        f"- Implementation packet IDs: {summary['implementation_packet_ids']}",
        f"- Environment / residual / discarded rows: {summary['environment_rows']} / {summary['orthonormal_residual_rows']} / {summary['discarded_weight_rows']}",
        f"- Convergence-passed rows: {summary['convergence_passed_rows']}",
        f"- Rows beating seeded pressure: {summary['rows_beating_seeded_pressure']}",
        f"- Same-access production cost ledger complete: {summary['same_access_production_cost_ledger_complete']}",
        "",
        "## Requirement Ledger",
        "",
        "| ID | Requirement | Passed | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for item in payload["requirements"]:
        evidence = "; ".join(f"{key}={value}" for key, value in item["evidence"].items())
        lines.append(f"| {item['requirement_id']} | {item['label']} | {item['passed']} | {evidence} |")

    lines.extend(
        [
            "",
            "## Row Artifact Schema",
            "",
            f"- required_row_count: {payload['row_artifact_schema']['required_row_count']}",
            f"- row_contract_hash: `{payload['row_artifact_schema']['row_contract_hash']}`",
            f"- required_row_keys: {payload['row_artifact_schema']['required_row_keys']}",
            "",
            "## Implementation Packets",
            "",
            "| Packet | Owner role | Required files | Acceptance |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in payload["implementation_packets"]:
        lines.append(
            f"| {item['packet_id']} | {item['owner_role']} | {', '.join(item['required_files'])} | "
            f"{'; '.join(item['acceptance'])} |"
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
            f"- same_access_positive_route_claimed: {payload['claim_boundary']['same_access_positive_route_claimed']}",
            f"- quantum_advantage_claimed: {payload['claim_boundary']['quantum_advantage_claimed']}",
            f"- bqp_separation_claimed: {payload['claim_boundary']['bqp_separation_claimed']}",
            "",
            "## Validation",
            "",
            f"- validation_error_count: {len(payload['validation_errors'])}",
        ]
    )
    if payload["validation_errors"]:
        lines.extend(f"- {err}" for err in payload["validation_errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--canonical-residual-blocker",
        type=Path,
        default=Path("results/B5_w1_canonical_residual_blocker_gate_v0.json"),
    )
    parser.add_argument(
        "--row-contract-harness",
        type=Path,
        default=Path("results/B5_B10_row_contract_harness_v0.json"),
    )
    parser.add_argument(
        "--denominator-engine",
        type=Path,
        default=Path("results/B5_production_dmrg_mps_denominator_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B5_B10_w1_implementation_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B5_B10_w1_implementation_contract_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-01")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    write_json(args.json_output, payload, pretty=args.pretty)
    write_markdown(payload, args.markdown_output)
    summary = payload["summary"]
    print(payload["status"])
    print(
        summary["implementation_contract_requirements_passed"],
        summary["implementation_contract_requirements_failed"],
        summary["failed_implementation_contract_requirement_ids"],
    )
    print(summary["implementation_packet_ids"])


if __name__ == "__main__":
    main()
