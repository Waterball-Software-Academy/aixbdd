---
name: speckit-aibdd-test-plan
description: Phase 5 Planner — Flow-Oriented Gherkin test plan synthesis. Consumes activities/*.activity + shared dsl.md ⊕ boundary dsl.md + contracts/ + bdd-plan.md and emits test-plan/*.feature (one Scenario per Path, Policy 1 coverage). Phase 2 = Python activity-parser (structural reasoning, no AI); Phase 4 = AI filling with DSL L1 Business Sentences. TRIGGER when 使用者下 /speckit.aibdd.test-plan、/speckit-aibdd-test-plan。
metadata:
  user-invocable: true
  source: project-level dogfooding, unified from legacy extension skill root
---

# speckit-aibdd-test-plan

Phase 5 Planner skill — 從 activity DSL 推 Path → 結構化骨架 → AI 填業務句型 → quality gate。Scenario 表面強制業務語言；mock 機制走 [MOCK] tag + datatable schema 守門。

## §1 REFERENCES

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `aibdd-core::spec-package-paths.md` | global | flat project-wide path SSOT |
| R2 | `aibdd-core::feature-granularity.md` | Phase 3 | feature 粒度 anti-pattern token（filename guard 共用）|
| R3 | `aibdd-core::physical-first-principle.md` | Phase 5 | MR-1 / MR-2 / MR-6 / MR-7 mock & datatable rules |
| R4 | `references/contracts/io.md` | Phase 1 | arguments.yml IO schema |
| R5 | `references/contracts/reason.md` | Phase 2 | Reason 契約 |
| R6 | `references/contracts/quality.md` | Phase 5 | Quality gate（含 Subagent semantic R1-R15 invariants）|
| R7 | `references/contracts/relevance.md` | global | axis 相關性判定 |
| R8 | `references/rules/flow-oriented-gherkin.md` | Phase 4 | flow-oriented Gherkin 寫法（指回 `test-plan-rules.md`）|
| R9 | `references/rules/filename-rename-protocol.md` | Phase 3 | Phase 3 rename 流程 + 守門 |
| R10 | `references/rules/mock-arming.md` | Phase 5 | R13 Mock-Arming Completeness |
| R11 | `references/rules/mock-tag-business-language.md` | Phase 5 | R14 [MOCK] tag + 業務語言 |
| R12 | `references/rules/datatable-schema.md` | Phase 5 | R15 datatable schema |

## §2 SOP

### Phase 1 — BIND parameters

1. READ `${arguments_yml_path}` per [`references/contracts/io.md`](references/contracts/io.md) §Config
2. ASSERT 必填 `SPECS_ROOT_DIR` / `ACTIVITIES_DIR` / `DSL_CORE_PATH` / `DSL_LOCAL_PATH` / `CONTRACTS_DIR`
   2.1 IF 缺: STOP + REPORT specific param
3. ASSERT `BDD_CONSTITUTION_PATH` 存在 + §5.1 含 `filename.convention` + `filename.title_language`
   3.1 IF 缺軸: STOP + REPORT「§5.1 declared axes 缺；Phase 3 rename 必依賴」
4. BIND defaults: `FEATURES_DIR` / `BDD_PLAN_PATH` / `TEST_PLAN_OUT_DIR` / `PATH_COVERAGE_POLICY=node-once` / `PARSER_MODE=mermaid-flowchart-flat`
5. ASSERT `TEST_PLAN_OUT_DIR` 可寫
6. COMPUTE DSL merge view：`DSL_CORE_PATH`（shared `dsl.md`）⊕ `DSL_LOCAL_PATH`（boundary `dsl.md`）（同 id 優先 boundary）

### Phase 2 — REASON skeleton（structural; no AI）

1. TRIGGER `bash .claude/skills/aibdd-core/scripts/bash/activity-parser.sh skeleton --specs-root ${SPECS_ROOT_DIR} --policy ${PATH_COVERAGE_POLICY} --out ${TEST_PLAN_OUT_DIR}`
2. ASSERT parser 對每個 `${ACTIVITIES_DIR}/*.activity` 解析為 Path list（Policy 1）
3. ASSERT 每份 `${TEST_PLAN_OUT_DIR}/*.feature` 骨架（step 全部為註解，尚無 G/W/T）已產出
4. EMIT 預期狀態：本 Phase 產出檔名為 `<activity-slug>.feature`（英文 kebab-case，沿用 activity 檔名 stem）— **這是中間態，不是最終態**

### Phase 3 — RENAME per filename convention

1. EXECUTE Phase 3 rename per [`references/rules/filename-rename-protocol.md`](references/rules/filename-rename-protocol.md) §2-§5
2. EXECUTE 守門兩層 per same §6
   2.1 IF anti-pattern token 命中: STOP + REPORT specific filename + 重做 Phase 3
   2.2 IF schema 違反: STOP + REPORT specific filename + 重做 Phase 3（不繞道進 Phase 4）
3. ASSERT 完成條件 per [`references/rules/filename-rename-protocol.md`](references/rules/filename-rename-protocol.md) §7

### Phase 4 — FORMULATE step-fill

1. LOOP per skeleton scenario step 註解
   1.1 SELECT matching DSL entry（以 L2 DSL Semantics 比對）
   1.2 IF entry 找到:
       1.2.1 WRITE step using entry's L1 Business Sentence Pattern
       1.2.2 IF entry L3 = mock: APPLY [MOCK] tag per [`references/rules/mock-tag-business-language.md`](references/rules/mock-tag-business-language.md) §1
   1.3 ELSE:
       1.3.1 INSERT `# CiC(BDY): no matching DSL entry for "<step intent>"`
   END LOOP
2. ASSERT Scenario 表面**不**含 Mock / channel / endpoint 字樣（per `references/rules/flow-oriented-gherkin.md` R6 + R9）
3. ASSERT 每份 feature 通過 Gherkin lint（平衡 Scenario / Given / When / Then / And / But）

### Phase 5 — QUALITY GATE

1. EXECUTE script checks:
   1.1 TRIGGER `python .claude/skills/clarify-loop/scripts/grep_sticky_notes.py ${TEST_PLAN_OUT_DIR}`
   1.2 TRIGGER `python .claude/skills/speckit-aibdd-test-plan/scripts/check_path_policy.py ${TEST_PLAN_OUT_DIR} --policy ${PATH_COVERAGE_POLICY}`
   1.3 TRIGGER `python .claude/skills/speckit-aibdd-test-plan/scripts/check_dsl_reference.py ${TEST_PLAN_OUT_DIR} --dsl-core ${DSL_CORE_PATH} --dsl-local ${DSL_LOCAL_PATH}`
2. EXECUTE filename last-line guard per [`references/rules/filename-rename-protocol.md`](references/rules/filename-rename-protocol.md) §6
   2.1 IF 違反: STOP + GOTO #3.1 (不回 Phase 4；檔名問題不會因 step-fill 改變)
3. DELEGATE Subagent semantic validation per [`references/contracts/quality.md`](references/contracts/quality.md) §Subagent
   含 R1-R15 全 invariants（R1-R12 ref `references/rules/flow-oriented-gherkin.md`；R13 ref [`references/rules/mock-arming.md`](references/rules/mock-arming.md)；R14 ref [`references/rules/mock-tag-business-language.md`](references/rules/mock-tag-business-language.md)；R15 ref [`references/rules/datatable-schema.md`](references/rules/datatable-schema.md)）
4. ASSERT script + subagent 皆 `ok=true`
   4.1 IF script `ok=false`: GOTO #4.1
   4.2 IF subagent R13 fail: SELECT root cause
       4.2.1 IF root cause 為 test-plan 缺 Given: GOTO #4.1
       4.2.2 IF root cause 為 boundary `dsl.md` 缺 mock-setup entry: STOP + REPORT 指示回 `/speckit.aibdd.bdd-analyze` 補
   4.3 IF subagent R14 fail: 同 R13 root cause 路由
   4.4 IF subagent R15 fail: 同 R13 root cause 路由

### Phase 6 — REPORT

1. EMIT REPORT per `aibdd-core::report-contract.md` §REPORT 匯報（白話文 1-3 句）：
   "Test Plan 完成。產出 N 份 flow-oriented Gherkin（= N 個 activity），共 K 個 Path / Scenario。{若有便條紙則加「尚有 M 張便條紙待釐清」；無則省略}"

## §3 FAILURE & FALLBACK

### Phase 1 fail handling
- IF 必填 param 缺: STOP + REPORT specific param 要求 caller 補 arguments.yml
- IF §5.1 declared axes 缺: STOP + REPORT「Phase 3 rename 必依賴 §5.1；先補 bdd-constitution」

### Phase 2 fail handling
- IF activity-parser script error: STOP + REPORT 退回 caller debug parser
- IF 任一 activity 無 Path 推出（空 activity）: STOP + REPORT specific activity，要求 caller 補 activity 內容

### Phase 3 fail handling
- IF rename 守門 anti-pattern token 命中: REPORT specific filename + 重做 Phase 3 §4
- IF rename 守門 schema 違反: REPORT specific filename + 重做 Phase 3 §4
- 本 skill **不**做推測性改名 retry — 要求 AI 重讀 §5.1 / §6 後手動再算

### Phase 4 fail handling
- IF Scenario 表面殘留 Mock / channel / endpoint 字樣: REPORT specific scenario, GOTO #4.1
- IF Gherkin lint 失敗: REPORT specific feature + 行號, GOTO #4.1

### Phase 5 fail handling
- IF filename last-line guard 違反: GOTO #3.1（檔名問題回 Phase 3）
- IF script `ok=false`: GOTO #4.1（補 step-fill）
- IF subagent R13/R14/R15 fail 且 root cause 為 test-plan 本層: GOTO #4.1
- IF subagent R13/R14/R15 fail 且 root cause 為 boundary DSL（`dsl.md`）: STOP + REPORT 指示回 `/speckit.aibdd.bdd-analyze` 補對應 DSL entry / schema

### Phase 6 fail handling
- IF EMIT 失敗（caller 已斷線）: WRITE summary to `${TEST_PLAN_OUT_DIR}/.report.md` + STOP

## §4 CROSS-REFERENCES

- 由 `/speckit.aibdd.test-plan` command 觸發（`.claude/skills` unified entry）
- 上游：`/aibdd-form-activity`（活動 DSL）+ `/speckit.aibdd.bdd-analyze`（boundary `dsl.md` + bdd-plan）
- 下游：`/speckit.tasks` 將 test-plan 收錄為 acceptance test 階段
- Re-entry 規則：`references/contracts/reason.md` §6
- Registry entry 樣板：`assets/registry/entry.yml`
- test-plan-rules.md（plugin repo 根目錄）— R1-R12 base rules
