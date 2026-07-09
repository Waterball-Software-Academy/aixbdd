# DDL state_specifier override

## Rule 1 — `data_schema_format ∈ { postgresql, mysql, mssql }` 時才寫整塊 `profile_overrides.state_specifier`；`dbml` 不寫，dialect 由 `format` SSOT

- web-service base preset 的 `state_specifier` 預設是 DBML（`/aibdd-form-entity-spec`、`format: dbml`、`domain.dbml`）。Q4 選 `dbml` 就**不動** `boundary.yml`，沿用 base；只有選 `ddl:<dialect>` 才把下面整塊寫進 `boundary.yml`。override 是**整塊替換、絕不 deep merge**，`output_dir_key` 沿用 base 的 `DATA_DIR`、不可改（output 目錄是結構契約）。dialect 的 origin **是 `format`**（`postgresql` / `mysql` / `mssql`）——Planner／`/aibdd-data-plan` 讀 `state_specifier.format`，據以把對應副檔名接到 `target_path`（下表）。`/aibdd-form-ddl-spec` 收到的 payload 只有 `target_path`（與 `/aibdd-form-entity-spec` 對稱），由副檔名判 dialect；`default_filename` 的副檔名即此慣例值，須與 `format` 對齊。

  ```yaml
  profile_overrides:
    state_specifier:
      skill: /aibdd-form-ddl-spec
      format: <postgresql|mysql|mssql>
      semantics: persistent
      output_dir_key: DATA_DIR
      default_filename: domain.<ext>
  ```

  `format` → `default_filename` 對照：

  | format | default_filename |
  |---|---|
  | `postgresql` | `domain.pg.sql` |
  | `mysql` | `domain.mysql.sql` |
  | `mssql` | `domain.mssql.sql` |

### ✅ Good

情境：Q4 = `ddl:postgresql`

```
boundary.yml 追加：
profile_overrides:
  state_specifier:
    skill: /aibdd-form-ddl-spec
    format: postgresql
    semantics: persistent
    output_dir_key: DATA_DIR
    default_filename: domain.pg.sql
```

情境：Q4 = `dbml`

```
boundary.yml 不動（沿用 web-service base preset 的 DBML state_specifier）
```

### ❌ Bad

```
Q4 = ddl:mysql，但只寫半塊（漏 output_dir_key / default_filename / semantics）
→ 解析時 deep-merge 預期落空、specifier 不完整
```

```
Q4 = ddl:postgresql，format 寫成 ddl 或 pg（非 postgresql / mysql / mssql 三者之一）
→ /aibdd-data-plan 無法由 format 判定 dialect
```

```
format: postgresql，default_filename 寫成 domain.mysql.sql
→ format 與 default_filename 不一致
```

**預期改法**
- 選 `ddl:<dialect>` 才寫，且寫**完整 block**；`output_dir_key` 固定 `DATA_DIR`；`format` 取 `postgresql` / `mysql` / `mssql`；`default_filename` 依上表對齊。選 `dbml` 一律不寫。
