# Handler: api-stub

## Role

`api-stub` renders a per-scenario override of the in-process mock backend's response behavior for a specific `operationId`.

It belongs to:

- `sentence_part`: `api-stub`
- `keywords`: `Given`

## Trigger Contract

Use this handler when the sentence overrides per-scenario response behavior — next response status, body fixture, latency, response sequence, or fault profile — for a specific `operationId`. Distinct from `mock-state-given`, which seeds data; `api-stub` seeds behavior. The override target operation comes from `L4.source_refs.contract`.

## Context Contract

Reads `mockApi` (fixture-injected) and the OpenAPI operation truth (when a provider contract exists) for response shape validation.

Writes a queued override into the mock layer through `mockApi.override(operationId, response, sequence?)`. The override lives in the variant fixture closure (see boundary invariant I1) and applies until the next per-scenario reset.

## Cross-Process Surface (I1)

`L4.callable_via` MUST resolve to `mockApi.override`. The fixture's `page.route` handler consumes the queued override on next dispatch; step definitions MUST NOT touch `page.route` directly.

## Per-Scenario Reset (I3)

The queued override is cleared automatically when the fixture is torn down (`fixture scope = test`). Step definitions MUST NOT clear the queue manually.

## Schema Gate (I2) Interaction

The variant's mock layer Zod-validates every outgoing response body against the operation's response schema. An override whose body violates that schema fails the test automatically at dispatch time — this is the boundary invariant, not a handler-level check.

## Playwright Surface

Primary call: `mockApi.override(operationId, { status, body, headers? }, sequence?)` (synchronous closure mutation). The override consumption is performed by the fixture's `page.route` handler; step definitions only enqueue.

## Forbidden

- Do not call `page.route` directly from a step definition.
- Do not stub through MSW or any in-app mock module — the canonical surface is the fixture closure.
- Do not invent operationIds outside the OpenAPI contract truth.
- Do not invent response field names outside the operation's response schema.
- Do not use this handler to seed persisted mock state — use `mock-state-given` instead.
- Do not bypass schema validation by overriding with non-conforming bodies; the mock layer's schema gate (I2) will still fail the test.
- Do not register additional reset hooks; fixture scope owns reset.
