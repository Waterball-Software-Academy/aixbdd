/* eslint-disable react-hooks/rules-of-hooks -- Playwright fixture `use` callback is not a React Hook */
import { test as base, createBdd } from "playwright-bdd";

import { env } from "@/lib/env";
import { operationRegistry } from "@/lib/schemas/operation-registry";

/**
 * playwright-bdd fixtures for this project.
 *
 * Mock layer pattern (web-frontend / nextjs-playwright variant):
 *   Mock state lives in this fixture's closure (test-runner process).
 *   `page.route` intercepts API calls via DevTools protocol — no in-app
 *   `src/mocks/**`, no `/__test__/*` HTTP indirection, no transport switch.
 *
 * Boundary invariants (see aibdd-core::boundaries/web-frontend):
 *   I1 — `page.route` is the cross-process surface (browser ↔ test-runner)
 *   I2 — dual Zod parse gate before `route.fulfill` (request + response)
 *   I3 — fixture scope = test → closure recreated per scenario; no manual reset
 *
 * Schemas wired through `operation-registry.ts` come from `_generated.ts`, which
 * is AI-derived from `${CONTRACTS_DIR}/api.yml` during pre-red §3.2.
 *
 * Five verbs exposed to step definitions (preset SSOT — web-frontend §3):
 *   - mockApi.seed(resource, rows)              → mock-state-given
 *   - mockApi.inspect(resource)                 → mock-state-then
 *   - mockApi.override(operationId, spec)       → api-stub
 *   - mockApi.calls(operationId?)               → api-call-then
 *   - mockApi.schemaViolations()                → diagnostic only (I2 runtime gate)
 *
 * `mockApi.reset()` is also exposed for ad-hoc mid-scenario clears; per-scenario
 * isolation is already guaranteed by fixture scope=test (I3), so step defs MUST
 * NOT call reset() in Before/After hooks.
 */

interface RecordedCall {
  operationId: string;
  method: string;
  pathname: string;
  query: Record<string, string>;
  headers: Record<string, string>;
  body: unknown;
  timestamp: number;
}

interface OverrideSpec {
  status?: number;
  body?: unknown;
  headers?: Record<string, string>;
}

interface MockApi {
  seed: <T>(resource: string, rows: ReadonlyArray<T>) => void;
  inspect: <T>(resource: string) => ReadonlyArray<T>;
  override: (operationId: string, spec: OverrideSpec) => void;
  calls: (operationId?: string) => ReadonlyArray<RecordedCall>;
  schemaViolations: () => ReadonlyArray<string>;
  reset: () => void;
}

const API_HOST = env.NEXT_PUBLIC_API_BASE_URL;
{
  const apiHost = new URL(API_HOST).host;
  if (apiHost === "localhost:3000") {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL must NOT equal the Next.js dev host (localhost:3000); " +
        "page.route would intercept page navigation. See prehandling §3.7.",
    );
  }
}

export const test = base.extend<{ mockApi: MockApi }>({
  mockApi: async ({ page }, use) => {
    const store = new Map<string, unknown[]>();
    const overrides = new Map<string, OverrideSpec>();
    const callLog: RecordedCall[] = [];
    const violations: string[] = [];

    await page.route(`${API_HOST}/**`, async (route) => {
      const req = route.request();
      const url = new URL(req.url());
      const method = req.method();

      const match = resolveOperation(method, url.pathname);
      if (!match) {
        await route.fulfill({
          status: 501,
          contentType: "text/plain",
          body: `unmapped ${method} ${url.pathname}`,
        });
        return;
      }
      const { op, pathParams } = match;

      const bodyText = req.postData();
      const bodyJson = bodyText !== null && bodyText.length > 0 ? safeJsonParse(bodyText) : undefined;

      if (op.requestSchema && bodyJson !== undefined) {
        const parsed = op.requestSchema.safeParse(bodyJson);
        if (!parsed.success) {
          violations.push(`${op.operationId} request: ${parsed.error.message}`);
          await route.fulfill({
            status: 400,
            contentType: "application/json",
            body: JSON.stringify({ error: parsed.error.flatten() }),
          });
          return;
        }
      }

      callLog.push({
        operationId: op.operationId,
        method,
        pathname: url.pathname,
        query: Object.fromEntries(url.searchParams),
        headers: req.headers(),
        body: bodyJson,
        timestamp: Date.now(),
      });

      const override = overrides.get(op.operationId);
      const responseBody =
        override?.body !== undefined
          ? override.body
          : op.defaultHandler({
              store,
              body: bodyJson,
              query: url.searchParams,
              pathParams,
            });
      const status = override?.status ?? 200;

      if (op.responseSchema && responseBody !== undefined) {
        const parsed = op.responseSchema.safeParse(responseBody);
        if (!parsed.success) {
          violations.push(`${op.operationId} response: ${parsed.error.message}`);
          await route.fulfill({
            status: 500,
            contentType: "application/json",
            body: JSON.stringify({ error: parsed.error.flatten() }),
          });
          return;
        }
      }

      await route.fulfill({
        status,
        contentType: "application/json",
        headers: override?.headers,
        body: responseBody === undefined ? "" : JSON.stringify(responseBody),
      });
    });

    const api: MockApi = {
      seed: (resource, rows) => {
        store.set(resource, [...rows]);
      },
      inspect: <T>(resource: string): ReadonlyArray<T> => (store.get(resource) ?? []) as ReadonlyArray<T>,
      override: (operationId, spec) => {
        overrides.set(operationId, spec);
      },
      calls: (operationId) =>
        operationId === undefined ? callLog : callLog.filter((c) => c.operationId === operationId),
      schemaViolations: () => violations,
      reset: () => {
        store.clear();
        overrides.clear();
        callLog.length = 0;
        violations.length = 0;
      },
    };

    await use(api);

    if (violations.length > 0) {
      throw new Error(`I2 schema gate violations:\n  - ${violations.join("\n  - ")}`);
    }
  },
});

export const { Given, When, Then } = createBdd(test);

function resolveOperation(
  method: string,
  pathname: string,
): { op: (typeof operationRegistry)[string]; pathParams: Record<string, string> } | undefined {
  for (const op of Object.values(operationRegistry)) {
    if (op.method !== method) continue;
    const pathParams = matchPath(op.pathTemplate, pathname);
    if (pathParams !== undefined) return { op, pathParams };
  }
  return undefined;
}

function matchPath(template: string, actual: string): Record<string, string> | undefined {
  const paramNames: string[] = [];
  const regexSrc = template.replace(/\{([^}]+)\}/g, (_, name: string) => {
    paramNames.push(name);
    return "([^/]+)";
  });
  const re = new RegExp(`^${regexSrc}$`);
  const m = re.exec(actual);
  if (!m) return undefined;
  const out: Record<string, string> = {};
  paramNames.forEach((n, i) => {
    out[n] = m[i + 1];
  });
  return out;
}

function safeJsonParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}
