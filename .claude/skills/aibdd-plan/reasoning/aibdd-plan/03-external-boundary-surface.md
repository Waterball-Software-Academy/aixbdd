---
rp_type: reasoning_phase
id: aibdd-plan.03-external-boundary-surface
context: aibdd-plan
slot: "03"
name: External Boundary Surface
variant: none
consumes:
  - name: BoundaryDispatchModel
    kind: derived_axis
    source: upstream_rp
    required: true
  - name: ExistingTechnicalTruthAxis
    kind: required_axis
    source: filesystem
    required: true
produces:
  - name: ExternalSurfaceModel
    kind: derived_axis
    terminal: false
downstream:
  - aibdd-plan.04-internal-implementation
  - aibdd-plan.05-dsl-truth-synthesis
---

# External Boundary Surface

## 1. Material Sourcing

### 1.1 Required Axis

```yaml
required_axis:
  - name: ExistingTechnicalTruthAxis
    source:
      kind: filesystem
      path: boundary-map.yml, contracts, data, test-strategy.yml
    granularity: provider operation or dependency edge
    required_fields:
      - dependency_edge
      - provider_kind
      - operation_or_state_need
    optional_fields:
      - existing_contract
      - existing_policy
      - known_failure_modes
    completeness_check:
      rule: every external edge can be classified as contract-needed or explicitly non-contract
      on_missing: STOP
    examples:
      positive:
        - payment provider edge with charge operation and failure response
      negative:
        - same-boundary service object marked as mock provider
```

### 1.2 Search SOP

1. `$edges` = READ BoundaryDispatchModel dependency edges
2. `$existing_contracts` = READ ExistingTechnicalTruthAxis contract source
3. `$strategy` = READ ExistingTechnicalTruthAxis test strategy source
4. ASSERT no edge is missing provider_kind

## 2. Modeling Element Definition

```yaml
modeling_element_definition:
  output_model: ExternalSurfaceModel
  element_rules:
    element_vs_field:
      element: externally callable or stubbable provider surface
      field: request/response field under a provider operation
  elements:
    ProviderOperation:
      role: contract-backed operation provided by another boundary or third party
      fields:
        provider: string
        operation_id: string
        request_fields: list
        response_fields: list
        error_modes: list
        source_refs: list
    TestDoublePolicy:
      role: test strategy for one consumer-provider edge
      fields:
        edge_id: string
        double_kind: stub | fake | real | none
        reset_lifecycle: string
        allowed_failure_modes: list
    ExternalStubSurface:
      role: DSL-callable stub surface for external dependency behavior
      fields:
        surface_id: string
        provider_operation: string
        payload_bindings: list
        response_bindings: list
```

## 3. Reasoning SOP

1. `$provider_ops` = DERIVE ProviderOperation set from external edges and existing contracts
2. `$policies` = DERIVE TestDoublePolicy set from provider edges and strategy
3. `$stubs` = DERIVE ExternalStubSurface set for mockable third-party edges
4. ASSERT every mockable edge has exactly one TestDoublePolicy
5. ASSERT every ExternalStubSurface references ProviderOperation

## 4. Material Reducer SOP

1. `$reducer_output` = DERIVE ExternalSurfaceModel from `$provider_ops`, `$policies`, `$stubs`
2. ASSERT `$reducer_output` can update contracts and test-strategy truth
3. ASSERT `$reducer_output` satisfies:

```yaml
status: complete | blocked
produces:
  ExternalSurfaceModel:
    provider_operations: list[ProviderOperation]
    test_double_policy: list[TestDoublePolicy]
    external_stub_surfaces: list[ExternalStubSurface]
traceability:
  inputs:
    - BoundaryDispatchModel
    - ExistingTechnicalTruthAxis
  derived:
    - ProviderOperation
    - TestDoublePolicy
    - ExternalStubSurface
clarifications: []
```
