# Week 01 Report Example

## Goal Statement

This run is baseline-ready because the starter solver produced all required artifacts and log metrics under fixed configuration.

## Status Classification

- status: `baseline-ready`
- reason (1-2 lines): all required files exist, and the run log includes reproducibility metadata and numeric diagnostics.

## Run Metadata (Numeric)

- date: 2026-03-08
- student: Example Student
- script: `solver_2d.py`
- config: `config.yaml`
- nx: 80
- ny: 80
- dx: 0.012658227848101266
- dy: 0.012658227848101266
- dt: 0.004475942048745247
- t_end: 0.2
- c: 1.0
- safety_factor: 0.5
- energy_eps: 1.0e-12

## Checkpoint Artifacts

- [x] `outputs/ex1_note.txt`
- [x] `outputs/u_t0.npy`
- [x] `outputs/u_tmid.npy`
- [x] `outputs/u_tend.npy`
- [x] `outputs/run_log.json`

## Evidence Table

| Metric | Value | Evidence File | Interpretation |
| :-- | :-- | :-- | :-- |
| relative_energy_drift | 8.7e-03 | `outputs/run_log.json` | finite and recorded for Week 02 thresholding |
| compute_l2_stub_value | 1.432e-01 | `outputs/run_log.json` | interface callable; analytic meaning deferred |

## Failure Classification

Choose one and justify with numeric evidence.

- [ ] `needs-fix: artifact-missing`
- [ ] `needs-fix: shape-or-guard-failure`
- [ ] `needs-fix: suspicious-drift-pattern`
- [x] `baseline-ready`

## Unresolved Risks (minimum 3)

1. Boundary reflection artifacts are not quantified yet.
2. Long-horizon drift beyond `t_end=0.2` is unknown.
3. Analytic reference mode is not selected yet.

## Reflection Questions

1. Which artifact most strongly supports your status label?
- `outputs/run_log.json` because it contains reproducibility metadata and drift scalar.
2. Which failure mode is still untested in Week 01?
- Accuracy against analytic reference remains untested.
3. Next-week bridge: what analytic reference will you use for `compute_l2`?
- A separable sine mode satisfying fixed Dirichlet boundaries.
