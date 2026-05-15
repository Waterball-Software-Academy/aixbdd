# SOP

輸入 `$rule_strategy`（02 產出）、`$indexed_truth`（01 產出）。本 sub-SOP 不寫檔；產出 `$rule_test_data`（每條 rule 對應 precondition setup + given/when/then 具體值 + binding trace）交予 04。

1. **THINK：逐條 strategy 枚舉具體值** — 規則見 `rules/data-enumeration-granularity.md`、`rules/enumeration-禁止自生.md`。
   - LOOP per `$strategy` in `$rule_strategy.strategies[]`:
     1.1 IF `$strategy.cic` 已阻塞（02 已標）→ 攜帶 CiC 帶入 `$rule_test_data.data_rows[]`；CONTINUE。
     1.2 `$dsl_entries` = MATCH `$strategy.feature_path` against `$indexed_truth.dsl_entries`。
     1.3 IF `$dsl_entries` 為空 → 累積 CiC(GAP) `"feature has no plan DSL entry"`；CONTINUE。
     1.4 `$precondition_setup` = DERIVE 該 rule 在 When step 之前需要的既存 entity／state（取自 rule body 提及之 entity name、operation 之 required input、DBML 之 FK／NOT-NULL、external-stub edge）。
     1.5 ASSERT 每個 `$precondition_setup[]` 之 setup 來源能對應到 matching Given-capable DSL entry／shared DSL setup entry／test-strategy seed／CiC(GAP)；**不准**自生未列於 DSL／seed 之 Given。
     1.6 `$given_value_sets` = DERIVE Given 具體值（僅從已 sourced `$precondition_setup`；任一 setup 為 cic_gap 則該 Given 不可執行，僅作 internal note）。
     1.7 `$when_value_sets` = DERIVE When 具體值（僅從 `L4.param_bindings`／`datatable_bindings`／`default_bindings`）。
     1.8 `$then_expect_sets` = DERIVE Then 具體期望（僅從 `L4.assertion_bindings`／OpenAPI response field／DBML field）。
     1.9 `$binding_trace` = DERIVE 每個 setup／value／expectation 對應之 `(dsl_entry_id, binding_key, binding_kind, target)`。

2. **THINK：依 technique 補各維度具體值**
   - LOOP per `$rule_data`:
     2.1 `EP ∈ techniques` → 從 DSL binding 名稱 + OpenAPI required field 推 valid／invalid 等價類代表值；invalid 列對應 `invalid_input` 或 `error_handling`。
     2.2 `BVA ∈ techniques` → 從 OpenAPI `minimum`／`maximum`／`format` + rule text 推 min／just_above_min／nominal／just_below_max／max（含 just_below_min／just_above_max）；contract／data 缺範圍 → CiC(BDY) `"BVA requires contract/data range truth"`。
     2.3 `State Transition ∈ techniques` → 從 rule text + DBML state field 推 `from_state`／`event`／`to_state`／illegal transitions；缺 state verifier target → CiC(GAP)。
     2.4 `Decision Table ∈ techniques` → 從 DSL-visible binding 推條件欄、從 assertion／state 推動作欄；組合爆炸時做 pairwise + 業務指定高風險組合；其餘走 CiC(BDY) 留待 clarify。
     2.5 `Clock Mock ∈ techniques` → 推 now anchor + in-window／just-expired／not-yet-active；缺 clock 來源 → CiC(GAP)。
     2.6 `Error Guessing ∈ techniques` → 補最多 2 筆殘留風險列，每筆含 `guess_reason`；**不准**用猜測取代 rule-derived 列。

3. **ASSERT：trace 完整性**
   - 每個 When payload key 對應 `$dsl_entries[].L4.{param_bindings, datatable_bindings, default_bindings}` 之一筆。
   - 每個 Then expectation key 對應 `$dsl_entries[].L4.assertion_bindings`／OpenAPI response field／DBML field 之一筆。
   - 每個 `$precondition_setup[]` 有具體 business identity 或 CiC(GAP)。
   - 任一失敗 → 列出 `(rule_anchor, key, reason)`，**STOP**；**禁止**寫弱 placeholder。

4. **ASSERT：具體值反佔位**
   - enumerated values 一律具體業務值；**禁止** placeholder（「某個」／「一些」／「XX」／「正確的」／「錯誤的」）。
   - 命中 → **STOP** + CiC(ASM)，列出 `(rule_anchor, value)`。

5. **EMIT：`$rule_test_data = { data_rows[], binding_trace[], cic_markers[] }`** — 不寫檔，交予 04。
