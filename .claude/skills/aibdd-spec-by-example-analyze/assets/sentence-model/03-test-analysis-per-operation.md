# 測試分析（每 operation 一段）

## {operation_name}

**等價類劃分**: …（對應 internal metadata 中的 `techniques: [EP, ...]`）
**邊界值分析**: …（若有 BVA）
**狀態轉移**: …（若有 State Transition）
**組合覆蓋**: …（Decision Table / pairwise）
**錯誤推測**: …（若有，≤2 條且附 `@guess_reason`）

**Examples 規劃**（每行對應一個測試案例）:

| # | 驗證目標 | DSL Entry | Binding Keys | 額外前置狀態 | 輸入資料摘要 | 預期結果 | 分析維度 |
|---|---------|-----------|--------------|-------------|-------------|---------|---------|
| 1 | … | dsl-... | customer_id, ... | （無）/ 需先 xxx | … | 成功 / 失敗(VIOLATION) | 等價類 / 邊界值 / … |

> `Binding Keys` 必須來自 matching DSL entry 的 L4 bindings；若需要的輸入或斷言不在 DSL / OpenAPI / DBML truth 中，標 CiC(GAP) 回 `/aibdd-plan`，不可在本 skill 補 mapping。

> **「額外前置狀態」欄位是 Scenario 結構決策的關鍵輸入。**
> 「（無）」表示 Background 即足夠。有值表示該行需要獨立的 Given 區塊，
> **不得**與「（無）」的行合併為同一個 Scenario Outline（見 RP-04 Step 1b）。
