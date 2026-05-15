---
name: aibdd-discovery-uiux
description: 從 sibling backend boundary 的 `.feature` + `.activity` + `contracts/api.yml` 推導 frontend TLB 的 userflow 視角 `.activity` + `.feature` skeleton — 取代 `/aibdd-discovery` 在 frontend TLB 場景。先依 arguments.yml 的 UIUX_BACKEND_BOUNDARY_ID 解析 BE truth；把 sibling BE `contracts/api.yml` 鏡像進 FE `${CONTRACTS_DIR}/api.yml` 並寫 `.source-hash`（下游 pre-red §3.0 freshness gate 依賴）；CLASSIFY 每個 BE operation 為 has-ui / no-ui（no-ui 寫進 GAP 報告不落 feature）；再為 has-ui operation 推導 UI verb binding + accessible-name anchor + 4 種驗證語意（locator / visual-state / route / API-binding）的 Rule preset；DELEGATE /aibdd-form-activity 與 /aibdd-form-feature-spec 落檔。TRIGGER when 使用者下 /aibdd-discovery-uiux、TLB.role=="frontend" 且 sibling BE 已具備 spec truth。SKIP when TLB 非 frontend、UIUX_BACKEND_BOUNDARY_ID 未設定、或 sibling BE artifacts 缺漏。
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
  - path: references/fe-intent-contract.md
    purpose: raw idea 收斂 SSOT — fe_intent_bundle schema / 7 類 Seam 0 題型 / 下游消費規約 / intent ↔ BE alignment matrix shape
  - path: references/be-gap-handling.md
    purpose: BE truth 對 FE 用途不足時的 FE-side 補位契約 — BG-001..BG-008 偵測規則 / 候選 supplement options / NO_BE_MUTATION_LEAK invariant
```

## §2 SOP

> 閱讀規則：主 item 只做摘要；要執行的內容一律編成子步驟。未編號縮排只保留給條件說明、branch label 或補充註解。

### Phase 1 — LOAD runtime context + sibling BE truth
> produces: `$$runtime_context`, `$$be_truth_bundle`

1. `$ctx_init` = MARK "bind skill dir, load runtime config and BDD stack refs"
   1.1 `$$skill_dir` = COMPUTE 目前 skill 目錄路徑
   1.2 LOAD REF [`aibdd-core::spec-package-paths.md`](aibdd-core::spec-package-paths.md) — boundary-aware 路徑規則
   1.3 LOAD REF [`aibdd-discovery::references/turn-discipline.md`](aibdd-discovery::references/turn-discipline.md) — 使用者回合的外顯訊號與狀態
   1.4 LOAD REF [`aibdd-discovery::references/contracts/io.md`](aibdd-discovery::references/contracts/io.md) — skill IO contract（必填欄位 / 綁定時點）
   1.5 `$args_abs` = COMPUTE `${arguments_yml_path}` 的絕對路徑（預設 `${workspace_root}/.aibdd/arguments.yml`）
   1.6 `$args_yaml` = READ `${args_abs}`
   1.7 `$$runtime_context` = PARSE `$args_yaml` 取 `STARTER_VARIANT` / `PRESET_KIND` / `PROJECT_SPEC_LANGUAGE` / `PROJECT_SLUG` / `TLB_ID` / `BACKEND_SUBDIR` / `FRONTEND_SUBDIR` / `SPECS_ROOT_DIR` / `UIUX_BACKEND_BOUNDARY_ID` / `LAST_USER_PROMPT` / 檔名軸欄位（`LAST_USER_PROMPT` 缺欄視為空字串）
   1.8 `$$runtime_context.TLB` = DERIVE struct{id: `${TLB_ID}` (展開為 PROJECT_SLUG 值；fallback PROJECT_SLUG 本身), role: `PRESET_KIND == "web-frontend" ? "frontend" : (PRESET_KIND == "web-backend" ? "backend" : "unknown")`}

2. `$preconditions` = MARK "assert TLB.role==frontend and UIUX_BACKEND_BOUNDARY_ID present"
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

3. `$path_expand` = MARK "run kickoff_path_resolve.py and expand FE paths"
   3.1 `$path_json` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/kickoff_path_resolve.py "${$args_abs}"`
   3.2 IF 路徑展開失敗:
       3.2.1 EMIT "kickoff 路徑展開失敗" to user
       3.2.2 STOP
   3.3 `$$runtime_context` = DERIVE 由設定、檔名軸與已展開 FE 路徑（`FEATURE_SPECS_DIR` / `ACTIVITIES_DIR` / `SPECS_ROOT_DIR` / `SPECS_DIR`）組成的最終執行設定

