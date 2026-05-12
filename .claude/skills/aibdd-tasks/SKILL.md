---
name: aibdd-tasks
description: Generate `${CURRENT_PLAN_PACKAGE}/tasks.md` after `/aibdd-plan` by weaving impacted feature scope, implementation topology, and per-feature TDD flow into a structured markdown task list. TRIGGER when the user asks for post-plan task breakdown or `/aibdd-tasks`. SKIP when the current plan package, feature package, or accepted planning artifacts are missing.
metadata:
  user-invocable: true
  source: project-level
---

# aibdd-tasks

Generate a structured `tasks.md` from a completed AIBDD plan package.

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
| R1 | `references/role-and-contract.md` | global | Define role, inputs, outputs, non-goals, and completion contract for `/aibdd-tasks`. |
| R2 | `references/path-contract.md` | global | Define arguments.yml keys, resolved paths, and tasks artifact destination. |
| R3 | `.claude/skills/aibdd-plan/references/impacted-feature-files-contract.md` | global | Define the upstream impacted-feature scope contract exported by `/aibdd-plan`. |
| R4 | `references/tasks-md-shape-contract.md` | global | Define the required markdown phase shape, per-feature template, and no-work sentences. |
| R5 | `references/topology-contract.md` | global | Define parser expectations, topo-wave semantics, and parser-failure fallback rules. |
| R6 | `references/green-wave-allocation-rules.md` | global | Define how global implementation waves are sliced into feature-specific GREEN plans. |
| R7 | `references/implementation-task-wording-contract.md` | global | Define how GREEN task wording must distinguish new classes from existing classes or methods. |
| R8 | `references/quality-gate-contract.md` | global | Define deterministic and semantic veto conditions for generated tasks artifacts. |
| R9 | `assets/templates/tasks-md.template.md` | global | Provide the document-level tasks.md rendering skeleton. |
| R10 | `assets/templates/feature-phase.template.md` | global | Provide the fixed per-feature phase shell with RED / GREEN / Refactor wording. |

## §2 SOP

### Phase 1 — BIND tasks context
> produces: `$$skill_dir`, `$$workspace_root`, `$$args_path`, `$$paths`, `$$current_plan_package`, `$$plan_md_path`, `$$research_md_path`, `$$internal_structure_path`, `$$feature_specs_dir`, `$$boundary_map_path`, `$$tasks_md_path`

1. `$$skill_dir` = COMPUTE current skill directory path
2. `$$workspace_root` = COMPUTE current workspace directory path
3. `$$args_path` = COMPUTE `${$$workspace_root}/.aibdd/arguments.yml`
4. ASSERT `$$args_path` exists
   4.1 IF assertion fails:
       4.1.1 EMIT "`.aibdd/arguments.yml` 不存在；請先完成 /aibdd-kickoff。" to user
       4.1.2 STOP
5. `$paths_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/resolve_tasks_paths.py" "${$$args_path}"`
6. ASSERT `$paths_out.exit_code == 0`
   6.1 IF assertion fails:
       6.1.1 EMIT `$paths_out.stdout` to user
       6.1.2 STOP
7. `$$paths` = PARSE `$paths_out.stdout`, schema=`json`
8. `$$current_plan_package` = PARSE `$$paths.current_plan_package`
9. `$$plan_md_path` = PARSE `$$paths.plan_md`
10. `$$research_md_path` = PARSE `$$paths.research_md`
11. `$$internal_structure_path` = PARSE `$$paths.plan_internal_structure`
12. `$$feature_specs_dir` = PARSE `$$paths.feature_specs_dir`
13. `$$boundary_map_path` = PARSE `$$paths.boundary_map`
14. `$$tasks_md_path` = PARSE `$$paths.tasks_md`
15. ASSERT `$$current_plan_package` is non-empty and `$$feature_specs_dir` is non-empty
    15.1 IF assertion fails:
        15.1.1 EMIT "current plan package 或 feature package 未綁定；請先完成 /aibdd-plan 與 function package 綁定。" to user
        15.1.2 STOP

### Phase 2 — LOAD plan and truth inputs
> produces: `$$plan_md`, `$$research_md`, `$$internal_structure_text`, `$$boundary_map_text`, `$$feature_bundle`, `$$impacted_section_text`, `$$code_symbol_index`

