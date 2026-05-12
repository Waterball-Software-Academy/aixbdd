# Pattern — 一個 component 拆多個 Story export 的判準

## §1 什麼樣的差異值得拆 story

| 差異維度 | 應拆 | 範例 |
|---|---|---|
| 顯著視覺差異 | 是 | `Primary` / `Secondary` / `Ghost` |
| 互動可達性差異 | 是 | `Default` / `Disabled` / `Loading` |
| Empty / Filled / Error | 是 | `Empty` / `Filled` / `WithError` |
| Boundary content（極短 / 極長） | 視情況 | `Default` / `WithLongLabel` |
| 顏色 token 差異 | 否（用 `parameters.backgrounds`） | — |
| 純尺寸（responsive） | 否（用 `parameters.viewport`） | — |

## §2 命名建議

- 用**狀態名詞**或**形容詞**：`Default` / `Loading` / `Submitting` / `Empty` / `WithError` / `Disabled`
- 不用**動詞片語**：避免 `ClickToSubmit` / `WhenLoaded`（讀起來像 scenario，不像 state）
- 不用**版本號**：避免 `V2` / `New`（用 git diff 表達演進；不在 sidebar 留歷史）

## §3 推薦最小集合（form-like component）

```
- Default        # 基線，可互動，empty values
- Filled         # 已填寫，有 prefilled args
- Submitting     # 提交中，disabled + spinner
- WithError      # 顯示驗證錯誤
- Disabled       # 全 disabled
```

## §4 推薦最小集合（list-like component）

```
- Empty          # 空清單 fallback UI
- WithItems      # 標準筆數
- WithManyItems  # 邊界（virtualization 視覺驗證）
- Loading        # skeleton / spinner
- Error          # 載入錯誤
```

## §5 caller 推理包不該預先發明 stories

caller 應從 `.feature` rule / scenario 已決定的狀態反推 stories；本 skill 不替 caller 做需求收斂。
若推理包出現「stories 數量遠大於 BDD scenarios 涉及的狀態數」→ caller 該重新收斂後再 DELEGATE。
