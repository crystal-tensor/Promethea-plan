# B4/B8/B10 R181 Integrated Active-Limb Superaccumulator Replay

- Status: `active_limb_superaccumulator_rejected_on_linux_matrix`
- Classification: `active_limb_cost_attribution_failed`
- Requirements: `16/18`
- Payload hash: `7a5f055dae4184e01e5c8bb8a18de7b9d09cde8db6b2415b24cb6c1ab9a0b38f`

## Research Question

Can an active-limb fixed-width exact binary64 superaccumulator preserve exact selection while reversing R179's Linux full-width scan penalty?

## Result

The matrix executes `4032` direct Qiskit calls, including `3200` recorded calls and `832` warmups across `52` isolated processes. Source, BigUint, fixed-34, and active-limb policies match `800/800`, `800/800`, `800/800`, and `800/800` outcomes. Active-limb agrees with BigUint on `800/800`, preserves R169 on `192/192`, repairs R170 on `192/192`, repairs R172 on `192/192`, and repairs R160 on `224/224`.

## Performance

Aggregate active/source is `2.074254`, active/BigUint is `1.093070`, and active/fixed-34 is `0.971310`. The worst active/source cell ratio is `2.396897` and the worst active/source peak-RSS ratio is `1.001689`. The same run records fixed-34/BigUint `1.125356` to test whether the R179 reversal reproduces.

## Claim Boundary

This is a bounded, source-bound Linux software experiment. It is not an upstream-accepted or production Qiskit patch, a confirmed Qiskit bug, broad graph-scale evidence, hardware evidence, quantum advantage, BQP separation, solved B4/B8/B10, or new credit.
