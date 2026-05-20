# SOP

緣由：把後續所有 sub-SOP 賴以決策的 `${SPEC_FILE}` 當前狀態一次 bind 起來——檔案是否存在、issues 結構、每個 issue 內已存在的 subsection 與其完成度、active 指針落點。沒在這裡 ASSERT 完，phase 2 的 input classify 會在假設不成立下 silently 寫錯位置；phase 4 的 consistency sweep 會誤把合法既有內容當 obsolete 砍掉。

0. RESOLVE arguments —— 確認 `${SPEC_DIR}`、`${SPEC_FILE}`、`${ARCHIVE_DIR}` 已由頂層 SKILL.md 步驟 0 綁定；任一為 unbound → STOP 並回報缺鍵。本步禁止落地任何 artifact。

1. SEARCH `${SPEC_FILE}` 是否存在
   - 存在 → 進入步驟 2。
   - 不存在 → CREATE `${SPEC_FILE}`，內容為單行 `# Spec\n`（最小 bootstrap 骨架）。本步僅允許 CREATE `${SPEC_FILE}` 一檔；禁止建立 `${ARCHIVE_DIR}/**`、禁止建立其他 sibling 檔案、禁止寫入任何 placeholder issue / subsection。

2. READ `${SPEC_FILE}` 全文為 `$spec_text`。本步只 READ，不寫檔。

3. PARSE issue 結構為 `$issues`：以 regex `^# (\d+)\. (.+)$` 匹配 H1 headings，每筆記錄 (index = 抓到的整數 N, title, line_start, line_end)；line_end 為下一個 H1 之前一行，或檔尾。
   - 非 `# N. <title>` 形式的 H1（例如裸 `# Spec`）標為 root header，不計入 `$issues`。
   - 同一 index 出現兩次 → STOP 並提示 user 修檔（這是 spec 結構違規，本 skill 不主動 renumber）。

4. PARSE 每個 `$issues[i]` 內含的 subsection 為 `$state[i]`：以 `^## (.+)$` H2 heading 為單位，將 heading 文字 normalize 至 enum `{definition, problem-space, brainstorming, solution, examples, implementation, implementation-package-structure}`；normalization 以對 lower-case + kebab 化為準（譬如 `## Problem Space` → `problem-space`、`## Implementation Package Structure` → `implementation-package-structure`）。不在 enum 內的 H2 視為 `unknown`，記入 `$state[i].unknown` 但不參與 progressive disclosure 推理。
   - 對每個已存在 enum subsection 標記 completion 狀態之一：
     - `present-with-content` — heading 下方至少 1 行非空白內容（fenced block、bullet、段落皆算）
     - `present-empty` — heading 存在但 body 全空白
     - `absent` — heading 不存在於該 issue
   - 結果寫入 `$state[i] = { subsection_name → status }`。

5. DERIVE `$active_pointer = (last_issue_index, last_active_subsection)`：
   - `last_issue_index` = `$issues` 內 index 數值最大的一筆；若 `$issues` 為空 → `last_issue_index = none`。
   - `last_active_subsection` = 對 `last_issue_index` 之 `$state` 按 progressive disclosure 順序（`definition` → `problem-space` → `brainstorming` → `solution` → `examples` → `implementation` → `implementation-package-structure`）取最後一個 `present-with-content` 或 `present-empty` 的 subsection；若該 issue 所有 enum subsection 皆 absent → `last_active_subsection = none`。
   - 若 `last_issue_index = none` 與 `last_active_subsection = none`：表示 spec 剛 bootstrap、無任何 issue，後續 phase 2 須將 user 訊息視為 `new-issue` 候選。

6. DERIVE `$bind_summary = { spec_exists, issues_count, active_pointer, state_map }`，供後續 sub-SOP READ。本步不寫檔。
