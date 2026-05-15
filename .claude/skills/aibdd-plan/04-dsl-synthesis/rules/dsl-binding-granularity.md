# DSL binding 顆粒度

- **placeholder ↔ binding 1:1**：L1 每個 `{placeholder}` 對應 `param_bindings` 或 `assertion_bindings` 之**恰好一筆**，never both、never none。
- **param_bindings**：給 sentence-critical L1 placeholder；**不得**塞 contract input 而 placeholder 未在 L1 出現（除非該 input 是 fixture／stub 實作細節）。
- **datatable_bindings**：scenario-visible 但非 sentence-critical 之業務 input；column name 為 DSL-facing key、`target` 為物理欄位。
- **default_bindings**：操作所需 input 但 atomic rule 表明 vary 之值不影響 majority behavior；每筆必含 `target`／`value`／`reason`（指回 atomic rule）／`override_via`（datatable 或不准 override）。
- **operation entry exact coverage**：`param_bindings + datatable_bindings + default_bindings` 之集合**恰好**等於 contract `request.params + request.body.fields + non-transport headers (required=true)`，**多一個或少一個**皆 fail。Transport／ambient headers（譬如 `X-Actor-Role`）由 gate policy 排除。
- **target prefix allow-list**：
  - `contracts/<file>.yml#<op>.request.{params|body|headers}.<name>` 或 `...response.<field>`
  - `data/<file>.dbml#<table>.<column>`（preferred for `web-service` 之 DBML）
  - `data/<file>.yml#<entity_id>.<field>`（legacy YAML）
  - `response:$.<jsonpath>`（含 `response:$.__http.*` for transport assertions）
  - `fixture:...`／`stub_payload:...`／`literal:...`
- **readability pressure**：operation entry 之 L1 sentence parameters **≤ 3**、datatable parameters **≤ 6**（after defaults）；違者必須把 input 推到 default 或 split entry。
- **datatable business projection**：datatable cell 為**業務 column**，**禁止**塞 raw JSON／YAML／DTO／DB-shape；nested aggregate 用 `group` 與 `item_field` 讓 handler 還原。
- **UI handler 之 component anchor**（frontend）：`ui-action`／`ui-readmodel-then` 之 `L4.source_refs.component` 必指向具體 story export（`<Component>.stories.ts::<ExportName>`），**不**指向單一 component 檔（boundary invariant I4）。

# 反例

- L1 含 `{訂單號}` 但 binding 同時放在 `param_bindings` 與 `assertion_bindings`——違反 1:1。
- operation entry 之 contract `request.body.fields` 有 4 個 required，但 DSL 只綁 3 個——`check_dsl_entries.py` 必 fail（exact coverage 失敗）。
- `default_bindings` 缺 `reason` 或 `override_via`——defaults 變成隱藏行為，無 reason 等於黑箱。
- L1 sentence parameters 7 個——readability gate 失敗，必須改寫 entry 或推 default。
- datatable cell 塞 `{"items":[{"sku":"A","qty":2}]}` 之 raw JSON——違反 business projection 原則，應拆 column 並用 `group`／`item_field`。
- frontend `ui-action` entry 之 `L4.source_refs.component = "Button.tsx"`——非 story export，違反 invariant I4。

# 禁止自生

- **不得**自填 raw 未提之 binding 目標（譬如 raw 寫「金額不可為負」，DSL 不得綁到 `[1, 100000]` 區間之 datatable）。
- **不得**為「補完 required input」自加 default value；每筆 default 之 value 必須能在 atomic rule 中找得到 majority-behavior 證據。
- **不得**自加 raw 未提之 datatable column（譬如 atomic rule 沒提 `discount_code`，datatable 不得自開該 column）。
