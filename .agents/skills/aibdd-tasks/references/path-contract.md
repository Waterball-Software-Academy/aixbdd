# Path Contract

## Required arguments.yml keys

`/aibdd-tasks` 透過 `aibdd-core` resolver 綁定下列鍵：

- `CURRENT_PLAN_PACKAGE`
- `PLAN_MD`
- `PLAN_REPORTS_DIR`
- `IMPACT_MATRIX_YML`
- `PLAN_IMPLEMENTATION_DIR`
- `PLAN_INTERNAL_STRUCTURE`
- `TRUTH_BOUNDARY_ROOT`
- `TRUTH_BOUNDARY_PACKAGES_DIR`
- `BOUNDARY_MAP_FILE`
- `AIBDD_ARGUMENTS_PATH`
- `PROJECT_SPEC_LANGUAGE` when present

`TRUTH_FUNCTION_PACKAGE` / `FEATURE_SPECS_DIR` 仍可能存在於 arguments.yml，但 tasks scope 不再綁死單一 function package。

## Derived Paths

- `plan.md` = `${PLAN_MD}`
- `research.md` = `${CURRENT_PLAN_PACKAGE}/research.md`
- `internal-structure.class.mmd` = `${PLAN_INTERNAL_STRUCTURE}`
- `tasks.md` = `${CURRENT_PLAN_PACKAGE}/tasks.md`
- `impact-matrix.yml` = `${IMPACT_MATRIX_YML}`
- `function-packaging.md` = `${PLAN_REPORTS_DIR}/function-packaging.md`
- `boundary-map.yml` = `${BOUNDARY_MAP_FILE}`

## Feature Scope Source

1. membership：`${IMPACT_MATRIX_YML}` query（`.feature` + `{add, update}`）
2. order：reasoning 產出的 ordered feature path list，經 `--feature-paths` 傳給 scaffold / checker

## Plan Package Binding

`CURRENT_PLAN_PACKAGE` 可能是 slot。scripts 接受：

1. 已 concrete resolve 的 arguments.yml
2. `--plan-package <path>` CLI 覆寫
3. `AIBDD_PLAN_PACKAGE` 環境變數覆寫

## Language Source

`tasks.md` 優先使用 `.aibdd/arguments.yml` 的 `PROJECT_SPEC_LANGUAGE`。
