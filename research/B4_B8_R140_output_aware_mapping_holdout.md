# B4/B8 R140 Output-Aware Mapping Holdout

## Verdict

- Preregistered verdict: REJECT
- Contract SHA-256: d11f07b5d5a25c81a3f89a1b03297deb1a80486ce3613d1c17d3071e651a7cb5
- Three-arm trial rows: 96
- Simulated executions / shots: 288 / 1179648
- Lagos new / old / automatic mean fidelity: 0.81916489 / 0.81813431 / 0.81576333
- Lagos new-auto / new-old: +0.00340156 / +0.00103058
- Lagos new wins vs automatic: 4 / 8
- Portfolio new-auto mean / bootstrap lower: +0.00582195 / +0.00405345
- Portfolio new-old mean: +0.00024811
- Groups above -0.01 vs old: 12 / 12
- Severe new-old regressions below -0.05: 0
- Conditions passed / failed: 9 / 1
- Phase replay: 4 / 4
- New credit delta: 0

The R140 design and thresholds were public before the hidden secret was
generated. Each fresh trial uses one transpiler seed and one shared simulator
seed for the frozen R140 circuit, frozen R136 circuit, and fresh automatic
compilation. The output-aware candidate is never recompiled during validation.

## Acceptance Conditions

- A1 PASS: the R140 design, 12 selected QASM files, and immutable contract remain hash-bound; value 12, threshold 12 and bound.
- A2 PASS: all 12 groups contain eight complete new/old/automatic paired trials; value [96, 12], threshold [96, 12].
- A3 PASS: the targeted Lagos complete-Ising group is repaired against automatic compilation; value 0.0034015551454047027, threshold >= 0.0.
- A4 FAIL: the targeted Lagos complete-Ising repair materially improves on the R136 selection; value 0.0010305772700850424, threshold >= 0.01.
- A5 PASS: the targeted Lagos complete-Ising route wins at least half of hidden trials against automatic compilation; value 4, threshold >= 4.
- A6 PASS: portfolio noninferiority against automatic compilation survives paired uncertainty; value 0.004053452345122788, threshold >= -0.005.
- A7 PASS: the output-aware portfolio does not materially regress against the frozen R136 portfolio; value 0.0002481102923812016, threshold >= -0.002.
- A8 PASS: cross-group repair is not purchased by broad regressions; value 12, threshold >= 11.
- A9 PASS: large new-versus-old row regressions remain rare and all design cost is disclosed; value [0, 1536], threshold ['<= 2', 1536].
- A10 PASS: hardware, scalable-output, soundness, advantage, BQP, and credit claims remain false; value 0, threshold forbidden claims false.

## Group Evidence

- FakeJakartaV2::dense_validation_complete_ising_n6: new-auto +0.00957695, new-old +0.00000000, wins vs auto 7/8, wins vs old 0/8.
- FakeJakartaV2::dense_validation_inverse_qft_n6: new-auto +0.00012262, new-old +0.00001728, wins vs auto 4/8, wins vs old 3/8.
- FakeJakartaV2::dense_validation_scrambled_qft_n6: new-auto +0.00023252, new-old +0.00000000, wins vs auto 5/8, wins vs old 0/8.
- FakeJakartaV2::dense_validation_xy_network_n6: new-auto +0.02634000, new-old +0.00000000, wins vs auto 8/8, wins vs old 0/8.
- FakeLagosV2::dense_validation_complete_ising_n6: new-auto +0.00340156, new-old +0.00103058, wins vs auto 4/8, wins vs old 4/8.
- FakeLagosV2::dense_validation_inverse_qft_n6: new-auto +0.00018973, new-old +0.00000000, wins vs auto 5/8, wins vs old 0/8.
- FakeLagosV2::dense_validation_scrambled_qft_n6: new-auto +0.00089500, new-old +0.00031764, wins vs auto 7/8, wins vs old 6/8.
- FakeLagosV2::dense_validation_xy_network_n6: new-auto +0.00331611, new-old +0.00161182, wins vs auto 7/8, wins vs old 5/8.
- FakeOslo::dense_validation_complete_ising_n6: new-auto +0.01122764, new-old +0.00000000, wins vs auto 8/8, wins vs old 0/8.
- FakeOslo::dense_validation_inverse_qft_n6: new-auto +0.00014650, new-old +0.00000000, wins vs auto 5/8, wins vs old 0/8.
- FakeOslo::dense_validation_scrambled_qft_n6: new-auto +0.00002009, new-old +0.00000000, wins vs auto 4/8, wins vs old 0/8.
- FakeOslo::dense_validation_xy_network_n6: new-auto +0.01439466, new-old +0.00000000, wins vs auto 8/8, wins vs old 0/8.

## Requirements

- P1 PASS: public design and contract hashes precede challenge generation
- P2 PASS: all 12 new QASM bindings remain exact
- P3 PASS: secret commitment precedes rows and reveal follows all rows
- P4 PASS: all 12 groups contain eight complete three-arm trials
- P5 PASS: 288 executions and 1,179,648 shots match the contract
- P6 PASS: each three-arm trial shares one simulator seed
- P7 PASS: both portfolio bootstraps use 10,000 resamples
- P8 PASS: the verdict follows unchanged A1-A10 gates
- P9 PASS: all four phase artifacts replay in a fresh process
- P10 PASS: scalability, hardware, mitigation, custody, soundness, advantage, BQP, and credit remain excluded

## Claim Boundary

Supported: one preregistered historical synthetic-noise holdout verdict for the
parameter-free output-aware mapper across twelve fixed groups. Not supported:
scalable exact-output estimation, current calibration, real hardware,
mitigation, independent verifier custody, protocol soundness, quantum
advantage, BQP separation, or new B10 credit.
