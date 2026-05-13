---
description: 當使用者只有 raw idea，想先把需求收斂成 boundary-aware 的 discovery 產物時使用。需求分析主入口（root planner）：先對 raw idea × target boundary full truth 做 sourcing，產出 `reports/discovery-sourcing.md` 與 `spec.md` summary；接著 DERIVE late-bind 的 target functional package slug（`packages/NN-…`／寫回 `arguments.yml`）並 reresolve `${FEATURE_SPECS_DIR}`/`${ACTIVITIES_DIR}`；再收斂 flow 與 atomic rules 草稿；DELEGATE `/aibdd-form-activity` 落 Activity Diagrams、`/aibdd-form-feature-spec` 落 Feature Rules 骨架（@ignore、無 Examples）。Scope 只到 external flow 與 atomic rule 草擬，不做 entity、BDD examples、service contract。抽象軸：動詞（行為／事件／規則）。產物路徑以 `/aibdd-discovery` reresolve 後的 boundary-aware `${ACTIVITIES_DIR}` / `${FEATURE_SPECS_DIR}` 為準（見 `aibdd-core::spec-package-paths.md`）。
metadata:
  source: project-level dogfooding
  user-invocable: true
name: aibdd-discovery
---

# aibdd-discovery

根規劃器｜將訪談需求先和 target boundary truth 對齊 impact scope，再 **bind** 選定的 functional package slug（落地 `packages/NN-*`）並 reresolve 行為 truth 路徑，最後 DELEGATE 至 formulation skills 落檔（spec artifacts）。

<!-- VERB-GLOSSARY:BEGIN — auto-rendered from programlike-skill-creator/references/verb-cheatsheet.md by render_verb_glossary.py; do not hand-edit -->

## §2 SOP

> 閱讀規則：主 item 只做摘要；需要執行的內容一律編成子步驟。未編號縮排只保留給條件說明、branch label 或補充註解。

### Phase 1 — 先把這次 Discovery 需要的設定準備好
> 交付：`$$runtime_context`、`$$skill_dir`

1. 先綁定目前 skill 目錄，再讀這次 Discovery 會用到的設定檔與目前 skill 執行環境，整理成本階段共用的執行設定。
   1.1 `$$skill_dir` = COMPUTE 目前 skill 目錄路徑
   1.2 LOAD REF `references/contracts/io.md` — 確認哪些欄位現在就要有，哪些欄位可以等 Phase 2 再綁定
   1.3 LOAD REF `aibdd-core::spec-package-paths.md` — 確認 boundary-aware 路徑規則
   1.4 `$$runtime_context` = READ `${arguments_yml_path}` + 目前的 skill 執行環境

2. 檢查必要欄位是否齊全；如果缺欄，就先交給 `/clarify-loop` 補齊，補完後回來重讀一次設定。
   2.1 IF 必要欄位缺失:
       2.1.1 [USER INTERACTION] `$clarify` = DELEGATE `/clarify-loop`，附上缺欄題組
       2.1.2 WAIT for `$clarify`
       2.1.3 GOTO #1.1

3. 確認 activity 副檔名是不是 `.activity`；如果不是，就直接停止，不往下跑。
   3.1 IF `ACTIVITY_EXT != ".activity"`:
       3.1.1 EMIT "ACTIVITY_EXT 必須是 .activity" to 使用者
       3.1.2 STOP

4. 讀 BDD 憲法裡的檔名規則，確認這次命名軸是完整的；如果不完整，就先補齊再回來確認。
   4.1 LOAD REF `references/turn-discipline.md` — 對齊使用者回合的外顯訊號與狀態
   4.2 `$constitution` = READ `${BDD_CONSTITUTION_PATH}` §5.1
   4.3 `$$runtime_context` = PARSE 檔名軸並寫入 `$$runtime_context`
   4.4 IF 命名軸不完整:
       4.4.1 [USER INTERACTION] `$axes_clarify` = DELEGATE `/clarify-loop`，附上 BDD feature 檔名軸題組
       4.4.2 WAIT for `$axes_clarify`
       4.4.3 GOTO #1.4

