# B4/B8 R153 Independent Seed Replication Holdout

- Preregistered verdict: ACCEPT
- Groups / trial rows / executions: `3` / `96` / `288`
- Portfolio repaired-automatic mean / bootstrap lower: `+0.02595381` / `+0.02209900`
- Portfolio repaired-denominator mean / bootstrap lower: `+0.00327876` / `+0.00170832`
- Groups above -0.02 versus denominator: `3 / 3`
- Blocks above -0.03 versus denominator: `12 / 12`
- Maximum within-backend block spread: `0.00609251`
- Severe rows below -0.05: `0`
- Semantic passes: `6 / 6`
- Conditions passed / failed: `10` / `0`
- New credit delta: `0`

## Backend Evidence

- `FakeCasablancaV2`: repaired-denominator `-0.00337217`, repaired-auto `+0.01914513`, minimum `-0.01890548`, severe rows `0`.
- `FakeNairobiV2`: repaired-denominator `+0.00860058`, repaired-auto `+0.03624033`, minimum `-0.00638309`, severe rows `0`.
- `FakePerth`: repaired-denominator `+0.00460786`, repaired-auto `+0.02247596`, minimum `-0.00993766`, severe rows `0`.

## Independent Block Evidence

- `FakeCasablancaV2` block `0`: repaired-denominator `-0.00392132`, minimum `-0.00924198`, wins `1 / 8`.
- `FakeCasablancaV2` block `1`: repaired-denominator `-0.00390117`, minimum `-0.01048545`, wins `3 / 8`.
- `FakeCasablancaV2` block `2`: repaired-denominator `-0.00415281`, minimum `-0.00927409`, wins `1 / 8`.
- `FakeCasablancaV2` block `3`: repaired-denominator `-0.00151336`, minimum `-0.01890548`, wins `3 / 8`.
- `FakeNairobiV2` block `0`: repaired-denominator `+0.01053813`, minimum `+0.00313187`, wins `8 / 8`.
- `FakeNairobiV2` block `1`: repaired-denominator `+0.00928370`, minimum `-0.00340003`, wins `7 / 8`.
- `FakeNairobiV2` block `2`: repaired-denominator `+0.00444562`, minimum `-0.00638309`, wins `7 / 8`.
- `FakeNairobiV2` block `3`: repaired-denominator `+0.01013486`, minimum `-0.00475977`, wins `7 / 8`.
- `FakePerth` block `0`: repaired-denominator `+0.00680487`, minimum `-0.00156671`, wins `6 / 8`.
- `FakePerth` block `1`: repaired-denominator `+0.00526201`, minimum `+0.00005484`, wins `8 / 8`.
- `FakePerth` block `2`: repaired-denominator `+0.00135946`, minimum `-0.00383837`, wins `5 / 8`.
- `FakePerth` block `3`: repaired-denominator `+0.00500510`, minimum `-0.00993766`, wins `7 / 8`.

## Acceptance Conditions

- A1 PASS: contract, protocol, accepted R152 result, routes, denominators, and bindings remain exact; value True, threshold True.
- A2 PASS: groups, rows, executions, blocks, and same-seed arms; value [3, 96, 288, 12], threshold [3, 96, 288, 12].
- A3 PASS: all repaired and denominator routes retain semantics; value [6, 0.9999999999999956], threshold [6, 0.9999999999].
- A4 PASS: portfolio repaired versus automatic noninferiority; value [0.0259538061022732, 0.022098999777958688], threshold [-0.005, -0.01].
- A5 PASS: portfolio repaired versus strong denominator noninferiority; value [0.0032787576260107456, 0.0017083245076636334], threshold [-0.005, -0.015].
- A6 PASS: all groups above negative 0.02 versus denominator; value 3, threshold 3.
- A7 PASS: severe row regressions below negative 0.05; value 0, threshold 0.
- A8 PASS: Casablanca mean, independent block count, and within-backend block spread clear frozen floors; value [-0.003372165193721615, 12, 0.0060925088018477375], threshold [-0.02, 10, 0.08].
- A9 PASS: commitment, hidden rows, reveal, and transcript; value True, threshold True.
- A10 PASS: forbidden claims and credit remain false; value 0, threshold 0.

## Claim Boundary

Supported only if accepted: one preregistered independent hidden-seed
replication of the accepted R152 routes across four blocks per backend. Not
supported: causal repair, temporal transfer, real-device transfer, hardware
performance, general route-generation advantage, quantum advantage, BQP
separation, solved B4/B8/B10, or new credit.

## Replay Caveat

The first generation-to-replay comparison matched only `2/4` phase artifacts:
the fresh-automatic portfolio mean moved from `+0.02595600` to `+0.02595381`,
a change of about `2.2e-6`, while the repaired-denominator evidence and every
acceptance condition remained unchanged. The following full replay matched all
`96/96` trial rows from the preceding replay and all `4/4` phase artifacts.
The final P8 gate therefore passes, but the initial automatic-arm drift remains
an explicit execution-reproducibility caveat. The next gate must preregister
per-row automatic-circuit hashes and serial Aer execution before consuming new
hidden seeds.
