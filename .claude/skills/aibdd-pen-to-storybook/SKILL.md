---
name: aibdd-pen-to-storybook
description: >
  Producer skill for Pencil `.pen` design files. Reads `.pen` → writes paired
  `<ComponentId>.tsx` + `<ComponentId>.stories.tsx` per detected component into
  caller-specified `target_dir`. Component .tsx 含完整 Tailwind 4 utility class
  與 variant-conditional className（從 `.pen` node tree + tokens 推導），stories
  .tsx 為 boundary I4 binding anchor SSOT。Design pipeline 一條龍；form-story-spec
  只處理非 design 路徑（caller-driven payload，無 .pen）。Pencil-side implementation
  of the cross-source design producer contract；未來 `aibdd-figma-to-storybook` /
  `aibdd-penpot-to-storybook` 等 sibling 須遵循同一 produced-files contract，讓
  caller（`/aibdd-plan` Phase 3 / `/aibdd-green-execute` Wave 1）不耦合任一設計來源。
metadata:
  user-invocable: false
  source: project-level dogfooding
---

# aibdd-pen-to-storybook

Pencil `.pen` **producer** skill。讀 `.pen` JSON、抽 design tokens、挑 single screen、做 component
candidate detection，**並直接寫**對應的 `<ComponentId>.tsx` + `<ComponentId>.stories.tsx` 到 caller 指定的
`target_dir`。Component .tsx 含完整 Tailwind 4 utility class（由 `.pen` 節點樹 + tokens 推導）與
variant-conditional className；stories .tsx 為 boundary I4 binding anchor SSOT。

被 `/aibdd-plan` Phase 3 design-pipeline 直接 DELEGATE。本 skill 為 component 檔的 **owner**：視覺修改一律
回 `.pen` 後重跑本 skill（`mode: "overwrite"`），不在下游手改。

只負責「設計來源是 `.pen` 的元件 + story 雙產出」；不重新做設計、不替設計者做顆粒度判斷、不對非 React
框架輸出、不寫業務邏輯（hooks / fetch / state machines 屬 green-execute；page-level 組裝亦屬 green）、
不建專案、不 npm install、不 build storybook（scaffold 屬 `/aibdd-auto-starter`）。

非 design pipeline（caller-driven payload，無 `.pen`）走 `/aibdd-form-story-spec`；本 skill 不接受
無 `pen_path` 的 caller。

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
    purpose: caller 入口契約 + 角色定位 + producer scope（target_dir / mode / frozen contract）
  - path: references/format-reference.md
    purpose: '.pen v2.x JSON schema verbatim + Tailwind 4 token namespace 對照'
  - path: references/dsl-best-practice.md
    purpose: 'component naming / variant enum / Tailwind 4 token 慣例'
  - path: references/patterns/tokens-mapping.md
    purpose: '.pen Document.variables → Tailwind 4 @theme namespace 對照'
  - path: references/patterns/component-detection.md
    purpose: '6 條 component candidate heuristics + 表格輸出契約'
  - path: references/patterns/pen-tree-rendering.md
    purpose: '.pen 節點樹（Frame/Group/Rectangle/Text/IconFont/Path/Ellipse/Line）→ 巢狀 JSX + Tailwind utility class 的映射規約'
  - path: references/patterns/variants-and-states.md
    purpose: 'detection 階段抽出的 variant / state enum → conditional className 渲染 + 一狀態一 story export'
  - path: references/patterns/binding-anchor.md
    purpose: 'boundary I4 binding anchor — 一 story = (role, accessible_name); accessible_name_arg.field 必須 ∈ props'
  - path: references/anti-patterns.md
    purpose: '常見錯誤：framework 拼錯、Tailwind 4 syntax 走 v3、@layer 用錯、token name 寫進 className 等'
  - path: references/fail-codes.md
    purpose: 'Phase N dispatch — failure_kind → caller-return message'