5. 把這次真正要用的實際路徑展開出來；如果展開失敗，就直接告知並停止。
   5.1 `$args_abs` = COMPUTE `${arguments_yml_path}` 的絕對路徑（預設 `${workspace_root}/.aibdd/arguments.yml`）
   5.2 `$path_json` = TRIGGER `python3 "${$$skill_dir}/scripts/kickoff_path_resolve.py" "${$args_abs}"`
   5.3 IF 路徑展開失敗:
       5.3.1 EMIT "kickoff 路徑展開失敗" to 使用者
       5.3.2 STOP

6. 把設定、命名軸與已展開路徑整成一份執行設定，交給下一個 phase 使用。
   6.1 `$$runtime_context` = DERIVE 由設定、檔名軸與已展開路徑組成的最終執行設定

### Phase 2 — 先做 sourcing，再把流程與規則草圖收斂出來
> 交付：`$$discovery_bundle`

> **File-first invariant (Phase 2 全 Seam 適用)**：
> 任何 `[USER INTERACTION] DELEGATE /clarify-loop` 呼叫**之前**，必須先在對應 plan package / function package 下 **WRITE** 一份承載該輪題組的 artifact，並在 clarify-loop payload 附 `located_file_path` 指向該檔；待澄清題組必須同步寫進該檔的 `## Open <Stage> Questions` section。**禁止**在 in-memory `$payload` 持有題組直接 fire clarify-loop — 若無檔可錨，trunk doctrine 的 file-first 不成立、`specformula-fork` route 也無合法錨點。違反此 invariant 視為 SOP 缺陷，呼叫 `/skill-rca`。

1. 先判斷這次輸入是不是屬於 Discovery 該處理的範圍；如果根本不在這個軸上，就直接說明並停止。
   1.1 LOAD REF `references/relevance.md` — 判斷這次輸入是否落在流程／角色／規則範疇
   1.2 LOAD REF `reasoning/discovery/01-source-material.md` — 做第一輪素材來源收斂
   1.3 `$$discovery_bundle` = THINK 依 `$$runtime_context` 收斂第一輪 source material
   1.4 IF 不屬於 Discovery:
       1.4.1 EMIT "不在 Discovery 軸範疇（僅資料／內部分工／Examples／API-only）" to 使用者
       1.4.2 STOP

2. 在做任何 sourcing 提問前，先決定本輪 Discovery 要寫到哪一個 plan package — Seam 0 提問檔（draft sourcing report）就落在這個 plan package 底下。
   - new-discovery：DERIVE 一個全新的 plan package slug，CREATE 該目錄，回寫 `arguments.yml#CURRENT_PLAN_PACKAGE`，再重展開 plan-side 路徑。
   - reconcile：caller payload（`$$reconcile_context` 非空，由 `/aibdd-reconcile` DELEGATE 注入）— 沿用既有 `CURRENT_PLAN_PACKAGE`，不切新 package。
   2.1 `$caller_intent` = CLASSIFY `$$reconcile_context` as `new-discovery | reconcile`
       - reconcile：`$$reconcile_context` 為 non-empty map（含 `session_id`/`earliest_planner`/`cascade_chain`/`archive_path`）
       - new-discovery：otherwise（含使用者直接 invoke `/aibdd-discovery` 的所有情境）
   2.2 BRANCH `$caller_intent`
       new-discovery → GOTO #2.3
       reconcile     → GOTO #3.1   # 沿用既有 CURRENT_PLAN_PACKAGE，跳過 plan package binding；draft report 直接寫進既有 package
   2.3 `$plan_package_slug` = DERIVE 新 plan package slug
       - 命名格式：`NNN-<slug>`，NNN 為當前 `${SPECS_ROOT_DIR}` 下未占用的最小三位數（掃 `${SPECS_ROOT_DIR}/*/` 取最大 + 1，從 `001` 起跳；`000-kickoff-placeholder` 永不重用）
       - `<slug>` 由本輪 sourcing impact scope 摘要推得；可與 `TRUTH_FUNCTION_PACKAGE` 同名但不強制
       - **不得**偷渡 boundary id；**不得**沿用上一輪 plan package slug
   2.4 `$bind_plan_rc` = TRIGGER `python3 "${$$skill_dir}/scripts/bind_plan_package.py" "${$args_abs}" "${$plan_package_slug}"`
   2.5 IF `$bind_plan_rc != 0`:
       2.5.1 EMIT "`bind_plan_package.py` 執行失敗" to 使用者
       2.5.2 STOP
   2.6 `$path_json` = TRIGGER `python3 "${$$skill_dir}/scripts/kickoff_path_resolve.py" "${$args_abs}"`
   2.7 `$$runtime_context` = DERIVE 已重展開 plan-side 路徑後的執行設定（`PLAN_SPEC` / `PLAN_REPORTS_DIR` / `TASKS_MD` / `CURRENT_PLAN_PACKAGE` 全部對齊新 slug）
   2.8 IF `${CURRENT_PLAN_PACKAGE}` 重展開後仍指向 placeholder 或舊 plan package:
       2.8.1 EMIT "CURRENT_PLAN_PACKAGE 未切換到新 plan package；plan-side 路徑解析失敗" to 使用者
       2.8.2 STOP

