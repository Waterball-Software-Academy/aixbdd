# Convention 對照表

## 共用參數（所有技術堆疊都包含）

### meta（skill 家族的結構基座）

| 參數 | 預設值 |
|------|--------|
| STARTER_VARIANT | `python-e2e`、`java-e2e`、或 `nextjs-storybook-cucumber-e2e`（由 Q1 決定） |
| PROJECT_SPEC_LANGUAGE | zh-hant |
| DSL_KEY_LOCALE | prefer_spec_language |
| BACKEND_SUBDIR | `""` | （backend stack 專用：`python-e2e` / `java-e2e`） |
| FRONTEND_SUBDIR | `""` | （frontend stack 專用：`nextjs-storybook-cucumber-e2e`） |
| AIBDD_CONFIG_DIR | .aibdd |
| AIBDD_ARGUMENTS_PATH | ${AIBDD_CONFIG_DIR}/arguments.yml |
| SPECS_ROOT_DIR | specs |
| PLAN_PACKAGES_DIR | ${SPECS_ROOT_DIR} |
| CURRENT_PLAN_PACKAGE | ${PLAN_PACKAGES_DIR}/<NNN-slug> |
| ACTIVITY_EXT | .activity |
| DEV_CONSTITUTION_PATH | .aibdd/dev-constitution.md |
| BDD_CONSTITUTION_PATH | .aibdd/bdd-stack/project-bdd-axes.md |
| MAX_QUESTIONS_PER_ROUND | 10 |
| PLAN_SPEC | ${CURRENT_PLAN_PACKAGE}/spec.md |
| PLAN_MD | ${CURRENT_PLAN_PACKAGE}/plan.md |
| PLAN_REPORTS_DIR | ${CURRENT_PLAN_PACKAGE}/reports |
| PLAN_COVERAGE_REPORT_DIR | ${PLAN_REPORTS_DIR}/coverage |
| PLAN_IMPLEMENTATION_DIR | ${CURRENT_PLAN_PACKAGE}/implementation |
| PLAN_SEQUENCE_DIR | ${PLAN_IMPLEMENTATION_DIR}/sequences |
| PLAN_INTERNAL_STRUCTURE | ${PLAN_IMPLEMENTATION_DIR}/internal-structure.class.mmd |
| CLARIFY_DIR | ${CURRENT_PLAN_PACKAGE}/clarify |

### Backend Root 組合規則

`BACKEND_SUBDIR` 控制後端程式碼是否放在 repo root 的子目錄：

- `BACKEND_SUBDIR = ""`（預設）→ `${BACKEND_ROOT} = ${PROJECT_ROOT}`（backend 與 specs/ 都直接掛在 repo 最外層）
- `BACKEND_SUBDIR = "<name>"`（例如 `backend`）→ `${BACKEND_ROOT} = ${PROJECT_ROOT}/${BACKEND_SUBDIR}`

所有 path 變數（`AIBDD_ARGUMENTS_PATH`、`SPECS_ROOT_DIR`、`PY_APP_DIR`、`PY_TEST_FEATURES_DIR`、`ALEMBIC_VERSIONS_DIR` 等）都解析為 `${BACKEND_ROOT}/<value>`。下游 `/aibdd-auto-starter` 的 same-repo guard 會以 `${BACKEND_ROOT}/${AIBDD_ARGUMENTS_PATH}` 為唯一合法 args 位置。

### Frontend Root 組合規則

`FRONTEND_SUBDIR` 控制前端程式碼是否放在 repo root 的子目錄（語意與 `BACKEND_SUBDIR` 對稱）：

- `FRONTEND_SUBDIR = ""`（預設）→ `${FRONTEND_ROOT} = ${PROJECT_ROOT}`（frontend 與 specs/ 都直接掛在 repo 最外層）
- `FRONTEND_SUBDIR = "<name>"`（例如 `oxo`）→ `${FRONTEND_ROOT} = ${PROJECT_ROOT}/${FRONTEND_SUBDIR}`

