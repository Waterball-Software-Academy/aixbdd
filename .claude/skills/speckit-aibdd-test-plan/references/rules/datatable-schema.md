# R15 — Datatable Schema 不得 key-value-bag（Phase 5 invariant）

> 純 declarative reference。Phase 5 Subagent semantic validation 用此規則檢驗。
>
> 來源：原 SKILL.md `## Step 4 — R15`。NEW per `aibdd-core::physical-first-principle.md` MR-6。

## §1 規則本體

flow scenario 內任何 datatable（不限 mock-setup；含 verify-state assertion 類），其 header row **不得**為 meta-naming 模式（`欄位 / 值 / field / value / key / label / text / name / 名稱 / type / 類型` 等元描述詞當 column header）。

Header **必須**為 ≥1 個 domain field name；單 column N row 退化形（`| 評審 |` + 多 row）合法。

## §2 合格範例

```
| 評審 | 原因           | 通過數 | 失敗數 | 待處理數 |
| pass | intent matches | 1      | 0      | 0        |
```

## §3 違反範例

```
| 欄位      | 值             |
| 評審      | pass           |
| 原因      | intent matches |
```

## §4 違反處理

違反 → `R15_DATATABLE_KEY_VALUE_BAG`（hard-fail）；指示回 Phase 4 重寫；若 boundary `dsl.md` 對應 entry datatable schema 本身違規 → 回 `/speckit.aibdd.bdd-analyze` Phase 5 補 `DSL_DATATABLE_NOT_KEY_VALUE_BAG`。