3. **先落 draft sourcing report 與 draft `spec.md`**，把目前已知的 sourcing 與本輪要問的 Seam 0 題組一起寫進檔；這份 draft 是 Seam 0 clarify-loop 的 fork 錨點。
   3.1 LOAD REF `references/contracts/discovery-sourcing-report.md` — sourcing report 形狀；draft 階段允許 `## Open Sourcing Questions` section（final 階段必須清空，由 §5 finalize 處理）
   3.2 LOAD REF `reasoning/discovery/02-sourcing-clarify.md` — Seam 0 題組推導規則（lexical / demo-anchor 腦補檢測）
   3.3 LOAD REF `references/rules/hallucination-detection-checklist.md` — 共用腦補檢查表
   3.4 `$sourcing_clarify_payload` = THINK 從 `$$discovery_bundle.source_material_bundle` 整理 Seam 0 題組（每題含 id / kind / context / question / options / recommendation / recommendation_rationale）
   3.5 CREATE `${PLAN_REPORTS_DIR}`
   3.6 WRITE `${PLAN_REPORTS_DIR}/discovery-sourcing.md` ← 包含目前 evidence matrix / 初步 impact scope **以及 `## Open Sourcing Questions` 章節**（內容對齊 `$sourcing_clarify_payload`，含每題 id / 選項 / 推薦）的 draft sourcing report
   3.7 WRITE `${PLAN_SPEC}` ← Discovery Sourcing Summary draft（含 pointer 指向 `${PLAN_REPORTS_DIR}/discovery-sourcing.md` 與 Open Sourcing Questions 章節）

4. Draft 檔已落地後，再 fire Seam 0 clarify-loop，且 payload 必須 anchor 到 `${PLAN_REPORTS_DIR}/discovery-sourcing.md`。
   4.1 IF count(`$sourcing_clarify_payload.questions`) == 0：GOTO #5.1   # 沒有題就跳過 Seam 0，直接走 finalize
   4.2 [USER INTERACTION] `$sourcing_clarify_report` = DELEGATE `/clarify-loop`，附上 `$sourcing_clarify_payload` + `located_file_path = ${PLAN_REPORTS_DIR}/discovery-sourcing.md` + `located_anchor_section = "Open Sourcing Questions"`
   4.3 WAIT for `$sourcing_clarify_report`
   4.4 IF `$sourcing_clarify_report.status == incomplete`:
       4.4.1 EMIT "sourcing 階段的 clarify-loop 回 incomplete；draft report 留檔，請補完題組後重跑 #4.2" to 使用者
       4.4.2 STOP

