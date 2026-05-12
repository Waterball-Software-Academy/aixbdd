# Execute Handoff Schemas

Runner evidence and skill mapping evidence remain separate.

## Red Handoff Expected By Green

Green requires a Red handoff with:

- `status: completed`
- exact `target_feature_files`
- `behavior_test_report` with runner-native failure evidence
- `scenario_reports` whose failures are legal red
- `runtime_refs_snapshot`
- `dsl_mapping` for every Scenario step
- `step_defs_touched`
- `stop_reason: none`

The runner-native `behavior_test_report` is not treated as a DSL-aware report.
All DSL and preset checks use the handoff mapping synthesized by Red.

## Green Handoff

Green emits:

- `status`: `completed`, `failed`, or `stop`
- `target_feature_files`: exact input target set
- `red_handoff_ref`: reference or embedded red summary
- `behavior_test_report`: final runner-native report
- `runtime_refs_snapshot`: current runtime reference paths and fingerprints
- `product_files_modified`: product-only changes
- `loop_history`: first failure signatures and actions per iteration
- `oscillation_trace`: present when oscillation is detected
- `stop_reason`: `none`, `oscillation_detected`, `architecture_veto`,
  `loop_budget_exceeded`, `red_invalid`, `handoff_drift`, or `test_bug`

## Failure Signature

Green records stable first-failure signatures with:

- `feature_file`
- `scenario_name`
- failing step keyword and prose when available
- normalized first failure type
- normalized message fingerprint, not the full volatile stack trace

These signatures support oscillation detection and loop reporting.
