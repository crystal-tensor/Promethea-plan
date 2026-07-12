# B4/B8 R133 Unseen Circuit-Family Holdout

## Result

- Unseen source circuits: `4`
- Backend/circuit groups: `12`
- Holdout compilations: `360`
- Groups with one route-exposure class: `12` / `12`
- Groups with one exact QASM hash: `12` / `12`
- Frozen constrained-QASM replay: `120` / `120`
- Wins/ties/losses vs automatic layout: `21/24/75`
- Groups with no automatic-baseline loss: `4` / `12`
- Fixed-mapping-gap losses: `46`
- Lookahead-policy-induced losses: `9`
- Deterministic generalization gate passed: `True`
- Automatic-baseline no-loss gate passed: `False`
- New credit delta: `0`

## Holdout Evidence

- `FakeJakartaV2` / `holdout_brickwork_n6`: route/QASM classes `1/1`; mean gain vs automatic `+0.000232`; wins/ties/losses `2/8/0`; mapping-gap/policy-induced losses `0/0`.
- `FakeJakartaV2` / `holdout_ghz_echo_n6`: route/QASM classes `1/1`; mean gain vs automatic `-0.030577`; wins/ties/losses `0/0/10`; mapping-gap/policy-induced losses `10/0`.
- `FakeJakartaV2` / `holdout_ring_phase_n6`: route/QASM classes `1/1`; mean gain vs automatic `-0.019023`; wins/ties/losses `0/0/10`; mapping-gap/policy-induced losses `0/0`.
- `FakeJakartaV2` / `holdout_star_phase_n6`: route/QASM classes `1/1`; mean gain vs automatic `-0.045444`; wins/ties/losses `0/0/10`; mapping-gap/policy-induced losses `6/0`.
- `FakeLagosV2` / `holdout_brickwork_n6`: route/QASM classes `1/1`; mean gain vs automatic `+0.002543`; wins/ties/losses `2/8/0`; mapping-gap/policy-induced losses `0/0`.
- `FakeLagosV2` / `holdout_ghz_echo_n6`: route/QASM classes `1/1`; mean gain vs automatic `-0.005831`; wins/ties/losses `2/0/8`; mapping-gap/policy-induced losses `8/0`.
- `FakeLagosV2` / `holdout_ring_phase_n6`: route/QASM classes `1/1`; mean gain vs automatic `-0.011370`; wins/ties/losses `0/0/10`; mapping-gap/policy-induced losses `5/4`.
- `FakeLagosV2` / `holdout_star_phase_n6`: route/QASM classes `1/1`; mean gain vs automatic `+0.008002`; wins/ties/losses `10/0/0`; mapping-gap/policy-induced losses `0/0`.
- `FakeOslo` / `holdout_brickwork_n6`: route/QASM classes `1/1`; mean gain vs automatic `+0.000956`; wins/ties/losses `2/8/0`; mapping-gap/policy-induced losses `0/0`.
- `FakeOslo` / `holdout_ghz_echo_n6`: route/QASM classes `1/1`; mean gain vs automatic `-0.010152`; wins/ties/losses `2/0/8`; mapping-gap/policy-induced losses `8/0`.
- `FakeOslo` / `holdout_ring_phase_n6`: route/QASM classes `1/1`; mean gain vs automatic `-0.032126`; wins/ties/losses `0/0/10`; mapping-gap/policy-induced losses `0/5`.
- `FakeOslo` / `holdout_star_phase_n6`: route/QASM classes `1/1`; mean gain vs automatic `-0.002608`; wins/ties/losses `1/0/9`; mapping-gap/policy-induced losses `9/0`.

R133 freezes four circuit families that were absent from R119-R132: star echo,
star phase, ring phase, and brickwork. It reuses only the already-selected R130
mapping associated with the parent star or path family and the already-selected
R132 `lookahead` policy. No policy or mapping is selected from these holdout rows.

Determinism generalizes, but baseline quality does not. The attribution ledger
compares the constrained route with both the same fixed mapping under Qiskit's
default router and the fully automatic layout, separating inherited mapping gaps
from losses introduced by the `lookahead` policy.

## Requirements

- `P1` PASS: R132 source and selected policy are hash-bound
- `P2` PASS: four unseen source circuit families are materialized
- `P3` PASS: fresh holdout seeds are disjoint and no holdout selection occurs
- `P4` PASS: all 12 groups retain one route-exposure class
- `P5` PASS: all 12 groups retain one exact QASM hash across seeds
- `P6` PASS: all 120 constrained circuits replay in a fresh process
- `P7` PASS: all holdout rows compare constrained, fixed-map, and automatic routes
- `P8` PASS: every automatic-baseline loss has a mapping-or-policy attribution
- `P9` PASS: verifier acceptance, mitigation, calibration, and hardware remain excluded
- `P10` PASS: no soundness, advantage, BQP, or new credit is claimed

## Claim Boundary

Supported: unseen circuit-family evidence that the R132 route policy remains
byte-reproducible while failing the automatic-layout no-loss criterion, with a
per-seed mapping-versus-policy loss attribution. Not supported: verifier
acceptance, causal hardware performance, current calibration, mitigation,
protocol soundness, quantum advantage, BQP separation, or new B10 credit.
