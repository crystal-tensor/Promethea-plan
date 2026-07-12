# B4/B8 R139 Lagos Complete-Ising Channel Attribution

## Result

- Source R138 group mean delta: `-0.01399989`
- Replayed full-noise mean delta: `-0.01399989`
- Gate-only mean delta: `-0.00033016`
- Readout-only mean delta: `-0.02365719`
- Noiseless sampled mean delta: `+0.00008690`
- Minimum exact semantic fidelity: `0.9999999999999984`
- Exact output-aware readout mean delta: `-0.02286062`
- Exact/sampled readout sign agreement: `8` / `8`
- Exact/sampled readout delta correlation: `0.98493343`
- Proxy says selected wins / exact readout says selected loses: `6` / `8`
- Attribution: `output_aware_readout_assignment_dominates_synthetic_regression`
- Phase replay: `2` / `2`
- New credit delta: `0`

R139 reuses the eight already revealed R138 seed pairs without selecting a new
seed or circuit. The same selected and automatic circuits are replayed under
full, gate-only, readout-only, and noiseless channels. It also removes final
measurements, reconstructs the exact classical output distribution from each
compiled circuit, and applies the backend readout matrices analytically using
the actual logical-to-physical measurement assignment.

## Channel Evidence

- `full`: mean selected/automatic `0.81120387` / `0.82520376`, delta `-0.01399989`, wins/losses `2/6`, bootstrap 95% `[-0.02310645, -0.00415060]`.
- `gate_only`: mean selected/automatic `0.92716231` / `0.92749247`, delta `-0.00033016`, wins/losses `3/5`, bootstrap 95% `[-0.00312635, +0.00285380]`.
- `readout_only`: mean selected/automatic `0.84882001` / `0.87247720`, delta `-0.02365719`, wins/losses `2/6`, bootstrap 95% `[-0.03775343, -0.00745905]`.
- `noiseless`: mean selected/automatic `0.99633397` / `0.99624707`, delta `+0.00008690`, wins/losses `5/3`, bootstrap 95% `[-0.00039808, +0.00056745]`.

The combined-any-error proxy ranks the selected route ahead in all eight rows,
but that proxy is output agnostic. The exact readout channel sees which logical
output bit lands on each physical readout channel and predicts the sampled
readout-only ranking in every row. The diagnostic therefore supports an
output-aware readout-assignment failure, not a semantic failure and not a raw
CX-count explanation.

## Requirements

- `P1` PASS: R138 source and the negative Lagos complete-Ising group are hash-bound
- `P2` PASS: the eight revealed R138 circuit and seed pairs are reused without reselection
- `P3` PASS: full, gate-only, readout-only, and noiseless channels cover all eight pairs
- `P4` PASS: the full-noise channel exactly replays all eight R138 deltas
- `P5` PASS: selected and automatic compiled circuits preserve the exact logical distribution
- `P6` PASS: gate-only, readout-only, and exact readout counterfactuals are materialized
- `P7` PASS: exact output-aware readout predicts all sampled readout ranking signs
- `P8` PASS: the readout-dominant attribution follows the fixed channel evidence
- `P9` PASS: both channel and attribution phase artifacts replay across a fresh process
- `P10` PASS: hardware causality, mitigation, repair, soundness, advantage, BQP, and credit remain excluded

## Claim Boundary

Supported: synthetic channel-ablation and exact output-aware readout attribution
for the R138 FakeLagosV2 complete-Ising negative group. Not supported: causal
hardware attribution, current calibration, mitigation performance, a repaired
mapping, independent verifier custody, protocol soundness, quantum advantage,
BQP separation, or new B10 credit.
