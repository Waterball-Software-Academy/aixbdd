---
name: aibdd-form-entity-spec
description: >
  從推理包翻譯為 DBML (.dbml)。負責 DBML 語法規章 + 歸檔。
  不做跨 boundary 決策；路徑 / 切檔策略由 Planner 透過 DELEGATE 參數指定。
user-invocable: false
---

## §1 角色

Formulation skill。綁定 DSL = DBML (.dbml)。被多個 Planner DELEGATE：
- `aibdd-entity-analysis`：L1 web-service logical ER 落地（`<function_module>/<boundary-id>/entities/logical.dbml`）
- `aibdd-system-analysis`：sub-boundary state schema 落地（`<function_module>/<boundary-id>/sub-boundaries/<sub-id>/states/*.dbml`，限 persistence=dbml 的 backend sub-boundary；`type` 不出現於 path — 由 boundary.yml `type` 欄位 SSOT）

---

## §2 入口契約

接收推理包：

| 項目 | 內容 |
|------|------|
| M/D/C 變更集 | Entity / Attribute / Relationship / AggregateHint 的增刪改 |
| Axis 單位對應 | 推理包中每個單位的具體對應 |
| CiC 記號清單 | 便條紙（GAP / ASM / BDY / CON）+ 錨點 |
| 退出狀態 | Reason 步是否完整通過 |
| `target_path` | Planner 指定的輸出路徑 |

**缺項**：推理包不完整或 `target_path` 未指定 → 回退呼叫 Planner 補齊。

---

## §3 Formulate SOP

1. **讀取 format reference**：`references/format-reference.md`（DBML 語法）
2. **展開 DBML 結構**：從推理包的 Entity / Relationship 展開為 Table / Ref 宣告
3. **套用 patterns**：讀 `references/patterns/naming-rules.md` + `schema-modularization.md`
4. **保留 CiC**：推理包中的便條紙 inline 到 DBML 註解（`// CiC(<KIND>): ...`）
5. **寫檔**：依 `target_path` 寫出

---

## §4 DSL 最佳實踐

### 命名規則
- Table: `snake_case` 複數（`lesson_progresses`）
- Column: `snake_case`（`user_id`）
- Ref: `<table1>.<column> - <table2>.<column>`
- Planner 傳入 prefix 時套用在 Table 名前

### Schema modularization
- 切檔策略由 Planner 決定（logical = 單檔；state = per-boundary）
- Ref 跨檔引用語法：`Ref: table_a.col > other_file.table_b.col`
- 本 skill 只負責在指定 path 寫出合格 DBML

### Aggregate Hint
- 用 DBML `Note` 標記 aggregate root：`Note: 'aggregate_root'`
- AggregateHint 不改 Table 結構，只加 Note

---

## §5 匯報

以白話文 1–3 句匯報（依 `aibdd-core::planner-contract.md` §REPORT 匯報；不輸出 JSON / YAML）：

> Form Entity Spec 完成。產出 N 個 .dbml 檔案。{若有便條紙則加「尚有 N 張便條紙待釐清」；無則省略}

---

## §6 參考

- **format-reference.md**：DBML 語法 / Table / Ref / index / enum
- **patterns/naming-rules.md**：Table / Column / Ref 命名
- **patterns/schema-modularization.md**：單檔 vs 多檔 + Ref 跨檔引用
- **anti-patterns.md**：過度正規化 / 重複定義 / 不一致命名
