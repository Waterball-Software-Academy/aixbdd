---
rp_type: reasoning_phase
id: aibdd-spec-by-example-analyze.02-classify-rule-test-strategy
context: aibdd-spec-by-example-analyze
slot: "02"
name: Classify Rule Test Strategy
variant: none
consumes:
  - name: IndexedTruthModel
    kind: derived_axis
    source: upstream_rp
    required: true
produces:
  - name: RuleStrategyBundle
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-spec-by-example-analyze.03-enumerate-rule-data-values
---

# Classify Rule Test Strategy

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis: []
```

### 1.2 Search SOP

1. `$indexed_truth` = READ `IndexedTruthModel`
2. ASSERT `$indexed_truth.files[]` is present
3. ASSERT `$indexed_truth.step_patterns` is present
4. ASSERT `$indexed_truth.plan_dsl_index` is present
5. ASSERT `$indexed_truth.test_strategy` is present
6. LOOP per `$file` in `$indexed_truth.files` until all Rule blocks are visited
   6.1 IF `$file.operation_gate_ok == false`
       6.1.1 `$file_cic` = DERIVE CiC(CON) for operation partition mismatch
       6.1.2 CONTINUE
   6.2 ASSERT `$file.dsl_entry_ids[]` is present
   6.3 LOOP per `$rule` in `$file.rules` until all rules are classified
       6.3.1 `$rule_text` = PARSE `$rule.raw_rule_title_line` and `$rule.body_lines`
       6.3.2 ASSERT `$rule_text` is not modified
       END LOOP
   END LOOP

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: RuleStrategyBundle
  element_rules:
    element_vs_field:
      element: "A per-Rule strategy assignment consumed by value enumeration"
      field: "A scalar annotation, technique name, or dimension nested under a RuleStrategy"
  elements:
    RuleStrategy:
      role: "Bind one atomic Rule to its BDD test strategy and internal metadata block"
      fields:
        feature_path: "path"
        rule_anchor: "string"
        annotations_block: "internal metadata string or structured rendering"
        type: "前置（參數）|前置（狀態）|後置（回應）|後置（狀態）"
        techniques: "string[]"
        dimensions: "string[]"
        params: "dict<string,string>"
        cic: "CiCMarker[]"
      invariants:
        - "annotations_block must retain type, techniques, and dimensions unless cic blocks the rule"
        - "Reducer metadata is internal artifact data; it must not be rendered into final .feature output"
        - "techniques must be selected by the decision tree, not copied from a template placeholder"
        - "dimensions must be a minimal set, not a mechanical full matrix"
```

## 3. Reasoning SOP

