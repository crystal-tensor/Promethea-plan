# Review Gates

Last updated: 2026-06-15

These gates prevent the project from mistaking motion for proof.

## Gate 0: Intake

The PR states:

- track ID;
- task ID;
- claim boundary;
- expected artifact;
- reproducible command.

## Gate 1: Reproducibility

Required evidence:

- scripts run from a clean workspace;
- result JSON is valid;
- report is human-readable;
- assumptions are recorded.

## Gate 2: Baseline Strength

Required evidence:

- baseline is named and justified;
- stronger baseline is listed if not implemented;
- result does not depend on hiding input, output, verification, or data-loading
  costs.

## Gate 3: Integration

Required evidence:

- benchmark manifest updated if status changes;
- audit script updated if project status changes;
- execution board or dossier updated if maturity changes.

## Gate 4: Adversarial Review

Required evidence:

- another agent or reviewer tries to break the claim;
- failure modes are documented;
- unsupported claims are explicitly removed.

## Gate 5: Translation Eligibility

A track can enter translation only when:

- the technical gate in `technical_resolution_program.md` is passed;
- the result survives adversarial baseline review;
- portfolio audit passes;
- there is a clear novelty, utility, or theorem story.

Translation outputs may include:

- manuscript outline;
- patent disclosure;
- fundable project memo;
- product/tool specification.
