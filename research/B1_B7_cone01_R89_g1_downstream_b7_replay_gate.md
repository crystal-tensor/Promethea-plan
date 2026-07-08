# B1/B7 Cone01 R89 G1 Downstream B7 Replay Gate

- Target: `T-B1-004gm/T-B7-015v`
- Upstream target: `T-B1-004gl/T-B7-015u`
- Method: `b1_b7_cone01_r89_g1_downstream_b7_replay_gate_v0`
- Status: `cone01_r89_g1_downstream_b7_replay_1_20_proxy_credit`
- Model status: `r88_downstream_b7_replay_accepts_1_20_proxy_credit_not_1_25_or_o3`

## Result

R89 closes the downstream B7 replay gate for the filled R83 G1 submission.
Under the current proxy FT/STV ledger, the candidate reaches the 1.20x
target: `6224 -> 5624`, with `8` units of margin below the `5632` ceiling.
The replay accepts one narrow proxy B7/STV credit unit. It does not reach
the 1.25x target, does not claim a physical layout, and does not close O3,
reroute, or resource-saving claims.

## Key Counters

- Baseline after T ledger: `6224`
- Candidate T-ledger reduction: `600`
- Candidate after T ledger: `5624`
- 1.20x target reached: `True`
- 1.20x margin: `8`
- 1.25x target reached: `False`
- 1.25x margin: `-224`
- Accepted B7 credit delta: `1`
- Accepted credit scope: `proxy_ft_stv_1_20_only`
- O3 closed: `False`

## Requirements

- `A1` PASS: R89 consumes the filled R88 G1 R83 submission
- `A2` PASS: R89 runs downstream B7 replay against the B7 boundary
- `A3` PASS: R89 reaches the 1.20x proxy STV target
- `A4` PASS: R89 does not claim the 1.25x target
- `A5` PASS: R89 accepts only narrow proxy FT/STV credit
- `A6` PASS: R89 keeps O3, reroute, physical-layout, and resource-saving claims closed
- `A7` PASS: R89 emits post-credit blockers for review, 1.25x, and physical layout

## Artifacts

- Result JSON: `results/B1_B7_cone01_R89_g1_downstream_b7_replay_gate_v0.json`
- Replay ledger: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R89-G1-downstream-b7-replay-ledger.json`
- Verdict: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R89-G1-downstream-b7-replay.verdict.json`
- Stdout: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R89-G1-downstream-b7-replay.stdout.txt`
- Post-credit blocker queue: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R89-G1-post-credit-blocker-queue.json`

## Claim Boundary

R89 accepts only a narrow proxy FT/STV 1.20x replay credit. It does not
solve B7, does not reach 1.25x, does not provide a physical layout, and
does not close O3, reroute, resource-saving, or product-readiness claims.
