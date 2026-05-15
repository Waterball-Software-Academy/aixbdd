# 角色 + 入口契約

> 純 declarative reference。Phase 1 LOAD 取入口 schema 與角色定位。

## §1 角色定位

**Producer skill**。輸入 = Pencil `.pen` 設計檔 + `target_dir`。輸出 = 對每個偵測到的 component 在
`target_dir/<ComponentId>/` 寫出兩檔：

```
${target_dir}/<ComponentId>/
├── <ComponentId>.tsx              ← React component 實作（Tailwind 4 utility class 完整、含 variant conditional className）
└── <ComponentId>.stories.tsx      ← CSF3 stories（boundary I4 binding anchor SSOT）
```

**做**：

- 解析 `.pen` JSON
- 抽 design tokens（Tailwind 4 namespace 對照）
- 挑 single screen
- 跑 component candidate detection（heuristics）
- 從 `.pen` 節點樹推導每個 component 的巢狀 JSX + Tailwind utility class + variant conditional className
- 推導每個 detected state/variant 對應的 CSF3 story export（含 boundary I4 binding anchor `role` + `accessible_name`）
- 把 `<ComponentId>.tsx` 與 `<ComponentId>.stories.tsx` co-located 寫到 `${target_dir}/<ComponentId>/`
- 回 producer report（含 `files_written` / `component_table` / `tokens`）給 caller

**不做**：

- 不修改原 `.pen`（單向 read-only on input）
- 不挑 component 顆粒度規則 — heuristics 屬 [`patterns/component-detection.md`](patterns/component-detection.md)，本 skill 只執行
- 不換 framework target — 綁定 React 19 + Next.js 16 + Tailwind 4 + `@storybook/nextjs-vite`
- 不引入額外 deps、不修 `tsconfig.json` / `.storybook/main.ts` / `vitest.config.ts`（那是 `/aibdd-auto-starter` 的 template 職責）
- 不建專案、不跑 `npm install`、不跑 `tsc`、不跑 `build-storybook`
- 不替 Pencil GUI 做視覺探索 — 探索期請走 Pencil + MCP（或 `/aibdd-uiux-draw`）
- 不在 component 寫業務邏輯（hooks / fetch / state machines）— 屬 `/aibdd-green-execute`
- 不在 component 寫 default param assignment / runtime default value — 屬 `/aibdd-green-execute`
- 不寫 page-level 組裝（`app/page.tsx` / `app/(route)/page.tsx`）— 屬 `/aibdd-green-execute`
- 不替 caller 解析非 `.pen` 來源 — 那是 `/aibdd-form-story-spec`（caller-driven）或 sibling adapter（figma / penpot）

## §2 入口契約 — caller payload schema

```yaml
pen_path: <string, required>           # 絕對路徑，副檔名必為 .pen

screen_id: <string?>                   # optional — 指定要轉換哪一個 top-level frame
                                       # 缺項 → Phase 4 回 caller 候選清單再確認

target_dir: <string, required>         # 絕對路徑；寫檔根目錄
                                       # 慣例：${TRUTH_BOUNDARY_ROOT}/contracts/components/
                                       # 例：specs/boss-fe/contracts/components/
                                       #
                                       # 每個偵測到的 component 在底下開一個 <ComponentId>/ 子目錄

mode: "create" | "overwrite"           # 預設 "create"
                                       # create   = 任何目標檔已存在即 fail (target-dir-conflict)
                                       # overwrite = 已存在則覆寫；對全部 components 一致生效
```

### 不允許在 payload 出現的東西

- `framework_target` / `verify` / `output_mode` — 框架已綁定，verify 改由 Green/Red 各自負責；本 skill 不接受
- 多個 `screen_id`（每次只轉一個 screen — 避免 component detection 在跨 screen 混淆抽象）
- `screen_id` 含 slash — `.pen` 規格禁止 id 含 `/`，本 skill 直接拒收
- `render_hints` / `component_modeling` / `props` 等 caller-side reasoning override —
  本 skill 從 `.pen` + heuristics 直推；caller 若想顯式控制 props/JSX，請改走 `/aibdd-form-story-spec`
- 部分 component overwrite（mode 一次性對全部 detected components 生效；caller 要選擇性更新請手動刪檔後 mode=create）

## §3 缺項處理