1. LOOP per `$rule` in `IndexedTruthModel.files[].rules[]` until all rules are assigned
   1.1 `$type` = CLASSIFY `$rule` by exact prefix or semantic cues:
       - input format, numeric range, required field -> `前置（參數）`
         few-shots:
         - "訂單總金額必須為正數" -> `前置（參數）`
         - "身分證字號格式必須符合統一編碼規則" -> `前置（參數）`
         - "單筆訂單未滿免運門檻時，運費計算不得為負數" -> `前置（參數）`
       - system or aggregate current state -> `前置（狀態）`
         few-shots:
         - "訂單必須處於待出貨審核狀態才能標記為已審核" -> `前置（狀態）`
         - "買家帳號遭限制下單時不得建立新訂單" -> `前置（狀態）`
         - "行銷滿額折價方案必須仍在有效期間內" -> `前置（狀態）`
       - 對外回覆／錯誤說明／回傳欄位 -> `後置（回應）`
         few-shots:
         - "訂單建立成功時，系統會回覆受理結果並提供可追蹤的訂單編號" -> `後置（回應）`
         - "結帳資料不完整或格式不符時，系統會回覆具體缺漏原因，方便使用者修正後再送" -> `後置（回應）`
         - "查詢訂單處理進度時，系統會回覆目前物流階段與已套用折扣等可讀資訊" -> `後置（回應）`
       - persisted write, state change, idempotency, side effect -> `後置（狀態）`
         few-shots:
         - "付款完成後訂單狀態變更為待出貨" -> `後置（狀態）`
         - "重複送出相同購物車結帳請求不得建立第二筆訂單" -> `後置（狀態）`
         - "退件後必須寫入客服備註並保留歷史紀錄" -> `後置（狀態）`
   1.2 IF `$type` cannot be classified:
       1.2.1 `$cic` = DERIVE CiC(BDY) "無法分類 rule 型別"
       1.2.2 `$strategy` = DERIVE `RuleStrategy` with `$cic`
       1.2.3 CONTINUE
   1.3 `$techniques` = CLASSIFY `$rule` and `$type` by the technique tree:
       - `前置（參數）` always includes `EP`
         few-shots:
         - "收貨人手機必須為 10 碼" -> `EP`
         - "買家必須擇一選擇配送時段（平日／假日）" -> `EP`
         - "收貨地址為必填" -> `EP`
       - numeric, length, min, max, interval, positive amount includes `BVA`
         few-shots:
         - "訂單金額必須介於 1 元到 99 萬之間" -> `EP + BVA`
         - "身分證字號長度必須為 10 碼" -> `EP + BVA`
         - "平台服務費率不得超過公告上限" -> `EP + BVA`
       - `前置（狀態）` includes `EP（狀態分類）`
         few-shots:
         - "僅限狀態為「待補資料」的訂單可上傳缺漏證明" -> `EP（狀態分類）`
         - "買家帳號遭限制時不得送出訂單" -> `EP（狀態分類）`
         - "滿額折價活動停用時不得選用該活動" -> `EP（狀態分類）`
       - time, expiry, not-yet-active includes `Clock Mock`
         few-shots:
         - "免運門檻僅在活動期間內有效" -> `Clock Mock`
         - "預購下單時間不得早於開放預購日" -> `Clock Mock`
         - "補資料期限到期後不得再上傳缺漏證明" -> `Clock Mock`
       - `後置（回應）` includes `EP（成功／錯誤路徑）`
         few-shots:
         - "結帳送出成功時，系統會回覆受理結果並提供可追蹤的訂單編號" -> `EP（成功／錯誤路徑）`
         - "結帳資料不完整時，系統會回覆缺漏欄位清單，方便使用者補齊後再送" -> `EP（成功／錯誤路徑）`
         - "訂單不符合出貨條件時，系統會回覆不可受理的原因" -> `EP（成功／錯誤路徑）`
       - state change includes `State Transition`
         few-shots:
         - "審核通過後，訂單狀態由待審核變更為待出貨" -> `State Transition`
         - "補資料完成後，訂單狀態由待補資料回到待審核" -> `State Transition`
         - "已結案的訂單不得再變更為待審核" -> `State Transition`
       - multi-condition outcome includes `Decision Table`
         few-shots:
         - "依會員等級與商品類別組合，決定可用運費規則區間" -> `Decision Table`
         - "依訂單金額區間與是否含預購品，決定是否需要額外審核" -> `Decision Table`
         - "依買家身分別與下單管道，決定可選用的配送方式種類" -> `Decision Table`
       - bounded aggregate amount includes `BVA`
         few-shots:
         - "套用折扣後結帳金額不得超過原始商品總額" -> `BVA`
         - "折扣後應付金額不得為負數" -> `BVA`
         - "單一會員累計已用點數加上本次兌換不得超過可用點數上限" -> `BVA`
       - common residual risk may add `Error Guessing` only after rule-derived techniques
         few-shots:
         - "在已具備 EP/BVA/狀態轉移案例後，補一筆『重複送出』的風險案例（≤2）" -> `Error Guessing`
         - "在已具備主要路徑後，補一筆『同分鐘內連點兩次』的風險案例（≤2）" -> `Error Guessing`
         - "不得只用猜測案例取代規則推導案例" -> `Error Guessing（禁止取代）`
   1.4 `$dimensions` = DERIVE minimal coverage dimensions from `$techniques`:
       - `happy_path` unless the rule has no valid business success path
         few-shots:
         - "結帳送出成功且資料齊全時，系統受理並進入審核流程" -> `happy_path`
         - "補資料完成且內容符合要求時，訂單可回到審核排程" -> `happy_path`
         - "若規則只描述禁止行為而沒有成功路徑，則以 `# @dimension_na happy_path: ...` 說明" -> `happy_path（N/A 需理由）`
       - `invalid_input` for validation or parameter preconditions
         few-shots:
         - "手機號碼格式不符合規定時不得送出" -> `invalid_input`
         - "必填欄位未填寫時不得送出" -> `invalid_input`
         - "上傳檔案類型不在允許清單時不得送出" -> `invalid_input`
       - `boundary_min` and `boundary_max` for BVA
         few-shots:
         - "訂單金額剛好等於下限與剛好等於上限皆可受理" -> `boundary_min + boundary_max`
         - "年齡剛滿門檻與剛好超過上限邊界需各驗一筆" -> `boundary_min + boundary_max`
         - "字串長度在邊界內外各驗一筆（避免只測中間值）" -> `boundary_min + boundary_max`
       - `error_handling` for response violations
         few-shots:
         - "訂單不符合資格時，系統需清楚回覆不可受理原因" -> `error_handling`
         - "補資料逾期時，系統需回覆已無法再補並提示下一步" -> `error_handling`
         - "庫存不足時，系統需回覆原因並避免默默失敗" -> `error_handling`
       - `state_transition` for State Transition
         few-shots:
         - "審核通過造成狀態由待審核變更為待出貨" -> `state_transition`
         - "退件造成狀態由待審核變更為已退件" -> `state_transition`
         - "非法狀態轉移需有對應失敗回覆或阻擋行為" -> `state_transition`
       - `time_dependency` for Clock Mock
         few-shots:
         - "活動截止前一日與截止後一日各驗一次" -> `time_dependency`
         - "補資料期限到期前一刻與到期後一刻各驗一次" -> `time_dependency`
         - "尚未到開放預購日與已開放日各驗一次" -> `time_dependency`
       - `idempotency` when replay or repeatable side effect is explicit
         few-shots:
         - "同一訂單編號重複送出不得重複建立出貨單" -> `idempotency`
         - "重複扣款情境不得發生二次入帳" -> `idempotency`
         - "重試送件不得產生多份相同內容的受理紀錄" -> `idempotency`
       - `decision_completeness` for Decision Table
         few-shots:
         - "會員等級 × 商品類別 的關鍵組合需各至少一列" -> `decision_completeness`
         - "是否含預購品 × 訂單金額區間 的關鍵組合需各至少一列" -> `decision_completeness`
         - "若組合過多，先 pairwise，再把業務指定的高風險組合補齊" -> `decision_completeness`
       - `authorization` for role or permission rules
         few-shots:
         - "一般客服不可核准超過一定金額的退款" -> `authorization`
         - "主管可覆核但不可越權修改已結案訂單資料" -> `authorization`
         - "外部買家不可查看內部出貨備註" -> `authorization`
       - `failure_path` for external dependency failures
         few-shots:
         - "金流查詢失敗時，系統需提示暫時無法完成付款確認並保留重試空間" -> `failure_path`
         - "簡訊通知服務不可用時，訂單仍可成立但需標示通知延遲" -> `failure_path`
         - "檔案儲存服務失敗時，不得假裝上傳成功" -> `failure_path`
   1.5 IF `$dimensions` includes `failure_path`:
       1.5.1 ASSERT `IndexedTruthModel.test_strategy.dependency_edges` or `plan_dsl_index.entries[].L4.surface_kind == external-stub` covers the dependency
       1.5.2 IF missing: add CiC(GAP) "failure_path requires /aibdd-plan dependency edge or external-stub DSL"
   1.6 `$params` = DERIVE business-readable parameters and constraints from `$rule` and matching DSL bindings
  1.7 `$annotation_block` = RENDER internal Rule metadata with `type`, `techniques`, `params`, `dimensions`, optional `dsl_entry`, optional `binding_keys`, optional `dimension_na`, optional `cic`
   1.8 `$strategy` = DERIVE `RuleStrategy` from `$rule`, `$type`, `$techniques`, `$dimensions`, `$params`, `$annotation_block`, and `$cic`
   1.9 ASSERT `$strategy.annotations_block` does not rewrite the Rule body
   END LOOP
