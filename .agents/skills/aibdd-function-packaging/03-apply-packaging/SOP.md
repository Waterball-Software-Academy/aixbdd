# SOP

1. 解析 arguments: EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出的 `${PLAN_REPORTS_DIR}` 含 `<<NNN-plan-slug>>` 借位由 `$PLAN_PACKAGE_SLUG` 解析，`${TRUTH_FUNCTION_PACKAGE}` 與 `${FEATURE_SPECS_DIR}` 含 `<<NN-functional-module>>` 借位由各 package 決策的 `NN-<slug>` 解析。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   FEATURE_SPECS_DIR=${FEATURE_SPECS_DIR}
   PLAN_REPORTS_DIR=${PLAN_REPORTS_DIR}
   TRUTH_FUNCTION_PACKAGE=${TRUTH_FUNCTION_PACKAGE}
   EOF
   ```

2. 落地新 package 目錄: 對 `$PACKAGING_DECISIONS` 每個 `flagged_reason` 為 `added` 的決策，依其 `package_path` 的 `NN-<slug>` 解析 `${TRUTH_FUNCTION_PACKAGE}`，CREATE `${TRUTH_FUNCTION_PACKAGE}` 與 `${FEATURE_SPECS_DIR}` 空骨架。

3. 校正 function-packaging.md: 對 `$PACKAGING_DECISIONS` 每個決策參考 `aibdd-function-packaging/assets/templates/function-packaging.template.md` 在 `${PLAN_REPORTS_DIR}/function-packaging.md` 將該 `package_path` 的章節 UPDATE 為其 `flagged_reason` 與 `rationale`，章節不存在則新增；未列入 `$PACKAGING_DECISIONS` 的既有章節保持不動。
