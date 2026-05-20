# SOP

緣由：phase 3 / 4 落地 spec 之後，AI 必須對 user 拋下一句具體 prompt 推動對話前進——「Problem Space 還有要聊的嗎？」「方案決定了嗎？」「需要看 Examples 嗎？」之類；ambiguous 路徑則 emit 一次性 batch 提問。沒這 phase，user 收到 spec 更新但不知道下一步該做什麼，對話會卡住。

0. RESOLVE arguments —— 沿用頂層綁定；READ `$bind_summary`、`$classify_summary`、`$apply_summary`、`$sweep_summary`。本步不寫檔。

1. READ `rules/prompt-patterns.md`（首次迭代後可快取；以快取為由跳過重讀時須 ASSERT 規則檔未變更）。

2. DERIVE `$elicit_mode` ∈ enum `{chat-text, ask-user-question}`：
   - `$classify_summary.action = ambiguous` → `$elicit_mode = ask-user-question`（一次性 batch 提問）。
   - `$classify_summary.action ∈ {advance-subsection, commit-variant}` 且推進到 `brainstorming` / 需要 user 在離散選項間挑選 → `$elicit_mode = ask-user-question`。
   - 其餘 → `$elicit_mode = chat-text`（開放式問句，user 文字回應）。

3. DERIVE `$prompt_payload`，規則依 `rules/prompt-patterns.md`：
   - `$elicit_mode = chat-text` → `$prompt_payload = { text: "..." }`，依當前 state（target_issue、target_subsection、action 結果）選擇對應 prompt pattern。
   - `$elicit_mode = ask-user-question` → `$prompt_payload = { questions: [...] }`，依 ambiguity_reason 或 next-step decision points 組裝批次題目。

4. EMIT prompt 至 user：
   - `$elicit_mode = chat-text` → 直接於本輪 chat 回應結尾輸出 `$prompt_payload.text`，並附 1 行說明本輪 spec 變更摘要（譬如「已寫入 issue 1 之 Problem Space P3；archive 既無動作」）。
   - `$elicit_mode = ask-user-question` → 透過 host 提供之 `AskUserQuestion` 工具（或等效互動工具）emit `$prompt_payload.questions`。
   - 本步**不寫檔**；只與 user 互動。

5. ASSERT 終態：
   - 本輪 phase 1–5 已全部 EXECUTE 完成；Tier 0 todo 將 (5) 標為 completed。
   - 若 `$sweep_summary.archived_files` 非空，於 chat-text 結尾**必須**告知 user archive 行為（譬如「已 archive issue 1 之 brainstorming 至 `${ARCHIVE_DIR}/issue-1-brainstorm-20260520T103412Z.md`」）。
