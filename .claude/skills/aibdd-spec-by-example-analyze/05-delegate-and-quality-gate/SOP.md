# SOP

輸入 `$scenario_plan`（04 產出）、`$indexed_truth`（01 產出，含 `persistence: { handler, state_ref_pattern, coverage_gate }`）。落地產出：`${FEATURE_SPECS_DIR}/**/*.feature`（**僅**經 DELEGATE）、`${TRUTH_FUNCTION_PACKAGE}/coverage/<feature-slug>.coverage.yml`、`${PLAN_REPORTS_DIR}/bdd-analyze-cic.md`、`${PLAN_REPORTS_DIR}/bdd-analyze-quality.md`。

1. **ASSERT：persistence coverage gate**（僅當 `$indexed_truth.persistence.coverage_gate == not-null-columns`）— 規則見 `rules/persistence-coverage-gate.md`。
   - LOOP per `$group` in `$scenario_plan.groups[]`：對該 group 之 When step 所需 entity 集合，ASSERT 每個 entity 在 `$indexed_truth.dsl_entries` 內有對應之 `$persistence_handler` builder（`L4.preset.handler == $persistence_handler` AND `L4.source_refs.data` 對齊 `$state_ref_pattern` 之 primary state ref）。
   - 缺 builder → **STOP** + 累積 CiC(GAP) 並提示回 `/aibdd-plan` 補 entity-level `$persistence_handler`；**禁止** CiC bypass、**禁止**發明未列於 plan DSL 的 Given step、**禁止**假設 composite given 已涵蓋 base entity。
   - `coverage_gate ∈ {deferred-v1, none}` → SKIP，記 reason 入 quality 報告。

2. **DERIVE：feature-file tasks**
   - `$feature_file_tasks` = GROUP `$scenario_plan.groups[]` by `feature_path`。
   - 每個 task payload = `{ target_path, mode: "example-fill", reasoning: { groups[], coverage_rows[], precondition_setup[], dsl_binding_refs[] }, atomic_rule_ids[] }`。
   - ASSERT 每個 group 之 `feature_path` 恰對應一個 task；ASSERT 每個 task self-contained。

3. **DELEGATE：`/aibdd-form-feature-spec` mode=example-fill（per feature path）** — 規則見 `rules/feature-spec-delegation.md`。
   - LOOP per `$task` in `$feature_file_tasks`：`DELEGATE /aibdd-form-feature-spec` with `$task`；ASSERT 回傳 `ok=true`。
   - 失敗則收集失敗 `target_path` 後 **STOP**（不續跑其他 task），REPORT 阻塞點。
   - 多 task 時優先 subagent 並行；runtime 不支援並行則 sequential，行為等價。

4. **WRITE：coverage rows**
   - LOOP per `$row` in `$scenario_plan.coverage_rows[]`：
     4.1 寫入 `${TRUTH_FUNCTION_PACKAGE}/coverage/<feature-slug>.coverage.yml`（目錄不存在則 CREATE）。
     4.2 APPEND `$row`（`coverage_type: example`）；**不**動既有 `coverage_type: rule` 列。

5. **SKIP：deterministic check 腳本** — `references/contracts/quality.md` §1 已空置；**不得**再要求執行已刪除之 `check_*`／`plan_paths`。**直接進** step 6。

6. **JUDGE：semantic verdict（Q1–Q4）** — 規則見 `rules/quality-gate-rubric.md`、`../references/contracts/quality.md` §2–§5。
   - 以 `../references/contracts/quality-gate-prompt.template.md` 實例化 prompt（subagent 或本流程 THINK 二擇一）。
   - 評 Q1 Truth fidelity / Q2 Example completeness / Q3 Binding traceability / Q4 Minimal rule-target focus；判 veto。
   - `verdict ∈ {PASS, SOFT_FAIL, VETO}`；VETO 必含 `vetoes[]` 含 evidence。

7. **WRITE：reports**
   - WRITE `${PLAN_REPORTS_DIR}/bdd-analyze-quality.md`：含 step 6 之 semantic verdict（JSON shape 見 `../references/contracts/quality.md` §5）。
   - IF CiC markers 非空 → WRITE `${PLAN_REPORTS_DIR}/bdd-analyze-cic.md` 逐筆列 `{kind, where, text}`。
   - IF `verdict == VETO` → **STOP**，REPORT vetoes 給使用者；不續跑 step 8。

8. **EMIT 給使用者**（fire-and-forget）：列本輪變更摘要（新增 Scenario／Outline 數 per feature path、新增 coverage rows 數、語意 verdict、CiC 便條紙數），回上層 SKILL.md step 6 之 handoff 一句話。
