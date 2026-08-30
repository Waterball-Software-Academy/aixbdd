# Rule 1 - 高影響未定事項必須就地標記 `# [need clarification]`

- Level: `MUST`
- 任何會改變 Journey 走向、驗收結果、規則歸屬、切檔方式或成功標準的未定事項，都必須標在對應 feature 的規則或步驟旁。
- 標記格式固定為 `# [need clarification] ...`，不可改成其他拼法或藏在檔尾摘要。
- 標記應盡量靠近引發疑問的那一行業務規則或步驟，讓使用者能直接看到問題上下文。
- 不可為了安置 `# [need clarification]`，額外新增一段本來不需要的 `Background`。

## Good Example

- 這個例子是好的，因為問題就貼在付款期限規則旁，讀者立刻知道哪裡還沒拍板。

```gherkin
Rule: 訂單成立後必須先保留庫存並等待付款結果

  Example: 首購會員逾時未付款後訂單取消且資源回復
    Given 商店提供以下結帳規則：
      | 規則     | 內容      |
      | 付款期限 | 15 分鐘   |
    # [need clarification] 付款期限是從「送出訂單」開始計時，還是從「進入付款頁」後開始計時？
    When "Alice" 確認送出訂單
```

## Bad Example

- 這個例子是壞的，因為疑點被藏在檔尾，讀者無法對照到具體規則位置。

```gherkin
Feature: 訂單成立與付款超時

  Rule: 訂單成立後必須先保留庫存並等待付款結果

    Example: 首購會員逾時未付款後訂單取消且資源回復
      When 該筆訂單超過付款期限仍未完成付款
      Then 訂單狀態為 "已取消"

# [need clarification] 上面有幾個地方之後再問
```

# Rule 2 - 先產出 Gherkin 與標記，再立刻升級 `/clarify`

- Level: `MUST`
- `spec-by-example` 必須先把 acceptance feature files 與 `# [need clarification]` 寫出來，讓疑點落在具體 artifact 上。
- 完成標記後，只要仍有高影響缺口，就必須立刻委派 `/clarify`，不得拖到後續 skill 或實作階段才問。
- 不得在還沒落位到 feature files 前就直接把模糊需求口頭丟給 `/clarify`。

## Good Example

- 這個例子是好的，因為先把問題落在 feature file，再立刻把最高影響疑點交給 `/clarify`。

```text
1. 先寫入 features/acceptance/訂單成立與付款超時.feature
2. 在付款期限旁標記 # [need clarification] ...
3. 立刻呼叫 /clarify 追問付款期限起算點
```

## Bad Example

- 這個例子是壞的，因為還沒形成 artifact 就先抽象提問，後續也無法明確回寫。

```text
1. 讀到 spec.md 後覺得哪裡怪怪的
2. 直接問使用者很多模糊問題
3. 等回答完才決定 feature files 要怎麼寫
```

# Rule 3 - `/clarify` 每輪只追最高影響的 1 至 3 題

- Level: `MUST`
- handoff 給 `/clarify` 時，必須先依 acceptance 影響程度排序，只交出本輪最需要先拍板的 1 至 3 題。
- 排序優先看：是否改變驗收結果、是否改變 Journey 分支、是否改變 feature 切檔或 Rule 歸屬。
- 不可把所有局部疑點一次傾倒給使用者，避免 clarify session 失焦。

## Good Example

- 這個例子是好的，因為只先問最影響規則與結果的幾題。

```text
本輪 /clarify：
1. 付款期限從哪個時間點開始算？
2. 免運門檻是看哪一層折後金額？
3. 互斥優惠是拒絕還是允許取代既有優惠？
```

## Bad Example

- 這個例子是壞的，因為把高低影響問題混在一起，且一次問太多。

```text
本輪 /clarify：
1. 付款期限怎麼算？
2. 表格裡「值」這個欄名要不要換字？
3. 離島怎麼定義？
4. 贈品文案要不要加全形括號？
5. 免運門檻怎麼算？
6. 顏色名稱要寫黑色還是墨黑？
```

# Rule 4 - 高影響缺口不得用腦補補完

- Level: `MUST`
- 若某個缺口會改變驗收標準或流程走向，在 `/clarify` 回答前不得自行假設答案並寫成既定規則。
- 在回答未回來前，可以先保留 `# [need clarification]` 與暫時性的 feature 結構，但不可把猜測偽裝成已確認需求。
- 只有不影響主要驗收判斷的局部細節，才可在回寫後繼續保留為後續處理事項。

## Good Example

- 這個例子是好的，因為它保留未定疑點，而沒有偷塞一個假設答案。

```gherkin
# [need clarification] 贈品門檻是看活動商品小計、套用折扣後金額，還是最後應付總額？
And 商店規定贈品資格會隨購物車內容即時更新
```

## Bad Example

- 這個例子是壞的，因為作者自行假設規則，之後即使使用者不同意，也很難追溯。

```gherkin
And 商店規定贈品門檻一定只看最後應付總額
```

# Rule 5 - 不要為低影響措辭差異濫貼標記

- Level: `SHOULD`
- `# [need clarification]` 應聚焦高影響業務缺口，不要把純文案偏好、欄位命名偏好或可晚點處理的小修飾都升級成 clarify。
- 若問題不影響驗收案例走法，只需在回寫時自行收斂，不必打斷 `/clarify`。

## Good Example

- 這個例子是好的，因為它只標記會影響配送規則的問題。

```gherkin
# [need clarification] 哪些行政區算「離島」，是固定清單，還是依物流商可配送範圍決定？
Given 商店提供以下配送規則：
```

## Bad Example

- 這個例子是壞的，因為它把低影響的措辭偏好也升級成 clarify。

```gherkin
# [need clarification] 「商品小計」要不要改成「商品金額小計」？
Then 訂單摘要如下：
```
