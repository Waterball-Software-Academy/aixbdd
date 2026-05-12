---
rp_type: reasoning_phase
id: skill-creation.02-populate-reasoning-artifacts.reasoning-heavy-skill
context: skill-creation
slot: "02"
name: Populate Reasoning Artifacts for Reasoning Heavy Skill
variant: reasoning-heavy-skill
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

# Populate Reasoning Artifacts for Reasoning Heavy Skill

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: reasoning_plan
    source:
      kind: upstream_rp
      path: skill-creation.01-design-reasoning-pipeline
    granularity: one multi-RP reasoning plan
    required_fields:
      - contexts
      - rps
      - consumes
      - produces
      - downstream
    optional_fields:
      - polymorphic_slots
      - selector
    completeness_check:
      rule: every RP has stable handoff contract and every polymorphic slot has selector plus variants
      on_missing: ASK
    examples:
      positive:
        - plan contains source intake, semantic classification, reducer, and variant selector
      negative:
        - plan only says "do reasoning" without RP ids or material handoffs
```

### 1.2 Search SOP

1. `$plan` = READ `reasoning_plan`
2. `$rp_specs` = EXTRACT RP specs from `$plan`
3. `$poly_specs` = EXTRACT polymorphic slot specs from `$plan`
4. `$gaps` = DERIVE missing artifact contract fields from `$rp_specs` and `$poly_specs`
5. IF `$gaps` not empty:
   5.1 `$artifact_clarification` = ASK "請補齊 RP meta / Required Axis / variant selector"
   5.2 `$rp_specs2` = DERIVE complete RP specs from `$rp_specs` and `$artifact_clarification`

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: reasoning_artifact_set
  element_rules:
    element_vs_field:
      element: "A generated reasoning artifact contract that changes files or validation behavior"
      field: "A nested path, id, selector, or schema attribute of an artifact contract"
  elements:
    RPArtifactSpec:
      role: "Concrete file plan for each reasoning/**/*.md reasoning phase"
      fields:
        id: string
        context: string
        slot: string
        path: string
        consumes: list
        produces: list
      invariants:
        - "Each RP has stable id / context / slot / path"
    PolymorphismArtifactSpec:
      role: "Concrete interface and variant file plan for each polymorphic slot"
      fields:
        slot: string
        selector: string
        variants: list
        shared_contract: object
      invariants:
        - "Selector exists when variants exist"
    GraphHandoff:
      role: "Consumes, produces, and downstream links needed by graph eval"
      fields:
        consumes: list
        produces: list
        downstream: list
      invariants:
        - "No dangling required upstream input"
    ModelingElementSchemaSet:
      role: "Per-RP Modeling Element Definition schema terms that are output model elements, domain-native, and free of intermediate variables"
      fields:
        output_model: string
        elements: list
        element_field_boundaries: list
      invariants:
        - "No verdict/check/render-format variables"
        - "Fields stay nested under parent elements"
```

## 3. Reasoning SOP

1. `$artifact_specs` = DERIVE `RPArtifactSpec` from `$rp_specs`
2. `$polymorphism_specs` = DERIVE `PolymorphismArtifactSpec` from `$poly_specs`
3. `$modeling_schemas` = DERIVE `ModelingElementSchemaSet` from `$artifact_specs`
4. `$handoff` = DERIVE `GraphHandoff` from `$artifact_specs` and `$polymorphism_specs`
5. ASSERT `GraphHandoff` has no dangling required upstream input
6. ASSERT `ModelingElementSchemaSet` contains no intermediate verdict/check/render-format variables

## 4. Material Reducer SOP

1. `$reasoning_artifact_set` = DERIVE output files from `RPArtifactSpec`, `PolymorphismArtifactSpec`, `GraphHandoff`, and `ModelingElementSchemaSet`
2. ASSERT `$artifact_clarification` is represented in `$reasoning_artifact_set` if ASK occurred
3. ASSERT `RPArtifactSpec`, `PolymorphismArtifactSpec`, `GraphHandoff`, and `ModelingElementSchemaSet` are represented in `$reasoning_artifact_set`

Return:

```yaml
status: complete | blocked
produces:
  reasoning_artifact_set:
    variant: reasoning-heavy-skill
traceability:
  inputs:
    - reasoning_plan
  derived:
    - RPArtifactSpec
    - PolymorphismArtifactSpec
    - GraphHandoff
    - ModelingElementSchemaSet
clarifications:
  - $artifact_clarification
```
