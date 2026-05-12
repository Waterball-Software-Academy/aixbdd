# BDD Analysis — Quality Gate

Phase 4 的 SR(T) sandwich。分兩層：Script checks（機械式）+ Subagent semantic validation（語意式）。任一 `ok=false` → 回 Phase 3 formulation。

---

## §Script checks

```bash
python .claude/skills/clarify-loop/scripts/grep_sticky_notes.py ${SPECS_ROOT_DIR}
python .claude/skills/aibdd-spec-by-example-analyze/scripts/check_example_coverage.py --args ${arguments_yml_path}
python .claude/skills/aibdd-spec-by-example-analyze/scripts/check_preset_compliance.py --args ${arguments_yml_path}
python .claude/skills/aibdd-spec-by-example-analyze/scripts/check_dsl_binding_trace.py --args ${arguments_yml_path}
```

| Script | 檢查 |
|--------|------|
| `grep_sticky_notes.py` | 所有便條紙（CiC: GAP/ASM/BDY/CON）殘留；回傳 `ok=true/false` |
| `check_example_coverage.py` | 對每條 atomic rule：至少一條 Scenario / Scenario Outline + Examples；`@ignore` tag 已移除 |
| `check_preset_compliance.py` | 所有 Gherkin step（canonicalized）必須出現在**任一** plan DSL entry 的 `L1` given/when/then 模板集合中（package + shared 合併）；`check_dsl_binding_trace.py` 與語意 gate 仍要求每步必須可追溯至正確 operation 之 entry |
| `check_dsl_binding_trace.py` | Scenario / Examples 欄位可追溯到 plan DSL binding 或 OpenAPI/DBML truth；且不修改 DSL |

---

## §Subagent semantic validation

用本模板實例化 subagent prompt：

```
你是 BDD Analysis 的 semantic validator。
讀取下列檔案：
- ${FEATURE_SPECS_DIR}/**/*.feature
- ${TRUTH_FUNCTION_PACKAGE}/coverage/*.coverage.yml
- ${BOUNDARY_PACKAGE_DSL}
- ${BOUNDARY_SHARED_DSL}
- ${CONTRACTS_DIR}/**/*.yml
- ${DATA_DIR}/**/*.dbml
- ${TEST_STRATEGY_FILE}
- .claude/skills/aibdd-spec-by-example-analyze/references/rules/clause-analysis.md（legacy glossary：ClauseBinding 詞彙／形狀；非 runtime SOP）
- .claude/skills/aibdd-spec-by-example-analyze/references/rules/coverage-matrix.md（legacy glossary：矩陣詞表／CiC 空格語意；非 runtime SOP）
- .claude/skills/aibdd-spec-by-example-analyze/reasoning/aibdd-spec-by-example-analyze/01-index-input-truth.md
- .claude/skills/aibdd-spec-by-example-analyze/reasoning/aibdd-spec-by-example-analyze/02-classify-rule-test-strategy.md
- .claude/skills/aibdd-spec-by-example-analyze/reasoning/aibdd-spec-by-example-analyze/03-enumerate-rule-data-values.md
- .claude/skills/aibdd-spec-by-example-analyze/reasoning/aibdd-spec-by-example-analyze/04-plan-scenario-structure.md
- .claude/skills/aibdd-spec-by-example-analyze/reasoning/aibdd-spec-by-example-analyze/05-build-coverage-handoff.md

逐條檢驗下列 checklist；每條附檔案路徑 + 行號 + 一句摘要。回傳 JSON：
{
  "ok": <bool>,
  "summary": "<≤100 字>",
  "violations": [{"check": "<ID>", "where": "<path:line>", "why": "<sentence>"}]
}
```

### Baseline checks（所有 planner 共用）

| ID | 意涵 |
|----|------|
| `CIC_GAP_RESIDUAL` | 無 `CiC(GAP)` 便條紙殘留 |
| `CIC_ASM_RESIDUAL` | 無 `CiC(ASM)` 便條紙殘留 |
| `CIC_BDY_RESIDUAL` | 無 `CiC(BDY)` 便條紙殘留 |
| `CIC_CON_RESIDUAL` | 無 `CiC(CON)` 便條紙殘留 |
| `RULE_UNIT_COVERAGE` | `reasoning/aibdd-spec-by-example-analyze/*.md` 產出的每條 rule strategy / coverage row 至少對應一個 artifact 單位；legacy glossary 不作 runtime coverage source |

### Axis-specific checks（業務例）

