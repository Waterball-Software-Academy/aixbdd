---
name: aibdd-discovery-uiux
description: 從 sibling backend boundary 的 `.feature` + `.activity` + `contracts/openapi.yml` 推導 frontend TLB 的 userflow 視角 `.activity` + `.feature` skeleton — 取代 `/aibdd-discovery` 在 frontend TLB 場景。先依 arguments.yml 的 UIUX_BACKEND_BOUNDARY_ID 解析 BE truth；CLASSIFY 每個 BE operation 為 has-ui / no-ui（no-ui 寫進 GAP 報告不落 feature）；再為 has-ui operation 推導 UI verb binding + accessible-name anchor + 4 種驗證語意（locator / visual-state / route / API-binding）的 Rule preset；DELEGATE /aibdd-form-activity 與 /aibdd-form-feature-spec 落檔。TRIGGER when 使用者下 /aibdd-discovery-uiux、TLB.role=="frontend" 且 sibling BE 已具備 spec truth。SKIP when TLB 非 frontend、UIUX_BACKEND_BOUNDARY_ID 未設定、或 sibling BE artifacts 缺漏。
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-discovery-uiux

根規劃器（frontend variant）｜由 sibling backend boundary 的 spec truth 推導 frontend TLB 的 userflow 視角 `.activity` + `.feature` rule-only skeleton，是 `/aibdd-discovery` 在 frontend TLB 場景下的取代品。

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
  - path: references/backend-input-contract.md
    purpose: sibling BE artifacts 來源 / 必填檔 / 解析順序 / 缺檔處理規約
  - path: references/be-to-fe-mapping.md
    purpose: BE operation → FE userflow 對應規則；has-ui / no-ui 分類 rubric
  - path: references/verification-semantics-presets.md
    purpose: 4 種 Rule preset（locator / visual-state / route / API-binding）句型樣板 + 互斥/可組合規則
  - path: references/userflow-rule-coverage.md
    purpose: frontend Rule coverage matrix — happy / error / state-transition / a11y / cross-actor 必填項
```

## §2 SOP

> 閱讀規則：主 item 只做摘要；要執行的內容一律編成子步驟。未編號縮排只保留給條件說明、branch label 或補充註解。

### Phase 1 — LOAD runtime context + sibling BE truth
> produces: `$$runtime_context`, `$$be_truth_bundle`

1. 先綁定目前 skill 目錄、讀本次 Discovery-UIUX 會用到的設定檔與 BDD 憲法檔名軸，整理成本階段共用的執行設定。
   1.1 `$$skill_dir` = COMPUTE 目前 skill 目錄路徑
   1.2 LOAD REF [`aibdd-core::spec-package-paths.md`](aibdd-core::spec-package-paths.md) — boundary-aware 路徑規則
   1.3 LOAD REF [`aibdd-discovery::references/turn-discipline.md`](aibdd-discovery::references/turn-discipline.md) — 使用者回合的外顯訊號與狀態
   1.4 LOAD REF [`aibdd-discovery::references/contracts/io.md`](aibdd-discovery::references/contracts/io.md) — skill IO contract（必填欄位 / 綁定時點）
   1.5 `$args_abs` = COMPUTE `${arguments_yml_path}` 的絕對路徑（預設 `${workspace_root}/.aibdd/arguments.yml`）
   1.6 `$args_yaml` = READ `${args_abs}`
   1.7 `$$runtime_context` = PARSE `$args_yaml` 取 `STARTER_VARIANT` / `PROJECT_SPEC_LANGUAGE` / `TLB` / `UIUX_BACKEND_BOUNDARY_ID` / 檔名軸欄位

2. 檢查必要欄位是否齊全；缺則先補再回來重讀。
   2.1 ASSERT `$$runtime_context.TLB.role == "frontend"`
   2.2 IF assertion fails:
       2.2.1 EMIT "目前 TLB.role != frontend，aibdd-discovery-uiux 不適用；frontend TLB 才走本 skill；其他 boundary 請改用 /aibdd-discovery" to user
       2.2.2 STOP
   2.3 ASSERT `$$runtime_context.UIUX_BACKEND_BOUNDARY_ID` is non-empty string
   2.4 IF assertion fails:
       2.4.1 [USER INTERACTION] `$be_id_clarify` = DELEGATE `/clarify-loop`，附上 schema={questions:[{id:"be-id-q1", concern:"arguments.yml 缺 UIUX_BACKEND_BOUNDARY_ID；請指明 sibling backend boundary id（例：foo-be）", options:[]}]}
       2.4.2 WAIT for `$be_id_clarify`
       2.4.3 IF `$be_id_clarify.status == incomplete`:
             2.4.3.1 EMIT "UIUX_BACKEND_BOUNDARY_ID 仍未補齊；停止本輪" to user
             2.4.3.2 STOP
       2.4.4 GOTO #1.6

3. 把 FE 路徑解析展開；如果展開失敗，就直接停止。
   3.1 `$path_json` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/kickoff_path_resolve.py "${$args_abs}"`
   3.2 IF 路徑展開失敗:
       3.2.1 EMIT "kickoff 路徑展開失敗" to user
       3.2.2 STOP
   3.3 `$$runtime_context` = DERIVE 由設定、檔名軸與已展開 FE 路徑（`FEATURE_SPECS_DIR` / `ACTIVITIES_DIR` / `SPECS_ROOT_DIR` / `SPECS_DIR`）組成的最終執行設定

