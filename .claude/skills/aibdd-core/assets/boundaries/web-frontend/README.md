# Web Frontend Boundary Preset

Canonical boundary-wise preset assets for the **frontend Web UI E2E surface** live in this directory.

This directory is the SSOT for `L4.preset.name: web-frontend`. It defines handler routing, handler narrative docs, shared DSL template entries, and stack-specific variant rendering contracts (e.g., `nextjs-playwright`). It is framework-shipped preset source under `aibdd-core`; it is **not** generated boundary truth under `${TRUTH_BOUNDARY_ROOT}`.

Machine checks should validate `aibdd-core/assets/boundaries/web-frontend/handler-routing.yml`.

## Ownership

- Owner: `aibdd-core`
- Consumers: `/aibdd-plan` (frontend mode), `/aibdd-spec-by-example-analyze` (read-only via plan output), `/aibdd-frontend-projection` (when introduced), `/aibdd-red-execute` (frontend stack)

## Layout

| Path | Role |
|------|------|
| `handler-routing.yml` | SSOT: `routes` (`sentence_part` + `keyword` + `handler`) and `handlers` (`required_source_kinds`, `optional_source_kinds`, `l4_requirements`). Top-of-file comment block declares 4 boundary-level invariants (I1–I4). |
| `handlers/*.md` | Handler narrative and rendering guidance; does not override `handler-routing.yml` *(future expansion — not in v1)* |
| `variants/*.md` | Stack-specific rendering contracts such as `nextjs-playwright` *(future expansion — not in v1)* |
| `shared-dsl-template.yml` | Boundary-wide canonical shared DSL entries |
| `test-strategy-schema.md` | Schema for project-owned `${TEST_STRATEGY_FILE}` (`tier2_handlers`, `viewport_profiles`, `coverage_gates`, `policies`); consumed by `prehandling-before-red-phase.md` §3.6 / §3.7 and `check_frontend_preset_refs.py` |

## Boundary Scope

This preset describes the **interactive UI surface** observed and driven through a real browser context (Playwright / Cypress / Storybook test runner). It is a **separate boundary** from `web-backend`; a single feature package that crosses both UI and backend behavior must reference both presets in its `dsl.yml` entries (each entry binds to exactly one preset).

## Storybook as Component Contract

Storybook is the **single source of truth** for component-level behavior. Every UI handler (`ui-action`, `ui-readmodel-then`) binds to a **Story export**, not the component file alone:

```text
L4.source_refs.component: src/stories/Button.stories.ts::Primary
```

This means:
- Same component × different state (Primary / Secondary / Disabled / Loading) bind to different stories.
- E2E feature scenarios **trust** Storybook for component-level invariants (a11y, prop validation, render correctness, hover/focus states).
- E2E only verifies **composition** + **cross-page flow** + **integration with the mock backend**.
- Granular component internals (focus ring, animation curve, hover transition) are story-level concerns; do not duplicate them as BDD assertions.

When binding a component candidate from a design-system library, the AI MUST use the `${PROJECT_SLUG}-sb-mcp` MCP tools (`list-all-documentation` → `get-documentation`) to verify supported props before writing the binding. Properties not in the documented surface are forbidden — see `AGENTS.md` in the starter template.

## Mock Layer Stance

This boundary assumes **custom in-process mock implementations** (not MSW). Mock-related handlers (`mock-state-given`, `mock-state-then`, `api-stub`, `api-call-then`) bind through a `mock_implementation` source kind that resolves to a typed function table under `src/mocks/**`.

**OpenAPI schema conformance is a layer-level auto-gate**, not a per-scenario assertion: the mock layer Zod-validates every outgoing call against its OpenAPI operation schema, and non-conforming dispatch fails the test automatically (see boundary invariant I2). BDD scenarios assume conformance is enforced — `api-call-then` does **not** redeclare schema validation; it only asserts call presence, count, and shape.

The variant declares the exact cross-process mechanism (e.g., dev-only `/__test__/*` HTTP endpoints, or direct module import when the test runner shares process with the dev server — see boundary invariant I1).

## Handler Taxonomy (v1 — 11 handlers)

