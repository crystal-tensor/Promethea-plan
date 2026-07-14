#!/usr/bin/env python3
"""Freeze the R157 direct VF2PostLayout tie-isolation experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from collections import Counter
from pathlib import Path

from qiskit import qasm3

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r128_transpiler_loop_layout_ranking import package_version
from b4_b8_r153_independent_seed_replication_holdout import TARGET_CLASSES
from b4_b8_r154_deterministic_automatic_replay import target_descriptor


METHOD = "b4_b8_r157_vf2_tie_isolation_protocol_v0"
R156_RESULT_PATH = "results/B4_B8_R156_transpiler_variant_capture_v0.json"
R156_VARIANTS_PATH = "results/B4_B8_R156_transpiler_variant_capture/variant_summary.json"
R156_DIVERGENCE_PATH = "results/B4_B8_R156_transpiler_variant_capture/pass_divergence.json"
R156_TRACE_A_PATH = "results/B4_B8_R156_transpiler_variant_capture/process_00_trace.json"
R156_TRACE_B_PATH = "results/B4_B8_R156_transpiler_variant_capture/process_01_trace.json"
R156_PROTOCOL_PATH = "results/B4_B8_R156_transpiler_variant_capture_protocol_v0.json"
R156_CONTRACT_PATH = "benchmarks/B4_B8_R156_transpiler_variant_capture_contract_v0.json"
R154_REFERENCE_MANIFEST_PATH = "results/B4_B8_R154_deterministic_automatic_replay/reference_manifest.json"
INPUT_PATH = "benchmarks/B4_B8_R157_vf2_post_layout_input_v0.qasm"
INPUT_SHA256 = "ce216610e995b4c8b4bd9de6547ac6069961e1eb8881997aa05e0068ea16ab98"
RESULT_PATH = "results/B4_B8_R157_vf2_tie_isolation_protocol_v0.json"
REPORT_PATH = "research/B4_B8_R157_vf2_tie_isolation_protocol.md"
CONTRACT_PATH = "benchmarks/B4_B8_R157_vf2_tie_isolation_contract_v0.json"
QISKIT_SOURCE_COMMIT = "0fd015a22b84c9082173597a5d2304dc0aaec08c"
QISKIT_VF2_SOURCE_PATH = "crates/transpiler/src/passes/vf2/vf2_layout.rs"
QISKIT_VF2_SOURCE_SHA256 = "267810aaddb8ac9336f4404e7da34c31e07eec725eb1baa4ed6bf32ff7448ca4"


def canonical_hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def source_binding(root: Path, path: str, payload: dict | None = None) -> dict:
    binding = {"path": path, "sha256": file_sha256(root / path)}
    if payload is not None and "payload_hash" in payload:
        binding["payload_hash"] = payload["payload_hash"]
    return binding


def deterministic_environment() -> dict[str, str]:
    return {
        "PYTHONHASHSEED": "0",
        "RAYON_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "QISKIT_PARALLEL": "FALSE",
    }


def average_target_error(target: object, qargs: tuple[int, ...]) -> float:
    errors = []
    for name in target.operation_names_for_qargs(qargs):
        if qargs not in target[name]:
            continue
        properties = target[name][qargs]
        errors.append(
            0.0
            if properties is None or properties.error is None
            else float(properties.error)
        )
    if not errors:
        raise ValueError(f"R157 target has no concrete operations for {qargs}")
    return sum(errors) / len(errors)


def tie_score_evidence(root: Path, backend: object) -> dict:
    circuit = qasm3.load(root / INPUT_PATH)
    one_qubit_counts: Counter[int] = Counter()
    two_qubit_counts: Counter[tuple[int, int]] = Counter()
    for instruction in circuit.data:
        qargs = tuple(circuit.find_bit(bit).index for bit in instruction.qubits)
        if len(qargs) == 1:
            one_qubit_counts[qargs[0]] += 1
        elif len(qargs) == 2:
            two_qubit_counts[qargs] += 1
    mappings = {
        "endpoint_4_to_0": [6, 5, 4, 3, 0, 1, 2],
        "endpoint_4_to_2": [6, 5, 4, 3, 2, 1, 0],
    }
    mapping_rows = []
    for mapping_id, mapping in mappings.items():
        one_qubit_score = sum(
            count * average_target_error(backend.target, (mapping[virtual],))
            for virtual, count in one_qubit_counts.items()
        )
        two_qubit_score = sum(
            count
            * average_target_error(
                backend.target, (mapping[left], mapping[right])
            )
            for (left, right), count in two_qubit_counts.items()
        )
        mapping_rows.append(
            {
                "mapping_id": mapping_id,
                "mapping_vector": mapping,
                "one_qubit_score": one_qubit_score,
                "two_qubit_score": two_qubit_score,
                "total_score": one_qubit_score + two_qubit_score,
            }
        )
    return {
        "input_circuit_size": circuit.size(),
        "input_circuit_depth": circuit.depth(),
        "one_qubit_operation_counts": {
            str(key): value for key, value in sorted(one_qubit_counts.items())
        },
        "two_qubit_operation_counts": {
            f"{left}->{right}": value
            for (left, right), value in sorted(two_qubit_counts.items())
        },
        "mapping_rows": mapping_rows,
        "scores_exactly_equal_in_python_recalculation": (
            mapping_rows[0]["total_score"] == mapping_rows[1]["total_score"]
        ),
        "shared_total_score": mapping_rows[0]["total_score"],
    }


def build(root: Path) -> tuple[dict, dict]:
    payloads = {
        "r156_result": json.loads((root / R156_RESULT_PATH).read_text()),
        "r156_variants": json.loads((root / R156_VARIANTS_PATH).read_text()),
        "r156_divergence": json.loads((root / R156_DIVERGENCE_PATH).read_text()),
        "r156_protocol": json.loads((root / R156_PROTOCOL_PATH).read_text()),
    }
    source_paths = {
        "r156_result": R156_RESULT_PATH,
        "r156_variants": R156_VARIANTS_PATH,
        "r156_divergence": R156_DIVERGENCE_PATH,
        "r156_trace_a": R156_TRACE_A_PATH,
        "r156_trace_b": R156_TRACE_B_PATH,
        "r156_protocol": R156_PROTOCOL_PATH,
        "r156_contract": R156_CONTRACT_PATH,
        "r154_reference_manifest": R154_REFERENCE_MANIFEST_PATH,
        "direct_replay_input": INPUT_PATH,
    }
    source_bindings = {
        key: source_binding(root, path, payloads.get(key))
        for key, path in source_paths.items()
    }
    backend = TARGET_CLASSES["FakeNairobiV2"]()
    descriptor = target_descriptor(backend)
    r154_reference = json.loads((root / R154_REFERENCE_MANIFEST_PATH).read_text())
    expected_descriptor = next(
        row
        for row in r154_reference["target_descriptor_rows"]
        if row["target_snapshot"] == "FakeNairobiV2"
    )["descriptor_hash"]
    tie_evidence = tie_score_evidence(root, backend)
    profiles = [
        {
            "profile_id": "native_target_independent_process",
            "process_count": 32,
            "replays_per_process": 1,
            "target_construction": "fresh FakeNairobiV2 target in each process",
            "target_order": "native",
            "shared_target_within_process": False,
        },
        {
            "profile_id": "canonical_ascending_independent_process",
            "process_count": 32,
            "replays_per_process": 1,
            "target_construction": "fresh target rebuilt with operation names and qargs ascending",
            "target_order": "ascending",
            "shared_target_within_process": False,
        },
        {
            "profile_id": "canonical_descending_independent_process",
            "process_count": 32,
            "replays_per_process": 1,
            "target_construction": "fresh target rebuilt with operation names and qargs descending",
            "target_order": "descending",
            "shared_target_within_process": False,
        },
        {
            "profile_id": "fresh_target_same_process",
            "process_count": 1,
            "replays_per_process": 32,
            "target_construction": "fresh native target for every replay in one process",
            "target_order": "native",
            "shared_target_within_process": False,
        },
        {
            "profile_id": "shared_target_same_process",
            "process_count": 1,
            "replays_per_process": 32,
            "target_construction": "one native target shared across all replays in one process",
            "target_order": "native",
            "shared_target_within_process": True,
        },
    ]
    protocol = {
        "research_question": (
            "Do the two exactly tied R156 post_layout mappings arise from process-local or "
            "Target-order state when VF2PostLayout is replayed directly on one frozen input?"
        ),
        "snapshot_name": "FakeNairobiV2",
        "target_descriptor_sha256": descriptor["descriptor_hash"],
        "expected_target_descriptor_sha256": expected_descriptor,
        "input_path": INPUT_PATH,
        "input_qasm_sha256": INPUT_SHA256,
        "input_source_callback_count": 16,
        "input_source_pass": "CheckMap",
        "vf2_pass": "VF2PostLayout",
        "vf2_configuration": {
            "seed": -1,
            "call_limit": 30000000,
            "time_limit": None,
            "strict_direction": False,
            "max_trials": 250000,
        },
        "profile_count": len(profiles),
        "profiles": profiles,
        "total_process_count": sum(row["process_count"] for row in profiles),
        "total_direct_replay_count": sum(
            row["process_count"] * row["replays_per_process"] for row in profiles
        ),
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "process_environment": deterministic_environment(),
        "tie_score_evidence": tie_evidence,
        "classification_rule": {
            "endpoint_4_to_0": [6, 5, 4, 3, 0, 1, 2],
            "endpoint_4_to_2": [6, 5, 4, 3, 2, 1, 0],
            "other_mapping": "any solution mapping outside the two R156 mapping vectors",
            "no_solution": "VF2PostLayout emits no post_layout mapping",
            "profile_collapse": "one mapping class covers every replay in a profile",
            "profile_variation": "more than one mapping class occurs in a profile",
        },
        "diagnostic_completion_rule": (
            "all 98 process artifacts and all 160 replay rows are retained; collapse, "
            "variation, new mappings, and no-solution rows are all admissible outcomes"
        ),
        "qiskit_source": {
            "repository": "https://github.com/Qiskit/qiskit",
            "release": "2.4.1",
            "commit": QISKIT_SOURCE_COMMIT,
            "path": QISKIT_VF2_SOURCE_PATH,
            "sha256": QISKIT_VF2_SOURCE_SHA256,
            "relevant_boundary": (
                "shuffle_seed is None for seed -1; VF2 uses strictly decreasing score "
                "restriction and returns the last improvement"
            ),
        },
        "frozen_software": {
            "python": platform.python_version(),
            "qiskit": package_version("qiskit"),
            "qiskit_aer": package_version("qiskit-aer"),
            "qiskit_ibm_runtime": package_version("qiskit-ibm-runtime"),
        },
        "new_hidden_seed_count": 0,
        "candidate_selection_performed": False,
        "route_change_performed": False,
        "sampling_performed": False,
    }
    requirements = [
        {"requirement_id": "R1", "label": "R156 result, variants, divergence, traces, protocol, and contract are hash-bound", "passed": payloads["r156_result"]["summary"]["global_acceptance"] is True},
        {"requirement_id": "R2", "label": "the direct replay QASM exactly matches the R156 count-16 circuit hash", "passed": file_sha256(root / INPUT_PATH) == INPUT_SHA256 and tie_evidence["input_circuit_size"] == 77 and tie_evidence["input_circuit_depth"] == 39},
        {"requirement_id": "R3", "label": "the FakeNairobiV2 target descriptor matches the R154 sealed descriptor", "passed": descriptor["descriptor_hash"] == expected_descriptor == "702c8fd9dcf67a069e7af63e31a57c74c17aaa5e3c5b6d8c2e28ec0c049c0de7"},
        {"requirement_id": "R4", "label": "both R156 mappings are independently rescored and exactly tied", "passed": tie_evidence["scores_exactly_equal_in_python_recalculation"] is True and tie_evidence["shared_total_score"] == 0.45894321220828727},
        {"requirement_id": "R5", "label": "five isolation profiles fix 98 processes and 160 direct replays", "passed": len(profiles) == 5 and protocol["total_process_count"] == 98 and protocol["total_direct_replay_count"] == 160},
        {"requirement_id": "R6", "label": "native, ascending, descending, fresh-target same-process, and shared-target same-process controls are present", "passed": [row["profile_id"] for row in profiles] == ["native_target_independent_process", "canonical_ascending_independent_process", "canonical_descending_independent_process", "fresh_target_same_process", "shared_target_same_process"]},
        {"requirement_id": "R7", "label": "all mapping, new-mapping, no-solution, collapse, and variation outcomes remain admissible", "passed": len(protocol["classification_rule"]) == 6 and "admissible outcomes" in protocol["diagnostic_completion_rule"]},
        {"requirement_id": "R8", "label": "Qiskit source commit, Rust path, source hash, pass configuration, software, and one-thread environment are frozen", "passed": protocol["qiskit_source"]["sha256"] == QISKIT_VF2_SOURCE_SHA256 and protocol["vf2_configuration"]["seed"] == -1 and all(protocol["frozen_software"].values())},
        {"requirement_id": "R9", "label": "no hidden seed, selection, route change, simulation, or sampling is introduced", "passed": protocol["new_hidden_seed_count"] == 0 and protocol["candidate_selection_performed"] is False and protocol["route_change_performed"] is False and protocol["sampling_performed"] is False and protocol["total_simulated_shots"] == 0},
        {"requirement_id": "R10", "label": "direct-pass localization is separated from mechanism, bug, hardware, advantage, BQP, and credit claims", "passed": True},
    ]
    claim_boundary = {
        "what_is_supported": (
            "a preregistered direct-pass isolation of the two exactly tied public R156 mappings"
        ),
        "what_is_not_supported": (
            "a lower-level mechanism or confirmed Qiskit-bug claim, a general compiler "
            "determinism theorem, hidden statistical evidence, simulation or hardware "
            "performance, transfer, route advantage, quantum advantage, BQP separation, "
            "solved B4/B8/B10, or new credit"
        ),
    }
    payload = {
        "title": "B4/B8 R157 VF2 tie-isolation protocol",
        "version": 0,
        "method": METHOD,
        "status": "vf2_tie_isolation_protocol_frozen_before_execution",
        "model_status": "direct_pass_process_and_target_order_matrix_unopened",
        "generated_at_unix": int(time.time()),
        "source_target_id": "T-B4-002bv/T-B8-003bz/T-B10-009bn",
        "upstream_target_id": "T-B4-002bu/T-B8-003by/T-B10-009bm",
        "source_bindings": source_bindings,
        "protocol": protocol,
        "requirements": requirements,
        "requirement_count": 10,
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "execution_started": False,
        "claim_boundary": claim_boundary,
    }
    payload["payload_hash"] = canonical_hash(payload)
    contract = {
        "contract_id": "B4-B8-R157-vf2-tie-isolation-contract-v0",
        "contract_status": "public_preregistration_execution_unopened",
        "target_id": payload["source_target_id"],
        "upstream_target_id": payload["upstream_target_id"],
        "research_question": protocol["research_question"],
        "source_bindings": {
            "protocol_path": RESULT_PATH,
            "protocol_payload_hash": payload["payload_hash"],
            "protocol_sha256": None,
            **source_bindings,
        },
        "execution_protocol": protocol,
        "acceptance_conditions": [
            {"condition_id": "A1", "condition": "contract, protocol, R156 evidence, input QASM, target descriptor, and source hashes remain exact"},
            {"condition_id": "A2", "condition": "98 post-preregistration process artifacts contain exactly 160 direct replay rows"},
            {"condition_id": "A3", "condition": "every replay uses the frozen QASM, target descriptor, pass configuration, software, and process environment"},
            {"condition_id": "A4", "condition": "all five native/order/process-sharing profiles complete without post-hoc replacement"},
            {"condition_id": "A5", "condition": "every replay retains process identity, target-order identity, mapping vector, mapping class, stop reason, and elapsed time"},
            {"condition_id": "A6", "condition": "within-profile and cross-profile mapping distributions are complete"},
            {"condition_id": "A7", "condition": "new mappings and no-solution rows are retained rather than excluded"},
            {"condition_id": "A8", "condition": "native, ascending, descending, fresh-target same-process, and shared-target same-process contrasts are emitted"},
            {"condition_id": "A9", "condition": "both R156 mappings are independently rescored and their exact tie remains documented"},
            {"condition_id": "A10", "condition": "no hidden seed, selection, route change, sampling, mechanism, bug, hardware, transfer, advantage, BQP, solved-frontier, or credit claim occurs"},
        ],
        "claim_boundary": claim_boundary,
    }
    return payload, contract


def report(payload: dict, contract_sha256: str) -> str:
    p = payload["protocol"]
    return f"""# B4/B8 R157 VF2 Tie-Isolation Protocol

