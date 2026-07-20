# B4/B8/B10 R180 Execution-Boundary Failure

- Status: `build_accepted_scientific_replay_unopened`
- GitHub Actions run: [29761452207](https://github.com/crystal-tensor/Prometheus-plan/actions/runs/29761452207)
- Scientific workers started: `0/52`
- Recorded calls: `0/3200`
- New credit: `0`

## What Passed

The source-bound Ubuntu x86-64 build completed all 12 declared steps. The official Qiskit 2.4.1 source was checked out at commit `0fd015a22b84c9082173597a5d2304dc0aaec08c`, the frozen R180 patch applied, `cargo fmt`, `cargo check`, four active-limb unit tests, `git diff --check`, the release build, ELF validation, and the isolated Python import smoke all passed. The imported accelerator hash is `985f7e9b02f4c663d16f122cc25cee363470d8b3d7beae1863e46664f1c66aa8`.

## What Failed

The replay stopped before creating any worker. The preregistration contract used one absence list for both build artifacts and scientific result artifacts. Once the build correctly created the Linux accelerator, the replay guard rejected that same accelerator as pre-existing evidence.

This is an orchestration-contract failure. It says nothing about the correctness or performance of the active-limb exact scorer because no frozen case, warmup, timing cell, mapping decision, simulation, or shot was executed.

## Claim Boundary

R180 contributes a reproducible Linux build and a negative workflow-state result only. It does not establish an exact-selection outcome, performance result, Qiskit remedy, hardware result, quantum advantage, BQP separation, solved B4/B8/B10 frontier, or new credit.

## Next Gate

R181 must separate build outputs from the scientific `result_paths_must_be_absent` list, bind the corrected executor before public dispatch, and rerun the unchanged 52-worker, 3,200-recorded-call matrix plus its Qiskit-free independent oracle.
