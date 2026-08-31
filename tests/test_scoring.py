import numpy as np
import pandas as pd
from symperturb.scoring import minmax_0_100, add_vpps


def test_constant_dimension_is_neutral_50():
    assert np.allclose(minmax_0_100([2, 2, 2]), [50, 50, 50])


def test_vpps_ranking():
    raw = pd.DataFrame({"target": ["a", "b"], "u1": [0.0, 1.0], "u2": [2.0, 2.0]})
    out = add_vpps(raw, ["u1", "u2"])
    assert out.loc[out.target == "b", "vpps"].iloc[0] > out.loc[out.target == "a", "vpps"].iloc[0]
