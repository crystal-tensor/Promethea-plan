#!/usr/bin/env python3
"""T-B4-002z/T-B8-003ad: replay R124 on historical IBM QPU snapshots."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import shutil
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import qiskit
import qiskit_aer
import qiskit_ibm_runtime
from qiskit import QuantumCircuit, qasm3, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeJakartaV2, FakeLagosV2, FakeOslo

from b4_b8_r119_private_observable_bundle_gate import build_bundle_tasks
from b4_b8_r121_private_bundle_shot_sweep import (
    basis_circuit,
    decode_counts,
    stable_hash,
    write_json,
)
from b4_b8_r122_matched_seed_prefix_replay import (
    bundle_error,
    choose_bundle,
    target_values,
)
from b4_b8_r123_independent_seed_block_replay import aggregate_task_rows
from b4_b8_r124_preregistered_holdout_block_replay import condition_row


METHOD = "b4_b8_r125_historical_snapshot_replay_v0"
STATUS = "preregistered_historical_qpu_snapshot_replay_boundary"
MODEL_STATUS = "r124_candidate_replayed_with_frozen_ibm_qpu_snapshot_properties"
TARGET_ID = "T-B4-002z/T-B8-003ad/T-B10-009r"
UPSTREAM_TARGET_ID = "T-B4-002y/T-B8-003ac/T-B10-009q"
R124_RESULT_PATH = "results/B4_B8_R124_preregistered_holdout_block_replay_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R125_historical_snapshot_replay_contract_v0.json"
CONTRACT_SHA256 = "547bef430ce85ea9052d791edd939e554b4a72f67dcabbb61169c7e02a675716"
PREREGISTRATION_DISCUSSION = "https://github.com/crystal-tensor/Prometheus-plan/discussions/126"
PREREGISTRATION_CREATED_AT = "2026-07-12T10:41:52Z"
OUT_DIR = "results/B4_B8_R125_historical_snapshot_replay"
RESULT_PATH = "results/B4_B8_R125_historical_snapshot_replay_v0.json"
REPORT_PATH = "research/B4_B8_R125_historical_snapshot_replay.md"
SNAPSHOT_CLASSES = {
    "FakeOslo": FakeOslo,
    "FakeJakartaV2": FakeJakartaV2,
    "FakeLagosV2": FakeLagosV2,
}


def contract_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_snapshot(backend_class: type) -> tuple[dict[str, Any], str]:
    backend = backend_class()
    instructions: dict[str, Any] = {}
    for operation in ["sx", "x", "cx", "measure"]:
        rows = []
        for qargs, properties in backend.target[operation].items():
            rows.append(
                {
                    "qargs": list(qargs),
                    "error": (
                        None
                        if properties is None or properties.error is None
                        else float(properties.error)
                    ),
                    "duration_s": (
                        None
                        if properties is None or properties.duration is None
                        else float(properties.duration)
                    ),
                }
            )
        instructions[operation] = sorted(rows, key=lambda row: row["qargs"])
    qubits = []
    for qubit in range(backend.num_qubits):
        properties = backend.qubit_properties(qubit)
        qubits.append(
            {
                "qubit": qubit,
                "t1_s": properties.t1,
                "t2_s": properties.t2,
                "frequency_hz": properties.frequency,
            }
        )
    payload = {
        "backend_class": backend_class.__name__,
        "backend_name": backend.name,
        "backend_version": backend.backend_version,
        "num_qubits": backend.num_qubits,
        "dt_s": backend.dt,
        "coupling_edges": sorted(
            [list(edge) for edge in backend.coupling_map.get_edges()]
        ),
        "instruction_properties": instructions,
        "qubit_properties": qubits,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload, digest


def measurement_map(circuit: QuantumCircuit) -> list[dict[str, int]]:
    rows = []
    for instruction in circuit.data:
        if instruction.operation.name != "measure":
            continue
        rows.append(
            {
                "physical_qubit": circuit.find_bit(instruction.qubits[0]).index,
                "classical_bit": circuit.find_bit(instruction.clbits[0]).index,
            }
        )
    return sorted(rows, key=lambda row: row["classical_bit"])


def compile_basis_cache(
    base: QuantumCircuit,
    backend: Any,
    transpiler_seed: int,
    optimization_level: int,
) -> tuple[dict[tuple[str, ...], QuantumCircuit], bool]:
    bases = list(itertools.product(["X", "Y", "Z"], repeat=base.num_qubits))
    logical = [basis_circuit(base, basis) for basis in bases]
    compiled = transpile(
        logical,
        backend=backend,
        optimization_level=optimization_level,
        seed_transpiler=transpiler_seed,
    )
    cache = dict(zip(bases, compiled, strict=True))
    expected_classical = list(range(base.num_qubits))
    preserved = all(
        [row["classical_bit"] for row in measurement_map(circuit)]
        == expected_classical
        for circuit in compiled
    )
    return cache, preserved


def snapshot_prefix_records(
    base: QuantumCircuit,
    simulator: AerSimulator,
    rng: np.random.Generator,
    cache: dict[tuple[str, ...], QuantumCircuit],
    maximum_shots: int,
) -> tuple[list[tuple[tuple[str, ...], np.ndarray]], str]:
    qubits = base.num_qubits
    schedule = [
        tuple(rng.choice(["X", "Y", "Z"], size=qubits))
        for _ in range(maximum_shots)
    ]
    positions: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, basis in enumerate(schedule):
        positions[basis].append(index)

    by_count: dict[int, list[tuple[str, ...]]] = defaultdict(list)
    for basis, basis_positions in positions.items():
        by_count[len(basis_positions)].append(basis)
    ordered: list[tuple[tuple[str, ...], np.ndarray] | None] = [None] * maximum_shots
    for shot_count, bases in sorted(by_count.items()):
        circuits = [cache[basis] for basis in bases]
        seed = int(rng.integers(0, 2**31 - 1))
        result = simulator.run(
            circuits,
            shots=shot_count,
            seed_simulator=seed,
        ).result()
        for circuit_index, basis in enumerate(bases):
            decoded = decode_counts(result.get_counts(circuit_index), qubits)
            basis_positions = positions[basis]
            if len(decoded) != len(basis_positions):
                raise RuntimeError("historical snapshot grouped replay count mismatch")
            assignment = rng.permutation(len(decoded))
            for position, decoded_index in zip(
                basis_positions, assignment, strict=True
            ):
                ordered[position] = (basis, decoded[int(decoded_index)])
    if any(record is None for record in ordered):
        raise RuntimeError("historical snapshot replay left unfilled positions")
    digest = hashlib.sha256(
        json.dumps(schedule, separators=(",", ":")).encode()
    ).hexdigest()
    return [record for record in ordered if record is not None], digest


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = []
    for snapshot_name, snapshot in summary["snapshots"].items():
        for shots in summary["shot_budgets"]:
            row = snapshot["by_shot_budget"][str(shots)]
            lines.append(
                f"- `{snapshot_name}` / `{shots}`: pooled point "
                f"`{row['minimum_pooled_honest_completeness']:.4f}`, pooled "
                f"Wilson lower `{row['minimum_pooled_wilson_lower']:.4f}`, "
                f"minimum leave-one-block-out lower "
                f"`{row['minimum_leave_one_block_out_wilson_lower']:.4f}`, "
                f"blocks above floor `{row['blocks_meeting_point_floor']}/"
                f"{summary['seed_block_count']}`."
            )
        lines.append(
            f"- `{snapshot_name}` decision: "
            f"`{'ACCEPT' if snapshot['snapshot_accepted'] else 'REJECT'}`; "
            + ", ".join(
                f"{row['condition_id']}={'PASS' if row['passed'] else 'FAIL'}"
                for row in snapshot["acceptance_conditions"]
            )
        )
    requirements = "\n".join(
        f"- `{row['requirement_id']}` "
        f"{'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    verdict = "ACCEPT" if summary["global_acceptance"] else "REJECT"
    return f"""# B4/B8 R125 Historical QPU Snapshot Replay

