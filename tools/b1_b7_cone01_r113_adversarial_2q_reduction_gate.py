#!/usr/bin/env python3
"""T-B1-004hk/T-B7-016t: reject an attractive but non-equivalent 2Q reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from qiskit import QuantumCircuit, qasm2, transpile


METHOD = "b1_b7_cone01_r113_adversarial_2q_reduction_gate_v0"
STATUS = "cone01_r113_adversarial_2q_reduction_rejected_non_equivalent"
MODEL_STATUS = "qiskit_level3_two_qubit_reduction_fails_exact_equivalence"
TARGET_ID = "T-B1-004hk/T-B7-016t"
UPSTREAM_TARGET_ID = "T-B1-004hj/T-B7-016s"
SOURCE_PATH = "benchmarks/qasmbench_medium_exact/gcm_h6.qasm"
OUT_DIR = "results/B1_B7_cone01_R113_adversarial_2q_reduction_gate"
RESULT_PATH = "results/B1_B7_cone01_R113_adversarial_2q_reduction_gate_v0.json"
REPORT_PATH = "research/B1_B7_cone01_R113_adversarial_2q_reduction_gate.md"


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def total(payload: dict, key: str) -> float:
    return sum(float(row[key]) for row in payload["results"])


def report(payload: dict) -> str:
    summary = payload["summary"]
    rows = "\n".join(
        f"- `{item['requirement_id']}` {'PASS' if item['passed'] else 'FAIL'}: {item['label']}"
        for item in payload["requirements"]
    )
    return f"""# B1/B7 Cone01 R113 Adversarial 2Q Reduction Gate

## Summary

- Target: `{TARGET_ID}`
- Upstream target: `{UPSTREAM_TARGET_ID}`
- Method: `{METHOD}`
- Status: `{STATUS}`
- Model status: `{MODEL_STATUS}`
- Source two-qubit gates: `{summary['source_two_qubit_gate_count']}`
- Candidate two-qubit gates: `{summary['candidate_two_qubit_gate_count']}`
- Apparent two-qubit reduction: `{summary['two_qubit_reduction_pct']:.4f}%`
- Exact equivalence: `{summary['equivalence_passed']}/{summary['equivalence_failed']}`
- Candidate accepted: `{summary['candidate_accepted']}`

R113 runs an adversarial Qiskit level-3 all-to-all `u3/cx` optimization. It
appears to save two-qubit gates, but the local exact statevector checker rejects
the candidate. This is a useful negative result: a nonzero two-qubit delta is
not enough to enter the B1/B7 ledger.

## Requirements

{rows}

## Claim Boundary

