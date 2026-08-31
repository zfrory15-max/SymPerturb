import numpy as np
from symperturb.topology import node_block, propagation_potential


def test_full_node_block_zeros_incident_edges():
    W = np.array([[0, .2, -.1], [.2, 0, .3], [-.1, .3, 0]], dtype=float)
    out = node_block(W, 1, 1.0)
    assert np.allclose(out[1, :], 0)
    assert np.allclose(out[:, 1], 0)


def test_propagation_is_nonnegative_with_absolute_weights():
    W = np.array([[0, -.2], [-.2, 0]], dtype=float)
    assert propagation_potential(W, T=3, gamma=.45, use_absolute=True) >= 0
