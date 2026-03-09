# Week 00 Report Example

## 1) Setup Evidence
- Command: `python environment/test_bootcamp_setup.py`
- Result summary: all required imports were detected, and the script exited with code 0.

## 2) Run Evidence
- Command: `python solver_bootcamp_starter.py --config config.yaml`
- Output file: `logs/week00_summary.json`
- Key metrics:
  - `nx`: 201
  - `nt`: 51
  - `c_dt_over_dx`: 0.8
  - `max_abs_u`: 1.0

## 3) Verdict
- Status label: `bootcamp-ready`
- Reason (2-3 sentences with numeric evidence): The setup check passed without missing dependencies. The summary JSON was generated and reports `c_dt_over_dx = 0.8`, which satisfies the CFL bound (`<= 1.0`). The run produced finite amplitude metrics and completed normally.
