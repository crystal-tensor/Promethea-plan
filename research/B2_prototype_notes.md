# B2 Prototype Notes: Low-Overhead QEC Baseline v0.1

Last updated: 2026-06-13

Problem: **22. Low-overhead quantum error correction**

The second attack direction is now initialized with a reproducible control
benchmark plus a first circuit-level surface-code memory baseline. This is
not yet an LDPC or searched-code improvement result; it establishes the output
schema, confidence intervals, space-time accounting, decoder-runtime fields,
and a real Stim/PyMatching comparison target needed for stronger B2
experiments.

## Current Components

- Benchmark manifest: `../benchmarks/B2_qec_overhead.yaml`
- Repetition-code baseline runner: `../tools/b2_repetition_code_baseline.py`
- Target-volume estimator: `../tools/b2_target_volume.py`
- Rough surface-code threshold-law estimator:
  `../tools/b2_surface_code_threshold_estimator.py`
- Phenomenological repetition decoder fallback:
  `../tools/b2_phenomenological_repetition_decoder.py`
- Stim/PyMatching surface-code baseline:
  `../tools/b2_stim_surface_code_baseline.py`
- Stim/PyMatching target-volume summarizer:
  `../tools/b2_stim_surface_code_target_volume.py`
- Stim/PyMatching biased-schedule circuit sweep:
  `../tools/b2_stim_biased_schedule_sweep.py`
- First result: `../results/B2_repetition_code_memory_baseline_v0.json`
- Target-volume result: `../results/B2_repetition_code_target_volume_v0.json`
- Rough surface-code estimate:
  `../results/B2_surface_code_threshold_estimate_v0.json`
- Phenomenological decoder result:
  `../results/B2_phenomenological_repetition_decoder_v0.json`
- Stim/PyMatching surface-code baseline result:
  `../results/B2_stim_surface_code_memory_baseline_v0.json`
- Stim/PyMatching target-volume result:
  `../results/B2_stim_surface_code_target_volume_v0.json`
- Stim/PyMatching biased-schedule sweep result:
  `../results/B2_stim_biased_schedule_sweep_v0.json`

## Baseline Definition

The v0 baseline is an odd-distance repetition-code memory control with
independent physical bit-flip errors and a majority-vote decoder.

Sweep:

- Distances: 3, 5, 7, 9, 11.
- Physical error rates: 0.001, 0.003, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15.
- Shots per configuration: 20,000.
- Seed: 220626.
- Configurations: 40.

Metrics:

- Monte Carlo logical error rate.
- Exact binomial logical error rate.
- Wilson 95% confidence interval.
- Physical qubits.
- Rounds.
- Space-time volume proxy: `physical_qubits * rounds`.
- Majority-decoder runtime per shot.

## First Results

Selected exact logical error rates:

| Physical error | d=3 | d=5 | d=7 | d=9 | d=11 |
|---:|---:|---:|---:|---:|---:|
| 0.02 | 1.184e-3 | 7.762e-5 | 5.336e-6 | 3.770e-7 | 2.712e-8 |
| 0.05 | 7.250e-3 | 1.158e-3 | 1.936e-4 | 3.322e-5 | 5.801e-6 |
| 0.10 | 2.800e-2 | 8.560e-3 | 2.728e-3 | 8.909e-4 | 2.957e-4 |
| 0.15 | 6.075e-2 | 2.661e-2 | 1.210e-2 | 5.629e-3 | 2.657e-3 |

Interpretation:

- The control benchmark shows expected distance scaling below the repetition
  code's 50% majority-vote threshold.
- The space-time proxy grows quadratically in this toy memory setting, so the
  useful B2 question is not just lower logical error, but lower logical error
  per qubit-round at a target reliability.
- The low-error rows have many zero Monte Carlo failures at 20,000 shots; the
  exact binomial column is therefore the authoritative baseline there.

## Target Space-Time Volume v0

The first target-volume layer converts logical-error curves into the benchmark
quantity B2 ultimately needs: the smallest code distance and space-time volume
that hit a target logical error.

Targets:

- 1e-2.
- 1e-3.
- 1e-4.
- 1e-5.

Result summary:

- Physical error rates checked: 8.
- Target combinations checked: 32.
- Met by available distances 3-11: 27.
- Unmet by available distances 3-11: 5.

Selected minimum space-time volumes:

| Physical error | Target 1e-2 | Target 1e-3 | Target 1e-4 | Target 1e-5 |
|---:|---:|---:|---:|---:|
| 0.02 | d3 / 9 | d5 / 25 | d5 / 25 | d7 / 49 |
| 0.05 | d3 / 9 | d7 / 49 | d9 / 81 | d11 / 121 |
| 0.10 | d5 / 25 | d9 / 81 | unmet | unmet |
| 0.15 | d9 / 81 | unmet | unmet | unmet |

Interpretation:

- This turns B2 into an overhead comparison problem rather than only an error
  suppression problem.
- At high physical error rates, the current control distances are insufficient
  for stricter targets, which gives the next baseline a clear job: either
  extend distance, switch code family, or exploit a better noise model.
