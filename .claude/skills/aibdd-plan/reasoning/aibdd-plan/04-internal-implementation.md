---
rp_type: reasoning_phase
id: aibdd-plan.04-internal-implementation
context: aibdd-plan
slot: "04"
name: Internal Implementation
variant: none
consumes:
  - name: BoundaryDispatchModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: ExternalSurfaceModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: CodeSkeletonAxis
    kind: required_axis
    source: filesystem
    required: true
produces:
  - name: ImplementationModel
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-plan.05-dsl-truth-synthesis
  - aibdd-plan.06-handoff-graph
---

# Internal Implementation

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: CodeSkeletonAxis
    source:
      kind: filesystem
      path: current project source tree
    granularity: module, class, function, route, repository, or adapter
    required_fields:
      - path
      - symbol_or_role
      - boundary_relevance
    optional_fields:
      - existing_test_hook
      - adapter_hint
    completeness_check:
      rule: impacted boundary has at least one plausible entry operation or explicit skeleton gap
      on_missing: mark_unknown
    examples:
      positive:
        - FastAPI route module with repository dependency
      negative:
        - unrelated project config file
```

### 1.2 Search SOP

1. `$dispatch` = READ BoundaryDispatchModel
2. `$external` = READ ExternalSurfaceModel
3. `$code_index` = READ CodeSkeletonAxis
4. ASSERT `$dispatch.rule_dispatch.defaults` exists

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: ImplementationModel
  element_rules:
    element_vs_field:
      element: independently targetable implementation unit or path
      field: method name, note, or source pointer under a unit
  elements:
    ImplementationPath:
      role: happy, alternative, or error behavior path
      fields:
        slug: string  # localized scenario slug is allowed, e.g. 指派學員至旅程階段
        kind: happy | alt | err
        source_rules: list
        sequence_participants: list
        provider_calls: list
        state_changes: list
        response_candidates: list
        failure_reason: string | null
    ImplementationTarget:
      role: class, module, operation, verifier, adapter, or repository used by tasks
      fields:
        target_id: string
        file_or_symbol: string
        target_kind: string
        source_refs: list
    InternalStructure:
      role: structural union of all implementation paths
      fields:
        classes_or_modules: list
        relationships: list
```

## 3. Reasoning SOP

1. `$operation_paths` = DERIVE one `happy` ImplementationPath for every feature operation that can complete without a branch or external/provider failure.
2. `$branch_paths` = DERIVE `alt` ImplementationPath set from activity decision branches and rule-only features that represent valid business alternatives (for example positive intent scheduling vs negative intent retention).
3. `$provider_failure_paths` = DERIVE `err` ImplementationPath set from ExternalSurfaceModel provider calls that can fail or be retryable.
4. `$precondition_failure_paths` = DERIVE `err` ImplementationPath set from precondition rules that can fail before the operation mutates state.
5. `$paths` = UNION `$operation_paths`, `$branch_paths`, `$provider_failure_paths`, `$precondition_failure_paths`
6. For every `$path`:
   6.1 SET `$path.kind` to exactly one of `happy | alt | err`
   6.2 SET `$path.slug` to the concise scenario name; use the feature/activity natural language when filenames are non-Latin-heavy
   6.3 SET `$path.sequence_participants` to actor + boundary entry + application service + repository + external provider where applicable
   6.4 SET `$path.state_changes` to persisted reads/writes touched by the path
   6.5 SET `$path.response_candidates` to the response verifier candidates consumed by downstream tasks
7. `$targets` = DERIVE ImplementationTarget set from `$paths` and code skeleton
8. `$structure` = DERIVE InternalStructure from `$targets`
9. ASSERT every major happy, alternative, and error behavior path has an ImplementationPath or blocked reason
10. ASSERT every ImplementationTarget traces to rule, operation, state, or provider surface
11. ASSERT sequence filenames can be rendered as `<slug>.<kind>.sequence.mmd`

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE ImplementationModel from `$paths`, `$targets`, `$structure`
2. ASSERT `$reducer_output` can render sequence diagrams and class diagram
3. ASSERT `$reducer_output` satisfies:

```yaml
status: complete | blocked
produces:
  ImplementationModel:
    paths: list[ImplementationPath]
    targets: list[ImplementationTarget]
    structure: InternalStructure
traceability:
  inputs:
    - BoundaryDispatchModel
    - ExternalSurfaceModel
    - CodeSkeletonAxis
  derived:
    - ImplementationPath
    - ImplementationTarget
    - InternalStructure
clarifications: []
```