- Input QASM hash / size / depth: `{p['input_qasm_sha256']}` / `{p['tie_score_evidence']['input_circuit_size']}` / `{p['tie_score_evidence']['input_circuit_depth']}`
- Target descriptor: `{p['target_descriptor_sha256']}`
- Profiles / OS processes / direct replays: `{p['profile_count']}` / `{p['total_process_count']}` / `{p['total_direct_replay_count']}`
- VF2 seed / strict direction / max trials: `{p['vf2_configuration']['seed']}` / `{str(p['vf2_configuration']['strict_direction']).lower()}` / `{p['vf2_configuration']['max_trials']}`
- Recomputed mapping score A / B: `{p['tie_score_evidence']['mapping_rows'][0]['total_score']}` / `{p['tie_score_evidence']['mapping_rows'][1]['total_score']}`
- Scores exactly equal: `{str(p['tie_score_evidence']['scores_exactly_equal_in_python_recalculation']).lower()}`
- Simulation executions / shots: `0` / `0`
- Contract SHA-256: `{contract_sha256}`
- Execution started: `false`

## Frozen Isolation

R157 removes the first sixteen full-pipeline passes from the experimental
surface. Every direct replay reads the same 77-operation OpenQASM 3 input whose
hash equals the R156 callback-16 circuit hash, then runs the exact R156
`VF2PostLayout` configuration. Three independent-process profiles compare the
native FakeNairobi target with targets rebuilt in ascending and descending
operation/qargs order. Two same-process profiles distinguish fresh target
construction from repeated use of one shared target.

