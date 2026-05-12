# Execute Handoff Schemas

This reference defines machine-readable report shapes exchanged by execute
skills. Runner-native behavior evidence and skill-synthesized mapping evidence
remain separate concepts.

## Behavior Test Report

`behavior_test_report` contains only information visible to the acceptance
runner:

- `kind`: fixed value `behavior_test_report`
- `runner`: runner name from runtime configuration
- `target_feature_files`: feature files exercised in this run
- `scenario_reports`: feature file, scenario name, outcome, step statuses
- `first_failure`: error type, normalized message, and runner location
- `report_path`: optional runner output path when configured

It must not contain `dsl_mapping`, DSL entry ids, preset tuples, or source refs.

## Red Handoff

`red_handoff` is synthesized by `aibdd-red-execute` after preflight, archive,
StepPlan compilation, rendering, visibility checks, and runner execution.

Required fields:

- `status`: `completed`, `failed`, or `stop`
- `phase`: caller phase when supplied
- `task_id`: caller task id when supplied
- `target_feature_files`: exact input target set
- `behavior_test_report`: runner-native report object
- `scenario_reports`: per Scenario red classification
- `red_type`: `value_difference`, `expected_exception`, `mixed`, or `n/a`
- `runtime_refs_snapshot`: resolved paths and content fingerprints for `ACCEPTANCE_RUNNER_RUNTIME_REF`, `STEP_DEFINITIONS_RUNTIME_REF`, `FIXTURES_RUNTIME_REF`, `FEATURE_ARCHIVE_RUNTIME_REF`, and `RED_PREHANDLING_HOOK_REF`
- `step_defs_touched`: generated or updated step definition files
- `dsl_mapping`: one entry per matched Scenario step
- `loop_iterations`: count of legal-red attempts
- `stop_reason`: `none` or a routeable stop reason

Each `dsl_mapping` entry records step prose, DSL entry id, matched L1, step-def
path, preset tuple, surface kind/id, source refs, binding keys, and failure
classification.

## Green Handoff

`green_handoff` is synthesized by `aibdd-green-execute` after the target set is
green.

Required fields:

- `status`: `completed`, `failed`, or `stop`
- `target_feature_files`: exact input target set
- `red_handoff_ref`: reference or embedded summary of the driving red handoff
- `behavior_test_report`: final runner-native report
- `runtime_refs_snapshot`: current runtime reference paths and fingerprints
- `product_files_modified`: product files changed by Green
- `loop_history`: ordered list of first failure signatures and actions
- `stop_reason`: `none`, `oscillation_detected`, `architecture_veto`,
  `loop_budget_exceeded`, `test_surface_drift`, or another routeable reason

## Refactor Handoff

`refactor_handoff` is synthesized by `aibdd-refactor-execute`.

Required fields:

- `status`: `completed`, `skipped`, `failed`, or `stop`
- `target_feature_files`: exact input target set
- `green_handoff_ref`: reference or embedded summary of the driving green handoff
- `behavior_test_report`: final runner-native report
- `runtime_refs_snapshot`: current runtime reference paths and fingerprints
- `refactor_moves_applied`: ordered accepted move list
- `refactor_moves_reverted`: rejected or risky move list
- `files_modified`: final modified file list
- `scope_history`: scope shrink events, if any
- `stop_reason`: `none` or a routeable stop reason
