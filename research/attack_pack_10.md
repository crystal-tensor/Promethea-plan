# First 10 Quantum Attack Directions v0.1

Last updated: 2026-06-13

These are not claims of solved problems. They are candidate research programs
where a one-year team could plausibly produce new algorithms, protocols,
benchmarks, or negative results that move the frontier.

## 1. Hardware-Aware Quantum Circuit Compression

**Problem ID:** 25

**Core hypothesis:** Treat quantum compilation as a constrained probabilistic
program synthesis problem over hardware-native operations, not as a fixed
sequence of local peephole optimizations.

**Method sketch:**

- Build an intermediate representation that preserves commutation structure,
  Pauli frames, magic-state cost, routing constraints, and noise model.
- Use a hybrid search loop: tensor-network equivalence checks, SAT/SMT
  fragments for exact subcircuits, and learned proposal distributions.
- Optimize for a multi-objective score: logical depth, T-count/T-depth,
  two-qubit error exposure, idle time, and verification cost.

**One-year milestone:** Demonstrate 20-50% resource reduction on 3 benchmark
families: quantum chemistry ansatzes, QEC syndrome extraction, and arithmetic
circuits used in Shor-style algorithms.

## 2. Low-Overhead Quantum Error-Correcting Codes

**Problem ID:** 22

**Core hypothesis:** Combine quantum LDPC codes with learned decoders and
hardware topology constraints to find codes whose practical overhead is lower
than surface-code baselines for specific platforms.

**Method sketch:**

- Search code families using Tanner graph generation constrained by hardware
  connectivity and measurement schedules.
- Train decoders that exploit correlated noise while preserving certifiable
  fallback decoders.
- Evaluate under circuit-level noise, leakage, biased noise, and measurement
  errors.

**One-year milestone:** Produce a reproducible code+decoder benchmark beating
surface-code overhead in at least one realistic noise regime.

## 3. Quantum Algorithms for Molecular Reaction Dynamics

**Problem ID:** 49

**Core hypothesis:** Near-term fault-tolerant quantum algorithms can target
reaction observables directly, avoiding full wavefunction reconstruction.

**Method sketch:**

- Select 3 hard reaction classes: transition-metal catalysis, nitrogen
  fixation motif, and photochemical conical intersections.
- Formulate observable-first phase estimation or amplitude estimation
  circuits.
- Compare resource estimates against best classical coupled-cluster,
  DMRG, selected CI, and tensor-network methods.

**One-year milestone:** Publish resource estimates and prototype circuits for
one reaction where the quantum path has a credible asymptotic or constant-factor
advantage.

## 4. Verifiable Quantum Advantage Protocols

**Problem ID:** 16

**Core hypothesis:** Verification should be designed into the task distribution
itself: useful quantum tasks can include hidden checks, trap instances, or
cross-device consistency constraints.

**Method sketch:**

- Create task families with tunable classical hardness and embedded checkable
  substructure.
- Combine interactive proofs, randomized compiling, and cross-entropy-like
  statistics with adversarial robustness.
- Test protocols on simulators and available quantum cloud backends.

**One-year milestone:** A verification protocol with quantified soundness and
completeness for a task beyond brute-force classical reproduction at target
sizes.

## 5. Strongly Correlated Matter via Hybrid Quantum-Tensor Solvers

**Problem ID:** 38

**Core hypothesis:** Quantum processors should be used as entanglement kernels
inside tensor-network or embedding algorithms, not as monolithic simulators.

**Method sketch:**

- Use quantum subroutines to solve impurity or plaquette problems embedded in
  classical many-body solvers.
- Couple with tensor networks, DMFT-like loops, or variational Monte Carlo.
- Benchmark on Hubbard, frustrated spin, and electron-phonon models.

**One-year milestone:** Beat a classical baseline on accuracy-per-resource for
one constrained but scientifically meaningful model family.

## 6. High-Temperature Superconductivity Search

**Problem ID:** 37

**Core hypothesis:** The path is not direct material discovery; it is to build
quantum-simulation-derived descriptors that improve candidate ranking for
strongly correlated superconductors.

**Method sketch:**

- Identify descriptors tied to pairing mechanisms and competing phases.
- Generate descriptor estimates from hybrid solvers on simplified Hamiltonians.
- Couple descriptors to active learning over materials databases.

**One-year milestone:** Produce a ranked candidate-generation pipeline and
retrospective validation against known unconventional superconductors.

## 7. Architecture-Level Fault-Tolerance Co-Design

**Problem ID:** 21

**Core hypothesis:** Fault tolerance should be co-designed across code,
compiler, layout, scheduling, and algorithm, because isolated optimization
leaves large resource savings unrealized.

**Method sketch:**

- Build a resource-estimation stack that connects algorithms to code choices
  and hardware constraints.
- Study co-optimization of lattice surgery, magic-state factories, routing,
  and algorithmic block structure.
- Target chemistry, arithmetic, and Hamiltonian simulation workloads.

**One-year milestone:** End-to-end resource reductions over a published
baseline for at least two workloads.

## 8. Classical Verification of Quantum Outputs

**Problem ID:** 30

**Core hypothesis:** Instead of verifying the full output distribution, verify
task-relevant invariants and randomly chosen projections that are hard to fake.

**Method sketch:**

- Define invariant families for sampling, simulation, and optimization tasks.
- Use randomized measurements, shadows, and property testing.
- Quantify adversarial spoofing resistance.

**One-year milestone:** A benchmark suite where honest quantum outputs pass
with high probability and known spoofing strategies fail.

## 9. Quantum PCP and Local Hamiltonian Hardness

**Problem ID:** 17

**Core hypothesis:** Product-test and entanglement-robust gap amplification
methods can be explored computationally to generate candidate counterexamples
or proof patterns.

**Method sketch:**

- Build a small-instance laboratory for local Hamiltonian gap behavior.
- Search for transformations preserving locality while amplifying promise gaps.
- Formalize promising patterns in proof assistants where possible.

**One-year milestone:** Either a new restricted-case theorem or a public
database of counterexample candidates that rules out a family of approaches.

## 10. Mapping the Boundary of BQP

**Problem ID:** 11

**Core hypothesis:** Progress may come from fine-grained, average-case, and
interactive-verification boundaries rather than a single grand separation.

**Method sketch:**

- Catalog problem families with plausible BQP advantage.
- Build reductions among sampling, Hamiltonian simulation, hidden subgroup,
  and linear-algebra tasks.
- Identify where data loading, precision, or verification erases claimed
  advantage.

**One-year milestone:** A taxonomy paper plus formal reductions or separations
for at least two restricted families.

## Shared Infrastructure Needed

- Benchmark repository for circuits, Hamiltonians, noise models, and classical
  baselines.
- Resource estimator for logical and physical costs.
- Literature map with claims, assumptions, and reproducibility status.
- Protocol for grading each result: theorem, benchmark, resource estimate,
  simulation, or experimental demonstration.
