# B3/B10 F1 Pilot Row Candidate Gate

- Target: `T-B3-023/T-B10-015j`
- Method: `b3_b10_f1_pilot_row_candidate_gate_v0`
- Status: `f1_pilot_row_candidate_extracted_zero_credit`
- Candidate row: `B3B10-F1-pilot-row-h2-ccpvdz-compiled-ucc-adapt-v0`
- Candidate row hash: `df0e080e64011ee171d8e3079e84b71a873a3af7fb460f663c510b4214cd81f0`
- Source F1 packet hash: `dce2291e5ee21b7b2ccda8024d7da7afeb25565541e8dbe13035d1d9828612d7`

## Result

The gate extracts one source-backed pilot row candidate from the existing compiled UCC/ADAPT covariance pilot. It passes 7/10 requirements and intentionally fails ['P8', 'P9', 'P10'] because F1 still needs four row-aligned rows and a submitted source-backed artifact.

## Candidate Row

- Molecule / basis: `h2_bond_stretch` / `cc-pvdz`
- Ansatz: `compiled_one_parameter_ucc_double_adapt_seed` at theta `0.18`
- Pilot groups / shots per group: `48` / `512`
- Pilot max relative variance error: `0.08265558952228451`
- Center covariance shot floor: `66955026`
- Derivative shot floor: `669550260000`
- Optimizer-loop shots: `24773359620000`
- Optimizer-loop 2Q executions: `7531101324480000`

## Requirement Results

- `P1` PASS: Compiled UCC/ADAPT pilot source is valid
- `P2` PASS: Candidate row is bound to the locked F1 packet
- `P3` PASS: One H2/cc-pVDZ candidate row is extracted
- `P4` PASS: Pilot sampled covariance evidence is present and below the preview error cap
- `P5` PASS: Compiled-state covariance and derivative shot floors are carried forward
- `P6` PASS: Optimizer-loop cost ledger remains charged
- `P7` PASS: No reaction-dynamics, denominator-win, quantum-advantage, or B10 credit claim is made
- `P8` FAIL: F1 four-row scope is complete
- `P9` FAIL: Source-backed F1 artifact has been submitted
- `P10` FAIL: Candidate row is accepted as part of the F1 artifact

## Claim Boundary

- Supported: One existing H2/cc-pVDZ compiled one-parameter UCC/ADAPT pilot row is extracted as a candidate row for the F1 full-covariance packet.
- Not supported: This is not a submitted F1 artifact, not four row-aligned F1 rows, not an accepted full-covariance row, not a denominator win, not a B3 reopen, not B10-T1 credit, and not quantum advantage or BQP separation.
- Next gate: Add three more source-backed row candidates and package all four into the locked F1 artifact with replay hashes, denominator contract, optimizer ledger, and claim boundary.

This candidate gate does not claim a reaction-dynamics solution, quantum advantage, B3 reopen credit, B10-T1 credit, or BQP separation.

## Validation

- validation_error_count: `0`
