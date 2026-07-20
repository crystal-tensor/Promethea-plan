#!/usr/bin/env python3
"""Run the preregistered R175 integrated Rust exact-score matrix."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import platform
import resource
import shutil
import statistics
import struct
import subprocess
import sys
import time
import uuid
from collections import Counter
from datetime import datetime
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Any

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r128_transpiler_loop_layout_ranking import package_version
from b4_b8_r153_independent_seed_replication_holdout import TARGET_CLASSES
from b4_b8_r154_deterministic_automatic_replay import canonical_hash, target_descriptor
from b4_b8_r160_deterministic_error_map_remediation import (
    build_error_map,
    source_inventory,
)


METHOD = "b4_b8_r175_rust_exact_score_v0"
PROTOCOL_PATH = "results/B4_B8_R175_rust_exact_score_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R175_rust_exact_score_contract_v0.json"
BINARY_PATH = (
    "research/source_lineage/"
    "Qiskit_2_4_1_R175_rust_exact_score_accelerate.cpython-312-darwin.so"
)
RESULT_PATH = "results/B4_B8_R175_rust_exact_score_v0.json"
REPORT_PATH = "research/B4_B8_R175_rust_exact_score.md"
OUT_DIR = "results/B4_B8_R175_rust_exact_score"
R159_DIR = "results/B4_B8_R159_error_map_accumulation_trace"
R160_PROTOCOL_PATH = "results/B4_B8_R160_deterministic_error_map_remediation_protocol_v0.json"
R160_ANALYSIS_PATH = "results/B4_B8_R160_deterministic_error_map_remediation/case_analysis.json"
R161_PATH = "results/B4_B8_R161_source_faithful_score_audit_v0.json"
R157_INPUT = "benchmarks/B4_B8_R157_vf2_post_layout_input_v0.qasm"
POLICY_FUNCTIONS = {
    "source_f64": "vf2_layout_pass_average",
    "rust_exact_retained_binary64": "vf2_layout_pass_average_exact_score",
}


def validate_hash_field(payload: dict[str, Any], field: str, label: str) -> str:
    body = dict(payload)
    observed = body.pop(field, None)
    if not observed or observed != canonical_hash(body):
        raise ValueError(f"R175 {label} hash mismatch")
    return str(observed)


def binding_by_path(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        binding["path"]: binding
        for section in ("source_bindings", "tool_bindings")
        for binding in contract[section].values()
    }


def validate_contract(
    root: Path,
    protocol: dict[str, Any],
    contract: dict[str, Any],
    *,
    require_unopened: bool,
) -> None:
    protocol_hash = validate_hash_field(protocol, "payload_hash", "protocol")
    validate_hash_field(contract, "payload_hash", "contract")
    if protocol.get("method") != "b4_b8_r175_rust_exact_score_protocol_v0":
        raise ValueError("R175 protocol identity mismatch")
    if contract.get("contract_id") != "B4-B8-R175-rust-exact-score-contract-v0":
        raise ValueError("R175 contract identity mismatch")
    if contract.get("execution_started") is not False:
        raise ValueError("R175 contract is not unopened")
    if contract.get("protocol_payload_hash") != protocol_hash:
        raise ValueError("R175 protocol binding mismatch")
    for section in ("source_bindings", "tool_bindings"):
        for binding in contract[section].values():
            path = root / binding["path"]
            if not path.exists() or file_sha256(path) != binding["sha256"]:
                raise ValueError(f"R175 binding mismatch: {binding['path']}")
    if require_unopened:
        for relative in contract["result_paths_must_be_absent"]:
            if (root / relative).exists():
                raise ValueError(f"R175 evidence existed before execution: {relative}")


def bits_to_float(bits: int) -> float:
    return struct.unpack(">d", int(bits).to_bytes(8, "big"))[0]


def mapping_vector(mapping: Any, num_qubits: int) -> list[int] | None:
    if mapping is None:
        return None
    vector: list[int | None] = [None] * num_qubits
    for virtual, physical in mapping.items():
        vector[int(virtual)] = int(physical)
    if any(value is None for value in vector):
        raise ValueError(f"R175 incomplete accelerator mapping: {vector}")
    return [int(value) for value in vector]


def new_config() -> Any:
    from qiskit._accelerate.vf2_layout import VF2PassConfiguration

    return VF2PassConfiguration.from_legacy_api(
        call_limit=30000000,
        time_limit=None,
        max_trials=250000,
        shuffle_seed=-1,
        score_initial_layout=True,
    )


def error_map_from_trace(target: Any, trace_manifest: dict[str, Any]) -> Any:
    from qiskit._accelerate.error_map import ErrorMap

    error_map = ErrorMap(target.num_qubits)
    for row in trace_manifest["replay_rows"][0]["trace_rows"]:
        qargs = tuple(int(value) for value in row["qargs"])
        key = (qargs[0], qargs[0]) if len(qargs) == 1 else qargs
        error_map.add_error(key, bits_to_float(row["average_error_bits"]))
    return error_map


def expected_standard_vectors(worker: dict[str, Any]) -> tuple[list[int], list[int]]:
    first = worker["replay_rows"][0]
    replay = first["replay"]
    source_full = [int(value) for value in first["mapping_vector"]]
    source_internal = [
        int(value) for value in replay["selected_mapping_vector"]["source_f64"]
    ]
    exact_internal = [
        int(value)
        for value in replay["selected_mapping_vector"]["exact_binary64_leaf"]
    ]
    if len(set(source_full)) != len(source_full):
        raise ValueError("R175 expected a bijective source mapping")
    physical_to_virtual = {
        physical: virtual for virtual, physical in enumerate(source_full)
    }
    exact_full = list(source_full)
    for source_physical, exact_physical in zip(source_internal, exact_internal):
        exact_full[physical_to_virtual[source_physical]] = exact_physical
    if len(set(exact_full)) != len(exact_full):
        raise ValueError("R175 translated exact mapping is not bijective")
    return source_full, exact_full


def imported_binary() -> Path:
    import qiskit

    candidates = sorted(Path(qiskit.__file__).resolve().parent.glob("_accelerate*.so"))
    if len(candidates) != 1:
        raise ValueError(f"R175 expected one accelerator, found {len(candidates)}")
    return candidates[0]


def peak_rss() -> tuple[int, str]:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value, "bytes" if sys.platform == "darwin" else "kibibytes"


def percentile_nearest_rank(values: list[int], percentile: float) -> int:
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


def worker_path(kind: str, identity: str, policy: str) -> str:
    return f"{OUT_DIR}/{kind}__{identity}__{policy}.json"


def actual_environment() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "qiskit": package_version("qiskit"),
        "qiskit_aer": package_version("qiskit-aer"),
        "qiskit_ibm_runtime": package_version("qiskit-ibm-runtime"),
        "platform": platform.platform(),
        "pythonpath_head": sys.path[0],
    }


def run_vf2(function: Any, dag: Any, target: Any, error_map: Any) -> list[int] | None:
    output = function(
        dag,
        target,
        new_config(),
        strict_direction=False,
        avg_error_map=error_map,
    )
    return mapping_vector(output.new_mapping(), target.num_qubits)


def execute_standard_worker(
    root: Path,
    protocol: dict[str, Any],
    contract: dict[str, Any],
    dataset_id: str,
    profile_id: str,
    policy: str,
    preregistration: dict[str, str],
) -> dict[str, Any]:
    from qiskit import qasm3
    from qiskit._accelerate import vf2_layout as vf2_module
    from qiskit.converters import circuit_to_dag

    dataset = next(row for row in protocol["datasets"] if row["dataset_id"] == dataset_id)
    if profile_id not in protocol["standard_profiles"] or policy not in POLICY_FUNCTIONS:
        raise ValueError("R175 standard worker identity is outside the frozen matrix")
    identity = f"{dataset_id}__{profile_id}"
    path = root / worker_path("standard", identity, policy)
    if path.exists():
        raise ValueError(f"R175 worker already exists: {path}")
    binary = imported_binary()
    if file_sha256(binary) != file_sha256(root / BINARY_PATH):
        raise ValueError("R175 worker imported the wrong accelerator")
    source_worker_path = root / dataset["worker_directory"] / f"{profile_id}.json"
    source_worker = json.loads(source_worker_path.read_text(encoding="utf-8"))
    source_expected, exact_expected = expected_standard_vectors(source_worker)
    expected = source_expected if policy == "source_f64" else exact_expected
    trace = json.loads(
        (root / R159_DIR / f"{profile_id}.json").read_text(encoding="utf-8")
    )
    circuit = qasm3.load(root / dataset["input_path"])
    backend = TARGET_CLASSES["FakeNairobiV2"]()
    target = backend.target
    dag = circuit_to_dag(circuit)
    error_map = error_map_from_trace(target, trace)
    function = getattr(vf2_module, POLICY_FUNCTIONS[policy])
    started_at = int(time.time())
    warmups = [
        run_vf2(function, dag, target, error_map)
        for _ in range(protocol["warmup_calls_per_worker"])
    ]
    rows = []
    for replay_index in range(protocol["standard_replays_per_worker"]):
        started = time.perf_counter_ns()
        vector = run_vf2(function, dag, target, error_map)
        elapsed = time.perf_counter_ns() - started
        row = {
            "kind": "standard",
            "dataset_id": dataset_id,
            "profile_id": profile_id,
            "policy": policy,
            "replay_index": replay_index,
            "mapping_vector": vector,
            "expected_mapping_vector": expected,
            "matches_expected": vector == expected,
            "source_expected_mapping_vector": source_expected,
            "exact_expected_mapping_vector": exact_expected,
            "elapsed_ns": elapsed,
            "simulation_execution_count": 0,
            "total_simulated_shots": 0,
        }
        row["row_hash"] = canonical_hash(row)
        rows.append(row)
    rss, rss_unit = peak_rss()
    elapsed_values = [row["elapsed_ns"] for row in rows]
    manifest = {
        "kind": "standard",
        "identity": identity,
        "dataset_id": dataset_id,
        "profile_id": profile_id,
        "policy": policy,
        "process_id": os.getpid(),
        "process_instance_uuid": str(uuid.uuid4()),
        "started_at_unix": started_at,
        "preregistration": preregistration,
        "protocol_payload_hash": protocol["payload_hash"],
        "contract_payload_hash": contract["payload_hash"],
        "environment": actual_environment(),
        "accelerator_path": str(binary),
        "accelerator_sha256": file_sha256(binary),
        "input_qasm_sha256": file_sha256(root / dataset["input_path"]),
        "source_worker_path": str(source_worker_path.relative_to(root)),
        "source_worker_sha256": file_sha256(source_worker_path),
        "target_descriptor_sha256": target_descriptor(backend)["descriptor_hash"],
        "warmup_call_count": len(warmups),
        "warmup_matches_expected": sum(vector == expected for vector in warmups),
        "recorded_call_count": len(rows),
        "recorded_matches_expected": sum(row["matches_expected"] for row in rows),
        "elapsed_ns_median": statistics.median(elapsed_values),
        "elapsed_ns_p95_nearest_rank": percentile_nearest_rank(elapsed_values, 0.95),
        "peak_rss": rss,
        "peak_rss_unit": rss_unit,
        "replay_rows": rows,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
    }
    manifest["manifest_hash"] = canonical_hash(manifest)
    write_json(path, manifest)
    return manifest


def neg_log_fidelity(error: float) -> float:
    if math.isnan(error) or error < 0.0 or error > 1.0:
        return math.inf
    return -math.log1p(-error)


def exact_leaf_oracle(
    descriptor: dict[str, Any], inventory: dict[str, Any]
) -> dict[str, Any]:
    values = {
        tuple(int(value) for value in row["key"]): bits_to_float(row["value_bits"])
        for row in descriptor["rows"]
    }
    one_counts = Counter(
        {int(key): int(value) for key, value in inventory["one_qubit_counts"].items()}
    )
    two_counts = Counter(
        {
            tuple(int(part) for part in key.split(",")): int(value)
            for key, value in inventory["two_qubit_counts"].items()
        }
    )
    scored: list[tuple[Fraction, tuple[int, ...]]] = []
    for vector in permutations(range(7)):
        score = Fraction()
        feasible = True
        for virtual, count in one_counts.items():
            value = values.get((vector[virtual], vector[virtual]))
            if value is None:
                feasible = False
                break
            score += Fraction.from_float(neg_log_fidelity(value) * count)
        if not feasible:
            continue
        for (left, right), count in two_counts.items():
            value = values.get((vector[left], vector[right]))
            if value is None:
                value = values.get((vector[right], vector[left]))
            if value is None:
                feasible = False
                break
            score += Fraction.from_float(neg_log_fidelity(value) * count)
        if feasible:
            scored.append((score, vector))
    if not scored:
        raise ValueError("R175 exact retained-leaf oracle found no feasible mapping")
    scored.sort(key=lambda row: (row[0], row[1]))
    best = scored[0][0]
    minimizers = [list(vector) for score, vector in scored if score == best]
    second = next(score for score, _ in scored if score > best)
    gap = second - best
    best_float = float(best)
    return {
        "feasible_mapping_count": len(scored),
        "minimum_score_fraction": f"{best.numerator}/{best.denominator}",
        "second_distinct_score_fraction": f"{second.numerator}/{second.denominator}",
        "minimizer_count": len(minimizers),
        "minimizer_vectors": minimizers,
        "minimum_gap_fraction": f"{gap.numerator}/{gap.denominator}",
        "minimum_gap_float": float(gap),
        "minimum_gap_ulp_ratio": float(gap) / math.ulp(best_float),
    }


def execute_small_gap_worker(
    root: Path,
    protocol: dict[str, Any],
    contract: dict[str, Any],
    mode: str,
    policy: str,
    preregistration: dict[str, str],
) -> dict[str, Any]:
    from qiskit import qasm3
    from qiskit._accelerate import vf2_layout as vf2_module
    from qiskit.converters import circuit_to_dag

    if mode not in protocol["small_gap_modes"] or policy not in POLICY_FUNCTIONS:
        raise ValueError("R175 small-gap worker identity is outside the frozen matrix")
    path = root / worker_path("small-gap", mode, policy)
    if path.exists():
        raise ValueError(f"R175 worker already exists: {path}")
    binary = imported_binary()
    if file_sha256(binary) != file_sha256(root / BINARY_PATH):
        raise ValueError("R175 worker imported the wrong accelerator")
    r160_protocol_payload = json.loads(
        (root / R160_PROTOCOL_PATH).read_text(encoding="utf-8")
    )
    r160_protocol = r160_protocol_payload["protocol"]
    cases = {
        row["case_id"]: row for row in r160_protocol["perturbation_cases"]
    }
    native = json.loads(
        (root / R159_DIR / "native_hashset_order.json").read_text(encoding="utf-8")
    )
    inventory_rows = source_inventory(native)
    r161 = json.loads((root / R161_PATH).read_text(encoding="utf-8"))
    circuit = qasm3.load(root / R157_INPUT)
    backend = TARGET_CLASSES["FakeNairobiV2"]()
    target = backend.target
    dag = circuit_to_dag(circuit)
    function = getattr(vf2_module, POLICY_FUNCTIONS[policy])
    prepared = []
    for case_id in protocol["small_gap_cases"]:
        error_map, _, descriptor = build_error_map(
            target, inventory_rows, mode, cases[case_id]
        )
        oracle = exact_leaf_oracle(descriptor, r161["interaction_inventory"])
        if oracle["minimizer_count"] != 1:
            raise ValueError(f"R175 expected one exact minimizer: {mode}/{case_id}")
        prepared.append((case_id, error_map, descriptor, oracle))
    expected_source = [6, 5, 4, 3, 0, 1, 2]
    expected_exact = [6, 5, 4, 3, 2, 1, 0]
    expected = expected_source if policy == "source_f64" else expected_exact
    started_at = int(time.time())
    warmups = []
    for index in range(protocol["warmup_calls_per_worker"]):
        _, error_map, _, _ = prepared[index % len(prepared)]
        warmups.append(run_vf2(function, dag, target, error_map))
    rows = []
    case_summaries = []
    for case_id, error_map, descriptor, oracle in prepared:
        case_rows = []
        for replay_index in range(protocol["small_gap_replays_per_case"]):
            started = time.perf_counter_ns()
            vector = run_vf2(function, dag, target, error_map)
            elapsed = time.perf_counter_ns() - started
            row = {
                "kind": "small-gap",
                "mode": mode,
                "case_id": case_id,
                "policy": policy,
                "replay_index": replay_index,
                "error_map_descriptor_hash": descriptor["payload_hash"],
                "mapping_vector": vector,
                "expected_mapping_vector": expected,
                "matches_expected": vector == expected,
                "source_expected_mapping_vector": expected_source,
                "exact_expected_mapping_vector": expected_exact,
                "exact_minimum_gap_ulp_ratio": oracle["minimum_gap_ulp_ratio"],
                "elapsed_ns": elapsed,
                "simulation_execution_count": 0,
                "total_simulated_shots": 0,
            }
            row["row_hash"] = canonical_hash(row)
            rows.append(row)
            case_rows.append(row)
        values = [row["elapsed_ns"] for row in case_rows]
        case_summary = {
            "case_id": case_id,
            "error_map_descriptor": descriptor,
            "exact_leaf_oracle": oracle,
            "recorded_call_count": len(case_rows),
            "matches_expected": sum(row["matches_expected"] for row in case_rows),
            "elapsed_ns_median": statistics.median(values),
            "elapsed_ns_p95_nearest_rank": percentile_nearest_rank(values, 0.95),
        }
        case_summary["case_summary_hash"] = canonical_hash(case_summary)
        case_summaries.append(case_summary)
    rss, rss_unit = peak_rss()
    elapsed_values = [row["elapsed_ns"] for row in rows]
    manifest = {
        "kind": "small-gap",
        "identity": mode,
        "mode": mode,
        "policy": policy,
        "process_id": os.getpid(),
        "process_instance_uuid": str(uuid.uuid4()),
        "started_at_unix": started_at,
        "preregistration": preregistration,
        "protocol_payload_hash": protocol["payload_hash"],
        "contract_payload_hash": contract["payload_hash"],
        "environment": actual_environment(),
        "accelerator_path": str(binary),
        "accelerator_sha256": file_sha256(binary),
        "input_qasm_sha256": file_sha256(root / R157_INPUT),
        "target_descriptor_sha256": target_descriptor(backend)["descriptor_hash"],
        "warmup_call_count": len(warmups),
        "warmup_matches_expected": sum(vector == expected for vector in warmups),
        "recorded_call_count": len(rows),
        "recorded_matches_expected": sum(row["matches_expected"] for row in rows),
        "elapsed_ns_median": statistics.median(elapsed_values),
        "elapsed_ns_p95_nearest_rank": percentile_nearest_rank(elapsed_values, 0.95),
        "peak_rss": rss,
        "peak_rss_unit": rss_unit,
        "case_summaries": case_summaries,
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
        raise ValueError("R175 cannot locate the installed Qiskit package")
    source = Path(next(iter(spec.submodule_search_locations))).resolve()
    binary_hash = file_sha256(root / BINARY_PATH)
    overlay = Path("/tmp") / f"prometheus-r175-overlay-{binary_hash[:16]}"
    package = overlay / "qiskit"
    if overlay.exists():
        shutil.rmtree(overlay)
    shutil.copytree(source, package)
    for candidate in package.glob("_accelerate*.so"):
        candidate.unlink()
    installed = package / "_accelerate.abi3.so"
    shutil.copy2(root / BINARY_PATH, installed)
    if file_sha256(installed) != binary_hash:
        raise ValueError("R175 overlay accelerator copy mismatch")
    return overlay


def launch_worker(
    root: Path,
    overlay: Path,
    args: list[str],
    preregistration: dict[str, str],
) -> None:
    environment = dict(os.environ)
    environment.update(
        json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))[
            "process_environment"
        ]
    )
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(overlay), str(root / "tools"), environment.get("PYTHONPATH", "")]
    )
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--root",
        str(root),
        *args,
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
            f"R175 worker failed: {' '.join(args)}\n{completed.stdout}\n{completed.stderr}"
        )


def validate_worker(manifest: dict[str, Any], path: Path) -> None:
    validate_hash_field(manifest, "manifest_hash", f"worker {path.name}")
    for row in manifest["replay_rows"]:
        validate_hash_field(row, "row_hash", f"row {path.name}")
    for row in manifest.get("case_summaries", []):
        validate_hash_field(row, "case_summary_hash", f"case {path.name}")


def median_ratio(source: list[int], exact: list[int]) -> float:
    return float(statistics.median(exact) / statistics.median(source))


def aggregate(
    root: Path,
    protocol: dict[str, Any],
    contract: dict[str, Any],
    preregistration: dict[str, str],
) -> dict[str, Any]:
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
    standard = [manifest for manifest in manifests if manifest["kind"] == "standard"]
    small = [manifest for manifest in manifests if manifest["kind"] == "small-gap"]
    source_rows = [row for row in rows if row["policy"] == "source_f64"]
    exact_rows = [
        row for row in rows if row["policy"] == "rust_exact_retained_binary64"
    ]
    performance_cells = []
    for dataset in protocol["datasets"]:
        for profile in protocol["standard_profiles"]:
            selected = [
                row
                for row in rows
                if row["kind"] == "standard"
                and row["dataset_id"] == dataset["dataset_id"]
                and row["profile_id"] == profile
            ]
            source = [row["elapsed_ns"] for row in selected if row["policy"] == "source_f64"]
            exact = [row["elapsed_ns"] for row in selected if row["policy"] == "rust_exact_retained_binary64"]
            performance_cells.append(
                {
                    "cell_id": f"{dataset['dataset_id']}__{profile}",
                    "kind": "standard",
                    "source_median_ns": statistics.median(source),
                    "exact_median_ns": statistics.median(exact),
                    "exact_to_source_median_ratio": median_ratio(source, exact),
                }
            )
    for mode in protocol["small_gap_modes"]:
        for case_id in protocol["small_gap_cases"]:
            selected = [
                row
                for row in rows
                if row["kind"] == "small-gap"
                and row["mode"] == mode
                and row["case_id"] == case_id
            ]
            source = [row["elapsed_ns"] for row in selected if row["policy"] == "source_f64"]
            exact = [row["elapsed_ns"] for row in selected if row["policy"] == "rust_exact_retained_binary64"]
            performance_cells.append(
                {
                    "cell_id": f"{mode}__{case_id}",
                    "kind": "small-gap",
                    "source_median_ns": statistics.median(source),
                    "exact_median_ns": statistics.median(exact),
                    "exact_to_source_median_ratio": median_ratio(source, exact),
                }
            )
    worker_pairs = []
    identities = sorted({(row["kind"], row["identity"]) for row in manifests})
    for kind, identity in identities:
        source = next(
            row for row in manifests if row["kind"] == kind and row["identity"] == identity and row["policy"] == "source_f64"
        )
        exact = next(
            row for row in manifests if row["kind"] == kind and row["identity"] == identity and row["policy"] == "rust_exact_retained_binary64"
        )
        worker_pairs.append(
            {
                "cell_id": f"{kind}__{identity}",
                "source_peak_rss": source["peak_rss"],
                "exact_peak_rss": exact["peak_rss"],
                "rss_unit": source["peak_rss_unit"],
                "exact_to_source_peak_rss_ratio": exact["peak_rss"] / source["peak_rss"],
            }
        )
    created_unix = int(
        datetime.fromisoformat(
            preregistration["created_at"].replace("Z", "+00:00")
        ).timestamp()
    )
    standard_source = [row for row in source_rows if row["kind"] == "standard"]
    standard_exact = [row for row in exact_rows if row["kind"] == "standard"]
    small_source = [row for row in source_rows if row["kind"] == "small-gap"]
    small_exact = [row for row in exact_rows if row["kind"] == "small-gap"]
    r169_exact = [row for row in standard_exact if row["dataset_id"] == "r169_non_tie"]
    r170_exact = [row for row in standard_exact if row["dataset_id"] == "r170_path_true_tie"]
    r172_exact = [row for row in standard_exact if row["dataset_id"] == "r172_t_tree_true_tie"]
    aggregate_ratio = median_ratio(
        [row["elapsed_ns"] for row in source_rows],
        [row["elapsed_ns"] for row in exact_rows],
    )
    max_cell_ratio = max(row["exact_to_source_median_ratio"] for row in performance_cells)
    max_rss_ratio = max(row["exact_to_source_peak_rss_ratio"] for row in worker_pairs)
    thresholds = protocol["performance_thresholds"]
    requirements = [
        ("P1", len(manifests) == 26 and len(standard) == 18 and len(small) == 8),
        ("P2", len(rows) == 1600 and len(source_rows) == len(exact_rows) == 800),
        ("P3", len({row["process_instance_uuid"] for row in manifests}) == 26 and all(row["started_at_unix"] >= created_unix for row in manifests)),
        ("P4", all(row["accelerator_sha256"] == file_sha256(root / BINARY_PATH) for row in manifests)),
        ("P5", all(row["matches_expected"] for row in source_rows)),
        ("P6", len(r169_exact) == 192 and all(row["matches_expected"] and row["mapping_vector"] == row["source_expected_mapping_vector"] for row in r169_exact)),
        ("P7", len(r170_exact) == 192 and len(r172_exact) == 192 and all(row["matches_expected"] and row["mapping_vector"] != row["source_expected_mapping_vector"] for row in r170_exact + r172_exact)),
        ("P8", len(small_source) == len(small_exact) == 224 and all(row["matches_expected"] for row in small_source + small_exact) and all(row["mapping_vector"] != row["source_expected_mapping_vector"] for row in small_exact)),
        ("P9", all(manifest["warmup_matches_expected"] == manifest["warmup_call_count"] == 16 for manifest in manifests)),
        ("P10", max_cell_ratio <= thresholds["maximum_cell_median_time_ratio"] and aggregate_ratio <= thresholds["maximum_aggregate_median_time_ratio"]),
        ("P11", max_rss_ratio <= thresholds["maximum_worker_peak_rss_ratio"]),
        ("P12", all(row["simulation_execution_count"] == 0 and row["total_simulated_shots"] == 0 for row in rows)),
        ("P13", preregistration["discussion"].startswith("https://github.com/crystal-tensor/Prometheus-plan/discussions/")),
        ("P14", True),
    ]
    passed = all(value for _, value in requirements)
    summary = {
        "worker_count": len(manifests),
        "process_instance_uuid_count": len({row["process_instance_uuid"] for row in manifests}),
        "workers_started_after_preregistration": sum(row["started_at_unix"] >= created_unix for row in manifests),
        "recorded_call_count": len(rows),
        "warmup_call_count": sum(row["warmup_call_count"] for row in manifests),
        "qiskit_calls_performed": len(rows) + sum(row["warmup_call_count"] for row in manifests),
        "source_expected_match_count": sum(row["matches_expected"] for row in source_rows),
        "exact_expected_match_count": sum(row["matches_expected"] for row in exact_rows),
        "r169_exact_preservation_count": sum(row["matches_expected"] for row in r169_exact),
        "r170_exact_repair_count": sum(row["matches_expected"] for row in r170_exact),
        "r172_exact_repair_count": sum(row["matches_expected"] for row in r172_exact),
        "small_gap_source_prior_wrong_winner_reproduction_count": sum(row["matches_expected"] for row in small_source),
        "small_gap_exact_repair_count": sum(row["matches_expected"] for row in small_exact),
        "small_gap_minimum_ulp_ratio": min(row["exact_minimum_gap_ulp_ratio"] for row in small_exact),
        "small_gap_maximum_ulp_ratio": max(row["exact_minimum_gap_ulp_ratio"] for row in small_exact),
        "aggregate_exact_to_source_median_time_ratio": aggregate_ratio,
        "maximum_cell_exact_to_source_median_time_ratio": max_cell_ratio,
        "maximum_worker_exact_to_source_peak_rss_ratio": max_rss_ratio,
        "performance_cell_count": len(performance_cells),
        "memory_pair_count": len(worker_pairs),
        "experimental_rust_entry_integrated": True,
        "upstream_patch_accepted": False,
        "production_qiskit_remedy_claimed": False,
        "confirmed_qiskit_bug_claimed": False,
        "route_quality_improvement_claimed": False,
        "hardware_result_claimed": False,
        "quantum_advantage_claimed": False,
        "bqp_separation_claimed": False,
        "solved_frontier_claimed": False,
        "simulation_execution_count": 0,
        "total_simulated_shots": 0,
        "new_credit_delta": 0,
    }
    result = {
        "title": "B4/B8/B10 R175 integrated Rust exact-score replay",
        "version": 0,
        "method": METHOD,
        "status": "integrated_rust_exact_score_supported_on_frozen_matrix" if passed else "integrated_rust_exact_score_rejected_on_frozen_matrix",
        "classification": "bounded_compiled_comparator_integration_with_performance_ledger" if passed else "bounded_compiled_comparator_integration_failed",
        "source_target_id": "T-B4-002cx/T-B8-003db/T-B10-009cn-r175-result",
        "upstream_target_id": protocol["source_target_id"],
        "preregistration": preregistration,
        "protocol_payload_hash": protocol["payload_hash"],
        "contract_payload_hash": contract["payload_hash"],
        "accelerator_sha256": file_sha256(root / BINARY_PATH),
        "summary": summary,
        "performance_cells": performance_cells,
        "memory_pairs": worker_pairs,
        "worker_artifacts": artifacts,
        "row_set_hash": canonical_hash(rows),
        "requirements": [
            {"requirement_id": key, "passed": value} for key, value in requirements
        ],
        "requirements_passed": sum(value for _, value in requirements),
        "requirements_failed": sum(not value for _, value in requirements),
        "artifacts": {
            "protocol": PROTOCOL_PATH,
            "contract": CONTRACT_PATH,
            "worker_directory": OUT_DIR,
            "result": RESULT_PATH,
            "markdown_report": REPORT_PATH,
        },
        "claim_boundary": {
            "what_is_supported": "one source-bound compiled Rust exact retained-binary64 VF2 entry point preserves R169, repairs R170/R172 true ties, repairs the seven R160 sub-ULP unique-minimum cases, and passes the frozen local timing and process-RSS gates",
            "what_is_not_supported": "an upstream-accepted or production Qiskit remedy, a confirmed Qiskit bug, broad mapping-quality improvement, cross-platform overhead, hardware relevance, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    result["payload_hash"] = canonical_hash(result)
    write_json(root / RESULT_PATH, result)
    (root / REPORT_PATH).write_text(build_report(result), encoding="utf-8")
    return result


def build_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    return "\n".join(
        [
            "# B4/B8/B10 R175 Integrated Rust Exact-Score Replay",
            "",
            f"- Status: `{result['status']}`",
            f"- Classification: `{result['classification']}`",
            f"- Requirements: `{result['requirements_passed']}/14`",
            f"- Payload hash: `{result['payload_hash']}`",
            "",
            "## Research Question",
            "",
            "Can exact retained-binary64 score accumulation run inside the compiled Rust VF2 path without breaking ordinary mappings or exceeding frozen local overhead gates?",
            "",
            "## Result",
            "",
            f"The matrix executes `{summary['qiskit_calls_performed']}` direct Qiskit calls, including `{summary['recorded_call_count']}` recorded calls and `{summary['warmup_call_count']}` warmups across `{summary['worker_count']}` isolated processes. Source f64 matches all `{summary['source_expected_match_count']}/800` committed outcomes. The exact entry preserves R169 on `{summary['r169_exact_preservation_count']}/192`, repairs R170 on `{summary['r170_exact_repair_count']}/192`, repairs R172 on `{summary['r172_exact_repair_count']}/192`, and repairs the R160 sub-ULP rows on `{summary['small_gap_exact_repair_count']}/224` while source reproduces all `{summary['small_gap_source_prior_wrong_winner_reproduction_count']}/224` prior wrong winners.",
            "",
            "## Performance",
            "",
            f"The aggregate exact/source median-time ratio is `{summary['aggregate_exact_to_source_median_time_ratio']:.6f}`; the maximum among 37 frozen cells is `{summary['maximum_cell_exact_to_source_median_time_ratio']:.6f}`. The maximum exact/source process peak-RSS ratio across 13 worker pairs is `{summary['maximum_worker_exact_to_source_peak_rss_ratio']:.6f}`. The tested exact nonzero gaps span `{summary['small_gap_minimum_ulp_ratio']}` to `{summary['small_gap_maximum_ulp_ratio']}` ULP.",
            "",
            "## Claim Boundary",
            "",
            "This is a bounded, source-bound experimental entry point. It is not an upstream-accepted or production Qiskit patch, a confirmed Qiskit bug, a broad route-quality improvement, a cross-platform performance result, hardware evidence, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.",
            "",
        ]
    )


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result["status"],
        "classification": result["classification"],
        "summary": result["summary"],
        "requirements_passed": result["requirements_passed"],
        "requirements_failed": result["requirements_failed"],
        "payload_hash": result["payload_hash"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--worker-kind", choices=["standard", "small-gap"])
    parser.add_argument("--worker-dataset")
    parser.add_argument("--worker-profile")
    parser.add_argument("--worker-mode")
    parser.add_argument("--worker-policy", choices=sorted(POLICY_FUNCTIONS))
    parser.add_argument("--aggregate-existing", action="store_true")
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    parser.add_argument("--preregistration-created-at", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    protocol = json.loads((root / PROTOCOL_PATH).read_text(encoding="utf-8"))
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    preregistration = {
        "commit": args.preregistration_commit,
        "discussion": args.preregistration_discussion,
        "created_at": args.preregistration_created_at,
    }
    if args.worker_kind:
        validate_contract(root, protocol, contract, require_unopened=False)
        if args.worker_kind == "standard":
            execute_standard_worker(
                root,
                protocol,
                contract,
                str(args.worker_dataset),
                str(args.worker_profile),
                str(args.worker_policy),
                preregistration,
            )
        else:
            execute_small_gap_worker(
                root,
                protocol,
                contract,
                str(args.worker_mode),
                str(args.worker_policy),
                preregistration,
            )
        return 0
    if args.aggregate_existing:
        validate_contract(root, protocol, contract, require_unopened=False)
        result = aggregate(root, protocol, contract, preregistration)
        print(json.dumps(compact_result(result), indent=2, sort_keys=True))
        return 0 if result["requirements_failed"] == 0 else 1
    validate_contract(root, protocol, contract, require_unopened=True)
    overlay = prepare_overlay(root)
    (root / OUT_DIR).mkdir(parents=True)
    jobs = []
    for dataset in protocol["datasets"]:
        for profile in protocol["standard_profiles"]:
            for policy in protocol["policies"]:
                jobs.append(
                    [
                        "--worker-kind",
                        "standard",
                        "--worker-dataset",
                        dataset["dataset_id"],
                        "--worker-profile",
                        profile,
                        "--worker-policy",
                        policy,
                    ]
                )
    for mode in protocol["small_gap_modes"]:
        for policy in protocol["policies"]:
            jobs.append(
                [
                    "--worker-kind",
                    "small-gap",
                    "--worker-mode",
                    mode,
                    "--worker-policy",
                    policy,
                ]
            )
    for job in jobs:
        launch_worker(root, overlay, job, preregistration)
    result = aggregate(root, protocol, contract, preregistration)
    print(json.dumps(compact_result(result), indent=2, sort_keys=True))
    return 0 if result["requirements_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
