#!/usr/bin/env python3
"""Restricted packet synthesis search gate for B1/B7 cone_01.

T-B1-004ae constructed exact 2-qubit replay targets for the blocked carrier
CNOT stacks. This gate is the first synthesis attempt over those packets: for
each target, search fixed-direction CNOT scaffolds with arbitrary local U3
layers and fewer CNOTs than the source packet.

Numerical scaffold matches are candidate synthesis evidence only. They are not
full-circuit replay certificates, not exact symbolic decompositions, and not B7
ledger reductions. Local U3 layers carry their own synthesis/accounting burden.
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


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "results" / "B1_B7_cone01_semantic_replay_packet_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_packet_synthesis_search_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_packet_synthesis_search_gate.md"

METHOD = "b1_b7_cone01_packet_synthesis_search_gate_v0"
STATUS = "cone01_packet_synthesis_search_candidate_not_replay_certificate"
MODEL_STATUS = "restricted_cnot_scaffold_search_finds_candidates_without_b7_ledger_acceptance"
EXACT_TOLERANCE = 1e-8
DEFAULT_SEED_COUNT = 10
DEFAULT_MAX_NFEV = 1800


def u3(theta: float, phi: float, lam: float) -> np.ndarray:
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)
    return np.array(
        [
            [c, -np.exp(1j * lam) * s],
            [np.exp(1j * phi) * s, np.exp(1j * (phi + lam)) * c],
        ],
        dtype=complex,
    )


def pair_layer(params: np.ndarray) -> np.ndarray:
    return np.kron(u3(*params[:3]), u3(*params[3:6]))


def cx_on(control: int, target: int) -> np.ndarray:
    unitary = np.zeros((4, 4), dtype=complex)
    for basis in range(4):
        bits = [(basis >> 1) & 1, basis & 1]
        out = bits[:]
        if bits[control]:
            out[target] ^= 1
        unitary[(out[0] << 1) | out[1], basis] = 1.0
    return unitary


def scaffold_unitary(params: np.ndarray, cnot_count: int, control: int, target: int) -> np.ndarray:
    total = np.eye(4, dtype=complex)
    cnot = cx_on(control, target)
    offset = 0
    for layer_index in range(cnot_count + 1):
        total = pair_layer(params[offset : offset + 6]) @ total
        offset += 6
        if layer_index < cnot_count:
            total = cnot @ total
    return total


def target_matrix(packet: dict[str, Any]) -> np.ndarray:
    rounded = packet["semantic_matrix"]["global_phase_normalized_matrix_rounded"]
    return np.array([[complex(real, imag) for real, imag in row] for row in rounded], dtype=complex)


def phase_align(candidate: np.ndarray, target: np.ndarray) -> np.ndarray:
    overlap = np.trace(np.conjugate(target.T) @ candidate)
    if abs(overlap) <= 1e-15:
        return candidate
    return candidate * np.exp(-1j * np.angle(overlap))


def residual_vector(candidate: np.ndarray, target: np.ndarray) -> np.ndarray:
    diff = phase_align(candidate, target) - target
    return np.concatenate([diff.real.ravel(), diff.imag.ravel()])


def residual_norm(candidate: np.ndarray, target: np.ndarray) -> float:
    return float(np.linalg.norm(residual_vector(candidate, target)))


def first_cnot_orientation(packet: dict[str, Any]) -> tuple[int, int]:
    for op in packet["normalized_ops"]:
        if op["gate"] == "cx":
            return int(op["local_control"]), int(op["local_target"])
    raise ValueError(f"packet has no CNOT orientation: {packet['candidate_line_number']}")


def seed_points(packet: dict[str, Any], cnot_count: int, seed_count: int) -> list[np.ndarray]:
    dimension = 6 * (cnot_count + 1)
    points = [np.zeros(dimension, dtype=float)]
    rng_seed = 24004 + int(packet["candidate_line_number"]) * 17 + cnot_count
    rng = np.random.default_rng(rng_seed)
    for scale in [0.1, 0.35, 1.0, math.pi]:
        points.append(rng.normal(0.0, scale, size=dimension))
        points.append(rng.uniform(-scale, scale, size=dimension))
    while len(points) < seed_count:
        points.append(rng.uniform(-2.0 * math.pi, 2.0 * math.pi, size=dimension))
    return points[:seed_count]


def parameter_stats(values: list[float]) -> dict[str, Any]:
    nonzero = [value for value in values if abs(value) > 1e-7]
    off_grid = [
        value
        for value in values
        if abs(value - round(value / (math.pi / 4.0)) * (math.pi / 4.0)) > 1e-6
    ]
    return {
        "parameter_count": len(values),
        "nonzero_parameter_count": len(nonzero),
        "off_pi_over_four_grid_parameter_count": len(off_grid),
    }


def wrap_angles(values: np.ndarray) -> list[float]:
    return [float((value + math.pi) % (2.0 * math.pi) - math.pi) for value in values]


def optimize_scaffold(
    packet: dict[str, Any],
    cnot_count: int,
    target: np.ndarray,
    control: int,
    target_qubit: int,
    seed_count: int,
    max_nfev: int,
) -> dict[str, Any]:
    def objective(values: np.ndarray) -> np.ndarray:
        return residual_vector(scaffold_unitary(values, cnot_count, control, target_qubit), target)

    best: dict[str, Any] | None = None
    attempts = []
    for seed_index, seed in enumerate(seed_points(packet, cnot_count, seed_count)):
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
        candidate = scaffold_unitary(result.x, cnot_count, control, target_qubit)
        max_error = float(np.max(np.abs(phase_align(candidate, target) - target)))
        attempt = {
            "seed_index": seed_index,
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
        "cnot_count": cnot_count,
        "local_u3_layer_count": cnot_count + 1,
        "parameter_count": 6 * (cnot_count + 1),
        "seed_count": seed_count,
        "best": best,
        "attempts": attempts,
        "exact_pass": best["residual_norm"] <= EXACT_TOLERANCE,
    }


def analyze_packet(packet: dict[str, Any], seed_count: int, max_nfev: int) -> dict[str, Any]:
    matrix = target_matrix(packet)
    control, target = first_cnot_orientation(packet)
    original_cnot_count = int(packet["cx_count"])
    max_reduced_cnot_count = min(3, original_cnot_count - 1)
    scaffolds = [
        optimize_scaffold(packet, cnot_count, matrix, control, target, seed_count, max_nfev)
        for cnot_count in range(max_reduced_cnot_count + 1)
    ]
    exact_scaffolds = [row for row in scaffolds if row["exact_pass"]]
    best_scaffold = min(scaffolds, key=lambda row: row["best"]["residual_norm"])
    best_exact = min(exact_scaffolds, key=lambda row: row["cnot_count"]) if exact_scaffolds else None
    cnot_reduction = original_cnot_count - best_exact["cnot_count"] if best_exact else 0
    return {
        "pattern_id": packet["pattern_id"],
        "candidate_line_number": int(packet["candidate_line_number"]),
        "window_start_line": int(packet["window_start_line"]),
        "window_end_line": int(packet["window_end_line"]),
        "support_qubits": packet["support_qubits"],
        "source_cnot_count": original_cnot_count,
        "source_single_qubit_gate_count": int(packet["single_qubit_gate_count"]),
        "searched_max_reduced_cnot_count": max_reduced_cnot_count,
        "fixed_cnot_orientation": {"local_control": control, "local_target": target},
        "scaffold_results": scaffolds,
        "best_scaffold_cnot_count": int(best_scaffold["cnot_count"]),
        "best_scaffold_residual_norm": best_scaffold["best"]["residual_norm"],
        "best_scaffold_max_abs_entry_error": best_scaffold["best"]["max_abs_entry_error"],
        "exact_reduced_scaffold_found": bool(best_exact),
        "best_exact_reduced_cnot_count": int(best_exact["cnot_count"]) if best_exact else None,
        "best_exact_cnot_reduction": cnot_reduction,
        "best_exact_local_u3_layer_count": int(best_exact["local_u3_layer_count"]) if best_exact else None,
        "best_exact_parameter_count": int(best_exact["parameter_count"]) if best_exact else None,
        "accepted_replay_certificate": False,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "claim_boundary": (
            "A numerical reduced-CNOT scaffold is only a candidate local synthesis witness. "
            "It is not accepted as a replay certificate, exact symbolic decomposition, or B7 ledger saving."
        ),
    }


def build_payload(seed_count: int, max_nfev: int) -> dict[str, Any]:
    source = load_json(SOURCE_PATH)
    rows = [
        analyze_packet(packet, seed_count, max_nfev)
        for packet in source.get("semantic_replay_packets", [])
    ]
    exact_rows = [row for row in rows if row["exact_reduced_scaffold_found"]]
    accepted_removed = sum(row["accepted_occurrence_removal"] for row in rows)
    summary = {
        "source_method": source.get("method"),
        "source_status": source.get("status"),
        "packet_count": len(rows),
        "fixed_direction_scaffold_packet_count": len(rows),
        "searched_scaffold_count": sum(len(row["scaffold_results"]) for row in rows),
        "optimizer_seed_count_per_scaffold": seed_count,
        "optimizer_max_nfev": max_nfev,
        "exact_reduced_scaffold_packet_count": len(exact_rows),
        "min_exact_reduced_cnot_count": min(
            (row["best_exact_reduced_cnot_count"] for row in exact_rows),
            default=None,
        ),
        "total_candidate_cnot_reduction_if_accepted": sum(
            row["best_exact_cnot_reduction"] for row in exact_rows
        ),
        "accepted_replay_certificate_count": sum(1 for row in rows if row["accepted_replay_certificate"]),
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": accepted_removed * PROXY_T_PER_OCCURRENCE,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed)
        * PROXY_T_PER_OCCURRENCE,
        "candidate_synthesis_found": len(exact_rows) > 0,
        "candidate_synthesis_claimed_as_resource_saving": False,
        "semantic_replay_certificate_claimed": False,
        "shorter_rewrite_claimed": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": None,
    }
    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 packet synthesis search gate",
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_result": display_path(SOURCE_PATH),
        "source_method": source.get("method"),
        "workload": source.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "summary": summary,
        "packet_synthesis_rows": rows,
        "claim_boundary": {
            "candidate_synthesis_found": len(exact_rows) > 0,
            "candidate_synthesis_claimed_as_resource_saving": False,
            "semantic_replay_certificate_claimed": False,
            "shorter_rewrite_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "Restricted fixed-direction CNOT scaffolds were numerically searched against the "
                "three T-B1-004ae packet unitary targets."
            ),
            "unsupported_claims": [
                "No candidate is accepted as a full-circuit replay certificate.",
                "No symbolic exact decomposition is produced.",
                "No occurrence is removed from the B7 ledger.",
            ],
        },
    }
    errors = validate(payload)
    payload["summary"]["validation_error_count"] = len(errors)
    payload["validation_errors"] = errors
    return payload


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = payload["summary"]
    if payload.get("method") != METHOD:
        errors.append("method_mismatch")
    if payload.get("status") != STATUS:
        errors.append("status_mismatch")
    if payload.get("source_method") != "b1_b7_cone01_semantic_replay_packet_gate_v0":
        errors.append("source_method_mismatch")
    if summary.get("packet_count") != 3:
        errors.append("packet_count_mismatch")
    if summary.get("fixed_direction_scaffold_packet_count") != 3:
        errors.append("fixed_direction_scaffold_packet_count_mismatch")
    if summary.get("searched_scaffold_count") != 12:
        errors.append("searched_scaffold_count_mismatch")
    for field in [
        "accepted_replay_certificate_count",
        "accepted_occurrence_removal",
        "accepted_proxy_t_reduction",
    ]:
        if summary.get(field) != 0:
            errors.append(f"{field}_must_be_zero")
    if summary.get("missing_occurrences_after_gate") != 30:
        errors.append("missing_occurrences_after_gate_mismatch")
    if summary.get("missing_proxy_t_after_gate") != 600:
        errors.append("missing_proxy_t_after_gate_mismatch")
    for field in [
        "candidate_synthesis_claimed_as_resource_saving",
        "semantic_replay_certificate_claimed",
        "shorter_rewrite_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(field) is not False or payload["claim_boundary"].get(field) is not False:
            errors.append(f"{field}_must_remain_false")
    for row in payload.get("packet_synthesis_rows", []):
        if row.get("accepted_replay_certificate") is not False:
            errors.append(f"{row.get('candidate_line_number')}_accepted_replay_certificate_must_be_false")
        if row.get("accepted_occurrence_removal") != 0:
            errors.append(f"{row.get('candidate_line_number')}_accepted_removal_must_be_zero")
        if len(row.get("scaffold_results", [])) != 4:
            errors.append(f"{row.get('candidate_line_number')}_scaffold_count_must_be_4")
        if row.get("best_scaffold_residual_norm") is None:
            errors.append(f"{row.get('candidate_line_number')}_missing_best_residual")
    return errors


def markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone_01 Packet Synthesis Search Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004ae and searches fixed-direction reduced-CNOT scaffolds with arbitrary local U3 layers against the three exact packet unitary targets.",
        "",
        "## Summary",
        "",
        f"- Packets searched: `{summary['packet_count']}`",
        f"- Scaffolds searched: `{summary['searched_scaffold_count']}`",
        f"- Optimizer seeds per scaffold: `{summary['optimizer_seed_count_per_scaffold']}`",
        f"- Exact reduced-CNOT scaffold packets: `{summary['exact_reduced_scaffold_packet_count']}`",
        f"- Minimum exact reduced CNOT count: `{summary['min_exact_reduced_cnot_count']}`",
        f"- Candidate CNOT reduction if accepted: `{summary['total_candidate_cnot_reduction_if_accepted']}`",
        f"- Accepted replay certificates: `{summary['accepted_replay_certificate_count']}`",
        f"- Accepted occurrence/proxy-T reduction: `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Packet Rows",
        "",
        "| Candidate line | Source CX | Best residual | Exact reduced scaffold | Best exact CX | Candidate CX reduction | Accepted replay |",
        "|---:|---:|---:|---|---:|---:|---|",
    ]
    for row in payload["packet_synthesis_rows"]:
        best_exact = row["best_exact_reduced_cnot_count"]
        lines.append(
            "| "
            f"{row['candidate_line_number']} | "
            f"{row['source_cnot_count']} | "
            f"{row['best_scaffold_residual_norm']:.3e} | "
            f"{row['exact_reduced_scaffold_found']} | "
            f"{best_exact if best_exact is not None else 'None'} | "
            f"{row['best_exact_cnot_reduction']} | "
            f"{row['accepted_replay_certificate']} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "A reduced-CNOT numerical scaffold is not yet an accepted rewrite. The current gate does not emit a symbolic exact decomposition, does not replay a candidate inside the full `gcm_h6` circuit, does not price the new local U3 layers, and does not change the B7 ledger.",
            "",
            "## Next Required Gate",
            "",
            "The next gate must convert any numerical reduced-CNOT candidate into a replayable full-circuit certificate with explicit local-layer resource accounting, or prove that the searched scaffold cannot support an accepted occurrence-removing rewrite.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-count", type=int, default=DEFAULT_SEED_COUNT)
    parser.add_argument("--max-nfev", type=int, default=DEFAULT_MAX_NFEV)
    parser.add_argument("--json-out", type=Path, default=JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.seed_count, args.max_nfev)
    write_json(args.json_out, payload, args.pretty)
    write_text(args.md_out, markdown(payload))
    if args.pretty:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    if payload["validation_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
