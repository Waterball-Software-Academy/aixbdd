# SOP

0. 解析 arguments

  0.0 在 CWD 底下 grep 搜尋 **/arguments.yml 檔案，如不存在檔案請直接 STOP，向使用者回報：「我在 CWD 底下找不到 **/arguments.yml 檔案，你是否已經執行過 /aibdd-kickoff 了？」

  0.1 將本 SOP 引用的變數透過 resolver 綁定，並把 resolver stdout（每行一筆 KEY=value）原樣顯示給用戶。Resolver 非 0 退出時，STOP 並把 stderr 透傳給用戶。

    ```bash
    python3 .claude/skills/aibdd-core/scripts/cli/resolve_args.py <<'EOF'
    PLAN_PACKAGES_DIR=${PLAN_PACKAGES_DIR}
    EOF
    ```

1. 上下文解析

  1.1 DECIDE plan package 指向。`arguments.yml` 的 CURRENT_PLAN_PACKAGE 永遠保持 <<NNN-plan-slug>> 借位形態，判據不在 yaml，而在對話上下文：
  - 對話歷史已指名具體 NNN-<slug>（例：稍早本 skill 曾經執行並解析過 plan package、使用者點名 `${PLAN_PACKAGES_DIR}/NNN-<slug>`、或「繼續／重跑 NNN 那包」這類指涉），並且 ASSERT `${PLAN_PACKAGES_DIR}/NNN-<slug>/` 存在於 CWD；則 `$PLAN_PACKAGE_SLUG` 設定為該指名 NNN-<slug>、`$MODE` 設定為 RECONCILE；路徑不存在則改走下方釐清。
  - 需求敘事明確指名要建立新的 plan package（例：「開新的 plan」「建立新 package」「這是一個新需求，開新包」這類明示字句）則 `$MODE` 設定為 NEW，本步不建包，交由後續 phase 建立。僅限明示指名新建，從敘事內容推測「看起來像新功能」不算。
  - 其餘情況不得自行判定。列出 `${PLAN_PACKAGES_DIR}/*/` 全部候選向使用者釐清，直接詢問——是變更哪個既有包（`$PLAN_PACKAGE_SLUG` 設定為該 slug、`$MODE` 設定為 RECONCILE），還是開新包（`$MODE` 設定為 NEW）；取得回覆前 STOP，候選僅一個、甚至為空，也必須釐清。

  1.2 ASSERT 使用者已提供需求描述；若無，則直接向使用者提問本輪需求（不使用 /clarify-loop），取得前 STOP。
