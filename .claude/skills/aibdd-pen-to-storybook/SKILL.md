---
name: aibdd-pen-to-storybook
description: >
  Convert Pencil `.pen` design files into a Next.js + React + Tailwind + Storybook component library
  — without MCP, without the Pencil desktop app. One-way `freeze-and-implement` pipeline.
  Two modes: scaffold (full Next.js + Storybook project) and adapter (DELEGATE from
  /aibdd-form-story-spec; return component_table + tokens only, no files written).
  Trigger phrases: `.pen 變 storybook`, `generate components from .pen`, `把 .pen 轉成 React`,
  `pencil to storybook`. Use when user has a frozen `.pen` and needs React-based component code
  (Next.js / Remix / plain React; headless / CI; Pencil desktop + MCP not running). Skip when user
  is still exploring visuals, the `.pen` is incomplete, or target stack has no component framework.
metadata:
  user-invocable: true
  source: project-level dogfooding
---

# aibdd-pen-to-storybook

One-way pipeline skill。輸入 `.pen` 設計檔，輸出可 build 的 Next.js 16 + React 19 + Tailwind 4 + Storybook 10
（`@storybook/nextjs-vite`）component 庫。不依賴 Pencil desktop app、不依賴 MCP server，只用 `jq` + Node toolchain。

Stack 鎖定與 `aibdd-auto-starter` 的 `nextjs-storybook-cucumber-e2e` template + `aibdd-form-story-spec` 對齊。

只負責「把已 freeze 的 .pen 翻成 storybook scaffold + components + stories」；不重新做設計、不替設計者做
顆粒度判斷、不對非 React 框架輸出。

## §1 REFERENCES

```yaml
references:
  - path: references/role-and-contract.md
    purpose: caller / user 入口契約 + 角色定位 + 不做事項
  - path: references/format-reference.md
    purpose: '.pen v2.x JSON schema verbatim + framework versions (Next 16 / React 19 / Tailwind 4 / Storybook 10 nextjs-vite)'
  - path: references/dsl-best-practice.md
    purpose: 'Tailwind 4 @theme / CSF3 / Next.js 16 慣例'
  - path: references/patterns/tokens-mapping.md
    purpose: '.pen Document.variables → Tailwind 4 @theme namespace 對照'
  - path: references/patterns/component-detection.md
    purpose: '6 條 component candidate heuristics + 表格輸出契約'
  - path: references/patterns/project-scaffold.md
    purpose: 'package.json / tsconfig / .storybook / app/* 標準骨架'
  - path: references/anti-patterns.md
    purpose: '常見錯誤：framework 拼錯、Tailwind 4 syntax 走 v3、@layer 用錯等'
  - path: references/fail-codes.md
    purpose: 'Phase N dispatch — failure_kind → caller-return message'
```

## §2 SOP

### Phase 1 — ASSERT intake｜驗證入口
> produces: `$$pen_path`, `$$target_dir?`, `$$screen_id?`, `$$output_mode`

1. `$contract` = READ [`references/role-and-contract.md`](references/role-and-contract.md)
2. `$$pen_path` = PARSE user/caller-provided `.pen` 檔絕對路徑
3. `$$target_dir` = PARSE 預期輸出根目錄（e.g. `pencil-ui/`；adapter 模式可省略）
4. `$$screen_id` = PARSE optional 指定 screen ID（缺項則 Phase 4 由 user 確認）
5. `$$output_mode` = PARSE caller-provided `output_mode`（預設 `"scaffold"`；允許值 `"scaffold" | "adapter"`）
6. `$payload_ok` = JUDGE `$$pen_path` against `$contract`
7. ASSERT `$payload_ok`
8. ASSERT path_exists(`$$pen_path`)
9. ASSERT `$$pen_path` 副檔名 == `.pen`
10. ASSERT `$$output_mode` ∈ {`"scaffold"`, `"adapter"`}
11. BRANCH `$$output_mode`
    `"scaffold"` → ASSERT `$$target_dir` non-empty AND (NOT path_exists(`$$target_dir`) OR caller 指定 `mode == "overwrite"`)
    `"adapter"`  → `$$target_dir` / `mode` 在 adapter 模式忽略（不寫任何檔；只回推理包）

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

