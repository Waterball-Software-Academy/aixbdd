---
name: aibdd-red-evaluate
description: Evaluate a completed AIBDD Red Worker run using runtime-visible feature files, step definitions, and test report evidence. Veto false red and hollow red before Green may consume the run.
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-red-evaluate

Evaluate whether a completed Red Worker run produced a legal, meaningful red.

<!-- VERB-GLOSSARY:BEGIN — auto-rendered from programlike-skill-creator/references/verb-cheatsheet.md by render_verb_glossary.py; do not hand-edit -->
> **Program-like SKILL.md — self-contained notation**
>
> **3 verb classes** (type auto-derived from verb name):
> - **D** = Deterministic — no LLM judgment required; future scripting candidate
> - **S** = Semantic — LLM reasoning required
> - **I** = Interactive — yields turn to user
>
> **Yield discipline** (executor 鐵律): **ONLY** `I` verbs yield turn to the user. `D` and `S` verbs MUST NOT pause for user reaction. In particular:
> - `EMIT $x to user` is **fire-and-forget** — continue immediately to the next step; do not wait for acknowledgment.
> - `WRITE` / `CREATE` / `DELETE` are side effects, **not** phase boundaries — execution continues to the next sub-step.
> - Phase transitions (Phase N → Phase N+1) and sub-step transitions are **non-yielding**.
> - Mid-SOP messages of the form 「要繼續嗎？」/「先 review 一下？」/「先 checkpoint？」/「先停下來確認？」/「want me to proceed?」/「should I continue?」are **FORBIDDEN**. The ONLY way to ask the user is an `[USER INTERACTION] $reply = ASK ...` step.
> - `STOP` / `RETURN` are terminations, not yields — no next step follows.
>
> **SSA bindings**: `$x = VERB args` (productive steps name their output);
> `$x` is phase-local; `$$x` crosses phases (declared in phase header's `> produces:` line).
>
> **Side effect**: `VERB target ← $payload` — `←` arrow = "write into target".
>
> **Control flow**: `BRANCH $check ? then : else` (binary) or indented arms (multi);
> `GOTO #N.M` = jump to Phase N step M (literal `#phase.step`).
>
> **Canonical verb table** (T = D / S / I):
>
> | Verb | T | Meaning |
> |---|---|---|
> | READ | D | 讀檔 → bytes / text |
> | WRITE | D | 寫檔（內容已備好） |
> | CREATE | D | 建立目錄 / 空檔 |
> | DELETE | D | 刪檔（rollback） |
> | COMPUTE | D | 純運算 |
> | DERIVE | D | 從既定規則推算 |
> | PARSE | D | 字串 → in-memory 結構 |
> | RENDER | D | template + vars → string |
> | ASSERT | D | 斷言 invariant；fail-stop |
> | MATCH | D | regex / pattern 比對 |
> | TRIGGER | D | 啟動 process / subagent / tool / script；output 可 bind |
> | DELEGATE | D | 呼叫其他 skill |
> | MARK | D | 紀錄狀態（譬如 TodoWrite） |
> | BRANCH | D | 分支（吃 `$check` / `$kind` binding） |
> | GOTO | D | 跳 `#phase.step` literal |
> | IF / ELSE / END IF | D | 條件 sub-step |
> | LOOP / END LOOP | D | 迴圈（必標 budget + exit） |
> | RETURN | D | 提前結束 phase |
> | STOP | D | 終止整個 skill |
> | EMIT | D | 輸出已生成資料（fire-and-forget；**不 yield**，continue 下一 step） |
> | WAIT | D | 等待已 spawn 的 process |
> | THINK | S | 內部判斷（不印 user） |
> | CLASSIFY | S | 多類別分類 → enum 之一 |
> | JUDGE | S | 二元語意判斷 |
> | DECIDE | S | 從 user reply / context 推結論 |
> | DRAFT | S | 生成 prose / 訊息 |
> | EDIT | S | LLM 推 patch 改既有檔 |
> | PARAPHRASE | S | 改寫 / 翻譯 prose |
> | CRITIQUE | S | 批評 / 建議 |
> | SUMMARIZE | S | 抽取重點 |
> | EXPLAIN | S | 對 user 解釋 why |
> | ASK | I | 問 user 等回應（仍配 `[USER INTERACTION]` tag）；**唯一允許 yield turn 給 user 的 verb**。**Planner-level skill** 對 user 的提問**必須 `DELEGATE /clarify-loop`**，不得直接 `ASK`（其他角色的 skill 自決）。 |
<!-- VERB-GLOSSARY:END -->

## §1 REFERENCES

```yaml
references:
  - path: references/evaluate-input-contract.md
    purpose: Defines Red evaluate payload and artifact pointer requirements
  - path: references/evaluate-report-schema.md
    purpose: Defines Red evaluate PASS FAIL Veto report fields
  - path: references/hollow-red-rubric.md
    purpose: Defines semantic hollow-red Veto signals for failing tests that do not test user-visible behavior
```

## §2 SOP

### Phase 1 — RECEIVE Red evidence
> produces: `$$payload`, `$$target_feature_files`, `$$report_path`, `$$runtime_feature_root`, `$$step_def_root`, `$$step_def_files`

1. `$$payload` = READ caller payload with `red_handoff` or explicit artifact pointers.
2. `$$target_feature_files` = PARSE `target_feature_files` per [`references/evaluate-input-contract.md`](references/evaluate-input-contract.md).
3. `$$report_path` = PARSE final test report path from payload or `red_handoff.behavior_test_report.report_path`.
4. `$$runtime_feature_root` = PARSE resolved `${FEATURE_ARCHIVE_RUNTIME_REF}` root from payload or runtime snapshot.
5. `$$step_def_root` = PARSE resolved `${STEP_DEFINITIONS_RUNTIME_REF}` root from payload or runtime snapshot.
6. `$$step_def_files` = PARSE touched step definition files from payload or `red_handoff.step_defs_touched`.
7. ASSERT every required artifact pointer exists; on failure STOP with `missing_red_evaluation_artifact`.

### Phase 2 — LOAD visible artifacts
> produces: `$$test_report`, `$$runtime_features`, `$$step_defs`

1. `$$test_report` = READ `$$report_path`.
2. `$$runtime_features` = READ every target feature file under `$$runtime_feature_root`.
3. `$$step_defs` = READ every path in `$$step_def_files`.
4. ASSERT every `$$step_def_files` path is under `$$step_def_root`.
5. ASSERT `$$test_report` is runner-native evidence and contains no DSL mapping fields.

### Phase 3 — CHECK Type A hard gates
> produces: `$$type_a_findings`

1. `$$type_a_findings` = COMPUTE empty ordered list.
2. `$collection_ok` = MATCH `$$test_report` contains collected entries for every target feature and Scenario.
3. IF `$collection_ok` == false:
   3.1 MARK `$$type_a_findings` with `runner_visibility_failed`
4. `$missing_step_free` = MATCH `$$test_report` contains no missing, undefined, skipped, xfail, deselected, import, syntax, fixture, or environment error for target Scenarios.
5. IF `$missing_step_free` == false:
   5.1 MARK `$$type_a_findings` with `false_red_runner_error`
6. LOOP per `$step_def` in `$$step_defs`
   6.1 `$matcher_ok` = MATCH `$step_def` matcher against target Scenario step prose without free-form widening.
   6.2 IF `$matcher_ok` == false:
       6.2.1 MARK `$$type_a_findings` with `step_matcher_not_grounded`
       END IF
   6.3 `$body_ok` = MATCH `$step_def` body contains no empty body, `pass`, `RED-PENDING`, placeholder throw, unimplemented marker, or direct production internal import.
   6.4 IF `$body_ok` == false:
       6.4.1 MARK `$$type_a_findings` with `invalid_step_definition_body`
       END IF
   END LOOP
7. `$failure_ok` = MATCH `$$test_report` first and target failures are assertion/value-difference or expected-exception failures with feature, Scenario, step, and message locations.
8. IF `$failure_ok` == false:
   8.1 MARK `$$type_a_findings` with `not_legal_red_failure`

### Phase 4 — JUDGE hollow red
> produces: `$$type_b_findings`

1. `$$type_b_findings` = COMPUTE empty ordered list.
2. LOOP per `$scenario_report` in `$$test_report.target_scenario_reports`
   2.1 `$evidence_pack` = DERIVE failing step, failure message, feature text, and matching step definition body for `$scenario_report`.
   2.2 `$hollow_red` = JUDGE `$evidence_pack` against [`references/hollow-red-rubric.md`](references/hollow-red-rubric.md).
   2.3 IF `$hollow_red` == true:
       2.3.1 MARK `$$type_b_findings` with `hollow_red`
       END IF
   END LOOP
3. ASSERT Type B is a hard gate; hollow-red findings cannot be downgraded to advisory.

### Phase 5 — EMIT Red evaluation
> produces: `$$evaluation_report`

1. `$verdict` = DERIVE `PASS` when `$$type_a_findings` and `$$type_b_findings` are empty, else `FAIL`.
2. `$$evaluation_report` = RENDER report per [`references/evaluate-report-schema.md`](references/evaluate-report-schema.md) using `$$target_feature_files`, artifact pointers, `$$type_a_findings`, `$$type_b_findings`, and `$verdict`.
3. EMIT `$$evaluation_report` to caller.

## §3 CROSS-REFERENCES

- `/aibdd-red-execute` — Worker skill that produces the Red run evidence evaluated here.
- `/aibdd-green-execute` — may consume only Red runs whose evaluation verdict is `PASS`.
