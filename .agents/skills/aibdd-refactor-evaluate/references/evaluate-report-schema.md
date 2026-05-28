# Refactor Evaluate Report Schema

`aibdd-refactor-evaluate` emits a machine-readable report.

## Required Fields

- `kind`: fixed value `refactor_evaluation_report`
- `verdict`: `PASS` or `FAIL`
- `artifacts`: object with `final_full_suite_report_path`,
  `dev_constitution_path`, and `code_scope`
- `constitution_findings`: ordered list of dev constitution violations
- `test_findings`: ordered list of all-pass violations
- `veto_reasons`: ordered list derived from all findings
- `refactor_accepted`: boolean, true only when `verdict == PASS`

## Finding Shape

Each finding contains:

- `id`: stable finding id
- `severity`: `veto`
- `evidence_path`: constitution, code, or full-suite report path
- `evidence_summary`: concise evidence excerpt or normalized report message
- `target`: constitution clause, code file, or report section

## Verdict Rules

- Any dev constitution violation makes `verdict = FAIL`.
- Any failure count above zero makes `verdict = FAIL`.
- Any error count above zero makes `verdict = FAIL`.
- Any improper skip, xfail, deselect, or collection omission makes
  `verdict = FAIL`.
- Refactor evaluation has no Type B layer.
