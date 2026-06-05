# Pattern Key 檢核清單（業務語言版）

- 每個 Example 必須體現其 pattern 之必填元素全集；禁止缺項。
- 檢核僅當讀已寫入之 Example 文字；禁止自行補完缺項（補完是 phase 2 的職責）。
- 缺項者必須標記 `$validation_failures` 並回 phase 2 重寫；禁止在本 phase UPDATE。
- 元素「存在」之判斷僅看字面是否出現該名詞或對應動詞；不得做語意推測來代答。
- 額外檢核業務語言判準：依 `../02-expand-each-rule/rules/business-language-judgments.md` 之 5 維度（識別／狀態值／資料量／動詞／結果描述）逐項核對；任一維度違規必須標 failure。

## 各 pattern 必填元素

### PATTERN_A_PRECONDITION_INPUT

- `$actor`: Given 與 When 區皆出現人物名（如 `"Alice"`），不得為 `"user-XXX"` 技術 ID
- `$aggregate`: Given 區出現業務序號（如 訂單 `"#001"`），不得為 `"order-XXX"` 技術 ID
- `$command`: When 區出現顧客視角動詞（按下、選擇），不得為 API 視角（執行、呼叫）
- `$input`（缺漏）: When 區出現「沒選／沒填／但沒…」之業務化缺漏描述
- 業務面失敗描述: Then 區出現「…沒有成功」等業務化失敗詞，不得為「操作失敗」
- 系統提示: Then 區出現 `系統提示 "<訊息>"`
- 系統狀態不變: Then 區出現 `<aggregate> 沒被改動` 或 `<aggregate> 仍是 "<原狀態>"`

### PATTERN_B_PRECONDITION_STATE

- `$actor`: 同 PATTERN_A
- `$aggregate`（含不合條件狀態）: Given 區出現「`<$aggregate>` 處於 `<業務狀態>`」，狀態用中文業務詞
- `$command`: 同 PATTERN_A
- 業務面失敗描述: 同 PATTERN_A
- 系統提示: 同 PATTERN_A
- Aggregate 維持原狀: Then 區出現 `<aggregate> 維持 "<原狀態>"`

### PATTERN_C_POSTCONDITION_STATE

- `$actor`: 同 PATTERN_A
- `$aggregate`（初始）: Given 區出現業務序號 + 初始業務狀態
- `$command`: When 區顧客視角動詞
- `$aggregate`（變更後）: Then 區出現 `<aggregate> 變成 "<業務面新狀態>"`，不得為 `變更為 "CHECKED_OUT"`
- `$event`: Then 區出現 `系統發出 "<業務化通知>"`（可接給 `"<actor>"`），不得為 `產生 "OrderCheckedOut" 事件` 等 class 名

### PATTERN_D_POSTCONDITION_RESPONSE

- `$actor`: 同 PATTERN_A
- `$aggregate`（初始）: Given 區出現業務序號 + 業務狀態
- `$query`: When 區出現顧客視角查詢動詞（查詢、查看）
- 業務面回應內容: Then 區出現 `<actor> 看到 <欄位:值>`，不得為 JSON / DTO / HTTP body

## Good

- PATTERN_A：When 寫 `"Alice" 按下結帳，但沒選擇要結帳哪一筆訂單` → 覆蓋 `$actor` + `$command` + `$input` 缺漏，且全為業務語言。
- PATTERN_C：Then 包含 `訂單 "#001" 變成 "已結帳"` + `系統發出 "結帳完成通知" 給 "Alice"` → 同時覆蓋變更後狀態與業務化事件。

## Bad

- PATTERN_A：When 寫 `顧客 "user-001" 執行結帳，未指明 結帳目標訂單編號` → `$actor` 用技術 ID、`$command` 用 API 視角動詞、缺漏描述非業務化；必須標 failure（業務語言 3 處違規）。
- PATTERN_A：Then 只寫 `操作失敗` → 缺業務化失敗描述、缺系統提示、缺系統狀態不變；必須標 failure（3 項缺漏）。
- PATTERN_C：Then 寫 `產生 "OrderCheckedOut" 事件` → event 用 class 名非業務語言；必須標 failure 並回 phase 2 業務化命名。
- PATTERN_D：Then 出現 `產生 "..." 事件` 或 `系統發出 "..."` → 違反 PATTERN_D 不發事件規則；必須標 failure 並回 phase 2 重產（疑似套錯模板）。
- PATTERN_D：Then 寫 `回應 { "amount": 900 }` → JSON 結構非業務語言；必須標 failure 並回 phase 2 改為 `"Alice" 看到 ...` 業務化敘述。
