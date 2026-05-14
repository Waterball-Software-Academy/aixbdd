---
name: aibdd-plan
description: Technical planning orchestrator for the new AIBDD packing model. Reads Discovery truth, updates owner-scoped boundary truth, plans external/internal implementation, synthesizes local/shared DSL truth, and hands off exact inputs to /aibdd-spec-by-example-analyze. DSL physical mapping is handled as an internal reasoning phase.
metadata:
  user-invocable: true
  source: project-level dogfooding
  skill-type: planner
---

# aibdd-plan

Plan technical boundary truth and red-usable DSL mappings from accepted Discovery artifacts without creating shadow truth.

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
  - path: references/role-and-contract.md
    purpose: Role, inputs, outputs, explicit non-goals, and completion contract.
  - path: references/path-contract.md
    purpose: arguments.yml keys, resolved paths, fallback rules, and no-overload path contract.
  - path: references/truth-ownership.md
    purpose: Owner-scoped truth writes and no-shadow-truth rules.
  - path: references/technical-truth-rules.md
    purpose: Boundary map, provider contract, data/state, and test strategy rules.
  - path: references/implementation-planning-rules.md
    purpose: Sequence diagram and internal structure planning rules.
  - path: references/dsl-output-contract.md
    purpose: DSL L1-L4, bindings, external stub, fixture upload, and red-usability contract.
  - path: references/impacted-feature-files-contract.md
    purpose: Defines how plan.md records the current plan package's impacted feature files for downstream task planning.
  - path: references/forbidden-mutations.md
    purpose: Artifacts and responsibilities this skill must not mutate.
  - path: references/quality-gate-contract.md
    purpose: Self-contained semantic quality gate rubric and verdict shape.
  - path: references/backend-preset-contract.md
    purpose: 本 skill 對 web-backend boundary 的 preset 使用契約（指向 aibdd-core SSOT）。
  - path: references/frontend-preset-contract.md
    purpose: 本 skill 對 web-frontend boundary 的 preset 使用契約（指向 aibdd-core SSOT）。
  - path: references/sentence-parts-framework.md
    purpose: Legacy tombstone — sentence-parts SSOT 已搬到 aibdd-core/assets/boundaries/web-backend/handler-routing.yml；保留以避免重新發明。
  - path: assets/templates/plan-md.template.md
    purpose: Plan package technical plan template.
  - path: assets/templates/research-md.template.md
    purpose: Planning research and trade-off record template.
  - path: assets/templates/dsl-entry.template.yml
    purpose: DSL entry skeleton used when rendering local/shared DSL truth.
  - path: ../aibdd-reconcile/references/planner-handoff-contract.md
    purpose: Optional reconcile caller payload schema for `plan.md` narrative injection.
  - path: aibdd-core::spec-package-paths.md
    purpose: Boundary-aware plan/truth path semantics and argument keys.
  - path: aibdd-core::physical-first-principle.md
    purpose: Physical mapping discipline for DSL L4 surfaces.
  - path: aibdd-core::preset-contract/web-backend.md
    purpose: Preset rule instance；物理 routing SSOT：aibdd-core/assets/boundaries/web-backend/handler-routing.yml。
  - path: aibdd-core::preset-contract/web-frontend.md
    purpose: Preset rule instance；物理 routing SSOT：aibdd-core/assets/boundaries/web-frontend/handler-routing.yml。
  - path: aibdd-core::diagram-file-naming.md
    purpose: Mermaid compound extensions for sequence/class diagram filenames.
  - path: aibdd-core::boundary-profile-contract.md
    purpose: Boundary type profile, state specifier, and operation contract specifier dispatch.
