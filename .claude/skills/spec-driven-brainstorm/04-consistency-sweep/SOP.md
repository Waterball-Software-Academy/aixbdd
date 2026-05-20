# SOP

緣由：phase 3 寫入新 fact 後，`${SPEC_FILE}` 內可能殘留與新 fact 矛盾的舊段落、應 archive 的 brainstorming subsection、或級聯失效的下游 subsection（譬如 Solution 改了但 Examples 仍對應舊 Solution）。本 phase 維護「spec.md 即 absolute design」invariant — 任何違反的段落都得在本輪內收乾。

0. RESOLVE arguments —— 沿用頂層綁定；READ `$bind_summary`、`$classify_summary`、`$apply_summary`。本步不寫檔。

1. READ `rules/archive-trigger.md`、`rules/consistency-invariants.md`（首次迭代後可快取；以快取為由跳過重讀時須 ASSERT 規則檔未變更）。

2. READ `${SPEC_FILE}` 全文為 `$spec_text_after_apply`。本步只 READ。

3. **BRANCH** on `$classify_summary.action`：

   3.1 `commit-variant` →
      - 套用 `rules/archive-trigger.md` §1：本輪 commit 之 target issue 內 `## Brainstorming` subsection **必須**全段 archive。
      - DERIVE `$archive_filename = "<issue-slug>-brainstorm-<UTC-yyyymmddThhmmssZ>.md"`，slug 自 issue title 推得（lower-case + kebab）。
      - WRITE `${ARCHIVE_DIR}/$archive_filename`：將該 issue 內 `## Brainstorming` heading 及其 body（含所有 Sn 區塊與比較表）整段複製為檔案內容；檔案開頭加上單行 `# Archived Brainstorming — <issue title> — <UTC timestamp>` heading。**本步若 `${ARCHIVE_DIR}` 不存在則一併 CREATE 目錄**；本步僅允許 WRITE `${ARCHIVE_DIR}/$archive_filename` 與 CREATE `${ARCHIVE_DIR}/` 目錄；禁止寫入其他檔案。
      - UPDATE `${SPEC_FILE}`：刪除該 issue 內 `## Brainstorming` heading 及其全部 body。本步僅允許 UPDATE `${SPEC_FILE}` 之該 subsection 刪除；禁止改動其他 subsection。

   3.2 `revise` →
      - 套用 `rules/consistency-invariants.md` §1（cascade）：若 `$classify_summary.target_subsection` 為上游（譬如 `definition` 或 `problem-space`），DERIVE 受影響之下游 subsection 列表 `$cascade_targets`。
      - THINK：對每個 `$cascade_targets[i]` 比對 `$spec_text_after_apply` 是否含與新 fact 衝突之段落；衝突段落寫入 `$cascade_obsolete_blocks`。本步只產出判斷，不寫檔。
      - 若 `$cascade_obsolete_blocks` 非空 → UPDATE `${SPEC_FILE}`：對每個 obsolete block，**整段替換**為「依新 fact 推導之肯定式描述」（不留新舊並存、不留 strikethrough）。本步僅允許 UPDATE `${SPEC_FILE}` 範圍受影響 subsection；禁止跨 issue 級聯改動（跨 issue 須由 user 另開 revise）。

   3.3 其餘 action（`create-issue` / `append-fact` / `advance-subsection` / `defer` / `ambiguous`）→
      - 套用 `rules/consistency-invariants.md` §2（同 subsection sweep）：掃描本輪 phase 3 寫入之 subsection，移除違反 `as-is-style` 之殘留（hedging 字、TODO 痕跡、`?` 句尾、外部 ticket ID 引用）。
      - 違規片段如為 phase 3 本輪寫入 → UPDATE `${SPEC_FILE}` 改寫成合規描述；如為既有殘留 → 同樣 UPDATE 改寫。本步僅允許 UPDATE `${SPEC_FILE}`；禁止 CREATE 其他檔案。

4. ASSERT 收尾：
   - `${SPEC_FILE}` 內**不得**同時存在 `## Solution` 與該 issue 之 `## Brainstorming`（commit-variant 已 archive 之 invariant）。
   - `${SPEC_FILE}` 內**不得**含 `rules/as-is-style.md` §1 列舉之任一禁用模式（hedging / TODO / `?` 句尾 / 外部 ticket ID 等）。
   - `${SPEC_FILE}` 內每個 issue 之 subsection 順序**必須**符合 progressive disclosure。
   - 任一 ASSERT 失敗 → 列出違規位置與規則名，**STOP**，本輪 phase 4 不算完成。

5. DERIVE `$sweep_summary = { archived_files[], purged_blocks[], cascade_rewrites[] }`，供 phase 5 READ（phase 5 emit prompt 時可向 user 告知 archive 行為）。本步不寫檔。
