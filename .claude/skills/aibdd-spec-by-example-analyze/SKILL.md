---
name: aibdd-spec-by-example-analyze
description: Phase 5 BDD Analyze — Clause Analysis + 覆蓋矩陣 → 最小必要 Example 句型集。消費 `/aibdd-plan` 產出的 boundary/package truth（features、dsl.yml、contracts、data、test-strategy），DELEGATE `/aibdd-form-feature-spec` 落 .feature（含 Examples），並寫入 package coverage。TRIGGER when 使用者下 /speckit.aibdd.bdd-analyze、/speckit-aibdd-bdd-analyze。本 skill 為 preset SSOT：所有 step pattern preset 在 references/presets/。
metadata:
  user-invocable: true
  source: project-level dogfooding, unified from legacy extension skill root
---

# aibdd-spec-by-example-analyze

Phase 5 業務例 analyzer skill — 把 `/aibdd-discovery` 的 atomic rule 翻成最小必要 Spec-by-Example 集合；L4 physical mapping **只讀** `/aibdd-plan` 產出的 `dsl.yml` / OpenAPI / DBML / test-strategy truth。preset SSOT 之所在。

## §1 REFERENCES

```yaml
references:
  - path: references/role-and-contract.md
    purpose: 角色定位 + L1-L4 職責拆分 + scope 邊界
  - path: references/contracts/io.md
    purpose: arguments.yml IO schema
  - path: references/contracts/quality.md
    purpose: Subagent semantic validation invariant + script checks
  - path: references/relevance.md
    purpose: axis 相關性判定
  - path: references/rules/clause-analysis.md
    purpose: Legacy — Given/When/Then clause 拆解詞彙表（reasoning phases SSOT 取代）
  - path: references/rules/coverage-matrix.md
    purpose: Legacy — 測試維度詞彙表（reasoning phases SSOT 取代）
  - path: references/rules/feature-syntax.md
    purpose: Gherkin syntax for example-fill mode
  - path: references/presets/README.md
    purpose: presets 子樹索引；preset SSOT 入口
  - path: references/presets/web-backend.md
    purpose: web-backend boundary 對應 preset patterns（與 aibdd-core boundary asset 對齊）
  - path: references/promotion-gate.md
    purpose: DSL promotion gate 判定（新版 boundary DSL 下目前 no-op/future work）
  - path: references/forbidden-mutations.md
    purpose: 本 skill 禁寫 artifact 清單
  - path: aibdd-core::physical-first-principle.md
    purpose: physical-first 原則 + L4 mapping 規則 + MIP / MR rules
  - path: aibdd-core::artifact-partitioning.md
    purpose: 四份 artifact 分工矩陣
  - path: aibdd-core::spec-package-paths.md
    purpose: boundary-aware package path SSOT
```

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `aibdd-core::physical-first-principle.md` | global | physical-first 原則 + L4 mapping 規則 + MIP / MR rules |
| R2 | `aibdd-core::artifact-partitioning.md` | global | 四份 artifact 分工矩陣 |
| R3 | `aibdd-core::spec-package-paths.md` | global | boundary-aware package path SSOT |
| R4 | `references/role-and-contract.md` | Phase 1-2 | 角色定位 + L1-L4 職責拆分 + scope 邊界 |
| R5 | `references/contracts/io.md` | Phase 1 | arguments.yml IO schema |
| R7 | `references/contracts/quality.md` | Phase 4 | Subagent semantic validation invariant + script checks |
| R8 | `references/relevance.md` | global | axis 相關性判定 |
| R9 | `references/rules/clause-analysis.md` | glossary | **Legacy**：Given/When/Then 部位對應；clause 拆解程序以 reasoning phases 為準 |
| R10 | `references/rules/coverage-matrix.md` | glossary | **Legacy**：測試維度詞表；矩陣填空程序以 reasoning phases 為準 |
| R11 | `references/rules/feature-syntax.md` | Phase 3 | Gherkin syntax for example-fill mode |
| R12 | `references/presets/` | Phase 2-3 | step pattern preset SSOT（preset 由 plan DSL `entries[].L4.preset.name` 派生）|
| R13 | `references/promotion-gate.md` | Phase 5 | DSL promotion gate 判定（新版 boundary DSL 下目前 no-op/future work） |
| R14 | `references/forbidden-mutations.md` | global | 禁寫 artifact 清單 |
| R15 | `reasoning/aibdd-spec-by-example-analyze/01-index-input-truth.md` | Phase 2 | 索引 `/aibdd-plan` output：features / dsl.yml / OpenAPI / DBML / test-strategy / preset |
| R16 | `reasoning/aibdd-spec-by-example-analyze/02-classify-rule-test-strategy.md` | Phase 2 | atomic rule → 決策樹測試策略 + internal reducer metadata（供 coverage / handoff 使用，不回寫 `.feature`） |
| R17 | `reasoning/aibdd-spec-by-example-analyze/03-enumerate-rule-data-values.md` | Phase 2 | 依 DSL binding / contract / data truth 枚舉 Given/When/Then 具體值 |
| R18 | `reasoning/aibdd-spec-by-example-analyze/04-plan-scenario-structure.md` | Phase 2 | Scenario vs Outline 合併決策（Step0/Step1 + datatable shape） |
| R19 | `reasoning/aibdd-spec-by-example-analyze/05-build-coverage-handoff.md` | Phase 2 | Diff/Reconcile/CiC + ClauseBinding + CoverageRow + plan DSL trace |
| R20 | `.claude/skills/aibdd-plan/scripts/python/resolve_plan_paths.py` | Phase 1 | 將 `arguments.yml` 展開成 plan output truth paths |
| R21 | `.claude/skills/aibdd-plan/references/dsl-output-contract.md` | Phase 1-5 | plan DSL entry / L4 binding contract |
| R22 | `.claude/skills/aibdd-core/assets/boundaries/web-backend/handler-routing.yml`（含 `handlers.*` policy） | glossary | **READ-only**：`sentence_part`／`handler`／Gherkin `keyword` 路由為 boundary preset asset SSOT；`/aibdd-plan` 已寫入 `dsl.yml`。歷史 `sentence-parts-framework.md` 僅 Tombstone。 |