## Summary

- Target: `{TARGET_ID}`
- Upstream target: `{UPSTREAM_TARGET_ID}`
- Method: `{METHOD}`
- Status: `{STATUS}`
- Public preregistration: {PREREGISTRATION_DISCUSSION}
- Contract SHA-256: `{payload['contract']['sha256']}`
- Historical snapshots: `{', '.join(summary['snapshot_names'])}`
- Seed blocks per snapshot: `{summary['seed_block_count']}`
- Trials per block/snapshot/task: `{summary['trials_per_block_snapshot_task']}`
- Total trial rows: `{len(payload['trial_rows'])}`
- Control / candidate shots: `{summary['control_shot_budget']}` / `{summary['candidate_shot_budget']}`
- Global preregistered verdict: `{verdict}`
- Fail-to-pass / pass-to-fail transitions: `{summary['fail_to_pass_transition_count']}` / `{summary['pass_to_fail_transition_count']}`

{chr(10).join(lines)}

R125 uses frozen IBM QPU system snapshots from Qiskit IBM Runtime fake
backends. Every randomized-measurement circuit is transpiled to the snapshot
topology before Aer applies snapshot-derived noise. These are historical
properties for local testing, not current calibration data or hardware jobs.

## Requirements

{requirements}

## Claim Boundary

