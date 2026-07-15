# B1/B7 Cone01 R72 Cost-Aware Packet Synthesis Gate

- Method: `b1_b7_cone01_r72_cost_aware_packet_synthesis_gate_v0`
- Status: `cone01_r72_exact_packet_scaffolds_cost_dominated_boundary`
- Requirements: `8/8`
- Search attempts: `192`
- Exact solution count: `112`
- Packets with reduced-CNOT exact solutions: `3`
- Packets with FT-cost improvement: `0`
- Source minus best exact rotation cost: `[-195, -255, -273]`
- Accepted occurrence removal / proxy-T reduction: `0` / `0`
- B7 credit: `0`

## Interpretation

The search finds exact local solutions with fewer CNOTs, but every best exact solution is rotation-cost dominated by its source packet under the pinned FT proxy ledger. This strengthens the R71 conclusion: residual-zero local synthesis is not enough; the candidate must also lower the non-Clifford resource burden.

## Claim Boundary

- This is a scoped fixed-direction numerical search, not a global lower-bound theorem.
- No full-circuit rewrite, occurrence removal, proxy-T reduction, reroute, or B7 credit is accepted.
