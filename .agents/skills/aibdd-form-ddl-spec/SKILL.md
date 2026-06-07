---
name: aibdd-form-ddl-spec
description: >
  從推理包翻譯為 SQL DDL（MySQL `.mysql.sql` / PostgreSQL `.pg.sql` / MSSQL `.mssql.sql`）。
  負責各方言 DDL 語法規章 + 歸檔。dialect 由 `target_path` 副檔名 SSOT，
  不做跨 boundary 決策；路徑 / 切檔策略 / dialect 選擇由 Planner 透過 DELEGATE 參數指定。
user-invocable: false
---

## §1 角色

Formulation skill。綁定 DSL = SQL DDL，支援三種方言：

| 副檔名 | Dialect | 對應 parser |
|--------|---------|-------------|
| `*.mysql.sql` | MySQL | `MySQLSpecParser` |
| `*.pg.sql`    | PostgreSQL | `PostgresSpecParser` |
| `*.mssql.sql` | Microsoft SQL Server | `MSSQLSpecParser` |

被多個 Planner DELEGATE（如 `aibdd-system-analysis` 之 sub-boundary state schema）。Planner 在 DELEGATE payload 內提供具體 `target_path`（含副檔名），本 skill 由副檔名 SSOT dialect、**不自決**。

下游 `dsl_cli` 的 spec parser 會把 DDL 解析為 `TablePart` / `RefPart`，與 DBML 共用同一份 Part 形狀 — 因此 boundary 的 `part_to_dsl.py` plugin 不需要因 dialect 而調整。

---

## §2 入口契約

接收推理包：

| 項目 | 內容 |
|------|------|
| M/D/C 變更集 | Entity / Attribute / Relationship / AggregateHint 的增刪改 |
| Axis 單位對應 | 推理包中每個單位的具體對應 |
| CiC 記號清單 | 便條紙（GAP / ASM / BDY / CON）+ 錨點 |
| 退出狀態 | Reason 步是否完整通過 |
| `target_path` | Planner 指定之**相對於 `${DATA_DIR}` 的檔案路徑**，**必須**以 `.mysql.sql` / `.pg.sql` / `.mssql.sql` 結尾（例：`domain.mysql.sql`、`<boundary-id>/states/<state>.pg.sql`；切檔策略由 Planner 決定）。**不得**含 `<<NN-functional-module>>` 借位子層 — `${DATA_DIR}` 在 SSOT 已是 flat directory（見 `aibdd-core::spec-package-paths.md`），functional module 借位只允許出現在 `${TRUTH_BOUNDARY_PACKAGES_DIR}` 子樹。 |

**Dialect SSOT**：dialect 完全由 `target_path` 副檔名決定；Planner **不另傳** `dialect` 欄位，本 skill 也**不另寫入** dialect 識別字到檔案中。

**缺項**：推理包不完整、`target_path` 未指定、或副檔名非三者之一 → 回退呼叫 Planner 補齊。

---

## §3 Formulate SOP

1. **判定 dialect**：讀 `target_path` 副檔名 → `mysql` / `pg` / `mssql`。
2. **讀取 format reference**：`references/format-reference.md`（共通 SQL DDL 語法 + 三方言型別 / 自增 / 約束對照）
3. **展開 DDL 結構**：從推理包的 Entity / Relationship 展開為 `CREATE TABLE` / 表級 `FOREIGN KEY` / inline `REFERENCES`（僅 PG）
4. **套用 patterns**：讀 `references/patterns/naming-rules.md`
5. **保留 CiC**：推理包中的便條紙 inline 到 DDL 註解（`-- CiC(<KIND>): ...` 或行尾 `-- ...`）
6. **寫檔前 ASSERT**：
   - `target_path` 不得含 `<<NN-functional-module>>` 借位子層；
   - `target_path` 副檔名必為 `.mysql.sql` / `.pg.sql` / `.mssql.sql`；
   - 任一違反 → STOP 並回退 Planner 補正（白話文回報具體違反項）。
7. **寫檔前 dialect 自查**：以 §3 判定的 dialect 對照 §4 表，確認**未使用其他方言獨有語法**（如 PG 檔不應出現 `AUTO_INCREMENT`、MSSQL 檔不應出現 `SERIAL`）。違反 → 改寫為當前 dialect 的對等語法。
8. **寫檔**：依 `target_path` 寫出（落點＝`${DATA_DIR}` ⊕ `target_path`）。
9. **機械驗證**：呼叫 `scripts/check_sql_syntax.py <寫出檔>` 確認語法合法 + dialect 自洽。

---

## §4 DSL 最佳實踐

### 命名規則
- Table：`snake_case` 複數（`lesson_progresses`）
- Column：`snake_case`（`user_id`）
- FK constraint：`FK_<from_table>_<to_table>`（具名）或匿名（MySQL/MSSQL 允許）
- PK constraint：`PK_<table>`（MSSQL/PG 偏好具名）；MySQL 可用 inline `PRIMARY KEY`
- Planner 傳入 prefix 時套用在 Table 名前

### Dialect 自增主鍵（最常見差異）

| 方言 | 慣用寫法 |
|------|----------|
| MySQL | `id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id)` |
| PG    | `id SERIAL PRIMARY KEY` 或 `id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY` |
| MSSQL | `id INT IDENTITY(1,1) NOT NULL, CONSTRAINT PK_<table> PRIMARY KEY (id)` |

### Schema modularization
- 切檔策略由 Planner 決定（domain = 單檔；state = per-boundary / per-sub-boundary）
- 跨檔 FK 在 SQL DDL 中無語法支援；若 Planner 指定多檔，**同一 referential 路徑下的 FK 雙端必須在同一檔**，否則 STOP 並回退 Planner 補正
- 本 skill 只負責在指定 path 寫出合格 DDL

### Aggregate Hint
- 用 SQL 行尾註解 `-- aggregate_root` 標記 aggregate root table
- AggregateHint 不改 Table 結構，只加註解

### CiC 註解
- 行尾：`-- CiC(<CATEGORY>): ...`（CATEGORY ∈ GAP / ASM / AMB / CON）
- 完整格式定義見 `aibdd-form-activity::references/cic-format.md`

---

## §5 匯報

以白話文 1–3 句匯報（依 `aibdd-core::planner-contract.md` §REPORT 匯報；不輸出 JSON / YAML）：

> Form DDL Spec 完成。產出 N 個 `<dialect>` DDL 檔案。{若有便條紙則加「尚有 N 張便條紙待釐清」；無則省略}

---

## §6 參考

- **references/format-reference.md**：共通 SQL DDL 語法 + 三方言型別 / 自增 / 約束對照
- **references/patterns/naming-rules.md**：Table / Column / Constraint 命名 + Strategy Guard
- **scripts/check_sql_syntax.py**：語法 / FK / dialect 一致性機械驗證
