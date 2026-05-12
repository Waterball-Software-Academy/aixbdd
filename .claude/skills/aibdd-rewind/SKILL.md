---
name: aibdd-rewind
description: Rewind an AIBDD project's filesystem state to the moment a chosen pipeline phase skill JUST FINISHED — preserves that skill's outputs and erases every downstream phase's outputs (deleting owned artifacts and reverting kickoff-shape skeletons). The phase-skill→owned-artifacts contract is a declarative rule table loaded from references/phase-rollback-rules.yml. Idempotent — safe to re-run on an already-rewound project. TRIGGER when user says 退回到 X 剛跑完 / rewind to aibdd-X / 退回上一步 / 把進度退到 X 完成那一刻. SKIP for non-AIBDD projects (no .aibdd/arguments.yml).
metadata:
  user-invocable: true
  source: project-scope
---

# aibdd-rewind

Rewind an AIBDD pipeline to a forward-pointing checkpoint — the moment a chosen phase skill just finished. The argument is the **skill name** of that phase (`aibdd-kickoff`, `aibdd-discovery`, `aibdd-plan`, …). The skill's own outputs are preserved; everything produced by downstream phases is erased.

<!-- VERB-GLOSSARY:BEGIN — program-like notation used by this skill -->

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
| R1 | [`references/role-and-contract.md`](references/role-and-contract.md) | global | Role, inputs, outputs, non-goals, completion contract. |
| R2 | [`references/phase-rollback-rules.yml`](references/phase-rollback-rules.yml) | Phase 2 + Phase 5 | Declarative phase → owned artifacts table. SSOT for what each AIBDD phase deletes / reverts. |
| R3 | [`references/safety-guardrails.md`](references/safety-guardrails.md) | Phase 4 + Phase 5 | Forbidden rollback targets and confirmation gates. |
| R4 | [`scripts/python/execute_rollback.py`](scripts/python/execute_rollback.py) | Phase 5 | Deterministic executor: applies one rule entry's deletions and skeleton reverts. |
| R5 | [`scripts/python/preview_rollback.py`](scripts/python/preview_rollback.py) | Phase 3 | Deterministic preview: lists every file/dir that would be deleted or reverted, without writing. |

## §2 SOP

### Phase 1 — BIND project + rollback target
> produces: `$$skill_dir`, `$$workspace_root`, `$$args_path`, `$$args`, `$$target_phase`, `$$rule`

1. `$$skill_dir` = COMPUTE current skill directory absolute path
2. `$$workspace_root` = COMPUTE current working directory absolute path
3. `$caller_payload` = READ caller payload if provided (skill ARGUMENTS string)
4. `$$args_path` = DERIVE absolute arguments path from `$caller_payload.arguments_path` else `${$$workspace_root}/.aibdd/arguments.yml`
5. `$args_exists` = MATCH path_exists(`$$args_path`)
6. BRANCH `$args_exists` ? GOTO #1.7 : GOTO #1.6.1
   6.1 `$missing_msg` = RENDER "`.aibdd/arguments.yml` 不存在；本 skill 只能在已執行 /aibdd-kickoff 的專案內運行"
   6.2 EMIT `$missing_msg` to user
   6.3 STOP
7. `$args_text` = READ `$$args_path`
8. `$$args` = PARSE `$args_text`, schema=`yaml`
9. `$rules_text` = READ [`references/phase-rollback-rules.yml`](references/phase-rollback-rules.yml)
10. `$rules` = PARSE `$rules_text`, schema=`yaml`
11. `$target_arg` = MATCH `$caller_payload` against pattern `aibdd[-_ ][a-z][a-z0-9-]*` else null
12. BRANCH `$target_arg` is non-null ? GOTO #1.16 : GOTO #1.13
13. `$choices` = DERIVE list of `phase_id` values from `$rules.phases`
14. [USER INTERACTION] `$user_choice` = ASK 「要 rewind 到哪一個 AIBDD phase skill 剛跑完那一刻？選擇：${$choices}」
15. `$target_arg` = DECIDE normalized `phase_id` from `$user_choice`
16. `$$target_phase` = COMPUTE `$target_arg` after normalization (lowercase, trimmed, hyphenated, leading slash stripped)
17. `$$rule` = MATCH `$rules.phases` where entry `phase_id == $$target_phase`
18. ASSERT `$$rule` is non-null
    18.1 IF assertion fails:
        18.1.1 `$unknown_msg` = RENDER "未知的 rewind target `${$$target_phase}`；目前支援：${$choices}"
        18.1.2 EMIT `$unknown_msg` to user
        18.1.3 STOP

### Phase 2 — DERIVE rollback delta
> produces: `$$delta`

1. `$preview_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/preview_rollback.py" "${$$args_path}" "${$$target_phase}"`
2. `$preview_ok` = MATCH `$preview_out.exit_code == 0`
3. BRANCH `$preview_ok` ? GOTO #2.4 : GOTO #2.3.1
   3.1 `$preview_msg` = RENDER preview script stderr summary
   3.2 EMIT `$preview_msg` to user
   3.3 STOP
4. `$$delta` = PARSE `$preview_out.stdout` as JSON, schema={chain: list, files_to_delete: list, dirs_to_delete: list, files_to_revert: list, features_to_rule_only: list, no_op_reasons: list}

