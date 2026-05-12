# Starter Variant: Python E2E

技術棧：FastAPI + SQLAlchemy 2.0 + Behave + Testcontainers (PostgreSQL)

---

## 目錄結構

```
${PROJECT_ROOT}/
├── .aibdd/
│   ├── arguments.yml                       # kickoff project config；starter 只讀
│   ├── dev-constitution.md                 # 產品架構 bridge（層級、依賴、持久化；對齊 DEV_CONSTITUTION_PATH）
│   └── bdd-stack/
│       ├── project-bdd-axes.md             # `${BDD_CONSTITUTION_PATH}`：§5.1 檔名軸、§5.2 Red Pre-Hook 軸
│       ├── acceptance-runner.md
│       ├── step-definitions.md
│       ├── fixtures.md
│       ├── feature-archive.md
│       └── prehandling-before-red-phase.md   # `${RED_PREHANDLING_HOOK_REF}`：python-e2e = schema-analysis／data-migration（見 §9）
├── ${PY_APP_DIR}/                          # 應用程式主目錄（例：app/）
│   ├── __init__.py
│   ├── main.py                             # FastAPI 入口（掛載 CORS、路由、/health）
│   ├── exceptions.py                       # 自定義例外：BusinessError, NotFoundError 等
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                       # Paths 類別 + Settings 類別（DB URL, JWT, API prefix）
│   │   └── deps.py                         # DI：get_db(), get_current_user_id(), set_session_factory()
│   ├── models/
│   │   ├── __init__.py                     # 匯出 Base（自 base.py）
│   │   └── base.py                         # DeclarativeBase 單一來源
│   ├── repositories/
│   │   └── __init__.py                     # 占位（docstring；業務 repo 由後續 skill 產生）
│   ├── services/
│   │   └── __init__.py                     # 占位（docstring）
│   ├── api/
│   │   └── __init__.py                     # 空 router 佔位
│   └── schemas/
│       └── __init__.py                     # 占位（docstring）
├── ${PY_TEST_FEATURES_DIR}/                # 測試目錄（例：tests/features/）；上層 `tests/__init__.py` 亦會建立
│   ├── __init__.py
│   ├── environment.py                      # Behave 環境：Testcontainers、DI override、truncate reset
│   ├── HealthCheck.feature                 # starter smoke：至少一個 .feature（Behave 1.3.x dry-run 相容）
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── http_response.py                # 共用 Then：__http transport probe
│   │   └── jwt_helper.py                   # 測試用 JWT Token 產生器
│   └── steps/
│       ├── __init__.py
│       ├── health_check.py                 # starter smoke：GET /health 步驟
│       └── common_then/
│           ├── __init__.py
│           ├── success.py                  # @then('操作成功')
│           ├── failure.py                  # @then('操作失敗，violation_type …')
│           ├── failure_with_reason.py      # @then('操作失敗，原因為 {reason}')
│           ├── operation_failure.py        # @then('操作失敗')
│           └── error_message.py            # @then('錯誤訊息應為 {msg}')
├── alembic/
│   ├── env.py                              # Alembic 環境（讀取 Base.metadata）
│   ├── script.py.mako                      # revision 範本（alembic init 慣例）
│   └── versions/                           # Migration 檔案目錄
├── ${SPECS_ROOT_DIR}/                      # 規格檔案（例：specs/）
│   ├── architecture/
│   │   ├── boundary.yml                   # kickoff：唯一 boundary id
│   │   └── component-diagram.class.mmd
│   ├── <NNN-slug>/                        # plan package；Discovery 建立 / 更新
│   │   ├── spec.md
│   │   └── reports/
│   └── <boundary>/                        # boundary truth root（例：backend）
│       ├── actors/
│       ├── contracts/                    # operation contracts; web-service uses OpenAPI via /aibdd-form-api-spec
│       ├── data/                         # boundary state truth; web-service uses DBML via /aibdd-form-entity-spec
│       ├── shared/
│       │   └── dsl.yml                    # boundary shared DSL truth
│       ├── test-strategy.yml
│       └── packages/                      # Discovery late-bind `NN-<功能模組描述>/`
├── requirements.txt
├── pyproject.toml
├── behave.ini
├── docker-compose.yml
└── alembic.ini
```

---

## 依賴安裝（pip）

`requirements.txt` 內容：

