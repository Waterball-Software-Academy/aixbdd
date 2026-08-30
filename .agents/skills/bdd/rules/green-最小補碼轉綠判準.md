# Rule 1 - `green` 必須從當前 `red` failure 出發，不可跳過失敗訊號

- Level: `MUST`
- `green` 階段只能根據當前 focused test 已觀察到的 failure 補碼，不可在沒有 `red` 訊號的情況下直接宣告進入 `green`。
- 若目前 failure 與本輪 slice 無關、過於上游或被其他錯誤遮蔽，應先回頭修正 `red`，而不是硬往下補。
- `green` 的最小補碼必須對應當前 failure，而不是對應想像中的完整功能。

## Good Example

- 這個例子是好的，因為它讓補碼和當前 failure 形成一一對應。

```md
當前 failure：
- 送出按鈕在選滿三個數字後仍維持 disabled

本輪補碼：
- 只補按鈕可用條件
- 不先做換手、計分或結算
```

## Bad Example

- 這個例子是壞的，因為它沒有真的從當前 failure 出發。

```md
當前 failure：
- undefined step

本輪補碼：
- 直接把整段提交流程、計分與回合切換全部寫完
```

# Rule 2 - 每次補碼只解決目前 slice 的 failure，不得偷跑未選定行為

- Level: `MUST`
- 當前 slice 需要的程式碼只應涵蓋目前 failure 所對應的最小行為。
- 不可因為預見下一個 slice 也會需要某能力，就一次把額外路徑、角色、flags 或 branches 全數寫進去。
- 若下一個 slice 會迫使目前設計調整，等到下一輪再由新的 `red` 或新的 `green` 訊號驅動。

## Good Example

- 這個例子是好的，因為它只補了目前 slice 所需的最小條件。

```md
本輪 slice：
- 玩家選滿三個數字後可按送出

本輪補碼：
- 只補「三個數字都存在時 enable submit」
- 不先加入「送出後鎖定」「輪到對手時禁用」
```

## Bad Example

- 這個例子是壞的，因為它把未來多個 slices 的能力一次寫進來。

```md
本輪 slice：
- 玩家選滿三個數字後可按送出

本輪補碼：
- 一次加入 enable / disable / lock / opponent turn / timeout / reconnect 全部分支
```

# Rule 3 - step definitions 必須保持薄層，重用應下沉到 helper、fixture 與 domain abstraction

- Level: `MUST`
- step definition 應只負責匹配 step、解析參數、進入 assertion 或委派 helper，不可在同一個 step 中堆疊大量建立資料、跨頁流程與多重斷言。
- 若多個 steps 共享底層行為，應抽 helper method、page object、service、fixture 或 parameter / data table type，而不是在 step definition 內互相呼叫。
- 依 feature 檔名硬切 step definitions 是高風險訊號；應優先按 domain concept 組織。

## Good Example

- 這個例子是好的，因為 step 很薄，重用點留在底層。

```js
When("玩家提交猜測 {string}", async function (guess) {
  await battlePage.submitGuess(guess);
});
```

## Bad Example

- 這個例子是壞的，因為 step definition 自己變成完整測試劇本。

```js
When("玩家提交猜測", async function () {
  await openBattlePage();
  await clickCell(1);
  await clickCell(2);
  await clickCell(3);
  await clickSubmit();
  await expectBanner("submitted");
  await expectTurnSwitch();
});
```

# Rule 4 - 同一次 invocation 可在範疇內連續轉綠多個 slices，但每個 slice 都要有獨立綠燈

- Level: `SHOULD`
- 若使用者指定的範疇允許同次 invocation 內 sequentially 推進多個 slices，前一個 slice 必須先得到獨立綠燈，才可切換到下一個 slice。
- 不可讓多個 slices 共用一個模糊的「大致上過了」訊號。
- 若某個 slice 雖然綠燈，但留下明顯的重複 step、硬編碼資料或暫時碼，應先做最小整理，再決定是否在同次 invocation 內繼續下一個 slice。

## Good Example

- 這個例子是好的，因為它讓每個綠燈都能單獨對應一個完成的 slice。

```md
順序：
1. `--name "玩家選滿三個數字後可按送出"` 先綠
2. 抽出共用 helper
3. 才切到 `--name "送出後同回合不可再次送出"`
```

## Bad Example

- 這個例子是壞的，因為它把多個未穩定的行為一起宣稱完成。

```md
狀態：
- 幾個 related tests 似乎都差不多過了
- 但哪個 slice 已真正綠燈不清楚

決策：
- 直接往下一批需求前進
```
