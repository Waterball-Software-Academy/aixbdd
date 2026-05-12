# MCP Binding Rules — brief section ↔ Pencil MCP tool 對照

> 純 declarative 對照。SKILL.md Phase 2-5 LOAD 本檔，逐 section 取對應 PARSE 規則與 MCP 工具呼叫骨架。
>
> Pencil MCP 可用工具：`get_editor_state` / `open_document` / `get_guidelines` / `batch_get` / `batch_design` / `snapshot_layout` / `get_screenshot` / `get_variables` / `set_variables` / `find_empty_space_on_canvas` / `search_all_unique_properties` / `replace_all_matching_properties` / `export_nodes`。

---

## §1 DESIGN TOKENS section → `set_variables`

`uiux-prompt.md` 開頭的 CSS-var 區塊 + `style-profile.yml` 一起 PARSE 成 token map，灌進 document variables。

**PARSE 規則**：
- 從 `style-profile.yml` 抽 `tokens.colors` / `tokens.typography` / `tokens.spacing` / `tokens.radius` / `tokens.shadow` / `motion`
- 命名統一：把 yml key 轉成 Pencil variable 命名規約：`color/<semantic>`、`type/<role>`、`space/<scale>`、`radius/<size>`、`shadow/<level>`、`motion/<token>`

**MCP 呼叫骨架**：

```yaml
tool: pencil::set_variables
args:
  variables:
    - name: "color/base"
      value: "<oklch_or_hex_from_profile>"
    - name: "color/surface"
      value: ...
    - name: "type/display"
      value:
        family: "<font>"
        weight: <number>
    - name: "space/base"
      value: "4px"
    - name: "radius/medium"
      value: "8px"
    # ...
```

不變式：
- 同一 token 在 component scene / frame scene 內必須引用 variable，**不可**內聯硬編碼色號
- 若 brief 中某 token 未填值（含 `<!-- TODO: ... -->`）→ Phase 2 ASSERT 失敗（refuse to draw with missing token）

---

## §2 COMPONENT CATALOG section → `batch_design` per component scene

`uiux-prompt.md` 內每個 `### \`ComponentId\` (role)` sub-section 為一個 component spec。

**PARSE 規則**：
- 每個 `###` heading 切一個 component
- heading 內括號取 role
- `Used by frames:` 取 used_by_frames（純資訊；本 skill 不用展開到 frame）
- `Anchor name:` 取 anchor name（與 ANCHOR NAME TABLE 對齊）
- state matrix table 抽成 states 陣列：每列 `{code, source, visual_hint}`

**MCP 呼叫骨架**（per component）：

```yaml
tool: pencil::batch_design
args:
  scene_name: "Component: <ComponentId>"
  canvas_spot: <from find_empty_space_on_canvas>
  ops:
    # 一個 component scene 內橫向擺 N 個 state variant；每個 variant 是一個獨立節點群組
    - kind: "create_group"
      label: "<state_code>"
      position: {x: <auto_layout>, y: 0}
      children:
        - kind: "<role-shape>"     # button → rectangle + text；textbox → input frame；list → stack
          style:
            background: "var(color/<inferred_from_state>)"
            border: ...
            radius: "var(radius/medium)"
            shadow: "var(shadow/<inferred_from_state>)"
          text:
            value: "<anchor_name>"  # 動詞鎖定來源；非互動 component（list/status）可省
            font: "var(type/body)"
        - kind: "label"
          value: "<state_code>"
          position: {y: below}
          font: "var(type/mono)"
    # 每個 state variant 一個 group，最終橫向排成一列
```

State → visual hint 對應規則（hint 沒填時的預設）：

| state code | 視覺預設 |
|---|---|
| `idle` / `populated` / `pristine` | accent / surface base + body text |
| `hover` | base color + lift（shadow up one level） |
| `focus` | focus ring（accent, 2px outline） |
| `active` / `pressed` | scale 0.98 + shadow down |
| `disabled` | surface 60% + text-on-disabled |
| `submitting` / `loading` | spinner overlay + label dim |
| `success` | state-on-success color tint |
| `rejected.*` | state-on-error tint + inline error message slot |
| `error.*` | state-on-error tint + retry / fallback slot |
| `empty` / `empty.*` | placeholder illustration slot + empty-state copy |

