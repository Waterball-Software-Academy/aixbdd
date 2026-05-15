# Clarify Axes Catalog — UIUX 澄清軸題庫（component-first）

> 純 declarative 題庫。SKILL.md Phase 3 step 1.1 LOAD 本檔，依下列 9 軸生題。
> 每軸的「context 來源」欄指出該題該 attach 哪個 Phase 2 derive 出的結構，
> 讓 user 在回答前看到 derive 過的當前資訊。
>
> Phase 3 step 1.2 會把 context 注入到對應軸的題目體裡，再交給 /clarify-loop。
>
> ⚠️ v2 變動：本題庫對齊 [`state-derivation-rules.md`](state-derivation-rules.md) v2 的兩階段推導
> （component inventory + frame composition），不再以 frame-level state matrix 為主軸。

---

## §1 Style Direction（視覺方向）

**問**：這個 frontend boundary 想走哪個視覺方向？

**選項範圍**（user 可選一或自填，自填需給 1-3 個參考連結）：
- editorial / magazine
- neo-brutalism
- glassmorphism with real depth
- dark luxury / light luxury
- bento layout
- scrollytelling
- 3D integration
- Swiss / International
- retro-futurism
- cyberpunk arcade
- minimal Scandinavian

**context 來源**：無（純偏好）

**validator**：必須選或自填 1 個方向；不可留空

---

## §2 Design Tokens（調色 / 字體 / 間距 / 陰影）

**問**：core tokens 想怎麼定？

**子題**：
- **palette**：3-5 個 semantic colors（base / surface / text / accent / state-on）— 建議用 OKLCH，hex 為替代格式
- **typography**：display font + body font + mono font（標各自用途）
- **spacing scale**：是否用 modular scale（建議 1.25× ratio）+ base unit（建議 4px）
- **radius scale**：sharp（≤2px）/ medium（6-10px）/ pillow（≥16px）三段任選或自定
- **shadow philosophy**：flat / layered / soft / glow — 擇一

**context 來源**：§1 Style Direction 的選擇（不同 style 通常配不同 token 範圍）

**validator**：palette ≥ 3 colors；typography 至少有 body font；radius 與 shadow philosophy 必選

---

## §3 Component Inventory 元件盤點（主軸 — v2 升格）

**問**：以下 derive 出的元件清單與每個元件的 state matrix，是否需要拆分 / 合併 / 新增 / 修改？

**context 來源**：`$$component_inventory`（含每個 component 的 id / role / base_states / domain_states / used_by_frames / anchor candidates）+ `$$frame_composition`（讓 user 看到每個 component 被哪些 frame 引用）

**子題（per component candidate）**：
- **id / role 是否正確**（命名、語意 role）
- **base_states 是否完整**（idle / hover / focus / active / disabled / submitting / ...）
- **domain_states 是否完整**（rejected.* / error.* / empty.* / loading）
- **跨 frame 重用是否合理**（同 component 在多 frame → 文案 / 行為必須一致；否則應分裂）
- **是否要抽 shared atomic component**（如 Button base / Input base — 通常不要先抽，等 storybook 看真實重複再說）

**新增軸（v2 新加）**：
- **未被 component 覆蓋的 atomic rule**：系統列出沒對應到任何 component candidate 的 Rule，user 必須補一個 component 或標 `non-visual`（純規則，不可見）

**validator**：
- 每個 component 至少 1 個 success-path state（idle / populated / pristine 視 role 而定）
- 每條 .feature Rule 至少對應 1 個 component 或被標 `non-visual`

---

## §4 Component Interactions（per-component 狀態轉換動效）

**問**：以下 component 的狀態轉換點，動效 / 時長 / easing 想怎麼處理？

**context 來源**：`$$component_inventory[*]` 的 state matrix（每對相鄰 state 轉換 = 一個 interaction 候選）

**子題（per component × per state-transition）**：
- duration（建議擇一：150ms / 250ms / 400ms / custom）
- easing（建議擇一：ease-out-expo / ease-in-out / linear / custom）
- 是否 compositor-friendly（transform / opacity only）
- `prefers-reduced-motion: reduce` 時的降級行為（瞬時 / 單次閃光 / 維持顏色變化）

**v2 變動**：interaction 鎖在 component 層；同 component 跨 frame 共用同一組 interaction spec（不再 per-frame 重定）。

**validator**：每個 state 轉換點的 reduced-motion 行為**必須**描述；不可留空

---

## §5 Copy Decisions（文案決策 / anchor name 鎖定）— component-keyed

**問**：以下 anchor 候選名稱，最終 accessible name 要採哪個？

