#!/usr/bin/env python3
"""B6/T-B6-004 readiness gate for crystallographic descriptor evidence.

This gate does not rerun the crystallographic descriptor screen. It audits the
existing T-B6-004 result for reproducibility and claim discipline in the current
runtime, then records whether the project is allowed to upgrade B6 from a
descriptor-boundary artifact to a materials-discovery or mechanism claim.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys
from pathlib import Path
from typing import Any


METHOD = "b6_crystallographic_reproducibility_gate_v0"
STATUS = "crystallographic_reproducibility_gate_failed_not_material_discovery_claim"
EXPECTED_SOURCE_METHOD = "b6_crystallographic_descriptor_screen_v0"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _requirement(req_id: str, label: str, passed: bool, evidence: str, blocker: str = "") -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": req_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }
    if not passed:
        row["blocker"] = blocker
    return row


def build_gate(source_path: Path) -> dict[str, Any]:
    source_exists = source_path.exists()
    source = _load_json(source_path) if source_exists else {}
    metrics = source.get("metrics", {})
    claim_boundary = source.get("claim_boundary", {})
    validation_errors = source.get("validation_errors", [])
    pymatgen_available = _has_module("pymatgen")
    numpy_available = _has_module("numpy")

    no_material_claim = (
        claim_boundary.get("material_discovery") is False
        and claim_boundary.get("mechanism_solved") is False
        and claim_boundary.get("complete_database") is False
    )
    post_split_crystallo_ap = float(metrics.get("post_split_crystallo_ap", 0.0))
    post_split_family_prior_ap = float(metrics.get("post_split_family_prior_ap", 0.0))
    requirements = [
        _requirement(
            "R1",
            "source T-B6-004 result exists",
            source_exists and source.get("method") == EXPECTED_SOURCE_METHOD,
            f"path={source_path}; method={source.get('method')!r}",
            "missing or mismatched source result",
        ),
        _requirement(
            "R2",
            "expanded table has at least 50 records",
            int(source.get("record_count", 0)) >= 50,
            f"record_count={source.get('record_count')}",
            "crystallographic screen is too small for this gate",
        ),
        _requirement(
            "R3",
            "post-2008 split has at least 24 records",
            int(source.get("post_split_record_count", 0)) >= 24,
            f"post_split_record_count={source.get('post_split_record_count')}",
            "post-split holdout remains too thin",
        ),
        _requirement(
            "R4",
            "expanded negative controls are present",
            int(source.get("negative_control_count", 0)) >= 18,
            f"negative_control_count={source.get('negative_control_count')}",
            "negative controls are not broad enough",
        ),
        _requirement(
            "R5",
            "source boundary claims crystallographic descriptor data",
            claim_boundary.get("real_crystallographic_data") is True,
            f"real_crystallographic_data={claim_boundary.get('real_crystallographic_data')}",
            "source result is not marked as crystallographic evidence",
        ),
        _requirement(
            "R6",
            "current runtime can reproduce pymatgen-dependent descriptors",
            pymatgen_available,
            f"pymatgen_available={pymatgen_available}; python={platform.python_version()}",
            "install and pin pymatgen or provide an equivalent crystallographic descriptor backend",
        ),
        _requirement(
            "R7",
            "source validation errors are empty",
            len(validation_errors) == 0,
            f"validation_errors={validation_errors}",
            "the source screen still reports validation blockers",
        ),
        _requirement(
            "R8",
            "post-split crystallographic AP beats family prior",
            post_split_crystallo_ap > post_split_family_prior_ap,
            f"post_split_crystallo_ap={post_split_crystallo_ap}; post_split_family_prior_ap={post_split_family_prior_ap}",
            "family-prior baseline remains stronger than the crystallographic channel",
        ),
        _requirement(
            "R9",
            "DFT observables are available",
            claim_boundary.get("dft_observables") is True,
            f"dft_observables={claim_boundary.get('dft_observables')}",
            "add DFT-computed descriptors before a candidate-ranking claim",
        ),
        _requirement(
            "R10",
            "B5-computed observables are available",
            claim_boundary.get("b5_computed_observables") is True,
            f"b5_computed_observables={claim_boundary.get('b5_computed_observables')}",
            "connect the B6 ranking to B5 computed response observables",
        ),
        _requirement(
            "R11",
            "no discovery, mechanism, or complete-database claim",
            no_material_claim,
            (
                f"material_discovery={claim_boundary.get('material_discovery')}; "
                f"mechanism_solved={claim_boundary.get('mechanism_solved')}; "
                f"complete_database={claim_boundary.get('complete_database')}"
            ),
            "claim boundary overstates the result",
        ),
    ]

    failed = [row for row in requirements if not row["passed"]]
    return {
        "benchmark_id": "B6",
        "method": METHOD,
        "status": STATUS,
        "source_result": str(source_path),
        "source_method": source.get("method"),
        "source_status": source.get("status"),
        "source_model_status": source.get("model_status"),
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "executable": sys.executable,
            "numpy_available": numpy_available,
            "pymatgen_available": pymatgen_available,
        },
        "metrics": {
            "record_count": source.get("record_count"),
            "family_count": source.get("family_count"),
            "negative_control_count": source.get("negative_control_count"),
            "post_split_record_count": source.get("post_split_record_count"),
            "post_split_positive_count": source.get("post_split_positive_count"),
            "top_k": source.get("top_k"),
            "negatives_in_top_k": source.get("negatives_in_top_k"),
            "all_crystallo_ap_k": metrics.get("all_crystallo_ap_k"),
            "post_split_crystallo_ap": metrics.get("post_split_crystallo_ap"),
            "post_split_family_prior_ap": metrics.get("post_split_family_prior_ap"),
            "post_split_physics_ap": metrics.get("post_split_physics_ap"),
            "post_split_combined_ap": metrics.get("post_split_combined_ap"),
            "family_holdout_mean_physics_ap": metrics.get("family_holdout_mean_physics_ap"),
            "source_validation_error_count": len(validation_errors),
        },
        "requirements": requirements,
        "gate_pass_count": len(requirements) - len(failed),
        "gate_fail_count": len(failed),
        "failed_requirement_ids": [row["id"] for row in failed],
        "validation_errors": [row["blocker"] for row in failed],
        "claim_boundary": {
            "material_discovery_claimed": False,
            "mechanism_solved": False,
            "complete_materials_database": False,
            "reproducible_crystallographic_descriptor_claim": False,
            "dft_observable_claimed": False,
            "b5_computed_observable_claimed": False,
            "solution_claimed": False,
            "next_required": (
                "pin a reproducible crystallographic backend, remove source validation blockers, "
                "beat family-prior post-split AP, and attach DFT or B5-computed observables"
            ),
        },
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    metrics = payload["metrics"]
    lines = [
        "# B6 Crystallographic Reproducibility Gate",
        "",
        f"- Benchmark: `{payload['benchmark_id']}`",
        f"- Method: `{payload['method']}`",
        f"- Status: `{payload['status']}`",
        f"- Source result: `{payload['source_result']}`",
        f"- Source method/status: `{payload['source_method']}` / `{payload['source_status']}`",
        f"- Gates passed/failed: {payload['gate_pass_count']} / {payload['gate_fail_count']}",
        "",
        "## Result",
        "",
        (
            "T-B6-004 has useful crystallographic descriptor evidence, but it is not a "
            "materials-discovery, solved-mechanism, complete-database, DFT-observable, "
            "or B5-computed-observable result. In the current runtime, the crystallographic "
            "backend is not reproducible because `pymatgen` is unavailable."
        ),
        "",
        "## Metrics",
        "",
        f"- Records / families: {metrics.get('record_count')} / {metrics.get('family_count')}",
        f"- Negative controls / top-k negatives: {metrics.get('negative_control_count')} / {metrics.get('negatives_in_top_k')}",
        f"- Post-split records / positives: {metrics.get('post_split_record_count')} / {metrics.get('post_split_positive_count')}",
        f"- AP all crystallographic: {metrics.get('all_crystallo_ap_k')}",
        f"- AP post-split crystallographic / family prior / physics / combined: {metrics.get('post_split_crystallo_ap')} / {metrics.get('post_split_family_prior_ap')} / {metrics.get('post_split_physics_ap')} / {metrics.get('post_split_combined_ap')}",
        f"- Source validation error count: {metrics.get('source_validation_error_count')}",
        "",
        "## Gate Requirements",
        "",
        "| ID | Pass | Requirement | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["requirements"]:
        mark = "yes" if row["passed"] else "no"
        lines.append(f"| {row['id']} | {mark} | {row['label']} | {row['evidence']} |")
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        "- No material discovery is claimed.",
        "- No high-temperature superconductivity mechanism is claimed solved.",
        "- No complete materials database is claimed.",
        "- No DFT or B5-computed observable is claimed.",
        "- Next required artifact: a pinned crystallographic/DFT/B5 observable pipeline that beats family-prior baselines on post-split holdouts.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-result",
        type=Path,
        default=Path("results/B6_crystallographic_descriptor_screen_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B6_crystallographic_reproducibility_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B6_crystallographic_reproducibility_gate.md"),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_gate(args.source_result)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if args.pretty else None
    args.json_output.write_text(json.dumps(payload, indent=indent, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload, args.markdown_output)
    print(json.dumps({
        "status": payload["status"],
        "gate_pass_count": payload["gate_pass_count"],
        "gate_fail_count": payload["gate_fail_count"],
        "failed_requirement_ids": payload["failed_requirement_ids"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