The two R156 endpoint mappings have the same independently recomputed average-
error score, `0.45894321220828727`. This motivates a tie-order experiment but
does not establish the lower-level mechanism. Mapping collapse, continued
variation, a new mapping, or no solution are all valid diagnostic outcomes.
The unopened protocol makes no confirmed Qiskit-bug, general determinism,
hardware, transfer, route-advantage, quantum-advantage, BQP, solved-frontier,
or research-credit claim.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    if any((root / path).exists() for path in [RESULT_PATH, REPORT_PATH, CONTRACT_PATH]):
        raise ValueError("R157 preregistration evidence already exists; refusing to overwrite")
    payload, contract = build(root)
    write_json(root / RESULT_PATH, payload)
    contract["source_bindings"]["protocol_sha256"] = file_sha256(root / RESULT_PATH)
    write_json(root / CONTRACT_PATH, contract)
    contract_sha256 = file_sha256(root / CONTRACT_PATH)
    (root / REPORT_PATH).write_text(report(payload, contract_sha256), encoding="utf-8")
    print(json.dumps({"payload_hash": payload["payload_hash"], "contract_sha256": contract_sha256, "requirements_passed": payload["requirements_passed"], "requirements_failed": payload["requirements_failed"]}, sort_keys=True))
    return 0 if payload["requirements_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
