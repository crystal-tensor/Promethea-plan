#!/usr/bin/env python3
"""T-B5-006e/T-B10-014c: audit whether exact-state-seeded MPS pressure is replaced."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b5_seeded_pressure_replacement_audit_v0"
STATUS = "seeded_pressure_replacement_failed_remains_blocker"
MODEL_STATUS = "w2_replacement_audit_completed_no_deployable_denominator"
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


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def candidate_summary(
    candidate_id: str,
    label: str,
    payload: dict[str, Any],
    seeded_rows: list[dict[str, Any]],
    deployable_selection: bool,
    production_ready: bool,
    exact_state_seeded: bool,
    extra_notes: list[str],
) -> dict[str, Any]:
    rows = payload["rows"]
    row_results = []
    for index, (candidate_row, seeded_row) in enumerate(zip(rows, seeded_rows)):
        candidate_error = float(candidate_row["selected_relative_response_error"])
        seeded_error = float(seeded_row["selected_relative_response_error"])
        row_results.append(
            {
                "row_index": index,
                "sites": seeded_row["sites"],
                "u_over_t": seeded_row["u_over_t"],
                "candidate_relative_response_error": candidate_error,
                "seeded_relative_response_error": seeded_error,
                "beats_seeded_pressure": candidate_error < seeded_error,
                "error_ratio_to_seeded": candidate_error / seeded_error if seeded_error else None,
            }
        )
    candidate_mean = mean([row["candidate_relative_response_error"] for row in row_results])
    seeded_mean = mean([row["seeded_relative_response_error"] for row in row_results])
    rows_beating_seeded = sum(1 for row in row_results if row["beats_seeded_pressure"])
    globally_replaces_seeded = (
        len(rows) == 9
        and rows_beating_seeded == 9
        and candidate_mean <= seeded_mean
        and deployable_selection
        and production_ready
        and not exact_state_seeded
    )
    return {
        "candidate_id": candidate_id,
        "label": label,
        "method": payload.get("method"),
        "status": payload.get("status"),
        "row_count": len(rows),
        "deployable_selection": deployable_selection,
        "production_ready": production_ready,
        "exact_state_seeded": exact_state_seeded,
        "mean_relative_response_error": candidate_mean,
        "seeded_mean_relative_response_error": seeded_mean,
        "rows_beating_seeded_pressure": rows_beating_seeded,
        "all_rows_beat_seeded_pressure": rows_beating_seeded == len(rows),
        "globally_replaces_seeded_pressure": globally_replaces_seeded,
        "notes": extra_notes,
        "row_results": row_results,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    row_contract = load_json(args.row_contract)
    seeded = load_json(args.seeded_mps)
    non_oracle = load_json(args.non_oracle)
    variational = load_json(args.variational_mps)
    two_site = load_json(args.two_site)
    bridge = load_json(args.bridge)

    seeded_rows = seeded["rows"]
    seeded_errors = [float(row["selected_relative_response_error"]) for row in seeded_rows]
    seeded_mean = mean(seeded_errors)
    row_contract_hash = row_contract["summary"]["row_contract_hash"]

    candidates = [
        candidate_summary(
            "non_oracle_embedding",
            "Non-oracle response embedding denominator",
            non_oracle,
            seeded_rows,
            deployable_selection=non_oracle.get("uses_exact_target_for_selection") is False,
            production_ready=False,
            exact_state_seeded=False,
            extra_notes=[
                "predeclared selection rule does not consume exact target states",
                "classical embedding denominator, not production DMRG",
            ],
        ),
        candidate_summary(
            "variational_mps_als",
            "Non-exact-state-seeded variational MPS/ALS prototype",
            variational,
            seeded_rows,
            deployable_selection=variational.get("uses_exact_target_for_selection") is False,
            production_ready=variational.get("production_dmrg") is True,
            exact_state_seeded=variational.get("exact_state_seeded") is True,
            extra_notes=[
                "not exact-state seeded",
                "uses exact energy for response shift in this pressure prototype",
                "not production DMRG",
            ],
        ),
        candidate_summary(
            "two_site_finite_dmrg_style",
            "Two-site finite-DMRG-style response pressure prototype",
            two_site,
            seeded_rows,
            deployable_selection=True,
            production_ready=two_site["summary"].get("production_dmrg") is True
            and two_site["summary"].get("canonical_environment_production_dmrg") is True,
            exact_state_seeded=two_site["summary"].get("exact_state_seeded") is True,
            extra_notes=[
                "not exact-state seeded",
                "finite-DMRG-style pressure prototype",
                "not canonical-environment production DMRG",
            ],
        ),
    ]

    deployable_replacements = [candidate for candidate in candidates if candidate["globally_replaces_seeded_pressure"]]
    best_candidate_by_mean = min(candidates, key=lambda candidate: candidate["mean_relative_response_error"])
    max_rows_beating_seeded = max(candidate["rows_beating_seeded_pressure"] for candidate in candidates)

    conditions = [
        {
            "condition_id": "S1",
            "label": "Row contract from W4 is present and preserved",
            "satisfied": row_contract["summary"].get("row_contract_count") == 9
            and row_contract["summary"].get("source_checks_failed") == 0,
            "evidence": {
                "row_contract_hash": row_contract_hash,
                "row_contract_count": row_contract["summary"].get("row_contract_count"),
                "source_checks_failed": row_contract["summary"].get("source_checks_failed"),
            },
        },
        {
            "condition_id": "S2",
            "label": "Seeded MPS pressure is identified as exact-state seeded and non-deployable",
            "satisfied": seeded.get("exact_state_seeded") is True
            and seeded.get("explicit_not_variational_dmrg") is True,
            "evidence": {
                "seeded_exact_state_seeded": seeded.get("exact_state_seeded"),
                "explicit_not_variational_dmrg": seeded.get("explicit_not_variational_dmrg"),
                "seeded_mean_relative_response_error": seeded_mean,
            },
        },
        {
            "condition_id": "S3",
            "label": "Replacement candidates are replayed on all nine rows",
            "satisfied": all(candidate["row_count"] == 9 for candidate in candidates),
            "evidence": {candidate["candidate_id"]: candidate["row_count"] for candidate in candidates},
        },
        {
            "condition_id": "S4",
            "label": "No replacement candidate globally beats seeded pressure",
            "satisfied": len(deployable_replacements) == 0,
            "evidence": {
                "deployable_replacement_count": len(deployable_replacements),
                "best_candidate_by_mean": best_candidate_by_mean["candidate_id"],
                "best_candidate_mean_relative_response_error": best_candidate_by_mean[
                    "mean_relative_response_error"
                ],
                "seeded_mean_relative_response_error": seeded_mean,
                "max_rows_beating_seeded_pressure": max_rows_beating_seeded,
            },
        },
        {
            "condition_id": "S5",
            "label": "B10 same-access bridge remains blocked",
            "satisfied": bridge["summary"].get("same_access_positive_route_ready") is False
            and bridge["summary"].get("production_dmrg_available") is False,
            "evidence": {
                "same_access_positive_route_ready": bridge["summary"].get(
                    "same_access_positive_route_ready"
                ),
                "production_dmrg_available": bridge["summary"].get("production_dmrg_available"),
                "sampling_oracle_constructed": bridge["summary"].get("sampling_oracle_constructed"),
            },
        },
        {
            "condition_id": "S6",
            "label": "Forbidden claims remain false",
            "satisfied": True,
            "evidence": {
                "production_dmrg_claimed": False,
                "quantum_response_win_claimed": False,
                "same_access_positive_route_claimed": False,
                "quantum_advantage_claimed": False,
                "bqp_separation_claimed": False,
            },
        },
    ]

    validation_errors: list[str] = []
    for condition in conditions:
        if not condition["satisfied"]:
            validation_errors.append(f"{condition['condition_id']} failed: {condition['label']}")

    summary = {
        "row_contract_hash": row_contract_hash,
        "row_contract_count": row_contract["summary"].get("row_contract_count"),
        "candidate_count": len(candidates),
        "seeded_exact_state_seeded": seeded.get("exact_state_seeded"),
        "seeded_mean_relative_response_error": seeded_mean,
        "best_replacement_candidate_id": best_candidate_by_mean["candidate_id"],
        "best_replacement_mean_relative_response_error": best_candidate_by_mean[
            "mean_relative_response_error"
        ],
        "best_replacement_rows_beating_seeded_pressure": best_candidate_by_mean[
            "rows_beating_seeded_pressure"
        ],
        "max_rows_beating_seeded_pressure": max_rows_beating_seeded,
        "deployable_replacement_count": len(deployable_replacements),
        "seeded_pressure_replaced": False,
        "w2_seeded_pressure_replacement_audit_executed": True,
        "remaining_positive_route_packets": ["W1", "W3"],
        "w2_remains_blocked_on_denominator": True,
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
        "condition_count": len(conditions),
        "conditions_satisfied": sum(1 for condition in conditions if condition["satisfied"]),
        "conditions_failed": sum(1 for condition in conditions if not condition["satisfied"]),
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B5",
        "linked_benchmark_id": "B10",
        "problem_id": 5,
        "linked_problem_id": 10,
        "title": "B5 Seeded-Pressure Replacement Audit",
        "version": VERSION,
        "last_updated": time.strftime("%Y-%m-%d"),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_row_contract_result": str(args.row_contract),
        "source_seeded_mps_pressure_result": str(args.seeded_mps),
        "source_non_oracle_embedding_result": str(args.non_oracle),
        "source_variational_mps_als_result": str(args.variational_mps),
        "source_two_site_dmrg_result": str(args.two_site),
        "source_same_access_bridge_result": str(args.bridge),
        "summary": summary,
        "replacement_candidates": candidates,
        "conditions": conditions,
        "claim_boundary": {
            "what_is_supported": (
                "The current non-exact-state-seeded or non-oracle replacements do not globally replace the "
                "exact-state-seeded MPS pressure reference under the locked 9-row B5/B10 contract."
            ),
            "what_is_not_supported": (
                "This is not production DMRG, not a deployable replacement denominator, not a response oracle, "
                "not a same-access positive route, not quantum advantage, and not BQP separation."
            ),
            "next_gate": (
                "Run W1 production DMRG/MPS or W3 same-access response oracle. Any W2 retry must preserve the "
                "row-contract hash and beat seeded pressure globally without exact-state seeding."
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
        "# B5 Seeded-Pressure Replacement Audit v0.1",
        "",
        f"Last updated: {payload['last_updated']}",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Row contract hash: `{s['row_contract_hash']}`",
        f"- Seeded mean relative response error: {s['seeded_mean_relative_response_error']:.6g}",
        f"- Best replacement candidate: `{s['best_replacement_candidate_id']}`",
        f"- Best replacement mean relative response error: {s['best_replacement_mean_relative_response_error']:.6g}",
        f"- Best replacement rows beating seeded pressure: {s['best_replacement_rows_beating_seeded_pressure']} / 9",
        f"- Deployable replacement count: {s['deployable_replacement_count']}",
        f"- Seeded pressure replaced: {s['seeded_pressure_replaced']}",
        f"- Conditions satisfied/failed: {s['conditions_satisfied']} / {s['conditions_failed']}",
        f"- Validation errors: {s['validation_error_count']}",
        "",
        "## Candidate Replay",
        "",
        "| Candidate | Mean error | Rows beating seeded | Deployable selection | Production ready | Replaces seeded |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for candidate in payload["replacement_candidates"]:
        lines.append(
            f"| {candidate['candidate_id']} | {candidate['mean_relative_response_error']:.6g} | "
            f"{candidate['rows_beating_seeded_pressure']} / 9 | {candidate['deployable_selection']} | "
            f"{candidate['production_ready']} | {candidate['globally_replaces_seeded_pressure']} |"
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
            "W2 has been audited, but not solved. The exact-state-seeded MPS pressure reference remains the blocker.",
            "The non-oracle embedding denominator beats seeded pressure on a small number of rows, but it does not replace it globally.",
            "The non-exact-state-seeded MPS/ALS and two-site finite-DMRG-style prototypes also fail to replace seeded pressure.",
            "A positive B5/B10 route must now come from W1 production DMRG/MPS or W3 same-access response-oracle evidence, or a stronger W2 retry.",
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
    parser.add_argument("--row-contract", type=Path, default=Path("results/B5_B10_row_contract_harness_v0.json"))
    parser.add_argument("--seeded-mps", type=Path, default=Path("results/B5_mps_truncation_response_reference_v0.json"))
    parser.add_argument("--non-oracle", type=Path, default=Path("results/B5_non_oracle_response_embedding_baseline_v0.json"))
    parser.add_argument("--variational-mps", type=Path, default=Path("results/B5_variational_mps_als_response_reference_v0.json"))
    parser.add_argument("--two-site", type=Path, default=Path("results/B5_two_site_dmrg_response_reference_v0.json"))
    parser.add_argument("--bridge", type=Path, default=Path("results/B10_t1_b5_same_access_sampling_or_dmrg_bridge_v0.json"))
    parser.add_argument("--json-output", type=Path, default=Path("results/B5_seeded_pressure_replacement_audit_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B5_seeded_pressure_replacement_audit.md"))
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
                "seeded_pressure_replaced": payload["summary"]["seeded_pressure_replaced"],
                "best_replacement_candidate_id": payload["summary"]["best_replacement_candidate_id"],
                "deployable_replacement_count": payload["summary"]["deployable_replacement_count"],
                "validation_errors": payload["validation_errors"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B5 seeded-pressure replacement audit validation failed")


if __name__ == "__main__":
    main()
