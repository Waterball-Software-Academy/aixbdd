---
rp_type: reasoning_phase
id: aibdd-plan.02-technical-boundary-dispatch
context: aibdd-plan
slot: "02"
name: Technical Boundary Dispatch
variant: none
consumes:
  - name: PlanningContext
    kind: material_bundle
    source: upstream_rp
    required: true
  - name: BehaviorTruthAxis
    kind: required_axis
    source: filesystem
    required: true
produces:
  - name: BoundaryDispatchModel
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-plan.03-external-boundary-surface
  - aibdd-plan.04-internal-implementation
---

# Technical Boundary Dispatch

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: BehaviorTruthAxis
    source:
      kind: filesystem
      path: ${TRUTH_FUNCTION_PACKAGE}/activities and ${TRUTH_FUNCTION_PACKAGE}/features
    granularity: accepted activity path or atomic rule
    required_fields:
      - activity_path
      - rule_id
      - operation_trigger
      - consequence
    optional_fields:
      - actor
      - state
      - provider_hint
    completeness_check:
      rule: every rule-only feature rule is traceable to Discovery scope
      on_missing: STOP
    examples:
      positive:
        - rule-only feature with operation trigger and consequence
      negative:
        - scenario example row without rule id
```

### 1.2 Search SOP

1. `$activities` = READ BehaviorTruthAxis activity source
2. `$features` = READ BehaviorTruthAxis feature source
3. `$rules` = EXTRACT atomic rules from `$features`
4. ASSERT `$rules` non-empty

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: BoundaryDispatchModel
  element_rules:
    element_vs_field:
      element: dispatchable technical ownership decision
      field: source pointer or explanatory note under a decision
  elements:
    DispatchDefault:
      role: declares how package structure implies ordinary rule ownership
      fields:
        boundary_id: string
        package_scope: glob
        infer_from: list[package_path | feature_file | activity_anchor | contract_operation_id | package_dsl]
    DispatchOverride:
      role: records only non-default dispatch decisions
      fields:
        rule_id: string
        reason: cross-boundary | shared-operation | non-standard-owner | planning-gap
        owner_boundary: string
        contract_ref: string
        source_refs: list
    DependencyEdge:
      role: consumer-provider relationship requiring contract or strategy
      fields:
        consumer: string
        provider: string
        provider_kind: internal_boundary | third_party
        contract_required: boolean
        mockable: boolean
    PersistenceDecision:
      role: boundary-owned state and storage responsibility
      fields:
        entity_or_state: string
        owner_boundary: string
        persistence_kind: string
        verifier_needed: boolean
```

## 3. Reasoning SOP

1. `$dispatch_default` = DERIVE DispatchDefault from PlanningContext and package layout
2. `$dispatch_overrides` = DERIVE DispatchOverride set only for rules that cannot be inferred from package layout
3. `$edges` = DERIVE DependencyEdge set from operation triggers and provider hints
4. `$persistence` = DERIVE PersistenceDecision set from consequences and state mentions
5. ASSERT no rule is copied into boundary-map when package structure + contract operation id can imply ownership
6. ASSERT no dependency edge treats same-boundary collaborator as external provider

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE BoundaryDispatchModel from `$dispatch_default`, `$dispatch_overrides`, `$edges`, `$persistence`
2. ASSERT `$reducer_output` can render `boundary-map.yml`
3. ASSERT `$reducer_output` satisfies:

```yaml
status: complete | blocked
produces:
  BoundaryDispatchModel:
    rule_dispatch:
      defaults: DispatchDefault
      overrides: list[DispatchOverride]
    dependency_edges: list[DependencyEdge]
    persistence: list[PersistenceDecision]
traceability:
  inputs:
    - PlanningContext
    - BehaviorTruthAxis
  derived:
    - DispatchDefault
    - DispatchOverride
    - DependencyEdge
    - PersistenceDecision
clarifications: []
```
