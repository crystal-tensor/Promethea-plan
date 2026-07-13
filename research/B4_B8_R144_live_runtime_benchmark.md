# B4/B8 R144 Live Runtime Benchmark

- Preregistered verdict: ACCEPT
- Strategy order: `['full', 'halving']`
- Full execution-loop seconds: `61.331846`
- Halving execution-loop seconds: `28.694975`
- Runtime reduction: `53.21%`
- Execution reduction: `52.78%`
- Halving/full per-execution ratio: `0.990771`
- Full selection replay: `12 / 12`
- Halving selection replay: `12 / 12`
- Shared setup / warmup seconds: `5.875736` / `0.272216`
- Conditions passed / failed: `10 / 0`
- New credit delta: `0`

## Acceptance Conditions

- A1 PASS: protocol and source bindings remain exact; value True, threshold True.
- A2 PASS: full and halving execution counts; value [1728, 816], threshold [1728, 816].
- A3 PASS: full strategy reproduces R142 selections; value 12, threshold 12.
- A4 PASS: halving strategy reproduces R143 selections; value 12, threshold 12.
- A5 PASS: execution-loop runtime reduction; value 0.532135805603889, threshold >= 0.30.
- A6 PASS: halving/full per-execution runtime ratio; value 0.9907712351917647, threshold 0.5 to 2.0.
- A7 PASS: strategy order follows secret; value ['full', 'halving'], threshold ['full', 'halving'].
- A8 PASS: identical circuits, seeds, shots, and snapshots; value True, threshold True.
- A9 PASS: measurement transcript hashes verify; value 5b8f91e5f319e6250e1a0ceef2b1fb8c498c7ede89cf83546dc7fc29fdd0c459, threshold bound.
- A10 PASS: calibration, hardware, billing, advantage, BQP, and credit claims false; value 0, threshold 0.

## Claim Boundary

Supported: one preregistered matched local execution-loop timing comparison on
the current machine. Not supported: repeated-order confidence, cross-machine
transfer, cross-calibration transfer, hardware or cloud billing savings,
soundness, quantum advantage, BQP separation, or new credit.
