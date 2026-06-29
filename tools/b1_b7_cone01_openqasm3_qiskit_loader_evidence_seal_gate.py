#!/usr/bin/env python3
"""Seal the B1/B7 OpenQASM 3 Qiskit-loader evidence chain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESEARCH = ROOT / "research"

METHOD = "b1_b7_cone01_openqasm3_qiskit_loader_evidence_seal_gate_v0"
STATUS = "cone01_openqasm3_qiskit_loader_evidence_seal_passed_without_b7_credit"
MODEL_STATUS = "qiskit_loader_openqasm3_patch_lift_evidence_chain_hash_sealed_without_b7_credit"

QASM3_PATH = (
    RESULTS
    / "B1_B7_cone01_openqasm3_candidate_export_gate"
    / "gcm_h6_line268_line1381_candidate_openqasm3.qasm"
)
REPLAY_PATH = RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_replay_gate_v0.json"
MULTI_INPUT_PATH = (
    RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_multi_input_replay_gate_v0.json"
)
PHASE_PATH = (
    RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_phase_consistent_replay_gate_v0.json"
)
GLOBAL_PATH = (
    RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_gate_v0.json"
)
SPAN_PATH = (
    RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_linear_span_replay_certificate_gate_v0.json"
)
PATCH_LIFT_SUPPORT_PATH = (
    RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_composable_patch_lift_gate_v0.json"
)
OUT_JSON = RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_gate_v0.json"
OUT_MD = RESEARCH / "B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_gate.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def build_payload() -> dict[str, Any]:
    replay = load_json(REPLAY_PATH)
    multi = load_json(MULTI_INPUT_PATH)
    phase = load_json(PHASE_PATH)
    global_phase = load_json(GLOBAL_PATH)
    span = load_json(SPAN_PATH)
    patch_lift = load_json(PATCH_LIFT_SUPPORT_PATH)
    replay_summary = replay.get("summary", {})
    multi_summary = multi.get("summary", {})
    phase_summary = phase.get("summary", {})
    global_summary = global_phase.get("summary", {})
    span_summary = span.get("summary", {})
    patch_summary = patch_lift.get("summary", {})
    errors: list[str] = []

    require(
        errors,
        replay.get("status") == "cone01_openqasm3_qiskit_loader_replay_passed_default_input_only",
        "Qiskit-loader default-input replay status changed",
    )
    require(
        errors,
        multi.get("status") == "cone01_openqasm3_qiskit_loader_multi_input_replay_passed_sampled_inputs",
        "Qiskit-loader multi-input replay status changed",
    )
    require(
        errors,
        phase.get("status") == "cone01_openqasm3_qiskit_loader_phase_consistent_replay_passed",
        "Qiskit-loader phase-consistent replay status changed",
    )
    require(
        errors,
        global_phase.get("status") == "cone01_openqasm3_qiskit_loader_global_phase_subspace_replay_passed",
        "Qiskit-loader global-phase replay status changed",
    )
    require(
        errors,
        span.get("status") == "cone01_openqasm3_qiskit_loader_linear_span_replay_certificate_passed",
        "Qiskit-loader finite-span status changed",
    )
    require(
        errors,
        patch_lift.get("status")
        == "cone01_openqasm3_qiskit_loader_composable_patch_lift_supported_without_b7_credit",
        "Qiskit-loader patch-lift support status changed",
    )

    expected_path = rel(QASM3_PATH)
    for label, summary in [
        ("replay", replay_summary),
        ("multi-input", multi_summary),
        ("phase", phase_summary),
        ("global", global_summary),
        ("span", span_summary),
        ("patch-lift", patch_summary),
    ]:
        require(
            errors,
            summary.get("openqasm3_candidate_path") == expected_path
            or summary.get("qiskit_loader_openqasm3_candidate_path") == expected_path,
            f"{label} OpenQASM 3 candidate path changed",
        )
        require(errors, summary.get("qiskit_version") == "2.4.1", f"{label} Qiskit version changed")
        require(
            errors,
            summary.get("qiskit_qasm3_import_version") == "0.6.0",
            f"{label} qiskit-qasm3-import version changed",
        )
        require(
            errors,
            summary.get("openqasm3_package_version") == "1.0.1",
            f"{label} openqasm3 package version changed",
        )
        require(errors, summary.get("qiskit_num_qubits") == 19, f"{label} qubit count changed")
        require(errors, summary.get("qiskit_num_clbits") == 1, f"{label} clbit count changed")
        require(errors, summary.get("qiskit_depth") == 1483, f"{label} depth changed")
        require(
            errors,
            summary.get("qiskit_count_ops") == {"cx": 789, "measure": 1, "rz": 601, "u": 487},
            f"{label} operation counts changed",
        )

    require(errors, multi_summary.get("failed_input_case_count") == 0, "multi-input failed cases changed")
    require(errors, phase_summary.get("failed_input_case_count") == 0, "phase failed cases changed")
    require(errors, global_summary.get("failed_input_case_count") == 0, "global failed cases changed")
    require(
        errors,
        span_summary.get("qiskit_loader_linear_span_certificate_passed") is True,
        "finite-span certificate flag changed",
    )
    require(
        errors,
        patch_summary.get("openqasm3_qiskit_loader_composable_patch_lift_supported") is True,
        "patch-lift support flag changed",
    )
    require(errors, patch_summary.get("selected_line_numbers") == [268, 1381], "selected lines changed")
    require(
        errors,
        patch_summary.get("dropped_overlap_candidate_line_numbers") == [1378],
        "dropped overlap lines changed",
    )
    require(errors, patch_summary.get("stream_mismatch_count") == 0, "stream mismatch changed")
    require(errors, patch_summary.get("normalized_instruction_count") == 1878, "instruction count changed")
    require(
        errors,
        float(span_summary.get("linear_span_error_spectral_norm", 1.0)) <= 1e-10,
        "finite-span spectral error too large",
    )
    require(
        errors,
        float(patch_summary.get("qiskit_loader_linear_span_error_spectral_norm", 1.0)) <= 1e-10,
        "patch-lift support span spectral error too large",
    )

    source_paths = [
        QASM3_PATH,
        REPLAY_PATH,
        MULTI_INPUT_PATH,
        PHASE_PATH,
        GLOBAL_PATH,
        SPAN_PATH,
        PATCH_LIFT_SUPPORT_PATH,
    ]
    source_hashes = {rel(path): sha256_text(read_text(path)) for path in source_paths}
    seal_material = json.dumps(source_hashes, sort_keys=True, separators=(",", ":"))
    seal_sha = sha256_text(seal_material)
    passed = not errors

    summary = {
        "openqasm3_candidate_path": expected_path,
        "qiskit_loader_source_artifact_count": len(source_paths),
        "qiskit_loader_source_artifact_hashes": source_hashes,
        "qiskit_loader_evidence_seal_sha256": seal_sha,
        "qiskit_version": "2.4.1",
        "qiskit_qasm3_import_version": "0.6.0",
        "openqasm3_package_version": "1.0.1",
        "qiskit_num_qubits": 19,
        "qiskit_num_clbits": 1,
        "qiskit_depth": 1483,
        "qiskit_count_ops": {"cx": 789, "measure": 1, "rz": 601, "u": 487},
        "default_input_replay_passed": replay_summary.get(
            "qiskit_loader_default_input_replay_passed"
        ),
        "multi_input_case_count": multi_summary.get("input_case_count"),
        "phase_consistent_input_case_count": phase_summary.get("input_case_count"),
        "global_phase_input_case_count": global_summary.get("input_case_count"),
        "failed_input_case_count_total": (
            int(multi_summary.get("failed_input_case_count", 0))
            + int(phase_summary.get("failed_input_case_count", 0))
            + int(global_summary.get("failed_input_case_count", 0))
        ),
        "qiskit_loader_global_phase_subspace_replay_passed": global_summary.get(
            "qiskit_loader_global_phase_subspace_replay_passed"
        ),
        "qiskit_loader_linear_span_certificate_passed": span_summary.get(
            "qiskit_loader_linear_span_certificate_passed"
        ),
        "qiskit_loader_composable_patch_lift_support_passed": patch_summary.get(
            "openqasm3_qiskit_loader_composable_patch_lift_supported"
        ),
        "qiskit_loader_certified_input_subspace_dimension": span_summary.get(
            "certified_input_subspace_dimension"
        ),
        "qiskit_loader_full_input_space_dimension": span_summary.get("full_input_space_dimension"),
        "qiskit_loader_linear_span_error_spectral_norm": span_summary.get(
            "linear_span_error_spectral_norm"
        ),
        "qiskit_loader_max_basis_l2_error": span_summary.get("max_basis_l2_error"),
        "qiskit_loader_max_basis_probability_delta": span_summary.get(
            "max_basis_probability_delta"
        ),
        "qiskit_loader_max_cross_gram_delta": span_summary.get("max_cross_gram_delta"),
        "selected_line_numbers": patch_summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": patch_summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "stream_mismatch_count": patch_summary.get("stream_mismatch_count"),
        "normalized_instruction_count": patch_summary.get("normalized_instruction_count"),
        "accepted_qiskit_loader_parse_artifact_count": 1,
        "accepted_qiskit_loader_replay_artifact_count": 1,
        "accepted_qiskit_loader_multi_input_replay_artifact_count": 1,
        "accepted_qiskit_loader_phase_consistent_replay_artifact_count": 1,
        "accepted_qiskit_loader_global_phase_subspace_replay_artifact_count": 1,
        "accepted_qiskit_loader_linear_span_certificate_count": 1,
        "accepted_qiskit_loader_composable_patch_lift_support_count": 1,
        "accepted_qiskit_loader_evidence_seal_count": 1 if passed else 0,
        "accepted_full_space_symbolic_certificate_count": 0,
        "accepted_local_u3_pricing_certificate_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "missing_occurrences_after_gate": 30,
        "missing_proxy_t_after_gate": 600,
        "qiskit_loader_parse_claimed": True,
        "qiskit_loader_replay_claimed": True,
        "qiskit_loader_evidence_seal_claimed": passed,
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
        "status": STATUS if passed else "cone01_openqasm3_qiskit_loader_evidence_seal_failed",
        "model_status": MODEL_STATUS if passed else "qiskit_loader_evidence_chain_not_sealed",
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "claim_boundary": {
            "supported_claim": (
                "The OpenQASM 3 Qiskit-loader evidence chain is hash-sealed across "
                "the candidate QASM file and the replay, multi-input, phase, global-phase, "
                "finite-span, and composable patch-lift support artifacts."
            ),
            "qiskit_loader_parse_claimed": True,
            "qiskit_loader_replay_claimed": True,
            "qiskit_loader_evidence_seal_claimed": passed,
            "symbolic_unitary_equivalence_claimed": False,
            "arbitrary_input_equivalence_claimed": False,
            "full_hilbert_space_certificate_claimed": False,
            "local_u3_pricing_accepted": False,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "unsupported_claims": [
                "This is a reproducibility and drift-detection seal, not a new equivalence theorem.",
                "This does not extend coverage beyond the 6-dimensional certified span.",
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
        "# B1/B7 cone_01 OpenQASM 3 Qiskit-Loader Evidence Seal Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- OpenQASM 3 candidate: `{summary['openqasm3_candidate_path']}`",
        f"- Source artifacts sealed: {summary['qiskit_loader_source_artifact_count']}",
        f"- Evidence seal SHA-256: `{summary['qiskit_loader_evidence_seal_sha256']}`",
        f"- Qiskit / qiskit-qasm3-import / openqasm3: {summary['qiskit_version']} / {summary['qiskit_qasm3_import_version']} / {summary['openqasm3_package_version']}",
        f"- Qubits / clbits / depth: {summary['qiskit_num_qubits']} / {summary['qiskit_num_clbits']} / {summary['qiskit_depth']}",
        f"- Operation counts: {summary['qiskit_count_ops']}",
        f"- Multi / phase / global input cases: {summary['multi_input_case_count']} / {summary['phase_consistent_input_case_count']} / {summary['global_phase_input_case_count']}",
        f"- Failed replay cases total: {summary['failed_input_case_count_total']}",
        f"- Qiskit-loader global-phase / finite-span / patch-lift support passed: {summary['qiskit_loader_global_phase_subspace_replay_passed']} / {summary['qiskit_loader_linear_span_certificate_passed']} / {summary['qiskit_loader_composable_patch_lift_support_passed']}",
        f"- Certified span / full space: {summary['qiskit_loader_certified_input_subspace_dimension']} / {summary['qiskit_loader_full_input_space_dimension']}",
        f"- Span spectral / max basis L2 / max probability / max cross-Gram delta: {summary['qiskit_loader_linear_span_error_spectral_norm']} / {summary['qiskit_loader_max_basis_l2_error']} / {summary['qiskit_loader_max_basis_probability_delta']} / {summary['qiskit_loader_max_cross_gram_delta']}",
        f"- Selected lines / dropped overlap lines: {summary['selected_line_numbers']} / {summary['dropped_overlap_candidate_line_numbers']}",
        f"- Stream mismatch / instruction count: {summary['stream_mismatch_count']} / {summary['normalized_instruction_count']}",
        f"- Accepted Qiskit-loader evidence seal count: {summary['accepted_qiskit_loader_evidence_seal_count']}",
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
    lines.extend(
        [
            "",
            "## Source Artifact Hashes",
            "",
        ]
    )
    for path, digest in summary["qiskit_loader_source_artifact_hashes"].items():
        lines.append(f"- `{path}`: `{digest}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
