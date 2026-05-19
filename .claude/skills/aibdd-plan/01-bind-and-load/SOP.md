# SOP

緣由：把 `/aibdd-plan` 後續所有 sub-SOP 賴以決策的真相一次 bind 起來——arguments 鍵齊不齊、Discovery 是否已 accepted、本輪 boundary type 該載入哪份 profile、既有 truth bundle 與 code skeleton 形狀為何。沒在這裡 ASSERT 完，後續 specifier 派遣與 DSL 推導會在假設不成立下 silently 產出對不上 SSOT 的 contracts／sequence／DSL。

1. ASSERT arguments 必備鍵齊全
   - 對上層已 PARSE 之 `${AIBDD_ARGUMENTS_PATH}` 逐項檢查下列鍵存在：`SPECS_ROOT_DIR`、`PLAN_SPEC`、`PLAN_REPORTS_DIR`、`TRUTH_BOUNDARY_ROOT`、`TRUTH_BOUNDARY_PACKAGES_DIR`、`TRUTH_FUNCTION_PACKAGE`、`CONTRACTS_DIR`、`DATA_DIR`、`BOUNDARY_PACKAGE_DSL`、`BOUNDARY_SHARED_DSL`、`TEST_STRATEGY_FILE`、`BOUNDARY_YML`、`ACTIVITIES_DIR`、`FEATURE_SPECS_DIR`；`DSL_KEY_LOCALE` 為選填。
   - 任一缺鍵 → 列出缺鍵，提示使用者回 `/aibdd-kickoff` 或 `/aibdd-discovery` 補綁後再執行本 skill，STOP。本步禁止順手補建 arguments.yml 任何欄位。

2. ASSERT Discovery 真相已 accepted（READ-ONLY）
   - `${PLAN_SPEC}` 存在且含需求敘事全文與 discovery sourcing pointer（章節對齊 `/aibdd-discovery`，例：`Discovery Sourcing Summary`）。
   - `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 存在。
   - `${ACTIVITIES_DIR}` 下至少一份 `.activity` 檔；`${FEATURE_SPECS_DIR}` 下至少一份 rule-only `.feature` 檔。
   - 任一條件失敗 → 提示使用者回 `/aibdd-discovery` 補完，STOP。本步禁止補建或改寫任何 discovery artifact。

3. READ：boundary type profile
   - PARSE `${BOUNDARY_YML}` 之 `type` 欄位為 `$boundary_type`。
   - READ `.claude/skills/aibdd-core/assets/boundaries/${boundary_type}/profile.yml`（相對 `${CWD}`）為本輪 profile；後續 sub-SOP 之 specifier 派遣（`operation_contract_specifier.skill`、`state_specifier.skill`、`component_contract_specifier.skill`、`persistence_handler.{handler_id, state_ref_pattern, coverage_gate}`）皆從此檔取。
   - profile 缺鍵或 `$boundary_type` 不被支援 → 列出缺項，STOP。

4. READ-ONLY 載入既有真相骨架（不寫入）
   - READ `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`、`${CONTRACTS_DIR}/**`、`${DATA_DIR}/**`、`${BOUNDARY_SHARED_DSL}`、`${BOUNDARY_PACKAGE_DSL}`、`${TEST_STRATEGY_FILE}`（缺則視為空骨架）。
   - READ code skeleton index（排除 ignored directories 與非主 worktree）。
   - 只 READ，不得 CREATE 任何空檔或目錄骨架。

5. DERIVE `$PLAN_INPUTS = { plan_spec, discovery_report, activity_truth, feature_truth, boundary_profile, existing_truth_bundle, code_skeleton }`，供後續 sub-SOP 引用；不落地。
