# Quality Gate — 語意軌（deterministic check 腳本已退役）

Phase 5 之 quality gate **僅**依下列 §2 語意 verdict 與 §3 veto。本 skill **已不再附帶** `check_example_coverage.py`、`check_preset_compliance.py`、`check_dsl_binding_trace.py`、`plan_paths.py`（檔案已刪）；亦**不要求**在本流程硬性 TRIGGER `grep_sticky_notes.py`。

## §1（保留序號；機械腳本欄已移除）

舊版曾在此列舉 deterministic scripts，現已空置。專案若自訂外加機械閘道，與 §2–§5 並行即可，不屬本 skill 契約義務。

## §2 Semantic verdict（subagent / 自己 THINK 二擇一）

Verdict prompt 模板放在 [`quality-gate-prompt.template.md`](quality-gate-prompt.template.md)。共 4 dimension（Q1–Q4，0.0–1.0），命中下列 veto 任一即 `VETO`，其餘無 veto 但任一 dim < 0.7 → `SOFT_FAIL`，否則 `PASS`。

## §3 Veto conditions（任一命中即 VETO）

- **NO_PLAN_TRUTH_EDIT**：`${BOUNDARY_PACKAGE_DSL}`／`${BOUNDARY_SHARED_DSL}`／`${CONTRACTS_DIR}`／`${DATA_DIR}`／`${TEST_STRATEGY_FILE}` 被本 skill 修改。
- **NO_RULE_WORDING_CHANGE**：atomic rule 本體字詞被改（逐字比對 input vs output）。
- **NO_FEATURE_REORG**：feature 路徑／檔名被本 skill 改動（屬 discovery owner）。
- **ATOMIC_RULE_EXAMPLE_COVERAGE**：任一 atomic rule 無任何 example 覆蓋。
- **COVERAGE_MATRIX_FULL**：(rule × dimension) 矩陣有空格且未標 CiC。
- **NO_REDUCER_METADATA_IN_FEATURE**：`.feature` 殘留 analyzer-only metadata（`@type` / `@techniques` / `@dimensions` / `@merge_decision` / `@cic` / `@setup_required` 等）。
- **PRECONDITION_SETUP_BOUND**：任一 Example 之 Given 未綁到既有 plan DSL／shared DSL／test-strategy seed → 缺 setup mapping。
- **DSL_BINDING_TRACE**：Scenario step／Examples 欄位無法追溯至 DSL binding 或 OpenAPI／DBML truth。
- **DSL_L1_STEP_PATTERN_COMPLIANCE**：Gherkin step 句型未對應任何 matching DSL entry 的 L1 canonical 模板。
- **SCENARIO_L1_FROM_PLAN_DSL**：具體 step 無法 trace 至所選 DSL entry 的 L1 與 `dsl_l1_pattern_index`。
- **NO_UNKNOWN_RESPONSE_ASSERTION**：Then assert OpenAPI response schema 或 DSL `assertion_bindings` 未宣告之 response 欄位。
- **MINIMAL_RULE_TARGET_EXAMPLE**：response-rule example 順手 assert DB state，或 state-rule example 順手 assert response（除非 dynamic-id bridge 並 trace）。
- **NO_MERGE_MIXED_WHEN_THEN**：同一 Scenario Outline 之 Examples 混用不同 When+Then 模板或不同 extra precondition。
- **SPEC_BY_EXAMPLE_CONCRETE**：Examples 含白話佔位符（「某個」／「一些」／「XX」／「正確的」／「錯誤的」）。
- **AGGREGATE_GIVEN_BUILDER_REACHABILITY**：persistence coverage gate = `not-null-columns` 時，任一參與 entity 缺 `${persistence_handler}` builder。

## §4 Weighted dimensions（0.0–1.0；任一 < 0.7 → SOFT_FAIL）

- **Q1 Truth fidelity**：atomic rule wording、feature 路徑、DSL／contract／data／test-strategy 全 byte-identical。
- **Q2 Example completeness**：每條 atomic rule × dimension 矩陣填滿或標 CiC；BVA／State Transition／Decision Table 之必備維度齊備。
- **Q3 Binding traceability**：每個 Scenario step／Examples 欄位有 `dsl_binding_trace` 指回 L4 binding 或 OpenAPI／DBML 欄位。
- **Q4 Minimal rule-target focus**：每條 example 只驗其 atomic rule 的目標 axis；跨 axis 旁路只在 dynamic-id bridge 時允許並有 trace。

## §5 Verdict JSON shape

寫入 `${PLAN_REPORTS_DIR}/bdd-analyze-quality.md`（僅語意軌；**不含**已刪除之 deterministic check 腳本匯出）：

```json
{
  "verdict": "PASS | SOFT_FAIL | VETO",
  "vetoes": [{ "condition": "string", "evidence": "string" }],
  "dimension_scores": { "Q1": 1.0, "Q2": 1.0, "Q3": 1.0, "Q4": 1.0 },
  "fix_hints": []
}
```
