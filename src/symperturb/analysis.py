from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Any, Iterable, Mapping
import json
import math
import warnings

import numpy as np
import pandas as pd
import yaml

from .network import GaussianNetwork, fit_gaussian_network
from .state import (
    expected_observed_mean,
    post_intervention_moments,
    standardized_improvement,
)
from .topology import (
    communication_block_score,
    propagation_potential,
    spectral_radius,
)
from .scoring import add_vpps, minmax_0_100


UTILITY_COLUMNS = [
    "efficacy",
    "dose_efficiency",
    "breadth",
    "cross_module",
    "communication_block",
    "combination_value",
    "responsiveness",
]


DEFAULT_CONFIG: dict[str, Any] = {
    "ridge": 0.02,
    "edge_threshold": 0.03,
    "bounds": [0.0, 4.0],
    "state_map": "linked",
    "mu_power": 1.0,
    "sigma_power": 1.0,
    "dose_grid": [0.0, 0.10, 0.25, 0.50, 0.75, 1.0],
    "dose_efficiency_grid": [0.25, 0.50, 0.75],
    "responsiveness_epsilon": 0.10,
    "breadth_threshold": 0.10,
    "module_threshold": 0.20,
    "block_fraction": 0.80,
    "propagation_steps": 6,
    "propagation_gamma": 0.45,
    "propagation_absolute": True,
    "adjacency_normalization": "raw",
    "combination_partner_k": 5,
    "combination_mode": "signed",
    "vpps_weights": {},
    "bootstrap_replicates": 0,
    "bootstrap_top_k": 5,
    "random_seed": 20260727,
    "run_robustness_scenarios": True,
    "sequence_length": 0,
    "sequence_pool": 8,
    "sequence_beam_width": 20,
    "sequence_eta": 0.90,
    "sequence_cost_lambda": 0.0,
}


@dataclass
class AnalysisResult:
    target_scores: pd.DataFrame
    dose_response: pd.DataFrame
    pair_scores: pd.DataFrame
    robustness: pd.DataFrame
    bootstrap: pd.DataFrame
    sequence: pd.DataFrame
    network_edges: pd.DataFrame
    metadata: dict[str, Any]


def load_config(path_or_dict: str | Path | Mapping[str, Any] | None) -> dict[str, Any]:
    cfg = deepcopy(DEFAULT_CONFIG)
    if path_or_dict is None:
        return cfg
    if isinstance(path_or_dict, (str, Path)):
        with open(path_or_dict, "r", encoding="utf-8") as f:
            user = yaml.safe_load(f) or {}
    else:
        user = dict(path_or_dict)
    cfg.update(user)
    return cfg


