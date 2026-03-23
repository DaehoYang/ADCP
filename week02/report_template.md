# Week 02 Report — Analytic Reference and First Error Measurement

**Course:** AI-Driven Computational Physics
**Student name / ID:** `<fill in>`
**Date:** `<fill in>`

---

## Scope Boundary Acknowledgment

This week's scope is **single-case measurement only** — not a convergence proof.

- [ ] I measured L2 error at one fixed `t_star` and one fixed resolution
- [ ] I did NOT run a resolution sweep (that is Week 02.5)
- [ ] I used `t_star` and Courant number directly from `config.yaml` without overriding them

---

## Final Status

| Gate | Result |
|------|--------|
| Analytic-limit test passed | `<True / False>` |
| `single_case_l2` recorded | `<float>` |
| **Final label** | `<reference-checked \| needs-fix>` |

**If `needs-fix`, select the failure class:**
- [ ] Indexing / weighting bug (`trapezoidal` endpoint weight)
- [ ] Shape mismatch (`compute_l2` guard)
- [ ] `dx*dy` scaling omitted (Riemann-sum weight)
- [ ] Reference formula wrong (`reference` function)
- [ ] Other: `<one line>`

---

## Module 2 — Integration Kernel

### `trapezoidal(f, a, b, n)` — Implementation Notes

- [ ] Implemented

**Write the formula you used (explicit endpoint weights):**

$$\int_a^b f(x)\,dx \approx h\left(\frac{f_0}{2} + f_1 + \cdots + f_{N-1} + \frac{f_N}{2}\right)$$

**Analytic-Limit Check** ($\int_0^2 x\,dx = 2.0$):

| Field | Value |
|-------|-------|
| Computed value | `<float>` |
| Absolute error $|v - 2.0|$ | `<float>` |
| Passed (`rtol=1e-4`) | `<True/False>` |

**Why is the endpoint weight `0.5` and not `1.0`?** (1 sentence):

`<your answer>`

---

## Module 3 — L2 Norm Contract

### `compute_l2(u_num, u_ref, dx, dy)` — Implementation Notes

- [ ] Implemented

**Formula used:**

$$\|e\|_2 = \sqrt{\sum_{i,j}(u^{\mathrm{num}}_{ij} - u^{\mathrm{exact}}_{ij})^2 \cdot \Delta x\,\Delta y}$$

**Why is the `dx*dy` factor required?** (1–2 sentences):

`<your answer — hint: resolution-independence via Riemann sum>`

### `reference(x, y, t, c)` — Implementation Notes

- [ ] Implemented

**Analytic formula:**

$$u(x,y,t) = \sin(\pi x)\sin(\pi y)\cos(\sqrt{2}\,\pi c\,t)$$

**Verification checklist:**

| Check | Result |
|-------|--------|
| $u(0,y,t) = 0$ (left wall) | `<yes/no>` |
| $u(1,y,t) = 0$ (right wall) | `<yes/no>` |
| $u(x,0,t) = 0$ (bottom wall) | `<yes/no>` |
| $u(x,1,t) = 0$ (top wall) | `<yes/no>` |
| Dispersion relation $\omega^2 = 2\pi^2c^2$ | `<yes/no>` |
| Output shape equals input mesh shape | `<yes/no>` |

---

## Module 4 — Single-Case Measurement

### `single_case_l2_measurement(cfg)` — Implementation Notes

- [ ] Implemented

**Run parameters (from `config.yaml` — do not override):**

| Parameter | Value |
|-----------|-------|
| `nx` | `<int>` |
| `ny` | `<int>` |
| `t_star` | `<float>` |
| Courant number `nu` | `<float>` |
| `c` | `<float>` |

**Single-case L2 error:** `<float>`

**Variable-Isolation Checklist (Module 4):**
- [ ] `t_star` taken directly from `cfg` — not changed between runs
- [ ] `dt = courant * dx / c` — Courant number held fixed
- [ ] Both constraints satisfied → variable isolation is valid

---

## Module 5 — Gate and Status

### JSON Artifact

Paste the full content of `outputs/week02_results.json`:

```json
<paste here>
```

### pytest Evidence

Run: `pytest test_reference_check.py -v`

Paste 6–10 key lines showing pass/fail status:

```text
<paste pytest output here>
```

---

## Interpretation

**Q1.** What does the analytic-limit result confirm about your integration kernel?

`<your answer>`

**Q2.** What does the single-case L2 scalar *not* yet confirm? Why?

`<your answer — hint: no sweep, no slope>`

**Q3.** Why is your final status label justified by the evidence above?

`<your answer>`

**Q4.** If a classmate omits the `dx*dy` factor in `compute_l2`, how will their L2
values behave as resolution increases? (Module 3 Riemann-sum bridge)

`<your answer>`

---

## Week 02.5 Bridge — Resolution Sweep Design

Design your first 4-point convergence sweep for Week 02.5.
Hold `nu` (Courant number) fixed at the value from `config.yaml`.

| Point | $N$ | $\Delta x = 1/N$ | Expected role |
|-------|-----|-----------------|---------------|
| 1 | `<int>` | `<float>` | Coarsest — truncation-dominant regime |
| 2 | `<int>` | `<float>` | |
| 3 | `<int>` | `<float>` | |
| 4 | `<int>` | `<float>` | Finest — approaching round-off regime? |

