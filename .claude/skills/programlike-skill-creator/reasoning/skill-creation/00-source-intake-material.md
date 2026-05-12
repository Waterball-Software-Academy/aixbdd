---
rp_type: reasoning_phase
id: skill-creation.00-source-intake-material
context: skill-creation
slot: "00"
name: Source Intake Material
variant: none
consumes:
  - name: user_intake_requirement
    kind: required_axis
    source: caller
    required: true
produces:
  - name: source_material_bundle
    kind: material_bundle
    terminal: false
downstream:
  - skill-creation.01-design-reasoning-pipeline
---

# Source Intake Material

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: user_intake_requirement
    source:
      kind: caller
      path: intake-questions
    granularity: 使用者對「要建立的 skill」提出的一份需求描述；以自然語言為主，可以是段落、條列、既有筆記、半成品 SOP、或已結構化的 intake answers
    required_fields:
      - natural_language_requirement
    optional_fields:
      - name
      - description
      - trigger_scenarios
      - phase_outline
      - rough_steps
      - resources
      - reasoning_plan
      - examples
      - target_skill_dir
      - constraints
      - desired_output_shape
    completeness_check:
      rule: 自然語言需求足以讓 agent 推導 skill 目的、觸發條件、主要工作流、資源需求，並判斷是否需要 reasoning/；若使用者已提供結構化欄位，視為輔助線索而非必要格式
      on_missing: ASK
    examples:
      positive:
        - 使用者用一段話描述「我要一個能把訪談稿轉成 BDD 規格的 skill」，並補充它應該問澄清問題、產生 activity 與 feature 草稿
        - 使用者貼上既有 SOP、幾個例子、以及期望輸出目錄；即使沒有填完正式 intake 表單，也能推導後續設計
        - 使用者提供完整表格式 intake answers，包含 name、description、phase_outline、resources、reasoning_plan
      negative:
        - 使用者只提供 skill 名稱，沒有說明目的、觸發情境、輸入、輸出或行為邊界
        - 使用者只說「幫我做一個很強的 skill」，但沒有任何 domain、workflow 或成功條件
```

### 1.2 Search SOP

1. `$intake` = READ caller user_intake_requirement
2. `$missing` = DERIVE missing required fields from `$intake`
3. IF `$missing` not empty:
   3.1 `$clarification` = ASK "請補齊 skill creation intake 缺少欄位"
   3.2 `$intake2` = DERIVE completed intake from `$intake` and `$clarification`
4. `$source_material_bundle` = DERIVE normalized source material from `$intake`

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: source_material_bundle
  element_rules:
    element_vs_field:
      element: "A unit that can block or drive downstream skill creation"
      field: "A normalized intake attribute nested under SourceMaterialBundle"
  elements:
    SourceMaterialBundle:
      role: "Normalized input bundle containing skill identity, SOP outline, resources, and reasoning requirements"
      fields:
        identity: object
        phase_outline: list
        rough_steps: list
        resources: list
        reasoning_plan: object | null
        constraints: list
      invariants:
        - "Contains all fields required by downstream RP"
    IntakeGap:
      role: "Missing field that blocks scaffold or reasoning artifact generation"
      fields:
        missing_field: string
        blocker_reason: string
        clarification: string | null
      invariants:
        - "Absent when source material is complete"
```

## 3. Reasoning SOP

1. `$bundle` = CLASSIFY caller input into `SourceMaterialBundle` and `IntakeGap`
2. `$source_material_bundle` = DERIVE `SourceMaterialBundle` from `$bundle`
3. ASSERT `SourceMaterialBundle` includes all fields required by downstream RP

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE `source_material_bundle` from `SourceMaterialBundle`
2. ASSERT `$clarification` is represented in `$reducer_output` if ASK occurred
3. ASSERT `IntakeGap` is absent or represented as blocked status

Return:

```yaml
status: complete | blocked
produces:
  source_material_bundle: SourceMaterialBundle
traceability:
  inputs:
    - user_intake_requirement
  derived:
    - SourceMaterialBundle
    - IntakeGap
clarifications:
  - $clarification
```
