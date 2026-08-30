# Rule 1 - `Wave` 執行順序必須服從 `plan.md`

- Level: `MUST`
- `system-analysis` 在委派各 planner skill 時，必須依 `plan.md` 已定義的 `Wave` 順序執行，不可因為某個 planner 看起來能先做，就跳過前一波直接啟動後一波。
- 同一個 `Wave` 內允許平行委派，但前提是這些介面在 `plan.md` 中已被判定為可平行分析。
- 若某 planner 的分析明顯依賴前一個 `Wave` 才會產生的資訊，則必須等前一個 `Wave` 完成後再委派。

## Good Example

- 這個例子是好的，因為 UI Prototyping 已在上游完成，system-analysis 只把前端 artifact review 與後端分析依賴排進 Wave，不重新委派 `/ui-plan`。

```md
#### Wave 1

- review：
  - `ui/ui-plan.md`
  - `ui/room.html`
  - `ui/game.html`

#### Wave 2

- 平行分析介面：
  - `後端房間與對戰 API 介面`

執行順序：
1. 先確認 UI artifact 的互動入口、狀態與錯誤回饋可落地
2. 等 Wave 1 完成後，再呼叫 `/api-plan`
```

## Bad Example

- 這個例子是壞的，因為它在 system-analysis 階段重新呼叫 `/ui-plan`，把已完成的 Prototyping 責任移回系統分析。

```md
#### Wave 1

- 呼叫 `/api-plan`

#### Wave 2

- 發現缺少前端狀態後，再呼叫 `/ui-plan` 重做畫面流程
```

# Rule 2 - planner 對應必須依分析責任邊界決定

- Level: `MUST`
- `system-analysis` 必須依每個系統介面的主要分析責任與產物邊界決定委派對象，而不是只看名稱中是否出現某個技術詞。
- 玩家可見流程、畫面狀態、互動節奏、資訊揭露與錯誤回饋，應讀取 plan package 內已完成的 UI plan 與靜態雛形；若缺漏會改變需求，回交 `/ui-plan`，不得由 `system-analysis` 直接重做。
- 實體、欄位、狀態持有、生命週期、資料關聯與儲存責任，應委派給 `/data-plan`。
- API 契約、事件協議、請求回應形狀、狀態轉移入口與錯誤碼語意，應委派給 `/api-plan`。
- 若某個後端介面同時涉及多種責任，應回到 `plan.md` 的介面切分重新判斷是否需要拆分，而不是把同一介面同時丟給多個 planner。

## Good Example

- 這個例子是好的，因為它是依分析責任分流，而不是先看技術名稱。

```md
1. `前端配對與對戰介面`
   - 主要介面：畫面狀態、角色標示、操作回饋
   - review：既有 `ui/ui-plan.md` 與靜態雛形
   - 若不一致：回交 `/ui-plan`

2. `房間與對戰狀態資料介面`
   - 主要介面：Room、Game、Guess 狀態持有與生命週期
   - 委派：`/data-plan`

3. `後端即時事件契約介面`
   - 主要介面：join/create、ready、start、guess、broadcast
   - 委派：`/api-plan`
```

## Bad Example

- 這個例子是壞的，因為它把同一個介面重複丟給多個 planner，且分流理由只來自技術詞，不是責任邊界。

```md
1. `前端配對與對戰介面`
   - 委派：`/api-plan`
   - 同時直接修改 `ui/ui-plan.md`
   - 理由：system-analysis 可以順手修 UI
```

# Rule 3 - 共用主產物邊界的同 wave 介面應優先合併 handoff

- Level: `SHOULD`
- 若同一個 `Wave` 內有多個系統介面最終都會寫入同一份主產物，應優先合併成一次委派，避免同一 planner 在同一 feature 中重複覆寫同一檔案。
- 合併 handoff 時，必須在委派內容中列出所有被合併的介面名稱、各自分析重點與它們共享的產物邊界。
- 只有在兩個介面雖指向同一 planner，但產物邊界明顯獨立時，才適合拆成多次委派。

## Good Example

- 這個例子是好的，因為它把同一波內都屬於後端契約的兩個介面合併交給同一個 planner，一次產出同一組 `contracts/` artifact。

```md
#### Wave 2

- 平行分析介面：
  - `後端房間事件契約介面`
  - `後端對戰事件契約介面`

委派：
- 單次呼叫 `/api-plan`
- prompt 內同時列出兩個介面與各自分析重點
- 共用主產物：`contracts/openapi.yaml`
```

## Bad Example

- 這個例子是壞的，因為它讓同一個 planner 在沒有新邊界的情況下重複覆寫同一產物。

```md
#### Wave 2

- 平行分析介面：
  - `後端房間事件契約介面`
  - `後端對戰事件契約介面`

委派：
1. 呼叫 `/api-plan` 產出 `contracts/openapi.yaml`
2. 再呼叫 `/api-plan` 覆寫同一份 `contracts/openapi.yaml`
```
