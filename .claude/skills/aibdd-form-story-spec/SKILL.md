---
name: aibdd-form-story-spec
description: >
  從推理包翻譯為「Storybook CSF3 stories + React component implementation 雙產出」。
  對 caller 指定的 `target_dir` 寫兩個檔：`<identifier>.tsx`（React component 實作）與
  `<identifier>.stories.tsx`（CSF3 stories；boundary I4 binding anchor SSOT）。
  目標目錄、props、stories、render hints 由 Planner 透過 DELEGATE 參數指定，本 skill 不自決。
  綁定 Storybook 10 + `@storybook/nextjs-vite`；步驟定義從 Story `args` 派生
  `getByRole(role, { name })` locator。
metadata:
  user-invocable: false
  source: project-level dogfooding
---

# aibdd-form-story-spec

Formulation skill。綁定 DSL = Storybook CSF3（`*.stories.tsx`）+ React TSX component（`*.tsx`）。
被 `/aibdd-plan` Phase 3 step 15.5 DELEGATE（當 boundary profile 之
`component_contract_specifier.skill == /aibdd-form-story-spec`）。

對 caller 指定的 `target_dir` 寫兩個共生檔：

1. `<identifier>.tsx` — React component 實作（TypeScript Props interface + named export function + Tailwind className）
2. `<identifier>.stories.tsx` — CSF3 stories（每個 export 為 boundary invariant I4 指定的 UI binding anchor）

兩個檔互為合約：Story `args` 必須對齊 component `Props` interface；component file 由 story file `import` 進來。
Story 檔為 boundary contract truth（per web-frontend invariant I4），component 檔為其視覺實作；兩者均由 plan
階段擁有，**不**留到 `/aibdd-green-execute` Wave 1 才產出。

只負責「把 Planner 推理包翻成 React TSX + CSF3 並寫兩個檔」；不重新判斷 component 顆粒度、不發明 props、不挑選
component file、不創造 design system 元件、不挑 Story 數量、不寫業務邏輯（component 為純視覺實作；data fetching
與 effect 屬 `/aibdd-green-execute`）。

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
  - path: aibdd-core::spec-package-paths.md
    purpose: kickoff boundary-aware path SSOT
  - path: aibdd-core::report-contract.md
    purpose: DELEGATE report 規範
  - path: aibdd-core::preset-contract/web-frontend.md
    purpose: Story export 作為 boundary I4 binding anchor 的契約
  - path: aibdd-core::assets/boundaries/web-frontend/variants/nextjs-playwright.md
    purpose: 'Storybook ≥ 10 / @storybook/nextjs-vite runtime contract'
  - path: references/role-and-contract.md
    purpose: caller payload schema + role boundary（含 component.props / render_hints / target_dir 規則）
  - path: references/format-reference.md
    purpose: 'CSF3 syntax — Meta / StoryObj / args / play / autodocs'
  - path: references/dsl-best-practice.md
    purpose: '命名 / args / argTypes / play / parameters 最佳實踐'
  - path: references/patterns/binding-anchor.md
    purpose: 'I4 — accessible-name args 必備；locator 派生規範'
  - path: references/patterns/states-and-variants.md
    purpose: 一個 component 拆多個 Story export 的判準
  - path: references/patterns/component-rendering.md
    purpose: 'React component .tsx 渲染規約（Props interface / 函式 export / Tailwind className / JSX 結構）'
  - path: references/anti-patterns.md
    purpose: '反例（無 accessible-name / 共享可變狀態 / hard-code 私有 selector）'
  - path: references/fail-codes.md
    purpose: 'Phase 6 fallback dispatch table — failure_kind → caller-return message'
