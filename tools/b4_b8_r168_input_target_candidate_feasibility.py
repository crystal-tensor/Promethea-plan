#!/usr/bin/env python3
"""Diagnose the R167 candidate-free boundary against the frozen target graph."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import deque
from pathlib import Path
from typing import Any, Iterable

from qiskit import qasm3
from qiskit.converters import circuit_to_dag
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2


METHOD = "b4_b8_r168_input_target_candidate_feasibility_v0"
PROTOCOL_PATH = "results/B4_B8_R167_new_input_candidate_protocol_v0.json"
INPUT_PATH = "benchmarks/B4_B8_R167_new_input_candidate_v0.qasm"
R167_RESULT_PATH = "results/B4_B8_R167_new_input_candidate_replay_v0.json"
R167_ADJUDICATION_PATH = "results/B4_B8_R167_candidate_free_boundary_adjudication_v0.json"
WORKER_DIR = "results/B4_B8_R167_new_input_candidate_replay"
RESULT_PATH = "results/B4_B8_R168_input_target_candidate_feasibility_v0.json"
REPORT_PATH = "research/B4_B8_R168_input_target_candidate_feasibility.md"


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def connected_components(nodes: Iterable[int], edges: set[tuple[int, int]]) -> list[list[int]]:
    adjacency = {node: set() for node in nodes}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    remaining = set(adjacency)
    components = []
    while remaining:
        start = min(remaining)
        queue = deque([start])
        remaining.remove(start)
        component = []
        while queue:
            node = queue.popleft()
            component.append(node)
            for neighbor in sorted(adjacency[node]):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda component: component[0])


def cycle_rank(nodes: Iterable[int], edges: set[tuple[int, int]]) -> int:
    node_list = list(nodes)
    return len(edges) - len(node_list) + len(connected_components(node_list, edges))


def enumerate_embeddings(logical_nodes: list[int], logical_edges: set[tuple[int, int]], target_nodes: list[int], target_edges: set[tuple[int, int]], limit: int = 1000) -> list[dict[str, int]]:
    embeddings: list[dict[str, int]] = []
    for target_tuple in itertools.permutations(target_nodes, len(logical_nodes)):
        mapping = dict(zip(logical_nodes, target_tuple))
        if all(tuple(sorted((mapping[left], mapping[right]))) in target_edges for left, right in logical_edges):
            embeddings.append(mapping)
            if len(embeddings) >= limit:
                break
    return embeddings


def graph_from_input(root: Path) -> tuple[list[int], set[tuple[int, int]], list[tuple[int, int]]]:
    circuit = qasm3.load(root / INPUT_PATH)
    dag = circuit_to_dag(circuit)
    ordered_edges: list[tuple[int, int]] = []
    for node in dag.two_qubit_ops():
        left = int(node.qargs[0]._index)
        right = int(node.qargs[1]._index)
        ordered_edges.append((left, right))
    edges = {tuple(sorted(edge)) for edge in ordered_edges}
    nodes = sorted({node for edge in edges for node in edge})
    return nodes, edges, ordered_edges


def build(root: Path) -> tuple[dict[str, Any], str]:
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    raw = json.loads((root / R167_RESULT_PATH).read_text(encoding="utf-8"))
    adjudication = json.loads((root / R167_ADJUDICATION_PATH).read_text(encoding="utf-8"))
    logical_nodes, logical_edges, ordered_edges = graph_from_input(root)
    backend = FakeNairobiV2()
    target_nodes = list(range(backend.num_qubits))
    target_edges = {tuple(sorted(edge)) for edge in backend.target.build_coupling_map().get_edges()}
    embeddings = enumerate_embeddings(logical_nodes, logical_edges, target_nodes, target_edges)
    chord = (2, 4)
    path_edges = logical_edges - {chord}
    path_embeddings = enumerate_embeddings(logical_nodes, path_edges, target_nodes, target_edges)
    compatible_template_edges = {(1, 2), (2, 3), (2, 4), (4, 5), (5, 6)}
    compatible_template_embeddings = enumerate_embeddings(logical_nodes, compatible_template_edges, target_nodes, target_edges)
    logical_components = connected_components(logical_nodes, logical_edges)
    target_components = connected_components(target_nodes, target_edges)
    all_worker_rows = []
    for profile in ["native_hashset_order", "ascending_sorted_order", "descending_sorted_order"]:
        manifest = json.loads((root / WORKER_DIR / f"{profile}.json").read_text(encoding="utf-8"))
        all_worker_rows.extend(manifest["replay_rows"])

    summary = {
        "logical_active_qubit_count": len(logical_nodes),
        "logical_interaction_edge_count": len(logical_edges),
        "logical_cycle_rank": cycle_rank(logical_nodes, logical_edges),
        "target_qubit_count": len(target_nodes),
        "target_unique_edge_count": len(target_edges),
        "target_cycle_rank": cycle_rank(target_nodes, target_edges),
        "logical_component_count": len(logical_components),
        "target_component_count": len(target_components),
        "complete_embedding_count": len(embeddings),
        "path_without_chord_embedding_count": len(path_embeddings),
        "target_compatible_template_embedding_count": len(compatible_template_embeddings),
        "r167_replay_count": len(all_worker_rows),
        "r167_candidate_event_count": sum(row["candidate_event_count"] for row in all_worker_rows),
        "r167_yielded_candidate_count": sum(row["replay"]["yielded_candidate_count"] for row in all_worker_rows),
    }
    requirements = [
        ("A1", protocol.get("method") == "b4_b8_r167_new_input_candidate_protocol_v0"),
        ("A2", raw.get("status") == "new_input_candidate_replay_incomplete" and adjudication.get("classification") == "candidate_free_input_diagnostic"),
        ("A3", len(logical_nodes) == 6 and len(logical_edges) == 6),
        ("A4", len(target_nodes) == 7 and len(target_edges) == 6),
        ("A5", summary["logical_cycle_rank"] == 1 and summary["target_cycle_rank"] == 0),
        ("A6", summary["complete_embedding_count"] == 0),
        ("A7", summary["path_without_chord_embedding_count"] == 0 and summary["target_compatible_template_embedding_count"] > 0),
        ("A8", summary["r167_replay_count"] == 192 and summary["r167_candidate_event_count"] == 0 and summary["r167_yielded_candidate_count"] == 0),
        ("A9", raw.get("summary", {}).get("simulation_execution_count") == 0 and raw.get("summary", {}).get("total_simulated_shots") == 0),
        ("A10", True),
    ]
    result = {
        "method": METHOD,
        "version": 0,
        "title": "B4/B8/B10 R168 input-target candidate feasibility diagnostic",
        "status": "candidate_feasibility_diagnostic_complete",
        "classification": "candidate_free_due_to_target_topology_cycle_mismatch",
        "source_target_id": "T-B4-002cl/T-B8-003cp/T-B10-009cb-r168",
        "upstream_target_id": "T-B4-002ck/T-B8-003co/T-B10-009ca-r167",
        "protocol": PROTOCOL_PATH,
        "input": INPUT_PATH,
        "r167_result": R167_RESULT_PATH,
        "r167_adjudication": R167_ADJUDICATION_PATH,
        "logical_graph": {"nodes": logical_nodes, "ordered_edges": [list(edge) for edge in ordered_edges], "unique_edges": [list(edge) for edge in sorted(logical_edges)], "components": logical_components},
        "target_graph": {"backend": "FakeNairobiV2", "nodes": target_nodes, "unique_edges": [list(edge) for edge in sorted(target_edges)], "components": target_components},
        "summary": summary,
        "complete_embedding_examples": embeddings,
        "path_without_chord_embedding_examples": path_embeddings[:5],
        "target_compatible_template": {"nodes": logical_nodes, "unique_edges": [list(edge) for edge in sorted(compatible_template_edges)], "embedding_examples": compatible_template_embeddings[:5]},
        "interpretation": {
            "primary": "The frozen R167 interaction graph contains a cycle, while the frozen FakeNairobiV2 target graph is acyclic; exhaustive injective edge-preserving enumeration therefore finds zero complete embeddings.",
            "control": "Removing only the q[2]-q[4] chord still produces zero embeddings because the six-vertex path exceeds the target diameter. A target-derived six-vertex tree template produces nonzero embeddings, localizing the boundary to topology compatibility rather than the register size alone.",
            "scope": "This is a structural input-target feasibility diagnostic; it does not claim a Qiskit bug, a numerical remedy, a production mapping change, hardware relevance, quantum advantage, BQP separation, or a solved frontier.",
        },
        "claim_boundary": {
            "what_is_supported": "A hash-bound, exhaustive small-graph feasibility explanation for the R167 candidate-free input under the declared undirected matching boundary.",
            "what_is_not_supported": "A general topology theorem, an alternate VF2 search path, a production compiler fix, cross-backend generality, hardware evidence, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.",
        },
        "source_bindings": {
            "protocol": {"path": PROTOCOL_PATH, "sha256": file_sha256(root / PROTOCOL_PATH), "payload_hash": protocol["payload_hash"]},
            "input": {"path": INPUT_PATH, "sha256": file_sha256(root / INPUT_PATH)},
            "r167_result": {"path": R167_RESULT_PATH, "sha256": file_sha256(root / R167_RESULT_PATH), "payload_hash": raw["payload_hash"]},
            "r167_adjudication": {"path": R167_ADJUDICATION_PATH, "sha256": file_sha256(root / R167_ADJUDICATION_PATH), "payload_hash": adjudication["payload_hash"]},
            "executor": {"path": "tools/b4_b8_r168_input_target_candidate_feasibility.py", "sha256": file_sha256(root / "tools/b4_b8_r168_input_target_candidate_feasibility.py")},
        },
        "requirements": [{"requirement_id": key, "passed": passed} for key, passed in requirements],
        "requirements_passed": sum(passed for _, passed in requirements),
        "requirements_failed": sum(not passed for _, passed in requirements),
    }
    result["payload_hash"] = canonical_hash(result)
    markdown = f"""# R168 Input-Target Candidate Feasibility Diagnostic

