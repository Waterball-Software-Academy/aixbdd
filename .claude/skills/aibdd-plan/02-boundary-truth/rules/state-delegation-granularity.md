# State 委派顆粒度

- **唯一寫入管道**：`${TRUTH_BOUNDARY_ROOT}/data/**` 之**任何**檔案產生／修改，**必須**透過 `$BOUNDARY_PROFILE.state_specifier.skill` 之 `DELEGATE`；**禁止**本 skill 手寫 DBML／YAML state 檔。
- **一個 aggregate-root 一次 DELEGATE**：每個 aggregate-root entity 為一次 DELEGATE 之單位；child entity／value object 由 specifier 在同次 payload 內處理。
- **payload 必含**：`entity_name`／`fields`（含 type、nullable、PK、unique、`[default: ...]` 標註）／`relations`（FK 與基數）／`state_transitions`（觸發 → 終態）／`state_subset_visible_to_acceptance`（哪些 fields 可被 acceptance test 驗）／`source_refs`（指回 atomic rule、activity step）。
- **profile=none**：若 `state_specifier.skill = none`，`$BOUNDARY_DELTA.entities` **必須**為空。
- **NOT-NULL 必有依據**：nullability 須來自 atomic rule「前置（狀態）」或「後置（狀態）」之原文依據；無依據則保留 nullable，等 specifier 之澄清流程處理。

# 反例

- 手刻 `data/orders.yml` 內含 `entities:` 直接落地——bypass specifier，違反 ownership。
- 把 3 個無關 aggregate-root entity 包進一次 payload——specifier 之單位是 aggregate-root，跨聚合根包裝會讓 NOT-NULL coverage gate 失準。
- payload 漏 `state_transitions`，導致下游 acceptance-visible state subset 無法決定，DSL `aggregate-then` 無 anchor。
- payload 對 `created_at` 標 `NOT NULL` 但無 `[default: \`now()\`]` 且 atomic rule 未提此欄位——下游 coverage gate 會要求 builder 補 binding，但 rule 中根本沒有對應的 raw 證據，等於要求 DSL 自生。

# 禁止自生

- **不得**自填 raw 未提之欄位（譬如 raw 寫「會員可下單」，payload 不得自加 `kyc_status`／`credit_limit`／`risk_tier` 等隱性前提欄位）。
- **不得**自決定欄位之 NOT-NULL／DEFAULT；nullability 與 default 之 truth 出處必須是 atomic rule 或 entity 領域 invariant；沒依據則保留 nullable 並交 specifier 澄清。
- **不得**自加 raw 未提之 FK 關係；relation 必須能在 atomic rule／activity flow 中找得到對應出處（譬如 rule 寫「訂單屬於某會員」→ relation order→member 有依據）。
