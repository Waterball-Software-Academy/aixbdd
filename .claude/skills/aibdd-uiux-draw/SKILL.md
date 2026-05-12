---
name: aibdd-uiux-draw
description: 從 /aibdd-uiux-discovery 產出的 `design/uiux-prompt.md` + `design/style-profile.yml`，透過 Pencil MCP 自動繪 `.pen`：先 set design tokens 進 document variables，再逐 component scene 畫全 state 變體，再依 frame composition table 組裝 frame scene，並透過 snapshot + screenshot 自檢；偵錯 loop ≤ 3 輪，最後 export 到 `${SPECS_DIR}/${current_package_slug}/design.pen`（package root）。TRIGGER when 使用者下 /aibdd-uiux-draw、或 /aibdd-uiux-discovery 結尾選路徑 A（自動繪製）。SKIP when 上游 brief 缺失（COMPONENT CATALOG / FRAME COMPOSITION / ANCHOR NAME TABLE 任一 ASSERT 不過）、Pencil MCP 不可用、或 user 明示要手動畫（路徑 B）。
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-uiux-draw

Pencil MCP 自動繪製器（component-first）｜把 `aibdd-uiux-discovery` 產的 brief 翻成 `.pen` design file。每個 component 一個 scene 含全 state 變體；每個 frame 一張組合圖（canonical state combo）；不展開 frame × state，因為下游 `<ComponentId>.stories.tsx` 才是 binding anchor SSOT。

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
> | ASK | I | 問 user 等回應（仍配 `[USER INTERACTION]` tag）；**唯一允許 yield turn 給 user 的 verb** |
<!-- VERB-GLOSSARY:END -->

## §1 REFERENCES

```yaml
references:
  - path: references/mcp-binding-rules.md
    purpose: prompt section ↔ Pencil MCP tool call 對照表（COMPONENT CATALOG → batch_design per component scene；DESIGN TOKENS → set_variables；FRAME COMPOSITION TABLE → batch_design per frame scene；ANCHOR NAME TABLE → 文字節點驗證）
  - path: references/self-correction-budget.md
    purpose: 自檢 / 自修 loop 規則 — snapshot_layout + get_screenshot 後的 grading 規約、失敗類型 → 修補手段對應、loop budget = 3
```

## §2 SOP

> 閱讀規則：主 item 只做摘要；要執行的內容一律編成子步驟。未編號縮排只保留給條件說明 / branch label / 補充註解。

### Phase 1 — LOAD brief + verify upstream truth
> 交付：`$$runtime_context`、`$$brief`、`$$profile`

1. 把目前 skill 的執行設定讀齊，缺則 STOP 引導使用者跑前置 skill。
   1.1 LOAD REF [`aibdd-core::spec-package-paths.md`](aibdd-core::spec-package-paths.md) — boundary-aware 路徑規則
   1.2 `$args_path` = COMPUTE `${workspace_root}/.aibdd/arguments.yml`
   1.3 `$args_exists` = MATCH path_exists(`$args_path`)
   1.4 IF `$args_exists` == false:
       1.4.1 EMIT "${$args_path} 不存在；本 skill 需要 kickoff 後再執行，請先跑 /aibdd-kickoff" to user
       1.4.2 STOP
   1.5 `$$runtime_context` = READ `$args_path` 並 PARSE 出 `SPECS_DIR`、`current_package_slug`、`TLB`

2. 確認 brief 與 style profile 都已落地。
   2.1 `$prompt_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/design/uiux-prompt.md`
   2.2 `$profile_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/design/style-profile.yml`
   2.3 ASSERT path_exists(`$prompt_path`) ∧ path_exists(`$profile_path`)
   2.4 IF assertion fails:
       2.4.1 EMIT "uiux brief 缺失；請先跑 /aibdd-uiux-discovery" to user
       2.4.2 STOP

