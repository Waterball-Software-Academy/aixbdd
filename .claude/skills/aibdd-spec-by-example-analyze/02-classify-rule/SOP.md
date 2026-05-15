# SOP

輸入 `$indexed_truth`（01 產出）。本 sub-SOP 不寫檔；產出 `$rule_strategy`（每條 atomic rule 對應 `{type, techniques, dimensions, params, cic}`）交予 03。

1. **THINK：逐條 atomic rule 分類** — 規則見 `rules/rule-type-classifier.md` §1–§3、`rules/classification-禁止自生.md`。
   - LOOP per `$rule` in `$indexed_truth.feature_files[].rules[]`:
     1.1 `$type` = CLASSIFY `$rule.body_lines` 為 `前置（參數）`／`前置（狀態）`／`後置（回應）`／`後置（狀態）` 其一（判定見 §1）。
     1.2 IF `$type` 無法判定 → 累積 CiC(BDY) `"無法分類 rule 型別"`，`$strategy.cic` 紀錄並 CONTINUE。
     1.3 `$techniques` = CLASSIFY 適用測試技術（§2：EP／BVA／Clock Mock／State Transition／Decision Table／Error Guessing）。
     1.4 `$dimensions` = DERIVE 最小覆蓋維度集合（§3：happy_path／invalid_input／boundary_min／boundary_max／error_handling／state_transition／time_dependency／idempotency／decision_completeness／authorization／failure_path）。
     1.5 `$params` = DERIVE 業務可讀參數（取自 rule text 字面與 matching DSL binding key）；**不**自加 rule 未提之參數。
     1.6 `$strategy = { rule_anchor, type, techniques, dimensions, params, cic }`；附入 `$rule_strategy.strategies[]`。

2. **ASSERT：分類完整性**
   - 每條非 CiC strategy 之 `type`、`techniques`、`dimensions` 皆非空。
   - `BVA ∈ techniques` → `dimensions` 必含 `boundary_min` 或 `boundary_max`。
   - `State Transition ∈ techniques` → `dimensions` 必含 `state_transition`。
   - `Clock Mock ∈ techniques` → `dimensions` 必含 `time_dependency`。
   - `Error Guessing ∈ techniques` 但無 rule-derived techniques（EP／BVA／State Transition 等）→ **STOP**；猜測技術不得單獨成為唯一測試策略（見 `rules/classification-禁止自生.md`）。

3. **ASSERT：failure_path 之外部依賴 anchor**
   - IF `failure_path ∈ dimensions`：ASSERT `$indexed_truth.test_strategy.dependency_edges` 或 `$indexed_truth.dsl_entries[].L4.surface_kind == external-stub` 涵蓋該依賴。
   - 缺 → 累積 CiC(GAP) `"failure_path requires /aibdd-plan dependency edge or external-stub DSL"` 並繼續；下游 04 之 example_body_shape 不渲染該維度。

4. **EMIT：`$rule_strategy = { strategies[], cic_markers[] }`** — 不寫檔，交予 03。
