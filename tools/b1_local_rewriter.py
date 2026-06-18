#!/usr/bin/env python3
"""Conservative local OpenQASM rewrites for the B1 compression baseline."""

from __future__ import annotations

import argparse
import ast
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path


GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
ZERO_ROTATION_RE = re.compile(r"^\((?:0|0\.0|0\*pi|0\.0\*pi)\)$")

SELF_INVERSE_GATES = {
    "h",
    "x",
    "y",
    "z",
    "cx",
    "cz",
    "cy",
    "swap",
}

ROTATION_GATES = {
    "rx",
    "ry",
    "rz",
    "u1",
    "p",
}

INVERSE_GATE_PAIRS = {
    ("s", "sdg"),
    ("sdg", "s"),
    ("t", "tdg"),
    ("tdg", "t"),
}


@dataclass(frozen=True)
class ParsedGate:
    gate: str
    params: str
    operands: str

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.gate, self.params, self.operands)


def strip_comment(line: str) -> tuple[str, str]:
    if "//" not in line:
        return line.rstrip("\n"), ""
    code, comment = line.rstrip("\n").split("//", 1)
    return code.rstrip(), "//" + comment


def parse_gate(line: str) -> ParsedGate | None:
    code, _comment = strip_comment(line)
    code = code.strip()
    match = GATE_RE.match(code)
    if not match:
        return None
    gate = match.group(1).lower()
    params = match.group(2) or ""
    operands = re.sub(r"\s+", "", match.group(3))
    return ParsedGate(gate=gate, params=params, operands=operands)


def is_zero_rotation(parsed: ParsedGate) -> bool:
    return parsed.gate in ROTATION_GATES and bool(ZERO_ROTATION_RE.match(parsed.params))


def can_cancel(left: ParsedGate, right: ParsedGate) -> bool:
    if left.gate in SELF_INVERSE_GATES and left.key == right.key:
        return True
    return (left.gate, right.gate) in INVERSE_GATE_PAIRS and left.operands == right.operands


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
            raise ValueError(expr)
        if isinstance(node, ast.Name) and node.id != "pi":
            raise ValueError(expr)
    return float(eval(compile(tree, "<angle>", "eval"), {"__builtins__": {}}, {"pi": math.pi}))


def angle_from_params(params: str) -> float | None:
    if not params.startswith("(") or not params.endswith(")"):
        return None
    inner = params[1:-1].strip()
    if "," in inner:
        return None
    try:
        return safe_eval_angle(inner)
    except Exception:
        return None


def can_merge_rotations(left: ParsedGate, right: ParsedGate) -> float | None:
    if left.gate != right.gate or left.gate not in ROTATION_GATES:
        return None
    if left.operands != right.operands:
        return None
    left_angle = angle_from_params(left.params)
    right_angle = angle_from_params(right.params)
    if left_angle is None or right_angle is None:
        return None
    return left_angle + right_angle


def format_angle(angle: float) -> str:
    if abs(angle) < 1e-12:
        return "0"
    return f"{angle:.17g}"


def rewrite_lines(lines: list[str]) -> tuple[list[str], dict[str, int]]:
    output: list[str] = []
    pending_gate: ParsedGate | None = None
    pending_line: str | None = None
    stats = {
        "cancelled_self_inverse_pairs": 0,
        "cancelled_inverse_pairs": 0,
        "merged_rotations": 0,
        "removed_identity_gates": 0,
        "removed_zero_rotations": 0,
        "input_lines": len(lines),
        "output_lines": 0,
    }

    def flush_pending() -> None:
        nonlocal pending_gate, pending_line
        if pending_line is not None:
            output.append(pending_line)
        pending_gate = None
        pending_line = None

    for raw_line in lines:
        parsed = parse_gate(raw_line)
        if parsed is None:
            flush_pending()
            output.append(raw_line)
            continue
        if parsed.gate == "id":
            stats["removed_identity_gates"] += 1
            continue
        if is_zero_rotation(parsed):
            stats["removed_zero_rotations"] += 1
            continue
        if pending_gate is not None and can_cancel(pending_gate, parsed):
            if pending_gate.gate == parsed.gate:
                stats["cancelled_self_inverse_pairs"] += 1
            else:
                stats["cancelled_inverse_pairs"] += 1
            pending_gate = None
            pending_line = None
            continue
        if pending_gate is not None:
            merged_angle = can_merge_rotations(pending_gate, parsed)
            if merged_angle is not None:
                stats["merged_rotations"] += 1
                pending_line = f"{parsed.gate}({format_angle(merged_angle)}) {parsed.operands};"
                pending_gate = ParsedGate(parsed.gate, f"({format_angle(merged_angle)})", parsed.operands)
                if abs(merged_angle) < 1e-12:
                    pending_gate = None
                    pending_line = None
                    stats["removed_zero_rotations"] += 1
                continue
        flush_pending()
        pending_gate = parsed
        pending_line = raw_line

    flush_pending()
    stats["output_lines"] = len(output)
    return output, stats


def rewrite_file(input_path: Path, output_path: Path) -> dict[str, int | str]:
    lines = input_path.read_text(encoding="utf-8").splitlines()
    rewritten, stats = rewrite_lines(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")
    return {
        "input": str(input_path),
        "output": str(output_path),
        **stats,
    }


def discover_inputs(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.qasm")))
        elif path.suffix == ".qasm":
            files.append(path)
    return files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    input_files = discover_inputs(args.inputs)
    if not input_files:
        raise SystemExit("No .qasm inputs found")

    for input_path in input_files:
        output_path = args.output_dir / input_path.name
        stats = rewrite_file(input_path, output_path)
        print(
            f"{stats['input']} -> {stats['output']}: "
            f"cancelled_pairs={stats['cancelled_self_inverse_pairs']} "
            f"inverse_pairs={stats['cancelled_inverse_pairs']} "
            f"merged_rotations={stats['merged_rotations']} "
            f"identity_gates={stats['removed_identity_gates']} "
            f"zero_rotations={stats['removed_zero_rotations']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
