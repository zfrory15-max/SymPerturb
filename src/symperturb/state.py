from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping
import numpy as np
from scipy.stats import norm


@dataclass
class InterventionMoments:
    mean: np.ndarray
    covariance: np.ndarray
    target_indices: tuple[int, ...]
    location_multipliers: np.ndarray
    scale_multipliers: np.ndarray


def _as_index_tuple(targets: Iterable[int], p: int) -> tuple[int, ...]:
    out = tuple(sorted({int(i) for i in targets}))
    if not out:
        raise ValueError("at least one target is required")
    if out[0] < 0 or out[-1] >= p:
        raise IndexError("target index out of range")
    return out


def _dose_vector(alpha: float | Mapping[int, float], targets: tuple[int, ...]) -> np.ndarray:
    if isinstance(alpha, Mapping):
        vals = np.array([float(alpha[i]) for i in targets], dtype=float)
    else:
        vals = np.repeat(float(alpha), len(targets))
    if np.any((vals < 0) | (vals > 1)):
        raise ValueError("all perturbation doses alpha must lie in [0, 1]")
    return vals


def map_multipliers(
    alpha: np.ndarray,
    state_map: str = "linked",
    mu_power: float = 1.0,
    sigma_power: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Return D_mu and D_sigma diagonal entries.

    linked:       D_mu = D_sigma = 1-alpha
    location_only:D_mu = 1-alpha, D_sigma = 1
    scale_only:   D_mu = 1, D_sigma = 1-alpha
    independent:  D_mu = (1-alpha)^mu_power,
                  D_sigma = (1-alpha)^sigma_power
    """
    one_minus = 1.0 - np.asarray(alpha, dtype=float)
    if state_map == "linked":
        return one_minus, one_minus
    if state_map == "location_only":
        return one_minus, np.ones_like(one_minus)
    if state_map == "scale_only":
        return np.ones_like(one_minus), one_minus
    if state_map == "independent":
        if mu_power <= 0 or sigma_power <= 0:
            raise ValueError("mu_power and sigma_power must be positive")
        return one_minus**mu_power, one_minus**sigma_power
    raise ValueError(
        "state_map must be one of: linked, location_only, scale_only, independent"
    )


def post_intervention_moments(
    mu: np.ndarray,
    covariance: np.ndarray,
    targets: Iterable[int],
    alpha: float | Mapping[int, float],
    anchors: np.ndarray | None = None,
    state_map: str = "linked",
    mu_power: float = 1.0,
    sigma_power: float = 1.0,
) -> InterventionMoments:
    """Apply the general Gaussian location-scale state intervention.

    X_S^(alpha) = c_S + D_mu(alpha)(mu_S-c_S)
                  + D_sigma(alpha)(X_S-mu_S)

    The non-target distribution is updated through the Gaussian regression
    decomposition X_K = mu_K + B(X_S-mu_S) + epsilon.
    """
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(covariance, dtype=float)
    p = len(mu)
    if sigma.shape != (p, p):
        raise ValueError("covariance shape does not match mean vector")
    s_idx = _as_index_tuple(targets, p)
    k_idx = tuple(i for i in range(p) if i not in s_idx)
    a = _dose_vector(alpha, s_idx)
    dmu, dsigma = map_multipliers(a, state_map, mu_power, sigma_power)

    if anchors is None:
        c = np.zeros(p, dtype=float)
    else:
        c = np.asarray(anchors, dtype=float)
        if c.shape != (p,):
            raise ValueError("anchors must have length p")

    S = np.array(s_idx, dtype=int)
    K = np.array(k_idx, dtype=int)
    mu_s = mu[S]
    sig_ss = sigma[np.ix_(S, S)]
    c_s = c[S]

    post_mu_s = c_s + dmu * (mu_s - c_s)
    Dsig = np.diag(dsigma)
    post_sig_ss = Dsig @ sig_ss @ Dsig

    post_mu = mu.copy()
    post_cov = np.zeros_like(sigma)
    post_mu[S] = post_mu_s
    post_cov[np.ix_(S, S)] = post_sig_ss

    if len(K) > 0:
        sig_ks = sigma[np.ix_(K, S)]
        sig_kk = sigma[np.ix_(K, K)]
        try:
            inv_ss = np.linalg.inv(sig_ss)
        except np.linalg.LinAlgError:
            inv_ss = np.linalg.pinv(sig_ss)
        B = sig_ks @ inv_ss
        omega = sig_kk - B @ sigma[np.ix_(S, K)]
        post_mu_k = mu[K] + B @ (post_mu_s - mu_s)
        post_sig_kk = omega + B @ post_sig_ss @ B.T
        post_sig_ks = B @ post_sig_ss

        post_mu[K] = post_mu_k
        post_cov[np.ix_(K, K)] = post_sig_kk
        post_cov[np.ix_(K, S)] = post_sig_ks
        post_cov[np.ix_(S, K)] = post_sig_ks.T

    post_cov = (post_cov + post_cov.T) / 2.0
    return InterventionMoments(
        mean=post_mu,
        covariance=post_cov,
        target_indices=s_idx,
        location_multipliers=dmu,
        scale_multipliers=dsigma,
    )


def clipped_normal_expectation(
    mean: np.ndarray,
    sd: np.ndarray,
    lower: float,
    upper: float,
) -> np.ndarray:
    """E[min(upper, max(lower, Y))] for normal Y.

    This is a winsorised-normal expectation, not a truncated-normal likelihood.
    """
    m = np.asarray(mean, dtype=float)
    s = np.asarray(sd, dtype=float)
    out = np.clip(m, lower, upper)
    mask = s > 1e-14
    if np.any(mask):
        mm = m[mask]
        ss = s[mask]
        a = (lower - mm) / ss
        b = (upper - mm) / ss
        out[mask] = (
            lower * norm.cdf(a)
            + mm * (norm.cdf(b) - norm.cdf(a))
            + ss * (norm.pdf(a) - norm.pdf(b))
            + upper * (1.0 - norm.cdf(b))
        )
    return out


def expected_observed_mean(
    mean: np.ndarray,
    covariance: np.ndarray,
    bounds: tuple[float, float] | None,
) -> np.ndarray:
    if bounds is None:
        return np.asarray(mean, dtype=float).copy()
    lower, upper = bounds
    sd = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    return clipped_normal_expectation(np.asarray(mean), sd, lower, upper)


def standardized_improvement(
    baseline_mean: np.ndarray,
    post_mean: np.ndarray,
    denominator_sd: np.ndarray,
) -> np.ndarray:
    den = np.asarray(denominator_sd, dtype=float)
    if np.any(den <= 0):
        raise ValueError("standardization SDs must be positive")
    return (np.asarray(baseline_mean) - np.asarray(post_mean)) / den
