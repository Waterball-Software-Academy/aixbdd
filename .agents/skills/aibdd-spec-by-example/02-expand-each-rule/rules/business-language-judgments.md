# 業務語言判準（5 維度）

- Example 內每個 step 文字必為業務語言；禁止滲入技術 ID、英文 enum、API 視角動詞、HTTP 描述、JSON 結構。
- 「業務語言」之判準僅依下列 5 維度；其他模糊偏好（「讀起來順」「比較清楚」）不得作為通過依據。
- 違反任一維度必須回 phase 2 重產或補問用戶；禁止在 phase 3 自動修補（修補是 phase 2 職責）。

## 5 維度判準

### 識別

- 業務語言: 人物名字（顧客 Alice）、業務序號（訂單 #001）
- 技術氣味: 技術 ID（user-001、order-001、uuid）

### 狀態值

- 業務語言: 中文業務詞（處理中、已結帳、待付款）
- 技術氣味: 英文 enum（process、CHECKED_OUT、PENDING）

### 資料量

- 業務語言: 只放與規則相關的最少欄位
- 技術氣味: 把 Aggregate 全欄位（含 invariant 衍生值）都塞進來

### 動詞

- 業務語言: 顧客視角（按下、選擇、查詢、看到）
- 技術氣味: API 視角（執行、呼叫、傳入、提交、GET、POST）

### 結果描述

- 業務語言: 顧客看得到的（系統提示訊息、Alice 看到 ...）
- 技術氣味: 系統內部的（操作失敗、HTTP 400、return null、throw exception）

## Good

```gherkin
    Given 顧客 "Alice" 有一筆處理中的訂單 "#001"，金額 "1000" 元
    When  "Alice" 按下結帳，但沒選擇要結帳哪一筆訂單
    Then  結帳沒有成功
    And 系統提示 "請選擇要結帳的訂單"
    And 訂單 "#001" 仍是 "處理中"
```

- 識別: 人物名與業務序號語意為 Alice／#001，字面加 `"..."`
- 狀態: 中文「處理中」，字面加 `"..."`
- 資料量: 只放金額；動詞: 按下、選擇；結果: 系統提示訊息

## Bad

```gherkin
# Bad - 識別維度
Given 顧客 "user-001"
  And 訂單 "order-001"

# Bad - 狀態值維度
And 訂單 "order-001" 狀態為 "process"

# Bad - 資料量維度（塞入 invariant 衍生值）
| 訂單編號 | 顧客編號 | 訂單狀態 | 訂單金額 | 折抵金額 | 套用優惠 |
| order-001 | user-001 | process | 1000 | 100 | 100元促銷 |
# ← 折抵金額是系統算的，不該由 Given 手動 seed

# Bad - 動詞維度
When 顧客 "user-001" 執行結帳，未指明 order_id

# Bad - 結果描述維度
Then 操作失敗
  And HTTP status = 400
  And response body 為 { "error": "MISSING_PARAM" }
```

## 取捨：必填的技術 ID

當業務人員實際用該 ID 跟工程師溝通（例如客服查單時就是用 `order-001`），則 ID 即是業務語言；此時得保留，但必須加業務化敘述：

```gherkin
Given 顧客 "Alice" 有訂單 "order-001"（內部編號）狀態為 "處理中"
```

→ ID 保留作為定位用，業務敘述放在前後文。不得整句只有 ID 沒有業務文字。
