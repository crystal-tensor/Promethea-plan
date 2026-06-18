#!/usr/bin/env python3
"""Replay B1 proof logs and compare reconstructed QASM with pipeline outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
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


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def qasm_files(path: Path) -> list[Path]:
    return sorted(path.rglob("*.qasm"))


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def group_by_input_file(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["input_file"], []).append(row)
    return grouped


def parse_single_qubit(line: str, line_number: int) -> dict | None:
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
    return {"raw": line, "gate": gate, "operand": f"{name}[{idx}]", "line_number": line_number}


def touched_operands(line: str) -> set[str]:
    return {f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(strip_comment(line))}


def event_matches_run(event: dict, run: list[dict]) -> bool:
    return event.get("input_line_numbers") == [item["line_number"] for item in run]


def flush_pending_operand(
    output: list[str],
    pending: dict[str, list[dict]],
    operand: str,
    min_run_length: int,
    events: list[dict],
    event_index: list[int],
    errors: list[str],
    input_path: Path,
) -> None:
    run = pending.pop(operand, [])
    if not run:
        return
    if len(run) < min_run_length:
        output.extend(item["raw"] for item in run)
        return
    if event_index[0] >= len(events):
        errors.append(f"missing 1Q proof event for {input_path}:{[item['line_number'] for item in run]}")
        return
    event = events[event_index[0]]
    if not event_matches_run(event, run):
        errors.append(
            f"1Q proof event mismatch for {input_path}: "
            f"expected lines {[item['line_number'] for item in run]}, got {event.get('input_line_numbers')}"
        )
        return
    output.append(event["output_gate"])
    event_index[0] += 1


def flush_all_pending(
    output: list[str],
    pending: dict[str, list[dict]],
    min_run_length: int,
    events: list[dict],
    event_index: list[int],
    errors: list[str],
    input_path: Path,
) -> None:
    for operand in list(pending):
        flush_pending_operand(output, pending, operand, min_run_length, events, event_index, errors, input_path)


def replay_oneq_file(input_path: Path, output_path: Path, events: list[dict], min_run_length: int, errors: list[str]) -> None:
    lines = input_path.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    pending: dict[str, list[dict]] = {}
    event_index = [0]

    for line_number, line in enumerate(lines, start=1):
        parsed = parse_single_qubit(line, line_number)
        if parsed is not None:
            if parsed["gate"] == "id":
                if event_index[0] >= len(events) or events[event_index[0]].get("rule") != "remove_identity_gate":
                    errors.append(f"missing identity proof event for {input_path}:{line_number}")
                    continue
                event = events[event_index[0]]
                if event.get("input_line_numbers") != [line_number]:
                    errors.append(f"identity proof event mismatch for {input_path}:{line_number}")
                    continue
                event_index[0] += 1
                continue
            if pending and parsed["operand"] not in pending:
                pass
            pending.setdefault(parsed["operand"], []).append(parsed)
            continue

        touched = touched_operands(line)
        code = strip_comment(line)
        if not touched or code.startswith(("barrier", "opaque", "gate ")):
            flush_all_pending(output, pending, min_run_length, events, event_index, errors, input_path)
            output.append(line)
            continue
        for operand in sorted(touched):
            flush_pending_operand(output, pending, operand, min_run_length, events, event_index, errors, input_path)
        output.append(line)

    flush_all_pending(output, pending, min_run_length, events, event_index, errors, input_path)
    if event_index[0] != len(events):
        errors.append(f"unused 1Q proof events for {input_path}: {len(events) - event_index[0]}")
    compare_output(input_path, output_path, output, errors)


def compare_output(input_path: Path, output_path: Path, replayed: list[str], errors: list[str]) -> None:
    if not output_path.exists():
        errors.append(f"missing output file for replay: {output_path}")
        return
    actual = output_path.read_text(encoding="utf-8").splitlines()
    if replayed == actual:
        return
    limit = min(len(replayed), len(actual))
    for idx in range(limit):
        if replayed[idx] != actual[idx]:
            errors.append(
                f"replay mismatch for {input_path} -> {output_path} at output line {idx + 1}: "
                f"{replayed[idx]!r} != {actual[idx]!r}"
            )
            return
    errors.append(
        f"replay length mismatch for {input_path} -> {output_path}: "
        f"{len(replayed)} != {len(actual)}"
    )


def parse_gate(line: str, line_number: int) -> dict | None:
    code = strip_comment(line)
    if code.startswith("measure"):
        return None
    match = GATE_RE.match(code)
    if not match:
        return None
    gate = match.group(1).lower()
    params = match.group(2) or ""
    qubits = tuple(f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(match.group(3)))
    return {"raw": line, "gate": gate, "params": params, "qubits": qubits, "line_number": line_number}


def replay_rzz_file(input_path: Path, output_path: Path, events: list[dict], errors: list[str]) -> None:
    lines = input_path.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    events_by_start = {int(event["input_line_numbers"][0]): event for event in events}
    consumed = 0
    idx = 0
    while idx < len(lines):
        line_number = idx + 1
        event = events_by_start.get(line_number)
        if event is None:
            output.append(lines[idx])
            idx += 1
            continue
        input_numbers = [int(value) for value in event["input_line_numbers"]]
        skipped_numbers = [int(value) for value in event.get("skipped_disjoint_line_numbers", [])]
        consumed_numbers = sorted([*input_numbers, *skipped_numbers])
        expected_range = list(range(line_number, max(consumed_numbers) + 1))
        if consumed_numbers != expected_range:
            errors.append(f"RZZ replay event does not cover a contiguous scan window at {input_path}:{line_number}")
            return
        gates = [strip_comment(lines[number - 1]) for number in input_numbers]
        if gates != event.get("input_gates"):
            errors.append(f"RZZ replay input gate mismatch at {input_path}:{line_number}")
            return
        output.append(event["output_gate"])
        output.extend(lines[number - 1] for number in skipped_numbers)
        idx = max(consumed_numbers)
        consumed += 1
    if consumed != len(events):
        errors.append(f"unused RZZ proof events for {input_path}: {len(events) - consumed}")
    compare_output(input_path, output_path, output, errors)


def infer_stage_dirs_from_log(path: Path) -> tuple[Path, Path]:
    rows = read_jsonl(path)
    if not rows:
        raise ValueError(f"cannot infer stage directories from empty proof log: {path}")
    return Path(rows[0]["input_file"]).parent, Path(rows[0]["output_file"]).parent


def replay_summary(summary_path: Path, min_run_length: int) -> dict:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    proof_logs = summary["proof_logs"]
    errors: list[str] = []
    stages: list[dict] = []

    oneq_log = Path(proof_logs["single_qubit_block_resynthesis"]["path"])
    oneq_input_dir, oneq_output_dir = infer_stage_dirs_from_log(oneq_log)
    oneq_events = group_by_input_file(read_jsonl(oneq_log))
    for input_path in qasm_files(oneq_input_dir):
        output_path = oneq_output_dir / input_path.name
        replay_oneq_file(input_path, output_path, oneq_events.get(str(input_path), []), min_run_length, errors)
    stages.append(
        {
            "stage": "single_qubit_block_resynthesis",
            "input_dir": str(oneq_input_dir),
            "output_dir": str(oneq_output_dir),
            "files_checked": len(qasm_files(oneq_input_dir)),
            "proof_events": sum(len(events) for events in oneq_events.values()),
        }
    )

    rzz_logs = proof_logs["rzz_window_resynthesis"]
    current_input_dir = oneq_output_dir
    for pass_info in rzz_logs:
        pass_index = int(pass_info["pass"])
        output_dir = Path(summary["rzz_passes"][pass_index - 1]["output_dir"])
        proof_log = Path(pass_info["path"])
        rzz_events = group_by_input_file(read_jsonl(proof_log))
        for input_path in qasm_files(current_input_dir):
            output_path = output_dir / input_path.name
            replay_rzz_file(input_path, output_path, rzz_events.get(str(input_path), []), errors)
        stages.append(
            {
                "stage": f"rzz_pass_{pass_index}",
                "input_dir": str(current_input_dir),
                "output_dir": str(output_dir),
                "files_checked": len(qasm_files(current_input_dir)),
                "proof_events": sum(len(events) for events in rzz_events.values()),
            }
        )
        current_input_dir = output_dir

    return {
        "summary": str(summary_path),
        "passed": not errors,
        "errors": errors,
        "stages": stages,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--min-run-length", type=int, default=2)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    report = replay_summary(args.summary, args.min_run_length)
    text = json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
