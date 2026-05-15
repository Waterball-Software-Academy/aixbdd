# Verification Semantics Presets

> 純 declarative — 規範 frontend Rule 內**使用者互動驗證語意**的 4 種 preset 句型樣板與互斥/可組合規則。**不含**任何步驟流程；步驟流程在 SKILL.md Phase 3。

---

## §1 4 種 verification mode

每條 atomic Rule 必標 exactly one `verification_mode`：

| verification_mode | 涵義 | 對應 UI verb 類別（見 [`aibdd-discovery::references/rules/frontend-rule-axes.md`](aibdd-discovery::references/rules/frontend-rule-axes.md) §2） |
|---|---|---|
| `locator` | 透過 accessible name + role 鎖定 DOM 元件並驗證其存在 / 可互動 | input / state-change（click / type / select / submit / toggle / focus） |
| `visual-state` | 驗證頁面/元件的視覺狀態（render / hide / loading / empty / error） | visual / feedback（render / hide / spinner / skeleton / empty-state / error-visual / toast） |
| `route` | 驗證使用者所在 URL 或路由 / 對話視窗開啟狀態 | navigation（navigate / open-dialog / close-dialog） |
| `api-binding` | 標注 UI 互動對應的 BE operation；該 Rule 對應的 step-def 會在 fixture 層綁定 API mock / record-replay | 任何能 trigger BE 副作用的 UI 互動（submit / select / toggle / navigate 後送 API） |

> **互斥規則**：一條 Rule 只能標一個 verification_mode。如需多重驗證，必拆成多條 Rule（一條 locator + 一條 visual-state 等）。

> **可組合規則**：同一個 UIVerbBinding 可衍生 N 條 Rule，每條對應不同 verification_mode。

---

## §2 Rule body 句型樣板

每個 preset 的 Gherkin Rule body 都遵守 [`aibdd-core::gherkin-rule-body-prefix-policy/four-rules-prefix.md`](aibdd-core::gherkin-rule-body-prefix-policy/four-rules-prefix.md) 的 prefix 規約。樣板使用 `{{ var }}` 表示填值佔位符。

### §2.1 locator preset

```gherkin
Rule: 使用者必須能透過 [{{ accessible_name }}] {{ role }} 觸發 {{ ui_verb }}
  - 元件 anchor: role={{ role }}, name="{{ accessible_name }}"
  - 互動類型: {{ ui_verb }}
  - 期望狀態: enabled / visible
  - verification_mode: locator
```

| 適用 ui_verb | 句型範例 |
|---|---|
| `click` | `Rule: 使用者必須能透過 [送出退款] 按鈕觸發點擊` |
| `type` | `Rule: 使用者必須能在 [Email] 欄位輸入電子郵件` |
| `select` | `Rule: 使用者必須能在 [國家] 下拉選單選擇選項` |
| `submit` | `Rule: 使用者必須能透過 [送出表單] 按鈕觸發送出` |

### §2.2 visual-state preset

```gherkin
Rule: 在 {{ trigger_condition }} 時，畫面必須 {{ visual_outcome }} [{{ anchor }}]
  - 對應 anchor: {{ anchor }}
  - visual_outcome: render / hide / spinner / skeleton / empty-state / error-visual / toast
  - verification_mode: visual-state
```

| 適用 ui_verb | 句型範例 |
|---|---|
| `render` | `Rule: 提交退款後，畫面必須顯示 [退款摘要]` |
| `hide` | `Rule: 載入完成後，畫面必須隱藏 [載入轉圈]` |
| `spinner` | `Rule: 送出申請時，畫面必須顯示 [送出中] loading 圖示` |
| `empty-state` | `Rule: 無歷史退款時，畫面必須顯示 [尚無退款紀錄] 空狀態` |
| `error-visual` | `Rule: 送出失敗時，畫面必須顯示 [送出失敗] 錯誤橫幅` |
| `toast` | `Rule: 提交退款成功時，畫面必須跳出 [退款已送出] 提示條` |

### §2.3 route preset

