# SOP

緣由：把 `/aibdd-plan` 後續所有 sub-SOP 賴以決策的真相一次 bind 起來——arguments 鍵齊不齊、Discovery 是否已 accepted、本輪 boundary type 該載入哪份 profile、既有 truth bundle 與 code skeleton 形狀為何。沒在這裡 ASSERT 完，後續 specifier 派遣與 DSL 推導會在假設不成立下 silently 產出對不上 SSOT 的 contracts／sequence／DSL。

0. RESOLVE arguments——將本 SOP 引用的 `${VAR}` 透過 sibling resolver 綁定，並把 resolver stdout（每行一筆 `KEY=value`）原樣 EMIT 給用戶。Resolver 非 0 退出時，停止本 SOP 並把 stderr 透傳給用戶。`${CWD}` 為 shell working directory，不入 manifest。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/python/resolve_args.py <<'EOF'
   ACTIVITIES_DIR=${ACTIVITIES_DIR}
   AIBDD_ARGUMENTS_PATH=${AIBDD_ARGUMENTS_PATH}
   BOUNDARY_PACKAGE_DSL=${BOUNDARY_PACKAGE_DSL}
   BOUNDARY_SHARED_DSL=${BOUNDARY_SHARED_DSL}
   BOUNDARY_YML=${BOUNDARY_YML}
   CONTRACTS_DIR=${CONTRACTS_DIR}
   DATA_DIR=${DATA_DIR}
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   TEST_STRATEGY_FILE=${TEST_STRATEGY_FILE}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

1. ASSERT arguments 必備鍵齊全
   - 對上層已 PARSE 之 `${AIBDD_ARGUMENTS_PATH}` 逐項檢查下列鍵存在：`SPECS_ROOT_DIR`、`PLAN_SPEC`、`PLAN_REPORTS_DIR`、`TRUTH_BOUNDARY_ROOT`、`TRUTH_BOUNDARY_PACKAGES_DIR`、`TRUTH_FUNCTION_PACKAGE`、`CONTRACTS_DIR`、`DATA_DIR`、`BOUNDARY_PACKAGE_DSL`、`BOUNDARY_SHARED_DSL`、`TEST_STRATEGY_FILE`、`BOUNDARY_YML`、`ACTIVITIES_DIR`、`FEATURE_SPECS_DIR`；`DSL_KEY_LOCALE` 為選填。
   - 任一缺鍵 → 列出缺鍵，提示使用者回 `/aibdd-kickoff` 或 `/aibdd-discovery` 補綁後再執行本 skill，STOP。本步禁止順手補建 arguments.yml 任何欄位。

2. ASSERT Discovery 真相已 accepted（READ-ONLY）
   - `${PLAN_SPEC}` 存在且含需求敘事全文與 discovery sourcing pointer（章節對齊 `/aibdd-discovery`，例：`Discovery Sourcing Summary`）。
   - `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 存在。
   - `${FEATURE_SPECS_DIR}` 下至少一份 rule-only `.feature` 檔。
   - `${ACTIVITIES_DIR}` 下若有 `.activity` 則納入 `activity_truth`；若無則視為空集合（Discovery 現行流程可不產 activity，不得因此 STOP）。
   - 任一條件失敗 → 提示使用者回 `/aibdd-discovery` 補完，STOP。本步禁止補建或改寫任何 discovery artifact。

3. READ：boundary type profile
   - PARSE `${BOUNDARY_YML}` 之 `type` 欄位為 `$boundary_type`。此 `$boundary_type` 欄位在後續 subsop 中會被使用到，需要被嚴格記住。若此欄位不存在則 STOP & 報錯。

4. READ-ONLY 載入既有真相骨架（不寫入）
   - READ `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`、`${CONTRACTS_DIR}/**`、`${DATA_DIR}/**`、`${BOUNDARY_SHARED_DSL}`、`${BOUNDARY_PACKAGE_DSL}`、`${TEST_STRATEGY_FILE}`（缺則視為空骨架）。
   - READ code skeleton index（排除 ignored directories 與非主 worktree）。
   - 只 READ，不得 CREATE 任何空檔或目錄骨架。

5. DERIVE `$PLAN_INPUTS = { plan_spec, discovery_report, activity_truth, feature_truth, boundary_profile, existing_truth_bundle, code_skeleton }`，供後續 sub-SOP 引用；不落地。