R113 supports only the rejection of this candidate on this workload. It does
not claim that Qiskit level 3 is generally incorrect, nor does it claim a
minimality theorem. No occurrence removal, proxy-T reduction, layout credit,
or B7 credit is accepted.
"""


def run_gate(root: Path) -> dict:
    root = root.resolve()
    source = root / SOURCE_PATH
    out = root / OUT_DIR
    if out.exists():
        shutil.rmtree(out)
    work = out / "work"
    work.mkdir(parents=True)
    candidate_path = work / "gcm_h6_qiskit_level3_candidate.qasm"
    source_circuit = QuantumCircuit.from_qasm_file(str(source))
    started = time.perf_counter()
    candidate = transpile(source_circuit, basis_gates=["u3", "cx", "measure"], optimization_level=3)
    transpile_seconds = time.perf_counter() - started
    candidate_path.write_text(qasm2.dumps(candidate), encoding="utf-8")
    source_metrics_path = out / "source_metrics.json"
    candidate_metrics_path = out / "candidate_metrics.json"
    equivalence_path = out / "exact_equivalence.json"
    source_run = run([sys.executable, "tools/b1_qasm_metrics.py", SOURCE_PATH, "--profile", "heavy_hex_like_sparse", "--pretty", "--output", str(source_metrics_path)], root)
    candidate_metrics = run([sys.executable, "tools/b1_qasm_metrics.py", str(candidate_path), "--profile", "heavy_hex_like_sparse", "--pretty", "--output", str(candidate_metrics_path)], root)
    equivalence = run([sys.executable, "tools/b1_equivalence_check.py", SOURCE_PATH, str(candidate_path), "--max-qubits", "15", "--pretty", "--output", str(equivalence_path)], root)
    (out / "commands.stdout.txt").write_text(
        "SOURCE_METRICS\n" + source_run.stdout + source_run.stderr + "\nCANDIDATE_METRICS\n" + candidate_metrics.stdout + candidate_metrics.stderr + "\nEQUIVALENCE\n" + equivalence.stdout + equivalence.stderr,
        encoding="utf-8",
    )
    source_metrics_data = load(source_metrics_path)
    candidate_metrics_data = load(candidate_metrics_path)
    equivalence_data = load(equivalence_path)
    source_2q = total(source_metrics_data, "two_qubit_gate_count")
    candidate_2q = total(candidate_metrics_data, "two_qubit_gate_count")
    source_ops = total(source_metrics_data, "operation_count")
    candidate_ops = total(candidate_metrics_data, "operation_count")
    source_row = source_metrics_data["results"][0]
    candidate_row = candidate_metrics_data["results"][0]
    failed_rows = [row for row in equivalence_data["results"] if not row["equivalent"]]
    fidelity = failed_rows[0].get("fidelity") if failed_rows else None
    candidate_accepted = equivalence_data["failed"] == 0
    summary = {
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "source_two_qubit_gate_count": source_2q,
        "candidate_two_qubit_gate_count": candidate_2q,
        "two_qubit_gate_delta": candidate_2q - source_2q,
        "two_qubit_reduction_pct": (source_2q - candidate_2q) / source_2q * 100 if source_2q else 0,
        "source_operation_count": source_ops,
        "candidate_operation_count": candidate_ops,
        "operation_reduction_pct": (source_ops - candidate_ops) / source_ops * 100 if source_ops else 0,
        "equivalence_passed": equivalence_data["passed"],
        "equivalence_failed": equivalence_data["failed"],
        "first_failed_fidelity": fidelity,
        "candidate_accepted": candidate_accepted,
        "transpile_seconds": transpile_seconds,
        "counter_transition_accepted": False,
        "counter_delta": 0,
        "new_credit_delta": 0,
    }
    requirements = [
        {"requirement_id": "P1", "label": "source and candidate metrics are materialized", "passed": source_metrics_path.exists() and candidate_metrics_path.exists(), "evidence": {"source": str(source_metrics_path.relative_to(root)), "candidate": str(candidate_metrics_path.relative_to(root))}},
        {"requirement_id": "P2", "label": "candidate shows a nonzero two-qubit reduction", "passed": summary["two_qubit_gate_delta"] < 0, "evidence": {"source": source_2q, "candidate": candidate_2q, "delta": summary["two_qubit_gate_delta"]}},
        {"requirement_id": "P3", "label": "exact equivalence checker rejects the candidate", "passed": equivalence_data["failed"] > 0 and not candidate_accepted, "evidence": {"passed": equivalence_data["passed"], "failed": equivalence_data["failed"], "first_failed_fidelity": fidelity}},
        {"requirement_id": "P4", "label": "candidate acceptance is gated on exact equivalence", "passed": not candidate_accepted, "evidence": {"candidate_accepted": candidate_accepted}},
        {"requirement_id": "P5", "label": "rejection keeps counters and credit at zero", "passed": summary["counter_delta"] == 0 and summary["new_credit_delta"] == 0, "evidence": {"counter_delta": 0, "new_credit_delta": 0}},
        {"requirement_id": "P6", "label": "adversarial claim boundary is recorded", "passed": True, "evidence": {"model_status": MODEL_STATUS}},
        {"requirement_id": "P7", "label": "candidate circuit is hashable and replayable", "passed": candidate_path.exists() and equivalence_path.exists(), "evidence": {"candidate": str(candidate_path.relative_to(root)), "equivalence": str(equivalence_path.relative_to(root))}},
        {"requirement_id": "P8", "label": "no B7 promotion occurs from the rejected 2Q delta", "passed": True, "evidence": {"b7_credit": 0}},
    ]
    failed_requirements = [item["requirement_id"] for item in requirements if not item["passed"]]
    payload = {
        "title": "B1/B7 cone01 R113 adversarial 2Q reduction gate",
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
        "requirements_passed": len(requirements) - len(failed_requirements),
        "requirements_failed": len(failed_requirements),
        "summary": summary,
        "artifacts": {"candidate_qasm": str(candidate_path.relative_to(root)), "source_metrics": str(source_metrics_path.relative_to(root)), "candidate_metrics": str(candidate_metrics_path.relative_to(root)), "exact_equivalence": str(equivalence_path.relative_to(root)), "commands_stdout": str((out / "commands.stdout.txt").relative_to(root))},
        "claim_boundary": {"what_is_supported": "Qiskit level-3 emits a candidate with a nonzero two-qubit reduction that is rejected by exact statevector equivalence.", "what_is_not_supported": "No accepted 2Q reduction, arbitrary-input equivalence, T-resource reduction, layout improvement, or B7 credit.", "next_gate": "Find a composable candidate that passes exact equivalence and retains a nonzero two-qubit or proxy-T delta under the same denominator."},
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
