#!/usr/bin/env python3
"""Build a planning-level reduction graph for mapping the boundary of BQP."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


NODES = {
    "period_finding": {
        "family": "algebraic",
        "bqp_status": "canonical_exponential_speedup",
        "input_model": "succinct_oracle_or_modular_arithmetic",
        "verification": "classical_certificate_available",
        "main_risk": "none_for_standard_instances",
    },
    "abelian_hidden_subgroup": {
        "family": "algebraic",
        "bqp_status": "canonical_speedup",
        "input_model": "oracle",
        "verification": "problem_dependent",
        "main_risk": "oracle_model_gap",
    },
    "nonabelian_hidden_subgroup": {
        "family": "algebraic",
        "bqp_status": "open_or_limited",
        "input_model": "oracle",
        "verification": "hard",
        "main_risk": "measurement_and_reduction_gap",
    },
    "hamiltonian_simulation": {
        "family": "simulation",
        "bqp_status": "natural_quantum_task",
        "input_model": "local_or_sparse_hamiltonian",
        "verification": "observable_dependent",
        "main_risk": "state_preparation",
    },
    "phase_estimation_observables": {
        "family": "simulation",
        "bqp_status": "conditional_speedup",
        "input_model": "prepared_state_plus_unitary",
        "verification": "observable_estimates",
        "main_risk": "state_preparation",
    },
    "linear_systems_hhl": {
        "family": "linear_algebra",
        "bqp_status": "conditional_exponential_speedup",
        "input_model": "block_encoding_or_qram",
        "verification": "observable_dependent",
        "main_risk": "data_loading_and_condition_number",
    },
    "amplitude_estimation": {
        "family": "estimation",
        "bqp_status": "quadratic_speedup",
        "input_model": "sampler_or_oracle",
        "verification": "statistical",
        "main_risk": "oracle_construction",
    },
    "random_circuit_sampling": {
        "family": "sampling",
        "bqp_status": "evidence_for_sampling_advantage",
        "input_model": "circuit_description",
        "verification": "statistical_or_cross_entropy",
        "main_risk": "spoofing_and_noise",
    },
    "iqp_sampling": {
        "family": "sampling",
        "bqp_status": "complexity_evidence",
        "input_model": "commuting_circuit_description",
        "verification": "hard",
        "main_risk": "average_case_assumptions",
    },
    "qaoa_optimization": {
        "family": "optimization",
        "bqp_status": "uncertain_practical_advantage",
        "input_model": "classical_instance",
        "verification": "objective_value",
        "main_risk": "classical_heuristics",
    },
    "quantum_machine_learning": {
        "family": "learning",
        "bqp_status": "conditional_or_contested",
        "input_model": "data_state_or_feature_map",
        "verification": "generalization",
        "main_risk": "data_loading_and_dequantization",
    },
    "interactive_verification": {
        "family": "verification",
        "bqp_status": "trust_layer",
        "input_model": "protocol_transcript",
        "verification": "interactive_or_statistical",
        "main_risk": "protocol_overhead",
    },
}


EDGES = [
    {
        "source": "period_finding",
        "target": "abelian_hidden_subgroup",
        "reduction_type": "special_case_to_general_family",
        "advantage_preserved": True,
        "failure_modes": [],
        "evidence_level": "textbook",
    },
    {
        "source": "abelian_hidden_subgroup",
        "target": "nonabelian_hidden_subgroup",
        "reduction_type": "generalization_attempt",
        "advantage_preserved": False,
        "failure_modes": ["measurement_gap", "missing_efficient_fourier_sampling"],
        "evidence_level": "open_boundary",
    },
    {
        "source": "hamiltonian_simulation",
        "target": "phase_estimation_observables",
        "reduction_type": "algorithmic_subroutine",
        "advantage_preserved": True,
        "failure_modes": ["state_preparation"],
        "evidence_level": "conditional",
    },
    {
        "source": "phase_estimation_observables",
        "target": "linear_systems_hhl",
        "reduction_type": "block_encoding_view",
        "advantage_preserved": False,
        "failure_modes": ["data_loading", "condition_number", "readout"],
        "evidence_level": "fragile",
    },
    {
        "source": "linear_systems_hhl",
        "target": "quantum_machine_learning",
        "reduction_type": "qml_application_claim",
        "advantage_preserved": False,
        "failure_modes": ["data_loading", "dequantization", "generalization"],
        "evidence_level": "contested",
    },
    {
        "source": "amplitude_estimation",
        "target": "phase_estimation_observables",
        "reduction_type": "estimation_wrapper",
        "advantage_preserved": True,
        "failure_modes": ["oracle_construction"],
        "evidence_level": "conditional",
    },
    {
        "source": "random_circuit_sampling",
        "target": "interactive_verification",
        "reduction_type": "verification_layer",
        "advantage_preserved": True,
        "failure_modes": ["protocol_overhead", "noise"],
        "evidence_level": "research_program",
    },
    {
        "source": "iqp_sampling",
        "target": "random_circuit_sampling",
        "reduction_type": "sampling_complexity_family",
        "advantage_preserved": True,
        "failure_modes": ["average_case_assumptions"],
        "evidence_level": "complexity_evidence",
    },
    {
        "source": "qaoa_optimization",
        "target": "amplitude_estimation",
        "reduction_type": "objective_estimation",
        "advantage_preserved": False,
        "failure_modes": ["classical_heuristics", "oracle_construction"],
        "evidence_level": "weak",
    },
    {
        "source": "hamiltonian_simulation",
        "target": "random_circuit_sampling",
        "reduction_type": "dynamics_to_sampling",
        "advantage_preserved": True,
        "failure_modes": ["verification", "noise"],
        "evidence_level": "conditional",
    },
    {
        "source": "quantum_machine_learning",
        "target": "linear_systems_hhl",
        "reduction_type": "linear_algebra_subroutine_claim",
        "advantage_preserved": False,
        "failure_modes": ["data_loading", "output_readout"],
        "evidence_level": "fragile",
    },
    {
        "source": "interactive_verification",
        "target": "random_circuit_sampling",
        "reduction_type": "trust_to_sampling_task",
        "advantage_preserved": False,
        "failure_modes": ["verification_not_computation", "protocol_overhead"],
        "evidence_level": "boundary_warning",
    },
    {
        "source": "phase_estimation_observables",
        "target": "amplitude_estimation",
        "reduction_type": "observable_estimation_link",
        "advantage_preserved": True,
        "failure_modes": ["precision"],
        "evidence_level": "conditional",
    },
    {
        "source": "nonabelian_hidden_subgroup",
        "target": "period_finding",
        "reduction_type": "restricted_case_projection",
        "advantage_preserved": True,
        "failure_modes": ["restriction_too_strong"],
        "evidence_level": "restricted",
    },
]


def classify_edges(edges: list[dict]) -> dict:
    failure_modes = Counter()
    preserving = []
    fragile = []
    for edge in edges:
        failure_modes.update(edge["failure_modes"])
        if edge["advantage_preserved"]:
            preserving.append(edge)
        else:
            fragile.append(edge)
    return {
        "advantage_preserving_edges": preserving,
        "fragile_edges": fragile,
        "failure_mode_counts": dict(failure_modes),
    }


def connected_components(nodes: dict, edges: list[dict]) -> list[list[str]]:
    graph = defaultdict(set)
    for edge in edges:
        graph[edge["source"]].add(edge["target"])
        graph[edge["target"]].add(edge["source"])
    seen = set()
    components = []
    for node in nodes:
        if node in seen:
            continue
        stack = [node]
        component = []
        seen.add(node)
        while stack:
            current = stack.pop()
            component.append(current)
            for nxt in graph[current]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        components.append(sorted(component))
    return components


def theorem_targets(edges: list[dict]) -> list[dict]:
    targets = []
    for edge in edges:
        if edge["advantage_preserved"]:
            targets.append(
                {
                    "name": f"{edge['source']}__to__{edge['target']}",
                    "goal": "prove restricted advantage preservation under explicit input and verification assumptions",
                    "edge_type": edge["reduction_type"],
                    "known_failure_modes_to_control": edge["failure_modes"],
                }
            )
        elif "data_loading" in edge["failure_modes"] or "dequantization" in edge["failure_modes"]:
            targets.append(
                {
                    "name": f"{edge['source']}__to__{edge['target']}_negative_boundary",
                    "goal": "formalize conditions where claimed speedup is erased",
                    "edge_type": edge["reduction_type"],
                    "known_failure_modes_to_control": edge["failure_modes"],
                }
            )
    return targets


def run() -> dict:
    classified = classify_edges(EDGES)
    components = connected_components(NODES, EDGES)
    targets = theorem_targets(EDGES)
    node_family_counts = Counter(node["family"] for node in NODES.values())
    fragile_failure_modes = classified["failure_mode_counts"]
    return {
        "benchmark_id": "B10",
        "method": "bqp_boundary_reduction_graph_v0",
        "model_status": "taxonomy_and_reduction_planning_not_complexity_theorem",
        "node_count": len(NODES),
        "edge_count": len(EDGES),
        "connected_component_count": len(components),
        "node_family_counts": dict(node_family_counts),
        "advantage_preserving_edge_count": len(classified["advantage_preserving_edges"]),
        "fragile_edge_count": len(classified["fragile_edges"]),
        "failure_mode_counts": fragile_failure_modes,
        "top_failure_modes": [mode for mode, _count in Counter(fragile_failure_modes).most_common(5)],
        "restricted_theorem_target_count": len(targets),
        "nodes": [{"id": key, **value} for key, value in sorted(NODES.items())],
        "edges": EDGES,
        "connected_components": components,
        "restricted_theorem_targets": targets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
