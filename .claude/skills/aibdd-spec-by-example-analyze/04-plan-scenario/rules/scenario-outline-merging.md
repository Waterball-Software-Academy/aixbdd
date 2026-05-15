# Scenario Outline 合併顆粒度

- **記什麼**：何時把多列 example 合成 `Scenario Outline + Examples`、何時必須分為多個 `Scenario`、何時為單列 `Example`。每個合 Outline 的決策必須有 `merge_decision` 四件套（`step0_when_then_same` / `step1_given_same` / `extra_precondition_same` / `row_count`）。
- **WHY**：Outline 的價值在於「相同句型骨架、不同資料值」之共享閱讀；一旦 When+Then 句型不同、Given 設定不同、extra precondition 不同，合 Outline 就會出現「同一份 step text 對應不同行為」的歧義，下游 step-def 無法 dispatch，閱讀者也無法理解每列在驗什麼。

## §1 三層合併判定（依序）

1. **Step 0（When+Then 同句型？）**
   - 跨列之 When step templates、Then step templates、DSL `datatable_bindings` 之 column shape **全部相同**才能進下一步。
   - **任一不同 → 必須分 Scenario，不得合 Outline**。

2. **Step 1（Given 同設定？）**
   - 跨列之 Given step templates、setup policy（哪些 setup item／用哪個 DSL entry）**全部相同**才能進下一步。
   - 不同 → 必須分 Scenario（即使 When+Then 相同）。

3. **Extra precondition 同？**
   - 額外 precondition label（譬如「該會員為 VIP」「該訂單為跨境」）**跨列相同**才能合 Outline。
   - 不同 → 分 Scenario。

## §2 outcome 矩陣

| step0_when_then_same | step1_given_same | extra_precondition_same | row_count | outcome |
|---|---|---|---|---|
| ✓ | ✓ | ✓ | ≥ 2 | `ScenarioOutline` |
| ✓ | ✓ | ✓ | 1 | `Example`（單列 Scenario） |
| ✓ | ✗ 或 ✗ 任一 | — | ≥ 2 | `Scenario`（多筆） |
| ✗ | — | — | ≥ 1 | `Scenario`（多筆） |

## §3 Examples 欄位顆粒度

- 欄位**只取**跨列實際變動之 Given／When／Then 值 + 對應之 DSL-visible binding key（business-readable label）。
- **不得**包入：raw locator selector、production internals、contract 欄位但非 DSL-visible（譬如 internal `tenantId`）、analyzer-only metadata。
- 欄位順序：先 Given 變動值，再 When 變動值，最後 Then expected value。
- 同一 Outline 之 Examples 列數 ≥ 2；若 row_count 退回 1，必須降級為 `Example`（單列）並重畫為非 Outline 結構。

# 反例

- ✗ Rule 同時有 `成功送出` 與 `送出失敗` 兩列，Then 不同（`Then 系統受理` vs `Then 系統拒絕並回覆缺漏原因`）→ 合 Outline 把 status code 當 Examples 欄位。**應改為**：分為 happy_path Scenario + invalid_input Scenario。
- ✗ Outline 之 Examples 列 row A 用 `Given 訂單 X 存在`、row B 用 `Given 訂單 X 已付款` → step1_given_same 為 false，硬合。**應改為**：分 Scenario。
- ✗ Examples 欄位含 `selector = "input[name=phone]"`（raw locator）。**應改為**：欄位只放業務值 `phone`；locator 由 step-def 從 Story args 解析（boundary I4）。
- ✗ Outline 一列 datatable 5 欄、另一列 7 欄。**應改為**：分 Scenario，因 datatable column shape 不同。
- ✓ Rule 「金額必須介於 1 到 99 萬」之 BVA 6 列（min/just_above_min/nominal/just_below_max/max + 邊界外失敗）：When 一律 `使用者送出結帳請求 金額 {金額}`、Then 一律 `系統 {接受/拒絕}` 走同句型 + 不同期望值 → 可合 Outline；欄位 `金額 | 期望結果`。

# 禁止自生

- **不得**為了合 Outline 而**模糊 Then 文本**（譬如把「系統受理」與「系統拒絕」抽成「系統 {結果}」）——這會把不同行為合進同一 Outline，違反 step0_when_then_same 的本意。
- **不得**為了合 Outline 而**省略 extra precondition**——若 row A 之 Given 含「該會員為 VIP」、row B 不含，這是不同 Given 設定，必須分 Scenario。
- **不得**用 `<placeholder>` 在 Outline 之 step text 內表示「待填值」——所有 placeholder 必須對應 Examples 欄位且每列有具體值。
- 違反處置：STOP + 將該 group 之 `merge_decision.outcome` 改為 `Scenario`（分多筆），重新跑該 group 之 row clustering。
