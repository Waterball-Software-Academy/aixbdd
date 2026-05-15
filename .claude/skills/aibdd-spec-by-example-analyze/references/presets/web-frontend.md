# Preset: web-frontend

Frontend（browser-rendered UI + Playwright E2E driver）Boundary 之 Gherkin step pattern preset。

> mock 層為 Playwright `page.route` 攔截 + fixture closure-local store；**不**走 in-app `src/mocks/**` 或 `/__test__/*` HTTP 旁路。

## §0 Four-Layer Mapping Schema

```yaml
- id: <snake-case-id>
  L1:
    given: "<Given 句型模板；可省；留 {param} 佔位>"
    when:  "<When 句型模板>"
    then:  "<Then 句型模板>"
  L2:
    context: "<使用者狀態，譬如「在大廳頁」「在房間頁」>"
    role:    "<執行者角色（房主／房客／訪客）>"
    scope:   "page | component | boundary"
  L3:
    type: ui-action | ui-readmodel | route-nav | mock-state-setup | mock-state-verify
        | api-stub | api-call-verify | url-verify | viewport-control | time-control
        | operation-response-success-and-failure
  L4:
    # UI 類 (type ∈ {ui-action, ui-readmodel, operation-response-success-and-failure})
    callable_via: "<Playwright driver verb：click | fill | selectOption | press | drag | toHaveText | ...>"
    source_refs:
      component: "<Story export anchor，譬如 `src/stories/Button.stories.ts::Primary`>"
      route:     "<route map entry id>"
    param_bindings:
      - { from: "{房碼}", target: "input[name=room-code]", via: "fill" }
    assertion_bindings:
      - { target: "<accessible-name / role>", expected: "<value>" }

    # Route 類 (type ∈ {route-nav, url-verify})
    target_route: "<route map entry id>"
    url_pattern:  "<pathname / searchParams.<key> / hash>"
    value_template: "<譬如 /rooms/{房碼}>"

    # Mock 類 (type ∈ {mock-state-setup, mock-state-verify, api-stub, api-call-verify})
    fixture_api: "mockApi.{seedXxx | inspectXxx | override | calls | reset}"
    operation_id: "<plan-DSL operation id；對應 page.route handler 涵蓋的 method × path>"
    payload_schema: |
      <Zod schema 描述>
    reference: "src/lib/schemas/<aggregate>.ts#<SchemaName>"

    # Viewport / Time 類
    summary: "<一行摘要；不展開 component / clock 內部細節>"
```

### 強制條款

- L1 句型**絕不**出現 fixture method 名、operation_id、Zod schema、Playwright API。
- UI 類 entry：L4 必含 `callable_via` + `source_refs.component`（Story export anchor）；locator 派生由 step-def 從 Story `args` 解析（boundary I4）。
- Mock 類 entry：L4 必含 `fixture_api` + `operation_id` + (`payload_schema` OR `reference`)；`page.route` handler 在 `route.fulfill` 前以 `responseSchema.parse(...)` 強制 schema gate（boundary I2）。
- Route 類 entry：L4 必含 `target_route` + `url_pattern`；URL 為觀察面（`page.url()`），非 navigation source。
- Viewport / Time 類 entry：L4 = `summary` 一行。

## §1 適用條件

- **Browser-rendered UI Layer**：Next.js／React App Router 渲染、瀏覽器 DOM 為主要互動面
- **Playwright E2E driver**：playwright-bdd ≥ 8.5、Playwright ≥ 1.45（required for `page.clock`）
- **Storybook Story export**：元件合約 SSOT，`L4.source_refs.component` 指向具體 Story（boundary I4）
- **Mock 層為 `page.route` + fixture closure**：mock state 住 test-runner process；不走 in-app 旁路（boundary I1）

server-rendered HTML 無 browser DOM 互動、或 worker／API-only 服務 → 自訂 preset 或改用 `web-backend`。

## §3 Handler 清單

定義於 `aibdd-core/assets/boundaries/web-frontend/handler-routing.yml::handlers`（11 條，分 Tier-1 / Tier-2）。

### Tier-1（建立新 frontend package 必含）

