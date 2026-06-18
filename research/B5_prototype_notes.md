# B5 Prototype Notes: Strongly Correlated Matter v0.1

Last updated: 2026-06-13

Problem: **38. Strongly correlated quantum matter**

The fifth attack direction is now initialized with a small exact-diagonalization
baseline for the one-dimensional half-filled Fermi-Hubbard model. This is not a
hybrid quantum advantage result yet. It establishes a calibration harness where
future quantum impurity or plaquette kernels can be compared against exact
small-system energies and simple cluster-product proxies.

## Current Components

- Benchmark manifest: `../benchmarks/B5_strongly_correlated_matter.yaml`
- Exact diagonalization runner: `../tools/b5_hubbard_embedding_baseline.py`
- First result: `../results/B5_hubbard_embedding_baseline_v0.json`

## Baseline Model

The v0 benchmark uses the open-boundary 1D Fermi-Hubbard Hamiltonian at
half filling:

`H = -t sum_<i,j>,sigma (c^dagger_i,sigma c_j,sigma + h.c.) + U sum_i n_i,up n_i,down`

The runner computes exact ground-state energies for small systems and compares
them with a cluster-product proxy that solves disconnected 2-site or 4-site
clusters and sums their energies.

This proxy is deliberately weak. Its purpose is to expose the missing
inter-cluster entanglement and correlation energy that a hybrid
quantum-tensor/embedding method must recover.

## First Results

The first run covers:

- Sites: 4, 6, 8.
- Interaction strengths: U/t = 2, 4, 8.
- Boundary condition: open.
- Cluster sizes: 2 and 4 where compatible.
- Total result rows: 15.

Summary by cluster size:

| Cluster size | Configurations | Mean error/site | Max error/site |
|---:|---:|---:|---:|
| 2 | 9 | 0.095526 | 0.160170 |
| 4 | 6 | 0.020620 | 0.059219 |

Interpretation:

- Exact diagonalization gives a trustworthy small-system calibration target.
- The cluster-product proxy has nonzero error whenever inter-cluster hopping
  and entanglement matter.
- Moving from 2-site to 4-site clusters reduces mean error per site by about
  4.63x on this small calibration grid.
- This creates the first measurable B5 target: recover cluster-product error
  using an embedding correction, tensor boundary update, or quantum impurity
  kernel.

## Limits

- The benchmark is 1D and small; DMRG will be extremely strong here.
- No tensor-network, DMFT, VMC, or quantum kernel baseline is implemented yet.
- Only ground-state energy is measured; spin, charge, pairing, and spectral
  observables are not included.
- The cluster-product proxy is not a serious state-of-the-art baseline.

## Next Algorithmic Step

Build the first genuine hybrid-solver comparison:

1. Add a DMRG or tensor-network reference for the same chains.
2. Add plaquette and impurity partitions with boundary fields.
3. Optimize boundary fields classically while solving each cluster exactly.
4. Replace exact cluster solves with a quantum-kernel interface that can later
   target small quantum hardware or simulators.
5. Measure whether the hybrid correction recovers a meaningful fraction of the
   cluster-product error per site.
