# B4/B8 R125 Historical QPU Snapshot Replay

## Summary

- Target: `T-B4-002z/T-B8-003ad/T-B10-009r`
- Upstream target: `T-B4-002y/T-B8-003ac/T-B10-009q`
- Method: `b4_b8_r125_historical_snapshot_replay_v0`
- Status: `preregistered_historical_qpu_snapshot_replay_boundary`
- Public preregistration: https://github.com/crystal-tensor/Prometheus-plan/discussions/126
- Contract SHA-256: `547bef430ce85ea9052d791edd939e554b4a72f67dcabbb61169c7e02a675716`
- Historical snapshots: `FakeOslo, FakeJakartaV2, FakeLagosV2`
- Seed blocks per snapshot: `5`
- Trials per block/snapshot/task: `16`
- Total trial rows: `480`
- Control / candidate shots: `4096` / `8192`
- Global preregistered verdict: `REJECT`
- Fail-to-pass / pass-to-fail transitions: `38` / `6`

- `FakeOslo` / `4096`: pooled point `0.6375`, pooled Wilson lower `0.5281`, minimum leave-one-block-out lower `0.4715`, blocks above floor `1/5`.
- `FakeOslo` / `8192`: pooled point `0.8625`, pooled Wilson lower `0.7703`, minimum leave-one-block-out lower `0.7179`, blocks above floor `3/5`.
- `FakeOslo` decision: `REJECT`; A1=PASS, A2=FAIL, A3=FAIL, A4=FAIL, A5=PASS
- `FakeJakartaV2` / `4096`: pooled point `0.6250`, pooled Wilson lower `0.5155`, minimum leave-one-block-out lower `0.4715`, blocks above floor `0/5`.
- `FakeJakartaV2` / `8192`: pooled point `0.8000`, pooled Wilson lower `0.6995`, minimum leave-one-block-out lower `0.6487`, blocks above floor `2/5`.
- `FakeJakartaV2` decision: `REJECT`; A1=PASS, A2=FAIL, A3=FAIL, A4=FAIL, A5=PASS
- `FakeLagosV2` / `4096`: pooled point `0.0000`, pooled Wilson lower `0.0000`, minimum leave-one-block-out lower `0.0000`, blocks above floor `0/5`.
- `FakeLagosV2` / `8192`: pooled point `0.0000`, pooled Wilson lower `0.0000`, minimum leave-one-block-out lower `0.0000`, blocks above floor `0/5`.
- `FakeLagosV2` decision: `REJECT`; A1=FAIL, A2=FAIL, A3=FAIL, A4=FAIL, A5=PASS

R125 uses frozen IBM QPU system snapshots from Qiskit IBM Runtime fake
backends. Every randomized-measurement circuit is transpiled to the snapshot
topology before Aer applies snapshot-derived noise. These are historical
properties for local testing, not current calibration data or hardware jobs.

## Requirements

- `P1` PASS: contract matches the publicly posted SHA-256
- `P2` PASS: public preregistration predates snapshot replay
- `P3` PASS: contract binds the accepted R124 payload
- `P4` PASS: Qiskit IBM Runtime version matches the software contract
- `P5` PASS: all frozen snapshot hashes match the preregistration
- `P6` PASS: R125 root seeds are disjoint from R123 and R124
- `P7` PASS: all compiled circuits preserve logical classical-bit order
- `P8` PASS: all trial rows are transpiled and preserve paired evidence
- `P9` PASS: all holdout schedules have unique hashes
- `P10` PASS: block, leave-one-out, and transition ledgers are complete
- `P11` PASS: all five preregistered conditions are evaluated per snapshot
- `P12` PASS: historical snapshots are not mislabeled as current or hardware evidence
- `P13` PASS: no soundness, advantage, BQP, or new-credit claim is promoted

## Claim Boundary

Supported: a preregistered local Aer replay driven by frozen historical IBM QPU
snapshot properties. Not supported: current calibrated backend evidence,
provider access, hardware execution, independent transcript evidence, protocol
or cryptographic soundness, sampling hardness, quantum advantage, BQP
separation, or B10 credit.
