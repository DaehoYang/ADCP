"""
Week 02 Starter: Analytic Reference and First Error Measurement
===============================================================
AI-Driven Computational Physics — Graduate Course

Goal
----
Define an exact analytic reference solution for the 2D wave equation,
implement an L2 error metric with proper grid-area scaling, and record
one synchronized single-case measurement.

Scope Boundary
--------------
This week (02):   reference definition + single-case L2 measurement.
Next week (02.5): resolution sweep, log-log regression, slope asserts.

Module Map
----------
Module 1 — Error budget:        E(h) = C1*h^p + C2*eps_mach/h
Module 2 — Integration kernel:  composite trapezoidal rule
Module 3 — L2 norm contract:    grid-area-scaled Riemann sum + reference function
Module 4 — Variable isolation:  fixed Courant number, fixed t_star
Module 5 — Pass criteria:       analytic-limit gate → status label

Functions to implement (5 TODOs)
---------------------------------
1. reference(x, y, t, c)            — analytic separable sine mode (Module 3)
2. compute_l2(u_num, u_ref, dx, dy) — L2 with dx*dy Riemann weight  (Module 3)
3. trapezoidal(f, a, b, n)          — composite trapezoidal rule      (Module 2)
4. analytic_limit_test()            — integration gate: ∫0^2 x dx = 2.0 (Module 5)
5. single_case_l2_measurement(cfg)  — synchronized L2 at fixed t_star  (Module 4)

Extension functions (ungraded)
-------------------------------
- wave_energy(u_now, u_prev, dt, c, dx, dy) — discrete wave energy diagnostic
- check_pde_residual(x, y, t, c, dx)        — PDE residual check for reference

Run
---
    cd week02
    python starter_reference_check.py
    pytest test_reference_check.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from solver_2d import simulate_dirichlet_wave


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config(path: str = "config.yaml") -> dict:
    """Parse a simple key: value YAML file (no external dependency).

    Reads lines of the form 'key: value', ignoring comments and blank lines.
    Converts numeric strings to int or float automatically.
    """
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
# TODO 1 — Analytic reference solution  (Module 3)
# ---------------------------------------------------------------------------

def reference(x: np.ndarray, y: np.ndarray, t: float, c: float = 1.0) -> np.ndarray:
    """Exact analytic solution for the 2D wave equation on [0,1]^2.

    PDE:  u_tt = c^2 * (u_xx + u_yy)    with Dirichlet BC u=0 on all walls.

    Derivation (separation of variables):
        Try u(x,y,t) = X(x) Y(y) T(t).
        Dirichlet BC forces X(x) = sin(m*pi*x), Y(y) = sin(n*pi*y).
        For m=n=1 with L_x=L_y=1 the dispersion relation gives
            omega = c * pi * sqrt(k_x^2 + k_y^2) = sqrt(2)*pi*c
        so T(t) = cos(sqrt(2)*pi*c*t)  (starting from rest: dT/dt|t=0 = 0).

    Resulting separable eigenmode (m=n=1):
        u(x, y, t) = sin(pi*x) * sin(pi*y) * cos(sqrt(2)*pi*c*t)

    Verification by direct PDE substitution:
        u_tt = -2*pi^2*c^2 * sin(pi*x)*sin(pi*y)*cos(sqrt(2)*pi*c*t)
        c^2*(u_xx + u_yy) = -2*pi^2*c^2 * sin(pi*x)*sin(pi*y)*cos(sqrt(2)*pi*c*t)
        => u_tt == c^2*laplacian(u)  ✓
        Dispersion: omega^2 = c^2*(kx^2 + ky^2) = 2*pi^2*c^2  ✓
        BC: sin(0) = sin(pi) = 0  => u=0 on all four walls  ✓

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
    return np.sin(np.pi * x) * np.sin(np.pi * y) * np.cos(np.sqrt(2.0) * np.pi * c * t)


# ---------------------------------------------------------------------------
# TODO 2 — L2 error metric (grid-area scaled)  (Module 3)
# ---------------------------------------------------------------------------

def compute_l2(
    u_num: np.ndarray,
    u_ref: np.ndarray,
    dx: float,
    dy: float,
) -> float:
    """Return the L2 norm of (u_num - u_ref) with Riemann-sum area weighting.

    Continuous definition:
        ||e||_2 = sqrt( integral integral e(x,y)^2 dx dy )

    Discrete approximation (Riemann sum):
        L2 = sqrt( sum_ij (u_num_ij - u_ref_ij)^2 * dx * dy )

    Why dx*dy is required (Module 3 — Riemann-sum bridge):
        Without dx*dy, a 100x100 grid reports ~4x larger "error" than a 50x50
        grid for IDENTICAL physics — a completely false signal.
        With dx*dy the sum approximates the physical continuous integral,
        making the scalar grid-resolution-independent.

    Guard requirements (raise ValueError):
    - Shapes of u_num and u_ref must match.
    - dx and dy must both be strictly positive.

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
        Grid-area-scaled L2 norm of the error.
    """
    if u_num.shape != u_ref.shape:
        raise ValueError(f"shape mismatch: {u_num.shape} vs {u_ref.shape}")
    if dx <= 0.0 or dy <= 0.0:
        raise ValueError("dx and dy must be positive")

    err = u_num - u_ref
    return float(np.sqrt(np.sum(err**2) * dx * dy))


