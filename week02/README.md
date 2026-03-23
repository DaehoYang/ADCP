# Week 02 Practice Pack — Analytic Reference and First Error Measurement

**Course:** AI-Driven Computational Physics — Graduate Level
**Prerequisite:** Week 01 (`baseline-ready` solver)
**Status upgrade target:** `baseline-ready` → `reference-checked`

---

## Goal

Define an exact analytic reference solution for the 2D wave equation, implement
a grid-area-scaled L2 error metric, and record one synchronized single-case
measurement. The result is a `reference-checked` status label backed by
reproducible numerical evidence.

> **Core principle:** A simulation that passes an analytic-limit gate and records
> a finite L2 scalar is making a *scientific claim*. A simulation that only
> "looks correct" is not.

---

---

## Scope Boundary

| Scope | This week (02) | Next (02.5) |
|-------|---------------|-------------|
| Reference function definition | ✓ | — |
| Single-case L2 measurement | ✓ | — |
| Analytic-limit gate | ✓ | — |
| Physical invariant diagnostics | ✓ (diagnostic only) | — |
| Resolution sweep (4-point) | — | ✓ |
| Log-log regression & slope assert | — | ✓ |

**Rule:** Do not attempt a multi-resolution sweep this week. Get one correct
scalar first, then automate in Week 02.5.

---

---

## Files

| File | Purpose |
|------|---------|
| `starter_reference_check.py` | 5-TODO starter — implement all functions here |
| `test_reference_check.py` | pytest suite mirroring the 5-module structure |
| `convergence_sweep_starter.py` | Week 02.5 preview — resolution sweep stub |
| `config.yaml` | Grid / physics / measurement-sync parameters |
| `report_template.md` | Submission template with evidence fields |
| `report_example.md` | Filled example report |
| `sample_week02_results.json` | Expected JSON output schema |
| `outputs/` | Generated run artifacts (`week02_results.json`) |

---

## Module Map and Execution Gates

### Module 1 — Error Budget *(Conceptual)*
- Understand the V-curve: $E(h) = C_1 h^p + C_2 \epsilon_\text{mach}/h$
- Know that "smaller grid is always better" is **false**
- **Gate:** Explain both error types from memory before Module 2

### Module 2 — Integration Kernel: `trapezoidal(f, a, b, n)`
- Composite Trapezoidal Rule — error order $\mathcal{O}(h^2)$
- Endpoint half-weight: `weights[0] = weights[-1] = 0.5`
- **Gate:** All `TestTrapezoidal` tests pass

### Module 3 — L2 Norm Contract: `compute_l2` + `reference`
- Formula: $\|e\|_2 = \sqrt{\sum_{ij}(u^\text{num}_{ij} - u^\text{ref}_{ij})^2 \Delta x \Delta y}$
- The `dx*dy` factor is a Riemann-sum weight — omitting it makes the result grid-dependent
- **Gate:** `reference` satisfies BC on all walls; `compute_l2` is resolution-invariant

### Module 4 — Variable Isolation: `single_case_l2_measurement` + `analytic_limit_test`
1. **Hold physical time fixed:** always measure at the same `t_star`
2. **Fix Courant number:** `dt = courant * dx / c`
- **Gate:** `analytic_limit_passed: true` in `outputs/week02_results.json`

### Module 5 — Report and Bridge to Week 02.5
- Fill `report_template.md` with all evidence
- Answer the 4-point sweep bridge question

---

## What You Implement

In `starter_reference_check.py` (5 TODOs):

1. **`reference(x, y, t, c)`** — exact separable sine mode
   $$u = \sin(\pi x)\sin(\pi y)\cos(\sqrt{2}\,\pi c\,t)$$
2. **`compute_l2(u_num, u_ref, dx, dy)`** — L2 with Riemann-sum area weight
3. **`trapezoidal(f, a, b, n)`** — composite trapezoidal rule
4. **`analytic_limit_test()`** — integration gate: $\int_0^2 x\,dx = 2.0$
5. **`single_case_l2_measurement(cfg)`** — synchronized L2 at fixed `t_star`

In `test_reference_check.py` (extend or complete):