- Once a surface-code or LDPC baseline exists, the same target-volume table can
  compare code families at fixed target logical error.

## Rough Surface-Code Threshold-Law Estimate v0

Before the first circuit-level run, B2 used a rough analytic estimate as a
planning layer. It remains in the benchmark because it gives a target-volume
table over larger distances, but it is not the authoritative surface-code
baseline. It uses:

- Logical error model: `p_L = A * (p / p_th)^((d + 1) / 2)`.
- Threshold: `p_th = 0.01`.
- Prefactor: `A = 0.1`.
- Odd distances: 3 through 25.
- Physical-qubit proxy: rotated surface-code data+ancilla estimate
  `2*d*d - 1`.
- Rounds: `d`.

Result summary:

- Physical error rates checked: 0.001, 0.003, 0.005, 0.007, 0.009.
- Target combinations checked: 20.
- Met by available distances 3-25: 13.
- Unmet by available distances 3-25: 7.

Selected estimated minimum space-time volumes:

| Physical error | Target 1e-2 | Target 1e-3 | Target 1e-4 | Target 1e-5 |
|---:|---:|---:|---:|---:|
| 0.001 | d3 / 51 | d5 / 245 | d7 / 679 | d9 / 1449 |
| 0.003 | d3 / 51 | d7 / 679 | d11 / 2651 | d15 / 6735 |
| 0.005 | d7 / 679 | d13 / 4381 | d19 / 13699 | unmet |
| 0.007 | d13 / 4381 | d25 / 31225 | unmet | unmet |
| 0.009 | unmet | unmet | unmet | unmet |

Interpretation:

- The estimator gives B2 a first surface-code-shaped target-volume table using
  the same reporting interface as the repetition-code control baseline.
- It should not be used as evidence of a code or decoder improvement.
- Its main use is planning: it identifies the distance and physical-error
  regimes where a real Stim/PyMatching baseline should be prioritized.

## Stim/PyMatching Surface-Code Memory Baseline v0

B2 now has a first real surface-code memory baseline built on standard tools.
The runner generates Stim rotated surface-code memory circuits for X and Z
memory, converts the detector error model into a PyMatching decoder, samples
detection events, decodes observables, and reports logical failures plus
decoder runtime.

Configuration:

- Stim tasks: `surface_code:rotated_memory_x` and
  `surface_code:rotated_memory_z`.
- Distances: 3, 5, 7.
- Rounds: equal to distance.
- Physical error rates: 0.001, 0.003, 0.005, 0.007, 0.01.
- Shots per configuration: 3,000.
- Seed: 220627.
- Configurations: 30.
- Total shots: 90,000.

Result summary:

- Minimum observed logical error rate: 0 in the lowest-error sampled rows.
- Maximum observed logical error rate: 0.118.
- Nonincreasing logical-error trend with distance: 4 / 10 basis/error checks.
- Maximum PyMatching decoder runtime: about 1.47e-5 seconds per shot.

Interpretation:

- This closes the first B2 execution-board gap: B2 now has a Stim/PyMatching
  surface-code memory baseline instead of only a repetition fallback and an
  analytic threshold-law estimate.
- The small sweep is intentionally not a threshold claim. Several rows are
  shot-limited or non-monotone across distances, so the next run should expand
  shots, distances, and noise regimes before any code-improvement claim.
- The baseline is now strong enough to compare future searched code graphs,
  biased-noise schedules, or cross-layer B7 resource models against a standard
  decoder stack.

## Stim/PyMatching Target-Volume Baseline v0

The first surface-code target-volume table converts the circuit-level baseline
into the quantity B2 must eventually beat: minimum qubit-round volume at a
target logical error. To avoid over-claiming from 3,000-shot zero-failure rows,
the default criterion requires the Wilson 95% upper confidence bound to be
below the target.

Configuration:

- Source: `B2_stim_surface_code_memory_baseline_v0.json`.
- Criterion: Wilson 95% upper bound.
- Targets: 0.1, 0.05, 0.01, 0.001.
- Memory bases: X and Z.
- Physical error rates: 0.001, 0.003, 0.005, 0.007, 0.01.
- Target combinations: 40.

Result summary:

- Met combinations: 22.
- Unmet combinations: 18.
- Minimum reported volume for met rows: 78 qubit-rounds, using Stim's 26-qubit
  distance-3 rotated surface-code circuit for 3 rounds.
- The strict 0.001 target is not certified by the current 3,000-shot sweep
  under the Wilson-upper-bound criterion, even where observed failures are
  zero.

Interpretation:

- This table creates a fair comparison contract for the next B2 idea: a
  candidate schedule, biased-noise code, or small graph code must beat this
  baseline on target volume, not only on raw logical error.
- The Wilson criterion makes the next experiment obvious: increase shots and
  extend distances before making claims at 1e-3 or below.
- The table also exposes the overhead gap between repetition-code controls and
  surface-code memory circuits because the surface-code volume uses actual
  Stim circuit qubits times rounds.