4. 解析 sibling BE 路徑並確認 BE artifacts 真的存在。
   4.1 LOAD REF [`references/backend-input-contract.md`](references/backend-input-contract.md) §1 — BE 路徑解析規則
   4.2 `$be_specs_dir` = COMPUTE `${SPECS_ROOT_DIR}/${UIUX_BACKEND_BOUNDARY_ID}`
   4.3 `$be_features_glob` = COMPUTE `${$be_specs_dir}/packages/**/*.feature`
   4.4 `$be_activities_glob` = COMPUTE `${$be_specs_dir}/packages/**/activities/*.activity`
   4.5 `$be_contracts_glob` = COMPUTE `${$be_specs_dir}/contracts/**/*.{yml,yaml}`
   4.6 ASSERT path_exists(`$be_specs_dir`)
   4.7 IF assertion fails:
       4.7.1 EMIT "sibling BE boundary 目錄不存在：`${$be_specs_dir}`；請先在該 boundary 跑 /aibdd-discovery + /aibdd-plan" to user
       4.7.2 STOP

5. 把 BE artifacts 全讀進 bundle；任一類缺檔就停下，引導使用者先把 BE 端跑完。
   5.1 `$be_features` = READ all paths matching `$be_features_glob`
   5.2 `$be_activities` = READ all paths matching `$be_activities_glob`
   5.3 `$be_contracts` = READ all paths matching `$be_contracts_glob`
   5.4 ASSERT length(`$be_features`) ≥ 1 ∧ length(`$be_activities`) ≥ 1
   5.5 IF assertion fails:
       5.5.1 EMIT "sibling BE 缺 .feature 或 .activity；請先跑 /aibdd-discovery 在 ${UIUX_BACKEND_BOUNDARY_ID}" to user
       5.5.2 STOP
   5.6 `$$be_truth_bundle` = DERIVE struct{features: `$be_features`, activities: `$be_activities`, contracts: `$be_contracts`, boundary_id: `$$runtime_context.UIUX_BACKEND_BOUNDARY_ID`}

### Phase 2 — SOURCE backend operations + classify has-ui vs no-ui
> produces: `$$discovery_bundle`

> **File-first invariant**：任何 `/clarify-loop` 呼叫之前，必須先在 plan package 下 WRITE 一份承載該輪題組的 artifact，並在 clarify-loop payload 附 `located_file_path` 指向該檔；待澄清題組同步寫進該檔的 `## Open <Stage> Questions` section。違反此 invariant 視為 SOP 缺陷，呼叫 `/skill-rca`。