### Phase 3 — RENDER preview
> produces: `$$preview_text`

1. `$$preview_text` = DRAFT human-readable preview from `$$delta`, format=
   - line "Chain to apply (prerequisites first)" with the `chain` phase_id list
   - section "Files to delete" with absolute paths
   - section "Directories to delete (recursive)" with absolute paths
   - section "Files to revert to skeleton" with absolute paths and the kickoff-shape body
   - section "Files to revert to rule-only" with absolute paths and the proposed reconstructed rule-only body
   - section "No-op (already in target state)" if any
2. EMIT `$$preview_text` to user

### Phase 4 — CONFIRM
> produces: `$$confirmation`

1. `$guardrails` = PARSE [`references/safety-guardrails.md`](references/safety-guardrails.md)
2. `$forbidden_target` = JUDGE `$$target_phase` against `$guardrails.forbidden_targets`
3. BRANCH `$forbidden_target` ? GOTO #4.3.1 : GOTO #4.4
   3.1 `$forbid_msg` = RENDER "rewind target `${$$target_phase}` 屬於禁止項；本 skill 不會破壞 kickoff 邊界"
   3.2 EMIT `$forbid_msg` to user
   3.3 STOP
4. `$nothing_to_do` = MATCH length(`$$delta.files_to_delete`) == 0 ∧ length(`$$delta.dirs_to_delete`) == 0 ∧ length(`$$delta.files_to_revert`) == 0 ∧ length(`$$delta.features_to_rule_only`) == 0
5. BRANCH `$nothing_to_do` ? GOTO #4.5.1 : GOTO #4.6
   5.1 `$noop_msg` = RENDER "目前 filesystem 已在 `${$$target_phase}` 剛跑完那一刻的狀態；nothing to do"
   5.2 EMIT `$noop_msg` to user
   5.3 STOP
6. [USER INTERACTION] `$$confirmation` = ASK 「上述 ${count(files_to_delete)+count(dirs_to_delete)+count(files_to_revert)+count(features_to_rule_only)} 項變更會發生在你的工作目錄，rewind 到 `${$$target_phase}` 剛跑完那一刻。回覆 `apply` 套用、`cancel` 取消。」
7. ASSERT `$$confirmation == apply`
    7.1 IF assertion fails:
        7.1.1 EMIT "rewind cancelled" to user
        7.1.2 STOP

### Phase 5 — EXECUTE rewind
> produces: `$$applied`

1. `$exec_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/execute_rollback.py" "${$$args_path}" "${$$target_phase}"`
2. `$exec_ok` = MATCH `$exec_out.exit_code == 0`
3. BRANCH `$exec_ok` ? GOTO #5.4 : GOTO #5.3.1
   3.1 `$exec_msg` = RENDER execute script stderr summary
   3.2 EMIT `$exec_msg` to user
   3.3 STOP
4. `$$applied` = PARSE `$exec_out.stdout` as JSON, schema={chain: list, deleted_files: list, deleted_dirs: list, reverted_files: list, rule_only_files: list}

### Phase 6 — VERIFY post-state
> produces: `$$verdict`

1. `$post_preview_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/preview_rollback.py" "${$$args_path}" "${$$target_phase}"`
2. `$post_delta` = PARSE `$post_preview_out.stdout` as JSON
3. `$$verdict` = MATCH length(`$post_delta.files_to_delete`) == 0 ∧ length(`$post_delta.dirs_to_delete`) == 0 ∧ length(`$post_delta.files_to_revert`) == 0 ∧ length(`$post_delta.features_to_rule_only`) == 0
4. ASSERT `$$verdict == true`
    4.1 IF assertion fails:
        4.1.1 `$verify_msg` = RENDER "rewind 後仍有殘留：${$post_delta}"
        4.1.2 EMIT `$verify_msg` to user
        4.1.3 STOP

### Phase 7 — REPORT

1. `$report` = DRAFT user-facing summary ← `$$target_phase`, `$$applied`, len=≤5 sentences, format=
   - "Rewound to the moment /${$$target_phase} just finished — erased outputs of ${$$rule.erases_skill} (and downstream phases via chain ${$$applied.chain})"
   - bullet list of deleted file count, deleted dir count, reverted skeleton count, rule-only feature count
   - one-line "Next: re-run ${$$rule.erases_skill} when ready" if applicable
2. EMIT `$report` to user

### Phase 8 — HANDLE failures

- IF rule lookup fails: STOP and instruct user to extend `references/phase-rollback-rules.yml`.
- IF preview script returns non-zero: STOP and surface stderr; do not attempt to execute.
- IF execute script partially succeeds and verify fails: STOP and surface the residual delta; do not retry destructive ops automatically.
- IF arguments.yml expansion produces a path outside `${$$workspace_root}`: STOP per safety-guardrails.md.

## §3 CROSS-REFERENCES

- `/aibdd-kickoff` — produces the baseline that `aibdd-rewind` will not erase.
- `/aibdd-discovery`, `/aibdd-plan`, `/aibdd-spec-by-example-analyze`, `/aibdd-red`, `/aibdd-green` — phases whose outputs `aibdd-rewind` can remove based on the rule table.
- `/programlike-skill-creator` — the authoring skill that this scaffold mirrors structurally.
