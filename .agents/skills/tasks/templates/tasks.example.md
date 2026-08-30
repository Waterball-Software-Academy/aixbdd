# Tasks: 房間聊天規格調整

**Plan Package**: `specs/plans/004-room-chat-adjustment`
**Core Inputs**: `spec.md`, `plan.md`, `research.md`, `truth-delta.md`, `specs/truth/techstack.md`, `specs/truth/contracts/**`, `specs/truth/data/**`, `specs/truth/features/backend/**`, `specs/truth/features/frontend/**`, `ui/**`

## Task Binding Contract

- 每個**開發任務**都必須對應 `truth-delta.md` 中的 ADD / MODIFY / DELETE / NOOP 語意。
- 若 `truth-delta.md` 含 `MODIFY` 或 `DELETE`，必須先建立 `Truth Delta Impact Audit` phase。
- `ADD` 使用 `[BDD-RED] -> [BDD-GREEN] -> [BDD-REFACTOR]`。
- `MODIFY` 使用 `[BDD-ALIGN] -> [BDD-GREEN] -> [BDD-REFACTOR]`。
- `DELETE` 使用 `[BDD-REMOVE] -> [CODE-REMOVE] -> [REGRESSION]`。
- Truth 參照必須使用 `specs/truth/**` 路徑；plan 參照才使用當前 plan package 內相對路徑。

## Phase 1: Truth Delta Impact Audit

**Goal**: 先盤點聊天 truth 修改與刪除會影響哪些既有 BDD 測試、step definitions、fixtures、helpers 與產品行為。

- [ ] T001 盤點聊天 MODIFY / DELETE 對既有自動化測試與產品碼的影響
  - Read:
    - `truth-delta.md` -> `/dsl-refine` MODIFY `When: "{玩家}" 送出訊息 "{內容}"`, `/dsl-refine` DELETE `Then: 對手仍看得到離房前訊息`
    - `specs/truth/features/backend/dsl.md` -> `When: "{玩家}" 送出訊息 "{內容}"`
    - `specs/truth/features/backend/離開後清空與他房隔離.feature` -> `Feature: 離開後清空與他房隔離`
    - `backend/features/steps/` -> 聊天 step definitions 與 shared helper
    - `frontend/features/steps/` -> 聊天 page helpers 與 assertions

## Phase 2: Foundational

**Goal**: 先集中更新聊天測試共用 helper，讓後續 MODIFY / DELETE phases 不各自修同一批 helper。

- [ ] T002 更新聊天測試共用 helper，使其以最新版 truth 的訊息清空與可見性語意為準
  - Read:
    - `truth-delta.md` -> `/api-plan`, `/data-plan`, `/dsl-refine` 的聊天 MODIFY / DELETE rows
    - `specs/truth/contracts/openapi.yaml` -> `RoomSnapshot.messages`
    - `specs/truth/data/data-model.dbml` -> `Table chat_messages`

## Phase 3A: ADD Feature File - backend/單人等待與空白訊息拒絕.feature

**Goal**: 新增單人等待與空白拒絕的後端 BDD 覆蓋。

**Shared Must Read**:
- `specs/truth/features/backend/單人等待與空白訊息拒絕.feature` -> `Feature: 單人等待與空白訊息拒絕`
- `specs/truth/features/backend/dsl.md` -> `When: "{玩家}" 嘗試送出空白訊息`, `Then: 這次聊天送出被拒絕`
- `truth-delta.md` -> `/dsl-refine` ADD 單人等待與空白訊息拒絕
- `spec.md` -> `使用者故事 1`, `FR-004`, `FR-005`

**Boundary**:
- 只處理單人等待與空白拒絕，不處理開局延續或離開清空。
- 新增測試不得改寫既有離房清空語意。

- [ ] T003 [BDD-RED] 先讓單人等待與空白拒絕規則出現正式紅燈
- [ ] T004 [BDD-GREEN] 以最小送訊拒絕邏輯讓此 feature file 全綠
- [ ] T005 [BDD-REFACTOR] 整理拒絕訊息與測試 helper

## Phase 3B: MODIFY Feature File - backend/雙方在場寫入房間對話.feature

**Goal**: 將既有雙方在場互傳測試更新為最新版 DSL：送訊成功必須同時驗證 store 落地與再讀快照。

**Shared Must Read**:
- `truth-delta.md` -> `/dsl-refine` MODIFY `When: "{玩家}" 送出訊息 "{內容}"`
- `specs/truth/features/backend/雙方在場寫入房間對話.feature` -> `Feature: 雙方在場寫入房間對話`
- `specs/truth/features/backend/dsl.md` -> `When: "{玩家}" 送出訊息 "{內容}"`, `Then: "{玩家}" 與 "{玩家}" 都看得到以下聊天內容：`
- `backend/features/steps/modules/房間聊天/操作與斷言.py` -> 既有送訊與斷言 step definitions
- `backend/features/steps/shared/chat_helpers.py` -> 既有聊天 helper

**Boundary**:
- 先修正既有測試語意，不新增無關聊天場景。
- 若舊 assertion 只看 API 回應，必須改成同時驗證 store 與再讀快照。

- [ ] T006 [BDD-ALIGN] 將既有雙方在場互傳 step definitions 與 helper 對齊最新版 DSL 語意
- [ ] T007 [BDD-GREEN] 調整送訊實作與快照投影，讓更新後測試全綠
- [ ] T008 [BDD-REFACTOR] 在綠燈下整理聊天寫入與再讀確認共用邏輯

## Phase 3C: DELETE Feature / DSL Truth - 離房後仍可看到舊訊息

**Goal**: 移除過期的離房後保留舊訊息行為與測試保護。

**Shared Must Read**:
- `truth-delta.md` -> `/dsl-refine` DELETE `Then: 對手仍看得到離房前訊息`
- `specs/truth/features/backend/離開後清空與他房隔離.feature` -> `Feature: 離開後清空與他房隔離`
- `specs/truth/features/backend/dsl.md` -> `Then: "{玩家}" 看不到先前的聊天訊息`
- `backend/features/steps/modules/房間聊天/操作與斷言.py` -> 可能仍保護舊訊息可見性的 step assertions
- `backend/app/store.py` -> 可能仍保留離房訊息的產品分支

**Boundary**:
- 只移除離房後保留舊訊息的過期語意，不移除雙方在場時的聊天歷史。
- 必須證明離房清空與他房隔離仍符合最新版 truth。

- [ ] T009 [BDD-REMOVE] 移除或改寫仍期待離房後看得到舊訊息的 BDD scenarios、step definitions 與 assertions
- [ ] T010 [CODE-REMOVE] 移除產品碼中保留離房訊息的過期分支
- [ ] T011 [REGRESSION] 跑離房清空、他房隔離與雙方在場聊天 focused tests，確認新版 truth 成立
