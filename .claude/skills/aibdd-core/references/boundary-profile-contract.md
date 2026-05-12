# Boundary Profile Contract

Boundary profiles define the minimal type-specific artifact behavior that cannot
be hard-coded into a planner. They are intentionally small: a profile tells
consumers which formulation skill owns each boundary-specific technical surface,
while path resolution still comes from `.aibdd/arguments.yml` and `boundary.yml`.

## Profile Location

Profiles live under:

`aibdd-core/references/boundary-type-profiles/<type>.profile.yml`

The `<type>` value is the `type` field from `specs/architecture/boundary.yml`.
Adding a new boundary type should add a new profile file, not a new branch in
`/aibdd-plan`.

## Minimal Shape

```yaml
id: web-service
role: backend

state_specifier:
  skill: /aibdd-form-entity-spec
  format: dbml
  semantics: persistent
  output_dir_key: DATA_DIR
  default_filename: domain.dbml

operation_contract_specifier:
  skill: /aibdd-form-api-spec
  format: openapi
  output_dir_key: CONTRACTS_DIR
  default_filename: api.yml

component_contract_specifier:
  # Owns Story-export-level UI contracts (boundary invariant I4 binding anchor).
  # Frontend boundaries use `/aibdd-form-story-spec` (CSF3 Storybook output);
  # backend boundaries declare `skill: none`.
  skill: /aibdd-form-story-spec | none
  format: csf3 | none
  output_dir_key: FE_STORIES_DIR      # frontend; "" for none
  default_filename: ""                # one file per component (caller picks per identifier)

# Handler used to seed boundary-persisted state in plan DSL.
# Consumed by /aibdd-plan persistence-ownership coverage gate and
# /aibdd-spec-by-example-analyze entity-coverage gate.
persistence_handler:
  handler_id: aggregate-given            # required — preset's persistence-state seeding handler
  state_ref_pattern: "data/<file>.dbml#<table>"   # required — glob/template for L4.source_refs.data
  routing_yml: aibdd-core/assets/boundaries/web-backend/handler-routing.yml  # required — preset SSOT
  coverage_gate: not-null-columns        # required — `not-null-columns` | `deferred-v1` | `none`

# Allowed L4 binding target prefixes for this preset.
# Consumed by check_dsl_entries.py.
allowed_l4_target_prefixes:
  - contracts/      # operation contract field
  - data/           # state truth field
  - response        # response body field
  - fixture         # fixture builder slot
  - stub_payload    # external-stub override payload
  - literal         # literal value
```

## Rules

- `/aibdd-plan` must resolve the target boundary profile before writing state
  truth or operation contract truth.
- If `state_specifier.format == dbml`, `/aibdd-plan` must delegate state/entity
  formulation to `/aibdd-form-entity-spec`; it must not hand-render YAML data
  models.
- If `operation_contract_specifier.format == openapi`, `/aibdd-plan` must
  delegate operation contract formulation to `/aibdd-form-api-spec`; it must not
  hand-render ad hoc operation-contract YAML for web-backend boundaries.
- The planner may still decide **what** entities, relationships, and aggregate
  hints are needed, and **what** endpoints / request / response fields are
  needed, but the profile's specifier skills own **how** those truths are
  serialized.
- `DATA_DIR` remains the boundary-owned state truth directory; the file format
  inside it is profile-specific.
- `CONTRACTS_DIR` remains the boundary-owned operation contract directory; the
  file format inside it is profile-specific.
- External boundaries may set `state_specifier.format: none`; planners must not
  write state truth for those boundaries.
- External or non-HTTP boundaries may set `operation_contract_specifier.format`
  to a different format or `none`; planners must not assume OpenAPI globally.
- `persistence_handler.handler_id` MUST appear in the preset's
  `routing_yml#handlers` map; consumers SHOULD verify this when running
  `check_handler_routing_consistency`.
- `persistence_handler.coverage_gate` controls whether `/aibdd-plan` enforces
  required-field coverage on persistence builders:
  - `not-null-columns` — backend DBML NOT-NULL coverage (web-service v1).
  - `deferred-v1` — gate is declared but not enforced in v1 (web-app v1).
  - `none` — gate is intentionally absent for this preset.
- `allowed_l4_target_prefixes` is the closed set of prefixes that
  `L4.{param,datatable,default,assertion}_bindings.*.target` strings may start
  with for this preset. Adding a new prefix is a profile-level change, not a
  per-project decision.
- If `component_contract_specifier.format == csf3`, `/aibdd-plan` must delegate
  Story-export formulation to `/aibdd-form-story-spec`; it must not hand-render
  ad hoc `*.stories.ts` files for web-frontend boundaries. Each component
  modeling unit in `$$boundary_delta.components` produces one
  `${FE_STORIES_DIR}/<identifier>.stories.ts` via DELEGATE.
- If `component_contract_specifier.skill == none`, `/aibdd-plan` must not
  produce Story files; `$$boundary_delta.components` must be empty or each
  entry marked `deferred: true`.
- Story files are **boundary contract truth** (per web-frontend invariant I4 —
  step-def locators derive from Story `args` accessible name); they are owned
  by `/aibdd-plan` via the specifier, NOT by `/aibdd-green-execute` Wave 1.
- The planner decides **what** components, Story states, accessible-name
  values, and play-step shapes are needed, but the specifier skill owns
  **how** the CSF3 file is rendered.

## Current Built-In Profiles

- `web-service`: backend HTTP service with persistent state expressed as DBML
  via `/aibdd-form-entity-spec`, and operation contracts expressed as OpenAPI
  via `/aibdd-form-api-spec`. Component contract specifier is `none` (no UI
  surface). Persistence handler is `aggregate-given` with `not-null-columns`
  coverage gate.
- `web-app`: frontend web application boundary verified via browser-level E2E
  tests (Playwright) against an in-process mock backend. Operation contract
  formulation is `/aibdd-form-api-spec` (OpenAPI authored by plan from frontend
  reasoning, or imported from upstream backend by placing api.yml in
  `${CONTRACTS_DIR}` before plan runs — plan reads it as truth and only extends
  it via `slice_list`). **Component contract formulation is
  `/aibdd-form-story-spec`** — plan reasons about component modeling units
  (identifier / import path / Story exports with accessible-name args) and
  DELEGATEs CSF3 rendering; Story files land under `${FE_STORIES_DIR}` and
  serve as the I4 binding anchor for ui-action / ui-readmodel-then DSL
  bindings. State formulation skill remains deferred (`none`) in v1;
  persistence handler is `mock-state-given` with `deferred-v1` coverage gate.
  Allowed L4 target prefixes additionally include `ui:`, `url:`, `route:`
  for UI / URL / route-map bindings.
