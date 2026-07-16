# SOP — 補實作 custom isa 的 StepDefinition（不分框架，恆執行）

本步驟針對 isa.yml 宣告為 `instruction_type: custom` 的指令，補上測試程式碼中尚缺的 StepDefinition。
**custom isa 的 step def 一律由本專案手寫——無論是否安裝框架皆然。**

> builtin instruction（time_control / entity_setup / api_call / response_validate / entity_validate /
> entity_non_existence_validate）的 step def **不在本步驟範圍**：安裝框架時由框架 BuiltinIsaPlugin 提供；
> 未安裝框架時另由 codegen 步驟依 instruction_type 生成（見主 SOP）。

範疇排除（不處理）：沒有被精煉成 isa 的 pass-through 句、或本身就是 isa step 語句者——只要不在
下述 custom 清單內，一律不管。

## 1. COLLECT custom isa —— 來源：isa.yml（**不看** `.isa.feature`）

從下列 isa.yml 蒐集所有 `instruction_type: custom` 的指令；**禁止**從展開後的 `.isa.feature` 反推：

- root：`${BOUNDARY_ISA}`
- 本輪 scope feature 所屬 package 的 `${TRUTH_BOUNDARY_PACKAGES_DIR}/<package>/*.isa.yml`

對每條 custom，BIND 其契約欄位：`name`、`format`（regex，含具名群組）、**`intent`（測試意圖／行為，含
Given/When/Then 角色——實作 body 的唯一依據）**、`data_format`（`data_table` / `json`，若有）、
`datatable_parameters`（若有）、`export_vars`（若有）、**`handler`（若有）**。`instruction_type` 非 custom（builtin）一律 SKIP。
若某 custom 缺 `intent` → 停下來回報 `stop_reason: custom_missing_intent`（dsl-refine 應補）。

**`handler` 決定分派**：契約帶 `handler` 且對應 dependency registry（`specs/dependencies/dependencies.yml`）某 entry 者為**外部依賴 custom**——其實作**不靠 intent 自推**，而是依 `handler` 分派到對應的具體模版（見 step 3 優先序第 0 點）。`intent` 對這類 custom 只作 WHAT 對照，不作 body 的來源。無 `handler` 的一般 custom 才走 intent 驅動手寫。

## 2. 比對測試程式碼，篩出「缺 StepDefinition」的 custom —— 來源：測試碼

READ `${STEP_DEFINITIONS_RUNTIME_REF}` 取得 step def 存放 glob。對每條 custom 的 `format`，
以 glob + grep 在既有 step def 中查詢是否已有對應 matcher（比對 `format` 主幹字樣）：

- 已存在 → SKIP（不重複實作）。
- 不存在 → 列入待實作清單。

## 3. 逐條實作待實作的 custom StepDefinition

先 READ `${STEP_DEFINITIONS_RUNTIME_REF}`、`${FIXTURES_RUNTIME_REF}` 理解共通寫法（注入、HTTP 互動、
共用 helper、禁止事項）。

**IF `${INSTALL_SPECTRUM}` 為 true** → READ
`.claude/skills/aibdd-core/assets/boundaries/${PRESET_KIND}/variants/${STARTER_VARIANT}.spectrum-custom-libs.md`
（該 variant 檔存在才讀、不存在 SKIP）——已安裝框架時 custom 可用的框架 library（符號解析／VAR 存取／
模擬時間／builtin 委派）與其使用規則；實作時**優先使用這些介面**，勿自己 parse 符號或繞過 time control。

**參照範本的優先序**：

