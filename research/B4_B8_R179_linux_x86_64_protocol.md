# B4/B8/B10 R179 Linux x86-64 Protocol

- Status: `preregistered_unopened`
- Protocol payload hash: `4c4899bb0e65de1387585ae034b884bb5508b5d01bf7775d670b65a7360b536d`
- Contract payload hash: `1612b5140aecb82024f8db34a12df87fcdcc9e4989f013a82eac3b4cae6cd96e`
- Execution: unopened until a public Discussion is created

## Research Question

After R178 built and identified the correct Linux binary but let the source checkout shadow its isolated import overlay, can a cwd-isolated Ubuntu x86-64 import pass and reproduce the full R176 exact-selection result inside the same frozen local performance gates?

## Frozen Matrix

The workflow fixes `39` isolated Linux x86-64 workers, `2400` recorded calls, and `624` warmups across source f64, R175 BigUint, and R176 fixed exact scoring.

## Performance Gates

Fixed/source must remain at most `3.0` per cell and `2.5` aggregate; fixed/BigUint must remain at most `0.9` aggregate; peak RSS must remain at most `1.25` relative to source.

## Claim Boundary

This is a preregistered Ubuntu x86-64 build and replay contract. It does not claim an upstream patch, production remedy, confirmed Qiskit bug, successful cross-platform result, hardware evidence, quantum advantage, BQP separation, solved B4/B8/B10, or new credit before execution.
