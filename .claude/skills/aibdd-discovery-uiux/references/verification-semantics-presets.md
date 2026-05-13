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

## §3 verification mode → step-def binding 暗示

下表給 `/aibdd-red-execute` 與 `/aibdd-form-story-spec` 的下游 step-def 推導參考：

| verification_mode | step-def 慣例（Playwright + playwright-bdd） |
|---|---|
| `locator` | `getByRole(role, { name })` + `.click() / .fill() / .selectOption() / .check()` |
| `visual-state` | `getByRole(role, { name }).waitFor({ state: 'visible' \| 'hidden' })` 或 `expect(getByText(...)).toBeVisible()` |
| `route` | `expect(page).toHaveURL(routePattern)` 或 dialog open assertion |
| `api-binding` | `page.route(beOpPath, mock)` 配 fixture；assertion 在 mock fulfillment 或 record-replay log |

> **本表為 hint，非規約**：實際 step-def code 由 `/aibdd-red-execute` 在 Phase 2 mapping 階段決定。本檔只規範 Rule body 句型。

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
