"""Week 04 Lab 1: Broken absorbing boundary condition.

AI-Driven Computational Physics — Graduate Course (Broken-First Lab)

This file contains TWO deliberate bugs in the absorbing BC implementation.
The simulation runs without errors, but:
    - A centered symmetric pulse evolves asymmetrically
    - Symmetry residual R_sym grows to ~0.15 by step 200 (expected: < 0.01)

Your task:
    1. Read the apply_absorbing_bc function below carefully.
    2. Identify both bugs (hint: check sign convention and edge coverage).
    3. Record what you find, then compare with the diff answer shown in week04.md.

Bug locations: only inside apply_absorbing_bc — do not modify other code.

Run
---
    cd week04
    python broken_boundary_starter.py

Expected output (broken):
    R_sym grows large by step 200   ← should stay < 0.01 for a symmetric setup
    Energy may increase             ← absorbing behavior should not inject energy
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from solver_2d import (
    compute_energy,
    discrete_laplacian,
    estimate_outward_flux,
    load_config,
    make_initial_field,
)


# ---------------------------------------------------------------------------
# Broken absorbing BC — contains 2 bugs
# ---------------------------------------------------------------------------

def apply_absorbing_bc(u: np.ndarray, alpha: float) -> None:
    """Apply Mur-like absorbing BC to all four edges.

    *** THIS IMPLEMENTATION HAS TWO BUGS ***
    Find them by observing the symmetry breakdown in the simulation output.
    """
    # Left edge  (outward direction: -x)
    u[0,  :] = (1 - alpha) * u[0,  :] + alpha * u[1,  :]

    # Right edge  (outward direction: +x)
    # Bug 1: wrong sign — should use +alpha, not (1 + alpha) / -(alpha)
    u[-1, :] = (1 + alpha) * u[-1, :] - alpha * u[-2, :]

    # Bug 2: top and bottom edges are NOT updated here.
    # Without BC assignment, these cells inherit leapfrog values that
    # treat the edge as a Dirichlet boundary (high-frequency artifact).
    # The fix: add identical absorbing updates for u[:,0] and u[:,-1].


def _apply_dirichlet(u: np.ndarray) -> None:
    u[0, :] = u[-1, :] = u[:, 0] = u[:, -1] = 0.0


# ---------------------------------------------------------------------------
# Simulation runner (uses the broken BC — no need to modify below this line)
# ---------------------------------------------------------------------------

def run_broken_simulation(cfg: dict, n_steps: int = 200) -> None:
    nx = int(cfg["nx"])
    ny = int(cfg["ny"])
    length = float(cfg.get("length", 1.0))
    c = float(cfg["c"])
    courant = float(cfg["courant"])
    dx = length / (nx - 1)
    dy = length / (ny - 1)
    dt = courant * dx / (c * math.sqrt(2.0))
    alpha = c * dt / dx

    u, v = make_initial_field(nx, ny, length)
    # Apply dirichlet initially to set clean boundaries
    _apply_dirichlet(u)
    E0 = compute_energy(u, v, c, dx, dy)

    sym_log = []

    for step in range(n_steps):
        lap = discrete_laplacian(u, dx, dy)
        v += dt * c ** 2 * lap
        u += dt * v
        # Apply broken absorbing BC (top/bottom stay whatever leapfrog produced)
        apply_absorbing_bc(u, alpha)

        if step % 50 == 0:
            rot = np.rot90(u)
            R_sym = np.linalg.norm(u - rot) / (np.linalg.norm(u) + 1e-14)
            E = compute_energy(u, v, c, dx, dy)
            sym_log.append({"step": step, "R_sym": float(R_sym), "E": float(E)})
            print(f"  step {step:4d}  R_sym={R_sym:.4f}  E={E:.6f} (E0={E0:.6f})")

    print(f"\nFinal R_sym = {sym_log[-1]['R_sym']:.4f}  (should be < 0.01 if BC is correct)")
    print("If R_sym is large, there are boundary bugs — check apply_absorbing_bc.")


if __name__ == "__main__":
    cfg = load_config("config.yaml")
    run_broken_simulation(cfg)
