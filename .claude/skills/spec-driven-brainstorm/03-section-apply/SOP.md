# SOP

緣由：依 phase 2 分類結果，把 user 本輪訊息推導出的 fact 以「絕對設計」形式寫入 `${SPEC_FILE}` 的對應 issue × subsection。每一條寫入都受 `rules/as-is-style.md` 約束；subsection 內部結構受 `rules/subsection-schema.md` 約束；推進順序受 `rules/progressive-disclosure-order.md` 約束。本 phase 不做 cross-subsection consistency 掃描（該責任屬 phase 4）。

0. RESOLVE arguments —— 沿用頂層綁定；READ `$bind_summary`、`$classify_summary`。本步不寫檔。

1. READ `rules/subsection-schema.md`（首次迭代後可快取；以快取為由跳過重讀時須 ASSERT 規則檔未變更）。

2. READ `rules/as-is-style.md`。

3. READ `rules/progressive-disclosure-order.md`。

4. BRANCH on `$classify_summary.action`：

   4.1 `create-issue` →
      - READ `templates/issue-block.template.md` 為新 issue 骨架。
      - DERIVE `$new_issue_title` 自 `$user_msg`（萃取最簡潔的議題名；不得含問號、不得帶 hedging）。
      - DERIVE `$new_issue_block` = 將 template 之 `<N>` 替換為 `$classify_summary.target_issue`、`<title>` 替換為 `$new_issue_title`、預填 `## Definition` 空 heading。
      - UPDATE `${SPEC_FILE}`：appendable 至檔尾（在最後一個 H1 之後）插入 `$new_issue_block`。本步僅允許 UPDATE `${SPEC_FILE}`；禁止 CREATE 其他檔案、禁止改動既有 issue。

   4.2 `append-fact` →
      - DERIVE `$new_fact_paragraph` 自 `$user_msg`：依 `rules/as-is-style.md` 將 user 表達改寫為肯定式 fact（去 hedging、去 Q&A 形態、去 transitional narrative）；依 `rules/subsection-schema.md` 將 paragraph 對齊目標 subsection 結構（譬如 problem-space 編為 **Pn** 區塊、brainstorming 編為 **Sn** 區塊）。
      - UPDATE `${SPEC_FILE}`：在 `$classify_summary.target_issue` × `$classify_summary.target_subsection` heading 下方追加 `$new_fact_paragraph`。本步僅允許 UPDATE `${SPEC_FILE}` 於該 subsection；禁止跨 subsection 修改、禁止改動其他 issue。

   4.3 `advance-subsection` →
      - DERIVE `$next_subsection_name` = progressive disclosure 順序之下一格（依 `rules/progressive-disclosure-order.md`）；若已到 `implementation-package-structure` → no-op，記 `$advance_blocked_reason = "terminal subsection reached"`。
      - UPDATE `${SPEC_FILE}`：在 `$classify_summary.target_issue` 區塊內插入 `## <Next Subsection Heading>` 空 H2（body 留空）；若 `$intent = confirm-section-done` 且 next 為 `brainstorming` → 同時預填一段 placeholder 描述（譬如 "尚待 AI 提案候選方案，將於下一輪 emit"）以利 phase 5 elicit。本步僅允許 UPDATE 該 issue 之新增 H2 與其 placeholder body；禁止改動既有 subsection。

   4.4 `commit-variant` →
      - PARSE 當前 `${SPEC_FILE}` 中 `$classify_summary.target_issue` 之 `## Brainstorming` subsection 內 user 選中的 Sn 區塊文字為 `$chosen_variant_text`。
      - DERIVE `$solution_block` 自 `$chosen_variant_text`：依 `rules/as-is-style.md` 改寫為「committed 絕對描述」（去除 pros / cons 對比、去除「為什麼選 X 而不是 Y」narrative、去除排序）；依 `rules/subsection-schema.md` 編為 `## Solution` 結構（Policy 1..N 或 Rule 1..N）。
      - UPDATE `${SPEC_FILE}`：在 `$classify_summary.target_issue` 區塊內插入 `## Solution` heading + `$solution_block`。本步僅允許 UPDATE 該 issue 之新增 `## Solution`；**不在本 phase 刪除 `## Brainstorming`**（該動作屬 phase 4 archive-trigger 職責）。

   4.5 `revise` →
      - PARSE `$user_msg` 識別被修正之目標範圍：subsection 整段、某條 Pn / Sn / Policy n、或某段文字。記為 `$revise_target`。
      - DERIVE `$revised_text`：依 `rules/as-is-style.md` 將 user 修正意圖改寫為肯定式 fact，**整段替換** `$revise_target`（不留新舊並存）。
      - UPDATE `${SPEC_FILE}`：以 `$revised_text` 替換 `$revise_target` 原內容。本步僅允許 UPDATE `$revise_target` 範圍；禁止 inline 留下 strikethrough / 「原本是 X，現在改為 Y」之類 transitional narrative。

   4.6 `defer` → no-op。本 phase 不寫檔；phase 5 emit 後續 prompt 推進對話。

   4.7 `ambiguous` → no-op。本 phase 不寫檔；phase 5 emit 一次性 batch 提問。

5. ASSERT：本輪寫入之內容符合 `rules/as-is-style.md` 之 strong-form rules（無 hedging、無 transitional narrative、無 Q&A 形態、無 ticket / PR / commit ID 引用）。違反 → 列出違規位置與規則名，**STOP**，並回退本輪 UPDATE（git-style 還原或重寫整段）。

6. DERIVE `$apply_summary = { action_taken, written_locations[], chosen_variant_id? }`，供 phase 4 / 5 READ。本步不寫檔。