0. **外部依賴 custom（契約帶 `handler`、對應 registry entry）→ 依 `handler` 分派到具體模版（首選且唯一來源，不退回 intent 自推）**：
   READ `.claude/skills/aibdd-core/assets/boundaries/${PRESET_KIND}/variants/${STARTER_VARIANT}/handlers/<entry.kind>-<handler>.md`
   （handler 模版依 kind 命名：同名 handler 在不同 kind 實作不同，如 external-stub 於 api 走 WireMock、於 grpc 走 grpcmock）
   的具體 step def 模版，逐 slot 填空——matcher／欄位取自本 custom 契約與該 entry 的 truth 檔（如 api 的
   operation → openapi truth 的 method/path、payload 欄位 → request/response schema，只可用 truth 宣告欄位）；
   句式有多變體（次數／payload／反面等）者依模版內變體節選對應。模版指示需替身（in-process stub 或 container）者，READ 並確認
   `variants/${STARTER_VARIANT}/test-doubles/<engine>.md` 的替身配置已由 prehandling（主 SOP step 5
   RED_PREHANDLING_HOOK）佈建、缺則據其補上（`@Import` 進 CucumberSpringConfiguration、DynamicPropertyRegistry
   覆寫 SUT 設定鍵、每情境 reset）。
   **測試套件檢查（避免生成的 stepdef 編不過）**：該 handler／test-double 檔宣告的「需要的測試套件」，
   先 CHECK 專案套件管理處（java-e2e＝專案根 `pom.xml` 的 `<dependencies>`；其他 stack 為各自 manifest）
   是否已裝；缺者**自動補進（scope=test）**，並在 red handoff 記錄補了哪些座標；套件管理處不存在或格式無法識別
   → 停下回報 `stop_reason: missing_package_manifest`，不臆造。此為 test-scope 相依（低風險、stepdef 直接需要），
   與缺框架（如 specformula，需 plugin／預處理）不同——後者仍走停下回報、不自行補框架。
   變體與 forbidden 一律承 kind-constants `<entry.kind>.yml` 的 `red_execute`。
   *（`variants/${STARTER_VARIANT}/handlers/<entry.kind>-<handler>.md` 該檔存在才走本點；不存在則回退第 2 點語言中立契約。）*
1. **既有 custom step def**（grep step glob 找形狀最近者）—— 無 `handler` 的一般 custom 首選範本。
2. 該 custom 若屬「外部資源」類、但無對應 variant handler 具體模版 → 參照 boundary `handlers/<handler>.md`（語言中立契約，據 variant 機制手寫）。
3. 其餘 builtin handler（state-builder / operation-invoke / response-verify …）**一律不參照**——那是框架已提供的
   builtin 形狀，custom 套它只會把 custom 又寫成 builtin 樣。

對每條待實作 custom：

1. **matcher**：`format` 具名群組 `(?P<x>...)` → 執行框架擷取群組（Cucumber Java：無名 `(...)`、參數依序）。
   matcher 字串須與 `format` 主幹一致。
2. **參數**：`format` 群組 ＋（`data_format: data_table` 時）`datatable_parameters` 欄位都從 Gherkin 接；
   `required: false` 但有 `default_value` 者，DataTable 未提供時在程式碼內寫死預設。
3. **行為（由 `intent` 驅動）**：以契約的 `intent` 為**唯一行為依據**——它已寫明步驟角色（Given/When/Then）
   與「觀察到什麼行為」。據此**推論**該 step def 要讀什麼（如 `last_response` / DB）、斷言什麼或做什麼，
   寫成**真實**邏輯（前置類真的建狀態、斷言類真的斷言）；VAR alias 經 `ScenarioContext` 存取。
   `intent` 只給 **WHAT**；**HOW**（讀哪個 context 物件、用什麼斷言、查哪張表）由你依專案範本推論。
   - **推論不出、或兩解皆通 → 停下來，帶該 custom 的 `format`＋`intent` DELEGATE `/clarify-loop` 與使用者確認，
     不得臆測寫入。**
4. **export**：有 `export_vars` → 執行後把對應 `$var` 寫回 ScenarioContext 供後續 step 引用。

## 互動 / STOP

- 本步驟為**人在環中**：當 `intent` 不足以決定實作，走 `/clarify-loop` 與使用者澄清。
- **headless／批次模式無法互動 → 遇到需澄清的 custom 即 STOP**，回報 `stop_reason: custom_intent_needs_clarification`
  並列出待澄清項，不要臆測硬寫。

## 禁止 / 合法紅燈

- 【嚴禁】為 builtin instruction 手寫 StepDefinition（框架已提供，重複註冊會衝突）。
- 【嚴禁】拿 builtin handler 當 custom 的實作範本（見上「參照優先序」第 3 點）。
- 【嚴禁】step def body 用 `pass`／空 body／placeholder throw／`RED-PENDING`——屬 false red，
  見 `references/legal-red-classification.md`。
- 【嚴禁】從 `.isa.feature` 反推要實作什麼；一律以 isa.yml 契約為準。

# Checklist

1. 每條已實作 custom 的 matcher 與 isa.yml `format` 主幹一致。
2. 只實作了 custom；builtin 全數未手寫。
3. 參數（`format` 群組 ＋ `datatable_parameters`）皆從 Gherkin 解析；有 `default_value` 者寫死預設。
4. 共用步驟只註冊一次；無重複註冊。