1. 決定本輪 Discovery-UIUX 要寫到哪一個 plan package；Seam 0 draft sourcing report 就落在這個 plan package 底下。
   1.1 LOAD REF [`aibdd-discovery::references/contracts/discovery-sourcing-report.md`](aibdd-discovery::references/contracts/discovery-sourcing-report.md) — sourcing report 形狀（draft vs final）
   1.2 LOAD REF [`aibdd-discovery::references/relevance.md`](aibdd-discovery::references/relevance.md) — 判斷輸入是否落在 Discovery 軸
   1.3 `$plan_package_slug` = DERIVE 新 plan package slug，命名格式 `NNN-uiux-<slug>`，NNN 為當前 `${SPECS_ROOT_DIR}/${TLB.id}/` 下未占用的最小三位數
   1.4 `$bind_plan_rc` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/bind_plan_package.py "${$args_abs}" "${$plan_package_slug}"`
   1.5 IF `$bind_plan_rc != 0`:
       1.5.1 EMIT "bind_plan_package.py 執行失敗" to user
       1.5.2 STOP
   1.6 `$path_json` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/kickoff_path_resolve.py "${$args_abs}"`
   1.7 `$$runtime_context` = DERIVE 已重展開 plan-side 路徑後的執行設定（`PLAN_SPEC` / `PLAN_REPORTS_DIR` / `CURRENT_PLAN_PACKAGE` 對齊新 slug）

2. 把 BE truth 整體先機械抽出 operation inventory（每筆含 source + verb + object + actors + activity 對應）。
   2.1 `$operation_inventory_draft` = THINK per [`reasoning/discovery-uiux/01-be-sourcing.md`](reasoning/discovery-uiux/01-be-sourcing.md), input=`$$be_truth_bundle`
   2.2 ASSERT length(`$operation_inventory_draft.items`) ≥ 1
   2.3 IF assertion fails:
       2.3.1 EMIT "BE inventory 為空；可能是 BE artifacts 內容退化（feature 全 @ignore / activity 全 stub）" to user
       2.3.2 STOP

