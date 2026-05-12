---
rp_type: reasoning_phase
id: skill-creation.01-design-reasoning-pipeline
context: skill-creation
slot: "01"
name: Design Reasoning Pipeline
variant: none
consumes:
  - name: source_material_bundle
    kind: required_axis
    source: upstream_rp
    required: true
produces:
  - name: reasoning_plan
    kind: decision
    terminal: false
downstream:
  - skill-creation.02-populate-reasoning-artifacts
---

# Design Reasoning Pipeline

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: source_material_bundle
    source:
      kind: upstream_rp
      path: skill-creation.00-source-intake-material
    granularity: one normalized skill creation bundle
    required_fields:
      - phase_outline
      - rough_steps
      - resources
      - reasoning_plan
    optional_fields:
      - polymorphic_slots
      - examples
    completeness_check:
      rule: bundle contains enough semantic complexity signals to decide if RP artifacts are useful
      on_missing: ASK
    examples:
      positive:
        - source material says the skill must classify, judge, reduce, or choose between reasoning strategies
      negative:
        - source material describes only deterministic file copying with no semantic transformation
```

### 1.2 Search SOP

1. `$bundle` = READ `source_material_bundle`
2. `$signals` = EXTRACT semantic complexity signals from `$bundle`
3. `$gaps` = DERIVE missing reasoning design fields from `$signals`
4. IF `$gaps` not empty:
   4.1 `$rp_clarification` = ASK "請補充 RP context / consumes / produces / variant selector"
   4.2 `$signals2` = DERIVE completed signals from `$signals` and `$rp_clarification`

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: reasoning_plan
  element_rules:
    element_vs_field:
      element: "A planning unit that changes generated reasoning artifacts"
      field: "A property nested under an RP plan or polymorphism plan"
  elements:
    ReasoningNeed:
      role: "Whether the generated skill benefits from a first-class reasoning/ pipeline"
      fields:
        enabled: boolean
        rationale: string
        semantic_complexity_signals: list
      invariants:
        - "False when the skill is only deterministic file or template generation"
    RPPlan:
      role: "Ordered list of RP files with context, slot, consumes, produces, and downstream relation"
      fields:
        rps: list
        contexts: list
        terminal_outputs: list
      invariants:
        - "Stable ids"
        - "Acyclic downstream handoff"
    PolymorphismNeed:
      role: "Whether a slot needs multiple reasoning strategies selected by SKILL.md"
      fields:
        enabled: boolean
        slot: string | null
        selector: string | null
        variants: list
      invariants:
        - "Selector exists when variants are generated"
```

## 3. Reasoning SOP

1. `$need` = JUDGE `$signals` against `ReasoningNeed`
2. `$rp_plan` = DERIVE `RPPlan` from `$bundle` and `$need`
3. `$poly_need` = CLASSIFY `$rp_plan` by `PolymorphismNeed`
4. ASSERT `RPPlan` has stable ids and acyclic downstream handoff

## 4. Material Reducer SOP

1. `$reasoning_plan` = DERIVE generated skill reasoning plan from `ReasoningNeed`, `RPPlan`, and `PolymorphismNeed`
2. ASSERT `$rp_clarification` is represented in `$reasoning_plan` if ASK occurred
3. ASSERT every `RPPlan` output is consumed downstream or marked terminal

Return:

```yaml
status: complete | blocked
produces:
  reasoning_plan: RPPlan
traceability:
  inputs:
    - source_material_bundle
  derived:
    - ReasoningNeed
    - RPPlan
    - PolymorphismNeed
clarifications:
  - $rp_clarification
```
