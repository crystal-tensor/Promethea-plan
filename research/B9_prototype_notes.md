# B9 Prototype Notes: Quantum PCP Local-Hamiltonian Lab v0.1

Last updated: 2026-06-13

Problem: **17. Quantum PCP conjecture and Local Hamiltonian hardness**

The ninth attack direction is initialized with a small exact-diagonalization
laboratory for local Hamiltonian gap behavior. This is not a Quantum PCP proof
and not evidence for the conjecture. It is a computational lab for finding
small proof-pattern candidates and counterexamples where a transformation
appears to amplify a spectral gap but fails after normalized-gap, locality, or
ground-space checks.

## Current Components

- Benchmark manifest: `../benchmarks/B9_quantum_pcp_local_hamiltonian.yaml`
- Gap lab runner: `../tools/b9_local_hamiltonian_gap_lab.py`
- First result: `../results/B9_local_hamiltonian_gap_lab_v0.json`

## Model Families

The v0 lab uses exact diagonalization on small qubit systems for:

1. `transverse_ising_frustrated`
2. `xxz_chain`
3. `cluster_stabilizer_open`

For each model and qubit count, it measures baseline spectral gap, normalized
gap, and ground-state vector.

## Transformations

The first two transformations are deliberately simple:

1. `local_interaction_reweight_v0`: reweights local interaction terms while
   preserving the original term support.
2. `shifted_square_spectral_filter_v0`: applies a dense shifted-square
   spectral filter. This often amplifies gaps but destroys locality, so it is
   tracked as a counterexample screen rather than a valid local PCP step.

## Metrics

- spectral gap
- normalized gap
- gap ratio
- normalized-gap ratio
- ground-state overlap
- locality maximum
- candidate-pass count
- counterexample-candidate count

## First Results

The first run covers 3 model families, 3 qubit counts, and 2 transformations,
for 18 total configurations.

| Metric | Value |
|---|---:|
| Configurations | 18 |
| Locality-preserving candidates | 9 |
| Candidate passes | 0 |
| Counterexample candidates | 4 |
| Max local normalized-gap ratio | 1.000000 |
| Max dense-filter raw gap ratio | 2.414243 |

Interpretation:

- The local reweighting transformation can increase raw spectral gaps in some
  cases, but it does not improve normalized gap under the v0 screen.
- The dense shifted-square filter can strongly increase raw gap, but it grows
  locality and is therefore tracked as a counterexample screen rather than a
  valid locality-preserving proof step.
- The useful B9 result so far is negative: naive gap amplification patterns
  fail once normalized gap, ground-space overlap, and locality are checked
  together.

## Limits

- Dense exact diagonalization only reaches tiny systems.
- The transformations are toy probes, not proof constructions.
- The shifted-square filter is nonlocal and mainly illustrates a trap.
- No product-test, robust gap amplification, or proof-assistant formalization
  is implemented yet.

## Next Algorithmic Step

Build the first useful B9 search:

1. Add random local-Hamiltonian instance generation.
2. Add product-test-inspired transformations.
3. Export a small counterexample database where naive transformations fail.
4. Track locality growth symbolically rather than only by a scalar.
5. Formalize one promising or failing pattern in a proof assistant.
