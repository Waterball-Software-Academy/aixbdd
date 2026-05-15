# SOP

1. **PARSE & ASSERT：arguments.yml 必備鍵齊**
   - PARSE `${ARGUMENTS_FILE}`（上層 SKILL.md step 0 已 grep 出之路徑）為 yaml。
   - 必備鍵：`SPECS_ROOT_DIR`、`PLAN_SPEC`、`PLAN_REPORTS_DIR`、`TRUTH_BOUNDARY_ROOT`、`TRUTH_FUNCTION_PACKAGE`、`FEATURE_SPECS_DIR`、`BOUNDARY_PACKAGE_DSL`、`BOUNDARY_SHARED_DSL`、`TEST_STRATEGY_FILE`、`BOUNDARY_YML`、`BDD_CONSTITUTION_PATH`。
   - 任一缺鍵 → 列出缺鍵，提示回 `/aibdd-kickoff` 或 `/aibdd-plan` 補綁，**STOP**；本步**禁止**順手補 arguments.yml 任何欄位。

2. **ASSERT：plan 真相就緒（READ-ONLY 驗收）** — 規則見 `rules/upstream-truth-readonly.md`。
   - `${BOUNDARY_PACKAGE_DSL}` 存在且 `entries[]` 非空；`${BOUNDARY_SHARED_DSL}` 存在則 READ，否則視為空。
   - `${FEATURE_SPECS_DIR}` 下至少一份 `.feature`；每份檔 `Rule:` block 非空。
   - `${TEST_STRATEGY_FILE}` 存在。
   - 任一失敗 → 列出原因，**STOP**；**禁止**改寫任何 plan owner 之檔。

3. **ASSERT：constitution §5 filename axes 已綁**
   - READ `${BDD_CONSTITUTION_PATH}`；ASSERT §5 之 `convention` 與 `title_language` 皆非 `TODO`／`unknown`。

4. **READ：boundary profile**
   - PARSE `${BOUNDARY_YML}` → 鎖定本輪 boundary 條目（與 `${TRUTH_BOUNDARY_ROOT}`／plan 對齊之 `id`／`role`）；READ 其 `type` 為 `$boundary_type`。
   - READ `.claude/skills/aibdd-core/assets/boundaries/${boundary_type}/profile.yml` 為 `$boundary_profile`（相對 **`CWD`**）。
   - 若檔案不存在或 `$boundary_type` 未支援 → 列出路徑，**STOP**，提示回 `/aibdd-kickoff` 或 `/aibdd-plan`。
   - DERIVE `$persistence_handler = $boundary_profile.persistence_handler.handler_id`、`$state_ref_pattern = $boundary_profile.persistence_handler.state_ref_pattern`、`$coverage_gate = $boundary_profile.persistence_handler.coverage_gate ∈ {not-null-columns, deferred-v1, none}`（集合以 profile 實際宣告為準；缺鍵視同 profile 不合格）。
   - persistence 三件任一無法自 profile 取得 → **STOP**，提示回 `/aibdd-kickoff` 或 `/aibdd-plan` 補 profile。

5. **READ：plan 真相全集** — 內容形狀見 `rules/input-truth-binding.md`。
   - READ `${BOUNDARY_PACKAGE_DSL}` 與 `${BOUNDARY_SHARED_DSL}`（若存在），MERGE 為 `$dsl_entries`。
   - READ `${CONTRACTS_DIR}/**/*.{yml,yaml}`（預設 `${TRUTH_BOUNDARY_ROOT}/contracts`）為 OpenAPI operation index `$contract_index`；不存在則對 web-service boundary 標 CiC(GAP)。
   - READ `${DATA_DIR}/**/*.dbml`（預設 `${TRUTH_BOUNDARY_ROOT}/data`）為 DBML table／field index `$data_index`；不存在則視為空。
   - READ `${TEST_STRATEGY_FILE}` 為 `$test_strategy`。

6. **DERIVE：indexed-truth bundle（不落地）**
   - `$indexed_truth = { dsl_entries, dsl_l1_pattern_index, contract_index, data_index, test_strategy, boundary_profile: $boundary_profile, persistence: { handler: $persistence_handler, state_ref_pattern: $state_ref_pattern, coverage_gate: $coverage_gate }, feature_files: [{path, relative_path, rules[]}] }`。
   - ASSERT 每個 DSL entry 含 `L1`、`L4.preset.name`、`L4.surface_kind`、`L4.source_refs`；缺則列 entry id 為 CiC(GAP)。
   - `$indexed_truth` 為下游 02–05 之輸入，本步不寫檔。
