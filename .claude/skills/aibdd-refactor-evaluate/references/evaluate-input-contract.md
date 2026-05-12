# Refactor Evaluate Input Contract

`aibdd-refactor-evaluate` evaluates only the evidence needed after a completed
Refactor Worker run: strict dev constitution conformance and final full suite
all pass.

## Accepted Payload

The caller supplies either `refactor_handoff` with all fields below embedded or
explicit artifact pointers:

- `final_full_suite_report_path`: final runner-native full acceptance suite
  report path.
- `dev_constitution_path`: resolved `${DEV_CONSTITUTION_PATH}`.
- `product_codebase_root`: product codebase root for constitution checking.
- `changed_files_scope`: files modified by Refactor, if available.
- `acceptance_runner_runtime_ref`: resolved `${ACCEPTANCE_RUNNER_RUNTIME_REF}`
  command/report configuration when available.

## Evidence Boundary

The evaluator may read only the full-suite report, the resolved dev
constitution, and the product code scope required to check that constitution.
It must not replay refactor moves, inspect ASK gates, rerun Worker loop logic,
or validate handoff schema internals.
