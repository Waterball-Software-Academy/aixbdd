---
name: skill-test-execute
description: Execute one fixture-based skill test scenario by validating the target skill's `.tests/TEST.md`, running the skill under test in a copy-only sandbox seeded from `before/`, comparing the sandbox result with `after/`, and emitting a compact evaluator report in chat. Use when the user wants to test a specific skill scenario without mutating fixtures or writing runner reports.
metadata:
  user-invocable: true
  source: global
  skill-type: test-runner
---

# skill-test-execute

Execute one scenario for a target skill as a chat-only evaluator runner: validate the target `.tests/TEST.md`, isolate the tested skill from the oracle, run it in a sandbox, compare files, and judge whether the diff is a real failure.

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

## Section 1 - References

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `<target-skill>/SKILL.md` | Phase 1 + Phase 5 + Phase 7 | Tested skill entrypoint, invocation behavior, allowed stable instructions, and expected artifact ownership. |
| R2 | `<target-skill>/.tests/TEST.md` | Phase 2 | Runner contract that defines the fixture protocol and isolation rules. |
| R3 | `<target-skill>/.tests/<scenario>/before/` | Phase 3 + Phase 4 | Only filesystem seed copied into the execution sandbox. |
| R4 | `<target-skill>/.tests/<scenario>/after/` | Phase 6 + Phase 7 | Runner-only oracle read after the tested-skill subagent completes. |
| R5 | `<target-skill>/references/` and `<target-skill>/assets/` | Phase 5 + Phase 7 | Stable skill-local knowledge the tested skill may need to execute, excluding tests and reports. |
| R6 | `<sandbox-root>/<scenario>/` | Phase 4 + Phase 5 + Phase 6 | Isolated cwd where the tested-skill subagent runs. |

## Section 2 - Output Contract

This skill emits exactly one compact Markdown evaluator report in chat.

Required report sections:

- `Verdict`: one of `PASS`, `FAIL`, or `BLOCKED`.
- `Failures`: concise list of failing issue IDs and affected paths.
- `Diff Evidence`: missing files, extra files, and content diff excerpts.
- `Semantic Judgment`: whether each diff is behaviorally meaningful for the target skill contract.
- `Fix Instructions`: direct implementation guidance for the next agent.

This skill MUST NOT write:

- `.tests/<scenario>/issues/`;
- `.tests/reports/`;
- `.tests/<scenario>/test-report.md`;
- scenario metadata files;
- fixture changes under `before/` or `after/`;
- patches to the target skill under test.

If a target `TEST.md` merely allows runner-owned issue output, this skill still uses the chat-only report sink. If a target `TEST.md` explicitly requires persistent report files and forbids chat-only reporting, this skill stops with `UNSUPPORTED_TEST_CONTRACT`.

## Section 3 - SOP

### Phase 1 - Bind target skill and scenario
> produces: `$$target_skill_dir`, `$$target_skill_md`, `$$tests_root`, `$$test_md`, `$$scenario_name`, `$$scenario_dir`, `$$before_dir`, `$$after_dir`

1. [USER INTERACTION] `$$target_skill_dir` = ASK target skill directory or skill invocation name.
2. `$$target_skill_dir` = COMPUTE absolute skill directory from user input.
3. `$$target_skill_md` = COMPUTE `${$$target_skill_dir}/SKILL.md`.
4. ASSERT path_exists(`$$target_skill_md`).
   4.1 IF assertion fails:
       4.1.1 EMIT "target skill must have SKILL.md".
       4.1.2 STOP.
5. [USER INTERACTION] `$$scenario_name` = ASK exact scenario directory name.
6. ASSERT `$$scenario_name` is non-empty and names exactly one scenario.
   6.1 IF assertion fails:
       6.1.1 EMIT "skill-test-execute runs exactly one named scenario".
       6.1.2 STOP.
7. `$$tests_root` = COMPUTE `${$$target_skill_dir}/.tests`.
8. `$$test_md` = COMPUTE `${$$tests_root}/TEST.md`.
9. `$$scenario_dir` = COMPUTE `${$$tests_root}/${$$scenario_name}`.
10. `$$before_dir` = COMPUTE `${$$scenario_dir}/before`.
11. `$$after_dir` = COMPUTE `${$$scenario_dir}/after`.

### Phase 2 - Validate runner contract
> produces: `$$test_contract`, `$$contract_status`

1. ASSERT path_exists(`$$test_md`).
   1.1 IF assertion fails:
       1.1.1 EMIT issue `MISSING_TEST_CONTRACT`.
       1.1.2 STOP.
