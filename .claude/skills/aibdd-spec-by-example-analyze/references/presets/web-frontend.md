# Preset: web-frontend

Frontend（browser-rendered UI + Playwright E2E driver）Boundary 的 Gherkin step pattern preset。

> v2 (2026-05-10): mock 層為 Playwright `page.route` 攔截 + fixture closure-local store；**不**走 in-app `src/mocks/**` 或 `/__test__/*` HTTP 旁路（v1 deprecated）。

---

## §0 Four-Layer Mapping Schema

本 preset 的 step pattern entry **必採下列四層 mapping**。Scenario 表面只呈現 L1 業務句型；L2-L4 供 step-def 實作 / validator / fixture 層讀取。

### §0.1 Entry Schema（YAML）

```yaml
- id: <snake-case-id>                    # preset entry 識別碼，全域唯一於本 preset
  L1:                                    # Business Sentence Pattern — feature file 表面採用的業務語言句型
    given: "<Given 句型模板，留 {param} 佔位>"  # 可省（only-When 類 entry）
    when:  "<When 句型模板>"
    then:  "<Then 句型模板>"              # 可多條（列表）
  L2:                                    # DSL Semantics — 語意 / Context / Role
    context: "<action 發生的使用者狀態（譬如「在大廳頁」「在房間頁」）>"
    role:    "<執行者角色（房主／房客／訪客 等）>"
    scope:   "<語意涵蓋範圍：page / component / boundary>"
  L3:                                    # Technical Pattern — 執行機制分類
    type: ui-action | ui-readmodel | route-nav | mock-state-setup | mock-state-verify
        | api-stub | api-call-verify | url-verify | viewport-control | time-control
        | success-failure
  L4:                                    # External Contract / Payload — 依 type 分流必填欄位
    # ─── UI 類 (type ∈ {ui-action, ui-readmodel, success-failure}) ───
    callable_via: "<Playwright driver verb：click | fill | selectOption | press | drag | toHaveText | ...>"
    source_refs:
      component: "<Story export anchor，譬如 `src/stories/Button.stories.ts::Primary`>"
      route:     "<route map entry id；用於確認此互動發生的頁面 context>"
    param_bindings:
      - { from: "{房碼}", target: "input[name=room-code]", via: "fill" }
    assertion_bindings:                  # ui-readmodel / success-failure 才有
      - { target: "<accessible-name / role>", expected: "<value>" }

    # ─── Route 類 (type ∈ {route-nav, url-verify}) ───
    target_route: "<route map entry id>"
    url_pattern:  "<pathname / searchParams.<key> / hash>"
    value_template: "<譬如 /rooms/{房碼}>"

    # ─── Mock 類 (type ∈ {mock-state-setup, mock-state-verify, api-stub, api-call-verify}) ───
    fixture_api: "mockApi.{seedXxx | inspectXxx | override | calls | reset}"
    operation_id: "<plan-DSL operation id；對應 page.route handler 涵蓋的 method × path>"
    payload_schema: |                    # 或 reference 指向 src/lib/schemas/...
      <Zod schema 描述>
    reference: "src/lib/schemas/<aggregate>.ts#<SchemaName>"  # 與 payload_schema 二擇一

    # ─── Viewport / Time 類 (type ∈ {viewport-control, time-control}) ───
    summary: "<一行摘要；不展開 component / clock 內部細節>"
```

### §0.2 強制條款

- **Scenario 表面一律業務語言**（test-plan-rules.md R6 + R9）— L1 句型絕不出現 fixture method 名、operation_id、Zod schema、Playwright API
- **UI 類 entry 的 L4** 必含 `callable_via` + `source_refs.component`（Story export anchor）；locator 派生由 step-def 從 Story `args` 解析（boundary I4）
- **Mock 類 entry 的 L4** 必含 `fixture_api` + `operation_id` + (`payload_schema` OR `reference`)；mock 狀態以 fixture closure 為 SSOT，`page.route` handler 在 `route.fulfill` 前以 `responseSchema.parse(...)` 強制 schema gate（boundary I2）
- **Route 類 entry 的 L4** 必含 `target_route` + `url_pattern`；URL 為觀察面（`page.url()`），非 navigation source
- **Viewport / Time 類 entry 的 L4** = `summary` 一行；具體 driver 細節屬 step-def 實作層

