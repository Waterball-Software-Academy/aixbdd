# SOP

緣由：把 `/aibdd-plan` 後續所有 sub-SOP 賴以決策的真相一次 bind 起來——arguments 鍵齊不齊、Discovery 是否已 accepted、本輪 boundary type 該載入哪份 profile、既有 truth bundle 與 code skeleton 形狀為何。沒在這裡 ASSERT 完，後續 specifier 派遣與 DSL 推導會在假設不成立下 silently 產出對不上 SSOT 的 contracts／sequence／DSL。

0. RESOLVE arguments——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。`${CWD}` 為 shell working directory，不入 manifest。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   BOUNDARY_PACKAGE_DSL=${BOUNDARY_PACKAGE_DSL}
   BOUNDARY_SHARED_DSL=${BOUNDARY_SHARED_DSL}
   BOUNDARY_YML=${BOUNDARY_YML}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   DATA_DIR=${DATA_DIR}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   SPECS_ROOT_DIR=${SPECS_ROOT_DIR}
   TEST_STRATEGY_FILE=${TEST_STRATEGY_FILE}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
   EOF
   ```

1. ASSERT arguments 必備鍵齊全
   - 對上層已 PARSE 之 `${AIBDD_ARGUMENTS_PATH}` 逐項檢查下列鍵存在：`SPECS_ROOT_DIR`、`PLAN_SPEC`、`PLAN_REPORTS_DIR`、`IMPACT_MATRIX_YML`、`TRUTH_BOUNDARY_ROOT`、`TRUTH_BOUNDARY_PACKAGES_DIR`、`TRUTH_FUNCTION_PACKAGE`、`CONTRACTS_DIR`、`DATA_DIR`、`BOUNDARY_PACKAGE_DSL`、`BOUNDARY_SHARED_DSL`、`TEST_STRATEGY_FILE`、`BOUNDARY_YML`、`ACTIVITIES_DIR`、`FEATURE_SPECS_DIR`；`DSL_KEY_LOCALE` 為選填。
   - 任一缺鍵 → 列出缺鍵，提示使用者回 `/aibdd-kickoff` 或 `/aibdd-flows-specify` 補綁後再執行本 skill，STOP。本步禁止順手補建 arguments.yml 任何欄位。

2. ASSERT Discovery 真相已 accepted（READ-ONLY）
   - `${PLAN_SPEC}` 存在且含需求敘事全文與 discovery sourcing pointer（章節對齊 `/aibdd-flows-specify`，例：`Discovery Sourcing Summary`）。
   - `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 存在。
   - `${IMPACT_MATRIX_YML}` 存在。
   - `${FEATURE_SPECS_DIR}` 下至少一份 rule-only `.feature` 檔。
   - `${ACTIVITIES_DIR}` 下若有 `.activity` 則納入 `activity_truth`；若無則視為空集合（Discovery 現行流程可不產 activity，不得因此 STOP）。
   - 任一條件失敗 → 提示使用者回 `/aibdd-flows-specify`（spec.md／feature 骨架）或 `/aibdd-rules-specify`（atomic rules）補完，STOP。本步禁止補建或改寫 discovery markdown／feature／activity artifact。

3. READ：boundary type profile
   - PARSE `${BOUNDARY_YML}` 之 `type` 欄位為 `$boundary_type`。此 `$boundary_type` 欄位在後續 subsop 中會被使用到，需要被嚴格記住。若此欄位不存在則 STOP & 報錯。

4. BIND `$PLAN_SCOPE`（本輪 plan package + function package charters）
   1. READ `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 之 `## Function package charters` 與 `## Packaging decision`。
   2. DERIVE `$plan_package_slug` 自 `${CURRENT_PLAN_PACKAGE}` basename（例：`002-會員登入記錄登入時間`）。
   3. DERIVE `$function_package_slugs[]`：`Packaging decision` 所列本輪涉及的 `packages/NN-<slug>`；每一 slug 須在 `Function package charters` 有對應小卡。
   4. DERIVE `$PLAN_SCOPE = { plan_package_slug, function_package_slugs[], charter_cards[] }`；`charter_cards[]` 每項含 function package path、納入、排除、本輪變更型態、本輪規格增量。
   5. 若 `Packaging decision` 與 `Function package charters` 不一致、或無法解析任一 function package slug，STOP 並回報 discovery sourcing 不完整。

5. TRIGGER impact matrix query，BIND `$PLAN_MUTABLE_IMPACT_ENTRIES`
   1. 讀取本輪 plan mutable workset（含 `conditional_update`）：
      ```bash
      python3 .claude/skills/aibdd-core/scripts/cli/manage_impact_matrix.py \
        --matrix ${IMPACT_MATRIX_YML} query \
        --change-type update \
        --change-type add \
        --change-type conditional_update
      ```
   2. PARSE stdout JSON 之 `entries` 為 `$PLAN_MUTABLE_IMPACT_ENTRIES`。
   3. FILTER：只保留 path 落在 `$PLAN_SCOPE.function_package_slugs[]` 所屬 `${TRUTH_BOUNDARY_PACKAGES_DIR}/<slug>/**`、或 `${CONTRACTS_DIR}/**`、或 `${DATA_DIR}/**` 的 entry；其餘 entry 不納入本輪 plan 推導 scope。
   4. 若 matrix 缺失或 `ok` 為 false，STOP 並回報 impact matrix 不完整。

6. READ-ONLY 載入既有真相骨架（不寫入）
   - READ `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`、`${CONTRACTS_DIR}/**`、`${DATA_DIR}/**`、`${BOUNDARY_SHARED_DSL}`、`${BOUNDARY_PACKAGE_DSL}`、`${TEST_STRATEGY_FILE}`（缺則視為空骨架）。
   - READ code skeleton index（排除 ignored directories 與非主 worktree）。
   - 只 READ，不得 CREATE 任何空檔或目錄骨架。

7. DERIVE `$PLAN_INPUTS = { plan_spec, discovery_report, plan_scope, plan_mutable_impact_entries, activity_truth, feature_truth, boundary_profile, existing_truth_bundle, code_skeleton }`，供後續 sub-SOP 引用；不落地。
