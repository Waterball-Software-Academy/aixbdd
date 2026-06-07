# SQL DDL 格式 — 三方言對照

dialect 由 `target_path` 副檔名 SSOT。本檔分三段：

1. 共通骨架（`CREATE TABLE` / column 定義 / `FOREIGN KEY`）
2. 三方言型別對照
3. 三方言自增 / 約束差異對照

---

## §1 共通骨架

```sql
CREATE TABLE <table_name> (
  <col_name> <type>[(<precision>)] [<col-level constraints>],
  ...
  CONSTRAINT <pk_name> PRIMARY KEY (<col>[, <col2>]),
  CONSTRAINT <fk_name> FOREIGN KEY (<col>) REFERENCES <other_table>(<other_col>)
);
```

- 表名與欄位名：`snake_case`（見 `patterns/naming-rules.md`）
- 一行一欄位定義；表級約束（PK / FK / UNIQUE）獨立成行
- 副檔名 = `.mysql.sql` / `.pg.sql` / `.mssql.sql` — **dialect SSOT**

---

## §2 三方言型別對照

| 邏輯型別 | 範例值 | MySQL | PG | MSSQL |
|----------|--------|-------|----|----|
| 整數 | `1`、`42` | `INT` / `BIGINT` | `INT` / `BIGINT` | `INT` / `BIGINT` |
| 自增主鍵 | — | `INT AUTO_INCREMENT` | `SERIAL` / `BIGSERIAL` | `INT IDENTITY(1,1)` |
| 短字串 | `"Alice"` | `VARCHAR(N)` | `VARCHAR(N)` | `NVARCHAR(N)` |
| 長文字 | 描述、內容 | `TEXT` | `TEXT` | `NVARCHAR(MAX)` |
| 布林 | `true`/`false` | `TINYINT(1)` 或 `BOOLEAN` | `BOOLEAN` | `BIT` |
| 小數 | `45000.5`、`0.8` | `DECIMAL(P,S)` | `DECIMAL(P,S)` / `NUMERIC(P,S)` | `DECIMAL(P,S)` |
| 日期 | `2026-01-01` | `DATE` | `DATE` | `DATE` |
| 時間戳 | `2026-01-01T00:00:00Z` | `DATETIME` / `TIMESTAMP` | `TIMESTAMP` / `TIMESTAMPTZ` | `DATETIME2` |
| UUID | — | `CHAR(36)` | `UUID` | `UNIQUEIDENTIFIER` |
| Enum / 有限值域 | `待付款`、`已付款` | `ENUM(...)` 或外部表 + FK | 外部表 + FK（或 PG `CREATE TYPE ... AS ENUM`）| 外部表 + FK |

> 列舉值優先用「外部 lookup table + FK」表達；只在推理包明示「值域固定且穩定」時才用方言原生 enum。

---

## §3 自增 / 約束差異對照

### 自增主鍵慣用寫法

```sql
-- MySQL (.mysql.sql)
CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id)
);

-- PostgreSQL (.pg.sql) — 兩種寫法擇一
CREATE TABLE users (
  id SERIAL PRIMARY KEY
);
CREATE TABLE users (
  id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
);

-- MSSQL (.mssql.sql)
CREATE TABLE users (
  id INT IDENTITY(1,1) NOT NULL,
  CONSTRAINT PK_users PRIMARY KEY (id)
);
```

### NOT NULL / DEFAULT / PK

| 場景 | MySQL | PG | MSSQL |
|------|-------|----|----|
| NOT NULL | `col TYPE NOT NULL` | `col TYPE NOT NULL` | `col TYPE NOT NULL` |
| DEFAULT 字面值 | `DEFAULT 'pending'` | `DEFAULT 'pending'` | `DEFAULT 'pending'` |
| DEFAULT 當前時間 | `DEFAULT NOW()` 或 `CURRENT_TIMESTAMP` | `DEFAULT NOW()` 或 `CURRENT_TIMESTAMP` | `DEFAULT GETDATE()` |
| 表級 PK | `PRIMARY KEY (col)` 或 `CONSTRAINT PK_t PRIMARY KEY (col)` | 同 MySQL | **慣用具名**：`CONSTRAINT PK_t PRIMARY KEY (col)` |
| Inline PK | `col INT PRIMARY KEY`（少用）| `col SERIAL PRIMARY KEY`（常用）| — |

