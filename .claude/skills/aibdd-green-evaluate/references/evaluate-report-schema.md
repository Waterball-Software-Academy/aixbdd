# Green Evaluate Report Schema

`aibdd-green-evaluate` emits a machine-readable report.

## Required Fields

- `kind`: fixed value `green_evaluation_report`
- `verdict`: `PASS` or `FAIL`
- `artifacts`: object with `final_full_suite_report_path` and optional
  `acceptance_runner_runtime_ref`
- `findings`: ordered list of all-pass violations
- `veto_reasons`: ordered list derived from findings
- `refactor_allowed`: boolean, true only when `verdict == PASS`

## Finding Shape

Each finding contains:

- `id`: stable finding id
- `severity`: `veto`
- `evidence_path`: final full-suite report path
- `evidence_summary`: normalized report evidence

## Verdict Rules

- Any failure count above zero makes `verdict = FAIL`.
- Any error count above zero makes `verdict = FAIL`.
- Any improper skip, xfail, deselect, or collection omission makes
  `verdict = FAIL`.
- Green evaluation has no Type B layer.
