# B1 30-Circuit Ablation Report v0.1

Last updated: 2026-06-13

Profile: `heavy_hex_like_sparse`
Circuits: 30

## Aggregate Stage Table

| Stage | Operation reduction | 2Q reduction | Depth reduction | Exposure reduction |
|---|---:|---:|---:|---:|
| baseline | 0.00% | 0.00% | 0.00% | 0.00% |
| after_1q_resynthesis | 28.18% | 0.00% | 29.66% | 4.42% |
| after_adjacent_rzz | 34.12% | 10.62% | 34.89% | 12.50% |
| final | 34.17% | 10.72% | 34.98% | 12.58% |

## Incremental Contribution Share

| Stage | Operation share | 2Q share | Depth share | Exposure share |
|---|---:|---:|---:|---:|
| after_1q_resynthesis | 82.46% | 0.00% | 84.78% | 35.13% |
| after_adjacent_rzz | 17.37% | 99.06% | 14.96% | 64.23% |
| final | 0.17% | 0.94% | 0.26% | 0.64% |

## Subset Final Reductions

| Subset | Circuits | Operation | 2Q | Depth | Exposure |
|---|---:|---:|---:|---:|---:|
| qasmbench_small | 10 | 26.68% | 8.44% | 30.86% | 9.26% |
| qasmbench_medium_exact | 6 | 38.10% | 0.00% | 37.88% | 7.70% |
| qasmbench_interaction_exact | 2 | 32.05% | 19.02% | 27.20% | 19.13% |
| b1_exact_extension | 12 | 31.73% | 43.24% | 47.09% | 22.28% |

## Interpretation

- Largest hardware-exposure contributor: `after_adjacent_rzz`.
- Largest depth contributor: `after_1q_resynthesis`.
- Limit: This is an ablation over the current fixed pass order, not a causal proof that passes are independent.
- Limit: The final stage includes all remaining RZZ passes after the adjacent pass.
- Limit: The suite includes generated exact-extension circuits and still needs more external benchmarks.
