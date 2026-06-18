#!/usr/bin/env python3
"""Generate a deterministic exact-checkable B1 extension circuit suite."""

from __future__ import annotations

import argparse
from pathlib import Path


HEADER = 'OPENQASM 2.0;\ninclude "qelib1.inc";\n'


def measure_all(register: str, count: int) -> list[str]:
    return [f"measure {register}[{idx}] -> c[{idx}];" for idx in range(count)]


def rzz_window(control: int, target: int, theta: str, register: str = "q") -> list[str]:
    return [
        f"cx {register}[{control}],{register}[{target}];",
        f"rz({theta}) {register}[{target}];",
        f"cx {register}[{control}],{register}[{target}];",
    ]


def circuit(name: str, qubits: int, body: list[str]) -> tuple[str, str]:
    text = [
        HEADER,
        f"// B1 exact-extension generated circuit: {name}",
        f"qreg q[{qubits}];",
        f"creg c[{qubits}];",
        "",
        *body,
        "",
        *measure_all("q", qubits),
        "",
    ]
    return f"{name}.qasm", "\n".join(text)


def build_circuits() -> list[tuple[str, str, str]]:
    specs: list[tuple[str, str, str]] = []

    body = [f"h q[{idx}];" for idx in range(6)]
    for layer, theta in enumerate(["pi/7", "-pi/9", "pi/11"]):
        for left in range(5):
            body.extend(rzz_window(left, left + 1, theta))
            body.extend([f"rx(pi/{5 + left + layer}) q[{left}];", f"ry(pi/{7 + left}) q[{left + 1}];"])
    specs.append((*circuit("01_trotter_ladder_n6", 6, body), "hamiltonian_trotter_ladder"))

    body = [f"h q[{idx}];" for idx in range(8)]
    for layer, theta in enumerate(["pi/13", "pi/17"]):
        for left in range(8):
            right = (left + 1) % 8
            body.extend(rzz_window(left, right, theta))
            if left % 2 == 0:
                body.append(f"rz(pi/{9 + layer + left}) q[{left}];")
    specs.append((*circuit("02_ring_interaction_n8", 8, body), "ring_interaction_simulation"))

    body = ["h q[0];", "h q[1];", "h q[2];"]
    for data, ancilla in [(0, 5), (1, 5), (2, 6), (3, 6), (4, 5)]:
        body.append(f"cx q[{data}],q[{ancilla}];")
        body.append(f"rz(pi/{8 + data}) q[{ancilla}];")
        body.append(f"cx q[{data}],q[{ancilla}];")
        body.append(f"h q[{data}];")
    specs.append((*circuit("03_qec_syndrome_phase_n7", 7, body), "qec_syndrome_phase"))

    body = ["x q[0];", "x q[2];", "h q[4];"]
    for control, target, theta in [(0, 3, "pi/5"), (1, 4, "-pi/6"), (2, 5, "pi/8"), (3, 5, "pi/10")]:
        body.extend(rzz_window(control, target, theta))
    body.extend(["ccx q[0],q[1],q[3];", "ccx q[2],q[3],q[5];", "t q[0];", "tdg q[5];"])
    specs.append((*circuit("04_arithmetic_phase_n6", 6, body), "arithmetic_phase"))

    body = [f"h q[{idx}];" for idx in range(5)]
    for target in range(5):
        for control in range(target + 1, 5):
            body.append(f"cu1(pi/{2 ** (control - target + 1)}) q[{control}],q[{target}];")
        body.append(f"h q[{target}];")
    specs.append((*circuit("05_qft_phase_ladder_n5", 5, body), "qft_phase_ladder"))

    body = [f"ry(pi/{idx + 3}) q[{idx}];" for idx in range(10)]
    for pair, theta in [((0, 9), "pi/12"), ((1, 8), "-pi/10"), ((2, 7), "pi/14"), ((3, 6), "-pi/16"), ((4, 5), "pi/18")]:
        body.extend(rzz_window(pair[0], pair[1], theta))
        body.append(f"rz(pi/{pair[0] + 7}) q[{pair[0]}];")
        body.append(f"rx(pi/{pair[1] + 9}) q[{pair[1]}];")
    specs.append((*circuit("06_long_range_echo_n10", 10, body), "long_range_echo"))

    body = ["h q[0];", "h q[3];", "h q[6];"]
    body.extend(["cx q[0],q[1];", "rx(pi/7) q[5];", "ry(pi/9) q[6];", "rz(pi/5) q[1];", "cx q[0],q[1];"])
    body.extend(["cx q[2],q[3];", "rz(pi/11) q[7];", "rx(pi/13) q[0];", "rz(-pi/6) q[3];", "cx q[2],q[3];"])
    body.extend(["cx q[4],q[5];", "h q[0];", "h q[2];", "rz(pi/8) q[5];", "cx q[4],q[5];"])
    specs.append((*circuit("07_commuting_disjoint_windows_n8", 8, body), "commuting_disjoint_windows"))

    body = [f"ry(pi/{idx + 4}) q[{idx}];" for idx in range(8)]
    for rep in range(2):
        for left, theta in [(0, "pi/9"), (2, "-pi/9"), (4, "pi/7"), (6, "-pi/7")]:
            body.extend(rzz_window(left, left + 1, theta))
        for idx in range(8):
            body.append(f"rz(pi/{11 + idx + rep}) q[{idx}];")
    specs.append((*circuit("08_chemistry_ansatz_n8", 8, body), "chemistry_ansatz"))

    body = [f"h q[{idx}];" for idx in range(8)] + ["x q[8];", "h q[8];"]
    for control in range(8):
        if control not in {1, 4, 7}:
            body.append(f"cx q[{control}],q[8];")
            body.append(f"rz(pi/{control + 5}) q[{control}];")
    body.extend([f"h q[{idx}];" for idx in range(8)])
    specs.append((*circuit("09_bv_phase_oracle_n9", 9, body), "bv_phase_oracle"))

    body = [f"h q[{idx}];" for idx in range(6)]
    for gamma in ["pi/10", "pi/12", "-pi/14"]:
        for left, right in [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)]:
            body.extend(rzz_window(left, right, gamma))
        for idx in range(6):
            body.append(f"rx(pi/{idx + 6}) q[{idx}];")
    specs.append((*circuit("10_qaoa_double_triangle_n6", 6, body), "qaoa_double_triangle"))

    body = []
    for base in [0, 3, 6]:
        body.extend([f"h q[{base}];", f"cx q[{base}],q[{base + 1}];", f"cx q[{base + 1}],q[{base + 2}];"])
        body.extend(rzz_window(base, base + 2, "pi/6"))
    body.extend(["h q[9];", "cx q[9],q[0];", "rz(pi/15) q[0];", "cx q[9],q[0];"])
    specs.append((*circuit("11_stabilizer_mixer_n10", 10, body), "stabilizer_mixer"))

    body = ["x q[0];", "x q[1];", "h q[2];"]
    body.extend(["ccx q[0],q[1],q[3];", "ccx q[2],q[3],q[4];"])
    body.extend(rzz_window(4, 5, "pi/9"))
    body.extend(["t q[3];", "tdg q[4];", "cx q[5],q[6];", "rz(-pi/7) q[6];", "cx q[5],q[6];"])
    specs.append((*circuit("12_toffoli_phase_n7", 7, body), "toffoli_phase"))

    return specs


def write_manifest(output_dir: Path, manifest_path: Path, specs: list[tuple[str, str, str]]) -> None:
    lines = [
        "id: B1_exact_extension",
        "benchmark_id: B1",
        "name: B1 deterministic exact-checkable extension suite",
        "version: 0.1",
        "source: generated_by_tools/b1_generate_exact_extension.py",
        "purpose: >",
        "  Extend B1 exact statevector validation from 18 to at least 30 circuits",
        "  using deterministic nontrivial OpenQASM circuits with interaction windows.",
        "circuit_count: 12",
        "max_qubits: 10",
        "circuits:",
    ]
    for filename, _text, family in specs:
        lines.extend(
            [
                f"  - file: b1_exact_extension/{filename}",
                f"    family: {family}",
            ]
        )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("benchmarks/b1_exact_extension"))
    parser.add_argument("--manifest", type=Path, default=Path("benchmarks/B1_exact_extension_manifest.yaml"))
    args = parser.parse_args()

    specs = build_circuits()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, text, _family in specs:
        (args.output_dir / filename).write_text(text, encoding="utf-8")
    write_manifest(args.output_dir, args.manifest, specs)
    print(f"generated {len(specs)} circuits in {args.output_dir}")
    print(f"manifest {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
