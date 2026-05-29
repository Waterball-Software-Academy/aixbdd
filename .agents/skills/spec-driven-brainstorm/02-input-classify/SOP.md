# SOP

緣由：把 user 本輪訊息收斂為「target_issue × target_subsection × action」三元組，後續 phase 3 才知道要寫哪、寫什麼，phase 4 才知道誰是 obsolete、phase 5 才知道下一句該問什麼。沒在這裡 ASSERT 分類確定，phase 3 會在 active pointer 假設下寫錯 subsection；phase 4 會誤砍合法內容。

0. RESOLVE arguments —— 沿用頂層綁定；READ `$bind_summary`（由 phase 1 DERIVE）。本步不寫檔。

1. READ user 本輪最新訊息文字（已在對話 context）為 `$user_msg`。本步不寫檔。

2. THINK：對 `$user_msg` 分類意圖至 enum，規則完全依 `rules/intent-enum.md`（含對照表與 Good／Bad 範例，逐字對照不得心證）：
   - `new-issue` — 引入新議題
   - `add-fact-to-current` — 對當前 active subsection 補充事實／意見
   - `confirm-section-done` — 明確或暗示「這段聊完了，下一步」
   - `pick-variant` — 在 brainstorming 中選定方案
   - `revise-prior-decision` — 修正先前已寫進 spec 的事實／決議
   - `pivot-section` — 跳到別的 issue 或別的 subsection 繼續聊
   - `meta-question` — 問現況、進度、不要求更新 spec
   - `ambiguous` — 訊息語意不夠收斂；本輪 phase 3 / 4 跳過、phase 5 emit 批次提問
   - 結果寫入 `$intent`。本步只產出分類判斷，不寫檔。

3. DERIVE `$target_issue`，規則依 `rules/target-resolution.md` §1：
   - `new-issue` → `$target_issue = ${issues_count} + 1`（後續 phase 3 用於 CREATE H1）。
   - `pivot-section` → 依 `$user_msg` 顯式引用之 issue 編號或 title 對齊既有 `$issues`；不顯式則 fallback 至 `$active_pointer.last_issue_index`。
   - 其餘 intent → `$target_issue = $active_pointer.last_issue_index`。
   - 若 `$active_pointer.last_issue_index = none` 且 `$intent ∉ {new-issue, meta-question, ambiguous}` → 強制 reclassify `$intent = ambiguous`，記 `$ambiguity_reason = "no active issue but intent expects one"`。

4. DERIVE `$target_subsection` ∈ enum `{definition, problem-space, brainstorming, solution, examples, implementation, implementation-package-structure, none}`，規則依 `rules/target-resolution.md` §2：
   - 依 `$intent` + `$active_pointer.last_active_subsection` + `$user_msg` 顯式 subsection 引用判定。
   - `meta-question` / `ambiguous` → `$target_subsection = none`。
   - 違反 progressive disclosure 順序之 pivot（譬如目前還在 problem-space，user 要求跳 implementation）→ 強制 reclassify `$intent = ambiguous`，記 `$ambiguity_reason = "pivot violates progressive disclosure"`。

5. DERIVE `$action` ∈ enum `{create-issue, append-fact, advance-subsection, commit-variant, revise, defer, ambiguous}`，規則依 `rules/intent-enum.md` 對照表（intent ↔ action 一對一映射）。

6. DERIVE `$classify_summary = { target_issue, target_subsection, action, ambiguity_reason? }`，供 phase 3 / 4 / 5 READ。本步不寫檔。