3. 載入 brief 並對齊上游 v2 結構（必須含三個必達 section）。
   3.1 `$$brief` = READ `$prompt_path`
   3.2 `$$profile` = READ `$profile_path`
   3.3 ASSERT `$$brief` contains `## COMPONENT CATALOG` ∧ `## FRAME COMPOSITION TABLE` ∧ `## ANCHOR NAME TABLE`
   3.4 IF assertion fails:
       3.4.1 EMIT "brief 不是 component-first v2 結構；請重跑 /aibdd-uiux-discovery 再來" to user
       3.4.2 STOP

4. TLB 必須是 frontend；否則終止。
   4.1 IF `$$runtime_context.TLB.role` ≠ "frontend":
       4.1.1 EMIT "目前 TLB 不是 frontend，aibdd-uiux-draw 不適用" to user
       4.1.2 STOP

### Phase 2 — PARSE brief into MCP plan
> 交付：`$$component_specs`、`$$frame_specs`、`$$anchor_table`、`$$tokens`

1. 從 brief 抽 component catalog（每個 ### sub-section）→ component spec 清單。
   1.1 `$$component_specs` = PARSE `$$brief` COMPONENT CATALOG sections per [`references/mcp-binding-rules.md`](references/mcp-binding-rules.md) §2
       # schema: [{component_id, role, used_by_frames, anchor_name, states: [{code, source, visual_hint}]}]

2. 從 brief 抽 frame composition table → frame spec 清單。
   2.1 `$$frame_specs` = PARSE `$$brief` FRAME COMPOSITION TABLE per [`references/mcp-binding-rules.md`](references/mcp-binding-rules.md) §3
       # schema: [{frame_slug, layout_pattern, uses: [{component_id, canonical_state}], sticky_regions, hidden_components}]

3. 從 brief 抽 anchor name table → component-keyed table。
   3.1 `$$anchor_table` = PARSE `$$brief` ANCHOR NAME TABLE per [`references/mcp-binding-rules.md`](references/mcp-binding-rules.md) §4
       # schema: [{component_id, role, accessible_name, source_rule_id}]

4. 從 style profile 抽 token map（要灌進 Pencil document variables）。
   4.1 `$$tokens` = PARSE `$$profile` per [`references/mcp-binding-rules.md`](references/mcp-binding-rules.md) §1
       # schema: {colors, typography, spacing, radius, shadow, motion}

5. 一致性驗證：anchor table 中每個 component_id 必須在 component_specs 出現；frame_specs 中每個 component_id 也必須在 component_specs 出現。
   5.1 ASSERT `$$anchor_table[*].component_id` ⊆ `$$component_specs[*].component_id`
   5.2 ASSERT `$$frame_specs[*].uses[*].component_id` ⊆ `$$component_specs[*].component_id`
   5.3 IF any assertion fails:
       5.3.1 EMIT "brief 內三個 table 的 component_id 命名空間不一致；請回 /aibdd-uiux-discovery 重出 brief" to user
       5.3.2 STOP

### Phase 3 — INIT Pencil document + load tokens
> 交付：`$$doc_id`

1. 開或建立 `.pen`。
   1.1 `$pen_target` = COMPUTE `${SPECS_DIR}/${$$runtime_context.current_package_slug}/design.pen`
   1.2 `$existing` = MATCH path_exists(`$pen_target`)
   1.3 BRANCH `$existing`:
       1.3.1 true → `$$doc_id` = TRIGGER pencil::open_document, args={path: `$pen_target`}
       1.3.2 false → `$$doc_id` = TRIGGER pencil::open_document, args={create: true, path: `$pen_target`}

2. 讀 Pencil guidelines（每次新開 doc / 每個新 skill session 必跑一次）。
   2.1 `$guidelines` = TRIGGER pencil::get_guidelines

3. 把 design tokens 灌進 document variables（單一 source of truth）。
   3.1 `$variables_payload` = RENDER token-to-pencil-variables map ← `$$tokens` per [`references/mcp-binding-rules.md`](references/mcp-binding-rules.md) §1
   3.2 TRIGGER pencil::set_variables, args=`$variables_payload`

