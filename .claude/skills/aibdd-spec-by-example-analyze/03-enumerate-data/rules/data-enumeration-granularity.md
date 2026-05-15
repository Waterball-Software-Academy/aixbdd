# Test-Data 枚舉顆粒度（per technique）

- **記什麼**：每條 atomic rule × dimension 的**最少必要**具體值列——足以驗 rule 所宣告之行為，且每個值都能 trace 回 plan DSL binding／OpenAPI／DBML 真相。
- **WHY**：spec-by-example 的精度來自「具體值」而非「規則描述」；只有具體值才能讓下游 step-def 拿來執行。但具體值不得超出 rule 與 plan 真相之合意範圍，否則 example 會驗到 rule 沒承諾的行為。

## §1 EP（等價類）

- **valid 類**：每條 rule 至少一筆代表值（happy_path），值取自 rule 提及之合法選項或 DSL binding 之預設業務值。
- **invalid 類**：每個不滿足 rule 之獨立子條件至少一筆代表值；對應 `invalid_input` 或 `error_handling`。
- 反例：rule 寫「必填欄位」→ valid = 任一非空字串，invalid = 空字串。**不得**自生「null」「undefined」這類技術值——除非 contract 明文宣告該欄位可為 null。

## §2 BVA（邊界值）

- 數值／長度／時間範圍 rule：至少含 `min`／`max` 兩端；rule 提及 just-above／just-below 時對應加 `just_above_min`／`just_below_max`。
- 來源優先序：OpenAPI `minimum`／`maximum`／`format` > rule body 字面數值 > DSL `param_bindings` 之 schema constraint。
- 三者皆缺 → CiC(BDY)；**不得**自定一個「合理」邊界值。
- 反例：rule 寫「金額必須為正數」→ values: `{ min: 1, max: <contract upper or rule-stated>, just_below_min: 0, just_above_max: <out-of-range value if contract bounded> }`。**不得**寫 `{ min: 1, max: 1000000 }` 若 contract／rule 都未提 100 萬上限。

## §3 State Transition（狀態轉移）

- 每條 rule 必含 `from_state`／`event`／`to_state` 三件；illegal transition 至少一筆（如 rule 明示拒絕）。
- 狀態值來源：rule body 字面狀態名 + DBML enum／status 欄位。
- DBML 缺 state verifier target → CiC(GAP)；**不得**自生狀態名。

## §4 Decision Table（決策表）

- 每個業務關鍵組合至少一列；組合爆炸時做 pairwise 並補業務指定之高風險組合。
- 條件欄取自 DSL-visible binding；動作欄取自 assertion／state target。
- 若 rule 未明示某組合之行為 → 該組合走 CiC(BDY) 留待 clarify，不得自定行為。

## §5 Clock Mock（時間 mock）

- 必含 `now` anchor + 至少一筆 in-window／just-expired／not-yet-active（依 rule 之時間語意選擇）。
- 時間值用 ISO-8601 具體 timestamp（不得寫「明天」「下週」這類相對值——具體值不得依賴 step-def 解析）。
- 缺 clock source 在 test-strategy → CiC(GAP)。

## §6 Error Guessing（猜測殘留風險）

- **僅**在 rule-derived techniques（EP／BVA／State Transition／Decision Table）已產生 ≥1 列之後加；最多 2 筆。
- 每筆必含 `guess_reason`（字串，說明為何猜測此風險）。
- **不得**用猜測列取代 rule-derived 列。

# 反例

- ✗ rule「金額必須為正數」，contract 未指定上限 → 自加 `{ max: 1000000 }`。**應改為**：max 走 CiC(BDY) 留待 contract 補。
- ✗ rule「狀態變更為待出貨」，DBML status 欄位枚舉缺「待出貨」 → 自定 status=`PENDING_SHIPMENT`。**應改為**：CiC(GAP)，回 `/aibdd-plan` 補 DBML enum。
- ✗ BVA 值用 `{ min: "一些值", max: "上限值" }` 這類抽象描述。**應改為**：具體數值 `{ min: 1, max: 99999 }` 或 CiC(BDY)。
- ✗ Error Guessing 寫 5 筆「我覺得可能會」風險。**應改為**：最多 2 筆且每筆 `guess_reason` 明確；不取代 rule-derived 列。
- ✓ rule「金額必須介於 1 到 99 萬」（rule 明示數值）→ BVA values: `{ min: 1, just_above_min: 2, max: 990000, just_below_max: 989999, just_below_min: 0, just_above_max: 990001 }`。

# 禁止自生

- **不得**自生 OpenAPI／DBML 未宣告之欄位值：rule 沒提 `email` 欄位之預設 → 不得寫 `email: test@example.com`。應為：CiC(GAP) 等 contract 加欄位。
- **不得**自生 contract schema constraint 以外之邊界：contract 寫 `minimum: 0` → 不得自定 `min: -100`，因為這在 contract 範圍之外，無法 trace。
- **不得**自生 placeholder：「某個 ID」「某個用戶」「XX 元」「正確的金額」一律 STOP + CiC(ASM)。
- **不得**自生 DSL binding key 以外之 When／Then 鍵：rule 明示某欄位但 DSL 未綁該欄位 → CiC(GAP)，回 `/aibdd-plan` 補 binding。
- 違反處置：STOP + 累積 CiC(GAP)／CiC(BDY)／CiC(ASM) 至 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`，列出 `(rule_anchor, key, source_missing)`。
