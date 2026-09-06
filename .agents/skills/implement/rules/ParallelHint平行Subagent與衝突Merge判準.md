# Rule 1 - 當前 phase 有 Parallel Hint 時必須一次派出該批 subagent

- Level: `MUST`
- 若 `tasks.md` 當前 phase 含 `Parallel Hint`，本輪任務集就是 Hint 列出的 `[P]` tasks，不是只拿第一個已解鎖 task。
- 每個列出的 `[P]` task 派一個獨立 subagent。
- review task 等該批全部回來後才啟動，不得與該批平行。

## Good Example

- 這個例子是好的，因為它按 Hint 一次派出 T008–T014。

```md
Parallel Hint: T008–T014 各派一個獨立 subagent；T015 等全部回來再 review。
本輪先派出 T008–T014，不先只做 T008。
```

## Bad Example

- 這個例子是壞的，因為它忽略 Hint，仍一次只做一個 Phase 3 task。

```md
看到 T008 [P] [BDD-ALIGN]，只派一個 subagent 做 T008，T009–T014 留到後面序列。
```

# Rule 2 - subagent prompt 只指向 tasks.md 的該筆任務

- Level: `MUST`
- 每個 subagent 的 prompt 必須包含：讀哪個 plan 的 `tasks.md`、第幾個任務、職責就是開發此任務。
- 衝突處理寫在 prompt 裡：若目標檔已被其他 subagent 改過，先讀最新內容，自己 merge 這條 DSL 的改動。
- 不得在 `tasks.md` 再貼一份完整 prompt。不得在 prompt 重寫 DSL / Why / Read；那些已在該 task 與 Phase `Shared Must Read`。

## Good Example

- 這個例子是好的，因為 prompt 指向任務本身。

```md
請讀 `specs/plans/004-room-chat-adjustment/tasks.md` 的 T008。
你的職責就是開發此任務。
若目標檔已被其他 subagent 改過，先讀最新內容，自己 merge 這條 DSL 的改動。
```

## Bad Example

- 這個例子是壞的，因為它另寫一套語意，不叫 subagent 去讀 task。

```md
請把送訊 stepdef 改成驗證 store。不要去看 tasks.md。
```

# Rule 3 - 同一檔由後寫入的 subagent 自己 merge，review 不負責合併

- Level: `MUST`
- 兩個 Phase 3 task 要寫同一檔時，仍各派 subagent、直接改檔。
- 後寫入的 subagent 必須先讀最新檔，再把自己這條 DSL 的改動 merge 進去。
- review task 只做 review，不合併 diff。

## Good Example

- 這個例子是好的，因為同檔衝突留在寫入端。

```md
T008 與 T009 都寫 `操作與斷言.py`。
T009 的 subagent 發現檔已被 T008 改過，讀最新內容後只 merge 自己那條 Then。
T015 只 review 結果。
```

## Bad Example

- 這個例子是壞的，因為它把合併丟給 review。

```md
T008–T011 只交 patch，等 T015 合併。
```

# Rule 4 - review 有 issues 就修正，再 review，直到沒有任何問題

- Level: `MUST`
- Phase 3 的 review task 必須啟動 subagent 去 review。
- 本輪所有 Feature phase 的 `Test Scope` 跑起來不得再有 undefined step；失敗只能是 assertion 或產品行為。
- 只要有 issues 就修正，再啟動 subagent review；重複直到 subagent 沒有任何問題。
- review 通過前，不得解鎖 Feature phase 的 Green。

## Good Example

- 這個例子是好的，因為它形成迴圈閘門。

```md
T015 review 回報 T012 的 stepdef 沒讀 `權威狀態落地`。
修正後再 review。第二次沒有 issues，才解鎖 T016 [BDD-GREEN]。
```

## Bad Example

- 這個例子是壞的，因為它 review 一次有 issues 仍進 Green。

```md
T015 列出 3 個 issues。
agent 說之後 Green 再修，直接開始 T016。
```