## §2 SOP

### Phase 1 — BIND `/aibdd-plan` output context
> produces: `$$args_path`, `$$plan_paths`, `$$plan_output_axis`

1. LOAD `aibdd-core::physical-first-principle.md`
2. LOAD `aibdd-core::artifact-partitioning.md`
3. LOAD `.claude/skills/aibdd-plan/references/dsl-output-contract.md`
4. `$$args_path` = DERIVE absolute arguments path from caller payload else `${workspace_root}/.aibdd/arguments.yml`
5. READ `$$args_path` per [`references/contracts/io.md`](references/contracts/io.md) §Config
6. ASSERT required plan keys exist: `SPECS_ROOT_DIR`, `PLAN_SPEC`, `PLAN_REPORTS_DIR`, `TRUTH_BOUNDARY_ROOT`, `TRUTH_FUNCTION_PACKAGE`, `FEATURE_SPECS_DIR`, `BOUNDARY_PACKAGE_DSL`, `BOUNDARY_SHARED_DSL`, `TEST_STRATEGY_FILE`
   6.1 IF 缺: STOP + REPORT 指示回 `/aibdd-discovery` 或 `/aibdd-plan` 綁定路徑
7. `$$plan_paths` = TRIGGER `python3 ".claude/skills/aibdd-plan/scripts/python/resolve_plan_paths.py" "$$args_path"`
8. ASSERT `$$plan_paths.ok == true`
   8.1 IF false: STOP + REPORT resolver error
