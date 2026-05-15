# Coverage Row 顆粒度

- **記什麼**：每個 `(atomic rule × dimension)` cell 對應之 example coverage——`{ coverage_type: example, rule_id, dimension, example_id, feature_path }`。寫入位置：`${TRUTH_FUNCTION_PACKAGE}/coverage/<feature-slug>.coverage.yml`。
- **WHY**：coverage matrix 是回答「rule 是否被測到 + 被哪個 example 測到」的 single source of truth；其他 skill（譬如 `/aibdd-tasks`／`/aibdd-red-execute`）依此推 task 拆分與 fixture 範圍。

## §1 Coverage row 欄位

| 欄位 | 值 | 約束 |
|---|---|---|
| `coverage_type` | `example` | 本 skill **僅**追加 `example` 層；`rule` 層由 `/aibdd-plan` 寫入，不動 |
| `rule_id` | atomic Rule anchor（byte-for-byte 與 `.feature` Rule title 相等） | 不得用 operation-level `dsl.source.rule_id` 取代 |
| `dimension` | 02 階段 dimensions 之一 | `happy_path` / `invalid_input` / `boundary_min` / `boundary_max` / `error_handling` / `state_transition` / `time_dependency` / `idempotency` / `decision_completeness` / `authorization` / `failure_path` |
| `example_id` | Scenario／Scenario Outline 之 anchor（group id 或 row index） | 必對應實際 `.feature` 之 Scenario 名稱或 Examples 列 |
| `feature_path` | canonical repo-relative path 至 `.feature` | 必落於 `${FEATURE_SPECS_DIR}` 下 |
| `cic`（optional） | 當 cell 為空格時帶 CiC marker | `{ kind, where, text }` |

## §2 矩陣覆蓋 invariants

- 每個 `(rule_id × dimension)` cell 必有恰好一筆 `CoverageRow`；若該 cell 無 example 覆蓋 → 必標 `cic` 或 `dimension_na`（含理由）；**不得**留空。
- `dimension` 必出現於 02 階段該 rule 之 `$strategy.dimensions`；不在的 dimension 不得寫入 coverage（避免長出 rule 未要求之維度）。
- `example_id` 必能在 04 之 `$scenario_plan.groups[]` 找到對應 group；找不到 → coverage row 不寫入。

## §3 寫入時機

- 本 sub-SOP **不寫檔**；只 DERIVE 入 `$scenario_plan.coverage_rows[]`。
- 實際寫入 `${TRUTH_FUNCTION_PACKAGE}/coverage/<feature-slug>.coverage.yml` 由 `05-delegate-and-quality-gate` 完成。

# 反例

- ✗ coverage row 之 `rule_id` 用 `op_create_order` 之 operation-level id。**應改為**：用 atomic rule anchor，譬如 `訂單建立成功時系統會回覆受理結果並提供可追蹤的訂單編號`。
- ✗ 為了「補滿矩陣」加 `(rule_id, dimension)` cell 但該 dimension 不在 02 之該 rule strategy。**應改為**：不加。
- ✗ `example_id` 指向不存在於 04 plan 之 group。**應改為**：跳過該 row；或回 04 重新確認 group。
- ✗ 寫入 `coverage_type: rule` 列。**應改為**：本 skill 只寫 `example` 層；`rule` 層之 ownership 屬 `/aibdd-plan`，不動。
- ✓ rule 「金額必須為正數」+ dimensions `[happy_path, invalid_input, boundary_min]` → 3 筆 CoverageRow，分別指向 happy Scenario、invalid Scenario、BVA Outline 之第 1 列。

# 禁止自生

- **不得**生 02 階段未宣告之 dimension 給 coverage row 用。
- **不得**改 `coverage_type: rule` 層之既有資料（屬 `/aibdd-plan` owner）。
- **不得**用 placeholder rule_id（譬如 `"rule_TBD"`）寫 coverage——rule_id 必須對應實際 `.feature` Rule title。
- 違反處置：該 coverage row 不寫入；累積 CiC 至 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`。
