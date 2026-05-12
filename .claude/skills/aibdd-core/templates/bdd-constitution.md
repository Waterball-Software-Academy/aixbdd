# BDD Constitution

> **Project-scope BDD practices** — where feature files live, where step
> definitions live, how fixtures are organised, how acceptance tests are
> wired. This document is the SSOT that `/speckit.tasks` reads to emit
> `archive-manifest.yml` and that `/speckit.aibdd.promote-dsl` reads to
> decide where promoted step definitions should move.
>
> Replace every `<TBD>` with your project's concrete decisions before
> running `/speckit.tasks` for the first time.

---

## 1. Framework Matrix (per-stack defaults)

Per-stack BDD framework / test-element-identifier defaults. Pick the row(s) that
match this project's composition. For **mono / mix** projects (e.g. Next.js with
both `app/` frontend and `pages/api/` backend), declare multiple rows under a
single `domain` and enumerate each stack in §2.

| Stack | Primary test framework | Acceptance runner | Gherkin dialect | Feature file ext | Reports | Test Element Identifier (§7.1) |
|---|---|---|---|---|---|---|
| `web-frontend` | `playwright-bdd` (or `@cucumber/cucumber` + Playwright) | Playwright | English / 中文 / mixed | `.feature` | Playwright HTML / Allure | `data-testid` |
| `web-backend` | `pytest + pytest-bdd` / `JUnit + Cucumber` / `Cucumber.js + supertest` | HTTP client (supertest / requests / RestAssured) | English / 中文 / mixed | `.feature` | Allure / Cucumber HTML / JUnit XML | structured JSON field paths (e.g. `$.data.id`) |
| `web-mono-fullstack` | duplicate rows — one frontend framework + one backend framework under same `domain` | Playwright + HTTP client | English / 中文 / mixed | `.feature` | combined report | combined (`data-testid` **and** JSON paths) |
| `native-ios` | `XCTest + Cucumberish` / `XCTest-Gherkin` / `Quick+Nimble BDD` | `xcodebuild test` / `xcrun simctl` | English | `.feature` | Xcode xcresult / Allure | `accessibilityIdentifier` |
| `native-android` | `Cucumber-Android` / `JUnit + Espresso` | `./gradlew connectedAndroidTest` | English | `.feature` | Gradle / Allure | `content-desc` / `androidx-test:testTag` |
| `mobile-rn-flutter` | RN: `Detox + Cucumber` · Flutter: `integration_test + gherkin` | Detox / Flutter driver | English | `.feature` | Allure / Flutter report | RN: `testID` · Flutter: `Key` |
| `cli` | `pytest + pytest-bdd` / `bash-bats` / `cucumber-rust` | direct exec + stdout/stderr capture | English | `.feature` | pytest HTML / bats TAP | structured output field paths (e.g. JSON stdout `$.result`, regex-matched stderr line) |
| `library` | `pytest + pytest-bdd` / `JUnit + Cucumber` / `RSpec` | in-process call | English | `.feature` | pytest / Allure | public API argument / return-value fields |
| `worker` | `pytest + pytest-bdd` (job bus harness) / `Cucumber.js + bull-board` | queue drain runner | English | `.feature` | pytest / Allure | job payload JSON fields |
| `mix-custom` | declare composition in §2 per-domain entry | declare composition | declare | `.feature` | declare | declare |

**Mono / mix rule**: when a single codebase hosts multiple stacks, §2 gets
**one entry per stack slice** sharing the same `domain` value. Example: a Next.js
domain `checkout` → one entry `stack=web-mono-fullstack` covering `app/checkout/`
UI + shared-state wrapper, plus one `stack=web-backend` entry covering
`pages/api/checkout/**`.

## 2. Loader Contracts *(NORMATIVE — SSOT for every plugin skill)*

> **This section is the SSOT read by ALL plugin skills** (`aibdd-discovery`,
> `speckit-aibdd-bdd-analyze`, `speckit-aibdd-test-plan`, `aibdd-form-activity`,
> `aibdd-form-feature-spec`, `clarify-loop`) **whenever they produce, validate,
> or consume fixtures.**
>
> Entries are **required (not example)** for every domain with a custom editor /
> wrapper / loader / test-seed strategy. A domain without a §2 entry is a
> `fixture-convention` blocker — `/speckit.aibdd.discovery` Step 0 must probe
> and draft one before proceeding.
>
> `aibdd-discovery/scripts/check_loader_contract_alignment.py` reads this
> section and verifies all referenced wrappers / fixture folders exist.

### 2.0 Entry Schema (required fields)

