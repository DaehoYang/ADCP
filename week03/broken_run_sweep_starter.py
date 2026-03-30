"""Week 03 convergence sweep: sweep automation, slope regression, and CSV output.

AI-Driven Computational Physics — Graduate Course

This script implements the 4-point resolution sweep, log-log slope regression,
and CSV output for the Week 03 convergence study.

Module Map
----------
run_single_case(n, cfg)         — run the wave solver at one resolution, return record
run_sweep(cfg)                  — loop over cfg['resolutions'], collect records
fit_slope(dx_values, errors)    — log-log linear regression, return |slope|
save_results_csv(results, path) — write records to CSV

Run
---
    cd week03
    python broken_run_sweep_starter.py
    pytest test_convergence_starter.py -v

Expected outputs
----------------
    results/convergence_results.csv
    results/summary.json
"""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Import reference function from Week 02 (fallback to inline if unavailable)
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from week02.starter_reference_check import reference  # type: ignore
except ImportError:
    def reference(x: np.ndarray, y: np.ndarray, t: float, c: float = 1.0) -> np.ndarray:
        """Exact separable sine mode: u = sin(pi x) sin(pi y) cos(sqrt(2) pi c t)."""
        return (np.sin(np.pi * x) * np.sin(np.pi * y)
                * np.cos(np.sqrt(2) * np.pi * c * t))


# ---------------------------------------------------------------------------
# Config loader (no external YAML dependency)
# ---------------------------------------------------------------------------

def load_config(path: str = "sweep_config.yaml") -> dict:
    """Parse a simple key: value YAML file (supports list values)."""
    data: dict[str, object] = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = [x.strip() for x in line.split(":", 1)]
        if v.startswith("[") and v.endswith("]"):
            vals = [x.strip() for x in v[1:-1].split(",") if x.strip()]
            data[k] = [int(x) for x in vals]
            continue
        try:
            data[k] = float(v) if ("." in v or "e" in v.lower()) else int(v)
        except ValueError:
            data[k] = v
    return data


# ---------------------------------------------------------------------------
# Inline 2D wave solver (no Week 01 import required)
# ---------------------------------------------------------------------------

def _simulate_wave_2d(n: int, dx: float, dt: float, t_star: float, c: float) -> np.ndarray:
    """Leapfrog finite-difference solver for the 2D wave equation on [0,1]^2.

    Uses central differences in space (2nd-order) and leapfrog in time (2nd-order).
    Dirichlet BC: u = 0 on all boundaries.
    Initial condition: u(x,y,0) = reference(x,y,0), u_t(x,y,0) = 0.

    Returns the solution array u at physical time t_star.
    """
    # Build uniform grid (interior + boundary)
    x1d = np.linspace(0.0, 1.0, n + 1)
    x, y = np.meshgrid(x1d, x1d)

    r2 = (c * dt / dx) ** 2           # Courant number squared
    n_steps = round(t_star / dt)

    # Initial conditions
    u_prev = reference(x, y, 0.0, c).copy()
    # First step using Taylor expansion: u_1 ≈ u_0 + dt * u_t(0) + dt^2/2 * u_tt(0)
    # u_t(0) = 0 for this mode; u_tt(0) = c^2 * Laplacian(u_0)
    lap = np.zeros_like(u_prev)
    lap[1:-1, 1:-1] = (
        u_prev[2:, 1:-1] - 2 * u_prev[1:-1, 1:-1] + u_prev[:-2, 1:-1]
        + u_prev[1:-1, 2:] - 2 * u_prev[1:-1, 1:-1] + u_prev[1:-1, :-2]
    ) / dx**2
    u_curr = u_prev + 0.5 * (c * dt)**2 * lap
    u_curr[0, :] = u_curr[-1, :] = u_curr[:, 0] = u_curr[:, -1] = 0.0

    # Leapfrog time integration
    for _ in range(1, n_steps):
        lap[:] = 0.0
        lap[1:-1, 1:-1] = (
            u_curr[2:, 1:-1] - 2 * u_curr[1:-1, 1:-1] + u_curr[:-2, 1:-1]
            + u_curr[1:-1, 2:] - 2 * u_curr[1:-1, 1:-1] + u_curr[1:-1, :-2]
        ) / dx**2
        u_next = 2.0 * u_curr - u_prev + (c * dt)**2 * lap
        u_next[0, :] = u_next[-1, :] = u_next[:, 0] = u_next[:, -1] = 0.0
        u_prev, u_curr = u_curr, u_next

    return u_curr


def _compute_l2(u_num: np.ndarray, u_ref: np.ndarray, dx: float) -> float:
    """Grid-scaled L2 norm: sqrt(sum((u_num - u_ref)^2) * dx)."""
    return float(np.sqrt(np.sum((u_num - u_ref) ** 2) * dx))


# ---------------------------------------------------------------------------
# Implementation
# ---------------------------------------------------------------------------

def run_single_case(n: int, cfg: dict) -> dict:
    """Run the wave solver at a single resolution and return one result record.

    Args:
        n:   grid resolution (number of intervals per side)
        cfg: config dict from load_config()

    Returns:
        dict with keys: n, dx, dt, error, runtime
    """
    dx = cfg["length"] / n
    dt = cfg["courant"] * dx / cfg["c"]

    t0 = time.time()
    u_num = _simulate_wave_2d(n, dx, dt, cfg["t_star"], cfg["c"])
    runtime = time.time() - t0

    x1d = np.linspace(0.0, 1.0, n + 1)
    x, y = np.meshgrid(x1d, x1d)
    u_ref = reference(x, y, cfg["t_star"], cfg["c"])

    error = _compute_l2(u_num, u_ref, dx)
    return {"n": n, "dx": dx, "dt": dt, "error": error, "runtime": runtime}


def run_sweep(cfg: dict) -> list[dict]:
    """Loop over resolutions and collect one record per resolution.

    Args:
        cfg: config dict from load_config()

    Returns:
        list of dicts (one per resolution), each from run_single_case
    """
    return [run_single_case(n, cfg) for n in cfg["resolutions"]]


def fit_slope(dx_values: np.ndarray, err_values: np.ndarray) -> float:
    """Perform log-log linear regression on (dx, error) data.

    Args:
        dx_values:  1D array of grid spacings (positive, decreasing)
        err_values: 1D array of corresponding L2 errors

    Returns:
        slope (float, absolute value), which is the convergence order
    """
    log_dx  = np.log10(dx_values)
    log_err = np.log10(err_values)
    slope, _ = np.polyfit(log_err, log_dx, 1)
    return abs(slope)


def save_results_csv(results: list[dict], path: Path) -> None:
    """Write the list of result records to a CSV file.

    Args:
        results: list of dicts (output of run_sweep)
        path:    output file path (e.g. Path('results/convergence_results.csv'))
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    cfg = load_config("sweep_config.yaml")

    results = run_sweep(cfg)
    dx_values  = np.array([r["dx"]    for r in results], dtype=float)
    err_values = np.array([r["error"] for r in results], dtype=float)
    slope = fit_slope(dx_values, err_values)

    out_dir = Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)
    save_results_csv(results, out_dir / "convergence_results.csv")

    summary = {
        "status": "convergence-checked" if abs(slope - float(cfg.get("slope_target", 2.0)))
                   <= float(cfg.get("slope_tol", 0.2)) else "needs-fix",
        "measured_slope": round(slope, 4),
        "target_slope":   float(cfg.get("slope_target", 2.0)),
        "tolerance":      float(cfg.get("slope_tol", 0.2)),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
