# Pattern D — 後置（回應）成功（Query 型）｜業務語言 + 類型前綴版

驗證面向：查詢回應的 Read Model 內容正確（不改狀態、不發事件）
引導一句話：查詢回應的內容長什麼樣？顧客看到什麼？
類型前綴：`後置（回應）`
必填元素：`$actor` / `$aggregate`（初始業務狀態） / `$query` / 業務面回應內容

## Given/When/Then 骨架

```gherkin
Rule: 後置（回應） - <成功查詢 should 回應業務面內容>
  Example: "<$actor>" 查詢 "<$aggregate>"，看到<業務面回應內容>
    Given "<$actor>" 有 <$aggregate 處於某業務狀態>
    When  "<$actor>" 查詢 <$aggregate>
    Then  "<$actor>" 看到 <業務面回應內容>
```

## Placeholder 替換規則

### `<$actor>`

- 替換來源: `$five_elements.actor`
- 業務語言判準: 用人物名（顧客 Alice），禁止技術 ID

### `<$aggregate>`

- 替換來源: `$five_elements.aggregate` + 業務化序號
- 業務語言判準: 用業務序號（訂單 2406KX8Q7M2P9T），禁止技術 ID

### `<$query>`

- 替換來源: `$five_elements.command`
- 業務語言判準: 顧客視角動詞（查詢、查看），禁止 API 視角（GET、呼叫）

### `<業務面回應內容>`

- 替換來源: `$five_elements.event` 的業務化描述
- 業務語言判準: 顧客看得到的欄位與值（金額 900 元、已折抵 100 元），禁止 JSON / DTO 結構

### `<某業務狀態>`

- 替換來源: 用戶補問後填入
- 業務語言判準: 中文業務狀態詞

## 嚴禁元素

- 不得出現 `Then <Aggregate> 變成 ...`（查詢不改狀態）
- 不得出現 `And 系統發出 "..."`（查詢不發事件）
- 不得出現 `200 OK` / `HTTP status` / JSON schema 等技術描述
- 出現上述任一行視為混入 Pattern C 模板或技術氣味，必須回退重產。

## Good

```gherkin
Rule: 後置（回應） - 成功查詢訂單應回應顧客看得到的訂單摘要

  Example: "Alice" 查詢訂單，看到金額與折抵資訊
    Given 顧客 "Alice" 有一筆處理中的訂單 "2406KX8Q7M2P9T"，金額 1000 元，已套用 "100元促銷" 優惠券
    When  "Alice" 查詢訂單 "2406KX8Q7M2P9T"
    Then  "Alice" 看到訂單摘要：
      | 訂單           | 狀態   | 商品總額 | 折抵金額 | 應付金額 |
      | 2406KX8Q7M2P9T | 處理中 | 1000 元  | 100 元   | 900 元   |
```

## Bad

```gherkin
# Bad 1：JSON / DTO 描述
Then 回應 { "orderId": "order-001", "amount": 900 }

# Bad 2：HTTP 技術描述
Then 回應 HTTP 200，body 包含 amount=900

# Bad 3：誤帶事件斷言（混入 Pattern C）
Then "Alice" 看到訂單摘要 ...
  And 系統發出 "查詢完成" 通知  ← 查詢不發事件
```