Every §2 entry **must** specify:

| Field | Required | Enum / format |
|---|---|---|
| `domain` | yes | BDD domain slug (matches `features/<domain>/` and `activities/<domain>-*.activity`) |
| `stack` | yes | one of `web-frontend` / `web-backend` / `web-mono-fullstack` / `native-ios` / `native-android` / `mobile-rn-flutter` / `cli` / `library` / `worker` / `custom-<label>` |
| `wrapper_entry` | required unless `stack=library` and N/A | loader entry file + exported function (absolute repo path allowed) |
| `fixture_shape` | yes | `file` / `folder` / `mixed` |
| `folder_layout` | required when `fixture_shape ∈ {folder, mixed}` | YAML tree |
| `data_source` | yes | `inline-yaml` / `inline-json` / `sibling-json` / `sibling-other` / `embedded-gherkin` / `embedded-sql` / `embedded-other` / `in-memory-seed` |
| `required_schema` | yes | minimum-valid document snippet (YAML / JSON / SQL / Swift / Kotlin / …) |
| `fallback_behaviour` | yes | what the loader does when required files are missing (throw / default / skip scenario / mock) |
| `starting_state` | **yes (PF-19)** | enumerates the entities / values the fixture exposes immediately after the loader mounts (e.g. `paths: 2, actors: 0, actions-per-path: 3`). Scenario authors reference this instead of re-deriving via trial-and-error DOM inspection. |

### 2.1 Example entry — `testplan-editor` (web-frontend)

```yaml
- domain: testplan-editor
  stack: web-frontend
  wrapper_entry: apps/electron/src/renderer/tests/wrappers/TestPlanEditorWrapper.tsx#loadTestPlan
  fixture_shape: folder
  folder_layout: |
    apps/electron/tests/testplan-editor/fixture/
    ├── standard-project/
    │   ├── .specformula/settings.yml          # directoryMarkings, spec-root
    │   ├── specs/101-checkout/test-plan/
    │   │   └── checkout-flow.testplan.json    # sample testplan (sibling JSON)
    │   └── specs/101-checkout/features/
    │       └── checkout.feature               # sibling gherkin
    └── empty-project/
        └── .specformula/settings.yml          # no testplan — triggers empty state
  data_source: sibling-json                    # .testplan.json read alongside .feature
  required_schema: |
    # .specformula/settings.yml
    version: 1
    directoryMarkings:
      - spec-root: specs/
    # *.testplan.json
    {"version": 1, "paths": [{"id": "p1", "name": "..."}], "nodes": [...]}
  fallback_behaviour: |
    - wrapper throws `FixtureNotFoundError` if .specformula/settings.yml missing
    - empty `paths` array falls through to the editor's empty-state UI (not an error)
    - malformed JSON surfaces as `onError` callback, editor stays mounted
  starting_state: |                    # PF-19 — what scenarios can rely on right after load
    paths:
      count: 2
      names: ["正常註冊", "註冊失敗"]
    actors_per_path:                   # parseTestPlanFromGherkin derives 0 actors for these
      count: 0
    background_per_path:
      count: 2                         # each path has 2 Background action rows
    actions_per_path:
      count: 3
      status: ["default", "default", "default"]
    dirty: false
```

### 2.2 Example entry — `checkout-api` (web-backend)

```yaml
- domain: checkout-api
  stack: web-backend
  wrapper_entry: backend/tests/_helpers/api_harness.py#load_checkout_fixture
  fixture_shape: mixed
  folder_layout: |
    backend/tests/checkout-api/fixture/
    ├── seed.sql                              # embedded-sql for DB seeding
    ├── users.json                            # sibling JSON
    └── idempotency-keys.yml                  # sibling YAML
  data_source: embedded-sql
  required_schema: |
    -- seed.sql
    INSERT INTO users (id, email) VALUES (1, 'alice@example.com');
    INSERT INTO products (id, price_cents) VALUES (42, 1999);
    -- users.json
    [{"id": 1, "email": "alice@example.com", "role": "customer"}]
  fallback_behaviour: |
    - if seed.sql missing → raise `FixtureMissingError`, halt Scenario collection
    - if users.json missing → default to empty user set (still runs; many scenarios skip)
    - DB rolled back via savepoint after each scenario
```

### 2.3 Example entry — `checkout` (web-mono-fullstack)

