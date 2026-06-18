# B8 Prototype Notes: Classical Verification of Quantum Outputs v0.1

Last updated: 2026-06-13

Problem: **30. Efficient classical verification of quantum outputs**

The eighth attack direction is initialized with a toy hidden-invariant property
tester. This is not full output-distribution verification and not a quantum
advantage proof. It is a benchmark scaffold for testing whether hidden
task-relevant projections can reject simple spoofers while preserving honest
completeness.

## Current Components

- Benchmark manifest: `../benchmarks/B8_classical_verification_outputs.yaml`
- Invariant verifier: `../tools/b8_output_invariant_verifier.py`
- Adaptive leakage spoofer stress test:
  `../tools/b8_adaptive_spoofer_leakage.py`
- First result: `../results/B8_output_invariant_verifier_v0.json`
- Adaptive leakage result: `../results/B8_adaptive_leakage_spoofer_v0.json`

## Protocol Model

The v0 task family uses synthetic bitstring samplers with hidden parity
projection invariants. The verifier estimates reference projection means from
an honest sampler and accepts a candidate sample set only if all hidden
projection means are within a fixed tolerance.

Adversaries include:

1. `uniform_random_spoofer`
2. `marginal_matching_spoofer`
3. `public_invariant_spoofer`
4. `leaked_half_invariant_spoofer`
5. `weak_surrogate_spoofer`

The point is to test the verification envelope, not to model a realistic
quantum experiment yet.

## Metrics

- honest completeness
- adversary soundness
- invariant count
- sample count
- maximum projection error
- number of adversaries failing the invariant rule

## First Results

The first run covers 3 hidden-parity tasks, 5 adversaries, and 15 total
task/adversary configurations.

| Metric | Value |
|---|---:|
| Tasks | 3 |
| Invariants per task | 8 |
| Samples per trial | 4096 |
| Trials | 100 |
| Minimum honest completeness | 1.000 |
| Maximum adversary soundness | 0.000 |
| Adversaries failing invariant rule | 5 |

All five toy adversaries fail the current hidden-invariant rule:

1. `uniform_random_spoofer`
2. `marginal_matching_spoofer`
3. `public_invariant_spoofer`
4. `leaked_half_invariant_spoofer`
5. `weak_surrogate_spoofer`

Interpretation:

- Hidden projection checks can reject simple sample spoofers without learning
  the full output distribution.
- The current toy benchmark is intentionally favorable to the verifier; the
  next version needs adaptive spoofers and randomized-measurement tasks.
- The result should be read as a verifier harness milestone, not as a claim
  about real quantum outputs.

## Adaptive Leakage Stress Test v0

B8 now has a first adaptive-spoofer stress layer. The benchmark lets spoofers
observe a controlled fraction of hidden projection invariants, infer or guess
some remaining hidden projections, and then attempts to pass the same
hidden-invariant verifier.

Configuration:

- Tasks: 3.
- Invariants per task: 10.
- Samples per trial: 4,096.
- Trials per configuration: 120.
- Leakage fractions: 0.0, 0.25, 0.5, 0.75.
- Adaptive adversaries: 4.
- Configurations: 48.

Result summary:

| Leakage fraction | Maximum adaptive soundness | Adversaries over 5% |
|---:|---:|---|
| 0.00 | 0.000 | none |
| 0.25 | 0.000 | none |
| 0.50 | 0.000 | none |
| 0.75 | 0.792 | `trap_aware_leakage_spoofer` |

Interpretation:

- Low and mid leakage are rejected in the current synthetic task family.
- High leakage is dangerous: once 75% of hidden projections leak and the
  spoofer can infer most remaining hidden projections, soundness can rise to
  0.792.
- This is a useful failure boundary rather than a bad result. It says B8/B4
  protocols need challenge refresh, hidden projection rotation, or trap
  redundancy before they can claim adaptive robustness.

## Limits

- The task distribution is synthetic.
- Invariants are parity checks, not classical shadows or randomized
  measurements.
- Spoofers are simple scalar-knowledge models.
- The new adaptive spoofers are still heuristic projection-enforcement
  models, not trained generative models.
- No real quantum backend or experimental noise is included.

## Next Algorithmic Step

Build the first useful B8 comparison:

1. Replace hidden parity checks with randomized measurement invariants.
2. Add classical-shadow observable tests.
3. Connect B8 to B4 trap-protocol tasks so both share verifier challenges.
4. Replace the current adaptive heuristics with trained generative or
   tensor-network spoofers that consume public metadata.
5. Add challenge refresh and projection rotation, then rerun the leakage
   boundary test.
6. Measure sample complexity against full-distribution learning baselines.
