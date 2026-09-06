# Tasks: {{FEATURE_NAME}}

**Plan Package**: `{{PLAN_PACKAGE}}`
**Core Inputs**: `spec.md`, `plan.md`, `research.md`, `truth-delta.md`, `specs/truth/techstack.md`, `specs/truth/contracts/**`, `specs/truth/data/**`, `specs/truth/features/backend/**`, `specs/truth/features/frontend/**`, `ui/**`

## Task Binding Contract

- 每個**開發任務**都必須對應 `truth-delta.md` 中的 ADD / MODIFY / DELETE / NOOP 語意。
- Phase 1 `Setup` 只做本輪新增技術的基礎建設、技術環境與最後的 smoke-test；不寫 DSL 語意、不寫產品行為。
- Phase 2 `Foundational` 只建立後續實作程式、測試共用元件、入口、fixture、helper 與落點骨架。
- Phase 3 `Test Alignment & Implementation` 的目的：在寫產品碼之前，先把本輪所有受影響 DSL 的自動化測試對齊最新版 truth。
- Truth 參照必須使用 `specs/truth/**` 路徑；plan 參照才使用當前 plan package 內相對路徑。

## Phase 1: Setup

**Goal**: {{SETUP_GOAL}}

- [ ] T{{SETUP_PACKAGE_TASK_ID}} {{SETUP_PACKAGE_TASK_TITLE}}
  - Read:
    - `specs/truth/techstack.md` -> {{SETUP_PACKAGE_TECHSTACK_SECTION}}
  - {{SETUP_PACKAGE_DEPENDENCY_ACTION}}
  - {{SETUP_PACKAGE_CONFIG_ACTION}}

- [ ] T{{SETUP_ENV_TASK_ID}} {{SETUP_ENV_TASK_TITLE}}
  - Read:
    - `specs/truth/techstack.md` -> {{SETUP_ENV_TECHSTACK_SECTION}}
    - `{{SETUP_ENV_APP_PATH}}` -> {{SETUP_ENV_MOUNT_POINT}}
  - {{SETUP_ENV_ENABLE_ACTION}}
  - {{SETUP_ENV_BOUNDARY}}

- [ ] T{{SETUP_SMOKE_TASK_ID}} {{SETUP_SMOKE_TASK_TITLE}}
  - Read:
    - `specs/truth/techstack.md` -> {{SETUP_SMOKE_TECHSTACK_SECTION}}
  - {{SETUP_SMOKE_VERIFY_ACTION}}
  - {{SETUP_SMOKE_BOUNDARY}}

## Phase 2: Foundational

**Goal**: {{FOUNDATIONAL_GOAL}}

- [ ] T{{FOUNDATIONAL_HELPER_TASK_ID}} {{FOUNDATIONAL_HELPER_TASK_TITLE}}
  - Read:
    - `truth-delta.md` -> {{FOUNDATIONAL_HELPER_TRUTH_DELTA_ROWS}}
    - `{{FOUNDATIONAL_HELPER_PATH}}`
  - 只做：{{FOUNDATIONAL_HELPER_DO}}
  - 不做：{{FOUNDATIONAL_HELPER_DONT}}

- [ ] T{{FOUNDATIONAL_CONNECTION_TASK_ID}} {{FOUNDATIONAL_CONNECTION_TASK_TITLE}}
  - Read:
    - `specs/truth/techstack.md` -> {{FOUNDATIONAL_CONNECTION_TECHSTACK_SECTION}}
    - `{{FOUNDATIONAL_CONNECTION_HELPER_PATH}}`
  - 只做：{{FOUNDATIONAL_CONNECTION_DO}}
  - 不做：{{FOUNDATIONAL_CONNECTION_DONT}}

- [ ] T{{FOUNDATIONAL_LANDING_TASK_ID}} {{FOUNDATIONAL_LANDING_TASK_TITLE}}
  - Read:
    - `{{FOUNDATIONAL_LANDING_PATH}}`
  - 只做：{{FOUNDATIONAL_LANDING_DO}}
  - 不做：{{FOUNDATIONAL_LANDING_DONT}}

- [ ] T{{FOUNDATIONAL_FIXTURE_TASK_ID}} {{FOUNDATIONAL_FIXTURE_TASK_TITLE}}
  - Read:
    - `{{FOUNDATIONAL_FIXTURE_DATA_PATH}}` -> {{FOUNDATIONAL_FIXTURE_DATA_SECTION}}
    - `{{FOUNDATIONAL_FIXTURE_HELPER_PATH}}`
  - 只做：{{FOUNDATIONAL_FIXTURE_DO}}
  - 不做：{{FOUNDATIONAL_FIXTURE_DONT}}

## Phase 3: Test Alignment & Implementation

**Goal**: 把本輪 Feature 用到的 DSL 自動化測試對齊最新版 truth；含 truth-delta 有改的句，以及本輪 Feature 用到、尚無 stepdef 的句。不寫產品行為。

**DSL 參照**:
- 每一句只屬於一個權威 `dsl.md`：同模組 `specs/truth/features/{介面}/{模組}/dsl.md`，或介面根 `specs/truth/features/{介面}/dsl.md`。不得掃其他模組。
- 本輪各句都在同模組 `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/dsl.md`。{{PHASE3_ROOT_DSL_STATUS}}
- 讀法：用 task title 的句型對到該檔那一列，以 `StepDef 實作語意` 當作測試程式碼語意。Given / When 讀 `怎麼做`、`權威狀態落地`、`回寫`；Then 讀 `必查`（`呈現結果`、`權威狀態`、`再讀確認`）。
- `truth-delta.md` 只告訴這句是 ADD / MODIFY / DELETE。語意以 `dsl.md` 那一列為準，不得用 feature 措辭或舊 stepdef 自行發明。