### Phase 5 — DETECT component candidates｜套用 heuristics + adapter early-return
> produces: `$$component_table`, `$$adapter_report?`

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
8. BRANCH `$$output_mode` == `"adapter"`
   true:
     8.1 `$$adapter_report` = DRAFT {
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
     8.2 RETURN `$$adapter_report`                # adapter mode skip Phase 6-9（不寫檔、不 npm install、不 build）
   false:
     # scaffold mode：自然 fall-through 進入 Phase 6（Phase transition 非 yielding）

### Phase 6 — SCAFFOLD project｜建檔
> produces: `$$scaffold_paths`

1. `$layout` = READ [`references/patterns/project-scaffold.md`](references/patterns/project-scaffold.md)
2. WRITE `$$target_dir/package.json` ← `$layout.package_json`（Next 16 + React 19 + Tailwind 4 + Storybook 10 nextjs-vite）
3. WRITE `$$target_dir/tsconfig.json` ← `$layout.tsconfig`
4. WRITE `$$target_dir/next.config.ts` ← `$layout.next_config`
5. WRITE `$$target_dir/postcss.config.mjs` ← `$layout.postcss_config`
6. WRITE `$$target_dir/next-env.d.ts` ← `$layout.next_env`
7. WRITE `$$target_dir/.storybook/main.ts` ← `$layout.storybook_main`
8. WRITE `$$target_dir/.storybook/preview.ts` ← `$layout.storybook_preview`
9. WRITE `$$target_dir/app/layout.tsx` ← `$layout.app_layout`
10. WRITE `$$target_dir/app/page.tsx` ← `$layout.app_page`
11. `$globals_css` = RENDER `app/globals.css`：
    - L1: font `@import url(...)`（必須最前）
    - L2: `@import "tailwindcss";`
    - L3: `@theme { ... }` 內 LOOP 寫入 `$$tokens` 每一筆 `--<namespace>-<name>: <value>;`
    - L4: `@layer base { body { ... } }`
    - L5: 自訂 `@utility name { ... }`（Tailwind 4 syntax，禁用 v3 的 `@layer utilities`）
12. WRITE `$$target_dir/app/globals.css` ← `$globals_css`
13. `$$scaffold_paths` = DERIVE all written paths above
14. ASSERT 所有檔案 IO 成功；任一失敗 → Phase 10 dispatch `write-io-failed`

### Phase 7 — RENDER components & stories｜逐 row 翻譯
> produces: `$$component_files`, `$$story_files`

1. `$best_practice` = READ [`references/dsl-best-practice.md`](references/dsl-best-practice.md)
2. `$$component_files` = DERIVE empty list
3. `$$story_files` = DERIVE empty list
4. LOOP per `$row` in `$$component_table.rows`
   4.1 `$tsx` = RENDER component file：
       - `export type ${$row.Component}Props = { ... };` 一欄一 prop
       - `export function ${$row.Component}(props): JSX { return <div className="...">…</div> }`
       - className 只走 Tailwind utilities（從 `$$tokens` 派生：`text-<color>` / `bg-<color>` / `rounded-<radius>` / `font-<role>`）
       - 不 `import React`（Next 16 + React 19 自動 JSX runtime）
       - 不引入 `clsx` / `cn`（除非 caller 已加 deps）
   4.2 WRITE `$$target_dir/components/${$row.Component}.tsx` ← `$tsx`
   4.3 `$$component_files` = DERIVE append path
   4.4 `$story` = RENDER `${$row.Component}.stories.tsx`：
       - `import type { Meta, StoryObj } from "@storybook/nextjs-vite";`
       - `import { ${$row.Component} } from "../components/${$row.Component}";`
       - `const meta = { title: "...", component: ${$row.Component} } satisfies Meta<typeof ${$row.Component}>;`
       - `export default meta;` + `type Story = StoryObj<typeof meta>;`
       - LOOP per `$state` in `$row.Stories`：`export const ${$state}: Story = { args: { ... } };`
       - 群組構圖（如 Roster）走 `render: () => <...>` 而非展開 args
   4.5 WRITE `$$target_dir/stories/${$row.Component}.stories.tsx` ← `$story`
   4.6 `$$story_files` = DERIVE append path
   END LOOP
5. ASSERT count(`$$component_files`) == count(`$$component_table.rows`)
6. ASSERT count(`$$story_files`) == count(`$$component_table.rows`)

### Phase 8 — VERIFY｜build 自檢
> produces: `$$verify_report`

1. RUN `cd $$target_dir && npm install`（背景跑；等候完成）
2. ASSERT exit_code == 0；否則 Phase 10 dispatch `npm-install-failed`
3. RUN `cd $$target_dir && npx tsc --noEmit`
4. ASSERT exit_code == 0；否則 Phase 10 dispatch `tsc-error`（先修 TS 錯誤再進 storybook build；storybook 錯誤難 debug）
5. RUN `cd $$target_dir && npm run build-storybook`（30–90s）
6. ASSERT exit_code == 0；否則 Phase 10 dispatch `storybook-build-failed`
7. `$$verify_report` = DRAFT { tsc_ok: true, storybook_build_ok: true, scaffold_paths: `$$scaffold_paths`, component_files: `$$component_files`, story_files: `$$story_files` }

### Phase 9 — REPORT｜回 caller / user
> produces: `$$report`

1. `$$report` = DRAFT {
     status: "completed",
     pen_path: `$$pen_path`,
     screen_id: `$$screen_id`,
     target_dir: `$$target_dir`,
     token_count: count(`$$tokens`),
     component_count: count(`$$component_files`),
     story_count: count(`$$story_files`),
     verify: `$$verify_report`
   }
2. RETURN `$$report`

### Phase 10 — HANDLE dispatch
> produces: `$$caller_msg`

1. `$failure_kind` = CLASSIFY runtime failure into one of the kinds enumerated in [`references/fail-codes.md`](references/fail-codes.md)
2. BRANCH `$failure_kind` == "return-unreachable"
   true:
     2.1 WRITE `${$$target_dir}/.aibdd-pen-to-storybook.report` ← `$$report`
     2.2 STOP
   false:
     2.3 `$$caller_msg` = DERIVE caller-return message from `$failure_kind` per [`references/fail-codes.md`](references/fail-codes.md)
     2.4 RETURN `$$caller_msg`

## §3 CROSS-REFERENCES

- 上游：Pencil GUI + MCP（探索期）— 設計者 freeze 後產出 `.pen`，再交給本 skill。
- 下游 / 觸發者（依 `$$output_mode` 分流）：
  - **scaffold mode**（user-invocable）— 直接被 user 呼叫；產整個 Next.js + Storybook scaffold（components / stories / project files），跑完 Phase 6-9。
  - **adapter mode**（DELEGATE）— 被 `/aibdd-form-story-spec` Phase 1.5 委派；只跑 Phase 1-5 後在 Phase 5.5 提早 RETURN `$$component_table` + `$$tokens`，**不**寫檔、**不** npm install、**不** build。Form-story-spec 拿這個推理包灌進 CSF3 RENDER。
- Sibling 對照：本 skill 與 `aibdd-form-story-spec` + `aibdd-auto-starter` (`nextjs-storybook-cucumber-e2e` template) 同步鎖 **Storybook 10 + `@storybook/nextjs-vite`**。版本鎖 SSOT 在 [`references/format-reference.md`](references/format-reference.md) §7；package.json 模板在 [`references/patterns/project-scaffold.md`](references/patterns/project-scaffold.md) §2。升級任一 lock 前讀 [`references/anti-patterns.md`](references/anti-patterns.md) §2。
- 未來 Sibling：`aibdd-figma-to-storybook` / `aibdd-penpot-to-storybook` 等其他 design-source adapter 將遵循同一 `output_mode=adapter` contract（回 `component_table` + `tokens`），讓 `/aibdd-form-story-spec` 不耦合任一設計來源。
- 不做：寫回 .pen、做視覺探索、選 design system 元件、做業務 BDD step 綁定。
- 視覺回歸 baseline（optional companion，非本 skill SOP 內步驟）：若 `@pencil.dev/cli` 已安裝且已認證，user 可在 Phase 9 RETURN 之後外部執行 `pencil interactive -i <pen_path> -o /dev/null <<< 'export_nodes({ nodeIds: ["SCREEN_ID"], outputDir: "./baseline" }); exit()'` 自行產 baseline 圖。本 skill 不主動觸發。

接著跑 `npm run storybook` 截同 component 比對。CI regression 可用。本 SOP 預設不跑這步。
