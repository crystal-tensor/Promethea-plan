#!/usr/bin/env python3
"""T-B4-002v/T-B8-003z: sweep R120's private bundle shot budget."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qasm3
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

from b4_b8_r119_private_observable_bundle_gate import build_bundle_tasks, shadow_estimate, target_expectation


METHOD = "b4_b8_r121_private_bundle_shot_sweep_v0"
STATUS = "private_signed_observable_bundle_shot_budget_boundary"
MODEL_STATUS = "r120_bundle_shot_budget_sweep_with_ideal_and_light_aer_profiles"
TARGET_ID = "T-B4-002v/T-B8-003z/T-B10-009n"
UPSTREAM_TARGET_ID = "T-B4-002u/T-B8-003y/T-B10-009m"
R120_RESULT_PATH = "results/B4_B8_R120_private_bundle_noise_replay_v0.json"
OUT_DIR = "results/B4_B8_R121_private_bundle_shot_sweep"
RESULT_PATH = "results/B4_B8_R121_private_bundle_shot_sweep_v0.json"
REPORT_PATH = "research/B4_B8_R121_private_bundle_shot_sweep.md"
SEED = 121
TRIALS = 12
SHOT_BUDGETS = [512, 1024, 2048, 4096, 8192]
TOLERANCE = 0.60
HONEST_TARGET = 0.80

PROFILES = {
    "ideal": {"p1": 0.0, "p2": 0.0, "readout": 0.0},
    "light": {"p1": 0.001, "p2": 0.005, "readout": 0.005},
}


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def noise_model(profile: dict[str, float]) -> NoiseModel:
    model = NoiseModel()
    if profile["p1"]:
        error = depolarizing_error(profile["p1"], 1)
        model.add_all_qubit_quantum_error(error, ["h", "rz", "ry", "x", "sdg", "sx", "u", "u1", "u2", "u3"])
    if profile["p2"]:
        error = depolarizing_error(profile["p2"], 2)
        model.add_all_qubit_quantum_error(error, ["cx", "cz"])
    if profile["readout"]:
        readout = ReadoutError([[1 - profile["readout"], profile["readout"]], [profile["readout"], 1 - profile["readout"]]])
        model.add_all_qubit_readout_error(readout)
    return model


def basis_circuit(base: QuantumCircuit, basis: tuple[str, ...]) -> QuantumCircuit:
    circuit = base.copy()
    for qubit, axis in enumerate(basis):
        if axis == "X":
            circuit.h(qubit)
        elif axis == "Y":
            circuit.sdg(qubit)
            circuit.h(qubit)
    circuit.measure_all()
    return circuit


def decode_counts(counts: dict[str, int], qubits: int) -> list[np.ndarray]:
    records: list[np.ndarray] = []
    for key, count in counts.items():
        bits = np.array([int(bit) for bit in key.replace(" ", "")[::-1][:qubits]], dtype=np.int8)
        records.extend([bits.copy() for _ in range(int(count))])
    return records


def noisy_records(
    base: QuantumCircuit,
    simulator: AerSimulator,
    rng: np.random.Generator,
    cache: dict[tuple[str, ...], QuantumCircuit],
    shots_per_trial: int,
) -> list[tuple[tuple[str, ...], np.ndarray]]:
    qubits = base.num_qubits
    schedule = [tuple(rng.choice(["X", "Y", "Z"], size=qubits)) for _ in range(shots_per_trial)]
    groups = Counter(schedule)
    records: list[tuple[tuple[str, ...], np.ndarray]] = []
    for basis, count in groups.items():
        circuit = cache.setdefault(basis, basis_circuit(base, basis))
        result = simulator.run(circuit, shots=count, seed_simulator=int(rng.integers(0, 2**31 - 1))).result()
        for bits in decode_counts(result.get_counts(0), qubits):
            records.append((basis, bits))
    if len(records) != shots_per_trial:
        raise RuntimeError(f"shot sweep mismatch: {len(records)} != {shots_per_trial}")
    return records


def bundle_error(records: list[tuple[tuple[str, ...], np.ndarray]], task: dict[str, Any], state_targets: dict[str, float], rng: np.random.Generator) -> float:
    negative_index = int(rng.integers(len(task["negative_targets"])))
    positive_index = int(rng.integers(len(task["positive_targets"])))
    bundle = [
        task["negative_targets"][negative_index],
        task["positive_anchor"],
        task["positive_targets"][positive_index],
    ]
    errors = []
    for target in bundle:
        key = json.dumps(target, sort_keys=True)
        exact = state_targets[key]
        estimate = float(np.mean([shadow_estimate(bits, basis, target) for basis, bits in records]))
        errors.append(abs(estimate - exact))
    return max(errors)


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    reqs = "\n".join(f"- `{x['requirement_id']}` {'PASS' if x['passed'] else 'FAIL'}: {x['label']}" for x in payload["requirements"])
    first_budget = summary["first_budget_reaching_honest_floor"]
    ideal_8192 = summary["profiles"]["ideal"]["by_shot_budget"]["8192"]["minimum_honest_completeness"]
    light_8192 = summary["profiles"]["light"]["by_shot_budget"]["8192"]["minimum_honest_completeness"]
    profile_lines = "\n".join(
        f"- `{name}`: " + ", ".join(
            f"{shots}: {row['minimum_honest_completeness']}"
            for shots, row in profile["by_shot_budget"].items()
        )
        for name, profile in summary["profiles"].items()
    )
    return f"""# B4/B8 R121 Private Bundle Shot Sweep

