# BDD Analyze — Presets 索引

本 skill 為 BDD step pattern preset 的 single source of truth。下游 (`/aibdd-red-*` / `/aibdd-green-*` / `/aibdd-tasks`) 讀 preset 時一律由此路徑引入。

## §1 目錄

| Preset | 適用 Boundary | 入口檔 | 決策表 |
|--------|-------------|---|---|
| `web-backend`  | HTTP API + DB／Repository 後端 | `web-backend.md`  | `decision-trees/web-backend-handler.yml`  |
| `web-frontend` | Browser UI + Playwright E2E    | `web-frontend.md` | `decision-trees/web-frontend-handler.yml` |

## §2 入口檔內容

每個入口檔只放：
- **§0 Four-Layer Mapping Schema**（L1–L4 entry 必填欄位）
- **§1 適用條件**（哪類 boundary 該套）
- **§3 Handler 清單**（routing id 對照）
- **§5 與 `handler-routing.yml` 對齊**（machine SSOT 指向）

**不放**：handler-selection 之 narrative 決策 SOP——已抽到 `decision-trees/*.yml`，結構化查表使用。

## §3 與 boundary preset routing（`/aibdd-plan` DSL）的關係

句型部位之機械對照表由 `aibdd-core/assets/boundaries/<preset>/handler-routing.yml` 與其 `handlers/` 子樹擁有；`/aibdd-plan` 在 DSL `entries[].L4.preset.{name,part,handler,variant}` 寫入分類結果。

本 skill 只做 Spec-by-Example 填值與一致性檢查，**不**維護 routing SSOT；新增 handler／variant 走 `aibdd-core` 該 boundary 之 asset 樹。
