# SymPerturb

[**English**](README.md) | [简体中文](README_zh-CN.md)
**SymPerturb** converts a fitted cross-sectional symptom network into explicit, auditable **virtual perturbation target hypotheses**. It separates state perturbations, topology perturbations, multi-target procedures, seven utility outcomes, VPPS ranking, and uncertainty diagnostics.

> **Scientific boundary:** SymPerturb is not a causal `do()`-intervention estimator and does not establish clinical treatment efficacy. A cross-sectional undirected Gaussian graphical model supports model-based perturbation queries, not identified treatment effects.

![SymPerturb workflow](docs/symperturb-workflow.png)

## What is in this repository

This repository is designed for two uses:

1. **Agent Skill** — `.agents/skills/symperturb-analysis/` is a portable `SKILL.md` bundle following the Agent Skills structure used by OpenAI/Codex.
2. **Reference analysis package** — `src/symperturb/` provides a Python implementation of the revised seven-utility SymPerturb specification described in the manuscript.

The current manuscript explicitly notes that its reported finite-sample composite results were generated with an older eight-component exploratory score and require regeneration under the revised seven-utility rule. This repository therefore treats the **seven utility dimensions + separate robustness diagnostic** as the governing specification.

## Implemented methodology

The package implements:

- Gaussian covariance model with diagonal ridge regularisation and thresholded partial-correlation adjacency;
- general symptom-specific anchor + location-scale state intervention;
- virtual knockout (vKO) and virtual knockdown (vKD);
- virtual dosage perturbation (vDP);
- edge-level and node-centred communication blocking;
- bounded/winsorised-normal expected symptom means;
- combination perturbation with common outcome sets and signed incremental pair values;
- decision-objective sequence optimisation;
- seven utilities: efficacy, dose efficiency, breadth, cross-module reach, communication block, combination value, responsiveness;
- seven-dimension VPPS with within-candidate-set min-max normalization;
- robustness reported separately across the 13 reference sensitivity scenarios;
- complete-pipeline nonparametric bootstrap summaries;
- auditable CSV/JSON/Markdown/PNG outputs.

## Install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -e .
```

For tests:

```bash
pip install -e ".[dev]"
pytest
```

## Run the included example

```bash
symperturb \
  --data examples/synthetic_symptoms.csv \
  --modules examples/modules.csv \
  --anchors examples/anchors.csv \
  --config examples/config.yaml \
  --out example-output
```

The included dataset is a **repository smoke-test dataset**, not the manuscript simulation dataset and not patient data. A small set of generated demonstration outputs is committed under `examples/example-output/` so GitHub readers can inspect the expected file structure without running the package.

## Run on your own data

Minimum files:

- symptom matrix: one row per participant, one numeric column per symptom;
- module map: `symptom,module`.

Recommended files:

- `anchors.csv`: `symptom,anchor`;
- `weights.csv`: `symptom,weight`;
- YAML config defining scale bounds, state map, thresholds, topology settings, combination rule, bootstrap count, and optional sequence objective.

See `docs/METHODS.md` and `.agents/skills/symperturb-analysis/references/input-output-contract.md`.

## Main outputs

`target_scores.csv` should be treated as the primary target-level table. It contains all seven raw utilities, their normalized 0-100 values, VPPS, rank, direct target benefit, beneficial downstream spillover, and adverse downstream spillover. Robustness and bootstrap summaries are separate by design.

## Exact knockout warning

An exact vKO with zero residual target variance creates a constant target. Do **not** standardize that target or re-estimate a full covariance matrix while retaining it. If a post-knockout network is scientifically required, prespecify an induced network with the target removed, a topology-only edge deletion, or a soft vKO and state the estimand.

## Reproducibility status

This is a **reference implementation generated from the method specification in the supplied manuscript draft**. It should be independently code-reviewed and numerically reconciled with the authors' research code before being presented as the validated publication implementation. The manuscript itself calls for independent implementation review, regeneration of the revised seven-utility results, and complete-pipeline uncertainty analysis.

## Citation

See `CITATION.cff`. Until a DOI/version of the manuscript is available, cite the manuscript title and this repository version.

## License

No redistribution license has been selected in this generated bundle. Before making the repository public, replace `LICENSE` with the license chosen by the authors for code and method content.