4. `$be_path_check` = MARK "derive sibling BE paths and assert boundary directory exists"
   4.1 LOAD REF [`references/backend-input-contract.md`](references/backend-input-contract.md) §1 — BE 路徑解析規則
   4.2 `$be_specs_dir` = COMPUTE `${SPECS_ROOT_DIR}/${UIUX_BACKEND_BOUNDARY_ID}`
   4.3 `$be_features_glob` = COMPUTE `${$be_specs_dir}/packages/**/*.feature`
   4.4 `$be_activities_glob` = COMPUTE `${$be_specs_dir}/packages/**/activities/*.activity`
   4.5 `$be_contracts_glob` = COMPUTE `${$be_specs_dir}/contracts/**/*.{yml,yaml}`
   4.6 ASSERT path_exists(`$be_specs_dir`)
   4.7 IF assertion fails:
       4.7.1 EMIT "sibling BE boundary 目錄不存在：`${$be_specs_dir}`；請先在該 boundary 跑 /aibdd-discovery + /aibdd-plan" to user
       4.7.2 STOP

5. `$be_load` = MARK "read all BE artifacts into truth bundle"
   5.1 `$be_features` = READ all paths matching `$be_features_glob`
   5.2 `$be_activities` = READ all paths matching `$be_activities_glob`
   5.3 `$be_contracts` = READ all paths matching `$be_contracts_glob`
   5.4 ASSERT length(`$be_features`) ≥ 1 ∧ length(`$be_activities`) ≥ 1
   5.5 IF assertion fails:
       5.5.1 EMIT "sibling BE 缺 .feature 或 .activity；請先跑 /aibdd-discovery 在 ${UIUX_BACKEND_BOUNDARY_ID}" to user
       5.5.2 STOP
   5.6 `$$be_truth_bundle` = DERIVE struct{features: `$be_features`, activities: `$be_activities`, contracts: `$be_contracts`, boundary_id: `$$runtime_context.UIUX_BACKEND_BOUNDARY_ID`}

6. `$api_yml_mirror` = MARK "mirror sibling BE api.yml into FE CONTRACTS_DIR + write .source-hash (pre-red §3.0 SSOT)"
   6.1 `$be_api_yml_src` = COMPUTE `${$be_specs_dir}/contracts/api.yml`
   6.2 ASSERT path_exists(`$be_api_yml_src`)
   6.3 IF assertion fails:
       6.3.1 EMIT "sibling BE 缺 contracts/api.yml：`${$be_api_yml_src}`；請先在 ${UIUX_BACKEND_BOUNDARY_ID} 跑 /aibdd-form-api-spec" to user
       6.3.2 STOP
   6.4 `$fe_contracts_dir` = COMPUTE `${SPECS_ROOT_DIR}/${$$runtime_context.TLB.id}/contracts`
   6.5 `$fe_api_yml_dst` = COMPUTE `${$fe_contracts_dir}/api.yml`
   6.6 `$fe_api_yml_hash` = COMPUTE `${$fe_api_yml_dst}.source-hash`
   6.7 CREATE `$fe_contracts_dir`（若不存在）
   6.8 `$be_api_sha256` = TRIGGER `python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${$be_api_yml_src}"`
   6.9 IF `$be_api_sha256` 取值失敗:
       6.9.1 EMIT "BE api.yml sha256 計算失敗：`${$be_api_yml_src}`" to user
       6.9.2 STOP
   6.10 `$mirror_decision` = BRANCH path_exists(`$fe_api_yml_dst`) ∧ path_exists(`$fe_api_yml_hash`)
         ? (READ `$fe_api_yml_hash` == `$be_api_sha256` ? "in-sync" : "drift")
         : "absent"
   6.11 IF `$mirror_decision` ∈ {"absent", "drift"}:
         6.11.1 `$be_api_yml_text` = READ `$be_api_yml_src`
         6.11.2 WRITE `$fe_api_yml_dst` ← `$be_api_yml_text`
         6.11.3 WRITE `$fe_api_yml_hash` ← `$be_api_sha256`
         6.11.4 EMIT "FE api.yml mirror 已${$mirror_decision == 'absent' ? '初始化' : '更新'}：`${$fe_api_yml_dst}`（hash=`${$be_api_sha256[:12]}…`）" to user
   6.12 `$$be_truth_bundle.fe_api_yml_path` = DERIVE `$fe_api_yml_dst`
   6.13 `$$be_truth_bundle.fe_api_yml_source_hash` = DERIVE `$be_api_sha256`