```
# BDD Testing
behave>=1.2.6
pytest>=7.0.0
typing-extensions>=4.0.0

# 開發工具
black>=23.0.0
isort>=5.0.0
mypy>=1.0.0

# === E2E 專屬 ===
# FastAPI
fastapi>=0.109.0
uvicorn>=0.27.0

# 資料庫
sqlalchemy>=2.0.0
psycopg[binary]>=3.1.0
alembic>=1.13.0

# 測試基礎設施
testcontainers[postgres]>=3.7.0
httpx>=0.26.0

# 認證
PyJWT>=2.8.0
```

安裝指令：`pip install -r requirements.txt`

---

## 設定檔說明

### behave.ini

指定 Behave 測試路徑至 `{{PY_TEST_FEATURES_DIR}}`，啟用 pretty 格式與彩色輸出，並開啟 `use_nested_step_modules` 以支援巢狀 steps package。

### docker-compose.yml

開發用 PostgreSQL 15 容器。容器名稱 `{{PROJECT_SLUG}}-postgres`，資料庫 `{{PROJECT_SLUG}}_dev`，帳密 `postgres:postgres`，port 5432。附帶 healthcheck。

### alembic.ini

指定 migration 腳本目錄 `alembic/`，預設連線 URL `postgresql+psycopg://postgres:postgres@localhost:5432/{{PROJECT_SLUG}}_dev`。env.py 會在測試時從環境變數 `DATABASE_URL` 覆寫。

必須包含 Python logging fileConfig 慣例的完整區段（`[loggers]` / `[handlers]` / `[formatters]` / `[logger_*]` / `[handler_*]` / `[formatter_*]`），因為 `alembic/env.py` 無條件呼叫 `fileConfig(config.config_file_name)`；缺任何一個 section 會導致 `before_all` hook 丟 `KeyError`，而 `behave --dry-run` 不會攔截到此缺陷。範本對應 `alembic init` 的預設輸出。

### pyproject.toml

專案 metadata（name、version、description）。包含 black、isort、mypy、behave 的工具設定。Python >= 3.11。

---

## 測試框架設定（Behave + Testcontainers）

### environment.py 生命週期

| Hook | 行為 |
|------|------|
| `before_all` | 啟動 PostgreSQL Testcontainer → 取得連線 URL → 設定 `DATABASE_URL` 環境變數 → 建立 SQLAlchemy engine → 執行 Alembic migrations (`upgrade head`) → 建立 SessionLocal → 呼叫 `set_session_factory()` |
| `before_scenario` | 初始化 context → DB Session → `dependency_overrides[get_db]` 與 Session 對齊 → TestClient → JwtHelper → `context.repos`/`context.services` |
| `after_scenario` | Rollback → `TRUNCATE … RESTART IDENTITY CASCADE`（依 metadata 排序）→ commit → 關閉 Session → 清理 context |
| `after_all` | Dispose engine → 停止 Testcontainer |

### Context 物件結構

```python
context.last_error       # str | None — 最近一次操作錯誤
context.last_response    # httpx.Response — 最近一次 HTTP 回應
context.query_result     # Any — 查詢結果
context.ids              # dict — 儲存建立的實體 ID（如 {"小明": 1}）
context.memo             # dict — 通用暫存
context.db_session       # sqlalchemy.orm.Session
context.api_client       # FastAPI TestClient
context.jwt_helper       # JwtHelper 實例
context.repos            # SimpleNamespace — 各 Repository 實例
context.services         # SimpleNamespace — 各 Service 實例
```

---

## 資料庫設定

- **開發環境**：透過 `docker-compose.yml` 啟動 PostgreSQL 15
- **測試環境**：透過 Testcontainers 自動管理（每次 test session 啟動新容器）
- **Migration**：Alembic。`alembic/env.py` 從 `{{PY_APP_MODULE}}.models` 匯入 `Base.metadata` 支援 autogenerate
- **清理策略**：每個 Scenario 結束後 TRUNCATE CASCADE 所有 tables

---

## arguments.yml 變數對照

