# B3 Prototype Notes: Molecular Reaction Resource Estimation v0.1

Last updated: 2026-06-15

Problem: **49. Exact molecular reaction dynamics**

The third attack direction is now initialized with a PySCF-backed calibration
and resource-estimation proxy. This is not yet a reaction-dynamics result and
not a fault-tolerant compiler output. It establishes the schema needed to
compare full-Hamiltonian phase-estimation style baselines against
observable-first estimates.

## Current Components

- Benchmark manifest: `../benchmarks/B3_molecular_reaction_dynamics.yaml`
- PySCF resource estimator: `../tools/b3_pyscf_resource_estimator.py`
- First result: `../results/B3_pyscf_resource_estimate_v0.json`
- B10-T1 D5 observable-denominator proxy:
  `../research/B10_t1_d5_b3_molecular_observable_table.md`
- B10-T1 Hamiltonian-derived D5 reaction-coordinate denominator:
  `../research/B10_t1_d5_b3_reaction_observable_table.md`
- B10-T1 correlated D5 reaction-coordinate references:
  `../research/B10_t1_d5_b3_correlated_reference_table.md`
- B10-T1 FCI-strength D5 reaction-coordinate references:
  `../research/B10_t1_d5_b3_fci_reference_table.md`

## Calibration Set

The v0 calibration uses small closed-shell molecules in STO-3G:

1. `h2_calibration`
2. `lih_calibration`
3. `h2o_calibration`
4. `n2_calibration`

For each molecule, the runner records:

- RHF energy from PySCF.
- Electron count.
- Spatial and spin orbital counts.
- Nonzero one- and two-electron integral counts.
- Lambda-style integral norm proxies.
- Full phase-estimation resource proxy.
- Observable-first resource proxy.

## Resource Proxy

The resource model is intentionally simple:

- Precision: 0.0016 Hartree.
- Observable fraction: 0.2.
- Full baseline: query-step proxy proportional to full integral lambda.
- Observable-first proxy: query-step proxy proportional to a selected
  observable fraction, with a state-preparation penalty of 4.
- T-count proxy: query steps multiplied by a term-count step-cost proxy.

This proxy is useful for comparing scaling interfaces, not for claiming a final
fault-tolerant resource estimate.

## First Results

| Molecule | Electrons | Spin orbitals | RHF energy | Full T proxy | Observable T proxy | Reduction |
|---|---:|---:|---:|---:|---:|---:|
| H2 | 2 | 4 | -1.116684 | 1.254e7 | 2.053e6 | 6.11x |
| LiH | 4 | 12 | -7.861865 | 1.159e9 | 1.859e8 | 6.23x |
| H2O | 10 | 14 | -74.963063 | 1.909e10 | 3.055e9 | 6.25x |
| N2 | 14 | 20 | -107.495893 | 7.658e10 | 1.225e10 | 6.25x |

Interpretation:

- The proxy meets the B3 first-pass goal of producing a reproducible resource
  estimate with explicit state-preparation penalty and precision assumptions.
- The approximate 6x proxy reduction is a signal that observable-first
  formulations are worth testing, not evidence that the chemistry problem is
  solved.
- H2 and LiH are calibration only; H2O and N2 begin to exercise larger term
  counts but remain too small to represent the hard reaction-dynamics regime.
- B10-T1 now adds a D5 molecular observable-denominator proxy for these four
  calibration molecules, making future HHL-style observable claims charge a
  classical response denominator before advertising a speedup.
- B10-T1 now also includes a Hamiltonian-derived reaction-coordinate
  denominator table: finite-difference one-electron Hamiltonian sources,
  central RHF orbitals, and singles response denominators for H2, LiH, H2O,
  and N2 coordinate rows.
- B10-T1 now adds correlated reaction-coordinate references for the same four
  rows, with RHF, MP2, and CCSD finite-difference energy derivatives. This
  strengthens the classical denominator but still does not solve reaction
  dynamics or demonstrate a quantum advantage.
- B10-T1 now also adds FCI-strength references in the same STO-3G settings,
  producing RHF/MP2/CCSD/FCI finite-difference derivatives for the four rows.
  This gives a stronger small-active-space denominator for future quantum
  observable-estimation comparisons.

## Limits

- No OpenFermion fermion-to-qubit mapping is yet emitted.
- No Trotter, qubitization, or phase-estimation circuit is compiled.
- State preparation is represented by a scalar penalty, not by an algorithm.
- No selected-CI, larger active-space, DMRG, or tensor-network baseline
  is included yet.
- No reaction coordinate or transition-state observable is modeled yet.

## Next Algorithmic Step

Build the first reaction-relevant B3 comparison:

1. Emit OpenFermion-compatible Hamiltonian metadata for the calibration set.
2. Add at least one reaction proxy, such as stretched N2 or a small
   photochemical active-space proxy.
3. Replace scalar state-preparation penalty with an explicit assumption ledger.
4. Upgrade the existing PySCF RHF/MP2/CCSD/FCI reference columns with
   selected-CI, larger active-space references, or tensor/DMRG baselines.
5. Compare the B10-T1 FCI denominator against an explicit quantum
   observable-estimation circuit, then decide whether the observable-first
   route has an accuracy-per-resource opening.
