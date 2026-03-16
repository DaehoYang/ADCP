# Week 01 Report Template

## Goal Statement

State one sentence proving why this run is baseline-ready.

## Status Classification

- status: `baseline-ready` or `needs-fix`
- reason (1-2 lines):

## Run Metadata (Numeric)

- date:
- student:
- script: `solver_2d.py`
- config: `config.yaml`
- nx:
- ny:
- dx:
- dy:
- dt:
- t_end:
- c:
- safety_factor:
- energy_eps:

## Checkpoint Artifacts

- [ ] `outputs/ex1_note.txt`
- [ ] `outputs/u_t0.npy`
- [ ] `outputs/u_tmid.npy`
- [ ] `outputs/u_tend.npy`
- [ ] `outputs/run_log.json`

## Evidence Table

| Metric | Value | Evidence File | Interpretation |
| :-- | :-- | :-- | :-- |
| relative_energy_drift |  | `outputs/run_log.json` |  |
| compute_l2_stub_value |  | `outputs/run_log.json` |  |

## Failure Classification

Choose one and justify with numeric evidence.

- [ ] `needs-fix: artifact-missing`
- [ ] `needs-fix: shape-or-guard-failure`
- [ ] `needs-fix: suspicious-drift-pattern`
- [ ] `baseline-ready`

## Unresolved Risks (minimum 3)

1.
2.
3.

## Reflection Questions

1. Which artifact most strongly supports your status label?
2. Which failure mode is still untested in Week 01?
3. Next-week bridge: what analytic reference will you use for `compute_l2`?
