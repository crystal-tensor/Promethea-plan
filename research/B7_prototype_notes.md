# B7 Prototype Notes: Fault-Tolerance Co-Design v0.1

Last updated: 2026-06-13

Problem: **21. Architecture-level fault-tolerance co-design**

The seventh attack direction is initialized with a planning-level resource
model for fault-tolerant quantum computing. This is not a physical layout, not
a compiler, and not a published-resource-estimate reproduction. It is a
cross-layer accounting harness that exposes how code distance, magic-state
factory count, routing overhead, lattice-surgery schedule, and algorithmic
block reuse interact.

## Current Components

- Benchmark manifest: `../benchmarks/B7_fault_tolerance_codesign.yaml`
- Resource model: `../tools/b7_fault_tolerance_codesign.py`
- B1/B2 dependency-schedule bridge: `../tools/b7_dependency_schedule_bridge.py`
- First result: `../results/B7_fault_tolerance_codesign_v0.json`
- B1/B2 bridge result: `../results/B7_b1_b2_dependency_schedule_bridge_v0.json`

## Workloads

The v0 model compares two architecture configurations on three synthetic
planning workloads:

1. `chemistry_phase_estimation`
2. `factoring_2048_modular_arithmetic`
3. `hubbard_time_evolution`

The baseline is a serial-factory surface-code estimate. The candidate is a
co-designed layout with more parallel factories, lower routing and lattice
surgery overhead, modest cycle-time improvement, and explicit block-reuse
accounting.

## Metrics

For each workload/config pair, the model records:

- chosen code distance under a logical failure budget
- physical qubits
- data and factory qubits
- runtime cycles and seconds
- space-time volume
- bottleneck classification

The key comparison metric is space-time-volume reduction against the baseline.

## First Results

The first run produces 6 resource rows: 3 workloads times 2 configurations.

| Workload | Space-time-volume reduction | Baseline bottleneck | Candidate bottleneck |
|---|---:|---|---|
| `chemistry_phase_estimation` | 6.774x | factory | factory |
| `factoring_2048_modular_arithmetic` | 7.592x | factory | factory |
| `hubbard_time_evolution` | 7.230x | factory | factory |

Summary:

- Minimum space-time-volume reduction: 6.774x.
- Mean space-time-volume reduction: 7.199x.
- Workloads exceeding the first-pass 25% reduction threshold: 3 of 3.

Interpretation:

- The candidate improves mainly by increasing factory parallelism and reducing
  routing/lattice-surgery overhead.
- All workloads remain factory bottlenecked, which is useful because it shows
  the next model should focus on factory sizing, scheduling, and T-depth.
- The large reduction is a hypothesis-generating signal, not a resource claim;
  it must survive dependency-graph scheduling and published-baseline
  comparison.

## B1/B2 Dependency-Schedule Bridge v0

B7 now has a first bridge from actual B1 and B2 artifacts:

- B1 source: virtual-SWAP before/after routed metrics.
- B2 source: Stim/PyMatching surface-code target-volume table with Wilson
  upper-bound criterion.
- Selected B2 target row: physical error 0.001, target logical error 0.01,
  distance 3, X memory, 26 physical qubits, 3 rounds, volume 78.
- Workloads: aggregate 30-circuit portfolio plus five B1 circuits with large
  virtual-SWAP reductions.

Result summary:

| Workload | Space-time-volume reduction | Exposure reduction |
|---|---:|---:|
| `aggregate_30_circuits` | 1.321x | 1.485x |
| `qasmbench_interaction_exact/basis_trotter_n4.qasm` | 1.195x | 1.394x |
| `qasmbench_medium_exact/gcm_h6.qasm` | 1.319x | 1.535x |
| `qasmbench_medium_exact/qf21_n15.qasm` | 1.469x | 2.046x |
| `qasmbench_medium_exact/sat_n11.qasm` | 1.616x | 1.899x |
| `qasmbench_small/hhl_n7.qasm` | 1.202x | 1.421x |

Interpretation:

- The dependency bridge is much more conservative than the scalar v0 resource
  model: minimum space-time-volume reduction is 1.195x and mean reduction is
  1.354x.
- This is useful because it ties B7 to current B1/B2 evidence instead of
  relying only on hand-authored routing and factory assumptions.
- The bridge does not yet model physical patch layout, magic-state factories,
  lattice-surgery surgery ordering, or feed-forward.

## Limits

- The estimates are planning-level only.
- Factory throughput, routing penalties, and schedule parallelism are scalar
  assumptions, not layouts.
- The first dependency graph is a logical-layer bridge, not a lattice-surgery
  patch schedule.
- The B1/B2 bridge must be expanded to real workload DAGs and factory
  scheduling before it can support a serious claim.

## Next Algorithmic Step

Build the next real B7 comparison:

1. Replace logical-layer depth proxies with a real workload DAG for one
   chemistry or Hamiltonian-simulation circuit.
2. Add magic-state factory sizing variants and factory-throughput bottlenecks
   to the B1/B2 bridge.
3. Extend the B2 target row beyond distance 3 by increasing shots and distance
   sweeps.
4. Compare against at least one published workload resource estimate.
