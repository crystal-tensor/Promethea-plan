# Top 20 Evidence Map v0.1

Last updated: 2026-06-13

Purpose: connect each first-pass Top 20 problem to source evidence and explain
why it deserves a place in the research portfolio. This is not yet a complete
literature review; it is the evidence layer needed before deep dives.

Evidence labels:

- `A`: official problem list, standard, institutional report, or consensus
  roadmap.
- `B`: peer-reviewed paper, major technical paper, or widely used open-source
  benchmark/tool.
- `C`: secondary synthesis or community reference.

## Evidence Table

| Rank | ID | Problem | Evidence | Source anchors | Evidence note | Quantum attackability note |
|---:|---:|---|---|---|---|---|
| 1 | 25 | Quantum compilation and circuit compression | A/B | NASEM QC report; DOE QIS roadmap; QASMBench; MQT Bench | Quantum computers require translation from algorithms to hardware-level circuits; benchmark suites exist for reproducible compiler evaluation. | High: objective metrics include depth, gate count, T-count/T-depth, routing overhead, fidelity, and runtime. |
| 2 | 22 | Low-overhead quantum error correction | A/B | NASEM QC report; DOE QIS roadmap; Stim | Error correction and fault tolerance are repeatedly identified as central to scalable quantum computing. | High: codes and decoders can be benchmarked under explicit noise models. |
| 3 | 49 | Exact molecular reaction dynamics | A/B | DOE QIS roadmap; DOE QIS topic pages; OpenFermion | Chemistry and materials simulation are flagship quantum-computing applications. | High: molecular Hamiltonians, active spaces, and resource estimates give concrete targets. |
| 4 | 16 | General verification of quantum advantage | A/B | NASEM QC report; DOE QIS roadmap | Verification and validation determine whether claimed quantum advantage is trustworthy. | High: protocols can be scored by soundness, completeness, sample complexity, and spoofing resistance. |
| 5 | 38 | Strongly correlated quantum matter | A/B | DOE QIS roadmap; DOE QIS topic pages | Quantum materials are a major DOE-relevant application area and remain difficult for classical simulation. | High: hybrid quantum-classical embedding and tensor methods can be benchmarked on model Hamiltonians. |
| 6 | 37 | High-temperature superconductivity | A/B | DOE QIS roadmap; DOE QIS topic pages | Better superconducting materials are named among quantum simulation opportunities. | Medium-high: direct discovery is hard, but descriptors and model solvers are feasible. |
| 7 | 21 | Fault-tolerant quantum computing at scale | A | NASEM QC report; DOE QIS roadmap | Fault-tolerant operation is the main bridge from noisy devices to large useful algorithms. | High: architecture and resource-estimation studies have concrete workload baselines. |
| 8 | 30 | Efficient classical verification of quantum outputs | A/B | NASEM QC report; quantum benchmarking literature | Trusting outputs beyond classical simulation is a necessary deployment condition. | High: property-testing and randomized-measurement protocols can be measured. |
| 9 | 17 | Quantum PCP conjecture | B/C | Hamiltonian complexity and quantum complexity literature | Quantum PCP is a central open problem in quantum complexity and local Hamiltonian hardness. | Medium-high: one-year output likely restricted theorems, counterexample search, or computational evidence. |
| 10 | 11 | Boundary of BQP | A/B/C | Stanford Encyclopedia quantum computing; complexity theory references; NASEM QC report | Understanding what quantum computers can and cannot efficiently solve is foundational. | Medium-high: likely progress through restricted separations, reductions, and taxonomy rather than full class separation. |
| 11 | 27 | Theory of error mitigation | A/B | NASEM QC report; NISQ algorithms literature | Error mitigation is central for extracting value before full fault tolerance. | High: benchmarkable on noisy simulators and real cloud devices. |
| 12 | 43 | Low-energy nitrogen fixation | A/B | DOE QIS roadmap; NAE Grand Challenges energy themes | Nitrogen fixation is an energy- and food-system challenge tied to catalysis. | Medium-high: catalyst active-site simulation is a natural quantum chemistry target. |
| 13 | 81 | Global post-quantum cryptography migration | A | NIST PQC project; NIST finalized PQC standards | NIST finalized principal PQC standards in August 2024 and encourages transition. | High for threat modeling and cryptanalysis; lower for original algorithms because standards are already selected. |
| 14 | 41 | Room-temperature ambient-pressure superconductors | A/B | DOE QIS roadmap; materials science roadmaps | Practical superconductors would transform energy, transport, sensing, and computing. | Medium-high: discovery validation is experimental, but quantum descriptors are feasible. |
| 15 | 6 | Yang-Mills mass gap | A | Clay Mathematics Institute Millennium Prize Problems | Official Millennium Prize problem in mathematical physics. | Medium: quantum simulation may map examples, but proving the theorem is beyond a one-year target. |
| 16 | 18 | Many-body localization complexity | B | Quantum many-body and Hamiltonian complexity literature | Thermalization/localization in interacting systems is a core frontier for many-body physics. | Medium-high: finite-size numerical laboratories and quantum simulation protocols are feasible. |
| 17 | 29 | Practical QRAM | B/C | Quantum algorithm data-loading literature | QRAM is a hidden assumption behind many claimed quantum speedups. | Medium: strong negative or alternative-architecture results may be more realistic than hardware construction. |
| 18 | 31 | Quantum gravity | A/B/C | Astro2020; P5 report; quantum information in gravity literature | Unifying quantum mechanics and gravity is one of the deepest physics goals. | Low-medium for one-year direct progress; higher for toy models and quantum-information probes. |
| 19 | 12 | Quantum speedups for NP-complete problems | A/B/C | Complexity theory; NASEM QC report | Clarifying the limits of quantum speedups affects expectations for optimization and search. | Medium: likely negative results, no-go theorems, or restricted benchmark studies. |
| 20 | 65 | Closed-loop autonomous laboratories | A/B | National Academies automated biotechnology report; DOE QIS roadmap | Automated laboratories can accelerate discovery in materials, chemistry, and biology. | Medium: strongest role is meta-acceleration for quantum/materials experiments. |

