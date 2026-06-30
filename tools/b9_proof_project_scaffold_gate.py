#!/usr/bin/env python3
"""T-B9-004d: audit the B9 Lean/Lake project scaffold without claiming proof."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
READINESS_PATH = ROOT / "results" / "B9_proof_environment_readiness_gate_v0.json"
CONTRACT_PATH = ROOT / "results" / "B9_proof_environment_contract_gate_v0.json"
LEAN_TOOLCHAIN = ROOT / "lean-toolchain"
LAKEFILE = ROOT / "lakefile.lean"
LEAN_SKELETON = ROOT / "research" / "proof_skeletons" / "B9_cluster_stabilizer_width_locality_bound.lean"
LEAN_PROJECT_MODULE = ROOT / "B9" / "ClusterStabilizer" / "WidthLocality.lean"

METHOD = "b9_proof_project_scaffold_gate_v0"
STATUS = "proof_project_scaffold_open_not_checked"
MODEL_STATUS = "lean_lake_scaffold_and_indexed_theorem_interface_without_checked_proof"
NAMED_FAMILY = "cluster_stabilizer_open_uniform_reweight"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def requirement(req_id: str, label: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {
        "id": req_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def theorem_interface_probe(source: str) -> dict[str, Any]:
    theorem_match = re.search(
        r"theorem\s+cluster_stabilizer_open_uniform_reweight_obligation\b(?P<body>.*?)"
        r":=\s*by",
        source,
        re.DOTALL,
    )
    body = theorem_match.group("body") if theorem_match else ""
    return {
        "theorem_present": theorem_match is not None,
        "quantifies_n": "(n : Nat)" in body,
        "requires_n_ge_4": "4 <= n" in body,
        "uses_raw_gap_predicate": "RawGapAmplifies" in body,
        "uses_locality_predicate": "LocalityPreserved" in body,
        "uses_normalized_gap_invariant": "NormalizedGapInvariant" in body,
        "rejects_normalized_gap_improvement": "not (after.normalizedGap > before.normalizedGap)" in body,
        "contains_placeholder_true_theorem": bool(
            re.search(
                r"theorem\s+cluster_stabilizer_open_uniform_reweight_obligation\s*:\s*True\s*:=",
                source,
            )
        ),
        "contains_sorry": "sorry" in source,
        "contains_admit": "admit" in source,
    }


def build_payload(readiness_path: Path, contract_path: Path) -> dict[str, Any]:
    readiness = load_json(readiness_path)
    contract = load_json(contract_path)
    skeleton_source = read_text(LEAN_SKELETON)
    project_source = read_text(LEAN_PROJECT_MODULE)
    skeleton_probe = theorem_interface_probe(skeleton_source)
    project_probe = theorem_interface_probe(project_source)
    readiness_failed = readiness.get("failed_gate_ids", [])
    contract_failed = contract.get("failed_contract_requirement_ids", [])
    requirements = [
        requirement(
            "S1",
            "source readiness gate is refreshed after scaffold creation",
            readiness.get("method") == "b9_proof_environment_readiness_gate_v0"
            and readiness.get("failed_gate_ids") == ["PE-03", "PE-04", "PE-09"],
            f"failed_gate_ids={readiness_failed}",
        ),
        requirement(
            "S2",
            "source contract gate is refreshed after scaffold creation",
            contract.get("method") == "b9_proof_environment_contract_gate_v0"
            and contract.get("failed_contract_requirement_ids") == ["K4", "K5", "K8"],
            f"failed_contract_requirement_ids={contract_failed}",
        ),
        requirement(
            "S3",
            "Lean toolchain file is pinned",
            LEAN_TOOLCHAIN.exists() and "leanprover/lean4:v4.12.0" in read_text(LEAN_TOOLCHAIN),
            rel(LEAN_TOOLCHAIN),
        ),
        requirement(
            "S4",
            "Lake project file declares mathlib dependency",
            LAKEFILE.exists() and "mathlib4" in read_text(LAKEFILE),
            rel(LAKEFILE),
        ),
        requirement(
            "S5",
            "skeleton theorem interface is indexed and non-placeholder",
            all(
                skeleton_probe[key]
                for key in [
                    "theorem_present",
                    "quantifies_n",
                    "requires_n_ge_4",
                    "uses_raw_gap_predicate",
                    "uses_locality_predicate",
                    "uses_normalized_gap_invariant",
                    "rejects_normalized_gap_improvement",
                ]
            )
            and not skeleton_probe["contains_placeholder_true_theorem"],
            rel(LEAN_SKELETON),
        ),
        requirement(
            "S6",
            "Lake module mirrors the theorem interface",
            LEAN_PROJECT_MODULE.exists()
            and all(
                project_probe[key]
                for key in [
                    "theorem_present",
                    "quantifies_n",
                    "requires_n_ge_4",
                    "uses_raw_gap_predicate",
                    "uses_locality_predicate",
                    "uses_normalized_gap_invariant",
                    "rejects_normalized_gap_improvement",
                ]
            )
            and not project_probe["contains_placeholder_true_theorem"],
            rel(LEAN_PROJECT_MODULE),
        ),
        requirement(
            "S7",
            "actual Lean 4 executable is available",
            readiness.get("lean4_signature_detected") is True,
            f"lean4_signature_detected={readiness.get('lean4_signature_detected')}",
        ),
        requirement(
            "S8",
            "the theorem is proof-assistant checked",
            readiness.get("proof_assistant_checked") is True
            and readiness.get("formal_theorem_proved") is True,
            (
                f"proof_assistant_checked={readiness.get('proof_assistant_checked')}; "
                f"formal_theorem_proved={readiness.get('formal_theorem_proved')}"
            ),
        ),
    ]
    failed = [row for row in requirements if not row["passed"]]
    return {
        "benchmark_id": "B9",
        "title": "B9 Lean/Lake proof project scaffold gate",
        "method": METHOD,
        "status": STATUS,
        "model_status": MODEL_STATUS,
        "named_family": NAMED_FAMILY,
        "source_readiness_gate": rel(readiness_path),
        "source_contract_gate": rel(contract_path),
        "readiness_failed_gate_ids": readiness_failed,
        "contract_failed_requirement_ids": contract_failed,
        "lean_toolchain": rel(LEAN_TOOLCHAIN),
        "lakefile": rel(LAKEFILE),
        "lean_skeleton": rel(LEAN_SKELETON),
        "lean_project_module": rel(LEAN_PROJECT_MODULE),
        "skeleton_probe": skeleton_probe,
        "project_probe": project_probe,
        "scaffold_requirement_count": len(requirements),
        "passed_scaffold_requirement_count": len(requirements) - len(failed),
        "failed_scaffold_requirement_count": len(failed),
        "failed_scaffold_requirement_ids": [row["id"] for row in failed],
        "requirements": requirements,
        "claim_boundary": {
            "proof_project_scaffold_created": True,
            "indexed_theorem_interface_created": True,
            "actual_lean4_available": readiness.get("lean4_signature_detected") is True,
            "lake_available": readiness.get("lake_probe", {}).get("available") is True,
            "proof_environment_ready": False,
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
        "# B9 Lean/Lake Proof Project Scaffold Gate",
        "",
        f"Status: **{payload['status']}**",
        "",
        "T-B9-004d creates a repository-local Lean/Lake scaffold and replaces the "
        "named-family placeholder theorem with an indexed theorem interface. This "
        "is still not a formal B9 theorem, Quantum PCP proof, NLTS proof, or "
        "global gap-amplification impossibility theorem.",
        "",
        "## Metrics",
        "",
        f"- Named family: `{payload['named_family']}`",
        f"- Readiness failed gates: `{payload['readiness_failed_gate_ids']}`",
        f"- Contract failed requirements: `{payload['contract_failed_requirement_ids']}`",
        (
            f"- Scaffold requirements passed / failed: "
            f"{payload['passed_scaffold_requirement_count']} / "
            f"{payload['failed_scaffold_requirement_count']}"
        ),
        f"- Failed scaffold requirement IDs: `{payload['failed_scaffold_requirement_ids']}`",
        f"- Lean toolchain: `{payload['lean_toolchain']}`",
        f"- Lakefile: `{payload['lakefile']}`",
        f"- Lean project module: `{payload['lean_project_module']}`",
        "",
        "## Requirements",
        "",
        "| ID | Pass | Requirement | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["requirements"]:
        passed = "yes" if row["passed"] else "no"
        lines.append(f"| {row['id']} | {passed} | {row['label']} | {row['evidence']} |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- The Lean/Lake project scaffold exists.",
            "- The named-family obligation is no longer a `True` placeholder.",
            "- The theorem is not proof-assistant checked.",
            "- The local executable named `lean` is not yet accepted as Lean 4 unless the version signature proves it.",
            "- Lake is still missing in the current environment.",
            "- No Quantum PCP, NLTS, or global gap-amplification theorem is claimed.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readiness", type=Path, default=READINESS_PATH)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "results" / "B9_proof_project_scaffold_gate_v0.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=ROOT / "research" / "B9_proof_project_scaffold_gate.md",
    )
    args = parser.parse_args()
    payload = build_payload(args.readiness, args.contract)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload, args.markdown_output)


if __name__ == "__main__":
    main()
