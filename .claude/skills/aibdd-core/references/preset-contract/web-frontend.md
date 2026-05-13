# web-frontend

## Rules

- Physical assets for this preset live under `aibdd-core/assets/boundaries/web-frontend/`.
- `handler-routing.yml` is the L4 policy SSOT for supported sentence parts, handler ids, keyword positions, and source-kind requirements.
- `handler-routing.yml` declares 4 boundary-level invariants (I1 cross-process surface, I2 OpenAPI schema auto-gate, I3 per-scenario reset, I4 Storybook contract granularity) at its top comment block; per-handler `l4_requirements` MUST NOT redeclare these invariants.
- `/aibdd-plan` DSL synthesis MUST classify each candidate clause against `handler-routing.yml.routes` (Gherkin `keyword` + route `semantic`) before emitting `L4.preset.{sentence_part,handler}`.
- Planner MUST cite the matched route or `(sentence_part, handler)` tuple in the derivation trace; do not keep a parallel generic markdown classification SSOT.
- `handlers/*.md` documents rendering slots and narrative guidance; it does not override `handler-routing.yml`. One file per handler id (listed below) MUST exist at `aibdd-core/assets/boundaries/web-frontend/handlers/<handler>.md`.
- `variants/*.md` defines runner/language/framework rendering contracts for a specific archetype, including the concrete cross-process mechanism required by invariant I1 and the per-scenario reset hook required by invariant I3.
- `shared-dsl-template.yml` defines canonical boundary-wide shared DSL entries (route precondition, viewport, success/failure feedback, time control).
- `L4.preset.name` MUST be `web-frontend`.
- For `web-frontend`, `L4.preset.sentence_part` MUST equal `L4.preset.handler`.
- Default variant is `nextjs-playwright` unless boundary truth declares another supported variant.
- `L4.preset.variant` MUST resolve to a file under `aibdd-core/assets/boundaries/web-frontend/variants/`.
- `L4.preset.handler` MUST be one of the supported handler ids listed below AND MUST resolve to a file under `aibdd-core/assets/boundaries/web-frontend/handlers/`.
- `L4.preset.sentence_part` MUST be supported by `handler-routing.yml`.
- Handler routing MUST be resolved from `handler-routing.yml`; handler docs may clarify rendering but MUST NOT override routing.
- Supported handler ids (Tier-1 — always required by any frontend boundary):
  - `route-given`
  - `viewport-control`
  - `mock-state-given`
  - `time-control`
  - `ui-action`
  - `success-failure`
  - `ui-readmodel-then`
- Supported handler ids (Tier-2 — opt-in per package):
  - `api-stub`
  - `url-then`
  - `api-call-then`
  - `mock-state-then`
- For `api-call-then`, the DSL entry MUST NOT redeclare per-call OpenAPI schema enforcement; schema conformance is auto-gated by the mock layer (boundary invariant I2).
- For UI handlers (`ui-action`, `ui-readmodel-then`), `L4.source_refs.component` MUST point to a Story export reference (e.g., `Button.stories.ts::Primary`), not the component file alone (boundary invariant I4).
- For mock-* and api-* handlers, `L4.callable_via` MUST resolve to the variant-defined cross-process surface (boundary invariant I1).
- Do not resolve `web-frontend` through a `frontend` or `web` alias.
- Do not synthesize handler docs from code or config key names.
- Do not let `L4.preset.handler` replace real L4 bindings, source refs, or callable mapping.
- Do not accept missing handler, missing variant, or unsupported sentence part silently.
- Do not collapse Tier-1 and Tier-2 handlers — a Tier-2 handler in `dsl.yml` requires the project test-strategy to declare its enablement.
- `check_handler_routing_consistency.py` SHOULD validate `aibdd-core/assets/boundaries/web-frontend/handler-routing.yml`.
- `check_frontend_preset_refs.py` SHOULD validate every DSL entry using `web-frontend` against the core routing file (parallel to `check_backend_preset_refs.py`).
- Missing `name`, `handler`, or `variant` assets MUST be fail-stop errors in `/aibdd-plan` and `/aibdd-red-execute`.

## Layout SSOT

`aibdd-core/assets/boundaries/web-frontend/` MUST contain the following layout. Both `/aibdd-plan` and `/aibdd-red-execute` enforce this; no consumer may relax or extend it.

| # | Component | Path | Cardinality |
|---|---|---|---|
| L1 | Routing SSOT | `handler-routing.yml` at preset root | exactly 1 |
| L2 | Handler narrative | `handlers/<handler>.md` per handler id referenced by any DSL `L4.preset.handler` | 1 per referenced handler |
| L3 | Variant rendering contract | `variants/<variant>.md` per variant id referenced by any DSL `L4.preset.variant` | 1 per referenced variant |
| L4 | Alias resolution | none — preset name MUST resolve to the directory name verbatim | n/a |

A missing component (L1 / L2 / L3) or an alias resolution attempt (L4) is a fail-stop error. Consumers MUST cite this section when enforcing layout.

### Preset Name Resolution Branches

- IF `L4.preset.name == web-frontend`:
  - RESOLVE assets from `aibdd-core/assets/boundaries/web-frontend/`.
