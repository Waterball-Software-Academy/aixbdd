---
name: aibdd-refactor-evaluate
description: Evaluate a completed AIBDD Refactor Worker run by checking strict dev constitution conformance and final full acceptance suite all pass.
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-refactor-evaluate

Evaluate whether a completed Refactor Worker run remained constitutional and behavior-safe.

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
    purpose: Defines Refactor evaluate payload and artifact pointer requirements
  - path: references/evaluate-report-schema.md
    purpose: Defines Refactor evaluate PASS FAIL Veto report fields
  - path: references/dev-constitution-check.md
    purpose: Defines strict dev constitution conformance evidence and Veto standard
```

## §2 SOP

### Phase 1 — RECEIVE Refactor evidence
> produces: `$$payload`, `$$report_path`, `$$dev_constitution_path`, `$$code_scope`

1. `$$payload` = READ caller payload with `refactor_handoff` or explicit artifact pointers.
2. `$$report_path` = PARSE final full acceptance suite test report path per [`references/evaluate-input-contract.md`](references/evaluate-input-contract.md).
3. `$$dev_constitution_path` = PARSE resolved `${DEV_CONSTITUTION_PATH}` from payload or project config pointer.
4. `$$code_scope` = PARSE product codebase root and changed-file scope used for constitution checking.
5. ASSERT `$$report_path` exists; on failure STOP with `missing_refactor_full_suite_report`.
6. ASSERT `$$dev_constitution_path` exists; on failure STOP with `missing_dev_constitution_path`.
7. ASSERT `$$code_scope` is present; on failure STOP with `missing_constitution_check_scope`.

### Phase 2 — LOAD evidence
> produces: `$$test_report`, `$$dev_constitution`, `$$scoped_code`

1. `$$test_report` = READ `$$report_path`.
2. `$$dev_constitution` = READ `$$dev_constitution_path`.
3. `$$scoped_code` = READ product files in `$$code_scope`.
4. ASSERT `$$test_report` identifies the run as the full acceptance suite, not a target-only subset.
5. ASSERT `$$test_report` is runner-native evidence and contains no DSL mapping fields.

### Phase 3 — CHECK dev constitution strict
> produces: `$$constitution_findings`

1. `$$constitution_findings` = COMPUTE empty ordered list.
2. `$rules` = PARSE mandatory and prohibitive clauses from `$$dev_constitution` per [`references/dev-constitution-check.md`](references/dev-constitution-check.md).
3. LOOP per `$rule` in `$rules`
   3.1 `$violation` = JUDGE `$$scoped_code` against `$rule`.
   3.2 IF `$violation` == true:
       3.2.1 MARK `$$constitution_findings` with `$rule`
       END IF
   END LOOP
4. ASSERT constitution judgment is strict; no violated MUST or MUST NOT may be downgraded to advisory.

### Phase 4 — CHECK full suite all pass
> produces: `$$test_findings`

1. `$$test_findings` = COMPUTE empty ordered list.
2. `$failures_zero` = MATCH `$$test_report` has `0 failed`.
3. IF `$failures_zero` == false:
   3.1 MARK `$$test_findings` with `full_suite_failed`
4. `$errors_zero` = MATCH `$$test_report` has `0 errors`.
5. IF `$errors_zero` == false:
   5.1 MARK `$$test_findings` with `full_suite_error`
6. `$skip_safe` = MATCH `$$test_report` contains no scenario hidden by improper skip, xfail, deselect, or collection omission.
7. IF `$skip_safe` == false:
   7.1 MARK `$$test_findings` with `not_assertion_passed`

### Phase 5 — EMIT Refactor evaluation
> produces: `$$evaluation_report`

1. `$verdict` = DERIVE `PASS` when `$$constitution_findings` and `$$test_findings` are empty, else `FAIL`.
2. `$$evaluation_report` = RENDER report per [`references/evaluate-report-schema.md`](references/evaluate-report-schema.md) using `$$report_path`, `$$dev_constitution_path`, `$$code_scope`, `$$constitution_findings`, `$$test_findings`, and `$verdict`.
3. EMIT `$$evaluation_report` to caller.

## §3 CROSS-REFERENCES

- `/aibdd-refactor-execute` — Worker skill that produces the Refactor run evidence evaluated here.
- `/speckit-constitution` — owns changes to `${DEV_CONSTITUTION_PATH}` outside the evaluator.
