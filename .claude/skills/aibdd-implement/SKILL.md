---
name: aibdd-implement
description: Execute an existing `tasks.md` through TodoWrite-driven task management. Every markdown checkbox becomes exactly one todo item, and both the todo list and `tasks.md` must stay synchronized while execution progresses.
metadata:
  user-invocable: true
  source: project-level
---

# aibdd-implement

Execute an existing AIBDD `tasks.md` by turning every markdown checkbox into one live todo item and keeping `TodoWrite` state and `tasks.md` progress synchronized throughout execution.

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

無。此 skill 的 runtime contract、todo 顆粒度規則、parent/child 完成規則、以及 `tasks.md` 同步規則全部 inline 於 §2 SOP；不得依賴同目錄其他檔案。

## §2 SOP

### Phase 1 — BIND target tasks artifact
> produces: `$$tasks_md_path`, `$$tasks_md`, `$$check_nodes`

1. `$$tasks_md_path` = DERIVE target `tasks.md` path from user request or attached file reference.
2. ASSERT `$$tasks_md_path` exists and basename(`$$tasks_md_path`) == `tasks.md`.
   2.1 IF assertion fails:
       2.1.1 EMIT "請直接提供要執行的 `tasks.md` 路徑。" to user
       2.1.2 STOP
3. `$$tasks_md` = READ `$$tasks_md_path`
4. `$$check_nodes` = PARSE every markdown checkbox line from `$$tasks_md`, preserving source order, indentation depth, heading context, and parent-child relation.
5. ASSERT length(`$$check_nodes`) > 0
   5.1 IF assertion fails:
       5.1.1 EMIT "目標 `tasks.md` 沒有任何 checkbox，無法用 `/aibdd-implement` 執行。" to user
       5.1.2 STOP
6. ASSERT every parsed checkbox will map to exactly one todo item; no merge, no omission, no coarse bundling.

### Phase 2 — INITIALIZE live todo list
> produces: `$$todo_items`, `$$leaf_nodes`, `$$parent_nodes`

1. `$$todo_items` = DERIVE one TodoWrite item per `$$check_nodes` entry.
2. ASSERT cardinality(`$$todo_items`) == cardinality(`$$check_nodes`)
3. `$$leaf_nodes` = DERIVE checklist entries with no child checklist entries.
4. `$$parent_nodes` = DERIVE checklist entries with one or more descendant checklist entries.
5. MARK TodoWrite ← `$$todo_items` with rules:
   5.1 every checkbox line in `tasks.md` becomes one todo item;
   5.2 at most one todo item may be `in_progress`;
   5.3 the first runnable leaf node becomes `in_progress`;
   5.4 every other unchecked node starts as `pending`.
6. ASSERT parent checklist items are still real todo items, but they may only be marked `completed` after all descendant checkbox items are completed.

### Phase 3 — EXECUTE one checkbox at a time
> produces: `$$completed_nodes`

1. LOOP per `$node` in `$$leaf_nodes` using file order, budget=all leaves, exit=all leaves terminal
   1.1 MARK TodoWrite update `$node.todo_id` → `in_progress`
   1.2 `$work_result` = TRIGGER the minimal tool call(s) needed to satisfy exactly `$node` and nothing larger
   1.3 `$done` = JUDGE `$work_result` truly satisfies `$node.checkbox_text`
   1.4 BRANCH `$done` ? GOTO #3.1.5 : GOTO #3.1.4.1
       4.1 `$blocker` = DRAFT concise blocker summary for `$node`
       4.2 MARK TodoWrite update `$node.todo_id` → `pending`
       4.3 EMIT `$blocker` to user
       4.4 STOP
   1.5 EDIT `$$tasks_md_path` ← mark `$node` from `- [ ]` to `- [x]` immediately after completion
   1.6 MARK TodoWrite update `$node.todo_id` → `completed`
   1.7 `$$completed_nodes` = DERIVE `$$completed_nodes` ⊕ `$node`
   1.8 LOOP per `$parent` in ancestors(`$node`) from nearest to farthest
       1.8.1 `$children_done` = JUDGE every descendant checkbox of `$parent` is already checked in `$$tasks_md_path`
       1.8.2 IF `$children_done` == true:
           1.8.2.1 EDIT `$$tasks_md_path` ← mark `$parent` from `- [ ]` to `- [x]`
           1.8.2.2 MARK TodoWrite update `$parent.todo_id` → `completed`
       END LOOP
   1.9 `$next_leaf` = DERIVE next unchecked leaf node in file order
   1.10 IF `$next_leaf` exists:
       1.10.1 MARK TodoWrite update `$next_leaf.todo_id` → `in_progress`
   END LOOP

### Phase 4 — ENFORCE synchronization invariants during execution
> produces: (none)

1. ASSERT every completed todo item has a matching checked checkbox `[x]` in `$$tasks_md_path`.
2. ASSERT every checked checkbox `[x]` in `$$tasks_md_path` has a matching todo item with status `completed`.
3. ASSERT no parent checkbox may be marked complete while any descendant checkbox remains unchecked.
4. ASSERT no tool work may silently advance without syncing both TodoWrite and `tasks.md`.
5. IF any drift is detected:
   5.1 EDIT or MARK the lagging side immediately
   5.2 RECHECK all affected ancestors before continuing

### Phase 5 — REPORT final progress
> produces: (none)

1. `$remaining` = DERIVE unchecked checkbox count from latest `$$tasks_md_path`
2. BRANCH `$remaining` == 0 ? GOTO #5.3 : GOTO #5.2
   2.1 `$partial_report` = DRAFT partial progress summary with counts for completed / remaining / blocked items
   2.2 EMIT `$partial_report` to user
   2.3 RETURN
3. `$final_report` = DRAFT concise completion summary with total completed checkbox count and any notable artifacts produced during execution
4. EMIT `$final_report` to user