- IF `L4.preset.name == frontend` OR `L4.preset.name == web`:
  - STOP with unsupported preset alias.
  - Do not map `frontend` or `web` to `web-frontend`.
- IF `L4.preset.name == web-backend`:
  - HANDOFF to `aibdd-core/references/preset-contract/web-backend.md`.
  - Do not let a single DSL entry mix `web-frontend` and `web-backend` source refs.
- IF `L4.preset.name` points to any folder not present under `aibdd-core/assets/boundaries/`:
  - STOP with missing preset asset.
- IF config value `FRONTEND_PRESET_CONTRACT_REF` points to this rule instance:
  - STILL read `L4.preset.name`; do not infer preset name from the config key.

### Handler Resolution Branches

- IF `L4.preset.handler` is missing:
  - STOP with missing handler.
- IF handler id is not listed in `handler-routing.yml`:
  - STOP with unsupported handler.
- IF handler id is a Tier-2 handler and the project test-strategy does not declare its enablement:
  - STOP with Tier-2 not enabled.
- IF `handlers/<handler>.md` is missing:
  - STOP with missing handler documentation.
- IF handler doc conflicts with `handler-routing.yml`:
  - TREAT `handler-routing.yml` as SSOT and report the conflict.
- IF handler id exists but required source kind is absent from the DSL entry:
  - STOP with source-kind mismatch.

### Sentence Part Resolution Branches

- IF `L4.preset.sentence_part` is missing:
  - STOP with missing sentence part.
- IF `sentence_part != handler` for `web-frontend`:
  - STOP with handler mismatch.
- IF sentence part is not listed in `handler-routing.yml`:
  - STOP with unsupported sentence part.
- IF keyword position conflicts with the routing policy:
  - STOP with keyword / sentence part mismatch.

### Variant Resolution Branches

V1 resolution order (highest precedence first):

- IF `L4.preset.variant` is present in the DSL entry:
  - RESOLVE `variants/<variant>.md`.
- ELSE IF `L4.preset.variant` is absent:
  - USE `nextjs-playwright` (the only v1 variant for `web-frontend`; selected by `/aibdd-plan` SKILL.md Phase 6 step 8 when `PRESET_KIND == web-frontend`).
- IF the selected variant file is missing:
  - STOP with missing variant.
- IF the variant does not support the handler or source kind required by routing:
  - STOP with variant incompatibility.
- IF the variant does not declare a cross-process mechanism for invariant I1, a per-scenario reset hook for I3, OR a Story-export-aware locator rule for I4:
  - STOP with variant invariant gap.

**V1 caveat — boundary-truth variant default is not implemented.** Neither `boundary.yml` nor `arguments.yml` carries a `variant_default` / `preset.variant` key. Per-DSL-entry override via `L4.preset.variant` is the only declaration site; everything else falls through to the hardcoded `nextjs-playwright` default. A future boundary.yml key `boundary.preset.variant_default` is reserved but not parsed. Until then, projects that need a non-default variant MUST set `L4.preset.variant` on every relevant DSL entry.

### Binding Boundary Branches

- IF a handler provides rendering slots:
  - USE the slots to render step definitions.
- IF a handler tries to replace `L4.source_refs`, `param_bindings`, `assertion_bindings`, `datatable_bindings`, or `default_bindings`:
  - REJECT because handler docs cannot replace DSL physical truth.
- IF a handler needs extra stack instructions:
  - READ project-owned runtime refs, not this preset rule instance.
- IF a UI handler binding (`ui-action` / `ui-readmodel-then`) supplies `L4.source_refs.component` pointing only to a component file (no `::StoryExport` suffix):
  - REJECT with Storybook contract granularity violation (I4).
- IF a mock-* / api-* handler binding declares `L4.callable_via` resolving to a same-process module path or `page.route` pattern instead of the variant-declared cross-process surface:
  - REJECT with cross-process surface violation (I1).

## Examples

### Good: complete preset tuple — UI action

```yaml
L4:
  source_refs:
    component: src/components/borrow-request/BorrowRequestForm.stories.ts::Default
    route: page-plan.md#/borrow-requests/new
  param_bindings:
    button_label:
      kind: literal
      target: literal:ui.button.name
  preset:
    name: web-frontend
    sentence_part: ui-action
    handler: ui-action
    variant: nextjs-playwright
```

Why good:

- Preset name maps directly to `aibdd-core/assets/boundaries/web-frontend/`.
- Sentence part and handler are aligned.
- Variant resolves to `variants/nextjs-playwright.md`.
- `source_refs.component` references a specific Story export (I4 satisfied).
- Real L4 bindings remain in the DSL entry.

### Good: mock state seed

```yaml
L4:
  datatable_bindings:
    application_id:
      target: src/lib/schemas/borrow-request.ts#BorrowRequestSchema.id
    status:
      target: src/lib/schemas/borrow-request.ts#BorrowRequestSchema.status
  preset:
    name: web-frontend
    sentence_part: mock-state-given
    handler: mock-state-given
    variant: nextjs-playwright
```

Why good:

