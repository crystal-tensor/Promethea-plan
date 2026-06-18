#!/usr/bin/env python3
"""Build formal theorem-target cards for the B10 BQP-boundary program."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TARGETS = [
    {
        "id": "B10-T1",
        "name": "linear_systems_data_loading_negative_boundary",
        "source_graph_target": "phase_estimation_observables__to__linear_systems_hhl_negative_boundary",
        "target_type": "negative_boundary",
        "informal_claim": (
            "An HHL-style exponential speedup claim collapses to at most a polynomial or "
            "undefined advantage when state preparation, block encoding, condition-number "
            "control, and output readout are charged explicitly."
        ),
        "input_model": {
            "instance": "Sparse or block-encoded linear system Ax=b with n-dimensional solution vector x.",
            "access": [
                "Classical sparse-row oracle or explicit sparse matrix description for A.",
                "State-preparation procedure P_b for |b> with declared cost C_prep.",
                "Block-encoding or Hamiltonian simulation oracle U_A with declared cost C_block.",
                "Observable family O_1..O_m whose expectation values on |x> are the requested outputs.",
            ],
            "cost_accounting": [
                "C_prep is included in the quantum runtime.",
                "C_block is included per query or simulation segment.",
                "Condition number kappa and target precision epsilon are explicit parameters.",
                "Readout cost scales with the number and precision of requested observables.",
            ],
        },
        "promise": [
            "A is Hermitian or embedded into a Hermitian block matrix with spectral norm <= 1.",
            "Nonzero singular values of A are in [1/kappa, 1].",
            "P_b prepares a state within trace distance eta_prep of |b>.",
            "Each requested observable has operator norm <= 1.",
            "The output is not the full vector x unless full readout cost is paid.",
        ],
        "output_model": {
            "accepted_output": "Estimates of m observable expectations <x|O_j|x> within additive error epsilon.",
            "rejected_output": "A claim of full-vector recovery without O(n) or equivalent readout cost.",
            "success_probability": "At least 2/3, boostable by standard repetition or amplitude-estimation schedules.",
        },
        "verifier_model": {
            "classical_verifier_inputs": [
                "Classical description of A or sparse-row oracle access.",
                "Classical descriptions of O_j.",
                "Declared costs C_prep, C_block, kappa, epsilon, eta_prep, m.",
            ],
            "checks": [
                "Reject if C_prep or C_block is hidden inside an oracle and not charged.",
                "Reject if kappa or 1/epsilon grows fast enough to erase the claimed speedup.",
                "Reject if m or requested output dimension implies full readout.",
                "Compare against classical iterative or sampling baselines at the same observable precision.",
            ],
        },
        "failure_modes_controlled": ["data_loading", "condition_number", "readout", "dequantization"],
        "dependencies": ["B3", "B5", "B10"],
        "proof_obligations": [
            "State a theorem bounding end-to-end quantum runtime in terms of C_prep, C_block, kappa, epsilon, and m.",
            "State a negative corollary showing that if C_prep + C_block + readout is Omega(n) or worse, exponential speedup cannot be claimed for full-output tasks.",
            "List classical baselines and denominator metrics before any advantage claim.",
        ],
        "current_status": "formal_model_ready_not_proved",
    },
    {
        "id": "B10-T2",
        "name": "sampling_advantage_verification_layer_target",
        "source_graph_target": "random_circuit_sampling__to__interactive_verification",
        "target_type": "restricted_advantage_preservation",
        "informal_claim": (
            "A sampling-advantage task can retain a restricted advantage claim after adding a "
            "classical verification layer only if the verifier's challenge refresh and leakage "
            "budget keep adaptive spoofing soundness below an explicit threshold."
        ),
        "input_model": {
            "instance": "Distribution-sampling circuit family C_n plus hidden verifier challenges generated after or independently of the prover's sampling strategy.",
            "access": [
                "Classical circuit descriptions for C_n.",
                "Verifier challenge generator G_chal with public parameters and hidden seed.",
                "A leakage channel L exposing a bounded fraction lambda of hidden challenge information.",
                "A finite adversary class A or a formally specified adaptive spoofing model.",
            ],
            "cost_accounting": [
                "Verifier runtime and sample count are included.",
                "Challenge refresh/projection rotation overhead is included.",
                "Soundness is reported against the declared leakage fraction lambda.",
            ],
        },
        "promise": [
            "Honest quantum samples pass the verifier with completeness at least c.",
            "Adaptive classical spoofers receive at most lambda leakage about hidden challenges.",
            "The verifier uses refresh or projection rotation so repeated transcripts do not reveal a fixed invariant too quickly.",
            "The task's sampling hardness assumption is stated separately from the verifier's property test.",
        ],
        "output_model": {
            "accepted_output": "A transcript, pass/fail decision, empirical completeness, and empirical or proven soundness bound.",
            "rejected_output": "A sampling-advantage claim based only on an easily inferred invariant or unrefreshed trap.",
            "success_probability": "Completeness >= c and adaptive-spoofer soundness <= s for declared lambda.",
        },
        "verifier_model": {
            "classical_verifier_inputs": [
                "Circuit family C_n.",
                "Challenge generator G_chal.",
                "Leakage budget lambda.",
                "Completeness threshold c and soundness threshold s.",
                "Adversary family or reduction assumptions.",
            ],
            "checks": [
                "Reject if no leakage budget is declared.",
                "Reject if the verifier's hidden invariant is fixed across too many trials.",
                "Require a challenge-refresh or projection-rotation schedule.",
                "Report empirical stress-test curves from B8 before using the target in B4.",
            ],
        },
        "failure_modes_controlled": ["verification", "protocol_overhead", "noise", "adaptive_leakage"],
        "dependencies": ["B4", "B8", "B10"],
        "proof_obligations": [
            "Define a theorem relating leakage fraction lambda, refresh schedule, sample count, and soundness s.",
            "Prove or empirically bound the adaptive-spoofer pass probability for the declared adversary class.",
            "Separate sampling hardness assumptions from verifier soundness assumptions.",
        ],
        "current_status": "formal_model_ready_not_proved",
    },
]


def validate_targets(targets: list[dict]) -> list[str]:
    errors: list[str] = []
    required = [
        "id",
        "name",
        "source_graph_target",
        "target_type",
        "informal_claim",
        "input_model",
        "promise",
        "output_model",
        "verifier_model",
        "failure_modes_controlled",
        "dependencies",
        "proof_obligations",
        "current_status",
    ]
    for target in targets:
        missing = [field for field in required if target.get(field) in (None, "", [], {})]
        if missing:
            errors.append(f"{target.get('id', '<unknown>')} missing fields: {missing}")
        if target.get("current_status") != "formal_model_ready_not_proved":
            errors.append(f"{target.get('id', '<unknown>')} must not claim a theorem proof")
        if len(target.get("proof_obligations", [])) < 3:
            errors.append(f"{target.get('id', '<unknown>')} should have at least three proof obligations")
        if len(target.get("promise", [])) < 3:
            errors.append(f"{target.get('id', '<unknown>')} should have at least three promise clauses")
    return errors


def build_report() -> dict:
    validation_errors = validate_targets(TARGETS)
    target_types = sorted({target["target_type"] for target in TARGETS})
    dependency_ids = sorted({dep for target in TARGETS for dep in target["dependencies"]})
    return {
        "benchmark_id": "B10",
        "problem_id": 11,
        "title": "B10 formal theorem target cards",
        "version": "0.1",
        "last_updated": "2026-06-13",
        "status": "formal_theorem_targets_not_proofs",
        "method": "bqp_boundary_formal_theorem_targets_v0",
        "source_result": "B10_bqp_boundary_graph_v0",
        "target_count": len(TARGETS),
        "target_types": target_types,
        "dependency_ids": dependency_ids,
        "validation_errors": validation_errors,
        "targets": TARGETS,
        "limits": [
            "These are theorem-target specifications, not proved theorems.",
            "Each target is designed to prevent overclaiming by making input, promise, output, verifier, and cost assumptions explicit.",
            "The next step is to prove at least one restricted theorem or negative lemma, or to record a failed proof attempt as a B9/B10 guardrail.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# B10 Formal Theorem Targets v0.1",
        "",
        "Last updated: 2026-06-13",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Summary",
        "",
        f"- Source result: {report['source_result']}",
        f"- Method: {report['method']}",
        f"- Target count: {report['target_count']}",
        f"- Target types: {report['target_types']}",
        f"- Cross-B dependencies: {report['dependency_ids']}",
        f"- Validation errors: {len(report['validation_errors'])}",
        "",
    ]
    for target in report["targets"]:
        lines.extend(
            [
                f"## {target['id']}: {target['name']}",
                "",
                f"- Type: {target['target_type']}",
                f"- Source graph target: `{target['source_graph_target']}`",
                f"- Status: {target['current_status']}",
                f"- Informal claim: {target['informal_claim']}",
                f"- Dependencies: {target['dependencies']}",
                f"- Failure modes controlled: {target['failure_modes_controlled']}",
                "",
                "### Input Model",
                "",
                f"- Instance: {target['input_model']['instance']}",
            ]
        )
        lines.extend(f"- Access: {item}" for item in target["input_model"]["access"])
        lines.extend(f"- Cost accounting: {item}" for item in target["input_model"]["cost_accounting"])
        lines.extend(["", "### Promise", ""])
        lines.extend(f"- {item}" for item in target["promise"])
        lines.extend(["", "### Output Model", ""])
        for key, value in target["output_model"].items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "### Verifier Model", ""])
        lines.extend(f"- Input: {item}" for item in target["verifier_model"]["classical_verifier_inputs"])
        lines.extend(f"- Check: {item}" for item in target["verifier_model"]["checks"])
        lines.extend(["", "### Proof Obligations", ""])
        lines.extend(f"- {item}" for item in target["proof_obligations"])
        lines.append("")
    lines.extend(["## Limits", ""])
    lines.extend(f"- {item}" for item in report["limits"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=Path("results/B10_formal_theorem_targets_v0.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("research/B10_formal_theorem_targets.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report()
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    if args.pretty:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "target_count": report["target_count"],
                    "target_types": report["target_types"],
                    "dependency_ids": report["dependency_ids"],
                    "validation_error_count": len(report["validation_errors"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
