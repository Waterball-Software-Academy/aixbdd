# Activity Action 顆粒度

本規則定義 `discovery.03-activity-analyze` 如何把自然語言中的使用者行為、產品系統反應、第三方服務互動，收斂成 Activity model 的 `Actor` 與 `Action`。

## 核心原則

Activity 不是循序圖。

- `Actor` 只代表 UI-facing 的外部使用者角色。
- `Action` 代表「由 UI-facing actor 從 UI 觸發的一個完整業務行動」。
- 該行動可以橫跨多個 product system / third-party system boundary。
- 跨 boundary 後完成的結果，屬於同一個 `Action` 的 postcondition，不拆成新的 Actor 或新的系統步驟。

## Actor 判斷

自然語言中出現一個候選參與者時：

1. 如果它是透過 UI 操作產品的人類 / 組織角色，才可成為 `Actor`。
2. 如果它是產品系統、自有後端、內部服務、排程器、worker、server、database，禁止成為 `Actor`。
3. 如果它是第三方系統，但不是本 Activity 的 UI-facing 觸發者，禁止成為 `Actor`；把它吸收到相關 `Action` 的 boundary / postcondition。
4. 如果找不到 UI-facing 觸發者，標成 `graph_gap`，不要用「系統」補洞。

## Action 判斷

一個 `Action` 必須同時滿足：

1. 有 UI-facing actor 觸發。
2. 名稱描述完整業務意圖，而不是內部技術步驟。
3. 包含使用者動作與使用者可觀察完成結果。
4. 如果產品系統或第三方服務參與處理，該處理結果以 postcondition 表達。

## 轉換範例

錯誤：把內部處理拆成循序圖。

```text
Action 1: 業務人員送出評級
Action 2: 系統計算風險分數
Action 3: 系統寫入 CRM
Action 4: 第三方通知服務寄信
```

正確：收斂成 UI-first 完整業務行動。

```text
Action: 業務人員送出客戶評級
Postcondition: 風險分數已計算、CRM 已更新、通知已送出或留下可追蹤狀態。
```

## Modeling 指引

- `Actor` 不收 product system / third-party system。
- `Action.name` 保留完整業務意圖。
- `Action.binds_feature` 指向描述該完整業務行動的 feature。
- system boundary、第三方互動、資料寫入、通知等只可成為該 feature / rule / postcondition 的內容，不可變成 Activity node。