### Phase 2 — SOURCE backend operations + FE intent + BE gaps + classify has-ui vs no-ui
> produces: `$$discovery_bundle`, `$$fe_intent_bundle`, `$$be_gap_findings`

> **File-first invariant**：任何 `/clarify-loop` 呼叫之前，必須先在 plan package 下 WRITE 一份承載該輪題組的 artifact，並在 clarify-loop payload 附 `located_file_path` 指向該檔；待澄清題組同步寫進該檔的 `## Open <Stage> Questions` section。違反此 invariant 視為 SOP 缺陷，呼叫 `/skill-rca`。

1. `$plan_pkg_init` = MARK "derive plan package slug, run bind_plan_package.py, re-resolve paths"
   1.1 LOAD REF [`aibdd-discovery::references/contracts/discovery-sourcing-report.md`](aibdd-discovery::references/contracts/discovery-sourcing-report.md) — sourcing report 形狀（draft vs final）
   1.2 LOAD REF [`aibdd-discovery::references/relevance.md`](aibdd-discovery::references/relevance.md) — 判斷輸入是否落在 Discovery 軸
   1.3 `$plan_package_slug` = DERIVE 新 plan package slug，命名格式 `NNN-uiux-<slug>`，NNN 為當前 `${SPECS_ROOT_DIR}/${TLB.id}/` 下未占用的最小三位數
   1.4 `$bind_plan_rc` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/bind_plan_package.py "${$args_abs}" "${$plan_package_slug}"`
   1.5 IF `$bind_plan_rc != 0`:
       1.5.1 EMIT "bind_plan_package.py 執行失敗" to user
       1.5.2 STOP
   1.6 `$path_json` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/kickoff_path_resolve.py "${$args_abs}"`
   1.7 `$$runtime_context` = DERIVE 已重展開 plan-side 路徑後的執行設定（`PLAN_SPEC` / `PLAN_REPORTS_DIR` / `CURRENT_PLAN_PACKAGE` 對齊新 slug）

2. `$op_extract` = MARK "extract BE operation inventory + detect BE gaps via RP 01-be-sourcing"
   2.1 LOAD REF [`references/be-gap-handling.md`](references/be-gap-handling.md) — BE 缺口偵測規則 + FE-side supplementation invariant
   2.2 `$be_sourcing_out` = THINK per [`reasoning/discovery-uiux/01-be-sourcing.md`](reasoning/discovery-uiux/01-be-sourcing.md), input=`$$be_truth_bundle`
   2.3 `$operation_inventory_draft` = DERIVE `$be_sourcing_out.operation_inventory`
   2.4 `$$be_gap_findings` = DERIVE `$be_sourcing_out.be_gap_findings`
   2.5 `$supplement_questions` = DERIVE `$be_sourcing_out.clarify_payload.questions`
   2.6 ASSERT length(`$operation_inventory_draft.items`) ≥ 1
   2.7 IF assertion fails:
       2.7.1 EMIT "BE inventory 為空；可能是 BE artifacts 內容退化（feature 全 @ignore / activity 全 stub）" to user
       2.7.2 STOP

