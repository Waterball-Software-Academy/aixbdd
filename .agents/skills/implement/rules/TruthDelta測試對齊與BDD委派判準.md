# Rule 1 - 執行前必須判斷 truth delta action

- Level: `MUST`
- `/implement` 開始任務前必須從 `truth-delta.md` 與 `tasks.md` 判斷當前 task 對應 `ADD`、`MODIFY`、`DELETE` 或 `NOOP`。
- 若 task 未明確連到 truth-delta row，但屬於受 truth 變更影響的 phase，必須依 phase 的 `Shared Must Read` 與 `Boundary` 推回 action。
- 若 action 無法判定且會影響測試或產品行為，應停止並回報 `tasks.md` 需要補明確參照。

## Good Example

- 這個例子是好的，因為 implement 先判斷當前 task 是 MODIFY。

```md
T006 [BDD-ALIGN]
truth-delta: /dsl-refine MODIFY `When: "{玩家}" 送出訊息 "{內容}"`
action: MODIFY
```

## Bad Example

- 這個例子是壞的，因為只看 task marker，沒有回讀 truth-delta。

```md
看到 [BDD-GREEN] 就直接改產品碼，不確認它是 ADD 還是 MODIFY。
```

# Rule 2 - MODIFY 必須先對齊既有自動化測試

- Level: `MUST`
- `MODIFY` 類 task 開始改產品碼前，必須確認受影響的既有 feature scenarios、step definitions、fixtures、helpers 與 assertions 是否仍表達舊 truth。
- 若既有測試表達舊 truth，必須先更新測試語意，使其符合最新版 truth，再讓產品碼轉綠。
- 若找不到既有測試落點，必須記錄查找範圍，並建立或使用能覆蓋新版 truth 的 focused test 入口。

## Good Example

- 這個例子是好的，因為先修正舊 assertion。

```md
先把「離房後仍看得到舊訊息」的 assertion 改成「離房後看不到先前訊息」，再調整產品碼。
```

## Bad Example

- 這個例子是壞的，因為產品碼改完但舊測試仍在驗錯規格。

```md
只新增一個新版測試並讓它通過，沒有處理仍期待舊行為的 step definition。
```

# Rule 3 - DELETE 必須移除過期測試與過期行為

- Level: `MUST`
- `DELETE` 類 task 必須移除或改寫不再成立的 feature scenarios、step definitions、fixtures、helpers、assertions 與產品分支。
- 不得只在產品碼中停止支援舊行為，卻留下仍保護舊 truth 的測試。
- `REGRESSION` task 必須跑受影響 focused tests，證明新版 truth 成立且舊行為沒有被測試繼續保護。

## Good Example

- 這個例子是好的，因為測試與產品行為一起移除。

```md
BDD-REMOVE: 移除舊 scenario 與 step assertion
CODE-REMOVE: 移除產品碼舊分支
REGRESSION: 跑離房清空與他房隔離 focused tests
```

## Bad Example

- 這個例子是壞的，因為只刪產品分支。

```md
刪掉 API 欄位，但保留舊 feature file 與 step definition。
```

# Rule 4 - 委派 BDD 時必須帶上 action 與既有測試面

- Level: `MUST`
- `/implement` 呼叫 `/bdd` 時，必須明確提供 truth delta action、affected truth rows、truth feature file、對應 `dsl.md`、requested step 與 affected existing automation surfaces。
- `BDD-ALIGN` 的 requested step 必須要求先更新既有測試語意。
- `BDD-REMOVE` 的 requested step 必須要求移除或改寫過期測試語意。
- 不得只傳 feature file 與 requested step，卻省略 action 與既有測試面。

## Good Example

- 這個例子是好的，因為 BDD handoff 足以判斷是修改既有測試。

```md
呼叫 /bdd
- action: MODIFY
- requested step: BDD-ALIGN
- truth row: /dsl-refine MODIFY `Then: "{玩家}" 看不到先前的聊天訊息`
- feature file: `specs/truth/features/backend/離開後清空與他房隔離.feature`
- dsl: `specs/truth/features/backend/dsl.md`
- affected automation: `backend/features/steps/modules/房間聊天/操作與斷言.py`
```

## Bad Example

- 這個例子是壞的，因為沒有告訴 BDD 這是 MODIFY。

```md
呼叫 /bdd，請處理離開後清空 feature。
```