9. READ `${BDD_CONSTITUTION_PATH}` 全文 and ASSERT §5 filename axes 無 TODO
   9.1 IF 任一軸 TODO: STOP + REPORT 指示跑 `/speckit.aibdd.author-constitution`
10. ASSERT paths exist where required: `features_dir`, `boundary_package_dsl`, `test_strategy_file`, `truth_boundary_root`
11. `$$plan_output_axis` = DERIVE bundle from `$$plan_paths`, constitution, and DSL output contract

### Phase 2 — REASON spec-by-example pipeline（reasoning phases SSOT）
> produces: `$$indexed_truth`, `$$rule_strategy`, `$$rule_test_data`, `$$scenario_plan`, `$$reason_handoff`, `$$feature_file_tasks`

0. **`sentence_part` / `handler` / Gherkin `keyword`**：由 `.claude/skills/aibdd-core/assets/boundaries/web-backend/handler-routing.yml`（routes + handlers）與 `.claude/skills/aibdd-core/references/preset-contract/web-backend.md`（preset 級契約）定義 SSOT，`/aibdd-plan` Phase 6 已寫入 `dsl.yml`；本 skill 依 R22 **唯讀**對齊，**不得**在本 skill 內重新發明路由或對照表。歷史檔 `.claude/skills/aibdd-plan/references/sentence-parts-framework.md` 僅 Tombstone。
1. `$$indexed_truth` = THINK per [`reasoning/aibdd-spec-by-example-analyze/01-index-input-truth.md`](reasoning/aibdd-spec-by-example-analyze/01-index-input-truth.md)，input=`$$plan_output_axis`
2. `$$rule_strategy` = THINK per [`reasoning/aibdd-spec-by-example-analyze/02-classify-rule-test-strategy.md`](reasoning/aibdd-spec-by-example-analyze/02-classify-rule-test-strategy.md)，input=`$$indexed_truth`
3. `$$rule_test_data` = THINK per [`reasoning/aibdd-spec-by-example-analyze/03-enumerate-rule-data-values.md`](reasoning/aibdd-spec-by-example-analyze/03-enumerate-rule-data-values.md)，input=`$$rule_strategy` + `$$indexed_truth.plan_dsl_index` + contract/data/test-strategy indexes
4. `$$scenario_plan` = THINK per [`reasoning/aibdd-spec-by-example-analyze/04-plan-scenario-structure.md`](reasoning/aibdd-spec-by-example-analyze/04-plan-scenario-structure.md)，input=`$$rule_test_data`
5. `$$reason_handoff` = THINK per [`reasoning/aibdd-spec-by-example-analyze/05-build-coverage-handoff.md`](reasoning/aibdd-spec-by-example-analyze/05-build-coverage-handoff.md)，input=`$$scenario_plan` + `$$indexed_truth`
6. ASSERT `$$reason_handoff` 內每條 atomic rule 已具備 reducer metadata：`type`、`techniques`、`dimensions`（見 R16）；metadata 僅可存在於 reasoning / coverage / handoff，**不得**要求回寫 `.feature`
7. ASSERT 指派 **BVA** 之 rule 在 `$$rule_test_data` 中至少有一組邊界代表值或 CiC(BDY)；否則 STOP
8. ASSERT 指派 **State Transition** 之 rule 具 `from/event/to` 或等價狀態枚舉；否則 STOP
9. ASSERT 每個 renderable Example / Scenario / Scenario Outline 已具備前置狀態建構分析；下列子規則 **皆為 hard-stop**，不得用 CiC(GAP) 旁路、不得自行發明 Given：
   9.0 `$$boundary_profile` = READ `aibdd-core::boundary-type-profiles/${boundary_type}.profile.yml` per [`aibdd-core::boundary-profile-contract.md`](aibdd-core::boundary-profile-contract.md)；`$boundary_type` 取自 `${BOUNDARY_YML}#boundaries[0].type`
       9.0.1 `$persistence_handler` = COMPUTE `$$boundary_profile.persistence_handler.handler_id`
       9.0.2 `$persistence_state_ref_pattern` = COMPUTE `$$boundary_profile.persistence_handler.state_ref_pattern`
       9.0.3 `$persistence_coverage_gate` = COMPUTE `$$boundary_profile.persistence_handler.coverage_gate`
       9.0.4 ASSERT `$persistence_handler` non-empty AND `$persistence_state_ref_pattern` non-empty AND `$persistence_coverage_gate ∈ {"not-null-columns", "deferred-v1", "none"}`；違反時 STOP + REPORT 指示回 `/aibdd-kickoff` 或 `/aibdd-plan` 補 boundary profile 之 `persistence_handler` 區塊
       9.0.5 BRANCH `$persistence_coverage_gate`
              `not-null-columns` → 套用 9.A–9.D（preset 啟用 entity coverage gate）
              `deferred-v1`      → SKIP 9.A–9.D，記錄 reason="profile coverage_gate=deferred-v1"，繼續 step 10
              `none`             → SKIP 9.A–9.D，記錄 reason="profile coverage_gate=none"，繼續 step 10
   9.A 識別該 Example 的 When step 所需的所有參與 entity（含 aggregate root 與被 `${$persistence_state_ref_pattern}` 引用的 child entity）
   9.B 對每個參與 entity，必須在 plan DSL（local + shared）中找到對應的 `${$persistence_handler}` builder（`L4.preset.handler == ${$persistence_handler}` AND `L4.source_refs.data` 符合 `${$persistence_state_ref_pattern}` 樣式並指向該 entity 的 primary state ref）；composite builder（同條 entry seed 多個 entity）**不算**涵蓋其底層 base entity 的 builder 義務（譬如 `student-assigned` 不視為涵蓋 `student` 的 builder）
   9.C 對每個 Given step 所引用的既有 entity ID（如 `學員 X`、`旅程 Y`、`stage Z`），必須能由 plan DSL 的 `${$persistence_handler}` 串鏈唯一構造出來，不得依賴未宣告的隱式 fixture
   9.D IF 任一參與 entity 缺對應 plan DSL `${$persistence_handler}` builder 或串鏈不可達：**STOP + REPORT 指示回 `/aibdd-plan` 補 entity-level `${$persistence_handler}`**；**禁止**改用 CiC(GAP) 標註後繼續、**禁止**發明未列於 plan DSL 的 Given step、**禁止**假設 composite given 已涵蓋 base entity
