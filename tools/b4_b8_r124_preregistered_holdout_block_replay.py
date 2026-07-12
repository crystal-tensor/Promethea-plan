#!/usr/bin/env python3
"""T-B4-002y/T-B8-003ac: execute the publicly preregistered R124 holdout."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qasm3
from qiskit_aer import AerSimulator

from b4_b8_r119_private_observable_bundle_gate import build_bundle_tasks
from b4_b8_r121_private_bundle_shot_sweep import (
    PROFILES,
    noise_model,
    stable_hash,
    write_json,
)
from b4_b8_r122_matched_seed_prefix_replay import (
    bundle_error,
    choose_bundle,
    matched_prefix_records,
    target_values,
)
from b4_b8_r123_independent_seed_block_replay import aggregate_task_rows


METHOD = "b4_b8_r124_preregistered_holdout_block_replay_v0"
STATUS = "preregistered_disjoint_holdout_block_acceptance_boundary"
MODEL_STATUS = "publicly_preregistered_r123_boundary_replay_on_disjoint_seed_blocks"
TARGET_ID = "T-B4-002y/T-B8-003ac/T-B10-009q"
UPSTREAM_TARGET_ID = "T-B4-002x/T-B8-003ab/T-B10-009p"
R123_RESULT_PATH = "results/B4_B8_R123_independent_seed_block_replay_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R124_block_robust_acceptance_contract_v0.json"
CONTRACT_SHA256 = "18da0e4fe50a98f2830782c04563102371a608e87a0e5859c9b5a65839693604"
PREREGISTRATION_DISCUSSION = "https://github.com/crystal-tensor/Prometheus-plan/discussions/124"
PREREGISTRATION_CREATED_AT = "2026-07-12T10:22:59Z"
OUT_DIR = "results/B4_B8_R124_preregistered_holdout_block_replay"
RESULT_PATH = "results/B4_B8_R124_preregistered_holdout_block_replay_v0.json"
REPORT_PATH = "research/B4_B8_R124_preregistered_holdout_block_replay.md"


def contract_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def condition_row(
    condition_id: str, label: str, value: float | int | bool, threshold: Any, passed: bool
) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "label": label,
        "value": value,
        "threshold": threshold,
        "passed": passed,
    }


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = []
    for profile_name, profile in summary["profiles"].items():
        for shots in summary["shot_budgets"]:
            row = profile["by_shot_budget"][str(shots)]
            lines.append(
                f"- `{profile_name}` / `{shots}`: pooled point "
                f"`{row['minimum_pooled_honest_completeness']:.4f}`, pooled "
                f"Wilson lower `{row['minimum_pooled_wilson_lower']:.4f}`, "
                f"minimum leave-one-block-out lower "
                f"`{row['minimum_leave_one_block_out_wilson_lower']:.4f}`, "
                f"blocks above floor `{row['blocks_meeting_point_floor']}/"
                f"{summary['seed_block_count']}`."
            )
        lines.append(
            f"- `{profile_name}` preregistered decision: "
            f"`{'ACCEPT' if profile['profile_accepted'] else 'REJECT'}`; "
            + ", ".join(
                f"{row['condition_id']}={'PASS' if row['passed'] else 'FAIL'}"
                for row in profile["acceptance_conditions"]
            )
        )

    requirements = "\n".join(
        f"- `{row['requirement_id']}` "
        f"{'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    verdict = "ACCEPT" if summary["global_acceptance"] else "REJECT"
    return f"""# B4/B8 R124 Preregistered Holdout Block Replay

## Summary

- Target: `{TARGET_ID}`
- Upstream target: `{UPSTREAM_TARGET_ID}`
- Method: `{METHOD}`
- Status: `{STATUS}`
- Public preregistration: {PREREGISTRATION_DISCUSSION}
- Contract SHA-256: `{payload['contract']['sha256']}`
- Holdout seed blocks: `{summary['seed_block_count']}`
- Trials per block/profile/task: `{summary['trials_per_block_profile_task']}`
- Total trial rows: `{len(payload['trial_rows'])}`
- Control / candidate shots: `{summary['control_shot_budget']}` / `{summary['candidate_shot_budget']}`
- Global preregistered verdict: `{verdict}`
- Fail-to-pass / pass-to-fail transitions: `{summary['fail_to_pass_transition_count']}` / `{summary['pass_to_fail_transition_count']}`

