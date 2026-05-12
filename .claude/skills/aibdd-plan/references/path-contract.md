# Path Contract

## Source of Truth

All paths are resolved from `.aibdd/arguments.yml`. The skill must not infer a boundary root from a hard-coded folder name when the argument file provides a key.

## Required Argument Keys

- `SPECS_ROOT_DIR`
- `PLAN_SPEC`
- `PLAN_REPORTS_DIR`
- `TRUTH_BOUNDARY_ROOT`
- `TRUTH_BOUNDARY_PACKAGES_DIR`
- `TRUTH_FUNCTION_PACKAGE`
- `BOUNDARY_PACKAGE_DSL`
- `BOUNDARY_SHARED_DSL`
- `TEST_STRATEGY_FILE`
- `DSL_KEY_LOCALE` (optional; BCP 47 values `zh-hant` / `zh-hans` / `en-us` / `ja-jp` / `ko-kr`, or `prefer_spec_language`)

## Derived Paths

- `CURRENT_PLAN_PACKAGE`: parent directory of `PLAN_SPEC`
- `PLAN_MD`: `${CURRENT_PLAN_PACKAGE}/plan.md`
- `PLAN_RESEARCH`: `${CURRENT_PLAN_PACKAGE}/research.md`
- `PLAN_IMPLEMENTATION_DIR`: `${CURRENT_PLAN_PACKAGE}/implementation`
- `PLAN_SEQUENCE_DIR`: `${PLAN_IMPLEMENTATION_DIR}/sequences` — each sequence file MUST be `<scenario>.<category>.sequence.mmd` (`<category>` ∈ `happy | alt | err`; `<scenario>` may be localized natural-language slug; see `aibdd-core::diagram-file-naming.md`)
- `PLAN_INTERNAL_STRUCTURE`: `${PLAN_IMPLEMENTATION_DIR}/internal-structure.class.mmd`
- `CONTRACTS_DIR`: `${TRUTH_BOUNDARY_ROOT}/contracts`
- `DATA_DIR`: `${TRUTH_BOUNDARY_ROOT}/data`
- `ACTIVITIES_DIR`: `${TRUTH_FUNCTION_PACKAGE}/activities`
- `FEATURE_SPECS_DIR`: `${TRUTH_FUNCTION_PACKAGE}/features`

## No-Overload Rule

Plan package paths and truth package paths are disjoint. A path under `CURRENT_PLAN_PACKAGE` may contain analysis, reports, and implementation planning. A path under `TRUTH_BOUNDARY_ROOT` or `TRUTH_FUNCTION_PACKAGE` may contain accepted truth.

## DSL registry paths (`dsl.yml`)

- **`BOUNDARY_PACKAGE_DSL`** and **`BOUNDARY_SHARED_DSL`** must resolve to **`*.yml`** files (YAML DSL registry). **`dsl.md` is rejected** by `check_plan_phase.py` and `check_dsl_entries.py`.
- Contract operation rows require **exact coverage** (required `request.params` + `request.body.fields` minus transport headers per gate policy); see [`dsl-output-contract.md`](dsl-output-contract.md) + `scripts/python/check_dsl_entries.py`.

## Phase 6 — DSL key locale gate

Before synthesizing entries, resolve `$$dsl_key_locale` (`prefer_spec_language` or one configured BCP 47 language tag).

Resolution order:

1. If `DSL_KEY_LOCALE` exists in `arguments.yml`, use it deterministically.
2. Else derive from filename script profile per Phase 6 in `SKILL.md`.
3. Ask the user only when no deterministic source is available and the current run is not a fixture/test execution.
