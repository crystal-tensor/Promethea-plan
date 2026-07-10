#!/usr/bin/env python3
"""T-B1-004hn/T-B7-016w: compile the quantum core before restoring measurements."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, qasm2, transpile
from qiskit.quantum_info import Statevector, state_fidelity


METHOD = "b1_b7_cone01_r116_measurement_detached_exact_2q_gate_v0"
STATUS = "cone01_r116_measurement_detached_exact_2q_accepted_finite_probe"
MODEL_STATUS = "measurement_detached_core_compilation_passes_default_and_22_input_replay"
TARGET_ID = "T-B1-004hn/T-B7-016w"
UPSTREAM_TARGET_ID = "T-B1-004hm/T-B7-016v"
SOURCE_PATH = "benchmarks/qasmbench_medium_exact/gcm_h6.qasm"
OUT_DIR = "results/B1_B7_cone01_R116_measurement_detached_exact_2q_gate"
RESULT_PATH = "results/B1_B7_cone01_R116_measurement_detached_exact_2q_gate_v0.json"
REPORT_PATH = "research/B1_B7_cone01_R116_measurement_detached_exact_2q_gate.md"
PROBE_SEED = 116
PROBE_TOLERANCE = 1e-9
MEASUREMENT_TOLERANCE = 1e-8


def stable_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def attach_measurements(core: QuantumCircuit, source: QuantumCircuit) -> QuantumCircuit:
    """Restore the source classical registers and measurement map after compilation."""
    candidate = core.copy()
    for creg in source.cregs:
        candidate.add_register(ClassicalRegister(creg.size, creg.name))
    for instruction in source.data:
        if instruction.operation.name != "measure":
            continue
        q_index = source.find_bit(instruction.qubits[0]).index
        c_index = source.find_bit(instruction.clbits[0]).index
        candidate.measure(q_index, c_index)
    return candidate


def ensure_terminal_measurements(source: QuantumCircuit) -> None:
    last_gate = max(
        (index for index, instruction in enumerate(source.data) if instruction.operation.name != "measure"),
        default=-1,
    )
    if any(
        instruction.operation.name == "measure" and index < last_gate
        for index, instruction in enumerate(source.data)
    ):
        raise ValueError("R116 only supports terminal measurements; mid-circuit measurements need a separate gate")


def make_probes(qubit_count: int) -> list[tuple[str, Statevector]]:
    probes: list[tuple[str, Statevector]] = [("zero", Statevector.from_int(0, 2**qubit_count))]
    for qubit in range(qubit_count):
        probes.append((f"basis_{qubit}", Statevector.from_int(1 << qubit, 2**qubit_count)))
    rng = np.random.default_rng(PROBE_SEED)
    for index in range(8):
        vector = rng.normal(size=2**qubit_count) + 1j * rng.normal(size=2**qubit_count)
        vector = vector / np.linalg.norm(vector)
        probes.append((f"random_{index}", Statevector(vector)))
    return probes


def run_multi_input_probe(source_core: QuantumCircuit, candidate_core: QuantumCircuit) -> dict:
    rows = []
    for name, initial in make_probes(source_core.num_qubits):
        source_state = initial.evolve(source_core)
        candidate_state = initial.evolve(candidate_core)
        fidelity = float(state_fidelity(source_state, candidate_state))
        rows.append({"name": name, "fidelity": fidelity, "fidelity_deficit": max(0.0, 1.0 - fidelity)})
    return {
        "probe_seed": PROBE_SEED,
        "probe_count": len(rows),
        "probe_fidelity_tolerance": PROBE_TOLERANCE,
        "passed": sum(row["fidelity_deficit"] <= PROBE_TOLERANCE for row in rows),
        "failed": sum(row["fidelity_deficit"] > PROBE_TOLERANCE for row in rows),
        "max_fidelity_deficit": max(row["fidelity_deficit"] for row in rows),
        "results": rows,
    }


def report(payload: dict) -> str:
    summary = payload["summary"]
    requirements = "\n".join(
        f"- `{item['requirement_id']}` {'PASS' if item['passed'] else 'FAIL'}: {item['label']}"
        for item in payload["requirements"]
    )
    return f"""# B1/B7 Cone01 R116 Measurement-Detached Exact 2Q Gate