5. Clarify 回答整合進 sourcing，re-WRITE 為 final report（移除 `Open Sourcing Questions` 章節，把答案併入 evidence matrix / decisions / impact scope）。
   5.1 `$$discovery_bundle` = THINK 把 `$sourcing_clarify_report.answers` 整合進 `$$discovery_bundle.source_material_bundle`
   5.2 WRITE `${PLAN_REPORTS_DIR}/discovery-sourcing.md` ← final sourcing report（**禁止保留** `Open Sourcing Questions` 章節；新增 `## Resolved Sourcing Decisions` 章節記錄每題答案 + reasoning）
   5.3 WRITE `${PLAN_SPEC}` ← final Discovery Sourcing Summary（pointer 對應 final report）

6. 決定這次要綁定的 functional package，回寫 `arguments.yml`，再重新展開一次 behavior 路徑；如果綁定或重展開失敗，就直接停止。
   - package slug 要從 impact scope 與 clarify 結果推得；**不得**偷渡 boundary id 直接選 package。
   - 如果真的推不出來，才用目前 plan package 名稱的 deterministic fallback。
   - reconcile 路徑下，如果上游 plan package 已經綁定 functional package，可以沿用而不重綁；本步驟仍 reresolve 確認路徑正確。
   6.1 `$function_package_slug` = DERIVE 這次要綁定的 package slug
   6.2 `$bind_rc` = TRIGGER `python3 "${$$skill_dir}/scripts/bind_truth_function_package.py" "${$args_abs}" "${$function_package_slug}"`
   6.3 IF `$bind_rc != 0`:
       6.3.1 EMIT "`bind_truth_function_package.py` 執行失敗" to 使用者
       6.3.2 STOP
   6.4 `$path_json` = TRIGGER `python3 "${$$skill_dir}/scripts/kickoff_path_resolve.py" "${$args_abs}"`
   6.5 IF `行為路徑已綁定` != true:
       6.5.1 EMIT "`arguments.yml` 在 bind 後仍缺少已綁定的 FEATURE_SPECS_DIR/ACTIVITIES_DIR" to 使用者
       6.5.2 STOP

7. 基於已確認的 impact scope，收斂 activity 分析；如果流程結構還有歧義，就先澄清，再回來重跑這一步。（**Seam A 亦適用 §Phase 2 File-first invariant**：fire `/clarify-loop` 前建議先把 activity-stage 題組與目前已知 uat flow 草圖落到 `${CURRENT_PLAN_PACKAGE}/.discovery-drafts/activity-analysis.md` 作為錨點；本 patch 暫不強制執行此寫檔，待後續另一輪 RCA 收尾。）
   7.1 LOAD REF `reasoning/discovery/03-activity-analyze.md` — 從來源素材與 impact scope 拆出 uat flows
   7.2 LOAD REF `references/rules/activity-variation-decomposition.md` — variation decomposition 的參考規則
   7.3 `$$discovery_bundle` = THINK 根據目前的 sourcing 結果收斂 activity 分析
   7.4 IF 流程結構仍有歧義:
       7.4.1 [USER INTERACTION] `$activity_clarify_report` = DELEGATE `/clarify-loop`，附上 `$$discovery_bundle.activity_analyses.clarify_payload`
       7.4.2 WAIT for `$activity_clarify_report`
       7.4.3 IF `$activity_clarify_report.status == incomplete`:
           7.4.3.1 EMIT "activity 階段的 clarify-loop 回 incomplete；請先修正再重跑 RP02" to 使用者
           7.4.3.2 STOP
       7.4.4 GOTO #2.7