- `pen_path` 缺項 / 不存在 / 非 `.pen`：Phase 1 fail，dispatch `pen-path-invalid`
- `target_dir` 缺項 / 非絕對路徑 / parent 不存在：Phase 1 fail，dispatch `target-dir-invalid`
- `mode` 不在 enum 內：Phase 1 fail（透過 ASSERT 阻擋，無獨立 fail kind）
- `screen_id` 缺項：Phase 4 列 top-level frame 候選清單回 caller，等 caller 補後重啟 Phase 4
- `.pen` 解析失敗（binary / 舊版）：Phase 2 fail，dispatch `pen-not-parseable`
- 偵測到的 component 缺可見文字 prop（boundary I4 無法成立）：Phase 6 fail，dispatch `accessible-name-prop-missing`
- `mode == "create"` 但目標檔已存在：Phase 9 fail，dispatch `target-dir-conflict`
- 寫檔 IO 失敗（權限 / 磁碟）：Phase 9 fail，dispatch `write-io-failed`

完整 failure_kind 對照見 [`fail-codes.md`](fail-codes.md)。

## §4 上下游邊界

### 上游

Pencil GUI + MCP — 設計者在 Pencil 內 freeze 設計、`File → Save` 產出 `.pen`。
`/aibdd-uiux-design` + `/aibdd-uiux-draw` 為 `.pen` 的形成路徑。

### 直接 caller（DELEGATE 入口）

- **`/aibdd-plan` Phase 3 design pipeline** — frontend boundary 的 design-source path 直接 DELEGATE 本 skill。
  caller 提供 `pen_path` / `screen_id` / `target_dir` (= `${TRUTH_BOUNDARY_ROOT}/contracts/components/`) / `mode`。

### 直接下游（消費本 skill 產物）

- **`/aibdd-green-execute`**：從 `<target_dir>/<id>/<id>.tsx` 與 `.stories.tsx` 直接 import 使用。
  視覺修改應該回 `.pen` 後重跑本 skill（`mode: "overwrite"`），而不是在下游手改 component；
  green 推薦把行為透過 props callback 從 page-level / hooks / store 注入。
- **`/aibdd-red-execute`**：從 story export args 派生 `getByRole(role, { name })` locator，呼叫已落地的 component。

### Sibling skill（同 produced-files contract，不同設計來源）

未來 `aibdd-figma-to-storybook` / `aibdd-penpot-to-storybook` 等遵循同一 producer return shape：

```yaml
status: "completed"
mode: "producer"
schema_version: <string>          # 來源檔的 schema version
target_dir: <string>
write_mode: "create" | "overwrite"
token_count: <int>
tokens: [...]
component_count: <int>
component_table: {...}
files_written: [<string>, ...]    # 絕對路徑列表
```

下游 caller 不關心設計來源。

### 與 `/aibdd-form-story-spec` 的邊界

| 場景 | skill | 入口 |
|---|---|---|
| 已有 `.pen`（design-source pipeline）| **本 skill** | `pen_path` + `target_dir` |
| 無 `.pen`，純從 BDD reasoning 推 utility component | `/aibdd-form-story-spec` | caller-driven payload + `target_dir` |
| 後端 boundary widget / 設計不適用的元件 | `/aibdd-form-story-spec` | caller-driven payload |

**同一 component 不該兩條路徑同時寫**；caller 二選一。

### 不可接受的請求

- 「在轉換途中讓 caller 改 `.pen`」— 拒收。`.pen` 必須在進入本 skill 前已 freeze。
- 「請只寫 stories.tsx，不寫 .tsx」/「只寫 .tsx，不寫 stories.tsx」— 拒收。兩檔強制雙產出（boundary I4 binding anchor 要求 story 端存在）。
- 「請建立 Next.js 專案 scaffold」— 拒收，改呼 `/aibdd-auto-starter`。
- 「請補 hooks / fetch / page-level 組裝」— 拒收，改呼 `/aibdd-green-execute`。

## §5 路徑慣例（caller 應對齊）

```
target_dir 慣例 = ${TRUTH_BOUNDARY_ROOT}/contracts/components/
                  ↑ 對齊 arguments.yml 的 CONTRACTS_DIR + 慣例子目錄

實際寫出 = ${target_dir}/<ComponentId>/<ComponentId>.tsx
        + ${target_dir}/<ComponentId>/<ComponentId>.stories.tsx
```

`src/` 端透過 tsconfig path alias `@/components/* → specs/<TLB>/contracts/components/*` 引用：

```ts
// src/app/page.tsx
import { LobbyRoomEntry } from "@/components/LobbyRoomEntry/LobbyRoomEntry";
```

Storybook 端在 `.storybook/main.ts` 加 glob：

```ts
stories: [
  "../specs/<TLB>/contracts/components/**/*.stories.@(ts|tsx)",
  "../specs/<TLB>/contracts/components/**/*.mdx"
]
```

本 skill 不修改 tsconfig / Storybook config / vitest config —— 那是 `/aibdd-auto-starter` 的 template 職責。
