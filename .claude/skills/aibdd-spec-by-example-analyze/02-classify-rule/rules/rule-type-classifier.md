# Rule 分類顆粒度（type × techniques × dimensions）

## §1 Type 分類（恰好一）

依 rule body 之語意分類為下列之一：

| Type | 判定特徵 | Few-shot |
|---|---|---|
| `前置（參數）` | 描述輸入格式／數值範圍／必填欄位 | 「訂單總金額必須為正數」「身分證字號格式必須符合統一編碼規則」「收貨地址為必填」 |
| `前置（狀態）` | 描述系統或 aggregate 當前狀態之約束 | 「訂單必須處於待出貨審核狀態才能標記為已審核」「買家帳號遭限制下單時不得建立新訂單」「行銷滿額折價方案必須仍在有效期間內」 |
| `後置（回應）` | 描述對外回覆內容／錯誤說明／回傳欄位 | 「訂單建立成功時系統會回覆受理結果並提供可追蹤的訂單編號」「結帳資料不完整時系統會回覆具體缺漏原因」 |
| `後置（狀態）` | 描述持久化寫入／狀態變更／idempotency／副作用 | 「付款完成後訂單狀態變更為待出貨」「重複送出相同購物車結帳請求不得建立第二筆訂單」「退件後必須寫入客服備註並保留歷史紀錄」 |

**WHY**：4 種 type 對應的測試 fixture 模板與斷言 surface 不同（params 走 invalid input 反例；狀態走 State Transition；回應走 response body；狀態寫入走 DB verifier）。分錯 type 會導致 example_body_shape 在 04 階段選錯，整條 example 失準。

## §2 Techniques 分類（一條 rule 可多技術；最小集合即可）

| Technique | 加入條件 | Few-shot |
|---|---|---|
| `EP` | `前置（參數）`／`前置（狀態）` 一律含 | 「收貨人手機必須為 10 碼」「買家必須擇一選擇配送時段（平日／假日）」 |
| `BVA` | 數值範圍／長度／上下限／金額 | 「訂單金額必須介於 1 元到 99 萬之間」「身分證字號長度必須為 10 碼」「平台服務費率不得超過公告上限」 |
| `EP（狀態分類）` | `前置（狀態）` 之狀態枚舉 | 「僅限狀態為待補資料的訂單可上傳缺漏證明」「買家帳號遭限制時不得送出訂單」 |
| `Clock Mock` | 時間／截止／生效 | 「免運門檻僅在活動期間內有效」「預購下單時間不得早於開放預購日」 |
| `EP（成功／錯誤路徑）` | `後置（回應）` 一律含 | 「結帳送出成功時系統會回覆受理結果」「結帳資料不完整時系統會回覆缺漏欄位清單」 |
| `State Transition` | `後置（狀態）` 之狀態變更 | 「審核通過後訂單狀態由待審核變更為待出貨」「補資料完成後訂單狀態由待補資料回到待審核」 |
| `Decision Table` | 多條件組合決策 | 「依會員等級與商品類別組合決定可用運費規則區間」「依訂單金額區間與是否含預購品決定是否需要額外審核」 |
| `Error Guessing` | 補充殘留風險（**僅**在 rule-derived techniques 之後加；最多 2 筆） | 「在已具備 EP/BVA/狀態轉移案例後，補一筆『重複送出』的風險案例」 |

## §3 Dimensions 分類（依 techniques 反推；最小集合）

| Dimension | 加入條件 |
|---|---|
| `happy_path` | 預設加；若 rule 只描述禁止行為而無成功路徑，需以 `dimension_na` 註記理由 |
| `invalid_input` | `前置（參數）` 之 validation |
| `boundary_min` / `boundary_max` | `BVA` |
| `error_handling` | `後置（回應）` 之失敗路徑 |
| `state_transition` | `State Transition` |
| `time_dependency` | `Clock Mock` |
| `idempotency` | 明示之 replay／重複 side effect |
| `decision_completeness` | `Decision Table`（無組合爆炸時做完整集；爆炸時用 pairwise + 業務指定關鍵組合） |
| `authorization` | 角色或權限規則 |
| `failure_path` | 外部依賴失敗 |

# 反例

- ✗ rule「訂單金額必須為正數」→ 分 `後置（狀態）`、技術 `State Transition`。**該為** `前置（參數）` + `EP/BVA` + `invalid_input/boundary_min`。
- ✗ rule「審核通過後訂單狀態由待審核變更為待出貨」→ 分 `後置（回應）` + 加 `error_handling`。**該為** `後置（狀態）` + `State Transition` + `state_transition`。
- ✗ rule「金額必須介於 1 到 99 萬」→ techniques 只放 `EP`，dimensions 缺 `boundary_min`／`boundary_max`。**該為** `EP + BVA` + `boundary_min + boundary_max`。
- ✗ rule 無 `BVA` 卻硬塞 `boundary_min`／`boundary_max`——dimensions 必須由 techniques 反推，不得無源頭添加。
- ✗ techniques 只放 `Error Guessing`——猜測技術不得單獨；rule-derived techniques 必先存在。

# 禁止自生

- **不得**加 rule body 未提之 technique／dimension：rule 沒寫時間條件不得加 `Clock Mock`／`time_dependency`；rule 沒寫角色不得加 `authorization`。
- **不得**為了「補滿矩陣」而加假 dimension——dimension 是「rule 自然要求」的覆蓋面，不是「我覺得應該測」的補充。
- **不得**從一條 rule 推導出超過 1 個 type——若 rule 同時包含參數約束與狀態變更兩個語意，必為 atomic rule 拆解問題，回 `/aibdd-discovery` 拆，不在本 skill 內 split。
- **不得**將 rule body 「應該」「通常」「視情況」hedging 解讀為「必須」——rule 語氣不得被本 skill 強化或弱化（見 `classification-禁止自生.md`）。
- 違反處置：STOP + 累積 CiC(BDY) 到 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`，列出該 rule_anchor 與分歧理由。
