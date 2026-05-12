# Kickoff Question Catalog

本檔是 `/aibdd-kickoff` 的互動題庫與訊息模板。`SKILL.md` 負責執行順序；本檔只保留選項、預設值、展示欄位與使用者可見文案。

## 技術堆疊確認

| Code | Stack | Framework | BDD / Test Tool | Status |
|---|---|---|---|---|
| A | Python | FastAPI + SQLAlchemy + Alembic | Behave E2E + Testcontainers | selectable |
| B | Java | Spring Boot 4 + JdbcClient + Flyway | Cucumber 7 + JUnit Platform Suite + Testcontainers | selectable |

Kickoff 的 Q1 目前提供 Python 與 Java 兩個可選答案；TypeScript、Frontend Only、Unit Test 只可在說明文字中提到「尚未支援」，不得放進 AskUserQuestion options。Q1 不得提供 `Other` / 自由輸入選項。

## 測試策略

Kickoff 不提供測試策略選單。Q1 選 Python 後固定為 Behave E2E（FastAPI TestClient + PostgreSQL via Testcontainers）；選 Java 後固定為 Cucumber E2E（MockMvc + PostgreSQL via Testcontainers `@ServiceConnection`）。

## 主要規格語言

Kickoff 只問一題 project spec language，用來推導 `PROJECT_SPEC_LANGUAGE`、`GHERKIN_EXECUTABLE_STEP_LANGUAGE_REF`、`FILENAME_AXES_TITLE_LANGUAGE_REF`。`DSL_KEY_LOCALE` 預設固定為 `prefer_spec_language`。

| Code | Language | Config value | Language asset |
|---|---|---|---|
| A | 繁體中文 | `zh-hant` | `.claude/skills/aibdd-core/references/i18n/zh-hant.md` |
| B | 簡體中文 | `zh-hans` | `.claude/skills/aibdd-core/references/i18n/zh-hans.md` |
| C | 美式英文 | `en-us` | `.claude/skills/aibdd-core/references/i18n/en-us.md` |
| D | 日文 | `ja-jp` | `.claude/skills/aibdd-core/references/i18n/ja-jp.md` |
| E | 韓文 | `ko-kr` | `.claude/skills/aibdd-core/references/i18n/ko-kr.md` |

## 唯一 TLB 命名

| Field | Default suggestion | Example | Rendering Rule |
|---|---|---|---|
| `TLB_ID` | `backend` | `course-api` | kebab-case，寫入 `boundary.yml` 的 boundary id；Java stack 同時直接成為 Maven `<artifactId>` |
| `BOUNDARY_TYPE` | `web-service` | `web-service` | 固定值 |
| `BOUNDARY_ROLE` | `backend` | `backend` | 固定值 |

## 後端佈局

| Field | Default | Example | Rendering Rule |
|---|---|---|---|
| `BACKEND_SUBDIR` | `""` | `backend` | 空字串 = backend 與 specs 直接放在 repo root；非空 = 都掛在 `${PROJECT_ROOT}/${BACKEND_SUBDIR}/` 下 |

Q4（佈局決定）必須在 Q3（service name）之後、推導確認之前發問。`subdir` 模式須收集自訂目錄名（kebab-case 建議），並更新 `arguments.yml` 的 `BACKEND_SUBDIR` 鍵；下游 `/aibdd-auto-backend-starter` 的 same-repo guard 會以 `${PROJECT_ROOT}/${BACKEND_SUBDIR}/${AIBDD_ARGUMENTS_PATH}` 為合法位置。

## Prompt Templates

### 批次提問模板

Kickoff 的初始訪談必須一次問完 Q1-Q4，不得逐題往返。建議回覆格式（Python 範例）：

```text
Q1: python_e2e
Q2: zh-hant
Q3: backend
Q4: repo_root
```

Java 範例：

```text
Q1: java_e2e
Q2: zh-hant
Q3: demo
Q4: repo_root
```

若 Q4 選子目錄，回答格式必須是：

```text
Q4: subdir:backend
```

Q3 可直接填 `backend` 或任一 kebab-case 服務名，例如：

