<!-- INSTRUCT: Phase 5 RENDER 本 template，依 references/pencil-prompt-sections.md §1 對照表填值。
     所有 {{PLACEHOLDER}} 必填；缺值 → 留 <!-- TODO: clarify-loop 未回收 X --> 並 fail Phase 5 ASSERT。
     最終輸出落在 ${SPECS_DIR}/${current_package_slug}/design/uiux-prompt.md。
     v2 結構：以 COMPONENT CATALOG 為主（per-component state matrix），FRAME COMPOSITION 為輔（組合圖）。 -->

# 🎨 Pencil Design Brief — {{PROJECT-NAME}}

## ROLE
You are a **senior product designer** building **{{PROJECT-NAME}}** in Pencil from the discovery contract. Treat `spec.md` + `*.activity` + `*.feature` + atomic-rules as the source of truth for **what** must exist; this brief tells you **how** it should look.

**Design unit = component, not page.** 每個 component 是獨立的 Pencil scene，含其所有 state 變體；frame 只是 component 的組合圖（單一 canonical state），由 `FRAME COMPOSITION TABLE` 指定。

Output `.pen` 必須含：
1. 每個 component 一個 scene，列出全部 state 變體
2. 每個 frame 一個組合 scene（canonical state combo）
偏離將導致下游 `aibdd-pen-to-storybook` 翻譯為 `<ComponentId>.stories.tsx` 時對不上。

## VISUAL DIRECTION (NON-NEGOTIABLE)
**Style**: {{VISUAL-STYLE}}

**Required qualities** (must hit 6+):
{{REQUIRED-QUALITIES}}

## DESIGN TOKENS
<!-- INSTRUCT: render $$clarify_resolved.tokens 成 CSS custom property 區塊，prefer OKLCH，hex 為替代格式 -->
```css
{{TOKENS}}
```

**Breakpoints**: {{BREAKPOINTS}}
Mobile-first；stack panels vertically below the smallest desktop breakpoint。

## COMPONENT CATALOG ← Story / 測試合約 SSOT
<!-- INSTRUCT: render $$component_inventory ⊕ $$clarify_resolved.components；
     每個 component 一個 ### sub-section，含 state matrix table。
     state matrix 缺漏 = 下游 form-story 補不到該 component 的 Story export → ASSERT 失敗。 -->

**畫法規約**：每個 component 開一個獨立 Pencil scene。scene 內橫向排列其全部 state 變體，每個變體下方標 state code（如 `idle` / `hover` / `disabled` / `rejected.duplicate_name`）。文字節點的 accessible name 必須一字不差來自下方 ANCHOR NAME TABLE。

{{COMPONENT-CATALOG}}

<!-- 渲染示意（每個 component 一段）：

### `CreateRoomButton` (button)

**Used by frames**: `lobby`, `landing`
**Anchor name**: `建立房間`（見 ANCHOR NAME TABLE）

| State | Source | 視覺提示 |
|---|---|---|
| idle | base | accent bg + body font + medium radius |
| hover | base | accent bg lift + shadow soft |
| focus | base | focus ring (accent, 2px) |
| active | base | scale 0.98 |
| disabled | base | surface 60% + text-on-disabled |
| submitting | F-001.R1 (waiting for server) | spinner + label dim |
| rejected.duplicate_name | F-001.R2 | error-on accent + inline message slot |
| error.system | activity.CreateRoom DECISION system_error branch | error-on accent + retry slot |

-->

## FRAME COMPOSITION TABLE ← 組合圖
<!-- INSTRUCT: render $$frame_composition ⊕ $$clarify_resolved.frame_layouts；
     一 frame 一張組合圖；只畫 canonical state combo，**不**展開其他 state。 -->

**畫法規約**：每個 frame 開一個獨立 Pencil scene，名稱 = `Frame: <frame_slug>`。scene 內依 `layout pattern` 把對應 component 擺好，每個 component 以 catalog 中的 `canonical state` 呈現。`hidden` slot 用淺灰邊框佔位、標 `(hidden by default)`，**不**畫實際內容。

