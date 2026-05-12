# 角色 + 入口契約

> 純 declarative reference。Phase 1 LOAD 取入口 schema 與角色定位。

## §1 角色定位

One-way pipeline skill。輸入 = Pencil `.pen` 設計檔。輸出 = Next.js 16 + React 19 + Tailwind 4 + Storybook 10
（`@storybook/nextjs-vite`）component library project tree。

**做**：

- 解析 `.pen` JSON、抽 design tokens、挑 single screen、做 component candidate detection、scaffold 專案、
  RENDER component + story 檔、跑 `tsc` / `build-storybook` 自檢。
- component / token / story 名稱以 `.pen` 觀察為 SSOT；不發明、不腦補。

**不做**：

- 不修改原 `.pen`（單向）
- 不挑 component 顆粒度規則 — heuristics 屬 [`patterns/component-detection.md`](patterns/component-detection.md)，
  本 skill 只執行
- 不換 framework target（Next.js 16 + React 19 + Storybook 10 nextjs-vite + Tailwind 4 鎖死）
- 不引入額外 deps（`clsx` / `cn` / framer-motion 等）除非 caller 顯式指定
- 不替 Pencil GUI 做視覺探索 — 探索期請走 Pencil + MCP

## §2 入口契約 — caller / user payload schema

```yaml
pen_path: <string, required>           # 絕對路徑，副檔名必為 .pen
target_dir: <string, required>         # 輸出根目錄；e.g. "pencil-ui"
mode: "create" | "overwrite"           # 預設 "create"；已存在目錄非 overwrite → 衝突回退

screen_id: <string?>                   # optional — 指定要轉換哪一個 top-level frame
                                       # 缺項 → Phase 4 回 caller 候選清單再確認

framework_target: "nextjs-storybook"   # 目前唯一支援值；保留欄位以利未來擴充
verify: true | false                   # 預設 true；false 跳過 Phase 8 (tsc + build-storybook)
```

### 不允許在 payload 出現的東西

- 多個 `screen_id`（每次只轉一個 screen — 避免 component detection 在跨 screen 混淆抽象）
- 自訂 `package.json` 內容 — scaffold 模板屬 [`patterns/project-scaffold.md`](patterns/project-scaffold.md) SSOT；
  改 deps 請改 reference，不要從 payload 傳
- `screen_id` 含 slash — `.pen` 規格禁止 id 含 `/`，本 skill 直接拒收

## §3 缺項處理

- `pen_path` 缺項 / 不存在 / 非 `.pen`：Phase 1 fail，dispatch `pen-path-invalid`
- `target_dir` 已存在且 `mode != "overwrite"`：Phase 1 fail，dispatch `target-dir-conflict`
- `screen_id` 缺項：Phase 4 列 top-level frame 候選清單回 caller，等 caller 補後重啟 Phase 4
- `.pen` 解析失敗（binary / 舊版）：Phase 2 fail，dispatch `pen-not-parseable`

完整 failure_kind 對照見 [`fail-codes.md`](fail-codes.md)。

## §4 上下游邊界

- **上游**：Pencil GUI + MCP — 設計者在 Pencil 內 freeze 設計、`File → Save` 產出 `.pen`。
- **下游**：產出的 component library 可選擇性被 `aibdd-form-story-spec` 重寫 story 檔以加入 BDD binding anchor。
  本 skill 產出的 story 為視覺骨架，**不**綁 BDD step pattern；BDD-aware story 由 `aibdd-form-story-spec` 接手。

任何「在轉換途中讓 caller 改 .pen」的請求 — 拒收。`.pen` 必須在進入本 skill 前已 freeze。
