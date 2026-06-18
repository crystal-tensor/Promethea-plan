# B6 Prototype Notes: High-Temperature Superconductivity Search v0.1

Last updated: 2026-06-13

Problem: **37. High-temperature superconductivity**

The sixth attack direction is now initialized with a toy descriptor-ranking
harness. This is not a material discovery claim. It is a scaffolding benchmark
for turning quantum-simulation-derived descriptors into candidate rankings and
for testing whether those rankings recover known high-temperature
superconducting families before moving to real materials databases.

## Current Components

- Benchmark manifest: `../benchmarks/B6_high_temperature_superconductivity.yaml`
- Descriptor ranker: `../tools/b6_superconductivity_descriptor_ranker.py`
- First result: `../results/B6_superconductivity_descriptor_ranker_v0.json`

## Descriptor Model

The v0 model uses six toy candidate families:

1. `cuprate_like`
2. `iron_pnictide_like`
3. `hydride_like`
4. `nickelate_like`
5. `flat_band_oxide_like`
6. `organic_salt_like`

Each candidate is represented by coarse features:

- correlation ratio `U/W`
- spin fluctuation strength
- electron-phonon coupling proxy
- dimensionality
- disorder
- pressure cost
- carrier-density optimality
- competing-order strength

The ranking score combines a spin-fluctuation pairing descriptor, a phonon
pairing descriptor, carrier optimality, and penalties for disorder, competing
orders, and high pressure. An ensemble of perturbed weights gives a small
uncertainty estimate for active-learning priority.

## First Result

The first run covers 72 toy candidates and ranks the top 12. The benchmark
records:

- known high-Tc family precision at 12
- known high-Tc family recall at 12
- top family counts
- top candidate IDs
- descriptor uncertainty per candidate

Current v0 results:

| Metric | Value |
|---|---:|
| Candidates | 72 |
| Top-k | 12 |
| Known high-Tc precision@12 | 0.833333 |
| Known high-Tc recall@12 | 0.277778 |

Top-12 family counts:

| Family | Count |
|---|---:|
| `cuprate_like` | 8 |
| `iron_pnictide_like` | 2 |
| `nickelate_like` | 2 |

Interpretation:

- This creates a measurable B6 target before real materials data is connected.
- The desired behavior is not to prove a new material, but to recover known
  high-Tc families and identify where the descriptor is merely copying family
  priors.
- The v0 ranking recovers known cuprate-like and iron-pnictide-like candidates
  strongly, but hydride-like candidates are pushed down by the pressure penalty;
  that tradeoff should be tested rather than accepted as truth.
- The descriptor should eventually be replaced by outputs from B5-style
  Hubbard, plaquette, or electron-phonon solvers.

## Limits

- Candidates are synthetic, not actual compounds.
- The descriptor is hand-built and should be treated as a schema test.
- Known-family precision is not scientific validation; it is only a smoke test.
- No synthesis feasibility, toxicity, stability, or experimental uncertainty is
  modeled beyond a crude pressure/disorder penalty.

## Next Algorithmic Step

Build the first useful B6 comparison:

1. Add random and family-prior baselines.
2. Connect at least one descriptor to the B5 Hubbard/plaquette solver.
3. Replace synthetic rows with real candidate records from a materials source.
4. Run retrospective validation on known cuprate, pnictide, hydride, nickelate,
   and organic families.
5. Track whether active learning chooses candidates that improve descriptor
   uncertainty rather than only reselecting obvious families.
