# 枚舉階段禁止自生（precision keystone）

03 階段把 type／techniques／dimensions 轉成具體值——這是本 skill 最容易吸收 plan 真相缺洞、用「合理」值補上的階段。每筆未在 rule／contract／data 出現的值即視為**自生**。下列四類命中任一即 STOP + CiC。

## §1 數值與技術欄位自生

rule 或 contract 未提之具體數值不得自填。

- ✗ rule「失敗會通知使用者」→ 自加 `{ 重試次數: 3, 通道: email }`
- ✗ rule「金額不可為負」+ contract 無 upper bound → 自填 `{ 金額上限: 100000 }`
- ✗ rule「停留 5 分鐘後逾時」→ contract 沒有 timeout 設定，自填 `{ timeout: 300s }`
- ✓ rule「失敗會通知使用者」→ values 只綁 `{ 通知對象: <rule 明示 ID> }`，retry／通道走 CiC(GAP) 等 rule／contract 補

## §2 隱性前提自生

rule 未明示之前置條件不得加為 Given step／precondition_setup。

- ✗ rule「會員可下單」→ 自加 `Given 該會員已通過 KYC`
- ✗ rule「使用者可結帳」→ 自加 `Given 使用者已綁定信用卡`
- ✗ rule「訂單可以退款」→ 自加 `Given 訂單已超過七天鑑賞期`
- ✓ rule「會員可下單」→ Given 只放 `會員 {會員 ID} 存在`（rule 之直接前提）；KYC／信用卡綁定由 rule 自己說才加

## §3 欄位假設自生

OpenAPI／DBML 未宣告之欄位值不得作為 example 出現。

- ✗ contract response 只有 `{ orderId, status }`，example 期望多出 `{ createdAt: "2026-05-15T10:00:00Z" }`
- ✗ DBML `orders` table 無 `priority` 欄位，example 寫 `Then 訂單 priority 為 high`
- ✗ DSL `param_bindings` 缺 `phone` 但 example 之 When 攜帶 `{ phone: "0912345678" }`
- ✓ 缺欄位 → CiC(GAP) 寫 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`，回 `/aibdd-plan`／contract specifier 補

## §4 與原文衝突的具體值

rule 之硬條件（「必須」「不得」「一律」「僅」）對應 example 值之選擇必須與 rule 一致。

- ✗ rule「**必須**通過二階段驗證」→ example 跑 happy_path 時 Given 寫 `使用者未通過二階段驗證` 但 Then 仍寫 `系統受理`（與 rule 衝突）
- ✗ rule「**僅**限會員可下單」→ example 用 `角色: 訪客` 並期望 `Then 系統受理`（違 rule）
- ✓ rule「必須通過二階段驗證」→ happy_path Given `通過二階段驗證 = 是`；invalid_input 用 `通過二階段驗證 = 否` 並期望 `Then 系統拒絕並回覆需先完成二階段驗證`

## §5 違反處置

任一類命中：
1. 該 example／value set 立即丟棄。
2. 累積 CiC 便條紙（GAP／BDY／ASM 依類型）到 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`。
3. 該 rule 之 `$rule_data.cic` 標記；下游 04 不會為此 rule 之該維度生 example。
4. 繼續其餘 rule／維度。

**WHY**：spec-by-example 的執行端是 step-def，step-def 走 DSL binding 找 fixture 與 verifier。若 example 含 plan 真相外之值，step-def 將找不到對應 binding，紅出來；若強行 mock／自填 fixture，會破壞 NO_PLAN_TRUTH_EDIT 邊界。所以**寧可缺 example 走 CiC，不准自生值湊矩陣**。