## Source Anchors

- Clay Mathematics Institute Millennium Prize Problems:
  https://www.claymath.org/millennium-problems/
- Clay Yang-Mills and Mass Gap:
  https://www.claymath.org/millennium/yang-mills-the-maths-gap/
- National Academies, Quantum Computing: Progress and Prospects:
  https://www.nationalacademies.org/read/25196
- NASEM chapter on quantum algorithms, error correction, and applications:
  https://www.nationalacademies.org/read/25196/chapter/5
- DOE Office of Science, QIS sponsored reports:
  https://science.osti.gov/Initiatives/QIS/Community-Resources/SC-Sponsored-Reports
- DOE 2024 Quantum Information Science Applications Roadmap:
  https://www.quantum.gov/wp-content/uploads/2024/12/DOE_QIS_Roadmap_Final.pdf
- DOE Quantum Information Science topic page:
  https://www.energy.gov/topics/quantum-information-science
- NIST Post-Quantum Cryptography project:
  https://csrc.nist.gov/projects/post-quantum-cryptography
- NIST first finalized PQC standards announcement:
  https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards
- National Academy of Engineering Grand Challenges:
  https://www.nae.edu/20782/grand-challenges-project
- National Academies automated biotechnology report:
  https://www.nationalacademies.org/read/27469
- QASMBench:
  https://github.com/pnnl/QASMBench
- MQT Bench:
  https://github.com/munich-quantum-toolkit/bench
- Stim:
  https://github.com/quantumlib/Stim
- OpenFermion:
  https://quantumai.google/openfermion

## Gaps to Close in v0.2

- Add paper-level citations for Quantum PCP, BQP boundaries, QRAM, many-body
  localization, and error mitigation.
- Split source anchors into `problem importance`, `known baselines`, and
  `benchmark/tooling`.
- Add an explicit `kill condition` for each Top 20 problem.
