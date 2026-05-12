---
rp_type: reasoning_phase
id: skill-creation.02-populate-reasoning-artifacts.simple-skill
context: skill-creation
slot: "02"
name: Populate Reasoning Artifacts for Simple Skill
variant: simple-skill
consumes:
  - name: reasoning_plan
    kind: required_axis
    source: upstream_rp
    required: true
produces:
  - name: reasoning_artifact_set
    kind: material_bundle
    terminal: true
downstream: []
---

# Populate Reasoning Artifacts for Simple Skill

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: reasoning_plan
    source:
      kind: upstream_rp
      path: skill-creation.01-design-reasoning-pipeline
    granularity: one minimal reasoning plan
    required_fields:
      - enabled
      - rps
      - terminal_outputs
    optional_fields:
      - omitted_reason
    completeness_check:
      rule: plan either disables reasoning/ or names the single RP to generate
      on_missing: ASK
    examples:
      positive:
        - plan contains one RP that classifies user input before rendering a report
      negative:
        - plan contains multiple polymorphic variants requiring separate files
```

### 1.2 Search SOP

1. `$plan` = READ `reasoning_plan`
2. `$minimal_set` = EXTRACT minimal RP requirements from `$plan`
3. ASSERT `$minimal_set` contains no polymorphic slot

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: reasoning_artifact_set
  element_rules:
    element_vs_field:
      element: "A generated artifact decision that changes the skill directory"
      field: "A nested reason or path attribute of that artifact decision"
  elements:
    MinimalRPSet:
      role: "One optional RP file or an explicit decision to omit reasoning/"
      fields:
        enabled: boolean
        rp_path: string | null
        terminal_outputs: list
      invariants:
        - "Contains no polymorphic slot"
    ReasoningOmission:
      role: "Rationale for not generating reasoning/ when semantic complexity is low"
      fields:
        reason: string
        traceability: list
      invariants:
        - "Present only when MinimalRPSet.enabled is false"
```

## 3. Reasoning SOP

1. `$minimal_need` = JUDGE `$plan` against `MinimalRPSet`
2. `$omission` = DERIVE `ReasoningOmission` if `$minimal_need` is false
3. `$artifact_shape` = DERIVE `MinimalRPSet` from `$minimal_set`

## 4. Material Reducer SOP

1. `$reasoning_artifact_set` = DERIVE output files from `MinimalRPSet` and `ReasoningOmission`
2. ASSERT `MinimalRPSet` is represented in `$reasoning_artifact_set`
3. ASSERT `ReasoningOmission` is represented when no RP file is generated

Return:

```yaml
status: complete
produces:
  reasoning_artifact_set:
    variant: simple-skill
traceability:
  inputs:
    - reasoning_plan
  derived:
    - MinimalRPSet
    - ReasoningOmission
```