class SymPerturbAnalyzer:
    def __init__(
        self,
        data: pd.DataFrame,
        modules: Mapping[str, str],
        anchors: Mapping[str, float] | None = None,
        symptom_weights: Mapping[str, float] | None = None,
        candidate_targets: Iterable[str] | None = None,
        config: Mapping[str, Any] | None = None,
        costs: Mapping[str, float] | None = None,
    ) -> None:
        self.config = load_config(config)
        self.data = data.copy()
        if self.data.empty:
            raise ValueError("input data is empty")
        if self.data.columns.duplicated().any():
            raise ValueError("symptom column names must be unique")
        self.columns = list(self.data.columns)
        self.p = len(self.columns)
        if self.p < 3:
            raise ValueError("SymPerturb requires at least 3 symptom variables")
        for col in self.columns:
            self.data[col] = pd.to_numeric(self.data[col], errors="raise")
        if self.data.isna().any().any():
            raise ValueError(
                "Missing data detected. The manuscript reference implementation does not "
                "define a missing-data estimator; preprocess or impute explicitly first."
            )
        if not np.isfinite(self.data.to_numpy(dtype=float)).all():
            raise ValueError("input contains non-finite values")

        missing_modules = [c for c in self.columns if c not in modules]
        if missing_modules:
            raise ValueError(f"module mapping missing symptoms: {missing_modules}")
        self.modules = {c: str(modules[c]) for c in self.columns}
        if len(set(self.modules.values())) < 2:
            raise ValueError("cross-module utility requires at least two modules")

        self.anchors = np.array(
            [0.0 if anchors is None else float(anchors.get(c, 0.0)) for c in self.columns]
        )
        self.weights = np.array(
            [1.0 if symptom_weights is None else float(symptom_weights.get(c, 1.0)) for c in self.columns]
        )
        if np.any(self.weights < 0) or np.isclose(self.weights.sum(), 0):
            raise ValueError("symptom weights must be non-negative with positive total")

        if candidate_targets is None:
            self.candidate_targets = self.columns.copy()
        else:
            self.candidate_targets = [str(c) for c in candidate_targets]
            unknown = [c for c in self.candidate_targets if c not in self.columns]
            if unknown:
                raise ValueError(f"unknown candidate targets: {unknown}")
        if len(self.candidate_targets) < 2:
            raise ValueError("at least two candidate targets are required for relative VPPS")

        self.index = {c: i for i, c in enumerate(self.columns)}
        self.costs = {c: 0.0 if costs is None else float(costs.get(c, 0.0)) for c in self.columns}
        self.network: GaussianNetwork | None = None
        self._baseline_observed: np.ndarray | None = None
        self._denominator_sd: np.ndarray | None = None

    @property
    def bounds(self) -> tuple[float, float] | None:
        b = self.config.get("bounds")
        return None if b is None else (float(b[0]), float(b[1]))

    def fit(self) -> GaussianNetwork:
        self.network = fit_gaussian_network(
            self.data.to_numpy(dtype=float),
            ridge=float(self.config["ridge"]),
            edge_threshold=float(self.config["edge_threshold"]),
        )
        self._baseline_observed = expected_observed_mean(
            self.network.mu, self.network.covariance, self.bounds
        )
        self._denominator_sd = np.sqrt(np.clip(np.diag(self.network.covariance), 1e-15, None))
        return self.network

    def _require_fit(self) -> GaussianNetwork:
        return self.fit() if self.network is None else self.network

    def _post(self, targets: Iterable[int], alpha: float | Mapping[int, float]):
        net = self._require_fit()
        return post_intervention_moments(
            net.mu,
            net.covariance,
            targets,
            alpha,
            anchors=self.anchors,
            state_map=str(self.config["state_map"]),
            mu_power=float(self.config.get("mu_power", 1.0)),
            sigma_power=float(self.config.get("sigma_power", 1.0)),
        )

    def _delta_for_targets(self, targets: Iterable[int], alpha: float) -> np.ndarray:
        post = self._post(targets, alpha)
        post_obs = expected_observed_mean(post.mean, post.covariance, self.bounds)
        return standardized_improvement(
            self._baseline_observed, post_obs, self._denominator_sd
        )

    def _system_benefit(self, delta: np.ndarray, outcome_indices: Iterable[int]) -> float:
        idx = np.array(list(outcome_indices), dtype=int)
        if len(idx) == 0:
            return 0.0
        w = self.weights[idx]
        if np.isclose(w.sum(), 0):
            return float(np.mean(delta[idx]))
        return float(np.average(delta[idx], weights=w))

    def _single_target_profile(self, name: str) -> tuple[dict[str, float], list[dict[str, float]]]:
        net = self._require_fit()
        j = self.index[name]
        other = [i for i in range(self.p) if i != j]
        dose_rows = []
        dose_values: dict[float, float] = {}
        delta_full = None
        for alpha in [float(a) for a in self.config["dose_grid"]]:
            delta = self._delta_for_targets([j], alpha)
            g = self._system_benefit(delta, other)
            dose_values[alpha] = g
            dose_rows.append({"target": name, "alpha": alpha, "system_benefit": g})
            if np.isclose(alpha, 1.0):
                delta_full = delta
        if delta_full is None:
            delta_full = self._delta_for_targets([j], 1.0)
            dose_values[1.0] = self._system_benefit(delta_full, other)
            dose_rows.append({"target": name, "alpha": 1.0, "system_benefit": dose_values[1.0]})

        eff = dose_values[1.0]
        dg = [float(a) for a in self.config["dose_efficiency_grid"]]
        vals = []
        for a in dg:
            if a <= 0:
                continue
            if a not in dose_values:
                d = self._delta_for_targets([j], a)
                dose_values[a] = self._system_benefit(d, other)
            vals.append(dose_values[a] / a)
        dose_eff = float(np.mean(vals)) if vals else np.nan

        tau = float(self.config["breadth_threshold"])
        breadth = float(np.mean(delta_full[other] >= tau))

        target_module = self.modules[name]
        other_modules = sorted({m for m in self.modules.values() if m != target_module})
        reached = []
        module_tau = float(self.config["module_threshold"])
        for mod in other_modules:
            midx = [self.index[c] for c in self.columns if self.modules[c] == mod]
            reached.append(float(np.mean(delta_full[midx])) >= module_tau)
        cross = float(np.mean(reached)) if reached else 0.0

        comm = communication_block_score(
            net.adjacency,
            j,
            q=float(self.config["block_fraction"]),
            T=int(self.config["propagation_steps"]),
            gamma=float(self.config["propagation_gamma"]),
            use_absolute=bool(self.config["propagation_absolute"]),
            normalization=str(self.config["adjacency_normalization"]),
        )

        eps = float(self.config["responsiveness_epsilon"])
        if eps not in dose_values:
            d = self._delta_for_targets([j], eps)
            dose_values[eps] = self._system_benefit(d, other)
        if 0.0 not in dose_values:
            d = self._delta_for_targets([j], 0.0)
            dose_values[0.0] = self._system_benefit(d, other)
        responsiveness = (dose_values[eps] - dose_values[0.0]) / eps

        direct_delta = float(delta_full[j])
        beneficial = float(np.mean(np.maximum(delta_full[other], 0.0)))
        adverse = float(np.mean(np.maximum(-delta_full[other], 0.0)))

        row = {
            "target": name,
            "efficacy": eff,
            "dose_efficiency": dose_eff,
            "breadth": breadth,
            "cross_module": cross,
            "communication_block": comm,
            "responsiveness": responsiveness,
            "direct_target_benefit": direct_delta,
            "beneficial_spillover_mean": beneficial,
            "adverse_spillover_mean": adverse,
        }
        return row, dose_rows

    def _pair_increment(self, a: str, b: str) -> dict[str, float]:
        ia, ib = self.index[a], self.index[b]
        outcome = [i for i in range(self.p) if i not in (ia, ib)]
        d_joint = self._delta_for_targets([ia, ib], 1.0)
        d_a = self._delta_for_targets([ia], 1.0)
        d_b = self._delta_for_targets([ib], 1.0)
        g_joint = self._system_benefit(d_joint, outcome)
        g_a = self._system_benefit(d_a, outcome)
        g_b = self._system_benefit(d_b, outcome)
        incr = g_joint - max(g_a, g_b)
        return {
            "target_a": a,
            "target_b": b,
            "joint_benefit_common_set": g_joint,
            "single_a_common_set": g_a,
            "single_b_common_set": g_b,
            "incremental_pair_value": incr,
        }

    def _combination_scores(self, base: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
        ranking = base.sort_values("efficacy", ascending=False)["target"].tolist()
        k = max(1, min(int(self.config["combination_partner_k"]), len(ranking) - 1))
        pair_cache: dict[tuple[str, str], dict[str, float]] = {}
        per_target: dict[str, list[float]] = {t: [] for t in self.candidate_targets}
        for target in self.candidate_targets:
            partners = [x for x in ranking if x != target][:k]
            for partner in partners:
                key = tuple(sorted((target, partner)))
                if key not in pair_cache:
                    pair_cache[key] = self._pair_increment(*key)
                val = pair_cache[key]["incremental_pair_value"]
                per_target[target].append(val)
        mode = str(self.config.get("combination_mode", "signed"))
        out: dict[str, float] = {}
        for target, vals in per_target.items():
            arr = np.array(vals, dtype=float)
            if mode == "signed":
                out[target] = float(arr.mean()) if arr.size else 0.0
            elif mode == "positive":
                out[target] = float(np.maximum(arr, 0.0).mean()) if arr.size else 0.0
            else:
                raise ValueError("combination_mode must be signed or positive")
        pairs = pd.DataFrame(list(pair_cache.values()))
        return pairs, out

    def target_scores(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        rows = []
        dose_rows = []
        for name in self.candidate_targets:
            row, dr = self._single_target_profile(name)
            rows.append(row)
            dose_rows.extend(dr)
        base = pd.DataFrame(rows)
        pairs, comb = self._combination_scores(base)
        base["combination_value"] = base["target"].map(comb).astype(float)
        scored = add_vpps(base, UTILITY_COLUMNS, self.config.get("vpps_weights") or None)
        scored = scored.sort_values(["rank", "target"]).reset_index(drop=True)
        return scored, pd.DataFrame(dose_rows).sort_values(["target", "alpha"]), pairs

    def _network_edges(self) -> pd.DataFrame:
        net = self._require_fit()
        rows = []
        for i in range(self.p):
            for j in range(i + 1, self.p):
                if net.adjacency[i, j] != 0:
                    rows.append(
                        {
                            "source": self.columns[i],
                            "target": self.columns[j],
                            "partial_correlation": net.partial_correlations[i, j],
                            "thresholded_weight": net.adjacency[i, j],
                        }
                    )
        return pd.DataFrame(rows)

    def robustness_scenarios(self) -> pd.DataFrame:
        if not bool(self.config.get("run_robustness_scenarios", True)):
            return pd.DataFrame()
        variants: list[tuple[str, dict[str, Any]]] = [
            ("reference", {}),
            ("ridge_0", {"ridge": 0.0}),
            ("ridge_0.05", {"ridge": 0.05}),
            ("breadth_0.05", {"breadth_threshold": 0.05}),
            ("breadth_0.15", {"breadth_threshold": 0.15}),
            ("module_0.10", {"module_threshold": 0.10}),
            ("module_0.30", {"module_threshold": 0.30}),
            ("gamma_0.35", {"propagation_gamma": 0.35}),
            ("gamma_0.55", {"propagation_gamma": 0.55}),
            ("block_0.60", {"block_fraction": 0.60}),
            ("block_1.00", {"block_fraction": 1.00}),
            ("partner_3", {"combination_partner_k": 3}),
            ("partner_8", {"combination_partner_k": 8}),
        ]
        rank_rows = []
        for label, update in variants:
            cfg = deepcopy(self.config)
            cfg.update(update)
            cfg["run_robustness_scenarios"] = False
            cfg["bootstrap_replicates"] = 0
            cfg["sequence_length"] = 0
            sub = SymPerturbAnalyzer(
                self.data,
                self.modules,
                anchors={c: self.anchors[self.index[c]] for c in self.columns},
                symptom_weights={c: self.weights[self.index[c]] for c in self.columns},
                candidate_targets=self.candidate_targets,
                config=cfg,
                costs=self.costs,
            )
            scores, _, _ = sub.target_scores()
            for _, r in scores.iterrows():
                rank_rows.append(
                    {"scenario": label, "target": r["target"], "rank": int(r["rank"]), "vpps": r["vpps"]}
                )
        ranks = pd.DataFrame(rank_rows)
        sd = ranks.groupby("target")["rank"].std(ddof=0)
        max_sd = float(sd.max()) if len(sd) else 0.0
        rob = 1.0 - sd / max_sd if max_sd > 0 else pd.Series(1.0, index=sd.index)
        summary = pd.DataFrame(
            {
                "target": sd.index,
                "scenario_rank_sd": sd.values,
                "robustness_diagnostic": rob.values,
                "best_scenario_rank": ranks.groupby("target")["rank"].min().reindex(sd.index).values,
                "worst_scenario_rank": ranks.groupby("target")["rank"].max().reindex(sd.index).values,
            }
        )
        return summary.sort_values("robustness_diagnostic", ascending=False).reset_index(drop=True)

    def bootstrap(self) -> pd.DataFrame:
        B = int(self.config.get("bootstrap_replicates", 0))
        if B <= 0:
            return pd.DataFrame()
        rng = np.random.default_rng(int(self.config["random_seed"]))
        n = len(self.data)
        records = []
        top_k = min(int(self.config.get("bootstrap_top_k", 5)), len(self.candidate_targets))
        for b in range(B):
            idx = rng.integers(0, n, size=n)
            boot_data = self.data.iloc[idx].reset_index(drop=True)
            cfg = deepcopy(self.config)
            cfg["bootstrap_replicates"] = 0
            cfg["run_robustness_scenarios"] = False
            cfg["sequence_length"] = 0
            sub = SymPerturbAnalyzer(
                boot_data,
                self.modules,
                anchors={c: self.anchors[self.index[c]] for c in self.columns},
                symptom_weights={c: self.weights[self.index[c]] for c in self.columns},
                candidate_targets=self.candidate_targets,
                config=cfg,
                costs=self.costs,
            )
            scores, _, _ = sub.target_scores()
            for _, r in scores.iterrows():
                records.append(
                    {
                        "replicate": b + 1,
                        "target": r["target"],
                        "vpps": float(r["vpps"]),
                        "rank": int(r["rank"]),
                        "top_k": int(r["rank"] <= top_k),
                    }
                )
        raw = pd.DataFrame(records)
        out_rows = []
        for target, g in raw.groupby("target"):
            out_rows.append(
                {
                    "target": target,
                    "vpps_median": g["vpps"].median(),
                    "vpps_q025": g["vpps"].quantile(0.025),
                    "vpps_q975": g["vpps"].quantile(0.975),
                    "rank_median": g["rank"].median(),
                    "rank_q025": g["rank"].quantile(0.025),
                    "rank_q975": g["rank"].quantile(0.975),
                    "top_k_selection_probability": g["top_k"].mean(),
                    "replicates": len(g),
                }
            )
        return pd.DataFrame(out_rows).sort_values(
            ["rank_median", "target"]
        ).reset_index(drop=True)

    def _set_benefit(self, names: Iterable[str]) -> float:
        names = list(names)
        if not names:
            return 0.0
        idx = [self.index[n] for n in names]
        outcome = [i for i in range(self.p) if i not in idx]
        delta = self._delta_for_targets(idx, 1.0)
        return self._system_benefit(delta, outcome)

    def sequence_optimization(self, base_scores: pd.DataFrame) -> pd.DataFrame:
        L = int(self.config.get("sequence_length", 0))
        if L <= 0:
            return pd.DataFrame()
        pool_n = min(int(self.config.get("sequence_pool", 8)), len(self.candidate_targets))
        pool = base_scores.sort_values("efficacy", ascending=False)["target"].head(pool_n).tolist()
        L = min(L, len(pool))
        eta = float(self.config.get("sequence_eta", 0.90))
        lam = float(self.config.get("sequence_cost_lambda", 0.0))
        beam_width = max(1, int(self.config.get("sequence_beam_width", 20)))
        beam: list[tuple[tuple[str, ...], float, float]] = [(tuple(), 0.0, 0.0)]
        for t in range(1, L + 1):
            cand = []
            for seq, objective, prev_g in beam:
                for name in pool:
                    if name in seq:
                        continue
                    new_seq = seq + (name,)
                    g = self._set_benefit(new_seq)
                    marginal = g - prev_g
                    obj = objective + (eta ** (t - 1)) * marginal - lam * self.costs[name]
                    cand.append((new_seq, obj, g))
            cand.sort(key=lambda x: x[1], reverse=True)
            beam = cand[:beam_width]
        rows = []
        for rank, (seq, obj, g) in enumerate(beam, start=1):
            rows.append(
                {
                    "sequence_rank": rank,
                    "sequence": " -> ".join(seq),
                    "objective": obj,
                    "final_set_benefit": g,
                    "length": len(seq),
                }
            )
        return pd.DataFrame(rows)

    def run(self) -> AnalysisResult:
        self.fit()
        target_scores, dose_response, pair_scores = self.target_scores()
        robustness = self.robustness_scenarios()
        bootstrap = self.bootstrap()
        sequence = self.sequence_optimization(target_scores)
        net = self._require_fit()
        rho = spectral_radius(float(self.config["propagation_gamma"]) * np.abs(net.adjacency))
        metadata = {
            "n": int(len(self.data)),
            "p": int(self.p),
            "candidate_targets": int(len(self.candidate_targets)),
            "ridge": float(self.config["ridge"]),
            "edge_threshold": float(self.config["edge_threshold"]),
            "state_map": self.config["state_map"],
            "bounds": self.config.get("bounds"),
            "combination_mode": self.config.get("combination_mode", "signed"),
            "vpps_dimensions": UTILITY_COLUMNS,
            "robustness_in_vpps": False,
            "used_pseudoinverse": bool(net.used_pseudoinverse),
            "spectral_radius_gamma_absW": rho,
            "causal_interpretation": False,
            "notes": [
                "VPPS is normalized within the prespecified candidate set and is not comparable across candidate sets without reanalysis.",
                "Robustness is reported separately as an uncertainty diagnostic.",
                "A cross-sectional undirected GGM does not identify a causal treatment effect.",
                "Exact vKO should not be followed by full-network covariance re-estimation with a constant target column.",
            ],
        }
        return AnalysisResult(
            target_scores=target_scores,
            dose_response=dose_response,
            pair_scores=pair_scores,
            robustness=robustness,
            bootstrap=bootstrap,
            sequence=sequence,
            network_edges=self._network_edges(),
            metadata=metadata,
        )


def run_analysis(
    data: pd.DataFrame,
    modules: Mapping[str, str],
    **kwargs: Any,
) -> AnalysisResult:
    return SymPerturbAnalyzer(data, modules, **kwargs).run()


def save_result(result: AnalysisResult, output_dir: str | Path) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result.target_scores.to_csv(out / "target_scores.csv", index=False)
    result.dose_response.to_csv(out / "dose_response.csv", index=False)
    result.pair_scores.to_csv(out / "pair_scores.csv", index=False)
    result.robustness.to_csv(out / "robustness.csv", index=False)
    result.bootstrap.to_csv(out / "bootstrap_summary.csv", index=False)
    result.sequence.to_csv(out / "sequence_optimization.csv", index=False)
    result.network_edges.to_csv(out / "network_edges.csv", index=False)
    with open(out / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(result.metadata, f, indent=2, ensure_ascii=False)
    _write_report(result, out / "report.md")
    _write_plots(result, out)
    return out


def _write_report(result: AnalysisResult, path: Path) -> None:
    top = result.target_scores.head(10)
    lines = [
        "# SymPerturb analysis report",
        "",
        "> **Interpretation boundary:** These are model-derived virtual perturbation priorities, not identified causal treatment effects.",
        "",
        "## Analysis summary",
        "",
        f"- n = {result.metadata['n']}; p = {result.metadata['p']}",
        f"- State map: `{result.metadata['state_map']}`",
        f"- Seven-utility VPPS; robustness is separate: `{not result.metadata['robustness_in_vpps']}`",
        f"- gamma|W| spectral radius: {result.metadata['spectral_radius_gamma_absW']:.3f}",
        "",
        "## Highest-ranked targets",
        "",
        top[["rank", "target", "vpps", "efficacy", "combination_value", "adverse_spillover_mean"]].to_markdown(index=False),
        "",
        "## Required reporting cautions",
        "",
        "- VPPS is a relative within-candidate-set ranking; do not compare raw VPPS values across networks or cohorts as if they were transportable clinical utilities.",
        "- Report the seven unaggregated utilities next to VPPS.",
        "- Report robustness/uncertainty separately using scenario ranks and, when requested, complete-pipeline bootstrap summaries.",
        "- Do not describe communication blocking as biological signal interruption; it is an adjacency attenuation operation.",
        "- Do not interpret sequence optimisation as biological time ordering in a cross-sectional undirected network.",
    ]
    if not result.bootstrap.empty:
        lines += ["", "## Bootstrap uncertainty", "", result.bootstrap.head(10).to_markdown(index=False)]
    if not result.sequence.empty:
        lines += ["", "## Sequence optimisation", "", result.sequence.head(10).to_markdown(index=False)]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_plots(result: AnalysisResult, out: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return
    scores = result.target_scores.sort_values("vpps", ascending=True)
    fig, ax = plt.subplots(figsize=(8, max(4, len(scores) * 0.28)))
    ax.barh(scores["target"], scores["vpps"])
    ax.set_xlabel("VPPS (0-100, within candidate set)")
    ax.set_title("SymPerturb target priorities")
    fig.tight_layout()
    fig.savefig(out / "vpps_ranking.png", dpi=180)
    plt.close(fig)

    dose = result.dose_response
    fig, ax = plt.subplots(figsize=(8, 5))
    for target in result.target_scores.head(min(5, len(result.target_scores)))["target"]:
        g = dose[dose["target"] == target]
        ax.plot(g["alpha"], g["system_benefit"], marker="o", label=target)
    ax.set_xlabel("Perturbation dose alpha")
    ax.set_ylabel("Downstream system benefit")
    ax.set_title("Dose-response curves: top VPPS targets")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "dose_response_top_targets.png", dpi=180)
    plt.close(fig)
