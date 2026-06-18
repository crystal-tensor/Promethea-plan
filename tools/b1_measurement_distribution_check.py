#!/usr/bin/env python3
"""Compare OpenQASM measurement-output distributions for B1 circuits."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

from b1_equivalence_check import (
    GATE_RE,
    MEASURE_RE,
    QREG_RE,
    QUBIT_RE,
    apply_controlled_x,
    apply_phase_if,
    apply_rzz,
    apply_single_qubit,
    apply_swap,
    parse_params,
    single_qubit_matrix,
)


CREG_RE = re.compile(r"^creg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]\s*;")
CREG_RE = re.compile(r"^creg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]\s*;")

STRUCTURAL_PREFIXES = (
    "OPENQASM",
    "include",
    "barrier",
    "opaque",
    "gate ",
)


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def parse_program(path: Path) -> dict:
    qregs: dict[str, int] = {}
    cregs: dict[str, int] = {}
    operations: list[dict] = []
    unsupported: list[tuple[int, str]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = strip_comment(raw)
        if not line:
            continue
        if any(line.startswith(prefix) for prefix in STRUCTURAL_PREFIXES):
            continue
        qmatch = QREG_RE.match(line)
        if qmatch:
            qregs[qmatch.group(1)] = int(qmatch.group(2))
            continue
        cmatch = CREG_RE.match(line)
        if cmatch:
            cregs[cmatch.group(1)] = int(cmatch.group(2))
            continue
        mmatch = MEASURE_RE.match(line)
        if mmatch:
            qbits = QUBIT_RE.findall(mmatch.group(1))
            cbits = QUBIT_RE.findall(mmatch.group(2))
            if len(qbits) != 1 or len(cbits) != 1:
                raise ValueError(f"unsupported measurement statement in {path}: {line}")
            operations.append(
                {
                    "kind": "measure",
                    "qbit": (qbits[0][0], int(qbits[0][1])),
                    "cbit": (cbits[0][0], int(cbits[0][1])),
                    "line": line_number,
                    "raw": line,
                }
            )
            continue
        gate_match = GATE_RE.match(line)
        if gate_match:
            operations.append(
                {
                    "kind": "gate",
                    "gate": gate_match.group(1).lower(),
                    "params": parse_params(gate_match.group(2)),
                    "qubits": [(name, int(idx)) for name, idx in QUBIT_RE.findall(gate_match.group(3))],
                    "line": line_number,
                    "raw": line,
                }
            )
            continue
        unsupported.append((line_number, line))
    if unsupported:
        detail = ", ".join(f"line {line}: {text}" for line, text in unsupported[:5])
        raise ValueError(f"Unsupported OpenQASM statements in {path}: {detail}")
    return {"qregs": qregs, "cregs": cregs, "operations": operations}


def flat_index(regs: dict[str, int]) -> dict[tuple[str, int], int]:
    mapping: dict[tuple[str, int], int] = {}
    offset = 0
    for name, size in regs.items():
        for idx in range(size):
            mapping[(name, idx)] = offset + idx
        offset += size
    return mapping


def collapse_state(state: list[complex], qubit: int, outcome: int) -> tuple[float, list[complex]]:
    bit = 1 << qubit
    probability = sum(abs(amp) ** 2 for idx, amp in enumerate(state) if ((idx & bit) != 0) == bool(outcome))
    if probability <= 1e-15:
        return 0.0, []
    scale = probability ** -0.5
    collapsed = [
        amp * scale if ((idx & bit) != 0) == bool(outcome) else 0j
        for idx, amp in enumerate(state)
    ]
    return probability, collapsed


def gate_qubit_indices(op: dict, qmap: dict[tuple[str, int], int]) -> set[int]:
    if op["kind"] != "gate":
        return set()
    return {qmap[qbit] for qbit in op["qubits"]}


def apply_gate(state: list[complex], op: dict, qmap: dict[tuple[str, int], int], path: Path) -> None:
    gate = op["gate"]
    qubits = [qmap[qubit] for qubit in op["qubits"]]
    matrix = single_qubit_matrix(gate, op["params"])
    if matrix is not None and len(qubits) == 1:
        apply_single_qubit(state, qubits[0], matrix)
    elif gate == "cx" and len(qubits) == 2:
        apply_controlled_x(state, [qubits[0]], qubits[1])
    elif gate == "ccx" and len(qubits) == 3:
        apply_controlled_x(state, [qubits[0], qubits[1]], qubits[2])
    elif gate == "cz" and len(qubits) == 2:
        apply_phase_if(state, qubits, -1)
    elif gate == "cu1" and len(qubits) == 2:
        theta = op["params"][0]
        apply_phase_if(state, qubits, complex(math.cos(theta), math.sin(theta)))
    elif gate == "crz" and len(qubits) == 2:
        theta = op["params"][0]
        control, target = qubits
        for idx, amp in enumerate(state):
            if idx & (1 << control):
                sign = 1 if idx & (1 << target) else -1
                angle = sign * theta / 2
                state[idx] = amp * complex(math.cos(angle), math.sin(angle))
    elif gate == "rzz" and len(qubits) == 2:
        apply_rzz(state, qubits[0], qubits[1], op["params"][0])
    elif gate == "swap" and len(qubits) == 2:
        apply_swap(state, qubits[0], qubits[1])
    else:
        raise ValueError(f"Unsupported gate in {path} at line {op['line']}: {op['raw']}")


def distribution(path: Path, max_qubits: int) -> dict[str, float]:
    parsed = parse_program(path)
    qmap = flat_index(parsed["qregs"])
    cmap = flat_index(parsed["cregs"])
    qubit_count = sum(parsed["qregs"].values())
    if qubit_count > max_qubits:
        raise ValueError(f"{path} has {qubit_count} qubits, exceeding max {max_qubits}")
    classical_bits = sum(parsed["cregs"].values())
    if not any(op["kind"] == "measure" for op in parsed["operations"]):
        raise ValueError(f"{path} has no measurements")

    future_gate_qubits: list[set[int]] = [set() for _ in parsed["operations"]]
    future: set[int] = set()
    for idx in range(len(parsed["operations"]) - 1, -1, -1):
        future_gate_qubits[idx] = set(future)
        future |= gate_qubit_indices(parsed["operations"][idx], qmap)

    initial_state = [0j] * (1 << qubit_count)
    initial_state[0] = 1 + 0j
    branches = [{"weight": 1.0, "state": initial_state, "classical": [0] * classical_bits}]
    deferred_measurements: list[tuple[int, int]] = []

    for index, op in enumerate(parsed["operations"]):
        if op["kind"] == "gate":
            for branch in branches:
                apply_gate(branch["state"], op, qmap, path)
            continue

        qidx = qmap[op["qbit"]]
        cidx = cmap[op["cbit"]]
        if qidx not in future_gate_qubits[index]:
            deferred_measurements.append((qidx, cidx))
            continue

        next_branches = []
        for branch in branches:
            for outcome in [0, 1]:
                probability, collapsed = collapse_state(branch["state"], qidx, outcome)
                if probability <= 1e-15:
                    continue
                classical = list(branch["classical"])
                classical[cidx] = outcome
                next_branches.append(
                    {
                        "weight": branch["weight"] * probability,
                        "state": collapsed,
                        "classical": classical,
                    }
                )
        branches = next_branches

    dist: dict[str, float] = {}
    for branch in branches:
        for basis_index, amplitude in enumerate(branch["state"]):
            probability = branch["weight"] * abs(amplitude) ** 2
            if probability <= 1e-15:
                continue
            bits = list(branch["classical"])
            for qidx, cidx in deferred_measurements:
                bits[cidx] = (basis_index >> qidx) & 1
            key = "".join(str(bit) for bit in bits)
            dist[key] = dist.get(key, 0.0) + probability
    return {key: value for key, value in dist.items() if value > 1e-15}


def compare_pair(left: Path, right: Path, max_qubits: int, tolerance: float) -> dict:
    left_dist = distribution(left, max_qubits)
    right_dist = distribution(right, max_qubits)
    keys = sorted(set(left_dist) | set(right_dist))
    l1 = sum(abs(left_dist.get(key, 0.0) - right_dist.get(key, 0.0)) for key in keys)
    max_delta = max((abs(left_dist.get(key, 0.0) - right_dist.get(key, 0.0)) for key in keys), default=0.0)
    return {
        "left": str(left),
        "right": str(right),
        "semantic_model": "sequential_statevector_with_branching_mid_circuit_measurements",
        "classical_outcome_count_left": len(left_dist),
        "classical_outcome_count_right": len(right_dist),
        "l1_delta": l1,
        "max_probability_delta": max_delta,
        "equivalent": l1 <= tolerance and max_delta <= tolerance,
    }


def discover_pairs(left: Path, right: Path) -> list[tuple[Path, Path]]:
    if left.is_file() and right.is_file():
        return [(left, right)]
    if not left.is_dir() or not right.is_dir():
        raise ValueError("Inputs must be either two files or two directories")
    pairs = []
    for left_file in sorted(left.rglob("*.qasm")):
        right_file = right / left_file.relative_to(left)
        if right_file.exists():
            pairs.append((left_file, right_file))
    return pairs


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--max-qubits", type=int, default=15)
    parser.add_argument("--tolerance", type=float, default=1e-8)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    pairs = discover_pairs(args.left, args.right)
    if not pairs:
        raise SystemExit("No matching .qasm file pairs found")
    results = [compare_pair(left, right, args.max_qubits, args.tolerance) for left, right in pairs]
    payload = {
        "benchmark_id": "B1",
        "check": "measurement_distribution_equivalence",
        "pair_count": len(results),
        "passed": sum(1 for row in results if row["equivalent"]),
        "failed": sum(1 for row in results if not row["equivalent"]),
        "tolerance": args.tolerance,
        "results": results,
    }
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if payload["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