Supported: a preregistered local Aer replay driven by frozen historical IBM QPU
snapshot properties. Not supported: current calibrated backend evidence,
provider access, hardware execution, independent transcript evidence, protocol
or cryptographic soundness, sampling hardness, quantum advantage, BQP
separation, or B10 credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    started_at = int(time.time())
    root = root.resolve()
    contract_file = root / CONTRACT_PATH
    observed_contract_hash = contract_hash(contract_file)
    if observed_contract_hash != CONTRACT_SHA256:
        raise ValueError("R125 preregistration contract hash mismatch")
    contract = json.loads(contract_file.read_text(encoding="utf-8"))
    r124 = json.loads((root / R124_RESULT_PATH).read_text(encoding="utf-8"))
    if not r124["summary"]["global_acceptance"]:
        raise ValueError("R125 requires the accepted R124 holdout")
    if r124["payload_hash"] != contract["source_payload_hash"]:
        raise ValueError("R125 contract does not bind the current R124 payload")

    preregistered_at = int(
        datetime.fromisoformat(
            PREREGISTRATION_CREATED_AT.replace("Z", "+00:00")
        ).astimezone(timezone.utc).timestamp()
    )
    if preregistered_at >= started_at:
        raise ValueError("R125 preregistration timestamp is not before execution")
    if qiskit_ibm_runtime.__version__ != contract["software_contract"][
        "qiskit_ibm_runtime_version"
    ]:
        raise ValueError("R125 Qiskit IBM Runtime version drift")

    snapshot_contract = contract["snapshot_contract"]
    snapshot_metadata: dict[str, Any] = {}
    for row in snapshot_contract:
        backend_class = SNAPSHOT_CLASSES[row["backend_class"]]
        canonical, digest = canonical_snapshot(backend_class)
        if digest != row["canonical_snapshot_sha256"]:
            raise ValueError(f"R125 snapshot hash drift for {row['backend_class']}")
        snapshot_metadata[row["backend_class"]] = {
            "contract": row,
            "canonical": canonical,
            "sha256": digest,
        }

    design = contract["holdout_design"]
    statistic = contract["acceptance_statistic"]
    block_seeds = design["root_seeds"]
    trials_per_block = design["trials_per_block_snapshot_task"]
    control_shots = design["control_shot_budget"]
    candidate_shots = design["candidate_shot_budget"]
    maximum_shots = design["maximum_replay_shots"]
    shot_budgets = [control_shots, candidate_shots]
    tolerance = statistic["bundle_maximum_absolute_error_tolerance"]
    honest_floor = statistic["honest_completeness_floor"]
    maximum_regressions = statistic["maximum_pass_to_fail_transitions_per_snapshot"]

    output = root / OUT_DIR
    if output.exists():
        shutil.rmtree(output)
    circuits_dir = output / "circuits"
    circuits_dir.mkdir(parents=True)
    snapshots_dir = output / "snapshots"
    snapshots_dir.mkdir(parents=True)

    tasks = build_bundle_tasks()
    if [task["task_id"] for task in tasks] != design["task_ids"]:
        raise ValueError("R125 task set drifted from preregistration")
    trial_rows: list[dict[str, Any]] = []
    circuit_files: list[str] = []
    snapshot_files: list[str] = []
    measurement_maps_preserved: dict[str, bool] = {}
    compiled_circuit_count = 0

    for snapshot_index, snapshot_row in enumerate(snapshot_contract):
        snapshot_name = snapshot_row["backend_class"]
        backend = SNAPSHOT_CLASSES[snapshot_name]()
        snapshot_path = snapshots_dir / f"{snapshot_name}.json"
        write_json(snapshot_path, snapshot_metadata[snapshot_name]["canonical"])
        snapshot_files.append(str(snapshot_path.relative_to(root)))
        simulator = AerSimulator.from_backend(backend, method="density_matrix")
        snapshot_map_preserved = True
        for task_index, task in enumerate(tasks):
            base = task["circuit"]
            exact_values = target_values(task)
            cache, map_preserved = compile_basis_cache(
                base,
                backend,
                design["transpiler_seed"],
                design["transpiler_optimization_level"],
            )
            compiled_circuit_count += len(cache)
            snapshot_map_preserved = snapshot_map_preserved and map_preserved
            representative = cache[tuple("Z" for _ in range(base.num_qubits))]
            path = circuits_dir / f"{snapshot_name}_{task['task_id']}_all_z.qasm"
            path.write_text(qasm3.dumps(representative), encoding="utf-8")
            circuit_files.append(str(path.relative_to(root)))
            for block_index, block_seed in enumerate(block_seeds):
                for trial in range(trials_per_block):
                    seed_components = [
                        block_seed,
                        snapshot_index,
                        task_index,
                        trial,
                    ]
                    rng = np.random.default_rng(np.random.SeedSequence(seed_components))
                    bundle, bundle_choice = choose_bundle(task, rng)
                    records, schedule_hash = snapshot_prefix_records(
                        base, simulator, rng, cache, maximum_shots
                    )
                    by_budget = {}
                    for shots in shot_budgets:
                        error = bundle_error(records[:shots], bundle, exact_values)
                        by_budget[str(shots)] = {
                            "maximum_bundle_error": error,
                            "passed": error <= tolerance,
                        }
                    trial_rows.append(
                        {
                            "snapshot": snapshot_name,
                            "snapshot_sha256": snapshot_row[
                                "canonical_snapshot_sha256"
                            ],
                            "block_index": block_index,
                            "block_seed": block_seed,
                            "task_id": task["task_id"],
                            "trial": trial,
                            "trial_seed_components": seed_components,
                            "schedule_sha256": schedule_hash,
                            "bundle_choice": bundle_choice,
                            "budgets_share_schedule_prefix": True,
                            "budgets_share_bundle": True,
                            "transpiled_to_snapshot_target": True,
                            "logical_classical_measurement_map_preserved": map_preserved,
                            "by_shot_budget": by_budget,
                        }
                    )
        measurement_maps_preserved[snapshot_name] = snapshot_map_preserved

    snapshots: dict[str, Any] = {}
    block_rows: list[dict[str, Any]] = []
    transition_rows: list[dict[str, Any]] = []
    for snapshot_row in snapshot_contract:
        snapshot_name = snapshot_row["backend_class"]
        snapshot_trials = [
            row for row in trial_rows if row["snapshot"] == snapshot_name
        ]
        by_budget: dict[str, Any] = {}
        for shots in shot_budgets:
            pooled_rows = aggregate_task_rows(snapshot_trials, tasks, shots)
            per_block = []
            for block_index, block_seed in enumerate(block_seeds):
                selected = [
                    row
                    for row in snapshot_trials
                    if row["block_index"] == block_index
                ]
                task_rows = aggregate_task_rows(selected, tasks, shots)
                block_row = {
                    "snapshot": snapshot_name,
                    "block_index": block_index,
                    "block_seed": block_seed,
                    "shot_budget": shots,
                    "minimum_honest_completeness": min(
                        row["pass_rate"] for row in task_rows
                    ),
                    "minimum_wilson_lower": min(
                        row["wilson_lower"] for row in task_rows
                    ),
                    "task_rows": task_rows,
                }
                block_rows.append(block_row)
                per_block.append(block_row)
            leave_one_out = []
            for omitted_index, omitted_seed in enumerate(block_seeds):
                selected = [
                    row
                    for row in snapshot_trials
                    if row["block_index"] != omitted_index
                ]
                task_rows = aggregate_task_rows(selected, tasks, shots)
                leave_one_out.append(
                    {
                        "omitted_block_index": omitted_index,
                        "omitted_block_seed": omitted_seed,
                        "minimum_honest_completeness": min(
                            row["pass_rate"] for row in task_rows
                        ),
                        "minimum_wilson_lower": min(
                            row["wilson_lower"] for row in task_rows
                        ),
                        "task_rows": task_rows,
                    }
                )
            by_budget[str(shots)] = {
                "minimum_pooled_honest_completeness": min(
                    row["pass_rate"] for row in pooled_rows
                ),
                "minimum_pooled_wilson_lower": min(
                    row["wilson_lower"] for row in pooled_rows
                ),
                "minimum_leave_one_block_out_wilson_lower": min(
                    row["minimum_wilson_lower"] for row in leave_one_out
                ),
                "minimum_block_honest_completeness": min(
                    row["minimum_honest_completeness"] for row in per_block
                ),
                "blocks_meeting_point_floor": sum(
                    row["minimum_honest_completeness"] >= honest_floor
                    for row in per_block
                ),
                "pooled_task_rows": pooled_rows,
                "block_rows": per_block,
                "leave_one_block_out_rows": leave_one_out,
            }

        snapshot_transition_rows = []
        for block_index, block_seed in enumerate(block_seeds):
            for task in tasks:
                selected = [
                    row
                    for row in snapshot_trials
                    if row["block_index"] == block_index
                    and row["task_id"] == task["task_id"]
                ]
                lower = [
                    row["by_shot_budget"][str(control_shots)]["passed"]
                    for row in selected
                ]
                upper = [
                    row["by_shot_budget"][str(candidate_shots)]["passed"]
                    for row in selected
                ]
                transition = {
                    "snapshot": snapshot_name,
                    "block_index": block_index,
                    "block_seed": block_seed,
                    "task_id": task["task_id"],
                    "lower_budget": control_shots,
                    "upper_budget": candidate_shots,
                    "fail_to_pass": sum(
                        (not before) and after
                        for before, after in zip(lower, upper, strict=True)
                    ),
                    "pass_to_fail": sum(
                        before and (not after)
                        for before, after in zip(lower, upper, strict=True)
                    ),
                }
                transition_rows.append(transition)
                snapshot_transition_rows.append(transition)

        candidate = by_budget[str(candidate_shots)]
        regressions = sum(row["pass_to_fail"] for row in snapshot_transition_rows)
        conditions = [
            condition_row(
                "A1",
                "minimum pooled task pass rate reaches the floor",
                candidate["minimum_pooled_honest_completeness"],
                honest_floor,
                candidate["minimum_pooled_honest_completeness"] >= honest_floor,
            ),
            condition_row(
                "A2",
                "minimum pooled Wilson lower reaches the floor",
                candidate["minimum_pooled_wilson_lower"],
                honest_floor,
                candidate["minimum_pooled_wilson_lower"] >= honest_floor,
            ),
            condition_row(
                "A3",
                "minimum leave-one-block-out Wilson lower reaches the floor",
                candidate["minimum_leave_one_block_out_wilson_lower"],
                honest_floor,
                candidate["minimum_leave_one_block_out_wilson_lower"]
                >= honest_floor,
            ),
            condition_row(
                "A4",
                "every block reaches the point floor",
                candidate["blocks_meeting_point_floor"],
                len(block_seeds),
                candidate["blocks_meeting_point_floor"] == len(block_seeds),
            ),
            condition_row(
                "A5",
                "paired pass-to-fail transitions stay within the ceiling",
                regressions,
                maximum_regressions,
                regressions <= maximum_regressions,
            ),
        ]
        snapshots[snapshot_name] = {
            "role": snapshot_row["role"],
            "backend_name": snapshot_row["backend_name"],
            "canonical_snapshot_sha256": snapshot_row[
                "canonical_snapshot_sha256"
            ],
            "by_shot_budget": by_budget,
            "pass_to_fail_transition_count": regressions,
            "fail_to_pass_transition_count": sum(
                row["fail_to_pass"] for row in snapshot_transition_rows
            ),
            "acceptance_conditions": conditions,
            "snapshot_accepted": all(row["passed"] for row in conditions),
        }

    global_acceptance = all(row["snapshot_accepted"] for row in snapshots.values())
    evidence = contract["evidence_classification"]
    summary = {
        "task_count": len(tasks),
        "snapshot_count": len(snapshot_contract),
        "snapshot_names": [row["backend_class"] for row in snapshot_contract],
        "seed_block_count": len(block_seeds),
        "block_seeds": block_seeds,
        "trials_per_block_snapshot_task": trials_per_block,
        "trials_per_snapshot_task": len(block_seeds) * trials_per_block,
        "shot_budgets": shot_budgets,
        "control_shot_budget": control_shots,
        "candidate_shot_budget": candidate_shots,
        "compiled_basis_circuit_count": compiled_circuit_count,
        "tolerance": tolerance,
        "honest_floor": honest_floor,
        "snapshots": snapshots,
        "global_acceptance": global_acceptance,
        "accepted_snapshot_count": sum(
            row["snapshot_accepted"] for row in snapshots.values()
        ),
        "fail_to_pass_transition_count": sum(
            row["fail_to_pass"] for row in transition_rows
        ),
        "pass_to_fail_transition_count": sum(
            row["pass_to_fail"] for row in transition_rows
        ),
        "measurement_maps_preserved": measurement_maps_preserved,
        "preregistered_before_execution": preregistered_at < started_at,
        "historical_real_system_snapshot_properties_used": evidence[
            "historical_real_system_snapshot_properties_used"
        ],
        "current_backend_calibration_used": False,
        "backend_refresh_performed": False,
        "provider_session_used": False,
        "hardware_execution_performed": False,
        "independent_backend_transcript_used": False,
        "real_backend_transcript_rows": 0,
        "protocol_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    expected_trials = (
        len(snapshot_contract) * len(block_seeds) * len(tasks) * trials_per_block
    )
    circuit_files = sorted(set(circuit_files))
    requirements = [
        {
            "requirement_id": "P1",
            "label": "contract matches the publicly posted SHA-256",
            "passed": observed_contract_hash == CONTRACT_SHA256,
            "evidence": {"contract_sha256": observed_contract_hash},
        },
        {
            "requirement_id": "P2",
            "label": "public preregistration predates snapshot replay",
            "passed": preregistered_at < started_at,
            "evidence": {
                "discussion": PREREGISTRATION_DISCUSSION,
                "created_at": PREREGISTRATION_CREATED_AT,
            },
        },
        {
            "requirement_id": "P3",
            "label": "contract binds the accepted R124 payload",
            "passed": r124["payload_hash"] == contract["source_payload_hash"],
            "evidence": {"r124_payload_hash": r124["payload_hash"]},
        },
        {
            "requirement_id": "P4",
            "label": "Qiskit IBM Runtime version matches the software contract",
            "passed": qiskit_ibm_runtime.__version__
            == contract["software_contract"]["qiskit_ibm_runtime_version"],
            "evidence": {
                "qiskit": qiskit.__version__,
                "qiskit_aer": qiskit_aer.__version__,
                "qiskit_ibm_runtime": qiskit_ibm_runtime.__version__,
            },
        },
        {
            "requirement_id": "P5",
            "label": "all frozen snapshot hashes match the preregistration",
            "passed": all(
                snapshot_metadata[row["backend_class"]]["sha256"]
                == row["canonical_snapshot_sha256"]
                for row in snapshot_contract
            ),
            "evidence": {
                row["backend_class"]: snapshot_metadata[row["backend_class"]][
                    "sha256"
                ]
                for row in snapshot_contract
            },
        },
        {
            "requirement_id": "P6",
            "label": "R125 root seeds are disjoint from R123 and R124",
            "passed": set(block_seeds).isdisjoint(
                r124["summary"]["block_seeds"]
            ),
            "evidence": {"r125_seeds": block_seeds},
        },
        {
            "requirement_id": "P7",
            "label": "all compiled circuits preserve logical classical-bit order",
            "passed": all(measurement_maps_preserved.values()),
            "evidence": measurement_maps_preserved,
        },
        {
            "requirement_id": "P8",
            "label": "all trial rows are transpiled and preserve paired evidence",
            "passed": len(trial_rows) == expected_trials
            and all(
                row["transpiled_to_snapshot_target"]
                and row["budgets_share_schedule_prefix"]
                and row["budgets_share_bundle"]
                for row in trial_rows
            ),
            "evidence": {
                "trial_row_count": len(trial_rows),
                "expected_trial_row_count": expected_trials,
            },
        },
        {
            "requirement_id": "P9",
            "label": "all holdout schedules have unique hashes",
            "passed": len({row["schedule_sha256"] for row in trial_rows})
            == len(trial_rows),
            "evidence": {
                "unique_schedule_hash_count": len(
                    {row["schedule_sha256"] for row in trial_rows}
                )
            },
        },
        {
            "requirement_id": "P10",
            "label": "block, leave-one-out, and transition ledgers are complete",
            "passed": len(block_rows)
            == len(snapshot_contract) * len(block_seeds) * len(shot_budgets)
            and len(transition_rows)
            == len(snapshot_contract) * len(block_seeds) * len(tasks),
            "evidence": {
                "block_row_count": len(block_rows),
                "transition_row_count": len(transition_rows),
            },
        },
        {
            "requirement_id": "P11",
            "label": "all five preregistered conditions are evaluated per snapshot",
            "passed": all(
                len(row["acceptance_conditions"]) == 5 for row in snapshots.values()
            ),
            "evidence": {"snapshot_count": len(snapshots)},
        },
        {
            "requirement_id": "P12",
            "label": "historical snapshots are not mislabeled as current or hardware evidence",
            "passed": summary["historical_real_system_snapshot_properties_used"]
            and not summary["current_backend_calibration_used"]
            and not summary["backend_refresh_performed"]
            and not summary["provider_session_used"]
            and not summary["hardware_execution_performed"]
            and not summary["independent_backend_transcript_used"]
            and summary["real_backend_transcript_rows"] == 0,
            "evidence": {"evidence_class": "frozen_historical_snapshot_local_aer"},
        },
        {
            "requirement_id": "P13",
            "label": "no soundness, advantage, BQP, or new-credit claim is promoted",
            "passed": not summary["protocol_soundness_claimed"]
            and not summary["quantum_advantage_claimed"]
            and not summary["bqp_separation_claimed"]
            and summary["new_credit_delta"] == 0,
            "evidence": {"new_credit_delta": 0},
        },
    ]
    failed = [row["requirement_id"] for row in requirements if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R125 historical QPU snapshot replay",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "execution_started_at_unix": started_at,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "contract": {
            "path": CONTRACT_PATH,
            "sha256": observed_contract_hash,
            "discussion": PREREGISTRATION_DISCUSSION,
            "discussion_created_at": PREREGISTRATION_CREATED_AT,
        },
        "requirements": requirements,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "summary": summary,
        "snapshot_metadata": snapshot_metadata,
        "trial_rows": trial_rows,
        "block_rows": block_rows,
        "transition_rows": transition_rows,
        "artifacts": {
            "circuits": circuit_files,
            "snapshots": snapshot_files,
            "contract": CONTRACT_PATH,
            "r124_result": R124_RESULT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": (
                "A preregistered local Aer replay driven by frozen historical "
                "IBM QPU snapshot properties."
            ),
            "what_is_not_supported": contract["claim_boundary"]["not_supported"],
            "next_gate": (
                contract["decision_policy"]["accepted"]
                if global_acceptance
                else contract["decision_policy"]["rejected"]
            ),
        },
    }
    payload["payload_hash"] = stable_hash(payload)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    print(json.dumps(run_gate(Path(args.repo_root)), sort_keys=True))


if __name__ == "__main__":
    main()
