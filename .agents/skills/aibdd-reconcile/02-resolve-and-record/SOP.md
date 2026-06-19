# SOP

1. 解析 arguments: EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr；resolver 輸出的 `${CURRENT_PLAN_PACKAGE}` 含 `<<NNN-plan-slug>>` 借位，由 `$PLAN_PACKAGE_SLUG` 解析為具體路徑。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   CURRENT_PLAN_PACKAGE=${CURRENT_PLAN_PACKAGE}
   IMPACT_MATRIX_YML=${IMPACT_MATRIX_YML}
   PLAN_SPEC=${PLAN_SPEC}
   EOF
   ```

2. 補齊 spec.md 與 impact matrix 骨架

   2.1 若 `${PLAN_SPEC}` 不存在，參考 `aibdd-reconcile/assets/templates/spec.template.md` CREATE `${PLAN_SPEC}` 空骨架，僅含需求描述章節標題。

   2.2 若 `${IMPACT_MATRIX_YML}` 不存在，EXECUTE command 跑一次 impact matrix `init` 建空檔，CLI 用法詳見 `aibdd-core/references/impact-matrix/cli-usage.md`。

3. 追加本輪需求: 參考 `aibdd-reconcile/assets/templates/spec.template.md` 的需求批次填寫規則，在 `${PLAN_SPEC}` WRITE `$RAW_IDEA`。
