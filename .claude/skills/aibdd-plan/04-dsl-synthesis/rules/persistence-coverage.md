# Persistence coverage 顆粒度（僅當 `$COVERAGE_GATE == not-null-columns`）

- **每個 aggregate-root 必有獨立 builder**：`boundary-map.yml#persistence_ownership` 內列出之每個 entity，**至少**有一條 DSL entry：`L4.preset.handler == ${PERSISTENCE_HANDLER}`（譬如 `aggregate-given`），且 `L4.source_refs.data` 指向該 entity 之 primary table。
- **composite builder 不豁免**：單筆 entry 同時 seed 多 entity rows（譬如 `student-assigned` 同跨 student／journey／stage／assignment）**不**取代 base-entity builder 之獨立存在義務；base entity 仍須有獨立 builder。
- **NOT-NULL 100% 覆蓋**：每條 handler builder 對應之 DBML table，所有 `[not null]`（含 `[pk]`）欄位必須出現在 `param_bindings + datatable_bindings + default_bindings` 之 target 集合中（target 形如 `data/<file>.dbml#<table>.<column>`）。
- **唯二豁免**：
  - (a) `[pk, increment]` 自增欄位（譬如 `id integer [pk, increment]`）
  - (b) DBML 顯式宣告 `[default: ...]` 欄位（譬如 `created_at timestamp [default: \`now()\`]`）
- **慣例 timestamp 不自動豁免**：`created_at`／`updated_at` 若 DBML 未標 `[default: ...]`，**不**自動豁免；想豁免必須在 DBML 加 default modifier（請 specifier 補）。
- **FK NOT-NULL 必直綁**：FK NOT-NULL 欄位（譬如 `responses.assignment_id`、`appointments.assignment_id`）**不得**用 lookup-chain 推論豁免；builder 必須有直接 binding 指向 `data/<file>.dbml#<table>.<fk_column>`。

# 反例

- 把 `journey` aggregate-root 之 builder 省略，只靠 composite `student-assigned` 同時 seed——base-entity builder 仍須獨立存在，否則 coverage gate fail。
- DBML 表有 `created_at TIMESTAMP NOT NULL` 但無 `[default: \`now()\`]`，DSL 卻無 binding——不自動豁免，必須補 binding 或請 specifier 補 DBML default。
- `responses.assignment_id` FK NOT-NULL，builder 寫 `lookup: $journey.assignment.id` 試圖鏈式推論——FK **不可** chain，必須直接 binding `data/<file>.dbml#responses.assignment_id`。
- DBML 欄位 `email_verified boolean [not null]` 無 default，atomic rule 也未提此欄位，builder 自行補 `default: false`——這是自生（rule 沒授權）；應回頭澄清或請 specifier 在 DBML 加 default。

# 禁止自生

- **不得**為了通過 coverage 自編 placeholder value；每個 binding 之 value 必須能在 atomic rule 或 entity 領域 invariant 中找到 majority-behavior 證據。
- **不得**為「我覺得這欄位應該 nullable」就跳過 builder——nullability 是 DBML 真相，本 skill 不重寫；若認為 DBML 設計錯，請 `DELEGATE /clarify-loop` 反饋給 state specifier，**不**就地 bypass。
- **不得**自加 raw 未提之 default modifier 期望（譬如 atomic rule 沒說「狀態預設為 pending」，builder 不得期望 `[default: 'pending']`）。
