#!/usr/bin/env python3
"""Non-overlap bounded patch subset gate for B1/B7 cone_01.

T-B1-004at emitted bounded OpenQASM 3 snippets for all three repaired
reduced-CNOT packets, but the line-1378 and line-1381 source windows overlap.
This gate computes the best non-overlapping bounded patch subset before any
full-circuit replay claim is allowed.

The result is intentionally narrower than the prior naive signal: the
composable bounded subset keeps line 1381 and line 268, drops line 1378, and
reduces the candidate CNOT delta from 9 to 6 until a merged-region replay gate
or a new resynthesis recovers the overlapped saving.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    load_json,
    write_json,
    write_text,
)


ROOT = Path(__file__).resolve().parents[1]
PATCH_PATH = ROOT / "results" / "B1_B7_cone01_bounded_replacement_patch_gate_v0.json"
SOURCE_QASM_PATH = ROOT / "results" / "b1_native_t_resource_optimizer" / "qasmbench_medium_exact" / "gcm_h6.qasm"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_nonoverlap_patch_subset_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_nonoverlap_patch_subset_gate.md"

METHOD = "b1_b7_cone01_nonoverlap_patch_subset_gate_v0"
STATUS = "cone01_nonoverlap_bounded_patch_subset_not_full_circuit_replay"
MODEL_STATUS = "nonoverlap_subset_reduces_naive_patch_delta_before_full_circuit_replay"


def source_qasm_dialect(path: Path) -> str:
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped:
            return stripped.rstrip(";")
    return "unknown"


def overlaps(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return max(int(left["window_start_line"]), int(right["window_start_line"])) <= min(
        int(left["window_end_line"]), int(right["window_end_line"])
    )


def is_nonoverlap(rows: list[dict[str, Any]]) -> bool:
    return all(not overlaps(left, right) for left, right in itertools.combinations(rows, 2))


def subset_score(rows: list[dict[str, Any]]) -> tuple[int, int, int, tuple[int, ...]]:
    cnot_delta = sum(int(row["candidate_cnot_reduction"]) for row in rows)
    covered_lines = sum(
        int(row["window_end_line"]) - int(row["window_start_line"]) + 1 for row in rows
    )
    patch_count = len(rows)
    line_numbers = tuple(sorted(int(row["candidate_line_number"]) for row in rows))
    return (cnot_delta, covered_lines, -patch_count, line_numbers)


def best_nonoverlap_subset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: list[dict[str, Any]] = []
    for size in range(1, len(rows) + 1):
        for subset_tuple in itertools.combinations(rows, size):
            subset = list(subset_tuple)
            if is_nonoverlap(subset) and subset_score(subset) > subset_score(best):
                best = subset
    return sorted(best, key=lambda row: (int(row["window_start_line"]), int(row["window_end_line"])))


def build_payload() -> dict[str, Any]:
    source = load_json(PATCH_PATH)
    rows = source["bounded_replacement_patch_rows"]
    selected_rows = best_nonoverlap_subset(rows)
    selected_lines = {int(row["candidate_line_number"]) for row in selected_rows}
    dropped_rows = [
        row for row in rows if int(row["candidate_line_number"]) not in selected_lines
    ]
    naive_delta = int(
        source["summary"]["candidate_cnot_reduction_if_all_patches_accepted"]
    )
    selected_delta = sum(int(row["candidate_cnot_reduction"]) for row in selected_rows)
    accepted_removed = 0
    summary = {
        "source_bounded_patch_method": source.get("method"),
        "input_bounded_patch_count": len(rows),
        "input_bounded_patch_exact_pass_count": sum(
            1 for row in rows if row["bounded_patch_exact_pass"]
        ),
        "input_naive_candidate_cnot_reduction": naive_delta,
        "nonoverlap_subset_available": bool(selected_rows),
        "selected_nonoverlap_patch_count": len(selected_rows),
        "selected_candidate_line_numbers": [
            int(row["candidate_line_number"]) for row in selected_rows
        ],
        "dropped_overlap_candidate_line_numbers": [
            int(row["candidate_line_number"]) for row in dropped_rows
        ],
        "selected_bounded_patch_exact_pass_count": sum(
            1 for row in selected_rows if row["bounded_patch_exact_pass"]
        ),
        "selected_candidate_cnot_reduction": selected_delta,
        "lost_candidate_cnot_reduction_due_to_overlap": naive_delta - selected_delta,
        "selected_replacement_off_pi_over_four_parameter_count": sum(
            int(row["replacement_off_pi_over_four_parameter_count"]) for row in selected_rows
        ),
        "selected_source_window_line_count": sum(
            int(row["window_end_line"]) - int(row["window_start_line"]) + 1
            for row in selected_rows
        ),
        "selected_patch_qasm3_line_count": sum(
            int(row["qasm3_patch_line_count"]) for row in selected_rows
        ),
        "source_qasm_dialect": source_qasm_dialect(SOURCE_QASM_PATH),
        "replacement_patch_dialect": "OPENQASM 3 bounded snippets",
        "source_to_replacement_dialect_bridge_required": True,
        "full_circuit_qasm_rewrite_emitted": False,
        "accepted_full_circuit_qasm_patch_count": 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(
            0,
            (REQUIRED_OCCURRENCE_REMOVALS - accepted_removed) * PROXY_T_PER_OCCURRENCE,
        ),
        "nonoverlap_subset_claimed_as_full_circuit_patch": False,
        "full_circuit_rewrite_claimed": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
    }
    payload = {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "workload": source.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "source_bounded_replacement_patch_result": display_path(PATCH_PATH),
        "source_qasm": display_path(SOURCE_QASM_PATH),
        "summary": summary,
        "selected_nonoverlap_patch_rows": selected_rows,
        "dropped_overlap_patch_rows": dropped_rows,
        "claim_boundary": {
            "supported_claim": (
                "The best non-overlapping bounded patch subset keeps line 1381 and line 268, "
                "dropping line 1378 because its window is contained inside the line-1381 window."
            ),
            "unsupported_claims": [
                "The selected bounded subset is not yet a full-circuit QASM rewrite.",
                "The selected bounded subset is not yet a full-circuit replay certificate.",
                "The selected bounded subset does not recover the dropped line-1378 CNOT delta.",
                "No occurrence or proxy-T reduction is accepted by B7.",
            ],
            "nonoverlap_subset_claimed_as_full_circuit_patch": False,
            "full_circuit_rewrite_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }
    payload["summary"]["validation_error_count"] = len(validate_payload(payload))
    return payload


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload.get("summary", {})
    selected = payload.get("selected_nonoverlap_patch_rows", [])
    dropped = payload.get("dropped_overlap_patch_rows", [])
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    expected = {
        "input_bounded_patch_count": 3,
        "input_bounded_patch_exact_pass_count": 3,
        "input_naive_candidate_cnot_reduction": 9,
        "nonoverlap_subset_available": True,
        "selected_nonoverlap_patch_count": 2,
        "selected_candidate_line_numbers": [268, 1381],
        "dropped_overlap_candidate_line_numbers": [1378],
        "selected_bounded_patch_exact_pass_count": 2,
        "selected_candidate_cnot_reduction": 6,
        "lost_candidate_cnot_reduction_due_to_overlap": 3,
        "selected_replacement_off_pi_over_four_parameter_count": 5,
        "source_qasm_dialect": "OPENQASM 2.0",
        "source_to_replacement_dialect_bridge_required": True,
        "full_circuit_qasm_rewrite_emitted": False,
        "accepted_full_circuit_qasm_patch_count": 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
    }
    for field, value in expected.items():
        if summary.get(field) != value:
            errors.append(f"{field}_expected_{value}_got_{summary.get(field)}")
    if not is_nonoverlap(selected):
        errors.append("selected_rows_must_be_nonoverlapping")
    for row in selected:
        if row.get("bounded_patch_exact_pass") is not True:
            errors.append(f"line_{row.get('candidate_line_number')}_must_exact_pass")
        if row.get("accepted_full_circuit_qasm_patch") is not False:
            errors.append(f"line_{row.get('candidate_line_number')}_must_not_accept_full_patch")
    if [row.get("candidate_line_number") for row in dropped] != [1378]:
        errors.append("dropped_rows_must_be_line_1378_only")
    for field in [
        "nonoverlap_subset_claimed_as_full_circuit_patch",
        "full_circuit_rewrite_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False or payload.get("claim_boundary", {}).get(field) is not False:
            errors.append(f"{field}_must_remain_false")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 Non-Overlap Patch Subset Gate",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Input bounded patches / exact-pass patches: `{summary['input_bounded_patch_count']}` / `{summary['input_bounded_patch_exact_pass_count']}`",
        f"- Naive candidate CNOT reduction before overlap handling: `{summary['input_naive_candidate_cnot_reduction']}`",
        f"- Selected non-overlap patches: `{summary['selected_candidate_line_numbers']}`",
        f"- Dropped overlap patches: `{summary['dropped_overlap_candidate_line_numbers']}`",
        f"- Selected candidate CNOT reduction: `{summary['selected_candidate_cnot_reduction']}`",
        f"- Lost candidate CNOT reduction due to overlap: `{summary['lost_candidate_cnot_reduction_due_to_overlap']}`",
        f"- Source / replacement dialect: `{summary['source_qasm_dialect']}` / `{summary['replacement_patch_dialect']}`",
        f"- Full-circuit QASM rewrite emitted: `{summary['full_circuit_qasm_rewrite_emitted']}`",
        f"- Accepted full-circuit patch / replay / occurrence / proxy-T reduction: `{summary['accepted_full_circuit_qasm_patch_count']}` / `{summary['accepted_full_circuit_replay_certificate_count']}` / `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Selected Rows",
        "",
        "| Line | Window | Support | CNOT delta | QASM3 lines | Off-grid params |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for row in payload["selected_nonoverlap_patch_rows"]:
        lines.append(
            f"| {row['candidate_line_number']} | {row['window_start_line']}-{row['window_end_line']} | "
            f"{row['support_qubits']} | {row['candidate_cnot_reduction']} | "
            f"{row['qasm3_patch_line_count']} | {row['replacement_off_pi_over_four_parameter_count']} |"
        )
    lines.extend(
        [
            "",
            "## Dropped Rows",
            "",
            "| Line | Window | Reason |",
            "|---:|---|---|",
        ]
    )
    for row in payload["dropped_overlap_patch_rows"]:
        lines.append(
            f"| {row['candidate_line_number']} | {row['window_start_line']}-{row['window_end_line']} | "
            "contained in the selected line-1381 window under the same bounded patch family |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"]["supported_claim"],
            "",
            "Unsupported claims:",
            "",
        ]
    )
    for claim in payload["claim_boundary"]["unsupported_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "This gate prevents double-counting the overlapping line-1378 and line-1381 "
                "bounded patch snippets. The best current composable bounded subset carries a "
                "candidate 6-CNOT reduction, not the naive 9-CNOT signal. Recovering the lost "
                "3-CNOT delta requires a merged-region synthesis/replay gate or a different "
                "occurrence-removing route."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=JSON_OUT)
    parser.add_argument("--markdown-output", type=Path, default=MD_OUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.json_output, payload, True)
    write_text(args.markdown_output, render_markdown(payload))
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
