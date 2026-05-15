---
name: aibdd-uiux-design
description: 從 /aibdd-discovery 產出（spec.md / *.activity / *.feature skeleton / atomic rules）機械推導 component-first 視覺結構：先抽 component inventory（含 per-component state matrix）再組 frame composition map（每 frame 用哪些 component + canonical state combo），DELEGATE /clarify-loop 與 user 批次澄清視覺方向 / 元件盤點 / 品牌參考，emit Pencil-ready prompt（design/uiux-prompt.md）+ style profile（design/style-profile.yml）。下游可手動畫 .pen 或委派 /aibdd-uiux-draw 走 Pencil MCP 自動繪製。TRIGGER when 使用者下 /aibdd-uiux-design、discovery 完成想開始視覺探索、或被 plan 前流程委派。SKIP when discovery 產物缺失、target boundary 為純後端、已有既有 .pen 上游 SSOT、或 user 明示視覺已鎖（直接用既有 design system）。
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-uiux-design

視覺探索規劃器（component-first v2）｜從 /aibdd-discovery 產出機械推導兩個關鍵結構 — **component inventory（含 per-component state matrix）+ frame composition map（每 frame 用哪些 component + canonical state combo）**；DELEGATE /clarify-loop 補齊使用者未講清楚的視覺維度；emit 一份 Pencil-ready 設計 brief（design/uiux-prompt.md）+ tokens 提案（design/style-profile.yml）。下游可手動畫 `.pen` 或委派 `/aibdd-uiux-draw` 透過 Pencil MCP 自動繪製。

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
  - path: references/clarify-axes-catalog.md
    purpose: 9 大 UIUX 澄清軸題庫（style direction / tokens / components / interactions / copy decisions / breakpoints / a11y / motion / brand references），每軸標 context 來源 + validator
  - path: references/state-derivation-rules.md
    purpose: 從 .activity DECISION 分支 + .feature Rule 條款機械推導 state matrix 的對應規則 + state code 命名規約
  - path: references/anchor-naming-rules.md
    purpose: accessible name 命名規則 — 必須取自 atomic-rules 動詞，禁同義改寫；唯一性 + role 強制 + forbidden anchor 黑名單
  - path: references/pencil-prompt-sections.md
    purpose: assets/templates/uiux-prompt.template.md 各 section 的填值來源表（哪段取自 discovery 推導、哪段取自 clarify-loop 回填）
