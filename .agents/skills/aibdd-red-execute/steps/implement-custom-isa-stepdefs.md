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

對每條 custom，BIND 其契約欄位：`name`、`format`（regex，含具名群組）、`data_format`
（`data_table` / `json`，若有）、`datatable_parameters`（若有）、`export_vars`（若有）。
`instruction_type` 非 custom（builtin）一律 SKIP。

## 2. 比對測試程式碼，篩出「缺 StepDefinition」的 custom —— 來源：測試碼

READ `${STEP_DEFINITIONS_RUNTIME_REF}` 取得 step def 存放 glob。對每條 custom 的 `format`，
以 glob + grep 在既有 step def 中查詢是否已有對應 matcher（比對 `format` 主幹字樣）：

- 已存在 → SKIP（不重複實作）。
- 不存在 → 列入待實作清單。

## 3. 逐條實作待實作的 custom StepDefinition

先 READ `${STEP_DEFINITIONS_RUNTIME_REF}`、`${FIXTURES_RUNTIME_REF}`，理解本專案 step def 的共通寫法
（依賴注入、HTTP 互動方式、共用 helper、禁止事項）。對每條待實作 custom：

1. **matcher**：把 isa.yml `format` 的具名群組 `(?P<x>...)` 轉成執行框架的擷取群組
   （Cucumber Java：改為無名 `(...)`、方法參數依序對應）。matcher 字串須與 `format` 主幹一致。
2. **參數**：`format` 擷取的群組 ＋（`data_format: data_table` 時）`datatable_parameters` 宣告的欄位，
   都要從 Gherkin 接進來。欄位 `required: false` 但有 `default_value` 者，DataTable 未提供時在程式碼內寫死預設。
3. **實作**：依該 custom 的測試意圖寫**真實**邏輯——前置／狀態類 custom 真的建狀態（走專案的 DB／fixture
   共用 helper），VAR alias 經 `ScenarioContext` 存取（例如 `alias + ".id"`）；產出須冪等。
4. **export**：若契約有 `export_vars`，執行後把對應 `$var` 寫回 ScenarioContext 供後續 step 引用。

## 禁止 / 合法紅燈

- 【嚴禁】為 builtin instruction 手寫 StepDefinition（框架已提供，重複註冊會衝突）。
- 【嚴禁】step def body 用 `pass`／空 body／placeholder throw／`RED-PENDING`——屬 false red，
  見 `references/legal-red-classification.md`。
- 【嚴禁】從 `.isa.feature` 反推要實作什麼；一律以 isa.yml 契約為準。

# Checklist

1. 每條已實作 custom 的 matcher 與 isa.yml `format` 主幹一致。
2. 只實作了 custom；builtin 全數未手寫。
3. 參數（`format` 群組 ＋ `datatable_parameters`）皆從 Gherkin 解析；有 `default_value` 者寫死預設。
4. 共用步驟只註冊一次；無重複註冊。
