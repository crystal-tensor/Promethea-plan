# B7 Nonlocal Template Block Scan v0.1

Last updated: 2026-06-15

Status: **nonlocal_template_block_scan_negative_boundary_not_physical_layout**

## Summary

- Input QASM: `results/b1_u3_phase_factored_optimizer/qasmbench_medium_exact/gcm_h6.qasm`
- Proof log: `results/b7_nonlocal_template_block_scan/proofs.jsonl`
- Window widths: [8, 10, 12, 16, 20, 24, 32, 40, 48, 64]
- Operation count scanned: 2341
- Candidate certificates: 2633
- Top repeated templates retained: 12
- Adjacent inverse block pairs: 0
- Adjacent duplicate same-binding block pairs: 0
- Arbitrary numeric rotations before/after/removed: 270 / 270 / 0
- Logical T ledger before/after/removed: 6224 / 6224 / 0
- Portfolio min STV after scan: 1.086008x
- Clears 1.20x all-variant min: False
- Interpretation: Role-normalized nonlocal templates are abundant, but this scan finds no adjacent inverse or duplicate same-binding block that supports a certified occurrence-removing rewrite. A future positive result must replace a repeated block with a lower-arbitrary-rotation unitary and prove equivalence; macro naming or template reuse alone is not a physical ledger reduction.

## Best Repeated Template

- Template ID: `w8_21`
- Width: 8
- Non-overlap occurrences: 20
- Arbitrary rotations per occurrence: 5
- Physical arbitrary occurrences covered: 100
- Unique binding count: 14
- First binding: `{'r0': 13, 'r1': 14}`

First operations:

- `rz(1.4922506383856682) q[13];`
- `cx q[14],q[13];`
- `rz(2.1870074319274799) q[13];`
- `ry(0.52538524712872736) q[13];`
- `rz(pi) q[13];`
- `cx q[14],q[13];`
- `rz(2.538142068316358) q[13];`
- `ry(1.1254377896453873) q[13];`

## Target Sweep

- First all-variant 1.20x row: `None`
- First gcm_h6 1.20x row: `{'removed_arbitrary_occurrences': 30, 'removed_t_ledger': 600, 'after_t_ledger': 5624, 'min_space_time_volume_reduction': 1.1218274111675126, 'gcm_h6_min_space_time_volume_reduction': 1.2017045454545454, 'clears_1_20_all_variant_min': False, 'clears_1_20_gcm_h6_min': True}`

| removed arbitrary occurrences | removed T ledger | after T ledger | portfolio min STV | gcm_h6 min STV | clears all 1.20x |
|---:|---:|---:|---:|---:|---|
| 0 | 0 | 6224 | 1.086008 | 1.086008 | False |
| 1 | 20 | 6204 | 1.088803 | 1.088803 | False |
| 5 | 100 | 6124 | 1.102999 | 1.102999 | False |
| 10 | 200 | 6024 | 1.121827 | 1.122016 | False |
| 20 | 400 | 5824 | 1.121827 | 1.160494 | False |
| 30 | 600 | 5624 | 1.121827 | 1.201705 | False |
| 40 | 800 | 5424 | 1.121827 | 1.245950 | False |
| 50 | 1000 | 5224 | 1.121827 | 1.293578 | False |

## Top Templates

| template | width | non-overlap occ | arbitrary/occ | physical arbitrary covered | unique bindings | first line spans |
|---|---:|---:|---:|---:|---:|---|
| `w8_21` | 8 | 20 | 5 | 100 | 14 | `[[55, 62], [213, 220], [306, 313]]` |
| `w64_2396` | 64 | 7 | 10 | 70 | 7 | `[[34, 97], [192, 255], [285, 348]]` |
| `w32_1701` | 32 | 10 | 7 | 70 | 10 | `[[532, 563], [588, 619], [644, 675]]` |
| `w16_790` | 16 | 11 | 6 | 66 | 11 | `[[532, 547], [588, 603], [644, 659]]` |
| `w48_2317` | 48 | 8 | 8 | 64 | 8 | `[[574, 621], [630, 677], [1265, 1312]]` |
| `w64_2389` | 64 | 7 | 9 | 63 | 7 | `[[27, 90], [185, 248], [278, 341]]` |
| `w64_2390` | 64 | 7 | 9 | 63 | 7 | `[[28, 91], [186, 249], [279, 342]]` |
| `w64_2391` | 64 | 7 | 9 | 63 | 7 | `[[29, 92], [187, 250], [280, 343]]` |
| `w64_2393` | 64 | 7 | 9 | 63 | 7 | `[[31, 94], [189, 252], [282, 345]]` |
| `w64_2394` | 64 | 7 | 9 | 63 | 7 | `[[32, 95], [190, 253], [283, 346]]` |
| `w64_2395` | 64 | 7 | 9 | 63 | 7 | `[[33, 96], [191, 254], [284, 347]]` |
| `w64_2397` | 64 | 7 | 9 | 63 | 7 | `[[35, 98], [193, 256], [286, 349]]` |

## Next Actions

- Target the highest-coverage templates with an actual unitary-synthesis subroutine, not a macro cache.
- Try exact small-block synthesis for the best template bindings and require fewer arbitrary rotations per executed block.
- If synthesis cannot beat the current block, promote this scan into a sharper block-family no-go memo.

## Limits

- The scan proves absence only for the configured window widths and adjacent inverse/duplicate criteria.
- Role-normalized repetition is a candidate generator, not by itself a semantics-preserving rewrite.
- No output QASM rewrite is emitted when cancellation_opportunities.adjacent_inverse_pair_count is zero.
- This remains an FT-ledger proxy, not a lattice-surgery layout or calibrated device claim.