所有 path 變數（`AIBDD_ARGUMENTS_PATH`、`SPECS_ROOT_DIR`、`FE_APP_DIR`、`FE_FEATURES_DIR` 等）都解析為 `${FRONTEND_ROOT}/<value>`。下游 `/aibdd-auto-frontend-starter` 的 same-repo guard 會以 `${FRONTEND_ROOT}/${AIBDD_ARGUMENTS_PATH}` 為唯一合法 args 位置。

### truth（佔位符：`<boundary>`；function package late-bound）

| 參數 | 預設值 |
|------|--------|
| TRUTH_ARCHITECTURE_DIR | ${SPECS_ROOT_DIR}/architecture |
| TRUTH_BOUNDARY_ROOT | ${SPECS_ROOT_DIR}/\<boundary\> |
| TRUTH_BOUNDARY_SHARED_DIR | ${TRUTH_BOUNDARY_ROOT}/shared |
| TRUTH_BOUNDARY_PACKAGES_DIR | ${TRUTH_BOUNDARY_ROOT}/packages |

`<boundary>` 由 `${BOUNDARY_YML}` 的唯一 kickoff boundary `id` 展開。**Kickoff 不得**宣告 active `TRUTH_FUNCTION_PACKAGE`、`FEATURE_SPECS_DIR`、`ACTIVITIES_DIR`、`TRUTH_TEST_PLAN_DIR`、`BOUNDARY_PACKAGE_DSL`。這些鍵只能在 `/aibdd-discovery` 完成 raw idea sourcing 並選定 `NN-<功能模組描述>` 後 **late-bind** 寫入 `arguments.yml`。

### boundary-aware（由 truth 變數推導；kickoff 只保證到 boundary root）

Kickoff 只建立一個 L1 backend boundary。`<boundary>` 必須直接解析為 boundary `id`，所以唯一 boundary root 是 `${SPECS_ROOT_DIR}/<id>`。**功能模組行為 truth**（activities / features / test-plan / package `dsl.yml`）只能在 Discovery 綁定 `TRUTH_FUNCTION_PACKAGE` 後，透過對應變數取得；不得在 kickoff 後假設任一 `packages/NN-*` 已存在。

每個變數有 scope，skill 使用前做 scope 驗證。

| 參數 | 預設值 | scope | 額外條件 |
|------|--------|-------|---------|
| BOUNDARY_YML | ${TRUTH_ARCHITECTURE_DIR}/boundary.yml | global | — |
| COMPONENT_DIAGRAM | ${TRUTH_ARCHITECTURE_DIR}/component-diagram.class.mmd | global | — |
| CONTRACTS_DIR | ${TRUTH_BOUNDARY_ROOT}/contracts | backend | — |
| DATA_DIR | ${TRUTH_BOUNDARY_ROOT}/data | backend | — |
| BOUNDARY_SHARED_DSL | ${TRUTH_BOUNDARY_SHARED_DIR}/dsl.yml | backend | written by `/aibdd-plan`（必要時）與 promotion 流程 |
| TEST_STRATEGY_FILE | ${TRUTH_BOUNDARY_ROOT}/test-strategy.yml | backend | — |

**Plan-cycle late-bind（`/aibdd-discovery` 寫入；kickoff `arguments.yml` 範例中以註解佔位）**

| 參數 | 預設值（綁定後） | scope |
|------|------------------|--------|
| TRUTH_FUNCTION_PACKAGE | ${TRUTH_BOUNDARY_PACKAGES_DIR}/NN-\<功能模組描述\> | backend |
| FEATURE_SPECS_DIR | ${TRUTH_FUNCTION_PACKAGE}/features | backend |
| ACTIVITIES_DIR | ${TRUTH_FUNCTION_PACKAGE}/activities | backend |
| TRUTH_TEST_PLAN_DIR | ${TRUTH_FUNCTION_PACKAGE}/test-plan | backend |
| BOUNDARY_PACKAGE_DSL | ${TRUTH_FUNCTION_PACKAGE}/dsl.yml | backend |

