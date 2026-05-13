# BE Operation → FE Userflow Mapping Rules

> 純 declarative — 規範 backend operation 怎麼分類為 has-ui / no-ui，以及 has-ui operation 怎麼對應到 frontend userflow。**不含**任何步驟流程；步驟流程在 SKILL.md Phase 2。

---

## §1 has-ui / no-ui 分類 Rubric

### §1.1 維度

每個 BE operation 依下列 4 個維度逐一打分，最終以加總規則決定 classification：

| 維度 | 訊號（has-ui） | 訊號（no-ui） | 訊號權重 |
|---|---|---|---|
| Actor | end-user / authenticated user / guest | system / cron / webhook / scheduler / message-broker | 必要條件 |
| Trigger | UAT flow 內可被使用者直接驅動 | 內部事件 / 排程 / async pipeline | 必要條件 |
| Permission | 對外公開或登入後可達 | admin-only / service-account-only / B2B SSO | 加重 no-ui 傾向 |
| Synchronicity | request-response 同步 | fire-and-forget / eventually consistent | 加重 no-ui 傾向 |

### §1.2 判定法則

| 法則 | classification |
|---|---|
| Actor 含 end-user ∧ Trigger 屬於某條 UAT flow | has-ui |
| Actor 全為 system / cron / async 且 Trigger 非 UAT flow | no-ui |
| Actor 含 admin-only ∧ FE TLB 是「管理後台」boundary | has-ui（admin UI） |
| Actor 含 admin-only ∧ FE TLB 是面向 end-user 的 boundary | no-ui（不在當前 FE 範疇） |
| Actor 全為 service-account / 系統間 | no-ui |
| 任何維度與訊號矩陣不吻合（fuzzy 或多重） | ambiguous（Seam A clarify-loop） |

### §1.3 訊號黑名單（強制 no-ui）

下列訊號出現一個就強制 no-ui：

- OpenAPI path 含 `/internal/` / `/system/` / `/webhook/` / `/_admin/` prefix
- BE feature Background actor 為 `cron` / `scheduler` / `message-broker` / `pubsub-subscriber`
- BE activity actor header 為 `system` / `worker` / `consumer`
- contract 含 `x-no-ui: true` 擴充欄位

### §1.4 訊號白名單（強制 has-ui）

下列訊號出現一個就強制 has-ui（除非 §1.3 黑名單同時命中，此時 → ambiguous）：

- contract 含 `x-frontend-binding: <view-id>` 擴充欄位
- BE activity actor header 為 `user` / `end user` / `customer` / `visitor`
- BE feature Background actor 為 `登入使用者` / `訪客` / `會員` / `customer`

---

## §2 BE operation 對應 FE userflow 的粒度

| BE operation 數 | FE userflow 數 | 對應規則 |
|---|---|---|
| 1 BE op | 1 FE userflow | 預設 — 一個 BE op 對一條 userflow |
| N BE ops（同一 UAT step） | 1 FE userflow | composite userflow — 例如「填表 + 預覽 + 送出」3 個 BE op 為同一 userflow |
| 1 BE op | N FE userflows | branch userflow — 例如「送出」依入口分 mobile-app / web / kiosk 三條 userflow |
| 0 BE op | 1 FE userflow | UX-only userflow — 純前端互動（filter、sort、客端搜尋）；標 `be_operation_binding: null` |

> **預設規則**：一律以 1:1 對應為起點；上述 1:N / N:1 / N:0 情境必須由 Seam A 或 Seam B clarify-loop 明確 confirm，不得 implicit 推導。

---

## §3 UAT flow attribution

每個 has-ui BE operation 必須歸屬於至少一條 BE `.activity` UAT flow。歸屬規則：

| 訊號 | UAT flow attribution |
|---|---|
| OpenAPI `x-uat-flow: <flow-id>` | 直接採用 |
| BE activity action node 引用此 operation | 採該 activity 的 flow id |
| BE feature `@uat-flow-<id>` tag | 採該 tag |
| 以上皆無 | ambiguous → Seam A clarify-loop |

---

## §4 GAP report 對 no-ui operation 的記錄欄位

`reports/discovery-uiux-sourcing.md` 的 `## GAP — no-ui operations` 章節對每筆 no-ui operation 必填下列欄位：

| 欄位 | 內容 |
|---|---|
| `op_id` | OpenAPI operationId 或 `<method>:<path>` |
| `source` | `openapi-endpoint` / `activity-action` / `feature-rule` 之一 |
| `reasoning` | 為何判定 no-ui（引用 §1 訊號） |
| `revisit_trigger` | 何時應重新評估（例：「admin UI 上線後」「行動端開發後」） |

---

## §5 不在本檔範疇

- 「使用者 verbatim 推 anchor 名」 — 屬 [`aibdd-discovery::references/rules/frontend-rule-axes.md`](aibdd-discovery::references/rules/frontend-rule-axes.md) §4
- 「UI verb catalog」 — 屬 [`aibdd-discovery::references/rules/frontend-rule-axes.md`](aibdd-discovery::references/rules/frontend-rule-axes.md) §2
- 「coverage matrix」 — 屬 [`userflow-rule-coverage.md`](userflow-rule-coverage.md)
- 「具體 Rule 句型」 — 屬 [`verification-semantics-presets.md`](verification-semantics-presets.md)
