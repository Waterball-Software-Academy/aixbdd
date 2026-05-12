# Pre-Red Hook — java-e2e fill: schema-analysis（flyway-migration）

## §1 為什麼存在

**合法紅燈** = production 行為缺失，導致 acceptance 斷言或預期例外失敗。

若 DB schema 與 DBML truth 不一致，Cucumber 往往在 `@SpringBootTest` 啟動的 Flyway autoconfigure 階段就先失敗——這是**基礎設施紅**，不是合法紅燈，且會誤導 Green worker。

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

### §3.2 比對應用層查詢／寫入

掃描：`src/main/java/com/example/backend/repository/**/*.java` 與 `src/main/java/com/example/backend/model/**/*.java`

規則：

- 每個 DBML table 對應一個 Java `record`（或 POJO）位於 `model/`，欄位名稱／型別與 DBML 一致。
- `repository/` 下的 `JdbcClient` SQL 必須只引用實際存在於 migration 鏈中的 table／column。
- DBML enum：依專案約定可（a）以 PostgreSQL `ENUM` 型別 + `CREATE TYPE ...` migration，或（b）以 `VARCHAR + CHECK` 落地，再於 record 中以 Java `enum` 表示——兩擇一，**禁止**單一 boundary 內混用。

### §3.3 比對 Flyway migrations

掃描：`src/main/resources/db/migration/V*__*.sql`

規則：

- migration **鏈**累積結果須與 DBML truth **語意一致**（table set、column set、constraint、enum value）。
- 缺 table／column／enum → **必須**新增 `V{N+1}__...sql`（見 §4），**禁止**修改既有已套用之 migration。
- 資料庫存在 DBML 未宣告之多餘欄位 → 記為 drift／報告，**單獨不作為阻擋 GO 的唯一理由**（除非與 NOT NULL／約束衝突）。
- Flyway 預設 fail-on-missing-locations / out-of-order = false；若專案啟用 `spring.flyway.out-of-order=true`，須在本檔註明並在 review 時人工把關 V 編號。

### §3.4 GO / NO-GO

| 狀態 | 行動 |
|---|---|
| DBML 與 model／repository／migrations 一致 | **GO** — 進 Red |
| 缺欄位／缺 aggregate／缺 enum，且可由新 V 編號 SQL 安全補齊 | **自動修正**後 **GO**（§4） |
| type 衝突、FK 衝突、rename 歧義、或無法用單一 forward migration 安全表達 | **NO-GO** — 暫停並產出報告，交由人工 |

## §4 修正流程（java-e2e）

### §4.0 Flyway：先備 Docker Compose 資料庫環境

凡將執行 `./mvnw flyway:migrate`、`./mvnw flyway:info`、或在本機跑 `./mvnw spring-boot:run` 觸發 Flyway autoconfigure 等**會連線資料庫**的指令：

1. **查文件**：先對照 **Flyway 官方文件**與本專案 `application.yaml`（連線 URL／帳密）、`src/main/resources/db/migration/`、`spring.flyway.*` 設定——**禁止**只靠記憶或臆測旗標與順序。
2. **預設假設**：walking skeleton 在 backend **根目錄**（與 `pom.xml`、`src/` 同框）附 **`docker-compose.yml`**，內含本 stack **local 開發用 PostgreSQL 服務**（單一 `postgres` service，預設 port 5432，DB／帳密由 `backend` / `postgres` / `postgres` 占位）。要把 migration **真正 apply** 到可供 Flyway 連線的實例，**預設**以該 Compose 啟動的服務為準——**禁止**無文件依據地猜連線字串或憑空假設本機預設帳密。
3. **強制步驟（若 §4 要做 migration）**
   - **①** 在 **`docker-compose.yml` 所在目錄**執行 `docker compose up -d`（或本專案 `dev-constitution`／README 明載之等價指令），確認 `postgres` 服務已就緒（compose `healthcheck`、`docker compose ps`、或 `pg_isready`）。
   - **②** 連線資訊與 `application.yaml` 一致後，再執行 `./mvnw spring-boot:run`（讓 Boot 自動觸發 Flyway autoconfigure），或 `./mvnw flyway:info` / `flyway:migrate`（若顯式安裝 `flyway-maven-plugin`）。
   - **③** 若 **Docker／Compose 不可用**、容器起不來、或**無法連上**目標資料庫（port 占用、資料庫名／帳密與 compose 不符、daemon 未跑等）→ **立刻 STOP（NO-GO）**，**不**繼續本 hook 後續自動 migration 步驟；向使用者**白話說明**缺什麼、要裝什麼、要改什麼，待其修復環境後再續。