scope 值意義：

- `internal` = `role ∈ {frontend, backend}`（external 一律無權使用）
- `frontend` / `backend` = 僅該 role
- 額外條件 = `level` + `type` 條件聯合判斷（未滿足 → 變數不可用）

綁定後的 `FEATURE_SPECS_DIR` / `ACTIVITIES_DIR` 是 accepted behavior truth 的落點；plan package 內的 `spec.md` / `reports/**` 只放本次工作證據與 summary，不複製 truth content。

## Python E2E

| 參數 | 預設值 |
|------|--------|
| PY_APP_DIR | app |
| PY_MODELS_DIR | ${PY_APP_DIR}/models |
| PY_REPOSITORIES_DIR | ${PY_APP_DIR}/repositories |
| PY_SERVICES_DIR | ${PY_APP_DIR}/services |
| PY_API_DIR | ${PY_APP_DIR}/api |
| PY_CORE_DIR | ${PY_APP_DIR}/core |
| PY_SCHEMAS_DIR | ${PY_APP_DIR}/schemas |
| PY_MAIN_FILE | ${PY_APP_DIR}/main.py |
| PY_TEST_FEATURES_DIR | tests/features |
| PY_STEPS_DIR | ${PY_TEST_FEATURES_DIR}/steps |
| PY_ENV_FILE | ${PY_TEST_FEATURES_DIR}/environment.py |
| PY_SHARED_STEPS_DIR | ${PY_TEST_FEATURES_DIR}/steps/shared |
| ALEMBIC_VERSIONS_DIR | alembic/versions |

## Java E2E

| 參數 | 預設值 / 推導規則 |
|------|--------|
| GROUP_ID | `com.example`（kickoff 不問；可手動編 `arguments.yml` 改） |
| ARTIFACT_ID | `${TLB_ID}`（Q3 答案直接作為 Maven artifactId） |
| BASE_PACKAGE | `${GROUP_ID}.<artifact_id without hyphens>`（例：`course-api` → `com.example.courseapi`） |
| BASE_PACKAGE_PATH | 由 starter 從 `BASE_PACKAGE` 推導（`.` → `/`） |
| JAVA_VERSION | `25` |
| SPRING_BOOT_VERSION | `4.0.6` |
| CUCUMBER_VERSION | `7.34.3` |
| JJWT_VERSION | `0.12.6` |
| POSTGRES_IMAGE_VERSION | `18` |
| DB_NAME | `${ARTIFACT_ID}` |
| DB_USER | `postgres` |
| DB_PASSWORD | `postgres` |
| DB_PORT | `5432` |

> Java stack 的所有 source / test 落點（`src/main/java/<base_package_path>/`、`src/test/resources/features/` 等）由 starter 從 `BASE_PACKAGE_PATH` 推導；kickoff 不在 `arguments.yml` 列舉這些路徑。完整輸出規範見 `aibdd-auto-starter/references/variants/java-e2e.md`。

## Unsupported Variants

其他 frontend 框架（Vue / Svelte 等）、Unit Test only、Mobile 在 kickoff 互動中只可顯示為「尚未支援」，不得寫入 artifact plan 或 `arguments.yml`。TypeScript / Next.js 已透過 `stack=nextjs_playwright` 支援；其他 TypeScript 後端（Nest / Hono 等）尚未支援。

## arguments.yml 範例

範例分三個 stack，分別由 `assets/templates/arguments.template.yml`（python-e2e）、`assets/templates/arguments.template.java-e2e.yml`（java-e2e）與 `assets/templates/arguments.template.nextjs-playwright.yml`（nextjs-playwright）渲染：

### Python E2E

