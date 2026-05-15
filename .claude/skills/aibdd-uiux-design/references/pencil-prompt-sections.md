# Pencil Prompt Sections — uiux-prompt.template.md 填值來源表（v2 component-first）

> 純 declarative 對照表。SKILL.md Phase 5 step 1.2 RENDER 時 LOAD 本檔，逐 section 取對應來源填值。
>
> ⚠️ v2 變動：取消舊版 frame-level STATE MATRIX；改成兩段必達 section
> （`COMPONENT CATALOG` + `FRAME COMPOSITION TABLE`），對應 [`state-derivation-rules.md`](state-derivation-rules.md) v2。

---

## §1 Section ↔ binding 來源對照

| Template section / placeholder | 來源 binding | 備註 |
|---|---|---|
| `{{PROJECT-NAME}}` | `$$runtime_context.current_package_slug` | kebab-case |
| `{{VISUAL-STYLE}}` | `$$clarify_resolved.style_direction` | clarify-axes §1 |
| `{{REQUIRED-QUALITIES}}` | `$$clarify_resolved.required_qualities` | clarify-axes §1（≥6） |
| `{{TOKENS}}` | `$$clarify_resolved.tokens`（render 成 CSS-var 區塊） | clarify-axes §2 |
| `{{BREAKPOINTS}}` | `$$clarify_resolved.breakpoints` | clarify-axes §7 |
| `{{COMPONENT-CATALOG}}` | `$$component_inventory` ⊕ `$$clarify_resolved.components` | **§3 必達**，per component sub-section |
| `{{FRAME-COMPOSITION-TABLE}}` | `$$frame_composition` ⊕ `$$clarify_resolved.frame_layouts` | **§3 必達** |
| `{{ANCHOR-NAME-TABLE}}` | `$$clarify_resolved.copy_decisions`（component-keyed） | **§3 必達** |
| `{{INTERACTION-SPEC}}` | `$$clarify_resolved.interactions`（component × state-transition） | clarify-axes §4 |
| `{{DELIVERABLES-ORDER}}` | `$$frame_composition` topo-sorted by activity flow | activity flow 拓樸序 |
| `{{ACCEPTANCE-CRITERIA-EXTRA}}` | `$$clarify_resolved.a11y` ⊕ `$$clarify_resolved.breakpoints` | clarify-axes §7 §8 |
| `{{CONSTRAINTS-EXTRA}}` | atomic-rules 動詞清單（從 `$$discovery_bundle.features` Rule 抽） | 強制設計師用領域動詞 |

> 舊 placeholder `{{SCREENS-TABLE}}` / `{{STATE-MATRIX-TABLE}}` / `{{COMPONENT-CONTRACT}}` 在 v2 廢除；
> 由 `{{COMPONENT-CATALOG}}` + `{{FRAME-COMPOSITION-TABLE}}` 取代。

---

## §2 缺值處理規則（fail-stop，非 silent default）

- 若 `$$clarify_resolved.<axis>` 缺值 → 對應 section 必須 render `<!-- TODO: clarify-loop 未回收 <axis_name> -->`，並 fail Phase 5 step 3 ASSERT
- 不允許 silent default
- 不允許 placeholder 字串如 `TBD` / `N/A` 進最終 output

---

## §3 必達 section（render 後 ASSERT non-empty）

以下三個 section 在 Phase 5 step 3 必須 ASSERT 非空（缺漏 = 下游合約斷裂）；ASSERT 須在 WRITE 之前完成，避免半成品殘留：

1. **COMPONENT CATALOG**
   - 缺漏 = 設計師會漏畫元件狀態 = 下游 form-story 補不到該 component 的 Story export
   - ASSERT regex：`## COMPONENT CATALOG[\s\S]*?### [A-Z][\w]+[\s\S]*?\|`（至少一個 `###` component sub-section + 至少一張 table）
   - 進一步檢查：每個 component sub-section 都必須有 state matrix table（含 `success` / `idle` / `populated` / `pristine` 其一）

2. **FRAME COMPOSITION TABLE**
   - 缺漏 = frame 與 component 對應斷裂；設計師不知道要組成哪些頁面
   - ASSERT regex：`## FRAME COMPOSITION[\s\S]*?\|[\s\S]*?\|[\s\S]*?\|`（至少一列 markdown table）
   - 進一步檢查：每列的 `uses` 欄位必須引用 COMPONENT CATALOG 中存在的 component id

3. **ANCHOR NAME TABLE**
   - 缺漏 = 設計 ↔ Story ↔ step 合約斷裂
   - ASSERT regex：`## ANCHOR NAME TABLE[\s\S]*?\|[\s\S]*?\|[\s\S]*?\|`
   - 進一步檢查：每列的 `component` 欄位必須引用 COMPONENT CATALOG 中存在的 component id

ASSERT 失敗 → Phase 5 step 3.3 EMIT 失敗訊息並 GOTO #5.1.1 重 render；因為 ASSERT 在 WRITE 之前，不需 rollback 任何已落地檔。

---

## §4 Render dependency declarations（依賴宣告，非流程）

Sections 分兩類，render 時必須遵守依賴關係（具體執行步驟在 SKILL.md §2 SOP）：

- **Mechanical-derived sections**（依賴 `$$component_inventory` / `$$frame_composition` / `$$anchor_candidates`）：
  `PROJECT-NAME` / `COMPONENT-CATALOG`（骨架） / `FRAME-COMPOSITION-TABLE`（骨架） / `DELIVERABLES-ORDER`
- **Clarify-resolved sections**（依賴 `$$clarify_resolved.<axis>`）：
  `VISUAL-STYLE` / `REQUIRED-QUALITIES` / `TOKENS` / `BREAKPOINTS` / `INTERACTION-SPEC` / `ANCHOR-NAME-TABLE` / `ACCEPTANCE-CRITERIA-EXTRA` / `CONSTRAINTS-EXTRA`
- **Hybrid sections**（兩者 merge）：
  `COMPONENT-CATALOG`（mechanical 骨架 ⊕ clarify 補 variants / notes）
  `FRAME-COMPOSITION-TABLE`（mechanical 骨架 ⊕ clarify 補 layout / canonical state combo / hidden / sticky）

不變式：
- §3 必達 section 的 ASSERT 必於 WRITE 落檔之前完成
- Mechanical sections 與 clarify-resolved sections 互不依賴；可獨立 render
- 任一 section 缺值 → 對應 placeholder 替換為 `<!-- TODO: clarify-loop 未回收 X -->` 並 fail Phase 5 ASSERT（§2）
- COMPONENT CATALOG 內每個 component 的 state matrix 必須與 ANCHOR NAME TABLE 中該 component_id 的列對齊

---

## §5 跨 boundary 注意事項

本 skill 只負責 frontend boundary 的 uiux-prompt。若有多 frontend boundary（罕見，目前 kickoff 限制單一 TLB），需各自跑一次 `/aibdd-uiux-design`，產 boundary-aware 路徑：

- `${SPECS_DIR}/${current_package_slug}/design/uiux-prompt.md`
- `${SPECS_DIR}/${current_package_slug}/design/style-profile.yml`

當前版本（v2）不支援多 frontend 並行 — 由 kickoff 規則保證。
