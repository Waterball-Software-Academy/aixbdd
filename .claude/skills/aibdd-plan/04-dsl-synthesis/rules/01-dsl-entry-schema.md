# DSL entry schema

本檔之前定義的 4 層巢狀 schema（`L1` / `L2` / `L3` / `L4`，含 `surface_id` / `surface_kind` / `callable_via` / `preset.{name,handler,variant}` / `source_refs.{contract,data,boundary,test_strategy}` / `default_bindings` / `assertion_bindings` 等）**已廢止**。

新 schema 為扁平單層，欄位為 `format` / `name` / `handler` / `target_part_path` / `param_bindings` / `datatable_bindings`，定義與完整 7-handler 範例見：

- 規格定義：`research/aibdd-plan-dsl合成步驟超級 harness 計劃/spec.md` §1「把 dsl.yml 的格式改得更 concise」
- Target URI Schemes 表（合法 binding target 5 種 scheme）：同檔 §1 末段
- HARNESS skeleton ↔ SEMANTIC filled 兩態對照：同檔 §3 Solution Summary as Flow 步驟 1.2 後

stage 4 SOP 直接呼叫 `dsl_cli`（見 [SOP.md](../SOP.md)）；不再以 per-rule 迭代產生 entry。

## 舊→新欄位對照（速查）

| 舊欄 | 新處置 |
|---|---|
| `L1.{given,when,then}` | 折到單一 `format`（actor-operation-object 句型） |
| `L2.{actor,context}` | 不獨立保留；actor 在 `format` 業務句中體現 |
| `L3.part` | 直接由 `handler` 標識（同名映射） |
| `L4.preset.{name,handler,variant}` | `handler` 一欄；variant 由 boundary 1:1 推導 |
| `L4.surface_id` / `surface_kind` / `callable_via` | 由 `target_part_path` + `handler` 結合推導 |
| `L4.source_refs.{contract,data,boundary,test_strategy}` | 收斂為單一 `target_part_path`（Spec anchor） |
| `L4.param_bindings.{key}.target` | 同 — `param_bindings[key].target` |
| `L4.default_bindings[]` | 折回 `datatable_bindings[key].default_value`（required: false 時可選提供） |
| `L4.assertion_bindings` | 移除；assertion 語意由 `handler` 自身指導 red-execute |
