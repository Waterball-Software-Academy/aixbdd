# Path Contract

## Required arguments.yml keys

`/aibdd-tasks` expects these keys to resolve correctly:

- `CURRENT_PLAN_PACKAGE`
- `PLAN_MD`
- `PLAN_IMPLEMENTATION_DIR`
- `PLAN_INTERNAL_STRUCTURE`
- `TRUTH_BOUNDARY_ROOT`
- `TRUTH_FUNCTION_PACKAGE`
- `FEATURE_SPECS_DIR`
- `AIBDD_ARGUMENTS_PATH`
- `PROJECT_SPEC_LANGUAGE` when present

## Derived Paths

- `plan.md` = `${PLAN_MD}`
- `research.md` = `${CURRENT_PLAN_PACKAGE}/research.md`
- `internal-structure.class.mmd` = `${PLAN_INTERNAL_STRUCTURE}`
- `tasks.md` = `${CURRENT_PLAN_PACKAGE}/tasks.md`
- `boundary-map.yml` = `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`

## Feature Scope Source Order

1. Primary: `plan.md` section `## Impacted Feature Files`
2. Fallback: `${FEATURE_SPECS_DIR}` scan + numbering + semantic filtering

## Language Source

`tasks.md` should prefer the project language declared in `.aibdd/arguments.yml`:

- `PROJECT_SPEC_LANGUAGE` when present
- otherwise repository-local default wording may be used