```yaml
# ── meta ──────────────────────────────────────────────
STARTER_VARIANT: python-e2e
PROJECT_SPEC_LANGUAGE: zh-hant
DSL_KEY_LOCALE: prefer_spec_language
BACKEND_SUBDIR: ""
AIBDD_CONFIG_DIR: .aibdd
AIBDD_ARGUMENTS_PATH: ${AIBDD_CONFIG_DIR}/arguments.yml
SPECS_ROOT_DIR: specs
PLAN_PACKAGES_DIR: ${SPECS_ROOT_DIR}
CURRENT_PLAN_PACKAGE: ${PLAN_PACKAGES_DIR}/<NNN-slug>
MAX_QUESTIONS_PER_ROUND: 10
ACTIVITY_EXT: .activity
DEV_CONSTITUTION_PATH: .aibdd/dev-constitution.md
BDD_CONSTITUTION_PATH: .aibdd/bdd-stack/project-bdd-axes.md

PLAN_SPEC: ${CURRENT_PLAN_PACKAGE}/spec.md
PLAN_MD: ${CURRENT_PLAN_PACKAGE}/plan.md
PLAN_REPORTS_DIR: ${CURRENT_PLAN_PACKAGE}/reports
PLAN_COVERAGE_REPORT_DIR: ${PLAN_REPORTS_DIR}/coverage
PLAN_IMPLEMENTATION_DIR: ${CURRENT_PLAN_PACKAGE}/implementation
PLAN_SEQUENCE_DIR: ${PLAN_IMPLEMENTATION_DIR}/sequences
PLAN_INTERNAL_STRUCTURE: ${PLAN_IMPLEMENTATION_DIR}/internal-structure.class.mmd
CLARIFY_DIR: ${CURRENT_PLAN_PACKAGE}/clarify

# ── truth ─────────────────────────────────────────────
TRUTH_ARCHITECTURE_DIR: ${SPECS_ROOT_DIR}/architecture
TRUTH_BOUNDARY_ROOT: ${SPECS_ROOT_DIR}/<boundary>
TRUTH_BOUNDARY_SHARED_DIR: ${TRUTH_BOUNDARY_ROOT}/shared
TRUTH_BOUNDARY_PACKAGES_DIR: ${TRUTH_BOUNDARY_ROOT}/packages

# ── late-bound by /aibdd-discovery ────────────────────
# Kickoff never creates or selects NN-<功能模組描述>.
# BIND after raw idea sourcing + package slug selection only:
# TRUTH_FUNCTION_PACKAGE: ${TRUTH_BOUNDARY_PACKAGES_DIR}/NN-<功能模組描述>
# FEATURE_SPECS_DIR: ${TRUTH_FUNCTION_PACKAGE}/features
# ACTIVITIES_DIR: ${TRUTH_FUNCTION_PACKAGE}/activities
# TRUTH_TEST_PLAN_DIR: ${TRUTH_FUNCTION_PACKAGE}/test-plan
# BOUNDARY_PACKAGE_DSL: ${TRUTH_FUNCTION_PACKAGE}/dsl.yml

BOUNDARY_YML: ${TRUTH_ARCHITECTURE_DIR}/boundary.yml
COMPONENT_DIAGRAM: ${TRUTH_ARCHITECTURE_DIR}/component-diagram.class.mmd
CONTRACTS_DIR: ${TRUTH_BOUNDARY_ROOT}/contracts
DATA_DIR: ${TRUTH_BOUNDARY_ROOT}/data
BOUNDARY_SHARED_DSL: ${TRUTH_BOUNDARY_SHARED_DIR}/dsl.yml
TEST_STRATEGY_FILE: ${TRUTH_BOUNDARY_ROOT}/test-strategy.yml

# ── AIBDD framework rule refs / language assets ────────
GHERKIN_RULE_BODY_PREFIX_POLICY_REF: .claude/skills/aibdd-core/references/gherkin-rule-body-prefix-policy/four-rules-prefix.md
GHERKIN_EXECUTABLE_STEP_LANGUAGE_REF: .claude/skills/aibdd-core/references/i18n/zh-hant.md
FILENAME_AXES_CONVENTION_REF: .claude/skills/aibdd-core/references/filename-axes-convention/nn-prefix-then-title.md
FILENAME_AXES_TITLE_LANGUAGE_REF: .claude/skills/aibdd-core/references/i18n/zh-hant.md
DSL_OUTPUT_CONTRACT_REF: .claude/skills/aibdd-core/references/dsl-output-contract/red-usable-l1-l4.md
BACKEND_PRESET_CONTRACT_REF: .claude/skills/aibdd-core/references/preset-contract/web-backend.md

# ── starter-generated project BDD stack refs ───────────
ACCEPTANCE_RUNNER_RUNTIME_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/acceptance-runner.md
STEP_DEFINITIONS_RUNTIME_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/step-definitions.md
FIXTURES_RUNTIME_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/fixtures.md
FEATURE_ARCHIVE_RUNTIME_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/feature-archive.md
RED_PREHANDLING_HOOK_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/prehandling-before-red-phase.md

# ── Python E2E starter output path bindings ────────────
PY_APP_DIR:          app
PY_MODELS_DIR:       ${PY_APP_DIR}/models
PY_REPOSITORIES_DIR: ${PY_APP_DIR}/repositories
PY_SERVICES_DIR:     ${PY_APP_DIR}/services
PY_API_DIR:          ${PY_APP_DIR}/api
PY_CORE_DIR:         ${PY_APP_DIR}/core
PY_SCHEMAS_DIR:      ${PY_APP_DIR}/schemas
PY_MAIN_FILE:        ${PY_APP_DIR}/main.py
PY_TEST_FEATURES_DIR: tests/features
PY_STEPS_DIR:        ${PY_TEST_FEATURES_DIR}/steps
PY_ENV_FILE:         ${PY_TEST_FEATURES_DIR}/environment.py
PY_SHARED_STEPS_DIR: ${PY_TEST_FEATURES_DIR}/steps/shared
ALEMBIC_VERSIONS_DIR: alembic/versions
```

