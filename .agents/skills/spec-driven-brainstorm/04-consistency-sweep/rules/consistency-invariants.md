# Consistency Invariants 規則

`${SPEC_FILE}` 每輪 phase 4 結束時**必須**同時滿足下列 invariants；任一違反 → ASSERT 失敗 STOP。

## §1 Cascade Rewrite — upstream 改了，downstream 必須跟改

- 當 `$classify_summary.action = revise` 且 `target_subsection ∈ {definition, problem-space}` 時，**必須** DERIVE 下游受影響 subsection 列表 `$cascade_targets`：
  - `definition` 變更 → cascade 至 `problem-space`、`solution`、`examples`、`implementation`、`implementation-package-structure`（凡存在者皆掃）。
  - `problem-space` 變更（譬如新增 / 刪除 / 改寫某 Pn）→ cascade 至 `solution`、`examples`、`implementation`、`implementation-package-structure`。
  - `solution` 變更 → cascade 至 `examples`、`implementation`、`implementation-package-structure`。
  - `examples` 變更 → cascade 至 `implementation`、`implementation-package-structure`。

- Cascade 範圍**僅限於**同一 issue 內；**禁止**跨 issue cascade（譬如改 issue 1 之 solution 不自動改 issue 2 之任何內容）。跨 issue 衝突須由 user 另開 `revise-prior-decision` 處理。
- Cascade rewrite **必須**整段替換受影響段落（如同 phase 3 `revise` 路徑），**不留**「原為 X，現為 Y」之 transitional narrative。
- THINK 推導 cascade 時 **僅允許 read-only 觀察**；本步不直接落地，落地走步驟 3.2 之 UPDATE。

## §2 As-Is Style 全檔 sweep

- `${SPEC_FILE}` 全檔**不得**含 `rules/as-is-style.md` §1 列舉之禁用語句／模式：
  - hedging（「可能」「也許」「應該」「視 case」「通常」「最好」「建議」）
  - transitional narrative（「之前」「原本」「後來」「現在」「TODO」「待定」）
  - Q&A 形態（spec 段落含 `？` / `?`、含「你覺得」「需要 …？」）
  - 外部 artifact 引用（ticket ID / PR # / commit hash / cross-repo 路徑 / 規劃工件代號）
  - 猶豫脈絡（「A 與 B 都可以」「目前傾向 X 但未拍板」「TBD」）
- 違規片段為 phase 3 本輪寫入 → UPDATE 重寫；為既有殘留 → 同 UPDATE 重寫；無法判定如何重寫 → STOP 並 phase 5 emit clarify batch。

## §3 Solution / Brainstorming 互斥

- 任一 issue 內，`## Solution` 與 `## Brainstorming` heading **不得**同時存在於 `${SPEC_FILE}`。
- `commit-variant` 後 `## Solution` 寫入 + `## Brainstorming` archive 必為原子操作（見 `archive-trigger.md` §2）；若 phase 4 結束時偵測到兩者並存 → 視為前一輪未完成 archive，**STOP** 並提示 user 此 inconsistent 狀態（不主動恢復，因為可能是 user 手動編輯）。

## §4 Progressive Disclosure Order 全檔 sweep

- 每個 issue 內 H2 subsection 在檔案中之出現順序**必須**對齊 progressive disclosure 順序（`definition` → `problem-space` → ...）。
- 若 phase 3 step 4.3 或 4.4 寫入新 subsection 時插入位置錯誤（例：把 `## Solution` 寫在 `## Definition` 之前）→ UPDATE 重排該 issue 內 H2 順序。

## Good

- User 改了 issue 1 的 P2 → phase 4 cascade 偵測 `## Solution` 內 `**Policy 1**` 段落原本描述「解 P1 與 P2 之 SSOT 錯位」仍提舊版 P2，UPDATE 整段重寫為符合新 P2 之描述；`## Examples` 對應 Policy 1 之示範也跟著重寫。
- User commit S2 後 phase 4 順利完成：`${SPEC_FILE}` 內 `## Brainstorming` 消失、`## Solution` 出現、`${ARCHIVE_DIR}/issue-1-brainstorm-<ts>.md` 寫入完整原 brainstorming。
- Phase 4 step 4 ASSERT 全過：spec 全檔無 `?` 句尾、無「TODO」字串、`## Solution` 與 `## Brainstorming` 不共存。

## Bad

- User 改 issue 1 的 P2 但 phase 4 沒掃 `## Solution`，`**Policy 1**` 仍提舊 P2 描述 — 違反 §1 cascade，spec 內出現上下不一致。
- User 改 issue 1 的 P2 順便連 issue 2 的 Solution 也被 AI 自動改寫 — 違反 §1「禁止跨 issue cascade」；應由 user 另開 revise。
- `${SPEC_FILE}` 內同時保留 `## Brainstorming` 與 `## Solution`（譬如 commit-variant 後忘 archive）— 違反 §3 互斥；phase 4 ASSERT 該 STOP。
- Spec 段落留「**Policy 1**: 用 plugin loader（**待定**，可能改 declarative）」— 違反 §2 as-is style sweep；phase 4 應 UPDATE 改寫成「採用 plugin loader」純肯定式。
- Issue 1 內 H2 順序為 `## Solution` → `## Definition`（因 phase 3 插入位置錯誤）— 違反 §4，phase 4 應重排。
