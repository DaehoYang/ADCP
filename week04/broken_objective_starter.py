"""Week 04 Lab 2: Broken inverse problem objective (objective leakage).

AI-Driven Computational Physics — Graduate Course (Broken-First Lab)

This file contains ONE deliberate bug in the cost function.
The optimizer converges to loss ≈ 0.000 for ANY input theta — it solves nothing.

Your task:
    1. Run this file and observe that it "succeeds" perfectly.
    2. Inspect cost() below: why does it always return 0.0?
    3. Apply the smoke test at the bottom to confirm the leakage.
    4. Record the fix, then compare with the diff answer shown in week04.md.

Bug location: inside the cost() function only.

Run
---
    cd week04
    python broken_objective_starter.py

Expected output (broken):
    Smoke test: cost([2.5]) = 0.0  ← should be >> cost([1.5])
    cost([1.5]) = 0.0              ← trivially zero for ALL inputs
    Recovered c: <anything>        ← optimizer result is meaningless
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from solver_2d import discrete_laplacian, load_config, make_initial_field


def _forward_solve(c: float, nx: int, t_end: float, courant: float = 0.55) -> np.ndarray:
    """Fast forward solver used by the broken-first leakage demo."""
    if c <= 0.0:
        return np.full(nx * nx, 1e9)
    dx = 1.0 / (nx - 1)
    dy = dx
    dt = courant * dx / (c * math.sqrt(2.0))
    n_steps = max(1, int(math.ceil(t_end / dt)))
    dt = t_end / n_steps

    u, v = make_initial_field(nx, nx)
    for _ in range(n_steps):
        lap = discrete_laplacian(u, dx, dy)
        v += dt * c ** 2 * lap
        u += dt * v
        u[0, :] = u[-1, :] = u[:, 0] = u[:, -1] = 0.0
    return u.ravel().copy()


# ---------------------------------------------------------------------------
# Broken objective — contains objective leakage bug
# ---------------------------------------------------------------------------

def cost(params: list, cfg: dict) -> float:
    """*** THIS OBJECTIVE HAS A BUG: objective leakage ***

    Both y_ref and y_obs are computed from the same c_est (params[0]).
    The L2 distance between two identical arrays is always 0.0.
    The optimizer finds loss = 0.0 trivially, without solving anything.

    Fix: load y_obs from a pre-computed file (generated once with c_true).
    """
    c_est = params[0]
    if c_est <= 0.0:
        return 1e9

    nx = int(cfg.get("obs_nx", 21))
    t_end = float(cfg.get("obs_t_end", 2.0))
    courant = float(cfg.get("obs_courant", 0.55))

    # Bug: both y_ref and y_obs are computed from the SAME c_est
    y_ref = _forward_solve(c_est, nx, t_end, courant)   # ← should be loaded from disk
    y_obs = _forward_solve(c_est, nx, t_end, courant)   # ← always identical to y_ref

    return float(np.linalg.norm(y_ref - y_obs) / (np.linalg.norm(y_obs) + 1e-14))


# ---------------------------------------------------------------------------
# Demo runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cfg = load_config("config.yaml")

    print("=== Broken Objective Demo ===\n")
    J_true = cost([1.5], cfg)
    J_wrong = cost([2.5], cfg)
    print(f"cost([1.5]) = {J_true:.6f}   (c_true)")
    print(f"cost([2.5]) = {J_wrong:.6f}   (wrong c)")
    print()

    # Smoke test — should FAIL with the broken objective
    if J_wrong <= J_true:
        print("SMOKE TEST FAILS: cost([2.5]) <= cost([1.5])")
        print("This confirms objective leakage — both calls return 0.0.")
        print("The optimizer cannot distinguish correct from incorrect c.\n")
    else:
        print("SMOKE TEST PASSES: objective is leak-free.")

    # Run a quick optimization to show "perfect" convergence on a broken objective
    try:
        from skopt import gp_minimize
        from skopt.space import Real

        low = float(cfg.get("opt_search_low", 0.5))
        high = float(cfg.get("opt_search_high", 2.0))
        result = gp_minimize(
            lambda p: cost(p, cfg),
            [Real(low, high)],
            n_calls=15,
            random_state=0,
            verbose=False,
        )
        print(f"Optimizer result: c_recovered={result.x[0]:.4f},  loss={result.fun:.6f}")
        print("Notice: loss is 0.000 regardless of recovered c — the objective is broken.")
    except ImportError:
        print("(scikit-optimize not installed — skipping optimizer demo)")
