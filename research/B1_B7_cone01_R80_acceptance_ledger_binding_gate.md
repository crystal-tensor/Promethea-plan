# B1/B7 Cone01 R80 Acceptance-Ledger Binding Gate

- Target: `T-B1-004gd/T-B7-015m`
- Upstream target: `T-B1-004gc/T-B7-015l`
- Method: `b1_b7_cone01_r80_acceptance_ledger_binding_gate_v0`
- Status: `cone01_r80_acceptance_ledgers_bound_zero_positive_delta`
- Model status: `acceptance_ledgers_hash_bound_but_positive_gates_still_zero`

## Result

R80 fills the two missing R78/R79 ledger path/hash fields with explicit
zero-acceptance occurrence and proxy-T ledgers. This removes the missing
production-field blocker and hash-binds all required packet artifacts, but
the packet remains rejected because the three positive-promotion gates all
stay at zero.

## Key Counters

- Missing fields before: `4`
- Missing fields after: `0`
- All hash-bound artifacts match: `True`
- R80 preflight accepted: `False`
- Failed gates: `['accepted_exit_route_positive', 'accepted_occurrence_positive', 'accepted_proxy_t_positive']`
- Accepted exit routes: `0`
- Accepted occurrence removal: `0`
- Accepted proxy-T reduction: `0`
- B7 credit delta: `0`

## Requirements

- `A1` PASS: R79 is the upstream partial packet with four missing ledger fields
- `A2` PASS: R80 binds an occurrence acceptance ledger while keeping occurrence credit zero
- `A3` PASS: R80 binds a proxy-T acceptance ledger while keeping proxy-T credit zero
- `A4` PASS: R80 removes the R78/R79 missing-field blocker
- `A5` PASS: R80 remains rejected only on the three positive-promotion gates
- `A6` PASS: Accepted counters and B7 credit remain zero
- `A7` PASS: R80 emits a tighter blocker queue with no missing-field work left
- `A8` PASS: R80 claim boundary blocks O3 closure, reroute, resource saving, and B7 credit

## Artifacts

- Result JSON: `results/B1_B7_cone01_R80_acceptance_ledger_binding_gate_v0.json`
- Occurrence ledger: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R80-occurrence-acceptance-zero-ledger.json`
- Proxy-T ledger: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R80-proxy-t-acceptance-zero-ledger.json`
- Bound packet: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R80-acceptance-ledger-bound-zero.packet.json`
- Preflight verdict: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R80-acceptance-ledger-bound-zero.verdict.json`
- Blocker queue: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R80-acceptance-ledger-blocker-queue.json`
- Stdout: `results/B1_B7_cone01_o3_f4_exit_route_submissions/R80-acceptance-ledger-binding.stdout.txt`

## Claim Boundary

R80 is not an accepted exit route, not O3 closure, not reroute
permission, not resource saving, and not B7 credit. It only proves that
the route/replay packet is now field-complete and hash-bound while the
positive occurrence/proxy-T gates remain unsatisfied.