10. ASSERT 每個 **Scenario Outline** 合併群組附 internal `merge_decision` trace（見 R18）；若 Step0 不通過仍合成 Outline → STOP
11. SCAN `$$reason_handoff` 是否引入 `test-strategy.yml` / plan DSL 未列舉之外部依賴
    11.1 IF 有: STOP + REPORT 指示回 `/aibdd-plan` 補 dependency edge / external-stub DSL
12. ASSERT `$$reason_handoff.coverage_rows` 對 `(rule × dimension)` 無空格 — 空格必須已是 CiC 標記附理由
13. ASSERT `$$reason_handoff.clause_bindings[*].dsl_entry_id` 均存在於 `$$indexed_truth.plan_dsl_index`
    13.1 IF 任一缺失: WRITE CiC(GAP) + STOP + REPORT 指示回 `/aibdd-plan` 補 DSL mapping
14. ASSERT `$$reason_handoff` 不產生或修改 DSL entries
15. IF matching DSL entry 含 datatable：ASSERT 符合 [`references/rules/feature-syntax.md`](references/rules/feature-syntax.md) 與該 entry preset 慣例
16. `$$feature_file_tasks` = DERIVE feature-file task list from `$$reason_handoff.examples`, grouping by target feature path; each task payload must contain exactly one `target_path`, the subset of reasoning / coverage / clause bindings / examples for that file, and the atomic rule ids covered by that file
17. ASSERT every target feature file referenced by `$$reason_handoff.examples` appears in exactly one `$$feature_file_tasks` item
18. ASSERT every `$$feature_file_tasks[*]` is self-contained for `/aibdd-form-feature-spec` example-fill execution and does not require cross-task mutable state

