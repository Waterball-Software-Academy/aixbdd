# 命名規則 + Strategy Guard

## §1 命名規則

### Table

- `snake_case` 複數：`users` / `lesson_progresses` / `order_items`
- 避開保留字（`order` → 用 `orders`；`user` → 用 `users`）
- Planner 傳入 prefix 時套用在 Table 名前

### Column

- `snake_case`：`user_id` / `created_at` / `lesson_progress_id`
- 外鍵欄位 = `<referenced_table_singular>_<referenced_pk>`：`user_id` 指向 `users.id`
- 時間欄位：`created_at` / `updated_at` / `deleted_at`（軟刪）
- 布林欄位：`is_<state>` / `has_<thing>`：`is_active`、`has_premium`

### 約束（Constraint）

| 種類 | 命名 | 範例 |
|------|------|------|
| Primary Key | `PK_<table>` | `PK_orders` |
| Foreign Key | `FK_<from>_<to>` | `FK_orders_user` |
| Unique | `UQ_<table>_<col>` | `UQ_users_email` |
| Check | `CK_<table>_<col>` | `CK_orders_status` |

> MySQL 允許匿名約束、MSSQL/PG 偏好具名；皆遵循上表，方便跨檔搜尋。

### 反例

| 反例 | 修法 |
|------|------|
| `User`、`UserOrder`（PascalCase）| `users`、`user_orders` |
| `userId`（camelCase）| `user_id` |
| `order_table`（含「table」字樣）| `orders` |
| `tbl_users`（含「tbl」前綴）| `users` |
| `fk1`、`fk2`（無語意約束名）| `FK_orders_user` |

---

## §2 Strategy Guard（逆向回饋）

生成/更新 DDL 時，若發現以下情況，**REPORT** 給協調器並觸發 Strategy Guard：

1. **Aggregate 結構衝突**：正規化發現某 Aggregate 應拆分，而現有 `.feature` 的 Background datatable 違反設計 → 回到 Feature 層修正。
2. **缺少必要 Aggregate**：關聯需要 Aggregate B 存在，但無 `.feature` 定義了它 → 回到 Strategic 補充。
3. **跨檔 FK**：Planner 切檔策略導致 FK 雙端不在同一檔（SQL DDL 無跨檔 `REFERENCES` 語法）→ 回到 Planner 重切。
4. **Dialect 不一致**：推理包暗示某 Aggregate 需要 MSSQL 獨有的 `ROWVERSION` / PG 獨有的 `JSONB` 等型別，但 Planner 指定的 dialect 不支援 → 回到 Planner 重選 dialect 或調整推理包。
