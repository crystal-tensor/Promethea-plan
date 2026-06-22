#!/usr/bin/env python3
"""Parser-readiness gate for the B1/B7 cone_01 OpenQASM 3 artifact.

T-B1-004bu exported a modern OpenQASM 3 candidate. This gate checks that the
artifact is locally parseable with a strict project parser and records whether
the installed Qiskit environment can load OpenQASM 3 directly.

In the current local environment Qiskit core is present, but the optional
qiskit_qasm3_import package is absent. The gate therefore accepts only the
local parse/readiness artifact and explicitly refuses to claim Qiskit loader
success, replay, equivalence, local-U3 pricing, or B7 credit.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

from b1_b7_cone01_carrier_absorption_inventory_gate import (
    PROXY_T_PER_OCCURRENCE,
    REQUIRED_OCCURRENCE_REMOVALS,
    display_path,
    load_json,
    write_json,
    write_text,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_RESULT = ROOT / "results" / "B1_B7_cone01_openqasm3_candidate_export_gate_v0.json"
JSON_OUT = ROOT / "results" / "B1_B7_cone01_openqasm3_parser_readiness_gate_v0.json"
MD_OUT = ROOT / "research" / "B1_B7_cone01_openqasm3_parser_readiness_gate.md"

METHOD = "b1_b7_cone01_openqasm3_parser_readiness_gate_v0"
STATUS = "cone01_openqasm3_local_parse_passed_qiskit_loader_dependency_missing"
MODEL_STATUS = "local_openqasm3_parse_passes_but_qiskit_loader_optional_dependency_missing"

HEADER_RE = re.compile(r"^OPENQASM 3\.0;$")
INCLUDE_RE = re.compile(r'^include "stdgates\.inc";$')
QUBIT_RE = re.compile(r"^qubit\[(\d+)\]\s+([A-Za-z_]\w*);$")
BIT_RE = re.compile(r"^bit\[(\d+)\]\s+([A-Za-z_]\w*);$")
U_RE = re.compile(r"^U\(([^()]*)\)\s+q\[(\d+)\];$")
RZ_RE = re.compile(r"^rz\(([^()]*)\)\s+q\[(\d+)\];$", re.IGNORECASE)
CX_RE = re.compile(r"^cx\s+q\[(\d+)\]\s*,\s*q\[(\d+)\];$", re.IGNORECASE)
MEASURE_RE = re.compile(r"^c\[(\d+)\]\s*=\s*measure\s+q\[(\d+)\];$")
NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
PI_EXPR_RE = re.compile(r"^[+-]?(?:\d+\*)?pi(?:/\d+)?$")


def argument_is_supported(expr: str) -> bool:
    expr = expr.strip()
    return bool(NUMBER_RE.match(expr) or PI_EXPR_RE.match(expr))


def parse_local_qasm3(text: str) -> dict[str, Any]:
    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    counts = {"U": 0, "rz": 0, "cx": 0, "measure": 0, "other_operation": 0}
    qubit_count: int | None = None
    bit_count: int | None = None
    qubit_name: str | None = None
    bit_name: str | None = None

    lines = text.splitlines()
    if len(lines) < 4:
        errors.append("too_few_lines")
    if not lines or not HEADER_RE.match(lines[0].strip()):
        errors.append("missing_openqasm3_header")
    if len(lines) < 2 or not INCLUDE_RE.match(lines[1].strip()):
        errors.append("missing_stdgates_include")

    for line_number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if line_number == 1 or line_number == 2:
            continue
        qdecl = QUBIT_RE.match(line)
        if qdecl:
            qubit_count = int(qdecl.group(1))
            qubit_name = qdecl.group(2)
            rows.append({"line": line_number, "kind": "qubit_decl", "width": qubit_count})
            continue
        bdecl = BIT_RE.match(line)
        if bdecl:
            bit_count = int(bdecl.group(1))
            bit_name = bdecl.group(2)
            rows.append({"line": line_number, "kind": "bit_decl", "width": bit_count})
            continue

        u_match = U_RE.match(line)
        if u_match:
            args = [arg.strip() for arg in u_match.group(1).split(",")]
            qubit = int(u_match.group(2))
            if len(args) != 3 or not all(argument_is_supported(arg) for arg in args):
                errors.append(f"line_{line_number}_unsupported_U_arguments")
            if qubit_count is not None and not (0 <= qubit < qubit_count):
                errors.append(f"line_{line_number}_qubit_index_out_of_range")
            counts["U"] += 1
            rows.append({"line": line_number, "kind": "U", "qubits": [qubit]})
            continue

        rz_match = RZ_RE.match(line)
        if rz_match:
            qubit = int(rz_match.group(2))
            if not argument_is_supported(rz_match.group(1)):
                errors.append(f"line_{line_number}_unsupported_rz_argument")
            if qubit_count is not None and not (0 <= qubit < qubit_count):
                errors.append(f"line_{line_number}_qubit_index_out_of_range")
            counts["rz"] += 1
            rows.append({"line": line_number, "kind": "rz", "qubits": [qubit]})
            continue

        cx_match = CX_RE.match(line)
        if cx_match:
            control = int(cx_match.group(1))
            target = int(cx_match.group(2))
            if control == target:
                errors.append(f"line_{line_number}_cx_self_loop")
            for qubit in [control, target]:
                if qubit_count is not None and not (0 <= qubit < qubit_count):
                    errors.append(f"line_{line_number}_qubit_index_out_of_range")
            counts["cx"] += 1
            rows.append({"line": line_number, "kind": "cx", "qubits": [control, target]})
            continue

        measure_match = MEASURE_RE.match(line)
        if measure_match:
            bit = int(measure_match.group(1))
            qubit = int(measure_match.group(2))
            if bit_count is not None and not (0 <= bit < bit_count):
                errors.append(f"line_{line_number}_bit_index_out_of_range")
            if qubit_count is not None and not (0 <= qubit < qubit_count):
                errors.append(f"line_{line_number}_qubit_index_out_of_range")
            counts["measure"] += 1
            rows.append({"line": line_number, "kind": "measure", "qubits": [qubit], "bits": [bit]})
            continue

        counts["other_operation"] += 1
        errors.append(f"line_{line_number}_unparsed_statement")

    if qubit_name != "q" or qubit_count != 19:
        errors.append("qubit_declaration_mismatch")
    if bit_name != "c" or bit_count != 1:
        errors.append("bit_declaration_mismatch")
    if "qelib1.inc" in text or re.search(r"(^|\n)(qreg|creg)\s", text):
        errors.append("legacy_declaration_present")
    if re.search(r"(^|\n)u3\(", text, re.IGNORECASE):
        errors.append("legacy_u3_present")
    if "->" in text:
        errors.append("legacy_measure_arrow_present")
    if rows and rows[-1].get("kind") != "measure":
        errors.append("final_statement_is_not_measure")

    return {
        "errors": errors,
        "counts": counts,
        "qubit_count": qubit_count,
        "bit_count": bit_count,
        "statement_count": len([line for line in lines if line.strip()]),
        "operation_row_count": sum(counts.values()),
        "first_operation_line": next((row["line"] for row in rows if row["kind"] not in {"qubit_decl", "bit_decl"}), None),
        "last_operation_kind": rows[-1]["kind"] if rows else None,
    }


def qiskit_loader_probe(qasm_text: str) -> dict[str, Any]:
    qiskit_available = importlib.util.find_spec("qiskit") is not None
    importer_available = importlib.util.find_spec("qiskit_qasm3_import") is not None
    probe: dict[str, Any] = {
        "qiskit_available": qiskit_available,
        "qiskit_qasm3_import_available": importer_available,
        "qiskit_loader_attempted": qiskit_available,
        "qiskit_loader_passed": False,
        "qiskit_loader_status": "not_attempted",
        "qiskit_loader_error_type": None,
        "qiskit_loader_error_message": None,
        "qiskit_num_qubits": None,
        "qiskit_num_clbits": None,
        "qiskit_count_ops": None,
        "qiskit_depth": None,
    }
    if not qiskit_available:
        probe["qiskit_loader_status"] = "qiskit_missing"
        return probe
    try:
        from qiskit import qasm3

        circuit = qasm3.loads(qasm_text)
        probe.update(
            {
                "qiskit_loader_passed": True,
                "qiskit_loader_status": "parsed",
                "qiskit_num_qubits": int(circuit.num_qubits),
                "qiskit_num_clbits": int(circuit.num_clbits),
                "qiskit_count_ops": {key: int(value) for key, value in circuit.count_ops().items()},
                "qiskit_depth": int(circuit.depth()),
            }
        )
    except Exception as exc:  # Keep the dependency boundary auditable.
        probe.update(
            {
                "qiskit_loader_status": (
                    "optional_dependency_missing" if not importer_available else "parse_failed"
                ),
                "qiskit_loader_error_type": type(exc).__name__,
                "qiskit_loader_error_message": str(exc).splitlines()[0][:240],
            }
        )
    return probe


def build_payload() -> dict[str, Any]:
    source = load_json(SOURCE_RESULT)
    qasm_path = ROOT / source["summary"]["openqasm3_candidate_path"]
    qasm_text = qasm_path.read_text(encoding="utf-8")
    local = parse_local_qasm3(qasm_text)
    qiskit_probe = qiskit_loader_probe(qasm_text)
    export_summary = source["summary"]
    accepted_removed = 0
    expected_counts = {"U": 487, "rz": 601, "cx": 789, "measure": 1, "other_operation": 0}
    local_parse_passed = not local["errors"] and local["counts"] == expected_counts
    summary = {
        "source_method": source.get("method"),
        "source_openqasm3_result": display_path(SOURCE_RESULT),
        "openqasm3_candidate_path": display_path(qasm_path),
        "local_parser_passed": local_parse_passed,
        "local_parser_error_count": len(local["errors"]),
        "local_parser_operation_counts": local["counts"],
        "expected_operation_counts": expected_counts,
        "operation_counts_match_export": local["counts"] == expected_counts,
        "qubit_count": local["qubit_count"],
        "bit_count": local["bit_count"],
        "statement_count": local["statement_count"],
        "operation_row_count": local["operation_row_count"],
        "first_operation_line": local["first_operation_line"],
        "last_operation_kind": local["last_operation_kind"],
        "qiskit_available": qiskit_probe["qiskit_available"],
        "qiskit_qasm3_import_available": qiskit_probe["qiskit_qasm3_import_available"],
        "qiskit_loader_attempted": qiskit_probe["qiskit_loader_attempted"],
        "qiskit_loader_passed": qiskit_probe["qiskit_loader_passed"],
        "qiskit_loader_status": qiskit_probe["qiskit_loader_status"],
        "qiskit_loader_error_type": qiskit_probe["qiskit_loader_error_type"],
        "qiskit_loader_error_message": qiskit_probe["qiskit_loader_error_message"],
        "accepted_local_openqasm3_parse_artifact_count": 1 if local_parse_passed else 0,
        "accepted_qiskit_loader_parse_artifact_count": 1 if qiskit_probe["qiskit_loader_passed"] else 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": accepted_removed,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": max(0, REQUIRED_OCCURRENCE_REMOVALS - accepted_removed),
        "missing_proxy_t_after_gate": max(
            0,
            (REQUIRED_OCCURRENCE_REMOVALS - accepted_removed) * PROXY_T_PER_OCCURRENCE,
        ),
        "local_parse_claimed": local_parse_passed,
        "qiskit_loader_parse_claimed": qiskit_probe["qiskit_loader_passed"],
        "full_circuit_replay_claimed": False,
        "local_u3_pricing_accepted": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "source_export_sha256": export_summary.get("openqasm3_sha256"),
        "validation_error_count": 0,
    }
    validation_errors = validate_payload(summary, local, qiskit_probe)
    summary["validation_error_count"] = len(validation_errors)
    return {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "workload": source.get("workload", "qasmbench_medium_exact/gcm_h6.qasm"),
        "source_openqasm3_export_result": display_path(SOURCE_RESULT),
        "openqasm3_candidate_qasm": display_path(qasm_path),
        "summary": summary,
        "local_parser_errors": local["errors"],
        "qiskit_loader_probe": qiskit_probe,
        "validation_errors": validation_errors,
        "claim_boundary": {
            "supported_claim": (
                "The OpenQASM 3 candidate passes the project's strict local parser and count checks."
            ),
            "unsupported_claims": [
                "The current environment has not passed Qiskit's OpenQASM 3 loader because qiskit_qasm3_import is missing.",
                "The local parse is not a full-circuit replay proof.",
                "The local parse does not price or eliminate local-U3 burden.",
                "The local parse does not create B7 occurrence, proxy-T, or space-time-volume credit.",
            ],
            "local_parse_claimed": local_parse_passed,
            "qiskit_loader_parse_claimed": qiskit_probe["qiskit_loader_passed"],
            "full_circuit_replay_claimed": False,
            "local_u3_pricing_accepted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
    }


def validate_payload(
    summary: dict[str, Any], local: dict[str, Any], qiskit_probe: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    expected_counts = {"U": 487, "rz": 601, "cx": 789, "measure": 1, "other_operation": 0}
    expected_fields = {
        "local_parser_passed": True,
        "local_parser_error_count": 0,
        "local_parser_operation_counts": expected_counts,
        "expected_operation_counts": expected_counts,
        "operation_counts_match_export": True,
        "qubit_count": 19,
        "bit_count": 1,
        "statement_count": 1884,
        "operation_row_count": 1878,
        "first_operation_line": 5,
        "last_operation_kind": "measure",
        "qiskit_available": True,
        "qiskit_qasm3_import_available": False,
        "qiskit_loader_attempted": True,
        "qiskit_loader_passed": False,
        "qiskit_loader_status": "optional_dependency_missing",
        "accepted_local_openqasm3_parse_artifact_count": 1,
        "accepted_qiskit_loader_parse_artifact_count": 0,
        "accepted_full_circuit_replay_certificate_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
        "local_parse_claimed": True,
        "qiskit_loader_parse_claimed": False,
        "full_circuit_replay_claimed": False,
        "local_u3_pricing_accepted": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
    }
    for field, value in expected_fields.items():
        if summary.get(field) != value:
            errors.append(f"{field}_expected_{value}_got_{summary.get(field)}")
    if local["errors"]:
        errors.append("local_parser_errors_not_empty")
    if qiskit_probe["qiskit_loader_error_type"] != "MissingOptionalLibraryError":
        errors.append("qiskit_loader_error_type_should_be_missing_optional_library")
    return errors


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# B1/B7 cone_01 OpenQASM 3 Parser-Readiness Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact consumes T-B1-004bu and checks whether the OpenQASM 3 candidate is locally parseable and whether the installed Qiskit stack can load it directly.",
        "",
        "## Summary",
        "",
        f"- OpenQASM 3 candidate: `{payload['openqasm3_candidate_qasm']}`",
        f"- Local parser passed / errors: `{summary['local_parser_passed']}` / `{summary['local_parser_error_count']}`",
        f"- Local operation counts: `{summary['local_parser_operation_counts']}`",
        f"- Qubits / bits / statements / operations: `{summary['qubit_count']}` / `{summary['bit_count']}` / `{summary['statement_count']}` / `{summary['operation_row_count']}`",
        f"- Qiskit available / qiskit_qasm3_import available: `{summary['qiskit_available']}` / `{summary['qiskit_qasm3_import_available']}`",
        f"- Qiskit loader attempted / passed / status: `{summary['qiskit_loader_attempted']}` / `{summary['qiskit_loader_passed']}` / `{summary['qiskit_loader_status']}`",
        f"- Qiskit loader error: `{summary['qiskit_loader_error_type']}`",
        f"- Accepted local parse / Qiskit loader parse artifacts: `{summary['accepted_local_openqasm3_parse_artifact_count']}` / `{summary['accepted_qiskit_loader_parse_artifact_count']}`",
        f"- Accepted replay / local-U3 pricing / occurrence / proxy-T reduction: `{summary['accepted_full_circuit_replay_certificate_count']}` / `{summary['accepted_local_u3_pricing_certificate_count']}` / `{summary['accepted_occurrence_removal']}` / `{summary['accepted_proxy_t_reduction']}`",
        f"- Validation errors: `{summary['validation_error_count']}`",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"]["supported_claim"],
        "",
        "Unsupported claims:",
        "",
    ]
    for claim in payload["claim_boundary"]["unsupported_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Next Required Gate",
            "",
            "Install or vendor a reproducible OpenQASM 3 loader such as qiskit_qasm3_import, parse the candidate through that loader, and only then attempt replay or local-U3 pricing evidence.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=JSON_OUT)
    parser.add_argument("--markdown-output", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.json_output, payload, args.pretty)
    write_text(args.markdown_output, render_markdown(payload))
    print(json.dumps(payload["summary"], indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
