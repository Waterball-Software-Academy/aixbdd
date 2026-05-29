# As-Is 寫作規則

- 寫入 `${SPEC_FILE}` 的每一段文字**必為**「肯定式絕對描述」；**禁止**留 hedging、Q&A、transitional narrative、外部 ticket / PR / commit ID 引用。
- 改寫 user 訊息為 spec 段落時，AI **必須**主動把問句轉肯定句、把試探語轉斷言句、把「之前 / 後來」歷史敘事轉純粹當前事實。

## §1 禁用語句／模式（落地前 sweep 移除）

- **Hedging 詞**：「可能」「也許」「大概」「應該」「或許」「看情況」「視 case」「通常」「一般來說」「最好」「建議」。
- **Transitional narrative**：「之前」「原本」「後來」「現在」「下一步」「先試試看」「等 X 之後再 Y」「未來」「TODO」「待定」「待釐清」。
- **Q&A 形態**：spec 段落含問號（`？` / `?`）、含「你覺得 …」「這樣可以嗎」「需要 …？」之類向 user 拋問。
- **外部 artifact 引用**：ticket ID（`SPE-123` / `JIRA-45`）、PR # / commit hash、cross-repo 路徑（`xxx-repo/foo.py`）、外部 spec section ref（`§2.1`）、規劃工件代號（`Phase 3a` / `Tier 5` / `err-NN`）。
- **猶豫脈絡**：「方案 A 與方案 B 都可以」「兩種方向都納入考慮」「目前傾向 X 但未拍板」「TBD」「TBA」。
- **Issue tracker 行為**：「重新討論」「再開一個 ticket」「之後追蹤」。

## §2 改寫範式

| User 表達 | 改寫成 spec 段落 |
|---|---|
| 「我覺得這樣應該不錯吧？」 | 「<取出 user 描述的 fact>，已採納為當前方針。」 |
| 「我們是不是該考慮 X？」 | 「採用 X — <該 X 的定義與作用範圍>。」 |
| 「之前那個方案太亂了，改用新的吧」 | 直接 replace 舊段落為新方案描述；**不留任何「之前 / 改用」字樣**。 |
| 「先試試看 S2 吧」 | 「採用 S2 — <S2 的構成>。」（去掉「先試試看」之 hedging） |
| 「TODO: 之後補 example」 | **不寫入**；若有缺，phase 5 emit prompt 邀 user 補；spec 不留 TODO 痕跡。 |

## §3 段落結構紀律

- 每段文字**必須**自含足夠 context — 讀者單看該段就能理解；**禁止**依賴上下段的脈絡 backreference（「如上所述」「同上」「同前」）。
- Bullet list 條目**必為** atomic — 一條 bullet 一個 fact，**不得**塞 2 個以上獨立 fact 連寫。
- 段落間留**單一空白行**分隔；**禁止**留多個空白行（>1）作 visual 空隙。

## Good

- User 訊息：「我覺得 P3 寫得不夠精準，應該強調 part 一定屬於 contract」→ 改寫成 `## Problem Space` 中 P3 段落直接替換為：
  > **P3: Part 定義必須錨定於 Contract 或 Data**
  >
  > Part 是某 Contract / Data spec 內的可定位元件；任何不掛 Contract / Data 的 DSL 不視為 Part-derived。harness 對非 Part-derived 之 entry 完全不處理。
- User 訊息：「想想看 S2 是不是比較好？」→ 改寫成 `## Solution` 段落（commit-variant 路徑）：
  > **Policy 1: 套件級 plugin**
  >
  > 每個 preset 為一份完整 Python sub-package，自家 harness/ 目錄持有 part_to_dsl.py 與必要 spec_parsers。aibdd-core 僅持 ABC + dynamic loader + writer / reporter。
- 段落中相關 invariant 直接以 atomic bullet 列出：
  > - aibdd-core 對任一 boundary 不做條件判斷。
  > - 新增 preset 不觸發 core 改動。

## Bad

- spec 段落寫「P3 我們**可能**需要強調 part 屬於 contract，**之後**再 review 一次」— hedging（「可能」）+ transitional narrative（「之後」）並存，違反 §1。
- spec 段落寫「**TODO**: example 之後補」— 留 TODO 痕跡，違反 §1；應改成於 `## Examples` 不寫任何條目，由 phase 5 邀 user 補；spec 中不出現 TODO 字樣。
- spec 段落寫「採用 S2 而非 S1，因為 S1 cons 太多」— 含「為什麼選 X 而不是 Y」narrative，pros/cons 與比較應已歸屬 archived brainstorming。
- spec 段落寫「**Policy 1**: 用 plugin loader，**目前**先這樣，**未來**可能改 declarative」— 含 transitional narrative（「目前」「未來」「可能」），違反 §1。
- spec 段落寫「**P1**: ... ；**這條跟前面 P2 同**」— 用 backreference「同前」，違反 §3「自含足夠 context」；應 spell-out 完整描述。
- spec 段落寫「**Policy 1**: 採用套件級 plugin，移除原本 template_generator.py，並且新增 ABC，且需要在 kickoff 階段 seed」— 一條 bullet 塞 3 個獨立 fact，違反 §3「bullet atomic」。
