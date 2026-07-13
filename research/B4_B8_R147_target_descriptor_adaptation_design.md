# B4/B8 R147 Target-Descriptor Foreign-Route Adaptation Design

- Targets / tasks / adaptation groups: `3` / `4` / `12`
- Foreign candidates: `24` (`2` per group)
- Target-specific routes in selector: `0`
- R146 hidden trial rows read: `0`
- Candidate semantic passes: `24 / 24`
- Holdout executed: `false`

## Frozen Selections

- `FakeJakartaV2` / `dense_validation_complete_ising_n6`: selected `FakeLagosV2`; combined/CX/readout proxies `0.455266` / `0.332734` / `0.183633`.
- `FakeJakartaV2` / `dense_validation_inverse_qft_n6`: selected `FakeOslo`; combined/CX/readout proxies `0.429517` / `0.304744` / `0.179463`.
- `FakeJakartaV2` / `dense_validation_scrambled_qft_n6`: selected `FakeLagosV2`; combined/CX/readout proxies `0.455755` / `0.341193` / `0.173894`.
- `FakeJakartaV2` / `dense_validation_xy_network_n6`: selected `FakeLagosV2`; combined/CX/readout proxies `0.518126` / `0.409734` / `0.183633`.
- `FakeLagosV2` / `dense_validation_complete_ising_n6`: selected `FakeOslo`; combined/CX/readout proxies `0.859528` / `0.482013` / `0.728811`.
- `FakeLagosV2` / `dense_validation_inverse_qft_n6`: selected `FakeOslo`; combined/CX/readout proxies `0.902191` / `0.540317` / `0.787226`.
- `FakeLagosV2` / `dense_validation_scrambled_qft_n6`: selected `FakeOslo`; combined/CX/readout proxies `0.845145` / `0.428979` / `0.728811`.
- `FakeLagosV2` / `dense_validation_xy_network_n6`: selected `FakeOslo`; combined/CX/readout proxies `0.877885` / `0.549706` / `0.728811`.
- `FakeOslo` / `dense_validation_complete_ising_n6`: selected `FakeJakartaV2`; combined/CX/readout proxies `0.368669` / `0.311083` / `0.083590`.
- `FakeOslo` / `dense_validation_inverse_qft_n6`: selected `FakeLagosV2`; combined/CX/readout proxies `0.356152` / `0.301526` / `0.078208`.
- `FakeOslo` / `dense_validation_scrambled_qft_n6`: selected `FakeLagosV2`; combined/CX/readout proxies `0.357551` / `0.303043` / `0.078208`.
- `FakeOslo` / `dense_validation_xy_network_n6`: selected `FakeJakartaV2`; combined/CX/readout proxies `0.438257` / `0.387017` / `0.083590`.

## Method Boundary

For each target snapshot and dense task, the selector recompiles only the two
foreign R143 route identities on the target. It selects the lowest combined
readout-and-CX exposure proxy from public target calibration metadata, with
fixed deterministic tie breaks. The target-specific R143 route is excluded
from selection and reserved as a holdout denominator. No R146 trial row is
read or used for tuning.

This design does not support a holdout improvement, temporal or cross-machine
transfer, real hardware, mitigation, soundness, quantum advantage, BQP
separation, a solved frontier, or new credit.
