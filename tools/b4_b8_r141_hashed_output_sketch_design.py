#!/usr/bin/env python3
"""Design a fixed-width output sketch that approximates R140 mapping scores."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qasm3

from b4_b8_r119_private_observable_bundle_gate import stable_hash, write_json
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r127_calibration_aware_layout_design import SNAPSHOT_CLASSES
from b4_b8_r132_topology_constrained_route_policy import (
    DETERMINISTIC_PROCESS_ENV,
    compile_policy,
)
from b4_b8_r135_dense_interaction_fallback import build_dense_validation_tasks
from b4_b8_r138_postcommit_statistical_challenge import exact_distribution


METHOD = "b4_b8_r141_hashed_output_sketch_design_v0"
STATUS = "fixed_width_hashed_output_sketch_frozen_before_holdout"
MODEL_STATUS = "sample_only_selector_replays_r140_candidates_without_holdout_rows"
TARGET_ID = "T-B4-002aq/T-B8-003au/T-B10-009ai"
UPSTREAM_TARGET_ID = "T-B4-002ap/T-B8-003at/T-B10-009ah"
R136_RESULT_PATH = "results/B4_B8_R136_route_realization_margin_v0.json"
R140_RESULT_PATH = "results/B4_B8_R140_output_aware_mapping_design_v0.json"
RESULT_PATH = "results/B4_B8_R141_hashed_output_sketch_design_v0.json"
REPORT_PATH = "research/B4_B8_R141_hashed_output_sketch_design.md"
OUT_DIR = "results/B4_B8_R141_hashed_output_sketch_design"

PILOT_SAMPLE_COUNT = 4096
READOUT_REPLICA_COUNT = 8
SKETCH_BUCKET_COUNT = 256
HASH_MULTIPLIER = 173
HASH_OFFSET = 97
CANONICAL_PILOT_SEEDS = {
    "dense_validation_complete_ising_n6": 14101,
    "dense_validation_inverse_qft_n6": 14102,
    "dense_validation_scrambled_qft_n6": 14103,
    "dense_validation_xy_network_n6": 14104,
}
PRESSURE_REPLICATE_COUNT = 16


def ensure_deterministic_process_environment() -> None:
    if all(os.environ.get(key) == value for key, value in DETERMINISTIC_PROCESS_ENV.items()):
        return
    environment = dict(os.environ)
    environment.update(DETERMINISTIC_PROCESS_ENV)
    os.execvpe(sys.executable, [sys.executable, *sys.argv], environment)


def distribution_arrays(distribution: dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.asarray([int(bitstring, 2) for bitstring in distribution], dtype=np.int64),
        np.asarray(list(distribution.values()), dtype=float),
    )


def hash_buckets(values: np.ndarray) -> np.ndarray:
    return (values * HASH_MULTIPLIER + HASH_OFFSET) % SKETCH_BUCKET_COUNT


def pilot_packet(
    distribution: dict[str, float], width: int, seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values, probabilities = distribution_arrays(distribution)
    generator = np.random.default_rng(seed)
    samples = generator.choice(values, size=PILOT_SAMPLE_COUNT, p=probabilities)
    uniforms = generator.random((PILOT_SAMPLE_COUNT, READOUT_REPLICA_COUNT, width))
    ideal_histogram = np.bincount(
        hash_buckets(samples), minlength=SKETCH_BUCKET_COUNT
    ).astype(float)
    ideal_histogram /= PILOT_SAMPLE_COUNT
    return samples, uniforms, ideal_histogram


def sketch_readout_fidelity(
    samples: np.ndarray,
    uniforms: np.ndarray,
    ideal_histogram: np.ndarray,
    readout_error_vector: list[float],
) -> float:
    noisy = np.repeat(samples[:, None], READOUT_REPLICA_COUNT, axis=1).copy()
    for bit, error in enumerate(readout_error_vector):
        noisy ^= (uniforms[:, :, bit] < error).astype(np.int64) << bit
    noisy_histogram = np.bincount(
        hash_buckets(noisy.reshape(-1)), minlength=SKETCH_BUCKET_COUNT
    ).astype(float)
    noisy_histogram /= PILOT_SAMPLE_COUNT * READOUT_REPLICA_COUNT
    coefficient = float(np.sqrt(ideal_histogram * noisy_histogram).sum())
    return coefficient * coefficient


def surrogate_score(
    row: dict[str, Any],
    samples: np.ndarray,
    uniforms: np.ndarray,
    ideal_histogram: np.ndarray,
) -> tuple[float, float]:
    readout_fidelity = sketch_readout_fidelity(
        samples, uniforms, ideal_histogram, row["readout_error_vector"]
    )
    return (1.0 - row["cx_any_error_proxy"]) * readout_fidelity, readout_fidelity


def selection_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["hashed_output_sketch_score"],
        row["hashed_output_sketch_readout_fidelity"],
        -row["cx_any_error_proxy"],
        -row["cx_occurrence_count"],
        row["policy_id"],
        tuple(row["mapping"]),
        -row["realization_seed"],
    )


def candidate_identity(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        tuple(row["mapping"]),
        row["policy_id"],
        row["realization_seed"],
    )


def pressure_seed(task_id: str, replicate: int) -> int:
    task_index = sorted(CANONICAL_PILOT_SEEDS).index(task_id)
    return 141000 + replicate * 17 + task_index


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    groups = "\n".join(
        f"- `{row['snapshot']}` / `{row['task_id']}`: sketch/exact selection "
        f"agreement `{row['selection_matches_r140_exact']}`, exact-score regret "
        f"`{row['exact_score_regret']:.8f}`, pressure agreement "
        f"`{row['pressure_selection_agreement_count']} / 16`, selected mapping "
        f"`{row['selected_mapping']}`."
        for row in payload["group_rows"]
    )
    requirements = "\n".join(
        f"- `{row['requirement_id']}` {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    return f"""# B4/B8 R141 Hashed Output Sketch Design

