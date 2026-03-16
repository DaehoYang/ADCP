"""Week 01 M1 runner: preflight + run-log stub only.

Use this script to complete Module 1 without needing M2–M4 implemented.
It validates the config, computes dt, and writes outputs/run_log.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from solver_2d import load_config, preflight


def main() -> None:
    cfg = load_config("config.yaml")

    nx            = int(cfg.get("nx", 80))
    ny            = int(cfg.get("ny", 80))
    length_x      = float(cfg.get("length_x", 1.0))
    length_y      = float(cfg.get("length_y", 1.0))
    c             = float(cfg.get("c", 1.0))
    t_end         = float(cfg.get("t_end", 0.2))
    safety_factor = float(cfg.get("safety_factor", 0.5))
    energy_eps    = float(cfg.get("energy_eps", 1e-12))
    bc            = str(cfg.get("bc", "dirichlet"))

    x  = np.linspace(0.0, length_x, nx)
    y  = np.linspace(0.0, length_y, ny)
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    dt_max = 1.0 / (c * np.sqrt((1.0 / dx ** 2) + (1.0 / dy ** 2)))
    dt     = safety_factor * dt_max

    preflight_cfg = {"nx": nx, "ny": ny, "bc": bc, "dt": dt, "dx": dx}
    preflight(preflight_cfg)

    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    run_log = {
        "label": "preflight-only",
        "nx": nx, "ny": ny,
        "dx": dx, "dy": dy, "dt": dt,
        "t_end": t_end,
        "bc": bc,
        "c": c,
        "safety_factor": safety_factor,
        "energy_eps": energy_eps,
        "note": "M1 stub log; full diagnostics added in M4.",
    }
    (out_dir / "run_log.json").write_text(
        json.dumps(run_log, indent=2), encoding="utf-8"
    )
    print(json.dumps(run_log, indent=2))


if __name__ == "__main__":
    main()