```text
Q3: course-api
```

> Java stack 下，Q3 同時會被當成 Maven `<artifactId>`；建議純小寫、可帶連字號（如 `demo` 或 `course-api`）。`groupId` 預設為 `com.example`，使用者可在 kickoff 完成後直接編 `arguments.yml` 自訂。

### Q1 技術堆疊確認

```markdown
[Q1/4] 要建立哪一種後端 stack？

可選擇：
- Python + FastAPI + SQLAlchemy + Alembic + Behave E2E
- Java + Spring Boot 4 + JdbcClient + Flyway + Cucumber 7

| 選項 | 說明 |
|---|---|
| A | python_e2e — Python 後端 stack |
| B | java_e2e — Java 後端 stack |

TypeScript、Frontend Only、Unit Test 尚未支援；本輪不提供選擇。
```

### Q2 主要規格語言

```markdown
[Q2/4] 專案規格主要用哪一種語言撰寫？

這會決定 Gherkin 可讀文字與 feature filename title 的 language asset；DSL key 預設跟隨規格語言。

| 選項 | 說明 |
|---|---|
| A | 繁體中文（zh-hant） |
| B | 簡體中文（zh-hans） |
| C | 美式英文（en-us） |
| D | 日文（ja-jp） |
| E | 韓文（ko-kr） |
```

### Q3 唯一後端服務名稱

```markdown
[Q3/4] 這個後端服務要叫什麼名字？

建議：<project>-api（Python）或專案小寫名（Java，會直接作為 Maven artifactId）

請提供 kebab-case 名稱（如 course-api），或直接回答 `backend` 接受預設。
```

### Q4 後端佈局選擇

```markdown
[Q4/4] 後端程式碼要放在 repo root 還是子目錄？

預設是 repo root（backend 與 specs/ 直接掛在 repo 最外層）。
若選 subdir：
- Python：所有 backend code（app/、tests/、alembic/）與 specs/ 會掛在 ${PROJECT_ROOT}/${BACKEND_SUBDIR}/ 下。
- Java：所有 backend code（pom.xml、src/、docker-compose.yml）與 specs/ 會掛在 ${PROJECT_ROOT}/${BACKEND_SUBDIR}/ 下。

| 選項 | 說明 |
|---|---|
| A | repo_root：backend 在 repo root，BACKEND_SUBDIR="" |
| B | subdir：backend 在子目錄，請另提供子目錄名（kebab-case，例如 `backend`） |

選 B 時在同一批回答中寫 `Q4: subdir:<子目錄名>`（例如 `Q4: subdir:backend`）；選 A 則寫 `Q4: repo_root`。
```

### 推導結果確認

推導確認畫面確認的是「使用者可理解的專案設定」，不是 raw `arguments.yml`。完整 technical arguments 只在使用者選擇「顯示完整技術細節」時展示。

#### Q4 白話確認契約

| 區塊 | 必須呈現的白話內容 | 禁止事項 |
|---|---|---|
| 後端佈局 | 後端 filesystem 根目錄絕對路徑（`${PROJECT_ROOT}` 或 `${PROJECT_ROOT}/${BACKEND_SUBDIR}`），所有後續路徑都掛在此根之下 | 不可只列 `BACKEND_SUBDIR` 變數名 |
| 專案骨架 | AIBDD 規格文件會放在哪裡、架構文件會放在哪裡 | 不可只列 `SPECS_ROOT_DIR`、`ARCHITECTURE_DIR` |
| Boundary 文件 | 每個後端 boundary 會有 contracts / data / shared / packages（root） / test-strategy skeleton；packages 底下的功能模組目錄交由 Discovery | 不可預設展示全部 boundary-aware / late-bind 變數表 |
| 程式碼位置 | 後端或前端原始碼、models、services、API、mock、page objects 的位置（依選定 stack 顯示對應路徑） | 不可只列 `PY_APP_DIR`、`BASE_PACKAGE_PATH`、`SRC_DIR` 等參數名 |
| 測試位置 | BDD feature、step definitions、support / environment 檔的位置（依選定 stack 顯示對應路徑） | 不可只列測試參數表 |
| 資料庫與合約 | migration、contracts、workflow state 會放在哪裡 | 不可讓使用者自行推導 scope 條件 |