> Acceptance／CI 期間 `@ServiceConnection` + Testcontainers 會在每次 `@SpringBootTest` 啟動全新 PostgreSQL 容器並由 Flyway 自動套用所有 `V*__*.sql`，與 §4.0 流程互不衝突。

### §4.1 新增 aggregate

1. 依 DBML 在 `model/` 下新增 Java `record`（或 POJO），欄位與 DBML 對齊。
2. 在 `repository/` 下對應的 `JdbcClient` 查詢／寫入加入新 table 對映；首次出現的 mapping helper 留在同一 file。
3. 在 `src/main/resources/db/migration/` 加入下一個 `V{N+1}__add_<aggregate>.sql`，內含 `CREATE TABLE`、index、FK、必要的 enum 型別。
4. **人工檢視** SQL；NOT NULL 預設、外鍵 cascade 行為、unique constraint 必須與 DBML 一致。
5. 依 §4.0 確認 Compose 所啟動之資料庫可用後驗證：`./mvnw spring-boot:run` 觀察 Flyway log 出現 `Migrating schema "public" to version "<N+1>"` 並成功完成（acceptance／CI 由 Testcontainers 自動處理，不需另外手動套用）。

### §4.2 新增或修改欄位

1. 更新對應 `record`／POJO 欄位與 `repository/` 內的 SQL。
2. 加入 `V{N+1}__alter_<table>_<column>.sql`：`ALTER TABLE ... ADD COLUMN ...` / `ALTER COLUMN ...`。
3. **人工檢視**；NOT NULL 新增須先寫 backfill UPDATE，再 `ALTER COLUMN ... SET NOT NULL`，避免既有 row 違反約束。
4. `./mvnw spring-boot:run` 驗證；如失敗，回到 §3.3 找出 migration 與 DBML 對不上的條目。

### §4.3 Enum 變更

1. 若採 PostgreSQL `ENUM` 型別：用 `ALTER TYPE ... ADD VALUE ...`（PostgreSQL 12+ 同 transaction 加入新值有限制，請查 Flyway／PostgreSQL 官方文件）。
2. 若採 `VARCHAR + CHECK`：DROP 既有 CHECK 後新增；對應 Java `enum` 同步擴充。
3. **禁止**直接 `DROP TYPE` 再 `CREATE TYPE`，會破壞既有資料。

### §4.4 Rename（manual gate）

DBML／業務 rename 常被誤解為 drop+add → **資料遺失風險**。**禁止**只靠單一 forward SQL 模擬 rename；須人工 revision（`ALTER TABLE ... RENAME COLUMN`、或先 ADD 新欄位 → 寫 backfill → 再 DROP 舊欄位的兩階段 release）。

## §5 失敗處理

- §4.0 環境未通（Docker／Compose／連線）→ **STOP**，依 §4.0③向使用者說明；**不**視為 RGB 失敗點數，亦不強行套用 migration。
- `./mvnw spring-boot:run`／`flyway:migrate` 失敗 → 看 Flyway 錯誤訊息決定回退策略：
  - 尚未 commit 到 git 的新 V 檔 → 直接刪除該檔並修正後重做。
  - 已 commit 但本機 DB 已套用 → `flyway:repair` 後再修正；**禁止**手動改 `flyway_schema_history` table。
  - **NO-GO** 並報告。
- DBML 無法解析 → **NO-GO**，回到 `/aibdd-form-entity-spec`。

## §6 與 RGB cycle 的關係

Schema-analysis／flyway-migration **不計入** RGB step 編號；為 Pre-Red gate。

- **通過**後才開始計 `R(1) → G(1) → B(1)`。
- **未通過**則不啟動 Red 主流程；Red loop budget **不消耗**於「合法紅燈」計數。
