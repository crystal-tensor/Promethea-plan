# B10-T1 Source-Backed Boundary Baselines v0.2

Last updated: 2026-06-13

Status: **source_backed_denominator_baselines_instantiated_not_publishable_theorem**

## Summary

- Source target: B10-T1 / linear_systems_data_loading_negative_boundary
- Builds on: b10_t1_negative_boundary_proof_v0
- Source anchors: 6
- Denominator baselines: 5
- Boundary checks: 4
- Explicitly not a BQP separation: True
- Validation errors: 0

## What Changed

- B10-T1-O1 is now source-linked across HHL/QLSA, dequantization, and classical sparse-solver baselines.
- B10-T1-O2 now has five concrete denominator regimes that future B3/B5/B10 claims must choose from.
- B10-T1-O3 is partly scoped: sampling-access and low-rank regimes are no longer treated as ordinary explicit-I/O tasks, but a separate theorem note is still needed.

## Sources

### hhl_2009

- Citation: Harrow, Hassidim, Lloyd (2009), [Quantum algorithm for solving linear systems of equations](https://arxiv.org/abs/0811.3171)
- Role: canonical_quantum_linear_systems_claim
- Supports:
  - The HHL task is naturally a state or observable-estimation task, not a free full-vector-output task.
  - The headline speedup depends on sparsity, conditioning, precision, and access assumptions.

### childs_kothari_somma_2017

- Citation: Childs, Kothari, Somma (2017), [Quantum algorithm for systems of linear equations with exponentially improved dependence on precision](https://arxiv.org/abs/1511.02306)
- Role: improved_qlsa_precision_boundary
- Supports:
  - Modern QLSA improvements refine precision dependence while still outputting a solution state.
  - Precision improvements do not remove state-preparation, oracle, block-encoding, or readout accounting.

### tang_2019

- Citation: Tang (2019), [A quantum-inspired classical algorithm for recommendation systems](https://arxiv.org/abs/1807.04271)
- Role: dequantization_warning_for_sampling_access
- Supports:
  - Under strong sample/query input access, some claimed quantum machine-learning speedups can be classically matched up to polynomial factors.
  - Sampling access is not a harmless implementation detail; it changes the fair classical denominator.

### chia_lin_wang_2018

- Citation: Chia, Lin, Wang (2018), [Quantum-inspired sublinear classical algorithms for solving low-rank linear systems](https://arxiv.org/abs/1811.04852)
- Role: linear_systems_dequantization_boundary
- Supports:
  - Low-rank linear systems with sample/query access admit sublinear classical algorithms for samples or entries of the solution.
  - A B10-T1 claim must separate explicit-I/O, succinct-oracle, and sampling-access regimes.

### shewchuk_1994

- Citation: Shewchuk (1994), [An Introduction to the Conjugate Gradient Method Without the Agonizing Pain](https://www.cs.cmu.edu/~quake-papers/painless-conjugate-gradient.pdf)
- Role: classical_sparse_spd_baseline
- Supports:
  - Conjugate gradient is a standard denominator for sparse symmetric positive-definite systems.
  - Iteration cost scales through sparse matrix-vector products and condition-dependent convergence.

### paige_saunders_1982

- Citation: Paige, Saunders (1982), [LSQR: An algorithm for sparse linear equations and sparse least squares](https://doi.org/10.1145/355984.355989)
- Role: classical_general_sparse_least_squares_baseline
- Supports:
  - LSQR is a standard baseline for general sparse linear equations and least-squares instances.
  - General sparse linear-system claims need a denominator beyond SPD-only conjugate gradient.

## Denominator Baselines

### D1_explicit_spd_full_solution_cg

- Task regime: Explicit sparse SPD A, explicit b, full solution vector requested.
- Classical denominator: Conjugate gradient or preconditioned conjugate gradient.
- Cost shape: O(nnz(A) * sqrt(kappa) * log(1/epsilon)) style matvec iteration accounting, plus Omega(n * bits) output writing for full x.
- Quantum claim allowed: No end-to-end exponential speedup claim unless input loading, block encoding, state preparation, and full readout are charged and still dominated.
- Sources: shewchuk_1994, hhl_2009

### D2_explicit_general_sparse_least_squares

- Task regime: Explicit rectangular or nonsymmetric sparse linear equation / least-squares instance.
- Classical denominator: LSQR or Krylov-family sparse iterative solvers.
- Cost shape: O(iterations * nnz(A)) sparse multiply accounting, plus explicit output or certificate cost.
- Quantum claim allowed: Only compare observable or state-output QLSA claims after charging all access construction and readout costs.
- Sources: paige_saunders_1982, childs_kothari_somma_2017

### D3_succinct_oracle_small_observable

- Task regime: Succinctly generated or prebuilt oracle/block-encoding with only a small observable required.
- Classical denominator: Best known classical algorithm under the same succinct description or oracle contract.
- Cost shape: Query complexity plus oracle-construction cost and observable-estimation samples; no full-vector readout.
- Quantum claim allowed: Admissible candidate advantage regime, but not a full explicit-I/O speedup claim.
- Sources: hhl_2009, childs_kothari_somma_2017

### D4_low_rank_sampling_access

- Task regime: Low-rank or recommendation-style matrix with sample/query access to rows, columns, norms, or entries.
- Classical denominator: Quantum-inspired sample/query classical algorithms.
- Cost shape: poly(rank, kappa, norm, 1/epsilon) * polylog(dimensions) style accounting under the same access model.
- Quantum claim allowed: No exponential claim until compared against dequantized sampling-access baselines.
- Sources: tang_2019, chia_lin_wang_2018

### D5_b3_b5_observable_linear_response

- Task regime: B3/B5 physics observable that reduces to a linear-system or Green-function estimate.
- Classical denominator: Domain baseline: sparse Krylov/DMRG/embedding/Monte Carlo as applicable, plus observable estimator.
- Cost shape: End-to-end wall-clock or operation-count baseline at fixed physical observable error, not only abstract QLSA query count.
- Quantum claim allowed: A future B3/B5 claim must state whether the advantage is from Hamiltonian simulation, state preparation, or observable estimation.
- Sources: hhl_2009, childs_kothari_somma_2017, shewchuk_1994

## Boundary Checklist

- C1_output_contract: Does the task request the full vector x, a sample from x, one entry of x, or an expectation value?
  Reject if: The claim advertises polylog(n) end-to-end runtime while requesting full explicit x.
- C2_access_contract: Is A/b explicit input, succinctly generated, oracle-provided, block-encoded, or sample/query accessible?
  Reject if: The claim treats oracle or sample/query access as free while comparing to an explicit-input classical baseline.
- C3_condition_precision_contract: Are kappa, epsilon, sparsity/rank, norm parameters, and success probability fixed in both algorithms?
  Reject if: The claim hides poor condition number, precision, or norm dependence in constants.
- C4_denominator_contract: Is the classical denominator CG/LSQR/domain-specific/dequantized under the same access model?
  Reject if: The claim compares a quantum oracle query bound to a weaker classical explicit-I/O baseline.

## Claim Boundary

- now_supported: B10-T1 is source-backed enough to reject hidden full-output/loading/readout HHL-style end-to-end exponential claims.
- still_not_supported: It is not yet a literature-ready theorem paper, not a BQP/classical separation, and not a blanket rejection of QLSA advantages.
- next_proof_pressure: Extend the D1/D2 numerical table to one D5 B3/B5 observable task, or write the D4 sampling-access theorem note.

## Remaining Open Items

- Replace cost-shape placeholders with theorem-specific asymptotic constants after choosing one B3/B5 observable.
- Add a source-backed sampling-access theorem note for the Chia-Lin-Wang regime.
- Map the D5 observable-denominator regime to one concrete B3/B5 physics task.
