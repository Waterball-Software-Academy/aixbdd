# Rule 1 - `spec-by-example` 只產總驗收層 Gherkin

- Level: `MUST`
- 這一層的產物是 spec package 內的 `features/acceptance/*.feature`。
- 此階段不得先拆成 `frontend` / `backend`，也不得同時產出 `dsl.md`。
- 句子只表達 PM 需要確認的驗收流程與業務結果，不提前混入實作層設計。

## Good Example

- 這個例子是好的，因為它只描述總驗收流程，沒有提早切成技術層 artifact。

```gherkin
Feature: 訂單成立與付款超時

  Rule: 待付款訂單逾時後必須取消並釋出資源

    Example: 首購會員逾時未付款後訂單取消且資源回復
      Given "Alice" 是首購會員
      When "Alice" 確認送出訂單
      Then 系統建立一筆待付款訂單給 "Alice"
      When 該筆訂單超過付款期限仍未完成付款
      Then 訂單狀態為 "已取消"
```

## Bad Example

- 這個例子是壞的，因為它在同一階段提前拆到前後端與 DSL。

```text
features/backend/訂單/訂單成立與付款超時.feature
features/frontend/訂單/訂單成立與付款超時.feature
features/backend/dsl.md
features/frontend/dsl.md
```

# Rule 2 - `Example` 必須以 Journey 顆粒度描述驗收流程

- Level: `MUST`
- 每個 `Example` 應優先描述一條可 demo 的長流程，而不是拆成很多微小操作測試。
- 案例數量應少於實作層測試，只保留主流程與少數高差異變種。
- 若一條 Journey 仍可自然閱讀，就不應為了實作方便過早切碎。

## Good Example

- 這個例子是好的，因為它把建立訂單、保留庫存、付款結果與後續狀態放在同一條驗收旅程中。

```gherkin
Example: 限量商品先保留庫存，逾時後下一位會員可重新下單
  Given "Alice" 的購物車中有 2 雙限量球鞋
  And "Bob" 的購物車中有 1 雙限量球鞋
  When "Alice" 確認送出訂單
  Then 系統建立一筆待付款訂單給 "Alice"
  When "Bob" 嘗試確認送出訂單
  Then 這次操作被拒絕
  When "Alice" 的訂單超過付款期限仍未完成付款
  Then 商品可賣庫存恢復
  When "Bob" 再次確認送出訂單
  Then 系統建立一筆待付款訂單給 "Bob"
```

## Bad Example

- 這個例子是壞的，因為它把同一條驗收旅程拆成過多微小案例，失去 PM demo 的價值。

```gherkin
Example: 建立待付款訂單
  When "Alice" 確認送出訂單
  Then 系統建立一筆待付款訂單給 "Alice"

Example: Bob 被拒絕
  When "Bob" 嘗試確認送出訂單
  Then 這次操作被拒絕

Example: Alice 逾時取消
  When "Alice" 的訂單超過付款期限仍未完成付款
  Then 商品可賣庫存恢復
```

# Rule 3 - Gherkin 句型只講業務語意

- Level: `MUST`
- 不可在 step 中暴露 API、HTTP method、資料表、selector、fixture 名稱或其他技術細節。
- 驗收層應讓 PM、需求方與測試作者都能直接閱讀，不需先理解系統內部實作。
- 若某段句子只對工程師有意義、對需求驗收沒有幫助，就不應出現在這一層。

## Good Example

- 這個例子是好的，因為它只描述會員能看到與需要確認的業務結果。

```gherkin
When "Alice" 套用折扣碼 "SPORT200"
Then 訂單摘要如下：
  | 項目     | 值   |
  | 訂單折抵 | 200  |
  | 應付總額 | 2920 |
```

## Bad Example

- 這個例子是壞的，因為它把技術實作細節直接暴露在驗收層。

```gherkin
When 前端呼叫 POST /api/orders/apply-coupon 並帶入 code "SPORT200"
Then response.status 應為 200
And order_summary.discount_amount 欄位應更新為 200
```

# Rule 4 - `Feature` / `Rule` / `Example` 應依驗收面向切分