1. `$$plan_md` = READ `$$plan_md_path`
2. ASSERT `$$plan_md` is non-empty
   2.1 IF assertion fails:
       2.1.1 EMIT "`plan.md` 不存在或為空；請先完成 /aibdd-plan。" to user
       2.1.2 STOP
3. `$$research_md` = READ `$$research_md_path`
4. `$$internal_structure_text` = READ `$$internal_structure_path`
5. `$$boundary_map_text` = READ `$$boundary_map_path`
6. `$$feature_bundle` = READ all `*.feature` under `$$feature_specs_dir`
7. ASSERT `$$feature_bundle` is non-empty
   7.1 IF assertion fails:
       7.1.1 EMIT "feature package 內沒有 `.feature` 檔案；無法產出 tasks.md。" to user
       7.1.2 STOP
8. `$$impacted_section_text` = PARSE `$$plan_md` for `## Impacted Feature Files` section
9. `$symbol_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/build_code_symbol_index.py" "${$$args_path}"`
10. ASSERT `$symbol_out.exit_code == 0`
    10.1 IF assertion fails:
        10.1.1 EMIT `$symbol_out.stdout` to user
        10.1.2 STOP
11. `$$code_symbol_index` = PARSE `$symbol_out.stdout`, schema=`json`

### Phase 3 — PARSE implementation topology
> produces: `$$parser_verdict`, `$$class_graph`, `$$plan_level_waves`, `$$fallback_strategy`

1. `$topo_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/parse_internal_structure_topo.py" "${$$internal_structure_path}"`
2. `$topo_ok` = MATCH `$topo_out.exit_code == 0`
3. BRANCH `$topo_ok` ? GOTO #3.4 : GOTO #3.7
4. `$$parser_verdict` = PARSE `$topo_out.stdout`, schema=`json`
5. `$$class_graph` = PARSE `$$parser_verdict.class_graph`
6. `$$plan_level_waves` = PARSE `$$parser_verdict.plan_level_waves`
7. `$$fallback_strategy` = THINK per [`reasoning/aibdd-tasks/01-semantic-planning-when-parse-fails.md`](reasoning/aibdd-tasks/01-semantic-planning-when-parse-fails.md), input=`$$plan_md`, `$$research_md`, `$$boundary_map_text`, `$$feature_bundle`
8. IF `$topo_ok` == false:
   8.1 `$$parser_verdict` = DERIVE `{ status: "fallback", reason: $topo_out.stdout }`
   8.2 `$$class_graph` = COMPUTE empty graph
   8.3 `$$plan_level_waves` = COMPUTE empty list

### Phase 4 — RESOLVE feature phase order
> produces: `$$ordered_feature_paths`, `$$feature_phase_labels`

1. `$$ordered_feature_paths` = THINK per [`reasoning/aibdd-tasks/02-resolve-feature-phase-order.md`](reasoning/aibdd-tasks/02-resolve-feature-phase-order.md), input=`$$impacted_section_text`, `$$feature_bundle`, `$$plan_md`, `$$research_md`, `$$boundary_map_text`, contract=[`.claude/skills/aibdd-plan/references/impacted-feature-files-contract.md`](.claude/skills/aibdd-plan/references/impacted-feature-files-contract.md)
2. ASSERT `$$ordered_feature_paths` is non-empty
   2.1 IF assertion fails:
       2.1.1 EMIT "無法解析 impacted feature scope；請先修正 plan.md 的 `Impacted Feature Files` 或補足相關 planning evidence。" to user
       2.1.2 STOP
3. `$$feature_phase_labels` = DERIVE display labels from `$$ordered_feature_paths`, `$$feature_bundle`

### Phase 5 — BUILD feature phase scaffold
> produces: `$$feature_phase_scaffold`

1. `$scaffold_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/build_feature_phase_scaffold.py" "${$$args_path}"`
2. ASSERT `$scaffold_out.exit_code == 0`
   2.1 IF assertion fails:
       2.1.1 EMIT `$scaffold_out.stdout` to user
       2.1.2 STOP
3. `$$feature_phase_scaffold` = PARSE `$scaffold_out.stdout`, schema=`json`
4. ASSERT length(`$$feature_phase_scaffold.feature_phases`) == length(`$$ordered_feature_paths`)
5. ASSERT every `$$feature_phase_scaffold.feature_phases[*].section_titles` equals `["RED", "GREEN", "Refactor"]`

### Phase 6 — ALLOCATE semantic fill
> produces: `$$allocation_by_feature`, `$$infra_section_model`, `$$integration_section_model`

