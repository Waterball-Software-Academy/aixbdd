# DSL entry 顆粒度

- **一條 entry 對一條 atomic rule**：每條 DSL entry 必須 trace 回 `source.rule_id`（即某條 `.feature` 中之 `Rule:`）；脫離 rule 漂浮的 entry **不得**收下，一條 entry 跨多 rule 的也**不得**收下。
- **必備 keys**：`id`／`source.{rule_id, boundary_id, feature_path}`／`L1`／`L2`／`L3.type`／`L4.{surface_id, surface_kind, callable_via, param_bindings, datatable_bindings, default_bindings, assertion_bindings, source_refs, preset}`。
- **L2 / L3 / L4 分層語意**：
  - `L1` ＝ 業務句（自然語言，BDD reader 可讀）
  - `L2` ＝ 語意脈絡（role／scope／業務角色）
  - `L3.type` ＝ 句型分類（前置-狀態／前置-參數／後置-回應／後置-狀態之 DSL 對偶）
  - `L4` ＝ 物理 mapping（surface_id 等技術錨點）
- **surface_kind 分類**（preset 對齊）：`loader`／`operation`／`state-verifier`／`response-verifier`／`external-stub`／`fixture-upload`／`internal-decision`。
- **L1 為業務句**：寫法為一句可被 BDD reader 讀懂的自然語言；**禁止**寫成技術 request shape 之 mirror。
- **stateless**：每條 L1／Then／And 句子單獨讀必能識別 business subject、lookup identity、expected data／effect；`And` 句**不繼承**上一 `Then` 之 subject。
- **identity opacity ban**：ID-like binding target 之 key 必含 `XXX ID`（譬如 `旅程 ID`、`stage ID`）；**禁止**把 identity 藏在 `旅程`／`階段`／`預約單` 等抽象名後。
- **dynamic ID**：scenario 中由系統產生之 ID 用 `$<business identifier>.id`（譬如 `$小明.id`、`$標準CRM旅程.id`）；**禁止** `$id`／`$previous.id`／`$剛剛建立的.id` 等依賴 scenario memory 之 ambiguous alias。

# 反例

- 一筆 entry 寫 `L1: "使用者送出訂單，系統計算金額並扣款並寄信"`——多 rule 混在一句，違反「一條 entry 對一條 atomic rule」。
- `L1: "POST /orders 回傳 201"`——把 request shape mirror 進 L1，破壞業務可讀性。
- `L4.assertion_bindings` 用 key `旅程` 指向 `data/journeys.dbml#journeys.id`——identity 不顯式，違反 ID opacity ban；應改 key 為 `旅程 ID`。
- `Then 訂單成立 And 訂單顯示在列表中`——`And` 句缺 subject／lookup identity，無法 stateless 解讀。
- entry 缺 `source.rule_id`——entry 脫離 rule 漂浮，無法 traceability。

# 禁止自生

- **不得**為 raw 未提之欄位開 placeholder（譬如 raw 寫「失敗會通知」，DSL 不得加 `{retry 次數}`／`{timeout 秒數}` 之 L1 placeholder）。
- **不得**為「方便寫 DSL」自加 placeholder 而非 atomic rule 真正需要的——placeholder 必須**對 rule 有意義**或**對 stateless lookup 必要**，二者皆不滿足則不增 placeholder。
- **不得**為「補齊四層」自填 L2／L3 但無 atomic rule 依據；缺資訊則回頭 `DELEGATE /clarify-loop`。
