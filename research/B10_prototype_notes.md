# B10 Prototype Notes: Mapping the Boundary of BQP v0.1

Last updated: 2026-06-15

Problem: **11. Boundary of BQP**

The tenth attack direction is initialized with a BQP-boundary reduction graph.
This is not a complexity-theory theorem. It is a planning artifact that tracks
where proposed quantum advantages are preserved, where they become fragile, and
which assumptions must be made explicit before a theorem or benchmark claim is
credible.

## Current Components

- Benchmark manifest: `../benchmarks/B10_bqp_boundary_map.yaml`
- Graph builder: `../tools/b10_bqp_boundary_graph.py`
- Formal theorem target builder: `../tools/b10_formal_theorem_targets.py`
- B10-T1 proof-attempt builder: `../tools/b10_t1_negative_boundary_proof.py`
- B10-T1 source-backed boundary builder:
  `../tools/b10_t1_source_backed_boundaries.py`
- B10-T1 numerical denominator builder:
  `../tools/b10_t1_numerical_denominator_table.py`
- B10-T1 D5 observable denominator builder:
  `../tools/b10_t1_d5_observable_denominator_table.py`
- B10-T1 D5 B3 molecular observable builder:
  `../tools/b10_t1_d5_b3_molecular_observable_table.py`
- B10-T1 D5 B3 reaction observable builder:
  `../tools/b10_t1_d5_b3_reaction_observable_table.py`
- B10-T1 D5 B3 correlated reference builder:
  `../tools/b10_t1_d5_b3_correlated_reference_table.py`
- B10-T1 D5 B3 FCI reference builder:
  `../tools/b10_t1_d5_b3_fci_reference_table.py`
- First result: `../results/B10_bqp_boundary_graph_v0.json`
- Formal theorem targets: `../results/B10_formal_theorem_targets_v0.json`
- B10-T1 proof attempt: `../results/B10_t1_negative_boundary_proof_v0.json`
- B10-T1 source-backed baselines:
  `../results/B10_t1_source_backed_boundaries_v0.json`
- B10-T1 numerical denominator table:
  `../results/B10_t1_numerical_denominator_table_v0.json`
- B10-T1 D5 observable denominator table:
  `../results/B10_t1_d5_observable_denominator_table_v0.json`
- B10-T1 D5 B3 molecular observable table:
  `../results/B10_t1_d5_b3_molecular_observable_table_v0.json`
- B10-T1 D5 B3 reaction observable table:
  `../results/B10_t1_d5_b3_reaction_observable_table_v0.json`
- B10-T1 D5 B3 correlated reference table:
  `../results/B10_t1_d5_b3_correlated_reference_table_v0.json`
- B10-T1 D5 B3 FCI reference table:
  `../results/B10_t1_d5_b3_fci_reference_table_v0.json`

## Graph Scope

The v0 graph covers families such as:

- period finding and hidden subgroup problems
- Hamiltonian simulation and phase-estimation observables
- amplitude estimation
- quantum linear algebra
- random-circuit and IQP sampling
- QAOA-style optimization
- quantum machine learning
- interactive verification

Each edge records whether the reduction is expected to preserve advantage and
which failure modes can erase that advantage.

## Metrics

- node count
- edge count
- advantage-preserving edge count
- fragile edge count
- failure-mode counts
- restricted theorem target count

## First Results

The first graph has:

| Metric | Value |
|---|---:|
| Nodes | 12 |
| Edges | 14 |
| Connected components | 2 |
| Advantage-preserving edges | 8 |
| Fragile edges | 6 |
| Restricted theorem / negative-boundary targets | 11 |

Top failure modes:

1. `data_loading`
2. `oracle_construction`
3. `protocol_overhead`
4. `noise`
5. `measurement_gap`

Interpretation:

- The graph separates canonical speedups from fragile application claims.
- Data loading and readout failures dominate the negative-boundary targets for
  quantum linear algebra and quantum machine learning.
- Verification edges connect directly to B4/B8, while simulation edges can be
  connected to B3/B5 in the next version.
- The immediate theory work has moved one step forward: two restricted theorem
  targets now have explicit input, promise, output, verifier, cost-accounting,
  and proof-obligation models.

## Formal Theorem Targets v0

The first formal target package is in
`../research/B10_formal_theorem_targets.md`. It does not prove a theorem; it
defines what would have to be proved or refuted.

Targets:

1. `B10-T1 linear_systems_data_loading_negative_boundary`
   - Type: negative boundary.
   - Purpose: prevent HHL-style claims from hiding state preparation,
     block-encoding, condition-number, or readout costs.
   - Dependencies: B3, B5, B10.
