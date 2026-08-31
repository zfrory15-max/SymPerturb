# SymPerturb method summary

This document is the human-facing companion to the Agent Skill. The authoritative implementation details are in `.agents/skills/symperturb-analysis/references/method-specification.md` and the source code.

## Conceptual architecture

SymPerturb has three layers:

- **State layer:** vKO, vKD, vDP.
- **Topology layer:** edge-level and node-centred communication blocking.
- **Multi-target layer:** combination perturbation and sequence optimisation.

These are not all the same mathematical object. vKO/vKD and communication blocks are primitive operators; vDP is an evaluation procedure; combination is a joint-target construction; sequence optimisation is a decision procedure.

## Primary estimand

The default `G_j(alpha)` in this implementation is a **downstream spillover estimand**: weighted mean standardised improvement among non-target symptoms. The target's own direct benefit is reported separately, as is adverse downstream spillover.

## VPPS

Seven utilities are direction-aligned and min-max normalized across the prespecified candidate target set. A constant utility contributes 50. VPPS is their weighted mean. Robustness is excluded from VPPS and reported separately.

## Interpretation

The framework answers: *What changes in the fitted statistical system under this explicit virtual perturbation operator?* It does not, by itself, answer: *What would happen under a real-world treatment?*
