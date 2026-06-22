#!/usr/bin/env python3
"""Low-CNOT union-region search gate for B1/B7 cone_01.

T-B1-004bd showed that the dropped line-1378 delta cannot be added on top of
the line-1381 replacement. This gate tests the honest alternative: synthesize
the union region itself with fewer CNOTs than the current 2-CNOT line-1381
replacement.

The search is intentionally scoped and conservative. It checks 0-CNOT and
1-CNOT local-U3 scaffolds for the line-1378/1381 union target, with both CNOT
orientations for the 1-CNOT case. Failure here is not a global lower bound; it
is a reproducible pressure test showing that this narrow low-CNOT route does
not recover additional delta or B7 credit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    load_json,
    write_json,
    write_text,
)
from b1_b7_cone01_packet_synthesis_search_gate import (
    EXACT_TOLERANCE,
    optimize_scaffold,
    target_matrix,
)


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_PACKET_PATH = ROOT / "results" / "B1_B7_cone01_semantic_replay_packet_gate_v0.json"
SYNTHESIS_PATH = ROOT / "results" / "B1_B7_cone01_packet_synthesis_search_gate_v0.json"
OVERLAP_BOUND_PATH = ROOT / "results" / "B1_B7_cone01_overlap_additivity_bound_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_union_region_low_cnot_search_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_union_region_low_cnot_search_gate.md"

METHOD = "b1_b7_cone01_union_region_low_cnot_search_gate_v0"
STATUS = "cone01_union_region_low_cnot_search_no_extra_delta"
MODEL_STATUS = "union_region_zero_one_cnot_scaffolds_fail_both_orientations"
DEFAULT_SEED_COUNT = 16
DEFAULT_MAX_NFEV = 2200


def line_packet(payload: dict[str, Any], line_number: int) -> dict[str, Any]:
    for packet in payload.get("semantic_replay_packets", []):
        if int(packet["candidate_line_number"]) == line_number:
            return packet
    raise ValueError(f"missing semantic packet line {line_number}")


def synthesis_row(payload: dict[str, Any], line_number: int) -> dict[str, Any]:
    for row in payload.get("packet_synthesis_rows", []):
        if int(row["candidate_line_number"]) == line_number:
            return row
    raise ValueError(f"missing synthesis row line {line_number}")


def best_existing_exact_cnot(row: dict[str, Any]) -> int | None:
    exact = [
        int(scaffold["cnot_count"])
        for scaffold in row.get("scaffold_results", [])
        if scaffold.get("exact_pass") is True
    ]
    return min(exact) if exact else None


def orientation_searches(
    packet: dict[str, Any],
    seed_count: int,
    max_nfev: int,
) -> list[dict[str, Any]]:
    target = target_matrix(packet)
    searches: list[dict[str, Any]] = []
    for cnot_count, orientations in [
        (0, [(0, 1)]),
        (1, [(0, 1), (1, 0)]),
    ]:
        for control, target_qubit in orientations:
            result = optimize_scaffold(
                packet,
                cnot_count,
                target,
                control,
                target_qubit,
                seed_count,
                max_nfev,
            )
            best = result["best"]
            searches.append(
                {
                    "cnot_count": cnot_count,
                    "local_control": control,
                    "local_target": target_qubit,
                    "seed_count": seed_count,
                    "max_nfev": max_nfev,
                    "best_residual_norm": best["residual_norm"],
                    "best_max_abs_entry_error": best["max_abs_entry_error"],
                    "best_seed_index": best["seed_index"],
                    "best_optimizer_nfev": best["optimizer_nfev"],
                    "best_parameter_count": result["parameter_count"],
                    "best_off_pi_over_four_parameter_count": best["parameter_stats"][
                        "off_pi_over_four_grid_parameter_count"
                    ],
                    "exact_pass": result["exact_pass"],
                }
            )
    return searches


def run_probe(seed_count: int, max_nfev: int) -> dict[str, Any]:
    semantic = load_json(SEMANTIC_PACKET_PATH)
    synthesis = load_json(SYNTHESIS_PATH)
    overlap = load_json(OVERLAP_BOUND_PATH)
    packet = line_packet(semantic, 1381)
    existing = synthesis_row(synthesis, 1381)
    searches = orientation_searches(packet, seed_count, max_nfev)
    exact_low_cnot = [row for row in searches if row["exact_pass"]]
    best_low_cnot = min(searches, key=lambda row: row["best_residual_norm"])
    current_min_exact = best_existing_exact_cnot(existing)
    source_cnot_count = int(packet["cx_count"])
    current_replacement_cnot = int(current_min_exact) if current_min_exact is not None else None
    current_delta = source_cnot_count - current_replacement_cnot if current_replacement_cnot is not None else 0
    best_low_cnot_exact = min((row["cnot_count"] for row in exact_low_cnot), default=None)
    low_cnot_extra_delta = (
        current_replacement_cnot - best_low_cnot_exact
        if best_low_cnot_exact is not None and current_replacement_cnot is not None
        else 0
    )
    accepted_removed = 0
    summary = {
        "source_semantic_packet_method": semantic.get("method"),
        "source_packet_synthesis_method": synthesis.get("method"),
        "source_overlap_bound_method": overlap.get("method"),
        "target_line_number": 1381,
        "union_window": [int(packet["window_start_line"]), int(packet["window_end_line"])],
        "support_qubits": packet.get("support_qubits"),
        "source_cnot_count": source_cnot_count,
        "current_min_exact_replacement_cnot_count": current_replacement_cnot,
        "current_candidate_cnot_delta": current_delta,
        "searched_cnot_counts": [0, 1],
        "searched_orientation_count": len(searches),
        "search_seed_count_per_orientation": seed_count,
        "search_max_nfev": max_nfev,
        "low_cnot_exact_pass_count": len(exact_low_cnot),
        "zero_cnot_exact_pass_count": sum(
            1 for row in searches if row["cnot_count"] == 0 and row["exact_pass"]
        ),
        "one_cnot_exact_pass_count": sum(
            1 for row in searches if row["cnot_count"] == 1 and row["exact_pass"]
        ),
        "best_low_cnot_residual_norm": best_low_cnot["best_residual_norm"],
        "best_low_cnot_max_abs_entry_error": best_low_cnot["best_max_abs_entry_error"],
        "best_low_cnot_cnot_count": best_low_cnot["cnot_count"],
        "best_low_cnot_orientation": [
            best_low_cnot["local_control"],
            best_low_cnot["local_target"],
        ],
        "best_low_cnot_exact_replacement_cnot_count": best_low_cnot_exact,
        "extra_delta_found_beyond_current_line1381_replacement": low_cnot_extra_delta,
        "line1378_full_delta_recovered": False,
        "low_cnot_union_rewrite_emitted": False,
        "low_cnot_union_replay_certificate_count": 0,
        "global_lower_bound_claimed": False,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_full_circuit_qasm_patch_count": 0,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(
            0,
            (REQUIRED_OCCURRENCE_REMOVALS - accepted_removed) * PROXY_T_PER_OCCURRENCE,
        ),
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": 0,
    }
    payload = {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "source_semantic_packet_result": display_path(SEMANTIC_PACKET_PATH),
        "source_packet_synthesis_result": display_path(SYNTHESIS_PATH),
        "source_overlap_bound_result": display_path(OVERLAP_BOUND_PATH),
        "summary": summary,
        "union_region_low_cnot_search_rows": searches,
        "claim_boundary": {
            "supported_claim": (
                "Within the tested 0/1-CNOT local-U3 scaffold family, both CNOT "
                "orientations fail for the line-1378/1381 union target, while the "
                "existing 2-CNOT line-1381 replacement remains the current exact "
                "candidate in this branch."
            ),
            "unsupported_claims": [
                "This is not a global two-qubit CNOT lower-bound theorem.",
                "This does not emit a new union-region rewrite.",
                "This does not recover the dropped line-1378 delta.",
                "This does not improve the B7 ledger.",
            ],
            "global_lower_bound_claimed": False,
            "low_cnot_union_rewrite_emitted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }
    return payload


def markdown_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 Union-Region Low-CNOT Search Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- Source semantic packet: `{payload['source_semantic_packet_result']}`",
        f"- Source packet synthesis: `{payload['source_packet_synthesis_result']}`",
        f"- Source overlap bound: `{payload['source_overlap_bound_result']}`",
        "",
        "## Result",
        "",
        f"- Union window: `{summary['union_window']}`",
        f"- Support qubits: `{summary['support_qubits']}`",
        f"- Source CNOT count: `{summary['source_cnot_count']}`",
        f"- Current exact replacement CNOT count: `{summary['current_min_exact_replacement_cnot_count']}`",
        f"- Current candidate CNOT delta: `{summary['current_candidate_cnot_delta']}`",
        f"- Searched CNOT counts: `{summary['searched_cnot_counts']}`",
        f"- Searched orientations: `{summary['searched_orientation_count']}`",
        f"- 0-CNOT / 1-CNOT exact pass count: `{summary['zero_cnot_exact_pass_count']}` / `{summary['one_cnot_exact_pass_count']}`",
        f"- Best low-CNOT residual / entry error: `{summary['best_low_cnot_residual_norm']}` / `{summary['best_low_cnot_max_abs_entry_error']}`",
        f"- Extra delta found beyond current replacement: `{summary['extra_delta_found_beyond_current_line1381_replacement']}`",
        f"- Global lower bound claimed: `{summary['global_lower_bound_claimed']}`",
        f"- Accepted occurrence / proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        "",
        "## Claim Boundary",
        "",
        "- This is a scoped numerical search failure for 0/1-CNOT union-region scaffolds, not a theorem.",
        "- The current branch still has no accepted occurrence removal, proxy-T reduction, or B7 ledger improvement.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-count", type=int, default=DEFAULT_SEED_COUNT)
    parser.add_argument("--max-nfev", type=int, default=DEFAULT_MAX_NFEV)
    parser.add_argument("--json-output", default=str(JSON_OUT))
    parser.add_argument("--markdown-output", default=str(MD_OUT))
    args = parser.parse_args()
    payload = run_probe(args.seed_count, args.max_nfev)
    write_json(Path(args.json_output), payload, True)
    write_text(Path(args.markdown_output), markdown_report(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