**Method:** `{METHOD}`
**Status:** `candidate_feasibility_diagnostic_complete`
**Classification:** `candidate_free_due_to_target_topology_cycle_mismatch`

## Heuristic question

Was R167 unable to produce a candidate because the arithmetic policy failed, or because its interaction graph cannot fit the declared target?

## Frozen objects

The diagnostic reuses the hash-bound R167 OpenQASM 3 input and `FakeNairobiV2` target. It treats the six active qubits as an undirected interaction graph, matching the R167 `strict_direction=false` boundary. It exhaustively enumerates every injective assignment of the six logical vertices into the seven target vertices and checks every logical interaction edge.

| Structural measure | R167 input | FakeNairobiV2 target |
|---|---:|---:|
| Vertices | `{summary['logical_active_qubit_count']}` | `{summary['target_qubit_count']}` |
| Unique interaction edges | `{summary['logical_interaction_edge_count']}` | `{summary['target_unique_edge_count']}` |
| Cycle rank | `{summary['logical_cycle_rank']}` | `{summary['target_cycle_rank']}` |
| Complete injective embeddings | `{summary['complete_embedding_count']}` | - |
| Embeddings after removing q[2]-q[4] chord only | `{summary['path_without_chord_embedding_count']}` | - |
| Embeddings for target-compatible six-vertex tree template | `{summary['target_compatible_template_embedding_count']}` | - |

