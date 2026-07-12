# B4/B8 R143 Successive-Halving LCB Design

## Design Result

- Fixed schedule: `8 -> 4 -> 2 -> 1` over `4 + 4 + 4` seed increments
- Charged executions: `816` versus R142 `1728`
- Execution reduction: `52.78%`
- Selection agreement with R142: `10 / 12`
- Mean / maximum full-budget LCB regret: `0.00010310` / `0.00098866`
- Lagos selection agreement: `True`
- Lagos full-budget LCB: `+0.00523438`
- R142 holdout rows read during selection: `0`
- Selected OpenQASM 3 replay: `12 / 12`
- New credit delta: `0`

The schedule evaluates all eight candidates on four seeds, keeps four, adds
four seeds, keeps two, adds four final seeds, and selects one. Automatic
baseline executions are shared once per used seed. The algorithm is replayed
from R142 design rows only; hidden R142 rows are not loaded.

## Group Evidence

- `FakeJakartaV2` / `dense_validation_complete_ising_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[3, 1, 5, 2, 0, 6]`.
- `FakeJakartaV2` / `dense_validation_inverse_qft_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[0, 2, 3, 5, 1, 6]`.
- `FakeJakartaV2` / `dense_validation_scrambled_qft_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[5, 3, 1, 6, 2, 0]`.
- `FakeJakartaV2` / `dense_validation_xy_network_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[0, 1, 3, 2, 5, 6]`.
- `FakeLagosV2` / `dense_validation_complete_ising_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[5, 3, 6, 4, 1, 0]`.
- `FakeLagosV2` / `dense_validation_inverse_qft_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[4, 5, 0, 2, 3, 1]`.
- `FakeLagosV2` / `dense_validation_scrambled_qft_n6`: matches R142 `False`, full-budget LCB regret `0.00024855`, selected mapping `[5, 0, 1, 4, 2, 3]`.
- `FakeLagosV2` / `dense_validation_xy_network_n6`: matches R142 `False`, full-budget LCB regret `0.00098866`, selected mapping `[6, 4, 5, 3, 1, 0]`.
- `FakeOslo` / `dense_validation_complete_ising_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[3, 1, 5, 0, 2, 4]`.
- `FakeOslo` / `dense_validation_inverse_qft_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[2, 1, 4, 6, 3, 5]`.
- `FakeOslo` / `dense_validation_scrambled_qft_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[5, 2, 1, 4, 0, 3]`.
- `FakeOslo` / `dense_validation_xy_network_n6`: matches R142 `True`, full-budget LCB regret `0.00000000`, selected mapping `[0, 2, 1, 3, 5, 4]`.

## Requirements

- `R1` PASS: all 96 R142 shortlist rows are replayed
- `R2` PASS: the fixed 8-to-4-to-2-to-1 schedule uses twelve seeds per finalist
- `R3` PASS: charged execution count is 816
- `R4` PASS: execution reduction exceeds fifty percent
- `R5` PASS: at least ten of twelve selections match R142
- `R6` PASS: maximum full-budget LCB regret remains below 0.001
- `R7` PASS: Lagos selection matches accepted R142
- `R8` PASS: all selected QASM files replay with exact semantics
- `R9` PASS: R142 holdout rows remain unread and no fresh holdout runs
- `R10` PASS: live savings, cross-calibration, hardware, advantage, BQP, and credit claims remain false

## Claim Boundary

Supported: a frozen counterfactual execution schedule that reduces the R142
design denominator by more than half while preserving low full-budget LCB
regret. Not supported: fresh hidden acceptance, live wall-clock savings,
cross-calibration transfer, hardware, soundness, quantum advantage, BQP
separation, solved B4/B8/B10, or new credit.
