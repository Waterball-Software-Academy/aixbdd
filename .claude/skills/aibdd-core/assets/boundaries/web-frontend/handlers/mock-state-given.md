# Handler: mock-state-given

## Role

`mock-state-given` renders seeded state into the in-process mock backend store before the scenario's target operation.

It belongs to:

- `sentence_part`: `mock-state-given`
- `keywords`: `Given`, `Background`

## Trigger Contract

Use this handler when the sentence describes mock-backend persisted state that must exist before the target UI interaction. The seeded shape comes from `L4.source_refs.data` (Zod schema or data-model truth). Bindings MUST cover all NOT-NULL fields; defaults come from fixture truth, not from binding-time invention.

## Context Contract

Reads `mockApi` (fixture-injected), `L4.source_refs.data` (Zod schema), and any earlier scenario memo for natural keys required by later operation / verification steps.

Writes mock-store entries through `mockApi.seed<Entity>(input)`. The store lives in the variant fixture closure on the test-runner side (see boundary invariant I1).

## Cross-Process Surface (I1)

`L4.callable_via` MUST resolve to a `mockApi.seed*` fixture method. The fixture itself owns `page.route` registration; step definitions only call the synchronous `mockApi` API.

## Per-Scenario Reset (I3)

Reset is automatic via fixture scope (`fixture scope = test`). Step definitions MUST NOT register `Before` / `After` hooks to clear or reseed the store.

## Playwright Surface

Primary call: `mockApi.seed<Entity>(input)` (synchronous closure mutation). The fixture's `page.route` handler reads the closure store on next dispatch and Zod-validates outgoing responses against the OpenAPI operation schema (boundary invariant I2).

## Forbidden

- Do not call `page.route` directly from a step definition.
- Do not import the fixture's closure store from product code (`src/**`).
- Do not invent entity fields outside the Zod schema in `L4.source_refs.data`.
- Do not seed through HTTP — the fixture closure is in-process and synchronous.
- Do not use this handler for per-call response override; use `api-stub` instead.
- Do not register additional `Before` hooks to clear or reseed state.
- Do not place mock layer code inside the app under test (`src/mocks/**` is forbidden).
