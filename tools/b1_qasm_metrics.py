#!/usr/bin/env python3
"""Compute lightweight OpenQASM 2.0 metrics for B1 circuit-compression work."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


QREG_RE = re.compile(r"^qreg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]\s*;")
CREG_RE = re.compile(r"^creg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]\s*;")
GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s+(.+);$")
MEASURE_RE = re.compile(r"^measure\s+(.+?)\s*->\s*(.+);$")
QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")

T_EQUIVALENTS = {
    "t": 1,
    "tdg": 1,
    "ccx": 7,
    "cu1": 2,
    "crz": 2,
}

TWO_QUBIT_GATES = {
    "cx",
    "cz",
    "cy",
    "ch",
    "swap",
    "cu1",
    "crz",
    "cry",
    "crx",
    "rxx",
    "ryy",
    "rzz",
}

THREE_OR_MORE_QUBIT_GATES = {
    "ccx",
    "cswap",
}

STRUCTURAL_PREFIXES = (
    "OPENQASM",
    "include",
    "barrier",
    "opaque",
    "gate ",
)


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def extract_qubits(operand_text: str) -> list[str]:
    return [f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(operand_text)]


def parse_qasm(path: Path) -> dict:
    qregs: dict[str, int] = {}
    cregs: dict[str, int] = {}
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
        creg_match = CREG_RE.match(line)
        if creg_match:
            cregs[creg_match.group(1)] = int(creg_match.group(2))
            continue
        measure_match = MEASURE_RE.match(line)
        if measure_match:
            qubits = extract_qubits(measure_match.group(1))
            operations.append(
                {
                    "gate": "measure",
                    "qubits": qubits,
                    "line": line_number,
                    "raw": line,
                }
            )
            continue
        gate_match = GATE_RE.match(line)
        if gate_match:
            gate = gate_match.group(1).lower()
            qubits = extract_qubits(gate_match.group(2))
            operations.append(
                {
                    "gate": gate,
                    "qubits": qubits,
                    "line": line_number,
                    "raw": line,
                }
            )
            continue
        unsupported.append((line_number, line))

    if unsupported:
        details = ", ".join(f"line {line}: {text}" for line, text in unsupported[:5])
        raise ValueError(f"Unsupported OpenQASM statements in {path}: {details}")

    return {"qregs": qregs, "cregs": cregs, "operations": operations}


def schedule_depth(operations: list[dict], include_measurements: bool = True) -> tuple[int, int]:
    qubit_layer: dict[str, int] = {}
    t_qubit_layer: dict[str, int] = {}
    max_layer = 0
    max_t_layer = 0

    for op in operations:
        gate = op["gate"]
        qubits = op["qubits"]
        if gate == "measure" and not include_measurements:
            continue
        if not qubits:
            continue

        start_layer = max(qubit_layer.get(qubit, 0) for qubit in qubits) + 1
        for qubit in qubits:
            qubit_layer[qubit] = start_layer
        max_layer = max(max_layer, start_layer)

        t_cost = T_EQUIVALENTS.get(gate, 0)
        if t_cost:
            start_t_layer = max(t_qubit_layer.get(qubit, 0) for qubit in qubits) + t_cost
            for qubit in qubits:
                t_qubit_layer[qubit] = start_t_layer
            max_t_layer = max(max_t_layer, start_t_layer)

    return max_layer, max_t_layer


def classify_gate(gate: str, arity: int) -> str:
    if gate == "measure":
        return "measurement"
    if gate in THREE_OR_MORE_QUBIT_GATES or arity >= 3:
        return "multi_qubit"
    if gate in TWO_QUBIT_GATES or arity == 2:
        return "two_qubit"
    return "single_qubit"


def compute_metrics(path: Path, hardware_profile: dict | None = None) -> dict:
    parsed = parse_qasm(path)
    operations = parsed["operations"]
    gate_counts: dict[str, int] = {}
    class_counts = {
        "single_qubit": 0,
        "two_qubit": 0,
        "multi_qubit": 0,
        "measurement": 0,
    }
    t_count = 0

    for op in operations:
        gate = op["gate"]
        gate_counts[gate] = gate_counts.get(gate, 0) + 1
        arity = len(op["qubits"])
        gate_class = classify_gate(gate, arity)
        class_counts[gate_class] += 1
        t_count += T_EQUIVALENTS.get(gate, 0)

    logical_depth, t_depth = schedule_depth(operations)
    qubit_count = sum(parsed["qregs"].values())
    classical_bit_count = sum(parsed["cregs"].values())

    metrics = {
        "path": str(path),
        "qubits": qubit_count,
        "classical_bits": classical_bit_count,
        "operation_count": len(operations),
        "gate_counts": dict(sorted(gate_counts.items())),
        "gate_class_counts": class_counts,
        "logical_depth": logical_depth,
        "two_qubit_gate_count": class_counts["two_qubit"] + class_counts["multi_qubit"],
        "two_qubit_or_larger_depth_proxy": logical_depth,
        "t_count_proxy": t_count,
        "t_depth_proxy": t_depth,
    }

    if hardware_profile is not None:
        errors = hardware_profile["gate_errors"]
        idle_error = hardware_profile["idle_error_per_layer"]
        active_qubit_layers = sum(len(op["qubits"]) for op in operations)
        idle_layers = max(qubit_count * logical_depth - active_qubit_layers, 0)
        exposure = (
            class_counts["single_qubit"] * errors["single_qubit"]
            + class_counts["two_qubit"] * errors["two_qubit"]
            + class_counts["multi_qubit"] * errors["two_qubit"] * 2
            + class_counts["measurement"] * errors["measurement"]
            + t_count * errors["t_gate"]
            + idle_layers * idle_error
        )
        metrics["hardware_weighted_error_exposure"] = exposure
        metrics["idle_layer_proxy"] = idle_layers

    return metrics


def load_profiles(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_qasm_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.qasm")))
        elif path.suffix == ".qasm":
            files.append(path)
    return files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="OpenQASM files or directories")
    parser.add_argument(
        "--hardware-profiles",
        type=Path,
        default=Path("benchmarks/hardware_profiles.json"),
        help="JSON hardware profile file",
    )
    parser.add_argument(
        "--profile",
        default="heavy_hex_like_sparse",
        help="Hardware profile name to use for weighted exposure",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args(argv)

    profiles = load_profiles(args.hardware_profiles)
    if args.profile not in profiles:
        available = ", ".join(sorted(profiles))
        raise SystemExit(f"Unknown profile {args.profile!r}. Available: {available}")

    qasm_files = find_qasm_files(args.inputs)
    if not qasm_files:
        raise SystemExit("No .qasm files found")

    results = [compute_metrics(path, profiles[args.profile]) for path in qasm_files]
    payload = {
        "benchmark_id": "B1",
        "profile": args.profile,
        "circuit_count": len(results),
        "results": results,
    }
    indent = 2 if args.pretty else None
    output = json.dumps(payload, indent=indent, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
