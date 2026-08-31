---
name: symperturb-analysis
description: Apply, audit, or explain the SymPerturb virtual-perturbation framework for cross-sectional symptom networks. Use when a task involves SymPerturb, virtual knockout (vKO), virtual knockdown (vKD), virtual dosage perturbation (vDP), edge- or node-centred communication blocking, combination perturbation, sequence optimisation, the seven utility outcomes, VPPS target ranking, robustness/complete-pipeline bootstrap uncertainty, or drafting/checking SymPerturb Methods and Results from symptom-network data.
---

# SymPerturb analysis

Treat SymPerturb as a **model-based target-hypothesis framework**, not a causal intervention estimator.

## Core workflow

1. Inspect the symptom dataset, module map, candidate target set, anchors, scale orientation, bounds, symptom weights, and analysis configuration.
2. Require all symptom variables to be oriented so larger values mean worse states. Do not assume zero is clinically meaningful; use symptom-specific anchors when supplied.
3. Fit the reference Gaussian network from the empirical covariance using diagonal ridge regularisation, invert it to obtain partial correlations, and threshold only for topology-based outcomes.
4. Apply state perturbations with the general location-scale map. Use the linked map only as the reference special case; support location-only, scale-only, and independently parameterised sensitivity maps.
5. Distinguish the four primitive operators from the three analytic procedures:
   - vKO and vKD are state operators.
   - Edge-level and node-centred communication blocking are topology operators.
   - vDP evaluates intensity-response.
   - Combination perturbation constructs a joint target.
   - Sequence optimisation searches an explicit decision objective.
6. Calculate direct target benefit separately from beneficial and adverse downstream spillover. Do not call downstream system benefit total clinical benefit.
7. Compute the seven utility outcomes: downstream efficacy, dose efficiency, breadth, cross-module reach, communication blocking, combination value, and responsiveness.
8. Normalize each utility across the prespecified candidate set, assigning 50 to a constant dimension, then compute the weighted seven-dimension VPPS. Keep robustness out of VPPS.
9. Report robustness separately using scenario-specific ranks and, when requested, a complete-pipeline bootstrap that repeats estimation, thresholding, perturbation, scoring, normalization, and ranking.
10. Produce auditable outputs: target scores, raw utilities, normalized utilities, dose curves, pair values, topology metrics, robustness/bootstrap summaries, and any sequence objective.

## Required guardrails

- Never describe a cross-sectional undirected GGM perturbation as an identified `do()` intervention or a demonstrated treatment effect.
- Never infer biological time from sequence optimisation. The order comes from the objective, discounting, costs, and constraints.
- Never interpret "communication blocking" as proven biological signal transmission. It is adjacency attenuation unless a valid distributional model is reconstructed.
- Do not re-estimate a full covariance matrix after exact vKO while retaining a constant target column. For network-after-knockout questions, use an induced network with the target removed, a topology-only deletion, or a prespecified soft vKO, and state which estimand is being answered.
- Do not compare VPPS values across cohorts, networks, or candidate sets as if the 0-100 scale were transportable. Re-normalization makes VPPS relative to the current candidate set.
- Inspect whether efficacy, dose efficiency, and responsiveness are redundant. Under an unbounded linear Gaussian linked map, `G_j(alpha) = alpha G_j(1)`.
- Preserve signed pair increments for confirmatory combination analysis so harmful or antagonistic combinations remain visible. Positive-part averaging is historical/exploratory compatibility only.

## Use bundled resources

- Read `references/method-specification.md` for equations, estimands, defaults, and operator definitions.
- Read `references/reporting-and-interpretation.md` when drafting Methods, Results, Discussion, figure captions, or claims.
- Read `references/input-output-contract.md` when preparing data/config files or interpreting generated outputs.
- Run `scripts/run_symperturb.py` for a deterministic local analysis when the repository package is available.
- Run `scripts/check_skill_inputs.py` before analysis when input files are user-supplied.

## Completion checks

Before finalizing, verify that:

- symptom direction and anchors are explicit;
- candidate targets and module mapping are explicit;
- the state-map choice and sensitivity maps are reported;
- direct, beneficial downstream, and adverse downstream effects are not conflated;
- seven utilities are shown separately from VPPS;
- robustness is not included in confirmatory VPPS;
- exact-vKO handling is stated;
- bounded versus unbounded response assumptions are stated when relevant;
- the interpretation says "model-derived target hypothesis" rather than "effective treatment target" unless supported by independent longitudinal or experimental evidence.
