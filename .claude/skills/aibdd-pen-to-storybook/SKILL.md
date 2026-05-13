---
name: aibdd-pen-to-storybook
description: >
  Adapter for Pencil `.pen` design files. Reads `.pen` → returns normalized
  `component_table` + Tailwind 4 `tokens`. Pure read-only — does NOT write files.
  Pencil-side adapter implementation of the cross-source design adapter contract;
  future siblings (`aibdd-figma-to-storybook`, `aibdd-penpot-to-storybook`) follow
  the same `component_table + tokens` return shape so downstream consumers
  (`/aibdd-form-story-spec`, `/aibdd-plan` Phase 3 component-design merge,
  `/aibdd-green-execute` Wave 1) stay design-source-agnostic.
metadata:
  user-invocable: false
  source: project-level dogfooding
---

# aibdd-pen-to-storybook

Pencil `.pen` adapter skill。**read-only**：讀 `.pen` JSON，抽 design tokens、挑 single screen、做 component
candidate detection，回 `component_table` + `tokens` 給 caller。**不寫任何檔**、不建專案、不 npm install、不
build storybook。

被 `/aibdd-form-story-spec` Phase 1 的 design-source cross-check 與（未來）`/aibdd-plan` Phase 3 component-design
merge sub-phase DELEGATE。

只負責「把已 freeze 的 .pen 解析成 component_table + tokens 推理包」；不重新做設計、不替設計者做顆粒度判斷、
不對非 React 框架輸出、不寫 component / story / project files（那些是 form-story-spec 與 green-execute 的職責）。

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
    purpose: caller 入口契約 + 角色定位 + 不做事項（adapter-only）
  - path: references/format-reference.md
    purpose: '.pen v2.x JSON schema verbatim + Tailwind 4 token namespace 對照（component_table 給 caller 直接用）'
  - path: references/dsl-best-practice.md
    purpose: 'component_table 命名 / variant enum / Tailwind 4 token 慣例（caller 渲染 .tsx 時參考）'
  - path: references/patterns/tokens-mapping.md
    purpose: '.pen Document.variables → Tailwind 4 @theme namespace 對照'
  - path: references/patterns/component-detection.md
    purpose: '6 條 component candidate heuristics + 表格輸出契約'
  - path: references/anti-patterns.md
    purpose: '常見錯誤：framework 拼錯、Tailwind 4 syntax 走 v3、@layer 用錯等'
  - path: references/fail-codes.md
    purpose: 'Phase N dispatch — failure_kind → caller-return message'
