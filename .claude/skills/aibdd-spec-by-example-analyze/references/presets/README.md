# BDD Analysis — Presets

本 skill 為所有 BDD step pattern preset 的 single source of truth。其他 skill（如 `aibdd-auto-red` / `aibdd-auto-green` / `aibdd-atdd-plan`）讀 preset 時一律由此路徑引入。

---

## §1 目錄

| Preset | 適用 Boundary | 檔案 | 狀態 |
|--------|-------------|------|---|
| `web-backend` | HTTP API + DB/Repository 的後端服務 | `web-backend.md` + `web-backend/` | full |
| `web-frontend` | UI + Client State 的前端應用 | `web-frontend.md` + `web-frontend/` | full |
| `native-ios` | UIKit / SwiftUI + XCUIApplication / XCTest | `native-ios.md` | seed (PF-14; §0 only, §1+ TODO) |
| `cli` | CLI subcommand harness (argv / stdin / stdout / exit-code) | `cli.md` | seed (PF-14; §0 only, §1+ TODO) |

---

## §2 檔案結構

每個 preset 由三部分組成：

```
presets/
├── <preset-name>.md              # 入口：適用條件 + 子活動入口 + handler/variant 清單
└── <preset-name>/
    ├── overview.md               # 後設決策樹：Gherkin 子句 → 抽象角色 → handler
    ├── handlers/
    │   └── <handler-type>.md     # 每個 handler 的 Trigger 辨識 / 任務 / BDD 模式 / 共用規則
    └── variants/
        └── <variant-name>.md     # 每個語言 / 框架 variant 的程式碼 pattern
```

---

## §3 新增 Preset

新增時必須：

1. 建立 `<preset-name>.md` 入口檔 + `<preset-name>/` 子目錄
2. 在 `<preset-name>.md` 宣告「適用條件」— 明確說明哪類 boundary 該用本 preset
3. 至少放一個 `handlers/<handler>.md`（否則 preset 無用）
4. 本 README §1 新增一行

---

## §4 與 boundary preset routing（`/aibdd-plan` DSL）的關係

**句型部位的機械對照表**已由 `aibdd-core/assets/boundaries/<preset>/handler-routing.yml`（以及各 preset 的 `handlers/` 敘事）取代；`/aibdd-plan` DSL 項目以 `dsl.yml` 的 `L4.preset.{name,sentence_part,handler,variant}` 記錄分類結果。本 Analyze skill 只做 Spec-by-Example 填值與一致性檢查，**不維護** routing SSOT。
