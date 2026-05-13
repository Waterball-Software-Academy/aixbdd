# Variant: nextjs-playwright

## Role

`nextjs-playwright` renders web-frontend preset handlers into TypeScript step definitions executed by `playwright-bdd` against a running Next.js app, with Storybook serving as component contract and a Playwright `page.route`-based mock layer holding state in the test-runner-side fixture closure.

This variant only defines rendering mechanics. It does not classify sentence parts and does not select handlers.

## Runtime Contract

- Language: TypeScript 5+
- App framework: Next.js 16 (App Router)
- BDD framework: `playwright-bdd` (≥ 8.5)
- Browser driver: Playwright (≥ 1.45 — required for `page.clock`)
- Component contract: Storybook (≥ 10) — Story export is the binding target (see boundary invariant I4)
- Schema runtime: Zod 4
- Mock layer: Playwright `page.route` interception in the fixture closure (`features/steps/fixtures.ts`); mock state lives in the test-runner Node process, not the dev server. **No** in-app mock module under `src/mocks/**`. **No** HTTP `/__test__/*` Route Handlers in the dev server.
- Mock control surface: in-process fixture API (`mockApi.{seedXxx, reset, inspectXxx, override, calls}`) consumable synchronously by step definitions (see boundary invariant I1)
- Time control: Playwright 1.45+ `page.clock`
- Server vs test process: Playwright spawns the Next.js dev server via `webServer` config (separate Node process). The cross-process boundary between browser and test-runner is bridged by `page.route` (DevTools protocol), NOT by HTTP Route Handlers in the dev server.
- API host separation: `NEXT_PUBLIC_API_BASE_URL` MUST resolve to a host distinct from the Next.js dev server host (e.g., dev = `http://localhost:3000`, API = `http://localhost:4000`). This prevents `page.route` glob from intercepting page navigations.

## Required Test-Side Scaffolding

The variant requires the test side to ship the following module. Its absence is a render-blocking gap; missing truth is not a legal red (see Legal Red Expectation).

| Module | Role |
|---|---|
| `features/steps/fixtures.ts` | `playwright-bdd` `test.extend` adds `mockApi` fixture (closure-local mock store + `page.route` registrations) and registers per-scenario lifecycle (fixture scope = test → automatic reset). Exports `Given/When/Then` from `createBdd(test)`. |

The app under test (`src/**`) MUST NOT contain mock layer code. `src/lib/api-client.ts` is a pure `fetch()` wrapper with no transport switch. `src/app/__test__/**` MUST NOT exist.

## Mock Control Surface (Fixture API)

All operations are synchronous closure mutations (no async HTTP). Per-scenario reset is automatic via fixture scope.

| Method | Backs handler | Signature |
|---|---|---|
| `mockApi.seed<E>(input)` | `mock-state-given` | `input: EntityShape` — all NOT-NULL Zod fields required; `z.optional()` fields may be omitted; `z.nullable()` fields accept `null`. Returns `void`. |
| `mockApi.inspect<E>(where?)` | `mock-state-then` | `where?: Partial<E>` — shallow-equality filter on the closure store; omit to return all entries. Returns `E \| E[]`. |
| `mockApi.override(op, response, sequence?)` | `api-stub` | `op: string` operationId; `response: { status: number; body: unknown; headers?: Record<string,string> }`; `sequence?: number` — 0-based call ordinal: this override applies when `mockApi.calls(op).length == sequence`; omit = applies on the next call only. Returns `void`. |
| `mockApi.calls(op, since?)` | `api-call-then` | `op: string` operationId; `since?: number` — 0-based call ordinal; returns calls at index ≥ `since`; omit = all calls in this scenario. Returns `RecordedCall[]`. |
| `mockApi.reset()` | per-scenario reset (I3) | No args. Clears closure store and call recorder. Usually unnecessary — fixture scope handles it automatically. Returns `void`. |

`RecordedCall` type:

```ts
interface RecordedCall {
  operationId: string;
  method: string;                       // 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  path: string;                         // resolved path, e.g. '/rooms/R-001/actions'
  pathParams: Record<string, string>;  // path template segments, e.g. { roomCode: 'R-001' }
  query: Record<string, string>;
  body: unknown;                        // parsed JSON or null (GET / DELETE)
  headers: Record<string, string>;
  timestamp: number;                    // 0-based call ordinal within this scenario
}
```