2. `$$test_contract` = READ `$$test_md`.
3. `$mentions_before` = MATCH `$$test_contract` contains `before/`.
4. `$mentions_after` = MATCH `$$test_contract` contains `after/`.
5. `$mentions_oracle_isolation` = MATCH `$$test_contract` contains oracle isolation rule or equivalent "after must not be visible" rule.
6. `$mentions_filesystem_compare` = MATCH `$$test_contract` contains filesystem comparison rule or equivalent actual-vs-expected rule.
7. ASSERT `$mentions_before` AND `$mentions_after` AND `$mentions_oracle_isolation` AND `$mentions_filesystem_compare`.
   7.1 IF assertion fails:
       7.1.1 EMIT issue `INVALID_TEST_CONTRACT` with missing contract elements.
       7.1.2 STOP.
8. `$requires_persistent_report` = JUDGE whether `$$test_contract` explicitly forbids chat-only reporting or requires persistent report files as the only valid output sink.
9. IF `$requires_persistent_report`:
   9.1 EMIT issue `UNSUPPORTED_TEST_CONTRACT`.
   9.2 STOP.
10. `$$contract_status` = MARK "valid fixture runner contract with chat-only compatible reporting".

### Phase 3 - Validate scenario fixture
> produces: `$$fixture_status`

1. ASSERT path_exists(`$$scenario_dir`).
   1.1 IF assertion fails:
       1.1.1 EMIT issue `MISSING_SCENARIO`.
       1.1.2 STOP.
2. ASSERT path_exists(`$$before_dir`).
   2.1 IF assertion fails:
       2.1.1 EMIT issue `MISSING_BEFORE`.
       2.1.2 STOP.
3. ASSERT path_exists(`$$after_dir`).
   3.1 IF assertion fails:
       3.1.1 EMIT issue `MISSING_ORACLE`.
       3.1.2 STOP.
4. `$before_index` = READ file tree under `$$before_dir`.
5. `$before_has_oracle` = MATCH `$before_index` contains `.tests`, `after`, `TEST.md`, `issues`, `report`, `.cursor/plans`, or oracle wording.
6. ASSERT `$before_has_oracle == false`.
   6.1 IF assertion fails:
       6.1.1 EMIT issue `ORACLE_IN_BEFORE`.
       6.1.2 STOP.
7. `$$fixture_status` = MARK "valid before/after scenario fixture".

### Phase 4 - Create copy-only sandbox
> produces: `$$sandbox_root`, `$$scenario_sandbox`

1. `$$sandbox_root` = CREATE fresh temporary sandbox root outside `$$tests_root`, outside `$$target_skill_dir`, and outside `.cursor/plans`.
2. `$$scenario_sandbox` = CREATE `${$$sandbox_root}/${$$scenario_name}`.
3. WRITE `$$scenario_sandbox` <- exact contents of `$$before_dir`.
4. ASSERT `$$scenario_sandbox` contains no `.tests`, `after`, `TEST.md`, issue report, previous run report, `.cursor/plans`, or answer oracle.
   4.1 IF assertion fails:
       4.1.1 DELETE `$$scenario_sandbox`.
       4.1.2 EMIT issue `SANDBOX_ORACLE_CONTAMINATION`.
       4.1.3 STOP.

### Phase 5 - Trigger tested-skill subagent
> produces: `$$subagent_prompt`, `$$run_report`

1. `$target_skill_text` = READ `$$target_skill_md`.
2. `$allowed_stable_skill_paths` = COMPUTE stable target skill files the subagent may read:
   - `$$target_skill_md`;
   - `${$$target_skill_dir}/references/`;
   - `${$$target_skill_dir}/assets/`;
   - sibling skill files explicitly referenced by `$$target_skill_md`.
3. `$forbidden_paths` = COMPUTE:
   - `$$tests_root`;
   - `$$test_md`;
   - `$$scenario_dir`;
   - `$$after_dir`;
   - any `.tests` directory;
   - `.cursor/plans`;
   - previous runner reports or issue folders.
4. `$$subagent_prompt` = RENDER tested-skill execution prompt:
   - cwd is `$$scenario_sandbox`;
   - execute `$$target_skill_dir` exactly as the user-facing skill under test;
   - use only the state and input artifacts present in cwd plus allowed stable skill files;
   - do not read forbidden paths;
   - do not ask for or infer expected `after/` contents;
   - stop and declare blocker if the scenario lacks enough input to run.
5. TRIGGER subagent with cwd `$$scenario_sandbox` and `$$subagent_prompt`.
6. WAIT for subagent completion.
7. `$$run_report` = MARK subagent exit state, declared blockers, touched paths if observable, and transcript summary.
8. IF `$$run_report` contains blocker:
   8.1 MARK scenario issue `SKILL_BLOCKED`.
   8.2 GOTO #8.1.

### Phase 6 - Compare actual against oracle
> produces: `$$diff_report`

1. `$expected_tree` = READ file tree under `$$after_dir`.
2. `$actual_tree` = READ file tree under `$$scenario_sandbox`.
3. `$actual_tree` = COMPUTE `$actual_tree` excluding runner-only temp metadata, shell transcripts, logs created by the runner itself, and any sandbox bookkeeping outside the copied cwd.
4. `$missing_files` = COMPUTE files in `$expected_tree` not in `$actual_tree`.
5. `$extra_files` = COMPUTE files in `$actual_tree` not in `$expected_tree`.
6. `$content_diffs` = COMPUTE normalized textual diffs for files present in both trees.
7. `$$diff_report` = MARK:
   - missing_files = `$missing_files`;
   - extra_files = `$extra_files`;
   - content_diffs = `$content_diffs`.