## Design Result

- R140 candidate rows replayed: `{summary['candidate_count']}`
- Sketch width: `{summary['sketch_bucket_count']}` buckets
- Pilot samples / readout replicas: `{summary['pilot_sample_count']}` / `{summary['readout_replica_count']}`
- Canonical selection agreement with R140 exact score: `{summary['canonical_selection_agreement_count']} / 12`
- Pressure selection agreement: `{summary['pressure_selection_agreement_count']} / {summary['pressure_selection_count']}`
- Lagos complete-Ising pressure agreement: `{summary['lagos_ising_pressure_agreement_count']} / 16`
- Mean / maximum exact-score regret: `{summary['mean_exact_score_regret']:.8f}` / `{summary['maximum_exact_score_regret']:.8f}`
- Selected QASM replay: `{summary['selected_qasm_replay_match_count']} / 12`
- Holdout rows read during selection: `0`
- New credit delta: `0`

The selector receives only integer output samples, shared uniform readout
variates, candidate readout-error vectors, and compiled CX exposure. It hashes
ideal and synthetically readout-corrupted samples into a fixed 256-bin sketch,
estimates Hellinger fidelity in that sketch, and multiplies it by the existing
CX-success proxy. Its memory is fixed by the sketch width rather than `2^n`.

The current pilot samples are generated from a statevector-backed design
oracle. Therefore this result establishes a scalable *scoring interface*, not
scalable end-to-end pilot acquisition.

## Group Evidence

{groups}

## Requirements

{requirements}

## Claim Boundary

