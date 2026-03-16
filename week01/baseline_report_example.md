# Week 01 Baseline Report (Example)

## Status Label

`baseline-ready`

## Required Numeric Fields

- nx: 80
- ny: 80
- dx: 0.012658227848101266
- dy: 0.012658227848101266
- dt: 0.004475942048745247
- t_end: 0.2
- c: 1.0
- safety_factor: 0.5
- energy_eps: 1.0e-12
- relative_energy_drift: 8.7e-03
- compute_l2_stub_value: 1.432e-01

## Required Files

- [x] `outputs/ex1_note.txt`
- [x] `outputs/u_t0.npy`
- [x] `outputs/u_tmid.npy`
- [x] `outputs/u_tend.npy`
- [x] `outputs/run_log.json`

## Failure Classification

- [ ] `needs-fix: artifact-missing`
- [ ] `needs-fix: shape-or-guard-failure`
- [ ] `needs-fix: suspicious-drift-pattern`
- [x] `baseline-ready`

## Unresolved Risks (minimum 3)

1. Grid convergence is unknown until analytic reference is added.
2. Boundary reflection is visible but not quantified.
3. Long-time behavior beyond `t_end=0.2` is not checked.

## Reflection Questions

1. Which artifact best supports your status label?
- `outputs/run_log.json`.
2. Which failure mode remains untested in Week 01?
- Analytic accuracy failure.
3. What is your Week 02 bridge task?
- Implement a valid reference mode and evaluate `compute_l2`.
