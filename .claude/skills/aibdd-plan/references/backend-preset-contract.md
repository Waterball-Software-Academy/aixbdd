# Backend Preset Contract

## Physical assets (boundary-wise)

Reusable routing, handler docs, variants, and schemas for the backend preset are maintained under `aibdd-core` at:

`aibdd-core/assets/boundaries/web-backend/` (see `README.md` in that folder).

**L4 policy SSOT:** per-handler `required_source_kinds`, optional `optional_source_kinds`, and `l4_requirements` live under `handler-routing.yml` → `handlers.<handler-id>`. Files in `handlers/*.md` describe rendering and narrative only; they are not authoritative for L4 binding rules.

`/aibdd-plan` must not materialize a boundary-local `sentence-parts/inventory.yml`
or package-local sentence-parts catalog. The backend preset already owns the
supported sentence part ids, handler ids, keyword positions, and L4 source-kind
policy through `handler-routing.yml`.

## Layout SSOT (cross-ref)

The boundary directory layout (routing yml + handler narrative + variant contract + no alias) is normatively declared in [`aibdd-core::preset-contract/web-backend.md`](aibdd-core::preset-contract/web-backend.md) § Layout SSOT. `/aibdd-plan` MUST enforce that section before emitting any `L4.preset` block referencing this preset; `/aibdd-red-execute` Phase 3 § preset registry assertion cites the same SSOT.

## Primary Stack

Backend DSL entries target the `web-backend` preset first. The default variant is `python-e2e` unless the boundary truth explicitly declares another supported variant.

## Handler References

Reusable backend handlers (for `web-backend`, `L4.preset.sentence_part` **must equal** `L4.preset.handler`; ids match `aibdd-core/assets/boundaries/web-backend/handler-routing.yml`):

| Handler | Gherkin position | Purpose |
|---|---|---|
| `aggregate-given` | Given / Background | Prepare aggregate state through a test loader or database fixture. |
| `http-operation` | Given / When | Invoke HTTP operations; method and path come from the operation contract. |
| `success-failure` | Then | Verify HTTP status, exception, or failure mode. |
| `readmodel-then` | Then | Verify response body fields from the captured response. |
| `aggregate-then` | Then | Verify persisted aggregate state. |
| `time-control` | Given / When | Control boundary-visible time via test strategy. |
| `external-stub` | Given | Stub backend-visible external resources via test strategy. |

## DSL Reference Form

Backend entries should include an L4 preset block or equivalent fields:

```yaml
preset:
  name: web-backend
  sentence_part: http-operation
  handler: http-operation
  variant: python-e2e
```

## Relationship to Physical Surface

The preset handler does not replace L4 physical mapping. It tells `/aibdd-red` which reusable step-definition pattern to use while L4 still provides operation, verifier, binding, and source references.

## Deterministic Gates

The backend preset is valid only when both checks pass:

- `check_handler_routing_consistency.py aibdd-core/assets/boundaries/web-backend/handler-routing.yml`
- `check_backend_preset_refs.py <handler-routing.yml> <dsl.yml> [<shared-dsl.yml>...]`

The first check validates the preset asset itself. The second validates every
backend DSL entry against that asset, including `preset.name`, `sentence_part`,
`handler`, and `variant`.
