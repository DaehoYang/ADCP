# Week 01: Physical Law to Computable Baseline

## Goal

Build a **baseline-ready** 2D wave solver with logged diagnostics.  
This week produces a *measurement framework*, not validated physics.

---

## File Map

| File | Role |
|:---|:---|
| `config.yaml` | All simulation parameters (edit here, not in code) |
| `solver_2d.py` | Main solver with TODO stubs (M1–M4) |
| `m1_preflight_only.py` | M1 runner: preflight + run-log stub only |
| `test_solver_2d.py` | pytest suite — run after each module |
| `report_template.md` | Evidence-first report template |
| `report_example.md` | Filled example for reference |
| `sample_run_log.json` | Expected `outputs/run_log.json` shape |
| `sample_summary.json` | Summary JSON reference |
| `baseline_report.md` | **Your deliverable** (fill this in) |

---

## Module Sequence

```
M1  preflight()             →  outputs/run_log.json (stub)
    run: python m1_preflight_only.py
M2  laplacian_2d()          →  pytest -q -k laplacian  PASS
    first_step()            →  outputs/ex1_note.txt
M3  update_step()           →  outputs/u_t0.npy  u_tmid.npy  u_tend.npy
M4  relative_energy_drift() →  outputs/run_log.json (drift field added)
M5  baseline_report.md      →  evidence table + 3 unresolved risks
```

---

## Quick Start

```bash
# from week01/ directory
python m1_preflight_only.py # M1: preflight + stub log only
python solver_2d.py          # run full solver
pytest test_solver_2d.py -v  # run all tests
pytest -q -k laplacian       # M2 filter
pytest -q -k drift           # M4 filter
```

---

## Pass Criteria (full checklist)

- [ ] Solver runs end-to-end without crash.
- [ ] Three snapshot files exist: `outputs/u_t0.npy`, `u_tmid.npy`, `u_tend.npy`.
- [ ] `outputs/run_log.json` includes `dx, dy, dt, nx, ny, t_end, bc, energy_eps`.
- [ ] `relative_energy_drift` and `compute_l2_stub_value` are recorded in the log.
- [ ] `baseline_report.md` has one status label and three unresolved risks.

---

## Troubleshooting

| Symptom | Fix |
|:---|:---|
| Shape mismatch error | Check `np.zeros((nx, ny))` — ensure both state arrays share the same shape |
| Boundaries drift from 0 | Re-apply `enforce_dirichlet` after each update step |
| No snapshot files generated | Confirm save block runs at `t0`, `t_mid`, `t_end`; check `outputs/` is writable |
| Too slow | Replace any `for i, j` loops with vectorised slicing on `[1:-1, 1:-1]` |
| `yaml` not found | `pip install pyyaml` |

---

## Deliverable

`week01/baseline_report.md` — use `report_template.md` as the basis.  
Every numeric claim must cite a file (e.g. `outputs/run_log.json`).
