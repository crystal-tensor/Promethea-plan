#!/usr/bin/env python3
"""Enumerate weighted T-tree controls and freeze the smallest R172 near tie."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import struct
from pathlib import Path
from typing import Any

from b4_b8_r154_deterministic_automatic_replay import canonical_hash, target_descriptor
from b4_b8_r165_candidate_selection_replay import new_config, normalize_events, parse_leaves
from qiskit import QuantumCircuit, qasm3
from qiskit._accelerate.vf2_layout import vf2_layout_pass_average_score_traced
from qiskit.converters import circuit_to_dag
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2


METHOD = "b4_b8_r172_second_near_tie_design_v0"
INPUT_PATH = "benchmarks/B4_B8_R172_second_near_tie_candidate_v0.qasm"
RESULT_PATH = "results/B4_B8_R172_second_near_tie_design_v0.json"
REPORT_PATH = "research/B4_B8_R172_second_near_tie_design.md"
INSTRUMENTED_BINARY_SHA256 = "56101c7bedbaa157c341542d18b95e60b9d37acb9f29d6305fa2f7337cb8fd69"
EDGES = ((0, 1), (0, 2), (0, 3), (1, 4))
R170_DEGREE_SEQUENCE = [2, 2, 2, 1, 1]
R172_DEGREE_SEQUENCE = [3, 2, 1, 1, 1]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bits_to_float(bits: int) -> float:
    return struct.unpack("!d", int(bits).to_bytes(8, "big"))[0]


def build_circuit(multiplicities: tuple[int, ...]) -> QuantumCircuit:
    circuit = QuantumCircuit(7, 5)
    for qubit, angle in enumerate((0.17, 0.29, 0.41, 0.53, 0.67)):
        circuit.rz(angle, qubit)
    for (left, right), count in zip(EDGES, multiplicities, strict=True):
        for _ in range(count):
            circuit.cx(left, right)
        for _ in range(count):
            circuit.cx(right, left)
    circuit.barrier(*range(5))
    circuit.measure(range(5), range(5))
    return circuit


def candidate_rows(circuit: QuantumCircuit, target: Any) -> list[dict[str, Any]]:
    _, raw_events, _ = vf2_layout_pass_average_score_traced(
        circuit_to_dag(circuit), target, new_config(), strict_direction=False, operation_order="ascending"
    )
    events = normalize_events(raw_events)
    rows = []
    for event in events:
        if event["kind"] != "candidate" or event["result_terms"].startswith("returned_by_minimize_vf2"):
            continue
        leaves = parse_leaves(event["result_terms"])
        rows.append({
            "candidate_index": len(rows),
            "mapping_terms": event["left_terms"],
            "source_score_bits": event["left_bits"],
            "source_score": bits_to_float(event["left_bits"]),
            "retained_leaf_count": len(leaves),
        })
    return sorted(rows, key=lambda row: row["source_score"])


def build(root: Path) -> tuple[dict[str, Any], str]:
    backend = FakeNairobiV2()
    target = backend.target
    scan_rows = []
    for multiplicities in itertools.product(range(1, 6), repeat=len(EDGES)):
        candidates = candidate_rows(build_circuit(multiplicities), target)
        if len(candidates) < 2:
            continue
        gap = candidates[1]["source_score"] - candidates[0]["source_score"]
        ulp = max(math.ulp(abs(candidates[0]["source_score"])), math.ulp(abs(candidates[1]["source_score"])))
        scan_rows.append({
            "multiplicities": list(multiplicities),
            "two_qubit_operation_count": 2 * sum(multiplicities),
            "candidate_count": len(candidates),
            "best_two_source_score_gap": gap,
            "best_two_source_score_gap_ulp_ratio": gap / ulp,
            "source_score_gap_is_one_ulp": gap == ulp,
        })
    one_ulp_rows = [row for row in scan_rows if row["source_score_gap_is_one_ulp"]]
    selected = min(one_ulp_rows, key=lambda row: (row["two_qubit_operation_count"], row["multiplicities"]))
    if selected["multiplicities"] != [2, 1, 1, 1]:
        raise ValueError("R172 selected multiplicity changed")

    input_path = root / INPUT_PATH
    input_circuit = qasm3.load(input_path)
    input_candidates = candidate_rows(input_circuit, target)
    gap = input_candidates[1]["source_score"] - input_candidates[0]["source_score"]
    ulp = max(math.ulp(abs(input_candidates[0]["source_score"])), math.ulp(abs(input_candidates[1]["source_score"])))
    selection_matches_input = len(input_candidates) == selected["candidate_count"] and gap == ulp
    summary = {
        "weighted_variants_scanned": 5 ** len(EDGES),
        "candidate_observable_variant_count": len(scan_rows),
        "one_ulp_variant_count": len(one_ulp_rows),
        "selected_multiplicities": selected["multiplicities"],
        "selected_two_qubit_operation_count": selected["two_qubit_operation_count"],
        "selected_candidate_count": len(input_candidates),
        "best_two_source_score_gap": gap,
        "best_two_source_score_gap_ulp_ratio": gap / ulp,
        "source_score_gap_is_one_ulp": gap == ulp,
        "selection_matches_input": selection_matches_input,
        "r170_degree_sequence": R170_DEGREE_SEQUENCE,
        "r172_degree_sequence": R172_DEGREE_SEQUENCE,
        "degree_sequence_proves_nonisomorphism": R170_DEGREE_SEQUENCE != R172_DEGREE_SEQUENCE,
        "qiskit_calls_performed": 5 ** len(EDGES) + 1,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "route_change_performed": False,
        "new_credit_delta": 0,
    }
    result = {
        "method": METHOD,
        "version": 0,
        "title": "B4/B8 R172 second near-tie graph design",
        "status": "second_near_tie_design_complete" if selection_matches_input else "second_near_tie_design_incomplete",
        "classification": "nonisomorphic_one_ulp_control_selected" if selection_matches_input else "design_incomplete",
        "source_target_id": "T-B4-002cp/T-B8-003ct/T-B10-009cf-r172-design",
        "input": INPUT_PATH,
        "input_sha256": file_sha256(input_path),
        "target": {"backend": "FakeNairobiV2", "descriptor_sha256": target_descriptor(backend)["descriptor_hash"]},
        "instrumented_binary_sha256": INSTRUMENTED_BINARY_SHA256,
        "graph": {"edges": [list(edge) for edge in EDGES], "edge_multiplicities": selected["multiplicities"], "degree_sequence": R172_DEGREE_SEQUENCE},
        "best_candidates": input_candidates[:3],
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": "an exhaustive bounded multiplicity scan selected a one-ULP weighted T-tree control whose degree sequence differs from R170",
            "what_is_not_supported": "a full replay, a universal arithmetic instability result, a numerical remedy, a confirmed Qiskit bug, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    result["payload_hash"] = canonical_hash(result)
    report = "\n".join([
        "# B4/B8 R172 Second Near-Tie Graph Design",
        "",
        f"- Status: `{result['status']}`",
        f"- Weighted variants scanned: `{summary['weighted_variants_scanned']}`",
        f"- Observable / one-ULP variants: `{summary['candidate_observable_variant_count']}` / `{summary['one_ulp_variant_count']}`",
        f"- Selected multiplicities: `{summary['selected_multiplicities']}`",
        f"- Best-two gap: `{summary['best_two_source_score_gap_ulp_ratio']} ULP`",
        "",
        "## Heuristic question",
        "",
        "Does the one-ULP selection split survive when the interaction graph changes from a path into a nonisomorphic T-tree?",
        "",
        "The degree sequences `(2,2,2,1,1)` and `(3,2,1,1,1)` prove that the R170 and R172 interaction graphs are not isomorphic. The bounded scan selects the lowest-two-qubit-cost one-ULP weighted variant under the declared search order.",
        "",
        "## Claim boundary",
        "",
        "This is a design scan and frozen control, not the full R172 replay. It performs no simulation or hardware execution and makes no compiler-bug, numerical-remedy, advantage, BQP, solved-frontier, or credit claim.",
        "",
    ])
    return result, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    result_path = root / RESULT_PATH
    report_path = root / REPORT_PATH
    if result_path.exists() or report_path.exists():
        raise ValueError("R172 design evidence already exists; refusing to overwrite")
    result, report = build(root)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": result["summary"], "payload_hash": result["payload_hash"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
