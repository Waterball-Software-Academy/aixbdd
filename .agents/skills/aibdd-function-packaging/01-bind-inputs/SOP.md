# SOP

1. 解析 arguments

   1.1 在 `CWD` SEARCH `**/arguments.yml` 檔案，找不到則 STOP 並對使用者輸出「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」。

   1.2 EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
   EOF
   ```

2. 解析本批次 plan package: 對話歷史已指名具體 `NNN-<slug>`（例：reconcile 剛校準完那個 package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續校正 NNN 那個 package」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則設 `$PLAN_PACKAGE_SLUG` 為該 `NNN-<slug>`，否則對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問（不使用 /clarify-loop）要校正哪一個 plan package、設 `$PLAN_PACKAGE_SLUG` 為其 slug，STOP 待使用者回答，候選僅一個甚至為空也必須釐清。