### Phase 4 — DRAW component scenes
> 交付：`$$component_node_ids`

1. 逐 component 落 scene（每 component 一個獨立 scene，含其全部 state 變體）。
   1.1 `$$component_node_ids` = {}
   1.2 LOOP per `$component` in `$$component_specs` budget=length(`$$component_specs`)
       1.2.1 `$canvas_spot` = TRIGGER pencil::find_empty_space_on_canvas
       1.2.2 `$component_anchor_name` = COMPUTE `$$anchor_table` 中 component_id == `$component.component_id` 的 accessible_name（textbox / list / status 等非 button role 可為空）
       1.2.3 `$design_payload` = RENDER component-scene template ← `$component.states` + `$component.role` + `$component_anchor_name` per [`references/mcp-binding-rules.md`](references/mcp-binding-rules.md) §2
              # 每個 state 一個橫向擺位，下方標 state code；按 spec.visual_hint 套色/形/陰影
       1.2.4 `$result` = TRIGGER pencil::batch_design, args={canvas_spot: `$canvas_spot`, scene_name: `Component: ${$component.component_id}`, ops: `$design_payload`}
       1.2.5 `$$component_node_ids[$component.component_id]` = `$result.scene_id`
   1.3 END LOOP

2. 驗證所有 component scene 都建立成功。
   2.1 ASSERT length(`$$component_node_ids`) == length(`$$component_specs`)
   2.2 IF assertion fails:
       2.2.1 EMIT "部分 component scene 建立失敗，準備進 self-correction loop" to user
       2.2.2 GOTO #6.1

### Phase 5 — DRAW frame composition scenes
> 交付：`$$frame_node_ids`

1. 逐 frame 組合 component（canonical state combo only）。
   1.1 `$$frame_node_ids` = {}
   1.2 LOOP per `$frame` in `$$frame_specs` budget=length(`$$frame_specs`)
       1.2.1 `$canvas_spot` = TRIGGER pencil::find_empty_space_on_canvas
       1.2.2 `$layout_ops` = RENDER frame-composition template ← `$frame.layout_pattern` + `$frame.uses` + `$frame.sticky_regions` + `$frame.hidden_components` per [`references/mcp-binding-rules.md`](references/mcp-binding-rules.md) §3
              # uses[*]：以對應 component 的 canonical_state 變體擺位；hidden_components：以淺灰邊框佔位標 "(hidden by default)"
       1.2.3 `$result` = TRIGGER pencil::batch_design, args={canvas_spot: `$canvas_spot`, scene_name: `Frame: ${$frame.frame_slug}`, ops: `$layout_ops`}
       1.2.4 `$$frame_node_ids[$frame.frame_slug]` = `$result.scene_id`
   1.3 END LOOP

### Phase 6 — SELF-CHECK + SELF-CORRECT (budget ≤ 3)
> 交付：`$$health`

1. 取 snapshot + screenshot 給自評使用。
   1.1 `$snapshot` = TRIGGER pencil::snapshot_layout
   1.2 `$screenshots` = TRIGGER pencil::get_screenshot, args={scene_ids: list(`$$component_node_ids` ⊕ `$$frame_node_ids`)}

2. 自評：對照 brief 找漏 state、文字節點偏離 anchor、layout 違反 spec。
   2.1 `$issues` = CRITIQUE snapshot + screenshots vs (`$$component_specs`, `$$frame_specs`, `$$anchor_table`) per [`references/self-correction-budget.md`](references/self-correction-budget.md) §1
       # 每個 issue 含 {scope: component|frame, target_id, defect_kind: missing_state|wrong_label|wrong_layout|wrong_color|other, hint}

3. 分支：若無 issue 直接結尾；有則進修補 loop。
   3.1 BRANCH `length($issues) == 0`:
       3.1.1 true → `$$health` = "clean"；GOTO #7.1
       3.1.2 false → continue #6.4