### Phase 3 — DELEGATE formulation + write artifacts

1. ASSERT `$$feature_file_tasks` non-empty
2. `$multi_feature_files` = MATCH length(`$$feature_file_tasks`) > 1
3. `$subagent_supported` = JUDGE current runtime supports feature-file subagent / task parallel execution
4. BRANCH `$multi_feature_files`
   true  → GOTO #3.5
   false → GOTO #3.11
5. BRANCH `$subagent_supported`
   true  → GOTO #3.6
   false → GOTO #3.8
6. LOOP per `$task` in `$$feature_file_tasks`
   6.1 TRIGGER one feature-file task as parallel subagent with payload {target_path: `$task.target_path`, mode: "example-fill", reasoning: `$task`}
   END LOOP
7. WAIT all feature-file subagent tasks and ASSERT all completed `ok=true`
8. MARK feature-file todo queue from `$$feature_file_tasks`
9. LOOP per `$task` in marked feature-file todo queue
   9.1 DELEGATE `/aibdd-form-feature-spec` with payload {target_path: `$task.target_path`, mode: "example-fill", reasoning: `$task`}
   END LOOP
10. GOTO #3.12
11. `$single_task` = DERIVE the only item from `$$feature_file_tasks`
12. DELEGATE `/aibdd-form-feature-spec` with payload {target_path: `$single_task.target_path`, mode: "example-fill", reasoning: `$single_task`}
13. WRITE `${TRUTH_FUNCTION_PACKAGE}/coverage/*.coverage.yml` example 層（`coverage_type: example`），若 coverage dir 不存在則建立
14. ASSERT `${BOUNDARY_PACKAGE_DSL}` / `${BOUNDARY_SHARED_DSL}` 未被修改
15. ASSERT 所有 atomic rule 至少有 1 條 example 覆蓋
16. ASSERT Gherkin 符合 matching DSL entry 的 preset step pattern
17. ASSERT feature output contains no analyzer-only metadata comments or tags（例如 `@type` / `@techniques` / `@dimensions` / `@merge_decision` / `@cic` / `@setup_required`）；reducer metadata 必須留在 reasoning / coverage / handoff

### Phase 4 — QUALITY GATE

1. EXECUTE script checks per [`references/contracts/quality.md`](references/contracts/quality.md) §Script checks
   1.1 IF 任一 script `ok=false`: GOTO #3.1
2. DELEGATE Subagent semantic validation per [`references/contracts/quality.md`](references/contracts/quality.md) §Subagent semantic validation invariants
   2.1 IF subagent 回 `ok=false`:
      2.1.1 IF 根因為 plan truth 缺 binding / contract / data target: STOP + REPORT 指示回跑 `/aibdd-plan`
      2.1.2 ELSE: GOTO #3.1
3. ASSERT script + subagent 皆 `ok=true`

### Phase 5 — PROMOTION gate

1. EXECUTE per [`references/promotion-gate.md`](references/promotion-gate.md) §2 scan
2. IF gate unavailable for `dsl.yml` package model: SKIP with report note（no-op）
3. IF gate 觸發 and supports package `dsl.yml`: WRITE `${CURRENT_PLAN_PACKAGE}/promotion-proposal.md`

### Phase 6 — REPORT

1. EMIT REPORT per `aibdd-core::report-contract.md` §REPORT 匯報（白話文 1-3 句）：
   "BDD Analysis 完成。依 `/aibdd-plan` 的 dsl.yml / contract / data truth 產出 .feature Examples 與 package coverage；未修改 DSL / contracts / data / test-strategy。{若有便條紙則加「尚有 N 張便條紙待釐清」；無則省略}"