3. `$seam_0_prime` = MARK "Seam 0' — fire BE-gap FE-side supplementation clarify-loop"
   3.1 CREATE `${PLAN_REPORTS_DIR}`
   3.2 `$be_gap_draft` = DRAFT BE gap report draft ← `$$be_gap_findings`, `$supplement_questions`；含 `## BE Gaps Detected` + `## Open BE Supplementation Questions` sections per [`references/be-gap-handling.md`](references/be-gap-handling.md) §4
   3.3 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-be-gap.md` ← `$be_gap_draft`
   3.4 IF length(`$supplement_questions`) == 0：GOTO #2.4.1
   3.5 [USER INTERACTION] `$be_gap_clarify_report` = DELEGATE `/clarify-loop`，附上 `$supplement_questions` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-uiux-be-gap.md` + `located_anchor_section = "Open BE Supplementation Questions"`
   3.6 WAIT for `$be_gap_clarify_report`
   3.7 IF `$be_gap_clarify_report.status == incomplete`:
       3.7.1 EMIT "Seam 0' (BE gap) 的 clarify-loop 回 incomplete；draft report 留檔，請補完題組後重跑" to user
       3.7.2 STOP
   3.8 `$$be_gap_findings` = DERIVE 把 `$be_gap_clarify_report.answers` 整合進 `$$be_gap_findings`（每筆填入 chosen_option_id）
   3.9 `$be_gap_final` = DRAFT final BE gap report ← `$$be_gap_findings`；section 改為 `## BE Gaps Detected` + `## BE Gaps Resolved (FE-side)` + `## BE Gaps Forwarded`
   3.10 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-be-gap.md` ← `$be_gap_final`

4. `$intent_sourcing` = MARK "RP 00 — derive fe_intent_bundle + fire Seam 0 intent clarify-loop"
   4.1 LOAD REF [`references/fe-intent-contract.md`](references/fe-intent-contract.md) — FE intent bundle schema + 7 類 Seam 0 題型
   4.2 `$raw_idea` = DERIVE `$$runtime_context.LAST_USER_PROMPT`（缺欄視為空字串）
   4.3 `$intent_out` = THINK per [`reasoning/discovery-uiux/00-fe-intent-sourcing.md`](reasoning/discovery-uiux/00-fe-intent-sourcing.md), input={raw_idea: `$raw_idea`, operation_inventory: `$operation_inventory_draft`, be_truth: `$$be_truth_bundle`}
   4.4 `$$fe_intent_bundle` = DERIVE `$intent_out.fe_intent_bundle`
   4.5 `$intent_questions` = DERIVE `$intent_out.clarify_payload.questions`
   4.6 `$intent_draft` = DRAFT intent report draft ← `$raw_idea`, `$$fe_intent_bundle`, `$intent_questions`；含 raw idea verbatim fenced block + alignment_matrix table + `## Open Intent Questions` section per [`references/fe-intent-contract.md`](references/fe-intent-contract.md) §5
   4.7 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-intent.md` ← `$intent_draft`
   4.8 IF length(`$intent_questions`) == 0：GOTO #2.5.1
   4.9 [USER INTERACTION] `$intent_clarify_report` = DELEGATE `/clarify-loop`，附上 `$intent_questions` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-uiux-intent.md` + `located_anchor_section = "Open Intent Questions"`
   4.10 WAIT for `$intent_clarify_report`
   4.11 IF `$intent_clarify_report.status == incomplete`:
        4.11.1 EMIT "Seam 0 (FE intent) 的 clarify-loop 回 incomplete；draft report 留檔，請補完題組後重跑" to user
        4.11.2 STOP
   4.12 `$$fe_intent_bundle` = DERIVE 把 `$intent_clarify_report.answers` 整合進 `$$fe_intent_bundle`（填回 scope_decisions / page_compositions / actor_splits / state_axis_priority / brand_seed unknown 欄位）
   4.13 `$intent_final` = DRAFT final intent report ← `$raw_idea`, `$$fe_intent_bundle`；section 改為 raw idea verbatim + alignment_matrix + `## Resolved Intent Decisions`
   4.14 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-intent.md` ← `$intent_final`

5. `$draft_sourcing` = MARK "classify operations (intent + be_gap aware) and write draft sourcing report as Seam A anchor"
   5.1 LOAD REF [`references/be-to-fe-mapping.md`](references/be-to-fe-mapping.md) §1 — has-ui / no-ui 分類 rubric
   5.2 `$classification_draft` = THINK per [`reasoning/discovery-uiux/02-operation-classify.md`](reasoning/discovery-uiux/02-operation-classify.md), input={operation_inventory: `$operation_inventory_draft`, be_truth: `$$be_truth_bundle`, fe_intent_bundle: `$$fe_intent_bundle`, be_gap_findings: `$$be_gap_findings`}
   5.3 `$sourcing_draft` = DRAFT sourcing report draft ← `$$be_truth_bundle`, `$operation_inventory_draft`, `$classification_draft.ambiguous_items`；含 pointer 到 `discovery-uiux-intent.md` + `discovery-uiux-be-gap.md`
   5.4 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md` ← `$sourcing_draft`
   5.5 `$plan_summary_draft` = DRAFT Discovery-UIUX Sourcing Summary draft ← pointer `${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md`
   5.6 WRITE `${PLAN_SPEC}` ← `$plan_summary_draft`

