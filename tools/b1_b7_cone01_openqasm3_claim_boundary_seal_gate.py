#!/usr/bin/env python3
"""Seal the current B1/B7 OpenQASM 3 claim boundary.

This gate aggregates the strongest current OpenQASM 3/Qiskit-loader replay
evidence for the `gcm_h6` cone_01 route, then keeps the B7 resource boundary
explicit. It is intentionally a claim-boundary gate: passing it means the replay
evidence is coherent and citable, not that B7 receives resource credit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESEARCH = ROOT / "research"

METHOD = "b1_b7_cone01_openqasm3_claim_boundary_seal_gate_v0"
STATUS = "cone01_openqasm3_claim_boundary_sealed_without_b7_credit"
MODEL_STATUS = "qiskit_loader_replay_chain_citable_but_resource_boundary_blocks_b7_credit"

EVIDENCE_SEAL_REPRODUCTION = (
    RESULTS
    / "B1_B7_cone01_openqasm3_qiskit_loader_evidence_seal_reproduction_gate_v0.json"
)
LINEAR_SPAN = (
    RESULTS
    / "B1_B7_cone01_openqasm3_qiskit_loader_linear_span_replay_certificate_gate_v0.json"
)
COMPOSABLE_LIFT = (
    RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_composable_patch_lift_gate_v0.json"
)
SEEDED_RESOURCE_BOUNDARY = (
    RESULTS / "B1_B7_cone01_openqasm3_qiskit_loader_seeded_resource_boundary_gate_v0.json"
)

OUT_JSON = RESULTS / "B1_B7_cone01_openqasm3_claim_boundary_seal_gate_v0.json"
OUT_MD = RESEARCH / "B1_B7_cone01_openqasm3_claim_boundary_seal_gate.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def requirement(req_id: str, name: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {
        "requirement_id": req_id,
        "name": name,
        "passed": passed,
        "evidence": evidence,
    }


def main() -> None:
    reproduction = load_json(EVIDENCE_SEAL_REPRODUCTION)
    linear = load_json(LINEAR_SPAN)
    lift = load_json(COMPOSABLE_LIFT)
    boundary = load_json(SEEDED_RESOURCE_BOUNDARY)

    reproduction_summary = reproduction["summary"]
    linear_summary = linear["summary"]
    lift_summary = lift["summary"]
    boundary_summary = boundary["summary"]

    requirements = [
        requirement(
            "S1",
            "Qiskit-loader evidence seal is byte-stably reproduced",
            reproduction_summary.get("evidence_seal_reproduction_passed") is True
            and reproduction_summary.get("validation_error_count") == 0,
            f"seal={reproduction_summary.get('expected_evidence_seal_sha256')}",
        ),
        requirement(
            "S2",
            "Qiskit loader has a certified finite linear span",
            linear_summary.get("qiskit_loader_linear_span_certificate_passed") is True
            and linear_summary.get("linear_span_dimension") == 6,
            (
                "dimension="
                f"{linear_summary.get('linear_span_dimension')}, spectral_error="
                f"{linear_summary.get('linear_span_error_spectral_norm')}"
            ),
        ),
        requirement(
            "S3",
            "Composable patch lift is supported through the Qiskit loader",
            lift_summary.get("openqasm3_qiskit_loader_composable_patch_lift_supported")
            is True
            and lift_summary.get("qiskit_loader_certified_input_subspace_dimension") == 6,
            (
                "selected_lines="
                f"{lift_summary.get('selected_line_numbers')}, certified_fraction="
                f"{lift_summary.get('qiskit_loader_certified_input_subspace_fraction')}"
            ),
        ),
        requirement(
            "S4",
            "Seeded product replay survives the loader path",
            boundary_summary.get("qiskit_loader_seeded_product_replay_passed") is True
            and boundary_summary.get("seeded_product_input_case_count") == 16,
            (
                "cases="
                f"{boundary_summary.get('seeded_product_input_case_count')}, min_fidelity="
                f"{boundary_summary.get('seeded_product_min_state_fidelity')}"
            ),
        ),
        requirement(
            "S5",
            "Line 1381 resource burden is still explicit",
            boundary_summary.get("line1381_replacement_off_pi_over_four_parameter_count")
            == 5
            and boundary_summary.get("line1381_unpriced_proxy_t_pressure") == 100,
            (
                "off_grid="
                f"{boundary_summary.get('line1381_replacement_off_pi_over_four_parameter_count')}, "
                "proxy_t="
                f"{boundary_summary.get('line1381_unpriced_proxy_t_pressure')}"
            ),
        ),
        requirement(
            "S6",
            "Dropped overlap line 1378 remains unrecovered",
            boundary_summary.get("line1378_delta_recovered") is False,
            f"line1378_delta_recovered={boundary_summary.get('line1378_delta_recovered')}",
        ),
        requirement(
            "S7",
            "B7 ledger credit remains zero",
            boundary_summary.get("accepted_occurrence_removal") == 0
            and boundary_summary.get("accepted_proxy_t_reduction") == 0
            and boundary_summary.get("resource_saving_claimed") is False,
            (
                "occurrence="
                f"{boundary_summary.get('accepted_occurrence_removal')}, proxy_t="
                f"{boundary_summary.get('accepted_proxy_t_reduction')}"
            ),
        ),
        requirement(
            "S8",
            "All resource blockers are still open",
            boundary_summary.get("resource_boundary_blocker_count") == 5
            and boundary_summary.get("resource_boundary_failed_blocker_count") == 5,
            (
                "failed_blockers="
                f"{boundary_summary.get('resource_boundary_failed_blocker_count')}/"
                f"{boundary_summary.get('resource_boundary_blocker_count')}"
            ),
        ),
    ]
    failed = [row for row in requirements if not row["passed"]]

    errors: list[str] = []
    expected_statuses = {
        "reproduction": "cone01_openqasm3_qiskit_loader_evidence_seal_reproduced_without_b7_credit",
        "linear": "cone01_openqasm3_qiskit_loader_linear_span_replay_certificate_passed",
        "lift": "cone01_openqasm3_qiskit_loader_composable_patch_lift_supported_without_b7_credit",
        "boundary": "cone01_openqasm3_qiskit_loader_seeded_resource_boundary_no_b7_credit",
    }
    observed_statuses = {
        "reproduction": reproduction.get("status"),
        "linear": linear.get("status"),
        "lift": lift.get("status"),
        "boundary": boundary.get("status"),
    }
    for key, expected in expected_statuses.items():
        if observed_statuses[key] != expected:
            errors.append(f"{key} status expected {expected}, got {observed_statuses[key]}")
    errors.extend(f"{row['requirement_id']} failed: {row['name']}" for row in failed)

    summary = {
        "source_evidence_seal_reproduction_gate": rel(EVIDENCE_SEAL_REPRODUCTION),
        "source_linear_span_gate": rel(LINEAR_SPAN),
        "source_composable_lift_gate": rel(COMPOSABLE_LIFT),
        "source_seeded_resource_boundary_gate": rel(SEEDED_RESOURCE_BOUNDARY),
        "selected_line_numbers": lift_summary.get("selected_line_numbers"),
        "dropped_overlap_candidate_line_numbers": lift_summary.get(
            "dropped_overlap_candidate_line_numbers"
        ),
        "qiskit_loader_linear_span_dimension": linear_summary.get("linear_span_dimension"),
        "qiskit_loader_linear_span_error_spectral_norm": linear_summary.get(
            "linear_span_error_spectral_norm"
        ),
        "qiskit_loader_certified_input_subspace_fraction": lift_summary.get(
            "qiskit_loader_certified_input_subspace_fraction"
        ),
        "seeded_product_input_case_count": boundary_summary.get(
            "seeded_product_input_case_count"
        ),
        "seeded_product_min_state_fidelity": boundary_summary.get(
            "seeded_product_min_state_fidelity"
        ),
        "line1381_replacement_off_pi_over_four_parameter_count": boundary_summary.get(
            "line1381_replacement_off_pi_over_four_parameter_count"
        ),
        "line1381_unpriced_proxy_t_pressure": boundary_summary.get(
            "line1381_unpriced_proxy_t_pressure"
        ),
        "line1378_delta_recovered": boundary_summary.get("line1378_delta_recovered"),
        "resource_boundary_blocker_count": boundary_summary.get(
            "resource_boundary_blocker_count"
        ),
        "resource_boundary_failed_blocker_count": boundary_summary.get(
            "resource_boundary_failed_blocker_count"
        ),
        "accepted_claim_boundary_seal_count": 0 if errors else 1,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "claim_boundary_sealed": not errors,
        "validation_error_count": len(errors),
    }

    payload = {
        "benchmark_id": "B1",
        "linked_b7_problem_id": 21,
        "method": METHOD,
        "status": STATUS if not errors else "cone01_openqasm3_claim_boundary_seal_failed",
        "model_status": MODEL_STATUS if not errors else "qiskit_loader_claim_boundary_validation_failed",
        "workload": "qasmbench_medium_exact/gcm_h6.qasm",
        "claim_boundary": {
            "supported_claim": (
                "The current OpenQASM 3/Qiskit-loader evidence chain is coherent "
                "enough to cite as finite-span replay and seeded-product semantic "
                "pressure for the selected cone_01 patch lines."
            ),
            "claim_boundary_sealed": not errors,
            "qiskit_loader_replay_chain_citable": not errors,
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
            "unsupported_claims": [
                "No B7 resource reduction is accepted.",
                "No full-Hilbert-space symbolic equivalence theorem is claimed.",
                "No line-1381 local-U3 pricing certificate is accepted.",
                "No recovery of the dropped line-1378 overlap delta is recorded.",
                "No occurrence-removing certificate meeting the 30-window target exists.",
            ],
            "next_gate": (
                "Either price/remove the five line-1381 off-grid local-U3 parameters, "
                "recover line 1378 without overlap double-counting, or produce at least "
                "30 occurrence-removing certificates accepted by the refreshed B7 ledger."
            ),
        },
        "requirements": requirements,
        "summary": summary,
        "validation_errors": errors,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    if errors:
        raise SystemExit("claim-boundary seal validation failed: " + "; ".join(errors))


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    claims = payload["claim_boundary"]
    lines = [
        "# B1/B7 cone_01 OpenQASM 3 Claim-Boundary Seal Gate",
        "",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Workload: `{payload['workload']}`",
        f"- Supported claim: {claims['supported_claim']}",
        "",
        "## Source Gates",
        "",
        f"- Evidence-seal reproduction: `{summary['source_evidence_seal_reproduction_gate']}`",
        f"- Linear-span certificate: `{summary['source_linear_span_gate']}`",
        f"- Composable patch lift: `{summary['source_composable_lift_gate']}`",
        f"- Seeded resource boundary: `{summary['source_seeded_resource_boundary_gate']}`",
        "",
        "## Seal Requirements",
        "",
    ]
    for row in payload["requirements"]:
        lines.append(
            f"- `{row['requirement_id']}` {row['name']}: "
            f"`{row['passed']}`. {row['evidence']}"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Selected line numbers: `{summary['selected_line_numbers']}`",
            f"- Dropped overlap line numbers: `{summary['dropped_overlap_candidate_line_numbers']}`",
            (
                "- Qiskit-loader linear-span dimension / spectral error: "
                f"`{summary['qiskit_loader_linear_span_dimension']}` / "
                f"`{summary['qiskit_loader_linear_span_error_spectral_norm']}`"
            ),
            (
                "- Certified input-subspace fraction: "
                f"`{summary['qiskit_loader_certified_input_subspace_fraction']}`"
            ),
            (
                "- Seeded product cases / min fidelity: "
                f"`{summary['seeded_product_input_case_count']}` / "
                f"`{summary['seeded_product_min_state_fidelity']}`"
            ),
            (
                "- Line-1381 off-grid local-U3 parameters / proxy-T pressure: "
                f"`{summary['line1381_replacement_off_pi_over_four_parameter_count']}` / "
                f"`{summary['line1381_unpriced_proxy_t_pressure']}`"
            ),
            f"- Line-1378 delta recovered: `{summary['line1378_delta_recovered']}`",
            (
                "- Resource blockers still failed: "
                f"`{summary['resource_boundary_failed_blocker_count']}` / "
                f"`{summary['resource_boundary_blocker_count']}`"
            ),
            (
                "- Accepted occurrence / proxy-T reduction: "
                f"`{summary['accepted_occurrence_removal']}` / "
                f"`{summary['accepted_proxy_t_reduction']}`"
            ),
            f"- Accepted claim-boundary seal: `{summary['accepted_claim_boundary_seal_count']}`",
            "",
            "## Claim Boundary",
            "",
        ]
    )
    for claim in claims["unsupported_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            claims["next_gate"],
            "",
            "## Validation",
            "",
            f"- Claim boundary sealed: `{summary['claim_boundary_sealed']}`",
            f"- Validation errors: `{summary['validation_error_count']}`",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