```

## §2 SOP

### Phase 1 — ASSERT intake｜驗證 caller payload + 解析 design source
> produces: `$$payload`, `$$target_dir`, `$$component`, `$$component_props`, `$$render_hints`, `$$stories`, `$$story_target_path`, `$$component_target_path`, `$$design_source`, `$$design_component_table?`, `$$design_tokens?`

1. `$contract` = READ [`references/role-and-contract.md`](references/role-and-contract.md)
2. `$$payload` = READ caller payload
3. `$$target_dir` = PARSE `$$payload.target_dir`
4. `$reasoning` = PARSE `$$payload.reasoning`
5. `$$component` = PARSE `$reasoning.component_modeling.component`
6. `$$component_props` = PARSE `$$component.props`
7. `$$render_hints` = PARSE `$$component.render_hints` (optional, default `{}`)
8. `$$stories` = PARSE `$reasoning.component_modeling.stories`
9. `$framework` = PARSE `$reasoning.component_modeling.framework`
10. `$exit_status` = PARSE `$reasoning.component_modeling.exit_status`
11. `$payload_ok` = JUDGE `$$payload` against `$contract`
12. ASSERT `$payload_ok`
13. ASSERT `$$target_dir` non-empty
14. ASSERT `$$target_dir` is absolute path OR resolves under workspace root
15. ASSERT `$$component.identifier` non-empty AND PascalCase
16. `$$component_target_path` = COMPUTE `${$$target_dir}/${$$component.identifier}.tsx`
17. `$$story_target_path` = COMPUTE `${$$target_dir}/${$$component.identifier}.stories.tsx`
18. ASSERT count(`$$component_props`) >= 0  # zero props OK；form 為純展示元件時無 props
19. LOOP per `$prop` in `$$component_props`
    19.1 ASSERT `$prop.name` is camelCase non-empty JS identifier
    19.2 ASSERT `$prop.type` is non-empty TypeScript type literal
    19.3 ASSERT `$prop.required ∈ {true, false}`
    19.4 IF `$prop.required == false` AND `$prop.default` is set:
        19.4.1 ASSERT `$prop.default` is JSON-serialisable
    END LOOP
20. ASSERT count(`$$stories`) >= 1
21. LOOP per `$story` in `$$stories`
    21.1 ASSERT `$story.export_name` is PascalCase non-empty
    21.2 ASSERT `$story.accessible_name` non-empty                       # I4 hard gate；缺 → caller fix
    21.3 ASSERT `$story.role` non-empty                                  # ARIA role 來源
    21.4 ASSERT `$story.accessible_name_arg.field` non-empty
    21.5 ASSERT `$story.accessible_name_arg.value` non-empty
    21.6 ASSERT `$story.accessible_name == $story.accessible_name_arg.value`  # 同步守門；對齊 binding-anchor.md §5
    21.7 ASSERT `$story.accessible_name_arg.field ∈ $$component_props[*].name`  # accessible-name arg 必須是 component 真實 prop
    END LOOP
22. ASSERT `$framework == "@storybook/nextjs-vite"` OR `$framework` matches caller-allowed list
23. ASSERT `$exit_status == "complete"`
24. `$$design_source` = PARSE `$$payload.design_source`（optional；缺省 `{ kind: "none" }`）
25. BRANCH `$$design_source.kind`
    `"none"` → `$$design_component_table` = `$$design_tokens` = null; GOTO #2.1
    `"pen"`  → GOTO #1.26
    other    → ASSERT false; STOP with "unsupported design_source.kind: ${$$design_source.kind}"
26. ASSERT path_exists(`$$design_source.path`)
27. ASSERT `$$design_source.path` 副檔名 == `.pen`
28. `$adapter_payload` = DRAFT {
      pen_path: `$$design_source.path`,
      screen_id: `$$design_source.screen_id`
    }
    # 注意：`aibdd-pen-to-storybook` 已簡化為 adapter-only，payload 不再接受 `output_mode` / `target_dir` / `mode` 等舊 scaffold 欄位。
29. `$adapter_report` = DELEGATE `aibdd-pen-to-storybook` with `$adapter_payload`
30. ASSERT `$adapter_report.status == "completed"` AND `$adapter_report.mode == "adapter"`  # mode 由 adapter 端固定回 "adapter"，此處 sanity check
31. `$$design_component_table` = PARSE `$adapter_report.component_table`
32. `$$design_tokens` = PARSE `$adapter_report.tokens`
33. `$design_row` = MATCH `$$design_component_table.rows[]` where `Component == $$component.identifier`
34. BRANCH `$design_row` is null
    true:
      34.1 EMIT "warn: component '${$$component.identifier}' 未在 .pen 派生 component table 中找到（caller reasoning 仍 authoritative，僅 cross-check 提示）" to user
    false:
      34.2 `$design_variants` = DERIVE `$design_row.Stories[]`
      34.3 LOOP per `$story` in `$$stories`
           34.3.1 BRANCH `$story.export_name` ∈ `$design_variants`
               true:  continue
               false: EMIT "warn: story '${$story.export_name}' 不在 .pen variants [${$design_variants}]（caller reasoning 仍 authoritative）" to user
           END LOOP

> 角色界線：步驟 24–34 只做 **design-source cross-check + warn**，**不** override `$$component` / `$$stories` / `$$component_props`。
> caller reasoning（從 Planner 推理包來）是 authoritative。`$$design_tokens` 可由 caller 在 `$$render_hints.tailwind_classes` 顯式攜帶進入 Phase 2 component RENDER；本 skill 不替 caller 注入 token。

### Phase 2 — RENDER React component .tsx + CSF3 stories.tsx
> produces: `$$component_doc`, `$$story_doc`

#### Phase 2A — RENDER component .tsx
> produces: `$$component_doc`

1. `$rendering_rules` = READ [`references/patterns/component-rendering.md`](references/patterns/component-rendering.md)
2. `$props_block` = RENDER TypeScript Props interface ← `$$component.identifier`, `$$component_props`:
   - line: `export type ${$$component.identifier}Props = {`
   - LOOP per `$prop` in `$$component_props`:
       - `$optional` = RENDER `?` if `$prop.required == false` else empty
       - `$default_comment` = RENDER `  // default: ${$prop.default}` if `$prop.default` is set else empty
       - line: `  ${$prop.name}${$optional}: ${$prop.type};${$default_comment}`
   - line: `};`
3. `$root_element` = DERIVE `$$render_hints.root_element` (default `"div"`)
4. `$base_class` = DERIVE `$$render_hints.base_class` (default empty string)
5. `$jsx_pattern` = DERIVE `$$render_hints.children_layout` (default `"leaf"`)
6. BRANCH `$jsx_pattern`
   `"leaf"`           → `$jsx_body` = RENDER `<${$root_element} className="${$base_class}" />`（無子元素）
   `"text"`           → `$jsx_body` = RENDER `<${$root_element} className="${$base_class}">{props.children ?? null}</${$root_element}>`
   `"labeled-input"`  → `$jsx_body` = RENDER labeled input 結構（`<label>` 包 `<input>` + accessible-name binding 來源 `$$render_hints.accessible_name_prop`）per [`references/patterns/component-rendering.md`](references/patterns/component-rendering.md) §3
   `"button"`         → `$jsx_body` = RENDER `<button>` 結構（`type` 由 `$$render_hints.button_type` 決定，default `"button"`；accessible name 由 caller 指定的 prop 內嵌） per [`references/patterns/component-rendering.md`](references/patterns/component-rendering.md) §4
   `"container"`      → `$jsx_body` = RENDER `<${$root_element} className="${$base_class}">{props.children}</${$root_element}>`（要求 `Props.children: React.ReactNode`）
   other              → ASSERT false; STOP with "unsupported render_hints.children_layout: ${$jsx_pattern}"
7. `$function_block` = RENDER named export function:
   - line: `export function ${$$component.identifier}(props: ${$$component.identifier}Props) {`
   - line: `  return (`
   - line: `    ${$jsx_body}`
   - line: `  );`
   - line: `}`
8. `$$component_doc` = DERIVE concatenation of `$props_block`, blank line, `$function_block`
9. ASSERT `$$component_doc` does not contain `import React`           # React 19 + Next 16 自動 JSX runtime
10. ASSERT `$$component_doc` does not contain `import { clsx }` OR `import { cn }`  # caller payload 必須提供 base_class 字串；不引入 utility lib
11. ASSERT `$$component_doc` contains `export type ${$$component.identifier}Props`
12. ASSERT `$$component_doc` contains `export function ${$$component.identifier}(`

#### Phase 2B — RENDER CSF3 stories.tsx
> produces: `$$story_doc`

1. `$syntax_map` = READ [`references/format-reference.md`](references/format-reference.md)
2. `$best_practice` = READ [`references/dsl-best-practice.md`](references/dsl-best-practice.md)
3. `$binding` = READ [`references/patterns/binding-anchor.md`](references/patterns/binding-anchor.md)
4. `$variants` = READ [`references/patterns/states-and-variants.md`](references/patterns/states-and-variants.md)
5. `$header_imports` = RENDER:
   - `import type { Meta, StoryObj } from "${$framework}";`
   - IF any `$story.has_action_args` → also `import { fn } from "storybook/test";`
   - IF any `$story.has_play` → also `import { expect } from "storybook/test";`
   - `import { ${$$component.identifier} } from "./${$$component.identifier}";`     # 同 target_dir co-located；相對 import
6. `$meta_block` = RENDER `default export` Meta block:
   - `title: "${$$component.title}"`           # e.g. `"Components/RoomCodeInput"` — caller-supplied
   - `component: ${$$component.identifier}`
   - IF `$$component.parameters` → `parameters: { ... }`
   - IF `$$component.tags` → `tags: [...]`     # `"autodocs"` 預設加入除非 caller 明示禁用
   - IF `$$component.argTypes` → `argTypes: { ... }`
   - IF `$$component.shared_args` → `args: { ... }`
   - SUFFIX `satisfies Meta<typeof ${$$component.identifier}>`
7. `$type_alias` = RENDER `type Story = StoryObj<typeof meta>;`
8. `$story_blocks` = DERIVE empty list
9. LOOP per `$story` in `$$stories`
   9.1 `$args_block` = RENDER `args: { ${$story.args}, ${$story.accessible_name_arg} }`
       - `accessible_name_arg` 形如 `label: "Submit"` / `aria-label: "Close dialog"` / `name: "Email"`
         （由 caller 推理包指定欄位名稱與值；本 skill 不發明）
   9.2 BRANCH `$story.has_play`
       true:
         9.2.1 `$play_fn` = RENDER `play: async ({ canvas, userEvent }) => { ... }`
                依 `$story.play_steps[]` 依序展開為 `userEvent.click / userEvent.type / await expect(...)`
         9.2.2 `$body` = DERIVE concatenation of `$args_block` and `$play_fn`
       false:
         9.2.3 `$body` = DERIVE `$args_block` unchanged (no play function)
   9.3 `$line` = RENDER `export const ${$story.export_name}: Story = { ${$body} };`
   9.4 `$story_blocks` = DERIVE append `$line`
   END LOOP
10. `$$story_doc` = DERIVE concatenation of `$header_imports`, `$meta_block`, `"export default meta;"`, `$type_alias`, and `$story_blocks`
11. ASSERT `$$story_doc` contains `import type { Meta, StoryObj }`
12. ASSERT `$$story_doc` contains `export default meta;`
13. ASSERT `$$story_doc` contains `satisfies Meta<typeof ${$$component.identifier}>`
14. ASSERT `$$story_doc` contains `import { ${$$component.identifier} } from "./${$$component.identifier}"`  # 與 component .tsx 在 target_dir co-located 對齊

### Phase 3 — WRITE artifacts｜逐檔寫入
> produces: `$$written_paths`

1. CREATE `$$target_dir` (idempotent — 若已存在則 skip)
2. `$component_exists` = MATCH path_exists(`$$component_target_path`)
3. BRANCH `$component_exists` ∧ `$$payload.mode != "overwrite"`
   true:
     3.1 `$msg` = DRAFT "path 衝突：component_target_path 已存在 (${$$component_target_path})；caller 需指定 mode=overwrite 或改 target_dir / identifier"
     3.2 RETURN `$msg`
   false:
     3.3 WRITE `$$component_target_path` ← `$$component_doc`
4. `$story_exists` = MATCH path_exists(`$$story_target_path`)
5. BRANCH `$story_exists` ∧ `$$payload.mode != "overwrite"`
   true:
     5.1 `$msg` = DRAFT "path 衝突：story_target_path 已存在 (${$$story_target_path})；caller 需指定 mode=overwrite 或改 target_dir / identifier"
     5.2 # rollback：刪掉剛寫的 component file 以避免半成品殘留
     5.3 IF NOT `$component_exists`: DELETE `$$component_target_path`
     5.4 RETURN `$msg`
   false:
     5.5 WRITE `$$story_target_path` ← `$$story_doc`
6. `$$written_paths` = DERIVE [`$$component_target_path`, `$$story_target_path`]
7. ASSERT `$$component_target_path` in `$$written_paths`
8. ASSERT `$$story_target_path` in `$$written_paths`

### Phase 4 — VALIDATE syntax｜雙檔結構自檢
> produces: `$$validation_report`

1. `$component_checks` = DERIVE list:
   - `$$component_doc` contains `export type ${$$component.identifier}Props`
   - `$$component_doc` contains `export function ${$$component.identifier}(`
   - `$$component_doc` does not contain `import React`
   - `$$component_doc` does not contain `import { clsx }` OR `import { cn }`
   - `$$component_doc` does not contain `useState` / `useEffect` / `useMemo` / `useReducer` / `useContext`  # form-story-spec 只寫純展示元件；hooks 屬 green-execute
   - `$$component_doc` does not contain `fetch(` / `XMLHttpRequest` / `axios`              # 無 IO；business logic 屬 green-execute
2. `$story_checks` = DERIVE list:
   - default export 存在且為 Meta block
   - 每個 named export 為 `StoryObj<typeof meta>`
   - 每個 named export 之 `args` 含 caller 指定之 `accessible_name_arg`（依 `$$stories[i].accessible_name_arg.field`）
   - 無 `import { storiesOf }` 等 CSF2 / 殘留語法
   - 無 `export default { ... }` 內出現 `Story` decorators 之 mutable closure 共享
   - story file `import` 路徑為 co-located 相對 import (`./${identifier}`)，不為絕對路徑或跨目錄路徑
3. `$findings_component` = MATCH each pattern in `$component_checks` against `$$component_doc`
4. `$findings_story` = MATCH each pattern in `$story_checks` against `$$story_doc`
5. `$$validation_report` = DRAFT {
     ok: count(`$findings_component`.failed) == 0 AND count(`$findings_story`.failed) == 0,
     component_findings: `$findings_component`,
     story_findings: `$findings_story`
   }
6. ASSERT `$$validation_report.ok == true`

### Phase 5 — RETURN report｜回傳 caller 訊號
> produces: `$$report`

1. `$$report` = DRAFT report JSON per `aibdd-core::report-contract.md` ← {
     status: "completed",
     target_dir: `$$target_dir`,
     component_target_path: `$$component_target_path`,
     story_target_path: `$$story_target_path`,
     written_paths: `$$written_paths`,
     story_count: count(`$$stories`),
     props_count: count(`$$component_props`),
     binding_anchors: `$$stories[].export_name`,
     syntax_valid: `$$validation_report.ok`,
     validation_report: `$$validation_report`
   }
2. RETURN `$$report`

### Phase 6 — HANDLE fallback
> produces: `$$caller_msg`

1. `$failure_kind` = CLASSIFY runtime failure into one of the kinds enumerated in [`references/fail-codes.md`](references/fail-codes.md)
2. BRANCH `$failure_kind` == "return-unreachable"
   true:
     2.1 WRITE `${$$target_dir}/.${$$component.identifier}.report` ← `$$report`
     2.2 STOP
   false:
     2.3 `$$caller_msg` = DERIVE caller-return message from `$failure_kind` per [`references/fail-codes.md`](references/fail-codes.md)
     2.4 RETURN `$$caller_msg`

## §3 CROSS-REFERENCES

- `/aibdd-discovery` — upstream UI flow 收斂；留下 component / state hint 給前端 component-modeling planner（目前 chain 為 aspirational，尚無單一 producer 直接餵本 skill）。
- `/aibdd-uiux-discovery` — upstream design brief；emit `design/uiux-prompt.md` + `design/style-profile.yml`，引導 user 在 Pencil 落 `design.pen`。本 skill 於 Phase 1 後段透過 `design_source.path` 接這個 `.pen` 做 cross-check。
- `aibdd-pen-to-storybook`（adapter-only skill）— DELEGATE 對象；當 `design_source.kind == "pen"` 時 Phase 1 步驟 24–34 呼叫之取 `component_table` + `tokens` 做 cross-check。adapter skill 已簡化為 read-only：payload 只接受 `pen_path` + 可選 `screen_id`，回傳 fixed shape `{ status, mode, schema_version, token_count, tokens, component_count, component_table }`。**未來 sibling**：`aibdd-figma-to-storybook` / `aibdd-penpot-to-storybook` 等其他 design-source adapter 將遵循同一 return shape contract 並列。
- `/aibdd-plan` — upstream caller；Phase 3 step 15.5 偵測 `${CURRENT_PLAN_PACKAGE}/design.pen` 存在時，自動把 `design_source` 注入本 skill 的 caller payload，並把 `target_dir` 推導為 `${TRUTH_BOUNDARY_ROOT}/contracts/components/<ComponentId>/`。
- `/aibdd-spec-by-example-analyze` — downstream consumer；其 `web-frontend` preset 將本 skill 產出之 Story export 寫進 `L4.source_refs.component`，路徑形如 `${CONTRACTS_DIR}/components/<ComponentId>/<ComponentId>.stories.tsx::<ExportName>`。
- `/aibdd-red-execute` — `nextjs-playwright` variant 從 Story `args` 派生 `getByRole(role, { name })` locator；boundary I4 在此被執行。
- `/aibdd-green-execute` — downstream extender；在本 skill 寫出的 component .tsx 上補業務邏輯（hooks、effects、API calls、conditional rendering）。本 skill 不寫這些，只給 caller 一個可 import 的純視覺 scaffold + 完整 stories。
- `aibdd-core::preset-contract/web-frontend.md` — boundary I4 SSOT，本 skill 對齊其 Story-export-as-binding-anchor 規定。
- `aibdd-core::assets/boundaries/web-frontend/variants/nextjs-playwright.md` — Storybook 10 / `@storybook/nextjs-vite` runtime contract；變更 framework 必同步更新此 variant 文件。
- 不做：新增 model element、改 component file（在第二次 invoke 時 mode=overwrite 由 caller 顯式授權才覆蓋）、挑 design system 元件、繞過 boundary I4 anchor、override caller reasoning（Phase 1 後段只 cross-check + warn）、寫業務邏輯、引入 hooks、做 IO。
