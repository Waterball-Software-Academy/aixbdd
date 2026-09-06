# Rule 1 - MODIFY 或 DELETE 必須先建立 impact audit

- Level: `MUST`
- 當 `truth-delta.md` 包含任何 `MODIFY` 或 `DELETE` row，`tasks.md` 必須在 Phase 3 與 Feature phases 前建立 `Truth Delta Impact Audit` phase 或等價的早期盤點任務。
- Impact audit 必須盤點受影響的 truth feature/dsl、既有 step definitions、fixtures、helpers、focused tests、產品分支與回歸測試面。
- Impact audit 不得偷做 Phase 3 測試層或 Feature Green，只負責找出需要對齊的既有測試與實作入口。

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

- 這個例子是壞的，因為直接在 Feature phase 寫測試層任務，沒有先盤點。

```md
## Phase 4A: ADD Feature File - backend/聊天.feature

- [ ] T001 [BDD-RED] 新增聊天規則紅燈
```

# Rule 2 - 測試層集中在 Phase 3，Feature phase 只留產品碼任務

- Level: `MUST`
- `ADD` 的句，或本輪 Feature 用到、尚無 stepdef 的句：Phase 3 用 `[BDD-RED]`；對應 Feature phase 只留 `[BDD-GREEN] -> [BDD-REFACTOR]`。
- `MODIFY` 的句：Phase 3 用 `[BDD-ALIGN]`；對應 Feature phase 只留 `[BDD-GREEN] -> [BDD-REFACTOR]`。
- `DELETE` 的句：Phase 3 用 `[BDD-REMOVE]`；對應 Feature phase 只留 `[CODE-REMOVE] -> [REGRESSION]`。
- DSL row 僅搬移唯一權威位置且語意不變時仍屬 `MODIFY`；Phase 3 只對齊精確參照與既有測試入口，不得拆成 `[BDD-REMOVE]` 與 `[BDD-RED]`。
- 不得把 `[BDD-RED]`、`[BDD-ALIGN]`、`[BDD-REMOVE]` 寫進 Feature phase。
- 不得把 DELETE 硬塞成新增式 RED，也不得把 MODIFY 當作完全新的 feature file。

## Good Example

- 這個例子是好的，因為測試層在 Phase 3，Feature 只留 Green。

```md
## Phase 3: Test Alignment & Implementation

- [ ] T003 [P] [BDD-ALIGN] `When: "{玩家}" 送出訊息 "{內容}"`

## Phase 4B: MODIFY Feature File - backend/房間聊天/雙方在場寫入房間對話.feature

- [ ] T013 [BDD-GREEN] 讓 Test Scope 全綠
- [ ] T014 [BDD-REFACTOR] 在綠燈下整理聊天寫入與再讀確認共用邏輯
```

## Bad Example

- 這個例子是壞的，因為 ALIGN 仍綁在 Feature phase 裡。

```md
## Phase 4B: MODIFY Feature File - backend/房間聊天/雙方在場寫入房間對話.feature

- [ ] T010 [BDD-ALIGN] 先把既有測試改成新版 DSL 語意
- [ ] T011 [BDD-GREEN] 寫新功能
```

# Rule 3 - Phase 3 必須列出本輪 Feature 用到的全部待處理 DSL

- Level: `MUST`
- Phase 3 清單必須包含 truth-delta 的 `ADD` / `MODIFY` / `DELETE` 句，以及本輪 Feature 用到、尚無 stepdef 的句。
- 一條 DSL 一個 `[P]` task；語意沒變且 stepdef 已在的句不列。
- `[BDD-ALIGN]` 只改既有測試，讓它表達最新版 `StepDef 實作語意`，不寫產品碼。
- `[BDD-REMOVE]` 只移除或改寫仍保護舊 truth 的測試，不寫產品碼。
- `[BDD-RED]` 依 `dsl.md` 該列寫出 stepdef；完成時這句可被跑到，失敗只能是 assertion 或產品行為。

## Good Example

- 這個例子是好的，因為本輪 Feature 用到、但不在 truth-delta 的句也進了 Phase 3。

```md
- [ ] T006 [P] [BDD-RED] `Given: "{玩家}" 在房間內單人等待`
- [ ] T007 [P] [BDD-RED] `When: "{玩家}" 嘗試送出空白訊息`
```

## Bad Example

- 這個例子是壞的，因為只列 truth-delta 改過的句，Green 會卡在沒寫的 Given。

```md
Phase 3 只列 `When: "{玩家}" 嘗試送出空白訊息`。
`單人等待與空白訊息拒絕.feature` 用到的 Given 沒有 stepdef，也沒有 task。
```

# Rule 4 - DELETE 的產品行為留在 Feature phase

- Level: `MUST`
- `[BDD-REMOVE]` 在 Phase 3 完成測試層清理。
- `[CODE-REMOVE]` 在 Feature phase 移除或關閉支援舊 truth 的產品分支、API 投影、資料欄位或 UI 行為。
- `[REGRESSION]` 必須跑該 phase 的 `Test Scope`，證明新版 truth 成立且舊行為沒有被測試繼續保護。

## Good Example

- 這個例子是好的，因為測試與產品行為分開、順序正確。

```md
Phase 3: [BDD-REMOVE] `Then: 對手仍看得到離房前訊息`
Phase 4C: [CODE-REMOVE] 移除產品碼中保留離房訊息的分支
Phase 4C: [REGRESSION] 跑 Test Scope
```

## Bad Example

- 這個例子是壞的，因為只刪產品碼，留下過期測試。

```md
- [ ] T014 [CODE-REMOVE] 移除舊功能
```