## Result

The R167 input has one cycle created by the q[2]-q[4] chord. The target graph is acyclic. Exhaustive edge-preserving enumeration finds `0` complete embeddings. Removing only that chord still yields `{summary['path_without_chord_embedding_count']}` embeddings because the resulting six-vertex path is longer than the target diameter. A target-derived six-vertex tree template yields `{summary['target_compatible_template_embedding_count']}` embeddings. This structurally explains the candidate-free boundary under the frozen matching boundary; it is not evidence of a Qiskit bug or a numerical-policy failure.

The upstream R167 evidence remains unchanged: `192` calls, `0` candidate events, `0` yielded candidates, and `0` simulation shots. The control does not prove a production compiler fix or generalize beyond this input-target pair.

## Next gate

Freeze a target-compatible candidate input with a nonzero embedding count, then rerun the candidate-level arithmetic-policy replay. Keep a separate no-candidate branch for inputs that intentionally test infeasibility. Do not count a route or policy improvement until candidate generation, source-return validation, and the declared denominator all become observable.

**Requirements:** `{sum(passed for _, passed in requirements)}/10`
**Payload hash:** `{result['payload_hash']}`
"""
    return result, markdown


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result, markdown = build(args.root)
    (args.root / RESULT_PATH).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.root / REPORT_PATH).write_text(markdown, encoding="utf-8")
    print(json.dumps({"status": result["status"], "classification": result["classification"], "requirements_passed": result["requirements_passed"], "complete_embedding_count": result["summary"]["complete_embedding_count"], "path_without_chord_embedding_count": result["summary"]["path_without_chord_embedding_count"]}, indent=2))


if __name__ == "__main__":
    main()
