# Reporting and interpretation for SymPerturb

## Language to use

Prefer:

- "model-derived target priority"
- "virtual perturbation response"
- "downstream spillover estimand"
- "adjacency attenuation"
- "within-candidate-set VPPS"
- "scenario rank stability" or "bootstrap top-k selection probability"
- "hypothesis for longitudinal or experimental validation"

Avoid unless independent causal evidence exists:

- "causal intervention target"
- "effective treatment target"
- "the symptom causes downstream symptoms"
- "communication pathway was biologically blocked"
- "sequence shows the order in which symptoms should biologically improve"

## Minimum Methods reporting

State:

- data type and symptom scale;
- scale orientation (higher=worse);
- symptom-specific anchors;
- candidate target set;
- module definitions;
- network estimator, ridge value, edge threshold;
- state-map choice and sensitivity maps;
- bounds or unbounded analysis;
- dose grid;
- breadth/module thresholds;
- topology functional, `q`, `T`, `gamma`, sign handling, and adjacency normalization;
- pair partner-selection rule and signed/positive combination mode;
- VPPS weights;
- robustness scenarios;
- bootstrap resampling count and whether the full pipeline was repeated;
- exact-vKO handling if any post-knockout network is estimated.

## Minimum Results reporting

Show the seven raw utilities and VPPS rather than VPPS alone. Report direct target benefit and adverse downstream spillover separately. Include uncertainty beside point rankings. If ranks are close, avoid categorical language such as "the best target"; report near-ties and selection probabilities.

## Limitation paragraph scaffold

SymPerturb conditions its conclusions on the fitted network and the selected perturbation semantics. Cross-sectional undirected networks do not identify intervention direction, exclude unmeasured confounding, or establish treatment effects. Anchors, location-scale maps, thresholds, weighting, module definitions, and topology functionals are analysis choices. VPPS is normalized within the candidate set and is not transportable across analyses without re-estimation. Longitudinal and experimental validation is required before treating a ranked symptom as a clinical intervention target.
