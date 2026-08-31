from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class GaussianNetwork:
    mu: np.ndarray
    covariance: np.ndarray
    precision: np.ndarray
    partial_correlations: np.ndarray
    adjacency: np.ndarray
    ridge: float
    edge_threshold: float
    used_pseudoinverse: bool


def _safe_inverse(matrix: np.ndarray) -> tuple[np.ndarray, bool]:
    try:
        return np.linalg.inv(matrix), False
    except np.linalg.LinAlgError:
        return np.linalg.pinv(matrix), True


def precision_to_partial_correlations(theta: np.ndarray) -> np.ndarray:
    d = np.sqrt(np.clip(np.diag(theta), 1e-15, None))
    denom = np.outer(d, d)
    pc = -theta / denom
    np.fill_diagonal(pc, 0.0)
    pc = (pc + pc.T) / 2.0
    return pc


def fit_gaussian_network(
    data: np.ndarray,
    ridge: float = 0.02,
    edge_threshold: float = 0.03,
) -> GaussianNetwork:
    """Fit the manuscript reference Gaussian network.

    Sigma_hat_lambda = S + ridge * diag(S), followed by inversion to obtain
    partial correlations. Partial correlations with absolute value below the
    edge threshold are set to zero for topology outcomes.
    """
    x = np.asarray(data, dtype=float)
    if x.ndim != 2 or x.shape[0] < 3:
        raise ValueError("data must be a 2D array with at least 3 rows")
    if not np.isfinite(x).all():
        raise ValueError(
            "SymPerturb reference implementation requires finite data. "
            "Handle missingness explicitly before fitting."
        )
    if ridge < 0:
        raise ValueError("ridge must be non-negative")
    if edge_threshold < 0:
        raise ValueError("edge_threshold must be non-negative")

    mu = x.mean(axis=0)
    s = np.cov(x, rowvar=False, ddof=1)
    if s.ndim == 0:
        s = np.array([[float(s)]])
    covariance = s + ridge * np.diag(np.diag(s))
    precision, used_pinv = _safe_inverse(covariance)
    pc = precision_to_partial_correlations(precision)
    adjacency = pc.copy()
    adjacency[np.abs(adjacency) < edge_threshold] = 0.0
    np.fill_diagonal(adjacency, 0.0)
    return GaussianNetwork(
        mu=mu,
        covariance=covariance,
        precision=precision,
        partial_correlations=pc,
        adjacency=adjacency,
        ridge=ridge,
        edge_threshold=edge_threshold,
        used_pseudoinverse=used_pinv,
    )