4. 修補 loop（最多 3 輪）。
   4.1 `$loop_idx` = 0
   4.2 LOOP self-correct max 3 until length(`$issues`) == 0
       4.2.1 LOOP per `$issue` in `$$issues` budget=length(`$issues`)
            - BRANCH `$issue.defect_kind`:
              - `missing_state` → 補 batch_design 該 component scene 缺的 variant per [`references/self-correction-budget.md`](references/self-correction-budget.md) §2.1
              - `wrong_label` → TRIGGER pencil::replace_all_matching_properties 改 accessible name 對齊 anchor_table per §2.2
              - `wrong_layout` → 對該 frame 重 batch_design layout ops per §2.3
              - `wrong_color` → TRIGGER pencil::replace_all_matching_properties 改色 token reference per §2.4
              - `other` → MARK 為人工待修，不嘗試自修
       4.2.2 END LOOP
       4.2.3 `$snapshot` = TRIGGER pencil::snapshot_layout
       4.2.4 `$screenshots` = TRIGGER pencil::get_screenshot, args={scene_ids: list(`$$component_node_ids` ⊕ `$$frame_node_ids`)}
       4.2.5 `$issues` = CRITIQUE `$snapshot` + `$screenshots` vs brief per [`references/self-correction-budget.md`](references/self-correction-budget.md) §1
       4.2.6 IF length(`$issues`) == 0:
            `$$health` = "clean"；RETURN
       4.2.7 `$loop_idx` = `$loop_idx` + 1
   4.3 END LOOP
   4.4 `$$health` = "degraded"   # 用光 budget 仍有 issue；交人工

### Phase 7 — EXPORT + WRITE
> 交付：`$$pen_path`

1. Export 並寫到 package root。
   1.1 `$$pen_path` = COMPUTE `${SPECS_DIR}/${$$runtime_context.current_package_slug}/design.pen`
   1.2 TRIGGER pencil::export_nodes, args={doc_id: `$$doc_id`, target_path: `$$pen_path`, scope: "all"}
   1.3 ASSERT path_exists(`$$pen_path`)
   1.4 IF assertion fails:
       1.4.1 EMIT "Pencil export 失敗，但 doc 仍在 MCP session 中；user 可手動 export 或重跑本 skill" to user
       1.4.2 STOP

### Phase 8 — EMIT REPORT
> 交付：(none)

1. 結案訊息：列出產出與 health。
   1.1 `$report` = DRAFT report ← `$$pen_path`, count(`$$component_node_ids`), count(`$$frame_node_ids`), `$$health`, 語言=zh-TW
       # 內容必含：
       # - .pen 路徑
       # - 落了幾個 component scene / 幾個 frame composition scene
       # - 自檢健康度（clean / degraded + 殘留 issue 清單）
       # - 下一步建議：跑 /aibdd-plan 萃取 I4 anchor / DSL L1 / contract
   1.2 EMIT `$report` to user

2. 若 health == degraded，明確提示人工待修點。
   2.1 IF `$$health` == "degraded":
       2.1.1 `$manual_fix_msg` = DRAFT 殘留 issue 清單 + 建議手動 fix 方式 ← `$issues`
       2.1.2 EMIT `$manual_fix_msg` to user

## §3 CROSS-REFERENCES

- `/aibdd-uiux-discovery` — 直接上游；產出 `design/uiux-prompt.md` + `design/style-profile.yml` 為本 skill 的 INPUT SSOT
- `/aibdd-plan` — 下游；讀本 skill 產的 `design.pen` 萃取 I4 anchor / DSL L1 / contract
- `/aibdd-form-story-spec` / `aibdd-pen-to-storybook` — 下下游；負責 `.pen → <ComponentId>.stories.tsx`

### Future evolution

- `scripts/python/parse_brief.py` — Phase 2 step 1-3 用 PARSE（D verb），可抽 deterministic script 取代純 markdown parse；待 brief schema 穩定後切換
- `scripts/python/grade_screenshots.py` — Phase 6 step 2 CRITIQUE（S verb），未來 vision LLM 穩定後可固定 grading rubric
