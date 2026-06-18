#!/usr/bin/env python3
"""Resynthesize single-qubit gate runs into one OpenQASM u3 gate."""

from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path


GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")

SINGLE_QUBIT_GATES = {
    "h",
    "x",
    "y",
    "z",
    "s",
    "sdg",
    "t",
    "tdg",
    "id",
    "sx",
    "rx",
    "ry",
    "rz",
    "u1",
    "p",
    "u",
    "u3",
}


@dataclass(frozen=True)
class GateLine:
    raw: str
    gate: str
    params: list[float]
    operand: str
    line_number: int


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


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


def parse_params(param_text: str | None) -> list[float]:
    if not param_text:
        return []
    inner = param_text.strip()[1:-1].strip()
    if not inner:
        return []
    return [safe_eval_angle(part.strip()) for part in inner.split(",")]


def parse_single_qubit_gate(line: str, line_number: int) -> GateLine | None:
    code = strip_comment(line)
    match = GATE_RE.match(code)
    if not match:
        return None
    gate = match.group(1).lower()
    if gate not in SINGLE_QUBIT_GATES:
        return None
    qubits = QUBIT_RE.findall(match.group(3))
    if len(qubits) != 1:
        return None
    name, idx = qubits[0]
    return GateLine(raw=line, gate=gate, params=parse_params(match.group(2)), operand=f"{name}[{idx}]", line_number=line_number)


def matmul(left: tuple[complex, complex, complex, complex], right: tuple[complex, complex, complex, complex]) -> tuple[complex, complex, complex, complex]:
    a, b, c, d = left
    e, f, g, h = right
    return (a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h)


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


def angle(value: complex) -> float:
    return math.atan2(value.imag, value.real)


def normalize_angle(value: float) -> float:
    while value <= -math.pi:
        value += 2 * math.pi
    while value > math.pi:
        value -= 2 * math.pi
    return value


def u3_from_matrix(matrix: tuple[complex, complex, complex, complex]) -> tuple[float, float, float]:
    a, b, c, d = matrix
    eps = 1e-12
    if abs(a) > eps:
        phase = complex(math.cos(-angle(a)), math.sin(-angle(a)))
        a, b, c, d = (phase * a, phase * b, phase * c, phase * d)
    theta = 2 * math.atan2(abs(c), abs(a))
    if abs(math.sin(theta / 2)) < eps:
        phi = 0.0
        lam = angle(d) - angle(a)
    elif abs(math.cos(theta / 2)) < eps:
        phi = angle(c)
        lam = angle(-b)
    else:
        phi = angle(c)
        lam = angle(-b)
    return (normalize_angle(theta), normalize_angle(phi), normalize_angle(lam))


def format_float(value: float) -> str:
    if abs(value) < 1e-12:
        return "0"
    return f"{value:.17g}"


def resynth_run(run: list[GateLine]) -> str:
    matrix = (1 + 0j, 0j, 0j, 1 + 0j)
    for gate_line in run:
        matrix = matmul(single_qubit_matrix(gate_line.gate, gate_line.params), matrix)
    theta, phi, lam = u3_from_matrix(matrix)
    operand = run[0].operand
    return f"u3({format_float(theta)},{format_float(phi)},{format_float(lam)}) {operand};"


def append_run_certificate(certificates: list[dict] | None, run: list[GateLine], output_gate: str, commute_disjoint: bool) -> None:
    if certificates is None:
        return
    certificates.append(
        {
            "rule": "single_qubit_run_to_u3",
            "certificate_type": "constructive_1q_unitary_matrix_decomposition",
            "commute_disjoint": commute_disjoint,
            "operand": run[0].operand,
            "input_line_numbers": [item.line_number for item in run],
            "input_gates": [strip_comment(item.raw) for item in run],
            "output_gate": output_gate,
            "removed_single_qubit_gates": len(run) - 1,
        }
    )


def append_identity_certificate(certificates: list[dict] | None, parsed: GateLine) -> None:
    if certificates is None:
        return
    certificates.append(
        {
            "rule": "remove_identity_gate",
            "certificate_type": "identity_gate_elimination",
            "operand": parsed.operand,
            "input_line_numbers": [parsed.line_number],
            "input_gates": [strip_comment(parsed.raw)],
            "output_gate": None,
            "removed_single_qubit_gates": 1,
        }
    )


def flush_run(output: list[str], run: list[GateLine], stats: dict[str, int], certificates: list[dict] | None = None, commute_disjoint: bool = False) -> None:
    if not run:
        return
    if len(run) == 1:
        output.append(run[0].raw)
        return
    output_gate = resynth_run(run)
    output.append(output_gate)
    stats["resynthesized_runs"] += 1
    stats["input_single_qubit_gates_in_runs"] += len(run)
    stats["output_u3_gates"] += 1
    stats["removed_single_qubit_gates"] += len(run) - 1
    append_run_certificate(certificates, run, output_gate, commute_disjoint)


def touched_operands(line: str) -> set[str]:
    return {f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(strip_comment(line))}


