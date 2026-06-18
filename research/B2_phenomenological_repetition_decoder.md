# B2 Phenomenological Repetition Decoder v0.1

Last updated: 2026-06-13

Status: **phenomenological_decoder_fallback_not_surface_code_claim**

## Summary

- Configurations: 12
- Improved configurations: 2
- Best relative reduction vs majority: 85.71%
- Max decoder runtime / shot: 0.000101133 s

## Results

| d | rounds | p_data | p_meas | Viterbi pL | Majority pL | Reduction | runtime/shot |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 3 | 0.003 | 0.003 | 0 | 0 | n/a | 1.837e-05 |
| 3 | 3 | 0.005 | 0.005 | 0 | 0 | n/a | 1.887e-05 |
| 3 | 3 | 0.01 | 0.01 | 0.003 | 0.003 | 0.00% | 2.174e-05 |
| 3 | 3 | 0.02 | 0.02 | 0.006 | 0.005 | -20.00% | 1.822e-05 |
| 5 | 5 | 0.003 | 0.003 | 0 | 0 | n/a | 3.288e-05 |
| 5 | 5 | 0.005 | 0.005 | 0 | 0 | n/a | 3.257e-05 |
| 5 | 5 | 0.01 | 0.01 | 0.001 | 0 | n/a | 3.283e-05 |
| 5 | 5 | 0.02 | 0.02 | 0.003 | 0.007 | 57.14% | 3.046e-05 |
| 7 | 7 | 0.003 | 0.003 | 0 | 0 | n/a | 0.0001011 |
| 7 | 7 | 0.005 | 0.005 | 0 | 0 | n/a | 9.685e-05 |
| 7 | 7 | 0.01 | 0.01 | 0 | 0 | n/a | 9.886e-05 |
| 7 | 7 | 0.02 | 0.02 | 0.001 | 0.007 | 85.71% | 9.808e-05 |

## Limits

- This is a phenomenological repetition-code memory model, not a surface-code or LDPC result.
- The decoder is a transparent Viterbi/minimum-weight fallback for small distances, not PyMatching.
- Data and measurement errors are independent bit-flip events; no leakage or correlated two-qubit circuit noise is modeled.
- The purpose is to establish B2's decoder interface and syndrome-history reporting before adding Stim/PyMatching or code search.
