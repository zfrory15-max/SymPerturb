import numpy as np
import pandas as pd
from symperturb.analysis import SymPerturbAnalyzer, UTILITY_COLUMNS


def make_data(seed=1):
    rng = np.random.default_rng(seed)
    cov = np.eye(6)
    cov[0, 1] = cov[1, 0] = .35
    cov[1, 2] = cov[2, 1] = .25
    cov[3, 4] = cov[4, 3] = .30
    cov[2, 3] = cov[3, 2] = .20
    x = rng.multivariate_normal(np.repeat(2.0, 6), cov, size=120)
    x = np.clip(x, 0, 4)
    cols = [f"S{i+1}" for i in range(6)]
    return pd.DataFrame(x, columns=cols), {c: ("A" if i < 3 else "B") for i, c in enumerate(cols)}


def test_full_target_table_has_seven_utilities_and_separate_robustness():
    data, modules = make_data()
    cfg = {"run_robustness_scenarios": False, "bootstrap_replicates": 0, "combination_partner_k": 2}
    result = SymPerturbAnalyzer(data, modules, config=cfg).run()
    for col in UTILITY_COLUMNS:
        assert col in result.target_scores.columns
    assert "robustness" not in UTILITY_COLUMNS
    assert result.target_scores["vpps"].between(0, 100).all()


def test_vpps_uses_exactly_seven_equal_weight_utilities():
    expected = [
        "efficacy", "dose_efficiency", "breadth", "cross_module",
        "communication_block", "combination_value", "responsiveness",
    ]
    assert UTILITY_COLUMNS == expected
    data, modules = make_data()
    result = SymPerturbAnalyzer(
        data, modules,
        config={"run_robustness_scenarios": False, "bootstrap_replicates": 0},
    ).run()
    normalized = result.target_scores[[f"{name}_norm" for name in expected]]
    np.testing.assert_allclose(
        result.target_scores["vpps"].to_numpy(), normalized.mean(axis=1).to_numpy()
    )
    assert result.metadata["vpps_dimensions"] == expected
    assert result.metadata["robustness_in_vpps"] is False


def test_robustness_scenarios_do_not_change_baseline_target_scores():
    data, modules = make_data()
    cfg = {"bootstrap_replicates": 0, "combination_partner_k": 2}
    without = SymPerturbAnalyzer(
        data, modules, config={**cfg, "run_robustness_scenarios": False}
    ).run()
    with_scenarios = SymPerturbAnalyzer(
        data, modules, config={**cfg, "run_robustness_scenarios": True}
    ).run()
    pd.testing.assert_frame_equal(without.target_scores, with_scenarios.target_scores)
    assert without.robustness.empty
    assert len(with_scenarios.robustness) == len(data.columns)
    assert "robustness_diagnostic" in with_scenarios.robustness.columns
    assert "robustness_diagnostic" not in with_scenarios.target_scores.columns
