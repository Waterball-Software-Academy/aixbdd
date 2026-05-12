---
name: skill-test-setup
description: Set up before/after fixtures for testing a skill. Use when the user wants to create `.tests/<scenario>/before` and `.tests/<scenario>/after` for any Claude or Cursor skill, grill the user to define a skill's workflow role, derive upstream workflow chain from skill references, execute upstream skills to produce the tested skill's `before`, or define expected skill outcomes test-first.
metadata:
  user-invocable: true
  source: global
  skill-type: test-setup
---

# skill-test-setup

Set up fixture scenarios for testing skills by deriving the tested skill's workflow role, executing confirmed upstream skills to produce `before/`, and collaborating with the user to define `after/`.

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
| R1 | `<target-skill>/SKILL.md` | Phase 1 + Phase 2 | Tested skill entrypoint, description, SOP phases, references, and cross references. |
| R2 | `<target-skill>/references/` | Phase 2 | Stable skill-local knowledge used to infer workflow role and upstream/downstream position. |
| R3 | `<target-skill>/assets/` | Phase 2 | Stable templates or fixture contracts that reveal expected inputs and outputs. |
| R4 | `<target-skill>/.tests/TEST.md` | Phase 8 | Test runner contract; created on first setup when missing. |
| R5 | `<target-skill>/.tests/<scenario>/before/` | Phase 6 | Fixture cwd seed for the tested skill. |
| R6 | `<target-skill>/.tests/<scenario>/after/` | Phase 7 | Expected fixture outcome. |

## §2 FIXTURE CONTRACT

This skill writes only:

- `<target-skill>/.tests/TEST.md` when it does not exist during first setup;
- `<target-skill>/.tests/<scenario>/before/`;
- `<target-skill>/.tests/<scenario>/after/`.

This skill MUST NOT write scenario metadata files, scenario README files, test execution reports, gap reports, or issue reports. Test execution and gap reporting belong to a separate test runner skill.

Two setup intents are supported, and the user MUST choose one every run:

| Mode | Name | Target skill execution policy |
|---|---|---|
| A | Regression fixture setup | The target skill MAY be executed only after user confirmation, to produce a draft after fixture. |
| B | Test-driven skill development | The target skill MUST NOT be executed; `after/` is built by grilling the user and patching expected outcome by collaboration. |

## §3 SOP

### Phase 1 — BIND target skill and scenario
> produces: `$$target_skill_dir`, `$$target_skill_md`, `$$tests_root`, `$$scenario_name`, `$$scenario_dir`, `$$before_dir`, `$$after_dir`

1. [USER INTERACTION] `$$target_skill_dir` = ASK target skill directory or skill invocation name.
2. `$$target_skill_dir` = COMPUTE absolute skill directory from user input.
3. `$$target_skill_md` = COMPUTE `${$$target_skill_dir}/SKILL.md`.
4. ASSERT path_exists(`$$target_skill_md`).
   4.1 IF assertion fails:
       4.1.1 EMIT "target skill must have SKILL.md".
       4.1.2 STOP.
5. [USER INTERACTION] `$$scenario_name` = ASK scenario name using filesystem-safe directory naming.
6. `$$tests_root` = COMPUTE `${$$target_skill_dir}/.tests`.
7. `$$scenario_dir` = COMPUTE `${$$tests_root}/${$$scenario_name}`.
8. `$$before_dir` = COMPUTE `${$$scenario_dir}/before`.
9. `$$after_dir` = COMPUTE `${$$scenario_dir}/after`.
10. `$existing_fixture` = MATCH path_exists(`$$before_dir`) OR path_exists(`$$after_dir`).
11. IF `$existing_fixture`:
    11.1 [USER INTERACTION] `$overwrite_scope` = ASK exact existing before/after files or directories user permits this skill to overwrite.
    11.2 ASSERT `$overwrite_scope` is explicit.
    11.3 IF assertion fails: STOP.

