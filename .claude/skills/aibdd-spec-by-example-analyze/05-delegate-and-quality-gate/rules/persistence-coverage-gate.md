# Persistence Coverage Gate 顆粒度

- **記什麼**：當 boundary profile 之 `persistence_handler.coverage_gate == not-null-columns` 時，每個 renderable example 之 When step 所需的每個參與 entity（含 aggregate root 與被 `$state_ref_pattern` 引用之 child entity），plan DSL 必須有對應之 `$persistence_handler` builder；缺 builder → STOP，**禁止** CiC bypass。
- **WHY**：persistence-driven backend 的 example 若 Given 端缺 entity builder，step-def 跑時會碰 NOT-NULL constraint violation 或 FK missing，整條 example 紅。Plan 階段已宣告該 boundary 採 `not-null-columns` gate 表示「真相要 100% 涵蓋 NOT-NULL 欄位 + FK」，所以 example 階段必須 enforce「每個參與 entity 都有 builder」這個前提。

## §1 三個來源欄位（取自 01-bind-and-load 之 boundary profile READ）

| 欄位 | 含義 | 範例（web-backend） |
|---|---|---|
| `$persistence_handler` | DSL `L4.preset.handler` 對應的 builder 類型 | `state-builder` |
| `$state_ref_pattern` | `L4.source_refs.data` 之 primary state ref 樣式 | `data/<entity>.dbml#<aggregate>` |
| `$coverage_gate` | gate 模式 | `not-null-columns` / `deferred-v1` / `none` |

## §2 Gate 執行流程

- **`$coverage_gate == not-null-columns`**：套用 §3 enforce。
- **`$coverage_gate == deferred-v1`**：SKIP enforce，但寫 reason 入 quality 報告（透明標示「本輪豁免 not-null-columns gate」）。
- **`$coverage_gate == none`**：SKIP enforce 且 quality 報告不需特別標。
- **三者皆非**：boundary profile 配置錯，**STOP** + 回 `/aibdd-plan` 修。

## §3 Enforce 程序（only when `not-null-columns`）

LOOP per `$group` in `$scenario_plan.groups[]`:

1. **識別參與 entity 集合**：該 group 之 When step 需要的所有 entity，含：
   - aggregate root（rule body 提及之主 entity）
   - 被 `$state_ref_pattern` 引用之 child entity（譬如 `student-assigned` 之 `assigned` 引用 `journey` 與 `stage`）
2. **每個參與 entity**：在 `$indexed_truth.dsl_entries`（package + shared 合併）中找：
   - `L4.preset.handler == $persistence_handler`
   - AND `L4.source_refs.data` 對齊 `$state_ref_pattern` 之 primary state ref
   - AND 該 ref 指向**該 entity 之 primary state**（非 composite）
3. **Composite builder 之限制**：
   - 譬如 `student-assigned` builder 不視為涵蓋其底層 `student` 的 builder 義務——`student` 必須有自己的 base entity builder。
   - 同理：`student` 不涵蓋 `journey`／`stage`，每個獨立 entity 必須各自有 builder。
4. **每個 Given step 引用既有 entity ID**（譬如 `學員 X`、`旅程 Y`、`stage Z`）：必須由 plan DSL 之 `$persistence_handler` 串鏈唯一構造出來，不得依賴未宣告之隱式 fixture。

## §4 失敗處置（任一參與 entity 缺對應 builder）

1. **STOP** 本 group 之 DELEGATE。
2. 累積 CiC(GAP) 至 `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`：
   ```yaml
   - kind: GAP
     where: "<feature_path>:<rule_anchor> group <example_id>"
     text: "persistence_handler builder 缺：entity <name> 未在 plan DSL 找到對應 $persistence_handler"
   ```
3. REPORT 給使用者：列出缺 builder 之 entity 名稱與所屬 group，提示回 `/aibdd-plan` 補 entity-level `$persistence_handler` builder。
4. **禁止 CiC bypass**：不得把該 group 標 CiC 後續跑（這會導致 example 寫到 .feature 但 step-def 無 fixture，整條紅）。
5. **禁止發明 Given**：不得在 example 加 plan DSL 未列舉之 Given step（譬如「`Given 學員 X 已建立`」但 DSL 無對應 builder）。
6. **禁止假設 composite 涵蓋 base**：composite given 對應之 entity ≠ 該 composite 之底層 base entity——必須分別有 builder。

# 反例

- ✗ rule 之 example 需 `學員 X` + `旅程 Y` + `stage Z`；plan DSL 只有 `student-assigned` composite builder，缺 `student`／`journey`／`stage` 三個 base entity builder——硬讓 example 過 gate。**應改為**：STOP + CiC(GAP)，回 `/aibdd-plan` 補三個 base builder。
- ✗ `$coverage_gate == deferred-v1` 但 quality 報告未標 reason。**應改為**：報告含 `"persistence coverage gate: deferred-v1（reason: ...）"` 之透明說明。
- ✗ example 之 Given 寫 `Given 學員 X 已存在` 但 DSL 缺對應 builder，靠 step-def fixture 默默 seed。**應改為**：CiC(GAP)，回 `/aibdd-plan`。
- ✓ rule 之 example 需 `學員 X` + `旅程 Y` + `stage Z`；plan DSL 含三個 base builder + `student-assigned` composite → gate PASS。

# 禁止自生

- **不得**自填 builder 給缺項——builder 之 ownership 屬 `/aibdd-plan`。
- **不得**把 `coverage_gate` 從 `not-null-columns` 自降為 `deferred-v1` 來繞過 gate——`coverage_gate` 之 ownership 屬 boundary profile（kickoff 階段）。
- **不得**用 fixture closure 之預設值掩蓋缺 builder——即使 step-def 能跑，缺 builder 仍違 plan 真相完整性。
- 違反處置：quality gate VETO（`AGGREGATE_GIVEN_BUILDER_REACHABILITY` 或對應 handler 之 reachability veto），整輪作廢。
