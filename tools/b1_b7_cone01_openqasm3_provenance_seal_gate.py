#!/usr/bin/env python3
"""Seal the OpenQASM 3 composable patch-lift artifact chain with file hashes."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESEARCH = ROOT / "research"

METHOD = "b1_b7_cone01_openqasm3_provenance_seal_gate_v0"
STATUS = "cone01_openqasm3_provenance_seal_passed_without_b7_resource_credit"
MODEL_STATUS = "openqasm3_patch_lift_artifacts_are_file_hash_sealed_without_b7_credit"

QASM2_PATH = RESULTS / "B1_B7_cone01_qasm2_candidate_rewrite_gate" / "gcm_h6_line268_line1381_candidate.qasm"
QASM3_PATH = (
    RESULTS
    / "B1_B7_cone01_openqasm3_candidate_export_gate"
    / "gcm_h6_line268_line1381_candidate_openqasm3.qasm"
)
PATCH_PATH = RESULTS / "B1_B7_cone01_composable_patch_certificate_gate_v0.json"
ROUNDTRIP_PATH = RESULTS / "B1_B7_cone01_openqasm3_structural_roundtrip_gate_v0.json"
SPAN_PATH = RESULTS / "B1_B7_cone01_openqasm3_linear_span_replay_certificate_gate_v0.json"
LIFT_PATH = RESULTS / "B1_B7_cone01_openqasm3_composable_patch_lift_gate_v0.json"
OUT_JSON = RESULTS / "B1_B7_cone01_openqasm3_provenance_seal_gate_v0.json"
OUT_MD = RESEARCH / "B1_B7_cone01_openqasm3_provenance_seal_gate.md"

QASM2_SKIP_RE = re.compile(
    r'^(?:OPENQASM 2\.0;|include "qelib1\.inc";|qreg\s+q\[\d+\];|creg\s+c\[\d+\];)$'
)
QASM3_SKIP_RE = re.compile(
    r'^(?:OPENQASM 3\.0;|include "stdgates\.inc";|qubit\[\d+\]\s+q;|bit\[\d+\]\s+c;)$'
)
U_RE = re.compile(r"^(?:u3|U)\(([^()]*)\)\s+q\[(\d+)\];$", re.IGNORECASE)
RZ_RE = re.compile(r"^rz\(([^()]*)\)\s+q\[(\d+)\];$", re.IGNORECASE)
CX_RE = re.compile(r"^cx\s+q\[(\d+)\]\s*,\s*q\[(\d+)\];$", re.IGNORECASE)
MEASURE_ARROW_RE = re.compile(r"^measure\s+q\[(\d+)\]\s*->\s*c\[(\d+)\];$", re.IGNORECASE)
MEASURE_ASSIGN_RE = re.compile(r"^c\[(\d+)\]\s*=\s*measure\s+q\[(\d+)\];$", re.IGNORECASE)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(read_text(path))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_args(args: str) -> str:
    return ",".join(part.strip().replace(" ", "") for part in args.split(","))


def normalize_line(line: str, dialect: str, line_number: int) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("//"):
        return None
    if dialect == "qasm2" and QASM2_SKIP_RE.match(stripped):
        return None
    if dialect == "qasm3" and QASM3_SKIP_RE.match(stripped):
        return None

    u_match = U_RE.match(stripped)
    if u_match:
        return f"U({normalize_args(u_match.group(1))})|q[{u_match.group(2)}]"

    rz_match = RZ_RE.match(stripped)
    if rz_match:
        return f"rz({normalize_args(rz_match.group(1))})|q[{rz_match.group(2)}]"

    cx_match = CX_RE.match(stripped)
    if cx_match:
        return f"cx|q[{cx_match.group(1)}],q[{cx_match.group(2)}]"

    arrow_match = MEASURE_ARROW_RE.match(stripped)
    if arrow_match:
        return f"measure|q[{arrow_match.group(1)}]->c[{arrow_match.group(2)}]"

    assign_match = MEASURE_ASSIGN_RE.match(stripped)
    if assign_match:
        return f"measure|q[{assign_match.group(2)}]->c[{assign_match.group(1)}]"

    raise ValueError(f"unparsed_{dialect}_line_{line_number}: {stripped}")


def normalize_qasm(text: str, dialect: str) -> list[str]:
    rows: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        normalized = normalize_line(line, dialect, line_number)
        if normalized is not None:
            rows.append(normalized)
    return rows


def stream_hash(rows: list[str]) -> str:
    return sha256_text("\n".join(rows) + "\n")


def operation_name(row: str) -> str:
    return row.split("(", 1)[0] if row.startswith(("U(", "rz(")) else row.split("|", 1)[0]


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    qasm2_text = read_text(QASM2_PATH)
    qasm3_text = read_text(QASM3_PATH)
    qasm2_rows = normalize_qasm(qasm2_text, "qasm2")
    qasm3_rows = normalize_qasm(qasm3_text, "qasm3")
    patch = load_json(PATCH_PATH)
    roundtrip = load_json(ROUNDTRIP_PATH)
    span = load_json(SPAN_PATH)
    lift = load_json(LIFT_PATH)
    roundtrip_summary = roundtrip.get("summary", {})
    lift_summary = lift.get("summary", {})

    qasm2_stream_sha = stream_hash(qasm2_rows)
    qasm3_stream_sha = stream_hash(qasm3_rows)
    expected_stream_sha = "7cd50bea1f5a3c191c5735c0891d3f70f8c07a9cfca9d6e93724e6d49cb36343"
    operation_counts = dict(Counter(operation_name(row) for row in qasm3_rows))

    errors: list[str] = []
    require(errors, qasm2_text.startswith("OPENQASM 2.0;"), "qasm2 header changed")
    require(errors, qasm3_text.startswith("OPENQASM 3.0;"), "qasm3 header changed")
    require(errors, 'include "stdgates.inc";' in qasm3_text, "qasm3 stdgates include missing")
    require(errors, "qreg " not in qasm3_text and "creg " not in qasm3_text, "legacy qreg/creg leaked into qasm3")
    require(errors, "u3(" not in qasm3_text.lower(), "legacy u3 leaked into qasm3")
    require(errors, "->" not in qasm3_text, "legacy measurement arrow leaked into qasm3")
    require(errors, len(qasm2_text.splitlines()) == 1884, "qasm2 line count changed")
    require(errors, len(qasm3_text.splitlines()) == 1884, "qasm3 line count changed")
    require(errors, len(qasm2_rows) == 1878 and len(qasm3_rows) == 1878, "normalized instruction count changed")
    require(errors, qasm2_rows == qasm3_rows, "normalized qasm2/qasm3 streams differ")
    require(errors, qasm2_stream_sha == expected_stream_sha, "qasm2 normalized stream hash changed")
    require(errors, qasm3_stream_sha == expected_stream_sha, "qasm3 normalized stream hash changed")
    require(errors, operation_counts == {"U": 487, "rz": 601, "cx": 789, "measure": 1}, "operation counts changed")
    require(errors, patch.get("status") == "cone01_composable_patch_certificate_passed_without_b7_resource_credit", "patch source status changed")
    require(errors, roundtrip.get("status") == "cone01_openqasm3_structural_roundtrip_matches_legacy_candidate", "roundtrip source status changed")
    require(errors, span.get("status") == "cone01_openqasm3_linear_span_replay_certificate_passed_not_full_unitary", "span source status changed")
    require(errors, lift.get("status") == "cone01_openqasm3_composable_patch_lift_passed_without_b7_resource_credit", "patch-lift source status changed")
    require(errors, roundtrip_summary.get("normalized_stream_sha256") == expected_stream_sha, "roundtrip stream hash changed")
    require(errors, lift_summary.get("normalized_stream_sha256") == expected_stream_sha, "lift stream hash changed")
    require(errors, lift_summary.get("selected_line_numbers") == [268, 1381], "selected patch lines changed")
    require(errors, lift_summary.get("dropped_overlap_candidate_line_numbers") == [1378], "dropped overlap lines changed")

    source_hashes = {
        rel(QASM2_PATH): sha256_text(qasm2_text),
        rel(QASM3_PATH): sha256_text(qasm3_text),
        rel(PATCH_PATH): sha256_text(read_text(PATCH_PATH)),
        rel(ROUNDTRIP_PATH): sha256_text(read_text(ROUNDTRIP_PATH)),
        rel(SPAN_PATH): sha256_text(read_text(SPAN_PATH)),
        rel(LIFT_PATH): sha256_text(read_text(LIFT_PATH)),
    }
    seal_material = json.dumps(source_hashes, sort_keys=True, separators=(",", ":"))
    seal_sha = sha256_text(seal_material)
    passed = not errors
    summary = {
        "qasm2_candidate_path": rel(QASM2_PATH),
        "openqasm3_candidate_path": rel(QASM3_PATH),
        "qasm2_raw_line_count": len(qasm2_text.splitlines()),
        "openqasm3_raw_line_count": len(qasm3_text.splitlines()),
        "normalized_instruction_count": len(qasm3_rows),
        "normalized_streams_match": qasm2_rows == qasm3_rows,
        "normalized_stream_sha256": qasm3_stream_sha,
        "operation_counts": operation_counts,
        "source_artifact_hashes": source_hashes,
        "provenance_seal_sha256": seal_sha,
        "selected_line_numbers": lift_summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": lift_summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "max_selected_patch_residual_norm": lift_summary.get("max_selected_patch_residual_norm"),
        "max_selected_patch_entry_error": lift_summary.get("max_selected_patch_entry_error"),
        "openqasm3_linear_span_error_spectral_norm": lift_summary.get(
            "openqasm3_linear_span_error_spectral_norm"
        ),
        "openqasm3_provenance_seal_passed": passed,
        "accepted_project_local_openqasm3_provenance_seal_count": 1 if passed else 0,
        "accepted_qiskit_loader_parse_artifact_count": 0,
        "accepted_symbolic_unitary_equivalence_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
        "qiskit_loader_parse_claimed": False,
        "symbolic_unitary_equivalence_claimed": False,
        "arbitrary_input_equivalence_claimed": False,
        "full_hilbert_space_certificate_claimed": False,
        "local_u3_pricing_accepted": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": len(errors),
    }
    payload = {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS if passed else "cone01_openqasm3_provenance_seal_failed",
        "model_status": MODEL_STATUS if passed else "openqasm3_patch_lift_artifacts_not_sealed",
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "source_openqasm3_composable_patch_lift_gate": rel(LIFT_PATH),
        "claim_boundary": {
            "supported_claim": (
                "The OpenQASM 3 patch-lift evidence chain is file-hash sealed: the QASM2 "
                "candidate, OpenQASM 3 candidate, source patch certificate, roundtrip "
                "certificate, finite-span certificate, and patch-lift certificate all match "
                "the recorded provenance seal."
            ),
            "qiskit_loader_parse_claimed": False,
            "symbolic_unitary_equivalence_claimed": False,
            "arbitrary_input_equivalence_claimed": False,
            "full_hilbert_space_certificate_claimed": False,
            "local_u3_pricing_accepted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "unsupported_claims": [
                "This is not a Qiskit OpenQASM 3 loader parse.",
                "This is not a symbolic exact full-circuit unitary proof.",
                "This is not arbitrary-input or full-Hilbert-space coverage.",
                "This does not price or eliminate the remaining local-U3 parameters.",
                "This does not improve the B7 resource ledger.",
            ],
        },
        "summary": summary,
        "validation_errors": errors,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    if errors:
        raise SystemExit("OpenQASM3 provenance seal gate failed: " + "; ".join(errors))


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    return "\n".join(
        [
            "# B1/B7 cone_01 OpenQASM 3 Provenance Seal Gate",
            "",
            f"- Method: `{payload['method']}`",
            f"- Status: `{payload['status']}`",
            f"- Model status: `{payload['model_status']}`",
            f"- Workload: `{payload['workload']}`",
            f"- QASM2 candidate: `{summary['qasm2_candidate_path']}`",
            f"- OpenQASM 3 artifact: `{summary['openqasm3_candidate_path']}`",
            "",
            "## Evidence",
            "",
            f"- Raw QASM2 / OpenQASM 3 line counts: {summary['qasm2_raw_line_count']} / {summary['openqasm3_raw_line_count']}",
            f"- Normalized stream match / instruction count: {summary['normalized_streams_match']} / {summary['normalized_instruction_count']}",
            f"- Normalized stream SHA-256: `{summary['normalized_stream_sha256']}`",
            f"- Provenance seal SHA-256: `{summary['provenance_seal_sha256']}`",
            f"- Selected lines / dropped overlap lines: {summary['selected_line_numbers']} / {summary['dropped_overlap_candidate_line_numbers']}",
            f"- Max patch residual / entry error: {summary['max_selected_patch_residual_norm']} / {summary['max_selected_patch_entry_error']}",
            f"- OpenQASM 3 span spectral error: {summary['openqasm3_linear_span_error_spectral_norm']}",
            "",
            "## Source Hashes",
            "",
            *[
                f"- `{path}`: `{digest}`"
                for path, digest in sorted(summary["source_artifact_hashes"].items())
            ],
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"]["supported_claim"],
            "",
            "Unsupported claims:",
            "",
            *[f"- {item}" for item in payload["claim_boundary"]["unsupported_claims"]],
            "",
        ]
    )


if __name__ == "__main__":
    main()