### Phase 2 — DERIVE workflow role
> produces: `$$target_skill_text`, `$$reference_index`, `$$workflow_chain_candidate`, `$$target_role_model`

1. `$$target_skill_text` = READ `$$target_skill_md`.
2. `$$reference_index` = READ stable local references and assets under `$$target_skill_dir`, excluding `.tests`, generated reports, caches, and plans.
3. `$$workflow_chain_candidate` = THINK from `$$target_skill_text`, `$$reference_index`, cross references, upstream/downstream sections, trigger descriptions, and SOP phases.
4. `$$target_role_model` = DRAFT:
   - tested skill responsibility;
   - upstream skills that must run before it;
   - downstream skills that consume its output;
   - artifacts it expects as input;
   - artifacts it is expected to write.
5. ASSERT `$$workflow_chain_candidate` identifies the target skill position.
   5.1 IF assertion fails:
       5.1.1 [USER INTERACTION] `$manual_chain` = ASK user to provide full workflow chain.
       5.1.2 `$$workflow_chain_candidate` = PARSE `$manual_chain`.

### Phase 3 — GRILL user for phase contract
> produces: `$$workflow_chain`, `$$phase_contract`, `$$setup_intent`

1. [USER INTERACTION] `$$setup_intent` = ASK user to choose exactly one:
   - A = regression fixture setup;
   - B = test-driven skill development.
2. ASSERT `$$setup_intent` in {A, B}.
3. LOOP per `$phase` in `$$workflow_chain_candidate`
   3.1 [USER INTERACTION] `$phase_answers` = ASK:
       - what exact input this workflow step receives;
       - which cwd it must run in;
       - what files it is allowed to read;
       - what files it is expected to write;
       - what would make this step invalid as upstream setup.
   3.2 `$$phase_contract[$phase]` = PARSE `$phase_answers`.
   3.3 ASSERT phase contract includes cwd, input artifacts, output artifacts, and stop condition.
      3.3.1 IF assertion fails: GOTO #3.1.
   END LOOP
4. `$$workflow_chain` = DERIVE confirmed chain from `$$workflow_chain_candidate` and `$$phase_contract`.

### Phase 4 — CONFIRM execution plan
> produces: `$$execution_plan`, `$$confirmation`

1. `$$execution_plan` = RENDER:
   - target skill;
   - setup mode A or B;
   - full upstream chain before target skill;
   - cwd for each upstream step;
   - inputs for each upstream step;
   - expected outputs from each upstream step;
   - exact `before/` and `after/` paths;
   - exact existing paths that will be overwritten, if any.
2. EMIT `$$execution_plan` to user.
3. [USER INTERACTION] `$$confirmation` = ASK "confirm execution plan?"
4. BRANCH `$$confirmation`
   confirmed → GOTO #5.1
   revise    → GOTO #3.1
   cancel    → STOP
5. ASSERT `$$confirmation == confirmed`.

### Phase 5 — EXECUTE upstream chain
> produces: `$$upstream_sandbox`, `$$upstream_result`

1. `$$upstream_sandbox` = CREATE isolated sandbox outside `$$tests_root`.
2. LOOP per `$upstream_step` before the target skill in `$$workflow_chain`
   2.1 WRITE cwd and inputs per `$$phase_contract[$upstream_step]` into `$$upstream_sandbox`.
   2.2 ASSERT cwd excludes `$$tests_root`, `$$after_dir`, and answer oracles.
   2.3 TRIGGER the upstream skill or command specified by `$upstream_step`.
   2.4 WAIT for completion.
   2.5 MARK changed files and declared blockers.
   2.6 IF upstream step fails:
       2.6.1 EMIT blocker summary.
       2.6.2 STOP.
   END LOOP
3. `$$upstream_result` = COMPUTE final filesystem state after the immediate predecessor of target skill.

### Phase 6 — WRITE before fixture
> produces: `$$before_written`

