# DSL Output Contract

## Purpose

`dsl.yml` is the physical mapping registry consumed by `/aibdd-red`. It maps exact business sentences (L1) to technical surfaces (L4) without requiring downstream skills to parse plan prose. The file is YAML; top-level shape is `entries: [ ... ]`.

## `source_refs` placement

`source_refs` are **normative on `L4`** (same block as `param_bindings` / `assertion_bindings`). Top-level `source_refs` outside `L4` is not the contract path for new work.

## DSL key locale (planning input)

Phase 6 receives `$$dsl_key_locale` (`prefer_spec_language` or a BCP 47 language tag such as `zh-hant` / `en-us`). When `prefer_spec_language`, L1 placeholders and `param_bindings` / `assertion_bindings` **keys** SHOULD follow the spec’s natural language with **optional** English technical tokens (e.g. `{旅程 ID}`, `{stage ID}`). **Underlying** `target` strings remain technical: `contracts/...`, `data/...`, `response:...`. Do **not** translate contract field names inside YAML operation contracts.

## Required entry shape

Each entry contains:

- `id`
- `source.rule_id`
- `source.boundary_id`
- `source.feature_path`
- `L1` business sentence pattern
- `L2` semantic context, role, and scope
- `L3.type`
- `L4.surface_id`
- `L4.surface_kind`
- `L4.callable_via`
- `L4.param_bindings`
- `L4.datatable_bindings` (when operation inputs stay scenario-visible but are not sentence-critical)
- `L4.default_bindings` (when operation inputs are atomic-rule-safe defaults)
- `L4.assertion_bindings`
- `L4.source_refs`
- `L4.preset` (backend handler tuple) where applicable

## Parameter / assertion binding discipline

- Every `{placeholder}` appearing in L1 must map to **exactly one** binding key in **either** `param_bindings` **or** `assertion_bindings`, never both.
- `param_bindings` is for sentence-critical L1 placeholders. It must not carry a contract input that is not visible in L1 unless that input is a fixture/stub implementation detail.
- `datatable_bindings` is for scenario-visible business inputs that are intentionally kept out of the sentence to protect readability. The datatable column name is the DSL-facing key; the `target` is the physical field.
- `default_bindings` is for required inputs whose values do not affect the feature atomic rules for the majority behavior under test. Each default binding must include `target`, `value`, `reason`, and `override_via`.
- For `surface_kind: operation`, **`param_bindings + datatable_bindings + default_bindings`** must list **exactly** the contract **`request.params` + `request.body.fields` + non-excluded `request.headers`** inputs marked `required: true`. **No extra** contract input bindings; **no missing** required ones. **Transport / ambient headers** commonly omitted from scenario prose (e.g. `X-Actor-Role`) are **excluded** from this exact set by deterministic gate policy.
- Every `contracts/...` target must use shape `contracts/<file>.yml#<operation_id>.request.{params|body|headers}.<name>` (or response fields when used for assertions). The file and operation must exist under `${CONTRACTS_DIR}`. For `web-service`, `${CONTRACTS_DIR}` files are OpenAPI documents produced by `/aibdd-form-api-spec`; deterministic gates index OpenAPI `operationId` values into the same anchor shape.
- Every `data/...` target must reference a real entity field in `${DATA_DIR}`. For `web-service`, entity truth is DBML produced by `/aibdd-form-entity-spec`, using `data/<file>.dbml#table.column` anchors (see `check_dsl_entries.py`). Legacy `entity_id`-shaped YAML anchors remain accepted only for older fixtures.

## Readability pressure discipline

- Operation-backed L1 sentence parameters must be `<= 3`.
- Datatable parameters must be `<= 6` after defaults.
- A parameter may be moved to `default_bindings` only when the feature's atomic rules show that varying the value does not change the behavior under test for the majority path.
- Defaults are not hidden behavior: they must be documented in L4 and may be overridden by datatable unless the contract/test strategy explicitly forbids variation.

## Stateless DSL discipline

Each L1 sentence must be stateless: if a single `Given` / `When` / `Then` / `And`
line is read without the previous or next step, `/aibdd-red` must still be able
to identify the business subject, lookup identity, and expected data/effect from
that line plus its same-step datatable.

