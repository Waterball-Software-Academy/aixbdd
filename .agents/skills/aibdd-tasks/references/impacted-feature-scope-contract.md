# Impacted Feature Scope Contract

## SSOT

`/aibdd-tasks` 的 impacted feature membership 以 `${IMPACT_MATRIX_YML}` 為機讀 SSOT。

查詢條件：matrix 中所有 `.feature` spec。

以 `read --spec-path '\.feature$'` 取回的 impacts，收集其 `impacts[].specs[].path`，即為本輪 task feature membership；不再有 `change_type` 軸。

## Path Shape

每筆 `specs[].path` 為 `${TRUTH_BOUNDARY_ROOT}` 相對路徑，例如 `packages/01-房間/features/開房或加入遊戲房.feature`。

tasks scripts 與 checker 一律以這個相對路徑 shape 比對 feature phase。

## Ordering

matrix 只決定 membership，不決定 phase order。

feature phase order 由 reasoning 依 `plan.md`、`research.md`、`boundary-map.yml` 與 feature 內容語意排序；排序結果以 `--feature-paths` 傳給 scaffold 與 checker。

## Human Summary

`plan.md` 若保留 `## Impacted Feature Files`，只作 derived human summary，不作機讀 membership 來源。
