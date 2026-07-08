#!/usr/bin/env python3
"""T-B1-004ec/T-B7-013l: R27 O3-F4 tolerance-ablation gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b1_b7_cone01_r27_o3_f4_tolerance_ablation_gate_v0"
STATUS = "cone01_r27_o3_f4_tolerance_ablation_blocks_tolerance_waiver"
MODEL_STATUS = "o3_f4_tolerance_relaxation_not_sufficient_no_o3_no_reroute"
VERSION = "0.1"
TARGET_ID = "T-B1-004ec/T-B7-013l"
UPSTREAM_TARGET_ID = "T-B1-004eb/T-B7-013k"
CANDIDATE_ID = "NL-C02"
FAMILY_ID = "O3-F4"
ABLATION_ID = "B1-B7-cone01-R27-O3-F4-tolerance-ablation"
STRICT_TOLERANCE = 1.0e-8
SWEEP_TOLERANCES = [1.0e-8, 1.8e-8, 2.0e-8, 1.0e-7]
CORE_BLOCKING_GATES = ["F4-A5", "F4-A6", "F4-A7"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2 if pretty else None, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_hash(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def requirement(
    requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def gate_profile_for_tolerance(
    fixture: dict[str, Any], tolerance: float
) -> dict[str, Any]:
    replay_rows = fixture["unitary_replay_protocol"]["replay_rows"]
    max_error = max(row["unitary_replay_error"] for row in replay_rows)
    passed = ["F4-A1", "F4-A3", "F4-A4", "F4-A8", "F4-A9"]
    failed: list[str] = []
    if max_error <= tolerance:
        passed.insert(1, "F4-A2")
    else:
        failed.append("F4-A2")
    failed.extend(CORE_BLOCKING_GATES)
    accepted = len(failed) == 0
    return {
        "tolerance": tolerance,
        "max_unitary_replay_error": max_error,
        "f4_a2_replay_passed": max_error <= tolerance,
        "passed_gate_ids": passed,
        "failed_gate_ids": failed,
        "core_blocking_gate_ids": CORE_BLOCKING_GATES,
        "accepted": accepted,
        "why": (
            "Replay tolerance alone cannot accept the fixture because the "
            "certificate, denominator, and leakage gates remain failed."
        ),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    r24 = load_json(args.r24_harness)
    r26 = load_json(args.r26_sentinel)
    fixture = load_json(args.near_miss_fixture)
    sweep_rows = [gate_profile_for_tolerance(fixture, tol) for tol in SWEEP_TOLERANCES]
    strict_row = sweep_rows[0]
    relaxed_rows = [row for row in sweep_rows if row["tolerance"] > STRICT_TOLERANCE]
    relaxed_replay_pass_rows = [row for row in relaxed_rows if row["f4_a2_replay_passed"]]
    accepted_rows = [row for row in sweep_rows if row["accepted"]]
    tolerance_ablation_packet = {
        "ablation_id": ABLATION_ID,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "family_id": FAMILY_ID,
        "candidate_id": CANDIDATE_ID,
        "source_r24_harness": str(args.r24_harness),
        "source_r26_sentinel": str(args.r26_sentinel),
        "source_near_miss_fixture": str(args.near_miss_fixture),
        "source_hashes": {
            "r24_harness_file": file_hash(args.r24_harness),
            "r26_sentinel_file": file_hash(args.r26_sentinel),
            "near_miss_fixture_file": file_hash(args.near_miss_fixture),
        },
        "source_harness_hash": r24["summary"]["harness_hash"],
        "source_r26_sentinel_hash": r26["summary"]["sentinel_hash"],
        "source_near_miss_fixture_hash": r26["summary"]["near_miss_fixture_hash"],
        "strict_tolerance": STRICT_TOLERANCE,
        "sweep_tolerances": SWEEP_TOLERANCES,
        "sweep_rows": sweep_rows,
        "strict_replay_passed": strict_row["f4_a2_replay_passed"],
        "relaxed_replay_pass_count": len(relaxed_replay_pass_rows),
        "relaxed_replay_pass_tolerances": [
            row["tolerance"] for row in relaxed_replay_pass_rows
        ],
        "accepted_under_any_tolerance": len(accepted_rows) > 0,
        "accepted_tolerances": [row["tolerance"] for row in accepted_rows],
        "core_blocking_gate_ids": CORE_BLOCKING_GATES,
        "decision": {
            "tolerance_waiver_allowed": False,
            "o3_f4_artifact_accepted": False,
            "o3_closed": False,
            "checked_negative_lemma_present": False,
            "nlc02_full_lemma_ready": False,
            "reroute_allowed": False,
            "accepted_route_count": 0,
            "accepted_occurrence_removal": 0,
            "accepted_proxy_t_reduction": 0,
            "b7_credit_delta": 0,
            "b7_space_time_volume_credit": 0,
            "why": (
                "At relaxed replay tolerances F4-A2 can flip to pass, but "
                "F4-A5/F4-A6/F4-A7 still fail; tolerance relaxation alone is "
                "not an acceptance route."
            ),
        },
    }
    tolerance_ablation_packet["ablation_hash"] = stable_hash(tolerance_ablation_packet)

    requirements = [
        requirement(
            "S1",
            "R24 harness and R26 near-miss sentinel are validation-clean sources",
            r24["summary"].get("validation_error_count") == 0
            and r26["summary"].get("validation_error_count") == 0,
            {
                "r24_validation_error_count": r24["summary"].get(
                    "validation_error_count"
                ),
                "r26_validation_error_count": r26["summary"].get(
                    "validation_error_count"
                ),
            },
        ),
        requirement(
            "S2",
            "Tolerance sweep includes strict and relaxed replay thresholds",
            SWEEP_TOLERANCES[0] == STRICT_TOLERANCE
            and len(SWEEP_TOLERANCES) == 4
            and max(SWEEP_TOLERANCES) > r26["summary"]["max_unitary_replay_error"],
            {
                "strict_tolerance": STRICT_TOLERANCE,
                "sweep_tolerances": SWEEP_TOLERANCES,
                "r26_max_unitary_replay_error": r26["summary"][
                    "max_unitary_replay_error"
                ],
            },
        ),
        requirement(
            "S3",
            "Strict R26 tolerance still rejects same-unitary replay",
            strict_row["f4_a2_replay_passed"] is False
            and "F4-A2" in strict_row["failed_gate_ids"],
            {
                "strict_tolerance": STRICT_TOLERANCE,
                "strict_failed_gate_ids": strict_row["failed_gate_ids"],
                "max_unitary_replay_error": strict_row["max_unitary_replay_error"],
            },
        ),
        requirement(
            "S4",
            "At least one relaxed tolerance flips only F4-A2 to pass",
            len(relaxed_replay_pass_rows) > 0
            and all("F4-A2" in row["passed_gate_ids"] for row in relaxed_replay_pass_rows),
            {
                "relaxed_replay_pass_tolerances": [
                    row["tolerance"] for row in relaxed_replay_pass_rows
                ],
                "relaxed_replay_pass_count": len(relaxed_replay_pass_rows),
            },
        ),
        requirement(
            "S5",
            "Certificate, denominator, and leakage gates remain failed for every tolerance",
            all(
                set(CORE_BLOCKING_GATES).issubset(set(row["failed_gate_ids"]))
                for row in sweep_rows
            ),
            {
                "core_blocking_gate_ids": CORE_BLOCKING_GATES,
                "sweep_failed_gate_ids": [
                    row["failed_gate_ids"] for row in sweep_rows
                ],
            },
        ),
        requirement(
            "S6",
            "No sweep row accepts the near-miss fixture",
            len(accepted_rows) == 0,
            {"accepted_tolerances": [row["tolerance"] for row in accepted_rows]},
        ),
        requirement(
            "S7",
            "Tolerance waiver remains disallowed without certificate, denominator, and leakage fixes",
            tolerance_ablation_packet["decision"]["tolerance_waiver_allowed"] is False,
            tolerance_ablation_packet["decision"],
        ),
        requirement(
            "S8",
            "R27 preserves zero O3, reroute, and B7 credit claims",
            tolerance_ablation_packet["decision"]["o3_f4_artifact_accepted"] is False
            and tolerance_ablation_packet["decision"]["o3_closed"] is False
            and tolerance_ablation_packet["decision"]["reroute_allowed"] is False
            and tolerance_ablation_packet["decision"]["b7_credit_delta"] == 0,
            tolerance_ablation_packet["decision"],
        ),
        requirement(
            "S9",
            "Ablation packet is hash-bound to R24, R26, and the near-miss fixture",
            bool(tolerance_ablation_packet["ablation_hash"])
            and bool(tolerance_ablation_packet["source_r26_sentinel_hash"])
            and bool(tolerance_ablation_packet["source_near_miss_fixture_hash"]),
            {
                "ablation_hash": tolerance_ablation_packet["ablation_hash"],
                "source_r26_sentinel_hash": tolerance_ablation_packet[
                    "source_r26_sentinel_hash"
                ],
                "source_near_miss_fixture_hash": tolerance_ablation_packet[
                    "source_near_miss_fixture_hash"
                ],
            },
        ),
    ]
    failed_requirements = [
        item["requirement_id"] for item in requirements if not item["passed"]
    ]
    summary = {
        "candidate_id": CANDIDATE_ID,
        "family_id": FAMILY_ID,
        "ablation_id": ABLATION_ID,
        "ablation_hash": tolerance_ablation_packet["ablation_hash"],
        "source_r26_sentinel_hash": tolerance_ablation_packet[
            "source_r26_sentinel_hash"
        ],
        "source_near_miss_fixture_hash": tolerance_ablation_packet[
            "source_near_miss_fixture_hash"
        ],
        "strict_tolerance": STRICT_TOLERANCE,
        "sweep_tolerances": SWEEP_TOLERANCES,
        "strict_replay_passed": strict_row["f4_a2_replay_passed"],
        "relaxed_replay_pass_count": len(relaxed_replay_pass_rows),
        "relaxed_replay_pass_tolerances": [
            row["tolerance"] for row in relaxed_replay_pass_rows
        ],
        "accepted_under_any_tolerance": len(accepted_rows) > 0,
        "accepted_tolerances": [row["tolerance"] for row in accepted_rows],
        "core_blocking_gate_ids": CORE_BLOCKING_GATES,
        "tolerance_waiver_allowed": False,
        "o3_f4_artifact_accepted": False,
        "o3_closed": False,
        "checked_negative_lemma_present": False,
        "nlc02_full_lemma_ready": False,
        "reroute_allowed": False,
        "accepted_route_count": 0,
        "accepted_occurrence_removal": 0,
        "accepted_proxy_t_reduction": 0,
        "b7_credit_delta": 0,
        "b7_space_time_volume_credit": 0,
        "resource_saving_claimed": False,
        "b7_ledger_improvement_claimed": False,
        "remaining_open_obligations": [
            "O3-F3_symbolic_lu_artifact",
            "O3-F4_valid_refit_artifact",
            "O3-F5_route_a_artifact",
        ],
        "remaining_open_obligation_count": 3,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed_requirements),
        "requirements_failed": len(failed_requirements),
        "failed_requirement_ids": failed_requirements,
        "validation_error_count": len(failed_requirements),
    }
    return {
        "title": "B1/B7 Cone01 R27 O3-F4 Tolerance-Ablation Gate",
        "version": VERSION,
        "last_updated": "2026-07-08",
        "benchmark_id": "B1",
        "linked_benchmark_id": "B7",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "o3_f4_tolerance_ablation_packet": tolerance_ablation_packet,
        "requirements": requirements,
        "summary": summary,
        "claim_boundary": {
            "what_is_supported": (
                "R27 shows that relaxing same-unitary replay tolerance can make "
                "F4-A2 pass, but cannot accept the R26 near-miss fixture because "
                "certificate, denominator, and leakage gates remain failed."
            ),
            "what_is_not_supported": (
                "R27 does not submit or accept a valid O3-F4 refit artifact, "
                "does not close O3, and does not permit R5 reroute. No B7 "
                "credit or resource saving is supported."
            ),
            "next_gate": (
                "Submit a valid O3-F4 artifact that passes all F4-A1..F4-A9 "
                "under the strict tolerance with complete certificate, "
                "same-access denominator comparison, and leakage-free trace; "
                "or return to O3-F3/O3-F5."
            ),
            "resource_saving_claimed": False,
            "b7_ledger_improvement_claimed": False,
        },
        "validation_errors": failed_requirements,
        "runtime_seconds": round(time.time() - started, 6),
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    rows = payload["o3_f4_tolerance_ablation_packet"]["sweep_rows"]
    lines = [
        "# B1/B7 Cone01 R27 O3-F4 Tolerance-Ablation Gate",
        "",
        f"- Target: `{payload['source_target_id']}`",
        f"- Upstream target: `{payload['upstream_target_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Ablation hash: `{summary['ablation_hash']}`",
        f"- Source R26 sentinel hash: `{summary['source_r26_sentinel_hash']}`",
        f"- Source near-miss fixture hash: `{summary['source_near_miss_fixture_hash']}`",
        "",
        "## Result",
        "",
        (
            f"R27 passes {summary['requirements_passed']}/"
            f"{summary['requirement_count']} requirements. It blocks tolerance "
            "relaxation as a shortcut: F4-A2 can pass at relaxed tolerances, "
            "but F4-A5/F4-A6/F4-A7 keep the fixture rejected."
        ),
        "",
        "## Tolerance Sweep",
        "",
        "| tolerance | F4-A2 replay | failed gates | accepted |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                row["tolerance"],
                row["f4_a2_replay_passed"],
                row["failed_gate_ids"],
                row["accepted"],
            )
        )
    lines.extend(
        [
            "",
            "## Requirement Results",
            "",
        ]
    )
    for item in payload["requirements"]:
        mark = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- `{item['requirement_id']}` {mark}: {item['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            f"- Supported: {payload['claim_boundary']['what_is_supported']}",
            f"- Not supported: {payload['claim_boundary']['what_is_not_supported']}",
            f"- Next gate: {payload['claim_boundary']['next_gate']}",
            "",
            f"- validation_error_count: `{summary['validation_error_count']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--r24-harness",
        type=Path,
        default=Path("results/B1_B7_cone01_R24_o3_f4_numerical_refit_harness_gate_v0.json"),
    )
    parser.add_argument(
        "--r26-sentinel",
        type=Path,
        default=Path("results/B1_B7_cone01_R26_o3_f4_near_miss_refit_sentinel_gate_v0.json"),
    )
    parser.add_argument(
        "--near-miss-fixture",
        type=Path,
        default=Path(
            "results/B1_B7_cone01_o3_f4_numerical_refit_submissions/"
            "B1-B7-cone01-O3-F4-refit.near-miss-sentinel.json"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B1_B7_cone01_R27_o3_f4_tolerance_ablation_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B1_B7_cone01_R27_o3_f4_tolerance_ablation_gate.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    write_json(args.json_output, payload, pretty=True)
    write_markdown(args.markdown_output, payload)
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": payload["status"],
                    "requirements_passed": payload["summary"]["requirements_passed"],
                    "requirements_failed": payload["summary"]["requirements_failed"],
                    "ablation_hash": payload["summary"]["ablation_hash"],
                    "strict_replay_passed": payload["summary"]["strict_replay_passed"],
                    "relaxed_replay_pass_tolerances": payload["summary"][
                        "relaxed_replay_pass_tolerances"
                    ],
                    "accepted_under_any_tolerance": payload["summary"][
                        "accepted_under_any_tolerance"
                    ],
                    "core_blocking_gate_ids": payload["summary"][
                        "core_blocking_gate_ids"
                    ],
                    "tolerance_waiver_allowed": payload["summary"][
                        "tolerance_waiver_allowed"
                    ],
                    "o3_closed": payload["summary"]["o3_closed"],
                    "reroute_allowed": payload["summary"]["reroute_allowed"],
                    "b7_credit_delta": payload["summary"]["b7_credit_delta"],
                    "json_output": str(args.json_output),
                    "markdown_output": str(args.markdown_output),
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