```

## §2 SOP

### Phase 1 — ASSERT intake｜驗證入口
> produces: `$$pen_path`, `$$screen_id?`, `$$target_dir`, `$$mode`, `$$skill_dir`

1. `$contract` = READ [`references/role-and-contract.md`](references/role-and-contract.md)
2. `$$pen_path` = PARSE caller-provided `.pen` 檔絕對路徑
3. `$$screen_id` = PARSE optional 指定 screen ID（缺項則 Phase 4 列候選回 caller）
4. `$$target_dir` = PARSE caller-provided 寫檔目錄（必填，慣例 `${TRUTH_BOUNDARY_ROOT}/contracts/components/`）
5. `$$mode` = PARSE caller-provided `"create" | "overwrite"`（預設 `"create"`）
6. `$payload_ok` = JUDGE `{ $$pen_path, $$target_dir, $$mode }` against `$contract`
7. ASSERT `$payload_ok`
8. ASSERT path_exists(`$$pen_path`)
9. ASSERT `$$pen_path` 副檔名 == `.pen`
10. ASSERT `$$mode` ∈ {`create`, `overwrite`}
11. ASSERT `$$target_dir` 為絕對路徑；若 parent 不存在，dispatch `target-dir-invalid`
12. `$$skill_dir` = COMPUTE current skill directory path
    # Phase 2-4 的 .pen query 透過 `${$$skill_dir}/scripts/python/pen_query.py` 執行，stdlib-only 不依賴 jq

### Phase 2 — VERIFY .pen 可解析
> produces: `$$pen_doc`, `$$schema_version`

1. `$schema` = READ [`references/format-reference.md`](references/format-reference.md)
2. `$file_kind` = MATCH `file $$pen_path` 結果
3. ASSERT `$file_kind` 含 `UTF-8` / `ASCII text`（拒收 binary、舊版 .pen）
4. `$$pen_doc` = TRIGGER `python3 "${$$skill_dir}/scripts/python/pen_query.py" "${$$pen_path}" --all`
   # 取代 `jq '.' $$pen_path`；script stdlib-only，exit 1 = parse/encoding error
5. `$$schema_version` = PARSE `$$pen_doc.version`
6. ASSERT `$$schema_version` matches `^2\.\d+$`
7. ASSERT `$$pen_doc.children` is array && length > 0

### Phase 3 — EXTRACT tokens｜抽 Tailwind 4 tokens
> produces: `$$tokens`

1. `$mapping` = READ [`references/patterns/tokens-mapping.md`](references/patterns/tokens-mapping.md)
2. `$variables` = TRIGGER `python3 "${$$skill_dir}/scripts/python/pen_query.py" "${$$pen_path}" --variables`
   # 取代 `jq '.variables' $$pen_path`
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

1. `$top_level` = TRIGGER `python3 "${$$skill_dir}/scripts/python/pen_query.py" "${$$pen_path}" --top-level`
   # 取代 `jq '[.children[] | {id, name, type, w: .width, h: .height}]' $$pen_path`
2. BRANCH `$$screen_id` is set
   true:
     2.1 ASSERT `$$screen_id ∈ $top_level[].id`
   false:
     2.2 RETURN `$top_level` to caller，請 caller 指定 `$$screen_id` 後重啟 Phase 4
     2.3 STOP
3. `$$screen_node` = TRIGGER `python3 "${$$skill_dir}/scripts/python/pen_query.py" "${$$pen_path}" --screen-node "${$$screen_id}"`
   # 取代 `jq '.children[] | select(.id=="$$screen_id")' $$pen_path`；exit 2 = screen_id 不存在
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

### Phase 6 — DERIVE render plan per component｜把 component_table × 節點樹合成可渲染 spec
> produces: `$$render_plans`

1. `$tree_rules` = READ [`references/patterns/pen-tree-rendering.md`](references/patterns/pen-tree-rendering.md)
2. `$variant_rules` = READ [`references/patterns/variants-and-states.md`](references/patterns/variants-and-states.md)
3. `$anchor_rules` = READ [`references/patterns/binding-anchor.md`](references/patterns/binding-anchor.md)
4. `$$render_plans` = DERIVE empty list
5. LOOP per `$row` in `$$component_table.rows`
   6.1 `$canonical_node` = DERIVE base instance from `$row.SourceNodes`（H2/H3 取第一個；H1/H6 取 `reusable` 本體；H4/H5 取 prop diff 之 representative）
   6.2 `$jsx_spec` = DRAFT 巢狀 JSX spec from `$canonical_node` 子樹 per `$tree_rules`（含 root element、children layout、leaf 屬性）
   6.3 `$base_className` = DRAFT Tailwind 4 utility 字串 from `$canonical_node` graphics/layout 屬性 per `$tree_rules` §3（fill → `bg-*`、stroke → `border-*`、padding → `p-*`、gap → `gap-*` …），引用 `$$tokens` 內 name（不寫 token 變數本體）
   6.4 `$variant_branches` = DERIVE conditional className map per `$variant_rules` §2（每個 detected `state`/`variant` enum 值對應一組 Tailwind class diff）
   6.5 `$accessible_name_field` = DERIVE accessible-name source prop per `$anchor_rules` §1 from `$canonical_node` 內可見文字節點
   6.6 `$stories_spec` = DRAFT one entry per `$row.Stories[]`：
       - `export_name` = state name
       - `role` = DERIVE from canonical_node root element（`button` → `"button"`、`input` → `"textbox"`、`label-wrap-input` → `"textbox"`、default → caller-overridable）
       - `accessible_name_arg` = `{ field: $accessible_name_field, value: <該 story 的可見字串> }`
       - `args` = DERIVE per-state prop overrides from variant diff
   6.7 `$plan` = DRAFT `{ identifier: $row.Component, props: $row.DetectedProps, jsx: $jsx_spec, base_class: $base_className, variants: $variant_branches, stories: $stories_spec }`
   6.8 ASSERT `$plan.props` 包含 `$accessible_name_field` name；否則 dispatch `accessible-name-prop-missing`
   6.9 `$$render_plans` = DERIVE append `$plan`
   END LOOP
6. ASSERT count(`$$render_plans`) == count(`$$component_table.rows`)

### Phase 7 — RENDER component .tsx｜把 render plan 落為 TypeScript React component 字串
> produces: `$$component_files`

1. `$tree_rules` = READ [`references/patterns/pen-tree-rendering.md`](references/patterns/pen-tree-rendering.md)
2. `$variant_rules` = READ [`references/patterns/variants-and-states.md`](references/patterns/variants-and-states.md)
3. `$dsl` = READ [`references/dsl-best-practice.md`](references/dsl-best-practice.md)
4. `$$component_files` = DERIVE empty list
5. LOOP per `$plan` in `$$render_plans`
   5.1 `$props_iface` = RENDER `export type ${$plan.identifier}Props = { ... }` from `$plan.props` per TypeScript 型別字串
   5.2 `$jsx_body` = RENDER 巢狀 JSX from `$plan.jsx` per `$tree_rules`，將 leaf text content 用 `{props.<field>}` 綁入
   5.3 `$variant_logic` = RENDER conditional className join from `$plan.variants` per `$variant_rules` §3（純字串 join；禁用 `clsx` / `cn`）
   5.4 `$file_body` = RENDER `export function ${$plan.identifier}(props: ${$plan.identifier}Props) { ... }`（無 React import、無 hooks、無 IO；違反即 ASSERT 失敗）
   5.5 `$file_path` = COMPUTE `${$$target_dir}/${$plan.identifier}/${$plan.identifier}.tsx`
   5.6 `$$component_files` = DERIVE append `{ path: $file_path, body: $props_iface + "\n\n" + $file_body }`
   END LOOP

### Phase 8 — RENDER stories .tsx｜CSF3 stories 雙產出
> produces: `$$story_files`

1. `$anchor_rules` = READ [`references/patterns/binding-anchor.md`](references/patterns/binding-anchor.md)
2. `$$story_files` = DERIVE empty list
3. LOOP per `$plan` in `$$render_plans`
   3.1 `$meta` = RENDER CSF3 meta from `{ title: "Game/${$plan.identifier}", component: ${$plan.identifier}, tags: ["autodocs"], parameters: { layout: "centered" } }`
   3.2 `$exports` = RENDER one CSF3 export per `$plan.stories[]`：
        - `export const ${story.export_name}: Story = { args: { ...meta.args, ...story.args } };`
        - ASSERT `story.accessible_name_arg.value == story.accessible_name`（boundary I4 hard gate）
        - ASSERT `story.accessible_name_arg.field ∈ $plan.props[].name`
   3.3 `$import` = RENDER `import { ${$plan.identifier} } from "./${$plan.identifier}";`
   3.4 `$file_path` = COMPUTE `${$$target_dir}/${$plan.identifier}/${$plan.identifier}.stories.tsx`
   3.5 `$$story_files` = DERIVE append `{ path: $file_path, body: $import + $meta + $exports }`
   END LOOP

### Phase 9 — WRITE files to target_dir
> produces: `$$files_written`

1. `$$files_written` = DERIVE empty list
2. LOOP per `$file` in `$$component_files ⊕ $$story_files`
   2.1 BRANCH path_exists(`$file.path`)
       true:
         2.1.1 IF `$$mode == "create"`: dispatch `target-dir-conflict`（caller 需 mode=overwrite 或先清空）
         2.1.2 IF `$$mode == "overwrite"`: continue
       false: continue
   2.2 CREATE parent dir `dirname($file.path)` if 不存在
   2.3 WRITE `$file.path` ← `$file.body`
   2.4 `$$files_written` = DERIVE append `$file.path`
   END LOOP
3. ASSERT count(`$$files_written`) == 2 * count(`$$render_plans`)

### Phase 10 — REPORT producer
> produces: `$$report`

1. `$$report` = DRAFT {
     status: "completed",
     mode: "producer",
     pen_path: `$$pen_path`,
     screen_id: `$$screen_id`,
     target_dir: `$$target_dir`,
     write_mode: `$$mode`,
     schema_version: `$$schema_version`,
     token_count: count(`$$tokens`),
     tokens: `$$tokens`,
     component_count: count(`$$render_plans`),
     component_table: `$$component_table`,
     files_written: `$$files_written`
   }
2. EMIT `$$report` to caller

### Phase 11 — HANDLE dispatch
> produces: `$$caller_msg`

1. `$failure_kind` = CLASSIFY runtime failure into one of the kinds enumerated in [`references/fail-codes.md`](references/fail-codes.md)
2. `$$caller_msg` = DERIVE caller-return message from `$failure_kind` per [`references/fail-codes.md`](references/fail-codes.md)
3. RETURN `$$caller_msg`

## §3 CROSS-REFERENCES

- 上游：Pencil GUI + MCP（探索期）— 設計者 freeze 後產出 `.pen`；`/aibdd-uiux-discovery` ＋ `/aibdd-uiux-draw` 為 `.pen` 的形成路徑。
- 直接 caller（DELEGATE 入口）：
  - **`/aibdd-plan` Phase 3 design pipeline** — frontend boundary 的 design-source path 改為直接 DELEGATE 本 skill 一條龍。caller payload 含 `pen_path` / `screen_id` / `target_dir`（= `${TRUTH_BOUNDARY_ROOT}/contracts/components/`） / `mode`；本 skill 一次寫完 `<id>.tsx` + `<id>.stories.tsx` 給每個偵測到的 component。
- 直接下游（消費本 skill 產物）：
  - **`/aibdd-green-execute`** — 從 `${TRUTH_BOUNDARY_ROOT}/contracts/components/<id>/<id>.tsx` 與 `.stories.tsx` 直接 import 使用；Green 推薦只在 page 層 / hooks / API client / store / fixtures 補業務邏輯，視覺修改應該回 `.pen` 後重跑本 skill。
  - **`/aibdd-red-execute`** — 從 story export args 派生 `getByRole(role, { name })` locator，呼叫已落地的 component。
- Sibling skill（同 produced-files contract，不同設計來源）：未來 `aibdd-figma-to-storybook` / `aibdd-penpot-to-storybook` 等遵循同一 producer output shape（`status / mode="producer" / files_written / component_count / component_table`），下游 caller 不耦合任一設計來源。
- 與 `/aibdd-form-story-spec` 的邊界：
  - 本 skill = **design-source pipeline**（必有 `.pen`）。
  - form-story-spec = **caller-driven pipeline**（無 `.pen`；caller 自己給 render_hints / props / stories 推理包，常用於從 BDD reasoning 直推、未設計過的 utility component、或 design 不適用的後端 boundary widget）。
  - 同一 component 不該兩條路徑同時寫；caller 二選一。
- 不做：寫回 `.pen`、做視覺探索、選 design system 元件（caller 若想用 shadcn 等，請改走 form-story-spec）、做業務 BDD step 綁定、scaffold Next.js 專案、跑 npm install / tsc / build-storybook（scaffold 屬 `/aibdd-auto-starter`，業務邏輯屬 `/aibdd-green-execute`）。
- 視覺回歸 baseline（optional companion，非本 skill SOP 內步驟）：若 `@pencil.dev/cli` 已安裝且已認證，user 可在本 skill 完成後外部執行 `pencil interactive -i <pen_path> -o /dev/null <<< 'export_nodes({ nodeIds: ["SCREEN_ID"], outputDir: "./baseline" }); exit()'` 自行產 baseline 圖。本 skill 不主動觸發。

## §4 ORPHANED REFERENCES (已棄用，未來清掃)

下列檔案為歷史殘留，**SOP 已不再 LOAD**，保留實體檔以利 git history / 未來考古：

- `references/patterns/project-scaffold.md` — 舊版 scaffold project 用的 package.json / tsconfig / .storybook / app/ 模板。scaffold 已歸 `/aibdd-auto-starter` 的 template 職責。

未來清掃時整批刪除即可，不影響本 skill 行為。
