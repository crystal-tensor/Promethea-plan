#!/usr/bin/env python3
"""Build a small PySCF-backed resource-estimation baseline for B3."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
from pyscf import gto, scf


MOLECULES = {
    "h2_calibration": {
        "atom": "H 0 0 0; H 0 0 0.7414",
        "charge": 0,
        "spin": 0,
    },
    "lih_calibration": {
        "atom": "Li 0 0 0; H 0 0 1.6",
        "charge": 0,
        "spin": 0,
    },
    "h2o_calibration": {
        "atom": "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587",
        "charge": 0,
        "spin": 0,
    },
    "n2_calibration": {
        "atom": "N 0 0 0; N 0 0 1.0977",
        "charge": 0,
        "spin": 0,
    },
}


def estimate_resources(row: dict, precision_hartree: float, observable_fraction: float) -> dict:
    phase_bits = math.ceil(math.log2(1 / precision_hartree))
    lambda_full = row["lambda_one_body_proxy"] + row["lambda_two_body_proxy"]
    full_query_steps = math.ceil(lambda_full / precision_hartree)
    full_step_cost = 2 * row["one_body_spin_terms"] + 8 * row["two_body_spin_terms"]
    full_t_count = full_query_steps * full_step_cost
    full_logical_qubits = row["spin_orbitals"] + phase_bits + 8

    observable_terms = max(1, math.ceil(row["two_body_spin_terms"] * observable_fraction))
    observable_lambda = max(precision_hartree, lambda_full * observable_fraction)
    observable_query_steps = math.ceil(observable_lambda / precision_hartree)
    observable_step_cost = 2 * max(1, math.ceil(row["one_body_spin_terms"] * observable_fraction)) + 8 * observable_terms
    state_prep_penalty = 4
    observable_t_count = observable_query_steps * observable_step_cost * state_prep_penalty
    observable_logical_qubits = math.ceil(row["spin_orbitals"] * max(0.5, observable_fraction)) + phase_bits + 8

    return {
        "precision_hartree": precision_hartree,
        "phase_register_bits": phase_bits,
        "full_phase_estimation": {
            "logical_qubits_proxy": full_logical_qubits,
            "query_steps_proxy": full_query_steps,
            "t_count_proxy": full_t_count,
            "step_cost_proxy": full_step_cost,
        },
        "observable_first": {
            "observable_fraction": observable_fraction,
            "logical_qubits_proxy": observable_logical_qubits,
            "query_steps_proxy": observable_query_steps,
            "t_count_proxy": observable_t_count,
            "step_cost_proxy": observable_step_cost,
            "state_prep_penalty": state_prep_penalty,
        },
        "proxy_t_count_reduction_factor": full_t_count / observable_t_count if observable_t_count else float("inf"),
        "proxy_logical_qubit_reduction_factor": full_logical_qubits / observable_logical_qubits if observable_logical_qubits else float("inf"),
    }


def run_molecule(name: str, spec: dict, basis: str, integral_cutoff: float, precision_hartree: float, observable_fraction: float) -> dict:
    started = time.perf_counter()
    mol = gto.Mole()
    mol.atom = spec["atom"]
    mol.unit = "Angstrom"
    mol.basis = basis
    mol.charge = spec["charge"]
    mol.spin = spec["spin"]
    mol.verbose = 0
    mol.build()

    mf = scf.RHF(mol)
    hf_energy = float(mf.kernel())
    hcore = mf.get_hcore()
    eri = mol.intor("int2e")

    spatial_orbitals = int(mol.nao_nr())
    spin_orbitals = 2 * spatial_orbitals
    one_body_nonzero = int(np.count_nonzero(np.abs(hcore) > integral_cutoff))
    two_body_nonzero = int(np.count_nonzero(np.abs(eri) > integral_cutoff))
    row = {
        "molecule": name,
        "basis": basis,
        "charge": mol.charge,
        "spin": mol.spin,
        "electrons": int(mol.nelectron),
        "spatial_orbitals": spatial_orbitals,
        "spin_orbitals": spin_orbitals,
        "hf_energy_hartree": hf_energy,
        "nuclear_repulsion_hartree": float(mol.energy_nuc()),
        "one_body_integral_nonzero": one_body_nonzero,
        "two_body_integral_nonzero": two_body_nonzero,
        "one_body_spin_terms": 2 * one_body_nonzero,
        "two_body_spin_terms": 4 * two_body_nonzero,
        "lambda_one_body_proxy": float(2 * np.sum(np.abs(hcore))),
        "lambda_two_body_proxy": float(4 * np.sum(np.abs(eri))),
        "integral_cutoff": integral_cutoff,
        "runtime_seconds": time.perf_counter() - started,
    }
    row["resource_estimates"] = estimate_resources(row, precision_hartree, observable_fraction)
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--basis", default="sto-3g")
    parser.add_argument("--molecules", default="h2_calibration,lih_calibration,h2o_calibration,n2_calibration")
    parser.add_argument("--integral-cutoff", type=float, default=1e-10)
    parser.add_argument("--precision-hartree", type=float, default=0.0016)
    parser.add_argument("--observable-fraction", type=float, default=0.2)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    selected = [item.strip() for item in args.molecules.split(",") if item.strip()]
    rows = []
    for name in selected:
        if name not in MOLECULES:
            raise SystemExit(f"Unknown molecule preset: {name}")
        rows.append(
            run_molecule(
                name=name,
                spec=MOLECULES[name],
                basis=args.basis,
                integral_cutoff=args.integral_cutoff,
                precision_hartree=args.precision_hartree,
                observable_fraction=args.observable_fraction,
            )
        )

    payload = {
        "benchmark_id": "B3",
        "method": "pyscf_small_molecule_resource_proxy_v0",
        "model_status": "pyscf_hf_integrals_plus_proxy_resource_estimates",
        "basis": args.basis,
        "precision_hartree": args.precision_hartree,
        "observable_fraction": args.observable_fraction,
        "integral_cutoff": args.integral_cutoff,
        "molecule_count": len(rows),
        "results": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