Split into **Tier-1** (always required) and **Tier-2** (opt-in per package). Tier-3 / future expansion is listed below.

### Tier-1 — always required (7)

| Handler | Backend dual | Keyword | Surface kind | Used by starter template? |
|---------|--------------|---------|--------------|---------------------------|
| `route-given` | *(frontend-only)* | Given/Background | `route-navigator` | ✅ `Given I am on the home page` |
| `viewport-control` | *(frontend-only)* | Given/When | `viewport-controller` | ✅ `When I resize the viewport to {int} x {int}` |
| `mock-state-given` | `aggregate-given` | Given/Background | `mock-loader` | – |
| `time-control` | `time-control` | Given/When | `clock` | – |
| `ui-action` | `http-operation` | Given/When | `ui-driver` | – |
| `success-failure` | `success-failure` | Then | `ui-feedback-verifier` | – |
| `ui-readmodel-then` | `readmodel-then` | Then | `ui-state-verifier` | ✅ 5 of 8 starter step patterns (page title / heading / link / button / text) |

### Tier-2 — opt-in per package (4)

| Handler | Backend dual | Keyword | When to enable |
|---------|--------------|---------|----------------|
| `api-stub` | `external-stub` | Given | Scenario needs a per-scenario mock-behavior override (e.g., next call returns 409, latency injection, response sequence) |
| `url-then` | *(frontend-only)* | Then | Scenario asserts on URL state where URL is the load-bearing observable (otherwise prefer `ui-readmodel-then`) |
| `api-call-then` | *(frontend-only)* | Then | Scenario asserts a specific outgoing call was emitted (count / shape match); schema conformance is automatic — see I2 |
| `mock-state-then` | `aggregate-then` | Then | UI does not render the mutation but the scenario must still verify the mock store changed |

> `route-given` exists because frontend behavior is route-conditional. Backend has no equivalent because each `http-operation` is self-locating via path.

## Boundary-Level Invariants (mirrored from handler-routing.yml top comment)

| ID | Invariant |
|----|-----------|
| **I1** | Cross-process surfaces — all `mock-*` / `api-*` handlers' `callable_via` resolves to a variant-defined surface that crosses the browser↔server process boundary. |
| **I2** | OpenAPI schema gate — the mock layer Zod-validates every outgoing call against its OpenAPI schema; non-conforming dispatch fails the test automatically. Per-scenario sentences MUST NOT redeclare schema enforcement. |
| **I3** | Per-scenario reset — handlers mutating cross-process state (`mock-state-given`, `api-stub`) require a per-scenario reset hook provided by the variant. |
| **I4** | Storybook contract granularity — UI handlers reference component contracts at the **Story export** level, not the component file alone. |

## Future Expansion (deferred from v1 — Tier-3)

| Candidate | Why deferred |
|-----------|--------------|
| `browser-storage-given` / `browser-storage-then` (cookies, localStorage, sessionStorage) | Auth/session pre-seed is typically done via test fixture (one-time login script), not Gherkin. Add when a scenario explicitly requires storage-state assertion (PWA offline cache, feature flag override, persistent UI preference) |
| `a11y-then` (axe / addon-a11y violations) | Storybook a11y addon already covers component-level; page-level a11y gate joins when the §4 dependency-graph plan lands |
| `download-then` (file download triggered) | Rare in product backlogs; add when first scenario needs it |
| `dialog-then` (alert/confirm/prompt) | Modern SPAs use custom modal components → covered by `ui-readmodel-then` |
| `console-then` (console.log / error capture) | Dev concern; not acceptance |
| `network-throttle-given` (offline / slow-3G) | Add when first explicit network-degradation scenario appears |

## Forbidden Content

- No Gherkin scenario text
- No Examples table
- No feature file path
- No atomic rule instance
- No concrete operationId, route literal, component name, story export name, or storage key
- No generated `dsl.yml` entry

Concrete operation, route, component, story, fixture, and storage-key references belong to `dsl.yml` entries under `L4.source_refs` and `L4.callable_via`. This preset only tells consumers how to classify frontend sentence parts and render a matched `L4.preset` tuple.
