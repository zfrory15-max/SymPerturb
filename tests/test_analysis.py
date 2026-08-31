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
