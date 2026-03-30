"""Week 04 solver: CFL pre-run guard and runtime watchdog.

Run with:
    python broken_solver_starter.py --c 1.0 --dx 0.01 --dy 0.01 --dt 0.006 --out_json logs/run_summary.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def get_max_dt_2d(c: float, dx: float, dy: float) -> float:
    """Return the maximum stable timestep for a 2D wave solver.

    Derived from the 2D CFL stability condition:
        c * dt * sqrt(1/dx^2 + 1/dy^2) <= 1
    """
    return 1.0 / (c * np.sqrt(1.0 / dx + 1.0 / dy))


def check_cfl(c: float, dt: float, dx: float, dy: float) -> float:
    """Return the effective CFL number. Must be <= 1.0 for stability."""
    cx = c * dt / dx
    cy = c * dt / dy
    return max(cx, cy)


def _validate_positive(
    c: float, dx: float, dy: float, dt: float, nx: int, ny: int, t_end: float
) -> None:
    if c <= 0 or dx <= 0 or dy <= 0 or dt <= 0:
        raise ValueError("c, dx, dy, dt must all be positive.")
    if nx <= 2 or ny <= 2:
        raise ValueError("nx and ny must be > 2.")
    if t_end <= 0:
        raise ValueError("t_end must be positive.")


def _make_initial_field(nx: int, ny: int) -> np.ndarray:
    x = np.linspace(0.0, 1.0, nx)
    y = np.linspace(0.0, 1.0, ny)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    return np.sin(np.pi * xx) * np.sin(np.pi * yy)


def run_simulation(
    c: float,
    dx: float,
    dy: float,
    dt: float,
    nx: int,
    ny: int,
    t_end: float,
    safety_factor: float = 0.95,
    watchdog_interval: int = 100,
    amp_threshold: float = 1e4,
) -> dict:
    """Run the 2D wave simulation with CFL guard and runtime watchdog."""
    _validate_positive(c, dx, dy, dt, nx, ny, t_end)

    dt_max = get_max_dt_2d(c, dx, dy)
    if dt > safety_factor * dt_max:
        raise ValueError(
            f"CFL Violation: dt={dt:.4e} exceeds safe limit {safety_factor * dt_max:.4e}. "
            f"Suggested safe dt: {0.9 * dt_max:.4e}"
        )

    u_prev = _make_initial_field(nx, ny)
    u_curr = u_prev.copy()

    r2x = (c * dt / dx) ** 2
    r2y = (c * dt / dy) ** 2
    num_steps = int(t_end / dt)

    log: list[dict] = []
    status = "completed"

    for step in range(num_steps):
        u_next = np.zeros_like(u_curr)
        u_next[1:-1, 1:-1] = (
            2.0 * u_curr[1:-1, 1:-1]
            - u_prev[1:-1, 1:-1]
            + r2x * (u_curr[2:, 1:-1] - 2.0 * u_curr[1:-1, 1:-1] + u_curr[:-2, 1:-1])
            + r2y * (u_curr[1:-1, 2:] - 2.0 * u_curr[1:-1, 1:-1] + u_curr[1:-1, :-2])
        )
        u_prev = u_curr
        u_curr = u_next

        if step % watchdog_interval == 0:
            max_u = float(np.max(np.abs(u_curr)))
            log.append({"step": step, "max_u": max_u})
            print(f"Step {step:5d}: max|u| = {max_u:.4e}")

            if not np.isfinite(u_curr).all():
                status = "nan_detected"
                break
            if max_u > amp_threshold:
                status = "amplitude_explosion"
                break

    cfl_value = check_cfl(c, dt, dx, dy)
    return {
        "status": status,
        "cfl_value": cfl_value,
        "dt_max": dt_max,
        "dt": dt,
        "num_steps": num_steps,
        "watchdog_log": log,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Week 04 CFL guard solver")
    p.add_argument("--c", type=float, default=1.0)
    p.add_argument("--dx", type=float, default=0.01)
    p.add_argument("--dy", type=float, default=0.01)
    p.add_argument("--dt", type=float, default=0.006)
    p.add_argument("--nx", type=int, default=80)
    p.add_argument("--ny", type=int, default=80)
    p.add_argument("--t_end", type=float, default=0.2)
    p.add_argument("--safety_factor", type=float, default=0.95)
    p.add_argument("--watchdog_interval", type=int, default=50)
    p.add_argument("--amp_threshold", type=float, default=1e4)
    p.add_argument("--out_json", type=str, default="logs/run_summary.json")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = run_simulation(
            c=args.c,
            dx=args.dx,
            dy=args.dy,
            dt=args.dt,
            nx=args.nx,
            ny=args.ny,
            t_end=args.t_end,
            safety_factor=args.safety_factor,
            watchdog_interval=args.watchdog_interval,
            amp_threshold=args.amp_threshold,
        )
        print(json.dumps(result, indent=2))
        out_path = Path(args.out_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        print(f"{type(exc).__name__}: {exc}")
        raise


if __name__ == "__main__":
    main()
