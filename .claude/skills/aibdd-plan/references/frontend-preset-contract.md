# Frontend Preset Contract

## Physical assets (boundary-wise)

Reusable routing, handler docs, variants, and schemas for the frontend preset are maintained under `aibdd-core` at:

`aibdd-core/assets/boundaries/web-frontend/` (see `README.md` in that folder).

**L4 policy SSOT:** per-handler `required_source_kinds`, optional `optional_source_kinds`, and `l4_requirements` live under `handler-routing.yml` → `handlers.<handler-id>`. Files in `handlers/*.md` describe rendering and narrative only; they are not authoritative for L4 binding rules.

**Boundary-level invariants:** `handler-routing.yml`'s top comment block declares 4 invariants (I1 cross-process surface, I2 OpenAPI schema auto-gate, I3 per-scenario reset, I4 Storybook contract granularity). Per-handler `l4_requirements` MUST NOT redeclare these invariants; consumers (this skill, `/aibdd-red-execute`) enforce them at the variant layer.

`/aibdd-plan` must not materialize a boundary-local `sentence-parts/inventory.yml` or package-local sentence-parts catalog. The frontend preset already owns the supported sentence part ids, handler ids, keyword positions, and L4 source-kind policy through `handler-routing.yml`.

## Layout SSOT (cross-ref)

The boundary directory layout (routing yml + handler narrative + variant contract + no alias) is normatively declared in [`aibdd-core::preset-contract/web-frontend.md`](aibdd-core::preset-contract/web-frontend.md) § Layout SSOT. `/aibdd-plan` MUST enforce that section before emitting any `L4.preset` block referencing this preset; `/aibdd-red-execute` Phase 3 § preset registry assertion cites the same SSOT.

## Primary Stack

Frontend DSL entries target the `web-frontend` preset first. The default variant is `nextjs-playwright` unless the boundary truth explicitly declares another supported variant.

## Handler References

Reusable frontend handlers (for `web-frontend`, `L4.preset.sentence_part` **must equal** `L4.preset.handler`; ids match `aibdd-core/assets/boundaries/web-frontend/handler-routing.yml`):

### Tier-1 — always required (7)

| Handler | Gherkin position | Purpose |
|---|---|---|
| `route-given` | Given / Background | Land the browser context on a specific application route as a scenario precondition. |
| `viewport-control` | Given / When | Control browser viewport dimensions or device emulation profile. |
| `mock-state-given` | Given / Background | Seed the in-process mock backend store with persistent state via the variant-defined cross-process surface. |
| `time-control` | Given / When | Control browser-visible time for time-dependent UI behavior. |
| `ui-action` | Given / When | Drive a UI interaction through the rendered surface — click, fill, select, upload, keyboard, drag, programmatic navigation. |
| `success-failure` | Then | Verify the success-or-failure feedback class surfaced to the user (toast, inline error, banner, status pill). |
| `ui-readmodel-then` | Then | Verify a rendered UI value, label, role, attribute, or count is observable on the page DOM. |

### Tier-2 — opt-in per package (4)

| Handler | Gherkin position | Purpose |
|---|---|---|
| `api-stub` | Given | Override the in-process mock backend's per-scenario behavior for a specific operationId. |
| `url-then` | Then | Verify URL state — pathname, query string parameters, hash fragment — when URL is the load-bearing observable. |
| `api-call-then` | Then | Verify outgoing API call presence, count, and shape via the mock-call-recorder side channel. Schema conformance is auto-gated layer-side (I2). |
| `mock-state-then` | Then | Verify the in-process mock backend store was mutated, when the UI does not render the mutation. |

## DSL Reference Form

Frontend entries should include an L4 preset block or equivalent fields:

```yaml
preset:
  name: web-frontend
  sentence_part: ui-action
  handler: ui-action
  variant: nextjs-playwright
```

For UI handlers (`ui-action`, `ui-readmodel-then`), `L4.source_refs.component` MUST point to a Story export reference (e.g., `Button.stories.ts::Primary`), not the component file alone (boundary invariant I4).

For mock-* and api-* handlers, `L4.callable_via` MUST resolve to the variant-defined cross-process surface (boundary invariant I1) — `nextjs-playwright` declares this as `/__test__/*` HTTP endpoints.

## Relationship to Physical Surface

The preset handler does not replace L4 physical mapping. It tells `/aibdd-red-execute` which reusable step-definition pattern to use while L4 still provides operation, verifier, binding, and source references. The variant declares the concrete cross-process mechanism, schema-gate implementation, and Storybook locator derivation rule.

## Deterministic Gates

The frontend preset is valid only when both checks pass:

- `check_handler_routing_consistency.py aibdd-core/assets/boundaries/web-frontend/handler-routing.yml`
- `check_frontend_preset_refs.py <handler-routing.yml> <dsl.yml> [<shared-dsl.yml>...]`

The first check (already generic; reused from backend pipeline) validates the preset asset itself. The second (frontend-specific twin of `check_backend_preset_refs.py`) validates every frontend DSL entry against that asset, including `preset.name`, `sentence_part`, `handler`, and `variant`. Tier-2 enablement is verified against the project's `test-strategy.yml`.

## Configuration

Projects using `web-frontend` preset MUST declare in `arguments.yml`:

```yaml
PRESET_KIND: web-frontend
FRONTEND_PRESET_CONTRACT_REF: aibdd-core::preset-contract/web-frontend.md
```

Projects using only `web-backend` preset may omit `PRESET_KIND` — the default falls back to `web-backend` for backward compatibility. Mixed-preset projects (one repo with both UI and backend boundaries) require separate plan packages until per-package boundary-kind dispatch lands in v2.
