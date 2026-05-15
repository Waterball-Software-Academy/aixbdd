# SOP

緣由：不同 boundary 在落實 operations 與 persistent state 時採用的規格撰寫格式可能不同，因此委派前必先讀取 profile：`operation_contract_specifier` 與 `state_specifier` 各指向哪一支 skill；不可以跳過 profile、用臆測格式硬寫 `${CONTRACTS_DIR}`／`${DATA_DIR}`。

1. PARSE `${BOUNDARY_YML}`（鎖定本輪 `boundary`）；READ profile（禁止憑空手改）；取出 `operation_contract_specifier`、`state_specifier` 及其 `skill`／`format`，並將產出對齊 `${CONTRACTS_DIR}`、`${DATA_DIR}`。

2. DELEGATE profile 指派之 `operation_contract_specifier.skill`：委派時載入該 `skill` 所指之 SKILL 並遵循其禁令與輸入／輸出形狀。以 `${PLAN_SPEC}` 與 `${FEATURE_SPECS_DIR}/**` 作為 SSOT 來做系統分析；並且你需要產出一系列良好模組化並且精準的此 boundary 的 operation contract。可多加分析 `${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${ACTIVITIES_DIR}/**`。依 skill 認定之 `format` 寫入 `${CONTRACTS_DIR}`。

3. DELEGATE profile 指派之 `state_specifier.skill`：同上載入規約與可追溯約束，以 `${PLAN_SPEC}`、`${FEATURE_SPECS_DIR}/**` 作為 SSOT 來做系統分析，並且你需要產出一系列良好模組化並且精準的此 boundary 的 state contract。分析著重點為客觀且完全去除腦補——從資料流動中建立資料狀態聚合分析，把資料拆分成 Domain Aggregate/Entity/Value-Object，並依 skill 認定之 `format` 寫入 `${DATA_DIR}`。
