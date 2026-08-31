# Input-output contract

## Required input data

### Symptom matrix CSV

Rows are independent participants/observations; columns are symptom variables. The current reference implementation requires finite numeric values and does not silently impute missing data.

### Module map CSV

Columns:

- `symptom`
- `module`

Every symptom column must have exactly one module. Cross-module utility requires at least two modules.

## Optional inputs

### Anchor CSV

Columns `symptom,anchor`. Unspecified anchors default to zero, but zero should only be used when clinically interpretable for that symptom.

### Weight CSV

Columns `symptom,weight`. Weights must be non-negative. These define the downstream system-benefit aggregation, not VPPS dimension weights.

### Candidate file

One symptom name per line. VPPS is normalized within this set.

### Cost CSV

Columns `symptom,cost`. Used only by sequence optimisation.

### YAML config

See repository `examples/config.yaml` for all common controls.

## Main outputs

- `target_scores.csv`: raw utilities, normalized utilities, VPPS, rank, direct target benefit, beneficial spillover, adverse spillover.
- `dose_response.csv`: target-by-dose downstream system benefit.
- `pair_scores.csv`: joint and single-target common-outcome benefits and signed incremental pair value.
- `robustness.csv`: scenario rank SD and separate robustness diagnostic.
- `bootstrap_summary.csv`: VPPS/rank intervals and top-k selection probability when bootstrap is enabled.
- `sequence_optimization.csv`: best decision-objective sequences when enabled.
- `network_edges.csv`: thresholded partial-correlation edges.
- `metadata.json`: model settings and interpretation warnings.
- `report.md`: concise auditable report.
- `vpps_ranking.png`, `dose_response_top_targets.png`: summary plots.