| Placeholder | 來源 | 說明 | 範例 |
|-------------|------|------|------|
| `{{STARTER_VARIANT}}` | arguments.yml | starter variant，固定為 `python-e2e` | `python-e2e` |
| `{{PROJECT_NAME}}` | 詢問使用者 | 專案顯示名稱 | `課程平台` |
| `{{PROJECT_DESCRIPTION}}` | 詢問使用者 | 專案描述 | `BDD Workshop - Python E2E` |
| `{{PROJECT_SLUG}}` | 從 PROJECT_NAME 推導 | URL-safe 識別碼（小寫、連字號） | `course-platform` |
| `{{PY_APP_DIR}}` | arguments.yml | 應用程式目錄名 | `app` |
| `{{PY_APP_MODULE}}` | 從 PY_APP_DIR 推導 | Python module 路徑（`.` 分隔） | `app` |
| `{{PY_TEST_MODULE}}` | 從 PY_TEST_FEATURES_DIR 推導 | 測試 module 路徑 | `tests.features` |
| `{{PY_TEST_FEATURES_DIR}}` | arguments.yml | 測試 features 目錄 | `tests/features` |
| `{{PY_SHARED_STEPS_DIR}}` | arguments.yml | 共用 step definitions 目錄 | `tests/features/steps/shared` |
| `{{SPECS_ROOT_DIR}}` | arguments.yml | 規格檔案根目錄 | `specs` |
| `{{BOUNDARY_YML}}` | arguments.yml | boundary 清單（通常 `specs/architecture/boundary.yml`） | `specs/architecture/boundary.yml` |
| `{{CONTRACTS_DIR}}` | arguments.yml | boundary operation contract directory；Python `web-service` contract files are OpenAPI generated by `/aibdd-form-api-spec` | `specs/backend/contracts` |
| `{{FEATURE_SPECS_DIR}}` | arguments.yml（`/aibdd-discovery` bind 後展開） | Discovery accepted rule / behavior truth 根 | `specs/backend/packages/01-計費/features` |
| `{{ACTIVITIES_DIR}}` | arguments.yml（bind 後展開） | Discovery accepted `.activity` truth 根 | `specs/backend/packages/01-計費/activities` |
| `{{DATA_DIR}}` | arguments.yml | boundary state truth directory；Python `web-service` state files are DBML generated by `/aibdd-form-entity-spec` | `specs/backend/data` |
| `{{DEV_CONSTITUTION_PATH}}` | arguments.yml | 開發基礎建設 bridge guideline | `.aibdd/dev-constitution.md` |
| `{{BDD_CONSTITUTION_PATH}}` | arguments.yml | bdd-stack 憲法樹之 §5.1 檔名軸錨點 | `.aibdd/bdd-stack/project-bdd-axes.md` |
| （鍵）`RED_PREHANDLING_HOOK_REF` | arguments.yml §9 | Red 前 schema-analysis／migration gate；`/aibdd-red-execute` 進 Red 前必讀 | `.aibdd/bdd-stack/prehandling-before-red-phase.md` |

推導規則：
- `PROJECT_SLUG` = PROJECT_NAME 轉小寫、空格換連字號、移除特殊字元
- `PY_APP_MODULE` = PY_APP_DIR 中 `/` 換成 `.`
- `PY_TEST_MODULE` = PY_TEST_FEATURES_DIR 中 `/` 換成 `.`

Starter 安全邊界：
- `${PROJECT_ROOT}/.aibdd/arguments.yml` 必須已存在；starter 不建立、不改寫 `specs/`。
- `project_dir` 必須是已 kickoff 的 backend repo root；若 arguments path 不在同一 repo root，停止並要求重新指定。

---

## 驗證步驟

完成骨架建立後，確認以下事項：

1. **檔案完整性**：所有 template 對照表中的檔案都已寫入目標路徑（含 `.aibdd/dev-constitution.md`、`.aibdd/bdd-stack/project-bdd-axes.md`、`prehandling-before-red-phase.md` 與其餘 `bdd-stack/*.md`）；且 `arguments.yml` §9 含 `RED_PREHANDLING_HOOK_REF`
2. **Placeholder 替換**：專案中不應殘留任何 `{{...}}` 字串
3. **目錄結構**：`repositories`／`services`／`schemas` 具占位 `__init__.py`；`tests/` 與 `tests/features/` 具 package `__init__.py` 以利巢狀 step modules
4. **安裝測試**：`pip install -r requirements.txt` 能正常完成
5. **Behave 可執行**：`behave --dry-run` 不報錯（骨架內建 `HealthCheck.feature`，至少載入 1 個 scenario；Behave 1.3.x 在完全無 `.feature` 時會 `ConfigError` 退出非零）

---

## 安全規則

- 不覆蓋已存在的檔案（跳過並回報）
- 不建立 feature-specific 程式碼（models、repositories、services、API endpoints、業務 step definitions）
- 例外：`HealthCheck.feature` + `steps/health_check.py` 為 **walking skeleton starter smoke**，僅驗證既有 `/health`，不屬於產品需求 BDD
- 例外：`.aibdd/dev-constitution.md`、`.aibdd/bdd-stack/*.md`（含 `project-bdd-axes.md`）為 **AIBDD bridge／runtime guideline**，非產品程式碼亦非業務 BDD
- 不執行 `pip install` 或 `alembic init`

---

## Template 檔案對照表