6. `$seam_a_clarify` = MARK "fire Seam A clarify-loop for ambiguous has-ui classification"
   6.1 IF length(`$classification_draft.ambiguous_items`) == 0：GOTO #2.7.1
   6.2 [USER INTERACTION] `$classify_clarify_report` = DELEGATE `/clarify-loop`，附上 `$classification_draft.clarify_payload` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md` + `located_anchor_section = "Open Classification Questions"`
   6.3 WAIT for `$classify_clarify_report`
   6.4 IF `$classify_clarify_report.status == incomplete`:
       6.4.1 EMIT "classification 階段的 clarify-loop 回 incomplete；draft report 留檔，請補完題組後重跑" to user
       6.4.2 STOP

7. `$sourcing_finalize` = MARK "integrate clarify answers and re-write final sourcing report"
   7.1 `$classification_final` = THINK 把 `$classify_clarify_report.answers` 整合進 `$classification_draft`
   7.2 `$sourcing_final` = DRAFT final sourcing report ← `$operation_inventory_draft`, `$classification_final`；含 pointer 到 `discovery-uiux-intent.md` + `discovery-uiux-be-gap.md`
   7.3 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md` ← `$sourcing_final`
   7.4 WRITE `${PLAN_SPEC}` ← updated Discovery-UIUX Sourcing Summary（pointer 對應 final report）

8. `$flow_derive` = MARK "derive uat_flows and frontend_lens for has-ui ops via RP 03 (intent + be_gap aware); fire Seam B clarify-loop if needed"
   8.1 `$has_ui_ops` = DERIVE 由 `$classification_final.items` 過濾出 classification == has-ui 的子集
   8.2 `$uat_flows_draft` = THINK per [`reasoning/discovery-uiux/03-userflow-derive.md`](reasoning/discovery-uiux/03-userflow-derive.md), input={has_ui_ops: `$has_ui_ops`, be_truth: `$$be_truth_bundle`, fe_intent_bundle: `$$fe_intent_bundle`, be_gap_findings: `$$be_gap_findings`}
   8.3 LOAD REF [`aibdd-discovery::references/rules/frontend-rule-axes.md`](aibdd-discovery::references/rules/frontend-rule-axes.md) — UI verb catalog / role mapping / anchor 命名 / boundary role gate
   8.4 LOAD REF [`aibdd-discovery::references/rules/hallucination-detection-checklist.md`](aibdd-discovery::references/rules/hallucination-detection-checklist.md) — Pattern 4 Frontend Lens 等腦補檢測
   8.5 `$frontend_lens` = THINK 從 `$uat_flows_draft` 機械抽 UIVerbBinding[] + AnchorCandidate[] + state_axes_hint per UI verb catalog
   8.6 IF `$frontend_lens.clarify_payload.questions` 非空 ∨ `$uat_flows_draft.clarify_payload.questions` 非空:
       8.6.1 `$flow_questions` = DERIVE concat(`$uat_flows_draft.clarify_payload.questions`, `$frontend_lens.clarify_payload.questions`)
       8.6.2 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-flow-clarify.md` ← draft flow + lens clarify anchor file
       8.6.3 [USER INTERACTION] `$flow_clarify_report` = DELEGATE `/clarify-loop`，附上 `$flow_questions` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-uiux-flow-clarify.md`
       8.6.4 WAIT for `$flow_clarify_report`
       8.6.5 IF `$flow_clarify_report.status == incomplete`:
             8.6.5.1 EMIT "uat-flow / frontend-lens 階段的 clarify-loop 回 incomplete；請補完題組後重跑" to user
             8.6.5.2 STOP
       8.6.6 GOTO #2.8.6.2

9. `$bundle_assemble` = MARK "assemble discovery bundle struct"
   9.1 `$$discovery_bundle` = DERIVE struct{be_truth: `$$be_truth_bundle`, operation_inventory: `$operation_inventory_draft`, classification: `$classification_final`, uat_flows: `$uat_flows_draft`, frontend_lens: `$frontend_lens`, fe_intent_bundle: `$$fe_intent_bundle`, be_gap_findings: `$$be_gap_findings`, gap_report_path: `${PLAN_REPORTS_DIR}/discovery-uiux-sourcing.md`, intent_report_path: `${PLAN_REPORTS_DIR}/discovery-uiux-intent.md`, be_gap_report_path: `${PLAN_REPORTS_DIR}/discovery-uiux-be-gap.md`}
   9.2 ASSERT length(`$$discovery_bundle.uat_flows.items`) >= length(`$has_ui_ops`)
   9.3 IF assertion fails:
       9.3.1 EMIT "uat_flow 數量小於 has-ui operation 數量；可能 reasoning RP 漏推（注意：ux-only-flow 視為額外 UATFlow，因此 ≥ 而非 ==）" to user
       9.3.2 STOP

### Phase 3 — DERIVE userflow activity + atomic rule with verification semantics
> produces: `$$activity_models`, `$$atomic_rule_draft`