6. Shape / finite-value happy-path tests
7. Input guard tests (invalid shape or invalid spacing)
8. Resolution-invariance test for `compute_l2`

**Extension (ungraded):** `check_pde_residual` and `wave_energy` in `starter_reference_check.py`.

---

## Typical Run Order

```bash
cd week02
python starter_reference_check.py   # produces outputs/week02_results.json
pytest test_reference_check.py -v   # all tests must pass
```

Expected `outputs/week02_results.json` keys:
```json
{
  "status": "reference-checked",
  "analytic_limit_passed": true,
  "analytic_limit_value": 2.0,
  "single_case_l2": 9.97e-4
}
```

---

## In-Class Exercise Blocks (120 min)

| Exercise | Time | Task | Artifact |
|----------|------|------|----------|
| 1 | 25 min | Implement `reference(...)`, validate shape + BC contract | Report §1 |
| 2 | 30 min | Implement `compute_l2(...)` + `single_case_l2_measurement(cfg)` | `outputs/week02_results.json` |
| 3 | 25 min | Implement `trapezoidal(...)` + `analytic_limit_test()` | JSON analytic-limit fields |
| 4 | 40 min | Implement pytest happy + guard paths; run full suite | pytest output snippet |

---

## Checkpoint Artifacts

1. `reference(...).shape == mesh.shape` — documented in report §1
2. `outputs/week02_results.json` — contains `single_case_l2`
3. `outputs/week02_results.json` — contains `analytic_limit_passed: true`
4. pytest output snippet — proves happy path and at least one guard path pass

---

## Deliverables

1. Completed `starter_reference_check.py` (all 5 TODOs)
2. Completed `test_reference_check.py` (all tests pass)
3. `outputs/week02_results.json`
4. Completed `report_template.md`

---

## Status Rule

| Condition | Status |
|-----------|--------|
| `analytic_limit_test()` fails | `needs-fix` |
| `analytic_limit_test()` passes | `reference-checked` |

Status is a **gate**, not an opinion. A visually perfect plot with a failed
analytic-limit test must be labelled `needs-fix`.

---

## Reflection Questions

1. Which artifact most strongly supports your status label, and why?
2. If the analytic-limit passes but L2 is unexpectedly high, what is your first debug hypothesis?
3. Week 02.5 bridge: what four-point $N$ sweep range would you choose and why?
4. Why does fixing the Courant number matter for interpreting the convergence slope?

---

## Reference Examples

- `sample_week02_results.json` — expected output JSON schema
- `report_example.md` — complete filled report

| 2 | 30 min | Implement `compute_l2(...)` + `single_case_l2_measurement(cfg)` | `outputs/week02_results.json` |
| 3 | 25 min | Implement `trapezoidal(...)` + `analytic_limit_test()` | JSON analytic-limit fields |
| 4 | 40 min | Implement pytest happy + guard paths | pytest output snippet |

---

## Checkpoint Artifacts

1. `reference(...).shape == mesh.shape` — documented in report §1
2. `outputs/week02_results.json` — contains `single_case_l2`
3. `outputs/week02_results.json` — contains `analytic_limit_passed` + `analytic_limit_value`
4. pytest output snippet — proves happy path and at least one guard path

---

## Deliverables

1. Completed `starter_reference_check.py` (all 5 TODOs)
2. Completed `test_reference_check.py` (all tests pass)
3. `outputs/week02_results.json`
4. Completed `report_template.md`

---

## Status Rule

| Condition | Status |
|-----------|--------|
| `analytic_limit_test()` fails | `needs-fix` |
| `analytic_limit_test()` passes | `reference-checked` |

Status is a **gate**, not an opinion. A visually perfect plot with a failed
analytic-limit test must be labelled `needs-fix`.

---

## Reflection Questions

1. Which artifact most strongly supports your status label, and why?
2. If the analytic-limit passes but L2 is unexpectedly high, what is your first debug hypothesis?
3. Week 02.5 bridge: what four-point sweep range would you choose and why?

---

## Reference Examples

- `sample_week02_results.json` — expected output JSON schema
- `report_example.md` — complete filled report
