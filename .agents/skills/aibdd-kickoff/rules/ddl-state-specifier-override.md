# DDL state_specifier override

## Rule 1 — `data_schema_format = ddl` 時才寫整塊 `profile_overrides.state_specifier`；`dbml` 不寫，dialect 由 default_filename 副檔名 SSOT

- web-service base preset 的 `state_specifier` 預設是 DBML（`/aibdd-form-entity-spec`、`domain.dbml`）。Q5 選 `dbml` 就**不動** `boundary.yml`，沿用 base；只有選 `ddl` 才把下面整塊寫進 `boundary.yml`。override 是**整塊替換、絕不 deep merge**（見 `aibdd-core::references/ssot/boundary-profile-resolution.md`），所以 block 必須完整，`output_dir_key` 沿用 base 的 `DATA_DIR`、不可改（output 目錄是結構契約）。dialect 不另寫識別欄位，完全由 `default_filename` 副檔名表達——這是 `/aibdd-form-ddl-spec` 認定 dialect 的唯一來源。

  ```yaml
  profile_overrides:
    state_specifier:
      skill: /aibdd-form-ddl-spec
      format: ddl
      semantics: persistent
      output_dir_key: DATA_DIR
      default_filename: domain.<ext>
  ```

  `db_dialect` → `default_filename` 副檔名：

  | db_dialect | default_filename |
  |---|---|
  | `postgresql` | `domain.pg.sql` |
  | `mysql` | `domain.mysql.sql` |
  | `mssql` | `domain.mssql.sql` |

### ✅ Good

情境：Q5 = `ddl:postgresql`

```
boundary.yml 追加：
profile_overrides:
  state_specifier:
    skill: /aibdd-form-ddl-spec
    format: ddl
    semantics: persistent
    output_dir_key: DATA_DIR
    default_filename: domain.pg.sql
```

情境：Q5 = `dbml`

```
boundary.yml 不動（沿用 web-service base preset 的 DBML state_specifier）
```

### ❌ Bad

```
Q5 = ddl:mysql，但只寫半塊（漏 output_dir_key / default_filename）
→ 解析時 deep-merge 預期落空、specifier 抓不到 dialect
```

```
Q5 = ddl:mssql，default_filename 寫成 domain.sql（無 dialect 副檔名）
→ /aibdd-form-ddl-spec 無法由副檔名判定 dialect
```

**預期改法**
- 選 `ddl` 才寫，且寫**完整 block**；`output_dir_key` 固定 `DATA_DIR`；`default_filename` 依 `db_dialect` 取對應 `.pg.sql` / `.mysql.sql` / `.mssql.sql`。選 `dbml` 一律不寫。