# ---------------------------------------------------------------------------
# TODO 3 — Composite Trapezoidal integration kernel  (Module 2)
# ---------------------------------------------------------------------------

def trapezoidal(f, a: float, b: float, n: int) -> float:
    """Composite Trapezoidal Rule for ∫_a^b f(x) dx with n sub-intervals.

    Formula:
        h = (b - a) / n
        I ≈ h * (f(x0)/2 + f(x1) + ... + f(x_{n-1}) + f(xn)/2)

    Why endpoints are halved (Module 2 foundational note):
        Each boundary trapezoid spans only HALF an interval, so its weight
        is 0.5 (not 1.0 like interior points). This is math, not heuristic.

    Error order: O(h^2) — doubling n quadruples accuracy.

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
    if n <= 0:
        raise ValueError("n must be positive")

    x = np.linspace(a, b, n + 1)
    fx = np.asarray(f(x), dtype=float)
    h = (b - a) / n
    return float(h * (0.5 * fx[0] + np.sum(fx[1:-1]) + 0.5 * fx[-1]))


# ---------------------------------------------------------------------------
# TODO 4 — Analytic-limit integration gate  (Module 5)
# ---------------------------------------------------------------------------

def analytic_limit_test() -> tuple[bool, float]:
    """Test the integration kernel against a known exact answer.

    Target integral:  ∫_0^2 x dx = [x^2/2]_0^2 = 2.0  (exact)

    This is the Module 5 gate: if the kernel fails here, no
    convergence sweep can recover the claim.

    Implementation:
        Call trapezoidal(lambda x: x, 0.0, 2.0, 1000) and compare
        with np.isclose(value, 2.0, rtol=1e-4).

    Returns
    -------
    (passed, value) where:
        passed : bool   — True if |value - 2.0| / 2.0 < 1e-4
        value  : float  — the numerical result of the integration
    """
    value = trapezoidal(lambda x: x, 0.0, 2.0, 1000)
    passed = bool(np.isclose(value, 2.0, rtol=1e-4))
    return passed, float(value)


# ---------------------------------------------------------------------------
# TODO 5 — Synchronized single-case L2 measurement  (Module 4)
# ---------------------------------------------------------------------------

def single_case_l2_measurement(cfg: dict) -> float:
    """Compute one L2 error at the fixed physical time t_star from config.

    This is the Module 4 measurement: one scalar confirming the reference
    is callable and the L2 contract is correct.

    It does NOT prove convergence — that requires the Week 02.5 sweep.

    Module 4 variable-isolation rules (must not be overridden here):
    - Hold physical time fixed: use t_star from cfg, same across every run.
    - Fix Courant number: dt = courant * dx / c (scale dt with grid).

    Parameters
    ----------
    cfg : dict with keys nx, ny, length_x, length_y, c, t_star, courant
          (loaded from config.yaml by load_config())

    Steps:
    1. Build x, y meshgrids on [0, length_x] x [0, length_y].
    2. Evaluate u_ref = reference(x, y, t_star, c).
    3. Simulate u_num using fake_numerical_field (placeholder for solver).
    4. Return compute_l2(u_num, u_ref, dx, dy).

    Returns
    -------
    float
        L2 error at t_star.
    """
    nx = int(cfg["nx"])
    ny = int(cfg["ny"])
    lx = float(cfg.get("length_x", 1.0))
    ly = float(cfg.get("length_y", 1.0))
    c = float(cfg.get("c", 1.0))
    t_star = float(cfg["t_star"])
    courant = float(cfg.get("courant", 0.5))

    x1 = np.linspace(0.0, lx, nx)
    y1 = np.linspace(0.0, ly, ny)
    x, y = np.meshgrid(x1, y1)
    dx = float(x1[1] - x1[0])
    dy = float(y1[1] - y1[0])
    dt = courant * min(dx, dy) / c

    u0 = reference(x, y, t=0.0, c=c)
    u_ref = reference(x, y, t=t_star, c=c)
    u_num = fake_numerical_field(x, y, t_star, c, dt=dt, u0=u0)
    return compute_l2(u_num, u_ref, dx, dy)


# ---------------------------------------------------------------------------
# Helper: fake numerical field
# (replaces the Week 01 solver until it is available)
# ---------------------------------------------------------------------------

def fake_numerical_field(
    x: np.ndarray,
    y: np.ndarray,
    t: float,
    c: float,
    dt: float | None = None,
    u0: np.ndarray | None = None,
) -> np.ndarray:
    """Return a numerical field from the local Week 02 solver copy.

    The function name is kept for backward compatibility with the existing
    Week 02 test and sweep scaffolding.
    """
    if dt is None:
        dx = float(x[0, 1] - x[0, 0])
        dy = float(y[1, 0] - y[0, 0])
        dt = 0.5 * min(dx, dy) / c
    if u0 is None:
        u0 = reference(x, y, t=0.0, c=c)
    return simulate_dirichlet_wave(x, y, t_end=t, c=c, dt=dt, u0=u0)


# ---------------------------------------------------------------------------
# Extension: Wave energy diagnostic  (Module 4 — Case Study 3)
# ---------------------------------------------------------------------------

def wave_energy(
    u_now: np.ndarray,
    u_prev: np.ndarray,
    dt: float,
    c: float,
    dx: float,
    dy: float,
) -> float:
    """Discrete wave energy: kinetic + potential, area-scaled.

    Definition (continuous):
        E(t) = (1/2) * integral integral [ u_t^2 + c^2 |grad u|^2 ] dx dy

    Discretization:
        - u_t ≈ (u_now - u_prev) / dt     (O(dt) backward difference)
        - grad u via numpy.gradient (O(dx^2) central difference interior)
        - Area scaling via dx*dy (same Riemann-sum logic as compute_l2)

    This is a DIAGNOSTIC quantity — not a pass/fail gate in Week 02.
    Large monotonic drift signals unphysical dissipation or instability.

    Parameters
    ----------
    u_now, u_prev : np.ndarray
        Field at current and previous time levels, same shape.
    dt : float
        Time step.
    c : float
        Wave speed.
    dx, dy : float
        Grid spacings.

    Returns
    -------
    float
        Total discrete wave energy at the current time level.
    """
    u_t = (u_now - u_prev) / dt                        # O(dt) time derivative
    dudx = np.gradient(u_now, dx, axis=1)
    dudy = np.gradient(u_now, dy, axis=0)
    kinetic   = 0.5 * np.sum(u_t**2)                   * dx * dy
    potential = 0.5 * c**2 * np.sum(dudx**2 + dudy**2) * dx * dy
    return float(kinetic + potential)


# ---------------------------------------------------------------------------
# Extension: PDE residual check  (Module 3 — verification recipe step 1)
# ---------------------------------------------------------------------------

def check_pde_residual(
    x: np.ndarray,
    y: np.ndarray,
    t: float,
    c: float = 1.0,
    dx: float | None = None,
) -> float:
    """Numerically verify that reference(x, y, t) satisfies u_tt = c^2*∇²u.

    Computes the pointwise residual |u_tt - c^2*(u_xx + u_yy)| at all
    interior points using second-order finite differences, then returns
    the maximum absolute residual.

    A well-implemented reference should return a residual close to machine
    precision times the function magnitude (~1e-10 or smaller for dx~1e-3).

    This is an EXTENSION exercise — not required for the pass criteria.

    Parameters
    ----------
    x, y : np.ndarray
        Coordinate meshgrids (2-D arrays, same shape).
    t : float
        Physical time at which to evaluate the residual.
    c : float
        Wave speed.
    dx : float or None
        Grid spacing. If None, inferred from x spacing (uniform grid assumed).

    Returns
    -------
    float
        Maximum absolute PDE residual over interior points.
    """
    if dx is None:
        dx_vals = np.diff(x[0]) if x.ndim == 2 else np.diff(x)
        dx = float(dx_vals[0])

    dt = dx  # use same step for time finite difference

    u_prev = reference(x, y, t - dt, c)
    u_curr = reference(x, y, t,      c)
    u_next = reference(x, y, t + dt, c)

    # Second-order time derivative
    u_tt = (u_next - 2 * u_curr + u_prev) / dt**2

    # Second-order Laplacian (np.roll gives periodic boundary wrap — OK for interior check)
    u_xx = (np.roll(u_curr, -1, axis=1) - 2 * u_curr + np.roll(u_curr, 1, axis=1)) / dx**2
    u_yy = (np.roll(u_curr, -1, axis=0) - 2 * u_curr + np.roll(u_curr, 1, axis=0)) / dx**2

    residual = np.abs(u_tt - c**2 * (u_xx + u_yy))
    return float(np.max(residual[1:-1, 1:-1]))


# ---------------------------------------------------------------------------
# Main — runs Module 5 gate and saves outputs/week02_results.json
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the analytic-limit gate and single-case L2 measurement.

    Output JSON schema:
        {
          "status":                "reference-checked" | "needs-fix",
          "analytic_limit_passed": bool,
          "analytic_limit_value":  float,
          "single_case_l2":        float
        }

    Status rule (Module 5 gate):
        analytic_limit_passed == True  →  "reference-checked"
        analytic_limit_passed == False →  "needs-fix"
        (regardless of how small single_case_l2 looks)
    """
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
    (out_dir / "week02_results.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