### FOREIGN KEY 寫法

```sql
-- 表級（三方言皆支援；MSSQL 偏好具名）
CONSTRAINT FK_orders_user FOREIGN KEY (user_id) REFERENCES users(id)

-- 匿名（MySQL / PG / MSSQL 皆支援）
FOREIGN KEY (user_id) REFERENCES users(id)

-- Inline（PG 獨有）
user_id INT NOT NULL REFERENCES users(id)
```

> 下游 `dsl_cli` 的 spec parser 三種寫法皆可解析為同一 `RefPart`（`target_part_path = <spec>#ref:<from_table>.<from_col>><to_table>.<to_col>`）。

### Identifier quoting（一般略過）

| 方言 | 引號 |
|------|------|
| MySQL | 反引號 `` `col` ``（含保留字時才需要）|
| PG    | 雙引號 `"col"`（含保留字時才需要）|
| MSSQL | 中括號 `[col]`（含保留字時才需要）|

> **本 skill 預設不加引號**；命名遵循 `naming-rules.md`，避開保留字即可。

---

## §4 註解語法

```sql
-- 行尾註解（三方言通用）
col INT NOT NULL,  -- CiC(GAP): unit unclear from feature

-- 區塊註解（三方言通用）
/*
  表級註解：說明該表 aggregate boundary
*/
```

### 便條紙格式

行尾 comment：`-- CiC(<CATEGORY>): ...`

完整格式定義見 `aibdd-form-activity::references/cic-format.md`。

| 代碼 | 何時標記 |
|------|---------|
| `GAP` | 無法從 .feature 確定欄位型別或長度 |
| `ASM` | 推斷了 Enum 值域但不確定是否完整 |
| `AMB` | 關聯方向不確定 |
| `CON` | 同欄位跨 Feature 型別不一致 |

### Aggregate root 標記

```sql
CREATE TABLE orders (  -- aggregate_root
  ...
);
```

---

## §5 範例（完整三方言對照）

### 推理包（同一邏輯模型）

- `users`：`id`（自增 PK）、`email`（VARCHAR(255), NOT NULL, UNIQUE）
- `orders`：`id`（自增 PK）、`user_id`（FK → users.id, NOT NULL）、`status`（enum: pending/paid）

### MySQL（`domain.mysql.sql`）

```sql
CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT UQ_users_email UNIQUE (email)
);

CREATE TABLE orders (  -- aggregate_root
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  status VARCHAR(20) NOT NULL,  -- CiC(ASM): values pending|paid
  PRIMARY KEY (id),
  CONSTRAINT FK_orders_user FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### PostgreSQL（`domain.pg.sql`）

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  CONSTRAINT UQ_users_email UNIQUE (email)
);

CREATE TABLE orders (  -- aggregate_root
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  status VARCHAR(20) NOT NULL  -- CiC(ASM): values pending|paid
);
```

### MSSQL（`domain.mssql.sql`）

```sql
CREATE TABLE users (
  id INT IDENTITY(1,1) NOT NULL,
  email NVARCHAR(255) NOT NULL,
  CONSTRAINT PK_users PRIMARY KEY (id),
  CONSTRAINT UQ_users_email UNIQUE (email)
);

CREATE TABLE orders (  -- aggregate_root
  id INT IDENTITY(1,1) NOT NULL,
  user_id INT NOT NULL,
  status NVARCHAR(20) NOT NULL,  -- CiC(ASM): values pending|paid
  CONSTRAINT PK_orders PRIMARY KEY (id),
  CONSTRAINT FK_orders_user FOREIGN KEY (user_id) REFERENCES users(id)
);
```