```yaml
# Mono/mix — this domain has BOTH frontend (Next.js app/) AND backend (pages/api/).
# Ship as TWO entries sharing the same `domain` value.
- domain: checkout
  stack: web-mono-fullstack
  wrapper_entry: apps/web/tests/wrappers/CheckoutFlowWrapper.tsx#mountCheckoutFlow
  fixture_shape: folder
  folder_layout: |
    apps/web/tests/checkout/fixture/
    ├── cart-populated/
    │   ├── cart.json                         # client-visible cart state
    │   └── session.json                      # NextAuth-style session
    └── cart-empty/
        └── session.json
  data_source: sibling-json
  required_schema: |
    # cart.json
    {"items": [{"sku": "A-1", "qty": 2}], "subtotal_cents": 1998}
    # session.json
    {"user": {"id": 1}, "expires": "2030-01-01"}
  fallback_behaviour: |
    - missing cart.json → wrapper mounts the empty-cart view (valid happy path)
    - missing session.json → wrapper redirects to /login (acceptance test asserts this)

- domain: checkout
  stack: web-backend
  wrapper_entry: apps/web/tests/api-harness/checkout.ts#seedCheckoutApi
  fixture_shape: mixed
  folder_layout: |
    apps/web/tests/checkout/fixture/api/
    ├── seed.sql
    └── stripe-mock.json                       # sibling JSON (mock webhook payloads)
  data_source: embedded-sql
  required_schema: |
    -- seed.sql (products, inventory)
    INSERT INTO products ... ;
    -- stripe-mock.json
    {"webhooks": [{"type": "checkout.session.completed", ...}]}
  fallback_behaviour: |
    - missing seed.sql → FixtureMissingError (halt)
    - missing stripe-mock.json → fall back to in-memory `PaymentProviderStub`
```

### 2.4 Example entry — `login-screen` (native-ios)

```yaml
- domain: login-screen
  stack: native-ios
  wrapper_entry: MyAppUITests/Wrappers/LoginScreenTestSeed.swift#seedLoginScreen
  fixture_shape: folder
  folder_layout: |
    MyAppUITests/Fixtures/login-screen/
    ├── valid-credentials/
    │   └── seed.json                         # payload passed via launchArguments
    └── expired-session/
        └── seed.json
  data_source: sibling-json                   # loaded at launch, wired via launchEnvironment
  required_schema: |
    # seed.json
    {"preloadedUser": {"id": "u1", "email": "alice@example.com"}, "sessionState": "valid"}
    // LoginScreenTestSeed.swift must expose:
    // func seedLoginScreen(_ fixtureName: String) -> XCUIApplication
  fallback_behaviour: |
    - missing seed.json → app launches to onboarding (valid for FR-auth-001 scenarios)
    - malformed seed → XCTFail before scenario body runs (fixture-convention failure)
```

### 2.5 Example entry — `spec-format-validator` (cli)

```yaml
- domain: spec-format-validator
  stack: cli
  wrapper_entry: tests/cli_harness.py#run_validator_with_fixture
  fixture_shape: folder
  folder_layout: |
    tests/spec-format-validator/fixture/
    ├── valid-project/
    │   ├── .specformula/settings.yml
    │   └── specs/001-sample/spec.md
    └── malformed-project/
        └── .specformula/settings.yml          # missing required version field
  data_source: embedded-other                  # raw yaml + md trees consumed via argv
  required_schema: |
    # .specformula/settings.yml (minimum valid)
    version: 1
    directoryMarkings: []
    # CLI wrapper signature (Python):
    # def run_validator_with_fixture(fixture: str, *, extra_args: list[str] = []) -> CompletedProcess
  fallback_behaviour: |
    - missing fixture dir → Python FileNotFoundError (halt; fixture-convention blocker)
    - validator exits non-zero for malformed-project → captured and asserted (expected red)
    - empty settings.yml → validator prints "NO_SETTINGS" to stderr (asserted by scenario)
```

> **Add one entry per domain × stack slice**. If a single domain spans multiple
> stacks (mono/mix), ship one entry per slice sharing the `domain` value (see
> §2.3 for the canonical web-mono-fullstack pattern).

## 3. File layout (repository-level)

```text
<project-root>/
├── tests/
│   ├── features/            # ← archive target for rule-only + Examples .feature files
│   │   └── <domain>/
│   ├── step-defs/           # ← archive target for step definition modules
│   │   ├── dsl-core/        # ← where promoted shared-tier step defs land（檔名仍可用 dsl-core 資料夾區隔）
│   │   └── dsl-local/       # ← per-feature local step defs (pre-promotion)
│   ├── fixtures/            # ← shared fixtures (data builders, mocks, fakes)
│   └── acceptance/          # ← archive target for test-plan/*.feature (Flow-Oriented Gherkin)
└── <app-source-tree>/
```

