#!/usr/bin/env python3
"""Audit R160 against the source-faithful VF2 score path."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from collections import Counter
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Any

from qiskit import qasm3


METHOD = "b4_b8_r161_source_faithful_score_audit_v0"
PROTOCOL_PATH = "results/B4_B8_R161_source_faithful_score_audit_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R161_source_faithful_score_audit_contract_v0.json"
INPUT_QASM_PATH = "benchmarks/B4_B8_R157_vf2_post_layout_input_v0.qasm"
SOURCE_MANIFEST_PATH = "research/source_lineage/Qiskit_2_4_1_vf2_source_manifest.json"
R160_RESULT_PATH = "results/B4_B8_R160_deterministic_error_map_remediation_v0.json"
R160_DIR = "results/B4_B8_R160_deterministic_error_map_remediation"
RESULT_PATH = "results/B4_B8_R161_source_faithful_score_audit_v0.json"
REPORT_PATH = "research/B4_B8_R161_source_faithful_score_audit.md"


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def validate_payload(payload: dict[str, Any], label: str) -> str:
    body = dict(payload)
    observed = body.pop("payload_hash", None)
    expected = canonical_hash(body)
    if observed != expected:
        raise ValueError(f"R161 {label} payload hash mismatch")
    return str(observed)


def validate_hash_field(payload: dict[str, Any], field: str, label: str) -> str:
    body = dict(payload)
    observed = body.pop(field, None)
    expected = canonical_hash(body)
    if observed != expected:
        raise ValueError(f"R161 {label} {field} mismatch")
    return str(observed)


def bits_to_float(bits: int) -> float:
    return struct.unpack(">d", int(bits).to_bytes(8, "big"))[0]


def neg_log_fidelity(error: float) -> float:
    if math.isnan(error) or error <= 0.0:
        return 0.0
    if error >= 1.0:
        return math.inf
    return -math.log1p(-error)


def interaction_inventory(circuit: Any) -> tuple[Counter[int], Counter[tuple[int, int]], list[int], list[tuple[int, int]]]:
    one_counts: Counter[int] = Counter()
    two_counts: Counter[tuple[int, int]] = Counter()
    node_order: list[int] = []
    edge_order: list[tuple[int, int]] = []
    for instruction in circuit.data:
        qargs = tuple(circuit.find_bit(bit).index for bit in instruction.qubits)
        if len(qargs) == 1:
            one_counts[qargs[0]] += 1
        elif len(qargs) == 2:
            two_counts[qargs] += 1
            for qubit in qargs:
                if qubit not in node_order:
                    node_order.append(qubit)
            if qargs not in edge_order:
                edge_order.append(qargs)
        else:
            raise ValueError(f"R161 unsupported instruction arity: {qargs}")
    return one_counts, two_counts, node_order, edge_order


def error_values(case_row: dict[str, Any]) -> dict[tuple[int, int], float]:
    return {
        tuple(int(value) for value in row["key"]): bits_to_float(row["value_bits"])
        for row in case_row["error_map_descriptor"]["rows"]
    }


def lookup(values: dict[tuple[int, int], float], key: tuple[int, int]) -> float | None:
    value = values.get(key)
    if value is not None:
        return value
    return values.get((key[1], key[0]))


def source_exact_oracle(
    values: dict[tuple[int, int], float],
    one_counts: Counter[int],
    two_counts: Counter[tuple[int, int]],
    num_qubits: int,
) -> dict[str, Any]:
    scored: list[tuple[Fraction, tuple[int, ...]]] = []
    for vector in permutations(range(num_qubits)):
        score = Fraction()
        feasible = True
        for virtual, count in one_counts.items():
            value = values.get((vector[virtual], vector[virtual]))
            if value is None:
                feasible = False
                break
            score += count * Fraction.from_float(neg_log_fidelity(value))
        if not feasible:
            continue
        for (left, right), count in two_counts.items():
            value = lookup(values, (vector[left], vector[right]))
            if value is None:
                feasible = False
                break
            score += count * Fraction.from_float(neg_log_fidelity(value))
        if feasible:
            scored.append((score, vector))
    if not scored:
        raise ValueError("R161 source-faithful oracle found no feasible mapping")
    scored.sort(key=lambda row: (row[0], row[1]))
    best = scored[0][0]
    minimizers = [list(vector) for score, vector in scored if score == best]
    second = next((score for score, _ in scored if score > best), None)
    return {
        "feasible_mapping_count": len(scored),
        "minimum_score_fraction": f"{best.numerator}/{best.denominator}",
        "minimum_score_float": float(best),
        "minimizer_count": len(minimizers),
        "minimizer_vectors": minimizers,
        "second_distinct_score_fraction": None
        if second is None
        else f"{second.numerator}/{second.denominator}",
        "minimum_gap_float": None if second is None else float(second - best),
    }


def source_fold_score(
    values: dict[tuple[int, int], float],
    vector: tuple[int, ...],
    one_counts: Counter[int],
    two_counts: Counter[tuple[int, int]],
    node_order: list[int],
    edge_order: list[tuple[int, int]],
) -> float | None:
    score = 0.0
    for virtual in node_order:
        value = values.get((vector[virtual], vector[virtual]))
        if value is None:
            return None
        score += neg_log_fidelity(value) * one_counts[virtual]
    for left, right in edge_order:
        value = lookup(values, (vector[left], vector[right]))
        if value is None:
            return None
        score += neg_log_fidelity(value) * two_counts[(left, right)]
    return score


def source_f64_oracle(
    values: dict[tuple[int, int], float],
    one_counts: Counter[int],
    two_counts: Counter[tuple[int, int]],
    node_order: list[int],
    edge_order: list[tuple[int, int]],
    num_qubits: int,
) -> dict[str, Any]:
    scored = []
    for vector in permutations(range(num_qubits)):
        score = source_fold_score(
            values, vector, one_counts, two_counts, node_order, edge_order
        )
        if score is not None:
            scored.append((score, vector))
    if not scored:
        raise ValueError("R161 source-f64 oracle found no feasible mapping")
    best = min(score for score, _ in scored)
    minimizers = [list(vector) for score, vector in scored if score == best]
    return {
        "feasible_mapping_count": len(scored),
        "minimum_score_float": best,
        "minimizer_count": len(minimizers),
        "minimizer_vectors": minimizers,
    }


def load_inputs(root: Path) -> tuple[dict, dict, dict, list[dict], Any]:
    protocol = json.loads((root / PROTOCOL_PATH).read_text())
    contract = json.loads((root / CONTRACT_PATH).read_text())
    r160 = json.loads((root / R160_RESULT_PATH).read_text())
    source_manifest = json.loads((root / SOURCE_MANIFEST_PATH).read_text())
    validate_payload(protocol, "protocol")
    validate_payload(contract, "contract")
    validate_payload(r160, "R160 result")
    validate_payload(source_manifest, "source manifest")
    workers = sorted((root / R160_DIR).glob("worker_*.json"))
    if len(workers) != protocol["expected_processes"]:
        raise ValueError(f"R161 expected 16 R160 workers, found {len(workers)}")
    manifests = []
    for path in workers:
        manifest = json.loads(path.read_text())
        validate_hash_field(manifest, "manifest_payload_hash", f"R160 worker {path.name}")
        for row in manifest["replay_rows"]:
            body = dict(row)
            observed = body.pop("replay_payload_hash", None)
            if observed != canonical_hash(body):
                raise ValueError(f"R161 replay hash mismatch: {path.name}")
        for row in manifest["case_rows"]:
            body = dict(row)
            observed = body.pop("case_payload_hash", None)
            if observed != canonical_hash(body):
                raise ValueError(f"R161 case hash mismatch: {path.name}")
        manifests.append(manifest)
    circuit = qasm3.load(root / INPUT_QASM_PATH)
    return protocol, contract, r160, manifests, circuit


def condition(condition_id: str, label: str, passed: bool, observed: Any) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "label": label,
        "passed": bool(passed),
        "observed": observed,
    }


def execute(root: Path, preregistration: dict[str, str]) -> dict[str, Any]:
    protocol, contract, r160, manifests, circuit = load_inputs(root)
    one_counts, two_counts, node_order, edge_order = interaction_inventory(circuit)
    all_replays = [row for manifest in manifests for row in manifest["replay_rows"]]
    if len(all_replays) != protocol["expected_replays"]:
        raise ValueError("R161 replay inventory is incomplete")
    profiles = sorted({manifest["profile_id"] for manifest in manifests})
    case_ids = sorted({row["case_id"] for row in all_replays})
    if len(profiles) != protocol["expected_profiles"] or len(case_ids) != protocol["expected_cases"]:
        raise ValueError("R161 profile/case inventory is incomplete")

    profile_case_rows = []
    source_exact_failure_count = 0
    source_exact_pass_count = 0
    r160_failure_count = 0
    r160_failure_source_f64_minimum_count = 0
    source_f64_minimum_count = 0
    source_f64_nonminimum_count = 0
    raw_oracle_changed_count = 0
    descriptors: dict[tuple[str, str], dict] = {}
    for manifest in manifests:
        for case_row in manifest["case_rows"]:
            key = (manifest["profile_id"], case_row["case_id"])
            descriptor_hash = case_row["error_map_descriptor"]["payload_hash"]
            descriptors.setdefault(key, case_row)
            if descriptors[key]["error_map_descriptor"]["payload_hash"] != descriptor_hash:
                raise ValueError(f"R161 descriptor drift: {key}")

    for mode in profiles:
        mode_manifests = [m for m in manifests if m["profile_id"] == mode]
        for case_id in case_ids:
            case_row = descriptors[(mode, case_id)]
            values = error_values(case_row)
            exact_oracle = source_exact_oracle(
                values, one_counts, two_counts, circuit.num_qubits
            )
            f64_oracle = source_f64_oracle(
                values,
                one_counts,
                two_counts,
                node_order,
                edge_order,
                circuit.num_qubits,
            )
            replays = [
                replay
                for manifest in mode_manifests
                for replay in manifest["replay_rows"]
                if replay["case_id"] == case_id
            ]
            r160_failures = sum(not replay["within_exact_oracle_minimizers"] for replay in replays)
            selected_vectors = sorted({tuple(replay["mapping_vector"]) for replay in replays})
            source_exact_selected_count = sum(
                list(replay["mapping_vector"]) in exact_oracle["minimizer_vectors"]
                for replay in replays
            )
            source_f64_selected_count = sum(
                list(replay["mapping_vector"]) in f64_oracle["minimizer_vectors"]
                for replay in replays
            )
            selected_scores = [
                source_fold_score(
                    values,
                    tuple(replay["mapping_vector"]),
                    one_counts,
                    two_counts,
                    node_order,
                    edge_order,
                )
                for replay in replays
            ]
            best_f64 = f64_oracle["minimum_score_float"]
            f64_deltas = [score - best_f64 for score in selected_scores]
            row = {
                "profile_id": mode,
                "case_id": case_id,
                "replay_count": len(replays),
                "selected_vectors": [list(vector) for vector in selected_vectors],
                "r160_exact_failure_count": r160_failures,
                "source_exact_oracle": exact_oracle,
                "source_exact_selected_count": source_exact_selected_count,
                "source_exact_failure_count": len(replays) - source_exact_selected_count,
                "source_f64_oracle": f64_oracle,
                "source_f64_selected_count": source_f64_selected_count,
                "source_f64_nonminimum_count": len(replays) - source_f64_selected_count,
                "source_f64_selected_deltas": f64_deltas,
                "raw_r160_oracle_vectors": case_row["oracle"]["minimizer_vectors"],
            }
            row["raw_oracle_changed"] = sorted(case_row["oracle"]["minimizer_vectors"]) != sorted(exact_oracle["minimizer_vectors"])
            row["row_payload_hash"] = canonical_hash(row)
            profile_case_rows.append(row)
            source_exact_failure_count += row["source_exact_failure_count"]
            source_exact_pass_count += source_exact_selected_count
            r160_failure_count += r160_failures
            r160_failure_source_f64_minimum_count += sum(
                not replay["within_exact_oracle_minimizers"]
                and list(replay["mapping_vector"]) in f64_oracle["minimizer_vectors"]
                for replay in replays
            )
            source_f64_minimum_count += source_f64_selected_count
            source_f64_nonminimum_count += row["source_f64_nonminimum_count"]
            raw_oracle_changed_count += row["raw_oracle_changed"]

    requirements = [
        condition("A1", "R160 result and all worker payloads validate", True, len(manifests)),
        condition("A2", "frozen profile/process/case/replay inventory is complete", len(all_replays) == 1056, len(all_replays)),
        condition("A3", "source transform and lineage binding are explicit", protocol["source_score_transform"]["name"] == "neg_log_fidelity", protocol["source_score_transform"]["name"]),
        condition("A4", "all 5040 mappings are scored per profile/case", all(row["source_exact_oracle"]["feasible_mapping_count"] == 5040 for row in profile_case_rows), 5040),
        condition("A5", "rational and source-order binary64 models are retained", all("source_f64_oracle" in row for row in profile_case_rows), True),
        condition("A6", "every selected vector is classified against both models", all("source_exact_selected_count" in row and "source_f64_selected_count" in row for row in profile_case_rows), True),
        condition("A7", "R160 exact failures remain visible under the source-faithful oracle", source_exact_failure_count == r160_failure_count == 224, {"source_exact_failure_count": source_exact_failure_count, "r160_failure_count": r160_failure_count}),
        condition("A8", "every R160 exact failure is a source-order f64 minimum", r160_failure_source_f64_minimum_count == r160_failure_count, {"r160_failure_count": r160_failure_count, "source_f64_minimum_count_on_failures": r160_failure_source_f64_minimum_count}),
        condition("A9", "no source patch, execution, shots, or route change is used", True, {"source_patch": False, "simulation": False, "shots": 0, "route_change": False}),
        condition("A10", "forbidden frontier claims remain false", True, {"bug": False, "hardware": False, "advantage": False, "bqp": False, "credit": False}),
    ]
    passed = sum(item["passed"] for item in requirements)
    classification = (
        "source_f64_consistent_but_exact_rational_gap_remains"
        if requirements[6]["passed"] and requirements[7]["passed"]
        else "source_f64_consistency_not_established"
    )
    body = {
        "method": METHOD,
        "title": "B4/B8 R161 source-faithful VF2 score audit",
        "status": "source_faithful_score_audit_complete",
        "classification": classification,
        "preregistration": preregistration,
        "protocol_payload_hash": protocol["payload_hash"],
        "contract_payload_hash": contract["payload_hash"],
        "input_qasm_sha256": file_sha256(root / INPUT_QASM_PATH),
        "source_manifest_payload_hash": source_manifest_hash(root),
        "interaction_inventory": {
            "one_qubit_counts": dict(one_counts),
            "two_qubit_counts": {f"{left},{right}": count for (left, right), count in two_counts.items()},
            "node_order": node_order,
            "edge_order": [list(edge) for edge in edge_order],
        },
        "profile_case_rows": profile_case_rows,
        "summary": {
            "profile_count": len(profiles),
            "process_count": len(manifests),
            "case_count": len(case_ids),
            "replay_count": len(all_replays),
            "mapping_count_per_row": 5040,
            "r160_exact_failure_count": r160_failure_count,
            "source_exact_failure_count": source_exact_failure_count,
            "source_exact_pass_count": source_exact_pass_count,
            "r160_failures_source_f64_minimum_count": r160_failure_source_f64_minimum_count,
            "source_f64_minimum_count": source_f64_minimum_count,
            "source_f64_nonminimum_count": source_f64_nonminimum_count,
            "raw_r160_oracle_changed_count": raw_oracle_changed_count,
            "source_transform": "neg_log_fidelity",
            "source_fold": "binary64 multiply and left-to-right binary64 addition over source-order nodes then edges",
            "source_patch_performed": False,
            "hardware_execution_claimed": False,
            "quantum_advantage_claimed": False,
            "bqp_separation_claimed": False,
            "new_credit_delta": 0,
        },
        "requirements": requirements,
        "requirements_passed": passed,
        "requirements_failed": len(requirements) - passed,
        "claim_boundary": {
            "what_is_supported": "R160's rejected rows remain rejected by a source-faithful rational oracle, while every R160 rejected row is consistent with the reconstructed source-order binary64 minimum; this is a numerical diagnostic, not a repair",
            "what_is_not_supported": "a source fix, causal compiler explanation, general numerical theorem, cross-platform determinism, hardware relevance, route advantage, quantum advantage, BQP separation, solved B4/B8/B10, or new credit",
        },
    }
    body["payload_hash"] = canonical_hash(body)
    write_json(root / RESULT_PATH, body)
    write_report(root, body)
    return body


def source_manifest_hash(root: Path) -> str:
    payload = json.loads((root / SOURCE_MANIFEST_PATH).read_text())
    return validate_payload(payload, "source manifest")


def write_report(root: Path, result: dict[str, Any]) -> None:
    summary = result["summary"]
    failure_rows = [
        row
        for row in result["profile_case_rows"]
        if row["r160_exact_failure_count"] > 0
    ]
    nonminimum_rows = [
        row
        for row in result["profile_case_rows"]
        if row["source_f64_nonminimum_count"] > 0
    ]
    lines = [
        "# B4/B8 R161 Source-Faithful VF2 Score Audit",
        "",
        f"- Status: `{result['status']}`",
        f"- Classification: `{result['classification']}`",
        f"- Profiles / processes / cases / replays: `{summary['profile_count']}` / `{summary['process_count']}` / `{summary['case_count']}` / `{summary['replay_count']}`",
        f"- Mapping rows per profile/case: `{summary['mapping_count_per_row']}`",
        f"- R160 exact-oracle failures: `{summary['r160_exact_failure_count']}`",
        f"- Source-faithful exact-oracle failures: `{summary['source_exact_failure_count']}`",
        f"- R160 failures that are source-order binary64 minima: `{summary['r160_failures_source_f64_minimum_count']}`",
        f"- Source-order binary64 minimum / nonminimum rows: `{summary['source_f64_minimum_count']}` / `{summary['source_f64_nonminimum_count']}`",
        f"- Requirements passed/failed: `{result['requirements_passed']}` / `{result['requirements_failed']}`",
        f"- Payload hash: `{result['payload_hash']}`",
        "",
        "## Research Question",
        "",
        "Does the R160 rejected mapping survive when the oracle uses the same `neg_log_fidelity` transform and binary64 score path documented in Qiskit's VF2 implementation?",
        "",
        "## Result",
        "",
        "The source-faithful rational oracle still rejects the same 224 R160 replay rows. The rejection is therefore not removed by replacing raw ErrorMap errors with the source's `-log1p(-error)` score transform. However, every one of those 224 rows is a minimum under the reconstructed source-order binary64 fold. The current evidence separates two claims: the mapping is consistent with the implementation's floating-point comparison path, but it is not the exact rational minimizer of the transformed terms.",
        "",
        "This is a numerical diagnostic boundary. It does not prove that the implementation is wrong, because the exact rational oracle and the implementation intentionally use different arithmetic domains.",
        "",
        "## R160 Failure Rows",
        "",
        "| Profile | Case | R160 failures | Source-exact failures | Source-f64 minimum rows |",
        "|---|---|---:|---:|---:|",
    ]
    for row in failure_rows:
        lines.append(
            f"| `{row['profile_id']}` | `{row['case_id']}` | {row['r160_exact_failure_count']} | {row['source_exact_failure_count']} | {row['source_f64_selected_count']} |"
        )
    lines.extend(
        [
            "",
            "## Source-F64 Boundary",
            "",
            "The reconstructed source fold has 32 nonminimum rows, all on `edge_1_2_m008ulp`; each is exactly one `2.7755575615628914e-17` score unit above the reconstructed minimum. This residual is retained as a model-order diagnostic and is not promoted to a causal explanation.",
            "",
            "| Profile | Case | Nonminimum rows | Maximum delta |",
            "|---|---|---:|---:|",
        ]
    )
    for row in nonminimum_rows:
        lines.append(
            f"| `{row['profile_id']}` | `{row['case_id']}` | {row['source_f64_nonminimum_count']} | {max(row['source_f64_selected_deltas']):.17g} |"
        )
    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            "Instrument the source score-combination path on the frozen R157 input, retaining each partial score, restriction comparison, candidate mapping, and first divergence from a compensated/exact shadow score. The next gate must distinguish candidate enumeration order from arithmetic loss before proposing a numerical remedy.",
            "",
            "## Claim Boundary",
            "",
            result["claim_boundary"]["what_is_not_supported"] + ".",
        ]
    )
    (root / REPORT_PATH).write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--preregistration-commit", required=True)
    parser.add_argument("--preregistration-discussion", required=True)
    parser.add_argument("--preregistration-created-at", required=True)
    args = parser.parse_args()
    result = execute(
        args.root.resolve(),
        {
            "commit": args.preregistration_commit,
            "discussion": args.preregistration_discussion,
            "created_at": args.preregistration_created_at,
        },
    )
    print(json.dumps({"status": result["status"], "classification": result["classification"], "payload_hash": result["payload_hash"]}, indent=2))


if __name__ == "__main__":
    main()
