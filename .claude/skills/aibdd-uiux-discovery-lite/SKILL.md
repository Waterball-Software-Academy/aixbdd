---
name: aibdd-uiux-discovery-lite
description: 從 /aibdd-discovery 產出機械推導 happy-path-only 視覺 brief：只納入 .feature 明確提到的畫面，或沒有明確畫面時每個 feature 的第一條 happy/success Scenario；只畫 primary/canonical 狀態，不展開錯誤、拒絕、loading、hover/active 等全狀態矩陣。emit design/uiux-prompt.md + design/style-profile.yml，可交給 /aibdd-uiux-draw 產 minimal design.pen。TRIGGER when 使用者下 /aibdd-uiux-discovery-lite、想先畫 happy path、MVP 視覺草圖、或覺得 /aibdd-uiux-discovery 畫太多情況。SKIP when 需要完整 state coverage、錯誤/空狀態設計、或 feature 未完成。
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-uiux-discovery-lite

Happy-path 視覺探索規劃器｜從 `/aibdd-discovery` 產物推導 **feature-mentioned screens only** 的最小 Pencil brief。它保留下游需要的三個合約 section（`COMPONENT CATALOG` / `FRAME COMPOSITION TABLE` / `ANCHOR NAME TABLE`），但把 component state 收斂成 primary/canonical 狀態，避免完整 `/aibdd-uiux-discovery` 的 component × state 展開造成畫面爆炸。

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
  - path: references/lite-selection-rules.md
    purpose: happy-path / feature-mentioned screen 選取規則、component/state 收斂規則、輸出 schema 與 invariants
  - path: references/lite-clarify-axes-catalog.md
    purpose: lite 版只問必要澄清軸：scope confirmation / style tokens / layout copy / breakpoint a11y
  - path: references/anchor-naming-rules.md
    purpose: accessible name 命名規則；沿用 component-keyed anchor contract，但只針對 lite scope 內的 interactive components
  - path: references/lite-prompt-sections.md
    purpose: assets/templates/uiux-prompt.template.md 各 section 填值來源表與 lite ASSERT 條件
  - path: assets/templates/uiux-prompt.template.md
    purpose: lite Pencil brief template；保留 downstream-required section names，但要求只畫 primary state 與 selected frames
  - path: assets/templates/style-profile.template.yml
    purpose: lite design token profile template；與 full discovery 相同輸出路徑與下游讀取契約
