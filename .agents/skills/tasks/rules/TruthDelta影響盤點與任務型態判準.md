# Rule 1 - MODIFY 或 DELETE 必須先建立 impact audit

- Level: `MUST`
- 當 `truth-delta.md` 包含任何 `MODIFY` 或 `DELETE` row，`tasks.md` 必須在 feature phases 前建立 `Truth Delta Impact Audit` phase 或等價的早期盤點任務。
- Impact audit 必須盤點受影響的 truth feature/dsl、既有 step definitions、fixtures、helpers、focused tests、產品分支與回歸測試面。
- Impact audit 不得偷做完整功能，只負責找出需要對齊的既有測試與實作入口。

## Good Example

- 這個例子是好的，因為修改既有 DSL 時先盤點既有測試落點。

```md
## Phase 1: Truth Delta Impact Audit

- [ ] T001 盤點 `RoomSnapshot.messages` 修改影響的後端 step definitions、前端 page helpers 與 focused tests
  - Read:
    - `truth-delta.md` -> `/api-plan` MODIFY `RoomSnapshot.messages`
    - `specs/truth/features/backend/房間聊天/dsl.md` -> `Then: "{玩家}" 看得到先前的聊天訊息`
```

## Bad Example

- 這個例子是壞的，因為直接新增 BDD task，沒有處理既有測試語意偏移。

```md
## Phase 3: Feature File - backend/聊天.feature

- [ ] T001 [BDD-RED] 新增聊天規則紅燈
```

# Rule 2 - ADD、MODIFY、DELETE 必須使用不同任務型態

- Level: `MUST`
- `ADD` 類 truth feature 使用 `[BDD-RED] -> [BDD-GREEN] -> [BDD-REFACTOR]`。
- `MODIFY` 類 truth feature 或 DSL 使用 `[BDD-ALIGN] -> [BDD-GREEN] -> [BDD-REFACTOR]`。
- DSL row 僅搬移唯一權威位置且語意不變時仍屬 `MODIFY`；任務只需對齊精確參照與既有測試入口，不得拆成 `[BDD-REMOVE]` 與 `[BDD-RED]`。
- `DELETE` 類 truth feature、Rule、Example 或 DSL 使用 `[BDD-REMOVE] -> [CODE-REMOVE] -> [REGRESSION]`。
- 不得把 DELETE 硬塞成新增式 RED，也不得把 MODIFY 當作完全新的 feature file。

## Good Example

- 這個例子是好的，因為依 action 選擇不同 task pattern。

```md
- [ ] T010 [BDD-ALIGN] 先把既有準備頁聊天測試改成新版 DSL 語意
- [ ] T011 [BDD-GREEN] 調整產品碼讓新版測試通過
- [ ] T012 [BDD-REFACTOR] 在綠燈下整理 shared helper
```

## Bad Example

- 這個例子是壞的，因為 MODIFY 被當作新功能紅燈。

```md
- [ ] T010 [BDD-RED] 新增一份新版準備頁聊天測試
- [ ] T011 [BDD-GREEN] 寫新功能
- [ ] T012 [BDD-REFACTOR] 整理
```

# Rule 3 - MODIFY 任務必須先對齊既有自動化測試語意

- Level: `MUST`
- `BDD-ALIGN` 的目標是讓既有 automated tests 表達最新版 truth，而不是先寫產品碼。
- 若舊 step definitions、fixtures、helpers 或 assertions 仍表達舊 truth，`BDD-ALIGN` 必須更新或替換它們。
- 若既有測試已不存在或無法定位，`BDD-ALIGN` 必須明確記錄查找結果，並建立能覆蓋新版 truth 的 focused test 入口。

## Good Example

- 這個例子是好的，因為先修正舊測試期望。

```md
- [ ] T006 [BDD-ALIGN] 將既有「單人等待可輸入聊天」測試改成「單人等待不可送出且不留訊息」
```

## Bad Example

- 這個例子是壞的，因為直接改產品碼，沒有確認舊測試是否仍在驗錯規格。

```md
- [ ] T006 [BDD-GREEN] 修改聊天送出 API
```

# Rule 4 - DELETE 任務必須移除過期測試與過期行為

- Level: `MUST`
- `BDD-REMOVE` 必須移除或改寫不再成立的 feature scenarios、step definitions、fixtures、helpers 或 assertions。
- `CODE-REMOVE` 必須移除或關閉支援舊 truth 的產品分支、API 投影、資料欄位或 UI 行為。
- `REGRESSION` 必須跑受影響 focused tests，證明新版 truth 成立且舊行為沒有被測試繼續保護。

## Good Example

- 這個例子是好的，因為刪除 truth 會清掉測試與產品行為。

```md
- [ ] T014 [BDD-REMOVE] 移除「離開後仍可看到舊訊息」相關舊 scenario 與 step assertion
- [ ] T015 [CODE-REMOVE] 移除產品碼中保留離房訊息的分支
- [ ] T016 [REGRESSION] 跑聊天離房與他房隔離 focused tests
```

## Bad Example

- 這個例子是壞的，因為只刪產品碼，留下過期測試。

```md
- [ ] T014 [CODE-REMOVE] 移除舊功能
```
