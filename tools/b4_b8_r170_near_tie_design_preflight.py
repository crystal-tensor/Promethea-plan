#!/usr/bin/env python3
"""Measure the frozen R170 input's candidate score gap before full replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from fractions import Fraction
from pathlib import Path
from typing import Any

from b4_b8_r154_deterministic_automatic_replay import canonical_hash, target_descriptor
from b4_b8_r165_candidate_selection_replay import new_config, normalize_events, parse_leaves
from qiskit import qasm3
from qiskit.converters import circuit_to_dag
from qiskit._accelerate.vf2_layout import vf2_layout_pass_average_score_traced
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2


METHOD = "b4_b8_r170_near_tie_design_preflight_v0"
INPUT_PATH = "benchmarks/B4_B8_R170_near_tie_candidate_v0.qasm"
RESULT_PATH = "results/B4_B8_R170_near_tie_design_preflight_v0.json"
REPORT_PATH = "research/B4_B8_R170_near_tie_design_preflight.md"
INSTRUMENTED_BINARY_SHA256 = "56101c7bedbaa157c341542d18b95e60b9d37acb9f29d6305fa2f7337cb8fd69"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bits_to_float(bits: int) -> float:
    return struct.unpack("!d", int(bits).to_bytes(8, "big"))[0]


def exact_score(event: dict[str, Any]) -> Fraction:
    leaves = parse_leaves(event["result_terms"])
    return sum((fraction for _, _, fraction in leaves), Fraction(0, 1))


def graph_summary(circuit: Any) -> dict[str, Any]:
    dag = circuit_to_dag(circuit)
    ordered_edges = []
    for node in dag.two_qubit_ops():
        ordered_edges.append(sorted((int(node.qargs[0]._index), int(node.qargs[1]._index))))
    unique_edges = sorted({tuple(edge) for edge in ordered_edges})
    active = sorted({node for edge in unique_edges for node in edge})
    return {"active_qubit_count": len(active), "active_qubits": active, "ordered_edges": ordered_edges, "unique_edges": [list(edge) for edge in unique_edges]}


def build(root: Path) -> tuple[dict[str, Any], str]:
    input_path = root / INPUT_PATH
    circuit = qasm3.load(input_path)
    backend = FakeNairobiV2()
    target = backend.target
    dag = circuit_to_dag(circuit)
    output, raw_events, _ = vf2_layout_pass_average_score_traced(
        dag, target, new_config(), strict_direction=False, operation_order="ascending"
    )
    events = normalize_events(raw_events)
    candidate_events = [
        event for event in events
        if event["kind"] == "candidate" and not event["result_terms"].startswith("returned_by_minimize_vf2")
    ]
    candidates = []
    for index, event in enumerate(candidate_events):
        exact = exact_score(event)
        candidates.append({
            "candidate_index": index,
            "mapping_terms": event["left_terms"],
            "source_score_bits": event["left_bits"],
            "source_score": bits_to_float(event["left_bits"]),
            "exact_score_numerator": str(exact.numerator),
            "exact_score_denominator": str(exact.denominator),
        })
    ordered = sorted(candidates, key=lambda row: row["source_score"])
    gap = ordered[1]["source_score"] - ordered[0]["source_score"] if len(ordered) > 1 else None
    ulp = max(math.ulp(abs(ordered[0]["source_score"])), math.ulp(abs(ordered[1]["source_score"]))) if len(ordered) > 1 else None
    summary = {
        "qiskit_calls_performed": 1,
        "candidate_event_count": len(candidate_events),
        "candidate_count": len(candidates),
        "best_two_source_score_gap": gap,
        "best_two_source_score_gap_ulp_ratio": gap / ulp if gap is not None and ulp else None,
        "source_score_gap_is_one_ulp": gap is not None and gap == ulp,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "route_change_performed": False,
    }
    result = {
        "method": METHOD,
        "version": 0,
        "title": "B4/B8 R170 near-tie design preflight",
        "status": "near_tie_design_preflight_complete",
        "classification": "one_ulp_source_gap_observed",
        "source_target_id": "T-B4-002cn/T-B8-003cr/T-B10-009cd-r170-design",
        "input": INPUT_PATH,
        "input_sha256": file_sha256(input_path),
        "target": {"backend": "FakeNairobiV2", "descriptor_sha256": target_descriptor(backend)["descriptor_hash"]},
        "instrumented_binary_sha256": INSTRUMENTED_BINARY_SHA256,
        "graph": graph_summary(circuit),
        "candidates": ordered,
        "summary": summary,
        "claim_boundary": {"what_is_supported": "a one-call design preflight exposing a near-tied source-score pair on the frozen input", "what_is_not_supported": "a full replay, arithmetic-policy conclusion, production mapping change, confirmed Qiskit bug, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit"},
    }
    result["payload_hash"] = canonical_hash(result)
    return result, "\n".join([
        "# R170 Near-Tie Design Preflight",
        "",
        f"- Status: `{result['status']}`",
        f"- Classification: `{result['classification']}`",
        f"- Candidate count: `{summary['candidate_count']}`",
        f"- Best-two source-score gap: `{summary['best_two_source_score_gap']}`",
        f"- Gap in ULP units: `{summary['best_two_source_score_gap_ulp_ratio']}`",
        "",
        "## Heuristic question",
        "",
        "Can a target-compatible graph with a one-ULP source-score gap make the arithmetic-policy boundary observable?",
        "",
        "The preflight runs one ascending-order call only. It selects no mapping, performs no simulation, and is not the R170 full replay result. The full candidate-level replay remains separately preregistered.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    result_path = root / RESULT_PATH
    report_path = root / REPORT_PATH
    if result_path.exists() or report_path.exists():
        raise ValueError("R170 design preflight evidence already exists; refusing to overwrite")
    result, report = build(root)
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "classification": result["classification"], "summary": result["summary"], "payload_hash": result["payload_hash"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