```

## §2 SOP

> 閱讀規則：主 item 只做摘要；要執行的內容一律編成子步驟。未編號縮排只保留給條件說明 / branch label / 補充註解。

### Phase 1 — LOAD discovery truth
> 交付：`$$runtime_context`、`$$discovery_bundle`

1. 把目前 skill 的執行設定與 discovery 產出讀齊，缺則 STOP 引導使用者跑前置 skill。
   1.1 `$$skill_dir` = COMPUTE 目前 skill 目錄
   1.2 LOAD REF [`aibdd-core::spec-package-paths.md`](aibdd-core::spec-package-paths.md) — boundary-aware 路徑規則
   1.3 `$args_path` = COMPUTE `${workspace_root}/.aibdd/arguments.yml`
   1.4 `$args_exists` = MATCH path_exists(`$args_path`)
   1.5 IF `$args_exists` == false:
       1.5.1 EMIT "${$args_path} 不存在；本 skill 需要 kickoff 後再執行，請先跑 /aibdd-kickoff 建立 arguments.yml" to user
       1.5.2 STOP
   1.6 `$$runtime_context` = READ `$args_path` 並 PARSE 出 `FEATURE_SPECS_DIR`、`ACTIVITIES_DIR`、`SPECS_DIR`、`current_package_slug`、`TLB`（target leaf boundary）

2. 確認 discovery 產物存在，否則停止。
   2.1 `$spec_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/spec.md`
   2.2 `$activities` = COMPUTE list of `${ACTIVITIES_DIR}/**/*.activity`
   2.3 `$features` = COMPUTE list of `${FEATURE_SPECS_DIR}/**/*.feature`
   2.4 ASSERT `$spec_path` exists ∧ length(`$activities`) ≥ 1 ∧ length(`$features`) ≥ 1
   2.5 IF assertion fails:
       2.5.1 EMIT "discovery 產物缺失；請先跑 /aibdd-discovery" to user
       2.5.2 STOP

3. TLB 必須是 frontend；後端 boundary 直接終止。
   3.1 IF `$$runtime_context.TLB.role` ≠ "frontend":
       3.1.1 EMIT "目前 TLB 不是 frontend，aibdd-uiux-discovery-lite 不適用" to user
       3.1.2 STOP

4. 把 discovery 產物讀進 bundle。
   4.1 `$spec` = READ `$spec_path`
   4.2 `$activity_files` = READ all paths in `$activities`
   4.3 `$feature_files` = READ all paths in `$features`
   4.4 `$$discovery_bundle` = DERIVE struct{spec, activities, features} from above

### Phase 2 — SELECT lite visual scope
> 交付：`$$lite_scope`、`$$component_inventory`、`$$frame_composition`、`$$anchor_candidates`

1. 從 `.feature` 明確畫面描述選 scope；沒有明確畫面時退回每個 feature 的 happy/success scenario。
   1.1 `$explicit_screens` = DERIVE screen candidates from `$$discovery_bundle.features` per [`references/lite-selection-rules.md`](references/lite-selection-rules.md) §1
   1.2 `$happy_scenarios` = DERIVE happy scenario candidates from `$$discovery_bundle.features` per [`references/lite-selection-rules.md`](references/lite-selection-rules.md) §2
   1.3 `$$lite_scope` = DERIVE selected visual scope per [`references/lite-selection-rules.md`](references/lite-selection-rules.md) §3
   1.4 ASSERT length(`$$lite_scope.selected_frames`) ≥ 1
   1.5 IF assertion fails:
       1.5.1 EMIT "找不到 feature 明確提到的畫面，也找不到可判定的 happy path scenario；請先補 .feature 的畫面或 happy scenario" to user
       1.5.2 STOP

2. 只從 `$$lite_scope` 中的 selected steps 抽 component candidate。
   2.1 `$component_candidates` = DERIVE component candidates ← `$$lite_scope.selected_steps` per [`references/lite-selection-rules.md`](references/lite-selection-rules.md) §4
   2.2 ASSERT 每個 selected frame 至少對應 1 個 component candidate 或標記為 `visual_shell_only`
   2.3 IF assertion fails:
       2.3.1 EMIT "lite scope 中有 frame 找不到可視元件；請檢查 .feature 是否只描述了純系統規則" to user
       2.3.2 STOP

3. 對每個 component 只保留 primary state；不展開錯誤、拒絕、loading、hover、active。
   3.1 `$$component_inventory` = DERIVE lite component inventory from `$component_candidates` per [`references/lite-selection-rules.md`](references/lite-selection-rules.md) §5
   3.2 ASSERT every `$$component_inventory[*].states` == one of {`idle`, `filled`, `populated`, `visible`, `selected`, `open`, `pristine`, `primary`}
   3.3 IF assertion fails:
       3.3.1 EMIT "lite component inventory 混入非 primary state；請改跑 full /aibdd-uiux-discovery 或重新收斂 scope" to user
       3.3.2 STOP

4. 依 selected frame 組 frame composition；每 frame 只保留一組 canonical state combo。
   4.1 `$$frame_composition` = DERIVE lite frame composition map from `$$lite_scope` + `$$component_inventory` per [`references/lite-selection-rules.md`](references/lite-selection-rules.md) §6
   4.2 ASSERT 每個 frame 對應 ≥ 1 條 `.feature` Scenario/Rule ∧ uses_components 非空
   4.3 ASSERT 每個 frame.uses_components[*].component_id ∈ `$$component_inventory[*].id`
   4.4 IF any assertion fails:
       4.4.1 EMIT "lite frame composition 與 component inventory 命名空間不一致，或 frame 沒有 feature 來源" to user
       4.4.2 STOP

5. 從 lite component candidate 抽 anchor name 候選。
   5.1 `$$anchor_candidates` = DERIVE accessible-name candidates from `$$component_inventory` where role ∈ {button, link, textbox, heading, listitem, tab, menuitem} per [`references/anchor-naming-rules.md`](references/anchor-naming-rules.md) §1

### Phase 3 — DRAFT lite clarification axes
> 交付：`$$clarify_payload`

1. 只產生 lite 必要澄清題；不問 full state matrix / per-state interaction。
   1.1 `$axes` = DRAFT lite axes per [`references/lite-clarify-axes-catalog.md`](references/lite-clarify-axes-catalog.md)
   1.2 `$axes` = EDIT `$axes` ← attach `$$lite_scope` / `$$component_inventory` / `$$frame_composition` / `$$anchor_candidates` as context

2. 組成 clarify-loop payload schema。
   2.1 `$$clarify_payload` = RENDER clarify-loop payload, vars={round_purpose: "aibdd-uiux-discovery-lite happy-path visual scope", questions: `$axes`, update_mode_hint: "sync"}
   2.2 ASSERT length(`$$clarify_payload.questions`) ≤ 8

### Phase 4 — DELEGATE /clarify-loop
> 交付：`$$clarify_resolved`

1. 把 payload 丟給 clarify-loop，等回 resolved answers。
   1.1 [USER INTERACTION] `$clarify_out` = DELEGATE `/clarify-loop` with `$$clarify_payload`
   1.2 WAIT for `$clarify_out`
   1.3 `$$clarify_resolved` = PARSE `$clarify_out`, schema=resolved-answers

2. 完整性檢查；缺答的軸重跑澄清。
   2.1 `$missing_axes` = DERIVE 未回答的 required lite axes from `$$clarify_resolved` per [`references/lite-clarify-axes-catalog.md`](references/lite-clarify-axes-catalog.md) §6
   2.2 IF `$missing_axes` non-empty:
       2.2.1 EMIT "still missing lite axes: ${$missing_axes}" to user
       2.2.2 GOTO #3.1

### Phase 5 — RENDER lite Pencil prompt + style profile + scope audit
> 交付：`$$prompt_path`、`$$profile_path`、`$$scope_path`

1. 載入 lite prompt template，依 selected scope + clarify 回填值填值。
   1.1 `$tmpl` = READ [`assets/templates/uiux-prompt.template.md`](assets/templates/uiux-prompt.template.md)
   1.2 `$prompt` = RENDER `$tmpl`, vars=`$$clarify_resolved` ⊕ `$$lite_scope` ⊕ `$$component_inventory` ⊕ `$$frame_composition` ⊕ `$$anchor_candidates` per [`references/lite-prompt-sections.md`](references/lite-prompt-sections.md)

2. 載入 style-profile template；專責 tokens / breakpoints / fonts / motion。
   2.1 `$profile_tmpl` = READ [`assets/templates/style-profile.template.yml`](assets/templates/style-profile.template.yml)
   2.2 `$profile` = RENDER `$profile_tmpl`, vars=`$$clarify_resolved` ⊕ {mode: "lite-happy-path"}

3. 渲染 scope audit，記錄為何只選這些畫面。
   3.1 `$scope_audit` = RENDER YAML audit ← `$$lite_scope`, `$$component_inventory`, `$$frame_composition`

4. 驗收條件 hard check：先 ASSERT 再落檔。
   4.1 ASSERT `$prompt` contains `MODE: lite-happy-path`
   4.2 ASSERT `$prompt` contains non-empty `## COMPONENT CATALOG` section per [`references/lite-prompt-sections.md`](references/lite-prompt-sections.md) §3
   4.3 ASSERT `$prompt` contains non-empty `## FRAME COMPOSITION TABLE` section per same §3
   4.4 ASSERT `$prompt` contains non-empty `## ANCHOR NAME TABLE` section per same §3
   4.5 ASSERT `$prompt` does not contain `rejected.` ∧ does not contain `error.` ∧ does not contain `loading` unless those words appear in `$$lite_scope.selected_steps`
   4.6 ASSERT FRAME COMPOSITION TABLE 內 `uses` 欄位引用的每個 component id 都在 COMPONENT CATALOG 中出現
   4.7 IF any assertion fails:
       4.7.1 EMIT "lite prompt render 不完整，或混入非 happy-path state；準備重 render" to user
       4.7.2 GOTO #5.1.1

