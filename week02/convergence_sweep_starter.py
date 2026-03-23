"""
Week 02.5 Preview: Convergence Sweep Starter
=============================================
AI-Driven Computational Physics — Graduate Course

Scope
-----
This file is a PREVIEW for Week 02.5.
It will NOT run successfully until Week 02's 5 TODOs are completed first.

Once starter_reference_check.py is fully implemented, this script will:
1. Run L2 error measurements at 4 increasing grid resolutions.
2. Fit a log-log regression to measure the observed convergence slope.
3. Assert that the slope is close to the theoretical value of 2.0.
4. Save results to outputs/week02_5_convergence.json.

Variable-Isolation Rules (from Week 02, Module 4)
---------------------------------------------------
- Hold t_star FIXED across all resolution points (loaded from config.yaml).
- Scale dt = courant * dx / c so the Courant number stays constant.
- Both rules must be active here — do NOT override them.

Run (Week 02.5)
---------------
    cd week02
    python convergence_sweep_starter.py
    pytest test_convergence_sweep.py -v   # (Week 02.5 test file, not yet created)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from starter_reference_check import (
    compute_l2,
    fake_numerical_field,
    load_config,
    reference,
)


# ---------------------------------------------------------------------------
# Sweep parameters
# ---------------------------------------------------------------------------

# Four resolution points for the convergence sweep.
# Choose a geometric sequence so that log-log slope is easy to read:
#   N = 25, 50, 100, 200  →  dx = 0.04, 0.02, 0.01, 0.005
SWEEP_N_VALUES = [25, 50, 100, 200]


# ---------------------------------------------------------------------------
# Core sweep function (TODO — complete in Week 02.5)
# ---------------------------------------------------------------------------

def run_convergence_sweep(cfg: dict) -> list[dict]:
    """Run the L2 measurement at each resolution in SWEEP_N_VALUES.

    Variable-isolation rules:
    - t_star is fixed (from cfg, not modified here).
    - dt = courant * dx / c so that the Courant number stays constant.

    Parameters
    ----------
    cfg : dict
        Loaded from config.yaml by load_config().

    Returns
    -------
    list of dicts, one per resolution point:
        [{"N": int, "dx": float, "l2": float}, ...]
    """
    c       = float(cfg["c"])
    t_star  = float(cfg["t_star"])
    courant = float(cfg.get("courant", 0.5))
    lx      = float(cfg.get("length_x", 1.0))
    ly      = float(cfg.get("length_y", 1.0))

    results = []
    for N in SWEEP_N_VALUES:
        dx = lx / N
        dy = ly / N
        dt = courant * dx / c          # Module 4: fixed Courant number

        # Build grid
        x1 = np.linspace(0.0, lx, N + 1)
        y1 = np.linspace(0.0, ly, N + 1)
        x, y = np.meshgrid(x1, y1)

        # Reference and numerical field at t_star
        u_ref = reference(x, y, t_star, c)
        u0 = reference(x, y, 0.0, c)
        u_num = fake_numerical_field(x, y, t_star, c, dt=dt, u0=u0)

        l2 = compute_l2(u_num, u_ref, dx=dx, dy=dy)
        results.append({"N": N, "dx": dx, "l2": l2})

    return results


# ---------------------------------------------------------------------------
# Log-log regression
# ---------------------------------------------------------------------------

def fit_convergence_slope(results: list[dict]) -> float:
    """Fit log(l2) vs log(dx) and return the observed slope.

    For a 2nd-order scheme the slope should be close to +2.0 because
    error ∝ dx^2, so log(error) = 2*log(dx) + constant.

    Parameters
    ----------
    results : list of dicts with keys "dx" and "l2" (output of run_convergence_sweep).

    Returns
    -------
    float
        Observed convergence slope (should be ≈ +2.0 for 2nd-order).
    """
    log_dx = np.log([r["dx"] for r in results])
    log_l2 = np.log([r["l2"] for r in results])
    # Linear fit: log_l2 = slope * log_dx + intercept
    slope, _ = np.polyfit(log_dx, log_l2, 1)
    return float(slope)


# ---------------------------------------------------------------------------
# Pass/fail assertion
# ---------------------------------------------------------------------------

def check_slope(slope: float, expected: float = 2.0, rtol: float = 0.15) -> bool:
    """Return True if slope is within rtol of expected.

    Default: slope must be within 15% of +2.0, i.e. in [1.70, 2.30].

    Parameters
    ----------
    slope : float
        Observed log-log slope.
    expected : float
        Theoretical slope (default +2.0 for 2nd-order).
    rtol : float
        Relative tolerance.
    """
    return bool(np.isclose(slope, expected, rtol=rtol))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the 4-point convergence sweep and save results.

    Output JSON schema:
        {
          "sweep": [{"N": int, "dx": float, "l2": float}, ...],
          "observed_slope": float,
          "expected_slope": 2.0,
          "slope_passed":   bool,
          "status":         "convergence-verified" | "slope-check-failed"
        }
    """
    cfg = load_config("config.yaml")

    print("Running Week 02.5 convergence sweep...")
    sweep_data = run_convergence_sweep(cfg)

    slope   = fit_convergence_slope(sweep_data)
    passed  = check_slope(slope, expected=2.0, rtol=0.15)

    for row in sweep_data:
        print(f"  N={row['N']:4d}  dx={row['dx']:.4f}  L2={row['l2']:.4e}")
    print(f"Observed slope: {slope:.3f}  (expected ~ 2.0)  {'PASS' if passed else 'FAIL'}")

    out = {
        "sweep":          sweep_data,
        "observed_slope": slope,
        "expected_slope": 2.0,
        "slope_passed":   passed,
        "status":         "convergence-verified" if passed else "slope-check-failed",
    }

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "week02_5_convergence.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(f"\nSaved to outputs/week02_5_convergence.json")


if __name__ == "__main__":
    main()
