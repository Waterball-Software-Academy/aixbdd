---
name: aibdd-aibdd-auto-frontend-nextjs-pages-tasks
description: AIBDD 前端流程的 tasks-generator。讀三條 SSOT（Pencil .pen 設計檔、backend OpenAPI 契約、backend feature files 行為樣本參考），合成出一份 triple-anchored、依賴排序明確、無 TDD red→green 形式的 tasks.md，作為下游 `/aibdd-auto-frontend-msw-api-layer`（Phase 1 MSW layer）與 `/aibdd-auto-frontend-nextjs-pages`（Phase 2 逐 frame 落頁）的執行藍圖。沿用 `aibdd-tasks` 的編號 / checkbox / 依賴句型，但前端不寫 .feature 不寫 step definitions。TRIGGER when 使用者下 `/aibdd-aibdd-auto-frontend-nextjs-pages-tasks`、想在跑 frontend MSW + pages 之前先看到完整任務藍圖、或 spec package 已就緒（.pen + api.yml + feature files 三者齊備）。SKIP when 三條 SSOT 任一缺漏、要求改打 backend tasks（請改用 `/aibdd-tasks`）、或要求保留 TDD red→green 章節。
metadata:
  user-invocable: true
  source: project-level
---

# aibdd-aibdd-auto-frontend-nextjs-pages-tasks

讀三條 SSOT 合成單一 triple-anchored 前端 tasks.md，作為 MSW layer + Next.js pages 兩個下游 skill 的執行藍圖。

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
| R1 | [`references/ssot-triangle.md`](references/ssot-triangle.md) | global | 三角 SSOT 定義（設計 / 契約 / 行為樣本參考）+ 路徑解析優先序 |
| R2 | [`references/triple-anchor-rule.md`](references/triple-anchor-rule.md) | global | 每條 task 必須左／中／右三錨齊備的硬規定 + 例外（純 token / gate task 可略中右錨） |
| R3 | [`references/feature-files-as-reference.md`](references/feature-files-as-reference.md) | global | feature files 為「參考用」非「嚴格 1:1」的措辭規範 |
| R4 | [`references/no-tdd-rule.md`](references/no-tdd-rule.md) | global | 禁止寫 .feature / step definitions / cucumber red→green，純視覺 + 行為 acceptance |
| R5 | [`references/task-id-scheme.md`](references/task-id-scheme.md) | global | T01 起跳的編號規則 + Phase 1 / 2 / 3 切段 + dependency 表達 |
| R6 | [`assets/templates/tasks-md.template.md`](assets/templates/tasks-md.template.md) | Phase 3 | tasks.md 輸出骨架（含 SSOT 三角表 + 任務地圖 + 三個 Phase + Acceptance 段） |

## §2 SOP

### Phase 1 — LOAD three SSOTs
> produces: `$$args`, `$$pen_path`, `$$preview_dir`, `$$api_spec_path`, `$$contracts_dir`, `$$feature_glob`, `$$tasks_output_path`, `$$frames`, `$$operations`, `$$feature_outlines`

1. `$args_path` = COMPUTE `${PROJECT_ROOT}/.aibdd/arguments.yml`
2. `$args_exists` = MATCH path_exists(`$args_path`)
3. BRANCH `$args_exists` ? GOTO #1.5 : GOTO #1.4.1
   4.1 `$missing_args_msg` = RENDER ".aibdd/arguments.yml 不存在；請先執行 /aibdd-kickoff 或 /aibdd-auto-frontend-apifirst-msw-starter 補上"
   4.2 EMIT `$missing_args_msg` to user
   4.3 STOP
