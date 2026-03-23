# Week 02 Report (Example)

## Status

- Final label: `reference-checked`
- Failure class (required if `needs-fix`): not applicable

## Implemented Functions

- [x] `reference(...)`
- [x] `compute_l2(...)`
- [x] `trapezoidal(...)`
- [x] `analytic_limit_test()`
- [x] `single_case_l2_measurement(cfg)`

## Numeric Evidence

- Analytic limit passed: `True`
- Analytic limit value: `2.0000000000`
- Analytic absolute error `|value - 2.0|`: `0.0`
- Single-case L2 at `t_star`: `1.42e-03`

## Checkpoint Artifacts

1. JSON artifact path: `outputs/week02_results.json`
2. Pytest command used: `pytest test_reference_check.py -v`
3. Pytest evidence snippet (2-4 lines):

```text
test_reference_check.py::test_single_case_measurement_is_finite PASSED
test_reference_check.py::test_compute_l2_rejects_shape_mismatch PASSED
```

## Interpretation (3-5 lines)

- The analytic-limit check passed exactly, so the integration kernel is not showing an obvious weighting/indexing defect.
- A synchronized L2 scalar was recorded at fixed `t_star`, which is enough for Week 02 status labeling.
- This does not prove convergence order yet because there is no multi-resolution sweep in this week.
- `reference-checked` is justified because pass/fail gating for this week is tied to the analytic-limit condition.

## Week 02.5 Bridge Question

- If the first 4-point sweep has one outlier, what objective criterion should exclude that point before slope fitting?

## Optional References

- Example output JSON: `sample_week02_results.json`
- Example report: `report_example.md`
