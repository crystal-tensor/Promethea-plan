# B1/B7 Cone_01 Theta-Sharing Ledger Gate

Status: `cone01_theta_sharing_ledger_guardrail`

This artifact separates a tempting cache interpretation from the current B7 occurrence ledger. The cone_01 windows use only four theta groups, so a template-cache model sees many repeated theta occurrences. The current B7 ledger, however, charges physical occurrences unless a replayable rewrite certificate removes or shares those occurrences in a countable way.

It is not a rewrite certificate, not a resource-saving claim, and not a physical-layout claim.

## Summary

- Candidate windows: `35`
- Distinct theta groups: `4`
- Duplicate theta occurrences under cache model: `31`
- Optimistic cache proxy-T reuse: `620`
- Target proxy-T reduction: `600`
- Optimistic cache model clears target: `True`
- Occurrence-ledger removed occurrences: `0`
- Occurrence-ledger proxy-T reduction: `0`
- Occurrence-ledger clears target: `False`
- Additional occurrence certificates required: `30`
- Validation errors: `0`

## Theta Groups

| canonical theta | occurrences | cache duplicates | optimistic proxy-T reuse | occurrence-ledger reduction |
|---:|---:|---:|---:|---:|
| 0.420540811611 | 16 | 15 | 300 | 0 |
| 0.364857351786 | 10 | 9 | 180 | 0 |
| 0.99803486463 | 6 | 5 | 100 | 0 |
| 2.813468447841 | 3 | 2 | 40 | 0 |

## Interpretation

The optimistic cache model would appear to clear the numerical B7 target, because 31 duplicate theta occurrences times a proxy cost of 20 gives 620 proxy-T units. This is deliberately not accepted as a B7 ledger improvement: the current ledger is occurrence-based, and these repeated theta values still appear in separate physical windows.

The next admissible route must either produce at least 30 occurrence-removing certificates, or define and justify a new physical cost model where theta sharing reduces the FT ledger.