2. `B10-T2 sampling_advantage_verification_layer_target`
   - Type: restricted advantage preservation.
   - Purpose: connect sampling-advantage claims to B4/B8 verification only
     when leakage, challenge refresh, protocol overhead, and adaptive spoofers
     are explicit.
   - Dependencies: B4, B8, B10.

Result summary:

- Target count: 2.
- Target types: negative boundary and restricted advantage preservation.
- Validation errors: 0.
- Status: formal model ready, not proved.

## B10-T1 Negative-Boundary Proof Attempt v0

The first proof-pressure artifact is in
`../research/B10_t1_negative_boundary_proof.md`.

Result:

- Status:
  `negative_boundary_accounting_lemma_proved_under_explicit_io_model_not_bqp_separation`.
- Proof result: restricted negative-boundary accounting lemma.
- Theorem/corollary count: 2.
- Validation errors: 0.
- Explicitly not a BQP/classical separation.

What it proves:

- In an explicit input/output model, a linear-system claim has end-to-end
  runtime at least the cost of explicit input ingestion, state preparation,
  block-encoding construction or invocation, and output writing.
- Therefore full-vector HHL-style tasks, or tasks that hide Omega(n) loading
  or readout costs, cannot claim polylog(n) end-to-end exponential speedup from
  the quantum subroutine alone.

What remains admissible:

- Conditional HHL-style advantage for succinctly specified or honestly charged
  access models and small observable outputs, with kappa, epsilon, and
  classical baselines declared.

Open obligations:

- Literature links have been added for HHL/QLSA, dequantization, CG, and
  LSQR denominator families.
- Five concrete classical denominator baselines have been instantiated.
- The dequantization and sampling-access boundary is partly scoped, but still
  needs a separate theorem note.

## B10-T1 Source-Backed Boundaries v0

The source-backed boundary note is in
`../research/B10_t1_source_backed_boundaries.md`.

Result:

- Status:
  `source_backed_denominator_baselines_instantiated_not_publishable_theorem`.
- Source anchors: 6.
- Denominator baselines: 5.
- Boundary checks: 4.
- Validation errors: 0.
- Explicitly not a BQP/classical separation.

What it adds:

- HHL and improved QLSA are treated as state/observable-output algorithms
  unless a full-vector output contract is explicitly declared and charged.
- Explicit sparse SPD, general sparse least-squares, succinct-oracle,
  low-rank sampling-access, and B3/B5 physics-observable regimes now have
  separate denominator baselines.
- Dequantization papers are elevated from background caveats to a required
  comparison class whenever sample/query access is assumed.

## B10-T1 Numerical Denominator Table v0

The runnable denominator table is in
`../research/B10_t1_numerical_denominator_table.md`.

Result:

- Status:
  `numerical_denominator_table_instantiated_not_quantum_speedup_claim`.
- Denominator families: 2.
- Total instances: 16.
- CG instances: 12.
- LSQR instances: 4.
- Maximum relative residual: below `1e-5`.
- Validation errors: 0.
- Explicitly not a BQP/classical separation.

What it adds:

- D1 now has explicit sparse SPD full-vector-output CG measurements across
  four sizes and three conditioning shifts.
- D2 now has explicit general sparse least-squares LSQR measurements across
  four sizes.
- Each row records sparse input size, full-output bits, explicit-I/O floor,
  residual, iteration count, and matvec-equivalent cost.

## B10-T1 D5 Observable Denominator Table v0

The B5-linked observable denominator table is in
`../research/B10_t1_d5_observable_denominator_table.md`.

Result:

- Status:
  `d5_observable_denominator_table_instantiated_not_quantum_speedup_claim`.
- Dependency benchmark: B5.
- Instances: 9.
- Site counts: 4, 6, 8.
- U/t values: 2.0, 4.0, 8.0.
- Maximum Hilbert dimension: 4900.
- Maximum relative residual: below `1e-8`.
- Validation errors: 0.
- Explicitly not a BQP/classical separation.

What it adds:

- D5 is no longer only a prose placeholder; it is mapped to a concrete B5
  half-filled Hubbard local-density response task.
- The denominator solves `(H - E0 + eta I) x = (n_i - <n_i>) |psi0>` with
  classical CG and reads out a scalar susceptibility proxy.
- This separates observable-output accounting from full-vector readout while
  still charging explicit Hamiltonian construction and Krylov iterations.

## B10-T1 D5 B3 Molecular Observable Proxy v0

The B3-linked molecular observable denominator proxy is in
`../research/B10_t1_d5_b3_molecular_observable_table.md`.

