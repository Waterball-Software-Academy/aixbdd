# Lite Clarify Axes Catalog

Lite 版澄清題只補足能畫 happy path 的必要資訊。禁止把 full `/aibdd-uiux-design` 的 9 軸完整搬回來。

## §1 Scope confirmation

**問**：以下 selected frames 是否就是這次要畫的 happy path / feature-mentioned 畫面？

**context 來源**：`$$lite_scope.selected_frames` + `$$lite_scope.excluded`

**validator**：user 必須確認 selected frames；若新增 frame，必須指出對應 `.feature` scenario/step，否則不可新增。

## §2 Visual direction + minimal tokens

**問**：happy path 草圖要走哪個視覺方向？核心 tokens 如何定？

**子題**：style direction、3-5 semantic colors、display/body font、spacing base、radius、shadow philosophy。

**validator**：style direction 不可空；palette ≥ 3；body font 必填。

## §3 Frame layout hints

**問**：每個 selected frame 的 layout pattern 是什麼？

**context 來源**：`$$frame_composition`

**選項**：single-column、two-column、sidebar-main、card-stack、dashboard-grid、dialog-over、wizard-step。

**validator**：每個 selected frame 必有 layout pattern；不可新增 non-feature frame。

## §4 Anchor names / copy decisions

**問**：lite scope 內的 interactive components 要採用哪些 accessible names？

**context 來源**：`$$anchor_candidates`

**validator**：每個互動 component 必有 `role + accessible name`；name 必須包含 source step/Rule 的關鍵動詞之一。

## §5 Breakpoints + accessibility minimum

**問**：這份 happy path brief 要畫哪些 breakpoint？最低 a11y 目標？

**建議預設**：mobile + desktop（390 / 1440）、WCAG AA、keyboard scope = happy-path、focus ring 2px。

**validator**：breakpoints ≥ 1；WCAG level、contrast min、focus ring 必填。

## §6 Resolved output schema

```yaml
clarify_resolved:
  scope_confirmation:
    selected_frames_confirmed: true
    adjustments: []
  style_direction: string
  required_qualities: [string]
  tokens:
    colors: {base, surface, text, accent, state_on, ...}
    typography: {display, body, mono, scale}
    spacing: {base, scale}
    radius: {sharp, medium, pillow}
    shadow: {philosophy, tokens}
  frame_layouts:
    - frame_slug: string
      layout_pattern: enum{single-column,two-column,sidebar-main,card-stack,dashboard-grid,dialog-over,wizard-step}
      notes: string
  copy_decisions:
    - component_id: string
      role: string
      name: string
      source_rule_id: string
  breakpoints: [int]
  a11y: {wcag_level, contrast_min, keyboard_scope, focus_ring}
  motion_budget: enum{functional, minimal}
  brand_references: [url|path]
```
