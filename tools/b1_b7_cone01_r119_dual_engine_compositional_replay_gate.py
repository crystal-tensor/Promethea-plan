#!/usr/bin/env python3
"""T-B1-004hq/T-B7-016z: cross-check R116 with two engines and replay composition."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import time
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

import b1_b7_cone01_r117_independent_numpy_replay_gate as numpy_engine


METHOD = "b1_b7_cone01_r119_dual_engine_compositional_replay_gate_v0"
STATUS = "cone01_r119_dual_engine_composition_accepted_finite_evidence"
MODEL_STATUS = "qiskit_numpy_cross_engine_and_prefix_suffix_composition_agree"
TARGET_ID = "T-B1-004hq/T-B7-016z"
UPSTREAM_TARGET_ID = "T-B1-004hp/T-B7-016y"
SOURCE_PATH = "benchmarks/qasmbench_medium_exact/gcm_h6.qasm"
CANDIDATE_PATH = "results/B1_B7_cone01_R116_measurement_detached_exact_2q_gate/measurement_detached_candidate.qasm"
R116_RESULT_PATH = "results/B1_B7_cone01_R116_measurement_detached_exact_2q_gate_v0.json"
R118_RESULT_PATH = "results/B1_B7_cone01_R118_randomized_channel_fingerprint_gate_v0.json"
OUT_DIR = "results/B1_B7_cone01_R119_dual_engine_compositional_replay_gate"
RESULT_PATH = "results/B1_B7_cone01_R119_dual_engine_compositional_replay_gate_v0.json"
REPORT_PATH = "research/B1_B7_cone01_R119_dual_engine_compositional_replay_gate.md"
PROBE_SEED = 119
PROBE_TOLERANCE = 1e-9
COMPOSITION_TOLERANCE = 1e-9
MEASUREMENT_RE = re.compile(r"^\s*measure\s+.+?\s*->\s*.+;\s*$")


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def measurement_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if MEASUREMENT_RE.match(line)]


def make_probes(qubit_count: int) -> list[tuple[str, np.ndarray]]:
    dimension = 1 << qubit_count
    probes: list[tuple[str, np.ndarray]] = []
    zero = np.zeros(dimension, dtype=np.complex128)
    zero[0] = 1.0
    probes.append(("zero", zero))
    for qubit in (0, qubit_count // 2, qubit_count - 1):
        basis = np.zeros(dimension, dtype=np.complex128)
        basis[1 << qubit] = 1.0
        probes.append((f"basis_{qubit}", basis))
    rng = np.random.default_rng(PROBE_SEED)
    for index in range(8):
        state = rng.normal(size=dimension) + 1j * rng.normal(size=dimension)
        probes.append((f"haar_{index}", state / np.linalg.norm(state)))
    for index in range(8):
        state = rng.normal(size=dimension) + 1j * rng.normal(size=dimension)
        state[0] += 2.0
        probes.append((f"biased_{index}", state / np.linalg.norm(state)))
    for index in range(4):
        state = np.zeros(dimension, dtype=np.complex128)
        state[0] = 1.0 / math.sqrt(2.0)
        state[dimension - 1] = np.exp(1j * rng.uniform(-math.pi, math.pi)) / math.sqrt(2.0)
        probes.append((f"endpoint_entangled_{index}", state))
    return probes


def qiskit_core(path: Path) -> QuantumCircuit:
    circuit = QuantumCircuit.from_qasm_file(str(path))
    return circuit.remove_final_measurements(inplace=False)


def qiskit_state(circuit: QuantumCircuit, initial: np.ndarray) -> np.ndarray:
    return np.asarray(Statevector(initial).evolve(circuit).data, dtype=np.complex128)


def fidelity(left: np.ndarray, right: np.ndarray) -> float:
    return numpy_engine.fidelity(left, right)


def write_slice(path: Path, template: Path, operations: list[dict]) -> None:
    header: list[str] = []
    for line in template.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith(("OPENQASM", "include", "qreg", "creg")):
            header.append(stripped)
    path.write_text("\n".join(header + [operation["raw"] for operation in operations]) + "\n", encoding="utf-8")


def composition_rows(root: Path, circuit_name: str, circuit_path: Path, probes: list[tuple[str, np.ndarray]], out: Path) -> list[dict]:
    qregs, operations = numpy_engine.parse_qasm(circuit_path)
    gate_operations = [operation for operation in operations if operation["gate"] != "measure"]
    qiskit_full = qiskit_core(circuit_path)
    rows: list[dict] = []
    for split_fraction in (1 / 3, 1 / 2, 2 / 3):
        split = max(1, min(len(gate_operations) - 1, round(len(gate_operations) * split_fraction)))
        prefix_path = out / f"{circuit_name}_prefix_{split}.qasm"
        suffix_path = out / f"{circuit_name}_suffix_{split}.qasm"
        write_slice(prefix_path, circuit_path, gate_operations[:split])
        write_slice(suffix_path, circuit_path, gate_operations[split:])
        qiskit_prefix = qiskit_core(prefix_path)
        qiskit_suffix = qiskit_core(suffix_path)
        for name, initial in probes[:8]:
            numpy_full, _, _ = numpy_engine.simulate(circuit_path, initial)
            numpy_prefix, _, _ = numpy_engine.simulate(prefix_path, initial)
            numpy_composed, _, _ = numpy_engine.simulate(suffix_path, numpy_prefix)
            qiskit_full_state = qiskit_state(qiskit_full, initial)
            qiskit_prefix_state = qiskit_state(qiskit_prefix, initial)
            qiskit_composed = qiskit_state(qiskit_suffix, qiskit_prefix_state)
            rows.append(
                {
                    "circuit": circuit_name,
                    "probe": name,
                    "split_gate_index": split,
                    "gate_count": len(gate_operations),
                    "numpy_composition_fidelity": fidelity(numpy_full, numpy_composed),
                    "qiskit_composition_fidelity": fidelity(qiskit_full_state, qiskit_composed),
                    "numpy_qiskit_full_fidelity": fidelity(numpy_full, qiskit_full_state),
                    "numpy_qiskit_composed_fidelity": fidelity(numpy_composed, qiskit_composed),
                }
            )
    return rows


def report(payload: dict) -> str:
    summary = payload["summary"]
    requirements = "\n".join(
        f"- `{item['requirement_id']}` {'PASS' if item['passed'] else 'FAIL'}: {item['label']}"
        for item in payload["requirements"]
    )
    return f"""# B1/B7 Cone01 R119 Dual-Engine Compositional Replay Gate

