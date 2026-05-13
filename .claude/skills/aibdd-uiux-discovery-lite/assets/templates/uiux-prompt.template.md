<!-- INSTRUCT: Lite template. Phase 5 RENDER 本 template，依 references/lite-prompt-sections.md 填值。
     最終輸出仍落在 ${SPECS_DIR}/${current_package_slug}/design/uiux-prompt.md，讓 /aibdd-uiux-draw 可直接讀取。 -->

# 🎨 Pencil Design Brief Lite — {{PROJECT-NAME}}

MODE: lite-happy-path

## ROLE
You are a senior product designer building a **minimal happy-path visual draft** for **{{PROJECT-NAME}}**.

Only draw screens/components selected from `.feature` evidence. Do **not** invent error, empty, loading, disabled, hover, active, or rejected states unless the selected happy-path step explicitly mentions them.

## LITE SCOPE — selected feature-mentioned / happy-path screens
{{LITE-SCOPE-SUMMARY}}

## VISUAL DIRECTION
**Style**: {{VISUAL-STYLE}}

**Required qualities**:
{{REQUIRED-QUALITIES}}

## DESIGN TOKENS
```css
{{TOKENS}}
```

**Breakpoints**: {{BREAKPOINTS}}

## COMPONENT CATALOG ← Story / 測試合約 SSOT（lite）

**Lite rule**: one component = one primary/canonical state only. If you need full state coverage, stop and rerun `/aibdd-uiux-discovery` full version.

{{COMPONENT-CATALOG}}

<!-- Render example:
### `SubmitOrderButton` (button)

**Used by frames**: `checkout-payment`
**Anchor name**: `送出訂單`

| State | Source | Visual hint |
|---|---|---|
| idle | checkout.feature / Successful payment | primary CTA |
-->

## FRAME COMPOSITION TABLE ← selected frames only

Each frame gets exactly one composition scene. Use only the component state listed in `Uses`.

| Frame slug | Source feature/scenario | Layout | Uses (component, canonical state) | Purpose |
|---|---|---|---|---|
{{FRAME-COMPOSITION-TABLE}}

## ANCHOR NAME TABLE ← Story / 測試合約 SSOT

Interactive components in lite scope must use these exact accessible names:

| Component | `role` | accessible name | source rule/step |
|---|---|---|---|
{{ANCHOR-NAME-TABLE}}

## DELIVERABLES (Pencil scene order)

1. Draw the selected frame scenes in this order.
2. Draw only listed primary component states.
3. Do not draw excluded scenarios.

{{DELIVERABLES-ORDER}}

## ACCEPTANCE CRITERIA
- [ ] Every selected frame in `LITE SCOPE` has one Pencil scene.
- [ ] Every component in `COMPONENT CATALOG` appears only in its listed primary/canonical state.
- [ ] No excluded scenario is drawn.
- [ ] All interactive text nodes match `ANCHOR NAME TABLE` exactly.
- [ ] Breakpoints listed above are represented for selected frames only.
- [ ] The result looks intentionally designed and does not look like default Tailwind / shadcn / Material.
{{ACCEPTANCE-CRITERIA-EXTRA}}

## CONSTRAINTS
- Do not add affordances that are not mentioned by selected `.feature` evidence.
- Do not expand state matrices.
- Do not draw error/empty/loading/rejected unless the selected step explicitly mentions it.
- Do not use framework default palette; use design tokens.
{{CONSTRAINTS-EXTRA}}

## HANDOFF
完成 `.pen` 後：
1. 存檔為 `design.pen`，放在 `${SPECS_DIR}/${PACKAGE}/design.pen`（package root，與 `spec.md` / `plan.md` 同層）。
2. 可直接呼叫 `/aibdd-uiux-draw`，由 Pencil MCP 自動把本 lite brief 翻成 `.pen`。
3. 下一步跑 `/aibdd-plan`。
4. 若後續要補錯誤、空狀態、loading、rejected 或完整 component states，重跑 `/aibdd-uiux-discovery` full version。