5. 落檔（design/ 目錄）。
   5.1 `$$prompt_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/design/uiux-prompt.md`
   5.2 `$$profile_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/design/style-profile.yml`
   5.3 `$$scope_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/design/uiux-scope-lite.yml`
   5.4 CREATE `${SPECS_DIR}/${current_package_slug}/design/`
   5.5 WRITE `$$prompt_path` ← `$prompt`
   5.6 WRITE `$$profile_path` ← `$profile`
   5.7 WRITE `$$scope_path` ← `$scope_audit`

### Phase 6 — EMIT REPORT
> 交付：(none)

1. 整理結案訊息給 user。
   1.1 `$summary` = DRAFT report ← `$$prompt_path`, `$$profile_path`, `$$scope_path`, count(`$$lite_scope.selected_frames`), count(`$$component_inventory`), count(`$$anchor_candidates`), 語言=zh-TW；訊息點出「lite：只畫 feature 明確提到 / happy path 畫面；每個 component 只畫 primary/canonical state」
   1.2 EMIT `$summary` to user

2. 給 user 明確的下一步動作。
   2.1 `$pen_target_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/design.pen`
   2.2 `$handoff_msg` = DRAFT 下一步指引 ← `$$prompt_path`, `$pen_target_path`, 語言=zh-TW, 內容必含：
       - 跑 `/aibdd-uiux-draw` 可讀同一份 `${$$prompt_path}` + `${$$profile_path}`；因 brief 是 lite mode，draw 只應照 prompt 畫 selected frames + primary states
       - 若想補錯誤 / 空狀態 / loading / rejected 狀態，再改跑 `/aibdd-uiux-discovery` full 版重產 brief
       - 不論走 lite 或 full，下一步都跑 `/aibdd-plan`；plan 從 package root 的 `design.pen` 萃取 I4 anchor / DSL L1 / contract
   2.3 EMIT `$handoff_msg` to user

## §3 CROSS-REFERENCES

- `/aibdd-discovery` — 上游；產出 spec.md / activities / features / atomic-rules 為本 skill 的 INPUT SSOT
- `/aibdd-uiux-discovery` — full 版；需要完整 component state matrix / error state coverage 時改用它
- `/clarify-loop` — DELEGATE 對象；本 skill 只問 lite 必要軸
- `/aibdd-uiux-draw` — 直接下游；讀 `design/uiux-prompt.md` + `design/style-profile.yml`，依 prompt 的 lite mode 產 `.pen`
- `/aibdd-plan` — 後續下游；從 package root 讀 `design.pen` 萃取 I4 anchor / DSL L1 / contract