Result:

- Status:
  `b3_d5_molecular_observable_denominator_proxy_not_reaction_solution`.
- Dependency benchmark: B3.
- Instances: 4 calibration molecules.
- Maximum response-matrix dimension: 160.
- Maximum relative residual: below `1e-8`.
- Validation errors: 0.
- Explicitly not a BQP/classical separation.

What it adds:

- D5 now touches both B5 strongly correlated response and B3 molecular
  observable-first resource estimates.
- The B3 table uses the existing PySCF calibration output to create a
  deterministic molecular response denominator proxy.
- It is not a reaction-coordinate simulation; the next B3 step is replacing
  the proxy matrix with a Hamiltonian-derived observable along a reaction path.

## B10-T1 D5 B3 Reaction Observable Table v0

The Hamiltonian-derived reaction-coordinate denominator table is in
`../research/B10_t1_d5_b3_reaction_observable_table.md`.

Result:

- Status:
  `hamiltonian_derived_b3_reaction_observable_denominator_not_reaction_solution`.
- Dependency benchmark: B3.
- Instances: 4 reaction-coordinate rows.
- Maximum response dimension: 21.
- Maximum relative residual: below `1e-12`.
- Validation errors: 0.
- Explicitly not a BQP/classical separation.

What it adds:

- The B3 D5 denominator no longer uses a hand-authored response matrix.
- Each row uses PySCF finite differences of the one-electron Hamiltonian along
  a molecular coordinate, central RHF orbitals, and a singles response
  denominator with two-electron coupling.
- This is still not a full reaction-dynamics result; it is the first
  Hamiltonian-derived denominator that future B3 observable claims must beat.

## B10-T1 D5 B3 Correlated References v0

The correlated B3 reaction-coordinate reference table is in
`../research/B10_t1_d5_b3_correlated_reference_table.md`.

Result:

- Status:
  `correlated_b3_reaction_references_instantiated_not_quantum_advantage_claim`.
- Dependency benchmark: B3.
- Instances: 4 reaction-coordinate rows.
- Methods: RHF, MP2, and CCSD.
- Maximum absolute CCSD-vs-RHF derivative shift: `0.2817594828918857`.
- Validation errors: 0.
- Explicitly not a BQP/classical separation.

What it adds:

- The B3 denominator no longer stops at RHF-derived response quantities.
- Each coordinate row now has finite-difference energy derivatives for RHF,
  MP2, and CCSD in the same small-basis molecular settings.
- The result is a stronger classical reference target for future observable
  estimation claims, but it is still not a quantum implementation, a complete
  reaction-dynamics solution, a basis-complete chemistry claim, or a BQP
  separation.

## B10-T1 D5 B3 FCI References v0

The FCI-strength B3 reaction-coordinate reference table is in
`../research/B10_t1_d5_b3_fci_reference_table.md`.

Result:

- Status:
  `fci_b3_reaction_references_instantiated_not_quantum_advantage_claim`.
- Dependency benchmark: B3.
- Instances: 4 reaction-coordinate rows.
- Methods: RHF, MP2, CCSD, and FCI.
- Maximum absolute FCI-vs-RHF derivative shift: `0.2980126599013033`.
- Maximum absolute FCI-vs-CCSD derivative shift: `0.01625317700941764`.
- Validation errors: 0.
- Explicitly not a BQP/classical separation.

What it adds:

- The B3 denominator now includes exact full-CI references for these small
  STO-3G active spaces.
- Future quantum observable-estimation claims can no longer compare only
  against RHF, MP2, or CCSD on these rows; they must explain whether they beat
  the FCI-strength denominator or why the comparison has moved to a larger
  selected-CI/active-space regime.
- This remains a classical reference artifact, not a quantum implementation,
  full reaction-dynamics solution, basis-complete chemistry result, or BQP
  separation.

## Limits

- The graph is hand-authored and must be source-backed in v0.2.
- It does not prove reductions or separations.
- Edge labels are planning judgements, not formal claims.
- The next version must connect directly to B3/B4/B5/B8 benchmark artifacts.

## Next Algorithmic Step

Build the first useful B10 theory package:

1. Add literature/source links to every node and edge.
2. Compare a concrete quantum observable-estimation circuit against the FCI
   reference denominator, scale the denominator to selected-CI or larger
   active-space settings, or compare a candidate B5 quantum impurity/response
   subroutine against the D5 table.
3. Prove or empirically bound the B4/B8 sampling-verification target under
   leakage and challenge-refresh assumptions.
4. Add more negative-boundary cards for dequantization failures.
5. Connect the formal targets to source-backed literature links per edge.
