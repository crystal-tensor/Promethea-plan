#!/usr/bin/env python3
"""T-B5-006d/T-B10-014b: preserve the B5/B10 D5 row contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b5_b10_row_contract_harness_v0"
STATUS = "row_contract_preserved_guardrail_ready"
MODEL_STATUS = "w4_row_contract_harness_executed_no_positive_route"
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


def fmt_float(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def row_id(row: dict[str, Any]) -> str:
    return (
        f"D5H_s{row['sites']}_u{fmt_float(row['u_over_t'])}_eta{fmt_float(row['eta'])}"
        f"_n{row['n_up']}x{row['n_down']}_obs_density_site_{row['density_site']}"
    )


def reference_contract_rows(reference: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for index, row in enumerate(reference["rows"]):
        contract = {
            "row_index": index,
            "row_id": row_id(row),
            "sites": row["sites"],
            "u_over_t": row["u_over_t"],
            "eta": row["eta"],
            "t": row["t"],
            "n_up": row["n_up"],
            "n_down": row["n_down"],
            "density_site": row["density_site"],
            "model": row["model"],
            "family": row["family"],
            "observable": "density_response_susceptibility_proxy",
            "solver": row["solver"],
            "relative_residual_target": row["rtol"],
            "hilbert_dimension": row["hilbert_dimension"],
            "hamiltonian_nnz": row["hamiltonian_nnz"],
            "explicit_io_floor_units": row["explicit_io_floor_units"],
            "susceptibility_proxy": row["susceptibility_proxy"],
        }
        rows.append(contract)
    return rows


def sha256_json(value: Any) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compare_source_rows(
    source_name: str,
    payload: dict[str, Any],
    contract_rows: list[dict[str, Any]],
    required_fields: list[str],
) -> dict[str, Any]:
    rows = payload.get("rows", [])
    mismatches: list[dict[str, Any]] = []
    if len(rows) != len(contract_rows):
        mismatches.append(
            {
                "type": "row_count",
                "expected": len(contract_rows),
                "actual": len(rows),
            }
        )

    compared_rows = min(len(rows), len(contract_rows))
    row_checks = []
    for index in range(compared_rows):
        source_row = rows[index]
        contract_row = contract_rows[index]
        field_mismatches = []
        for field in required_fields:
            if source_row.get(field) != contract_row.get(field):
                field_mismatches.append(
                    {
                        "field": field,
                        "expected": contract_row.get(field),
                        "actual": source_row.get(field),
                    }
                )
        if field_mismatches:
            mismatches.append(
                {
                    "type": "field_mismatch",
                    "row_index": index,
                    "row_id": contract_row["row_id"],
                    "mismatches": field_mismatches,
                }
            )
        row_checks.append(
            {
                "row_index": index,
                "row_id": contract_row["row_id"],
                "required_fields": required_fields,
                "passed": not field_mismatches,
            }
        )

    return {
        "source_name": source_name,
        "method": payload.get("method"),
        "status": payload.get("status"),
        "row_count": len(rows),
        "required_fields": required_fields,
        "row_contract_preserved": not mismatches,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "row_checks": row_checks,
    }


def check_summary_count(source_name: str, payload: dict[str, Any], count_field: str) -> dict[str, Any]:
    summary = payload.get("summary", {})
    count = summary.get(count_field)
    return {
        "source_name": source_name,
        "method": payload.get("method"),
        "status": payload.get("status"),
        "count_field": count_field,
        "count": count,
        "row_contract_preserved": count == 9,
        "mismatch_count": 0 if count == 9 else 1,
        "mismatches": []
        if count == 9
        else [{"type": "summary_count", "field": count_field, "expected": 9, "actual": count}],
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    reference = load_json(args.d5_table)
    non_oracle = load_json(args.non_oracle)
    seeded_mps = load_json(args.seeded_mps)
    variational_mps = load_json(args.variational_mps)
    two_site = load_json(args.two_site)
    readiness = load_json(args.readiness)
    smoke = load_json(args.smoke)
    bridge = load_json(args.bridge)
    contract = load_json(args.production_contract)
    triage = load_json(args.production_triage)

    contract_rows = reference_contract_rows(reference)
    contract_hash = sha256_json(contract_rows)
    full_fields = ["sites", "u_over_t", "eta", "t", "model"]
    partial_fields = ["sites", "u_over_t"]

    source_checks = [
        compare_source_rows("B10 D5 denominator table", reference, contract_rows, full_fields),
        compare_source_rows("B5 non-oracle embedding baseline", non_oracle, contract_rows, full_fields),
        compare_source_rows("B5 exact-state-seeded MPS pressure", seeded_mps, contract_rows, full_fields),
        compare_source_rows("B5 variational MPS/ALS prototype", variational_mps, contract_rows, full_fields),
        compare_source_rows("B5 two-site finite-DMRG-style prototype", two_site, contract_rows, full_fields),
        compare_source_rows("B5 canonical-environment smoke gate", smoke, contract_rows, partial_fields),
        check_summary_count("B5 canonical DMRG readiness gate", readiness, "instance_count"),
        check_summary_count("B10 same-access bridge", bridge, "b5_instance_count"),
        check_summary_count("B5/B10 production contract", contract, "instance_count"),
    ]

    triage_summary = triage.get("summary", {})
    triage_work_packets = triage.get("work_packets", [])
    packet_ids = [packet.get("packet_id") for packet in triage_work_packets]
    w4 = next((packet for packet in triage_work_packets if packet.get("packet_id") == "W4"), {})
    source_checks.append(
        {
            "source_name": "B5/B10 production implementation triage",
            "method": triage.get("method"),
            "status": triage.get("status"),
            "count_field": "work_packet_count",
            "count": triage_summary.get("work_packet_count"),
            "packet_ids": packet_ids,
            "w4_status": w4.get("status"),
            "row_contract_preserved": triage_summary.get("work_packet_count") == 6
            and "W4" in packet_ids
            and w4.get("status") == "ready_now",
            "mismatch_count": 0
            if triage_summary.get("work_packet_count") == 6
            and "W4" in packet_ids
            and w4.get("status") == "ready_now"
            else 1,
            "mismatches": []
            if triage_summary.get("work_packet_count") == 6
            and "W4" in packet_ids
            and w4.get("status") == "ready_now"
            else [
                {
                    "type": "triage_w4",
                    "expected": "six packets including W4 ready_now",
                    "actual": {"work_packet_count": triage_summary.get("work_packet_count"), "packet_ids": packet_ids},
                }
            ],
        }
    )

    conditions = [
        {
            "condition_id": "R1",
            "label": "Reference D5 row contract has exactly nine rows",
            "satisfied": len(contract_rows) == 9,
            "evidence": {"row_count": len(contract_rows)},
        },
        {
            "condition_id": "R2",
            "label": "Reference rows preserve the 3x3 sites/u grid",
            "satisfied": sorted((row["sites"], row["u_over_t"]) for row in contract_rows)
            == [(4, 2.0), (4, 4.0), (4, 8.0), (6, 2.0), (6, 4.0), (6, 8.0), (8, 2.0), (8, 4.0), (8, 8.0)],
            "evidence": {"row_keys": [[row["sites"], row["u_over_t"]] for row in contract_rows]},
        },
        {
            "condition_id": "R3",
            "label": "All row-bearing B5 sources preserve row order and shared fields",
            "satisfied": all(check["row_contract_preserved"] for check in source_checks[:6]),
            "evidence": {
                "checked_sources": [check["source_name"] for check in source_checks[:6]],
                "mismatch_counts": {check["source_name"]: check["mismatch_count"] for check in source_checks[:6]},
            },
        },
        {
            "condition_id": "R4",
            "label": "Count-only gates preserve nine-instance scope",
            "satisfied": all(check["row_contract_preserved"] for check in source_checks[6:9]),
            "evidence": {
                "checked_sources": [check["source_name"] for check in source_checks[6:9]],
                "counts": {check["source_name"]: check["count"] for check in source_checks[6:9]},
            },
        },
        {
            "condition_id": "R5",
            "label": "Triage still exposes W4 as the row-contract packet",
            "satisfied": source_checks[-1]["row_contract_preserved"],
            "evidence": {"packet_ids": packet_ids, "w4_status": w4.get("status")},
        },
        {
            "condition_id": "R6",
            "label": "No positive route or forbidden claim is introduced",
            "satisfied": all(
                triage_summary.get(field) is False
                for field in [
                    "production_dmrg_claimed",
                    "quantum_response_win_claimed",
                    "accuracy_per_resource_win_claimed",
                    "same_access_positive_route_claimed",
                    "quantum_advantage_claimed",
                    "bqp_separation_claimed",
                    "dequantization_theorem_claimed",
                    "sampling_access_theorem_claimed",
                ]
            ),
            "evidence": {
                field: triage_summary.get(field)
                for field in [
                    "production_dmrg_claimed",
                    "quantum_response_win_claimed",
                    "accuracy_per_resource_win_claimed",
                    "same_access_positive_route_claimed",
                    "quantum_advantage_claimed",
                    "bqp_separation_claimed",
                    "dequantization_theorem_claimed",
                    "sampling_access_theorem_claimed",
                ]
            },
        },
    ]

    validation_errors: list[str] = []
    for condition in conditions:
        if not condition["satisfied"]:
            validation_errors.append(f"{condition['condition_id']} failed: {condition['label']}")
    for check in source_checks:
        if not check["row_contract_preserved"]:
            validation_errors.append(f"{check['source_name']} row contract mismatch")

    summary = {
        "row_contract_source": str(args.d5_table),
        "row_contract_hash": contract_hash,
        "row_contract_count": len(contract_rows),
        "source_check_count": len(source_checks),
        "source_checks_passed": sum(1 for check in source_checks if check["row_contract_preserved"]),
        "source_checks_failed": sum(1 for check in source_checks if not check["row_contract_preserved"]),
        "condition_count": len(conditions),
        "conditions_satisfied": sum(1 for condition in conditions if condition["satisfied"]),
        "conditions_failed": sum(1 for condition in conditions if not condition["satisfied"]),
        "w4_row_contract_harness_executed": True,
        "w6_audit_wiring_required": True,
        "remaining_positive_route_packets": ["W1", "W2", "W3"],
        "remaining_theory_integration_packet": "W5",
        "production_dmrg_available": False,
        "sampling_oracle_constructed": False,
        "same_access_positive_route_ready": False,
        "b10_t1_positive_route_ready": False,
        "catalog_change_required": False,
        "production_dmrg_claimed": False,
        "quantum_response_win_claimed": False,
        "accuracy_per_resource_win_claimed": False,
        "same_access_positive_route_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "dequantization_theorem_claimed": False,
        "sampling_access_theorem_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B5",
        "linked_benchmark_id": "B10",
        "problem_id": 5,
        "linked_problem_id": 10,
        "title": "B5/B10 D5 Row-Contract Harness",
        "version": VERSION,
        "last_updated": time.strftime("%Y-%m-%d"),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_d5_table": str(args.d5_table),
        "source_non_oracle_embedding_result": str(args.non_oracle),
        "source_seeded_mps_pressure_result": str(args.seeded_mps),
        "source_variational_mps_als_result": str(args.variational_mps),
        "source_two_site_dmrg_result": str(args.two_site),
        "source_readiness_result": str(args.readiness),
        "source_smoke_result": str(args.smoke),
        "source_same_access_bridge_result": str(args.bridge),
        "source_production_contract_result": str(args.production_contract),
        "source_production_triage_result": str(args.production_triage),
        "summary": summary,
        "contract_rows": contract_rows,
        "source_checks": source_checks,
        "conditions": conditions,
        "claim_boundary": {
            "what_is_supported": (
                "The B5/B10 D5 row contract is now machine-checkable across the current denominator ladder, "
                "readiness/smoke gates, production contract, and triage queue."
            ),
            "what_is_not_supported": (
                "This harness is not a new denominator, not production DMRG, not a response oracle, "
                "not a positive same-access route, not quantum advantage, and not BQP separation."
            ),
            "next_gate": (
                "Future W1/W2/W3 outputs must preserve the row_contract_hash and the nine row IDs before "
                "they can be compared against the current ladder."
            ),
            "production_dmrg_claimed": False,
            "quantum_response_win_claimed": False,
            "accuracy_per_resource_win_claimed": False,
            "same_access_positive_route_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "dequantization_theorem_claimed": False,
            "sampling_access_theorem_claimed": False,
        },
        "runtime_seconds": round(time.time() - started, 6),
        "validation_errors": validation_errors,
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    s = payload["summary"]
    cb = payload["claim_boundary"]
    lines = [
        "# B5/B10 Row-Contract Harness v0.1",
        "",
        f"Last updated: {payload['last_updated']}",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Row contract count: {s['row_contract_count']}",
        f"- Row contract hash: `{s['row_contract_hash']}`",
        f"- Source checks passed/failed: {s['source_checks_passed']} / {s['source_checks_failed']}",
        f"- Conditions satisfied/failed: {s['conditions_satisfied']} / {s['conditions_failed']}",
        f"- W4 row-contract harness executed: {s['w4_row_contract_harness_executed']}",
        f"- Remaining positive-route packets: {', '.join(s['remaining_positive_route_packets'])}",
        f"- Validation errors: {s['validation_error_count']}",
        "",
        "## Contract Rows",
        "",
        "| Row | Row ID | sites | U/t | eta | n_up/n_down | observable | Hilbert dim |",
        "|---:|---|---:|---:|---:|---|---|---:|",
    ]
    for row in payload["contract_rows"]:
        lines.append(
            f"| {row['row_index']} | `{row['row_id']}` | {row['sites']} | {row['u_over_t']} | "
            f"{row['eta']} | {row['n_up']}/{row['n_down']} | {row['observable']} | {row['hilbert_dimension']} |"
        )
    lines.extend(
        [
            "",
            "## Source Checks",
            "",
            "| Source | Rows/count | Passed | Mismatches |",
            "|---|---:|---:|---:|",
        ]
    )
    for check in payload["source_checks"]:
        rows_or_count = check.get("row_count", check.get("count"))
        lines.append(
            f"| {check['source_name']} | {rows_or_count} | {check['row_contract_preserved']} | {check['mismatch_count']} |"
        )
    lines.extend(
        [
            "",
            "## Conditions",
            "",
            "| Condition | Satisfied | Evidence |",
            "|---|---:|---|",
        ]
    )
    for condition in payload["conditions"]:
        evidence = "; ".join(f"{key}={value}" for key, value in condition["evidence"].items())
        lines.append(f"| {condition['condition_id']}: {condition['label']} | {condition['satisfied']} | {evidence} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "W4 is now executed as an auditable harness instead of a prose reminder.",
            "The harness does not improve B5/B10 accuracy. It prevents future W1/W2/W3 outputs from changing the benchmark rows while claiming a denominator win.",
            "Any future positive route must preserve the contract hash before cost or accuracy comparisons are accepted.",
            "",
            "## Claim Boundary",
            "",
        ]
    )
    for key, value in cb.items():
        lines.append(f"- {key}: {value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--d5-table", type=Path, default=Path("results/B10_t1_d5_observable_denominator_table_v0.json"))
    parser.add_argument("--non-oracle", type=Path, default=Path("results/B5_non_oracle_response_embedding_baseline_v0.json"))
    parser.add_argument("--seeded-mps", type=Path, default=Path("results/B5_mps_truncation_response_reference_v0.json"))
    parser.add_argument("--variational-mps", type=Path, default=Path("results/B5_variational_mps_als_response_reference_v0.json"))
    parser.add_argument("--two-site", type=Path, default=Path("results/B5_two_site_dmrg_response_reference_v0.json"))
    parser.add_argument("--readiness", type=Path, default=Path("results/B5_canonical_dmrg_readiness_gate_v0.json"))
    parser.add_argument("--smoke", type=Path, default=Path("results/B5_canonical_environment_smoke_gate_v0.json"))
    parser.add_argument("--bridge", type=Path, default=Path("results/B10_t1_b5_same_access_sampling_or_dmrg_bridge_v0.json"))
    parser.add_argument(
        "--production-contract",
        type=Path,
        default=Path("results/B5_B10_same_access_production_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--production-triage",
        type=Path,
        default=Path("results/B5_B10_production_implementation_triage_gate_v0.json"),
    )
    parser.add_argument("--json-output", type=Path, default=Path("results/B5_B10_row_contract_harness_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B5_B10_row_contract_harness.md"))
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    write_json(args.json_output, payload, pretty=args.pretty)
    write_markdown(args.markdown_output, payload)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "row_contract_count": payload["summary"]["row_contract_count"],
                "source_checks_passed": payload["summary"]["source_checks_passed"],
                "source_checks_failed": payload["summary"]["source_checks_failed"],
                "validation_errors": payload["validation_errors"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B5/B10 row-contract harness validation failed")


if __name__ == "__main__":
    main()
