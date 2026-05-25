# Red Evaluate Input Contract

`aibdd-red-evaluate` evaluates a completed Red Worker run. It does not execute
Red and does not inspect `aibdd-red-execute` source files.

## Accepted Payload

The caller supplies either `red_handoff` with all fields below embedded or
explicit artifact pointers:

- `target_feature_files`: exact target feature-file set evaluated by Red.
- `final_test_report_path`: runner-native final test report path.
- `feature_archive_runtime_root`: resolved `${FEATURE_ARCHIVE_RUNTIME_REF}`
  runtime feature root, including copy/include output.
- `step_definitions_runtime_root`: resolved `${STEP_DEFINITIONS_RUNTIME_REF}`
  step definition root used by the runner step glob.
- `step_defs_touched`: step definition files generated or updated by Red.
- `acceptance_runner_runtime_ref`: resolved `${ACCEPTANCE_RUNNER_RUNTIME_REF}`
  command/report configuration when available.

When a `resolved ${...}` value above is absent from the payload, it is bound by
`resolve_args.py` from `.aibdd/arguments.yml`. The `red_handoff` runtime
snapshot takes precedence over a re-resolved value, so the evaluator checks the
paths Red actually used rather than paths that may have drifted since.

## Evidence Boundary

The evaluator may read only:

- runner-native test report
- runtime-visible feature files
- runtime-visible step definition files
- explicit artifact pointers from the Worker run

The evaluator must not rely on DSL indexes, StepPlan IR, preset registries, or
skill source lint as evidence that this Red run is legal.
