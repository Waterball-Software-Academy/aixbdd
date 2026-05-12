---
name: aibdd-reconcile
description: Reconcile one AIBDD plan package from the earliest affected planner by archiving current package artifacts, classifying trigger impact against planner relevance, cascading the reconcilable planners, and recording one session narrative. TRIGGER when user, evaluator, or worker reports an upstream artifact defect or requirement change against an existing plan package. SKIP when the request is to rewind filesystem state, regenerate tasks/implement directly, or modify non-AIBDD product code.
metadata:
  user-invocable: true
  source: project-level dogfooding
  skill-type: planner
---

# aibdd-reconcile

Reconcile one plan package by classifying the earliest impacted planner, archiving the current package snapshot, cascading downstream planners, and preserving one append-only session narrative.

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

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `references/role-and-contract.md` | global | Define reconcile role, non-goals, completion contract, and archive semantics. |
| R2 | `references/path-and-session-contract.md` | global | Define target plan-package validation, active-session location, record lifecycle, and session JSON schema. |
| R3 | `references/planner-handoff-contract.md` | global | Define the payload passed from reconcile into discovery, plan, and spec-by-example planners. |
| R4 | `assets/templates/reconcile-record.template.md` | Phase 4 + Phase 6 | Provide the markdown shape for `RECONCILE_RECORD.md`. |
| R5 | `scripts/python/resolve_reconcile_context.py` | Phase 1 | Resolve the target package, archive directory, and reconcile file paths from `.aibdd/arguments.yml`. |
| R6 | `scripts/python/derive_cascade_chain.py` | Phase 2 | Derive the suffix cascade chain from the classified earliest planner. |
| R7 | `scripts/python/preview_archive.py` | Phase 3 | Preview which non-archive package entries would move into the new archive timestamp directory. |
| R8 | `scripts/python/execute_archive.py` | Phase 4 | Move every non-archive package entry into the session archive snapshot. |
| R9 | `scripts/python/manage_reconcile_session.py` | Phase 2 + Phase 5 + Phase 6 | Create, merge, advance, and finish the active reconcile session state. |
| R10 | `scripts/python/render_reconcile_record.py` | Phase 4 + Phase 6 | Render the current session JSON into root-level `RECONCILE_RECORD.md`. |

## §2 SOP

### Phase 1 — BIND target package and active session
> produces: `$$skill_dir`, `$$workspace_root`, `$$args_path`, `$$context`, `$$trigger_desc`, `$$session_mode`

1. `$$skill_dir` = COMPUTE current skill directory path
2. `$$workspace_root` = COMPUTE current workspace directory path
3. `$caller_payload` = READ caller payload if provided
4. `$$args_path` = DERIVE absolute arguments path from `$caller_payload.arguments_path` else `${$$workspace_root}/.aibdd/arguments.yml`
5. `$plan_package_arg` = DERIVE target plan package path from `$caller_payload.plan_package_path` else first positional argument from skill ARGUMENTS
6. `$$trigger_desc` = DERIVE trigger description from `$caller_payload.trigger_description` else quoted remainder of skill ARGUMENTS
7. `$$context` = TRIGGER `python3 "${$$skill_dir}/scripts/python/resolve_reconcile_context.py" "${$$args_path}" "${$plan_package_arg}"`
8. `$context_ok` = MATCH `$$context.exit_code == 0`
9. BRANCH `$context_ok` ? GOTO #1.10 : GOTO #1.9.1
   9.1 `$bind_msg` = RENDER resolve-context stderr/stdout summary
   9.2 EMIT `$bind_msg` to user
   9.3 STOP
10. ASSERT `$$trigger_desc` is non-empty
    10.1 IF assertion fails:
        10.1.1 EMIT "trigger description 不可為空；請提供本次 reconcile 的缺陷或需求描述" to user
        10.1.2 STOP
11. `$active_exists` = MATCH path_exists(`$$context.stdout.active_session_path`)
12. BRANCH `$active_exists`
    true  → `$$session_mode` = COMPUTE `merge_existing`
    false → `$$session_mode` = COMPUTE `start_new`

### Phase 2 — CLASSIFY earliest planner and materialize session
> produces: `$$merged_trigger_text`, `$$earliest_planner`, `$$cascade_chain`, `$$session_state`

