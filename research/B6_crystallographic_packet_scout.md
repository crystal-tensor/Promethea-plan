# B6 Crystallographic Packet Scout v0.1

Status: **crystallographic_packet_scout_failed_missing_computed_evidence**

## Summary

- Method: `b6_crystallographic_packet_scout_v0`
- Model status: `contract_packets_mapped_but_backend_observable_and_denominator_evidence_missing`
- Requirements passed/failed: 3 / 5
- Failed requirement IDs: S4, S5, S6, S7, S8
- Contract packets: 5
- Records / families / negative controls: 56 / 28 / 18
- Post-split crystallographic AP / family-prior AP: 0.2476190476190476 / 0.4901360544217687
- Source validation errors: 2
- Pymatgen/backend available: False
- DFT observable rows: 0
- B5-computed observable rows: 0

## Requirement Results

- S1 [PASS]: Crystallographic evidence contract is present and open
- S2 [PASS]: Source reproducibility gate remains mapped
- S3 [PASS]: Scope remains the locked 56-record / 28-family / 18-negative-control dataset
- S4 [FAIL]: Reproducible crystallographic backend is available
- S5 [FAIL]: Source validation blockers are cleared
- S6 [FAIL]: Crystallographic model beats post-split family-prior denominator
- S7 [FAIL]: DFT observable channel exists
- S8 [FAIL]: B5-computed observable channel exists

## Claim Boundary

- Supported: The B6 crystallographic packet surface is mapped to the current failed reproducibility and contract evidence.
- Not supported: This is not material discovery, not a superconductivity mechanism, not a reproducible crystallographic descriptor, not DFT evidence, not B5 observable evidence, and not a solution claim.
- Next gate: close S4-S8 by pinning a backend, clearing source validation, beating the family-prior denominator, and attaching DFT or B5-computed observables.
