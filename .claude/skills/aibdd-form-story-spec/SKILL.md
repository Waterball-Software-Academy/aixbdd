---
name: aibdd-form-story-spec
description: >
  從推理包翻譯為 Storybook CSF3 stories（`*.stories.ts` / `*.stories.tsx`）。負責 CSF3 語法規章 + 歸檔。
  綁定 Storybook 10 + `@storybook/nextjs-vite`；每個 Story export 為 boundary invariant I4
  指定的 UI binding anchor（步驟定義從 Story `args` 派生 `getByRole(role, { name })` locator）。
  目標路徑、切檔策略、要產出的 Story export 清單由 Planner 透過 DELEGATE 參數指定，本 skill 不自決。
metadata:
  user-invocable: false
  source: project-level dogfooding
---

# aibdd-form-story-spec

Formulation skill。綁定 DSL = Storybook CSF3（`*.stories.ts` / `*.stories.tsx`）。
被 `/aibdd-plan` Phase 3 step 15.5 DELEGATE（當 boundary profile 之
`component_contract_specifier.skill == /aibdd-form-story-spec`）。Plan 把已收斂的 component modeling
units（identifier、import_path、title、stories[]（export_name + role + accessible_name + accessible_name_arg
+ optional play steps）翻譯成可被 step-def 綁定的 Story 檔（CSF3）。
Story 檔為 boundary contract truth（per web-frontend invariant I4），由 plan 階段擁有，**不**留到
`/aibdd-green-execute` Wave 1 才產出。

只負責「把 Planner 推理包翻成 CSF3 並落檔」；不重新判斷 component 顆粒度、不發明 props、不挑選
component file、不創造 design system 元件、不挑 Story 數量。

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
    purpose: caller payload schema + role boundary
  - path: references/format-reference.md
    purpose: 'CSF3 syntax — Meta / StoryObj / args / play / autodocs'
  - path: references/dsl-best-practice.md
    purpose: '命名 / args / argTypes / play / parameters 最佳實踐'
  - path: references/patterns/binding-anchor.md
    purpose: 'I4 — accessible-name args 必備；locator 派生規範'
  - path: references/patterns/states-and-variants.md
    purpose: 一個 component 拆多個 Story export 的判準
  - path: references/anti-patterns.md
    purpose: '反例（無 accessible-name / 共享可變狀態 / hard-code 私有 selector）'
  - path: references/fail-codes.md
    purpose: 'Phase 6 fallback dispatch table — failure_kind → caller-return message'