```

## §2 SOP

> 閱讀規則：主 item 只做摘要；要執行的內容一律編成子步驟。未編號縮排只保留給條件說明 / branch label / 補充註解。

### Phase 1 — LOAD discovery truth
> 交付：`$$runtime_context`、`$$discovery_bundle`

1. 把目前 skill 的執行設定與 discovery 產出讀齊，缺則先 STOP 引導使用者跑前置 skill。
   1.1 `$$skill_dir` = COMPUTE 目前 skill 目錄
   1.2 LOAD REF [`aibdd-core::spec-package-paths.md`](aibdd-core::spec-package-paths.md) — boundary-aware 路徑規則
   1.3 `$args_path` = COMPUTE `${workspace_root}/.aibdd/arguments.yml`
   1.4 `$args_exists` = MATCH path_exists(`$args_path`)
   1.5 IF `$args_exists` == false:
       1.5.1 EMIT "${$args_path} 不存在；本 skill 需要 kickoff 後再執行，請先跑 /aibdd-kickoff 建立 arguments.yml" to user
       1.5.2 STOP
   1.6 `$$runtime_context` = READ `$args_path` 並 PARSE 出 `FEATURE_SPECS_DIR`、`ACTIVITIES_DIR`、`SPECS_DIR`、`current_package_slug`、`TLB`（target leaf boundary）

2. 必要欄位若缺，先委派 clarify-loop 補齊。
   2.1 IF `$$runtime_context` 缺 `FEATURE_SPECS_DIR` ∨ `ACTIVITIES_DIR` ∨ `current_package_slug`:
       2.1.1 [USER INTERACTION] `$clarify` = DELEGATE `/clarify-loop`，附上缺欄題組
       2.1.2 WAIT for `$clarify`
       2.1.3 GOTO #1.3

3. 確認 discovery 產物存在，否則停止。
   3.1 `$spec_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/spec.md`
   3.2 `$activities` = COMPUTE list of `${ACTIVITIES_DIR}/**/*.activity`
   3.3 `$features` = COMPUTE list of `${FEATURE_SPECS_DIR}/**/*.feature`
   3.4 ASSERT `$spec_path` exists ∧ length(`$activities`) ≥ 1 ∧ length(`$features`) ≥ 1
   3.5 IF assertion fails:
       3.5.1 EMIT "discovery 產物缺失；請先跑 /aibdd-discovery" to user
       3.5.2 STOP

4. TLB 必須是 frontend；後端 boundary 直接終止。
   4.1 IF `$$runtime_context.TLB.role` ≠ "frontend":
       4.1.1 EMIT "目前 TLB 不是 frontend，aibdd-uiux-design 不適用" to user
       4.1.2 STOP

5. 把 discovery 產物全部讀進 bundle。
   5.1 `$spec` = READ `$spec_path`
   5.2 `$activity_files` = READ all paths in `$activities`
   5.3 `$feature_files` = READ all paths in `$features`
   5.4 `$$discovery_bundle` = DERIVE struct{spec, activities, features} from above

### Phase 2 — DERIVE component inventory + frame composition + anchor candidates
> 交付：`$$component_inventory`、`$$frame_composition`、`$$anchor_candidates`

1. 從 atomic-rules 動詞 + .feature Rule 條款抽 component candidate（§A 元件層第一步）。
   1.1 `$component_candidates` = DERIVE component candidates ← `$$discovery_bundle.features` Rule 動詞 + 名詞 per [`references/state-derivation-rules.md`](references/state-derivation-rules.md) §A1
   1.2 ASSERT 每條 .feature Rule 至少對應 1 個 component candidate 或標記為 `non-visual`
   1.3 IF assertion fails:
       1.3.1 EMIT "有 .feature Rule 找不到對應 component candidate；可能是 Rule 句型不含動作對象，請在 clarify §3 補" to user
       1.3.2 # 不 STOP；保留 unclassified 標記，交 clarify-loop 收尾

2. 依 role 給每個 component 補 base states（互動本質）。
   2.1 `$component_with_base_states` = DERIVE per-component base_states ← `$component_candidates` per [`references/state-derivation-rules.md`](references/state-derivation-rules.md) §A2 來源 1

3. 從 .activity DECISION × .feature Rule 補 domain states（rejection / error / empty / loading）。
   3.1 `$component_with_domain_states` = DERIVE per-component domain_states ← `$$discovery_bundle.activities` + `$$discovery_bundle.features` per [`references/state-derivation-rules.md`](references/state-derivation-rules.md) §A2 來源 2

4. 整合成 component inventory（per component 一列，含 base_states ⊕ domain_states ⊕ used_by_frames）。
   4.1 `$$component_inventory` = DERIVE component inventory merging `$component_with_base_states` + `$component_with_domain_states` per [`references/state-derivation-rules.md`](references/state-derivation-rules.md) §A4
   4.2 ASSERT 每個 component 至少 1 個 success-path state（idle / populated / pristine 視 role 而定）
   4.3 IF assertion fails:
       4.3.1 EMIT "有 component 沒有 success-path state；DECISION branch 可能漏抽" to user
       4.3.2 STOP

5. 從 activity action node 抽 frame，建 frame ↔ activity ↔ feature ↔ component 對應表（§B 組合層）。
   5.1 `$$frame_composition` = DERIVE frame composition map ← `$$discovery_bundle.activities` + `$$component_inventory` per [`references/state-derivation-rules.md`](references/state-derivation-rules.md) §B1+§B2
   5.2 ASSERT 每個 frame 都能對應至少一條 .feature Rule ∧ uses_components 非空
   5.3 IF assertion fails:
       5.3.1 EMIT "有 activity action node 無對應 feature Rule，或對應後沒用到任何 component；可能是 discovery 漏寫 Rule" to user
       5.3.2 STOP
   5.4 ASSERT 每個 frame.uses_components[*].component_id ∈ `$$component_inventory[*].id`
   5.5 IF assertion fails:
       5.5.1 EMIT "frame 引用了 inventory 中不存在的 component_id；命名空間不一致" to user
       5.5.2 STOP

6. 從 component candidate 抽 anchor name 候選（keyed by component_id，跨 frame 共用一條）。
   6.1 `$$anchor_candidates` = DERIVE accessible-name 候選 ← `$$component_inventory` 中 role ∈ {button, link, textbox, heading, listitem, tab, menuitem} 的 component per [`references/anchor-naming-rules.md`](references/anchor-naming-rules.md) §1

### Phase 3 — DRAFT UIUX clarification axes
> 交付：`$$clarify_payload`

1. 依題庫 9 大軸生成題目；每軸都帶 derive 出來的 context 給 user 看。
   1.1 `$axes` = DRAFT 9 axes per [`references/clarify-axes-catalog.md`](references/clarify-axes-catalog.md)
   1.2 `$axes` = EDIT `$axes` ← attach `$$component_inventory` / `$$frame_composition` / `$$anchor_candidates` 為各題 context（讓 user 看到目前 derive 的當前資訊再回答）；§3 component inventory 與 §6 frame composition 為 v2 必答軸

2. 組成 clarify-loop payload schema。
   2.1 `$$clarify_payload` = RENDER clarify-loop payload, vars={round_purpose: "aibdd-uiux-design visual axes (component-first)", questions: `$axes`, update_mode_hint: "sync"}
   2.2 ASSERT length(`$$clarify_payload.questions`) ≤ 16   # clarify-loop 會自動分 Sub-round（每 round ≤ 4 題）

### Phase 4 — DELEGATE /clarify-loop
> 交付：`$$clarify_resolved`

1. 把 payload 丟給 clarify-loop，等回 resolved answers。
   1.1 [USER INTERACTION] `$clarify_out` = DELEGATE `/clarify-loop` with `$$clarify_payload`
   1.2 WAIT for `$clarify_out`
   1.3 `$$clarify_resolved` = PARSE `$clarify_out`, schema=resolved-answers

2. 完整性檢查；缺答的軸重跑澄清。
   2.1 `$missing_axes` = DERIVE 未回答的軸 from `$$clarify_resolved`
   2.2 IF `$missing_axes` non-empty:
       2.2.1 EMIT "still missing axes: ${$missing_axes}" to user
       2.2.2 GOTO #3.1

### Phase 5 — RENDER Pencil prompt + style profile + handoff
> 交付：`$$prompt_path`、`$$profile_path`

1. 載入 prompt template，依 discovery 推導值 + clarify 回填值填值。
   1.1 `$tmpl` = READ [`assets/templates/uiux-prompt.template.md`](assets/templates/uiux-prompt.template.md)
   1.2 `$prompt` = RENDER `$tmpl`, vars=`$$clarify_resolved` ⊕ `$$component_inventory` ⊕ `$$frame_composition` ⊕ `$$anchor_candidates` per [`references/pencil-prompt-sections.md`](references/pencil-prompt-sections.md)

2. 載入 style-profile template；專責 tokens / breakpoints / fonts / motion。
   2.1 `$profile_tmpl` = READ [`assets/templates/style-profile.template.yml`](assets/templates/style-profile.template.yml)
   2.2 `$profile` = RENDER `$profile_tmpl`, vars=`$$clarify_resolved`

3. 驗收條件 hard check：先 ASSERT 再落檔（避免半成品殘留）。
   3.1 ASSERT `$prompt` contains non-empty COMPONENT CATALOG section（含至少一個 ### sub-section + state matrix table） per [`references/pencil-prompt-sections.md`](references/pencil-prompt-sections.md) §3
   3.2 ASSERT `$prompt` contains non-empty FRAME COMPOSITION TABLE section per same §3
   3.3 ASSERT `$prompt` contains non-empty ANCHOR NAME TABLE section per same §3
   3.4 ASSERT FRAME COMPOSITION TABLE 內 `uses` 欄位引用的每個 component id 都在 COMPONENT CATALOG 中出現
   3.5 ASSERT ANCHOR NAME TABLE 內 `Component` 欄位引用的每個 component id 都在 COMPONENT CATALOG 中出現
   3.6 IF any assertion fails:
       3.6.1 EMIT "prompt render 不完整；component catalog / frame composition / anchor name 任一缺漏或 component_id 命名空間不一致" to user
       3.6.2 GOTO #5.1.1

4. 落檔（design/ 目錄）。
   4.1 `$$prompt_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/design/uiux-prompt.md`
   4.2 `$$profile_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/design/style-profile.yml`
   4.3 CREATE `${SPECS_DIR}/${current_package_slug}/design/`
   4.4 WRITE `$$prompt_path` ← `$prompt`
   4.5 WRITE `$$profile_path` ← `$profile`

### Phase 6 — EMIT REPORT
> 交付：(none)

1. 整理一段口語結案訊息給 user。
   1.1 `$summary` = DRAFT report ← `$$prompt_path`, `$$profile_path`, count(`$$component_inventory`), count(`$$frame_composition`), count(`$$anchor_candidates`), 語言=zh-TW；訊息點出「component-first：每個 component 一個 scene 含全 state 變體；每個 frame 一張組合圖只畫 canonical state」
   1.2 EMIT `$summary` to user

2. 給 user 明確的下一步動作（兩條路徑：自動繪製 OR 手動畫）。
   2.1 `$pen_target_path` = COMPUTE `${SPECS_DIR}/${current_package_slug}/design.pen`   # 固定檔名；package root；與 spec.md / plan.md / tasks.md 同層；不進 design/ 目錄
   2.2 `$handoff_msg` = DRAFT 下一步指引 ← `$$prompt_path`, `$pen_target_path`, 語言=zh-TW, 內容必含：
       - **路徑 A（推薦，自動）**：跑 `/aibdd-uiux-draw`；該 skill 讀 `${$$prompt_path}` + `${$$profile_path}`，透過 Pencil MCP 自動逐 component scene + frame composition scene 繪製並 export `.pen` 到 `${$pen_target_path}`
       - **路徑 B（手動，fallback）**：把 `${$$prompt_path}` 整段內容貼進 Pencil app 自己畫；完成後 export 為 `design.pen` 存到 `${$pen_target_path}`（**package root**，與 `spec.md` / `plan.md` 同層；不進 `design/` 目錄內）
       - 不論走 A 或 B，下一步都跑 `/aibdd-plan` — plan 階段從 package root 讀 `design.pen` 萃取 I4 anchor / DSL L1 / contract
       - 註記：`.pen` 為**過渡轉換檔**；下游 `aibdd-pen-to-storybook` 一條龍翻成 `<ComponentId>.tsx` + `<ComponentId>.stories.tsx` 後，**Story 才是 boundary I4 binding anchor 的 SSOT**，`.pen` 不保證長期保留
   2.3 EMIT `$handoff_msg` to user

## §3 CROSS-REFERENCES

- `/aibdd-discovery` — 上游；產出 spec.md / activities / features / atomic-rules 為本 skill 的 INPUT SSOT
- `/clarify-loop` — DELEGATE 對象；本 skill 不自寫 UX 文案，所有澄清題目都丟它
- `/aibdd-uiux-draw` — 直接下游（推薦路徑 A）；讀本 skill 產出的 `design/uiux-prompt.md` + `design/style-profile.yml`，透過 Pencil MCP 自動繪 `.pen`
- `/aibdd-plan` — 後續下游；plan 階段會吃 `.pen` 萃取 I4 anchor / DSL L1 / contract
- `/aibdd-pen-to-storybook` — 下下游；**producer skill**，負責 `.pen → <ComponentId>.tsx + <ComponentId>.stories.tsx` 一條龍翻譯（合約定型；每個 component 對一份雙產出，每個 state 一個 story export）
- `/aibdd-form-story-spec` — 平行路徑（caller-driven，無 `.pen`）；本 discovery 流程不會走到 — 設計來源既然是 `.pen`，下游就走 pen-to-storybook

### Future evolution

- `scripts/python/derive_component_inventory.py` — 目前 Phase 2 step 1-4 用 CLASSIFY / DERIVE（混 D + S）；當 `.activity` DSL parser 與 .feature Rule parser 穩定後抽出 deterministic script，把 component candidate 抽取 + state matrix 推導改 TRIGGER 該 script（純 D，省 token）
- `scripts/python/derive_frame_composition.py` — Phase 2 step 5；frame ↔ activity node ↔ component 對應表機械化
- `scripts/python/extract_anchor_candidates.py` — Phase 2 step 6 可機械化
