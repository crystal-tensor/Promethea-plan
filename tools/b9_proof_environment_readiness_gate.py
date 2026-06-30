#!/usr/bin/env python3
"""Audit B9 proof-environment readiness for the cluster-stabilizer family.

This gate does not try to prove Quantum PCP. It converts the current B9
formalization gap into a machine-readable checklist: what is already covered
by the local exact-rational verifier, what can be checked by the local Lean
tooling, and what remains blocking before a proof-assistant theorem can be
claimed.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "results" / "B9_cluster_stabilizer_parametric_certificate_v0.json"
LEAN_PATH = ROOT / "research" / "proof_skeletons" / "B9_cluster_stabilizer_width_locality_bound.lean"
JSON_OUT = ROOT / "results" / "B9_proof_environment_readiness_gate_v0.json"
MD_OUT = ROOT / "research" / "B9_proof_environment_readiness_gate.md"

METHOD = "b9_proof_environment_readiness_gate_v0"
STATUS = "proof_environment_readiness_blocked_not_formal_theorem"
MODEL_STATUS = "tooling_and_theorem_obligation_gate_not_quantum_pcp_proof"
NAMED_FAMILY = "cluster_stabilizer_open_uniform_reweight"


def has_lean4_signature(probe: dict[str, Any]) -> bool:
    output = f"{probe.get('stdout', '')}\n{probe.get('stderr', '')}"
    return bool(re.search(r"\bLean\b.*\b4\.", output, re.IGNORECASE))


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def command_probe(command: str, args: list[str]) -> dict[str, Any]:
    executable = shutil.which(command)
    if not executable:
        return {
            "command": command,
            "available": False,
            "executable": None,
            "return_code": None,
            "stdout": "",
            "stderr": "",
            "detail": f"{command} executable not found on PATH",
        }
    try:
        completed = subprocess.run(
            [executable, *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as exc:  # pragma: no cover - environment dependent.
        return {
            "command": command,
            "available": True,
            "executable": executable,
            "return_code": None,
            "stdout": "",
            "stderr": "",
            "detail": f"{command} probe exception: {exc}",
        }
    return {
        "command": command,
        "available": True,
        "executable": executable,
        "return_code": completed.returncode,
        "stdout": completed.stdout.strip()[:2000],
        "stderr": completed.stderr.strip()[:2000],
        "detail": "ok" if completed.returncode == 0 else f"{command} exited with {completed.returncode}",
    }


def lean_file_probe(path: Path) -> dict[str, Any]:
    exists = path.exists()
    source = path.read_text(encoding="utf-8") if exists else ""
    placeholder_pattern = re.compile(
        r"theorem\s+cluster_stabilizer_open_uniform_reweight_obligation\s*:\s*True\s*:=",
        re.MULTILINE,
    )
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": exists,
        "imports_mathlib": "import Mathlib" in source,
        "contains_sorry": "sorry" in source,
        "contains_admit": "admit" in source,
        "contains_placeholder_true_theorem": bool(placeholder_pattern.search(source)),
        "line_count": len(source.splitlines()) if exists else 0,
    }


def lake_project_probe() -> dict[str, Any]:
    project_files = [
        ROOT / "lakefile.lean",
        ROOT / "lakefile.toml",
        ROOT / "lean-toolchain",
    ]
    present = [str(path.relative_to(ROOT)) for path in project_files if path.exists()]
    return {
        "required_files": [str(path.relative_to(ROOT)) for path in project_files],
        "present_files": present,
        "lake_project_present": bool(present)
        and any((ROOT / name).exists() for name in ["lakefile.lean", "lakefile.toml"])
        and (ROOT / "lean-toolchain").exists(),
    }


def build_gate() -> dict[str, Any]:
    source = load_json(SOURCE_PATH)
    lean_probe = command_probe("lean", ["--version"])
    lake_probe = command_probe("lake", ["--version"])
    lean_file = lean_file_probe(LEAN_PATH)
    project = lake_project_probe()
    lean4_signature_detected = has_lean4_signature(lean_probe)

    validation_errors: list[str] = []
    if source.get("method") != "b9_cluster_stabilizer_parametric_certificate_v0":
        validation_errors.append("unexpected_source_method")
    if source.get("named_family") != NAMED_FAMILY:
        validation_errors.append("unexpected_named_family")
    if source.get("validation_error_count") != 0:
        validation_errors.append("source_parametric_certificate_has_validation_errors")
    if source.get("claim_boundary", {}).get("local_verifier_checked") is not True:
        validation_errors.append("source_local_verifier_not_checked")
    if not lean_file["exists"]:
        validation_errors.append("lean_skeleton_missing")

    readiness_gates = [
        {
            "id": "PE-01",
            "name": "local parametric certificate exists",
            "passed": SOURCE_PATH.exists(),
            "evidence": str(SOURCE_PATH.relative_to(ROOT)),
        },
        {
            "id": "PE-02",
            "name": "local exact-rational verifier passed",
            "passed": source.get("claim_boundary", {}).get("local_verifier_checked") is True
            and source.get("validation_error_count") == 0,
            "evidence": "source validation_error_count == 0",
        },
        {
            "id": "PE-03",
            "name": "Lean 4 executable available",
            "passed": lean_probe["available"]
            and lean_probe["return_code"] == 0
            and lean4_signature_detected,
            "evidence": (
                f"{lean_probe['detail']}; lean4_signature_detected="
                f"{lean4_signature_detected}"
            ),
        },
        {
            "id": "PE-04",
            "name": "Lake executable available",
            "passed": lake_probe["available"] and lake_probe["return_code"] == 0,
            "evidence": lake_probe["detail"],
        },
        {
            "id": "PE-05",
            "name": "Lean/mathlib project files present",
            "passed": project["lake_project_present"],
            "evidence": f"present files: {project['present_files']}",
        },
        {
            "id": "PE-06",
            "name": "Lean skeleton imports Mathlib",
            "passed": lean_file["exists"] and lean_file["imports_mathlib"],
            "evidence": lean_file["path"],
        },
        {
            "id": "PE-07",
            "name": "Lean skeleton has no sorry/admit token",
            "passed": lean_file["exists"] and not lean_file["contains_sorry"] and not lean_file["contains_admit"],
            "evidence": lean_file["path"],
        },
        {
            "id": "PE-08",
            "name": "Named-family theorem is not a placeholder",
            "passed": lean_file["exists"] and not lean_file["contains_placeholder_true_theorem"],
            "evidence": "cluster_stabilizer_open_uniform_reweight_obligation must not prove only True",
        },
        {
            "id": "PE-09",
            "name": "Source theorem is proof-assistant checked",
            "passed": source.get("proof_assistant_checked") is True
            and source.get("formal_theorem_proved") is True,
            "evidence": "source proof_assistant_checked/formal_theorem_proved flags",
        },
    ]

    passed_gate_count = sum(1 for gate in readiness_gates if gate["passed"])
    failed_gates = [gate for gate in readiness_gates if not gate["passed"]]
    blocking_obligations = [
        "pin an actual Lean 4 executable and make it shadow unrelated lean CLIs",
        "pin Lake tooling for the scaffolded Lean project",
        "make the cluster-stabilizer skeleton check inside that project",
        "formalize support-size, uniform-scaling, spectral-width, and normalized-gap invariance for all n >= 4",
        "record proof-assistant checked theorem output before upgrading any B9 claim",
    ]

    proof_environment_ready = len(failed_gates) == 0 and not validation_errors
    claim_boundary = {
        "local_verifier_checked": source.get("claim_boundary", {}).get("local_verifier_checked") is True,
        "proof_environment_ready": proof_environment_ready,
        "proof_assistant_checked": False,
        "formal_theorem_proved": False,
        "explicit_not_quantum_pcp_proof": True,
        "global_gap_amplification_impossibility_claimed": False,
        "nlts_theorem_claimed": False,
    }

    return {
        "benchmark_id": "B9",
        "method": METHOD,
        "status": STATUS if not proof_environment_ready else "proof_environment_ready_no_quantum_pcp_claim",
        "model_status": MODEL_STATUS,
        "source_result": str(SOURCE_PATH.relative_to(ROOT)),
        "source_method": source.get("method"),
        "named_family": NAMED_FAMILY,
        "lean_probe": lean_probe,
        "lean4_signature_detected": lean4_signature_detected,
        "lake_probe": lake_probe,
        "lake_project_probe": project,
        "lean_file_probe": lean_file,
        "readiness_gates": readiness_gates,
        "readiness_gate_count": len(readiness_gates),
        "passed_gate_count": passed_gate_count,
        "failed_gate_count": len(failed_gates),
        "failed_gate_ids": [gate["id"] for gate in failed_gates],
        "blocking_obligations": blocking_obligations,
        "blocking_obligation_count": len(blocking_obligations),
        "proof_environment_ready": proof_environment_ready,
        "independent_proof_check_ready": proof_environment_ready,
        "claim_boundary": claim_boundary,
        "proof_assistant_checked": False,
        "formal_theorem_proved": False,
        "explicit_not_quantum_pcp_proof": True,
        "global_gap_amplification_impossibility_claimed": False,
        "validation_errors": validation_errors,
        "validation_error_count": len(validation_errors),
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# B9 Proof-Environment Readiness Gate",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This artifact audits the current proof-checking path for the B9 "
        "cluster-stabilizer negative certificate. It does not claim a formal "
        "theorem. It records that the local exact-rational verifier is useful "
        "but still insufficient for a Lean/mathlib or equivalent theorem.",
        "",
        "## Summary",
        "",
        f"- Named family: `{payload['named_family']}`",
        f"- Readiness gates passed: `{payload['passed_gate_count']}` / `{payload['readiness_gate_count']}`",
        f"- Failed gate IDs: `{payload['failed_gate_ids']}`",
        f"- Blocking obligations: `{payload['blocking_obligation_count']}`",
        f"- Proof environment ready: `{payload['proof_environment_ready']}`",
        f"- Proof assistant checked: `{payload['proof_assistant_checked']}`",
        f"- Formal theorem proved: `{payload['formal_theorem_proved']}`",
        f"- Explicitly not Quantum PCP proof: `{payload['explicit_not_quantum_pcp_proof']}`",
        "",
        "## Readiness Gates",
        "",
        "| Gate | Passed | Evidence |",
        "|---|---:|---|",
    ]
    for gate in payload["readiness_gates"]:
        lines.append(f"| {gate['id']} {gate['name']} | {gate['passed']} | {gate['evidence']} |")
    lines.extend(
        [
            "",
            "## Blocking Obligations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["blocking_obligations"])
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- The local verifier can remain as executable evidence for formula-level checks.",
            "- The B9 result must remain a negative guardrail until an independent proof-checking environment passes.",
            "- This artifact does not prove Quantum PCP, NLTS, local-Hamiltonian hardness, or a global gap-amplification no-go theorem.",
            "",
            f"Validation error count: `{payload['validation_error_count']}`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=JSON_OUT)
    parser.add_argument("--markdown-output", type=Path, default=MD_OUT)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    payload = build_gate()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload, args.markdown_output)
    if args.pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Wrote {args.json_output}")
        print(f"Wrote {args.markdown_output}")


if __name__ == "__main__":
    main()
