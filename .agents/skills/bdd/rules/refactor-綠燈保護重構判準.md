# Rule 1 - `refactor` 只能在綠燈保護下進行

- Level: `MUST`
- 進入 `refactor` 前，當前 slice 或本輪要整理的 slices 必須已由 focused test 或最小代表性測試集合保護。
- 若目前仍有未釐清的紅燈、間歇性失敗或與當前重構無關的測試噪音，應先回到 `red` 或 `green` 處理，不可硬做 `refactor`。
- `refactor` 的前提是「行為已成立」，不是「功能快做完了」。

## Good Example

- 這個例子是好的，因為它先確認綠燈存在，再整理結構。

```md
前提：
- `--name "送出後同回合不可再次送出"` 已穩定綠燈

處理：
- 開始抽共用 assertion helper
- 每次整理後重跑代表性測試
```

## Bad Example

- 這個例子是壞的，因為它在行為尚未站穩前就開始搬動結構。

```md
前提：
- 測試還有 undefined step
- 送出流程偶爾紅燈

處理：
- 先重命名大量 helper 與 fixtures
```

# Rule 2 - `refactor` 應優先清理重複 step、型別轉換邊界與支撐層命名

- Level: `SHOULD`
- 當前範疇內若已出現重複 step wording、可抽的 parameter / data table type、硬編碼測試資料、命名失焦或薄 glue 被破壞，應優先在 `refactor` 階段整理。
- 重構的目標是讓後續同範疇 slices 更容易繼續前進，而不是追求與本輪行為無關的大型架構整理。
- 若整理只會改善局部可讀性、卻會放大風險與變動面，應保守處理。

## Good Example

- 這個例子是好的，因為它先整理剛被本輪行為驗證過的重複與失焦邊界。

```md
本輪重構：
- 把三個相近的 submit steps 收斂成同一個 wording
- 抽出共用 `GuessSelection` parameter type
- 把 `tmpBattleAssert` 改回領域名稱
```

## Bad Example

- 這個例子是壞的，因為它跳去做和當前範疇關聯很弱的大型重構。

```md
本輪重構：
- 順手重寫整個測試框架初始化流程
- 順手更換所有 support 目錄命名規則
```

# Rule 3 - `refactor` 不可改寫已核准的業務意圖，也不可回頭修改上游規格

- Level: `MUST`
- `refactor` 只可整理 step definitions、helpers、fixtures、assertion helpers、產品碼結構與命名，不可把已核准的業務行為悄悄改掉。
- 若重構過程發現目前設計其實需要改變 `feature file` 邊界、`dsl.md` 詞彙或驗收結果，應停止並回交上游，而不是在本地重新定義規格。
- 重構是改善落地方式，不是重寫需求。

## Good Example

- 這個例子是好的，因為它只改落地結構，不改行為契約。

```md
已核准行為：
- 玩家送出後同回合不可再次送出

重構處理：
- 抽共用 `turnStateHelper`
- 不修改 feature wording 與驗收結果
```

## Bad Example

- 這個例子是壞的，因為它在重構名義下改變了業務結果。

```md
已核准行為：
- 玩家送出後同回合不可再次送出

重構處理：
- 覺得導去價格頁比較合理
- 直接把 assertion 與流程行為改掉
```

# Rule 4 - 若重構需要跨出指定範疇，應停止並回報，不得順手擴張

- Level: `MUST`
- `refactor` 若只在當前 `feature file` 或其明確區塊內整理即可完成，應限制在本輪範疇內。
- 若重構必須同步改多個不在本輪授權內的 `feature files`、介面邏輯或上游 DSL，應停止並回報原因，讓使用者重新拍板範疇。
- 不可因為「現在最順手」就把 refactor 變成跨模組、跨介面的無界整理。

## Good Example

- 這個例子是好的，因為它把 scope guard 視為 refactor 的硬限制。

```md
觀察：
- 只要整理當前 frontend helper 與 assertion 命名，就能消除重複

處理：
- 留在 frontend 這個 feature 範圍內完成
```

## Bad Example

- 這個例子是壞的，因為它把局部整理擴成無界的系統性改造。

```md
觀察：
- 當前只是 frontend feature 的 refactor

處理：
- 順手同步改 backend steps、shared DSL 與 acceptance wording
```