**Markers**:
- `[BDD-ALIGN]`：`MODIFY`。既有 stepdef 還在，但語意是舊 truth。依 `dsl.md` 該列改測試，讓它表達最新版 `StepDef 實作語意`。
- `[BDD-REMOVE]`：`DELETE`。此句已不是 truth。移除或改寫仍綁這句的 stepdef / assertion，不得留下保護舊行為的測試。
- `[BDD-RED]`：`ADD`，或本輪 Feature 用到、尚無 stepdef 的句。依 `dsl.md` 該列寫出 stepdef。完成時這句可被跑到，失敗只能是 assertion 或產品行為，不能是 undefined step。
- 三個 marker 都只動測試層，不寫產品碼。

**Shared Must Read**:
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/dsl.md`
  -> `{{PHASE3_MODULE_DSL_SENTENCE}}`
{{OPTIONAL_PHASE3_ROOT_DSL_SHARED_MUST_READ}}
- `truth-delta.md` -> `/dsl-refine` 有對應 ADD / MODIFY / DELETE 的句
- `{{PHASE3_EXISTING_STEPDEF_PATH}}`

**Boundary**:
- 一條 DSL 一個 task。
- 只改該句的 stepdef / assertion / 直接依賴的 helper。
- 不寫產品碼。
- review 啟動 subagent；本輪所有 Test Scope 不得再有 undefined step，失敗只能是 assertion 或產品行為。有 issues 就修正再 review，直到沒有任何問題。通過前不解鎖 Phase 4。

**Parallel Hint**:
- T{{PHASE3_FIRST_DSL_TASK}}–T{{PHASE3_LAST_DSL_TASK}} 各派一個獨立 subagent；T{{PHASE3_REVIEW_TASK}} 等全部回來再啟動 subagent 來 review。

- [ ] T{{ALIGN_TASK_ID}} [P] [BDD-ALIGN] `{{ALIGN_DSL_SENTENCE}}`
  - Read: `{{ALIGN_EXISTING_STEPDEF_PATH}}`

- [ ] T{{REMOVE_TASK_ID}} [P] [BDD-REMOVE] `{{REMOVE_DSL_SENTENCE}}`
  - Read: `{{REMOVE_EXISTING_STEPDEF_PATH}}`

- [ ] T{{RED_TASK_ID}} [P] [BDD-RED] `{{RED_DSL_SENTENCE}}`

- [ ] T{{PHASE3_REVIEW_TASK}} subagent review (phase quality gate)

## Phase 4A: ADD Feature File - {{INTERFACE_KIND}}/{{MODULE}}/{{ADDED_FEATURE_FILE_NAME}}.feature

**Goal**: {{ADD_FEATURE_PHASE_GOAL}}

**Shared Must Read**:
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/{{ADDED_FEATURE_FILE_NAME}}.feature` -> `Feature: {{ADDED_FEATURE_TITLE}}`
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/dsl.md` -> `{{ADDED_DSL_REQUIRED_SECTIONS}}`
- `truth-delta.md` -> `{{ADD_TRUTH_DELTA_ROWS}}`

**Boundary**:
- {{ADD_BOUNDARY_RULE}}

**Test Scope**:
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/{{ADDED_FEATURE_FILE_NAME}}.feature`

- [ ] T{{ADD_GREEN_TASK_ID}} [BDD-GREEN] 讓 Test Scope 全綠
- [ ] T{{ADD_REFACTOR_TASK_ID}} [BDD-REFACTOR] {{ADD_REFACTOR_TASK_TITLE}}

## Phase 4B: MODIFY Feature File - {{INTERFACE_KIND}}/{{MODULE}}/{{MODIFIED_FEATURE_FILE_NAME}}.feature

**Goal**: {{MODIFY_FEATURE_PHASE_GOAL}}

**Shared Must Read**:
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/{{MODIFIED_FEATURE_FILE_NAME}}.feature` -> `Feature: {{MODIFIED_FEATURE_TITLE}}`
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/dsl.md` -> `{{MODIFIED_DSL_REQUIRED_SECTIONS}}`
- `truth-delta.md` -> `{{MODIFY_TRUTH_DELTA_ROWS}}`

**Boundary**:
- {{MODIFY_BOUNDARY_RULE}}

**Test Scope**:
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/{{MODIFIED_FEATURE_FILE_NAME}}.feature`

- [ ] T{{MODIFY_GREEN_TASK_ID}} [BDD-GREEN] 讓 Test Scope 全綠
- [ ] T{{MODIFY_REFACTOR_TASK_ID}} [BDD-REFACTOR] {{MODIFY_REFACTOR_TASK_TITLE}}

## Phase 4C: DELETE Feature / DSL Truth - {{DELETED_TRUTH_UNIT}}

**Goal**: {{DELETE_PHASE_GOAL}}

**Shared Must Read**:
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/{{DELETED_FEATURE_FILE_NAME}}.feature` -> `Feature: {{DELETED_FEATURE_TITLE}}`
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/dsl.md` -> `{{DELETE_DSL_SECTIONS}}`
- `truth-delta.md` -> `{{DELETE_TRUTH_DELTA_ROWS}}`
- `{{OBSOLETE_PRODUCT_CODE_PATH}}` -> {{OBSOLETE_PRODUCT_BEHAVIOR}}

**Boundary**:
- {{DELETE_BOUNDARY_RULE}}

**Test Scope**:
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/{{DELETED_FEATURE_FILE_NAME}}.feature`

- [ ] T{{CODE_REMOVE_TASK_ID}} [CODE-REMOVE] {{CODE_REMOVE_TASK_TITLE}}
- [ ] T{{REGRESSION_TASK_ID}} [REGRESSION] 跑 Test Scope，確認新版 truth 成立
