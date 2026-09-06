# Tasks: 房間聊天規格調整

**Plan Package**: `specs/plans/004-room-chat-adjustment`
**Core Inputs**: `spec.md`, `plan.md`, `research.md`, `truth-delta.md`, `specs/truth/techstack.md`, `specs/truth/contracts/**`, `specs/truth/data/**`, `specs/truth/features/backend/**`, `specs/truth/features/frontend/**`, `ui/**`

## Task Binding Contract

- 每個**開發任務**都必須對應 `truth-delta.md` 中的 ADD / MODIFY / DELETE / NOOP 語意。
- 若 `truth-delta.md` 含 `MODIFY` 或 `DELETE`，必須先建立 `Truth Delta Impact Audit` phase。
- Phase 3 `Test Alignment & Implementation` 的目的：在寫產品碼之前，先把本輪所有受影響 DSL 的自動化測試對齊最新版 truth。
- Truth 參照必須使用 `specs/truth/**` 路徑；plan 參照才使用當前 plan package 內相對路徑。

## Phase 1: Truth Delta Impact Audit

**Goal**: 先盤點聊天 truth 修改與刪除會影響哪些既有 BDD 測試、step definitions、fixtures、helpers 與產品行為。

- [ ] T001 盤點聊天 MODIFY / DELETE 對既有自動化測試與產品碼的影響
  - Read:
    - `truth-delta.md` -> `/dsl-refine` MODIFY `When: "{玩家}" 送出訊息 "{內容}"`, `/dsl-refine` DELETE `Then: 對手仍看得到離房前訊息`
    - `backend/features/steps/` -> 聊天 step definitions 與 shared helper
    - `frontend/features/steps/` -> 聊天 page helpers 與 assertions

## Phase 2: Foundational

**Goal**: 只建立聊天測試共用 helper 入口與骨架，讓後續 Phase 3 不各自重開落點。語意對齊不放這裡。

- [ ] T002 建立或確認聊天測試共用 helper 入口
  - Read:
    - `truth-delta.md` -> `/dsl-refine` 的聊天 ADD / MODIFY / DELETE rows
    - `backend/features/steps/shared/chat_helpers.py`

## Phase 3: Test Alignment & Implementation

**Goal**: 把本輪 Feature 用到的 DSL 自動化測試對齊最新版 truth；含 truth-delta 有改的句，以及本輪 Feature 用到、尚無 stepdef 的句。不寫產品行為。

**DSL 參照**:
- 每一句只屬於一個權威 `dsl.md`：同模組 `specs/truth/features/{介面}/{模組}/dsl.md`，或介面根 `specs/truth/features/{介面}/dsl.md`。不得掃其他模組。
- 本輪各句都在同模組 `specs/truth/features/backend/房間聊天/dsl.md`。本輪沒有介面根 `specs/truth/features/backend/dsl.md` 的句。
- 讀法：用 task title 的句型對到該檔那一列，以 `StepDef 實作語意` 當作測試程式碼語意。Given / When 讀 `怎麼做`、`權威狀態落地`、`回寫`；Then 讀 `必查`（`呈現結果`、`權威狀態`、`再讀確認`）。
- `truth-delta.md` 只告訴這句是 ADD / MODIFY / DELETE。語意以 `dsl.md` 那一列為準，不得用 feature 措辭或舊 stepdef 自行發明。

**Markers**:
- `[BDD-ALIGN]`：`MODIFY`。既有 stepdef 還在，但語意是舊 truth。依 `dsl.md` 該列改測試，讓它表達最新版 `StepDef 實作語意`。
- `[BDD-REMOVE]`：`DELETE`。此句已不是 truth。移除或改寫仍綁這句的 stepdef / assertion，不得留下保護舊行為的測試。
- `[BDD-RED]`：`ADD`，或本輪 Feature 用到、尚無 stepdef 的句。依 `dsl.md` 該列寫出 stepdef。完成時這句可被跑到，失敗只能是 assertion 或產品行為，不能是 undefined step。
- 三個 marker 都只動測試層，不寫產品碼。

**Shared Must Read**:
- `specs/truth/features/backend/房間聊天/dsl.md`
  -> `When: "{玩家}" 送出訊息 "{內容}"`
  -> `Then: "{玩家}" 與 "{玩家}" 都看得到以下聊天內容：`
  -> `Then: 對手仍看得到離房前訊息`
  -> `Given: "{玩家}" 在房間內單人等待`
  -> `When: "{玩家}" 嘗試送出空白訊息`
  -> `Then: 這次聊天送出被拒絕`
  -> `Then: "{玩家}" 看不到先前的聊天訊息`
- `truth-delta.md` -> `/dsl-refine` 有對應 ADD / MODIFY / DELETE 的句
- `backend/features/steps/modules/房間聊天/操作與斷言.py`

