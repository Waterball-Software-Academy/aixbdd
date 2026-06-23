### q5-data-schema-format
- prompt: 後端持久狀態的 data schema 要用哪種格式落地？
- kind: CON
- options: dbml | ddl:postgresql | ddl:mysql | ddl:mssql
- recommendation: dbml
- answer.raw: {{Q5_ANSWER}}
- resolved_decision: { key: data_schema_format, value: {{DATA_SCHEMA_FORMAT}} }
- resolved_decision: { key: db_dialect, value: {{DB_DIALECT}} }
- status: {{Q5_STATUS}}

<!-- @guideline -->
**僅 `type: web-service` 的 boundary 詢問**（stack = `python_e2e` / `java_e2e`）。其他 type（如 `nextjs_playwright` 的 `web-app`）的 state_specifier 非 persistent，**不問本題**，`data_schema_format = n/a`、`db_dialect = none`。

決定 `state_specifier` 怎麼落 `${DATA_DIR}`：
- `dbml` — 採 web-service base preset 的 `state_specifier`（`/aibdd-form-entity-spec`，format `dbml`，`domain.dbml`）。**不寫** `boundary.yml` 的 `profile_overrides`，沿用 base。`db_dialect = none`。
- `ddl:<dialect>` — 改用 `/aibdd-form-ddl-spec`（format `ddl`）；dialect 由 default_filename 副檔名 SSOT（見 `aibdd-form-ddl-spec`）。Phase 4 把整塊 `profile_overrides.state_specifier` 寫進 `boundary.yml`。dialect↔副檔名：

| db_dialect | default_filename |
|---|---|
| `postgresql` | `domain.pg.sql` |
| `mysql` | `domain.mysql.sql` |
| `mssql` | `domain.mssql.sql` |

resolved 後 `data_schema_format` ∈ `dbml` / `ddl`，`db_dialect` ∈ `none` / `postgresql` / `mysql` / `mssql`（`dbml` 時恆為 `none`）。

答非四個 option 之一、或 web-service 卻未答 → 標 unresolved 重問，不要自行猜值。
reply token：`Q5: dbml | ddl:postgresql | ddl:mysql | ddl:mssql`
