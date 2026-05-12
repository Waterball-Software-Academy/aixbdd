# Preset: web-backend

Backend（有 HTTP API + persistence layer）Boundary 的 Gherkin step pattern preset。

---

## §0 Four-Layer Mapping Schema

本 preset 的 step pattern entry **必採下列四層 mapping**。Scenario 表面只呈現 L1 業務句型；L2-L4 供 step-def 實作 / validator / mock 層讀取。

### §0.1 Entry Schema（YAML）

```yaml
- id: <snake-case-id>                    # preset entry 識別碼，全域唯一於本 preset
  L1:                                    # Business Sentence Pattern — feature file 表面採用的業務語言句型
    given: "<Given 句型模板，留 {param} 佔位>"  # 可省（only-When 類 entry）
    when:  "<When 句型模板>"
    then:  "<Then 句型模板>"              # 可多條（列表）
  L2:                                    # DSL Semantics — 語意 / Context / Role
    context: "<action 發生的使用者狀態>"
    role:    "<執行者角色>"
    scope:   "<語意涵蓋範圍：system / boundary / entity>"
  L3:                                    # Technical Pattern — 執行機制分類
    type: mock | direct-call | state-check | state-setup | ...
  L4:                                    # External Contract / Payload — mock 類必具體，non-mock 類可摘要
    # Mock 類（type=mock）：
    channel_type: HTTP | IPC | FileSystem | ...
    channel_name: "<endpoint / channel / path>"
    method: GET | POST | ...                 # HTTP 類必填
    payload_schema: |                        # 或 reference 指向 contracts/...
      <JSON schema-like / dataclass-like 描述>
    reference: "contracts/<yaml#path>"       # 可選，與 payload_schema 二擇一
    # Non-mock 類（type ∈ {direct-call, state-check, state-setup, ...}）：
    summary: "<一行摘要；不展開 UI component / internal state 細節>"
```

### §0.2 強制條款

- **Scenario 表面一律業務語言**（test-plan-rules.md R6 + R9）— L1 句型絕不出現 channel 名、endpoint URL、payload schema、method
- **Mock 類 entry 的 L4 必具體**：channel_type + channel_name + (payload_schema OR reference) 一個都不能少
- **Non-mock 類 entry 的 L4** = summary 一行，避免污染 preset；過多細節屬 step def 實作層，不屬 DSL

## §1 適用條件

本 preset 適用的 boundary 必須同時具備：

- **API Layer** — HTTP endpoint（REST / gRPC / GraphQL 皆可，本 preset 以 REST 為主）
- **持久化 Layer** — DB / Repository（提供 States Prepare 直接注入 + States Verify 直接查詢）

若 boundary 僅有 API Layer 而無持久化（pure in-memory service），或僅有 persistence 而無 API（資料整合 batch job），需自訂 preset。

---

## §2 子活動入口

Reason §3.⑦ preset step pattern 套用的實際步驟：

1. 讀 `overview.md` 取後設決策樹（4 抽象角色：States Prepare / Operation Invocation / Operation Result Verifier / States Verify，加 Mock（時間 / 跨 Boundary））
2. 對每個 Gherkin 子句套用 §2 決策樹 → 得抽象角色分類
3. 依 `overview.md §3 抽象→handler 映射表` 找到對應 handler type
4. 讀 `handlers/<type>.md` 取該 handler 的 Trigger 辨識 / 任務 / BDD 模式 / 共用規則
5. 讀 `variants/<variant>.md` 取該語言的程式碼 pattern（`variant` 由 `${ATDD_LANGUAGE}` 或 feature tag 決定）

---

## §3 Handler 清單

位於 `handlers/`：

| Handler | Gherkin 位置 | 用途 |
|---------|-------------|------|
| `aggregate-given` | Given | 直接寫 DB 建立前置 aggregate 狀態 |
| `command` | Given / When | 執行 HTTP POST/PUT/PATCH/DELETE |
| `query` | When | 執行 HTTP GET |
| `success-failure` | Then | 驗證 HTTP status / exception |
| `readmodel-then` | Then | 驗證 Query 的 response body |
| `aggregate-then` | Then | 驗證 DB 中的 aggregate 狀態 |

---

## §4 Variant 清單

位於 `variants/`：

| Variant | 對應技術棧 |
|---------|-----------|
| `python-e2e` | Python 3.11+ / Behave / FastAPI TestClient / SQLAlchemy / PostgreSQL |
| `python-ut` | Python 3.11+ / Behave / Service 直呼 / FakeRepo |
| `java-e2e` | Java 17+ / Cucumber / Spring Boot MockMvc / JPA |

Variant 本身不增 handler 種類，只改實作語法。

---

## §5 與 `handler-routing.yml`（boundary preset routing SSOT）的關係

本文件中 **preset 級**的 step pattern、`overview.md`、抽象決策樹，與 **`dsl.yml`** 所使用的 **routing id**（`sentence_part`、`handler`、`http-operation` 等）**必須**與機械來源對齊：

`.claude/skills/aibdd-core/assets/boundaries/web-backend/handler-routing.yml`

以及契約：`aibdd-core/references/preset-contract/web-backend.md`。

| `handler-routing.yml` routing id | 對應本 preset 文件中常見語意角色 |
|---------|--------------------|
| `aggregate-given` | States → Given state setup |
| `aggregate-then` | States → Then persisted state verify |
| `http-operation` | Operations → Invoke HTTP（讀／寫由 operation contract 決定） |
| `success-failure` | Operations → Result / outcome verify（status／exception／envelope） |
| `readmodel-then` | Operations → Response body / projection verify |
| `time-control` | Mock → Boundary-visible clock |
| `external-stub` | Mock → Cross-boundary / provider stub |

**不得**將本檔表中舊稱呼 `command`／`query` 當成 `dsl.yml` 的 routing id — 對外 truth 為上表 hyphenated handler。

歷史：`.claude/skills/aibdd-plan/references/sentence-parts-framework.md` 已廢止，僅留 Tombstone；勿再宣稱其為 SSOT。

---

## §6 擴充點

新增 handler：在 `handlers/` 放 `<handler-name>.md`，並於 §3 更新清單；`overview.md §3` 映射表同步更新。

新增 variant：在 `variants/` 放 `<variant-name>.md`，並於 §4 更新清單。
