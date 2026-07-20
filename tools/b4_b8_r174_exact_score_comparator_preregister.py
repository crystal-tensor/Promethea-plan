#!/usr/bin/env python3
"""Freeze the R174 fixed-grid exact-score comparator experiment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from b4_b8_r119_private_observable_bundle_gate import write_json
from b4_b8_r126_calibration_attribution_ledger import file_sha256
from b4_b8_r154_deterministic_automatic_replay import canonical_hash


METHOD = "b4_b8_r174_exact_score_comparator_protocol_v0"
PROTOCOL_PATH = "results/B4_B8_R174_exact_score_comparator_protocol_v0.json"
CONTRACT_PATH = "benchmarks/B4_B8_R174_exact_score_comparator_contract_v0.json"
REPORT_PATH = "research/B4_B8_R174_exact_score_comparator_protocol.md"
RESULT_PATH = "results/B4_B8_R174_exact_score_comparator_v0.json"
ORACLE_PATH = "results/B4_B8_R174_independent_exact_score_oracle_v0.json"

DATASETS = [
    {
        "dataset_id": "r169_non_tie",
        "result_path": "results/B4_B8_R169_target_compatible_candidate_replay_v0.json",
        "worker_directory": "results/B4_B8_R169_target_compatible_candidate_replay",
        "expected_rows": 192,
        "expected_relation": "source_and_exact_agree",
    },
    {
        "dataset_id": "r170_path_true_tie",
        "result_path": "results/B4_B8_R170_near_tie_candidate_replay_v0.json",
        "worker_directory": "results/B4_B8_R170_near_tie_candidate_replay",
        "expected_rows": 192,
        "expected_relation": "source_one_ulp_split_exact_first_seen_tie",
    },
    {
        "dataset_id": "r172_t_tree_true_tie",
        "result_path": "results/B4_B8_R172_second_near_tie_candidate_replay_v0.json",
        "worker_directory": "results/B4_B8_R172_second_near_tie_candidate_replay",
        "expected_rows": 192,
        "expected_relation": "source_one_ulp_split_exact_first_seen_tie",
    },
]

TOOL_PATHS = [
    "tools/b4_b8_r174_exact_score_comparator.py",
    "tools/b4_b8_r174_exact_score_comparator_preregister.py",
    "tools/b4_b8_r174_exact_score_comparator_replay.py",
    "tools/b4_b8_r174_independent_exact_score_oracle.py",
]


def source_binding(root: Path, path: str) -> dict[str, Any]:
    payload: dict[str, Any] = {"path": path, "sha256": file_sha256(root / path)}
    if path.endswith(".json"):
        parsed = json.loads((root / path).read_text(encoding="utf-8"))
        for key in ("payload_hash", "case_analysis_payload_hash"):
            if key in parsed:
                payload[key] = parsed[key]
    return payload


def build_report(protocol: dict[str, Any], contract: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# B4/B8/B10 R174 Exact-Score Comparator Protocol",
            "",
            "- Status: `preregistered_unopened`",
            f"- Protocol payload hash: `{protocol['payload_hash']}`",
            f"- Contract payload hash: `{contract['payload_hash']}`",
            "",
            "## Research Question",
            "",
            "Can a fixed-grid exact accumulator repair the two observed one-ULP false winners while preserving every declared non-tie and first-seen tie control?",
            "",
            "## Frozen Comparator",
            "",
            "Each finite binary64 leaf is decoded into an integer coefficient on the exact `2^-1074` grid. Candidate scores are compared as arbitrary-precision integers, and equality preserves the first candidate seen. The candidate set, Qiskit source, routing output, and target are not modified.",
            "",
            "## Frozen Matrix",
            "",
            "- R169: 192 target-compatible non-tie replays.",
            "- R170: 192 path-graph exact ties with a source-order one-ULP split.",
            "- R172: 192 nonisomorphic T-tree exact ties with a source-order one-ULP split.",
            "- R160: 4 exact-tie and 28 exact non-tie controls.",
            "- All six candidate permutations per replay must select the first exact minimizer in that permutation.",
            "",
            "## Claim Boundary",
            "",
            "This is a preregistered shadow-comparator experiment. It is not a Qiskit source patch, production remedy, performance result, hardware result, quantum advantage, BQP separation, solved frontier, or new credit.",
            "",
        ]
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for path in (root / PROTOCOL_PATH, root / CONTRACT_PATH, root / REPORT_PATH):
        if path.exists():
            raise ValueError(f"R174 preregistration output already exists: {path}")
    source_paths = [
        "results/B4_B8_R160_deterministic_error_map_remediation/case_analysis.json",
        "results/B4_B8_R173_first_divergent_combine_trace_v0.json",
    ]
    for dataset in DATASETS:
        source_paths.append(dataset["result_path"])
        source_paths.extend(
            str(path.relative_to(root))
            for path in sorted((root / dataset["worker_directory"]).glob("*.json"))
        )
    bindings = {
        f"source_{index:02d}": source_binding(root, path)
        for index, path in enumerate(source_paths, start=1)
    }
    protocol = {
        "title": "B4/B8/B10 R174 fixed-grid exact-score comparator protocol",
        "version": 0,
        "method": METHOD,
        "status": "preregistered_unopened",
        "source_target_id": "T-B4-002cs/T-B8-003cw/T-B10-009ci-r174-protocol",
        "upstream_target_id": "T-B4-002cq/T-B8-003cu/T-B10-009cg-r173",
        "research_question": "Can exact fixed-grid score comparison remove two cross-graph one-ULP false winners without changing declared non-ties or first-seen exact ties?",
        "algorithm": {
            "input": "finite IEEE-754 binary64 leaf bit patterns retained by the source trace",
            "representation": "signed arbitrary-precision integer multiples of 2^-1074",
            "comparison": "strict integer less-than",
            "tie_policy": "preserve the first candidate seen on exact equality",
            "candidate_generation_changed": False,
            "qiskit_source_changed": False,
        },
        "datasets": DATASETS,
        "r160_controls": {"exact_tie_rows": 4, "exact_non_tie_rows": 28},
        "permutation_rule": "all six permutations of every three-candidate replay must select the first exact minimizer in that permutation",
        "acceptance_requirements": [
            "576/576 replay rows and 1728/1728 candidate payloads validate",
            "all exact-grid totals equal the committed exact retained-leaf totals",
            "R169 source selection remains unchanged on 192/192 rows",
            "R170 selects the first exact minimizer on 192/192 rows",
            "R172 selects the first exact minimizer on 192/192 rows",
            "all 3456 candidate-permutation checks select the first exact minimizer",
            "R160 passes 4/4 tie and 28/28 non-tie controls",
            "an independent standard-library Fraction oracle reproduces every row",
        ],
        "forbidden_claims": [
            "qiskit_bug",
            "source_patch",
            "production_remedy",
            "performance_improvement",
            "hardware_result",
            "quantum_advantage",
            "bqp_separation",
            "solved_frontier",
            "new_credit",
        ],
        "planned_artifacts": {
            "contract": CONTRACT_PATH,
            "result": RESULT_PATH,
            "independent_oracle": ORACLE_PATH,
            "report": "research/B4_B8_R174_exact_score_comparator.md",
            "oracle_report": "research/B4_B8_R174_independent_exact_score_oracle.md",
        },
    }
    protocol["payload_hash"] = canonical_hash(protocol)
    write_json(root / PROTOCOL_PATH, protocol)
    contract = {
        "contract_id": "B4-B8-R174-exact-score-comparator-contract-v0",
        "execution_started": False,
        "protocol_path": PROTOCOL_PATH,
        "protocol_payload_hash": protocol["payload_hash"],
        "source_bindings": bindings,
        "tool_bindings": {
            Path(path).stem: {"path": path, "sha256": file_sha256(root / path)}
            for path in TOOL_PATHS
        },
        "expected_counts": {
            "dataset_count": 3,
            "worker_file_count": 9,
            "replay_row_count": 576,
            "candidate_count": 1728,
            "candidate_permutation_count": 3456,
            "r160_tie_controls": 4,
            "r160_non_tie_controls": 28,
        },
        "result_paths_must_be_absent": [RESULT_PATH, ORACLE_PATH],
    }
    contract["payload_hash"] = canonical_hash(contract)
    write_json(root / CONTRACT_PATH, contract)
    (root / REPORT_PATH).write_text(build_report(protocol, contract), encoding="utf-8")
    print(json.dumps({"protocol": protocol, "contract": contract}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

