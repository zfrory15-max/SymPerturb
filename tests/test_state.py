import numpy as np
from symperturb.state import post_intervention_moments


def setup_moments():
    mu = np.array([2.0, 1.0, 1.5])
    sigma = np.array([[1.0, 0.3, 0.2], [0.3, 1.2, 0.1], [0.2, 0.1, 0.8]])
    return mu, sigma


def test_alpha_zero_recovers_baseline():
    mu, sigma = setup_moments()
    out = post_intervention_moments(mu, sigma, [0], 0.0, state_map="linked")
    assert np.allclose(out.mean, mu)
    assert np.allclose(out.covariance, sigma)


def test_exact_linked_knockout_zero_anchor_is_degenerate():
    mu, sigma = setup_moments()
    out = post_intervention_moments(mu, sigma, [0], 1.0, state_map="linked")
    assert np.isclose(out.mean[0], 0.0)
    assert np.isclose(out.covariance[0, 0], 0.0)
    assert np.allclose(out.covariance[0, 1:], 0.0)