## Summary

- Target: `{TARGET_ID}`
- Upstream target: `{UPSTREAM_TARGET_ID}`
- Method: `{METHOD}`
- Status: `{STATUS}`
- Full probes: `{summary['full_probe_passed']}/{summary['full_probe_count']}`
- Composition rows: `{summary['composition_passed']}/{summary['composition_count']}`
- Maximum cross-engine fidelity deficit: `{summary['max_cross_engine_fidelity_deficit']}`
- Maximum prefix/suffix composition deficit: `{summary['max_composition_fidelity_deficit']}`
- Source/Candidate CX: `{summary['source_two_qubit_gate_count']} -> {summary['candidate_two_qubit_gate_count']}`
- B7 credit: `{summary['b7_credit_delta']}`

R119 subjects the R116 candidate to two independent replay semantics. The
Qiskit Statevector engine and the repository's NumPy gate engine receive the
same 24 structured inputs. Each source and candidate circuit is also split at
three gate frontiers; prefix output is fed into the suffix and compared with
the unsplit replay in both engines. An inserted-X candidate is retained as a
negative control.

The composition check validates replay structure and cross-engine agreement;
it does not turn finite probes into an exact arbitrary-input theorem. The
candidate still has no hardware, T-resource, or B7 ledger credit.

## Requirements

{requirements}

## Claim Boundary

