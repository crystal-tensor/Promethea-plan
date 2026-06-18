# B4 Prototype Notes: Verifiable Quantum Advantage Protocols v0.1

Last updated: 2026-06-13

Problem: **16. Verifiable quantum advantage protocols**

The fourth attack direction is now initialized with a toy hidden-trap
statistical protocol. This is not a quantum advantage claim. It is a
verification-soundness scaffold for asking whether embedded checks can reject
simple spoofing families while preserving high honest acceptance.

## Current Components

- Benchmark manifest: `../benchmarks/B4_verifiable_quantum_advantage.yaml`
- Trap protocol simulator: `../tools/b4_trap_protocol_sim.py`
- First result: `../results/B4_toy_trap_protocol_v0.json`

## Protocol Model

The v0 simulator treats each task as a sample with hidden trap checks. An
honest device passes each trap with probability `1 - honest_error_per_trap`.
Each adversary has a per-trap success rate and must pass every hidden trap in a
task. A batch is accepted when at least 80% of 64 tasks pass.

This is intentionally a statistical abstraction:

- It does not construct full random quantum circuits yet.
- It does not prove hardness of the underlying task distribution.
- It does not model tensor-network, stabilizer-rank, or learned generative
  spoofers at circuit level.
- It does quantify completeness, soundness, spoofing gap, and a Hoeffding-style
  sample-complexity proxy.

## First Results

The first run covers 36 configurations:

- Qubit counts: 16, 24, 32.
- Hidden trap counts: 2, 4, 8.
- Honest error per trap: 0.02.
- Trials per configuration: 20,000.
- Batch size: 64.
- Batch acceptance fraction: 0.8.
- Spoofing families tested: 4.

| Trap count | Batch completeness | Worst batch soundness |
|---:|---:|---:|
| 2 | 0.999999 | 2.277e-05 |
| 4 | 0.998873 | 3.929e-16 |
| 8 | 0.849536 | 1.007e-40 |

All four toy adversary families fail the current batch rule:

1. `uniform_random_spoofer`
2. `marginal_matching_spoofer`
3. `low_depth_surrogate_spoofer`
4. `partial_trap_leak_spoofer`

Interpretation:

- More traps sharply reduce soundness but also reduce honest completeness.
- The current best operating region is likely 2-4 traps for this toy noise
  model, because completeness remains near one while soundness is already
  small.
- The 8-trap setting is useful as a stress point but may be too brittle unless
  error correction, trap redundancy, or a softer acceptance rule is introduced.

## Limits

- No real trap circuit generator is implemented yet.
- No hidden-structure IQP, XEB, Hamiltonian invariant, or cross-device
  consistency task is instantiated.
- No classical simulator runtime is measured.
- The adversaries are scalar per-trap success models, not adaptive algorithms.
- The proof of usefulness is absent; this only tests a verification envelope.

## Next Algorithmic Step

Build the first circuit-level B4 comparison:

1. Implement a small exact-simulable hidden-trap circuit family.
2. Add adversary interfaces that consume public circuit metadata and produce
   output samples.
3. Compare uniform, marginal-matching, shallow surrogate, and partial-leak
   adversaries on exact small circuits.
4. Add a target-size regime where full distribution verification is unavailable
   but trap checks and cross-device invariants remain cheap.
5. Replace scalar per-trap adversary rates with measured pass rates from the
   implemented spoofers.
