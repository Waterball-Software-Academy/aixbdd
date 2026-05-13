# Lite Prompt Sections

本檔定義 lite template section 的填值來源與驗收條件。Section 名稱維持 downstream-compatible，但內容刻意比 full discovery 少。

## §1 Section source map

| Template section / placeholder | 來源 binding | 備註 |
|---|---|---|
| `{{PROJECT-NAME}}` | `$$runtime_context.current_package_slug` | kebab-case |
| `{{LITE-SCOPE-SUMMARY}}` | `$$lite_scope` | 必須列 selected/excluded 原因 |
| `{{VISUAL-STYLE}}` | `$$clarify_resolved.style_direction` | lite axis §2 |
| `{{REQUIRED-QUALITIES}}` | `$$clarify_resolved.required_qualities` | 3+ 即可 |
| `{{TOKENS}}` | `$$clarify_resolved.tokens` | CSS vars |
| `{{BREAKPOINTS}}` | `$$clarify_resolved.breakpoints` | 1+ |
| `{{COMPONENT-CATALOG}}` | `$$component_inventory` ⊕ copy/layout notes | 每 component 只列 primary state table |
| `{{FRAME-COMPOSITION-TABLE}}` | `$$frame_composition` ⊕ `$$clarify_resolved.frame_layouts` | selected frames only |
| `{{ANCHOR-NAME-TABLE}}` | `$$clarify_resolved.copy_decisions` | lite scope interactive components only |
| `{{DELIVERABLES-ORDER}}` | selected frames topo order | 不列 excluded |
| `{{ACCEPTANCE-CRITERIA-EXTRA}}` | `$$clarify_resolved.a11y` | happy-path a11y minimum |
| `{{CONSTRAINTS-EXTRA}}` | `$$lite_scope.excluded` | 明確說 excluded 不畫 |

## §2 Missing value handling

- required lite axes 缺值 → render `<!-- TODO: clarify-loop 未回收 <axis_name> -->` 並 fail Phase 5 ASSERT。
- 不允許 placeholder `TBD` / `N/A` 進最終 output。

## §3 Lite ASSERT conditions

1. `MODE: lite-happy-path` 必須出現在 prompt 前段。
2. `## COMPONENT CATALOG` 必須至少包含一個 `### ComponentId` 與 primary state table。
3. `## FRAME COMPOSITION TABLE` 必須至少包含一列 markdown table。
4. `## ANCHOR NAME TABLE` 必須至少包含一列 markdown table；若 scope 沒有 interactive component，必須明確列 `No interactive anchors in lite scope` 並附原因。
5. `COMPONENT CATALOG` 中每個 component 最多列一個 state，除非該額外 state 的 source step 原文在 `LITE SCOPE` 中出現。
6. 不得因 activity graph 或 full component base state 自動加入 `hover`、`active`、`disabled`、`rejected.*`、`error.*`、`loading`。

## §4 Downstream compatibility

`/aibdd-uiux-draw` 只依 prompt 中的 table 畫圖；lite prompt 仍提供 full skill 同名三 section，因此下游 parser 不需要改路徑。差異在於 table rows 較少、state list 只有 primary state。
