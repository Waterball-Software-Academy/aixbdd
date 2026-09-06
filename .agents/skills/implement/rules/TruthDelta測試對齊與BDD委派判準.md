# Rule 1 - 執行前必須判斷 truth delta action

- Level: `MUST`
- `/implement` 開始任務前必須從 `truth-delta.md` 與 `tasks.md` 判斷當前 task 對應 `ADD`、`MODIFY`、`DELETE` 或 `NOOP`。
- 若 task 未明確連到 truth-delta row，但屬於受 truth 變更影響的 phase，必須依 phase 的 `Shared Must Read` 與 `Boundary` 推回 action。
- 本輪 Feature 用到、尚無 stepdef、因而不在 truth-delta 的 `[BDD-RED]`，action 視為 `ADD`。
- 若 action 無法判定且會影響測試或產品行為，應停止並回報 `tasks.md` 需要補明確參照。

## Good Example

- 這個例子是好的，因為 implement 先判斷當前 task 是 MODIFY。

```md
T008 [BDD-ALIGN]
truth-delta: /dsl-refine MODIFY `When: "{玩家}" 送出訊息 "{內容}"`
action: MODIFY
```

## Bad Example

- 這個例子是壞的，因為只看 task marker，沒有回讀 truth-delta。

```md
看到 [BDD-GREEN] 就直接改產品碼，不確認它是 ADD 還是 MODIFY。
```

# Rule 2 - 改產品碼前，Phase 3 必須已對齊測試

- Level: `MUST`
- Feature Green / `CODE-REMOVE` 開始改產品碼前，Phase 3 review 必須已通過。
- 若既有測試仍表達舊 truth，必須先在 Phase 3 用 `[BDD-ALIGN]` 或 `[BDD-REMOVE]` 處理，不得在 Green 裡順便改測試來就綠。
- 若找不到既有測試落點，必須記錄查找範圍，並在 Phase 3 建立能覆蓋新版 truth 的 stepdef。

## Good Example

- 這個例子是好的，因為產品碼只在測試層對齊之後才動。

```md
T015 review 通過後，T018 [BDD-GREEN] 才調整送訊實作。
```

## Bad Example

- 這個例子是壞的，因為產品碼改完但舊測試仍在驗錯規格。

```md
只新增一個新版測試並讓它通過，沒有處理仍期待舊行為的 step definition。
```

# Rule 3 - DELETE 必須先清測試、再清產品行為

- Level: `MUST`
- Phase 3 的 `[BDD-REMOVE]` 必須移除或改寫不再成立的 feature scenarios、step definitions、fixtures、helpers 或 assertions。
- Feature phase 的 `[CODE-REMOVE]` 必須移除或關閉支援舊 truth 的產品分支。
- `[REGRESSION]` 必須跑該 phase 的 `Test Scope`，證明新版 truth 成立且舊行為沒有被測試繼續保護。
- 不得只在產品碼中停止支援舊行為，卻留下仍保護舊 truth 的測試。

## Good Example

- 這個例子是好的，因為測試與產品行為按 phase 分開。

```md
Phase 3 BDD-REMOVE: 移除舊 step assertion
Phase 4C CODE-REMOVE: 移除產品碼舊分支
Phase 4C REGRESSION: 跑 Test Scope
```

## Bad Example

- 這個例子是壞的，因為只刪產品分支。

```md
刪掉 API 欄位，但保留舊 feature file 與 step definition。
```

# Rule 4 - 只有 Green / Refactor 才委派 `/bdd`，並帶 Test Scope

- Level: `MUST`
- `/implement` 只在 `[BDD-GREEN]` 或 `[BDD-REFACTOR]` 呼叫 `/bdd`。
- 呼叫時必須明確提供 `Test Scope`、truth delta action、affected truth rows、同模組 `dsl.md`、該 feature 實際使用的介面根共用 DSL rows 與 requested step。
- 若該 feature 沒有使用介面根共用 DSL row，必須明示「無」。
- `/implement` 只傳遞 `tasks.md` 已綁定的精確 DSL 參照，不重新判斷句型應屬模組或共用。
- Phase 3 的 `[BDD-ALIGN]`、`[BDD-REMOVE]`、`[BDD-RED]` 不委派 `/bdd`。

## Good Example

- 這個例子是好的，因為 Green 帶了 Test Scope。

```md
呼叫 /bdd
- requested step: green
- Test Scope: `specs/truth/features/backend/房間聊天/單人等待與空白訊息拒絕.feature`
- action: ADD
- module dsl: `specs/truth/features/backend/房間聊天/dsl.md`
- shared dsl rows: 無
```

## Bad Example

- 這個例子是壞的，因為它把 Phase 3 ALIGN 當成 `/bdd` 的單一 feature red。

```md
呼叫 /bdd，requested step=red，請處理離開後清空 feature。
```
