"""Week 01 starter: baseline-ready 2D wave solver.

Student tasks are marked with TODO.
Complete TODO blocks in order (M1 → M2 → M3 → M4), then run end-to-end.

Module map:
  M1  preflight()             – boolean gate before any physics
  M2  laplacian_2d()          – discrete ∇² on interior points
      first_step()            – leapfrog initialisation step
  M3  update_step()           – main time-advance loop body
  M4  relative_energy_drift() – scale-invariant conservation metric
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import yaml


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config(path: str = "config.yaml") -> dict:
    """Load simulation parameters from a YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# M1: Preflight (Boolean Gate)
# ---------------------------------------------------------------------------

def preflight(cfg: dict) -> None:
    """Validate configuration before any solver state is created.

    If any assertion fails, no physics results are allowed.
    The exact CFL bound is derived in Week 04; this guard uses a basic safety
    check only.

    TODO(M1): complete the assertions below.
    """
    # TODO: assert cfg["nx"] > 2 and cfg["ny"] > 2
    # TODO: assert cfg["bc"] in {"dirichlet", "neumann", "periodic"}
    # TODO: assert cfg["dt"] > 0 and cfg["dt"] < cfg.get("dx", 1.0)
    raise NotImplementedError("TODO: preflight")


# ---------------------------------------------------------------------------
# Boundary helpers
# ---------------------------------------------------------------------------

def enforce_dirichlet(u: np.ndarray) -> None:
    u[0, :] = 0.0
    u[-1, :] = 0.0
    u[:, 0] = 0.0
    u[:, -1] = 0.0


def gaussian_2d(x: np.ndarray, y: np.ndarray,
                x0: float, y0: float, sigma: float) -> np.ndarray:
    return np.exp(-(((x - x0) ** 2 + (y - y0) ** 2) / (2.0 * sigma ** 2)))


# ---------------------------------------------------------------------------
# M2: Discrete Laplacian and First Step
# ---------------------------------------------------------------------------