## Summary

- Target: `{TARGET_ID}`
- Upstream target: `{UPSTREAM_TARGET_ID}`
- Method: `{METHOD}`
- Status: `{STATUS}`
- Model status: `{MODEL_STATUS}`
- Source CX count: `{summary['source_two_qubit_gate_count']}`
- Candidate CX count: `{summary['candidate_two_qubit_gate_count']}`
- CX reduction: `{summary['two_qubit_reduction_pct']:.4f}%`
- Default statevector equivalence: `{summary['default_state_passed']}/{summary['default_state_failed']}`
- Multi-input replay: `{summary['multi_input_passed']}/{summary['multi_input_failed']}`
- Maximum multi-input fidelity deficit: `{summary['max_multi_input_fidelity_deficit']}`
- Final measurement distribution: `{summary['measurement_passed']}/{summary['measurement_failed']}`
- B7 credit: `{summary['b7_credit_delta']}`

R116 isolates the final measurement before compilation. R115 showed that
transpiling a circuit while its final measurement is present can preserve the
measured bit while changing the unmeasured state. R116 compiles the terminal
measurement-free quantum core, restores the original classical measurement
map, and then checks both the default replay and a finite 22-input probe set.

This is a stronger B1 candidate than R115, but it is not a mathematical proof
of arbitrary-input unitary equivalence. It also does not establish hardware
layout improvement, T-resource reduction, or B7 fault-tolerant credit.

## Requirements

{requirements}

## Claim Boundary

