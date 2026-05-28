# SOP

緣由：不同 boundary 在落實 operations 與 persistent state 時所用的規格格式不同；本 phase 不手寫 OpenAPI／DBML／其他格式，而是依 boundary profile 派遣 `operation_contract_specifier.skill`／`state_specifier.skill`，避免用臆測格式硬寫 `${CONTRACTS_DIR}`／`${DATA_DIR}`。

0. **RESOLVE arguments**——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   DATA_DIR=${DATA_DIR}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

1. PARSE 從 `01-bind-and-load` 已載入之 profile 取出 `operation_contract_specifier.{skill,format}` 與 `state_specifier.{skill,format}`；產出目錄分別對齊 `${CONTRACTS_DIR}`、`${DATA_DIR}`。沿用 `$PLAN_SCOPE` 與 `$PLAN_MUTABLE_IMPACT_ENTRIES` 約束本 phase 推導範圍。

2. DERIVE operation contract `slice_list`：以 `${PLAN_SPEC}`、`$PLAN_SCOPE` 所涵蓋之 `${FEATURE_SPECS_DIR}/**` 為 SSOT 做系統分析（可加讀 `${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${ACTIVITIES_DIR}/**`），切出良好模組化、精準切分的 operation contract slice。每個 slice 必須含 `target_path` + `scope`，其中 `target_path` 為**相對於 `${CONTRACTS_DIR}` 的檔案路徑**（例：`api.yml`、`api/<resource>.yml`、`<boundary-id>/api.yml`，依切檔策略決定）。`target_path` **不得**含 `<<NN-functional-module>>` 借位子層 — `${CONTRACTS_DIR}` 在 SSOT 已是 flat directory（見 `aibdd-core::spec-package-paths.md`）。

3. DELEGATE `/${operation_contract_specifier.skill}`：請直接透過 Load SKILL 執行該 skill，並遵循其自身的禁令與輸入／輸出形狀，DELEGATE payload 內帶入步驟 2 之 `slice_list`；specifier 依其認定之 `format` 寫入 `${CONTRACTS_DIR} ⊕ slice.target_path`。

4. DERIVE state `target_path` 集合：同樣以 `${PLAN_SPEC}`、`$PLAN_SCOPE` 所涵蓋之 `${FEATURE_SPECS_DIR}/**` 為 SSOT，從資料流動建立資料狀態聚合分析，把資料拆分成 Domain Aggregate／Entity／Value-Object——客觀、不腦補；依切檔策略決定每份 state schema 的 `target_path`（相對 `${DATA_DIR}` 的檔案路徑）。`target_path` **不得**含 `<<NN-functional-module>>` 借位子層。

5. DELEGATE `/${state_specifier.skill}`：請直接透過 Load SKILL 執行該 skill，DELEGATE payload 內帶入步驟 4 之 `target_path`；specifier 依其認定之 `format` 寫入 `${DATA_DIR} ⊕ target_path`。

6. TRIGGER impact matrix writeback（本 phase 派生出的 contracts／data target paths）: EXECUTE `steps/impact-matrix-writeback.md`。

7. （此步驟必須嚴格遵守，至少要有一條澄清項目）`$NEED_TO_CLARIFY`, `$NEED_TO_FIX` = DO FAITHFUL REASONING 針對本 phase 已導出之 operation contracts、state schemas 與 impact writeback 整體結果，依照 `steps/derive-findings.md` 中的分析切角去進行深度分析，並找到所有需要修正、澄清的地方。

8. 若 `$NEED_TO_FIX` 非空：依 `$NEED_TO_FIX` 修正本 phase 之 operation contract slices、state target paths、specifier delegation input 與 impact matrix writeback，必要時重跑步驟 `2` 到 `6`。

9. 若 `$NEED_TO_CLARIFY` 非空：DELEGATE `/clarify-loop` 一次進行提問。
