# B4/B8/B10 R173 First Divergent Combine Trace

- Status: `first_divergent_combine_localized`
- Classification: `two_graph_rounding_path_localized_with_exact_guardrail`
- Requirements: `10/10`
- Payload hash: `22ba7693a4ffe43d61c365d875be4a4c82b267a25eb78bb07fd25013f592f5a8`

## Research Question

Where does source-order binary64 first separate two candidates whose retained leaf sums are exactly equal?

## Result

R173 localizes the first divergence on `12/12` selected branches across `6` source traces. Every traced combine reproduces native binary64 `left + right`; the observed split is therefore an accumulation-order effect under the declared instrumented path, not evidence of undefined addition behavior.

| Input | Profile | First divergent prefix | Final signed ULP debt | Source gap |
|---|---|---:|---:|---:|
| r170_path | native_hashset_order | c1@leaf4 / c2@leaf5 | 0 / -1 | 1 |
| r170_path | ascending_sorted_order | c1@leaf10 / c2@leaf5 | 0 / -1 | 1 |
| r170_path | descending_sorted_order | c1@leaf8 / c2@leaf4 | 0 / -1 | 1 |
| r172_t_tree | native_hashset_order | c1@leaf8 / c2@leaf13 | 2 / 1 | 1 |
| r172_t_tree | ascending_sorted_order | c1@leaf7 / c2@leaf11 | 2 / 1 | 1 |
| r172_t_tree | descending_sorted_order | c1@leaf8 / c2@leaf13 | 2 / 1 | 1 |

## Policy Guardrail

The exact retained-leaf, first-seen policy passes `6/6` R170/R172 exact-tie traces. The immutable R160 score control classifies `4/4` tie rows as ties and `28/28` non-tie rows as strict inequalities.

## Claim Boundary

Undefined floating-point behavior, a confirmed qiskit bug, a merged source patch, production performance, route improvement, hardware relevance, quantum advantage, bqp separation, solved b4/b8/b10, or new credit.