The fixture registers a single `page.route(API_HOST + '/**', handler)` that dispatches all operations by `method × path` regex. Each dispatch branch Zod-validates outgoing responses (boundary invariant I2).

## Required Test Fixture Shape (`features/steps/fixtures.ts`)

```ts
/* eslint-disable react-hooks/rules-of-hooks -- Playwright fixture `use` callback is not a React Hook */
import { test as base, createBdd } from 'playwright-bdd';
import { CreateRoomBodySchema, CreateRoomResponseSchema, GetRoomResponseSchema } from '@/lib/schemas/room';

interface MockApi {
  reset(): void;
  // domain-specific seed/inspect methods — one method per entity, camelCase entity name:
  seedRoom(input: { roomCode: string; seatsTaken: number; capacity?: number }): void;
  inspectRoom(code: string): RoomState | undefined;
  // tier-2 only:
  override(operationId: string, response: { status: number; body: unknown; headers?: Record<string, string> }, sequence?: number): void;
  calls(operationId: string, since?: number): RecordedCall[];
}

const API_HOST = 'http://localhost:4000'; // distinct from Next.js dev (localhost:3000)

export const test = base.extend<{ mockApi: MockApi }>({
  mockApi: async ({ page }, use) => {
    const store = new Map<string, RoomState>();
    const recorder: RecordedCall[] = [];
    const overrides = new Map<string, Array<{ sequence?: number; response: OverrideResponse }>>();

    // Helper: pop a matching override for (op, callIndex) if one is queued
    const popOverride = (op: string, callIndex: number) => {
      const queue = overrides.get(op);
      if (!queue) return undefined;
      const idx = queue.findIndex(o => o.sequence === undefined || o.sequence === callIndex);
      return idx >= 0 ? queue.splice(idx, 1)[0].response : undefined;
    };

    // Single page.route covers every API operation; dispatch is by method × path regex.
    await page.route(`${API_HOST}/**`, async (route) => {
      const req = route.request();
      const method = req.method();
      const url = new URL(req.url());
      const path = url.pathname;
      const query = Object.fromEntries(url.searchParams);
      const headers = req.headers();

      // ── POST /rooms ─────────────────────────────────────────
      if (method === 'POST' && path === '/rooms') {
        const op = 'createRoom';
        const body = req.postDataJSON() as unknown;
        CreateRoomBodySchema.parse(body);                                              // I2 request gate
        const callIndex = recorder.filter(c => c.operationId === op).length;
        recorder.push({ operationId: op, method, path, pathParams: {}, query, body, headers, timestamp: recorder.length });

        const override = popOverride(op, callIndex);
        if (override) {
          await route.fulfill({ status: override.status, contentType: 'application/json', body: JSON.stringify(override.body), headers: override.headers });
          return;
        }
        const parsed = body as { roomCode: string };
        const room: RoomState = { roomCode: parsed.roomCode, seatsTaken: 0 };
        store.set(room.roomCode, room);
        const resp = { roomCode: room.roomCode };
        CreateRoomResponseSchema.parse(resp);                                          // I2 response gate
        await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify(resp) });
        return;
      }

      // ── GET /rooms/:roomCode ────────────────────────────────
      const getRoomMatch = path.match(/^\/rooms\/([^/]+)$/);
      if (method === 'GET' && getRoomMatch) {
        const op = 'getRoom';
        const roomCode = getRoomMatch[1];
        const callIndex = recorder.filter(c => c.operationId === op).length;
        recorder.push({ operationId: op, method, path, pathParams: { roomCode }, query, body: null, headers, timestamp: recorder.length });

        const override = popOverride(op, callIndex);
        if (override) {
          await route.fulfill({ status: override.status, contentType: 'application/json', body: JSON.stringify(override.body), headers: override.headers });
          return;
        }
        const room = store.get(roomCode);
        if (!room) {
          await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ error: 'room not found' }) });
          return;
        }
        GetRoomResponseSchema.parse(room);                                             // I2 response gate
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(room) });
        return;
      }

      // Unknown operation — fail explicitly rather than passing through to the real API.
      await route.abort('failed');
    });

    const api: MockApi = {
      reset: () => { store.clear(); recorder.length = 0; overrides.clear(); },
      seedRoom: (input) => store.set(input.roomCode, { roomCode: input.roomCode, seatsTaken: input.seatsTaken, capacity: input.capacity ?? 4 }),
      inspectRoom: (code) => store.get(code),
      override: (op, response, sequence) => {
        if (!overrides.has(op)) overrides.set(op, []);
        overrides.get(op)!.push({ sequence, response });
      },
      calls: (op, since) => recorder.filter(c => c.operationId === op).slice(since ?? 0),
    };
    await use(api);
  },
});

export const { Given, When, Then } = createBdd(test);
```

The fixture's closure (`store`, `page.route` registrations) is automatically recreated per test (fixture scope = test). This is the **single** legitimate per-scenario reset hook (boundary invariant I3). Step files MUST NOT invent additional reset paths.

## Step File Layout

Directories under `features/steps/<function-package-or-domain>/` map one-to-one to handlers in [`../handler-routing.yml`](../handler-routing.yml) (hyphen in handler name preserved).

```text
features/
  steps/
    fixtures.ts
    <function-package-or-domain>/
      route-given/
      viewport-control/
      mock-state-given/
      time-control/
      ui-action/
      success-failure/
      ui-readmodel-then/
      api-stub/                # only if Tier-2 enabled in this package
      url-then/                # only if Tier-2 enabled
      api-call-then/           # only if Tier-2 enabled
      mock-state-then/         # only if Tier-2 enabled
```

One generated step pattern maps to one `.ts` file unless an existing shared common step already owns the exact matcher. Shared matchers outside the 11 preset handlers are project-specific and are not part of this preset SSOT.

## Playwright-BDD Matcher Contract

- Use `Given`, `When`, or `Then` imported from `./fixtures` (never directly from `playwright-bdd` — that would re-instantiate `createBdd(test)` and break fixture sharing).
- First fixture argument receives `{ page, request, mockApi, ... }` destructured.
- Additional positional arguments are derived from `L1` placeholders.
- Integer placeholders use `{int}`.
- Float placeholders use `{float}`.
- String placeholders use `{string}` (quoted in the matcher).

## Per-Handler Playwright API Mapping

Each handler's full Playwright surface — allowed verbs, assertion APIs, locator derivation rules, and Forbidden patterns — lives in `../handlers/<handler>.md` § Playwright Surface. This variant section only declares **stack-level constraints** that apply across all handlers; handler-local mapping MUST NOT be duplicated here.

### Stack-level constraints (apply to every handler below)

| Constraint | Authority |
|---|---|
| Playwright ≥ 1.45 (required for `page.clock`) | Runtime Contract (top of this file) |
| `baseURL` resolution via `playwright.config.ts` | Playwright config |
| Named viewport profiles resolved from `test-strategy.yml#viewport_profiles` | Project test strategy |
| `Given` / `When` / `Then` imported from `./fixtures` only (never directly from `playwright-bdd`) | §Playwright-BDD Matcher Contract |
| `mockApi.*` fixture API is the sole cross-process surface (I1) | §Mock Control Surface |
| Zod-validated fulfillment / response bodies (I2) | §Schema Auto-Gate |
| Story export as locator source (I4) | §Storybook Binding |

### Handler narrative index (cross-link only)

| Tier | Handler | Narrative |
|---|---|---|
| T1 | `route-given` | [`../handlers/route-given.md`](../handlers/route-given.md) |
| T1 | `viewport-control` | [`../handlers/viewport-control.md`](../handlers/viewport-control.md) |
| T1 | `mock-state-given` | [`../handlers/mock-state-given.md`](../handlers/mock-state-given.md) |
| T1 | `time-control` | [`../handlers/time-control.md`](../handlers/time-control.md) |
| T1 | `ui-action` | [`../handlers/ui-action.md`](../handlers/ui-action.md) |
| T1 | `success-failure` | [`../handlers/success-failure.md`](../handlers/success-failure.md) |
| T1 | `ui-readmodel-then` | [`../handlers/ui-readmodel-then.md`](../handlers/ui-readmodel-then.md) |
| T2 | `api-stub` | [`../handlers/api-stub.md`](../handlers/api-stub.md) |
| T2 | `url-then` | [`../handlers/url-then.md`](../handlers/url-then.md) |
| T2 | `api-call-then` | [`../handlers/api-call-then.md`](../handlers/api-call-then.md) |
| T2 | `mock-state-then` | [`../handlers/mock-state-then.md`](../handlers/mock-state-then.md) |

## Schema Auto-Gate (Boundary Invariant I2 — Concrete Impl)

The fixture's `page.route` handler wraps every fulfillment:

```ts
await page.route(`${API_HOST}/<path>`, async (route) => {
  const req = route.request();
  const op = openApiOperations[/* resolve from method × path */];
  if (op?.requestSchema && req.postDataJSON()) {
    op.requestSchema.parse(req.postDataJSON()); // throws on non-conforming
  }
  const response = handlers[/* resolved op */](req);
  if (op?.responseSchema) {
    op.responseSchema.parse(response.body);     // throws on non-conforming
  }
  callRecorder.record(/* ... */);
  return route.fulfill(response);
});
```

A schema-parse failure throws `OpenApiContractViolationError` and the surrounding test fails immediately. BDD scenarios SHALL NOT redeclare schema enforcement — `api-call-then` only asserts call presence/count/shape, not validity (validity is implicit).

For `none`-profile boundaries (web-app v1, no OpenAPI source) the schema gate is provided by hand-written Zod schemas under `src/lib/schemas/<aggregate>.ts`; the fixture handler imports those Zod schemas directly to validate fulfillment bodies.

## Storybook Binding (Boundary Invariant I4 — Concrete Impl)

`L4.source_refs.component` resolves to a fully-qualified Story export reference:

```text
src/components/borrow-request/BorrowRequestForm.stories.ts::Submitting
src/components/room-lobby/RoomLobby.stories.ts::Idle
```

Locator derivation rule:

1. Parse the Story export's `args` to determine accessible name / role / test-id.
2. Step definition uses `page.getByRole(role, { name })` matching that accessible name.
3. If the Story uses a design-system library component, the AI MUST verify the resulting role and accessible-name match library docs via `${PROJECT_SLUG}-sb-mcp` MCP tools BEFORE writing the locator.

Stories without explicit accessible-name args MUST NOT be bind targets — the Story author must add the args first; otherwise the binding fails legally (missing truth, not legal red).

## Forbidden (stack-level only)

Handler-level Forbidden items (route invention, field inference, CSS / nth-child selector bans, `time-control` wall-clock ban, `mock-state-then` ↔ `ui-readmodel-then` confusion, extra `Before` hooks, etc.) live in `../handlers/<handler>.md` § Forbidden and MUST NOT be redeclared here. This section keeps only constraints that span the whole `nextjs-playwright` stack:

- Mock layer location — `src/mocks/**` MUST NOT exist; `src/app/__test__/**` MUST NOT exist (deprecated v0 path). The fixture closure is the sole mock SSOT.
- Mock store import boundary — the fixture's mock store is test-process-only; product code under `src/**` MUST NOT import it.
- Production internals import boundary — step definitions MUST NOT `import` from `src/app/**` or any component file directly; the only legal channels are the rendered DOM (via `page`) and the fixture API (via `mockApi`).
- API host separation — `NEXT_PUBLIC_API_BASE_URL` MUST resolve to a host distinct from the Next.js dev server host; otherwise `page.route` glob can intercept page navigations.
- Fixture re-instantiation — `Given` / `When` / `Then` MUST be imported from `./fixtures`, never directly from `playwright-bdd` (a direct import re-instantiates `createBdd(test)` and breaks fixture sharing).
- Reset hook ownership — the fixture's per-test closure recreation is the sole legal per-scenario reset (I3); the variant MUST NOT ship additional reset entry points and step files MUST NOT register `Before` / `After` hooks that mutate closure state.

## Legal Red Expectation

A generated step definition is a valid red step only when:

- the matcher is generated from exact `L1`;
- all locator and assertion values come from L4 bindings (Story export args, route map, OpenAPI operation when present, data-model schema, test-strategy);
- the preset tuple resolves to this variant (`L4.preset.variant: nextjs-playwright`);
- the code can run far enough to expose missing product implementation or behavioral mismatch (a click reaches the page, the API call fires, the schema validates) — failure originates in product code, not in scaffolding.

Missing truth is not a legal red; rendering MUST stop before the step file is written. Specifically:

- Missing Story export referenced by `L4.source_refs.component` → stop; require Story to be authored first.
- Missing OpenAPI operation referenced by `L4.source_refs.contract` → stop; require operation to be added to the contract first.
- Missing `page.route` handler in `features/steps/fixtures.ts` for the target operation → stop; require fixture handler to be authored first (per Pre-Red Hook §3.3).
- Missing or mis-configured API host (`NEXT_PUBLIC_API_BASE_URL` overlaps with Next.js dev host) → stop; require host separation per Pre-Red Hook §3.7.
