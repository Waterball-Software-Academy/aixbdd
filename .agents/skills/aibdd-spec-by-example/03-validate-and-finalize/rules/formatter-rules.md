# Formatter 檢核規則（含類型前綴）

- 每個 Example 必須符合 Gherkin 語法與本檔列出之版面慣例；禁止僅靠人眼判讀。
- 檢核僅當讀已寫入之 Example 文字逐項比對；禁止自動修補（修補是 phase 2 的職責）。
- 違規項必須逐條記入 `$validation_failures.formatter_issues`；禁止只記「格式錯誤」籠統描述。
- Cucumber 引號、`And` 縮排、step 內「」：不在本檔檢核；僅由同 phase `SOP.md` 步驟 4 與 `cucumber-literal-format.md` 負責。

## 必檢項目

- 類型前綴：`Rule:` 標題必為以封閉 4-類型前綴之一（`前置（參數）`／`前置（狀態）`／`後置（狀態）`／`後置（回應）`）開頭、以 ` - ` 與業務標題分隔；禁止省略前綴、禁止前綴不在封閉 4 類、禁止把前綴寫進 Example 標題（前綴僅屬 Rule 標題層）。
- 關鍵字順序：Example 內必為 `Given` → `When` → `Then` 順序；`And` 僅當跟在前一個 Given/When/Then 之後。
- 空行分隔：Rule 之間必為至少一空行；Example 與下一 Rule 之間必為至少一空行；Given/When/Then/And 之間不得有空行。
- Example 標題：必為 `Example: <情境描述>` 格式；情境描述不得為純關鍵字堆疊，必為含逗號或語句結構的自然句，且必為業務語言（依 `../../02-expand-each-rule/rules/business-language-judgments.md`）。
- 取捨註解：若 Example 上方有 `# 取捨：...` 註解，必為緊貼 Example 之上一行，且註解之前必為空行。
- 中文標點：When/Then 句內若有並列短語，必為以全形逗號「，」分隔；禁止多個短語並列無連接。
- 高參數 step：單一 Given/When/Then/And 若承載超過 4 個可綁定參數，必須依 `cucumber-literal-format.md` 改寫為 Data Table；本檔只檢核版面分隔，參數計數與 Data Table 字面規則由 `cucumber-literal-format.md` 負責。

## Good

```gherkin
Rule: 前置（參數） - 結帳必須先選擇要結帳的訂單

  Example: "Alice" 按下結帳但沒選訂單，結帳沒成功
    Given 顧客 "Alice" 有一筆處理中的訂單 "2406KX8Q7M2P9T"，金額 1000 元
    When  "Alice" 按下結帳，但沒選擇要結帳哪一筆訂單
    Then  結帳沒有成功
    And 系統提示 "請選擇要結帳的訂單"
    And 訂單 "2406KX8Q7M2P9T" 仍是 "處理中"
```

- 類型前綴在 Rule 標題開頭、以 ` - ` 分隔業務標題
- Example 標題不含類型前綴
- Example 縮排與 Rule 同階
- 標題自然句、業務語言、全形逗號分隔並列語
- 引號與 `And` 對齊：見 `cucumber-literal-format.md` 步驟 4 檢核

## Bad

```gherkin
# Bad 1：缺類型前綴
Rule: 結帳必須先選擇要結帳的訂單
```

→ 缺前綴，pattern 無法分類。

```gherkin
# Bad 2：前綴不在封閉 4 類
Rule: 中置（條件） - 套用優惠中
```

→ `中置（條件）` 不在 4-pattern 對應表，pattern 無法分類；必須回 phase 1 DELEGATE 補上合法前綴。

```gherkin
# Bad 3：前綴誤寫進 Example 標題
Rule: 前置（參數） - 結帳必須先選擇要結帳的訂單

  Example: 前置（參數） - Alice 按下結帳但沒選訂單
```

→ 前綴僅屬 Rule 標題層，Example 標題不得重複前綴。

- 標題：`Example: 顧客 未指名 結帳目標訂單 結帳失敗` ← 純關鍵字堆疊、typo
- When：`When 顧客 執行結帳 未指明 結帳目標訂單編號` ← 短語無逗號
- 標題滲入技術 ID：`Example: user-001 結帳失敗` ← 業務語言違規（識別維度）；若保留 ID 須在步驟 4 寫 `"user-001"`