## 3.1 Feature file naming *(NORMATIVE — PF-22)*

**Hard rule**: every `.feature` file in the acceptance tree (both archived
scenario files and Flow-Oriented Gherkin test-plan files) **must** be named:

```
NN-<繁體中文標題>.feature
```

Where:

- `NN` = two-digit decimal sequence prefix (`01`–`99`). Prefix orders files by
  narrative read order within a domain (entry → primary CRUD → cross-cutting
  → flow-level acceptance features), **not** alphabetical. Curate the sequence by hand.
- `<繁體中文標題>` = Traditional Chinese title that names exactly one
  recognisable operation (e.g. `新增` / `刪除` / `重新命名` / `重新排序` /
  `檢視` / `驗收總覽`).
- **Domain proper nouns stay in original language** and concat directly
  without a separator — e.g. `Actor` / `Path` / `Step` / `Background` /
  `CRUD` / `Payload` / `Evaluation`.

**Good examples**:

- `01-開啟測試計劃.feature`
- `14-新增Actor.feature`
- `18-重新命名Actor連動更新.feature`
- `39-Step資料負載維護.feature`
- `42-髒資料存檔.feature`

**Bad examples** (must be refactored):

- `actor-add.feature` — all-English, no prefix
- `新增Actor.feature` — missing prefix
- `14-AddActor.feature` — English verb (use `新增`)
- `14-新增 Actor.feature` — space between Chinese and proper noun (use concat)

**Why**: non-engineer stakeholders (domain SMEs, QA managers, product owners)
scan feature trees to understand acceptance coverage. An all-English tree is
opaque to them; a prefix-ordered Chinese tree reads like a table of contents.
Alphabetical ordering scrambles the narrative — the hand-curated prefix
sequence is the human-authored read order.

**Enforcement**: `/speckit.tasks` Phase Z emission **must** rename archive
targets to this scheme; `aibdd-form-feature-spec` Step 5 Quality Gate must
reject source filenames that violate this rule.

## 4. Step Definition conventions

| Rule | Value |
|---|---|
| Naming pattern | `<TBD: e.g. one file per DSL entry id / one file per feature / ... >` |
| Parameter binding | `<TBD: Gherkin expression / regex>` |

> Wrapper / loader / seed routing is defined per-domain in **§2 Loader
> Contracts** (normative). This section covers only step-def file naming and
> binding style — anything relating to how a step reaches test data is
> governed by §2.

## 5. Fixture / Seed strategy

This section describes **project-wide** hooks only (per-run seed, per-scenario
teardown, mock server choice). **Per-domain fixture structure, loader signature,
data source, and fallback behaviour are normative in §2 Loader Contracts.** Do
not invent a per-domain layout here that contradicts §2.

| Scope | How |
|---|---|
| Per-run seed | `<TBD>` |
| Per-scenario teardown | `<TBD>` |
| Mock server | `<TBD: MSW / WireMock / mockoon / none>` |

## 6. Archive migration (what `/speckit.tasks` moves) — per-file (PF-16)

**Hard rule (PF-16)**: `/speckit.tasks` Phase Z emission **must expand one `git mv` task per source file** under the spec package. **Glob / group tasks are forbidden** (no "Move all `features/*.feature`"). This is what lets the Archive Gate (PF-15b, in `/speckit.implement` overlay) verify 1-to-1 coverage by comparing `archive-manifest.yml.moves[]` length against the spec package's unarchived artefact count.

**After Phase Z runs**, the **spec package keeps only `archive-manifest.yml` as pointer**; actual `.feature` / `dsl.md` content lives at the destinations below. To trace spec ↔ archived code, grep `archive-manifest.yml`.

### Target resolution table (per source artefact)

| Source (in spec package) | Target (project final location) — must be per-file absolute resolved |
|---|---|
| `specs/<feature>/features/<domain>/<f>.feature` (scenario-level) | `<TBD: e.g. tests/features/<domain>/<f>.feature>` — one `git mv` per file |
| `specs/<feature>/test-plan/<a>.feature` (flow-oriented, 1:1 with Activity) | `<TBD: e.g. tests/features/<domain>/<a>-acceptance.feature>` — one `git mv` per file |
| `specs/<feature>/dsl.md` | `<TBD: merge as comment header into tests/step-defs/<domain>.steps.ts>` — one merge task |
| `specs/<feature>/step-defs/` (if pre-authored) | `<TBD: tests/step-defs/<domain>/>` — per-file `git mv` |

Filed via `archive-manifest.yml.moves[]` entries with schema `{from, to, task, timestamp}` (merge rows additionally carry `merge: true`).