```gherkin
Rule: 完成 {{ trigger }} 後，使用者必須被導向 {{ route_pattern }}
  - 對應 ui_verb: navigate / open-dialog / close-dialog
  - 期望 URL pattern: {{ route_pattern }}
  - verification_mode: route
```

| 適用 ui_verb | 句型範例 |
|---|---|
| `navigate` | `Rule: 完成結帳後，使用者必須被導向 /checkout/success` |
| `open-dialog` | `Rule: 點擊 [編輯個資] 後，必須開啟個資編輯對話視窗` |
| `close-dialog` | `Rule: 完成個資編輯後，個資編輯對話視窗必須關閉` |

### §2.4 api-binding preset

```gherkin
Rule: 觸發 {{ ui_verb }} [{{ accessible_name }}] 時，必須對應呼叫 BE operation {{ be_operation_id }}
  - 對應 anchor: role={{ role }}, name="{{ accessible_name }}"
  - 對應 BE operation: {{ be_operation_id }}（OpenAPI operationId 或 method:path）
  - 對應 BE feature: {{ be_feature_path }}
  - verification_mode: api-binding
```

| 適用情境 | 句型範例 |
|---|---|
| 表單送出 → POST | `Rule: 點擊 [送出退款] 時，必須對應呼叫 BE operation submitRefund` |
| 下拉選擇 → GET | `Rule: 在 [城市] 下拉選擇選項時，必須對應呼叫 BE operation listCities` |
| 切換開關 → PATCH | `Rule: 切換 [通知開關] 時，必須對應呼叫 BE operation togglePreferenceNotification` |

> **重要**：句型中**禁止**寫 HTTP method / path / status code，一律以 BE operation id 引用，避免 leak backend 細節（per [`aibdd-discovery::references/rules/frontend-rule-axes.md`](aibdd-discovery::references/rules/frontend-rule-axes.md) §2.1 backend-verb 黑名單）。

---

## §3 verification_mode → sentence_part binding（規約）

每條 atomic Rule 標的 `verification_mode` 必須對應到 [`aibdd-core::assets/boundaries/web-frontend/handler-routing.yml`](aibdd-core::assets/boundaries/web-frontend/handler-routing.yml) 既有 `sentence_part` 之一。下表為單一 routing source — `/aibdd-red-execute` Phase 2 依 `handler-routing.yml` 走，不另建對應表。

| verification_mode | Gherkin 位置 | sentence_part | handler 檔 |
|---|---|---|---|
| `locator` | Given / When（互動前置或目標操作） | `ui-action` | [`handlers/ui-action.md`](aibdd-core::assets/boundaries/web-frontend/handlers/ui-action.md) |
| `locator` | Then（可達 / 可見 / 可聚焦） | `ui-readmodel-then` | [`handlers/ui-readmodel-then.md`](aibdd-core::assets/boundaries/web-frontend/handlers/ui-readmodel-then.md) |
| `visual-state` | Then（render / hide / spinner / skeleton / empty-state / error-visual / disabled / value） | `ui-readmodel-then` | [`handlers/ui-readmodel-then.md`](aibdd-core::assets/boundaries/web-frontend/handlers/ui-readmodel-then.md) |
| `visual-state` | Then（toast / inline-error / banner / status-pill — 成功失敗反饋類） | `success-failure` | [`handlers/success-failure.md`](aibdd-core::assets/boundaries/web-frontend/handlers/success-failure.md) |
| `route` | Given / Background（落點到指定路由） | `route-given` | [`handlers/route-given.md`](aibdd-core::assets/boundaries/web-frontend/handlers/route-given.md) |
| `route` | Then（URL pathname / query / hash 斷言） | `url-then` | [`handlers/url-then.md`](aibdd-core::assets/boundaries/web-frontend/handlers/url-then.md) |
| `api-binding` | Given（per-scenario 行為 override — 回應 status / body / latency） | `api-stub` | [`handlers/api-stub.md`](aibdd-core::assets/boundaries/web-frontend/handlers/api-stub.md) |
| `api-binding` | Then（驗證 outgoing call 的 method / path / body / query 形狀） | `api-call-then` | [`handlers/api-call-then.md`](aibdd-core::assets/boundaries/web-frontend/handlers/api-call-then.md) |

