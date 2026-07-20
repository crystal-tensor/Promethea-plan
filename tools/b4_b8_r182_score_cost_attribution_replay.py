#!/usr/bin/env python3
"""Run the preregistered R182 exact-score cost-attribution matrix."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r153_independent_seed_replication_holdout import TARGET_CLASSES
from b4_b8_r154_deterministic_automatic_replay import (
    canonical_hash,
    target_descriptor,
)
from b4_b8_r160_deterministic_error_map_remediation import (
    build_error_map,
    source_inventory,
)
from b4_b8_r181_active_limb_replay import (
    R157_INPUT,
    R159_DIR,
    R160_PROTOCOL_PATH,
    R161_PATH,
    actual_environment,
    error_map_from_trace,
    exact_leaf_oracle,
    expected_standard_vectors,
    imported_binary as r181_imported_binary,
    mapping_vector,
    new_config,
)


METHOD = "b4_b8_r182_score_cost_attribution_replay_v0"
PROTOCOL_PATH = "results/B4_B8_R182_score_cost_attribution_protocol_v0.json"
AMENDMENT_PATH = (
    "results/B4_B8_R182_score_cost_attribution_protocol_amendment_v1.json"
)
CONTRACT_PATH = (
    "benchmarks/B4_B8_R182_score_cost_attribution_execution_contract_v0.json"
)
R181_PROTOCOL_PATH = "results/B4_B8_R181_active_limb_protocol_v0.json"
BINARY_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R182_score_cost_pyext.x86_64-linux-gnu.so"
)
BUILD_MANIFEST_PATH = (
    "research/source_lineage/Qiskit_2_4_1_R182_score_cost_linux_x86_64_build_manifest.json"
)
OUT_DIR = "results/B4_B8_R182_score_cost_attribution_replay"
RESULT_PATH = "results/B4_B8_R182_score_cost_attribution_v0.json"
REPORT_PATH = "research/B4_B8_R182_score_cost_attribution.md"
POLICIES = {
    "rust_biguint_exact_retained_binary64": {
        "timing": "vf2_layout_pass_average_exact_score",
        "probe": "vf2_layout_pass_average_exact_score_cost_traced",
    },
    "rust_fixed_exact_retained_binary64": {
        "timing": "vf2_layout_pass_average_fixed_exact_score",
        "probe": "vf2_layout_pass_average_fixed_exact_score_cost_traced",
    },
    "rust_active_limb_exact_retained_binary64": {
        "timing": "vf2_layout_pass_average_active_fixed_exact_score",
        "probe": "vf2_layout_pass_average_active_fixed_exact_score_cost_traced",
    },
}
COUNTER_KEYS = [
    "leaf_construction_count",
    "destination_zeroed_limb_count",
    "arithmetic_limb_visit_count",
    "comparison_limb_visit_count",
    "carry_extension_count",
    "maximum_used_limb_count",
    "biguint_heap_allocation_count",
    "biguint_heap_allocated_bytes",
]


def validate_hash_field(payload: dict[str, Any], field: str, label: str) -> str:
    body = dict(payload)
    observed = body.pop(field, None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R182 {label} hash mismatch")
    return str(observed)


def validate_contract(
    root: Path,
    protocol: dict[str, Any],
    amendment: dict[str, Any],
    contract: dict[str, Any],
    *,
    require_unopened: bool,
    require_build: bool,
) -> None:
    protocol_hash = validate_hash_field(protocol, "payload_hash", "protocol")
    amendment_hash = validate_hash_field(amendment, "payload_hash", "amendment")
    validate_hash_field(contract, "payload_hash", "execution contract")
    if protocol.get("method") != "b4_b8_r182_score_cost_attribution_protocol_v0":
        raise ValueError("R182 protocol identity mismatch")
    if amendment.get("method") != "b4_b8_r182_protocol_count_label_amendment_v1":
        raise ValueError("R182 amendment identity mismatch")
    if (
        contract.get("contract_id")
        != "B4-B8-R182-score-cost-attribution-execution-contract-v0"
    ):
        raise ValueError("R182 execution contract identity mismatch")
    if contract.get("execution_started") is not False:
        raise ValueError("R182 execution contract is not unopened")
    if contract.get("protocol_payload_hash") != protocol_hash:
        raise ValueError("R182 protocol binding mismatch")
    if contract.get("amendment_payload_hash") != amendment_hash:
        raise ValueError("R182 amendment binding mismatch")
    for section in ("source_bindings", "tool_bindings"):
        for binding in contract[section].values():
            path = root / binding["path"]
            if not path.is_file() or file_sha256(path) != binding["sha256"]:
                raise ValueError(f"R182 binding mismatch: {binding['path']}")
    generator = contract["contract_generator_binding"]
    generator_path = root / generator["path"]
    if (
        not generator_path.is_file()
        or file_sha256(generator_path) != generator["sha256"]
    ):
        raise ValueError("R182 execution-contract generator binding mismatch")
    if require_unopened:
        for relative in contract["result_paths_must_be_absent"]:
            if (root / relative).exists():
                raise ValueError(f"R182 evidence existed before execution: {relative}")
    if require_build:
        for relative in contract["build_output_paths_created_before_replay"]:
            if not (root / relative).exists():
                raise ValueError(f"R182 required build output is missing: {relative}")


def validate_runtime_preregistration(
    root: Path, preregistration: dict[str, str], contract: dict[str, Any]
) -> None:
    public = contract["public_preregistration"]
    if preregistration["discussion"] != public["discussion"]:
        raise ValueError("R182 runtime discussion does not match the public contract")
    if preregistration["created_at"] != public["created_at"]:
        raise ValueError("R182 runtime creation time does not match the public contract")
    current_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    if preregistration["commit"] != current_commit:
        raise ValueError("R182 runtime commit does not match the checked-out commit")
    ancestor = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            public["amendment_public_commit"],
            current_commit,
        ],
        cwd=root,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ValueError("R182 runtime commit predates the public count amendment")


def imported_binary() -> Path:
    path = r181_imported_binary()
    return path


def run_vf2(function: Any, dag: Any, target: Any, error_map: Any) -> list[int] | None:
    output = function(
        dag,
        target,
        new_config(),
        strict_direction=False,
        avg_error_map=error_map,
    )
    return mapping_vector(output.new_mapping(), target.num_qubits)


def run_probe(
    function: Any, dag: Any, target: Any, error_map: Any
) -> tuple[list[int] | None, dict[str, int]]:
    output, values = function(
        dag,
        target,
        new_config(),
        strict_direction=False,
        avg_error_map=error_map,
    )
    if len(values) != len(COUNTER_KEYS):
        raise ValueError(f"R182 probe returned {len(values)} counters")
    counters = {key: int(value) for key, value in zip(COUNTER_KEYS, values)}
    if any(value < 0 for value in counters.values()):
        raise ValueError("R182 probe returned a negative counter")
    return mapping_vector(output.new_mapping(), target.num_qubits), counters


def worker_path(cell_id: str, policy: str) -> str:
    return f"{OUT_DIR}/{cell_id}__{policy}.json"


def cell_definitions(r181: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for dataset in r181["datasets"]:
        for profile in r181["standard_profiles"]:
            rows.append(
                {
                    "cell_id": f"standard__{dataset['dataset_id']}__{profile}",
                    "kind": "standard",
                    "dataset_id": dataset["dataset_id"],
                    "profile_id": profile,
                }
            )
    for mode in r181["small_gap_modes"]:
        rows.append(
            {
                "cell_id": f"small-gap__{mode}",
                "kind": "small-gap",
                "mode": mode,
            }
        )
    return rows


def prepare_standard(root: Path, r181: dict[str, Any], cell: dict[str, Any]) -> dict[str, Any]:
    from qiskit import qasm3
    from qiskit.converters import circuit_to_dag

    dataset = next(
        row for row in r181["datasets"] if row["dataset_id"] == cell["dataset_id"]
    )
    source_worker_path = (
        root / dataset["worker_directory"] / f"{cell['profile_id']}.json"
    )
    source_worker = json.loads(source_worker_path.read_text(encoding="utf-8"))
    _, exact_expected = expected_standard_vectors(source_worker)
    trace = json.loads(
        (root / R159_DIR / f"{cell['profile_id']}.json").read_text(encoding="utf-8")
    )
    circuit = qasm3.load(root / dataset["input_path"])
    backend = TARGET_CLASSES["FakeNairobiV2"]()
    return {
        "dag": circuit_to_dag(circuit),
        "target": backend.target,
        "backend": backend,
        "work_units": [
            {
                "subcell_id": cell["cell_id"],
                "case_id": None,
                "error_map": error_map_from_trace(backend.target, trace),
                "expected": exact_expected,
            }
        ],
        "input_path": dataset["input_path"],
        "source_worker_path": str(source_worker_path.relative_to(root)),
    }


def prepare_small_gap(root: Path, r181: dict[str, Any], cell: dict[str, Any]) -> dict[str, Any]:
    from qiskit import qasm3
    from qiskit.converters import circuit_to_dag

    r160_payload = json.loads((root / R160_PROTOCOL_PATH).read_text(encoding="utf-8"))
    cases = {
        row["case_id"]: row
        for row in r160_payload["protocol"]["perturbation_cases"]
    }
    native = json.loads(
        (root / R159_DIR / "native_hashset_order.json").read_text(encoding="utf-8")
    )
    inventory_rows = source_inventory(native)
    r161 = json.loads((root / R161_PATH).read_text(encoding="utf-8"))
    circuit = qasm3.load(root / R157_INPUT)
    backend = TARGET_CLASSES["FakeNairobiV2"]()
    units = []
    for case_id in r181["small_gap_cases"]:
        error_map, _, descriptor = build_error_map(
            backend.target, inventory_rows, cell["mode"], cases[case_id]
        )
        oracle = exact_leaf_oracle(descriptor, r161["interaction_inventory"])
        if oracle["minimizer_count"] != 1:
            raise ValueError(f"R182 expected one minimizer for {cell['mode']}/{case_id}")
        units.append(
            {
                "subcell_id": f"{cell['cell_id']}__{case_id}",
                "case_id": case_id,
                "error_map": error_map,
                "error_map_descriptor_hash": descriptor["payload_hash"],
                "exact_minimum_gap_ulp_ratio": oracle["minimum_gap_ulp_ratio"],
                "expected": [6, 5, 4, 3, 2, 1, 0],
            }
        )
    return {
        "dag": circuit_to_dag(circuit),
        "target": backend.target,
        "backend": backend,
        "work_units": units,
        "input_path": R157_INPUT,
        "source_worker_path": None,
    }


def execute_worker(
    root: Path,
    protocol: dict[str, Any],
    amendment: dict[str, Any],
    contract: dict[str, Any],
    r181: dict[str, Any],
    cell_id: str,
    policy: str,
    preregistration: dict[str, str],
) -> dict[str, Any]:
    from qiskit._accelerate import vf2_layout as vf2_module

    cells = {row["cell_id"]: row for row in cell_definitions(r181)}
    if cell_id not in cells or policy not in POLICIES:
        raise ValueError("R182 worker identity is outside the frozen matrix")
    path = root / worker_path(cell_id, policy)
    if path.exists():
        raise ValueError(f"R182 worker already exists: {path}")
    binary = imported_binary()
    if file_sha256(binary) != file_sha256(root / BINARY_PATH):
        raise ValueError("R182 worker imported the wrong accelerator")
    cell = cells[cell_id]
    prepared = (
        prepare_standard(root, r181, cell)
        if cell["kind"] == "standard"
        else prepare_small_gap(root, r181, cell)
    )
    timing = getattr(vf2_module, POLICIES[policy]["timing"])
    probe = getattr(vf2_module, POLICIES[policy]["probe"])
    units = prepared["work_units"]
    counts = amendment["corrected_workload_counts"]
    warmup_count = counts["warmups_per_cell"]
    measured_count = counts["measured_replays_per_cell"]
    started_at = int(time.time())
    warmups = []
    for index in range(warmup_count):
        unit = units[index % len(units)]
        warmups.append(
            run_vf2(timing, prepared["dag"], prepared["target"], unit["error_map"])
        )
    rows = []
    for replay_index in range(measured_count):
        unit = units[replay_index % len(units)]
        started = time.perf_counter_ns()
        timing_vector = run_vf2(
            timing, prepared["dag"], prepared["target"], unit["error_map"]
        )
        elapsed = time.perf_counter_ns() - started
        probe_vector, counters = run_probe(
            probe, prepared["dag"], prepared["target"], unit["error_map"]
        )
        row = {
            "cell_id": cell_id,
            "subcell_id": unit["subcell_id"],
            "kind": cell["kind"],
            "policy": policy,
            "replay_index": replay_index,
            "case_id": unit["case_id"],
            "timing_mapping_vector": timing_vector,
            "probe_mapping_vector": probe_vector,
            "expected_mapping_vector": unit["expected"],
            "timing_matches_expected": timing_vector == unit["expected"],
            "probe_matches_expected": probe_vector == unit["expected"],
            "timing_probe_mapping_match": timing_vector == probe_vector,
            "cost_counters": counters,
            "elapsed_nanoseconds": elapsed,
            "timing_call_count": 1,
            "counter_probe_call_count": 1,
            "simulation_execution_count": 0,
            "total_simulated_shots": 0,
        }
        if "error_map_descriptor_hash" in unit:
            row["error_map_descriptor_hash"] = unit["error_map_descriptor_hash"]
            row["exact_minimum_gap_ulp_ratio"] = unit[
                "exact_minimum_gap_ulp_ratio"
            ]
        row["row_hash"] = canonical_hash(row)
        rows.append(row)
    manifest = {
        "title": "R182 score-cost attribution isolated worker",
        "version": 0,
        "method": METHOD,
        "status": "isolated_worker_complete",
        "cell": cell,
        "policy": policy,
        "process_id": os.getpid(),
        "process_instance_uuid": str(uuid.uuid4()),
        "started_at_unix": started_at,
        "preregistration": preregistration,
        "protocol_payload_hash": protocol["payload_hash"],
        "amendment_payload_hash": amendment["payload_hash"],
        "contract_payload_hash": contract["payload_hash"],
        "environment": actual_environment(),
        "accelerator_path": str(binary),
        "accelerator_sha256": file_sha256(binary),
        "input_path": prepared["input_path"],
        "input_sha256": file_sha256(root / prepared["input_path"]),
        "source_worker_path": prepared["source_worker_path"],
        "target_descriptor_sha256": target_descriptor(prepared["backend"])[
            "descriptor_hash"
        ],
        "measurement_pair_order": ["uninstrumented_timing", "counter_probe"],
        "warmup_call_count": len(warmups),
        "warmup_matches_expected": sum(
            vector == units[index % len(units)]["expected"]
            for index, vector in enumerate(warmups)
        ),
        "recorded_measurement_count": len(rows),
        "timing_call_count": sum(row["timing_call_count"] for row in rows),
        "counter_probe_call_count": sum(
            row["counter_probe_call_count"] for row in rows
        ),
        "timing_expected_match_count": sum(
            row["timing_matches_expected"] for row in rows
        ),
        "probe_expected_match_count": sum(
            row["probe_matches_expected"] for row in rows
        ),
        "timing_probe_mapping_match_count": sum(
            row["timing_probe_mapping_match"] for row in rows
        ),
        "replay_rows": rows,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
    }
    manifest["manifest_hash"] = canonical_hash(manifest)
    write_json(path, manifest)
    return manifest


def prepare_overlay(root: Path) -> Path:
    spec = importlib.util.find_spec("qiskit")
    if spec is None or not spec.submodule_search_locations:
        raise ValueError("R182 cannot locate the installed Qiskit package")
    source = Path(next(iter(spec.submodule_search_locations))).resolve()
    binary_hash = file_sha256(root / BINARY_PATH)
    overlay = Path("/tmp") / f"prometheus-r182-overlay-{binary_hash[:16]}"
    if overlay.exists():
        shutil.rmtree(overlay)
    package = overlay / "qiskit"
    shutil.copytree(source, package)
    for candidate in package.glob("_accelerate*.so"):
        candidate.unlink()
    installed = package / "_accelerate.abi3.so"
    shutil.copy2(root / BINARY_PATH, installed)
    if file_sha256(installed) != binary_hash:
        raise ValueError("R182 overlay accelerator copy mismatch")
    return overlay


def launch_worker(
    root: Path,
    overlay: Path,
    cell_id: str,
    policy: str,
    preregistration: dict[str, str],
    process_environment: dict[str, str],
) -> None:
    environment = dict(os.environ)
    environment.update(process_environment)
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(overlay), str(root / "tools"), environment.get("PYTHONPATH", "")]
    )
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--root",
        str(root),
        "--worker-cell",
        cell_id,
        "--worker-policy",
        policy,
        "--preregistration-commit",
        preregistration["commit"],
        "--preregistration-discussion",
        preregistration["discussion"],
        "--preregistration-created-at",
        preregistration["created_at"],
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"R182 worker failed: {cell_id}/{policy}\n"
            f"{completed.stdout}\n{completed.stderr}"
        )


def validate_worker(manifest: dict[str, Any], path: Path) -> None:
    validate_hash_field(manifest, "manifest_hash", f"worker {path.name}")
    for row in manifest["replay_rows"]:
        validate_hash_field(row, "row_hash", f"row {path.name}")


def average_ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda row: (row[1], row[0]))
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(indexed):
        end = cursor + 1
        while end < len(indexed) and indexed[end][1] == indexed[cursor][1]:
            end += 1
        rank = (cursor + 1 + end) / 2
        for index, _ in indexed[cursor:end]:
            ranks[index] = rank
        cursor = end
    return ranks


def pearson(left: list[float], right: list[float]) -> float:
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)
    numerator = sum(
        (x - left_mean) * (y - right_mean) for x, y in zip(left, right)
    )
    left_norm = math.sqrt(sum((x - left_mean) ** 2 for x in left))
    right_norm = math.sqrt(sum((y - right_mean) ** 2 for y in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def spearman(left: list[float], right: list[float]) -> float:
    return pearson(average_ranks(left), average_ranks(right))


def aggregate(
    root: Path,
    protocol: dict[str, Any],
    amendment: dict[str, Any],
    contract: dict[str, Any],
    r181: dict[str, Any],
    preregistration: dict[str, str],
) -> dict[str, Any]:
    build = json.loads((root / BUILD_MANIFEST_PATH).read_text(encoding="utf-8"))
    validate_hash_field(build, "payload_hash", "build manifest")
    manifests = []
    artifacts = []
    for path in sorted((root / OUT_DIR).glob("*.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        validate_worker(manifest, path)
        manifests.append(manifest)
        artifacts.append(
            {
                "path": str(path.relative_to(root)),
                "sha256": file_sha256(path),
                "manifest_hash": manifest["manifest_hash"],
            }
        )
    rows = [row for manifest in manifests for row in manifest["replay_rows"]]
    expected_cells = cell_definitions(r181)
    expected_worker_count = len(expected_cells) * len(POLICIES)
    counts = amendment["corrected_workload_counts"]
    by_cell_policy: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_cell_policy[(row["cell_id"], row["policy"])].append(row)
    cell_summaries = []
    for cell in expected_cells:
        policy_rows = {
            policy: by_cell_policy[(cell["cell_id"], policy)] for policy in POLICIES
        }
        summary = {"cell": cell, "policies": {}}
        for policy, selected in policy_rows.items():
            summary["policies"][policy] = {
                "measurement_count": len(selected),
                "median_elapsed_nanoseconds": statistics.median(
                    row["elapsed_nanoseconds"] for row in selected
                ),
                "median_cost_counters": {
                    key: statistics.median(
                        row["cost_counters"][key] for row in selected
                    )
                    for key in COUNTER_KEYS
                },
            }
        biguint = summary["policies"]["rust_biguint_exact_retained_binary64"]
        fixed = summary["policies"]["rust_fixed_exact_retained_binary64"]
        active = summary["policies"][
            "rust_active_limb_exact_retained_binary64"
        ]
        summary["active_to_fixed_median_time_ratio"] = (
            active["median_elapsed_nanoseconds"] / fixed["median_elapsed_nanoseconds"]
        )
        summary["active_to_biguint_median_time_ratio"] = (
            active["median_elapsed_nanoseconds"]
            / biguint["median_elapsed_nanoseconds"]
        )
        summary["biguint_minus_active_median_nanoseconds"] = (
            biguint["median_elapsed_nanoseconds"]
            - active["median_elapsed_nanoseconds"]
        )
        summary["cell_summary_hash"] = canonical_hash(summary)
        cell_summaries.append(summary)

    counter_vectors: dict[tuple[str, str, str], set[tuple[int, ...]]] = defaultdict(set)
    for row in rows:
        key = (row["cell_id"], row["policy"], row["subcell_id"])
        counter_vectors[key].add(tuple(row["cost_counters"][name] for name in COUNTER_KEYS))
    deterministic_group_count = sum(len(values) == 1 for values in counter_vectors.values())
    fixed_arithmetic = sum(
        row["cost_counters"]["arithmetic_limb_visit_count"]
        for row in rows
        if row["policy"] == "rust_fixed_exact_retained_binary64"
    )
    active_arithmetic = sum(
        row["cost_counters"]["arithmetic_limb_visit_count"]
        for row in rows
        if row["policy"] == "rust_active_limb_exact_retained_binary64"
    )
    fixed_zeroed = sum(
        row["cost_counters"]["destination_zeroed_limb_count"]
        for row in rows
        if row["policy"] == "rust_fixed_exact_retained_binary64"
    )
    active_zeroed = sum(
        row["cost_counters"]["destination_zeroed_limb_count"]
        for row in rows
        if row["policy"] == "rust_active_limb_exact_retained_binary64"
    )
    arithmetic_reduction = 1.0 - (active_arithmetic / fixed_arithmetic)
    active_times = [
        row["elapsed_nanoseconds"]
        for row in rows
        if row["policy"] == "rust_active_limb_exact_retained_binary64"
    ]
    fixed_times = [
        row["elapsed_nanoseconds"]
        for row in rows
        if row["policy"] == "rust_fixed_exact_retained_binary64"
    ]
    aggregate_active_to_fixed = statistics.median(active_times) / statistics.median(
        fixed_times
    )
    h1 = next(
        row
        for row in protocol["frozen_hypotheses"]
        if row["hypothesis_id"] == "H1-full-destination-initialization"
    )
    h1_supported = (
        arithmetic_reduction
        >= h1["minimum_arithmetic_visit_reduction_fraction"]
        and active_zeroed == fixed_zeroed
        and aggregate_active_to_fixed
        > h1["maximum_end_to_end_active_to_fixed_ratio_for_speed_success"]
    )
    allocation_pressure = [
        float(
            row["policies"]["rust_biguint_exact_retained_binary64"][
                "median_cost_counters"
            ]["biguint_heap_allocated_bytes"]
        )
        for row in cell_summaries
    ]
    timing_gap = [
        float(row["biguint_minus_active_median_nanoseconds"])
        for row in cell_summaries
    ]
    correlation = spearman(allocation_pressure, timing_gap)
    h2 = next(
        row
        for row in protocol["frozen_hypotheses"]
        if row["hypothesis_id"] == "H2-biguint-heap-cost"
    )
    h2_supported = (
        min(allocation_pressure) > 0
        and correlation >= h2["minimum_spearman_rank_correlation"]
    )
    h3_supported = len(cell_summaries) == 13
    classifications = {
        "H1-full-destination-initialization": {
            "classification": (
                "full_width_initialization_or_common_cost_pressure_consistent_not_causal"
                if h1_supported
                else "rejected_or_inconclusive"
            ),
            "supported_under_frozen_rule": h1_supported,
            "arithmetic_visit_reduction_fraction": arithmetic_reduction,
            "fixed_destination_zeroed_limb_count": fixed_zeroed,
            "active_destination_zeroed_limb_count": active_zeroed,
            "aggregate_active_to_fixed_median_time_ratio": aggregate_active_to_fixed,
        },
        "H2-biguint-heap-cost": {
            "classification": (
                "biguint_heap_pressure_supported"
                if h2_supported
                else "biguint_heap_pressure_rejected"
            ),
            "supported_under_frozen_rule": h2_supported,
            "allocation_pressure_positive_all_cells": min(allocation_pressure) > 0,
            "spearman_rank_correlation": correlation,
        },
        "H3-candidate-shape": {
            "classification": (
                "cell_heterogeneity_reported" if h3_supported else "cell_coverage_failed"
            ),
            "supported_under_frozen_rule": h3_supported,
            "reported_cell_count": len(cell_summaries),
        },
    }
    all_mappings_pass = all(
        row["timing_matches_expected"]
        and row["probe_matches_expected"]
        and row["timing_probe_mapping_match"]
        for row in rows
    )
    counters_complete = all(
        set(row["cost_counters"]) == set(COUNTER_KEYS)
        and all(value >= 0 for value in row["cost_counters"].values())
        for row in rows
    )
    requirements = {
        "P1": True,
        "P2": all(
            manifest["started_at_unix"]
            > int(
                datetime.fromisoformat(
                    preregistration["created_at"].replace("Z", "+00:00")
                ).timestamp()
            )
            for manifest in manifests
        ),
        "P3": True,
        "P4": (
            build.get("status")
            == "linux_x86_64_pyext_built_and_imported_after_preregistration"
            and build.get("preregistration") == preregistration
            and build.get("accelerator", {}).get("sha256")
            == file_sha256(root / BINARY_PATH)
            and build.get("github_actions", {}).get("sha")
            == preregistration["commit"]
            and build.get("github_actions", {}).get("run_url", "").startswith(
                "https://github.com/crystal-tensor/Prometheus-plan/actions/runs/"
            )
        ),
        "P5": all_mappings_pass,
        "P6": counters_complete,
        "P7": deterministic_group_count == len(counter_vectors),
        "P8": (
            len(manifests) == expected_worker_count
            and len(rows) == counts["measured_calls_all_policies"]
            and sum(manifest["warmup_call_count"] for manifest in manifests)
            == counts["warmup_calls_all_policies"]
            and all(
                manifest["recorded_measurement_count"]
                == counts["measured_replays_per_cell"]
                for manifest in manifests
            )
        ),
        "P9": set(classifications)
        == {"H1-full-destination-initialization", "H2-biguint-heap-cost", "H3-candidate-shape"},
        "P10": False,
        "P11": all(
            row["simulation_execution_count"] == 0
            and row["total_simulated_shots"] == 0
            for row in rows
        ),
        "P12": True,
    }
    summary = {
        "worker_count": len(manifests),
        "expected_worker_count": expected_worker_count,
        "workload_cell_count": len(cell_summaries),
        "recorded_measurement_count": len(rows),
        "timing_call_count": sum(row["timing_call_count"] for row in rows),
        "counter_probe_call_count": sum(
            row["counter_probe_call_count"] for row in rows
        ),
        "warmup_call_count": sum(manifest["warmup_call_count"] for manifest in manifests),
        "total_qiskit_function_call_count": (
            sum(row["timing_call_count"] + row["counter_probe_call_count"] for row in rows)
            + sum(manifest["warmup_call_count"] for manifest in manifests)
        ),
        "timing_expected_match_count": sum(
            row["timing_matches_expected"] for row in rows
        ),
        "probe_expected_match_count": sum(
            row["probe_matches_expected"] for row in rows
        ),
        "timing_probe_mapping_match_count": sum(
            row["timing_probe_mapping_match"] for row in rows
        ),
        "counter_determinism_group_count": len(counter_vectors),
        "counter_determinism_pass_count": deterministic_group_count,
        "requirements_passed": sum(requirements.values()),
        "requirements_failed": sum(not value for value in requirements.values()),
        "pending_requirement": "P10 independent oracle",
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
    }
    result = {
        "title": "B4/B8/B10 R182 exact-score cost attribution",
        "version": 0,
        "method": METHOD,
        "status": "cost_attribution_complete_independent_oracle_pending",
        "preregistration": preregistration,
        "protocol_path": PROTOCOL_PATH,
        "protocol_payload_hash": protocol["payload_hash"],
        "amendment_path": AMENDMENT_PATH,
        "amendment_payload_hash": amendment["payload_hash"],
        "contract_path": CONTRACT_PATH,
        "contract_payload_hash": contract["payload_hash"],
        "build_manifest_path": BUILD_MANIFEST_PATH,
        "build_manifest_payload_hash": build["payload_hash"],
        "counter_keys": COUNTER_KEYS,
        "counter_definitions": contract["counter_definitions"],
        "measurement_pair_contract": contract["measurement_pair_contract"],
        "cell_summaries": cell_summaries,
        "hypothesis_classifications": classifications,
        "requirements": requirements,
        "requirements_passed": summary["requirements_passed"],
        "requirements_failed": summary["requirements_failed"],
        "summary": summary,
        "worker_artifacts": artifacts,
        "hardware_result_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "production_qiskit_remedy_claimed": False,
        "causal_bottleneck_claimed": False,
        "new_credit_delta": 0,
    }
    result["payload_hash"] = canonical_hash(result)
    write_json(root / RESULT_PATH, result)
    write_report(root, result)
    return result


def write_report(root: Path, result: dict[str, Any]) -> None:
    summary = result["summary"]
    h1 = result["hypothesis_classifications"]["H1-full-destination-initialization"]
    h2 = result["hypothesis_classifications"]["H2-biguint-heap-cost"]
    h3 = result["hypothesis_classifications"]["H3-candidate-shape"]
    lines = [
        "# B4/B8/B10 R182 Exact-Score Cost Attribution",
        "",
        f"- Status: `{result['status']}`",
        f"- Result payload hash: `{result['payload_hash']}`",
        f"- Requirements: `{result['requirements_passed']}/12` passed; P10 awaits the independent oracle",
        "",
        "## Paired Measurement",
        "",
        f"R182 completed `{summary['recorded_measurement_count']}` measurement pairs across `{summary['worker_count']}` isolated workers and `{summary['workload_cell_count']}` cells. Each pair timed an uninstrumented exact-score call, then ran a separate counter probe. Timing/probe/expected mappings agree on `{summary['timing_probe_mapping_match_count']}/{summary['recorded_measurement_count']}` rows.",
        "",
        "## Frozen Classifications",
        "",
        f"- H1: `{h1['classification']}`; arithmetic-visit reduction `{h1['arithmetic_visit_reduction_fraction']:.6f}`, active/fixed timing ratio `{h1['aggregate_active_to_fixed_median_time_ratio']:.6f}`.",
        f"- H2: `{h2['classification']}`; allocation/timing-gap Spearman `{h2['spearman_rank_correlation']:.6f}`.",
        f"- H3: `{h3['classification']}` over `{h3['reported_cell_count']}` cells.",
        "",
        "## Claim Boundary",
        "",
        "P10 remains pending until the executor-free oracle reproduces every artifact hash, count, mapping outcome, counter vector, rank correlation, and classification. These source-bound counters may support or reject a diagnostic pressure; they do not prove causality, a production Qiskit remedy, hardware behavior, quantum advantage, BQP separation, a solved frontier, or new credit.",
        "",
    ]
    (root / REPORT_PATH).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    parser.add_argument("--preregistration-created-at", required=True)
    parser.add_argument("--worker-cell")
    parser.add_argument("--worker-policy", choices=sorted(POLICIES))
    args = parser.parse_args()
    root = args.root.resolve()
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    amendment = json.loads((root / AMENDMENT_PATH).read_text(encoding="utf-8"))
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    r181 = json.loads((root / R181_PROTOCOL_PATH).read_text(encoding="utf-8"))
    preregistration = {
        "commit": args.preregistration_commit,
        "discussion": args.preregistration_discussion,
        "created_at": args.preregistration_created_at,
    }
    validate_contract(
        root,
        protocol,
        amendment,
        contract,
        require_unopened=not bool(args.worker_cell),
        require_build=True,
    )
    validate_runtime_preregistration(root, preregistration, contract)
    if args.worker_cell:
        execute_worker(
            root,
            protocol,
            amendment,
            contract,
            r181,
            str(args.worker_cell),
            str(args.worker_policy),
            preregistration,
        )
        return 0
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "amd64"}:
        raise ValueError("R182 replay requires Linux x86-64")
    overlay = prepare_overlay(root)
    for cell in cell_definitions(r181):
        for policy in POLICIES:
            launch_worker(
                root,
                overlay,
                cell["cell_id"],
                policy,
                preregistration,
                contract["process_environment"],
            )
    result = aggregate(root, protocol, amendment, contract, r181, preregistration)
    print(
        json.dumps(
            {
                "status": result["status"],
                "payload_hash": result["payload_hash"],
                "requirements_passed": result["requirements_passed"],
                "requirements_failed": result["requirements_failed"],
                "summary": result["summary"],
                "hypothesis_classifications": result["hypothesis_classifications"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
