---
rp_type: reasoning_phase
id: aibdd-plan.07-component-design-merge
context: aibdd-plan
slot: "07"
name: Component Design Merge
variant: none
trigger_condition: boundary_profile.component_contract_specifier.skill non-empty
consumes:
  - name: BoundaryDelta
    kind: derived_axis
    source: upstream_rp
    upstream_rp: aibdd-plan.02-technical-boundary-dispatch
    required: true
  - name: BehaviorTruthAxis
    kind: required_axis
    source: filesystem
    required: true
  - name: DesignAdapterAxis
    kind: required_axis
    source: skill_delegate
    delegate: aibdd-pen-to-storybook
    required: false
  - name: UixPromptAxis
    kind: required_axis
    source: filesystem
    required: false
produces:
  - name: ComponentDesignMergeModel
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-plan.06-handoff-graph
---

# Component Design Merge

把 `BoundaryDelta.components` 初稿（reasoning/02 從 features/activities 推導）與設計來源（pen adapter + uiux-prompt）合併，
產出 enriched `boundary_delta.components`，包含 form-story-spec 寫雙產出（component .tsx + story .stories.tsx）所需的全部欄位：
`identifier` / `title` / `props[]` / `render_hints` / `stories[]`。

只在 `boundary_profile.component_contract_specifier.skill` 非空時觸發；後端 boundary 不跑此 RP。

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: BoundaryDelta
    source:
      kind: upstream_rp
      upstream_rp: aibdd-plan.02-technical-boundary-dispatch
    granularity: component candidate（initial draft from features × activities）
    required_fields:
      - identifier         # PascalCase
      - source_rule_ids    # 來自哪些 atomic rules
    optional_fields:
      - notes
    completeness_check:
      rule: every component candidate has at least one source_rule_id
      on_missing: STOP

  - name: BehaviorTruthAxis
    source:
      kind: filesystem
      path: ${TRUTH_FUNCTION_PACKAGE}/activities and ${TRUTH_FUNCTION_PACKAGE}/features
    granularity: activity DECISION branch + feature Rule
    required_fields:
      - rule_id
      - operation_trigger
      - consequence
    optional_fields:
      - decision_branches  # 從 activity DECISION 抽出的 state hints
    completeness_check:
      rule: every component candidate maps to at least one Rule + (optional) DECISION branch
      on_missing: WARN（不 STOP；no DECISION 表示該 component 沒有變體 state）

  - name: DesignAdapterAxis
    source:
      kind: skill_delegate
      delegate: aibdd-pen-to-storybook
      payload: { pen_path: ${CURRENT_PLAN_PACKAGE}/design.pen, screen_id: null }
    granularity: design adapter return shape（component_table + tokens）
    required_fields:
      - component_table.rows    # [{ Component, "Source nodes", "Detected props", Stories }]
      - tokens                   # [{ name, namespace, value }]
    optional_fields: []
    completeness_check:
      rule: pen_path exists at ${CURRENT_PLAN_PACKAGE}/design.pen
      on_missing: SKIP（design_adapter = empty bundle；走純 caller-reasoning 流程）

  - name: UixPromptAxis
    source:
      kind: filesystem
      path: ${CURRENT_PLAN_PACKAGE}/design/uiux-prompt.md
    granularity: component catalog（含 Used by frames + source rule + state matrix）
    required_fields:
      - COMPONENT CATALOG section
      - FRAME COMPOSITION TABLE section
      - ANCHOR NAME TABLE section
    optional_fields: []
    completeness_check:
      rule: file exists
      on_missing: SKIP（uiux_prompt = empty；走純 caller-reasoning + adapter 流程）
