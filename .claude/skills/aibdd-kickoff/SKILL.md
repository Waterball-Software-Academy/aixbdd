---
description: 專案初始化引導；支援 Python E2E、Java E2E、Next.js + Playwright 三個 stack，收集唯一 TLB 名稱（backend 或 frontend），產出 arguments.yml、boundary.yml、component-diagram.class.mmd 與 boundary skeleton。TRIGGER when 使用者說 kickoff、初始化專案、建 arguments.yml、新專案設定。SKIP when 需要多 TLB、Vue/Svelte 等其他 frontend 框架、Unit Test only、Mobile，或其他尚未支援的 stack。
metadata:
  skill-type: planner
  source: project-level
  user-invocable: true
name: aibdd-kickoff
---

# aibdd-kickoff

Initialize an AIBDD backend (Python E2E or Java E2E) by deriving stack-aware config and one top-level boundary truth skeleton.

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
  - path: references/question-catalog.md
    purpose: 定義 kickoff 題庫、互動文案與完成訊息模板
  - path: references/convention-mapping.md
    purpose: 定義技術堆疊路徑、arguments.yml 範例與 starter skill 對照
  - path: references/python-backend-packing.md
    purpose: 定義 Python E2E 後端的唯一 TLB packing 與架構落檔（stack=python_e2e 走此路徑）
  - path: references/java-backend-packing.md
    purpose: 定義 Java E2E 後端的唯一 TLB packing 與架構落檔（stack=java_e2e 走此路徑）
  - path: references/nextjs-frontend-packing.md
    purpose: 定義 Next.js + Playwright 前端的唯一 TLB packing 與架構落檔（stack=nextjs_playwright 走此路徑；reuse 4-folder boundary skeleton）
  - path: references/kickoff-plan-contract.md
    purpose: "定義 KICKOFF_PLAN.md schema、狀態值、question record、batch reply contract 與 final confirm contract"
  - path: assets/templates/kickoff-plan.template.md
    purpose: "提供 KICKOFF_PLAN.md 暫存訪談工作檔模板"
  - path: aibdd-core::diagram-file-naming.md
    purpose: "Mermaid compound extension：*.class.mmd／*.sequence.mmd（COMPONENT_DIAGRAM 檔名合約）"
  - path: assets/templates/arguments.template.yml
    purpose: "arguments.yml 的 byte-deterministic 模板（python-e2e）；占位符 {{TLB_ID}}、{{PROJECT_SPEC_LANGUAGE}}、{{BACKEND_SUBDIR}}"
  - path: assets/templates/arguments.template.java-e2e.yml
    purpose: "arguments.yml 的 byte-deterministic 模板（java-e2e）；占位符 {{PROJECT_SPEC_LANGUAGE}}、{{BACKEND_SUBDIR}}、{{GROUP_ID}}、{{ARTIFACT_ID}}、{{BASE_PACKAGE}}、{{JAVA_VERSION}}、{{SPRING_BOOT_VERSION}}、{{CUCUMBER_VERSION}}、{{JJWT_VERSION}}、{{POSTGRES_IMAGE_VERSION}}、{{DB_NAME}}"
  - path: assets/templates/arguments.template.nextjs-playwright.yml
    purpose: "arguments.yml 的 byte-deterministic 模板（nextjs-playwright）；占位符 {{PROJECT_SPEC_LANGUAGE}}、{{FRONTEND_SUBDIR}}、{{PROJECT_SLUG}}"
  - path: assets/templates/boundary.template.yml
    purpose: "boundary.yml 的 byte-deterministic 模板；占位符 {{TLB_ID}}"
  - path: assets/templates/component-diagram.class.template.mmd
    purpose: "Mermaid component class diagram 模板；占位符 {{TLB_ID}}"
  - path: assets/templates/test-strategy.placeholder.yml
    purpose: "test-strategy.yml placeholder（policies={}）"
  - path: assets/templates/shared-dsl.placeholder.yml
    purpose: "shared/dsl.yml placeholder（entries=[]）"