- `mock-state-given` is a supported routing handler (Tier-1).
- Datatable binding identity comes from data-model truth (Zod schema).
- Implicit cross-process via variant-defined `/__test__/seed` (I1 satisfied at variant layer).

### Good: api-call-then asserting outgoing call shape

```yaml
L4:
  assertion_bindings:
    operation:
      kind: call_selector
      target: calls:$[?(@.operationId=="createBorrowRequest")][0]
    body_amount:
      kind: call_body
      target: calls:$[0].request.body.amount
      value: 50000
  source_refs:
    contract: contracts/borrow-request.yml#/paths/~1borrow-requests/post
  preset:
    name: web-frontend
    sentence_part: api-call-then
    handler: api-call-then
    variant: nextjs-playwright
```

Why good:

- Asserts on call presence + body shape via the call-recorder side channel.
- Schema conformance is NOT redeclared (I2 enforced layer-side).
- Tier-2 handler used; project test-strategy must declare `api-call-then` enablement.

### Bad: `frontend` alias

```yaml
L4:
  preset:
    name: frontend
    sentence_part: ui-action
    handler: ui-action
    variant: nextjs-playwright
```

Why bad:

- `frontend` is not a valid preset folder name.
- There is no alias from `frontend` to `web-frontend`.

Better:

```yaml
L4:
  preset:
    name: web-frontend
    sentence_part: ui-action
    handler: ui-action
    variant: nextjs-playwright
```

### Bad: handler mismatch

```yaml
L4:
  preset:
    name: web-frontend
    sentence_part: ui-readmodel-then
    handler: mock-state-then
    variant: nextjs-playwright
```

Why bad:

- For `web-frontend`, sentence part and handler must match.
- DOM-rendered value verification and mock store mutation verification use different handlers.

### Bad: missing variant

```yaml
L4:
  preset:
    name: web-frontend
    sentence_part: success-failure
    handler: success-failure
```

Why bad when no boundary default exists:

- The selected rendering contract is ambiguous.
- `/aibdd-plan` must choose an explicit supported variant or use the declared default.

Better:

```yaml
L4:
  preset:
    name: web-frontend
    sentence_part: success-failure
    handler: success-failure
    variant: nextjs-playwright
```

### Bad: handler replaces L4 bindings

```yaml
L4:
  preset:
    name: web-frontend
    sentence_part: ui-action
    handler: ui-action
    variant: nextjs-playwright
  handler_notes: "click the primary submit button on the credit application form"
```

Why bad:

- Handler notes are prose and cannot replace `source_refs.component` or parameter bindings.
- `/aibdd-red-execute` would have to parse prose to synthesize a legal red.

Better:

```yaml
L4:
  source_refs:
    component: src/components/borrow-request/BorrowRequestForm.stories.ts::Default
    route: page-plan.md#/borrow-requests/new
  param_bindings:
    button_label:
      kind: literal
      target: literal:ui.button.name
  preset:
    name: web-frontend
    sentence_part: ui-action
    handler: ui-action
    variant: nextjs-playwright
```

### Bad: unsupported handler id

```yaml
L4:
  preset:
    name: web-frontend
    sentence_part: dom-event-then
    handler: dom-event-then
    variant: nextjs-playwright
```

Why bad:

- `dom-event-then` is not listed in `handler-routing.yml`.
- Consumers must fail-stop instead of inventing a handler.

### Bad: Story export granularity violation (I4)

```yaml
L4:
  source_refs:
    component: src/components/borrow-request/BorrowRequestForm.tsx
  preset:
    name: web-frontend
    sentence_part: ui-action
    handler: ui-action
    variant: nextjs-playwright
```

Why bad:

- `source_refs.component` points only to the component file, not a specific Story export.
- Locator derivation cannot resolve the per-state accessible name without the Story args.
- Boundary invariant I4 violated.

Better: append `::<StoryExport>` to bind to the precise state — see "Good: complete preset tuple — UI action" above.

### Bad: cross-process surface violation (I1)

```yaml
L4:
  callable_via: src/mocks/store.ts::seedApplications
  preset:
    name: web-frontend
    sentence_part: mock-state-given
    handler: mock-state-given
    variant: nextjs-playwright
```

Why bad:

- `callable_via` resolves to a same-process module path; the test runner cannot reach it from the browser context.
- The variant requires resolution through the cross-process surface (e.g., `POST /__test__/seed`).
- Boundary invariant I1 violated.

### Bad: redeclared schema gate (I2)

```yaml
L4:
  assertion_bindings:
    schema_valid:
      kind: schema_check
      target: contracts/borrow-request.yml#/components/schemas/BorrowRequestPayload
      value: true
  preset:
    name: web-frontend
    sentence_part: api-call-then
    handler: api-call-then
    variant: nextjs-playwright
```

Why bad:

- `api-call-then` MUST NOT redeclare schema enforcement; the mock layer auto-gates every dispatch.
- Per-scenario `schema_valid` assertions create the false impression that some scenarios opt out of validation.
- Boundary invariant I2 violated.

Better: drop the `schema_valid` assertion. Schema enforcement is implicit; assert on call presence, count, or non-schema body shape only.
