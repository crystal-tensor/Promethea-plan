#!/usr/bin/env python3
"""T-B3-023/T-B10-015j: extract one B3/B10 F1 pilot row candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


METHOD = "b3_b10_f1_pilot_row_candidate_gate_v0"
STATUS = "f1_pilot_row_candidate_extracted_zero_credit"
MODEL_STATUS = "one_of_four_f1_candidate_rows_extracted_from_existing_compiled_pilot"
SOURCE_TARGET_ID = "T-B3-023/T-B10-015j"
EXPECTED_F1_PACKET_ID = "B3B10-F1-full-compiled-state-covariance-rows"
EXPECTED_F1_PACKET_HASH = "dce2291e5ee21b7b2ccda8024d7da7afeb25565541e8dbe13035d1d9828612d7"
EXPECTED_SOURCE_METHOD = "b3_compiled_ucc_adapt_covariance_pilot_v0"
EXPECTED_ROW_COUNT = 4


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(
        payload,
        indent=2 if pretty else None,
        sort_keys=True,
        separators=None if pretty else (",", ":"),
    )
    path.write_text(text + "\n", encoding="utf-8")


def requirement(req_id: str, passed: bool, description: str, evidence: Any) -> dict[str, Any]:
    return {
        "id": req_id,
        "passed": bool(passed),
        "description": description,
        "evidence": evidence,
    }


def build_candidate_row(source_row: dict[str, Any], source_path: Path) -> dict[str, Any]:
    sampled_groups = source_row.get("sampled_groups", [])
    preview = sampled_groups[:8]
    row_id = "B3B10-F1-pilot-row-h2-ccpvdz-compiled-ucc-adapt-v0"
    candidate = {
        "candidate_row_id": row_id,
        "source_result": str(source_path),
        "source_method": EXPECTED_SOURCE_METHOD,
        "source_row_hash": canonical_hash(source_row),
        "molecule": source_row.get("molecule"),
        "coordinate": source_row.get("coordinate"),
        "coordinate_center": source_row.get("coordinate_center"),
        "selected_ci_basis": source_row.get("selected_ci_basis", "cc-pvdz"),
        "total_qubits": source_row.get("total_qubits", 20),
        "electrons": source_row.get("electrons"),
        "ansatz_model": source_row.get("ansatz_model"),
        "ansatz_theta": source_row.get("ansatz_theta"),
        "ansatz_parameter_count": 1,
        "converged_vqe_or_adapt_energy": False,
        "compiled_two_qubit_gates_per_preparation": source_row.get(
            "compiled_two_qubit_gates_per_preparation"
        ),
        "qwc_group_count_under_compiled_state": source_row.get(
            "qwc_group_count_under_compiled_state"
        ),
        "random_pauli_terms_under_compiled_state": source_row.get(
            "random_pauli_terms_under_compiled_state"
        ),
        "full_sampled_group_count": source_row.get("full_sampled_group_count"),
        "pilot_group_count": source_row.get("pilot_group_count"),
        "pilot_shots_per_group": source_row.get("pilot_shots_per_group"),
        "pilot_total_group_measurement_shots": source_row.get(
            "pilot_total_group_measurement_shots"
        ),
        "pilot_mean_relative_variance_error": source_row.get(
            "pilot_mean_relative_variance_error"
        ),
        "pilot_max_relative_variance_error": source_row.get(
            "pilot_max_relative_variance_error"
        ),
        "sampled_groups_hash": canonical_hash(sampled_groups),
        "sampled_group_preview_hash": canonical_hash(preview),
        "compiled_state_center_grouped_covariance_shot_floor": source_row.get(
            "compiled_state_center_grouped_covariance_shot_floor"
        ),
        "compiled_state_three_point_derivative_shot_floor": source_row.get(
            "compiled_state_three_point_derivative_shot_floor"
        ),
        "optimizer_loop_model": source_row.get("optimizer_loop_model"),
        "optimizer_iterations": source_row.get("optimizer_iterations"),
        "optimizer_evaluation_multiplier": source_row.get("optimizer_evaluation_multiplier"),
        "optimizer_loop_total_shots": source_row.get("optimizer_loop_total_shots"),
        "optimizer_loop_two_qubit_executions": source_row.get(
            "optimizer_loop_two_qubit_executions"
        ),
        "candidate_beats_selected_ci_larger_basis_denominator": source_row.get(
            "candidate_beats_selected_ci_larger_basis_denominator"
        ),
        "f1_candidate_limitations": [
            "one row only, while F1 requires four row-aligned instances",
            "one-parameter UCC/ADAPT seed, not a converged multi-parameter chemistry state",
            "sampled covariance covers pilot groups, not every group as a submitted F1 artifact",
            "no accepted same-access denominator win",
        ],
    }
    candidate["candidate_row_hash"] = canonical_hash(candidate)
    return candidate


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    source = load_json(args.compiled_pilot)
    f1_gate = load_json(args.f1_packet_gate)
    rows = source.get("rows", [])
    source_row = rows[0] if rows else {}
    candidate = build_candidate_row(source_row, args.compiled_pilot) if source_row else {}
    source_summary = source.get("summary", {})
    f1_summary = f1_gate.get("summary", {})

    candidate_count = 1 if candidate else 0
    missing_count = max(0, EXPECTED_ROW_COUNT - candidate_count)
    submitted_f1_artifact_exists = bool(f1_summary.get("submitted_f1_artifact_exists"))
    accepted_f1_rows = bool(f1_summary.get("f1_full_covariance_rows_accepted"))
    no_claims = (
        source_summary.get("quantum_advantage_claimed") is False
        and source_summary.get("reaction_dynamics_solution_claimed") is False
        and source_summary.get("selected_ci_larger_basis_denominator_beaten_count") == 0
        and f1_summary.get("b10_t1_credit_allowed") is False
    )

    requirements = [
        requirement(
            "P1",
            source.get("method") == EXPECTED_SOURCE_METHOD and not source.get("validation_errors"),
            "Compiled UCC/ADAPT pilot source is valid",
            {
                "method": source.get("method"),
                "validation_error_count": len(source.get("validation_errors", [])),
                "source_file_hash": file_hash(args.compiled_pilot),
            },
        ),
        requirement(
            "P2",
            f1_summary.get("f1_packet_hash") == EXPECTED_F1_PACKET_HASH
            and f1_summary.get("f1_packet_id") == EXPECTED_F1_PACKET_ID,
            "Candidate row is bound to the locked F1 packet",
            {
                "f1_packet_id": f1_summary.get("f1_packet_id"),
                "f1_packet_hash": f1_summary.get("f1_packet_hash"),
            },
        ),
        requirement(
            "P3",
            candidate_count == 1
            and candidate.get("molecule") == "h2_bond_stretch"
            and candidate.get("selected_ci_basis") == "cc-pvdz",
            "One H2/cc-pVDZ candidate row is extracted",
            {
                "candidate_row_count": candidate_count,
                "candidate_row_id": candidate.get("candidate_row_id"),
                "candidate_row_hash": candidate.get("candidate_row_hash"),
            },
        ),
        requirement(
            "P4",
            bool(candidate)
            and candidate.get("pilot_group_count") == 48
            and candidate.get("pilot_shots_per_group") == 512
            and candidate.get("pilot_max_relative_variance_error", 1.0) < 0.1,
            "Pilot sampled covariance evidence is present and below the preview error cap",
            {
                "pilot_group_count": candidate.get("pilot_group_count"),
                "pilot_shots_per_group": candidate.get("pilot_shots_per_group"),
                "pilot_max_relative_variance_error": candidate.get(
                    "pilot_max_relative_variance_error"
                ),
                "sampled_groups_hash": candidate.get("sampled_groups_hash"),
            },
        ),
        requirement(
            "P5",
            bool(candidate)
            and candidate.get("compiled_state_center_grouped_covariance_shot_floor", 0) > 0
            and candidate.get("compiled_state_three_point_derivative_shot_floor", 0) > 0,
            "Compiled-state covariance and derivative shot floors are carried forward",
            {
                "center_shot_floor": candidate.get(
                    "compiled_state_center_grouped_covariance_shot_floor"
                ),
                "derivative_shot_floor": candidate.get(
                    "compiled_state_three_point_derivative_shot_floor"
                ),
            },
        ),
        requirement(
            "P6",
            bool(candidate)
            and candidate.get("optimizer_loop_total_shots", 0) > 0
            and candidate.get("optimizer_loop_two_qubit_executions", 0) > 0,
            "Optimizer-loop cost ledger remains charged",
            {
                "optimizer_loop_total_shots": candidate.get("optimizer_loop_total_shots"),
                "optimizer_loop_two_qubit_executions": candidate.get(
                    "optimizer_loop_two_qubit_executions"
                ),
            },
        ),
        requirement(
            "P7",
            no_claims,
            "No reaction-dynamics, denominator-win, quantum-advantage, or B10 credit claim is made",
            {
                "selected_ci_larger_basis_denominator_beaten_count": source_summary.get(
                    "selected_ci_larger_basis_denominator_beaten_count"
                ),
                "reaction_dynamics_solution_claimed": source_summary.get(
                    "reaction_dynamics_solution_claimed"
                ),
                "quantum_advantage_claimed": source_summary.get("quantum_advantage_claimed"),
                "b10_t1_credit_allowed": f1_summary.get("b10_t1_credit_allowed"),
            },
        ),
        requirement(
            "P8",
            candidate_count == EXPECTED_ROW_COUNT,
            "F1 four-row scope is complete",
            {
                "candidate_row_count": candidate_count,
                "required_row_count": EXPECTED_ROW_COUNT,
                "missing_row_count": missing_count,
            },
        ),
        requirement(
            "P9",
            submitted_f1_artifact_exists,
            "Source-backed F1 artifact has been submitted",
            {
                "submitted_f1_artifact_exists": submitted_f1_artifact_exists,
                "expected_packet_id": EXPECTED_F1_PACKET_ID,
            },
        ),
        requirement(
            "P10",
            accepted_f1_rows,
            "Candidate row is accepted as part of the F1 artifact",
            {
                "f1_full_covariance_rows_accepted": accepted_f1_rows,
                "accepted_full_covariance_row_count": f1_summary.get(
                    "accepted_full_covariance_row_count"
                ),
            },
        ),
    ]

    failed = [item["id"] for item in requirements if not item["passed"]]
    validation_errors: list[str] = []
    if failed != ["P8", "P9", "P10"]:
        validation_errors.append(f"unexpected_failed_requirement_ids:{failed}")
    if candidate_count != 1:
        validation_errors.append(f"unexpected_candidate_row_count:{candidate_count}")
    if f1_summary.get("accepted_full_covariance_row_count") != 0:
        validation_errors.append("accepted row count must remain zero")

    summary = {
        "candidate_row_count": candidate_count,
        "required_f1_row_count": EXPECTED_ROW_COUNT,
        "missing_f1_row_count": missing_count,
        "candidate_row_id": candidate.get("candidate_row_id"),
        "candidate_row_hash": candidate.get("candidate_row_hash"),
        "source_compiled_pilot_hash": file_hash(args.compiled_pilot),
        "source_f1_packet_hash": f1_summary.get("f1_packet_hash"),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "failed_requirement_ids": failed,
        "pilot_group_count": candidate.get("pilot_group_count"),
        "pilot_shots_per_group": candidate.get("pilot_shots_per_group"),
        "pilot_max_relative_variance_error": candidate.get("pilot_max_relative_variance_error"),
        "compiled_state_center_grouped_covariance_shot_floor": candidate.get(
            "compiled_state_center_grouped_covariance_shot_floor"
        ),
        "compiled_state_three_point_derivative_shot_floor": candidate.get(
            "compiled_state_three_point_derivative_shot_floor"
        ),
        "optimizer_loop_total_shots": candidate.get("optimizer_loop_total_shots"),
        "optimizer_loop_two_qubit_executions": candidate.get(
            "optimizer_loop_two_qubit_executions"
        ),
        "accepted_full_covariance_row_count": 0,
        "denominator_win_count": 0,
        "b3_reopen_ready": False,
        "b10_t1_credit_allowed": False,
        "quantum_advantage_claimed": False,
        "reaction_dynamics_solution_claimed": False,
        "bqp_separation_claimed": False,
        "validation_error_count": len(validation_errors),
    }

    return {
        "benchmark_id": "B3_B10",
        "problem_ids": ["B3", "B10"],
        "source_target_id": SOURCE_TARGET_ID,
        "title": "B3/B10 F1 Pilot Row Candidate Gate",
        "version": "0.1",
        "last_updated": args.last_updated,
        "status": STATUS,
        "method": METHOD,
        "model_status": MODEL_STATUS,
        "source_compiled_pilot": str(args.compiled_pilot),
        "source_f1_packet_gate": str(args.f1_packet_gate),
        "candidate_row": candidate,
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "One existing H2/cc-pVDZ compiled one-parameter UCC/ADAPT pilot row is "
                "extracted as a candidate row for the F1 full-covariance packet."
            ),
            "what_is_not_supported": (
                "This is not a submitted F1 artifact, not four row-aligned F1 rows, not an "
                "accepted full-covariance row, not a denominator win, not a B3 reopen, not "
                "B10-T1 credit, and not quantum advantage or BQP separation."
            ),
            "next_gate": (
                "Add three more source-backed row candidates and package all four into the "
                "locked F1 artifact with replay hashes, denominator contract, optimizer ledger, "
                "and claim boundary."
            ),
        },
        "validation_errors": validation_errors,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    candidate = payload["candidate_row"]
    lines = [
        "# B3/B10 F1 Pilot Row Candidate Gate",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Candidate row: `{summary['candidate_row_id']}`",
        f"- Candidate row hash: `{summary['candidate_row_hash']}`",
        f"- Source F1 packet hash: `{summary['source_f1_packet_hash']}`",
        "",
        "## Result",
        "",
        (
            "The gate extracts one source-backed pilot row candidate from the existing "
            "compiled UCC/ADAPT covariance pilot. It passes "
            f"{summary['requirements_passed']}/"
            f"{summary['requirements_passed'] + summary['requirements_failed']} "
            "requirements and intentionally fails "
            f"{summary['failed_requirement_ids']} because F1 still needs four row-aligned rows "
            "and a submitted source-backed artifact."
        ),
        "",
        "## Candidate Row",
        "",
        f"- Molecule / basis: `{candidate.get('molecule')}` / `{candidate.get('selected_ci_basis')}`",
        f"- Ansatz: `{candidate.get('ansatz_model')}` at theta `{candidate.get('ansatz_theta')}`",
        f"- Pilot groups / shots per group: `{summary['pilot_group_count']}` / `{summary['pilot_shots_per_group']}`",
        f"- Pilot max relative variance error: `{summary['pilot_max_relative_variance_error']}`",
        f"- Center covariance shot floor: `{summary['compiled_state_center_grouped_covariance_shot_floor']}`",
        f"- Derivative shot floor: `{summary['compiled_state_three_point_derivative_shot_floor']}`",
        f"- Optimizer-loop shots: `{summary['optimizer_loop_total_shots']}`",
        f"- Optimizer-loop 2Q executions: `{summary['optimizer_loop_two_qubit_executions']}`",
        "",
        "## Requirement Results",
        "",
    ]
    for req in payload["requirements"]:
        status = "PASS" if req["passed"] else "FAIL"
        lines.append(f"- `{req['id']}` {status}: {req['description']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            "This candidate gate does not claim a reaction-dynamics solution, quantum advantage, B3 reopen credit, B10-T1 credit, or BQP separation.",
            "",
            "## Validation",
            "",
            f"- validation_error_count: `{summary['validation_error_count']}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compiled-pilot",
        type=Path,
        default=Path("results/B3_compiled_ucc_adapt_covariance_pilot_v0.json"),
    )
    parser.add_argument(
        "--f1-packet-gate",
        type=Path,
        default=Path("results/B3_B10_F1_full_covariance_row_packet_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B3_B10_F1_pilot_row_candidate_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B3_B10_F1_pilot_row_candidate_gate.md"),
    )
    parser.add_argument("--last-updated", default="2026-07-03")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args)
    write_json(args.json_output, payload, args.pretty)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "candidate_row_hash": payload["summary"]["candidate_row_hash"],
                "requirements_passed": payload["summary"]["requirements_passed"],
                "requirements_failed": payload["summary"]["requirements_failed"],
                "failed_requirement_ids": payload["summary"]["failed_requirement_ids"],
                "validation_error_count": payload["summary"]["validation_error_count"],
                "json_output": str(args.json_output),
                "markdown_output": str(args.markdown_output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    if payload["validation_errors"]:
        raise SystemExit("B3/B10 F1 pilot row candidate gate validation failed")


if __name__ == "__main__":
    main()
