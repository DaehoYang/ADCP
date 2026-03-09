"""Week 00 starter: minimal 1D wave solver with TODO blocks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import yaml


def gaussian(x: np.ndarray, x0: float, sigma: float) -> np.ndarray:
    return np.exp(-((x - x0) ** 2) / (2.0 * sigma**2))


def enforce_dirichlet(u: np.ndarray) -> None:
    u[0] = 0.0
    u[-1] = 0.0


def compute_time_step(c: float, dx: float, safety_factor: float, dt_override: float | None) -> float:
    """Return a valid dt and raise if CFL ratio exceeds 1."""
    raise NotImplementedError("TODO: implement compute_time_step")


def first_step(u_prev: np.ndarray, ratio: float) -> np.ndarray:
    """Taylor-consistent first step with zero initial velocity."""
    raise NotImplementedError("TODO: implement first_step")


def advance_step(u_prev: np.ndarray, u_curr: np.ndarray, ratio: float) -> np.ndarray:
    """One leapfrog-style update with fixed-end boundaries."""
    raise NotImplementedError("TODO: implement advance_step")


def solve_wave_1d(cfg: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    length = float(cfg.get("length", 1.0))
    c = float(cfg.get("c", 1.0))
    nx = int(cfg.get("nx", 201))
    t_end = float(cfg.get("t_end", 0.2))
    safety_factor = float(cfg.get("safety_factor", 0.8))
    dt_override = cfg.get("dt", None)
    x0 = float(cfg.get("x0", 0.5))
    sigma = float(cfg.get("sigma", 0.08))

    if nx < 3:
        raise ValueError("nx must be at least 3")
    if c <= 0.0:
        raise ValueError("c must be positive")

    x = np.linspace(0.0, length, nx)
    dx = x[1] - x[0]

    dt = compute_time_step(c, dx, safety_factor, dt_override)
    ratio = c * dt / dx

    nt = int(np.ceil(t_end / dt)) + 1
    t = np.linspace(0.0, dt * (nt - 1), nt)

    u_prev = gaussian(x, x0=x0, sigma=sigma)
    enforce_dirichlet(u_prev)

    u_curr = first_step(u_prev, ratio)

    u_hist = np.zeros((nt, nx), dtype=float)
    u_hist[0] = u_prev
    if nt > 1:
        u_hist[1] = u_curr

    for n in range(1, nt - 1):
        u_next = advance_step(u_prev, u_curr, ratio)
        u_prev, u_curr = u_curr, u_next
        u_hist[n + 1] = u_curr

    return x, t, u_hist, dx, dt


def build_summary(x: np.ndarray, t: np.ndarray, u_hist: np.ndarray, dx: float, dt: float, c: float) -> dict:
    """Build week00 summary JSON fields."""
    raise NotImplementedError("TODO: implement build_summary")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Week 00 bootcamp starter")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        raise FileNotFoundError(f"config not found: {cfg_path}")

    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    x, t, u_hist, dx, dt = solve_wave_1d(cfg)
    summary = build_summary(x, t, u_hist, dx, dt, float(cfg.get("c", 1.0)))

    out_path = Path(cfg.get("out_json", "logs/week00_summary.json"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
