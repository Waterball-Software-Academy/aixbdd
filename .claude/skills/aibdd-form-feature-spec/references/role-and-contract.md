# 角色 + 入口契約

> 純 declarative reference。Phase 1 LOAD 取入口 schema 與角色定位。
>
> 來源：原 SKILL.md `## §1 角色` + `## §2 入口契約`。

## §1 角色定位

Formulation skill。綁定 DSL = Gherkin（`.feature`）。被多個 Planner DELEGATE：

（`${FEATURE_SPECS_DIR}` 由 kickoff `arguments.yml` + `boundary.yml` 展開；見 `aibdd-core::spec-package-paths.md`）
- `speckit-aibdd-bdd-analyze`：example 回填模式（填入 Examples + 移除 `@ignore`），覆寫至原路徑

## §2 入口契約 — 推理包 schema

| 項目 | 內容 |
|---|---|
| M/D/C 變更集 | Feature / Rule / Example 的增刪改 |
| Axis 單位對應 | rule → Feature.Rule 的具體對應 |
| CiC 記號清單 | 便條紙（GAP / ASM / BDY / CON）+ 錨點 |
| 退出狀態 | Reason 步是否完整通過 |
| `target_path` | Planner 指定的輸出路徑（**必須**為 kickoff 展開後之 `${FEATURE_SPECS_DIR}` 底下的絕對或專案相對路徑；允許子目錄 `<sub-domain>/`）|
| `mode` | `rule-only`（Feature + Rule 層，無 Background、無 Examples）/ `example-fill`（填入 Examples）|

## §3 缺項處理

推理包不完整或 `target_path` 未指定 → Phase 1 RETURN「推理包不完整」回退呼叫 Planner 補齊。