5. `$$args` = PARSE `$args_path`, schema=yaml
6. `$$pen_path`          = DERIVE `$$args.UIUX_PEN_FILE` ?? "specs/frontend/uiux/user-journey.pen"
7. `$$preview_dir`       = DERIVE `$$args.UIUX_PREVIEW_DIR` ?? "specs/frontend/uiux/preview"
8. `$$api_spec_path`     = DERIVE `$$args.API_SPEC_FILE` ?? "specs/backend/api.yml"
9. `$$contracts_dir`     = DERIVE `$$args.BACKEND_CONTRACTS_DIR` ?? "specs/backend/contracts"
10. `$$feature_glob`     = DERIVE `$$args.BACKEND_FEATURE_FILES_GLOB` ?? "specs/backend/packages/**/features/*.feature"
11. `$$tasks_output_path` = DERIVE `$$args.TASKS_OUTPUT_PATH` ?? "specs/000-kickoff-placeholder/frontend/tasks.md"
12. `$pen_exists`     = MATCH path_exists(`$$pen_path`)
13. `$api_exists`     = MATCH path_exists(`$$api_spec_path`)
14. `$features_glob_count` = COMPUTE count(glob(`$$feature_glob`))
15. ASSERT `$pen_exists` ∧ `$api_exists` ∧ `$features_glob_count` ≥ 1 per [`references/ssot-triangle.md`](references/ssot-triangle.md) §"三角缺一不可"
16. IF assertion #1.15 fails:
    16.1 `$ssot_msg` = RENDER "三角 SSOT 缺漏：pen=`$pen_exists` api=`$api_exists` features=`$features_glob_count`；補齊後再試"
    16.2 EMIT `$ssot_msg` to user
    16.3 STOP
17. `$pen_raw`        = READ `$$pen_path`
18. `$pen_doc`        = PARSE `$pen_raw`, schema=json
19. `$$frames`        = SUMMARIZE `$pen_doc.children` filtered by type==frame and name not starting with "Design System" → list of `{node_id, name, width, height, preview_png}` per [`references/ssot-triangle.md`](references/ssot-triangle.md) §"frame 提取規則"
20. `$api_raw`        = READ `$$api_spec_path`
21. `$api_doc`        = PARSE `$api_raw`, schema=openapi
22. `$$operations`    = SUMMARIZE `$api_doc.paths` → list of `{operation_id, method, path, request_schema_ref, response_schema_ref, feature_file_hint}` per [`references/ssot-triangle.md`](references/ssot-triangle.md) §"operation 提取規則"
23. `$feature_files`  = COMPUTE glob(`$$feature_glob`)
24. `$$feature_outlines` = SUMMARIZE `$feature_files` → list of `{file, scenario_count, example_categories, fixture_seed_hints}` per [`references/feature-files-as-reference.md`](references/feature-files-as-reference.md)

### Phase 2 — SYNTHESIZE task graph
> produces: `$$frame_to_react`, `$$endpoint_to_msw`, `$$task_graph`

1. `$$frame_to_react` = THINK per [`references/triple-anchor-rule.md`](references/triple-anchor-rule.md) §"frame → React component 對映"; for each `$frame` in `$$frames`, map to `{route_path, page_component, child_components, reusable_pen_components}`
2. `$$endpoint_to_msw` = THINK per [`references/triple-anchor-rule.md`](references/triple-anchor-rule.md) §"endpoint → MSW handler 對映"; for each `$op` in `$$operations`, map to `{handler_module, fixture_module, api_client_func, related_feature_file}`
3. `$design_token_task`    = DRAFT task object `{phase: 2, id_hint: T05, kind: design-token-binding, anchors: {left, middle: null, right: null}}`  # exception: design token 全局 task 中右錨可空 per refs/triple-anchor-rule.md §exceptions
4. `$msw_layer_tasks`      = DRAFT list of 4 task objects (zod-schemas / fixtures / handlers / api-client) ← `$$endpoint_to_msw`, anchors=triple per task
5. `$page_tasks`           = DRAFT list of `count($$frames)` task objects ← `$$frame_to_react`, anchors=triple per task
6. `$visual_gate_task`     = DRAFT task object `{phase: 3, id_hint: T<last>, kind: visual-parity-gate, anchors: {left: playwright-screenshot-diff, middle: null, right: all-frames}}`
7. `$$task_graph` = COMPUTE `[...$msw_layer_tasks, $design_token_task, ...$page_tasks, $visual_gate_task]`
8. LOOP per `$task` in `$$task_graph`
   8.1 `$anchors_ok` = JUDGE `$task.anchors` 符合 [`references/triple-anchor-rule.md`](references/triple-anchor-rule.md) §"必填欄位 + exception"
   8.2 ASSERT `$anchors_ok`
   END LOOP
