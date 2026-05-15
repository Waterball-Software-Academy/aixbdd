# SOP

輸入 `$rule_test_data`（03 產出）、`$indexed_truth`（01 產出）。本 sub-SOP 不寫檔；產出 `$scenario_plan`（每條 rule 對應 Scenario／Outline 群組、`example_columns`、`example_body_shape`、`merge_decision`、coverage rows）交予 05。

1. **THINK：assertion scope 限縮** — 規則見 `rules/scenario-outline-merging.md`、`rules/coverage-row-granularity.md`、`rules/plan-scenario-禁止自生.md`。
   - LOOP per `$rule_data` in `$rule_test_data.data_rows[]`:
     1.1 `$assertion_scope` = CLASSIFY by 02 之 `$strategy.type`：
         - `前置（參數）`／`前置（狀態）` → `precondition`
         - `後置（回應）` → `response`
         - `後置（狀態）` → `state`
         - `後置（狀態：外發）` → `external`
     1.2 FILTER `$rule_data.then_expect_sets` 至最小 `$assertion_scope`；其餘 Then 暫存 `$forbidden_then_entry_ids[]`（**禁止**渲染為 executable steps，除非為 dynamic-id bridge 並 trace）。
     1.3 ASSERT `response` scope 不含 aggregate／state Then；ASSERT `state` scope 不含 response Then（dynamic-id bridge 例外，必須附 trace）。

2. **THINK：row cluster → merge_decision → outcome**
   - LOOP per `$rule_data`:
     2.1 `$case_rows` = MERGE `$rule_data.{precondition_setup, given_value_sets, when_value_sets, then_expect_sets}` 為候選 case rows，每列含 `dimension`／`technique`／payload／binding_keys。
     2.2 `$row_clusters` = CLUSTER `$case_rows` by `(rule_anchor, $assertion_scope, setup_policy, normalized_clause_shape)`。
     2.3 LOOP per `$cluster`:
         2.3.1 `$when_then_same` = JUDGE normalized When／Then step templates 與 DSL datatable column shape 跨列相同（Step 0 check）。
         2.3.2 IF NOT `$when_then_same` → `$outcome = Scenario`（不可合 Outline）；CONTINUE。
         2.3.3 `$given_same` = JUDGE normalized Given step template 與 setup policy 跨列相同（Step 1 check）。
         2.3.4 `$extra_precondition_same` = JUDGE extra precondition labels 跨列相同。
         2.3.5 IF `$given_same` AND `$extra_precondition_same` AND count(`$cluster.rows`) ≥ 2 → `$outcome = ScenarioOutline`。
         2.3.6 ELSE IF count(`$cluster.rows`) == 1 → `$outcome = Example`（單列 Scenario）。
         2.3.7 ELSE → `$outcome = Scenario`（多列但無法合 Outline）。
     2.4 `$example_columns` = DERIVE 業務可讀之 Examples 欄位（跨列變動之 Given／When／Then 值 + DSL-visible binding key）。
     2.5 `$example_body_shape = { setup_policy, operation_clause, assertion_scope, allowed_then_entry_ids[], forbidden_then_entry_ids[] }`。
     2.6 `$merge_decision = { step0_when_then_same, step1_given_same, extra_precondition_same, row_count, outcome, reason }`。
     2.7 `$group = { feature_path, rule_anchor, precondition_setup, merge_decision, example_body_shape, outline_title, example_columns, rows, cic }`；附入 `$scenario_plan.groups[]`。

3. **DERIVE：coverage rows**
   - LOOP per `$group`, per `$dimension ∈ $strategy.dimensions`:
     3.1 IF `$group.rows` 含對應 dimension 之列 → DERIVE `CoverageRow = { coverage_type: example, rule_id: $group.rule_anchor, dimension, example_id, feature_path }`。
     3.2 ELSE → DERIVE `CoverageRow` 標 CiC reason（取自 03 之 cic_markers 或 `dimension_na` 註記）。

4. **ASSERT：merge invariants**
   - 每個 `$outcome == ScenarioOutline` 之 group：`step0_when_then_same` AND `step1_given_same` AND `extra_precondition_same` 全為 true 且 `row_count >= 2`；任一失敗 → **STOP**（違反 `rules/scenario-outline-merging.md`）。
   - 成功／失敗路徑（不同 Then 模板）不得合於同一 Outline；不同 extra precondition 不得合於同一 Outline；不同 DSL datatable column shape 不得合於同一 Outline。
   - `example_columns` 不得暴露 raw internal locators／production internals／非 DSL-visible 之 contract 欄位。

5. **ASSERT：coverage matrix 無空格**
   - 每個 `(rule × dimension)` cell 必有 ≥1 `CoverageRow` 或 CiC／N/A reason；否則 **STOP**。

6. **EMIT：`$scenario_plan = { groups[], coverage_rows[], cic_markers[] }`** — 不寫檔，交予 05。
