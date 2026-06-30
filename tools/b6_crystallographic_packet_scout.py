#!/usr/bin/env python3
"""T-B6-005b: scout crystallographic evidence packets without promoting discovery claims."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


METHOD = "b6_crystallographic_packet_scout_v0"
STATUS = "crystallographic_packet_scout_failed_missing_computed_evidence"
MODEL_STATUS = "contract_packets_mapped_but_backend_observable_and_denominator_evidence_missing"
VERSION = "0.1"
FAILED_IDS = ["S4", "S5", "S6", "S7", "S8"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")


def requirement(requirement_id: str, label: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_payload(root: Path) -> dict[str, Any]:
    start = time.time()
    contract = load_json(root / "results/B6_crystallographic_evidence_contract_gate_v0.json")
    reproducibility = load_json(root / "results/B6_crystallographic_reproducibility_gate_v0.json")

    metrics = reproducibility.get("metrics", {})
    runtime = reproducibility.get("runtime", {})
    packets = contract.get("contract_packets", [])
    packet_ids = contract.get("contract_packet_ids", [])
    source_failures = contract.get("failed_contract_requirement_ids", [])
    source_validation_error_count = int(contract.get("source_validation_error_count", 0))
    post_split_crystallo_ap = float(contract.get("post_split_crystallo_ap", 0.0))
    post_split_family_prior_ap = float(contract.get("post_split_family_prior_ap", 0.0))
    pymatgen_available = bool(contract.get("pymatgen_available"))

    rows = []
    for packet in packets:
        packet_id = packet["id"]
        blocks_gate = packet["source_gate"]
        rows.append(
            {
                "packet_id": packet_id,
                "blocks_gate": blocks_gate,
                "title": packet["title"],
                "required_artifact_count": len(packet.get("acceptance_criteria", [])),
                "current_evidence_rows": 0,
                "ready_for_discovery_claim": False,
                "source_failure_preserved": blocks_gate in ["R6", "R7", "R8", "R9", "R10"],
            }
        )

    requirements = [
        requirement(
            "S1",
            "Crystallographic evidence contract is present and open",
            contract.get("status") == "crystallographic_evidence_contract_open_not_material_discovery_claim",
            {
                "contract_status": contract.get("status"),
                "contract_packet_count": contract.get("contract_packet_count"),
            },
        ),
        requirement(
            "S2",
            "Source reproducibility gate remains mapped",
            reproducibility.get("status") == "crystallographic_reproducibility_gate_failed_not_material_discovery_claim",
            {
                "source_status": reproducibility.get("status"),
                "source_failed_requirement_ids": reproducibility.get("failed_requirement_ids"),
            },
        ),
        requirement(
            "S3",
            "Scope remains the locked 56-record / 28-family / 18-negative-control dataset",
            contract.get("record_count") == 56
            and contract.get("family_count") == 28
            and contract.get("negative_control_count") == 18,
            {
                "record_count": contract.get("record_count"),
                "family_count": contract.get("family_count"),
                "negative_control_count": contract.get("negative_control_count"),
            },
        ),
        requirement(
            "S4",
            "Reproducible crystallographic backend is available",
            pymatgen_available,
            {"pymatgen_available": pymatgen_available, "runtime_pymatgen_available": runtime.get("pymatgen_available")},
        ),
        requirement(
            "S5",
            "Source validation blockers are cleared",
            source_validation_error_count == 0,
            {"source_validation_error_count": source_validation_error_count},
        ),
        requirement(
            "S6",
            "Crystallographic model beats post-split family-prior denominator",
            post_split_crystallo_ap > post_split_family_prior_ap,
            {
                "post_split_crystallo_ap": post_split_crystallo_ap,
                "post_split_family_prior_ap": post_split_family_prior_ap,
            },
        ),
        requirement(
            "S7",
            "DFT observable channel exists",
            False,
            {"dft_observable_rows": 0},
        ),
        requirement(
            "S8",
            "B5-computed observable channel exists",
            False,
            {"b5_computed_observable_rows": 0},
        ),
    ]

    passed = sum(1 for item in requirements if item["passed"])
    failed = len(requirements) - passed
    failed_ids = [item["requirement_id"] for item in requirements if not item["passed"]]
    validation_errors = []
    if failed_ids != FAILED_IDS:
        validation_errors.append(f"Expected failed ids {FAILED_IDS}, got {failed_ids}")
    if len(rows) != 5:
        validation_errors.append("Expected five crystallographic packet rows")

    forbidden_false = {
        "material_discovery_claimed": False,
        "mechanism_solved": False,
        "complete_materials_database": False,
        "reproducible_crystallographic_descriptor_claim": False,
        "dft_observable_claimed": False,
        "b5_computed_observable_claimed": False,
        "solution_claimed": False,
    }
    summary = {
        "source_contract_status": contract.get("status"),
        "source_reproducibility_status": reproducibility.get("status"),
        "packet_scout_requirement_count": len(requirements),
        "packet_scout_requirements_passed": passed,
        "packet_scout_requirements_failed": failed,
        "failed_packet_scout_requirement_ids": failed_ids,
        "contract_packet_count": len(rows),
        "contract_packet_ids": packet_ids,
        "record_count": contract.get("record_count"),
        "family_count": contract.get("family_count"),
        "negative_control_count": contract.get("negative_control_count"),
        "post_split_record_count": contract.get("post_split_record_count"),
        "post_split_crystallo_ap": post_split_crystallo_ap,
        "post_split_family_prior_ap": post_split_family_prior_ap,
        "source_validation_error_count": source_validation_error_count,
        "pymatgen_available": pymatgen_available,
        "dft_observable_rows": 0,
        "b5_computed_observable_rows": 0,
        "crystallographic_packet_scout_ready": False,
        **forbidden_false,
    }

    return {
        "benchmark": "B6",
        "benchmark_id": "B6",
        "title": "B6 crystallographic packet scout",
        "version": VERSION,
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "last_updated": "2026-07-01",
        "elapsed_seconds": time.time() - start,
        "source_metrics": metrics,
        "summary": summary,
        "rows": rows,
        "requirements": requirements,
        "claim_boundary": {
            "crystallographic_packet_scout_built": True,
            "what_is_supported": "The five B6 crystallographic evidence packets are mapped against the current reproducibility and contract evidence.",
            "what_is_not_supported": "No reproducible crystallographic backend, cleaned source validation, denominator defeat, DFT observable, B5 observable, material discovery, mechanism solution, or superconductivity solution is established.",
            **forbidden_false,
        },
        "validation_error_count": len(validation_errors),
        "validation_errors": validation_errors,
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    lines = [
        "# B6 Crystallographic Packet Scout v0.1",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        f"- Method: `{payload['method']}`",
        f"- Model status: `{payload['model_status']}`",
        f"- Requirements passed/failed: {summary['packet_scout_requirements_passed']} / {summary['packet_scout_requirements_failed']}",
        f"- Failed requirement IDs: {', '.join(summary['failed_packet_scout_requirement_ids'])}",
        f"- Contract packets: {summary['contract_packet_count']}",
        f"- Records / families / negative controls: {summary['record_count']} / {summary['family_count']} / {summary['negative_control_count']}",
        f"- Post-split crystallographic AP / family-prior AP: {summary['post_split_crystallo_ap']} / {summary['post_split_family_prior_ap']}",
        f"- Source validation errors: {summary['source_validation_error_count']}",
        f"- Pymatgen/backend available: {summary['pymatgen_available']}",
        f"- DFT observable rows: {summary['dft_observable_rows']}",
        f"- B5-computed observable rows: {summary['b5_computed_observable_rows']}",
        "",
        "## Requirement Results",
        "",
    ]
    for item in payload["requirements"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {item['requirement_id']} [{marker}]: {item['label']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Supported: The B6 crystallographic packet surface is mapped to the current failed reproducibility and contract evidence.",
            "- Not supported: This is not material discovery, not a superconductivity mechanism, not a reproducible crystallographic descriptor, not DFT evidence, not B5 observable evidence, and not a solution claim.",
            "- Next gate: close S4-S8 by pinning a backend, clearing source validation, beating the family-prior denominator, and attaching DFT or B5-computed observables.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json-output", type=Path, default=Path("results/B6_crystallographic_packet_scout_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B6_crystallographic_packet_scout.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    payload = build_payload(root)
    write_json(root / args.json_output, payload, args.pretty)
    write_markdown(root / args.markdown_output, payload)
    print(payload["status"])
    print(
        payload["summary"]["packet_scout_requirements_passed"],
        payload["summary"]["packet_scout_requirements_failed"],
        payload["summary"]["failed_packet_scout_requirement_ids"],
    )


if __name__ == "__main__":
    main()