### Phase 7 - Judge semantic impact
> produces: `$$semantic_report`, `$$verdict`

1. IF `$$diff_report` has no missing files, no extra files, and no content diffs:
   1.1 `$$semantic_report` = MARK "no diff".
   1.2 `$$verdict` = MARK `PASS`.
   1.3 GOTO #8.1.
2. `$target_contract` = READ `$$target_skill_md`.
3. `$semantic_context` = DERIVE from `$$test_contract`, `$target_contract`, `$$diff_report`, and concise excerpts from expected and actual files.
4. `$$semantic_report` = JUDGE each diff as one of:
   - `blocking_failure`: violates target skill output contract or fixture oracle intent;
   - `non_behavioral_drift`: formatting, ordering, or equivalent phrasing that does not change the target skill outcome;
   - `runner_ambiguity`: fixture or TEST.md lacks enough specificity to decide.
5. IF any `blocking_failure`:
   5.1 `$$verdict` = MARK `FAIL`.
6. ELSE IF any `runner_ambiguity`:
   6.1 `$$verdict` = MARK `BLOCKED`.
7. ELSE:
   7.1 `$$verdict` = MARK `PASS`.

### Phase 8 - Emit compact evaluator report
> produces: `$$summary`

1. `$$summary` = DRAFT compact Markdown report:
   - `Verdict`: `$$verdict`;
   - `Failures`: issue IDs and affected paths only;
   - `Diff Evidence`: concise missing, extra, and content diff excerpts;
   - `Semantic Judgment`: blocking vs non-behavioral vs ambiguous rationale;
   - `Fix Instructions`: direct instructions for the next agent that will fix the target skill or fixture.
2. EMIT `$$summary` to user.
3. ASSERT no report file, issue file, metadata file, fixture mutation, target skill patch, or plan file was written by this skill.

## Section 4 - Guardrails

- This skill MUST run exactly one user-specified scenario per invocation.
- This skill MUST NOT auto-discover all scenarios or run an entire `.tests/` suite.
- This skill MUST NOT write report files; all evaluator output is chat-only.
- This skill MUST NOT create `.tests/<scenario>/issues/`, `.tests/reports/`, `test-report.md`, scenario README files, or manifest files.
- This skill MUST NOT mutate `before/`, `after/`, `TEST.md`, the target skill, or the plan file that requested execution.
- The tested-skill subagent MUST NOT read `.tests/`, `TEST.md`, `after/`, `.cursor/plans`, previous report folders, issue folders, or answer oracle material.
- The tested-skill subagent MUST NOT be told expected diffs, expected files, or oracle excerpts.
- The runner MAY read `after/` only after the tested-skill subagent completes or declares blocker.
- The runner MUST compare filesystem state before semantic judging.
- The runner MUST treat missing `before/`, missing `after/`, and invalid `TEST.md` as test definition failures, not as target skill failures.
- The runner MUST preserve sandbox contents until the chat report has been emitted.
- The runner MUST NOT fix failures; the next agent consumes the evaluator report and performs repairs.

## Section 5 - Issue IDs

| ID | Meaning |
|---|---|
| `MISSING_TEST_CONTRACT` | Target skill has no `.tests/TEST.md`. |
| `INVALID_TEST_CONTRACT` | `TEST.md` lacks required before/after, oracle isolation, or filesystem comparison rules. |
| `UNSUPPORTED_TEST_CONTRACT` | `TEST.md` explicitly requires persistent report files and forbids chat-only reporting. |
| `MISSING_SCENARIO` | Named scenario directory does not exist. |
| `MISSING_BEFORE` | Named scenario has no executable `before/` seed. |
| `MISSING_ORACLE` | Named scenario has no `after/` oracle. |
| `ORACLE_IN_BEFORE` | `before/` contains `.tests`, `after`, report, plan, or oracle material. |
| `SANDBOX_ORACLE_CONTAMINATION` | Sandbox creation copied forbidden oracle material. |
| `RUNNER_ERROR` | Sandbox setup, subagent launch, or comparison failed. |
| `SKILL_BLOCKED` | Tested skill stopped with a declared blocker. |
| `MISSING_FILE` | Expected file is absent from sandbox result. |
| `EXTRA_FILE` | Sandbox produced a file not present in `after/`. |
| `CONTENT_DIFF` | File exists in both trees but content differs. |

## Section 6 - Cross-References

- `/skill-test-setup` - creates the `before/`, `after/`, and `TEST.md` fixtures consumed by this runner.
- `/programlike-skill-creator` - source style for program-like SOP notation.