1. `$$allocation_by_feature` = THINK per [`reasoning/aibdd-tasks/03-allocate-green-waves-per-feature.md`](reasoning/aibdd-tasks/03-allocate-green-waves-per-feature.md), input=`$$ordered_feature_paths`, `$$feature_bundle`, `$$plan_md`, `$$research_md`, `$$boundary_map_text`, `$$plan_level_waves`, `$$parser_verdict`, `$$feature_phase_scaffold`, `$$code_symbol_index`, rules=[`references/green-wave-allocation-rules.md`](references/green-wave-allocation-rules.md), wording=[`references/implementation-task-wording-contract.md`](references/implementation-task-wording-contract.md)
2. ASSERT every feature in `$$ordered_feature_paths` has at least one wave in `$$allocation_by_feature`
3. ASSERT no feature reuses the full unmodified global topo waves without feature-specific rationale
4. `$$infra_section_model` = THINK per [`reasoning/aibdd-tasks/04-infra-integration-extraction.md`](reasoning/aibdd-tasks/04-infra-integration-extraction.md), focus=`infra`, input=`$$plan_md`, `$$research_md`, `$$allocation_by_feature`
5. `$$integration_section_model` = THINK per [`reasoning/aibdd-tasks/04-infra-integration-extraction.md`](reasoning/aibdd-tasks/04-infra-integration-extraction.md), focus=`integration`, input=`$$plan_md`, `$$research_md`, `$$allocation_by_feature`
6. IF `$$infra_section_model.items` is empty:
   6.1 `$$infra_section_model` = DERIVE explicit no-work sentence per [`references/tasks-md-shape-contract.md`](references/tasks-md-shape-contract.md)
7. IF `$$integration_section_model.items` is empty:
   7.1 `$$integration_section_model` = DERIVE explicit no-work sentence per [`references/tasks-md-shape-contract.md`](references/tasks-md-shape-contract.md)

### Phase 7 — RENDER tasks artifact
> produces: `$$tasks_doc`

1. `$feature_phase_blocks` = RENDER [`assets/templates/feature-phase.template.md`](assets/templates/feature-phase.template.md) per `$$feature_phase_scaffold.feature_phases`, filling only `green_wave_block` from `$$allocation_by_feature`
2. `$$tasks_doc` = RENDER [`assets/templates/tasks-md.template.md`](assets/templates/tasks-md.template.md) with `$$infra_section_model`, `$feature_phase_blocks`, `$$feature_phase_scaffold.integration_phase.phase_number`, `$$integration_section_model`
3. WRITE `$$tasks_md_path` ← `$$tasks_doc`

### Phase 8 — ASSERT tasks quality
> produces: `$$script_verdict`, `$$semantic_verdict`, `$$quality_verdict`

1. `$scaffold_check_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_feature_phase_scaffold.py" "${$$args_path}"`
2. `$tasks_check_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_tasks_md.py" "${$$args_path}"`
3. `$wording_check_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_tasks_codewording.py" "${$$args_path}"`
4. `$$script_verdict` = PARSE merged JSON of `$scaffold_check_out`, `$tasks_check_out`, `$wording_check_out`
5. ASSERT `$$script_verdict.ok == true`
   5.1 IF assertion fails:
       5.1.1 EMIT `$$script_verdict` to user
       5.1.2 STOP
6. `$quality_contract` = PARSE [`references/quality-gate-contract.md`](references/quality-gate-contract.md)
7. `$$semantic_verdict` = JUDGE per `$quality_contract`, input=`$$tasks_doc`, `$$feature_phase_scaffold`, `$$parser_verdict`, `$$ordered_feature_paths`, `$$allocation_by_feature`, `$$infra_section_model`, `$$integration_section_model`, `$$code_symbol_index`
8. ASSERT `$$semantic_verdict.verdict != VETO`
   8.1 IF assertion fails:
       8.1.1 EMIT `$$semantic_verdict` to user
       8.1.2 STOP
9. `$$quality_verdict` = DERIVE combined verdict from `$$script_verdict`, `$$semantic_verdict`

### Phase 9 — REPORT downstream handoff
> produces: (none)

1. `$summary` = DRAFT concise summary from `$$tasks_md_path`, `$$feature_phase_scaffold`, `$$parser_verdict`, `$$quality_verdict`
2. EMIT `$summary` to user
