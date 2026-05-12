/* eslint-disable react-hooks/rules-of-hooks -- Playwright fixture `use` callback is not a React Hook */
import { test as base, createBdd } from 'playwright-bdd';

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
 *   I3 — fixture scope = test → closure recreated per scenario; no manual reset
 *
 * URL host design:
 *   API base URL must be distinct from the Next.js dev host. By default,
 *   `.env.example` sets `NEXT_PUBLIC_API_BASE_URL=http://localhost:4000` while
 *   Playwright `use.baseURL` is `http://localhost:3000` (the Next.js dev). The
 *   page.route glob targets the API host so page navigations are not intercepted.
 *
 * Skeleton (uncomment and adapt during GREEN Wave 1 of your first feature):
 *
 *   interface MockApi {
 *     reset(): void;
 *     // domain-specific seed/inspect methods, e.g.:
 *     // seed<Entity>(input: ...): void;
 *     // inspect<Store>(where?): ... | undefined;
 *   }
 *
 *   const API_HOST = 'http://localhost:4000';
 *
 *   export const test = base.extend<{ mockApi: MockApi }>({
 *     mockApi: async ({ page }, use) => {
 *       const store = new Map<string, unknown>(); // closure-local mock state
 *
 *       await page.route(`${API_HOST}/<resource>/**`, async (route) => {
 *         const req = route.request();
 *         const url = new URL(req.url());
 *         const method = req.method();
 *         // 1. Match method × url.pathname.
 *         // 2. Mutate `store` for write operations.
 *         // 3. Build response body conforming to its responseSchema (Zod parse).
 *         // 4. route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(...) }).
 *       });
 *
 *       const api: MockApi = {
 *         reset: () => store.clear(),
 *       };
 *       await use(api);
 *     },
 *   });
 */

type Fixtures = Record<string, never>;

export const test = base.extend<Fixtures>({});

export const { Given, When, Then } = createBdd(test);
