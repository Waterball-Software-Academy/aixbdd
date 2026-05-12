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

| API | Backs handler | Input shape | Output shape |
|---|---|---|---|
| `mockApi.seed<Entity>(input)` | `mock-state-given` | entity-specific seed shape (record values validated by data-model Zod schema) | `void` (mutates closure store) |
| `mockApi.inspect<Store>(where?)` | `mock-state-then` | optional `where` predicate object | `<Entity> \| <Entity>[]` from closure store |
| `mockApi.override(operationId, response, sequence?)` | `api-stub` | `(operationId, { status, body, headers? }, sequence?)` | `void` (queues per-scenario response override) |
| `mockApi.calls(operationId, since?)` | `api-call-then` | `(operationId, since?)` | `RecordedCall[]` from closure call recorder |
| `mockApi.reset()` | per-scenario reset (I3) | – | `void` (clears closure store; usually unnecessary — fixture scope handles it) |

The fixture itself registers `page.route(API_HOST + '/<path>', handler)` for every operation. Handlers parse `req.method()` + path, mutate closure store, and call `route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(...) })`. Each handler MUST validate its outgoing payload against the operation's response Zod schema (boundary invariant I2).

## Required Test Fixture Shape (`features/steps/fixtures.ts`)

```ts
/* eslint-disable react-hooks/rules-of-hooks -- Playwright fixture `use` callback is not a React Hook */
import { test as base, createBdd } from 'playwright-bdd';

interface MockApi {
  reset(): void;
  // domain-specific seed/inspect methods, e.g.:
  seedRoom(input: { roomCode: string; seatsTaken: number; capacity?: number }): void;
  inspectRoom(code: string): RoomState | undefined;
  // tier-2 only:
  // override(operationId: string, response: Override, sequence?: number): void;
  // calls(operationId: string, since?: string): RecordedCall[];
}

const API_HOST = 'http://localhost:4000'; // distinct from Next.js dev (localhost:3000)

export const test = base.extend<{ mockApi: MockApi }>({
  mockApi: async ({ page }, use) => {
    const store = new Map<string, RoomState>();

    await page.route(`${API_HOST}/<resource>/**`, async (route) => {
      const req = route.request();
      const url = new URL(req.url());
      const method = req.method();
      // dispatch by method × path
      // mutate `store` and call route.fulfill({ status, contentType, body })
      // every fulfilled body must conform to its responseSchema (Zod)
    });

    const api: MockApi = {
      reset: () => store.clear(),
      seedRoom: (input) => store.set(input.roomCode, /* build entity */),
      inspectRoom: (code) => store.get(code),
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

| Handler | Primary surface | Notes |
|---|---|---|
| `route-given` | `page.goto(url)` | Resolved against `baseURL` (Next.js dev host) from `playwright.config.ts` |
| `viewport-control` | `page.setViewportSize({width, height})` or `test.use({ viewport })` | Named profiles resolve via `test-strategy.yml#viewport_profiles` |
| `mock-state-given` | `mockApi.seed<Entity>(input)` (synchronous closure mutation) | Records Zod-validated by fixture's `page.route` handler on next dispatch |
| `time-control` | `page.clock.install({ time })` / `page.clock.fastForward(ms)` / `page.clock.setFixedTime(d)` | Requires Playwright ≥ 1.45 |
| `ui-action` | `page.getByRole / getByLabel / getByTestId(...).click() / .fill() / .selectOption() / .setInputFiles() / page.keyboard.press() / page.goBack() / page.goForward() / page.reload()` | Locator query MUST come from `L4.source_refs.component` Story export's argTypes / accessible name |
| `success-failure` | `await expect(page.getByRole('alert' \| 'status'))...toBeVisible()` and `.toContainText(reason)` | Surface (toast / inline / banner) declared in `L4.assertion_bindings.surface` |
| `ui-readmodel-then` | `await expect(...).toHaveText \| toBeVisible \| toHaveCount \| toHaveAttribute(...)` | Collection assertions use `getByRole('row' \| 'listitem')` + `.toHaveCount(n)` |
| `api-stub` | `mockApi.override(operationId, response, sequence?)` (synchronous closure mutation) | Active until per-scenario reset (fixture scope) |
| `url-then` | `await expect(page).toHaveURL(re)` and/or `new URL(page.url()).searchParams.get(k)` | Pathname dynamic segments matched by regex from route map |
| `api-call-then` | `mockApi.calls(operationId)` then assert on returned tuples | Schema validity already enforced (I2); handler asserts presence/count/shape only |
| `mock-state-then` | `mockApi.inspect<Store>(where?)` then assert | Reads closure store directly; never via DOM |

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

## Forbidden

- Do not invent route paths outside the project route map.
- Do not infer request or response field names outside L4 bindings.
- Do not call production internals from step definitions (no `import` from `src/app/**` or component file directly; only via rendered DOM or `mockApi`).
- Do not place mock layer code inside the app under test (`src/mocks/**` MUST NOT exist).
- Do not add `/__test__/*` Route Handlers to the Next.js dev server (deprecated v0 path).
- Do not import the fixture's mock store from product code (the store is test-process-only).
- Do not assert UI state in `mock-state-then` (use `ui-readmodel-then` for visible state).
- Do not assert mock-store state in `ui-readmodel-then` (use `mock-state-then` for non-visible mutation).
- Do not sleep or read wall-clock time in `time-control` (must go through `page.clock`).
- Do not register additional `Before` hooks that mutate closure state — closure recreation per test fixture scope is the only legal reset.
- Do not use raw CSS class selectors or nth-child positional selectors when role / label / test-id is available.
- Do not configure `NEXT_PUBLIC_API_BASE_URL` to the Next.js dev host (would cause `page.route` to intercept page navigations).

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
