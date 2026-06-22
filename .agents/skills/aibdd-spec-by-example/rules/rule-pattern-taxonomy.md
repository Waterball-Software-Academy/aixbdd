# Rule Pattern 分類規則（4-pattern taxonomy，類型前綴版）

- Rule 標題必須以 4 種 pattern 對應之「類型前綴」之一開頭，並以 ` - ` 與業務標題分隔；禁止省略前綴。
- 類型前綴與 pattern 的對應必須一對一固定，禁止自行新增或合併前綴。
- 同一條 Rule 不得橫跨多種 pattern；橫跨者必須拆成多條 atomic Rule，每條一個 pattern。
- Command 型操作僅當對應 pattern A / B / C；Query 型操作僅當對應 pattern A / B / D；禁止 Command 對應 D 或 Query 對應 C。
- 缺前綴、或前綴不在封閉 4 類者，禁止自行推測 pattern；必須 DELEGATE 詢問用戶補上對應類型前綴。

## 對應表（lock）

| 類型前綴 | Pattern 代號 | 驗證面向 | 成敗 |
|---|---|---|---|
| `前置（參數）` | `PATTERN_A_PRECONDITION_INPUT` | 輸入參數缺漏／不合法 | 失敗 |
| `前置（狀態）` | `PATTERN_B_PRECONDITION_STATE` | 目標 Aggregate 狀態不滿足前提 | 失敗 |
| `後置（狀態）` | `PATTERN_C_POSTCONDITION_STATE` | 狀態變更 + 事件發出 | 成功 |
| `後置（回應）` | `PATTERN_D_POSTCONDITION_RESPONSE` | 查詢回應內容正確 | 成功 |

## Good

```gherkin
Rule: 前置（參數） - 結帳必須先選擇要結帳的訂單
```

→ 對應 `PATTERN_A_PRECONDITION_INPUT`；前綴明確、業務標題清楚。

```gherkin
Rule: 前置（狀態） - 已結帳的訂單不能再次結帳
```

→ 對應 `PATTERN_B_PRECONDITION_STATE`。

```gherkin
Rule: 後置（狀態） - 處理中的訂單按下結帳後應變成已結帳並通知顧客
```

→ 對應 `PATTERN_C_POSTCONDITION_STATE`。

```gherkin
Rule: 後置（回應） - 成功查詢訂單應回應顧客看得到的訂單摘要
```

→ 對應 `PATTERN_D_POSTCONDITION_RESPONSE`。

## Bad

```gherkin
# Bad 1：沒帶類型前綴
Rule: 結帳必須先選擇要結帳的訂單
```

→ 缺前綴，禁止自行推測；必須 DELEGATE 詢問用戶補上對應類型前綴。

```gherkin
# Bad 2：標題橫跨兩面向
Rule: 前置（狀態） - 顧客必須處於結帳流程且訂單必須已綁定優惠券
```

→ 一條 Rule 含兩個業務前提，必須拆成兩條 atomic Rule，各自帶前綴。

```gherkin
# Bad 3：前綴不在封閉 4 類
Rule: 中置（條件） - 套用優惠中
```

→ `中置（條件）` 不在 4-pattern 對應表，禁止自行歸類；必須 DELEGATE 詢問用戶選用合法類型前綴。

```gherkin
# Bad 4：Command Rule 用 Query 前綴（語意衝突）
Rule: 後置（回應） - 處理中的訂單按下結帳後應變成已結帳
```

→ Command 操作（按下結帳）改變狀態，僅當對應 `後置（狀態）`；用 `後置（回應）` 是 pattern 混淆。
