# SymPerturb method summary

This document is the human-facing companion to the Agent Skill. The authoritative implementation details are in `.agents/skills/symperturb-analysis/references/method-specification.md` and the source code.

## Conceptual architecture

SymPerturb has three layers:

- **State layer:** vKO, vKD, vDP.
- **Topology layer:** edge-level and node-centred communication blocking.
- **Multi-target layer:** combination perturbation and sequence optimisation.

These are not all the same mathematical object. There are **four primitive operators** (vKO, vKD, edge-level blocking, and node-centred blocking) and **three analytic procedures** (vDP intensity-response evaluation, combination joint-target construction, and sequence optimisation). The architecture above groups them by role; it does not make vDP a primitive operator.

This method summary describes the reference package, not evidence that the manuscript simulation has been reproduced. See [reproducibility status](REPRODUCIBILITY.md).

## Primary estimand

The default `G_j(alpha)` in this implementation is a **downstream spillover estimand**: weighted mean standardised improvement among non-target symptoms. The target's own direct benefit is reported separately, as is adverse downstream spillover.

## VPPS

Seven utilities are direction-aligned and min-max normalized across the prespecified candidate target set. A constant utility contributes 50. VPPS is their weighted mean. Robustness is excluded from VPPS and reported separately.

## Interpretation

The framework answers: *What changes in the fitted statistical system under this explicit virtual perturbation operator?* It does not, by itself, answer: *What would happen under a real-world treatment?*

