#!/usr/bin/env python3
"""Run the current best B1 compression pipeline to a fixed point."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.stdout


def qasm_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix == ".qasm":
        return [path]
    return sorted(path.rglob("*.qasm"))


def copy_qasm_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)
    if src.is_file():
        shutil.copy2(src, dst / src.name)
        return
    for file in qasm_files(src):
        target = dst / file.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)


def total_operation_count(metrics_path: Path) -> float:
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    return sum(float(row["operation_count"]) for row in payload["results"])


def parse_key_value_totals(stdout: str, keys: set[str]) -> dict[str, int]:
    totals = {key: 0 for key in keys}
    for line in stdout.splitlines():
        for token in line.split():
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            if key in totals:
                totals[key] += int(value)
    return totals


def parse_oneq_certificate(stdout: str) -> dict:
    totals = parse_key_value_totals(
        stdout,
        {
            "runs",
            "identity_gates",
            "removed_1q",
            "commuted_disjoint",
        },
    )
    return {
        "rule": "maximal_single_qubit_gate_run -> one u3(theta,phi,lambda)",
        "certificate_type": "constructive_1q_unitary_matrix_decomposition",
        "resynthesized_runs": totals["runs"],
        "identity_gates_removed": totals["identity_gates"],
        "removed_single_qubit_gates": totals["removed_1q"],
        "commuted_disjoint_single_qubit_gates": totals["commuted_disjoint"],
    }


def parse_rzz_certificate(stdout: str) -> dict:
    totals = parse_key_value_totals(
        stdout,
        {
            "windows",
            "commuting_windows",
            "cx_removed",
            "rzz_inserted",
        },
    )
    return {
        "rule": "cx(control,target); rz(theta) target; cx(control,target) -> rzz(theta) control,target",
        "certificate_type": "local_rewrite_identity_plus_disjoint_commutation",
        "windows": totals["windows"],
        "commuting_disjoint_windows": totals["commuting_windows"],
        "cx_removed": totals["cx_removed"],
        "rzz_inserted": totals["rzz_inserted"],
    }


def combine_rzz_certificates(certificates: list[dict]) -> dict:
    combined = {
        "rule": "cx(control,target); rz(theta) target; cx(control,target) -> rzz(theta) control,target",
        "certificate_type": "local_rewrite_identity_plus_disjoint_commutation",
        "windows": 0,
        "commuting_disjoint_windows": 0,
        "cx_removed": 0,
        "rzz_inserted": 0,
    }
    for certificate in certificates:
        for key in ["windows", "commuting_disjoint_windows", "cx_removed", "rzz_inserted"]:
            combined[key] += int(certificate[key])
    return combined


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def summarize(
    before_path: Path,
    after_path: Path,
    equivalence_path: Path,
    method: str,
    rzz_passes: list[dict],
    local_certificates: dict,
    proof_logs: dict,
) -> dict:
    before = load_json(before_path)
    after = load_json(after_path)
    equivalence = load_json(equivalence_path) if equivalence_path.exists() else None
    before_rows = before["results"]
    after_rows = after["results"]

    def total(key: str, rows: list[dict]) -> float:
        return sum(float(row[key]) for row in rows)

    summary = {
        "benchmark_id": "B1",
        "method": method,
        "profile": before["profile"],
        "circuit_count": before["circuit_count"],
        "equivalence_passed": equivalence["passed"] if equivalence else None,
        "equivalence_failed": equivalence["failed"] if equivalence else None,
        "equivalence_mode": "exact_statevector" if equivalence else "skipped",
        "certificate_mode": "local_rewrite_certificates_plus_exact_statevector"
        if equivalence
        else "local_rewrite_certificates_without_global_statevector",
        "local_certificates": local_certificates,
        "proof_log_mode": "jsonl_local_rewrite_events_v1",
        "proof_logs": proof_logs,
        "rzz_passes": rzz_passes,
    }
    for key in [
        "operation_count",
        "two_qubit_gate_count",
        "logical_depth",
        "hardware_weighted_error_exposure",
    ]:
        short = "hardware_weighted_exposure" if key == "hardware_weighted_error_exposure" else key
        before_total = total(key, before_rows)
        after_total = total(key, after_rows)
        summary[f"{short}_before"] = before_total
        summary[f"{short}_after"] = after_total
        summary[f"{short}_delta"] = after_total - before_total
        summary[f"{short}_reduction_pct"] = (before_total - after_total) / before_total * 100 if before_total else 0
    return summary


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--profile", default="heavy_hex_like_sparse")
    parser.add_argument("--max-qubits", type=int, default=12)
    parser.add_argument("--max-rzz-passes", type=int, default=8)
    parser.add_argument("--max-scan", type=int, default=80)
    parser.add_argument("--skip-equivalence", action="store_true")
    parser.add_argument("--label", default="b1_pipeline")
    args = parser.parse_args(argv)

    if args.work_dir.exists():
        shutil.rmtree(args.work_dir)
    args.work_dir.mkdir(parents=True, exist_ok=True)
    args.results_dir.mkdir(parents=True, exist_ok=True)

    before_metrics = args.results_dir / f"{args.label}_before_metrics.json"
    after_metrics = args.results_dir / f"{args.label}_after_metrics.json"
    equivalence_path = args.results_dir / f"{args.label}_equivalence.json"
    summary_path = args.results_dir / f"{args.label}_summary.json"
    oneq_proof_log = args.results_dir / f"{args.label}_1q_proofs.jsonl"

    source_dir = args.work_dir / "00_input"
    oneq_dir = args.work_dir / "01_1q_commute"
    copy_qasm_tree(args.input, source_dir)

    oneq_stdout = run(
        [
            sys.executable,
            "tools/b1_single_qubit_resynth.py",
            str(source_dir),
            "--output-dir",
            str(oneq_dir),
            "--commute-disjoint",
            "--certificate-log",
            str(oneq_proof_log),
        ]
    )
    oneq_certificate = parse_oneq_certificate(oneq_stdout)

    current_dir = oneq_dir
    rzz_passes: list[dict] = []
    rzz_certificates: list[dict] = []
    rzz_proof_logs: list[dict] = []
    for pass_index in range(1, args.max_rzz_passes + 1):
        next_dir = args.work_dir / f"{pass_index + 1:02d}_rzz_pass"
        rzz_proof_log = args.results_dir / f"{args.label}_rzz_pass_{pass_index}_proofs.jsonl"
        command = [
            sys.executable,
            "tools/b1_rzz_resynth.py",
            str(current_dir),
            "--output-dir",
            str(next_dir),
            "--certificate-log",
            str(rzz_proof_log),
        ]
        if pass_index > 1:
            command.extend(["--commute-disjoint", "--max-scan", str(args.max_scan)])
        stdout = run(command)
        rzz_certificate = parse_rzz_certificate(stdout)
        windows = rzz_certificate["windows"]
        rzz_certificates.append(rzz_certificate)
        rzz_proof_logs.append(
            {
                "pass": pass_index,
                "mode": "adjacent" if pass_index == 1 else "commute_disjoint",
                "path": str(rzz_proof_log),
                "entries": count_jsonl(rzz_proof_log),
            }
        )
        rzz_passes.append(
            {
                "pass": pass_index,
                "mode": "adjacent" if pass_index == 1 else "commute_disjoint",
                "windows": windows,
                "commuting_disjoint_windows": rzz_certificate["commuting_disjoint_windows"],
                "cx_removed": rzz_certificate["cx_removed"],
                "rzz_inserted": rzz_certificate["rzz_inserted"],
                "output_dir": str(next_dir),
            }
        )
        current_dir = next_dir
        if windows == 0:
            break

    run(
        [
            sys.executable,
            "tools/b1_qasm_metrics.py",
            str(source_dir),
            "--profile",
            args.profile,
            "--pretty",
            "--output",
            str(before_metrics),
        ]
    )
    run(
        [
            sys.executable,
            "tools/b1_qasm_metrics.py",
            str(current_dir),
            "--profile",
            args.profile,
            "--pretty",
            "--output",
            str(after_metrics),
        ]
    )
    if not args.skip_equivalence:
        run(
            [
                sys.executable,
                "tools/b1_equivalence_check.py",
                str(source_dir),
                str(current_dir),
                "--max-qubits",
                str(args.max_qubits),
                "--pretty",
                "--output",
                str(equivalence_path),
            ]
        )

    final_dir = args.work_dir / "final"
    copy_qasm_tree(current_dir, final_dir)
    summary = summarize(
        before_metrics,
        after_metrics,
        equivalence_path,
        method="fixed_point_commuting_1q_plus_iterative_rzz_v0",
        rzz_passes=rzz_passes,
        local_certificates={
            "single_qubit_block_resynthesis": oneq_certificate,
            "rzz_window_resynthesis": combine_rzz_certificates(rzz_certificates),
        },
        proof_logs={
            "single_qubit_block_resynthesis": {
                "path": str(oneq_proof_log),
                "entries": count_jsonl(oneq_proof_log),
            },
            "rzz_window_resynthesis": rzz_proof_logs,
        },
    )
    summary["final_dir"] = str(final_dir)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["equivalence_failed"] in (0, None) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
