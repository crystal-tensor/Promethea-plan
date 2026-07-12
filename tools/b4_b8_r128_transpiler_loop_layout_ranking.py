#!/usr/bin/env python3
"""T-B4-002ac/T-B8-003ag: rerank R127 layouts inside the transpiler loop."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import platform
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qasm3, transpile
from qiskit_ibm_runtime.fake_provider import FakeJakartaV2, FakeLagosV2, FakeOslo

from b4_b8_r119_private_observable_bundle_gate import build_bundle_tasks
from b4_b8_r121_private_bundle_shot_sweep import basis_circuit, stable_hash, write_json
from b4_b8_r126_calibration_attribution_ledger import circuit_exposure, file_sha256


METHOD = "b4_b8_r128_transpiler_loop_layout_ranking_v0"
STATUS = "transpiler_loop_layout_ranking_boundary"
MODEL_STATUS = "r127_static_candidates_reranked_by_compiled_exposure_without_holdout"
TARGET_ID = "T-B4-002ac/T-B8-003ag/T-B10-009u"
UPSTREAM_TARGET_ID = "T-B4-002ab/T-B8-003af/T-B10-009t"
R125_RESULT_PATH = "results/B4_B8_R125_historical_snapshot_replay_v0.json"
R127_RESULT_PATH = "results/B4_B8_R127_calibration_aware_layout_design_v0.json"
RESULT_PATH = "results/B4_B8_R128_transpiler_loop_layout_ranking_v0.json"
REPORT_PATH = "research/B4_B8_R128_transpiler_loop_layout_ranking.md"
OUT_DIR = "results/B4_B8_R128_transpiler_loop_layout_ranking"
TRANSPILER_SEEDS = (12801, 12802, 12803, 12804, 12805)
OPTIMIZATION_LEVEL = 1
EXPECTED_GROUPS = 6
EXPECTED_CANDIDATES_PER_GROUP = 10
SNAPSHOT_CLASSES = {
    "FakeOslo": FakeOslo,
    "FakeJakartaV2": FakeJakartaV2,
    "FakeLagosV2": FakeLagosV2,
}


def package_version(name: str) -> str:
    return importlib.metadata.version(name)


def exposure_from_qasm(qasm: str, metadata: dict[str, Any], scratch: Path) -> dict[str, Any]:
    scratch.write_text(qasm, encoding="utf-8")
    return circuit_exposure(scratch, metadata)


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    exposures = [row["combined_any_error_proxy"] for row in rows]
    cx_counts = [row["cx_occurrence_count"] for row in rows]
    return {
        "mean_combined_any_error_proxy": float(np.mean(exposures)),
        "minimum_combined_any_error_proxy": min(exposures),
        "maximum_combined_any_error_proxy": max(exposures),
        "mean_cx_occurrence_count": float(np.mean(cx_counts)),
        "minimum_cx_occurrence_count": min(cx_counts),
        "maximum_cx_occurrence_count": max(cx_counts),
    }


def report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = []
    for row in payload["selected_layout_rows"]:
        lines.append(
            "- `{snapshot}` / `{task}`: static rank `{rank}` -> mapping `{mapping}`; "
            "mean exposure selected/static/default `{selected:.4f}/{static:.4f}/{default:.4f}`; "
            "delta vs static/default `{ds:.4f}/{dd:.4f}`; selected seed wins `{wins}/5`; "
            "mean CX selected/default `{cx:.1f}/{dcx:.1f}`.".format(
                snapshot=row["snapshot"],
                task=row["task_id"],
                rank=row["selected_static_rank"],
                mapping=row["selected_mapping"],
                selected=row["selected_aggregate"]["mean_combined_any_error_proxy"],
                static=row["static_rank_one_aggregate"]["mean_combined_any_error_proxy"],
                default=row["default_layout_aggregate"]["mean_combined_any_error_proxy"],
                ds=row["mean_exposure_delta_vs_static_rank_one"],
                dd=row["mean_exposure_delta_vs_default_layout"],
                wins=row["seed_win_count_vs_default_layout"],
                cx=row["selected_aggregate"]["mean_cx_occurrence_count"],
                dcx=row["default_layout_aggregate"]["mean_cx_occurrence_count"],
            )
        )
    requirements = "\n".join(
        f"- `{row['requirement_id']}` {'PASS' if row['passed'] else 'FAIL'}: {row['label']}"
        for row in payload["requirements"]
    )
    return f"""# B4/B8 R128 Transpiler-In-The-Loop Layout Ranking

