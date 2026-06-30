#!/usr/bin/env python3
"""T-B5-006l/T-B10-014j: W1 production-row intake template gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b5_b10_w1_production_row_intake_template_gate_v0"
STATUS = "w1_production_row_intake_template_open_missing_submitted_rows"
MODEL_STATUS = "w1_submission_template_built_no_production_rows_accepted"
VERSION = "0.1"
EXPECTED_ROW_CONTRACT_HASH = "7ee407e20f51bd0c003d885c8d43282359f84bea9729f0da203b9b2c2970a9fc"
EXPECTED_FAILED_IDS = ["I5", "I6", "I7"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def stable_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_template_row(
    prototype_row: dict[str, Any], required_keys: list[str], production_required_keys: list[str]
) -> dict[str, Any]:
    prefilled_values = {
        "row_id": prototype_row["row_id"],
        "sites": int(prototype_row["sites"]),
        "u_over_t": float(prototype_row["u_over_t"]),
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "sweep_count": int(prototype_row.get("sweep_count", 0)),
        "energy_variance": float(prototype_row.get("energy_variance", 0.0)),
        "fixed_sector_norm": float(prototype_row.get("fixed_sector_norm", 0.0)),
        "relative_response_error": float(prototype_row.get("relative_response_error", 0.0)),
        "seeded_pressure_relative_response_error": float(
            prototype_row.get("seeded_pressure_relative_response_error", 0.0)
        ),
    }
    missing_required_keys = [key for key in required_keys if key not in prefilled_values]
    production_missing_keys = [key for key in production_required_keys if key in missing_required_keys]
    template = {
        "row_id": prefilled_values["row_id"],
        "sites": prefilled_values["sites"],
        "u_over_t": prefilled_values["u_over_t"],
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "prefilled_values": prefilled_values,
        "required_row_keys": required_keys,
        "prefilled_required_keys": [key for key in required_keys if key in prefilled_values],
        "missing_required_keys": missing_required_keys,
        "production_required_keys": production_required_keys,
        "production_missing_keys": production_missing_keys,
        "prototype_trace_hash": prototype_row.get("prototype_trace_hash"),
        "prototype_discarded_weight_metric_present": bool(
            prototype_row.get("prototype_discarded_weight_metric_present")
        ),
        "submission_artifact_path": None,
        "submitted_production_row_present": False,
        "accepted_production_row": False,
    }
    template["template_hash"] = stable_hash(
        {
            "row_id": template["row_id"],
            "row_contract_hash": template["row_contract_hash"],
            "required_row_keys": required_keys,
            "production_required_keys": production_required_keys,
            "prototype_trace_hash": template["prototype_trace_hash"],
        }
    )
    return template


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    implementation_contract = load_json(args.implementation_contract)
    prototype_scout = load_json(args.prototype_scout)

    required_keys = implementation_contract["row_artifact_schema"]["required_row_keys"]
    prototype_rows = prototype_scout.get("rows", [])
    prototype_summary = prototype_scout.get("summary", {})

    prefilled_key_set = {
        "row_id",
        "sites",
        "u_over_t",
        "row_contract_hash",
        "sweep_count",
        "energy_variance",
        "fixed_sector_norm",
        "relative_response_error",
        "seeded_pressure_relative_response_error",
    }
    production_required_keys = [key for key in required_keys if key not in prefilled_key_set]
    template_rows = [
        build_template_row(row, required_keys, production_required_keys) for row in prototype_rows
    ]

    row_template_count = len(template_rows)
    template_hashes = [row["template_hash"] for row in template_rows]
    template_table_hash = stable_hash(template_rows)
    min_prefilled_key_count = min(
        (len(row["prefilled_required_keys"]) for row in template_rows), default=0
    )
    submitted_production_row_count = sum(row["submitted_production_row_present"] for row in template_rows)
    accepted_production_row_count = sum(row["accepted_production_row"] for row in template_rows)
    missing_required_key_total = sum(len(row["missing_required_keys"]) for row in template_rows)
    production_missing_key_total = sum(len(row["production_missing_keys"]) for row in template_rows)
    prototype_trace_hash_rows = sum(bool(row["prototype_trace_hash"]) for row in template_rows)

    requirements = [
        requirement(
            "I1",
            "W1 implementation contract and prototype scout are locked to the same row contract",
            implementation_contract["summary"].get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH
            and prototype_summary.get("row_contract_hash") == EXPECTED_ROW_CONTRACT_HASH,
            {
                "implementation_contract_hash": implementation_contract["summary"].get(
                    "row_contract_hash"
                ),
                "prototype_scout_hash": prototype_summary.get("row_contract_hash"),
            },
        ),
        requirement(
            "I2",
            "Nine production-row intake templates are generated",
            row_template_count == 9,
            {"row_template_count": row_template_count, "required_rows": 9},
        ),
        requirement(
            "I3",
            "Every template preserves the 17-key W1 row schema",
            all(len(row["required_row_keys"]) == 17 for row in template_rows),
            {
                "required_row_key_count": len(required_keys),
                "template_count": row_template_count,
            },
        ),
        requirement(
            "I4",
            "Prototype trace hashes are carried into all templates as provenance only",
            prototype_trace_hash_rows == 9,
            {"prototype_trace_hash_rows": prototype_trace_hash_rows, "required_rows": 9},
        ),
        requirement(
            "I5",
            "Submitted production-row artifacts exist for all locked rows",
            submitted_production_row_count == 9,
            {
                "submitted_production_row_count": submitted_production_row_count,
                "required_rows": 9,
            },
        ),
        requirement(
            "I6",
            "Canonical environment, residual, discarded-weight, and cost keys are populated",
            production_missing_key_total == 0,
            {
                "production_required_key_count": len(production_required_keys),
                "production_missing_key_total": production_missing_key_total,
            },
        ),
        requirement(
            "I7",
            "All submitted rows are accepted as production contract rows",
            accepted_production_row_count == 9,
            {
                "accepted_production_row_count": accepted_production_row_count,
                "required_rows": 9,
            },
        ),
        requirement(
            "I8",
            "Forbidden claims remain false while intake rows are missing",
            all(
                prototype_summary.get(key) is False
                for key in [
                    "production_dmrg_claimed",
                    "same_access_positive_route_claimed",
                    "quantum_advantage_claimed",
                    "bqp_separation_claimed",
                ]
            ),
            {
                "production_dmrg_claimed": prototype_summary.get("production_dmrg_claimed"),
                "same_access_positive_route_claimed": prototype_summary.get(
                    "same_access_positive_route_claimed"
                ),
                "quantum_advantage_claimed": prototype_summary.get("quantum_advantage_claimed"),
                "bqp_separation_claimed": prototype_summary.get("bqp_separation_claimed"),
            },
        ),
    ]
    passed = sum(1 for item in requirements if item["passed"])
    failed_ids = [item["requirement_id"] for item in requirements if not item["passed"]]

    validation_errors: list[str] = []
    if failed_ids != EXPECTED_FAILED_IDS:
        validation_errors.append(f"unexpected failed intake requirements: {failed_ids}")
    if row_template_count != 9:
        validation_errors.append("production-row intake template must preserve nine rows")
    if len(required_keys) != 17:
        validation_errors.append("W1 production-row schema should have 17 keys")
    if submitted_production_row_count != 0:
        validation_errors.append("template gate must not fabricate submitted production rows")
    if accepted_production_row_count != 0:
        validation_errors.append("template gate must not accept production rows")

    summary = {
        "row_contract_count": row_template_count,
        "row_contract_hash": EXPECTED_ROW_CONTRACT_HASH,
        "source_implementation_contract_status": implementation_contract.get("status"),
        "source_prototype_scout_status": prototype_scout.get("status"),
        "intake_requirement_count": len(requirements),
        "intake_requirements_passed": passed,
        "intake_requirements_failed": len(requirements) - passed,
        "failed_intake_requirement_ids": failed_ids,
        "required_row_key_count": len(required_keys),
        "prefilled_required_key_count_min": min_prefilled_key_count,
        "production_required_key_count": len(production_required_keys),
        "row_template_count": row_template_count,
        "template_hash_count": len(template_hashes),
        "template_table_hash": template_table_hash,
        "prototype_trace_hash_rows": prototype_trace_hash_rows,
        "submitted_production_row_count": submitted_production_row_count,
        "accepted_production_row_count": accepted_production_row_count,
        "missing_required_key_total": missing_required_key_total,
        "production_missing_key_total": production_missing_key_total,
        "w1_production_row_intake_ready": False,
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
        "title": "B5/B10 W1 Production Row Intake Template Gate v0",
        "version": VERSION,
        "last_updated": args.last_updated,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_implementation_contract_result": str(args.implementation_contract),
        "source_prototype_scout_result": str(args.prototype_scout),
        "summary": summary,
        "requirements": requirements,
        "production_required_keys": production_required_keys,
        "template_rows": template_rows,
        "claim_boundary": {
            "what_is_supported": (
                "The locked W1 row contract has been converted into nine row-level intake templates "
                "that carry prototype provenance and name the missing production fields explicitly."
            ),
            "what_is_not_supported": (
                "No submitted production rows, canonical environment hashes, residual norms, "
                "production discarded weights, cost rows, production DMRG denominator, positive "
                "same-access route, quantum advantage, or BQP separation are supported."
            ),
            "next_gate": (
                "Submit production-row artifacts for all nine templates with canonical center sites, "
                "left/right environment hashes, residual norms, discarded weights, wall-clock, memory, "
                "and sweep/matvec counts, then rerun the gate."
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
        "# B5/B10 W1 Production Row Intake Template Gate v0.1",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Row contract count/hash: {summary['row_contract_count']} / `{summary['row_contract_hash']}`",
        f"- Requirements passed/failed: {summary['intake_requirements_passed']} / {summary['intake_requirements_failed']}",
        f"- Failed requirement IDs: {summary['failed_intake_requirement_ids']}",
        f"- Required row keys / prefilled min / production-required keys: {summary['required_row_key_count']} / {summary['prefilled_required_key_count_min']} / {summary['production_required_key_count']}",
        f"- Template rows / template hashes: {summary['row_template_count']} / {summary['template_hash_count']}",
        f"- Template table hash: `{summary['template_table_hash']}`",
        f"- Prototype trace-hash rows: {summary['prototype_trace_hash_rows']}",
        f"- Submitted / accepted production rows: {summary['submitted_production_row_count']} / {summary['accepted_production_row_count']}",
        f"- Missing required keys total / production missing keys total: {summary['missing_required_key_total']} / {summary['production_missing_key_total']}",
        "",
        "## Production Required Keys",
        "",
        ", ".join(f"`{key}`" for key in payload["production_required_keys"]),
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
            "## Template Rows",
            "",
            "| row_id | prefilled keys | missing production keys | template hash |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for row in payload["template_rows"]:
        lines.append(
            f"| {row['row_id']} | {len(row['prefilled_required_keys'])} | "
            f"{len(row['production_missing_keys'])} | `{row['template_hash']}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
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
        lines.extend(f"- {error}" for error in payload["validation_errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--implementation-contract",
        type=Path,
        default=Path("results/B5_B10_w1_implementation_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--prototype-scout",
        type=Path,
        default=Path("results/B5_B10_w1_prototype_environment_scout_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B5_B10_w1_production_row_intake_template_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B5_B10_w1_production_row_intake_template_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-01")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    write_markdown(payload, args.markdown_output)
    print(payload["status"])
    print(
        payload["summary"]["intake_requirements_passed"],
        payload["summary"]["intake_requirements_failed"],
        payload["summary"]["failed_intake_requirement_ids"],
    )


if __name__ == "__main__":
    main()
