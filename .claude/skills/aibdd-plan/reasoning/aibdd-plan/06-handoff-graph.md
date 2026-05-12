---
rp_type: reasoning_phase
id: aibdd-plan.06-handoff-graph
context: aibdd-plan
slot: "06"
name: Handoff Graph
variant: none
consumes:
  - name: HandoffArtifactAxis
    kind: required_axis
    source: caller
    required: true
  - name: BoundaryDispatchModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: ExternalSurfaceModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: ImplementationModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: DSLDeltaModel
    kind: derived_axis
    source: upstream_rp
    required: true
produces:
  - name: DownstreamHandoffGraph
    kind: material_bundle
    terminal: true
downstream: []
---

# Handoff Graph

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: HandoffArtifactAxis
    source:
      kind: caller
      path: written artifact paths from SKILL.md Phase 3-7
    granularity: artifact pointer
    required_fields:
      - plan
      - research
      - boundary_map
      - contracts
      - data
      - test_strategy
      - dsl
      - sequence_diagrams
      - internal_structure
    optional_fields:
      - blocking_gaps
      - quality_report
    completeness_check:
      rule: downstream can read artifact graph without re-planning
      on_missing: STOP
    examples:
      positive:
        - graph linking rule id to DSL entry and sequence target
      negative:
        - plain summary with only written file count
```

### 1.2 Search SOP

1. `$outputs` = READ HandoffArtifactAxis
2. `$dsl` = READ DSLDeltaModel
3. ASSERT `$outputs.plan` and `$dsl` exist

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: DownstreamHandoffGraph
  element_rules:
    element_vs_field:
      element: independently walkable downstream input pointer
      field: reason, note, or review focus under a pointer
  elements:
    ArtifactPointer:
      role: path or anchor consumed downstream
      fields:
        artifact_type: string
        path: path
        anchor: string
        owner: string
    TraceLink:
      role: relationship between behavior truth and technical truth
      fields:
        from: string
        to: string
        relation: string
        evidence: string
    ReviewFocus:
      role: Git diff review item
      fields:
        artifact: string
        reason: string
        risk: string
```

## 3. Reasoning SOP

1. `$pointers` = DERIVE ArtifactPointer set for plan, research, truth files, DSL, diagrams, and quality reports
2. `$links` = DERIVE TraceLink set from:
   2.1 feature rule → boundary-map dispatch
   2.2 boundary-map operation → contract operation
   2.3 boundary-map state effect → data model field/table
   2.4 provider edge → test-strategy external stub policy
   2.5 feature rule / provider edge → DSL entry
   2.6 DSL entry / operation path → sequence diagram
3. `$review_focus` = DERIVE ReviewFocus set from owner-scoped truth deltas
4. ASSERT no pointer requires `/aibdd-test-plan`
5. ASSERT every changed DSL entry has at least one trace link to a rule or provider edge
6. ASSERT every sequence diagram pointer has a trace link from at least one operation, branch, provider failure, or precondition failure
7. ASSERT quality report pointer includes actual script verdict evidence, not only expected-pass prose

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE DownstreamHandoffGraph from `$pointers`, `$links`, `$review_focus`
2. ASSERT `$reducer_output` can be emitted as final report
3. ASSERT `$reducer_output` satisfies:

```yaml
status: complete | blocked
produces:
  DownstreamHandoffGraph:
    artifact_pointers: list[ArtifactPointer]
    trace_links: list[TraceLink]
    review_focus: list[ReviewFocus]
traceability:
  inputs:
    - HandoffArtifactAxis
    - DSLDeltaModel
  derived:
    - ArtifactPointer
    - TraceLink
    - ReviewFocus
clarifications: []
```