3. 落 draft sourcing report 作為 Seam A clarify-loop 的 anchor。
   3.1 LOAD REF [`references/be-to-fe-mapping.md`](references/be-to-fe-mapping.md) §1 — has-ui / no-ui 分類 rubric
   3.2 `$classification_draft` = THINK per [`reasoning/discovery-uiux/02-operation-classify.md`](reasoning/discovery-uiux/02-operation-classify.md), input=`$operation_inventory_draft`
   3.3 CREATE `${PLAN_REPORTS_DIR}`
   3.4 `$sourcing_draft` = DRAFT sourcing report draft ← `$$be_truth_bundle`, `$operation_inventory_draft`, `$classification_draft.ambiguous_items`
   3.5 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md` ← `$sourcing_draft`
   3.6 `$plan_summary_draft` = DRAFT Discovery-UIUX Sourcing Summary draft ← pointer `${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md`
   3.7 WRITE `${PLAN_SPEC}` ← `$plan_summary_draft`

4. Draft 檔已落地，再 fire Seam A clarify-loop，把 ambiguous classification 拉出來問。
   4.1 IF length(`$classification_draft.ambiguous_items`) == 0：GOTO #2.5.1
   4.2 [USER INTERACTION] `$classify_clarify_report` = DELEGATE `/clarify-loop`，附上 `$classification_draft.clarify_payload` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md` + `located_anchor_section = "Open Classification Questions"`
   4.3 WAIT for `$classify_clarify_report`
   4.4 IF `$classify_clarify_report.status == incomplete`:
       4.4.1 EMIT "classification 階段的 clarify-loop 回 incomplete；draft report 留檔，請補完題組後重跑" to user
       4.4.2 STOP

5. 整合 clarify 答案，re-WRITE final sourcing report（含 `## Resolved Classification Decisions` 與 `## GAP — no-ui operations`）。
   5.1 `$classification_final` = THINK 把 `$classify_clarify_report.answers` 整合進 `$classification_draft`
   5.2 `$sourcing_final` = DRAFT final sourcing report ← `$operation_inventory_draft`, `$classification_final`
   5.3 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md` ← `$sourcing_final`
   5.4 WRITE `${PLAN_SPEC}` ← updated Discovery-UIUX Sourcing Summary（pointer 對應 final report）

6. 對 has-ui operation 推 frontend uat_flow 草稿與 frontend_lens；如果結構仍歧義，先澄清再回來重跑這一步。
   6.1 `$has_ui_ops` = DERIVE 由 `$classification_final.items` 過濾出 classification == has-ui 的子集
   6.2 `$uat_flows_draft` = THINK per [`reasoning/discovery-uiux/03-userflow-derive.md`](reasoning/discovery-uiux/03-userflow-derive.md), input={has_ui_ops: `$has_ui_ops`, be_truth: `$$be_truth_bundle`}
   6.3 LOAD REF [`aibdd-discovery::references/rules/frontend-rule-axes.md`](aibdd-discovery::references/rules/frontend-rule-axes.md) — UI verb catalog / role mapping / anchor 命名 / boundary role gate
   6.4 LOAD REF [`aibdd-discovery::references/rules/hallucination-detection-checklist.md`](aibdd-discovery::references/rules/hallucination-detection-checklist.md) — Pattern 4 Frontend Lens 等腦補檢測
   6.5 `$frontend_lens` = THINK 從 `$uat_flows_draft` 機械抽 UIVerbBinding[] + AnchorCandidate[] + state_axes_hint per UI verb catalog
   6.6 IF `$frontend_lens.clarify_payload.questions` 非空 ∨ `$uat_flows_draft.clarify_payload.questions` 非空:
       6.6.1 `$flow_questions` = DERIVE concat(`$uat_flows_draft.clarify_payload.questions`, `$frontend_lens.clarify_payload.questions`)
       6.6.2 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-flow-clarify.md` ← draft flow + lens clarify anchor file
       6.6.3 [USER INTERACTION] `$flow_clarify_report` = DELEGATE `/clarify-loop`，附上 `$flow_questions` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-uiux-flow-clarify.md`
       6.6.4 WAIT for `$flow_clarify_report`
       6.6.5 IF `$flow_clarify_report.status == incomplete`:
             6.6.5.1 EMIT "uat-flow / frontend-lens 階段的 clarify-loop 回 incomplete；請補完題組後重跑" to user
             6.6.5.2 STOP
       6.6.6 GOTO #2.6.2

7. 整成 discovery bundle，準備餵給 Phase 3。
   7.1 `$$discovery_bundle` = DERIVE struct{be_truth: `$$be_truth_bundle`, operation_inventory: `$operation_inventory_draft`, classification: `$classification_final`, uat_flows: `$uat_flows_draft`, frontend_lens: `$frontend_lens`, gap_report_path: `${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md`}
   7.2 ASSERT length(`$$discovery_bundle.uat_flows.items`) == length(`$has_ui_ops`)
   7.3 IF assertion fails:
       7.3.1 EMIT "has-ui operation 數量與 derived uat_flow 數量不一致；可能 reasoning RP 漏推" to user
       7.3.2 STOP

### Phase 3 — DERIVE userflow activity + atomic rule with verification semantics
> produces: `$$activity_models`, `$$atomic_rule_draft`

1. 對每個 uat_flow 機械生 Activity model（actor=end-user，nodes=UI verb actions + DECISION branches + visual feedback nodes + terminals）。
   1.1 LOAD REF [`aibdd-discovery::references/rules/activity-variation-decomposition.md`](aibdd-discovery::references/rules/activity-variation-decomposition.md) — variation decomposition 規則
   1.2 LOAD REF [`aibdd-discovery::references/rules/actor-legality.md`](aibdd-discovery::references/rules/actor-legality.md) — Activity actor 必須是 external user / third-party
   1.3 LOAD REF [`aibdd-discovery::references/rules/activity-action-granularity.md`](aibdd-discovery::references/rules/activity-action-granularity.md) — activity action 粒度判定
   1.4 `$activity_models_draft` = THINK per [`reasoning/discovery-uiux/03-userflow-derive.md`](reasoning/discovery-uiux/03-userflow-derive.md) §Activity Build, input=`$$discovery_bundle.uat_flows`
   1.5 LOOP per `$am` in `$activity_models_draft.items`
       1.5.1 ASSERT `$am.actor` is external user / third-party
       1.5.2 ASSERT every branch has explicit terminal
       1.5.3 ASSERT step order has source justification（BE activity 對應 或 clarify 結果）
       1.5.4 IF any assertion fails:
             1.5.4.1 EMIT "activity model `${$am.id}` 違反 actor / branch / order 規約；停止" to user
             1.5.4.2 STOP
       END LOOP
   1.6 `$$activity_models` = `$activity_models_draft`

2. 載入 verification semantics preset 與 coverage matrix。
   2.1 LOAD REF [`aibdd-core::atomic-rule-definition.md`](aibdd-core::atomic-rule-definition.md) — Atomic Rule semantic 判定
   2.2 LOAD REF [`references/verification-semantics-presets.md`](references/verification-semantics-presets.md) — 4 種 Rule preset（locator / visual-state / route / API-binding）句型樣板
   2.3 LOAD REF [`references/userflow-rule-coverage.md`](references/userflow-rule-coverage.md) — Rule coverage matrix（happy / error / state-transition / a11y / cross-actor）

3. 對每個 UIVerbBinding 推 atomic rule（含 ui_verb + anchor.accessible_name + verification_mode + optional be_operation_binding）；以 coverage matrix 校驗完整性。
   3.1 `$atomic_rule_draft_raw` = THINK per [`reasoning/discovery-uiux/04-fe-atomic-rules.md`](reasoning/discovery-uiux/04-fe-atomic-rules.md), input={ui_verb_bindings: `$$discovery_bundle.frontend_lens.ui_verb_bindings`, anchors: `$$discovery_bundle.frontend_lens.anchor_candidates`, uat_flows: `$$discovery_bundle.uat_flows`, has_ui_ops: `$has_ui_ops`}
   3.2 LOOP per `$rule` in `$atomic_rule_draft_raw.items`
       3.2.1 ASSERT `$rule.ui_verb` ∈ UI verb catalog enum
       3.2.2 ASSERT `$rule.anchor.accessible_name` 為 source-quote-verbatim
       3.2.3 ASSERT `$rule.verification_mode` ∈ {locator, visual-state, route, api-binding}
       3.2.4 IF any assertion fails:
             3.2.4.1 EMIT "atomic rule `${$rule.id}` 違反 ui_verb / anchor / verification_mode 規約" to user
             3.2.4.2 STOP
       END LOOP

4. 用 coverage matrix 檢查每個 has-ui operation 都有對應規則覆蓋；如果 coverage gap 或 verification_mode 模糊就先澄清，再回來重跑。
   4.1 `$coverage_matrix` = DERIVE per `$has_ui_ops`：對每筆 op 統計對應到的 rule × {happy / error / state-transition / a11y}
   4.2 LOOP per `$op` in `$has_ui_ops`
       4.2.1 ASSERT `$coverage_matrix[$op.id].happy ≥ 1`
       4.2.2 IF assertion fails:
             4.2.2.1 MARK `$op.id` as coverage-gap candidate
       END LOOP
   4.3 IF count(coverage-gap candidates) > 0 ∨ `$atomic_rule_draft_raw.clarify_payload.questions` 非空:
       4.3.1 `$coverage_questions` = DERIVE concat(coverage-gap 題組, `$atomic_rule_draft_raw.clarify_payload.questions`)
       4.3.2 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-coverage-clarify.md` ← draft coverage clarify anchor file
       4.3.3 [USER INTERACTION] `$coverage_clarify_report` = DELEGATE `/clarify-loop`，附上 `$coverage_questions` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-uiux-coverage-clarify.md`
       4.3.4 WAIT for `$coverage_clarify_report`
       4.3.5 IF `$coverage_clarify_report.status == incomplete`:
             4.3.5.1 EMIT "coverage 階段的 clarify-loop 回 incomplete；請補完題組後重跑" to user
             4.3.5.2 STOP
       4.3.6 GOTO #3.3.1

5. 整成 atomic rule draft，準備餵給 Phase 4 落檔。
   5.1 `$$atomic_rule_draft` = DERIVE 由 `$atomic_rule_draft_raw.items` + `$coverage_matrix` 組成的 atomic rule bundle，含 features index（每個 has-ui op 一個 feature）
   5.2 ASSERT length(`$$atomic_rule_draft.features`) == length(`$has_ui_ops`)
   5.3 IF assertion fails:
       5.3.1 EMIT "feature index 與 has-ui ops 數量不一致；可能 RP 04 漏推" to user
       5.3.2 STOP

### Phase 4 — FORM .activity + .feature skeleton via DELEGATE
> produces: `$$artifact_bundle`

1. 先確認 Phase 2 / 3 沒留下未解問題；如果還有 open question 就停下，不寫檔。
   1.1 ASSERT length(`$$discovery_bundle.uat_flows.clarify_payload.questions`) == 0
   1.2 ASSERT length(`$$discovery_bundle.frontend_lens.clarify_payload.questions`) == 0
   1.3 ASSERT length(`$$atomic_rule_draft.clarify_payload.questions`) == 0
   1.4 IF any assertion fails:
       1.4.1 EMIT "Phase 2/3 仍有未解 question；禁止落檔" to user
       1.4.2 STOP

2. 逐個 Activity model 落出 `.activity`；同一份連續失敗兩次就停止整輪。
   2.1 LOOP per `$am` in `$$activity_models.items`
       2.1.1 `$activity_target_path` = COMPUTE `${ACTIVITIES_DIR}/${$am.slug}.activity`
       2.1.2 `$activity_report` = DELEGATE `/aibdd-form-activity`，附上 target_path=`$activity_target_path`, format=".activity", mode="overwrite", reasoning.activity_analysis=`$am`
       2.1.3 IF `$activity_report.status != completed`:
             2.1.3.1 `$activity_retry` = DELEGATE `/aibdd-form-activity`，附上同一份題組
             2.1.3.2 IF `$activity_retry.status != completed`:
                   2.1.3.2.1 EMIT "aibdd-form-activity 失敗兩次（${$am.slug}）；停止本輪 Discovery-UIUX" to user
                   2.1.3.2.2 STOP
       END LOOP

3. 逐個 feature 落出 rule-only `.feature` 骨架；feature 必須 flat 寫在 `${FEATURE_SPECS_DIR}` 下，不得自行插入 domain 子目錄。
   3.1 LOOP per `$feature` in `$$atomic_rule_draft.features`
       3.1.1 ASSERT `$feature.target_path` is flat under `${FEATURE_SPECS_DIR}`
       3.1.2 IF assertion fails:
             3.1.2.1 EMIT "feature target_path 不是 flat（${$feature.target_path}）" to user
             3.1.2.2 STOP
       3.1.3 `$feature_report` = DELEGATE `/aibdd-form-feature-spec`，附上 {target_path: `$feature.target_path`, mode: "rule-only", folder_strategy: "flat", reasoning: `$feature.reasoning_package`}
       3.1.4 IF `$feature_report.status != completed`:
             3.1.4.1 EMIT "${$feature.target_path} formulation 失敗：${$feature_report.reason}" to user
             3.1.4.2 STOP
       END LOOP

4. 收尾檢查：所有 has-ui operation 都有對應 `.feature`、所有 modeled uat_flow 都有對應 `.activity`、GAP report 已就位、formulation skill 沒自己補腦缺欄。
   4.1 ASSERT every has-ui op 在 `${FEATURE_SPECS_DIR}` 下都有對應 `.feature`
   4.2 ASSERT every modeled uat_flow 在 `${ACTIVITIES_DIR}` 下都有對應 `.activity`
   4.3 ASSERT path_exists(`$$discovery_bundle.gap_report_path`)
   4.4 IF any assertion fails:
       4.4.1 EMIT "落檔收尾檢查失敗；停止本輪 Discovery-UIUX" to user
       4.4.2 STOP
   4.5 `$$artifact_bundle` = DERIVE struct{activities: `$$activity_models.items`, features: `$$atomic_rule_draft.features`, gap_report: `$$discovery_bundle.gap_report_path`, coverage_matrix: `$coverage_matrix`}

### Phase 5 — GATE quality + residual clarification sweep
> produces: `$$quality_verdict`, `$$clarify_report`

#### 5.A Script gates (deterministic)

| # | Script | 這一輪要擋的事 |
|---|---|---|
| 1 | `grep_sticky_notes.py` | clean artifact 內不得殘留未解的 `CiC(...)` |
| 2 | `check_actor_legality.py` | Activity actor 必須是 external user / third-party |
| 3 | `check_discovery_phase.py` | Discovery feature 必須維持 rule-only 形狀 |
| 4 | `check_operation_wise.py` | 先擋明顯檔名或 trigger 反模式 |
| 5 | `check_raw_artifact_alignment.py` | raw idea / BE truth 與 artifact 對齊檢查；違規記為 GAP，不阻擋通關 |

#### 5.B Semantic gate (subagent rubric — inline per §4.7.6)

Planner 禁止 self-judge — DELEGATE 至獨立 subagent，依下表 rubric 評判。下表是本 Phase 5 §5.B step 的**唯一** rubric，rubric 與 step 同生死。

| rule_id | Requirement |
|---|---|
| `CIC_GAP_RESIDUAL` | clean artifact 內無 `CiC(GAP: ...)` 殘留 |
| `CIC_ASM_RESIDUAL` | clean artifact 內無 `CiC(ASM: ...)` 殘留 |
| `CIC_BDY_RESIDUAL` | clean artifact 內無 `CiC(BDY: ...)` 殘留 |
| `CIC_CON_RESIDUAL` | clean artifact 內無 `CiC(CON: ...)` 殘留 |
| `RULE_UNIT_COVERAGE` | 每條帶有規則意義的 BE 來源敘述，至少對應一個 frontend artifact unit |
| `OPERATION_WISE_FEATURE_FILE` | 每個 feature file 只對應一個 has-ui operation |
| `ACTIVITY_ACTOR_EXTERNAL` | 每個 Activity actor 為 external user / third-party |
| `RULE_NO_EXAMPLE_LEAK` | example data 不得洩漏進 Discovery Rules |
| `ACTIVITY_STEP_ORDER_JUSTIFIED` | Activity step 順序必須有 BE 對應或使用者確認 |
| `ACTIVITY_SELF_CONTAINED_PATH` | 每個 Activity 都是完整 user-entry → terminal 路徑 |
| `ACTIVITY_BRANCH_TERMINAL_EXPLICIT` | 每個 branch 都要有 explicit terminal |
| `F1_HAPPY_PATH` | 每個 has-ui op 至少一條 happy-path Rule |
| `F2_EDGE_CASES` | edge / error path 有 Rules 或 explicit CiC markers |
| `F3_ACTOR_RULES` | 每個 Actor 都有對應的合法性 / 授權規則 |
| `F4_STATE_TRANSITIONS` | 重要 state transitions 有 Rules |
| `UIUX_VERIFICATION_MODE_PRESENT` | 每條 Rule 必標 verification_mode ∈ {locator, visual-state, route, api-binding} |
| `UIUX_NO_BE_VERB_LEAK` | Rule 不得出現 backend 黑名單動詞（POST / persist / 200 / database / API / commit transaction 等） |
| `UIUX_BE_OPERATION_COVERAGE` | 每個 has-ui operation ≥1 frontend feature |
| `UIUX_NO_UI_GAP_REPORT_PRESENT` | GAP report 含每個 no-ui operation 的 reasoning column 與 source 對應 |

**Failure contract**: violations 不得透過弱化 checklist 來 patch；fail 時返回 Phase 4 §1（落檔重做）並帶回原始 inputs。

#### 5.C 合併 verdict 迴圈

1. 用最多 5 輪的補救迴圈跑完 script gate 與 semantic gate；只要其中一輪全數通過，就進殘留 sweep。
   1.1 LOOP quality gate remediation (max 5)
       1.1.1 `$sticky_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/grep_sticky_notes.py ${SPECS_ROOT_DIR}`
       1.1.2 `$actor_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/check_actor_legality.py ${$args_abs}`
       1.1.3 `$phase_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/check_discovery_phase.py ${$args_abs}`
       1.1.4 `$operation_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/check_operation_wise.py ${$args_abs} --constitution ${BDD_CONSTITUTION_PATH}`
       1.1.5 `$alignment_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/check_raw_artifact_alignment.py ${$args_abs}`
       1.1.6 `$semantic_verdict` = DELEGATE 獨立 semantic subagent，rubric=Phase 5 §5.B table，input={discovery_bundle: `$$discovery_bundle`, atomic_rule_draft: `$$atomic_rule_draft`, artifact_bundle: `$$artifact_bundle`}
       1.1.7 `$$quality_verdict` = PARSE 所有 gate 輸出的合併 verdict
       1.1.8 BRANCH `$$quality_verdict.ok` ? GOTO #5.2.1 : GOTO #4.2.1
       END LOOP

2. 5 輪未過則停下來，不允許靠放鬆 gate 規則硬過。
   2.1 EMIT "Quality gate 連續 5 輪仍未通過；違反 Failure contract 禁止弱化 checklist" to user
   2.2 STOP

#### 5.D 殘留 clarify sweep

1. 當 deterministic 與 semantic gate 都先過一輪後，再做一次跨 artifact 的殘留 sweep。
   1.1 `$$clarify_report` = THINK per [`reasoning/discovery-uiux/05-userflow-clarification-dimensions.md`](reasoning/discovery-uiux/05-userflow-clarification-dimensions.md), input={discovery_bundle: `$$discovery_bundle`, artifact_bundle: `$$artifact_bundle`, quality_verdict: `$$quality_verdict`}
   1.2 BRANCH length(`$$clarify_report.questions`) == 0 ? GOTO #6.1 : GOTO #5.5.2.1

2. 把殘留問題交給 `/clarify-loop`；如果回來後真的改到了檔案，就回 Phase 5 §5.C 重新驗一次。
   2.1 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-residual-clarify.md` ← draft residual sweep anchor file
   2.2 [USER INTERACTION] `$residual_clarify` = DELEGATE `/clarify-loop`，附上 `$$clarify_report.questions` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-uiux-residual-clarify.md`
   2.3 WAIT for `$residual_clarify`
   2.4 IF `$residual_clarify.status == incomplete`:
       2.4.1 EMIT "殘留 clarify 階段未完成；請補完題組後重跑" to user
       2.4.2 STOP
   2.5 BRANCH `$residual_clarify.files_changed` is non-empty ? GOTO #5.3.1.1 : GOTO #6.1

### Phase 6 — EMIT REPORT
> produces: (none)

1. 用使用者看得懂的語氣收斂這輪 Discovery-UIUX 的成果。
   1.1 LOAD REF [`aibdd-core::report-contract.md`](aibdd-core::report-contract.md) — 對外報告的語氣與必要欄位
   1.2 `$summary` = DRAFT 最終 Discovery-UIUX 報告 ← `$$artifact_bundle`, `$$discovery_bundle`, `$$quality_verdict`, `$$clarify_report`；訊息包含 has-ui / no-ui 統計、coverage matrix 摘要、GAP report pointer、verification mode 分布、下一步建議跑 `/aibdd-plan`

2. 把報告送給使用者；如果當下送不出去，再寫入 fallback report 並停。
   2.1 EMIT `$summary` to user
   2.2 IF EMIT 失敗:
       2.2.1 WRITE `${SPECS_ROOT_DIR}/.discovery-uiux-report.md` ← `$summary`
       2.2.2 STOP

## §3 CROSS-REFERENCES

- 由 `/aibdd-discovery-uiux` command 觸發（root entry，frontend TLB 場景取代 `/aibdd-discovery`）
- DELEGATE `/aibdd-form-activity` + `/aibdd-form-feature-spec` — 落檔 formulation skills
- DELEGATE `/clarify-loop` — 5 個觸發點：missing-field（UIUX_BACKEND_BOUNDARY_ID）/ Seam A classification / Seam B uat-flow+frontend-lens / Seam C atomic-rule coverage / Phase 5 殘留 sweep；題組沿用既有 schema，每次呼叫前必先落 draft 檔（File-first invariant）
- 下游：`/aibdd-plan` 進行 technical plan / DSL proposal planning；frontend 場景常接 `/aibdd-uiux-discovery` 做視覺探索後再 `/aibdd-plan`
- 共用 scripts（reuse aibdd-discovery）：`kickoff_path_resolve.py` / `bind_plan_package.py` / `grep_sticky_notes.py` / `check_actor_legality.py` / `check_discovery_phase.py` / `check_operation_wise.py` / `check_raw_artifact_alignment.py`
- Registry entry 樣板：`assets/registry/entry.yml`
