# B4/B8/B10 R186 Full VF2 Workflow Protocol

- Status: `preregistered_design_unopened`
- Protocol payload hash: `7e4629295f6a0ecc986a6812f38c839f5da8b65b98cf91c248ef1d2ae747a8ac`
- Design contract payload hash: `3e4c24252f9e340ae221a9ae76e88eb10e3d488f4e79ce2513df1e5a0ef76dc6`
- Scientific execution: unopened

## Heuristic Question

R184/R185 made exact VF2 scoring faster inside the Rust search entry point. Does that advantage survive the actual Python VF2Layout plus PassManager boundary on both Linux x86-64 and macOS arm64, or does orchestration overhead erase it?

## Why This Gate Exists

R184 and R185 timed the complete Rust VF2 search-and-score entry point. They did not time Qiskit's Python `VF2Layout.run`, target resolution, pass configuration, `Layout` construction, property-set writes, or `PassManager` scheduling. R186 measures both surfaces and refuses to call a Rust-core gain a compiler-workflow gain unless the latter survives independently.

## Frozen Matrix

Each architecture runs `468` rows across `13` cells. Every row contains BigUint, prefix, and window exact arms on both the direct accelerator surface and the Python PassManager surface. The 12 arm/surface schedules each occur three times per cell, yielding `2808` measured and `936` warmup calls per platform.

## Decision Boundary

All six outputs must equal the frozen expected mapping in every row. On Linux x86-64 and macOS arm64 separately, window/BigUint must be at most 1.00 on both surfaces. At least 10% of the direct-surface fractional saving must remain after the PassManager boundary. No threshold may be relaxed after timing data open.

## Claim Boundary

This is a source-faithful external monkeypatch harness around Qiskit 2.4.1, not an upstream integration or full transpilation benchmark. It uses zero circuit simulations, zero quantum shots, and zero real-backend rows. It cannot establish a production remedy, hardware result, quantum advantage, BQP separation, solved B4/B8/B10 frontier, or new credit.