1. `$activity_build` = MARK "build Activity models per uat_flow via RP 03 Activity Build"
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
   1.6 `$$activity_models` = DERIVE `$activity_models_draft`

2. `$verification_load` = MARK "load verification semantics presets and coverage matrix refs"
   2.1 LOAD REF [`aibdd-core::atomic-rule-definition.md`](aibdd-core::atomic-rule-definition.md) — Atomic Rule semantic 判定
   2.2 LOAD REF [`references/verification-semantics-presets.md`](references/verification-semantics-presets.md) — 4 種 Rule preset（locator / visual-state / route / API-binding）句型樣板
   2.3 LOAD REF [`references/userflow-rule-coverage.md`](references/userflow-rule-coverage.md) — Rule coverage matrix（happy / error / state-transition / a11y / cross-actor）

3. `$rule_derive` = MARK "derive atomic rules per UIVerbBinding via RP 04-fe-atomic-rules"
   3.1 `$atomic_rule_draft_raw` = THINK per [`reasoning/discovery-uiux/04-fe-atomic-rules.md`](reasoning/discovery-uiux/04-fe-atomic-rules.md), input={ui_verb_bindings: `$$discovery_bundle.frontend_lens.ui_verb_bindings`, anchors: `$$discovery_bundle.frontend_lens.anchor_candidates`, uat_flows: `$$discovery_bundle.uat_flows`, has_ui_ops: `$has_ui_ops`}
   3.2 LOOP per `$rule` in `$atomic_rule_draft_raw.items`
       3.2.1 ASSERT `$rule.ui_verb` ∈ UI verb catalog enum
       3.2.2 ASSERT `$rule.anchor.accessible_name` 為 source-quote-verbatim
       3.2.3 ASSERT `$rule.verification_mode` ∈ {locator, visual-state, route, api-binding}
       3.2.4 IF any assertion fails:
             3.2.4.1 EMIT "atomic rule `${$rule.id}` 違反 ui_verb / anchor / verification_mode 規約" to user
             3.2.4.2 STOP
       END LOOP

4. `$coverage_check` = MARK "check coverage matrix gaps and fire Seam C clarify-loop if needed"
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

5. `$rule_bundle` = MARK "assemble atomic rule bundle with features index"
   5.1 `$$atomic_rule_draft` = DERIVE 由 `$atomic_rule_draft_raw.items` + `$coverage_matrix` 組成的 atomic rule bundle，含 features index（每個 has-ui op 一個 feature）
   5.2 ASSERT length(`$$atomic_rule_draft.features`) == length(`$has_ui_ops`)
   5.3 IF assertion fails:
       5.3.1 EMIT "feature index 與 has-ui ops 數量不一致；可能 RP 04 漏推" to user
       5.3.2 STOP

### Phase 4 — FORM .activity + .feature skeleton via DELEGATE
> produces: `$$artifact_bundle`

1. `$open_q_gate` = MARK "assert no open questions remain from Phase 2/3 before writing files"
   1.1 ASSERT length(`$$discovery_bundle.uat_flows.clarify_payload.questions`) == 0
   1.2 ASSERT length(`$$discovery_bundle.frontend_lens.clarify_payload.questions`) == 0
   1.3 ASSERT length(`$$atomic_rule_draft.clarify_payload.questions`) == 0
   1.4 IF any assertion fails:
       1.4.1 EMIT "Phase 2/3 仍有未解 question；禁止落檔" to user
       1.4.2 STOP

2. `$activity_form` = MARK "delegate /aibdd-form-activity per Activity model with 2-retry guard"
   2.1 LOOP per `$am` in `$$activity_models.items`
       2.1.1 `$activity_target_path` = COMPUTE `${ACTIVITIES_DIR}/${$am.slug}.activity`
       2.1.2 `$activity_report` = DELEGATE `/aibdd-form-activity`，附上 target_path=`$activity_target_path`, format=".activity", mode="overwrite", reasoning.activity_analysis=`$am`
       2.1.3 IF `$activity_report.status != completed`:
             2.1.3.1 `$activity_retry` = DELEGATE `/aibdd-form-activity`，附上同一份題組
             2.1.3.2 IF `$activity_retry.status != completed`:
                   2.1.3.2.1 EMIT "aibdd-form-activity 失敗兩次（${$am.slug}）；停止本輪 Discovery-UIUX" to user
                   2.1.3.2.2 STOP
       END LOOP