2. `$rule_strategy_bundle` = DERIVE `RuleStrategyBundle` from all `RuleStrategy` elements
3. ASSERT every non-CiC RuleStrategy has non-empty `type`, `techniques`, and `dimensions`

## 4. Material Reducer SOP

1. EMIT `RuleStrategyBundle` with:
   1.1 `strategies[]`: all `RuleStrategy` elements
   1.2 `cic_markers[]`: all CiC(GAP|ASM|BDY|CON) emitted during classification
2. `$annotation_format` = READ [`assets/sentence-model/02-rule-reducer-block.md`](../../assets/sentence-model/02-rule-reducer-block.md)（Rule reducer metadata SSOT）
3. LOOP per `$strategy` in `RuleStrategyBundle.strategies[]` until every rule has persisted metadata
   3.1 `$block` = READ `$strategy.annotations_block`
   3.2 ASSERT `$block` preserves Rule title / Rule body semantics without requiring `.feature` mutation
   3.3 ASSERT `$block` field order matches `$annotation_format`
   3.4 ASSERT `$block` is retained in downstream bundles for coverage / handoff consumption
   END LOOP
4. ASSERT every `RuleStrategy.rule_anchor` points to one indexed Rule
5. ASSERT every `RuleStrategy.annotations_block` contains `type`, `techniques`, and `dimensions` unless `RuleStrategy.cic` blocks enumeration
6. ASSERT BVA techniques imply `boundary_min` or `boundary_max`
7. ASSERT State Transition techniques imply `state_transition`