### Java E2E

```yaml
# ── meta ──────────────────────────────────────────────
STARTER_VARIANT: java-e2e
PROJECT_SPEC_LANGUAGE: zh-hant
DSL_KEY_LOCALE: prefer_spec_language
BACKEND_SUBDIR: ""
AIBDD_CONFIG_DIR: .aibdd
AIBDD_ARGUMENTS_PATH: ${AIBDD_CONFIG_DIR}/arguments.yml
SPECS_ROOT_DIR: specs
PLAN_PACKAGES_DIR: ${SPECS_ROOT_DIR}
CURRENT_PLAN_PACKAGE: ${PLAN_PACKAGES_DIR}/<NNN-slug>
MAX_QUESTIONS_PER_ROUND: 10
ACTIVITY_EXT: .activity
DEV_CONSTITUTION_PATH: .aibdd/dev-constitution.md
BDD_CONSTITUTION_PATH: .aibdd/bdd-stack/project-bdd-axes.md

# ── truth ─────────────────────────────────────────────
TRUTH_ARCHITECTURE_DIR: ${SPECS_ROOT_DIR}/architecture
TRUTH_BOUNDARY_ROOT: ${SPECS_ROOT_DIR}/<boundary>
TRUTH_BOUNDARY_SHARED_DIR: ${TRUTH_BOUNDARY_ROOT}/shared
TRUTH_BOUNDARY_PACKAGES_DIR: ${TRUTH_BOUNDARY_ROOT}/packages

# ── late-bound by /aibdd-discovery（同 Python E2E）

BOUNDARY_YML: ${TRUTH_ARCHITECTURE_DIR}/boundary.yml
COMPONENT_DIAGRAM: ${TRUTH_ARCHITECTURE_DIR}/component-diagram.class.mmd
CONTRACTS_DIR: ${TRUTH_BOUNDARY_ROOT}/contracts
DATA_DIR: ${TRUTH_BOUNDARY_ROOT}/data
BOUNDARY_SHARED_DSL: ${TRUTH_BOUNDARY_SHARED_DIR}/dsl.yml
TEST_STRATEGY_FILE: ${TRUTH_BOUNDARY_ROOT}/test-strategy.yml

# ── AIBDD framework rule refs / language assets（同 Python E2E）

# ── starter-generated project BDD stack refs（同 Python E2E）
ACCEPTANCE_RUNNER_RUNTIME_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/acceptance-runner.md
STEP_DEFINITIONS_RUNTIME_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/step-definitions.md
FIXTURES_RUNTIME_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/fixtures.md
FEATURE_ARCHIVE_RUNTIME_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/feature-archive.md
RED_PREHANDLING_HOOK_REF: ${AIBDD_CONFIG_DIR}/bdd-stack/prehandling-before-red-phase.md

# ── Java E2E starter Maven coordinates / 套件落點 ─────
GROUP_ID: com.example
ARTIFACT_ID: demo                  # = TLB id（Q3 答案）
BASE_PACKAGE: com.example.demo     # = ${GROUP_ID}.<artifact_id without hyphens>

# Stack versions
JAVA_VERSION: "25"
SPRING_BOOT_VERSION: "4.0.6"
CUCUMBER_VERSION: "7.34.3"
JJWT_VERSION: "0.12.6"
POSTGRES_IMAGE_VERSION: "18"

# Local PostgreSQL（docker-compose）
DB_NAME: demo
DB_USER: postgres
DB_PASSWORD: postgres
DB_PORT: "5432"
```