### §3.1 對應規約

- 每條 Rule 標一個 `verification_mode` + 一個 Gherkin keyword（Given / When / Then），二者組合**唯一**決定 `sentence_part`。同一個 `verification_mode` 在不同 Gherkin 位置會路由到不同 handler，這是預期行為，不是衝突。
- 同一個 UI verb binding 衍生多條 Rule 時（per §1 可組合規則），每條 Rule 各自選一格走自己的 routing。
- discovery-uiux 階段**不**渲染 step-def 程式碼；本表只決定下游 routing 落點。Playwright API surface / forbidden / Storybook I4 binding 一律由各 handler 檔自身規約。

### §3.2 routing 之外的物理對應

| verification_mode | 必須 carry 的額外輸入 | 物理對應解析者 |
|---|---|---|
| `api-binding` | `be_operation_binding`（sibling BE `openapi.yml` 的 `operationId`） | `/aibdd-red-execute` Phase 2 讀 sibling BE `contracts/openapi.yml` 解析為 method + path |
| `route` | `route_pattern`（相對於 frontend variant 的 route map） | `route-given` / `url-then` 的 `L4.source_refs.route` 解析 |
| `locator` / `visual-state` | `anchor`（role + accessible name） | `ui-action` / `ui-readmodel-then` 依 Storybook I4 binding 從 Story export args 對齊（per [`handler-routing.yml`](aibdd-core::assets/boundaries/web-frontend/handler-routing.yml) 邊界不變式 I4） |

### §3.3 失敗條件

下列情況 fail Phase 5 gate（與 §4 並列）：

- Rule 標的 `verification_mode` 無法在 §3 表查到對應 `sentence_part`（例如錯字、用了未支援的 mode）。
- `api-binding` Rule 缺 `be_operation_binding`，或 `be_operation_binding` 在 sibling BE `openapi.yml` 找不到對應 `operationId`。
- `route` Rule 缺 `route_pattern`，或 `route_pattern` 在 frontend variant 的 route map 找不到對應 entry。
- `locator` / `visual-state` Rule 的 `anchor` 不是 `role=... , name="..."` 形狀，或 Storybook 對應 Story export 缺 accessible-name args（per I4 missing-truth stop）。

---

## §4 不允許的 verification_mode 寫法

下列寫法皆 fail Phase 5 `UIUX_VERIFICATION_MODE_PRESENT` / `UIUX_NO_BE_VERB_LEAK` gate：

- Rule 無 `verification_mode` 標注
- Rule 含 backend 黑名單動詞（POST / GET / PUT / DELETE / persist / 200 / 4xx / database / commit transaction / publish event / enqueue / dispatch / process job）
- Rule 同時標兩個 verification_mode（必拆兩條）
- `verification_mode` 值不在 enum {locator, visual-state, route, api-binding}
- `api-binding` Rule 缺 `be_operation_id` 引用
- `locator` Rule 缺 `accessible_name` 或 `role`

---

## §5 不在本檔範疇

- 「accessible name 怎麼取」 — 屬 [`aibdd-discovery::references/rules/frontend-rule-axes.md`](aibdd-discovery::references/rules/frontend-rule-axes.md) §4.1
- 「UI verb catalog enum」 — 屬 [`aibdd-discovery::references/rules/frontend-rule-axes.md`](aibdd-discovery::references/rules/frontend-rule-axes.md) §2
- 「coverage 完整性 / 缺哪幾種 mode 算 gap」 — 屬 [`userflow-rule-coverage.md`](userflow-rule-coverage.md)
- 「Rule prefix 寫作規範（必須 / 允許 / 禁止 / 預設）」 — 屬 [`aibdd-core::gherkin-rule-body-prefix-policy/four-rules-prefix.md`](aibdd-core::gherkin-rule-body-prefix-policy/four-rules-prefix.md)