{chr(10).join(lines)}

R124 was publicly preregistered before holdout execution. The contract fixes the
root seeds, trial count, profiles, tasks, shot budgets, error tolerance, Wilson
confidence rule, leave-one-block-out rule, all-block point rule, and paired
regression ceiling. Seeds may not be replaced and thresholds may not be revised
after observing the holdout.

## Requirements

{requirements}

## Claim Boundary

Supported: one publicly preregistered synthetic Aer holdout verdict for the
fixed tasks, profiles, and 8,192-shot candidate. Not supported: an iid theorem,
universal shot threshold, calibrated backend evidence, real hardware execution,
protocol or cryptographic soundness, sampling hardness, quantum advantage, BQP
separation, or B10 credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    started_at = int(time.time())
    root = root.resolve()
    contract_file = root / CONTRACT_PATH
    observed_contract_hash = contract_hash(contract_file)
    if observed_contract_hash != CONTRACT_SHA256:
        raise ValueError("R124 preregistration contract hash mismatch")
    contract = json.loads(contract_file.read_text(encoding="utf-8"))
    r123 = json.loads((root / R123_RESULT_PATH).read_text(encoding="utf-8"))
    if r123.get("status") != "independent_seed_block_confidence_stability_boundary":
        raise ValueError("R124 requires the accepted R123 block boundary")
    if r123.get("payload_hash") != contract["source_payload_hash"]:
        raise ValueError("R124 contract does not bind the current R123 payload")

    design = contract["holdout_design"]
    statistic = contract["acceptance_statistic"]
    block_seeds = design["root_seeds"]
    trials_per_block = design["trials_per_block_profile_task"]
    control_shots = design["control_shot_budget"]
    candidate_shots = design["candidate_shot_budget"]
    shot_budgets = [control_shots, candidate_shots]
    tolerance = statistic["bundle_maximum_absolute_error_tolerance"]
    honest_floor = statistic["honest_completeness_floor"]
    maximum_regressions = statistic["maximum_pass_to_fail_transitions_per_profile"]
    preregistered_at = int(
        datetime.fromisoformat(
            PREREGISTRATION_CREATED_AT.replace("Z", "+00:00")
        ).astimezone(timezone.utc).timestamp()
    )
    if preregistered_at >= started_at:
        raise ValueError("R124 preregistration timestamp is not before execution")

    output = root / OUT_DIR
    if output.exists():
        shutil.rmtree(output)
    circuits_dir = output / "circuits"
    circuits_dir.mkdir(parents=True)

    tasks = build_bundle_tasks()
    if [task["task_id"] for task in tasks] != design["task_ids"]:
        raise ValueError("R124 task set drifted from preregistration")
    if set(PROFILES) != set(design["profiles"]):
        raise ValueError("R124 profile set drifted from preregistration")

    trial_rows: list[dict[str, Any]] = []
    circuit_files: list[str] = []
    for profile_index, (profile_name, profile) in enumerate(PROFILES.items()):
        if profile != design["profiles"][profile_name]:
            raise ValueError(f"R124 profile parameters drifted for {profile_name}")
        simulator = AerSimulator(
            noise_model=noise_model(profile),
            method="density_matrix",
        )
        for task_index, task in enumerate(tasks):
            base = task["circuit"]
            path = circuits_dir / f"{profile_name}_{task['task_id']}.qasm"
            path.write_text(qasm3.dumps(base), encoding="utf-8")
            circuit_files.append(str(path.relative_to(root)))
            exact_values = target_values(task)
            cache = {}
            for block_index, block_seed in enumerate(block_seeds):
                for trial in range(trials_per_block):
                    seed_components = [
                        block_seed,
                        profile_index,
                        task_index,
                        trial,
                    ]
                    rng = np.random.default_rng(np.random.SeedSequence(seed_components))
                    bundle, bundle_choice = choose_bundle(task, rng)
                    records, schedule_hash = matched_prefix_records(
                        base, simulator, rng, cache
                    )
                    by_budget = {}
                    for shots in shot_budgets:
                        error = bundle_error(records[:shots], bundle, exact_values)
                        by_budget[str(shots)] = {
                            "maximum_bundle_error": error,
                            "passed": error <= tolerance,
                        }
                    trial_rows.append(
                        {
                            "block_index": block_index,
                            "block_seed": block_seed,
                            "profile": profile_name,
                            "task_id": task["task_id"],
                            "trial": trial,
                            "trial_seed_components": seed_components,
                            "schedule_sha256": schedule_hash,
                            "bundle_choice": bundle_choice,
                            "budgets_share_schedule_prefix": True,
                            "budgets_share_bundle": True,
                            "by_shot_budget": by_budget,
                        }
                    )

    profiles: dict[str, Any] = {}
    block_rows: list[dict[str, Any]] = []
    transition_rows: list[dict[str, Any]] = []
    for profile_name, profile in PROFILES.items():
        profile_trials = [row for row in trial_rows if row["profile"] == profile_name]
        by_budget: dict[str, Any] = {}
        for shots in shot_budgets:
            pooled_rows = aggregate_task_rows(profile_trials, tasks, shots)
            per_block = []
            for block_index, block_seed in enumerate(block_seeds):
                selected = [
                    row for row in profile_trials if row["block_index"] == block_index
                ]
                task_rows = aggregate_task_rows(selected, tasks, shots)
                block_row = {
                    "block_index": block_index,
                    "block_seed": block_seed,
                    "profile": profile_name,
                    "shot_budget": shots,
                    "minimum_honest_completeness": min(
                        row["pass_rate"] for row in task_rows
                    ),
                    "minimum_wilson_lower": min(
                        row["wilson_lower"] for row in task_rows
                    ),
                    "task_rows": task_rows,
                }
                block_rows.append(block_row)
                per_block.append(block_row)

            leave_one_out = []
            for omitted_index, omitted_seed in enumerate(block_seeds):
                selected = [
                    row
                    for row in profile_trials
                    if row["block_index"] != omitted_index
                ]
                task_rows = aggregate_task_rows(selected, tasks, shots)
                leave_one_out.append(
                    {
                        "omitted_block_index": omitted_index,
                        "omitted_block_seed": omitted_seed,
                        "minimum_honest_completeness": min(
                            row["pass_rate"] for row in task_rows
                        ),
                        "minimum_wilson_lower": min(
                            row["wilson_lower"] for row in task_rows
                        ),
                        "task_rows": task_rows,
                    }
                )
            by_budget[str(shots)] = {
                "minimum_pooled_honest_completeness": min(
                    row["pass_rate"] for row in pooled_rows
                ),
                "minimum_pooled_wilson_lower": min(
                    row["wilson_lower"] for row in pooled_rows
                ),
                "minimum_leave_one_block_out_wilson_lower": min(
                    row["minimum_wilson_lower"] for row in leave_one_out
                ),
                "minimum_block_honest_completeness": min(
                    row["minimum_honest_completeness"] for row in per_block
                ),
                "blocks_meeting_point_floor": sum(
                    row["minimum_honest_completeness"] >= honest_floor
                    for row in per_block
                ),
                "pooled_task_rows": pooled_rows,
                "block_rows": per_block,
                "leave_one_block_out_rows": leave_one_out,
            }

        profile_transition_rows = []
        for block_index, block_seed in enumerate(block_seeds):
            for task in tasks:
                selected = [
                    row
                    for row in profile_trials
                    if row["block_index"] == block_index
                    and row["task_id"] == task["task_id"]
                ]
                lower_flags = [
                    row["by_shot_budget"][str(control_shots)]["passed"]
                    for row in selected
                ]
                upper_flags = [
                    row["by_shot_budget"][str(candidate_shots)]["passed"]
                    for row in selected
                ]
                transition = {
                    "block_index": block_index,
                    "block_seed": block_seed,
                    "profile": profile_name,
                    "task_id": task["task_id"],
                    "lower_budget": control_shots,
                    "upper_budget": candidate_shots,
                    "fail_to_pass": sum(
                        (not before) and after
                        for before, after in zip(lower_flags, upper_flags, strict=True)
                    ),
                    "pass_to_fail": sum(
                        before and (not after)
                        for before, after in zip(lower_flags, upper_flags, strict=True)
                    ),
                }
                transition_rows.append(transition)
                profile_transition_rows.append(transition)

        candidate = by_budget[str(candidate_shots)]
        pass_to_fail = sum(row["pass_to_fail"] for row in profile_transition_rows)
        conditions = [
            condition_row(
                "A1",
                "minimum pooled task pass rate reaches the floor",
                candidate["minimum_pooled_honest_completeness"],
                honest_floor,
                candidate["minimum_pooled_honest_completeness"] >= honest_floor,
            ),
            condition_row(
                "A2",
                "minimum pooled Wilson lower reaches the floor",
                candidate["minimum_pooled_wilson_lower"],
                honest_floor,
                candidate["minimum_pooled_wilson_lower"] >= honest_floor,
            ),
            condition_row(
                "A3",
                "minimum leave-one-block-out Wilson lower reaches the floor",
                candidate["minimum_leave_one_block_out_wilson_lower"],
                honest_floor,
                candidate["minimum_leave_one_block_out_wilson_lower"]
                >= honest_floor,
            ),
            condition_row(
                "A4",
                "every block reaches the point floor",
                candidate["blocks_meeting_point_floor"],
                len(block_seeds),
                candidate["blocks_meeting_point_floor"] == len(block_seeds),
            ),
            condition_row(
                "A5",
                "paired pass-to-fail transitions stay within the ceiling",
                pass_to_fail,
                maximum_regressions,
                pass_to_fail <= maximum_regressions,
            ),
        ]
        profiles[profile_name] = {
            "noise": profile,
            "by_shot_budget": by_budget,
            "pass_to_fail_transition_count": pass_to_fail,
            "fail_to_pass_transition_count": sum(
                row["fail_to_pass"] for row in profile_transition_rows
            ),
            "acceptance_conditions": conditions,
            "profile_accepted": all(row["passed"] for row in conditions),
        }

    global_acceptance = all(row["profile_accepted"] for row in profiles.values())
    summary = {
        "task_count": len(tasks),
        "profile_count": len(PROFILES),
        "seed_block_count": len(block_seeds),
        "block_seeds": block_seeds,
        "trials_per_block_profile_task": trials_per_block,
        "trials_per_profile_task": len(block_seeds) * trials_per_block,
        "shot_budgets": shot_budgets,
        "control_shot_budget": control_shots,
        "candidate_shot_budget": candidate_shots,
        "tolerance": tolerance,
        "honest_floor": honest_floor,
        "profiles": profiles,
        "global_acceptance": global_acceptance,
        "accepted_profile_count": sum(
            row["profile_accepted"] for row in profiles.values()
        ),
        "fail_to_pass_transition_count": sum(
            row["fail_to_pass"] for row in transition_rows
        ),
        "pass_to_fail_transition_count": sum(
            row["pass_to_fail"] for row in transition_rows
        ),
        "preregistered_before_execution": preregistered_at < started_at,
        "seed_substitution_performed": False,
        "optional_stopping_performed": False,
        "post_hoc_threshold_revision_performed": False,
        "hardware_execution_performed": False,
        "calibrated_backend_evidence": False,
        "protocol_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    expected_trials = len(block_seeds) * len(PROFILES) * len(tasks) * trials_per_block
    circuit_files = sorted(set(circuit_files))
    requirements = [
        {
            "requirement_id": "P1",
            "label": "contract file matches the publicly posted SHA-256",
            "passed": observed_contract_hash == CONTRACT_SHA256,
            "evidence": {"contract_sha256": observed_contract_hash},
        },
        {
            "requirement_id": "P2",
            "label": "public preregistration predates holdout execution",
            "passed": preregistered_at < started_at,
            "evidence": {
                "discussion": PREREGISTRATION_DISCUSSION,
                "created_at": PREREGISTRATION_CREATED_AT,
                "execution_started_at_unix": started_at,
            },
        },
        {
            "requirement_id": "P3",
            "label": "contract binds the accepted R123 result payload",
            "passed": r123["payload_hash"] == contract["source_payload_hash"],
            "evidence": {"r123_payload_hash": r123["payload_hash"]},
        },
        {
            "requirement_id": "P4",
            "label": "holdout root seeds are disjoint from R123",
            "passed": set(block_seeds).isdisjoint(r123["summary"]["block_seeds"]),
            "evidence": {
                "r123_seeds": r123["summary"]["block_seeds"],
                "r124_seeds": block_seeds,
            },
        },
        {
            "requirement_id": "P5",
            "label": "all trial rows preserve paired prefixes and bundles",
            "passed": all(
                row["budgets_share_schedule_prefix"]
                and row["budgets_share_bundle"]
                for row in trial_rows
            ),
            "evidence": {"trial_row_count": len(trial_rows)},
        },
        {
            "requirement_id": "P6",
            "label": "the preregistered block/profile/task trial count is complete",
            "passed": len(trial_rows) == expected_trials,
            "evidence": {
                "trial_row_count": len(trial_rows),
                "expected_trial_row_count": expected_trials,
            },
        },
        {
            "requirement_id": "P7",
            "label": "all schedules are bound to unique hashes",
            "passed": len({row["schedule_sha256"] for row in trial_rows})
            == len(trial_rows),
            "evidence": {
                "unique_schedule_hash_count": len(
                    {row["schedule_sha256"] for row in trial_rows}
                )
            },
        },
        {
            "requirement_id": "P8",
            "label": "block, pooled, leave-one-out, and transition ledgers are complete",
            "passed": len(block_rows)
            == len(block_seeds) * len(PROFILES) * len(shot_budgets)
            and len(transition_rows) == len(block_seeds) * len(PROFILES) * len(tasks),
            "evidence": {
                "block_row_count": len(block_rows),
                "transition_row_count": len(transition_rows),
            },
        },
        {
            "requirement_id": "P9",
            "label": "all five preregistered conditions are evaluated per profile",
            "passed": all(
                len(row["acceptance_conditions"]) == 5 for row in profiles.values()
            ),
            "evidence": {"profile_count": len(profiles)},
        },
        {
            "requirement_id": "P10",
            "label": "no seed substitution, optional stopping, or threshold revision occurred",
            "passed": not summary["seed_substitution_performed"]
            and not summary["optional_stopping_performed"]
            and not summary["post_hoc_threshold_revision_performed"],
            "evidence": {"contract_locked": True},
        },
        {
            "requirement_id": "P11",
            "label": "all fixed profile circuits are materialized",
            "passed": len(circuit_files) == len(PROFILES) * len(tasks),
            "evidence": {"circuit_file_count": len(circuit_files)},
        },
        {
            "requirement_id": "P12",
            "label": "synthetic holdout verdict grants no hardware, advantage, or BQP credit",
            "passed": not summary["hardware_execution_performed"]
            and not summary["calibrated_backend_evidence"]
            and not summary["protocol_soundness_claimed"]
            and not summary["quantum_advantage_claimed"]
            and not summary["bqp_separation_claimed"]
            and summary["new_credit_delta"] == 0,
            "evidence": {"new_credit_delta": 0},
        },
    ]
    failed = [row["requirement_id"] for row in requirements if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R124 preregistered holdout block replay",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "execution_started_at_unix": started_at,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "contract": {
            "path": CONTRACT_PATH,
            "sha256": observed_contract_hash,
            "discussion": PREREGISTRATION_DISCUSSION,
            "discussion_created_at": PREREGISTRATION_CREATED_AT,
        },
        "requirements": requirements,
        "requirement_count": len(requirements),
        "requirements_passed": len(requirements) - len(failed),
        "requirements_failed": len(failed),
        "summary": summary,
        "trial_rows": trial_rows,
        "block_rows": block_rows,
        "transition_rows": transition_rows,
        "artifacts": {
            "circuits": circuit_files,
            "contract": CONTRACT_PATH,
            "r123_result": R123_RESULT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": (
                "One publicly preregistered ideal/light Aer holdout verdict for "
                "the fixed tasks and 8192-shot candidate."
            ),
            "what_is_not_supported": contract["claim_boundary"]["not_supported"],
            "next_gate": (
                contract["decision_policy"]["accepted"]
                if global_acceptance
                else contract["decision_policy"]["rejected"]
            ),
        },
    }
    payload["payload_hash"] = stable_hash(payload)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    print(json.dumps(run_gate(Path(args.repo_root)), sort_keys=True))


if __name__ == "__main__":
    main()
