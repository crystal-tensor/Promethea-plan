#!/usr/bin/env python3
"""Generate a customer-readable Q-Cert compiler audit report.

This MVP does not run the full compiler pipeline. It packages the current B1
evidence artifacts into a concise report that can be shown to collaborators,
pilot customers, or investors while preserving limitations.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"_missing": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}%"
    return "n/a"


def first(items: list[dict[str, Any]], key: str) -> Any:
    if not items:
        return None
    return items[0].get(key)


def build_report() -> dict[str, Any]:
    virtual = load_json(RESEARCH / "B1_virtual_swap_elimination_report.json")
    replay = load_json(RESEARCH / "B1_virtual_swap_replay_report.json")
    synthetic = load_json(RESEARCH / "B1_synthetic_noise_proxy_report.json")
    certificate = load_json(RESEARCH / "B1_certificate_report.json")
    bridge = load_json(ROOT / "results" / "B7_b1_b2_dependency_schedule_bridge_v0.json")
    gates = certificate.get("gates", {})
    exact_aggregate = certificate.get("exact_aggregate", {})

    twoq_reduction = (
        virtual.get("metrics", {})
        .get("two_qubit_gate_count", {})
        .get("reduction_pct")
    )
    exposure_reduction = (
        virtual.get("metrics", {})
        .get("hardware_weighted_error_exposure", {})
        .get("reduction_pct")
    )
    synthetic_source_vs_virtual = next(
        (
            row
            for row in synthetic.get("comparisons", [])
            if row.get("name") == "source_level1_routed_vs_virtual_swap"
        ),
        {},
    )

    return {
        "schema_version": "0.1",
        "generated_on": date.today().isoformat(),
        "product": "Q-Cert Compiler Audit CLI",
        "status": "mvp_report_not_live_device_claim",
        "headline": "Measurement-aware virtual-SWAP elimination produced replayable proof evidence on the current 30-circuit B1 suite.",
        "customer_value": [
            "Shows whether a routing/compiler change removes real two-qubit work or only shifts bookkeeping.",
            "Packages proof replay, Aer cross-checks, and limitation labels into one report.",
            "Creates a pilot-ready audit artifact before live calibrated hardware integration.",
        ],
        "b1_virtual_swap": {
            "report_status": virtual.get("report_status"),
            "rewritten_circuits": virtual.get("rewritten_circuits"),
            "skipped_circuits": virtual.get("skipped_circuits"),
            "virtual_swaps_removed": virtual.get("virtual_swaps_removed"),
            "removed_cx_gates": virtual.get("removed_cx_gates"),
            "two_qubit_reduction_pct": twoq_reduction,
            "exposure_reduction_pct": exposure_reduction,
            "local_aer_failures": virtual.get("local_aer_crosscheck", {}).get("failed"),
            "end_to_end_aer_failures": virtual.get("end_to_end_aer_crosscheck", {}).get("failed"),
            "top_circuit": first(virtual.get("top_circuits_by_virtual_swaps", []), "relative_path"),
        },
        "proof_replay": {
            "status": replay.get("report_status"),
            "proof_events": replay.get("proof_events"),
            "replayed_events": replay.get("replayed_events"),
            "output_mismatches": replay.get("output_mismatches"),
            "error_count": replay.get("error_count"),
        },
        "synthetic_noise_proxy": {
            "status": synthetic.get("report_status"),
            "profile": synthetic.get("profile_name"),
            "source_vs_virtual_exposure_reduction_pct": (
                synthetic_source_vs_virtual.get("metrics", {})
                .get("hardware_weighted_error_exposure", {})
                .get("reduction_pct")
            ),
            "source_vs_virtual_success_proxy_ratio": synthetic_source_vs_virtual.get(
                "aggregate_success_proxy_ratio"
            ),
        },
        "b7_bridge": {
            "status": bridge.get("status"),
            "comparison_count": bridge.get("comparison_count"),
            "min_space_time_volume_reduction": bridge.get("min_space_time_volume_reduction"),
            "mean_space_time_volume_reduction": bridge.get("mean_space_time_volume_reduction"),
        },
        "limitations": [
            "This is a topology/layout and synthetic-noise diagnostic, not a calibrated hardware claim.",
            "Dynamic-circuit semantics and native-basis local optimization are not yet complete.",
            "The current CLI packages existing artifacts; it does not yet run customer circuits end to end.",
        ],
        "next_customer_pilot_steps": [
            "Accept a customer QASM bundle and hardware profile.",
            "Run baseline transpilation, virtual-SWAP audit, proof replay, and Aer cross-check.",
            "Emit a signed JSON/HTML audit report with unsupported-claim warnings.",
        ],
        "certificate_gate_summary": {
            "status": certificate.get("report_status"),
            "exact_circuit_count": exact_aggregate.get("circuit_count"),
            "exact_equivalence_failed": exact_aggregate.get("equivalence_failed"),
            "proof_log_verification_passed": gates.get("proof_log_verification", {}).get("passed"),
            "global_equivalence_scope_passed": gates.get("global_equivalence_scope", {}).get("passed"),
            "calibrated_heavy_hex_baseline_passed": gates.get(
                "routing_aware_calibrated_heavy_hex_baseline", {}
            ).get(
                "passed"
            ),
            "unsupported_claim_count": len(certificate.get("claim_not_supported_yet", [])),
        },
    }


def markdown(report: dict[str, Any]) -> str:
    b1 = report["b1_virtual_swap"]
    replay = report["proof_replay"]
    synthetic = report["synthetic_noise_proxy"]
    bridge = report["b7_bridge"]
    gate = report["certificate_gate_summary"]

    lines = [
        "# Q-Cert Compiler Audit MVP Report",
        "",
        f"Generated on: {report['generated_on']}",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Headline: {report['headline']}",
        "",
        "## Customer Value",
        "",
    ]
    lines.extend(f"- {item}" for item in report["customer_value"])
    lines.extend(
        [
            "",
            "## B1 Virtual-SWAP Evidence",
            "",
            f"- Report status: {b1.get('report_status')}",
            f"- Rewritten circuits: {b1.get('rewritten_circuits')}",
            f"- Virtual SWAPs removed: {b1.get('virtual_swaps_removed')}",
            f"- Removed CX gates: {b1.get('removed_cx_gates')}",
            f"- Two-qubit reduction: {pct(b1.get('two_qubit_reduction_pct'))}",
            f"- Exposure reduction: {pct(b1.get('exposure_reduction_pct'))}",
            f"- Local Aer failures: {b1.get('local_aer_failures')}",
            f"- End-to-end Aer failures: {b1.get('end_to_end_aer_failures')}",
            f"- Top circuit: {b1.get('top_circuit')}",
            "",
            "## Proof Replay",
            "",
            f"- Status: {replay.get('status')}",
            f"- Events replayed: {replay.get('replayed_events')} / {replay.get('proof_events')}",
            f"- Output mismatches: {replay.get('output_mismatches')}",
            f"- Errors: {replay.get('error_count')}",
            "",
            "## Synthetic Noise Proxy",
            "",
            f"- Status: {synthetic.get('status')}",
            f"- Profile: {synthetic.get('profile')}",
            f"- Source routed vs virtual-SWAP exposure reduction: {pct(synthetic.get('source_vs_virtual_exposure_reduction_pct'))}",
            f"- Success proxy ratio: {synthetic.get('source_vs_virtual_success_proxy_ratio')}",
            "",
            "## B7 Resource Bridge Signal",
            "",
            f"- Status: {bridge.get('status')}",
            f"- Comparisons: {bridge.get('comparison_count')}",
            f"- Minimum STV reduction: {bridge.get('min_space_time_volume_reduction')}",
            f"- Mean STV reduction: {bridge.get('mean_space_time_volume_reduction')}",
            "",
            "## Certificate Gate Summary",
            "",
            f"- Status: {gate.get('status')}",
            f"- Exact circuit count: {gate.get('exact_circuit_count')}",
            f"- Exact equivalence failures: {gate.get('exact_equivalence_failed')}",
            f"- Proof-log verification passed: {gate.get('proof_log_verification_passed')}",
            f"- Global equivalence scope passed: {gate.get('global_equivalence_scope_passed')}",
            f"- Calibrated heavy-hex baseline passed: {gate.get('calibrated_heavy_hex_baseline_passed')}",
            f"- Unsupported claim count: {gate.get('unsupported_claim_count')}",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "## Next Customer Pilot Steps", ""])
    lines.extend(f"- {item}" for item in report["next_customer_pilot_steps"])
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", default="results/qcert_audit_mvp_report.json")
    parser.add_argument("--markdown-output", default="research/QCERT_MVP_REPORT.md")
    args = parser.parse_args()

    report = build_report()
    json_path = (ROOT / args.json_output).resolve()
    markdown_path = (ROOT / args.markdown_output).resolve()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"json_output": str(json_path), "markdown_output": str(markdown_path)}, indent=2))


if __name__ == "__main__":
    main()