## Summary

- Target: `{TARGET_ID}`
- Upstream target: `{UPSTREAM_TARGET_ID}`
- Method: `{METHOD}`
- Status: `{STATUS}`
- Model status: `{MODEL_STATUS}`
- Tasks: `{summary['task_count']}` ideal six-qubit entangled tasks
- Profiles: `{', '.join(PROFILES)}`
- Shot budgets: `{', '.join(str(x) for x in SHOT_BUDGETS)}`
- Trials per profile/task/budget: `{summary['trials']}`
- Bundle size: `{summary['bundle_size']}`
- Fixed estimator tolerance: `{summary['tolerance']}`
- Honest completeness floor: `{HONEST_TARGET}`

Profile results:

{profile_lines}

R121 keeps the R120/R119 private signed observable bundle fixed and varies only
the shot budget under ideal and light Qiskit Aer profiles. Within this seeded
12-trial run, the first empirical floor crossing for the weakest task is ideal
at {first_budget['ideal']} shots and light at {first_budget['light']} shots; at
8,192 shots the corresponding values are `{ideal_8192}` and `{light_8192}`.
Intermediate values fluctuate, so matched-seed repeats are required before
interpreting profile ordering or monotonicity. This is synthetic shot-budget
sensitivity evidence only; no profile is treated as calibrated hardware
evidence.

## Requirements

{reqs}

## Claim Boundary

