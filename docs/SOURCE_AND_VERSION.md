# Source and version note

## Current manuscript alignment

Documentation reviewed on **2026-10-29** against the author-supplied manuscript titled:

**SymPerturb: a virtual-perturbation framework for ranking intervention targets in symptom networks**

The current manuscript specifies four primitive operators, three analytic procedures, and **seven utility outcomes with robustness reported separately**. Its software section identifies Python package version **0.1.0**, commit [`76dd4178b285b80beb69f14a642e84ed1cabc7a0`](https://github.com/zfrory15-max/SymPerturb/commit/76dd4178b285b80beb69f14a642e84ed1cabc7a0). This commit is present in the repository and its `UTILITY_COLUMNS` contains seven utilities, not robustness.

The manuscript also describes a simulation driver that reused the package's perturbation/scoring functions. That driver and the full generating parameters have not been located in the repository reviewed here. The manuscript's numerical verification claims are therefore **reported manuscript results, not independently reproduced repository results**. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the missing artifact mapping.

## Historical provenance

The repository scaffold dates to **2026-08-31**. It was initially documented against an earlier draft titled *SymPerturb converts symptom-network structure into testable intervention priorities*. That draft's eight-component/regeneration warning is historical; it must not be attributed to the current manuscript, which reports seven-utility analyses.

The 2026-10-29 synchronization updates documentation, citation URL/title references, and regression-test coverage. It does **not** change package equations, defaults, numerical outputs, the package version (`0.1.0`), or the existing license. It does not create a new research release or establish manuscript replication.

The bundled synthetic example remains a smoke-test dataset, not the manuscript's reported 22-node generating dataset. The original software-author metadata is retained; it should not be read as a verified author list for a later manuscript version.
