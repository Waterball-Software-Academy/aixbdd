# Tasks: {{FEATURE_NAME}}

**Plan Package**: `{{PLAN_PACKAGE}}`
**Core Inputs**: `spec.md`, `plan.md`, `research.md`, `truth-delta.md`, `specs/truth/techstack.md`, `specs/truth/contracts/**`, `specs/truth/data/**`, `specs/truth/features/backend/**`, `specs/truth/features/frontend/**`, `ui/**`

## Task Binding Contract

- 每個**開發任務**都必須對應 `truth-delta.md` 中的 ADD / MODIFY / DELETE / NOOP 語意，並引用實際存在、且有 `dsl.md` 可承接的 truth interface `.feature` 檔或 DSL 句型。
- 每個 Feature File phase 必須引用同模組 `dsl.md`；只有該 feature 實際使用介面根共用 DSL row 時，才列出根 `dsl.md` 與精確句型，否則省略該行。
- `Setup` / `Foundational` phase 可存在，但只能建立測試入口、共用 fixture、shared helper、DSL 承接骨架與後續 feature phases 的共同依賴；不得偷做某個故事的完整功能。
- 若 `truth-delta.md` 含 `MODIFY` 或 `DELETE`，必須先建立 `Truth Delta Impact Audit` phase，盤點既有自動化測試、step definitions、fixtures、helpers 與產品行為。
- `ADD` 使用 `[BDD-RED] -> [BDD-GREEN] -> [BDD-REFACTOR]`。
- `MODIFY` 使用 `[BDD-ALIGN] -> [BDD-GREEN] -> [BDD-REFACTOR]`。
- `DELETE` 使用 `[BDD-REMOVE] -> [CODE-REMOVE] -> [REGRESSION]`。
- Truth 參照必須使用 `specs/truth/**` 路徑；plan 參照才使用當前 plan package 內相對路徑。

## Phase 1: Truth Delta Impact Audit

**Goal**: {{IMPACT_AUDIT_GOAL}}

- [ ] T001 盤點本輪 MODIFY / DELETE truth rows 影響的既有自動化測試與產品行為
  - Read:
    - `truth-delta.md` -> `{{TRUTH_DELTA_MODIFY_DELETE_ROWS}}`
    - `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/{{FEATURE_FILE_NAME}}.feature` -> `{{AFFECTED_FEATURE_SECTION}}`
    - `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/dsl.md` -> `{{AFFECTED_DSL_SECTION}}`
    {{OPTIONAL_AFFECTED_SHARED_DSL_REFERENCE}}
    - `{{EXISTING_TEST_ENTRY}}` -> `{{EXISTING_TEST_SURFACE}}`

## Phase 2: Setup / Foundational

**Goal**: {{SETUP_OR_FOUNDATIONAL_GOAL}}

- [ ] T002 {{SETUP_OR_FOUNDATIONAL_TASK_TITLE}}
  - Read:
    - `truth-delta.md` -> `{{TRUTH_DELTA_RELEVANT_ROWS}}`
    - `specs/truth/contracts/openapi.yaml` -> `{{CONTRACT_SECTION}}`
    - `specs/truth/data/data-model.dbml` -> `{{DATA_SECTION}}`

## Phase 3A: ADD Feature File - {{INTERFACE_KIND}}/{{MODULE}}/{{ADDED_FEATURE_FILE_NAME}}.feature

**Goal**: {{ADD_FEATURE_PHASE_GOAL}}

**Shared Must Read**:
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/{{ADDED_FEATURE_FILE_NAME}}.feature` -> `Feature: {{ADDED_FEATURE_TITLE}}`
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/dsl.md` -> `{{ADDED_DSL_REQUIRED_SECTIONS}}`
{{OPTIONAL_ADDED_SHARED_DSL_REFERENCE}}
- `truth-delta.md` -> `{{ADD_TRUTH_DELTA_ROWS}}`
- `spec.md` -> `{{SPEC_RELEVANT_SECTIONS}}`

**Boundary**:
- {{ADD_BOUNDARY_RULE_1}}
- {{ADD_BOUNDARY_RULE_2}}

- [ ] T003 [BDD-RED] {{BDD_RED_TASK_TITLE}}
- [ ] T004 [BDD-GREEN] {{BDD_GREEN_TASK_TITLE}}
  - Extra Read:
    - `specs/truth/contracts/openapi.yaml` -> `{{CONTRACT_EXTRA_SECTION}}`
    - `specs/truth/data/data-model.dbml` -> `{{DATA_EXTRA_SECTION}}`
    - `research.md` -> `{{RESEARCH_EXTRA_SECTION}}`
- [ ] T005 [BDD-REFACTOR] {{BDD_REFACTOR_TASK_TITLE}}

## Phase 3B: MODIFY Feature File - {{INTERFACE_KIND}}/{{MODULE}}/{{MODIFIED_FEATURE_FILE_NAME}}.feature

**Goal**: {{MODIFY_FEATURE_PHASE_GOAL}}

**Shared Must Read**:
- `truth-delta.md` -> `{{MODIFY_TRUTH_DELTA_ROWS}}`
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/{{MODIFIED_FEATURE_FILE_NAME}}.feature` -> `Feature: {{MODIFIED_FEATURE_TITLE}}`
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/dsl.md` -> `{{MODIFIED_DSL_REQUIRED_SECTIONS}}`
{{OPTIONAL_MODIFIED_SHARED_DSL_REFERENCE}}
- `{{EXISTING_STEP_DEFINITIONS}}` -> `{{AFFECTED_STEP_DEFINITIONS}}`
- `{{EXISTING_HELPERS_OR_FIXTURES}}` -> `{{AFFECTED_HELPERS_OR_FIXTURES}}`

**Boundary**:
- {{MODIFY_BOUNDARY_RULE_1}}
- {{MODIFY_BOUNDARY_RULE_2}}

- [ ] T006 [BDD-ALIGN] {{BDD_ALIGN_TASK_TITLE}}
- [ ] T007 [BDD-GREEN] {{BDD_GREEN_MODIFY_TASK_TITLE}}
- [ ] T008 [BDD-REFACTOR] {{BDD_REFACTOR_MODIFY_TASK_TITLE}}

## Phase 3C: DELETE Feature / DSL Truth - {{DELETED_TRUTH_UNIT}}

**Goal**: {{DELETE_PHASE_GOAL}}

**Shared Must Read**:
- `truth-delta.md` -> `{{DELETE_TRUTH_DELTA_ROWS}}`
- `specs/truth/features/{{INTERFACE_KIND}}/{{MODULE}}/dsl.md` -> `{{DELETE_DSL_SECTIONS}}`
{{OPTIONAL_DELETE_SHARED_DSL_REFERENCE}}
- `{{EXISTING_STEP_DEFINITIONS}}` -> `{{OBSOLETE_STEP_DEFINITIONS}}`
- `{{EXISTING_PRODUCT_CODE}}` -> `{{OBSOLETE_PRODUCT_BEHAVIOR}}`

**Boundary**:
- {{DELETE_BOUNDARY_RULE_1}}
- {{DELETE_BOUNDARY_RULE_2}}

- [ ] T009 [BDD-REMOVE] {{BDD_REMOVE_TASK_TITLE}}
- [ ] T010 [CODE-REMOVE] {{CODE_REMOVE_TASK_TITLE}}
- [ ] T011 [REGRESSION] {{REGRESSION_TASK_TITLE}}