| ID | 意涵 |
|----|------|
| `ATOMIC_RULE_EXAMPLE_COVERAGE` | 每條 atomic rule 至少有 1 條 example 覆蓋（Scenario 或 Scenario Outline + Examples 至少一列） |
| `COVERAGE_MATRIX_FULL` | 覆蓋矩陣無空格：每個 (rule, 測試維度) 組合都已填入 example 或已標 CiC 交由 Phase 3 formulation 清掉 |
| `DSL_L1_STEP_PATTERN_COMPLIANCE` | 所有 Gherkin Given / When / Then 句型與 plan `dsl.yml` **L1** canonical 模板一致（機械檢查：`check_preset_compliance.py`） |
| `NO_RULE_WORDING_CHANGE` | atomic rule 本體字詞未被改動（逐字比對 Step 1 輸入的 `.feature` rule draft 與 Step 3 產出）|
| `SPEC_BY_EXAMPLE_CONCRETE` | 所有 Examples 使用具體值；禁用白話佔位符（「某個」/「一些」/「XX」/「正確的」/「錯誤的」） |
| `NO_FEATURE_REORG` | feature 路徑 / 檔名未被本 skill 改動（屬 discovery / operation-partition 管轄） |
| `NO_PLAN_TRUTH_EDIT` | `${BOUNDARY_PACKAGE_DSL}` / `${BOUNDARY_SHARED_DSL}` / `${CONTRACTS_DIR}` / `${DATA_DIR}` / `${TEST_STRATEGY_FILE}` 未被本 skill 改動（屬 `/aibdd-plan` 管轄） |
| `COVERAGE_EXAMPLE_LAYER_ONLY` | 本 skill 僅追加 `coverage_type: example` entries；`coverage_type: rule` 部分保留不動 |
| `NO_REDUCER_METADATA_IN_FEATURE` | `.feature` 不得殘留 analyzer-only metadata：`# @type`、`# @techniques`、`# @dimensions`、`# @merge_decision`、`# @cic`、`# @setup_required`、`# --- reducer:` 等 |
| `RULE_METADATA_RETAINED_OUTSIDE_FEATURE` | 每條 atomic rule 的 type / techniques / dimensions / merge decision / value reasoning 仍存在於 reasoning bundle 或 coverage/handoff；不得因清掉 `.feature` 註解而遺失 |
| `PRECONDITION_SETUP_BOUND` | 每個 Example / Scenario / Scenario Outline 在第一個 When 之前必須有足夠的前置狀態建構：可執行 Given step 必須綁到既有 plan DSL/shared DSL/test-strategy seed；缺 setup mapping → **STOP + REPORT 指示回 `/aibdd-plan`**（不再允許用 inline analysis notes 或 CiC bypass） |
| `AGGREGATE_GIVEN_BUILDER_REACHABILITY` | 對該 Example 之 When step 所需的每個參與 entity（含 aggregate root 與 FK 引用之 child entity），plan DSL 必須有對應的 `aggregate-given` builder（`L4.preset.handler == aggregate-given` AND `L4.source_refs.data` 指該 entity primary table）。Composite aggregate-given **不視為**涵蓋其底層 base entity（譬如 `student-assigned` 不算 `student` 已有 builder）。任一參與 entity 缺 builder → **STOP + REPORT 指示回 `/aibdd-plan`**；禁止用 CiC bypass、禁止發明未列於 plan DSL 的 Given step |
| `BVA_NOT_HAPPY_ONLY` | rule metadata 含 `BVA` 時，Examples 不得僅 `happy_path`（須含 min / max / just-below / just-above / out-of-range 等對應列，或矩陣空格為 CiC） |
| `STATE_TRANSITION_ARTIFACT` | technique 含 `State Transition` 時，reasoning / coverage artifact 須保留起始／事件／目標狀態與非法轉移 trace；不得要求寫回 `.feature` |
| `MERGE_DECISION_TRACE` | 凡 `Scenario Outline`，reasoning / coverage artifact 須保留 `merge_decision.step0_when_then_same`、`step1_given_same`、`outcome` |
| `NO_MERGE_MIXED_WHEN_THEN` | 同一 Outline 之 Examples 不得混用不同 When+Then 結構；成功與失敗路徑模板不同時禁止合併為同一 Outline |
| `MINIMAL_RULE_TARGET_EXAMPLE` | 每個 Example 只驗證所屬 atomic Rule 的目標：後置（回應）不得順手驗 DB state；後置（狀態）不得順手驗 response，除非註明為 dynamic-id bridge |
| `DSL_BINDING_TRACE` | 每個 Scenario step / Examples 欄位可追溯到 matching DSL entry 的 `param_bindings` / `datatable_bindings` / `default_bindings` / `assertion_bindings`，或 OpenAPI/DBML truth |
| `NO_DSL_MUTATION` | `${BOUNDARY_PACKAGE_DSL}` / `${BOUNDARY_SHARED_DSL}` 未被本 skill 修改；缺 binding 時必須 CiC/STOP 回 `/aibdd-plan` |
| `NO_UNKNOWN_RESPONSE_ASSERTION` | Then 不得 assert OpenAPI response schema 或 DSL `assertion_bindings` 未宣告的 response 欄位 |
| `COVERAGE_ATOMIC_RULE_ANCHOR` | coverage `rule_id` 必須是 atomic Rule anchor；不得用 operation-level `dsl.source.rule_id` 取代 |
| `SCENARIO_L1_FROM_PLAN_DSL` | 具體 step 必須可對應到所選 DSL entry 的 `L1` 與 `dsl_l1_pattern_index`；`L4.preset.name` 只用於 `/aibdd-plan` asset 追溯，不得從全域 markdown preset 目錄猜測 |

---

## §完成條件

- Script checks 全 `ok=true`
- Subagent validation `ok=true`
- 匯報：白話文 1–3 句（依 `aibdd-core::report-contract.md` §REPORT 匯報；不輸出 JSON / YAML）
