"""Week 04 baseline 2D wave solver.

This is the only implementation file students should start from for the
main Week 04 practices. The intended workflow matches Week 03:

1. inspect the broken examples first,
2. ask the AI to extend this solver for a specific Week 04 task,
3. review the AI output against the checklist in week04.md.

The file stays intentionally compact, but exposes a few utilities that are
useful for Week 04 extensions:

- grid generation,
- initial condition generation,
- discrete Laplacian,
- Dirichlet baseline time stepping,
- energy and boundary-flux diagnostics,
- simple config loading.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_config(path: str = "config.yaml") -> dict:
    """Parse a simple key: value YAML file without external dependencies."""
    data: dict[str, object] = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = [item.strip() for item in line.split(":", 1)]
        value = value.split("#", 1)[0].strip()
        if not value:
            continue
        try:
            data[key] = float(value) if ("." in value or "e" in value.lower()) else int(value)
        except ValueError:
            data[key] = value
    return data


def make_grid(nx: int, ny: int, length: float = 1.0):
    """Return X, Y, dx, dy for a uniform grid on [0, length]^2."""
    if nx < 3 or ny < 3:
        raise ValueError("grid must be at least 3x3")
    x = np.linspace(0.0, length, nx)
    y = np.linspace(0.0, length, ny)
    X, Y = np.meshgrid(x, y, indexing="ij")
    dx = float(x[1] - x[0])
    dy = float(y[1] - y[0])
    return X, Y, dx, dy


def make_initial_field(nx: int, ny: int, length: float = 1.0):
    """Return a separable sine mode and zero initial velocity."""
    X, Y, _, _ = make_grid(nx, ny, length)
    u = np.sin(np.pi * X) * np.sin(np.pi * Y)
    v = np.zeros_like(u)
    return u, v


def enforce_dirichlet(u: np.ndarray) -> None:
    """Apply homogeneous Dirichlet boundaries in-place."""
    u[0, :] = 0.0
    u[-1, :] = 0.0
    u[:, 0] = 0.0
    u[:, -1] = 0.0


def discrete_laplacian(u: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Second-order central-difference Laplacian with zero boundary rows."""
    lap = np.zeros_like(u)
    lap[1:-1, 1:-1] = (
        (u[2:, 1:-1] - 2.0 * u[1:-1, 1:-1] + u[:-2, 1:-1]) / dx**2
        + (u[1:-1, 2:] - 2.0 * u[1:-1, 1:-1] + u[1:-1, :-2]) / dy**2
    )
    return lap


def compute_energy(u: np.ndarray, v: np.ndarray, c: float, dx: float, dy: float) -> float:
    """Return discrete wave energy using centered spatial gradients."""
    kinetic = 0.5 * np.sum(v**2) * dx * dy

    dudx = np.zeros_like(u)
    dudy = np.zeros_like(u)
    dudx[1:-1, :] = (u[2:, :] - u[:-2, :]) / (2.0 * dx)
    dudy[:, 1:-1] = (u[:, 2:] - u[:, :-2]) / (2.0 * dy)

    potential = 0.5 * c**2 * np.sum(dudx**2 + dudy**2) * dx * dy
    return float(kinetic + potential)


def estimate_outward_flux(
    u: np.ndarray,
    v: np.ndarray,
    c: float,
    dx: float,
    dy: float,
    dt: float,
) -> float:
    """Estimate outward energy flux through all four boundaries over one step."""
    phi_left = -c**2 / dx * np.sum(v[0, :] * (u[1, :] - u[0, :])) * dy
    phi_right = c**2 / dx * np.sum(v[-1, :] * (u[-1, :] - u[-2, :])) * dy
    phi_bottom = -c**2 / dy * np.sum(v[:, 0] * (u[:, 1] - u[:, 0])) * dx
    phi_top = c**2 / dy * np.sum(v[:, -1] * (u[:, -1] - u[:, -2])) * dx
    return float((phi_left + phi_right + phi_bottom + phi_top) * dt)


def first_step(
    u_prev: np.ndarray,
    c: float,
    dt: float,
    dx: float,
    dy: float,
) -> np.ndarray:
    """Advance from t=0 to t=dt assuming zero initial velocity."""
    u_curr = u_prev.copy()
    lap = discrete_laplacian(u_prev, dx, dy)
    u_curr[1:-1, 1:-1] = u_prev[1:-1, 1:-1] + 0.5 * (c * dt) ** 2 * lap[1:-1, 1:-1]
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
    """Leapfrog update for the 2D wave equation with Dirichlet walls."""
    lap = discrete_laplacian(u_curr, dx, dy)
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
    """Simulate the homogeneous 2D wave equation with Dirichlet boundaries."""
    if x.shape != y.shape or x.shape != u0.shape:
        raise ValueError("x, y, and u0 must have the same shape")
    if dt <= 0.0:
        raise ValueError("dt must be positive")
    if t_end < 0.0:
        raise ValueError("t_end must be non-negative")

    dx = float(x[0, 1] - x[0, 0])
    dy = float(y[1, 0] - y[0, 0])
    if dx <= 0.0 or dy <= 0.0:
        raise ValueError("grid spacings must be positive")

    dt_max = 1.0 / (c * np.sqrt((1.0 / dx**2) + (1.0 / dy**2)))
    if dt > dt_max * (1.0 + 1e-12):
        raise ValueError(f"dt={dt:.4e} exceeds stability guard dt_max={dt_max:.4e}")

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