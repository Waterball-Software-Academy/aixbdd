# Rule 1 - 同一次 invocation 可推進多個 slices，但同一時刻只能處理一個 slice

- Level: `MUST`
- `/bdd` 雖可在使用者指定的單一介面 `feature file` 或其明確區塊內 sequentially 推進多個 slices，但任何時刻都只能鎖定一個當前 slice。
- 不可把多個 slices 打包成同一輪同時寫碼、同時驗證，只因為它們看起來共用同一批 step 或頁面。
- 只有當前 slice 已達成該入口的完成條件，才可選下一個 slice。

## Good Example

- 這個例子是好的，因為它允許在同範疇內持續前進，但每次只讓一個 slice 驅動當前修改。

```md
本輪範疇：
- `features/frontend/三連猜/對戰頁三連猜選擇與一次出手.feature`

推進順序：
1. 先處理「玩家已選滿三個數字」slice
2. 該 slice 完成本輪 `green` 後
3. 才切到「送出後按鈕禁用」slice
```

## Bad Example

- 這個例子是壞的，因為它把多個獨立行為混成一輪，失去局部回饋。

```md
本輪處理：
- 一次把三個 Rule 下的五個 slices 全部補碼
- 最後再一起跑測試
```

# Rule 2 - 下一個 slice 必須優先能形成最小且獨立的回饋

- Level: `MUST`
- 在指定範疇內選擇下一個 slice 時，優先考慮哪一個行為能以最小增量形成獨立的紅綠回饋，而不是哪一個一次能順手帶出最多能力。
- 若某個 slice 依賴前置基礎能力，應先選能建立該基礎能力的最小驅動 slice。
- 不可為了後面多個 slices 的方便，一開始就鋪設大量尚未被當前 slice 驅動的抽象層。

## Good Example

- 這個例子是好的，因為它先讓最小行為站穩，再疊下一個差異。

```md
同一範疇下的 slices：
1. 玩家選滿三個數字後可按送出
2. 送出後同回合不可再次送出
3. 換手後對手可送出

推進順序：
1 -> 2 -> 3
```

## Bad Example

- 這個例子是壞的，因為它先做通用框架，卻沒有任何 slice 先得到獨立訊號。

```md
先做：
- 通用 turn engine
- 通用 submit policy matrix
- 通用 guess permission framework

之後再回來跑第一個 slice
```

# Rule 3 - 不可跨出使用者指定範疇去吸收相鄰需求

- Level: `MUST`
- 當前 invocation 只可推進屬於指定 `feature file` 或其明確區塊的 slices。
- 若在實作途中發現相鄰 `Rule`、其他介面檔或其他 `feature files` 也會受影響，除非當前 slice 無法在原範疇內成立，否則不應順手擴張 scope。
- 若確實需要跨範疇修改才能讓目前 slice 成立，應停止並回報原因，讓使用者重新拍板範疇或回交上游。

## Good Example

- 這個例子是好的，因為它把 scope guard 視為真正的停止條件。

```md
觀察：
- 當前 frontend slice 可在既有 API mock 下完成
- backend 另一份 feature 也可能之後要補，但目前不是阻塞

處理：
- 只完成 frontend 這個 slice
- 不主動切去 backend feature
```

## Bad Example

- 這個例子是壞的，因為它把「之後可能會需要」誤當成當前範疇授權。

```md
觀察：
- 目前只被要求做 frontend feature 的一段

處理：
- 因為預期 backend 也要改，所以直接同步擴到 backend feature 與 API 規格
```

# Rule 4 - `Scenario Outline` 或資料家族仍要維持單一行為家族

- Level: `SHOULD`
- 若當前範疇包含 `Scenario Outline` 或一組資料家族，可在同次 invocation 內 sequentially 推進多個 slices，但前提是它們仍屬同一個業務規則或同一種行為差異。
- 若不同 rows、Examples 或資料列實際代表不同商業規則，應先回到上游規格拆分，而不是在 `/bdd` 階段硬吃。
- Data Table 若同時包含 setup 與 assertion 資料，也應先確認其核心行為仍然只有一個。

## Good Example

- 這個例子是好的，因為它把多筆資料視為同一規則的多組輸入。

```gherkin
Scenario Outline: 非法猜測會被拒絕
  Given 輪到玩家出手
  When 玩家送出 "<guess>"
  Then 系統提示 "<reason>"
```

## Bad Example

- 這個例子是壞的，因為它把不同規則硬塞進同一個資料家族。

```gherkin
Scenario Outline: 出手結果
  Given 一個對局
  When 玩家送出 "<case>"
  Then 系統處理 "<result>"
```

# Rule 5 - 當前 slice 的完成定義必須包含行為訊號與局部整潔度

- Level: `SHOULD`
- 一個 slice 只有在達成當前入口的完成條件、focused test 訊號清楚，且沒有留下明顯重複 step、臨時碼、錯誤命名或失焦 abstraction 時，才適合進下一個 slice。
- `red` 要求的是有效失敗訊號；`green` 要求的是目前 slice 已轉綠；`refactor` 要求的是重構後仍由代表性測試保護。
- 完成定義追求的是「可安全繼續下一個 slice」，不是「看起來差不多就往下做」。

## Good Example

- 這個例子是好的，因為它在轉綠後先處理局部可見的債，再前進。

```md
當前 slice 狀態：
- focused test 已綠
- 抽出共用 assertion helper
- 移除 debug print

決策：
- 進下一個 slice
```

## Bad Example

- 這個例子是壞的，因為它只看功能是否大致可跑，忽略明顯的局部失真。

```md
當前 slice 狀態：
- 測試偶爾綠偶爾紅
- 留著 `tmpGuessHelper2`
- step wording 還混著 UI 操作細節

決策：
- 直接做下一個 slice
```
