#!/usr/bin/env python3
"""T-B5-006k/T-B10-014i: scout prototype environment evidence for W1 K5/K6."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b5_b10_w1_prototype_environment_scout_v0"
STATUS = "w1_prototype_environment_scout_failed_not_canonical_contract"
MODEL_STATUS = "prototype_two_site_ledgers_mapped_but_not_promoted_to_production_dmrg"
VERSION = "0.1"
EXPECTED_ROW_CONTRACT_HASH = "7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc"
EXPECTED_FAILED_IDS = ["P5", "P6", "P7"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def row_id(row: dict[str, Any]) -> str:
    return f"{int(row['sites'])}|{float(row['u_over_t']):.6g}"


def stable_hash(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_row(contract_row: dict[str, Any], smoke_row: dict[str, Any], required_keys: list[str]) -> dict[str, Any]:
    transformed = {
        "row_id": contract_row["row_id"],
        "sites": int(contract_row["sites"]),
        "u_over_t": float(contract_row["u_over_t"]),
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "sweep_count": int(smoke_row.get("sweep_count", 0)),
        "energy_variance": float(smoke_row.get("selected_energy_variance", 0.0)),
        "fixed_sector_norm": float(
            smoke_row.get("selected_fixed_sector_norm_before_normalization", 0.0)
        ),
        "relative_response_error": float(smoke_row.get("selected_relative_response_error", 0.0)),
        "seeded_pressure_relative_response_error": float(
            smoke_row.get("seeded_mps_pressure_relative_response_error", 0.0)
        ),
    }
    available_contract_keys = [key for key in required_keys if key in transformed]
    missing_contract_keys = [key for key in required_keys if key not in transformed]
    trace_basis = {
        "row_id": transformed["row_id"],
        "sweep_count": transformed["sweep_count"],
        "selected_bond_dimension": smoke_row.get("selected_bond_dimension"),
        "max_relative_discarded_weight": smoke_row.get("max_relative_discarded_weight"),
        "min_local_rank": smoke_row.get("min_local_rank"),
        "max_local_parameter_count": smoke_row.get("max_local_parameter_count"),
        "energy_monotonicity_violations": smoke_row.get("energy_monotonicity_violations"),
        "source": "B5_canonical_environment_smoke_gate_v0",
    }
    return {
        **transformed,
        "prototype_environment_ledger_present": bool(smoke_row.get("environment_ledger_present")),
        "prototype_trace_hash": stable_hash(trace_basis),
        "prototype_discarded_weight_metric_present": "max_relative_discarded_weight" in smoke_row,
        "prototype_max_relative_discarded_weight": smoke_row.get("max_relative_discarded_weight"),
        "prototype_energy_monotonicity_passed": bool(
            smoke_row.get("energy_monotonicity_smoke_passed")
        ),
        "prototype_energy_variance_passed": bool(smoke_row.get("energy_variance_smoke_passed")),
        "prototype_fixed_sector_norm_passed": bool(
            smoke_row.get("fixed_sector_norm_smoke_passed")
        ),
        "contract_available_key_count": len(available_contract_keys),
        "contract_available_keys": available_contract_keys,
        "contract_missing_keys": missing_contract_keys,
        "canonical_center_site": None,
        "left_environment_hash": None,
        "right_environment_hash": None,
        "orthonormal_residual_norm": None,
        "discarded_weight": None,
        "wall_clock_seconds": None,
        "peak_memory_mb": None,
        "matvec_or_sweep_count": None,
        "production_contract_row_accepted": False,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    implementation_contract = load_json(args.implementation_contract)
    smoke = load_json(args.smoke_gate)
    row_contract = load_json(args.row_contract_harness)
    denominator = load_json(args.denominator_engine)

    required_keys = implementation_contract["row_artifact_schema"]["required_row_keys"]
    smoke_rows = {row_id(row): row for row in smoke.get("rows", [])}
    contract_rows = row_contract.get("contract_rows", row_contract.get("row_contract", []))
    rows = [
        build_row(row, smoke_rows[f"{int(row['sites'])}|{float(row['u_over_t']):.6g}"], required_keys)
        for row in contract_rows
    ]

    source_smoke_environment_rows = sum(row["prototype_environment_ledger_present"] for row in rows)
    prototype_trace_hash_rows = sum(bool(row["prototype_trace_hash"]) for row in rows)
    prototype_discarded_weight_rows = sum(
        row["prototype_discarded_weight_metric_present"] for row in rows
    )
    contract_canonical_environment_rows = sum(
        bool(row["left_environment_hash"]) and bool(row["right_environment_hash"]) for row in rows
    )
    contract_residual_rows = sum(row["orthonormal_residual_norm"] is not None for row in rows)
    contract_discarded_weight_rows = sum(row["discarded_weight"] is not None for row in rows)
    accepted_rows = sum(row["production_contract_row_accepted"] for row in rows)
    available_key_counts = [row["contract_available_key_count"] for row in rows]

    requirements = [
        requirement(
            "P1",
            "Locked B5/B10 row contract and W1 contract sources are present",
            len(rows) == 9
            and row_contract["summary"].get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH
            and implementation_contract["summary"].get("row_contract_hash")
            == EXPECTED_ROW_CONTRACT_HASH,
            {
                "row_count": len(rows),
                "row_contract_hash": row_contract["summary"].get("row_contract_hash"),
                "implementation_contract_hash": implementation_contract["summary"].get(
                    "row_contract_hash"
                ),
            },
        ),
        requirement(
            "P2",
            "Prototype smoke gate exposes environment-ledger rows for all contract rows",
            source_smoke_environment_rows == 9,
            {
                "source_smoke_environment_rows": source_smoke_environment_rows,
                "required_rows": 9,
            },
        ),
        requirement(
            "P3",
            "Prototype trace hashes are generated for all rows",
            prototype_trace_hash_rows == 9,
            {
                "prototype_trace_hash_rows": prototype_trace_hash_rows,
                "required_rows": 9,
            },
        ),
        requirement(
            "P4",
            "Prototype rows can cover stable identity and scalar diagnostic keys",
            min(available_key_counts) >= 9,
            {
                "min_available_contract_key_count": min(available_key_counts),
                "required_row_key_count": len(required_keys),
            },
        ),
        requirement(
            "P5",
            "Canonical left/right environment hashes are supplied",
            contract_canonical_environment_rows == 9,
            {
                "contract_canonical_environment_rows": contract_canonical_environment_rows,
                "prototype_environment_ledger_rows": source_smoke_environment_rows,
                "required_rows": 9,
            },
        ),
        requirement(
            "P6",
            "Orthonormal residual norms are supplied under the W1 row schema",
            contract_residual_rows == 9,
            {"contract_orthonormal_residual_rows": contract_residual_rows, "required_rows": 9},
        ),
        requirement(
            "P7",
            "Production discarded-weight rows are supplied under the exact W1 key",
            contract_discarded_weight_rows == 9,
            {
                "contract_discarded_weight_rows": contract_discarded_weight_rows,
                "prototype_discarded_weight_metric_rows": prototype_discarded_weight_rows,
                "required_rows": 9,
            },
        ),
        requirement(
            "P8",
            "Forbidden claims remain false and prototype evidence is not promoted",
            all(
                denominator["summary"].get(key) is False
                for key in [
                    "production_dmrg_claimed",
                    "same_access_positive_route_claimed",
                    "quantum_advantage_claimed",
                    "bqp_separation_claimed",
                ]
            ),
            {
                "production_dmrg_claimed": denominator["summary"].get("production_dmrg_claimed"),
                "same_access_positive_route_claimed": denominator["summary"].get(
                    "same_access_positive_route_claimed"
                ),
                "quantum_advantage_claimed": denominator["summary"].get(
                    "quantum_advantage_claimed"
                ),
                "bqp_separation_claimed": denominator["summary"].get("bqp_separation_claimed"),
            },
        ),
    ]
    passed = sum(1 for item in requirements if item["passed"])
    failed_ids = [item["requirement_id"] for item in requirements if not item["passed"]]

    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected failed prototype scout requirements: {failed_ids}")
    if source_smoke_environment_rows != 9:
        validation_errors.append("prototype smoke gate should expose nine environment-ledger rows")
    if accepted_rows != 0:
        validation_errors.append("prototype scout must not accept production contract rows")

    summary = {
        "row_contract_count": len(rows),
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "source_smoke_status": smoke.get("status"),
        "source_implementation_contract_status": implementation_contract.get("status"),
        "prototype_scout_requirement_count": len(requirements),
        "prototype_scout_requirements_passed": passed,
        "prototype_scout_requirements_failed": len(requirements) - passed,
        "failed_prototype_scout_requirement_ids": failed_ids,
        "required_row_key_count": len(required_keys),
        "min_available_contract_key_count": min(available_key_counts),
        "source_smoke_environment_ledger_rows": source_smoke_environment_rows,
        "prototype_trace_hash_rows": prototype_trace_hash_rows,
        "prototype_discarded_weight_metric_rows": prototype_discarded_weight_rows,
        "contract_canonical_environment_rows": contract_canonical_environment_rows,
        "contract_orthonormal_residual_rows": contract_residual_rows,
        "contract_discarded_weight_rows": contract_discarded_weight_rows,
        "production_contract_rows_accepted": accepted_rows,
        "w1_k5_k6_evidence_ready": False,
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
        "title": "B5/B10 W1 Prototype Environment Scout v0",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_implementation_contract_result": str(args.implementation_contract),
        "source_smoke_gate_result": str(args.smoke_gate),
        "source_row_contract_harness_result": str(args.row_contract_harness),
        "source_denominator_engine_result": str(args.denominator_engine),
        "summary": summary,
        "requirements": requirements,
        "rows": rows,
        "claim_boundary": {
            "production_dmrg_claimed": False,
            "same_access_positive_route_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "what_is_supported": (
                "The older two-site smoke gate has nine prototype environment/sweep ledgers that can "
                "be traced row by row against the locked B5/B10 contract."
            ),
            "what_is_not_supported": (
                "The prototype ledgers are not canonical left/right environment hashes, not "
                "orthonormal residual norms, not production discarded-weight rows under the W1 schema, "
                "not production DMRG, and not a positive B5/B10 route."
            ),
            "next_gate": (
                "Turn the prototype trace rows into real W1-E4/K5 and W1-E4/K6 artifacts by storing "
                "canonical center sites, left/right environment hashes, residual norms, and production "
                "discarded weights for all nine locked rows."
            ),
        },
        "validation_errors": validation_errors,
        "runtime_seconds": time.time() - started,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    lines = [
        "# B5/B10 W1 Prototype Environment Scout v0.1",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Locked row contract hash: `{summary['row_contract_hash']}`",
        f"- Rows: {summary['row_contract_count']}",
        f"- Prototype smoke environment-ledger rows: {summary['source_smoke_environment_ledger_rows']}",
        f"- Prototype trace-hash rows: {summary['prototype_trace_hash_rows']}",
        f"- Prototype discarded-weight metric rows: {summary['prototype_discarded_weight_metric_rows']}",
        f"- Production canonical environment rows accepted: {summary['contract_canonical_environment_rows']}",
        f"- Production orthonormal-residual rows accepted: {summary['contract_orthonormal_residual_rows']}",
        f"- Production discarded-weight rows accepted: {summary['contract_discarded_weight_rows']}",
        f"- Production contract rows accepted: {summary['production_contract_rows_accepted']}",
        f"- Requirements passed/failed: {summary['prototype_scout_requirements_passed']} / {summary['prototype_scout_requirements_failed']}",
        f"- Failed requirement IDs: {', '.join(summary['failed_prototype_scout_requirement_ids'])}",
        "",
        "## Why This Matters",
        "",
        "This scout finds reusable row-level prototype evidence without promoting it into a production DMRG claim. The current two-site smoke gate already has nine sweep/environment-ledger traces, but W1 K5/K6 require canonical environment hashes and orthonormal residual norms under the exact 17-key row schema.",
        "",
        "## Requirement Results",
        "",
    ]
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
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--implementation-contract", type=Path, default=Path("results/B5_B10_w1_implementation_contract_gate_v0.json"))
    parser.add_argument("--smoke-gate", type=Path, default=Path("results/B5_canonical_environment_smoke_gate_v0.json"))
    parser.add_argument("--row-contract-harness", type=Path, default=Path("results/B5_B10_row_contract_harness_v0.json"))
    parser.add_argument("--denominator-engine", type=Path, default=Path("results/B5_production_dmrg_mps_denominator_v0.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B5_B10_w1_prototype_environment_scout_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B5_B10_w1_prototype_environment_scout.md"))
    parser.add_argument("--last-updated", default="2026-07-01")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    write_markdown(payload, args.markdown_output)
    print(payload["status"])
    print(
        payload["summary"]["prototype_scout_requirements_passed"],
        payload["summary"]["prototype_scout_requirements_failed"],
        payload["summary"]["failed_prototype_scout_requirement_ids"],
    )


if __name__ == "__main__":
    main()
