# B4/B8 R128 Transpiler-In-The-Loop Layout Ranking

## Result

- Retained R127 candidates: `60`
- Candidate compilations: `300`
- Default-layout compilations: `30`
- Static-rank-one layouts replaced: `3` / `6`
- Groups beating mean default exposure: `5` / `6`
- Groups winning at least 4/5 seeds: `1` / `6`
- Routing-survival gate passed: `False`
- Acceptance holdout executed: `False`
- New credit delta: `0`

## Per-Group Evidence

- `FakeJakartaV2` / `private_bundle_ghz_n6`: static rank `1` -> mapping `[1, 2, 3, 5, 6, 0]`; mean exposure selected/static/default `0.2415/0.2415/0.2317`; delta vs static/default `0.0000/-0.0098`; selected seed wins `1/5`; mean CX selected/default `14.0/11.0`.
- `FakeJakartaV2` / `private_bundle_graph_n6`: static rank `2` -> mapping `[2, 1, 0, 3, 5, 6]`; mean exposure selected/static/default `0.2116/0.2146/0.2139`; delta vs static/default `0.0030/0.0022`; selected seed wins `3/5`; mean CX selected/default `8.0/8.0`.
- `FakeLagosV2` / `private_bundle_ghz_n6`: static rank `1` -> mapping `[3, 0, 1, 4, 5, 6]`; mean exposure selected/static/default `0.7365/0.7365/0.7605`; delta vs static/default `0.0000/0.0240`; selected seed wins `2/5`; mean CX selected/default `14.0/11.0`.
- `FakeLagosV2` / `private_bundle_graph_n6`: static rank `1` -> mapping `[6, 5, 4, 3, 1, 0]`; mean exposure selected/static/default `0.7026/0.7026/0.7111`; delta vs static/default `0.0000/0.0085`; selected seed wins `5/5`; mean CX selected/default `8.0/8.0`.
- `FakeOslo` / `private_bundle_ghz_n6`: static rank `9` -> mapping `[3, 5, 4, 0, 1, 2]`; mean exposure selected/static/default `0.1585/0.1732/0.1603`; delta vs static/default `0.0147/0.0018`; selected seed wins `2/5`; mean CX selected/default `11.0/11.0`.
- `FakeOslo` / `private_bundle_graph_n6`: static rank `2` -> mapping `[0, 1, 2, 3, 5, 4]`; mean exposure selected/static/default `0.1321/0.1352/0.1344`; delta vs static/default `0.0032/0.0024`; selected seed wins `3/5`; mean CX selected/default `8.0/8.0`.

The selection rule is fixed before inspection: minimize mean compiled combined
exposure over five declared transpiler seeds, then worst exposure, mean CX count,
static rank, and mapping. The automatic-layout baseline uses the same circuit,
backend snapshot, optimization level, and seed. R125 acceptance rows are not read.

## Gate

The routing-survival gate requires every selected layout to beat the automatic
layout's mean and worst compiled exposure and to win at least four of five seeds.
Passing this design gate would authorize preregistration of a new disjoint
layout/readout holdout; it would not itself count as verifier or B10 credit.

## Requirements

- `P1` PASS: R127 source is hash-bound and all 60 retained candidates are consumed
- `P2` PASS: five declared transpiler seeds are used for every retained candidate
- `P3` PASS: automatic-layout baselines use the same five seeds for all six groups
- `P4` PASS: selection follows the preregistered mean-worst-CX-static-rank order
- `P5` PASS: selected layouts are never worse in mean than static rank one
- `P6` PASS: all 30 selected circuit artifacts preserve logical measurement order
- `P7` PASS: routing-survival acceptance rule is evaluated for every group
- `P8` PASS: R125 acceptance rows, holdout execution, and mitigation remain excluded
- `P9` PASS: historical snapshots remain separate from current and hardware evidence
- `P10` PASS: no soundness, advantage, BQP, or new credit is claimed

## Claim Boundary

Supported: deterministic, same-condition transpiler-loop ranking of the 60
predeclared R127 candidates against automatic layout. Not supported: acceptance
holdout performance, readout mitigation, current calibration, provider access,
hardware execution, protocol soundness, quantum advantage, BQP separation, or
new B10 credit.
