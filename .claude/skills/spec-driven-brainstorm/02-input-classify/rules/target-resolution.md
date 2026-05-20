# Target Issue × Subsection 解析規則

## §1 `$target_issue` 解析

- `$target_issue` **必為**「正整數 issue index」或字面 `none`；不得為標題字串、不得為 range。
- 解析優先序（高 → 低）：
  1. `$user_msg` 顯式引用 issue 編號（譬如「issue 2」「議題 #1」「第三個議題」）→ `$target_issue = 該 index`。
  2. `$user_msg` 顯式引用 issue title 片段且可唯一匹配 `$issues` 中某筆 → `$target_issue = 該 index`。
  3. 否則 fallback `$target_issue = $active_pointer.last_issue_index`。
  4. `$intent = new-issue` → `$target_issue = ${issues_count} + 1`（覆蓋上述 fallback）。

- 顯式引用無法唯一匹配（譬如 user 說「issue 2」但 `$issues` 只有 1 筆，或 title 片段同時對應多筆）→ 強制 reclassify `$intent = ambiguous`，記 `$ambiguity_reason = "target_issue unresolvable: <reason>"`。

## §2 `$target_subsection` 解析

- `$target_subsection` **必為** enum `{definition, problem-space, brainstorming, solution, examples, implementation, implementation-package-structure, none}` 之一。
- 解析優先序（高 → 低）：
  1. `$user_msg` 顯式引用 subsection 名稱（譬如「Definition」「P3 那條」對應 problem-space、「S2」對應 brainstorming）→ `$target_subsection = 該 enum`。
  2. `$intent = new-issue` → `$target_subsection = definition`（新 issue 從 definition 起步）。
  3. `$intent = confirm-section-done` → `$target_subsection = next($active_pointer.last_active_subsection)`，next 依 progressive disclosure 順序推進一格。
  4. `$intent = pick-variant` → `$target_subsection = solution`（pick-variant 一定把當前 brainstorming 結果落到 solution）。
  5. `$intent ∈ {add-fact-to-current, revise-prior-decision}` → `$target_subsection = $active_pointer.last_active_subsection`。
  6. `$intent = pivot-section` → 依 `$user_msg` 顯式跳轉目標；無顯式則 `$target_subsection = $active_pointer.last_active_subsection`。
  7. `$intent ∈ {meta-question, ambiguous}` → `$target_subsection = none`。

- Progressive disclosure 順序（固定）：`definition` → `problem-space` → `brainstorming` → `solution` → `examples` → `implementation` → `implementation-package-structure`。
- Pivot 跳轉**僅允許**回到順序上**已存在**的 subsection；**禁止**前向跳轉到尚未開啟之 subsection（譬如目前 active 在 problem-space，user 要求跳 implementation）→ 強制 reclassify `$intent = ambiguous`，記 `$ambiguity_reason = "pivot violates progressive disclosure"`。

## Good

- `$intent = new-issue`、`$user_msg = "順便聊聊 dsl.yml 檔名"`、`${issues_count} = 2` → `$target_issue = 3`、`$target_subsection = definition`。
- `$intent = confirm-section-done`、`$active_pointer = (1, problem-space)` → `$target_issue = 1`、`$target_subsection = brainstorming`（推進一格）。
- `$intent = pick-variant`、`$active_pointer = (1, brainstorming)` → `$target_issue = 1`、`$target_subsection = solution`（archive brainstorming + 寫 solution，於 phase 3 / 4 落地）。
- `$intent = pivot-section`、`$user_msg = "回 issue 1 補 P4"`、`$issues` 含 index 1 → `$target_issue = 1`、`$target_subsection = problem-space`（顯式回跳合法已存在 subsection）。
- `$intent = revise-prior-decision`、`$active_pointer = (2, solution)`、`$user_msg = "Solution 那段第二條要改"` → `$target_issue = 2`、`$target_subsection = solution`。

## Bad

- `$intent = new-issue`、`$target_issue` 設為某 issue title 字串（`"dsl.yml 檔名"`）→ 違反「必為正整數 index」契約，phase 3 無從定位 H1 編號。
- `$intent = confirm-section-done`、`$active_pointer = (1, definition)`，AI 直接把 `$target_subsection` 設為 `examples`（跳過 problem-space / brainstorming / solution）→ 違反 progressive disclosure 順序；應為 `problem-space`。
- `$intent = pivot-section`、`$active_pointer = (1, problem-space)`、user 要求跳 implementation → AI 直接設 `$target_subsection = implementation` → 違反「pivot 僅允許回跳已存在」；應 reclassify 為 `ambiguous` 並由 phase 5 batch 提問。
- 顯式 `$user_msg = "issue 2"` 但 `$issues` 只有 1 筆，AI 直接 fallback `$target_issue = 1` → 應 reclassify 為 `ambiguous`（target_issue unresolvable），不得替 user 猜。
- `$intent = pick-variant`、`$target_subsection` 設為 `brainstorming`（保留在 brainstorming）→ 違反「pick-variant 一定落到 solution」；應為 `solution`，brainstorming 由 phase 4 archive。