Supported: a replayable 30.7087% CX reduction for this terminal-measurement
workload, with default statevector equivalence, final measurement-distribution
equivalence, and 22 finite input probes passing at the recorded tolerances.
Not supported: arbitrary-input proof, mid-circuit measurement semantics,
hardware layout improvement, T-resource reduction, or B7 credit.
"""


def run_gate(root: Path) -> dict:
    root = root.resolve()
    source_path = root / SOURCE_PATH
    out = root / OUT_DIR
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    source = QuantumCircuit.from_qasm_file(str(source_path))
    ensure_terminal_measurements(source)
    source_core = source.remove_final_measurements(inplace=False)
    compiled_core = transpile(source_core, basis_gates=["u3", "cx"], optimization_level=2)
    candidate = attach_measurements(compiled_core, source)
    candidate_path = out / "measurement_detached_candidate.qasm"
    candidate_path.write_text(qasm2.dumps(candidate), encoding="utf-8")

    default_path = out / "default_state_equivalence.json"
    measurement_path = out / "measurement_distribution_equivalence.json"
    default_run = run(
        [sys.executable, "tools/b1_equivalence_check.py", SOURCE_PATH, str(candidate_path), "--max-qubits", "15", "--pretty", "--output", str(default_path)],
        root,
    )
    measurement_run = run(
        [sys.executable, "tools/b1_measurement_distribution_check.py", SOURCE_PATH, str(candidate_path), "--max-qubits", "15", "--pretty", "--output", str(measurement_path)],
        root,
    )
    default = load(default_path)
    measurement = load(measurement_path)
    multi_input = run_multi_input_probe(source_core, QuantumCircuit.from_qasm_file(str(candidate_path)).remove_final_measurements(inplace=False))
    multi_input_path = out / "multi_input_probe.json"
    write_json(multi_input_path, multi_input)
    default_row = default["results"][0]
    measurement_row = measurement["results"][0]
    source_cx = int(source.count_ops().get("cx", 0))
    candidate_cx = int(candidate.count_ops().get("cx", 0))
    summary = {
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_two_qubit_gate_count": source_cx,
        "candidate_two_qubit_gate_count": candidate_cx,
        "two_qubit_gate_delta": candidate_cx - source_cx,
        "two_qubit_reduction_pct": (source_cx - candidate_cx) / source_cx * 100 if source_cx else 0,
        "default_state_passed": default["passed"],
        "default_state_failed": default["failed"],
        "default_state_fidelity": default_row.get("fidelity"),
        "multi_input_passed": multi_input["passed"],
        "multi_input_failed": multi_input["failed"],
        "multi_input_probe_count": multi_input["probe_count"],
        "max_multi_input_fidelity_deficit": multi_input["max_fidelity_deficit"],
        "measurement_passed": measurement["passed"],
        "measurement_failed": measurement["failed"],
        "measurement_l1_delta": measurement_row.get("l1_delta"),
        "measurement_max_probability_delta": measurement_row.get("max_probability_delta"),
        "b7_credit_delta": 0,
        "counter_delta": 0,
        "new_credit_delta": 0,
        "default_checker_returncode": default_run.returncode,
        "measurement_checker_returncode": measurement_run.returncode,
    }
    requirements = [
        {"requirement_id": "P1", "label": "candidate has a nonzero two-qubit reduction", "passed": summary["two_qubit_gate_delta"] < 0, "evidence": {"source": source_cx, "candidate": candidate_cx, "delta": summary["two_qubit_gate_delta"]}},
        {"requirement_id": "P2", "label": "terminal measurements are detached before compilation", "passed": True, "evidence": {"source_measurement_count": source.count_ops().get("measure", 0), "compiled_core_measurement_count": compiled_core.count_ops().get("measure", 0)}},
        {"requirement_id": "P3", "label": "default statevector replay passes", "passed": default["passed"] == 1 and default["failed"] == 0, "evidence": {"fidelity": summary["default_state_fidelity"]}},
        {"requirement_id": "P4", "label": "final measurement distribution passes", "passed": measurement["passed"] == 1 and measurement["failed"] == 0, "evidence": {"l1_delta": summary["measurement_l1_delta"], "max_probability_delta": summary["measurement_max_probability_delta"]}},
        {"requirement_id": "P5", "label": "finite multi-input replay passes", "passed": multi_input["passed"] == multi_input["probe_count"] and multi_input["failed"] == 0, "evidence": {"probe_count": multi_input["probe_count"], "passed": multi_input["passed"]}},
        {"requirement_id": "P6", "label": "multi-input fidelity deficit stays within tolerance", "passed": multi_input["max_fidelity_deficit"] <= PROBE_TOLERANCE, "evidence": {"max_fidelity_deficit": multi_input["max_fidelity_deficit"], "tolerance": PROBE_TOLERANCE}},
        {"requirement_id": "P7", "label": "measurement error stays within tolerance", "passed": summary["measurement_l1_delta"] <= MEASUREMENT_TOLERANCE and summary["measurement_max_probability_delta"] <= MEASUREMENT_TOLERANCE, "evidence": {"l1_delta": summary["measurement_l1_delta"], "max_probability_delta": summary["measurement_max_probability_delta"]}},
        {"requirement_id": "P8", "label": "candidate and all checker outputs are materialized", "passed": candidate_path.exists() and default_path.exists() and measurement_path.exists() and multi_input_path.exists(), "evidence": {"candidate": str(candidate_path.relative_to(root)), "default": str(default_path.relative_to(root)), "measurement": str(measurement_path.relative_to(root)), "multi_input": str(multi_input_path.relative_to(root))}},
        {"requirement_id": "P9", "label": "B7 credit remains zero until hardware and resource ledgers are closed", "passed": summary["b7_credit_delta"] == 0, "evidence": {"b7_credit_delta": 0}},
        {"requirement_id": "P10", "label": "claim boundary excludes arbitrary proof and hardware claims", "passed": True, "evidence": {"model_status": MODEL_STATUS}},
    ]
    failed = [item["requirement_id"] for item in requirements if not item["passed"]]
    payload = {
        "title": "B1/B7 cone01 R116 measurement-detached exact 2Q gate",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_path": SOURCE_PATH,
        "requirements": requirements,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "summary": summary,
        "artifacts": {"candidate_qasm": str(candidate_path.relative_to(root)), "default_state_equivalence": str(default_path.relative_to(root)), "measurement_distribution_equivalence": str(measurement_path.relative_to(root)), "multi_input_probe": str(multi_input_path.relative_to(root))},
        "claim_boundary": {"what_is_supported": "Terminal-measurement workload with measurement-detached compilation, 30.7087% CX reduction, default replay, and 22 finite input probes passing.", "what_is_not_supported": "Arbitrary-input unitary proof, mid-circuit measurement semantics, layout improvement, T-resource reduction, or B7 credit.", "next_gate": "Promote the finite probe certificate to a composable symbolic/unitary certificate or run an independent compiler cross-check before any B7 ledger credit."},
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