不變式：
- accessible name 一字不差用 `$$anchor_table[component_id].accessible_name`；不允許自由改寫
- state code 一字不差用 `$$component_specs[*].states[*].code`；不允許自由命名
- 每個 component 至少 1 個 success-path state（`idle` / `populated` / `pristine` 其一）

---

## §3 FRAME COMPOSITION TABLE section → `batch_design` per frame scene

`uiux-prompt.md` FRAME COMPOSITION TABLE 每列為一個 frame spec。

**PARSE 規則**：
- 從 markdown table 抽欄位：`Frame slug` / `Activity node` / `Feature Rule` / `Layout` / `Uses` / `Sticky` / `Hidden slots`
- `Uses` 欄解析成 `[{component_id, canonical_state}]`，格式為 `ComponentId(state_code)`
- `Hidden slots` 解析成 `component_id` 清單

**MCP 呼叫骨架**（per frame）：

```yaml
tool: pencil::batch_design
args:
  scene_name: "Frame: <frame_slug>"
  canvas_spot: <from find_empty_space_on_canvas>
  ops:
    - kind: "create_frame"
      label: "<frame_slug>"
      layout: "<layout_pattern>"    # stack / sidebar-main / split / grid / dialog-over / wizard-steps
      children:
        # 依 layout_pattern 派下 children 排版
        # 每個 used component 用 canonical_state variant；不展開其他 state
        - kind: "component_instance"
          component_ref: "<ComponentId>"
          state: "<canonical_state>"
          slot: "<layout_slot_name>"
        # ...
        # hidden slots：用淺灰邊框佔位 + 標籤 "(hidden by default)"
        - kind: "placeholder"
          label: "<HiddenComponentId> (hidden by default)"
          style:
            border: "1px dashed var(color/surface)"
```

Layout pattern → 對應 layout 提示：

| layout_pattern | 提示 |
|---|---|
| `stack` | 單欄垂直堆疊；mobile-friendly |
| `sidebar-main` | 左 sidebar + 右主區（desktop） / 上下堆疊（mobile） |
| `split` | 左右 50/50（或 user 指定比例） |
| `grid` | 多欄等寬卡片 |
| `dialog-over` | dim overlay + 中央 dialog |
| `wizard-steps` | 上方 stepper + 下方 step content |

不變式：
- 每個 used component 必須對應到 Phase 4 已建立的 component scene（透過 `component_ref`）；不可 inline 重畫
- canonical_state 必須在該 component 的 state set 內
- hidden slot 必須以 placeholder 形式存在；不可省略（讓設計師看見 slot 預留位置）

---

## §4 ANCHOR NAME TABLE section → 文字節點驗證

**PARSE 規則**：
- 從 markdown table 抽 `Component` / `role` / `accessible name` / `source rule` 四欄
- 與 component_specs 內 `anchor_name` 對齊；若兩處不一致 → ASSERT 失敗（caller 上游 brief 內部不一致）

**MCP 用途**：
- Phase 4 batch_design 時的 button / link / textbox 文字節點 value 必須等於本表的 accessible name
- Phase 6 self-check 時用 `pencil::search_all_unique_properties`（搜 text 屬性）撈出所有文字節點，跟本表對 diff；不在 anchor 集合內的可疑文字 → `wrong_label` issue
- 修補時用 `pencil::replace_all_matching_properties` 把錯誤文字節點替換為正確 accessible name

---

## §5 跨工具不變式

- 任一 batch_design 後不立即 export；export 集中在 Phase 7
- snapshot_layout 用於 self-check 階段唯讀；不在這之外呼叫
- set_variables 只在 Phase 3 一次性 set；Phase 6 修補時可 re-set 個別 token（不重 set 全表）
- 失敗 → MARK 不嘗試自修的 issue 為 `other`，最終 EMIT 給 user 看