**Boundary**:
- 一條 DSL 一個 task。
- 只改該句的 stepdef / assertion / 直接依賴的 helper。
- 不寫產品碼。
- review 啟動 subagent；本輪所有 Test Scope 不得再有 undefined step，失敗只能是 assertion 或產品行為。有 issues 就修正再 review，直到沒有任何問題。通過前不解鎖 Phase 4。

**Parallel Hint**:
- T003–T009 各派一個獨立 subagent；T010 等全部回來再啟動 subagent 來 review。

- [ ] T003 [P] [BDD-ALIGN] `When: "{玩家}" 送出訊息 "{內容}"`
  - Read: `backend/features/steps/modules/房間聊天/操作與斷言.py`

- [ ] T004 [P] [BDD-ALIGN] `Then: "{玩家}" 與 "{玩家}" 都看得到以下聊天內容：`
  - Read: `backend/features/steps/modules/房間聊天/操作與斷言.py`

- [ ] T005 [P] [BDD-REMOVE] `Then: 對手仍看得到離房前訊息`
  - Read: `backend/features/steps/modules/房間聊天/操作與斷言.py`

- [ ] T006 [P] [BDD-RED] `Given: "{玩家}" 在房間內單人等待`

- [ ] T007 [P] [BDD-RED] `When: "{玩家}" 嘗試送出空白訊息`

- [ ] T008 [P] [BDD-RED] `Then: 這次聊天送出被拒絕`

- [ ] T009 [P] [BDD-RED] `Then: "{玩家}" 看不到先前的聊天訊息`

- [ ] T010 subagent review (phase quality gate)

## Phase 4A: ADD Feature File - backend/房間聊天/單人等待與空白訊息拒絕.feature

**Goal**: 以最小送訊拒絕邏輯讓此 feature file 全綠。

**Shared Must Read**:
- `specs/truth/features/backend/房間聊天/單人等待與空白訊息拒絕.feature` -> `Feature: 單人等待與空白訊息拒絕`
- `specs/truth/features/backend/房間聊天/dsl.md` -> `Given: "{玩家}" 在房間內單人等待`, `When: "{玩家}" 嘗試送出空白訊息`, `Then: 這次聊天送出被拒絕`
- `truth-delta.md` -> `/dsl-refine` ADD 單人等待與空白訊息拒絕

**Boundary**:
- 只處理單人等待與空白拒絕，不處理開局延續或離開清空。

**Test Scope**:
- `specs/truth/features/backend/房間聊天/單人等待與空白訊息拒絕.feature`

- [ ] T011 [BDD-GREEN] 讓 Test Scope 全綠
- [ ] T012 [BDD-REFACTOR] 在綠燈下整理拒絕訊息與測試 helper

## Phase 4B: MODIFY Feature File - backend/房間聊天/雙方在場寫入房間對話.feature

**Goal**: 調整送訊實作與快照投影，讓更新後測試全綠。

**Shared Must Read**:
- `specs/truth/features/backend/房間聊天/雙方在場寫入房間對話.feature` -> `Feature: 雙方在場寫入房間對話`
- `specs/truth/features/backend/房間聊天/dsl.md` -> `When: "{玩家}" 送出訊息 "{內容}"`, `Then: "{玩家}" 與 "{玩家}" 都看得到以下聊天內容：`
- `truth-delta.md` -> `/dsl-refine` MODIFY `When: "{玩家}" 送出訊息 "{內容}"`

**Boundary**:
- 不新增無關聊天場景。

**Test Scope**:
- `specs/truth/features/backend/房間聊天/雙方在場寫入房間對話.feature`

- [ ] T013 [BDD-GREEN] 讓 Test Scope 全綠
- [ ] T014 [BDD-REFACTOR] 在綠燈下整理聊天寫入與再讀確認共用邏輯

## Phase 4C: DELETE Feature / DSL Truth - 離房後仍可看到舊訊息

**Goal**: 移除產品碼中保留離房訊息的過期分支，並確認新版 truth 仍成立。

**Shared Must Read**:
- `specs/truth/features/backend/房間聊天/離開後清空與他房隔離.feature` -> `Feature: 離開後清空與他房隔離`
- `specs/truth/features/backend/房間聊天/dsl.md` -> `Then: "{玩家}" 看不到先前的聊天訊息`
- `truth-delta.md` -> `/dsl-refine` DELETE `Then: 對手仍看得到離房前訊息`
- `backend/app/store.py` -> 可能仍保留離房訊息的產品分支

**Boundary**:
- 只移除離房後保留舊訊息的過期語意，不移除雙方在場時的聊天歷史。

**Test Scope**:
- `specs/truth/features/backend/房間聊天/離開後清空與他房隔離.feature`

- [ ] T015 [CODE-REMOVE] 移除產品碼中保留離房訊息的過期分支
- [ ] T016 [REGRESSION] 跑 Test Scope，確認新版 truth 成立
