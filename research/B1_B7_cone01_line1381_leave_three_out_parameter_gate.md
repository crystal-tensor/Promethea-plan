# B1/B7 cone_01 Line-1381 Leave-Three-Out Parameter Gate

- Method: `b1_b7_cone01_line1381_leave_three_out_parameter_gate_v0`
- Status: `cone01_line1381_no_three_parameter_free_removal`
- Model status: `line1381_off_grid_parameter_triples_are_leave_three_out_required`
- Workload: `qasmbench_medium_exact/gcm_h6.qasm`
- Source five-parameter repair: `results/B1_B7_cone01_five_parameter_line1381_exact_repair_gate_v0.json`
- Source leave-two-out gate: `results/B1_B7_cone01_line1381_leave_two_out_parameter_gate_v0.json`

## Result

- Current line-1381 off-grid parameter indices: `[3, 4, 9, 16, 17]`
- Base five-parameter residual: `6.513210005207597e-13`
- Leave-three-out rows: `10`
- Exact pass / fail: `0` / `10`
- Best leave-three-out residual: `0.29673862906454757` at parameters `[4, 9, 16]`
- Worst leave-three-out residual: `0.7449029676343185` at parameters `[4, 16, 17]`
- Minimum residual ratio to exact tolerance: `29673862.906454757`
- Three-parameter free removal accepted: `False`
- Accepted occurrence / proxy-T reduction / B7 claim: `0` / `0` / `False`

## Leave-Three-Out Rows

| Fixed parameters | Snap errors | Reoptimized indices | Residual | Exact |
| --- | ---: | --- | ---: | --- |
| [3, 4, 9] | [0.142527506515, 0.362110796574, 0.267119127289] | `[16, 17]` | 0.457077569066 | False |
| [3, 4, 16] | [0.142527506515, 0.362110796574, 0.226452509199] | `[9, 17]` | 0.406153114512 | False |
| [3, 4, 17] | [0.142527506515, 0.362110796574, 0.362110796574] | `[9, 16]` | 0.35793848562 | False |
| [3, 9, 16] | [0.142527506515, 0.267119127289, 0.226452509199] | `[4, 17]` | 0.310622881407 | False |
| [3, 9, 17] | [0.142527506515, 0.267119127289, 0.362110796574] | `[4, 16]` | 0.450323073451 | False |
| [3, 16, 17] | [0.142527506515, 0.226452509199, 0.362110796574] | `[4, 9]` | 0.422736136861 | False |
| [4, 9, 16] | [0.362110796574, 0.267119127289, 0.226452509199] | `[3, 17]` | 0.296738629065 | False |
| [4, 9, 17] | [0.362110796574, 0.267119127289, 0.362110796574] | `[3, 16]` | 0.546936096006 | False |
| [4, 16, 17] | [0.362110796574, 0.226452509199, 0.362110796574] | `[3, 9]` | 0.744902967634 | False |
| [9, 16, 17] | [0.267119127289, 0.226452509199, 0.362110796574] | `[3, 4]` | 0.415081698316 | False |

## Claim Boundary

- This is a scaffold-local leave-three-out pressure gate, not a global minimality theorem.
- The result blocks a cheap three-parameter removal claim for line 1381, but it does not remove, absorb, or symbolically decompose the five-parameter burden.
