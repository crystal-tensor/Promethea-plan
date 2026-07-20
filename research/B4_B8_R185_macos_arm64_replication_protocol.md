# B4/B8/B10 R185 macOS arm64 Replication Protocol

- Status: `preregistered_design_unopened`
- Protocol payload hash: `bd2f5c9acb8dbfcb3c4f388ae33ca7bb7dbef4c170a176c6a721e8bb5322d961`
- Design contract payload hash: `c8f8b7e8012b64c90e49f76d218b9e4c7fcb565aa43be8ce8a55af8108fd3664`
- Scientific execution: unopened

## Heuristic Question

R184 preserved all 468 mappings and reached 0.771535x versus prefix plus 0.814726x versus BigUint on Linux x86-64. Does the same exact representation clear the unchanged integrity, compactness, and performance gates on macOS arm64, or was the apparent win architecture-specific?

## Frozen Cross-Architecture Pairing

The macOS arm64 matrix repeats the exact R184 Linux workload: `468` same-process BigUint/prefix/window triplets across `13` cells. All six arm orders appear `6` times per cell, so platform is changed without changing workload or scheduler position balance.

## Decision Boundary

The macOS build must preserve every expected mapping, stay at four compact limbs or fewer, remain at 64 bytes or fewer, and avoid fallback on the frozen workload. The same 0.90 window/prefix and 1.00 window/BigUint ceilings are retained. Cross-architecture transfer is accepted only if the committed Linux result and the new macOS result both pass H1-H4 without changing the patch, inputs, or thresholds.

## Claim Boundary

This is a preregistered classical compiler cross-architecture replication. It is not a universal architecture theorem, upstream Qiskit patch, full-domain performance theorem, production remedy, hardware result, quantum advantage, BQP separation, solved B4/B8/B10 frontier, or new credit.