## Phenomenological Decoder Fallback v0

B2 now has a first transparent decoder interface beyond final majority vote.
It is still a repetition-code memory model, not a surface-code or LDPC result.
The model uses independent data bit-flip errors and noisy syndrome
measurements across repeated rounds, then decodes the full syndrome history
with a small Viterbi/minimum-weight hidden-state decoder.

Configuration:

- Distances: 3, 5, 7.
- Rounds: equal to distance.
- Data error rates: 0.003, 0.005, 0.01, 0.02.
- Measurement error: equal to data error.
- Shots per configuration: 1,000.
- Seed: 220626.
- Configurations: 12.

Result summary:

- Improved configurations vs final-majority decoder: 2 / 12.
- Best relative reduction: 85.71%.
- Best configuration: distance 7, rounds 7, data/measurement error 0.02.
- In that best configuration, final-majority logical error was 0.007 while
  Viterbi syndrome-history decoding was 0.001.
- Maximum decoder runtime was about 1.02e-4 seconds per shot.

Interpretation:

- This establishes B2's decoder abstraction and runtime reporting without
  depending on Stim or PyMatching.
- Low-error configurations are shot-limited and often have zero failures, so
  the result should be read as an interface/prototype milestone rather than a
  threshold estimate.
- The next useful comparison is a real circuit-level surface-code memory
  baseline or a PyMatching-backed repetition/surface decoder.

## Limits

This baseline does **not** claim progress over surface code or LDPC codes. It
is a control harness. The next B2 milestone must introduce at least one of:

1. A larger Stim/PyMatching sweep with more shots, distances, and calibrated or
   hardware-motivated noise regimes.
2. Candidate small LDPC/subsystem graph inputs with an explicit syndrome model.
3. A biased-noise schedule or code variant that beats the surface-code baseline
   on target space-time volume.
4. A cross-layer B7 resource estimate that converts logical-error curves into
   physical qubit-time and factory-throughput requirements.

## Next Algorithmic Step

Build the first real B2 improvement comparison:

1. Expand the Stim/PyMatching baseline to distances 3-11 and increase shots in
   low-error regimes where zero-failure rows hide uncertainty.
2. Convert the circuit-level logical-error table into target logical error
   levels such as 1e-3, 1e-4, and 1e-5, then compare required space-time
   volume using Wilson upper bounds.
3. Introduce one candidate schedule, biased-noise variant, or small code graph
   and test it against the same decoder/reporting interface.
4. Only after the baseline is stable, test learned decoders or searched code
   graphs against it.

## Biased-Schedule Proxy Candidate v0.1

B2 now has a first candidate-comparison layer in
`../research/B2_biased_schedule_proxy.md`.

This is not yet a circuit-level biased-noise simulation. It is a parameterized
proxy that scales the existing Wilson/observed logical-error metrics from the
Stim/PyMatching surface-code baseline while explicitly charging qubit and round
overhead for three biased schedule variants.

Result summary:

- Same target-volume contract as the Stim surface-code table.
- Target combinations: 40.
- Baseline met targets: 22.
- Candidate met targets: 28.
- Candidate-only target hits: 6.
- Volume-improvement rows where baseline already met target: 0.

Interpretation:

- The proxy closes six Wilson-bounded feasibility gaps, so it gives B2 a
  concrete biased-schedule hypothesis to test.
- It does not yet prove low-overhead QEC improvement because it does not reduce
  volume on rows where the surface-code baseline already meets target.
- The next B2 milestone is a circuit-level biased-noise/schedule sweep with
  enough shots to validate or kill this proxy.

## Stim Biased-Schedule Circuit-Level Sweep v0.1

B2 now has the first real circuit-level follow-up to the proxy:
`../research/B2_stim_biased_schedule_sweep.md`.

This run uses Stim generated rotated-memory circuits and PyMatching decoding,
but changes operation-class noise parameters rather than merely scaling result
metrics. It tests three variants:

- Measurement/reset hardening: measurement and reset flip probabilities x0.5.
- Data-memory hardening: before-round data depolarization x0.5.
- Clifford-gate hardening: Clifford/CX depolarization x0.5.

Result summary:

- Configurations: 90.
- Total shots: 270,000.
- Same Wilson target-volume combinations: 40.
- Baseline met targets: 22.
- Candidate met targets: 26.
- Candidate-only target hits: 4.
- Volume-improvement rows where baseline already met target: 0.
- All four new target hits come from the Clifford-gate hardening variant.

Interpretation:

- The proxy was directionally useful but too optimistic: it predicted 6
  candidate-only hits, while the real circuit-level sweep produced 4.
- The useful lever is not measurement/reset-only or data-memory-only
  hardening; the current circuit-level evidence points at Clifford/CX-class
  error as the bottleneck.
- This is still not a B2 solution because no row has reduced target volume
  relative to the baseline. The next candidate must turn the Clifford-hardening
  signal into a fair same-hardware schedule, biased/correlated-noise code, or
  decoder/code co-design that beats the Wilson-bounded target-volume table.
