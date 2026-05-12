# Execute Config Contract

This reference defines the shared input and runtime configuration contract for
AIBDD execute skills.

## Target

- External target granularity is `target_feature_files`, a non-empty list of
  feature file paths.
- Scenario is an internal iteration unit discovered from each target feature
  file, not the public execute input boundary.
- A target set mismatch against upstream handoff is a hard STOP condition.

## Arguments Path

- `arguments_path` may be supplied by the caller.
- When omitted, the default is `${AIBDD_CONFIG_DIR}/arguments.yml`.
- If neither path exists, the execute skill must STOP.
- `specs/arguments.yml` is not a fallback.

## Core References

- `GHERKIN_*_REF`, `FILENAME_*_REF`, `DSL_OUTPUT_CONTRACT_REF`, and
  `BACKEND_PRESET_CONTRACT_REF` are file paths.
- The loader reads those paths directly.
- The loader must not infer rules from key names, basenames, or conventions.

## Boundary Preset Assets

- `L4.preset.name` resolves directly to
  `.claude/skills/aibdd-core/assets/boundaries/<preset-name>/`.
- `web-backend` is not resolved through a `backend` alias.
- `/aibdd-plan/assets/boundaries` is not a runtime source for execute skills.
- `handler-routing.yml` is the source for sentence part, Gherkin keyword,
  handler, and required source kinds.
- For `web-backend`, `sentence_part` must equal `handler`.

## Project-Owned Runtime References

These behaviors come only from project-owned BDD stack references:

- acceptance runner command, dry-run command, report output, and visibility check
- runtime feature glob and step definition glob
- shared step glob and duplicate registration policy
- fixture/helper extension points
- feature archive/copy/include mechanism
- Red Pre-Red gate prose contract (`RED_PREHANDLING_HOOK_REF`)

Paths in `arguments.yml` values resolve relative to the **backend root**: the directory that contains `.aibdd/` (the parent directory of the `.aibdd` folder holding `arguments.yml`).

The required source references are `ACCEPTANCE_RUNNER_RUNTIME_REF`,
`STEP_DEFINITIONS_RUNTIME_REF`, `FIXTURES_RUNTIME_REF`,
`FEATURE_ARCHIVE_RUNTIME_REF`, and `RED_PREHANDLING_HOOK_REF`.

## Drift And Routing

- Green and Refactor compare current runtime references with upstream runtime
  snapshots before acting.
- Any drift that changes visibility or step resolution for the same target set
  is a STOP condition.
- DSL, preset, binding, or source reference drift routes to `/aibdd-plan` or
  `/aibdd-spec-by-example-analyze`.
- Runtime command, glob, archive, fixture, or BDD stack instruction drift routes
  to project-owned BDD stack configuration.
