#!/usr/bin/env python3
"""Audit B1 local rewrite proof logs against a pipeline summary."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def touched_qubits(gate: str) -> set[str]:
    return {f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(gate)}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL: {exc}") from exc
    return rows


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def read_input_lines(path: Path, line_cache: dict[Path, list[str]]) -> list[str] | None:
    if path not in line_cache:
        if not path.exists():
            return None
        line_cache[path] = path.read_text(encoding="utf-8").splitlines()
    return line_cache[path]


def check_input_lines(entry: dict, errors: list[str], line_cache: dict[Path, list[str]]) -> None:
    input_path = Path(entry["input_file"])
    require(input_path.exists(), f"missing input file: {input_path}", errors)
    lines = read_input_lines(input_path, line_cache)
    if lines is None:
        return
    line_numbers = entry.get("input_line_numbers", [])
    gates = entry.get("input_gates", [])
    require(len(line_numbers) == len(gates), f"line/gate length mismatch in {input_path}", errors)
    for line_number, gate in zip(line_numbers, gates):
        require(1 <= int(line_number) <= len(lines), f"line number out of range: {input_path}:{line_number}", errors)
        if 1 <= int(line_number) <= len(lines):
            actual = strip_comment(lines[int(line_number) - 1])
            require(actual == gate, f"gate mismatch at {input_path}:{line_number}: {actual!r} != {gate!r}", errors)


def audit_oneq(path: Path, expected_entries: int, errors: list[str], line_cache: dict[Path, list[str]]) -> dict:
    rows = read_jsonl(path)
    require(len(rows) == expected_entries, f"1Q proof count mismatch: {path} has {len(rows)}, expected {expected_entries}", errors)
    rules: dict[str, int] = {}
    for entry in rows:
        rule = entry.get("rule")
        rules[rule] = rules.get(rule, 0) + 1
        require(rule in {"single_qubit_run_to_u3", "remove_identity_gate"}, f"unknown 1Q rule: {rule}", errors)
        check_input_lines(entry, errors, line_cache)
        if rule == "single_qubit_run_to_u3":
            require(str(entry.get("output_gate", "")).startswith("u3("), f"1Q output is not u3: {entry.get('output_gate')}", errors)
            require(len(entry.get("input_line_numbers", [])) >= 2, "1Q run proof has fewer than 2 input gates", errors)
        if rule == "remove_identity_gate":
            require(entry.get("output_gate") is None, "identity removal should have null output_gate", errors)
    return {"path": str(path), "entries": len(rows), "rules": rules}


def audit_rzz(path: Path, expected_entries: int, errors: list[str], line_cache: dict[Path, list[str]]) -> dict:
    rows = read_jsonl(path)
    require(len(rows) == expected_entries, f"RZZ proof count mismatch: {path} has {len(rows)}, expected {expected_entries}", errors)
    modes: dict[str, int] = {}
    for entry in rows:
        mode = entry.get("mode")
        modes[mode] = modes.get(mode, 0) + 1
        require(entry.get("rule") == "cx_rz_cx_to_rzz", f"unknown RZZ rule: {entry.get('rule')}", errors)
        require(str(entry.get("output_gate", "")).startswith("rzz"), f"RZZ output is not rzz: {entry.get('output_gate')}", errors)
        require(len(entry.get("input_line_numbers", [])) == 3, "RZZ proof must have exactly 3 input gates", errors)
        check_input_lines(entry, errors, line_cache)
        pair = {entry.get("control"), entry.get("target")}
        skipped_numbers = entry.get("skipped_disjoint_line_numbers", [])
        skipped_gates = entry.get("skipped_disjoint_gates", [])
        require(len(skipped_numbers) == len(skipped_gates), "skipped line/gate length mismatch", errors)
        for gate in skipped_gates:
            require(touched_qubits(gate).isdisjoint(pair), f"skipped gate is not disjoint from RZZ pair: {gate}", errors)
    return {"path": str(path), "entries": len(rows), "modes": modes}


def audit_summary(summary_path: Path) -> dict:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    line_cache: dict[Path, list[str]] = {}
    proof_logs = summary.get("proof_logs", {})
    local = summary.get("local_certificates", {})

    oneq_expected = int(local["single_qubit_block_resynthesis"]["resynthesized_runs"]) + int(
        local["single_qubit_block_resynthesis"]["identity_gates_removed"]
    )
    oneq_path = Path(proof_logs["single_qubit_block_resynthesis"]["path"])
    require(int(proof_logs["single_qubit_block_resynthesis"]["entries"]) == oneq_expected, "summary 1Q proof count mismatch", errors)
    oneq_report = audit_oneq(oneq_path, oneq_expected, errors, line_cache)

    rzz_expected = int(local["rzz_window_resynthesis"]["windows"])
    rzz_reports = []
    rzz_total = 0
    for rzz_log in proof_logs["rzz_window_resynthesis"]:
        entries = int(rzz_log["entries"])
        rzz_total += entries
        rzz_reports.append(audit_rzz(Path(rzz_log["path"]), entries, errors, line_cache))
    require(rzz_total == rzz_expected, f"summary RZZ proof count mismatch: {rzz_total} != {rzz_expected}", errors)

    return {
        "summary": str(summary_path),
        "passed": not errors,
        "errors": errors,
        "oneq": oneq_report,
        "rzz": rzz_reports,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    report = audit_summary(args.summary)
    text = json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
