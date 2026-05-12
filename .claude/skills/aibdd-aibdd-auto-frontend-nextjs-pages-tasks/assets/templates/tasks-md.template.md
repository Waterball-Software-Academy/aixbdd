# tasks.md output template

> 純 declarative 樣板。Phase 3 EMIT 階段 SOP 會 RENDER 各 §-section 並 concat 寫入 `${TASKS_OUTPUT_PATH}`。
>
> **每個 `<<...>>` 是 placeholder**，由對應 SOP step 的變數填值。

---

## §header

```markdown
# Frontend Implementation Tasks — <<PROJECT_NAME>>

> Owner：下游 `/aibdd-auto-frontend-msw-api-layer`（Phase 1）+ `/aibdd-auto-frontend-nextjs-pages`（Phase 2）執行藍圖
> Generator：`/aibdd-aibdd-auto-frontend-nextjs-pages-tasks`
> 完成原則：視覺對得上 PNG export + 行為符合 acceptance；**前端不走 TDD**（不寫 .feature、不跑 cucumber red→green）

## SSOT 三角

| 角 | SSOT 位置 | 用途 |
|---|---|---|
| 🎨 設計 | `<<UIUX_PEN_FILE>>` + `<<UIUX_PREVIEW_DIR>>` | <<FRAME_COUNT>> frames + N reusable components + design tokens |
| 📜 契約 | `<<API_SPEC_FILE>>` + `<<BACKEND_CONTRACTS_DIR>>` | <<OPERATION_COUNT>> operations（method × path × schema） |
| 🧪 行為樣本（**參考用，非 1:1**） | `<<BACKEND_FEATURE_FILES_GLOB>>` | feature files 內 Scenario / Example 作為 fixture 設計**靈感**（不要求逐 Example 對映） |
```

## §task-map

```markdown
## 任務地圖

| Task | Phase | Kind | Pencil Frame | Pencil Node | PNG | Route / Endpoint |
|------|-------|------|--------------|-------------|-----|------------------|
<<TASK_MAP_ROWS>>
```

每列格式：
```
| <<TASK_ID>> | <<PHASE>> | <<KIND>> | <<FRAME_NAME or "—">> | <<NODE_ID or "—">> | `<<PNG_PATH or "—">>` | `<<ROUTE_OR_ENDPOINT or "—">>` |
```

## §phase1-msw

```markdown
## Phase 1 — MSW API Layer

> 先做。pages 還不能碰，因為 page 要 import api client，api client 又依賴 handler / fixture / zod。

<<PHASE1_TASK_BODIES>>
```

每個 task body：
```markdown
## <<TASK_ID>> — <<TASK_NAME>>

**錨點**：
- 左：`<<LEFT_SKILL>>` → <<LEFT_ELEMENT>>
- 中：<<MIDDLE_DESCRIPTION>>
- 右：N/A（資料層 task）

**依賴**：<<DEPS or "無">>

**Action**：
<<ACTION_CHECKLIST>>

**Acceptance**：
<<ACCEPTANCE_CHECKLIST>>
```

## §phase2-pages

```markdown
## Phase 2 — Next.js Pages

> 在 Phase 1 全綠後啟動。每個 frame 一條，**boss 4 招（10–13）獨立不合併**。

<<PHASE2_TASK_BODIES>>
```

每個 page task body：
```markdown
## <<TASK_ID>> — Frame <<FRAME_NAME>>

**錨點**：
- 左：`/aibdd-auto-frontend-nextjs-pages` → <<LEFT_ELEMENT>>
- 中：<<MIDDLE_DESCRIPTION>>
- 右：`<<UIUX_PEN_FILE>>` frame `<<FRAME_NAME>>`（node `<<NODE_ID>>`）+ `<<PNG_PATH>>`

**依賴**：<<DEPS>>

**元件對映**（左=.pen reusable / 右=React）：
| .pen reusable | node ID | React 對應 |
|---|---|---|
<<COMPONENT_MAPPING_ROWS>>

**程式碼產出**：
<<CODE_CHECKLIST>>

**API / MSW 串接**：
<<API_INTEGRATION_LIST>>

**Acceptance**：
- [ ] 視覺：截圖比對 `<<PNG_PATH>>`，token / 排版 / glow 一致（差異 <5%）
- [ ] 行為：<<BEHAVIOR_DESCRIPTION>>
- [ ] 邊界：<<EDGE_CASE_DESCRIPTION>>
- [ ] 整合：<<INTEGRATION_VERIFICATION>>
```

## §phase3-gate

```markdown
## Phase 3 — Visual Parity Gate

> 全 16 frame 落地後最後一關。pixel diff 不過就回到對應 page task 修。

<<PHASE3_TASK_BODY>>
```

phase3 task body 樣板：
```markdown
## <<TASK_ID>> — Visual Parity Gate（全 frame）

**錨點**：
- 左：`/aibdd-auto-frontend-nextjs-pages` → 視覺一致性審查（不在 skill SOP 內，由本 task 額外要求）
- 中：N/A（純 visual gate）
- 右：`<<UIUX_PEN_FILE>>` 全 frame + `<<UIUX_PREVIEW_DIR>>/*.png`

**依賴**：T05 .. <<LAST_PAGE_TASK_ID>>

**Action**：
- [ ] 寫 `frontend/scripts/visual-check.md` 列出 16 frame ↔ Playwright route ↔ 比對 PNG 的清單
- [ ] 對每條 route 跑 Playwright `page.screenshot()` 存到 `frontend/dist-test/screenshots/`
- [ ] 跟 `<<UIUX_PREVIEW_DIR>>/*.png` 對應檔做 pixelmatch diff（或人工目測）

**Acceptance**：
- [ ] 16 個畫面像素差異 < 5%
- [ ] 色 token 沒漂、字體沒回退到系統字
- [ ] 任何 fail 的 frame 回該 page task 修，再跑一次本 task
```