7.5 推導 frontend axes 草稿（僅 TLB.role=="frontend" 啟動完整推導；其他 role 即時 short-circuit 為 null lens）；若 frontend-stage 仍有歧義（accessible_name 同義改寫 / anchor 自生 / backend verb 入侵 / role 黑名單），就先澄清，再回來重跑這一步。（**Seam C 亦適用 §Phase 2 File-first invariant**：fire `/clarify-loop` 前建議先把 frontend-stage 題組落到 `${CURRENT_PLAN_PACKAGE}/.discovery-drafts/frontend-axes.md` 作為錨點；本 patch 暫不強制執行此寫檔。）
   7.5.1 LOAD REF `reasoning/discovery/04b-frontend-axes.md` — 從 activity action 推 UI verb binding + anchor candidate + state axes hint
   7.5.2 LOAD REF `references/rules/frontend-rule-axes.md` — UI verb catalog / role mapping / anchor 命名規則 / boundary role gate
   7.5.3 `$frontend_lens` = THINK 根據 `$$discovery_bundle.source_material_bundle.target_boundary.role`、`$$discovery_bundle.activity_analyses` 與 `$$discovery_bundle.source_material_bundle.impact_scope` 推 frontend lens；TLB.role != "frontend" 時 SET null
   7.5.4 IF `$frontend_lens` is non-null AND `$frontend_lens.clarify_payload.questions` 非空:
       7.5.4.1 [USER INTERACTION] `$frontend_clarify_report` = DELEGATE `/clarify-loop`，附上 `$frontend_lens.clarify_payload`
       7.5.4.2 WAIT for `$frontend_clarify_report`
       7.5.4.3 IF `$frontend_clarify_report.status == incomplete`:
           7.5.4.3.1 EMIT "frontend axes 階段的 clarify-loop 回 incomplete；請先修正再重跑 RP04b" to 使用者
           7.5.4.3.2 STOP
       7.5.4.4 GOTO #2.7.5
   7.5.5 `$$discovery_bundle` = THINK 將 `$frontend_lens` 併入 discovery bundle（即使為 null 也保留欄位以利下游一致檢查）

8. 基於 activity 分析（必要時搭配 `$$discovery_bundle.frontend_lens`）收斂 atomic rule 草稿；如果規則層還有歧義，就先澄清，再回來重跑這一步。（**Seam B 亦適用 §Phase 2 File-first invariant**：fire `/clarify-loop` 前建議先把 atomic-stage 題組落到 `${CURRENT_PLAN_PACKAGE}/.discovery-drafts/atomic-rules.md` 作為錨點；本 patch 暫不強制執行此寫檔。）
   8.1 LOAD REF `reasoning/discovery/05-atomic-rules.md` — 從 activity 與來源素材（必要時 ⊕ frontend_lens）收斂 atomic rules
   8.2 LOAD REF `aibdd-core::atomic-rule-definition.md` — Atomic Rule 的判斷基準
   8.3 `$atomic_rule_draft` = THINK 根據 `$$discovery_bundle.activity_analyses` ⊕（`$$discovery_bundle.frontend_lens` 非空時）frontend lens 收斂 atomic rule 草稿；frontend lens 非空時每條 rule 必須帶 `ui_verb` 與 `anchor_hint`
   8.4 IF 規則層仍有歧義:
       8.4.1 [USER INTERACTION] `$atomic_clarify_report` = DELEGATE `/clarify-loop`，附上 `$atomic_rule_draft.clarify_payload`
       8.4.2 WAIT for `$atomic_clarify_report`
       8.4.3 IF `$atomic_clarify_report.status == incomplete`:
           8.4.3.1 EMIT "atomic 階段的 clarify-loop 回 incomplete；請先修正再重跑 RP03" to 使用者
           8.4.3.2 STOP
       8.4.4 GOTO #2.8

9. 把 sourcing、activity 分析、atomic rule 草稿和 formulation handoff 整成一份 discovery bundle；如果交棒欄位缺漏，就不能往下委派。
   9.1 `$$discovery_bundle` = DERIVE 由 sourcing、activity 分析、atomic rules 與 formulation handoff 組成的 discovery bundle
   9.2 IF `$$discovery_bundle.formulation_reasoning_package.exit_status != complete`:
       9.2.1 EMIT "交棒欄位缺漏；不得委派 formulation" to 使用者
       9.2.2 STOP

### Phase 3 — 把已收斂的 Discovery truth 落成 activity 與 feature 骨架
> 交付：`$$artifact_bundle`

1. 先確認 activity-stage 沒有留下未解問題；如果 Seam A 的問題還在，就先停下，不能寫檔。
   1.1 IF count(`$$discovery_bundle.activity_analyses.clarify_payload.questions`) > 0:
       1.1.1 EMIT "Activity-stage cic 未解決（Seam A questions 仍非空）；禁止寫檔／委派 formulation" to 使用者
       1.1.2 STOP

