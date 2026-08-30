# Rule 1 - 每個 `red` slice 都必須先明確宣告目標與 focused test 入口

- Level: `MUST`
- 在開始任何 `red` 工作前，必須先指明本輪要驅動的單一 slice，以及對應要執行的最窄測試入口，例如單一 scenario、單一 `Rule`、單一 feature 檔或等價的 focused rerun 策略。
- 若目前專案無法做到單一 slice rerun，也應選擇最小可接受範圍，而不是直接跑整包測試。
- 沒有明確目標 slice 的測試修改，不算有效的 `red`。

## Good Example

- 這個例子是好的，因為它先對齊本輪目標與最窄執行入口。

```md
本輪目標：
- Slice: 玩家選滿三個數字後可按送出

Focused test：
- `npm test -- --name "玩家選滿三個數字後可按送出"`
```

## Bad Example

- 這個例子是壞的，因為它沒有明確指定要讓哪個行為先失敗。

```md
本輪目標：
- 先做對戰頁相關東西

Focused test：
- 全部 test 都跑一次看看
```

# Rule 2 - `red` 必須先觀察到與當前 slice 對應的合理失敗

- Level: `MUST`
- 新 slice 的實作必須先讓對應測試以合理方式失敗，確認它真的在驅動本輪需求，再進入 `green`。
- 若 skeleton 已存在，也必須至少重跑 focused test，確認目前 failure 與這個 slice 有關，不可憑感覺直接補實作。
- 不可在沒有觀察過 failure 的情況下，直接寫完整功能後宣稱自己完成了 `red`。

## Good Example

- 這個例子是好的，因為它先用失敗訊號確認切中的就是本輪行為。

```md
1. 新增對應 step skeleton 或 assertion
2. 跑 focused test
3. 看到 undefined step、missing assertion 或行為不符的 failure
4. 停在紅燈，準備交給 `green`
```

## Bad Example

- 這個例子是壞的，因為它把 `red` 當成事後驗證，而不是驅動入口。

```md
1. 先把整個送出流程寫完
2. 最後一次跑測試
3. 如果失敗再說自己剛剛其實在做 `red`
```

# Rule 3 - `red` 只建立失敗訊號，不提前補產品行為

- Level: `MUST`
- `red` 階段可以建立或調整測試骨架、step definitions、fixtures、assertion hook-up 與最小必要的編譯通路，但不可提前把產品行為補到足以轉綠。
- 若為了讓測試可執行而必須補最小樣板程式，其目的也只能是露出更真實的 failure，不可偷跑商業邏輯。
- `red` 的完成條件是「失敗訊號清楚」，不是「功能差一點就做好」。

## Good Example

- 這個例子是好的，因為它只做到讓 failure 真正落在當前行為上。

```md
本輪 `red` 補的內容：
- 新增 step skeleton
- 接上現有 fixture
- 讓測試跑到 assertion failure

本輪不做：
- 不實作「送出後換手」
- 不補真正的提交流程
```

## Bad Example

- 這個例子是壞的，因為它已經開始吸收 `green` 的工作。

```md
本輪 `red` 補的內容：
- 把提交 API、回合切換與按鈕禁用邏輯都先寫好
- 只差最後一個 assertion 還沒過
```

# Rule 4 - 在同一範疇內連續做多個 `red` 時，也必須一個 slice 一個 slice 地建立紅燈

- Level: `SHOULD`
- 若使用者指定的範疇允許同次 invocation 內 sequentially 推進多個 slices，應先讓前一個 slice 形成穩定紅燈，再切下一個 slice。
- 不應一次為多個未完成的 slices 大量新增測試骨架，導致 failure 來源彼此干擾。
- 若第一個 slice 的失敗仍混雜、無法歸因或被更上層錯誤遮蔽，應先停下修正失敗訊號品質，而不是繼續鋪下一個 `red`。

## Good Example

- 這個例子是好的，因為它把多 slice `red` 仍維持在可歸因的序列中。

```md
順序：
1. 先讓「可按送出」slice 穩定紅燈
2. 確認 failure 來源清楚
3. 才切到「送出後不可再送」slice 的紅燈
```

## Bad Example

- 這個例子是壞的，因為它一次鋪太多骨架，讓每個 failure 都失去辨識度。

```md
一次新增：
- 三個新 scenarios
- 六個 undefined steps
- 兩個互相覆蓋的 assertion

結果：
- 不知道哪個 failure 對應哪個 slice
```
