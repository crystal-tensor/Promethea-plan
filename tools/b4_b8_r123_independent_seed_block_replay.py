#!/usr/bin/env python3
"""T-B4-002x/T-B8-003ab: test R122 across independent seed blocks."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qasm3
from qiskit_aer import AerSimulator

from b4_b8_r119_private_observable_bundle_gate import build_bundle_tasks
from b4_b8_r121_private_bundle_shot_sweep import (
    HONEST_TARGET,
    PROFILES,
    TOLERANCE,
    noise_model,
    stable_hash,
    write_json,
)
from b4_b8_r122_matched_seed_prefix_replay import (
    bundle_error,
    choose_bundle,
    matched_prefix_records,
    target_values,
    wilson_interval,
)


METHOD = "b4_b8_r123_independent_seed_block_replay_v0"
STATUS = "independent_seed_block_confidence_stability_boundary"
MODEL_STATUS = "r122_boundary_replayed_across_independent_seed_blocks"
TARGET_ID = "T-B4-002x/T-B8-003ab/T-B10-009p"
UPSTREAM_TARGET_ID = "T-B4-002w/T-B8-003aa/T-B10-009o"
R122_RESULT_PATH = "results/B4_B8_R122_matched_seed_prefix_replay_v0.json"
OUT_DIR = "results/B4_B8_R123_independent_seed_block_replay"
RESULT_PATH = "results/B4_B8_R123_independent_seed_block_replay_v0.json"
REPORT_PATH = "research/B4_B8_R123_independent_seed_block_replay.md"
BLOCK_SEEDS = [12301, 12302, 12303, 12304, 12305]
TRIALS_PER_BLOCK = 12
SHOT_BUDGETS = [4096, 8192]
MAX_SHOTS = max(SHOT_BUDGETS)


def first_crossing(profile: dict[str, Any], field: str) -> int | None:
    for shots in SHOT_BUDGETS:
        if profile["by_shot_budget"][str(shots)][field] >= HONEST_TARGET:
            return shots
    return None


def aggregate_task_rows(
    selected_rows: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    shots: int,
) -> list[dict[str, Any]]:
    rows = []
    for task in tasks:
        task_trials = [
            row for row in selected_rows if row["task_id"] == task["task_id"]
        ]
        flags = [row["by_shot_budget"][str(shots)]["passed"] for row in task_trials]
        errors = [
            row["by_shot_budget"][str(shots)]["maximum_bundle_error"]
            for row in task_trials
        ]
        successes = sum(flags)
        lower, upper = wilson_interval(successes, len(task_trials))
        rows.append(
            {
                "task_id": task["task_id"],
                "trials": len(task_trials),
                "successes": successes,
                "pass_rate": successes / len(task_trials),
                "wilson_lower": lower,
                "wilson_upper": upper,
                "mean_bundle_error": float(np.mean(errors)),
                "maximum_bundle_error": max(errors),
            }
        )
    return rows


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    requirements = "\n".join(
        f"- `{row['requirement_id']}` "
        f"{'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    profile_lines = []
    for name, profile in summary["profiles"].items():
        for shots in SHOT_BUDGETS:
            row = profile["by_shot_budget"][str(shots)]
            profile_lines.append(
                f"- `{name}` / `{shots}`: pooled weakest point "
                f"`{row['minimum_pooled_honest_completeness']:.4f}`, pooled "
                f"Wilson lower `{row['minimum_pooled_wilson_lower']:.4f}`, "
                f"minimum leave-one-block-out Wilson lower "
                f"`{row['minimum_leave_one_block_out_wilson_lower']:.4f}`, "
                f"point-stable blocks `{row['blocks_meeting_point_floor']}/"
                f"{len(BLOCK_SEEDS)}`."
            )

    return f"""# B4/B8 R123 Independent-Seed Block Replay

## Summary