1. CREATE `$$tests_root`.
2. CREATE `$$scenario_dir`.
3. IF path_exists(`$$before_dir`):
   3.1 ASSERT user explicitly allowed overwriting `$$before_dir` or selected files.
   3.2 IF assertion fails: STOP.
4. WRITE `$$before_dir` ← `$$upstream_result`.
5. ASSERT `$$before_dir` contains no `.tests`, `after`, issue report, gap report, or answer oracle.
6. `$$before_written` = MARK written path list.

### Phase 7 — BUILD after fixture
> produces: `$$after_written`

1. IF path_exists(`$$after_dir`):
   1.1 ASSERT user explicitly allowed overwriting `$$after_dir` or selected files.
   1.2 IF assertion fails: STOP.
2. WRITE `$$after_dir` ← contents of `$$before_dir`.
3. BRANCH `$$setup_intent`
   A → GOTO #7.4
   B → GOTO #7.8
4. [USER INTERACTION] `$run_target` = ASK whether to execute the target skill to produce a draft `after/`.
5. IF `$run_target` is confirmed:
   5.1 TRIGGER target skill in sandbox seeded from `$$before_dir`.
   5.2 WAIT for completion.
   5.3 WRITE `$$after_dir` ← target skill result.
6. [USER INTERACTION] `$regression_adjustments` = ASK what corrections are required before freezing `after/`.
7. EDIT `$$after_dir` with user-approved corrections.
8. IF `$$setup_intent == B`:
   8.1 ASSERT target skill has not been executed.
   8.2 LOOP per target skill phase in `$$target_role_model`
       8.2.1 [USER INTERACTION] `$expected_delta` = ASK expected output delta for that phase.
       8.2.2 EDIT `$$after_dir` with user-approved expected delta.
       END LOOP
9. ASSERT `$$after_dir` contains expected outcome only, not runner reports or metadata.
10. `$$after_written` = MARK written path list.

### Phase 8 — ENSURE TEST.md
> produces: `$$test_contract_status`

1. `$test_md` = COMPUTE `${$$tests_root}/TEST.md`.
2. IF path_exists(`$test_md`):
   2.1 `$$test_contract_status` = MARK "existing TEST.md preserved".
   2.2 GOTO #9.1.
3. CREATE `$$tests_root`.
4. WRITE `$test_md` ← generic fixture runner contract:
   - scenario structure `.tests/<scenario>/before` and `.tests/<scenario>/after`;
   - sandbox cwd seeded from `before/`;
   - oracle isolation for `after/`;
   - runner compares sandbox result to `after/`;
   - runner, not this setup skill, writes reports.
5. `$$test_contract_status` = MARK "created TEST.md".

### Phase 9 — REPORT setup summary

1. `$summary` = DRAFT:
   - target skill path;
   - scenario path;
   - setup mode A or B;
   - upstream chain used to create `before/`;
   - written `before/` and `after/` paths;
   - TEST.md status.
2. EMIT `$summary`.
3. ASSERT no scenario metadata, README, gap report, issue report, or test execution report was written.

## §4 GUARDRAILS

- This skill MUST NOT write `.tests/<scenario>/manifest.yml`.
- This skill MUST NOT write `.tests/<scenario>/README.md`.
- This skill MUST NOT write test execution reports, gap reports, or issue reports.
- This skill MUST NOT execute the target skill in mode B.
- This skill MUST NOT execute upstream skills before the user confirms chain, cwd, inputs, and expected outputs.
- This skill MUST NOT use `after/` as readable input for upstream chain or target skill execution.
- This skill MUST NOT create `before/` from an unreviewed cwd snapshot.
- This skill MAY overwrite existing before/after content only when the user names the exact allowed overwrite scope.

## §5 CROSS-REFERENCES

- `/programlike-skill-creator` — source style for program-like SOP notation.
- `.tests/TEST.md` inside each target skill — runner contract consumed by a separate test execution skill.