1. `$discovery_relevance` = READ `.claude/skills/aibdd-discovery/references/relevance.md`
2. `$plan_relevance` = READ `.claude/skills/aibdd-plan/references/relevance.md`
3. `$sbe_relevance` = READ `.claude/skills/aibdd-spec-by-example-analyze/references/relevance.md`
4. BRANCH `$$session_mode`
   start_new      → `$$merged_trigger_text` = COMPUTE `$$trigger_desc`
   merge_existing → `$$merged_trigger_text` = DRAFT merged trigger text from active session trigger history + `$$trigger_desc`
5. `$$earliest_planner` = CLASSIFY `$$merged_trigger_text` against `$discovery_relevance`, `$plan_relevance`, `$sbe_relevance`, enum=`aibdd-discovery | aibdd-plan | aibdd-spec-by-example-analyze`
6. BRANCH `$$earliest_planner`
   `aibdd-discovery`               → GOTO #2.8
   `aibdd-plan`                    → GOTO #2.8
   `aibdd-spec-by-example-analyze` → GOTO #2.8
   other                           → GOTO #2.7.1
   7.1 `$$earliest_planner` = COMPUTE `aibdd-discovery`
7.2 EMIT "reconcile classification 模糊；依保守規則改由最上游 /aibdd-discovery 起跑" to user
8. `$$cascade_chain` = TRIGGER `python3 "${$$skill_dir}/scripts/python/derive_cascade_chain.py" "${$$earliest_planner}"`
9. `$chain_ok` = MATCH `$$cascade_chain.exit_code == 0`
10. BRANCH `$chain_ok` ? GOTO #2.11 : GOTO #2.10.1
    10.1 `$chain_msg` = RENDER cascade-chain stderr/stdout summary
    10.2 EMIT `$chain_msg` to user
    10.3 STOP
11. BRANCH `$$session_mode`
    start_new      → `$$session_state` = TRIGGER `python3 "${$$skill_dir}/scripts/python/manage_reconcile_session.py" start "${$$context.stdout.active_session_path}" "${$$context.stdout.record_path}" "${$$context.stdout.target_plan_package}" "${$$merged_trigger_text}" "${$$earliest_planner}" "${$$cascade_chain.stdout_csv}"`
    merge_existing → `$$session_state` = TRIGGER `python3 "${$$skill_dir}/scripts/python/manage_reconcile_session.py" merge "${$$context.stdout.active_session_path}" "${$$trigger_desc}" "${$$earliest_planner}" "${$$cascade_chain.stdout_csv}"`
12. ASSERT `$$session_state.exit_code == 0`
    12.1 IF assertion fails:
        12.1.1 `$session_msg` = RENDER session-manager stderr/stdout summary
        12.1.2 EMIT `$session_msg` to user
        12.1.3 STOP

### Phase 3 — PREVIEW archive or merged replay
> produces: `$$archive_preview`

1. BRANCH `$$session_mode`
   start_new      → `$$archive_preview` = TRIGGER `python3 "${$$skill_dir}/scripts/python/preview_archive.py" "${$$args_path}" "${$$context.stdout.target_plan_package}" "${$$session_state.stdout_session_id}"`
   merge_existing → `$$archive_preview` = COMPUTE `{"ok": true, "mode": "merge_existing", "entries_to_move": [], "archived_to": $$session_state.stdout_archive_path}`
2. ASSERT `$$archive_preview.ok == true`
   2.1 IF assertion fails:
       2.1.1 EMIT "archive preview 失敗；停止本次 reconcile" to user
       2.1.2 STOP

### Phase 4 — ARCHIVE package snapshot and refresh session record
> produces: `$$archive_result`

1. BRANCH `$$session_mode`
   start_new      → `$$archive_result` = TRIGGER `python3 "${$$skill_dir}/scripts/python/execute_archive.py" "${$$args_path}" "${$$context.stdout.target_plan_package}" "${$$session_state.stdout_session_id}"`
   merge_existing → `$$archive_result` = COMPUTE `{"ok": true, "mode": "merge_existing", "moved_entries": [], "archived_to": $$session_state.stdout_archive_path}`