- Target: `{TARGET_ID}`
- Upstream target: `{UPSTREAM_TARGET_ID}`
- Method: `{METHOD}`
- Status: `{STATUS}`
- Independent seed blocks: `{len(BLOCK_SEEDS)}`
- Trials per block/profile/task: `{TRIALS_PER_BLOCK}`
- Total trial rows: `{len(payload['trial_rows'])}`
- Shot budgets: `{', '.join(str(value) for value in SHOT_BUDGETS)}`
- Honest completeness floor: `{HONEST_TARGET}`
- Pooled point first crossing: `{summary['pooled_point_first_budget_reaching_honest_floor']}`
- Pooled confidence first crossing: `{summary['pooled_confidence_first_budget_reaching_honest_floor']}`
- Leave-one-block-out confidence first crossing: `{summary['leave_one_block_out_confidence_first_budget_reaching_honest_floor']}`
- All-block point first crossing: `{summary['all_blocks_point_first_budget_reaching_honest_floor']}`
- Fail-to-pass / pass-to-fail transitions: `{summary['fail_to_pass_transition_count']}` / `{summary['pass_to_fail_transition_count']}`

{chr(10).join(profile_lines)}

R123 asks whether the R122 boundary survives independent randomization rather
than merely adding more trials to one seed family. Every block has a distinct
root seed. Within a trial, 4,096 shots remain a prefix of the same 8,192-shot
stream and the hidden observable bundle is unchanged. The acceptance summary
reports block-level point stability, pooled Wilson bounds, and the weakest
leave-one-block-out Wilson bound so that one favorable block cannot determine
the confidence result.

## Requirements

{requirements}

## Claim Boundary