| Handler | Gherkin 位置 | 用途 |
|---------|-------------|------|
| `route-given`       | Given / Background | 將瀏覽器 context 落在指定路由 |
| `viewport-control`  | Given / When | 控視窗尺寸或 device emulation |
| `mock-state-given`  | Given / Background | seed mock 狀態（`mockApi.seedXxx`） |
| `time-control`      | Given / When | 控 browser-visible 時間（`page.clock`） |
| `ui-action`         | Given / When | 透過 rendered surface 驅 UI 互動 |
| `operation-response-success-and-failure`   | Then | 驗 UI feedback class（toast／inline-error／banner／status pill） |
| `ui-readmodel-then` | Then | 驗 rendered DOM 上可觀察的值／role／attribute／count |

### Tier-2（opt-in；`test-strategy.yml.tier2_handlers.<id> == enabled` 才可用）

| Handler | Gherkin 位置 | 用途 |
|---------|-------------|------|
| `api-stub`        | Given | per-scenario response override（`mockApi.override`） |
| `url-then`        | Then  | 驗 URL pathname／searchParams／hash 在操作後狀態 |
| `api-call-then`   | Then  | 驗 outgoing API call 之 method／path／body／query／headers（`mockApi.calls`） |
| `mock-state-then` | Then  | 驗 fixture closure store 被改為預期狀態（`mockApi.inspectXxx`） |

**Handler 選取程序**：見 [`decision-trees/web-frontend-handler.yml`](decision-trees/web-frontend-handler.yml)。

## §4 Variant 清單

位於 `aibdd-core/assets/boundaries/web-frontend/variants/`：

| Variant | 對應技術棧 |
|---------|-----------|
| `nextjs-playwright` | TypeScript 5+ / Next.js 16 App Router / playwright-bdd ≥ 8.5 / Playwright ≥ 1.45 / Storybook ≥ 10 / Zod 4 / Vitest 4 / Tailwind 4 |

## §5 與 machine routing SSOT 的關係

- machine routing SSOT：`.claude/skills/aibdd-core/assets/boundaries/web-frontend/handler-routing.yml`
- preset 級契約：`.claude/skills/aibdd-core/references/preset-contract/web-frontend.md`

| `handler-routing.yml` routing id | 對應語意角色 |
|---|---|
| `route-given` | Pre-conditions → Land browser on target route |
| `viewport-control` | Pre-conditions / Operation → Resize / device emulation |
| `mock-state-given` | States → Given mock state seed |
| `time-control` | Pre-conditions / Operation → Control browser clock |
| `ui-action` | Operations → Drive UI interaction |
| `operation-response-success-and-failure` | Operations → Result feedback class verify |
| `ui-readmodel-then` | Operations → Observable DOM state verify |
| `api-stub` | Mock → Per-scenario operation response override (Tier-2) |
| `url-then` | Operations → URL state verify (Tier-2) |
| `api-call-then` | Operations → Outgoing call shape verify (Tier-2) |
| `mock-state-then` | States → Then mock state verify (Tier-2) |

### Boundary invariants I1–I4

- **I1 cross-process surface**：所有 mock-* / api-* handler 之 `callable_via` 由 variant 提供 cross-process surface；canonical 機制為 Playwright `page.route` + fixture closure；`/__test__/*` HTTP endpoints 為 deprecated；`src/mocks/**` 為 forbidden。
- **I2 OpenAPI schema gate**：mock layer 必須 Zod-validate 每筆 outgoing call 對應 OpenAPI／Zod schema；非合規 dispatch 自動 fail test。Schema gate 在 `route.fulfill` 前 enforce，**不**在 Scenario 句子重宣告。
- **I3 per-scenario reset**：mutating cross-process state 之 handler（mock-state-given／api-stub）必須在 scenario 之間 reset；由 fixture scope (test) 自動重建 closure（無需手動 reset）。
- **I4 Storybook contract granularity**：UI handler 之 `L4.source_refs.component` 必須指向 **Story export 層**（`<file>.stories.@(ts|tsx)::<ExportName>`），非 component file alone。同元件不同狀態可綁不同 Story。
