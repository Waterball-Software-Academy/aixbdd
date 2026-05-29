# SOP

本 sub-SOP 收集 kickoff 配置選項（Q1 stack / Q2 spec-language / Q3 service-name / Q4 codebase-layout），interactive 路徑下將答案落檔於 `${PLAN_PATH}` 供 `02-execute-layout/SOP.md` 消費。

題庫 SSOT = `${PLAN_PATH}`（從 [`../assets/kickoff-plan.template.md`](../assets/kickoff-plan.template.md) 渲染而來）；其餘規則見 [`../assets/kickoff-plan-contract.md`](../assets/kickoff-plan-contract.md)。

1. IF `${NON_INTERACTIVE}` == true：
   1.1 DERIVE `$decisions` ← defaults `{stack: python_e2e, project_spec_language: zh-hant, tlb_id: backend, boundary_codebase_subdir: ""}`（headless 要 java_e2e / nextjs_playwright 須由 caller payload 帶 `stack:` 覆寫）。
   1.2 END Sub-SOP。`$decisions` 由 `02-execute-layout/` 直接消費，**不寫** `${PLAN_PATH}`。

2. DERIVE `$action`：
   - IF path_exists(`${PLAN_PATH}`) == false → `$action = write_fresh`，續執行 step 4。
   - ELSE → DELEGATE `/clarify-loop`，`delegated_intake`：
     - `profile`   = `aibdd-kickoff`
     - `phase`     = `resume`
     - `raw_items` ← 一題：
       - `id`: `q-resume-mode`
       - `kind`: `CON`
       - `prompt`: 要從現有的 KICKOFF_PLAN.md 繼續，還是重做？
       - `context`: `${PLAN_PATH}` 已存在，可能來自上次未完成的 kickoff。
       - `options`:
         - `resume` — 繼續上次的進度（讀取現有答案，只補沒答完的題目）
         - `restart` — 重新開始（覆寫 plan、丟棄現有答案）
         - `cancel` — 取消這次 kickoff（不動現有檔案，整個 skill stop）
       - `recommendation`: `resume`
     - `anchors`: `plan_path: ${PLAN_PATH}`
     IF 回傳 `completed` → CLASSIFY 為 `resume | restart | cancel`，對應 `$action ∈ {keep_existing | write_fresh | stop}`。
     IF 回傳 `unsupported_tooling` → 唯轉述 `/clarify-loop` 結果，禁止在 chat 重造題組。

3. IF `$action == stop` → STOP。

4. IF `$action == write_fresh`：
   4.1 READ [`../assets/kickoff-plan.template.md`](../assets/kickoff-plan.template.md) → `$template`。
   4.2 WRITE `${PLAN_PATH}` ← RENDER `$template` 帶入 `STATUS=collecting_answers`、Context block 路徑變數、Q1–Q4 答案欄位空白（`{{Q*_RAW_ANSWER}}` / `{{Q*_STATUS}}` 等保留為 unanswered placeholder）。題目本文（prompt / context / options / recommendation）**逐字**取自 template，禁止改寫。**ASSERT** plan 含 q1–q4 四題 question record。**本步僅允許 WRITE `${PLAN_PATH}`**。

5. READ `${PLAN_PATH}` → `$plan_doc`。

6. PARSE 所有 unanswered question records 為 `$question_batch`（stable id order，`1 <= count <= 4`），每筆含 `id` / `prompt` / `context` / `options` / `recommendation`，**直接逐字**取自 `$plan_doc`。

7. DELEGATE `/clarify-loop`，`delegated_intake`：
   - `profile`   = `aibdd-kickoff`
   - `phase`     = `collect`
   - `raw_items` ← `$question_batch`（回答格式依 [`../assets/kickoff-plan-contract.md`](../assets/kickoff-plan-contract.md) §Batch Reply Format）
   - `anchors`: `plan_path: ${PLAN_PATH}`
   IF 回傳 `completed` → PARSE 為 per-question `$decisions` map（依 [`../assets/kickoff-plan-contract.md`](../assets/kickoff-plan-contract.md) §Resolved Decisions YAML 形態）。
   IF 回傳 `unsupported_tooling` → 唯轉述 `/clarify-loop` 結果，禁止在 chat 重造題組。

8. ASSERT `$decisions` 對 `$question_batch` 每題都有 resolved answer。若有缺漏 → UPDATE `${PLAN_PATH}` 在缺漏題加註 `unresolved`，向 user 告知「`${PLAN_PATH}` 已標記 unresolved，請人工檢查或重答整批 kickoff 問題」並 STOP。

9. UPDATE `${PLAN_PATH}`：對 `$question_batch` 每題以 answer writeback block 替換 unanswered（依 [`../assets/kickoff-plan-contract.md`](../assets/kickoff-plan-contract.md) §Question Record Fields），status 改為 `answered`。**ASSERT** plan 中所有 question status == `answered`（File First invariant）。**本步僅允許 UPDATE `${PLAN_PATH}`**。

10. END Sub-SOP。`$decisions` 供 `02-execute-layout/` 消費。
