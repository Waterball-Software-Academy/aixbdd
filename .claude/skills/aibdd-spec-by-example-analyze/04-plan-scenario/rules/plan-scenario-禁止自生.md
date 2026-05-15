# Scenario 規劃階段禁止自生

04 階段最容易發生**自生**：為了 example 看起來「完整」而把不屬於該 atomic rule 的 Then 旁路加入。下列三類命中即 STOP。

## §1 跨 axis 旁路 assertion

每個 example 只驗其 atomic rule 之**唯一** target axis；不得順手驗其他 axis（除非 dynamic-id bridge 並 trace）。

- ✗ rule type=`後置（回應）` 之 example，順手加 `Then 訂單狀態應變更為 待出貨`（這是 state axis）
- ✗ rule type=`後置（狀態）` 之 example，順手加 `Then response.body.orderId 不為空`（這是 response axis，除非 state verifier 必須用 dynamic id 從 response 取，並標 `dynamic_id_bridge` trace）
- ✗ rule type=`前置（參數）` 之 example，順手加 `Then 系統寫入 audit log`（這是 state axis 之副作用，rule 沒承諾）
- ✓ rule type=`後置（回應）` → Then 只放 `系統 {接受／拒絕}` + 回覆內容；DB 不驗。
- ✓ dynamic-id bridge 合法情境：state verifier 需 `orderId` 但業務無內生 ID → 從 response 取 `orderId` 後驗 DB，必須在 `merge_decision.reason` 與 binding_trace 標 `dynamic_id_bridge`。

## §2 強塞 Outline

把不同句型／設定／precondition 之列硬合為 Outline 即自生。

- ✗ 把 happy_path 與 invalid_input 之列合 Outline（Then 不同模板）
- ✗ 把 VIP 與一般會員之列合 Outline（extra precondition 不同）
- ✗ 把 5 欄 datatable 與 7 欄 datatable 之列合 Outline（datatable column shape 不同）
- ✗ 為了合 Outline 把 Then 文本模糊化成 `Then 系統 {結果}`（破壞 step0_when_then_same 本意）
- ✓ 不同 BVA 邊界值（min／max／just_below_max）+ 相同 When＋Then 模板 → 合 Outline

## §3 加 rule 沒承諾的 example 欄位

Examples 欄位之 column 必須對應跨列實際變動且 DSL-visible 之 binding key；不得加 rule 沒提之欄位。

- ✗ rule「金額必須為正數」之 Outline 加欄位 `phone`（rule 沒提 phone）
- ✗ Outline 加欄位 `tenantId`（internal field，非 DSL-visible）
- ✗ Outline 加欄位 `selector = "input[name=amount]"`（raw locator）
- ✓ rule「金額必須介於 1 到 99 萬」之 BVA Outline → 欄位 `金額 | 期望結果`

## §4 違反處置

任一類命中：
1. STOP 當前 group 之規劃。
2. 累積 CiC(CON) 至 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`，格式：`{kind: CON, where: <feature_path:rule_anchor>, text: "scenario 規劃自生 X 旁路／合 Outline／欄位"}`。
3. 重畫該 group（分 Scenario 或刪除自生 Then 旁路）。

**WHY**：自生跨 axis 旁路 assertion 會讓 example 在 step-def 端紅出來——step-def 找不到 DSL binding；自生合 Outline 會讓 step-def 跑出未承諾的行為；自生欄位會破壞 binding traceability，違反 `quality.md DSL_BINDING_TRACE` veto。
