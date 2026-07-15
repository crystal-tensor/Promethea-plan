# B7 w8_21 Real-Circuit Context Absorption

- Status: `context_replay_complete_no_resource_reduction_claim`
- Classification: `exact_context_replay_with_boundary_no_go`
- Requirements: `10/10`
- Payload hash: `e7660b7b541959df43319fb7fdf6345d6177bd69b915389a898946f3674568fb`

## Heuristic question

Can the exact w8_21 normal form absorb a neighboring target-local operation in the real gcm_h6 stream, or does the next CX preserve the resource boundary?

## Replay result

The gate replays `16` selected non-overlapping source occurrences from `gcm_h6.qasm` (the upstream template scan records 20 raw occurrences and selects 16 non-overlapping spans). All `16/16` context checks pass; the maximum local-context residual is `1.630e-16`.

The source contains `0` immediately preceding same-target Rz merge opportunities. `7` occurrences are followed by a same-target Rz, but the normal form ends in Ry(e), so those are not direct Rz merges. The following CX remains the next non-local boundary in the source stream.

## Resource boundary

The exact rewrite preserves two CNOTs and five arbitrary parameters. Direct Rz merge count, accepted occurrence removal, proxy-T reduction, and B7 credit remain zero. This is a reproducible context-level negative boundary, not a full-circuit no-go theorem.
