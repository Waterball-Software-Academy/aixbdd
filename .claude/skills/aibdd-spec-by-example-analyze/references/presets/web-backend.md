# Preset: web-backend

Backend（HTTP API + persistence layer）Boundary 之 Gherkin step pattern preset。

## §0 Four-Layer Mapping Schema

每筆 entry 必採下列四層 mapping。Scenario 表面只呈現 L1；L2–L4 供 step-def／validator／mock 層讀取。

```yaml
- id: <snake-case-id>
  L1:
    given: "<Given 句型模板；可省（only-When 類 entry）；留 {param} 佔位>"
    when:  "<When 句型模板>"
    then:  "<Then 句型模板>"      # 可多條（列表）
  L2:
    context: "<action 發生時使用者狀態>"
    role:    "<執行者角色>"
    scope:   "<語意涵蓋範圍：system | boundary | entity>"
  L3:
    type: mock | direct-call | state-check | state-setup | ...
  L4:
    # Mock 類（type=mock）：
    channel_type: HTTP | IPC | FileSystem | ...
    channel_name: "<endpoint / channel / path>"
    method: GET | POST | ...        # HTTP 類必填
    payload_schema: |               # 或 reference: "contracts/...yml#path"
      <JSON schema-like / dataclass-like 描述>
    # Non-mock 類：
    summary: "<一行摘要；不展開 UI component / internal state 細節>"
```

### 強制條款

- L1 句型**絕不**出現 channel 名、endpoint URL、payload schema、method——Scenario 表面一律業務語言。
- Mock 類 entry 之 L4：channel_type + channel_name + (payload_schema OR reference) 一個都不能少。
- Non-mock 類 entry 之 L4 = summary 一行；過多細節屬 step def 實作層，不入 DSL。

## §1 適用條件

- **API Layer**：HTTP endpoint（REST／gRPC／GraphQL 皆可；本 preset 以 REST 為主）
- **持久化 Layer**：DB／Repository（提供 States Prepare 直接注入 + States Verify 直接查詢）

僅有 API Layer 而無持久化（pure in-memory service），或僅有 persistence 而無 API（資料整合 batch job）→ 自訂 preset。

## §3 Handler 清單

對應 `aibdd-core/assets/boundaries/web-backend/step-classification.yml::routes`：

| Handler | Gherkin 位置 | 用途 |
|---------|-------------|------|
| `state-builder` | Given | 直接寫 DB 建立前置 aggregate 狀態 |
| `operation-invoke`  | Given / When | HTTP 操作（讀寫由 contract 決定） |
| `operation-response-success-and-failure` | Then | 驗證 HTTP status / exception envelope |
| `operation-response-success-readmodel`  | Then | 驗證 response body / projection |
| `state-verifier`  | Then | 驗證 DB aggregate 持久化狀態 |
| `time-control`    | Given / When | 控 boundary-visible clock |
| `external-stub`   | Given | 跨 boundary 之 provider stub |

**Handler 選取程序**：見 [`decision-trees/web-backend-handler.yml`](decision-trees/web-backend-handler.yml)（結構化查表）。

## §4 Variant 清單

位於 `aibdd-core/assets/boundaries/web-backend/variants/`：

| Variant | 對應技術棧 |
|---------|-----------|
| `python-e2e` | Python 3.11+ / Behave / FastAPI TestClient / SQLAlchemy / PostgreSQL |
| `python-ut`  | Python 3.11+ / Behave / Service 直呼 / FakeRepo |
| `java-e2e`   | Java 17+ / Cucumber / Spring Boot MockMvc / JPA |

Variant 本身不增 handler 種類，只改實作語法。

## §5 與 machine routing SSOT 的關係

- machine routing SSOT：`.claude/skills/aibdd-core/assets/boundaries/web-backend/step-classification.yml`
- preset 級契約：`.claude/skills/aibdd-core/references/preset-contract/web-backend.md`
- 各 handler 之 `required_source_kinds` 與 plan-time 履約規則：`.claude/skills/aibdd-core/assets/boundaries/web-backend/plugin-contract.md`（human-readable，原本內嵌於 yaml 之 `dsl-writing-rules-for-each-part`）

| routing id | 對應本 preset 之語意角色 |
|---|---|
| `state-builder` | States → Given state setup |
| `state-verifier`  | States → Then persisted state verify |
| `operation-invoke`  | Operations → Invoke HTTP |
| `operation-response-success-and-failure` | Operations → Result / outcome verify |
| `operation-response-success-readmodel`  | Operations → Response body / projection verify |
| `time-control`    | Mock → Boundary-visible clock |
| `external-stub`   | Mock → Cross-boundary provider stub |

**不得**將舊稱呼 `command`／`query` 當成 `dsl.yml` 的 routing id——對外 truth 為上表 hyphenated handler。
