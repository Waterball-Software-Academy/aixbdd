# Indexed-Truth Bundle 顆粒度

- **記什麼**：`/aibdd-plan` 已 accepted 真相之**索引快照**——plan paths、merged DSL entries（package + shared）、OpenAPI operation index（per operationId）、DBML table／field index、test-strategy edges、boundary profile（含 persistence handler triple）、feature files 之 `Rule:` block 列表。
- **WHY**：本 skill 後續 4 個 sub-SOP（02–05）每步都要查 plan 真相；一次 READ 並結構化索引可避免每步重讀大檔，也讓「未在索引中」這件事成為清楚的 STOP 條件。
- **不記什麼**：DSL entry 之逐字內容（保留 reference 即可；具體 L1 句型在用時直查）、contract YAML 全文、DBML 全文。索引只記 lookup keys（entry id、operationId、table name、rule anchor）。
- **完整性 invariants**：
  - 每個 DSL entry 必有 `L1`、`L4.preset.name`、`L4.surface_kind`、`L4.source_refs`；缺則該 entry 視為不可用，列 CiC(GAP)。
  - 每個 feature file 必有 ≥1 `Rule:` block；`Rule:` 內每條 rule 必有 `rule_anchor`、`raw_rule_title_line`、`body_lines`。
  - boundary profile 必有 `persistence_handler.{handler_id, state_ref_pattern, coverage_gate}` 三件齊。

# 反例

- ✗ 把 contract YAML 全文塞進 `$contract_index.operations[id]`——只記 lookup 必要欄位（required inputs、response fields、status codes），其餘走 reference。
- ✗ 把 DSL entry 之完整 L4 binding 表 inline 進 indexed-truth bundle——只記 entry id 與 surface kind；用時 lookup。
- ✗ 把 optional 之 `aibdd-plan-quality.md` 或 sidecar preset markdown 當成 persistence／coverage gate 的 SSOT——**`$indexed_truth.persistence` 只許來自** `BOUNDARY_YML` → `aibdd-core/assets/boundaries/<type>/profile.yml`。
- ✓ `$indexed_truth.feature_files[].rules[].rule_anchor = "<exact Rule title byte-for-byte>"`；downstream 之 `coverage_rows[].rule_id` 與此 anchor 完全相等。

# 禁止自生

- **不得**在 indexed-truth bundle 內**新增** DSL entry／operation／table／rule——bundle 只能反映 plan 既有真相之**子集**。
- **不得**對缺項自填空白 placeholder（譬如「假設 `persistence_handler.handler_id = state-builder`」）——缺 profile 三件之一即 STOP，由 `/aibdd-plan` 補。
- **不得**在 profile 缺 `persistence_handler` 完整三件時用 `aibdd-plan-quality.md` 或 `PRESET_KIND` 旁路代替——缺則 STOP，由上游補 **boundary profile**。
- 違反處置：STOP + 累積 CiC(GAP)／CiC(CON) 到 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`，並向使用者列出阻塞項。
