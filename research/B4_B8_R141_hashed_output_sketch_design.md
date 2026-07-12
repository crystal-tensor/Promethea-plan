# B4/B8 R141 Hashed Output Sketch Design

## Design Result

- R140 candidate rows replayed: `1536`
- Sketch width: `256` buckets
- Pilot samples / readout replicas: `4096` / `8`
- Canonical selection agreement with R140 exact score: `10 / 12`
- Pressure selection agreement: `171 / 192`
- Lagos complete-Ising pressure agreement: `16 / 16`
- Mean / maximum exact-score regret: `0.00006503` / `0.00207426`
- Selected QASM replay: `12 / 12`
- Holdout rows read during selection: `0`
- New credit delta: `0`

The selector receives only integer output samples, shared uniform readout
variates, candidate readout-error vectors, and compiled CX exposure. It hashes
ideal and synthetically readout-corrupted samples into a fixed 256-bin sketch,
estimates Hellinger fidelity in that sketch, and multiplies it by the existing
CX-success proxy. Its memory is fixed by the sketch width rather than `2^n`.

The current pilot samples are generated from a statevector-backed design
oracle. Therefore this result establishes a scalable *scoring interface*, not
scalable end-to-end pilot acquisition.

## Group Evidence

- `FakeJakartaV2` / `dense_validation_complete_ising_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `16 / 16`, selected mapping `[1, 3, 0, 2, 5, 6]`.
- `FakeJakartaV2` / `dense_validation_inverse_qft_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `9 / 16`, selected mapping `[0, 2, 3, 1, 6, 5]`.
- `FakeJakartaV2` / `dense_validation_scrambled_qft_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `16 / 16`, selected mapping `[5, 0, 3, 6, 2, 1]`.
- `FakeJakartaV2` / `dense_validation_xy_network_n6`: sketch/exact selection agreement `False`, exact-score regret `0.00012670`, pressure agreement `10 / 16`, selected mapping `[0, 1, 3, 2, 5, 6]`.
- `FakeLagosV2` / `dense_validation_complete_ising_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `16 / 16`, selected mapping `[1, 3, 2, 0, 5, 4]`.
- `FakeLagosV2` / `dense_validation_inverse_qft_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `16 / 16`, selected mapping `[4, 5, 2, 0, 3, 1]`.
- `FakeLagosV2` / `dense_validation_scrambled_qft_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `16 / 16`, selected mapping `[5, 0, 1, 4, 2, 3]`.
- `FakeLagosV2` / `dense_validation_xy_network_n6`: sketch/exact selection agreement `False`, exact-score regret `0.00052800`, pressure agreement `8 / 16`, selected mapping `[6, 4, 5, 3, 1, 0]`.
- `FakeOslo` / `dense_validation_complete_ising_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `16 / 16`, selected mapping `[1, 3, 2, 0, 5, 4]`.
- `FakeOslo` / `dense_validation_inverse_qft_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `16 / 16`, selected mapping `[4, 5, 0, 2, 3, 1]`.
- `FakeOslo` / `dense_validation_scrambled_qft_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `16 / 16`, selected mapping `[5, 0, 1, 4, 2, 3]`.
- `FakeOslo` / `dense_validation_xy_network_n6`: sketch/exact selection agreement `True`, exact-score regret `0.00000000`, pressure agreement `16 / 16`, selected mapping `[2, 0, 5, 4, 1, 3]`.

## Requirements

- `R1` PASS: all 1,536 frozen R140 candidates are replayed
- `R2` PASS: selector memory is fixed at 256 histogram buckets
- `R3` PASS: selector consumes samples rather than a full distribution table
- `R4` PASS: Lagos target matches R140 exact selection in all 16 pressure blocks
- `R5` PASS: at least 160 of 192 pressure selections match R140
- `R6` PASS: maximum exact-score regret remains at most 0.005
- `R7` PASS: all twelve selected QASM files replay
- `R8` PASS: teacher scores are used only after selection for evaluation
- `R9` PASS: no noisy acceptance holdout is opened during design
- `R10` PASS: pilot acquisition, hardware, advantage, BQP, and credit claims remain false

## Claim Boundary

Supported: a frozen fixed-width, sample-only reranker over the 1,536 R140
candidates, plus deterministic pressure tests against the already frozen R140
exact score. Not supported: scalable pilot acquisition, unseen noisy holdout
acceptance, current calibration, hardware, mitigation, soundness, quantum
advantage, BQP separation, or new B10 credit.
