# Research release checklist

This repository is already public. The items below distinguish the checked reference package from a complete, independently reproduced manuscript archive. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the evidence and missing artifacts.

## Documentation and reference package

- [x] Identify the current manuscript title and its cited package version/commit.
- [x] Remove the superseded draft's eight-component/regeneration warning from current-status statements.
- [x] Confirm that the package computes seven utilities and keeps robustness separate.
- [x] Distinguish smoke-test data and demonstration bootstrap settings from manuscript inputs.
- [x] Replace the citation repository-URL placeholder with the actual repository URL.
- [x] Run existing package tests and both included example configurations during the 2026-10-29 synchronization.

These checks do not establish manuscript replication or a new validated release.

## Required before claiming manuscript reproduction

- [ ] Supply the exact manuscript-specific simulation driver, full generating parameters, configuration, and seed manifest.
- [ ] Reconcile that driver with the cited package commit and verify the claimed numerical agreement.
- [ ] Reproduce all seven-utility results, centrality comparisons, knockout validity checks, and sensitivity outputs; map them to the main and supplementary tables/figures.
- [ ] Preserve per-replicate results and the uncertainty-summary code; distinguish simulation replicates, Monte Carlo draws, and bootstrap resamples.
- [ ] Archive the exact environment and run instructions, and rerun from a clean environment.
- [ ] Independently review methods, implementation, and numerical agreement, documenting unresolved discrepancies.
- [ ] Confirm final manuscript citation metadata and software author metadata; add publication details/DOI only when available.
- [ ] Check the complete research archive for patient data, credentials, private manuscripts, local paths, and private metadata.
- [ ] Confirm the copyright holders' license choice before describing the project as open source; do not assume public visibility grants a license.
- [ ] Create a versioned research release and durable archive only after verification.

## Additional validation, not claimed as completed

- [ ] Run complete-pipeline bootstrap at a prespecified count for any applied analysis that relies on bootstrap uncertainty.
- [ ] Run the broader factorial misspecification/benchmark suite before making validation claims beyond the manuscript's generating-model scope.

The last two items concern additional validation or application-specific analysis. They should not be presented as already completed, or as evidence that the existing manuscript still uses an eight-component score.
