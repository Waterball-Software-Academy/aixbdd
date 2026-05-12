# Physical-First Principle

> LOAD target: `/aibdd-plan`, `/aibdd-spec-by-example-analyze`, `/aibdd-red`, and any skill that creates or consumes DSL physical mappings.

## Principle

Business DSL must be backed by a physical testing surface before it is used by RED phase.

The source of truth is no longer `testability-plan.md`. In the new packing model, physical testability lives in boundary truth:

- provider operation contracts: `specs/<boundary>/contracts/`
- data/state/verifier truth: `specs/<boundary>/data/`
- dependency-edge test strategy: `specs/<boundary>/test-strategy.yml`
- local DSL mapping: `specs/<boundary>/packages/NN-*/dsl.yml`
- shared boundary DSL mapping: `specs/<boundary>/shared/dsl.yml`

## Layer Order

| Layer | Meaning | Owner |
|---|---|---|
| Technical truth | boundary map, contracts, data/state, test strategy | `/aibdd-plan` |
| L4 physical mapping | callable surface, source refs, parameter/assertion bindings | `/aibdd-plan` DSL synthesis |
| L3 preset handler | reusable step-def pattern such as `web-backend.command` | `/aibdd-plan` DSL synthesis |
| L2 semantics | business context, role, scope | `/aibdd-plan` DSL synthesis |
| L1 business sentence | exact Gherkin-facing phrase | `/aibdd-plan` DSL synthesis, enriched by downstream examples |

## L4 Mapping Contract

Each DSL entry must include an L4 section that points to reviewable truth and is sufficient for `/aibdd-red`.

```yaml
- id: submit-order
  L1:
    when: "客服送出訂單「{order_id}」"
    then:
      - "訂單狀態應為「{expected_status}」"
  L3:
    type: direct-call
  L4:
    surface_id: order-submit-operation
    surface_kind: operation
    callable_via: api
    preset:
      name: web-backend
      handler: command
      variant: python-e2e
    param_bindings:
      order_id:
        kind: contract_field
        target: contracts/orders.yml#operations.submit.request.order_id
    assertion_bindings:
      expected_status:
        kind: response_path
        target: response:$.status
    source_refs:
      contract: contracts/orders.yml#operations.submit
      data: data/orders.yml#states.order_status
      boundary: boundary-map.yml#rule_dispatch.defaults
      test_strategy: null
```

Missing L4, summary-only L4, or untyped parameter bindings are hard failures.

## Red-Usability Rule

`/aibdd-red` should resolve:

```text
step prose
  -> unique DSL entry
  -> L3 type / preset handler
  -> L4 callable surface
  -> parameter bindings
  -> assertion bindings
```

It must not parse plan prose, import production internals directly, invent mock channels, or guess fixture paths.

## Anti-Patterns

- DSL entry has only L1/L2/L3 and a prose `summary`.
- `{placeholder}` appears in L1 but not in `L4.param_bindings`.
- Then expected value has no `L4.assertion_bindings`.
- External provider behavior is mocked without a dependency edge and test strategy.
- Same-boundary internal collaborator is modeled as an external stub.
- File upload API lacks fixture catalog, upload invocation, response verifier, state/file-store verifier, or missing-file behavior.

## Mock DSL Business Language Rule

### MR-1 `[MOCK]` Tag

Mock-setup Given steps must include visible `[MOCK]` after the keyword:

- Good: `Given [MOCK] 金流平台預設授權付款成功`
- Good: `And [MOCK] AWS 檔案儲存服務回報上傳成功`
- Bad: `Given payment gateway mock returns approved`

### MR-2 Business-Language Surface

L1 phrases and example datatable headers must avoid implementation terms:

- forbidden: `mock`, `stub`, `queue`, `fixture`, `harness`, `spy`, `MSW`, `stub_payload`, raw contract type names
- allowed: stakeholder-visible provider roles, such as `金流平台`, `檔案儲存服務`, `通知服務`

### MR-3 Datatable Headers

Datatable headers follow the same business-language rule. Prefer `評審`, `原因`, `金額`, `付款結果` over schema field names.

### MR-6 Datatable Schema Rule

Do not use generic key-value-bag headers such as `field | value` when the table represents business data. Use domain column names.

## Mock Interaction Pattern

External stub DSL entries should declare one interaction pattern:

- `arm-default`: provider has one default response
- `arm-by-input`: provider response depends on request fields
- `arm-sequence`: provider responses occur in order
- `observe-calls`: test verifies provider was called
- `overridden-impl`: test swaps an adapter implementation

The pattern belongs in DSL L4 or the referenced test strategy entry, and must be traceable from `test-strategy.yml`.

## Relationship to Backend Presets

Backend entries should reference `web-backend` handler names when applicable:

- `aggregate-given`
- `command`
- `query`
- `success-failure`
- `readmodel-then`
- `aggregate-then`

The preset reference selects reusable step-definition pattern instructions; it does not replace L4 physical mapping.
