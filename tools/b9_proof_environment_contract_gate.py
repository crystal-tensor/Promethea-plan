#!/usr/bin/env python3
"""T-B9-004c: convert proof-environment blockers into PR-sized contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METHOD = "b9_proof_environment_contract_gate_v0"
STATUS = "proof_environment_contract_open_not_formal_theorem"
MODEL_STATUS = "proof_environment_readiness_blockers_decomposed_for_prs"
SOURCE_METHOD = "b9_proof_environment_readiness_gate_v0"
SOURCE_STATUS = "proof_environment_readiness_blocked_not_formal_theorem"
NAMED_FAMILY = "cluster_stabilizer_open_uniform_reweight"
EXPECTED_SOURCE_FAILED = ["PE-03", "PE-04", "PE-09"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def requirement(
    req_id: str,
    label: str,
    passed: bool,
    evidence: str,
    missing_to_promote: str,
) -> dict[str, Any]:
    return {
        "id": req_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
        "missing_to_promote": missing_to_promote,
    }


def packet(packet_id: str, source_gate: str, title: str, acceptance: list[str]) -> dict[str, Any]:
    return {
        "id": packet_id,
        "source_gate": source_gate,
        "title": title,
        "acceptance_criteria": acceptance,
        "claim_boundary": (
            "Packet evidence may improve B9 formal-readiness only after audit; it must not "
            "claim Quantum PCP, NLTS, local-Hamiltonian hardness, a formal theorem, or a "
            "global gap-amplification impossibility result until the proof environment and "
            "the theorem itself are independently checked."
        ),
    }


def build_contract(source_path: Path) -> dict[str, Any]:
    source = load_json(source_path)
    claim_boundary = source.get("claim_boundary", {})
    lean_file_probe = source.get("lean_file_probe", {})
    lake_project_probe = source.get("lake_project_probe", {})
    lean_probe = source.get("lean_probe", {})
    lake_probe = source.get("lake_probe", {})
    lean4_signature_detected = source.get("lean4_signature_detected") is True

    no_forbidden_claims = (
        claim_boundary.get("proof_environment_ready") is False
        and claim_boundary.get("proof_assistant_checked") is False
        and claim_boundary.get("formal_theorem_proved") is False
        and claim_boundary.get("explicit_not_quantum_pcp_proof") is True
        and claim_boundary.get("global_gap_amplification_impossibility_claimed") is False
        and claim_boundary.get("nlts_theorem_claimed") is False
    )

    source_failed = source.get("failed_gate_ids", [])
    requirements = [
        requirement(
            "K1",
            "source proof-environment gate is present and bounded",
            source.get("benchmark_id") == "B9"
            and source.get("method") == SOURCE_METHOD
            and source.get("status") == SOURCE_STATUS
            and source.get("named_family") == NAMED_FAMILY
            and source_failed == EXPECTED_SOURCE_FAILED,
            (
                f"benchmark_id={source.get('benchmark_id')}; method={source.get('method')}; "
                f"status={source.get('status')}; family={source.get('named_family')}; "
                f"failed={source_failed}"
            ),
            "Keep this contract tied to the failed B9 proof-environment readiness gate.",
        ),
        requirement(
            "K2",
            "local verifier evidence remains clean",
            source.get("validation_error_count") == 0
            and claim_boundary.get("local_verifier_checked") is True
            and source.get("passed_gate_count") == 6,
            (
                f"validation_error_count={source.get('validation_error_count')}; "
                f"local_verifier_checked={claim_boundary.get('local_verifier_checked')}; "
                f"passed_gate_count={source.get('passed_gate_count')}"
            ),
            "Preserve local exact-rational evidence as the non-formal denominator.",
        ),
        requirement(
            "K3",
            "forbidden theorem claims are absent",
            no_forbidden_claims,
            f"no_forbidden_claims={no_forbidden_claims}",
            "Keep B9 in theorem-readiness mode until independent proof checking passes.",
        ),
        requirement(
            "K4",
            "Lean 4 executable succeeds",
            lean_probe.get("available") is True
            and lean_probe.get("return_code") == 0
            and lean4_signature_detected,
            (
                f"lean_available={lean_probe.get('available')}; "
                f"lean_return_code={lean_probe.get('return_code')}; "
                f"lean4_signature_detected={lean4_signature_detected}"
            ),
            "Pin an actual Lean 4 executable that returns success for the project.",
        ),
        requirement(
            "K5",
            "Lake executable succeeds",
            lake_probe.get("available") is True and lake_probe.get("return_code") == 0,
            f"lake_available={lake_probe.get('available')}; lake_return_code={lake_probe.get('return_code')}",
            "Pin Lake and make it available to the proof project.",
        ),
        requirement(
            "K6",
            "Lake/mathlib project files are present",
            lake_project_probe.get("lake_project_present") is True,
            f"present_files={lake_project_probe.get('present_files')}",
            "Add lean-toolchain plus lakefile.lean or lakefile.toml with mathlib dependency.",
        ),
        requirement(
            "K7",
            "named-family theorem is not a placeholder",
            lean_file_probe.get("contains_placeholder_true_theorem") is False,
            (
                "contains_placeholder_true_theorem="
                f"{lean_file_probe.get('contains_placeholder_true_theorem')}"
            ),
            "Replace the True theorem with an indexed Hamiltonian-family statement.",
        ),
        requirement(
            "K8",
            "formal theorem is proof-assistant checked",
            source.get("proof_assistant_checked") is True
            and source.get("formal_theorem_proved") is True,
            (
                f"proof_assistant_checked={source.get('proof_assistant_checked')}; "
                f"formal_theorem_proved={source.get('formal_theorem_proved')}"
            ),
            "Record checked theorem output before upgrading the B9 claim.",
        ),
    ]
    all_packets = [
        packet(
            "B9-PE03-lean-toolchain",
            "PE-03",
            "Pin a successful Lean 4 executable",
            [
                "lean --version exits successfully and reports Lean 4",
                "toolchain version is recorded",
                "local verifier artifacts remain unchanged",
            ],
        ),
        packet(
            "B9-PE04-lake-tooling",
            "PE-04",
            "Pin Lake tooling",
            [
                "lake --version exits successfully",
                "Lake version is recorded",
                "the command runs from the repository root",
            ],
        ),
        packet(
            "B9-PE05-mathlib-project",
            "PE-05",
            "Create a Lean/Lake/mathlib project",
            [
                "lean-toolchain is present",
                "lakefile.lean or lakefile.toml is present",
                "mathlib dependency is declared or vendored reproducibly",
            ],
        ),
        packet(
            "B9-PE08-indexed-theorem",
            "PE-08",
            "Replace the placeholder True theorem",
            [
                "named-family theorem quantifies n >= 4",
                "Hamiltonian family, support, locality, width, and normalized gap are explicit",
                "no placeholder True theorem remains",
            ],
        ),
        packet(
            "B9-PE09-checked-formal-output",
            "PE-09",
            "Record proof-assistant checked theorem output",
            [
                "proof_assistant_checked is true",
                "formal_theorem_proved is true for the restricted theorem",
                "claim boundary still says this is not Quantum PCP or NLTS",
            ],
        ),
    ]
    packets = [row for row in all_packets if row["source_gate"] in source_failed]
    closed_packets = [row for row in all_packets if row["source_gate"] not in source_failed]
    failed = [row for row in requirements if not row["passed"]]
    return {
        "benchmark_id": "B9",
        "title": "B9 proof-environment contract gate",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "source_gate": str(source_path),
        "source_method": source.get("method"),
        "source_status": source.get("status"),
        "source_failed_gate_ids": source_failed,
        "named_family": source.get("named_family"),
        "readiness_gate_count": source.get("readiness_gate_count"),
        "source_passed_gate_count": source.get("passed_gate_count"),
        "source_failed_gate_count": source.get("failed_gate_count"),
        "blocking_obligation_count": source.get("blocking_obligation_count"),
        "lean_available": lean_probe.get("available"),
        "lean_return_code": lean_probe.get("return_code"),
        "lean4_signature_detected": lean4_signature_detected,
        "lake_available": lake_probe.get("available"),
        "lake_return_code": lake_probe.get("return_code"),
        "lake_project_present": lake_project_probe.get("lake_project_present"),
        "contains_placeholder_true_theorem": lean_file_probe.get(
            "contains_placeholder_true_theorem"
        ),
        "contract_requirement_count": len(requirements),
        "passed_contract_requirement_count": len(requirements) - len(failed),
        "failed_contract_requirement_count": len(failed),
        "failed_contract_requirement_ids": [row["id"] for row in failed],
        "contract_packet_count": len(packets),
        "contract_packet_ids": [row["id"] for row in packets],
        "closed_contract_packet_count": len(closed_packets),
        "closed_contract_packet_ids": [row["id"] for row in closed_packets],
        "requirements": requirements,
        "contract_packets": packets,
        "claim_boundary": {
            "proof_environment_contract_built": True,
            "local_verifier_checked": claim_boundary.get("local_verifier_checked") is True,
            "proof_environment_ready": False,
            "independent_proof_check_ready": False,
            "proof_assistant_checked": False,
            "formal_theorem_proved": False,
            "explicit_not_quantum_pcp_proof": True,
            "global_gap_amplification_impossibility_claimed": False,
            "nlts_theorem_claimed": False,
        },
        "validation_errors": [],
        "validation_error_count": 0,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# B9 Proof-Environment Contract Gate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "## Summary",
        "",
        (
            "T-B9-004c converts the blocked proof-environment readiness gate into "
            "five PR-sized proof packets. This is a handoff contract, not a formal "
            "theorem, Quantum PCP proof, NLTS proof, or global gap-amplification "
            "impossibility claim."
        ),
        "",
        "## Contract Metrics",
        "",
        f"- Named family: `{payload['named_family']}`",
        f"- Source failed gates: {', '.join(payload['source_failed_gate_ids'])}",
        (
            f"- Source readiness passed / failed: {payload['source_passed_gate_count']} / "
            f"{payload['source_failed_gate_count']}"
        ),
        (
            f"- Lean / Lake / project / placeholder: {payload['lean_return_code']} / "
            f"{payload['lake_available']} / {payload['lake_project_present']} / "
            f"{payload['contains_placeholder_true_theorem']}"
        ),
        (
            f"- Contract requirements passed / failed: "
            f"{payload['passed_contract_requirement_count']} / "
            f"{payload['failed_contract_requirement_count']}"
        ),
        f"- Contract packets: {payload['contract_packet_count']}",
        "",
        "## Requirements",
        "",
        "| ID | Pass | Requirement | Evidence | Missing to promote |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["requirements"]:
        passed = "yes" if row["passed"] else "no"
        lines.append(
            f"| {row['id']} | {passed} | {row['label']} | {row['evidence']} | {row['missing_to_promote']} |"
        )
    lines.extend(["", "## PR Packets", ""])
    for row in payload["contract_packets"]:
        lines.append(f"### {row['id']}")
        lines.append("")
        lines.append(f"- Source gate: {row['source_gate']}")
        lines.append(f"- Title: {row['title']}")
        for criterion in row["acceptance_criteria"]:
            lines.append(f"- Acceptance: {criterion}")
        lines.append(f"- Claim boundary: {row['claim_boundary']}")
        lines.append("")
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "- No formal theorem is claimed.",
            "- No Quantum PCP or NLTS theorem is claimed.",
            "- No global gap-amplification impossibility theorem is claimed.",
            "- The local verifier remains useful evidence, but it is not a proof assistant.",
            "- The B9 route remains a restricted negative-result track until the contract packets close.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("results/B9_proof_environment_readiness_gate_v0.json"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/B9_proof_environment_contract_gate_v0.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("research/B9_proof_environment_contract_gate.md"),
    )
    args = parser.parse_args()
    payload = build_contract(args.source)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload, args.markdown_output)


if __name__ == "__main__":
    main()
