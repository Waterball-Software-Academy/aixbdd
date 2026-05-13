# 角色 + 入口契約

> 純 declarative reference。Phase 1 LOAD 取入口 schema 與角色定位。

## §1 角色定位

Adapter skill。輸入 = Pencil `.pen` 設計檔。輸出 = `component_table` + Tailwind 4 `tokens`（in-memory；
**不寫任何檔**）。

**做**：

- 解析 `.pen` JSON
- 抽 design tokens（Tailwind 4 namespace 對照）
- 挑 single screen
- 跑 component candidate detection（heuristics）
- 回 `component_table` + `tokens` 推理包給 caller

**不做**：

- 不寫任何檔案（component / story / package.json / tsconfig / globals.css 全不寫）
- 不建專案、不跑 `npm install`、不跑 `tsc`、不跑 `build-storybook`
- 不修改原 `.pen`（單向 read-only）
- 不挑 component 顆粒度規則 — heuristics 屬 [`patterns/component-detection.md`](patterns/component-detection.md)，本 skill 只執行
- 不換 framework target — `component_table` 本身與 framework 無關，下游自己決定怎麼渲染
- 不引入額外 deps
- 不替 Pencil GUI 做視覺探索 — 探索期請走 Pencil + MCP

## §2 入口契約 — caller payload schema

```yaml
pen_path: <string, required>           # 絕對路徑，副檔名必為 .pen

screen_id: <string?>                   # optional — 指定要轉換哪一個 top-level frame
                                       # 缺項 → Phase 4 回 caller 候選清單再確認
```

### 不允許在 payload 出現的東西

- `target_dir` / `mode` / `framework_target` / `verify` / `output_mode` — 舊 scaffold 模式參數已**全部砍除**；
  本 skill 為 read-only adapter，不接受寫檔指示
- 多個 `screen_id`（每次只轉一個 screen — 避免 component detection 在跨 screen 混淆抽象）
- `screen_id` 含 slash — `.pen` 規格禁止 id 含 `/`，本 skill 直接拒收

## §3 缺項處理

- `pen_path` 缺項 / 不存在 / 非 `.pen`：Phase 1 fail，dispatch `pen-path-invalid`
- `screen_id` 缺項：Phase 4 列 top-level frame 候選清單回 caller，等 caller 補後重啟 Phase 4
- `.pen` 解析失敗（binary / 舊版）：Phase 2 fail，dispatch `pen-not-parseable`

完整 failure_kind 對照見 [`fail-codes.md`](fail-codes.md)。

## §4 上下游邊界

### 上游
Pencil GUI + MCP — 設計者在 Pencil 內 freeze 設計、`File → Save` 產出 `.pen`。

### 下游（DELEGATE caller）
- **`/aibdd-form-story-spec`** Phase 1 design-source cross-check — 比對 caller reasoning 之
  `component.identifier` / `stories[].export_name` 是否在 `component_table` 內，不一致時 warn（不 override
  caller reasoning）。
- **`/aibdd-plan`** Phase 3（未來 component-design merge sub-phase）— 把 `component_table + tokens` 與
  features × activities 合成 enriched `boundary_delta.components`，下游分流：
  - `/aibdd-form-story-spec` 寫 component + story 到 `${TRUTH_BOUNDARY_ROOT}/contracts/components/<C>/`
  - `/aibdd-green-execute` 在這些 component 上補業務邏輯（hooks / API / state）

### Sibling adapters（同 return contract，不同設計來源）
未來 `aibdd-figma-to-storybook` / `aibdd-penpot-to-storybook` 等遵循同一 return shape：

```yaml
status: "completed"
mode: "adapter"
schema_version: <string>          # 來源檔的 schema version
token_count: <int>
tokens: [...]                     # design tokens 標準化
component_count: <int>
component_table: {...}            # Component | Source nodes | Detected props | Stories
```

下游 caller 不關心設計來源。

任何「在轉換途中讓 caller 改 .pen」的請求 — 拒收。`.pen` 必須在進入本 skill 前已 freeze。
任何「請寫出 component / story / project files」的請求 — 拒收，請改呼叫 `/aibdd-form-story-spec`（component + story）
或 `/aibdd-auto-starter`（project scaffold）。
