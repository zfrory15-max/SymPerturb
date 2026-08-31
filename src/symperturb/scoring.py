from __future__ import annotations

from typing import Sequence
import numpy as np
import pandas as pd


def minmax_0_100(values: Sequence[float]) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    finite = np.isfinite(x)
    out = np.full(x.shape, np.nan, dtype=float)
    if not finite.any():
        return out
    lo = np.nanmin(x)
    hi = np.nanmax(x)
    if np.isclose(lo, hi):
        out[finite] = 50.0
    else:
        out[finite] = 100.0 * (x[finite] - lo) / (hi - lo)
    return out


def add_vpps(
    raw: pd.DataFrame,
    utility_columns: list[str],
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    out = raw.copy()
    norm_cols: list[str] = []
    for col in utility_columns:
        ncol = f"{col}_norm"
        out[ncol] = minmax_0_100(out[col].to_numpy())
        norm_cols.append(ncol)
    if weights is None:
        w = np.ones(len(utility_columns), dtype=float)
    else:
        w = np.array([float(weights.get(c, 1.0)) for c in utility_columns])
    if np.any(w < 0) or np.isclose(w.sum(), 0):
        raise ValueError("VPPS weights must be non-negative with a positive sum")
    vals = out[norm_cols].to_numpy(dtype=float)
    out["vpps"] = np.average(vals, axis=1, weights=w)
    out["rank"] = out["vpps"].rank(method="min", ascending=False).astype(int)
    return out