**Courant number held fixed:** `nu = <float>` (from `config.yaml`)

**One unresolved question for the sweep:**

`<your question>`

---

## Optional References

- Example output JSON: `sample_week02_results.json`
- Example completed report: `report_example.md`


---

## Status

**A — Analytic-Limit Gate**
- `analytic_limit_test()` passed: `<True / False>`
- If False → status is `needs-fix` regardless of L2 magnitude

**B — Single-Case L2**
- `single_case_l2` recorded: `<float>`
- This is evidence, not a pass/fail threshold

**C — Final Label**
- `<reference-checked | needs-fix>`

Failure class (required if `needs-fix`):
  - [ ] indexing / weighting bug (Module 2 trapezoidal)
  - [ ] shape mismatch (Module 3 compute_l2 guard)
  - [ ] `dx*dy` scaling omitted (Module 3 Riemann-sum weight)
  - [ ] reference formula wrong (Module 3 reference function)
  - [ ] other: `<one line>`

---

## Module 2 — Integration Kernel

### Implemented: `trapezoidal(f, a, b, n)`

- [ ] Implemented
- Formula used (write the weights explicitly):

$$\int_a^b f(x)\,dx \approx h\left(\frac{f_0}{2} + f_1 + \cdots + f_{N-1} + \frac{f_N}{2}\right)$$

### Analytic-Limit Check

- Integral: $\int_0^2 x\,dx$
- Expected exact value: `2.0`
- Computed value: `<float>`
- Absolute error `|value - 2.0|`: `<float>`
- Passed: `<True/False>`

---

## Module 3 — L2 Norm Contract

### Implemented: `compute_l2(u_num, u_ref, dx, dy)`

- [ ] Implemented
- Formula:

$$\|e\|_2 = \sqrt{\sum_{i,j}(u^{\mathrm{num}}_{ij} - u^{\mathrm{exact}}_{ij})^2 \cdot \Delta x\,\Delta y}$$

### Why `dx*dy` is required (1–2 sentences):

`<your answer>`

### Implemented: `reference(x, y, t, c)`

- [ ] Implemented
- Analytic formula:

$$u(x,y,t) = \sin(\pi x)\sin(\pi y)\cos(\sqrt{2}\,\pi c\,t)$$

- BC check: $u(0,y,t) = u(1,y,t) = u(x,0,t) = u(x,1,t) = 0$ — verified: `<yes/no>`
- Dispersion relation $\omega^2 = c^2(k_x^2+k_y^2) = 2\pi^2c^2$ — verified: `<yes/no>`

---

## Module 4 — Single-Case Measurement

### Implemented: `single_case_l2_measurement(cfg)`

- [ ] Implemented
- Grid resolution: `nx=<int>`, `ny=<int>`
- Measurement time: `t_star = <float>` (from `config.yaml`, not overridden)
- Courant number: `nu = <float>` (from `config.yaml`, not overridden)
- Single-case L2 error: `<float>`

**Hold Physical Time Fixed — Checklist:**
- [ ] `t_star` taken directly from `cfg` — not changed between runs
- [ ] `dt = courant * dx / c` — Courant number fixed, not `dt` itself
- [ ] Both constraints satisfied → variable isolation is valid for Module 4

---

## Module 5 — Pass Criteria Gate

### Implemented: `analytic_limit_test()`

- [ ] Implemented

### Status Logic

```python
status = "reference-checked" if analytic_limit_passed else "needs-fix"
```

- `analytic_limit_passed`: `<True/False>`
- `analytic_limit_value`: `<float>`
- `single_case_l2`: `<float>`
- Final `status`: `<reference-checked | needs-fix>`

---

## Checkpoint Artifacts

1. JSON artifact path: `outputs/week02_results.json`
2. Pytest command used: `pytest test_reference_check.py -v`
3. Pytest evidence snippet (copy 4–8 key pass/fail lines):

```text
<paste pytest output here>
```

---

## Interpretation (answer each in 1–2 sentences)

**Q1.** What does the analytic-limit result confirm about your integration kernel?

`<your answer>`

**Q2.** What does the single-case L2 scalar *not* yet confirm?

`<your answer — hint: no sweep, no slope>`

**Q3.** Why is your final status label justified by the evidence above?

`<your answer>`

**Q4.** If a classmate omits the `dx*dy` factor, how will their L2 values behave as
resolution increases? (Module 3 Riemann-sum bridge)

`<your answer>`

---

## Week 02.5 Bridge Question

Design your first 4-point resolution sweep for Week 02.5:

| Point | $N$ | $\Delta x$ | Expected role |
|-------|-----|-----------|---------------|
| 1 | `<int>` | `<float>` | coarsest — reveal truncation-dominated regime |
| 2 | `<int>` | `<float>` | |
| 3 | `<int>` | `<float>` | |
| 4 | `<int>` | `<float>` | finest |

Courant number you will hold fixed: `nu = <float>` (from `config.yaml`)

One unresolved question for the sweep:

`<your question>`

---

## Optional References

- Example output JSON: `sample_week02_results.json`
- Example completed report: `report_example.md`
