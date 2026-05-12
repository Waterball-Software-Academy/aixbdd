# Pre-Red Hook — python-e2e fill: schema-analysis（data-migration）

## §1 為什麼存在

**合法紅燈** = production 行為缺失，導致 acceptance 斷言或預期例外失敗。

若 DB schema 與 DBML truth 不一致，Behave 往往在 fixture、migration、repository 層先失敗——這是**基礎設施紅**，不是合法紅燈，且會誤導 Green worker。

→ 本 Hook 為 **Pre-Red gate**：先收斂 schema／migration，再進入 RGB cycle。

## §2 觸發條件

- `specs/<boundary>/data` 下**不存在**任何 `*.dbml` → **trivial GO**（無 truth 可比對，放行進 Red）。
- 存在 `specs/<boundary>/data/*.dbml`（通常由 `/aibdd-form-entity-spec` 產出）→ **必須**執行 §3。
- 該 boundary／功能包的 DBML 自上次 schema-analysis 後有新增或修改 → 視為過期，**重新**執行 §3。

## §3 流程

### §3.1 讀取 DBML truth

來源：`specs/<boundary>/data/*.dbml`

解析並對齊下列項目（至少）：

- Table（aggregate／entity）
- Column（name、type、nullable、default）
- Foreign key
- Enum
- Index（若 DBML 有宣告）

### §3.2 比對 SQLAlchemy models

掃描：`app/models/**/*.py`（依 `<domain-or-bounded-context>` 子目錄分區；module：`app.models`）

規則：

- 每個 DBML table 對應一個 `class …(Base)`，`__tablename__` 與 DBML 一致。
- 每個 DBML column 對應 `mapped_column(...)`，type／nullable／FK 一致。
- DBML enum 對應 Python `Enum` 與 `mapped_column(SAEnum(...))`（或專案約定之等價寫法）。

### §3.3 比對 Alembic revisions

掃描：`alembic/versions/*.py`

規則：

- migration **鏈**累積結果須與 DBML truth **語意一致**。
- 缺 table／column／enum → **必須**產生新 revision（見 §4）。
- 資料庫存在 DBML 未宣告之多餘欄位 → 記為 drift／報告，**單獨不作為阻擋 GO 的唯一理由**（除非與 NOT NULL／約束衝突）。

### §3.4 GO / NO-GO

| 狀態 | 行動 |
|---|---|
| DBML 與 models、migrations 一致 | **GO** — 進 Red |
| 缺欄位／缺 aggregate／缺 enum，且可由 model + autogenerate 安全補齊 | **自動修正**後 **GO**（§4） |
| type 衝突、FK 衝突、rename 歧義、或 autogenerate 無法安全表達 | **NO-GO** — 暫停並產出報告，交由人工 |

## §4 修正流程（python-e2e）

### §4.0 Alembic：先備 Docker Compose 資料庫環境

凡將執行 `alembic revision`、`alembic upgrade head`、`revision --autogenerate` 等**會連線資料庫**的指令：

1. **查文件**：先對照 **Alembic 官方文件**與本專案 `alembic.ini`、`alembic/env.py`、連線 URL／環境變數約定——**禁止**只靠記憶或臆測旗標與順序。
2. **預設假設**：walking skeleton 在 backend **根目錄**（與 `pyproject.toml`／`app` 同框）附 **`docker-compose.yml`**，內含本 stack **local 開發用資料庫服務**（常為單一 db service）。要把 migration **真正 apply** 到可供 Alembic 連線的實例，**預設**以該 Compose 啟動的服務為準——**禁止**無文件依據地猜連線字串或憑空假設本機預設帳密。
3. **強制步驟（若 §4 要做 migration）**  
   - **①** 在 **`docker-compose.yml` 所在目錄**執行 `docker compose up -d`（或本專案 `dev-constitution`／README 明載之等價指令），確認**資料庫服務**已就緒（例如 compose `healthcheck`、`docker compose ps`、或該映像文件建議的就緒探測）。  
   - **②** 連線與 `env.py` 預期一致後，再執行 Alembic（`current`／`upgrade head`／`revision --autogenerate` 等）。  
   - **③** 若 **Docker／Compose 不可用**、容器起不來、或**無法連上**目標資料庫（port 占用、資料庫名／帳密與 compose 不符、daemon 未跑等）→ **立刻 STOP（NO-GO）**，**不**繼續本 hook 後續自動 migration 步驟；向使用者**白話說明**缺什麼、要裝什麼、要改什麼，待其修復環境後再續。

### §4.1 新增 aggregate

1. 在 `app/models/<domain-or-bounded-context>/<aggregate>.py` 建立 model，欄位依 DBML。
2. 在 `app/models/__init__.py` 匯出，確保 Alembic `env.py` 載入 metadata。
3. `alembic revision --autogenerate -m "add <aggregate>"`
4. **人工檢視** revision；enum／index 必要時補 `op.execute(...)`。
5. 依 §4.0 確認 Compose 所啟動之資料庫可用後驗證：`alembic upgrade head`（acceptance／CI 若另起隔離資料庫／容器，仍以專案文件為準）。

### §4.2 新增或修改欄位

1. 更新對應 model 之 `mapped_column(...)`。
2. `alembic revision --autogenerate -m "alter <table>.<column>"`
3. **人工檢視**；NOT NULL 新增須處理 default／backfill。
4. `alembic upgrade head`。

### §4.3 Enum 變更

1. 更新 Python `Enum`。
2. 資料庫層 enum 演進**方言差異大**，常需手寫 `op.execute(...)`；**必須**對照 Alembic 與**目標引擎**文件，**禁止**照搬單一引擎範例當全域真理。
3. `alembic upgrade head`。

### §4.4 Rename（manual gate）

DBML／業務 rename 常被 autogenerate 誤判為 drop+add → **資料遺失風險**。**禁止**只靠 autogenerate；須人工 revision（例如 `op.alter_column`／資料搬移策略）。

## §5 失敗處理

- §4.0 環境未通（Docker／Compose／連線）→ **STOP**，依 §4.0③向使用者說明；**不**視為 RGB 失敗點數，亦不強行 autogenerate。
- `alembic upgrade head` 失敗 → 還原該 revision（例如 `alembic downgrade -1` 並移除錯誤檔），**NO-GO** 並報告。
- DBML 無法解析 → **NO-GO**，回到 `/aibdd-form-entity-spec`。

## §6 與 RGB cycle 的關係

Schema-analysis／data-migration **不計入** RGB step 編號；為 Pre-Red gate。

- **通過**後才開始計 `R(1) → G(1) → B(1)`。
- **未通過**則不啟動 Red 主流程；Red loop budget **不消耗**於「合法紅燈」計數。