## 7. Promotion (what `/speckit.aibdd.promote-dsl` moves)

When a DSL entry is promoted from boundary `dsl.md` to shared `dsl.md`:

| Artefact | Destination |
|---|---|
| DSL entry YAML (4-layer mapping) | append to `.specify/memory/dsl.md` |
| Step definition code | move from `<per-feature step-defs>` → `tests/step-defs/dsl-core/` |
| boundary `dsl.md` reference | replace with pointer comment `# promoted → shared-dsl#<id>` |
| archive-manifest.yml | append promotion event (kind=promotion) |

## 7.1 Test Element Identifier conventions (PF-14 polyglot, supersedes Round-1 `data-testid`)

Test Element Identifier is the **per-stack locator** that step definitions use
to reach a UI / API / CLI element. It replaces the previous frontend-biased
`data-testid` section. Pick the attribute for your stack from §1 Framework
Matrix column "Test Element Identifier"; the non-negotiable priority order
below applies within each stack.

**Priority (highest → lowest, Non-Negotiable, per stack)**:

| Stack | 1st | 2nd | 3rd | 4th |
|---|---|---|---|---|
| `web-frontend` / `web-mono-fullstack` | `data-testid` | ARIA (`[role=…]`, `aria-*`) | `getByText()` (when unique) | semantic selector (`[data-sonner-toast]`, `.monaco-editor`) |
| `web-backend` | response JSON field path (`$.data.id`) | header field (`X-Request-Id`) | HTTP status + path pattern | error-code field |
| `native-ios` | `accessibilityIdentifier` | `accessibilityLabel` | `XCUIElement.Type` + label | coordinate (last resort) |
| `native-android` | `androidx-test:testTag` / `content-desc` | `resource-id` | text (when unique) | coordinate (last resort) |
| `mobile-rn-flutter` | RN `testID` · Flutter `Key` | accessibility label | text (when unique) | XY coordinate |
| `cli` | structured output field path (e.g. JSON `$.result`) | regex-matched stderr line | exit code | full stdout match |

**Naming format (when identifier is a string tag)**: `{domain}-{component}-{role}[-{suffix}]`

| Element kind | Pattern | Example (web) |
|---|---|---|
| Structural container | `{domain}-{component}` | `testplan-path-tabs` |
| Interactive element | `{domain}-{component}-{action}` | `testplan-path-add-button` |
| List item instance | `{domain}-{component}-item-{identifier}` | `testplan-path-tab-item-01` |
| Dialog / modal / sheet | `{domain}-{purpose}-dialog` | `testplan-path-delete-dialog` |
| Confirmation button | `{domain}-{purpose}-confirm-button` | `testplan-path-delete-confirm-button` |

**Bad examples** (must be refactored): `button-1`, `delete-btn`, CSS-selector-looking values, numeric-only `tag_01`.

UI / screen / CLI components that add testable behaviour **must** ship with
their stack's Test Element Identifier simultaneously. No "we'll add the tag
later." This applies to all stacks — an iOS UIButton needs its
`accessibilityIdentifier` at first check-in, a CLI subcommand needs structured
JSON output at first check-in.

## 8. Vocabulary appendix (per-stack)

The previous VOCABULARY categories A–F were React-biased. Here they are
generalised per stack:

| Category | web-frontend | web-backend | native-ios | native-android | cli |
|---|---|---|---|---|---|
| A. entry point | Component / Route | HTTP endpoint | UIViewController / SwiftUI View | Activity / Fragment | subcommand (argv[1]) |
| B. user action | click / type / navigate | HTTP request | tap / swipe / type | tap / swipe / type | argv / stdin |
| C. state check | DOM text / `data-testid` | response body / status | `accessibilityIdentifier` | `testTag` / `content-desc` | stdout / exit-code |
| D. async signal | network request / websocket | async job / outbox | delegate callback | broadcast receiver | progress line / file |
| E. persistence | IndexedDB / localStorage / server | DB row / cache | CoreData / Keychain | Room / SharedPreferences | filesystem |
| F. side-effect exit | navigation / toast | 2xx + body / 4xx + error | navigation / Haptic | Toast / navigation | exit-code + stdout |

## 9. Review cadence

This file should be reviewed at every **major** framework upgrade (Cucumber
major version, pytest-bdd 5+, Playwright major, XCTest major, etc.) **and**
whenever a new domain is added — §2 entry must be landed before the domain's
first feature file is written (probe-first rule, see
`aibdd-discovery/SKILL.md` Step 0).