2. 逐個 modeled uat flow 落出 `.activity`；如果同一份 activity 連續失敗兩次，就停止這輪 Discovery。
   2.1 LOOP per `$activity_analysis` in `$$discovery_bundle.activity_analyses.items`
       2.1.1 IF `$activity_analysis.modeled != true`：CONTINUE
       2.1.2 `$activity_target_path` = RENDER 根據命名規則與已展開 activity 目錄得到的 `.activity` 路徑
       2.1.3 `$activity_report` = DELEGATE `/aibdd-form-activity`，附上 target_path=`$activity_target_path`, format=".activity", mode="overwrite", reasoning.activity_analysis=`$activity_analysis`
       2.1.4 IF `$activity_report.status != completed`:
           2.1.4.1 `$activity_retry_report` = DELEGATE `/aibdd-form-activity`，附上同一份題組
           2.1.4.2 IF `$activity_retry_report.status != completed`:
               2.1.4.2.1 EMIT "aibdd-form-activity 失敗兩次；停止本輪 Discovery" to 使用者
               2.1.4.2.2 STOP
   2.2 END LOOP

3. 確認所有 `modeled=true` 的 uat flow 都已經有對應的 `.activity` 檔。
   3.1 ASSERT every modeled uat flow has one `.activity`

4. 再逐個 feature 落出 rule-only `.feature` 骨架；這些 feature 必須直接寫在 resolved features dir 下，不得自行插入 domain 子目錄。
   4.1 LOOP per `$feature` in `$$discovery_bundle.formulation_reasoning_package.features`
       4.1.1 ASSERT `$feature.target_path` is flat under `${RESOLVED_FEATURES_DIR}`
       4.1.2 `$feature_report` = DELEGATE `/aibdd-form-feature-spec`，附上題組 {target_path: `$feature.target_path`, mode: "rule-only", folder_strategy: "flat", reasoning: `$$discovery_bundle.formulation_reasoning_package`}
       4.1.3 IF `$feature_report.status != completed`:
           4.1.3.1 EMIT `$feature.target_path` + `$feature_report.reason` to 使用者
           4.1.3.2 STOP
   4.2 END LOOP

5. 收尾檢查：所有應落的 Activity / Feature.Rule 都已落出，而且 formulation skill 沒有自己補腦缺欄。
   5.1 LOAD REF `references/rules/actor-legality.md` — 後面 gate 仍會用同一套角色合法性規則
   5.2 `$$artifact_bundle` = DERIVE 由 formulation 產物組成的 artifact bundle
   5.3 ASSERT no formulation skill filled missing reasoning fields on its own

### Phase 4 — 先做 gate，再決定能不能把這輪 Discovery 視為乾淨
> 交付：`$$quality_verdict`

#### 4.A Script gates

先跑 deterministic 的機械 gate。這些 gate 的目的不是替代判斷，而是先把明顯不合法的 artifact 擋下來。

| Script | 這一輪要擋的事 |
| --- | --- |
| `grep_sticky_notes.py` | clean artifact 內不得殘留未解的 `CiC(...)` |
| `check_actor_legality.py` | Activity actor 必須是 external user / third-party |
| `check_discovery_phase.py` | Discovery feature 必須維持 rule-only 形狀 |
| `check_operation_wise.py` | 先擋明顯檔名或 trigger 反模式 |
| `check_raw_artifact_alignment.py` | raw idea 與 artifact 對齊檢查；違規記為 GAP，不阻擋通關 |

#### 4.B Semantic gate

script gate 過後，再交給獨立 subagent 做 semantic gate；planner 自己不能 self-judge。

