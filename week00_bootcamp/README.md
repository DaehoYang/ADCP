# Week 00 Practice Pack (Starter)

Goal: build a bootcamp-ready baseline by verifying environment setup and producing one reproducible 1D wave run summary.

## Files

- `solver_bootcamp_starter.py`: TODO-based starter for a minimal 1D wave run
- `config.yaml`: default Week 00 run config
- `report_template.md`: submission template
- `report_example.md`: one filled report example
- `sample_week00_summary.json`: expected output JSON schema example
- `logs/`: generated artifacts (`week00_summary.json`)
- `environment/test_bootcamp_setup.py`: environment dependency check
- `environment/setup_ssh.py`: helper for local SSH config
- `environment/docker-compose.yml`: bootcamp container launcher
- `environment/`: Dockerfile and requirements

## What You Must Implement

In `solver_bootcamp_starter.py`:

1. `compute_time_step(c, dx, safety_factor, dt_override)`
2. `first_step(u_prev, ratio)`
3. `advance_step(u_prev, u_curr, ratio)`
4. `build_summary(...)`

## Typical Run Order

From `week00_bootcamp/`:

```bash
python environment/test_bootcamp_setup.py
python solver_bootcamp_starter.py --config config.yaml
```

Expected output file:

- `logs/week00_summary.json`

## Deliverables

1. Completed `solver_bootcamp_starter.py`
2. `logs/week00_summary.json`
3. Completed `report_template.md`

## Status Rule

- Use `bootcamp-ready` only when environment checks pass and `logs/week00_summary.json` is generated with a valid CFL ratio (`c_dt_over_dx <= 1.0`).
- Use `needs-fix` if setup checks fail, the run fails, or summary evidence is missing.

## Reference Examples

- `sample_week00_summary.json`: expected output schema and field names
- `report_example.md`: one filled report example
