# SOP

1. 解析 arguments

   1.1 在 `CWD` SEARCH `**/arguments.yml` 檔案，找不到則 STOP 並對使用者輸出「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」。

   1.2 EXECUTE command 以 resolver 綁定本 SOP 引用的變數並對使用者輸出 resolver stdout（每行一筆 `KEY=value`），resolver 非 0 退出時 STOP 並對使用者輸出其 stderr。

   ```bash
   python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
   PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
   PROJECT_SPEC_LANGUAGE=${PROJECT_SPEC_LANGUAGE}
   EOF
   ```

2. 解析本輪 plan package

   2.1 對話歷史已指名具體 `NNN-<slug>`（例：稍早曾解析過 plan package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續／重跑 NNN 那包」這類指涉），且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 `CWD`，則 `$PLAN_PACKAGE_SLUG` 設為該 `NNN-<slug>`、`$MODE` 設為 `RECONCILE`。

   2.2 需求敘事明確指名要開新 plan package（例：「開新的 plan」「建立新 package」「這是新需求，開新包」這類明示字句），則 `$MODE` 設為 `NEW`；僅限明示指名新建，從敘事推測「看起來像新功能」不算。

   2.3 其餘情況不得自行判定: 對使用者輸出 `${PLAN_PACKAGES_DIR}/*/` 全部候選 folder 並直接詢問（不使用 /clarify-loop）是要更新哪一個 plan package（`$PLAN_PACKAGE_SLUG` 設為該 slug、`$MODE` 設為 `RECONCILE`）還是開新 plan package（`$MODE` 設為 `NEW`），STOP 待使用者回答，候選僅一個甚至為空也必須釐清。

3. 確認本輪需求: ASSERT 使用者已提供需求描述並綁為 `$RAW_IDEA`，若無則直接向使用者提問本輪需求（不使用 /clarify-loop），STOP 待使用者回答。

4. 建立 plan package folder: `$MODE` 為 `NEW` 時依 `$RAW_IDEA` 與 slug 命名規則 PRINCIPLE 命名 `$PLAN_PACKAGE_SLUG`（`NNN-<slug>`），CREATE `${PLAN_PACKAGES_DIR}/$PLAN_PACKAGE_SLUG/`。