9. `$ids_assigned` = DERIVE T01..T<N> 編號到 `$$task_graph`，依 phase 升冪 + within-phase 依賴拓撲序 per [`references/task-id-scheme.md`](references/task-id-scheme.md)
10. `$$task_graph` = COMPUTE `$ids_assigned`

### Phase 3 — EMIT tasks.md
> produces: `$$tasks_md_path`

1. `$tmpl`             = READ [`assets/templates/tasks-md.template.md`](assets/templates/tasks-md.template.md)
2. `$header_block`     = RENDER `$tmpl` §header, vars={pen=`$$pen_path`, preview=`$$preview_dir`, api=`$$api_spec_path`, contracts=`$$contracts_dir`, features=`$$feature_glob`, frame_count=count(`$$frames`), op_count=count(`$$operations`)}
3. `$task_map_table`   = RENDER `$tmpl` §task-map, rows=`$$task_graph`
4. `$phase1_block`     = RENDER `$tmpl` §phase1-msw, tasks=filter(`$$task_graph`, kind ∈ {zod, fixtures, handlers, api-client})
5. `$phase2_block`     = RENDER `$tmpl` §phase2-pages, tasks=filter(`$$task_graph`, kind ∈ {design-token-binding, page})
6. `$phase3_block`     = RENDER `$tmpl` §phase3-gate, tasks=filter(`$$task_graph`, kind == visual-parity-gate)
7. `$tdd_check`        = JUDGE every task body in `[$phase1_block, $phase2_block, $phase3_block]` 不含 "red→green" / ".feature 檔" / "step definitions" / "cucumber" 等 TDD 字眼 per [`references/no-tdd-rule.md`](references/no-tdd-rule.md)
8. ASSERT `$tdd_check`
9. IF #3.8 assertion fails:
   9.1 `$tdd_msg` = RENDER "tasks 內容混入 TDD ceremony；重寫 phase blocks"
   9.2 EMIT `$tdd_msg` to user
   9.3 GOTO #3.4
10. `$ref_phrase_check` = JUDGE phase 1 fixtures task 描述使用「參考」語氣（contains 「參考」/「reference」）而非「逐 Example 1:1 對映」per [`references/feature-files-as-reference.md`](references/feature-files-as-reference.md)
11. ASSERT `$ref_phrase_check`
12. IF #3.11 assertion fails:
    12.1 `$phrase_msg` = RENDER "fixtures task 用詞過嚴；改回『參考』語氣"
    12.2 EMIT `$phrase_msg` to user
    12.3 GOTO #3.4
13. `$$tasks_md_path` = COMPUTE `${PROJECT_ROOT}/${$$tasks_output_path}`
14. `$parent_dir` = COMPUTE dirname(`$$tasks_md_path`)
15. CREATE `$parent_dir`
16. `$full_doc` = COMPUTE `$header_block` + "\n\n" + `$task_map_table` + "\n\n" + `$phase1_block` + "\n\n" + `$phase2_block` + "\n\n" + `$phase3_block`
17. WRITE `$$tasks_md_path` ← `$full_doc`

### Phase 4 — REPORT
> produces: (none)

1. `$summary` = DRAFT 繁體中文 ≤4 句報告 ← `$$tasks_md_path`, count(`$$task_graph`), count(`$$frames`), count(`$$operations`)
2. EMIT `$summary` to user