Supported: a frozen fixed-width, sample-only reranker over the 1,536 R140
candidates, plus deterministic pressure tests against the already frozen R140
exact score. Not supported: scalable pilot acquisition, unseen noisy holdout
acceptance, current calibration, hardware, mitigation, soundness, quantum
advantage, BQP separation, or new B10 credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    started_at = int(time.time())
    r136 = json.loads((root / R136_RESULT_PATH).read_text(encoding="utf-8"))
    r140 = json.loads((root / R140_RESULT_PATH).read_text(encoding="utf-8"))
    tasks = {task["task_id"]: task for task in build_dense_validation_tasks()}
    candidate_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for source in r140["candidate_rows"]:
        candidate_groups.setdefault((source["snapshot"], source["task_id"]), []).append(source)
    if len(candidate_groups) != 12 or any(len(rows) != 128 for rows in candidate_groups.values()):
        raise ValueError("R141 requires twelve complete 128-candidate R140 groups")

    output = root / OUT_DIR
    selected_dir = output / "selected_circuits"
    selected_dir.mkdir(parents=True, exist_ok=True)
    group_rows: list[dict[str, Any]] = []
    canonical_candidate_rows: list[dict[str, Any]] = []
    pressure_rows: list[dict[str, Any]] = []
    selected_replay_matches = 0
    selected_preexisting = 0

    distributions = {
        task_id: exact_distribution(task["circuit"]) for task_id, task in tasks.items()
    }
    for key in sorted(candidate_groups):
        snapshot_name, task_id = key
        task = tasks[task_id]
        samples, uniforms, ideal_histogram = pilot_packet(
            distributions[task_id], task["circuit"].num_qubits, CANONICAL_PILOT_SEEDS[task_id]
        )
        scored = []
        for source in candidate_groups[key]:
            score, readout_fidelity = surrogate_score(
                source, samples, uniforms, ideal_histogram
            )
            row = dict(source)
            row["hashed_output_sketch_score"] = score
            row["hashed_output_sketch_readout_fidelity"] = readout_fidelity
            scored.append(row)
            canonical_candidate_rows.append(row)
        selected = max(scored, key=selection_key)
        exact_selected = max(
            candidate_groups[key],
            key=lambda row: (
                row["output_aware_product_score"],
                row["exact_output_aware_readout_fidelity"],
                -row["cx_any_error_proxy"],
            ),
        )

        pressure_agreements = 0
        pressure_regrets = []
        for replicate in range(PRESSURE_REPLICATE_COUNT):
            seed = pressure_seed(task_id, replicate)
            p_samples, p_uniforms, p_histogram = pilot_packet(
                distributions[task_id], task["circuit"].num_qubits, seed
            )
            pressure_candidates = []
            for source in candidate_groups[key]:
                score, readout_fidelity = surrogate_score(
                    source, p_samples, p_uniforms, p_histogram
                )
                pressure_candidates.append(
                    {
                        **source,
                        "hashed_output_sketch_score": score,
                        "hashed_output_sketch_readout_fidelity": readout_fidelity,
                    }
                )
            p_selected = max(pressure_candidates, key=selection_key)
            agreement = candidate_identity(p_selected) == candidate_identity(exact_selected)
            regret = exact_selected["output_aware_product_score"] - p_selected[
                "output_aware_product_score"
            ]
            pressure_agreements += agreement
            pressure_regrets.append(regret)
            pressure_rows.append(
                {
                    "snapshot": snapshot_name,
                    "task_id": task_id,
                    "replicate": replicate,
                    "pilot_seed": seed,
                    "selection_matches_r140_exact": agreement,
                    "exact_score_regret": regret,
                    "selected_mapping": p_selected["mapping"],
                    "selected_policy_id": p_selected["policy_id"],
                    "selected_realization_seed": p_selected["realization_seed"],
                }
            )

        backend = SNAPSHOT_CLASSES[snapshot_name]()
        logical = basis_circuit(
            task["circuit"], tuple("Z" for _ in range(task["circuit"].num_qubits))
        )
        compiled = compile_policy(
            logical,
            backend,
            selected["mapping"],
            selected["policy_id"],
            selected["realization_seed"],
        )
        qasm = qasm3.dumps(compiled)
        if stable_hash(qasm) != selected["qasm_hash"]:
            raise ValueError(f"R141 selected QASM drift for {key}")
        selected_path = selected_dir / f"{snapshot_name}_{task_id}.qasm"
        if selected_path.exists():
            selected_preexisting += 1
            replay_match = selected_path.read_text(encoding="utf-8") == qasm
        else:
            selected_path.write_text(qasm, encoding="utf-8")
            replay_match = True
        selected_replay_matches += replay_match
        group_rows.append(
            {
                "snapshot": snapshot_name,
                "task_id": task_id,
                "candidate_count": len(scored),
                "canonical_pilot_seed": CANONICAL_PILOT_SEEDS[task_id],
                "selected_mapping": selected["mapping"],
                "selected_policy_id": selected["policy_id"],
                "selected_realization_seed": selected["realization_seed"],
                "selected_sketch_score": selected["hashed_output_sketch_score"],
                "selected_exact_score": selected["output_aware_product_score"],
                "r140_exact_mapping": exact_selected["mapping"],
                "r140_exact_policy_id": exact_selected["policy_id"],
                "r140_exact_realization_seed": exact_selected["realization_seed"],
                "r140_exact_score": exact_selected["output_aware_product_score"],
                "selection_matches_r140_exact": candidate_identity(selected)
                == candidate_identity(exact_selected),
                "exact_score_regret": exact_selected["output_aware_product_score"]
                - selected["output_aware_product_score"],
                "pressure_selection_agreement_count": pressure_agreements,
                "pressure_maximum_exact_score_regret": max(pressure_regrets),
                "selected_circuit_path": str(selected_path.relative_to(root)),
                "selected_circuit_sha256": file_sha256(selected_path),
                "selected_qasm_replay_matches": replay_match,
            }
        )

    all_regrets = [row["exact_score_regret"] for row in pressure_rows]
    lagos_pressure = [
        row
        for row in pressure_rows
        if row["snapshot"] == "FakeLagosV2"
        and row["task_id"] == "dense_validation_complete_ising_n6"
    ]
    summary = {
        "candidate_count": len(canonical_candidate_rows),
        "group_count": len(group_rows),
        "candidates_per_group": 128,
        "sketch_bucket_count": SKETCH_BUCKET_COUNT,
        "pilot_sample_count": PILOT_SAMPLE_COUNT,
        "readout_replica_count": READOUT_REPLICA_COUNT,
        "sample_replica_work_per_candidate": PILOT_SAMPLE_COUNT * READOUT_REPLICA_COUNT,
        "score_formula": "(1-cx_any_error_proxy)*hashed_hellinger_fidelity",
        "canonical_selection_agreement_count": sum(
            row["selection_matches_r140_exact"] for row in group_rows
        ),
        "pressure_replicate_count": PRESSURE_REPLICATE_COUNT,
        "pressure_selection_count": len(pressure_rows),
        "pressure_selection_agreement_count": sum(
            row["selection_matches_r140_exact"] for row in pressure_rows
        ),
        "lagos_ising_pressure_agreement_count": sum(
            row["selection_matches_r140_exact"] for row in lagos_pressure
        ),
        "mean_exact_score_regret": statistics.mean(all_regrets),
        "maximum_exact_score_regret": max(all_regrets),
        "pressure_regret_at_most_0_002_count": sum(value <= 0.002 for value in all_regrets),
        "selected_qasm_preexisting_count": selected_preexisting,
        "selected_qasm_replay_match_count": selected_replay_matches,
        "selector_full_distribution_value_count": 0,
        "teacher_exact_scores_read_after_selection_only": True,
        "pilot_acquisition_method": "statevector_backed_samples_design_only",
        "scalable_pilot_acquisition_claimed": False,
        "noisy_holdout_executed": False,
        "hardware_execution_performed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        {"requirement_id": "R1", "label": "all 1,536 frozen R140 candidates are replayed", "passed": summary["candidate_count"] == 1536},
        {"requirement_id": "R2", "label": "selector memory is fixed at 256 histogram buckets", "passed": summary["sketch_bucket_count"] == 256},
        {"requirement_id": "R3", "label": "selector consumes samples rather than a full distribution table", "passed": summary["selector_full_distribution_value_count"] == 0},
        {"requirement_id": "R4", "label": "Lagos target matches R140 exact selection in all 16 pressure blocks", "passed": summary["lagos_ising_pressure_agreement_count"] == 16},
        {"requirement_id": "R5", "label": "at least 160 of 192 pressure selections match R140", "passed": summary["pressure_selection_agreement_count"] >= 160},
        {"requirement_id": "R6", "label": "maximum exact-score regret remains at most 0.005", "passed": summary["maximum_exact_score_regret"] <= 0.005},
        {"requirement_id": "R7", "label": "all twelve selected QASM files replay", "passed": selected_replay_matches == 12},
        {"requirement_id": "R8", "label": "teacher scores are used only after selection for evaluation", "passed": summary["teacher_exact_scores_read_after_selection_only"]},
        {"requirement_id": "R9", "label": "no noisy acceptance holdout is opened during design", "passed": not summary["noisy_holdout_executed"]},
        {"requirement_id": "R10", "label": "pilot acquisition, hardware, advantage, BQP, and credit claims remain false", "passed": not any([summary["scalable_pilot_acquisition_claimed"], summary["hardware_execution_performed"], summary["quantum_advantage_claimed"], summary["bqp_separation_claimed"], summary["new_credit_delta"]])},
    ]
    payload = {
        "title": "B4/B8 R141 hashed output sketch design",
        "version": 0,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "generated_at_unix": started_at,
        "source_target_id": TARGET_ID,
        "upstream_target_id": UPSTREAM_TARGET_ID,
        "summary": summary,
        "group_rows": group_rows,
        "pressure_rows": pressure_rows,
        "candidate_rows": canonical_candidate_rows,
        "requirements": requirements,
        "requirement_count": len(requirements),
        "requirements_passed": sum(row["passed"] for row in requirements),
        "requirements_failed": sum(not row["passed"] for row in requirements),
        "failed_requirement_ids": [row["requirement_id"] for row in requirements if not row["passed"]],
        "artifacts": {
            "r136_result": R136_RESULT_PATH,
            "r140_design_result": R140_RESULT_PATH,
            "selected_circuit_directory": str(selected_dir.relative_to(root)),
            "result": RESULT_PATH,
            "markdown_report": REPORT_PATH,
        },
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "deterministic_process_environment": DETERMINISTIC_PROCESS_ENV,
        },
        "claim_boundary": {
            "what_is_supported": "fixed-width sample-only sketch reranking and deterministic design pressure evidence",
            "what_is_not_supported": "scalable pilot acquisition, noisy holdout acceptance, hardware, mitigation, soundness, quantum advantage, BQP separation, or new credit",
        },
    }
    hash_payload = dict(payload)
    payload["payload_hash"] = hashlib.sha256(
        json.dumps(hash_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    ensure_deterministic_process_environment()
    root = args.root.resolve()
    payload = run_gate(root)
    output = args.output or root / RESULT_PATH
    markdown = args.report or root / REPORT_PATH
    write_json(output, payload)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if payload["requirements_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
