#!/usr/bin/env python3
"""Two-CNOT orientation census gate for the B1/B7 cone_01 union region.

T-B1-004be ruled out the 0/1-CNOT union-region shortcut. This gate checks the
next honest boundary: all length-2 CNOT direction sequences on the same
line-1378/1381 union target, with arbitrary local U3 layers between CNOTs.

The result is still candidate synthesis evidence only. It confirms whether a
2-CNOT union-region scaffold is numerically reachable across the direction
space, records the local-U3 parameter pressure, and keeps B7 credit at zero
until a replayable full-circuit patch and pricing proof exist.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import least_squares

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
    cx_on,
    parameter_stats,
    pair_layer,
    phase_align,
    residual_vector,
    target_matrix,
    wrap_angles,
)


ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_PACKET_PATH = ROOT / "results" / "B1_B7_cone01_semantic_replay_packet_gate_v0.json"
SYNTHESIS_PATH = ROOT / "results" / "B1_B7_cone01_packet_synthesis_search_gate_v0.json"
LOW_CNOT_PATH = ROOT / "results" / "B1_B7_cone01_union_region_low_cnot_search_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_union_region_two_cnot_orientation_census_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_union_region_two_cnot_orientation_census_gate.md"

METHOD = "b1_b7_cone01_union_region_two_cnot_orientation_census_gate_v0"
STATUS = "cone01_union_region_two_cnot_orientation_census_candidate_only"
MODEL_STATUS = "two_cnot_union_candidate_confirmed_without_replay_or_b7_credit"
DEFAULT_SEED_COUNT = 18
DEFAULT_MAX_NFEV = 3000
ORIENTATION_SEQUENCES = [
    [(0, 1), (0, 1)],
    [(0, 1), (1, 0)],
    [(1, 0), (0, 1)],
    [(1, 0), (1, 0)],
]


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


def previous_two_cnot_warm_start(row: dict[str, Any]) -> list[float] | None:
    for scaffold in row.get("scaffold_results", []):
        if int(scaffold.get("cnot_count", -1)) == 2 and scaffold.get("exact_pass") is True:
            return scaffold["best"]["wrapped_parameters"]
    return None


def mixed_scaffold_unitary(params: np.ndarray, sequence: list[tuple[int, int]]) -> np.ndarray:
    total = np.eye(4, dtype=complex)
    offset = 0
    for layer_index in range(len(sequence) + 1):
        total = pair_layer(params[offset : offset + 6]) @ total
        offset += 6
        if layer_index < len(sequence):
            control, target = sequence[layer_index]
            total = cx_on(control, target) @ total
    return total


def sequence_seed_points(
    packet: dict[str, Any],
    sequence: list[tuple[int, int]],
    seed_count: int,
    warm_start: list[float] | None,
) -> list[np.ndarray]:
    dimension = 6 * (len(sequence) + 1)
    points: list[np.ndarray] = []
    if warm_start is not None and len(warm_start) == dimension:
        points.append(np.array(warm_start, dtype=float))
    points.append(np.zeros(dimension, dtype=float))
    signature = sum((index + 1) * (3 * control + 7 * target) for index, (control, target) in enumerate(sequence))
    rng_seed = 25004 + int(packet["candidate_line_number"]) * 19 + signature
    rng = np.random.default_rng(rng_seed)
    for scale in [0.1, 0.35, 1.0, math.pi]:
        points.append(rng.normal(0.0, scale, size=dimension))
        points.append(rng.uniform(-scale, scale, size=dimension))
    while len(points) < seed_count:
        points.append(rng.uniform(-2.0 * math.pi, 2.0 * math.pi, size=dimension))
    return points[:seed_count]


def optimize_sequence(
    packet: dict[str, Any],
    sequence: list[tuple[int, int]],
    target: np.ndarray,
    seed_count: int,
    max_nfev: int,
    warm_start: list[float] | None,
) -> dict[str, Any]:
    def objective(values: np.ndarray) -> np.ndarray:
        return residual_vector(mixed_scaffold_unitary(values, sequence), target)

    best: dict[str, Any] | None = None
    attempts = []
    seeds = sequence_seed_points(packet, sequence, seed_count, warm_start)
    for seed_index, seed in enumerate(seeds):
        result = least_squares(
            objective,
            seed,
            method="trf",
            max_nfev=max_nfev,
            ftol=1e-12,
            xtol=1e-12,
            gtol=1e-12,
        )
        residual = float(np.linalg.norm(result.fun))
        candidate = mixed_scaffold_unitary(result.x, sequence)
        max_error = float(np.max(np.abs(phase_align(candidate, target) - target)))
        attempt = {
            "seed_index": seed_index,
            "warm_start_seed": bool(warm_start is not None and seed_index == 0),
            "residual_norm": residual,
            "max_abs_entry_error": max_error,
            "optimizer_success": bool(result.success),
            "optimizer_nfev": int(result.nfev),
        }
        attempts.append(attempt)
        if best is None or residual < best["residual_norm"]:
            wrapped = wrap_angles(result.x)
            best = {
                **attempt,
                "wrapped_parameters": wrapped,
                "parameter_stats": parameter_stats(wrapped),
            }
    assert best is not None
    return {
        "cnot_count": len(sequence),
        "cnot_sequence": [[control, target] for control, target in sequence],
        "local_u3_layer_count": len(sequence) + 1,
        "parameter_count": 6 * (len(sequence) + 1),
        "seed_count": len(seeds),
        "best": best,
        "attempts": attempts,
        "exact_pass": best["residual_norm"] <= EXACT_TOLERANCE,
    }


def run_probe(seed_count: int, max_nfev: int) -> dict[str, Any]:
    semantic = load_json(SEMANTIC_PACKET_PATH)
    synthesis = load_json(SYNTHESIS_PATH)
    low_cnot = load_json(LOW_CNOT_PATH)
    packet = line_packet(semantic, 1381)
    existing = synthesis_row(synthesis, 1381)
    warm_start = previous_two_cnot_warm_start(existing)
    target = target_matrix(packet)
    rows = []
    for sequence_index, sequence in enumerate(ORIENTATION_SEQUENCES):
        row = optimize_sequence(
            packet,
            sequence,
            target,
            seed_count,
            max_nfev,
            warm_start if sequence == [(0, 1), (0, 1)] else None,
        )
        row["sequence_index"] = sequence_index
        row["sequence_id"] = "-".join(f"{control}{target}" for control, target in sequence)
        rows.append(row)

    exact_rows = [row for row in rows if row["exact_pass"]]
    best_row = min(rows, key=lambda row: row["best"]["residual_norm"])
    best_exact_row = (
        min(
            exact_rows,
            key=lambda row: (
                row["best"]["parameter_stats"]["off_pi_over_four_grid_parameter_count"],
                row["best"]["residual_norm"],
            ),
        )
        if exact_rows
        else None
    )
    source_cnot_count = int(packet["cx_count"])
    accepted_removed = 0
    current_replacement_cnot = int(
        low_cnot["summary"]["current_min_exact_replacement_cnot_count"]
    )
    summary = {
        "source_semantic_packet_method": semantic.get("method"),
        "source_packet_synthesis_method": synthesis.get("method"),
        "source_low_cnot_method": low_cnot.get("method"),
        "target_line_number": 1381,
        "union_window": [int(packet["window_start_line"]), int(packet["window_end_line"])],
        "support_qubits": packet.get("support_qubits"),
        "source_cnot_count": source_cnot_count,
        "current_min_exact_replacement_cnot_count": current_replacement_cnot,
        "current_candidate_cnot_delta": source_cnot_count - current_replacement_cnot,
        "searched_cnot_count": 2,
        "searched_orientation_sequence_count": len(rows),
        "search_seed_count_per_sequence": seed_count,
        "search_max_nfev": max_nfev,
        "two_cnot_exact_sequence_count": len(exact_rows),
        "two_cnot_exact_sequence_ids": [row["sequence_id"] for row in exact_rows],
        "best_sequence_id": best_row["sequence_id"],
        "best_residual_norm": best_row["best"]["residual_norm"],
        "best_max_abs_entry_error": best_row["best"]["max_abs_entry_error"],
        "best_exact_sequence_id": best_exact_row["sequence_id"] if best_exact_row else None,
        "best_exact_residual_norm": best_exact_row["best"]["residual_norm"] if best_exact_row else None,
        "best_exact_max_abs_entry_error": (
            best_exact_row["best"]["max_abs_entry_error"] if best_exact_row else None
        ),
        "best_exact_off_pi_over_four_parameter_count": (
            best_exact_row["best"]["parameter_stats"]["off_pi_over_four_grid_parameter_count"]
            if best_exact_row
            else None
        ),
        "best_exact_nonzero_parameter_count": (
            best_exact_row["best"]["parameter_stats"]["nonzero_parameter_count"]
            if best_exact_row
            else None
        ),
        "best_exact_parameter_count": best_exact_row["parameter_count"] if best_exact_row else None,
        "two_cnot_union_candidate_confirmed": bool(exact_rows),
        "extra_delta_found_beyond_current_line1381_replacement": 0,
        "lower_than_two_cnot_rewrite_found": False,
        "two_cnot_union_replay_certificate_count": 0,
        "two_cnot_union_qasm_patch_count": 0,
        "local_u3_pricing_completed": False,
        "global_minimality_claimed": False,
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
        "source_low_cnot_result": display_path(LOW_CNOT_PATH),
        "summary": summary,
        "union_region_two_cnot_orientation_rows": rows,
        "claim_boundary": {
            "supported_claim": (
                "A scoped all-sequence 2-CNOT local-U3 census confirms whether "
                "the line-1378/1381 union target remains numerically reachable "
                "at the current 2-CNOT replacement count."
            ),
            "unsupported_claims": [
                "This is not a full-circuit replay certificate.",
                "This is not a QASM patch.",
                "This does not price local U3 layers into a B7 fault-tolerant ledger.",
                "This does not prove global CNOT minimality.",
                "This does not improve the B7 ledger.",
            ],
            "two_cnot_union_replay_certificate_count": 0,
            "local_u3_pricing_completed": False,
            "global_minimality_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }
    return payload


def markdown_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 Union-Region Two-CNOT Orientation Census Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- Source semantic packet: `{payload['source_semantic_packet_result']}`",
        f"- Source packet synthesis: `{payload['source_packet_synthesis_result']}`",
        f"- Source low-CNOT gate: `{payload['source_low_cnot_result']}`",
        "",
        "## Result",
        "",
        f"- Union window: `{summary['union_window']}`",
        f"- Support qubits: `{summary['support_qubits']}`",
        f"- Source CNOT / current replacement CNOT / current delta: `{summary['source_cnot_count']}` / `{summary['current_min_exact_replacement_cnot_count']}` / `{summary['current_candidate_cnot_delta']}`",
        f"- Searched 2-CNOT orientation sequences: `{summary['searched_orientation_sequence_count']}`",
        f"- Seeds / max evaluations per sequence: `{summary['search_seed_count_per_sequence']}` / `{summary['search_max_nfev']}`",
        f"- Exact 2-CNOT sequence count: `{summary['two_cnot_exact_sequence_count']}`",
        f"- Exact 2-CNOT sequence ids: `{summary['two_cnot_exact_sequence_ids']}`",
        f"- Best sequence / residual / entry error: `{summary['best_sequence_id']}` / `{summary['best_residual_norm']}` / `{summary['best_max_abs_entry_error']}`",
        f"- Best exact sequence / residual / entry error: `{summary['best_exact_sequence_id']}` / `{summary['best_exact_residual_norm']}` / `{summary['best_exact_max_abs_entry_error']}`",
        f"- Best exact off-grid / nonzero / total U3 parameters: `{summary['best_exact_off_pi_over_four_parameter_count']}` / `{summary['best_exact_nonzero_parameter_count']}` / `{summary['best_exact_parameter_count']}`",
        f"- Extra delta beyond current replacement: `{summary['extra_delta_found_beyond_current_line1381_replacement']}`",
        f"- Replay certificates / QASM patches / B7 claim: `{summary['two_cnot_union_replay_certificate_count']}` / `{summary['two_cnot_union_qasm_patch_count']}` / `{summary['b7_ledger_improvement_claimed']}`",
        "",
        "## Claim Boundary",
        "",
        "- This is a numerical 2-CNOT orientation census for the union-region target.",
        "- It keeps the branch at candidate-only status until full-circuit replay, QASM patching, and local-U3 fault-tolerant pricing are completed.",
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
