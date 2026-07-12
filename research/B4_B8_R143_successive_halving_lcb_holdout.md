# B4/B8 R143 Successive-Halving LCB Holdout

## Verdict

- Preregistered verdict: ACCEPT
- Charged design executions: 816 versus R142 1,728
- Lagos R143-auto mean / wins: +0.00833417 / 5 of 8
- Lagos R143-R142 mean: +0.00000000
- Portfolio R143-auto mean / bootstrap lower: +0.00836707 / +0.00591163
- Portfolio R143-R142 mean: -0.00020420
- Groups above -0.01 versus R142: 12 / 12
- Conditions passed / failed: 10 / 0
- Phase replay: 4 / 4
- New credit delta: 0

## Acceptance Conditions

- A1 PASS: bindings exact and charged design executions at most 864; value [True, 816], threshold [True, '<= 864'].
- A2 PASS: all groups contain eight complete three-arm rows; value [96, 12], threshold [96, 12].
- A3 PASS: Lagos R143-auto mean nonnegative; value 0.008334167103553058, threshold >= 0.
- A4 PASS: Lagos R143 wins at least half; value 5, threshold >= 4.
- A5 PASS: Lagos R143-R142 noninferiority; value 0.0, threshold >= -0.002.
- A6 PASS: portfolio R143-auto bootstrap lower; value 0.005911626534927596, threshold >= -0.005.
- A7 PASS: portfolio R143-R142 mean; value -0.0002042029622800924, threshold >= -0.002.
- A8 PASS: groups avoid broad R142 regression; value 12, threshold >= 11.
- A9 PASS: execution and shot budget; value [288, 1179648], threshold [288, 1179648].
- A10 PASS: live savings, calibration, hardware, soundness, advantage, BQP, and credit false; value 0, threshold 0.

## Group Evidence

- FakeJakartaV2::dense_validation_complete_ising_n6: R143-auto +0.01256459, R143-R142 +0.00000000, wins 7/8.
- FakeJakartaV2::dense_validation_inverse_qft_n6: R143-auto +0.00035156, R143-R142 +0.00000000, wins 7/8.
- FakeJakartaV2::dense_validation_scrambled_qft_n6: R143-auto -0.00042048, R143-R142 +0.00000000, wins 1/8.
- FakeJakartaV2::dense_validation_xy_network_n6: R143-auto +0.02938264, R143-R142 +0.00000000, wins 8/8.
- FakeLagosV2::dense_validation_complete_ising_n6: R143-auto +0.00833417, R143-R142 +0.00000000, wins 5/8.
- FakeLagosV2::dense_validation_inverse_qft_n6: R143-auto +0.00039403, R143-R142 +0.00000000, wins 6/8.
- FakeLagosV2::dense_validation_scrambled_qft_n6: R143-auto +0.00094932, R143-R142 +0.00010487, wins 7/8.
- FakeLagosV2::dense_validation_xy_network_n6: R143-auto +0.00958958, R143-R142 -0.00255531, wins 7/8.
- FakeOslo::dense_validation_complete_ising_n6: R143-auto +0.00811995, R143-R142 +0.00000000, wins 7/8.
- FakeOslo::dense_validation_inverse_qft_n6: R143-auto +0.00005678, R143-R142 +0.00000000, wins 4/8.
- FakeOslo::dense_validation_scrambled_qft_n6: R143-auto +0.00008548, R143-R142 +0.00000000, wins 4/8.
- FakeOslo::dense_validation_xy_network_n6: R143-auto +0.03099720, R143-R142 +0.00000000, wins 8/8.

## Requirements

- P1 PASS: public preregistration precedes challenge
- P2 PASS: all artifact bindings exact
- P3 PASS: commitment and reveal order valid
- P4 PASS: 96 complete rows
- P5 PASS: 288 executions and 1,179,648 shots
- P6 PASS: shared simulator seeds
- P7 PASS: 10,000 bootstrap resamples
- P8 PASS: unchanged A1-A10 verdict
- P9 PASS: phase replay
- P10 PASS: claim exclusions remain false

## Claim Boundary

Supported: one preregistered synthetic hidden-seed verdict for the R143
successive-halving portfolio and its charged execution ledger. Not supported:
live wall-clock savings, cross-calibration transfer, hardware, soundness,
quantum advantage, BQP separation, solved B4/B8/B10, or new credit.