```

## §2 SOP

### Phase 1 — ASSERT intake｜驗證 caller payload + 解析 design source
> produces: `$$payload`, `$$target_path`, `$$format`, `$$component`, `$$stories`, `$$design_source`, `$$design_component_table?`, `$$design_tokens?`

1. `$contract` = READ [`references/role-and-contract.md`](references/role-and-contract.md)
2. `$$payload` = READ caller payload
3. `$$target_path` = PARSE `$$payload.target_path`
4. `$$format` = PARSE `$$payload.format`
5. `$reasoning` = PARSE `$$payload.reasoning`
6. `$$component` = PARSE `$reasoning.component_modeling.component`
7. `$$stories` = PARSE `$reasoning.component_modeling.stories`
8. `$framework` = PARSE `$reasoning.component_modeling.framework`
9. `$exit_status` = PARSE `$reasoning.component_modeling.exit_status`
10. `$payload_ok` = JUDGE `$$payload` against `$contract`
11. ASSERT `$payload_ok`
12. ASSERT `$$target_path` non-empty
13. ASSERT `$$format ∈ {".stories.ts", ".stories.tsx"}`
14. ASSERT `$$target_path` ends with `$$format`
15. ASSERT `$$component.import_path` non-empty
16. ASSERT `$$component.identifier` non-empty
17. ASSERT count(`$$stories`) >= 1
18. LOOP per `$story` in `$$stories`
    18.1 ASSERT `$story.export_name` is PascalCase non-empty
    18.2 ASSERT `$story.accessible_name` non-empty                       # I4 hard gate；缺 → caller fix
    18.3 ASSERT `$story.role` non-empty                                  # ARIA role 來源
    18.4 ASSERT `$story.accessible_name_arg.field` non-empty
    18.5 ASSERT `$story.accessible_name_arg.value` non-empty
    18.6 ASSERT `$story.accessible_name == $story.accessible_name_arg.value`  # 同步守門；對齊 binding-anchor.md §5
    END LOOP
19. ASSERT `$framework == "@storybook/nextjs-vite"` OR `$framework` matches caller-allowed list
20. ASSERT `$exit_status == "complete"`
21. `$$design_source` = PARSE `$$payload.design_source`（optional；缺省 `{ kind: "none" }`）
22. BRANCH `$$design_source.kind`
    `"none"` → `$$design_component_table` = `$$design_tokens` = null; RETURN（end Phase 1；Phase 2 進入純 caller reasoning 流程）
    `"pen"`  → GOTO #1.23
    other    → ASSERT false; STOP with "unsupported design_source.kind: ${$$design_source.kind}"
23. ASSERT path_exists(`$$design_source.path`)
24. ASSERT `$$design_source.path` 副檔名 == `.pen`
25. `$adapter_payload` = DRAFT {
      pen_path: `$$design_source.path`,
      screen_id: `$$design_source.screen_id`,
      output_mode: `"adapter"`
    }
26. `$adapter_report` = DELEGATE `aibdd-pen-to-storybook` with `$adapter_payload`
27. ASSERT `$adapter_report.status == "completed"` AND `$adapter_report.mode == "adapter"`
28. `$$design_component_table` = PARSE `$adapter_report.component_table`
29. `$$design_tokens` = PARSE `$adapter_report.tokens`
30. `$design_row` = MATCH `$$design_component_table.rows[]` where `Component == $$component.identifier`
31. BRANCH `$design_row` is null
    true:
      31.1 EMIT "warn: component '${$$component.identifier}' 未在 .pen 派生 component table 中找到（caller reasoning 仍 authoritative，僅 cross-check 提示）" to user
    false:
      31.2 `$design_variants` = DERIVE `$design_row.Stories[]`
      31.3 LOOP per `$story` in `$$stories`
           31.3.1 BRANCH `$story.export_name` ∈ `$design_variants`
               true:  continue
               false: EMIT "warn: story '${$story.export_name}' 不在 .pen variants [${$design_variants}]（caller reasoning 仍 authoritative）" to user
           END LOOP

> 角色界線：步驟 21–31 只做 **design-source cross-check + warn**，**不** override `$$component` / `$$stories`。
> caller reasoning（從 Planner 推理包來）是 authoritative。`$$design_tokens` 可由 caller 在 `$$component.parameters.designTokens` 顯式攜帶進入 Phase 2 Meta；本 skill 不替 caller 注入 token。

### Phase 2 — RENDER CSF3 document｜逐 Story 翻譯
> produces: `$$story_doc`

1. `$syntax_map` = READ [`references/format-reference.md`](references/format-reference.md)
2. `$best_practice` = READ [`references/dsl-best-practice.md`](references/dsl-best-practice.md)
3. `$binding` = READ [`references/patterns/binding-anchor.md`](references/patterns/binding-anchor.md)
4. `$variants` = READ [`references/patterns/states-and-variants.md`](references/patterns/states-and-variants.md)
5. `$header_imports` = RENDER:
   - `import type { Meta, StoryObj } from "${$framework}";`
   - IF any `$story.has_action_args` → also `import { fn } from "storybook/test";`
   - IF any `$story.has_play` → also `import { expect } from "storybook/test";`
   - `import { ${$$component.identifier} } from "${$$component.import_path}";`
6. `$meta_block` = RENDER `default export` Meta block:
   - `title: "${$$component.title}"`           # e.g. `"Example/Button"` — caller-supplied
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

### Phase 3 — WRITE artifact｜寫入 Story 檔
> produces: `$$written_paths`

1. `$target_exists` = MATCH path_exists(`$$target_path`)
2. BRANCH `$target_exists` ∧ `$$payload.mode != "overwrite"`
   true:
     2.1 `$msg` = DRAFT "path 衝突：target_path 已存在，caller 需指定 mode=overwrite 或改 target_path"
     2.2 RETURN `$msg`
   false:
     2.3 WRITE `$$target_path` ← `$$story_doc`
3. `$$written_paths` = DERIVE [`$$target_path`]
4. ASSERT `$$target_path` in `$$written_paths`

### Phase 4 — VALIDATE syntax｜CSF3 結構自檢
> produces: `$$validation_report`

1. `$checks` = DERIVE list:
   - default export 存在且為 Meta block
   - 每個 named export 為 `StoryObj<typeof meta>`
   - 每個 named export 之 `args` 含 caller 指定之 `accessible_name_arg`（依 `$$stories[i].accessible_name_arg.field`）
   - 無 `import { storiesOf }` 等 CSF2 / 殘留語法
   - 無 `export default { ... }` 內出現 `Story` decorators 之 mutable closure 共享
2. `$findings` = MATCH each pattern in `$checks` against `$$story_doc`
3. `$$validation_report` = DRAFT { ok: count(`$findings`.failed) == 0, findings: `$findings` }
4. ASSERT `$$validation_report.ok == true`

### Phase 5 — RETURN report｜回傳 caller 訊號
> produces: `$$report`

1. `$$report` = DRAFT report JSON per `aibdd-core::report-contract.md` ← {
     status: "completed",
     target_path: `$$target_path`,
     written_paths: `$$written_paths`,
     story_count: count(`$$stories`),
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
     2.1 WRITE `${$$target_path}.report` ← `$$report`
     2.2 STOP
   false:
     2.3 `$$caller_msg` = DERIVE caller-return message from `$failure_kind` per [`references/fail-codes.md`](references/fail-codes.md)
     2.4 RETURN `$$caller_msg`

## §3 CROSS-REFERENCES

- `/aibdd-discovery` — upstream UI flow 收斂；留下 component / state hint 給前端 component-modeling planner（目前 chain 為 aspirational，尚無單一 producer 直接餵本 skill）。
- `/aibdd-uiux-discovery` — upstream design brief；emit `design/uiux-prompt.md` + `design/style-profile.yml`，引導 user 在 Pencil 落 `design.pen`。本 skill 於 Phase 1.5 透過 `design_source.path` 接這個 `.pen`。
- `aibdd-pen-to-storybook`（adapter mode）— DELEGATE 對象；當 `design_source.kind == "pen"` 時 Phase 1.5 呼叫 `output_mode="adapter"` 取 `component_table` + `tokens` 做 cross-check。**未來 sibling**：`aibdd-figma-to-storybook` / `aibdd-penpot-to-storybook` 等其他 design-source adapter 將以同一 `output_mode=adapter` contract 並列。
- `/aibdd-plan` — upstream caller；Phase 3 step 15.5 偵測 `${CURRENT_PLAN_PACKAGE}/design.pen` 存在時，自動把 `design_source` 注入本 skill 的 caller payload。
- `/aibdd-spec-by-example-analyze` — downstream consumer；其 `web-frontend` preset 將本 skill 產出之 Story export 寫進 `L4.source_refs.component`。
- `/aibdd-red-execute` — `nextjs-playwright` variant 從 Story `args` 派生 `getByRole(role, { name })` locator；boundary I4 在此被執行。
- `aibdd-core::preset-contract/web-frontend.md` — boundary I4 SSOT，本 skill 對齊其 Story-export-as-binding-anchor 規定。
- `aibdd-core::assets/boundaries/web-frontend/variants/nextjs-playwright.md` — Storybook 10 / `@storybook/nextjs-vite` runtime contract；變更 framework 必同步更新此 variant 文件。
- 不做：新增 model element、改 component file、挑 design system 元件、繞過 boundary I4 anchor、override caller reasoning（Phase 1.5 只 cross-check + warn）。