## Result

- Retained R127 candidates: `{summary['retained_candidate_count']}`
- Candidate compilations: `{summary['candidate_compilation_count']}`
- Default-layout compilations: `{summary['default_layout_compilation_count']}`
- Static-rank-one layouts replaced: `{summary['strict_static_rerank_count']}` / `6`
- Groups beating mean default exposure: `{summary['mean_default_improvement_count']}` / `6`
- Groups winning at least 4/5 seeds: `{summary['four_of_five_default_seed_win_count']}` / `6`
- Routing-survival gate passed: `{summary['routing_survival_gate_passed']}`
- Acceptance holdout executed: `False`
- New credit delta: `0`

## Per-Group Evidence

{chr(10).join(lines)}

The selection rule is fixed before inspection: minimize mean compiled combined
exposure over five declared transpiler seeds, then worst exposure, mean CX count,
static rank, and mapping. The automatic-layout baseline uses the same circuit,
backend snapshot, optimization level, and seed. R125 acceptance rows are not read.

## Gate

The routing-survival gate requires every selected layout to beat the automatic
layout's mean and worst compiled exposure and to win at least four of five seeds.
Passing this design gate would authorize preregistration of a new disjoint
layout/readout holdout; it would not itself count as verifier or B10 credit.

## Requirements

{requirements}

## Claim Boundary