## §3 FAILURE & FALLBACK

### Phase 1 fail handling
- IF `/aibdd-plan` resolver 失敗或 required truth path 缺: STOP + REPORT 指示回跑 `/aibdd-plan`
- IF plan quality report 缺或 plan gate 未過: STOP + REPORT 指示回上游補完
- IF constitution §5 任一軸 TODO: STOP + REPORT 指示跑 `/speckit.aibdd.author-constitution`

### Phase 2 fail handling
- IF plan DSL entry 無 preset: STOP + REPORT 指示回 `/aibdd-plan` 補 DSL L4 preset
- IF matching preset 檔不存在: STOP + REPORT specific preset path
- IF feature 無 matching DSL entry: WRITE CiC(GAP) + STOP + REPORT 指示回 `/aibdd-plan`
- IF 新外部依賴未列於 `test-strategy.yml` / DSL external-stub: STOP + REPORT 指示回 `/aibdd-plan`
- IF datatable schema 違反: REPORT specific entry, GOTO #2.14 重新套用 feature-syntax / preset
- IF rule 缺 `type` / `techniques` / `dimensions` reducer metadata，或 metadata 被回寫進 `.feature`: GOTO #2.2 重跑 RP-02
- IF BVA / State Transition 產物不完整: GOTO #2.3 重跑 RP-03
- IF Example 缺前置狀態建構分析，或缺 setup source 卻產生未列於 DSL 的 Given: STOP + REPORT 指示回 `/aibdd-plan` 補 setup DSL / seed mapping
- IF 非法 Outline 合併: GOTO #2.4 重跑 RP-04

### Phase 3 fail handling
- IF DELEGATE form-feature-spec 失敗（filename guard 觸發）: REPORT 退回 caller 重新 Discovery Operation Partition
- IF multi-feature task bundle 中任一 target feature path 缺 task、重複 task 或 task payload 非 self-contained: STOP + REPORT specific target path and task partition defect
- IF runtime 支援 subagent/task 平行執行卻未優先採用 feature-file 平行 task: GOTO #3.3 重選執行策略
- IF 任一 feature-file subagent/task 失敗: REPORT failed target path + STOP
- IF WRITE package coverage 失敗: REPORT IO error + STOP
- IF DSL / contract / data / test-strategy 被偵測為修改: STOP + REPORT owner conflict

### Phase 4 fail handling
- IF script checks `ok=false`: GOTO #3.1 重做 formulation
- IF subagent semantic validation `ok=false` 且根因為 plan truth: STOP + REPORT 指示回 `/aibdd-plan`
- IF subagent semantic validation `ok=false` 且根因為本層: GOTO #3.1

### Phase 5 fail handling
- IF promotion-gate-scan.sh 失敗: REPORT script error + STOP（promotion 是非阻塞 phase，但 script 不能壞）

### Phase 6 fail handling
- IF EMIT 失敗（caller 已斷線）: WRITE summary to `${SPECS_ROOT_DIR}/.bdd-analysis-report.md` + STOP

## §4 CROSS-REFERENCES

- 由 `/speckit.aibdd.bdd-analyze` command 觸發（`.claude/skills` unified entry）
- DELEGATE `/aibdd-form-feature-spec`（example-fill mode）
- 上游：`/aibdd-plan` 產出 boundary/package physical mapping truth (`dsl.yml`, contracts, data, test-strategy)
- 下游：`/speckit.tasks` + `/speckit.implement` 處理 implementation gap
- DSL promotion 後續：`/speckit.aibdd.promote-dsl`
- Re-entry 規則：見 [`reasoning/aibdd-spec-by-example-analyze/05-build-coverage-handoff.md`](reasoning/aibdd-spec-by-example-analyze/05-build-coverage-handoff.md)
- Registry entry 樣板：`assets/registry/entry.yml`