def rewrite_lines(lines: list[str], min_run_length: int, certificates: list[dict] | None = None) -> tuple[list[str], dict[str, int]]:
    output: list[str] = []
    run: list[GateLine] = []
    stats = {
        "resynthesized_runs": 0,
        "input_single_qubit_gates_in_runs": 0,
        "output_u3_gates": 0,
        "removed_identity_gates": 0,
        "removed_single_qubit_gates": 0,
        "input_lines": len(lines),
        "output_lines": 0,
    }

    for line_number, line in enumerate(lines, start=1):
        parsed = parse_single_qubit_gate(line, line_number)
        if parsed is None:
            flush_run(output, run if len(run) >= min_run_length else [], stats, certificates)
            if run and len(run) < min_run_length:
                output.extend(item.raw for item in run)
            run = []
            output.append(line)
            continue
        if parsed.gate == "id":
            stats["removed_identity_gates"] += 1
            append_identity_certificate(certificates, parsed)
            continue
        if run and parsed.operand != run[-1].operand:
            flush_run(output, run if len(run) >= min_run_length else [], stats, certificates)
            if len(run) < min_run_length:
                output.extend(item.raw for item in run)
            run = []
        run.append(parsed)

    flush_run(output, run if len(run) >= min_run_length else [], stats, certificates)
    if run and len(run) < min_run_length:
        output.extend(item.raw for item in run)
    stats["output_lines"] = len(output)
    return output, stats


def flush_pending_operand(
    output: list[str],
    pending: dict[str, list[GateLine]],
    operand: str,
    min_run_length: int,
    stats: dict[str, int],
    certificates: list[dict] | None = None,
) -> None:
    run = pending.pop(operand, [])
    if not run:
        return
    if len(run) >= min_run_length:
        flush_run(output, run, stats, certificates, commute_disjoint=True)
    else:
        output.extend(item.raw for item in run)


def flush_all_pending(
    output: list[str],
    pending: dict[str, list[GateLine]],
    min_run_length: int,
    stats: dict[str, int],
    certificates: list[dict] | None = None,
) -> None:
    for operand in list(pending):
        flush_pending_operand(output, pending, operand, min_run_length, stats, certificates)


def rewrite_lines_commuting_disjoint(lines: list[str], min_run_length: int, certificates: list[dict] | None = None) -> tuple[list[str], dict[str, int]]:
    output: list[str] = []
    pending: dict[str, list[GateLine]] = {}
    stats = {
        "resynthesized_runs": 0,
        "input_single_qubit_gates_in_runs": 0,
        "output_u3_gates": 0,
        "removed_identity_gates": 0,
        "removed_single_qubit_gates": 0,
        "commuted_disjoint_single_qubit_gates": 0,
        "input_lines": len(lines),
        "output_lines": 0,
    }

    for line_number, line in enumerate(lines, start=1):
        parsed = parse_single_qubit_gate(line, line_number)
        if parsed is not None:
            if parsed.gate == "id":
                stats["removed_identity_gates"] += 1
                append_identity_certificate(certificates, parsed)
                continue
            if pending and parsed.operand not in pending:
                stats["commuted_disjoint_single_qubit_gates"] += sum(len(run) for run in pending.values())
            pending.setdefault(parsed.operand, []).append(parsed)
            continue

        touched = touched_operands(line)
        code = strip_comment(line)
        if not touched or code.startswith(("barrier", "opaque", "gate ")):
            flush_all_pending(output, pending, min_run_length, stats, certificates)
            output.append(line)
            continue
        for operand in sorted(touched):
            flush_pending_operand(output, pending, operand, min_run_length, stats, certificates)
        output.append(line)

    flush_all_pending(output, pending, min_run_length, stats, certificates)
    stats["output_lines"] = len(output)
    return output, stats


def write_certificates(path: Path, certificates: list[dict], input_path: Path, output_path: Path) -> None:
    if not certificates:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for certificate in certificates:
            certificate = {
                "input_file": str(input_path),
                "output_file": str(output_path),
                **certificate,
            }
            handle.write(json.dumps(certificate, sort_keys=True) + "\n")


def rewrite_file(input_path: Path, output_path: Path, min_run_length: int, commute_disjoint: bool, certificate_log: Path | None = None) -> dict[str, int | str]:
    lines = input_path.read_text(encoding="utf-8").splitlines()
    certificates: list[dict] | None = [] if certificate_log else None
    if commute_disjoint:
        rewritten, stats = rewrite_lines_commuting_disjoint(lines, min_run_length, certificates)
    else:
        rewritten, stats = rewrite_lines(lines, min_run_length, certificates)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")
    if certificate_log and certificates is not None:
        write_certificates(certificate_log, certificates, input_path, output_path)
        stats["certificate_entries"] = len(certificates)
    return {"input": str(input_path), "output": str(output_path), **stats}


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
    parser.add_argument("--min-run-length", type=int, default=2)
    parser.add_argument(
        "--commute-disjoint",
        action="store_true",
        help="Allow 1Q runs to accumulate across operations touching other qubits",
    )
    parser.add_argument("--certificate-log", type=Path, help="Append JSONL local rewrite certificates to this path")
    args = parser.parse_args(argv)

    input_files = discover_inputs(args.inputs)
    if not input_files:
        raise SystemExit("No .qasm inputs found")
    if args.certificate_log and args.certificate_log.exists():
        args.certificate_log.unlink()

    for input_path in input_files:
        output_path = args.output_dir / input_path.name
        stats = rewrite_file(input_path, output_path, args.min_run_length, args.commute_disjoint, args.certificate_log)
        print(
            f"{stats['input']} -> {stats['output']}: "
            f"runs={stats['resynthesized_runs']} "
            f"identity_gates={stats['removed_identity_gates']} "
            f"removed_1q={stats['removed_single_qubit_gates']} "
            f"commuted_disjoint={stats.get('commuted_disjoint_single_qubit_gates', 0)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
