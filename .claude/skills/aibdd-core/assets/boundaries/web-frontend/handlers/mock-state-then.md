# Handler: mock-state-then

## Role

`mock-state-then` renders verification that the in-process mock backend store was mutated as expected, when the UI does not render the mutation.

It belongs to:

- `sentence_part`: `mock-state-then`
- `keywords`: `Then`

## Trigger Contract

Use this handler when the scenario must verify a mock-store mutation that is not user-visible (audit fields, server-only flags, soft-delete tombstone, denormalized counters). When the mutation IS rendered, prefer `ui-readmodel-then`. Lookup identity comes from `L4.param_bindings` / `datatable_bindings`; expected values map to data-model fields per `L4.assertion_bindings`.

## Context Contract

Reads `mockApi.inspect<Store>(where?)` for the mutated entity shape, and `L4.source_refs.data` (Zod schema) for valid field targets.

Writes no behavior state.

## Cross-Process Surface (I1)

`L4.callable_via` MUST resolve to a `mockApi.inspect*` fixture method. Step definitions MUST NOT read the fixture closure store through any other path (no direct import of the store from product or test code).

## Playwright Surface

Primary call: `const entity = mockApi.inspect<Entity>(where?)` then standard `expect(...)` against the returned entity or entity collection.

Typical shape:

```ts
const room = mockApi.inspectRoom('R-001');
expect(room).toBeDefined();
expect(room?.seatsTaken).toBe(3);
```

## Forbidden

- Do not assert UI state — use `ui-readmodel-then` for visible state.
- Do not call `page.*` — this handler does not touch the DOM.
- Do not mutate the mock store in a Then step (no `mockApi.seed*` here).
- Do not invent entity fields outside the data-model Zod schema in `L4.source_refs.data`.
- Do not import the fixture's closure store from product code.
- Do not query a database — the boundary owns no real persistence at the frontend layer.
- Do not assert on entity shape that lives outside the variant fixture closure (e.g., backend service state).
