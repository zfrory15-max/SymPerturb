# Contributing

SymPerturb is a methodological research implementation. Changes that alter equations, estimands, default thresholds, normalization, or interpretation should be treated as scientific changes rather than routine refactoring.

## Pull-request expectations

1. State whether the change is implementation-only, numerical, or methodological.
2. Link the change to the corresponding method definition in `.agents/skills/symperturb-analysis/references/method-specification.md`.
3. Add or update tests for state moments, topology functionals, utility scores, normalization, or uncertainty calculations as applicable.
4. Preserve the seven-utility VPPS and keep robustness separate unless the manuscript specification itself is formally revised.
5. Do not introduce causal language unsupported by design.
6. Run `pytest` and the example CLI before submission.

## Reproducibility

For any numerical result intended for a paper, archive the exact config, code commit, random seed, source-data tables, and environment metadata. Publication-facing results should be independently reproduced before release.
