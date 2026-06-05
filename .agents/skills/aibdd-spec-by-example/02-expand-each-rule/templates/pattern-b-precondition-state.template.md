# Pattern B — 前置（狀態）失敗｜業務語言 + 類型前綴版

驗證面向：目標 Aggregate 狀態不滿足前提 → 動作打到了但被拒絕
引導一句話：目標業務實體處於什麼狀態時會被擋下？
類型前綴：`前置（狀態）`
必填元素：`$actor` / `$aggregate`（含業務面不滿足狀態） / `$command` / 業務面失敗描述 / 系統提示 / Aggregate 維持原狀

## Given/When/Then 骨架

```gherkin
Rule: 前置（狀態） - <業務面 must>
  Example: "<$aggregate>" 處於<不合條件狀態>，"<$actor>" 無法 <業務動作>
    Given "<$actor>" 有 <$aggregate 處於不合條件的業務狀態>
    When  "<$actor>" <$command>
    Then  <業務面失敗描述>
    And 系統提示 "<$actor 看到的訊息>"
    And <$aggregate> 維持 "<原業務狀態>"
```

## Placeholder 替換規則

### `<$actor>`

- 替換來源: `$five_elements.actor`
- 業務語言判準: 用人物名（顧客 Alice），禁止技術 ID

### `<$aggregate>`

- 替換來源: `$five_elements.aggregate` + 業務化序號
- 業務語言判準: 用業務序號（訂單 #001），禁止技術 ID

### `<$command>`

- 替換來源: `$five_elements.command`
- 業務語言判準: 顧客視角動詞，禁止 API 視角

### `<不合條件狀態>`

- 替換來源: 用戶補問後填入
- 業務語言判準: 中文業務狀態詞（已結帳、已取消），禁止 enum 英文

### `<業務面失敗描述>`

- 替換來源: 對應 Rule 的失敗
- 業務語言判準: 用「結帳沒有成功」，禁止「操作失敗」

### `<$actor 看到的訊息>`

- 替換來源: 用戶補問或自由文
- 業務語言判準: 必為顧客視角能看到的字串訊息

## Good

```gherkin
Rule: 前置（狀態） - 已結帳的訂單不能再次結帳

  Example: "Alice" 的訂單已結帳，無法再次按結帳
    Given "Alice" 有一筆已結帳的訂單 "#001"
    When  "Alice" 對訂單 "#001" 按下結帳
    Then  結帳沒有成功
    And 系統提示 "此訂單已完成結帳，無法重複操作"
    And 訂單 "#001" 維持 "已結帳"
```

## Bad

```gherkin
# Bad 1：英文 enum 狀態
Given 訂單 "order-001" 狀態為 "CHECKED_OUT"

# Bad 2：失敗無業務描述
Then 操作失敗（狀態必須為 PROCESS）

# Bad 3：缺維持原狀斷言（無法驗證副作用是否發生）
Then 結帳沒有成功
    And 系統提示 "..."
# ← 缺 And 訂單 "#001" 維持 "已結帳"
```