- Level: `SHOULD`
- `Feature` 應聚焦單一 PM 關心的驗收主題，例如付款超時、運費判定或贈品資格。
- `Rule` 應保持原子；若 `Example` 標題聽起來像另一條規則，應拆出新的 `Rule` 或新的 feature file。
- `Example` 標題應描述資料情境或 journey 變種，而不是只重複 `Rule` 名稱。

## Good Example

- 這個例子是好的，因為 `Feature`、`Rule` 與 `Example` 各自承擔不同層次的驗收語意。

```gherkin
Feature: 滿額贈品與條件取消

  Rule: 達成門檻時必須自動帶入贈品，失去門檻時必須自動取消

    Example: 會員調整購物車後在贈品資格成立與失效之間來回切換
```

## Bad Example

- 這個例子是壞的，因為 `Example` 標題只是重複規則句，沒有提供情境資訊。

```gherkin
Feature: 滿額贈品與條件取消

  Rule: 達成門檻時必須自動帶入贈品，失去門檻時必須自動取消

    Example: 達成門檻時必須自動帶入贈品，失去門檻時必須自動取消
```

# Rule 5 - `Background` 只在多個 Example 真正共用測試語意時才保留

- Level: `MUST`
- `Background` 是可選結構，不是 acceptance feature 的預設起手式。
- 若一份 feature 只有單一 `Example`，預設應直接從 `Rule` / `Example` 起手，不要為了排版對稱硬補 `Background`。
- 只有當多個 `Example` 真的共用同一段帶測試語意的步驟，且抽出後能讓每條 Journey 更短、更清楚時，才應保留 `Background`。
- 不可把 `spec.md` 已知規則、產品世界觀、全域規則導讀，或只是為了介紹功能背景的敘述塞進 `Background`。
- 若抽出 `Background` 反而讓讀者必須來回跳讀，才能拼回完整 Journey，應改回各自 `Example` 內的 `Given` / `And`。

## Good Example

- 這個例子是好的，因為同一份 feature 有兩個 `Example` 共用相同的商品、結帳規則與優惠設定，抽成 `Background` 後能縮短重複步驟，且仍保留明確測試語意。

```gherkin
Feature: 訂單成立與付款超時

  Background:
    Given 商店有以下可販售商品：
      | 商品       | 規格   | 單價 | 可賣庫存 |
      | 防潑水外套 | 黑色 M | 1280 | 5        |
      | 吸排長褲   | 黑色 L | 980  | 5        |
    And 商店提供以下結帳規則：
      | 規則         | 內容      |
      | 宅配運費     | 80        |
      | 付款期限     | 15 分鐘   |
    And 商店提供折扣碼 "NEW100" 給首購會員使用

  Rule: 訂單成立後必須先保留庫存並等待付款結果

    Example: 首購會員在付款期限內完成付款
      Given "Alice" 是首購會員
      When "Alice" 確認送出訂單
      Then 系統建立一筆待付款訂單給 "Alice"

    Example: 首購會員逾時未付款後訂單取消
      Given "Alice" 是首購會員
      When "Alice" 確認送出訂單
      Then 系統建立一筆待付款訂單給 "Alice"
```

## Bad Example

- 這個例子是壞的，因為這份 feature 只有單一 `Example`，而 `Background` 只是把活動規則重新介紹一次，沒有幫助 Journey 更清楚。

```gherkin
Feature: 滿額贈品與條件取消

  Background:
    Given 商店提供以下贈品活動：
      | 活動名稱   | 條件                | 贈品          |
      | 春季滿額贈 | 活動商品小計滿 3000 | 保冷提袋 1 個 |
    And 商店規定贈品資格會隨購物車內容即時更新

  Rule: 達成門檻時必須自動帶入贈品，失去門檻時必須自動取消

    Example: 會員調整購物車後在贈品資格成立與失效之間來回切換
      Given "Alice" 的購物車中有以下商品：
        | 商品       | 類別     | 單價 | 數量 |
        | 旅行後背包 | 活動商品 | 1680 | 1    |
```