Supported: dual-engine finite replay and prefix/suffix composition agree for
the R116 source/candidate pair, while the negative control is detected. Not
supported: formal arbitrary-input unitary equality, mid-circuit measurement
semantics, hardware layout improvement, T-resource reduction, or B7 credit.
"""


def run_gate(root: Path) -> dict:
    root = root.resolve()
    source = root / SOURCE_PATH
    candidate = root / CANDIDATE_PATH
    r116 = json.loads((root / R116_RESULT_PATH).read_text(encoding="utf-8"))
    r118 = json.loads((root / R118_RESULT_PATH).read_text(encoding="utf-8"))
    if r116.get("status") != "cone01_r116_measurement_detached_exact_2q_accepted_finite_probe":
        raise ValueError("R119 requires the accepted R116 result")
    if r118.get("status") != "cone01_r118_randomized_channel_fingerprint_160_probe_accepted":
        raise ValueError("R119 requires the accepted R118 result")
    out = root / OUT_DIR
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    source_qregs, source_ops = numpy_engine.parse_qasm(source)
    candidate_qregs, candidate_ops = numpy_engine.parse_qasm(candidate)
    qubit_count = sum(source_qregs.values())
    if sum(candidate_qregs.values()) != qubit_count:
        raise ValueError("source and candidate qubit counts differ")
    probes = make_probes(qubit_count)
    source_core = qiskit_core(source)
    candidate_core = qiskit_core(candidate)
    full_rows: list[dict] = []
    for name, initial in probes:
        numpy_source, _, _ = numpy_engine.simulate(source, initial)
        numpy_candidate, _, _ = numpy_engine.simulate(candidate, initial)
        qiskit_source = qiskit_state(source_core, initial)
        qiskit_candidate = qiskit_state(candidate_core, initial)
        full_rows.append(
            {
                "name": name,
                "numpy_source_candidate_fidelity": fidelity(numpy_source, numpy_candidate),
                "qiskit_source_candidate_fidelity": fidelity(qiskit_source, qiskit_candidate),
                "numpy_qiskit_source_fidelity": fidelity(numpy_source, qiskit_source),
                "numpy_qiskit_candidate_fidelity": fidelity(numpy_candidate, qiskit_candidate),
            }
        )
    full_path = out / "dual_engine_full_replay.json"
    write_json(full_path, {"seed": PROBE_SEED, "probe_count": len(full_rows), "rows": full_rows})
    rows = composition_rows(root, "source", source, probes, out) + composition_rows(root, "candidate", candidate, probes, out)
    composition_path = out / "prefix_suffix_composition.json"
    write_json(composition_path, {"split_fractions": [1 / 3, 1 / 2, 2 / 3], "rows": rows})

    negative_path = out / "negative_control_candidate.qasm"
    negative_text = candidate.read_text(encoding="utf-8").replace("measure q[0] -> c[0];", "x q[0];\nmeasure q[0] -> c[0];", 1)
    negative_path.write_text(negative_text, encoding="utf-8")
    negative_rows = []
    for name, initial in probes[:8]:
        source_state, _, _ = numpy_engine.simulate(source, initial)
        negative_state, _, _ = numpy_engine.simulate(negative_path, initial)
        negative_rows.append({"name": name, "fidelity": fidelity(source_state, negative_state)})
    negative_path_json = out / "negative_control.json"
    write_json(negative_path_json, {"probe_count": len(negative_rows), "rows": negative_rows})

    source_cx = sum(operation["gate"] == "cx" for operation in source_ops)
    candidate_cx = sum(operation["gate"] == "cx" for operation in candidate_ops)
    full_probe_count = len(full_rows)
    full_probe_passed = sum(
        row["numpy_source_candidate_fidelity"] >= 1 - PROBE_TOLERANCE
        and row["qiskit_source_candidate_fidelity"] >= 1 - PROBE_TOLERANCE
        and row["numpy_qiskit_source_fidelity"] >= 1 - PROBE_TOLERANCE
        and row["numpy_qiskit_candidate_fidelity"] >= 1 - PROBE_TOLERANCE
        for row in full_rows
    )
    composition_passed = sum(
        row["numpy_composition_fidelity"] >= 1 - COMPOSITION_TOLERANCE
        and row["qiskit_composition_fidelity"] >= 1 - COMPOSITION_TOLERANCE
        and row["numpy_qiskit_full_fidelity"] >= 1 - COMPOSITION_TOLERANCE
        and row["numpy_qiskit_composed_fidelity"] >= 1 - COMPOSITION_TOLERANCE
        for row in rows
    )
    max_cross_deficit = max(
        max(1 - row[key] for row in full_rows)
        for key in ("numpy_qiskit_source_fidelity", "numpy_qiskit_candidate_fidelity")
    )
    max_composition_deficit = max(
        max(1 - row[key] for row in rows)
        for key in ("numpy_composition_fidelity", "qiskit_composition_fidelity", "numpy_qiskit_full_fidelity", "numpy_qiskit_composed_fidelity")
    )
    negative_failed = sum(row["fidelity"] < 1 - PROBE_TOLERANCE for row in negative_rows)
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
        "full_probe_count": full_probe_count,
        "full_probe_passed": full_probe_passed,
        "full_probe_failed": full_probe_count - full_probe_passed,
        "composition_count": len(rows),
        "composition_passed": composition_passed,
        "composition_failed": len(rows) - composition_passed,
        "max_cross_engine_fidelity_deficit": max_cross_deficit,
        "max_composition_fidelity_deficit": max_composition_deficit,
        "negative_control_count": len(negative_rows),
        "negative_control_failed": negative_failed,
        "measurement_map_preserved": measurement_lines(source) == measurement_lines(candidate) and bool(measurement_lines(source)),
        "b7_credit_delta": 0,
        "counter_delta": 0,
        "new_credit_delta": 0,
    }
    requirements = [
        {"requirement_id": "P1", "label": "accepted R116 and R118 artifacts are consumed", "passed": True, "evidence": {"r116": r116["status"], "r118": r118["status"]}},
        {"requirement_id": "P2", "label": "same 24 probes are replayed by NumPy and Qiskit", "passed": full_probe_count == 24, "evidence": {"count": full_probe_count, "seed": PROBE_SEED}},
        {"requirement_id": "P3", "label": "source/candidate semantics agree in both engines", "passed": full_probe_passed == full_probe_count, "evidence": {"passed": full_probe_passed, "failed": summary["full_probe_failed"]}},
        {"requirement_id": "P4", "label": "NumPy and Qiskit agree on full replay outputs", "passed": max_cross_deficit <= PROBE_TOLERANCE, "evidence": {"max_deficit": max_cross_deficit, "tolerance": PROBE_TOLERANCE}},
        {"requirement_id": "P5", "label": "prefix/suffix composition agrees at three frontiers", "passed": composition_passed == len(rows), "evidence": {"passed": composition_passed, "count": len(rows)}},
        {"requirement_id": "P6", "label": "composition and cross-engine deficits stay within tolerance", "passed": max_composition_deficit <= COMPOSITION_TOLERANCE, "evidence": {"max_deficit": max_composition_deficit, "tolerance": COMPOSITION_TOLERANCE}},
        {"requirement_id": "P7", "label": "inserted-X negative control is detected", "passed": negative_failed == len(negative_rows), "evidence": {"failed": negative_failed, "count": len(negative_rows)}},
        {"requirement_id": "P8", "label": "source measurement map and CX reduction are preserved", "passed": summary["measurement_map_preserved"] and summary["two_qubit_gate_delta"] < 0, "evidence": {"measurement_map_preserved": summary["measurement_map_preserved"], "cx": [source_cx, candidate_cx]}},
        {"requirement_id": "P9", "label": "replay and composition artifacts are materialized", "passed": full_path.exists() and composition_path.exists() and negative_path_json.exists(), "evidence": {"full": str(full_path.relative_to(root)), "composition": str(composition_path.relative_to(root)), "negative": str(negative_path_json.relative_to(root))}},
        {"requirement_id": "P10", "label": "formal arbitrary-input, hardware, and B7 claims remain excluded", "passed": summary["b7_credit_delta"] == 0, "evidence": {"b7_credit_delta": 0, "formal_theorem_proved": False}},
    ]
    failed = [item["requirement_id"] for item in requirements if not item["passed"]]
    payload = {
        "title": "B1/B7 cone01 R119 dual-engine compositional replay gate",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": STATUS if not failed else "cone01_r119_dual_engine_composition_failed",
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_path": SOURCE_PATH,
        "candidate_path": CANDIDATE_PATH,
        "requirements": requirements,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "summary": summary,
        "artifacts": {"full_replay": str(full_path.relative_to(root)), "composition": str(composition_path.relative_to(root)), "negative_control": str(negative_path_json.relative_to(root)), "r116_result": R116_RESULT_PATH, "r118_result": R118_RESULT_PATH},
        "claim_boundary": {"what_is_supported": "Dual-engine finite replay and prefix/suffix composition agree for the R116 source/candidate pair; an inserted-X negative control is detected.", "what_is_not_supported": "Formal arbitrary-input unitary equality, mid-circuit measurement semantics, hardware layout improvement, T-resource reduction, or B7 credit.", "next_gate": "Obtain a genuinely independent compiler candidate or a symbolic local rewrite certificate before any B7 resource credit."},
    }
    payload["payload_hash"] = stable_hash(payload)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    payload = run_gate(Path(args.repo_root))
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    if payload["requirements_failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
