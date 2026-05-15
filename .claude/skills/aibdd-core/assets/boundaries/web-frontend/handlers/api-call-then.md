# Handler: api-call-then

## Role

`api-call-then` renders verification that a specific outgoing API call was emitted and matches expected shape (method, path-params, body, query, headers).

It belongs to:

- `sentence_part`: `api-call-then`
- `keywords`: `Then`

## Trigger Contract

Use this handler when the scenario must assert that the UI emitted a specific call — presence, count, and content shape. Schema conformance is automatic; this handler MUST NOT redeclare schema validation (see boundary invariant I2). Call selector (`operationId` + ordinal or predicate) comes from `L4.assertion_bindings`.

## Context Contract

Reads `mockApi.calls(operationId, since?)` and the OpenAPI operation truth (`L4.source_refs.contract`) for binding shape.

Writes no behavior state.

## Cross-Process Surface (I1)

`L4.callable_via` MUST resolve to the variant's call-recorder surface (`mockApi.calls`). The recorder runs inside the variant fixture closure on the test-runner side; step definitions MUST NOT inspect network traffic through `page.route` directly or `page.waitForRequest` for assertion.

## Schema Gate (I2)

Schema conformance is enforced by the mock layer when the call dispatches — `requestSchema.parse` failures already fail the test before this handler runs. Step bodies MUST NOT call `op.requestSchema.parse` again or otherwise re-validate the dispatched payload.

## Playwright Surface

Primary call: `const calls = mockApi.calls(operationId, since?)` then standard `expect(...)` against the returned `RecordedCall[]`.

### `RecordedCall` shape

```ts
interface RecordedCall {
  operationId: string;
  method: string;                       // 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  path: string;                         // resolved path, e.g. '/rooms/R-001/actions'
  pathParams: Record<string, string>;  // path template segments
  query: Record<string, string>;
  body: unknown;                        // parsed JSON; null for GET / DELETE
  headers: Record<string, string>;
  timestamp: number;                    // 0-based call ordinal within this scenario
}
```

### `since` semantics

`mockApi.calls(op, since?)` returns calls **at or after** index `since` within the per-operation call list:

- `calls('op')` → all calls (equivalent to `calls('op', 0)`).
- `calls('op', 1)` → second call onwards (skip the first).
- Use this to assert only the most-recent batch after a triggering UI action.

### Call selector

`L4.assertion_bindings` MUST resolve to one of:

| Selector kind | Form | Example |
|---|---|---|
| **Ordinal** | `{ kind: ordinal, index: <int> }` | First call: `calls[0]` |
| **Predicate** | `{ kind: predicate, where: <ShallowMatchObject> }` | Match `where.body.roomCode == 'R-001'` |
| **All-then-assert-count** | `{ kind: count, expected: <int> }` | `expect(calls).toHaveLength(2)` |

Predicate matches use shallow `toMatchObject` semantics on `body`, `pathParams`, `query`, or `headers`. Multiple matches → renderer MUST emit the assertion against the **first** match (predicate is a uniqueness assertion, not a filter) — failing this is `AMBIGUOUS_CALL_PREDICATE`.

### Typical shape

```ts
// Ordinal: assert the first createBorrowRequest call had specific body
const calls = mockApi.calls('createBorrowRequest');
expect(calls).toHaveLength(1);
expect(calls[0].body).toMatchObject({ roomCode: 'R-001' });

// Path-params: assert a POST /rooms/{roomCode}/actions call landed on the right room
const actions = mockApi.calls('postRoomAction');
expect(actions[0].pathParams).toEqual({ roomCode: 'R-001' });
expect(actions[0].body).toMatchObject({ action: 'join' });

// Since: assert only the call emitted after the latest UI click
const before = mockApi.calls('refreshRoom').length;
await page.getByRole('button', { name: 'Refresh' }).click();
const after = mockApi.calls('refreshRoom', before);
expect(after).toHaveLength(1);
```

## Forbidden

- Do not use `page.waitForRequest` or `page.route` listeners to capture calls — the canonical surface is `mockApi.calls`.
- Do not redeclare schema validation; the mock layer's I2 gate already enforces it.
- Do not assert UI state in this handler — use `ui-readmodel-then` / `success-failure`.
- Do not invent operationIds outside the OpenAPI contract truth.
- Do not assert raw URL strings; match through the operation's path template + path-params binding.
- Do not bypass the recorder by importing fetch interceptors from product code.
- Do not assert on call ordering across operations through `mockApi.calls` for a single operation — order across operations is variant-specific and not part of this handler.
