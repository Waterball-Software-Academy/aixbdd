# SOP

1. 解析 arguments: EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出的 `${CURRENT_PLAN_PACKAGE}` 含 `<<NNN-plan-slug>>` 借位，由 `$PLAN_PACKAGE_SLUG` 解析為具體路徑。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   PLAN_SPEC=${PLAN_SPEC}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   TRUTH_BOUNDARY_PACKAGES_DIR=${TRUTH_BOUNDARY_PACKAGES_DIR}
   TRUTH_BOUNDARY_ROOT=${TRUTH_BOUNDARY_ROOT}
   EOF
   ```

2. 載入校正基準

   2.1 若 `${PLAN_REPORTS_DIR}/function-packaging.md` 不存在則參考 `aibdd-function-packaging/assets/templates/function-packaging.template.md` CREATE `${PLAN_REPORTS_DIR}/function-packaging.md` 空骨架，僅含 `# Function Packaging` 標題。

   2.2 READ `${PLAN_REPORTS_DIR}/function-packaging.md` 內容作為 `$CURRENT_PACKAGING`。

   2.3 READ `${PLAN_SPEC}` 需求描述段最新批次作為 `$LATEST_BATCH`。

   2.4 EXECUTE command 以 `read --impact-status pending` 讀出 `${IMPACT_MATRIX_YML}` 全部 pending impact 作為 `$PENDING_IMPACTS`，CLI 用法詳見 `aibdd-core::references/impact-matrix/cli-usage.md`。

3. 識別 impact matrix 標記的既有 package: 設 `$RELATED_PACKAGES` 為 `$PENDING_IMPACTS` 中 spec path 落在 `packages/NN-<slug>/` 下者所對映的既有 `packages/NN-<slug>` 集合；`${CONTRACTS_DIR}`、`${DATA_DIR}` 等 boundary spec 不對映 function package。

4. 判定全新需求的 package 歸屬: 對 `$PENDING_IMPACTS` 中 specs 為空的每個 impact，參考 `aibdd-function-packaging/rules/function-package-granularity.md` 與 `$CURRENT_PACKAGING`，依其 quotes 與 `$LATEST_BATCH` REASONING 其需求該歸入哪個 function package；落入某既有 package 者把該 `packages/NN-<slug>` 加入 `$RELATED_PACKAGES`，無既有 package 可承載者依 slug 命名規則 PRINCIPLE derive 新 `packages/NN-<slug>` 加入 `$ADDED_PACKAGES`。

5. 梳理決策與 rationale

   5.1 對 `$RELATED_PACKAGES` 每個 package，參考 `aibdd-function-packaging/rules/function-package-granularity.md` READ 該 package 於 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 下的既有 specs 了解職責，依 `$LATEST_BATCH` REASONING 其 rationale 以說明本批次對它要增修或新增哪些 spec。

   5.2 對 `$ADDED_PACKAGES` 每個 package，參考 `aibdd-function-packaging/rules/function-package-granularity.md` 依 `$LATEST_BATCH` REASONING 其 rationale 以說明為何必須新開。

   5.3 設 `$PACKAGING_DECISIONS` 為 `$RELATED_PACKAGES` 與 `$ADDED_PACKAGES` 各 package 的決策集合，每筆為 `{ package_path, flagged_reason, rationale }`，對應 `${PLAN_REPORTS_DIR}/function-packaging.md` 內容章節，語意參考 `aibdd-function-packaging/assets/templates/function-packaging.template.md`。