```

## §2 SOP

### Phase 1 — ASSERT intake｜驗證入口
> produces: `$$pen_path`, `$$screen_id?`

1. `$contract` = READ [`references/role-and-contract.md`](references/role-and-contract.md)
2. `$$pen_path` = PARSE caller-provided `.pen` 檔絕對路徑
3. `$$screen_id` = PARSE optional 指定 screen ID（缺項則 Phase 4 由 caller 確認）
4. `$payload_ok` = JUDGE `$$pen_path` against `$contract`
5. ASSERT `$payload_ok`
6. ASSERT path_exists(`$$pen_path`)
7. ASSERT `$$pen_path` 副檔名 == `.pen`

### Phase 2 — VERIFY .pen 可解析
> produces: `$$pen_doc`, `$$schema_version`

1. `$schema` = READ [`references/format-reference.md`](references/format-reference.md)
2. `$file_kind` = MATCH `file $$pen_path` 結果
3. ASSERT `$file_kind` 含 `UTF-8` / `ASCII text`（拒收 binary、舊版 .pen）
4. `$$pen_doc` = PARSE `jq '.' $$pen_path`
5. `$$schema_version` = PARSE `$$pen_doc.version`
6. ASSERT `$$schema_version` matches `^2\.\d+$`
7. ASSERT `$$pen_doc.children` is array && length > 0

### Phase 3 — EXTRACT tokens｜抽 Tailwind 4 tokens
> produces: `$$tokens`

1. `$mapping` = READ [`references/patterns/tokens-mapping.md`](references/patterns/tokens-mapping.md)
2. `$variables` = PARSE `jq '.variables' $$pen_path`
3. `$$tokens` = DERIVE empty list
4. LOOP per `$var_name, $var` in `$variables`
   4.1 `$ns` = MATCH `$var.type` against `$mapping` namespace table
       - `color` → `--color-<name>`
       - `string` (font family) → `--font-<role>`
       - `number` 含 `radius` → `--radius-<name>`
       - `number` 含 `spacing` / `gap` → `--spacing-<name>`
       - `number` 其他 → `--<name>` custom var
       - `boolean` → SKIP（不入 Tailwind）
   4.2 `$entry` = DRAFT `{ name: $var_name, namespace: $ns, value: $var.value }`
   4.3 `$$tokens` = DERIVE append `$entry`
   END LOOP
5. ASSERT count(`$$tokens`) >= 1（沒有任何 token 通常代表 .pen 沒設計過）

### Phase 4 — MAP screen tree｜挑選並讀取單一 screen
> produces: `$$screen_node`, `$$node_tree_pretty`

1. `$top_level` = PARSE `jq '[.children[] | {id, name, type, w: .width, h: .height}]' $$pen_path`
2. BRANCH `$$screen_id` is set
   true:
     2.1 ASSERT `$$screen_id ∈ $top_level[].id`
   false:
     2.2 RETURN `$top_level` to caller，請 caller 指定 `$$screen_id` 後重啟 Phase 4
     2.3 STOP
3. `$$screen_node` = PARSE `jq '.children[] | select(.id=="$$screen_id")' $$pen_path`
4. `$$node_tree_pretty` = RENDER pretty-print of `$$screen_node`（縮排樹；節點顯示 type / id / name / size / fill / layout）
5. 用 `$$node_tree_pretty` 作為 Phase 5 的 input；不要在多個 screen 上同時跑 component detection（會混淆抽象）

### Phase 5 — DETECT component candidates｜套用 heuristics
> produces: `$$component_table`

1. `$rules` = READ [`references/patterns/component-detection.md`](references/patterns/component-detection.md)
2. `$skip_list` = PARSE `$rules.always_inline`（topBar / bottomBar / sidebar / hero…）
3. `$candidates` = DERIVE empty list
4. APPLY `$rules` heuristics 1–6 順序對 `$$screen_node` 子樹掃描：
   4.1 `reusable: true` 節點 → 強制 component
   4.2 numeric-suffix 重複（`tile1..N`）→ 推導 `state` / `variant` enum
   4.3 prefix grouping（`chipA0..A2 / chipB0..B3`）→ 推導 `kind` × `count` 雙 enum
   4.4 同 subtree 不同文案 → `content` prop
   4.5 同 subtree 不同 fill / text-color → enum `state` prop
   4.6 `comp/`、`Component/` 前綴 → 顯式 component intent
5. `$$component_table` = DRAFT 表格 columns: `Component | Source nodes | Detected props | Stories`
6. LOOP per `$candidate` in `$candidates`
   6.1 ASSERT `$candidate.name` is PascalCase（小寫開頭強制改 PascalCase 寫進表格）
   6.2 ASSERT `$candidate.props` 至少含一個 prop（無差異 → 不抽，inline）
   6.3 `$candidate.stories` = DERIVE list of observed states (3–6 推薦上限)
   6.4 `$$component_table` = DERIVE append row
   END LOOP
7. ASSERT count(`$$component_table.rows`) >= 1

### Phase 6 — REPORT adapter
> produces: `$$report`

1. `$$report` = DRAFT {
     status: "completed",
     mode: "adapter",
     pen_path: `$$pen_path`,
     screen_id: `$$screen_id`,
     schema_version: `$$schema_version`,
     token_count: count(`$$tokens`),
     tokens: `$$tokens`,
     component_count: count(`$$component_table.rows`),
     component_table: `$$component_table`
   }
2. RETURN `$$report` to caller

### Phase 7 — HANDLE dispatch
> produces: `$$caller_msg`

1. `$failure_kind` = CLASSIFY runtime failure into one of the kinds enumerated in [`references/fail-codes.md`](references/fail-codes.md)
2. `$$caller_msg` = DERIVE caller-return message from `$failure_kind` per [`references/fail-codes.md`](references/fail-codes.md)
3. RETURN `$$caller_msg`

## §3 CROSS-REFERENCES

- 上游：Pencil GUI + MCP（探索期）— 設計者 freeze 後產出 `.pen`，再交給 caller skill 把本 adapter 的 `pen_path` 拼進 caller payload。
- 直接下游（DELEGATE caller）：
  - `/aibdd-form-story-spec` Phase 1 design-source cross-check — 比對 caller reasoning 之 `component.identifier` / `stories[].export_name` 是否在本 adapter 的 `component_table` 內，不一致時 warn（不 override）。
  - `/aibdd-plan` Phase 3（未來 component-design merge sub-phase）— 把本 adapter 的 `component_table + tokens` 與 features × activities 合成 enriched `boundary_delta.components`，下游分流到 form-story-spec（寫 component + story）與 green-execute（補業務邏輯）。
- Sibling adapters（同 contract，不同設計來源）：未來 `aibdd-figma-to-storybook` / `aibdd-penpot-to-storybook` 等遵循同一 return shape（`status / mode / token_count / tokens / component_count / component_table`），讓下游不耦合任一設計來源。
- 不做：寫回 .pen、做視覺探索、選 design system 元件、做業務 BDD step 綁定、scaffold Next.js 專案、跑 npm install / tsc / build-storybook（這些已在歷史版本砍除；scaffold 屬 `/aibdd-auto-starter`，component / story 寫檔屬 `/aibdd-form-story-spec`，業務邏輯屬 `/aibdd-green-execute`）。
- 視覺回歸 baseline（optional companion，非本 skill SOP 內步驟）：若 `@pencil.dev/cli` 已安裝且已認證，user 可在 caller 流程結束後外部執行 `pencil interactive -i <pen_path> -o /dev/null <<< 'export_nodes({ nodeIds: ["SCREEN_ID"], outputDir: "./baseline" }); exit()'` 自行產 baseline 圖。本 skill 不主動觸發。

## §4 ORPHANED REFERENCES (已棄用，未來清掃)

下列檔案是舊版 scaffold mode 殘留，**SOP 已不再 LOAD**，保留實體檔以利 git history / 未來考古：

- `references/patterns/project-scaffold.md` — 舊版 Phase 6 scaffold project 用的 package.json / tsconfig / .storybook / app/ 模板。新流程下 scaffold 屬 `/aibdd-auto-starter` 的 template 職責。

未來清掃時整批刪除即可，不影響本 skill 行為。