| Frame slug | Activity node | Feature Rule | Layout | Uses (component, canonical state) | Sticky | Hidden slots |
|---|---|---|---|---|---|---|
{{FRAME-COMPOSITION-TABLE}}

## ANCHOR NAME TABLE ← Story / 測試合約 SSOT
<!-- INSTRUCT: render $$clarify_resolved.copy_decisions（component-keyed）成 markdown table -->

每個互動 component 的文字節點**必須一字不差**寫成下表 `accessible name`（同義詞改寫會直接破壞 test step 合約）：

| Component | `role` | accessible name | source rule |
|---|---|---|---|
{{ANCHOR-NAME-TABLE}}

## INTERACTION SPEC
<!-- INSTRUCT: render $$clarify_resolved.interactions（component × state-transition）+ 全域 reduced-motion 規則 -->

{{INTERACTION-SPEC}}

**全域**：`prefers-reduced-motion: reduce` 時所有 motion 降級為瞬時或單次閃光；狀態變化必須仍清晰可辨。

## DELIVERABLES (Pencil scene 落地順序)
<!-- INSTRUCT: 先列全部 component scene（依字母順序），再列 frame composition scene（依 activity flow 拓樸序） -->

**第一階段：Component scenes**（每個 component 一個 scene，含全部 state 變體）
**第二階段：Frame composition scenes**（依下列順序，每個 frame 一個組合 scene）：

{{DELIVERABLES-ORDER}}

## ACCEPTANCE CRITERIA
- [ ] 每個 component 都有獨立 scene，且該 component 在 catalog 列的所有 state 都畫齊（缺一即 fail）
- [ ] 每個 frame 都有獨立組合 scene，使用的 component 與 FRAME COMPOSITION TABLE 一致
- [ ] 所有 component 的文字節點與 ANCHOR NAME TABLE **一字不差**
- [ ] 同一 component 跨 frame 重用時**長相一致**（不可在 A frame 與 B frame 對同一 component 改文案 / 改色）
- [ ] 兩個 breakpoint（{{BREAKPOINTS}}）的 frame composition scene 都要畫
- [ ] 文字節點使用 atomic-rules 的關鍵動詞（不可同義改寫）
- [ ] 螢幕截圖看不出「default Tailwind / shadcn / Material」痕跡
{{ACCEPTANCE-CRITERIA-EXTRA}}

## CONSTRAINTS
- 不要新增 `.feature` 沒提到的 affordance（YAGNI）
- 不要用 framework default 配色，全部走 DESIGN TOKENS
- 文字節點不要靜默改寫 atomic-rules 動詞
- 不要為了視覺加未在 Rule 中宣告的 hidden state（如 `loading_skeleton`）— 那些等 `/aibdd-plan` 補
- **不要在 frame 組合 scene 展開 component state matrix**；state 變體只畫在 component scene 內，frame scene 只展示 canonical state combo
- **不要把同一 component 拆兩份畫**（除非 catalog 真的列為兩個不同 component_id）
{{CONSTRAINTS-EXTRA}}

## HANDOFF
完成 `.pen` 後：
1. 存檔為 `design.pen`，放在 `${SPECS_DIR}/${PACKAGE}/design.pen`（**package root**，與 `spec.md` / `plan.md` 同層；與 `design/` 目錄並列形成 source ↔ built artifact 對應；**不**進 `design/` 目錄內）
2. 或：直接呼叫 `/aibdd-uiux-draw`，由 Pencil MCP 自動把本 brief 翻成 `.pen`（推薦）
3. 下一步跑 `/aibdd-plan` — plan 階段從 package root 讀 `design.pen` 萃取 I4 anchor / DSL L1 / contract
4. 再跑 `/aibdd-form-story-spec` — 透過 `aibdd-pen-to-storybook` 翻成 `<ComponentId>.stories.tsx`（每個 component 對應一個 `.stories.tsx`，每個 state 一個 Story export）
5. `.pen` 為**過渡轉換檔**；`*.stories.tsx` 落地後即為 binding anchor 的 SSOT，`.pen` 不保證長期保留