**context 來源**：`$$anchor_candidates`（從 atomic-rules 動詞抽出的候選，每個帶 `component_id` + role + name_candidates + source_rule_id）

**子題（per anchor，keyed by component_id）**：
- 從候選中擇一鎖定 accessible name
- 若候選都不滿意，自填新名稱（但**必須**包含 atomic-rules 的關鍵動詞之一，禁同義改寫）

**v2 變動**：anchor 跨 frame 重用時只回答一次；不再每個 frame 重複問。

**validator**：每個 `component_id` 必有最終 name；name 必須包含 source_rule_id 對應 Rule 中的動詞之一

---

## §6 Frame Composition / Layout Hints（新軸 — v2 取代舊版 frame state matrix）

**問**：以下 derive 出的 frame composition map，每個 frame 的 layout / canonical state combo 想怎麼定？

**context 來源**：`$$frame_composition`（每 frame 列出 uses_components + activity_node + feature_rules + 預設 layout_hint）

**子題（per frame）**：
- **layout pattern**：stack / sidebar+main / split / grid / dialog-over / wizard-steps
- **canonical state combo**：選一組 component state 作為「主畫面」展示（其它 state 透過 component-level Story 展示，不在 frame 圖內畫）
- **重要排版線索**：sticky header / sticky CTA / scroll region / split ratio
- **空 slot 處理**：哪些 component 在此 frame 預設 `hidden`（如 ErrorBanner）

**validator**：每 frame 必有 layout pattern + canonical state combo；canonical state 必須來自對應 component 的 state set

---

## §7 Breakpoints

**問**：要支援哪幾個 breakpoint？

**選項**：
- mobile-only（390）
- mobile + desktop（390 / 1440）— 預設
- responsive 全段（320 / 768 / 1024 / 1440 / 1920）
- mobile-first stack-down（自訂斷點）

**context 來源**：無

**validator**：≥ 1 個 breakpoint；若選自訂需給具體 px 值

---

## §8 Accessibility + Motion Budget

**問**：a11y 目標 + 動效預算？

**子題**：
- WCAG 等級（A / AA / AAA — 預設 AA）
- 鍵盤可達性最低範圍（happy path / 全流程）
- prefers-reduced-motion 行為（會與 §4 對齊）
- 對比度最低值（4.5:1 / 7:1）
- 焦點環色 + 寬度
- 動效預算：
  - **純功能型**：僅 hover / focus / transition
  - **中度**：加上 page transition + micro-interaction
  - **高度**：含 hero animation / scroll-driven motion

**validator**：必須選 WCAG 等級；對比度與焦點環必設；motion budget 必選

---

## §9 Brand References

**問**：有沒有 1-3 個參考設計（網址 / Pinterest / Dribbble / 截圖路徑），讓 Pencil 對齊風格？

**context 來源**：無

**validator**：optional；若 §1 選 "other" / 自填則此題 ≥ 1 必填

---

## §10 Resolved-answers Output Schema（clarify-loop 回填預期形狀）

clarify-loop resolve 完，`$$clarify_resolved` 應有以下 keys（缺值 → Phase 5 ASSERT 失敗）：

```yaml
clarify_resolved:
  style_direction: string
  required_qualities: [string]            # §1 衍生（user 從預設質感清單勾選 ≥6）
  tokens:
    colors: {base, surface, text, accent, state_on, ...}
    typography: {display, body, mono, scale}
    spacing: {base, scale}
    radius: {sharp, medium, pillow}
    shadow: {philosophy, tokens}
  components:                              # §3 回填後的 component_inventory
    - id: string
      role: string
      base_states: [string]
      domain_states: [{code, source}]
      used_by_frames: [string]
      variants: [string]                  # 若 user 補了 variant（如 "primary"/"ghost"）
      notes: string
  interactions:                            # §4 per component × per state-transition
    - component_id: string
      from_state: string
      to_state: string
      duration: string
      easing: string
      reduced_motion: string
  copy_decisions:                          # §5 component-keyed
    - component_id: string
      role: string
      name: string
      source_rule_id: string
  frame_layouts:                           # §6 per frame
    - frame_slug: string
      layout_pattern: enum{stack, sidebar-main, split, grid, dialog-over, wizard-steps}
      canonical_state_combo:
        - component_id: string
          state: string
      sticky_regions: [string]
      hidden_components: [string]
  breakpoints: [int]
  a11y: {wcag_level, contrast_min, keyboard_scope, focus_ring}
  motion_budget: enum{functional, medium, high}
  brand_references: [url|path]
```
