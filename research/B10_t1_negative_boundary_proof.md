# B10-T1 HHL/Data-Loading Negative-Boundary Proof Attempt v0.1

Last updated: 2026-06-13

Status: **negative_boundary_accounting_lemma_proved_under_explicit_io_model_not_bqp_separation**

## Summary

- Source target: B10-T1 / linear_systems_data_loading_negative_boundary
- Method: b10_t1_linear_systems_io_accounting_negative_boundary_v0
- Proof result: restricted_negative_boundary_accounting_lemma
- Theorem/corollary count: 2
- Open obligations: 3
- Explicitly not a BQP separation: True
- Validation errors: 0

## Claim Boundary

- Rejected claim: End-to-end exponential HHL-style speedup for explicit full-output linear-system tasks while hiding loading, block-encoding, state-preparation, or readout costs.
- Admissible claim: Conditional quantum speedup for small observable outputs under succinct, prebuilt, or fully charged access models with kappa, epsilon, and classical baselines declared.
- Next proof pressure: Instantiate denominator baselines and source-backed assumptions for specific B3/B5 observable tasks.

## B10-T1-L1: explicit_io_lower_bound_for_linear_system_claims

- Type: accounting_lower_bound
- Status: proved_under_explicit_io_model
- Statement: For an n-dimensional linear-system task with explicit matrix/vector input or full-vector output, any end-to-end algorithm in the explicit-I/O model has runtime at least Omega(C_input + C_prep + C_block + B_out), where C_input is the cost of ingesting the explicit instance, C_prep is the cost of preparing |b>, C_block is the cost of constructing or invoking the block encoding, and B_out is the number of output bits written or certified.

### Assumptions

- The input matrix/vector is not a free oracle unless its construction cost is charged separately.
- The algorithm must either ingest the explicit instance or cite a prebuilt oracle/data structure with declared cost.
- The output medium must contain enough bits to represent the requested answer to the requested precision.
- Runtime accounting includes classical preprocessing, state preparation, block-encoding construction, quantum queries, and output writing.

### Proof Sketch

- Any algorithm that receives an explicit instance through a finite-bandwidth classical interface must spend at least C_input steps to ingest or construct the data structure it later queries.
- If the quantum routine uses |b> or a block encoding of A, the construction or invocation costs C_prep and C_block are part of the end-to-end algorithm unless they are explicitly delegated to a trusted external oracle.
- If the claimed output contains B_out bits, at least B_out bit-write or equivalent certification operations are necessary simply to emit the answer.
- These lower bounds are independent bottlenecks in the end-to-end contract, so the total runtime is at least their sum up to constant-factor machine-model choices.

### Consequence

- A polylog(n) quantum subroutine does not imply a polylog(n) end-to-end algorithm when explicit input loading, oracle construction, state preparation, or full-output readout is required.

## B10-T1-C1: no_hidden_exponential_speedup_for_full_output_hhl

- Type: negative_boundary_corollary
- Status: proved_under_explicit_io_model
- Statement: If a linear-system advantage claim requests the full n-dimensional solution vector to b bits of precision, or uses explicit input whose preparation/block-encoding cost is Omega(n), then no end-to-end exponential speedup over input/output size can be claimed from an HHL-style polylogarithmic quantum subroutine alone.

### Assumptions

- Full-vector output requires B_out = Omega(n b) output bits.
- Explicit input or oracle construction costs are charged rather than hidden.
- The comparison denominator is end-to-end runtime, not only quantum query complexity.

### Proof Sketch

- Apply B10-T1-L1 with B_out = Omega(n b) for full-vector output.
- Alternatively, apply B10-T1-L1 with C_input + C_prep + C_block = Omega(n) for explicit loading or block-encoding construction.
- Either condition gives an Omega(n) end-to-end lower bound, excluding a polylog(n) end-to-end exponential-speedup claim in that model.

### Consequence

- HHL-like claims remain admissible only for succinct or already-charged input access and small observable-output tasks, with condition number, precision, and classical baselines declared.

## Open Obligations

- B10-T1-O1 (open_literature_linking): Source-back the machine model and lower-bound statement with literature references.
- B10-T1-O2 (open_baseline_instantiation): Instantiate the denominator comparison against concrete classical sparse linear-system or observable-estimation baselines.
- B10-T1-O3 (open_dequantization_boundary): Extend the lemma from full-output/readout and explicit-loading accounting to dequantization-style low-rank or sampling-access regimes.

## Limits

- This is an accounting lower-bound lemma under an explicit-I/O model, not an unconditional BQP versus classical separation.
- It does not rule out HHL-style speedups for succinctly specified, oracle-access, or small-observable tasks when all access costs are honestly charged.
- It still needs source-backed citations and concrete classical denominator baselines before it can become a publishable theory note.