2. ASSERT `$$archive_result.ok == true`
   2.1 IF assertion fails:
       2.1.1 EMIT "archive 執行失敗；停止本次 reconcile" to user
       2.1.2 STOP
3. `$record_write` = TRIGGER `python3 "${$$skill_dir}/scripts/python/render_reconcile_record.py" "${$$session_state.stdout_session_path}" "${$$context.stdout.record_path}"`
4. ASSERT `$record_write.exit_code == 0`
   4.1 IF assertion fails:
       4.1.1 EMIT "RECONCILE_RECORD.md 寫入失敗；停止本次 reconcile" to user
       4.1.2 STOP

### Phase 5 — CASCADE reconcilable planners
> produces: `$$cascade_result`

1. `$replay_from` = PARSE `$$session_state.stdout_replay_from`
2. BRANCH `$replay_from`
   `aibdd-discovery` → GOTO #5.3
   `aibdd-plan` → GOTO #5.8
   `aibdd-spec-by-example-analyze` → GOTO #5.11
   other → GOTO #5.2.1
   2.1 EMIT "session replay pointer 非法；停止本次 reconcile" to user
   2.2 STOP
3. `$discovery_report` = DELEGATE `/aibdd-discovery` with payload per [`references/planner-handoff-contract.md`](references/planner-handoff-contract.md) §Discovery Payload
4. ASSERT `$discovery_report.status == completed`
   4.1 IF assertion fails:
       4.1.1 EMIT "reconcile 停在 /aibdd-discovery；下游未執行" to user
       4.1.2 STOP
5. `$advance_plan` = TRIGGER `python3 "${$$skill_dir}/scripts/python/manage_reconcile_session.py" advance "${$$context.stdout.active_session_path}" "aibdd-plan"`
6. ASSERT `$advance_plan.exit_code == 0`
7. GOTO #5.8
8. `$plan_report` = DELEGATE `/aibdd-plan` with payload per [`references/planner-handoff-contract.md`](references/planner-handoff-contract.md) §Plan Payload
9. ASSERT `$plan_report.status == completed`
   9.1 IF assertion fails:
       9.1.1 EMIT "reconcile 停在 /aibdd-plan；/aibdd-spec-by-example-analyze 未執行" to user
       9.1.2 STOP
10. `$advance_sbe` = TRIGGER `python3 "${$$skill_dir}/scripts/python/manage_reconcile_session.py" advance "${$$context.stdout.active_session_path}" "aibdd-spec-by-example-analyze"`
11. `$sbe_report` = DELEGATE `/aibdd-spec-by-example-analyze` with payload per [`references/planner-handoff-contract.md`](references/planner-handoff-contract.md) §Spec-by-Example Payload
12. ASSERT `$sbe_report.status == completed`
    12.1 IF assertion fails:
        12.1.1 EMIT "reconcile 停在 /aibdd-spec-by-example-analyze" to user
        12.1.2 STOP
13. `$$cascade_result` = COMPUTE `completed`

### Phase 6 — STAMP final state and REPORT next steps

1. `$finish_state` = TRIGGER `python3 "${$$skill_dir}/scripts/python/manage_reconcile_session.py" finish "${$$context.stdout.active_session_path}" "completed"`
2. ASSERT `$finish_state.exit_code == 0`
   2.1 IF assertion fails:
       2.1.1 EMIT "reconcile session 收尾失敗；請檢查 active session 檔" to user
       2.1.2 STOP
3. `$final_record` = TRIGGER `python3 "${$$skill_dir}/scripts/python/render_reconcile_record.py" "${$finish_state.stdout_final_session_path}" "${$$context.stdout.record_path}"`
4. ASSERT `$final_record.exit_code == 0`
   4.1 IF assertion fails:
       4.1.1 EMIT "最終 RECONCILE_RECORD.md 寫入失敗" to user
       4.1.2 STOP
5. `$summary` = DRAFT user-facing summary from `$$context.stdout.target_plan_package`, `$$earliest_planner`, `$$session_state.stdout_archive_path`, `$$cascade_chain.stdout_csv`, and `$$trigger_desc`
6. EMIT `$summary` to user
7. EMIT "提醒：`/aibdd-tasks`、`/aibdd-implement` 已過期；請重新 derive tasks 並重跑 implement。" to user