3. `$feature_form` = MARK "delegate /aibdd-form-feature-spec per has-ui op, enforce flat target path"
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

4. `$artifact_check` = MARK "final completeness check: features + activities + gap report presence"
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
| 6 | `check_uiux_intent_alignment.py` | raw idea 提到的 UX 元素必須有對應 frontend artifact unit 或顯式 GAP entry；違規記為 GAP，不阻擋通關 |
| 7 | `check_no_be_mutation_leak.py` | clean artifact + GAP report 不得含 `references/be-gap-handling.md` §3 forbidden phrase（modify BE / 改 BE / patch BE 等） |

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
| `UIUX_API_YML_MIRROR_PRESENT` | `${SPECS_ROOT_DIR}/${TLB.id}/contracts/api.yml` 存在且旁檔 `.source-hash` 與 sibling BE 來源 sha256 一致（Phase 1 §6 落地；下游 `nextjs-storybook-cucumber-e2e` pre-red §3.0 依賴） |
| `UIUX_INTENT_REPORT_PRESENT` | `${PLAN_REPORTS_DIR}/discovery-uiux-intent.md` 存在且無 `Open Intent Questions` 殘留；含 raw idea verbatim block + alignment_matrix |
| `UIUX_INTENT_ALIGNMENT` | raw idea 提到的 UX 元素皆有對應 frontend artifact unit（feature / activity）或在 GAP section 顯式列出 |
| `UIUX_INTENT_NO_LEAK` | clean artifact 與所有 report 不得殘留 `CiC(INT: ...)` |
| `UIUX_BE_GAP_REPORT_PRESENT` | `${PLAN_REPORTS_DIR}/discovery-uiux-be-gap.md` 存在且無 `Open BE Supplementation Questions` 殘留；終稿含 `## BE Gaps Resolved (FE-side)` + `## BE Gaps Forwarded` |
| `UIUX_NO_BE_MUTATION_LEAK` | clean artifact + GAP report + classification reasoning 不得含 `references/be-gap-handling.md` §3 forbidden phrase blacklist |
| `UIUX_INTENT_SCOPE_BINDING` | `$$fe_intent_bundle.scope_decisions` 每筆對應到 classification.items 的同 op_id；classification.intent_trace.decision == exclude 時 classification ≠ has-ui |

**Failure contract**: violations 不得透過弱化 checklist 來 patch；fail 時返回 Phase 4 §1（落檔重做）並帶回原始 inputs。

#### 5.C 合併 verdict 迴圈

1. `$quality_loop` = MARK "run quality gate remediation loop (max 5 rounds)"
   1.1 LOOP quality gate remediation (max 5)
       1.1.1 `$sticky_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/grep_sticky_notes.py ${SPECS_ROOT_DIR}`
       1.1.2 `$actor_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/check_actor_legality.py ${$args_abs}`
       1.1.3 `$phase_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/check_discovery_phase.py ${$args_abs}`
       1.1.4 `$operation_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/check_operation_wise.py ${$args_abs} --constitution ${BDD_CONSTITUTION_PATH}`
       1.1.5 `$alignment_out` = TRIGGER `python3 ${PROJECT_ROOT}/.claude/skills/aibdd-discovery/scripts/check_raw_artifact_alignment.py ${$args_abs}`
       1.1.6 `$intent_alignment_out` = TRIGGER `python3 ${$$skill_dir}/scripts/check_uiux_intent_alignment.py ${$args_abs}`
       1.1.7 `$be_mutation_leak_out` = TRIGGER `python3 ${$$skill_dir}/scripts/check_no_be_mutation_leak.py ${$args_abs}`
       1.1.8 `$semantic_verdict` = DELEGATE 獨立 semantic subagent，rubric=Phase 5 §5.B table，input={discovery_bundle: `$$discovery_bundle`, atomic_rule_draft: `$$atomic_rule_draft`, artifact_bundle: `$$artifact_bundle`, fe_intent_bundle: `$$fe_intent_bundle`, be_gap_findings: `$$be_gap_findings`}
       1.1.9 `$$quality_verdict` = PARSE 所有 gate 輸出的合併 verdict
       1.1.10 BRANCH `$$quality_verdict.ok` ? GOTO #5.2.1 : GOTO #4.2.1
       END LOOP

2. `$gate_hard_stop` = MARK "hard stop — failure contract: 5 rounds exhausted"
   2.1 EMIT "Quality gate 連續 5 輪仍未通過；違反 Failure contract 禁止弱化 checklist" to user
   2.2 STOP

#### 5.D 殘留 clarify sweep

