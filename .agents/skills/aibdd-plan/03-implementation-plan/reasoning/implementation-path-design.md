# implementation path design — THINK 步驟輸入與輸出約束

## SSOT 與須載入之真相

設計須考慮 SSOT：`${ACTIVITIES_DIR}/**`、`$PLAN_SCOPE` 所涵蓋之 `${FEATURE_SPECS_DIR}/**`；脈絡不足時補讀 `${PLAN_SPEC}`、`${PLAN_REPORTS_DIR}/function-packaging.md` 之各 function package 章節。另載入既有 operation／state 契約：`${CONTRACTS_DIR}/**`、`${DATA_DIR}/**`，以及 `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`（不存在則視為尚無 dispatch 覆寫）。

## Impact 覆蓋義務

以 `$PLAN_MUTABLE_IMPACT_SPECS`（來自 `${IMPACT_MATRIX_YML}` 之 `read`，且已受 `$PLAN_SCOPE` 過濾）中 contracts／data 相關 spec，與 `${CONTRACTS_DIR}/**` 中對客戶端暴露之 `operationId`（或同義路由入口）做交集盤點；交集內之每一入口視為須覆蓋之 boundary-entry operation。對每一須覆蓋之 operation，預設須各有 happy／alt／err 各至少一條獨立 path（檔粒度仍遵守 `sequence-path-granularity.md`）；若規格上某一類別無合理語意（例如僅唯一成功態），須於 `$IMPLEMENTATION_MODEL.blocked_reasons[]` 記載該 operation、缺漏類別與規格／契約依據，不得默認縮減全集。

## Path 可追溯性

自上述來源 faithful reasoning 萃取實作路徑：每條 path 須能指向 activity flow、atomic rule、契約中可綁定之 operation，或 boundary-map 之 dispatch 依據。

## `$IMPLEMENTATION_MODEL` 輸出形狀

輸出 `$IMPLEMENTATION_MODEL = { paths: [...], collaborators: [...] }`；每條 path 含 `scenario_slug`、`category`（`happy`|`alt`|`err`）、`actor`、`boundary_entry_operation`、`internal_collaborators[]`、`provider_calls[]`、`state_changes[]`、`response_verifier_candidates[]`、`source_refs`。THINK 步驟本身不寫檔。
