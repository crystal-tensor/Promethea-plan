#!/usr/bin/env python3
"""Single-carrier local-dressing gate for B1/B7 cone_01 flat packets.

T-B1-004r showed that arbitrary SU(2)xSU(2) local dressing can numerically
match the three residual flat-pattern packets. T-B1-004s and T-B1-004t closed
direct pi/4 projection, shared grid signatures, and plain local Clifford
dressing. This gate checks one more cheap certificate route: can a single
non-Clifford local carrier rotation, wrapped by pair-local Cliffords, exactify
each packet?

The carrier angle is not optimized. It is selected from small multiples of the
source theta or theta-to-nearest-grid delta. A pass still needs replay and
ledger review because it can replace one arbitrary local angle with another
arbitrary local carrier rather than remove an occurrence.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from b1_b7_cone01_flat_pattern_kak_packet import parse_normalized_op, replace_target_ry_with_grid
from b1_b7_cone01_local_clifford_dressing_gate import one_qubit_cliffords, pair_local_cliffords
from b1_b7_cone01_phase_removal_gate import EXACT_TOLERANCE, rx, ry, rz, single_on, unitary_for_ops


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKET_PATH = ROOT / "results" / "B1_B7_cone01_flat_pattern_kak_packet_v0.json"
SOURCE_CLIFFORD_PATH = ROOT / "results" / "B1_B7_cone01_local_clifford_dressing_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_single_carrier_dressing_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_single_carrier_dressing_gate.md"

METHOD = "b1_b7_cone01_single_carrier_dressing_gate_v0"
STATUS = "cone01_single_carrier_exact_packet_not_resource_certificate"
MODEL_STATUS = "single_nonclifford_carrier_exactifies_flat_packets_without_resource_saving"
PROXY_T_PER_OCCURRENCE = 20
REQUIRED_OCCURRENCE_REMOVALS = 30
CARRIER_COEFFICIENTS = (-2.0, -1.0, -0.5, 0.5, 1.0, 2.0)
CARRIER_SOURCES = ("theta", "theta_delta")
AXES = ("x", "y", "z")
LOCAL_INDICES = (0, 1)
SIDES = ("left", "right")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def wrap_angle(value: float) -> float:
    return (float(value) + math.pi) % (2.0 * math.pi) - math.pi


def carrier_matrix(axis: str, local_index: int, angle: float) -> np.ndarray:
    if axis == "x":
        base = rx(angle)
    elif axis == "y":
        base = ry(angle)
    elif axis == "z":
        base = rz(angle)
    else:
        raise ValueError(axis)
    return single_on(local_index, base)


def batch_residual_norms(candidates: np.ndarray, target: np.ndarray) -> np.ndarray:
    flat = candidates.reshape((-1, 4, 4))
    overlaps = np.einsum("ij,nij->n", np.conjugate(target), flat)
    phases = np.ones_like(overlaps, dtype=complex)
    nonzero = np.abs(overlaps) > 1e-15
    phases[nonzero] = np.exp(-1j * np.angle(overlaps[nonzero]))
    aligned = flat * phases[:, None, None]
    diff = aligned - target
    return np.linalg.norm(diff.reshape((flat.shape[0], -1)), axis=1)


def reconstruct_pattern(packet: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    ops = [parse_normalized_op(text) for text in packet["normalized_window_text"]]
    target = unitary_for_ops(ops, [0, 1])
    grid_ops = replace_target_ry_with_grid(ops, float(packet["nearest_grid_angle"]))
    return target, unitary_for_ops(grid_ops, [0, 1])


def carrier_variants(packet: dict[str, Any]) -> list[dict[str, Any]]:
    theta = float(packet["theta"])
    delta = wrap_angle(theta - float(packet["nearest_grid_angle"]))
    source_values = {"theta": theta, "theta_delta": delta}
    rows = []
    seen = set()
    for source in CARRIER_SOURCES:
        for coefficient in CARRIER_COEFFICIENTS:
            angle = wrap_angle(coefficient * source_values[source])
            key_angle = round(angle, 12)
            if abs(angle) <= 1e-12:
                continue
            for axis in AXES:
                for local_index in LOCAL_INDICES:
                    key = (source, coefficient, key_angle, axis, local_index)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(
                        {
                            "carrier_source": source,
                            "carrier_coefficient": coefficient,
                            "carrier_angle": angle,
                            "axis": axis,
                            "local_index": local_index,
                            "local_role": "partner" if local_index == 0 else "target",
                        }
                    )
    return rows


def evaluate_variant(
    target: np.ndarray,
    grid_unitary: np.ndarray,
    pair_mats: np.ndarray,
    pair_labels: list[str],
    variant: dict[str, Any],
    side: str,
    chunk_size: int,
) -> tuple[int, dict[str, Any]]:
    carrier = carrier_matrix(variant["axis"], int(variant["local_index"]), float(variant["carrier_angle"]))
    exact_count = 0
    best: dict[str, Any] | None = None
    if side == "left":
        left_mats = np.einsum("aij,jk,kl->ail", pair_mats, carrier, grid_unitary)
    else:
        left_mats = np.einsum("aij,jk,kl->ail", pair_mats, grid_unitary, carrier)

    for start in range(0, len(pair_mats), chunk_size):
        left_chunk = left_mats[start : start + chunk_size]
        candidates = np.einsum("aij,bjk->abik", left_chunk, pair_mats)
        residuals = batch_residual_norms(candidates, target).reshape((left_chunk.shape[0], len(pair_mats)))
        exact_count += int(np.count_nonzero(residuals <= EXACT_TOLERANCE))
        flat_index = int(np.argmin(residuals))
        local_best = float(residuals.ravel()[flat_index])
        if best is None or local_best < best["residual_norm"]:
            left_offset, right_index = np.unravel_index(flat_index, residuals.shape)
            left_index = start + int(left_offset)
            best = {
                **variant,
                "side": side,
                "left_pair_label": pair_labels[left_index],
                "right_pair_label": pair_labels[int(right_index)],
                "residual_norm": local_best,
            }
    assert best is not None
    return exact_count, best


def analyze_packet(packet: dict[str, Any], pair_rows: list[dict[str, Any]], chunk_size: int) -> dict[str, Any]:
    target, grid_unitary = reconstruct_pattern(packet)
    pair_mats = np.stack([row["matrix"] for row in pair_rows])
    pair_labels = [row["label"] for row in pair_rows]
    variants = carrier_variants(packet)
    total_exact = 0
    best: dict[str, Any] | None = None
    for variant in variants:
        for side in SIDES:
            exact_count, candidate_best = evaluate_variant(
                target, grid_unitary, pair_mats, pair_labels, variant, side, chunk_size
            )
            total_exact += exact_count
            if best is None or candidate_best["residual_norm"] < best["residual_norm"]:
                best = candidate_best
    assert best is not None
    trial_count = len(variants) * len(SIDES) * len(pair_rows) * len(pair_rows)
    return {
        "pattern_id": packet["pattern_id"],
        "occurrence_count": packet["occurrence_count"],
        "theta": float(packet["theta"]),
        "theta_delta": wrap_angle(float(packet["theta"]) - float(packet["nearest_grid_angle"])),
        "nearest_grid_label": packet["nearest_grid_label"],
        "carrier_variant_count": len(variants),
        "left_right_pair_trial_count": trial_count,
        "single_carrier_exact_pass_count": total_exact,
        "single_carrier_exact_pass": total_exact > 0,
        "best_single_carrier_residual_norm": best["residual_norm"],
        "best_single_carrier_candidate": best,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
    }


def build_payload(chunk_size: int) -> dict[str, Any]:
    packet_payload = load_json(SOURCE_PACKET_PATH)
    clifford_payload = load_json(SOURCE_CLIFFORD_PATH)
    single_rows = one_qubit_cliffords()
    pair_rows = pair_local_cliffords(single_rows)
    pattern_rows = [analyze_packet(packet, pair_rows, chunk_size) for packet in packet_payload["pattern_packets"]]
    exact_packet_count = sum(1 for row in pattern_rows if row["single_carrier_exact_pass"])
    accepted_occurrence_removal = sum(row["accepted_occurrence_removal"] for row in pattern_rows)
    missing_occurrences = REQUIRED_OCCURRENCE_REMOVALS - accepted_occurrence_removal
    total_trial_count = sum(row["left_right_pair_trial_count"] for row in pattern_rows)
    summary = {
        "source_method": packet_payload.get("method"),
        "source_status": packet_payload.get("status"),
        "source_clifford_method": clifford_payload.get("method"),
        "source_clifford_status": clifford_payload.get("status"),
        "single_qubit_clifford_count": len(single_rows),
        "pair_local_clifford_count": len(pair_rows),
        "carrier_source_count": len(CARRIER_SOURCES),
        "carrier_coefficient_count": len(CARRIER_COEFFICIENTS),
        "carrier_axis_count": len(AXES),
        "carrier_local_role_count": len(LOCAL_INDICES),
        "side_count": len(SIDES),
        "pattern_group_count": len(pattern_rows),
        "covered_invariant_flat_occurrence_count": sum(int(row["occurrence_count"]) for row in pattern_rows),
        "total_single_carrier_trial_count": total_trial_count,
        "single_carrier_exact_packet_count": exact_packet_count,
        "all_packets_have_single_carrier_certificate": exact_packet_count == len(pattern_rows),
        "best_single_carrier_residual_norm": min(
            (row["best_single_carrier_residual_norm"] for row in pattern_rows), default=None
        ),
        "max_best_single_carrier_residual_norm": max(
            (row["best_single_carrier_residual_norm"] for row in pattern_rows), default=None
        ),
        "accepted_occurrence_removal": accepted_occurrence_removal,
        "accepted_proxy_t_reduction": 0,
        "required_occurrence_removals_for_b7_target": REQUIRED_OCCURRENCE_REMOVALS,
        "missing_occurrences_after_gate": missing_occurrences,
        "missing_proxy_t_after_gate": missing_occurrences * PROXY_T_PER_OCCURRENCE,
        "single_carrier_exact_packet_found": exact_packet_count > 0,
        "single_carrier_resource_certificate_claimed": False,
        "rewrite_claimed": False,
        "semantic_certificate_claimed": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": None,
    }
    payload = {
        "benchmark_id": "B1",
        "problem_id": 25,
        "linked_b7_problem_id": 21,
        "title": "B1/B7 cone_01 single-carrier local dressing gate",
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "method": METHOD,
        "source_result": display_path(SOURCE_PACKET_PATH),
        "source_method": packet_payload.get("method"),
        "source_clifford_result": display_path(SOURCE_CLIFFORD_PATH),
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "summary": summary,
        "pattern_single_carrier_results": pattern_rows,
        "claim_boundary": {
            "single_carrier_exact_packet_found": exact_packet_count > 0,
            "single_carrier_resource_certificate_claimed": False,
            "rewrite_claimed": False,
            "semantic_certificate_claimed": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "supported_claim": (
                "A finite search over one theta/delta-derived local carrier rotation wrapped by "
                "pair-local Cliffords exactifies the three flat packets, but the carrier remains "
                "an arbitrary local rotation and is not accepted as B7 resource reduction."
            ),
            "unsupported_claims": [
                "This is not an occurrence-removing rewrite certificate.",
                "This does not reduce the current occurrence ledger because one arbitrary local carrier remains.",
                "This does not rule out a broader two-qubit rewrite with changed envelope.",
                "This is not a B7 resource saving.",
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
    if payload.get("source_method") != "b1_b7_cone01_flat_pattern_kak_packet_v0":
        errors.append("source_method_mismatch")
    if summary.get("source_clifford_method") != "b1_b7_cone01_local_clifford_dressing_gate_v0":
        errors.append("source_clifford_method_mismatch")
    if summary.get("single_qubit_clifford_count") != 24:
        errors.append("single_qubit_clifford_count_mismatch")
    if summary.get("pair_local_clifford_count") != 576:
        errors.append("pair_local_clifford_count_mismatch")
    if summary.get("pattern_group_count") != 3:
        errors.append("pattern_group_count_mismatch")
    if summary.get("covered_invariant_flat_occurrence_count") != 11:
        errors.append("covered_occurrence_count_mismatch")
    if summary.get("single_carrier_exact_packet_count") != 3:
        errors.append("single_carrier_exact_packet_count_mismatch")
    if summary.get("all_packets_have_single_carrier_certificate") is not True:
        errors.append("all_packets_single_carrier_flag_should_be_true")
    if summary.get("accepted_occurrence_removal") != 0:
        errors.append("accepted_occurrence_removal_should_be_zero")
    if summary.get("accepted_proxy_t_reduction") != 0:
        errors.append("accepted_proxy_t_reduction_should_be_zero")
    for key in [
        "single_carrier_resource_certificate_claimed",
        "rewrite_claimed",
        "semantic_certificate_claimed",
        "resource_saving_claimed",
        "b7_ledger_improvement_claimed",
    ]:
        if summary.get(key) is not False:
            errors.append(f"{key}_should_be_false")
    for row in payload.get("pattern_single_carrier_results", []):
        if not row.get("single_carrier_exact_pass"):
            errors.append(f"{row['pattern_id']}_missing_exact_pass")
        if row.get("accepted_occurrence_removal") != 0:
            errors.append(f"{row['pattern_id']}_accepted_occurrence_should_be_zero")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 Cone 01 Single-Carrier Local Dressing Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact performs a finite route check: one theta- or delta-derived local carrier "
        "rotation is wrapped by pair-local Cliffords and tested against each residual flat packet. "
        "All three packets exactify, but this is still not an occurrence-removing rewrite or "
        "resource-saving claim because one arbitrary local carrier remains.",
        "",
        "## Summary",
        "",
        f"- Carrier sources: `{', '.join(CARRIER_SOURCES)}`",
        f"- Carrier coefficients: `{', '.join(str(value) for value in CARRIER_COEFFICIENTS)}`",
        f"- Pair-local Clifford representatives: `{summary['pair_local_clifford_count']}`",
        f"- Pattern groups: `{summary['pattern_group_count']}`",
        f"- Total single-carrier trials: `{summary['total_single_carrier_trial_count']}`",
        f"- Single-carrier exact packets: `{summary['single_carrier_exact_packet_count']}`",
        f"- Best/max best single-carrier residual: `{summary['best_single_carrier_residual_norm']}` / `{summary['max_best_single_carrier_residual_norm']}`",
        f"- Accepted occurrence removal: `{summary['accepted_occurrence_removal']}`",
        f"- Missing occurrences after this gate: `{summary['missing_occurrences_after_gate']}`",
        "",
        "## Pattern Results",
        "",
        "| Pattern | Occurrences | Carrier variants | Trials | Best residual | Exact passes | Best carrier | Best side | Best left | Best right |",
        "|---|---:|---:|---:|---:|---:|---|---|---|---|",
    ]
    for row in payload["pattern_single_carrier_results"]:
        best = row["best_single_carrier_candidate"]
        carrier = (
            f"{best['carrier_coefficient']}*{best['carrier_source']} "
            f"{best['axis'].upper()}[{best['local_role']}]"
        )
        lines.append(
            "| {pattern} | {occ} | {variants} | {trials} | `{resid:.12g}` | {passes} | `{carrier}` | `{side}` | `{left}` | `{right}` |".format(
                pattern=row["pattern_id"],
                occ=row["occurrence_count"],
                variants=row["carrier_variant_count"],
                trials=row["left_right_pair_trial_count"],
                resid=row["best_single_carrier_residual_norm"],
                passes=row["single_carrier_exact_pass_count"],
                carrier=carrier,
                side=best["side"],
                left=best["left_pair_label"],
                right=best["right_pair_label"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- A single-carrier local-Clifford-wrapped exact packet was found for each of the three packets.",
            "- Accepted occurrence removal and accepted proxy-T reduction remain 0.",
            "- The carrier is still an arbitrary local rotation, so this does not clear the B7 occurrence ledger.",
            "- No semantic rewrite, resource saving, or B7 ledger improvement is claimed.",
            "",
            f"Validation error count: `{summary['validation_error_count']}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=JSON_OUT)
    parser.add_argument("--markdown-output", type=Path, default=MD_OUT)
    parser.add_argument("--chunk-size", type=int, default=32)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_payload(chunk_size=args.chunk_size)
    write_json(args.json_output, payload, pretty=args.pretty)
    write_text(args.markdown_output, render_markdown(payload))
    if args.pretty:
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