## §1 適用條件

本 preset 適用的 boundary 必須同時具備：

- **Browser-rendered UI Layer** — Next.js / React App Router 渲染、瀏覽器 DOM 為主要互動面
- **Playwright E2E driver** — playwright-bdd ≥ 8.5、Playwright ≥ 1.45（required for `page.clock`）
- **Storybook Story export** — 元件合約 SSOT，`L4.source_refs.component` 指向具體 Story（boundary I4）
- **Mock 層為 Playwright `page.route` + fixture closure** — mock state 住 test-runner process；不走 in-app `src/mocks/**` 或 `/__test__/*` 旁路（boundary I1）

若 boundary 為 server-rendered HTML 但無 browser DOM 互動、或為 worker / API-only 服務，需自訂 preset（或改用 `web-backend`）。

---

## §2 子活動入口

Reason §3.⑦ preset step pattern 套用的實際步驟：

1. 讀 `aibdd-core/assets/boundaries/web-frontend/handler-routing.yml`（含 `handlers:` section 與 boundary invariants I1-I4 註解區塊）取後設決策樹（route-nav / viewport / mock-state / time / ui-action / success-failure / ui-readmodel / api-stub / url / api-call / mock-state-then）
2. 對每個 Gherkin 子句套用本 preset §0.1 schema → 得 type 分類（11 type 之一）
3. 依 §3 routing id 對照表找對應 handler id
4. 讀 `handler-routing.yml::handlers.<id>` 取該 handler 的 `required_source_kinds` / `optional_source_kinds` / `l4_requirements`（**注意**：web-frontend 不拆 `handlers/<id>.md` per-file，handler 文件 inline 在 routing yml）
5. 讀 `aibdd-core/assets/boundaries/web-frontend/variants/<variant>.md` 取該 variant 的程式碼 pattern（`variant` 由 `${STARTER_VARIANT}` 或 plan DSL `L4.preset.variant` 決定）

---

## §3 Handler 清單

定義在 `aibdd-core/assets/boundaries/web-frontend/handler-routing.yml` `handlers:` section（11 條，分 Tier-1 / Tier-2）：

### Tier-1（always required；建立新 frontend package 必含）

| Handler | Gherkin 位置 | 用途 |
|---------|-------------|------|
| `route-given` | Given / Background | 將瀏覽器 context 落在指定路由作為 scenario 前置 |
| `viewport-control` | Given / When | 控制視窗尺寸或 device emulation profile |
| `mock-state-given` | Given / Background | 在 fixture closure store 內 seed 持久化狀態（透過 `mockApi.seedXxx`） |
| `time-control` | Given / When | 控制 browser-visible 時間（Playwright 1.45+ `page.clock`） |
| `ui-action` | Given / When | 透過 rendered surface 驅動 UI 互動（click / fill / select / upload / press / drag / navigate） |
| `success-failure` | Then | 驗證 UI feedback class（toast / inline-error / banner / status pill） |
| `ui-readmodel-then` | Then | 驗證 rendered DOM 上可觀察的值、role、attribute、count |

### Tier-2（opt-in per package；test-strategy.yml `tier2_handlers.<id> == enabled` 才能用）

| Handler | Gherkin 位置 | 用途 |
|---------|-------------|------|
| `api-stub` | Given | 對指定 `operationId` 設置 per-scenario response override（`mockApi.override`） |
| `url-then` | Then | 驗證 URL pathname / searchParams / hash 在操作後的狀態 |
| `api-call-then` | Then | 驗證 outgoing API call 的 method / path / body / query / headers（`mockApi.calls`） |
| `mock-state-then` | Then | 驗證 fixture closure store 被改成預期狀態（`mockApi.inspectXxx`） |

---

## §4 Variant 清單

位於 `aibdd-core/assets/boundaries/web-frontend/variants/`：

| Variant | 對應技術棧 |
|---------|-----------|
| `nextjs-playwright` | TypeScript 5+ / Next.js 16 App Router / playwright-bdd ≥ 8.5 / Playwright ≥ 1.45 / Storybook ≥ 10 / Zod 4 / Vitest 4 / Tailwind 4。Mock 層走 `features/steps/fixtures.ts` 內 `page.route` + closure-local store；產品端 `src/lib/api-client.ts` 為純 fetch wrapper（無 transport switch）。 |