- `Given` state/stub/time sentences must name the pre-existing state or external
  edge being controlled. If the state belongs to a specific entity, the entity
  identity must appear in L1 or in the same-step datatable.
- `When` operation sentences must name the actor, business subject, operation,
  and subject identity whenever the operation acts on an identifiable entity.
- `Then` and `And` assertions must name the observable response, persisted state,
  or external effect and include lookup identity plus expected value. `And` does
  not inherit a subject from the previous `Then`.
- Binding keys for identity fields must say `XXX ID` when the physical target is
  an ID-like contract/data/response field. Do not hide identity behind keys such
  as `旅程`, `階段`, or `預約單`.
- A placeholder may not be added only to satisfy a technical binding; it must be
  meaningful to the atomic rule or to the step's stateless lookup.

## Dynamic ID reference notation

When an ID is generated by the system and cannot be known before execution,
feature Examples may use `$<unique business identifier>.id`, for example
`$小明.id` or `$標準CRM旅程.id`.

The business identifier must be declared in the same scenario through L1,
datatable, fixture alias, captured response, or queryable state. Ambiguous aliases
such as `$id`, `$previous.id`, `$that.id`, `$上一筆.id`, or `$剛剛建立的.id`
are illegal because they depend on scenario memory instead of a stable business
identifier.

## Datatable business projection

Gherkin datatables are business projections, not raw API payloads, DTOs, JSON
arrays, YAML objects, GraphQL inputs, or DB rows.

- Do not put raw JSON/YAML/object literals in datatable cells.
- For nested aggregates, keep one logical setup/operation step and expose child
  fields as business columns. The handler normalizes those columns into the
  technical payload.
- When a datatable column maps into an array/object item, the DSL binding should
  declare `group` and `item_field` so downstream renderers can reconstruct the
  aggregate deterministically.
- Do not split one aggregate setup into multiple partial `Given` steps unless a
  declared handler explicitly supports partial aggregate construction.

## Binding target kinds

Allowed binding target prefixes:

- `contracts/<file>.yml#…`
- `data/<file>.dbml#table.column` (preferred for `web-service` DBML entity truth)
- `data/<file>.yml#entity_id.field` (legacy YAML entity truth)
- `response:...` (JSONPath-style probe; `response:$.__http.*` allowed for transport assertions)
- `fixture:...`
- `stub_payload:...`
- `literal:...`

## Surface kinds

Same as previous contract: `loader`, `operation`, `state-verifier`, `response-verifier`, `external-stub`, `fixture-upload`, `internal-decision`.

## External stubs / fixture upload / red-usability

Unchanged from prior contract: external stubs reference provider contracts + test strategy; file upload APIs document fixture paths, missing-file behavior, and verifiers.

## Aggregate-given DBML coverage discipline

For any DSL entry whose `L4.preset.handler == aggregate-given`, the union of
`param_bindings + datatable_bindings + default_bindings` must 100% cover the
NOT-NULL columns of the DBML table identified by `L4.source_refs.data` (shape
`data/<file>.dbml#<table>`).

Exemption rules (applied in order; first match wins):

1. **PK auto-increment** — column declared with both `[pk]` and `[increment]`.
2. **Explicit DBML default** — column declared with `[default: <value>]`.

There is no conventional exemption for `created_at` / `updated_at`; if a
timestamp should be DB-defaulted, mark it `[default: \`now()\`]` in DBML so the
exemption is explicit truth. FK NOT-NULL columns must be bound directly — a
lookup-chain binding pointing at a different table's column does not satisfy
coverage for the verified table's FK.

## Deterministic verification

`/aibdd-plan` Phase 7 runs `scripts/python/check_dsl_entries.py "${arguments.yml}"`, which enforces DSL registry path extension (`dsl.yml`), placeholder coverage, contract operation **required input** exact set across `param_bindings + datatable_bindings + default_bindings` for `operation` entries, contract/data target existence, DBML table-column anchor existence, default binding shape, basic response-probe consistency, and **aggregate-given NOT-NULL coverage** against the entry's DBML target table per the rules above.
