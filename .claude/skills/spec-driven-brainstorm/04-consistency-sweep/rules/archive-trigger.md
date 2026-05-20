# Archive Trigger 規則

- 唯一觸發 archive 之條件**必為** `$classify_summary.action = commit-variant`；**禁止**在其他 action 路徑下動 archive（譬如 user 只是 `add-fact-to-current` 或 `pivot-section` 時，brainstorming 不得被砍）。
- Archive 之 scope **必為**「該輪 target issue 之 `## Brainstorming` 整段」；**禁止**只 archive 未被選中的 Sn 區塊而保留被選中的 Sn — 一律整段搬走。
- Archive 之目的地**必為** `${ARCHIVE_DIR}/<issue-slug>-brainstorm-<UTC-yyyymmddThhmmssZ>.md`；**禁止**寫到 `${SPEC_DIR}` 根目錄、**禁止**寫到 `${ARCHIVE_DIR}` 外。

## §1 Archive 完整性

- 被 archive 之檔案內容**必須**包含：
  - 首行 archive metadata heading：`# Archived Brainstorming — <issue title> — <UTC timestamp>`。
  - 完整 `## Brainstorming` heading 與其下所有 Sn 區塊（含 pros / cons）與比較表（若有）。
- **禁止**只 archive 部分 Sn、**禁止**刪除 pros / cons、**禁止**改寫文字 — archive 必須是原段落 verbatim 複本，方便日後 audit「當時為何選 Sn」。

## §2 Archive 與 `${SPEC_FILE}` 刪除之原子性

- WRITE archive 檔與 UPDATE `${SPEC_FILE}` 刪除原段落**必須**在同一 phase 4 step 3.1 內連續完成；**禁止**只 WRITE archive 而不刪 `${SPEC_FILE}` 段落（會造成內容重複）、**禁止**只刪 `${SPEC_FILE}` 段落而不 WRITE archive（會永久遺失方案歷史）。
- 任一步失敗 → STOP 並回退所有本輪變動，不得留下「半 archive」狀態。

## §3 Slug 推導

- `<issue-slug>` 從 issue title 推得：lower-case、空白與標點轉 `-`、保留 ASCII 字母數字與 `-`、移除其他符號。
  - 範例：`# 1. 把 dsl.yml 的格式改得更 concise` → slug = `ba-dsl-yml-de-ge-shi-gai-de-geng-concise`（直譯保留語意，但對非 ASCII 字元無 transliteration 規則者直接 strip → 範例 fallback：`issue-1`）。
  - 若 title 含主要為 CJK 字元、strip ASCII 後 slug 為空 → fallback `issue-<N>`。

## Good

- User commit S2 後，phase 4 WRITE `${ARCHIVE_DIR}/issue-1-brainstorm-20260520T103412Z.md`（內容 = 原 `## Brainstorming` verbatim + 首行 metadata heading），同 phase UPDATE `${SPEC_FILE}` 刪除該 `## Brainstorming` heading 與 body。
- Archive 檔保留 S1 / S2 / S3 完整 pros / cons 與比較表，未來 audit 可追溯「user 為何在當時 commit S2」。

## Bad

- User commit S2 後，phase 4 只刪 `## Brainstorming` 而沒寫 archive — 違反 §2 原子性，方案歷史永久遺失。
- Phase 4 把 brainstorming archive 到 `${SPEC_DIR}/dsl-brainstorm.md`（根目錄）— 違反 archive 目的地必為 `${ARCHIVE_DIR}/` 之約束。
- Phase 4 只 archive S1 / S3 而把 S2 留在 `${SPEC_FILE}` 的 `## Brainstorming` block 內 — 違反「整段搬走」，spec 內仍殘留 brainstorming subsection。
- 在 `add-fact-to-current` 路徑下，AI 順手把 `## Brainstorming` archive 掉 — 違反「唯一觸發條件為 commit-variant」；user 還沒 commit 之前 brainstorming 不得被動掉。
- Archive 檔案名只用 `brainstorm.md`（沒帶 issue-slug 與 timestamp）— 違反 §3 命名規約，後續 commit 多次會撞名互蓋。
