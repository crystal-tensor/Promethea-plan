# B1/B7 Cone_01 Carrier Interleaving Commutation Gate

Status: `cone01_carrier_interleaving_commutation_negative_gate`

This artifact consumes T-B1-004ac and checks whether the single-qubit gates interleaved between repeated blocker CNOTs are benign enough to commute away without a real two-qubit semantic replay certificate.

## Summary

- Commutation candidates: `3`
- Interleaving single-qubit ops: `18`
- Unique interleaving lines: `13`
- Cheap control-side phase commutations: `7`
- Target-side phase obstructions: `4`
- Non-diagonal interleaving obstructions: `7`
- Candidates with non-diagonal interleavings: `3`
- Accepted interleaving commutation clearances: `0`
- Accepted occurrence/proxy-T reduction: `0` / `0`
- Validation errors: `0`

## Candidate Rows

| Pattern | Candidate line | Interleavings | Control-side phases | Target-side phases | Non-diagonal gates | Rejection |
|---|---:|---:|---:|---:|---:|---|
| flat_pattern_01 | 1378 | 5 | 2 | 1 | 2 | non-diagonal interleavings remain inside repeated blocker-CNOT pairs |
| flat_pattern_01 | 1381 | 6 | 2 | 1 | 3 | non-diagonal interleavings remain inside repeated blocker-CNOT pairs |
| flat_pattern_01 | 268 | 7 | 3 | 2 | 2 | non-diagonal interleavings remain inside repeated blocker-CNOT pairs |

## Claim Boundary

This is a negative cheap-commutation gate. It does not prove that no semantic CNOT-stack rewrite exists. It only rejects the shortcut where the repeated blocker CNOTs can be cleared by commuting away all intervening single-qubit gates under simple CNOT rules.
