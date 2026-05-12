# Red Evaluate Report Schema

`aibdd-red-evaluate` emits a machine-readable report.

## Required Fields

- `kind`: fixed value `red_evaluation_report`
- `verdict`: `PASS` or `FAIL`
- `target_feature_files`: evaluated target set
- `artifacts`: object with `final_test_report_path`, `feature_archive_runtime_root`,
  `step_definitions_runtime_root`, and `step_defs_touched`
- `type_a_findings`: ordered list of scripted hard-gate findings
- `type_b_findings`: ordered list of hollow-red semantic findings
- `veto_reasons`: ordered list derived from all failing hard gates
- `green_allowed`: boolean, true only when `verdict == PASS`

## Finding Shape

Each finding contains:

- `id`: stable finding id
- `severity`: `veto`
- `evidence_path`: report, feature, or step definition path
- `evidence_summary`: concise evidence excerpt or normalized message
- `target`: feature, scenario, step, or step definition target

## Verdict Rules

- Any Type A finding makes `verdict = FAIL`.
- Any Type B hollow-red finding makes `verdict = FAIL`.
- Type B is never advisory for Red evaluation because hollow red contaminates
  Green with a failing test that does not prove a product behavior gap.
