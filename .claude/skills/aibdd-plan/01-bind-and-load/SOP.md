# 參數設定

- **產出錨點** → 與上層 `/aibdd-plan/SKILL.md` **PRINCIPLE: CWD 為產出錨點**一致；下列 `${…}` 均錨定於 **`CWD`**。
- **arguments 檔** → `${ARGUMENTS_FILE}`（由上層 SKILL.md step 0 已 grep 出之路徑）
- **必備鍵集合** → `SPECS_ROOT_DIR`、`PLAN_SPEC`、`PLAN_REPORTS_DIR`、`TRUTH_BOUNDARY_ROOT`、`TRUTH_BOUNDARY_PACKAGES_DIR`、`TRUTH_FUNCTION_PACKAGE`、`BOUNDARY_PACKAGE_DSL`、`BOUNDARY_SHARED_DSL`、`TEST_STRATEGY_FILE`、`BOUNDARY_YML`、`PRESET_KIND`（後者缺則 default `web-backend`）。**選填**：`DSL_KEY_LOCALE`。
- **plan package** → `${CURRENT_PLAN_PACKAGE}`（解析自 `${PLAN_SPEC}` 之 parent directory）
- **function package** → `${TRUTH_FUNCTION_PACKAGE}`（由 `/aibdd-discovery` 階段綁定）；其下子目錄：`${ACTIVITIES_DIR}`、`${FEATURE_SPECS_DIR}`
- **Discovery 真相** → `${PLAN_SPEC}`、`${PLAN_REPORTS_DIR}/discovery-sourcing.md`、`${ACTIVITIES_DIR}/**.activity`、`${FEATURE_SPECS_DIR}/**.feature`

請注意，所有路徑都是相對於 ${CWD} 所在路徑，請勿新增任何檔案是並非在 ${CWD} 之中，不可妥協。

---

# SOP

1. **PARSE & ASSERT：arguments.yml 包含所有必備鍵**
   - PARSE `${ARGUMENTS_FILE}` 為 yaml；逐項檢查上述「必備鍵集合」是否齊。
   - 若任一缺鍵 → 列出缺鍵清單，提示使用者回到 `/aibdd-kickoff` 或 `/aibdd-discovery` 補綁路徑後再執行本 skill，**STOP**；**禁止**在本步順手補建 arguments.yml 任何欄位。

2. **ASSERT：Discovery 真相已 accepted（READ-ONLY 驗收）**
   - `${PLAN_SPEC}` 必須存在且內含需求敘事全文與 discovery sourcing pointer（章節名稱對齊 `/aibdd-discovery` 規範，例如 `Discovery Sourcing Summary`）。
   - `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 必須存在。
   - `${ACTIVITIES_DIR}` 下**至少有一份** `.activity` 檔；`${FEATURE_SPECS_DIR}` 下**至少有一份** rule-only `.feature` 檔。
   - 任一條件失敗 → 提示使用者回到 `/aibdd-discovery` 補完，**STOP**；本步**禁止**順手補建任何 discovery artifact，亦**禁止**修改既有 activity／feature 內容。

3. **READ：boundary profile**
   - READ `${BOUNDARY_YML}`，PARSE 其 `type` 欄位為 `$boundary_type`。
   - READ `aibdd-core::boundary-type-profiles/${boundary_type}.profile.yml`，存為 `$BOUNDARY_PROFILE`。後續 sub-SOP 之 specifier 派遣依據（`operation_contract_specifier.skill`、`state_specifier.skill`、`component_contract_specifier.skill`、`persistence_handler.{handler_id, state_ref_pattern, coverage_gate}`）皆出自此檔。
   - 若 profile 缺鍵或 `$boundary_type` 不被支援 → 列出缺項，**STOP**。

4. **READ-ONLY：載入既有真相骨架（不做寫入）**
   - READ `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml`（不存在則視為空骨架）。
   - READ `${TRUTH_BOUNDARY_ROOT}/contracts/**`、`${TRUTH_BOUNDARY_ROOT}/data/**`、`${BOUNDARY_SHARED_DSL}`、`${BOUNDARY_PACKAGE_DSL}`、`${TEST_STRATEGY_FILE}`（缺則視為空）。
   - READ code skeleton index（排除 ignored directories 與非主 worktree）。
   - 本步**只 READ**，**不得 CREATE** 任何空檔或目錄骨架。

5. **DERIVE：本輪 plan 之輸入快照** → `$PLAN_INPUTS = { plan_spec, discovery_report, activity_truth, feature_truth, boundary_profile, existing_truth_bundle, code_skeleton }`。供後續 sub-SOP 引用；**不落地**為任何檔案。