```

### 1.2 Search SOP

1. `$boundary_delta_components` = READ BoundaryDelta from upstream RP02
2. `$activities` = READ BehaviorTruthAxis activity source
3. `$features` = READ BehaviorTruthAxis feature source
4. `$design_pen_path` = COMPUTE `${CURRENT_PLAN_PACKAGE}/design.pen`
5. BRANCH path_exists(`$design_pen_path`)
   true:  `$design_adapter` = DELEGATE `/aibdd-pen-to-storybook` with `{ pen_path: $design_pen_path }`
   false: `$design_adapter` = COMPUTE `{ component_table: { rows: [] }, tokens: [] }`
6. `$uiux_prompt_path` = COMPUTE `${CURRENT_PLAN_PACKAGE}/design/uiux-prompt.md`
7. BRANCH path_exists(`$uiux_prompt_path`)
   true:  `$uiux_prompt` = READ `$uiux_prompt_path`
   false: `$uiux_prompt` = COMPUTE empty
8. ASSERT `$boundary_delta_components` non-empty

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: ComponentDesignMergeModel
  element_rules:
    element_vs_field:
      element: enriched component for form-story-spec consumption
      field: implementation hint or accessible-name binding under a component
  elements:
    EnrichedComponent:
      role: form-story-spec ready component reasoning bundle
      fields:
        identifier: string                 # PascalCase；同 BoundaryDelta candidate
        title: string                       # Storybook sidebar 路徑，e.g. "Components/RoomCodeInput"
        tags: list[string]                  # default ["autodocs"]
        parameters: object                  # optional Storybook meta parameters
        argTypes: object                    # optional Storybook control types
        shared_args: object                 # optional meta-level shared args
        props: list[PropSpec]               # TypeScript Props interface 來源
        render_hints: RenderHints           # JSX 結構與 Tailwind class
        stories: list[StorySpec]            # 各 state variant
        source_rule_ids: list[string]       # 來自哪些 atomic rules（traceability）
        source_decision_branches: list[string]  # 來自哪些 activity DECISION branches（state derivation）
        design_warnings: list[string]       # 三方來源不一致警示（不 block）

    PropSpec:
      role: TypeScript Props field declaration
      fields:
        name: camelCase
        type: TypeScript type literal       # e.g. "string" / "(value: string) => void"
        required: boolean
        default: any                        # optional；JSON-serialisable

    RenderHints:
      role: form-story-spec Phase 2A JSX render directives
      fields:
        root_element: string                # "div" / "button" / "input" / "label" / ...
        children_layout: enum               # "leaf" / "text" / "labeled-input" / "button" / "container"
        base_class: string                  # 預先解析的 Tailwind 4 class string
        accessible_name_prop: string        # children_layout=labeled-input/button 時必填
        button_type: string                 # children_layout=button 時 optional

    StorySpec:
      role: per-state Story export reasoning（form-story-spec Phase 2B 消費）
      fields:
        export_name: PascalCase
        role: ARIA role
        accessible_name: string             # I4 hard gate；必須 == accessible_name_arg.value
        accessible_name_arg:
          field: string                     # ∈ EnrichedComponent.props[*].name
          value: string                     # == accessible_name
        args: object                        # story-specific overrides
        has_action_args: boolean
        has_play: boolean
        play_steps: list                    # has_play=true 時必填
        source_rule_id: string              # state 來源規則
        source_decision_branch: string      # state 來源活動分支
```

## 3. Reasoning SOP

> 三來源（features/activities × design.pen × uiux-prompt）以**caller reasoning（features+activities）為 authoritative**，
> design 來源做**enrichment**（補 props type / Tailwind class / structure pattern）與**cross-validation warn**（state coverage / accessible name 一致性）。

### 3.1 Per-component enrichment

LOOP per `$candidate` in `$boundary_delta_components`:

1. `$design_row` = MATCH `$design_adapter.component_table.rows` where `Component == $candidate.identifier`（若 design_adapter 空則 null）
2. `$uiux_section` = MATCH `$uiux_prompt` `### \`${$candidate.identifier}\`` section（若 uiux_prompt 空則 null）

#### 3.1.1 Derive `props[]`

- 從 atomic rules 抽**互動意圖**（input fields → value/onChange props；action triggers → onClick/onSubmit；toggles → disabled/loading）
- 從 `$design_row.Detected props` 補**視覺意圖**（content / state enum）
- 對 callback prop 用標準 signature：`(value: T) => void`
- ASSERT 每個 `accessible_name_arg.field` 在 `props[*].name` 內（否則 caller 推不到 component prop interface）

