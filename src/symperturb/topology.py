from __future__ import annotations

import numpy as np


def edge_block(W: np.ndarray, u: int, v: int, q: float) -> np.ndarray:
    if not 0 <= q <= 1:
        raise ValueError("q must lie in [0,1]")
    out = np.array(W, dtype=float, copy=True)
    out[u, v] *= 1.0 - q
    out[v, u] *= 1.0 - q
    return out


def node_block(W: np.ndarray, j: int, q: float) -> np.ndarray:
    if not 0 <= q <= 1:
        raise ValueError("q must lie in [0,1]")
    out = np.array(W, dtype=float, copy=True)
    out[j, :] *= 1.0 - q
    out[:, j] *= 1.0 - q
    out[j, j] = 0.0
    return out


def spectral_radius(A: np.ndarray) -> float:
    vals = np.linalg.eigvals(np.asarray(A, dtype=float))
    return float(np.max(np.abs(vals))) if vals.size else 0.0


def normalize_adjacency(W: np.ndarray, mode: str = "raw") -> np.ndarray:
    A = np.asarray(W, dtype=float)
    if mode == "raw":
        return A.copy()
    if mode == "row":
        denom = np.sum(np.abs(A), axis=1)
        denom = np.where(denom > 0, denom, 1.0)
        return A / denom[:, None]
    if mode == "spectral":
        r = spectral_radius(np.abs(A))
        return A.copy() if r <= 1e-15 else A / r
    raise ValueError("adjacency normalization must be raw, row, or spectral")


def propagation_potential(
    W: np.ndarray,
    T: int = 6,
    gamma: float = 0.45,
    use_absolute: bool = True,
    normalization: str = "raw",
) -> float:
    if T < 1:
        raise ValueError("T must be >=1")
    if gamma < 0:
        raise ValueError("gamma must be non-negative")
    A = normalize_adjacency(W, normalization)
    A = np.abs(A) if use_absolute else A
    A = gamma * A
    power = np.eye(A.shape[0])
    total = np.zeros_like(A)
    for _ in range(T):
        power = power @ A
        total += power
    ones = np.ones(A.shape[0])
    return float(ones @ total @ ones)


def communication_block_score(
    W: np.ndarray,
    j: int,
    q: float = 0.80,
    T: int = 6,
    gamma: float = 0.45,
    use_absolute: bool = True,
    normalization: str = "raw",
) -> float:
    base = propagation_potential(W, T, gamma, use_absolute, normalization)
    blocked = propagation_potential(
        node_block(W, j, q), T, gamma, use_absolute, normalization
    )
    if abs(base) < 1e-15:
        return 0.0
    return (base - blocked) / base