```

| ID | Path | Phase scope | Purpose |
|---|---|---|---|
| R1 | `aibdd-core::spec-package-paths.md` | global | Boundary-aware plan/truth path semantics and argument keys. |
| R2 | `aibdd-core::physical-first-principle.md` | Phase 6 | Physical mapping discipline for DSL L4 surfaces. |
| R3 | `references/role-and-contract.md` | global | Role, inputs, outputs, explicit non-goals, and completion contract. |
| R4 | `references/path-contract.md` | Phase 1 | `arguments.yml` keys, resolved paths, fallback rules, and no-overload path contract. |
| R5 | `references/truth-ownership.md` | Phase 3 + Phase 6 | Owner-scoped truth writes and no-shadow-truth rules. |
| R6 | `references/technical-truth-rules.md` | Phase 3 + Phase 4 | Boundary map, provider contract, data/state, and test strategy rules. |
| R7 | `references/implementation-planning-rules.md` | Phase 5 | Sequence diagram and internal structure planning rules. |
| R8 | `references/dsl-output-contract.md` | Phase 6 + Phase 7 | DSL L1-L4, bindings, external stub, fixture upload, and red-usability contract. |
| R9 | `references/impacted-feature-files-contract.md` | Phase 3 + Phase 8 | Defines how plan.md records the current plan package's impacted feature files for downstream task planning. |
| R10 | `aibdd-core::preset-contract/web-backend.md` | Phase 6 | Preset rule instance；物理 routing SSOT：`aibdd-core/assets/boundaries/web-backend/handler-routing.yml`。 |
| R10F | `aibdd-core::preset-contract/web-frontend.md` | Phase 6 | Preset rule instance（frontend 對偶）；物理 routing SSOT：`aibdd-core/assets/boundaries/web-frontend/handler-routing.yml`。 |
| R11 | `references/forbidden-mutations.md` | global | Artifacts and responsibilities this skill must not mutate. |
| R12 | `references/quality-gate-contract.md` | Phase 7 | Self-contained semantic quality gate rubric and verdict shape. |
| R13 | `assets/templates/plan-md.template.md` | Phase 3 + Phase 8 | Plan package technical plan template. |
| R14 | `assets/templates/research-md.template.md` | Phase 3 + Phase 8 | Planning research and trade-off record template. |
| R15 | `assets/templates/dsl-entry.template.yml` | Phase 6 | DSL entry skeleton used when rendering local/shared DSL truth. |
| R16 | `aibdd-core::diagram-file-naming.md` | Phase 5 | Mermaid compound extensions for sequence/class diagram filenames. |
| R17 | `aibdd-core::boundary-profile-contract.md` | Phase 2 + Phase 3 | Boundary type profile, state specifier, operation contract specifier, and component contract specifier dispatch. |
| R17S | `.claude/skills/aibdd-form-story-spec/references/role-and-contract.md` | Phase 3 (step 15.5) | Caller payload schema for `/aibdd-form-story-spec` DELEGATE — **caller-driven pipeline 專用**（`design_source.kind == "none"`）。當 boundary 有 `design.pen` 時改走 R21（producer 一條龍），不再走 form-story-spec。 |
| R20  | `reasoning/aibdd-plan/07-component-design-merge.md` | Phase 3 (step 15.3) | Component design × spec merge reasoning artifact；用於 caller-driven 路徑（無 `.pen`），把 features × activities × uiux-prompt 合成 `$$boundary_delta.components`。`.pen` 路徑下 producer skill 直接寫檔，不經此 reasoning。 |
| R21  | `.claude/skills/aibdd-pen-to-storybook/references/role-and-contract.md` | Phase 3 (step 15.3) | **Producer skill** payload schema — 當 boundary 有 `design.pen` 時，step 15.3.5 直接 DELEGATE 一條龍寫出 `<id>.tsx` + `<id>.stories.tsx`；payload 含 `pen_path` / `screen_id` / `target_dir` / `mode`。 |
| R18 | `.claude/skills/aibdd-core/assets/boundaries/web-backend/handler-routing.yml` | Phase 6 | Boundary preset routing SSOT（routes keyword → sentence_part/handler，`handlers.*` L4 binding 要求）；DSL 合成前必讀。 |
| R18F | `.claude/skills/aibdd-core/assets/boundaries/web-frontend/handler-routing.yml` | Phase 6 | Boundary preset routing SSOT（frontend 對偶；含 4 條 boundary-level invariants I1–I4）；DSL 合成前必讀。 |
| R19 | `.claude/skills/aibdd-reconcile/references/planner-handoff-contract.md` | Phase 1 + Phase 3 | Optional reconcile caller payload schema for `plan.md` narrative injection. |

## §2 SOP

### Phase 1 — BIND planning context
> produces: `$$skill_dir`, `$$workspace_root`, `$$args_path`, `$$args`, `$$paths`, `$$current_plan_package`, `$$truth_function_package`, `$$reconcile_context`

1. `$$skill_dir` = COMPUTE current skill directory path
2. `$$workspace_root` = COMPUTE current workspace directory path
3. `$caller_payload` = READ caller payload if provided
4. `$$args_path` = DERIVE absolute arguments path from `$caller_payload.arguments_path` else `${$$workspace_root}/.aibdd/arguments.yml`
5. `$args_exists` = MATCH path_exists(`$$args_path`)
6. BRANCH `$args_exists` ? GOTO #1.7 : GOTO #1.6.1
   6.1 `$missing_args_msg` = RENDER "`.aibdd/arguments.yml` 不存在；請先完成 /aibdd-kickoff"
   6.2 EMIT `$missing_args_msg` to user
   6.3 STOP
7. `$args_text` = READ `$$args_path`
8. `$$args` = PARSE `$args_text`, schema=`yaml`
   8.1 `$$reconcile_context` = PARSE optional reconcile payload from `$caller_payload` per [`.claude/skills/aibdd-reconcile/references/planner-handoff-contract.md`](.claude/skills/aibdd-reconcile/references/planner-handoff-contract.md) else empty map
   8.2 IF `$$reconcile_context` is non-empty:
       8.2.1 ASSERT `$$reconcile_context` contains `session_id`, `earliest_planner`, `cascade_chain`, `archive_path`
       8.2.2 IF assertion fails:
           8.2.2.1 EMIT "reconcile payload 缺必要欄位；拒絕寫入不完整的 reconcile 敘事" to user
           8.2.2.2 STOP
9. ASSERT `$$args` includes `SPECS_ROOT_DIR`, `PLAN_SPEC`, `PLAN_REPORTS_DIR`, `TRUTH_BOUNDARY_ROOT`, `TRUTH_BOUNDARY_PACKAGES_DIR`, `BOUNDARY_PACKAGE_DSL`, `BOUNDARY_SHARED_DSL`, `TEST_STRATEGY_FILE`
   9.1 IF assertion fails:
       9.1.1 `$args_msg` = RENDER missing key list and "回到 /aibdd-kickoff 或 /aibdd-discovery 綁定路徑"
       9.1.2 EMIT `$args_msg` to user
       9.1.3 STOP
10. `$$paths` = TRIGGER `python3 "${$$skill_dir}/scripts/python/resolve_plan_paths.py" "${$$args_path}"`
11. `$paths_ok` = MATCH `$$paths.exit_code == 0`
12. BRANCH `$paths_ok` ? GOTO #1.13 : GOTO #1.12.1
    12.1 `$paths_msg` = RENDER path resolver stderr/stdout summary
    12.2 EMIT `$paths_msg` to user
    12.3 STOP
13. `$$current_plan_package` = PARSE `$$paths.stdout.current_plan_package`
14. `$$truth_function_package` = PARSE `$$paths.stdout.truth_function_package`
15. `$function_package_bound` = MATCH `$$truth_function_package` is non-empty and path_exists(parent(`$$truth_function_package`))
16. BRANCH `$function_package_bound` ? GOTO #2.1 : GOTO #1.16.1
    16.1 `$bind_msg` = RENDER "TRUTH_FUNCTION_PACKAGE 尚未綁定；請先由 /aibdd-discovery 綁定功能模組 package"
    16.2 EMIT `$bind_msg` to user
    16.3 STOP

### Phase 2 — LOAD discovery, profile, and truth inputs
> produces: `$$plan_spec`, `$$discovery_report`, `$$activity_truth`, `$$feature_truth`, `$$boundary_profile`, `$$truth_bundle`, `$$code_skeleton`

1. `$$plan_spec` = READ `${PLAN_SPEC}`
2. ASSERT `$$plan_spec` exists and includes `Discovery Sourcing Summary`
   2.1 IF assertion fails:
       2.1.1 `$spec_msg` = RENDER "PLAN_SPEC 缺 Discovery Sourcing Summary；請先完成 /aibdd-discovery"
       2.1.2 EMIT `$spec_msg` to user
       2.1.3 STOP
3. `$$discovery_report` = READ `${PLAN_REPORTS_DIR}/discovery-sourcing.md`
4. ASSERT `$$discovery_report` exists
5. `$activities_dir` = DERIVE activities directory from `$$paths.stdout.activities_dir` or `${$$truth_function_package}/activities`
6. `$features_dir` = DERIVE features directory from `$$paths.stdout.features_dir` or `${$$truth_function_package}/features`
7. `$$activity_truth` = READ all `*.activity` under `$activities_dir`
8. `$$feature_truth` = READ all `*.feature` under `$features_dir`
9. ASSERT `$$activity_truth` non-empty
10. ASSERT `$$feature_truth` non-empty
11. `$boundary_yml` = READ `${BOUNDARY_YML}` from `$$args`
12. `$boundary_type` = PARSE target boundary `type` from `$boundary_yml`
13. `$$boundary_profile` = READ `aibdd-core::boundary-type-profiles/${$boundary_type}.profile.yml`
14. ASSERT `$$boundary_profile` satisfies `aibdd-core::boundary-profile-contract.md`
15. `$boundary_map` = READ `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml` if exists else empty skeleton
16. `$contracts` = READ `${TRUTH_BOUNDARY_ROOT}/contracts/` if exists else empty bundle
17. `$data_truth` = READ `${TRUTH_BOUNDARY_ROOT}/data/` if exists else empty bundle
18. `$shared_dsl` = READ `${BOUNDARY_SHARED_DSL}` if exists else empty DSL registry
19. `$local_dsl` = READ `${BOUNDARY_PACKAGE_DSL}` if exists else empty DSL registry
20. `$test_strategy` = READ `${TEST_STRATEGY_FILE}` if exists else empty strategy
21. `$$truth_bundle` = DERIVE bundle from `$boundary_map`, `$contracts`, `$data_truth`, `$shared_dsl`, `$local_dsl`, `$test_strategy`, `$$boundary_profile`
22. `$$code_skeleton` = DERIVE code skeleton index from project files, excluding ignored directories and non-primary worktrees
23. ASSERT no input path points to plan package when truth path is required

### Phase 3 — PLAN technical boundary truth
> produces: `$$boundary_delta` (incl. `components` for frontend boundaries), `$$contract_delta`, `$$data_delta`, `$$strategy_delta`, `$$impacted_feature_files`, `$$plan_doc`, `$$research_doc`

1. `$truth_rules` = PARSE [`references/technical-truth-rules.md`](references/technical-truth-rules.md)
2. `$ownership` = PARSE [`references/truth-ownership.md`](references/truth-ownership.md)
3. `$$boundary_delta` = THINK per [`reasoning/aibdd-plan/02-technical-boundary-dispatch.md`](reasoning/aibdd-plan/02-technical-boundary-dispatch.md), input=`$$plan_spec`, `$$discovery_report`, `$$activity_truth`, `$$feature_truth`, `$$truth_bundle`, `$truth_rules`, `$ownership`
4. `$$contract_delta` = THINK per [`reasoning/aibdd-plan/03-external-boundary-surface.md`](reasoning/aibdd-plan/03-external-boundary-surface.md), input=`$$boundary_delta`, `$$truth_bundle`, `$$boundary_profile`, `$$code_skeleton`, `$truth_rules`
5. `$$data_delta` = THINK per [`reasoning/aibdd-plan/02-technical-boundary-dispatch.md`](reasoning/aibdd-plan/02-technical-boundary-dispatch.md), focus=`data-state-persistence`, input=`$$boundary_delta`, `$$contract_delta`, `$$truth_bundle`, `$$boundary_profile`, `$truth_rules`
6. `$$strategy_delta` = THINK per [`reasoning/aibdd-plan/03-external-boundary-surface.md`](reasoning/aibdd-plan/03-external-boundary-surface.md), focus=`test-double-policy`, input=`$$boundary_delta`, `$$contract_delta`, `$$truth_bundle`, `$truth_rules`
7. `$$impacted_feature_files` = THINK per [`references/impacted-feature-files-contract.md`](references/impacted-feature-files-contract.md), input=`$$plan_spec`, `$$feature_truth`, `$$boundary_delta`, `$$contract_delta`, `$$truth_bundle`
8. ASSERT `$$boundary_delta` maps every impacted atomic rule exactly once
9. ASSERT every path in `$$impacted_feature_files` resolves under `${FEATURE_SPECS_DIR}`
10. ASSERT `$$contract_delta` targets only `${TRUTH_BOUNDARY_ROOT}/contracts/` and matches `$$boundary_profile.operation_contract_specifier`
11. ASSERT `$$data_delta` targets only `${TRUTH_BOUNDARY_ROOT}/data/` and matches `$$boundary_profile.state_specifier`
12. ASSERT `$$strategy_delta` writes only `${TEST_STRATEGY_FILE}`
13. WRITE `${TRUTH_BOUNDARY_ROOT}/boundary-map.yml` ← rendered boundary map from `$$boundary_delta`
14. BRANCH `$$boundary_profile.operation_contract_specifier.skill`
    `/aibdd-form-api-spec` → DELEGATE `/aibdd-form-api-spec` with `slice_list` from `$$contract_delta` and target paths under `${TRUTH_BOUNDARY_ROOT}/contracts/`
    empty/none             → ASSERT `$$contract_delta.contracts` empty
    other                  → STOP with unsupported operation contract specifier message
15. BRANCH `$$boundary_profile.state_specifier.skill`
    `/aibdd-form-entity-spec` → DELEGATE `/aibdd-form-entity-spec` with entity/state reasoning from `$$data_delta` and target paths under `${TRUTH_BOUNDARY_ROOT}/data/`
    empty/none                → ASSERT `$$data_delta.files` empty
    other                     → STOP with unsupported state specifier message
15.3 BRANCH `$$boundary_profile.component_contract_specifier.skill` non-empty
    true  → GOTO #15.3.1   # frontend boundary：跑 design × spec merge，enrich `$$boundary_delta.components`
    false → GOTO #15.5     # backend boundary：跳過 component-design merge
   15.3.1 `$design_pen_path` = COMPUTE `${CURRENT_PLAN_PACKAGE}/design.pen`
   15.3.2 `$design_style_profile_path` = COMPUTE `${CURRENT_PLAN_PACKAGE}/design/style-profile.yml`
   15.3.3 `$design_uiux_prompt_path` = COMPUTE `${CURRENT_PLAN_PACKAGE}/design/uiux-prompt.md`
   15.3.4 `$design_source` = COMPUTE
       IF path_exists(`$design_pen_path`):
         `{ kind: "pen", path: $design_pen_path, screen_id: null, style_profile_path: ($design_style_profile_path if path_exists else null) }`
       ELSE:
         `{ kind: "none" }`
   15.3.5 BRANCH path_exists(`$design_pen_path`)
       true:   # design pipeline — producer skill 一條龍寫檔，跳過 form-story-spec
           15.3.5.1 `$components_root` = RENDER `${TRUTH_BOUNDARY_ROOT}/contracts/components/`
           15.3.5.2 `$producer_payload` = DRAFT `{
                      pen_path: $design_pen_path,
                      screen_id: null,
                      target_dir: $components_root,
                      mode: "create"
                    }`
                    # producer 寫雙檔（<id>.tsx + <id>.stories.tsx）到 target_dir/<id>/；mode=create 防誤覆寫
           15.3.5.3 `$producer_report` = DELEGATE `/aibdd-pen-to-storybook` with `$producer_payload`
           15.3.5.4 ASSERT `$producer_report.status == "completed"` AND `$producer_report.mode == "producer"`
           15.3.5.5 ASSERT count(`$producer_report.files_written`) == 2 * `$producer_report.component_count`
           15.3.5.6 `$$boundary_delta.components` = DERIVE informational summary from `$producer_report.component_table`
                    # 注意：design pipeline 下 boundary_delta.components 僅作為 plan.md 記錄；實際視覺檔已由 producer 寫出。
                    # 不再 DELEGATE form-story-spec（合約已由 producer 一次寫完）。
           15.3.5.7 GOTO #16   # 跳過 15.5 — design pipeline 已完成
       false:  # caller-driven pipeline — 走 reasoning/07 + form-story-spec
           15.3.5.8 `$design_adapter` = COMPUTE `{ component_table: { rows: [] }, tokens: [] }`
   15.3.6 BRANCH path_exists(`$design_uiux_prompt_path`)
       true:  `$uiux_prompt` = READ `$design_uiux_prompt_path`
       false: `$uiux_prompt` = COMPUTE empty
   15.3.7 `$$boundary_delta.components` = THINK per [`reasoning/aibdd-plan/07-component-design-merge.md`](reasoning/aibdd-plan/07-component-design-merge.md), input=`$$boundary_delta.components`, `$$activity_truth`, `$$feature_truth`, `$design_adapter`, `$uiux_prompt`
   15.3.8 ASSERT every entry in `$$boundary_delta.components` has `identifier`, `title`, `props` (list), `render_hints` (object with `root_element` + `children_layout`), and non-empty `stories[]` with `export_name`, `role`, `accessible_name`, `accessible_name_arg` per [`.claude/skills/aibdd-form-story-spec/references/role-and-contract.md`](.claude/skills/aibdd-form-story-spec/references/role-and-contract.md) §2
   15.3.9 IF reasoning/07 returns `cross_validation_warnings` non-empty: log warnings to plan.md research section（不 block）
15.5 BRANCH `$$boundary_profile.component_contract_specifier.skill`
    `/aibdd-form-story-spec` → GOTO #15.5.1
    `/aibdd-pen-to-storybook` → GOTO #15.5.5   # design pipeline 已在 15.3.5 處理；此處只 assert
    empty/none                → GOTO #15.5.5
    other                     → STOP with unsupported component contract specifier message
   15.5.1 `$story_jobs` = LOOP-COLLECT per `$component` in `$$boundary_delta.components`:
              `{ identifier:  $component.identifier,
                 target_dir:  RENDER ${TRUTH_BOUNDARY_ROOT}/contracts/components/${$component.identifier}/,
                 payload:     DERIVE form-story-spec caller payload from $component per
                              [`.claude/skills/aibdd-form-story-spec/references/role-and-contract.md`](.claude/skills/aibdd-form-story-spec/references/role-and-contract.md) §2 }`
              # 對齊 contract-as-SSOT 慣例：component .tsx 與 stories.tsx 都落到 boundary contracts/components/<id>/
              # tsconfig path alias `@/components/* → specs/<TLB>/contracts/components/*` 由 aibdd-auto-starter template 設定
              # payload 必含 component.props (list) + component.render_hints (object)；由 reasoning/07 enrich 進 `$$boundary_delta.components` 後直接取用
   15.5.2 `$story_batches` = COMPUTE partition(`$story_jobs`, 8)
              # ≤8 concurrent subagents per batch；超過自動切批序列 dispatch，避免一次 spawn 過多打到 rate limit
   15.5.3 `$story_reports` = COMPUTE []
   15.5.4 LOOP per `$batch` in `$story_batches` (budget: ≤ ceil(count(`$story_jobs`)/8) batches, exit: all batches drained 或 fail-fast STOP)
       15.5.4.1 `$batch_reports` = TRIGGER parallel Agent fan-out:
                spawn one Agent(subagent_type="general-purpose") per `$job` in `$batch` in a SINGLE message (multi tool-use);
                each subagent prompt:
                  "DELEGATE /aibdd-form-story-spec with
                     target_dir=${$job.target_dir},
                     mode=\"create\",
                     design_source={ kind: \"none\" },
                     reasoning.component_modeling=${$job.payload};
                   return JSON {identifier, status, files_written[]} on success
                   or {identifier, status: \"incomplete\", reason} on failure."
                # caller-driven pipeline 專用；form-story-spec 不再接受 design_source.kind == "pen"（design 路徑改走 producer 一條龍）
                # 主 context 只收每個 subagent 的 JSON report (~200 bytes)；component-level props 推導 / CSF3 渲染 全部留在 subagent
       15.5.4.2 `$story_reports` = COMPUTE `$story_reports` ++ `$batch_reports`
       15.5.4.3 LOOP per `$report` in `$batch_reports`
           15.5.4.3.1 IF `$report.status` ≠ "completed":
               15.5.4.3.1.1 EMIT "component modeling 推理包不完整：${$report.identifier} (${$report.reason})" to user
               15.5.4.3.1.2 STOP   # fail-fast：當前 batch 內任一 component 失敗即 STOP，不再 dispatch 下一 batch
           END LOOP
       END LOOP
   15.5.5 ASSERT `$$boundary_delta.components` is empty OR every entry is marked `deferred: true` OR design pipeline 已在 15.3.5 處理; on violation STOP with "component_contract_specifier mismatch with boundary_delta.components state"
16. WRITE `${TEST_STRATEGY_FILE}` ← rendered strategy from `$$strategy_delta`
17. `$plan_template` = READ [`assets/templates/plan-md.template.md`](assets/templates/plan-md.template.md)
18. `$research_template` = READ [`assets/templates/research-md.template.md`](assets/templates/research-md.template.md)
19. `$$plan_doc` = RENDER `$plan_template` with `$$boundary_delta`, `$$contract_delta`, `$$data_delta`, `$$strategy_delta`, `$$impacted_feature_files`, `$$reconcile_context`
20. `$$research_doc` = RENDER `$research_template` with planning decisions and trade-offs
21. WRITE `${CURRENT_PLAN_PACKAGE}/plan.md` ← `$$plan_doc`
22. WRITE `${CURRENT_PLAN_PACKAGE}/research.md` ← `$$research_doc`

### Phase 4 — PLAN external boundary surface
> produces: `$$external_surface_model`

1. `$external_rules` = PARSE [`references/technical-truth-rules.md`](references/technical-truth-rules.md) §External Boundary Surface
2. `$$external_surface_model` = THINK per [`reasoning/aibdd-plan/03-external-boundary-surface.md`](reasoning/aibdd-plan/03-external-boundary-surface.md), input=`$$boundary_delta`, `$$contract_delta`, `$$strategy_delta`, `$$truth_bundle`, `$external_rules`
3. ASSERT every provider boundary has contract reference or explicit non-contract reason
4. ASSERT every mockable consumer→provider edge has test double policy
5. ASSERT no edge marks same-boundary internal collaborator as mock target
6. IF `$$external_surface_model` includes 3rd-party providers:
   6.1 ASSERT each provider has external stub candidate for DSL Phase 6
   6.2 ASSERT each stub has payload and response binding source

### Phase 5 — PLAN internal implementation
> produces: `$$implementation_model`, `$$sequence_paths`, `$$internal_structure`

1. `$impl_rules` = PARSE [`references/implementation-planning-rules.md`](references/implementation-planning-rules.md)
2. CREATE `${CURRENT_PLAN_PACKAGE}/implementation`
3. CREATE `${CURRENT_PLAN_PACKAGE}/implementation/sequences`
4. `$$implementation_model` = THINK per [`reasoning/aibdd-plan/04-internal-implementation.md`](reasoning/aibdd-plan/04-internal-implementation.md), input=`$$activity_truth`, `$$feature_truth`, `$$boundary_delta`, `$$contract_delta`, `$$data_delta`, `$$external_surface_model`, `$$code_skeleton`, `$impl_rules`
5. LOOP per `$path` in `$$implementation_model.paths`
   5.1 `$sequence_doc` = RENDER [`assets/templates/sequence.template.mmd`](assets/templates/sequence.template.mmd) with `$path`
   5.2 WRITE `${CURRENT_PLAN_PACKAGE}/implementation/sequences/${$path.slug}.${$path.kind}.sequence.mmd` ← `$sequence_doc`
   END LOOP
6. `$$sequence_paths` = COMPUTE written sequence diagram paths
7. `$$internal_structure` = RENDER [`assets/templates/internal-structure.class.template.mmd`](assets/templates/internal-structure.class.template.mmd) with structural union of `$$implementation_model.paths`
8. WRITE `${CURRENT_PLAN_PACKAGE}/implementation/internal-structure.class.mmd` ← `$$internal_structure`
9. ASSERT each major happy/alternative/error path has implementation target or explicit blocked reason

### Phase 6 — SYNTHESIZE DSL truth
> produces: `$$dsl_delta`, `$$dsl_written_paths`, `$$dsl_quality_seed`, `$$dsl_key_locale`

1. `$locale_override` = READ `DSL_KEY_LOCALE` from `$$args` if present
2. BRANCH `$locale_override`
   `prefer_spec_language` → `$$dsl_key_locale` = COMPUTE `prefer_spec_language` GOTO #6.7
   `zh-hant`              → `$$dsl_key_locale` = COMPUTE `zh-hant` GOTO #6.7
   `zh-hans`              → `$$dsl_key_locale` = COMPUTE `zh-hans` GOTO #6.7
   `en-us`                → `$$dsl_key_locale` = COMPUTE `en-us` GOTO #6.7
   `ja-jp`                → `$$dsl_key_locale` = COMPUTE `ja-jp` GOTO #6.7
   `ko-kr`                → `$$dsl_key_locale` = COMPUTE `ko-kr` GOTO #6.7
   empty/invalid          → GOTO #6.3
3. `$lang_sources` = DERIVE up to 40 path basenames from `$features_dir`, `$activities_dir`, and `${PLAN_SPEC}` path (filenames only)
4. `$script_profile` = CLASSIFY `$lang_sources` as `latin-heavy | non_latin-heavy` via non-ASCII codepoint proportion heuristic on basenames（多數檔名為英文與數字 → `latin-heavy`）
5. BRANCH `$script_profile`
   latin-heavy     → `$$dsl_key_locale` = COMPUTE `en-us` GOTO #6.7
   non_latin-heavy → GOTO #6.6
6. `$dsl_key_payload` = DERIVE clarify-loop batch payload with one question id `q-dsl-key-locale`, kind `CON`, context = "規格檔案檔名以非英文為主。`{參數鍵}` 與 `param_bindings`／`assertion_bindings` 的鍵名要不要跟規格自然語言一致？（contracts／data／response 技術欄位鍵維持英文）", question = "DSL `{參數鍵}` 與 binding 鍵名要走規格語感還是維持英文？", options = `prefer_spec_language | en-us`（label 分別為「跟規格語感（允許中英混合：`旅程 ID`、`stage ID`）」與「維持英文鍵」）, recommendation = `prefer_spec_language`, recommendation_rationale = "規格檔名為主非英文時，DSL 鍵跟著規格語感讓 BDD 句型更貼近領域語言"
   6.0 [USER INTERACTION] `$dsl_key_reply` = DELEGATE `/clarify-loop` with `$dsl_key_payload`
   6.1 `$locale_choice` = CLASSIFY `$dsl_key_reply` as `prefer_spec_language | en-us`
   6.2 BRANCH `$locale_choice`
       prefer_spec_language → `$$dsl_key_locale` = COMPUTE `prefer_spec_language` GOTO #6.7
       en-us                → `$$dsl_key_locale` = COMPUTE `en-us` GOTO #6.7
7. `$dsl_contract` = PARSE `${DSL_OUTPUT_CONTRACT_REF}`
8. `$preset_kind` = COMPUTE `${PRESET_KIND}`（default `web-backend` when key missing — backward compat for existing backend projects）
   8.1 BRANCH `$preset_kind`
       web-backend  → `$preset_contract_path`  = COMPUTE `${BACKEND_PRESET_CONTRACT_REF}`
                      `$boundary_assets_dir`   = COMPUTE `aibdd-core/assets/boundaries/web-backend/`
                      `$default_variant`       = COMPUTE `python-e2e`
                      `$external_stub_handler` = COMPUTE `external-stub`
       web-frontend → `$preset_contract_path`  = COMPUTE `${FRONTEND_PRESET_CONTRACT_REF}`
                      `$boundary_assets_dir`   = COMPUTE `aibdd-core/assets/boundaries/web-frontend/`
                      `$default_variant`       = COMPUTE `nextjs-playwright`
                      `$external_stub_handler` = COMPUTE `api-stub`
       other        → EMIT "PRESET_KIND `${$preset_kind}` not supported by /aibdd-plan v1（supported: web-backend, web-frontend）" to user
                      STOP
   8.2 `$persistence_handler` = COMPUTE `$$boundary_profile.persistence_handler.handler_id` per [`aibdd-core::boundary-profile-contract.md`](aibdd-core::boundary-profile-contract.md) — value comes from the boundary profile (Phase 2 step 13), not from a per-preset hardcoded branch.
   8.3 `$persistence_state_ref_pattern` = COMPUTE `$$boundary_profile.persistence_handler.state_ref_pattern`
   8.4 `$persistence_coverage_gate` = COMPUTE `$$boundary_profile.persistence_handler.coverage_gate`
   8.5 `$persistence_ownership_required` = COMPUTE `$persistence_coverage_gate == "not-null-columns"`
   8.6 ASSERT `$persistence_handler` non-empty AND `$persistence_state_ref_pattern` non-empty AND `$persistence_coverage_gate ∈ {"not-null-columns", "deferred-v1", "none"}`
       8.6.1 IF assertion fails: EMIT "boundary profile missing or invalid persistence_handler — see aibdd-core/references/boundary-profile-contract.md" to user; STOP
9. `$preset_contract` = PARSE `$preset_contract_path`
   9.1 `$handler_routing_policy` = READ `${$boundary_assets_dir}/handler-routing.yml`（對齊 `L4.preset.name: ${$preset_kind}`；routes + handlers SSOT）
10. `$$dsl_delta` = THINK per [`reasoning/aibdd-plan/05-dsl-truth-synthesis.md`](reasoning/aibdd-plan/05-dsl-truth-synthesis.md), input=`$$activity_truth`, `$$feature_truth`, `$$boundary_delta`, `$$contract_delta`, `$$data_delta`, `$$strategy_delta`, `$$external_surface_model`, `$$implementation_model`, `$handler_routing_policy`, `$dsl_contract`, `$preset_contract`, `$$dsl_key_locale`
11. ASSERT every changed DSL entry has L1, L2, L3, L4
12. ASSERT every L1 placeholder has exactly one binding in exactly one of (`L4.param_bindings`, `L4.assertion_bindings`)
13. ASSERT every Then expected value has `L4.assertion_bindings`
14. ASSERT every operation required input is covered by exactly one of (`L4.param_bindings`, `L4.datatable_bindings`, `L4.default_bindings`) after transport-header exclusions
15. ASSERT operation-backed entries have <= 3 L1 sentence parameters and <= 6 datatable parameters after defaults
16. ASSERT every L4 binding target uses allowed source prefix: `contracts/`, `data/`, `response`, `fixture`, `stub_payload`, `literal`
17. ASSERT every `L4.default_bindings` item has target, value, atomic-rule reason, and override policy
18. ASSERT operation entries reference `${$preset_kind}` handler and variant, defaulting to `${$default_variant}`
19. ASSERT external dependency entries use `${$external_stub_handler}` surface kind and do not reference same-boundary internal collaborator
19.A IF `$persistence_ownership_required`:
     ASSERT every aggregate-root entity declared in `${TRUTH_BOUNDARY_ROOT}/data/` AND listed under `boundary-map.yml#persistence_ownership` has at least one DSL entry where `L4.preset.handler == ${$persistence_handler}` AND `L4.source_refs.data` 指向該 entity 的 primary table — **每個聚合根都必須有獨立的 persistence builder**；composite builder（單條 entry 同時 seed 多個 entity rows，例如 `student-assigned` 同時牽涉 student / journey / stage / assignment）**不豁免** base-entity builder 的獨立存在義務。Missing entity coverage 視為 plan-level gap，**禁止**寫弱 placeholder DSL，**禁止**讓下游 `/aibdd-spec-by-example-analyze` 自行用 CiC(GAP) bypass，必須在本 phase STOP。
     ELSE: # frontend boundary — persistence-ownership coverage gate is future work (see web-frontend preset README §"Future Expansion"); skip this assertion in v1.
    19.A.1 IF assertion fails:
        19.A.1.1 `$missing_builder_msg` = RENDER list of persistence_ownership entities lacking aggregate-given DSL builder
        19.A.1.2 EMIT `$missing_builder_msg` to user
        19.A.1.3 STOP
19.B IF `$persistence_ownership_required`:
     ASSERT every `L4.preset.handler == ${$persistence_handler}` DSL entry **100% 覆蓋**對應 DBML table 的 NOT-NULL 欄位集合：對每條 builder 從 `L4.source_refs.data` 解析出 `data/<file>.dbml#<table>`，把該 table 所有 `[not null]`（含 `[pk]`）欄位收成 `required_columns`；把 `param_bindings + datatable_bindings + default_bindings` 中 target 形如 `data/<file>.dbml#<table>.<column>` 的 column 收成 `bound_columns`；要求 `required_columns ⊆ bound_columns`，唯一豁免清單為 (a) `[pk, increment]` 自增欄位，(b) DBML 顯式宣告 `[default: ...]` 欄位。`created_at` / `updated_at` 等慣例 timestamp **沒有** DBML 預設就**不**自動豁免——若想豁免必須在 DBML 加 `[default: ...]` modifier。FK NOT-NULL 欄位（譬如 `responses.assignment_id`、`appointments.assignment_id`、`retention_letters.assignment_id`、`responses.stage_id`）**不得**用 lookup-chain 推論豁免——builder 必須有直接 binding。違反屬於 plan-level gap，**禁止**寫弱 placeholder DSL，必須 STOP。
     ELSE: # frontend boundary — Zod-schema-based mock-state coverage gate is future work; skip this assertion in v1.
    19.B.1 IF assertion fails:
        19.B.1.1 `$missing_columns_msg` = RENDER per-builder list of unbound NOT-NULL columns（含 table、column、type、reason "missing param/datatable/default binding"）
        19.B.1.2 EMIT `$missing_columns_msg` to user
        19.B.1.3 STOP
20. IF any contract indicates file upload:
    20.1 ASSERT DSL includes fixture catalog/path, loader or wrapper, upload invocation, response verifier, state or file-store verifier, and missing-file behavior
21. `$local_entries` = DERIVE entries scoped to `${BOUNDARY_PACKAGE_DSL}` from `$$dsl_delta`
22. `$shared_entries` = DERIVE entries scoped to `${BOUNDARY_SHARED_DSL}` from `$$dsl_delta`
22.1 `$shared_template_entries` = DERIVE missing canonical shared entries from `${$boundary_assets_dir}/shared-dsl-template.yml`, resolving `<backend-variant-id>` / `<frontend-variant-id>` to `${$default_variant}`, when `${BOUNDARY_SHARED_DSL}` lacks the boundary's canonical shared entries (web-backend: success/failure + time-control; web-frontend: route-given + viewport-control + success/failure + time-control)
22.2 `$shared_entries` = UNION `$shared_entries`, `$shared_template_entries`
23. IF `$local_entries` non-empty:
    23.1 WRITE `${BOUNDARY_PACKAGE_DSL}` ← merged local DSL registry
24. IF `$shared_entries` non-empty:
    24.1 WRITE `${BOUNDARY_SHARED_DSL}` ← merged shared DSL registry
25. IF `$local_entries` empty and `$shared_entries` empty:
    25.1 ASSERT `$$dsl_delta.no_op_reason` is non-empty
26. `$$dsl_written_paths` = COMPUTE changed DSL paths
27. `$$dsl_quality_seed` = DERIVE quality input for Phase 7 from `$$dsl_delta`, `$$dsl_written_paths`

### Phase 7 — ASSERT quality gates
> produces: `$$script_verdict`, `$$semantic_verdict`, `$$quality_verdict`

1. `$forbidden` = PARSE [`references/forbidden-mutations.md`](references/forbidden-mutations.md)
2. `$plan_phase_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_plan_phase.py" "${$$args_path}"`
3. `$impacted_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_impacted_feature_files.py" "${$$args_path}"`
4. `$ownership_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_truth_ownership.py" "${$$args_path}"`
5. `$dsl_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_dsl_entries.py" "${$$args_path}"`
6. `$routing_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_handler_routing_consistency.py" "${$boundary_assets_dir}/handler-routing.yml"`
7. BRANCH `$preset_kind`
   web-backend  → `$preset_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_backend_preset_refs.py" "${$boundary_assets_dir}/handler-routing.yml" "${BOUNDARY_PACKAGE_DSL}" "${BOUNDARY_SHARED_DSL}"`
   web-frontend → `$preset_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_frontend_preset_refs.py" "${$boundary_assets_dir}/handler-routing.yml" "${BOUNDARY_PACKAGE_DSL}" "${BOUNDARY_SHARED_DSL}"`  # script body deferred — fail-loud signals scaffolding incomplete
8. `$mock_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_external_mock_policy.py" "${TRUTH_BOUNDARY_ROOT}/boundary-map.yml" "${TEST_STRATEGY_FILE}" "${BOUNDARY_PACKAGE_DSL}" "${BOUNDARY_SHARED_DSL}"`
9. `$fixture_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_fixture_upload_mapping.py" "${TRUTH_BOUNDARY_ROOT}/contracts" "${BOUNDARY_PACKAGE_DSL}" "${BOUNDARY_SHARED_DSL}"`
10. `$sequence_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_sequence_diagrams.py" "${$$args_path}"`
11. `$shared_dsl_out` = TRIGGER `python3 "${$$skill_dir}/scripts/python/check_shared_dsl_template.py" "${$$args_path}"`
12. `$$script_verdict` = PARSE merged JSON of `$plan_phase_out`, `$impacted_out`, `$ownership_out`, `$dsl_out`, `$routing_out`, `$preset_out`, `$mock_out`, `$fixture_out`, `$sequence_out`, `$shared_dsl_out`
13. BRANCH `$$script_verdict.ok` ? GOTO #7.14 : GOTO #7.13.1
   13.1 `$script_fail_msg` = RENDER script violations with rule_id, file, message
   13.2 EMIT `$script_fail_msg` to user
   13.3 STOP
14. `$quality_contract` = PARSE [`references/quality-gate-contract.md`](references/quality-gate-contract.md)
15. `$$semantic_verdict` = JUDGE per `$quality_contract`, input=`SKILL.md`, `$$boundary_delta`, `$$contract_delta`, `$$data_delta`, `$$strategy_delta`, `$$implementation_model`, `$$dsl_delta`, `$$dsl_quality_seed`, `$$impacted_feature_files`
16. ASSERT `$$semantic_verdict.verdict != VETO`
    16.1 IF assertion fails:
        16.1.1 `$semantic_fail_msg` = RENDER semantic gate vetoes
        16.1.2 EMIT `$semantic_fail_msg` to user
        16.1.3 STOP
17. `$$quality_verdict` = DERIVE combined verdict from `$$script_verdict`, `$$semantic_verdict`
18. CREATE `${CURRENT_PLAN_PACKAGE}/reports`
19. WRITE `${CURRENT_PLAN_PACKAGE}/reports/aibdd-plan-quality.md` ← rendered quality summary including actual script verdict evidence

### Phase 8 — REPORT downstream handoff

1. `$handoff_graph` = THINK per [`reasoning/aibdd-plan/06-handoff-graph.md`](reasoning/aibdd-plan/06-handoff-graph.md), input=`$$plan_doc`, `$$research_doc`, `$$boundary_delta`, `$$contract_delta`, `$$data_delta`, `$$strategy_delta`, `$$implementation_model`, `$$dsl_delta`, `$$quality_verdict`
2. ASSERT `$handoff_graph` lists plan, research, impacted feature files, contracts, data/test strategy, local/shared DSL, sequence diagrams, internal structure, blocking gaps, and Git diff review focus
3. ASSERT `$handoff_graph` does not require `/aibdd-test-plan`
4. `$summary` = DRAFT user-facing summary from `$handoff_graph`
5. EMIT `$summary` to user
   5.1 IF EMIT fails:
       5.1.1 WRITE `${CURRENT_PLAN_PACKAGE}/reports/aibdd-plan-report.md` ← `$summary`
       5.1.2 STOP

### Phase 9 — HANDLE failure contracts

- IF Discovery artifacts are missing: STOP and instruct caller to run `/aibdd-discovery`.
- IF target function package is not bound: STOP and instruct caller to bind via `/aibdd-discovery`; do not invent a boundary id from the backend name.
- IF owner-scoped truth write would touch an artifact owned by another skill: STOP and report owner conflict.
- IF DSL output needs a contract/data/test-strategy item that is missing: STOP and report the exact planning gap; do not write a weak DSL placeholder.
- IF file upload contract is detected but fixture convention is absent: STOP and report fixture-testability gap.
- IF quality gate fails: do not weaken the rubric; return to the phase that produced the failing model.

### Phase 10 — REPORT cross references

- Upstream: `/aibdd-discovery` produces plan package summary, activities, rule-only features, actor truth, and function package binding.
- Internal responsibility: DSL physical mapping is implemented by Phase 6 in this skill.
- Downstream: `/aibdd-spec-by-example-analyze` consumes plan, truth DSL, contracts, implementation diagrams, and quality reports; `/aibdd-tasks` may optionally consume the plan package's impacted feature list and implementation diagrams.
- Explicitly out of scope: `/aibdd-test-plan`, `speckit-aibdd-test-plan`, `/aibdd-implement`, `/aibdd-red`, `/aibdd-green`, `/aibdd-refactor`.
