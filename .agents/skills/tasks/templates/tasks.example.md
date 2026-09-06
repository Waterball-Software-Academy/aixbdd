# Tasks: 房間聊天規格調整

**Plan Package**: `specs/plans/004-room-chat-adjustment`
**Core Inputs**: `spec.md`, `plan.md`, `research.md`, `truth-delta.md`, `specs/truth/techstack.md`, `specs/truth/contracts/**`, `specs/truth/data/**`, `specs/truth/features/backend/**`, `specs/truth/features/frontend/**`, `ui/**`

## Task Binding Contract

- 每個**開發任務**都必須對應 `truth-delta.md` 中的 ADD / MODIFY / DELETE / NOOP 語意。
- Phase 1 `Setup` 只做本輪新增技術的基礎建設、技術環境與最後的 smoke-test；不寫 DSL 語意、不寫產品行為。
- Phase 2 `Foundational` 只建立後續實作程式、測試共用元件、入口、fixture、helper 與落點骨架。
- Phase 3 `Test Alignment & Implementation` 的目的：在寫產品碼之前，先把本輪所有受影響 DSL 的自動化測試對齊最新版 truth。
- Truth 參照必須使用 `specs/truth/**` 路徑；plan 參照才使用當前 plan package 內相對路徑。

## Phase 1: Setup

**Goal**: 本輪聊天要新增 websocket。後端用 FastAPI 內建 `WebSocket` 掛端點，測試端用 `websockets` 連線。先把套件與連線配置備好，最後用 smoke-test 確認測得到一條 websocket。不寫聊天 DSL 語意，不寫送訊產品行為。

- [ ] T001 加入 `websockets` 套件與測試用連線設定
  - Read:
    - `specs/truth/techstack.md` -> 後端與測試與驗證
  - 後端測試依賴加入 `websockets`。
  - 測試設定寫清 websocket URL（例如 `ws://127.0.0.1:{port}/ws`），給後續測試讀，不寫送訊語意。

- [ ] T002 對齊後端 FastAPI websocket 技術環境
  - Read:
    - `specs/truth/techstack.md` -> 後端測試入口
    - `backend/` -> FastAPI app 與測試 server 掛載點
  - FastAPI 掛一個 `WebSocket` 端點（例如 `/ws`），讓測試 server 能接受 `websockets` 連線。
  - 只開連線；不實作送訊、清空或拒絕規則。

- [ ] T003 smoke-test 確認 `websockets` 能連上 FastAPI `/ws`
  - Read:
    - `specs/truth/techstack.md` -> 測試與驗證
  - 用 `websockets.connect` 打 T001 的 URL，確認連得上就停。
  - 不跑本輪 Feature，不寫 stepdef 語意。

## Phase 2: Foundational

**Goal**: 只建立後續實作程式、測試共用元件、入口、fixture、helper 與落點骨架，讓後續 Phase 3 不各自重開檔、不各自發明連線方式。語意對齊不放這裡。

- [ ] T004 建立聊天測試共用 helper 入口與骨架
  - Read:
    - `truth-delta.md` -> `/dsl-refine` 的聊天 ADD / MODIFY / DELETE rows
    - `backend/features/steps/shared/chat_helpers.py`
  - 只做：固定 helper 落在 `backend/features/steps/shared/chat_helpers.py`，留出後續 stepdef 會呼叫的函式殼。
  - 不做：不寫各句 StepDef 實作語意，不寫送訊、清空或拒絕規則。

- [ ] T005 建立 websocket 連線 helper
  - Read:
    - `specs/truth/techstack.md` -> 測試與驗證
    - `backend/features/steps/shared/chat_helpers.py`
  - 只做：用 `websockets.connect` 包開線／關線；context 記「玩家名 → 連線」；scenario 結束要關線。
  - 不做：不送聊天內容，不斷言誰看得到什麼。

- [ ] T006 預留房間聊天 stepdef 落點
  - Read:
    - `backend/features/steps/modules/房間聊天/操作與斷言.py`
  - 只做：確認 Phase 3 只寫進這個檔，必要時建空殼。
  - 不做：不寫 ALIGN / REMOVE / RED 語意。

- [ ] T007 建立雙玩家房間測試 fixture 入口
  - Read:
    - `specs/truth/data/**` -> 房間／玩家相關實體
    - `backend/features/steps/shared/chat_helpers.py`
  - 只做：能開兩個玩家的 websocket 連線，並對到同一房間的測試入口。
  - 不做：不寫「單人等待」「送出訊息」或空白拒絕的 DSL。

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
- T008–T014 各派一個獨立 subagent；T015 等全部回來再啟動 subagent 來 review。

- [ ] T008 [P] [BDD-ALIGN] `When: "{玩家}" 送出訊息 "{內容}"`
  - Read: `backend/features/steps/modules/房間聊天/操作與斷言.py`

- [ ] T009 [P] [BDD-ALIGN] `Then: "{玩家}" 與 "{玩家}" 都看得到以下聊天內容：`
  - Read: `backend/features/steps/modules/房間聊天/操作與斷言.py`

- [ ] T010 [P] [BDD-REMOVE] `Then: 對手仍看得到離房前訊息`
  - Read: `backend/features/steps/modules/房間聊天/操作與斷言.py`

- [ ] T011 [P] [BDD-RED] `Given: "{玩家}" 在房間內單人等待`

- [ ] T012 [P] [BDD-RED] `When: "{玩家}" 嘗試送出空白訊息`

- [ ] T013 [P] [BDD-RED] `Then: 這次聊天送出被拒絕`

- [ ] T014 [P] [BDD-RED] `Then: "{玩家}" 看不到先前的聊天訊息`

- [ ] T015 subagent review (phase quality gate)

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

- [ ] T016 [BDD-GREEN] 讓 Test Scope 全綠
- [ ] T017 [BDD-REFACTOR] 在綠燈下整理拒絕訊息與測試 helper

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

- [ ] T018 [BDD-GREEN] 讓 Test Scope 全綠
- [ ] T019 [BDD-REFACTOR] 在綠燈下整理聊天寫入與再讀確認共用邏輯

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

- [ ] T020 [CODE-REMOVE] 移除產品碼中保留離房訊息的過期分支
- [ ] T021 [REGRESSION] 跑 Test Scope，確認新版 truth 成立
