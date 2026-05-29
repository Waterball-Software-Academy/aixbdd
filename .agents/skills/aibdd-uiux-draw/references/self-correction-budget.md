# Self-correction Budget — 自檢 / 自修 loop 規約

> SKILL.md Phase 6 LOAD 本檔。定義 CRITIQUE rubric、defect_kind → 修補手段對應、loop budget。

---

## §1 CRITIQUE rubric — defect 分類

對 `snapshot_layout` + `get_screenshot` 結果做 grading，輸出 issue 陣列。

每個 issue schema：

```yaml
issue:
  scope: enum{component, frame}
  target_id: string             # component_id 或 frame_slug
  defect_kind: enum{missing_state, wrong_label, wrong_layout, wrong_color, other}
  hint: string                  # 自然語描述，給 self-correct 階段參考
  evidence_ref: string          # 截圖 ID / scene_id / snapshot path
```

**Defect 分類規約**：

| defect_kind | 觸發條件 | 嚴重度 |
|---|---|---|
| `missing_state` | component scene 內缺少 brief catalog 列出的某個 state variant | high — must fix |
| `wrong_label` | 文字節點 value ∉ ANCHOR NAME TABLE 對應的 accessible_name；或對應 component 缺 anchor | high — must fix |
| `wrong_layout` | frame scene 使用的 component 缺漏 / 排錯位置 / canonical_state 不在該 component state set | medium |
| `wrong_color` | 節點 fill / border 內聯硬編碼色號（未引用 var(color/*)）| medium |
| `other` | 其他 grading 不確定的偏差（如風格主觀差異） | low — MARK 不自修 |

**Grading invariants**：
- 不評論「美感」；只看 brief 規約是否落實
- 不評論「字體 / 間距是否符合視覺方向」（屬上游 brief 範疇）
- snapshot 缺漏（找不到 scene）視同 `missing_state` 或 `wrong_layout`，依 scope 分

---

## §2 Defect → 修補手段對應

### §2.1 `missing_state` → `batch_design` 補 variant

```yaml
tool: pencil::batch_design
args:
  scene_name: "Component: <component_id>"   # 既有 scene
  mode: "append"                              # 不覆蓋現有 variant
  ops:
    - kind: "create_group"
      label: "<missing_state_code>"
      # ...
      # 依 mcp-binding-rules.md §2 state → visual hint 預設套
```

### §2.2 `wrong_label` → `replace_all_matching_properties` 改文字

```yaml
tool: pencil::replace_all_matching_properties
args:
  match:
    property: "text"
    value: "<current_wrong_value>"
    scope_scene: "Component: <component_id>"
  replace:
    property: "text"
    value: "<correct_accessible_name from anchor_table>"
```

不變式：以 anchor_table 為 SSOT；component scene 與 frame composition scene 中所有引用同 component 的文字節點都同步更新。

### §2.3 `wrong_layout` → `batch_design` 重畫 frame scene

不單獨 patch；對整個 frame scene 重 batch_design layout ops（per mcp-binding-rules.md §3）。修補後該 frame 應從 snapshot 重新出現。

### §2.4 `wrong_color` → `replace_all_matching_properties` 改引用

```yaml
tool: pencil::replace_all_matching_properties
args:
  match:
    property: "fill"
    value: "<hardcoded_hex_or_oklch>"
    scope_scene: "Component: <component_id>"
  replace:
    property: "fill"
    value: "var(color/<semantic>)"   # 從 mcp-binding-rules.md §1 對應 semantic name
```

### §2.5 `other` → MARK 不自修

不嘗試自動修；最終 Phase 8 step 2 EMIT 給 user 看，由人工 / 下一輪 brief 修正。

---

## §3 Loop budget

- **總修補 loop 上限**：3 輪（per SKILL.md Phase 6 step 4.2 LOOP `$loop_idx < 3`）
- **每輪上限**：把當前 `$issues` 中所有 `missing_state` / `wrong_label` / `wrong_layout` / `wrong_color` 全部嘗試一次；不分批
- **退出條件**：
  - `length($issues) == 0` → `$$health = "clean"` → RETURN
  - 用光 3 輪仍有 issue → `$$health = "degraded"`，殘留 issue 透過 Phase 8 step 2 EMIT 給 user
- **不允許**：
  - 修補時刪除其他 component scene
  - 修補時改 anchor_table 或 component_specs（那是 brief 的職責；本 skill 唯讀消費）
  - 在 budget 內無限重跑 CRITIQUE 直到「自評」OK（避免幻覺收斂）

---

## §4 Loop oscillation 偵測

連續兩輪間 `$issues` 完全相同 → 視為震盪；不浪費下一輪 budget：

- 立刻 break loop
- `$$health = "degraded"`
- EMIT 「修補 loop 偵測到震盪（連續兩輪 issue 集合相同）；停止自修，請人工處理」

實作：每輪結束前 SUMMARIZE `$issues` 為 fingerprint（target_id + defect_kind 集合）；與上輪比對。

---

## §5 報告契約

Phase 8 EMIT 時的 `health` 對應：

| health | EMIT 內容 |
|---|---|
| `clean` | 「`.pen` 落地完成，所有 component / frame scene 通過自檢」 |
| `degraded` | 「`.pen` 落地但仍有 N 項待修：`<issue summary>`；可重跑 `/aibdd-uiux-draw` 或手動編輯 `.pen`」 |

不論 `clean` 或 `degraded`，下一步建議都是跑 `/aibdd-plan`（plan 階段不要求 `.pen` 完美，只要 component scene 與 anchor name 對齊即可萃取 I4 anchor）。