| Template 檔名（`__` = `/`） | 輸出路徑 |
|------------------------------|----------|
| `.aibdd__dev-constitution.md` | `.aibdd/dev-constitution.md` |
| `.aibdd__bdd-stack__project-bdd-axes.md` | `.aibdd/bdd-stack/project-bdd-axes.md` |
| `.aibdd__bdd-stack__acceptance-runner.md` | `.aibdd/bdd-stack/acceptance-runner.md` |
| `.aibdd__bdd-stack__step-definitions.md` | `.aibdd/bdd-stack/step-definitions.md` |
| `.aibdd__bdd-stack__fixtures.md` | `.aibdd/bdd-stack/fixtures.md` |
| `.aibdd__bdd-stack__feature-archive.md` | `.aibdd/bdd-stack/feature-archive.md` |
| `.aibdd__bdd-stack__prehandling-before-red-phase.md` | `.aibdd/bdd-stack/prehandling-before-red-phase.md` |
| `requirements.txt` | `requirements.txt` |
| `pyproject.toml` | `pyproject.toml` |
| `behave.ini` | `behave.ini` |
| `docker-compose.yml` | `docker-compose.yml` |
| `alembic.ini` | `alembic.ini` |
| `app__init__.py` | `${PY_APP_DIR}/__init__.py` |
| `app__main.py` | `${PY_APP_DIR}/main.py` |
| `app__exceptions.py` | `${PY_APP_DIR}/exceptions.py` |
| `app__core__init__.py` | `${PY_APP_DIR}/core/__init__.py` |
| `app__core__config.py` | `${PY_APP_DIR}/core/config.py` |
| `app__core__deps.py` | `${PY_APP_DIR}/core/deps.py` |
| `app__models__base.py` | `${PY_APP_DIR}/models/base.py` |
| `app__models__init__.py` | `${PY_APP_DIR}/models/__init__.py` |
| `app__api__init__.py` | `${PY_APP_DIR}/api/__init__.py` |
| `alembic__env.py` | `alembic/env.py` |
| `alembic__script.py.mako` | `alembic/script.py.mako` |
| `tests__features__HealthCheck.feature` | `${PY_TEST_FEATURES_DIR}/HealthCheck.feature` |
| `tests__init__.py` | `tests/__init__.py` |
| `tests__features__init__.py` | `tests/features/__init__.py` |
| `tests__features__environment.py` | `${PY_TEST_FEATURES_DIR}/environment.py` |
| `tests__features__helpers__init__.py` | `${PY_TEST_FEATURES_DIR}/helpers/__init__.py` |
| `tests__features__helpers__http_response.py` | `${PY_TEST_FEATURES_DIR}/helpers/http_response.py` |
| `tests__features__helpers__jwt_helper.py` | `${PY_TEST_FEATURES_DIR}/helpers/jwt_helper.py` |
| `tests__features__steps__init__.py` | `${PY_TEST_FEATURES_DIR}/steps/__init__.py` |
| `tests__features__steps__health_check.py` | `${PY_TEST_FEATURES_DIR}/steps/health_check.py` |
| `tests__features__steps__common_then__init__.py` | `${PY_TEST_FEATURES_DIR}/steps/common_then/__init__.py` |
| `tests__features__steps__common_then__success.py` | `${PY_TEST_FEATURES_DIR}/steps/common_then/success.py` |
| `tests__features__steps__common_then__failure.py` | `${PY_TEST_FEATURES_DIR}/steps/common_then/failure.py` |
| `tests__features__steps__common_then__failure_with_reason.py` | `${PY_TEST_FEATURES_DIR}/steps/common_then/failure_with_reason.py` |
| `tests__features__steps__common_then__operation_failure.py` | `${PY_TEST_FEATURES_DIR}/steps/common_then/operation_failure.py` |
| `tests__features__steps__common_then__error_message.py` | `${PY_TEST_FEATURES_DIR}/steps/common_then/error_message.py` |
| `app__repositories__init__.py` | `${PY_APP_DIR}/repositories/__init__.py`（占位 docstring） |
| `app__services__init__.py` | `${PY_APP_DIR}/services/__init__.py`（占位 docstring） |
| `app__schemas__init__.py` | `${PY_APP_DIR}/schemas/__init__.py`（占位 docstring） |

額外建立（無 template，僅目錄）：
- `alembic/versions/` 空目錄

---

## 完成後引導

```
Walking skeleton 已建立完成。

下一步：
1. cd ${PROJECT_ROOT} && pip install -r requirements.txt
2. /aibdd-discovery — 開始需求探索
```
