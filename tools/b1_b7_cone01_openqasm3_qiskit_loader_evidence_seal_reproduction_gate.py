#!/usr/bin/env python3
"""Reproduce the B1/B7 OpenQASM 3 Qiskit-loader evidence seal."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESEARCH = ROOT / "research"

METHOD = "b1_b7_cone01_openqasm3_qiskit_loader_evidence_seal_reproduction_gate_v0"
STATUS = "cone01_openqasm3_qiskit_loader_evidence_seal_reproduced_without_b7_credit"
MODEL_STATUS = (
    "qiskit_loader_evidence_seal_reproduced_by_independent_hash_replay_without_b7_credit"
)

SEAL_SCRIPT = ROOT / "tools" / "b1_b7_cone01_openqasm3_qiskit_loader_evidence_seal_gate.py"
SEAL_JSON = RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_gate_v0.json"
SEAL_MD = RESEARCH / "B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_gate.md"
OUT_JSON = (
    RESULTS
    / "B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_reproduction_gate_v0.json"
)
OUT_MD = (
    RESEARCH / "B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_reproduction_gate.md"
)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_text(read_text(path))


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def recompute_source_hashes(source_hashes: dict[str, str]) -> dict[str, str]:
    recomputed: dict[str, str] = {}
    for source_path in source_hashes:
        recomputed[source_path] = sha256_path(ROOT / source_path)
    return recomputed


def build_payload() -> dict[str, Any]:
    pre_payload = load_json(SEAL_JSON)
    pre_summary = pre_payload.get("summary", {})
    expected_source_hashes = pre_summary.get("qiskit_loader_source_artifact_hashes", {})
    errors: list[str] = []

    require(
        errors,
        pre_payload.get("status")
        == "cone01_openqasm3_qiskit_loader_evidence_seal_passed_without_b7_credit",
        "input evidence-seal status is not accepted",
    )
    require(errors, isinstance(expected_source_hashes, dict), "source hash map missing")
    require(errors, len(expected_source_hashes) == 7, "source hash map does not contain 7 artifacts")

    pre_json_hash = sha256_path(SEAL_JSON)
    pre_md_hash = sha256_path(SEAL_MD)
    recomputed_source_hashes = recompute_source_hashes(expected_source_hashes)
    independent_seal_material = json.dumps(
        recomputed_source_hashes, sort_keys=True, separators=(",", ":")
    )
    independent_seal = sha256_text(independent_seal_material)
    source_hash_mismatches = [
        path
        for path, digest in expected_source_hashes.items()
        if recomputed_source_hashes.get(path) != digest
    ]

    completed = subprocess.run(
        [sys.executable, rel(SEAL_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    post_payload = load_json(SEAL_JSON)
    post_summary = post_payload.get("summary", {})
    post_json_hash = sha256_path(SEAL_JSON)
    post_md_hash = sha256_path(SEAL_MD)
    post_source_hashes = post_summary.get("qiskit_loader_source_artifact_hashes", {})
    expected_seal = pre_summary.get("qiskit_loader_evidence_seal_sha256")
    reproduced_seal = post_summary.get("qiskit_loader_evidence_seal_sha256")

    require(errors, completed.returncode == 0, "evidence-seal generator did not exit cleanly")
    require(errors, not source_hash_mismatches, "independent source hash recomputation mismatched")
    require(errors, independent_seal == expected_seal, "independent seal does not match expected seal")
    require(errors, reproduced_seal == expected_seal, "reproduced seal does not match expected seal")
    require(errors, post_source_hashes == expected_source_hashes, "reproduced source hash map changed")
    require(errors, pre_json_hash == post_json_hash, "evidence-seal JSON is not byte-stable")
    require(errors, pre_md_hash == post_md_hash, "evidence-seal markdown is not byte-stable")
    require(
        errors,
        post_payload.get("status")
        == "cone01_openqasm3_qiskit_loader_evidence_seal_passed_without_b7_credit",
        "reproduced evidence-seal report status changed",
    )
    require(
        errors,
        post_summary.get("failed_input_case_count_total") == 0,
        "reproduced evidence-seal report has failed replay cases",
    )
    require(
        errors,
        post_summary.get("accepted_occurrence_removal") == 0
        and post_summary.get("accepted_proxy_t_reduction") == 0
        and post_summary.get("b7_ledger_improvement_claimed") is False,
        "reproduced report started claiming B7 resource credit",
    )

    passed = not errors
    summary = {
        "input_evidence_seal_report_path": rel(SEAL_JSON),
        "input_evidence_seal_markdown_path": rel(SEAL_MD),
        "reproduction_command": f"{Path(sys.executable).name} {rel(SEAL_SCRIPT)}",
        "subprocess_exit_code": completed.returncode,
        "subprocess_stdout_sha256": sha256_text(completed.stdout),
        "subprocess_stderr_sha256": sha256_text(completed.stderr),
        "source_artifact_count": len(expected_source_hashes),
        "source_hash_match_count": len(expected_source_hashes) - len(source_hash_mismatches),
        "source_hash_mismatch_count": len(source_hash_mismatches),
        "source_hash_mismatch_paths": source_hash_mismatches,
        "expected_evidence_seal_sha256": expected_seal,
        "independent_evidence_seal_sha256": independent_seal,
        "reproduced_evidence_seal_sha256": reproduced_seal,
        "evidence_seal_reproduction_passed": passed,
        "source_hashes_reproduced": post_source_hashes == expected_source_hashes,
        "json_report_sha256_before": pre_json_hash,
        "json_report_sha256_after": post_json_hash,
        "json_report_byte_stable": pre_json_hash == post_json_hash,
        "markdown_report_sha256_before": pre_md_hash,
        "markdown_report_sha256_after": post_md_hash,
        "markdown_report_byte_stable": pre_md_hash == post_md_hash,
        "qiskit_version": post_summary.get("qiskit_version"),
        "qiskit_qasm3_import_version": post_summary.get("qiskit_qasm3_import_version"),
        "openqasm3_package_version": post_summary.get("openqasm3_package_version"),
        "qiskit_depth": post_summary.get("qiskit_depth"),
        "qiskit_count_ops": post_summary.get("qiskit_count_ops"),
        "multi_input_case_count": post_summary.get("multi_input_case_count"),
        "phase_consistent_input_case_count": post_summary.get("phase_consistent_input_case_count"),
        "global_phase_input_case_count": post_summary.get("global_phase_input_case_count"),
        "failed_input_case_count_total": post_summary.get("failed_input_case_count_total"),
        "selected_line_numbers": post_summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": post_summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "accepted_qiskit_loader_evidence_seal_count": post_summary.get(
            "accepted_qiskit_loader_evidence_seal_count"
        ),
        "accepted_qiskit_loader_evidence_seal_reproduction_count": 1 if passed else 0,
        "accepted_full_space_symbolic_certificate_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
        "symbolic_unitary_equivalence_claimed": False,
        "arbitrary_input_equivalence_claimed": False,
        "full_hilbert_space_certificate_claimed": False,
        "local_u3_pricing_accepted": False,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "validation_error_count": len(errors),
    }
    return {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS if passed else "cone01_openqasm3_qiskit_loader_evidence_seal_reproduction_failed",
        "model_status": MODEL_STATUS if passed else "qiskit_loader_evidence_seal_not_reproduced",
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "claim_boundary": {
            "supported_claim": (
                "The T-B1-004cm Qiskit-loader evidence seal is independently hash-recomputed "
                "and byte-stably regenerated by rerunning the seal generator."
            ),
            "qiskit_loader_evidence_seal_reproduction_claimed": passed,
            "symbolic_unitary_equivalence_claimed": False,
            "arbitrary_input_equivalence_claimed": False,
            "full_hilbert_space_certificate_claimed": False,
            "local_u3_pricing_accepted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "unsupported_claims": [
                "This is a reproducibility gate, not a new semantic-equivalence theorem.",
                "This does not extend coverage beyond the existing 6-dimensional certified span.",
                "This does not price the remaining line-1381 local-U3 burden.",
                "This does not recover the dropped line-1378 overlap delta.",
                "This does not improve the B7 resource ledger.",
            ],
        },
        "summary": summary,
        "validation_errors": errors,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    claims = payload["claim_boundary"]
    lines = [
        "# B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Evidence Seal Reproduction Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- Input evidence-seal report: `{summary['input_evidence_seal_report_path']}`",
        f"- Reproduction command: `{summary['reproduction_command']}`",
        f"- Source artifacts / matching hashes: {summary['source_artifact_count']} / {summary['source_hash_match_count']}",
        f"- Expected / independent / reproduced seal: `{summary['expected_evidence_seal_sha256']}` / `{summary['independent_evidence_seal_sha256']}` / `{summary['reproduced_evidence_seal_sha256']}`",
        f"- JSON report byte-stable: {summary['json_report_byte_stable']} (`{summary['json_report_sha256_before']}` -> `{summary['json_report_sha256_after']}`)",
        f"- Markdown report byte-stable: {summary['markdown_report_byte_stable']} (`{summary['markdown_report_sha256_before']}` -> `{summary['markdown_report_sha256_after']}`)",
        f"- Qiskit / qiskit-qasm3-import / openqasm3: {summary['qiskit_version']} / {summary['qiskit_qasm3_import_version']} / {summary['openqasm3_package_version']}",
        f"- Depth / operation counts: {summary['qiskit_depth']} / {summary['qiskit_count_ops']}",
        f"- Multi / phase / global input cases: {summary['multi_input_case_count']} / {summary['phase_consistent_input_case_count']} / {summary['global_phase_input_case_count']}",
        f"- Failed replay cases total: {summary['failed_input_case_count_total']}",
        f"- Selected lines / dropped overlap lines: {summary['selected_line_numbers']} / {summary['dropped_overlap_candidate_line_numbers']}",
        f"- Accepted evidence seal / reproduction count: {summary['accepted_qiskit_loader_evidence_seal_count']} / {summary['accepted_qiskit_loader_evidence_seal_reproduction_count']}",
        f"- Accepted occurrence removal / proxy-T reduction / B7 claim: {summary['accepted_occurrence_removal']} / {summary['accepted_proxy_t_reduction']} / {summary['b7_ledger_improvement_claimed']}",
        f"- Validation errors: {summary['validation_error_count']}",
        "",
        "## Claim Boundary",
        "",
        claims["supported_claim"],
        "",
        "Unsupported claims:",
    ]
    for item in claims["unsupported_claims"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
