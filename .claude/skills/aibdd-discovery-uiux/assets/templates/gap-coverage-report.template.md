# Discovery-UIUX Sourcing Report — {{ plan_package_slug }}

<!-- INSTRUCT: 此 template 由 SKILL.md Phase 2 §3 / §5 / Phase 3 §4 / Phase 6 §1 寫入；draft 與 final 兩階段共用同一模板，但 `## Open Classification Questions` 章節在 final 階段必須清空、改寫成 `## Resolved Classification Decisions`。 -->

> Plan package: `${PLAN_REPORTS_DIR}` 對應的 plan package
> Target frontend boundary: `{{ tlb_id }}`（role={{ tlb_role }}）
> Sibling backend boundary: `{{ uiux_backend_boundary_id }}`

---

## 1. BE Truth Pointer

<!-- INSTRUCT: 列出本輪 sourcing 讀的 BE artifact paths（features / activities / contracts）；不複製內容，只 pointer。 -->

- BE features: `{{ be_specs_dir }}/packages/**/*.feature` — N={{ be_features_count }}
- BE activities: `{{ be_specs_dir }}/packages/**/activities/*.activity` — N={{ be_activities_count }}
- BE contracts: `{{ be_specs_dir }}/contracts/**/*.{yml,yaml}` — N={{ be_contracts_count }}

---

## 2. Operation Inventory

<!-- INSTRUCT: 每筆 BE operation 一列；source 為 openapi-endpoint / activity-action / feature-rule 之一。 -->

| op_id | source | verb | object | actors | uat_flow |
|---|---|---|---|---|---|
| `{{ op_id }}` | {{ source }} | {{ verb }} | {{ object }} | {{ actors }} | {{ uat_flow }} |

---

## 3. Classification

<!-- INSTRUCT: classification 三值之一：has-ui / no-ui / ambiguous（ambiguous 在 Open Classification Questions 章節提問）。 -->

| op_id | classification | reasoning（引用 be-to-fe-mapping.md §1 訊號） |
|---|---|---|
| `{{ op_id }}` | {{ classification }} | {{ reasoning }} |

---

## 4. Open Classification Questions

<!-- INSTRUCT: 僅 draft 階段使用；final 階段必須清空，改寫為 `## Resolved Classification Decisions`。每題含 id / concern / options / recommendation。 -->

- **{{ q_id }}** — {{ concern }}
  - options: {{ options }}
  - recommendation: {{ recommendation }}（{{ rationale }}）

---

## 5. Resolved Classification Decisions

<!-- INSTRUCT: 僅 final 階段使用；每題答案 + reasoning。 -->

- **{{ q_id }}** — answer: {{ answer }}
  - reasoning: {{ reasoning }}

---

## 6. GAP — no-ui operations

<!-- INSTRUCT: 每筆 no-ui operation 必填 op_id / source / reasoning / revisit_trigger 四欄；參考 be-to-fe-mapping.md §4。 -->

| op_id | source | reasoning | revisit_trigger |
|---|---|---|---|
| `{{ op_id }}` | {{ source }} | {{ reasoning }} | {{ revisit_trigger }} |

---

## 7. Coverage Matrix（only for has-ui ops）

<!-- INSTRUCT: 每個 has-ui op 一列；維度標 `✅ N rules` / `❌ MISSING` / `➖ 不適用`。參考 userflow-rule-coverage.md §3。 -->

| op_id | happy | error | state-transition | a11y | cross-actor |
|---|---|---|---|---|---|
| `{{ op_id }}` | {{ happy }} | {{ error }} | {{ state_transition }} | {{ a11y }} | {{ cross_actor }} |

---

## 8. Coverage 統計

<!-- INSTRUCT: 整體統計；參考 userflow-rule-coverage.md §4。 -->

- `total_has_ui_ops`: {{ total_has_ui_ops }}
- `total_no_ui_ops`: {{ total_no_ui_ops }}
- `rules_total`: {{ rules_total }}
- `rules_by_verification_mode`:
  - `locator`: {{ rules_locator }}
  - `visual-state`: {{ rules_visual_state }}
  - `route`: {{ rules_route }}
  - `api-binding`: {{ rules_api_binding }}
- `coverage_gap_ops`: {{ coverage_gap_ops_list }}