#### Q4 可修改項目

| Option | 使用者語意 | 會影響的 arguments 類型 |
|---|---|---|
| accept | 設定看起來合理，寫入 `${BACKEND_ROOT}/.aibdd/arguments.yml` | all |
| revise_layout | 修改 backend filesystem root（repo root vs subdirectory） | BACKEND_SUBDIR + 所有衍生路徑 |
| revise_specs | 修改 AIBDD 規格文件或架構文件位置 | common meta |
| revise_source | 修改後端 / 前端原始碼位置 | selected stack |
| revise_tests | 修改 BDD 測試情境與 step definitions 位置 | selected stack test paths |
| revise_database | 修改 migration / contracts / workflow state 位置 | backend paths |
| show_details | 顯示完整 `arguments.yml` 技術參數 | diagnostic only |
| restart | 重新確認後端設定（含 stack 重選） | all |

#### Q4 白話範例（Python E2E）

```markdown
請確認這些專案設定是否符合你的期待：

你選的是 Python + FastAPI，測試採 E2E。
主要規格語言是 <project spec language>。
唯一 top-level boundary 會是 <tlb id>。

後端佈局：
- 後端 filesystem 根目錄會在 <backend_root>
  （= ${PROJECT_ROOT}，或 ${PROJECT_ROOT}/${BACKEND_SUBDIR} 當你選 subdir）
- 以下所有路徑都相對於這個根目錄

AIBDD 規格文件：
- 專案 config 會放在 <backend_root>/.aibdd/arguments.yml
- 所有規格會放在 <backend_root>/specs/
- 架構圖與 boundary 設定會放在 <backend_root>/specs/architecture/
- 單次 plan package 的 spec、reports、clarifications 會放在 <backend_root>/specs/<NNN-slug>/

功能與 boundary 文件：
- kickoff 會直接建立 <backend_root>/specs/architecture/boundary.yml
- kickoff 會直接建立 <backend_root>/specs/architecture/component-diagram.class.mmd
- <tlb id> 會有 actors、contracts、data、shared/dsl.yml、packages（root）、test-strategy.yml（功能模組 `NN-<功能模組描述>/` 只在 `/aibdd-discovery` 綁定後建立）

Python 程式碼：
- FastAPI app 會放在 <backend_root>/app/
- models / repositories / services / api / schemas 會放在 <backend_root>/app/ 底下
- 入口檔會是 <backend_root>/app/main.py

BDD 測試：
- feature 檔會放在 <backend_root>/tests/features/
- step definitions 會放在 <backend_root>/tests/features/steps/
- Behave environment 會是 <backend_root>/tests/features/environment.py

資料庫 migration：
- Alembic migration 會放在 <backend_root>/alembic/versions/

你想怎麼處理？
- Yes，接受並寫入 <backend_root>/.aibdd/arguments.yml
- Revise layout：修改 backend 根目錄（repo root 或子目錄）
- Revise specs：修改規格文件位置
- Revise source：修改程式碼位置
- Revise tests：修改測試位置
- Revise database：修改 migration / contracts 位置
- Show technical details：顯示完整 arguments.yml
- Restart：重新確認後端設定
```

#### Q4 白話範例（Java E2E）