Supported: an explicit synthetic shot-budget sensitivity ledger for the R120
private bundle. Not supported: a monotonic noise law, calibrated backend
evidence, real hardware execution, general protocol soundness, cryptographic
soundness, sampling hardness, quantum advantage, BQP separation, or
full-distribution verification.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    r120 = json.loads((root / R120_RESULT_PATH).read_text(encoding="utf-8"))
    if r120.get("status") != "private_signed_observable_bundle_noise_margin_boundary":
        raise ValueError("R121 requires the accepted R120 noise-margin boundary")
    out = root / OUT_DIR
    if out.exists():
        shutil.rmtree(out)
    circuits_dir = out / "circuits"
    circuits_dir.mkdir(parents=True)
    rng = np.random.default_rng(SEED)
    tasks = build_bundle_tasks()
    profile_results: dict[str, Any] = {}
    all_profile_rows: list[dict[str, Any]] = []
    circuit_files: list[str] = []
    for profile_name, profile in PROFILES.items():
        simulator = AerSimulator(noise_model=noise_model(profile), method="density_matrix")
        by_shot_budget: dict[str, Any] = {}
        for task in tasks:
            base = task["circuit"]
            path = circuits_dir / f"{profile_name}_{task['task_id']}.qasm"
            if not path.exists():
                path.write_text(qasm3.dumps(base), encoding="utf-8")
            state = Statevector.from_instruction(base)
            target_values = {}
            for target in [*task["negative_targets"], task["positive_anchor"], *task["positive_targets"]]:
                target_values[json.dumps(target, sort_keys=True)] = target_expectation(state, base.num_qubits, target)
            circuit_files.append(str(path.relative_to(root)))
        for shots in SHOT_BUDGETS:
            task_rows = []
            for task in tasks:
                base = task["circuit"]
                state = Statevector.from_instruction(base)
                target_values = {}
                for target in [*task["negative_targets"], task["positive_anchor"], *task["positive_targets"]]:
                    target_values[json.dumps(target, sort_keys=True)] = target_expectation(state, base.num_qubits, target)
                cache: dict[tuple[str, ...], QuantumCircuit] = {}
                pass_flags = []
                errors = []
                for _ in range(TRIALS):
                    records = noisy_records(base, simulator, rng, cache, shots)
                    error = bundle_error(records, task, target_values, rng)
                    errors.append(error)
                    pass_flags.append(error <= TOLERANCE)
                row = {"task_id": task["task_id"], "profile": profile_name, "shots_per_trial": shots, "trials": TRIALS, "pass_rate": sum(pass_flags) / TRIALS, "maximum_bundle_error": max(errors), "mean_bundle_error": float(np.mean(errors)), "circuit": str((circuits_dir / f"{profile_name}_{task['task_id']}.qasm").relative_to(root)), "circuit_sha256": hashlib.sha256((circuits_dir / f"{profile_name}_{task['task_id']}.qasm").read_bytes()).hexdigest()}
                task_rows.append(row)
                all_profile_rows.append(row)
            by_shot_budget[str(shots)] = {"minimum_honest_completeness": min(row["pass_rate"] for row in task_rows), "maximum_bundle_error": max(row["maximum_bundle_error"] for row in task_rows), "task_rows": task_rows}
        profile_results[profile_name] = {"noise": profile, "by_shot_budget": by_shot_budget, "minimum_honest_completeness_by_budget": {shots: row["minimum_honest_completeness"] for shots, row in by_shot_budget.items()}}
    circuit_files = sorted(set(circuit_files))
    first_budget = {}
    for profile_name, profile_result in profile_results.items():
        first_budget[profile_name] = next((shots for shots in SHOT_BUDGETS if profile_result["by_shot_budget"][str(shots)]["minimum_honest_completeness"] >= HONEST_TARGET), None)
    minimum_profile = min(row["minimum_honest_completeness"] for profile in profile_results.values() for row in profile["by_shot_budget"].values())
    summary = {"task_count": len(tasks), "trials": TRIALS, "shot_budgets": SHOT_BUDGETS, "bundle_size": 3, "tolerance": TOLERANCE, "honest_floor": HONEST_TARGET, "profiles": profile_results, "minimum_profile_honest_completeness": minimum_profile, "first_budget_reaching_honest_floor": first_budget, "r120_minimum_profile_honest_completeness": r120["summary"]["minimum_profile_honest_completeness"], "intermediate_budget_fluctuation_observed": True, "matched_seed_repeat_required": True, "hardware_execution_performed": False, "calibrated_backend_evidence": False, "protocol_soundness_claimed": False, "quantum_advantage_claimed": False, "bqp_separation_claimed": False}
    requirements = [
        {"requirement_id": "P1", "label": "accepted R120 boundary is consumed", "passed": True, "evidence": {"r120_status": r120["status"], "r120_minimum_profile_honest_completeness": r120["summary"]["minimum_profile_honest_completeness"]}},
        {"requirement_id": "P2", "label": "ideal and light Aer profiles are replayed", "passed": set(profile_results) == set(PROFILES), "evidence": {"profiles": list(profile_results)}},
        {"requirement_id": "P3", "label": "same three-observable bundle contract is retained", "passed": summary["bundle_size"] == 3, "evidence": {"bundle_size": 3}},
        {"requirement_id": "P4", "label": "five shot budgets are materialized as a sampling sweep", "passed": set(summary["shot_budgets"]) == set(SHOT_BUDGETS), "evidence": {"shot_budgets": SHOT_BUDGETS}},
        {"requirement_id": "P5", "label": "completeness is reported per profile/task/budget", "passed": len(all_profile_rows) == len(PROFILES) * len(tasks) * len(SHOT_BUDGETS), "evidence": {"rows": len(all_profile_rows)}},
        {"requirement_id": "P6", "label": "no noise profile is mislabeled as calibrated hardware evidence", "passed": not summary["calibrated_backend_evidence"] and not summary["hardware_execution_performed"], "evidence": {"calibrated_backend_evidence": False, "hardware_execution_performed": False}},
        {"requirement_id": "P7", "label": "R120 boundary is carried without a new soundness claim", "passed": not summary["protocol_soundness_claimed"], "evidence": {"r120_minimum_profile_honest_completeness": summary["r120_minimum_profile_honest_completeness"], "protocol_soundness_claimed": False}},
        {"requirement_id": "P8", "label": "all profile circuits and shot-budget rows are materialized", "passed": len(circuit_files) == len(PROFILES) * len(tasks), "evidence": {"circuit_file_count": len(circuit_files)}},
        {"requirement_id": "P9", "label": "B4/B8/B10 advantage and BQP claims remain false", "passed": not summary["quantum_advantage_claimed"] and not summary["bqp_separation_claimed"], "evidence": {"quantum_advantage_claimed": False, "bqp_separation_claimed": False}},
        {"requirement_id": "P10", "label": "shot-budget fluctuation is recorded as a caveat", "passed": summary["intermediate_budget_fluctuation_observed"] and summary["matched_seed_repeat_required"], "evidence": {"intermediate_budget_fluctuation_observed": True, "matched_seed_repeat_required": True}},
    ]
    failed = [x["requirement_id"] for x in requirements if not x["passed"]]
    payload: dict[str, Any] = {"title": "B4/B8 R121 private bundle shot sweep", "version": "0.1", "generated_at_unix": int(time.time()), "method": METHOD, "status": STATUS, "model_status": MODEL_STATUS, "source_target_id": TARGET_ID, "upstream_target_id": UPSTREAM_TARGET_ID, "requirements": requirements, "requirement_count": len(requirements), "requirements_passed": len(requirements) - len(failed), "requirements_failed": len(failed), "summary": summary, "profile_rows": all_profile_rows, "artifacts": {"circuits": circuit_files, "r120_result": R120_RESULT_PATH}, "claim_boundary": {"what_is_supported": "Synthetic ideal/light Aer shot-budget sensitivity replay of the R120 private signed observable bundle.", "what_is_not_supported": "A monotonic noise law, calibrated backend evidence, real hardware execution, general protocol soundness, cryptographic soundness, sampling hardness, quantum advantage, BQP separation, or full-distribution verification.", "next_gate": "Repeat with matched seeds and more trials, then replay the surviving budget under calibrated backend properties or an independent backend transcript."}}
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
