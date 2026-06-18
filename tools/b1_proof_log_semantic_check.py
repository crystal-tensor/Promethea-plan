#!/usr/bin/env python3
"""Check local semantic identities recorded in B1 proof logs."""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sys
from pathlib import Path


GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def safe_eval_angle(expr: str) -> float:
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


def parse_gate(line: str) -> dict:
    code = strip_comment(line)
    match = GATE_RE.match(code)
    if not match:
        raise ValueError(f"Unsupported gate line: {line}")
    return {
        "gate": match.group(1).lower(),
        "params": parse_params(match.group(2)),
        "qubits": tuple(f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(match.group(3))),
        "raw": code,
    }


def matmul(left: tuple[complex, ...], right: tuple[complex, ...], size: int) -> tuple[complex, ...]:
    return tuple(
        sum(left[row * size + mid] * right[mid * size + col] for mid in range(size))
        for row in range(size)
        for col in range(size)
    )


def single_qubit_matrix(gate: str, params: list[float]) -> tuple[complex, complex, complex, complex]:
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
    raise ValueError(f"Unsupported single-qubit gate: {gate}")


def cx_matrix() -> tuple[complex, ...]:
    return (
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 0, 1,
        0, 0, 1, 0,
    )


def rz_on_target_matrix(theta: float) -> tuple[complex, ...]:
    minus = complex(math.cos(-theta / 2), math.sin(-theta / 2))
    plus = complex(math.cos(theta / 2), math.sin(theta / 2))
    return (
        minus, 0, 0, 0,
        0, plus, 0, 0,
        0, 0, minus, 0,
        0, 0, 0, plus,
    )


def rzz_matrix(theta: float) -> tuple[complex, ...]:
    same = complex(math.cos(-theta / 2), math.sin(-theta / 2))
    different = complex(math.cos(theta / 2), math.sin(theta / 2))
    return (
        same, 0, 0, 0,
        0, different, 0, 0,
        0, 0, different, 0,
        0, 0, 0, same,
    )


def max_global_phase_adjusted_delta(left: tuple[complex, ...], right: tuple[complex, ...]) -> float:
    inner = sum(a.conjugate() * b for a, b in zip(left, right))
    phase = 1 + 0j if abs(inner) == 0 else inner / abs(inner)
    return max(abs(a * phase - b) for a, b in zip(left, right))


def check_oneq_event(event: dict, tolerance: float) -> tuple[bool, float, str | None]:
    if event["rule"] == "remove_identity_gate":
        gate = parse_gate(event["input_gates"][0])
        if gate["gate"] != "id":
            return False, float("inf"), "identity-removal event does not reference an id gate"
        if event.get("output_gate") is not None:
            return False, float("inf"), "identity-removal event has non-null output gate"
        return True, 0.0, None

    if event["rule"] != "single_qubit_run_to_u3":
        return False, float("inf"), f"unknown 1Q rule: {event['rule']}"

    matrix = (1 + 0j, 0j, 0j, 1 + 0j)
    operand = event["operand"]
    for raw_gate in event["input_gates"]:
        gate = parse_gate(raw_gate)
        if gate["qubits"] != (operand,):
            return False, float("inf"), f"1Q input gate touches unexpected operand: {raw_gate}"
        matrix = matmul(single_qubit_matrix(gate["gate"], gate["params"]), matrix, 2)

    output = parse_gate(event["output_gate"])
    if output["gate"] != "u3" or output["qubits"] != (operand,):
        return False, float("inf"), f"1Q output is not u3 on {operand}: {event['output_gate']}"
    output_matrix = single_qubit_matrix(output["gate"], output["params"])
    delta = max_global_phase_adjusted_delta(matrix, output_matrix)
    return delta <= tolerance, delta, None if delta <= tolerance else f"1Q matrix delta {delta} exceeds tolerance {tolerance}"


def check_rzz_event(event: dict, tolerance: float) -> tuple[bool, float, str | None]:
    if event["rule"] != "cx_rz_cx_to_rzz":
        return False, float("inf"), f"unknown RZZ rule: {event['rule']}"
    input_gates = [parse_gate(raw_gate) for raw_gate in event["input_gates"]]
    output_gate = parse_gate(event["output_gate"])
    control = event["control"]
    target = event["target"]
    if [gate["gate"] for gate in input_gates] != ["cx", "rz", "cx"]:
        return False, float("inf"), "RZZ event input gates are not cx,rz,cx"
    if input_gates[0]["qubits"] != (control, target) or input_gates[2]["qubits"] != (control, target):
        return False, float("inf"), "RZZ event CX operands do not match control,target"
    if input_gates[1]["qubits"] != (target,):
        return False, float("inf"), "RZZ event RZ does not touch target"
    if output_gate["gate"] != "rzz" or output_gate["qubits"] != (control, target):
        return False, float("inf"), "RZZ event output does not match control,target"
    theta = input_gates[1]["params"][0]
    if abs(theta - output_gate["params"][0]) > tolerance:
        return False, abs(theta - output_gate["params"][0]), "RZZ angle differs from input RZ angle"

    cx = cx_matrix()
    local = matmul(cx, matmul(rz_on_target_matrix(theta), cx, 4), 4)
    output = rzz_matrix(theta)
    delta = max_global_phase_adjusted_delta(local, output)
    return delta <= tolerance, delta, None if delta <= tolerance else f"RZZ matrix delta {delta} exceeds tolerance {tolerance}"


def summarize_deltas(deltas: list[float]) -> dict:
    if not deltas:
        return {"count": 0, "max_delta": 0.0}
    return {"count": len(deltas), "max_delta": max(deltas)}


def check_summary(summary_path: Path, tolerance: float) -> dict:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    proof_logs = summary["proof_logs"]
    errors: list[str] = []
    oneq_deltas: list[float] = []
    rzz_deltas: list[float] = []
    oneq_rules: dict[str, int] = {}
    rzz_modes: dict[str, int] = {}

    for event in read_jsonl(Path(proof_logs["single_qubit_block_resynthesis"]["path"])):
        rule = event.get("rule", "")
        oneq_rules[rule] = oneq_rules.get(rule, 0) + 1
        ok, delta, message = check_oneq_event(event, tolerance)
        oneq_deltas.append(delta)
        if not ok:
            errors.append(f"{event.get('input_file')}:{event.get('input_line_numbers')}: {message}")

    for log in proof_logs["rzz_window_resynthesis"]:
        for event in read_jsonl(Path(log["path"])):
            mode = event.get("mode", "")
            rzz_modes[mode] = rzz_modes.get(mode, 0) + 1
            ok, delta, message = check_rzz_event(event, tolerance)
            rzz_deltas.append(delta)
            if not ok:
                errors.append(f"{event.get('input_file')}:{event.get('input_line_numbers')}: {message}")

    return {
        "summary": str(summary_path),
        "passed": not errors,
        "tolerance": tolerance,
        "errors": errors,
        "single_qubit": {
            **summarize_deltas(oneq_deltas),
            "rules": oneq_rules,
        },
        "rzz": {
            **summarize_deltas(rzz_deltas),
            "modes": rzz_modes,
        },
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    report = check_summary(args.summary, args.tolerance)
    text = json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