```markdown
請確認這些專案設定是否符合你的期待：

你選的是 Java + Spring Boot 4，測試採 E2E（Cucumber + Testcontainers）。
主要規格語言是 <project spec language>。
唯一 top-level boundary 會是 <tlb id>，同時作為 Maven <artifactId>。

後端佈局：
- 後端 filesystem 根目錄會在 <backend_root>
  （= ${PROJECT_ROOT}，或 ${PROJECT_ROOT}/${BACKEND_SUBDIR} 當你選 subdir）
- 以下所有路徑都相對於這個根目錄

AIBDD 規格文件：
- 專案 config 會放在 <backend_root>/.aibdd/arguments.yml
- 所有規格會放在 <backend_root>/specs/
- 架構圖與 boundary 設定會放在 <backend_root>/specs/architecture/
- 單次 plan package 的 spec、reports、clarifications 會放在 <backend_root>/specs/<NNN-slug>/

功能與 boundary 文件：
- kickoff 會直接建立 <backend_root>/specs/architecture/boundary.yml
- kickoff 會直接建立 <backend_root>/specs/architecture/component-diagram.class.mmd
- <tlb id> 會有 actors、contracts、data、shared/dsl.yml、packages（root）、test-strategy.yml（功能模組 `NN-<功能模組描述>/` 只在 `/aibdd-discovery` 綁定後建立）

Maven 設定：
- groupId 預設為 com.example，artifactId 為 <tlb id>
- Java base package 預設為 com.example.<tlb id 去掉連字號>
- 上述都可在 kickoff 完成後手動編 arguments.yml 自訂

Java 程式碼：
- 主程式會放在 <backend_root>/src/main/java/<base_package_path>/
- controller / service / repository / model 會放在該 package 底下
- 應用入口會是 <backend_root>/src/main/java/<base_package_path>/Application.java
- application.yaml 會放在 <backend_root>/src/main/resources/

BDD 測試：
- feature 檔會放在 <backend_root>/src/test/resources/features/
- step definitions 會放在 <backend_root>/src/test/java/<base_package_path>/steps/
- Cucumber 入口會是 <backend_root>/src/test/java/<base_package_path>/RunCucumberTest.java

資料庫 migration：
- Flyway migration 會放在 <backend_root>/src/main/resources/db/migration/

你想怎麼處理？
- Yes，接受並寫入 <backend_root>/.aibdd/arguments.yml
- Revise layout：修改 backend 根目錄（repo root 或子目錄）
- Revise specs：修改規格文件位置
- Revise source：修改程式碼位置
- Revise tests：修改測試位置
- Revise database：修改 migration / contracts 位置
- Show technical details：顯示完整 arguments.yml
- Restart：重新確認後端設定
```

## 微調模式摘要

```markdown
目前設定：

技術堆疊：<derived stack label>
測試策略：<derived strategy label>
後端佈局：<derived layout label>（repo root 或 subdir <BACKEND_SUBDIR>）
參數：共 <N> 個

要修改哪一類設定？
- 後端佈局（repo root vs subdirectory）
- 規格文件位置
- 程式碼位置
- BDD 測試位置
- migration / contracts 位置
- 重新選技術堆疊
- 顯示完整 technical arguments
```

## resume-or-restart 模板

當 `${PROJECT_ROOT}/KICKOFF_PLAN.md` 已存在時，`/aibdd-kickoff` 用此模板組成單題 clarify-loop payload，由 clarify-loop 路由到 fork / AskUserQuestion。

```yaml
question:
  id: q-resume-mode
  kind: CON
  context: |
    `${PROJECT_ROOT}/KICKOFF_PLAN.md` 已存在，可能來自上次未完成的 kickoff。
    請選擇要怎麼處理。
  question: 要從現有的 KICKOFF_PLAN.md 繼續，還是重做？
  options:
    - id: resume
      label: 繼續上次的進度
      impact: 讀取現有答案，只補沒答完的題目
    - id: restart
      label: 重新開始
      affect: 覆寫 plan、丟棄現有答案
    - id: cancel
      label: 取消這次 kickoff
      impact: 不動現有檔案，整個 skill stop
  recommendation: resume
  recommendation_rationale: 預設保留進度，避免使用者誤刪上次答案
```

## 完成訊息模板

```markdown
Kickoff 已完成。

已建立：
- <backend_root>/.aibdd/arguments.yml
- <backend_root>/specs/architecture/boundary.yml
- <backend_root>/specs/architecture/component-diagram.class.mmd
- <tlb id> 的 boundary truth skeleton（含 `packages/` root，無預建 `packages/NN-*`）

下一步，來建立專案骨架吧，請直接使用 /aibdd-auto-backend-starter，或是告訴我「繼續」。
```