> Java starter 的 source / test 目錄座標（`src/main/java/<base_package_path>/`、`src/test/resources/features/` 等）由 `/aibdd-auto-starter` 從 `BASE_PACKAGE` / `BASE_PACKAGE_PATH` 推導，不在 `arguments.yml` 列舉。

## Boundary Path Resolution（consumer 側）

`.aibdd/arguments.yml` 不列舉具體 boundary id；skill 依 `${BOUNDARY_YML}` 動態取得唯一 kickoff boundary：

```yaml
# specs/architecture/boundary.yml（由 /aibdd-kickoff 產出）
version: 2
boundaries:
  - id: backend
    level: 1
    role: backend
    type: web-service
    description: backend Python FastAPI backend service
```

下游 skill 在 kickoff 專案中以 `boundary.id` 替換 `<boundary>`。因此 `TRUTH_BOUNDARY_ROOT` 會解析為 `specs/backend`，`TRUTH_BOUNDARY_PACKAGES_DIR` 會解析為 `specs/backend/packages`。在 Discovery 綁定前，`TRUTH_FUNCTION_PACKAGE` / `FEATURE_SPECS_DIR` / `ACTIVITIES_DIR` **不存在於** `.aibdd/arguments.yml`，不得被推斷為 `specs/backend/packages/01-<id>`。scope 驗證規則見本表 scope 列與 `aibdd-core::spec-package-paths.md`。

注意：以上 `specs/` 為相對路徑，實際檔案系統位置為 `${BACKEND_ROOT}/specs/`，其中 `${BACKEND_ROOT} = ${PROJECT_ROOT}/${BACKEND_SUBDIR}`（`BACKEND_SUBDIR = ""` 時退化為 `${PROJECT_ROOT}`）。

## Starter Skill 對照表

### 後端 Starter

| 技術堆疊 + 測試策略 | Starter Skill |
|---------------------|---------------|
| Python + E2E Test | `/aibdd-auto-starter`（變體：`python-e2e`） |
| Java + E2E Test | `/aibdd-auto-starter`（變體：`java-e2e`） |
| TypeScript + E2E Test | （尚未建立） |

### 前端 Starter

| 技術堆疊 + 測試策略 | Starter Skill |
|---------------------|---------------|
| Next.js 16 + Storybook + Playwright BDD | `/aibdd-auto-starter`（變體：`nextjs-storybook-cucumber-e2e`） |
| API-first MSW workflow | `/aibdd-auto-frontend-apifirst-msw-starter` |

前端 starter 永遠顯示，不受 Q1 技術堆疊選擇影響。
specformula Phase 03（Frontend Engineering）需要前端骨架已就位。
