# `/aibdd-tasks` Role and Contract

## Role

`/aibdd-tasks` 是 plan 完成後的 downstream planning skill，把一個 AIBDD plan package 轉成結構化 `tasks.md`。

它不重寫架構，而是消費：

- 當前 plan package 的 `plan.md` / `research.md`
- `${IMPACT_MATRIX_YML}` 匯出的 impacted feature scope
- `implementation/internal-structure.class.mmd` 的 topology
- boundary truth 與 impacted feature texts

再編排成：

- plan-level implementation topology
- feature-driven TDD phase order
- 固定 RED / GREEN / Refactor execution template

## Required Inputs

- `.aibdd/arguments.yml`
- current plan package `plan.md`
- current plan package `research.md` when present
- current plan package `reports/impact-matrix.yml`
- current plan package `implementation/internal-structure.class.mmd`
- impacted `.feature` files referenced by impact matrix
- `${BOUNDARY_MAP_FILE}`

## Outputs

- `${CURRENT_PLAN_PACKAGE}/tasks.md`

## Non-Goals

- 不取代 `/aibdd-plan`
- 不寫 contracts、DSL、DBML、sequence diagrams
- 不直接執行 `/aibdd-red-execute`、`/aibdd-green-execute`、`/aibdd-refactor-execute`
- 不寫 product code、tests、step definitions、runtime fixtures

## Completion Contract

skill 完成時，`tasks.md` 必須提供穩定 markdown task list：

- 開頭有 `Infra setup`
- 每個 impacted feature 一個 TDD phase
- 結尾有 `Integration`
- 每個 feature phase 都有 `RED` / `GREEN` / `Refactor`
- GREEN waves 是 feature-specific，不是整包 topology 複製貼上
