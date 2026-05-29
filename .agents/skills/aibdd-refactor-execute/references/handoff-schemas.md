# Execute Handoff Schemas

## Green Handoff Expected By Refactor

Refactor requires a Green handoff with:

- `status: completed`
- exact `target_feature_files`
- final `behavior_test_report` whose target set passed
- `runtime_refs_snapshot`
- product files modified by Green
- loop history and stop reason `none`

If the handoff does not prove the target set is green, Refactor stops.

## Refactor Handoff

Refactor emits:

- `status`: `completed`, `skipped`, `failed`, or `stop`
- `target_feature_files`
- `green_handoff_ref`: reference or embedded summary
- `behavior_test_report`: final runner-native report
- `runtime_refs_snapshot`
- `refactor_moves_applied`
- `refactor_moves_reverted`
- `files_modified`
- `scope_history`
- `stop_reason`

The report distinguishes applied moves from reverted risky moves.
