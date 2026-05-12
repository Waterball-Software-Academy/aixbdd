# Execute Config Contract

This reference defines shared execute configuration for AIBDD Refactor.

## Target

- Public input is `target_feature_files`, a non-empty feature file list.
- Refactor protection and improvement scope are bounded by that target set.
- Scenario is an internal unit for runner evidence and scope narrowing.

## Arguments Path

- `arguments_path` may be supplied by the caller.
- The default path is `${AIBDD_CONFIG_DIR}/arguments.yml`.
- Missing caller path and missing default path is a STOP condition.
- `specs/arguments.yml` is not a fallback.

## Required Truth

Refactor loads:

- `DEV_CONSTITUTION_PATH`
- `BDD_CONSTITUTION_PATH`
- `ACCEPTANCE_RUNNER_RUNTIME_REF`
- `STEP_DEFINITIONS_RUNTIME_REF`
- `FIXTURES_RUNTIME_REF`
- `FEATURE_ARCHIVE_RUNTIME_REF`
- `RED_PREHANDLING_HOOK_REF`

Refactor does not infer runner commands, globs, fixture contracts, or archive
behavior from project layout.

## Drift

Refactor compares the Green handoff runtime snapshot with current runtime
references before making any move. Drift that changes the same target set's
test surface is a STOP condition.
