"""Week 03 broken-first energy diagnostic.

This file runs, but the physics is wrong in three places.
Students should diagnose the bugs before coding the fixed version.
"""

from __future__ import annotations

import numpy as np


def compute_total_energy(
    u: np.ndarray,
    v: np.ndarray,
    c: float,
    dx: float,
    dy: float,
) -> float:
    """Broken discrete energy formula for the 2D wave field."""
    if u.shape != v.shape:
        raise ValueError(f"u and v must have the same shape, got {u.shape} vs {v.shape}")
    if c <= 0:
        raise ValueError(f"c must be positive, got {c}")
    if dx <= 0 or dy <= 0:
        raise ValueError(f"dx and dy must be positive, got dx={dx}, dy={dy}")

    kinetic = 0.5 * v[1:-1, 1:-1] ** 2
    ux = (u[2:, 1:-1] - u[:-2, 1:-1]) / (2.0 * dy)
    uy = (u[1:-1, 2:] - u[1:-1, :-2]) / (2.0 * dx)
    potential = 0.5 * c * (ux ** 2 + uy ** 2)
    return float(np.sum(kinetic + potential) * dx * dy)
