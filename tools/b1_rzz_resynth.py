#!/usr/bin/env python3
"""Rewrite CX-RZ-CX interaction windows into native RZZ gates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(\([^)]*\))?\s+(.+);$")
QUBIT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]")


@dataclass(frozen=True)
class ParsedLine:
    raw: str
    gate: str
    params: str
    qubits: tuple[str, ...]
    line_number: int


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def parse_line(line: str, line_number: int) -> ParsedLine | None:
    code = strip_comment(line)
    if code.startswith("measure"):
        return None
    match = GATE_RE.match(code)
    if not match:
        return None
    gate = match.group(1).lower()
    params = match.group(2) or ""
    qubits = tuple(f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(match.group(3)))
    return ParsedLine(raw=line, gate=gate, params=params, qubits=qubits, line_number=line_number)


def is_cx_rz_cx(window: list[ParsedLine]) -> bool:
    first, second, third = window
    if first.gate != "cx" or second.gate != "rz" or third.gate != "cx":
        return False
    if first.qubits != third.qubits or len(first.qubits) != 2:
        return False
    return second.qubits == (first.qubits[1],)


def rzz_line(window: list[ParsedLine]) -> str:
    first, second, _third = window
    control, target = first.qubits
    return f"rzz{second.params} {control},{target};"


def touched_qubits(line: str) -> set[str]:
    code = strip_comment(line)
    if code.startswith("measure") and "->" in code:
        code = code.split("->", 1)[0]
    return {f"{name}[{idx}]" for name, idx in QUBIT_RE.findall(code)}


def rzz_certificate(window: list[ParsedLine], mode: str, skipped: list[ParsedLine] | None = None) -> dict:
    first, second, third = window
    control, target = first.qubits
    skipped = skipped or []
    return {
        "rule": "cx_rz_cx_to_rzz",
        "certificate_type": "local_rewrite_identity_plus_disjoint_commutation",
        "mode": mode,
        "control": control,
        "target": target,
        "angle": second.params,
        "input_line_numbers": [first.line_number, second.line_number, third.line_number],
        "input_gates": [strip_comment(first.raw), strip_comment(second.raw), strip_comment(third.raw)],
        "skipped_disjoint_line_numbers": [item.line_number for item in skipped],
        "skipped_disjoint_gates": [strip_comment(item.raw) for item in skipped],
        "output_gate": rzz_line(window),
        "removed_cx_gates": 2,
        "inserted_rzz_gates": 1,
    }


def find_commuting_window(lines: list[str], start: int, max_scan: int) -> tuple[list[str], int, dict] | None:
    first = parse_line(lines[start], start + 1)
    if first is None or first.gate != "cx" or len(first.qubits) != 2:
        return None

    pair = set(first.qubits)
    target = first.qubits[1]
    skipped_before_rz: list[ParsedLine] = []
    skipped_after_rz: list[ParsedLine] = []
    rz_line_parsed: ParsedLine | None = None
    scanned = 1

    for idx in range(start + 1, min(len(lines), start + max_scan + 1)):
        scanned = idx - start + 1
        parsed = parse_line(lines[idx], idx + 1)
        touched = touched_qubits(lines[idx])
        if parsed is None:
            return None

        if touched.isdisjoint(pair):
            if rz_line_parsed is None:
                skipped_before_rz.append(parsed)
            else:
                skipped_after_rz.append(parsed)
            continue

        if rz_line_parsed is None:
            if parsed.gate == "rz" and parsed.qubits == (target,):
                rz_line_parsed = parsed
                continue
            return None

        if parsed.gate == "cx" and parsed.qubits == first.qubits:
            replacement = [rzz_line([first, rz_line_parsed, parsed])]
            replacement.extend(item.raw for item in skipped_before_rz)
            replacement.extend(item.raw for item in skipped_after_rz)
            certificate = rzz_certificate(
                [first, rz_line_parsed, parsed],
                mode="commute_disjoint",
                skipped=[*skipped_before_rz, *skipped_after_rz],
            )
            return replacement, scanned, certificate

        return None

    return None


def rewrite_lines(lines: list[str], certificates: list[dict] | None = None) -> tuple[list[str], dict[str, int]]:
    output: list[str] = []
    stats = {
        "cx_rz_cx_windows": 0,
        "cx_removed": 0,
        "rz_absorbed": 0,
        "rzz_inserted": 0,
        "input_lines": len(lines),
        "output_lines": 0,
    }
    idx = 0
    while idx < len(lines):
        parsed = parse_line(lines[idx], idx + 1)
        if parsed is None or idx + 2 >= len(lines):
            output.append(lines[idx])
            idx += 1
            continue
        second = parse_line(lines[idx + 1], idx + 2)
        third = parse_line(lines[idx + 2], idx + 3)
        if second is not None and third is not None and is_cx_rz_cx([parsed, second, third]):
            output.append(rzz_line([parsed, second, third]))
            if certificates is not None:
                certificates.append(rzz_certificate([parsed, second, third], mode="adjacent"))
            stats["cx_rz_cx_windows"] += 1
            stats["cx_removed"] += 2
            stats["rz_absorbed"] += 1
            stats["rzz_inserted"] += 1
            idx += 3
            continue
        output.append(lines[idx])
        idx += 1

    stats["output_lines"] = len(output)
    return output, stats


def rewrite_lines_commuting_disjoint(lines: list[str], max_scan: int, certificates: list[dict] | None = None) -> tuple[list[str], dict[str, int]]:
    output: list[str] = []
    stats = {
        "cx_rz_cx_windows": 0,
        "commuting_disjoint_windows": 0,
        "cx_removed": 0,
        "rz_absorbed": 0,
        "rzz_inserted": 0,
        "input_lines": len(lines),
        "output_lines": 0,
    }
    idx = 0
    while idx < len(lines):
        window = find_commuting_window(lines, idx, max_scan)
        if window is not None:
            replacement, consumed, certificate = window
            output.extend(replacement)
            if certificates is not None:
                certificates.append(certificate)
            stats["cx_rz_cx_windows"] += 1
            stats["commuting_disjoint_windows"] += 1
            stats["cx_removed"] += 2
            stats["rz_absorbed"] += 1
            stats["rzz_inserted"] += 1
            idx += consumed
            continue
        output.append(lines[idx])
        idx += 1

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


def rewrite_file(input_path: Path, output_path: Path, commute_disjoint: bool, max_scan: int, certificate_log: Path | None = None) -> dict[str, int | str]:
    lines = input_path.read_text(encoding="utf-8").splitlines()
    certificates: list[dict] | None = [] if certificate_log else None
    if commute_disjoint:
        rewritten, stats = rewrite_lines_commuting_disjoint(lines, max_scan, certificates)
    else:
        rewritten, stats = rewrite_lines(lines, certificates)
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
    parser.add_argument(
        "--commute-disjoint",
        action="store_true",
        help="Allow CX-RZ-CX windows to span operations on disjoint qubits",
    )
    parser.add_argument("--max-scan", type=int, default=80)
    parser.add_argument("--certificate-log", type=Path, help="Append JSONL local rewrite certificates to this path")
    args = parser.parse_args(argv)

    input_files = discover_inputs(args.inputs)
    if not input_files:
        raise SystemExit("No .qasm inputs found")
    if args.certificate_log and args.certificate_log.exists():
        args.certificate_log.unlink()

    for input_path in input_files:
        output_path = args.output_dir / input_path.name
        stats = rewrite_file(input_path, output_path, args.commute_disjoint, args.max_scan, args.certificate_log)
        print(
            f"{stats['input']} -> {stats['output']}: "
            f"windows={stats['cx_rz_cx_windows']} "
            f"commuting_windows={stats.get('commuting_disjoint_windows', 0)} "
            f"cx_removed={stats['cx_removed']} "
            f"rzz_inserted={stats['rzz_inserted']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