def laplacian_2d(u: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Return ∇²u for interior points; boundary rows/cols remain 0.

    Derivation (reviewed in slides):
        u_xx ≈ (u[i+1,j] - 2u[i,j] + u[i-1,j]) / dx²  (Taylor, 2nd-order)
        u_yy ≈ (u[i,j+1] - 2u[i,j] + u[i,j-1]) / dy²
        ∇²u  = u_xx + u_yy   (Cartesian definition; no cross term)

    Sanity checks (derivable from the definition above):
        constant field → ∇²u == 0
        linear field   → ∇²u == 0

    TODO(M2): fill lap[1:-1, 1:-1] using vectorised slicing.
    """
    lap = np.zeros_like(u)
    # TODO: lap[1:-1, 1:-1] = ...
    raise NotImplementedError("TODO: laplacian_2d")


def first_step(u_prev: np.ndarray, c: float,
               dt: float, dx: float, dy: float) -> np.ndarray:
    """Compute u at t=dt from u at t=0 (zero initial velocity assumed).

    Leapfrog initialisation (half-step):
        u_curr[i,j] = u_prev[i,j] + 0.5*(c*dt)² * ∇²u_prev[i,j]

    Interior-only update leaves Dirichlet boundaries intact.

    TODO(M2): implement using laplacian_2d.
    """
    u_curr = u_prev.copy()
    # TODO: fill interior using laplacian_2d(u_prev, dx, dy)
    enforce_dirichlet(u_curr)
    raise NotImplementedError("TODO: first_step")


# ---------------------------------------------------------------------------
# M3: Time-Advance Step
# ---------------------------------------------------------------------------

def update_step(u_prev: np.ndarray, u_curr: np.ndarray,
                c: float, dt: float, dx: float, dy: float) -> np.ndarray:
    """Leapfrog update: u_next from u_curr and u_prev.

    u_next[i,j] = 2*u_curr[i,j] - u_prev[i,j] + (c*dt)² * ∇²u_curr[i,j]

    Only interior points [1:-1, 1:-1] are updated.
    Dirichlet boundary is re-enforced after the update.

    TODO(M3): implement the leapfrog formula.
    """
    u_next = np.empty_like(u_curr)
    # TODO: fill u_next[1:-1, 1:-1]
    enforce_dirichlet(u_next)
    raise NotImplementedError("TODO: update_step")


# ---------------------------------------------------------------------------
# M4: Energy Conservation Metric
# ---------------------------------------------------------------------------

def relative_energy_drift(u0: np.ndarray, u1: np.ndarray,
                           eps: float = 1e-12) -> float:
    """Compute |E1 - E0| / (|E0| + eps) using E = Σ u².

    Using the sum of squares as a proxy energy is sufficient for Week 01.
    Full kinetic + potential energy definition is introduced in Week 05.

    The epsilon guard prevents division by zero when E0 ≈ 0.

    TODO(M4): implement this function.
    """
    # TODO: implement
    raise NotImplementedError("TODO: relative_energy_drift")


# ---------------------------------------------------------------------------
# Week 02 interface stubs (do not modify)
# ---------------------------------------------------------------------------

def reference(x: np.ndarray, y: np.ndarray, t: float) -> np.ndarray:
    """Placeholder analytic reference; filled in Week 02."""
    return np.zeros_like(x) + 0.0 * y + 0.0 * t


def compute_l2(u_num: np.ndarray, u_ref: np.ndarray,
               dx: float, dy: float) -> float:
    """L2 error norm; full usage in Week 02."""
    if u_num.shape != u_ref.shape:
        raise ValueError(f"Shape mismatch: {u_num.shape} vs {u_ref.shape}")
    if dx <= 0.0 or dy <= 0.0:
        raise ValueError("dx and dy must be positive")
    return float(np.sqrt(np.sum((u_num - u_ref) ** 2) * dx * dy))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    cfg = load_config("config.yaml")

    nx            = int(cfg.get("nx", 80))
    ny            = int(cfg.get("ny", 80))
    length_x      = float(cfg.get("length_x", 1.0))
    length_y      = float(cfg.get("length_y", 1.0))
    c             = float(cfg.get("c", 1.0))
    t_end         = float(cfg.get("t_end", 0.2))
    safety_factor = float(cfg.get("safety_factor", 0.5))
    sigma         = float(cfg.get("sigma", 0.08))
    energy_eps    = float(cfg.get("energy_eps", 1e-12))
    bc            = str(cfg.get("bc", "dirichlet"))

    x  = np.linspace(0.0, length_x, nx)
    y  = np.linspace(0.0, length_y, ny)
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    dt_max = 1.0 / (c * np.sqrt((1.0 / dx ** 2) + (1.0 / dy ** 2)))
    dt     = safety_factor * dt_max
    nt     = int(np.ceil(t_end / dt)) + 1

    # M1: preflight gate
    preflight_cfg = {"nx": nx, "ny": ny, "bc": bc, "dt": dt, "dx": dx}
    preflight(preflight_cfg)

    xx, yy = np.meshgrid(x, y, indexing="ij")
    u_prev = gaussian_2d(xx, yy, x0=0.5 * length_x, y0=0.5 * length_y,
                         sigma=sigma)
    enforce_dirichlet(u_prev)

    # Structural guards (always present)
    assert u_prev.ndim == 2
    assert u_prev.shape == (nx, ny), f"Expected {(nx, ny)}, got {u_prev.shape}"
    assert np.isclose(dt, safety_factor * dt_max), "Inconsistent dt"

    # M2: first step
    u_curr = first_step(u_prev, c, dt, dx, dy)

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "u_t0.npy", u_prev)

    # M3: time loop
    mid_step = max(1, nt // 2)
    for n in range(1, nt - 1):
        u_next = update_step(u_prev, u_curr, c, dt, dx, dy)
        if n == mid_step:
            np.save(out_dir / "u_tmid.npy", u_next)
        u_prev, u_curr = u_curr, u_next

    np.save(out_dir / "u_tend.npy", u_curr)

    # M4: energy drift
    drift = relative_energy_drift(
        np.load(out_dir / "u_t0.npy"), u_curr, eps=energy_eps
    )

    # Week 02 interface check (do not modify)
    ref0     = reference(xx, yy, 0.0)
    l2_stub  = compute_l2(u_curr, ref0, dx, dy)

    run_log = {
        "label":                       "baseline-ready",
        "nx": nx, "ny": ny,
        "dx": dx, "dy": dy, "dt": dt,
        "t_end": t_end,
        "bc":                          bc,
        "c":                           c,
        "safety_factor":               safety_factor,
        "energy_eps":                  energy_eps,
        "relative_energy_drift":       drift,
        "reference_interface_callable": True,
        "compute_l2_interface_callable": True,
        "compute_l2_stub_value":       l2_stub,
    }
    (out_dir / "run_log.json").write_text(
        json.dumps(run_log, indent=2), encoding="utf-8"
    )
    print(json.dumps(run_log, indent=2))


if __name__ == "__main__":
    main()