Variant 本身不增 handler 種類，只改實作語法與 framework binding。

---

## §5 與 `handler-routing.yml`（boundary preset routing SSOT）的關係

本文件中 **preset 級**的 step pattern、§2 子活動入口、§3 handler 清單，與 **`dsl.yml`** 所使用的 **routing id**（`sentence_part`、`handler`、Gherkin `keyword`）**必須**與機械來源對齊：

- machine routing SSOT：`.claude/skills/aibdd-core/assets/boundaries/web-frontend/handler-routing.yml`
- preset 級契約：`.claude/skills/aibdd-core/references/preset-contract/web-frontend.md`

| `handler-routing.yml` routing id | 對應本 preset 文件中常見語意角色 |
|---------|--------------------|
| `route-given` | Pre-conditions → Land browser on a target route |
| `viewport-control` | Pre-conditions / Operation → Resize / device emulation |
| `mock-state-given` | States → Given mock state seed (fixture closure mutate) |
| `time-control` | Pre-conditions / Operation → Control browser clock |
| `ui-action` | Operations → Drive rendered UI interaction |
| `success-failure` | Operations → Result / outcome feedback class verify |
| `ui-readmodel-then` | Operations → Observable DOM state verify |
| `api-stub` | Mock → Per-scenario operation response override (Tier-2) |
| `url-then` | Operations → URL state verify (Tier-2) |
| `api-call-then` | Operations → Outgoing call presence / count / shape verify (Tier-2) |
| `mock-state-then` | States → Then mock state verify (Tier-2) |

### Boundary invariants I1-I4（inline 於 handler-routing.yml 註解區塊；本 preset 必須對齊）

- **I1 cross-process surface**：所有 mock-* / api-* handler 的 `callable_via` 必須由 variant 提供 cross-process surface；v2 canonical 機制為 Playwright `page.route` + fixture closure（DevTools protocol-backed）；`/__test__/*` HTTP endpoints 為 deprecated；`src/mocks/**` 為 forbidden。
- **I2 OpenAPI schema gate**：mock layer 必須 Zod-validate 每筆 outgoing call 對應 OpenAPI / Zod schema；非合規 dispatch 自動 fail test。Schema 強制由 fixture handler 在 `route.fulfill` 前 enforce，**不**在 scenario 句子重宣告。
- **I3 per-scenario reset**：mutating cross-process state 的 handler（mock-state-given / api-stub）必須在 scenario 之間 reset；v2 由 fixture scope (test) 自動重建 closure（無需手動 reset）。
- **I4 Storybook contract granularity**：UI handler（ui-action / ui-readmodel-then）的 `L4.source_refs.component` 必須指向 **Story export 層**（`<file>.stories.@(ts|tsx)::<ExportName>`），非 component file alone。同元件不同狀態可綁不同 Story。

歷史：`.claude/skills/aibdd-plan/references/sentence-parts-framework.md` 已廢止，僅留 Tombstone；勿再宣稱其為 SSOT。

---

## §6 擴充點

### 新增 handler

frontend handler 文件 **inline** 在 `aibdd-core/assets/boundaries/web-frontend/handler-routing.yml` 的 `handlers:` section（每個 handler 含 `required_source_kinds` / `optional_source_kinds` / `l4_requirements`）— **不**走 `handlers/<id>.md` per-file 拆分（與 web-backend 結構不同）。

新增步驟：
1. 在 `handler-routing.yml::routes` 加 routing entry（`sentence_part` / `keyword` / `handler` / `semantic`）
2. 在 `handler-routing.yml::handlers` 加 handler 定義（含 L4 requirements）
3. 同步本檔 §3 清單（Tier-1 或 Tier-2）
4. 若新 handler 涉及 cross-process state 變更，更新本檔 §5 boundary invariants I3 範圍

### 新增 variant

在 `aibdd-core/assets/boundaries/web-frontend/variants/` 放 `<variant-name>.md`，並於本檔 §4 更新清單。Variant 必須說明：
- runtime contract（語言 / framework / 版本下限）
- mock layer 機制（必符合 I1 cross-process surface）
- 必要 fixture 結構（含 mockApi shape）
- per-handler Playwright API mapping
- API host separation 要求（避免 page.route glob 攔截 page navigation）
