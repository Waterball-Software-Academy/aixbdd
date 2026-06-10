# Pattern C — 後置（狀態）成功（Command 型）｜業務語言 + 類型前綴版

驗證面向：狀態變更 + 事件發出（滿足前提時走完整流程）
引導一句話：操作成功後，業務實體變成什麼樣？系統發出什麼通知？
類型前綴：`後置（狀態）`
必填元素：`$actor` / `$aggregate`（初始業務狀態） / `$command` / `$aggregate`（變更後業務狀態） / `$event`（業務化的通知）

## Given/When/Then 骨架

```gherkin
Rule: 後置（狀態） - <業務面 should>
  Example: "<$actor>" <業務動作>成功，"<$aggregate>" 變成<業務面新狀態>並<系統通知>
    Given "<$actor>" 有 <$aggregate 滿足前提的業務狀態>
    When  "<$actor>" <$command>
    Then  <$aggregate> 變成 "<業務面新狀態>"
    And 系統發出 "<$event 業務化通知>" 給 "<$actor>"
```

## Placeholder 替換規則

### `<$actor>`

- 替換來源: `$five_elements.actor`
- 業務語言判準: 用人物名（顧客 Alice），禁止技術 ID

### `<$aggregate>`

- 替換來源: `$five_elements.aggregate` + 業務化序號
- 業務語言判準: 用業務序號（訂單 2406KX8Q7M2P9T），禁止技術 ID

### `<$command>`

- 替換來源: `$five_elements.command`
- 業務語言判準: 顧客視角動詞，禁止 API 視角

### `<業務面新狀態>`

- 替換來源: Rule 標題「應」後的結果文字（業務化改寫）
- 業務語言判準: 中文業務狀態詞（已結帳、已折抵），禁止 enum

### `<$event 業務化通知>`

- 替換來源: `$five_elements.event` 業務化命名
- 業務語言判準: 用業務人員看得懂的通知名（結帳完成通知），禁止 event class 名（OrderCheckedOut）

### `<滿足前提的業務狀態>`

- 替換來源: 用戶補問後填入
- 業務語言判準: 中文業務狀態詞

## Good

```gherkin
Rule: 後置（狀態） - 處理中的訂單按下結帳後應變成已結帳並通知顧客

  Example: "Alice" 按下結帳，訂單變成已結帳並收到通知
    Given "Alice" 有一筆處理中的訂單 "2406KX8Q7M2P9T"，金額 1000 元
    When  "Alice" 對訂單 "2406KX8Q7M2P9T" 按下結帳
    Then  訂單 "2406KX8Q7M2P9T" 變成 "已結帳"，金額 1000 元
    And 系統發出 "結帳完成通知" 給 "Alice"
```

## Bad

```gherkin
# Bad 1：用 event class 名（技術氣味）
And 產生 "OrderCheckedOut" 事件

# Bad 2：用英文 enum 新狀態
Then 訂單 "2406KX8Q7M2P9T" 變更為 "CHECKED_OUT"

# Bad 3：缺事件斷言（C 必檢）
Then 訂單 "2406KX8Q7M2P9T" 變成 "已結帳"
# ← 缺 And 系統發出 "..."
```
