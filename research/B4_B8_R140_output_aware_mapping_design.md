# B4/B8 R140 Output-Aware Mapping Design

## Design Result

- R136 candidates replayed: `1536`
- Candidate QASM hashes matched: `1536`
- Backend/task groups: `12`
- Changed selections: `4`
- Groups with improved output-aware score: `3`
- Groups with improved exact readout fidelity: `2`
- Minimum selected exact semantic fidelity: `0.9999999999999976`
- Frozen selected QASM replay: `12` / `12`
- R138/R139 validation rows read during selection: `0`
- New credit delta: `0`

The parameter-free score is

`(1 - cx_any_error_proxy) * exact_output_aware_readout_fidelity`.

The first factor uses the historical compiled CX route. The second factor
applies the physical readout channel induced by the candidate measurement map
to the exact logical output distribution. There is no fitted weight. R138 and
R139 are used only to motivate the score and define the later falsification
target; their validation rows are not loaded by this design program.

## Group Selection Evidence

- `FakeJakartaV2` / `dense_validation_complete_ising_n6`: old/new exact-readout `0.99109604` / `0.99109604`, old/new CX-any-error `0.31423155` / `0.31423155`, score improvement `+0.00000000`, changed `False`.
- `FakeJakartaV2` / `dense_validation_inverse_qft_n6`: old/new exact-readout `1.00000000` / `1.00000000`, old/new CX-any-error `0.31257218` / `0.31257218`, score improvement `+0.00000000`, changed `True`.
- `FakeJakartaV2` / `dense_validation_scrambled_qft_n6`: old/new exact-readout `1.00000000` / `1.00000000`, old/new CX-any-error `0.30796030` / `0.30796030`, score improvement `+0.00000000`, changed `False`.
- `FakeJakartaV2` / `dense_validation_xy_network_n6`: old/new exact-readout `0.85361259` / `0.85361259`, old/new CX-any-error `0.39205781` / `0.39205781`, score improvement `+0.00000000`, changed `False`.
- `FakeLagosV2` / `dense_validation_complete_ising_n6`: old/new exact-readout `0.85186761` / `0.85595748`, old/new CX-any-error `0.51115694` / `0.42900958`, score improvement `+0.07231395`, changed `True`.
- `FakeLagosV2` / `dense_validation_inverse_qft_n6`: old/new exact-readout `1.00000000` / `1.00000000`, old/new CX-any-error `0.41603319` / `0.41603319`, score improvement `+0.00000000`, changed `False`.
- `FakeLagosV2` / `dense_validation_scrambled_qft_n6`: old/new exact-readout `1.00000000` / `1.00000000`, old/new CX-any-error `0.51333610` / `0.41600191`, score improvement `+0.09733419`, changed `True`.
- `FakeLagosV2` / `dense_validation_xy_network_n6`: old/new exact-readout `0.39097472` / `0.40235459`, old/new CX-any-error `0.60464488` / `0.61290320`, score improvement `+0.00117632`, changed `True`.
- `FakeOslo` / `dense_validation_complete_ising_n6`: old/new exact-readout `0.99738687` / `0.99738687`, old/new CX-any-error `0.28714779` / `0.28714779`, score improvement `+0.00000000`, changed `False`.
- `FakeOslo` / `dense_validation_inverse_qft_n6`: old/new exact-readout `1.00000000` / `1.00000000`, old/new CX-any-error `0.28714779` / `0.28714779`, score improvement `+0.00000000`, changed `False`.
- `FakeOslo` / `dense_validation_scrambled_qft_n6`: old/new exact-readout `1.00000000` / `1.00000000`, old/new CX-any-error `0.28545081` / `0.28545081`, score improvement `+0.00000000`, changed `False`.
- `FakeOslo` / `dense_validation_xy_network_n6`: old/new exact-readout `0.92423279` / `0.92423279`, old/new CX-any-error `0.36477889` / `0.36477889`, score improvement `+0.00000000`, changed `False`.

## Requirements

- `P1` PASS: R136 result and all 1,536 route realizations are hash-bound
- `P2` PASS: all 1,536 candidate QASM programs replay their R136 hashes
- `P3` PASS: the score has no fitted weight and uses only CX and exact readout terms
- `P4` PASS: R138 and R139 validation outcomes are not loaded during selection
- `P5` PASS: all 12 groups expose 128 candidates and one frozen selection
- `P6` PASS: all frozen selections preserve the exact logical output distribution
- `P7` PASS: the output-aware objective changes the Lagos complete-Ising selection
- `P8` PASS: all 12 selected QASM files replay in a fresh process
- `P9` PASS: no noisy holdout or current calibration is consumed during design
- `P10` PASS: repair, hardware, soundness, advantage, BQP, and credit remain unclaimed

## Claim Boundary

Supported: a frozen, replayable, parameter-free output-aware reranking of the
1,536 R136 route realizations. Not supported: noisy validation acceptance,
Lagos repair, scalable exact-output estimation, current calibration, hardware,
mitigation, protocol soundness, quantum advantage, BQP separation, or new B10
credit.
