---
name: aibdd-refactor-execute
description: Refactor product code under a Green target feature-file set by loading constitutions and runtime refs, applying one minimal move at a time, rerunning acceptance tests, reverting red moves, and emitting a Refactor handoff. TRIGGER when Refactor execute is requested after aibdd-green-execute. SKIP when the target set is not green or the request adds behavior.
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-refactor-execute

Refactor within the green target feature-file safety boundary.

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
  - path: references/execute-config-contract.md
    purpose: Defines target, arguments, constitution, runtime reference, and drift contracts
  - path: references/handoff-schemas.md
    purpose: Defines Green input and Refactor output schemas
  - path: references/refactor-move-policy.md
    purpose: Defines protected behavior, candidate priority, move size, interaction gates, and scope shrink
```

## §2 SOP

### Phase 1 — RECEIVE green handoff
> produces: `$$payload`, `$$target_feature_files`, `$$green_handoff`, `$$arguments_path`

1. `$$payload` = READ caller payload with `target_feature_files`, `green_handoff`, optional `arguments_path`, optional `scope`.
2. `$$target_feature_files` = PARSE `$$payload.target_feature_files` as non-empty path list.
3. `$$green_handoff` = PARSE `$$payload.green_handoff` using [`references/handoff-schemas.md`](references/handoff-schemas.md).
4. ASSERT `$$green_handoff.status == completed` and `$$green_handoff.stop_reason == none`.
5. ASSERT `$$green_handoff.target_feature_files` equals `$$target_feature_files`.
6. `$$arguments_path` = DERIVE caller override or `${AIBDD_CONFIG_DIR}/arguments.yml` per [`references/execute-config-contract.md`](references/execute-config-contract.md).
7. ASSERT `$$arguments_path` exists; on failure STOP with `missing_arguments_path`.

### Phase 2 — LOAD constitutions and runtime
> produces: `$$config`, `$$dev_constitution`, `$$bdd_constitution`, `$$runtime_refs`, `$$runtime_snapshot`

1. `$$config` = PARSE `$$arguments_path` as project config.
2. `$$dev_constitution` = READ `DEV_CONSTITUTION_PATH`.
3. `$$bdd_constitution` = READ `BDD_CONSTITUTION_PATH`.
4. `$$runtime_refs` = READ project-owned BDD stack runtime refs from `$$config`.
5. ASSERT dev constitution, BDD constitution, runner command, runtime feature glob, step glob, fixture contract, archive behavior, and readable Red Pre-Red hook (`RED_PREHANDLING_HOOK_REF`) exist.
6. `$$runtime_snapshot` = DERIVE current runtime ref path and content fingerprints including `RED_PREHANDLING_HOOK_REF`.
7. ASSERT `$$runtime_snapshot` matches `$$green_handoff.runtime_refs_snapshot` for this target set; on failure STOP with `runtime_drift`.

### Phase 3 — ASSERT green baseline
> produces: `$$baseline_report`

1. `$$baseline_report` = TRIGGER acceptance runner for `$$target_feature_files`.
2. ASSERT `$$baseline_report.outcome == passed`; on failure STOP with `not_green_baseline`.
3. ASSERT target runner command covers all `$$target_feature_files`.

### Phase 4 — SELECT candidate moves
> produces: `$$candidate_moves`

1. `$code_region` = DERIVE protected product-code region from `$$green_handoff.product_files_modified`, `$$target_feature_files`, and constitutions.
2. `$$candidate_moves` = CLASSIFY improvement candidates using priority in [`references/refactor-move-policy.md`](references/refactor-move-policy.md).
3. FILTER `$$candidate_moves` to remove behavior changes, new features, contract changes, and test-surface changes.
4. FILTER `$$candidate_moves` to remove DRY extraction with fewer than three repetitions.
5. MARK candidates requiring user approval: cross-file move, helper extraction, test or step-def refactor, fixture contract change, or out-of-scope cleanup.

### Phase 5 — LOOP one move at a time
> produces: `$$applied_moves`, `$$reverted_moves`, `$$scope_history`, `$$final_report`

1. `$$applied_moves` = COMPUTE empty ordered list.
2. `$$reverted_moves` = COMPUTE empty ordered list.
3. `$$scope_history` = COMPUTE empty ordered list.
4. LOOP per `$move` in `$$candidate_moves`
   4.1 `$needs_approval` = MATCH `$move` against interaction gates in [`references/refactor-move-policy.md`](references/refactor-move-policy.md).
   4.2 IF `$needs_approval`:
       4.2.1 [USER INTERACTION] `$approval` = ASK approve this gated refactor move.
       4.2.2 BRANCH `$approval` ? CONTINUE : MARK `$move` skipped
       END IF
   4.3 `$patch` = APPLY code change for exactly one structural move.
   4.4 ASSERT `$patch` does not change API contract, DB schema, IPC contract, runtime feature, step-def matcher, fixture contract, runtime ref, or testability anchor signature.
   4.5 `$$final_report` = TRIGGER acceptance runner for `$$target_feature_files`.
   4.6 BRANCH `$$final_report.outcome`
       `passed` → MARK `$move` in `$$applied_moves`
       `failed` → DELETE `$patch`; MARK `$move` in `$$reverted_moves`
   4.7 `$risky_count` = COUNT consecutive reverted moves.
   4.8 IF `$risky_count >= 3`:
       4.8.1 `$new_scope` = DERIVE narrower scope from target set to one feature file or smallest product-code region.
       4.8.2 MARK `$new_scope` in `$$scope_history`.
       4.8.3 `$candidate_moves` = FILTER remaining candidates by `$new_scope`.
       END IF
   END LOOP
5. `$$final_report` = TRIGGER acceptance runner for `$$target_feature_files`.
6. ASSERT `$$final_report.outcome == passed`; on failure STOP with `refactor_safety_failure`.

### Phase 6 — EMIT refactor handoff

1. `$files_modified` = DERIVE final changed files from accepted moves only.
2. `$refactor_handoff` = RENDER schema from [`references/handoff-schemas.md`](references/handoff-schemas.md), `$$green_handoff`, `$$final_report`, `$$applied_moves`, `$$reverted_moves`, `$files_modified`, `$$scope_history`, and `$$runtime_snapshot`.
3. EMIT `$refactor_handoff` to caller.

## §3 CROSS-REFERENCES

- `/aibdd-green-execute` — produces the Green handoff consumed here.
- `/aibdd-red-execute` — starts any new behavior that Refactor must not add.
- `/speckit-constitution` — owns development constitution changes outside Refactor scope.
