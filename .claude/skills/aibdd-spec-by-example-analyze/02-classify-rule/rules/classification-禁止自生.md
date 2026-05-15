# 分類階段禁止自生（precision keystone）

本 sub-SOP 在判 type／techniques／dimensions 時最容易發生**自生**：把 rule 沒寫的測試需求塞進分類結果，下游 03 就會被迫去生 rule 未提的資料值與 example。本檔列**三類常見自生**，命中任一即 STOP + CiC(BDY)。

## §1 加 rule 沒寫的 technique

`techniques` 之來源**必須**是 rule body 字面或 type 之蘊含（見 `rule-type-classifier.md` §2）；**不得**從「為了多測一些」或「為了補滿矩陣」自加。

- ✗ rule 寫「會員可下單」→ 加 `BVA` 跑 `boundary_min`／`boundary_max`（rule 沒提數值範圍）
- ✗ rule 寫「使用者可建立帳號」→ 加 `Clock Mock` 跑 `time_dependency`（rule 沒提時間）
- ✗ rule 寫「使用者可查詢訂單」→ 加 `authorization` 跑角色拒絕（rule 沒提角色限制）
- ✓ rule 寫「金額必須介於 1 到 99 萬」→ 加 `BVA` + `boundary_min/max`（rule 明示數值區間）

## §2 加 rule 沒寫的 dimension

`dimensions` 必須由已加之 `techniques` 反推；**不得**加 technique 不蘊含之 dimension。

- ✗ techniques 只有 `EP`，dimensions 加 `state_transition`（無 `State Transition` 技術不該有此維度）
- ✗ techniques 有 `BVA` 但 dimensions 缺 `boundary_min`／`boundary_max`（BVA 必含邊界維度）
- ✗ 為了「完整」加 `failure_path` 但 rule 沒提外部依賴失敗——應改為：不加，或加並標 CiC(GAP)「rule 未提失敗模式」
- ✓ techniques `EP + BVA + State Transition` → dimensions `happy_path + invalid_input + boundary_min + boundary_max + state_transition`

## §3 改變 rule 語氣（hedging strengthening or weakening）

Rule body 的語氣（「必須」「不得」「一律」「僅」vs「應該」「通常」「視情況」「可能」）**必須 byte-for-byte preserve**。分類結果之 `params`／techniques 不得改變語氣強度。

- ✗ rule 寫「**必須**通過二階段驗證」→ params 標 `"通常會通過二階段驗證"`（弱化）
- ✗ rule 寫「**應該**通知使用者」→ params 標 `"必須通知使用者"`（強化）
- ✗ rule 寫「**僅**限會員可下單」→ techniques 不加 `authorization` 而視為一般 happy_path（弱化必要條件）
- ✓ rule 寫「**必須**通過二階段驗證」→ dimensions 含 `authorization`，params 保留 `"必須"` 原句

## §4 違反處置

任一類命中：
1. STOP 當前 rule 的分類動作。
2. 累積 CiC(BDY) 到 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`，格式：`{kind: BDY, where: <feature_path:rule_anchor>, text: "分類時自生 X 維度／technique／hedging；原 rule body 未支持"}`。
3. 繼續處理其餘 rule；該條 rule 之 `$strategy.cic` 標記，下游 03–05 不會為此 rule 生 example，只在 coverage report 標 CiC。

**WHY**：本 skill 的精度來源是「rule 真相不夠就停」，不是「為了多測一些補上去」。任何自生 dimension／technique 都會讓下游 03 自生資料值，最終把 plan 真相未授權之 example 落到 .feature，破壞 NO_PLAN_TRUTH_EDIT 與 NO_RULE_WORDING_CHANGE 邊界。
