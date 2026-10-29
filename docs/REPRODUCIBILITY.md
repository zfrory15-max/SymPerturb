# Reproducibility status

**Reviewed: 2026-10-29. Status: reference package checked; manuscript replication not established.**

## What is aligned

The current manuscript is *SymPerturb: a virtual-perturbation framework for ranking intervention targets in symptom networks*. It names package version `0.1.0` at commit [`76dd417`](https://github.com/zfrory15-max/SymPerturb/commit/76dd4178b285b80beb69f14a642e84ed1cabc7a0).

| Item | Repository evidence | Scope of the evidence |
| --- | --- | --- |
| Seven utility outcomes | `src/symperturb/analysis.py::UTILITY_COLUMNS` | Efficacy, dose efficiency, breadth, cross-module reach, communication blocking, combination value, responsiveness |
| Robustness separate from VPPS | `target_scores()`, `robustness_scenarios()`, output metadata | Scenario summaries do not enter the composite |
| State/topology/procedure distinction | `state.py`, `topology.py`, `analysis.py`, method specification | Four primitive operators; three analytic procedures |
| Software-version reference | `pyproject.toml`, `src/symperturb/__init__.py`, cited commit | Matches the package version identified by the manuscript |
| Example data/configuration | `examples/` | 360 rows, 12 symptom columns; smoke test only, not the manuscript-generating inputs |
| Automated verification | `tests/` and `.github/workflows/ci.yml` | Package checks and an example run; not reproduction of paper tables or figures |

## Manuscript-to-artifact gap

The design below is recorded to identify the required artifacts, **not** to claim it has been rerun. No new numerical paper results are supplied by this documentation update.

| Manuscript analysis | Reported design | Artifact needed for exact reproduction |
| --- | --- | --- |
| Generating network and population scores | 22 nodes, four modules; master seed `20260727` | Exact ordered node/module map, full mean/covariance or precision parameters, anchors, bounds, weights, candidate set, and population-score computation |
| Analytical/Monte Carlo comparison | 100,000 post-knockout draws per target | Actual driver, RNG/child-seed scheme, per-target analytical and sampled outputs |
| Finite-sample recovery | 200 datasets per measurement/sample-size condition; continuous and ordinal; n = 250, 500, 1,000 | Dataset-generation and fitting driver, full configuration, replicate-level scores/recovery outputs, aggregation code |
| Sensitivity | 13 analysis scenarios | Exact scenario configuration and target-by-scenario ranks used in the paper |
| Knockout covariance validity | 100 replicates, exact/removed-target/soft conditions | Driver and validity criteria with replicate-level results |
| Centrality comparison, boundary stress test, and uncertainty summaries | As specified in the current manuscript | Benchmark definitions, full settings and scripts for each reported table/figure and supplementary output |
| Numerical agreement with the package | Manuscript reports comparison with its separate driver | Executable comparison and tolerance checks against the exact cited package commit |

`examples/config.yaml` uses **25 bootstrap replicates for demonstration**. It is not a substitute for the paper's simulation replicates, Monte Carlo draws, or resampling-based summary uncertainty. The package exports aggregate scenario diagnostics in `robustness.csv`; the full target-by-scenario profile required to reproduce the paper is not an exported result of the current example CLI.

## Required completion package

Supply the authors' actual analysis artifacts rather than reconstructing or inventing a replacement that merely resembles the manuscript:

1. A manuscript-specific simulation runner and exact configuration, including the generating parameters and deterministic seed/child-seed mapping.
2. An environment lock or equivalent recorded dependency versions. The package's broad minimum dependency bounds are not an exact research environment.
3. A documented command sequence from clean checkout to outputs, with expected runtime and resource requirements.
4. A manifest mapping each main/supplementary table and figure to its producing command, input files, output files, and expected numerical tolerances. Include file checksums where appropriate.
5. A verification report separating exact reproduction, numerical-tolerance agreement, known discrepancies, and checks not performed.
6. A versioned commit/tag and durable archive once the authors have reviewed the complete package. Add a DOI only if one actually exists.

Do not include patient data, private manuscript files, editorial correspondence, credentials, or personal contact details. License selection remains the copyright holders' decision.

## Checks performed in this synchronization

- The existing seven tests passed before documentation changes.
- Both `examples/config-ci.yaml` and `examples/config.yaml` completed through the CLI on the included synthetic data. The full example exercised scenario summaries, 25 demonstration bootstrap replicates, and sequence optimization.
- Additional regression tests check the exact seven-utility set, equal-weight VPPS arithmetic, and that running robustness scenarios does not alter the baseline target scores.
- No manuscript-specific simulation, numerical table/figure reproduction, or independent research-code reconciliation was performed.

For the final test count and remote CI outcome, use the checks attached to the documentation-synchronization commit. A green CI run does not change the manuscript-replication status above.
