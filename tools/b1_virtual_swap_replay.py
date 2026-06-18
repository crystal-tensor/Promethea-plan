#!/usr/bin/env python3
"""Replay B1 virtual-SWAP proof logs and compare reconstructed QASM outputs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
QREG_RE = re.compile(r"^qreg\s+([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]\s*;")
MEASURE_RE = re.compile(r"^measure\s+(.+?)\s*->\s*(.+);$")
QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def qasm_files(path: Path) -> list[Path]:
    return sorted(path.rglob("*.qasm"))


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                row = json.loads(line)
                row["_proof_line_number"] = line_number
                rows.append(row)
    return rows


def group_by_input_file(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["input_file"], []).append(row)
    return grouped


def qreg_size(lines: list[str]) -> tuple[str, int]:
    for line in lines:
        match = QREG_RE.match(strip_comment(line))
        if match:
            return match.group(1), int(match.group(2))
    raise ValueError("No qreg declaration found")


def parse_gate(line: str) -> dict | None:
    code = strip_comment(line)
    if not code or code.startswith("measure"):
        return None
    match = GATE_RE.match(code)
    if not match:
        return None
    return {
        "gate": match.group(1).lower(),
        "qubits": tuple(f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(match.group(3))),
        "raw": code,
    }


def is_swap_macro(first: dict, second: dict, third: dict) -> bool:
    if first["gate"] != "cx" or second["gate"] != "cx" or third["gate"] != "cx":
        return False
    if len(first["qubits"]) != 2 or len(second["qubits"]) != 2 or len(third["qubits"]) != 2:
        return False
    left, right = first["qubits"]
    return second["qubits"] == (right, left) and third["qubits"] == (left, right)


def remap_qubit(token: str, wire_map: dict[str, str]) -> str:
    return wire_map.get(token, token)


def remap_operands(text: str, wire_map: dict[str, str]) -> str:
    def replace(match: re.Match) -> str:
        token = f"{match.group(1)}[{match.group(2)}]"
        return remap_qubit(token, wire_map)

    return QUBIT_RE.sub(replace, text)


def remap_gate_line(line: str, wire_map: dict[str, str]) -> str:
    code = strip_comment(line)
    comment = ""
    if "//" in line:
        comment = " //" + line.split("//", 1)[1].strip()
    measure = MEASURE_RE.match(code)
    if measure:
        return f"measure {remap_operands(measure.group(1), wire_map)} -> {measure.group(2)};{comment}"
    gate = GATE_RE.match(code)
    if gate:
        return f"{gate.group(1)}{gate.group(2) or ''} {remap_operands(gate.group(3), wire_map)};{comment}"
    return line


def event_by_start_line(events: list[dict], errors: list[str], source: Path) -> dict[int, dict]:
    indexed: dict[int, dict] = {}
    for event in events:
        numbers = event.get("input_line_numbers")
        if not isinstance(numbers, list) or len(numbers) != 3:
            errors.append(f"{source}: malformed input_line_numbers in proof line {event.get('_proof_line_number')}")
            continue
        start = int(numbers[0])
        if start in indexed:
            errors.append(f"{source}: duplicate proof event at input line {start}")
            continue
        indexed[start] = event
    return indexed


def replay_file(source: Path, target: Path, events: list[dict]) -> dict:
    errors: list[str] = []
    lines = source.read_text(encoding="utf-8").splitlines()
    qreg_name, size = qreg_size(lines)
    wire_map = {f"{qreg_name}[{index}]": f"{qreg_name}[{index}]" for index in range(size)}
    events_by_line = event_by_start_line(events, errors, source)
    output: list[str] = []
    consumed_starts: set[int] = set()
    idx = 0
    while idx < len(lines):
        line_number = idx + 1
        event = events_by_line.get(line_number)
        if event:
            window = lines[idx : idx + 3]
            gates = [parse_gate(line) for line in window]
            expected_numbers = [line_number, line_number + 1, line_number + 2]
            if event.get("input_line_numbers") != expected_numbers:
                errors.append(f"{source}:{line_number}: non-contiguous proof event")
            if [strip_comment(line) for line in window] != event.get("input_gates"):
                errors.append(f"{source}:{line_number}: input gate text does not match proof log")
            if not all(gates) or not is_swap_macro(gates[0], gates[1], gates[2]):
                errors.append(f"{source}:{line_number}: proof event does not point to a cx-cx-cx SWAP macro")
                idx += 1
                continue
            left, right = gates[0]["qubits"]
            if event.get("left") != left or event.get("right") != right:
                errors.append(f"{source}:{line_number}: proof left/right does not match parsed SWAP")
            wire_map[left], wire_map[right] = wire_map[right], wire_map[left]
            if dict(sorted(wire_map.items())) != event.get("wire_map_after"):
                errors.append(f"{source}:{line_number}: wire_map_after does not match replayed permutation")
            if event.get("removed_cx_gates") != 3:
                errors.append(f"{source}:{line_number}: removed_cx_gates should be 3")
            consumed_starts.add(line_number)
            idx += 3
            continue
        output.append(remap_gate_line(lines[idx], wire_map))
        idx += 1
    missing_starts = sorted(set(events_by_line) - consumed_starts)
    for start in missing_starts:
        errors.append(f"{source}:{start}: proof event was not consumed during replay")

    expected_output = target.read_text(encoding="utf-8").splitlines() if target.exists() else []
    output_matches = output == expected_output
    if not target.exists():
        errors.append(f"{target}: missing replay target output")
    elif not output_matches:
        errors.append(f"{target}: replayed QASM differs from generated output")

    return {
        "input": str(source),
        "output": str(target),
        "proof_events": len(events),
        "consumed_events": len(consumed_starts),
        "output_matches": output_matches,
        "errors": errors,
    }


def build_report(input_dir: Path, output_dir: Path, proof_log: Path) -> dict:
    rows = read_jsonl(proof_log)
    grouped = group_by_input_file(rows)
    circuit_rows = []
    for source in qasm_files(input_dir):
        relative = source.relative_to(input_dir)
        target = output_dir / relative
        events = grouped.get(str(source.resolve()), [])
        circuit_rows.append(replay_file(source.resolve(), target.resolve(), events))
    proof_files = set(grouped)
    input_files = {str(path.resolve()) for path in qasm_files(input_dir)}
    orphan_files = sorted(proof_files - input_files)
    errors = [error for row in circuit_rows for error in row["errors"]]
    errors.extend(f"proof log references missing input file: {path}" for path in orphan_files)
    output_mismatches = sum(1 for row in circuit_rows if not row["output_matches"])
    replayed_events = sum(row["consumed_events"] for row in circuit_rows)
    return {
        "benchmark_id": "B1",
        "problem_id": 25,
        "title": "B1 virtual SWAP proof-log replay",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "report_status": "passed" if not errors else "failed",
        "input_dir": str(input_dir.resolve()),
        "output_dir": str(output_dir.resolve()),
        "proof_log": str(proof_log.resolve()),
        "circuit_count": len(circuit_rows),
        "proof_events": len(rows),
        "replayed_events": replayed_events,
        "output_mismatches": output_mismatches,
        "orphan_proof_files": orphan_files,
        "error_count": len(errors),
        "errors": errors[:50],
        "circuits": circuit_rows,
    }


def markdown(report: dict) -> str:
    lines = [
        "# B1 Virtual SWAP Proof-Log Replay v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['report_status']}**",
        "",
        "## Summary",
        "",
        f"- Circuits: {report['circuit_count']}",
        f"- Proof events: {report['proof_events']}",
        f"- Replayed events: {report['replayed_events']}",
        f"- Output mismatches: {report['output_mismatches']}",
        f"- Error count: {report['error_count']}",
        "",
        "## Per-Circuit Replay",
        "",
        "| Circuit | Proof events | Consumed | Output matches | Errors |",
        "|---|---:|---:|---|---:|",
    ]
    for row in report["circuits"]:
        circuit = Path(row["input"]).name
        lines.append(
            f"| `{circuit}` | {row['proof_events']} | {row['consumed_events']} | "
            f"{row['output_matches']} | {len(row['errors'])} |"
        )
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in report["errors"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("results/b1_heavyhex_end_to_end_30_level1_work/03_b1_heavyhex_d3_level1"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/b1_virtual_swap_elimination_level1_work/01_virtual_swap_eliminated"))
    parser.add_argument("--proof-log", type=Path, default=Path("results/b1_virtual_swap_elimination_level1/virtual_swap_elimination_proofs.jsonl"))
    parser.add_argument("--json-output", type=Path, default=Path("research/B1_virtual_swap_replay_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B1_virtual_swap_replay_report.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(args.input_dir, args.output_dir, args.proof_log)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report["report_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
