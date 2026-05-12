# Execute Config Contract

This reference defines shared execute configuration for AIBDD Green.

## Target

- Public input is `target_feature_files`, a non-empty feature file list.
- Green may iterate over Scenarios inside those files, but must not accept a
  Scenario-only target as the external boundary.
- The target set must exactly match the driving Red handoff.

## Arguments Path

- `arguments_path` may be supplied by the caller.
- The default path is `${AIBDD_CONFIG_DIR}/arguments.yml`.
- Missing caller path and missing default path is a STOP condition.
- `specs/arguments.yml` is not a fallback.

## Core And Runtime References

- Core reference keys ending in `_REF` are paths and must be read directly.
- Boundary preset assets resolve through
  `.claude/skills/aibdd-core/assets/boundaries/<preset-name>/`.
- `web-backend` is never resolved through a `backend` alias.
- Runtime commands, globs, report output, fixture behavior, and archive behavior
  come only from project-owned BDD stack runtime refs.

## Drift

Green compares the Red handoff with current DSL, core preset assets, and runtime
visibility before editing product code.

Any drift in DSL entry id, matched L1, preset tuple, step-def path, source refs,
runtime feature visibility, or step glob visibility is a STOP condition.

DSL and preset drift routes to planning or BDD analysis. Runtime command, glob,
archive, fixture, and visibility drift routes to project-owned BDD stack config.
