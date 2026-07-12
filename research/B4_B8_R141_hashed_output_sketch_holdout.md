# B4/B8 R141 Hashed Output Sketch Holdout

## Verdict

- Preregistered verdict: REJECT
- Contract SHA-256: 388fb1aa35ae98d2c5f624e34541832e8590481046b42af105e57be63d6a770f
- Selection agreement with R140 exact: 87 / 96
- Lagos selection agreement: 8 / 8
- Mean / maximum exact-score regret: 0.00004099 / 0.00197748
- Portfolio sketch-auto mean / bootstrap lower: +0.00386523 / +0.00213694
- Lagos sketch-auto mean / wins: -0.00355006 / 3 of 8
- Portfolio sketch-R140-exact mean: -0.00044153
- Four-arm rows / executions / shots: 96 / 384 / 1572864
- Conditions passed / failed: 9 / 1
- Phase replay: 4 / 4
- New credit delta: 0

The hidden pilot seed changes the sample sketch before each selection. The
selector receives samples and shared readout variates, never the full ideal
distribution or the R140 teacher score. Teacher scores are opened only after
selection to compute agreement and regret. All four noisy arms in a row share
one simulator seed.

## Acceptance Conditions

- A1 PASS: design, candidate pool, and QASM bindings remain exact; value [True, 96], threshold [True, 96].
- A2 PASS: all rows contain sample-only selection and four noisy arms; value [96, 12, 0], threshold [96, 12, 0].
- A3 PASS: Lagos selection matches R140 exact in hidden pilot blocks; value 8, threshold >= 7.
- A4 PASS: portfolio selection agreement with R140 exact; value 87, threshold >= 80.
- A5 PASS: maximum exact R140 score regret; value 0.0019774847695264164, threshold <= 0.005.
- A6 PASS: portfolio sketch-auto bootstrap lower bound; value 0.0021369426677347765, threshold >= -0.005.
- A7 FAIL: Lagos sketch-auto mean is nonnegative and wins at least half; value [-0.003550061697868895, 3], threshold ['>= 0', '>= 4'].
- A8 PASS: portfolio sketch-R140-exact noisy noninferiority; value -0.0004415306660382704, threshold >= -0.002.
- A9 PASS: phase replay and disclosed execution budget; value [384, 1572864], threshold [384, 1572864].
- A10 PASS: pilot acquisition, hardware, soundness, advantage, BQP, and credit claims remain false; value 0, threshold 0.

## Group Evidence

- FakeJakartaV2::dense_validation_complete_ising_n6: selection agreement 8/8, mean sketch-auto +0.00389708, mean sketch-exact +0.00000000.
- FakeJakartaV2::dense_validation_inverse_qft_n6: selection agreement 4/8, mean sketch-auto -0.00038655, mean sketch-exact -0.00022795.
- FakeJakartaV2::dense_validation_scrambled_qft_n6: selection agreement 8/8, mean sketch-auto +0.00006609, mean sketch-exact +0.00000000.
- FakeJakartaV2::dense_validation_xy_network_n6: selection agreement 5/8, mean sketch-auto +0.01586482, mean sketch-exact -0.00323988.
- FakeLagosV2::dense_validation_complete_ising_n6: selection agreement 8/8, mean sketch-auto -0.00355006, mean sketch-exact +0.00000000.
- FakeLagosV2::dense_validation_inverse_qft_n6: selection agreement 8/8, mean sketch-auto +0.00123571, mean sketch-exact +0.00000000.
- FakeLagosV2::dense_validation_scrambled_qft_n6: selection agreement 8/8, mean sketch-auto +0.00059642, mean sketch-exact +0.00000000.
- FakeLagosV2::dense_validation_xy_network_n6: selection agreement 6/8, mean sketch-auto +0.00604276, mean sketch-exact -0.00183055.
- FakeOslo::dense_validation_complete_ising_n6: selection agreement 8/8, mean sketch-auto +0.00906107, mean sketch-exact +0.00000000.
- FakeOslo::dense_validation_inverse_qft_n6: selection agreement 8/8, mean sketch-auto +0.00047755, mean sketch-exact +0.00000000.
- FakeOslo::dense_validation_scrambled_qft_n6: selection agreement 8/8, mean sketch-auto +0.00032658, mean sketch-exact +0.00000000.
- FakeOslo::dense_validation_xy_network_n6: selection agreement 8/8, mean sketch-auto +0.01275129, mean sketch-exact +0.00000000.

## Requirements

- P1 PASS: public contract and discussion precede challenge generation
- P2 PASS: all source and candidate identity bindings remain exact
- P3 PASS: secret commitment precedes rows and reveal follows complete rows
- P4 PASS: all twelve groups contain eight complete four-arm rows
- P5 PASS: 384 executions and 1,572,864 shots match the contract
- P6 PASS: selector receives samples and no full distribution values
- P7 PASS: all selected QASM hashes replay from the frozen pool
- P8 PASS: both portfolio bootstraps use 10,000 resamples
- P9 PASS: all four phase artifacts replay in a fresh process
- P10 PASS: scalable pilot acquisition, hardware, soundness, advantage, BQP, and credit remain excluded

## Claim Boundary

Supported: one preregistered synthetic four-arm holdout verdict for a
fixed-width sample-only mapping selector. Not supported: scalable pilot
acquisition, current calibration, real hardware, mitigation, independent
custody, protocol soundness, quantum advantage, BQP separation, solved
B4/B8/B10, or new credit.
