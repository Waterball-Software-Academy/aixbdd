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

## Current Built-In Profile

- `web-service`: backend HTTP service with persistent state expressed as DBML
  via `/aibdd-form-entity-spec`, and operation contracts expressed as OpenAPI
  via `/aibdd-form-api-spec`.
