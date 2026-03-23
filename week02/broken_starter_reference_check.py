"""
Week 02: Analytic Reference and First Error Measurement
========================================================
AI-Driven Computational Physics — Graduate Course

This is a complete implementation of the Week 02 reference-check workflow.
All five functions are implemented. Run the code to see if everything works.

    cd week02
    python broken_starter_reference_check.py
    pytest test_reference_check.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config(path: str = "config.yaml") -> dict:
    """Parse a simple key: value YAML file (no external dependency)."""
    data: dict[str, object] = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = [x.strip() for x in line.split(":", 1)]
        try:
            data[k] = float(v) if ("." in v or "e" in v.lower()) else int(v)
        except ValueError:
            data[k] = v
    return data


# ---------------------------------------------------------------------------
# Analytic reference solution
# ---------------------------------------------------------------------------

def reference(x: np.ndarray, y: np.ndarray, t: float, c: float = 1.0) -> np.ndarray:
    """Exact analytic solution for the 2D wave equation on [0,1]^2.

    PDE:  u_tt = c^2 * (u_xx + u_yy)    with Dirichlet BC u=0 on all walls.

    Separable eigenmode (m=n=1):
        u(x, y, t) = sin(pi*x) * sin(pi*y) * cos(omega*t)
        omega = pi * c

    Parameters
    ----------
    x, y : array-like, same shape
        Coordinate meshgrids from np.meshgrid on [0,1]^2.
    t : float
        Physical time.
    c : float
        Wave speed (default 1.0).

    Returns
    -------
    np.ndarray of the same shape as x.
    """
    omega = np.pi * c
    return np.sin(np.pi * x) * np.sin(np.pi * y) * np.cos(omega * t)


# ---------------------------------------------------------------------------
# L2 error metric
# ---------------------------------------------------------------------------

def compute_l2(
    u_num: np.ndarray,
    u_ref: np.ndarray,
    dx: float,
    dy: float,
) -> float:
    """Return the L2 norm of (u_num - u_ref).

    Accumulates pointwise squared errors and returns the square root of the total.

    Parameters
    ----------
    u_num : np.ndarray
        Numerical solution field.
    u_ref : np.ndarray
        Reference (exact) solution field, same shape as u_num.
    dx : float
        Grid spacing in x (must be > 0).
    dy : float
        Grid spacing in y (must be > 0).

    Returns
    -------
    float
        L2 norm of the error.
    """
    if u_num.shape != u_ref.shape:
        raise ValueError(
            f"Shape mismatch: u_num {u_num.shape} vs u_ref {u_ref.shape}"
        )
    if dx <= 0 or dy <= 0:
        raise ValueError(f"Grid spacings must be positive: dx={dx}, dy={dy}")

    diff = u_num - u_ref
    return float(np.sqrt(np.sum(diff ** 2)))


# ---------------------------------------------------------------------------
# Composite Trapezoidal integration kernel
# ---------------------------------------------------------------------------

def trapezoidal(f, a: float, b: float, n: int) -> float:
    """Composite Trapezoidal Rule for integral_a^b f(x) dx with n sub-intervals.

    Formula:
        h = (b - a) / n
        I ~ h * (f(x0)/2 + f(x1) + ... + f(x_{n-1}) + f(xn)/2)

    Parameters
    ----------
    f : callable
        Integrand function; must accept a 1-D numpy array and return array.
    a, b : float
        Integration limits.
    n : int
        Number of sub-intervals (number of points = n+1).

    Returns
    -------
    float
        Numerical estimate of the integral.
    """
    x = np.linspace(a, b, n + 1)
    y = f(x)
    h = (b - a) / n
    weights = np.ones_like(y)
    weights[0] = 0.5
    weights[-1] = 0.5
    return float(h * np.sum(weights * y))


# ---------------------------------------------------------------------------
# Analytic-limit integration gate
# ---------------------------------------------------------------------------

def analytic_limit_test() -> tuple[bool, float]:
    """Test the integration kernel against the known exact answer.

    Target integral:  integral_0^2 x dx = 2.0  (exact)

    Returns
    -------
    (passed, value)
    """
    value = trapezoidal(lambda x: x, 0.0, 2.0, 1000)
    passed = bool(np.isclose(value, 2.0, rtol=1e-4))
    return passed, float(value)


# ---------------------------------------------------------------------------
# Synchronized single-case L2 measurement
# ---------------------------------------------------------------------------

def single_case_l2_measurement(cfg: dict) -> float:
    """Compute one L2 error at the fixed physical time t_star from config.

    Parameters
    ----------
    cfg : dict with keys nx, ny, length_x, length_y, c, t_star, courant

    Returns
    -------
    float
        L2 error at t_star.
    """
    nx      = int(cfg["nx"])
    ny      = int(cfg["ny"])
    lx      = float(cfg.get("length_x", 1.0))
    ly      = float(cfg.get("length_y", 1.0))
    c       = float(cfg["c"])
    t_star  = float(cfg["t_star"])

    dx = lx / nx
    dy = ly / ny

    xs = np.linspace(0.0, lx, nx)
    ys = np.linspace(0.0, ly, ny)
    x, y = np.meshgrid(xs, ys)

    u_ref = reference(x, y, t_star, c)
    u_num = fake_numerical_field(x, y, t_star, c)

    return compute_l2(u_num, u_ref, dx, dy)


# ---------------------------------------------------------------------------
# Helper: fake numerical field
# ---------------------------------------------------------------------------

def fake_numerical_field(
    x: np.ndarray,
    y: np.ndarray,
    t: float,
    c: float,
) -> np.ndarray:
    """Emulate a noisy numerical solver output for Week 02 exercises."""
    rng = np.random.default_rng(42)
    noise = 1e-3 * rng.standard_normal(size=x.shape)
    return (
        np.sin(np.pi * x) * np.sin(np.pi * y) * np.cos(np.sqrt(2) * np.pi * c * t)
        + noise
    )


# ---------------------------------------------------------------------------
# Extension: Wave energy diagnostic
# ---------------------------------------------------------------------------

def wave_energy(
    u_now: np.ndarray,
    u_prev: np.ndarray,
    dt: float,
    c: float,
    dx: float,
    dy: float,
) -> float:
    """Discrete wave energy: kinetic + potential, area-scaled."""
    u_t = (u_now - u_prev) / dt
    dudx = np.gradient(u_now, dx, axis=1)
    dudy = np.gradient(u_now, dy, axis=0)
    kinetic   = 0.5 * np.sum(u_t**2)                   * dx * dy
    potential = 0.5 * c**2 * np.sum(dudx**2 + dudy**2) * dx * dy
    return float(kinetic + potential)


# ---------------------------------------------------------------------------
# Extension: PDE residual check
# ---------------------------------------------------------------------------

def check_pde_residual(
    x: np.ndarray,
    y: np.ndarray,
    t: float,
    c: float = 1.0,
    dx: float | None = None,
) -> float:
    """Numerically verify that reference(x, y, t) satisfies u_tt = c^2*nabla^2 u."""
    if dx is None:
        dx_vals = np.diff(x[0]) if x.ndim == 2 else np.diff(x)
        dx = float(dx_vals[0])

    dt = dx

    u_prev = reference(x, y, t - dt, c)
    u_curr = reference(x, y, t,      c)
    u_next = reference(x, y, t + dt, c)

    u_tt = (u_next - 2 * u_curr + u_prev) / dt**2

    u_xx = (np.roll(u_curr, -1, axis=1) - 2 * u_curr + np.roll(u_curr, 1, axis=1)) / dx**2
    u_yy = (np.roll(u_curr, -1, axis=0) - 2 * u_curr + np.roll(u_curr, 1, axis=0)) / dx**2

    residual = np.abs(u_tt - c**2 * (u_xx + u_yy))
    return float(np.max(residual[1:-1, 1:-1]))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the analytic-limit gate and single-case L2 measurement."""
    cfg = load_config("config.yaml")

    passed, value = analytic_limit_test()
    l2_value = single_case_l2_measurement(cfg)

    out = {
        "status": "reference-checked" if passed else "needs-fix",
        "analytic_limit_passed": passed,
        "analytic_limit_value": value,
        "single_case_l2": l2_value,
    }

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "week02_broken_results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