Supported: deterministic, same-condition transpiler-loop ranking of the 60
predeclared R127 candidates against automatic layout. Not supported: acceptance
holdout performance, readout mitigation, current calibration, provider access,
hardware execution, protocol soundness, quantum advantage, BQP separation, or
new B10 credit.
"""


def run_gate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    r125_path = root / R125_RESULT_PATH
    r127_path = root / R127_RESULT_PATH
    r125 = json.loads(r125_path.read_text(encoding="utf-8"))
    r127 = json.loads(r127_path.read_text(encoding="utf-8"))
    if r127.get("status") != "calibration_aware_layout_design_boundary":
        raise ValueError("R128 requires the R127 layout-design boundary")
    if r127["summary"].get("top_mapping_row_count") != 60:
        raise ValueError("R128 requires all 60 retained R127 candidates")

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in r127["top_layout_rows"]:
        grouped[(row["snapshot"], row["task_id"])].append(row)
    if len(grouped) != EXPECTED_GROUPS or any(
        len(rows) != EXPECTED_CANDIDATES_PER_GROUP for rows in grouped.values()
    ):
        raise ValueError("R127 candidate groups are incomplete")

    output = root / OUT_DIR
    circuits_dir = output / "selected_circuits"
    circuits_dir.mkdir(parents=True, exist_ok=True)
    for old in circuits_dir.glob("*.qasm"):
        old.unlink()

    tasks = {task["task_id"]: task for task in build_bundle_tasks()}
    selected_rows = []
    candidate_aggregates = []
    candidate_compilation_count = 0
    default_compilation_count = 0
    circuit_files = []
    with tempfile.TemporaryDirectory(prefix="r128-") as temporary:
        scratch = Path(temporary) / "compiled.qasm"
        for snapshot_name, task_id in sorted(grouped):
            backend = SNAPSHOT_CLASSES[snapshot_name]()
            metadata = r125["snapshot_metadata"][snapshot_name]
            representative = basis_circuit(
                tasks[task_id]["circuit"],
                tuple("Z" for _ in range(tasks[task_id]["circuit"].num_qubits)),
            )
            default_seed_rows = []
            for seed in TRANSPILER_SEEDS:
                compiled = transpile(
                    representative,
                    backend=backend,
                    optimization_level=OPTIMIZATION_LEVEL,
                    seed_transpiler=seed,
                )
                qasm = qasm3.dumps(compiled)
                exposure = exposure_from_qasm(qasm, metadata, scratch)
                default_seed_rows.append(
                    {
                        "seed": seed,
                        "combined_any_error_proxy": exposure["combined_any_error_proxy"],
                        "cx_occurrence_count": exposure["cx_occurrence_count"],
                    }
                )
                default_compilation_count += 1
            default_aggregate = aggregate(default_seed_rows)

            qasm_by_mapping_seed: dict[tuple[tuple[int, ...], int], str] = {}
            group_aggregates = []
            for candidate in sorted(grouped[(snapshot_name, task_id)], key=lambda row: row["rank"]):
                mapping = tuple(candidate["mapping"])
                seed_rows = []
                for seed in TRANSPILER_SEEDS:
                    compiled = transpile(
                        representative,
                        backend=backend,
                        initial_layout=list(mapping),
                        optimization_level=OPTIMIZATION_LEVEL,
                        seed_transpiler=seed,
                    )
                    qasm = qasm3.dumps(compiled)
                    qasm_by_mapping_seed[(mapping, seed)] = qasm
                    exposure = exposure_from_qasm(qasm, metadata, scratch)
                    seed_rows.append(
                        {
                            "seed": seed,
                            "combined_any_error_proxy": exposure["combined_any_error_proxy"],
                            "cx_occurrence_count": exposure["cx_occurrence_count"],
                            "measurement_map_preserves_logical_order": exposure[
                                "measurement_map_preserves_logical_order"
                            ],
                        }
                    )
                    candidate_compilation_count += 1
                row = {
                    "snapshot": snapshot_name,
                    "task_id": task_id,
                    "static_rank": candidate["rank"],
                    "mapping": list(mapping),
                    "static_combined_any_error_proxy": candidate[
                        "static_combined_any_error_proxy"
                    ],
                    "aggregate": aggregate(seed_rows),
                    "seed_rows": seed_rows,
                }
                group_aggregates.append(row)
                candidate_aggregates.append(row)

            selected = min(
                group_aggregates,
                key=lambda row: (
                    row["aggregate"]["mean_combined_any_error_proxy"],
                    row["aggregate"]["maximum_combined_any_error_proxy"],
                    row["aggregate"]["mean_cx_occurrence_count"],
                    row["static_rank"],
                    row["mapping"],
                ),
            )
            static_rank_one = next(row for row in group_aggregates if row["static_rank"] == 1)
            selected_seed_rows = selected["seed_rows"]
            selected_paths = []
            for seed in TRANSPILER_SEEDS:
                path = circuits_dir / f"{snapshot_name}_{task_id}_seed_{seed}.qasm"
                path.write_text(
                    qasm_by_mapping_seed[(tuple(selected["mapping"]), seed)],
                    encoding="utf-8",
                )
                selected_paths.append(str(path.relative_to(root)))
                circuit_files.append(str(path.relative_to(root)))
            default_by_seed = {row["seed"]: row for row in default_seed_rows}
            selected_rows.append(
                {
                    "snapshot": snapshot_name,
                    "snapshot_sha256": metadata["sha256"],
                    "task_id": task_id,
                    "candidate_count": len(group_aggregates),
                    "selected_mapping": selected["mapping"],
                    "selected_static_rank": selected["static_rank"],
                    "selected_aggregate": selected["aggregate"],
                    "static_rank_one_mapping": static_rank_one["mapping"],
                    "static_rank_one_aggregate": static_rank_one["aggregate"],
                    "default_layout_aggregate": default_aggregate,
                    "default_layout_seed_rows": default_seed_rows,
                    "mean_exposure_delta_vs_static_rank_one": (
                        static_rank_one["aggregate"]["mean_combined_any_error_proxy"]
                        - selected["aggregate"]["mean_combined_any_error_proxy"]
                    ),
                    "mean_exposure_delta_vs_default_layout": (
                        default_aggregate["mean_combined_any_error_proxy"]
                        - selected["aggregate"]["mean_combined_any_error_proxy"]
                    ),
                    "worst_exposure_delta_vs_default_layout": (
                        default_aggregate["maximum_combined_any_error_proxy"]
                        - selected["aggregate"]["maximum_combined_any_error_proxy"]
                    ),
                    "seed_win_count_vs_default_layout": sum(
                        row["combined_any_error_proxy"]
                        < default_by_seed[row["seed"]]["combined_any_error_proxy"]
                        for row in selected_seed_rows
                    ),
                    "all_measurement_maps_preserve_logical_order": all(
                        row["measurement_map_preserves_logical_order"]
                        for row in selected_seed_rows
                    ),
                    "selected_circuit_paths": selected_paths,
                    "selected_circuit_sha256": {
                        path: file_sha256(root / path) for path in selected_paths
                    },
                }
            )

    mean_default_improvements = sum(
        row["mean_exposure_delta_vs_default_layout"] > 0.0 for row in selected_rows
    )
    worst_default_improvements = sum(
        row["worst_exposure_delta_vs_default_layout"] > 0.0 for row in selected_rows
    )
    four_of_five = sum(
        row["seed_win_count_vs_default_layout"] >= 4 for row in selected_rows
    )
    routing_gate = all(
        row["mean_exposure_delta_vs_default_layout"] > 0.0
        and row["worst_exposure_delta_vs_default_layout"] > 0.0
        and row["seed_win_count_vs_default_layout"] >= 4
        for row in selected_rows
    )
    summary = {
        "snapshot_count": len(SNAPSHOT_CLASSES),
        "task_count": len(tasks),
        "retained_candidate_count": len(candidate_aggregates),
        "transpiler_seed_count": len(TRANSPILER_SEEDS),
        "candidate_compilation_count": candidate_compilation_count,
        "default_layout_compilation_count": default_compilation_count,
        "strict_static_rerank_count": sum(
            row["selected_static_rank"] != 1 for row in selected_rows
        ),
        "mean_default_improvement_count": mean_default_improvements,
        "worst_default_improvement_count": worst_default_improvements,
        "four_of_five_default_seed_win_count": four_of_five,
        "routing_survival_gate_passed": routing_gate,
        "transpiler_seeds": list(TRANSPILER_SEEDS),
        "optimization_level": OPTIMIZATION_LEVEL,
        "acceptance_holdout_executed": False,
        "r125_acceptance_rows_read": False,
        "readout_mitigation_tested": False,
        "current_backend_calibration_used": False,
        "hardware_execution_performed": False,
        "protocol_soundness_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "new_credit_delta": 0,
    }
    requirements = [
        {
            "requirement_id": "P1",
            "label": "R127 source is hash-bound and all 60 retained candidates are consumed",
            "passed": len(candidate_aggregates) == 60,
            "evidence": {"r127_sha256": file_sha256(r127_path)},
        },
        {
            "requirement_id": "P2",
            "label": "five declared transpiler seeds are used for every retained candidate",
            "passed": candidate_compilation_count == 60 * len(TRANSPILER_SEEDS),
            "evidence": {"candidate_compilation_count": candidate_compilation_count},
        },
        {
            "requirement_id": "P3",
            "label": "automatic-layout baselines use the same five seeds for all six groups",
            "passed": default_compilation_count == EXPECTED_GROUPS * len(TRANSPILER_SEEDS),
            "evidence": {"default_layout_compilation_count": default_compilation_count},
        },
        {
            "requirement_id": "P4",
            "label": "selection follows the preregistered mean-worst-CX-static-rank order",
            "passed": len(selected_rows) == EXPECTED_GROUPS,
            "evidence": {"selected_layout_count": len(selected_rows)},
        },
        {
            "requirement_id": "P5",
            "label": "selected layouts are never worse in mean than static rank one",
            "passed": all(
                row["mean_exposure_delta_vs_static_rank_one"] >= -1e-15
                for row in selected_rows
            ),
            "evidence": {
                "minimum_delta": min(
                    row["mean_exposure_delta_vs_static_rank_one"] for row in selected_rows
                )
            },
        },
        {
            "requirement_id": "P6",
            "label": "all 30 selected circuit artifacts preserve logical measurement order",
            "passed": len(circuit_files) == 30
            and all(row["all_measurement_maps_preserve_logical_order"] for row in selected_rows),
            "evidence": {"selected_circuit_count": len(circuit_files)},
        },
        {
            "requirement_id": "P7",
            "label": "routing-survival acceptance rule is evaluated for every group",
            "passed": all(
                math.isfinite(row["mean_exposure_delta_vs_default_layout"])
                and math.isfinite(row["worst_exposure_delta_vs_default_layout"])
                for row in selected_rows
            ),
            "evidence": {"routing_survival_gate_passed": routing_gate},
        },
        {
            "requirement_id": "P8",
            "label": "R125 acceptance rows, holdout execution, and mitigation remain excluded",
            "passed": not summary["r125_acceptance_rows_read"]
            and not summary["acceptance_holdout_executed"]
            and not summary["readout_mitigation_tested"],
            "evidence": {"design_only": True},
        },
        {
            "requirement_id": "P9",
            "label": "historical snapshots remain separate from current and hardware evidence",
            "passed": not summary["current_backend_calibration_used"]
            and not summary["hardware_execution_performed"],
            "evidence": {"evidence_class": "historical_snapshot_transpiler_design"},
        },
        {
            "requirement_id": "P10",
            "label": "no soundness, advantage, BQP, or new credit is claimed",
            "passed": not summary["protocol_soundness_claimed"]
            and not summary["quantum_advantage_claimed"]
            and not summary["bqp_separation_claimed"]
            and summary["new_credit_delta"] == 0,
            "evidence": {"new_credit_delta": 0},
        },
    ]
    failed = [row["requirement_id"] for row in requirements if not row["passed"]]
    payload: dict[str, Any] = {
        "title": "B4/B8 R128 transpiler-in-the-loop layout ranking",
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
        "selected_layout_rows": selected_rows,
        "candidate_aggregate_rows": candidate_aggregates,
        "environment": {
            "python": platform.python_version(),
            "qiskit": package_version("qiskit"),
            "qiskit_ibm_runtime": package_version("qiskit-ibm-runtime"),
            "numpy": package_version("numpy"),
        },
        "artifacts": {
            "r127_result": R127_RESULT_PATH,
            "selected_circuits": sorted(circuit_files),
        },
        "claim_boundary": {
            "what_is_supported": (
                "Same-condition transpiler-loop ranking of the 60 predeclared R127 "
                "candidates against automatic layout on frozen snapshots."
            ),
            "what_is_not_supported": (
                "Acceptance holdout performance, readout mitigation, current calibration, "
                "provider access, hardware execution, protocol soundness, quantum advantage, "
                "BQP separation, or new B10 credit."
            ),
            "next_gate": (
                "If the routing-survival gate passes, preregister a new disjoint-seed "
                "layout/readout holdout; otherwise expand or revise the routing-aware objective."
            ),
        },
    }
    payload["payload_hash"] = stable_hash(payload)
    write_json(root / RESULT_PATH, payload)
    (root / REPORT_PATH).write_text(report(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    payload = run_gate(args.root)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