| rule_id | Requirement |
| --- | --- |
| `CIC_GAP_RESIDUAL` | clean artifact 內無 `CiC(GAP: ...)` 殘留 |
| `CIC_ASM_RESIDUAL` | clean artifact 內無 `CiC(ASM: ...)` 殘留 |
| `CIC_BDY_RESIDUAL` | clean artifact 內無 `CiC(BDY: ...)` 殘留 |
| `CIC_CON_RESIDUAL` | clean artifact 內無 `CiC(CON: ...)` 殘留 |
| `RULE_UNIT_COVERAGE` | 每條帶有規則意義的來源敘述，至少對應一個 artifact unit |
| `SOURCING_REPORT_SHAPE` | `reports/discovery-sourcing.md` 符合報告規約 |
| `SOURCING_NO_TRUTH_COPY` | sourcing report 與 `spec.md` summary 不複製 truth 內容 |
| `SOURCING_NO_DELTA_DIFF` | sourcing report 與 `spec.md` summary 不寫 delta / diff |
| `SPEC_SUMMARY_POINTER_COMPLETE` | `spec.md` 的 Discovery Sourcing Summary 有 report pointer |
| `IMPACT_SCOPE_FEEDS_DOWNSTREAM` | downstream 真的沿用同一份 impact scope |
| `ATOMIC_RULE_UNIT` | 每條 AtomicRule 保持原子性 |
| `OPERATION_WISE_FEATURE_FILE` | 每個 feature file 只對應一個 operation trigger |
| `ACTIVITY_ACTOR_EXTERNAL` | 每個 Activity actor 為 external user / third-party |
| `RULE_NO_EXAMPLE_LEAK` | example data 不得洩漏進 Discovery Rules |
| `ACTIVITY_STEP_ORDER_JUSTIFIED` | Activity step 順序必須有來源或使用者確認 |
| `ACTIVITY_SELF_CONTAINED_PATH` | 每個 Activity 都是完整 actor-entry → terminal 路徑 |
| `ACTIVITY_NO_FEATURE_INDEX` | Activity 不得退化成 feature 索引清單 |
| `ACTIVITY_BRANCH_TERMINAL_EXPLICIT` | 每個 branch 都要有 explicit terminal |
| `F1_HAPPY_PATH` | happy path 有 explicit Rules |
| `F2_EDGE_CASES` | edge / error path 有 Rules 或 explicit CiC markers |
| `F3_ACTOR_RULES` | 每個 Actor 都有對應的合法性 / 授權規則 |
| `F4_STATE_TRANSITIONS` | 重要 state transitions 有 Rules |
| `F5_TEMPORAL_RULES` | temporal constraints 為 explicit 或 boundary gap |
| `F6_CROSS_ENTITY_RULES` | cross-entity 互動不得被靜默丟掉 |

#### 4.C 合併 verdict

1. 用最多 5 輪的補救迴圈跑完 script gate 與 semantic gate；只要其中一輪全數通過，就進下一階段。
   1.1 LOOP quality gate remediation (max 5)
       1.1.1 `$sticky_out` = TRIGGER `python3 ${$$skill_dir}/scripts/grep_sticky_notes.py ${SPECS_ROOT_DIR}`
       1.1.2 `$actor_out` = TRIGGER `python3 ${$$skill_dir}/scripts/check_actor_legality.py ${$args_abs}`
       1.1.3 `$phase_out` = TRIGGER `python3 ${$$skill_dir}/scripts/check_discovery_phase.py ${$args_abs}`
       1.1.4 `$operation_out` = TRIGGER `python3 ${$$skill_dir}/scripts/check_operation_wise.py ${$args_abs} --constitution ${BDD_CONSTITUTION_PATH}`
       1.1.5 `$alignment_out` = TRIGGER `python3 ${$$skill_dir}/scripts/check_raw_artifact_alignment.py ${$args_abs}`
       1.1.6 `$semantic_report` = DELEGATE 獨立的 semantic gate，檢查 `$$discovery_bundle`、`$atomic_rule_draft`、`$$artifact_bundle`
       1.1.7 `$$quality_verdict` = PARSE 所有 gate 輸出的合併 verdict
       1.1.8 BRANCH `$$quality_verdict.ok` ? GOTO #5.1 : GOTO #3.1
   1.2 END LOOP

2. 如果連續 5 輪都還是沒過，就停下來，不允許靠放鬆 gate 規則硬過。
   2.1 EMIT "Quality gate 連續 5 輪仍未通過" to 使用者
   2.2 STOP