```

## §2 SOP

### §2.0 EXECUTION DISCIPLINE（進入 Phase 1 前必讀）

This skill is **planner-level** and **File First**. The executor MUST NOT:

1. 在 Phase 1 / Phase 2 對 user 發出任何 acknowledgment、status check 摘要、phase 流程預告、或「我會做 X 然後做 Y」說明文字。

2. **【File First Invariant】** 任何對 user 的提問都必須遵守 write → ask → write back 三段式：
   - **Step A（Write Questions）**：問題的 SSOT 是 `KICKOFF_PLAN.md`。Phase 2 必須先把整批 Q1–Q4 含 prompt / options / context 完整寫進檔案，且檔案落地（Phase 2.6 WRITE）後才允許進 Phase 3。
   - **Step B（Ask via Clarify-Loop）**：Phase 3.5 從**已寫入的檔案**讀回題目組 batch payload，透過 `DELEGATE /clarify-loop` 詢問。禁止 executor 自己在 chat 直接列題、自己 ASK、或在 file 之外另起一份問題集。
   - **Step C（Write Back Answers）**：Phase 3.9–3.10 必須把 user 的答案 writeback 進**同一份**`KICKOFF_PLAN.md`，每題狀態變 `answered` 後才允許離開 Phase 3。
   - **凡未先存檔就出題、或答完不寫回檔案，即違反 File First**。

3. 自行發明執行模式選單（如「A) 互動版 / B) 快速初始化 / C) 先看現況」）。`$$non_interactive` 是 **caller payload 旗標**，不是 user 可選的選項。

4. 在 Phase 3 之前以任何形式 yield turn 給 user。對 user 唯一合法的 yield 是 Phase 3.5 / Phase 5.4 的 `DELEGATE /clarify-loop`。

5. 違反任一條 == skill 啟動失敗，請立即停下並回報。

### Phase 1 — INITIALIZE plan context
> produces: `$$project_root`, `$$plan_path`, `$$plan_mode`, `$$non_interactive`

1. `$$project_root` = COMPUTE project root from caller payload or current workspace
2. `$project_root_ok` = MATCH `$$project_root` is non-empty and path_exists(`$$project_root`)
3. BRANCH `$project_root_ok` ? GOTO #1.4 : GOTO #1.3.1
   3.1 `$root_msg` = RENDER missing project-root guidance
   3.2 EMIT `$root_msg` to user
   3.3 STOP
4. `$$plan_path` = COMPUTE `${$$project_root}/KICKOFF_PLAN.md`
5. `$$non_interactive` = MATCH caller payload contains `non_interactive: true`, OR caller payload contains `defaults_profile: happy-path`, OR caller payload signals headless sandbox execution (e.g. `.tests/<scenario>/before` runtime origin)
   <!-- caller-payload-only：此 flag 由上游 caller 注入；executor 禁止對 user 詢問「要走 interactive 還是 happy-path」。User 永遠走 interactive 路徑（File First：先寫 KICKOFF_PLAN.md，再 DELEGATE /clarify-loop 出題）。 -->
6. BRANCH `$$non_interactive` ? GOTO #4.0 : GOTO #1.7
7. `$plan_exists` = MATCH path_exists(`$$plan_path`)
8. BRANCH `$plan_exists` ? GOTO #1.9 : GOTO #1.13
9. `$existing_plan` = READ `$$plan_path`
   9.1 IF READ fails:
       9.1.1 `$read_msg` = RENDER plan path and permission hint for `$$plan_path`
       9.1.2 EMIT `$read_msg` to user
       9.1.3 STOP
10. `$resume_payload` = DERIVE clarify-loop batch payload with one question id `q-resume-mode`, kind `CON`, options `resume | restart | cancel`, recommendation `resume`, recommendation_rationale 引用 [`references/question-catalog.md`](references/question-catalog.md) §resume-or-restart 模板
    10.1 [USER INTERACTION] `$resume_reply` = DELEGATE `/clarify-loop` with `$resume_payload`
11. `$$plan_mode` = CLASSIFY `$resume_reply` as `resume | restart | cancel`
12. BRANCH `$$plan_mode`
   resume  → GOTO #3.1
   restart → GOTO #2.1
   cancel  → STOP
13. `$$plan_mode` = COMPUTE `new`

Note: `$$args_path` 與 `$$artifact_paths` 延後到 Phase 4 等 q3-backend-layout 答案後再算（解析 `$$backend_root = ${$$project_root}/${$$backend_subdir}`，`$$backend_subdir` 為空時退化為 `${$$project_root}`）。

### Phase 2 — WRITE kickoff plan
> produces: `$$plan_doc`

1. `$template` = READ [`assets/templates/kickoff-plan.template.md`](assets/templates/kickoff-plan.template.md)
2. `$question_set` = DERIVE backend question records from [`references/question-catalog.md`](references/question-catalog.md) and [`references/kickoff-plan-contract.md`](references/kickoff-plan-contract.md)
3. ASSERT `q1-tech-stack` has exactly the three selectable options `python_e2e`, `java_e2e`, and `nextjs_playwright`, and no `Other`
   3.1 IF assertion fails:
       3.1.1 `$q1_msg` = RENDER "Q1 tech stack contract violation: must offer python_e2e and java_e2e only"
       3.1.2 EMIT `$q1_msg` to user
       3.1.3 STOP
4. `$artifact_plan` = DERIVE files and folders from the stack-specific packing reference — `python_e2e` → [`references/python-backend-packing.md`](references/python-backend-packing.md), `java_e2e` → [`references/java-backend-packing.md`](references/java-backend-packing.md), `nextjs_playwright` → [`references/nextjs-frontend-packing.md`](references/nextjs-frontend-packing.md) — with unresolved placeholders; ASSERT no plan package path, no boundary root `actors/`, no boundary root `features/`, no `coverage/`, no `entities/`, no `sub-boundaries/`. Stack-specific packing is finalised once Q1 is answered in Phase 3
5. `$$plan_doc` = RENDER `$template` with status=`collecting_answers`, `$question_set`, and `$artifact_plan`
6. WRITE `$$plan_path` ← `$$plan_doc`
   6.1 IF WRITE fails:
       6.1.1 `$plan_write_msg` = RENDER plan path and permission hint for `$$plan_path`
       6.1.2 EMIT `$plan_write_msg` to user
       6.1.3 STOP
7. ASSERT `$$plan_path` contains required sections per [`references/kickoff-plan-contract.md`](references/kickoff-plan-contract.md) §Required Sections
   7.1 IF assertion fails:
       7.1.1 DELETE `$$plan_path`
       7.1.2 `$contract_msg` = RENDER "KICKOFF_PLAN.md required sections contract violation"
       7.1.3 EMIT `$contract_msg` to user
       7.1.4 STOP
8. ASSERT path_exists(`$$plan_path`) AND `$$plan_doc` includes question records for `q1-tech-stack`, `q2-project-spec-language`, `q3-backend-service-name`, `q4-backend-layout` — File First invariant：四題必須都已落檔
   8.1 IF assertion fails:
       8.1.1 `$invariant_msg` = RENDER "File First invariant violated: KICKOFF_PLAN.md must contain all four question records before Phase 3 may delegate clarify-loop"
       8.1.2 EMIT `$invariant_msg` to user
       8.1.3 STOP

### Phase 3 — COLLECT answers in one batch
> produces: `$$resolved_plan`, `$$question_batch`, `$$batch_answers`

0. ASSERT path_exists(`$$plan_path`) — File First invariant：clarify-loop 只能在 KICKOFF_PLAN.md 已存檔後啟動
   0.1 IF assertion fails:
       0.1.1 `$pre_clarify_msg` = RENDER "File First invariant violated: cannot enter Phase 3 without KICKOFF_PLAN.md on disk"
       0.1.2 EMIT `$pre_clarify_msg` to user
       0.1.3 STOP
1. `$plan_doc` = READ `$$plan_path`
2. `$$question_batch` = PARSE all unanswered question records from `$plan_doc` in stable question-id order.
3. ASSERT `count($$question_batch) > 0` and `count($$question_batch) <= 4`
4. `$batch_payload` = DERIVE clarify-loop batch payload from `$$question_batch`, [`references/question-catalog.md`](references/question-catalog.md) §批次提問模板, and [`references/kickoff-plan-contract.md`](references/kickoff-plan-contract.md) §Batch Reply Contract（每題附 prompt、options、recommendation_rationale；anchor 與 routing 由 clarify-loop 內部依 runtime tool capability 自動決定）
5. `$$batch_answers` = DELEGATE `/clarify-loop` with `$batch_payload`
6. `$decision_bundle` = PARSE `$$batch_answers` into per-question raw answer and resolved decision map using [`references/kickoff-plan-contract.md`](references/kickoff-plan-contract.md) §Question IDs and §Batch Reply Contract
7. `$bundle_ok` = MATCH `$decision_bundle` contains resolved answers for every question in `$$question_batch`
8. IF `$bundle_ok` == false:
   8.1 `$unresolved_plan` = RENDER `$plan_doc` with unresolved note for missing or ambiguous question ids from `$decision_bundle`
   8.2 WRITE `$$plan_path` ← `$unresolved_plan`
   8.3 `$ambiguous_msg` = RENDER "`$$plan_path` 已標記 unresolved，請人工檢查或重答整批 kickoff 問題"
   8.4 EMIT `$ambiguous_msg` to user
   8.5 STOP
9. LOOP per `$question` in `$$question_batch`
   9.1 `$answer_block` = RENDER answer writeback block per [`references/kickoff-plan-contract.md`](references/kickoff-plan-contract.md) §Question Record Fields using `$decision_bundle[$question.id]`
   9.2 `$plan_doc` = RENDER `$plan_doc` with `$answer_block`
   END LOOP
10. WRITE `$$plan_path` ← `$plan_doc`
11. `$$resolved_plan` = READ `$$plan_path`
12. ASSERT all questions in `$$resolved_plan` have status `answered`
13. IF #3.12 assertion fails:
   13.1 `$manual_msg` = RENDER "`$$plan_path` 仍有未回答問題，請人工檢查"
   13.2 EMIT `$manual_msg` to user
   13.3 STOP
14. GOTO #4.1
15. `$revision_payload` = DERIVE clarify-loop batch payload with one question id `q-plan-revision`, kind `CON`, options 由 `$$resolved_plan` 已答題目枚舉 + `cancel`，recommendation 取最近一次有效題目 id，recommendation_rationale 引用 [`references/kickoff-plan-contract.md`](references/kickoff-plan-contract.md) §Question Record Fields
    15.1 [USER INTERACTION] `$revision` = DELEGATE `/clarify-loop` with `$revision_payload`
16. `$revised_plan` = RENDER `$$resolved_plan` with `$revision`
17. IF `$revision` invalidates earlier answers:
   17.1 `$revised_plan` = RENDER `$revised_plan` with affected question status=`unanswered`
18. WRITE `$$plan_path` ← `$revised_plan`
19. GOTO #3.1

### Phase 4 — EXECUTE artifact plan
> produces: `$$artifact_set`, `$$backend_subdir`, `$$backend_root`, `$$args_path`

0. BRANCH `$$non_interactive`
   true  → `$decisions` = DERIVE defaults `{stack: python_e2e, test_strategy: e2e, project_spec_language: zh-hant, tlb_id: backend, boundary_role: backend, boundary_type: web-service, backend_subdir: ""}` (non-interactive 預設走 python_e2e；要在 headless 模式跑 java_e2e，caller payload 必須帶 `stack: java_e2e`)
       0.1 GOTO #4.4
   false → GOTO #4.1
1. `$execution_plan` = READ `$$plan_path`
2. `$decisions` = PARSE Resolved Decisions from `$execution_plan`
3. `$artifact_plan` = PARSE Artifact Plan from `$execution_plan`
4. `$$backend_subdir` = DERIVE `$decisions.backend_subdir` (default `""` if absent)
5. `$$backend_root` = COMPUTE `${$$project_root}` if `$$backend_subdir` is empty else `${$$project_root}/${$$backend_subdir}`
6. `$$args_path` = COMPUTE `${$$backend_root}/.aibdd/arguments.yml`
7. IF `$$backend_subdir` is non-empty:
   7.1 CREATE `$$backend_root`
   7.2 IF CREATE fails:
       7.2.1 `$backend_root_msg` = RENDER permission or parent-directory error for `$$backend_root`
       7.2.2 EMIT `$backend_root_msg` to user
       7.2.3 STOP
   END IF
8. CREATE `${$$backend_root}/.aibdd/`
   8.1 IF CREATE fails:
       8.1.1 `$config_create_msg` = RENDER permission or parent-directory error for `${$$backend_root}/.aibdd/`
       8.1.2 EMIT `$config_create_msg` to user
       8.1.3 STOP
8.2 CREATE `${$$backend_root}/specs/`
   8.2.1 IF CREATE fails:
       8.2.1.1 `$specs_create_msg` = RENDER permission or parent-directory error for `${$$backend_root}/specs/`
       8.2.1.2 EMIT `$specs_create_msg` to user
       8.2.1.3 STOP
9. CREATE `${$$backend_root}/specs/architecture/`
   9.1 IF CREATE fails:
       9.1.1 `$arch_create_msg` = RENDER permission or parent-directory error for `${$$backend_root}/specs/architecture/`
       9.1.2 EMIT `$arch_create_msg` to user
       9.1.3 STOP
10. BRANCH `$decisions.stack`
    python_e2e → GOTO #4.10.A
    java_e2e   → GOTO #4.10.B
    other      → GOTO #4.10.X
    10.A `$args_template` = READ [`assets/templates/arguments.template.yml`](assets/templates/arguments.template.yml)
        10.A.1 `$yaml` = RENDER `$args_template` substituting `{{TLB_ID}} := $decisions.tlb_id`, `{{PROJECT_SPEC_LANGUAGE}} := $decisions.project_spec_language`, `{{BACKEND_SUBDIR}} := $$backend_subdir`
        10.A.2 GOTO #4.11
    10.B `$args_template` = READ [`assets/templates/arguments.template.java-e2e.yml`](assets/templates/arguments.template.java-e2e.yml)
        10.B.1 `$java_artifact_id` = COMPUTE `$decisions.tlb_id` (kebab-case 直接作為 Maven artifactId)
        10.B.2 `$java_group_id` = DERIVE `$decisions.group_id` if present else `com.example`
        10.B.3 `$java_base_package` = DERIVE `$decisions.base_package` if present else `${$java_group_id}.<artifact_id with hyphens removed>` (例：`course-api` → `com.example.courseapi`)
        10.B.4 `$java_db_name` = DERIVE `$decisions.db_name` if present else `$java_artifact_id`
        10.B.5 `$yaml` = RENDER `$args_template` substituting `{{PROJECT_SPEC_LANGUAGE}} := $decisions.project_spec_language`, `{{BACKEND_SUBDIR}} := $$backend_subdir`, `{{GROUP_ID}} := $java_group_id`, `{{ARTIFACT_ID}} := $java_artifact_id`, `{{BASE_PACKAGE}} := $java_base_package`, `{{JAVA_VERSION}} := 25`, `{{SPRING_BOOT_VERSION}} := 4.0.6`, `{{CUCUMBER_VERSION}} := 7.34.3`, `{{JJWT_VERSION}} := 0.12.6`, `{{POSTGRES_IMAGE_VERSION}} := 18`, `{{DB_NAME}} := $java_db_name`
        10.B.6 GOTO #4.11
    10.C `$args_template` = READ [`assets/templates/arguments.template.nextjs-playwright.yml`](assets/templates/arguments.template.nextjs-playwright.yml)
        10.C.1 `$frontend_subdir` = COMPUTE `$decisions.frontend_subdir` (default `""` if absent; mirrors `BACKEND_SUBDIR` semantics)
        10.C.2 `$project_slug` = COMPUTE `$decisions.tlb_id` (TLB id 同時作為 `PROJECT_SLUG` for `${PROJECT_SLUG}-sb-mcp` MCP tools)
        10.C.3 `$yaml` = RENDER `$args_template` substituting `{{PROJECT_SPEC_LANGUAGE}} := $decisions.project_spec_language`, `{{FRONTEND_SUBDIR}} := $frontend_subdir`, `{{PROJECT_SLUG}} := $project_slug`
        10.C.4 GOTO #4.11
    10.X `$stack_msg` = RENDER "未知 stack `${$decisions.stack}`；只支援 `python_e2e`、`java_e2e`、`nextjs_playwright`"
        10.X.1 EMIT `$stack_msg` to user
        10.X.2 STOP
11. `$boundary_template` = READ [`assets/templates/boundary.template.yml`](assets/templates/boundary.template.yml)
    11.1 `$boundary_doc` = RENDER `$boundary_template` substituting `{{TLB_ID}} := $decisions.tlb_id`
12. `$diagram_template` = READ [`assets/templates/component-diagram.class.template.mmd`](assets/templates/component-diagram.class.template.mmd)
    12.1 `$diagram_doc` = RENDER `$diagram_template` substituting `{{TLB_ID}} := $decisions.tlb_id` — output path MUST obey `aibdd-core::diagram-file-naming.md`
13. `$folder_plan` = DERIVE boundary truth folder skeleton from `$decisions` per the stack-specific packing reference (`python_e2e` → [`references/python-backend-packing.md`](references/python-backend-packing.md), `java_e2e` → [`references/java-backend-packing.md`](references/java-backend-packing.md), `nextjs_playwright` → [`references/nextjs-frontend-packing.md`](references/nextjs-frontend-packing.md)) §Boundary Folder Skeleton — MUST be exactly `[specs/${tlb_id}/contracts, specs/${tlb_id}/data, specs/${tlb_id}/shared, specs/${tlb_id}/packages]` (relative to `$$backend_root`)；boundary truth skeleton 與 stack 無關，因此三個 packing 檔對此節的規範一致
14. `$placeholder_file_plan` = DERIVE placeholder files:
    - `${TRUTH_BOUNDARY_ROOT}/shared/dsl.yml`
    - `${TRUTH_BOUNDARY_ROOT}/test-strategy.yml`
    - `${TRUTH_BOUNDARY_ROOT}/contracts/.gitkeep`
    - `${TRUTH_BOUNDARY_ROOT}/data/.gitkeep`
    - `${TRUTH_BOUNDARY_ROOT}/packages/.gitkeep`
    （不得宣告 package-level `dsl.yml`／`dsl.md`；不得宣告 boundary root `actors/`、`features/`、`coverage/`、`entities/`、`step-defs/`、`sub-boundaries/`）
15. ASSERT `$folder_plan` root equals `specs/${$decisions.tlb_id}` relative to `$$backend_root`
16. ASSERT no path in `$folder_plan` contains `${$decisions.tlb_id}/${$decisions.tlb_id}` or `${$decisions.tlb_id}/${$decisions.boundary_type}`
17. ASSERT no path in `$folder_plan` contains boundary root `actors/`, boundary root `features/`, `coverage/`, `entities/`, `step-defs/`, or `sub-boundaries/`
18. WRITE `$$args_path` ← `$yaml`
    18.1 IF WRITE fails:
        18.1.1 DELETE `$$args_path`
        18.1.2 `$args_write_msg` = RENDER path and error summary for `$$args_path`
        18.1.3 EMIT `$args_write_msg` to user
        18.1.4 STOP
19. WRITE `${$$backend_root}/specs/architecture/boundary.yml` ← `$boundary_doc`
    19.1 IF WRITE fails:
        19.1.1 DELETE `${$$backend_root}/specs/architecture/boundary.yml`
        19.1.2 `$boundary_write_msg` = RENDER path and error summary for `boundary.yml`
        19.1.3 EMIT `$boundary_write_msg` to user
        19.1.4 STOP
20. WRITE `${$$backend_root}/specs/architecture/component-diagram.class.mmd` ← `$diagram_doc`
    20.1 IF WRITE fails:
        20.1.1 DELETE `${$$backend_root}/specs/architecture/component-diagram.class.mmd`
        20.1.2 `$diagram_write_msg` = RENDER path and error summary for `component-diagram.class.mmd`
        20.1.3 EMIT `$diagram_write_msg` to user
        20.1.4 STOP
21. LOOP per `$folder` in `$folder_plan`
   21.1 CREATE `$folder`
   END LOOP
22. LOOP per `$placeholder_file` in `$placeholder_file_plan`
   22.1 `$basename` = COMPUTE basename of `$placeholder_file`
   22.2 BRANCH `$basename`
       `dsl.yml`           → `$ph_body` = READ [`assets/templates/shared-dsl.placeholder.yml`](assets/templates/shared-dsl.placeholder.yml)
       `test-strategy.yml` → `$ph_body` = READ [`assets/templates/test-strategy.placeholder.yml`](assets/templates/test-strategy.placeholder.yml)
       `.gitkeep`          → `$ph_body` = COMPUTE literal string `"# keep\n"`
   22.3 WRITE `$placeholder_file` ← `$ph_body`
   END LOOP
22.4 `$root_seed_gitkeep` = COMPUTE `${$$project_root}/.gitkeep`
22.5 IF path_exists(`$root_seed_gitkeep`):
     22.5.1 DELETE `$root_seed_gitkeep`
     END IF
23. `$$artifact_set` = DERIVE written paths for `arguments.yml`, `boundary.yml`, `component-diagram.class.mmd`, `$folder_plan`, and `$placeholder_file_plan`
24. BRANCH `$$non_interactive`
    true  → GOTO #4.26
    false → GOTO #4.25
25. `$logged_plan` = RENDER `$execution_plan` with execution log for `$$artifact_set`
    25.1 WRITE `$$plan_path` ← `$logged_plan`
26. ASSERT every path in `$$artifact_set` exists
    26.1 IF assertion fails:
        26.1.1 `$verify_msg` = RENDER verification failure summary for `$$artifact_set`
        26.1.2 EMIT `$verify_msg` to user
        26.1.3 STOP

### Phase 5 — CONFIRM and cleanup

1. BRANCH `$$non_interactive`
   true  → GOTO #5.14
   false → GOTO #5.2
2. `$final_message` = DRAFT plain-text final confirmation context from `$$artifact_set` and `$$plan_path`
3. `$final_payload` = DERIVE clarify-loop batch payload with one question id `q-final-confirm`, kind `CON`, context = `$final_message`, options `confirm | revise_plan | show_plan`, recommendation `confirm`, recommendation_rationale 引用 [`references/kickoff-plan-contract.md`](references/kickoff-plan-contract.md) §Final Confirmation Replies
4. [USER INTERACTION] `$final_reply` = DELEGATE `/clarify-loop` with `$final_payload`
5. `$final_decision` = CLASSIFY `$final_reply` as `confirm | revise_plan | show_plan`
6. BRANCH `$final_decision`
   confirm     → GOTO #5.7
   revise_plan → GOTO #3.5
   show_plan   → GOTO #5.12
7. `$confirmed_plan` = RENDER latest `KICKOFF_PLAN.md` with status=`confirmed`
8. WRITE `$$plan_path` ← `$confirmed_plan`
9. DELETE `$$plan_path`
   9.1 IF DELETE fails:
       9.1.1 `$cleanup_msg` = RENDER manual cleanup path for `$$plan_path`
       9.1.2 EMIT `$cleanup_msg` to user
10. `$summary` = DRAFT completion message using [`references/question-catalog.md`](references/question-catalog.md) §完成訊息模板 and `$$artifact_set`
11. EMIT `$summary` to user
    11.1 IF EMIT fails:
        11.1.1 WRITE `${$$project_root}/specs/.kickoff-report.md` ← `$summary`
    11.2 STOP
12. EMIT `$$plan_path` to user
13. GOTO #5.2
14. `$summary` = DRAFT completion message using [`references/question-catalog.md`](references/question-catalog.md) §完成訊息模板 and `$$artifact_set`
15. EMIT `$summary` to user
16. STOP

## §3 CROSS-REFERENCES

- `/clarify-loop` — 可被此 skill 的互動步驟採用為一次一題的選項式問答外殼。
