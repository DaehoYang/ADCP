"""Week 02 local copy of the Week 01 2D wave solver.

This copy lets Week 02 stay self-contained while assuming students already
implemented the baseline solver in the previous week.
"""

from __future__ import annotations

import numpy as np


def enforce_dirichlet(u: np.ndarray) -> None:
    """Apply homogeneous Dirichlet boundary conditions in-place."""
    u[0, :] = 0.0
    u[-1, :] = 0.0
    u[:, 0] = 0.0
    u[:, -1] = 0.0


def laplacian_2d(u: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Return the 2D Laplacian using second-order central differences."""
    lap = np.zeros_like(u)
    lap[1:-1, 1:-1] = (
        (u[2:, 1:-1] - 2.0 * u[1:-1, 1:-1] + u[:-2, 1:-1]) / dx**2
        + (u[1:-1, 2:] - 2.0 * u[1:-1, 1:-1] + u[1:-1, :-2]) / dy**2
    )
    return lap


def first_step(
    u_prev: np.ndarray,
    c: float,
    dt: float,
    dx: float,
    dy: float,
) -> np.ndarray:
    """Advance from t=0 to t=dt assuming zero initial velocity."""
    u_curr = u_prev.copy()
    lap = laplacian_2d(u_prev, dx, dy)
    u_curr[1:-1, 1:-1] = (
        u_prev[1:-1, 1:-1] + 0.5 * (c * dt) ** 2 * lap[1:-1, 1:-1]
    )
    enforce_dirichlet(u_curr)
    return u_curr


def update_step(
    u_prev: np.ndarray,
    u_curr: np.ndarray,
    c: float,
    dt: float,
    dx: float,
    dy: float,
) -> np.ndarray:
    """Leapfrog update for the 2D wave equation."""
    lap = laplacian_2d(u_curr, dx, dy)
    u_next = np.zeros_like(u_curr)
    u_next[1:-1, 1:-1] = (
        2.0 * u_curr[1:-1, 1:-1]
        - u_prev[1:-1, 1:-1]
        + (c * dt) ** 2 * lap[1:-1, 1:-1]
    )
    enforce_dirichlet(u_next)
    return u_next


def simulate_dirichlet_wave(
    x: np.ndarray,
    y: np.ndarray,
    t_end: float,
    c: float,
    dt: float,
    u0: np.ndarray,
) -> np.ndarray:
    """Simulate the homogeneous 2D wave equation up to t_end.

    Parameters
    ----------
    x, y : np.ndarray
        Coordinate meshgrids with identical shape.
    t_end : float
        Final physical time.
    c : float
        Wave speed.
    dt : float
        Time step.
    u0 : np.ndarray
        Initial displacement at t=0. Zero initial velocity is assumed.
    """
    if x.shape != y.shape or x.shape != u0.shape:
        raise ValueError("x, y, and u0 must have the same shape")
    if dt <= 0.0:
        raise ValueError("dt must be positive")
    if t_end < 0.0:
        raise ValueError("t_end must be non-negative")

    if x.shape[0] < 3 or x.shape[1] < 3:
        raise ValueError("grid must be at least 3x3")

    dx = float(x[0, 1] - x[0, 0])
    dy = float(y[1, 0] - y[0, 0])
    if dx <= 0.0 or dy <= 0.0:
        raise ValueError("grid spacings must be positive")

    dt_max = 1.0 / (c * np.sqrt((1.0 / dx**2) + (1.0 / dy**2)))
    if dt > dt_max * (1.0 + 1e-12):
        raise ValueError(
            f"dt={dt:.4e} exceeds stability guard dt_max={dt_max:.4e}"
        )

    u_prev = np.array(u0, dtype=float, copy=True)
    enforce_dirichlet(u_prev)
    if t_end == 0.0:
        return u_prev

    u_curr = first_step(u_prev, c, dt, dx, dy)
    t_curr = dt
    if t_curr >= t_end:
        return u_curr

    while t_curr + dt <= t_end + 1e-15:
        u_next = update_step(u_prev, u_curr, c, dt, dx, dy)
        u_prev, u_curr = u_curr, u_next
        t_curr += dt

    return u_curr