1. `$residual_sweep` = MARK "run residual clarification sweep after all gates pass"
   1.1 `$$clarify_report` = THINK per [`reasoning/discovery-uiux/05-userflow-clarification-dimensions.md`](reasoning/discovery-uiux/05-userflow-clarification-dimensions.md), input={discovery_bundle: `$$discovery_bundle`, artifact_bundle: `$$artifact_bundle`, quality_verdict: `$$quality_verdict`}
   1.2 BRANCH length(`$$clarify_report.questions`) == 0 ? GOTO #6.1 : GOTO #5.5.2.1

2. `$residual_delegate` = MARK "delegate residual questions to /clarify-loop; re-run gates if files changed"
   2.1 WRITE `${PLAN_REPORTS_DIR}/discovery-uiux-residual-clarify.md` ← draft residual sweep anchor file
   2.2 [USER INTERACTION] `$residual_clarify` = DELEGATE `/clarify-loop`，附上 `$$clarify_report.questions` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-uiux-residual-clarify.md`
   2.3 WAIT for `$residual_clarify`
   2.4 IF `$residual_clarify.status == incomplete`:
       2.4.1 EMIT "殘留 clarify 階段未完成；請補完題組後重跑" to user
       2.4.2 STOP
   2.5 BRANCH `$residual_clarify.files_changed` is non-empty ? GOTO #5.3.1.1 : GOTO #6.1

### Phase 6 — EMIT REPORT
> produces: (none)

1. `$report_draft` = MARK "draft final Discovery-UIUX summary report"
   1.1 LOAD REF [`aibdd-core::report-contract.md`](aibdd-core::report-contract.md) — 對外報告的語氣與必要欄位
   1.2 `$summary` = DRAFT 最終 Discovery-UIUX 報告 ← `$$artifact_bundle`, `$$discovery_bundle`, `$$quality_verdict`, `$$clarify_report`；訊息包含 has-ui / no-ui 統計、coverage matrix 摘要、GAP report pointer、verification mode 分布、下一步建議跑 `/aibdd-plan`

2. `$emit_report` = MARK "emit report to user with fallback write"
   2.1 EMIT `$summary` to user
   2.2 IF EMIT 失敗:
       2.2.1 WRITE `${SPECS_ROOT_DIR}/.discovery-uiux-report.md` ← `$summary`
       2.2.2 STOP

## §3 CROSS-REFERENCES

- 由 `/aibdd-discovery-uiux` command 觸發（root entry，frontend TLB 場景取代 `/aibdd-discovery`）
- 下游 contract 鏡像責任：Phase 1 §6 把 sibling BE `contracts/api.yml` 鏡像進 FE `${SPECS_ROOT_DIR}/${TLB.id}/contracts/api.yml` 並寫 `.source-hash`；`nextjs-storybook-cucumber-e2e` template pre-red §3.0 freshness gate 依賴此鏡像
- DELEGATE `/aibdd-form-activity` + `/aibdd-form-feature-spec` — 落檔 formulation skills
- DELEGATE `/clarify-loop` — 7 個觸發點：missing-field（UIUX_BACKEND_BOUNDARY_ID）/ Seam 0' BE-gap FE-side supplementation（Phase 2 §3）/ Seam 0 FE intent（Phase 2 §4）/ Seam A classification（Phase 2 §6）/ Seam B uat-flow+frontend-lens（Phase 2 §8）/ Seam C atomic-rule coverage（Phase 3）/ Phase 5 殘留 sweep；題組沿用既有 schema，每次呼叫前必先落 draft 檔（File-first invariant）。Seam 0' 題型必為 FE-side supplementation；禁 BE-mutation 選項（[`references/be-gap-handling.md`](references/be-gap-handling.md) §3 黑名單）
- 下游：`/aibdd-plan` 進行 technical plan / DSL proposal planning；frontend 場景常接 `/aibdd-uiux-design` 做視覺探索後再 `/aibdd-plan`；視覺探索可消費 `$$fe_intent_bundle.brand_seed` 作為起點
- 共用 scripts（reuse aibdd-discovery）：`kickoff_path_resolve.py` / `bind_plan_package.py` / `grep_sticky_notes.py` / `check_actor_legality.py` / `check_discovery_phase.py` / `check_operation_wise.py` / `check_raw_artifact_alignment.py`
- 本 skill 私有 scripts：`check_uiux_intent_alignment.py` / `check_no_be_mutation_leak.py`
- Registry entry 樣板：`assets/registry/entry.yml`