#### 3.1.2 Derive `render_hints`

- `root_element` 從 `$design_row.Source nodes[0].type` 推（`button` / `input` / `div` / ...）；缺則 default `"div"`
- `children_layout` 從以下訊號推：
  - `$design_row.Source nodes` 含 `<label>` + `<input>` → `"labeled-input"`
  - `$design_row.Source nodes` 含 `<button>` + visible text → `"button"`
  - 規則 mention `children` / accept slot → `"container"`
  - 純自閉節點 → `"leaf"`
  - 其他 → `"text"`
- `base_class` 從 `$design_adapter.tokens` + `$design_row.Source nodes[0].fill / typography / spacing` 解析為 Tailwind 4 class string
  （e.g. `--color-surface` + radius=2px + padding=4 → `"bg-surface rounded-sharp px-4"`）
- `accessible_name_prop` 從 `$candidate.stories[*].accessible_name_arg.field` 取（必須一致）

#### 3.1.3 Derive `stories[]`

- 初稿從 `$candidate.source_rule_ids` 對應 features 的 Rule 抽 happy state
- 從 `$activities` 對應的 DECISION branch 抽 alternate states（rejected / disabled / submitting / 4A 等）
- 從 `$design_row.Stories` 對齊 design variants（warn 不 override）
- 每個 story export_name 為 PascalCase 狀態名（`Idle` / `Filled` / `Submitting` / `RejectedInvalidFormat`）
- ASSERT 每個 story 帶 `accessible_name` + `accessible_name_arg`（I4 hard gate）

#### 3.1.4 Cross-validation

- IF `$candidate.identifier ∉ $design_adapter.component_table.rows[*].Component`:
  → APPEND warn "component '${id}' 未在 .pen 中出現；caller reasoning 仍 authoritative" to `design_warnings`
- IF `$story.export_name ∉ $design_row.Stories`:
  → APPEND warn "story '${name}' 不在 .pen variants" to `design_warnings`
- IF `$candidate.identifier ∉ $uiux_prompt` COMPONENT CATALOG:
  → APPEND warn "component '${id}' 未在 uiux-prompt.md 中宣告" to `design_warnings`
- IF `$story.accessible_name` 與 `$uiux_prompt` ANCHOR NAME TABLE 對應 row 不一致:
  → APPEND warn "accessible_name 'X' 與 uiux-prompt 宣告 'Y' 不一致" to `design_warnings`

> warn 不 block；caller（form-story-spec）即使收到 warn 仍依 authoritative reasoning 寫檔。warn 進 plan.md research section 供 user review。

### 3.2 Cross-component checks

5. ASSERT `$enriched_components` 內無重複 identifier
6. ASSERT `$enriched_components` 內每個 identifier ∈ `$boundary_delta_components` 初稿（不得引入新 component；新增應走 reasoning/02）
7. ASSERT `$enriched_components` 涵蓋 `$boundary_delta_components` 全部 identifier（不得遺漏；遺漏應在 reasoning/02 標 deferred）

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE ComponentDesignMergeModel from per-component `$enriched_components`
2. ASSERT `$reducer_output` can replace `$$boundary_delta.components` 直接給 form-story-spec consume
3. ASSERT `$reducer_output` satisfies:

```yaml
status: complete | blocked
produces:
  ComponentDesignMergeModel:
    components: list[EnrichedComponent]
    design_source_used:
      pen_path: string | null
      uiux_prompt_path: string | null
    cross_validation_warnings: list[string]
traceability:
  inputs:
    - BoundaryDelta
    - BehaviorTruthAxis
    - DesignAdapterAxis
    - UixPromptAxis
  derived:
    - EnrichedComponent
    - PropSpec
    - RenderHints
    - StorySpec
clarifications: []
```

4. IF `cross_validation_warnings` non-empty: 不 block；warns 寫進 plan.md research section
5. IF `$enriched_components` 任一缺 `props` / `render_hints` / `stories[]` 任一欄位: status = blocked，回 caller fix
