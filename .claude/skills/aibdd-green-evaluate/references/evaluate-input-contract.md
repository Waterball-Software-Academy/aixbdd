# Green Evaluate Input Contract

`aibdd-green-evaluate` evaluates only the final full acceptance suite report
from a completed Green Worker run.

## Accepted Payload

The caller supplies either `green_handoff` with all fields below embedded or
explicit artifact pointers:

- `final_full_suite_report_path`: final runner-native full acceptance suite
  report path.
- `acceptance_runner_runtime_ref`: resolved `${ACCEPTANCE_RUNNER_RUNTIME_REF}`
  command/report configuration when available.

## Evidence Boundary

The evaluator may read only the final full-suite report and the explicit runner
configuration pointer. It must not inspect Green patches, drift records,
handoff schema internals, loop history, architecture decisions, or product code.

## Full Suite Requirement

The report must represent the full acceptance suite. A target-only report is not
sufficient evidence for Green evaluation.