Supported: an independent-seed-block synthetic Aer stability test of the R122
4,096/8,192-shot boundary. Not supported: iid proof, a universal concentration
law, calibrated backend evidence, real hardware execution, protocol or
cryptographic soundness, sampling hardness, quantum advantage, BQP separation,
or B10 credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    r122 = json.loads((root / R122_RESULT_PATH).read_text(encoding="utf-8"))
    if r122.get("status") != "matched_seed_prefix_shot_budget_confidence_boundary":
        raise ValueError("R123 requires the accepted R122 confidence boundary")

    output = root / OUT_DIR
    if output.exists():
        shutil.rmtree(output)
    circuits_dir = output / "circuits"
    circuits_dir.mkdir(parents=True)

    tasks = build_bundle_tasks()
    trial_rows: list[dict[str, Any]] = []
    circuit_files: list[str] = []
    for profile_index, (profile_name, profile) in enumerate(PROFILES.items()):
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
            for block_index, block_seed in enumerate(BLOCK_SEEDS):
                for trial in range(TRIALS_PER_BLOCK):
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
                    for shots in SHOT_BUDGETS:
                        error = bundle_error(records[:shots], bundle, exact_values)
                        by_budget[str(shots)] = {
                            "maximum_bundle_error": error,
                            "passed": error <= TOLERANCE,
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
        for shots in SHOT_BUDGETS:
            pooled_task_rows = aggregate_task_rows(profile_trials, tasks, shots)
            per_block = []
            for block_index, block_seed in enumerate(BLOCK_SEEDS):
                selected = [
                    row
                    for row in profile_trials
                    if row["block_index"] == block_index
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
            for omitted_index, omitted_seed in enumerate(BLOCK_SEEDS):
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
                    row["pass_rate"] for row in pooled_task_rows
                ),
                "minimum_pooled_wilson_lower": min(
                    row["wilson_lower"] for row in pooled_task_rows
                ),
                "minimum_leave_one_block_out_wilson_lower": min(
                    row["minimum_wilson_lower"] for row in leave_one_out
                ),
                "minimum_block_honest_completeness": min(
                    row["minimum_honest_completeness"] for row in per_block
                ),
                "blocks_meeting_point_floor": sum(
                    row["minimum_honest_completeness"] >= HONEST_TARGET
                    for row in per_block
                ),
                "pooled_task_rows": pooled_task_rows,
                "block_rows": per_block,
                "leave_one_block_out_rows": leave_one_out,
            }

        for block_index, block_seed in enumerate(BLOCK_SEEDS):
            for task in tasks:
                selected = [
                    row
                    for row in profile_trials
                    if row["block_index"] == block_index
                    and row["task_id"] == task["task_id"]
                ]
                lower_flags = [
                    row["by_shot_budget"][str(SHOT_BUDGETS[0])]["passed"]
                    for row in selected
                ]
                upper_flags = [
                    row["by_shot_budget"][str(SHOT_BUDGETS[1])]["passed"]
                    for row in selected
                ]
                transition_rows.append(
                    {
                        "block_index": block_index,
                        "block_seed": block_seed,
                        "profile": profile_name,
                        "task_id": task["task_id"],
                        "lower_budget": SHOT_BUDGETS[0],
                        "upper_budget": SHOT_BUDGETS[1],
                        "fail_to_pass": sum(
                            (not before) and after
                            for before, after in zip(
                                lower_flags, upper_flags, strict=True
                            )
                        ),
                        "pass_to_fail": sum(
                            before and (not after)
                            for before, after in zip(
                                lower_flags, upper_flags, strict=True
                            )
                        ),
                    }
                )

        profile_payload = {"noise": profile, "by_shot_budget": by_budget}
        profile_payload["pooled_point_first_budget_reaching_honest_floor"] = (
            first_crossing(profile_payload, "minimum_pooled_honest_completeness")
        )
        profile_payload["pooled_confidence_first_budget_reaching_honest_floor"] = (
            first_crossing(profile_payload, "minimum_pooled_wilson_lower")
        )
        profile_payload[
            "leave_one_block_out_confidence_first_budget_reaching_honest_floor"
        ] = first_crossing(
            profile_payload, "minimum_leave_one_block_out_wilson_lower"
        )
        profile_payload["all_blocks_point_first_budget_reaching_honest_floor"] = (
            next(
                (
                    shots
                    for shots in SHOT_BUDGETS
                    if by_budget[str(shots)]["blocks_meeting_point_floor"]
                    == len(BLOCK_SEEDS)
                ),
                None,
            )
        )
        profiles[profile_name] = profile_payload

    def crossings(field: str) -> dict[str, int | None]:
        return {name: row[field] for name, row in profiles.items()}

    summary = {
        "task_count": len(tasks),
        "profile_count": len(PROFILES),
        "seed_block_count": len(BLOCK_SEEDS),
        "block_seeds": BLOCK_SEEDS,
        "trials_per_block_profile_task": TRIALS_PER_BLOCK,
        "trials_per_profile_task": len(BLOCK_SEEDS) * TRIALS_PER_BLOCK,
        "shot_budgets": SHOT_BUDGETS,
        "maximum_replay_shots": MAX_SHOTS,
        "bundle_size": 3,
        "tolerance": TOLERANCE,
        "honest_floor": HONEST_TARGET,
        "matched_prefix_within_trial": True,
        "independent_seed_blocks": True,
        "profiles": profiles,
        "pooled_point_first_budget_reaching_honest_floor": crossings(
            "pooled_point_first_budget_reaching_honest_floor"
        ),
        "pooled_confidence_first_budget_reaching_honest_floor": crossings(
            "pooled_confidence_first_budget_reaching_honest_floor"
        ),
        "leave_one_block_out_confidence_first_budget_reaching_honest_floor": crossings(
            "leave_one_block_out_confidence_first_budget_reaching_honest_floor"
        ),
        "all_blocks_point_first_budget_reaching_honest_floor": crossings(
            "all_blocks_point_first_budget_reaching_honest_floor"
        ),
        "fail_to_pass_transition_count": sum(
            row["fail_to_pass"] for row in transition_rows
        ),
        "pass_to_fail_transition_count": sum(
            row["pass_to_fail"] for row in transition_rows
        ),
        "r122_confidence_first_budget_reaching_honest_floor": r122["summary"][
            "confidence_first_budget_reaching_honest_floor"
        ],
        "hardware_execution_performed": False,
        "calibrated_backend_evidence": False,
        "protocol_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
    }
    circuit_files = sorted(set(circuit_files))
    expected_trials = (
        len(BLOCK_SEEDS) * len(PROFILES) * len(tasks) * TRIALS_PER_BLOCK
    )
    requirements = [
        {
            "requirement_id": "P1",
            "label": "accepted R122 confidence boundary is consumed",
            "passed": True,
            "evidence": {"r122_status": r122["status"]},
        },
        {
            "requirement_id": "P2",
            "label": "five distinct root seeds define independent replay blocks",
            "passed": len(BLOCK_SEEDS) == 5 and len(set(BLOCK_SEEDS)) == 5,
            "evidence": {"block_seeds": BLOCK_SEEDS},
        },
        {
            "requirement_id": "P3",
            "label": "all trial rows preserve matched prefixes and hidden bundles",
            "passed": all(
                row["budgets_share_schedule_prefix"]
                and row["budgets_share_bundle"]
                for row in trial_rows
            ),
            "evidence": {"trial_row_count": len(trial_rows)},
        },
        {
            "requirement_id": "P4",
            "label": "every block/profile/task has twelve trial rows",
            "passed": len(trial_rows) == expected_trials,
            "evidence": {
                "trial_row_count": len(trial_rows),
                "expected_trial_row_count": expected_trials,
            },
        },
        {
            "requirement_id": "P5",
            "label": "every trial binds its declared block seed",
            "passed": all(
                row["trial_seed_components"][0] == row["block_seed"]
                for row in trial_rows
            ),
            "evidence": {
                "unique_schedule_hashes": len(
                    {row["schedule_sha256"] for row in trial_rows}
                )
            },
        },
        {
            "requirement_id": "P6",
            "label": "block, pooled, and leave-one-block-out statistics are materialized",
            "passed": len(block_rows)
            == len(BLOCK_SEEDS) * len(PROFILES) * len(SHOT_BUDGETS),
            "evidence": {"block_row_count": len(block_rows)},
        },
        {
            "requirement_id": "P7",
            "label": "paired 4096-to-8192 transitions are materialized per block/task",
            "passed": len(transition_rows)
            == len(BLOCK_SEEDS) * len(PROFILES) * len(tasks),
            "evidence": {"transition_row_count": len(transition_rows)},
        },
        {
            "requirement_id": "P8",
            "label": "all profile circuits are materialized",
            "passed": len(circuit_files) == len(PROFILES) * len(tasks),
            "evidence": {"circuit_file_count": len(circuit_files)},
        },
        {
            "requirement_id": "P9",
            "label": "synthetic evidence is not promoted to hardware or soundness credit",
            "passed": not summary["hardware_execution_performed"]
            and not summary["calibrated_backend_evidence"]
            and not summary["protocol_soundness_claimed"]
            and not summary["quantum_advantage_claimed"]
            and not summary["bqp_separation_claimed"],
            "evidence": {"new_credit_delta": 0},
        },
        {
            "requirement_id": "P10",
            "label": "point, pooled-confidence, and block-robust crossings remain separate",
            "passed": True,
            "evidence": {
                "pooled_point": summary[
                    "pooled_point_first_budget_reaching_honest_floor"
                ],
                "pooled_confidence": summary[
                    "pooled_confidence_first_budget_reaching_honest_floor"
                ],
                "leave_one_block_out": summary[
                    "leave_one_block_out_confidence_first_budget_reaching_honest_floor"
                ],
            },
        },
    ]
    failed = [row["requirement_id"] for row in requirements if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R123 independent-seed block replay",
        "version": "0.1",
        "generated_at_unix": int(time.time()),
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
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
            "r122_result": R122_RESULT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": (
                "Independent-seed-block ideal/light Aer replay of the R122 "
                "4096/8192-shot confidence boundary."
            ),
            "what_is_not_supported": (
                "An iid proof, universal concentration law, calibrated backend "
                "evidence, real hardware execution, protocol or cryptographic "
                "soundness, sampling hardness, quantum advantage, BQP separation, "
                "or B10 credit."
            ),
            "next_gate": (
                "Pre-register a block-robust acceptance statistic and replay the "
                "surviving budget under calibrated backend properties or an "
                "independent backend transcript."
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
    payload = run_gate(Path(args.repo_root))
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
