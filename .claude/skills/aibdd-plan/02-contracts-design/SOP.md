# SOP

緣由：不同 boundary 在落實 operations 與 persistent state 時所用的規格格式不同；本 phase 不手寫 OpenAPI／DBML／其他格式，而是依 boundary profile 派遣 `operation_contract_specifier.skill`／`state_specifier.skill`，避免用臆測格式硬寫 `${CONTRACTS_DIR}`／`${DATA_DIR}`。

1. PARSE 從 `01-bind-and-load` 已載入之 profile 取出 `operation_contract_specifier.{skill,format}` 與 `state_specifier.{skill,format}`；產出目錄分別對齊 `${CONTRACTS_DIR}`、`${DATA_DIR}`。

2. DELEGATE `operation_contract_specifier.skill`：載入該 skill 並遵循其自身的禁令與輸入／輸出形狀。以 `${PLAN_SPEC}`、`${FEATURE_SPECS_DIR}/**` 為 SSOT 做系統分析（可加讀 `${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${ACTIVITIES_DIR}/**`）；產出一系列良好模組化、精準切分的 boundary operation contract，依該 skill 認定之 `format` 寫入 `${CONTRACTS_DIR}`。

3. DELEGATE `state_specifier.skill`：同樣以 `${PLAN_SPEC}`、`${FEATURE_SPECS_DIR}/**` 為 SSOT，從資料流動建立資料狀態聚合分析，把資料拆分成 Domain Aggregate／Entity／Value-Object——客觀、不腦補；依該 skill 認定之 `format` 寫入 `${DATA_DIR}`。
