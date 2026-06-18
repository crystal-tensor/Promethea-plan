#!/usr/bin/env python3
"""Exact statevector equivalence checks for small B1 OpenQASM circuits."""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sys
from pathlib import Path


QREG_RE = re.compile(r"^qreg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]\s*;")
GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
MEASURE_RE = re.compile(r"^measure\s+(.+?)\s*->\s*(.+);$")
QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")

STRUCTURAL_PREFIXES = (
    "OPENQASM",
    "include",
    "creg",
    "barrier",
    "opaque",
    "gate ",
)


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def safe_eval_angle(expr: str) -> float:
    """Evaluate a small arithmetic expression containing pi."""
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Constant,
        ast.Name,
        ast.Load,
    )
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f"Unsupported angle expression: {expr}")
        if isinstance(node, ast.Name) and node.id != "pi":
            raise ValueError(f"Unsupported name in angle expression: {node.id}")
    return float(eval(compile(tree, "<angle>", "eval"), {"__builtins__": {}}, {"pi": math.pi}))


def parse_params(param_text: str | None) -> list[float]:
    if not param_text:
        return []
    inner = param_text.strip()[1:-1].strip()
    if not inner:
        return []
    return [safe_eval_angle(part.strip()) for part in inner.split(",")]


def parse_qasm(path: Path) -> tuple[dict[str, int], list[dict]]:
    qregs: dict[str, int] = {}
    operations: list[dict] = []
    unsupported: list[tuple[int, str]] = []

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = strip_comment(raw_line)
        if not line:
            continue
        if any(line.startswith(prefix) for prefix in STRUCTURAL_PREFIXES):
            continue
        qreg_match = QREG_RE.match(line)
        if qreg_match:
            qregs[qreg_match.group(1)] = int(qreg_match.group(2))
            continue
        if MEASURE_RE.match(line):
            continue
        gate_match = GATE_RE.match(line)
        if gate_match:
            operations.append(
                {
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
    return qregs, operations


def qubit_index_map(qregs: dict[str, int]) -> dict[tuple[str, int], int]:
    mapping: dict[tuple[str, int], int] = {}
    offset = 0
    for name, size in qregs.items():
        for idx in range(size):
            mapping[(name, idx)] = offset + idx
        offset += size
    return mapping


def apply_single_qubit(state: list[complex], qubit: int, matrix: tuple[complex, complex, complex, complex]) -> None:
    a00, a01, a10, a11 = matrix
    bit = 1 << qubit
    for base in range(len(state)):
        if base & bit:
            continue
        paired = base | bit
        zero = state[base]
        one = state[paired]
        state[base] = a00 * zero + a01 * one
        state[paired] = a10 * zero + a11 * one


def apply_phase_if(state: list[complex], qubits: list[int], phase: complex) -> None:
    mask = 0
    for qubit in qubits:
        mask |= 1 << qubit
    for idx, amp in enumerate(state):
        if idx & mask == mask:
            state[idx] = amp * phase


def apply_rzz(state: list[complex], left: int, right: int, theta: float) -> None:
    left_mask = 1 << left
    right_mask = 1 << right
    same_phase = complex(math.cos(-theta / 2), math.sin(-theta / 2))
    different_phase = complex(math.cos(theta / 2), math.sin(theta / 2))
    for idx, amp in enumerate(state):
        same = bool(idx & left_mask) == bool(idx & right_mask)
        state[idx] = amp * (same_phase if same else different_phase)


def apply_controlled_x(state: list[complex], controls: list[int], target: int) -> None:
    control_mask = 0
    for control in controls:
        control_mask |= 1 << control
    target_mask = 1 << target
    for idx in range(len(state)):
        if idx & target_mask:
            continue
        if idx & control_mask == control_mask:
            paired = idx | target_mask
            state[idx], state[paired] = state[paired], state[idx]


def apply_swap(state: list[complex], left: int, right: int) -> None:
    if left == right:
        return
    left_mask = 1 << left
    right_mask = 1 << right
    for idx in range(len(state)):
        left_bit = bool(idx & left_mask)
        right_bit = bool(idx & right_mask)
        if left_bit or not right_bit:
            continue
        paired = (idx | left_mask) & ~right_mask
        state[idx], state[paired] = state[paired], state[idx]


def single_qubit_matrix(gate: str, params: list[float]) -> tuple[complex, complex, complex, complex] | None:
    inv_sqrt2 = 1 / math.sqrt(2)
    if gate == "h":
        return (inv_sqrt2, inv_sqrt2, inv_sqrt2, -inv_sqrt2)
    if gate == "x":
        return (0, 1, 1, 0)
    if gate == "y":
        return (0, -1j, 1j, 0)
    if gate == "z":
        return (1, 0, 0, -1)
    if gate == "s":
        return (1, 0, 0, 1j)
    if gate == "sdg":
        return (1, 0, 0, -1j)
    if gate == "t":
        return (1, 0, 0, complex(math.cos(math.pi / 4), math.sin(math.pi / 4)))
    if gate == "tdg":
        return (1, 0, 0, complex(math.cos(-math.pi / 4), math.sin(-math.pi / 4)))
    if gate == "id":
        return (1, 0, 0, 1)
    if gate == "sx":
        return (
            0.5 + 0.5j,
            0.5 - 0.5j,
            0.5 - 0.5j,
            0.5 + 0.5j,
        )
    if gate in {"u1", "p"}:
        theta = params[0]
        return (1, 0, 0, complex(math.cos(theta), math.sin(theta)))
    if gate in {"u", "u3"}:
        theta, phi, lam = params
        c = math.cos(theta / 2)
        s = math.sin(theta / 2)
        exp_phi = complex(math.cos(phi), math.sin(phi))
        exp_lam = complex(math.cos(lam), math.sin(lam))
        exp_phi_lam = complex(math.cos(phi + lam), math.sin(phi + lam))
        return (c, -exp_lam * s, exp_phi * s, exp_phi_lam * c)
    if gate == "rx":
        theta = params[0]
        c = math.cos(theta / 2)
        s = math.sin(theta / 2)
        return (c, -1j * s, -1j * s, c)
    if gate == "ry":
        theta = params[0]
        c = math.cos(theta / 2)
        s = math.sin(theta / 2)
        return (c, -s, s, c)
    if gate == "rz":
        theta = params[0]
        return (
            complex(math.cos(-theta / 2), math.sin(-theta / 2)),
            0,
            0,
            complex(math.cos(theta / 2), math.sin(theta / 2)),
        )
    return None


def simulate(path: Path, max_qubits: int) -> dict:
    qregs, operations = parse_qasm(path)
    mapping = qubit_index_map(qregs)
    qubit_count = sum(qregs.values())
    if qubit_count > max_qubits:
        raise ValueError(f"{path} has {qubit_count} qubits, exceeding max {max_qubits}")

    state = [0j] * (1 << qubit_count)
    state[0] = 1 + 0j

    for op in operations:
        gate = op["gate"]
        qubits = [mapping[qubit] for qubit in op["qubits"]]
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
            apply_phase_if(state, [control], 1)
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

    return {"path": str(path), "qubits": qubit_count, "state": state}


def fidelity(left: list[complex], right: list[complex]) -> float:
    if len(left) != len(right):
        return 0.0
    inner = sum(a.conjugate() * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(abs(a) ** 2 for a in left))
    right_norm = math.sqrt(sum(abs(b) ** 2 for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return abs(inner / (left_norm * right_norm)) ** 2


def max_global_phase_adjusted_delta(left: list[complex], right: list[complex]) -> float:
    inner = sum(a.conjugate() * b for a, b in zip(left, right))
    phase = 1 + 0j if abs(inner) == 0 else inner / abs(inner)
    return max(abs(a * phase - b) for a, b in zip(left, right))


def compare_pair(left_path: Path, right_path: Path, max_qubits: int, tolerance: float) -> dict:
    left = simulate(left_path, max_qubits)
    right = simulate(right_path, max_qubits)
    if left["qubits"] != right["qubits"]:
        return {
            "left": str(left_path),
            "right": str(right_path),
            "equivalent": False,
            "reason": "qubit_count_mismatch",
            "left_qubits": left["qubits"],
            "right_qubits": right["qubits"],
        }
    fid = fidelity(left["state"], right["state"])
    delta = max_global_phase_adjusted_delta(left["state"], right["state"])
    return {
        "left": str(left_path),
        "right": str(right_path),
        "qubits": left["qubits"],
        "fidelity": fid,
        "max_global_phase_adjusted_delta": delta,
        "equivalent": fid >= 1 - tolerance and delta <= math.sqrt(tolerance),
    }


def discover_pairs(left: Path, right: Path) -> list[tuple[Path, Path]]:
    if left.is_file() and right.is_file():
        return [(left, right)]
    if not left.is_dir() or not right.is_dir():
        raise ValueError("Inputs must be either two files or two directories")
    pairs: list[tuple[Path, Path]] = []
    for left_file in sorted(left.rglob("*.qasm")):
        right_file = right / left_file.relative_to(left)
        if right_file.exists():
            pairs.append((left_file, right_file))
    return pairs


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--max-qubits", type=int, default=12)
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    pairs = discover_pairs(args.left, args.right)
    if not pairs:
        raise SystemExit("No matching .qasm file pairs found")

    results = [
        compare_pair(left, right, max_qubits=args.max_qubits, tolerance=args.tolerance)
        for left, right in pairs
    ]
    payload = {
        "benchmark_id": "B1",
        "check": "statevector_equivalence",
        "pair_count": len(results),
        "passed": sum(1 for result in results if result["equivalent"]),
        "failed": sum(1 for result in results if not result["equivalent"]),
        "tolerance": args.tolerance,
        "results": results,
    }
    output = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0 if payload["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