**Failure contract**：fail 時只能回 formulation 修 artifact；不得透過弱化 checklist 來 patch gate。

### Phase 5 — 看 clean artifact 還有沒有跨 artifact 殘留問題
> 交付：`$$clarify_report`

1. 當 deterministic 與 semantic gate 都先過一輪後，再做一次跨 artifact 的殘留 sweep。
   1.1 LOAD REF `reasoning/discovery/07-clarification-dimensions.md` — 專門掃 clean artifacts 後仍殘留的問題
   1.2 `$$clarify_payload` = THINK 根據 `$$discovery_bundle`、`$$artifact_bundle`、`$$quality_verdict` 整理殘留澄清題組

2. 如果沒有問題，就直接往報告階段走；如果有問題，就先確認這份題組對使用者來說是自然語言，而不是追蹤用中繼資訊。
   2.1 BRANCH count(`$$clarify_payload.questions`) == 0 ? GOTO #6.1 : GOTO #5.3

3. 把殘留問題交給 `/clarify-loop`；如果回來後真的改到了檔案，就回 gate 重新驗一次。
   3.1 [USER INTERACTION] `$$clarify_report` = DELEGATE `/clarify-loop`，附上 `$$clarify_payload`
   3.2 WAIT for `$$clarify_report`
   3.3 IF `$$clarify_report.status == incomplete`:
       3.3.1 EMIT "clarify-loop 題組不完整，或不是使用者可讀語言；請先重跑 clarification dimensions reasoning" to 使用者
       3.3.2 STOP

4. 判斷這輪 clarify 有沒有動到 artifact；有就回 gate，沒有就往報告走。
   4.1 BRANCH `$$clarify_report.files_changed` is non-empty ? GOTO #4.1 : GOTO #6.1

### Phase 6 — 對使用者匯報這輪 Discovery 的結果

1. 用使用者看得懂的語氣收斂這輪 Discovery 的成果、阻塞點與 clarify 結果。
   1.1 LOAD REF `aibdd-core::report-contract.md` — 對外報告的語氣與必要欄位
   1.2 `$summary` = DRAFT 最終 Discovery 報告，包含 Phase 5 的 `$$clarify_report` 狀態

2. 把報告送給使用者；如果當下送不出去，再寫入 fallback report。
   2.1 EMIT `$summary` to 使用者
   2.2 IF EMIT 失敗:
       2.2.1 WRITE `${SPECS_ROOT_DIR}/.discovery-report.md` ← `$summary`
       2.2.2 STOP

## §3 CROSS-REFERENCES

- 由 `/aibdd-discovery` command 觸發（root entry）；caller 也可為 `/aibdd-reconcile`（透過 DELEGATE 注入 `$$reconcile_context`）
- DELEGATE `/aibdd-form-activity` + `/aibdd-form-feature-spec`
- DELEGATE `/clarify-loop`（7 個觸發點：missing-field / filename axes 缺 / Seam 0 sourcing / Seam A activity / Seam C frontend axes（僅 TLB.role=="frontend"） / Seam B atomic / Phase 5 殘留 sweep；題組沿用既有 schema 不擴充，stage 資訊透過 question.context 傳遞；Seam 0 起所有 Phase 2 內 clarify-loop 呼叫必須先落 draft 檔，遵守 §Phase 2 File-first invariant）
- 下游：`/aibdd-plan` 進行 technical plan / DSL proposal planning；`/aibdd-spec-by-example-analyze` 進行 example 層分析
- 內部 scripts：
  - `scripts/bind_plan_package.py` — Phase 2 §2 new-discovery 路徑回寫 `CURRENT_PLAN_PACKAGE`（reconcile 路徑不呼叫）
  - `scripts/bind_truth_function_package.py` — Phase 2 §6 回寫 `TRUTH_FUNCTION_PACKAGE` 與 derived dirs（new-discovery + reconcile 都呼叫）
  - `scripts/kickoff_path_resolve.py` — 共用 path 展開器
- Registry entry 樣板：`assets/registry/entry.yml`
