# SOP

緣由：判斷這次的 trigger 描述最上游影響到哪一個 planner，算出從該 planner 開始往下游的 cascade chain，並據此開新或併入 reconcile session。

1. DERIVE 本輪要拿去分類的 trigger 文字：
   1. 若 session 模式為 `start_new` → 直接用頂層綁定的 trigger 描述。
   2. 若 session 模式為 `merge_existing` → READ active session JSON 的 `triggers` 歷史，DRAFT 一段「歷史 trigger ＋ 這次新 trigger」合併後的描述，作為分類依據。

2. CLASSIFY 最上游被影響的 planner，從下列四者擇一。四者固定上下游順序為 flows-specify → rules-specify → plan → spec-by-example；挑「被這次 trigger 碰到的 planner 之中最上游的那一個」，因為重跑上游會帶動下游。本步只產出判斷，不寫檔。
   1. `aibdd-flows-specify` ── 負責：要做哪些 feature、feature 檔的範圍與切分、sourcing／packaging 與 impact matrix。若 trigger 牽動「要新增或移除 feature、改變 feature 範圍與切分」就選它。
   2. `aibdd-rules-specify` ── 負責：每個 feature 上每條 atomic rule 的萃取與修正。若 trigger 牽動「atomic rule 本身對不對、要加／改／刪某條規則」且未改變 feature 範圍，就選它。
   3. `aibdd-plan` ── 負責：架構與 boundary、API／entity／contract 設計、implementation plan、DSL 合成。若 trigger 牽動「contract 缺欄位、架構或邊界要調整、實作規劃要改」且未觸及上游 feature／rule，就選它。
   4. `aibdd-spec-by-example-analyze` ── 負責：Gherkin scenario 的 example 形態、step handler 對應、DSL arrangement、具體參數值。若 trigger 只牽動「example 的具體值、邊界值、step 寫法」就選它。

3. BRANCH 分類結果落點：
   1. 若分類結果是上述三者之一 → 以它作為最上游 planner，前往步驟 4。
   2. 若語意模糊到無法歸類四者之一 → 保守改選最上游的 `aibdd-flows-specify`，並 EMIT 告知用戶：「reconcile 分類模糊，依保守規則改由最上游 /aibdd-flows-specify 起跑。」再前往步驟 4。

4. TRIGGER cascade chain 推導 script：

   ```bash
   python3 .claude/skills/aibdd-reconcile/scripts/python/derive_cascade_chain.py "<最上游 planner>"
   ```

   1. OUTCOME：stdout JSON 的 `stdout_csv` 是從最上游 planner 到 spec-by-example 的逗號分隔下游鏈。
   2. 若 script 非 0 退出，STOP 並把 stderr 透傳給用戶。

5. TRIGGER session 建立／併入 script（依 session 模式擇一執行）。本步授權落地 active session JSON。
   1. 若 session 模式為 `start_new`：

      ```bash
      python3 .claude/skills/aibdd-reconcile/scripts/python/manage_reconcile_session.py start \
        "<active_session_path>" "<record_path>" "<target_plan_package>" \
        "<本輪 trigger 描述>" "<最上游 planner>" "<cascade_chain CSV>"
      ```

   2. 若 session 模式為 `merge_existing`：

      ```bash
      python3 .claude/skills/aibdd-reconcile/scripts/python/manage_reconcile_session.py merge \
        "<active_session_path>" "<這次新 trigger 描述>" "<最上游 planner>" "<cascade_chain CSV>"
      ```

   3. OUTCOME：stdout JSON 含 `stdout_session_id`、`stdout_archive_path`、`stdout_replay_from`；active session JSON 已落地，其 `mode` 欄位記錄本輪是 `start_new` 還是 `merge_existing`，`replay_from` 記錄本輪該從哪個 planner 重跑。
   4. 若 script 非 0 退出，STOP 並把 stderr 透傳給用戶。
