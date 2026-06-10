# Pattern A — 前置（參數）失敗｜業務語言 + 類型前綴版

驗證面向：輸入參數缺漏或不合法，動作還沒打到 Aggregate 就被擋下
引導一句話：哪個輸入沒選／沒填？
類型前綴：`前置（參數）`
必填元素：`$actor` / `$aggregate` / `$command` / `$input`（缺漏） / 業務面失敗描述 / 系統提示 / 系統狀態不變

## Given/When/Then 骨架

```gherkin
Rule: 前置（參數） - <業務面 must>
  Example: "<$actor>" <業務動作>但<沒帶業務化的 input>，<業務面結果失敗>
    Given "<$actor>" 有 <$aggregate 業務描述>
    When  "<$actor>" <$command>，但<業務化的輸入缺漏描述>
    Then  <業務面失敗描述>
    And 系統提示 "<$actor 看到的訊息>"
    And <$aggregate> 沒被改動
```

## Placeholder 替換規則

### `<$actor>`

- 替換來源: `$five_elements.actor`
- 業務語言判準: 用人物名（顧客 Alice），禁止技術 ID（user-001）

### `<$aggregate>`

- 替換來源: `$five_elements.aggregate` + 業務化序號
- 業務語言判準: 用業務序號（訂單 2406KX8Q7M2P9T），禁止技術 ID（order-001）

### `<$command>`

- 替換來源: `$five_elements.command`
- 業務語言判準: 用顧客視角動詞（按下結帳），禁止 API 視角（執行結帳、呼叫 API）

### `<$input>`

- 替換來源: `$five_elements.input` 的業務化描述
- 業務語言判準: 用「沒選／沒填」，禁止「未指明／傳入」

### `<$aggregate 業務描述>`

- 替換來源: 自由文（金額、狀態）
- 業務語言判準: 狀態值用中文（處理中），禁止 enum 英文（process）

### `<業務面失敗描述>`

- 替換來源: 對應 Rule 的失敗
- 業務語言判準: 用「結帳沒有成功」，禁止「操作失敗」

### `<$actor 看到的訊息>`

- 替換來源: 用戶補問或自由文
- 業務語言判準: 必為顧客視角能看到的字串訊息

## Good

```gherkin
Rule: 前置（參數） - 結帳必須先選擇要結帳的訂單

  Example: "Alice" 按下結帳但沒選訂單，結帳沒成功
    Given "Alice" 有一筆處理中的訂單 "2406KX8Q7M2P9T"，金額 1000 元
    When  "Alice" 按下結帳，但沒選擇要結帳哪一筆訂單
    Then  結帳沒有成功
    And 系統提示 "請選擇要結帳的訂單"
    And 訂單 "2406KX8Q7M2P9T" 仍是 "處理中"
```

## Bad

```gherkin
# Bad 1：技術 ID + 英文 enum
Given 顧客 "user-001"
  And 訂單 "order-001" 狀態為 "process"

# Bad 2：API 視角動詞
When 顧客 "user-001" 執行結帳，未指明 結帳目標訂單編號

# Bad 3：失敗無業務描述
Then 操作失敗
```
