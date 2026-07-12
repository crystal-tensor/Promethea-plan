# B4/B8 R138 Post-Commit Statistical Challenge

## Verdict

- Preregistered verdict: `ACCEPT`
- Contract SHA-256: `caee4c8fe9d8fb7b12482e714b3aa29a23f8531bfa4a9682e56e84438a288ab0`
- Public preregistration commit: `17012a4a5706eca8ec3c650c3e2a72bbfa82c80c`
- Paired trial rows: `96`
- Shots per circuit / total shots: `4096` / `786432`
- Mean selected / automatic Hellinger fidelity: `0.85347188` / `0.84992130`
- Mean paired delta: `+0.00355058`
- Paired bootstrap 95% interval: `[+0.00137647, +0.00577807]`
- Selected wins/ties/losses: `64/0/32`
- Groups above -0.025: `12` / `12`
- Severe regressions below -0.05: `0`
- Phase artifact replay: `4` / `4`
- New credit delta: `0`

The R138 contract and thresholds were public before the challenge secret was
generated. The secret deterministically derives fresh automatic-transpiler,
paired simulator, and bootstrap seeds. Each frozen selected QASM is compared
with a fresh optimization-level-3 automatic compilation under the matching
historical FakeBackend noise model and the same simulator seed within each
pair.

## Acceptance Conditions

- `A1` PASS: all committed artifacts and the R137 source remain hash-bound; value `12`, threshold `12 and source binding valid`.
- `A2` PASS: the hidden challenge expands to every preregistered group and trial; value `[96, 12]`, threshold `[96, 12]`.
- `A3` PASS: selected mean Hellinger fidelity is noninferior on the paired holdout; value `0.0035505846509601906`, threshold `>= -0.005`.
- `A4` PASS: paired bootstrap uncertainty remains inside the preregistered margin; value `0.001376466732817468`, threshold `>= -0.0125`.
- `A5` PASS: noninferiority is not concentrated in only a few backend-task groups; value `12`, threshold `>= 10`.
- `A6` PASS: large row-level regressions remain rare; value `0`, threshold `<= 2`.
- `A7` PASS: the complete R136 selection cost remains charged; value `[1536, 1656]`, threshold `[1536, 1656]`.
- `A8` PASS: forbidden scientific claims remain false regardless of the verdict; value `0`, threshold `all forbidden claims false and new_credit_delta == 0`.

## Group Evidence

- `FakeJakartaV2::dense_validation_complete_ising_n6`: mean delta `+0.009512`, wins/ties/losses `6/0/2`, minimum `-0.007551`.
- `FakeJakartaV2::dense_validation_inverse_qft_n6`: mean delta `-0.000148`, wins/ties/losses `4/0/4`, minimum `-0.001584`.
- `FakeJakartaV2::dense_validation_scrambled_qft_n6`: mean delta `+0.000075`, wins/ties/losses `4/0/4`, minimum `-0.000937`.
- `FakeJakartaV2::dense_validation_xy_network_n6`: mean delta `+0.022992`, wins/ties/losses `8/0/0`, minimum `+0.000365`.
- `FakeLagosV2::dense_validation_complete_ising_n6`: mean delta `-0.014000`, wins/ties/losses `2/0/6`, minimum `-0.033838`.
- `FakeLagosV2::dense_validation_inverse_qft_n6`: mean delta `-0.000438`, wins/ties/losses `1/0/7`, minimum `-0.001167`.
- `FakeLagosV2::dense_validation_scrambled_qft_n6`: mean delta `+0.000606`, wins/ties/losses `5/0/3`, minimum `-0.000779`.
- `FakeLagosV2::dense_validation_xy_network_n6`: mean delta `+0.002618`, wins/ties/losses `7/0/1`, minimum `-0.006079`.
- `FakeOslo::dense_validation_complete_ising_n6`: mean delta `+0.010408`, wins/ties/losses `8/0/0`, minimum `+0.002510`.
- `FakeOslo::dense_validation_inverse_qft_n6`: mean delta `+0.000541`, wins/ties/losses `6/0/2`, minimum `-0.000115`.
- `FakeOslo::dense_validation_scrambled_qft_n6`: mean delta `+0.000143`, wins/ties/losses `6/0/2`, minimum `-0.000735`.
- `FakeOslo::dense_validation_xy_network_n6`: mean delta `+0.010298`, wins/ties/losses `7/0/1`, minimum `-0.000229`.

## Requirements

- `P1` PASS: public contract hash and publication precede challenge generation
- `P2` PASS: R137 payload, commitment, and all 12 artifact hashes remain bound
- `P3` PASS: challenge secret is committed before rows and revealed after all rows
- `P4` PASS: all 12 groups and 96 paired hidden-seed rows execute
- `P5` PASS: 192 circuit executions and 786,432 shots match the contract
- `P6` PASS: every selected/automatic pair shares its simulator seed
- `P7` PASS: the fixed Hellinger and 10,000-resample bootstrap statistics are materialized
- `P8` PASS: the verdict is computed from unchanged A1-A8 conditions
- `P9` PASS: all four phase artifacts replay identically in a fresh process
- `P10` PASS: hardware, custody, soundness, advantage, BQP, and new credit remain excluded

## Claim Boundary

Supported: one publicly preregistered post-commit synthetic-noise statistical
noninferiority verdict for the fixed 12-artifact R136 bundle under the frozen
R138 design. Not supported: current calibration, real hardware, mitigation,
independent verifier custody, protocol or cryptographic soundness, sampling
hardness, quantum advantage, BQP separation, or new B10 credit.
