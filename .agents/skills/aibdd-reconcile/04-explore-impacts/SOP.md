# SOP

1. 解析 arguments: EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   DATA_DIR=${DATA_DIR}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   EOF
   ```

2. 載入校準基準

   2.1 EXECUTE command 以 `read`（無 filter）讀出 `${IMPACT_MATRIX_YML}` 全部 impact 作為 `$CURRENT_MATRIX` 並對使用者輸出，CLI 用法詳見 `aibdd-core::references/impact-matrix/cli-usage.md`。

   2.2 READ `${PLAN_SPEC}` 內最新批次的需求敘事作為 `$RAW_IDEA`。

   2.3 確立 finding 構成原則作為 `$FINDING_RULE`：一個 impact 把 `$RAW_IDEA` 的一或數句話交給某 owner 職責下 formulate 成 spec；本步逐句對照既有 spec 判斷該句是改動既有 spec、還是須由 owner 新建 spec。每個 finding 為 `{ owner, quotes, spec_path }`：`owner` 為所屬階段；`quotes` 為交給該 owner 的 `$RAW_IDEA` 原句，至少一句；`spec_path` 僅在影響既有 spec 時填其相對 `${TRUTH_BOUNDARY_ROOT}` 的路徑，否則留空，確定或有懷疑被牽動者皆視為受影響。

3. `aibdd-flows-specify` 階段探索: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${FEATURE_SPECS_DIR}` 下 `.feature` 骨架與 `${ACTIVITIES_DIR}` 下 `.activity` 與 `${PLAN_REPORTS_DIR}/function-packaging.md` REASONING 本階段被牽動的 finding，包含但不限於 UAT flow、function package 範圍劃分、feature 範圍劃分，加入 `$STAGE_FINDINGS`。

4. `aibdd-rules-specify` 階段探索: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${FEATURE_SPECS_DIR}` 下既有 `.feature` 的 atomic rules REASONING 本階段被牽動的 finding，包含但不限於 feature 範圍不變下各條 atomic rule 的對錯與增刪，加入 `$STAGE_FINDINGS`。

5. `aibdd-spec-by-example` 階段探索: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${FEATURE_SPECS_DIR}` 下既有 `.feature` 的 Scenario／Examples REASONING 本階段被牽動的 finding，包含但不限於 example 具體值、邊界值、step 寫法，加入 `$STAGE_FINDINGS`。

6. `aibdd-api-plan` 階段探索: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${CONTRACTS_DIR}` 下契約檔 REASONING 本階段被牽動的 finding，包含但不限於 operation contract、對外 operation／路由／欄位，加入 `$STAGE_FINDINGS`。

7. `aibdd-data-plan` 階段探索: 依據 `$RAW_IDEA` 與 `$FINDING_RULE`、參考 `${DATA_DIR}` 下 schema 檔 REASONING 本階段被牽動的 finding，包含但不限於 persistent data schema、entity／table／欄位，加入 `$STAGE_FINDINGS`。

8. 彙整待校準清單

   8.1 自 `$STAGE_FINDINGS` 取有 `spec_path` 者 REASONING `$STALE_SPECS`：不論該 spec 在 `$CURRENT_MATRIX` 現為 `consistent` 或 `inconsistent`，被 finding 命中即表示有新 quote 要加入該 impact。每筆含 `{ impact_id, spec_path, owner, quote, rationale }`：`impact_id`／`owner` 取自該 spec 所屬 impact；`quote` 為該 impact 既有 quotes 加上該 finding 之 quotes；`rationale` 整合該 impact 更新後的全部 quote，以一句話說明此 impact 在該 owner 下為何要產生其 spec。

   8.2 自 `$STAGE_FINDINGS` 取無 `spec_path` 者（formulate 對象為待建 spec）REASONING `$NEW_IMPACTS`，每筆含 `{ owner, quote, rationale }`：`owner` 取自該 finding；`quote` 取自該 finding 之 quotes（≥1）；`rationale` 整合其 quote 以一句話說明此 impact 在該 owner 下為何要產生 spec。
